from pathlib import Path
import hashlib,json,re
v=Path(__file__).resolve().parents[3];b=Path(__file__).resolve().parent
capture='Sources/Prompts/2026-10-22-sequential-control-data-runner.txt'
names=['Resources/Coder Prompts/benchmark-runner.md','Resources/Coder Prompts/spark-benchmark-setup.md','Resources/Coder Prompts/README.md','Home.md','Active Stage.md','Designs/Design Library.md','Designs/Agent Reading and Freshness.md','Workstreams/M1 Design Code and Tests.md','Sources/Implementation Intent.md','Sources/Prompt Register.md','Activities/Activity Register.md','Sources/capture-manifest.json']
sha=lambda d:hashlib.sha256(d).hexdigest()
rows=[]
for name in names:
    data=(v/name).read_bytes();dst=b/'before'/(name.replace('/','__')+'.snapshot')
    dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open('xb') as f:f.write(data)
    assert sha(dst.read_bytes())==sha(data)
    rows.append({'path':name,'snapshot':str(dst.relative_to(v)),'sha256':sha(data)})
(b/'before-receipt.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
request='ok single seuqnetial is fine tho. we dont have muhc time to test and build the frame we just want something to work so we can test the app. think of the benchmark runner as a control and data plane. not jsut a sidecar. thats a change we want.\n'
with (v/capture).open('xb') as f:f.write(request.encode())
manifest=json.loads((v/names[-1]).read_text(encoding='utf-8'))
manifest.append({'path':capture,'sha256':sha(request.encode()),'capture_method':'exact visible user message as UTF-8 LF; terminal newline included; not a transport export','captured_date':'2026-10-22'})
(v/names[-1]).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prompt='''---
id: coder-prompt-benchmark-runner
status: ready-to-send
source: Sources/Prompts/2026-10-22-sequential-control-data-runner.txt; Sources/Prompts/2026-10-22-two-image-runner-layout.txt; Sources/Prompts/2026-10-22-runner-code-observability.txt
last_reviewed: 2026-10-22
next_action: Deliver one sequential app-testing path with runner control, observability and persistent data collection
---
# benchmark-runner

## For human and AI

- **Purpose:** Get a useful tool working quickly so we can test AI4Research with supplied tasks and files.
- **Deployment:** AI4R builds two images: `ai4r` for the app and `benchmark-runner` for the separate CLI runner. Run one container of each.
- **Control plane:** The runner prepares inputs, submits tasks one at a time, tracks progress, handles deadlines/cancellation and resumes observation after interruption.
- **Data plane:** The runner transfers input files, executes declared preparation/collection code, captures observability and saves actual outputs/artifacts to the user's mounted output directory.
- **Your paths:** Cases, inputs and output directory are user-selected. Held-out tests are supplied elsewhere. Saved files survive container removal; humans judge results.
- **First version:** Sequential, CLI only. Worker pools, app replicas, distributed scheduling and new framework infrastructure are not required.

## Implementation instructions

Build this in AI4R, our AI4Research branch of JiuwenSwarm. The runner is the control and data plane for a testing campaign; these are responsibilities of one package/process, not two new services. It uses the app's supported interface; the app owns research execution and its policies. Spark deployment is optional.

### 1. Reuse the existing path

Read branch instructions, current M1 task/spec records and the relevant deployment/client contracts. The previously inspected branch was `ai4r_M1`; verify the actual checkout. Locate design files named `benchmark-runner.md` (Platform benchmark runner), `automation.md` and the sidecar/test-runner `README.md` pages. Record this sequential, human-reviewed scope through the native process; earlier parallel requirements are superseded.

Reuse `research_sidecar` client, ledger, reconciliation, evidence and cleanup code plus `deploy/m1` assets. Preserve scoped access, file/hash checks and ownership enforcement. Use existing dependencies and telemetry. Do not build a new SDK, plugin framework, monitoring platform or scheduler. Keep brief progress/decisions/next steps for context recovery.

### 2. Build and connect the two containers

Build `ai4r` with app code/dependencies and `benchmark-runner` with runner code/dependencies. Small neutral contracts may be shared; exclude runner modules from the app wheel/image. Exclude external cases, answers, datasets, credentials, caches and results from both build contexts. Expose the Compose service roles with those exact names, namespace resources by project, and remove required score/referee mounts for this mode without breaking other modes.

Use Compose, private networking and non-root processes. Neither container gets the Docker socket. A small host helper may manage Compose lifecycle, but the runner CLI executes inside `benchmark-runner`. Ordinary app startup must work without the runner.

Use one documented versioned authenticated interface for **readiness/build identity, input upload, submit with client request ID, reconcile, status/events, cancel, and artifact list/download with collection confirmation/retention**. Reuse existing routes. **Modify the app where required to complete this connected path**, preserving research verification, permissions and effect controls. Fix implementation gaps; report actual external prerequisites separately. Pin the build before a campaign and never patch its running target.

Accept endpoint, credential reference and expected identity through configuration. Another hypothetical system implementing this interface must work without private app imports or system-name branches; no second integration is needed now. Optional internal stages/metrics remain unavailable when unsupported. Do not redesign the research workflow or add app concurrency.

### 3. Run the sequential queue

Provide CLI operations for `doctor`, `run`, `status`, `resume`, `cancel`, `export` and owned `cleanup` (equivalent existing commands are fine). Include helpful errors/progress and `--json`; logs go to stderr. Noninteractive runs report required human action instead of hanging. Exit codes describe execution/prerequisite failures, not research correctness.

Load versioned YAML/JSON cases with task text, input references, setup/steps, repeats, limits and deadlines. Persist case/request/run IDs and queue state on the output mount using the existing ledger or SQLite. One task executes at a time: submit → observe terminal state → collect → next task. There is no worker leasing or replica management to build.

After interruption, reconcile the recorded request before any submission; never blindly rerun uncertain work. A disconnected or cancellation-pending run is not stopped: pause dispatch until its state is reconciled so tasks cannot overlap. Preserve failed/blocked/cancelled/timed-out results. Continue after ordinary task failure according to policy; pause new work on shared access/storage failure or unresolved execution. Use fresh run workspaces without changing normal user sessions.

Support case-declared trusted preparation/collection scripts in owned runner workspaces. Execute generated/untrusted task code through the app's existing isolated execution path, not automatically in the runner. Apply explicit commands, working directories, allowed environment, time/resource limits; capture stdout, stderr, exit codes and files. Never execute in user source folders or treat a script exit code as a correctness assessment.

### 4. Persist files and observations

Require explicit user-selected case/input/output host paths resolved on the Docker host, including remote deployment. Bind cases/inputs read-only and output read-write into the runner, for example `/cases`, `/inputs`, `/results`. Validate paths, types, ownership/UID access, conflicting roots and actual mount writability. No fallback to ephemeral container-local output. Create only explicitly requested new directories and owned campaign subfolders; never overwrite existing user files.

Send only permitted task inputs to the app, never private criteria/answers or the whole case store. Collect **actual artifact bytes**, not app-internal paths or links, through the interface into campaign/case/repeat folders. Keep the ledger and collection manifest there. No shared app-private database/state mount. Container writable layers consume disk and disappear on removal; they are not automatically memory-only.

Stream files, validate safe relative paths/archives and sizes/hashes, write temporary files, durably flush and publish atomically. Refuse traversal/symlinks/conflicting names. Retry interrupted collection without rerunning the task or replacing verified evidence. Collect partial artifacts for failed/cancelled runs. Execution and collection have separate states; missing files, disk full and permission/network failure are explicit. Retain app-side pending state/artifacts until collection confirmation or documented expiry; cleanup cannot silently delete uncollected data.

Capture live and saved logs/events, stage/command/tool activity and exposed results, errors, timings, app decisions, identities/configuration and available CPU/memory/disk/GPU/model usage. Correlate by campaign/case/repeat/run/step; record sampling scope, contention and missing metrics. Reuse existing telemetry and add missing essential app observations; advanced optional instrumentation must not delay the first working path. Redact secrets and respect export audiences. Bound disk/cache/log growth and do not infer missing usage as zero.

Automatically save JSON records, a CSV matrix and a readable Markdown report with **Inputs and Setup**, **Actual Output and Observations**, artifact links and blank **Assessment**, **Evidence references**, **Review notes**. Reports rebuild from saved data without reruns or lost annotations. Humans assess quality: no automatic task score, judge, task PASS/FAIL or winner. Distinguish scientific negatives from infrastructure failures.

### 5. Finish a small working version

First deliver **one supplied task → actual app execution → artifact saved on the host**. Then demonstrate a short sequential queue, interruption recovery and reports. Use generic smoke fixtures; do not invent held-out tests. Keep this delivery small: no UI, VM/factory work, parallelism or extensive framework construction.

Run focused connected checks: two images/containers with correct contents; real input/output mounts and authenticated calls; two cases executing in sequence with separated results; cancellation/resume without duplicate submission; failed/interrupted artifact collection; and removal of both containers while host files/hashes survive. Existing sentinel files remain unchanged; cleanup refuses foreign resources and retains results. Use a small interface fixture for configuration-only portability rather than another product integration.

Provide a short build/start/doctor/run/status/export runbook, plus resume/cancel/cleanup examples. Secrets stay out of images/logs/exports. Cleanup is limited to owned disposable resources with no global prune. Report exact commands, evidence and limitations; finish independent work if host access/login is pending and never claim unrun checks passed.
'''
assert not re.search(r'baseline|codex',prompt,re.I)
(v/names[0]).write_text(prompt,encoding='utf-8')
def update(name,fn):
    p=v/name;p.write_text(fn(p.read_text(encoding='utf-8')),encoding='utf-8')
update(names[1],lambda s:s.replace('CLI sidecar','CLI control/data runner').replace('the sidecar image','the runner image').replace('inside the sidecar container','inside the runner container').replace('case loading, parallel scheduling','case loading, sequential task control').replace('The sidecar handles its worker pool; app concurrency uses isolated run workspaces in the app.', 'The runner owns sequential task control, input transfer, observability and persistent artifact collection; there is one active benchmark task at a time.').replace('The sidecar uploads permitted task files','The runner uploads permitted task files').replace('and concurrent tasks use isolated workspaces in the app.', 'and sequential tasks use separate run workspaces in the app.').replace('The `benchmark-runner` sidecar reaches','The `benchmark-runner` control/data runner reaches').replace('Workers use target service addresses','The runner uses the app service address'))
update(names[2],lambda s:s.replace('AI4R sidecar image/container: CLI task execution and automatic artifact collection into user-selected output mounts','Sequential control/data runner: task submission, code/observability and persistent artifact collection'))
update(names[3],lambda s:s.replace('with isolated branch containers, parallel case queues and remote file exports', 'with sequential task control, input transfer, observability and persistent artifact collection'))
update(names[4],lambda s:s.replace('and runs isolated targets in parallel', 'and runs tasks sequentially through a separate control/data runner'))
update(names[5],lambda s:s.replace('is the current parallel, human-judged execution/export handoff','is the current sequential, human-judged control/data runner handoff'))
update(names[6],lambda s:s.replace('parallel isolated targets and evidence exports for human judgment','sequential task execution and control/data collection for human judgment').replace('The CLI runs in the sidecar; a host helper only handles Compose lifecycle.', 'The CLI runs in the separate control/data runner container; a host helper only handles Compose lifecycle.'))
update(names[7],lambda s:s.replace('It runs queued cases in parallel and exports a human-review matrix.', 'It runs queued cases sequentially as a control/data runner and exports a human-review matrix.'))
extras={
names[8]:'\n## Current runner delivery: sequential control and data plane\n\nThe [[Sources/Prompts/2026-10-22-sequential-control-data-runner.txt|latest change]] prioritizes a small working app-testing tool. [[Resources/Coder Prompts/benchmark-runner]] is now one sequential control/data runner with one app container: it owns task sequencing, input transfer, execution observations and persistent artifact collection. Parallel execution, worker pools, leases and replicas are removed from first-delivery requirements. Existing code and essential telemetry are reused; advanced instrumentation is optional. The physical two-container separation remains, but the runner is an active campaign controller and data collector. Spark and current reading routes are aligned; M2 lab designs remain separate.\n',
names[9]:'\n- [[Sources/Prompts/2026-10-22-sequential-control-data-runner.txt|Sequential first: a small control/data runner to test the app]] — supersedes first-version parallelism and worker-pool requirements.\n',
names[10]:'\n- 2026-10-22: Revised [[Resources/Coder Prompts/benchmark-runner]] and current reading routes to sequential control/data operation; prioritized one connected task, a short queue and saved evidence over framework construction. No runtime implementation.\n'
}
for name,extra in extras.items():update(name,lambda s,extra=extra:s+extra)
assert all(sha((v/r['snapshot']).read_bytes())==r['sha256'] for r in rows)
checks=['Control plane','Data plane','One task executes at a time','no worker leasing','pause dispatch','actual artifact bytes','Humans assess quality','First deliver']
assert all(t in prompt for t in checks)
assert 'Run independent sessions concurrently' not in prompt
print('PASS: sequential control/data scope, durable collection, no parallel implementation requirement, original byte hashes. Words:',len(prompt.split()))
