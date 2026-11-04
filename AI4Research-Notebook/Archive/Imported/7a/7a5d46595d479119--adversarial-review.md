# Adversarial review: "AI4Research Workload Profiling - Quiet Windows"

Reviewer stance: a hostile but fair expert who has to decide whether to fund the work. Each claim was checked against the deck spec (`deck.json`, cited as `deck.json:LINE`), the rendered slides in `review/`, the measured source (`sources/2026-10-16-shared-gpu/report.md`, cited as `report.md:LINE`, and `chart-data.json`), the plan (`gb10-profiling-plan.md`, cited as `plan:LINE`) and the design package (`design-package/reference/run-plan.md`, cited as `run-plan:LINE`).

Slide numbers follow the rendered deck: 1 title, 2 proposal, 3 counters, 4 GB10 memory, 5 heatmap, 6 time-split and batching, 7 jagged timeline, 8 model routing, 9 AWS vs DGX Spark, 10 unified-memory caveat, 11 planner 33%, 12 containers, 13 record, 14 node checks, 15 six advantages, 16 attachment, 17 do/avoid, 18 next tests, 19 divider, 20 to 26 appendix.

Verdicts: **defended** means the deck answers the question with evidence. **Partly** means the deck admits the issue but does not resolve it, or the answer is only in the notes. **Undefended** means the deck has no answer.

---

## 1. Top 8 most damaging weaknesses (ranked)

### W1. The central claim, that solo profiles predict busy runs, is never demonstrated, and the deck's own interference model needs co-run data (slides 2, 6, 11, 13; undefended on the main slides, partly conceded on 25)

**Attack.** The title promise is "Profile alone, store the record, predict the busy runs" (deck.json:28). The only interference model in the evidence is the time-split blend (slide 6). Its inputs are each task's **GPU time share during the co-run** (report.md:312-314, B.6 report.md:466-472). That share is an outcome of contention. A solo run cannot give it. The "2 to 22% switching loss" is the residual between the model and the measurement, fitted after the co-run (report.md:318). A model with a free residual term of up to 22% that is only known after the fact is not a predictor. The model was also tested on one counter (DRAM read), not on completion time, which is what the planner needs. For DRAM write in LLM+LLM the measured value (1.6) is above the time-split value (1.0) (report.md:490), so the "switching loss" is negative there. The report itself lists "Can a node's own profile predict its time share?" as an open question (report.md:211). Slide 11 uses **measured pair slowdowns**, not values predicted from solo profiles. Nothing in the deck goes from a solo record to a pair slowdown.

**Deck defence.** Slide 25 concedes "Prediction accuracy: no predictor has been built or held out" (deck.json:1058). Test 3 and plan Phase D (plan:73-77) move pair testing later. The pitch on slides 1, 2 and 16 still presents prediction as the mechanism.

**Fix.** Reframe the proposal as two parts: solo records in quiet windows, plus a small, deliberately chosen pair matrix. Add a falsifiable test to slide 18: predict pair slowdown from solo features only (kernel length, GPU busy, DRAM share) on held-out pairs, and report the error against two baselines, "no interference" and "a one-bit GPU-heavy label". State the accuracy the planner needs, for example a slowdown error under 0.2x, and the result that would stop the program.

### W2. The deck says busy runs cannot be profiled per process, and its own data shows a per-process profile of a busy run (slides 2, 3, 7, 9; undefended)

**Attack.** Slide 2 says "Busy runs cannot be profiled per process, so we look the profile up instead of measuring it". The slide 3 notes say "per-process GPU truth is not on offer anywhere" (deck.json:109). Slide 7 is itself a per-process kernel trace of one LLM taken while four processes shared the GPU. The report's scope table says per-process GPU memory and every kernel and copy (CUPTI) are "isolated to one task ... even when sharing", and cgroup counters are "Yes, exactly, even when sharing" (report.md:285-286). Only the device counters (SM, tensor, DRAM %) are device-wide (report.md:287). The plan also lists DCGM per-PID and job statistics as a possible attribution path (plan:30). The deck drops that path. Datacenter GPUs offer MIG for counter isolation, and the deck never says whether MIG is available on GB10. A reviewer will say the attribution problem is narrower than claimed: only counter-level resource shares cannot be attributed, while per-process time, kernels and memory can. That weakens the reason the GPU must be taken away from production.

