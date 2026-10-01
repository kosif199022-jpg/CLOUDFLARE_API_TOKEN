# Identity Reference Set v4.0.1

Reference-set coverage and per-artifact verification are different questions.

A strong reference set uses front, left, right, back and three-quarter views plus immutable traits and explicitly allowed mutable traits. `ready=true` means the **reference set** is complete.

When checking one generated frame, compare only traits/views actually observable in that frame. Missing unobserved immutable traits are reported as `unobserved_traits`, not as drift. Block only observed immutable mismatch, character-ID mismatch, or an explicitly `required_current_view` that is not visible.

This remains a generation-consistency mechanism, not biometric identification.
