#!/usr/bin/env python3
"""Capability Truth Registry for KOSIF Think Pro 4.
A capability name is never evidence that the capability works.
"""
from __future__ import annotations
from typing import Any, Mapping

ALLOWED = {"verified","measured","implemented","host-dependent","prompt-only","simulated","historical","unavailable"}


def assess_capability(record: Mapping[str, Any]) -> dict[str, Any]:
    impl = str(record.get("implementation") or "prompt-only").strip().lower()
    if impl not in ALLOWED:
        impl = "prompt-only"
    evidence = list(record.get("evidence") or [])
    deterministic = any(e.get("type") == "deterministic-test" and e.get("passed") is True for e in evidence if isinstance(e, Mapping))
    measured = any(e.get("type") in {"measurement","benchmark"} and e.get("passed", True) is True for e in evidence if isinstance(e, Mapping))
    observed_receipt = any(e.get("type") in {"executor-receipt","artifact-receipt"} and e.get("observed") is True for e in evidence if isinstance(e, Mapping))
    host_observed = any(e.get("type") == "host-exposure" and e.get("observed") is True for e in evidence if isinstance(e, Mapping))

    status = impl
    verified = False
    if impl == "host-dependent":
        if host_observed and (deterministic or observed_receipt or measured):
            status, verified = "verified", True
    elif impl in {"implemented","measured"}:
        if deterministic and (observed_receipt or measured):
            status, verified = "verified", True
        elif measured:
            status = "measured"
    elif impl == "verified":
        # Imported claims cannot self-assert verified without fresh supporting evidence.
        if deterministic and (observed_receipt or measured):
            verified = True
        else:
            status = "implemented"
    return {
        "name": record.get("name"),
        "status": status,
        "verified": verified,
        "evidence_count": len(evidence),
        "limitations": list(record.get("limitations") or []),
        "rule": "claim-name != capability; server availability != host exposure; confidence != evidence",
    }
