#!/usr/bin/env python3
"""KOSIF Pro receipt validator v4.0.0.

Preserves trace 3.1 semantics and adds optional visual-quality completion checks.
Quality metadata is observational/non-cryptographic and does not prove provider identity,
pixel truth, host/kernel enforcement, or cryptographic authenticity.
"""
import argparse
import json
import sys

MODULES=[f"M{i:02d}" for i in range(1,29)]
PROFILES=[
 "Skeptic","Strict Verifier","Decisive Operator","Ambitious Optimizer",
 "Creative Explorer","Conservative Risk Guardian","Analytical Decomposer",
 "Adversarial Critic","Naive-Reasoning Simulator","Integrator","Bias Hunter",
 "Constraint Optimizer","Conflict Scout","Evidence Accountant"
]
MOD_STATES={"relevant","not-material","unavailable"}
PROF_STATES={"complete","not-material","unavailable"}
GATE_STATES={"pass","revise","escalate"}
DISPOSITIONS={"accepted","partially-accepted","rejected","unresolved"}
POST_STATES={"pass","failed-drift","not-verified","not-needed"}
RECEIPT_EVIDENCE_TYPES={"host-tool-result","state-observation","native-receipt"}
ARTIFACT_EVIDENCE_TYPES={"host-artifact-reference","state-observation","native-receipt","materialized-file"}
TRACE_VERSIONS={"2.7","2.7.1","2.8","2.8.1","3.0","3.1"}
MODERN_TRACES={"2.8","2.8.1","3.0","3.1"}
CONSISTENCY_TRACES={"3.0","3.1"}
RECEIPT_PHASES={"pre-execution","final"}
QUALITY_SCORE_KEYS={
 "contract_match_score","visual_drift_score","anatomy_score","composition_score",
 "lighting_consistency","physics_consistency","attention_preservation"
}


def has_receipt_evidence(c):
    if c.get("receipt_id"):
        return True
    ev=c.get("receipt_evidence")
    return isinstance(ev,dict) and ev.get("observed") is True and ev.get("type") in RECEIPT_EVIDENCE_TYPES


def _phase(obj):
    return obj.get("receipt_phase") or "final"


def _validate_quality(q, phase, issues):
    if not isinstance(q,dict):
        issues.append("artifact quality must be an object")
        return
    required=q.get("required",False)
    if not isinstance(required,bool):
        issues.append("artifact quality.required must be boolean")
        return
    if not required:
        return
    if phase=="pre-execution":
        if q.get("verified") is True:
            issues.append("pre-execution artifact quality must not be pre-verified")
        return
    if q.get("verified") is not True:
        issues.append("required artifact quality must be verified")
    if not isinstance(q.get("passed"),bool):
        issues.append("required artifact quality.passed must be boolean")
    for key in QUALITY_SCORE_KEYS:
        if key in q:
            v=q.get(key)
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not 0 <= float(v) <= 1:
                issues.append(f"artifact quality {key} must be in [0,1]")
    for key in ("contract_match_score","visual_drift_score"):
        if key not in q:
            issues.append(f"required artifact quality missing {key}")
    attempts=q.get("repair_attempts")
    if isinstance(attempts,bool) or not isinstance(attempts,int) or not 0 <= attempts <= 1:
        issues.append("artifact quality.repair_attempts must be integer 0 or 1")
    if not str(q.get("verification_source") or "").strip():
        issues.append("artifact quality.verification_source is required")
    if not str(q.get("contract_id") or "").strip():
        issues.append("artifact quality.contract_id is required")


