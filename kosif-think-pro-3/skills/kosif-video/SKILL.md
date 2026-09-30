---
name: kosif-video
description: Use for video creation and cinematography — AI video prompts (Sora, Veo, Runway, Kling, Luma, Pika, Seedance, Hailuo), shot lists, storyboards, reels/shorts/ads scripts, camera movement, continuity between shots, editing plans, subtitles and timing. Triggers on /video /shots /storyboard /reel /ad, "فيديو", "ريلز", "إعلان", "مشهد", "لقطة".
---
# KOSIF Video Director

## Pipeline
1. **Frame**: platform (Reels/TikTok 9:16, YouTube 16:9, cinema 2.39:1), total duration, goal (sell, tell, teach), audience, hook in the first 1–2 s, call to action.
2. **Locks**: Character Lock(s) + Style Lock + Location Lock (from kosif-image-studio) — reused verbatim in every shot prompt for continuity.
3. **Beat sheet**: hook → setup → escalation → payoff → CTA with timecodes.
4. **Shot list table**: # · time (start–end) · shot type · lens · camera move · action · lighting (kosif-lighting preset) · audio/VO/SFX (kosif-audio) · on-screen text · transition.
5. **Per-shot prompts** (English): `[Locks] + [action over time] + [camera move + speed] + [lens] + [lighting] + [environment motion: wind, rain, crowd] + [duration 5–10 s] + [fps / slow motion] + [style/grade] + [aspect ratio]`. Lint each with `../kosif-image-studio/scripts/prompt_lint.py` using `"mode": "video"`.
6. **Keyframe first**: generate/approve a still per shot (image-to-video) for identity consistency when the platform supports it.
7. **Edit plan**: order, cut points on beats (use BPM from kosif-audio: beat = 60/BPM s), music, VO, SFX, subtitles (max 42 chars/line, 1–2 lines, 1–7 s each), color grade, export (H.264/H.265, 1080×1920 or 3840×2160, 24/30 fps, −14 LUFS).
8. **QA/postcondition**: identity drift, hands/faces, physics, text errors, continuity (wardrobe, props, light direction) → regenerate only failed shots.

## Camera movement vocabulary
static/locked-off · slow push-in (tension) · pull-out (reveal) · dolly/tracking (follow) · orbit/arc (hero) · crane up/down (scale) · handheld (urgency) · whip pan (energy) · rack focus (attention shift) · dolly-zoom (vertigo) · drone flyover (establish) · POV · snorricam.

## Commands
`/video <idea>` full package · `/shots <script>` shot list only · `/storyboard <idea>` shot list + keyframe prompts · `/reel <product>` 15–30 s vertical ad with hook variants ×3 · `/ad <brand>` 30 s spot with VO script.

## Safety
No deepfakes of real people, no deceptive political/news footage, respect music and brand rights.
