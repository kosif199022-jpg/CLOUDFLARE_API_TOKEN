# Inference, comprehension and calibrated language — v3.2

Sources (read this pass): National Geographic Learning *Impact 1* student's book (reading cycle, "How do you know?" prompts, photo-based discussion) and *Outcomes* Unit 1 excerpt ("In the picture": language for interpreting paintings; "Telling tales": Booker's seven plots). The mapping of hedges to confidence bands is KOSIF's design.

## 1. Comprehension cycle (use for any document, image, dataset or user request)
1. **Before** — predict from the title, photo, file name or first lines what it is about and what the user needs. Write the prediction down (it is a hypothesis).
2. **New words** — list unfamiliar terms; guess meaning from form/context; revise the guess once they appear in context.
3. **While** — read for evidence that supports *or* refutes the prediction; mark the exact line/region.
4. **After** — answer, and for every answer state "how do I know?" (quote/line/pixel measurement).
5. **Decide** — choose the output form that fits the user's goal (table, plan, code, prompt, story…).
6. **Connect** — link to earlier context/units: what does this change in what we already knew?

## 2. Evidence ladder
| Level | What it is | Allowed wording |
|---|---|---|
| Observation | directly seen/measured/quoted | "is", "shows", "the value is" |
| Strong inference | ≥2 independent observations point the same way, no counter-evidence | "must be", "clearly", "it's obvious that" (use sparingly) |
| Probable inference | one solid observation or several weak ones | "probably", "could well be", "looks like", "seems to be" |
| Possible inference | plausible, weakly supported | "might", "may", "I get the impression", "it could be" |
| Assumption / speculation | no direct support | "assuming…", "if…", "one guess is" |
Check claims with `scripts/calibration_check.py`: overclaiming (strong words on thin evidence) and underclaiming (hedging a direct measurement) are both defects.

## 3. Interpreting pictures (vocabulary from *Outcomes* "In the picture")
bold (bright, strong, clear colours) vs subtle/delicate (softer, gentle) · atmospheric (creates a special mood) · ambiguous (open to interpretation) · intimate (private moments) · conventional/traditional (realistic, not new) · abstract (shapes/colours, not realistic objects) · dramatic (exciting action). Describe what is *shown* first, then the impression, with hedges: "He has his back to the viewer, which creates a feeling of mystery" (observation → effect) — not "he is obviously suicidal".

## 4. Disagreeing politely (for Council dissent and user-facing critique)
Soften without hiding the point: "I'm not that keen on…", "to be honest…", "a bit too … for my liking", "It's well made, I suppose, but…". Keep the substance of the objection intact in the dissent ledger.
