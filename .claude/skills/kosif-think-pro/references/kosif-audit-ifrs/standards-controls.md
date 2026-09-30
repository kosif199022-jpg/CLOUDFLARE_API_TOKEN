# Standards → system controls (from the AI-Powered Accounting Skill report, sec. "Standards map")

| Framework | Operational requirement | Control & evidence the skill records | Review owner |
|---|---|---|---|
| IFRS 15 | contract, performance obligations, transaction price, allocation, timing | contract fields, obligation map, allocation worksheet, approval | Controller |
| IFRS 9 | classify financial assets; expected credit losses | business-model flag, cash-flow terms, ageing/ECL schedule | Controller / credit lead |
| IAS 2 | lower of cost and NRV; expense cost when revenue recognised | cost layers, NRV test, FIFO/weighted-average policy, write-down entry | Inventory owner |
| IAS 16 | recognise PPE when benefits probable & cost reliable; systematic depreciation | asset register, component/cost evidence, useful life approval | Controller |
| IAS 8 | policy change vs estimate change vs prior-period error | versioned policy, retrospective/prospective flag, correction link | Controller / auditor |
| IAS 12 | current vs deferred tax from tax-base evidence | tax package, temporary-difference schedule, tax sign-off | Tax adviser |
| IFRS 16 | identify leases; ROU asset and lease liability | contract scan, lease term, discount-rate approval, ROU roll-forward | Controller |
| IAS 36 | impairment indicators; recoverable amount | indicator checklist, valuation inputs, impairment journal | Controller |
| IAS 7 | operating / investing / financing; reconcile cash to SFP | cash-flow mapping, reconciliation | Controller |
| ISA 315/500/530 | risk assessment; sufficient appropriate evidence; sampling | risk register, evidence index, sample plan, reviewer sign-off | Engagement team |
| COSO | control environment, risk, activities, information, monitoring | role matrix, control tests, exception dashboard, remediation log | Control owner |

Release gates from the report: a single unbalanced entry, lost original, cross-tenant leak or posting without approval stops release regardless of speed. Pilot metrics: entry accuracy ≥95% on recurring cases, 100% halala-correct posted amounts, zero duplicates in the gold set, 100% evidence coverage, ≥99% correct escalation of new cases.

Exception playbook (report sec. 18): new customer → temporary record + identity question · total ≠ base+tax → arithmetic exception · payment short (e.g. 1,125 vs 1,150) → partial match, ask for the difference (discount? fee? partial?) · bank line without reference → suspense draft or request support · blurred scan → request a clearer original (a blurred amount is not evidence).
