#!/usr/bin/env python3
"""Project Forge 4: architecture plan with test/security/acceptance receipts."""
from __future__ import annotations
ARCHETYPES=("cli","library","api","web","data","automation","analysis")

def forge_plan(archetype: str, spec: dict) -> dict:
    if archetype not in ARCHETYPES: raise ValueError(f"archetype must be one of {ARCHETYPES}")
    name=spec.get("name") or "project"; lang=spec.get("language") or ("typescript" if archetype=="web" else "python")
    foundations={
      "cli":["src/","tests/","README.md","pyproject.toml"],"library":["src/","tests/","README.md","pyproject.toml"],
      "api":["src/api/","tests/","README.md","pyproject.toml","Dockerfile"],"web":["src/","tests/","package.json","README.md"],
      "data":["src/etl/","tests/","schemas/","README.md"],"automation":["src/workflows/","tests/","README.md"],
      "analysis":["src/","tests/","fixtures/","README.md"]}
    return {"name":name,"archetype":archetype,"language":lang,"supported_archetypes":list(ARCHETYPES),"foundation":foundations[archetype],
      "tests":{"required":["main path","edge case","failure/rollback","capability truth"],"rule":"unexecuted tests are not passed tests"},
      "security":{"required":["secret scan","input boundary validation","least privilege","dependency review"]},
      "acceptance":{"required":["observable postcondition","artifact QA","delivery receipt"],"status":"planned-not-executed"},
      "receipt_schema":{"request_id":"required","tests_run":"list","security_scan":"result","artifact_refs":"list","postcondition":"observed"}}
