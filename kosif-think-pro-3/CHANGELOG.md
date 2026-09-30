# Changelog

## 3.1.0 — 2026-09-30 (library reading pass)
### Added
- references/books/: library index + per-book analysis for all 18 Drive files (coverage, contamination test, status, transfer).
- kosif-audit-ifrs skill: ledger_check.py, standards-controls, CAM template, filing-source registry, Arabic IFRS terms, DipIFR practice map.
- kosif-video: story-conflict.md + story_lint.py (GMC+S, six central conflicts, four levels, agency, escalation, 80/20).
- kosif-image-studio: character-psychology.md (FFM 30 facets, visible cues, CAPS if-then signatures, SDT) → Personality Lock.
- kosif-code-master: pragmatic-principles.md (70 tips grouped, checklists, /ml methodology, optimisation ladder, SICP notes); /design-review, /ml.
- kosif-think-pro: bias-firewall.md, ideate.py, decision_sensitivity.py, probability_coherence.py; /ideate /decide /bias /library; facet-grounded Personality Council.
### Changed
- book-source-ledger.md corrected: Judgment → TOC-only advertisement; Convex → ch.1 only; Designing Bots → contaminated confirmed; coverage notes for Code Complete, Deep Learning.
- Regression suite 65 → 84; manifests 3.1.0.

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
