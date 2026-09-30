# Changelog

## 3.0.0 — 2026-09-30
### Added
- Expert Studio skills: kosif-vision, kosif-image-studio, kosif-lighting, kosif-audio, kosif-code-master, kosif-video.
- Helpers: image_analyze.py, prompt_lint.py, light_calc.py, audio_analyze.py, code_scan.py.
- Core helpers: evidence_consistency_check.py (typed validators), artifact_normalize.py, version_check.py + references/version-compat.json.
- references/expert-studio.md; /help /pro /deep /verify /selftest /versions commands.
- tools/build_zip.py reproducible, validated package build.
### Changed
- pro_receipt_verify.py: trace 3.0, separate `structurally_valid` and `completion_ready`; exit 0 only when completion-ready.
- regression_self_test.py: 17 → 65 cases; optional-library tests are reported as skipped, never passed.
- Manifests: v3.0.0, short description ≤ 30 chars.
### Preserved
- 28-module registry, 14-profile Council, source-taint, capability provenance, dissent ledger, bounded budgets, execution contract, known-answer 92 regression, Ronin-duck regression.
