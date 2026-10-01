#!/usr/bin/env python3
"""Secret sanitization gate for imported source text.
Heuristic only: findings require human/context review; never logs secret values.
"""
from __future__ import annotations
import re
PATTERNS=[
 ('openai',re.compile(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}\b')),
 ('github',re.compile(r'\bgh[pousr]_[A-Za-z0-9]{20,}\b')),
 ('google',re.compile(r'\bAIza[0-9A-Za-z_-]{20,}\b')),
 ('generic',re.compile(r'(?i)\b(?:api[_ -]?key|token|secret)\s*[:=]\s*["\']?([A-Za-z0-9_./+\-=]{20,})["\']?')),
]
def scan_text(text:str)->dict:
    findings=[]
    for kind,rx in PATTERNS:
        for m in rx.finditer(text or ''):
            findings.append({'type':kind,'start':m.start(),'end':m.end()})
    return {'blocked':bool(findings),'findings':findings,'rule':'Do not import/publish likely credentials until moved to a secret store.'}
def redact_text(text:str)->str:
    out=text or ''
    for _,rx in PATTERNS: out=rx.sub('[REDACTED_SECRET]',out)
    return out
