# Personality Council — Trait Profiles and Dissent Routing (2.7)

Reasoning profiles are bounded internal lenses, not diagnoses of real people.

## Trait axes
Openness, Conscientiousness, Initiative, Agreeableness/Contrarianism, Emotional Stability, Skepticism, Evidence Threshold, Risk Tolerance, Decisiveness, Divergent Thinking, Persistence, Self-Criticism, Uncertainty Tolerance, Goal Focus, Perspective Taking, Depth-vs-Speed.

## 14 profiles
Skeptic; Strict Verifier; Decisive Operator; Ambitious Optimizer; Creative Explorer; Conservative Risk Guardian; Analytical Decomposer; Adversarial Critic; Naive-Reasoning Simulator; Integrator; Bias Hunter; Constraint Optimizer; Conflict Scout; Evidence Accountant.

## Standard Mode
Select the smallest decision-changing subset, usually 2–6, with context-conditioned trait weights.

## Pro Mode
Run all 14. Freeze first pass independently, then cross-critique, synthesis, Self-Critic and verifier/Jev when applicable. A profile can be `not-material` or `unavailable`, never silently absent.

## Dissent ledger
Every `complete` profile must leave: `profile, conclusion, strongest_objection, evidence_or_assumptions, disposition, what_would_change_it`.
Allowed dispositions: accepted, partially-accepted, rejected, unresolved.
Material unresolved dissent => revise/escalate. Synthesis is evidence-weighted, not majority voting.

Shared fallback models or copied evidence do not establish independent verification.

## Facet grounding and if-then activation (v3.1, Cambridge Handbook ch.9 & ch.27)
The facet vocabulary and the if-then (CAPS) idea come from the handbook; the mapping of facets to KOSIF profiles is our design adaptation. Each profile is a reasoning lens defined by a Five-Factor facet emphasis plus *if … then …* activation rules (behavioural signatures depend on situation class). These are internal lenses only.

| Profile | Facet emphasis (NEO-PI-R) | If … then … activation |
|---|---|---|
| Skeptic | low A1 trust, high C6 deliberation | if a claim lacks a traceable source → demand evidence before use |
| Strict Verifier | high C2 order, C3 dutifulness | if numbers/contracts are involved → recompute and check postconditions |
| Decisive Operator | high E3 assertiveness, E4 activity | if options are adequate and reversible → recommend acting now |
| Ambitious Optimizer | high C4 achievement striving, O4 actions | if a baseline plan exists → ask what would make it 2× better |
| Creative Explorer | high O5 ideas, O1 fantasy | if options look homogeneous → run /ideate for structurally different ones |
| Conservative Risk Guardian | high N1 anxiety (vigilance), low E5 excitement seeking | if an action is irreversible or high-stakes → require pilot/rollback |
| Analytical Decomposer | high C6 deliberation, O5 ideas | if the problem is compound → split into sub-problems and interfaces |
| Adversarial Critic | low A4 compliance, high A2 straightforwardness | if consensus forms quickly → attack the strongest conclusion |
| Naive-Reasoning Simulator | high O6 values openness, low expertise assumption | if jargon or hidden assumptions appear → ask the naive "why?" |
| Integrator | high A3 altruism, E1 warmth, O5 ideas | if profiles disagree → build a synthesis that preserves valid parts |
| Bias Hunter | high C6 deliberation, low A1 trust in intuition | if an estimate, ranking or probability is given → run bias-firewall + probability_coherence |
| Constraint Optimizer | high C2 order, C5 self-discipline | if resources/limits exist → run decision_sensitivity with firm constraints |
| Conflict Scout | high A6 tender-mindedness (stakeholder empathy), N4 self-consciousness (social threat awareness) | if people, incentives or power are involved → run the conflict pre-mortem |
| Evidence Accountant | high C1 competence, C3 dutifulness | if a conclusion is drafted → map every claim to evidence status |

Standard Mode activates only the profiles whose *if* condition is met; Pro Mode runs all 14 regardless and records `not-material` where the condition is absent.

## Council-100 — 100 distinct expert members (v3.3)
The 14 profiles above remain the **core** (they are what Pro receipts require). v3.3 adds 86 specialists so the council has **100 members in 10 chambers of 10**:

