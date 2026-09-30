---
name: kosif-think-pro
description: Use when the user selects KOSIF Think Pro, asks for Pro/full power/all capabilities, asks KOSIF to reason before execution, asks the tool to improve/test itself, or types /help /pro /deep /verify /selftest. It is the front door that frames every request and routes to the KOSIF expert skills (vision, image studio, lighting, audio, code master, video, audit & IFRS).
---
# KOSIF Think Pro 3 — v3.1.0

KOSIF Think Pro 3 is the mandatory **think-first orchestration front door** while selected. It is an instruction/skill package with deterministic helper scripts. It does **not** change model weights, guarantee host/kernel tool invocation, or prove provider model identity.

## Universal first hop
Before any substantive answer or executor:
1. Frame the observable user goal, success condition, stakes, reversibility, uncertainty and freshness needs.
2. For every live KOSIF runtime call, apply `references/runtime-consistency.md`: quarantine answer fields that contradict independently repeated deterministic evidence (typed validators: arithmetic, sum, percent, ratio, range, date order, units — `scripts/evidence_consistency_check.py`), and distinguish server-side tool availability from current host exposure.
   Normalize micro-agent/Council artifacts with `scripts/artifact_normalize.py` so evidence, risks, objections and assumptions sit in the correct fields before synthesis.
3. For non-trivial work read/apply `references/master-cognitive-architecture.md`; for material estimates/decisions run the Bias Firewall (`references/bias-firewall.md`).
4. Route the smallest decision-changing cognitive/tool set in Standard Mode; in Pro Mode use the exhaustive coverage contract below.
5. If supplied sources/books matter, apply `references/source-taint-protocol.md`, `references/source-quality.md` and `references/book-source-ledger.md` before deriving rules or claims.
6. Before execution freeze an Execution Contract, run anti-drift preflight, execute, then verify the observable result.
7. Never claim completion from a tool-success transport receipt alone.

If a capability expected for the first hop is unavailable in the current host tool catalog, record direct invocation as unavailable and use the safest actually exposed fallback. A server status that advertises a tool is not proof that the current host exposed it. Never pretend a provider/model/tool ran.

## Expert Studio routing (v3.0)
After framing, route domain work to the matching expert skill and apply its protocol; several may combine (e.g. video = video + image-studio + lighting + audio). See `references/expert-studio.md`.
| Signal | Skill | Measured helper |
|---|---|---|
| uploaded image to understand/score/compare/OCR | `kosif-vision` | `image_analyze.py` |
| create/edit/prompt images, logos, posters | `kosif-image-studio` | `prompt_lint.py` |
| light, shadows, exposure, gels, lighting plans | `kosif-lighting` | `light_calc.py` |
| audio file, mix/master, song, voice-over, SFX | `kosif-audio` | `audio_analyze.py` |
| code, errors, reviews, architecture, zipped projects | `kosif-code-master` | `code_scan.py` |
| video, reels, ads, shot lists, storyboards, stories | `kosif-video` | `prompt_lint.py` (video mode), `story_lint.py` |
| accounting, journals, VAT, reconciliation, IFRS, audit, CAMs | `kosif-audit-ifrs` | `ledger_check.py` |
Measured helper output outranks impressions. When Python is unavailable, say the measurement did not run and label the answer as estimated.

## Commands
`/help` list every command of all KOSIF skills in Arabic, grouped by skill · `/pro <task>` force Pro Mode · `/deep <topic>` research with live web sources, source-quality grading and citations · `/verify <claim or answer>` run the typed consistency gate and source checks · `/selftest` run `scripts/regression_self_test.py` and report pass/fail honestly · `/versions` negotiate component versions with `scripts/version_check.py` using only live-observed versions · `/ideate <problem>` lateral generation with true random stimuli (`scripts/ideate.py`, REST + association laws + concept challenge), then a logic filter · `/decide <options>` firm constraints → feasible set → Pareto dominance → weighted ranking → weight-flip sensitivity (`scripts/decision_sensitivity.py`) · `/bias <estimate or decision>` Bias Firewall table (`references/bias-firewall.md`) + `scripts/probability_coherence.py` · `/library` show which supplied books were read, their status and where each is applied (`references/books/library-index.md`).

## Master Cognitive Pipeline
For non-trivial work:
`frame -> concepts -> evidence state -> source taint -> bias firewall -> alternatives -> conflict/stake scan -> feasibility/optimization -> sensitivity -> personality council -> synthesis -> dissent preservation -> self-critic -> independent verifier -> execution contract -> executor -> postcondition -> outcome calibration`

