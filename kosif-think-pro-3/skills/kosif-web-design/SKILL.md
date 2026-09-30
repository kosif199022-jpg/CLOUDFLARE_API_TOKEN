---
name: kosif-web-design
description: Use for designing or building websites, landing pages, web apps, dashboards, UI components, design systems and themes — layout, typography (Arabic + Latin, RTL), colour tokens, dark mode, accessibility (WCAG), responsive/mobile-first, SEO, performance, conversion, and auditing an existing page or site. Triggers on /site /landing /ui /dashboard /tokens /webaudit /redesign /component, "صمم موقع", "صفحة هبوط", "واجهة", "لوحة تحكم", "تصميم ويب".
---
# KOSIF Web Design Studio — measured, accessible, mobile-first

KOSIF think-first: frame the page's single job, audience, device mix, language/direction, brand, content that exists (no invented numbers), and how success is measured. Select the council's design chamber with `../kosif-think-pro/scripts/council_select.py` (`"domains": ["web"]`) — it always brings the Accessibility Advocate.

## Pipeline
1. **Brief** — primary action, audience, languages (Arabic ⇒ `dir="rtl"`), brand colour(s), must-have sections, constraints (hosting, framework, single-file?), success metric.
2. **Information architecture** — sections in order of the user's questions; one H1; navigation ≤ 7 items; primary CTA above the fold and repeated at the end.
3. **Tokens first** — run `scripts/design_tokens.py` with the brand colour: light + dark themes, status colours, spacing, radius, type scale, motion. Every colour in CSS comes from a token; no one-off hex values.
4. **Layout** — mobile-first at 360px, then 768 / 1024 / 1280; CSS grid/flex; `max-width` on content (≈ 68ch for text); touch targets ≥ 44px; safe areas on phones.
5. **Components** — every interactive component has default, hover, focus-visible, active, disabled, loading, empty and error states. Semantic HTML first; ARIA only when HTML cannot express it.
6. **Build** — complete files (no `...`). Single-file pages inline CSS/JS; multi-page projects use the forge (`../kosif-think-pro/scripts/project_forge.py … static-web` or `cf-worker`) for a tested scaffold.
7. **Audit** — `scripts/web_audit.py PAGE_OR_DIR` (static: document, a11y, contrast in both themes, responsive, performance, design-token use, security). Fix every BLOCK and high item.
8. **Render check** — when a browser is available (Playwright/Chromium in the sandbox, or the host's browser tools), open the page at 360×800 and 1280×800 in light and dark, screenshot, check for horizontal scroll, overlapping text and focus visibility, and tab through the page. Report what was actually rendered; if no browser ran, say `not rendered`.
9. **Deliver** — files + audit score + screenshots (if taken) + next improvements. Publishing (artifact, Pages, Workers) only when asked; deployment needs the user's account.

## Commands
- `/site <brief>` — full pipeline, multi-section site.
- `/landing <product>` — conversion landing page: hero (value proposition + primary CTA), social proof, benefits, how it works, pricing/offer, FAQ, final CTA; A/B headline variants ×3.
- `/ui <screen>` — one screen/component with all states.
- `/dashboard <data>` — data-dense layout: KPI tiles, charts with legends + table fallback, filters; numbers with tabular figures; never invented data (empty states instead).
- `/tokens <brand hex>` — run `design_tokens.py`, show the contrast report and the CSS.
- `/webaudit <file|url|folder>` — `web_audit.py` + (if a browser is available) rendered checks; findings table: severity | issue | where | fix.
- `/redesign <page>` — audit → prioritised fixes → rebuilt page → before/after audit scores.
- `/component <name>` — accessible component (HTML/CSS/JS or React) with keyboard support and tests.

## Non-negotiables
WCAG 2.2 AA: text contrast ≥ 4.5:1 (3:1 for large text and UI parts) in **both** themes · visible `:focus-visible` · labels for every control · alt text · no zoom blocking · `prefers-reduced-motion` honoured · one H1 · landmarks · keyboard operable · RTL mirrors layout (use logical properties: `margin-inline-start`, `inset-inline-end`) · Arabic typography: IBM Plex Sans Arabic / Noto Kufi / Tajawal / Cairo with a matching Latin face, line-height ≥ 1.6 · numbers in tables with `font-variant-numeric: tabular-nums` · no secrets in front-end code · no fake statistics or testimonials.

References: `references/web-playbook.md` (layout recipes, section patterns, Arabic/RTL rules, performance budget, dashboard rules, KOSIF design-system lessons from the user's repositories).
