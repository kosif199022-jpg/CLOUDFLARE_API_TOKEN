#!/usr/bin/env python3
"""Deterministic checks; input evidence truth is outside this helper."""
import json, sys
from decimal import Decimal, InvalidOperation
def number(x):
    if not isinstance(x, (str,int)) or isinstance(x,bool):
        raise ValueError("numbers must be decimal strings or integers")
    d=Decimal(x)
    if not d.is_finite(): raise ValueError("non-finite number")
    return d
def verify(x):
    if x["operation"]=="bayes":
        p,s,f=(number(x[k]) for k in ("prior","sensitivity","false_positive_rate"))
        if any(v<0 or v>1 for v in (p,s,f)): raise ValueError("probability outside [0,1]")
        den=p*s+(1-p)*f
        if den==0: raise ValueError("zero evidence probability")
        return {"posterior":str(p*s/den),"numerator":str(p*s),"denominator":str(den)}
    if x["operation"]!="select": raise ValueError("unknown operation")
    if x["objective"] not in ("min","max"): raise ValueError("objective must be min or max")
    constraints=x["constraints"]; options=x["options"]
    ids=[o["id"] for o in options]
    if any(not isinstance(i,str) or not i for i in ids) or len(set(ids))!=len(ids): raise ValueError("invalid or duplicate option id")
    for c in constraints.values():
        if not isinstance(c.get("unit"),str) or not c["unit"]: raise ValueError("constraint unit required")
        if "min" not in c and "max" not in c: raise ValueError("constraint bound required")
        if "min" in c and "max" in c and number(c["min"])>number(c["max"]): raise ValueError("inverted bounds")
        for k in ("min","max"):
            if k in c: number(c[k])
    rows=[]; feasible=[]
    for o in options:
        score=number(o["objective"]); failures=[]; unknown=[]
        for key,c in constraints.items():
            m=o.get("measurements",{}).get(key)
            if not m or m.get("unit")!=c["unit"] or "value" not in m:
                unknown.append(key); continue
            v=number(m["value"])
            if ("min" in c and v<number(c["min"])) or ("max" in c and v>number(c["max"])): failures.append(key)
        status="rejected" if failures else "pending" if unknown else "feasible"
        rows.append({"id":o["id"],"status":status,"failed":failures,"unknown":unknown})
        if status=="feasible": feasible.append((o["id"],score))
    winners=[]
    if feasible:
        best=(min if x["objective"]=="min" else max)(v for _,v in feasible)
        winners=[i for i,v in feasible if v==best]
    return {"options":rows,"winners":winners,"scope":"submitted candidates and measurements"}
if __name__=="__main__":
    try: print(json.dumps(verify(json.load(sys.stdin))))
    except (ValueError,KeyError,TypeError,InvalidOperation) as e:
        print(json.dumps({"error":str(e)})); sys.exit(2)

