---
id: muse-spark-procedures-cc-handbook-20261110
status: current-research-and-preliminary-portfolio
source: Sources/Prompts/2026-11-10-muse-handbook-focus.txt; Sources/Prompts/2026-11-10-muse-handbook-implementation.txt; Sources/Prompts/2026-11-10-handbook-illustrated-implementation.txt; Sources/Prompts/2026-11-10-handbook-campaign-feedback.txt
last_reviewed: 2026-11-10
next_action: Select the saved-profile CC for a bounded implementation; establish Muse checkpoint/reference and Spark provider prerequisites independently
---
# Muse Spark procedures and CC handbook

**Session closed:** [[Resources/Handoffs/muse-handbook-major-20261110/Resume tomorrow|Start here after clearing memory]]. The major handbook is preserved; next task is choosing and preparing the November 11 deliverable.

**Major reference saved:** [[Resources/Handoffs/muse-handbook-major-20261110/Start here|Muse Spark Inference Factory Handbook — November 10 milestone]].



**Primary target:** Muse Spark Open on one DGX Spark with 128 GB unified memory. Lower peak physical memory under the externally owned quality benchmark and acceptable TTFT/token rate. The exact accepted benchmark policy and selected checkpoint remain prerequisites; this work does not fabricate either.

[Portable single-file handbook](../../../research/muse-spark-handbook-20261110/HANDBOOK.md) · [Sendable output copy](../../../outputs/Muse-Spark-CC-Handbook-20261110.md) · [Review and validation records](../../../research/muse-spark-handbook-20261110/README.md)

## What changed

**Illustrated revision:** executive summary first, six rendered Mermaid diagrams with text fallbacks, plain-English named capability cards, node toolkit assignments, three worked examples and an owner/output/acceptance backlog. Multiple CCs may be assigned to one task node without merging their releases or granting every agent every permission. Earlier technical IDs are retained in the appendix cross-reference.

Configuration Planner and Campaign Notebook are separate preliminary CC proposals. Planner proposes supported experiments but does not admit jobs or judge results. Notebook records evidence and handoffs but does not inherit arbitrary command execution from the historical operation wrapper.

The latest user direction narrows the broad constrained-inference handbook to Muse/Spark. It supersedes treating Muse as only presentation background to Granite. RTX and Jetson campaigns remain supporting evidence, unchanged. One useful tool or component still satisfies Friday; the factory handbook is the longer-term objective.

## Decisions and findings

- Lead with procedures: inspect, hypothesize, construct, cheap-check, submit, execute, assess and retain/reject. Each of 11 procedures names needed tools/components and experimental evidence.
- Preliminary catalog: 12 tool candidates, four component families, Field Guide methodology and a conditional Specialist agent role. These are reference boundaries, not full declarations or a mandate to implement every package.
- Prioritize model compatibility/reference, weight representation/residency/SSD access and whole-pool memory measurement. Quantization label, active-parameter count or an enabled cache flag does not establish fit.
- Separate privileged capture from read-only report analysis. Reuse existing builders and supported format readers; qualify Spark recipes. Current CC materialization is not an engine image builder, and its MCP call has no timeout argument for long builds.
- The installed Muse modeling file differs from the pinned reference. Preserve exact source identity; config defaults and public model-card properties do not replace selected-checkpoint inspection.
- Keep independent coding and test environments, immutable engine products, other-team provider ownership and deterministic Manager coordination. Recovery distinguishes engine, test environment, coordinator and host failure; local retention does not prove host-loss durability.
- Recommend bounded long-form NCU CSV analysis as the first demo CC, after parser hardening and one real agent/CC invocation. Recorded RTX fixtures must be labelled as such. No new GPU work or implementation changes occurred here.

## Evidence and review

Three GPT-6.1 Sol reviewers inspected mechanisms, construction/CC protocol and lab behavior, then cross-reviewed one another. The lead incorporated cache accounting, Muse operator boundaries, state equivalence, call-deadline limits, continuous measurement eligibility and stale-attempt fencing. Source checks, hashes and documentation validation are retained in the linked package.

See [[Designs/Muse Spark - CC and Lab Workshop/README]], [[Designs/Inference Factory - Empirical Discovery/Follow-up evidence]] and [[Designs/Inference Factory - Empirical Discovery/Jetson closeout and CC implications]]. Do not transfer their speedups, missing-evidence assumptions or hardware compatibility to Spark.

The supplied campaign-agent feedback is preserved byte-for-byte; visibly damaged tables were not reconstructed as measurements. Two GPT-6.1 Sol follow-up reviews checked package boundaries and the recovery example. Prior handbook bytes and edited-note bytes are retained in the illustrated revision review batch.
