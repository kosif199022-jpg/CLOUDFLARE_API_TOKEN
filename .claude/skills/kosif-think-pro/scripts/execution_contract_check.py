#!/usr/bin/env python3
import json, sys

def check(contract, brief):
    text = brief.lower()
    missing = []
    for term in contract.get("required_terms", []):
        if term.lower() not in text:
            missing.append(term)
    forbidden = []
    for term in contract.get("forbidden_terms", []):
        if term.lower() in text:
            forbidden.append(term)
    ok = not missing and not forbidden
    return {"ok": ok, "missing_required": missing, "forbidden_present": forbidden}

def main():
    if len(sys.argv) != 3:
        print("usage: execution_contract_check.py CONTRACT.json BRIEF.txt", file=sys.stderr)
        return 2
    with open(sys.argv[1], encoding="utf-8") as f:
        contract = json.load(f)
    with open(sys.argv[2], encoding="utf-8") as f:
        brief = f.read()
    result = check(contract, brief)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
