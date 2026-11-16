# Friday November 13 — show the factory's useful parts

**New evidence received:** [follow-up verification and corrections](followup-evidence/README.md) confirms up1 MUL_MAT passed and a historical live recovery rehearsal exists. Earlier unresolved statements below record the prior inspection state; do not use them as current negatives. Targeted reuse-hit/alias/graph tests and current integration readiness remain open.

**Scope refinement:** one useful tool OR component is the required demo. The sequence below is an optional expanded flow. See [concrete CC design](next-cc-design.md) for the current proposal and its verification contracts.

Recommendation: **one component, one build CC, one test/evidence flow**. Build an inference-engine image from identified source plus the accepted Granite patch stack, deliver that image and a small request to a disposable test environment, and show an inspectable result. Use a bounded interruption/retry only after rehearsal proves it fits. The other team demonstrates its lab agent; we demonstrate the image producer and deterministic request/result/evidence boundary. Keep broad optimization results as recorded context.

## 5–8 minute story and evidence

| Time | Show | What it establishes |
|---|---|---|
| 0:00–0:45 | Model/host target, accepted Q8 reuse component, one rejected candidate with evidence | The CC portfolio came from actual improvement work. Saved Granite result +2.17%, limited to that qualification scope. |
| 0:45–2:00 | Build CC invocation and its identified source, patch, bases and output | Product is the engine image, without weights or coding-agent credentials. Use a warm cached build only if rehearsal fits; otherwise show a clearly labelled prior build. |
| 2:00–3:00 | Image transport hash, platform manifest/config identity and local runnable reference; request and receiver receipt | These identifiers serve different purposes. An offline compatibility receipt is labelled offline. A real remote receipt is shown only if the other team actually provides it. |
| 3:00–4:15 | Fresh bounded real Granite inference test in the test environment; status and output | Submission is new, inputs pinned, mechanism shown engaged, execution/assessment distinct. Show one useful test CC rather than the entire catalog. |
| 4:15–6:30 | Optional owned test-container kill, retained partial evidence, confirmed stop, new attempt | Manager value: failure does not erase evidence or silently pass the test. This exercises sandbox loss only, with the controller/store alive. |
| 6:30–7:30 | Verified bundle and old-attempt hash preservation; small backlog | Explain what this taught us about build/test/component CCs and Manager responsibilities. |

## Existing assets reduce coding

- [Build CC](snapshot/campaign/cc/build_engine/README.md) already stages pinned source/patch, uses Buildx/Bake, emits runtime image/archive/build record, handles failures and separates identity fields. Use it directly. Fix stale prose before presenting; no general build service required.
- [Component contracts](snapshot/campaign/cc/components/COMPONENTS.md) and the Granite release stack already demonstrate composability. Show source-patch integration, not a generic shared-library swap: strict ABI analysis disagreed with the exact-pair swap demonstration.
- [Existing demo script](snapshot/campaign/cc/demo/demo.sh), [runbook](snapshot/campaign/cc/demo/DEMO.md), and display helper already exercise pinned submit, offline compatibility checks, interruption and separate retry with hash checks. **This script neither builds nor transfers images**, uses the older `novmm-4` image, and its recorded validation is dry-only. It is a recovery-scene starting point, not the complete proposed demo. Do not casually replace its build record: tests, image registration and proposal must agree.
- [Existing Manager adapter](snapshot/campaign/bin/lab) and [handoff tools](snapshot/campaign/cc/engine_handoff) provide the local reference flow. They are not the other team's lab agent or a qualified remote protocol.
- [Record audit](record-audit.json) and received source offer a truthful offline fallback. It may be presented as an evidence inspection, never as live execution.

## Request sketch to agree with the lab team

Start with the already implemented envelope schemas; do not build an incompatible second format. The logical contents should cover request/attempt identity, engine platform and verifiable artifact reference, actual model/input/test hashes, exact argv/env, reset/warmup policy, requirements and declared budget-guarantee class, result/evidence destination, assessment-policy revision, timeout and cancellation/cleanup expectations. Null/missing identities make it a draft, not dispatchable work. Coding environment is separate; our image is run in the lab's test environment. Provisioning choice remains theirs.

The receiver must distinguish received/accepted/rejected/needs-information and execution from acceptance. If that integration is unavailable, explicitly use the local Docker reference adapter and call it a contract demonstration. A Jetson template rejection is an offline compatibility example, not Jetson execution.

## Readiness gates before selecting the live scenes

1. Rehearse on the actual x86 host with owner-approved GPU access. Owner services are restored; do not stop them under an old approval. Check disk capacity (reported only 60 GB free), required images/model/source/base layers and build cache. No downloads or compiles during measurement.
2. Use one immutable release identity consistently across build record, image registration, tests and request. Hash the actual image archive and actual test inputs. Compilation needs no idle GPU, but consumes CPU/IO; schedule it before measurements.
3. Resolve factory's three failures if the factory is on the critical path. Plain Build CC avoids depending on the whole planner/factory. Fix record-schema/prose inconsistencies and use saved real Docker/containerd records in tests.
4. Qualify test engagement, prompt template, resource-sample availability and a bounded output length. Keep performance claims recorded; +2% is too small for an uncontrolled single live comparison.
5. Run the complete selected demo twice. Verify total elapsed time, output hashes, export manifests, interrupted coverage, owned-container cleanup and unchanged prior attempt. Fail visibly if the target finishes before injection; do not invent a crash.
6. Review ordinary display/export for private data before sharing. Hashes identify the sanitized view separately from preserved originals. No public repository link is necessary for the demo.

## Selection if timing or integration is tight

**Minimum:** build CC + image identity + one real inference/test result + retained evidence. **Optional:** interruption/new attempt. **Backup:** inspect the saved bundle and walk through the existing dry-run commands, visibly recorded. Avoid live Qwen downloads, full large-model sweeps, new hard-VRAM-cap work, profiler installation, planner retraining or a production Manager rewrite for Friday.

Nothing in this inspection qualifies the final Incus design, cross-host transport, whole-host failure survival, exclusive GPU scheduling, broad task quality or Jetson execution. Those are campaign backlog items, not workshop prerequisites.
