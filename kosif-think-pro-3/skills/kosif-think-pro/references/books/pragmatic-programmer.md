# The Pragmatic Programmer (Hunt & Thomas) — full read

Coverage: all 352 pages; the 70 numbered tips and the quick-reference checklists were extracted verbatim-titled and mapped.

## Core ideas transferred (own words)
- **Care + think + own it**: provide options, not excuses; fix "broken windows" (small rot invites large rot).
- **DRY & orthogonality**: one authoritative representation of every piece of knowledge; independent components with minimal coupling; avoid global state; Law of Demeter (call only yourself, parameters, objects you create, your components).
- **Tracer bullets vs prototypes**: tracer = thin end-to-end working path you keep; prototype = throwaway to learn (architecture, new features, external data, third-party tools, performance, UI).
- **Design by contract & crash early**: preconditions, postconditions, invariants; assertions for "can't happen"; exceptions for exceptional cases only; finish what you start (resources).
- **Debugging discipline**: fix the problem not the blame; don't panic; "select isn't broken" (suspect your code first); don't assume — prove; rubber-duck explanation; ask whether the report is the bug or a symptom, whether tests are complete enough, and whether the same conditions exist elsewhere.
- **Program deliberately** (not by coincidence): proceed from a plan, rely only on reliable things, document and test assumptions, prioritise, don't be a slave to history.
- **Refactor when**: DRY violations, non-orthogonal parts, knowledge improves, requirements evolve, performance needs.
- **Testing**: test early/often/automatically; coding isn't done until all tests run; use saboteurs to test the tests; state coverage over code coverage; find bugs once (add a regression test); aspects: unit, integration, validation, resource exhaustion & recovery, performance, usability, testing the tests.
- **Requirements**: dig for them; work with a user; abstractions outlive details; keep a project glossary; "don't think outside the box — find the box" (identify real constraints: Gordian-knot questions — easier way? right problem? why is it hard? must it be done this way? at all?).
- **Communication (WISDOM)**: what should they learn, their interest, sophistication, detail wanted, who owns it, how to motivate.

## Where it lives in KOSIF
kosif-code-master: `references/pragmatic-principles.md`, `/debug`, `/review`, `/design-review`; Execution Contract (pre/postconditions) in kosif-think-pro; regression suite rule "find bugs once".
