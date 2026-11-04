# Diagram fact check

Sources: report.md (shared-gpu report), gb10-profiling-plan.md (plan), design package (dp). Only problems and notes are listed.

| Figure | Element | Diagram says | Source says | Verdict |
|---|---|---|---|---|
| f16_two_way | Declaration row: "No memory or GPU-quantity field today" | No GPU-quantity field exists | dp reference/run-plan.md:79 and :98 (and capsules/planner.md:163): `resource_needs` entries carry `min_quantity` ("for example one GPU"), and `resource_feasibility` checks it. The memory half is right (field-catalog.md:1038, declaration carries no memory budget). | wrong (GPU-quantity half; true only if limited to the declaration file, and declaration.md shows no quantity field) |
| f16_two_way | Host checks: "need clause, budgets" declared vs observed | Host checks compare declared need clause and budgets with observation | checking/README.md:96 and verifier.md:207 describe host checks on identities, permissions, limits, required fields, and an effects check from workspace.tar. No check against observed CPU/GPU use is described. | unsupported (reads as existing; only the right-hand "New usage clause" is a proposal) |
| f16_two_way | "New usage clause: ... memory claim" | A memory claim is checked | Declaration has no memory claim; memory_mb lives in the admission record (field-catalog.md:1038). | ok-with-note (a proposal, needs a new declaration field) |
| f16_two_way | RSI: "medians, noise rule" | Timing method includes medians | owner-rulings.md:56 gives 5 warm-up batches and 7 paired rounds; rsi-workbench.md:216 gives "calibration, 7 paired rounds and the noise multiplier". No source says medians. | unsupported (medians only) |
| f16_two_way | Planner: execution-profile seam (run-plan.md:645) | Seam exists at line 645 | Line 645 exists: "Parallel branches need declared effects, resources and an execution profile." M1 runs one node at a time. | ok-with-note (seam is for parallel branches, not for a predicted profile) |
| f16_two_way | Admission "Self-tests run the pinned version" | Self-tests run pinned version | platform/README.md:29 (PLT-12): admission runs self-tests in the confined executor. | ok-with-note |
| f1_pipeline | Chip "NOT SCHEDULED" under Planner + scheduler | Planner and scheduler not scheduled | 3-build-plan.md: a bounded Planner, binder and SwarmFlow scheduler are M1 core. Only profile-aware planning/pairing is unscheduled. | unsupported (chip is ambiguous and reads as if the M1 Planner is unplanned) |
| f1_pipeline | "x2.08 slower (our n=2)" | 2.08 from n=2 | report.md B.2 line 405: x2.08, 2 paired runs. A.4 line 306: ranged x1.7 to 2.4 over the two runs. | ok-with-note (range not shown) |
| f14_runner | GPU signals box: "DCGM device-wide, Nsight per kernel" | Both are signal sources on the host-side profiler | plan:29 and :140: DCGM profiling on GB10 is unproven (probe first) and its counters conflict with Nsight counter sessions. plan diagram (line 103) says "NSYS timeline / NCU kernels". The report (A.3) measured with Nsight Systems inside the container and NVML, never DCGM. Host-launcher origin and device-wide scope are right (plan:96, :43, :75). | unsupported (DCGM as a working source; the two cannot run in the same session) |
| f14_runner | Host launcher to GPU signals; container to cgroup+PSI | GPU signals host-side and device-wide; cgroup belongs to container | plan:31, :43, :96-107 and report.md A.3 scope table (lines 283-287). | ok |
| f4_gpu_map | Signal column "DCGM" for SM_ACTIVE, PIPE_*, DRAM_ACTIVE, PCIE/NVLINK bytes | These come from DCGM | plan:29: DCGM "can expose" these, availability on GB10 "a preflight question". Report measured them via Nsight Systems GPU metrics at 10 kHz (A.2 line 258). | unsupported (as measured source) |
| f4_gpu_map | Interconnect "PCIe / NVLink / C2C" | C2C listed | No source mentions C2C. | unsupported |
| f4_gpu_map | "NVENC alone read 1% DRAM and 0% SM" | as stated | report.md B.5 line 464: 1% DRAM, 0% SMs active. | ok |
| f3_memory | B: "fastest when data sits next to the processor that uses it (CUDA guide)" | cited to CUDA guide | No CUDA guide is in the sources; plan cites only the DGX Spark porting guide. | unsupported |
| f3_memory | C: "nvidia-smi: Memory-Usage 'Not Supported'" | Stated as fact | plan:20: nvidia-smi "may report framebuffer memory as unsupported on iGPU/UMA". Not verified on our unit. | unsupported (overstated, "may") |
| f3_memory | C: "CPU work and GPU work fight for the same bandwidth" | Stated as fact | report.md lines 201 and 183: an expectation ("new interference is likely"), not measured. | ok-with-note (label as expectation) |
| f3_memory | A: "28.5 GB/s pinned, 10-17 GB/s pageable" | as stated | report.md B.7 lines 496-501: pinned 28.45 (to CPU) and 28.70 (to GPU); pageable 10.03 and 16.72. | ok-with-note (28.5 is the to-CPU value only; range 28.5-28.7) |
| f12_record | Record 3: "remote wait, model_calls, tokens" | Part of measured outcome | plan:120 lists phase boundaries, kernels, signals, cgroup, latency/throughput/energy, quality/OOM. Remote wait and tokens not listed (model_calls exists only as a Limits count in run-plan.md:80). | unsupported |
| f12_record | Arrows 1 -> 2 -> 3 | Sequence between records | plan:116 says "three linked records"; plan:55 only requires 1 known before launch and 3 after. | ok-with-note |
| f12_record | Record 1 "phase list and order"; record 2 "sharing mode, concurrent jobs" | as stated | plan:118 puts "phase and concurrency" in record 1; plan:119 puts "sharing mode" and "background jobs" in record 2. | ok-with-note (concurrency placement differs) |
| f15b_attach | "library max_limits: copied from admission" | all from admission | run-plan.md:80: only `memory_mb` comes from the admission record; `time_s` comes from declaration `wall_s`, `model_calls` from `invocations`. | ok-with-note (partial) |
| f15b_attach | other four "not a landing spot" reasons | ext ignored; needs/budget protected, RSI cannot edit; inventory host intake only; Planner output cannot set a policy value | declaration.md:41 (ext accepted-unused); :423 and :426 (/needs and /budget always-protected); run-plan.md:183 and :191 (host intake writes the list, never a CC); run-plan.md:199 (Planner cannot change plan_policy). Footer: sidecar README:107 and owner ruling 9 confirmed. | ok |
| c_scope | Tile "5 model sizes, 0.5B to 14B" vs bar label "X2 ... 4 sizes" | 5 sizes in X2-era runs, 4 sizes in X2 | report.md A.2 line 262 lists 5 models (0.5, 1.5, 3, 7, 14B); B.3 and B.5 give results for only 4 (no 1.5B). | unsupported (1.5B has no result row) |
| c_scope | Per-experiment counts | X0 6, X1 3, X2 21, X3 8, X4 28, X5 32, X6 6, X7 28, JIT 8 | A.4 id ranges give the same: 3+3, 3, 21, 8, 4+24, 8+24, 6, 28, 8. Total 140 (sum of ranges). | ok |
| c_scope | Tiles 1,760, 354k, 20 GB, 2 to 12, 100 ms, 10 kHz, 13 pair cells | as stated | report.md lines 117, 348 (353,970 for one task), 333, 181, 277, 258, B.2 (13 rows). | ok-with-note (1,760 starts are not among the 140 runs; 354k is one task, run 254) |
| c_scaling | Bars 294/545/737/723 and tok/s 738/283/157/80 | as stated | B.3 lines 420-426. | ok |
| c_scaling | Ceilings 850 and 770 | matrix-vector and copy ceilings | B.7: 849.71 (matrix x vector) and 769.85 (GPU memory copy). | ok |
| c_scaling | 273 GB10 spec line | A spec, not measured | plan:20 (NVIDIA docs). Labelled "spec (NVIDIA docs)" correctly. | ok-with-note (the bars are RTX 5070 Ti measurements, not GB10; the 294 bar sits above the 273 line and the chart does not say the bars come from a different machine) |
| c_fingerprint | All 24 cells | as stated | B.5 lines 455-464 (7B decode, 7B prefill, CNN fp32/AMP, speech, NVENC). | ok |
| c_levers | Eight values (6.14, 2.7, 0.049; 64.4, 5.3; 258, 614, 8.9 vs 2.5 GiB; 3, 49, 219 ms) | as stated | B.8 lines 513-519, 544-548; B.1 lines 392, 396. | ok |

## Elements checked per figure

- f1_pipeline: 15 (7 boxes, 7 chips, 3 callouts; no arrow implies live runs write profiles; caption "written only by quiet-window runs" matches plan:75). Chips otherwise match: declaration designed M1; OCI image, solo run, record PROPOSED (plan:37, :39, :114); predictor HYPOTHESIS; live runs M1 serial (run-plan.md:645).
- f14_runner: 14
- f3_memory: 13
- f12_record: 18
- f16_two_way: 24
- f15b_attach: 12
- f4_gpu_map: 14
- c_fingerprint: 24
- c_scope: 18
- c_scaling: 12
- c_levers: 12
