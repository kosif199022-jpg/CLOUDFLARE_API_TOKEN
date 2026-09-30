#!/usr/bin/env python3
"""KOSIF Code Master — fast static scanner (no dependencies).

usage: code_scan.py PATH [PATH ...] [--json]
  PATH may be a file, a directory (recursive) or a .zip archive.

Finds: leaked secrets, dangerous calls (eval/exec/shell=True/pickle/yaml.load/...),
injection-prone patterns (SQL string building, innerHTML, dangerouslySetInnerHTML),
weak crypto, TLS verification disabled, debug mode in production, placeholders that
make delivered code incomplete ("...", TODO, "rest of code"), and Python syntax errors.
Each finding has severity (critical/high/medium/low), rule, file:line and a fix hint.
It is a heuristic linter: findings need human/AI confirmation; absence of findings
is not proof of security.
"""
import ast
import io
import json
import os
import re
import sys
import zipfile

EXT = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".php", ".rb", ".go", ".java", ".kt", ".cs",
       ".sh", ".bash", ".sql", ".html", ".vue", ".svelte", ".swift", ".rs", ".c", ".cpp", ".h", ".yml",
       ".yaml", ".toml", ".json", ".env", ".ini", ".cfg", ".tf", ".dart"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__", ".venv", "venv", ".next", "vendor"}
MAX_BYTES = 1_500_000

