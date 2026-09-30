#!/usr/bin/env python3
"""Compare baseline vs candidate metrics without collapsing them into one IQ score."""
import json, sys

def evaluate(o):
    base=o.get("baseline") or {}; cand=o.get("candidate") or {}; crit=o.get("criteria") or {}
    issues=[]; results={}; improved=False
    for name,c in crit.items():
        if name not in base or name not in cand:
            if c.get("required",True): issues.append(f"missing metric {name}")
            continue
        b=float(base[name]); v=float(cand[name]); direction=c.get("direction")
        if direction not in {"higher","lower"}: issues.append(f"invalid direction {name}"); continue
        improvement=(v-b) if direction=="higher" else (b-v)
        max_reg=float(c.get("max_regression",0))
        if improvement < -max_reg: issues.append(f"regression {name}: {improvement}")
        if improvement > float(c.get("min_improvement",0)): improved=True
        results[name]={"baseline":b,"candidate":v,"improvement":improvement}
    if o.get("require_any_improvement",True) and not improved: issues.append("no required metric improved")
    return {"ok":not issues,"issues":issues,"metrics":results}

def main():
    try:o=json.load(sys.stdin)
    except Exception as e: print(json.dumps({"ok":False,"issues":[str(e)]})); return 2
    out=evaluate(o); print(json.dumps(out,sort_keys=True)); return 0 if out["ok"] else 1
if __name__=="__main__": raise SystemExit(main())
