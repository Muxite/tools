from pathlib import Path
import hashlib,json
v=Path(__file__).resolve().parents[3];b=Path(__file__).resolve().parent
capture='Sources/Prompts/2026-10-22-runner-code-observability.txt'
names=['Resources/Coder Prompts/benchmark-runner.md','Sources/capture-manifest.json','Sources/Implementation Intent.md','Sources/Prompt Register.md','Activities/Activity Register.md']
sha=lambda d:hashlib.sha256(d).hexdigest()
rows=[]
for name in names:
    data=(v/name).read_bytes();dst=b/'before'/(name.replace('/','__')+'.snapshot')
    dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open('xb') as f:f.write(data)
    assert sha(dst.read_bytes())==sha(data)
    rows.append({'path':name,'snapshot':str(dst.relative_to(v)),'sha256':sha(data)})
(b/'before-receipt.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
request='adjsut to "for human and ai". note the benchmarker must be able to run code and see all sorts of observaiblity\n'
with (v/capture).open('xb') as f:f.write(request.encode())
manifest=json.loads((v/names[1]).read_text(encoding='utf-8'))
manifest.append({'path':capture,'sha256':sha(request.encode()),'capture_method':'exact visible user message as UTF-8 LF; terminal newline included; not a transport export','captured_date':'2026-10-22'})
(v/names[1]).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=v/names[0];s=p.read_text(encoding='utf-8')
s=s.replace('source: Sources/Prompts/', 'source: '+capture+'; Sources/Prompts/',1)
s=s.replace('## For human\n','## For human and AI\n',1).replace('## For AI: implement in this order','## Implement in this order',1)
s=s.replace('- **Does:** Runs externally supplied tasks, shows progress, and collects actual outputs, artifacts, timing and available usage for human assessment.', '- **Does:** Runs supplied tasks and declared code, shows progress, and records logs, execution events, artifacts, timing and available resource usage for human assessment.')
needle='Reconcile uncertain submissions after restart;'
block='''Support case-declared executable setup/collection scripts as well as app task execution. Run trusted user-authorized runner scripts in per-job sidecar workspaces; execute generated or untrusted task code through the app's existing isolated execution path. Use explicit commands, working directories, environment allowlists, deadlines and resource limits; capture stdout, stderr, exit codes and produced files. Do not run artifact code automatically in the sidecar or execute anything in user source folders. Script failures are execution observations, not correctness judgments.

'''
assert needle in s;s=s.replace(needle,block+needle,1)
needle='Automatically retain inputs/setup and hashes,'
block='''Provide live CLI status and retained observability: timestamped logs/events, stage transitions, command/tool invocations and exposed results, errors, retries, cancellation, queue/execution/collection timings, and available CPU, memory, disk/I/O, GPU and model usage. Correlate records by campaign/case/repeat/run/step; record sampling interval, scope and contention. Reuse existing telemetry and extend the app interface for missing required observations. Optional metrics advertise capability/unavailability; never fabricate them. Keep exportable structured traces and summaries, redact secrets, and apply audience restrictions without losing declared evidence silently. No monitoring platform, extra container or Docker socket is required.

'''
assert needle in s;s=s.replace(needle,block+needle,1)
s=s.replace('- Concurrent tasks/campaign isolation, missing prerequisites, cancellation, restart and uncertain submission without duplicates.', '- Concurrent tasks/campaign isolation, executable steps with stdout/stderr/exit evidence, deadlines, cancellation, restart and uncertain submission without duplicates.')
s=s.replace('- Safe resume/report regeneration and the same interface tests against AI4R plus the independent fixture using configuration only.', '- Correlated live/retained telemetry, unavailable-metric labels, secret redaction, safe report regeneration and interface portability using the independent fixture.')
p.write_text(s,encoding='utf-8')
extras={
names[2]:'\n## Shared prompt, code execution and observability\n\nThe [[Sources/Prompts/2026-10-22-runner-code-observability.txt|latest direction]] makes the prompt explicitly for human and AI readers. [[Resources/Coder Prompts/benchmark-runner]] now requires declared executable steps and broad live/retained execution telemetry. Trusted runner setup/collection scripts run in owned sidecar workspaces; generated/untrusted task code uses the app execution boundary. Observations remain separate from human correctness assessment. Two-image deployment and persistent outputs are unchanged.\n',
names[3]:'\n- [[Sources/Prompts/2026-10-22-runner-code-observability.txt|For human and AI; executable steps and broad observability]] — scoped code execution and correlated live/retained telemetry added.\n',
names[4]:'\n- 2026-10-22: Updated [[Resources/Coder Prompts/benchmark-runner]] for human/AI readership, executable steps and broad observability; retained concise scope, two images and human judgment. No runtime implementation.\n'
}
for name,extra in extras.items():
    p=v/name;p.write_text(p.read_text(encoding='utf-8')+extra,encoding='utf-8')
assert all(sha((v/r['snapshot']).read_bytes())==r['sha256'] for r in rows)
assert all(t in s for t in ['## For human and AI','stdout, stderr, exit codes','existing isolated execution path','sampling interval','capability/unavailability','Humans assess correctness'])
print('PASS: shared readership, scoped code execution, observability coverage and snapshot hashes. Words:',len(s.split()))
