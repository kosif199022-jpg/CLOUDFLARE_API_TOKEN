#!/usr/bin/env python3
"""Build a Pro receipt from observed runtime data without fabricating provenance.

The builder produces a pre-execution receipt plus a separate authorization verdict.
It never marks completion ready; final completion is owned by pro_receipt_verify.py
after observable postcondition/delivery evidence.
"""
from __future__ import annotations
import json, sys
from copy import deepcopy
from pro_receipt_verify import MODULES, PROFILES, RECEIPT_EVIDENCE_TYPES

def _observable(cap:dict)->bool:
    if cap.get("receipt_id"):
        return True
    ev=cap.get("receipt_evidence")
    return isinstance(ev,dict) and ev.get("observed") is True and ev.get("type") in RECEIPT_EVIDENCE_TYPES

def _caps(runtime:dict)->list[dict]:
    src=runtime.get("capabilities") or runtime.get("models_tools") or []
    out=[]
    keep={"id","kind","requested","available","used","actual_source","actual_model",
          "fallback_used","fallback_reason","receipt_id","receipt_evidence","limitations"}
    for raw in src:
        if not isinstance(raw,dict): continue
        c={k:deepcopy(v) for k,v in raw.items() if k in keep}
        c.setdefault("requested",False); c.setdefault("available",False); c.setdefault("used",False)
        c.setdefault("fallback_used",False)
        out.append(c)
    return out

def build(runtime:dict, context:dict)->dict:
    runtime=runtime or {}; context=context or {}
    blockers=[]
    request_id=context.get("request_id")
    expected=context.get("expected_request_id")
    runtime_request=runtime.get("request_id")
    if not request_id or not expected or not runtime_request:
        blockers.append("fresh request_id/expected_request_id/runtime request_id are all required")
    elif not (request_id==expected==runtime_request):
        blockers.append("request_id mismatch")

    execution_needed=context.get("execution_needed",True) is True
    contract=context.get("execution_contract")
    contract_ok=isinstance(contract,dict) and bool(contract.get("contract_id")) and bool(contract.get("user_goal"))
    if execution_needed and not contract_ok:
        blockers.append("execution contract missing or incomplete")

    rg=context.get("risk_gate") or {}
    if execution_needed and rg.get("verdict")!="PASS":
        blockers.append(f"risk gate is {rg.get('verdict')!r}, not PASS")

    caps=_caps(runtime)
    if not caps:
        blockers.append("no capability records observed")
    for c in caps:
        if c.get("used"):
            if c.get("available") is not True:
                blockers.append(f"{c.get('id')}: used but unavailable")
            if not _observable(c):
                blockers.append(f"{c.get('id')}: used without observable receipt evidence")
            if not c.get("actual_source"):
                blockers.append(f"{c.get('id')}: missing actual_source")
            if c.get("kind")=="model" and not c.get("actual_model"):
                blockers.append(f"{c.get('id')}: missing actual_model")

    taint=deepcopy(context.get("source_taint") or {"checked":False,"blocked_supports":0})
    if taint.get("checked") is not True:
        blockers.append("source taint was not checked")

    consistency=deepcopy(context.get("consistency") or {"checked":False,"quarantined":[],"evidence_conflict":False})
    if consistency.get("checked") is not True:
        blockers.append("evidence consistency was not checked")

    modules={m:"unavailable" for m in MODULES}
    modules.update({k:v for k,v in (context.get("modules") or {}).items() if k in modules})
    profiles={p:"unavailable" for p in PROFILES}
    profiles.update({k:v for k,v in (context.get("profiles") or {}).items() if k in profiles})

    budget=deepcopy(context.get("budget") or {
      "model_calls_used":0,"max_model_calls":0,"tool_calls_used":0,"max_tool_calls":0,
      "retries_used":0,"max_retries":0,"no_change_count":0,"max_no_change":1,"status":"stopped"
    })
    gates=deepcopy(context.get("gates") or {
      "bias_gate":"revise","optimizer_gate":{"feasible":0},"self_critic":"revise","verifier":"revise"
    })

    receipt={
      "trace_version":"3.0",
      "request_id":request_id,
      "modules":modules,
      "profiles":profiles,
      "models_tools":caps,
      "dissent_ledger":deepcopy(context.get("dissent_ledger") or []),
      "source_taint":taint,
      "evidence_gaps":deepcopy(context.get("evidence_gaps") or []),
      "gates":gates,
      "execution_contract":"present" if contract_ok else ("not-needed" if not execution_needed else "missing"),
      "postcondition":context.get("postcondition") or ("not-verified" if execution_needed else "not-needed"),
      "budget":budget,
      "consistency":consistency,
    }
    if contract_ok:
        receipt["execution_contract_ref"]=deepcopy(contract)
    if "final_answer" in context: receipt["final_answer"]=context["final_answer"]
    if "council" in context: receipt["council"]=deepcopy(context["council"])

    return {
      "request_id":request_id,
      "receipt":receipt,
      "authorization_ready":not blockers,
      "authorization_blockers":blockers,
      "completion_ready":False,
      "completion_rule":"Run pro_receipt_verify.py only after observable executor/postcondition/delivery evidence; builder never grants completion.",
    }

def main():
    try:
        obj=json.load(sys.stdin)
        out=build(obj.get("runtime") or {},obj.get("context") or {})
    except Exception as e:
        print(json.dumps({"authorization_ready":False,"error":str(e)})); return 2
    print(json.dumps(out,ensure_ascii=False,sort_keys=True))
    return 0 if out["authorization_ready"] else 1

if __name__=="__main__": raise SystemExit(main())
