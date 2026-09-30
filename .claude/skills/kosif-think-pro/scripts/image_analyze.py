#!/usr/bin/env python3
"""KOSIF Vision — measured image analysis (Pillow + numpy).

usage:
  image_analyze.py IMAGE                 # full JSON report
  image_analyze.py IMAGE --summary       # short Arabic summary + JSON
  image_analyze.py A.jpg B.jpg --compare # metric-by-metric comparison

All numbers are measured from pixels/EXIF. Labels such as "warm" or "key light
from left" are heuristics derived from those numbers and are reported as such.
"""
import json
import math
import os
import sys

try:
    import numpy as np
    from PIL import ExifTags, Image, ImageOps
except ImportError as e:  # pragma: no cover
    print(json.dumps({"ok": False, "error": f"missing dependency: {e.name}; install pillow and numpy"}))
    raise SystemExit(2)

RATIOS = {"1:1": 1, "4:5": 0.8, "3:4": 0.75, "2:3": 2 / 3, "9:16": 9 / 16, "5:4": 1.25, "4:3": 4 / 3,
          "3:2": 1.5, "16:9": 16 / 9, "1.85:1": 1.85, "2:1": 2, "2.39:1": 2.39}
EXIF_KEYS = ("Make", "Model", "LensModel", "FNumber", "ExposureTime", "ISOSpeedRatings", "FocalLength",
             "FocalLengthIn35mmFilm", "DateTimeOriginal", "Software", "Flash", "WhiteBalance")


def load(path, max_side=1600):
    im = Image.open(path)
    info = {"file": os.path.basename(path), "format": im.format, "mode": im.mode,
            "width": im.width, "height": im.height, "bytes": os.path.getsize(path)}
    exif = {}
    try:
        raw = im.getexif()
        merged = dict(raw)
        try:
            merged.update(raw.get_ifd(0x8769))
        except Exception:  # noqa: BLE001
            pass
        for k, v in merged.items():
            name = ExifTags.TAGS.get(k, str(k))
            if name in EXIF_KEYS:
                exif[name] = float(v) if hasattr(v, "numerator") else (v if isinstance(v, (int, float)) else str(v))
    except Exception:  # noqa: BLE001
        pass
    im = ImageOps.exif_transpose(im).convert("RGB")
    if max(im.size) > max_side:
        im.thumbnail((max_side, max_side), Image.LANCZOS)
    return im, info, exif


