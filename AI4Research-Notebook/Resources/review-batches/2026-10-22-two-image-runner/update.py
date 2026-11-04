from pathlib import Path
import hashlib,json,re
v=Path(__file__).resolve().parents[3]
b=Path(__file__).resolve().parent
capture='Sources/Prompts/2026-10-22-two-image-runner-layout.txt'
names=['Resources/Coder Prompts/benchmark-runner.md','Resources/Coder Prompts/spark-benchmark-setup.md','Resources/Coder Prompts/README.md','Sources/Implementation Intent.md','Sources/Prompt Register.md','Activities/Activity Register.md','Sources/capture-manifest.json','Workstreams/Lab Infrastructure.md','Designs/Agent Reading and Freshness.md']
sha=lambda data:hashlib.sha256(data).hexdigest()
rows=[]
for name in names:
    data=(v/name).read_bytes();dst=b/'before'/(name.replace('/','__')+'.snapshot')
    dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open('xb') as f:f.write(data)
    assert sha(dst.read_bytes())==sha(data)
    rows.append({'path':name,'snapshot':str(dst.relative_to(v)),'sha256':sha(data)})
(b/'before-receipt.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
request='here is the exact set up that we want. I will refer to our repostiroy as AI4R. AI4R will be used to build 2 containers, 1 is the app itself. call it ai4r. the other is the benchmark runner sidecar. call it benchmark-runner specificaly. heldout tests come from elsewhere.  we will use normal container style for it, so we will build 2 images. 1 for app and 1 for benchmark-runner. so the relevant content for the app is copied into app, relevant to benchmark is copied benchmark-runner. the benchmark runner. our system takes in inputs and files and then produces artifacts in folder, thats what the app is for. but otherwise these will only be in memory and not on disk cuz its containerized. benchmark-runner must consistently copy and take these files and put them on a volume mount in the location user specified. so inputs and output location is all user defined. does this make sense? review, revise your docs, make sure the prompt that will be given to the coding agent makes it clear for both ai and for human. benchmark-runner will be a piece of the ai4r repostory, but it is not in the app container because it is another container. make sense??\n'
with (v/capture).open('xb') as f:f.write(request.encode())
manifest=json.loads((v/names[6]).read_text(encoding='utf-8'))
manifest.append({'path':capture,'sha256':sha(request.encode()),'capture_method':'exact visible user message as UTF-8 LF; terminal newline included; not a transport export','captured_date':'2026-10-22'})
(v/names[6]).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

p=v/names[0];s=p.read_text(encoding='utf-8')
s=s.replace('source: Sources/Prompts/2026-10-22-ai4r-runner-scope.txt','source: '+capture+'; Sources/Prompts/2026-10-22-ai4r-runner-scope.txt',1)
s=s.replace('next_action: Build the CLI runner for AI4Research using a documented system-neutral execution interface','next_action: Build separate ai4r and benchmark-runner images from AI4R; persist collected artifacts in the user-selected output mount')
start=s.index('## For human');end=s.index('## For AI:',start)
s=s[:start]+'''## For human

- **One repository, two images:** AI4R builds `ai4r` for the application and `benchmark-runner` for the separate CLI sidecar.
- **App:** Receives task inputs and files, runs the research work and produces artifact files.
- **Runner:** Reads externally supplied cases, submits their permitted inputs, follows progress and copies actual artifacts and records to persistent storage.
- **Your paths:** You choose the case directory, input files/directories and host output directory at runtime. They are not baked into either image.
- **Persistence:** The output directory is bind-mounted into `benchmark-runner`; saved files survive removal of both containers. Container files are on disk unless explicitly held in memory, but the container's writable layer is disposable.
- **Interface:** CLI only first; parallel jobs share the app's supported execution interface, and humans judge the exported results.
- **Separation:** The runner belongs to AI4R source but is not installed or run inside the `ai4r` app image. Another system implementing the same execution interface can be configured later.
- **Safety:** Each campaign writes to a new owned subfolder of your output directory without overwriting existing files. Spark setup is optional.

'''+s[end:]
s=s.replace('Implement **benchmark-runner in our AI4Research branch of JiuwenSwarm**.', 'Implement **benchmark-runner as part of the AI4R repository**, our AI4Research branch of JiuwenSwarm.')
s=s.replace('Deliver an installable CLI package with a working end-to-end path, example campaign and short runbook.', 'Deliver the CLI package inside its own `benchmark-runner` image, the matching `ai4r` app image, a working end-to-end path, example campaign and short runbook. The user runs the CLI in the sidecar container through Compose; a native host installation is not required.')
needle='### 1. One execution interface'
block='''### Required deployment: two images and two containers

Build **exactly two application images from AI4R** for this deployment, with Compose service names **`ai4r`** and **`benchmark-runner`**. Use immutable version tags/digests; the names are image/service roles, not globally fixed `container_name` values. A normal deployment starts one container of each role. Keep existing external app dependencies/configuration available without adding another benchmark service.

| Image and service | Build contents | Runtime responsibility |
|---|---|---|
| `ai4r` | App code, app dependencies and necessary shared contracts | Accept task inputs/files, execute research, maintain run state and expose outputs/artifacts through the supported interface |
| `benchmark-runner` | CLI, queue/collection/report code, client contracts and runner dependencies | Read user-supplied cases/inputs, submit/observe/cancel work and persist retrieved artifact bytes, ledger and reports to its output mount |

Use two Dockerfiles or two explicit build targets with narrow copy lists and build contexts. Share dependency layers and small neutral contracts where useful; do not copy the entire app into the runner or the runner package into the app. Move any required shared types into a neutral module instead of making app startup import benchmark code. Exclude tests supplied for campaigns, answer keys, datasets, credentials, caches and generated outputs from both image contexts. Do not bake held-out cases or user paths into images. No third worker/referee container is required; the sidecar owns its worker pool and durable queue.

Use Compose for the two services and a small host invocation helper only if needed to resolve mounts/start/stop them. The runner executes in `benchmark-runner`, never inside `ai4r` and never in a helper's second host-side queue. It connects to `ai4r` through authenticated client calls on the private Compose network. Product startup can run with `ai4r` alone.

### User-supplied cases, inputs and persistent output

Require explicit user-selected host paths for the externally supplied case directory, input root(s) and output directory through documented configuration/flags. Resolve them on the Docker host before creating containers. Mount cases and inputs read-only into `benchmark-runner` (for example `/cases` and `/inputs`) and bind the user's output directory read-write (for example `/results`). Fixed paths inside containers are fine; host paths are user-defined. Reject absent/unreadable input paths and unwritable/missing output mounts rather than silently falling back to container-local storage. An explicitly requested new output directory may be created without replacing existing contents. Reject overlapping input/output roots and conflicting mounts.

Held-out tests come from elsewhere. Load the supplied case format and preserve its identity/hash; do not author, guess, embed or expose those tests during implementation. Generic development smoke fixtures are separate. Send only case-authorized task text/files to the app using its input-registration/upload interface. The whole case manifest, private review criteria and answer keys must not be mounted into or forwarded to `ai4r`.

For each submitted task, `ai4r` produces artifacts in its own per-run workspace. The runner cannot read an app-internal absolute path as if it existed in its container. Use the shared execution interface to list and stream/download artifact files, with stable run/artifact IDs, safe relative paths, sizes and hashes. An app-side path or URL alone is not a collected result. The runner must copy the actual bytes into the user's mounted output directory, preserving the artifact folder structure within an owned campaign/case/repeat subtree. Do not expose the app's private filesystem/database to solve file transfer.

Persist the queue, run IDs and collection manifest under that same output mount in a reserved owned campaign subdirectory. Collect available immutable artifacts during observation where supported, and finalize collection for every terminal state, including failed/cancelled/timed-out runs. Stream large files rather than loading a whole bundle into memory. Validate paths and archive entries, refuse symlinks/traversal and conflicting names, write to temporary files, verify size/hash, then atomically publish. Interrupted transfers resume or restart into temporary files without replacing previously verified evidence. Record excluded or unavailable files explicitly.

Track application execution status separately from artifact-collection status. A task that finished in the app is not fully collected until required files and the manifest have been durably written to the mount. Report partial exports, network failure, disk full and permission errors honestly; allow collection retry without rerunning the research task. Check available space and mount writability before submission and during long collections.

The app must retain pending run records and exportable artifacts until collection is confirmed or an explicit documented retention policy expires. Use bounded app-owned persistent staging/state for restart recovery where needed; this is not the user's final result destination and is not a volume shared directly with the runner. Containerization does not make data memory-only: writable layers consume disk and are lost on removal; explicit tmpfs is memory-backed. [Docker storage guidance](https://docs.docker.com/engine/storage/volumes/) explains the distinction. Do not promise recovery of uncollected bytes after deleting the app's last copy. Cleanup requires verified collection or explicit acknowledgement of retained incomplete work; it must not silently destroy uncollected artifacts. User output files survive container removal without `docker cp` or a later manual export step.

'''
assert needle in s;s=s.replace(needle,block+needle,1)
s=s.replace('**Collect:** Retrieve actual outputs, artifacts, available usage/timing and integrity/provenance records through the supported export boundary.', '**Collect:** List and retrieve actual artifact bytes plus available usage/timing and integrity/provenance records; provide immutable artifact identities, paths, sizes and hashes and report when export is complete. Record collection confirmation/retention through the documented interface.')
s=s.replace('If one app instance permits only one active run, launch additional isolated AI4Research instances or serialize only that instance. Do not require parallelism inside the research DAG.', 'Run concurrent task sessions safely in the single `ai4r` app container when its advertised capacity permits. Implement required app admission/concurrency support for independent runs without changing the research DAG. Queue work above the configured capacity and report actual limits. Do not add app replicas or extra worker containers as a prerequisite for this two-container deployment.')
s=s.replace('Use a small host launcher, existing Docker Compose and bounded client workers. The host launcher owns container lifecycle; app/worker containers receive no Docker socket.', 'Use existing Docker Compose for `ai4r` and `benchmark-runner`, with bounded workers inside the sidecar. A host helper may own Compose lifecycle; neither container receives the Docker socket.')
s=s.replace('Create campaign directories atomically under an owned data root outside user projects by default.', "Create unique campaign directories atomically beneath the user's explicitly selected output mount. The runner owns only its campaign subdirectories, not the user's entire output root.")
s=s.replace('Deliver the installed command, shared interface contract, real AI4Research integration, generic queue, parallel execution and safe export.', 'Deliver both images, the containerized CLI command, shared interface contract, real AI4Research integration, generic queue, parallel execution and automatic persistent artifact collection.')
s=s.replace('Verify the installed CLI/help/JSON output, invalid configuration, actual mounted paths and authenticated client calls.', 'Verify both image contents and the CLI/help/JSON output inside `benchmark-runner`, invalid configuration, actual user-selected mounts and authenticated client calls to `ai4r`.')
s=s.replace('Verify concurrent campaigns and normal app use do not collide, and foreign-resource cleanup is refused.', 'Verify concurrent campaigns and normal app use do not collide, and foreign-resource cleanup is refused. Generate a nested artifact tree in `ai4r`, collect it through `benchmark-runner`, remove both containers and prove the host output tree and hashes remain intact. Test interrupted transfer, disk/permission failure, failed-run partial artifacts, restart and retry without duplicate task execution. Prove the app image excludes runner code and both images exclude external cases/secrets.')
assert not re.search(r'baseline|codex',s,re.I)
p.write_text(s,encoding='utf-8')

p=v/names[1];s=p.read_text(encoding='utf-8')
s=s.replace('source: Sources/Prompts/', 'source: '+capture+'; Sources/Prompts/',1)
s=s.replace('- **Provides:** Repeatable Docker/Compose setup, isolated AI4Research task containers, working connections and storage controls.', '- **Provides:** Two AI4R-built images and separate Compose containers: `ai4r` for the app and `benchmark-runner` for the CLI sidecar, with user-selected input and persistent output mounts.')
s=s.replace('Put scripts, deployment configuration and documentation in our AI4Research branch of JiuwenSwarm, using its native task/spec process.', 'Put scripts, deployment configuration and documentation in AI4R, our AI4Research branch of JiuwenSwarm, using its native task/spec process. Build the app image `ai4r` and the sidecar image `benchmark-runner` from their respective source/dependency subsets. The runner package is not included in the app image; neither image contains externally supplied campaign tests or user data. Run the CLI inside the sidecar container; a host installation of the runner is not required.')
start=s.index('Run the selected AI4Research build in isolated task containers')
end=s.index('\n\nResolve bind sources',start)
s=s[:start]+'''Run one `ai4r` container and one `benchmark-runner` container in the normal deployment. Keep service/image role names exact, but let Compose project identities namespace container resources. The sidecar handles its worker pool; app concurrency uses isolated run workspaces in the app. Do not add replicas or worker containers as a setup prerequisite. Reuse runner ownership identities and lifecycle handling. Setting up another system is outside this task.

Require user-selected case/input host paths and a user-selected host output directory. Bind cases/inputs read-only into `benchmark-runner` and bind output read-write; resolve on the actual Docker host and verify inside-container access. The sidecar uploads permitted task files through the app interface and retrieves actual artifact bytes into the output mount automatically. Do not assume app paths exist in the sidecar or use a shared app-private volume. Keep queue/collection state and reports in the mounted output campaign directory. Use bounded app-owned state/staging for pending-artifact recovery; final results belong in the user's output directory. Verify a missing mount fails preflight rather than writing an ephemeral result inside a container.'''+s[end:]
s=s.replace('Create only deployment-owned paths, validate file-versus-directory types', 'Create only explicitly selected new paths and owned subdirectories, validate file-versus-directory types')
s=s.replace('Concurrent AI4Research instances have working scoped client connections and separate writable state; one instance\'s restart does not disrupt the other or normal app use.', 'The `benchmark-runner` sidecar reaches `ai4r` through the scoped client interface, and concurrent tasks use isolated workspaces in the app.')
s=s.replace('Representative container inputs are readable and outputs land in the intended owned location. Pre-existing sentinel files and another deployment remain unchanged.', "User-selected inputs are readable, actual nested app artifacts are copied through the interface into the mounted output location, and host files/hashes survive removal of both containers. Pre-existing sentinel files and another deployment remain unchanged.")
s=s.replace('Repeated setup and stop/start preserve state, avoid duplicate resources and refuse naming/ownership conflicts.', 'Repeated setup and stop/start preserve mounted state, avoid duplicate resources and refuse naming/ownership conflicts. Interrupted collection retries without rerunning the task; missing output mounts and disk/permission failures are reported.')
p.write_text(s,encoding='utf-8')

p=v/names[2];s=p.read_text(encoding='utf-8').replace('CLI task runner for AI4Research: durable parallel execution and safe evidence export through a shared execution interface','AI4R sidecar image/container: CLI task execution and automatic artifact collection into user-selected output mounts').replace('Optional direct-host Spark setup using existing containers, bounded storage and verified connectivity','Optional Spark deployment of ai4r plus benchmark-runner, user-selected mounts and bounded storage')
p.write_text(s,encoding='utf-8')
extras={
names[3]:'''\n## Exact AI4R container and file layout\n\nThe [[Sources/Prompts/2026-10-22-two-image-runner-layout.txt|latest exact layout]] fixes two images from AI4R: `ai4r` contains the app; `benchmark-runner` contains the runner CLI/queue/collection code and runs separately. User-supplied cases and inputs are mounted read-only into the runner; its persistent output bind mount points at the user's chosen host directory. The app receives only permitted task inputs and exposes actual artifact bytes through the shared interface. The runner automatically copies, verifies and records them on the mount; saved artifacts survive removal of both containers. App execution and collection have separate statuses. Files in container writable layers consume disk and are disposable, not automatically memory-only. Earlier host-installed-runner and replica requirements are superseded for this two-container deployment. Both coder prompts now state this explicitly. No Docker deployment was performed.\n''',
names[4]:'\n- [[Sources/Prompts/2026-10-22-two-image-runner-layout.txt|Exact layout: AI4R builds ai4r and benchmark-runner; user chooses input/output mounts]] — separate image contents, external cases and automatic persistent artifact collection.\n',
names[5]:'\n- 2026-10-22: Aligned [[Resources/Coder Prompts/benchmark-runner]] and [[Resources/Coder Prompts/spark-benchmark-setup]] to two images/two containers, user-defined mounts and durable collection of actual app artifacts. Source snapshots and focused checks: `Resources/review-batches/2026-10-22-two-image-runner/`. No runtime execution.\n',
names[7]:'\n## Current app/runner deployment boundary\n\nFor immediate task execution, AI4R builds exactly two images: `ai4r` (app) and `benchmark-runner` (CLI sidecar). [[Resources/Coder Prompts/benchmark-runner]] owns submission and durable artifact collection into user-selected output bind mounts; [[Resources/Coder Prompts/spark-benchmark-setup]] deploys that pair. This supersedes native-host runner installation and additional app replicas as requirements for the immediate setup. M2 VM/factory architecture remains separate.\n',
names[8]:'\n## Exact immediate deployment\n\nThe current [[Resources/Coder Prompts/benchmark-runner]] handoff builds `ai4r` and `benchmark-runner` images from AI4R. Read it for image contents, external case/input mounts, authenticated artifact transfer and persistence in a user-selected host output directory. The CLI runs in the sidecar; a host helper only handles Compose lifecycle. [[Resources/Coder Prompts/spark-benchmark-setup]] uses the same two-container contract.\n'
}
for name,extra in extras.items():
    p=v/name;p.write_text(p.read_text(encoding='utf-8')+extra,encoding='utf-8')
for name in names[:2]:
    text=(v/name).read_text(encoding='utf-8')
    assert not re.search(r'baseline|codex',text,re.I)
    assert all(t in text for t in ['`ai4r`','`benchmark-runner`','user-selected','actual artifact bytes'])
assert all(sha((v/r['snapshot']).read_bytes())==r['sha256'] for r in rows)
print('PASS: two-image roles, user mount paths, actual artifact transfer, removed obsolete deployment requirements, and pre-edit hashes.')
