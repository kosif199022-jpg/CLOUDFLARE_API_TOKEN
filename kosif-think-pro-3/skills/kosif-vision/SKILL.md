---
name: kosif-vision
description: Use whenever the user uploads or references an image and wants it analyzed, described, critiqued, compared, read (OCR), scored, checked for technical quality or AI-generation artifacts, or reverse-engineered into a prompt. Triggers on /analyze /compare /ocr /critique /reverse /score, "حلل الصورة", "قيّم الصورة", "ما مشكلة الصورة".
---
# KOSIF Vision — measured image analysis

KOSIF think-first still applies: frame the user's goal (why they want the analysis: print? social? fix? recreate?) before answering, then separate **measured** facts from **visual judgement** in the output.

## Step 1 — measure (when Python/Code Interpreter is available)
Run `scripts/image_analyze.py IMAGE --summary` (needs Pillow + numpy). It measures: resolution & nearest aspect ratio, EXIF (camera, lens, f-number, shutter, ISO), luminance percentiles, clipped highlights / crushed shadows %, tonal key, estimated color temperature (McCamy CCT), color cast, saturation, colorfulness, 6-color HEX palette, focus-region sharpness, noise σ, luminance-based light direction & ratio, visual centroid vs rule-of-thirds, symmetry.
For two images: `scripts/image_analyze.py A B --compare`.
If Python is unavailable, say so and give a visual-only analysis labelled "estimated".

## Step 2 — /analyze report (use these headings)
1. **الخلاصة** — what the image is, purpose, mood (2 lines).
2. **التكوين** — thirds/centered/symmetry (use measured centroid), leading lines, framing, negative space, eye path.
3. **الكاميرا** — shot type, estimated focal length (perspective compression/distortion), aperture (depth of field), angle; prefer EXIF when present.
4. **الإضاءة** — key direction (clock position), hardness (shadow edge), ratio (measured), color temperature (measured CCT), number of sources, practicals, time of day. Hand off to `kosif-lighting` for a fix plan.
5. **الألوان** — palette HEX (measured), harmony (complementary/analogous/triadic), grade, cast.
6. **العناصر** — subjects, objects, text, wardrobe. Never identify real people from their face; describe only.
7. **الجودة التقنية** — sharpness, noise, exposure, compression artifacts, resolution adequacy for the target use (print 300 ppi / web / reels).
8. **مؤشرات التوليد بالذكاء الاصطناعي** (only if asked) — hands, teeth, text, reflections, earrings asymmetry, repeated textures, impossible geometry. Give a likelihood with reasons, never certainty.
9. **الدرجات /10** — composition, light, color, technical, impact (+ one-line reason each).
10. **الإصلاحات** — 3–5 concrete, ordered fixes (from measured `fixes` + visual review).
11. **برومبت إعادة الإنشاء** — English prompt (KOSIF formula) + negative list, in a code block. Lint it with `../kosif-image-studio/scripts/prompt_lint.py` when available.

## Other commands
- `/compare A B` — table per axis + winner per axis + overall recommendation.
- `/ocr` — transcribe all text exactly (keep Arabic right-to-left order, numbers, punctuation); mark unreadable parts `[؟]`; translate only if asked.
- `/critique` — photographer-style critique: strengths, weaknesses, verdict, one reshoot plan.
- `/reverse` — only the recreation prompt + Style Lock + negative list.
- `/score` — only the scores table + 3 fixes.

## Rules
Measured numbers beat impressions; if they disagree with what you see, say so and explain (e.g. intentional low-key). Heuristic labels (light direction, placement) must be called estimates. Privacy: no face identification, no guessing age/ethnicity/health of real people beyond what is needed for the user's legitimate task.
