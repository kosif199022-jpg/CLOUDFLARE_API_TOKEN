#!/usr/bin/env python3
"""Source Atlas 4.0.1: exact/near dedup, retrieval weighting, quarantine and freshness."""
from __future__ import annotations
from collections import defaultdict
from datetime import date, timedelta
import hashlib, re
from typing import Any, Iterable, Mapping

TOKEN_RE=re.compile(r"[\w\u0600-\u06ff]+",re.UNICODE)
EXCLUDED_KINDS={"operational-private","generated","vendor","build","git-object","secret","credential"}

def _tokens(text: str) -> set[str]:
    return {x.lower() for x in TOKEN_RE.findall(text or "") if len(x)>1}

def _jaccard(a:set[str], b:set[str]) -> float:
    if not a and not b:return 1.0
    if not a or not b:return 0.0
    return len(a & b)/len(a | b)

def _age_days(modified:str|None, as_of:str)->int|None:
    if not modified:return None
    try:return (date.fromisoformat(as_of[:10])-date.fromisoformat(modified[:10])).days
    except Exception:return None

def _freshness(record:Mapping[str,Any], as_of:str)->str:
    raw=record.get("modified") or record.get("verified_at") or record.get("read_at")
    if not raw:return "unknown"
    try:
        d=date.fromisoformat(str(raw)[:10]); now=date.fromisoformat(as_of[:10])
    except Exception:return "unknown"
    days=record.get("stale_after_days")
    if days in (None,""):return "unknown"
    try:return "stale" if now>d+timedelta(days=int(days)) else "fresh"
    except Exception:return "unknown"

def _content_hash(text:str)->str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()

def build_atlas(records:Iterable[Mapping[str,Any]], *, as_of:str, near_threshold:float=0.75)->dict[str,Any]:
    recs=[dict(r) for r in records]
    exact=defaultdict(list); quarantine={"empty":[],"operational_private":[],"generated_vendor":[],"secret":[]}; token_map={}; normalized=[]
    for idx,r in enumerate(recs):
        name=str(r.get("name") or f"unnamed-{idx+1}")
        text=str(r.get("text") or "")
        sha=str(r.get("sha256") or "").strip() or _content_hash(text)
        kind=str(r.get("kind") or "knowledge")
        exact[sha].append(name)
        if not text.strip():quarantine["empty"].append(name)
        if kind=="operational-private":quarantine["operational_private"].append(name)
        if kind in {"generated","vendor","build","git-object"}:quarantine["generated_vendor"].append(name)
        if kind in {"secret","credential"}:quarantine["secret"].append(name)
        tok=_tokens(text); token_map[name]=tok; age=_age_days(r.get("modified"),as_of)
        eligible=bool(text.strip()) and kind not in EXCLUDED_KINDS
        normalized.append({
            "name":name,"sha256":sha,"hash_source":"provided" if r.get("sha256") else "computed-from-text",
            "kind":kind,"age_days":age,"freshness":_freshness(r,as_of),
            "eligible_for_knowledge":eligible,"retrieval_weight":1 if eligible else 0,
            "duplicate_of":None,
        })
    by_name={r["name"]:r for r in normalized}
    exact_groups=[]
    for vals in exact.values():
        if len(vals)<=1:continue
        group=sorted(vals); exact_groups.append(group)
        eligible=[n for n in group if by_name[n]["eligible_for_knowledge"]]
        canonical=eligible[0] if eligible else group[0]
        for n in group:
            if n!=canonical:
                by_name[n]["retrieval_weight"]=0; by_name[n]["duplicate_of"]=canonical
            elif not by_name[n]["eligible_for_knowledge"]:
                by_name[n]["retrieval_weight"]=0
    exact_groups.sort()
    names=list(token_map); graph={n:set() for n in names}
    for i,a in enumerate(names):
        for b in names[i+1:]:
            if _jaccard(token_map[a],token_map[b])>=near_threshold:
                graph[a].add(b);graph[b].add(a)
    seen=set();near=[]
    for n in names:
        if n in seen or not graph[n]:continue
        stack=[n];comp=set()
        while stack:
            x=stack.pop()
            if x in comp:continue
            comp.add(x);stack.extend(graph[x]-comp)
        seen|=comp
        if len(comp)>1:near.append(sorted(comp))
    near.sort()
    return {
      "as_of":as_of,"records":normalized,"exact_duplicate_groups":exact_groups,"near_duplicate_groups":near,"quarantined":quarantine,
      "effective_retrieval_weight":sum(float(r["retrieval_weight"]) for r in normalized),
      "rules":{"duplicates":"preserve provenance records; exact duplicates receive one canonical retrieval vote","private":"never bake raw operational/private/secret content into durable knowledge","freshness":"version-sensitive claims need explicit freshness thresholds and execution-time verification"}
    }
