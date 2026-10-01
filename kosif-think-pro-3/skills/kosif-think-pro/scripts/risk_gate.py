#!/usr/bin/env python3
"""Unified v4 Tool-Swap / Action / Data risk gate.

Deterministic preflight only. PASS is permission to continue the workflow, not proof
that a downstream action occurred. Human checkpoints and secrets remain blocked.
"""
from __future__ import annotations
import json, re, sys

HUMAN_RE=re.compile(r"\b(captcha|otp|mfa|one[- ]time|password|credential|card number|cvv|payment|billing)\b",re.I)
IRREV_RE=re.compile(r"\b(delete|drop|destroy|erase|factory reset|force[- ]?push|publish permanently|terminate)\b",re.I)

def _out(verdict,gate,reasons,checks):
    return {"verdict":verdict,"gate":gate,"reasons":reasons,"checks":checks,
            "rule":"PASS is preflight only; verify executor result and postcondition separately"}

def evaluate(state:dict)->dict:
    gate=str(state.get("gate") or "").strip().lower()
    reasons=[]; checks=[]

    if gate=="tool-swap":
        intended=str(state.get("intended_tool") or "").strip()
        proposed=str(state.get("proposed_tool") or "").strip()
        if not intended or not proposed:
            return _out("BLOCK",gate,["intended_tool and proposed_tool are required"],checks)
        checks.append("tools-named")
        same_tool=intended==proposed
        same_semantics=state.get("same_semantics") is True
        schema=state.get("fresh_schema_verified") is True
        if same_tool:
            if not same_semantics:
                return _out("VERIFY",gate,["same tool selected but semantic contract was not verified"],checks)
            if not schema:
                return _out("VERIFY",gate,["live/fresh schema was not verified"],checks)
            return _out("PASS",gate,[],checks+["same-tool","semantics-verified","schema-verified"])
        if not same_semantics:
            return _out("BLOCK",gate,[f"material tool swap {intended!r} -> {proposed!r} changes semantics"],checks)
        if not schema:
            return _out("VERIFY",gate,["replacement schema/capabilities need fresh verification"],checks)
        if state.get("explicit_approval") is not True:
            return _out("VERIFY",gate,["compatible replacement still needs explicit approval for this task"],checks)
        return _out("PASS",gate,[],checks+["replacement-compatible","schema-verified","approved"])

    if gate=="action":
        action=str(state.get("action") or "")
        side=str(state.get("side_effect") or "unknown").lower()
        checks.append("action-classified")
        if HUMAN_RE.search(action):
            return _out("BLOCK",gate,["human-controlled credential/security/payment checkpoint"],checks)
        if side=="none":
            return _out("PASS",gate,[],checks+["read-only-or-no-side-effect"])
        if side=="unknown":
            return _out("VERIFY",gate,["side-effect state is unknown"],checks)
        irreversible=(side=="irreversible" or bool(IRREV_RE.search(action)))
        if irreversible and state.get("explicit_approval") is not True:
            return _out("BLOCK",gate,["irreversible/destructive action lacks explicit approval"],checks)
        if state.get("fresh_target_verified") is not True:
            return _out("VERIFY",gate,["target and impact must be freshly verified"],checks)
        if side in {"external-write","public-write","irreversible"} and state.get("explicit_approval") is not True:
            return _out("VERIFY",gate,["material external/public write needs explicit approval"],checks)
        return _out("PASS",gate,[],checks+["fresh-target","approval-ok" if state.get("explicit_approval") else "low-risk-write"])

    if gate=="data":
        cls=str(state.get("data_class") or "unknown").lower()
        dest=str(state.get("destination") or "unknown").lower()
        if state.get("minimum_necessary") is not True:
            return _out("BLOCK",gate,["data scope exceeds minimum necessary or was not established"],checks)
        checks.append("minimum-necessary")
        if cls in {"secret","credential","otp","payment-card","private-key"}:
            return _out("BLOCK",gate,[f"{cls} data cannot be passed through this gate"],checks)
        if cls=="unknown":
            return _out("VERIFY",gate,["data classification is unknown"],checks)
        if dest=="unknown":
            return _out("VERIFY",gate,["destination classification is unknown"],checks)
        if cls in {"private","personal","confidential","sensitive"} and dest=="external" and state.get("explicit_approval") is not True:
            return _out("VERIFY",gate,["external disclosure of non-public data needs explicit approval"],checks)
        return _out("PASS",gate,[],checks+["classification-known","destination-known"])

    return _out("BLOCK",gate or "<missing>",["unknown or missing gate type"],checks)

def main():
    try: obj=json.load(sys.stdin); out=evaluate(obj)
    except Exception as e:
        print(json.dumps({"verdict":"BLOCK","error":str(e)})); return 2
    print(json.dumps(out,ensure_ascii=False,sort_keys=True))
    return {"PASS":0,"VERIFY":1,"BLOCK":3}[out["verdict"]]

if __name__=="__main__": raise SystemExit(main())
