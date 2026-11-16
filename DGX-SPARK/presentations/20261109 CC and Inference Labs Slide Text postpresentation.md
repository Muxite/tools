# 20261109 CC and Inference Labs postpresentation

Extracted text for search. Slide geometry, diagrams and visual meaning remain in the original deck. This extraction is not a new presentation or a visual review.


## Slide 1

Software Factory and its lab boundary
One Factory coordinates intent, reusable capabilities, builds and retained evidence through its Lab Manager.
Design proposal • Muse Spark Open on DGX Spark • asynchronous jobs; independent lab deployments
01
Software Factory
Plaintext input
model • hardware
environment limits
Intent compiler
seek missing facts
Intent IR + ontology
Contract compiler
requirements • gates
verification rules
intent
Intent IR
CC registry
tool / skill CCs
component CCs
Builder swarm
plan • code • assemble
invoke tools / integrate parts
Release image
engine + build manifest
identified model/config
capabilities
build
contract + ontology
Knowledge + telemetry
contracts • releases • raw evidence • assessments
Lab manager
queue • admit • track jobs
release refs + playbook
submit / job ID
evidence
findings / next change
Lab execution service
Lab executor
worker now; agent optional
separate management container
Incus experiment
private Docker + engine
GPU / tools / bounded writes
dispatch +
release refs
status +
artifacts
provision / run / stop
results
Recommendation: deterministic execution through Lab Manager. Factory agents can analyze evidence.

Speaker-note text (package numbering):

The single Software Factory boundary contains all intent/contract compilation, CC registry, Builder, release metadata, durable knowledge/telemetry and Lab Manager. The Lab execution service is external and contains a separate management container plus disposable Incus experiment. Every visible external job-control/evidence path goes through Lab Manager; Builder submits an asynchronous identified experiment request and receives a job ID rather than holding a remote process call open. Manager admits and dispatches bounded jobs, receives status/artifact references, and commits the result to Factory knowledge. The worker can fetch image/model/tool artifacts by immutable references under scoped access; the diagram does not require Manager to proxy all artifact bytes. No unrestricted Incus socket is handed to an LLM. Recommended starting worker is deterministic API/state machine executing approved playbook branches. Agent reasoning can analyze evidence inside Factory and request another permitted diagnostic job. An optional local diagnostic agent can be added later without changing job identity, admission or recovery. This recommendation replaces a mandatory autonomous lab LLM in the first implementation, not the need for trusted platform actuation. One Spark serializes scored/profiled GPU work; multiple independent lab hosts can execute admitted jobs concurrently. The engine remains its own release/runtime, CCs provide reusable tools/components, and the lab never edits source. The release-to-manager path supplies immutable references, playbook and constraints. Fundamental requirement changes remain governed by contract approval policy.
Sources
https://github.com/Stellven/jiuwenswarm/tree/a838b97048b2c561212ccfa82b5d414c39359dc9
https://linuxcontainers.org/incus/docs/main/reference/devices_gpu/
POST-WORKSHOP DESIGN ALIGNMENT
The top-level product contract is separate from reusable capability capsules and from the released engine image. Tool CCs support the workflow; component CC assets may be incorporated into engine code. The engine has its own runtime, without an engine CC wrapper. Lab manager belongs to Software Factory. Lab executor and protected client run in a separate management container outside the disposable Incus experiment. Durable job/stage checkpoints and evidence receipts remain in Factory. A failed attempt is restarted with a new generation after confirmed stop, not resumed as a partially scored run. Runtime settings may change only within the permitted contract and retain configuration identity; source changes require a rebuilt image.
Source: supplied AI4Research Workshop Key Takeaways (Nov6) and post-presentation directions.
MANAGER / EXECUTOR RECOMMENDATION
Proposed simplest first implementation: the Factory exposes one asynchronous Lab Manager API. Builder submits identified releases/playbooks and receives a durable job ID, then continues other work. A deterministic worker in a separate management container polls/claims assigned jobs, emits heartbeat/stage events and returns artifact manifests/results through Manager. No separate public worker API or message broker is required initially. Manager owns admission, cancellation, generation/lease and durable status; trusted platform actuation owns narrowly allowed Incus operations. The worker follows permitted playbook stages and bounded retries. Agent reasoning can remain in Factory report analysis and request another bounded diagnostic job; a resident LLM is optional, not required for execution or recovery. All prior references to lab-agent judgment describe that optional future role. One scored or profiling GPU job at a time per Spark; independent qualified hosts can run in parallel. Polling can be replaced by other transport later without changing job semantics. At-least-once delivery requires idempotent claim/start/export, generation fencing and confirmed stop before retry; do not promise exactly-once GPU execution. A cancellation acknowledgement is distinct from a stop request. Manager gateway carries control and evidence references; scoped artifact fetch/upload may carry large bytes directly without exposing another experiment API. Manager may be a module in the existing Factory service with its existing database. Worker may include the Incus adapter and profiler wrappers as modules; a protected client can be a subprocess in the management container. No separate network actuator is required. Trusted worker credentials remain scoped and unavailable to reasoning agents or the engine. Factory job IDs cover full experiments and differ from Incus operation IDs. After event disconnection, reconcile actual operation/instance state because events need not replay. Release GPU admission while waiting for agent reasoning. This is a recommendation for discussion, not a claimed deployed or accepted implementation.

## Slide 2

CCs are reusable capabilities, distinct from the release contract
The contract defines what the product must do. CCs supply tools and functional components used to realize it.
Workshop distinction • existing CC fields remain applicable to capability units, not the whole inference-engine contract
02
Source material
paper • repository • code
capability requirements
CC production
reuse Factory workflows
source-specific adapters
Reusable CC
declaration + implementation + materials
Registry
discover / reuse
adapt
verify / publish
index
CC describes
What this enables
does / takes / gives
One capability with explicit behavior and finite inputs / outputs.
needs / changes
Resource requirements and scoped effects, applied through actual grants.
bindings / materials
Executable implementation plus skills, references, examples and component assets.
Composition
Use several CCs in a temporary workflow, or publish a tested Composite CC.
Tool CCs operate the production line. Component CCs contribute implementation to the product.
CC Factory is a capability-producing function that can reuse the Software Factory workflow and orchestrator.

Speaker-note text (package numbering):

A CC is a reusable capability unit, not the top-level contract or final application image. One implementation image may host several callable capabilities. Component CCs can provide source/library/kernel assets to incorporate into the inference engine. This is a proposed use of current materials and bindings, not a new schema kind. Tool CCs execute during building, testing or analysis. CC production converts heterogeneous sources through shared Factory workflow machinery plus source-specific agents/adapters. CC2CC includes temporary workflow composition and publishing an identified reusable Composite CC after checks. Ordinary invocation/composition is distinct from creating a durable new capsule. The exact component incorporation interface needs qualification; dependencies, licenses, ABI and build identity belong in build receipts. The earlier whole-product request-CC narrative is superseded. Current partial CC requests remain useful for requesting a missing capability implementation. No schema migration is implied.
Sources
https://github.com/Stellven/jiuwenswarm/tree/a838b97048b2c561212ccfa82b5d414c39359dc9
POST-WORKSHOP DESIGN ALIGNMENT
The top-level product contract is separate from reusable capability capsules and from the released engine image. Tool CCs support the workflow; component CC assets may be incorporated into engine code. The engine has its own runtime, without an engine CC wrapper. Lab manager belongs to Software Factory. Lab executor and protected client run in a separate management container outside the disposable Incus experiment. Durable job/stage checkpoints and evidence receipts remain in Factory. A failed attempt is restarted with a new generation after confirmed stop, not resumed as a partially scored run. Runtime settings may change only within the permitted contract and retain configuration identity; source changes require a rebuilt image.
Source: supplied AI4Research Workshop Key Takeaways (Nov6) and post-presentation directions.
MANAGER / EXECUTOR RECOMMENDATION
Proposed simplest first implementation: the Factory exposes one asynchronous Lab Manager API. Builder submits identified releases/playbooks and receives a durable job ID, then continues other work. A deterministic worker in a separate management container polls/claims assigned jobs, emits heartbeat/stage events and returns artifact manifests/results through Manager. No separate public worker API or message broker is required initially. Manager owns admission, cancellation, generation/lease and durable status; trusted platform actuation owns narrowly allowed Incus operations. The worker follows permitted playbook stages and bounded retries. Agent reasoning can remain in Factory report analysis and request another bounded diagnostic job; a resident LLM is optional, not required for execution or recovery. All prior references to lab-agent judgment describe that optional future role. One scored or profiling GPU job at a time per Spark; independent qualified hosts can run in parallel. Polling can be replaced by other transport later without changing job semantics. At-least-once delivery requires idempotent claim/start/export, generation fencing and confirmed stop before retry; do not promise exactly-once GPU execution. A cancellation acknowledgement is distinct from a stop request. Manager gateway carries control and evidence references; scoped artifact fetch/upload may carry large bytes directly without exposing another experiment API. Manager may be a module in the existing Factory service with its existing database. Worker may include the Incus adapter and profiler wrappers as modules; a protected client can be a subprocess in the management container. No separate network actuator is required. Trusted worker credentials remain scoped and unavailable to reasoning agents or the engine. Factory job IDs cover full experiments and differ from Incus operation IDs. After event disconnection, reconcile actual operation/instance state because events need not replay. Release GPU admission while waiting for agent reasoning. This is a recommendation for discussion, not a claimed deployed or accepted implementation.

## Slide 3

Tools across the Muse inference engine
Architectural layers locate controls and observations; repeated transformer layers live inside layer 3.
HF Muse fd3cf014 • Strata / DwarfStar supply mechanisms to investigate, not measured Muse results
03
Native calls / buffers ↓
Tool outputs
1  API / protocol
HTTP inputs → native engine service → SSE / errors
Trial CC
first-token ms • tokens/s • events
observe
2  Scheduling / execution
admit / batch / advance prefill and decode; cancel / reset
State / load checks
queue ms • session outcomes
observe
3  Muse operations
embedding → attention / KV → router + experts → logits
NVTX / coverage tools
builder patch; lab emitted coverage
observe
4  State / weights / tensors
layouts, KV allocation, selected-expert access and residency
Weight prep / Observe
pack identity • misses • bytes
observe
5  CUDA / GB10
kernels, streams, events, copies and synchronization
Systems / Compute
device ns • selected counters
observe
Router uses hidden states to choose experts; residency policy decides how their weights are accessed.
Prefill: prompt-token work and workspace. Decode: repeated next-token work, KV access and expert reuse.

Speaker-note text (package numbering):

