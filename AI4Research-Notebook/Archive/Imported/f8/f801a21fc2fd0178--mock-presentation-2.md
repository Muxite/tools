# Mock presentation 2: slides 1 to 14 (images only)

## 1. Script per slide

**Slide 1.** Today is an early exploration of GPU workload profiling for AI4Research. I will show what we measured, what we cannot see yet on the GB10, which is the DGX Spark, and where I think we should spend time next. One caveat first: we have no GB10 results yet. Everything measured so far comes from a different machine. My goal is to help us decide whether this work is worth doing at all.
Transition: Let me start with the idea in one picture.

**Slide 2.** The idea is to record each capsule alone on a quiet GPU, store that as a profile record, and look it up when the system is busy. Offline, the capsule gets a container image, a solo run, and a record. Online, a predictor, then the planner and scheduler, then parallel runs. Only the capability capsule is designed. Most boxes are proposed or hypothesis. The reason is that key GPU counters are device-wide, so we cannot split them per process on a busy GPU. The question today is whether this is worth our time.
Transition: First check whether AI4Research even uses the local GPU.

**Slide 3.** Most capsules call a fixed Codex CLI route to a remote model. They declare no GPU, so their wall time is remote wait. The builder runs experiment code in a workspace, and how much GPU that uses is unmeasured. Only research.benchmark declares an exclusive GPU device with a 3600-second wall budget. Later, local models might change this. So the likely M1 answer is that the bottleneck is remote Codex wait, which GPU profiling cannot predict. Test 0 is to trace one real run.
Transition: If we did profile, here is what the tools can and cannot see.

**Slide 4.** This table lists the tools and whether each can split its numbers per process when the GPU is shared. SM, tensor and DRAM counters cannot be split. They need the GPU alone. Process memory and cgroup data do split. Nsight kernel times split too, but they include time the GPU spent on other work. On the GB10, several of these, such as DCGM support, MIG and per-process utilisation, are marked preflight, meaning we have not checked yet.
Transition: The GB10 itself makes this harder.

**Slide 5.** Three layouts. On a discrete card like our RTX 5070 Ti test machine, the CPU and GPU have separate memory and copy over PCIe. CUDA unified memory migrates pages between them. On the GB10 there is one 128 GB pool shared by CPU, GPU and OS, at 273 GB/s. CPU work and GPU work then compete for the same bandwidth. And nvidia-smi reports memory usage as not supported there. Migration cost we have not measured.
Transition: Now what we did measure, on the discrete card.

**Slide 6.** This matrix shows how much each task slows when running beside another. LLM decode ran 2.08 times slower beside CNN training, with only two runs, and 2.27 times beside another LLM. CNN training slowed only 1.16 times. Speech-to-text and video encode stayed near 1.0. So the pair matters. Most cells are n equals 2, so these are rough. A toy planner case later asks whether a simple label is enough.
Transition: Then I ran four LLMs together.

**Slide 7.** One LLM alone keeps the GPU busy across the whole trace and gives 3.5 ms per token. As one of four, its busy share averages 37% and flickers between 0 and 100% every 5 ms, and it takes 15.8 ms per token. Each stream gets 22 to 26% of its solo throughput, 91% in total: 258 tokens per second against 284. So sharing is a loss, not a clean split. This is a discrete card; unified memory may differ.
Transition: Does batching avoid that loss?

**Slide 8.** Four separate processes gave 258 tokens per second and used 8.9 GiB. Batching four requests in one process gave 614 tokens per second and 2.5 GiB. That suggests a routing hypothesis: few models, batched requests. Two caveats on the slide: n equals 2, and batch 8 looks faster per token than batch 4, which needs a recheck. Cold load of a 7B model was 6.1 seconds from disk, 2.7 from RAM, 0.05 resident. Model quality is not measured.
Transition: Which of this survives on unified memory?

**Slide 9.** This table sorts findings by what carries over to the GB10. Two are expected to carry over: decode being bandwidth-bound, and batching beating separate processes. CPU work taking GPU bandwidth is likely the main new interference, and untested. Switching cost, model load, partial CPU offload and memory accounting are unknown. So nothing on this slide is measured on a GB10.
Transition: Does any of this change planning?

