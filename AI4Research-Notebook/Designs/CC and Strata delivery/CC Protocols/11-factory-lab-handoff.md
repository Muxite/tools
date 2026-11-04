---
id: cc-v2-11-factory-lab-handoff
status: v2-reference-implementation
source: November 4 CC v2 revision
last_reviewed: 2026-11-04
next_action: Qualify selected adapter and consumer evidence policy
---
# Factory to Lab · delivery checklist

The full provenance/measurement route is [04](04-provenance.md); construction is [02](02-compiler-and-release.md). Factory delivers a product and optional CCs. **Zero CCs is valid.**

| Boundary | Required fact |
|---|---|
| Product | Native manifest and immutable payload, or complete source/build material. |
| Source | Exact base/tree, dirty changes, binary/untracked files, modes, submodule/LFS material. |
| Build | Recipe/toolchain/dependencies, produced binary and observed tests. |
| Compatibility | Actual platform/ABI/backend/runtime/driver. |
| Lab preparation | Verified candidate, host eligibility, explicit selection/restart. |
| Loaded identity | Actual binary/component, effective configuration, instance generation. |
| Measurement | Pinned model/workload/cache policy, window, raw evidence and coverage. |
| Evaluation | Frozen baseline/criteria and independent verdict. |

Preserve native `engine-component.json` rather than invent a competing engine format. Component file hashes and outer archive hash cover different bytes. Loader fallback is candidate mismatch; a PID alone cannot identify the engine.

Source is not a built engine. A diff is complete only with exact base and all reconstructing material. Restart request is not loaded-generation evidence. Successful benchmark execution is not improvement. Retain failures, interruptions and missing evidence.

A qualified-host restart and measurement trial is required before claiming end-to-end Strata/Muse/GB10 validation. Local CC checks do not establish it.
