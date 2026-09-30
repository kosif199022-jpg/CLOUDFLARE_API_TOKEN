#!/usr/bin/env python3
"""KOSIF Ledger Check — deterministic accounting controls (v3.1).

Grounded in the supplied "AI-Powered Accounting Skill — IFRS/ISA Expanded Report"
(read in full): integer minor units (halala) instead of floats, debits = credits,
valid accounts, open period, tax = base × rate under declared rounding, idempotency,
logical event keys to prevent duplicates, invoice ↔ bank settlement matching, and
"a bank movement is not revenue merely because it appears in the bank".

stdin JSON:
{"currency_minor_units": 2, "vat_rate": "0.15", "rounding": "half_up",
 "chart": ["1101", "1201", "2201", "4101", "6101"],
 "revenue_accounts": ["4101"], "bank_accounts": ["1101"],
 "period": {"start": "2026-09-01", "end": "2026-09-30", "status": "open"},
 "entries": [{"id": "JE1", "date": "2026-09-03", "source": "INV-104", "event_key": "INV-104|NOUR|1150.00|SAR",
              "lines": [{"account": "1201", "debit": "1150.00"}, {"account": "4101", "credit": "1000.00"},
                        {"account": "2201", "credit": "150.00"}],
              "tax": {"base": "1000.00", "amount": "150.00"}}],
 "invoices": [{"id": "INV-104", "party": "NOUR", "total": "1150.00", "date": "2026-09-03"}],
 "bank": [{"id": "B1", "party": "NOUR", "amount": "1150.00", "date": "2026-09-05", "ref": "INV-104"}]}
"""
import json
import sys
from datetime import date
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal


def minor(x, units):
    v = Decimal(str(x))
    q = v * (10 ** units)
    if q != q.to_integral_value():
        raise ValueError(f"amount {x} has more than {units} decimals")
    return int(q)


def check(o):
    units = int(o.get("currency_minor_units", 2))
    rate = Decimal(str(o.get("vat_rate", "0")))
    rmode = ROUND_HALF_EVEN if o.get("rounding") == "half_even" else ROUND_HALF_UP
    chart = set(map(str, o.get("chart", [])))
    revenue = set(map(str, o.get("revenue_accounts", [])))
    banks = set(map(str, o.get("bank_accounts", [])))
    per = o.get("period") or {}
    p0 = date.fromisoformat(per["start"]) if per.get("start") else None
    p1 = date.fromisoformat(per["end"]) if per.get("end") else None
    issues, results = [], []
    seen_ids, seen_keys = set(), {}
    for e in o.get("entries", []):
        eid = e.get("id", "?")
        row = {"id": eid, "problems": []}
        if eid in seen_ids:
            row["problems"].append("duplicate entry id (idempotency)")
        seen_ids.add(eid)
        k = e.get("event_key")
        if k:
            if k in seen_keys:
                row["problems"].append(f"same economic event already booked in {seen_keys[k]}")
            else:
                seen_keys[k] = eid
        dr = cr = 0
        for ln in e.get("lines", []):
            acc = str(ln.get("account"))
            if chart and acc not in chart:
                row["problems"].append(f"account {acc} not in chart")
            try:
                d_, c_ = minor(ln.get("debit", 0), units), minor(ln.get("credit", 0), units)
            except (ValueError, ArithmeticError) as ex:
                row["problems"].append(f"line {acc}: {ex}")
                continue
            if d_ < 0 or c_ < 0 or (d_ and c_):
                row["problems"].append(f"line {acc}: debit/credit must be one non-negative side")
            dr += d_
            cr += c_
        if dr != cr:
            row["problems"].append(f"unbalanced: debit {dr} vs credit {cr} (minor units)")
        if dr == 0 and cr == 0:
            row["problems"].append("empty entry")
        if e.get("date") and p0 and p1:
            d0 = date.fromisoformat(e["date"])
            if not (p0 <= d0 <= p1):
                row["problems"].append("date outside the declared period")
        if per.get("status") and per["status"] != "open":
            row["problems"].append(f"period is {per['status']}: posting not allowed")
        t = e.get("tax")
        if t:
            expect = (Decimal(str(t["base"])) * rate).quantize(Decimal(1).scaleb(-units), rounding=rmode)
            if minor(t["amount"], units) != minor(expect, units):
                row["problems"].append(f"tax {t['amount']} ≠ base × rate = {expect}")
        credits_rev = any(str(ln.get("account")) in revenue and ln.get("credit") for ln in e.get("lines", []))
        debits_bank = any(str(ln.get("account")) in banks and ln.get("debit") for ln in e.get("lines", []))
        if credits_rev and debits_bank and not e.get("source_is_cash_sale"):
            row["problems"].append("bank receipt credited directly to revenue: settle the receivable unless it is a documented cash sale")
        row["balanced"] = dr == cr
        results.append(row)
        issues += [f"{eid}: {p}" for p in row["problems"]]
    # invoice ↔ bank matching
    matches, unmatched = [], []
    inv = {i["id"]: i for i in o.get("invoices", [])}
    open_bal = {i: minor(v["total"], units) for i, v in inv.items()}
    for b in o.get("bank", []):
        amt = minor(b["amount"], units)
        cand = inv.get(b.get("ref")) or next((v for v in inv.values() if v.get("party") == b.get("party")
                                              and open_bal[v["id"]] == amt), None)
        if not cand:
            unmatched.append({"bank": b["id"], "reason": "no invoice reference or same-party equal amount; ask before booking"})
            continue
        diff = open_bal[cand["id"]] - amt
        open_bal[cand["id"]] = max(0, diff)
        status = "full" if diff == 0 else "partial" if diff > 0 else "overpayment"
        matches.append({"bank": b["id"], "invoice": cand["id"], "status": status,
                        "difference_minor": diff, "treatment": "Dr bank / Cr receivable (not revenue)"})
    return {"ok": not issues, "issues": issues, "entries": results, "matches": matches,
            "unmatched_bank_lines": unmatched,
            "open_invoice_balances_minor": {k: v for k, v in open_bal.items() if v},
            "scope": "deterministic controls only; classification and IFRS judgement need an authorised reviewer"}


def main():
    try:
        out = check(json.load(sys.stdin))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
