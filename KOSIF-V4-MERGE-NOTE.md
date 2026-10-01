# v4 merge note

The 3.4 implementations of Project Forge, Prompt Forge, Web Audit, GitHub preflight, Computer action gate and Jev packet are intentionally preserved on this branch.

The compact ChatGPT-plugin v4 truth/freshness implementations that were initially synchronized are retained only as sidecars:
- `skills/kosif-prompt-master/scripts/prompt_forge_v4_truth.py`
- `skills/kosif-think-pro/scripts/project_forge_v4_truth.py`

The next merge step is feature composition: keep the richer 3.4 behavior and add v4 Capability Truth / Source Atlas / freshness / identity / artifact QA invariants around it. Do not replace the richer implementations with the sidecars.
