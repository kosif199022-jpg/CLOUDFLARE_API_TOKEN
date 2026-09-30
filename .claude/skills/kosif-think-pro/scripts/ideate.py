#!/usr/bin/env python3
"""KOSIF Ideate — real randomness for lateral idea generation (v3.1).

Language models are poor random generators: asked for a "random word" they return
predictable ones. This helper supplies genuine, reproducible random stimuli so the
Random External Stimulus Technique (REST) actually escapes the obvious path.

Source basis (see references/books/lateral-thinking-course.md and smart-thinking.md):
- two stages of thinking: generate (movement, no judgement) then process (logic);
- random/chance input on demand; Aristotle's association laws: contiguity,
  similarity, contrast; challenge established concepts; ask naive "why" questions;
- define, simplify, detach from the problem before generating.

stdin JSON: {"problem": "...", "concepts": ["delivery fee", "store"], "n": 5, "seed": 42}
Output: problem-definition checklist, n random stimuli each with three association
prompts, challenge prompts per concept, provocation operators, and a stage-2 filter.
Ideas are hypotheses/options only — never evidence.
"""
import json
import random
import sys
import time

WORDS = """anchor bridge candle mirror compass ladder lantern magnet kite needle orchard harbor
glacier volcano desert oasis river delta canyon reef tide storm rainbow shadow echo
spiral knot zipper hinge valve filter sieve funnel pulley lever spring gear clock
hourglass calendar map key lock vault passport ticket receipt stamp envelope parcel
bicycle elevator escalator subway tunnel runway parachute balloon rocket satellite
telescope microscope prism lens camera film radio antenna battery fuse switch socket
bee ant spider octopus chameleon owl camel falcon salmon wolf elephant tortoise seed
root bark leaf thorn pollen mushroom cactus bamboo vine honey salt yeast bread coffee
tea spice recipe kitchen oven fridge freezer market auction lottery dice chess puzzle
theater mask costume stage orchestra drum whistle choir dance tattoo mural museum
library archive diary poem riddle joke rumor gossip debate court jury referee whistle
hospital vaccine bandage pulse mirror fingerprint barcode password queue waiting-room
school exam diploma apprentice mentor coach team relay marathon trophy medal podium
wedding funeral birthday festival lantern-festival pilgrimage caravan tent nomad
fishing-net harvest well irrigation windmill dam lighthouse pier ferry shipwreck
treasure pirate spy detective disguise alibi fingerprint trap bait decoy camouflage
recycling landfill compost fossil amber crystal diamond rust paint glue tape origami
thermostat vending-machine chatbot robot drone printer scanner hologram subtitles
playlist podcast trailer sequel remix sample cover-version karaoke applause silence
""".split()
WORDS = list(dict.fromkeys(WORDS))  # de-duplicate while keeping order

LAWS = {
    "contiguity": "What is usually next to, before, or after '{w}'? Borrow that neighbour into the problem.",
    "similarity": "What in the problem already works like '{w}'? Push the resemblance further.",
    "contrast": "What is the opposite of '{w}'? Apply that opposite to the problem.",
}
PROVOCATIONS = [
    ("reverse", "Reverse the usual direction: who pays/acts/waits becomes the other side."),
    ("remove", "Remove the element everyone assumes is essential. What still works?"),
    ("exaggerate", "Multiply one parameter by 100 or divide it by 100."),
    ("combine", "Merge two unrelated parts of the problem into one thing."),
    ("time-shift", "Solve it as someone 100 years ago / 100 years ahead would."),
    ("wishful", "Describe the impossible ideal outcome, then walk back to the nearest feasible step."),
]


def run(o):
    seed = o.get("seed")
    seed = int(seed) if seed is not None else int(time.time() * 1000) % 2_147_483_647
    rng = random.Random(seed)
    n = max(1, min(int(o.get("n", 5)), 20))
    words = rng.sample(WORDS, n)
    problem = str(o.get("problem", "")).strip()
    concepts = [str(c) for c in o.get("concepts", [])][:10]
    return {
        "seed": seed,
        "stage": "1-generate (no judgement yet)",
        "problem_definition": [
            f"State the problem in one sentence: {problem or '<missing: define it first>'}",
            "Simplify: list the 3-5 basic components.",
            "Name the obvious solution explicitly — it may be the best one.",
            "Detach: restate it as an outsider with no stake would.",
            "Ask 'why?' five times about the goal to find the real problem behind the stated one.",
        ],
        "random_stimuli": [{"word": w, "prompts": {k: v.format(w=w) for k, v in LAWS.items()}} for w in words],
        "challenge_concepts": [{"concept": c, "prompts": [
            f"Why does '{c}' exist at all? What need does it serve?",
            f"What if '{c}' were removed completely?",
            f"Who decided '{c}' must be done this way, and is that reason still true?",
            f"What would a naive newcomer ask about '{c}'?"]} for c in concepts],
        "provocations": [{"op": k, "prompt": v} for k, v in PROVOCATIONS],
        "stage_2_filter": [
            "Now switch to logic: keep ideas that serve the frozen goal and hard constraints.",
            "For each surviving idea: smallest reversible test, cost, and what evidence would kill it.",
            "Ideas generated here are options/hypotheses, never evidence.",
        ],
    }


def main():
    try:
        raw = sys.stdin.read().strip()
        out = run(json.loads(raw) if raw else {})
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
