#!/usr/bin/env python3
"""Structured multi-view identity reference sets; does not inspect pixels itself."""
from __future__ import annotations
REQUIRED=("front","left","right","back","three_quarter")

def build_reference_set(spec: dict) -> dict:
    views=dict(spec.get("views") or {}); present=[v for v in REQUIRED if views.get(v)]
    return {"schema":"identity-reference-set/4.0","character_id":spec.get("character_id"),"immutable":dict(spec.get("immutable") or {}),"mutable":dict(spec.get("mutable") or {}),"views":views,"required_views_present":present,"missing_views":[v for v in REQUIRED if v not in present],"ready":bool(spec.get("character_id")) and len(present)==len(REQUIRED),"evidence_rule":"references are constraints; post-generation identity must be verified from observed host/vision/human evidence"}

def verify_identity(reference: dict, observed: dict) -> dict:
    issues=[]
    if observed.get("character_id") != reference.get("character_id"): issues.append("character_id mismatch")
    traits=dict(observed.get("traits") or {})
    for k,v in (reference.get("immutable") or {}).items():
        if k in traits and traits[k] != v: issues.append(f"immutable drift: {k}")
        elif k not in traits: issues.append(f"unobserved immutable: {k}")
    missing=[v for v in REQUIRED if v not in set(observed.get("views_seen") or [])]
    if missing: issues.append("unobserved views: "+", ".join(missing))
    return {"verdict":"PASS" if not issues else "BLOCK","issues":issues,"observed":True,"rule":"helper never self-claims pixel observation"}
