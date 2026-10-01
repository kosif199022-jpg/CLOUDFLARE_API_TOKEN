from pathlib import Path
import importlib.util,sys,json
ROOT=Path(__file__).resolve().parents[3]
def load(path,name):
 p=ROOT/path;spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def run():
 t=[]
 def c(n,v):t.append((n,bool(v)))
 atlas=load(Path('skills/kosif-think-pro/scripts/source_atlas.py'),'atlas')
 a=atlas.build_atlas([
  {'name':'A','text':'same text','modified':'2026-09-30','kind':'knowledge'},
  {'name':'B','text':'same text','modified':'2026-09-30','kind':'knowledge'},
  {'name':'P','text':'private','modified':'2026-09-30','kind':'operational-private'},
 ],as_of='2026-10-01')
 rec={x['name']:x for x in a['records']}
 c('atlas-computes-hash',bool(rec['A'].get('sha256')))
 weights=[rec['A'].get('retrieval_weight'),rec['B'].get('retrieval_weight')]
 c('atlas-collapses-exact-retrieval-weight',all(isinstance(x,(int,float)) for x in weights) and sorted(weights)==[0,1])
 c('atlas-private-weight-zero',rec['P'].get('retrieval_weight')==0)
 c('atlas-has-freshness',rec['A'].get('freshness') in {'fresh','stale','unknown'})

 pa=load(Path('skills/kosif-think-pro/scripts/platform_adapter.py'),'pa')
 for p in ['chatgpt','flux','sdxl','ideogram','sora','nanobanana']:
  r=pa.resolve_adapter(p,as_of='2026-10-01')
  c('adapter-'+p,r['platform']==p and r.get('known') is True)

 ident=load(Path('skills/kosif-think-pro/scripts/identity_reference.py'),'ident')
 ref=ident.build_reference_set({'character_id':'C','immutable':{'eyes':'brown','hair':'black'},'views':{'front':'f','left':'l','right':'r','back':'b','three_quarter':'q'}})
 one=ident.verify_identity(ref,{'character_id':'C','traits':{'eyes':'brown'},'views_seen':['front'],'observation_source':'host-vision'})
 c('identity-single-view-can-pass',one['verdict']=='PASS')
 c('identity-unobserved-traits-reported-not-blocked','hair' in one.get('unobserved_traits',[]))
 drift=ident.verify_identity(ref,{'character_id':'C','traits':{'eyes':'blue'},'views_seen':['front'],'observation_source':'host-vision'})
 c('identity-real-drift-blocks',drift['verdict']=='BLOCK')

 pf=load(Path('skills/kosif-prompt-master/scripts/prompt_forge_v4_truth.py'),'pf')
 o=pf.forge({'mode':'image','subject':'portrait','platforms':['chatgpt','flux','sdxl','ideogram','midjourney'],'as_of':'2026-10-01'})
 c('forge-correct-adapter-chatgpt',o['prompts']['chatgpt']['adapter']['platform']=='chatgpt')
 c('forge-correct-adapter-flux',o['prompts']['flux']['adapter']['platform']=='flux')
 c('forge-does-not-claim-unverified-current-midjourney',o['prompts']['midjourney']['adapter']['current_syntax_verified'] is False)
 c('forge-gates-version-specific-syntax','--v 7' not in o['prompts']['midjourney']['prompt'])
 c('forge-preserves-source-syntax-separately','source_syntax_prompt' in o['prompts']['midjourney'])
 secret=load(Path('skills/kosif-think-pro/scripts/secret_sanitize.py'),'secret')
 sr=secret.scan_text('api_key=\"abcdefghijklmnopqrstuvwxyz123456\"')
 c('secret-gate-detects',sr['blocked'] and len(sr['findings'])>=1)
 c('secret-gate-redacts','abcdefghijklmnopqrstuvwxyz' not in secret.redact_text('api_key=\"abcdefghijklmnopqrstuvwxyz123456\"'))
 failed=[n for n,v in t if not v]
 print(json.dumps({'ok':not failed,'passed':sum(v for _,v in t),'total':len(t),'failed':failed},sort_keys=True))
 return 0 if not failed else 1
if __name__=='__main__':raise SystemExit(run())
