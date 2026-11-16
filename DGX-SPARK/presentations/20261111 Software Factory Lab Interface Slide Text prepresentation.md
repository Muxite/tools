# 20261111 Software Factory Lab Interface prepresentation

Extracted text for search. Slide geometry, diagrams and visual meaning remain in the original deck. This extraction is not a new presentation or a visual review.


## Slide 1

SOFTWARE FACTORY ↔ SPARK LAB  /  PROPOSED INTERFACE
Submit a test, receive a verdict, reuse the evidence
Coding agents submit an image and question. Lab Agent designs, runs and recovers the experiment.
1 / 8
SOFTWARE FACTORY
SPARK LAB ENVIRONMENT
Coder A
Coder B
Builder CC + tools
use
Image + CC catalogs
Lab Manager
route • ingest • reply
task A + image
task B + image
publish
pinned refs
Request + attempt journal
caller ↔ task ↔ lab
Primary logs + artifacts
verdicts + receipts by task
Evidence query / read
coders read retained journals + logs
Lab Agent
investigate • diagnose • analyze
brief + engine image
verdict + requested data
Experiments
setup + lab scripts
Selected tools
+ parameters
prepare
choose / adjust
Brief-local data store
inputs • scripts • run data
read / write for this brief only
Evidence
transfer
upload to Manager
persist
ACK after durable save
receipt to local spool
MANY RUNS  /  WITHIN THIS BRIEF
Container A
Container B
results / observations
Host supervisor restarts Agent; persistent workspace.
reply to original caller
CC = capability capsule. Blue: factory; teal: lab; purple: evidence; amber: recovery. Proposed Spark integration, not qualified.

Speaker-note text (package numbering):

Lab Manager and primary evidence storage are inside Software Factory. The Spark boundary includes Lab Agent and its supervisor outside experimental containers. A brief-local data store retains input copies, scripts, plans, selected tool settings, raw outputs and analysis for this brief only. Separate per-brief namespaces and credentials prevent access to other lab briefs. Evidence transfer calls the Lab Manager interface for JSONL batches and artifact uploads. Lab Manager writes to factory stores and returns durable acknowledgments through the transfer process. The Lab Agent has no direct write path to factory stores. Acknowledgment permits spool deletion, not automatic deletion of the Agent working dataset. Task closeout/retention controls local cleanup. Local storage is not resilient to destruction of its host disk. Arrows are logical payload flows; Agent and harness logs share the mandatory streaming path detailed on slide 5. Multiple coding agents retain independent durable task mappings. Coder B replies use the same caller-keyed path shown for A. Image/CC catalog references travel in the task; credentials are scoped separately. Factory tools produce the submitted immutable image, not a parent manager subsystem. Lab Agent may create experiment scripts, configure environments, adjust parameters and analyze many runs across multiple containers, sequentially or concurrently within task limits. Persistent workspace retains plans, scripts and attempt/container identities. Observations feed the Agent analysis/revision loop; results are not a one-container restriction. Substantial engine/product code development remains in Software Factory.
Sources and evidence scope:
Local current branch: AI4Research-Development/ccv2-work/docs/architecture/README.md; jiuwenswarm/ccv2/schemas/request.schema.json
C:/Users/m50066326/huawei/outputs/milestones/20261110/Muse-Spark-Inference-Factory-Handbook.md
This is a proposed application design. Existing CC discovery and invocation do not establish GPU deployment or Spark qualification. No new experiment results are claimed.

## Slide 2

SOFTWARE FACTORY ↔ SPARK LAB  /  PROPOSED INTERFACE
The coder sends a brief; the Lab Agent returns a verdict
References pin the image, inputs and acceptance policy. The brief specifies returns, not experiment steps.
2 / 8
CODER → MANAGER → LAB AGENT
LAB AGENT → MANAGER → ORIGINAL CODER
schema: lab-task/v1
request_id: test-042
image: {ref: engine@sha256:<digest>}
question: Can this change reduce peak memory?
required_returns:
  policy: returns-policy@v1
  items: [verdict, peak_memory, profile]
inspection_context:
  source: repo@<commit>
  docs: code-state@v3
  changed_areas: [expert_store]
  known_issues: issues@v2
  guidance: inspect-residency@v1
