#!/usr/bin/env python3
"""Validate whether source statuses are allowed to support material claims."""
import json, sys
BLOCKED={"quarantined","mixed","advertisement","testbank","unreadable","unverified"}

def validate(obj):
    claims={c.get("id"):c for c in obj.get("claims",[]) if c.get("id")}
    valid_support={cid:[] for cid in claims}
    invalid=[]
    for s in obj.get("sources",[]):
        sid=s.get("id") or "<unknown>"; status=s.get("status")
        for cid in s.get("supports",[]) or []:
            if cid not in claims: invalid.append({"source":sid,"claim":cid,"reason":"unknown-claim"}); continue
            claim=claims[cid]
            if status in BLOCKED:
                invalid.append({"source":sid,"claim":cid,"reason":f"blocked-status:{status}"}); continue
            if status=="historical" and claim.get("current_authority"):
                invalid.append({"source":sid,"claim":cid,"reason":"historical-cannot-establish-current-authority"}); continue
            valid_support[cid].append(sid)
    unsupported=[cid for cid,c in claims.items() if c.get("requires_source",True) and not valid_support[cid]]
    return {"ok":not invalid and not unsupported,"invalid_support":invalid,"unsupported_claims":unsupported,"valid_support":valid_support}

def main():
    try: obj=json.load(sys.stdin)
    except Exception as e: print(json.dumps({"ok":False,"error":str(e)})); return 2
    out=validate(obj); print(json.dumps(out,ensure_ascii=False,sort_keys=True)); return 0 if out["ok"] else 1
if __name__=="__main__": raise SystemExit(main())
