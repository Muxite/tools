# 20261113 Software Factory Demo Companion Revision 2 prepresentation

Extracted text for search. Slide geometry, diagrams and visual meaning remain in the original deck. This extraction is not a new presentation or a visual review.


## Slide 1

What we did: a traceable engine modification
We packaged engineering guidance as Capability Capsules (CCs), applied it through JiuwenSwarm,
and recorded the source, build and evaluation chain.
Operator task
Frozen contract
Agent + capsules
Inspect and integrate
Modified llama.cpp
Commit 885eec82
Execution lab
Build + one screen
task + constraints
agent applies patches
explicit build/run requests
Build receipt
3445e556 → image a15f04f0
Screen bbc85611
Frozen stdout identity passed
Decision + report
Fill engagement supported
Receipt names the image; screen evidence names the same image; the agent records a bounded decision.
JIFAN NOW
Native inspection and verified graph replay
SATAY HISTORY
Completed fill-only build and correctness screen
Separate evidence: J-OM13 measured another image. Spark remains the intended deployment target.

Speaker-note text (package numbering):



## Slide 2

Why it matters: reusable knowledge with testable evidence
Development constraint
An 8 GB Jetson ran a 22.36 GB model file. CPU expert computation can wait for mapped weight pages from storage.
Selected expert pages absent
Storage read / page fault stalls computation
Prepare needed pages before expert math
What becomes reusable
Mechanism and applicability guidance
Source prerequisites and exact patches
Runtime switches and engagement checks
Frozen workload, image identity and raw outputs
Acceptance rules and rollback instructions
Separate historical result
841.5 → 711.4 ms/token
15.5% lower decode time
18.3% higher reciprocal throughput
J-OM13: image 1274abb8, fill + predictive reads,
4 repeats per headline arm. This is not the fill-only proof.
Demonstrated: packaging and evidence-linked application. Engineering-time savings and Spark gains remain unmeasured.

Speaker-note text (package numbering):



## Slide 3

How the CCs change llama.cpp
BUILD TIME: agent applies materials, then the builder produces the recorded image
mmap_advice
Patch 01: mapping policy
Runtime mode OFF
router_prefetch
Patch 02: CPU scheduler hook
Optional advice mode OFF
expert_fill
Patches 03–05: range fill / phase / diagnostics
Fill ON; diagnostics OFF
Source prerequisites retained
Source 885eec82 → build 3445e556 → image a15f04f0
Image contains the complete runtime lane below
RUNTIME: CPU expert path under -cmoe
Router top-k
Host selected IDs
ADDED CPU callback
Synchronize preceding work
ExpertFiller
mincore → parallel pread
Wait for missing reads
Existing CPU kernels
MUL_MAT_ID
Consume mapped weights
Loader/context changes retain file offsets and expert ranges. Buffered reads populate Linux page cache.
The callback returns after demand fill completes, then expert computation proceeds and generation continues.
Demand fill blocks the caller. Workers parallelize I/O, not that layer’s compute.
The proof keeps CPU/CUDA math kernels unchanged and does not move CPU experts to GPU.

Speaker-note text (package numbering):



## Slide 4

JiuwenSwarm and the siminfeng lab
Operator
Task + test contract
JiuwenSwarm factory
Agent + CC runtime
Task graph + evidence store
Execution lab
Repository: siminfeng
Queue / build / run / ABBA
llama.cpp image on hardware
Fixed workload + instrumentation
Evidence for the next decision
Commits, image identity, output, measurements
The lab keeps hardware execution and research records separate from the agent loop.
“siminfeng” is the repository name you will see in real file paths.
The task graph records dependencies; explicit job submissions execute the work.
REFERENCE 4   Video 00:06   Sources: REPOS.md

Speaker-note text (package numbering):



## Slide 5

Task input and constraints
Apply demand fill to plain llama.cpp cf34d3113.
Integrate expert_fill plus mmap_advice and router_prefetch prerequisites; keep prerequisite runtime switches off.
Build once, run one correctness screen, inspect engagement and report.
The operator prohibited ABBA comparisons, extra components and tuning.
REFERENCE 5   Video 00:12   Sources: task.json

Speaker-note text (package numbering):



## Slide 6

Frozen correctness contract
qwen36-quick-v1: fixed p0-short.txt prompt, 32 generated tokens, temperature 0, seed 1, context 4096.
The candidate must reproduce the reference stdout byte for byte.
The reference image, run ID and stdout hash are fixed. Model SHA-256 is null in the contract, although the task records one.
This is a narrow correctness screen. The 12-token response captures and 64-token historical experiment are separate workloads.
REFERENCE 6   Video 00:25   Sources: qwen36-quick-v1.json; task.json; 1-plain.typescript; spec.json
Actual workload arguments
llama-completion -m /om/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf -f /om/prompts/p0-short.txt -n 32 -c 4096 --temp 0 -s 1 -no-cnv -ngl 99 -lm mmap -cmoe -lv 4
Full recorded 32-token stdout
The three main parts of a computer are the CPU, the memory, and the input/output devices. The CPU is the brain of the computer, and it is responsible for executing instructions. The memory is

