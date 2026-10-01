#!/usr/bin/env python3
from __future__ import annotations
import re, sys
from pathlib import Path
CORE=Path(__file__).resolve().parents[2]/'kosif-think-pro'/'scripts'
sys.path.insert(0,str(CORE))
from platform_adapter import resolve_adapter

IMAGE=['chatgpt','midjourney','flux','sdxl','ideogram','nanobanana']
VIDEO=['sora','veo','runway','kling']
QUALITY_RUBRIC={'subject_clarity':20,'camera_and_lens':20,'lighting_physics':20,'materials_and_texture':20,'platform_fit':20}
VAGUE=re.compile(r'\b(4k|8k|masterpiece|best quality|ultra[- ]?detailed|hyper[- ]?realistic|award[- ]winning|trending on artstation)\b',re.I)

def clean(x):return re.sub(r'\s+',' ',str(x or '')).strip().rstrip('.')

def iron_rules(sp):
    w=[];subj=clean(sp.get('subject'));light=clean(sp.get('lighting'));blob=' '.join(clean(sp.get(k)) for k in ('subject','style','quality'))
    if re.match(r'\s*(a|an)\s+(photo|picture|image)\s+of\b',subj,re.I):w.append("iron rule: start with the subject, not 'a photo/image of'")
    if VAGUE.search(blob):w.append('iron rule: replace vague quality boosters with concrete optical/material detail')
    if light and not re.search(r'\d{4}\s*k|key|rim|fill|window|left|right|above|behind|overcast|golden hour',light,re.I):w.append('iron rule: lighting needs source/direction/temperature or physical condition')
    return w

def variations(sp):
    lens=clean(sp.get('lens')) or '50mm f/2.8';light=clean(sp.get('lighting')) or 'soft natural light'
    return {'subtle':f'same intent, gentler contrast, {light}, restrained palette','dramatic':'same intent, stronger separation, directional key/rim, deeper shadows, tighter framing','technical':f'same intent, {lens}, explicit exposure/material/physics notes'}

def _provider_verified(sp,platform):
    pv=sp.get('provider_verified',False)
    if isinstance(pv,dict):return bool(pv.get(platform))
    return bool(pv)

def forge(sp):
    mode=sp.get('mode','image');subject=clean(sp.get('subject'))
    if mode not in {'image','video'}:raise ValueError('mode must be image or video')
    if not subject:raise ValueError('subject is required')
    platforms=sp.get('platforms') or (VIDEO if mode=='video' else IMAGE)
    unknown=[p for p in platforms if p not in IMAGE+VIDEO]
    if unknown:raise ValueError(f'unknown platforms {unknown}')
    aspect=clean(sp.get('aspect')) or '1:1';style=clean(sp.get('style'));lens=clean(sp.get('lens'));light=clean(sp.get('lighting'));env=clean(sp.get('environment'));action=clean(sp.get('action'));move=clean(sp.get('camera_move'));dur=clean(sp.get('duration')) or '5 seconds';dialogue=clean(sp.get('dialogue'));audio=clean(sp.get('audio'));neg=[clean(x) for x in sp.get('negative',[]) if clean(x)]
    warnings=iron_rules(sp);out={}
    for p in platforms:
        adapter=resolve_adapter(p,as_of=sp.get('as_of','2026-10-01'),provider_verified=_provider_verified(sp,p))
        core=', '.join(x for x in [subject,action,env,f'camera {lens}' if lens else '',f'lighting {light}' if light else '',style] if x)
        source_prompt=core;negative=', '.join(neg) if neg else None
        if p=='midjourney':source_prompt=f'{core} --ar {aspect} --style raw --v 7';negative=None
        elif p=='veo':
            source_prompt=f'{core}. Camera movement: {move or "stable shot"}. Duration {dur}. Aspect {aspect}.';bits=[]
            if dialogue:bits.append(f'The character says: "{dialogue}" (no subtitles)')
            if audio:bits.append(audio)
            if bits:source_prompt+=' Audio: '+'. '.join(bits)+'.'
            negative=None
        elif p=='runway':
            source_prompt=f'{core}. {move or "controlled camera movement"}. Duration {dur}. Aspect {aspect}.'
            source_prompt=re.sub(r'\b(no|without|avoid)\s+[^.,]+[.,]?\s*','',source_prompt,flags=re.I);negative=None
        elif p=='kling':source_prompt=f'Start: {core}. End: preserve identity and scene continuity after {dur}. Motion: {move or "natural"}. Aspect {aspect}.'
        elif p=='sora':source_prompt=f'{core}. Action/physics: {action or "natural motion"}. Camera: {move or "controlled"}. Duration {dur}. Aspect {aspect}.'
        elif p=='chatgpt':source_prompt=f'Create an image, aspect {aspect}. Subject: {core}.'
        elif p=='flux':source_prompt=f'{core}. Aspect ratio {aspect}.';negative=None
        elif p=='sdxl':source_prompt=core
        elif p=='ideogram':source_prompt=f'{core}, aspect {aspect}'
        elif p=='nanobanana':source_prompt=f'{core}. Preserve supplied references as identity/style anchors; apply only requested changes. Aspect {aspect}.'
        # Version-sensitive exact syntax is not presented as current unless provider-verified.
        if adapter.get('version_sensitive') and not adapter.get('current_syntax_verified') and p=='midjourney':
            prompt=f'{core}. Aspect ratio {aspect}. Keep style/reference controls version-neutral until current provider syntax is verified.'
        else:
            prompt=source_prompt
        out[p]={'prompt':prompt,'negative_prompt':negative,'source_syntax_prompt':source_prompt,'adapter':adapter,'syntax_status':'provider-verified-current' if adapter.get('current_syntax_verified') else 'source-derived-unverified-current'}
        if adapter.get('requires_live_verification'):
            warnings.append(f'{p}: version-sensitive source syntax is not provider-verified current; verify fresh provider docs before treating exact parameters as current')
    return {'mode':mode,'prompts':out,'warnings':sorted(set(warnings)),'variations':variations(sp),'quality_rubric':QUALITY_RUBRIC}
