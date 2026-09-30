#!/usr/bin/env python3
"""KOSIF Think Pro 3 regression suite (v3.0.0).

Covers the 2.7.3 invariants (receipts, spoofing, dissent, taint, budgets,
self-improvement, manifest/skill binding) plus the 3.0 layer: typed evidence
consistency (known-answer 92), completion-ready receipts, artifact normalization,
version negotiation, the Ronin-duck execution contract, and every expert helper.
Tests that need optional libraries (numpy/Pillow) are reported as skipped, never
as passed. Exit 0 only when no test failed.
"""
import importlib.util
import json
import math
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SKILLS = ROOT / "skills"
sys.path.insert(0, str(HERE))

from artifact_normalize import normalize  # noqa: E402
from budget_stop_check import decide as budget_decide  # noqa: E402
from evidence_consistency_check import validate as consistency  # noqa: E402
from pro_receipt_verify import MODULES, PROFILES  # noqa: E402
from pro_receipt_verify import validate as receipt_validate  # noqa: E402
from self_improvement_eval import evaluate as improve_eval  # noqa: E402
from source_taint_check import validate as taint_validate  # noqa: E402
from version_check import negotiate  # noqa: E402

EXPERTS = ["kosif-vision", "kosif-image-studio", "kosif-lighting", "kosif-audio", "kosif-code-master", "kosif-video"]


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, SKILLS / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def valid_receipt(trace="2.7.1"):
    r = {
        "trace_version": trace,
        "modules": {m: "relevant" for m in MODULES},
        "profiles": {p: "complete" for p in PROFILES},
        "models_tools": [{"id": "kosif-gpt", "kind": "model", "requested": True, "available": True, "used": True,
                          "actual_source": "cleanapis", "actual_model": "gpt-5.6-sol", "fallback_used": False,
                          "receipt_id": "r1"}],
        "dissent_ledger": [{"profile": p, "conclusion": "x", "strongest_objection": "y", "disposition": "accepted",
                            "what_would_change_it": "new evidence"} for p in PROFILES],
        "source_taint": {"checked": True, "blocked_supports": 0},
        "evidence_gaps": [],
        "gates": {"bias_gate": "pass", "optimizer_gate": {"feasible": 1}, "self_critic": "pass", "verifier": "pass"},
        "execution_contract": "present", "postcondition": "pass",
        "budget": {"model_calls_used": 5, "max_model_calls": 10, "tool_calls_used": 3, "max_tool_calls": 12,
                   "retries_used": 0, "max_retries": 3, "no_change_count": 0, "max_no_change": 2, "status": "completed"},
    }
    if trace == "3.0":
        r["consistency"] = {"checked": True, "quarantined": ["97"], "evidence_conflict": False}
        r["final_answer"] = "92"
    return r


def clone(x):
    return json.loads(json.dumps(x))


