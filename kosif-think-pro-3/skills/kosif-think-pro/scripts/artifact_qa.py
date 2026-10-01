#!/usr/bin/env python3
"""Deterministic artifact QA for common deliverable containers."""
from __future__ import annotations
import json, re, zipfile
from pathlib import Path

SECRET_PATTERNS=[re.compile(r"AIza[0-9A-Za-z_-]{20,}"),re.compile(r"sk-[A-Za-z0-9_-]{20,}"),re.compile(r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"][^'\"]{12,}['\"]")]

def _result(path, verdict, checks, issues):
    return {"path":str(path),"verdict":verdict,"checks":checks,"issues":issues}

def verify_artifact(path) -> dict:
    p=Path(path); checks=[]; issues=[]
    if not p.exists() or not p.is_file(): return _result(p,"BLOCK",checks,["missing artifact"])
    if p.stat().st_size==0: return _result(p,"BLOCK",checks,["empty artifact"])
    ext=p.suffix.lower(); checks.append("non-empty")
    if ext==".json":
        try: json.loads(p.read_text(encoding="utf-8")); checks.append("json-parse")
        except Exception as e: issues.append(f"invalid JSON: {e}")
    elif ext in {".docx",".xlsx",".pptx"}:
        required={".docx":["[Content_Types].xml","word/document.xml"],".xlsx":["[Content_Types].xml","xl/workbook.xml"],".pptx":["[Content_Types].xml","ppt/presentation.xml"]}[ext]
        try:
            with zipfile.ZipFile(p) as z:
                names=set(z.namelist()); missing=[x for x in required if x not in names]
                if missing: issues.append("missing package members: "+", ".join(missing))
                else: checks.append("opc-structure")
                bad=z.testzip()
                if bad: issues.append("corrupt zip member: "+bad)
                else: checks.append("zip-integrity")
        except Exception as e: issues.append(f"invalid OPC zip: {e}")
    elif ext==".pdf":
        head=p.read_bytes()[:5]
        if head!=b"%PDF-": issues.append("missing PDF header")
        else: checks.append("pdf-header")
    elif ext in {".py",".js",".ts",".tsx",".jsx",".md",".txt",".html",".css"}:
        try: txt=p.read_text(encoding="utf-8",errors="replace")
        except Exception: txt=""
        leaked=[pat.pattern for pat in SECRET_PATTERNS if pat.search(txt)]
        if leaked: issues.append("possible embedded secret")
        else: checks.append("secret-scan-basic")
    verdict="PASS" if not issues else "BLOCK"
    return _result(p,verdict,checks,issues)
