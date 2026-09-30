# Bias Firewall — v3.1

Grounded in Smart Thinking ch.1–2 (readable) and the bias-family headings of Judgment in Managerial Decision Making (TOC-only copy). Run for material decisions, estimates, forecasts and rankings. Metacognition rule: monitor hardest when intuitions are likely unreliable (statistics, risk, unfamiliar domains) and when decisions are complex.

| Trap | Probe question | Deterministic check |
|---|---|---|
| Narrative fallacy | Am I forcing events into a familiar story? What else would explain the same facts? | list ≥2 alternative explanations |
| Representativeness / base-rate neglect | What is the base rate before this description? | `probability_coherence.py` Bayes (per-1000 counts) |
| Conjunction fallacy | Did I rate "A and B" above "A" alone? | conjunction rule in `probability_coherence.py` |
| Belief bias | Am I judging the argument's validity by whether I like its conclusion? | test validity with the conclusion negated |
| Anchoring | Which number did I see first? Would I estimate the same without it? | re-estimate from an independent reference class |
| Availability | Am I overweighting what is vivid or recent? | seek frequency data |
| Affect heuristic | Is liking/fear standing in for risk/benefit analysis? | score risk and benefit separately |
| Overconfidence (overprecision, overestimation, overplacement) | Would my 90% interval really contain the truth 9 times in 10? | widen intervals; calibrate against outcomes (M26) |
| Confirmation | What evidence would prove me wrong, and did I look for it? | record disconfirming search in the dissent ledger |
| Bounded awareness (inattentional/change blindness, focalism) | What information is outside my focus but decision-relevant? Who else is affected? | stakeholder + pre-mortem scan |
| Framing / preference reversal / pseudocertainty | Does my choice flip if gains are framed as losses, or certainty is only apparent? | reframe both ways; compare |

Outcome: pass / revise / escalate. A failed probe is recorded in the receipt's `gates.bias_gate`.
