---
id: muse-inference-ontology-request
status: current-material-mechanism-candidate-domain-description
source: November 5 implementation inspection; focused CC FORMAT; preserved ontology discussion
last_reviewed: 2026-11-05
next_action: Coordinate the actual inference ontology with its assigned contributor; use desired.materials
---

> **Post-presentation revision, November 9:** [[Post-presentation design revision]] is the current conceptual reference. Contract, CC and release image are distinct. Tool/skill CCs support agents; component CCs supply engine functionality. The lab agent now sits outside the experiment Incus instance in a separate management container. Earlier diagrams/specimens below remain historical where they disagree.

> Retained detailed context. Current November6 direction is [[Alignment and decisions]]: immutable submitted images, test-only lab, and Factory-owned knowledge/telemetry. Earlier local-workbench/native-first options are superseded, not implementation evidence.

**Current presentation revision (November 5):** [[Design rationale]] and [[Inference layers and profiling]] record the compatible Builder, optional ontology, scoped lab build/debug loop, nested Docker/Incus capture and current terminology. [[Build challenges]] and [[Data to collect]] distinguish proposed integrations from qualified evidence. The retained detail below predates that presentation revision where its scope differs.

# How a CC declaration supports the inference-system ontology now

**The ontology describes the inference engine itself. The request CC declares that desired engine and carries the ontology as construction material.** It is not a declaration for a builder tool whose result happens to be an engine. The coding agent is the external builder that implements the request.

## Supported representation

The current focused CC v2 draft and `ai4r_ccv2` schema use `desired.materials` for externally defined construction material. A request has `format: cc-request/2`, its request `id`, a partial `desired` completed declaration, and `open` pointers naming absent implementation choices. There is no root `system` field or required `kind` field in this current request format.

Inside `desired`:

- `capabilities.api.serves` declares the engine's offered native interface, readiness and API contract.
- `materials.ontology.path` names the bundled desired structure document.
- Other materials can carry the assigned vocabulary/schema, pinned source/image records, diagrams, instructions and evaluation references.
- `bindings` and explicit absent-field `open` choices identify what implementation still must be supplied.

The [worked request](examples/engine-request.json) and [material document](examples/engine-system.desired.json) illustrate that arrangement. The [current format](../../../research/tools-transfer-20261104/AI4Research-Notebook/Designs/CC%20Protocols/FORMAT.md#externally-defined-construction-material) and [implementation](../../../AI4Research-Development/ccv2-work/jiuwenswarm/ccv2/ccv2.py) own actual syntax. Our former root `system`/root request `materials` sketches are preserved in history and are superseded.

## What the external ontology could contain

The ontology has an assigned contributor. These are candidate information needs for the Muse/Spark tools and lab, not an attempt to finalize their vocabulary or infer an unknown model graph.

| Content | Why the builder/tools need it |
|---|---|
| Checkpoint, tokenizer/template, precision, modalities and model operators/layout | Establish actual execution semantics and compatibility |
| Components and typed relations | Relate loader, weight access, executor, scheduler, API and diagnostic roles |
| State ownership and transitions | Identify KV/recurrent/session/cache state, reset, commit, rewind and recovery rules where applicable |
| Memory paths and representation choices | Expose weight/state/workspace lifetimes, mapping/copies, cache residency and storage streaming |
| Supported controls and observability | Tell agents which settings, traces and sensors exist for this implementation |
| Target/dependency requirements | Bind platform, backend, native artifacts, images, source/build material and compatibility |
| Required behavior versus permitted tuning | Keep model/workload/quality obligations distinct from choices such as representation, cache policy and scheduling |

The seven roles in our JSON illustration are conceptual reference roles, not a verified Muse layer graph. Do not import Qwen recurrent-state details or DeepSeek lookup tables into Muse by analogy. Approved model facts remain to be inspected.

## Desired, realized and measured

| Object | Meaning and custody |
|---|---|
| Desired ontology material | Required structure/constraints and open questions supplied in the request |
| Callable CC declaration | The engine's finite operations or served interface; separate from its internal structural vocabulary |
| Realized description material | What the builder claims it implemented, linked to native manifest/source/image/build identity |
| Attempt/instance evidence | What actually loaded and happened under a particular allocation/configuration/workload |
| Independent assessment | Whether identified outputs/observations meet the evaluation policy |

Classify requirements, tunable choices, build-derived claims and runtime observations separately. A material hash identifies bytes; it does not prove their statements. The engine package can include a realized description and source-request link. Measured memory, residency and latency remain instance-specific evidence. Preserve Strata's native `engine-component.json` as the domain package authority when using Strata.

## Current implementation evidence and its boundary

The coding branch contains a real JiuwenSwarm/Codex request-to-native-service demonstration, with the request's stand-in ontology copied into the built package. It also contains native tools, passive material and a Docker service/client demonstration. Those facts support transport, construction and lifecycle feasibility. They do not establish a real Muse ontology, automated semantic ontology compilation, GPU execution or memory savings. [Implementation status](Implementation%20status.md) separates source/evidence inspection from tests not rerun here.

One retained request fixture asks questions through open pointers that also name already-fixed fields. The current generic resolver rejects that fixture with `FIXED_FIELD_CHANGE`; the live agent constructed the service separately. Track that fixture issue rather than describing the demo as a successful generic-resolver completion of every request field. Our workshop illustration uses only an absent binding pointer.

## Adversarial constraints carried forward

- Ontology or image/reference material cannot expand host grants or authorize publication.
- Mutable repositories/images require pinned identities and reconstruction evidence.
- Contradictory typed requirements/drawings become explicit unresolved requirements.
- A metadata graph attached to the wrong binary is not conformance; check actual loaded identity.
- Precision, expert-count, context or sampling changes are labeled and evaluated rather than silently treated as unchanged computation.
- A desired 40 GB bound is not an observed or enforced physical-memory limit.
- Builders do not own benchmark policy or certify their own candidate through metadata alone.
- No separate tool invocation per internal layer or generated token is required.

The earlier Luna findings remain useful for these boundaries. Its suggestion to freeze the old schema or choose a first prototype is not current direction. Prototype/project planning is deferred; the presentation focuses on our CC and lab modules with only brief architecture context.