inputs: inputs.lock@v1
resources: spark-budget@v1
constraints: acceptance-and-recovery@v1
available_ccs: catalog@v12
recommended_ccs: [inspector, trace-reader]
schema: lab-result/v1
request_id: test-042
submitted_image: engine@sha256:<digest>
variants: []
attempts: [attempt-01]
verdict: inconclusive
explanation: Required profile was lost.
metrics:
  peak_memory: {value: null,
    unit: bytes, status: unavailable}
evidence: evidence-manifest@v1
selected_ccs: selection.lock@v1
changes: []
recovery_history: recovery-log@v1
limitations: [missing_required_capture]
cleanup: {state: confirmed}
Delivery envelope adds authenticated caller, assignment ID,
lab endpoint, execution generation and telemetry destination.
Required items: verdict present; memory unavailable; profile missing.
Manager reports incomplete evidence; preserves the Lab Agent verdict.
Illustrative references, no measured result. Full examples contain pinned identities, attempts, artifact hashes and stream receipts.

Speaker-note text (package numbering):

Top-level request fields match companion examples. Manager binds caller from authentication rather than trusting a supplied caller string. Delivery metadata is outside the coder task and covers task hash, assignment, fencing generation, endpoint and telemetry scope. Required_returns pins metrics, reports, captures and completion policy. Result fields retain original and actual images, every attempt and policy/workload identity. Unknown measurements remain null/unavailable. Manager validates schema, required outputs and uploaded receipts; it does not reproduce scientific analysis. Conflicting/stale assignment replies are retained for audit but cannot overwrite the active result. Infeasible contracts return a proposal for a revised version; acceptance cannot change silently.
Sources and evidence scope:
C:/Users/m50066326/huawei/outputs/milestones/20261110/Muse-Spark-Inference-Factory-Handbook.md
This is a proposed application design. Existing CC discovery and invocation do not establish GPU deployment or Spark qualification. No new experiment results are claimed.

## Slide 3

SOFTWARE FACTORY ↔ SPARK LAB  /  PROPOSED INTERFACE
Lab Manager routes tasks and retains their records
One durable journal and existing artifact storage support many callers and configured labs.
3 / 8
LAB MANAGER  /  SERVICE INSIDE SOFTWARE FACTORY
Coder A
test-042
Coder B
test-043
Submit / status
cancel / result
Request journal
caller • hash • assignment
A / 042
B / 043
persist before dispatch
FIFO dispatch
compatible + available
queued task
Lab registry
compatibility • availability • task
choose lab
Spark 1
042 active
Spark 2
043 active
042 / gen 1
043 / gen 1
042 reply
Task-scoped read API
Ingest / result records
read
index receipts / attempts / verdict refs
lookup
logs / reply + assignment
Caller-scoped status + results; authorized coders can read journals, logs and artifacts
042 → A
Same ID + content: reuse; conflict: reject. Restart: reconcile. Late assignments stay in audit; cannot replace active results.
One active task per Spark. Confirm old execution stopped or blocked before retry. Cancel waits for a stop receipt.

Speaker-note text (package numbering):

Service uses transactional request journal/index, configured endpoints and existing file/artifact storage. Persist request identity and caller mapping before acceptance, assignment before delivery. Lab accepts a durable idempotent assignment; re-delivery queries same execution rather than launching again. Execution generation is a fencing token only when enforced by the lab runtime; never rely on token issuance alone to stop old containers. No reassignment while prior execution may remain active. Manager restart reconciles assignments and late replies. Queue is FIFO among compatible eligible tasks, not a resource optimization planner. Results retained for disconnected callers. Task status queued/running/unavailable/finished/cancelled is distinct from supported/negative/inconclusive/blocked verdict. No provisioning or autonomous repair inside Manager.
Sources and evidence scope:
C:/Users/m50066326/huawei/outputs/milestones/20261110/Muse-Spark-Inference-Factory-Handbook.md
This is a proposed application design. Existing CC discovery and invocation do not establish GPU deployment or Spark qualification. No new experiment results are claimed.

## Slide 4

