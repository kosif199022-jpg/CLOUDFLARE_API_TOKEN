#!/usr/bin/env python3
"""KOSIF typed evidence/answer consistency gate v3.0.

Generalizes the v0.8.3 arithmetic quarantine into typed deterministic validators.
It checks internal consistency of submitted evidence only; it never proves that
the evidence itself is true.

Input (stdin JSON):
{
  "tolerance": "0.000001",                      # optional, absolute
  "evidence": [
    {"id": "e1", "source": "gpt",  "type": "arithmetic", "expression": "120 - 120*15% - 10", "claimed": "92"},
    {"id": "e2", "source": "claude", "type": "arithmetic", "expression": "(120 - 18) - 10"},
    {"id": "e3", "source": "calc", "type": "sum", "parts": ["18", "102"], "total": "120"},
    {"id": "e4", "source": "calc", "type": "percent", "part": "18", "whole": "120", "percent": "15"},
    {"id": "e5", "source": "calc", "type": "range", "value": "92", "min": "0", "max": "120"},
    {"id": "e6", "source": "calc", "type": "ratio", "numerator": "3", "denominator": "4", "ratio": "0.75"},
    {"id": "e7", "source": "calc", "type": "date_order", "dates": ["2026-01-01", "2026-03-31"]},
    {"id": "e8", "source": "calc", "type": "unit", "units": ["kg", "kg"]}
  ],
  "answers": [{"id": "a1", "source": "gpt", "value": "97"}, {"id": "a2", "source": "jev", "value": "92"}]
}

Output: per-evidence validity, the converged value (a valid arithmetic result
repeated by >=2 independent sources), quarantined answers, and a provisional
repair when every numeric answer was quarantined.
Exit 0 = consistent; 1 = defects/quarantine; 2 = invalid input.
"""
import ast
import json
import operator
import sys
from datetime import date
from decimal import Decimal, InvalidOperation, getcontext

getcontext().prec = 40

_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Mod: operator.mod, ast.Pow: operator.pow}
_UN = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def num(x):
    if isinstance(x, bool) or not isinstance(x, (str, int, float)):
        raise ValueError("numbers must be decimal strings or numbers")
    s = str(x).strip().replace(",", "").replace("٬", "")
    pct = s.endswith("%")
    d = Decimal(s[:-1] if pct else s)
    if not d.is_finite():
        raise ValueError("non-finite number")
    return d / 100 if pct else d


def safe_eval(expr):
    """Evaluate + - * / % ** and parentheses on Decimals. `15%` means 0.15."""
    if not isinstance(expr, str) or len(expr) > 500:
        raise ValueError("expression must be a string of <=500 chars")
    src = expr.replace("×", "*").replace("÷", "/").replace("−", "-").replace(",", "")
    # turn "15%" into "(15/100)" while keeping modulo "a % b"
    out, i = [], 0
    while i < len(src):
        ch = src[i]
        if ch == "%":
            j = i + 1
            while j < len(src) and src[j] == " ":
                j += 1
            nxt = src[j] if j < len(src) else ""
            if nxt == "" or nxt in "+-*/)":
                k = len(out)
                while k > 0 and (out[k - 1].isdigit() or out[k - 1] == "."):
                    k -= 1
                out[k:] = ["(", *out[k:], "/100)"]
                i += 1
                continue
        out.append(ch)
        i += 1
    tree = ast.parse("".join(out), mode="eval")

    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
            return Decimal(str(n.value))
        if isinstance(n, ast.BinOp) and type(n.op) in _BIN:
            a, b = ev(n.left), ev(n.right)
            if isinstance(n.op, (ast.Div, ast.Mod)) and b == 0:
                raise ValueError("division by zero")
            if isinstance(n.op, ast.Pow) and (abs(b) > 64 or b != b.to_integral_value()):
                raise ValueError("only small integer powers allowed")
            return _BIN[type(n.op)](a, b)
        if isinstance(n, ast.UnaryOp) and type(n.op) in _UN:
            return _UN[type(n.op)](ev(n.operand))
        raise ValueError(f"unsupported syntax: {type(n).__name__}")

    return ev(tree)


def close(a, b, tol):
    return abs(a - b) <= tol


def norm(d):
    s = format(d.normalize(), "f")
    return s if "." not in s else s.rstrip("0").rstrip(".") or "0"