**Deck defence.** Slide 3's table is accurate per tool. The headline sentences overreach it.

**Fix.** State the exact gap: "device counters (SM, tensor and DRAM activity) cannot be split per process. Kernel time, memory and cgroup data can be split, even under sharing." Then argue that quiet windows are needed only for the counter-level part of the record. Say what the record would lose if it were captured online from per-process traces instead. Add DCGM job statistics and MIG to the slide 3 table with their GB10 status, which is a preflight question.

### W3. No evidence that GPU contention matters for AI4Research's real workload (slides 2, 5, 11, 15; undefended)

**Attack.** The measured tasks are llama.cpp qwen2.5 Q4 decode, synthetic ResNet training, and the wonhee video pipeline used "as a stand-in for agent work nodes" (report.md:153, 260-265). None of them is an AI4Research capsule. In M1 the default model route is the Codex CLI (design-package/README.md:48, model routing "Phase 1 stays fixed Codex"). Most capsule time is probably remote model wait plus CPU and tool work, not local GPU work. The plan itself says "measure actual task mix before treating that as established" (plan:39). The test list on slide 18 has no task-mix measurement. The one GPU capsule in the design, the Research Benchmark CC, "needs one exclusive GPU" (side-systems/benchmark-runner.md:23). Under `exclusive` no other node may share the GPU (run-plan:97), so profile-aware pairing cannot apply to it at all. The supervisor's question will be: which capsules would this pairing ever apply to?

**Deck defence.** Slide 25 lists "real agent traffic" as not shown. Nothing else addresses it.

**Fix.** Add test 0 to slide 18: trace one real AI4Research run end to end on the GB10 and break wall time into remote model wait, CPU, local GPU and I/O. If local GPU work is under about 10% of wall time, the planner-pairing argument falls back to the local-model routing case (slide 8). Say so before anyone else does. List the capsules that are expected to use the GPU without `exclusive`.

### W4. The 33% planner win compares against a strawman (slide 11; partly defended by the "illustrative" label)

**Attack.** I checked the arithmetic. With every node at 10 solo: top schedule A+B gives LLM 20.8 and training 11.6, then C+D gives 10.2 and 10.5, so it ends at 31.3. Bottom schedule: LLM+speech and training+NVENC give 21.1. Both match (deck.json:453). The fairness problems:
- The baseline is a gang or barrier schedule. C and D wait until A ends at 20.8 even though B ends at 11.6. A greedy list scheduler starts C next to A at 11.6. I estimate the end at about 26, not 31.3.
- There are only three ways to pair four nodes: {AB,CD} = 31.3, {AC,BD} = 21.1, {AD,BC} = about 21.2. The deck shows the single worst one. A random pairing averages about 24.5.
- A one-bit label ("GPU-heavy, do not co-locate two") finds 21.1 without any profile store or predictor. The example shows the value of a class label, not of quiet-window profiling.
- M1 runs nodes serially (run-plan:645). The baseline the audience actually has is 40, and against 40 even naive pairing wins.
- The LLM-beside-training slowdown ranged from x1.7 to x2.4 over two runs (report.md:306). At x1.7 the top case ends at 27.5 and the saving falls to 23%.

**Deck defence.** The title says "(illustrative)". The notes give equal lengths and say M1 is serial (deck.json:453).

**Fix.** Show five bars: serial (40), random pairing (about 24.5), greedy list scheduling (about 26), one-bit heuristic (21.1), profile-aware (21.1). Add the 1.7 to 2.4 range. Then state the real claim: profiles beat the heuristic only when there are many GPU-heavy classes. Give a case where that happens, or drop the 33% headline.

### W5. Discrete RTX 5070 Ti data is used to back GB10 recommendations (slides 5 to 8, 11, 17; partly defended)