SOFTWARE FACTORY ↔ SPARK LAB  /  PROPOSED INTERFACE
Lab Agent investigates the goal and returns useful evidence
Collect the richest relevant data possible within the brief. Failed tests are evidence to investigate, not an automatic handback.
4 / 8
Manager’s brief
question • required returns
resources • limits
Engine image
+ exposed internal signals
Available tools
recommendations + permissions
Lab Agent
plan • investigate • analyze
goal + context
inspect signals
select / use
Run / observe
parameters • scripts • environments
design experiments
Brief-local evidence
measurements • traces • failures
analysis + missing observations
collect + retain
analyze +
diagnose
failure → inspect, adapt, retry
Verdict + evidence
findings • coverage • limitations
return to Manager
Factory work request
if substantial code is needed
via Manager: diagnosis + evidence
Before handback: diagnose the failure,
try other useful observations or tests,
and state what remains unknown.
MANY RUNS / CONTAINERS
One brief; isolated working data.
Local setup and scripts belong to the lab.
INTERNAL SIGNALS + EXTERNAL MEASUREMENTS
Use exposed engine counters, traces and error context
alongside tool measurements. Record unavailable signals.
Stop when the brief is answered, the budget is reached, or safe progress is blocked. Never change acceptance criteria silently.

Speaker-note text (package numbering):

Responsibility-oriented view, not a fixed workflow. Software Factory builds the engine and exposes available internal instrumentation; the Lab Agent combines these signals with external observations and tools. Select tools from the available catalog under grants; recommendations are advisory. Maximize relevant information, not bytes or indefinite retries. A failed smoke test is an observation: capture context, inspect logs/counters, diagnose, adjust environment/settings or lab scripts within limits, and pursue other useful checks before returning. Continue collecting evidence even if the original performance comparison is blocked, when safe and useful. Missing signals remain explicitly unavailable. Findings and diagnostic hypotheses must be distinguished from causally established conclusions. Substantial engine code development returns as an evidence-backed request via Manager to Software Factory, rather than being triggered by any simple failure. Baseline identity and task acceptance remain fixed; local variants are recorded. Agent restart reconciles persistent task state and live containers; stop/fence old execution before retry; whole host loss requires host return/external restoration. Factory receives streams throughout and receives verdict, data, limitations and specific remaining blockers at closeout.
Sources and evidence scope:
C:/Users/m50066326/huawei/outputs/milestones/20261110/Muse-Spark-Inference-Factory-Handbook.md
https://docs.nvidia.com/nsight-systems/AnalysisGuide/index.html
https://opentelemetry.io/docs/specs/otel/logs/data-model/
This is a proposed application design. Existing CC discovery and invocation do not establish GPU deployment or Spark qualification. No new experiment results are claimed.

## Slide 5

SOFTWARE FACTORY ↔ SPARK LAB  /  PROPOSED INTERFACE
Factory stores preserve evidence for the next change
Factory retains shared evidence. Each Lab Agent reads only its own brief-local working data and transfer spool.
5 / 8
SPARK  /  ONE BRIEF’S LOCAL DATA
SOFTWARE FACTORY  /  PRIMARY STORAGE
Agent / tool actions
engine output / resources
Brief-local store
+ transfer spool
Manager
ingestion
JSONL segments
+ stream index
Artifacts + work journals
originals / hashes / receipts
batch replay / upload
ack: saved in factory storage
events
files
Factory coders
+ Builder CC
Agent reads/writes its own brief only; separate data + credentials.
ACK releases spool bytes; working data follows brief retention.
UTF-8 JSONL  /  ONE EVENT PER LINE (WRAPPED HERE)
{"schema":"lab-event/v1","request_id":"test-042",
 "experiment_id":"exp-01","attempt_id":"attempt-01",
 "producer_id":"spark-1","producer_epoch":"boot-7","seq":42,
 "event_time":"2026-11-11T14:00:00Z",
 "observed_time":"2026-11-11T14:00:00.010Z",
 "type":"resource.sample","payload":{"metric":"peak_memory",
 "value":null,"unit":"bytes","status":"unavailable"}}
Replay: ignore duplicate producer / restart ID / sequence.
Conflicts and missing intervals stay visible.
Spool full: stop new trials; flag any lost evidence.
Lost Spark disk can lose unacknowledged data.
Final manifest: each required item + gaps + receipts.
Missing required evidence: report incomplete support.
producer_epoch = unique producer restart ID
Coders
Evidence read API
Index + files
query
read
TRACE   request → experiment → attempt → CC call → image / component → NVTX region → observation
OTel: persistent queues can still lose data. NVIDIA: preserve .nsys-rep; SQLite/CSV are derived. This JSONL is not OTLP wire format.

Speaker-note text (package numbering):

