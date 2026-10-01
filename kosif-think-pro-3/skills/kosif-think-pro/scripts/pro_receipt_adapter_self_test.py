#!/usr/bin/env python3
import copy,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; sys.path.insert(0,str(HERE))
from pro_receipt_builder import build_pre_execution, finalize_receipt, MODULES, PROFILES
from pro_receipt_verify import validate

def payload():
    return {
        "request_id":"req-current","trace_version":"3.1",
        "runtime_receipts":[{"id":"gpt","kind":"model","actual_source":"cleanapis","actual_model":"gpt-5.6-sol","observed_request_id":"req-current","native_request_binding":False,
            "receipt":{"receiptId":"runtime-r1","engineVersion":"0.8.3","tool":"kosif_agent","generatedAt":"2026-09-30T19:00:00Z","integrity":{"signed":False,"type":"trace-correlation-digest","digest":"abc123"}}}],
        "modules":{m:"relevant" for m in MODULES},"profiles":{p:"complete" for p in PROFILES},
        "dissent_ledger":[{"profile":p,"conclusion":"proceed","strongest_objection":"none material","disposition":"accepted","what_would_change_it":"new contradictory evidence"} for p in PROFILES],
        "source_taint":{"checked":True,"blocked_supports":0},"evidence_gaps":[],
        "gates":{"bias_gate":"pass","optimizer_gate":{"feasible":1},"self_critic":"pass","verifier":"pass"},
        "execution_contract":{"request_id":"req-current","contract_id":"contract-1","user_goal":"generate image","executor_type":"image-generator"},
        "budget":{"model_calls_used":5,"max_model_calls":10,"tool_calls_used":7,"max_tool_calls":20,"retries_used":0,"max_retries":3,"no_change_count":0,"max_no_change":2,"status":"completed"},
        "consistency":{"checked":True,"quarantined":[],"evidence_conflict":False},"artifact_expected":True,
    }

def main():
    results=[]
    def check(n,c): results.append((n,bool(c)))
    pre=build_pre_execution(payload()); v=validate(pre)
    check("0.8.3-runtime-adapts-to-modern-pro",v["structurally_valid"])
    check("pre-execution-is-authorization-ready",v["authorization_ready"])
    check("pre-execution-is-not-completion-ready",not v["completion_ready"])
    check("runtime-version-remains-0.8.3",pre["runtime_compat"]["runtime_engine_versions"]==["0.8.3"])
    check("trace-version-remains-separate",pre["runtime_compat"]["pro_trace_version"]=="3.1")
    check("unsigned-digest-not-upgraded",pre["runtime_compat"]["cryptographic_provenance"] is False)
    final=finalize_receipt(pre,{"request_id":"req-current","observed":True,"evidence_type":"host-artifact-reference","reference":"artifact://image-123"},"pass")
    check("final-artifact-completion-ready",validate(final)["completion_ready"])
    bad=payload(); bad["runtime_receipts"][0]["observed_request_id"]="req-old"
    try: build_pre_execution(bad); ok=False
    except ValueError: ok=True
    check("mismatched-request-blocked",ok)
    stale=payload(); stale["runtime_receipts"][0]["reused_prior_receipt"]=True
    try: build_pre_execution(stale); ok=False
    except ValueError: ok=True
    check("stale-receipt-blocked",ok)
    obs=payload(); obs["runtime_receipts"][0]["receipt"].pop("receiptId"); obs["runtime_receipts"][0]["host_observation"]={"observed":True,"type":"host-tool-result","observation_id":"obs-1","result_digest":"sha256:abc"}
    check("host-observation-without-native-receipt-accepted",validate(build_pre_execution(obs))["authorization_ready"])
    fake=copy.deepcopy(pre); fake["artifact_delivery"]["verified"]=True; fake["artifact_delivery"]["reference"]="artifact://fabricated"
    check("preverified-artifact-blocked",not validate(fake)["structurally_valid"])
    failed=[n for n,ok in results if not ok]
    print(json.dumps({"ok":not failed,"passed":sum(1 for _,ok in results if ok),"failed":failed,"tests":[{"name":n,"ok":ok} for n,ok in results]},ensure_ascii=False,sort_keys=True)); return 0 if not failed else 1

if __name__=="__main__": raise SystemExit(main())