**Slide 10.** A toy fluid model: four nodes of 10 units each, two slots. Serial, which is M1 today, takes 40. Worst pairing 26.5, random order 22.9, and both a one-bit GPU-heavy label and a profile-aware planner take 21. So a one-bit label already matches the profile here, if each node's class is known. Profiles may earn their cost with many GPU-heavy classes, and for memory and routing. M1 runs one node at a time, so parallel nodes are outside M1.
Transition: Now how this would attach to the CC layer.

**Slide 11.** Each CC component gives profiling something, and profiling gives something back. The declaration supplies a profile key, the declaration hash, and claims to test: exclusive and the wall-time budget. The runner supplies join keys. The planner would get a predicted profile as a protected input. Host checks could compare declared against observed. RSI would re-profile each child. Owner ruling 9 currently forbids continuous CPU or GPU sampling.
Transition: And where the profile must not go.

**Slide 12.** Five existing fields are not places to put a prediction: declaration ext, needs and budget, library max_limits, inventory quantity, and planner output. The proposal is a new protected input beside resource inventory and plan policy: a versioned read-only profile store, a predictor, a protected profile input hashed at freeze, then the binder's resource feasibility. Sidecar README line 107 and owner ruling 9 limit profiling today, so a profile store needs an owner decision.
Transition: So where do we spend time?

**Slide 13.** Six candidate questions, cheapest first. One: how much of a real run is local GPU? Trace one run, no GPU window needed. Two: what can the GB10 show us? Probe the tools. Three: does CPU work slow GPU work in the shared pool? Then pairs, local models, and whether the schema can carry resource facts. I suggest starting with one and two, since they decide if the rest is worth doing. Open: owner, quiet-window rules, sidecar and capture rules.
Transition: One longer-term item.

**Slide 14.** This is much later. If we wanted to inform chip design for agentic systems, we would need controlled sweeps: working set, power cap and GPU clock, a CPU streaming job beside decode, and replay of real capsule traces. Decode being bandwidth-bound is already known. What would be new is the agent mix and the shared pool. Simulator fidelity on unified memory is unverified. I am not asking for a decision here.
Transition: That is the talk; the appendix has the rest.

## 2. Overclaims in my script, by slide

- Slide 2: "Most boxes are proposed or hypothesis" is fine. "We cannot split them per process" is stated by the slide but only supported by slide 4. Mild.
- Slide 3: "Their wall time is remote wait" is the slide's claim from declarations, not a measurement; the slide itself says Test 0 has not been run. My "likely M1 answer" is fine only because the slide says "likely".
- Slide 5: "CPU work and GPU work then compete" is stated as fact; slide 9 says untested.
- Slide 6: "So the pair matters" rests on n=2 and one LLM+LLM n=8; overclaim for CNN and speech cells.
- Slide 7: "sharing is a loss, not a clean split" holds only for a discrete card running four LLM processes.
- Slide 8: "That suggests a routing hypothesis" is the slide's word; I must not say batching is better in general. Quality unmeasured, n=2, and the batch-8 point is flagged suspect.
- Slide 9: "Expected to carry over" is a prediction, not evidence.
- Slide 10: "already matches profile-aware" holds only in a fluid toy model whose inputs are my own n=2 numbers.
- Slide 11 and 12: I describe components and rulings (owner ruling 9, README:107) that the slide cites but does not explain. [GAP: what ruling 9 says in full.]
- Slide 13: "they decide if the rest is worth doing" is an argument, not shown.
- Slide 14: "Decode being bandwidth-bound is already known" is cited only to a plan file and 87 to 96% of ceilings on a discrete card.

## 3. Where I got stuck

**Terms an audience that knows CCs but not GPU profiling cannot follow.** SM, tensor, DRAM counters; pmon; DCGM; NVML; MIG; MPS; Nsight Systems and Compute; PSI; cgroup v2; OCI digest; VRAM; LPDDR5x; unified memory; decode versus prefill; NVENC; "replay perturbs the run"; "span"; "duty cycle"; "fair share". Slide 4 is a wall of these with no one-line definition. "Quiet window" is used from slide 2 on and never defined (how long, who guarantees it).

