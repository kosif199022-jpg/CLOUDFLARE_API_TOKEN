#!/usr/bin/env python3
"""KOSIF Project Forge (v3.3) — any council member scaffolds a complete, runnable project alone.

stdin JSON: {"member": "security-red-teamer", "name": "secret-guard", "out": "/path/to/dir",
             "goal": "optional one-line product goal", "archetype": "optional override"}
or CLI:     project_forge.py MEMBER_ID NAME OUT_DIR [ARCHETYPE]
            project_forge.py --list                    archetypes and which members lead each

What is generated (standard library only for Python archetypes; Node ≥ 18 for the worker):
  * working code for the archetype (library · CLI · JSON HTTP service · idempotent data pipeline ·
    bounded agent loop · accessible static site · Cloudflare Worker);
  * the member's deterministic probes, vendored verbatim from kcl_probes.py and wired into the product;
  * tests that pass on generation (the forge runs them and reports the real result);
  * README with the member's specialty and a milestone roadmap built from the member's 8 programming
    capabilities (each with acceptance criteria), docs/ARCHITECTURE.md, docs/adr/0001, SECURITY.md,
    CI workflow (.github/workflows/ci.yml), .gitignore.
Honest scope: the forge builds a verified foundation and a roadmap; the large project is then grown
milestone by milestone, each milestone test-first. It never claims features it did not generate.
Exit 0 = generated and tests passed; 1 = generated but tests failed/not run; 2 = invalid input.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARCHETYPES = {
    "python-lib": "typed Python library with a validated record registry",
    "python-cli": "argparse command-line tool with check and report commands",
    "python-service": "stdlib JSON HTTP API with /health, /capabilities and /check",
    "data-pipeline": "idempotent CSV → validate → SQLite pipeline with run log",
    "agent": "bounded observe-plan-act-verify agent loop with risk gate and budget",
    "static-web": "accessible, responsive static site with light/dark tokens and an audit test",
    "cf-worker": "Cloudflare Worker JSON API with node:test tests and wrangler config",
}


def _load_council():
    from council_select import load  # local import keeps --list fast even without the data file
    return load()


def pkg_name(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return s if s and not s[0].isdigit() else f"p_{s}"


def render(text: str, ctx: dict[str, str]) -> str:
    for k, v in ctx.items():
        text = text.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{[A-Z_]+\}\}", text)
    if left:
        raise ValueError(f"unrendered placeholders {left}")
    return text


# ───────────────────────────── shared files ─────────────────────────────
README = """# {{NAME}}

{{GOAL}}

Forged by the KOSIF council member **{{MEMBER}}** ({{MEMBER_AR}}) — *{{SPECIALTY}}*.
Archetype: `{{ARCH}}` — {{ARCH_DESC}}.

## Run
{{RUN}}

## Built-in checks (vendored `kcl_probes.py`)
{{PROBE_LIST}}

## Roadmap — the member's programming capabilities as milestones
Each milestone is done only when its acceptance test exists, fails first, then passes in CI.
{{ROADMAP}}

## Expertise applied in reviews
{{MASTERY}}

## Honest scope
This repository is a verified foundation (tests pass on generation) plus a roadmap. Features listed in
the roadmap are **not implemented yet** until their milestone tests exist.
"""

ARCH_DOC = """# Architecture — {{NAME}}

## Layers
1. **Interface** — {{INTERFACE}}
2. **Core** — domain logic with typed inputs and explicit errors.
3. **Quality** — `kcl_probes.py` deterministic checks owned by {{MEMBER}}: {{PROBES}}.
4. **Tests** — unit tests for core and probes; CI runs them on every push.

## Principles
- Validate at boundaries, fail loudly with actionable messages.
- No secrets in code: configuration comes from environment variables (see `.env.example` when present).
- Every side effect is idempotent or guarded; every claim of success is backed by a test or an observed state.
"""

ADR = """# ADR-0001: Start from the `{{ARCH}}` archetype

- Status: accepted
- Context: {{GOAL}}
- Decision: begin with {{ARCH_DESC}}, vendored KOSIF probes and CI, then grow by milestones.
- Consequences: small verified core first; each roadmap item adds tests before code.
"""

SECURITY = """# Security

