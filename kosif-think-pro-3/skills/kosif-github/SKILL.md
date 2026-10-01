---
name: kosif-github
description: Use for any git or GitHub work — branches, commits, pushes, pull requests, reviews, issues, releases, GitHub Actions CI, merge conflicts, repository setup, CODEOWNERS/branch protection, and watching a PR until it is green and merged. Works with GitHub MCP tools (mcp__github__*), the gh CLI or plain git, whichever the host exposes. Triggers on /gh /commit /pr /review-pr /ci /release /repo /conflict, "جيت هاب", "ارفع", "بول ريكوست", "فرع", "دمج", "كومِت".
---
# KOSIF GitHub Operator — safe, conventional, verified repository work

KOSIF think-first: frame the repository, branch, what must change, who will see it, and whether the user asked for anything visible on GitHub. Council lead: GitHub Maintainer (`../kosif-think-pro/scripts/council_select.py`, `"domains": ["github"]`).

## Operation classes (decide before acting)
| Class | Examples | Rule |
|---|---|---|
| read-only | status, log, diff, fetch, reading files/PRs/issues/CI logs | free |
| local-write | commit, branch, merge, rebase **on your own branch** | free, but on the designated branch only |
| remote-write | push, open/edit/merge PR, comment, review, create issue/release/branch | only when the user asked for it; say what will become visible |
| destructive | force-push, reset --hard on shared work, delete branch/repo, history rewrite | never on someone else's branch; on your own only with explicit approval |
Run `scripts/gh_preflight.py` with the operations, branch, designated branch, diff and messages. BLOCK ⇒ do not run. CONFIRM ⇒ the user must have asked for this visible change.

## Workflow
1. **Locate** — which repo and branch; which tool path is actually exposed (GitHub MCP tools, `gh`, or git over the proxy). Never assume a tool exists; if GitHub access is missing, say what the user must connect.
2. **Branch** — develop on the designated branch; create it from the latest default branch if it does not exist; never push elsewhere without permission.
3. **Change** — minimal diff for the task; run the repo's own fast checks (lint, typecheck, unit tests for changed packages) before committing.
4. **Commit** — imperative subject ≤ 72 chars, blank line, body explaining *why*; follow the repo's convention (Conventional Commits if used). Add attribution lines the host requires. Review `git status`/`git diff --staged` so no unintended files (env files, build output, large binaries) are included.
5. **Pre-flight** — `gh_preflight.py` on the diff (secrets on added lines, `.env` files, large/generated files) and the planned operations.
6. **Push** — `git push -u origin <branch>`; on network failure retry with backoff (2s, 4s, 8s, 16s); on rejection fetch and merge/rebase **your own** branch only.
7. **Pull request** (only if asked) — find the PR template (`.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE.md`, root or `docs/`), mirror its headings, fill from the actual diff, skip sections asking for secrets; include a test plan with real results.
8. **CI and reviews** — when watching a PR: fix red CI by root cause (reproduce locally first, then push one validated fix); a failure also red on the base branch is not yours — port an existing fix or explain once; never skip/disable tests, never empty commits to re-trigger; answer or implement every review comment; resolve merge conflicts with a merge commit on shared branches.
9. **Verify** — read back the pushed branch/PR state (commit SHA on the remote, PR URL, check status). "Pushed" means the remote shows the commit, not that the command exited 0.

## Commands
- `/gh <task>` — classify → plan → pre-flight → execute → verify.
- `/commit` — stage the intended files, write the message, run checks, commit (no push unless asked).
- `/pr [base]` — PR from the current branch with the template filled and test evidence.
- `/review-pr <url|number>` — read the diff, run `code_scan.py` on changed files, review for correctness/security/tests; findings table with file:line; post comments only if asked.
- `/ci <run|PR>` — fetch failing job logs, classify (this PR / base branch / infrastructure before tests ran), reproduce, fix, push once.
- `/conflict` — merge the base into the branch, resolve with both sides' intent, regenerate lockfiles with the tool (never by hand), run tests.
- `/release <version>` — changelog from commits, tag, release notes; confirm before publishing.
- `/repo <setup>` — .gitignore, README, LICENSE choice (the user decides), CODEOWNERS, branch protection advice, Actions workflow (`references/github-playbook.md`).

## Hard rules
Secrets never enter git (rotate any that did — deleting the line does not remove it from history) · no force-push/amend/rebase on branches you did not create · no pushing to the default branch directly · no PRs unless asked · no merging, approving or closing others' PRs unless asked · do not delete branches, tags or repos unless asked · attribution footers on posted comments when the host requires them · everything posted on GitHub is public to the repo's readers — keep it factual and brief.

References: `references/github-playbook.md` (commit/PR templates, Actions recipes, CI triage table, conflict recipes, useful MCP tool mapping).
