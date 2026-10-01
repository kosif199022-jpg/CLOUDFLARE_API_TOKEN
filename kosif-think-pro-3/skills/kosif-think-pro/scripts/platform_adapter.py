#!/usr/bin/env python3
"""Version-aware prompt platform registry. Source-derived syntax is never current by default."""
from __future__ import annotations
from datetime import date

REGISTRY={
 "midjourney":{"version":"V7-source-not-provider-verified","verified_at":"2026-09-30","stale_after_days":30,"source":"Drive: Cinema AI Director audit + Prompt Master ledger","syntax":["--ar","--style raw","--oref","--sref","--stylize","--seed"],"version_sensitive":True},
 "veo":{"version":"3.x-family-not-provider-verified","verified_at":"2026-09-30","stale_after_days":14,"source":"Drive: Veo guide + Cinema AI Director audit","syntax":["Audio:","dialogue","last-frame continuity"],"version_sensitive":True},
 "runway":{"version":"Gen-4.x-family-not-provider-verified","verified_at":"2026-09-30","stale_after_days":14,"source":"Drive: Cinema AI Director audit","syntax":["positive sequential action","reference keyframe"],"version_sensitive":True},
 "kling":{"version":"2.x/3.x-family-not-provider-verified","verified_at":"2026-09-30","stale_after_days":14,"source":"Drive: Blue Diamond/Pokemon/Shining Star specs","syntax":["Start frame","End frame","motion"],"version_sensitive":True},
 "sora":{"version":"source-family-not-provider-verified","verified_at":"2026-09-30","stale_after_days":14,"source":"Drive: cinematic studio specs","syntax":["scene/action/physics","camera intent"],"version_sensitive":True},
 "nanobanana":{"version":"source-family-not-provider-verified","verified_at":"2026-09-30","stale_after_days":30,"source":"Drive: Nano Banana samples + 360 reference workflow","syntax":["reference-led edit","cross-view consistency"],"version_sensitive":True},
 "chatgpt":{"version":"generic-image-brief","verified_at":"2026-09-30","stale_after_days":60,"source":"v4 durable visual prompt principles","syntax":["subject","action","environment","camera","lighting","constraints"],"version_sensitive":False},
 "flux":{"version":"generic-source-profile","verified_at":"2026-09-30","stale_after_days":60,"source":"Drive: cinematic prompt corpus","syntax":["subject","composition","materials","lighting"],"version_sensitive":False},
 "sdxl":{"version":"generic-source-profile","verified_at":"2026-09-30","stale_after_days":60,"source":"Drive: cinematic prompt corpus","syntax":["positive prompt","optional negative prompt","composition"],"version_sensitive":False},
 "ideogram":{"version":"generic-source-profile","verified_at":"2026-09-30","stale_after_days":60,"source":"Drive: prompt corpus","syntax":["subject","layout","text placement when requested"],"version_sensitive":False},
 "legacy-midjourney-v5":{"version":"V5.1","verified_at":"2023-01-01","stale_after_days":30,"source":"Drive: Midjourney Comprehensive Guide V4/V5/V5.1","syntax":["--ar","--seed","--iw"],"version_sensitive":True},
}

def resolve_adapter(platform:str, *, as_of:str, provider_verified:bool=False)->dict:
    p=(platform or "").lower().strip()
    if p not in REGISTRY:
        return {"platform":p,"known":False,"version":None,"freshness":"unknown","current_syntax_verified":False,"source":None,"syntax":[],"version_sensitive":True,"rule":"unknown adapter; verify current provider docs before syntax claims"}
    rec=dict(REGISTRY[p])
    try:age=(date.fromisoformat(as_of[:10])-date.fromisoformat(rec["verified_at"])).days
    except Exception:age=None
    freshness="unknown" if age is None else ("fresh" if age<=rec["stale_after_days"] else "stale")
    current=bool(provider_verified and freshness=="fresh")
    return {"platform":p,"known":True,**rec,"age_days":age,"freshness":freshness,"current_syntax_verified":current,"requires_live_verification":bool(rec.get("version_sensitive") and not current),"rule":"source-derived syntax is a versioned hint; provider verification is required before representing version-sensitive syntax as current"}
