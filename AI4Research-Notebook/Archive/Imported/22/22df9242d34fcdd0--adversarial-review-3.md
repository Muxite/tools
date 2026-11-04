# Adversarial review 3: AI4Research Workload Profiling - Quiet Windows

Scope: the whole deck (30 slides, 22 main), the renders in `review/`, deck.json, planner_baselines.py (re-run), future-path.md, the source report and the design package. I did not read the earlier reviews or the v1 files.

## 1. Verdict

1. The deck is mostly honest. It labels the 5070 Ti numbers as unaudited, says no GB10 result exists, and the arithmetic checks out (planner_baselines.py reproduces 40.0 / 26.5 / 22.9 / 21.0 / 21.0, and the bounds 58/48 and 30/25).
2. Its main weakness is the story. The motivating data (LLM decode beside CNN training, NVENC, speech) is never mapped to AI4Research capsules, and slide 3 shows that in M1 no capsule contends for the GPU. So the "why" depends on future features that have no milestone.
3. Five claims overreach. Slide 4 says kernel times split under sharing, but the source says they absorb other tasks' time. Slide 13 says the declaration has "no GPU field", but slide 3 shows `gpu_device exclusive`. Slide 14 says two rulings "forbid this". Slide 7's title says time-split "fits". Slide 22 says "add/ship" schema changes the deck cannot authorize.
4. Status framing slips in four places. Slides 13 and 15 use present-tense titles ("feed each other", "authorized quiet window"), slides 15 and 16 have no PROPOSED marker, and the notes for slide 20 say "the funded first step".
5. Answer to the core question: the deck honestly says "unknown, here is a test". It does not state the likely M1 answer up front: the M1 bottleneck is remote Codex wait, which GPU profiling cannot predict. The chip-design path is a fair list of needed controlled changes, but the step from one GB10 to chip conclusions is under-argued.

## 2. Story gaps (whole deck)

1. **Premise against reality (slides 1-3, 6-8).** The title and slide 2 open on contention ("LLM decode ran 2.1x slower beside CNN training"). Slide 3 then shows that M1 has no local GPU contention: everything is serial, and every capsule except benchmark runs on remote Codex. The deck never says which AI4Research capsule looks like "CNN training", "NVENC" or "speech-to-text". The four measured task families are proxies with no stated mapping to capsules. Fix: right after slide 3, state the mapping, or say there is none yet.
2. **The predictor's inputs depend on counters that may not exist (slides 4, 17, 20, 22).** Slide 17's "solo features" are DRAM %, tensor % and GPU busy. These are exactly the device counters that test 1 may find unavailable on GB10. Slide 22's branch for "no usable counters" says "keep timing, memory and cgroup records". It does not say what happens to the predictor test. One more row is needed: without counters, the predictor uses only kernel median and launch rate (from Nsight), or the test is dropped.
3. **The one-bit label is itself a profile (slides 12, 17, 22).** Baseline B1, "no two GPU-heavy", needs to know which nodes are GPU-heavy. The toy script hard-codes A and B as heavy, a choice made from measured solo behaviour. No declaration field carries such a label today. So "a label finds it without any profile" (slide 12 notes) is circular. The stop rule "ship the label" still needs a minimal solo measurement plus a schema change.
4. **No GB10 pair data is scheduled for the predictor test (slides 17, 20).** Test 5, "Predictor hold-out", needs measured pair slowdowns on GB10. The test list schedules only two single pairs (tests 3 and 4) and no GB10 pair matrix. Either add a "GB10 pair matrix, 4 families x n repeats" step before test 5, or say the hold-out runs on 5070 Ti pairs.
5. **The gate rests on synthetic cases (slides 20, 21).** gb10-profiling-plan.md Phase B says a synthetic kernel "is calibration, not evidence of the project task mix". Yet the sizing covers only the 5 synthetic cases ("real-capsule runs are extra"), and the go/narrow/stop gate comes after them. The gate should require at least the benchmark capsule and one builder POC.
6. **The online feedback loop conflicts with a stated constraint (slide 2).** The dashed arrow "observed outcomes become new evidence", drawn from live parallel runs back to the record, needs in-run sampling. Owner ruling 9 (owner-rulings.md:123) excludes continuous CPU/GPU sampling in run capture, which the deck cites on slides 13 and 14. Mark the arrow as needing the same owner decision, or limit it to outcome timings that run capture already records.
7. **The statistical weight is admitted and then dropped (slides 17, 22).** Slide 17 correctly says leave-one-out over 4 families "is a feasibility check, not a statistical test". Slide 22 then turns "predictor beats the label" into adding a protected planner input. future-path.md row 4 keeps the qualifier "by more than the repeat spread" and the verb "propose". Slide 22 drops both.
8. **The repeat spread is over-generalised (slide 17).** The report (report.md:306) says most co-run slowdowns repeat within about x0.1. Only LLM beside training ranged x1.7 to x2.4. Slide 17 turns that one pair into "no error target below that is testable", which is too strong for the other pairs.
9. **The step from one chip to chip design (slide 18).** Sweeps on one GB10 give sensitivity at one design point. For chip conclusions you need either several operating points or a simulator validated for this architecture. Accel-Sim is NVIDIA-discrete-GPU oriented and has no LPDDR unified-memory model. "Calibrate Accel-Sim on the baseline" hides that porting effort. The deck should say that the simulator row is a research risk, not a step.
10. **The quiet-window authority is unresolved but the title says otherwise (slides 14, 15, 21).** The only reserved-window mechanism in the package is the sidecar's for exclusive GPU benchmark cases (sidecar/README.md:103). The deck's profiler is not that runner. Slide 15's title "authorized quiet window" assumes the open decision is already made.

