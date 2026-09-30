#!/usr/bin/env python3
"""KOSIF calibration linter — do certainty words match the evidence? (v3.2)

Grounded in references/inference-and-comprehension.md (evidence ladder; hedging
language from the Outcomes "In the picture" lesson). Heuristic, deterministic.

stdin JSON: {"claims": [{"text": "He must be French", "evidence": [
                {"type": "observation", "source": "sign in photo"}]}, ...]}
evidence types: observation | measurement | quote | inference | assumption.
Independent = distinct `source` values among observation/measurement/quote.
"""
import json
import re
import sys

STRONG = r"\b(must|certainly|definitely|clearly|obviously|undoubtedly|without doubt|proves?|always|never|بالتأكيد|قطعا|قطعاً|حتما|حتماً|بلا شك|من الواضح)\b"
PROBABLE = r"\b(probably|likely|could well|looks like|looks as if|seems|appears|يبدو|غالبا|غالباً|على الأرجح|من المرجح)\b"
POSSIBLE = r"\b(might|may|could|perhaps|possibly|i get the impression|ربما|قد|من الممكن|يحتمل)\b"
DIRECT = {"observation", "measurement", "quote"}


def level(text):
    t = text.lower()
    if re.search(STRONG, t):
        return "strong"
    if re.search(PROBABLE, t):
        return "probable"
    if re.search(POSSIBLE, t):
        return "possible"
    return "plain"


def check(o):
    rows, issues = [], []
    for i, c in enumerate(o.get("claims", [])):
        text = str(c.get("text", ""))
        ev = c.get("evidence") or []
        direct = {e.get("source") or f"e{j}" for j, e in enumerate(ev) if e.get("type") in DIRECT}
        only_assumed = ev and all(e.get("type") == "assumption" for e in ev)
        lv = level(text)
        verdict = "ok"
        if lv == "strong" and len(direct) < 2:
            verdict = "overclaim: strong wording needs ≥2 independent direct observations"
        elif lv in ("plain", "probable") and not ev:
            verdict = "unsupported: add evidence or hedge as possible/assumption"
        elif lv == "plain" and only_assumed:
            verdict = "assumption stated as fact: mark it 'assuming …'"
        elif lv == "plain" and not direct:
            verdict = "inference stated as fact: hedge it (probably/seems)"
        elif lv in ("possible",) and len(direct) >= 2:
            verdict = "underclaim: two independent observations support a firmer statement"
        rows.append({"claim": text, "level": lv, "independent_direct_evidence": len(direct), "verdict": verdict})
        if verdict != "ok":
            issues.append(f"claim {i + 1}: {verdict}")
    return {"ok": not issues, "issues": issues, "claims": rows}


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
