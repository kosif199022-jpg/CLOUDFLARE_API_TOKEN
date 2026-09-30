# Expert Studio — v3.0

The expert skills are domain protocols that run **after** KOSIF framing and **inside** the same guarantees: Execution Contract before any generator/executor, observable postcondition after it, truthful capability provenance, and no claim that a tool ran unless it did.

## Shared rules
1. Measure before judging: run the skill's helper script when Python/Code Interpreter is exposed. Report measured values separately from visual/aural judgement.
2. Generators (image, video, audio, code execution) are executors: freeze the contract (required / forbidden / flexibility / success criteria), lint the brief, execute, then verify the artifact. A visibly wrong artifact is `failed-drift`, not success.
3. Locks (Character, Style, Location) are verbatim contract terms; `prompt_lint.py` checks them.
4. When a host capability is not exposed (image generation, audio synthesis, Python), say so, deliver the best non-executed artifact (prompt, script, plan) and mark it `not-executed`.
5. Arabic in, Arabic out for explanations; English for prompts, code and technical parameters.
6. Safety: no face identification, no deceptive real-person media, no secrets in code, no copyrighted characters/brands for commercial output.

## Cross-skill combos
- Photo fix: vision (measure) → lighting (diagnose) → image-studio (/edit or /relight) → vision (verify improvement numerically).
- Product ad: image-studio (product shots, Style Lock) → video (shot list) → audio (VO + music BPM) → lighting (product rim preset).
- Song + clip: audio (/song, BPM) → video (cuts on beats) → image-studio (keyframes).
- App build: code-master (/arch → /code → /test) → code_scan → deploy.

## Helper scripts
| Script | Input | Verdict |
|---|---|---|
| `kosif-vision/scripts/image_analyze.py` | image path(s) | measured report + fixes |
| `kosif-image-studio/scripts/prompt_lint.py` | JSON prompt/contract/locks | PASS / REVISE / BLOCK |
| `kosif-lighting/scripts/light_calc.py` | JSON op(s) | numbers |
| `kosif-audio/scripts/audio_analyze.py` | audio path | measured report + fixes |
| `kosif-code-master/scripts/code_scan.py` | files / folder / .zip | findings + score |
