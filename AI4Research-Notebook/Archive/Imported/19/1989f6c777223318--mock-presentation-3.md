# Mock presentation 3: solo rehearsal from slide images only

Slides viewed: 1 to 30 (PNG only). Backup slides were skimmed, not rehearsed.

## 1. Script, main slides 1 to 13

**Slide 1.** I am going to give you an early look at GPU workload profiling for AI4Research. This is exploratory. I will tell you what we measured, what we cannot see yet on the GB10, the DGX Spark, and where I think we should spend time next. I want to be clear up front: we have no GB10 results yet. Everything numeric you will see today comes from other sources, and I will say which on each slide.
*Transition: Let me give you the whole answer first, then the detail.*

**Slide 2.** Six questions, six short answers. Does GPU contention matter in M1? Maybe not much, because capsules call a remote model, so remote wait likely dominates. One traced run would tell us. Where could it matter later? Local models behind the router, experiment code, the benchmark capsule, parallel nodes. On a different machine, an RTX 5070 Ti, heavy jobs slowed LLM decode about 2x, and batching beat separate copies. On the GB10 we know nothing yet. I will ask you to approve two first steps, with an owner and a date, neither of which is set.
*Transition: First, how much does AI4Research touch the local GPU at all?*

**Slide 3.** This is from the design package, not from measurement. Most capsules run on the fixed Codex CLI route, so the model is remote and no GPU is declared. The builder runs experiment code, and how much GPU that uses depends on the experiment: unmeasured. The benchmark capsule declares an exclusive GPU for 3600 seconds, so it is never paired by declaration. My likely M1 answer is that remote Codex wait is the bottleneck, which GPU profiling cannot predict.
*Transition: If I am wrong, or once we go local, here is what a profiling design would look like.*

**Slide 4.** Suppose the GPU does matter. The proposal is to run each capsule alone on the GB10 in a quiet window, meaning nothing else uses the GPU, because the key counters are device-wide. We store the result as a versioned profile record, and a planner could look it up when the system is busy. Only the capability capsule is designed. The container image, solo run and record are proposed. The predictor is a hypothesis, scheduling is not scheduled, and M1 runs serially. Nothing on the GB10 has been run.
*Transition: Why would pairing matter at all? Here is the one measurement we have.*

**Slide 5.** This is a pair table from our other machine, the RTX 5070 Ti, imported and unaudited. Read a row as: this task, slowed by the task in the column. LLM decode ran 2.08 times slower beside CNN training, and 2.27 times slower beside another LLM. CNN training slowed only 1.16 times beside LLM decode. Speech-to-text and video encode stayed near 1. Each pair is n=2, except LLM plus LLM at n=8. So pair choice matters, in this data.
*Transition: Next, what happens if you simply run several LLMs at once.*

**Slide 6.** Same machine. One LLM alone gets 3.5 milliseconds per token. As one of four, it takes 15.8 milliseconds. Its trace span averages 37%, flickering from 0 to 100% every 5 milliseconds, but useful throughput is only 22 to 26% of solo per stream. Total output for four processes is 258 tokens per second against 284 for one. So four together made 91% of one alone. That is a loss, not a split. The footnote says the cost may differ on unified memory.
*Transition: Given that, one hypothesis for routing is few models and batched requests.*

**Slide 7.** This is a routing hypothesis, still on the discrete card, with a 3-billion-parameter model. Four separate processes gave 258 tokens per second and used 8.9 GiB. Batching four requests in one process gave 614 tokens per second and used 2.5 GiB. One request alone is about the same either way. Batch 8 looks faster per token than batch 4, but that is n=2 and needs a recheck. Cold load of a 7B model: 6.1 seconds from disk, 2.7 from RAM, 0.05 resident. Model quality is not measured. [GAP: how many local models the router design actually expects.]
*Transition: Now the GB10, where the memory picture is different.*

**Slide 8.** Panel A is our card: separate GPU memory over PCIe. Panel B is CUDA unified memory in general, where pages migrate, and we have not measured migration cost. Panel C is the GB10 per NVIDIA documentation: 20 Arm cores and a Blackwell GPU share one 128 GB LPDDR5x pool at 273 GB/s. CPU work and GPU work compete for that bandwidth. NVIDIA's known-issues page says nvidia-smi Memory-Usage is Not Supported on this machine.
*Transition: So what can we still observe, and what cannot be separated per process?*

**Slide 9.** I will go by tool. nvidia-smi gives per-process memory, but not on the GB10 per the known-issues page. DCGM profiling counters are whole-device, they conflict with Nsight, and whether DCGM works on the GB10 is unknown. Nsight gives per-kernel times, but those include time spent waiting on others, and it perturbs the run. cgroups give host CPU, memory and I/O only. So SM, tensor and DRAM counters need the GPU alone. [GAP: what "GB10 unknown" means for DCGM, i.e. whether anyone has tried it.]
*Transition: Which of my discrete-card findings might not survive on the GB10?*