Speaker-note text (package numbering):



## Slide 7

A capsule can contain tools, materials or both
A Capability Capsule (CC) can expose tools, package materials, or do both.
engine.expert_streaming
Tools: applicability and engagement
Materials: guide, source map, ontology and component definitions
factory.components.expert_fill
Materials only: component definition and three patches
The agent applies those patches to llama.cpp before building an image.
Actual expert_fill capsule declaration
cc: '2'
id: factory.components.expert_fill
version: 1.1.0
materials:
  component:
    kind: component
    path: component.yaml
  patch_03:
    kind: component
    path: 03-expert-fill.patch
  patch_04:
    kind: component
    path: 04-fill-phase.patch
  patch_05:
    kind: component
    path: 05-fill-diag.patch
REFERENCE 7   Video 00:44 / 00:55   Sources: cc.yaml; cc.yaml; cc.yaml

Speaker-note text (package numbering):



## Slide 8

Capsule inventory and recorded use
CALLABLE CAPSULES (5)
factory.builder
factory.engine_inspector
factory.evidence
factory.lab_client
engine.expert_streaming
OTHER MATERIAL CAPSULES (3)
factory.integration_skill
factory.methodology_ab
factory.engine_component
COMPONENT MATERIAL CAPSULES (8)
factory.components.
  expert_fill
  mmap_advice
  router_prefetch
  expert_pregate
  expert_readiness
  inflight_join
  phase_stats
  thread_names
Proof: three source components integrated; only expert_fill enabled.
J-OM13: a different image with fill + predictive reads. Catalog membership alone is not execution evidence.
REFERENCE 8   Video 00:34   Sources: Current 16 cc.yaml declarations at fe88a206; STORY.txt; result.json; spec.json

Speaker-note text (package numbering):



## Slide 9

Engine ontology and work-node vocabulary
Engineering work node
kind / state / depends_on
inputs / attempt_ids / evidence_ids
engine_slice
expert_weight_readiness
Engine-system ontology
L4: router, selected experts, expert execution
M: weight ranges, read requests, readiness,
page cache and memory budget
Component definition
implements
modifies_region
quantities
All ten recorded work nodes reference the same engine slice. They perform different engineering actions.
The vocabulary validates names and relationships. It does not derive the workflow or prove that edits satisfy the ontology.
REFERENCE 9   Video 01:10 / 01:17   Sources: NODE-EXAMPLE.md; taskgraph.py; ONTOLOGY.yaml

Speaker-note text (package numbering):



## Slide 10

Task graph revisions and execution
RECORDED WORK NODES
inspect                 done
applicability           done
baseline-build          cancelled
baseline-measure        cancelled
integrate               done
candidate-build         done
candidate-measure       cancelled
candidate-screen        done
accept                  done
report                  done
REVISION CHECKPOINTS
1  Initial suggested workflow
2  Remove unauthorized baseline/A/B work
3  Integration complete; build ready
4  Build complete; screen ready
5  Screen, decision and report complete
Ready frontier identifies eligible work.
The agent/controller must submit jobs.
The video opens a complete candidate-build node with its exact inputs and evidence links.
Work-node schema ≠ engine architecture. Some decision/integration nodes have capability: null.
Their engine_slice still identifies the target. No requires_evidence fields were added to these historical nodes.
REFERENCE 10   Video 01:30 / 01:35   Sources: taskgraph.py; 20261113 Satay Verified Proof Task Graph prepresentation.json

Speaker-note text (package numbering):



## Slide 11

llama.cpp architecture and intervention
Prompt + generation loop
llama_context / process_ubatch
Model graph
Attention / normalization / router
Top-k expert selection
ggml backend scheduler
Split work by backend
Copy split inputs
CPU expert path (-cmoe)
Host expert IDs + activations
First expert MUL_MAT_ID
ADDED CPU callback
Synchronize earlier work
Prepare selected expert pages
GPU backend
Other eligible offloaded work
Existing CPU expert kernels
Read mapped weights; compute expert output
Changed: loader/context metadata, scheduler hook and filler. CPU/CUDA math kernels remain unchanged.
REFERENCE 11   Video 01:42   Sources: excerpt-1-ggml-backend-hook.diff; full.diff; SOURCE-MAP.md sections 1–4

Speaker-note text (package numbering):



## Slide 12

Demand fill before CPU expert computation
Selected expert IDs + tensor file offsets
Merge exact GGUF ranges; check page residency
Worker threads read missing pages with pread
Caller waits; CPU then consumes mapped weights
mmap connects tensor addresses to file pages.
Buffered reads populate Linux’s page cache.
Demand fill parallelizes I/O but blocks before expert computation.
Predictive reads in the separate historical engine can prepare later-layer pages earlier.
REFERENCE 12   Video 01:42   Sources: full.diff; SOURCE-MAP.md sections 3–5; component.yaml

