from pathlib import Path
import hashlib,json
v=Path(__file__).resolve().parents[3]
b=Path(__file__).resolve().parent
capture='Sources/Prompts/2026-10-22-runner-cli-interface.txt'
names=['Resources/Coder Prompts/benchmark-runner.md','Sources/capture-manifest.json','Sources/Implementation Intent.md','Sources/Prompt Register.md','Activities/Activity Register.md']
sha=lambda data:hashlib.sha256(data).hexdigest()
rows=[]
for name in names:
    data=(v/name).read_bytes(); dst=b/'before'/(name.replace('/','__')+'.snapshot')
    dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open('xb') as f:f.write(data)
    assert sha(dst.read_bytes())==sha(data)
    rows.append({'path':name,'snapshot':str(dst.relative_to(v)),'sha256':sha(data)})
(b/'before-receipt.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
text='''Capture labels below distinguish two visible user contributions; message wording is preserved.

User clarification:
ok the prompt is for building the runner to use in our system, with a good interface and everything such that it doesnt collide

User answer to interface preference question (small web UI alongside CLI, or CLI-only first version):
CLI only first
'''
with (v/capture).open('xb') as f:f.write(text.encode())
manifest=json.loads((v/names[1]).read_text(encoding='utf-8'))
manifest.append({'path':capture,'sha256':sha(text.encode()),'capture_method':'exact visible clarification and interface answer with explicit capture labels; UTF-8 LF; terminal newline included; not a transport export','captured_date':'2026-10-22'})
(v/names[1]).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=v/names[0]; s=p.read_text(encoding='utf-8')
s=s.replace('source: Sources/Prompts/', 'source: '+capture+'; Sources/Prompts/',1)
s=s.replace('- **Runs:**', '- **Interface:** CLI only for the first version, usable by developers and their agents.\n- **Runs:**',1)
needle='### Start with the actual M1 branch'
new='''### Deliver a usable runner package: CLI first

The deliverable is the **benchmark runner for our system**, not only a Codex wrapper, container recipe or deployment proposal. Package it as an installable module/command in our branch with a documented invocation, example campaign and working end-to-end path. Its targets include the Codex-backed app configurations described below. Codex is a target runtime/backend; it does not replace the runner's queue, lifecycle control or result collection.

**First version: CLI only.** Do not build a web UI, require a browser or add a UI server. Provide one consistent `benchmark-runner` entry point for `doctor`, `run`, `status`, `resume`, `cancel`, `compare`, `export` and `cleanup`, with useful top-level and per-command help. Reuse existing implementations behind that interface instead of adding a second queue or lifecycle manager.

Support an explicit campaign/config file, data root, target selections and concurrency. Validate configuration before launching work and show the resolved target commits, output destination and resource ownership. Match the branch's supported configuration conventions and document precedence. Provide readable status/progress for humans and a versioned `--json` mode for agents. Keep progress/log messages on stderr so stdout can contain parseable results. Return documented exit codes distinguishing command completion, invalid configuration, missing prerequisites and execution failure; exit codes never grade research correctness. Noninteractive commands must not hang on an unexpected prompt; report required authentication or approval with a clear next action.

Every control operation identifies its campaign and validates ownership. Status may inspect retained records, but resume/cancel/cleanup must refuse ambiguous or foreign resources. A graceful CLI interruption must follow the documented cancel/detach behavior and preserve reconciliation records; it must never cancel unrelated app work. Run the CLI on the chosen Docker host, including through SSH, rather than assuming local paths are visible to a remote daemon. Preserve the existing app commands, endpoints, ports and user configuration. Unique campaign names, isolated volumes/networks/workspaces and atomic output creation must allow the app, runner and another campaign to coexist.

Validate the actual installed command, help/config errors, JSON output, concurrent campaign ownership and interruption/recovery. Document a short sequence from `doctor` through run/status to export, plus resume/cancel/cleanup examples. A developer or authorized agent must be able to use that sequence without editing Python files or overwriting user state.

'''
assert needle in s
s=s.replace(needle,new+needle,1)
s=s.replace('no Kubernetes, distributed scheduler, mandatory UI or new message-broker stack is needed for the first release.', 'no Kubernetes, distributed scheduler, web UI or new message-broker stack is needed for the first release.')
p.write_text(s,encoding='utf-8')
extras={
names[2]:'\n## Runner usability and CLI-first scope\n\nThe [[Sources/Prompts/2026-10-22-runner-cli-interface.txt|latest clarification and preference]] confirms an integrated runner package with a good interface and no collisions; the first version is CLI only. [[Resources/Coder Prompts/benchmark-runner]] now requires consistent commands, agent-readable JSON, helpful errors, an installed-command walkthrough and campaign ownership checks. Codex packaging remains target integration, not the runner deliverable. No web UI is requested for this version.\n',
names[3]:'\n- [[Sources/Prompts/2026-10-22-runner-cli-interface.txt|Build a usable integrated runner; CLI only first]] — clarified package/interface and coexistence requirements.\n',
names[4]:'\n- 2026-10-22: Clarified [[Resources/Coder Prompts/benchmark-runner]] as an installable system tool with a CLI-only first version, JSON output, consistent commands and campaign isolation; no runtime implementation performed.\n'}
for name,extra in extras.items():
    p=v/name;p.write_text(p.read_text(encoding='utf-8')+extra,encoding='utf-8')
assert all(sha((v/r['snapshot']).read_bytes())==r['sha256'] for r in rows)
assert 'First version: CLI only' in s and 'not only a Codex wrapper' in s and 'versioned `--json`' in s
print('PASS: prompt interface requirements, pre-edit snapshots and captured direction.')
