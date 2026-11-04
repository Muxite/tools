# Mock presentation: slides only

Written from the PNGs alone. Square brackets marked GAP are facts I would need and the slides do not give.

## Script

### Slide 1. Workload profiling for AI4Research

Thanks for coming. This is an early exploration of workload profiling for AI4Research. I want to be clear about what it is. It is not a funding pitch and not a result. The footer says there are no GB10 results yet, and I will keep coming back to that. I will show you what we measured on a different machine, what we cannot see yet on the GB10, and then a list of questions so we can decide together where to spend time next. [GAP: what AI4Research is in one sentence, and what a Capability Capsule is. Slide 1 defines neither.]

Transition: First, the idea in one picture.

### Slide 2. The idea: record each capsule alone, look it up when busy

The idea is two phases. Offline, in quiet windows on the GB10, we take a capsule, build its container image, run it alone on the GPU, and keep a profile record. Online, on the busy system, a predictor looks up similar records, a planner picks capsules and pairings, and parallel runs follow. The status tags matter: only the capsule is designed. Everything else is proposed, a hypothesis, or not scheduled, and M1 is serial. The reason for going offline is that key GPU counters are device-wide. The one number I have: an LLM decode ran 2.1x slower beside CNN training. That was on one x86 machine with an RTX 5070 Ti. [GAP: what M1 is, and what "pairing" means here.]

Transition: So where in AI4Research could this even matter?

### Slide 3. Where GPU contention can occur in AI4Research

This table asks which capsules touch a local GPU at all. Most of them, from intent through verifier, run a fixed Codex CLI route against a remote model. They declare no GPU, so locally there is no contention. Their wall time is remote waiting. The builder runs experiment code in its workspace, and how much GPU that uses is unmeasured. Only research.benchmark declares an exclusive GPU, and it is never paired. Local models and parallel branches come later. So the likely M1 answer is that the bottleneck is remote Codex wait, which GPU profiling cannot predict. Test 0 is to trace one real run. [GAP: what share of a real run each class takes.]

Transition: Suppose the GPU does matter. What can we observe?

### Slide 4. Device counters cannot be split; most else can

This is the tool survey. The question for each tool is whether it can split its numbers per process when several processes share the GPU. For nvidia-smi and NVML, memory per process yes, but not kernel detail, and on the GB10 memory usage is not supported. DCGM profiling is whole-device: SM, tensor and DRAM counters cannot be split. Nsight Systems can split, but kernel durations include time the GPU spent on others. Nsight Compute replay perturbs the run. cgroups split per container but cover host resources only. So the SM, tensor and DRAM counters need the GPU alone, which is why slide 2 profiles in quiet windows. [GAP: what SM, pmon and PSI mean; I would not define them aloud.]

Transition: And on the GB10 specifically, there is an extra problem.

### Slide 5. On GB10 the GPU shares one pool and dashboards go blind

Three memory layouts. A is the discrete card we tested: separate CPU and GPU memory, with a PCIe link. B is CUDA unified memory: one address space, pages migrate. C is the GB10: 20 Arm cores and a Blackwell GPU on one 128 GB LPDDR5x pool, 273 GB/s shared by CPU, GPU and OS. There is no PCIe copy, but CPU work and GPU work fight for the same bandwidth. And nvidia-smi reports Memory-Usage as Not Supported. So the VRAM-used number we get on our test card does not exist on the target. Migration cost in B is not measured by us. [GAP: why panel B is included, since the GB10 is panel C.]

Transition: Now our measurements, all on the discrete card.

### Slide 6. LLM decode ran x2.08 slower beside CNN training (n=2)

This matrix shows how much the row task slows when it runs beside the column task. LLM decode beside CNN training slows 2.08x, with a range of 1.7 to 2.4 over two runs. Beside another LLM, 2.27x, from eight runs. CNN training itself slows only 1.16x. Speech-to-text and NVENC encode stay between 0.98 and 1.12. So the pair matters: two GPU-heavy jobs hurt, a light job does not. The n is two per pair, and the grey cells were not run. I would not quote a single number as a constant. [GAP: why the title says x2.08 while slide 2 says 2.1x; same number, different rounding.]

Transition: Why is the loss so large with four LLMs? Look at the timeline.

### Slide 7. Four LLMs together make 91% of one alone

