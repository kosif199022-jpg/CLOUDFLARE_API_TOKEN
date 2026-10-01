#!/usr/bin/env python3
"""KOSIF Jev — build, check and interpret Jev (TypeSafe System One) decision packets.

Jev answers closed-set judgements: `noul` (yes/no probability), `choice` (one of N labels with
probabilities) and `score` (position on an ordered rubric). This helper keeps calls well-formed and
honest; it does not call Jev itself (the host's jev_noul / jev_choice / jev_score tools do).

  jev_packet.py build      < {"mode": "choice", "question": "...", "evidence": {...}, "options": {"A": "desc", ...}}
  jev_packet.py interpret  < {"response": {<raw Jev tool result>}, "options"?: [...]}
  jev_packet.py stability  < {"responses": [<raw result>, <raw result>, ...]}

build   → packet ready for the tool + issues. BLOCK when the question asks Jev to authorise a risky action
          (Jev never approves payments, deletions, pushes, sends or security bypasses), when evidence is
          empty, or options are not a closed set. Secrets and personal data are redacted from the state.
interpret → decision, margin/uncertainty class and a recommended next step; `score` gives the expected level
          and the argmax level separately.
stability → whether repeated/reordered/rephrased calls agree (use for consequential decisions).
Exit 0 ok · 1 needs revision/unstable · 3 blocked · 2 invalid.
"""
import json
import math
import re
import sys

