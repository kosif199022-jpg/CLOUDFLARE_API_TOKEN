#!/usr/bin/env python3
from pathlib import Path
import importlib.util, json, tempfile
HERE=Path(__file__).resolve().parent
REF=HERE.parent/"references"

def load(name):
    p=HERE/f"{name}.py"
    spec=importlib.util.spec_from_file_location(name,p)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def run():
    tests=[]
    def check(name,cond): tests.append((name,bool(cond)))
    truth=load("capability_truth")
    atlas=load("source_atlas")
    adapter=load("platform_adapter")
    ident=load("identity_reference")
    qa=load("artifact_qa")

    check("truth-prompt-only-not-verified", truth.assess_capability({"name":"demo","implementation":"prompt-only","evidence":[]})["verified"] is False)
    check("truth-host-needs-observed-exposure", truth.assess_capability({"name":"host","implementation":"host-dependent","evidence":[{"type":"deterministic-test","passed":True}]})["verified"] is False)
    check("truth-measured-can-verify", truth.assess_capability({"name":"m","implementation":"measured","evidence":[{"type":"deterministic-test","passed":True},{"type":"measurement","passed":True}]})["verified"] is True)

    result=atlas.build_atlas([
      {"name":"a","text":"same source text","sha256":"x","kind":"knowledge"},
      {"name":"b","text":"same source text","sha256":"x","kind":"knowledge"},
      {"name":"empty","text":"","sha256":"e","kind":"knowledge"},
      {"name":"restricted","text":"internal record","sha256":"p","kind":"restricted"}],as_of="2026-10-01")
    check("atlas-exact-dedup", result["exact_duplicate_groups"]==[["a","b"]])
    check("atlas-empty-quarantined", result["quarantined"]["empty"]==["empty"])
    check("atlas-restricted-quarantined", result["quarantined"]["restricted"]==["restricted"])

    old=adapter.resolve_adapter("legacy-midjourney-v5",as_of="2026-10-01",provider_verified=False)
    check("adapter-stale-not-current", old["freshness"]=="stale" and old["current_syntax_verified"] is False)

    ref=ident.build_reference_set({"character_id":"c1","immutable":{"eyes":"brown"},"views":{"front":"f","left":"l","right":"r","back":"b","three_quarter":"q"}})
    check("identity-360-ready", ref["ready"] is True and not ref["missing_views"])
    check("identity-drift-blocks", ident.verify_identity(ref,{"character_id":"c1","traits":{"eyes":"blue"},"views_seen":["front","left","right","back","three_quarter"]})["verdict"]=="BLOCK")

    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"x.json"; p.write_text('{"ok":true}',encoding="utf-8")
        q=Path(d)/"bad.json"; q.write_text('{',encoding="utf-8")
        check("artifact-json-pass", qa.verify_artifact(p)["verdict"]=="PASS")
        check("artifact-bad-json-block", qa.verify_artifact(q)["verdict"]=="BLOCK")

    council=json.loads((REF/"council-100.json").read_text(encoding="utf-8"))
    check("council-100-preserved", council.get("size")==100 and council.get("capabilities_total")==2000 and len(council.get("personas") or [])==100)
    import kcl_probes as kcl
    check("kcl-36-probes-preserved", len(kcl.PROBES)==36)

    for f in ("capability-truth-registry.md","source-atlas-v4.md","artifact-qa-v4.md","identity-reference-set-v4.md","platform-adapters-v4.json"):
        check("reference-"+f,(REF/f).exists())

    failed=[n for n,ok in tests if not ok]
    print(json.dumps({"ok":not failed,"passed":sum(ok for _,ok in tests),"total":len(tests),"failed":failed,"version":"4.0.0"},sort_keys=True))
    return 0 if not failed else 1

if __name__=="__main__":
    raise SystemExit(run())
