---
id: muse-cc-schema-communication
status: implementation-aligned-module-design
source: November 5 user direction; CC v2 owner; evidence/source-receipts.json
last_reviewed: 2026-11-05
next_action: Use the implemented schema; develop inference-specific material semantics with the ontology contributor
---

> **Post-presentation revision, November 9:** [[Post-presentation design revision]] is the current conceptual reference. Contract, CC and release image are distinct. Tool/skill CCs support agents; component CCs supply engine functionality. The lab agent now sits outside the experiment Incus instance in a separate management container. Earlier diagrams/specimens below remain historical where they disagree.

> Retained detailed context. Current November6 direction is [[Alignment and decisions]]: immutable submitted images, test-only lab, and Factory-owned knowledge/telemetry. Earlier local-workbench/native-first options are superseded, not implementation evidence.

**Current presentation revision (November 5):** [[Design rationale]] and [[Inference layers and profiling]] record the compatible Builder, optional ontology, scoped lab build/debug loop, nested Docker/Incus capture and current terminology. [[Build challenges]] and [[Data to collect]] distinguish proposed integrations from qualified evidence. The retained detail below predates that presentation revision where its scope differs.

# CC schema, engine products and lab communication

## The working model, in one paragraph

One coding-agent factory can build native inference engines, package those engines as implemented CCs, and implement supporting CCs. A request CC describes wanted behavior and may include the desired inference-system ontology. Existing implemented CCs supply tools the coding and lab agents use. RSI proposes improvements to the same code/tool-building loop. This is a working architecture assumption for discussing our modules, not an adopted whole-system architecture or a need for a separate CC implementation factory.

The primary objective remains lower Muse peak unified physical memory on DGX Spark under the existing standardized benchmark and acceptable TTFT/token rate. The benchmark is externally supplied; we neither choose nor design it here.

## Full spectrum of CCs in this workflow

| CC family | Example operations / contents | Primary consumer | Carrier and lifetime |
|---|---|---|---|
| Ontology-bearing request | Required engine behavior/ports, system description, reference sources/images, open implementation choices | Coding agent / builder | Non-callable request plus pinned material; lives through construction and provenance |
| Implemented engine | `describe`, `start`, `endpoint`, `infer` where finite, `stop`; identified native engine and optional OCI image | Worker, lab agent, dyno | Native or ARM64 image; long-lived serving process managed by worker |
| Source/model/pack preparation | Metadata inspection, tensor/format checks, conversion, pack identification | Coding agent | Native Python/C++ tools or build image; finite calls |
| Build and qualification | Build native code, inspect ABI/backend, package engine, verify component identity | Coding agent and worker | Existing native build chain or pinned build image; finite calls |
| Configuration and tuning | Expose supported knobs, generate profiles, edit supported settings, propose candidate patches | Coding agent / lab agent | Native tools, scripts and supporting knowledge; edits produce identified candidates |
| Sensors and profiling | Host samples, engine diagnostics, GPU-event traces, versioned trace decoders | Lab agent for diagnosis; protected collector for evidence | Host-native collectors, engine hooks, optional profiler container; bounded collection session |
| Dyno and benchmark adapter | Fixed inference load, memory-budget sweeps, standardized benchmark invocation | Lab agent and protected evaluation runner | Native HTTP client / owner harness; finite run with durable output |
| Numerical/state correctness | Compare tokenization, tensors/logits, continuation, reset/cancel/restore | Coding agent for feedback; evaluator for acceptance | Native comparison runner, optional NumPy; finite calls |
| Lab support | Request allocation/status, stage, start/stop/restart, export observations, release | Lab agent through granted worker capabilities | Worker-backed calls; underlying lab policy owns the actual effects |
| Knowledge/integration adapters | Versioned tuning guidance, code references, skill instructions, MCP/app adapters | Coding/lab agent | Bundled materials and callable adapters as appropriate; not necessarily a container |

These are capability families, not ten mandatory services or a proposed registry redesign. Group implementations by shared dependencies and responsibility. Some capabilities are prebuilt; missing ones can themselves be requested from the same coding-agent factory. Materials can be passive content inside a CC; ordinary files do not need artificial executable wrappers.

## Current declaration support — corrected to the implemented branch

The current code is [ai4r_ccv2](../../../AI4Research-Development/ccv2-work/docs/architecture/ccv2/README.md), pinned for this handoff at `a838b97048b2c561212ccfa82b5d414c39359dc9`. Its schema/reference source is [the focused CC Protocols draft](../../../research/tools-transfer-20261104/AI4Research-Notebook/Designs/CC%20Protocols/README.md), imported from tools revision `89893083ebbcb3b54f5672df720e3afc37a8df7e`. The older notebook `CC and Strata delivery/CC Protocols` implementation and our earlier optional `system` proposal are historical inputs.

| Existing field / mechanism | What it supports |
|---|---|
| `capabilities` | One map for finite actions and served interfaces; a passive-only package may omit it |
| `bindings` | Native commands, pinned images or registered `delegate` implementations |
| `takes`, `gives`, `needs`, `changes`, `guarantees` | Inputs/results/provisions/effect ceiling/optional checks; `gives` belongs to finite actions, not served interfaces |
| `serves.interfaces` / `serves.ready` | Native API protocol/port/path/optional contract and readiness configuration |
| `materials.NAME.path` | Bundled immutable instruction/reference/ontology bytes, with optional description/media type |
| `provenance` | Optional bundled build/evidence record; package identity and actual runtime facts remain distinct |
| `cc-request/2` | `format`, `id`, partial `desired` declaration and absent-field `open` pointers; no mandatory root `kind` |

