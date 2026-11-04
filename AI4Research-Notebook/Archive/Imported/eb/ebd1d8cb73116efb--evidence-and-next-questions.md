---
title: Evidence and next questions
status: exploratory
captured: 2026-10-16
tags:
  - planning
  - gpu
  - evidence-log
---

# Evidence and next questions

This note records what the imported report can suggest for resource-aware planning, while keeping its scope and evidence limits visible. It is exploratory and does not establish a requirement, architecture, planner policy, or current-machine fact.

## Evidence log (append-only)

### 2026-10-16 — published report captured

Source: [Shared GPU, same node](sources/2026-10-16-shared-gpu/report.md), with retained [HTML](sources/2026-10-16-shared-gpu/report.html), [chart data](sources/2026-10-16-shared-gpu/chart-data.json), and [capture metadata](sources/2026-10-16-shared-gpu/capture.json). This entry records only the published report as imported on this date. No source ledger, CSV, or trace was available here for independent recalculation.

The report describes a single RTX 5070 Ti workstation. Its paired runs indicate asymmetric contention: an LLM decode workload slowed about 2.08× beside CNN training while training slowed about 1.16× beside decode (report §“Who loses depends on the shape of the work”; Appendix B.2). The report's task-level GPU traces show training receiving 84% and decode 16% of GPU time in that pairing (§“Two tasks on one GPU take turns”; Appendix B.6). These results suggest that a shared-resource planner may need task-specific effects and service priorities, rather than assuming equal slowdown or additive device use. They do not establish behavior on another GPU, backend, driver, software stack, or workload.

The report also contrasts four separate qwen2.5 3B processes with four requests batched in one process: reported aggregate throughput was 258 versus 614 tokens/s, and GPU memory 8.87 versus 2.51 GiB (report §“Separate copies of a model lose to batching in one process”; Appendix B.1). It reports cold-path costs: a fresh Ollama container took 64.4 s without a shared GPU-code cache versus 5.3 s with one; a 7B model's first-token time was 0.049 s when already in GPU memory, 2.70 s from RAM, and 6.14 s from disk (report §“Starting a task is cheap; starting it cold is not”; Appendix B.8). These are useful hypotheses about batching and warm-state availability, not portable constants. Repeat counts are small for many comparisons (often two); the report itself notes variation, including 1.7–2.4× for decode beside training. Profiling overhead, one hardware setup, workload choices, and imported-source status constrain interpretation (§“Limits…” and Appendix A.4).

## Questions for future evidence

The gauge repository, its revision, `DATA_CARD.md`, dataset CSVs, ledger, and compact traces remain on the other machine. Before using further results, identify the exact repository revision and map each exported row or trace to its run and workload. Preserve the data card and conditions alongside any derived summaries; do not treat chart values alone as a reproducible dataset.

For follow-up measurements, record machine and accelerator identity, memory layout, OS, driver/runtime, backend and version, model/workload parameters, and measurement tools. Pair solo and co-run conditions in the same profiling mode; distinguish LLM prefill from LLM token decode and media encoding from media decoding, and whether the model, container, and compiled GPU code are cold, warm in RAM, or resident on-device. Include repeated runs, report distributions or uncertainty, and retain failed or censored runs with their status. Compare availability and resource effects under stated concurrency, including memory pressure and queueing, rather than inferring them from utilization alone.

Small experiments could vary inference backends while holding the model and task fixed, then compare solo and co-run behavior for LLM prefill versus token decode. For a separate video task, compare supported hardware encoding and decoding paths against CPU fallbacks, recording codec, quality settings, and device availability. A separate warm-state sweep could measure first-result latency with model weights in disk cache, RAM, and accelerator memory where the backend permits. On a unified-memory machine, examine whether CPU/GPU co-runs contend for shared memory bandwidth and whether loading paths converge. These are candidate questions only; no benchmark is run or claimed here.
