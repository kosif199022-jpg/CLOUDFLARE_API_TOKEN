#!/usr/bin/env python3
from __future__ import annotations
from collections import defaultdict
from datetime import date
import re
TOKEN_RE=re.compile(r"[\w\u0600-\u06ff]+",re.UNICODE)

def _tokens(text):
    return {x.lower() for x in TOKEN_RE.findall(text or "") if len(x)>1}

def _jaccard(a,b):
    if not a and not b: return 1.0
    if not a or not b: return 0.0
    return len(a & b)/len(a | b)

def _age_days(modified,as_of):
    if not modified: return None
    try: return (date.fromisoformat(as_of[:10])-date.fromisoformat(str(modified)[:10])).days
    except Exception: return None

def build_atlas(records,*,as_of,near_threshold=0.75):
    recs=[dict(r) for r in records]
    exact=defaultdict(list); quarantine={"empty":[],"restricted":[],"generated":[]}; token_map={}; normalized=[]
    excluded={"restricted","generated","vendor","build","git-object","cache"}
    for r in recs:
        name=str(r.get("name") or "unnamed"); text=str(r.get("text") or ""); sha=str(r.get("sha256") or ""); kind=str(r.get("kind") or "knowledge")
        if sha: exact[sha].append(name)
        if not text.strip(): quarantine["empty"].append(name)
        if kind=="restricted": quarantine["restricted"].append(name)
        if kind in {"generated","vendor","build","git-object","cache"}: quarantine["generated"].append(name)
        token_map[name]=_tokens(text)
        normalized.append({"name":name,"sha256":sha,"kind":kind,"age_days":_age_days(r.get("modified"),as_of),"eligible_for_knowledge":bool(text.strip()) and kind not in excluded})
    exact_groups=sorted(sorted(v) for v in exact.values() if len(v)>1)
    graph={n:set() for n in token_map}; names=list(token_map)
    for i,a in enumerate(names):
        for b in names[i+1:]:
            if _jaccard(token_map[a],token_map[b])>=near_threshold:
                graph[a].add(b); graph[b].add(a)
    near=[]; seen=set()
    for n in names:
        if n in seen or not graph[n]: continue
        stack=[n]; comp=set()
        while stack:
            x=stack.pop()
            if x in comp: continue
            comp.add(x); stack.extend(graph[x]-comp)
        seen|=comp
        if len(comp)>1: near.append(sorted(comp))
    return {"as_of":as_of,"records":normalized,"exact_duplicate_groups":exact_groups,"near_duplicate_groups":sorted(near),"quarantined":quarantine,"rules":{"duplicates":"preserve provenance but collapse evidence weight","restricted":"exclude raw restricted content from durable public knowledge","freshness":"re-verify version-sensitive claims at execution time"}}
