# Changelog

## 4.0.0 — 2026-10-01 (truth-first reconciliation)
### Added
- Capability Truth Registry, Source Atlas, freshness-aware platform adapters, Artifact QA and multi-view Identity Reference Sets.
- Request-bound authorization/completion and guarded visual execution merged into the Council-100/KCL/Project Forge lineage.
- GitHub CI plus repository hygiene gates; generated Python bytecode removed from the v4 branch.
### Preserved
- Council-100: 100 personas / 10 chambers / 2,000 unique capability descriptors, KCL 36 deterministic probes, Project Forge and Prompt Master 3.4 rules.


## 3.4.0 — 2026-09-30 (Drive books «كتب هامة»)
### Added
- `kosif-prompt-master/references/books-drive-ledger.md`: a note for each file read, a list of the files not yet read, what was adopted and what was rejected.
- prompt_forge: iron-rule warnings, Veo `Audio:` plus dialogue "(no subtitles)" plus last-frame continuity, Runway positive-only, MJ V7 --oref/--sref, Kling Start/End, 3 variations, 5×20% quality rubric.
- Council phase-1 thinker lenses in personality-council.md.
- 5 regression tests, including `forge-no-euphemism-substitution` (the euphemism dictionary in the source app is safety-filter evasion and was rejected).

## 3.3.0 — 2026-09-30 (Council-100, council language, project forge, five new experts)
### Added
- **Council-100**: 100 distinct members in 10 chambers (14 core profiles + 86 specialists), each with a unique specialty,
  12 mastery + 8 programming capabilities (2,000 unique, enforced by `tools/build_council.py`), EN/AR triggers, if-then rule,
  signature question, optional veto domain, 1–3 probes and a forge archetype → `references/council-100.json`.
- **KCL — KOSIF Council Language**: `scripts/kcl_probes.py` (typed messages + 36 deterministic probes) and
  `scripts/council_lang.py` (members, SHA-256-sealed first pass, `run` = select → measure → seal → aggregate).
- `scripts/council_select.py` (standard / pro / full), `scripts/council_aggregate.py` (evidence-weighted; blocking vetoes and
  unresolved material objections cannot be outvoted), `scripts/project_forge.py` (7 archetypes; all 100 members' projects
  generated and their tests passed at release).
- New expert skills: **kosif-prompt-master** (`llm_prompt_lint.py`, `prompt_forge.py`), **kosif-web-design**
  (`web_audit.py`, `design_tokens.py`), **kosif-github** (`gh_preflight.py`), **kosif-computer-use** (`action_gate.py`,
  `ui_ground.py`), **kosif-jev** (`jev_packet.py`).
- Commands: /council /council100 /persona /forge /probe, /prompt /sysprompt /agentprompt /fixprompt /promptscore /abtest,
  /site /landing /ui /dashboard /tokens /webaudit /redesign /component, /gh /commit /pr /review-pr /ci /conflict /release /repo,
  /computer /browse /automate /fillform /scrape, /jev /noul /choose /score /triage /rank.
- Lessons imported from the user's repositories: `think` (action graph, deterministic-rank-then-Jev router, risk gate,
  guardrails — its anti-bot stealth profile deliberately not imported), `cloude` (design tokens with light/dark/auto, validated
  chart palette, Jev-chosen typeface, a11y pass, think-mcp computer routing rule "Jev never grants approval").
- Live Jev observations recorded (jev-1.13.0), including an over-confident pick on an under-specified instruction → new
  under-specification guard in `ui_ground.py`.
### Changed
- `pro_receipt_verify.py`: optional `council` block; `completion_ready` requires `aggregate_verdict: proceed` and verified seals.
- Regression suite 96 → 165 (plugin layout, numpy/Pillow present; audio/vision tests skip honestly when they are absent).
- Manifests and Claude edition 3.3.0; twelve expert skills.

## 3.2.0 — 2026-09-30 (second book batch + Claude edition)
### Added
- inference-and-comprehension.md (Impact 1 reading cycle, Outcomes hedging/picture vocabulary), counterfactual-reasoning.md (Cursed Child case), reasoning-examples.md (10 worked patterns), calibration_check.py.
- Booker's seven plots + Overcoming-the-Monster stages in story_lint; calibrated interpretation in kosif-vision.
- Commands /understand /whatif /calibrate /examples.
- Claude edition: tools/build_claude_skill.py → dist-claude/kosif-think-pro(.skill|.zip), single SKILL.md with references/domains/*, validated with the skill-creator validator; installed at repo .claude/skills/kosif-think-pro.
- Library ledger: second batch (Cursed Child, Impact 1, Outcomes Unit 1, ACM 10 unreadable, Cambridge duplicate).
### Changed
- regression_self_test.py is layout-agnostic (plugin or Claude skill); 84 → 95 (plugin) / 96 (Claude).

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