**Attack.** Every measurement is on x86 with a separate 16 GB GDDR7 card over PCIe (report.md:31, 183). The GB10 has a different GPU size (6,144 CUDA cores, plan:20, against 8,960 on the 5070 Ti), about 3.3x lower memory bandwidth (273 GB/s against a 896 GB/s spec), a coherent CPU-GPU memory pool, Arm CPUs, and a different driver build. Slides 10 and 25 correctly say that nothing transfers in absolute terms. Yet slide 17 is titled "each backed" and backs "Pair by resource type" and "Batch, do not clone" with 5070 Ti numbers. Slide 11 uses 5070 Ti slowdowns, and slide 8 sets router rules from them. The new interference mode on unified memory, CPU work stealing GPU memory bandwidth, is "likely" (report.md:201) but has no test of its own on slide 18. Test 5 compares the two machines. It does not test CPU-GPU bandwidth contention.

**Deck defence.** Slides 4, 7, 10 and 25 and the notes on 4 and 10 repeat the caveat. The defence is honest, but it is not reflected in the recommendations.

**Fix.** Mark each row on slide 17 "measured on 5070 Ti, GB10 pending". Add a GB10 test: a CPU memory-streaming job beside LLM decode. Order slide 18 so that the funding ask covers tests 1 and 2 first, then a go/no-go gate.

### W6. The chip-design goal does not follow from this data or this method (slides 1, 2, 13, 24, 25; partly defended)

**Attack.** The stated end goal includes informing future chips for agentic systems. Solo profiles on one fixed chip cannot separate design parameters such as bandwidth, SM count, cache size or C2C link speed. The plan itself says "a bottleneck claim also needs a performance response to a controlled change" (plan:14). The deck has no sensitivity sweeps: memory or GPU clock locks, power caps, MPS active-thread-percentage as a proxy for SM count, working-set sweeps. It has no roofline or per-kernel placement and no calibrated simulator. Slide 24 says the simulator "needs a validated simulator", which is not funded or planned. The workloads are not agentic either. Bursty calls, tool waits, KV-cache reuse across turns and model swaps are "not measured" (report.md:215). One finding does point at chips: decode is bandwidth-bound (slide 22). That is already well known and needs no profiling campaign.

**Deck defence.** Slide 25: "Chip-design conclusions: no sensitivity runs" (deck.json:1062). The slide 2 notes defer it ("feed chip-development questions later").

**Fix.** Either remove chip design from the pitch or add a slide on chip-design method: the controlled knobs available on GB10, the agentic traces to replay, the simulator to calibrate (Accel-Sim, or Chakra traces), and the output format a chip team would accept, such as per-workload sensitivity to bandwidth, compute and capacity with confidence intervals.

### W7. "One LLM of four gets 37%, not 25%" misreads the measurement (slide 7; undefended, and it contradicts slide 9)

**Attack.** If each of four identical processes gets a mean of 37%, the four sum to 148% of the GPU, which is impossible. The report explains why: time share comes from a kernel's span in the trace, and "a kernel's span includes time it was switched out" (report.md:312). The useful throughput share is 63.4 / 283.5 tok/s = 22% (chart-data `concurrency`: separate n=4 per-stream 63.38, solo 283.54). The token time gives the same figure: 3.5 / 15.8 ms = 22%. So each process gets **less** than a fair 25%, which fits a switching cost. It does not get more. I checked the plotted means (solo 1.00, four 0.374) against chart-data `timeline`, so the 37% is plotted correctly but read wrongly. Slide 7 also says "Alone: 100% busy", while slide 9 says "solo 3B decode is already 91% busy" (deck.json:350; B.4 and B.5 report.md:444, 454). These are different metrics (kernel-trace span against device busy), and no slide explains the difference.

**Fix.** Retitle the slide: "Each of four gets about 22% of useful throughput. The trace reads 37% because spans include switched-out time." Name the metric on slides 7 and 9.

### W8. The bandwidth "ceiling" on slide 8 rests on a mislabelled input and best-case assumptions (slide 8; partly defended in the notes)

