from pathlib import Path
import hashlib,json
v=Path(__file__).resolve().parents[3];b=Path(__file__).resolve().parent
sha=lambda d:hashlib.sha256(d).hexdigest()
capture='Sources/Prompts/2026-10-22-runner-agent-clarity.txt'
names=['Resources/Coder Prompts/benchmark-runner.md','Sources/capture-manifest.json','Sources/Prompt Register.md','Activities/Activity Register.md']
rows=[]
for name in names:
    data=(v/name).read_bytes();dst=b/'before'/(name.replace('/','__')+'.snapshot')
    dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open('xb') as f:f.write(data)
    assert sha(dst.read_bytes())==sha(data)
    rows.append({'path':name,'snapshot':str(dst.relative_to(v)),'sha256':sha(data)})
(b/'before-receipt.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
request='ok just inform the changes and make sure its easy for the agent to understand the prompt and as long as it sticks to it it will be able to do the job.\n'
with (v/capture).open('xb') as f:f.write(request.encode())
manifest=json.loads((v/names[1]).read_text(encoding='utf-8'))
manifest.append({'path':capture,'sha256':sha(request.encode()),'capture_method':'exact visible user message as UTF-8 LF; terminal newline included; not a transport export','captured_date':'2026-10-22'})
(v/names[1]).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=v/names[0];s=p.read_text(encoding='utf-8')
needle='Read the branch\'s `AGENTS.md`'
block='''### Required changes, in implementation order

1. **Check and reuse the existing code.** Read the applicable branch instructions and registered contracts, then inspect the client, ledger, evidence helpers and Compose assets listed below. Keep app permission enforcement in the app.
2. **Separate the builds.** Produce `ai4r` and `benchmark-runner` images. Exclude runner modules from the app wheel/image; keep the runner's dependencies small. Rename/expose the sidecar service as `benchmark-runner` and remove required score/referee mounts for this mode.
3. **Connect the app interface.** Implement any missing input upload, readiness, submit/reconcile/status/cancel and artifact retrieval operations. The runner uses this documented interface; app paths are not shared filesystem paths.
4. **Run and collect.** Accept user-specified external cases, inputs and output mount. Add the durable concurrent queue. Automatically copy actual artifact bytes into the mounted output campaign folder, verify them and persist collection state. Collection retry must not rerun a task.
5. **Make the CLI usable.** Wire the documented commands to that same queue and client, with helpful errors, progress and JSON output. Keep deployment to the two containers and preserve existing app behavior and user files.
6. **Prove the complete path.** Run generic smoke tasks, including concurrent jobs, interrupted collection and restart. Remove both containers and verify that collected files and hashes remain in the selected host directory. Document the exact invocation and remaining external prerequisites.

The sections below specify these changes; they are not separate feature requests. Use a generic development fixture to build the connected path without needing the held-out test set. Do not invent or expose held-out tests. If host access or authentication is missing, finish the independent implementation and checks, then identify exactly which real execution checks remain incomplete. Do not report those checks as passed.

'''
assert needle in s;s=s.replace(needle,block+needle,1)
p.write_text(s,encoding='utf-8')
for name,extra in {
names[2]:'\n- [[Sources/Prompts/2026-10-22-runner-agent-clarity.txt|Make the runner changes clear and actionable for the coding agent]] — ordered implementation checklist added to the existing handoff.\n',
names[3]:'\n- 2026-10-22: Added a six-step required-change checklist to [[Resources/Coder Prompts/benchmark-runner]]; no scope change or runtime implementation.\n'}.items():
    p=v/name;p.write_text(p.read_text(encoding='utf-8')+extra,encoding='utf-8')
assert all(sha((v/r['snapshot']).read_bytes())==r['sha256'] for r in rows)
assert all(x in s for x in ['Required changes, in implementation order','Exclude runner modules','Collection retry must not rerun a task','verify that collected files and hashes remain'])
print('PASS: ordered implementation checklist and pre-edit/capture preservation.')
