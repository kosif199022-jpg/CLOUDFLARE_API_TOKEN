# Convex Optimization (Boyd & Vandenberghe) — chapter 1 only

Coverage: pp.1–27 clean (ch.1 Introduction). Pages 28–205 of the supplied file are unrelated fiction text — contaminated.

## Transferred
- Optimisation = choose x minimising cost f0(x) subject to firm requirements fi(x) ≤ bi; a solution is the best choice among those meeting the firm requirements → **feasibility before preference**.
- Recognition ladder: least-squares (quadratic objective, analytic/very reliable) → linear programming (many problems reducible, e.g. Chebyshev approximation) → convex (efficiently solvable once recognised; recognition is the skill) → general nonlinear (local optimisation gives a good point, not a guaranteed best; global methods are exponential).
- Never claim a global optimum without mathematical support.

## Where it lives
`scripts/decision_sensitivity.py` (firm constraints, pending on missing data, Pareto dominance, weighted ranking, weight-flip thresholds), `/decide`; code-master `/optimize` uses LP/least-squares via SciPy when the problem is recognised as such.