**Attack.** The source line says "measured bytes per token (decode GB/s over tok/s)" (deck.json:249). The report defines decode bandwidth as **model file bytes x tokens/s** (report.md:320), so bytes per token is simply the GGUF file size: 737/157 = 4.69 GB and 723/80 = 9.04 GB. The arithmetic 273/4.69 = 58 and 273/9.04 = 30 is correct. The weaknesses:
- It assumes 100% of the 273 GB/s peak. The 5070 Ti reached about 82% of its 896 GB/s spec (737/896). At the same efficiency the GB10 figures are about 48 and 25 tok/s.
- It ignores KV-cache and activation traffic. These are small at 256 tokens but grow with the long contexts agents use.
- It ignores CPU traffic in the shared pool. The notes concede this (deck.json:286).
- Batching raises total tokens per second above the ceiling, because weights are read once per batch (slide 6). The router rule of keeping few models resident and batching is therefore not bounded by this ceiling.
- The design's model catalog includes an MoE model, `qwen.code30b` (about 30.5B total, 3.3B active; side-systems/model-catalog.md:57). For MoE models bytes per token is not the file size, so the 7B and 14B dense examples do not describe the models the router will actually choose.
- The router rule "one good large model plus a small one" (deck.json:286) has no quality data at all. Routing is a quality-cost trade-off, and the deck measures only cost.

**Fix.** Label the bar "upper bound at spec peak" and add an 80%-efficiency bar. Correct the source line to "model file size". Add an MoE example. Move the router rule to "hypothesis", or add a quality axis.

---

## 2. Per-slide questions

