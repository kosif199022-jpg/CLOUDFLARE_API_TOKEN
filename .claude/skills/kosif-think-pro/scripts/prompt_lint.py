#!/usr/bin/env python3
"""KOSIF Image/Video Studio — prompt linter + Execution Contract binding.

stdin JSON:
{"prompt": "...", "mode": "image"|"video",
 "contract": {"required": ["duck", "lacquered armor"], "forbidden": ["rifle", "tactical"]},   # optional
 "locks": {"character": "…exact Character Lock text…", "style": "…Style Lock…"}             # optional
}
Checks the prompt against the KOSIF formula (subject, action, environment, camera,
lens, lighting, color/grade, style, quality, aspect ratio; for video also motion,
camera movement, duration, pacing), Execution Contract required/forbidden terms,
verbatim locks, contradictions and length. Returns score, missing parts, and
verdict PASS / REVISE / BLOCK (BLOCK = forbidden term present or required missing).
"""
import json
import re
import sys

PARTS = {
    "camera": r"\b(close[- ]?up|extreme close|medium shot|wide shot|full[- ]body|establishing|over[- ]the[- ]shoulder|pov|aerial|bird'?s[- ]eye|low[- ]angle|high[- ]angle|eye[- ]level|dutch|macro|portrait shot|headshot|two[- ]shot|shot)\b",
    "lens": r"\b(\d{2,3}\s?mm|f/\d(\.\d)?|anamorphic|telephoto|wide[- ]angle|fisheye|tilt[- ]shift|bokeh|depth of field|dof)\b",
    "lighting": r"\b(light(ing)?|lit|rim|backlight|key light|fill|softbox|golden hour|blue hour|rembrandt|butterfly|split light|neon|volumetric|god rays|chiaroscuro|shadow|sunlight|moonlight|candle|overcast|\d{4}\s?k\b)",
    "color": r"\b(palette|teal|orange|grade|graded|color grading|colour|monochrome|black and white|pastel|muted|vibrant|desaturated|warm tones|cool tones|#[0-9a-f]{6})\b",
    "style": r"\b(photoreal(istic)?|cinematic|film still|illustration|oil painting|watercolor|3d render|pixar|anime|ghibli|isometric|vector|minimal(ist)?|editorial|commercial|documentary|fashion|concept art|portra|kodak|fujifilm|arri|sony a7|canon|nikon|octane|unreal engine)\b",
    "quality": r"\b(ultra[- ]detailed|highly detailed|intricate|sharp focus|razor[- ]sharp|8k|4k|high resolution|hdr|micro[- ]details|texture|pores|physically[- ]based)\b",
    "aspect": r"(\b\d{1,2}:\d{1,2}\b|\b2\.39:1\b|--ar\s+\d+:\d+|\baspect ratio\b|\b(vertical|horizontal|square) format\b)",
    "environment": r"\b(in|at|on|inside|outside|background|interior|exterior|street|forest|desert|city|studio|room|beach|mountain|temple|courtyard|space|ocean|market|office|kitchen)\b",
}
VIDEO = {
    "camera_move": r"\b(dolly|push[- ]in|pull[- ]out|pan|tilt|tracking|crane|handheld|steadicam|orbit|zoom|static camera|locked[- ]off|drone|whip)\b",
    "duration": r"\b(\d+(\.\d+)?\s?(s|sec|seconds))\b",
    "motion": r"\b(walk(s|ing)?|run(s|ning)?|turn(s|ing)?|slow[- ]motion|moves?|moving|flow(s|ing)?|falls?|rises?|dance|blink|wind|rain falling|timelapse|time[- ]lapse)\b",
    "pacing": r"\b(\d{2}\s?fps|slow|fast|real[- ]time|beat|cut|transition|continuous|one take|single take)\b",
}
CONFLICTS = [("photorealistic", "cartoon"), ("photorealistic", "anime"), ("black and white", "vibrant"),
             ("minimalist", "intricate"), ("daylight", "night"), ("golden hour", "midnight"),
             ("shallow depth of field", "everything in focus"), ("high-key", "low-key")]
