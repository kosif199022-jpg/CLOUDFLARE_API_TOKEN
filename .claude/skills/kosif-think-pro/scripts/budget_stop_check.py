#!/usr/bin/env python3
"""Bounded Pro execution controller. Purely advisory/deterministic; does not cancel host calls itself."""
import json, sys

def decide(o):
    if o.get("safety_block"): return {"action":"stop","reason":"safety_block"}
    hard=[("model_calls", "max_model_calls"),("tool_calls","max_tool_calls"),("retries","max_retries"),("elapsed_seconds","max_elapsed_seconds")]
    for used,limit in hard:
        if isinstance(o.get(used), (int,float)) and isinstance(o.get(limit),(int,float)) and o[used] >= o[limit]:
            return {"action":"stop","reason":f"budget:{used}"}
    if isinstance(o.get("no_change_count"),int) and isinstance(o.get("max_no_change"),int) and o["no_change_count"]>=o["max_no_change"]:
        return {"action":"escalate","reason":"repeated_no_change"}
    return {"action":"continue","reason":"within_budget"}

def main():
    try:o=json.load(sys.stdin)
    except Exception as e: print(json.dumps({"action":"stop","reason":f"invalid-json:{e}"})); return 2
    out=decide(o); print(json.dumps(out,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
