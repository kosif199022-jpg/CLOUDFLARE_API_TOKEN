#!/usr/bin/env python3
import json, sys, tempfile, zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from capability_truth import assess_capability
from source_atlas import build_atlas
from platform_adapter import resolve_adapter
from artifact_qa import verify_artifact
from identity_reference import build_reference_set, verify_identity
from council100 import build_council, select_members
from project_forge import forge_plan


def run():
    tests=[]
    def check(name, cond): tests.append((name,bool(cond)))

    c=assess_capability({"name":"voice-gen","implementation":"simulated","evidence":[]})
    check("truth-simulated-not-verified", c["status"]=="simulated" and not c["verified"])
    c2=assess_capability({"name":"arith","implementation":"implemented","evidence":[{"type":"deterministic-test","passed":True},{"type":"executor-receipt","observed":True}]})
    check("truth-promotes-with-evidence", c2["status"]=="verified" and c2["verified"])
    c3=assess_capability({"name":"browser","implementation":"host-dependent","evidence":[{"type":"server-advertised","passed":True}]})
    check("truth-host-server-not-enough", c3["status"]=="host-dependent" and not c3["verified"])

    atlas=build_atlas([
        {"name":"A.txt","sha256":"aaa","text":"alpha beta gamma delta","modified":"2026-09-30","kind":"knowledge"},
        {"name":"A-copy.txt","sha256":"aaa","text":"alpha beta gamma delta","modified":"2026-09-30","kind":"knowledge"},
        {"name":"near.txt","sha256":"bbb","text":"alpha beta gamma delta epsilon","modified":"2026-09-30","kind":"knowledge"},
        {"name":"empty.txt","sha256":"ccc","text":"","modified":"2026-09-30","kind":"knowledge"},
        {"name":"ops.pdf","sha256":"ddd","text":"private trial balance", "modified":"2026-09-30","kind":"operational-private"},
    ], as_of="2026-10-01")
    check("atlas-exact-dedup", atlas["exact_duplicate_groups"]==[["A-copy.txt","A.txt"]])
    check("atlas-near-dedup", any(set(g)=={"A.txt","A-copy.txt","near.txt"} for g in atlas["near_duplicate_groups"]))
    check("atlas-empty-quarantine", "empty.txt" in atlas["quarantined"]["empty"])
    check("atlas-private-not-knowledge", "ops.pdf" in atlas["quarantined"]["operational_private"])

    mj=resolve_adapter("midjourney", as_of="2026-10-01")
    check("adapter-has-version-and-source", bool(mj["version"]) and bool(mj["source"]))
    old=resolve_adapter("legacy-midjourney-v5", as_of="2026-10-01")
    check("adapter-stale-blocks-current-claim", old["freshness"]=="stale" and not old["current_syntax_verified"])

    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        (td/"ok.json").write_text('{"x":1}',encoding="utf-8")
        check("artifact-json-pass", verify_artifact(td/"ok.json")["verdict"]=="PASS")
        (td/"bad.json").write_text('{x:}',encoding="utf-8")
        check("artifact-json-block", verify_artifact(td/"bad.json")["verdict"]=="BLOCK")
        docx=td/"a.docx"
        with zipfile.ZipFile(docx,'w') as z:
            z.writestr('[Content_Types].xml','x'); z.writestr('word/document.xml','<w:document/>')
        check("artifact-docx-structure", verify_artifact(docx)["verdict"]=="PASS")
        fake=td/"fake.pdf"; fake.write_bytes(b'notpdf')
        check("artifact-pdf-header", verify_artifact(fake)["verdict"]=="BLOCK")

    ref=build_reference_set({"character_id":"CHR-001","immutable":{"hair":"black","eyes":"brown"},"views":{"front":"f","left":"l","right":"r","back":"b","three_quarter":"q"}})
    check("identity-reference-complete", ref["ready"] and len(ref["required_views_present"])==5)
    obs={"request_id":"r1","character_id":"CHR-001","traits":{"hair":"black","eyes":"brown"},"views_seen":["front","left","right","back","three_quarter"]}
    check("identity-verifies-observed", verify_identity(ref,obs)["verdict"]=="PASS")
    obs2=dict(obs); obs2["traits"]={"hair":"blonde","eyes":"brown"}
    check("identity-drift-detected", verify_identity(ref,obs2)["verdict"]=="BLOCK")

    council=build_council()
    check("council-100", len(council["members"])==100 and council["capabilities_total"]==2000)
    check("council-unique-capabilities", council["capabilities_unique"]==2000)
    sel=select_members("review a risky GitHub deployment with secrets and rollback",mode="pro")
    check("council-adaptive-routing", "evidence" in sel["chambers"] and "risk" in sel["chambers"] and "engineering" in sel["chambers"])
    check("council-one-provenance-rule", sel["independence_note"].startswith("Council personas sharing one model/source"))

    fp=forge_plan("api",{"name":"demo","language":"python"})
    check("forge-seven-archetypes", len(fp["supported_archetypes"])==7)
    check("forge-has-tests-security-receipt", all(k in fp for k in ("tests","security","acceptance","receipt_schema")))

    failed=[n for n,ok in tests if not ok]
    out={"ok":not failed,"passed":sum(ok for _,ok in tests),"total":len(tests),"failed":failed,"version":"4.0.0"}
    print(json.dumps(out,ensure_ascii=False,sort_keys=True))
    return 0 if not failed else 1

if __name__=='__main__':
    raise SystemExit(run())