AUTHORISE = r"\b(should (i|we)|can (i|we)|may (i|we)|is it (ok|okay|safe) to|approve|authori[sz]e|allow)\b.{0,60}\b(pay(ment|ing)?|transfer|purchas|buy|delet|drop|wipe|force[- ]push|push|merg|deploy|send|publish|post|submit|bypass|disabl|share (the )?(password|credential))|هل (أ|ن)(دفع|حذف|نشر|أرسل|ادمج|اعتمد)|وافق على (الدفع|الحذف|النشر)"
REDACT = [
    (r"\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}", "[REDACTED_KEY]"), (r"\bgh[pousr]_[A-Za-z0-9]{36,}", "[REDACTED_GITHUB_TOKEN]"),
    (r"\bAKIA[0-9A-Z]{16}\b", "[REDACTED_AWS_KEY]"), (r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----", "[REDACTED_PRIVATE_KEY]"),
    (r"\b[\w.+-]+@[\w-]+\.[\w.-]{2,}\b", "[REDACTED_EMAIL]"), (r"(?<!\d)(?:\+?966|0)?5\d{8}(?!\d)", "[REDACTED_PHONE]"),
    (r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)", "[REDACTED_NUMBER]"), (r"\bSA\d{2}[0-9A-Z]{20}\b", "[REDACTED_IBAN]"),
]


def redact(obj, count):
    if isinstance(obj, str):
        for rx, rep in REDACT:
            obj, n = re.subn(rx, rep, obj)
            count[0] += n
        return obj
    if isinstance(obj, list):
        return [redact(x, count) for x in obj]
    if isinstance(obj, dict):
        return {k: redact(v, count) for k, v in obj.items()}
    return obj


def build(o):
    mode = o.get("mode")
    if mode not in {"noul", "choice", "score"}:
        raise ValueError("mode must be noul, choice or score")
    q = str(o.get("question", "")).strip()
    if not q:
        raise ValueError("question is required")
    issues, verdict = [], "OK"
    if re.search(AUTHORISE, q, re.I):
        return {"verdict": "BLOCK", "issues": ["Jev cannot authorise risky actions (payment, deletion, push/merge/deploy, send/publish, "
                                               "security bypass). Use it to classify or score evidence; the approval stays with the user."]}
    ev = o.get("evidence")
    if ev in (None, "", [], {}):
        return {"verdict": "BLOCK", "issues": ["evidence is empty: put the facts Jev should judge in `evidence` (it becomes `state`)"]}
    if len(q.split()) < 5:
        issues.append("question is very short: write the complete decision question with its context")
        verdict = "REVISE"
    if not q.endswith(("?", "؟")) and mode != "score":
        issues.append("phrase the instruction as a question ending with '?'")
    cnt = [0]
    state = redact(ev, cnt)
    if cnt[0]:
        issues.append(f"redacted {cnt[0]} secret/personal value(s) from the state")
    size = len(json.dumps(state, ensure_ascii=False))
    if size > 20000:
        issues.append(f"state is {size} chars: summarise to the decision-relevant facts")
        verdict = "REVISE"
    packet = {"state": state, "instructions": q}
    if mode == "noul":
        tool = "jev_noul"
        for k in ("true_criteria", "false_criteria"):
            if o.get(k):
                packet[k] = o[k]
        if not (o.get("true_criteria") or o.get("false_criteria")):
            issues.append("add true_criteria/false_criteria so 'yes' is unambiguous")
    elif mode == "choice":
        tool = "jev_choice"
        opts = o.get("options")
        if isinstance(opts, list):
            opts = {str(x): None for x in opts}
        if not isinstance(opts, dict) or len(opts) < 2:
            return {"verdict": "BLOCK", "issues": ["choice needs a closed set of ≥ 2 options"]}
        if len(opts) > 12:
            issues.append(f"{len(opts)} options: prune to the feasible ≤ 12 first (decision_sensitivity.py)")
            verdict = "REVISE"
        labels = [k.strip().lower() for k in opts]
        if len(set(labels)) != len(labels):
            return {"verdict": "BLOCK", "issues": ["duplicate option labels"]}
        if sum(1 for v in opts.values() if not v) > len(opts) // 2:
            issues.append("most options have no description: describe what each label means")
        if not any(re.search(r"none|other|unclear|لا شيء|غير واضح", k, re.I) for k in opts) and o.get("allow_none", True):
            issues.append("consider an explicit 'none/unclear' option so Jev is not forced to pick a wrong label")
        packet["criteria"] = opts
    else:
        tool = "jev_score"
        levels = o.get("options") or o.get("levels")
        if not isinstance(levels, list) or not 2 <= len(levels) <= 10:
            return {"verdict": "BLOCK", "issues": ["score needs an ordered rubric of 2–10 levels (lowest → highest)"]}
        packet["criteria"] = levels
    if o.get("model"):
        packet["model"] = o["model"]
    return {"verdict": verdict, "tool": tool, "packet": packet, "issues": issues,
            "provenance_to_record": ["returned model id", "packet (as sent)", "decision", "confidence/probabilities", "timestamp"]}


def _decision(resp):
    if isinstance(resp, str):
        resp = json.loads(resp)
    d = (resp.get("answers") or {}).get("decision") or resp.get("decision") or resp
    return resp.get("model"), d


def interpret(o):
    model, d = _decision(o.get("response"))
    t = d.get("type")
    if t == "noul":
        p = float(d["noul"])
        cls = "strong-yes" if p >= 0.8 else "lean-yes" if p >= 0.65 else "uncertain" if p > 0.35 else "lean-no" if p > 0.2 else "strong-no"
        nxt = "act on it only if reversible; otherwise gather evidence" if cls in {"lean-yes", "lean-no"} else \
            "gather more evidence or ask the user" if cls == "uncertain" else "usable as a judgement (not as approval)"
        return {"model": model, "type": t, "answer": "yes" if p >= 0.5 else "no", "p_yes": p, "class": cls, "next": nxt}
    if t == "choice":
        probs = {k: float(v) for k, v in (d.get("probabilities") or {}).items()}
        ranked = sorted(probs.items(), key=lambda kv: -kv[1])
        margin = ranked[0][1] - ranked[1][1] if len(ranked) > 1 else 1.0
        conf = float(d.get("confidence", ranked[0][1] if ranked else 0))
        cls = "clear" if conf >= 0.8 and margin >= 0.4 else "lean" if conf >= 0.6 else "uncertain"
        return {"model": model, "type": t, "choice": d.get("choice"), "confidence": conf, "margin": round(margin, 3),
                "ranking": ranked, "class": cls,
                "next": {"clear": "usable; still verify with deterministic checks where they exist",
                         "lean": "run stability (reorder options / rephrase) before relying on it",
                         "uncertain": "do not rely on it: add evidence, split the question, or ask the user"}[cls],
                "caveat": "high confidence does not prove the question was answerable; if the deciding information is missing from the state, ask the user"}
    if t == "score":
        probs = {int(k): float(v) for k, v in (d.get("probabilities") or {}).items()}
        legend = d.get("legend") or {}
        expected = sum(k * v for k, v in probs.items()) if probs else float(d.get("score", 0))
        argmax = max(probs, key=probs.get) if probs else round(expected)
        ent = -sum(v * math.log(v, 2) for v in probs.values() if v > 0) if probs else None
        return {"model": model, "type": t, "expected_level": round(expected, 3), "argmax_level": argmax,
                "argmax_label": legend.get(str(argmax)) or legend.get(argmax), "confidence": d.get("confidence"),
                "entropy_bits": round(ent, 3) if ent is not None else None,
                "class": "clear" if ent is not None and ent < 0.8 else "spread",
                "note": "`score` in the raw result is the expected level (probability-weighted), not a percentage"}
    raise ValueError(f"unrecognised Jev result type {t!r}")


def stability(o):
    rs = o.get("responses") or []
    if len(rs) < 2:
        raise ValueError("give ≥ 2 responses (e.g. original, options reordered, question rephrased)")
    reads = [interpret({"response": r}) for r in rs]
    key = {"noul": "answer", "choice": "choice", "score": "argmax_level"}[reads[0]["type"]]
    vals = [r[key] for r in reads]
    stable = len(set(map(str, vals))) == 1
    return {"stable": stable, "decisions": vals, "reads": reads,
            "next": "stable: usable as a judgement" if stable else "unstable: the question is ambiguous or evidence insufficient — do not rely on Jev here"}


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    try:
        o = json.load(sys.stdin)
        if cmd == "build":
            out = build(o)
            code = {"OK": 0, "REVISE": 1, "BLOCK": 3}[out["verdict"]]
        elif cmd == "interpret":
            out, code = interpret(o), 0
        elif cmd == "stability":
            out = stability(o)
            code = 0 if out["stable"] else 1
        else:
            raise ValueError("usage: jev_packet.py build|interpret|stability < json")
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
