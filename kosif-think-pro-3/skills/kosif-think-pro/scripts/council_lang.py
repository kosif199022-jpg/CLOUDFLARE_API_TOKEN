#!/usr/bin/env python3
"""KOSIF Council Language (KCL) v3.3 — the typed Python lingua franca of the 100-member council.

Every council member speaks the same small, typed language:

    Evidence   – something observed or measured (probe results are `measured=True`)
    Objection  – a problem the member raises, with a Severity and an optional veto domain
    Artifact   – one member's sealed first-pass position: stance, confidence, claims, evidence,
                 objections, the member's signature question and the probes it actually ran

Members do not "vote"; they exchange Artifacts. Artifacts are sealed (SHA-256 over canonical
JSON) in the first pass, before any cross-critique, so later agreement cannot rewrite what a
member said independently. The wire format is plain JSON and is accepted as-is by
council_aggregate.py.

Each member owns 1–3 deterministic *probes* (real, executable Python measurements: WCAG
contrast, secret scanning, Bayes, Benford, NPV/IRR, git-operation risk, human-checkpoint
detection, cyclomatic complexity …). A member without input for its probes says
`not-material` instead of inventing a measurement.

CLI
  council_lang.py spec                    language grammar + probe catalogue (JSON)
  council_lang.py probes                  probe names with the inputs each needs
  council_lang.py probe NAME   < kwargs   run one probe, e.g. {"fg": "#777", "bg": "#fff"}
  council_lang.py persona ID              the member's card (specialty, capabilities, probes, forge)
  council_lang.py run          < request  select members, run their probes, seal, aggregate
      request: {"task": "...", "mode": "standard|pro|full", "domains": [...],
                "inputs": {"contrast": {"fg": "#777", "bg": "#fff"}, "secrets": {"text": "..."}}}
Exit codes for `run`: 0 proceed · 1 revise · 3 escalate · 2 invalid input.
Limits (honest): probes measure what they are given; they do not prove truth, and all members
voiced by one model remain ONE independent source.
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from council_aggregate import aggregate
from council_select import load, select
from kcl_probes import (KCL_VERSION, PROBES, Artifact, Evidence, Objection, Severity, Stance,  # noqa: F401
                        run_probe)


# ───────────────────────────── members and the council ─────────────────────────────
@dataclass(frozen=True, slots=True)
class Member:
    card: Mapping[str, Any]

    @property
    def id(self) -> str:
        return self.card["id"]

    def assess(self, inputs: Mapping[str, Mapping[str, Any]]) -> Artifact:
        evidence, objections, ran = [], [], []
        for name in self.card.get("probes", []):
            if name not in inputs:
                continue
            try:
                r = run_probe(name, inputs[name])
            except Exception as e:  # noqa: BLE001 — a failed probe is reported, never hidden
                objections.append(Objection(text=f"probe {name} could not run: {e}", severity=Severity.LOW))
                continue
            ran.append(name)
            evidence.append(Evidence(source=f"probe:{name}", content=r.detail, measured=True,
                                     data={"ok": r.ok, "value": r.value}))
            if r.flag.rank >= Severity.MATERIAL.rank:
                sev = Severity.BLOCKING if (r.flag is Severity.BLOCKING and self.card.get("veto")) else Severity.MATERIAL
                objections.append(Objection(text=f"{self.card['name']}: {r.detail}", severity=sev, veto=self.card.get("veto")))
            elif r.flag is Severity.LOW:
                objections.append(Objection(text=f"{self.card['name']}: {r.detail}", severity=Severity.LOW))
        if not ran:
            return Artifact(persona=self.id, stance=Stance.NOT_MATERIAL, confidence=0.0, question=self.card["question"],
                            claims=(f"no input for my probes {self.card.get('probes', [])}; lens applied qualitatively only",),
                            objections=tuple(objections))
        worst = max((o.severity.rank for o in objections), default=0)
        stance = Stance.OPPOSE if worst >= Severity.MATERIAL.rank else Stance.SUPPORT
        conf = min(1.0, 0.55 + 0.15 * len(ran))
        return Artifact(persona=self.id, stance=stance, confidence=conf, question=self.card["question"],
                        claims=(self.card["if_then"],), evidence=tuple(evidence), objections=tuple(objections),
                        probes_run=tuple(ran))


class Council:
    """First pass → seal → (model-written cross-critique happens outside) → aggregate."""

    def __init__(self, cards: Iterable[Mapping[str, Any]]):
        self.members = [Member(c) for c in cards]
        self._ledger: Mapping[str, tuple[Artifact, str]] = MappingProxyType({})

    def first_pass(self, inputs: Mapping[str, Mapping[str, Any]]) -> Mapping[str, tuple[Artifact, str]]:
        if self._ledger:
            raise RuntimeError("first pass already sealed; independent positions cannot be re-written")
        self._ledger = MappingProxyType({m.id: (a, a.seal()) for m in self.members for a in [m.assess(inputs)]})
        return self._ledger

    def verify(self) -> bool:
        return all(a.seal() == s for a, s in self._ledger.values())

    def transcript(self) -> list[dict[str, Any]]:
        return [{**a.wire(), "seal": s} for a, s in self._ledger.values()]


def run(req: Mapping[str, Any]) -> dict[str, Any]:
    data = load()
    cards = {p["id"]: p for p in data["personas"]}
    sel = select(req, data)
    council = Council(cards[p["id"]] for p in sel["personas"])
    council.first_pass(req.get("inputs") or {})
    arts = council.transcript()
    heard = [a for a in arts if a["stance"] != "not-material"]
    agg = aggregate({"artifacts": heard or arts, "sources": {"models": ["single-model"],
                     "tools": sorted({f"probe:{p}" for a in arts for p in a["probes_run"]})}}, data)
    return {"kcl": KCL_VERSION, "task": req.get("task"), "mode": sel["mode"], "members": len(arts),
            "measured_members": len(heard), "seals_verified": council.verify(), "transcript": arts,
            "aggregate": agg}


def spec() -> dict[str, Any]:
    return {"kcl": KCL_VERSION,
            "types": {"Stance": [s.value for s in Stance], "Severity": [s.value for s in Severity],
                      "Evidence": [f for f in Evidence.__dataclass_fields__], "Objection": [f for f in Objection.__dataclass_fields__],
                      "Artifact": [f for f in Artifact.__dataclass_fields__]},
            "rules": ["first pass is sealed (SHA-256) before cross-critique",
                      "a member without probe input answers not-material, never an invented number",
                      "support + blocking objection is a type error",
                      "blocking veto or unresolved material objection cannot be outvoted (council_aggregate.py)",
                      "all members voiced by one model = one independent source"],
            "probes": {n: {"needs": list(needs), "summary": s} for n, (_, needs, s) in sorted(PROBES.items())}}


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "spec"
    try:
        match cmd:
            case "spec":
                out: Any = spec()
            case "probes":
                out = {n: list(needs) for n, (_, needs, _) in sorted(PROBES.items())}
            case "probe":
                out = asdict(run_probe(argv[2], json.load(sys.stdin)))
            case "persona":
                cards = {p["id"]: p for p in load()["personas"]}
                out = cards[argv[2]]
            case "run":
                out = run(json.load(sys.stdin))
                print(json.dumps(out, ensure_ascii=False, sort_keys=True, default=str))
                return {"proceed": 0, "revise": 1, "escalate": 3}.get(out["aggregate"].get("verdict"), 2)
            case _:
                raise ValueError(f"unknown command {cmd}")
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps(out, ensure_ascii=False, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
