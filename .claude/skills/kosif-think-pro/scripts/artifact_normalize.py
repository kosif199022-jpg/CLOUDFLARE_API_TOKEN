#!/usr/bin/env python3
"""Normalize micro-agent / Council artifacts into the canonical KOSIF schema v3.0.

Canonical artifact:
{"agent", "conclusion", "evidence": [], "risks": [], "objections": [],
 "assumptions": [], "confidence": null|number 0..1, "disposition": null|str}

Deterministic only: alias keys are merged, strings are coerced to lists, items
explicitly prefixed "Risk:", "Objection:", "Evidence:" or "Assumption:" (Arabic
prefixes too) are moved to their correct field, duplicates are removed.
Every change is reported so nothing is silently rewritten.
Reads one artifact or a list of artifacts from stdin.
"""
import json
import re
import sys

LIST_FIELDS = ("evidence", "risks", "objections", "assumptions")
ALIASES = {
    "agent": ("agent", "profile", "role", "name", "model"),
    "conclusion": ("conclusion", "answer", "result", "verdict", "summary", "final", "recommendation"),
    "evidence": ("evidence", "sources", "support", "supports", "proof", "citations", "facts", "الأدلة", "أدلة"),
    "risks": ("risks", "risk", "concerns", "dangers", "hazards", "المخاطر", "مخاطر"),
    "objections": ("objections", "objection", "counterarguments", "counterpoints", "critique", "criticism",
                   "strongest_objection", "الاعتراضات", "اعتراضات"),
    "assumptions": ("assumptions", "assumption", "premises", "الافتراضات", "افتراضات"),
    "confidence": ("confidence", "certainty", "probability", "الثقة"),
    "disposition": ("disposition", "status", "decision"),
}
PREFIX = {
    "risks": re.compile(r"^\s*(risk|concern|خطر|مخاطرة)\s*[:：\-]\s*", re.I),
    "objections": re.compile(r"^\s*(objection|counter(point|argument)?|اعتراض)\s*[:：\-]\s*", re.I),
    "evidence": re.compile(r"^\s*(evidence|source|proof|دليل|مصدر)\s*[:：\-]\s*", re.I),
    "assumptions": re.compile(r"^\s*(assumption|assume|افتراض)\s*[:：\-]\s*", re.I),
}


def as_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return [x for x in v if x not in (None, "", [])]
    if isinstance(v, str):
        parts = [p.strip(" -•*\t") for p in re.split(r"\n+|;\s*", v)]
        return [p for p in parts if p]
    return [v]


def conf(v, changes):
    if v is None:
        return None
    try:
        s = str(v).strip()
        x = float(s[:-1]) / 100 if s.endswith("%") else float(s)
    except ValueError:
        changes.append(f"confidence {v!r} is not numeric -> null")
        return None
    if 1 < x <= 100:
        changes.append(f"confidence {v!r} rescaled to {x / 100}")
        x = x / 100
    if not 0 <= x <= 1:
        changes.append(f"confidence {v!r} out of range -> null")
        return None
    return x


def normalize(a):
    if not isinstance(a, dict):
        raise ValueError("artifact must be an object")
    changes, out, used = [], {f: [] for f in LIST_FIELDS}, set()
    lower = {str(k).lower(): k for k in a}
    for field, names in ALIASES.items():
        for n in names:
            k = lower.get(n.lower())
            if k is None:
                continue
            used.add(k)
            if k != field:
                changes.append(f"alias '{k}' -> '{field}'")
            if field in LIST_FIELDS:
                out[field] += as_list(a[k])
            elif field not in out or out[field] in (None, ""):
                out[field] = a[k]
    # move explicitly prefixed items to the right list
    for src in LIST_FIELDS:
        keep = []
        for item in out[src]:
            moved = False
            if isinstance(item, str):
                for dst, rx in PREFIX.items():
                    if dst != src and rx.match(item):
                        out[dst].append(rx.sub("", item, count=1))
                        changes.append(f"moved item from {src} to {dst}: {item[:60]}")
                        moved = True
                        break
            if not moved:
                keep.append(item)
        out[src] = keep
    for f in LIST_FIELDS:
        seen, uniq = set(), []
        for x in out[f]:
            key = json.dumps(x, sort_keys=True, ensure_ascii=False)
            if key not in seen:
                seen.add(key)
                uniq.append(x)
        if len(uniq) != len(out[f]):
            changes.append(f"removed {len(out[f]) - len(uniq)} duplicate(s) in {f}")
        out[f] = uniq
    out.setdefault("agent", None)
    out.setdefault("conclusion", None)
    out["confidence"] = conf(out.get("confidence"), changes)
    out.setdefault("disposition", None)
    extra = {k: a[k] for k in a if k not in used}
    if extra:
        out["extra"] = extra
        changes.append(f"unmapped keys kept under extra: {sorted(extra)}")
    issues = []
    if not out["conclusion"]:
        issues.append("missing conclusion")
    if not out["evidence"]:
        issues.append("no evidence recorded")
    return {"artifact": out, "changes": changes, "issues": issues}


def main():
    try:
        data = json.load(sys.stdin)
        items = data if isinstance(data, list) else [data]
        res = [normalize(x) for x in items]
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    ok = all(not r["issues"] for r in res)
    print(json.dumps({"ok": ok, "results": res}, ensure_ascii=False, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
