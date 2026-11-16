# Design continuation: decisions, questions and first vertical slice

## Terminology and boundaries

| Entity | Meaning in the current proposal |
|---|---|
| System ontology + plaintext* | Supplied structured system description plus human intent; ontology representation is still unknown. Collect model/checkpoint, hardware, environment requirements and missing facts without inventing them. |
| Intent / contract compilation | Reconcile known facts with ontology and produce requirements, dependencies, gates, permitted changes and verification obligations. Exact compiler split and realization-space representation remain open. |
| Contract | Definition of the intended release. It can reference many CCs; it is not itself a CC. Missing information remains unresolved rather than unlimited permission. |
| Tool CC | Reusable capability invoked to inspect, annotate, prepare, build, test, profile or analyze. Several capabilities can share an implementation package. |
| Component CC | Reusable implementation/interface/test assets incorporated into engine source, libraries or kernels. The specific incorporation API still needs design. |
| Release image / manifest | Identified runnable application and its build/component/input/runtime references. The engine has its own native interface; no whole-engine CC wrapper. |
| Lab Manager | Factory gateway for submission, admission, status, cancellation, result registration and durable job history. Can be a module using existing Factory storage. |
| Lab executor | Proposed deterministic worker in a separate management container. Includes the Incus adapter, bounded stage wrappers and protected client; a separate reasoning model is optional. |
| Experiment / attempt | A durable requested evaluation and a particular execution generation. A retry is another attempt, not an uninterrupted successful trial. |
| Evidence | Raw reports/events, measured outcomes, coverage/loss flags and identities, retained separately from interpretations and release claims. |

*System ontology format is unknown at time of writing. Do not present a template as already supplied or redefine its semantics in CC.*

## Directions to preserve

- The single Factory box contains compilers, Builder, CC registry, release metadata, Lab Manager and knowledge/telemetry. External executor and Incus are reached through Manager. Scoped artifact uploads may move large bytes directly to Factory storage, but Manager remains the authority for job completion and receipts.
- Reuse Factory workflows for capability production and improvement. CC Factory is a capability-producing function, not a mandatory duplicated production stack. Temporary CC composition and publishing a tested Composite CC are different outcomes.
- Images remain unchanged in the lab. No source workbench, engine rebuild or binary replacement there. Allowed runtime configuration changes retain their own identity; source/instrumentation changes return to Builder and produce a new image.
- Initial deployment proposal remains ARM64 OCI through private Docker inside Incus. Direct Incus OCI is a fallback to investigate if nested GPU/profiling qualification fails, not a second initial implementation path.
- Correctness precedes unprofiled representative timing. Nsight Systems and targeted Nsight Compute are separate bounded diagnostic attempts. Reuse saved reports before capturing again.
- NVTX tool CC combines skill/rules with deterministic inspection, checked placement plans, patching and build checks. Builder applies code changes; lab verifies actual emitted coverage. Host NVTX duration is not GPU completion. Expert misses/residency need engine counters.
- Learned token routing per layer differs from expert weight residency/retrieval. Configuration defaults are not verified checkpoint values. Do not assume DeepSeek-specific attention, shared experts or MTP.
- One Spark admits one scored or profiling GPU experiment at a time. Independent qualified hosts can run in parallel. Queue depth is not hardware capacity; CPU/staging overlap must respect interference and resource budgets.
- Fundamental requirement changes require the applicable human approval. Permitted implementation/configuration/CC choices can iterate within the contract.
- TKCC-style persistence/hot loading and SkyDiscover remain conditional exploration. Collect setup costs and reset-safety evidence before investing in runtime replacement interfaces. Do not transfer external performance results.

## Latest recommendation, still open for discussion

Use a Manager API plus durable job table and deterministic worker. Submit returns a `job_id` immediately so Builder can continue or submit other jobs. A worker polls/claims assigned jobs, runs fixed permitted stages, emits status and exports results. Factory agents analyze reports and submit further bounded jobs. Release hardware while waiting for reasoning.

Reuse an existing Factory service, database or dispatcher if suitable. No separate broker, public worker API, or microservice per tool is required by this proposal. The worker can include the Incus adapter; the client can be a protected subprocess. Exact transport and storage technology should follow the actual integration environment.

An API is an interface; it does not replace the executor. A resident reasoning model is the optional part. Incus operation IDs track infrastructure actions; our job identity tracks the full experiment.

## First design work to complete