R = [
    # secrets
    ("critical", "secret-aws-key", r"\bAKIA[0-9A-Z]{16}\b", "move to env var / secret manager and rotate the key"),
    ("critical", "secret-private-key", r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", "never commit private keys; rotate"),
    ("critical", "secret-github-token", r"\bgh[pousr]_[A-Za-z0-9]{36,}\b", "revoke the token and use env vars"),
    ("critical", "secret-openai-key", r"\bsk-(?:proj-|svcacct-|admin-)?(?=[A-Za-z0-9]{0,40}\d)[A-Za-z0-9]{20,}[A-Za-z0-9_\-]*",
     "revoke the key and load it from env"),
    ("critical", "secret-anthropic-key", r"\bsk-ant-[A-Za-z0-9_\-]{20,}\b", "revoke the key and load it from env"),
    ("critical", "secret-google-key", r"\bAIza[0-9A-Za-z_\-]{35}\b", "restrict/rotate the key and load it from env"),
    ("critical", "secret-slack-token", r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b", "revoke and use env vars"),
    ("critical", "secret-stripe-key", r"\b(sk|rk)_live_[A-Za-z0-9]{20,}\b", "revoke the live key immediately"),
    ("high", "secret-generic-assignment",
     r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token)\b\s*[:=]\s*['\"][^'\"\s]{8,}['\"]",
     "hardcoded credential: read it from environment/secret store"),
    ("high", "secret-jwt", r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}", "do not commit tokens"),
    # dangerous execution
    ("high", "py-eval-exec", r"(?<![\w.])(eval|exec)\s*\(", "avoid eval/exec on any external input; use ast.literal_eval/json"),
    ("high", "py-shell-true", r"subprocess\.\w+\([^)]*shell\s*=\s*True", "pass an argument list and shell=False"),
    ("high", "py-os-system", r"\bos\.(system|popen)\s*\(", "use subprocess.run([...], check=True) without a shell"),
    ("high", "py-pickle-load", r"\bpickle\.loads?\s*\(", "never unpickle untrusted data; use json"),
    ("high", "py-yaml-load", r"\byaml\.load\s*\((?![^)]*Loader\s*=\s*yaml\.SafeLoader)", "use yaml.safe_load"),
    ("high", "js-eval", r"(?<![\w.])(eval|new\s+Function)\s*\(", "avoid dynamic code evaluation"),
    ("high", "js-child-exec", r"child_process[^\n]*\bexec\s*\(|\bexecSync\s*\(", "use execFile/spawn with an args array"),
    # injection
    ("high", "sql-string-building",
     r"(?i)(execute|query|raw)\s*\(\s*(f['\"]|['\"][^'\"]*(select|insert|update|delete)[^'\"]*['\"]\s*(\+|%|\.format))",
     "use parameterized queries / placeholders"),
    ("high", "sql-template-literal", r"(?i)(query|execute)\s*\(\s*`[^`]*(select|insert|update|delete)[^`]*\$\{", "use bound parameters"),
    ("medium", "xss-innerhtml", r"\.innerHTML\s*\+?=(?!\s*(['\"`])\1)|\.outerHTML\s*=|document\.write\s*\(", "use textContent or sanitize (DOMPurify)"),
    ("medium", "xss-react-dangerous", r"dangerouslySetInnerHTML", "sanitize HTML before rendering"),
    # crypto/tls/config
    ("medium", "weak-hash", r"(?i)\b(md5|sha1)\s*\(|hashlib\.(md5|sha1)\b|createHash\(['\"](md5|sha1)", "use SHA-256+; for passwords use bcrypt/argon2"),
    ("low", "insecure-random", r"\bMath\.random\s*\(|\brandom\.(random|randint|choice)\s*\(", "use secrets / crypto.getRandomValues for tokens"),
    ("high", "tls-verify-disabled", r"verify\s*=\s*False|rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0|InsecureSkipVerify\s*:\s*true", "keep TLS verification on"),
    ("medium", "debug-enabled", r"(?i)\bdebug\s*=\s*True\b|app\.run\([^)]*debug\s*=\s*True", "disable debug in production"),
    ("medium", "cors-wildcard", r"Access-Control-Allow-Origin['\"]?\s*[:,]\s*['\"]\*['\"]|cors\(\s*\)", "restrict allowed origins"),
    ("low", "http-url", r"['\"]http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)[^'\"\s]+['\"]", "prefer https"),
    # completeness
    ("medium", "placeholder-code", r"(?i)(rest of (the )?code|your code here|implement (this|me)|\.\.\.\s*(existing|rest|more) code|// \.\.\.$|# \.\.\.$)", "deliver complete code: remove placeholders"),
    ("low", "todo-marker", r"\b(TODO|FIXME|XXX|HACK)\b", "resolve or track the TODO"),
    ("low", "bare-except", r"^\s*except\s*:\s*$", "catch specific exceptions"),
    ("low", "console-log", r"\bconsole\.log\s*\(", "remove debug logging or use a logger"),
]
JS_LIKE = {".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".html", ".vue", ".svelte"}
SCOPE = {"py-": {".py"}, "js-": JS_LIKE, "xss-": JS_LIKE, "console-": JS_LIKE, "bare-except": {".py"}}
COMPILED = [(s, n, re.compile(p, re.M), h) for s, n, p, h in R]


def applies(rule, name):
    ext = os.path.splitext(name)[1].lower()
    for prefix, exts in SCOPE.items():
        if rule.startswith(prefix):
            return ext in exts
    return True
ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def iter_files(paths):
    for p in paths:
        if p.lower().endswith(".zip") and os.path.isfile(p):
            with zipfile.ZipFile(p) as z:
                for info in z.infolist():
                    parts = info.filename.split("/")
                    if info.is_dir() or any(x in SKIP_DIRS for x in parts) or info.file_size > MAX_BYTES:
                        continue
                    if os.path.splitext(info.filename)[1].lower() in EXT or parts[-1].startswith(".env"):
                        yield f"{os.path.basename(p)}:{info.filename}", z.read(info).decode("utf-8", "replace")
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for f in files:
                    fp = os.path.join(root, f)
                    if (os.path.splitext(f)[1].lower() in EXT or f.startswith(".env")) and os.path.getsize(fp) <= MAX_BYTES:
                        with io.open(fp, encoding="utf-8", errors="replace") as fh:
                            yield fp, fh.read()
        elif os.path.isfile(p):
            with io.open(p, encoding="utf-8", errors="replace") as fh:
                yield p, fh.read()


def scan_text(name, text):
    out = []
    lines = text.splitlines()
    is_min = name.endswith((".min.js", ".min.css")) or (text.count("\n") < 3 and len(text) > 5000)
    for sev, rule, rx, hint in COMPILED:
        if (is_min and sev == "low") or not applies(rule, name):
            continue
        for m in rx.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            src = lines[line - 1] if line <= len(lines) else ""
            if re.search(r"kosif-scan:\s*ignore", src):
                continue
            snippet = src.strip()[:160]
            if rule.startswith("secret"):
                snippet = re.sub(r"([A-Za-z0-9_\-]{4})[A-Za-z0-9_\-]{8,}", r"\1…", snippet)
            out.append({"severity": sev, "rule": rule, "file": name, "line": line, "code": snippet, "fix": hint})
    if name.endswith(".py"):
        try:
            ast.parse(text)
        except SyntaxError as e:
            out.append({"severity": "high", "rule": "python-syntax-error", "file": name, "line": e.lineno or 0,
                        "code": (e.text or "").strip()[:160], "fix": f"fix syntax: {e.msg}"})
    return out


def scan(paths):
    findings, files = [], 0
    for name, text in iter_files(paths):
        files += 1
        findings += scan_text(name, text)
    findings.sort(key=lambda f: (ORDER[f["severity"]], f["file"], f["line"]))
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in ORDER}
    # per-rule capped penalty so one noisy pattern cannot hide everything else
    weight = {"critical": 25, "high": 10, "medium": 3, "low": 1}
    per_rule = {}
    for f in findings:
        per_rule.setdefault((f["severity"], f["rule"]), 0)
        per_rule[(f["severity"], f["rule"])] += 1
    penalty = sum(weight[sev] * (n if sev == "critical" else min(n, 5)) for (sev, _), n in per_rule.items())
    score = max(0, 100 - penalty)
    return {"ok": counts["critical"] == 0 and counts["high"] == 0, "files_scanned": files, "counts": counts,
            "score": score, "findings": findings,
            "scope": "heuristic static scan; confirm each finding; no findings is not proof of security"}


def table(r):
    icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
    lines = ["| | القاعدة | الموقع | الإصلاح |", "|---|---|---|---|"]
    shown = {}
    for f in r["findings"]:
        shown[f["rule"]] = shown.get(f["rule"], 0) + 1
        if shown[f["rule"]] <= 8:
            lines.append(f"| {icon[f['severity']]} | {f['rule']} | {f['file']}:{f['line']} | {f['fix']} |")
    hidden = {k: v - 8 for k, v in shown.items() if v > 8}
    if hidden:
        lines.append("\n+ " + ", ".join(f"{k}: {v} more" for k, v in hidden.items()) + " (use --json for all)")
    c = r["counts"]
    lines.append(f"\nالنتيجة: {r['score']}/100 · 🔴{c['critical']} 🟠{c['high']} 🟡{c['medium']} 🟢{c['low']} · ملفات: {r['files_scanned']}")
    return "\n".join(lines)


def main(argv):
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 2
    r = scan(paths)
    print(json.dumps(r, ensure_ascii=False, indent=1) if "--json" in argv else table(r))
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
