#!/usr/bin/env python3
"""Compact Council-100 generator + adaptive chamber router for v4.
100 lenses are not 100 independent model sources.
"""
from __future__ import annotations
CHAMBERS=("evidence","strategy","risk","creativity","human","engineering","design","media","finance-audit","automation-agents")
KEYWORDS={
 "evidence":{"verify","evidence","source","research","fact","دليل","تحقق"},
 "strategy":{"plan","decision","strategy","tradeoff","خطة","قرار"},
 "risk":{"risk","security","secret","rollback","destructive","خطر","أمان"},
 "creativity":{"idea","creative","story","concept","إبداع","قصة"},
 "human":{"user","behavior","accessibility","human","مستخدم","إنسان"},
 "engineering":{"code","api","github","deploy","database","build","كود","برمجة","نشر"},
 "design":{"ui","ux","web","typography","layout","تصميم","واجهة"},
 "media":{"image","video","audio","camera","lighting","صورة","فيديو","صوت","إضاءة"},
 "finance-audit":{"audit","ifrs","vat","ledger","finance","مراجعة","محاسبة","ضريبة"},
 "automation-agents":{"agent","automation","tool","browser","computer","وكيل","أتمتة","أداة"},
}
PROBES={
 "evidence":["overclaim","fallacies","seal"],"strategy":["scenario","weighted_rank"],"risk":["secrets","pii","checkpoint"],
 "creativity":["prompt_parts","readability"],"human":["readability","touch_target"],"engineering":["complexity","retry_safe","git_class"],
 "design":["contrast","type_scale","touch_target"],"media":["ev100","beat","lufs_target"],"finance-audit":["vat","npv","benford"],
 "automation-agents":["budget","loop_detect","checkpoint"]}

def build_council() -> dict:
    members=[]; caps=[]
    for ci,ch in enumerate(CHAMBERS,1):
        for i in range(1,11):
            pid=f"C{ci:02d}-P{i:02d}"
            pcaps=[f"{ch}:capability:{i:02d}:{j:02d}" for j in range(1,21)]
            caps.extend(pcaps)
            members.append({"id":pid,"chamber":ch,"specialty":f"{ch} specialist {i}","capabilities":pcaps,"probes":PROBES[ch][:(i%3)+1]})
    return {"version":"4.0.0","members":members,"chambers":list(CHAMBERS),"capabilities_total":len(caps),"capabilities_unique":len(set(caps)),"independence_rule":"All personas sharing one underlying model/source count as one provenance source."}

def select_members(task: str, mode: str="standard") -> dict:
    low=(task or "").lower(); chambers={"evidence"}
    for ch,words in KEYWORDS.items():
        if any(w in low for w in words): chambers.add(ch)
    if any(w in low for w in ("risk","secret","deploy","write","send","delete","payment","خطر","حذف","نشر")): chambers.add("risk")
    if mode in {"pro","full"}: chambers.add("strategy")
    count_per={"standard":1,"pro":2,"full":10}.get(mode,1)
    council=build_council(); chosen=[]
    for ch in sorted(chambers):
        chosen.extend([m for m in council["members"] if m["chamber"]==ch][:count_per])
    return {"mode":mode,"chambers":sorted(chambers),"members":[m["id"] for m in chosen],"probes":sorted({p for m in chosen for p in m["probes"]}),"independence_note":"Council personas sharing one model/source count as one provenance source; add another model, deterministic probe or primary source for real independence."}