**Slide 10.** Two findings I expect to carry over: decode is bandwidth-bound, and batching beats separate processes, though with a lower ceiling shared with the CPU. One new interference is likely: CPU work taking GPU bandwidth, but untested. Process switching cost, model load, partial CPU offload and memory accounting are all unknown on the GB10. The status column is my expectation, not a measurement. Nothing on this slide is measured on a GB10. [GAP: what "2 to 22% of GPU work lost" means in plain terms.]
*Transition: Does any of this change what a planner would do? I built a toy case.*

**Slide 11.** A fluid-model toy: two slots, four nodes of 10 units each. Serial, as M1 does today, takes 40. Worst pairing 26.5, random greedy 22.9. A simple one-bit label, never put two GPU-heavy nodes together, gives 21.0, the same as profile-aware. This assumes each node's class is known. It uses our n=2 slowdowns. So profiles earn their cost only with many GPU-heavy classes, and for memory and routing. In serial M1 there is no benefit. [GAP: what the "fluid model" assumes.]
*Transition: Now, how does this connect to the capsule layer you already know?*

**Slide 12.** Left column: what the CC layer gives profiling. A profile key from the declaration hash, join keys from the runner, admission, planner and binder, host checks, and the RSI workbench. Right column: what profiling would give back. Evidence for exclusive and wall_s, a separate profile store, measured peaks informing memory_mb, a predicted profile as a protected planner input, and re-profiling each RSI child. Owner ruling 9 currently says no continuous CPU or GPU sampling. [GAP: how a profile store squares with ruling 9.]
*Transition: So where would I spend the time?*

**Slide 13.** Questions in order of cost, not importance. One: trace one real run, no GPU window; if local GPU share is small, drop pairing. Two: probe what the GB10 shows: DCGM, Nsight, MIG, cgroups. Three: does CPU work slow GPU work in the shared pool. Four to six: solo profiles versus pairs, local model count, and whether the CC schema can carry resource facts. Decision for this meeting: do questions 1 and 2, and name who and by when. That is not set yet.
*Transition: That is the main talk; the appendix holds the detail.*

## 2. Overclaim check

- Slide 2: "heavy GPU jobs slowed LLM decode about 2x" generalises from two partners (CNN training, another LLM) on one card. Mild overclaim.
- Slide 5 title and my script: "Heavy GPU jobs" plural; sample is 4 task families, n=2 per pair. The slide's "long kernels hold the GPU" is an explanation the slide does not show.
- Slide 5: "Pair choice matters" is supported only for LLM decode as victim; CNN training slowed only 1.16.
- Slide 6: "A loss, not a split" is supported for four identical LLM processes only.
- Slide 7: the title says "Routing hypothesis"; the slide shows no routing evidence, only batching on a 3B model. Cold-load numbers are for 7B, mixed in with a 3B chart.
- Slide 8: the title "dashboards go blind" is stronger than the body, which only says one field (Memory-Usage) is unsupported.
- Slide 9: the title "most else can" is not shown for the GB10, since DCGM is listed as "GB10 unknown".
- Slide 10: "Expected to carry over" and "Likely the main new interference" are guesses; they read as findings in a table.
- Slide 11: "a simple label already finds the best pairing" is a toy with four known classes, so the tie is partly by construction. It also hides that most of the gain over serial comes from running in parallel, not from pairing.
- Slide 4: the "Why it matters" box cites x2.08 as the motivation, while slide 3 says M1 probably has no local LLM contending. The motivation is conditional.

## 3. Where I got stuck

**Terms the audience cannot follow without GPU background.**
- Decode, tok/s, kernel, trace span (slide 6 defines it in one sentence), fair share, GiB vs GB, LPDDR5x, unified memory.
- SM, MIG, pmon, DCGM, Nsight, cgroups (defined only on slide 9, after use on slide 2).
- NVENC and NVDEC (never defined on the main slides).
- "Quiet window" (defined on slides 2 and 9, but used on slide 4 first in the diagram).
- "One-bit label" and "fluid model" (slide 11).
- "Test 0" (slide 3) is never defined again; slide 13 numbers the questions 1 to 6.
- "Self-tests run the pinned version (quiet host not stated)" and "poc_workspace" (slides 12 and 3).
- File:line references such as run-plan.md:645 mean nothing in the room.