| Slide | Question | Verdict | Where answered |
|---|---|---|---|
| 1 Title | Which capsules use the GPU at all in M1, given the Codex route? | Undefended | none (see W3) |
| 1 | "Schedule busy runs": M1 has no busy runs (serial). When does this pay off? | Partly | slide 11 notes, deck.json:453 ("gain starts with M2") |
| 2 Proposal | How does a solo record predict a pair or 3-way outcome? | Undefended | none on main slides; slide 25 concedes |
| 2 | "Busy runs cannot be profiled per process": slide 7 is a per-process busy profile, so is that true? | Undefended | contradicted by slide 7, report.md:285-286 |
| 2 | Who owns the predictor, and which field does its output go into? | Partly | slide 16 shows a dashed arrow; run-plan:645 says the execution profile is a future seam only |
| 2 | Each new capsule version (and RSI-generated children) needs a new quiet window. How does profiling cost scale with library growth? | Undefended | none; slide 13 notes mention nearest-neighbour only |
| 3 Counters | Are DCGM profiling metrics even supported on GB10? | Defended as unknown | slide 3 notes, slide 18 test 1 |
| 3 | Why not DCGM per-PID and job statistics (plan:30) or MIG? | Undefended | omitted from the deck |
| 3 | "AWS, Google and Azure ship device metrics": they schedule fleets without quiet-window profiles, so why do we need them? | Undefended | none |
| 3 | Is the DCGM "1 Hz default" the default for dcgmi dmon or for the exporter? | Partly | source map row 1, URL given; exporter default not checked here |
| 4 GB10 memory | Panel B (UVM migration "hides inside GPU busy") was never measured. Source? | Partly | "CUDA guide" in the source line, no URL in source map |
| 4 | Does cgroup memory accounting see CUDA allocations on unified memory? | Undefended | none (report.md:203 says it needs re-validating) |
| 4 | With the product (Compose stack) on the same host (D35), is a "quiet" GPU also quiet memory bandwidth? | Undefended | none |
| 5 Heatmap | n=2 per cell with 3 significant figures. What are the intervals? x2.08 ranged 1.7 to 2.4. | Partly | notes deck.json:160 give the 1.7 to 2.4 spread; no intervals on the slide |
| 5 | Which LLM size, context and batch were used in the pairs? | Undefended | not on the slide; the report does not state the X5 model |
| 5 | "Pair by hardware used": would a one-bit GPU-heavy label do the same? | Undefended | none (see W4) |
| 5 | Is the "x1.02 to x1.12" range accurate? | Partly | the real range is x0.98 to x1.12 (section 4) |
| 6 Time-split | The time shares come from the co-run, so is this a prediction? | Undefended | none (W1) |
| 6 | Was it validated on completion time or only on counters? Only 3 pairs? | Undefended | slide 25 "three measured pairs" |
| 6 | Batched 8 has lower ms per token (5.6) than batched 4 (6.5). Is that a measurement error? | Undefended | none (report.md:393) |
| 6 | Is a constant 2.5 GiB at batch 8 realistic, or is the KV cache preallocated for 256 tokens? | Undefended | none |
| 7 Jagged timeline | 4 x 37% = 148%. What is the 37% a share of? | Undefended | contradicts report.md:312 (W7) |
| 7 | 100% busy alone here, 91% on slide 9. Which is it? | Undefended | none |
| 7 | Is a 600 ms window representative of a 256-token run (about 4 s)? | Partly | the notes say "mean of the plotted window" |
| 8 Routing | Does the ceiling assume spec peak, and does "measured bytes" really mean file size? | Partly | the notes concede bandwidth-bound and CPU-sharing assumptions; the label is wrong (W8) |
| 8 | Where is model quality in the routing rule? | Undefended | none |
| 8 | Routing "does not appear in the plan" (run-plan:646) and models are outside the capsule layer. Who owns residency and how many models stay loaded? | Partly | the notes say "behind RouterPort with a fixed route" |
| 8 | On GB10 "in RAM" and "resident" may converge. Does the 6.1 s against 0.05 s rule still hold? | Partly | slide 10 row "Model load": Unknown |
| 9 AWS vs DGX | "4 LLM processes still read busy": was utilization measured for the 4-process run? | Undefended | not in the report; X7 shows SMs active falling from 84 to 72 for 2 LLMs (report.md:486) |
| 9 | Sources for ECS Managed Instances per-container GPU and the EKS add-on v6.0.1? | Partly | named in the source line, no URL in the source map |
| 9 | Does nvidia-smi on Spark really show per-process GPU memory? | Undefended | no source given |
| 10 Caveat | Why isn't CPU-GPU bandwidth contention a row? It is the main new effect on UMA. | Undefended | report.md:201 lists it; the deck omits it |
| 10 | "Expected to carry over" on what evidence? | Partly | report Limits section, stated as expectation |
| 11 Planner 33% | Why does C wait for A when B ended at 11.6? | Undefended | none (W4) |
| 11 | Why compare against the worst of 3 pairings, not random, greedy or serial? | Undefended | none |
| 11 | What happens at x1.7 or x2.4? | Partly | spread is in the slide 5 notes only |
| 11 | Does Orion (kernel-level co-scheduling) support DAG-level pairing? | Partly | notes cite it; the analogy is loose |
| 12 Containers | Who grants quiet windows on the only product host, and what is the downtime? | Undefended | none |
| 12 | The box "NVIDIA device-wide signals: Nsight Systems, Nsight Compute": these are per-process and per-kernel tools (slide 3). Is that a mislabel? | Undefended | contradicts slide 3 |
| 12 | "+219 ms per GPU container start": overhead or total? | Partly | total; the overhead is +216 ms (section 4) |
| 12 | Paper2Agent and HiPC 2023 are cited without references | Undefended | not in the source map |
| 13 Record | For agent capsules the main cost driver (tokens generated, tool calls, branches) is unknown before launch. What does the description predict from? | Undefended | none |
| 13 | How many repeats per record, and how is variance carried into "spread"? | Partly | slide 18 notes: "repeat counts from pilot variance" |
| 13 | Why Chakra? It is a training-trace format, not one for agent workloads. | Undefended | none |
| 14 Node checks | Why is this slide in a profiling funding deck? | Undefended | none; it is off-topic for the ask |
| 14 | "Early halt saves tokens" is a hypothesis | Defended (labelled) | notes deck.json:539 |
| 15 Six advantages | 5 of 6 rows are unrelated to profiling. Does that dilute the ask? | Undefended | none |
| 15 | Is "Runtime behavior can be evaluated: Proposed" just this deck restated? | Defended (honest status) | status column |
| 16 Attachment | "Feed existing planner fields": `resource_needs` and `max_limits` are copied from the declaration and admission, "never taken from a plan" (run-plan:80, 149). Which existing field takes a prediction? | Undefended | run-plan:645 says the execution profile is a future seam; plan:133 "proposes no schema or planner change" |
| 16 | Is the predictor off the hot path if the planner consumes it at freeze? | Partly | slide 24 "before launch ... planner can use it at freeze" |
| 17 Do/avoid | "Each backed": 4 of 5 "Do" rows rest on 5070 Ti numbers | Partly | slide 10 caveat |
| 17 | "Time-split fits better": on 3 pairs, one counter, with co-run shares | Partly | slide 25 |
| 18 Next tests | Where are task mix, predictor holdout, CPU-vs-GPU bandwidth contention and >2 jobs? | Undefended | none |
| 18 | Row 4: "on GB10" with status "Done on discrete card" | Partly | misleading status |
| 18 | Cost, schedule, owner, success and kill criteria for the ask? | Undefended | notes deck.json:735 ask for an owner only |
| 20 Clouds | Labels on DCGM metrics give pod attribution on dedicated GPUs. Does that undercut "not on offer anywhere"? | Partly | slide 20 says "only Kubernetes labels give workload attribution" |
| 21 GPU map | "Media engines stress memory without GPU busy": NVENC DRAM read was 1% | Undefended | contradicted by report.md:464 |
| 22 Decode | Table mixes decode DRAM and prefill Tensor in one row | Undefended | headers do not say which phase |
| 22 | "95% of ceiling" is an estimate from file size, not a measured DRAM byte count | Partly | report.md:320 |
| 23 Startup | "Overhead is a fixed cost": the overhead grows by 25 to 34 ms with a real task | Partly | report.md:533-540 |
| 24 Prediction | No accuracy target, no baseline predictor, no dataset size | Partly | point "hold out whole task families" |
| 24 | Is SoCC 2025 "Interference" a real, citable paper? | Undefended | no reference in the source map |
| 25 Limits | Strong and honest. Why is it in the appendix rather than main? | Partly | it exists, but only on request |