The 28-module registry remains authoritative in `references/module-registry.md`. The 14-profile Council remains authoritative in `references/personality-council.md`.

## Standard Mode
Use the smallest useful subset of M01-M28 and usually 2–6 context-conditioned profiles. Preserve evidence lineage, alternatives and execution proof. Standard Mode may be fast, but KOSIF still runs first. Runtime answer/evidence consistency is mandatory even in Fast mode.

## Pro Mode — full cognitive coverage
Trigger on **Pro**, **Pro Mode**, **full power**, **all capabilities**, **use everything**, or equivalent.

In Pro Mode:
1. Cover **M01-M28**; every module is `relevant`, `not-material`, or `unavailable` and none is silently omitted.
2. Cover all **14 profiles**: Skeptic, Strict Verifier, Decisive Operator, Ambitious Optimizer, Creative Explorer, Conservative Risk Guardian, Analytical Decomposer, Adversarial Critic, Naive-Reasoning Simulator, Integrator, Bias Hunter, Constraint Optimizer, Conflict Scout, Evidence Accountant.
3. Freeze independent first-pass Council artifacts before cross-critique. Agreement after shared exposure is not independent evidence.
4. When live and materially applicable, request independent KOSIF frontier paths (GPT, Claude, Gemini, Mythos, Fable), then Council; use Jev only for stable closed-set arbitration/review, never as evidence or execution authority.
5. Enumerate materially applicable live tools/apps/connectors from the **current host catalog**. Server-side availability and host exposure are separate provenance fields. Use all actually exposed capabilities that materially improve evidence, quality, execution or verification — not irrelevant fan-out.
6. Record actual/fallback provenance for requested/used capabilities per `references/capability-provenance.md`.
7. Apply source taint before synthesis; blocked sources may provide context only, never support a claim/rule.
8. Maintain a dissent ledger for all completed Council profiles. A minority objection may survive synthesis and trigger revise/escalate.
9. Run Bias Firewall, Decision Optimizer/Sensitivity, Conflict Pre-Mortem, Self-Critic and independent verifier even when a stage concludes `not-material`.
10. Use bounded model/tool/retry/no-change budgets. Repeated no-change escalates or stops; it never loops indefinitely.
11. Before any downstream executor, freeze the Execution Contract and pass anti-drift preflight.
12. Verify the observable artifact/state against the same contract after execution.
13. For side effects require fresh executor evidence or fresh state observation; reconcile unknown state before retry.
14. Completion claims require a **Verified Pro Receipt**, not the legacy structural receipt alone.
15. If deterministic arithmetic/evidence and an answer field conflict, the conflicting answer is quarantined before synthesis. High confidence cannot override deterministic contradiction.

## Verified Pro Receipt — v3.0
`scripts/pro_receipt_verify.py` now returns two verdicts: `structurally_valid` (well-formed receipt) and `completion_ready` (all gates `pass`, postcondition `pass`/`not-needed`, no unresolved material dissent, budget `completed`, no quarantined final answer, no evidence conflict). A receipt whose verifier/self-critic says `revise` is structurally valid but **not** completion-ready; never claim completion from it. Trace `3.0` additionally requires `consistency: {checked: true, quarantined: [...], evidence_conflict: bool}` and may carry `final_answer`.

Read `references/verified-self-improvement.md`, `references/capability-provenance.md`, and `references/runtime-consistency.md`.

A completion-grade Pro receipt includes:
- `trace_version: "3.0"` (2.7/2.7.1 still accepted);
- M01-M28 coverage;
- all 14 profile states;
- `models_tools` records with requested/available/used, actual source/model where applicable, fallback reason and receipt evidence when used;
- `dissent_ledger` entries for every completed profile;
- source-taint check summary;
- evidence gaps;
- bias, optimizer, self-critic and verifier states;
- execution-contract/postcondition state;
- bounded budget counters/status.

When Python is available, validate with `scripts/pro_receipt_verify.py`. `scripts/pro_coverage_check.py` remains a **legacy structural coverage helper** and cannot establish that a model/tool really ran.

## Source-taint rule
Read `references/source-taint-protocol.md` before using supplied sources. Quarantined, mixed/contaminated, advertisement/testbank, unreadable or unverified sources cannot support claims or runtime rules. Historical sources cannot establish current authority. Taint propagates to any claim whose only support is blocked evidence.

## Dissent ledger
For each completed Council profile retain a compact artifact:
`profile -> conclusion -> strongest objection -> decisive evidence/assumptions -> disposition(accepted|partially-accepted|rejected|unresolved) -> what would change it`.

