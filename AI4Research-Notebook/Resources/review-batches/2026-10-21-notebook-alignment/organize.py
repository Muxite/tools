from pathlib import Path
import hashlib, json, re

v = Path(__file__).resolve().parents[3]
w = v.parent.resolve()
b = Path(__file__).resolve().parent
src = (w / 'm1-benchmark-ci-coder-prompt.md').resolve()
dst = (v / 'Resources/Coder Prompts/M1 Benchmark and CI.md').resolve()
assert src.is_relative_to(w) and dst.is_relative_to(v.resolve())
assert src.is_file() and not dst.exists()
paths = ['Home.md', 'Active Stage.md', 'Designs/Design Library.md', 'Workstreams/M1 Design Code and Tests.md', 'Workstreams/Lab Infrastructure.md', 'Designs/Agent Reading and Freshness.md', 'Sources/Implementation Intent.md', 'Sources/Prompt Register.md', 'Activities/Activity Register.md', 'Notebook Guide.md']
snapshots = []
for name in paths:
    p = v / name
    q = b / 'before' / (name + '.snapshot')
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_bytes(p.read_bytes())
    assert q.read_bytes() == p.read_bytes()
    snapshots.append(dict(path=name, snapshot=q.relative_to(v).as_posix(), sha256=hashlib.sha256(q.read_bytes()).hexdigest()))
body = src.read_bytes()
q = b / 'before/m1-benchmark-ci-coder-prompt.md.snapshot'
q.write_bytes(body)
snapshots.append(dict(path=str(src), snapshot=q.relative_to(v).as_posix(), sha256=hashlib.sha256(body).hexdigest()))
(b / 'pre-edit-receipts.json').write_text(json.dumps(snapshots, indent=2) + '\n', encoding='utf-8')

captures = {
    '2026-10-21-notebook-organization-request.txt': 'move files into correct locations in my notes obsidian library, correct place, align docs',
    '2026-10-21-working-m1-and-poc-request.txt': 'we have a working code now on another persons machine, give an example of what the system should do (m1 POC pipeline)',
    '2026-10-21-m1-benchmark-prompt-directions.txt': 'Message 1 (exact visible text):\nmake 1 quick md file that is just a simple prompt to send to main coder agent so that it knows to build the benchmarking/ci apparatus and make sure it connects to container as designed. it already has access to the m1 design package, but you should tell it to look at design too. just jis just small prompt to send\n\nMessage 2 (exact visible text):\nthe location isnt the same, so just say the file names on m1 and specifics of what this benchmarker is\n\nMessage 3 (exact visible text):\nmake sure this matches design-package for m1 very closely.',
}
f = v / 'Sources/capture-manifest.json'
manifest = json.loads(f.read_text())
for name, text in captures.items():
    p = v / 'Sources/Prompts' / name
    assert not p.exists()
    p.write_bytes(text.encode('utf-8'))
    manifest.append(dict(path=p.relative_to(v).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), captured_date='2026-10-21', capture_method='Visible user wording in UTF-8; multi-message file has explicit capture labels; no added terminal newline; not transport export', original_message_timestamp='unavailable; date denotes capture'))
f.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')

dst.parent.mkdir(parents=True, exist_ok=True)
src.rename(dst)
assert dst.read_bytes() == body and not src.exists()
metadata = '''---
id: coder-prompt-m1-benchmark-ci
status: ready-to-send
source: Sources/Prompts/2026-10-21-m1-benchmark-prompt-directions.txt; Sources/Prompts/2026-10-21-notebook-organization-request.txt
last_reviewed: 2026-10-21
next_action: Copy the Markdown body to the main coder; record implementation evidence in the owning repository
---
'''
dst.write_bytes(metadata.encode('utf-8') + body)
assert dst.read_bytes().split(b'---\n', 2)[2] == body
(b / 'move-receipt.json').write_text(json.dumps(dict(source=str(src), destination=str(dst), original_body_sha256=hashlib.sha256(body).hexdigest(), final_file_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(), body_preserved=True, change='Added only Obsidian YAML metadata; coder-facing body unchanged', root_original_removed_by_move=True), indent=2) + '\n', encoding='utf-8')