WEIGHTS = {"subject": 20, "camera": 10, "lens": 8, "lighting": 14, "color": 8, "style": 10, "quality": 8,
           "aspect": 8, "environment": 14}


def lint(o):
    prompt = str(o.get("prompt", "")).strip()
    if not prompt:
        raise ValueError("prompt is empty")
    mode = o.get("mode", "image")
    low = prompt.lower()
    found = {k: bool(re.search(rx, low)) for k, rx in PARTS.items()}
    words = re.findall(r"[a-z؀-ۿ']+", low)
    found["subject"] = len(words) >= 4
    weights = dict(WEIGHTS)
    if mode == "video":
        for k, rx in VIDEO.items():
            found[k] = bool(re.search(rx, low))
            weights[k] = 8
    score = round(100 * sum(w for k, w in weights.items() if found.get(k)) / sum(weights.values()))
    missing = [k for k in weights if not found.get(k)]

    issues, verdict = [], "PASS"
    c = o.get("contract") or {}
    req_missing = [t for t in c.get("required", []) if t.lower() not in low]
    forb_present = [t for t in c.get("forbidden", []) if re.search(r"\b" + re.escape(t.lower()) + r"\b", low)
                    and not re.search(r"\b(no|without|not|avoid)\s+(\w+\s+){0,2}" + re.escape(t.lower()), low)]
    if req_missing or forb_present:
        verdict = "BLOCK"
        if req_missing:
            issues.append(f"contract required missing: {req_missing}")
        if forb_present:
            issues.append(f"contract forbidden present: {forb_present}")
    for name, text in (o.get("locks") or {}).items():
        if text and text.strip().lower() not in low:
            issues.append(f"{name} lock not included verbatim")
            verdict = "BLOCK" if verdict == "BLOCK" else "REVISE"
    for a, b in CONFLICTS:
        if a in low and b in low:
            issues.append(f"contradiction: '{a}' vs '{b}'")
            verdict = "BLOCK" if verdict == "BLOCK" else "REVISE"
    if re.search(r"[؀-ۿ]", prompt):
        issues.append("prompt contains Arabic: write the generation prompt in English; keep only quoted on-image text in Arabic")
        verdict = "BLOCK" if verdict == "BLOCK" else "REVISE"
    n = len(words)
    if n < 25:
        issues.append(f"prompt is short ({n} words): add camera/lighting/style detail")
    elif n > 220:
        issues.append(f"prompt is long ({n} words): models may ignore the tail; move key constraints to the front")
    if score < 60 and verdict == "PASS":
        verdict = "REVISE"
    hints = {
        "subject": "describe the main subject precisely (who/what, look, materials)",
        "camera": "add shot type + angle (e.g. medium shot, low angle)",
        "lens": "add lens/aperture (e.g. 85mm f/1.4, shallow depth of field)",
        "lighting": "add lighting direction/quality/temperature (e.g. soft key from left, rim light, 3200K)",
        "color": "add palette/grade (e.g. teal-orange grade, muted earth tones)",
        "style": "add style/medium (e.g. photorealistic film still, Kodak Portra 400)",
        "quality": "add quality cues (ultra-detailed, sharp focus, natural skin texture)",
        "aspect": "add aspect ratio (16:9, 9:16, 4:5, 1:1, 2.39:1)",
        "environment": "add location/background/time of day",
        "camera_move": "add camera movement (slow dolly-in, tracking shot, static)",
        "duration": "add clip duration (e.g. 5 seconds)",
        "motion": "describe subject motion over time",
        "pacing": "add pacing/fps (24fps, slow motion, single continuous take)",
    }
    return {"verdict": verdict, "score": score, "mode": mode, "components": found, "missing": missing,
            "suggestions": [hints[m] for m in missing], "issues": issues, "word_count": n}


def main():
    try:
        out = lint(json.load(sys.stdin))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"verdict": "INVALID", "error": str(e)}))
        return 2
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))
    return {"PASS": 0, "REVISE": 1, "BLOCK": 3}[out["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
