#!/usr/bin/env python3
"""KOSIF Council-100 aggregator (v3.3): evidence-weighted synthesis, never vote counting.

stdin JSON:
{"artifacts": [
   {"id": "security-red-teamer", "stance": "support"|"oppose"|"abstain"|"not-material",
    "confidence": 0.0-1.0, "evidence": ["measured: ...", "source: ..."],
    "objection": "text or empty", "severity": "none"|"low"|"material"|"blocking",
    "disposition": "accepted"|"partially-accepted"|"rejected"|"unresolved",   # after synthesis; optional
    "rejection_evidence": ["why the objection is wrong"]},                     # needed to reject a blocking veto
   ...],
 "sources": {"models": ["claude"], "tools": ["code_scan.py"]}}                 # optional independence info

Rules
- Weight = confidence × evidence factor (0 evidence → 0.25, 1 → 0.6, 2 → 0.85, ≥3 → 1.0).
  Confidence without evidence cannot carry the council.
- A blocking objection from a veto holder (security, privacy, safety, legal, human-checkpoint,
  financial, remote-write, accessibility, ethics, evidence) → verdict `escalate` unless its disposition is
  `rejected` WITH rejection_evidence, or `accepted` (i.e. the plan was changed to satisfy it).
- Any unresolved material objection → `revise`. Majority support never overrides it.
- Independence: personas voiced by one model are one source; report effective independent sources.
Verdict: proceed | revise | escalate. Exit 0 proceed, 1 revise, 3 escalate, 2 invalid.
"""
import json
import sys

from council_select import load

STANCES = {"support", "oppose", "abstain", "not-material"}
SEVERITIES = {"none", "low", "material", "blocking"}
DISPOSITIONS = {"accepted", "partially-accepted", "rejected", "unresolved"}


def ev_factor(n):
    return 0.25 if n == 0 else 0.6 if n == 1 else 0.85 if n == 2 else 1.0


def aggregate(req, data=None):
    data = data or load()
    by_id = {p["id"]: p for p in data["personas"]}
    arts = req.get("artifacts")
    if not isinstance(arts, list) or not arts:
        raise ValueError("artifacts must be a non-empty list")
    issues, seen = [], set()
    support = oppose = 0.0
    chambers = {}
    surviving, blockers = [], []
    for a in arts:
        pid = a.get("id")
        p = by_id.get(pid)
        if not p:
            issues.append(f"unknown persona {pid!r}")
            continue
        if pid in seen:
            issues.append(f"duplicate artifact for {pid}")
            continue
        seen.add(pid)
        stance = a.get("stance")
        if stance not in STANCES:
            issues.append(f"{pid}: invalid stance {stance!r}")
            continue
        sev = a.get("severity", "none" if not a.get("objection") else "material")
        if sev not in SEVERITIES:
            issues.append(f"{pid}: invalid severity {sev!r}")
            continue
        disp = a.get("disposition", "unresolved")
        if disp not in DISPOSITIONS:
            issues.append(f"{pid}: invalid disposition {disp!r}")
            continue
        conf = min(1.0, max(0.0, float(a.get("confidence", 0.5) or 0)))
        w = conf * ev_factor(len(a.get("evidence") or []))
        if stance == "support":
            support += w
        elif stance == "oppose":
            oppose += w
        c = chambers.setdefault(p["chamber"], {"support": 0, "oppose": 0, "abstain": 0, "not-material": 0})
        c[stance] += 1
        if a.get("objection") and sev in {"material", "blocking"}:
            entry = {"id": pid, "name_ar": p["name_ar"], "severity": sev, "veto": p.get("veto"),
                     "objection": a["objection"], "disposition": disp}
            if sev == "blocking" and p.get("veto"):
                ok_reject = disp == "rejected" and bool(a.get("rejection_evidence"))
                if not (ok_reject or disp == "accepted"):
                    blockers.append(entry)
                    continue
            if disp == "unresolved":
                surviving.append(entry)
    if issues:
        return {"ok": False, "verdict": "invalid", "issues": issues}
    models = (req.get("sources") or {}).get("models") or ["single-model"]
    tools = (req.get("sources") or {}).get("tools") or []
    total = support + oppose
    verdict = "escalate" if blockers else "revise" if surviving else "proceed"
    if verdict == "proceed" and total and support / total < 0.5:
        verdict = "revise"
    return {
        "ok": True, "verdict": verdict, "personas_heard": len(seen),
        "weighted_support": round(support, 3), "weighted_oppose": round(oppose, 3),
        "support_share": round(support / total, 3) if total else None,
        "chambers": chambers, "blocking_vetoes": blockers, "surviving_dissent": surviving,
        "effective_independent_sources": len(set(models)) + len(set(tools)),
        "independence_note": f"{len(seen)} personas from {len(set(models))} model(s): agreement among them is not "
                             "independent confirmation.",
        "rule": "evidence-weighted; a blocking veto or unresolved material objection cannot be outvoted",
    }


def main():
    try:
        out = aggregate(json.load(sys.stdin))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "verdict": "invalid", "issues": [str(e)]}))
        return 2
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))
    return {"proceed": 0, "revise": 1, "escalate": 3}.get(out["verdict"], 2)


if __name__ == "__main__":
    raise SystemExit(main())