JSONL logs setup, concise actions, calls/results, stdout/stderr chunks, measurements, failures, recovery, transitions and artifact receipts; no private reasoning. Conditional fields cc_call_id/cc_id/cc_version, image_digest/component_refs, artifact refs, scoped CUDA/NVTX correlation. Null experiment/attempt before assignment. Commit durable bytes then index/receipt; recover index after interruption. ACK contiguous sequence positions, not simply highest seen. Local spool cannot survive destroyed Spark disk; unacknowledged missing data becomes explicit gaps. Missing original required capture blocks full support. Original nsys-rep retained, derived SQLite/CSV references parent hash. Attribution points to involved implementation, not proof of causation; controlled comparison required. Existing factory work journals and Builder CC logs are retained alongside original artifacts with their own source schemas; lab-event/v1 is the required format for lab streams, not a forced rewrite of all factory records. Factory coding agents can query request/attempt/image/CC identities and read retained journals, operational events, Lab Agent verdicts and original artifacts under caller/workspace access policy. This is deterministic retrieval, not Manager scientific analysis. An index of prior work lets coders use evidence in later changes; fresh experiments still need a new request. Final status, scientific verdict, evidence completeness, and cleanup independently reported. Runtime integration and end-to-end recovery remain proposed, not implemented or Spark-qualified.
Sources and evidence scope:
https://opentelemetry.io/docs/collector/resiliency/
https://opentelemetry.io/docs/specs/otel/logs/data-model/
https://docs.nvidia.com/nsight-systems/AnalysisGuide/index.html
This is a proposed application design. Existing CC discovery and invocation do not establish GPU deployment or Spark qualification. No new experiment results are claimed.

## Slide 6

SOFTWARE FACTORY ↔ SPARK LAB  /  PROPOSED INTERFACE
Appendix · Lab Agent tools
Proposed packages for turning a question into an executable experiment and a defensible answer.
6 / 8
TOOL CC
INPUT → OUTPUT
EXECUTION CONTEXT / LIMIT
Trial Runner
Trial spec + image → attempt and results
Lab adapter. Reserves resources and starts the existing benchmark harness.
Resource Watch
Attempt scope → resource timeline and gaps
Lab host. Shared-memory counters need scope, units and sampling cadence.
Capture Kit
Capture recipe → original diagnostic report
Lab host. Per-tool grants; profiling may replay or perturb execution.
Experiment Judge
Results + frozen policy → validity and verdict
Read-only analysis. A valid slowdown differs from an invalid test.
Configuration Planner
Capabilities + evidence → candidate settings
Offline analysis. Proposes tests; cannot change acceptance thresholds.
Plan
Trial Runner
Observations
Judge
Answer
Trial Runner is a proposed thin adapter, not a new benchmark or infrastructure scheduler. Tools still require runtime grants.

Speaker-note text (package numbering):

Primary consumers shown, not an exclusivity rule. Trial Runner wraps the chosen benchmark/workload invocation and qualified provider lifecycle, not a new general scheduler or a replacement for the supplied benchmark. Resource Watch covers attributable process/cgroup/host/device observations and unavailable measurements. GPU/UMA views may overlap and cannot simply be summed. Capture Kit wraps separately admitted Nsight Systems/Compute/Sanitizer recipes; it does not provide blanket privileged execution. Experiment Judge applies frozen policy and preserves raw comparison units, workload, uncertainty and missing evidence. Configuration Planner proposes supported settings given inspected versions and calibration. These package boundaries are proposals; scripts are reuse candidates, not finished releases.
Sources and evidence scope:
C:/Users/m50066326/huawei/outputs/milestones/20261110/Muse-Spark-Inference-Factory-Handbook.md
https://docs.nvidia.com/nsight-systems/AnalysisGuide/index.html
This is a proposed application design. Existing CC discovery and invocation do not establish GPU deployment or Spark qualification. No new experiment results are claimed.

## Slide 7

SOFTWARE FACTORY ↔ SPARK LAB  /  PROPOSED INTERFACE
Appendix · Factory coding-agent CC tools
Builder is an existing CC tool. Its image and supporting materials enter the lab brief; Spark qualification is a separate check.
7 / 8
Coding agent
jiuwenswarm
Builder CC
Runtime image
+ build / CC provenance
Weight Workshop CC
Weight pack
+ tensor mapping
Instrumenter CC
Instrumentation patch
+ marker map
build + publish
convert + validate
patch + annotate
Reads prior verdicts + logs
Uses component assets
Calls Builder CC
Separate weights from image.
Record conversion provenance.
instrumentation enters a rebuilt diagnostic image
Builder: pinned source/dependencies → digest + manifest + target checks.
Weight Workshop: source weights → validated pack + conversion provenance.
Instrumenter: source + inspection target → NVTX patch + marker map.
Image contains engine + runtime libraries + integrated components. Weights, workload, source/inspection docs and captures stay separate.

