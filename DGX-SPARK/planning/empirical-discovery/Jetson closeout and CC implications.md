---
id: inference-factory-jetson-closeout-20261110
status: handoff-and-committed-records-inspected
source: Sources/Prompts/2026-11-10-jetson-closeout-received.txt; research/jetson-campaign-closeout-20261110/source/CLOSEOUT.md
last_reviewed: 2026-11-10
next_action: Qualify a useful portable tool; consider scoped Q4_K graph-dispatch component on Jetson and target-specific transfer experiments
---
# Jetson evidence changes component and tool choices

The user supplied the Jetson ZIP through the x86 relay. [Original archive and source](../../../research/jetson-campaign-closeout-20261110/README.md) are preserved, SHA256 dc264ae20bff66451aeac581dae3412375353a6b83c6a9bb5a01e067da076435. It contains two handoff files. We also retrieved a read-only committed campaign archive via x86: remote branch and local ref both resolve to **73484492c67cbf5b38d2cd8522f7f780975907aa**, final Jetson closeout. Both ZIP documents exactly match that snapshot. This supersedes earlier Jetson-transfer-blocked notes; no Jetson authentication changes or hardware work were needed.

## New evidence

[Independent offline arithmetic](../../../research/jetson-campaign-closeout-20261110/record-audit.json) on saved J-E007 benchmark samples gives per-type graph-unfusion changes of **+19.21% BF16**, **+23.64% Q4_K-expert mixE4K**, and **−6.21% Q8_0**. Two invocations per arm; each discards the first of five in-process samples under the declared warm-up policy. mixE4K greedy files have equal full hashes and equal printed PPL/KLD summaries. Those summaries compare each arm to a BF16 reference, not a zero-KLD baseline/candidate or raw-logit proof. BF16 changes activation rounding. No RTX transfer is established, and model hashes differ across hosts.

The **moe_gateup_dispatch** component is a stronger illustrative candidate on Jetson than the small x86 Q8-reuse gain, because the positive effect and Q8 counterexample make applicability visible. Patch 03 replaces patch 01, it is not stacked with it. Patch 03 has no architecture guard despite the sm87 directory name; qualification is still Orin-local. Type names are case-sensitive, the legacy BF16 alias can remain active, and startup policy logs do not alone prove eligible nodes engaged. Single-op kernel screening failed to reproduce the full-engine fusion effect.

SPEC2 records recompute to **+63.14% rewrite / +96.81% repeat** for upstream n-gram self-speculation on copy-heavy prompts. Stored text hashes are matching 12-hex prefixes. Chat was invalid, not an established gain. This is a workload-specific upstream feature, not a new loader or our engine-code contribution.

## Manager and CC implications

- Cache hit rate, fewer IO bytes and fewer kernels are intermediate measurements. Jetson caching, random read advice and near-zero-lead-time prefetch reportedly slowed the workload despite attractive counters. Preserve actual end-to-end measures and transfer labels.
- Reuse Jetson's existing target-aware builder and ccache normalization. Our earlier amd64-only observation applies to the x86 builder snapshot; compare versions before adding arm64 support again. Native Jetson builds are minutes to tens of minutes, so live building is optional.
- A useful initial tool set now has stronger evidence for engine preflight/effective configuration, graph engagement checks and run/evidence summary, alongside the proposed profile parser. Eleven invalid-flag attempts, zero-case type screen, watchdog misclassification and process-polling deadlock justify these details.
- Requests pin context, model representation, memory domain/runtime and applicable precision. Host cgroups are not proven CUDA caps. Telemetry cannot sum shared-DRAM and nested process/cgroup scopes. Watchdog trigger, kill request, actual exit and cleanup are separate states.
- Job completion/dependency observation should use explicit identities and durable state, not pgrep patterns. A pid disappearing is not proof of accepted results.

## Evidence limits and Friday scope

The snapshot includes 2,357 regular files, but **376 lab-output files referenced by result hashes are absent**, including Jetson-local jobs. Experiment-level benchmark/quality/telemetry evidence exists; those absent raw lab files cannot be hash-verified from Git. Original “all logs committed” language is insufficient. No host-loss durability follows. We did no new GPU test, build, service change or push.

[[Designs/Inference Factory - Empirical Discovery/One useful CC demo|One useful tool OR component remains Friday's core]]. Keep the portable profile tool option; if Jetson is available, the Q4_K dispatch component is a clearer component demo. Source integration/build/Manager/mock-lab scenes are optional. [Detailed CC design changes](../../../research/jetson-campaign-closeout-20261110/cc-design-delta.md) specify patch conflicts, type policy, graph scope, testing and reuse. [Assessment](../../../research/jetson-campaign-closeout-20261110/assessment.md) separates independently checked records, reported results and unqualified transfers.
