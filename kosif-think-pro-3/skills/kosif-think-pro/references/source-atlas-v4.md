# Source Atlas v4 — Public Policy

Source Atlas is the provenance and corpus-hygiene layer for KOSIF Think Pro 4.

## Rules
- Preserve every source record and its lineage, but exact duplicates receive a single retrieval/evidence weight.
- Cluster near duplicates before treating them as independent support.
- Empty/unreadable records may prove provenance only; they cannot support substantive claims.
- Generated/vendor/build/cache content is implementation context, not durable knowledge by default.
- Private operational material is excluded from public durable knowledge; only anonymized regression shapes may be retained.
- Platform/provider syntax carries version and freshness metadata. Historical guidance is not a current provider claim.
- A source summary is not proof that every underlying source was fully read; coverage is recorded explicitly.

## Deterministic layer
See `scripts/source_atlas.py` for exact-hash, near-duplicate, quarantine and freshness mechanics.

## Public/private boundary
Detailed private source identifiers stay in the private plugin/source ledger. Public GitHub stores only transferable rules and sanitized provenance summaries.
