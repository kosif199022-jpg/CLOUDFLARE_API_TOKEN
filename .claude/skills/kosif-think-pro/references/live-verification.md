# Live Verification — 2.7

## Capability provenance
Record requested capability, availability, actual returned source/model when exposed, fallback reason, receipt/correlation ID, duration, completeness and degradation. Configured aliases are not verified model identity. Shared fallbacks are not independent votes.

## Numeric verification
Use deterministic arithmetic for material numbers, explicit units/rounding/currency/period. Confidence, Council agreement or Jev cannot validate arithmetic.

## Source verification
Apply source taint before synthesis. Block quarantined/mixed/unverified evidence from supporting claims. Current-authority claims require current authoritative support, effective date and jurisdiction.

## Council verification
Freeze independent first-pass artifacts. Preserve dissent. Require material answer completeness. Abstention/unavailable differs from disagreement. Majority is descriptive, not truth.

## Execution verification
A frozen Execution Contract, preflight and postcondition are required for material downstream execution. Tool transport success is not user-goal success. Unknown side-effect state must be reconciled before retry.

## Pro completion
`pro_coverage_check.py` verifies legacy structural coverage only. `pro_receipt_verify.py` additionally checks capability receipts/provenance, dissent coverage, source-taint summary and bounded budget consistency. Passing either script does not prove truth or host/kernel enforcement.

## Self-improvement
A saved plugin release is source evidence only. Host adoption requires a fresh behavioral check after reload. Keep known-answer and held-out tests separate.
