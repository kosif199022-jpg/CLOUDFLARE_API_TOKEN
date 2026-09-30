#!/usr/bin/env python3
"""Explicit version negotiation between KOSIF runtime, mobile bridge, ChatGPT plugin,
Pro package and receipt trace. Reads observed versions from stdin JSON, e.g.
{"runtime": "0.8.3", "mobile_bridge": "1.4.0", "chatgpt_plugin": "1.5.3", "trace": "3.0"}
A version that was not observed live must be omitted, never guessed.
Output status: compatible | degraded | incompatible. Exit 0/1/2 respectively (3 = bad input).
"""
import json
import sys
from pathlib import Path

MATRIX = Path(__file__).resolve().parents[1] / "references" / "version-compat.json"


def parse(v):
    parts = str(v).strip().lstrip("v").split(".")
    if not parts or not all(p.isdigit() for p in parts):
        raise ValueError(f"bad version {v!r}")
    return tuple(int(p) for p in parts) + (0,) * (3 - len(parts))


def negotiate(observed, matrix=None):
    m = matrix or json.loads(MATRIX.read_text(encoding="utf-8"))
    rows, status = {}, "compatible"
    for name, rule in m["components"].items():
        if name not in observed or observed[name] in (None, ""):
            st = "degraded" if name in m.get("degraded_if_missing", []) else "compatible"
            rows[name] = {"observed": None, "status": "missing" if st == "degraded" else "optional-missing",
                          "action": f"observe {name} version live before relying on it"}
            if st == "degraded" and status == "compatible":
                status = "degraded"
            continue
        v = parse(observed[name])
        if v < parse(rule["min"]):
            rows[name] = {"observed": observed[name], "status": "incompatible",
                          "action": f"upgrade to >= {rule['min']} ({rule['reason']})"}
            status = "incompatible"
        elif v < parse(rule["recommended"]):
            rows[name] = {"observed": observed[name], "status": "outdated",
                          "action": f"recommended {rule['recommended']}"}
            if status == "compatible":
                status = "degraded"
        else:
            rows[name] = {"observed": observed[name], "status": "ok"}
    unknown = sorted(set(observed) - set(m["components"]))
    return {"status": status, "pro_package": m["pro_package"], "components": rows, "unknown_components": unknown}


def main():
    try:
        out = negotiate(json.load(sys.stdin))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"status": "invalid", "error": str(e)}))
        return 3
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))
    return {"compatible": 0, "degraded": 1, "incompatible": 2}[out["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
