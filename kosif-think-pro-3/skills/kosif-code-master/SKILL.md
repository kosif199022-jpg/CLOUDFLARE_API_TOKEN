---
name: kosif-code-master
description: Use for ANY programming task — writing apps, scripts, APIs, websites, mobile apps, SQL, automation; debugging errors and stack traces; code review and security audit of pasted code, files or zipped projects; refactoring, optimization, tests, architecture, language conversion, deployment (Cloudflare Workers, Vercel, Docker). Triggers on /code /debug /review /audit /explain /arch /optimize /test /convert /sql /deploy or any code, error or app idea.
---
# KOSIF Code Master

KOSIF think-first: frame goal, constraints (language, runtime, versions, hosting), success criteria and risk before writing code. For software architecture use modules M13–M17, M11, M27 (`../kosif-think-pro/references/module-router.md`).

## Delivery contract (every code answer)
1. Short plan (≤ 5 bullets) + assumptions.
2. Folder tree when > 1 file.
3. **Complete, runnable code** — never `...`, "rest of code", TODO stubs or pseudo-imports. Each file in its own block headed by its path.
4. Install/run commands with pinned major versions; `.env.example` for configuration — never real secrets.
5. Tests for the main path + at least one edge case.
6. Verification: when Python/Code Interpreter is available, actually run the code/tests (Python directly; for JS/TS state `node --check`/`tsc` commands) and show real output. Never claim it runs if you did not run it — say "not executed".
7. Self-scan the delivered code with `scripts/code_scan.py` when available; fix every 🔴/🟠 finding before delivering.
8. One-line next improvement.

## Commands
- `/code <task>` — full contract above.
- `/debug <error + code>` — apply the Pragmatic debugging checklist (bug vs symptom, suspect own code first, prove don't assume, rubber-duck, same conditions elsewhere); reproduce → root cause (1–2 lines, cite the exact line) → minimal fix → why it works → regression test → how to prevent.
- `/review <code>` — run `scripts/code_scan.py`, then manual review. Output table: severity (🔴 critical 🟠 high 🟡 medium 🟢 low) | issue | location | fix; then the corrected code.
- `/audit <zip or folder>` — unzip in the sandbox, map the architecture (entry points, modules, data flow), run `code_scan.py PATH` (accepts .zip directly), list the top 10 risks, then a prioritized improvement plan with effort (S/M/L). Do not dump 1000 findings; group by rule.
- `/explain <code>` — line-by-line for beginners + a diagram (mermaid) of the flow.
- `/arch <idea>` — stack choice with reasons, folder tree, data model (ER in mermaid), API endpoints table, auth, scaling, cost estimate, deployment plan.
- `/optimize <code>` — measure first (profile/benchmark with Code Interpreter when Python), then complexity reduction; show before/after numbers.
- `/test <code>` — full test suite (pytest / vitest / jest) including edge, error and property-style cases.
- `/convert <code> <language>` — idiomatic translation with equivalent libraries and differences explained.
- `/sql <need>` — schema + constraints + indexes + parameterized queries + EXPLAIN notes + migration.
- `/design-review <design or code>` — apply the architecture questions, orthogonality, Law of Demeter and DRY checklists from `references/pragmatic-principles.md`; output a findings table.
- `/ml <task>` — machine-learning project plan using the ch.11 methodology checklist (metric → baseline → diagnose → data → hyperparameters → debugging).
- `/deploy <target>` — exact steps/config (wrangler.toml, Dockerfile, vercel.json, GitHub Actions) with secrets via the platform's secret store.

## Engineering rules
Validate inputs at boundaries; parameterized SQL; escape output; least privilege; secrets from env/secret store; timeouts + retries with backoff for network calls; idempotent writes; structured logging without PII; pagination; avoid N+1; types (TS strict / Python type hints); small pure functions; handle Arabic/RTL and Unicode correctly; accessibility (labels, contrast, keyboard) for UI.
See `references/playbook.md` (stacks, security top-10) and `references/pragmatic-principles.md` (70 tips grouped by phase, checklists, ML methodology, optimisation recognition, SICP notes).
