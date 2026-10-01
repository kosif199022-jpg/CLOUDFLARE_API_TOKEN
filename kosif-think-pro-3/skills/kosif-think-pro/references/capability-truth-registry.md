# Capability Truth Registry

States: `verified`, `measured`, `implemented`, `host-dependent`, `prompt-only`, `simulated`, `historical`, `unavailable`.

Promotion rules:
- `verified`: deterministic/observable evidence appropriate to the capability plus an observed executor/artifact/measurement path.
- `measured`: a measurement ran, but it may not prove full end-to-end execution.
- `implemented`: source code/logic exists; runtime behavior has not been observed here.
- `host-dependent`: capability requires a host tool/app; server metadata alone is insufficient.
- `prompt-only`: instructions/persona/knowledge only.
- `simulated`: demo/mock/fake output path.
- `historical`: once-relevant version-specific behavior that is not current evidence.
- `unavailable`: not exposed or failed current verification.

Never infer a higher state from confidence, marketing copy, tool names or persona counts.