These are engineering boundaries, not mandatory separate services. Within the pinned Muse sparse MLP, router scoring uses the original hidden states while a separate projection supplies the expert computation path. Selected expert projections and weighted accumulation feed the output path; A1 shows the detailed source-derived graph. Do not import DeepSeek MLA, shared-expert or MTP assumptions. Configuration defaults are separate from gated checkpoint values. Scheduling means choosing and advancing accepted work; execution means performing operations and submitting CUDA activity. Tensor is a shaped numeric array; weights are learned parameters; activation/workspace is temporary numerical state; KV persists with a session. Expert-weight cache is different from attention KV. Strata initial layer/expert residency ranking is distinct from learned token routing. Prefill/decode bottlenecks remain hypotheses. Tool CC calls configure useful coarse operations; never insert a CC call per token/layer.
Sources
https://github.com/huggingface/transformers/blob/fd3cf0140de03f7619ac95b5cfed05b711ff9e22/src/transformers/models/muse_spark/modeling_muse_spark.py
https://github.com/huggingface/transformers/blob/fd3cf0140de03f7619ac95b5cfed05b711ff9e22/src/transformers/models/muse_spark/configuration_muse_spark.py
https://github.com/Niko1221/Strata/tree/ffa80d73133ea5c548aefe57889a16e8085a938f
https://github.com/antirez/ds4/tree/b3f50180ec2c7324892be1f50bc83555ccb8d5e7
TERMS AND BOUNDARY
Scheduling selects admitted work and advances prefill/decode steps. Muse operations compute embeddings, attention, expert routing/execution and logits. A tensor is a shaped numerical array; weights are learned parameters; activations/workspaces are temporary; KV is session state. CUDA is the GPU programming/runtime layer executing kernels on streams. API transport, scheduler delay, host NVTX scopes and device spans have different timing boundaries.
POST-WORKSHOP DESIGN ALIGNMENT
The top-level product contract is separate from reusable capability capsules and from the released engine image. Tool CCs support the workflow; component CC assets may be incorporated into engine code. The engine has its own runtime, without an engine CC wrapper. Lab manager belongs to Software Factory. Lab executor and protected client run in a separate management container outside the disposable Incus experiment. Durable job/stage checkpoints and evidence receipts remain in Factory. A failed attempt is restarted with a new generation after confirmed stop, not resumed as a partially scored run. Runtime settings may change only within the permitted contract and retain configuration identity; source changes require a rebuilt image.
Source: supplied AI4Research Workshop Key Takeaways (Nov6) and post-presentation directions.
MANAGER / EXECUTOR RECOMMENDATION
Proposed simplest first implementation: the Factory exposes one asynchronous Lab Manager API. Builder submits identified releases/playbooks and receives a durable job ID, then continues other work. A deterministic worker in a separate management container polls/claims assigned jobs, emits heartbeat/stage events and returns artifact manifests/results through Manager. No separate public worker API or message broker is required initially. Manager owns admission, cancellation, generation/lease and durable status; trusted platform actuation owns narrowly allowed Incus operations. The worker follows permitted playbook stages and bounded retries. Agent reasoning can remain in Factory report analysis and request another bounded diagnostic job; a resident LLM is optional, not required for execution or recovery. All prior references to lab-agent judgment describe that optional future role. One scored or profiling GPU job at a time per Spark; independent qualified hosts can run in parallel. Polling can be replaced by other transport later without changing job semantics. At-least-once delivery requires idempotent claim/start/export, generation fencing and confirmed stop before retry; do not promise exactly-once GPU execution. A cancellation acknowledgement is distinct from a stop request. Manager gateway carries control and evidence references; scoped artifact fetch/upload may carry large bytes directly without exposing another experiment API. Manager may be a module in the existing Factory service with its existing database. Worker may include the Incus adapter and profiler wrappers as modules; a protected client can be a subprocess in the management container. No separate network actuator is required. Trusted worker credentials remain scoped and unavailable to reasoning agents or the engine. Factory job IDs cover full experiments and differ from Incus operation IDs. After event disconnection, reconcile actual operation/instance state because events need not replay. Release GPU admission while waiting for agent reasoning. This is a recommendation for discussion, not a claimed deployed or accepted implementation.

## Slide 4

Two CC roles produce different reusable outputs
Tool / skill CCs help agents do a job. Component CCs provide implementation that Builder incorporates into the engine.
Proposed groupings • several capabilities can share an implementation package • product release stays independently identified
04
Role / CC example
Input
Useful output and destination
Tool: NVTX engineering
source + diagnostic question
checked patch + marker manifest → Builder
Tool: build / weight preparation
source + recipe / checkpoint
engine image / weight pack + provenance → release
Component: expert access
tensor / residency interface + constraints
source or library + tests → engine code / build
Component: kernel implementation
operation / dtype / layout contract
CUDA implementation + compatibility checks → engine build
Lab tool: trial / Systems / Compute
release + fixture / capture question
checks, raw events and profiler reports → Factory
Tool: analysis / evidence export
reports + identities + coverage
assessment + durable references / receipt → Factory
Tool / skill CCs
invoke during the workflow
Builder
assemble + verify
Component CCs
integrate assets into product
artifacts / checks
source / library
Reuse code, tools and intermediate artifacts. Each result retains the CC version, inputs, and evidence.

Speaker-note text (package numbering):

The distinction is how a capability is used, not necessarily a new discriminator in the CC schema. NVTX helper runs on Builder source and emits a patch; a kernel or expert-access component supplies implementation and tests incorporated into the build. An engine image can contain code obtained through component CCs without being wrapped as a CC itself. A capability may serve both roles in different workflows. Tools for profiling and analysis remain independently versioned and can change without changing the engine, subject to compatibility qualification. Weight pack means identified prepared tensor files/layout metadata rather than the model checkpoint claim alone. Source/library incorporation requires interface and dependency checks, not arbitrary binary linking. The named components are examples to implement or adapt, not existing proven Muse CCs. The lab consumes product releases and invokes permitted tool capabilities.
Sources
https://github.com/Stellven/jiuwenswarm/tree/a838b97048b2c561212ccfa82b5d414c39359dc9
https://github.com/Niko1221/Strata/tree/ffa80d73133ea5c548aefe57889a16e8085a938f
https://github.com/antirez/ds4/tree/b3f50180ec2c7324892be1f50bc83555ccb8d5e7
https://docs.nvidia.com/nsight-systems/UserGuide/index.html
https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html
POST-WORKSHOP DESIGN ALIGNMENT
The top-level product contract is separate from reusable capability capsules and from the released engine image. Tool CCs support the workflow; component CC assets may be incorporated into engine code. The engine has its own runtime, without an engine CC wrapper. Lab manager belongs to Software Factory. Lab executor and protected client run in a separate management container outside the disposable Incus experiment. Durable job/stage checkpoints and evidence receipts remain in Factory. A failed attempt is restarted with a new generation after confirmed stop, not resumed as a partially scored run. Runtime settings may change only within the permitted contract and retain configuration identity; source changes require a rebuilt image.
Source: supplied AI4Research Workshop Key Takeaways (Nov6) and post-presentation directions.
MANAGER / EXECUTOR RECOMMENDATION
Proposed simplest first implementation: the Factory exposes one asynchronous Lab Manager API. Builder submits identified releases/playbooks and receives a durable job ID, then continues other work. A deterministic worker in a separate management container polls/claims assigned jobs, emits heartbeat/stage events and returns artifact manifests/results through Manager. No separate public worker API or message broker is required initially. Manager owns admission, cancellation, generation/lease and durable status; trusted platform actuation owns narrowly allowed Incus operations. The worker follows permitted playbook stages and bounded retries. Agent reasoning can remain in Factory report analysis and request another bounded diagnostic job; a resident LLM is optional, not required for execution or recovery. All prior references to lab-agent judgment describe that optional future role. One scored or profiling GPU job at a time per Spark; independent qualified hosts can run in parallel. Polling can be replaced by other transport later without changing job semantics. At-least-once delivery requires idempotent claim/start/export, generation fencing and confirmed stop before retry; do not promise exactly-once GPU execution. A cancellation acknowledgement is distinct from a stop request. Manager gateway carries control and evidence references; scoped artifact fetch/upload may carry large bytes directly without exposing another experiment API. Manager may be a module in the existing Factory service with its existing database. Worker may include the Incus adapter and profiler wrappers as modules; a protected client can be a subprocess in the management container. No separate network actuator is required. Trusted worker credentials remain scoped and unavailable to reasoning agents or the engine. Factory job IDs cover full experiments and differ from Incus operation IDs. After event disconnection, reconcile actual operation/instance state because events need not replay. Release GPU admission while waiting for agent reasoning. This is a recommendation for discussion, not a claimed deployed or accepted implementation.

## Slide 5

NVTX CC: reusable judgment support and repeatable edits
NVTX labels code regions so traces identify Muse operations; the CC makes placement repeatable.
NVTX labels host work and launched CUDA activity • DwarfStar demonstrates conditional hooks, not full coverage
05
Question + exact source
Which expert-access stage delays decode?
Skill + deterministic tools
inspect • check_plan • apply • check_build
Builder output
new image + patch + marker manifest
inspect
build
Agent proposes placement
source anchor + base hash
phase / layer / operation IDs
thread ownership + async lifetime
fixture that exercises the path
Semantics require reasoning.
Helpers prevent repeated mistakes
C++ scope sketch:
nvtx3::scoped_range r{"moe.dispatch"};
dispatch_experts(...);
Reject stale anchors / duplicate hooks.
Check early exits and enabled build paths.
Lab checks the submitted build
fixture → emitted markers + CUDA trace
numerical check + coverage result
missing hooks → builder request
new instrumentation → new image
Lab reports gaps; it does not patch.
Fused / batched work may map many requests and experts to one kernel. Preserve the participant map.
A host range is not GPU duration. NVTX does not count expert misses; the engine must expose them.

Speaker-note text (package numbering):

NVTX supplies semantic context. Push/pop is nested and thread-local; start/end handles cover overlapping and cross-thread lifetimes. C++ RAII supports ordinary scope closure; C paths need explicit cleanup on every exit. Do not insert CUDA synchronization solely to force host ranges to resemble device duration. Stable registered strings and selective granularity reduce avoidable work. Source inspection identifies symbols/macros/backend paths; agent reasoning proposes placement. check_plan validates source fingerprints and range policy. apply is exact-base, bounded, idempotent and emits a patch/new snapshot; repeated application must not duplicate hooks. check_build in builder validation compiles and runs a fixture; lab independent coverage verifies the submitted image and returns missing sites. Compilation alone is insufficient: conditional NVTX headers can make calls no-ops, and an environment flag may only enable a gated path. DwarfStar pinned fused-prefill scopes require additional conditions; Strata documents Nsight investigations, but the earlier scan did not establish native NVTX coverage. CUDA Graph construction/replay and graph/node trace modes need explicit coverage. Fused kernels cannot be divided into invented per-expert times. Compare original, instrumented-without-capture and captured diagnostic arms when assessing perturbation. Evidence gaps improve regression fixtures/rule packs rather than merely growing prose.
Sources
https://nvidia.github.io/NVTX/
https://nvidia.github.io/NVTX/doxygen/group___m_a_r_k_e_r_s___a_n_d___r_a_n_g_e_s.html
https://docs.nvidia.com/nsight-systems/UserGuide/index.html
https://github.com/antirez/ds4/tree/b3f50180ec2c7324892be1f50bc83555ccb8d5e7
https://github.com/Niko1221/Strata/tree/ffa80d73133ea5c548aefe57889a16e8085a938f
TERMS AND BOUNDARY
An annotation plan is not the system ontology. It can refer to its supplied component identifiers, but the ontology team owns their semantics. Push/pop ranges belong to one thread and nest; start/end ranges can overlap/cross threads. Marker calls can be compiled out or fail to execute on a conditional path. The tool can deterministically validate and apply an anchored plan; it cannot certify arbitrary semantic meaning by reading a function name.
POST-WORKSHOP DESIGN ALIGNMENT
The top-level product contract is separate from reusable capability capsules and from the released engine image. Tool CCs support the workflow; component CC assets may be incorporated into engine code. The engine has its own runtime, without an engine CC wrapper. Lab manager belongs to Software Factory. Lab executor and protected client run in a separate management container outside the disposable Incus experiment. Durable job/stage checkpoints and evidence receipts remain in Factory. A failed attempt is restarted with a new generation after confirmed stop, not resumed as a partially scored run. Runtime settings may change only within the permitted contract and retain configuration identity; source changes require a rebuilt image.
Source: supplied AI4Research Workshop Key Takeaways (Nov6) and post-presentation directions.
MANAGER / EXECUTOR RECOMMENDATION
Proposed simplest first implementation: the Factory exposes one asynchronous Lab Manager API. Builder submits identified releases/playbooks and receives a durable job ID, then continues other work. A deterministic worker in a separate management container polls/claims assigned jobs, emits heartbeat/stage events and returns artifact manifests/results through Manager. No separate public worker API or message broker is required initially. Manager owns admission, cancellation, generation/lease and durable status; trusted platform actuation owns narrowly allowed Incus operations. The worker follows permitted playbook stages and bounded retries. Agent reasoning can remain in Factory report analysis and request another bounded diagnostic job; a resident LLM is optional, not required for execution or recovery. All prior references to lab-agent judgment describe that optional future role. One scored or profiling GPU job at a time per Spark; independent qualified hosts can run in parallel. Polling can be replaced by other transport later without changing job semantics. At-least-once delivery requires idempotent claim/start/export, generation fencing and confirmed stop before retry; do not promise exactly-once GPU execution. A cancellation acknowledgement is distinct from a stop request. Manager gateway carries control and evidence references; scoped artifact fetch/upload may carry large bytes directly without exposing another experiment API. Manager may be a module in the existing Factory service with its existing database. Worker may include the Incus adapter and profiler wrappers as modules; a protected client can be a subprocess in the management container. No separate network actuator is required. Trusted worker credentials remain scoped and unavailable to reasoning agents or the engine. Factory job IDs cover full experiments and differ from Incus operation IDs. After event disconnection, reconcile actual operation/instance state because events need not replay. Release GPU admission while waiting for agent reasoning. This is a recommendation for discussion, not a claimed deployed or accepted implementation.

## Slide 6