def validate(obj):
    issues=[]
    tv=obj.get("trace_version")
    if tv not in TRACE_VERSIONS:
        issues.append("trace_version must be one of 2.7/2.7.1/2.8/2.8.1/3.0/3.1")

    phase=_phase(obj)
    if phase not in RECEIPT_PHASES:
        issues.append("receipt_phase must be pre-execution or final")

    request_id=""
    if tv in MODERN_TRACES:
        if obj.get("pro_mode") is not True:
            issues.append("pro_mode must be true for modern Pro receipts")
        if not str(obj.get("receipt_id") or "").strip():
            issues.append("missing receipt_id")
        rb=obj.get("request_binding") or {}
        request_id=str(rb.get("request_id") or "").strip()
        if not request_id:
            issues.append("request_binding.request_id required")
        if rb.get("current_request") is not True:
            issues.append("request_binding.current_request must be true")
        if rb.get("reused_prior_receipt") is not False:
            issues.append("request_binding.reused_prior_receipt must be false")

    modules=obj.get("modules") or {}; profiles=obj.get("profiles") or {}
    for m in MODULES:
        if modules.get(m) not in MOD_STATES:
            issues.append(f"invalid/missing module {m}")
    for p in PROFILES:
        if profiles.get(p) not in PROF_STATES:
            issues.append(f"invalid/missing profile {p}")

    caps=obj.get("models_tools")
    if not isinstance(caps,list) or not caps:
        issues.append("models_tools must contain at least one capability record")
    else:
        ids=set()
        for i,c in enumerate(caps):
            cid=c.get("id")
            if not cid:
                issues.append(f"capability[{i}] missing id"); continue
            if cid in ids:
                issues.append(f"duplicate capability id {cid}")
            ids.add(cid)
            if c.get("kind") not in {"model","tool","app"}:
                issues.append(f"{cid}: invalid kind")
            for b in ("requested","available","used"):
                if not isinstance(c.get(b),bool):
                    issues.append(f"{cid}: {b} must be boolean")
            if c.get("used"):
                if not c.get("available"):
                    issues.append(f"{cid}: used but unavailable")
                if not has_receipt_evidence(c):
                    issues.append(f"{cid}: used without observable receipt evidence")
                if not c.get("actual_source"):
                    issues.append(f"{cid}: used without actual_source")
                if c.get("kind")=="model" and not c.get("actual_model"):
                    issues.append(f"{cid}: model used without actual_model")
            if c.get("fallback_used") and not c.get("fallback_reason"):
                issues.append(f"{cid}: fallback without reason")

            ev=c.get("receipt_evidence")
            if isinstance(ev,dict) and ev.get("binding_mode")=="host-observed-adapter":
                if ev.get("observed") is not True:
                    issues.append(f"{cid}: adapter receipt evidence must be observed")
                if str(ev.get("request_id") or "").strip()!=request_id:
                    issues.append(f"{cid}: adapter receipt request_id mismatch")
                integ=ev.get("integrity")
                if isinstance(integ,dict) and integ.get("signed") is False and "signature" in str(integ.get("type","")).lower():
                    issues.append(f"{cid}: unsigned integrity evidence must not be labeled signature")

    ledger=obj.get("dissent_ledger")
    complete={p for p,s in profiles.items() if s=="complete"}; seen=set()
    if not isinstance(ledger,list):
        issues.append("dissent_ledger must be a list")
    else:
        for e in ledger:
            p=e.get("profile")
            if p: seen.add(p)
            if p not in PROFILES:
                issues.append(f"dissent unknown profile {p}")
            if e.get("disposition") not in DISPOSITIONS:
                issues.append(f"{p}: invalid dissent disposition")
            if not e.get("conclusion"):
                issues.append(f"{p}: missing conclusion")
            if "strongest_objection" not in e:
                issues.append(f"{p}: missing strongest_objection")
        for p in sorted(complete-seen):
            issues.append(f"missing dissent entry for complete profile {p}")

    taint=obj.get("source_taint") or {}
    if taint.get("checked") is not True:
        issues.append("source_taint.checked must be true")
    if not isinstance(taint.get("blocked_supports",0),int):
        issues.append("source_taint.blocked_supports must be int")

    gates=obj.get("gates") or {}
    for g in ("bias_gate","self_critic","verifier"):
        if gates.get(g) not in GATE_STATES:
            issues.append(f"invalid/missing gate {g}")
    if "optimizer_gate" not in gates:
        issues.append("missing optimizer_gate")
    if obj.get("execution_contract") not in {"present","not-needed"}:
        issues.append("invalid execution_contract")
    if obj.get("postcondition") not in POST_STATES:
        issues.append("invalid postcondition")
    if not isinstance(obj.get("evidence_gaps"),list):
        issues.append("evidence_gaps must be a list")

    delivery=obj.get("artifact_delivery") or {"required":False}
    if not isinstance(delivery.get("required",False),bool):
        issues.append("artifact_delivery.required must be boolean")
    elif delivery.get("required"):
        if tv not in MODERN_TRACES:
            issues.append("artifact delivery proof requires a request-bound modern trace")
        if str(delivery.get("request_id") or "").strip() != request_id:
            issues.append("artifact request_id must match receipt request_id")
        if phase=="pre-execution":
            if delivery.get("verified") is True:
                issues.append("pre-execution receipt must not pre-verify an expected artifact")
            if str(delivery.get("reference") or "").strip():
                issues.append("pre-execution receipt must not carry a fabricated artifact reference")
        else:
            if delivery.get("verified") is not True:
                issues.append("required artifact must be verified")
            if not str(delivery.get("reference") or "").strip():
                issues.append("required artifact missing observable reference")
            if delivery.get("evidence_type") not in ARTIFACT_EVIDENCE_TYPES:
                issues.append("required artifact has invalid/missing evidence_type")
            if delivery.get("delivery_unknown") is True:
                issues.append("artifact delivery state is unknown")
        _validate_quality(delivery.get("quality") or {"required":False},phase,issues)

    b=obj.get("budget") or {}
    required=["model_calls_used","max_model_calls","tool_calls_used","max_tool_calls","retries_used","max_retries","no_change_count","max_no_change","status"]
    for k in required:
        if k not in b:
            issues.append(f"budget missing {k}")
    for used,maxk in [("model_calls_used","max_model_calls"),("tool_calls_used","max_tool_calls"),("retries_used","max_retries")]:
        if isinstance(b.get(used),int) and isinstance(b.get(maxk),int) and b[used]>b[maxk] and b.get("status") not in {"stopped","escalated"}:
            issues.append(f"budget exceeded {used} without stop/escalate")
    if isinstance(b.get("no_change_count"),int) and isinstance(b.get("max_no_change"),int) and b["no_change_count"]>=b["max_no_change"] and b.get("status") not in {"stopped","escalated"}:
        issues.append("no-change threshold reached without stop/escalate")

    if tv in CONSISTENCY_TRACES:
        cons=obj.get("consistency")
        if not isinstance(cons,dict) or cons.get("checked") is not True:
            issues.append(f"trace {tv} requires consistency.checked=true")
        elif not isinstance(cons.get("quarantined",[]),list):
            issues.append("consistency.quarantined must be a list of values")


    council=obj.get("council")
    if council is not None:
        if not isinstance(council,dict):
            issues.append("council must be an object")
        else:
            if council.get("aggregate_verdict") not in {"proceed","revise","escalate"}:
                issues.append("council.aggregate_verdict must be proceed/revise/escalate")
            if not isinstance(council.get("size"),int) or not 1 <= council["size"] <= 100:
                issues.append("council.size must be an int in 1..100")
            if not isinstance(council.get("seals_verified"),bool):
                issues.append("council.seals_verified must be boolean")

    structural=not issues
    auth=authorization(obj,structural)
    comp=completion(obj,structural)
    return {
        "ok":structural,
        "structurally_valid":structural,
        "issues":issues,
        **auth,
        **comp,
    }


