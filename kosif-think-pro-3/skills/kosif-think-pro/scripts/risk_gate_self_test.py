#!/usr/bin/env python3
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from execution_contract_check import safety_gate

REQ="req-current"
BASE_PRO={
    "request_id":REQ,
    "pro_mode_required":True,
    "pro_receipt_verified":True,
    "pro_receipt_id":"receipt-current",
    "pro_receipt_request_id":REQ,
    "pro_receipt_current_request":True,
    "prior_receipt_reused":False,
}

def with_base(**kwargs):
    x=dict(BASE_PRO); x.update(kwargs); return x

CASES = [
    ("read_only_safe", {"side_effect_class":"none"}, True),
    ("pro_current_receipt_passes", with_base(side_effect_class="none"), True),
    ("pro_missing_receipt_blocks", {"request_id":REQ,"pro_mode_required":True}, False),
    ("pro_stale_receipt_blocks", with_base(prior_receipt_reused=True), False),
    ("pro_mismatched_receipt_blocks", with_base(pro_receipt_request_id="req-old"), False),
    ("material_unverified_blocks", {"side_effect_class":"material"}, False),
    ("material_verified_passes", {"side_effect_class":"material","fresh_verification":True}, True),
    ("destructive_without_approval_blocks", {"side_effect_class":"destructive","fresh_verification":True,"rollback_or_backup_ready":True}, False),
    ("destructive_full_controls_pass", {"side_effect_class":"destructive","fresh_verification":True,"rollback_or_backup_ready":True,"explicit_user_approval":True}, True),
    ("sensitive_write_without_approval_blocks", {"side_effect_class":"material","data_write":True,"touches_sensitive_or_important_data":True,"fresh_verification":True}, False),
    ("risky_executor_swap_blocks", {"side_effect_class":"material","executor_or_tool_replacement":True,"fresh_verification":True}, False),
    ("risky_executor_swap_approved_passes", {"side_effect_class":"material","executor_or_tool_replacement":True,"fresh_verification":True,"explicit_user_approval":True}, True),
    ("unknown_side_effect_state_blocks", {"side_effect_state_unknown":True}, False),
    ("preexec_artifact_expected_allowed", with_base(execution_phase="pre-execution",artifact_expected=True,artifact_verified=False,artifact_reference=""), True),
    ("preexec_artifact_fake_reference_blocks", with_base(execution_phase="pre-execution",artifact_expected=True,artifact_verified=False,artifact_reference="artifact://fake"), False),
    ("final_artifact_missing_reference_blocks", with_base(execution_phase="final",artifact_expected=True,artifact_verified=True,artifact_request_id=REQ), False),
    ("final_artifact_request_mismatch_blocks", with_base(execution_phase="final",artifact_expected=True,artifact_verified=True,artifact_request_id="req-old",artifact_reference="artifact://x"), False),
    ("final_artifact_verified_passes", with_base(execution_phase="final",artifact_expected=True,artifact_verified=True,artifact_request_id=REQ,artifact_reference="artifact://x",artifact_delivery_unknown=False), True),
]

def main():
    results=[]
    for name, contract, expected in CASES:
        got=safety_gate(contract)["ok"]
        results.append({"name":name,"ok":got==expected,"gate_ok":got,"expected":expected})
    failed=[r["name"] for r in results if not r["ok"]]
    print(json.dumps({"ok":not failed,"passed":len(results)-len(failed),"total":len(results),"failed":failed,"results":results},ensure_ascii=False,indent=2))
    return 0 if not failed else 1

if __name__ == "__main__":
    raise SystemExit(main())