def check_item(e, tol):
    t = e.get("type", "arithmetic")
    if t == "arithmetic":
        v = safe_eval(e["expression"])
        ok = "claimed" not in e or close(v, num(e["claimed"]), tol)
        return ok, v, None if ok else f"claimed {e['claimed']} but expression gives {norm(v)}"
    if t == "sum":
        s = sum((num(p) for p in e["parts"]), Decimal(0))
        ok = close(s, num(e["total"]), tol)
        return ok, None, None if ok else f"parts sum to {norm(s)}, not {e['total']}"
    if t == "percent":
        whole = num(e["whole"])
        if whole == 0:
            raise ValueError("whole is zero")
        p = num(e["part"]) / whole * 100
        ok = close(p, num(e["percent"]), max(tol, Decimal("0.01")))
        return ok, None, None if ok else f"part/whole = {norm(p)}%, not {e['percent']}%"
    if t == "ratio":
        den = num(e["denominator"])
        if den == 0:
            raise ValueError("denominator is zero")
        r = num(e["numerator"]) / den
        ok = close(r, num(e["ratio"]), max(tol, Decimal("0.0001")))
        return ok, None, None if ok else f"ratio = {norm(r)}, not {e['ratio']}"
    if t == "range":
        v = num(e["value"])
        lo = num(e["min"]) if "min" in e else None
        hi = num(e["max"]) if "max" in e else None
        ok = (lo is None or v >= lo) and (hi is None or v <= hi)
        return ok, None, None if ok else f"{e['value']} outside [{e.get('min', '-inf')}, {e.get('max', 'inf')}]"
    if t == "date_order":
        ds = [date.fromisoformat(x) for x in e["dates"]]
        ok = all(a <= b for a, b in zip(ds, ds[1:]))
        return ok, None, None if ok else "dates are not in chronological order"
    if t == "unit":
        units = [str(u).strip().lower() for u in e["units"]]
        ok = len(set(units)) <= 1
        return ok, None, None if ok else f"mixed units: {sorted(set(units))}"
    raise ValueError(f"unknown evidence type {t}")


def validate(obj):
    tol = num(obj.get("tolerance", "0.000001"))
    rows, defects, results = [], [], {}
    for i, e in enumerate(obj.get("evidence") or []):
        eid = e.get("id") or f"e{i + 1}"
        try:
            ok, val, why = check_item(e, tol)
        except (ValueError, KeyError, TypeError, InvalidOperation, SyntaxError) as ex:
            ok, val, why = False, None, f"invalid: {ex}"
        rows.append({"id": eid, "source": e.get("source"), "type": e.get("type", "arithmetic"),
                     "valid": ok, "value": None if val is None else norm(val), "reason": why})
        if not ok:
            defects.append(f"{eid}: {why}")
        elif val is not None:
            results.setdefault(norm(val), set()).add(e.get("source") or eid)

    converged = [v for v, srcs in results.items() if len(srcs) >= 2]
    conflict = len(converged) > 1
    target = Decimal(converged[0]) if len(converged) == 1 else None

    quarantined, accepted = [], []
    for i, a in enumerate(obj.get("answers") or []):
        aid = a.get("id") or f"a{i + 1}"
        try:
            v = num(a["value"])
        except (ValueError, KeyError, TypeError, InvalidOperation):
            quarantined.append({"id": aid, "value": a.get("value"), "reason": "non-numeric answer"})
            continue
        if target is not None and not close(v, target, tol):
            quarantined.append({"id": aid, "value": norm(v), "reason": f"contradicts converged evidence {norm(target)}"})
        else:
            accepted.append({"id": aid, "value": norm(v)})

    repair = None
    if target is not None and obj.get("answers") and not accepted:
        repair = {"value": norm(target), "status": "provisional", "confidence": "discarded",
                  "note": "every answer contradicted independently repeated deterministic evidence"}
    if conflict:
        defects.append(f"independent evidence converges on multiple values {converged}: escalate")
    return {"ok": not defects and not quarantined, "evidence": rows,
            "converged_value": None if target is None else norm(target),
            "evidence_conflict": conflict, "quarantined_answers": quarantined,
            "accepted_answers": accepted, "provisional_repair": repair, "defects": defects,
            "scope": "internal consistency of submitted evidence; not proof of truth"}


def main():
    try:
        obj = json.load(sys.stdin)
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "defects": [f"invalid-json: {e}"]}))
        return 2
    out = validate(obj)
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