## 3. Class (e) ledger: unsupported, overclaimed, or (b) found wrong

| # | Slide | Text now | Problem | Replacement |
|---|---|---|---|---|
| 1 | 2 | "Two big GPU jobs together: LLM decode ran 2.1x slower beside CNN training (our measurement)." | No card or n; it reads as if it were on the target | "On our RTX 5070 Ti (n=2, unaudited), LLM decode ran 2.1x slower beside CNN training. Not yet measured on GB10." |
| 2 | 2 | "Device counters cannot be split per process in a busy run, so we record them alone and look them up." | "look them up" assumes solo counters predict busy runs, which is the open hypothesis | "...so we record them alone. Whether solo records predict busy runs is the hypothesis under test." |
| 3 | 2 | Chip "NOT SCHEDULED" under "Planner + scheduler" | The Planner is designed for M1 (planner.md). Only pairing is unscheduled | "PAIRING: NOT SCHEDULED" |
| 4 | 3 | "Never paired by declaration" (research.benchmark) | `exclusive` means "no other node may use it during the attempt" (declaration.md:208), so it binds only nodes that declare `gpu_device`. A builder POC that runs GPU code without declaring it is not excluded. M1 is serial anyway | "Exclusive against nodes that declare gpu_device; M1 runs nodes one at a time anyway. Peak memory measured at first pilot (benchmark-runner.md:23)" |
| 5 | 4 | "Only the counter part of a record needs the GPU alone. Time, kernels, memory and cgroup data split even under sharing" | report.md:286 says "Under sharing a kernel's duration also includes time the GPU spent on others". Slide 8 shows the same. Whether GB10 cgroups see GPU allocations is unproven (slide 11) | "Device counters need the GPU alone. cgroup data and per-process GPU memory split under sharing; kernel durations split but include time switched out, so solo timing also needs a quiet GPU" |
| 6 | 4 | Nsight Systems: "Yes: kernels, copies" | Same issue as row 5 | "Yes, per process, but durations include time the GPU served others" |
| 7 | 5 | Title "dashboards go blind" | Only nvidia-smi Memory-Usage is unsupported (NVIDIA known issues, verified). Per-process memory, utilization and power remain | "On GB10 the GPU shares one pool and nvidia-smi shows no GPU memory total" |
| 8 | 5 | Panel C "CPU work and GPU work fight for the same bandwidth" | Shared bandwidth is a spec fact; contention is untested (slide 11) | "CPU and GPU share the same 273 GB/s; how much they interfere is untested" |
| 9 | 6 | "Training slows only x1.16: long kernels hold the GPU" | The mechanism is the report's interpretation (report.md:101). report.md:211 lists it as an open question | "Training slows only x1.16, likely because its long kernels hold the GPU (not isolated)" |
| 10 | 6 | "Speech-to-text and NVENC stay between x0.98 and x1.12" | Their own slowdowns are x0.98 to x1.08 (table B.2). x1.12 is the LLM slowing beside NVENC | "Speech-to-text and NVENC slow by x0.98 to x1.08 and slow others by at most x1.12" |
| 11 | 7 | Title "Time-split fits three pairs but needs co-run shares" | Error on DRAM read is 9%, 2% and 22%. SMs active is 21% off for LLM+LLM, and DRAM write is off too (table B.6). "Fits" is too strong | "Time-split comes within 2 to 22% on DRAM read, but needs co-run shares" |
| 12 | 8 | y-axis "GPU busy with this process, %" with bullets saying "trace span" | Inconsistent metric names. The bullet says span includes switched-out time, so it is not "busy" | Rename axis "Kernel trace span, % of window" |
| 13 | 8 | "91% in total" against notes "mean stream 63.4 of 283.5" | 4 x 63.4 = 253.6, which is 89%. 91% comes from the table total of 258 (B.1). Small mismatch | Quote one source: "258 of 284 tok/s total (91%, table B.1)"; per stream 22 to 26% |
| 14 | 10 | "A time-based utilization number does not show that" | Device utilization during the four-LLM run is not reported | "A time-based utilization number would not show that (inferred: solo decode already reads 91% busy)" |
| 15 | 11 | Title "What will change on unified memory" | Five of seven rows are Unknown or Untested | "What may change on unified memory" |
| 16 | 11 | "PCIe cliff goes away" (Partial CPU offload, GB10 column) | Stated as fact; Status says Unknown | "No PCIe copy; the offload cost on shared LPDDR5x is unmeasured" |
| 17 | 12 | "Profiles earn their cost with many GPU-heavy classes, and for memory and routing" | A hypothesis stated as a result; the toy shows the opposite for pairing | "Profiles might earn their cost with many GPU-heavy classes, or for memory and routing; untested" |
| 18 | 12 notes | "A one-bit GPU-heavy label picks the best pairing without any profile" | Circular: the label needs to know which nodes are heavy (gap 3) | "...picks the best pairing, given someone already knows which nodes are GPU-heavy" |
| 19 | 12 | "Parallel nodes stay outside M1 with no milestone (planner.md:216)" | planner.md:216 verifies "outside M1". "No milestone" is an absence claim. D33 (decisions.md:138) puts Agent Team and Cluster Mode in Phase 3, which is part of M1, without saying how concurrent they are | "Parallel nodes stay outside M1 (planner.md:216, run-plan.md:645); no later milestone names them" |
| 20 | 13 | Title "The CC layer and profiling feed each other" | Present tense; profiling does not exist | "How the CC layer and a profiler could feed each other (proposed)" |
| 21 | 13 | "No memory or GPU field in the declaration today" | Wrong as written. `needs.resources[].resource_key` can be `gpu_device` with mode `exclusive` (declaration.md:207-208; research_benchmark_capsule.json:131), and slide 3 says so. The notes say "no ... duration field", but `budget.per_call.wall_s` exists (declaration.md:368) | "No memory field and no GPU quantity in the declaration; GPU appears only as a resource key with read/write/exclusive mode. memory_mb comes from admission (run-plan.md:80)" |
| 22 | 13 notes | "memory_mb is the only resource number and it is a placeholder today" | "placeholder" has no source. field-catalog.md:1038 says the admission operator sets it. Only the plan-policy aggregate 32768 "may be lowered" by the pilot (run-plan.md:224) | "memory_mb is a per-node-attempt ceiling set by hand at admission (field-catalog.md:1038), at most the plan-policy aggregate of 32768 MiB" |
| 23 | 14 | Chip "Sidecar README:107 and owner ruling 9 forbid this today" | Misattributed. README:107 says the sidecar adds "no profiling integration, CC diagnostic API or new product telemetry". Ruling 9 forbids continuous CPU/GPU sampling in run evidence capture. Neither addresses an offline profile store or a protected planner input | "Sidecar README:107 rules out profiling in the sidecar; owner ruling 9 rules out continuous sampling in run capture. An offline profiler and a new protected input need owner decisions" |
| 24 | 15 | Title "Pinned containers in an authorized quiet window" | No authorization exists (open decision 2 in future-path.md) | "Pinned containers in a quiet window (window policy not yet decided)" |
| 25 | 15 | Unlabelled bullets "No process is preempted", "Every run kept, crashes too", "Preflight ... all checked" | Proposed behaviour read as built; no status chip on the slide | Add a PROPOSED chip; prefix "Proposed:" |
| 26 | 15 | "Sidecar README:107 bans it today" (row: Paper2Agent packaging / declaration change) | Unclear what "it" is; README:107 is scoped to the sidecar | "Sidecar README:107 excludes profiling integration from the sidecar" |
| 27 | 16 | "Planner falls back to declared exclusive or serial" | No such fallback is designed. M1 is serial for every node | "Proposed: the planner treats an unprofiled capsule as exclusive or serial" |
| 28 | 17 | "Spread first: LLM beside training varied x1.7 to x2.4 over two runs, so no error target below that is testable" | Over-generalised. Most pairs agree within about x0.1 (report.md:306) | "Most pairs repeated within about x0.1, but LLM beside training ranged x1.7 to x2.4; measure repeat variance per pair before setting a target" |
| 29 | 17 | "Time-split with measured shares is an upper bound, not a predictor" | Not shown to bound anything (it is 2 to 22% off) | "Time-split with measured shares is an oracle reference, not a predictor" |
| 30 | 20 notes | "Tests 1 and 2 are the funded first step" | Implies funding exists | "Tests 1 and 2 are the first step we ask to fund" |
| 31 | 22 | "Ship the label in declarations" | The declaration has no such field; changing it needs the schema owner | "Propose a GPU-heavy label to the declaration owner" |
| 32 | 22 | "Add the protected profile input and admission clause, ahead of parallel branches" | The deck cannot authorize this. future-path.md row 4 says "Propose" and "by more than the repeat spread" | Row: "Predictor beats the label by more than the repeat spread (4 families: feasibility only)" then "Propose the protected profile input and admission clause to the planner and CC schema owners" |
| 33 | 21 | "Quiet window: On the single product host (D35). Launcher never preempts" | "Launcher" is the sidecar host launcher (README:103). No profiler launcher is designed | "Proposed: the profiler follows the sidecar rule (README:103): reserved window, never preempts a core run" |