def note(name, identity, title, action, content, status='active'):
    (v / name).write_text(f'---\nid: {identity}\nstatus: {status}\nsource: Sources/Prompts/2026-10-21-notebook-organization-request.txt; Sources/Prompts/2026-10-21-m1-benchmark-prompt-directions.txt\nlast_reviewed: 2026-10-21\nnext_action: {action}\n---\n# {title}\n\n' + content.strip() + '\n', encoding='utf-8')

note('Resources/Coder Prompts/README.md', 'coder-prompts-index', 'Coder prompts', 'Use the M1 benchmark prompt for the existing sidecar implementation work', '''
Short handoffs to paste into a coder conversation. Copy the note body; Obsidian YAML properties are notebook metadata. Prompts identify design files by filename/title so they work on another machine.

| Prompt | Purpose | Authority |
|---|---|---|
| [[Resources/Coder Prompts/M1 Benchmark and CI|M1 benchmark and CI]] | Complete platform benchmarking and client-validation tooling against the working M1 app/container | Existing maintained M1 design-package; no new product requirements |

See [[Workstreams/M1 Design Code and Tests]] for implementation context and [[Designs/Design Library]] for canonical design links. M2 VM labs, factories, container CCs and Spark resource policy remain proposals under [[Designs/Lab Capsule and Factory Design Plan]] and [[Designs/Spark Shared Services and Storage]].
''')

p = v / 'Home.md'
t = p.read_text(encoding='utf-8')
t = t.replace('next_action: Read the project overview and first CC accuracy amendment', 'next_action: Use the M1 coder prompt for benchmark tooling and the M2 roadmap for Spark sandbox design')
t = t.replace('| Validate the lab CLI on a running Docker host |', '| Qualify Spark capacity and ARM64 CPU guests under the M2 resource policy |')
t = t.replace('| Reconcile compiler candidates with current contracts |', '| Use the M1 benchmark/CI coder prompt and collect actual candidate evidence |')
t = t.replace('- [[Resources/Current Baseline|Captured M1 source and host status]] supersedes earlier Docker-unavailable observations. Docker Desktop now responds; M1 account/operator readiness and GB10 qualification remain separate requirements.', '- [[Resources/Current Baseline|Captured M1 source and host receipts]] are dated, machine-specific observations. The user reports working M1 code on another person\'s machine; its build/test evidence has not been inspected here. Later local Docker availability and Spark qualification are separate facts.')
i = t.index('## AI4R lab idea')
t = t[:i] + '''## M1 coder handoff

[[Resources/Coder Prompts/M1 Benchmark and CI|Copy the short benchmark/CI prompt]]. It follows the existing M1 platform benchmark, sidecar, test-runner and automation contracts. [[Resources/Coder Prompts/README|Coder prompt index]] and [[Workstreams/M1 Design Code and Tests|M1 workstream]] retain context. The platform benchmarker is separate from the Research Benchmark CC.

## M2 sandbox and capability infrastructure

[[Designs/Lab Capsule and Factory Design Plan|M2 roadmap]] → [[Designs/Spark Shared Services and Storage|Spark resource policy]] → [[Designs/VM Lab Infrastructure Design|VM deployment]], [[Designs/Container Capability Capsule Design|container CCs]] and [[Designs/Per Lab Capability Factory Design|local factories]]. [[Designs/Docker Architecture Review and Feasibility|Feasibility review]] records design corrections and untested dependencies.

Target: the supplied 128 GB unified-memory/2 TB GB10 Spark, central host models/inference and bounded ARM64 CPU labs. These are M2 proposals; no registry, factory, two-VM or Spark resource acceptance is claimed. [[Designs/AI4R Lab and CC Images]] and [[Designs/CC as Universal Component]] retain the idea's lineage.
'''
p.write_text(t, encoding='utf-8')

