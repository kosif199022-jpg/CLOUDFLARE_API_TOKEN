#!/usr/bin/env python3
"""Validate structural completeness of a KOSIF Think Pro coverage receipt.
Does not validate truth, quality, model independence, or tool execution.
Reads one JSON object from stdin. Exit 0 = structurally complete; nonzero = incomplete/invalid.
"""
import json, sys

MODULES=[f"M{i:02d}" for i in range(1,29)]
PROFILES=[
    "Skeptic","Strict Verifier","Decisive Operator","Ambitious Optimizer",
    "Creative Explorer","Conservative Risk Guardian","Analytical Decomposer",
    "Adversarial Critic","Naive-Reasoning Simulator","Integrator","Bias Hunter",
    "Constraint Optimizer","Conflict Scout","Evidence Accountant"
]
MODULE_STATES={"relevant","not-material","unavailable"}
PROFILE_STATES={"complete","not-material","unavailable"}

def main():
    try:
        obj=json.load(sys.stdin)
    except Exception as e:
        print(json.dumps({"ok":False,"error":"invalid-json","detail":str(e)}))
        return 2
    modules=obj.get("modules") or {}
    profiles=obj.get("profiles") or {}
    missing_m=[m for m in MODULES if m not in modules]
    invalid_m={m:modules.get(m) for m in MODULES if m in modules and modules.get(m) not in MODULE_STATES}
    missing_p=[p for p in PROFILES if p not in profiles]
    invalid_p={p:profiles.get(p) for p in PROFILES if p in profiles and profiles.get(p) not in PROFILE_STATES}
    ok=not (missing_m or invalid_m or missing_p or invalid_p)
    out={"ok":ok,"missing_modules":missing_m,"invalid_modules":invalid_m,"missing_profiles":missing_p,"invalid_profiles":invalid_p}
    print(json.dumps(out,ensure_ascii=False,sort_keys=True))
    return 0 if ok else 1

if __name__=="__main__":
    raise SystemExit(main())