### (b) claims checked and found correct (for the record)

- declaration.md:41: `ext` is "accepted-unused" and consumers may ignore it.
- run-plan.md:80: `memory_mb` in `max_limits` comes from admission because "a declaration carries no memory budget".
- field-catalog.md:1038: `memory_mb` is the per-node-attempt ceiling, set by the admission operator, not above the plan-policy aggregate, and an RSI child copies its parent value. This supports slide 16, "RSI child inherits memory_mb".
- run-plan.md:224: 32768 is the plan-policy `aggregate_limits.memory_mb`.
- run-plan.md:191: inventory is set by host intake, never by a CC.
- run-plan.md:645: the execution-profile seam for parallel branches.
- checking/README.md:29: host checks cover declared versus observed scope and budgets.
- checking/README.md:30, :94 and D24: the verifier sees only the pinned declaration and the output.
- The always-protected set covers `/needs` and `/budget` (declaration.md:418-427).
- owner-rulings.md:123 (ruling 9) and sidecar README:103 and :107, as quoted.
- rsi-workbench.md:174: 5 warm-ups, 7 paired rounds, medians, more than 3x the calibrated noise.
- research-benchmark.md:29; the builder's Codex CLI; qwen.code30b in model-catalog.md.
- benchmark-runner.md:278 `hardware_inventory` with `execution_peaks`.
- External sources: NVIDIA DGX Spark known issues ("Memory-Usage: Not Supported", per-process memory listed, /proc/meminfo); DCGM feature overview (device-level, 1 Hz default, conflicts with Nsight); GKE DCGM (21 metrics, pod/container/namespace labels).
- All 5070 Ti numbers I spot-checked against report.md match: B.1, B.2, B.3, B.6, B.7, startup and offload. The 5.7 figure is 0.91/0.16.

