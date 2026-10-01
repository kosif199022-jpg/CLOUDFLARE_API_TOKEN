#!/usr/bin/env python3
BLOCK=('captcha','otp','mfa','password','credential','payment','billing','buy','purchase')
RISKY=('delete','send','submit','install','uninstall','change setting','restart','format','factory reset')

def classify(state:dict)->dict:
    action=str(state.get('action','')).lower()
    if any(x in action for x in BLOCK): return {'verdict':'BLOCK','risk':'human-checkpoint','reason':'credential/payment/security checkpoint must stay human-controlled'}
    if any(x in action for x in RISKY) and not state.get('fresh_target_verified'): return {'verdict':'VERIFY','risk':'side-effect','reason':'fresh target/impact verification required'}
    return {'verdict':'PASS','risk':'read-only-or-low','reason':'no material checkpoint detected'}
