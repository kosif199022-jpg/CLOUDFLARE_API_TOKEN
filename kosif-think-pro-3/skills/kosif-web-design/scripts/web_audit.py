#!/usr/bin/env python3
import re

def audit(html:str, meta:dict|None=None)->dict:
    meta=meta or {}; issues=[]; low=html.lower()
    for m in re.finditer(r'<img\b[^>]*>',html,re.I):
        if not re.search(r'\balt\s*=',m.group(0),re.I): issues.append('image missing alt')
    for m in re.finditer(r'<button\b[^>]*>(.*?)</button>',html,re.I|re.S):
        text=re.sub(r'<[^>]+>','',m.group(1)).strip(); tag=m.group(0)
        if not text and not re.search(r'aria-label\s*=',tag,re.I): issues.append('button missing accessible name')
    if meta.get('direction')=='rtl' and not re.search(r'\b(dir=["\']rtl["\']|direction\s*:\s*rtl)',low): issues.append('RTL requested but not declared')
    return {'verdict':'PASS' if not issues else 'REVISE','issues':issues,'checks':['accessible-name','image-alt','rtl-declaration']}
