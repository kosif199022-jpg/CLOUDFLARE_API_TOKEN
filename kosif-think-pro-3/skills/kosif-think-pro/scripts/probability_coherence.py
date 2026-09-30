#!/usr/bin/env python3
"""KOSIF probability coherence & base-rate checker (v3.1).

Grounded in Smart Thinking ch.1-2 (representativeness, the Linda conjunction
fallacy, base-rate neglect, anchoring, availability, affect heuristic) — these are
the heuristics the Bias Firewall must catch. This helper checks the arithmetic
part deterministically; judgement biases still need the Bias Firewall prompts.

stdin JSON:
{"events": {"A": "0.3", "B": "0.6", "A&B": "0.4", "not A": "0.7", "A|B": "0.5"},
 "bayes": [{"name": "test", "prior": "0.01", "sensitivity": "0.9",
            "false_positive_rate": "0.09", "stated_posterior": "0.9"}]}
Keys: "X", "not X", "X&Y" (and), "X|Y" (or). Probabilities as decimal strings.
"""
import json
import sys
from decimal import Decimal


def d(x):
    v = Decimal(str(x))
    if not v.is_finite():
        raise ValueError("non-finite")
    return v


def check(o):
    ev = {k: d(v) for k, v in (o.get("events") or {}).items()}
    issues, notes = [], []
    for k, v in ev.items():
        if v < 0 or v > 1:
            issues.append(f"P({k})={v} outside [0,1]")
    for k, v in ev.items():
        if k.startswith("not "):
            base = k[4:]
            if base in ev and abs(ev[base] + v - 1) > Decimal("0.0001"):
                issues.append(f"P({base}) + P(not {base}) = {ev[base] + v}, must be 1")
        if "&" in k:
            parts = [p.strip() for p in k.split("&")]
            for p in parts:
                if p in ev and v > ev[p]:
                    issues.append(f"conjunction fallacy: P({k})={v} > P({p})={ev[p]}")
        if "|" in k:
            parts = [p.strip() for p in k.split("|")]
            for p in parts:
                if p in ev and v < ev[p]:
                    issues.append(f"disjunction error: P({k})={v} < P({p})={ev[p]}")
            if len(parts) == 2 and all(p in ev for p in parts):
                a, b = parts
                inter = ev.get(f"{a}&{b}", ev.get(f"{b}&{a}"))
                if inter is not None and abs(ev[a] + ev[b] - inter - v) > Decimal("0.0001"):
                    issues.append(f"P({a}|{b}) should be {ev[a] + ev[b] - inter} (inclusion-exclusion)")
    bayes = []
    for b in o.get("bayes") or []:
        p, s, f = d(b["prior"]), d(b["sensitivity"]), d(b["false_positive_rate"])
        if any(x < 0 or x > 1 for x in (p, s, f)):
            raise ValueError("bayes inputs must be in [0,1]")
        den = p * s + (1 - p) * f
        if den == 0:
            raise ValueError("zero evidence probability")
        post = p * s / den
        row = {"name": b.get("name"), "posterior": str(round(post, 6)),
               "per_1000": {"true_positive": str(round(1000 * p * s, 1)),
                            "false_positive": str(round(1000 * (1 - p) * f, 1))}}
        if "stated_posterior" in b:
            st = d(b["stated_posterior"])
            row["stated"] = str(st)
            if abs(st - post) > Decimal("0.05"):
                kind = "base-rate neglect (stated ≈ sensitivity)" if abs(st - s) < Decimal("0.05") else "incorrect posterior"
                issues.append(f"{b.get('name')}: stated {st} vs computed {round(post, 4)} — {kind}")
        bayes.append(row)
    if not issues:
        notes.append("coherent for the submitted numbers; this does not validate the numbers themselves")
    return {"ok": not issues, "issues": issues, "bayes": bayes, "notes": notes}


def main():
    try:
        out = check(json.load(sys.stdin))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
