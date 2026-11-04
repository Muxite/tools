from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parents[3]
batch=Path(__file__).resolve().parent/'jiuwenbox-fit';batch.mkdir(exist_ok=True)
records=[]
def save(rel,text):
 p=root/rel
 if p.exists():
  old=p.read_bytes();(batch/(rel.replace('/','__')+'.snapshot')).write_bytes(old);records.append({'path':rel,'before_sha256':hashlib.sha256(old).hexdigest()})
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8',newline='\n')
def edit(rel,fn):save(rel,fn((root/rel).read_text(encoding='utf-8-sig')))
prompt='then after doing that, check, waht does jiuwenbox satisfy for us? for "inside the labs AI4R", swrap the CC library box and the supervisor box so their lines dont overlap\n'
rel='Sources/Prompts/2026-10-27-jiuwenbox-fit-and-diagram.txt';save(rel,prompt)
manifest='Sources/capture-manifest.json';rows=json.loads((root/manifest).read_text(encoding='utf-8-sig'));rows.append({'path':rel,'sha256':hashlib.sha256(prompt.encode()).hexdigest(),'capture_method':'Exact visible user message, UTF-8 LF; not a transport export','captured_date':'2026-10-27'});save(manifest,json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
edit('Sources/Prompt Register.md',lambda s:s+'\n- [[Sources/Prompts/2026-10-27-jiuwenbox-fit-and-diagram.txt|JiuwenBox requirements fit and diagram routing]]: source-check reuse against the model-routing design; swap library and supervisor positions.\n')
fit='''
### JiuwenBox fit after adding CC model routing

Pinned upstream `02b37f47fbefe80a58e4ed88606120818ca44ac3` was inspected again on October 27. [Official overview](https://github.com/openJiuwen-ai/jiuwenswarm/blob/develop/jiuwenbox/README.md). The pin, not the moving branch, grounds the code findings. Appendix slide 17 gives a requirement-to-mechanism table.

| Requirement | Existing JiuwenBox mechanism | What remains for our integration |
|---|---|---|
| Tool/file operations | API command and file operations; Python/JS execution with installed runtimes | Bind CC operation contracts, inputs, results and errors |
| Execution restrictions | Bubblewrap, filesystem/network policy, optional cgroup CPU/memory/PID controls | Qualify host support and effective policy; map container-specific execution through Docker |
| Job control / stop | Background job controls, separate stop/restart/delete; graceful daemon shutdown and process-group signal escalation | Verify termination and retained state; integrate Docker CC ownership/cancellation |
| Model API transport | Configured path-prefix routes to endpoints and API-key injection | Inject reachable routes into CCs; resolve logical aliases/features, enforce scoped access and record actual model bindings |
| Operational persistence | Sandbox lifecycle records and audit events | Research knowledge/results, application checkpoints and independent backup/restore |
| Whole-lab control | Reusable Linux service inside a lab VM | Host/provider VM stop and durable lab orchestration |

`server/runtime/process.py:stop` first stops tracked background processes, asks the daemon to shut down, waits, then uses SIGTERM and SIGKILL if needed, waiting again. `sandbox_manager.py` saves STOPPED after runtime.stop returns. This establishes actual termination implementation, beyond an API name, but is not an observed deployment test. Background kill can report failure, and resource limits are optional. Verify outcomes rather than treating status labels as proof.

`proxy/inference_privacy_proxy.py:ProxyRoute` binds path prefixes to target endpoints and credentials. This is useful transport and secret injection, not evidence of semantic model-role selection or feature matching. It does not automatically make a container network path reachable or enforce our experiment model pins. Keep those responsibilities in the lab model adapter/configuration, evaluating extensions only when needed.

The stable supervisor remains a responsibility, not a demand for a new daemon. Evaluate reuse of JiuwenBox's execution backend and proxy first, with narrow AI4R/Docker lifecycle integration. Do not impose a second bubblewrap sandbox around every OCI CC without a demonstrated need. Whole-VM control stays outside the guest. No software was installed and no runtime compatibility test was run for this review.

'''
edit('Designs/Sandbox Lab Design.md',lambda s:s.replace('## Evidence that would make this valuable',fit+'## Evidence that would make this valuable'))
edit('Designs/Sandbox Briefing/presentation/README.md',lambda s:s.replace('Design rev3','Design rev4').replace('Design%20rev3','Design%20rev4').replace('six hidden appendix slides','seven hidden appendix slides').replace('six hidden appendix references','seven hidden appendix references').replace('| 16 | Tradeoffs and resource constraints |','| 16 | Tradeoffs and resource constraints |\n| 17 | JiuwenBox requirements fit and remaining integration |').replace('`export_routing.mjs` exports','`jiuwenboxFit` adds the reuse map on slide 17 and updates the appendix index; `export_jiuwenbox.mjs` exports').replace('## Evidence and limits','Slide 3 now puts the supervisor above the CC library, with straight execution/admission lines and a separate routed library-selection line. Appendix 17 maps JiuwenBox to execution, restrictions, shutdown, model transport, operational state and whole-lab control. The source includes graceful stop plus signal escalation; actual deployment termination remains untested.\n\n## Evidence and limits'))
edit('Home.md',lambda s:s.replace('ten main slides, six hidden appendix references','ten main slides, seven hidden appendix references'))
edit('Presentation Library/Deck Catalog.md',lambda s:s.replace('Ten main slides and six hidden appendix references','Ten main slides and seven hidden appendix references'))
renders=Path('C:/Users/m50066326/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Roaming/Codex/web/Codex/artifact-sessions/exports/latest/e91be6b1fafe6d85492b7271ed7d3473f685aa0efa44c444b2b4a3768bc2c6e9')
for n in [2,3,11,17]:
 for ext in ['png','layout.json']:
  dest=root/'Designs/Sandbox Briefing/presentation/review-system'/f'slide-{n}.{ext}'
  if dest.exists():shutil.copy2(dest,batch/f'previous-slide-{n}.{ext}')
  shutil.copy2(renders/f'slide-{n}.{ext}',dest)
sources=[]
for rel in ['README.md','src/jiuwenbox/server/sandbox_manager.py','src/jiuwenbox/server/runtime/process.py','src/jiuwenbox/proxy/inference_privacy_proxy.py']:
 p=root.parent/'openjiuwen/jiuwenswarm/jiuwenbox'/rel;sources.append({'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(batch/'source-review.json').write_text(json.dumps({'revision':'02b37f47fbefe80a58e4ed88606120818ca44ac3','scope':'source inspected, integration untested','sources':sources,'note_backups':records},indent=2)+'\n',encoding='utf-8')
print('Saved requirement mapping, source receipt, prompt and diagram previews.')
