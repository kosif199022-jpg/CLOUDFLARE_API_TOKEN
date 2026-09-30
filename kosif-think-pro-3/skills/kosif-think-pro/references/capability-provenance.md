# Capability Provenance — 2.7.1

At Pro start, snapshot materially applicable capabilities as `requested / available / unavailable / not-needed`. After calls, record `used`, actual returned source/model when exposed, fallback reason, receipt/correlation ID, completeness and degradation.

Required fields for used capability records:
- `id`
- `kind`: model | tool | app
- `requested`
- `available`
- `used`
- `actual_source`
- `actual_model` for model paths when returned
- `fallback_reason` when fallback/substitution occurred
- `receipt_id` when the provider/tool exposes one; otherwise `receipt_evidence` with an observed host-tool-result/state-observation type and limitation

Configured aliases and status declarations are not independent proof of provider identity. Shared fallback models do not count as independent verification. A claimed used path needs observable receipt evidence. Native receipt IDs are preferred; when unavailable, an explicit observed host-tool-result/state-observation record is acceptable but is not cryptographic/provider proof.
