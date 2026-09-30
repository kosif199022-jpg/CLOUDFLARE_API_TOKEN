# Causal analysis and computational planning (2.3)
## Reviewed sources, 2026-09-30
Scribd home https://www.scribd.com/home was inspected for discovery. It is not an open-license catalogue. Search listings are not book-reading evidence.
Primary text reviewed: https://causalinference.gitlab.io/causal-reasoning-book-chapter2/ sections 2.1–2.4; https://causalinference.gitlab.io/causal-reasoning-book-chapter3/ introduction and summary. These online book chapters contain incomplete sections; do not imply full-book coverage.
Programming foundation reviewed: OpenStax Introduction to Computer Science 3.1 introduction https://openstax.org/books/introduction-computer-science/pages/3-1-introduction-to-data-structures-and-algorithms and preface. This limited coverage supports structured representation, not claims of mastering all algorithms.

## Causal gate
For recommendations claiming an intervention changes an outcome:
- Specify treatment, outcome, target population, time window and comparison intervention. Separate predictive, associational and interventional questions.
- Describe the proposed causal assumptions and their domain evidence. Label latent variables and measurement limitations. A DAG is an assumption record, not proof.
- Separate modeling, identification, estimation and refutation. If identification is unresolved, report an association or conditional hypothesis rather than a numerical causal effect.
- Check potential confounding, selection bias, collider conditioning and post-treatment adjustment. Do not adjust for every available variable indiscriminately.
- State design and method assumptions, including treatment assignment, overlap and consistency when relevant. Random assignment does not remove problems from attrition, interference, or measurement.
- Define a refutation/sensitivity plan and evidence that could change the recommendation. Distinguish a failed refutation from proof of causality.

## DAG helper
scripts/graph_verify.py checks node/edge schema, self-loops, unknown endpoints, duplicate edges and cycles. A topological order means structurally acyclic only. It does not identify an effect, choose an adjustment set, estimate parameters, or verify causal truth. Cyclic models need a different representation; never silently delete edges to force a DAG.

## Computational plan
Before costly execution specify input size, representation, time/memory limits and acceptable approximation. Prefer explicit dependency graphs for multi-step tasks. Detect cycles before scheduling dependencies. Budget retrieval and tool calls by expected usefulness, with a stopping condition. Measure performance on actual inputs; do not invent runtime improvements or imply this helper accelerates model reasoning.

## Evaluation contract
Include counterexamples: correlation without a justified intervention model; valid DAG with a hidden confounder; unsupported effect magnitude; cyclic dependencies; missing graph nodes. Passing structural checks must not be described as causal validation. Instruction updates are separate from tested host adoption.

