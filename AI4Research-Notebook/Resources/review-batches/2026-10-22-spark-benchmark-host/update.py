from pathlib import Path
import hashlib,json
v=Path.cwd()/"AI4Research-Notebook"; b=v/"Resources/review-batches/2026-10-22-spark-benchmark-host"
files=["Workstreams/Lab Infrastructure.md","Designs/Durable Project Labs.md","Designs/Spark Shared Services and Storage.md","Designs/Agent Reading and Freshness.md","Activities/Activity Register.md","Sources/capture-manifest.json"]
sha=lambda x:hashlib.sha256(x).hexdigest(); rec=[]
for n in files:
 d=(v/n).read_bytes(); p=b/"before"/(n.replace('/','__')+'.snapshot');p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(d)
 assert sha(p.read_bytes())==sha(d);rec.append({'path':n,'snapshot':str(p.relative_to(v)),'sha256':sha(d)})
(b/'before-receipt.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8')
msg="heres whats happening now, we wont be doing much development on the dgx spark, its just hardware for running benchmarks really, so we need a system to efficiently build our images, bring the inputs and outputs stuff onto dgx spark, let the spark run it, be able to inspect it, and then bring the data back to our machines. put that consideration in an update notes. we will need to plan the sandbox. the prompt for benchmarker has been sent already, just a cosndieration for next prompts.\n"
cap='Sources/Prompts/2026-10-22-spark-benchmark-host-direction.txt'; data=msg.encode()
with (v/cap).open('xb') as f:f.write(data)
mf=v/'Sources/capture-manifest.json'; m=json.loads(mf.read_text(encoding='utf-8'));m.append({'path':cap,'sha256':sha(data),'capture_method':'exact visible user message as UTF-8 LF; terminal newline included; not a transport export','captured_date':'2026-10-22'});mf.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='''---
id: spark-benchmark-host-direction
status: current-direction
source: Sources/Prompts/2026-10-22-spark-benchmark-host-direction.txt
last_reviewed: 2026-10-22
next_action: Use this split in future Spark deployment and M2 sandbox prompts; validate transfer paths on the actual host
---
# Spark as a benchmark host

The DGX Spark is primarily benchmark execution hardware. Most application development and image-building should happen on development machines or an appropriate build service. Prepare only the required versioned images and campaign inputs for Spark, run and inspect tasks there, then bring results and observations back to development machines for review.

This updates the operating assumption for future prompts. The already-sent benchmark-runner prompt remains as issued; image transfer or remote-host operation has not been implemented or tested.

## Intended flow

1. Build and identify app and runner images away from Spark where practical. Record source commit, architecture, image tags and immutable digests; verify Spark compatibility.
2. Deliver only required images/dependencies to Spark through a reachable registry or portable OCI archive. Prefer incremental content-addressed transfer; avoid copying full source trees and build caches for routine runs.
3. Stage each campaign's permitted cases and inputs in an owned Spark location. Keep inputs read-only and held-out material access-controlled.
4. Run with isolated workspaces and persistent campaign output. Inspect readiness, live progress, logs, resource observations and artifacts on Spark.
5. Transfer results, observations and provenance to a user-selected development-machine location. Verify manifests, sizes and hashes; support resume and retain Spark data until the receiving copy verifies.
6. Bound storage on both ends. Reclaim only verified owned staging and disposable cache/image data. Never globally prune or implicitly delete source inputs or accepted results.

## Sandbox planning

Plan the complete build-to-execution-to-review lifecycle: image provenance and architecture, authenticated image delivery, campaign input staging, run isolation, host inspection, result export, transfer recovery, ownership and retention. Spark can be a bounded execution host without being the authoritative home for source development or durable project data. Durable lab identity and project state need an explicit storage and backup design separate from disposable benchmark execution state.

The next sandbox design should choose transfer mechanisms, authentication, directory ownership, quotas, resumable copy and evidence-retention rules. Keep the first slice practical: move one image pair and one campaign end-to-end, run it, inspect artifacts, return them with verified integrity and survive container removal.

## Prompt routing

Use [[Designs/Durable Project Labs]] and [[Designs/Spark Shared Services and Storage]] for M2 sandbox planning. Future Spark prompts should include remote image/input staging and result return. Keep [[Resources/Coder Prompts/benchmark-runner]] as the already-sent app-testing handoff; this note does not change its scope or implementation status.
'''
(v/'Activities/2026-10-22 Spark Benchmark Host Direction.md').write_text(note,encoding='utf-8')
def add(rel,anchor,text):
 p=v/rel;s=p.read_text(encoding='utf-8');assert anchor in s,rel;p.write_text(s.replace(anchor,text+anchor,1),encoding='utf-8')
add('Workstreams/Lab Infrastructure.md','## Immediate Spark benchmark setup\n','## Spark as a benchmark host\n\n[[Activities/2026-10-22 Spark Benchmark Host Direction]] records the updated direction: build images and prepare campaign inputs on development machines or a build service, stage only required images and inputs on Spark, run and inspect benchmarks there, then transfer verified results back. Spark is execution hardware, not the main development workstation. The benchmark prompt was already sent and remains unchanged; apply this to future Spark prompts and M2 sandbox planning. No transfer workflow has been tested.\n\n')
add('Designs/Durable Project Labs.md','## Durability within the Spark budget\n','## Development-to-benchmark-host lifecycle\n\nSee [[Activities/2026-10-22 Spark Benchmark Host Direction]]. Treat Spark as execution hardware: prepare versioned images and campaign inputs elsewhere, stage them for a run, inspect execution/artifacts on Spark, and return verified results. Sandbox design must cover compatible image builds, authenticated transfer, read-only inputs, isolated outputs, resumable export and quotas on both ends. Durable lab state needs an explicit home and backup policy; benchmark storage is not implicitly the durable project store. This is planning only.\n\n')
add('Designs/Spark Shared Services and Storage.md','## Hardware changes the deployment\n',"## Spark's benchmark-host role\n\nRoutine development and image builds should happen on development machines or a suitable build service where practical. Future deployment should move only versioned, architecture-compatible images and selected inputs to Spark, support inspection there, and return verified outputs/provenance to development machines. Count transfer staging and temporary overlap against capacity; keep durable project data under explicit storage/backup policy. The sent benchmark prompt is unchanged; this flow is untested. See [[Activities/2026-10-22 Spark Benchmark Host Direction]].\n\n")
add('Designs/Agent Reading and Freshness.md','## Long-lived lab direction\n','## Spark benchmark-host direction\n\n[[Activities/2026-10-22 Spark Benchmark Host Direction]] is the latest operating consideration for future Spark and M2 sandbox prompts: build/prepare on development infrastructure, transfer selected images and inputs to Spark, execute and inspect there, then return verified data. The sent benchmark-runner prompt remains unchanged; this is not implementation evidence.\n\n')
add('Activities/Activity Register.md','# Activity log\n','- [[Activities/2026-10-22 Spark Benchmark Host Direction|Spark as benchmark execution host]] — recorded build/input staging → Spark execution/inspection → verified result return for future prompts and M2 sandbox planning; no host transfer or run performed.\n\n')
assert all(sha((v/r['snapshot']).read_bytes())==r['sha256'] for r in rec)
print('Captured source and updated five routed notes; verified all before-snapshot hashes.')
