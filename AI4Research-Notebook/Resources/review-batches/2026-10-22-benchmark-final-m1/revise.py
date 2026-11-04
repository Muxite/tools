from pathlib import Path
import hashlib, json, subprocess

vault = Path(__file__).resolve().parents[3]
batch = Path(__file__).resolve().parent
def sha(data): return hashlib.sha256(data).hexdigest()
files = ['Resources/Coder Prompts/benchmark-runner.md', 'Sources/Implementation Intent.md', 'Sources/Prompt Register.md', 'Activities/Activity Register.md', 'Sources/capture-manifest.json']
before = []
for name in files:
    data = (vault / name).read_bytes()
    dest = batch / 'before' / (name.replace('/', '__') + '.snapshot')
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open('xb') as f: f.write(data)
    assert sha(dest.read_bytes()) == sha(data)
    before.append({'path': name, 'snapshot': str(dest.relative_to(vault)), 'sha256': sha(data)})
(batch / 'before-receipt.json').write_text(json.dumps(before, indent=2)+'\n', encoding='utf-8')

request = 'also add instruction that if the implementation of the main app does not support benchmarking, then the implementation must be realigned and modified to do it, and tell the agent to be careful with context and stick to the primary goals of what it is told to do. use plain technical english. note the branch this is on does not know about m2 really. i think it is ai4r_m1 branch, you may check that branch and see how things are done, and make a final prompt revision here for what to do\n'
capture = 'Sources/Prompts/2026-10-22-benchmark-main-app-alignment.txt'
with (vault / capture).open('xb') as f: f.write(request.encode('utf-8'))
manifest = json.loads((vault / 'Sources/capture-manifest.json').read_text(encoding='utf-8-sig'))
manifest.append({'path': capture, 'sha256': sha(request.encode('utf-8')), 'capture_method': 'exact visible user message as UTF-8 LF; terminal newline included; not a transport export', 'captured_date': '2026-10-22'})
(vault / 'Sources/capture-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

p = vault / files[0]
s = p.read_text(encoding='utf-8')
s = s.replace('last_reviewed: 2026-10-22', 'last_reviewed: 2026-10-22', 1)
s = s.replace('source: Sources/Prompts/', 'source: '+capture+'; Sources/Prompts/', 1)
s = s.replace('- **Setup:**', '- **App changes:** Fix missing app support as part of implementation; keep benchmark execution isolated from user files.\n- **Setup:**', 1)
start = s.index('Read the current M1 design-package')
end = s.index('### Non-negotiable ownership', start)
s = s[:start] + '''### Start with the actual M1 branch

The inspected branch is **`ai4r_M1`** (capital `M`) in `Stellven/jiuwenswarm`. Its head was `7cc7c2d843bc4ac22a7e9e731dc0efb2e09439e3` on 2026-10-22. Recheck the available branch and current commit before editing; this is a source review, not proof that its containers or model runs work.

Read `AGENTS.md`, the current `TASKS.md` for M1, the relevant registered task/spec files and their design sources. Locate the design files named `benchmark-runner.md` (Platform benchmark runner), `automation.md`, and the `README.md` pages titled **AI4Research sidecar container** and **Test runner (client validation in the sidecar container)**. Use the branch's registered source locations. Do not assume paths from another machine. The task register already contains M1 work; do not create a duplicate because an older instruction says registration is pending.

Reuse the existing `research_sidecar` code, especially `client.py`, `runner.py`, `launcher.py`, `ledger.py`, `reconcile.py`, `campaign.py`, `cleanup.py` and export/report helpers. Inspect `deploy/m1` Dockerfiles and Compose files, including `compose.sidecar.yaml`. The inspected launcher has a fixed set of case families, and its sidecar configuration requires score/report mounts. Extend this into a generic case-driven mode that works without score files or a referee. Reuse useful code; wrapping the existing fixed CLI alone does not meet this request.

The existing design describes sequential campaigns and automatic referee scoring. This request changes those parts for **benchmark-runner**: run independent cases in parallel, use separate baseline containers, and leave assessment to humans. Record these changes through the native task/spec process and update affected interface and deployment documentation. Preserve existing scoring functionality for other callers; this mode must not invoke it or depend on it. Keep the authenticated client/export boundary, app verification gates and separation from product startup.

### Required app changes and context discipline

**If the main app cannot support this benchmark workflow, modify and realign the main app as part of this task.** This includes necessary API, readiness, input import, request reconciliation, cancellation, output export, configuration and container startup changes. Trace the real request path from client to app and exported result. Fix missing or disconnected implementation in our branch and add focused integration checks. Do not deliver a disconnected wrapper, leave implementation gaps as permanent blocked cases, or ask for separate permission for changes already required by this task. Preserve unrelated user work and update the relevant registered contracts and task records.

Implement these changes during development, then build and pin the target image before a campaign starts. A running campaign must never patch its target or alter the original checkout. A deliberately selected older branch may lack a capability; record that incompatibility honestly instead of modifying the historical target. An unavailable remote host, human login or external service is a real external blocker; an interface you still need to implement is unfinished work.

Keep the primary goals visible: load cases, run isolated targets concurrently, collect actual results, and export them for human review without overwriting user files. Read the relevant code and registered design before changing it. Keep a short record of decisions, current changes, validation, blockers and next steps so work can continue after context loss. Distinguish current instructions from historical delivery notes; earlier task-specific limits do not cancel this requested implementation and its focused validation. Do not expand into a new platform, research workflow redesign, automatic judge or unrelated infrastructure project. Use plain technical English in code documentation and the final handoff.

''' + s[end:]
s = s.replace('Runtime never auto-patches a target to make a test pass; missing interfaces are reported or addressed separately as authorized development changes in our branch.', 'Runtime never patches a target to make a case pass. Implement required app support during development as specified above, then test the resulting pinned build.')
s = s.replace('AI4R uses its readiness/submit/reconcile/status/events/retrieve/cancel contract with scoped authentication.', 'AI4R uses its supported readiness, submit, reconcile, status, event/timeline, retrieve and cancel operations with scoped authentication. Verify the actual routes and capabilities; do not invent endpoints.')
s = s.replace('Implement compatibility in the adapter; necessary integration changes belong to normal development in our branch. During a campaign, missing operations/exports are explicit limitations or blocks, never permission to patch source, import private modules to bypass the API or mount the app database into the runner.', 'Implement compatibility in the adapter and fix required missing app operations/exports during development. During a campaign, unexpected incompatibility is recorded as a limitation or block; never patch source, import private modules to bypass the API or mount the app database into the runner. Do not weaken research verification, evidence requirements or effect controls to obtain an output. Preserve the M1 semantic verifier boundary: it receives the pinned declaration and exact output, not original sources or producer context.')
s = s.replace('Export both targets\' terminal artifacts in the same reviewable format without changing either target\'s code.', 'Export both targets\' terminal artifacts in the same reviewable format. Make necessary integration changes in our AI4R branch; keep an upstream baseline at its recorded upstream commit. Any baseline harness or adapter must be versioned and disclosed, without silently substituting our modified AI4R for upstream.')
s = s.replace('Neither M1 automated scoring nor the M2 VM/factory system is a prerequisite.', 'Automatic scoring is not a prerequisite. Build a working M1 developer tool using the existing app and container structure.')
s = s.replace('The eventual Spark target is ARM64 with 128 GB unified memory/2 TB SSD; qualify the actual remote host rather than assuming that hardware. ', 'Record the actual remote host architecture, memory and disk capacity; do not assume unlimited space. Share immutable model files/caches only through supported safe access, while keeping writable app/session state separate. ')
s = s.replace('Do not implement the M2 VM/capsule factory system as a prerequisite for this tool.', 'Do not add VM provisioning or a capsule factory to this delivery.')
assert 'M2' not in s
p.write_text(s, encoding='utf-8')

appendices = {
    'Sources/Implementation Intent.md': '\n## Final M1 benchmark handoff\n\nThe [[Sources/Prompts/2026-10-22-benchmark-main-app-alignment.txt|latest request]] explicitly requires necessary main-app changes when benchmarking is unsupported, plus careful context use and plain technical English. [[Resources/Coder Prompts/benchmark-runner]] now points to the inspected `ai4r_M1` branch, existing sidecar code and deployment gaps. Development must fix required integration; runtime still protects original checkouts and user files. The coder prompt is self-contained for M1 and omits future architecture dependencies. The inspected remote head was `7cc7c2d843bc4ac22a7e9e731dc0efb2e09439e3`; source inspection is not runtime validation. See [[Activities/2026-10-22 Final M1 Benchmark Prompt]].\n',
    'Sources/Prompt Register.md': '\n- [[Sources/Prompts/2026-10-22-benchmark-main-app-alignment.txt|Final M1 prompt: fix missing main-app support, preserve context and stay on task]] — exact request captured 2026-10-22; branch source checked and handoff revised.\n',
    'Activities/Activity Register.md': '\n- [[Activities/2026-10-22 Final M1 Benchmark Prompt|Final M1 benchmark prompt]] — verified remote branch, reviewed existing sidecar/deployment code, required app integration fixes and removed future architecture assumptions; no app implementation or model execution.\n'
}
for name, extra in appendices.items():
    q = vault / name
    q.write_text(q.read_text(encoding='utf-8') + extra, encoding='utf-8')

repo = vault.parent / 'AI4Research-Development/jiuwenswarm-m1-prompt-review-20261022.git'
paths = ['AGENTS.md', 'docs/code/Missions/M1/TASKS.md', 'docs/code/Missions/M1/source/Architecture_Design/side-systems/benchmark-runner.md', 'docs/code/Missions/M1/source/Architecture_Design/development-tools/test-runner/README.md', 'jiuwenswarm/research_sidecar/client.py', 'jiuwenswarm/research_sidecar/runner.py', 'jiuwenswarm/research_sidecar/launcher.py', 'deploy/m1/compose.sidecar.yaml']
receipt = {'repository':'https://github.com/Stellven/jiuwenswarm.git', 'branch':'ai4r_M1', 'commit':subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'], text=True).strip(), 'review_date':'2026-10-22', 'method':'read-only git object inspection in a separate shallow bare clone; no product tests or containers run', 'files':[]}
for name in paths:
    data = subprocess.check_output(['git','-C',str(repo),'show','HEAD:'+name])
    receipt['files'].append({'path':name,'sha256':sha(data)})
(batch / 'branch-source-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
activity = '''---
id: activity-final-m1-benchmark-prompt
status: complete
source: Sources/Prompts/2026-10-22-benchmark-main-app-alignment.txt
last_reviewed: 2026-10-22
next_action: Send the revised coder prompt to the implementing agent
---
# Final M1 benchmark prompt

Revised [[Resources/Coder Prompts/benchmark-runner]] after read-only inspection of `Stellven/jiuwenswarm`, branch `ai4r_M1`, commit `7cc7c2d843bc4ac22a7e9e731dc0efb2e09439e3`. The earlier local development checkout remains unchanged.

The prompt now requires development-time changes to missing main-app support, preserves runtime file protection, and tells the coder to reuse the sidecar client, launcher, ledger and deployment assets. Fixed launcher cases and mandatory score/report mounts need adaptation for generic human-reviewed campaigns. Existing sequential/referee contracts need an explicit recorded amendment for this requested mode. The coder must preserve research gates and real upstream baseline identity. The prompt includes a short context record requirement and contains no future milestone architecture assumptions.

Exact pre-edit bytes and hashes: `Resources/review-batches/2026-10-22-benchmark-final-m1/before-receipt.json`. Branch file hashes: `Resources/review-batches/2026-10-22-benchmark-final-m1/branch-source-receipt.json`.

Validation is recorded in `Resources/review-batches/2026-10-22-benchmark-final-m1/validation.txt`. This delivery edits documentation only. No app implementation, Docker execution, model comparison or remote qualification is claimed.
'''
(vault / 'Activities/2026-10-22 Final M1 Benchmark Prompt.md').write_text(activity, encoding='utf-8')
print('Revised prompt; preserved pre-edit bytes and exact request; recorded branch source hashes.')
