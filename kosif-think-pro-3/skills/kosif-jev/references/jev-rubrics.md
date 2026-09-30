# Ready Jev rubrics and option sets

Levels are ordered lowest → highest. Put the evidence (measurements, text, diff summary) in `state`.

## Prompt production-readiness (score)
`["unusable — the model cannot tell what to produce", "weak — task present, format/constraints/context missing", "adequate — task + format + some constraints, edge cases unhandled", "strong — full structure, delimited inputs, example, edge cases", "production-ready — plus tested typical/edge/adversarial cases with recorded results"]`

## Web page quality (score) — state: web_audit.py summary + screenshots notes
`["broken — blockers (zoom disabled, contrast failures, missing viewport)", "poor — many high issues", "acceptable — minor issues only", "good — AA in both themes, responsive, clear hierarchy", "excellent — plus fast, polished states, measured conversion elements"]`

## Pull-request readiness (score) — state: diff stats, CI status, PR body
`["not reviewable", "needs work — missing tests or description", "reviewable — tests and description present", "ready — CI green, focused diff, test plan with results", "exemplary — plus risk/rollback notes and docs"]`

## Idea value (score, as in cloude/docs/ROADMAP-ar.md)
`["ضعيفة", "محدودة", "متوسطة", "عالية", "حاسمة"]`

## GitHub operation class (choice)
```json
{"read_only": "only reading repository/PR/issue/CI data",
 "local_write": "local commits or branches only",
 "remote_write": "push, PR, comment, review, release or any change visible on GitHub",
 "destructive": "force-push, history rewrite, deleting branches/tags/repos",
 "unclear": "the request does not say enough to classify"}
```

## Request lane (choice) — KOSIF expert routing
```json
{"vision": "analyse an uploaded image", "image": "create/edit image prompts", "lighting": "light plans and exposure",
 "audio": "audio analysis, mastering, songs", "code": "programming, debugging, review", "video": "video, story, shots",
 "audit": "accounting, VAT, IFRS, audit", "prompt": "write or fix prompts for models", "web": "websites, UI, design systems",
 "github": "git and GitHub operations", "computer": "operate a browser, desktop or app", "reasoning": "decision, verification, research"}
```

## Evidence sufficiency (noul)
Question: "Does the state contain enough direct evidence to support the conclusion without assumptions?"
true_criteria: "every material claim in the conclusion is backed by a measured, observed or cited item in the state"
false_criteria: "at least one material claim rests on an assumption or on missing information"

## Council objection review (noul)
Question: "Could any surviving objection in the state change the council's conclusion if it were true?"
true_criteria: "at least one unresolved objection is material to the conclusion"
false_criteria: "all objections are resolved, immaterial, or already reflected in the conclusion"

## Stability recipe
1. Original packet. 2. Same packet with option order reversed. 3. Question rephrased with the same meaning.
All three agree ⇒ stable. Otherwise treat the judgement as unavailable and gather evidence or ask the user.
