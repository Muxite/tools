from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parents[3];batch=Path(__file__).resolve().parent/'factory-bundle';batch.mkdir(exist_ok=True)
receipts=[]
def save(rel,text):
 p=root/rel
 if p.exists():
  data=p.read_bytes();(batch/(rel.replace('/','__')+'.snapshot')).write_bytes(data);receipts.append({'path':rel,'sha256_before':hashlib.sha256(data).hexdigest()})
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8',newline='\n')
def edit(rel,fn):save(rel,fn((root/rel).read_text(encoding='utf-8-sig')))
prompt='we should make it more clear how CC factory is itself a bunch of CCs, so the line is kinda blurred between the complete lab, its just a matter of bundling imo\n'
rel='Sources/Prompts/2026-10-27-factory-is-cc-bundle.txt';save(rel,prompt)
mf='Sources/capture-manifest.json';rows=json.loads((root/mf).read_text(encoding='utf-8-sig'));rows.append({'path':rel,'sha256':hashlib.sha256(prompt.encode()).hexdigest(),'capture_method':'Exact visible user message, UTF-8 LF; not a transport export','captured_date':'2026-10-27'});save(mf,json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
edit('Sources/Prompt Register.md',lambda s:s+'\n- [[Sources/Prompts/2026-10-27-factory-is-cc-bundle.txt|Factory as a CC bundle]]: the factory composes the same lab capabilities; its boundary is bundling/purpose, not a new execution layer.\n')
explanation='''The CC Factory is itself a composition of CCs, rather than a fundamentally different component type. Research and factory workflows use the same lab library, native JiuwenSwarm orchestration, execution controller, model routes, permissions, budgets and persistent data. An illustrative factory composes ingest/analyze, build/test and packaging CCs. This is not a fixed component count or a demand for separate containers. A versioned bundle can expose one composite CC interface while its members remain reusable independently. Deployment follows actual dependency, isolation and resource needs.

Checking can also use CC implementations. Independence refers to who assigns criteria and admission authority, not a requirement for another service: a producer cannot redefine its own acceptance rules. Factory CC upgrades, including changes to their own bundle, become candidates for future bindings after independent qualification; active work retains pins. Stable recovery and host/provider control stay explicit. The whole lab includes CC compositions plus orchestration, state and infrastructure, so bundling flexibility does not imply that the VM or trusted controller is an ordinary generated capsule.

'''
edit('Designs/Sandbox Lab Design.md',lambda s:s.replace('## CC sources, factory and native JiuwenSwarm integration\n\n','## CC sources, factory and native JiuwenSwarm integration\n\n'+explanation))
edit('Designs/Lab Capsule and Factory Design Plan.md',lambda s:s+'\nThe Factory is a versioned bundle of lab CCs, potentially callable as one composite CC, and shares the research execution/model/state path. Reuse existing CCs for ingestion, building/testing and packaging; avoid a separate generic factory runtime. Qualification authority stays independently assigned even when its checks are CCs. Bundle members remain reusable and updates affect future bindings after qualification.\n')
edit('Sources/Implementation Intent.md',lambda s:s+'\n## October 27 factory composition\n\nThe Factory is itself a bundle of CCs using the same machinery as research workflows. Treat its box as a grouping by purpose/interface, not another service class. Composite bundles can be reused as CCs while retaining constituent reuse. Independent acceptance authority and stable recovery remain explicit. Slides 2, 3 and 5 now show this, without adding slides.\n')
pres='Designs/Sandbox Briefing/presentation/'
edit(pres+'README.md',lambda s:s.replace('Design rev5','Design rev6').replace('Design%20rev5','Design%20rev6').replace('review-rev5/','review-rev6/').replace('`review-rev5/`','`review-rev6/`').replace('CC sources, factory and local reuse','CC sources, factory bundle and local reuse').replace('## Native integration and evidence','The Factory is explicitly a bundle of lab CCs, not a new execution layer. The factory view expands illustrative ingestion, build/test and packaging CCs and shows their shared lab execution/model routing. Research and factory workflows use the same CC machinery. A bundle can expose a composite CC interface while its parts remain reusable. Checkers can be CCs; independent criteria and admission authority still apply.\n\n## Native integration and evidence').replace('`cc_factory_native.mjs` contains','`factory_bundle.mjs` updates the current fifteen-slide deck with the explicit Factory composition; `export_bundle.mjs` exports the reviewed state. `cc_factory_native.mjs` contains').replace('`export_native.mjs` exports','The earlier `export_native.mjs` exports'))
renders=Path('C:/Users/m50066326/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Roaming/Codex/web/Codex/artifact-sessions/exports/latest/e91be6b1fafe6d85492b7271ed7d3473f685aa0efa44c444b2b4a3768bc2c6e9');dest=root/pres/'review-rev6';dest.mkdir(exist_ok=True)
for i in range(1,16):
 for ext in ['png','layout.json']:shutil.copy2(renders/f'slide-{i}.{ext}',dest/f'slide-{i}.{ext}')
(batch/'receipt.json').write_text(json.dumps({'notes':receipts,'deck_slides':15,'scope':'design clarification, no runtime implementation'},indent=2)+'\n',encoding='utf-8')
print('Saved Factory composition clarification and updated presentation route.')
