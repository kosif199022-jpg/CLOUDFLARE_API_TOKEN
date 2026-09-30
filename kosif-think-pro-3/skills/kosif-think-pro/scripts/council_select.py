#!/usr/bin/env python3
"""KOSIF Council-100 selector (v3.3).

Picks which of the 100 council personas (references/council-100.json) should speak
for a task. Deterministic: keyword triggers (English + Arabic) + domain boosts +
guard rules. It does not run any persona; it tells the model which lenses to apply.

stdin JSON:
{"task": "...", "mode": "standard"|"pro"|"full", "domains": ["web", "github", ...],   # domains optional
 "max": 12}                                                                            # optional cap (standard/pro)

Modes
- standard: 3–12 personas whose triggers fire, plus Skeptic and Evidence Accountant as guards.
- pro:      the 14 core profiles (receipt-required) + up to `max` (default 16) triggered specialists,
            at least one per triggered chamber, plus every veto-holder whose trigger fires.
- full:     all 100, ordered by chamber (use for /council100; answer compactly, one line each).

Output: selected personas with reason, chamber coverage, veto holders in play and the
independence note (one model voicing many personas is one independent source).
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _find_data():
    for p in (HERE.parent / "references" / "council-100.json",
              HERE.parents[1] / "kosif-think-pro" / "references" / "council-100.json"):
        if p.exists():
            return p
    hits = sorted(HERE.parents[2].rglob("council-100.json")) if len(HERE.parents) > 2 else []
    if hits:
        return hits[0]
    raise FileNotFoundError("council-100.json")


DOMAIN_CHAMBERS = {
    "web": ["design", "engineering"], "design": ["design"], "prompt": ["media", "creativity"],
    "image": ["media"], "video": ["media", "creativity"], "audio": ["media"], "story": ["creativity", "media"],
    "code": ["engineering"], "github": ["operations", "engineering"], "computer": ["operations", "risk"],
    "jev": ["operations", "evidence"], "finance": ["business"], "audit": ["business", "evidence"],
    "decision": ["strategy", "evidence"], "research": ["evidence"], "people": ["human"], "security": ["risk"],
}
GUARDS_STANDARD = ["skeptic", "evidence-accountant"]


def load():
    return json.loads(_find_data().read_text(encoding="utf-8"))


def _hits(persona, text):
    out = []
    for t in persona["triggers"]:
        t_low = t.lower()
        if re.search(r"[؀-ۿ]", t_low):
            if t_low in text:
                out.append(t)
        elif re.search(r"(?<![a-z0-9])" + re.escape(t_low) + r"(?![a-z0-9])", text):
            out.append(t)
    return out


def select(req, data=None):
    data = data or load()
    people = data["personas"]
    task = str(req.get("task", "")).strip()
    if not task:
        raise ValueError("task is empty")
    mode = req.get("mode", "standard")
    if mode not in {"standard", "pro", "full"}:
        raise ValueError("mode must be standard, pro or full")
    text = task.lower()
    boosted = {c for d in req.get("domains", []) or [] for c in DOMAIN_CHAMBERS.get(d, [])}

    scored = []
    for p in people:
        hits = _hits(p, text)
        score = 3 * len(hits) + (2 if p["chamber"] in boosted and hits else 0) + (1 if p["chamber"] in boosted else 0)
        scored.append((score, hits, p))
    scored.sort(key=lambda x: (-x[0], x[2]["id"]))

    chosen, reasons = [], {}

    def add(p, why):
        if p["id"] not in reasons:
            chosen.append(p)
            reasons[p["id"]] = why

    by_id = {p["id"]: p for p in people}
    if mode == "full":
        for p in people:
            add(p, "full council")
    else:
        cap = int(req.get("max", 12 if mode == "standard" else 16))
        if mode == "pro":
            for p in people:
                if p["core"]:
                    add(p, "core profile (receipt-required in Pro)")
        else:
            for g in GUARDS_STANDARD:
                add(by_id[g], "standing guard")
        triggered = [(s, h, p) for s, h, p in scored if h]
        # one per triggered chamber first (diversity), then by score
        seen_ch = set()
        extra = 0
        for s, h, p in triggered:
            if p["chamber"] not in seen_ch and p["id"] not in reasons and extra < cap:
                add(p, "triggered: " + ", ".join(h))
                seen_ch.add(p["chamber"])
                extra += 1
        for s, h, p in triggered:
            if extra >= cap:
                break
            if p["id"] not in reasons:
                add(p, "triggered: " + ", ".join(h))
                extra += 1
        # a requested domain whose chamber nobody triggered gets its lead persona
        for ch in sorted(boosted):
            if not any(p["chamber"] == ch for p in chosen):
                lead = next(p for p in people if p["chamber"] == ch)
                add(lead, "domain lead: " + ch)
        # veto holders whose trigger fired always speak, even past the cap
        for s, h, p in scored:
            if h and p.get("veto") and p["id"] not in reasons:
                add(p, f"veto holder ({p['veto']}) triggered: " + ", ".join(h))
        # chamber companions: UI work always gets an accessibility voice
        if any(p["chamber"] == "design" for p in chosen):
            add(by_id["accessibility-advocate"], "companion: design work needs an accessibility check")
        # temperament balance: an optimiser/operator needs a risk voice and vice versa
        ids = set(reasons)
        if ids & {"decisive-operator", "ambitious-optimizer"} and not ids & {"conservative-risk-guardian", "pre-mortem-pessimist"}:
            add(by_id["pre-mortem-pessimist"], "balance: risk voice against optimiser/operator")
        if ids & {"conservative-risk-guardian"} and not ids & {"decisive-operator", "ambitious-optimizer"}:
            add(by_id["decisive-operator"], "balance: action voice against risk guardian")
        if mode == "standard" and len(chosen) < 3:
            add(by_id["adversarial-critic"], "minimum council of three")

    chambers = {}
    for p in chosen:
        chambers.setdefault(p["chamber"], 0)
        chambers[p["chamber"]] += 1
    return {
        "mode": mode, "count": len(chosen),
        "personas": [{"id": p["id"], "name": p["name"], "name_ar": p["name_ar"], "chamber": p["chamber"],
                      "core": p["core"], "veto": p.get("veto"), "if_then": p["if_then"], "question": p["question"],
                      "reason": reasons[p["id"]]} for p in chosen],
        "chambers": chambers,
        "veto_holders": [p["id"] for p in chosen if p.get("veto")],
        "independence_note": "All personas voiced by one model count as ONE independent source; "
                             "independence needs a different model, tool measurement or primary source.",
        "protocol": "freeze each persona's first-pass artifact before cross-critique; aggregate with council_aggregate.py",
    }


def main():
    try:
        out = select(json.load(sys.stdin))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
