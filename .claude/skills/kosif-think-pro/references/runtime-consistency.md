# Runtime Consistency & Host Exposure — v0.8.3 (Pro package 3.0)

Use this reference whenever KOSIF Think Pro 2 calls the live KOSIF runtime.

## Answer/evidence consistency
- A model answer field is not authoritative merely because its confidence is high.
- When at least two independently-provenanced artifacts end in the same deterministically valid arithmetic result, any numeric answer that omits/contradicts that result is quarantined from synthesis.
- If every numeric answer is quarantined but the deterministic arithmetic result is independently repeated, the provisional synthesis may repair to that arithmetic result with model confidence discarded.
- Pro 3.0 generalizes the gate with typed deterministic validators in `scripts/evidence_consistency_check.py`: `arithmetic` (safe expression evaluation, `15%` = 0.15), `sum`, `percent`, `ratio`, `range`, `date_order`, `unit`. Convergence requires the same valid arithmetic result from >= 2 distinct sources; two different converged values are an evidence conflict and must escalate.
- The gate remains provisional: Jev/ChatGPT review and ordinary evidence checks still apply.

## Host-tool exposure truthfulness
- `kosif_think_status` may report that a tool exists on the server. That does not prove the current ChatGPT host exposed the tool in this conversation.
- Treat the live host tool catalog as authoritative for direct invocation.
- If `kosif_auto` or `kosif_route` is absent from the host catalog, record direct capability as unavailable.
- If an exposed mobile bridge provides `kosif_mobile_capabilities` / `kosif_mobile_call`, inspect the live schema and use that bridge for advanced runtime calls. Do not assume the bridge is exposed merely because the server implements it.

## Regression case
Known-answer case: 120 units, 15% defective, then sell 10 non-defective units => 92 non-defective remain. The v0.8.3+ runtime must quarantine conflicting numeric answer fields when their independently repeated valid arithmetic evidence terminates at 92.
