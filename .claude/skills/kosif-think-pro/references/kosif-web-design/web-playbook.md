# Web playbook

## Lessons carried over from the user's repositories
From `kosif199022-jpg/cloude` (SQC / KOSIF Luxe design system):
- **One token file is the only place colours, spacing, type and motion are defined** (`ui/ds/tokens.css`); legacy names are aliases of the tokens so every screen follows one system.
- **Three modes**: light (default), dark, auto (follows the device), set through `html[data-theme]`; several complete "looks" (`html[data-look]`) re-define the same tokens.
- **Categorical chart palette validated for colour-blind separation** (worst adjacent ΔE ≈ 9 light / 8.4 dark); slots below 3:1 on white ship with legends, tooltips and a table view.
- **Typeface chosen by Jev**: `jev_choice` picked IBM Plex Sans Arabic (p≈0.99) for clearer digits in dense tables with a matching Latin face — decisions like this are recorded with their probability.
- **Tabular Latin numerals** (`tnum`) in tables; time runs left→right in charts even in RTL layouts.
- **No invented numbers**: every figure comes from records; an empty source shows an empty state.
- **Automatic accessibility pass** (`ui/core/a11y.js`): unnamed inputs get names from column headers/row labels, images without alt get `alt=""`, icon buttons get names — a safety net, not a substitute for correct markup.
- `prefers-reduced-motion` sets the motion token to 0ms.

## Section patterns (landing page)
| Section | Must contain | Common mistake |
|---|---|---|
| Hero | outcome-focused headline (≤ 10 words), one-sentence sub-headline, one primary CTA, visual of the product in use | three CTAs of equal weight |
| Social proof | real logos/testimonials/numbers with sources | invented reviews |
| Benefits | 3–6 benefits phrased as user outcomes | feature lists |
| How it works | 3 numbered steps | walls of text |
| Offer / pricing | clear plan names, what is included, risk reversal | hidden fees |
| FAQ | top objections answered | marketing fluff |
| Final CTA | repeat primary action | new, different action |

## Layout recipes
- Page container: `max-width: 72rem; margin-inline: auto; padding-inline: 16px` (24px ≥ 768px).
- Auto-fit cards: `grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr))`.
- Holy-grail app shell: header / (nav | main) / footer with grid areas; nav collapses to a bottom bar ≤ 900px.
- Fluid type: `font-size: clamp(28px, 5vw, 44px)` for H1.
- Media: `img{max-width:100%;height:auto}` plus width/height attributes to reserve space.

## Arabic and RTL
- `<html lang="ar" dir="rtl">`; use logical CSS properties; mirror directional icons (arrows) but not logos, media controls or charts' time axes.
- Mixed text: wrap Latin/numbers in `<bdi>` or `unicode-bidi: isolate` when order breaks.
- Line height 1.6–1.8; avoid letter-spacing on Arabic; avoid all-caps logic (Arabic has no case).
- Dates: offer Hijri + Gregorian where the audience expects it.

## Performance budget (mobile, 4G)
LCP ≤ 2.5 s · CLS ≤ 0.1 · INP ≤ 200 ms · JS ≤ 170 KB gz on first load · images in AVIF/WebP with `srcset` · fonts subset + `font-display: swap` + preload for the primary face · `defer` scripts · no render-blocking third parties.

## Dashboards
- Start with the question each chart answers; one chart type per question.
- KPI tile = value + unit + delta vs comparison + period + source.
- Every chart: title, axis labels, legend (or direct labels), tooltip, accessible table fallback.
- Colour: categorical palette in fixed order (identity, never rank); sequential for magnitude; diverging only around a meaningful midpoint.

## SEO basics
Unique `<title>` (10–65 chars) · meta description (50–160) · one H1 · descriptive link text · `alt` text · canonical URL · Open Graph tags · sitemap.xml · structured data where relevant · fast mobile page.

## Security for front-end
No API keys in client code (use a Worker/server proxy with the secret in the platform store) · CSP without `unsafe-inline` when possible (so no inline handlers) · `rel="noopener"` on new-tab links · HTTPS for all resources · escape user content before inserting into the DOM (`textContent`, not `innerHTML`).
