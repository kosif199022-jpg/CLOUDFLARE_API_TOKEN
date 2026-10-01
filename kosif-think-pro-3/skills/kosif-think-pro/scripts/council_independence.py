#!/usr/bin/env python3
"""Heuristic KOSIF Council provenance/diversity scorer v1.0.

stdin: {"artifacts": [{"agentId", "source", "model", "fallback_used"? ...}], "min_score"?: 0.7}
This is a provenance-diversity heuristic, not proof of model or provider independence.
"""
import json
import sys


def nonempty(v, fallback):
    s = str(v or "").strip()
    return s or fallback


def main():
    try:
        p = json.load(sys.stdin)
        arts = p.get("artifacts")
        if not isinstance(arts, list) or not arts:
            raise ValueError("artifacts must be a non-empty list")
        min_score = float(p.get("min_score", 0.70))
        if not 0 <= min_score <= 1:
            raise ValueError("min_score must be in [0,1]")
        pair_seen = set()
        source_seen = set()
        rows = []
        total = 0.0
        for idx, a in enumerate(arts):
            if not isinstance(a, dict):
                raise ValueError(f"artifacts[{idx}] must be an object")
            source = nonempty(a.get("source") or a.get("actual_source"), "unknown-source")
            model = nonempty(a.get("model") or a.get("actual_model"), "unknown-model")
            pair = (source, model)
            weight = 1.0
            reasons = []
            if pair in pair_seen:
                weight *= 0.25
                reasons.append("same source+model already counted")
            elif source in source_seen:
                weight *= 0.85
                reasons.append("same source with a different model")
            fb = a.get("fallback")
            fallback_used = bool(a.get("fallback_used")) or (isinstance(fb, dict) and fb.get("used") is True)
            if fallback_used:
                weight *= 0.5
                reasons.append("fallback provenance discounted")
            if source == "unknown-source" or model == "unknown-model":
                weight *= 0.5
                reasons.append("incomplete provenance")
            total += weight
            pair_seen.add(pair)
            source_seen.add(source)
            rows.append({
                "agentId": a.get("agentId") or f"artifact-{idx}",
                "source": source,
                "model": model,
                "fallback_used": fallback_used,
                "independence_weight": round(weight, 3),
                "reasons": reasons or ["distinct observed provenance"],
            })
        score = total / len(arts)
        out = {
            "ok": True,
            "score": round(score, 4),
            "effective_independent_votes": round(total, 3),
            "artifact_count": len(arts),
            "unique_source_model_pairs": len(pair_seen),
            "unique_sources": len(source_seen),
            "meets_gate": score >= min_score,
            "min_score": min_score,
            "artifacts": rows,
            "limitation": "Heuristic from reported/observed provenance metadata; it does not independently verify provider identity or statistical independence.",
        }
    except Exception as exc:  # noqa: BLE001
        out = {"ok": False, "error": str(exc)}
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))
    return 0 if out.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
