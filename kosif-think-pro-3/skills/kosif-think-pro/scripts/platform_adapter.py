#!/usr/bin/env python3
"""Version-aware prompt platform registry. Provider syntax is time-sensitive."""
from __future__ import annotations
from datetime import date

REGISTRY={
 "midjourney":{"version":"V7","verified_at":"2026-09-30","stale_after_days":30,"source":"Drive: Cinema AI Director audit + Prompt Master ledger","syntax":["--ar","--style raw","--oref","--sref","--stylize","--seed"]},
 "veo":{"version":"3.x-family-not-provider-verified","verified_at":"2026-09-30","stale_after_days":14,"source":"Drive: Veo guide + Cinema AI Director audit","syntax":["Audio:","dialogue","last-frame continuity"]},
 "runway":{"version":"Gen-4.x-family-not-provider-verified","verified_at":"2026-09-30","stale_after_days":14,"source":"Drive: Cinema AI Director audit","syntax":["positive sequential action","reference keyframe"]},
 "kling":{"version":"2.x/3.x-family-not-provider-verified","verified_at":"2026-09-30","stale_after_days":14,"source":"Drive: Blue Diamond/Pokemon/Shining Star specs","syntax":["Start frame","End frame","motion"]},
 "legacy-midjourney-v5":{"version":"V5.1","verified_at":"2023-01-01","stale_after_days":30,"source":"Drive: Midjourney Comprehensive Guide V4/V5/V5.1","syntax":["--ar","--seed","--iw"]},
}

def resolve_adapter(platform: str, *, as_of: str, provider_verified: bool=False) -> dict:
    p=platform.lower().strip()
    if p not in REGISTRY:
        return {"platform":p,"version":None,"freshness":"unknown","current_syntax_verified":False,"source":None,"syntax":[],"rule":"unknown adapter; verify provider docs before current-syntax claims"}
    rec=dict(REGISTRY[p]); age=(date.fromisoformat(as_of[:10])-date.fromisoformat(rec["verified_at"])).days
    freshness="fresh" if age <= rec["stale_after_days"] else "stale"
    # Internal/source review is not provider verification. Explicit fresh provider verification may elevate current syntax.
    current = bool(provider_verified and freshness=="fresh")
    return {"platform":p,**rec,"age_days":age,"freshness":freshness,"current_syntax_verified":current,"rule":"source-derived syntax must be re-verified against current provider docs before consequential/current claims"}
