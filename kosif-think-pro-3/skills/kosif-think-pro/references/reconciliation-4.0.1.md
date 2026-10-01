# v4.0.1 reconciliation rules

This patch reconciles the published v4.0.0 with additional Drive/GitHub review without replacing its safety model.

1. **Duplicate evidence:** preserving duplicate provenance is not enough; exact copies must receive one canonical retrieval vote. A duplicated file may be cited as lineage but cannot multiply evidentiary weight.
2. **Adapter truth:** each platform gets its own adapter record. Never attach Midjourney provenance to ChatGPT/Flux/SDXL/Ideogram merely to satisfy a schema.
3. **Version-sensitive syntax:** a source book/repo can provide a useful historical syntax example. Until current provider docs are freshly verified, keep that example in `source_syntax_prompt` and compile a version-neutral prompt instead of claiming the exact flags are current.
4. **Identity reference vs observation:** the reference set may require five views for good coverage. A single generated image normally exposes only one/few views; absence of the other reference views in that one image is not identity drift. Block only actual observed immutable drift, character-ID mismatch, or a specifically required current view that is missing.
5. **Secrets:** source code from Drive/GitHub must pass a redaction/blocking gate before reuse or publication. Never include detected secret values in logs or plugin references.