Crash-surviving lab control and immutable engine deployment
Proposed separation: a management container coordinates tests outside the disposable Incus experiment.
Incus shares the host kernel • private Docker runs the ARM64 image • GPU/profiler path still requires qualification
06
Software Factory
Lab manager API
job ID • status • cancel
Knowledge + telemetry
job checkpoints • raw reports
release IDs • receipts
DGX Spark host — driver / trusted Incus integration
Management container
Lab executor
worker now; agent optional
bounded playbook
Protected trial runner
HTTP / SSE • client timings
Disposable Incus experiment
Engine application
read-only image + identified inputs
private Docker • native endpoint
Qualified profiler tools
plain / nsys / targeted ncu launch
job spec
results
persist job / evidence
Builder submits; receives job ID
claim / events
run fixture
events
worker adapter: provision / stop
GPU device + compatible libraries
native traffic / replies
capture wrapper
reports + coverage to worker; return via Manager
Mounts: read-only inputs/tools; bounded state/cache/scratch; protected report spool.
Worker polls Manager for jobs. Durable stage checkpoints survive; a restart creates a new attempt / generation.
One scored/profiled GPU job per Spark. Independent hosts run jobs in parallel; Factory retains every job.

Speaker-note text (package numbering):

Lab executor is outside the experiment Incus in a separate management container, avoiding a raw-host LLM agent and keeping management out of the experiment memory/process failure envelope. Protected trial runner is also separate, so candidate failures cannot author its timings/results. This does not isolate shared-host kernel/driver failures. Lab manager in Software Factory stores durable job stage, attempt generation, release/config/resource identities, completed artifact references and export receipts. A trusted host platform actuator enforces scoped provision/launch/stop requests and named budgets. Do not mount an unrestricted Incus or host Docker socket into the agent/candidate; Incus administrative access has host-level authority. The diagram abbreviates readiness/status return through actuator. Private Docker inside experiment is the concrete first provider. Exact GPU nodes, compatible libraries and profiler injection cross the Incus and Docker boundaries; both need qualification. Read-only root/inputs plus bounded writable state/cache/scratch/report spool enforce no code editing. Reports stage under protected custody and return to Factory before cleanup. Engine exit: preserve status/partial output and restart same identified release within retry budget. Incus loss: actuator recreates environment, worker reconciles checkpoint and starts a new attempt; incomplete captures remain incomplete. Worker loss: manager reassigns/resumes durable orchestration state, fences previous attempt before duplication. GPU/host failure: stop admission and request platform recovery. Checkpoint refers to workflow state, not live CUDA allocation/graph/KV restoration. Same-host failures may lose unflushed local traces, recorded as coverage loss. Separate management resource reserve is accounted apart from experiment limits. Direct Incus OCI remains alternative if nested qualification fails.
Sources
https://linuxcontainers.org/incus/docs/main/reference/devices_gpu/
https://linuxcontainers.org/incus/docs/main/reference/instance_options/#nvidia-and-cuda-configuration
https://docs.nvidia.com/nsight-systems/UserGuide/index.html
https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html
https://linuxcontainers.org/incus/docs/main/explanation/security/
https://linuxcontainers.org/incus/docs/main/howto/instances_backup/
POST-WORKSHOP DESIGN ALIGNMENT
The top-level product contract is separate from reusable capability capsules and from the released engine image. Tool CCs support the workflow; component CC assets may be incorporated into engine code. The engine has its own runtime, without an engine CC wrapper. Lab manager belongs to Software Factory. Lab executor and protected client run in a separate management container outside the disposable Incus experiment. Durable job/stage checkpoints and evidence receipts remain in Factory. A failed attempt is restarted with a new generation after confirmed stop, not resumed as a partially scored run. Runtime settings may change only within the permitted contract and retain configuration identity; source changes require a rebuilt image.
Source: supplied AI4Research Workshop Key Takeaways (Nov6) and post-presentation directions.
MANAGER / EXECUTOR RECOMMENDATION
Proposed simplest first implementation: the Factory exposes one asynchronous Lab Manager API. Builder submits identified releases/playbooks and receives a durable job ID, then continues other work. A deterministic worker in a separate management container polls/claims assigned jobs, emits heartbeat/stage events and returns artifact manifests/results through Manager. No separate public worker API or message broker is required initially. Manager owns admission, cancellation, generation/lease and durable status; trusted platform actuation owns narrowly allowed Incus operations. The worker follows permitted playbook stages and bounded retries. Agent reasoning can remain in Factory report analysis and request another bounded diagnostic job; a resident LLM is optional, not required for execution or recovery. All prior references to lab-agent judgment describe that optional future role. One scored or profiling GPU job at a time per Spark; independent qualified hosts can run in parallel. Polling can be replaced by other transport later without changing job semantics. At-least-once delivery requires idempotent claim/start/export, generation fencing and confirmed stop before retry; do not promise exactly-once GPU execution. A cancellation acknowledgement is distinct from a stop request. Manager gateway carries control and evidence references; scoped artifact fetch/upload may carry large bytes directly without exposing another experiment API. Manager may be a module in the existing Factory service with its existing database. Worker may include the Incus adapter and profiler wrappers as modules; a protected client can be a subprocess in the management container. No separate network actuator is required. Trusted worker credentials remain scoped and unavailable to reasoning agents or the engine. Factory job IDs cover full experiments and differ from Incus operation IDs. After event disconnection, reconcile actual operation/instance state because events need not replay. Release GPU admission while waiting for agent reasoning. This is a recommendation for discussion, not a claimed deployed or accepted implementation.

## Slide 7

A playbook spends profiling effort only where needed
Input: engine/model/config + fixture/reference + tools/resource profile + playbook time, report-size and retry caps.
Worker runs approved stages; Factory agents can request bounded follow-up diagnostics
07
1  Intake + correctness
verify bytes • launch / readiness
reference / numerical / state checks
2  Unprofiled trial
protected client + lightweight telemetry
matched workload / warmup / reset
3  Systems, if unresolved
CUDA / NVTX phase capture
time / report-size caps
analyze saved report first
4  Compute, if justified
selected kernel + metrics
launch/time caps; replay policy
pass
failed / unavailable
Mandatory
Conditional diagnostic attempts — same identified product
Useful result
score / checks • diagnosis • raw references
failed / missing / inconclusive evidence
Evidence gap request
affected component + missing observation
new engine hooks or tool / decoder release
insufficient coverage
Each attempt: own generation / settings; diagnostic branches can be skipped
Budget reached → stop; retain partial / inconclusive evidence.
Stop / finalize run → export every outcome to Factory knowledge / telemetry → receipt → clean staging
A capture is diagnostic evidence, not a serving score. A source or instrumentation fix requires a new image.

Speaker-note text (package numbering):

