#!/usr/bin/env python3
"""KOSIF Lighting calculator — deterministic photographic/cinema light math.

usage (JSON on stdin, one operation per call or a list):
  {"op": "inverse_square", "d1": 1, "d2": 2}                         -> intensity ratio & stops
  {"op": "ev", "aperture": 2.8, "shutter": "1/125", "iso": 100}      -> EV100 / scene EV
  {"op": "equivalent", "aperture": 2.8, "shutter": "1/125", "iso": 100,
                       "new_aperture": 1.4, "new_iso": 100}            -> matching shutter
  {"op": "ratio", "key_stops_over_fill": 2}                           -> lighting ratio 5:1 etc.
  {"op": "ratio_to_stops", "ratio": 4}                                 -> fill should be N stops under key
  {"op": "mired", "from_k": 3200, "to_k": 5600}                       -> mired shift + suggested gel
  {"op": "guide_number", "gn": 60, "iso": 100, "distance_m": 5}      -> f-number
  {"op": "softness", "source_size_m": 1.2, "distance_m": 1.5}        -> apparent angular size + label
  {"op": "shutter_angle", "fps": 24, "angle": 180}                   -> shutter speed
  {"op": "falloff", "subject_m": 2, "background_m": 4}               -> background darker by N stops
"""
import json
import math
import sys
from fractions import Fraction

GELS = [(-159, "Full CTB"), (-68, "1/2 CTB"), (-30, "1/4 CTB"), (-12, "1/8 CTB"),
        (0, "none"), (20, "1/8 CTO"), (42, "1/4 CTO"), (81, "1/2 CTO"), (159, "Full CTO")]


def sec(x):
    if isinstance(x, str) and "/" in x:
        return float(Fraction(x))
    return float(x)


def fmt_shutter(t):
    if t >= 1:
        return f"{t:.2f}s"
    return f"1/{round(1 / t)}s"


def op(o):
    k = o.get("op")
    if k == "inverse_square":
        d1, d2 = float(o["d1"]), float(o["d2"])
        r = (d1 / d2) ** 2
        return {"intensity_ratio": round(r, 4), "stops_change": round(math.log2(r), 2),
                "note": "negative stops = darker at new distance"}
    if k == "ev":
        N, t, iso = float(o["aperture"]), sec(o["shutter"]), float(o.get("iso", 100))
        ev100 = math.log2(N * N / t) - math.log2(iso / 100)
        scene = ("bright sun on sand/snow" if ev100 >= 16 else "full sun" if ev100 >= 14 else
                 "overcast/open shade" if ev100 >= 11 else "bright interior/sunset" if ev100 >= 8 else
                 "home interior" if ev100 >= 5 else "night street/candle" if ev100 >= 2 else "moonlit/very dark")
        return {"ev100": round(ev100, 2), "typical_scene": scene}
    if k == "equivalent":
        N, t, iso = float(o["aperture"]), sec(o["shutter"]), float(o.get("iso", 100))
        N2, iso2 = float(o.get("new_aperture", N)), float(o.get("new_iso", iso))
        t2 = t * (N2 / N) ** 2 * (iso / iso2)
        return {"new_shutter_s": round(t2, 6), "new_shutter": fmt_shutter(t2),
                "motion_warning": t2 > 1 / 60 and "handheld blur risk below 1/60s" or None}
    if k == "ratio":
        s = float(o["key_stops_over_fill"])
        r = 2 ** s + 1  # key+fill side vs fill-only side
        return {"lighting_ratio": f"{round(r, 1)}:1",
                "mood": "flat/commercial" if r <= 2.5 else "natural portrait" if r <= 4.5 else
                "dramatic" if r <= 9 else "low-key/noir"}
    if k == "ratio_to_stops":
        r = float(o["ratio"])
        if r <= 1:
            raise ValueError("ratio must be > 1")
        return {"fill_stops_under_key": round(math.log2(r - 1), 2)}
    if k == "mired":
        a, b = float(o["from_k"]), float(o["to_k"])
        shift = 1e6 / b - 1e6 / a
        gel = min(GELS, key=lambda g: abs(g[0] - shift))
        return {"mired_shift": round(shift, 1), "nearest_gel": gel[1],
                "direction": "warmer (orange)" if shift > 0 else "cooler (blue)" if shift < 0 else "none"}
    if k == "guide_number":
        gn, iso, d = float(o["gn"]), float(o.get("iso", 100)), float(o["distance_m"])
        return {"f_number": round(gn * math.sqrt(iso / 100) / d, 1)}
    if k == "softness":
        size, d = float(o["source_size_m"]), float(o["distance_m"])
        ang = math.degrees(2 * math.atan(size / (2 * d)))
        return {"apparent_angle_deg": round(ang, 1),
                "quality": "very soft" if ang > 45 else "soft" if ang > 20 else "medium" if ang > 8 else "hard",
                "tip": "move the source closer or enlarge it for softer shadows"}
    if k == "shutter_angle":
        fps, ang = float(o["fps"]), float(o.get("angle", 180))
        t = ang / 360 / fps
        return {"shutter_s": round(t, 6), "shutter": fmt_shutter(t)}
    if k == "falloff":
        s, b = float(o["subject_m"]), float(o["background_m"])
        stops = 2 * math.log2(b / s)
        return {"background_darker_by_stops": round(stops, 2),
                "tip": "increase light-to-subject distance for more even light; decrease for darker background"}
    raise ValueError(f"unknown op {k!r}")


def main():
    try:
        data = json.load(sys.stdin)
        items = data if isinstance(data, list) else [data]
        out = [{"op": i.get("op"), **op(i)} for i in items]
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps(out if isinstance(data, list) else out[0], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
