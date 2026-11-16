---
id: muse-final-resource-provisioning-md
status: current-design-proposal
source: November 6 accepted presentation plan and user steering; pinned sources in Evidence
last_reviewed: 2026-11-06
next_action: Use the final deck for design discussion; qualify implementation before claiming results
---

> **Latest feasibility recommendation, November 9:** [[Asynchronous lab manager and executor]] proposes a Factory Lab Manager API plus deterministic external executor. The earlier always-present reasoning lab agent is optional, not a starting requirement. The Manager is the Factory’s logical lab gateway. This recommendation remains a design proposal.

> **Post-presentation revision, November 9:** [[Post-presentation design revision]] is the current conceptual reference. Contract, CC and release image are distinct. Tool/skill CCs support agents; component CCs supply engine functionality. The lab agent now sits outside the experiment Incus instance in a separate management container. Earlier diagrams/specimens below remain historical where they disagree.

# Safety envelope and experiment controls

**Starting proposal:** the builder submits an immutable ARM64 OCI engine release image. A Factory lab manager coordinates with a lab agent in a separate management container outside the experiment Incus instance. The experiment instance runs the private Docker runtime and engine on DGX Spark. Builder edits/instruments/builds; lab control stages, launches, tests, observes and returns evidence. No in-lab source workbench, rebuild or binary substitution.

**Software Factory owns the durable knowledge and telemetry plane.** Every raw trace, event/counter record, correctness result, assessment, failed/partial attempt and coverage gap returns there with identities, hashed manifest and export receipt. Lab storage is protected staging. Stop owned processes on completion/timeout; retain unexported files and do not clean them until receipt. Bounded retries/retention capacity can block new admission rather than discard evidence.

TKCC-style persistent execution is a valuable evolution. It adds engine-specific loading/reset/graph-recapture/recovery work and is not an initial dependency. No actual Muse engine/factory, Spark profiling qualification or measured performance is claimed here.

| Control | Meaning | Qualification / evidence |
|---|---|---|
| CPU/process limits | eligibility/pinning differs from time quota/soft share; CPU count is not exclusive reservation | effective cpuset/quota, CPU time/throttling, bounded process rejection |
| RAM/swap | experiment-instance accounting includes private runtime/tools/candidate; management container has its own reserve; inner limits cannot add capacity | CUDA allocation-path probes, parent/child bytes, effective memory.swap.max, OOM/swap events |
| Capacity | root quota does not cover arbitrary bind mounts; custom volumes and Docker cache need supported limits | backend/mount map, bounded disposable fill, report retention |
| I/O | actual backing-device bytes/s or IOPS; cached reads bypass throttling | real-device versus warm-cache bytes/time and backend/same-disk restrictions |
| GPU | selected device/trace/counter grants; not a GPU-memory quota or guaranteed compute partition | known CUDA result, expected NVTX, Systems and Compute separately |
| Project/admission | aggregate configured instance limits plus one active scored GPU experiment | reject over-budget configuration; project CPU-count limits cannot be mixed with CPU-ID pinning |
| Engine budget | expert residency/state/cache policy, separate from safety RAM | actual route/lookup/miss/state counters under unchanged outer profile |

No selected64/112GiB profile, guaranteed swap prevention or GB10 MIG support is assumed. Actual limits follow host headroom/tool overhead and accounting qualification. Initial fixtures deliberately use small disposable limits; they establish lab capability, not Muse fit/performance.

Sources: [Incus options](https://linuxcontainers.org/incus/docs/main/reference/instance_options/), [storage](https://linuxcontainers.org/incus/docs/main/howto/storage_volumes/), [projects](https://linuxcontainers.org/incus/docs/main/reference/projects/), [cgroupv2](https://docs.kernel.org/admin-guide/cgroup-v2.html).