Top: one LLM alone has the GPU 100% busy, 3.5 ms per token. Bottom: the same LLM as one of four. Its busy trace flickers between 0 and 100% every 5 ms, averages 37%, and each token takes 15.8 ms. Fair share would be 25%. The span includes time switched out, so useful throughput per stream is 22 to 26% of solo, and about 91% in total. Total output is 258 tokens per second against 284 for one. That is a loss, not a split. [GAP: how 91% reconciles with the two other 91% figures on the slide; the bullet says solo 3B decode reads 91% as a different metric, and I cannot explain why a different metric matters.]

Transition: If separate processes waste the GPU, the obvious alternative is batching.

### Slide 8. Routing hypothesis: few models, batched requests

Left: GPU memory. Four separate processes of a 3B model use 8.9 GiB. Batching the same requests in one process stays at 2.5 GiB. Right: throughput. Four separate processes give 258 tokens per second. Batched in one process gives 614, and 1,417 at eight. So the hypothesis is to keep few local models resident and batch requests. Caveats on the slide: n is two, batch 8 being faster per token than batch 4 needs a recheck, and model quality is not measured. On the GB10 the weights come from the shared pool. [GAP: what "routing" and "the router" are. Also why cold load is 6.1 s here; slide 9 says 2.7 s for what looks like the same measurement.]

Transition: But everything so far is a discrete card. What may change?

### Slide 9. What may change on unified memory

This is the honest slide. Seven findings from the discrete card, and what we expect on the GB10. Two are expected to carry over: decode is bandwidth-bound, and batching beats separate processes. One is likely the main new interference: CPU work taking GPU bandwidth, untested. The other four are unknown: process switching cost, model load, partial CPU offload, and memory accounting under cgroups. Nothing on this slide is measured on a GB10. So the measurements I just showed are suggestive for the carry-over rows and silent on the rest. [GAP: why decode being bandwidth-bound is expected to carry over; the slide only says "ceiling lower".]

Transition: Suppose pairing does matter. How much could a planner gain?

### Slide 10. Toy case: pairing 21.0 vs 26.5 worst; a label finds it

This is a toy model, not a measurement. Four nodes of ten time units each, two slots. Serial, which is M1 today, takes 40. Worst pairing 26.5, random order 22.9, and both a one-bit label, no two GPU-heavy together, and a profile-aware planner reach 21.0. So a simple label already matches a profile, if each node's class is known. Profiles earn their cost with many GPU-heavy classes, and for memory and routing. M1 runs one node at a time anyway. [GAP: what the pair slowdowns in the model are drawn from, and what "one-bit label" is declared by.]

Transition: How does this connect to the capsule layer?

### Slide 11. The CC layer and profiling feed each other

Six rows, each pairing something the capsule layer gives profiling with what profiling gives back. The declaration gives a profile key, declaration_sha256, and two claims to test: exclusive and wall_s. The runner gives join keys. Admission gives a self-test and a hand-set memory_mb ceiling, and measured peaks could inform it. The planner takes a predicted profile as a protected input. Host checks compare declared against observed. The RSI workbench re-profiles each child. Owner ruling 9 says no continuous CPU or GPU sampling today. [GAP: what RSI, binder, admission, host checks and owner ruling 9 are. This slide is unintelligible without them.]

Transition: Given all that, where may a profile live, and where not?

### Slide 12. Where a profile attaches, and where it must not

Five existing fields are marked "not a landing spot": the declaration extension, needs and budget, library max_limits, inventory quantity and planner output. The reasons are on the cards. A prediction would be ignored, or would be protected data that RSI cannot edit, or would turn a measured fact into a policy value. The proposed landing is a new protected input beside resource_inventory and plan_policy: profile store, predictor, profile input hashed at freeze, then the binder. The bottom banner says the sidecar README and owner ruling 9 limit profiling today, so this needs an owner decision. [GAP: what freeze, hashed at freeze, resource_feasibility and sidecar mean.]

Transition: Now to the decision. What do we do first?

### Slide 13. Candidate questions, cheapest first

Six questions, ordered by cost. First: how much of a real run is local GPU? Trace one real run, no GPU window needed. If small, drop pairing and keep routing and experiments. Second: what can the GB10 show us? Probe DCGM, Nsight, MIG and cgroups. Third: does CPU work slow GPU work in the shared pool? Fourth: do solo profiles say anything about pairs, against the label. Fifth: how many local models. Sixth: can the CC schema carry resource facts, which needs owner decisions. Not decided: who owns this, when a quiet window is allowed on the single product host, and what the sidecar permits. [GAP: what we ask the audience to choose or commit.]

