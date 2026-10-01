#!/usr/bin/env python3
"""KOSIF Verified Pro Receipt adapter/builder v3.3.0.

Adds optional artifact visual-quality evidence while preserving trace 3.1 request binding.
Quality evidence is observational/non-cryptographic and never upgrades unsigned runtime evidence.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, sys, uuid
from datetime import datetime, timezone

MODULES = [f"M{i:02d}" for i in range(1, 29)]
PROFILES = [
    "Skeptic", "Strict Verifier", "Decisive Operator", "Ambitious Optimizer",
    "Creative Explorer", "Conservative Risk Guardian", "Analytical Decomposer",
    "Adversarial Critic", "Naive-Reasoning Simulator", "Integrator",
    "Bias Hunter", "Constraint Optimizer", "Conflict Scout", "Evidence Accountant",
]
MODULE_STATES = {"relevant", "not-material", "unavailable"}
PROFILE_STATES = {"complete", "not-material", "unavailable"}
ARTIFACT_EVIDENCE_TYPES = {"host-artifact-reference", "state-observation", "native-receipt", "materialized-file"}
QUALITY_SCORE_KEYS = {
    "contract_match_score", "visual_drift_score", "anatomy_score", "composition_score",
    "lighting_consistency", "physics_consistency", "attention_preservation",
}


def _now(): return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
def _nonempty(value, name):
    s=str(value or "").strip()
    if not s: raise ValueError(f"{name} is required")
    return s

def _coverage(obj, keys, allowed, name):
    if not isinstance(obj, dict): raise ValueError(f"{name} must be an object")
    missing=[k for k in keys if k not in obj]
    if missing: raise ValueError(f"{name} missing: {', '.join(missing)}")
    invalid=[k for k in keys if obj.get(k) not in allowed]
    if invalid: raise ValueError(f"{name} invalid state: {', '.join(invalid)}")
    return {k: obj[k] for k in keys}

def _binding_digest(request_id, runtime_receipt_ids, contract_digest):
    material=json.dumps({"request_id":request_id,"runtime_receipt_ids":sorted(runtime_receipt_ids),"execution_contract_digest":contract_digest},sort_keys=True,separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(material).hexdigest()

def _quality_score(value, name):
    if isinstance(value,bool) or not isinstance(value,(int,float)): raise ValueError(f"{name} must be numeric")
    v=float(value)
    if not 0 <= v <= 1: raise ValueError(f"{name} must be in [0,1]")
    return v

def _normalize_quality(q, required=False):
    if not isinstance(q,dict):
        if required: raise ValueError("artifact_evidence.quality is required")
        return None
    if q.get("verified") is not True: raise ValueError("artifact_evidence.quality.verified must be true")
    if not isinstance(q.get("passed"),bool): raise ValueError("artifact_evidence.quality.passed must be boolean")
    out={"required":bool(required),"verified":True,"passed":q["passed"]}
    for key in QUALITY_SCORE_KEYS:
        if key in q and q[key] is not None:
            out[key]=round(_quality_score(q[key],f"artifact_evidence.quality.{key}"),4)
    if required:
        for key in ("contract_match_score","visual_drift_score"):
            if key not in out: raise ValueError(f"artifact_evidence.quality.{key} is required")
    attempts=q.get("repair_attempts",0)
    if isinstance(attempts,bool) or not isinstance(attempts,int) or not 0 <= attempts <= 1:
        raise ValueError("artifact_evidence.quality.repair_attempts must be integer 0 or 1")
    out["repair_attempts"]=attempts
    out["verification_source"]=_nonempty(q.get("verification_source"),"artifact_evidence.quality.verification_source")
    out["contract_id"]=_nonempty(q.get("contract_id"),"artifact_evidence.quality.contract_id") if required else str(q.get("contract_id") or "")
    out["limitation"]="Observed quality metadata; not cryptographic proof and not independent pixel inspection by the receipt builder."
    return out

def _normalize_capability(item, request_id):
    if not isinstance(item, dict): raise ValueError("runtime_receipts entries must be objects")
    cid=_nonempty(item.get("id"),"runtime_receipts[].id")
    raw=item.get("receipt") or {}
    if not isinstance(raw,dict): raise ValueError(f"{cid}: receipt must be an object")
    observed_request_id=_nonempty(item.get("observed_request_id"),f"{cid}.observed_request_id")
    if observed_request_id!=request_id: raise ValueError(f"{cid}: observed_request_id {observed_request_id!r} does not match current request {request_id!r}")
    if item.get("reused_prior_receipt") is True: raise ValueError(f"{cid}: reused prior receipt is forbidden")
    receipt_id=str(raw.get("receiptId") or raw.get("receipt_id") or "").strip()
    host_observation=item.get("host_observation")
    if not receipt_id:
        if not isinstance(host_observation,dict): raise ValueError(f"{cid}: runtime receipt id or host_observation is required")
        if host_observation.get("observed") is not True: raise ValueError(f"{cid}: host_observation.observed must be true")
        if host_observation.get("type") not in {"host-tool-result","state-observation"}: raise ValueError(f"{cid}: invalid host_observation.type")
        _nonempty(host_observation.get("observation_id"),f"{cid}.host_observation.observation_id")
        _nonempty(host_observation.get("result_digest"),f"{cid}.host_observation.result_digest")
    engine_version=str(raw.get("engineVersion") or raw.get("engine_version") or item.get("engine_version") or "").strip()
    tool_name=str(raw.get("tool") or item.get("tool") or "").strip()
    generated_at=str(raw.get("generatedAt") or raw.get("generated_at") or "").strip()
    integrity=raw.get("integrity")
    if integrity is not None and not isinstance(integrity,dict): raise ValueError(f"{cid}: integrity must be an object when present")
    capability={
        "id":cid,"kind":item.get("kind","tool"),"requested":bool(item.get("requested",True)),
        "available":bool(item.get("available",True)),"used":bool(item.get("used",True)),
        "actual_source":item.get("actual_source") or item.get("source") or "observed-runtime",
        "fallback_used":bool(item.get("fallback_used",False)),
        "receipt_evidence":{
            "type":(host_observation or {}).get("type") or "host-tool-result","observed":True,"request_id":request_id,
            "binding_mode":"host-observed-adapter","native_request_binding":bool(item.get("native_request_binding",False)),
            "engine_version":engine_version or None,"tool":tool_name or None,"generated_at":generated_at or None,
            "integrity":integrity or None,"observation_id":(host_observation or {}).get("observation_id"),
            "result_digest":(host_observation or {}).get("result_digest"),
            "limitation":"Adapter binds an observed runtime/host result to the frozen request_id; this is not cryptographic proof and does not upgrade an unsigned runtime digest.",
        },
    }
    if receipt_id: capability["receipt_id"]=receipt_id
    if capability["kind"]=="model": capability["actual_model"]=_nonempty(item.get("actual_model") or item.get("model"),f"{cid}.actual_model")
    if capability["fallback_used"]: capability["fallback_reason"]=_nonempty(item.get("fallback_reason"),f"{cid}.fallback_reason")
    return capability

def build_pre_execution(payload):
    if not isinstance(payload,dict): raise ValueError("payload must be an object")
    request_id=_nonempty(payload.get("request_id"),"request_id")
    trace_version=str(payload.get("trace_version") or "3.1").strip()
    if trace_version not in {"2.8","2.8.1","3.0","3.1"}: raise ValueError("trace_version must be one of 2.8/2.8.1/3.0/3.1")
    modules=_coverage(payload.get("modules"),MODULES,MODULE_STATES,"modules")
    profiles=_coverage(payload.get("profiles"),PROFILES,PROFILE_STATES,"profiles")
    rr=payload.get("runtime_receipts")
    if not isinstance(rr,list) or not rr: raise ValueError("runtime_receipts must contain at least one observed receipt")
    caps=[_normalize_capability(x,request_id) for x in rr]
    ids=[c["id"] for c in caps]
    if len(ids)!=len(set(ids)): raise ValueError("duplicate capability ids")
    execution_contract=payload.get("execution_contract")
    if not isinstance(execution_contract,dict): raise ValueError("execution_contract object is required")
    contract_request_id=_nonempty(execution_contract.get("request_id"),"execution_contract.request_id")
    if contract_request_id!=request_id: raise ValueError("execution_contract.request_id must match request_id")
    contract_digest=hashlib.sha256(json.dumps(execution_contract,sort_keys=True,separators=(",", ":")).encode("utf-8")).hexdigest()
    dissent=payload.get("dissent_ledger")
    if not isinstance(dissent,list): raise ValueError("dissent_ledger must be a list")
    source_taint=payload.get("source_taint")
    if not isinstance(source_taint,dict) or source_taint.get("checked") is not True: raise ValueError("source_taint.checked must be true")
    gates=payload.get("gates")
    if not isinstance(gates,dict): raise ValueError("gates object is required")
    budget=payload.get("budget")
    if not isinstance(budget,dict): raise ValueError("budget object is required")
    consistency=payload.get("consistency")
    if trace_version in {"3.0","3.1"} and (not isinstance(consistency,dict) or consistency.get("checked") is not True): raise ValueError("trace 3.0/3.1 requires consistency.checked=true")
    artifact_expected=bool(payload.get("artifact_expected",False))
    quality_required=bool(payload.get("artifact_quality_expected",False))
    if quality_required and not artifact_expected: raise ValueError("artifact_quality_expected requires artifact_expected=true")
    runtime_receipt_ids=[c.get("receipt_id") or (c.get("receipt_evidence") or {}).get("observation_id") for c in caps]
    receipt={
        "trace_version":trace_version,"receipt_phase":"pre-execution","pro_mode":True,"receipt_id":"pro-"+uuid.uuid4().hex,"created_at":_now(),
        "request_binding":{"request_id":request_id,"current_request":True,"reused_prior_receipt":False,"binding_mode":"host-observed-adapter",
                           "native_runtime_request_binding":all(bool((c.get("receipt_evidence") or {}).get("native_request_binding")) for c in caps),
                           "binding_digest":_binding_digest(request_id,runtime_receipt_ids,contract_digest)},
        "runtime_compat":{"adapter_version":"3.3.0","runtime_engine_versions":sorted({str((c.get("receipt_evidence") or {}).get("engine_version") or "") for c in caps if (c.get("receipt_evidence") or {}).get("engine_version")}),
                          "pro_trace_version":trace_version,"truthfulness":"engine version and Pro trace version are separate namespaces","cryptographic_provenance":False},
        "modules":modules,"profiles":profiles,"models_tools":caps,"dissent_ledger":dissent,"source_taint":source_taint,
        "evidence_gaps":list(payload.get("evidence_gaps") or []),"gates":gates,"execution_contract":"present",
        "execution_contract_digest":contract_digest,"postcondition":"not-needed","budget":budget,
        "artifact_delivery":{"required":artifact_expected,"verified":False,"request_id":request_id,"reference":"","evidence_type":None,"delivery_unknown":artifact_expected,
                             "quality":{"required":quality_required,"verified":False,"passed":False} if quality_required else {"required":False,"verified":False}},
    }
    if trace_version in {"3.0","3.1"}:
        receipt["consistency"]=consistency
        if "final_answer" in payload: receipt["final_answer"]=payload["final_answer"]
    return receipt

def finalize_receipt(receipt, artifact_evidence=None, postcondition="pass"):
    if not isinstance(receipt,dict): raise ValueError("receipt must be an object")
    out=copy.deepcopy(receipt)
    rb=out.get("request_binding") or {}
    request_id=_nonempty(rb.get("request_id"),"receipt.request_binding.request_id")
    if rb.get("current_request") is not True or rb.get("reused_prior_receipt") is not False: raise ValueError("receipt is not bound to the current request")
    if out.get("receipt_phase") not in {"pre-execution","final",None}: raise ValueError("invalid receipt_phase")
    current_delivery=out.get("artifact_delivery") or {}
    required=bool(current_delivery.get("required",False))
    quality_required=bool((current_delivery.get("quality") or {}).get("required",False))
    if required:
        ev=artifact_evidence
        if not isinstance(ev,dict): raise ValueError("artifact_evidence is required for an expected artifact")
        evidence_request_id=_nonempty(ev.get("request_id"),"artifact_evidence.request_id")
        if evidence_request_id!=request_id: raise ValueError("artifact_evidence.request_id must match receipt request_id")
        if ev.get("observed") is not True: raise ValueError("artifact_evidence.observed must be true")
        evidence_type=ev.get("evidence_type")
        if evidence_type not in ARTIFACT_EVIDENCE_TYPES: raise ValueError("invalid artifact evidence_type")
        reference=_nonempty(ev.get("reference"),"artifact_evidence.reference")
        quality=_normalize_quality(ev.get("quality"),required=quality_required) if (quality_required or ev.get("quality") is not None) else {"required":False,"verified":False}
        if quality_required and postcondition=="pass" and quality.get("passed") is not True:
            raise ValueError("postcondition pass requires artifact quality passed=true")
        out["artifact_delivery"]={"required":True,"verified":True,"request_id":request_id,"reference":reference,"evidence_type":evidence_type,"delivery_unknown":False,"observed_at":ev.get("observed_at") or _now(),"quality":quality}
    else:
        out["artifact_delivery"]={"required":False,"verified":False,"request_id":request_id,"reference":"","evidence_type":None,"delivery_unknown":False,"quality":{"required":False,"verified":False}}
    if postcondition not in {"pass","failed-drift","not-verified","not-needed"}: raise ValueError("invalid postcondition")
    out["postcondition"]=postcondition; out["receipt_phase"]="final"; out["finalized_at"]=_now(); out["finalization_id"]="final-"+uuid.uuid4().hex
    return out

def main():
    p=argparse.ArgumentParser(); p.add_argument("command",choices=["build","finalize"]); args=p.parse_args()
    try:
        obj=json.load(sys.stdin)
        out=build_pre_execution(obj) if args.command=="build" else finalize_receipt(obj["receipt"],obj.get("artifact_evidence"),obj.get("postcondition","pass"))
    except Exception as exc:
        print(json.dumps({"ok":False,"error":str(exc)},ensure_ascii=False)); return 2
    print(json.dumps({"ok":True,"receipt":out},ensure_ascii=False,sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