Speaker-note text (package numbering):

Builder is a CC tool per the current design clarification. The proposed lab interface consumes its outputs. Builder reuses upstream build systems/BuildKit as suitable, producing image identity, executable and library hashes, source and component references, build logs and smoke results. Weight Workshop produces a separate immutable pack with tensor mapping/calibration and conversion identity. Instrumenter creates markers and engagement evidence for a specific question. Diagnostic images have separate identities and overhead checks. The repeated agent-to-tools edges mean tool selection, not mandatory execution of all three in every experiment. The dashed return illustrates source instrumentation feeding Builder; it is an artifact dependency, not permission for runtime mutation. A component change or diagnostic patch must pass through a fresh build. Long asynchronous builds require a supported adapter lifecycle; the current cc_call interface cannot simply be extended by assuming an arbitrary timeout field.
Sources and evidence scope:
C:/Users/m50066326/huawei/outputs/milestones/20261110/Muse-Spark-Inference-Factory-Handbook.md
Local current branch: AI4Research-Development/ccv2-work/docs/architecture/README.md; jiuwenswarm/ccv2/schemas/request.schema.json
https://docs.docker.com/build/building/best-practices/
This is a proposed application design. Existing CC discovery and invocation do not establish GPU deployment or Spark qualification. No new experiment results are claimed.

## Slide 8

SOFTWARE FACTORY ↔ SPARK LAB  /  PROPOSED INTERFACE
Appendix · shared tools and engine components
Both Lab Agent and Software Factory can use shared tools. Components enter identified engine variants; tools act in their granted context.
8 / 8
SHARED TOOLS / INSTRUCTIONS
ENGINE COMPONENT CC FAMILIES
Inspector
Model/runtime facts and compatibility gaps
Trace Reader
Saved reports → observations + missing data
Correctness Kit
Reference + fixtures → scoped correctness
Courier
Transfer + identity → receiver receipt
Campaign Notebook
Evidence refs + decisions → campaign index
Field Guide · instructions
Experiment procedure; no execution rights
Weight Reader
Weight pack → correctly typed tensor views
Expert Store
Demand → resident experts / bounded misses
Execution Modules
Qualified kernel, dispatch or fusion changes
Memory / State Modules
Workspace, KV and session lifetimes
Builder CC
integrates
Image
Lab
executes
Tool calls remain separate from component code inside the image. Shared access does not imply identical permissions.
Proposed catalog from the preserved handbook. Passive materials and component assets do not automatically create executable services.

Speaker-note text (package numbering):

Classify by both consumer and kind. Shared Inspector/Trace Reader/Correctness Kit/Courier/Campaign Notebook are tools, with grants depending on operation and context. Field Guide is passive methodology, kept on the shared side but explicitly not a callable tool. Component families are materials/source/library assets integrated by factory and exercised through the built engine in the lab. They are not six more services deployed by Manager. Weight Reader consumes prepared packs; Weight Workshop prepares them. Expert Store owns selected-weight residency/fetch behavior. Execution Modules are scoped kernel/dispatch/fusion interventions. Memory/State Modules govern qualified workspace, KV and state-lifetime changes. Correctness, engagement and matched workload comparison are needed for each component. Trace Reader analyzes saved reports; Capture Kit creates reports. Campaign Notebook is an index of experiments/decisions, not the authoritative Manager telemetry store. New telemetry streaming is a mandatory harness/runtime integration, not an optional CC. All names are proposed package boundaries, not claims of implemented releases.
Sources and evidence scope:
C:/Users/m50066326/huawei/outputs/milestones/20261110/Muse-Spark-Inference-Factory-Handbook.md
Local current branch: AI4Research-Development/ccv2-work/docs/architecture/README.md; jiuwenswarm/ccv2/schemas/request.schema.json
This is a proposed application design. Existing CC discovery and invocation do not establish GPU deployment or Spark qualification. No new experiment results are claimed.
