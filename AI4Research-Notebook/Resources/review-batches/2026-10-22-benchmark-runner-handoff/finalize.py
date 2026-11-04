from pathlib import Path
import json, hashlib, re

v = Path(__file__).resolve().parents[3]
b = Path(__file__).resolve().parent
old = v / 'Resources/Coder Prompts/M1 Benchmark and CI.md'
new = v / 'Resources/Coder Prompts/benchmark-runner.md'
assert old.resolve().is_relative_to(v.resolve()) and new.resolve().is_relative_to(v.resolve())
assert old.is_file() and not new.exists()
before = []

def preserve(p):
    rel = p.relative_to(v).as_posix()
    q = b / 'before' / (rel + '.snapshot')
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_bytes(p.read_bytes())
    before.append(dict(path=rel, snapshot=q.relative_to(v).as_posix(), sha256=hashlib.sha256(q.read_bytes()).hexdigest()))

files = []
for p in v.rglob('*.md'):
    rel = p.relative_to(v).as_posix()
    if rel.startswith(('Archive/', 'Resources/review-batches/')):
        continue
    if p == old or 'Resources/Coder Prompts/M1 Benchmark and CI' in p.read_text(encoding='utf-8'):
        files.append(p)
for rel in ['Sources/Prompt Register.md', 'Activities/Activity Register.md']:
    p = v / rel
    if p not in files:
        files.append(p)
for p in files:
    preserve(p)

captures = {
    '2026-10-22-benchmark-runner-orchestrator-request.txt': 'the benchmarker must above ai4r and msut be able to switch branches and allow A vs B. we need the ability to do these in parallel. ideally move onto the remote and we can run either and it must be a good benchmark runner. we load in the cases, it will run in parallel and then say what the results are. the benchmarker job is to speed up the process of finding the results of various tasks and allow file export. thats the job, and it must do it well. so make the prompt to get the agent to make it, knowing that the agent. the docker stuff must be very clean, volume mounts resolved, apis msut work. note that user will need to set up the codex connection at some point for it to run successfully, write the document, keep a short "for huamn" at the top to explain and review, the rest for ai. we will call this benchmark-runner',
    '2026-10-22-separate-baseline-container-request.txt': 'ideally the jiuwenswarm and ai4r branch are on different containers so tehy dont collide and cause problems, follow standard procedures and make sure this cna be built relatviely quickly',
    '2026-10-22-standalone-human-judged-benchmarks.txt': 'it must not touch the user codebase, and msut live on its own, it will not judge the results beyond the program, the humans will take the results and judge them for each test in matrix, whateve rthese tests may be',
}
f = v / 'Sources/capture-manifest.json'
m = json.loads(f.read_text())
for name, text in captures.items():
    p = v / 'Sources/Prompts' / name
    assert not p.exists()
    p.write_bytes(text.encode('utf-8'))
    m.append(dict(path=p.relative_to(v).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), captured_date='2026-10-22', capture_method='Exact visible user wording in UTF-8, no added terminal newline; not transport export', original_message_timestamp='unavailable; date denotes capture'))
f.write_text(json.dumps(m, indent=2) + '\n', encoding='utf-8')

old_bytes = old.read_bytes()
old.rename(new)
assert new.read_bytes() == old_bytes
new.write_bytes((b / 'benchmark-runner.draft').read_bytes())

for p in files:
    if p == old:
        continue
    t = p.read_text(encoding='utf-8')
    t = t.replace('Resources/Coder Prompts/M1 Benchmark and CI', 'Resources/Coder Prompts/benchmark-runner')
    if p == v / 'Resources/Coder Prompts/README.md':
        t = t.replace('last_reviewed: 2026-10-21', 'last_reviewed: 2026-10-22').replace('next_action: Use the M1 benchmark prompt for the existing sidecar implementation work', 'next_action: Send benchmark-runner to its implementing agent; human reviews task results')
        t = re.sub(r'^\| \[\[Resources/Coder Prompts/benchmark-runner.*$', '| [[Resources/Coder Prompts/benchmark-runner\\|benchmark-runner]] | Standalone parallel AI4R/JiuwenSwarm branch runs and exports for human review | Latest user handoff; existing M1 APIs are read-only integration references |', t, flags=re.M)
    elif p == v / 'Home.md':
        start = t.index('## M1 coder handoff')
        end = t.index('## M2 sandbox and capability infrastructure', start)
        t = t[:start] + '## Standalone benchmark-runner\n\n[[Resources/Coder Prompts/benchmark-runner|Copy the implementation handoff]]: own repository, isolated AI4R/JiuwenSwarm branch containers, parallel case queues, remote-host operation and file exports. It does not modify user codebases or automatically judge task correctness; humans review the matrix. This replaces the earlier sidecar-only/scorer prompt. Existing M1 APIs are integration references; M2 VM/factory work remains separate.\n\n' + t[end:]
    elif p == v / 'Workstreams/M1 Design Code and Tests.md':
        start = t.index('## Current coder handoff')
        end = t.index('## Immediate work', start)
        t = t[:start] + '## Current coder handoff\n\nThe user reports working M1 code on another machine; that is not a locally inspected runtime result. [[Resources/Coder Prompts/benchmark-runner]] now requests a standalone tool in its own repository, above AI4R and JiuwenSwarm. It runs isolated branches/targets and queued cases in parallel, preserves actual outputs and exports a human-review matrix. It must not change user code or automatically grade the tasks.\n\nThis supersedes the earlier sidecar-only/automatic-referee handoff. Existing M1 product/client contracts remain context; the runner integrates through supported APIs/CLI or reports gaps. M2 lab/factory construction is not a prerequisite.\n\n' + t[end:]
    elif p == v / 'Designs/Design Library.md':
        t = t.replace('## M1 implementation prompt', '## Standalone benchmark implementation prompt')
        t = re.sub(r'\[\[Resources/Coder Prompts/benchmark-runner\]\] is the portable.*?(?=\n\n)', '[[Resources/Coder Prompts/benchmark-runner]] is the current standalone, parallel, human-judged execution/export handoff. The latest user scope supersedes its earlier sidecar-only and automatic-scoring assumptions. Existing M1 design/API files remain read-only integration context; no product-code or M2 implementation is implied.', t, count=1, flags=re.S)
    elif p == v / 'Designs/Agent Reading and Freshness.md':
        t += '\n## Updated benchmark-runner authority\n\n[[Resources/Coder Prompts/benchmark-runner]] is the latest human-authorized scope: independent repository, no user-code mutations, parallel isolated branch targets, raw evidence/export and human task judgment. Earlier M1 sequential/automatic-referee restrictions do not override this handoff; it does not rewrite the maintained M1 architecture.\n'
    elif p == v / 'Sources/Implementation Intent.md':
        t += '\n## Standalone, human-judged benchmark-runner\n\nThe latest three requests replace the earlier M1-sidecar-only prompt: [[Resources/Coder Prompts/benchmark-runner]] must live in its own repository, leave user code untouched, select branches using runner-owned clones, execute isolated AI4R/JiuwenSwarm targets in parallel and export results. Humans judge each matrix test. Automatic referee/scoring, target-repository edits and mandatory M1 pilot work are not requirements of this updated tool. Codex authentication is a human setup dependency, reported explicitly by preflight.\n'
    elif p == v / 'Active Stage.md':
        t += '\nThe current benchmark handoff is standalone and human-judged: [[Resources/Coder Prompts/benchmark-runner]]. It does not modify the user codebases or redefine product acceptance. Its case queue runs across isolated targets in parallel; M2 sandbox/factory implementation is separate.\n'
    p.write_text(t, encoding='utf-8')

