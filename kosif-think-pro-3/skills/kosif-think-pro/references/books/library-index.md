# KOSIF Library — reading pass 2026-09-30 (v3.1)

Drive folder «كتب» (18 files, 17 unique). Every file was fetched and checked: text extraction method, page/char coverage, and a contamination test (on-topic keyword density per page + visual sampling of beginning/middle/end). A filename is never treated as proof of reading.

| # | Book (file) | Read in this pass | Status | Transferred into |
|---|---|---|---|---|
| 1 | The Pragmatic Programmer | full PDF, 352 pp, 616k chars; 320 pp clean | **adopted** | kosif-code-master `pragmatic-principles.md`; execution contracts; regression discipline |
| 2 | The Conflict Thesaurus (vol. 2) | full PDF, 715 pp, 719k chars; 521 pp on-topic | **adopted** (fiction craft) | kosif-video `story-conflict.md` + `story_lint.py`; pre-mortem taxonomy |
| 3 | Cambridge Handbook of Personality Psychology | full PDF, 906 pp, 2.6M chars; 733 pp on-topic | **adopted** | Personality Council facets + if-then signatures; `character-psychology.md` |
| 4 | Lateral Thinking Course | full PDF, 100 pp | **adopted with limits** (self-help; neuroscience claims = rhetoric) | `/ideate` + `ideate.py` |
| 5 | AI-Powered Accounting Skill (IFRS/ISA report) | full text, 16 pp | **adopted** (applied design report) | kosif-audit-ifrs + `ledger_check.py` + `standards-controls.md` |
| 6 | Smart Thinking (Greetham) | partial: intro → ch.4 (≈65 of 310 pp) + full TOC | **adopted, partial** | Bias Firewall (`bias-firewall.md`), `probability_coherence.py`, concept framing |
| 7 | Deep Learning (Goodfellow et al.) | partial: TOC + pp.1–50 | **partial** (TOC-level for later chapters) | ML methodology checklist (ch.11 structure) in code-master; evaluation harness |
| 8 | Convex Optimization (Boyd) | ch.1 only clean (27 of 205 pp); pp.28+ are unrelated fiction | **mixed** — ch.1 only | `decision_sensitivity.py`; formulation ladder |
| 9 | Global Financial & Audit Research Bundle | partial (301k of ≈29 MB): source registry + Apple/Amazon report excerpts + auditor's CAM | **adopted, partial** | `filing-sources.md`, `cam-template.md` |
| 10 | Dip IFRS Kit 2025 (BPP) | partial, OCR-noisy | **training material** | `dipifr-syllabus.md`, `/practice` |
| 11 | IFRS in Arabic 2018 (SOCPA) | partial; text layer reversed, recovered | **historical/terminology** | `arabic-terms.md` |
| 12 | SICP (file) | full, but it is a study guide, not the textbook | **secondary** | abstraction/dispatch notes in code-master |
| 13 | Judgment in Managerial Decision Making | 208 pp, only the TOC page is real; the rest is random multilingual filler | **advertisement/TOC-only** (downgraded) | chapter names only → bias checklist headings |
| 14 | Designing Bots (Shevat) | ≈12 front-matter pages real; rest unrelated filler | **contaminated** | nothing substantive |
| 15 | Probability Theory: The Logic of Science (testbank) | advertisement pages | **quarantined** | nothing |
| 16 | Code Complete | connector returned empty text (160 MB file) | **unreadable this pass** | prior 2.7 mapping kept, no new claims |
| 17 | Aristotle, Organon | empty text (92 MB scan) | **unreadable** | nothing |
| 18 | ابن سينا — الشفاء، المنطق ج1 | 714 image-only pages (34 MB), no text layer | **unreadable without OCR** | nothing |
| — | Smart Thinking (second copy) | identical size to #6 | **duplicate** | — |

## Honest limits
- Files larger than ≈5 MB could not be downloaded whole through the Drive connector (session expired); for those, only the connector's text extract was available (partial).
- Transfers are written in our own words as operating rules; they do not copy the books. Short titles/headings are cited for traceability.
- Reading books changes instructions and helper scripts only — not model weights.

## To complete coverage (next passes)
1. Upload smaller split PDFs (≤5 MB) of Code Complete, Deep Learning, Smart Thinking, Dip IFRS, IFRS Arabic, the audit bundle.
2. Replace the advertisement/contaminated files (Judgment, Designing Bots, Jaynes) with clean copies.
3. Provide a text-layer (OCR) version of Ibn Sina and the Organon, or allow page-image reading in small batches.