Speaker-note text (package numbering):



## Slide 13

Recorded build and image identity
Build request pins source commit 885eec8245e20d2c864227d3a05a4bdaee7fc55d and target jetson-orin.
Attempt 3445e556 reaches succeeded. The receipt names image a15f04f0 and hashes its preparation, request and build record.
This is recorded Satay execution. On Jifan we inspect these files and replay the graph.
The response segment replays complete original terminal captures. All playback gaps are capped at 0.5 seconds, including response gaps. It demonstrates recorded functionality only.
REFERENCE 13   Video 01:55 / 02:05   Sources: request.json; attempt.json; receipt.json; *.typescript

Speaker-note text (package numbering):



## Slide 14

Correctness and component engagement
Frozen 32-token stdout identity passed. Exit 0, no OOM and no watchdog trip.
Component-specific stderr and engagement inspection establish demand-fill activation.
Two broader instrumentation checks were unavailable: effective-config output and xfill thread names. Those absent features do not become successful checks.
The screen recorded 898.36 ms/token. One run does not establish a speed improvement.
REFERENCE 14   Video 02:43   Sources: evaluations.json; result.json; stdout.txt; README.md
Recorded component activation lines
1.22.898.093 I expert_fill: active threads=16 chunk_kib=2048 random=decode files=1
1.37.243.054 I expert_fill: random advice applied at decode
Activation evidence does not imply a comparative speed improvement.

Speaker-note text (package numbering):



## Slide 15

Historical performance: separate image
J-OM13 used image 1274abb8 with fill + predictive reads.
This is a different image from the fill-only proof.
Four repeats per headline arm: 841.4975 to 711.425 ms/token.
15.5% lower decode time and 18.3% higher reciprocal throughput.
All 12 outputs agree. The third factory_t4 arm remains in the record.
REFERENCE 15   Video 03:05   Sources: spec.json; REPORT.md; verdict.json
Per-run decode time (ms/token)
base       850.81  820.94  854.65  839.59
factory    698.57  715.45  720.55  711.13
factory_t4 660.86  655.93  662.16  658.08
Headline: base vs factory.
Third arm changes CPU thread setting.
Recorded conditions
Jetson Orin Nano Super 8 GB
Qwen3.6-35B-A3B UD-Q4_K_XL
64 tokens, context 4096, temperature 0, seed 1
CPU experts (-cmoe), mmap weights
Base: plain cf34d311
Factory: fill + pregate, K 8, lookahead 1
Warm cache; initial residency unrecorded

Speaker-note text (package numbering):



## Slide 16

Demonstrated workflow and Spark transfer
Recorded Satay evidence links task, component material, source commits, build image, correctness output and decision.
Jifan demonstrates that inspection and verified history replay run from the matched factory source.
Spark remains the target. Inspect its constraints and establish an unmodified baseline before selecting interventions.
Use the indexed reference deck for full contracts, all 16 declarations, schemas, inputs, outputs and per-run results.
REFERENCE 16   Video 03:09   Sources: 20261113 Jifan Source Verification prepresentation.json; 20261113 Satay Evidence Coverage prepresentation.json

Speaker-note text (package numbering):



## Slide 17

Questions about the claims
Did the fill-only proof deliver the 15.5% improvement?
No. a15f04f0 passed a correctness/engagement screen. J-OM13 used image 1274abb8 with fill + predictive reads.
Does 32-token output equality prove general correctness?
No. It checks one frozen workload. It does not establish broad model accuracy or all-input equivalence.
Did all 16 capsules execute?
No. The proof integrated three source components. Only fill was enabled. Inventory and declared resources are not invocation evidence.
Does the ontology plan work or prove code edits are valid?
No. It validates named relationships and records targeting. The agent chooses actions; jobs execute explicit submissions.
Was there a new build or inference run on Jifan or Spark?
No. Jifan runs native inspection/replay. Build and inference evidence comes from historical Satay execution. Spark transfer is future work.

Speaker-note text (package numbering):



## Slide 18

Questions about execution, failure and evidence
What proves a build finished?
Succeeded attempt 3445e556 plus its receipt and immutable image identity. A submit acknowledgment alone is not completion.
What if an I/O worker fails or the process crashes?
This proof demonstrates the successful path. It does not establish worker-loss, timeout, exactly-once or crash-recovery guarantees.
Does demand fill overlap that layer’s expert computation?
No. The caller waits for demand reads. Separate predictive reads can prepare later-layer pages earlier.
How strong is model provenance?
The task contains a model hash, but the frozen contract’s model hash is null. The binding remains incomplete.
Can the historical gain be generalized?
Only to the recorded comparison. Cache residency, workload and hardware matter. No isolated 80% cache penalty, productivity gain or Spark result is established.

Speaker-note text (package numbering):


