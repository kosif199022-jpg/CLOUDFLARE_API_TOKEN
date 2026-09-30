#!/usr/bin/env python3
"""KOSIF Prompt Forge — one structured spec → correctly formatted prompts for each generator.

stdin JSON (English values; only `text` may be Arabic because it is rendered on the image):
{"mode": "image"|"video",
 "subject": "a Saudi barista in a linen apron", "action": "pouring latte art",
 "environment": "minimal cafe with palm-wood counter", "time": "early morning",
 "shot": "medium close-up", "angle": "eye level", "lens": "85mm f/1.8",
 "lighting": "soft window key from camera left, warm 3800K", "palette": "cream, walnut, sage green",
 "style": "photorealistic editorial", "quality": ["natural skin texture", "sharp focus"],
 "aspect": "4:5", "negative": ["text artifacts", "extra fingers"], "text": "صباح الخير",
 "locks": {"character": "Layla · 28 · warm olive skin ..."},
 "camera_move": "slow push-in", "duration": "6 seconds", "motion": "steam rising", "fps": "24fps",   # video
 "platforms": ["chatgpt", "midjourney", "flux", "sdxl", "ideogram"] }                                 # optional
Platforms: chatgpt (DALL·E / GPT image), midjourney, flux, sdxl, ideogram, sora, veo, runway, kling.
Output: {"prompts": {platform: {...}}, "warnings": [...]} — lint each with kosif-image-studio prompt_lint.py.
"""
import json
import re
import sys

IMAGE = ["chatgpt", "midjourney", "flux", "sdxl", "ideogram"]
VIDEO = ["sora", "veo", "runway", "kling"]
FIELDS = ["subject", "action", "environment", "time", "shot", "angle", "lens", "lighting", "palette", "style"]


def _clean(s):
    return re.sub(r"\s+", " ", str(s or "")).strip().rstrip(".")


def _core(sp):
    locks = [_clean(v) for v in (sp.get("locks") or {}).values() if v]
    who = ", ".join(x for x in [_clean(sp.get("subject")), _clean(sp.get("action"))] if x)
    where = ", ".join(x for x in [_clean(sp.get("environment")), _clean(sp.get("time"))] if x)
    cam = ", ".join(x for x in [_clean(sp.get("shot")), _clean(sp.get("angle")), _clean(sp.get("lens"))] if x)
    return locks, who, where, cam


