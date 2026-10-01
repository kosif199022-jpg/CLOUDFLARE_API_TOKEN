#!/usr/bin/env python3
"""KOSIF Web Design — static audit of an HTML page (and its local CSS/JS).

Usage:  web_audit.py PAGE.html | SITE_DIR        (a directory audits every *.html in it)
        echo '{"html": "...", "css": "..."}' | web_audit.py -
Checks (deterministic; a browser run with Playwright is still needed for layout, focus order and real rendering):
  document    doctype, <html lang>, dir=rtl for Arabic, charset, viewport (and no zoom blocking), title,
              meta description, single h1, heading-level skips, landmarks, skip link
  a11y        img alt, form-control labels, button/link accessible names, positive tabindex, iframe title,
              autoplay, outline removal without :focus-visible, WCAG contrast of color/background pairs
              (hex, rgb() and var() resolved from :root and dark-theme tokens), tiny font sizes
  responsive  fixed widths > 480px without max-width, viewport meta, image intrinsic size (CLS)
  performance render-blocking scripts in <head>, heavy inline styles, font-display
  design      token usage vs hard-coded colours, dark-mode support, reduced-motion support
  security    inline event handlers, http:// resources, target=_blank without rel, secrets in page/scripts
Verdict PASS / REVISE / BLOCK. BLOCK = zoom disabled, missing viewport or lang, text contrast failure, secret.
Exit 0 PASS · 1 REVISE · 3 BLOCK · 2 invalid.
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

SECRET = re.compile(r"\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}|\bgh[pousr]_[A-Za-z0-9]{36,}|\bAKIA[0-9A-Z]{16}\b|-----BEGIN [A-Z ]*PRIVATE KEY-----|\bxox[baprs]-[A-Za-z0-9-]{10,}")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.doctype = False
        self.els = []            # (tag, attrs, index)
        self.stack = []
        self.text_of = {}        # index -> collected text
        self.labels_for = set()
        self.in_label = 0
        self.labelled_in_label = set()
        self.head_open = False
        self.head_scripts = []
        self.styles = []
        self._in_style = False
        self.inline_scripts = []
        self._in_script = False

    def handle_decl(self, decl):
        if decl.lower().startswith("doctype"):
            self.doctype = True

    def handle_starttag(self, tag, attrs):
        a = {k: (v if v is not None else "") for k, v in attrs}
        idx = len(self.els)
        self.els.append((tag, a, idx))
        if tag == "head":
            self.head_open = True
        if tag == "script" and self.head_open:
            self.head_scripts.append(a)
        if tag == "label":
            self.in_label += 1
            if a.get("for"):
                self.labels_for.add(a["for"])
        if tag in {"input", "select", "textarea"} and self.in_label:
            self.labelled_in_label.add(idx)
        if tag == "style":
            self._in_style = True
        if tag == "script" and "src" not in a:
            self._in_script = True
        if tag not in VOID:
            self.stack.append(idx)
            self.text_of[idx] = ""

    def handle_endtag(self, tag):
        if tag == "head":
            self.head_open = False
        if tag == "label" and self.in_label:
            self.in_label -= 1
        if tag == "style":
            self._in_style = False
        if tag == "script":
            self._in_script = False
        while self.stack:
            idx = self.stack.pop()
            if self.els[idx][0] == tag:
                break

    def handle_data(self, data):
        if self._in_style:
            self.styles.append(data)
            return
        if self._in_script:
            self.inline_scripts.append(data)
            return
        for idx in self.stack:
            self.text_of[idx] = self.text_of.get(idx, "") + data


# ---- colour ----------------------------------------------------------------
def rgb(c):
    c = c.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})", c)
    if m:
        h = m.group(1)
        h = "".join(x * 2 for x in h) if len(h) == 3 else h
        return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    m = re.fullmatch(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)", c)
    if m and (m.group(4) is None or float(m.group(4)) >= 0.999):
        return tuple(int(x) / 255 for x in m.groups()[:3])
    named = {"white": (1, 1, 1), "black": (0, 0, 0)}
    return named.get(c)


def lum(c):
    f = lambda v: v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4  # noqa: E731
    r, g, b = (f(v) for v in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def blocks(css):
    """Flatten CSS into (selector-with-at-rule-context, declarations) leaf blocks."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out, stack, pos = [], [], 0
    for m in re.finditer(r"[{}]", css):
        if m.group() == "{":
            stack.append((css[pos:m.start()].strip(), m.end()))
        elif stack:
            prelude, start = stack.pop()
            inner = css[start:m.start()]
            if "{" not in inner:
                outer = " ".join(p for p, _ in stack)
                out.append(((outer + " " + prelude).strip(), inner))
        pos = m.end()
    return out


