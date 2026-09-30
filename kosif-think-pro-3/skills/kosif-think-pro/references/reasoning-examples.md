# Worked examples — how KOSIF should think (few-shot for ChatGPT / Claude)

Use these as patterns. Each shows the visible output style; internal reasoning stays private.

## 1. Numeric answer with contradicting agents
User: "120 units, 15% defective, we sold 10 good ones — how many good units are left?" Agents answered 97, 100, 92.
KOSIF: compute independently (`evidence_consistency_check.py`: 120 − 18 − 10 = 92, repeated by two sources) → quarantine 97 and 100 → **92**, with the one-line calculation.

## 2. Picture inference with calibrated language
User uploads a photo of a man seen from behind looking at a city at dusk.
KOSIF: observation first ("figure with back to camera, warm low sun from the right, CCT ≈3400 K measured, subject on the left third") → impression hedged ("this creates a feeling of solitude/mystery; he *might* be waiting for someone") → never "he is obviously depressed" (no evidence). `calibration_check.py` flags "obviously" if used.

## 3. Reading a contract/report (comprehension cycle)
Before: "title suggests a lease → I predict term, rent, renewal, penalties matter". While: mark clauses 4.1 (term), 7.3 (penalty). After: each answer cites its clause ("how do I know? clause 7.3"). Decide: output as a table + risks.

## 4. Base-rate question
"A test is 90% sensitive, 9% false positive, disease prevalence 1%. Positive result — 90% chance of disease?"
KOSIF: `probability_coherence.py` → posterior ≈ 9.2% (per 1,000 people: 9 true vs 89 false positives) → flag base-rate neglect.

## 5. Decision with fragile weights
Three suppliers; KOSIF screens firm constraints (quality ≥ 6), marks the one with missing speed data *pending*, removes the dominated option, ranks the rest, and reports "B wins, but if cost weight rises from 0.40 to 0.48, A wins" (`decision_sensitivity.py`). Recommendation includes what data would settle it.

## 6. Counterfactual plan
"Should we reverse last month's price increase?" → /whatif template: direct effect (volume up), second-order (competitor reaction, customer expectation of future discounts), cascade (margin squeeze), reversibility (hard to re-raise), who pays, decision: pilot in one region first.

## 7. Story beat check
Ad script where the product "magically" solves the problem → `story_lint.py`: "no protagonist choice (agency)". Fix: the character *chooses* the product after a failed attempt; stakes are personal.

## 8. Accounting
Invoice INV-104 (1,000 + 15% VAT = 1,150) and a bank receipt of 1,150 from the same customer → one event: Dr Receivable/Cr Revenue & VAT, then Dr Bank/Cr Receivable. Booking the bank line as revenue would double revenue (`ledger_check.py` flags it).

## 9. Code bug
"My loop skips the last item." → Pragmatic debugging checklist: reproduce with the smallest list, it's our code not the language ("select isn't broken"), off-by-one in `range(len(x)-1)`, fix, add a regression test ("find bugs once").

## 10. Disagreeing politely inside the Council
Adversarial Critic: "The plan is well structured, I suppose, but the demand estimate is a bit too optimistic for my liking — it relies on one survey." → dissent ledger keeps the objection and what would resolve it (a second data source).
