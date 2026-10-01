#!/usr/bin/env python3
"""Structured multi-view identity reference sets; never performs biometric identification."""
from __future__ import annotations
REQUIRED=("front","left","right","back","three_quarter")

def build_reference_set(spec:dict)->dict:
    views=dict(spec.get("views") or {});present=[v for v in REQUIRED if views.get(v)]
    return {"schema":"identity-reference-set/4.0.1","character_id":spec.get("character_id"),"immutable":dict(spec.get("immutable") or {}),"mutable":dict(spec.get("mutable") or {}),"views":views,"required_views_present":present,"missing_views":[v for v in REQUIRED if v not in present],"ready":bool(spec.get("character_id")) and len(present)==len(REQUIRED),"evidence_rule":"reference set completeness is separate from per-artifact observation; post-generation drift must come from observed host/vision/human evidence"}

def verify_identity(reference:dict, observed:dict)->dict:
    issues=[];unobserved=[]
    if observed.get("character_id")!=reference.get("character_id"):issues.append("character_id mismatch")
    traits=dict(observed.get("traits") or {})
    for k,v in (reference.get("immutable") or {}).items():
        if k in traits and traits[k]!=v:issues.append(f"immutable drift: {k}")
        elif k not in traits:unobserved.append(k)
    required_view=observed.get("required_current_view")
    seen=set(observed.get("views_seen") or [])
    if required_view and required_view not in seen:issues.append(f"required current view unobserved: {required_view}")
    return {"verdict":"PASS" if not issues else "BLOCK","issues":issues,"unobserved_traits":unobserved,"views_seen":sorted(seen),"observation_source":observed.get("observation_source") or "unspecified-external","rule":"a single generated artifact is checked only for traits/views actually observable in that artifact; reference-set completeness is validated separately"}
