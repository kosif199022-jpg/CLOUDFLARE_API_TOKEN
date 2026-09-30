# Prompt Library

## Lenses
14–24mm epic/architecture (distortion near edges) · 28–35mm street/documentary/environmental portrait · 50mm natural perspective · 85mm portrait (f/1.2–f/2 bokeh, flattering compression) · 100mm macro (products, details) · 135–200mm compressed background, isolation · 300mm+ wildlife/sports, stacked layers.

## Shot types & angles
Extreme wide · wide/establishing · full body · medium · medium close-up · close-up · extreme close-up · over-the-shoulder · POV · top-down/flat lay · low angle (power) · high angle (vulnerability) · eye level (neutral) · Dutch angle (unease) · aerial/drone.

## Lighting presets (details in kosif-lighting)
Rembrandt · Butterfly/Paramount · Loop · Split · Clamshell beauty · Broad/Short · High-key white · Low-key black · Cinematic teal-orange · Neon noir magenta/cyan · Golden-hour backlight · Blue hour · Moonlight 7000K · Candle/firelight 1900K · Volumetric god rays · Product rim + gradient · Silhouette · Window light soft side.

## Styles & mediums
Photorealistic (shot on Sony A7R V / Canon R5 / ARRI Alexa 35 / Hasselblad X2D) · Film: Kodak Portra 400, Ektar 100, CineStill 800T, Fuji Velvia · Cinematic anamorphic · Editorial fashion · Luxury commercial · Documentary · Pixar-style 3D · Claymation · Studio Ghibli–inspired watercolor · Anime key visual · Oil painting (impasto) · Ink wash · Isometric 3D · Flat vector · Low-poly · Paper cut · Blueprint · Double exposure · Tilt-shift miniature · Islamic geometric ornament · Arabic calligraphy composition.

## Templates
Portrait: `Hyper-realistic portrait of [person], [expression], [wardrobe], [background], 85mm f/1.4, eye-level, Rembrandt lighting from camera left, shallow depth of field, natural skin texture with pores, catchlights, ultra-detailed, 4:5`
Product: `Luxury commercial photo of [product] on [surface], [props], large softbox key with strip rim lights, crisp controlled reflections, 100mm macro, focus-stacked razor-sharp, seamless [color] gradient background, 1:1`
Food: `Overhead flat lay of [dish] on [surface], soft window light from the left, gentle shadows, steam, garnish details, 50mm, appetizing warm grade, 4:5`
Landscape: `Epic landscape of [place], [time/weather], 16mm wide, strong foreground interest, leading lines, volumetric light, rich dynamic range, ultra-detailed, 16:9`
Architecture: `Architectural photo of [building], two-point perspective corrected, 24mm tilt-shift, blue hour, interior lights glowing, clean lines, 3:2`
Cinematic: `Cinematic still of [Character Lock] [action] in [environment], anamorphic 40mm, [lighting preset], film grain, [grade], depth haze, 2.39:1`
Logo: `Minimal modern logo mark for [brand], [symbol idea], flat vector, [2 colors HEX], balanced negative space, centered on white, no extra text`
Thumbnail: `YouTube thumbnail, [subject] with exaggerated [emotion], high contrast, bold rim light, clean background, space on the right for title, 16:9`

## Platform syntax
- ChatGPT / DALL·E: natural sentences, put constraints first, state aspect ratio in words.
- Midjourney: `prompt --ar 16:9 --style raw --s 150 --v 7`; negatives via `--no text, watermark`; character ref `--cref URL --cw 80`; style ref `--sref URL`.
- Flux: detailed natural language, no negative prompt field (describe what you want); guidance 3–4.
- SDXL: comma-separated tags, weights `(term:1.2)`, separate negative prompt, 1024px base resolutions.
- Ideogram: best for text in images; put exact text in quotes.

## Negative list (describe to avoid)
blurry, low-res, jpeg artifacts, extra fingers, fused fingers, deformed hands, distorted face, crossed eyes, asymmetrical eyes, bad teeth, extra limbs, watermark, signature, text artifacts, oversaturated, plastic skin, waxy skin, duplicate subject, cropped head, tilted horizon, banding.

## Locks
Character Lock: `NAME · age · skin tone · face shape · eyes (color/shape) · brows · nose · lips · hair (color/length/style) · build/height · signature outfit · accessories · distinctive marks · MUST NOT CHANGE: …`
Style Lock: `palette HEX ×5 · lighting preset · lens · grade · texture/grain · era/medium · mood words ×3`
