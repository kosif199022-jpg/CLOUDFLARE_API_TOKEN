#!/usr/bin/env python3
"""KOSIF Image Studio visual execution contract v1.0.

Commands (stdin JSON -> stdout JSON):
  build   Freeze a request-bound visual contract and deterministically compile prompt text.
  verify  Compare structured observed evidence with a frozen visual contract.
  repair  Produce at most one targeted correction packet; never authorizes execution by itself.
  jev     Convert a below-threshold Jev result into one bounded re-analysis packet.

This helper does not inspect pixels by itself and does not prove semantic compliance. `verify`
requires structured evidence from an observed host/vision/human check bound to the same request.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy

CONTRACT_VERSION = "1.0"
ALLOWED_EVIDENCE_SOURCES = {"host-vision", "vision-tool", "human-review", "state-observation"}
LOCK_ORDER = ["subject", "action", "composition", "camera", "lighting", "weather", "environment", "style"]
QUALITY_KEYS = ["anatomy", "composition", "lighting", "physics", "attention"]
DEFAULT_THRESHOLDS = {
    "anatomy": 0.70,
    "composition": 0.65,
    "lighting": 0.65,
    "physics": 0.65,
    "attention": 0.70,
}


def _nonempty(v, name):
    s = str(v or "").strip()
    if not s:
        raise ValueError(f"{name} is required")
    return s


def _list(v, name, allow_empty=True):
    if v is None:
        return []
    if not isinstance(v, list):
        raise ValueError(f"{name} must be a list")
    out = []
    for i, item in enumerate(v):
        s = str(item or "").strip()
        if not s:
            raise ValueError(f"{name}[{i}] must be non-empty")
        out.append(s)
    if not allow_empty and not out:
        raise ValueError(f"{name} must not be empty")
    return out


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(obj):
    return hashlib.sha256(_canonical(obj).encode("utf-8")).hexdigest()


def _norm(s):
    return " ".join(str(s).casefold().split())


def _score(v, name):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError(f"{name} must be a number in [0,1]")
    f = float(v)
    if not 0 <= f <= 1:
        raise ValueError(f"{name} must be in [0,1]")
    return f


def compile_prompt(contract):
    locks = contract.get("locks") or {}
    parts = []
    for key in LOCK_ORDER:
        val = locks.get(key)
        if isinstance(val, list):
            val = "; ".join(str(x).strip() for x in val if str(x).strip())
        if str(val or "").strip():
            parts.append(f"{key.upper()}: {str(val).strip()}")
    required = contract.get("required") or []
    if required:
        parts.append("MUST VISIBLY INCLUDE: " + "; ".join(required))
    attention = contract.get("attention_budget") or []
    if attention:
        parts.append("ATTENTION PRIORITY (highest first): " + " > ".join(attention))
    physics = contract.get("physics_checks") or []
    if physics:
        parts.append("PHYSICS / INTERACTION REQUIREMENTS: " + "; ".join(physics))
    criteria = contract.get("success_criteria") or []
    if criteria:
        parts.append("SUCCESS CRITERIA: " + "; ".join(criteria))
    flexibility = contract.get("allowed_flexibility") or []
    if flexibility:
        parts.append("ALLOWED FLEXIBILITY ONLY: " + "; ".join(flexibility))
    parts.append(f"REQUEST BINDING: request_id={contract['request_id']} contract_id={contract['contract_id']}")
    prompt = " | ".join(parts)
    negative = "; ".join(contract.get("forbidden") or [])
    return prompt, negative


def build(payload):
    request_id = _nonempty(payload.get("request_id"), "request_id")
    goal = _nonempty(payload.get("goal"), "goal")
    required = _list(payload.get("required"), "required", allow_empty=False)
    forbidden = _list(payload.get("forbidden"), "forbidden")
    success = _list(payload.get("success_criteria"), "success_criteria")
    flexibility = _list(payload.get("allowed_flexibility"), "allowed_flexibility")
    physics = _list(payload.get("physics_checks"), "physics_checks")
    attention = _list(payload.get("attention_budget"), "attention_budget") or required[:3]
    if len(attention) > 3:
        raise ValueError("attention_budget supports at most 3 priority items")
    locks = payload.get("locks") or {}
    if not isinstance(locks, dict):
        raise ValueError("locks must be an object")
    locks = {str(k): v for k, v in locks.items() if str(v or "").strip()}
    max_repairs = int(payload.get("max_repairs", 1))
    if max_repairs not in {0, 1}:
        raise ValueError("v3.3 permits max_repairs only 0 or 1")
    jev_threshold = float(payload.get("jev_threshold", 0.85))
    if not 0.5 <= jev_threshold <= 0.99:
        raise ValueError("jev_threshold must be between 0.50 and 0.99")
    thresholds = dict(DEFAULT_THRESHOLDS)
    custom = payload.get("quality_thresholds") or {}
    if not isinstance(custom, dict):
        raise ValueError("quality_thresholds must be an object")
    for k, v in custom.items():
        if k not in thresholds:
            raise ValueError(f"unsupported quality threshold {k}")
        thresholds[k] = _score(v, f"quality_thresholds.{k}")

    base = {
        "contract_version": CONTRACT_VERSION,
        "request_id": request_id,
        "goal": goal,
        "required": required,
        "forbidden": forbidden,
        "locks": locks,
        "attention_budget": attention,
        "physics_checks": physics,
        "allowed_flexibility": flexibility,
        "success_criteria": success,
        "max_repairs": max_repairs,
        "jev_threshold": jev_threshold,
        "quality_thresholds": thresholds,
        "immutable": True,
    }
    contract_id = "visual-" + _digest(base)[:24]
    contract = {**base, "contract_id": contract_id}
    prompt, negative = compile_prompt(contract)
    return {
        "ok": True,
        "contract": contract,
        "compiled_prompt": prompt,
        "negative_prompt": negative,
        "contract_digest": _digest(contract),
        "note": "Contract is deterministic and request-bound; host generation is still a separate executor requiring Pro authorization when Pro Mode is active.",
    }


def verify(payload):
    contract = payload.get("contract")
    observed = payload.get("observed")
    if not isinstance(contract, dict):
        raise ValueError("contract object is required")
    if not isinstance(observed, dict):
        raise ValueError("observed object is required")
    request_id = _nonempty(contract.get("request_id"), "contract.request_id")
    if _nonempty(observed.get("request_id"), "observed.request_id") != request_id:
        return {"ok": False, "decision": "block", "reasons": ["request_id mismatch"], "repairable": False}
    source = _nonempty(observed.get("evidence_source"), "observed.evidence_source")
    if source not in ALLOWED_EVIDENCE_SOURCES:
        return {"ok": False, "decision": "block", "reasons": ["unrecognized observation source"], "repairable": False}
    if observed.get("observed") is not True:
        return {"ok": False, "decision": "block", "reasons": ["evidence is not marked observed"], "repairable": False}

    required = contract.get("required") or []
    forbidden = contract.get("forbidden") or []
    present = {_norm(x) for x in _list(observed.get("required_present"), "observed.required_present")}
    bad_present = {_norm(x) for x in _list(observed.get("forbidden_present"), "observed.forbidden_present")}
    missing = [x for x in required if _norm(x) not in present]
    forbidden_hits = [x for x in forbidden if _norm(x) in bad_present]

    scores_in = observed.get("scores") or {}
    if not isinstance(scores_in, dict):
        raise ValueError("observed.scores must be an object")
    scores = {}
    low = []
    thresholds = contract.get("quality_thresholds") or DEFAULT_THRESHOLDS
    for key in QUALITY_KEYS:
        if key in scores_in:
            scores[key] = _score(scores_in[key], f"observed.scores.{key}")
            if scores[key] < float(thresholds.get(key, DEFAULT_THRESHOLDS[key])):
                low.append(key)

    denom = max(1, len(required) + 2 * len(forbidden))
    contract_match = max(0.0, 1.0 - (len(missing) + 2 * len(forbidden_hits)) / denom)
    quality_values = [contract_match] + list(scores.values())
    quality_mean = sum(quality_values) / len(quality_values)
    drift_score = 1.0 - quality_mean
    reasons = []
    if missing:
        reasons.append("missing required: " + ", ".join(missing))
    if forbidden_hits:
        reasons.append("forbidden present: " + ", ".join(forbidden_hits))
    if low:
        reasons.append("low quality dimensions: " + ", ".join(low))
    hard_block = bool(observed.get("hard_block", False))
    attempts = int(observed.get("repair_attempts_used", 0))
    max_repairs = int(contract.get("max_repairs", 1))
    passed = not reasons and not hard_block
    if passed:
        decision = "pass"
    elif hard_block or attempts >= max_repairs:
        decision = "block"
    else:
        decision = "repair"
    return {
        "ok": True,
        "decision": decision,
        "passed": passed,
        "repairable": decision == "repair",
        "request_id": request_id,
        "contract_id": contract.get("contract_id"),
        "missing_required": missing,
        "forbidden_present": forbidden_hits,
        "low_quality_dimensions": low,
        "scores": scores,
        "contract_match_score": round(contract_match, 4),
        "visual_drift_score": round(drift_score, 4),
        "quality_mean": round(quality_mean, 4),
        "repair_attempts_used": attempts,
        "max_repairs": max_repairs,
        "reasons": reasons or ["all checked constraints passed"],
        "verification_source": source,
        "limitation": "Structured evidence gate; semantic correctness depends on the quality of the host/vision/human observation supplied.",
    }


def repair(payload):
    contract = payload.get("contract")
    verification = payload.get("verification")
    if not isinstance(contract, dict) or not isinstance(verification, dict):
        raise ValueError("contract and verification objects are required")
    if verification.get("request_id") != contract.get("request_id") or verification.get("contract_id") != contract.get("contract_id"):
        return {"ok": False, "authorized": False, "decision": "block", "reasons": ["verification is not bound to this contract"]}
    if verification.get("decision") != "repair":
        return {"ok": False, "authorized": False, "decision": "block", "reasons": ["verification did not authorize a repair candidate"]}
    attempts = int(verification.get("repair_attempts_used", 0))
    max_repairs = int(contract.get("max_repairs", 1))
    if attempts >= max_repairs:
        return {"ok": False, "authorized": False, "decision": "block", "reasons": ["repair budget exhausted"]}
    corrections = []
    if verification.get("missing_required"):
        corrections.append("restore missing required elements exactly: " + "; ".join(verification["missing_required"]))
    if verification.get("forbidden_present"):
        corrections.append("remove forbidden elements: " + "; ".join(verification["forbidden_present"]))
    if verification.get("low_quality_dimensions"):
        corrections.append("repair only these weak dimensions: " + "; ".join(verification["low_quality_dimensions"]))
    packet = {
        "request_id": contract["request_id"],
        "contract_id": contract["contract_id"],
        "repair_attempt": attempts + 1,
        "max_repairs": max_repairs,
        "instruction": "Correction pass only. Preserve every already-compliant subject, composition, camera, lighting, style and identity lock unless explicitly named below. " + " | ".join(corrections),
        "requires_fresh_preflight": True,
        "changes_contract": False,
        "execution_authority": False,
    }
    packet["repair_id"] = "repair-" + _digest(packet)[:20]
    return {"ok": True, "authorized": False, "decision": "repair-candidate", "packet": packet}


def jev_packet(payload):
    probability = _score(payload.get("probability"), "probability")
    threshold = float(payload.get("threshold", 0.85))
    if not 0.5 <= threshold <= 0.99:
        raise ValueError("threshold must be between 0.50 and 0.99")
    reasons = _list(payload.get("reasons"), "reasons")
    if probability >= threshold:
        return {"ok": True, "reanalyze_required": False, "probability": probability, "threshold": threshold, "max_additional_rounds": 0}
    return {
        "ok": True,
        "reanalyze_required": True,
        "probability": probability,
        "threshold": threshold,
        "focus_reasons": reasons or ["Jev confidence below configured threshold; identify the single most material unresolved ambiguity"],
        "max_additional_rounds": 1,
        "instruction": "Run one targeted analysis round addressing only the listed reasons, then re-run Jev once. Do not loop if still below threshold; escalate/stop instead.",
    }


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["build", "verify", "repair", "jev"])
    args = p.parse_args(argv)
    try:
        payload = json.load(sys.stdin)
        fn = {"build": build, "verify": verify, "repair": repair, "jev": jev_packet}[args.command]
        out = fn(payload)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
