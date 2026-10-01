# Source Atlas v4.0.1

Source records preserve lineage; retrieval weighting prevents evidence inflation.

## Rules
- If SHA-256 is provided, preserve it. If missing and text is available, compute SHA-256 deterministically from the source text.
- Exact duplicates remain separate source records but receive **one canonical retrieval vote**. The canonical eligible record has `retrieval_weight=1`; exact copies get `0` and point to `duplicate_of`.
- Near duplicates are grouped conservatively and remain traceable; do not silently collapse them into one record.
- Empty sources, vendor/build/.git/generated material and private/secret/credential sources have retrieval weight 0 for durable knowledge.
- Record `age_days` and `freshness`. Without an explicit freshness threshold, freshness is `unknown` rather than guessed.
- Platform/version-sensitive syntax requires execution-time/provider-current verification when current behavior matters.

## Corpus snapshot used for v4
The reviewed source set includes the AI Studio 85-record manifest/profiles, the newer Drive root and nested projects, prompt/platform guides, 360-character workflows, Cinema/Blue Dragon/Aetherius/MasryTube/Pokemon/Shining Star sources, artifact-building manuals and GitHub v3.4 architecture. Private operational accounting/legal/product documents remain quarantined from durable plugin knowledge.