p = v / 'Designs/Design Library.md'
t = p.read_text(encoding='utf-8').replace('last_reviewed: 2026-10-20', 'last_reviewed: 2026-10-21', 1)
t = t.replace('| Lab-related existing design |', '| M1 sidecar and RSI design |')
marker = '## Your new design work'
t = t.replace(marker, '## M1 implementation prompt\n\n[[Resources/Coder Prompts/M1 Benchmark and CI]] is the portable filename-only handoff for existing M1 tooling. The M1 design-package remains the authority; the prompt is not an amendment or an M2 implementation instruction.\n\n' + marker, 1)
i = t.index('## Coordinated infrastructure design')
t = t[:i] + '''## M2 infrastructure reading route

| Question | Owning note |
|---|---|
| What should be developed, and in what order? | [[Designs/Lab Capsule and Factory Design Plan]] |
| How do storage, models, inference and retention fit the Spark? | [[Designs/Spark Shared Services and Storage]] |
| How is a lab VM provisioned and recovered? | [[Designs/VM Lab Infrastructure Design]] |
| How are CC images identified, invoked and checked? | [[Designs/Container Capability Capsule Design]] |
| How does each lab build and contribute candidates? | [[Designs/Per Lab Capability Factory Design]] |
| What changed after checking actual Docker mechanics? | [[Designs/Docker Architecture Review and Feasibility]] |

M2 notes are proposed designs, with shared Spark host resources and independent lab histories. Earlier M1 carrier-pilot and generic-host ideas remain history; they do not redefine this milestone or establish runtime evidence.
'''
p.write_text(t, encoding='utf-8')

p = v / 'Workstreams/M1 Design Code and Tests.md'
t = p.read_text(encoding='utf-8').replace('last_reviewed: 2026-10-20', 'last_reviewed: 2026-10-21', 1).replace('next_action: Reconcile available compiler candidates and current registered coding scope', 'next_action: Send the M1 benchmark/CI prompt and record the actual candidate and container evidence')
t = t.replace('## Immediate work', '''## Current coder handoff

The user reports a working implementation on another person's machine. That is user-supplied status, not a locally inspected acceptance result. [[Resources/Coder Prompts/M1 Benchmark and CI]] is the short prompt to complete the existing M1 platform benchmark runner and test runner with the designed sidecar/app connection.

The initial nine-run E1 feasibility pilot and the full S01–S06 benchmark pilot are distinct. The client-validation matrix governs the designed pre-merge check; the sidecar benchmark pilot does not gate the core M1 research workflow. Canonical detail stays in the maintained design package. M2 VM/factory/shared-inference work is tracked separately under [[Workstreams/Lab Infrastructure]].

## Immediate work''', 1)
p.write_text(t, encoding='utf-8')

p = v / 'Workstreams/Lab Infrastructure.md'
t = p.read_text(encoding='utf-8').replace('Next: shared contracts/topology, factory journey and native M1 reconciliation.', 'Next: Spark resource admission, ARM64 CPU guest qualification and M2 carrier/factory implementation.')
p.write_text(t, encoding='utf-8')
p = v / 'Active Stage.md'
t = p.read_text(encoding='utf-8').replace('The latest [[Sources/Prompts/2026-10-21-paper2agent-system-direction.txt|request]]', 'The earlier [[Sources/Prompts/2026-10-21-paper2agent-system-direction.txt|request]]')
t = t.replace('- [ ] Validate [[Resources/lab/README|the lab prototype]] on a running Docker host before assigning it real research work.', '- [ ] Use [[Designs/Lab Progression|the existing synthetic smoke evidence]] as bounded history; qualify actual M1 and Spark targets separately before assigning research work.')
t += '\n## Current M1 and M2 routes\n\n[[Resources/Coder Prompts/M1 Benchmark and CI]] is the current portable M1 tooling handoff. [[Designs/Lab Capsule and Factory Design Plan]] and [[Designs/Spark Shared Services and Storage]] own M2 sandbox/factory/resource planning. Working M1 code reported on another machine does not establish local runtime acceptance or a measured CC accuracy result.\n'
p.write_text(t, encoding='utf-8')

