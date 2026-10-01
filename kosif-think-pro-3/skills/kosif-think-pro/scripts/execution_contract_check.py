#!/usr/bin/env python3
import json, sys

MATERIAL = {"material", "destructive"}
PHASES = {"pre-execution", "final"}


def safety_gate(contract):
    reasons = []
    request_id = str(contract.get("request_id") or "").strip()
    pro_required = bool(contract.get("pro_mode_required", False))
    phase = contract.get("execution_phase") or "final"
    if phase not in PHASES:
        reasons.append("invalid_execution_phase")

    if pro_required:
        if not request_id:
            reasons.append("pro_mode_requires_request_id")
        if not bool(contract.get("pro_receipt_verified", False)):
            reasons.append("pro_mode_requires_verified_current_request_receipt")
        if not str(contract.get("pro_receipt_id") or "").strip():
            reasons.append("pro_mode_requires_receipt_id")
        if not bool(contract.get("pro_receipt_current_request", False)):
            reasons.append("pro_receipt_must_be_current_request")
        if bool(contract.get("prior_receipt_reused", False)):
            reasons.append("prior_request_receipt_reuse_blocked")
        receipt_request_id = str(contract.get("pro_receipt_request_id") or "").strip()
        if request_id and receipt_request_id != request_id:
            reasons.append("pro_receipt_request_id_mismatch")

    side_effect = str(contract.get("side_effect_class", "none")).lower()
    data_write = bool(contract.get("data_write", False))
    sensitive = bool(contract.get("touches_sensitive_or_important_data", False))
    irreversible = bool(contract.get("irreversible_or_hard_to_undo", False))
    swap = bool(contract.get("executor_or_tool_replacement", False))
    verified = bool(contract.get("fresh_verification", False))
    rollback = bool(contract.get("rollback_or_backup_ready", False))
    approved = bool(contract.get("explicit_user_approval", False))

    if side_effect in MATERIAL and not verified:
        reasons.append("material_action_requires_fresh_verification")
    if side_effect == "destructive" and not approved:
        reasons.append("destructive_action_requires_explicit_user_approval")
    if side_effect == "destructive" and not rollback:
        reasons.append("destructive_action_requires_rollback_or_backup_when_possible")
    if irreversible and not approved:
        reasons.append("irreversible_action_requires_explicit_user_approval")
    if sensitive and data_write and not verified:
        reasons.append("sensitive_data_write_requires_fresh_verification")
    if sensitive and data_write and not approved:
        reasons.append("sensitive_data_write_requires_explicit_user_approval")
    if swap:
        if not verified:
            reasons.append("executor_swap_requires_fresh_verification")
        if side_effect in MATERIAL or data_write or sensitive or irreversible:
            if not approved:
                reasons.append("risky_executor_swap_requires_explicit_user_approval")
    if bool(contract.get("side_effect_state_unknown", False)):
        reasons.append("unknown_side_effect_state_must_be_reconciled_before_retry")

    if bool(contract.get("artifact_expected", False)):
        if phase == "pre-execution":
            if bool(contract.get("artifact_verified", False)):
                reasons.append("pre_execution_artifact_must_not_be_preverified")
            if str(contract.get("artifact_reference") or "").strip():
                reasons.append("pre_execution_artifact_reference_must_be_empty")
        else:
            if not bool(contract.get("artifact_verified", False)):
                reasons.append("artifact_expected_but_not_verified")
            if not str(contract.get("artifact_reference") or "").strip():
                reasons.append("artifact_expected_but_reference_missing")
            artifact_request_id = str(contract.get("artifact_request_id") or "").strip()
            if request_id and artifact_request_id != request_id:
                reasons.append("artifact_request_id_mismatch")
            if bool(contract.get("artifact_delivery_unknown", False)):
                reasons.append("artifact_delivery_state_unknown")

    return {"ok": not reasons, "reasons": reasons, "execution_phase": phase}


def check(contract, brief):
    text = brief.lower()
    missing = [t for t in contract.get("required_terms", []) if t.lower() not in text]
    forbidden = [t for t in contract.get("forbidden_terms", []) if t.lower() in text]
    risk = safety_gate(contract)
    ok = not missing and not forbidden and risk["ok"]
    return {
        "ok": ok,
        "decision": "PASS" if ok else "BLOCK",
        "missing_required": missing,
        "forbidden_present": forbidden,
        "risk_gate": risk,
    }


def main():
    if len(sys.argv) != 3:
        print("usage: execution_contract_check.py CONTRACT.json BRIEF.txt", file=sys.stderr)
        return 2
    with open(sys.argv[1], encoding="utf-8") as f:
        contract = json.load(f)
    with open(sys.argv[2], encoding="utf-8") as f:
        brief = f.read()
    result = check(contract, brief)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
