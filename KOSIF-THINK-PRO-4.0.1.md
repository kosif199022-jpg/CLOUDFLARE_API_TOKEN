# KOSIF Think Pro 4.0.1 — Truth-First Reconciliation

This branch starts from Claude's 3.4.0 branch and layers the currently published ChatGPT plugin v4.0.1 source over the legacy `kosif-think-pro-3/` directory without renaming it, to preserve history.

Key v4 additions: Capability Truth Registry, Source Atlas with canonical duplicate retrieval weights, adaptive Council-100, Project Forge 4, version/freshness-aware platform adapters, Prompt Forge, Identity Reference Set, Artifact QA, Secret Sanitization, and host-aware GitHub/Computer/Web/Jev skills.

v4.0.1 specifically fixes:
- exact duplicate records now get one canonical retrieval vote;
- platform adapters no longer borrow Midjourney provenance for unrelated platforms;
- unverified version-specific syntax is separated from the current compiled prompt;
- a single generated frame is not required to show all five 360° reference views;
- stale “KOSIF Think Pro 3” wording in the v4 manifest was corrected.

Published plugin: https://chatgpt.com/plugins/plugins_6abd29b907ac8191a457bce773dc7515
Source release: pluginrel_6abdd5102e848191b1239f27f3a3c86c