---

## 3. Missing content the end goal needs

1. **A funding case.** Campaign size (capsules x inputs x 3 passes: timing, nsys, ncu x repeats), GPU-hours, analyst time, calendar time, owner, and a go/no-go gate after tests 1 and 2. Opportunity cost: the GB10 is the single M1 product host running the whole Compose stack (D35, design-package/README.md:48), so a quiet window means product downtime or a non-quiet memory system.
2. **The real AI4Research task mix** (W3): which capsules touch the GPU, for how long, and whether they declare `exclusive`.
3. **A predictor validation design** with baselines: no interference, a one-bit GPU-heavy label, nearest neighbour, and later a learned model. Add held-out families (plan:122 and slide 24 point at this but do not define it). State the accuracy the planner needs and the threshold that would stop the program.
4. **An interference model beyond pairs**: 3 or more concurrent jobs, and CPU-vs-GPU bandwidth contention on UMA (report.md:201).
5. **Agentic dynamics**: data-dependent run length, bursty remote calls, KV reuse, model swaps (report.md:215). Without these, records describe kernels, not agents.
6. **Record lifecycle**: invalidation on capsule version, image, driver or firmware change; RSI-generated children; cold start for an unprofiled capsule (what the planner does with "unknown").
7. **Schema landing point**: the exact future field (the run-plan "execution profile" seam, run-plan:645), its writer, and its forbidden uses. Per the explicit-field-definitions rule, each needs a meaning cell.
8. **Chip-design method** (W6): the controlled knobs on GB10 (clock and memory locks, power caps, MPS SM percentage), a sensitivity output format, simulator calibration, and comparison with existing agentic-workload characterization work.
9. **Routing quality axis**: a cost-only router rule is not a routing policy.
10. **Statistics**: intervals or at least min-max on every measured number; n=2 cells shown as x2.08 overstate precision.
11. **Energy per task**, which the report can compute (report.md:322) and chip designers care about. It is absent from the deck.

---

## 4. Factual and numeric errors