def decls(body):
    d = {}
    for part in body.split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            d[k.strip().lower()] = v.strip()
    return d


def resolve(val, vars_):
    for _ in range(5):
        m = re.search(r"var\(\s*--([\w-]+)\s*(?:,\s*([^)]+))?\)", val or "")
        if not m:
            break
        val = vars_.get(m.group(1), m.group(2) or "")
    v = (val or "").replace("!important", "").strip()
    m = re.search(r"#[0-9a-fA-F]{3,6}\b|rgba?\([^)]*\)|\b(white|black)\b", v)
    return rgb(m.group(0)) if m else None


def audit(html, css="", scripts=""):
    p = Page()
    p.feed(html)
    css_all = css + "\n" + "\n".join(p.styles)
    js_all = scripts + "\n" + "\n".join(p.inline_scripts)
    issues = []   # (severity, category, message)

    def add(sev, cat, msg):
        issues.append({"severity": sev, "category": cat, "message": msg})

    tags = [t for t, _, _ in p.els]
    attrs_of = lambda tag: [a for t, a, _ in p.els if t == tag]  # noqa: E731
    html_a = (attrs_of("html") or [{}])[0]
    if not p.doctype:
        add("medium", "document", "missing <!doctype html> (quirks mode)")
    lang = html_a.get("lang", "")
    if not lang:
        add("blocker", "a11y", "<html> has no lang attribute")
    body_text = " ".join(p.text_of.values())
    arabic = lang.startswith("ar") or len(re.findall(r"[؀-ۿ]", body_text)) > 20
    if arabic and html_a.get("dir", "").lower() != "rtl" and not any(a.get("dir") == "rtl" for _, a, _ in p.els):
        add("high", "a11y", "Arabic content without dir=\"rtl\"")
    metas = attrs_of("meta")
    if not any("charset" in m or m.get("http-equiv", "").lower() == "content-type" for m in metas):
        add("medium", "document", "no <meta charset>")
    vp = next((m.get("content", "") for m in metas if m.get("name", "").lower() == "viewport"), None)
    if vp is None:
        add("blocker", "responsive", "no viewport meta: the page will render as desktop on phones")
    elif re.search(r"user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*1(\.0)?\b", vp):
        add("blocker", "a11y", "viewport blocks zoom (user-scalable=no / maximum-scale=1)")
    title = next((p.text_of.get(i, "").strip() for t, _, i in p.els if t == "title"), "")
    if not title:
        add("high", "seo", "missing <title>")
    elif not 10 <= len(title) <= 65:
        add("low", "seo", f"title length {len(title)} (aim 10–65 chars)")
    desc = next((m.get("content", "") for m in metas if m.get("name", "").lower() == "description"), "")
    if not desc:
        add("medium", "seo", "missing meta description")
    h1 = tags.count("h1")
    if h1 != 1:
        add("medium", "a11y", f"{h1} <h1> elements (use exactly one)")
    levels = [int(t[1]) for t in tags if re.fullmatch(r"h[1-6]", t)]
    for a, b in zip(levels, levels[1:]):
        if b > a + 1:
            add("low", "a11y", f"heading level skips from h{a} to h{b}")
            break
    if "main" not in tags and not any(a.get("role") == "main" for _, a, _ in p.els):
        add("medium", "a11y", "no <main> landmark")
    if not any(t == "a" and a.get("href", "").startswith("#") and re.search(r"skip|تخط|المحتوى", p.text_of.get(i, ""), re.I) for t, a, i in p.els):
        add("low", "a11y", "no skip-to-content link")

    ids = {a.get("id") for _, a, _ in p.els if a.get("id")}
    for t, a, i in p.els:
        text = re.sub(r"\s+", " ", p.text_of.get(i, "")).strip()
        named = a.get("aria-label") or a.get("aria-labelledby") or a.get("title")
        if t == "img" and "alt" not in a:
            add("high", "a11y", f"<img src={a.get('src', '?')!r}> has no alt (use alt=\"\" for decoration)")
        if t == "img" and not (a.get("width") and a.get("height")) and "aspect-ratio" not in a.get("style", ""):
            add("low", "performance", f"<img src={a.get('src', '?')!r}> without width/height (layout shift)")
        if t in {"input", "select", "textarea"} and a.get("type", "") not in {"hidden", "submit", "button", "reset", "image"}:
            if not (named or (a.get("id") in p.labels_for) or i in p.labelled_in_label):
                add("high", "a11y", f"<{t} name={a.get('name', '?')!r}> has no label")
            if a.get("type") in {"email", "tel", "password"} and not a.get("autocomplete"):
                add("low", "a11y", f"<input type={a['type']}> without autocomplete")
        if t == "button" and not (text or named):
            add("high", "a11y", "<button> without an accessible name")
        if t == "a":
            if not (text or named or any(tt == "img" and aa.get("alt") for tt, aa, ii in p.els[i + 1:i + 3])):
                add("high", "a11y", f"link {a.get('href', '?')!r} has no text")
            if a.get("href") in {"#", "javascript:void(0)", "javascript:;"}:
                add("medium", "a11y", "link used as a button (href=\"#\"): use <button>")
            if a.get("target") == "_blank" and "noopener" not in a.get("rel", ""):
                add("low", "security", f"target=_blank without rel=\"noopener\" on {a.get('href', '?')!r}")
        if a.get("tabindex", "").lstrip("-").isdigit() and int(a["tabindex"]) > 0:
            add("medium", "a11y", "positive tabindex breaks focus order")
        if t == "iframe" and not a.get("title"):
            add("medium", "a11y", "<iframe> without title")
        if t in {"video", "audio"} and "autoplay" in a and "muted" not in a:
            add("medium", "a11y", f"<{t}> autoplays with sound")
        if any(k.startswith("on") for k in a):
            add("low", "security", f"inline event handler on <{t}> (use addEventListener; blocks strict CSP)")
        for k in ("src", "href"):
            if a.get(k, "").startswith("http://"):
                add("medium", "security", f"insecure http:// resource {a[k]!r}")
        if a.get("aria-labelledby") and not all(x in ids for x in a["aria-labelledby"].split()):
            add("medium", "a11y", "aria-labelledby points to a missing id")
    for s in p.head_scripts:
        if s.get("src") and "defer" not in s and "async" not in s and s.get("type") != "module":
            add("medium", "performance", f"render-blocking script in <head>: {s['src']!r} (add defer)")
    inline_styles = sum(1 for _, a, _ in p.els if a.get("style"))
    if inline_styles > 10:
        add("low", "design", f"{inline_styles} inline style attributes: move to classes/tokens")

    # ---- CSS -------------------------------------------------------------------------
    bl = blocks(css_all)
    root_vars, dark_vars = {}, {}
    for sel, body in bl:
        d = {k[2:]: v for k, v in decls(body).items() if k.startswith("--")}
        if re.search(r'data-theme\s*=\s*"?dark|\.dark\b|prefers-color-scheme\s*:\s*dark', sel):
            dark_vars.update(d)
        elif sel.strip().startswith(":root") or sel.strip() == "html":
            root_vars.update(d)
    has_dark = bool(dark_vars) or "prefers-color-scheme" in css_all
    if css_all.strip() and not has_dark:
        add("low", "design", "no dark theme (prefers-color-scheme or [data-theme=dark])")
    if re.search(r"(animation|transition)\s*:", css_all) and "prefers-reduced-motion" not in css_all:
        add("medium", "a11y", "animations without a prefers-reduced-motion rule")
    if re.search(r"outline\s*:\s*(none|0)\b", css_all) and ":focus-visible" not in css_all:
        add("high", "a11y", "outline removed without a :focus-visible replacement")
    if "@font-face" in css_all and "font-display" not in css_all:
        add("low", "performance", "@font-face without font-display (invisible text while loading)")
    hard = 0
    contrast = []
    body_bg = next((decls(b2).get("background-color") or decls(b2).get("background") for s2, b2 in bl
                    if re.search(r"(^|,)\s*(body|html)\s*(,|$)", s2)), None)
    for sel, body in bl:
        d = decls(body)
        is_token_block = sel.strip().startswith(":root") or "data-theme" in sel
        if not is_token_block:
            hard += sum(1 for k, v in d.items() if not k.startswith("--") and re.search(r"#[0-9a-fA-F]{3,6}\b|rgba?\(", v))
        for theme, vars_ in (("light", root_vars), ("dark", {**root_vars, **dark_vars})):
            if theme == "dark" and not dark_vars:
                continue
            fg = resolve(d.get("color"), vars_)
            bg = resolve(d.get("background-color") or d.get("background"), vars_) or resolve(body_bg, vars_)
            if fg and bg:
                r = ratio(fg, bg)
                size = d.get("font-size", "")
                large = bool(re.match(r"(2[4-9]|[3-9]\d)px|([1-9]\.\d+|[2-9])r?em", size)) or (
                    d.get("font-weight", "") in {"700", "bold"} and bool(re.match(r"(1[89]|2\d)px", size)))
                need = 3.0 if large else 4.5
                contrast.append({"selector": sel[:60], "theme": theme, "ratio": round(r, 2), "needed": need, "pass": r >= need})
                if r < need:
                    add("blocker", "a11y", f"contrast {r:.2f}:1 < {need}:1 in {theme} theme for `{sel[:50]}`")
        fs = d.get("font-size", "")
        m = re.match(r"(\d+(?:\.\d+)?)px", fs)
        if m and float(m.group(1)) < 12:
            add("medium", "a11y", f"font-size {fs} in `{sel[:40]}` is too small")
        w = re.match(r"(\d+)px", d.get("width", ""))
        if w and int(w.group(1)) > 480 and "max-width" not in d and "@media" not in sel:
            add("medium", "responsive", f"fixed width {d['width']} in `{sel[:40]}` may cause horizontal scroll on phones")
    if hard > 8:
        add("low", "design", f"{hard} hard-coded colours outside token blocks: use CSS custom properties")
    if SECRET.search(html) or SECRET.search(js_all) or SECRET.search(css_all):
        add("blocker", "security", "credential/secret found in the page or its scripts")

    weights = {"blocker": 25, "high": 10, "medium": 4, "low": 1}
    score = max(0, 100 - sum(weights[i["severity"]] for i in issues))
    verdict = "BLOCK" if any(i["severity"] == "blocker" for i in issues) else "REVISE" if any(i["severity"] in {"high", "medium"} for i in issues) else "PASS"
    by_cat = {}
    for i in issues:
        by_cat[i["category"]] = by_cat.get(i["category"], 0) + 1
    return {"verdict": verdict, "score": score, "issues": issues, "by_category": by_cat, "contrast_pairs": contrast,
            "tokens": {"light": len(root_vars), "dark": len(dark_vars)}, "elements": len(p.els),
            "note": "static audit; confirm layout, focus order and rendering in a real browser (Playwright) at 360px and 1280px"}