| Priority | Work product for the next session | Decision it enables |
|---|---|---|
| 1 | One illustrative release + job submission + result example, with known and unresolved fields marked | Agreement on contract/release/job separation, inputs, allowed runtime knobs and evidence identity |
| 2 | End-to-end sequence and state-transition table for submit, claim, qualify, check, trial, diagnose, export and cleanup | Minimal API/state machine; who can act; terminal outcomes and safe retry points |
| 3 | Failure walkthroughs: duplicate submit, engine crash, worker loss, network loss, cancel, export failure and GPU/host fault | Idempotency, stop confirmation, recovery and bounded retention without duplicate scoring |
| 4 | One tool CC and one component CC integration example | Which existing CC mechanisms suffice; what adapter/module interface, build/test and dependency evidence is needed |
| 5 | Target-environment qualification checklist tied to an actual available Spark | GPU/library/profiler path, credentials, mounts, memory accounting and interference claims that can actually be tested |
| 6 | Observation-to-next-action policy for a few inference hypotheses | Which evidence permits runtime retest, new code/markers, tool upgrade, or contract revision |

Prefer a small, readable design artifact over a finished exhaustive schema. Start from a supplied/illustrative engine image and known CUDA qualification fixture without pretending the latter validates Muse. Do not begin implementation merely because this handoff exists.

## Questions that still need answers

1. What ontology/template will be supplied, and what stable identities/versions connect its elements to code, markers, tests and evidence? What exactly is the proposed realization space?
2. Which existing Factory job/store/agent interfaces are available now? Inspect their current source before selecting a database or introducing a new service.
3. What exact engine startup/readiness/API, component module interface and runtime controls will the first release expose? Which component boundary is worth implementing first?
4. What acceptance workload, tokenizer/template/checkpoint identity, numerical reference and thresholds are supplied? Benchmark policy is external; do not invent acceptance criteria.
5. What Spark/Incus/Docker/driver/tool versions and permissions are actually available? What is the resource safety envelope, separately from engine expert-cache/state budgets?
6. What bounds govern capture time/size, retries, cancellation, evidence retention and unknown state? Which conditions stop a campaign versus request a new release?

## Recovery invariants to design explicitly

| Scenario | Required design outcome |
|---|---|
| Duplicate submit / delivery | Idempotency and generation-aware claims; do not promise exactly-once GPU execution. |
| Engine crash | Preserve exit/partial artifacts, record failed attempt, confirm stop, retry same identified release only within budget. |
| Worker heartbeat lost | Mark state uncertain and reconcile actual resources. Lease expiry is not proof the old work stopped. Fence stale ownership before reassignment. |
| Cancel | Record request, stop owned work, preserve partial evidence, then confirm canceled. Incus operations may not all be cancellable. |
| Event disconnect | Re-fetch tracked operation/instance state; missed Incus events are not resent. |
| Export failure | Keep bounded protected staging, retry registration, pause admission if storage fills. Cleanup follows durable manifest/receipt. |
| GPU/host fault | Suspend admission and use qualified platform recovery. Recreating Incus alone is not a GPU reset. |

Workflow checkpoints preserve job/stage/attempt identities and completed evidence, not live CUDA allocations, graphs or KV state. A new attempt repeats its declared warmup/state policy. Buffered trace loss remains explicit coverage loss.

## Evidence and implementation limits

CC implementation pin: `a838b97048b2c561212ccfa82b5d414c39359dc9` in [Stellven/jiuwenswarm](https://github.com/Stellven/jiuwenswarm/tree/a838b97048b2c561212ccfa82b5d414c39359dc9). The existing `cc-request/2` and completed-capability schema remain unchanged. A retained request fixture has conflicting open pointers under absent-pointer semantics; successful manual materialization did not prove resolver conformance. Inspect the current implementation/status note before implementation claims.

Muse reference: `fd3cf0140de03f7619ac95b5cfed05b711ff9e22`. Strata reference: `ffa80d73133ea5c548aefe57889a16e8085a938f`. DwarfStar reference: `b3f50180ec2c7324892be1f50bc83555ccb8d5e7`. Exact URLs and qualifications are in [evidence-register.md](evidence-register.md).

No new runtime or engine was implemented. No target GPU/profiling/memory/crash test was run. Presentation validation and source review establish document integrity and support for proposed mechanisms, not operational acceptance.

## Presentation continuity

Keep 10 main + eight appendices unless the user changes scope. Use dense, editable diagrams with labeled arrows and capsule shapes for capabilities. Explain the proposal on the slides; speaker notes add depth. Avoid assigning work to named teammates or implying unknown interfaces are settled. Preserve proposal/inspiration/source/measurement distinctions. Reconnect and inspect the live deck before editing. The current generator and review records remain in the original workspace; portable editable PowerPoint is sufficient for design continuation.