**"So what?" jumps.**
- Slide 4 title says "If yes", but slide 3 says the answer is likely no. The audience must hold a conditional through slides 4 to 12, which is 9 of 13 slides.
- Slide 5 and 6 results are about LLM decode and CNN training. No slide says which M1 or later capsule is an LLM decode or a training job.
- Slide 7 is a "routing hypothesis" without a routing claim.
- Slide 9 to 10 to 11 do not lead to a decision. Slide 11 argues profiles are not needed for pairing, and slide 4 spends its whole diagram on profiles and a predictor.

**Contradictions and number mismatches.**
- Slide 9 says nvidia-smi gives per-process memory ("Memory yes"), and the Limit column says GB10 does not support it. Both are true but read as a contradiction.
- Slide 6: trace span 37% is above the 25% fair share, yet useful throughput is 22 to 26%. The chart's y-axis ("GPU busy") therefore shows an inflated measure. The takeaway sits in the bullets.
- Slide 2 says x2.08 n=2 and x2.27 n=8; the footer says n=2 to 12. Slide 5 says "n=2 per pair except LLM+LLM", which is consistent, but the 12 is not explained on main slides.
- Slide 12 right column is cut off on the first row ("The declaration has...").
- Slide 12 says owner ruling 9 forbids continuous sampling while slide 4 proposes profiling; reconciled only in the appendix.
- Slide 2 says "Four LLM processes together made less than one" and slide 6 says 91%; consistent, but the 91% is 258 vs 284 and the footnote says 63.4 of 283.5 per stream, an extra number that does not match the 22 to 26% range on first read.

**Source clarity per number.**
- Slides 2, 5, 6, 7, 10 footers: measured on another machine, imported, unaudited. Clear.
- Slide 3: design package; clear.
- Slide 8: NVIDIA documentation for GB10; PCIe copy speeds are ours. Mixed in one slide, and the footer is truncated.
- Slide 11: a script (planner_baselines.py) fed with our n=2 slowdowns; the audience cannot tell how much is assumption.
- Slide 10: the "On the GB10" column mixes vendor docs and speculation; the footer says "nothing here is measured on a GB10", which helps.

**Cut, merge, reorder.**
- Merge slides 5 and 6 (both "measured, contention"); the 91% result is the stronger one.
- Merge slides 8 and 9, then keep slide 10 as the single "what changes on GB10" page.
- Move slide 3 before slide 2 or fold it in; the whole talk hinges on it.
- Move slide 12 later, or to the appendix with a one-line summary, unless the CC owners are the decision-makers (slide 13, question 6 says they are).
- Slide 7: drop or move to the appendix; it is a router design input, not a profiling input.

## 4. The story in five sentences

1. AI4Research's M1 probably uses little local GPU because capsules call a remote Codex model, so remote wait likely dominates.
2. If local GPU use grows (local models, experiments, parallel nodes), data from a different machine shows that pairing and batching matter.
3. The GB10 shares one memory pool between CPU and GPU, so those results may not carry over, and the standard tools may not show per-process GPU memory.
4. A toy case suggests a simple one-bit label may find the best pairing without profiles, so profiles earn their cost mainly for memory and routing.
5. The cheapest next steps are to trace one real run and to probe what the GB10 can show.

The story is mostly clear, but sentence 4 sits awkwardly against the long profile design on slides 4 and 12.

**What the audience is asked to decide.** Do steps 1 and 2, and name who does them and by when. That is clear in wording, but it is not a real decision yet: owner and date are marked "not set". Slide 13 then adds "also open" items (quiet-window rules, sidecar and capture rules) without saying whether they are asks. Slide 12's owners (declaration, planner, sidecar) are also implied decision-makers, and no slide says so. I would state the ask as: "agree that someone owns the trace and the probe by a date, today".

## 5. Verdict

I would not present this as is. It is honest about what is measured where, but a listener finishes the talk unsure why they were given nine slides of conditional design when slide 3 says the likely answer is "no".

Three changes that matter most:
1. Restructure around the likely answer. Open with slide 3's finding, then present the GPU material explicitly as "if this changes", and cut it down (merge 5+6, 8+9; move 7 and 12 to appendix).
2. Make the ask real. Put a named owner and date on steps 1 and 2 before the meeting, or say the ask is "who volunteers". Remove the competing "also open" items from the decision line.
3. Define terms and fix slide 12. Add a glossary line for decode, kernel, NVENC, DCGM, Nsight, one-bit label and Test 0 (or drop them), fix the clipped text, and explain how profiling fits owner ruling 9.

Scores out of 10:
- Clarity: 6 (good source labels and hedging, but jargon, dense tables and a conditional structure).
- Honesty: 8 (consistent "other machine, unaudited, no GB10 results" tagging; a few titles and the toy case read stronger than their bodies).
- Usefulness for deciding where to spend time: 5 (the ask is right but unowned, and little of the deck bears on it).
