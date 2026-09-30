#!/usr/bin/env python3
"""KOSIF Computer Use — ground a natural-language instruction to one observed UI element.

Deterministic ranking first; when the top candidates are too close, it emits a ready-to-send
Jev `jev_choice` packet over the closed set of observed candidates (Jev disambiguates, it never
approves risky actions — run action_gate.py after grounding).

stdin JSON:
{"instruction": "اضغط زر الدفع" | "click the Download March invoice link",
 "elements": [{"id": "a_1x", "role": "button", "tag": "button", "text": "Download", "name": null,
               "placeholder": null, "aria_label": null, "in_viewport": true, "disabled": false,
               "rect": {"x": 10, "y": 20, "w": 120, "h": 40}}],
 "history": ["a_1x", "a_1x"]}          # optional: element ids acted on recently (anti-loop)
Output: action (click/type/scroll), chosen element + centre point, ranked candidates, ambiguity, optional Jev packet.
Elements can come from an accessibility tree, a DOM index (e.g. the action-graph script) or OCR boxes.
"""
import json
import re
import sys

AR_DIAC = re.compile(r"[ً-ْـ]")
STOP = {"the", "a", "an", "on", "in", "into", "to", "of", "and", "button", "link", "field", "icon", "please", "click", "press",
        "tap", "type", "enter", "write", "select", "choose", "open", "اضغط", "انقر", "على", "زر", "رابط", "حقل", "في", "اكتب", "افتح", "اختر", "ال"}
TYPE_WORDS = r"\b(type|enter|write|fill|search for|input)\b|اكتب|ادخل|أدخل|ابحث عن|املأ"
SCROLL_WORDS = r"\b(scroll|swipe)\b|مرر|انزل|اسحب"


def norm(s):
    s = AR_DIAC.sub("", str(s or "").lower())
    s = re.sub("[إأآا]", "ا", s).replace("ى", "ي").replace("ة", "ه")
    return s


def tokens(s):
    toks = []
    for w in re.findall(r"[\w؀-ۿ]+", norm(s)):
        w = w[2:] if w.startswith("ال") and len(w) > 4 else w
        if w not in STOP and len(w) > 1:
            toks.append(w)
    return toks


def label(e):
    return " ".join(str(e.get(k) or "") for k in ("aria_label", "text", "name", "placeholder", "title", "value")).strip()


def ground(o):
    instr = str(o.get("instruction", "")).strip()
    els = o.get("elements")
    if not instr or not isinstance(els, list) or not els:
        raise ValueError("instruction and a non-empty elements list are required")
    want_type = bool(re.search(TYPE_WORDS, norm(instr)))
    if re.search(SCROLL_WORDS, norm(instr)):
        return {"action": "scroll", "reason": "instruction asks to scroll", "chosen": None, "candidates": []}
    quoted = re.findall(r"[\"“«']([^\"”»']+)[\"”»']", instr)
    q = set(tokens(instr))
    hist = o.get("history") or []
    scored = []
    for e in els:
        lab = label(e)
        lt = set(tokens(lab))
        role = str(e.get("role") or e.get("tag") or "").lower()
        score = 0.0
        if q and lt:
            overlap = len(q & lt)
            score += 50 * overlap / len(q) + 10 * overlap / len(lt)
            score += sum(8 for a in q for b in lt if a != b and (a in b or b in a) and min(len(a), len(b)) > 2)
        if quoted and any(norm(x) in norm(lab) for x in quoted):
            score += 40
        textual = role in {"input", "textbox", "textarea", "searchbox", "combobox"} or e.get("tag") in {"input", "textarea"}
        if want_type and textual:
            score += 25
        if not want_type and role in {"button", "link", "a", "menuitem", "tab", "checkbox", "radio", "option"}:
            score += 8
        if e.get("in_viewport"):
            score += 5
        if e.get("disabled"):
            score -= 60
        r = e.get("rect") or {}
        if r and (r.get("w", 0) < 4 or r.get("h", 0) < 4):
            score -= 30
        scored.append({"score": round(score, 2), "element": e, "label": lab})
    scored.sort(key=lambda x: -x["score"])
    top = scored[0]
    runner = scored[1] if len(scored) > 1 else None
    if top["score"] <= 5:
        return {"action": "scroll", "reason": "no element matches the instruction in the observed set; scroll or re-observe",
                "chosen": None, "candidates": [{"id": c["element"].get("id"), "score": c["score"], "label": c["label"]} for c in scored[:5]]}
    looped = len(hist) >= 2 and hist[-1] == hist[-2] == top["element"].get("id")
    if looped and runner and runner["score"] > 5:
        top, runner = runner, top
    ambiguous = bool(runner and runner["score"] > 5 and top["score"] - runner["score"] < max(6.0, 0.12 * top["score"]))
    e = top["element"]
    r = e.get("rect") or {}
    centre = {"x": round(r["x"] + r["w"] / 2), "y": round(r["y"] + r["h"] / 2)} if {"x", "y", "w", "h"} <= set(r) else None
    textual = str(e.get("role") or e.get("tag") or "").lower() in {"input", "textbox", "textarea", "searchbox", "combobox"}
    action = "type" if want_type and textual else "click"
    out = {"action": action, "chosen": {"id": e.get("id"), "label": top["label"], "role": e.get("role") or e.get("tag"), "centre": centre},
           "score": top["score"], "ambiguous": ambiguous, "loop_avoided": looped,
           "candidates": [{"id": c["element"].get("id"), "score": c["score"], "label": c["label"]} for c in scored[:5]],
           "next": "run action_gate.py on the chosen step, act once, then verify the expected change"}
    if action == "type":
        m = re.search(r"(?:type|enter|write|search for|اكتب|ادخل|أدخل|ابحث عن)\s+[\"“«']?([^\"”»']+)", instr, re.I)
        out["text"] = (quoted[0] if quoted else (m.group(1).strip() if m else ""))
    underspecified = False
    if ambiguous and runner:
        distinguishing = set(tokens(top["label"])) ^ set(tokens(runner["label"]))
        underspecified = bool(distinguishing) and not (distinguishing & q)
    out["underspecified"] = underspecified
    if underspecified:
        out["next"] = ("ask the user which one: the words that tell the candidates apart "
                       f"({sorted(set(tokens(top['label'])) ^ set(tokens(runner['label'])))}) are not in the instruction; "
                       "do not let Jev guess missing intent")
    elif ambiguous:
        closed = [c for c in scored[:5] if c["score"] >= max(5.0, 0.5 * top["score"])]
        out["jev_packet"] = {
            "tool": "jev_choice",
            "instructions": f"Which on-screen element should be used to do this: {instr}? Choose the element whose label and role best match the intent.",
            "criteria": {c["element"].get("id"): f"{c['element'].get('role') or c['element'].get('tag')}: {c['label'][:80]}" for c in closed},
            "state": {"instruction": instr, "candidates": [{"id": c["element"].get("id"), "role": c["element"].get("role") or c["element"].get("tag"),
                                                            "label": c["label"][:120], "in_viewport": bool(c["element"].get("in_viewport"))} for c in closed]},
            "rule": "use Jev's choice only if confidence ≥ 0.7; otherwise ask the user or observe more; re-run action_gate.py on the result",
        }
    return out


def main():
    try:
        res = ground(json.load(sys.stdin))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
