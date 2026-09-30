#!/usr/bin/env python3
"""KOSIF Pro receipt validator v3.0.
Validates internal structural/provenance consistency only. It does not prove truth,
provider identity, host/kernel enforcement, or cryptographic authenticity.

Two separate verdicts (v3.0):
- ok / structurally_valid: the receipt is well-formed and internally consistent.
- completion_ready: additionally every gate passed, the postcondition passed (or was
  not needed), no material dissent is unresolved, the budget completed normally and
  (trace 3.0) no quarantined answer became the final answer. A verifier/self-critic
  state of `revise` or `escalate` is structurally valid but NOT completion-ready.
Reads one JSON object from stdin. Exit 0 = completion-ready; 1 = structurally valid
but not completion-ready, or defects; 2 = invalid JSON.
"""
import json, sys
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
TRACE_VERSIONS={"2.7","2.7.1","3.0"}

def has_receipt_evidence(c):
    if c.get("receipt_id"): return True
    ev=c.get("receipt_evidence")
    return isinstance(ev,dict) and ev.get("observed") is True and ev.get("type") in RECEIPT_EVIDENCE_TYPES

def validate(obj):
    issues=[]
    tv=obj.get("trace_version")
    if tv not in TRACE_VERSIONS: issues.append("trace_version must be 2.7/2.7.1/3.0")
    modules=obj.get("modules") or {}; profiles=obj.get("profiles") or {}
    for m in MODULES:
        if modules.get(m) not in MOD_STATES: issues.append(f"invalid/missing module {m}")
    for p in PROFILES:
        if profiles.get(p) not in PROF_STATES: issues.append(f"invalid/missing profile {p}")
    caps=obj.get("models_tools")
    if not isinstance(caps,list) or not caps:
        issues.append("models_tools must contain at least one capability record")
    else:
        ids=set()
        for i,c in enumerate(caps):
            cid=c.get("id")
            if not cid: issues.append(f"capability[{i}] missing id"); continue
            if cid in ids: issues.append(f"duplicate capability id {cid}")
            ids.add(cid)
            if c.get("kind") not in {"model","tool","app"}: issues.append(f"{cid}: invalid kind")
            for b in ("requested","available","used"):
                if not isinstance(c.get(b),bool): issues.append(f"{cid}: {b} must be boolean")
            if c.get("used"):
                if not c.get("available"): issues.append(f"{cid}: used but unavailable")
                if not has_receipt_evidence(c): issues.append(f"{cid}: used without observable receipt evidence")
                if not c.get("actual_source"): issues.append(f"{cid}: used without actual_source")
                if c.get("kind")=="model" and not c.get("actual_model"): issues.append(f"{cid}: model used without actual_model")
            if c.get("fallback_used") and not c.get("fallback_reason"): issues.append(f"{cid}: fallback without reason")
    ledger=obj.get("dissent_ledger")
    complete={p for p,s in profiles.items() if s=="complete"}; seen=set()
    if not isinstance(ledger,list): issues.append("dissent_ledger must be a list")
    else:
        for e in ledger:
            p=e.get("profile")
            if p: seen.add(p)
            if p not in PROFILES: issues.append(f"dissent unknown profile {p}")
            if e.get("disposition") not in DISPOSITIONS: issues.append(f"{p}: invalid dissent disposition")
            if not e.get("conclusion"): issues.append(f"{p}: missing conclusion")
            if "strongest_objection" not in e: issues.append(f"{p}: missing strongest_objection")
        for p in sorted(complete-seen): issues.append(f"missing dissent entry for complete profile {p}")
    taint=obj.get("source_taint") or {}
    if taint.get("checked") is not True: issues.append("source_taint.checked must be true")
    if not isinstance(taint.get("blocked_supports",0),int): issues.append("source_taint.blocked_supports must be int")
    gates=obj.get("gates") or {}
    for g in ("bias_gate","self_critic","verifier"):
        if gates.get(g) not in GATE_STATES: issues.append(f"invalid/missing gate {g}")
    if "optimizer_gate" not in gates: issues.append("missing optimizer_gate")
    if obj.get("execution_contract") not in {"present","not-needed"}: issues.append("invalid execution_contract")
    if obj.get("postcondition") not in POST_STATES: issues.append("invalid postcondition")
    if not isinstance(obj.get("evidence_gaps"),list): issues.append("evidence_gaps must be a list")
    b=obj.get("budget") or {}
    required=["model_calls_used","max_model_calls","tool_calls_used","max_tool_calls","retries_used","max_retries","no_change_count","max_no_change","status"]
    for k in required:
        if k not in b: issues.append(f"budget missing {k}")
    for used,maxk in [("model_calls_used","max_model_calls"),("tool_calls_used","max_tool_calls"),("retries_used","max_retries")]:
        if isinstance(b.get(used),int) and isinstance(b.get(maxk),int) and b[used]>b[maxk] and b.get("status") not in {"stopped","escalated"}:
            issues.append(f"budget exceeded {used} without stop/escalate")
    if isinstance(b.get("no_change_count"),int) and isinstance(b.get("max_no_change"),int) and b["no_change_count"]>=b["max_no_change"] and b.get("status") not in {"stopped","escalated"}:
        issues.append("no-change threshold reached without stop/escalate")
    if tv=="3.0":
        cons=obj.get("consistency")
        if not isinstance(cons,dict) or cons.get("checked") is not True:
            issues.append("trace 3.0 requires consistency.checked=true (evidence_consistency_check.py)")
        elif not isinstance(cons.get("quarantined",[]),list):
            issues.append("consistency.quarantined must be a list of values")
    return {"ok":not issues,"structurally_valid":not issues,"issues":issues,**completion(obj,not issues)}

def completion(obj,structural):
    blockers=[] if structural else ["receipt is not structurally valid"]
    gates=obj.get("gates") or {}
    for g in ("bias_gate","self_critic","verifier"):
        if gates.get(g)!="pass": blockers.append(f"{g} is {gates.get(g)!r}, not pass")
    if obj.get("postcondition") not in {"pass","not-needed"}: blockers.append(f"postcondition is {obj.get('postcondition')!r}")
    for e in obj.get("dissent_ledger") or []:
        if isinstance(e,dict) and e.get("disposition")=="unresolved" and e.get("material",True):
            blockers.append(f"unresolved material dissent: {e.get('profile')}")
    if (obj.get("budget") or {}).get("status")!="completed": blockers.append("budget status is not completed")
    cons=obj.get("consistency") or {}
    final=obj.get("final_answer")
    if final is not None and str(final) in {str(q) for q in cons.get("quarantined",[]) or []}:
        blockers.append(f"final_answer {final!r} was quarantined by the consistency gate")
    if cons.get("evidence_conflict"): blockers.append("independent evidence conflict unresolved")
    return {"completion_ready":not blockers,"completion_blockers":blockers}

def main():
    try: obj=json.load(sys.stdin)
    except Exception as e:
        print(json.dumps({"ok":False,"issues":[f"invalid-json: {e}"]})); return 2
    out=validate(obj); print(json.dumps(out,ensure_ascii=False,sort_keys=True)); return 0 if out["completion_ready"] else 1
if __name__=="__main__": raise SystemExit(main())
