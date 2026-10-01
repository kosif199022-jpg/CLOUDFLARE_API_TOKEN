#!/usr/bin/env python3
import json
from pathlib import Path
HERE=Path(__file__).resolve();ROOT=HERE.parents[3]
def run():
 t=[]
 def c(n,v):t.append((n,bool(v)))
 manifest=json.loads((ROOT/'plugin.json').read_text(encoding='utf-8'));codex=json.loads((ROOT/'.codex-plugin/plugin.json').read_text(encoding='utf-8'))
 c('manifest-401',manifest.get('version')=='4.0.1' and codex.get('version')=='4.0.1')
 prompts=manifest['extensions']['com.openai']['interface']['defaultPrompt']
 c('prompt-says-pro4',prompts[0].startswith('KOSIF Think Pro 4'))
 c('prompt-no-stale-pro3',not any('KOSIF Think Pro 3 is the mandatory' in x for x in prompts))
 c('prompt-preserves-binding',any('fresh request_id' in x for x in prompts))
 c('prompt-adds-truth',any('Capability Truth Registry' in x for x in prompts))
 c('prompt-adds-reconciliation',any('reconciliation-4.0.1.md' in x for x in prompts))
 for ref in ['reconciliation-4.0.1.md','source-atlas-v4.md','identity-reference-set-v4.md','platform-adapters-v4.json','version-compat.json','v4-source-atlas.seed.json','v4-capability-registry.seed.json','overlay-preservation.json']:
  c('ref-'+ref,(ROOT/'skills/kosif-think-pro/references'/ref).exists())
 for script in ['source_atlas.py','platform_adapter.py','identity_reference.py','secret_sanitize.py','reconcile_401_self_test.py']:
  c('script-'+script,(ROOT/'skills/kosif-think-pro/scripts'/script).exists())
 c('prompt-forge-patched',(ROOT/'skills/kosif-prompt-master/scripts/prompt_forge.py').exists())
 preservation=json.loads((ROOT/'skills/kosif-think-pro/references/overlay-preservation.json').read_text(encoding='utf-8'))
 c('preservation-source-release',preservation.get('source_version')=='4.0.0' and preservation.get('target_version')=='4.0.1')
 failed=[n for n,v in t if not v];print(json.dumps({'ok':not failed,'passed':sum(v for _,v in t),'total':len(t),'failed':failed,'version':'4.0.1'},ensure_ascii=False,sort_keys=True));return 0 if not failed else 1
if __name__=='__main__':raise SystemExit(run())
