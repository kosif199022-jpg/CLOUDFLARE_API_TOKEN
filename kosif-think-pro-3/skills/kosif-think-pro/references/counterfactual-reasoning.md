# Counterfactual & intervention reasoning — worked from *Harry Potter and the Cursed Child* (v3.2)

Source: the supplied Arabic fan translation of the play (390 pp, 4 acts, 74 scenes; fully extracted; text layer partly reversed and repaired). Used as a narrative case study for reasoning, not as factual evidence.

## Case
Goal: save one person (Cedric) by changing a past event. Tool constraints: the Time-Turner prototype goes back only five minutes and returns you to the same place (constraints define the action space).
- Intervention 1 (disarm in Task 1) → Cedric humiliated → a changed world (Ron married to someone else, Hermione a bitter teacher, Albus in a different house).
- Intervention 2 (humiliate in Task 2) → Cedric turns dark → a world ruled by Voldemort, Dementors, the heroes hunted; the intervener's own existence becomes contingent.
- Repair requires a third intervention that restores the original timeline; the characters who lived in the alternate world pay for the repair.
- A helpful ally who volunteered access to the Time-Turner (Delphi, claiming to be a relative) was the adversary: **helpfulness and a claimed identity are not evidence of trustworthiness**.
- Emotional driver: the father–son conflict (Harry and Albus) caused the risky plan; Dumbledore's portrait scene: withholding the truth "to protect" someone caused more harm than telling it.

## Rules extracted
1. **Model the system before intervening**: list the causal chains the changed event participates in; small changes in tightly coupled systems cascade.
2. **Second- and third-order effects**: for each intervention ask "and then what?" three times; include effects on the decision-maker's own future.
3. **Minimal reversible intervention first**; keep a frozen baseline so you can compare and roll back (maps to the Execution Contract and reversibility M16).
4. **Constraints shape strategy**: explicit limits (time window, place, budget) are part of the problem, not obstacles to ignore.
5. **Verify identity and intent of helpers** (provenance/source-taint): an unverified relative/source that grants access is a risk to model, not a trusted input.
6. **Name the motive**: when a plan is driven by guilt, grief or a need to prove oneself, run the Bias Firewall (affect heuristic) before execution.
7. **Truth-telling beats protective silence** in advice: state uncomfortable facts with care.

## Template for /whatif
Intervention → direct effect → second-order effects (people, money, time, trust) → worst plausible cascade → reversibility & rollback → who pays the cost → decision.
