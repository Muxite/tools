from pathlib import Path
import hashlib,json,subprocess
v=Path(__file__).resolve().parents[3]
batch=Path(__file__).parent
paths=['Activities/Activity Register.md','Workstreams/CC Effectiveness.md','Designs/Capability Capsule Factory Feature.md','Activities/2026-10-22 Integrated Benchmark Operator.md','Sources/Prompt Register.md','Sources/capture-manifest.json','Resources/migration/validation.json']
receipt=[]
for name in paths:
 p=v/name
 if not p.exists():continue
 target=batch/'before'/(name.replace('/','__')+'.snapshot')
 target.parent.mkdir(parents=True,exist_ok=True)
 raw=p.read_bytes()
 with target.open('xb') as f:f.write(raw)
 assert target.read_bytes()==raw
 receipt.append({'path':name,'snapshot':target.relative_to(batch).as_posix(),'sha256':hashlib.sha256(raw).hexdigest()})
(batch/'before-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
captures={
'2026-10-23-capsule-branches.txt': 'ok go ahead and build these components onto a branch of the latest m1 while trying to avoid blocking existing work, so leave commits completely perfectly ready to use and merge, verify as best as you can. keep them seperate for each feature. diff branches to make mergability as good as possible. for each branch, give a very short but comprehensive description of the changes it makes (in terms of function, not implementation) and give them to me so i can show it.\n',
'2026-10-23-capsule-development-process.txt': 'after youve finsihed all that, document the dev process for capsules and think of how this shapes capability capsulef actory\n',
'2026-10-23-factory-agent-or-pipeline.txt': 'addition for later: tink if capability capsule factory it should be adaptive agent with clear rules, or fixed pipeline with agents inside, or both?\n',
}
manifest=json.loads((v/'Sources/capture-manifest.json').read_text(encoding='utf-8'))
for filename,content in captures.items():
 path='Sources/Prompts/'+filename
 raw=content.encode('utf-8')
 with (v/path).open('xb') as f:f.write(raw)
 manifest.append({'path':path,'sha256':hashlib.sha256(raw).hexdigest(),'capture_method':'exact visible individual user message as UTF-8 LF; terminal newline included; not a transport export','captured_date':'2026-10-23','original_message_timestamp':'unavailable; date denotes capture'})
(v/'Sources/capture-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
repo=v.parent/'AI4Research-Development/jiuwenswarm-m1-capsules'
refs=subprocess.check_output(['git','for-each-ref','--format=%(refname:short) %(objectname)','refs/heads/capsules','refs/heads/deployment-usability'],cwd=repo,text=True)
(batch/'branch-refs.json').write_text(json.dumps(dict(line.split() for line in refs.splitlines()),indent=2)+'\n',encoding='utf-8',newline='\n')
note='''---
id: capsule-branches-and-factory-direction
status: implemented-local-checks
source: Sources/Prompts/2026-10-23-capsule-branches.txt; Sources/Prompts/2026-10-23-capsule-development-process.txt; Sources/Prompts/2026-10-23-factory-agent-or-pipeline.txt
last_reviewed: 2026-10-23
next_action: Review and merge selected branches, then independently qualify checking assets and validate admitted capsules with a real model and available Docker host
---
# Capsule branches and factory direction

Implemented isolated, committed local branches in our AI4R implementation, based on latest checked remote `ai4r_M1` at `bfc30ba291c762d09f464c3e6a6c25f011826a33`. Source work is in `AI4Research-Development/jiuwenswarm-m1-capsules`. No push, central M1 merge, candidate admission or activation occurred. Other developers' research internals checkouts were not overwritten. The earlier deployment work is committed separately on `deployment-usability` as `e296d2b`.

## Functional handoff

| Branch | Function |
|---|---|
| `deployment-usability` | Repository-owned local/SSH benchmark build, stage, start, inspect, verified result retrieval and bounded temporary-resource expiry |
| `capsules/planner-foundation` | Opt-in typed DAG policy, explicit evidence coverage, optional candidate discovery and protected calibration integration; original default POC workflows preserved |
| `capsules/generalist-m1` | Low-trust fallback producing frozen-task-bound files/data and bounded pure expression results, with gap provenance and checks |
| `capsules/table-normalize-m1` | Explicit JSON/CSV parsing preserving original values, types and row/column order |
| `capsules/calculate-m1` | Explicit decimal count/sum/mean/min/max with independent recomputation |
| `capsules/markdown-report-m1` | Deterministic Markdown artifact/manifest from supplied content, retaining evidence and trust |
| `capsules/development-guide` | Capsule authoring, testing, qualification and release guide; factory design implications |
| `capsules/m1-integration-check` | Clean combined merge rehearsal plus actual utility-composition test |

Foundation first; each optional capsule has its own disjoint package/docs/tests and can merge independently. Deployment is independent. Exact branch identities are captured in `Resources/review-batches/2026-10-23-capsule-branches/branch-refs.json`. The convenience integration branch contains selected features but does not replace maintained M1.

## Definition and verification choices

Read historical Generalist sources through [[Designs/CC History]] before implementation: the original report and workshop schema v2.10b §4.14 describe a small declaration, frozen task intention and lowest trust. They are historical motivation, not current runtime authority.

The user-authorized M1 extension deliberately differs from the earlier Generalist deferral and D20/D24 restriction on task criteria hidden in output. Generalist explicitly publishes a host-authenticated frozen task projection in its exact output. Host checks compare objective, requirement IDs, parent/policy/attempt identity and actual expression result before the fixed semantic task-alignment criterion runs. No original input, worker conversation or private test suite is added to reviewer context. Specialists retain ordinary declaration/output review. The Planner cannot choose arbitrary judge code, waive checks or grant permissions. Low trust is preserved through utilities; passing is not specialist certification or proof of scientific truth.

The new DAG policy permits any compatible acyclic order with exact pins, typed dependencies, coverage, budgets/effects and one attempt per node. Scientific work still requires Scientific Evaluation and scientific Delivery. The node cap is 12 because the current public schema permits 12, refining the earlier suggested 16; Generalist is capped at two nodes. A generic packet is an interoperability envelope, not implicit compatibility with every scientific port. Operation settings must be supplied and actual inputs validated; missing adapters/capabilities remain blocked.

Generalist code files are generated artifacts. Actual execution is limited to a bounded pure JSON expression language using Python syntax, with no eval/exec/imports, loops, arbitrary Python, network, package installation or ambient host access. This is a deliberate narrow first implementation; a broader native agent executor needs a separately designed isolation profile. Capsule modules currently ship inside the `ai4r` image; container-per-capsule and factory automation remain M2 work.

## Actual evidence and remaining work

A clean combined merge was tested from a fresh committed Git checkout: **103 passed on Windows; 102 passed and 1 skipped on Ubuntu 24.04 WSL**. The skip is Linux Compose rendering because that plugin was unavailable. Windows real Compose rendering passed without a daemon. The focused suite covers deployment safety, capsule functions/negatives, frozen tasks, provenance/taint, typed graph checks, ordinary gates/admission boundaries and existing sequential runner collection. A real deterministic CSV → decimal calculation → Markdown trial used exact registered check assets and retained original files. Model responses in Generalist tests were fixtures.

Original compiler/scientific and versioned PDF release catalogs reproduce from fresh bytes. Explicit Git attributes resolve cross-platform source pinning while preserving the legacy frozen CRLF review-instruction bytes. Focused Ruff checks, Git whitespace and repository documentation links passed. This was not the entire repository test suite.

Independent protected calibration, human admission/activation, a live app DAG, Docker builds/two-container campaigns, actual SSH/Docker, unattended schedule activation, ARM64 and native Spark remain unrun. Docker Desktop's ingest-socket startup error was retained as a limitation; no unrelated host reset or deletion was performed. Preparing or merging candidates grants no standing.

## Factory conclusion

Recommend **both**: a fixed durable production lifecycle with bounded adaptive agents inside authoring stages. Fixed control owns source/dependency identity, declarations, independent checks, stage gates, budgets, leases, retries/cancellation, qualification and promotion. Adaptive workers handle repository differences and public development feedback within finite permissions/budgets. They cannot see private held-outs, weaken checks, admit their own products or mutate a live graph. This is a proposal, not implemented factory automation.

The factory produces immutable candidates. RSI improves an existing declared capability with lineage; both may share builders/evaluators, but neither is the admission authority. Durable labs can propose useful local results to shared AI4R without automatic promotion. Build on development machines/CI; use Spark primarily for benchmark execution, with shared model weights/inference and bounded owned scratch. The existing protected results/inputs/models/credentials/rollback policy and seven-day temporary-only expiry remain relevant.

## Repository reading route

- [Development process](../../AI4Research-Development/jiuwenswarm-m1-capsules/docs/capsules/development.md)
- [Factory alternatives and proposed lifecycle](../../AI4Research-Development/jiuwenswarm-m1-capsules/docs/capsules/factory-direction.md)
- [Branches and functional descriptions](../../AI4Research-Development/jiuwenswarm-m1-capsules/docs/capsules/branches.md)
- [Actual validation and unrun checks](../../AI4Research-Development/jiuwenswarm-m1-capsules/docs/capsules/validation.md)
- [Design-package entry](../../AI4Research-Development/jiuwenswarm-m1-capsules/docs/architecture/design-package/capsule-development.md)
'''
(v/'Activities/2026-10-23 Capsule Branches and Factory Direction.md').write_text(note,encoding='utf-8',newline='\n')
updates={
'Activities/Activity Register.md':'\n- [[Activities/2026-10-23 Capsule Branches and Factory Direction|Capsule branches and factory direction]] — separate committed features, fresh-checkout Windows/Linux checks, explicit qualification limits and hybrid factory recommendation.\n',
'Workstreams/CC Effectiveness.md':'\n## October 23 implementation candidates\n\n[[Activities/2026-10-23 Capsule Branches and Factory Direction]] records Generalist and three deterministic utilities on independent branches, plus an opt-in typed DAG policy. These are development candidates with local checks, not measured improvements or admitted capabilities. Generalist has an explicit host-authenticated task projection exception; specialist semantic review remains declaration/output-only. Real comparative/held-out evidence and admission remain separate.\n',
'Designs/Capability Capsule Factory Feature.md':'\n## October 23 development-process implication\n\n[[Activities/2026-10-23 Capsule Branches and Factory Direction]] records user-requested capsule modules and the proposed factory choice: **fixed durable lifecycle with bounded adaptive agents inside stages**. Keep source/dependency identity, declaration/check freezing, budgets, durable evidence, qualification and promotion under protected control; let agents adapt authoring/repository work within finite grants. Current capsule branches implement no factory automation or per-capsule containers. Generalist task-bound checking is a named M1 extension on candidate branches; the factory remains M2.\n',
'Sources/Prompt Register.md':'\n- [[Sources/Prompts/2026-10-23-capsule-branches.txt|Separate capsule branches and merge-ready commits]], [[Sources/Prompts/2026-10-23-capsule-development-process.txt|Document development process]], and [[Sources/Prompts/2026-10-23-factory-agent-or-pipeline.txt|Factory agent/pipeline alternatives]] — exact individual captures; interpreted in [[Activities/2026-10-23 Capsule Branches and Factory Direction]].\n',
}
for name,addition in updates.items():
 p=v/name;s=p.read_text(encoding='utf-8');s=s.replace('last_reviewed: 2026-10-21','last_reviewed: 2026-10-23',1).replace('last_reviewed: 2026-10-22','last_reviewed: 2026-10-23',1)
 p.write_text(s+addition,encoding='utf-8',newline='\n')
p=v/'Activities/2026-10-22 Integrated Benchmark Operator.md';s=p.read_text(encoding='utf-8').replace('Changes remain uncommitted and unpushed;', 'The October 22 implementation was committed October 23 as `e296d2b` on `deployment-usability` and remains unpushed;').replace('last_reviewed: 2026-10-22','last_reviewed: 2026-10-23',1)
p.write_text(s+'\nOctober 23: [[Activities/2026-10-23 Capsule Branches and Factory Direction]] records the separate capsule branches and combined fresh-checkout verification. Connected Docker/Spark checks remain unrun.\n',encoding='utf-8',newline='\n')
print('Captured',len(captures),'messages; snapshotted',len(receipt),'existing files; recorded',len(refs.splitlines()),'branch refs')