| # | Slide | Deck says | Correct value | Source |
|---|---|---|---|---|
| 1 | 7 | "One LLM of four gets 37% of the GPU ... not 25%" | Kernel-span share 37% includes switched-out time. Useful throughput share is 63.4/283.5 = 22% (also 3.5/15.8 ms = 22%) | report.md:312; chart-data `concurrency` |
| 2 | 7 and 9 | Solo "100% busy" (7) and "91% busy" (9) | Different metrics: kernel-trace span (100%) against device GPU busy (91%). Must be named | chart-data `timeline`; report.md:444, 454 |
| 3 | 8 | Source: "measured bytes per token" | Model file bytes x tok/s, so bytes per token = file size (4.69 GB, 9.04 GB). Ceilings 58 and 30 are right at 100% of the 273 GB/s spec; about 48 and 25 at the 5070 Ti's achieved 82% | report.md:320, 424-426 |
| 4 | 12, 23 | "+219 ms per GPU container start" | 219 ms is the median total; overhead is +216 ms | report.md:519 |
| 5 | 23 | "Overhead is a fixed cost: 339 vs 336 ms" | The overhead grows with a real task: GPU +216 to +245 ms, no-network +149 to +174 ms | report.md:533-540 |
| 6 | 5 | "Speech-to-text and NVENC stay within x1.02 to x1.12" | x0.98 to x1.12 (speech beside training x0.98, training beside speech x1.00) | report.md:404, 412 |
| 7 | 5 notes | "about 7 microsecond kernels" | Median decode kernel is 2.5 us (B.4). 7 us is the report's prose and one sample kernel (6.85 us). The source is inconsistent | report.md:101, 343, 444 |
| 8 | 21 | "Media engines ... stress memory without GPU busy" | NVENC alone: DRAM read 1%, SM 0%, busy 0%. Not supported by our data | report.md:464 |
| 9 | 22 | "Speech-to-text and NVENC: 1 to 3% on every counter" | 0 to 3% (NVENC 0% on SM, tensor, busy) | report.md:463-464 |
| 10 | 22 | Table row mixes phases unlabelled | DRAM column is decode; Tensor column is prefill (decode tensor is 0%) | report.md:420-427 |
| 11 | 6 | "2 to 22% switching loss" stated generally | Computed on DRAM read only. Other counters differ, for example SMs active LLM+LLM 21%, SM issue LLM+training 11%, DRAM write LLM+LLM negative (measured 1.6 > model 1.0) | report.md:318, 476-490 |
| 12 | 9 | "4 LLM processes still read busy" | No device utilization is reported for the 4-process run. For 2 LLMs, SMs active fell from 84 to 72 | report.md:486 |
| 13 | 6 | Batched curve to 1,417 tok/s shown without comment | Batch 8 (5.6 ms/token) is faster per token than batch 4 (6.5 ms). This is non-monotonic at n=2 and needs a check or a flag | report.md:392-393 |
| 14 | 12 | "NVIDIA device-wide signals: Nsight Systems, Nsight Compute" | Nsight Systems is a per-process timeline and Nsight Compute is per kernel (as slide 3 says). Device-wide is DCGM | deck.json:68-77 |
| 15 | 18 | Row 4 "Cold start ... on GB10", status "Done on discrete card" | On the GB10 it is missing | deck.json:708-710 |
| 16 | 16 | "Profiles feed existing planner fields" | Existing resource fields are copied from the declaration and admission, never from a plan. A predicted profile has no field yet (future seam) | run-plan:80, 149, 645; plan:133 |
| 17 | 26 | Source map | No URLs for Orion, NeuSight, HotCloud 2020, SoCC 2025, Accel-Sim, Chakra, Paper2Agent, HiPC 2023 (the plan has arxiv 2312.07220), CUDA UM guide, EKS add-on, ECS Managed Instances. SoCC 2025 could not be verified | deck.json:1086-1129 |
| 18 | 20 to 26 | Rendered page numbers 19b and 19c | Appendix numbering does not match slide order (cosmetic) | review/slide-21.png, slide-22.png |

Checked and correct: x2.08, x2.27, x1.16 (report.md:402-406); 258, 284, 614 tok/s and 8.9 vs 2.5 GiB (report.md:390-396); 3.5 and 15.8 ms (report.md:77); 37% plotted mean (chart-data 0.374); 28.5 GB/s pinned and 10 to 17 pageable (report.md:496-501); 64.4 s vs 5.3 s, 0.049/2.7/6.1 s (report.md:542-548); 2.8x at 16 containers (chart-data burst 422.8/151.7); 95% of ceiling (737/769.85 = 95.7%); planner totals 31.3 and 21.1; 32768 MB ceiling (run-plan:224); GB10 128 GB, 273 GB/s, 20 Arm cores (plan:20).