### (b) not independently verified

- AWS ECS Managed Instances per-container GPU metrics, and the EKS add-on v6.0.1 note in the slide 10 notes.
- The Orin HiPC 2023 container-overhead finding.
- The GB10 specs (20 Arm cores, 273 GB/s) are consistent with gb10-profiling-plan.md, but I did not re-fetch them.

## 4. Layout defects (from the renders)

- **Slide 7:** the right chart's y-axis label is clipped at the left edge ("total tokens per second" is cut).
- **Slide 10:** the footer source runs off the bottom edge. The second line ("...shared-gpu/report.md") is cut.
- **Slide 12:** the footer source runs off the bottom edge ("design-package/reference/run-" is cut).
- **Slide 8:** the y-axis wording contradicts the bullets (ledger row 12).
- **Slide 2:** box text touches the borders. "joined, versioned," fills the Profile record box, and "estimate + spread" touches the Predictor box edges.
- **Slides 11, 18 and 19:** the bottom 25 to 30% is empty. The tables could use larger type or carry the missing qualifiers.
- **Slide 15:** the left bullet list has uneven spacing. "Preflight: GPU idle, temperature, / memory, swap all checked" wraps so it looks like two items.
- **Slide 26 (appendix):** the 7B and 14B decode labels overlap at 78% DRAM.
- No slide is unreadable. Slide 13's figure text is small but legible.

