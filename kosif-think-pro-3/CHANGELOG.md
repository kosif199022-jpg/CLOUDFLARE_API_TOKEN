# Changelog

## 4.0.1 — 2026-10-01
### Fixed
- Exact duplicate records now collapse **retrieval weight**, not just appear in a duplicate report.
- Missing SHA-256 values are deterministically computed from source text for atlas use.
- Platform adapter misrouting for ChatGPT/Flux/SDXL/Ideogram/Sora/Nano Banana.
- Unverified Midjourney version flags are retained only as source syntax, not asserted as current compiled syntax.
- Per-artifact identity checks no longer require all five 360° reference views to be visible in one frame.
- Stale “KOSIF Think Pro 3” wording in the v4 manifest default prompt.
### Added
- `secret_sanitize.py` reusable import/publish gate.
- Machine-readable `v4-source-atlas.seed.json` and `v4-capability-registry.seed.json`.
- `reconciliation-4.0.1.md` and deterministic `reconcile_401_self_test.py`.

## 4.0.0 — 2026-10-01
- Capability Truth Registry, Source Atlas, adaptive Council-100, Project Forge 4, freshness-aware Prompt Forge, Identity Reference Set, Artifact QA and five host-aware expert skills.
