# Continue the CC and inference-lab design

**Scope:** resume design for Muse Spark Open text inference on DGX Spark. The presentation is complete enough to discuss; the next task is to make the interfaces and failure behavior concrete. This handoff does not authorize or claim a lab implementation.

**Session closed:** [delivery checkpoint and next-session work](Session%20closeout.md). The dated PPTX is saved in Downloads.

## Read first

1. [Design continuation](Design%20continuation.md): current model, decision status, unresolved questions and next work.
2. [Executor/API rationale](async-lab-feasibility-rationale.md): why a deterministic worker is the starting recommendation.
3. [Current editable PowerPoint](CC-and-Inference-Lab.pptx), then [presenter script](presenter-script-manager.md). Detailed [speaker notes](speaker-notes-ontology-input.md) retain definitions and source explanations.
4. [Technical evidence](evidence-register.md) and [post-workshop corrections](evidence-register-post-presentation.md) before making implementation or performance claims.

The live editable presentation is [the existing Spaces deck](page://page_c8a8306864208191957b062102a675da). Read its latest saved state before editing; this folder is a dated snapshot. The PowerPoint has 10 main slides and eight hidden appendices.

## Current design in one paragraph

Input is **System ontology + plaintext\***. Intent and contract compilation guide a Builder swarm that uses tool CCs and component CCs. The contract defines the product; the image is its runnable release. One Software Factory boundary contains the compilers, Builder, CC registry, release metadata, Lab Manager and durable knowledge/telemetry. Lab control and result registration go through the Manager. Outside it, a separate management container hosts the proposed deterministic executor and protected client; disposable Incus runs the immutable engine and profiling tools. Builder receives a job ID and continues work. Optional reasoning can remain in Factory.

*At time of writing, the system ontology’s format is not known. The label does not establish a delivered template, finished schema or mandatory new CC fields.*

## Status that must not drift

- Contract, CC and image separation; two CC roles; Factory evidence placement; test-only immutable submissions; and a single Factory boundary are user/workshop directions.
- Manager API, polling deterministic worker, database-backed queue and optional resident reasoning are the latest **recommendation for discussion**, not a confirmed implementation decision.
- No Muse inference, Spark GPU/profiler qualification, crash injection, memory-limit qualification or lab API implementation ran during this presentation/design work.
- The pinned CC implementation remains the source of implementation truth. The proposed contract and release manifest are not renamed CC schemas.
- Earlier whole-engine request-CC/engine-CC examples, lab editing/rebuild proposals and mandatory in-lab reasoning-agent diagrams are superseded for this design.

## Next session

Use [Resume prompt](Resume%20prompt.md). Start with one concrete job submission, result bundle and normal/failure sequence. Do not begin another broad architecture rewrite or add orchestration services without a demonstrated need.

This is a curated design snapshot, not the full chat archive or code repository. Original recent user inputs are under `Sources`; older conversation/repository evidence remains in the notebook and pinned sources. No weights, credentials or runtime stores are included. File identities are in `manifest.json`.
