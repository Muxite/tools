---
id: muse-final-evidence-md
status: current-design-proposal
source: November 6 accepted presentation plan and user steering; pinned sources in Evidence
last_reviewed: 2026-11-06
next_action: Use the final deck for design discussion; qualify implementation before claiming results
---

> **Post-presentation revision, November 9:** [[Post-presentation design revision]] is the current conceptual reference. Contract, CC and release image are distinct. Tool/skill CCs support agents; component CCs supply engine functionality. The lab agent now sits outside the experiment Incus instance in a separate management container. Earlier diagrams/specimens below remain historical where they disagree.

# Sources and evidence boundaries

# Evidence register

Reviewed 2026-11-06. The saved Spaces deck is the editable presentation. This package retains its generator, rendered slides, notes, sources and review history.

| Source | Claim boundary |
|---|---|
| [CC implementation](https://github.com/Stellven/jiuwenswarm/tree/a838b97048b2c561212ccfa82b5d414c39359dc9) | Implemented material/native/image/service foundation; no inference qualification |
| [Muse operator source](https://github.com/huggingface/transformers/blob/fd3cf0140de03f7619ac95b5cfed05b711ff9e22/src/transformers/models/muse_spark/modeling_muse_spark.py) | Structural reference; not optimized Spark runtime |
| [Muse config defaults](https://github.com/huggingface/transformers/blob/fd3cf0140de03f7619ac95b5cfed05b711ff9e22/src/transformers/models/muse_spark/configuration_muse_spark.py) | Reference defaults, pending selected-checkpoint config |
| [Strata](https://github.com/Niko1221/Strata/tree/ffa80d73133ea5c548aefe57889a16e8085a938f) | Inspected mechanisms; no transferred result |
| [DwarfStar](https://github.com/antirez/ds4/tree/b3f50180ec2c7324892be1f50bc83555ccb8d5e7) | Inspected mechanisms; no transferred result |
| [Together](https://www.together.ai/blog/together-compiler-continual-compilation-for-ai-inference) | Experiment methodology; no assumed source dependency |
| [Incus](https://linuxcontainers.org/incus/docs/main/reference/devices_gpu/) | GPU exposure; target environment qualification required |
| [Incus NVIDIA config](https://linuxcontainers.org/incus/docs/main/reference/instance_options/#nvidia-and-cuda-configuration) | Host libraries and runtime config |
| [Nsight Systems](https://docs.nvidia.com/nsight-systems/UserGuide/index.html) | CUDA/NVTX timeline and container capture |
| [Nsight Compute](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html) | Selected kernel analysis and replay caveat |
| [GPU counter access](https://developer.nvidia.com/ERR_NVGPUCTRPERM) | Separate driver permission gate |
| [Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html) | Accounting and event semantics |


# Final source and evidence additions

Checked 2026-11-06. Primary documentation supports mechanisms; no target execution or profiling occurred during these checks. Earlier native-workbench edits are superseded by immutable-submission/test-only direction.

| Source | What it supports | Boundary for the deck |
|---|---|---|
| https://www.together.ai/together-compiler-paper | Tiered persistent engines; dynamic implementation reload; realistic-data motivation; startup/throughput findings | TKCC findings are vendor-reported research on stated models/hardware, not Muse/Spark measurements. Page 4 separates random MoE 13–38% expert activation from sparse-attention top-k 1.3× slowdown. |
| https://www.together.ai/blog/together-compiler-continual-compilation-for-ai-inference | Accessible method overview and source paper link | Headline experiment throughput is not inference speed. Paper is preferred for exact causal/numeric claims. |
| https://docs.nvidia.com/nsight-systems/UserGuide/index.html | CUDA/NVTX capture, mounted profiler in workload, stats/SQLite analysis, bounded/range collection and process kill behavior | Summary/detail can analyze one report. Trace collection changes observation conditions; set lifecycle intentionally. Full compatible tool tree must be available inside workload. |
| https://docs.nvidia.com/nsight-systems/InstallationGuide/ | ARM SBSA target/platform requirements, CPU sampling/perf policy and environment checks | Pin installed release; do not assume historic minimum versions apply to current package. CPU sampling availability differs from CUDA trace success. |
| https://docs.nvidia.com/nsight-compute/ProfilingGuide/ | Metric sets, collection overhead, replay/serialization and determinism requirements | Basic static facts need not replay; requested metrics may. Isolated kernel counters do not prove full serving gain. |
| https://docs.nvidia.com/nsight-compute/NsightComputeCli/index.html | Kernel/invocation/section filters and bounded export | Select observed supported kernel/metrics, not an unqualified universal counter list. |
| https://nvidia.github.io/NVTX/ | Header-only annotation API, normally inactive without attached tooling, domain/context use | Host annotations are context, not GPU completion timers or quality evidence. |
| https://nvidia.github.io/NVTX/doxygen/group___m_a_r_k_e_r_s___a_n_d___r_a_n_g_e_s.html | Same-thread nested push/pop and handle-based process ranges | Thread/callback/batch semantics must match actual source placement. |
| https://developer.nvidia.com/ERR_NVGPUCTRPERM | Separate GPU counter/hardware-event permission | No inference from CUDA visibility to permitted counter collection. |
| https://linuxcontainers.org/incus/docs/main/faq/#how-can-i-run-docker-inside-an-incus-container | Docker nesting with `security.nesting=true`; host supplies kernel modules | Nested GPU/Nsight on assigned Spark remains unqualified. |
| https://linuxcontainers.org/incus/docs/main/howto/instances_create/ | Direct Incus OCI application launch is supported | Valid alternative to default private-Docker-inside-existing-lab; different peer-instance/provider integration. |
| https://linuxcontainers.org/incus/docs/main/reference/instance_options/ | NVIDIA runtime-library exposure; CPU pinning and allowance; memory-related instance controls | CPU percent allowance is soft/weight, time allowance is hard quota. Declare effective config and actual hierarchy. |
| https://linuxcontainers.org/incus/docs/main/reference/devices_disk/ | Root capacity setting and disk read/write byte/s/IOPS controls | Root size does not give bind mounts a quota. Verify storage driver/backing device/volume behavior. |
| https://linuxcontainers.org/incus/docs/main/reference/devices_gpu/ | Selected device exposure, distinct GPU-device types | Access is not VRAM quota/SM fraction or established GB10 MIG support. |
| https://docs.nvidia.com/datacenter/tesla/mig-user-guide/supported-gpus.html | MIG requires supported hardware/configuration | Do not infer MIG from Incus offering a generic MIG device type. |
| https://docs.docker.com/reference/cli/docker/container/run/ | Read-only root and separately writable mounts, runtime/entrypoint launch | Image digest alone is not read-only enforcement. Do not expose Docker socket to candidate. |
| https://docs.docker.com/engine/storage/bind-mounts/ | Bind-mount path/permission semantics | Source path is relative to daemon environment; nested namespace/UID mapping must qualify. |
| https://docs.docker.com/engine/containers/resource_constraints/ | CPU/memory and combined memory-plus-swap semantics | Translate UI/request resource policy explicitly into cgroup-v2 limits; inspect actual values. |
| https://docs.kernel.org/admin-guide/cgroup-v2.html | Hierarchical resources; memory/swap state; I/O per-device BPS/IOPS | Parent includes children; no child escape above parent. `memory.high` is not hard cap; `memory.swap.max` is swap-only. Cached I/O and GPU accounting require separate coverage. |

## Implementation evidence to keep precise

Pinned CC source remains `a838b97048b2c561212ccfa82b5d414c39359dc9`:

- `jiuwenswarm/ccv2/ccv2.py:713` already launches finite image calls through Docker with read-only root and dropped capabilities; `:721` requires qualified provider for implicit process/device attachment. This supports choosing the existing image convention; it does not demonstrate GPU execution.
- `ccv2.py:736–743` retains native-timeout uncertainty and requires one JSON stdout result. Nsight/native wrappers must capture tool logs independently and return declared artifacts/partial outcomes.
- `applications.py:235` image service path similarly uses Docker/read-only root. `:318` checks process birth identity before stop; `:336` can report `STOP_UNCONFIRMED`.
- Current runner has no completed remote Spark/Incus GPU provider; this remains proposed work.

Source links: https://github.com/Stellven/jiuwenswarm/blob/a838b97048b2c561212ccfa82b5d414c39359dc9/jiuwenswarm/ccv2/ccv2.py ; https://github.com/Stellven/jiuwenswarm/blob/a838b97048b2c561212ccfa82b5d414c39359dc9/jiuwenswarm/ccv2/applications.py .

## Honest status language

Initial known-CUDA-fixture success qualifies the lab path only. It does not establish Muse support, correctness, fit, speed or a functioning software factory. E1–E4 are bounded proposed investigations after their prerequisites exist; their one-hour/day limits are stop budgets, not delivery estimates. Unsupported, incomplete, negative and recovery outcomes remain useful evidence.


## Final scope

10 main +8 appendix. Knowledge/telemetry belongs to Software Factory; lab output is staging. Existing CC foundations differ from proposed GPU/Incus/Factory integration. No Muse inference or hardware qualification ran here.
