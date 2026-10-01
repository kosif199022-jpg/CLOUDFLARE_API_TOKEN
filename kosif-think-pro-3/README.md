# KOSIF Think Pro 4 — v4.0.1

v4.0.1 is a reconciliation patch over the already-published v4.0.0 truth-first architecture. It keeps the current request-bound execution, Capability Truth Registry, Council-100, Project Forge, Artifact QA and expert routing, while fixing four concrete truth/consistency bugs found during comparison with the Drive/GitHub corpus.

## Fixed in 4.0.1
- Source Atlas now computes a content SHA-256 when a source hash is absent and gives exact duplicates **one canonical retrieval vote** (`retrieval_weight=1`, copies `0`) while preserving every provenance record.
- Platform adapters now map ChatGPT, Flux, SDXL, Ideogram, Sora and Nano Banana to their own records instead of borrowing Midjourney metadata.
- Version-sensitive exact syntax is separated into `source_syntax_prompt` when provider-current syntax has not been freshly verified; e.g. Midjourney source `--v 7` is no longer presented as current by default.
- Identity verification no longer requires a single output frame to show all five reference views. The reference set must be complete, while each artifact is judged only on traits/views actually observable in that artifact.
- Added a reusable secret-sanitization gate and machine-readable Source Atlas / Capability Truth seed registries.
- Corrected the first default prompt from “KOSIF Think Pro 3” to “KOSIF Think Pro 4”.

## Verification
Run the existing v4.0 tests plus:
```bash
python3 skills/kosif-think-pro/scripts/reconcile_401_self_test.py
```
Source saved/published does not by itself prove a ChatGPT host session has reloaded the new plugin release.