p = v / 'Sources/Prompt Register.md'
p.write_text(p.read_text(encoding='utf-8').rstrip() + '\n\n- [[Sources/Prompts/2026-10-22-benchmark-runner-orchestrator-request.txt|External benchmark-runner: branch A/B, remote parallel queues and exports]].\n- [[Sources/Prompts/2026-10-22-separate-baseline-container-request.txt|Separate AI4R/JiuwenSwarm containers and a quick standard implementation]].\n- [[Sources/Prompts/2026-10-22-standalone-human-judged-benchmarks.txt|Own repository, untouched user codebases and human matrix judgments]] - these latest directions supersede the earlier sidecar-only/automatic-referee handoff.\n', encoding='utf-8')
p = v / 'Activities/Activity Register.md'
p.write_text(p.read_text(encoding='utf-8').rstrip() + '\n\n- [[Activities/2026-10-22 Standalone Benchmark Runner Handoff|Standalone benchmark-runner handoff]] - renamed prompt, external parallel branch targets, no user-code edits, human judgment and remote/container/export requirements.\n', encoding='utf-8')
(v / 'Activities/2026-10-22 Standalone Benchmark Runner Handoff.md').write_text('''---
id: activity-standalone-benchmark-runner-handoff
status: completed-documentation
source: Sources/Prompts/2026-10-22-benchmark-runner-orchestrator-request.txt; Sources/Prompts/2026-10-22-separate-baseline-container-request.txt; Sources/Prompts/2026-10-22-standalone-human-judged-benchmarks.txt
last_reviewed: 2026-10-22
next_action: Send benchmark-runner to the implementing agent in its own repository
---
# Standalone benchmark-runner handoff

Replaced and renamed the earlier prompt as [[Resources/Coder Prompts/benchmark-runner]]. The new handoff has a short human section and implementation instructions for a standalone remote-capable CLI, parallel branch/case scheduling, independent target containers, clean mounts/APIs, Codex preflight and reviewable file exports.

User steering explicitly forbids modifying user codebases and assigns task judgments to humans. Removed external automatic scoring/referee and target-code changes from requested delivery. Existing program verdicts remain observations. Earlier prompt bytes and incoming-note snapshots are preserved in the review batch; links were rebased to the new name. Historical source captures were not rewritten.

No runner code was implemented, no remote connection or container/model run occurred, and no user application repository was edited. Documentation validation is recorded in Resources/review-batches/2026-10-22-benchmark-runner-handoff.
''', encoding='utf-8')
(b / 'pre-edit-receipts.json').write_text(json.dumps(before, indent=2) + '\n', encoding='utf-8')
(b / 'revision-receipt.json').write_text(json.dumps(dict(date='2026-10-22', old_path=old.relative_to(v).as_posix(), current_path=new.relative_to(v).as_posix(), previous_sha256=hashlib.sha256(old_bytes).hexdigest(), current_sha256=hashlib.sha256(new.read_bytes()).hexdigest(), scope='Standalone runner, parallel targets, no user-code mutations, human-only task judgment; document handoff only', standard_sources=['https://docs.docker.com/compose/how-tos/project-name/', 'https://docs.docker.com/engine/storage/bind-mounts/', 'https://docs.docker.com/engine/security/protect-access/', 'https://git-scm.com/docs/git-worktree']), indent=2) + '\n', encoding='utf-8')
print(f'Renamed and revised prompt; rebased links in {len(files)-1} notes.')
