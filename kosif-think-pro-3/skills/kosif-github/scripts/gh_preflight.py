#!/usr/bin/env python3
"""KOSIF GitHub — pre-flight gate for git/GitHub operations.

stdin JSON (every field optional except one of operations/operation):
{"operations": ["git commit -m '...'", "git push -u origin feature/x", "create_pull_request"],
 "branch": "feature/x", "designated_branch": "feature/x", "default_branch": "main",
 "approved": false,                           # the user explicitly approved remote writes for THIS task
 "own_branch": true,                          # branch was created by us in this task (rewrites allowed there only)
 "diff": "unified diff text",                 # scanned on added lines only
 "files": [{"path": "data.bin", "size_bytes": 7340032}],
 "commit_message": "Fix login redirect\n\nWhy ...",
 "pr_title": "...", "pr_body": "...", "pr_template": "## Summary\n## Test plan"}
Classes: read-only · local-write · remote-write · destructive.
Verdict: PASS (safe) · CONFIRM (remote write — needs explicit user approval) · BLOCK (must not run as is).
Exit 0 PASS · 1 CONFIRM · 3 BLOCK · 2 invalid.
"""
import json
import re
import sys

GIT = [("destructive", r"push\s+(?:\S+\s+)*(-f|--force)(?!-with-lease)\b|reset\s+--hard|branch\s+-D\b|clean\s+-[a-z]*f|filter-(branch|repo)|push\s+\S+\s+:\S+|push\s+(?:\S+\s+)*--delete|delete_(file|branch|repo)|gh\s+repo\s+delete|update-ref\s+-d"),
       ("remote-write", r"\bgit\s+push\b|\bpush_files\b|\bcreate_or_update_file\b|pr\s+(create|merge|edit|close|comment|review)|create_pull_request|merge_pull_request|update_pull_request|add_issue_comment|issue_write|pull_request_review_write|release\s+create|\bgh\s+api\b.*-X\s*(POST|PATCH|PUT|DELETE)|create_branch|enable_pr_auto_merge"),
       ("local-write", r"\bgit\s+(commit|checkout|switch|merge|rebase|add|stash|tag|init|clone|cherry-pick|revert|mv|rm|restore|apply|am|pull)\b"),
       ("read-only", r"\bgit\s+(status|log|diff|show|fetch|blame|branch|remote|rev-parse|ls-files|grep|describe)\b|get_file_contents|list_|search_|pull_request_read|issue_read|get_commit|get_job_logs|actions_(get|list)")]
SECRET = {
    "openai-key": r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}", "anthropic-key": r"\bsk-ant-[A-Za-z0-9_-]{20,}",
    "github-token": r"\bgh[pousr]_[A-Za-z0-9]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}", "aws-key": r"\bAKIA[0-9A-Z]{16}\b",
    "slack-token": r"\bxox[baprs]-[A-Za-z0-9-]{10,}", "private-key": r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    "google-api-key": r"\bAIza[0-9A-Za-z_-]{35}\b", "stripe-key": r"\b(sk|rk)_live_[0-9a-zA-Z]{20,}",
    "password-assignment": r"(?i)\b(pass(word)?|pwd|secret|api_?key|access_?token|auth_?token)\s*[=:]\s*['\"][^'\"\s]{8,}['\"]",
    "cloudflare-token": r"(?i)(cf|cloudflare)_?(api)?_?token\s*[=:]\s*['\"]?[A-Za-z0-9_-]{35,}",
}
PAST = {"added", "fixed", "updated", "removed", "changed", "created", "refactored", "improved", "deleted", "renamed", "implemented", "moved"}


def classify(op):
    for cls, rx in GIT:
        if re.search(rx, op, re.I):
            return cls
    return "unknown"


def added_lines(diff):
    path, out = None, []
    for line in diff.splitlines():
        if line.startswith("+++ "):
            path = line[4:].strip()
            path = path[2:] if path.startswith("b/") else path
        elif line.startswith("+") and not line.startswith("+++"):
            out.append((path, line[1:]))
    return out


