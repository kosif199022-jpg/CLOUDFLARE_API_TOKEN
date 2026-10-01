#!/usr/bin/env python3
"""Regression tests for KOSIF Think Pro 3.3 visual reliability additions."""
from __future__ import annotations
import importlib.util
import json
import pathlib
import subprocess
import sys

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[1]
VISUAL=ROOT / "kosif-image-studio" / "scripts" / "visual_contract.py"
INDEP=HERE / "council_independence.py"
BUILDER=HERE / "pro_receipt_builder.py"
VERIFY=HERE / "pro_receipt_verify.py"


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod


def run_json(path,args,payload):
    p=subprocess.run([sys.executable,str(path),*args],input=json.dumps(payload),text=True,capture_output=True)
    try: out=json.loads(p.stdout)
    except Exception: out={"ok":False,"raw":p.stdout,"stderr":p.stderr}
    return p.returncode,out


def assert_true(cond,name,results):
    results.append({"name":name,"ok":bool(cond)})


def main():
    results=[]
    vc=load(VISUAL,"visual_contract")
    pb=load(BUILDER,"pro_receipt_builder")
    pv=load(VERIFY,"pro_receipt_verify")

    built=vc.build({
        "request_id":"req-v33","goal":"duck fights dragon in rain",
        "required":["natural duck","dragon","torrential rain"],
        "forbidden":["armor","sword","text"],
        "locks":{"subject":"natural white duck versus dragon","camera":"low-angle 24mm","weather":"directional torrential rain"},
        "attention_budget":["duck","dragon","confrontation"],
        "physics_checks":["rain creates splashes and puddle ripples"],
        "success_criteria":["duck remains visually readable"],
    })
    assert_true(built["ok"] and built["contract"]["max_repairs"]==1,"build_contract",results)
    assert_true("REQUEST BINDING" in built["compiled_prompt"] and "armor" in built["negative_prompt"],"compiled_prompt_binding",results)

    drift=vc.verify({"contract":built["contract"],"observed":{
        "request_id":"req-v33","evidence_source":"host-vision","observed":True,
        "required_present":["dragon","torrential rain"],"forbidden_present":["armor","sword"],
        "scores":{"anatomy":0.8,"composition":0.75,"lighting":0.7,"physics":0.8,"attention":0.55},
        "repair_attempts_used":0,
    }})
    assert_true(drift["decision"]=="repair" and "natural duck" in drift["missing_required"],"drift_detects_material_mismatch",results)
    rep=vc.repair({"contract":built["contract"],"verification":drift})
    assert_true(rep["ok"] and rep["packet"]["repair_attempt"]==1 and rep["packet"]["requires_fresh_preflight"] is True,"one_repair_packet",results)

    drift2=vc.verify({"contract":built["contract"],"observed":{
        "request_id":"req-v33","evidence_source":"host-vision","observed":True,
        "required_present":["dragon","torrential rain"],"forbidden_present":["armor"],
        "repair_attempts_used":1,
    }})
    assert_true(drift2["decision"]=="block","repair_budget_stops_loop",results)
    mismatch=vc.verify({"contract":built["contract"],"observed":{"request_id":"req-other","evidence_source":"host-vision","observed":True}})
    assert_true(mismatch["decision"]=="block","cross_request_evidence_blocked",results)

    low=vc.jev_packet({"probability":0.76,"threshold":0.85,"reasons":["composition ambiguity"]})
    high=vc.jev_packet({"probability":0.91,"threshold":0.85})
    assert_true(low["reanalyze_required"] and low["max_additional_rounds"]==1,"jev_below_threshold_one_round",results)
    assert_true(not high["reanalyze_required"],"jev_above_threshold_no_retry",results)

    _,ind=run_json(INDEP,[],{"artifacts":[
        {"agentId":"a","source":"cleanapis","model":"m1"},
        {"agentId":"b","source":"cleanapis","model":"m2"},
        {"agentId":"c","source":"cloudflare","model":"m3","fallback_used":True},
        {"agentId":"d","source":"cloudflare","model":"m3","fallback_used":True},
    ]})
    assert_true(ind.get("ok") and ind["score"]<1 and ind["effective_independent_votes"]<4,"fallback_independence_discounted",results)

    modules={f"M{i:02d}":"not-material" for i in range(1,29)}
    profiles={p:"not-material" for p in pb.PROFILES}
    pre=pb.build_pre_execution({
        "request_id":"req-v33","trace_version":"3.1","modules":modules,"profiles":profiles,
        "runtime_receipts":[{"id":"think","kind":"tool","observed_request_id":"req-v33","receipt":{"receiptId":"runtime-1","engineVersion":"0.8.3","tool":"kosif_think"}}],
        "execution_contract":{"request_id":"req-v33","goal":"image"},"dissent_ledger":[],
        "source_taint":{"checked":True,"blocked_supports":0},
        "gates":{"bias_gate":"pass","self_critic":"pass","verifier":"pass","optimizer_gate":"pass"},
        "budget":{"model_calls_used":1,"max_model_calls":5,"tool_calls_used":1,"max_tool_calls":10,"retries_used":0,"max_retries":1,"no_change_count":0,"max_no_change":2,"status":"completed"},
        "consistency":{"checked":True,"quarantined":[],"evidence_conflict":False},
        "artifact_expected":True,"artifact_quality_expected":True,
    })
    auth=pv.validate(pre)
    assert_true(auth["authorization_ready"] and pre["artifact_delivery"]["quality"]["verified"] is False,"preauth_quality_not_prefabricated",results)
    final=pb.finalize_receipt(pre,{
        "request_id":"req-v33","observed":True,"evidence_type":"host-artifact-reference","reference":"artifact://image-1",
        "quality":{"verified":True,"passed":True,"contract_match_score":1.0,"visual_drift_score":0.08,"anatomy_score":0.9,"composition_score":0.88,"lighting_consistency":0.9,"physics_consistency":0.86,"attention_preservation":0.95,"repair_attempts":1,"verification_source":"host-vision","contract_id":built["contract"]["contract_id"]}
    },"pass")
    comp=pv.validate(final)
    assert_true(comp["completion_ready"],"quality_gated_completion_passes",results)

    # Backward compatibility: ordinary artifact receipts require no quality object.
    pre_legacy=pb.build_pre_execution({
        "request_id":"req-legacy","trace_version":"3.1","modules":modules,"profiles":profiles,
        "runtime_receipts":[{"id":"think","kind":"tool","observed_request_id":"req-legacy","receipt":{"receiptId":"runtime-legacy","engineVersion":"0.8.3","tool":"kosif_think"}}],
        "execution_contract":{"request_id":"req-legacy","goal":"ordinary artifact"},"dissent_ledger":[],
        "source_taint":{"checked":True,"blocked_supports":0},
        "gates":{"bias_gate":"pass","self_critic":"pass","verifier":"pass","optimizer_gate":"pass"},
        "budget":{"model_calls_used":1,"max_model_calls":5,"tool_calls_used":1,"max_tool_calls":10,"retries_used":0,"max_retries":1,"no_change_count":0,"max_no_change":2,"status":"completed"},
        "consistency":{"checked":True,"quarantined":[],"evidence_conflict":False},
        "artifact_expected":True
    })
    final_legacy=pb.finalize_receipt(pre_legacy,{"request_id":"req-legacy","observed":True,"evidence_type":"host-artifact-reference","reference":"artifact://legacy"},"pass")
    assert_true(pv.validate(final_legacy)["completion_ready"],"backward_compatible_artifact_receipt",results)

    rejected=False
    try:
        pb.finalize_receipt(pre,{
            "request_id":"req-v33","observed":True,"evidence_type":"host-artifact-reference","reference":"artifact://bad",
            "quality":{"verified":True,"passed":False,"contract_match_score":0.4,"visual_drift_score":0.6,"repair_attempts":1,"verification_source":"host-vision","contract_id":built["contract"]["contract_id"]}
        },"pass")
    except ValueError:
        rejected=True
    assert_true(rejected,"failed_quality_cannot_claim_pass",results)

    failed=[r["name"] for r in results if not r["ok"]]
    print(json.dumps({"ok":not failed,"passed":len(results)-len(failed),"total":len(results),"failed":failed,"results":results},ensure_ascii=False,indent=2))
    return 0 if not failed else 1


if __name__=="__main__":
    raise SystemExit(main())
