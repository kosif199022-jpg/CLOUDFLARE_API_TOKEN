#!/usr/bin/env python3
"""KOSIF Web Design — accessible design tokens (light + dark) from one brand colour.

stdin JSON: {"brand": "#8a5a2b", "name": "kosif", "base_font": 16, "ratio": 1.25, "radius": 12,
             "font": "\"IBM Plex Sans Arabic\", system-ui, sans-serif"}
Produces surfaces, text, brand, on-brand, focus, line and status colours for both themes, adjusting
lightness until every text pair meets WCAG AA (4.5:1) and UI/brand-vs-background meets 3:1; plus spacing,
radius, type scale and motion tokens. Output: {"tokens": {...}, "css": "...", "contrast": [...], "ok": bool}.
The CSS follows the dark-mode contract: :root (light), @media (prefers-color-scheme: dark) guarded by
:root:not([data-theme="light"]), and :root[data-theme="dark"]; reduced motion zeroes durations.
"""
import colorsys
import json
import re
import sys


def to_rgb(h):
    h = h.strip().lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]{3}|[0-9a-fA-F]{6}", h):
        raise ValueError(f"invalid hex colour #{h}")
    h = "".join(c * 2 for c in h) if len(h) == 3 else h
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def to_hex(rgb):
    return "#" + "".join(f"{round(max(0, min(1, c)) * 255):02x}" for c in rgb)


def lum(rgb):
    f = lambda v: v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4  # noqa: E731
    r, g, b = (f(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    x, y = sorted((lum(to_rgb(a)), lum(to_rgb(b))), reverse=True)
    return (x + 0.05) / (y + 0.05)


def hls(hexc):
    return colorsys.rgb_to_hls(*to_rgb(hexc))


def mk(h, l, s):
    return to_hex(colorsys.hls_to_rgb(h, max(0, min(1, l)), max(0, min(1, s))))


def fit(hue, sat, against, need, start, step):
    """Move lightness from `start` in direction `step` until contrast with `against` ≥ need."""
    l = start
    for _ in range(200):
        c = mk(hue, l, sat)
        if ratio(c, against) >= need:
            return c
        l += step
        if not 0 <= l <= 1:
            break
    return "#000000" if step < 0 else "#ffffff"


def theme(brand, dark):
    h, l, s = hls(brand)
    if not dark:
        bg, surface, surface2 = mk(h, 0.975, min(s, 0.25)), "#ffffff", mk(h, 0.955, min(s, 0.2))
        line = mk(h, 0.86, min(s, 0.18))
        ink = mk(h, 0.1, min(s, 0.35))
        ink2 = fit(h, min(s, 0.2), surface2, 4.6, 0.42, -0.01)
        brand_c = fit(h, s, bg, 4.6, min(l, 0.5), -0.01)
        on_brand = "#ffffff" if ratio("#ffffff", brand_c) >= 4.5 else "#000000"
        status_l, step = 0.4, -0.01
    else:
        bg, surface, surface2 = mk(h, 0.07, min(s, 0.3)), mk(h, 0.11, min(s, 0.25)), mk(h, 0.15, min(s, 0.2))
        line = mk(h, 0.24, min(s, 0.18))
        ink = mk(h, 0.94, min(s, 0.3))
        ink2 = fit(h, min(s, 0.2), surface2, 4.6, 0.6, 0.01)
        brand_c = fit(h, min(1, s + 0.05), bg, 4.6, max(l, 0.6), 0.01)
        on_brand = "#000000" if ratio("#000000", brand_c) >= ratio("#ffffff", brand_c) else "#ffffff"
        status_l, step = 0.62, 0.01
    t = {"bg": bg, "surface": surface, "surface-2": surface2, "line": line, "ink": ink, "ink-2": ink2,
         "brand": brand_c, "on-brand": on_brand, "focus": brand_c}
    for name, hue in (("ok", 140 / 360), ("warn", 35 / 360), ("bad", 4 / 360), ("info", 200 / 360)):
        t[name] = fit(hue, 0.65, surface, 4.6, status_l, step)
    return t


def scale(base, r):
    names = ["xs", "s", "m", "l", "xl", "2xl", "3xl"]
    return {n: f"{round(base * r ** (i - 2), 2)}px" for i, n in enumerate(names)}


def build(o):
    brand = o.get("brand")
    if not brand:
        raise ValueError("brand colour is required")
    brand = to_hex(to_rgb(brand))
    base = float(o.get("base_font", 16))
    r = float(o.get("ratio", 1.25))
    light, dark = theme(brand, False), theme(brand, True)
    common = {**{f"space-{i}": f"{v}px" for i, v in enumerate([4, 8, 12, 16, 24, 32, 48, 64], 1)},
              "radius-s": f"{max(2, int(o.get('radius', 12)) // 2)}px", "radius": f"{int(o.get('radius', 12))}px", "radius-pill": "999px",
              **{f"fs-{k}": v for k, v in scale(base, r).items()},
              "font": o.get("font", '"IBM Plex Sans Arabic", system-ui, "Segoe UI", Tahoma, sans-serif'),
              "lh": "1.6", "measure": "68ch", "t-fast": "120ms", "t": "180ms", "ease": "cubic-bezier(.2,.8,.2,1)",
              "touch": "44px"}
    pairs = [("ink", "bg", 4.5), ("ink", "surface", 4.5), ("ink-2", "surface", 4.5), ("ink-2", "surface-2", 4.5),
             ("on-brand", "brand", 4.5), ("brand", "bg", 3.0), ("ok", "surface", 4.5), ("warn", "surface", 4.5),
             ("bad", "surface", 4.5), ("info", "surface", 4.5), ("focus", "bg", 3.0)]
    report = []
    for tname, t in (("light", light), ("dark", dark)):
        for fg, bg, need in pairs:
            rr = ratio(t[fg], t[bg])
            report.append({"theme": tname, "pair": f"{fg} on {bg}", "ratio": round(rr, 2), "needed": need, "pass": rr >= need})
    prefix = re.sub(r"[^a-z0-9-]", "", str(o.get("name", "k")).lower()) or "k"
    var = lambda d: ";".join(f"--{prefix}-{k}:{v}" for k, v in d.items())  # noqa: E731
    css = (f":root{{{var(common)};{var(light)};color-scheme:light}}\n"
           f"@media (prefers-color-scheme: dark){{:root:not([data-theme=\"light\"]){{{var(dark)};color-scheme:dark}}}}\n"
           f":root[data-theme=\"dark\"]{{{var(dark)};color-scheme:dark}}\n"
           f"@media (prefers-reduced-motion: reduce){{:root{{--{prefix}-t-fast:0ms;--{prefix}-t:0ms}}}}\n"
           f"body{{background:var(--{prefix}-bg);color:var(--{prefix}-ink);font:var(--{prefix}-fs-m)/var(--{prefix}-lh) var(--{prefix}-font)}}\n"
           f":focus-visible{{outline:3px solid var(--{prefix}-focus);outline-offset:2px}}\n")
    return {"ok": all(x["pass"] for x in report), "brand_input": brand,
            "tokens": {"common": common, "light": light, "dark": dark}, "contrast": report, "css": css}


def main():
    try:
        out = build(json.load(sys.stdin))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