def _shared_readiness_blockers(obj, structural):
    blockers=[] if structural else ["receipt is not structurally valid"]
    tv=obj.get("trace_version")
    if tv not in MODERN_TRACES:
        blockers.append("legacy trace lacks current-request binding and cannot authorize modern Pro execution")
    gates=obj.get("gates") or {}
    for g in ("bias_gate","self_critic","verifier"):
        if gates.get(g)!="pass":
            blockers.append(f"{g} is {gates.get(g)!r}, not pass")
    for e in obj.get("dissent_ledger") or []:
        if isinstance(e,dict) and e.get("disposition")=="unresolved" and e.get("material",True):
            blockers.append(f"unresolved material dissent: {e.get('profile')}")
    if (obj.get("budget") or {}).get("status")!="completed":
        blockers.append("budget status is not completed")
    cons=obj.get("consistency") or {}
    final=obj.get("final_answer")
    if final is not None and str(final) in {str(q) for q in cons.get("quarantined",[]) or []}:
        blockers.append(f"final_answer {final!r} was quarantined by the consistency gate")
    if cons.get("evidence_conflict"):
        blockers.append("independent evidence conflict unresolved")

    council=obj.get("council")
    if isinstance(council,dict):
        if council.get("aggregate_verdict")!="proceed":
            blockers.append(f"council verdict is {council.get('aggregate_verdict')!r}, not proceed")
        if council.get("seals_verified") is not True:
            blockers.append("council first-pass seals not verified")
    if obj.get("execution_contract")!="present":
        blockers.append("execution_contract is not present")
    return blockers


def authorization(obj, structural):
    blockers=_shared_readiness_blockers(obj, structural)
    if obj.get("postcondition") not in {"not-needed","pass"}:
        blockers.append(f"postcondition is {obj.get('postcondition')!r}")
    return {"authorization_ready":not blockers,"authorization_blockers":blockers}


def completion(obj, structural):
    blockers=_shared_readiness_blockers(obj, structural)
    if _phase(obj)!="final":
        blockers.append("receipt_phase is not final")
    if obj.get("postcondition") not in {"pass","not-needed"}:
        blockers.append(f"postcondition is {obj.get('postcondition')!r}")
    delivery=obj.get("artifact_delivery") or {"required":False}
    if delivery.get("required") and delivery.get("verified") is not True:
        blockers.append("required artifact is not verified")
    q=delivery.get("quality") or {"required":False}
    if q.get("required"):
        if q.get("verified") is not True:
            blockers.append("required artifact quality is not verified")
        if q.get("passed") is not True:
            blockers.append("required artifact quality did not pass")
    return {"completion_ready":not blockers,"completion_blockers":blockers}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode", choices=["authorization","completion","structural"], default="completion")
    args=p.parse_args()
    try:
        obj=json.load(sys.stdin)
    except Exception as e:
        print(json.dumps({"ok":False,"issues":[f"invalid-json: {e}"]})); return 2
    out=validate(obj)
    print(json.dumps(out,ensure_ascii=False,sort_keys=True))
    if args.mode=="authorization":
        return 0 if out["authorization_ready"] else 1
    if args.mode=="structural":
        return 0 if out["structurally_valid"] else 1
    return 0 if out["completion_ready"] else 1


if __name__=="__main__":
    raise SystemExit(main())
