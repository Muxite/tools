# 20261113 Spark Research Handoff postpresentation

## Current outcome

The local-agent / SSH-tools workflow is running and has completed real Spark builds and bounded inference tests. Account authentication remains on the Windows machine. No independent remote coding agent was started. No new presentation was made.

The user reported that the November 13 video-led demo communicated the work clearly, told a good story, achieved worthwhile results and was received as a software-factory proof of concept. The next work is deeper research, expanded CCs and stronger hardware. The notebook now reflects that direction rather than video preparation.

## Measured results

| Check | Observed outcome |
|---|---|
| Source transfer | Factory `fe88a20682550603a5d32193403c74cc6e68e8b7`; archive hash verified and 7,605 regular files matched |
| SSH recovery | A bounded probe finished after its SSH connection closed; identical resubmission recovered the same job |
| Cancellation and timeout | Owned process probes passed; container probes exposed a v1 cleanup bug, then both passed with runner v2 |
| Cold build | Compilation/linking 233.43 s; whole first attempt 241.84 s, ending in a failed CUDA-library launch check |
| Corrected unchanged rebuild | 2.60 s overall; driver-access launch correction passed |
| Small source edit | 9.26 s overall, 5.48 s compilation/linking; new diagnostic marker executed |
| Tiny GPU correctness screen | Baseline and edited image returned byte-identical 16-token output |
| Ordinary GPT-OSS loading | 16 GiB succeeded; 8 GiB was OOM-killed during loading |
| Shared-file mmap/no-repack | 8 GiB succeeded, but about 391 MB charged memory and no reads during output exposed a shared-cache confound |
| Owned-file 8 GiB tests | Both completed, hit an 8 GiB charged-memory peak, used no swap, and recorded 3.17 / 3.40 GB of block reads after output began |
| Owned-file 16 GiB control | Same complete 64-token output as both capped runs; no additional sampled reads after output began |

The device records map to the local NVMe. I/O timestamps are sampled, not per-token attribution. The owned model file is 12,109,566,624 bytes with SHA-256 `27cd6c432c7672cb812a92f611cf3ba7bbc35928262bb1e1253ff4ee6ae35901`.

## Accepted within a bounded scope

Retain compatible build objects and separate runtime-setting changes from compilation. Use explicit mmap/no-repack and owned-file cache control as a method for CPU memory-budget experiments. Preserve the failed cold launch, OOM and shared-cache tests: they explain why these controls are necessary.

Two material CC candidates package those methods, version 0.1.1, declaration-validated but not promoted to the central catalog. Their documentation states applicability and limitations. This is a completed locally directed qualification cycle; it does not establish an autonomous remote agent or a new inference-speed win.

## Next research, in order

1. Use the v3 admission wrapper and pinned request examples for subsequent experiments; preserve its current ownership/recovery behavior.
2. Compare supported Strata and llama.cpp configurations for the same model/workload and quality requirements. Qualify other engines only where they support the needed model and SSD-backed execution.
3. Qualify GPU/unified-memory allocation accounting and useful placement strategies. The current constrained-model experiment used CPU execution; only the tiny smoke used full GPU offload.
4. Expand the prompt set and contexts, retain held-out checks and repeats, then evaluate a mechanism change through the CC workflow.
5. Validate promising changes on a genuinely larger-than-physical-memory model before making a scaling claim. Existing large artifacts need completeness/provenance review first.

Do not promise a speedup, reuse Jetson tuning unchanged or begin a presentation project. November 20 remains a progress checkpoint.

## Retention

Original shared projects, models, sessions and the existing worker were preserved. The owned workspace contains source snapshots, private environment, compatible build objects, images, request records, logs, the factory evidence store and the justified private model copy. Failed drafts are retained under versioned names. The operating guide identifies the current versions.
