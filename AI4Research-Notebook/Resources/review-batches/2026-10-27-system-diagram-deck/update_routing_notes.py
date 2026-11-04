from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parents[3]
batch=Path(__file__).resolve().parent/'model-routing';batch.mkdir(exist_ok=True)
receipt=[]
def save(rel,text):
 p=root/rel
 if p.exists():
  data=p.read_bytes();backup=batch/(rel.replace('/','__')+'.snapshot');backup.write_bytes(data);receipt.append({'path':rel,'sha256_before':hashlib.sha256(data).hexdigest()})
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8',newline='\n')
def edit(rel,fn):save(rel,fn((root/rel).read_text(encoding='utf-8-sig')))
prompt='containerized CC should also be able to call the shared inference APIs, or perhaps we have model routing drawn somewhere so that the system can fill it in with avaialbe models and its easier to manage. this will allow CC authors to write more freely so CC authors for internal code dont need to wrry about where the api goes, cuz things can change.\n'
rel='Sources/Prompts/2026-10-27-cc-model-routing.txt';save(rel,prompt)
mf='Sources/capture-manifest.json';rows=json.loads((root/mf).read_text(encoding='utf-8-sig'));rows.append({'path':rel,'sha256':hashlib.sha256(prompt.encode()).hexdigest(),'capture_method':'Exact visible user message captured as UTF-8 LF; not a transport export','captured_date':'2026-10-27'});save(mf,json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
edit('Sources/Prompt Register.md',lambda s:s+'\n- [[Sources/Prompts/2026-10-27-cc-model-routing.txt|CC model routing]]: AI4R and container CCs use lab-supplied model routes so authors avoid fixed provider endpoints.\n')
text='''
### Model access contract for containerized CCs

Both AI4R and CC containers use a stable lab-scoped model interface. CC authors declare a logical role/model alias and feature requirements (tool calling, modality, structured output, context capacity), optionally an exact model/version. Lab configuration maps those requirements to compatible available endpoints. At launch the runtime injects the reachable client/base URL and scoped access configuration. Container localhost refers to the container, so the injected route must actually reach the guest-side service or authorized remote gateway. Provider secrets stay outside CC images.

Resolve and record the actual model identity/version, route configuration and inference settings per invocation. Moving the same endpoint/model should not require rebuilding a CC. Changing model identity is an explicit new binding under compatible policy; exact-model experiments cannot silently substitute another model. Missing compatible routes produce visible wait/failure. Availability alone does not establish feature compatibility. Models private to one lab are visible only in that lab's routing configuration and remain inaccessible to other labs.

This logical routing responsibility need not become another custom service. Start with existing adapters and injected configuration; evaluate a gateway when shared credential/routing management needs it. JiuwenBox's inference proxy provides request routing/key injection; [LiteLLM's public model mappings](https://docs.litellm.ai/docs/proxy/model_management) provide another reuse precedent. No gateway product or integrated compatibility is claimed selected/tested. The contract extends the earlier endpoint-profile view to explicitly cover CC authors and configured model aliases.

Acceptance: run a containerized CC through an allowed alias, move its endpoint without changing CC code, verify the recorded model pin, reject incompatible/unauthorized routes, protect private models, and preserve per-lab quotas and other clients during lab stop. Integration remains unverified.
'''
edit('Designs/Sandbox Lab Design.md',lambda s:s.replace('### OpenJiuwen compatibility and contributions',text+'\n### OpenJiuwen compatibility and contributions'))
edit('Sources/Implementation Intent.md',lambda s:s+'\n## October 27 CC model routing\n\nContainerized CCs and AI4R can call shared inference via a stable injected model interface. Authors declare aliases/requirements; lab configuration resolves compatible available models and credentials. Pin actual identity for each invocation, with explicit model-change policy. Endpoints may move without CC changes. Private models remain lab-only. This extends the previous endpoint-profile explanation and does not select a new gateway product.\n')
edit('Designs/Lab Capsule and Factory Design Plan.md',lambda s:s+'\nModel access integration must inject routes into CC containers as well as AI4R. Validate aliases/features, reachable container networking, credential scoping and recorded model identity after endpoint relocation. A model change must follow explicit binding policy. See the model access contract in [[Designs/Sandbox Lab Design]].\n')
edit('Designs/Sandbox Briefing/presentation/README.md',lambda s:s.replace('Design rev2','Design rev3').replace('Design%20rev2','Design%20rev3').replace('Shared inference API, local or remote','Model routing for AI4R and containerized CCs').replace('`export_system.mjs` exports','`modelRouting` updates slide 7 and the related stack/evidence/acceptance tables after the base callbacks; `export_routing.mjs` exports').replace('## Evidence and limits','The model interface now explicitly serves containerized CCs and AI4R. Lab configuration maps logical roles/aliases to compatible endpoints, injects scoped client configuration, and records the actual model per invocation. Endpoint relocation requires no CC code change; model substitution follows explicit policy. Private models stay lab-scoped. LiteLLM is a routing precedent, not a selected dependency.\n\n## Evidence and limits').replace('- vLLM official API serving:','- Model alias management precedent: https://docs.litellm.ai/docs/proxy/model_management . JiuwenBox routing/key injection: https://github.com/openJiuwen-ai/jiuwenswarm/blob/develop/jiuwenbox/README.md . These do not prove our integrated routing contract.\n- vLLM official API serving:'))
renders=Path('C:/Users/m50066326/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Roaming/Codex/web/Codex/artifact-sessions/exports/latest/e91be6b1fafe6d85492b7271ed7d3473f685aa0efa44c444b2b4a3768bc2c6e9')
for n in [7,10,14,15]:
 for ext in ['png','layout.json']:
  dest=root/'Designs/Sandbox Briefing/presentation/review-system'/f'slide-{n}.{ext}'
  shutil.copy2(dest,batch/f'previous-slide-{n}.{ext}')
  shutil.copy2(renders/f'slide-{n}.{ext}',dest)
(batch/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print('Updated routing contract, prompt capture, plan and presentation index.')
