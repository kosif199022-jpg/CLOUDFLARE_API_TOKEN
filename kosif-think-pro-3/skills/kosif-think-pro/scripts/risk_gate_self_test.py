#!/usr/bin/env python3
import json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from risk_gate import evaluate

def run():
    tests=[]
    def check(n,c): tests.append((n,bool(c)))

    check("tool-same-pass", evaluate({
        "gate":"tool-swap","intended_tool":"github","proposed_tool":"github",
        "same_semantics":True,"fresh_schema_verified":True
    })["verdict"]=="PASS")

    check("tool-material-swap-block", evaluate({
        "gate":"tool-swap","intended_tool":"image_gen","proposed_tool":"browser",
        "same_semantics":False,"fresh_schema_verified":False
    })["verdict"]=="BLOCK")

    check("tool-compatible-swap-needs-approval", evaluate({
        "gate":"tool-swap","intended_tool":"github","proposed_tool":"git-cli",
        "same_semantics":True,"fresh_schema_verified":True,"explicit_approval":False
    })["verdict"]=="VERIFY")

    check("read-only-action-pass", evaluate({
        "gate":"action","action":"inspect status","side_effect":"none"
    })["verdict"]=="PASS")

    check("write-needs-fresh-target", evaluate({
        "gate":"action","action":"send message","side_effect":"external-write",
        "fresh_target_verified":False,"explicit_approval":True
    })["verdict"]=="VERIFY")

    check("irreversible-needs-approval", evaluate({
        "gate":"action","action":"delete production database","side_effect":"irreversible",
        "fresh_target_verified":True,"explicit_approval":False
    })["verdict"]=="BLOCK")

    check("human-checkpoint-block", evaluate({
        "gate":"action","action":"enter OTP","side_effect":"external-write",
        "fresh_target_verified":True,"explicit_approval":True
    })["verdict"]=="BLOCK")

    check("secret-egress-block", evaluate({
        "gate":"data","data_class":"secret","destination":"external",
        "minimum_necessary":True,"explicit_approval":True
    })["verdict"]=="BLOCK")

    check("private-egress-needs-approval", evaluate({
        "gate":"data","data_class":"private","destination":"external",
        "minimum_necessary":True,"explicit_approval":False
    })["verdict"]=="VERIFY")

    check("private-internal-minimal-pass", evaluate({
        "gate":"data","data_class":"private","destination":"internal",
        "minimum_necessary":True,"explicit_approval":False
    })["verdict"]=="PASS")

    check("excess-data-block", evaluate({
        "gate":"data","data_class":"private","destination":"internal",
        "minimum_necessary":False
    })["verdict"]=="BLOCK")

    check("unknown-gate-block", evaluate({"gate":"mystery"})["verdict"]=="BLOCK")

    failed=[n for n,c in tests if not c]
    print(json.dumps({"ok":not failed,"passed":sum(c for _,c in tests),"total":len(tests),"failed":failed},sort_keys=True))
    return 0 if not failed else 1
if __name__=="__main__": raise SystemExit(run())
