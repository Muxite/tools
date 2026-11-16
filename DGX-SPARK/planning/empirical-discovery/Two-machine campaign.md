---
id: inference-factory-two-machine-campaign-20261109
status: current-user-scope-and-proposed-task-allocation
source: Sources/Prompts/2026-11-09-two-machine-inference-campaign.txt; research/lab-manager-reuse-20261109/two-machine/platform-source-receipts.json
last_reviewed: 2026-11-10
next_action: Send the shared prompt to both Opus leads; inspect actual campaign and Jetson platform before execution
---

# Two complementary machines, one empirical campaign

**Jetson closeout now received:** [[Designs/Inference Factory - Empirical Discovery/Jetson closeout and CC implications|Per-type graph dispatch and portable-tool implications]]. Saved Orin results recompute to +23.64% Q4_K, +19.21% BF16 and −6.21% Q8; target qualification stays local. One useful CC remains sufficient for Friday.


**November 10 evidence update:** [[Designs/Inference Factory - Empirical Discovery/X86 closeout and Friday demo|X86 closeout inspected and preserved]]. Saved Granite Q8 reuse arithmetic supports +2.17% within its measured scope; this supersedes the earlier no-engine-win snapshot. Larger Qwen gains are upstream runtime trade-offs. Build/component/test demo proposed; live rehearsal and real lab-agent exchange remain unqualified.


The user has added a Ryzen7 3700X/RTX5070Ti/48 GB x86 host and a Jetson Orin Nano 8 GB, both Ubuntu/server-like, to the same project. Both use Opus as lead, Sonnet/Haiku subagents where suitable and Codex on tightly bounded reasoning/code tasks with compact context. This extends [[Designs/Inference Factory - Empirical Discovery/README|the current central objective]]; it does not replace discovery through real inference improvement with a portability-only or demo-only project.

## Recommended allocation

| Host | Primary work | Expected unique evidence |
|---|---|---|
| x86-main | Resume and audit current campaign, repair/qualify runner, finish matched comparisons, qualify budget mechanism, integrate promising components end to end, own build CC/shared contract/integration | Discrete CPU/GPU placement and transfers, full-engine versus layer-result attribution, repeatable image delivery and engine gains |
| jetson-arm | Native ARM/JetPack image qualification, conservative shared-memory experiments, portable telemetry/evidence/state tools, selected real inference/component candidates, remote job/recovery validation | Applicability/ISA/ABI differences, truthful missing metrics, resource-limited component value, portable methods and Manager requirements |

Jetson must do real engine/component work where feasible, not just act as a client. It should not repeat every x86 sweep. Both own their local baseline/candidate comparisons; don't pool cross-host token rates or transfer speedups without testing. x86 initially owns shared integration and external durable control/evidence outside disposable test sandboxes; this is not automatic whole-host failover.

## Reported x86 state to preserve

The user relayed `campaign/START-HERE.md` as entrypoint in `~/projects/siminfeng`. Strata concepts and a hard GPU-memory restriction are unfinished. A budget-shim task was still writing at commit, uncompiled/untested. The matched static-offload sweep failed on runner UTF-8 handling and was not rerun after its reported fix. No full-engine win is established; memory results are quantization/offload trade-offs and hybrid dispatch is single-layer evidence only.

`euaaa-llm-gpu-1` and Sunshine were reportedly stopped with owner approval; restoration commands are in START-HERE and `decisions/D002-gpu-freed.md`. These are user-relayed snapshot facts, not remote state independently observed here. A suggested push is not proof the remote is current or authorization to push main/change permissions. Resume existing work and inspect current commit/worktree/agents before relying on artifacts.

## Platform considerations to qualify

NVIDIA lists RTX5070Ti at compute capability 12.0 and Orin Nano at 8.7. Tegra CPU/GPU allocations share physical DRAM with different allocation/cache behavior; 8 GB is not separate CPU and GPU pools. Orin needs native Jetson-compatible arm64 output and installed JetPack/L4T/toolchain/runtime inspection. Native image qualification and model checks remain unrun here.

Use actual Jetson-supported sensors such as tegrastats where available, with unavailable fields explicit. NVML/nvidia-smi-only telemetry is not a portable assumption. Record power/clocks/thermal state; do not silently reflash, upgrade or force clock/power modes. Host RAM cgroups, engine cache budget, cooperative allocator restriction and a proven GPU-memory cap are distinct guarantees. A partial shim is not a hard limit.

Primary source references and collected snapshots are in [platform notes](../../../research/lab-manager-reuse-20261109/two-machine/PLATFORM-NOTES.md). No Jetson, GPU, network or crash qualification ran on the research workstation.

## Handoff

Send [the complete shared two-machine prompt](../../../research/lab-manager-reuse-20261109/two-machine/ORCHESTRATOR-PROMPT.md) to both Opus leads. It contains the mission, reported snapshot, per-host tasks, agent task contracts, shared coordination/evidence rules, useful source/research links and an illustrative job envelope. It has no dependency on the full research bundle. Each lead identifies its target lane; the x86 lead integrates shared code/contracts and the Jetson lead owns its adaptation/evidence contributions.
