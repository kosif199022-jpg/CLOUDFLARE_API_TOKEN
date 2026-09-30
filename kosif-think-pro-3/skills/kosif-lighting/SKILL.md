---
name: kosif-lighting
description: Use for any lighting question or task — photo, film, video, product, portrait, interior or 3D lighting; diagnosing bad light in an image; relighting; lighting plans and diagrams; gear, gels, exposure and camera settings; lighting words for image/video prompts. Triggers on /light /relight /lightplan /exposure /gel, "إضاءة", "ظل", "الضوء", "lighting".
---
# KOSIF Lighting Director

## Physics & numbers (compute, do not guess)
Use `scripts/light_calc.py` (JSON on stdin) whenever numbers matter:
`inverse_square` (distance → stops) · `ev` (aperture/shutter/ISO → EV100 + typical scene) · `equivalent` (reciprocal exposure) · `ratio` / `ratio_to_stops` (lighting ratio) · `mired` (Kelvin shift → CTO/CTB gel) · `guide_number` (flash f-number) · `softness` (source size/distance → apparent angle) · `shutter_angle` (fps + angle → shutter) · `falloff` (background darkening).

Core rules: bigger/closer source ⇒ softer shadows; doubling distance ⇒ −2 stops; ratios 2:1 commercial · 3:1 natural portrait · 4–8:1 dramatic · 8:1+ noir. Color temperature: candle 1900K · tungsten 3200K · golden hour ~3500K · daylight 5600K · overcast 6500K · shade 7500K+. Direction: front (flat) · 45° loop/Rembrandt · 90° split · back/rim (separation) · top butterfly · under (horror). Modifiers: softbox, octa, stripbox, umbrella (shoot-through/reflective), beauty dish, fresnel, grid, snoot, barn doors, flags, diffusion (1/4–full), bounce (white/silver/gold), negative fill.

## /lightplan <scene>
Deliver:
1. Mood & story goal (one line).
2. Top-view diagram (ASCII): camera at bottom, subject center, each light with angle and distance.
3. Table per light: role (key/fill/rim/hair/background/practical) · fixture · modifier · power/stops · height · angle · distance · color temp/gel.
4. Ratios & exposure: computed with light_calc (show the numbers).
5. Camera: ISO, shutter (or shutter angle), aperture, white balance.
6. Budget version: window + lamp + white foam board + phone light.
7. Common mistakes for this setup.
8. English prompt fragment reproducing the look (for kosif-image-studio / kosif-video).

## /light (uploaded image)
Run `../kosif-vision/scripts/image_analyze.py IMAGE --summary` when available, then: what the light is (direction, hardness, ratio, temperature), what's wrong (with the measured evidence), exact fix on set and in post (curves, dodge/burn, WB shift, relight mask).

## /relight <image> <mood>
Describe the target setup (preset + numbers), then edit/regenerate keeping subject identity, pose and composition frozen in an Execution Contract; verify the postcondition (identity unchanged, new light direction visible).

## /exposure and /gel
Quick answers via light_calc: equivalent exposures, ND needed, gel to match sources (e.g. tungsten lamp in daylight room ⇒ Full CTB on lamp or Full CTO on window).

## Presets
See `references/lighting-presets.md` (18 presets with diagrams, ratios, and prompt fragments).
