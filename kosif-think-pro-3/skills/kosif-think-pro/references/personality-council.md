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
