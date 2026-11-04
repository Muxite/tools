---
id: coder-prompts-index
status: active
source: Sources/Prompts/2026-10-21-notebook-organization-request.txt; Sources/Prompts/2026-10-22-benchmark-runner-orchestrator-request.txt; Sources/Prompts/2026-10-22-benchmark-runner-branch-and-runtime-safety.txt
last_reviewed: 2026-10-23
next_action: Choose benchmark-runner for execution tooling or spark-benchmark-setup for optional Spark deployment
---
# Coder prompts

Short handoffs to paste into a coder conversation. Copy the note body; Obsidian YAML properties are notebook metadata. Prompts identify design files by filename/title so they work on another machine.

| Prompt | Purpose | Authority |
|---|---|---|
| [[Resources/Coder Prompts/benchmark-runner\|benchmark-runner]] | Sequential control/data runner: task submission, code/observability and persistent artifact collection | Latest user handoff; implementation is allowed in our branch, runtime user files are protected |
| [[Resources/Coder Prompts/spark-benchmark-setup\|spark-benchmark-setup]] | Optional Spark deployment of ai4r plus benchmark-runner, user-selected mounts and bounded storage | Approved setup handoff; not a benchmark prerequisite or VM/factory implementation |

See [[Workstreams/M1 Design Code and Tests]] for implementation context and [[Designs/Design Library]] for canonical design links. M2 VM labs, factories, container CCs and Spark resource policy remain proposals under [[Designs/Lab Capsule and Factory Design Plan]] and [[Designs/Spark Shared Services and Storage]].

## M2 component implementation handoffs

[[Resources/Handoffs/m2-labs/README|M2 implementation handoffs]] contains the portable shared contract, baseline, validation and three handoffs:

- [[Resources/Handoffs/m2-labs/vm-labs|vm-labs]]: durable project identity, permitted VM provider, persistent state and fenced recovery.
- [[Resources/Handoffs/m2-labs/container-capsules|container-capsules]]: one stateless image carrier through the existing check/gate boundary.
- [[Resources/Handoffs/m2-labs/local-factories|local-factories]]: fixed durable lifecycle with bounded adaptive authoring and independent admission.

These do not replace the working M1 benchmark runner or require Spark infrastructure changes.
