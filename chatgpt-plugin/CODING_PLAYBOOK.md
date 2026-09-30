# Coding Playbook (Knowledge file)

## Default stacks
| Need | Choice |
|---|---|
| Web frontend | React + TypeScript + Vite + Tailwind |
| Full-stack | Next.js (App Router) + TypeScript |
| API | FastAPI (Python) or Hono/Express (Node) |
| DB | PostgreSQL + Prisma/SQLAlchemy; SQLite for small |
| Mobile | Flutter or React Native (Expo) |
| Edge/serverless | Cloudflare Workers + D1/KV/R2 |
| Scripts/data | Python 3.12 + pandas |

## Pre-delivery checklist
- [ ] Code runs as-is; all imports present
- [ ] Inputs validated; errors handled with clear messages
- [ ] No secrets in code (.env + .env.example)
- [ ] SQL parameterized; HTML output escaped
- [ ] Edge cases: empty, null, huge input, unicode/Arabic, concurrency
- [ ] Tests for the main path + 1 edge case
- [ ] README: install, env vars, run, test

## Debug method
1. Read the full error + stack trace (bottom-up for Python, top-down for JS)
2. Reproduce minimally
3. Hypothesis → check → fix the root cause, not the symptom
4. Add a test that would have caught it

## Review severity
🔴 Critical: security, data loss, crash · 🟠 High: wrong logic · 🟡 Medium: performance, maintainability · 🟢 Low: style

## Security top 10 reminders
Injection · broken auth · secret leaks · XSS · CSRF · SSRF · insecure deserialization · missing rate limits · verbose errors in prod · outdated deps
