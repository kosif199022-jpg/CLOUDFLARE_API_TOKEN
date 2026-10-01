#!/usr/bin/env python3
import importlib.util, json, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def load(path,name):
    p=ROOT/path
    spec=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def run():
    tests=[]
    def check(n,c): tests.append((n,bool(c)))
    pf=load(Path('kosif-prompt-master/scripts/prompt_forge.py'),'pf')
    out=pf.forge({"mode":"video","subject":"a fisherman","camera_move":"slow dolly","duration":"8 seconds","dialogue":"hello","audio":"waves","lighting":"window key from left, 4300K","lens":"50mm f/2.8","style":"cinematic","aspect":"16:9","platforms":["veo","runway"]})
    check('prompt-three-variations',set(out['variations'])=={'subtle','dramatic','technical'})
    check('prompt-rubric-100',sum(out['quality_rubric'].values())==100)
    check('veo-audio', 'Audio:' in out['prompts']['veo']['prompt'] and '(no subtitles)' in out['prompts']['veo']['prompt'])
    check('runway-no-negative',out['prompts']['runway']['negative_prompt'] is None)
    check('adapter-truth-attached',all('adapter' in x for x in out['prompts'].values()))
    bad=pf.forge({"subject":"a photo of a boy","lighting":"nice","style":"8K masterpiece","aspect":"1:1","lens":"35mm","platforms":["flux"]})
    check('iron-rules',sum('iron rule' in x for x in bad['warnings'])>=3)

    wa=load(Path('kosif-web-design/scripts/web_audit.py'),'wa')
    w=wa.audit('<button></button><img src="x">',{"direction":"rtl","language":"ar"})
    check('web-a11y-detects',w['verdict']=='REVISE' and len(w['issues'])>=2)

    gh=load(Path('kosif-github/scripts/gh_preflight.py'),'gh')
    g=gh.preflight({"operation":"push","branch":"main","files":{"a.txt":"token='abc12345678901234567890'"},"tests_passed":False})
    check('github-blocks-secret-and-tests',g['verdict']=='BLOCK')
    r=gh.preflight({"operation":"read","branch":"main","files":{},"tests_passed":False})
    check('github-read-safe',r['verdict']=='PASS')

    ag=load(Path('kosif-computer-use/scripts/action_gate.py'),'ag')
    check('computer-captcha-block',ag.classify({'action':'solve captcha'})['verdict']=='BLOCK')
    check('computer-read-allow',ag.classify({'action':'inspect page'})['verdict']=='PASS')

    jp=load(Path('kosif-jev/scripts/jev_packet.py'),'jp')
    p=jp.build({'mode':'choice','question':'A or B?','options':{'A':'one','B':'two'},'evidence':{'email':'a@b.co'}})
    check('jev-redacts-email',p['packet']['evidence']['email']=='[REDACTED_EMAIL]')
    check('jev-never-authority',p['packet']['authority']=='review-only')

    failed=[n for n,c in tests if not c]
    print(json.dumps({'ok':not failed,'passed':sum(c for _,c in tests),'total':len(tests),'failed':failed,'version':'4.0.0'},sort_keys=True))
    return 0 if not failed else 1
if __name__=='__main__': raise SystemExit(run())
