#!/usr/bin/env python3
"""KOSIF Audio — measured audio analysis (numpy; WAV natively, other formats via
soundfile or ffmpeg when installed).

usage:
  audio_analyze.py FILE [--target streaming|podcast|broadcast|club] [--summary] [--plot out.png]

Measures: duration, sample rate, channels, peak & approx. true-peak dBFS, RMS,
crest factor, integrated loudness (ITU-R BS.1770-4 K-weighting + gating, zero-phase
frequency-domain filter), DC offset, clipped samples, silence segments, stereo
correlation/balance, spectral centroid, band energy, tempo (BPM) estimate.
Tempo and key-free musical labels are estimates; loudness follows BS.1770 closely
but is not a certified meter.
"""
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import wave

try:
    import numpy as np
except ImportError:  # pragma: no cover
    print(json.dumps({"ok": False, "error": "numpy is required"}))
    raise SystemExit(2)

TARGETS = {"streaming": (-14.0, -1.0), "podcast": (-16.0, -1.0), "broadcast": (-23.0, -1.0), "club": (-8.0, -0.3)}
BANDS = [("sub", 20, 60), ("bass", 60, 250), ("low_mid", 250, 500), ("mid", 500, 2000),
         ("presence", 2000, 6000), ("air", 6000, 20000)]


def read_wav(path):
    with wave.open(path, "rb") as w:
        sr, ch, sw, n = w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()
        raw = w.readframes(n)
    if sw == 1:
        x = (np.frombuffer(raw, np.uint8).astype(np.float64) - 128) / 128
    elif sw == 2:
        x = np.frombuffer(raw, "<i2").astype(np.float64) / 32768
    elif sw == 3:
        b = np.frombuffer(raw, np.uint8).reshape(-1, 3)
        v = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8) | (b[:, 2].astype(np.int32) << 16))
        v = np.where(v >= 1 << 23, v - (1 << 24), v)
        x = v.astype(np.float64) / (1 << 23)
    elif sw == 4:
        x = np.frombuffer(raw, "<i4").astype(np.float64) / 2 ** 31
    else:
        raise ValueError(f"unsupported sample width {sw}")
    return x.reshape(-1, ch), sr, sw * 8


def load(path):
    if path.lower().endswith((".wav", ".wave")):
        try:
            return read_wav(path)
        except (wave.Error, ValueError):
            pass  # e.g. float WAV: fall through
    try:
        import soundfile as sf  # type: ignore
        x, sr = sf.read(path, always_2d=True, dtype="float64")
        return x, sr, None
    except Exception:  # noqa: BLE001
        pass
    ff = shutil.which("ffmpeg")
    if not ff:
        raise ValueError("cannot decode this format: install soundfile or ffmpeg, or convert to WAV")
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    try:
        subprocess.run([ff, "-v", "error", "-y", "-i", path, "-c:a", "pcm_s24le", tmp], check=True)
        return read_wav(tmp)
    finally:
        os.unlink(tmp)


def db(v):
    return round(20 * math.log10(v), 2) if v > 0 else None


def biquad_mag(f, sr, b, a):
    z = np.exp(-2j * np.pi * f / sr)
    return np.abs((b[0] + b[1] * z + b[2] * z * z) / (a[0] + a[1] * z + a[2] * z * z))