- Report vulnerabilities privately to the maintainers; do not open public issues for them.
- Secrets are never committed; use environment variables or the platform secret store.
- `python3 -m {{PKG}}.quality` (Python archetypes) or the probe tests scan for secrets and unsafe SQL where applicable.
"""

GITIGNORE = "__pycache__/\n*.pyc\n.venv/\n.env\n*.sqlite3\nnode_modules/\ndist/\n.wrangler/\n"

CI_PY = """name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python: ["3.10", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - run: python -m unittest discover -s tests -v
"""

CI_NODE = """name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: node --test
"""

PYPROJECT = """[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "{{NAME}}"
version = "0.1.0"
description = "{{GOAL}}"
requires-python = ">=3.10"
{{SCRIPTS}}
[tool.setuptools.packages.find]
where = ["src"]
"""

QUALITY_PY = '''"""Run this project's KOSIF probes: python -m {{PKG}}.quality < inputs.json

inputs.json maps probe name → keyword arguments, e.g. {"secrets": {"text": "..."}}.
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from typing import Any, Mapping

from .kcl_probes import PROBES, run_probe

MEMBER = "{{MEMBER_ID}}"
OWNED = {{PROBES_PY}}


def run_checks(inputs: Mapping[str, Mapping[str, Any]], probes: list[str] | None = None) -> dict[str, Any]:
    results, failed = {}, []
    for name in probes or OWNED:
        if name not in inputs:
            continue
        r = run_probe(name, inputs[name])
        results[name] = asdict(r)
        if r.ok is False:
            failed.append(name)
    return {"member": MEMBER, "ran": sorted(results), "failed": failed, "ok": not failed, "results": results}


def main() -> int:
    out = run_checks(json.load(sys.stdin))
    print(json.dumps(out, ensure_ascii=False, sort_keys=True, default=str))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
'''

TEST_QUALITY = '''import unittest

from {{PKG}}.kcl_probes import PROBES, run_probe
from {{PKG}}.quality import OWNED, run_checks


class ProbeTests(unittest.TestCase):
    def test_owned_probes_exist(self):
        for name in OWNED:
            self.assertIn(name, PROBES)

    def test_contrast_known_value(self):
        self.assertEqual(run_probe("contrast", {"fg": "#000000", "bg": "#ffffff"}).value, 21.0)

    def test_secret_scanner_flags_token(self):
        fake = "ghp_" + "a" * 36
        self.assertFalse(run_probe("secrets", {"text": "token=" + fake}).ok)

    def test_arith_quarantines_wrong_claim(self):
        self.assertFalse(run_probe("arith", {"expression": "120 - 120*15% - 10", "claimed": 97}).ok)
        self.assertTrue(run_probe("arith", {"expression": "120 - 120*15% - 10", "claimed": 92}).ok)

    def test_run_checks_skips_missing_inputs(self):
        self.assertEqual(run_checks({})["ran"], [])


if __name__ == "__main__":
    unittest.main()
'''

# ───────────────────────────── archetype code ─────────────────────────────
LIB_CORE = '''"""Core of {{NAME}}: a typed, validated record registry.

Records are immutable; every registry mutation returns a new version number so callers can
detect lost updates. Validation runs the owning member's KOSIF probes when inputs are present.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterator, Mapping

from .kcl_probes import PROBES
from .quality import run_checks


class ValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Record:
    key: str
    data: Mapping[str, Any] = field(default_factory=dict)
    checks: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.key or not self.key.strip():
            raise ValidationError("record key must be non-empty")


class Registry:
    def __init__(self) -> None:
        self._items: dict[str, Record] = {}
        self.version = 0

    def add(self, record: Record, *, expected_version: int | None = None) -> int:
        if expected_version is not None and expected_version != self.version:
            raise ValidationError(f"stale write: expected v{expected_version}, registry is v{self.version}")
        unknown = [p for p in record.checks if p not in PROBES]
        if unknown:
            raise ValidationError(f"unknown checks {unknown}")
        report = run_checks(record.checks, list(record.checks))
        if not report["ok"]:
            raise ValidationError(f"quality checks failed: {report['failed']}")
        self._items[record.key] = record
        self.version += 1
        return self.version

    def get(self, key: str) -> Record:
        try:
            return self._items[key]
        except KeyError:
            raise ValidationError(f"unknown key {key!r}") from None

    def query(self, **equals: Any) -> Iterator[Record]:
        for r in self._items.values():
            if all(r.data.get(k) == v for k, v in equals.items()):
                yield r

    def __len__(self) -> int:
        return len(self._items)
'''

LIB_TEST = '''import unittest

from {{PKG}}.core import Record, Registry, ValidationError


class RegistryTests(unittest.TestCase):
    def test_add_get_query(self):
        reg = Registry()
        v = reg.add(Record(key="a", data={"kind": "x"}))
        self.assertEqual(v, 1)
        self.assertEqual(reg.get("a").data["kind"], "x")
        self.assertEqual([r.key for r in reg.query(kind="x")], ["a"])

    def test_stale_write_rejected(self):
        reg = Registry()
        reg.add(Record(key="a"))
        with self.assertRaises(ValidationError):
            reg.add(Record(key="b"), expected_version=0)

    def test_failed_quality_check_blocks_record(self):
        reg = Registry()
        bad = Record(key="k", checks={"secrets": {"text": "pass" + "word = " + repr("hunter22")}})
        with self.assertRaises(ValidationError):
            reg.add(bad)
        self.assertEqual(len(reg), 0)

    def test_empty_key_rejected(self):
        with self.assertRaises(ValidationError):
            Record(key=" ")


if __name__ == "__main__":
    unittest.main()
'''

CLI_MAIN = '''"""{{NAME}} command line: check JSON inputs with the member's probes and write reports.

    python -m {{PKG}} check  [FILE|-]      run probes, exit 1 when any check fails
    python -m {{PKG}} report [FILE|-]      Markdown report of the same checks
    python -m {{PKG}} probes               list available probes
"""
from __future__ import annotations

import argparse
import json
import sys

from .kcl_probes import PROBES
from .quality import MEMBER, OWNED, run_checks


def _read(path: str) -> dict:
    return json.load(sys.stdin if path == "-" else open(path, encoding="utf-8"))


def report_md(result: dict) -> str:
    lines = [f"# Check report — {MEMBER}", "", "| probe | ok | detail |", "|---|---|---|"]
    for name in result["ran"]:
        r = result["results"][name]
        lines.append(f"| {name} | {'✅' if r['ok'] is not False else '❌'} | {r['detail']} |")
    lines += ["", f"Overall: {'PASS' if result['ok'] else 'FAIL'}"]
    return "\\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="{{PKG}}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("check", "report"):
        p = sub.add_parser(c)
        p.add_argument("file", nargs="?", default="-")
    sub.add_parser("probes")
    a = ap.parse_args(argv)
    if a.cmd == "probes":
        print(json.dumps({"owned": OWNED, "all": sorted(PROBES)}, indent=2))
        return 0
    result = run_checks(_read(a.file), list(PROBES))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, default=str) if a.cmd == "check" else report_md(result))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
'''

CLI_DUNDER = "from .cli import main\n\nraise SystemExit(main())\n"

CLI_TEST = '''import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from {{PKG}}.cli import main


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(list(args))
        return code, buf.getvalue()

    def test_check_pass_and_fail(self):
        with tempfile.TemporaryDirectory() as d:
            good = Path(d, "good.json")
            good.write_text(json.dumps({"contrast": {"fg": "#111111", "bg": "#ffffff"}}))
            self.assertEqual(self.run_cli("check", str(good))[0], 0)
            bad = Path(d, "bad.json")
            bad.write_text(json.dumps({"contrast": {"fg": "#999999", "bg": "#ffffff"}}))
            self.assertEqual(self.run_cli("check", str(bad))[0], 1)

    def test_report_is_markdown(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d, "in.json")
            f.write_text(json.dumps({"arith": {"expression": "2+2", "claimed": 4}}))
            code, out = self.run_cli("report", str(f))
            self.assertEqual(code, 0)
            self.assertIn("| arith |", out)

    def test_probes_listing(self):
        code, out = self.run_cli("probes")
        self.assertEqual(code, 0)
        self.assertIn("secrets", json.loads(out)["all"])


if __name__ == "__main__":
    unittest.main()
'''

SERVICE_MAIN = '''"""{{NAME}} JSON HTTP service (standard library only).

    python -m {{PKG}}.service [--port 8080]
GET  /health        → {"ok": true}
GET  /capabilities  → owned probes and all probes
POST /check         → body {"probe": {kwargs}, ...} → probe results (400 on invalid JSON, 413 when > 1 MB)
"""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .kcl_probes import PROBES
from .quality import MEMBER, OWNED, run_checks

MAX_BODY = 1_000_000


class Handler(BaseHTTPRequestHandler):
    server_version = "{{PKG}}/0.1"

    def _send(self, code: int, obj: dict) -> None:
        body = json.dumps(obj, ensure_ascii=False, default=str).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.send_header("x-content-type-options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):  # quiet by default; no request bodies are logged
        pass

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"ok": True, "member": MEMBER})
        if self.path == "/capabilities":
            return self._send(200, {"owned": OWNED, "all": sorted(PROBES)})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/check":
            return self._send(404, {"error": "not found"})
        n = int(self.headers.get("content-length") or 0)
        if n > MAX_BODY:
            return self._send(413, {"error": "body too large"})
        try:
            inputs = json.loads(self.rfile.read(n) or b"{}")
            if not isinstance(inputs, dict):
                raise ValueError("body must be a JSON object")
            result = run_checks(inputs, [p for p in inputs if p in PROBES])
        except (ValueError, TypeError) as e:
            return self._send(400, {"error": str(e)})
        return self._send(200 if result["ok"] else 422, result)


def make_server(port: int = 0) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    srv = make_server(ap.parse_args().port)
    print(f"listening on http://127.0.0.1:{srv.server_address[1]}")
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

SERVICE_TEST = '''import json
import threading
import unittest
import urllib.error
import urllib.request

from {{PKG}}.service import make_server


class ServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = make_server(0)
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def req(self, path, body=None):
        data = None if body is None else json.dumps(body).encode()
        r = urllib.request.Request(self.base + path, data=data, method="POST" if data else "GET")
        try:
            with urllib.request.urlopen(r, timeout=5) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_health(self):
        self.assertEqual(self.req("/health")[0], 200)

    def test_check_ok_and_failing(self):
        self.assertEqual(self.req("/check", {"arith": {"expression": "6*7", "claimed": 42}})[0], 200)
        code, body = self.req("/check", {"contrast": {"fg": "#aaaaaa", "bg": "#ffffff"}})
        self.assertEqual(code, 422)
        self.assertEqual(body["failed"], ["contrast"])

    def test_bad_input_is_400(self):
        self.assertEqual(self.req("/check", [1, 2])[0], 400)

    def test_unknown_path_404(self):
        self.assertEqual(self.req("/nope")[0], 404)


if __name__ == "__main__":
    unittest.main()
'''

PIPE_MAIN = '''"""{{NAME}} data pipeline: CSV → validate → SQLite, idempotent by row hash.

    python -m {{PKG}}.pipeline INPUT.csv DB.sqlite3 [--key col1,col2]
Re-running with the same file inserts nothing new; every run is logged in the `runs` table.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .kcl_probes import run_probe

SCHEMA = """
CREATE TABLE IF NOT EXISTS rows (row_hash TEXT PRIMARY KEY, source TEXT NOT NULL, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS runs (id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL, source TEXT NOT NULL,
  read INTEGER NOT NULL, inserted INTEGER NOT NULL, skipped INTEGER NOT NULL, duplicate_groups INTEGER NOT NULL);
"""


def extract(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return [dict(r) for r in csv.DictReader(f)]


def row_hash(row: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def run(src: Path, db: Path, keys: list[str] | None = None) -> dict[str, int]:
    rows = extract(src)
    dups = run_probe("duplicates", {"records": rows, "keys": keys}).value if keys else []
    con = sqlite3.connect(db)
    try:
        con.executescript(SCHEMA)
        inserted = 0
        with con:
            for r in rows:
                cur = con.execute("INSERT OR IGNORE INTO rows(row_hash, source, data) VALUES (?, ?, ?)",
                                  (row_hash(r), src.name, json.dumps(r, ensure_ascii=False)))
                inserted += cur.rowcount
            stats = {"read": len(rows), "inserted": inserted, "skipped": len(rows) - inserted, "duplicate_groups": len(dups)}
            con.execute("INSERT INTO runs(at, source, read, inserted, skipped, duplicate_groups) VALUES (?,?,?,?,?,?)",
                        (datetime.now(timezone.utc).isoformat(), src.name, *stats.values()))
        return stats
    finally:
        con.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("db", type=Path)
    ap.add_argument("--key", default="")
    a = ap.parse_args()
    print(json.dumps(run(a.src, a.db, [k for k in a.key.split(",") if k] or None)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

PIPE_TEST = '''import sqlite3
import tempfile
import unittest
from pathlib import Path

from {{PKG}}.pipeline import run


class PipelineTests(unittest.TestCase):
    def test_idempotent_and_duplicates_reported(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d, "in.csv")
            src.write_text("invoice,amount\\nA1,100\\nA2,250\\nA1,100\\n", encoding="utf-8")
            db = Path(d, "out.sqlite3")
            first = run(src, db, ["invoice"])
            self.assertEqual(first["read"], 3)
            self.assertEqual(first["inserted"], 2)
            self.assertEqual(first["duplicate_groups"], 1)
            second = run(src, db, ["invoice"])
            self.assertEqual(second["inserted"], 0)
            con = sqlite3.connect(db)
            self.assertEqual(con.execute("select count(*) from runs").fetchone()[0], 2)
            con.close()


if __name__ == "__main__":
    unittest.main()
'''

AGENT_MAIN = '''"""{{NAME}} agent loop: observe → plan → risk gate → act → verify, with hard budgets.

Tools are plain functions registered with @tool. The loop never passes a human checkpoint
(CAPTCHA, OTP, credentials, payment): it stops with status "needs-human". Repeated actions without
state change stop with "no-progress". Success requires the goal predicate to hold on observed state.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .kcl_probes import run_probe

Tool = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]
TOOLS: dict[str, Tool] = {}


def tool(name: str) -> Callable[[Tool], Tool]:
    def deco(fn: Tool) -> Tool:
        TOOLS[name] = fn
        return fn
    return deco


@dataclass
class Budget:
    max_steps: int = 20
    max_no_progress: int = 3
    steps: int = 0


@dataclass
class Step:
    tool: str
    args: dict[str, Any] = field(default_factory=dict)
    description: str = ""


def run(state: dict[str, Any], planner: Callable[[dict[str, Any]], Step | None],
        goal: Callable[[dict[str, Any]], bool], budget: Budget | None = None,
        approved: set[str] | None = None) -> dict[str, Any]:
    budget = budget or Budget()
    approved = approved or set()
    log: list[dict[str, Any]] = []
    while True:
        if goal(state):
            return {"status": "done", "state": state, "log": log}
        if budget.steps >= budget.max_steps:
            return {"status": "budget-exhausted", "state": state, "log": log}
        step = planner(state)
        if step is None:
            return {"status": "no-plan", "state": state, "log": log}
        gate = run_probe("checkpoint", {"text": f"{step.tool} {step.description} {step.args}"})
        hard = {"captcha", "otp-mfa", "credential", "payment"} & set(gate.value)
        if hard:
            return {"status": "needs-human", "checkpoint": sorted(hard), "state": state, "log": log}
        if gate.value and step.tool not in approved:
            return {"status": "needs-approval", "checkpoint": gate.value, "state": state, "log": log}
        before = repr(sorted(state.items()))
        state = TOOLS[step.tool](dict(state), step.args)
        budget.steps += 1
        log.append({"action": step.tool, "target": repr(step.args), "state_hash": hash(repr(sorted(state.items())))})
        loops = run_probe("loop_detect", {"actions": log, "window": budget.max_no_progress})
        if loops.value and repr(sorted(state.items())) == before:
            return {"status": "no-progress", "state": state, "log": log}


@tool("increment")
def _increment(state: dict[str, Any], args: dict[str, Any]) -> dict[str, Any]:
    state["count"] = state.get("count", 0) + int(args.get("by", 1))
    return state


@tool("noop")
def _noop(state: dict[str, Any], args: dict[str, Any]) -> dict[str, Any]:
    return state
'''

AGENT_TEST = '''import unittest

from {{PKG}}.agent import Budget, Step, run


class AgentTests(unittest.TestCase):
    def test_reaches_goal_and_verifies(self):
        out = run({"count": 0}, lambda s: Step("increment", {"by": 1}), lambda s: s["count"] >= 3)
        self.assertEqual(out["status"], "done")
        self.assertEqual(out["state"]["count"], 3)

    def test_stops_on_no_progress(self):
        out = run({}, lambda s: Step("noop"), lambda s: False, Budget(max_steps=10, max_no_progress=3))
        self.assertEqual(out["status"], "no-progress")

    def test_budget_is_hard(self):
        out = run({"count": 0}, lambda s: Step("increment"), lambda s: False, Budget(max_steps=2, max_no_progress=5))
        self.assertEqual(out["status"], "budget-exhausted")

    def test_human_checkpoint_never_passed(self):
        out = run({}, lambda s: Step("noop", description="enter the OTP code"), lambda s: False)
        self.assertEqual(out["status"], "needs-human")

    def test_publish_needs_approval(self):
        out = run({}, lambda s: Step("noop", description="publish the post"), lambda s: False)
        self.assertEqual(out["status"], "needs-approval")


if __name__ == "__main__":
    unittest.main()
'''

WEB_INDEX = """<!doctype html>
<html lang="{{LANG}}" dir="{{DIR}}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{NAME}}</title>
<meta name="description" content="{{GOAL}}">
<link rel="stylesheet" href="tokens.css">
<link rel="stylesheet" href="app.css">
<script src="app.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="bar">
  <strong class="brand">{{NAME}}</strong>
  <button id="theme" type="button" aria-pressed="false">Dark mode</button>
</header>
<main id="main">
  <section class="hero">
    <h1>{{NAME}}</h1>
    <p>{{GOAL}}</p>
    <a class="cta" href="#features">Get started</a>
  </section>
  <section id="features" aria-labelledby="features-title">
    <h2 id="features-title">What it does</h2>
    <ul class="cards">
{{CARDS}}
    </ul>
  </section>
</main>
<footer class="foot"><small>Forged by {{MEMBER}} · KOSIF council</small></footer>
</body>
</html>
"""

WEB_TOKENS = """:root{
  --bg:#f7f7fb;--surface:#ffffff;--ink:#16181d;--ink-2:#4a4f5c;--line:#dfe2ea;
  --brand:#1d4ed8;--on-brand:#ffffff;--focus:#1d4ed8;
  --s-1:4px;--s-2:8px;--s-3:12px;--s-4:16px;--s-5:24px;--s-6:32px;--s-7:48px;
  --r:12px;--fs:16px;--fs-l:20px;--fs-xl:clamp(28px,5vw,44px);
  --font:system-ui,"Segoe UI","IBM Plex Sans Arabic",Tahoma,sans-serif;
  --t:160ms;color-scheme:light;
}
:root[data-theme="dark"]{
  --bg:#0f1115;--surface:#171a21;--ink:#eef0f5;--ink-2:#b4b9c6;--line:#2a2f3a;
  --brand:#8ab4ff;--on-brand:#0b1020;--focus:#8ab4ff;color-scheme:dark;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#0f1115;--surface:#171a21;--ink:#eef0f5;--ink-2:#b4b9c6;--line:#2a2f3a;
    --brand:#8ab4ff;--on-brand:#0b1020;--focus:#8ab4ff;color-scheme:dark;
  }
}
@media (prefers-reduced-motion:reduce){:root{--t:0ms}}
"""

WEB_CSS = """*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:var(--fs)/1.6 var(--font)}
.skip{position:absolute;inset-inline-start:-999px}.skip:focus{inset-inline-start:var(--s-4);top:var(--s-4);background:var(--surface);padding:var(--s-2)}
.bar{display:flex;justify-content:space-between;align-items:center;padding:var(--s-4);border-bottom:1px solid var(--line)}
main{max-width:72rem;margin:0 auto;padding:var(--s-5) var(--s-4)}
.hero h1{font-size:var(--fs-xl);line-height:1.15;margin:0 0 var(--s-3)}
.hero p{color:var(--ink-2);max-width:65ch}
.cta,button{display:inline-flex;align-items:center;min-height:44px;min-width:44px;padding:0 var(--s-4);border-radius:var(--r);
  background:var(--brand);color:var(--on-brand);text-decoration:none;border:0;font:inherit;cursor:pointer;transition:transform var(--t)}
.cta:hover,button:hover{transform:translateY(-1px)}
:focus-visible{outline:3px solid var(--focus);outline-offset:2px}
.cards{list-style:none;padding:0;display:grid;gap:var(--s-4);grid-template-columns:repeat(auto-fit,minmax(16rem,1fr))}
.cards li{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:var(--s-4)}
.foot{padding:var(--s-5) var(--s-4);color:var(--ink-2);text-align:center}
"""

WEB_JS = """(() => {
  "use strict";
  const root = document.documentElement, btn = document.getElementById("theme");
  const apply = (t) => { root.dataset.theme = t; btn.setAttribute("aria-pressed", String(t === "dark")); btn.textContent = t === "dark" ? "Light mode" : "Dark mode"; };
  let saved = null;
  try { saved = localStorage.getItem("theme"); } catch { /* storage may be blocked */ }
  apply(saved || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
  btn.addEventListener("click", () => {
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    apply(next);
    try { localStorage.setItem("theme", next); } catch { /* ignore */ }
  });
})();
"""

WEB_TEST = '''"""Static-site audit: structure, accessibility basics and token contrast in both themes."""
import re
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from kcl_probes import contrast_ratio  # noqa: E402


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.attrs = [], []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs.append((tag, dict(attrs)))


def tokens(block):
    return dict(re.findall(r"--([\\w-]+):\\s*(#[0-9a-fA-F]{3,6})", block))


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.p = Collector()
        cls.p.feed(cls.html)
        css = (ROOT / "tokens.css").read_text(encoding="utf-8")
        cls.light = tokens(css.split(':root[data-theme="dark"]')[0])
        cls.dark = tokens(css.split(':root[data-theme="dark"]')[1].split("}")[0])

    def test_document_basics(self):
        html_attrs = dict(self.p.attrs[0][1]) if self.p.attrs and self.p.attrs[0][0] == "html" else {}
        self.assertIn("lang", html_attrs)
        self.assertTrue(any(t == "meta" and a.get("name") == "viewport" for t, a in self.p.attrs))
        self.assertEqual(self.p.tags.count("h1"), 1)
        self.assertIn("<title>", self.html)

    def test_images_have_alt_and_buttons_have_type(self):
        for t, a in self.p.attrs:
            if t == "img":
                self.assertIn("alt", a)
            if t == "button":
                self.assertIn("type", a)

    def test_contrast_both_themes(self):
        for theme in (self.light, self.dark):
            self.assertGreaterEqual(contrast_ratio(theme["ink"], theme["bg"]), 4.5)
            self.assertGreaterEqual(contrast_ratio(theme["ink-2"], theme["surface"]), 4.5)
            self.assertGreaterEqual(contrast_ratio(theme["on-brand"], theme["brand"]), 4.5)

    def test_reduced_motion_supported(self):
        self.assertIn("prefers-reduced-motion", (ROOT / "tokens.css").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
'''

WORKER_JS = """// {{NAME}} — Cloudflare Worker JSON API. Forged by {{MEMBER}} (KOSIF council).
// GET /health · GET /capabilities · POST /check {"contrast": {"fg": "#111", "bg": "#fff"}}

const hex = (c) => {
  let h = String(c).trim().replace(/^#/, "");
  if (h.length === 3) h = [...h].map((x) => x + x).join("");
  if (!/^[0-9a-f]{6}$/i.test(h)) throw new Error(`unsupported colour ${c}`);
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16) / 255);
};
const lum = (c) => {
  const [r, g, b] = hex(c).map((v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};
export const contrast = (fg, bg) => {
  const [a, b] = [lum(fg), lum(bg)].sort((x, y) => y - x);
  return Math.round(((a + 0.05) / (b + 0.05)) * 100) / 100;
};
const SECRET = /\\bgh[pousr]_[A-Za-z0-9]{36,}\\b|\\bsk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----/;

export const PROBES = {
  contrast: ({ fg, bg, large = false }) => {
    const ratio = contrast(fg, bg);
    return { ok: ratio >= (large ? 3 : 4.5), value: ratio };
  },
  secrets: ({ text }) => ({ ok: !SECRET.test(String(text)), value: SECRET.test(String(text)) ? ["secret-like"] : [] }),
};

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { "content-type": "application/json; charset=utf-8", "x-content-type-options": "nosniff" } });

export default {
  async fetch(request) {
    const { pathname } = new URL(request.url);
    if (request.method === "GET" && pathname === "/health") return json({ ok: true });
    if (request.method === "GET" && pathname === "/capabilities") return json({ probes: Object.keys(PROBES) });
    if (request.method === "POST" && pathname === "/check") {
      const len = Number(request.headers.get("content-length") || 0);
      if (len > 1_000_000) return json({ error: "body too large" }, 413);
      let body;
      try { body = await request.json(); } catch { return json({ error: "invalid JSON" }, 400); }
      if (!body || typeof body !== "object" || Array.isArray(body)) return json({ error: "body must be an object" }, 400);
      const results = {}, failed = [];
      for (const [name, args] of Object.entries(body)) {
        if (!PROBES[name]) continue;
        try { results[name] = PROBES[name](args || {}); } catch (e) { return json({ error: String(e.message || e) }, 400); }
        if (results[name].ok === false) failed.push(name);
      }
      return json({ ok: failed.length === 0, failed, results }, failed.length ? 422 : 200);
    }
    return json({ error: "not found" }, 404);
  },
};
"""

WORKER_TEST = """import { test } from "node:test";
import assert from "node:assert/strict";
import worker, { contrast } from "../src/worker.js";

const call = (method, path, body) =>
  worker.fetch(new Request("https://example.test" + path, { method, body: body === undefined ? undefined : JSON.stringify(body), headers: { "content-type": "application/json" } }));

test("contrast known values", () => {
  assert.equal(contrast("#000000", "#ffffff"), 21);
  assert.equal(contrast("#777777", "#ffffff"), 4.48);
});

test("health and 404", async () => {
  assert.equal((await call("GET", "/health")).status, 200);
  assert.equal((await call("GET", "/nope")).status, 404);
});

test("check passes and fails with the right status", async () => {
  assert.equal((await call("POST", "/check", { contrast: { fg: "#111111", bg: "#ffffff" } })).status, 200);
  const bad = await call("POST", "/check", { secrets: { text: "ghp_" + "a".repeat(36) } });
  assert.equal(bad.status, 422);
  assert.deepEqual((await bad.json()).failed, ["secrets"]);
});

test("invalid body is 400", async () => {
  assert.equal((await call("POST", "/check", [1, 2])).status, 400);
});
"""

WRANGLER = 'name = "{{NAME}}"\nmain = "src/worker.js"\ncompatibility_date = "2026-09-01"\n'
PACKAGE_JSON = '{\n  "name": "{{NAME}}",\n  "version": "0.1.0",\n  "private": true,\n  "type": "module",\n  "scripts": {\n    "test": "node --test",\n    "dev": "wrangler dev",\n    "deploy": "wrangler deploy"\n  }\n}\n'


# ───────────────────────────── generator ─────────────────────────────
def roadmap(member: dict) -> str:
    rows = []
    for i, cap in enumerate(member["code"], 1):
        rows.append(f"{i}. **M{i}: {cap[0].upper() + cap[1:]}** — acceptance: a test proves the behaviour on a typical, "
                    f"an edge and an invalid input; docs updated; CI green.")
    return "\n".join(rows)


def forge(req: dict) -> dict:
    data = _load_council()
    cards = {p["id"]: p for p in data["personas"]}
    member = cards.get(req.get("member", ""))
    if not member:
        raise ValueError(f"unknown member {req.get('member')!r}")
    name = re.sub(r"[^a-z0-9-]+", "-", str(req.get("name") or member["id"] + "-project").lower()).strip("-")
    if not name:
        raise ValueError("project name is empty")
    arch = req.get("archetype") or member["forge"]
    if arch not in ARCHETYPES:
        raise ValueError(f"unknown archetype {arch!r}")
    out = Path(req["out"]).expanduser().resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError(f"output directory {out} is not empty")
    pkg = pkg_name(name)
    goal = str(req.get("goal") or f"{member['specialty'][0].upper() + member['specialty'][1:]} — {ARCHETYPES[arch]}.")
    arabic = bool(re.search(r"[؀-ۿ]", goal))
    ctx = {"NAME": name, "PKG": pkg, "GOAL": goal.replace('"', "'"), "MEMBER": member["name"], "MEMBER_AR": member["name_ar"],
           "MEMBER_ID": member["id"], "SPECIALTY": member["specialty"], "ARCH": arch, "ARCH_DESC": ARCHETYPES[arch],
           "PROBES": ", ".join(member["probes"]), "PROBES_PY": json.dumps(member["probes"]),
           "PROBE_LIST": "\n".join(f"- `{p}`" for p in member["probes"]), "ROADMAP": roadmap(member),
           "MASTERY": "\n".join(f"- {m}" for m in member["mastery"]), "LANG": "ar" if arabic else "en", "DIR": "rtl" if arabic else "ltr"}
    files: dict[str, str] = {}
    py = arch not in {"static-web", "cf-worker"}
    if py:
        base = f"src/{pkg}"
        files[f"{base}/__init__.py"] = f'"""{name} — forged by {member["name"]} (KOSIF council)."""\n__version__ = "0.1.0"\n'
        files[f"{base}/kcl_probes.py"] = (HERE / "kcl_probes.py").read_text(encoding="utf-8")
        files[f"{base}/quality.py"] = QUALITY_PY
        files["tests/__init__.py"] = ""
        files["tests/test_quality.py"] = TEST_QUALITY
        files[".github/workflows/ci.yml"] = CI_PY
        scripts = ""
        if arch == "python-lib":
            files[f"{base}/core.py"], files["tests/test_core.py"] = LIB_CORE, LIB_TEST
            ctx["INTERFACE"] = "importable API: `Registry`, `Record` (`from " + pkg + ".core import Registry`)."
            ctx["RUN"] = "```bash\nPYTHONPATH=src python -m unittest discover -s tests -v\n```"
        elif arch == "python-cli":
            files[f"{base}/cli.py"], files[f"{base}/__main__.py"], files["tests/test_cli.py"] = CLI_MAIN, CLI_DUNDER, CLI_TEST
            scripts = f'[project.scripts]\n{name} = "{pkg}.cli:main"\n'
            ctx["INTERFACE"] = f"CLI `python -m {pkg} check|report|probes`."
            ctx["RUN"] = f"```bash\necho '{{\"contrast\": {{\"fg\": \"#111\", \"bg\": \"#fff\"}}}}' | PYTHONPATH=src python -m {pkg} report -\nPYTHONPATH=src python -m unittest discover -s tests -v\n```"
        elif arch == "python-service":
            files[f"{base}/service.py"], files["tests/test_service.py"] = SERVICE_MAIN, SERVICE_TEST
            ctx["INTERFACE"] = "JSON over HTTP: GET /health, GET /capabilities, POST /check."
            ctx["RUN"] = f"```bash\nPYTHONPATH=src python -m {pkg}.service --port 8080\nPYTHONPATH=src python -m unittest discover -s tests -v\n```"
        elif arch == "data-pipeline":
            files[f"{base}/pipeline.py"], files["tests/test_pipeline.py"] = PIPE_MAIN, PIPE_TEST
            ctx["INTERFACE"] = "batch CLI: CSV in, SQLite out, run log table."
            ctx["RUN"] = f"```bash\nPYTHONPATH=src python -m {pkg}.pipeline data.csv out.sqlite3 --key id\nPYTHONPATH=src python -m unittest discover -s tests -v\n```"
        elif arch == "agent":
            files[f"{base}/agent.py"], files["tests/test_agent.py"] = AGENT_MAIN, AGENT_TEST
            ctx["INTERFACE"] = "Python API `run(state, planner, goal, budget)` with registered tools."
            ctx["RUN"] = "```bash\nPYTHONPATH=src python -m unittest discover -s tests -v\n```"
        ctx["SCRIPTS"] = scripts
        files["pyproject.toml"] = PYPROJECT
    elif arch == "static-web":
        cards_html = "\n".join(f"      <li><h3>{c[0].upper() + c[1:]}</h3></li>" for c in member["mastery"][:6])
        ctx["CARDS"] = cards_html
        files.update({"index.html": WEB_INDEX, "tokens.css": WEB_TOKENS, "app.css": WEB_CSS, "app.js": WEB_JS,
                      "tools/kcl_probes.py": (HERE / "kcl_probes.py").read_text(encoding="utf-8"),
                      "tests/__init__.py": "", "tests/test_site.py": WEB_TEST, ".github/workflows/ci.yml": CI_PY})
        ctx["INTERFACE"] = "static HTML/CSS/JS; open index.html or serve the folder."
        ctx["RUN"] = "```bash\npython -m http.server 8000   # then open http://localhost:8000\npython -m unittest discover -s tests -v\n```"
    else:  # cf-worker
        files.update({"src/worker.js": WORKER_JS, "test/worker.test.mjs": WORKER_TEST, "wrangler.toml": WRANGLER,
                      "package.json": PACKAGE_JSON, ".github/workflows/ci.yml": CI_NODE})
        ctx["INTERFACE"] = "HTTP JSON API on Cloudflare Workers (GET /health, GET /capabilities, POST /check)."
        ctx["RUN"] = "```bash\nnode --test\nnpx wrangler dev      # local\nnpx wrangler deploy   # needs your Cloudflare login\n```"
    files.update({"README.md": README, "docs/ARCHITECTURE.md": ARCH_DOC, "docs/adr/0001-archetype.md": ADR,
                  "SECURITY.md": SECURITY, ".gitignore": GITIGNORE})
    out.mkdir(parents=True, exist_ok=True)
    for rel, text in files.items():
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text if rel.endswith("kcl_probes.py") else render(text, ctx), encoding="utf-8")
    tests = run_tests(out, arch)
    return {"ok": tests["passed"] is True, "member": member["id"], "archetype": arch, "path": str(out),
            "files": sorted(files), "tests": tests, "roadmap_milestones": len(member["code"])}


def run_tests(out: Path, arch: str) -> dict:
    if arch == "cf-worker":
        if not shutil.which("node"):
            return {"passed": None, "detail": "node not installed: tests not run"}
        cmd = ["node", "--test"]
        env = None
    else:
        cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"]
        env = {"PYTHONPATH": str(out / "src"), "PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1"}
    r = subprocess.run(cmd, cwd=out, capture_output=True, text=True, timeout=180, env=env)
    tail = (r.stdout + r.stderr).strip().splitlines()[-3:]
    return {"passed": r.returncode == 0, "command": " ".join(cmd), "detail": " | ".join(tail)}


def main(argv: list[str]) -> int:
    try:
        if len(argv) > 1 and argv[1] == "--list":
            data = _load_council()
            lead = {a: [p["id"] for p in data["personas"] if p["forge"] == a] for a in ARCHETYPES}
            print(json.dumps({"archetypes": ARCHETYPES, "members_by_archetype": lead}, ensure_ascii=False, indent=1))
            return 0
        if len(argv) >= 4:
            req = {"member": argv[1], "name": argv[2], "out": argv[3]}
            if len(argv) > 4:
                req["archetype"] = argv[4]
        else:
            req = json.load(sys.stdin)
        res = forge(req)
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
