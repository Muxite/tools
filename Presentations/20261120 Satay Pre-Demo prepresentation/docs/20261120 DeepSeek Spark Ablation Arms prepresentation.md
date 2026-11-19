# Ablation arms (DRAFT)

Names follow the rule that a CC is named for what it builds or sets, not for an action. The ontology and contract state the target and constraints. Each CC fills unspecified details with its own defaults, creates or modifies the part, and verifies before reporting done.

| Arm | Contents | What the comparison isolates |
|---|---|---|
| **A** | Stock as documented (see Baseline Source List) | The reference |
| **B** | A + **Prefill Configuration Tuner CC** output only (batch/microbatch, threads, residency budget). No engine code | What automated configuration alone buys |
| **C** | A + one **component builder CC** change only (first candidate: Expert Weight Cache Builder, if the cost breakdown shows repeated critical-path transfers) at A's configuration | What the engine change alone buys |
| **D** | A + B's configuration + C's code | Whether they combine, add or overlap |

**Reading the result.** C vs A is the engine-code effect. B vs A is the tuning effect. D vs max(B, C) shows interaction. If B accounts for nearly all of D, the demo claim is about automated configuration, not the component CC.

**Cells and order.** 4 arms × 2 predeclared inputs (coding, held-out) at 512-in/≤16-out first, ABBA fresh-process pairs, ~4–8 min per cell after build. The 4,096-in/16-out confirmation runs only for arms that pass the short screen. Each arm that builds code uses `factory.builder` for the immutable image, `factory.lab_client` for the paired run, and `factory.evidence` for the receipt. `factory.methodology_ablation` owns the design and attribution.

**Required per cell.** Source and image IDs, effective settings read back from the loader, activation markers (arm B: config receipt; C/D: feature-active marker), client TTFT, native prefill and decode, end-to-end, peak cgroup and headroom, exact generated IDs and stop reason, filesystem-cache state, raw receipts.

**Pass bars.** Priority is showing several CCs doing real, verified work. Improvement is wanted but not critical. Required: output exact, decode and memory within the agreed limits, no regression vs A, and a measured TTFT/prefill change reported honestly. 1.30× (stretch 1.50×) stays a target. A modest, attributed gain passes.

## Scaling to five builder CCs
Four arms fit one builder. With five, run the full factorial only if time allows. Otherwise:
1. **Stage ladder per CC**, labelled honestly: fixture → native CC execution → compile → runtime acceptance → hardware measurement. Each CC shows its inputs, applied diff, verification result and activation marker at whatever stage it has really reached. Do not present an earlier stage as a later one.
2. **Cumulative add on hardware** (A, A+1, A+1+2, ...) for the CCs that reach the machine, then **leave-one-out** from the full set for attribution. Arms B (Prefill Configuration Tuner) can sit at either end.
3. The Runtime Event Recorder Builder is the diagnostic: it supplies the coverage that lets the planner choose and explain the other four. Its overhead is reported, and it is off in timed cells.

| ★ | Builder CC | Component → subcomponent | Why it is one of the five | Evidence so far |
|---|---|---|---|---|
| ★1 | Runtime Event Recorder Builder | Generation runtime → Runtime event recording | Shows where memory-bound time goes and feeds the planner | Granite capture, 6,144 selections, exact capture-off/on parity |
| ★2 | Expert Weight Cache Builder | Weight residency → Expert weight cache | Core of running a model larger than memory: which expert bytes stay ready | Spark: 8× fewer acquisitions, but stock still faster on decode |
| ★3 | Weight Placement Planner Builder | Weight residency → Weight placement planner | Decides what lives where under one byte budget (16-block proposal = 51.94 GiB) | Calculator and tests only; no hardware arm returned |
| ★4 | Expert Demand Predictor Builder | Weight residency → Expert demand prediction | Early hints so reads finish before use | Satay Pregate smoke; J-OM13 Fill+Pregate 18.3% on the older Qwen run |
| ★5 | Batch Layout Mapper Builder | Generation runtime → Request and batch orchestration | Layout sets how often weights are re-read during prefill | `engine.prompt_batch_layout` 1.0.1 passed 14 single-slot lengths |
| later | Expert Row Dispatcher and Combiner Builder | Model execution → Expert computation and combination | Compute side; only if dispatch dominates | none yet |
| later | Sequence Memory builder | Sequence state → Sequence memory | Shares the capacity ledger with expert slots | none yet |

The selection is my judgement from the "big MoE on insufficient memory" goal and how mature each CC's evidence is. Swapping one is cheap. ★3 has the least hardware evidence, so it can be shown at the fixture or compile stage.

The remaining CCs (planner, requirements, builder, lab client, evidence, methodology) are the factory that makes the five work. RSI improves the CCs themselves, so the demo should show the CCs and the loop around them, not claim to be the CC-improvement system.

**Not run yet.** Nothing here has been measured. Which component CC fills arm C depends on the cost breakdown. If the repeated-transfer wait is small, arm C is replaced or dropped and the rejection is recorded.

## Quiet-run protocol
Benchmarks run only while the factory is idle: no concurrent builds, planner revisions, indexing or other lab jobs on the target. Record `ps`/load before and after each cell. Pause factory tasks before a measurement window and resume after.
