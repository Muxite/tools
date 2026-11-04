from pathlib import Path
import hashlib,json,re
v=Path(__file__).resolve().parents[3]
b=Path(__file__).resolve().parent
capture='Sources/Prompts/2026-10-22-ai4r-runner-scope.txt'
names=['Resources/Coder Prompts/benchmark-runner.md','Resources/Coder Prompts/spark-benchmark-setup.md','Resources/Coder Prompts/README.md','Sources/Implementation Intent.md','Sources/Prompt Register.md','Activities/Activity Register.md','Sources/capture-manifest.json']
sha=lambda data:hashlib.sha256(data).hexdigest()
rows=[]
for name in names:
    data=(v/name).read_bytes();dst=b/'before'/(name.replace('/','__')+'.snapshot')
    dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open('xb') as f:f.write(data)
    assert sha(dst.read_bytes())==sha(data)
    rows.append({'path':name,'snapshot':str(dst.relative_to(v)),'sha256':sha(data)})
(b/'before-receipt.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
request='no need to make the interface or design for the baseline stuff, we just focus on stuff for running ai4rsearch and thats it. dont mention baseline or codex, just how do these tasks perform on our system? and the runner must be compatible with another hypothetical system with the same interface.\n'
with (v/capture).open('xb') as f:f.write(request.encode())
manifest=json.loads((v/names[-1]).read_text(encoding='utf-8'))
manifest.append({'path':capture,'sha256':sha(request.encode()),'capture_method':'exact visible user message as UTF-8 LF; terminal newline included; not a transport export','captured_date':'2026-10-22'})
(v/names[-1]).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

prompt='''---
id: coder-prompt-benchmark-runner
status: ready-to-send
source: Sources/Prompts/2026-10-22-ai4r-runner-scope.txt
last_reviewed: 2026-10-22
next_action: Build the CLI runner for AI4Research using a documented system-neutral execution interface
---
# benchmark-runner

## For human

- **What it is:** A CLI tool in our AI4Research branch for running a queue of tasks against our system.
- **Does:** Loads cases, runs them in parallel, shows progress and collects actual outputs, artifacts, timing and available resource usage.
- **Exports:** JSON records, a CSV matrix and a readable report for human review.
- **Compatible:** Can run against another system that implements the same execution interface, without changing the runner.
- **Protects:** Isolates workspaces and outputs so campaigns do not overwrite user files or interfere with normal app use.
- **Judgment:** Humans assess task quality. The runner reports execution and the application's own observations.
- **Setup:** Uses the app's existing configuration and supported authentication. Spark setup is optional.

## For AI: build the runner

Implement **benchmark-runner in our AI4Research branch of JiuwenSwarm**. The goal is to answer: **what happened when these tasks ran on AI4Research, and what evidence can a human inspect?** Deliver an installable CLI package with a working end-to-end path, example campaign and short runbook. Keep it outside the research hot path; product startup must not depend on it.

Read the branch's `AGENTS.md`, current M1 `TASKS.md`, relevant registered specifications and deployment instructions. The previously inspected branch was `ai4r_M1`, commit `7cc7c2d843bc4ac22a7e9e731dc0efb2e09439e3`; recheck the actual branch and changes before editing. Locate the design files named `benchmark-runner.md` (Platform benchmark runner), `automation.md`, and the sidecar/test-runner `README.md` pages. Follow the native task/spec process and reuse existing task/interface identities.

Reuse the existing `research_sidecar` client, launcher, ledger, reconciliation, cleanup and evidence/export code, plus `deploy/m1` Docker/Compose assets. Extend the fixed case launcher into a generic task queue. The existing design's sequential execution and required automatic referee scoring need a recorded amendment for this mode: independent cases run in parallel and humans judge the results. Preserve useful existing functionality for other callers; this mode must work without score files, protected answers or a referee.

### 1. One execution interface

Define and document one versioned interface from the current supported AI4Research client contract. The runner must use it for:

- **Readiness:** Report system/build identity, interface version, capabilities and missing prerequisites.
- **Submit:** Accept the visible task inputs, permitted resources, execution limits and a stable client request ID; return the run identity.
- **Reconcile:** Find the run by that request ID after an uncertain submission, without creating a duplicate.
- **Observe:** Report status, progress and terminal reason. Stream events when supported; status polling is sufficient otherwise.
- **Cancel:** Request cancellation of a run owned by this campaign and report the resulting state.
- **Collect:** Retrieve actual outputs, artifacts, available usage/timing and integrity/provenance records through the supported export boundary.

Use existing routes where possible; specify the request/response meanings, required fields, authentication scope, capability handling and error behavior in the native contract. Do not invent routes without implementing them. Keep task content separate from runner-only review criteria. System-specific internal stages, capsules and gates are optional observations, not required fields for a conforming system. Missing optional metrics are unavailable, never zero. Incompatible versions or missing required capabilities produce clear preflight errors.

The runner accepts a configured endpoint, credential reference and expected identity. Another hypothetical system implementing this same interface must be usable through configuration, without adding system-name branches, importing private product modules or redesigning the runner. Build the real AI4Research integration now; use a small contract fixture to verify this portability. Do not implement another product or a collection of separate system integrations.

**If the main app does not support the required workflow, modify it as part of this task.** Complete necessary readiness, input registration, submission, reconciliation, cancellation and export support; update the registered contracts and add focused integration checks. An implementation gap is unfinished work, not a permanent blocked case. Preserve research verification and effect controls. Make changes during development, then build and pin the app before execution; a running campaign must not patch its target.

### 2. CLI and durable parallel execution

First version is **CLI only**. Provide consistent `doctor`, `run`, `status`, `resume`, `cancel`, `export` and owned `cleanup` commands with useful help. Support versioned YAML/JSON campaign and case files, target endpoint/configuration, repeats, timeouts, budgets, data root and bounded concurrency. Validate configuration before launching. Provide readable progress and a versioned `--json` mode; keep logs/progress on stderr and machine-readable output on stdout. Document exit codes for command/configuration/prerequisite/execution failures; they do not grade research quality.

Persist case × repeat jobs, claims/leases, request/run identities and pending/running/terminal states transactionally using existing tooling; SQLite is sufficient. Actually run independent jobs concurrently. If one app instance permits only one active run, launch additional isolated AI4Research instances or serialize only that instance. Do not require parallelism inside the research DAG.

After interruption or restart, reconcile uncertain submissions and continue observing existing work. Do not blindly resubmit. Preserve failed, blocked, cancelled and timed-out jobs; unrelated jobs continue according to the configured stop policy. Support a finite campaign deadline. Noninteractive operation must report required human action rather than wait indefinitely. Document Ctrl-C behavior and ensure cancellation/cleanup touches only campaign-owned work.

The runner may execute tasks against one selected AI4Research build or configuration. Retain its source/image/configuration identity so later runs remain interpretable. If branch selection is exposed, resolve the ref once in runner-owned source storage and leave the user's checkout untouched. Multi-system experiments are not a delivery requirement.

### 3. Isolation and reliable container integration

Use a small host launcher, existing Docker Compose and bounded client workers. The host launcher owns container lifecycle; app/worker containers receive no Docker socket. Resolve bind paths on the actual daemon host, including remote deployments. Validate file types, ownership, UID/GID access, symlink/junction escapes and actual in-container input-read/output-write behavior. Inputs are read-only; writable state, authentication sessions and workspaces are isolated by app instance and campaign. Verify real service DNS, ports and scoped API calls.

Use unique Compose project/resource names, ownership labels, isolated networks/volumes and nonconflicting ports. Normal app usage, this campaign and another campaign must coexist. Do not adopt foreign resources, overwrite existing configuration, mount live app data into the runner or use the user's original project as a writable task workspace.

Create campaign directories atomically under an owned data root outside user projects by default. Refuse existing destinations or choose a fresh name. Explicit resume validates matching manifest and ownership, preserves old evidence and human annotations, and appends or versions records. Export never overwrites an existing report. Cleanup validates resolved paths/ownership, removes only disposable owned resources and retains results and persistent state. No global pruning.

Use configured app/model services and their supported authentication. `doctor` distinguishes container liveness, interface readiness and working execution prerequisites. Keep credentials outside images, logs and exports. If access or authentication requires human action, finish independent implementation/checks and report the exact supported next step. Do not fabricate successful runs.

Bound disk/cache/log growth, build contexts, downloads and worker resource use. Reuse immutable dependency layers and build each candidate image once. Record contention, queue waits, effective limits and unavailable measurements; concurrent elapsed times are not isolated performance measurements. Exclusive hardware measurements use a declared reservation. Optional host preparation is in `spark-benchmark-setup.md`; the runner must also work on another compatible Docker host.

### 4. Evidence and human review

Retain each case's inputs/setup and hashes, effective system/build/configuration identities, request/run IDs, events where exposed, actual outputs, artifacts, application-produced gate decisions, terminal reason, timestamps, available usage and limitations. Distinguish queue wait, execution and collection time when observable. Never infer private program decisions from missing records.

Export JSON execution records, a CSV case matrix and a readable Markdown/HTML report with **Inputs and Setup**, **Actual Output and Observations** and artifact references. Include coverage, incomplete jobs and observed timing/usage. Give humans blank **Assessment**, **Evidence references** and **Review notes** fields. Preserve annotations across report regeneration. Reports rebuild from retained records without rerunning agents; the bundle includes permitted artifacts and hashes, with exclusions explicit.

Do not add an automatic correctness judge, task PASS/FAIL, scientific score or winner. Record the application's own verdicts as observations. A scientific negative differs from infrastructure failure. Restricted answers and human criteria never enter task/model context; credentials never enter exports. Keep case support generic without embedding supplied examples or held-out test details.

### 5. Deliver and verify

Deliver the installed command, shared interface contract, real AI4Research integration, generic queue, parallel execution and safe export. Document a short doctor → run → status → export sequence, plus resume/cancel/cleanup examples. Keep a concise implementation record of decisions, changes, validation, blockers and next steps for context recovery. Stay focused on task execution and evidence collection; do not expand into a UI, new infrastructure platform or research workflow redesign.

Verify the installed CLI/help/JSON output, invalid configuration, actual mounted paths and authenticated client calls. Run representative tasks concurrently and preserve real artifacts. Test uncertain-submit reconciliation without duplicate work, restart, cancellation, target failure, missing prerequisites, safe resume and report regeneration. Prepopulate sentinel user files and an existing export; prove they remain unchanged. Verify concurrent campaigns and normal app use do not collide, and foreign-resource cleanup is refused.

Run the same client contract checks against AI4Research and a minimal independent fixture with different internal behavior, using configuration only. This establishes interface portability; it does not claim a second production system was integrated. Label mocks, source checks, actual container execution and model-backed evidence separately. Report real host/authentication blockers honestly; do not claim runtime success without executing it.
'''
assert not re.search(r'baseline|codex',prompt,re.I)
(v/names[0]).write_text(prompt,encoding='utf-8')

p=v/names[1];s=p.read_text(encoding='utf-8')
s=s.replace('source: Sources/Prompts/2026-10-22-spark-benchmark-setup-approved-plan.txt','source: '+capture+'; Sources/Prompts/2026-10-22-spark-benchmark-setup-approved-plan.txt')
s=s.replace('isolated AI4R and baseline containers','isolated AI4Research task containers')
s=s.replace('any required Codex login','any required service authentication')
s=s.replace('cases, scheduling, comparisons and exports','cases, scheduling, execution records and exports')
s=s.replace('case loading, parallel scheduling, branch selection, comparisons, evidence and file export','case loading, parallel scheduling, selected build configuration, evidence and file export')
start=s.index('Run AI4R and upstream JiuwenSwarm/OpenJiuwen in separate target containers')
end=s.index('\n\nResolve bind sources',start)
s=s[:start]+"Run the selected AI4Research build in isolated task containers with separate mutable app state, workspaces, authentication/session state and endpoints where concurrency requires multiple instances. Reuse runner ownership identities and lifecycle handling when available. Standalone setup uses its own explicit owner; do not create a second copy of resources already owned by a campaign. The runner communicates through the documented versioned execution interface. Setting up another system is outside this task."+s[end:]
start=s.index('For Codex-backed campaigns,')
end=s.index('## 3. Keep storage',start)
s=s[:start]+s[end:]
s=s.replace('supported Codex setup/login path','supported service authentication/setup path')
s=s.replace('AI4R and baseline targets have working scoped client connections and separate writable state; one target\'s restart does not disrupt the other.', 'Concurrent AI4Research instances have working scoped client connections and separate writable state; one instance\'s restart does not disrupt the other or normal app use.')
s=s.replace('Missing Codex login','Missing service authentication')
assert not re.search(r'baseline|codex',s,re.I)
p.write_text(s,encoding='utf-8')

p=v/names[2];s=p.read_text(encoding='utf-8')
s=s.replace('In-branch development tool: parallel isolated targets and non-overwriting exports for human review','CLI task runner for AI4Research: durable parallel execution and safe evidence export through a shared execution interface')
p.write_text(s,encoding='utf-8')
p=v/names[3];s=p.read_text(encoding='utf-8')
start=s.index('## Codex-backed comparison')
end=s.index('\n## ',start+1)
s=s[:start]+'''## Prior multi-system proposal: superseded

The earlier comparison proposal is retained in its original prompt captures and pre-edit snapshots. The current user direction below removes that delivery requirement and replaces it with one shared execution interface.
'''+s[end:]
s+='''
## Current runner scope: tasks on AI4Research

The [[Sources/Prompts/2026-10-22-ai4r-runner-scope.txt|latest correction]] narrows [[Resources/Coder Prompts/benchmark-runner]] to running tasks on AI4Research, collecting actual outputs/timing/usage and exporting evidence for human judgment. The CLI remains first. One documented versioned execution interface allows a hypothetical conforming system to work through configuration; no second product integration is required. The current coder prompts no longer prescribe a particular model provider or comparative target. [[Resources/Coder Prompts/spark-benchmark-setup]] deploys only AI4Research task instances. Earlier captures remain history, not current implementation scope.
'''
p.write_text(s,encoding='utf-8')
extras={names[4]:'\n- [[Sources/Prompts/2026-10-22-ai4r-runner-scope.txt|Narrow runner to AI4Research task execution with a shared interface]] — supersedes the earlier multi-system integration requirements; preserves CLI, parallel execution and human review.\n',names[5]:'\n- 2026-10-22: Rewrote [[Resources/Coder Prompts/benchmark-runner]] around AI4Research tasks and one system-neutral execution interface; aligned [[Resources/Coder Prompts/spark-benchmark-setup]] and retired the prior comparison interpretation. No runtime implementation performed.\n'}
for name,extra in extras.items():
    p=v/name;p.write_text(p.read_text(encoding='utf-8')+extra,encoding='utf-8')
assert all(sha((v/r['snapshot']).read_bytes())==r['sha256'] for r in rows)
assert all(x in prompt for x in ['hypothetical system','Reconcile','CLI only','Assessment','transactionally','modify it as part of this task'])
print('PASS: narrowed scope, shared interface, preserved safety requirements and pre-edit hashes.')