Mandatory stages establish intake/readiness, independent supplied correctness and an unprofiled representative trial. An optional Factory agent may request only predeclared diagnostic branches/budgets. Systems obtains a short CUDA/NVTX timeline around actual prefill/decode work after startup; summaries and detailed inspection normally reuse the same report. Compute needs a specific observed kernel/question and bounded invocation/metric selection, in a separate diagnostic execution with declared state policy. It may replay kernels or applications; record actual replay/cache settings. Avoid startup kernels when the question concerns inference. nsys --duration defaults may terminate a launched process; use explicit bounded replay or --kill=none and worker-owned shutdown, preserving report flush. Never run Systems and Compute concurrently on one attempt. Failed intake, missing counter permission, stale generation, timeout or truncated capture remain distinct statuses. Completion requires Factory-resolvable artifact references/receipt. Transfer failure retains staging with bounded retries; exhausted capacity pauses admission, not deletes unexported evidence. Factory analysis assesses evidence but cannot repair submitted code in lab. Reference thresholds and token-count policy come from supplied evaluation materials.
Sources
https://docs.nvidia.com/nsight-systems/UserGuide/index.html
https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html
https://github.com/Stellven/jiuwenswarm/tree/a838b97048b2c561212ccfa82b5d414c39359dc9
DETAILED TECHNICAL BACKING
Slide 7 — Staged evaluation playbook
1. **Admit and check.** Bind model/checkpoint/tokenizer/pack/image/config/fixture; verify actual loaded product. Numerical/state checks use a supplied checkpoint-matched reference and declared tolerances. Startup health is not correctness.
2. **Benchmark without a heavy profiler.** Warmup and state/cache policy are fixed. Preserve client request start, first declared content and completion/error. TTFT is reported in ms; rates in tokens/s with explicit per-user versus aggregate denominators. SSE events are not token IDs. Keep raw events/count policy and incomplete work.
3. **Systems capture when evidence warrants it.** A short CUDA/NVTX trace localizes launch, synchronization, copy or phase gaps. Initially disable optional CPU sampling/context switches; enable additional acquisition only for a declared question and qualified permission.
4. **Analyze existing trace before rerunning.** Summary reports and event-level SQLite inspection can use the same raw capture. Recapture only for inadequate coverage or a different experiment condition. Sum of overlapping kernel durations is aggregate device work, not elapsed latency saved; GPU idle gaps do not by themselves prove CPU launch causality.
5. **Compute only for a selected kernel question.** Select observed kernel/invocation and supported sections. Requested metrics can require replay or software instrumentation. Static launch/occupancy facts do not necessarily require replay. Counter interpretation is diagnostic; the comparison remains unprofiled.
6. **Return and decide.** Bundle raw reports, metrics/checks, identities, coverage, failures and proposed next investigation. Builder changes implementation and submits a new image.
Systems and Compute are separate runs, never concurrent collection on the same attempt. Fixed-duration capture can terminate the launched process by default; choose an intentional lifecycle. A finite disposable replay can end normally, while a persistent diagnostic session can use `--kill=none` with an independent worker deadline/confirmed stop. Prefer supported capture ranges when model load would consume the window. Preserve truncated reports and failed acquisition. [Systems CLI and capture controls](https://docs.nvidia.com/nsight-systems/UserGuide/index.html), [Compute replay/overhead](https://docs.nvidia.com/nsight-compute/ProfilingGuide/).
**Commands are templates, not measured receipts:** `nsys profile --trace=cuda,nvtx --sample=none --cpuctxsw=none --duration=20 --kill=none ...` selects a diagnostic policy, not a latency benchmark. `ncu --set basic --kernel-name regex:OBSERVED_KERNEL --launch-count 1 ...` bounds a first kernel investigation. Installed version/help, ARM64 package, output mount and permissions must match the execution environment.
**Every outcome returns to Factory:** finalize the manifest for successful, failed, cancelled, truncated and unavailable-coverage outcomes; transfer all retained raw artifacts/results to the Factory knowledge/telemetry plane and obtain its receipt. Cleanup must not delete unexported evidence. An export failure is explicitly `pending`/failed transfer, never a successful overall completion: retain bounded protected staging, retry within the declared budget, and report what remains unexported. If staging capacity or retry budget is exhausted, stop admission of new attempts and return a clear blocked/failed export status while preserving existing unexported files. Resume/reconcile the same transfer identity rather than creating an unrelated attempt.
POST-WORKSHOP DESIGN ALIGNMENT
The top-level product contract is separate from reusable capability capsules and from the released engine image. Tool CCs support the workflow; component CC assets may be incorporated into engine code. The engine has its own runtime, without an engine CC wrapper. Lab manager belongs to Software Factory. Lab executor and protected client run in a separate management container outside the disposable Incus experiment. Durable job/stage checkpoints and evidence receipts remain in Factory. A failed attempt is restarted with a new generation after confirmed stop, not resumed as a partially scored run. Runtime settings may change only within the permitted contract and retain configuration identity; source changes require a rebuilt image.
Source: supplied AI4Research Workshop Key Takeaways (Nov6) and post-presentation directions.
MANAGER / EXECUTOR RECOMMENDATION
Proposed simplest first implementation: the Factory exposes one asynchronous Lab Manager API. Builder submits identified releases/playbooks and receives a durable job ID, then continues other work. A deterministic worker in a separate management container polls/claims assigned jobs, emits heartbeat/stage events and returns artifact manifests/results through Manager. No separate public worker API or message broker is required initially. Manager owns admission, cancellation, generation/lease and durable status; trusted platform actuation owns narrowly allowed Incus operations. The worker follows permitted playbook stages and bounded retries. Agent reasoning can remain in Factory report analysis and request another bounded diagnostic job; a resident LLM is optional, not required for execution or recovery. All prior references to lab-agent judgment describe that optional future role. One scored or profiling GPU job at a time per Spark; independent qualified hosts can run in parallel. Polling can be replaced by other transport later without changing job semantics. At-least-once delivery requires idempotent claim/start/export, generation fencing and confirmed stop before retry; do not promise exactly-once GPU execution. A cancellation acknowledgement is distinct from a stop request. Manager gateway carries control and evidence references; scoped artifact fetch/upload may carry large bytes directly without exposing another experiment API. Manager may be a module in the existing Factory service with its existing database. Worker may include the Incus adapter and profiler wrappers as modules; a protected client can be a subprocess in the management container. No separate network actuator is required. Trusted worker credentials remain scoped and unavailable to reasoning agents or the engine. Factory job IDs cover full experiments and differ from Incus operation IDs. After event disconnection, reconcile actual operation/instance state because events need not replay. Release GPU admission while waiting for agent reasoning. This is a recommendation for discussion, not a claimed deployed or accepted implementation.

## Slide 8

Combine profiler data with engine facts and matched trials
The engine must expose routing, residency and state decisions that generic CUDA tools cannot infer.
Prefill and decode are separate investigations • unified physical memory does not mean identical accounting views
08
Question
Required evidence and boundary
Builder feedback
Why did expert work wait?
Engine (layer,expert) route + residency lookup/miss events; read bytes; NVTX/CUDA gap
Residency / prefetch / layout hypothesis, or request missing counters
Is a kernel the bottleneck?
Systems: device spans and overlap. Compute: selected-kernel counters with replay settings
Target the actual kernel; a busy GPU or long host range is insufficient
Is state or scheduling wrong?
Queue and batch IDs; KV allocation/lifetime; cancel/reset/continuation fixtures
State / batching fix, with preserved context and concurrency policy
Did serving improve correctly?
Protected first-token latency (TTFT), ms; tokens/s, errors/raw SSE; supplied numerical / quality reference
Accept / regress / incorrect / inconclusive under matched conditions
What evidence is missing?
Expected versus emitted markers; unsupported metrics; format / coverage / loss
Engine observability request or reusable tool/analyzer upgrade
Safety RAM limit ≠ expert-cache experiment budget. Page fault ≠ expert miss. Cached read ≠ SSD access.
Factory keeps measurements and assessments separately, linked to code, image, fixture, tools, and conditions.

Speaker-note text (package numbering):

The expert router selects token/expert work; cache lookup and actual dispatch decide residency/access and execution. Record actual lookup/execution outcomes, not label all selected experts as executed/cache hits. Prefetch, deduplication, fallback or skipped work affect denominators. Per-layer/expert counters need identities and meaningful invocation/byte units; sampled detail can complement aggregates. OS faults/read counters do not equal semantic expert misses or guaranteed SSD fetches. Unified Spark memory views include CPU/GPU allocations, file cache, OS and tools; qualify cgroup/RSS/NVML coverage without summing overlapping views. SSE events may batch tokens; raw event gaps are not per-token gaps. TTFT boundary and pinned tokenizer/template/count policy must be declared. Correctness includes independent reference/numerical checks plus state and supplied benchmark, not agreement with the candidate itself. Missing evidence is a useful output: a marker site, counter, capture mode, decoder or fixture can become a tool/engine request. Raw findings and agent hypotheses remain separate in Factory records.
Sources
https://github.com/huggingface/transformers/blob/fd3cf0140de03f7619ac95b5cfed05b711ff9e22/src/transformers/models/muse_spark/modeling_muse_spark.py
https://github.com/Niko1221/Strata/tree/ffa80d73133ea5c548aefe57889a16e8085a938f
https://github.com/antirez/ds4/tree/b3f50180ec2c7324892be1f50bc83555ccb8d5e7
https://docs.nvidia.com/nsight-systems/UserGuide/index.html
https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html
https://docs.kernel.org/admin-guide/cgroup-v2.html
POST-WORKSHOP DESIGN ALIGNMENT
The top-level product contract is separate from reusable capability capsules and from the released engine image. Tool CCs support the workflow; component CC assets may be incorporated into engine code. The engine has its own runtime, without an engine CC wrapper. Lab manager belongs to Software Factory. Lab executor and protected client run in a separate management container outside the disposable Incus experiment. Durable job/stage checkpoints and evidence receipts remain in Factory. A failed attempt is restarted with a new generation after confirmed stop, not resumed as a partially scored run. Runtime settings may change only within the permitted contract and retain configuration identity; source changes require a rebuilt image.
Source: supplied AI4Research Workshop Key Takeaways (Nov6) and post-presentation directions.
MANAGER / EXECUTOR RECOMMENDATION
Proposed simplest first implementation: the Factory exposes one asynchronous Lab Manager API. Builder submits identified releases/playbooks and receives a durable job ID, then continues other work. A deterministic worker in a separate management container polls/claims assigned jobs, emits heartbeat/stage events and returns artifact manifests/results through Manager. No separate public worker API or message broker is required initially. Manager owns admission, cancellation, generation/lease and durable status; trusted platform actuation owns narrowly allowed Incus operations. The worker follows permitted playbook stages and bounded retries. Agent reasoning can remain in Factory report analysis and request another bounded diagnostic job; a resident LLM is optional, not required for execution or recovery. All prior references to lab-agent judgment describe that optional future role. One scored or profiling GPU job at a time per Spark; independent qualified hosts can run in parallel. Polling can be replaced by other transport later without changing job semantics. At-least-once delivery requires idempotent claim/start/export, generation fencing and confirmed stop before retry; do not promise exactly-once GPU execution. A cancellation acknowledgement is distinct from a stop request. Manager gateway carries control and evidence references; scoped artifact fetch/upload may carry large bytes directly without exposing another experiment API. Manager may be a module in the existing Factory service with its existing database. Worker may include the Incus adapter and profiler wrappers as modules; a protected client can be a subprocess in the management container. No separate network actuator is required. Trusted worker credentials remain scoped and unavailable to reasoning agents or the engine. Factory job IDs cover full experiments and differ from Incus operation IDs. After event disconnection, reconcile actual operation/instance state because events need not replay. Release GPU admission while waiting for agent reasoning. This is a recommendation for discussion, not a claimed deployed or accepted implementation.

## Slide 9

Together Compiler (TKCC): potential evolution
TKCC combines persistent engines, candidate hot reload, representative inputs, and tiered validation.
Together AI, November 2026 • external results concern its evaluated stacks; no transferred Muse / Spark performance
09
Mechanism
Potential advantage here
Additional work / risk
Persistent loaded engine
Avoid repeated loading, initialization and warmup
State reset, contamination checks, memory drift and crash recovery
Hot-reload candidate code
Test compatible implementations without full restart
Loading interface; drain work; graph recapture; restore / identify loaded code
Fast → realistic tiers
Reject poor candidates before expensive evaluation
Validate screen fidelity against real routing and full-engine checks
Parallel candidate generation
Keep useful experiments queued while agents reason
Coordinate candidates; serialize scored GPU experiments on one Spark
Immutable-image lab
Identified launch + tests + profiler wrappers
Fresh-instance recovery; broad engine changes
TKCC-style extension
Engine-specific loading + reset / restore
Compatible changes only; qualification still required
Experiment throughput is not inference throughput. Reusable CCs and release evidence work with either path.

Speaker-note text (package numbering):

TKCC treats optimization as experimental code search. Published examples report lower setup cost and higher experiment throughput through persistent forward-pass replacement and tiered evaluation. Keep benchmark scope/hardware/configuration explicit. Blog startup467s versus9s is one reported example, not full candidate-development duration or a Muse estimate; 252x concerns experiment throughput. The paper table for another workload has different startup/reload values; do not silently combine them. Random inputs activating13–38% more MoE experts and a1.3x sparse-attention indexer slowdown are separate examples. Representative data and tier-fidelity tests matter to residency questions. Additional hot-reload mechanisms include compatible callable/module boundary, quiescence, graph invalidation/recapture, buffer ownership, baseline restoration, loaded-module digest and generation, contamination checks and process restart on unknown state. An OCI image can still define the immutable base for a future loading protocol. Static function selection or cached images is not candidate hot reload. No claim of available reusable TKCC source/backend integration is required. Do not adopt multi-GPU TP/EP/DCP cost modeling for the single-Spark first version. Avoid unsupported week estimates and numerical complexity scores.
Sources
https://www.together.ai/blog/together-compiler-continual-compilation-for-ai-inference
https://www.together.ai/together-compiler-paper
DETAILED TECHNICAL BACKING
Slide 9 — Together-inspired evolution
TKCC targets experiment throughput as well as inference quality/performance: persistent engines, low-cost layer subsets, realistic validation and candidate-forward implementation reload. These are inspiration for future tests, not current integrations or a required starting architecture. The public paper reports 252× more optimization experiments against its evaluated baseline; that is not a Muse/Spark inference speedup.
Correct the attachment's conflation: random input activated 13–38% more MoE experts; a separate sparse-attention indexer/top-k example produced the 1.3× end-to-end slowdown. Both motivate realistic data, but they are different findings. [Official TKCC paper, page 4](https://www.together.ai/together-compiler-paper).
Safe initial reuse includes cached image layers, pinned model storage, offline analysis and same-image sessions whose reset is qualified. Reusing cached staging is not hot reload. Reusing one image's engine while resetting requests is not changing implementation. Actual hot reload changes a loaded implementation inside a persistent process and introduces buffer/ABI ownership, graph invalidation, in-flight work, rollback and memory-lifetime questions.
A future dynamic-module experiment can bundle A/B modules in one immutable experimental image. A lab-selected test loads/uses/unloads those fixed implementations; the Lab Agent still does not author code. Static startup selection or switching statically linked functions must not be described as dynamic hot reload. Even a working module POC validates a boundary, not a general TKCC optimizer.
POST-WORKSHOP DESIGN ALIGNMENT
The top-level product contract is separate from reusable capability capsules and from the released engine image. Tool CCs support the workflow; component CC assets may be incorporated into engine code. The engine has its own runtime, without an engine CC wrapper. Lab manager belongs to Software Factory. Lab executor and protected client run in a separate management container outside the disposable Incus experiment. Durable job/stage checkpoints and evidence receipts remain in Factory. A failed attempt is restarted with a new generation after confirmed stop, not resumed as a partially scored run. Runtime settings may change only within the permitted contract and retain configuration identity; source changes require a rebuilt image.
Source: supplied AI4Research Workshop Key Takeaways (Nov6) and post-presentation directions.
MANAGER / EXECUTOR RECOMMENDATION
Proposed simplest first implementation: the Factory exposes one asynchronous Lab Manager API. Builder submits identified releases/playbooks and receives a durable job ID, then continues other work. A deterministic worker in a separate management container polls/claims assigned jobs, emits heartbeat/stage events and returns artifact manifests/results through Manager. No separate public worker API or message broker is required initially. Manager owns admission, cancellation, generation/lease and durable status; trusted platform actuation owns narrowly allowed Incus operations. The worker follows permitted playbook stages and bounded retries. Agent reasoning can remain in Factory report analysis and request another bounded diagnostic job; a resident LLM is optional, not required for execution or recovery. All prior references to lab-agent judgment describe that optional future role. One scored or profiling GPU job at a time per Spark; independent qualified hosts can run in parallel. Polling can be replaced by other transport later without changing job semantics. At-least-once delivery requires idempotent claim/start/export, generation fencing and confirmed stop before retry; do not promise exactly-once GPU execution. A cancellation acknowledgement is distinct from a stop request. Manager gateway carries control and evidence references; scoped artifact fetch/upload may carry large bytes directly without exposing another experiment API. Manager may be a module in the existing Factory service with its existing database. Worker may include the Incus adapter and profiler wrappers as modules; a protected client can be a subprocess in the management container. No separate network actuator is required. Trusted worker credentials remain scoped and unavailable to reasoning agents or the engine. Factory job IDs cover full experiments and differ from Incus operation IDs. After event disconnection, reconcile actual operation/instance state because events need not replay. Release GPU admission while waiting for agent reasoning. This is a recommendation for discussion, not a claimed deployed or accepted implementation.

## Slide 10

Start with attributable experiments; evolve when evidence justifies it
Proposed progression: reusable Factory workflows, an immutable evaluation loop, then qualified optimization.
Recommended progression • simpler first integration; future experiments have explicit stop budgets in A7
10
1  Immutable lab
image → checks / trial → evidence
Worker executes bounded playbook
2  Improve the loop
measure setup / coverage gaps
upgrade tools or engine hooks
3  Qualified reuse
cached artifacts; then test reset
same-image process reuse only if safe
4  TKCC-style loading
compatible module boundary
state / graph restore + fresh final trial
First implementation
Conditional evolution
Measure first
Decision it informs
delivery + startup + weight load + warmup + trial time
Optimize the dominant cost; do not presume hot reload is the answer.
correctness / coverage / recovery / report export
Establish a trustworthy experiment before increasing its throughput.
valid experiments per hour + recovery and integration effort
Judge whether a more persistent engine is worth its added complexity.
Permitted code / CC choices can iterate. Fundamental contract changes require human approval.
Build the image-based evaluation loop first. TKCC is an evolution—not a dependency of the proposed CC / lab system.

Speaker-note text (package numbering):

We recommend the immutable-image lab because the actual engine/factory are not yet built. It lets broad code changes be tested without inventing engine ABI/loading interfaces. It still requires orchestration, GPU/profiler qualification, correct comparisons and evidence export; simpler does not mean no work. Initial known CUDA fixture establishes lab/tool capability only. A real Muse image with approved model/config then establishes actual inference tests. Cache identified image layers/model files and reuse offline analysis first. Measure Tbuild,Tdelivery,Tstartup,Twarmup,Tevaluation separately. Only then investigate safe same-image process reuse, representative screening and dynamic loading. A7 pilots are optional future investigations, not milestones blocking the first lab. No human/team assignment or schedule estimate is made. Factory knowledge/telemetry retains artifacts/results for every stage. New tooling or engine-observability releases follow the same builder/CC mechanism. Current local CC finite/service foundations are distinct from proposed GPU/Incus/registry integration.
Sources
https://github.com/Stellven/jiuwenswarm/tree/a838b97048b2c561212ccfa82b5d414c39359dc9
https://www.together.ai/blog/together-compiler-continual-compilation-for-ai-inference
https://linuxcontainers.org/incus/docs/main/reference/devices_gpu/
DETAILED TECHNICAL BACKING
Slide 10 — Integration order, without a calendar
**Foundation:** define submitted image/materials and permitted test request; implement worker-backed staging/start/identify/stop/export and raw finite wrappers. Run one known CUDA fixture through the final Incus/private-Docker path. Qualify lab mechanics, not Muse.
**Engine admission:** Builder supplies an actual Muse-compatible engine and checkpoint-matched references. Establish supported operator/pack/model identity, correctness, realistic workload and initial unprofiled behavior. A source model graph or successful build is insufficient.
**Instrumented evaluation:** execute the same submission in benchmark, bounded Systems and selected Compute modes. Add protected dyno/host observations, marker/route/cache/state coverage checks and durable artifact joins. Missing hooks return to Builder.
**Evolution:** only then run bounded startup/reuse/fidelity/module experiments. They can show no benefit or unsupported behavior. No weeks, scores or autonomous factory completion are inferred.
**Completion includes durable return:** the worker/export adapter is complete only when Factory can resolve the manifest and raw artifact references and records receipt/coverage status. The Factory index links candidate/model/config/fixture, run/generation, capture settings and assessment so later agents can reference prior evidence. Lab staging may be removed after acknowledged durable return under the retention policy; failed or incomplete measurements are not filtered out of the knowledge plane.
POST-WORKSHOP DESIGN ALIGNMENT
The top-level product contract is separate from reusable capability capsules and from the released engine image. Tool CCs support the workflow; component CC assets may be incorporated into engine code. The engine has its own runtime, without an engine CC wrapper. Lab manager belongs to Software Factory. Lab executor and protected client run in a separate management container outside the disposable Incus experiment. Durable job/stage checkpoints and evidence receipts remain in Factory. A failed attempt is restarted with a new generation after confirmed stop, not resumed as a partially scored run. Runtime settings may change only within the permitted contract and retain configuration identity; source changes require a rebuilt image.
Source: supplied AI4Research Workshop Key Takeaways (Nov6) and post-presentation directions.
MANAGER / EXECUTOR RECOMMENDATION
Proposed simplest first implementation: the Factory exposes one asynchronous Lab Manager API. Builder submits identified releases/playbooks and receives a durable job ID, then continues other work. A deterministic worker in a separate management container polls/claims assigned jobs, emits heartbeat/stage events and returns artifact manifests/results through Manager. No separate public worker API or message broker is required initially. Manager owns admission, cancellation, generation/lease and durable status; trusted platform actuation owns narrowly allowed Incus operations. The worker follows permitted playbook stages and bounded retries. Agent reasoning can remain in Factory report analysis and request another bounded diagnostic job; a resident LLM is optional, not required for execution or recovery. All prior references to lab-agent judgment describe that optional future role. One scored or profiling GPU job at a time per Spark; independent qualified hosts can run in parallel. Polling can be replaced by other transport later without changing job semantics. At-least-once delivery requires idempotent claim/start/export, generation fencing and confirmed stop before retry; do not promise exactly-once GPU execution. A cancellation acknowledgement is distinct from a stop request. Manager gateway carries control and evidence references; scoped artifact fetch/upload may carry large bytes directly without exposing another experiment API. Manager may be a module in the existing Factory service with its existing database. Worker may include the Incus adapter and profiler wrappers as modules; a protected client can be a subprocess in the management container. No separate network actuator is required. Trusted worker credentials remain scoped and unavailable to reasoning agents or the engine. Factory job IDs cover full experiments and differ from Incus operation IDs. After event disconnection, reconcile actual operation/instance state because events need not replay. Release GPU admission while waiting for agent reasoning. This is a recommendation for discussion, not a claimed deployed or accepted implementation.

## Slide 11

A1  Muse text layer: precise instrumentation boundaries
Reference graph supports the engine specification and diagnostics; numeric defaults are not checkpoint certification.
HF reference fd3cf014: 62 layers; 8192 hidden; 128 Q / 16 KV heads; 256 experts, top-8; confirm selected checkpoint.
A1
Input norm
NVTX: layer + phase
Q/K/V + QK norm
NVTX: layer + phase
RoPE / NoPE + KV
Full / sliding cache
Attention + output
Norm / gate / projection
Residual → FFN norm
NVTX: layer + phase
MoE branches
Router selection + projected expert computation
Router
fp32 linear → sigmoid
Bias selects top-k
Normalize weights
Expert input
8192 → 4096
Projection + norm
Selected experts
SwiGLU + expert norm
Dispatch / weight retrieval
Weighted accumulation
Expert output
4096 → 8192
Post projection
FFN input forks
expert IDs + normalized weights
Post norm → residual gate → next layer
After last layer: final norm → logits → sampling
Prefill [B,T,H] / decode [B,1,H]: capture batch, context, dtype, expert work, cache policy.
Trace key = run / generation / request / phase / layer; expert-level dumps are targeted diagnostics.

Speaker-note text (package numbering):

HF source is the structural/numerical reference, not the recommended optimized Spark runtime. Default text config has 62 layers, hidden width 8192, 128 query/16 KV heads, head dimension 64 and sliding window 2048. Full-attention/NoPE layers occur every fourth counted backwards from the last, yielding 16 full and 46 sliding layers in these defaults. Exact checkpoint values require authorized config. The router reads the original 8192-wide state, uses fp32 linear logits scaled by output_multiplier, sigmoid routing scores, correction bias for top-k choice, then normalized selected weights. The parallel expert path projects to 4096, normalizes, runs selected SwiGLU experts with per-expert normalization and weighted accumulation, and projects to 8192. This decomposition tells the builder which hooks and contracts the lab needs. Numeric shapes are defaults; dynamic batches, context and active-expert distribution must be captured per experiment. No DeepSeek shared expert, MLA or MTP is assumed.
Sources
https://github.com/huggingface/transformers/blob/fd3cf0140de03f7619ac95b5cfed05b711ff9e22/src/transformers/models/muse_spark/modeling_muse_spark.py
https://github.com/huggingface/transformers/blob/fd3cf0140de03f7619ac95b5cfed05b711ff9e22/src/transformers/models/muse_spark/configuration_muse_spark.py
TERMS AND BOUNDARY
Reference numeric shapes/defaults are from public pinned configuration, not confirmed gated Muse checkpoint values. The runtime implementation may fuse operations. Per-layer/expert observability may therefore be sampled, aggregated or unavailable; record actual coverage. Keep participant mapping instead of dividing one fused kernel into fictional expert durations.
POST-WORKSHOP DESIGN ALIGNMENT
The top-level product contract is separate from reusable capability capsules and from the released engine image. Tool CCs support the workflow; component CC assets may be incorporated into engine code. The engine has its own runtime, without an engine CC wrapper. Lab manager belongs to Software Factory. Lab executor and protected client run in a separate management container outside the disposable Incus experiment. Durable job/stage checkpoints and evidence receipts remain in Factory. A failed attempt is restarted with a new generation after confirmed stop, not resumed as a partially scored run. Runtime settings may change only within the permitted contract and retain configuration identity; source changes require a rebuilt image.
Source: supplied AI4Research Workshop Key Takeaways (Nov6) and post-presentation directions.
MANAGER / EXECUTOR RECOMMENDATION
Proposed simplest first implementation: the Factory exposes one asynchronous Lab Manager API. Builder submits identified releases/playbooks and receives a durable job ID, then continues other work. A deterministic worker in a separate management container polls/claims assigned jobs, emits heartbeat/stage events and returns artifact manifests/results through Manager. No separate public worker API or message broker is required initially. Manager owns admission, cancellation, generation/lease and durable status; trusted platform actuation owns narrowly allowed Incus operations. The worker follows permitted playbook stages and bounded retries. Agent reasoning can remain in Factory report analysis and request another bounded diagnostic job; a resident LLM is optional, not required for execution or recovery. All prior references to lab-agent judgment describe that optional future role. One scored or profiling GPU job at a time per Spark; independent qualified hosts can run in parallel. Polling can be replaced by other transport later without changing job semantics. At-least-once delivery requires idempotent claim/start/export, generation fencing and confirmed stop before retry; do not promise exactly-once GPU execution. A cancellation acknowledgement is distinct from a stop request. Manager gateway carries control and evidence references; scoped artifact fetch/upload may carry large bytes directly without exposing another experiment API. Manager may be a module in the existing Factory service with its existing database. Worker may include the Incus adapter and profiler wrappers as modules; a protected client can be a subprocess in the management container. No separate network actuator is required. Trusted worker credentials remain scoped and unavailable to reasoning agents or the engine. Factory job IDs cover full experiments and differ from Incus operation IDs. After event disconnection, reconcile actual operation/instance state because events need not replay. Release GPU admission while waiting for agent reasoning. This is a recommendation for discussion, not a claimed deployed or accepted implementation.

## Slide 12

A2  Required observability: producer, units, and diagnostic value
Normal trials keep lightweight evidence; extra capture is bounded by the question and declared tool policy.
Every output retains version / identity / coverage; unsupported or missing data is never reported as zero
A2
Producer / tool
Evidence and native units
Location / prerequisites / useful outcome
NVTX + CUDA / CUPTI via Systems
phase/site IDs; API/device intervals ns; copies bytes
Hooks in engine; profiler in workload; correlate launch gaps / transfers / synchronization
Compute
selected-kernel ns; bytes; occupancy / throughput ratios
Separate replay; permitted counters/metrics; explain compute or memory limitation
CPU scheduling / sampling
thread states, samples, CPU time ns / throttling
Qualified perf permissions; identify CPU starvation or submission overhead
cgroup + /proc + supported NVML
bytes/peak, faults, I/O bytes, OOM/swap; supported GPU signals
Protected host collector; verify CUDA/GB10 coverage; allocation and pressure hypotheses
Engine diagnostics
routes / misses counts; queue ms; state bytes / lifetimes
Versioned engine producer + batch/request map; distinguish routing, residency and execution
Trial / correctness runner
raw SSE, TTFT ms, tokens/s, numerical / state results
Client in management container; tokenizer/reference identity; matched serving comparison
Provenance + evidence export
digests, generations, settings, loss / failure flags
Factory manifest + receipt; repeat or interpret experiment without guessing its inputs
Targeted fault / I/O tracing only for a defined question; no mandatory custom CUPTI service or eBPF subsystem.

Speaker-note text (package numbering):

NVTX and CUDA trace correlations use Systems including CUPTI/tool integrations; do not imply all events come from hardware counters. CPU scheduling and sampling are separate captures and permissions. Compute collection may replay/serialize or instrument, depending on metrics and mode; record settings. NVML fields on GB10 must be probed, not assumed complete. cgroup/proc/NVML are overlapping views. Targeted eBPF/perf fault/I/O instrumentation is conditional on a question/kernel qualification, not a baseline requirement. All producers retain native format/options, monotonic clock/correlation, data loss/truncation and unit conversions. Keep request/phase/layer/expert association where supported; many-to-many mappings need a manifest. No aggregate duration sum across overlapping kernels without interval-aware calculation. Factory stores raw reports and parsed summaries so analyzers can improve without new GPU execution.
Sources
https://docs.nvidia.com/nsight-systems/UserGuide/index.html
https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html
https://docs.kernel.org/admin-guide/cgroup-v2.html
https://developer.nvidia.com/ERR_NVGPUCTRPERM
https://linuxcontainers.org/incus/docs/main/reference/devices_gpu/
POST-WORKSHOP DESIGN ALIGNMENT
The top-level product contract is separate from reusable capability capsules and from the released engine image. Tool CCs support the workflow; component CC assets may be incorporated into engine code. The engine has its own runtime, without an engine CC wrapper. Lab manager belongs to Software Factory. Lab executor and protected client run in a separate management container outside the disposable Incus experiment. Durable job/stage checkpoints and evidence receipts remain in Factory. A failed attempt is restarted with a new generation after confirmed stop, not resumed as a partially scored run. Runtime settings may change only within the permitted contract and retain configuration identity; source changes require a rebuilt image.
Source: supplied AI4Research Workshop Key Takeaways (Nov6) and post-presentation directions.
MANAGER / EXECUTOR RECOMMENDATION
Proposed simplest first implementation: the Factory exposes one asynchronous Lab Manager API. Builder submits identified releases/playbooks and receives a durable job ID, then continues other work. A deterministic worker in a separate management container polls/claims assigned jobs, emits heartbeat/stage events and returns artifact manifests/results through Manager. No separate public worker API or message broker is required initially. Manager owns admission, cancellation, generation/lease and durable status; trusted platform actuation owns narrowly allowed Incus operations. The worker follows permitted playbook stages and bounded retries. Agent reasoning can remain in Factory report analysis and request another bounded diagnostic job; a resident LLM is optional, not required for execution or recovery. All prior references to lab-agent judgment describe that optional future role. One scored or profiling GPU job at a time per Spark; independent qualified hosts can run in parallel. Polling can be replaced by other transport later without changing job semantics. At-least-once delivery requires idempotent claim/start/export, generation fencing and confirmed stop before retry; do not promise exactly-once GPU execution. A cancellation acknowledgement is distinct from a stop request. Manager gateway carries control and evidence references; scoped artifact fetch/upload may carry large bytes directly without exposing another experiment API. Manager may be a module in the existing Factory service with its existing database. Worker may include the Incus adapter and profiler wrappers as modules; a protected client can be a subprocess in the management container. No separate network actuator is required. Trusted worker credentials remain scoped and unavailable to reasoning agents or the engine. Factory job IDs cover full experiments and differ from Incus operation IDs. After event disconnection, reconcile actual operation/instance state because events need not replay. Release GPU admission while waiting for agent reasoning. This is a recommendation for discussion, not a claimed deployed or accepted implementation.

## Slide 13

A3  Qualification and recovery across failure boundaries
Recovery preserves attribution and completed evidence, then starts a bounded new attempt when safe.
Proposed recovery protocol • workflow checkpoint ≠ suspended CUDA / KV state • known CUDA fixture ≠ Muse validation
A3
Boundary / test
Required behavior
Evidence retained
GPU / profiler qualification
Known CUDA kernel + NVTX through Incus and Docker; Systems and Compute grants separately
driver/tools/image IDs, trace coverage, denied or unsupported metrics
Engine exit / timeout
Worker detects exit, preserves partial reports, confirms stop; finite retry of same release
exit/OOM/timeout, attempt generation, incomplete coverage, retry reason
Incus experiment loss
Worker survives; actuator recreates from manifest and declared clean state
job-stage checkpoint, image/model/config/profile IDs, new generation
Lab executor / client loss
Factory manager detects missing heartbeat; fence old attempt before reassigning
lease/status history, confirmed-stop or unresolved status; no duplicate score
GPU / host failure
Stop admission; diagnose driver/device state; platform recovery when required
host/GPU errors and last durable checkpoint; local trace loss explicit
Export / retention failure
Keep protected staging; bounded resend; pause admission when storage exhausted
manifest + Factory receipt before cleanup; pending export remains pending
Actual Muse acceptance
Approved release/checkpoint/config and independent correctness/performance fixtures
real engine result and coverage, distinct from CUDA fixture qualification
Retry exhaustion returns a failed / inconclusive result to Factory. Repeated crashes trigger a Builder request.

Speaker-note text (package numbering):

Qualification includes identified ARM64 image/userspace, compatible GPU libraries/device exposure across nested boundaries, read-only code/inputs, bounded writes and independent profiling permissions. Disposable fixture validates lab functions only. Engine crashes normally leave Incus alive; separate management additionally survives experiment OOM or destruction. Containerizing management avoids requiring an agent on raw host, but both may share host kernel, GPU driver and physical memory, so reserve and host-level failure recovery remain necessary. Manager must not launch duplicate scored work on an unknown previous attempt: lease/generation and confirmed fencing/stop are proposed safeguards, not existing implementation claims. Store last completed stage and artifact receipt, not claims that every byte of in-flight profiler state survives. Retry caps/backoff/error classes are supplied policy. A deterministic candidate crash should stop after budget and return evidence; no in-lab patch. Incus snapshots are filesystem backup mechanisms; stateful container backup has CRIU limitations and does not establish CUDA context/KV/graph restoration. GPU driver faults may need host/platform action; recreating Incus alone is not a universal repair. Incremental durable export limits loss, subject to report flush/support. Retention failure pauses new work rather than deleting unexported reports.
Sources
https://linuxcontainers.org/incus/docs/main/reference/devices_gpu/
https://docs.nvidia.com/nsight-systems/UserGuide/index.html
https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html
https://linuxcontainers.org/incus/docs/main/howto/instances_backup/
https://docs.nvidia.com/deploy/xid-errors/analyzing-xid-catalog.html
POST-WORKSHOP DESIGN ALIGNMENT
The top-level product contract is separate from reusable capability capsules and from the released engine image. Tool CCs support the workflow; component CC assets may be incorporated into engine code. The engine has its own runtime, without an engine CC wrapper. Lab manager belongs to Software Factory. Lab executor and protected client run in a separate management container outside the disposable Incus experiment. Durable job/stage checkpoints and evidence receipts remain in Factory. A failed attempt is restarted with a new generation after confirmed stop, not resumed as a partially scored run. Runtime settings may change only within the permitted contract and retain configuration identity; source changes require a rebuilt image.
Source: supplied AI4Research Workshop Key Takeaways (Nov6) and post-presentation directions.
MANAGER / EXECUTOR RECOMMENDATION
Proposed simplest first implementation: the Factory exposes one asynchronous Lab Manager API. Builder submits identified releases/playbooks and receives a durable job ID, then continues other work. A deterministic worker in a separate management container polls/claims assigned jobs, emits heartbeat/stage events and returns artifact manifests/results through Manager. No separate public worker API or message broker is required initially. Manager owns admission, cancellation, generation/lease and durable status; trusted platform actuation owns narrowly allowed Incus operations. The worker follows permitted playbook stages and bounded retries. Agent reasoning can remain in Factory report analysis and request another bounded diagnostic job; a resident LLM is optional, not required for execution or recovery. All prior references to lab-agent judgment describe that optional future role. One scored or profiling GPU job at a time per Spark; independent qualified hosts can run in parallel. Polling can be replaced by other transport later without changing job semantics. At-least-once delivery requires idempotent claim/start/export, generation fencing and confirmed stop before retry; do not promise exactly-once GPU execution. A cancellation acknowledgement is distinct from a stop request. Manager gateway carries control and evidence references; scoped artifact fetch/upload may carry large bytes directly without exposing another experiment API. Manager may be a module in the existing Factory service with its existing database. Worker may include the Incus adapter and profiler wrappers as modules; a protected client can be a subprocess in the management container. No separate network actuator is required. Trusted worker credentials remain scoped and unavailable to reasoning agents or the engine. Factory job IDs cover full experiments and differ from Incus operation IDs. After event disconnection, reconcile actual operation/instance state because events need not replay. Release GPU admission while waiting for agent reasoning. This is a recommendation for discussion, not a claimed deployed or accepted implementation.

## Slide 14

A4  Detailed contract and ontology references
A proposed release specification produced from intent and ontology, separate from the CC declaration schema.
Conceptual fields for alignment • no new mandatory CC schema or finished contract-compiler implementation is claimed
A4
Contract section
What it defines
How it connects
Target / environment
model/checkpoint, hardware, constraints and limitations
Input to planning, resource qualification and release checks
System ontology
domain elements, relationships, behaviors, identity/version
Common references for code, component mapping and observations
Requirements / acceptance
functional behavior, numerical/quality criteria, serving measurements
Gates and verification fixtures for the delivered product
Dependencies / CC references
selected tool capabilities and candidate component implementations
Planner/Builder resolves compatible versions and composition
Permitted changes / effects
configuration freedoms, resource envelope, allowed operations
Automation remains inside intent and approval boundaries
Release / verification plan
expected image/manifest, startup interface, tests and evidence
Lab receives identified release plus bounded experiment playbook
Compiler output
contract + ontology reference
known facts + unresolved choices
Realization-space representation remains an alignment question.
Fundamental requirement changes require human approval; permitted implementation choices can iterate automatically.

Speaker-note text (package numbering):

This is an illustrative conceptual contract inventory, not cc-request/2 or proposed mandatory fields for the ontology team. Intent compilation obtains model, hardware and environment requirements from natural language and other sources, asks for missing information and links a manual initial domain ontology. Requirements/contract compilation records obligations, dependencies, gates, verification and allowed degrees of freedom. Planner chooses workflows and CCs, Builder realizes a package and Lab supplies evidence. The exact division between intent and requirements compilers remains an alignment choice. Known requirements, implementation claims and observed evidence must remain distinguishable. Missing information is unresolved, not implied permission to violate constraints. Realization space was discussed as an output concept but its representation and producing stage are not settled. A separate request for a missing CC can still use the existing partial CC request schema; that is not the whole product contract. Requirements that change core intent require human approval under the supplied policy; runtime tuning and CC selection may be automated if explicitly allowed.
Sources
https://github.com/Stellven/jiuwenswarm/tree/a838b97048b2c561212ccfa82b5d414c39359dc9
POST-WORKSHOP DESIGN ALIGNMENT
The top-level product contract is separate from reusable capability capsules and from the released engine image. Tool CCs support the workflow; component CC assets may be incorporated into engine code. The engine has its own runtime, without an engine CC wrapper. Lab manager belongs to Software Factory. Lab executor and protected client run in a separate management container outside the disposable Incus experiment. Durable job/stage checkpoints and evidence receipts remain in Factory. A failed attempt is restarted with a new generation after confirmed stop, not resumed as a partially scored run. Runtime settings may change only within the permitted contract and retain configuration identity; source changes require a rebuilt image.
Source: supplied AI4Research Workshop Key Takeaways (Nov6) and post-presentation directions.
MANAGER / EXECUTOR RECOMMENDATION
Proposed simplest first implementation: the Factory exposes one asynchronous Lab Manager API. Builder submits identified releases/playbooks and receives a durable job ID, then continues other work. A deterministic worker in a separate management container polls/claims assigned jobs, emits heartbeat/stage events and returns artifact manifests/results through Manager. No separate public worker API or message broker is required initially. Manager owns admission, cancellation, generation/lease and durable status; trusted platform actuation owns narrowly allowed Incus operations. The worker follows permitted playbook stages and bounded retries. Agent reasoning can remain in Factory report analysis and request another bounded diagnostic job; a resident LLM is optional, not required for execution or recovery. All prior references to lab-agent judgment describe that optional future role. One scored or profiling GPU job at a time per Spark; independent qualified hosts can run in parallel. Polling can be replaced by other transport later without changing job semantics. At-least-once delivery requires idempotent claim/start/export, generation fencing and confirmed stop before retry; do not promise exactly-once GPU execution. A cancellation acknowledgement is distinct from a stop request. Manager gateway carries control and evidence references; scoped artifact fetch/upload may carry large bytes directly without exposing another experiment API. Manager may be a module in the existing Factory service with its existing database. Worker may include the Incus adapter and profiler wrappers as modules; a protected client can be a subprocess in the management container. No separate network actuator is required. Trusted worker credentials remain scoped and unavailable to reasoning agents or the engine. Factory job IDs cover full experiments and differ from Incus operation IDs. After event disconnection, reconcile actual operation/instance state because events need not replay. Release GPU admission while waiting for agent reasoning. This is a recommendation for discussion, not a claimed deployed or accepted implementation.

## Slide 15

A5  Illustrative release package for the Muse engine
The contract specifies the deliverable. Builder assembles an image and manifest that the lab runs as an application.
Illustrative product manifest, not CC YAML • no existing Muse image, checkpoint values or verified launch command is implied
A5
Release material
Identified content
Consumer / use
Engine image
future immutable ARM64 OCI digest + source/build receipt
Lab actuator stages and launches the application
Native runtime interface
entrypoint, startup config, endpoint and readiness protocol
Actuator verifies ready generation; client sends native HTTP/SSE
Model / configuration
approved checkpoint, prepared weights, tokenizer/template, effective settings
Engine loads read-only inputs; trial records exact identities
Component bill of materials
incorporated CC/module versions, libraries, kernels, interface checks
Builder traces parts to source; diagnostics map back to components
Instrumentation manifest
NVTX sites, counters, schema/version, supported controls
Lab chooses captures and reports actual vs expected coverage
Contract + verification material
contract/ontology version, acceptance fixtures, allowed policies
Lab assesses release under the supplied gates
Experiment result association
release + run + attempt/generation + tools + environment
Factory retains observations separately from release claims
CCs can contribute parts to the image. The image has its own execution and deployment contract.

Speaker-note text (package numbering):

This appendix replaces the earlier completed engine CC specimen. The product is no longer wrapped as an engine CC. These are conceptual release-package contents, not a fabricated validated schema. No runnable image or verified Muse launch command is supplied. The image contains application code and dependencies; weights/config/fixtures can be separately identified read-only mounts to avoid image bloat. Tool CCs used to build the image are recorded in build provenance but need not ship in it. Component CC implementations incorporated into code or linked libraries appear in component/build records. Which component packaging patterns prove practical must be tested. Startup interface/readiness are owned by the released application and deployment integration, not a CC serves wrapper around inference. The protected client speaks the engine API directly. Immutable release plus effective launch/environment identities supports repeatability, while actual results remain separate evidence. Runtime policy changes allowed by contract require a new identified configuration/attempt; source or binary changes require rebuilt image.
Sources
https://github.com/Stellven/jiuwenswarm/tree/a838b97048b2c561212ccfa82b5d414c39359dc9
https://linuxcontainers.org/incus/docs/main/reference/devices_gpu/
POST-WORKSHOP DESIGN ALIGNMENT
The top-level product contract is separate from reusable capability capsules and from the released engine image. Tool CCs support the workflow; component CC assets may be incorporated into engine code. The engine has its own runtime, without an engine CC wrapper. Lab manager belongs to Software Factory. Lab executor and protected client run in a separate management container outside the disposable Incus experiment. Durable job/stage checkpoints and evidence receipts remain in Factory. A failed attempt is restarted with a new generation after confirmed stop, not resumed as a partially scored run. Runtime settings may change only within the permitted contract and retain configuration identity; source changes require a rebuilt image.
Source: supplied AI4Research Workshop Key Takeaways (Nov6) and post-presentation directions.
MANAGER / EXECUTOR RECOMMENDATION
Proposed simplest first implementation: the Factory exposes one asynchronous Lab Manager API. Builder submits identified releases/playbooks and receives a durable job ID, then continues other work. A deterministic worker in a separate management container polls/claims assigned jobs, emits heartbeat/stage events and returns artifact manifests/results through Manager. No separate public worker API or message broker is required initially. Manager owns admission, cancellation, generation/lease and durable status; trusted platform actuation owns narrowly allowed Incus operations. The worker follows permitted playbook stages and bounded retries. Agent reasoning can remain in Factory report analysis and request another bounded diagnostic job; a resident LLM is optional, not required for execution or recovery. All prior references to lab-agent judgment describe that optional future role. One scored or profiling GPU job at a time per Spark; independent qualified hosts can run in parallel. Polling can be replaced by other transport later without changing job semantics. At-least-once delivery requires idempotent claim/start/export, generation fencing and confirmed stop before retry; do not promise exactly-once GPU execution. A cancellation acknowledgement is distinct from a stop request. Manager gateway carries control and evidence references; scoped artifact fetch/upload may carry large bytes directly without exposing another experiment API. Manager may be a module in the existing Factory service with its existing database. Worker may include the Incus adapter and profiler wrappers as modules; a protected client can be a subprocess in the management container. No separate network actuator is required. Trusted worker credentials remain scoped and unavailable to reasoning agents or the engine. Factory job IDs cover full experiments and differ from Incus operation IDs. After event disconnection, reconcile actual operation/instance state because events need not replay. Release GPU admission while waiting for agent reasoning. This is a recommendation for discussion, not a claimed deployed or accepted implementation.

## Slide 16

A6  NVTX tool CC: skill materials plus finite executable helpers
Reusable instructions guide the agent; checked code performs repetitive source edits and verifies their outputs.
Illustrative prebuilt tool contract • examples are schema-checked; no claim arbitrary semantics can be inferred automatically
A6
cc: "2"
id: tools.nvtx.engineering
version: 0.1.0
bindings:
  helpers: ... # pinned implementation
materials:
  instructions: {path: SKILL.md}
  rules: {path: placement-rules.json}
  helpers: {path: helpers/README.md}
capabilities:
  inspect: ...
  check_plan: ...
  apply: ...
  check_build: ...
# Each: does / using / takes / gives
# Narrow needs / changes per action
Capability
Takes → gives
inspect
source snapshot + question → anchored sites / existing hooks / unknowns
check_plan
agent-authored plan + base → checked ranges / naming / scope violations
apply
checked plan + exact base → patch / new snapshot / marker manifest
check_build
source + recipe + optional lab coverage → build/check record; missing coverage explicit
SKILL + rules / regression cases
async/fusion/graphs, exits/thread ownership, gated paths, duplicate/stale edits
Inspection reads. Apply writes a builder workspace. Build/check may execute. Grants stay specific to each action.
Lab reads coverage and reports missing sites. Builder applies changes and submits a newly identified engine image.

Speaker-note text (package numbering):

Full specimen examples/final-nvtx-cc.yaml passes pinned read_yaml+normalize schema checks. This does not execute the tool. Instructions/rules are materials, not invented root skill/system fields. inspect finds candidates/build paths; it does not prove semantic placement. The agent creates a placement plan with source fingerprint, domain/name/category/payload, phase/layer/component reference if supplied, range type/lifetime, expected fixture and participant mapping. check_plan validates mechanical constraints. apply rejects a changed base and avoids duplicate hooks, returning an identified new snapshot/patch/manifest. check_build uses builder validation to verify compiled/emitted coverage and numerical smoke checks. Lab independent coverage is acquisition over the immutable submitted image, never permission to apply a patch there. Source workspace read/write and process effects vary per action; do not grant the union to every helper. Regression cases include stale base, twice-applied patch, early exits, wrong thread, compiled-out branch, fused operation and graph replay. guarantees describe commitments to assess, not automatically enforce truth.
Sources
https://github.com/Stellven/jiuwenswarm/tree/a838b97048b2c561212ccfa82b5d414c39359dc9
https://nvidia.github.io/NVTX/
https://nvidia.github.io/NVTX/doxygen/group___m_a_r_k_e_r_s___a_n_d___r_a_n_g_e_s.html
https://docs.nvidia.com/nsight-systems/UserGuide/index.html
TERMS AND BOUNDARY
The complete NVTX specimen check_build takes source snapshot, marker manifest, declared build recipe and optional returned lab_coverage. It checks available build/smoke records and reports absent execution evidence explicitly. It does not secretly acquire GPU/model grants or invent a fixture that was not supplied. The rendered table is a compact excerpt; full field definitions live in the example.
POST-WORKSHOP DESIGN ALIGNMENT
The top-level product contract is separate from reusable capability capsules and from the released engine image. Tool CCs support the workflow; component CC assets may be incorporated into engine code. The engine has its own runtime, without an engine CC wrapper. Lab manager belongs to Software Factory. Lab executor and protected client run in a separate management container outside the disposable Incus experiment. Durable job/stage checkpoints and evidence receipts remain in Factory. A failed attempt is restarted with a new generation after confirmed stop, not resumed as a partially scored run. Runtime settings may change only within the permitted contract and retain configuration identity; source changes require a rebuilt image.
Source: supplied AI4Research Workshop Key Takeaways (Nov6) and post-presentation directions.
MANAGER / EXECUTOR RECOMMENDATION
Proposed simplest first implementation: the Factory exposes one asynchronous Lab Manager API. Builder submits identified releases/playbooks and receives a durable job ID, then continues other work. A deterministic worker in a separate management container polls/claims assigned jobs, emits heartbeat/stage events and returns artifact manifests/results through Manager. No separate public worker API or message broker is required initially. Manager owns admission, cancellation, generation/lease and durable status; trusted platform actuation owns narrowly allowed Incus operations. The worker follows permitted playbook stages and bounded retries. Agent reasoning can remain in Factory report analysis and request another bounded diagnostic job; a resident LLM is optional, not required for execution or recovery. All prior references to lab-agent judgment describe that optional future role. One scored or profiling GPU job at a time per Spark; independent qualified hosts can run in parallel. Polling can be replaced by other transport later without changing job semantics. At-least-once delivery requires idempotent claim/start/export, generation fencing and confirmed stop before retry; do not promise exactly-once GPU execution. A cancellation acknowledgement is distinct from a stop request. Manager gateway carries control and evidence references; scoped artifact fetch/upload may carry large bytes directly without exposing another experiment API. Manager may be a module in the existing Factory service with its existing database. Worker may include the Incus adapter and profiler wrappers as modules; a protected client can be a subprocess in the management container. No separate network actuator is required. Trusted worker credentials remain scoped and unavailable to reasoning agents or the engine. Factory job IDs cover full experiments and differ from Incus operation IDs. After event disconnection, reconcile actual operation/instance state because events need not replay. Release GPU admission while waiting for agent reasoning. This is a recommendation for discussion, not a claimed deployed or accepted implementation.

## Slide 17

A7  Bounded experiments before adopting persistent execution
Future investigations after a runnable engine and qualified lab exist; none blocks the first immutable evaluation loop.
Budgets are stop limits, not completion promises • sequential GPU measurements; preserve incomplete / unsupported outcomes
A7
Experiment / question
Procedure and bound
Decision evidence
E1  Where is time spent?
2 workloads; ≤5 paired fresh / warm blocks each; 1 GPU-hour. Split staging/loading/warmup/graph/trial.
Setup share, valid experiments/hour and spread. Fresh process ≠ cold storage.
E2  Is same-image reuse safe?
10 A–B–A session/cancel cycles vs fresh warm reference; 1 GPU-hour. Reset KV/queues/RNG/prefix policy.
Outputs/continuation, memory drift, reset time, stale handles. Failure → fresh restart.
E3  Is a cheap tier faithful?
≤4 existing candidates ×2 workloads ×3 repetitions; all also get full validation. ≤1 builder-day +1 GPU-hour.
Real captured activations/routes; false rejects and gain-sign reversals beyond A/A noise.
E4  Can code load/restore work?
One expert projection; 2 submitted modules; 5 A–B–A cycles. ≤1 builder-day +1 GPU-hour.
Actual loaded-module IDs; drain/graph restore, correctness, memory growth and total job cost.
E4 is a feasibility spike: static function selection is not hot reload; a working module loader is not full TKCC.
Every candidate remains builder-produced. New observability or implementation code returns as a new release.

Speaker-note text (package numbering):

Detailed protocols are retained in the notebook Future experiments note and research/final-technical-notes.md. Fixed inputs, correct reference policy, image/model/config/tool IDs and cache/reset conditions precede all runs. E1 prestages images/weights, measures build/delivery separately, and retains incomplete sample counts if1hour expires. E2 compares equivalently warmed fresh engines, not cold versus warm disguised as gain; cancellation sentinel and continuation checks detect leakage. E3 harness is builder-produced immutable software with real captured activation/route identities; initially slow-tier-confirm every candidate to identify false negatives. Few-layer gain never substitutes for full quality/state evaluation. E4 requires an actual compatible loading boundary; otherwise unsupported is useful. Package modules immutably outside lab, record loaded digest/generation, quiesce kernels and manage graph/function/buffer lifetimes. Crash/unknown context forces process restart. Profile only a targeted diagnostic if needed; never score profiled wall time. Compute is not mandatory for any pilot. No universal variance/quality threshold is invented; use supplied policy and baseline noise. Report effort consumed and break-even future candidate count.
Sources
https://www.together.ai/blog/together-compiler-continual-compilation-for-ai-inference
https://www.together.ai/together-compiler-paper
https://docs.nvidia.com/nsight-systems/UserGuide/index.html
https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html
DETAILED TECHNICAL BACKING
A7 — Four bounded experiments
Prerequisite for E1/E2: an admitted working engine/image and two supplied representative workloads; image/model files already staged. One GPU at a time. The following are pilot effort limits, not expected completion times or general acceptance thresholds. Budget expiry yields incomplete evidence, not a pass/fail on engine merit.
| Pilot | Fixture/repetitions and stop budget | Observe/check | Decision |
|---|---|---|---|
| E1 startup decomposition | Five paired fresh-start / same-image-warm blocks per workload; two workloads; one GPU-hour | staging, launch, load, warmup/autotune/graph, trial wall seconds; rate/peak/correctness; actual cache state | Is startup large enough to justify reuse work? Fresh process is not cold SSD/page cache. |
| E2 same-image reset | Ten A–B–A request/session/cancel cycles against fresh-engine warm reference; one GPU-hour | reset KV/session/RNG/scheduler/prefix state; continuation/sentinel correctness; memory drift; stale handles | Reuse only within demonstrated state/reset coverage. Leak/unknown state → fresh restart. No implementation reload. |
| E3 cheap-tier fidelity | Builder supplies immutable single-Muse-block harness and real captured activations; up to four prebuilt candidates; two workloads; three repetitions; one builder-day plus one GPU-hour | initially run all candidates in cheap and full tier; detect false rejects/sign reversals beyond A/A noise; validate numerical boundaries | Useful screening must save total experiment time without hiding full-tier wins/regressions. Full quality remains mandatory. |
| E4 hotload boundary | Optional builder-supplied image with equivalent A/B projection modules; five A–B–A cycles; one builder-day plus one GPU-hour | actual module/code identity; drain in-flight work; load/reset/graph recapture/unload/wall time; outputs/memory drift | Go only with compatible boundary, rollback and real loaded identity. Otherwise unsupported/no-go; static selection is not hot reload. |
Every cycle records image/product/module, environment, fixture, state policy, run/generation and raw outputs. E4 recovery after crash or unknown state is a clean engine restart. No retry silently repeats uncertain effects. The lab spends bounded observation effort; implementation changes remain Builder-side.
POST-WORKSHOP DESIGN ALIGNMENT
The top-level product contract is separate from reusable capability capsules and from the released engine image. Tool CCs support the workflow; component CC assets may be incorporated into engine code. The engine has its own runtime, without an engine CC wrapper. Lab manager belongs to Software Factory. Lab executor and protected client run in a separate management container outside the disposable Incus experiment. Durable job/stage checkpoints and evidence receipts remain in Factory. A failed attempt is restarted with a new generation after confirmed stop, not resumed as a partially scored run. Runtime settings may change only within the permitted contract and retain configuration identity; source changes require a rebuilt image.
Source: supplied AI4Research Workshop Key Takeaways (Nov6) and post-presentation directions.
MANAGER / EXECUTOR RECOMMENDATION
Proposed simplest first implementation: the Factory exposes one asynchronous Lab Manager API. Builder submits identified releases/playbooks and receives a durable job ID, then continues other work. A deterministic worker in a separate management container polls/claims assigned jobs, emits heartbeat/stage events and returns artifact manifests/results through Manager. No separate public worker API or message broker is required initially. Manager owns admission, cancellation, generation/lease and durable status; trusted platform actuation owns narrowly allowed Incus operations. The worker follows permitted playbook stages and bounded retries. Agent reasoning can remain in Factory report analysis and request another bounded diagnostic job; a resident LLM is optional, not required for execution or recovery. All prior references to lab-agent judgment describe that optional future role. One scored or profiling GPU job at a time per Spark; independent qualified hosts can run in parallel. Polling can be replaced by other transport later without changing job semantics. At-least-once delivery requires idempotent claim/start/export, generation fencing and confirmed stop before retry; do not promise exactly-once GPU execution. A cancellation acknowledgement is distinct from a stop request. Manager gateway carries control and evidence references; scoped artifact fetch/upload may carry large bytes directly without exposing another experiment API. Manager may be a module in the existing Factory service with its existing database. Worker may include the Incus adapter and profiler wrappers as modules; a protected client can be a subprocess in the management container. No separate network actuator is required. Trusted worker credentials remain scoped and unavailable to reasoning agents or the engine. Factory job IDs cover full experiments and differ from Incus operation IDs. After event disconnection, reconcile actual operation/instance state because events need not replay. Release GPU admission while waiting for agent reasoning. This is a recommendation for discussion, not a claimed deployed or accepted implementation.

## Slide 18

A8  Resource limits: safety envelope versus inference experiment
Incus bounds the experiment; management has a separate budget; admission serializes scored GPU work.
Actual budgets follow host headroom / CUDA accounting qualification • no selected 64/112 GiB profile or GB10 MIG assumption
A8
Resource / control
Enforcement boundary
Qualification evidence
CPU / processes
Eligible CPUs or time quota; process cap. CPU count is not exclusive reservation.
effective cpuset/quota, CPU time/throttling; bounded process rejection
RAM / swap
Experiment limit includes Docker + tools + candidate. Management has a separate reserve.
allocation-path probes, parent/child bytes + OOM/swap; effective memory.swap.max
Storage capacity
Root quota plus supported quotas for cache/scratch/report volumes; not arbitrary bind paths.
backend/mount map; bounded disposable fill and retained report export
Storage I/O
Backing-device bytes/s or IOPS where supported; cached reads bypass throttling.
real-device vs warm-cache read bytes/time; same-disk / backend restrictions
GPU access / profiling
Selected GPU + separate trace/counter grants; not GPU-memory or compute partition.
known CUDA + NVTX, Systems/Compute separately; actual supported metrics
Project / admission
Aggregate configured instance limits + one scored GPU experiment at a time.
over-budget request rejected; no CPU-pinning / aggregate-quota conflation
Engine experiment budget
Expert-cache/state/residency controls, distinct from outer safety RAM limit.
actual lookup/miss/state evidence under unchanged outer profile
Retain the effective resource profile with every result. Changing limits can change the inference workload.

Speaker-note text (package numbering):

Incus hard limits govern accounting represented by the cgroup; CUDA device/managed/mapped paths on integrated Spark need actual driver/allocation tests before calling the limit a total physical GPU budget. Swap=false is not presented as a universal no-swap guarantee; verify installed cgroup/kernel behavior, effective memory.swap.max and actual usage. CPU eligibility/pinning differs from hard time allowance and soft weights. Parent cgroup restrictions bound all descendants. Root disk size does not cap arbitrary host bind mounts; qualify storage backend custom-volume quotas and locate Docker layers/cache separately from scratch/reports. Block I/O limits exclude cached reads and have backing-device/layout restrictions. Project memory/CPU/process quotas sum configured instance limits; CPU-ID pinning is incompatible with aggregate CPU-count quota, and absolute memory is required. GPU device grant is not memory quota or MIG guarantee. Protect host reserve/collector resources outside lab. A named profile in experiment materials is an allowed request; host worker applies actual validated limits. Initial tests use deliberately small disposable CPU/memory/process/disk/CUDA fixtures, not an arbitrary full Muse allocation. OOM/quota denial is retained as failure with diagnostics. Resource-limit changes are experimental factors and cannot masquerade as code gains.
Sources
https://linuxcontainers.org/incus/docs/main/reference/instance_options/
https://linuxcontainers.org/incus/docs/main/reference/devices_disk/
https://linuxcontainers.org/incus/docs/main/howto/storage_volumes/
https://linuxcontainers.org/incus/docs/main/reference/projects/
https://docs.kernel.org/admin-guide/cgroup-v2.html
https://linuxcontainers.org/incus/docs/main/reference/devices_gpu/
DETAILED TECHNICAL BACKING
A8 — Resource controls and honest claims
**Hierarchy:** the experiment parent covers its private runtime, workload and profiler/helper descendants; the separate management container has its own resource reserve. Attempt limits can further constrain the engine/profiler/test children; they cannot exceed ancestors. Host collectors outside that subtree need their own declared budget/reserve. Report which processes each measurement includes. Host kernel/driver/OS and shared services are additional physical context, not free resources.
**CPU:** distinguish placement from throughput. Incus `limits.cpu` controls visible/pinned CPUs; hard allowance uses time quota/period. Percentage allowance is a scheduling-weight/soft mechanism, not an unconditional percentage cap. Preserve effective CPU set and throttling evidence. [Incus CPU controls](https://linuxcontainers.org/incus/docs/main/reference/instance_options/).
**Memory/swap:** record actual cgroup-v2 `memory.current/peak/stat/events`, `memory.max` and swap limit/use/events. `memory.high` pressures/reclaims rather than being the hard maximum. Docker memory+swap flags have different combined semantics from cgroup-v2's swap-only limit. Set/inspect swap explicitly; zero `memory.swap.max` disables new anonymous swap-out. Ancestor limits include all descendants. Never sum GB10 CPU/GPU shared-memory views; qualify actual CUDA/mapping accounting before claiming a physical-memory cap. [cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html), [Docker memory/swap semantics](https://docs.docker.com/engine/containers/resource_constraints/).
**Storage capacity:** root volume size/quota does not automatically cap bind-mounted weights, output or scratch. Apply supported storage-volume/filesystem quotas or bounded paths independently; record available space and truncated outputs. Read-only prohibits writes, not reads or consumption already stored elsewhere. [Incus disk controls](https://linuxcontainers.org/incus/docs/main/reference/devices_disk/).
**Storage traffic:** byte/s or IOPS limits constrain qualified block-device I/O paths; cached reads can be served from RAM and do not establish a throttled SSD experiment. Match backing device, actual read-byte counters and cold/warm policy. Quota/capacity and throughput are different controls. Preserve faults/cache outcomes without treating either as the other's proxy.
**GPU:** device access and supported telemetry do not imply a VRAM quota, SM allocation or MIG partition. GB10 unified memory requires measured coverage; do not invent MIG or a GPU-only memory budget for this target. Serialize scored GPU workloads to control interference. CPU quota does not cap GPU kernels. [Incus GPU device](https://linuxcontainers.org/incus/docs/main/reference/devices_gpu/), [NVIDIA MIG supported hardware](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/supported-gpus.html).
**Profiling:** CPU samples, CUDA activity and GPU counters have separate permissions and overhead. Qualify from inside the final nested workload, not only on the host. Do not grant the whole lab executor unrestricted privileges to pass a probe. A failed permission is unavailable coverage; it is not zero usage. [Systems installation](https://docs.nvidia.com/nsight-systems/InstallationGuide/), [counter permission](https://developer.nvidia.com/ERR_NVGPUCTRPERM).
POST-WORKSHOP DESIGN ALIGNMENT
The top-level product contract is separate from reusable capability capsules and from the released engine image. Tool CCs support the workflow; component CC assets may be incorporated into engine code. The engine has its own runtime, without an engine CC wrapper. Lab manager belongs to Software Factory. Lab executor and protected client run in a separate management container outside the disposable Incus experiment. Durable job/stage checkpoints and evidence receipts remain in Factory. A failed attempt is restarted with a new generation after confirmed stop, not resumed as a partially scored run. Runtime settings may change only within the permitted contract and retain configuration identity; source changes require a rebuilt image.
Source: supplied AI4Research Workshop Key Takeaways (Nov6) and post-presentation directions.
MANAGER / EXECUTOR RECOMMENDATION
Proposed simplest first implementation: the Factory exposes one asynchronous Lab Manager API. Builder submits identified releases/playbooks and receives a durable job ID, then continues other work. A deterministic worker in a separate management container polls/claims assigned jobs, emits heartbeat/stage events and returns artifact manifests/results through Manager. No separate public worker API or message broker is required initially. Manager owns admission, cancellation, generation/lease and durable status; trusted platform actuation owns narrowly allowed Incus operations. The worker follows permitted playbook stages and bounded retries. Agent reasoning can remain in Factory report analysis and request another bounded diagnostic job; a resident LLM is optional, not required for execution or recovery. All prior references to lab-agent judgment describe that optional future role. One scored or profiling GPU job at a time per Spark; independent qualified hosts can run in parallel. Polling can be replaced by other transport later without changing job semantics. At-least-once delivery requires idempotent claim/start/export, generation fencing and confirmed stop before retry; do not promise exactly-once GPU execution. A cancellation acknowledgement is distinct from a stop request. Manager gateway carries control and evidence references; scoped artifact fetch/upload may carry large bytes directly without exposing another experiment API. Manager may be a module in the existing Factory service with its existing database. Worker may include the Incus adapter and profiler wrappers as modules; a protected client can be a subprocess in the management container. No separate network actuator is required. Trusted worker credentials remain scoped and unavailable to reasoning agents or the engine. Factory job IDs cover full experiments and differ from Incus operation IDs. After event disconnection, reconcile actual operation/instance state because events need not replay. Release GPU admission while waiting for agent reasoning. This is a recommendation for discussion, not a claimed deployed or accepted implementation.
