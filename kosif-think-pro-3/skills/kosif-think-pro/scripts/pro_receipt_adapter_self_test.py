#!/usr/bin/env python3
import json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from pro_receipt_builder import build
from pro_receipt_verify import validate

def runtime(observed=True):
    cap={"id":"kosif-gpt","kind":"model","requested":True,"available":True,"used":True,
         "actual_source":"cleanapis","actual_model":"gpt-5.6-sol","fallback_used":False}
    if observed:
        cap["receipt_evidence"]={"type":"host-tool-result","observed":True,"limitation":"no native receipt id"}
    else:
        cap["receipt_evidence"]={"type":"server-advertised","observed":False}
    return {"request_id":"req-1","capabilities":[cap]}

def context():
    return {
      "request_id":"req-1","expected_request_id":"req-1","execution_needed":True,
      "execution_contract":{"contract_id":"c1","user_goal":"send verified artifact"},
      "risk_gate":{"verdict":"PASS"},
      "source_taint":{"checked":True,"blocked_supports":0},
      "consistency":{"checked":True,"quarantined":[],"evidence_conflict":False},
      "gates":{"bias_gate":"pass","optimizer_gate":{"feasible":1},"self_critic":"pass","verifier":"pass"},
      "budget":{"model_calls_used":1,"max_model_calls":10,"tool_calls_used":1,"max_tool_calls":10,
                "retries_used":0,"max_retries":2,"no_change_count":0,"max_no_change":2,"status":"stopped"}
    }

def run():
    tests=[]
    def check(n,c): tests.append((n,bool(c)))

    b=build(runtime(True),context())
    check("authorization-ready-with-observed-evidence",b["authorization_ready"] is True)
    check("builder-never-completion-ready",b["completion_ready"] is False)
    check("no-fabricated-receipt-id","receipt_id" not in b["receipt"]["models_tools"][0])
    check("preserves-model-provenance",b["receipt"]["models_tools"][0]["actual_model"]=="gpt-5.6-sol")
    v=validate(b["receipt"])
    check("built-receipt-structurally-valid",v["structurally_valid"] is True)
    check("preexecution-not-complete",v["completion_ready"] is False)

    c=context(); c["expected_request_id"]="req-other"
    check("request-mismatch-blocks",build(runtime(True),c)["authorization_ready"] is False)

    b2=build(runtime(False),context())
    check("unobserved-capability-blocks",b2["authorization_ready"] is False)
    check("server-advertised-not-receipt",any("observable receipt" in x for x in b2["authorization_blockers"]))

    c=context(); c["risk_gate"]={"verdict":"VERIFY"}
    check("risk-not-pass-blocks",build(runtime(True),c)["authorization_ready"] is False)

    c=context(); c.pop("execution_contract")
    check("missing-contract-blocks",build(runtime(True),c)["authorization_ready"] is False)

    failed=[n for n,c in tests if not c]
    print(json.dumps({"ok":not failed,"passed":sum(c for _,c in tests),"total":len(tests),"failed":failed},sort_keys=True))
    return 0 if not failed else 1
if __name__=="__main__": raise SystemExit(run())