additions = {
    'Designs/Agent Reading and Freshness.md': '## M1 handoff and M2 sandbox route\n\nFor the current M1 platform benchmark/CI coder request, use [[Resources/Coder Prompts/M1 Benchmark and CI]] and its named design owners. For M2 infrastructure, use [[Designs/Lab Capsule and Factory Design Plan]] then [[Designs/Spark Shared Services and Storage]]. Do not import M2 host/factory changes into the M1 sidecar handoff.',
    'Sources/Implementation Intent.md': '## M1 coder prompt and notebook placement\n\nThe user asks for a small, portable filename-only M1 benchmark/CI prompt closely matching the existing design. It now lives at [[Resources/Coder Prompts/M1 Benchmark and CI]], separate from M2 architecture. The original root file was moved; coder-facing text is unchanged. The user-reported working M1 machine is a separate source of runtime evidence, not proof that this workstation or the Spark has passed qualification.',
    'Notebook Guide.md': '## Coder handoffs\n\nShort copyable implementation prompts live in [[Resources/Coder Prompts/README]]. Existing M1 implementation prompts link to maintained design owners; proposed M2 architecture stays under Designs. Copy a prompt body without its Obsidian YAML properties when sending it to a coder.',
    'Sources/Prompt Register.md': '- [[Sources/Prompts/2026-10-21-m1-benchmark-prompt-directions.txt|M1 benchmark prompt: short, filename-only and closely design-aligned]] — verbatim user-message blocks with capture labels.\n- [[Sources/Prompts/2026-10-21-working-m1-and-poc-request.txt|Working M1 reported on another machine]] — user report, not inspected runtime evidence.\n- [[Sources/Prompts/2026-10-21-notebook-organization-request.txt|Move files into the Obsidian library and align notes]] — exact visible request; prompt moved and reading routes reconciled.',
    'Activities/Activity Register.md': '- [[Activities/2026-10-21 Coder Prompt and Notebook Alignment|Coder prompt placement and notebook alignment]] — prompt moved into Resources, M1/M2 navigation consolidated, historical host status clarified.',
}
for name, section in additions.items():
    p = v / name
    p.write_text(p.read_text(encoding='utf-8').rstrip() + '\n\n' + section + '\n', encoding='utf-8')
note('Activities/2026-10-21 Coder Prompt and Notebook Alignment.md', 'activity-coder-prompt-notebook-alignment', 'Coder prompt placement and notebook alignment', 'Send the M1 prompt from Resources/Coder Prompts and retain actual implementation evidence', '''
Moved the standalone workspace-root M1 benchmark/CI prompt into [[Resources/Coder Prompts/M1 Benchmark and CI]]. The coder-facing body is byte-identical; only notebook YAML metadata was added. The source was removed by the requested move, not duplicated. The move receipt and pre-edit hashes are in Resources/review-batches/2026-10-21-notebook-alignment.

M2 design files were already correctly located in Designs and were not relocated. Consolidated their Home/design-index routes and linked the separate M1 handoff from the workstream, stage and agent reading guide. Clarified that working M1 code on another machine is user-reported, while local Docker receipts are dated/machine-specific. No code, acceptance evidence, original prompt or archived import was rewritten.

Preserved exact user requests and earlier note bytes. No coder was messaged, and no runtime, deployment or cleanup test was performed. Notebook validation is recorded separately in the batch receipt.
''', 'completed-documentation')
print('Moved prompt with body preserved; aligned notebook routes and milestone scope.')
