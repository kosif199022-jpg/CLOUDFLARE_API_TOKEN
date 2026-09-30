# Source Taint Protocol — 2.7

## Statuses
- `adopted` / `readable`: may support bounded claims within reviewed scope.
- `secondary`: may support secondary/context claims; label limitations.
- `historical`: may support historical/terminology claims, not current authority by itself.
- `quarantined`: context only; cannot support claims or runtime rules.
- `mixed`: treat as quarantined for precise claim support until clean passages are isolated.
- `unverified`: cannot support claims until verified.

## Propagation
A claim is tainted when its only supporting sources are blocked for that claim type. Agent repetition, Council agreement, confidence or Jev selection does not cleanse taint.

For each material source-derived claim record source IDs and purpose. Current-authority claims require a current authoritative source/effective date/jurisdiction. Historical/exam/training material may suggest a question but cannot close that gate.

Use `scripts/source_taint_check.py` when Python is available. If not run, do not claim deterministic taint validation.
