# Visual Execution Reliability Contract — v4

Use a frozen, versioned visual contract for image generation or editing.

## Locks
Record the material subject, action, composition, camera, lighting, environment, style, required elements, forbidden elements, success criteria and a maximum three-item attention budget.

## Observation
Post-generation verification must use evidence explicitly marked as observed and bound to the same request. The helper never claims it inspected pixels by itself.

## Drift and repair
- PASS when the observed result satisfies the frozen contract.
- REPAIR when a bounded, targetable drift is observed and no repair has yet been attempted.
- BLOCK on request mismatch, hard failure, unknown observation state, or exhausted repair budget.

Only one automatic repair candidate is allowed. It keeps the same request and contract identifiers, changes only failed dimensions, requires a fresh preflight before execution, and must be re-verified.

## Receipt
Visual quality evidence is observational and non-cryptographic. It never proves model identity, host enforcement or cryptographic provenance.
