#!/usr/bin/env python3
import re, json
EMAIL=re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
PHONE=re.compile(r'(?<!\d)\+?\d[\d -]{7,}\d')

def _redact(v):
    if isinstance(v,str): return PHONE.sub('[REDACTED_PHONE]',EMAIL.sub('[REDACTED_EMAIL]',v))
    if isinstance(v,dict): return {k:_redact(x) for k,x in v.items()}
    if isinstance(v,list): return [_redact(x) for x in v]
    return v

def build(spec:dict)->dict:
    mode=spec.get('mode','choice')
    if mode not in {'choice','noul','score'}: raise ValueError('mode must be choice|noul|score')
    packet={'mode':mode,'question':spec.get('question'),'options':_redact(spec.get('options') or {}),'evidence':_redact(spec.get('evidence') or {}),'authority':'review-only','rule':'Jev is bounded judgement over supplied evidence; never execution approval or primary evidence'}
    return {'tool':{'choice':'jev_choice','noul':'jev_noul','score':'jev_score'}[mode],'packet':packet}