## 5. The five changes that would most improve the deck

1. **Lead with the honest M1 answer and the mapping.** After slide 3, add one line: "In M1 the bottleneck is remote Codex wait; GPU profiling cannot predict it. The pairing case starts only with local models or experiment capsules." Also state which capsule each measured task family stands in for, or that none does yet. This closes story gaps 1 and 2.
2. **Fix the two factual errors that a design reviewer will catch first.** On slide 4, kernel times under sharing include switched-out time (report.md:286). On slide 13, the declaration does carry GPU as a resource key with exclusive mode, and has `wall_s`. Make slide 13 agree with slide 3.
3. **Re-word every authority claim as a proposal to a named owner.** Slide 14 chip (row 23), slide 15 title (row 24), slide 22 "Ship/Add" (rows 31 and 32), slide 20 notes "funded" (row 30). Add PROPOSED chips to slides 15 and 16.
4. **Make the test plan internally complete.** Add a GB10 pair-matrix step before test 5. State what the predictor uses if test 1 finds no counters. Put at least one real capsule inside the gate and the sizing. Note that the one-bit label itself needs a solo measurement and a declaration field.
5. **Tighten the result titles to what was measured.** Slide 5 "dashboards go blind", slide 7 "fits", slide 11 "will", slide 12 "Profiles earn their cost", slide 17 spread wording. Also flag the Accel-Sim-on-GB10 step on slide 18 as a research risk rather than a calibration step.
