#!/usr/bin/env python3
import importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def load(path,name):
    p=ROOT/path
    spec=importlib.util.spec_from_file_location(name,p)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def run():
    tests=[]
    def check(n,c): tests.append((n,bool(c)))

    # v4 truth/freshness Prompt Forge stays additive to rich 3.4 Prompt Forge.
    pf=load(Path('kosif-prompt-master/scripts/prompt_forge_v4_truth.py'),'pf4')
    out=pf.forge({"mode":"video","subject":"a fisherman","camera_move":"slow dolly","duration":"8 seconds",
                  "dialogue":"hello","audio":"waves","lighting":"window key from left, 4300K",
                  "lens":"50mm f/2.8","style":"cinematic","aspect":"16:9","platforms":["veo","runway"]})
    check('truth-prompt-three-variations',set(out['variations'])=={'subtle','dramatic','technical'})
    check('truth-prompt-rubric-100',sum(out['quality_rubric'].values())==100)
    check('truth-veo-audio','Audio:' in out['prompts']['veo']['prompt'] and '(no subtitles)' in out['prompts']['veo']['prompt'])
    check('truth-runway-no-negative',out['prompts']['runway']['negative_prompt'] is None)
    check('truth-adapter-attached',all('adapter' in x for x in out['prompts'].values()))

    # Rich 3.4 experts must remain executable, not just present.
    wa=load(Path('kosif-web-design/scripts/web_audit.py'),'wa34')
    w=wa.audit('<button></button><img src="x">')
    check('rich-web-audit-runs',w['verdict'] in {'REVISE','BLOCK'} and len(w['issues'])>=2)
    check('rich-web-audit-structured',all(k in w for k in ('score','by_category','contrast_pairs')))

    gh=load(Path('kosif-github/scripts/gh_preflight.py'),'gh34')
    g=gh.run({"operation":"git push origin main","branch":"main","default_branch":"main","approved":False})
    check('rich-github-blocks-default-push',g['verdict']=='BLOCK')
    gr=gh.run({"operation":"git status","branch":"feature/x","designated_branch":"feature/x"})
    check('rich-github-read-safe',gr['verdict']=='PASS')

    ag=load(Path('kosif-computer-use/scripts/action_gate.py'),'ag34')
    a=ag.run({"steps":[{"id":"s1","action":"observe","target":"page"}]})
    check('rich-computer-observe-runs',a['verdict']=='RUN')
    ah=ag.run({"steps":[{"id":"s1","action":"click","target":"CAPTCHA verification","expect":"user takes over"}]})
    check('rich-computer-human-checkpoint',ah['verdict']=='HANDOFF')

    jp=load(Path('kosif-jev/scripts/jev_packet.py'),'jp34')
    j=jp.build({"mode":"choice","question":"Which option best fits the supplied evidence?",
                "options":{"A":"one","B":"two","unclear":"insufficient evidence"},
                "evidence":{"contact":"a@b.co","fact":"x"}})
    check('rich-jev-packet-runs',j['verdict'] in {'OK','REVISE'} and j['tool']=='jev_choice')
    blob=json.dumps(j,ensure_ascii=False)
    check('rich-jev-redacts-pii','a@b.co' not in blob)

    failed=[n for n,c in tests if not c]
    print(json.dumps({'ok':not failed,'passed':sum(c for _,c in tests),'total':len(tests),'failed':failed,'version':'4.0.1-merge'},sort_keys=True))
    return 0 if not failed else 1
if __name__=='__main__': raise SystemExit(run())