def run(o):
    ops = o.get("operations") or ([o["operation"]] if o.get("operation") else [])
    if not ops and not any(o.get(k) for k in ("diff", "commit_message", "pr_body", "files")):
        raise ValueError("give operations/operation, or a diff/commit/PR to check")
    findings, verdict = [], "PASS"
    order = ["PASS", "CONFIRM", "BLOCK"]

    def flag(level, msg):
        nonlocal verdict
        findings.append({"level": level, "message": msg})
        verdict = max(verdict, level, key=order.index)

    branch, designated = o.get("branch"), o.get("designated_branch")
    default = o.get("default_branch", "main")
    classes = []
    for op in ops:
        cls = classify(op)
        classes.append({"operation": op, "class": cls})
        target = None
        m = re.search(r"\bpush\b(?:\s+-\S+)*\s+\S+\s+(?:HEAD:)?([\w./-]+)", op)
        if m:
            target = m.group(1)
        if cls == "destructive":
            if re.search(r"--force-with-lease", op) and o.get("own_branch") and o.get("approved"):
                findings.append({"level": "PASS", "message": f"force-with-lease on own branch approved: {op}"})
            else:
                flag("BLOCK", f"destructive operation: {op!r} — never on someone else's branch; needs explicit approval on your own")
        elif cls == "remote-write":
            if not o.get("approved"):
                flag("CONFIRM", f"remote write {op!r} is visible on GitHub — confirm the user asked for it")
            if target and designated and target != designated:
                flag("BLOCK", f"push target {target!r} differs from the designated branch {designated!r}")
            if (target or branch) == default and "push" in op:
                flag("BLOCK", f"direct push to the default branch {default!r}: open a pull request instead")
            if re.search(r"--force-with-lease", op) and not o.get("own_branch"):
                flag("BLOCK", "history rewrite on a branch you did not create")
        elif cls == "unknown":
            flag("CONFIRM", f"unrecognised operation {op!r}: treat as remote write until proven otherwise")
        if re.search(r"--no-verify\b", op):
            flag("BLOCK", "--no-verify skips the repository's hooks")
        if re.search(r"commit\s+(?:\S+\s+)*--amend", op) and not o.get("own_branch"):
            flag("BLOCK", "amending a commit on a shared branch rewrites history")
        if re.search(r"git\s+add\s+(-A|--all|\.)(\s|$)", op):
            findings.append({"level": "PASS", "message": "broad `git add` — check `git status` for unintended files before committing"})
    if branch and designated and branch != designated and any(c["class"] in {"remote-write", "local-write", "destructive"} for c in classes):
        flag("BLOCK", f"working on {branch!r} but the designated branch is {designated!r}")

    secrets = []
    for path, line in added_lines(o.get("diff", "")):
        for name, rx in SECRET.items():
            if re.search(rx, line):
                secrets.append({"file": path, "type": name})
        if path and re.search(r"(^|/)\.env(\.|$)(?!example|sample|template)", path):
            secrets.append({"file": path, "type": "dotenv-file"})
    seen = {(s["file"], s["type"]) for s in secrets}
    for f, t in sorted(seen, key=lambda x: (str(x[0]), x[1])):
        flag("BLOCK", f"possible secret ({t}) added in {f} — remove it, rotate the credential, use the platform secret store")
    for f in o.get("files", []):
        size = int(f.get("size_bytes", 0))
        if size > 50 * 1024 * 1024:
            flag("BLOCK", f"{f.get('path')} is {size / 1048576:.1f} MB (GitHub rejects > 100 MB and warns > 50 MB): use Git LFS or a release asset")
        elif size > 5 * 1024 * 1024:
            findings.append({"level": "PASS", "message": f"large file {f.get('path')} ({size / 1048576:.1f} MB): confirm it belongs in git"})
        if re.search(r"(^|/)(node_modules|__pycache__|\.venv|dist|build)/|\.pyc$|\.DS_Store$", f.get("path", "")):
            flag("CONFIRM", f"{f.get('path')} looks generated/vendored: check .gitignore")

    msg = o.get("commit_message")
    commit = None
    if msg is not None:
        lines = msg.strip().splitlines() or [""]
        subj = lines[0]
        problems = []
        if not subj:
            problems.append("empty subject")
        if len(subj) > 72:
            problems.append(f"subject is {len(subj)} chars (≤ 72)")
        if subj.endswith("."):
            problems.append("subject ends with a period")
        first = subj.split(":", 1)[-1].strip().split(" ")[0].lower() if subj else ""
        if first in PAST:
            problems.append(f"use the imperative mood ('{first[:-2] if first.endswith('ed') else first}…' instead of '{first}')")
        if re.search(r"\b(wip|tmp|asdf|fix stuff|misc)\b", subj, re.I):
            problems.append("uninformative subject")
        if len(lines) > 1 and lines[1].strip():
            problems.append("missing blank line between subject and body")
        if len(lines) < 3 and len(subj.split()) < 4:
            problems.append("no body: explain why the change is needed")
        commit = {"subject": subj, "problems": problems}
        if problems:
            findings.append({"level": "PASS", "message": "commit message: " + "; ".join(problems)})

    pr = None
    if o.get("pr_body") is not None or o.get("pr_title") is not None:
        body, title = o.get("pr_body") or "", o.get("pr_title") or ""
        problems = []
        if not title or len(title) > 72:
            problems.append("PR title missing or longer than 72 chars")
        if len(body.strip()) < 40:
            problems.append("PR body too thin: say what changed, why, and how it was tested")
        if not re.search(r"(?im)^#+\s*(test|testing|test plan|verification|how (it was|to) test)|\btested\b|\bpytest\b|\bnpm test\b|unittest|اختبار", body):
            problems.append("no test evidence in the PR body")
        tmpl = o.get("pr_template")
        if tmpl:
            heads = [h.strip().lower() for h in re.findall(r"(?m)^#+\s*(.+)$", tmpl)]
            have = [h.strip().lower() for h in re.findall(r"(?m)^#+\s*(.+)$", body)]
            missing = [h for h in heads if h not in have and not re.search(r"credential|token|secret|password|env", h)]
            if missing:
                problems.append(f"template sections missing: {missing}")
        if any(re.search(rx, body) for rx in SECRET.values()):
            flag("BLOCK", "secret-like value inside the PR body")
        pr = {"title": title, "problems": problems}
        if problems:
            findings.append({"level": "PASS", "message": "PR: " + "; ".join(problems)})
    return {"verdict": verdict, "operations": classes, "findings": findings, "secrets": sorted(({"file": f, "type": t} for f, t in seen), key=str),
            "commit": commit, "pull_request": pr,
            "rules": "PASS = safe to run · CONFIRM = ask/confirm the user wants this visible change · BLOCK = do not run"}


def main():
    try:
        out = run(json.load(sys.stdin))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"verdict": "INVALID", "error": str(e)}))
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return {"PASS": 0, "CONFIRM": 1, "BLOCK": 3}[out["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