Transition: One last slide, for completeness.

### Slide 14. Chip questions: what would be needed

These are questions for a chip team, marked much later. How much does bandwidth matter, how much compute, does CPU work take GPU bandwidth, and what do agent workloads look like. Each needs a controlled change, such as working-set sweeps, power caps, or replaying capsule traces. The output would be slopes, slowdown curves, duty cycles. Decode being bandwidth-bound is known already. What would be new is the agent mix and the shared pool. A simulator would need calibration, and its fidelity on unified memory is unverified. [GAP: who the chip team is, why it is in this talk, and whether I am asking anything of them.]

Transition: That is the main talk; backup follows if needed.

## Where I got stuck

### (a) Terms I could not explain from the slides

- AI4Research, Capability Capsule / CC, M1, "M1: serial", Test 0, "pairing".
- GB10 vs DGX Spark (I assume same machine; never stated). "Quiet window", "solo profile", "profile record".
- OCI digest, declaration_sha256, "declared needs, pinned version".
- Planner, binder, predictor, scheduler (slide 2 shows Predictor and Planner + scheduler; slide 11 says Planner + binder; slide 12 says Predictor then Binder), resource_feasibility, resource_needs, exclusive, wall_s, memory_mb, max_limits, resource_inventory, plan_policy, "freeze".
- Admission, library, scorecard, RSI workbench, RSI child, host checks (not the verifier CC), sidecar, owner ruling 9, D35, "protected input".
- Router / routing (slide 8 and 13) versus "routing" in the planner sense.
- Codex CLI route, POC code / poc_workspace, research.builder, research.benchmark.
- pmon, PSI, MIG, MPS, SM, NVENC, NVDEC, DCGM, NVML. Not defined on the main slides.
- "Trace span", "fair share", "device busy" (slide 7). "Fluid model" (slide 10). "One-bit label".
- "Paper2Agent" (backup only).

### (b) Where a listener asks "so what?" or "why does that follow?"

- Slide 3: the likely M1 answer is that remote wait dominates and GPU profiling cannot help. Then why is this deck about GPU profiling? It undercuts itself and never resolves.
- Slide 4 to slide 2: why must profiling be offline and solo? It follows from device-wide counters, but the audience is never told what decision the counters are needed for.
- Slide 6 and 7: contention is real on a discrete card. So what for the GB10? Slide 9 says unknown.
- Slide 7: "91% total, a loss not a split" does not state what a planner should do about it.
- Slide 8: batching beats separate processes. Why is that a routing hypothesis, and what does it ask of the router? Quality is unmeasured, so few models may be worse.
- Slide 10: the toy shows a label equals a profile. That argues against the deck's own proposal (slide 2). The deck does not say whether it recommends profiles or the label.
- Slide 10 uses the worst case of my own measured slowdowns in a toy model; the gain depends entirely on assumed numbers.
- Slide 12: why is a new protected input the right landing? Who asked for one?
- Slide 13: no recommendation of which question to pick. "Cheapest first" is a sort order, not a decision.
- Slide 14: why is a chip-team slide in a design discussion?

### (c) Contradictions and overlaps

- Slide 2 says 2.1x; slide 6 says x2.08 with range x1.7 to x2.4; slide 10 uses 1.7 to 2.4 for whiskers. Same number three ways.
- Slide 2 "Predictor" is a hypothesis and "Planner + scheduler" is not scheduled; slide 11 treats the planner and binder as existing seams (run-plan.md:645). Status is unclear.
- Slide 3 says a pairing case is "the case for this deck" but also that most capsules have no local GPU. Slide 10 says M1 is serial. Three slides undercut the premise.
- Slide 8 cold load 6.1 s vs 0.05 s resident; slide 9 says 2.7 s vs 0.05 s. The footnote on slide 8 says 7B, but the chart is 3B. Appendix slide 26 explains 2.7 (RAM) and 6.1 (disk); the main slides do not.
- Slide 7 title says 91% and the final bullet says solo 3B decode reads 91% device busy. Two different 91s.
- Slides 3, 11, 12 and 13 all repeat the same "does the schema carry resource facts" point.
- Slides 5 and 9 overlap (unified memory differences); slide 4 and 5 overlap on "Not Supported".
- Slide 9 row "Batching beats separate processes" repeats slide 8. Slide 14 "decode is bandwidth-bound" repeats slide 9.
- Slide 11 says no memory or GPU quantity field in the declaration. Slide 3 says "GPU declared: gpu_device exclusive". Probably consistent, but unclear.