**Ontology support already exists through `desired.materials`.** Declare the desired inference service itself under `desired.capabilities`, and place the desired engine-structure document, vocabulary/profile and source/image records in `desired.materials`. The assigned ontology owner defines their contents. The coding agent reads those materials to implement the desired service; CC does not automatically become an ontology reasoner or engine compiler.

The former proposed root `system`, root request `materials`, and `materials.{role,artifact}` descriptors are not the current schema. Do not use them. Current material entries are relative package paths with optional metadata; preparation/release indexing captures their bytes. External image/model/source identities can be recorded inside those material files rather than invented as new core fields.

## Request CC and implemented engine CC describe the same subject

The request declares an engine capability such as `api` with `serves`, its native API contract and the required construction materials. Its unresolved binding is an explicit open choice. The coding agent supplies real files and a binding, preserves fixed requirements and prepares an implemented engine CC. This is not a builder-tool declaration whose `gives` port returns an engine.

The implemented engine can carry its realized system description as a material and link the original request in build provenance. The desired description states requirements; the realized description records build claims; runtime observations belong to the actual instance/attempt evidence. Ontology material does not grant privileges or prove conformance. Our [worked request](examples/engine-request.json) uses this current schema; its [ontology illustration](examples/engine-system.desired.json) is not an approved Muse architecture or executable engine.

A retained coding-agent demo built and ran a native synthetic service from a request with a stand-in ontology material. That demonstrates agent-mediated construction and material transport, not correct implementation of Muse or a general formal ontology compiler. [Implementation status](Implementation%20status.md) records the evidence and an outstanding request-fixture issue.

## Implemented runner and communication surface

JiuwenSwarm now exposes eight tools through one `agent_mcp` server: `cc_list`, `cc_describe`, `cc_material`, `cc_call`, `cc_start`, `cc_instance`, `cc_stop` and `cc_artifact`. They wrap the local CC Host. Native/image actions use the finite process protocol; served capabilities use instance lifecycle and their own native API.

`cc_start` returns an instance and, when running, a host-resolved environment handle for client CCs. `cc_instance` inspects identity/state; `cc_stop` confirms cessation of an instance owned by that session. A finite `cc_call` returns a receipt whose state must be inspected; a delivered MCP tool result is not automatically success. Stable keys support deduplication only while the bound inputs/resources still match; stopping a service can invalidate a later handle-bound replay.

An implemented image-service demonstration used a real built-image ID, native client CC and confirmed stop. Persistent service startup is therefore not a missing feature of the current runner. Remote multi-host control, Incus integration, GB10 allocation and independent inference measurements remain separate lab work. Do not confuse the implemented local application manager with a deployed distributed lab manager.

The dyno accesses the service's returned HTTP endpoint directly. Generated tokens are not individual CC calls. `serves.interfaces.contract` references a native API description; do not duplicate every API method in the CC capability map. Image packaging and service lifetime are independent: native services and finite image actions are also supported patterns.

## Exactly who communicates with whom

| Sender → recipient | Payload / transport | Reply and use |
|---|---|---|
| Request author or coding agent → builder | Request CC with desired interface, system profile/document, materials and allowed choices; staged artifacts | Candidate native product, implemented engine CC, optional supporting CCs and build lineage |
| Coding agent → CC host | Selected release/capability and plain arguments through existing host API or configured adapter | Host receipt plus identified reports/artifacts; local coding sessions stay native |
| Coordinator → worker | Existing lab proposal: authenticated TLS, persisted command identity, lease/attempt/generation and scoped resources | Observed status and results; retry reconciles existing effects instead of blindly starting another engine |
| Lab agent → worker-backed CCs | Granted lease/generation handles; stage/start/configure/observe/stop requests | Endpoint and evidence handles. The agent cannot invent a device handle or increase limits |
| Dyno → engine | Private HTTP streaming API on resolved endpoint; fixed request body and sampling/config | Raw SSE events, usage and finish reason; protected client stamps arrival times |
| Host collector → evidence store | Append-only raw samples and final manifest via granted output path/artifact upload | Hash-identified observations outside candidate-writable space |
| Engine → diagnostic adapter | Opt-in telemetry snapshots, stderr trace files or native event dumps | Versioned raw diagnostic artifacts; availability and coverage are explicit |
| Evaluator → coding agent / RSI | Benchmark result, memory/speed comparison, contamination/failures and missing evidence | Next candidate or reusable tool/recipe proposal; adoption is separately reviewed |

CCs provide the shared declaration, request, handle and result vocabulary. HTTP/SSE, worker TLS and immutable artifacts carry the actual traffic. This is how CCs support communication; they are not a replacement network stack or a telemetry database.

## End-to-end example without a new factory

A request asks for a Muse engine for Spark and includes the desired system description and reference Strata/DwarfStar sources. The coding agent inspects the model and sources, uses existing build/inspection CCs and native coding tools, and outputs an engine CC plus any useful new trace/pack-preparation CCs. The worker launches the engine; the lab agent selects observation and trial tools; protected sensors/client capture a memory/performance run. The standardized benchmark runner evaluates the pinned workload. Evidence returns to the same coding agent/RSI lane. It can revise the engine, the reusable tools or build recipe, then produce another candidate. No second implementation factory is necessary under this working model.

See [tool contracts](Tools.md), [lab internals and telemetry](Lab%20internals%20and%20telemetry.md) and [the candidate ontology](Ontology%20and%20request%20CCs.md) for the deep dive.
