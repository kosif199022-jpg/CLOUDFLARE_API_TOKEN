# Pragmatic principles (from The Pragmatic Programmer, fully read) + ML methodology + SICP notes

## The 70 tips, grouped by when to apply them
- **Attitude & ownership**: 1 Care about your craft · 2 Think about your work · 3 Provide options, don't make lame excuses · 4 Don't live with broken windows · 5 Be a catalyst for change · 6 Remember the big picture · 7 Make quality a requirements issue · 8 Invest in your knowledge portfolio · 9 Critically analyse what you read and hear · 10 How you say it matters.
- **Design**: 11 DRY · 12 Make it easy to reuse · 13 Eliminate effects between unrelated things (orthogonality) · 14 No final decisions (keep reversible) · 15 Tracer bullets · 16 Prototype to learn · 17 Program close to the problem domain · 36 Minimise coupling · 37 Configure, don't integrate · 38 Abstractions in code, details in metadata · 39–41 Analyse workflow for concurrency, design using services, always design for concurrency · 42 Separate views from models · 43 Blackboards to coordinate workflow · 53 Abstractions live longer than details.
- **Estimating & planning**: 18 Estimate to avoid surprises · 19 Iterate the schedule with the code · 45 Estimate the order of your algorithms · 46 Test your estimates.
- **Tools**: 20 Plain text · 21 Command shells · 22 One editor well · 23 Always use source control · 28 Learn a text-manipulation language · 29 Write code that writes code · 61 Don't use manual procedures.
- **Debugging**: 24 Fix the problem, not the blame · 25 Don't panic · 26 "select" isn't broken · 27 Don't assume it — prove it.
- **Defensive coding**: 30 You can't write perfect software · 31 Design with contracts · 32 Crash early · 33 Assertions for "can't happen" · 34 Exceptions for exceptional problems · 35 Finish what you start.
- **While coding**: 44 Don't program by coincidence · 47 Refactor early, refactor often · 48 Design to test · 50 Don't use wizard code you don't understand.
- **Requirements**: 51 Dig for requirements · 52 Work with a user to think like a user · 54 Project glossary · 55 Find the box (real constraints) · 56 Listen to nagging doubts · 57 Some things are better done than described · 58 Don't be a slave to formal methods · 59 Expensive tools don't make better designs.
- **Teams & delivery**: 60 Organise around functionality · 62 Test early, often, automatically · 63 Not done until all tests run · 64 Saboteurs test your tests · 65 State coverage over code coverage · 66 Find bugs once · 67 Treat English as a programming language · 68 Build documentation in · 69 Gently exceed expectations · 70 Sign your work.

## Checklists (use in /review, /debug, /design-review)
- **Debugging**: Is this the bug or a symptom? Is it really the compiler/OS, or our code? Explain it step by step (rubber duck). If the suspect code passes its tests, are the tests complete — what happens with *this* data? Do the same conditions exist elsewhere? → add a regression test (find bugs once).
- **Orthogonality**: independent well-defined components · decoupled code · no global data · refactor similar functions.
- **Architecture questions**: responsibilities defined? collaborations defined? coupling minimised? duplication? interfaces & constraints acceptable? can modules reach needed data when needed?
- **Law of Demeter**: a method calls only its own methods, its parameters, objects it creates, its components.
- **Program deliberately**: be aware · plan · rely only on reliable things · document assumptions · test assumptions as well as code · prioritise · don't be a slave to history.
- **When to refactor**: DRY violation · non-orthogonality · knowledge improved · requirements evolved · performance.
- **Gordian knot** (impossible problems): easier way? right problem? why is it a problem? what makes it hard? must it be done this way? at all?
- **Aspects of testing**: unit · integration · validation & verification · resource exhaustion, errors, recovery · performance · usability · testing the tests.
- **Prototype when unsure about**: architecture · new functionality in an existing system · external data structure · third-party components · performance · UI.

## /ml — machine-learning project checklist (Deep Learning ch.11 structure)
1. Performance metric tied to the real goal (precision/recall/coverage, cost of errors) + target value.
2. Default baseline model first (simple, well-known) and an end-to-end pipeline.
3. Diagnose: train vs validation error → underfitting (bigger model, better features) or overfitting (more data, regularisation, augmentation, early stopping).
4. Decide whether to gather more data (learning curves) before tuning.
5. Hyperparameters on a validation set only; test set touched once.
6. Debugging strategies: visualise predictions, check worst errors, fit a tiny dataset, compare to reference implementations, monitor activations/gradients.
7. Include adversarial/edge cases in evaluation. Details beyond the TOC are background knowledge.

## Optimisation (Convex Optimization ch.1)
Recognise the problem class before solving: least-squares (`numpy.linalg.lstsq`) → LP (`scipy.optimize.linprog`) → convex (cvxpy if available) → nonlinear (local optimum only; say so). Formulate: variables, objective, firm constraints; check feasibility first.

## SICP notes (study-guide source, secondary)
Prefer data-directed dispatch tables over ever-growing switch statements; distinguish a recursive *procedure* from a recursive *process* (an iterative process keeps constant state); write REPL-style input→expected tests before extending interpreters or DSLs.
