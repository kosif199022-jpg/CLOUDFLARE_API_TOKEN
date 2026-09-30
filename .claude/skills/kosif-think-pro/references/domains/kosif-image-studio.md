# KOSIF Image Studio — ultra-detailed generation with contract binding

## Pipeline (every image)
1. **Frame** the goal: use (post, print, ad, thumbnail), audience, must-have elements, forbidden elements, text on image, aspect ratio.
2. **Freeze an Execution Contract** (see `references/execution-binding.md`): `required`, `forbidden`, `allowed_flexibility`, `success_criteria`.
3. **Build the prompt** (English) with the formula:
   `[Subject + precise details] + [Action/pose/expression] + [Environment + time] + [Camera: shot, angle] + [Lens: mm, aperture] + [Lighting: direction, quality, color temp — use kosif-lighting presets] + [Color palette/grade] + [Style/medium/film stock] + [Quality boosters] + [Aspect ratio]`
   Quality boosters: ultra-detailed, razor-sharp focus, micro-details, natural skin texture with pores, accurate anatomy, correct hands with five fingers, physically-based lighting.
4. **Lint** (when Python is available): pipe `{"prompt", "contract", "locks"}` to `scripts/prompt_lint.py`. BLOCK ⇒ fix before generating. REVISE ⇒ improve missing parts.
5. **Generate** with the host image tool (only if actually exposed; otherwise deliver the prompt and say generation is unavailable).
6. **Postcondition check**: inspect the result against the contract + anatomy (hands, eyes, teeth), text spelling, perspective, lighting consistency. Mismatch ⇒ FAILED-DRIFT ⇒ regenerate or edit; never call a drifted image "done". Optionally measure with `scripts/image_analyze.py`.
7. **Deliver**: image + final prompt in a code block + 2 variation ideas (different light / angle / lens).

## Commands
- `/img <idea>` — full pipeline, one image.
- `/imgpro <idea>` — show 3 structurally different prompt options (A/B/C: e.g. cinematic / editorial / illustrative) with a one-line rationale; generate the chosen one.
- `/edit` — edit uploaded/last image; state what must stay identical (identity, composition, colors) and change only the requested part.
- `/prompt <idea> [midjourney|flux|sdxl|dalle|ideogram]` — prompts only, adapted to the platform (see `references/kosif-image-studio/prompt-library.md` for syntax).
- `/style <image>` — extract a reusable **Style Lock** (palette HEX, lighting, lens, grade, texture, era) using kosif-vision measurements.
- `/lock <character>` — create a **Character Lock** + **Personality Lock** (facets, visible cues, if-then signatures from `references/kosif-image-studio/character-psychology.md`) and reuse them verbatim in every later prompt (the linter checks it).
- `/batch <idea> <n>` — n consistent images (same locks, varied pose/angle), e.g. storyboards, carousels.

## Text on images
Only when asked; short, exact spelling in quotes. Arabic text often renders imperfectly: warn and offer to add it as a separate layer/overlay (give font suggestion: IBM Plex Sans Arabic / Cairo / Tajawal).

## Safety
No sexual content, no minors in any suggestive context, no photoreal fakes of real people or public figures in deceptive contexts, no trademark/logo counterfeits, no copyrighted characters for commercial use. Offer an original alternative.

Cross-platform translation of one spec into Midjourney/Flux/SDXL/DALL·E/Ideogram/video syntax: `/forge` in `references/domains/kosif-prompt-master.md` (`scripts/prompt_forge.py`).

References: `references/kosif-image-studio/prompt-library.md` (lenses, lighting, styles, templates, platform syntax, negatives).