def srgb_to_linear(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def cct_mccamy(rgb_mean):
    r, g, b = srgb_to_linear(np.array(rgb_mean, dtype=float))
    X = 0.4124 * r + 0.3576 * g + 0.1805 * b
    Y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    Z = 0.0193 * r + 0.1192 * g + 0.9505 * b
    s = X + Y + Z
    if s <= 0:
        return None
    x, y = X / s, Y / s
    n = (x - 0.3320) / (0.1858 - y)
    cct = 449 * n ** 3 + 3525 * n ** 2 + 6823.3 * n + 5520.33
    return int(round(cct)) if 1000 <= cct <= 25000 else None


def laplacian(gray):
    g = gray.astype(float)
    return -4 * g[1:-1, 1:-1] + g[:-2, 1:-1] + g[2:, 1:-1] + g[1:-1, :-2] + g[1:-1, 2:]


def sharpness(gray, grid=8):
    """Global Laplacian variance plus the 90th percentile over tiles, so a sharp
    subject on a smooth/bokeh background is still recognised as in focus."""
    lap = laplacian(gray)
    h, w = lap.shape
    tiles = [float(lap[i * h // grid:(i + 1) * h // grid, j * w // grid:(j + 1) * w // grid].var())
             for i in range(grid) for j in range(grid)]
    tiles.sort(reverse=True)
    return float(lap.var()), sum(tiles[:3]) / 3  # focus region = mean of the 3 most detailed tiles


def noise_sigma(gray):
    """Immerkaer (1996) fast noise variance estimate."""
    g = gray.astype(float)
    h, w = g.shape
    if h < 3 or w < 3:
        return 0.0
    m = (g[:-2, :-2] - 2 * g[:-2, 1:-1] + g[:-2, 2:] - 2 * g[1:-1, :-2] + 4 * g[1:-1, 1:-1]
         - 2 * g[1:-1, 2:] + g[2:, :-2] - 2 * g[2:, 1:-1] + g[2:, 2:])
    return float(math.sqrt(math.pi / 2) * np.abs(m).sum() / (6 * (w - 2) * (h - 2)))


def palette(im, k=6):
    small = im.copy()
    small.thumbnail((256, 256))
    q = small.quantize(colors=k, method=Image.MEDIANCUT)
    pal = q.getpalette()[: 3 * k]
    counts = sorted(q.getcolors(), reverse=True)
    total = sum(c for c, _ in counts)
    out = []
    for c, idx in counts:
        r, g, b = pal[3 * idx: 3 * idx + 3]
        out.append({"hex": f"#{r:02X}{g:02X}{b:02X}", "share": round(c / total, 3)})
    return out


def nearest_ratio(w, h):
    r = w / h
    name = min(RATIOS, key=lambda k: abs(math.log(RATIOS[k] / r)))
    return {"value": round(r, 4), "nearest": name, "exact": abs(RATIOS[name] - r) / r < 0.01}


def analyze(path):
    im, info, exif = load(path)
    a = np.asarray(im).astype(float)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    Y = 0.2126 * R + 0.7152 * G + 0.0722 * B
    h, w = Y.shape

    p1, p50, p99 = (float(np.percentile(Y, q)) for q in (1, 50, 99))
    clip_hi = float((a.max(axis=2) >= 250).mean())
    clip_lo = float((Y <= 5).mean())
    mean_y = float(Y.mean())
    exposure = ("overexposed" if mean_y > 185 or clip_hi > 0.05 else
                "underexposed" if mean_y < 60 or clip_lo > 0.15 else "balanced")
    zones = {"shadows_0_85": float((Y < 85).mean()), "mids_85_170": float(((Y >= 85) & (Y < 170)).mean()),
             "highlights_170_255": float((Y >= 170).mean())}
    key = "high-key" if zones["highlights_170_255"] > 0.5 else "low-key" if zones["shadows_0_85"] > 0.5 else "mid-key"

    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    rg, yb = R - G, 0.5 * (R + G) - B
    colorful = float(math.hypot(rg.std(), yb.std()) + 0.3 * math.hypot(rg.mean(), yb.mean()))
    rgb_mean = [float(R.mean()), float(G.mean()), float(B.mean())]
    cast = rgb_mean[0] - rgb_mean[2]
    cct = cct_mccamy(rgb_mean)

    gray = Y
    sharp_global, sharp = sharpness(gray)
    noise = noise_sigma(gray)

    # lighting direction heuristic: compare halves of the mid/high tones
    left, right = float(Y[:, : w // 2].mean()), float(Y[:, w // 2:].mean())
    top, bottom = float(Y[: h // 2].mean()), float(Y[h // 2:].mean())
    dx, dy = right - left, bottom - top
    horiz = "right" if dx > 8 else "left" if dx < -8 else "center"
    vert = "below" if dy > 8 else "above" if dy < -8 else "level"
    # contrast ratio between lit and shadow side in stops
    lit, shade = max(left, right), max(min(left, right), 1)
    side_ratio = round(math.log2(lit / shade), 2)

    # composition: gradient-magnitude centroid as saliency proxy
    gy, gx = np.gradient(gray)
    mag = np.hypot(gx, gy)
    thr = max(float(np.percentile(mag, 99)), 0.3 * float(mag.max()))
    mag = np.where(mag >= thr, mag, 0)  # dominant edges only: ignores noise and smooth gradients
    tot = mag.sum() or 1
    cy = float((mag.sum(axis=1) * np.arange(h)).sum() / tot) / h
    cx = float((mag.sum(axis=0) * np.arange(w)).sum() / tot) / w
    thirds = [(x, y) for x in (1 / 3, 2 / 3) for y in (1 / 3, 2 / 3)]
    d_third = min(math.hypot(cx - x, cy - y) for x, y in thirds)
    d_center = math.hypot(cx - 0.5, cy - 0.5)
    placement = "rule-of-thirds" if d_third < 0.08 else "centered" if d_center < 0.08 else "off-grid"
    sym = float(1 - np.abs(gray - gray[:, ::-1]).mean() / 255)

    report = {
        "ok": True, "file": info, "exif": exif or None,
        "geometry": {"width": info["width"], "height": info["height"],
                     "megapixels": round(info["width"] * info["height"] / 1e6, 2),
                     "aspect_ratio": nearest_ratio(info["width"], info["height"]),
                     "orientation": "landscape" if info["width"] > info["height"] else
                     "portrait" if info["height"] > info["width"] else "square"},
        "exposure": {"mean_luma": round(mean_y, 1), "p1": round(p1, 1), "median": round(p50, 1),
                     "p99": round(p99, 1), "dynamic_range_used": round(p99 - p1, 1),
                     "contrast_std": round(float(Y.std()), 1), "clipped_highlights_pct": round(100 * clip_hi, 2),
                     "crushed_shadows_pct": round(100 * clip_lo, 2), "zones": {k: round(v, 3) for k, v in zones.items()},
                     "tonal_key": key, "verdict": exposure},
        "color": {"mean_rgb": [round(c, 1) for c in rgb_mean], "estimated_cct_k": cct,
                  "cast": "warm" if cast > 12 else "cool" if cast < -12 else "neutral",
                  "saturation_mean": round(float(sat.mean()), 3), "colorfulness": round(colorful, 1),
                  "colorfulness_label": ("not colorful" if colorful < 15 else "slightly" if colorful < 33 else
                                         "moderately" if colorful < 45 else "averagely" if colorful < 59 else
                                         "quite" if colorful < 82 else "highly"),
                  "palette": palette(im)},
        "detail": {"sharpness_laplacian_var": round(sharp, 1), "sharpness_global_var": round(sharp_global, 1),
                   "sharpness_label": "blurry" if sharp < 60 else "soft" if sharp < 150 else "sharp",
                   "noise_sigma": round(noise, 2),
                   "noise_label": "clean" if noise < 2.5 else "moderate" if noise < 6 else "noisy",
                   "measured_at": f"{w}x{h}"},
        "lighting_heuristic": {"brighter_side": horiz, "vertical_bias": vert, "side_ratio_stops": side_ratio,
                               "lighting_ratio": f"{round(2 ** side_ratio, 1)}:1",
                               "note": "heuristic from luminance halves; confirm visually"},
        "composition": {"visual_centroid": [round(cx, 3), round(cy, 3)], "placement": placement,
                        "nearest_thirds_distance": round(d_third, 3), "mirror_symmetry": round(sym, 3)},
    }
    report["fixes"] = suggest(report)
    return report


def suggest(r):
    s = []
    e, c, d = r["exposure"], r["color"], r["detail"]
    if e["clipped_highlights_pct"] > 2:
        s.append("خفّض التعريض أو الإضاءات العالية: توجد مناطق محترقة")
    if e["crushed_shadows_pct"] > 10:
        s.append("ارفع الظلال أو أضف ضوء تعبئة: تفاصيل الظل مفقودة")
    if e["dynamic_range_used"] < 120:
        s.append("التباين منخفض: وسّع نطاق النغمات (levels/curves)")
    if d["sharpness_label"] != "sharp":
        s.append("الصورة غير حادة: استخدم سرعة غالق أعلى أو ركّز بدقة أو طبّق تحديداً خفيفاً")
    if d["noise_label"] == "noisy":
        s.append("الضجيج مرتفع: قلّل ISO أو طبّق إزالة ضجيج")
    if c["cast"] != "neutral":
        s.append(f"يوجد ميل لوني {'دافئ' if c['cast'] == 'warm' else 'بارد'}: صحّح توازن الأبيض إن لم يكن مقصوداً")
    if r["composition"]["placement"] == "off-grid":
        s.append("مركز الاهتمام خارج خطوط الأثلاث: جرّب قصّاً يضعه على تقاطع")
    return s or ["لا توجد مشاكل تقنية واضحة في القياسات"]


def compare(p1, p2):
    a, b = analyze(p1), analyze(p2)
    keys = [("exposure", "mean_luma"), ("exposure", "contrast_std"), ("exposure", "clipped_highlights_pct"),
            ("exposure", "crushed_shadows_pct"), ("color", "estimated_cct_k"), ("color", "saturation_mean"),
            ("color", "colorfulness"), ("detail", "sharpness_laplacian_var"), ("detail", "noise_sigma"),
            ("composition", "mirror_symmetry")]
    rows = []
    for sec, k in keys:
        va, vb = a[sec][k], b[sec][k]
        rows.append({"metric": f"{sec}.{k}", "A": va, "B": vb,
                     "delta": None if va is None or vb is None else round(vb - va, 3)})
    return {"ok": True, "A": a["file"]["file"], "B": b["file"]["file"], "comparison": rows,
            "sharper": "A" if a["detail"]["sharpness_laplacian_var"] > b["detail"]["sharpness_laplacian_var"] else "B",
            "cleaner": "A" if a["detail"]["noise_sigma"] < b["detail"]["noise_sigma"] else "B"}


def summary_ar(r):
    e, c, d, l, g = r["exposure"], r["color"], r["detail"], r["lighting_heuristic"], r["geometry"]
    return "\n".join([
        f"📐 {g['width']}×{g['height']} ({g['megapixels']}MP) — نسبة {g['aspect_ratio']['nearest']}",
        f"☀️ التعريض: {e['verdict']} · متوسط {e['mean_luma']} · احتراق {e['clipped_highlights_pct']}% · ظلال مطموسة {e['crushed_shadows_pct']}% · {e['tonal_key']}",
        f"🎨 الألوان: {c['cast']} · حرارة تقديرية {c['estimated_cct_k']}K · تشبّع {c['saturation_mean']} · لوحة: {' '.join(p['hex'] for p in c['palette'])}",
        f"🔍 الحدة: {d['sharpness_label']} ({d['sharpness_laplacian_var']}) · الضجيج: {d['noise_label']} ({d['noise_sigma']})",
        f"💡 الإضاءة (تقدير): الجانب الأسطع {l['brighter_side']} · نسبة {l['lighting_ratio']}",
        f"🧭 التكوين: {r['composition']['placement']}",
        "🛠️ " + " | ".join(r["fixes"]),
    ])


def main(argv):
    args = [x for x in argv if not x.startswith("--")]
    flags = {x for x in argv if x.startswith("--")}
    if not args:
        print(__doc__)
        return 2
    try:
        if "--compare" in flags:
            if len(args) != 2:
                raise ValueError("--compare needs exactly two images")
            out = compare(args[0], args[1])
        else:
            out = analyze(args[0])
            if "--summary" in flags:
                print(summary_ar(out))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 1
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
