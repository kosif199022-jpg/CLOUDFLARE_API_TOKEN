# Code Master Playbook

## Default stacks
| Need | Default | Why |
|---|---|---|
| Web app | Next.js (App Router) + TypeScript + Tailwind | full-stack, SSR, ecosystem |
| SPA / dashboard | React + Vite + TypeScript | fast dev, simple deploy |
| API | FastAPI (Python) / Hono (TS, edge) | typed, fast, OpenAPI |
| Edge / serverless | Cloudflare Workers + D1 / KV / R2 / Queues | global, cheap, no servers |
| Database | PostgreSQL (+ Prisma / SQLAlchemy); SQLite/D1 for small | reliability |
| Mobile | Flutter or React Native (Expo) | one codebase |
| Automation / data | Python 3.12 + pandas / polars | libraries |
| AI features | official SDKs (Anthropic / OpenAI / Google), streaming, structured outputs | reliability |

## Pre-delivery checklist
- [ ] Runs as-is; all imports/deps listed with versions
- [ ] Inputs validated, errors handled with clear messages
- [ ] No secrets in code (.env + .env.example)
- [ ] SQL parameterized, HTML escaped, file paths sanitized
- [ ] Edge cases: empty, null, huge, Unicode/Arabic, concurrency, timezones
- [ ] Tests: main path + edge + failure
- [ ] README: install, env, run, test, deploy
- [ ] code_scan.py: no 🔴/🟠

## Debug method
Read the full trace → reproduce minimally → form one hypothesis → test it → fix the root cause → add a regression test → check for the same bug elsewhere.

## Security top-10
Injection (SQL/NoSQL/command) · broken auth & session · secret leakage · XSS · CSRF · SSRF · insecure deserialization · missing rate limits · verbose errors in production · vulnerable dependencies (npm audit / pip-audit).

## Review severity
🔴 critical: exploitable security, data loss, crash in main path · 🟠 high: wrong logic, missing validation · 🟡 medium: performance, maintainability · 🟢 low: style, naming.