def k_weight_coeffs(sr):
    """BS.1770 K-weighting for any sample rate (bilinear design as used by libebur128)."""
    f0, G, Q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    K = math.tan(math.pi * f0 / sr)
    Vh = 10 ** (G / 20)
    Vb = Vh ** 0.4996667741545416
    a0 = 1 + K / Q + K * K
    shelf = ([(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0, (Vh - Vb * K / Q + K * K) / a0],
             [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0])
    f0, Q = 38.13547087602444, 0.5003270373238773
    K = math.tan(math.pi * f0 / sr)
    hp = ([1, -2, 1], [1, 2 * (K * K - 1) / (1 + K / Q + K * K), (1 - K / Q + K * K) / (1 + K / Q + K * K)])
    return shelf, hp


def k_filter(x, sr):
    n = x.shape[0]
    nfft = 1 << (n - 1).bit_length()
    f = np.fft.rfftfreq(nfft, 1 / sr)
    (b1, a1), (b2, a2) = k_weight_coeffs(sr)
    H = biquad_mag(f, sr, b1, a1) * biquad_mag(f, sr, b2, a2)
    X = np.fft.rfft(x, nfft, axis=0)
    return np.fft.irfft(X * H[:, None], nfft, axis=0)[:n]


def integrated_lufs(x, sr):
    y = k_filter(x, sr)
    blk, hop = int(0.4 * sr), int(0.1 * sr)
    if y.shape[0] < blk:
        return None, []
    idx = range(0, y.shape[0] - blk + 1, hop)
    weights = np.ones(y.shape[1])
    if y.shape[1] == 5:
        weights[3:] = 1.41
    z = np.array([(np.mean(y[i:i + blk] ** 2, axis=0) * weights).sum() for i in idx])
    L = np.where(z > 0, -0.691 + 10 * np.log10(np.maximum(z, 1e-20)), -200)
    g = z[L > -70]
    if g.size == 0:
        return None, L
    rel = -0.691 + 10 * math.log10(g.mean()) - 10
    g2 = z[(L > -70) & (L > rel)]
    return (round(-0.691 + 10 * math.log10(g2.mean()), 2) if g2.size else None), L


def true_peak(x, factor=4, taps_per_phase=12):
    """4x oversampling with a Kaiser-windowed-sinc polyphase interpolator (BS.1770 Annex 2 style)."""
    n = taps_per_phase * factor
    k = np.arange(n) - (n - 1) / 2
    h = np.sinc(k / factor) * np.kaiser(n, 8.0)
    phases = [h[p::factor] for p in range(factor)]
    phases = [ph / ph.sum() for ph in phases]  # unity DC gain per phase
    peak = 0.0
    for c in range(x.shape[1]):
        col = x[:, c]
        for ph in phases:
            if col.size:
                peak = max(peak, float(np.abs(np.convolve(col, ph, mode="same")).max()))
    return peak


def silence(mono, sr, thr_db=-50, min_len=0.5):
    win = max(1, int(0.05 * sr))
    n = mono.size // win
    if n == 0:
        return []
    rms = np.sqrt(np.mean(mono[: n * win].reshape(n, win) ** 2, axis=1))
    quiet = 20 * np.log10(np.maximum(rms, 1e-12)) < thr_db
    segs, start = [], None
    for i, q in enumerate(list(quiet) + [False]):
        if q and start is None:
            start = i
        elif not q and start is not None:
            if (i - start) * win / sr >= min_len:
                segs.append([round(start * win / sr, 2), round(i * win / sr, 2)])
            start = None
    return segs


def tempo(mono, sr):
    hop, nfft = 512, 2048
    if mono.size < sr * 4:
        return None, 0.0
    frames = 1 + (mono.size - nfft) // hop
    win = np.hanning(nfft)
    spec = np.abs(np.fft.rfft(np.stack([mono[i * hop:i * hop + nfft] * win for i in range(frames)]), axis=1))
    flux = np.maximum(np.diff(np.log1p(spec), axis=0), 0).sum(axis=1)
    if flux.size < 8 or np.percentile(flux, 95) < 1.0:
        return None, 0.0  # no rhythmic onsets (e.g. drone, pure tone, silence)
    flux = flux - flux.mean()
    ac = np.correlate(flux, flux, mode="full")[flux.size - 1:]
    fps = sr / hop
    lo, hi = int(fps * 60 / 200), int(fps * 60 / 60)
    if hi >= ac.size or ac[0] <= 0:
        return None, 0.0
    lag = lo + int(np.argmax(ac[lo:hi]))
    # parabolic interpolation for sub-frame precision
    if 0 < lag < ac.size - 1:
        y0, y1, y2 = ac[lag - 1], ac[lag], ac[lag + 1]
        den = y0 - 2 * y1 + y2
        lag = lag + (0.5 * (y0 - y2) / den if den else 0)
    bpm = 60 * fps / lag
    while bpm < 70:
        bpm *= 2
    while bpm > 180:
        bpm /= 2
    return round(bpm, 1), round(float(ac[int(round(lag))] / ac[0]), 3)


def analyze(path, target="streaming"):
    x, sr, bits = load(path)
    x = np.nan_to_num(x.astype(np.float64))
    n, ch = x.shape
    mono = x.mean(axis=1)
    peak = float(np.abs(x).max()) if n else 0.0
    rms = float(np.sqrt(np.mean(x ** 2))) if n else 0.0
    tp = true_peak(x)
    lufs, _ = integrated_lufs(x, sr)
    spec = np.abs(np.fft.rfft(mono[: min(mono.size, sr * 60)]))
    f = np.fft.rfftfreq(min(mono.size, sr * 60), 1 / sr)
    power = spec ** 2
    tot = power.sum() or 1
    centroid = float((f * power).sum() / tot)
    bands = {name: round(float(power[(f >= lo) & (f < hi)].sum() / tot), 4) for name, lo, hi in BANDS}
    bpm, conf = tempo(mono, sr)
    stereo = None
    if ch == 2:
        l, r = x[:, 0], x[:, 1]
        denom = math.sqrt(float((l ** 2).sum() * (r ** 2).sum())) or 1
        rl, rr = float(np.sqrt(np.mean(l ** 2))), float(np.sqrt(np.mean(r ** 2)))
        stereo = {"correlation": round(float((l * r).sum()) / denom, 3),
                  "balance_db_L_minus_R": db(rl / rr) if rl > 0 and rr > 0 else None}
    tl, ttp = TARGETS[target]
    rep = {
        "ok": True, "file": os.path.basename(path),
        "format": {"sample_rate": sr, "channels": ch, "bit_depth": bits, "duration_s": round(n / sr, 3)},
        "levels": {"peak_dbfs": db(peak), "true_peak_dbtp_approx": db(tp), "rms_dbfs": db(rms),
                   "crest_factor_db": db(peak / rms) if rms > 0 else None,
                   "integrated_lufs": lufs, "dc_offset": round(float(mono.mean()), 5),
                   "clipped_samples": int((np.abs(x) >= 0.999).sum())},
        "target": {"name": target, "lufs": tl, "true_peak_max": ttp,
                   "gain_to_target_db": None if lufs is None else round(tl - lufs, 2)},
        "spectrum": {"centroid_hz": round(centroid, 1), "band_energy_share": bands,
                     "brightness": "dark" if centroid < 1200 else "balanced" if centroid < 3500 else "bright"},
        "tempo": {"bpm_estimate": bpm, "confidence": conf},
        "stereo": stereo, "silence_segments": silence(mono, sr),
    }
    rep["fixes"] = fixes(rep)
    return rep


def fixes(r):
    s, lv, t = [], r["levels"], r["target"]
    if lv["clipped_samples"] > 0:
        s.append(f"يوجد {lv['clipped_samples']} عيّنة مقصوصة (clipping): خفّض الكسب وأعد التصدير")
    if lv["true_peak_dbtp_approx"] is not None and lv["true_peak_dbtp_approx"] > t["true_peak_max"]:
        s.append(f"القمة الحقيقية أعلى من {t['true_peak_max']} dBTP: استخدم limiter بسقف {t['true_peak_max']}")
    if t["gain_to_target_db"] is not None and abs(t["gain_to_target_db"]) > 1:
        s.append(f"غيّر الكسب بمقدار {t['gain_to_target_db']:+} dB للوصول إلى {t['lufs']} LUFS ({t['name']})")
    if abs(lv["dc_offset"]) > 0.005:
        s.append("يوجد انحياز DC: طبّق فلتر high-pass عند 20Hz")
    b = r["spectrum"]["band_energy_share"]
    if b["low_mid"] > 0.35:
        s.append("طاقة زائدة في 250–500Hz (عكارة): قصّ 2–4 dB")
    if b["presence"] < 0.03 and r["spectrum"]["brightness"] == "dark":
        s.append("الصوت مكتوم: ارفع 2–5kHz قليلاً لوضوح الكلام/الغناء")
    st = r["stereo"]
    if st and st["correlation"] < 0:
        s.append("ارتباط الستيريو سالب: مشكلة طور (phase)، افحص التوافق مع المونو")
    if st and st["balance_db_L_minus_R"] is not None and abs(st["balance_db_L_minus_R"]) > 1.5:
        s.append("عدم توازن بين اليسار واليمين")
    return s or ["القياسات ضمن الحدود المستهدفة"]


def summary_ar(r):
    f, lv, t, sp, tm = r["format"], r["levels"], r["target"], r["spectrum"], r["tempo"]
    return "\n".join([
        f"🎧 {r['file']} · {f['duration_s']}s · {f['sample_rate']}Hz · {f['channels']}ch · {f['bit_depth'] or '?'}bit",
        f"📊 LUFS {lv['integrated_lufs']} (الهدف {t['lufs']}) · Peak {lv['peak_dbfs']} dBFS · TP≈{lv['true_peak_dbtp_approx']} dBTP · Crest {lv['crest_factor_db']} dB",
        f"🎼 BPM≈{tm['bpm_estimate']} (ثقة {tm['confidence']}) · مركز الطيف {sp['centroid_hz']}Hz ({sp['brightness']})",
        "🛠️ " + " | ".join(r["fixes"]),
    ])


def plot(r, path, out):
    import matplotlib  # type: ignore
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # type: ignore
    x, sr, _ = load(path)
    mono = x.mean(axis=1)
    fig, ax = plt.subplots(2, 1, figsize=(10, 6))
    t = np.arange(mono.size) / sr
    ax[0].plot(t, mono, linewidth=0.3)
    ax[0].set_title("Waveform")
    ax[0].set_xlabel("s")
    seg = mono[: min(mono.size, sr * 60)]
    spec = 20 * np.log10(np.maximum(np.abs(np.fft.rfft(seg)), 1e-9))
    ax[1].semilogx(np.fft.rfftfreq(seg.size, 1 / sr)[1:], spec[1:], linewidth=0.4)
    ax[1].set_xlim(20, sr / 2)
    ax[1].set_title("Spectrum")
    ax[1].set_xlabel("Hz")
    fig.tight_layout()
    fig.savefig(out, dpi=120)


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    target, out_png = "streaming", None
    if "--target" in argv:
        target = argv[argv.index("--target") + 1]
        args.remove(target)
    if "--plot" in argv:
        out_png = argv[argv.index("--plot") + 1]
        args.remove(out_png)
    if not args or target not in TARGETS:
        print(__doc__)
        return 2
    try:
        r = analyze(args[0], target)
        if out_png:
            plot(r, args[0], out_png)
            r["plot"] = out_png
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 1
    if "--summary" in argv:
        print(summary_ar(r))
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
