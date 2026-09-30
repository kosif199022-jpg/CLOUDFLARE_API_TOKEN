#!/usr/bin/env python3
"""KOSIF Story Lint — GMC+S conflict engine checker for scripts, reels and ads (v3.1).

Grounded in The Conflict Thesaurus (vol. 2, readable copy): central conflict takes
one of six forms; conflict works on levels (central, story/macro, scene/micro,
inner); every beat needs Goal, Motivation, Conflict and Stakes (GMC+S); the
protagonist must drive events through choices (agency); keep ~80% action / 20%
introspection; stakes should be personal and escalate; relationship conflict must
not resolve too quickly; the climax resolves the outer clash through the inner one.

stdin JSON:
{"central_conflict": "character vs self",
 "protagonist": "Laila",
 "beats": [
   {"id": 1, "goal": "...", "motivation": "...", "conflict": "...", "stakes": "...",
    "stakes_level": 1, "choice": "Laila decides to ...", "mode": "action"|"introspection",
    "level": "scene"|"story"|"inner", "relationship_resolved": false, "type": "setup"}
   ...],
 "climax": {"outer": "...", "inner": "..."}}
"""
import json
import sys

PLOTS = {  # Christopher Booker's seven basic plots (via the Outcomes coursebook reading)
    "overcoming the monster": ["threat and call", "preparation / weapon or fatal flaw", "initial success",
                               "first confrontation and frustration", "nightmare stage", "escape, victory, reward"],
    "rags to riches": [], "the quest": [], "voyage and return": [], "comedy": [], "tragedy": [], "rebirth": []}
CENTRAL = {"character vs character", "character vs society", "character vs nature",
           "character vs technology", "character vs supernatural", "character vs self"}


def lint(o):
    issues, warns = [], []
    cc = str(o.get("central_conflict", "")).strip().lower()
    if cc not in CENTRAL:
        issues.append(f"central_conflict must be one of {sorted(CENTRAL)}")
    beats = o.get("beats") or []
    if len(beats) < 3:
        issues.append("need at least 3 beats (setup, escalation, climax/payoff)")
    hero = str(o.get("protagonist", "")).strip().lower()
    stakes, modes, levels = [], [], set()
    for i, b in enumerate(beats):
        bid = b.get("id", i + 1)
        for f in ("goal", "motivation", "conflict", "stakes"):
            if not str(b.get(f, "")).strip():
                issues.append(f"beat {bid}: missing {f} (GMC+S)")
        ch = str(b.get("choice", "")).strip()
        if not ch:
            issues.append(f"beat {bid}: no protagonist choice — events happen TO the hero (agency)")
        elif hero and hero not in ch.lower():
            warns.append(f"beat {bid}: choice does not name the protagonist; confirm they drive it")
        if isinstance(b.get("stakes_level"), (int, float)):
            stakes.append((bid, b["stakes_level"]))
        modes.append(b.get("mode", "action"))
        if b.get("level"):
            levels.add(b["level"])
        if b.get("relationship_resolved") and i < len(beats) * 0.6:
            warns.append(f"beat {bid}: relationship conflict resolved early — tension collapses")
    for (a, sa), (b2, sb) in zip(stakes, stakes[1:]):
        if sb < sa:
            warns.append(f"stakes drop from beat {a} ({sa}) to beat {b2} ({sb}); make sure it is a deliberate breather")
    if stakes and stakes[-1][1] < max(s for _, s in stakes):
        issues.append("final beat does not carry the highest stakes")
    if modes:
        intro = sum(1 for m in modes if m == "introspection") / len(modes)
        if intro > 0.3:
            warns.append(f"introspection is {intro:.0%} of beats (target ≈20%): give the character something to do")
    if "inner" not in levels and cc != "character vs self":
        warns.append("no inner-conflict beat: the outer climax will feel hollow")
    plot = str(o.get("plot", "")).strip().lower()
    if plot:
        if plot not in PLOTS:
            warns.append(f"plot '{plot}' is not one of Booker's seven: {sorted(PLOTS)}")
        elif PLOTS[plot]:
            stages = {str(b.get("stage", "")).strip().lower() for b in beats}
            missing = [st for st in PLOTS[plot] if st not in stages]
            if missing:
                warns.append(f"{plot}: stages not marked in beats: {missing}")
    cl = o.get("climax") or {}
    if not str(cl.get("outer", "")).strip() or not str(cl.get("inner", "")).strip():
        issues.append("climax must state both the outer clash and the inner shift that decides it")
    score = max(0, 100 - 12 * len(issues) - 4 * len(warns))
    return {"ok": not issues, "score": score, "issues": issues, "warnings": warns,
            "levels_present": sorted(levels), "beats": len(beats)}


def main():
    try:
        out = lint(json.load(sys.stdin))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
