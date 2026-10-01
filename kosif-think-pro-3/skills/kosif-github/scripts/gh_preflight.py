#!/usr/bin/env python3
import re
REMOTE_WRITE={'push','create-pr','merge','release','delete-branch','force-push'}
SECRET=[re.compile(r'AIza[0-9A-Za-z_-]{20,}'),re.compile(r'(?i)(token|secret|api[_-]?key)\s*[:=]\s*["\'][^"\']{12,}["\']')]

def preflight(state:dict)->dict:
    op=str(state.get('operation','read')).lower(); issues=[]; files=state.get('files') or {}
    for path,content in files.items():
        if any(p.search(str(content)) for p in SECRET): issues.append(f'possible secret in {path}')
    if op in REMOTE_WRITE and not state.get('tests_passed'): issues.append('remote write requires fresh passing tests')
    if op in {'force-push','delete-branch'} and not state.get('explicit_approval'): issues.append('destructive Git action requires explicit approval')
    return {'verdict':'BLOCK' if issues else 'PASS','issues':issues,'operation':op,'rule':'fresh target + tests + secret scan before remote writes'}