def run():
    tests = []
    skipped = []

    def check(name, cond):
        tests.append((name, bool(cond)))

    # ---- 2.7.3 invariants -------------------------------------------------
    good = valid_receipt()
    check("valid-receipt", receipt_validate(good)["ok"])
    spoof = {k: v for k, v in good.items() if k != "models_tools"}
    check("spoofed-no-capability-receipts-blocked", not receipt_validate(spoof)["ok"])
    bad = clone(good); bad["models_tools"][0]["available"] = False
    check("used-unavailable-blocked", not receipt_validate(bad)["ok"])
    host = clone(good); host["models_tools"][0].pop("receipt_id", None)
    host["models_tools"][0]["receipt_evidence"] = {"type": "host-tool-result", "observed": True, "limitation": "no native id"}
    check("host-tool-result-evidence-accepted", receipt_validate(host)["ok"])
    missing = clone(host); missing["models_tools"][0]["receipt_evidence"]["observed"] = False
    check("unobserved-receipt-evidence-blocked", not receipt_validate(missing)["ok"])
    bad = clone(good); bad["dissent_ledger"] = bad["dissent_ledger"][1:]
    check("missing-dissent-blocked", not receipt_validate(bad)["ok"])
    taint = {"claims": [{"id": "c1", "requires_source": True, "current_authority": False}],
             "sources": [{"id": "jaynes-testbank", "status": "quarantined", "supports": ["c1"]}]}
    check("quarantined-source-blocked", not taint_validate(taint)["ok"])
    hist = {"claims": [{"id": "c1", "requires_source": True, "current_authority": True}],
            "sources": [{"id": "ifrs2018", "status": "historical", "supports": ["c1"]}]}
    check("historical-current-authority-blocked", not taint_validate(hist)["ok"])
    base = {"model_calls": 1, "max_model_calls": 10, "tool_calls": 1, "max_tool_calls": 10, "retries": 0,
            "max_retries": 2, "elapsed_seconds": 1, "max_elapsed_seconds": 60, "no_change_count": 0, "max_no_change": 2}
    check("budget-hard-stop", budget_decide({**base, "model_calls": 10})["action"] == "stop")
    check("no-change-escalate", budget_decide({**base, "no_change_count": 2})["action"] == "escalate")
    crit = {"false_success_rate": {"direction": "lower", "required": True, "max_regression": 0, "min_improvement": 0},
            "source_support": {"direction": "higher", "required": True, "max_regression": 0, "min_improvement": 0}}
    check("bad-self-improvement-rejected", not improve_eval({"baseline": {"false_success_rate": 0.1, "source_support": 0.8},
          "candidate": {"false_success_rate": 0.2, "source_support": 0.81}, "criteria": crit})["ok"])
    check("good-self-improvement-passes", improve_eval({"baseline": {"false_success_rate": 0.1, "source_support": 0.8},
          "candidate": {"false_success_rate": 0.05, "source_support": 0.9}, "criteria": crit})["ok"])

    # ---- 3.0 typed consistency gate ---------------------------------------
    ev = [{"id": "e1", "source": "gpt", "expression": "120 - 120*15% - 10", "claimed": "92"},
          {"id": "e2", "source": "claude", "expression": "(120 - 18) - 10"}]
    r = consistency({"evidence": ev, "answers": [{"id": "a1", "value": "97"}, {"id": "a2", "value": "100"},
                                                 {"id": "a3", "value": "102"}]})
    check("known-answer-92-converges", r["converged_value"] == "92")
    check("known-answer-92-quarantines-97-100-102", len(r["quarantined_answers"]) == 3)
    check("known-answer-92-provisional-repair", (r["provisional_repair"] or {}).get("value") == "92")
    r = consistency({"evidence": ev, "answers": [{"value": "92"}, {"value": "97"}]})
    check("correct-answer-accepted-wrong-quarantined", [a["value"] for a in r["accepted_answers"]] == ["92"]
          and r["provisional_repair"] is None)
    r = consistency({"evidence": [ev[0]], "answers": [{"value": "97"}]})
    check("single-source-does-not-converge", r["converged_value"] is None)
    r = consistency({"evidence": [{"source": "a", "expression": "2+2"}, {"source": "b", "expression": "2*2"},
                                  {"source": "c", "expression": "10-5"}, {"source": "d", "expression": "25/5"}]})
    check("two-converged-values-escalate", r["evidence_conflict"] and not r["ok"])
    r = consistency({"evidence": [{"source": "x", "expression": "__import__('os').system('id')"}]})
    check("code-injection-expression-rejected", not r["evidence"][0]["valid"])
    r = consistency({"evidence": [{"source": "x", "type": "sum", "parts": ["18", "102"], "total": "121"},
                                  {"source": "x", "type": "percent", "part": "18", "whole": "120", "percent": "15"},
                                  {"source": "x", "type": "unit", "units": ["kg", "g"]},
                                  {"source": "x", "type": "date_order", "dates": ["2026-03-01", "2026-01-01"]}]})
    check("typed-validators-sum-unit-date-flagged", [e["valid"] for e in r["evidence"]] == [False, True, False, False])

    # ---- 3.0 completion-ready receipts ------------------------------------
    g3 = valid_receipt("3.0")
    v = receipt_validate(g3)
    check("trace-3.0-completion-ready", v["ok"] and v["completion_ready"])
    rev = clone(g3); rev["gates"]["verifier"] = "revise"
    v = receipt_validate(rev)
    check("verifier-revise-structurally-valid-not-ready", v["structurally_valid"] and not v["completion_ready"])
    q = clone(g3); q["final_answer"] = "97"
    check("quarantined-final-answer-not-ready", not receipt_validate(q)["completion_ready"])
    nc = clone(g3); nc.pop("consistency")
    check("trace-3.0-requires-consistency", not receipt_validate(nc)["ok"])
    un = clone(g3); un["dissent_ledger"][0]["disposition"] = "unresolved"
    check("unresolved-dissent-not-ready", not receipt_validate(un)["completion_ready"])
    check("legacy-2.7.1-still-structurally-valid", receipt_validate(valid_receipt("2.7.1"))["structurally_valid"])

    # ---- normalization & versions -----------------------------------------
    n = normalize({"profile": "Skeptic", "answer": "92", "sources": ["calc", "Risk: stale defect rate"],
                   "concerns": "Objection: small sample", "certainty": "85%"})
    a = n["artifact"]
    check("normalize-aliases-and-moves", a["agent"] == "Skeptic" and a["conclusion"] == "92"
          and "stale defect rate" in a["risks"] and "small sample" in a["objections"] and a["confidence"] == 0.85)
    check("normalize-reports-changes", len(n["changes"]) >= 5)
    check("version-compatible", negotiate({"runtime": "0.8.3", "mobile_bridge": "1.4.0", "chatgpt_plugin": "1.5.3",
                                           "trace": "3.0"})["status"] == "compatible")
    check("version-old-runtime-incompatible", negotiate({"runtime": "0.8.1", "mobile_bridge": "1.4.0",
                                                         "chatgpt_plugin": "1.5.3"})["status"] == "incompatible")
    check("version-unobserved-degraded", negotiate({"trace": "3.0"})["status"] == "degraded")

    # ---- expert helpers ----------------------------------------------------
    lint = load("kosif-image-studio/scripts/prompt_lint.py", "prompt_lint").lint
    contract = {"required": ["duck", "lacquered armor"], "forbidden": ["rifle", "tactical", "helicopter"]}
    bad_brief = "A duck soldier in a tactical vest with an assault rifle, lacquered armor, helicopter overhead, 16:9"
    good_brief = ("Cinematic film still of an anthropomorphic duck ronin in Edo-period lacquered armor in a rain-lit "
                  "temple courtyard, medium shot, low angle, 85mm f/1.4, soft key light from left, warm lantern rim "
                  "light, teal-orange grade, photorealistic, ultra-detailed feathers, sharp focus, 2.39:1, no modern "
                  "tactical gear")
    check("ronin-duck-modern-brief-blocked", lint({"prompt": bad_brief, "contract": contract})["verdict"] == "BLOCK")
    check("ronin-duck-corrected-brief-passes", lint({"prompt": good_brief, "contract": contract})["verdict"] == "PASS")
    check("character-lock-enforced", lint({"prompt": good_brief, "locks": {"character": "scar over left eye"}})["verdict"] != "PASS")
    check("video-mode-requires-motion", "camera_move" in lint({"prompt": "a cat on a sofa, 16:9, photorealistic",
                                                               "mode": "video"})["missing"])

    op = load("kosif-lighting/scripts/light_calc.py", "light_calc").op
    check("light-inverse-square-minus-2-stops", op({"op": "inverse_square", "d1": 1, "d2": 2})["stops_change"] == -2.0)
    check("light-equivalent-exposure", op({"op": "equivalent", "aperture": 2.8, "shutter": "1/125", "iso": 100,
                                           "new_aperture": 1.4})["new_shutter"] == "1/500s")
    check("light-mired-daylight-to-tungsten-cto", op({"op": "mired", "from_k": 5600, "to_k": 3200})["nearest_gel"] == "Full CTO")
    check("light-ev-sunny16", abs(op({"op": "ev", "aperture": 16, "shutter": "1/125", "iso": 100})["ev100"] - 15) < 0.1)

    scan_text = load("kosif-code-master/scripts/code_scan.py", "code_scan").scan_text
    leaked = scan_text("x.py", 'API_KEY = "sk-proj-abcdefghijklmnopqrstuvwxyz123456"\nsubprocess.run(c, shell=True)\n')
    rules = {f["rule"] for f in leaked}
    check("code-scan-secret-and-shell-found", "secret-openai-key" in rules and "py-shell-true" in rules)
    check("code-scan-secret-redacted", all("klmnopq" not in f["code"] for f in leaked if f["rule"].startswith("secret")))
    clean = scan_text("ok.py", 'import os\nKEY = os.environ["API_KEY"]\ncur.execute("SELECT 1 WHERE id=%s", (i,))\n')
    check("code-scan-clean-code-no-high", not [f for f in clean if f["severity"] in ("critical", "high")])
    check("code-scan-css-id-not-secret", not scan_text("a.js", 'const s=$("#sk-export-sheet-summary-table");'))

    try:
        import numpy as np  # noqa: F401
        have_np = True
    except ImportError:
        have_np = False
        skipped.append("audio-*: numpy missing")
    if have_np:
        import wave
        aa = load("kosif-audio/scripts/audio_analyze.py", "audio_analyze")
        with tempfile.TemporaryDirectory() as td:
            sr = 48000
            t = np.arange(sr * 5) / sr
            p = Path(td) / "sine.wav"
            with wave.open(str(p), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
                w.writeframes((np.sin(2 * np.pi * 997 * t) * 32767).astype("<i2").tobytes())
            rep = aa.analyze(str(p))
            check("audio-bs1770-997hz-fullscale-minus-3.01-lufs", abs(rep["levels"]["integrated_lufs"] + 3.01) < 0.05)
            check("audio-pure-tone-no-bpm", rep["tempo"]["bpm_estimate"] is None)
            sr2, n = 44100, 44100 * 16
            x = np.zeros(n)
            for k in range(0, n, int(sr2 * 0.5)):
                x[k:k + 800] += np.sin(2 * np.pi * 1500 * np.arange(800) / sr2) * np.exp(-np.arange(800) / 150) * 0.8
            p2 = Path(td) / "click.wav"
            with wave.open(str(p2), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr2)
                w.writeframes((x * 32767).astype("<i2").tobytes())
            bpm = aa.analyze(str(p2))["tempo"]["bpm_estimate"]
            check("audio-120-bpm-click", bpm is not None and abs(bpm - 120) < 1.5)
            isp = Path(td) / "isp.wav"
            with wave.open(str(isp), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
                w.writeframes((np.sin(2 * np.pi * np.arange(sr * 2) / 4 + math.pi / 4) * 32767).astype("<i2").tobytes())
            lv = aa.analyze(str(isp))["levels"]
            check("audio-true-peak-catches-intersample", lv["peak_dbfs"] < -2.9 and lv["true_peak_dbtp_approx"] > -0.3)

    try:
        from PIL import Image, ImageFilter
        have_pil = have_np
    except ImportError:
        have_pil = False
    if not have_pil:
        skipped.append("vision-*: Pillow/numpy missing")
    else:
        ia = load("kosif-vision/scripts/image_analyze.py", "image_analyze")
        with tempfile.TemporaryDirectory() as td:
            h, w = 600, 900
            yy, xx = np.mgrid[0:h, 0:w]
            img = np.zeros((h, w, 3))
            img[..., 0] = 80 + 120 * (xx / w); img[..., 1] = 60 + 80 * (xx / w); img[..., 2] = 50 + 40 * (xx / w)
            img[((xx - 2 * w / 3) ** 2 + (yy - h / 3) ** 2) < 60 ** 2] = [240, 200, 150]
            p = Path(td) / "a.png"
            Image.fromarray(img.clip(0, 255).astype("uint8")).save(p)
            Image.open(p).filter(ImageFilter.GaussianBlur(6)).save(Path(td) / "b.png")
            ra = ia.analyze(str(p))
            check("vision-aspect-3:2", ra["geometry"]["aspect_ratio"]["nearest"] == "3:2")
            check("vision-warm-cast", ra["color"]["cast"] == "warm")
            check("vision-brighter-right", ra["lighting_heuristic"]["brighter_side"] == "right")
            check("vision-thirds-placement", ra["composition"]["placement"] == "rule-of-thirds")
            cmp = ia.compare(str(p), str(Path(td) / "b.png"))
            check("vision-compare-sharper-original", cmp["sharper"] == "A")

    # ---- package binding ---------------------------------------------------
    manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    skill = (SKILLS / "kosif-think-pro" / "SKILL.md").read_text(encoding="utf-8")
    runtime = (SKILLS / "kosif-think-pro" / "references" / "runtime-consistency.md").read_text(encoding="utf-8")
    check("manifest-3.0.0", manifest.get("version") == "3.0.0" and codex.get("version") == "3.0.0")
    check("manifest-description-lengths", len(manifest["extensions"]["com.openai"]["interface"]["longDescription"]) <= 1024
          and len(manifest["extensions"]["com.openai"]["interface"]["shortDescription"]) <= 30)
    check("skill-version-3.0.0", "# KOSIF Think Pro 3 — v3.0.0" in skill)
    check("skill-binds-layers", all(x in skill for x in ("verified-self-improvement.md", "pro_receipt_verify.py",
          "source-taint-protocol.md", "runtime-consistency.md", "evidence_consistency_check.py", "expert-studio.md")))
    check("skill-routes-all-experts", all(e in skill for e in EXPERTS))
    check("runtime-answer-evidence-guard", "quarantined" in runtime.lower()
          and "deterministically valid arithmetic" in runtime.lower() and "92" in runtime)
    check("runtime-host-exposure-guard", "host tool catalog" in runtime.lower() and "server" in runtime.lower())
    for e in EXPERTS:
        text = (SKILLS / e / "SKILL.md").read_text(encoding="utf-8") if (SKILLS / e / "SKILL.md").exists() else ""
        check(f"expert-skill-{e}-frontmatter", text.startswith("---\nname: " + e + "\n") and "\ndescription: " in text)

    failed = [n for n, ok in tests if not ok]
    out = {"ok": not failed, "passed": sum(1 for _, ok in tests if ok), "total": len(tests), "failed": failed,
           "skipped": skipped, "version": "3.0.0"}
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(run())
