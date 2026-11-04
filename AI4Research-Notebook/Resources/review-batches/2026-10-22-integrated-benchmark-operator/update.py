from pathlib import Path
import hashlib,json
v=Path(__file__).resolve().parents[3]; b=Path(__file__).resolve().parent
files=['Activities/Activity Register.md','Workstreams/Lab Infrastructure.md','Designs/Agent Reading and Freshness.md','Sources/Implementation Intent.md','Sources/Prompt Register.md','Sources/capture-manifest.json']
sha=lambda x:hashlib.sha256(x).hexdigest(); receipts=[]
for name in files:
 data=(v/name).read_bytes(); dst=b/'before'/(name.replace('/','__')+'.snapshot');dst.parent.mkdir(parents=True,exist_ok=True)
 with dst.open('xb') as f:f.write(data)
 receipts.append({'path':name,'snapshot':str(dst.relative_to(v)),'sha256':sha(data)})
(b/'before-receipt.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8')
request='''PLEASE IMPLEMENT THIS PLAN:
# Make AI4R benchmarking self-contained and easy to operate

## Summary

Deliver a repository-owned workflow for **build → stage → start → run/inspect → retrieve results**, usable locally and against an SSH-connected Spark. Reuse the existing sequential runner and two images, `ai4r` and `benchmark-runner`.

All required executable code and configuration templates ship in AI4R. Private runtime directories may hold generated state and credentials, but must contain no required scripts. Spark testing is not required for this implementation.

## Integrated commands and deployment

- Add one host entry point: `python deploy/m1/ai4r.py`. Provide `setup`, `doctor`, `build`, `stage`, `start`, `stop`, `logs`, `fetch`, and `gc`; forward existing campaign commands through `runner`.
- Use a generated deployment profile containing target, Compose project, architecture, image identities, paths and credential references. Support local Docker and SSH targets through the same commands. Keep profile/state outside tracked source.
- Prefer the selected Docker context. Allow explicit WSL distribution selection; remove assumptions about `Ubuntu`, workstation paths and existing installations. Report missing prerequisites clearly.
- Replace imports of private operator scripts with checked-in helpers. Use existing app initialization and scoped-grant commands for setup and credential refresh. Human authentication remains an explicit step; setup must explain how to complete it.
- Make setup repeatable and preserve state. Keep localhost port **5175**, existing app execution isolation, and separate runner mounts. Existing installations require explicit adoption; never silently replace them.
- Retain old launch commands as thin compatibility wrappers where practical.

## Builds, remote execution and storage

- Parameterize builds for `linux/amd64` and `linux/arm64`. Use existing multi-stage Dockerfiles, frozen dependency locks and BuildKit caching. Cached rebuilds remain optional and require compatible pinned dependencies.
- Record source revision, dirty-source identity, platform and immutable image identities. Build away from Spark by default; staging never builds or patches the running target.
- Use SSH/SCP and Docker image archives for the initial remote delivery path; no registry is required. Transfer only selected images, repository-owned deployment helpers and permitted campaign inputs. Skip already verified files/images. Interrupted files remain temporary and are retransferred safely.
- Keep cases and inputs read-only, outputs persistent, and credentials separate. `fetch` copies a stable campaign snapshot into a fresh local directory, verifies hashes and publishes it atomically. Fetching results does not delete their Spark copies.
- Preserve the existing authenticated runner interface and sequential execution behavior. Add no research API redesign, workflow changes, VM provisioning or capsule-factory requirements.
- Report storage usage, cap deployment logs and dedicated build caches, and check staging/build capacity while retaining **20% filesystem headroom**. Refuse new growth when capacity is insufficient.

## Automatic temporary-resource expiry

- Implement repository-owned garbage collection with a default **seven-day TTL**, configurable per deployment.
- Expire only explicitly owned, inactive temporary transfers, completed build contexts and disposable scratch resources. Images require no active or retained deployment reference before removal.
- Protect results, inputs, credentials, app/account volumes, model weights and rollback pins regardless of age. Unknown or interrupted run state prevents cleanup.
- Provide `gc --dry-run`, ownership checks, locking and deletion receipts. Never use global Docker pruning.
- Run expiry during setup and before new allocations. Provide daily scheduling through systemd timers on Linux and Task Scheduler on Windows. If unattended scheduling is unavailable, report that limitation without blocking ordinary benchmarking.

## Validation and documentation

- Test configuration, Docker/WSL selection, command construction, SSH transfer failures, hash verification, repeated setup and expiry boundaries locally.
- Where Docker is available, verify fresh-checkout setup, two-container connectivity, persistent mounts, stop/start recovery and a small sequential campaign. Preserve sentinel user files.
- Exercise the remote path against a local Linux SSH/Docker target where available. Treat ARM64 build checks and native Spark execution as separate evidence.
- Do not require Spark access or model authentication to finish independent implementation. Report any connected checks that remain unrun.
- Add a short operational design with a Mermaid flow and a quick-start runbook. Update the notes library with the repository-only requirement, selected expiry policy and implementation status, preserving source captures and previous notes.
- Keep changes concentrated in deployment tooling and runner integration so ongoing AI4R internals work can merge independently.
'''
cap='Sources/Prompts/2026-10-22-integrated-benchmark-operator-approved-plan.txt'
with (v/cap).open('xb') as f:f.write(request.encode('utf-8'))
manifest=json.loads((v/files[-1]).read_text(encoding='utf-8'))
manifest.append({'path':cap,'sha256':sha(request.encode('utf-8')),'capture_method':'exact visible user implementation request as UTF-8 LF; terminal newline included; not a transport export','captured_date':'2026-10-22'})
(v/files[-1]).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
code='../../AI4Research-Development/jiuwenswarm-m1-deployment/deploy/m1/'
note='''---
id: integrated-benchmark-operator-implementation
status: implemented-local-checks
source: Sources/Prompts/2026-10-22-integrated-benchmark-operator-approved-plan.txt; Activities/2026-10-22 Spark Benchmark Host Direction
last_reviewed: 2026-10-22
next_action: Restore a working Docker engine, then validate the two-container campaign and SSH/ARM64 delivery on available hosts
---
# Integrated benchmark operator

Implemented the approved repository-owned build → stage → start → run/inspect → fetch workflow in our AI4R implementation branch. Code is in `AI4Research-Development/jiuwenswarm-m1-deployment`, isolated branch `deployment-usability`, based on remote `ai4r_M1` commit `bfc30ba291c762d09f464c3e6a6c25f011826a33`. Changes remain uncommitted and unpushed; other development checkouts and AI4R research internals were left intact.

## What changed

The public entry point is `python deploy/m1/ai4r.py`. All required helper source ships in AI4R; generated profiles contain target, paths, ownership, platform and image/credential references rather than private executable dependencies. Old launch/runner commands forward to the integrated operator. The workstation-specific automatic migration was retired: existing installations are refused instead of silently adopted.

The same commands control local Docker, an explicitly selected WSL distribution, or an SSH-connected Linux host. Images are built on the development machine for AMD64/ARM64, with frozen public source manifests, image IDs and bounded dedicated BuildKit caching. Staging verifies images and selected input files; fetch creates a locked snapshot, verifies actual bytes, resumes interrupted copies and retains source results. Localhost remains 5175. The two runtime images remain `ai4r` and `benchmark-runner`.

Linux runner identity follows the non-root host operator where possible, retaining UID11001 for root/Windows targets. Scoped credentials use a separate private Docker volume with mode0600, avoiding Windows bind-permission problems. Model sign-in remains human-owned; no research verification gates were relaxed.

## Expiry and durability

The chosen default is **seven-day temporary-only expiry**. Completed owned transfer/snapshot/build staging and unreferenced owned image candidates are eligible. Results, inputs, credentials, models, app/account volumes and rollback pins are protected. Unknown execution and incomplete transfers are retained until reconciled. No global pruning or data-volume deletion is used.

Expiry runs with setup/start/allocation and supports an explicit daily schedule through Linux systemd or Windows Task Scheduler. Installed Linux helper copies are immutable, hashed copies of repository source in the standard user program location, not handwritten private runtime scripts. Missing user-manager/scheduler access is reported. Docker Desktop's separate virtual-disk capacity and Linux executor delegation still need host qualification.

This implements the practical [[Activities/2026-10-22 Spark Benchmark Host Direction|Spark benchmark-host lifecycle]]. The already-sent [[Resources/Coder Prompts/benchmark-runner|benchmark prompt]] is preserved. M2 durable labs, VM/factory design and broader sandbox planning remain separate.

## Evidence and limits

- New host tests: 24 passed on Windows; 23 passed on Linux/WSL with one Compose-plugin check skipped there. Actual Compose rendering passed on Windows without a daemon.
- Existing sequential-runner, human-report and archive-collection tests: 22 passed in an isolated dependency environment.
- Source compilation and focused lint/checks are recorded with this implementation session.
- Docker Desktop failed to start: its ingest socket could not be renamed because the file was inaccessible. No reset or deletion of Docker data was attempted.
- Live image builds, real two-container campaigns, actual SSH/Docker execution, scheduler activation, ARM64 builds and native Spark runs remain **NOT RUN**. Process/transport fixtures do not establish these outcomes.

Start with [the operational design and runbook](../../AI4Research-Development/jiuwenswarm-m1-deployment/deploy/m1/OPERATIONS.md), which includes the Mermaid flow and exact commands.
'''
(v/'Activities/2026-10-22 Integrated Benchmark Operator.md').write_text(note,encoding='utf-8')
append={
'Activities/Activity Register.md':'\n- [[Activities/2026-10-22 Integrated Benchmark Operator|Integrated repository-owned benchmark operator]] — implemented local/SSH workflows and protected temporary expiry in an isolated AI4R checkout; host and existing runner checks pass, live Docker/Spark execution remains unrun.\n',
'Workstreams/Lab Infrastructure.md':'\n## Integrated benchmark-host operations\n\n[[Activities/2026-10-22 Integrated Benchmark Operator]] records the implementation of repository-owned build, stage, start, inspect, retrieve and temporary-expiry commands. Generated runtime data no longer requires private scripts. Seven-day expiry protects results/project state; the full Spark lifecycle still needs live host qualification. The sent benchmark prompt is preserved and M2 durable sandbox work remains separate.\n',
'Designs/Agent Reading and Freshness.md':'\n## Repository-owned benchmark deployment implementation\n\nRead [[Activities/2026-10-22 Integrated Benchmark Operator]] for the current implementation location, public runbook, supported command path and exact evidence limits. It supersedes instructions requiring private workstation operator scripts. Runtime data and installed hashed repository programs are distinct from handwritten private dependencies. Live Docker/SSH/ARM64/Spark readiness is not established by local fixture tests.\n',
'Sources/Implementation Intent.md':'\n## Repository-owned benchmark operations\n\nThe [[Sources/Prompts/2026-10-22-integrated-benchmark-operator-approved-plan.txt|approved implementation direction]] requires all executable deployment helpers in AI4R, an easy shared local/SSH command path and seven-day expiry of owned temporary resources only. Inputs, retained results, credentials, models and durable app/lab state are protected. Actual Spark testing is deferred; complete independent local checks and report unrun host checks. See [[Activities/2026-10-22 Integrated Benchmark Operator]] for the implemented code location and current validation.\n',
'Sources/Prompt Register.md':'\n- [[Sources/Prompts/2026-10-22-integrated-benchmark-operator-approved-plan.txt|Approved integrated benchmark-operator implementation]] — repository-only helpers, local/remote delivery and seven-day temporary-only expiry; Spark testing not required for the first implementation.\n'}
for name,addition in append.items():
 p=v/name;p.write_text(p.read_text(encoding='utf-8')+addition,encoding='utf-8')
assert all(sha((v/r['snapshot']).read_bytes())==r['sha256'] for r in receipts)
print('Updated five notes/routes and added implementation activity; exact approved-plan capture and six before-snapshot hashes verified.')
