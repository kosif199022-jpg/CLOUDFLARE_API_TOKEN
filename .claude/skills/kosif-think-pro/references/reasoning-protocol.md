# Book-derived reasoning protocol (2.6)
Use after the live first hop. Scale effort to consequence; do not print private reasoning. For non-trivial or Pro work, apply `master-cognitive-architecture.md` and obey `book-source-ledger.md`.

1. **Frame before fan-out.** State the desired observable result, key concept definitions, hard constraints, soft preferences and unknown inputs. For ambiguous concepts compare examples/counterexamples rather than silently changing meaning. Do not launch broad research before the Concept Framing Gate is stable enough to guide retrieval.
2. **Evidence state.** Separate observations, source-backed facts, inferences, assumptions, unknowns and proposals. Preserve effective date and jurisdiction where material. Quarantined sources cannot justify rules.
3. **Bias Firewall.** Probe anchoring, framing/reversal, availability, representativeness, confirmation, overconfidence and bounded awareness for material decisions. A failed check returns revise/escalate.
4. **Alternatives / divergence.** Generate structurally different options, including a reversible pilot when useful. Challenge at least one established assumption. Random association is an idea generator only, never evidence.
5. **Conflict pre-mortem.** Check resource loss, power/incentive conflict, trust friction, internal objective conflict and second-order failure. Convert material risks into controls or contingencies.
6. **Feasibility before preference.** Declare objective, direction and units. Reject options violating hard constraints; unknown feasibility is pending, not pass. Never compensate a hard failure with a high weighted score. Remove verified dominated options.
7. **Sensitivity/reversal.** Vary decision-changing uncertain inputs over stated plausible ranges. If the preferred option changes, report the switching condition and acquire useful evidence or choose a reversible action. Do not invent numerical probabilities.
8. **Council.** Standard Mode selects the smallest useful Trait Profiles. Pro Mode runs all profiles independently before cross-critique. Synthesis is evidence-weighted, not a vote, and preserves unresolved minority objections.
9. **Evaluation Harness.** Define a baseline and task-specific metrics. Keep development examples separate from held-out/unseen checks. Include adversarial/edge cases where relevant. Track false success, source support, completeness and drift separately.
10. **Execution Contract.** Define input preconditions, invariants, forbidden attributes and observable postconditions. Isolate source retrieval, reasoning and execution so failures can be diagnosed. Unknown execution state requires reconciliation before retry.
11. **Verification.** Compute material numbers independently, test adversarial and unseen cases, preserve provenance and unresolved dissent. Verification failure produces revise/escalate, never a confidence override.
12. **Outcome learning.** Propose a specific change from a failure, then evaluate on a separate held-out suite. Record improvements only in an available authorized persistence mechanism. Do not claim automatic memory, model training or weight updates.

## Optional deterministic helpers
- `scripts/decision_verify.py`: exact Decimal Bayes / finite-option hard-constraint screening within its documented limits.
- `scripts/pro_coverage_check.py`: structural completeness of M01..M28 + full Personality Council receipt. It does not prove correctness or independence.
- `scripts/graph_verify.py`: DAG structure only, not causal truth.

Missing/wrong-unit measurements are pending. Zero evidence probability is an error, not a fabricated posterior.