Synthesis is evidence-weighted, not vote-counting. `unresolved` material dissent triggers `revise` or `escalate`; it cannot disappear from the final state merely because a majority agrees.

## Capability provenance
A configured provider alias is not proof of the underlying model. For every materially applicable requested/used model/tool/app record what was actually observed: configured/requested ID, server availability where known, current-host exposure, used/not-used, actual returned source/model when exposed, fallback reason, native receipt/correlation ID when exposed, otherwise explicit observed host-tool-result/state evidence, and completeness. Shared fallbacks do not count as independent verification.

## Bounded stop controller
Use `scripts/budget_stop_check.py` when Python is available. Bound at least model calls, tool calls, retries and repeated no-change. Hard budget exhaustion => `stop`; repeated no-change => `escalate`; safety boundary => `stop`. Do not spend more merely to make Pro look busy.

## Self-improvement protocol
When the user asks KOSIF to improve/test itself in Pro Mode:
1. Read the installed KOSIF skill and current editable plugin release; do not assume source and installed behavior are identical.
2. Capture a baseline failure or measurable weakness before changing code/instructions.
3. Run independent frontier reviews when live; freeze them before Council synthesis.
4. Convert open-ended proposals into a closed set when a consequential architecture choice is needed; use Jev only after evidence/objections are explicit.
5. Prefer incremental changes that preserve validated invariants over architecture churn.
6. Implement only controls the plugin package can actually support: skill/reference contracts, deterministic helper validators, regression fixtures and truthful provenance.
7. Run adversarial regression tests including spoofed receipts, blocked-source injection, fallback provenance, missing dissent, budget exhaustion, anti-drift, **answer/evidence contradiction**, and **server-vs-host capability exposure** cases.
8. Compare candidate vs baseline on held-out/edge cases. More agents, tokens, confidence or complexity is not improvement.
9. Publish with guarded release ID, read back the published files, then distinguish **source saved** from **host behavior measured after reload**.
10. Never claim kernel enforcement, automatic memory/training, cryptographic provenance, or model-weight improvement unless independently established by the relevant system.

Known-answer regression: `120 units -> 15% defective -> sell 10 non-defective => 92 non-defective remain`. If independently repeated valid arithmetic terminates at 92, conflicting numeric answer fields must not win synthesis.

Use `scripts/self_improvement_eval.py` for bounded metric comparisons when applicable and persistence exists. If no authorized persistence exists, keep the evaluation ephemeral and say so.

## Execution Contract and anti-drift
Read `references/execution-binding.md`. Before a material executor call freeze:
`contract_id, user_goal, selected_decision, required_attributes, forbidden_attributes, allowed_flexibility, executor_type, success_criteria, verification_method, decision_provenance`.

The Final Executor Brief is derived from that frozen contract. Material mismatch => revise/block before execution. A successful transport receipt with a visibly wrong result => failed drift, not success.

## Self-Critic / verifier
Before consequential completion challenge the strongest conclusion, weakest premise, missing/contradictory evidence, counterexamples, bias, stale authority, arithmetic, source lineage, dissent, budget state, and execution postcondition. Return `pass`, `revise`, or `escalate`. High-impact unresolved defects fail closed.

## Hard rules
Confidence is not evidence. Agreement is not independence. Correlation is not causation. A metric is not the objective. Tool completion is not user-goal success. Server-advertised capability is not host exposure. Unknown side-effect state must be reconciled before retry. Never bypass CAPTCHA, OTP/MFA, credentials, payments, billing or security checkpoints. Do not expose private chain-of-thought; expose conclusions, assumptions, gaps, alternatives and verification criteria when useful.

## Key references/helpers
- `references/master-cognitive-architecture.md`
- `references/runtime-consistency.md`
- `references/verified-self-improvement.md`
- `references/source-taint-protocol.md`
- `references/capability-provenance.md`
- `references/module-registry.md`
- `references/module-router.md`
- `references/personality-council.md`
- `references/source-quality.md`
- `references/book-source-ledger.md`
- `references/live-verification.md`
- `references/execution-binding.md`
- `scripts/pro_receipt_verify.py`
- `scripts/source_taint_check.py`
- `scripts/budget_stop_check.py`
- `scripts/self_improvement_eval.py`
- `scripts/regression_self_test.py`
- `scripts/evidence_consistency_check.py`
- `scripts/artifact_normalize.py`
- `scripts/version_check.py` + `references/version-compat.json`
- `references/expert-studio.md`
- `references/bias-firewall.md`
- `references/books/` (library index + one analysis per book)
- `scripts/ideate.py`, `scripts/decision_sensitivity.py`, `scripts/probability_coherence.py`
