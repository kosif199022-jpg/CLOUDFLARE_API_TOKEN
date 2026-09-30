#!/usr/bin/env python3
"""KOSIF decision optimizer with feasibility, dominance and sensitivity (v3.1).

Grounded in Convex Optimization ch.1 (objective + firm constraints + feasible set:
the best choice among those that meet firm requirements) and the reasoning
protocol steps "feasibility before preference" and "sensitivity/reversal".

stdin JSON:
{
 "criteria": {"cost": {"direction": "min", "weight": 0.4},
              "quality": {"direction": "max", "weight": 0.4},
              "speed": {"direction": "max", "weight": 0.2}},
 "constraints": {"cost": {"max": 5000}, "quality": {"min": 6}},       # firm requirements
 "options": [{"id": "A", "scores": {"cost": 4000, "quality": 7, "speed": 5}}, ...]
}
Missing scores make an option "pending" (never silently pass). Scores are min-max
normalised across feasible options so units do not dominate. Output: feasible /
rejected / pending sets, Pareto-dominated options, weighted ranking, winner margin,
and for every criterion weight the smallest change that flips the winner.
A weighted sum is a modelling choice, not proof of a global optimum.
"""
import json
import sys


def norm_scores(opts, criteria):
    out = {o["id"]: {} for o in opts}
    for c, spec in criteria.items():
        vals = [o["scores"][c] for o in opts]
        lo, hi = min(vals), max(vals)
        for o in opts:
            v = o["scores"][c]
            x = 0.5 if hi == lo else (v - lo) / (hi - lo)
            out[o["id"]][c] = 1 - x if spec.get("direction", "max") == "min" else x
    return out


def rank(ns, weights):
    tot = sum(weights.values()) or 1
    sc = {oid: sum(ns[oid][c] * w for c, w in weights.items()) / tot for oid in ns}
    return sorted(sc.items(), key=lambda kv: (-kv[1], kv[0]))


def dominated(opts, criteria):
    def better_eq(a, b, c):
        d = criteria[c].get("direction", "max")
        return a <= b if d == "min" else a >= b

    def strictly(a, b, c):
        d = criteria[c].get("direction", "max")
        return a < b if d == "min" else a > b
    dom = {}
    for a in opts:
        for b in opts:
            if a is b:
                continue
            if all(better_eq(b["scores"][c], a["scores"][c], c) for c in criteria) and \
               any(strictly(b["scores"][c], a["scores"][c], c) for c in criteria):
                dom[a["id"]] = b["id"]
                break
    return dom


def analyse(o):
    criteria = o["criteria"]
    if not criteria:
        raise ValueError("criteria required")
    cons = o.get("constraints", {})
    feasible, rejected, pending = [], [], []
    ids = set()
    for opt in o["options"]:
        if opt["id"] in ids:
            raise ValueError(f"duplicate option id {opt['id']}")
        ids.add(opt["id"])
        miss = [c for c in criteria if not isinstance(opt.get("scores", {}).get(c), (int, float))]
        fails = []
        for c, b in cons.items():
            v = opt.get("scores", {}).get(c)
            if not isinstance(v, (int, float)):
                if c not in miss:
                    miss.append(c)
                continue
            if ("min" in b and v < b["min"]) or ("max" in b and v > b["max"]):
                fails.append(c)
        if fails:
            rejected.append({"id": opt["id"], "failed": fails})
        elif miss:
            pending.append({"id": opt["id"], "missing": miss})
        else:
            feasible.append(opt)
    res = {"feasible": [f["id"] for f in feasible], "rejected": rejected, "pending": pending}
    if not feasible:
        res.update(winner=None, note="no feasible option: relax a constraint or gather missing data")
        return res
    dom = dominated(feasible, criteria)
    res["dominated"] = dom
    weights = {c: float(s.get("weight", 1)) for c, s in criteria.items()}
    ns = norm_scores(feasible, criteria)
    ranking = rank(ns, weights)
    res["ranking"] = [{"id": i, "score": round(s, 4)} for i, s in ranking]
    winner = ranking[0][0]
    res["winner"] = winner
    res["margin"] = round(ranking[0][1] - ranking[1][1], 4) if len(ranking) > 1 else None
    # weight sensitivity: vary one weight (others fixed) from 0 to 3x the total; report the nearest flip
    sens = {}
    total = sum(weights.values())
    for c in weights:
        cur, flip, best = weights[c], None, None
        for i in range(0, 601):
            w2 = dict(weights)
            w2[c] = total * i / 200
            top = rank(ns, w2)[0][0]
            if top != winner and (best is None or abs(w2[c] - cur) < best):
                best, flip = abs(w2[c] - cur), (w2[c], top)
        if flip:
            rel = best / cur if cur else float("inf")
            sens[c] = {"current_weight": round(cur, 4), "flips_at_weight": round(flip[0], 4),
                       "new_winner": flip[1], "relative_change_needed": round(rel, 3), "robust": rel >= 0.5}
        else:
            sens[c] = {"current_weight": round(cur, 4), "flips_at_weight": None, "robust": True}
    res["weight_sensitivity"] = sens
    res["fragile"] = [c for c, s in sens.items() if not s["robust"]]
    res["scope"] = "weighted-sum model over submitted options; not a proof of global optimality"
    return res


def main():
    try:
        out = analyse(json.load(sys.stdin))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))
    return 0 if out.get("winner") else 1


if __name__ == "__main__":
    raise SystemExit(main())
