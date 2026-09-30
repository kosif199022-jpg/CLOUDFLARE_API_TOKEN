# Verified Self-Improvement Layer — 2.7.1

Purpose: improve KOSIF orchestration without confusing edited instructions with measured intelligence or kernel enforcement.

## Five controls
1. **Traceable Pro receipt:** structural coverage is necessary but insufficient. A completion receipt records actual/fallback capability provenance and observable receipt evidence for used paths.
2. **Source-taint propagation:** claims/rules inherit evidence restrictions. A quarantined or unverified source cannot become valid merely because another agent repeats it.
3. **Dissent preservation:** every completed Council profile leaves a compact objection/disposition artifact. Material unresolved dissent forces revise/escalate.
4. **Bounded execution:** model/tool/retry/no-change budgets prevent performative fan-out and infinite self-improvement loops.
5. **Outcome calibration:** compare candidate behavior with a baseline on held-out/adversarial cases. Track false success, source support, completeness, fallback, drift and latency separately.

## What this layer can enforce
Within a skill/plugin package it can:
- require fields/instructions;
- provide deterministic helper validators;
- gate claims in hosts that honor the skill;
- ship repeatable regression fixtures;
- make provenance gaps explicit.

It cannot by itself:
- force the host/kernel to call a tool;
- cryptographically prove provider identity;
- change model weights;
- persist learning without an authorized persistence mechanism;
- guarantee that a helper script was executed unless there is an observed script/tool receipt.

## Completion rule
For Pro work, do not say "all capabilities were used" from module/profile coverage alone. State actual live/fallback/unavailable coverage. If `pro_receipt_verify.py` is unavailable, label the receipt `not-deterministically-validated`.

## Self-improvement release gate
A self-improvement release is ready only when:
- a baseline weakness is reproduced;
- candidate change targets that weakness;
- adversarial regression passes;
- no protected invariant regresses;
- source update is published/read back;
- measured host adoption is reported separately from saved source.
