---
id: muse-final-data-to-collect-md
status: current-design-proposal
source: November 6 accepted presentation plan and user steering; pinned sources in Evidence
last_reviewed: 2026-11-06
next_action: Use the final deck for design discussion; qualify implementation before claiming results
---

> **Post-presentation revision, November 9:** [[Post-presentation design revision]] is the current conceptual reference. Contract, CC and release image are distinct. Tool/skill CCs support agents; component CCs supply engine functionality. The lab agent now sits outside the experiment Incus instance in a separate management container. Earlier diagrams/specimens below remain historical where they disagree.

# Data collection priorities

| Stage | Data | Useful boundary |
|---|---|---|
| Intake/qualification | image/model/config/fixture/tool IDs, GPU/driver/runtime, mounts/effective grants/profile | what actually ran; known CUDA qualification differs from actual Muse checks |
| Baseline | correctness/state outcomes, protected TTFTms/tokens/s/rawSSE/errors, stage durations, lightweight host/engine records | unprofiled serving versus startup/warmup; pinned token/reference policy |
| Engine semantics | route/layer/expert IDs, actual lookup/miss/residency, execution decisions, queue/state lifetimes | routing selection differs from actual dispatch/cache outcome |
| Systems diagnostic | CUDA/API/device intervals ns, copies bytes, synchronization, NVTX/batch map | logical host scopes differ from overlapping device execution |
| Compute diagnostic | selected invocation/shape/kernel, metric units and replay/cache settings | isolated diagnostic counter result is not end-to-end score |
| Memory/storage | qualified cgroup/proc/NVML bytes, faults/OOM/swap, real I/O bytes/time, cache conditions | one physical pool; page fault≠expert miss; cached read≠SSD |
| Return | raw artifacts + loss/coverage/failure, assessment and future question | durable Factory references/manifest/receipt; lab staging only |

Capture expensive events only for a concrete unresolved question. Every promised metric identifies producer/tool, capture location, prerequisites, functional authority, units and interpretation limit in A2/A8. Thresholds/workloads come from supplied benchmark policy.
