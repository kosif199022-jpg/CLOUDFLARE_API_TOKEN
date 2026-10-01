# KOSIF Jev Arbiter — typed judgements, never authority

Jev (TypeSafe System One models) returns **structured judgements with probabilities**, not prose. It is a fast, calibrated-looking second opinion on a closed question. In KOSIF it is a judge of evidence you give it, never the evidence itself and never the approver of risky actions (same rule as the user's `cloude` think-mcp worker: "Jev may disambiguate a closed candidate set but never grants approval for a high-risk action").

## When to use which
| Mode | Tool | Use for | Output |
|---|---|---|---|
| noul | `jev_noul` | one yes/no question over evidence ("does this PR description include a test plan?") | probability of yes |
| choice | `jev_choice` | exactly one of N labels ("which lane handles this request?", "which element matches the instruction?") | choice + probabilities + confidence |
| score | `jev_score` | a position on an ordered rubric ("how production-ready is this prompt?") | expected level, level probabilities, confidence |
Do **not** use Jev for: arithmetic, facts that need a source, anything a deterministic check can decide, open-ended writing, approvals of payments/deletions/pushes/sends, or when the deciding information is missing (then ask the user).

## Protocol
1. **Deterministic first** — run the domain's measured checks (lint, contrast, tests, ranking). Call Jev only for what remains a judgement, or for ties/ambiguity.
2. **Build the packet** — `scripts/jev_packet.py build` with `mode`, a complete `question`, the facts as `evidence` (becomes `state`), and a closed `options` set (descriptions for each label; rubric levels lowest → highest). It redacts secrets/personal data and BLOCKs authorisation questions.
3. **Call** the host tool with the packet exactly as built. If the tool is not in the current host catalog, record `unavailable` and fall back to the deterministic result or the council; never pretend Jev ran.
4. **Interpret** — `scripts/jev_packet.py interpret` on the raw result: noul classes (strong/lean/uncertain), choice margin, score expected-vs-argmax. `score` in a raw result is the probability-weighted expected level, not a percentage.
5. **Stability for consequential calls** — call again with options reordered and the question rephrased; `jev_packet.py stability`. Unstable ⇒ do not rely on it.
6. **Record provenance** — returned model id (e.g. `jev-1.13.0`), packet, decision, probabilities, time. In Pro receipts Jev is a `tool` with `actual_source` and receipt evidence.
7. **Use** — Jev's output may rank, route or flag; the final decision, and any risky action, still goes through KOSIF gates and the user.

## Built-in uses across KOSIF
- **Prompt Master** — `jev_score` a prompt on the 5-level rubric (`references/kosif-prompt-master/prompt-patterns.md`) next to `llm_prompt_lint.py`; report both.
- **Web Design** — `jev_choice` between typeface or layout options with the audit numbers in the state (how the user's `cloude` repo chose IBM Plex Sans Arabic, p≈0.99).
- **GitHub** — `jev_choice` to classify a request (read-only / local / remote write / destructive) as a cross-check of `gh_preflight.py`; `jev_noul` "does the PR body contain a real test plan?".
- **Computer Use** — `ui_ground.py` emits a `jev_choice` packet over observed candidates when ranking ties; accept only confidence ≥ 0.7 and never when `underspecified`.
- **Council-100** — after `council_aggregate.py`, `jev_noul` "could any surviving objection change the conclusion?" as a review; Jev never outvotes a veto.
- **Roadmaps** — `jev_score` each idea's value on a 0–4 rubric with confidence (as in the user's `cloude/docs/ROADMAP-ar.md`).

## Observed behaviour (live, 2026-09-30, jev-1.13.0)
- Correctly scored the prompt "a cat" as *weak* (p=0.88) on the production-readiness rubric.
- Classified "push my changes and open a pull request" as `remote_write` with confidence 1.0.
- Chose "Download PDF" with confidence 0.91 for the **under-specified** "click Download" (PDF vs CSV unstated) → high confidence can hide missing intent; KOSIF asks the user in that case.

## Commands
`/jev <question>` pick the mode, build, call, interpret · `/noul <question> | <evidence>` · `/choose <question> | <options> | <evidence>` · `/score <dimension> | <levels> | <evidence>` · `/triage <items>` one `jev_choice` per item into fixed lanes · `/rank <ideas>` `jev_score` each on a value rubric then sort by expected level, ties by confidence.

References: `references/kosif-jev/jev-rubrics.md` (ready rubrics and option sets).