def forge(sp):
    mode = sp.get("mode", "image")
    if mode not in {"image", "video"}:
        raise ValueError("mode must be image or video")
    if not _clean(sp.get("subject")):
        raise ValueError("subject is required")
    warnings = []
    for k in FIELDS + ["camera_move", "motion"]:
        if re.search(r"[؀-ۿ]", str(sp.get(k, ""))):
            warnings.append(f"field '{k}' is Arabic: write generation fields in English; keep Arabic only in 'text'")
    missing = [k for k in ("lighting", "lens", "style", "aspect") if not sp.get(k)]
    if missing:
        warnings.append(f"missing {missing}: prompts will be weaker")
    platforms = sp.get("platforms") or (VIDEO if mode == "video" else IMAGE)
    unknown = [p for p in platforms if p not in IMAGE + VIDEO]
    if unknown:
        raise ValueError(f"unknown platforms {unknown}")
    locks, who, where, cam = _core(sp)
    light, pal, style = _clean(sp.get("lighting")), _clean(sp.get("palette")), _clean(sp.get("style"))
    quality = ", ".join(_clean(q) for q in sp.get("quality") or [])
    aspect = _clean(sp.get("aspect")) or "1:1"
    neg = [_clean(n) for n in sp.get("negative") or []]
    text = _clean(sp.get("text"))
    if text and re.search(r"[؀-ۿ]", text):
        warnings.append("Arabic on-image text often renders imperfectly: prefer Ideogram or add it as an overlay layer (IBM Plex Sans Arabic / Cairo)")
    lock_line = " ".join(f"[{l}]" for l in locks)
    out = {}
    for p in platforms:
        if p == "chatgpt":
            parts = [f"Create a {style or 'photorealistic'} image in {aspect} aspect ratio."]
            if lock_line:
                parts.append(f"Keep this identity exactly: {lock_line}.")
            parts.append(f"Subject: {who}.")
            if where:
                parts.append(f"Setting: {where}.")
            if cam:
                parts.append(f"Camera: {cam}.")
            if light:
                parts.append(f"Lighting: {light}.")
            if pal:
                parts.append(f"Palette: {pal}.")
            if quality:
                parts.append(f"Quality: {quality}.")
            if text:
                parts.append(f'Render this exact text: "{text}".')
            if neg:
                parts.append(f"Avoid: {', '.join(neg)}.")
            out[p] = {"prompt": " ".join(parts)}
        elif p == "midjourney":
            body = ", ".join(x for x in [lock_line, who, where, cam, light, pal, style, quality] if x)
            if text:
                body += f', the text "{text}"'
            params = f" --ar {aspect} --style raw --v 7" + (f" --no {', '.join(neg)}" if neg else "")
            out[p] = {"prompt": body + params, "notes": "add --cref URL --cw 80 for character reference; --sref URL for style"}
        elif p == "flux":
            body = f"{style.capitalize() + ' image' if style else 'An image'} of {who}"
            body += f", {where}" if where else ""
            body += f". Shot as {cam}" if cam else ""
            body += f", lit by {light}" if light else ""
            body += f", palette of {pal}" if pal else ""
            body += f". {quality.capitalize()}" if quality else ""
            if lock_line:
                body = f"{lock_line} " + body
            if text:
                body += f'. The text "{text}" appears clearly'
            out[p] = {"prompt": body + f". Aspect ratio {aspect}.", "notes": "Flux has no negative prompt: describe the clean result you want instead; guidance 3–4"}
        elif p == "sdxl":
            tags = [f"({who}:1.2)"] + [x for x in [lock_line, where, cam, light, pal, style, quality] if x]
            out[p] = {"prompt": ", ".join(tags), "negative_prompt": ", ".join(neg + ["lowres", "jpeg artifacts", "watermark"]),
                      "notes": f"1024px base resolution matching {aspect}; CFG 5–7; 30–40 steps"}
        elif p == "ideogram":
            q = f'"{text}" ' if text else ""
            out[p] = {"prompt": f"{q}{style + ' ' if style else ''}design of {who}" + (f", {where}" if where else "") +
                      (f", {light}" if light else "") + (f", palette {pal}" if pal else "") + f", aspect {aspect}",
                      "notes": "put exact on-image text first in quotes; choose Design or Realistic style type"}
        else:  # video
            move, dur, motion, fps = (_clean(sp.get(k)) for k in ("camera_move", "duration", "motion", "fps"))
            if not (move and dur):
                warnings.append(f"{p}: video needs camera_move and duration")
            body = ". ".join(x for x in [
                lock_line, f"{who}" + (f" while {motion}" if motion else ""), where and f"Setting: {where}",
                cam and f"Camera: {cam}" + (f", {move}" if move else ""), light and f"Lighting: {light}",
                pal and f"Palette: {pal}", style and f"Style: {style}", quality] if x)
            body += f". Duration {dur or '5 seconds'}, {fps or '24fps'}, aspect ratio {aspect}."
            notes = {"sora": "describe one continuous shot; keep physics plausible",
                     "veo": "Veo can add native audio: append 'Audio: …' with ambience and SFX",
                     "runway": "start from an approved keyframe (image-to-video) for identity consistency",
                     "kling": "use the motion brush for subject paths; keep 5–10 s per shot"}[p]
            out[p] = {"prompt": body, "negative_prompt": ", ".join(neg) if neg and p in {"kling", "runway"} else None, "notes": notes}
    return {"mode": mode, "prompts": out, "warnings": warnings,
            "next": "lint each prompt: python3 prompt_lint.py (kosif-image-studio) with mode image/video and the contract + locks"}


def main():
    try:
        res = forge(json.load(sys.stdin))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