def audit_path(path):
    path = Path(path)
    pages = sorted(path.rglob("*.html")) if path.is_dir() else [path]
    results = {}
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        css = scripts = ""
        for href in re.findall(r"<link[^>]+href=[\"']([^\"']+\.css)[\"']", html, re.I):
            f = (page.parent / href).resolve()
            if f.exists() and not href.startswith(("http:", "https:", "//")):
                css += f.read_text(encoding="utf-8", errors="replace") + "\n"
        for src in re.findall(r"<script[^>]+src=[\"']([^\"']+)[\"']", html, re.I):
            f = (page.parent / src).resolve()
            if f.exists() and not src.startswith(("http:", "https:", "//")):
                scripts += f.read_text(encoding="utf-8", errors="replace") + "\n"
        results[str(page)] = audit(html, css, scripts)
    return results


def main(argv):
    try:
        if len(argv) < 2:
            raise ValueError("usage: web_audit.py PAGE.html|DIR|-")
        if argv[1] == "-":
            o = json.load(sys.stdin)
            out = audit(o.get("html", ""), o.get("css", ""), o.get("js", ""))
            verdicts = [out["verdict"]]
        else:
            out = audit_path(argv[1])
            if not out:
                raise ValueError("no .html files found")
            verdicts = [r["verdict"] for r in out.values()]
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"verdict": "INVALID", "error": str(e)}))
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 3 if "BLOCK" in verdicts else 1 if "REVISE" in verdicts else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