**So-what jumps.**
- Slides 5 to 9 show contention and batching results, but slide 3 says the M1 bottleneck is remote Codex wait and GPU profiling cannot predict it. The talk's own M1 answer undercuts its middle half. The reader cannot tell why 4 slides of measurements precede the question that may make them moot.
- Slide 7 to 8: a routing recommendation (few models, batch) is drawn, but the Codex route is remote and "Later" local models are not scheduled.
- Slide 10 compares against "Serial (M1 today)", but parallel is outside M1, so the benefit is not available in M1.
- Slides 11 and 12 spend two slides on schema landing spots for a predictor that slide 2 labels HYPOTHESIS and slide 10 says a one-bit label can replace.
- Slide 13 asks nothing concrete: no owner, no time, no decision to make today.

**Contradictions and number mismatches.**
- Slide 6 title and slide 2 headline use 2.08 (CNN, n=2) while the largest cell is 2.27 (LLM+LLM, n=8); slide 6 bullet 4 says n=2 except LLM+LLM, so the "n=2" headline sits beside an n=8 figure in the same bullet. Slide 2's "two big GPU jobs together" cites only the n=2 case.
- Slide 6: 2.27 slowdown between two LLMs vs slide 7: one of four LLMs takes 15.8 vs 3.5 ms (4.5 times). Consistent in direction, but pair figures and four-way figures use different framings (slowdown vs share) with no bridge.
- Slide 8: at 1 request, separate gives 284 tok/s and batched 274; unexplained difference at identical load. Batch 8 gives 1,417 against 614 at batch 4 (super-linear), flagged "recheck" but still plotted. Separate processes have no point at 8.
- Slide 9: "2 to 22% lost" process switching; slide 7 shows 9% total loss and 74 to 78% per stream. Unclear which loss that refers to.
- Slide 9: "157 to 22 tok/s at 20 of 28 layers" appears nowhere else. Never introduced.
- Slide 9 says "Nothing here is measured on a GB10" yet slide 5 shows GB10 specs (273 GB/s) and "Not Supported" from NVIDIA pages; sources are not distinguished visually from measurements.
- Slide 1 says "what we measured" with no results; slide 2 footer says the imported report's raw traces "we have not reviewed" while slide footers say "our measurements". Our or imported? Needs one honest label.
- Slide 11 left column "No memory or GPU quantity field in the declaration" vs slide 3 "memory_mb" and "gpu_device exclusive" declared. Needs a sentence on which exists.

**Cut, merge, reorder.**
- Move slide 3 (is the GPU even used) to immediately after slide 2, or before it. It is already there, but then slides 4 to 10 should be demoted to backup, or framed as "if the answer to slide 3 is yes".
- Merge slides 4 and 9 into one "what we can and cannot see" slide; slide 4 can drop to appendix.
- Merge 6 and 7 (both contention evidence).
- Slide 8 belongs in backup unless local models are on the roadmap.
- Slides 11 and 12 merge into one.
- Slide 14 is out of scope for a decision talk; backup.
- Slide 13 should be the second slide, not the last.

## 4. The story in five sentences

1. AI4Research could record each capsule's GPU behaviour alone and use it to pair jobs when busy. 2. Measurements on a different machine (RTX 5070 Ti, mostly n=2, unaudited) show LLM decode slows about 2x beside heavy GPU jobs, and batching beats separate processes. 3. The GB10's shared memory pool may change these results, and none of it is measured there. 4. In M1 the work is serial and mostly remote Codex wait, and a one-bit label matches a profile in a toy case, so the payoff is unclear. 5. The talk suggests tracing one real run and probing the GB10 tools first, but it is not plain who should do this or what we decide today.

The walk-away decision is weakly stated: "start with questions 1 and 2" appears only on slide 13, and the deck's own slide 3 and slide 10 already lean toward "probably not worth it for M1".

## 5. Verdict

Not comfortable presenting as is. It is honest about its limits, but the order buries the decision, and the middle is heavy with jargon and discrete-card numbers the audience cannot act on.

Three changes that matter most:
1. Lead with the decision: put the question list (slide 13) and the "likely M1 answer" (slide 3) right after slide 2, state a concrete ask (who traces one run, by when), and demote slides 4 to 10 to evidence for "if yes".
2. Define the GPU terms (SM/DRAM counters, DCGM, MIG, quiet window, span, unified memory) in one glossary line each, and cut slide 4 to the three rows that matter; label every number as measured-here, imported, or vendor-documented.
3. Fix the number issues: reconcile the 2.08 headline with n=2 and the 2.27 n=8, explain or remove the batch-8 and 1-request anomalies and the 157-to-22 figure, and say clearly that slide 10's benefit is not available in serial M1.