| Chamber | Members (core in bold) |
|---|---|
| evidence — الأدلة والتحقق | **Skeptic**, **Strict Verifier**, **Evidence Accountant**, **Bias Hunter**, Fact Checker, Statistician, Source Auditor, Replication Tester, Measurement Scientist, Logician |
| strategy — الاستراتيجية والقرار | **Decisive Operator**, **Ambitious Optimizer**, **Constraint Optimizer**, Strategist, Game Theorist, Economist, Portfolio Manager, Scenario Planner, Opportunity-Cost Analyst, Long-Term Steward |
| risk — المخاطر والأمان | **Conservative Risk Guardian**, **Adversarial Critic**, Security Red-Teamer, Privacy Guardian, Safety Engineer, Compliance Officer, Legal Reviewer, Reliability Engineer, Fraud Examiner, Pre-Mortem Pessimist |
| creativity — الإبداع والأفكار | **Creative Explorer**, Lateral Thinker, Provocateur, Analogist, Storyteller, Poet-Lyricist, Brand Strategist, Humorist, Futurist, Minimalist Editor |
| human — الإنسان والمجتمع | **Conflict Scout**, **Naive-Reasoning Simulator**, **Integrator**, User Advocate, Negotiator, Ethicist, Cultural Advisor, Teacher, Mediator, Arabic Language Editor |
| engineering — الهندسة والبرمجة | **Analytical Decomposer**, Software Architect, Code Reviewer, Test Engineer, Performance Engineer, Release Engineer, Data Engineer, API Designer, Debugger, Maintainability Advocate |
| design — التصميم والتجربة | UX Researcher, UI Visual Designer, Accessibility Advocate, Typographer, Color Scientist, Motion Designer, Information Architect, Conversion Specialist, Mobile-First Designer, Design-System Keeper |
| media — الإنتاج البصري والإعلامي | Cinematographer, Lighting Director, Photographer, Art Director, Prompt Engineer, Video Editor, Sound Designer, Music Producer, Continuity Supervisor, Character Designer |
| business — المال والمراجعة والأعمال | External Auditor, IFRS Specialist, VAT Advisor, Controller, CFO, Forensic Accountant, Marketer, Sales Lead, Operations Manager, Procurement Specialist |
| operations — الأتمتة والوكلاء والأدوات | GitHub Maintainer, Computer-Use Operator, Automation Engineer, Jev Arbiter, Tool Provenance Auditor, Budget Controller, Incident Commander, Idempotency Guardian, Postcondition Verifier, Human-Checkpoint Guardian |

### Each member carries
`id · name / name_ar · chamber · facets · triggers (EN + AR) · if_then · question · veto · specialty · mastery[12] · code[8] · probes[1–3] · forge` — see `council-100.json`. The build (`tools/build_council.py`) fails unless all 100 specialties and all 2,000 capabilities are unique (normalised text, no near-duplicates at token Jaccard ≥ 0.8), every probe exists and every forge archetype exists. "No repetition" is therefore a tested property, not a promise.

### The council language (KCL, `scripts/council_lang.py` + `scripts/kcl_probes.py`)
Typed Python 3.10+ messages: `Evidence(source, content, measured, data)`, `Objection(text, severity, veto)`, `Artifact(persona, stance, confidence, question, claims, evidence, objections, probes_run)`; enums `Stance` and `Severity`. Type rules enforced at construction: confidence ∈ [0, 1]; a member cannot `support` while raising a `blocking` objection. A member whose probes received no input answers `not-material` (never an invented number). First-pass artifacts are sealed (SHA-256 of canonical JSON) in a read-only ledger; a second first pass raises an error; `verify()` detects tampering. The wire format is plain JSON accepted by `council_aggregate.py`.

### Protocol
1. `council_select.py` → members (standard 3–12 · pro 14 core + up to 16 triggered specialists + every triggered veto holder · full 100). Design work always adds the Accessibility Advocate; optimiser/operator voices are balanced by a risk voice and vice versa.
2. Collect measurable inputs for the selected members' probes (colours, code, diffs, cash flows, dates, commands, page text …) and run `council_lang.py run` — or, when writing positions by hand, one Artifact per member in the same schema.
3. Freeze (seal) first-pass artifacts; then cross-critique in prose.
4. `council_aggregate.py`: evidence-weighted support (confidence × evidence factor), blocking vetoes ⇒ `escalate`, unresolved material objections ⇒ `revise`, otherwise `proceed`.
5. Report: verdict, blocking vetoes, surviving dissent, measured evidence, and the independence note.

### `/council100` output format
One line per member, grouped by chamber: `name_ar — stance — strongest point or objection — evidence (measured/observed/none)`. Members with nothing material say `not-material` in one word. Close with the aggregate verdict and surviving dissent. Keep it compact; 100 members do not justify 100 paragraphs.

### Build alone (`scripts/project_forge.py`)
Any member can scaffold a complete project in its archetype, with its probes vendored and wired in, tests that pass on generation (the forge runs them and reports the real result), CI, architecture doc, ADR, SECURITY.md and a milestone roadmap built from its 8 programming capabilities. The project then grows milestone by milestone, test-first. All 100 members' default projects were generated and tested at release time.

## Phase-1 thinker lenses (v3.4, from the user's «مجلس» app)
Before members measure, ask up to six lens questions and keep only the ones that change the plan: higher dimensions (what view is missing?), forces (what pushes and resists?), contradictions (which two requirements conflict?), unconscious patterns (what habit or bias shapes the request?), algorithm (what repeatable procedure solves it?), timescales (what happens in the first second vs the first year?). Then activate chambers by request type, and close each active chamber with a QA check and an archivist note. Claimed counts are not evidence: that app claimed 500+ experts while its data held 138.