### (d) Numbers I could not source or interpret

- "x2.08" vs "x2.1" (see above). n=2 per pair but the title still states two decimals.
- 91%, 37%, 25%, 22 to 26% (slide 7): derivation not shown. 63.4 of 283.5 tok/s appears only in the footer.
- 258 vs 284 vs 274 vs 250 (slide 8): the 1-request values differ (284 on the orange line, 274 on the green). Why?
- 614 and 1,417 tok/s: batch 8 is more than double batch 4. The slide says recheck.
- 273 GB/s: a GB10 spec or measured? Slide 5 says 273 shared; appendix says "spec". 28.5 and 10-17 GB/s PCIe: n=2 to 12.
- 21.0, 26.5, 22.9, 40.0 on slide 10: units are "time to finish four nodes of 10", so time units, not seconds.
- 87 to 96% of ceilings, 2 to 22% switching loss, 157 to 22 tok/s: appear without context on slide 9.
- 5 warm-ups, 7 paired rounds (slide 11): source unclear.
- "n=2 to 12" in every footer: which n applies to which number?
- "unaudited" in every footer: undefined.

### (e) Cut, merge, reorder

- Reorder: slide 3 (where it applies) and its conclusion should come after the measurements, or the talk should open with the question "how much is GPU at all?" The talk currently spends slides 4 to 9 building a case that slide 3 says may not matter.
- Merge slides 5 and 9. Both are "GB10 differs from the test card". Place the shared-pool diagram beside the carry-over table.
- Merge slides 6 and 7 into a single contention story, or cut slide 7's timeline detail to backup (appendix 17 repeats the batching chart already).
- Slide 8 duplicates appendix 17's right panel; drop one.
- Slides 11 and 12 are an architecture review for people who know the design package. For a mixed audience, cut one or push to backup. They are the least readable slides.
- Slide 14 should be cut or moved to backup. It answers nobody's question here.
- Add a decision slide at the end: what we ask the group to pick (slide 13 gives a list but no ask).
- Slide 1 needs a one-line definition of the system; I would add a "what is AI4Research and what is M1" slide before slide 2.

## The story in five sentences

I believe the talk argues that GPU contention between capsules is real on a discrete card, that a plan of solo offline profiles could predict it, and that this is mostly unproven on the GB10. It also argues that in M1 the cost may be remote Codex wait rather than local GPU, so the cheapest first step is to trace a real run. It shows a toy case where a one-bit label does as well as a full profile, which weakens the case for the profiling system on slide 2. It then lists six questions ordered by cost. The decision it asks for appears to be which of those questions to work on first and who owns the work, but the deck never states a recommendation, so I cannot tell what is being asked.

## Backup slides

PNG index 16 to 29 corresponds to footer labels 15a to 15n.

- Slide 2 (idea): 19 (quiet-window run), 20 (three linked records), 21 (how a predictor would be tested).
- Slide 3 (where it applies): 28 (what the evidence shows and does not).
- Slide 4 (tools): 16 (AWS vs DGX Spark), 22 (vendor practices), 23 (six GPU resources), 26 (clouds collect device metrics).
- Slide 5 (shared pool): 18 (decode bandwidth bound at GB10 spec), 28.
- Slides 6 and 7 (contention): 17 (time-split model explains, does not predict), 28.
- Slide 8 (batching, cold load): 17 (right panel repeats the chart), 25 (startup, 64 s vs 5 s, 6.1 s from disk).
- Slide 9 (unified memory): 18, 24 (decode memory-bound table), 28.
- Slide 10 (toy case): 21 (baselines B0 to B2, stop rule).
- Slides 11 and 12: 20 (invalidation, unprofiled capsule), 19.
- Slide 14: 27 (prior work), 18.
- Source challenges anywhere: 29 (source map).
- Most likely needed live: 28, on slides 6, 7 or 9, when someone asks whether this shows anything about the GB10.
