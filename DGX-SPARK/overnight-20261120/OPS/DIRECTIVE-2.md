# Directive 2 from the owner (2026-11-20 ~07:15Z), relayed by the orchestrator

1. **Roles.** The top-level Codex is an ORCHESTRATOR. It runs on gpt-6.2-astra, spawns gpt-6.2-sol subagents for bounded work, and steers. It does not do every task itself.
2. **Focus.** Concentrate on the experiments, the CCs, and the llama.cpp code that JiuwenSwarm builds. Those are the open questions. Avoid infrastructure and tooling work: no more jobq or docker vendoring, and nothing beyond the minimum needed to build and run.
3. **JiuwenSwarm doesn't have to get it right first time.** It doesn't need to compile on the first attempt.
   - Multi-attempt runs, replanning and adapting are fine.
   - The task graph can be richer than a single straight line.
   - The planner is not isolated. It may read what other sessions and earlier runs did, including the Satay candidates, scores and logs.
   - Coding agents (you, your subagents) may help steer and guide JiuwenSwarm sessions. Record that steering as notes or decisions in the factory store, so the UI shows it honestly.
   - Friday's earlier run worked through the factory; reuse that path.
4. **Frontend matters a lot.** Three separate UI agents are working in their own worktrees (tmux windows ui-cc, ui-data, ui-story). Merge their branches when they report done, and don't duplicate their work.
   - English is the default language.
   - CCs get their own tab or tag, held to a high standard.
   - JSON and YAML get multiple views: readable, tree or table, and raw. Anything that is a graph can be viewed as a graph.
5. **Results.** Aim for good results and a good showing of what CCs enable.
   - Measure the gap to Strata. Use the Strata mechanisms the CCs were reverse-engineered from to improve the CCs.
   - Revise or add CCs when results are weak.
6. **Timed runs.** Final P4 timings need a quiet machine: no factory agents, pytest or npm builds running at the same time. P1 numbers taken under concurrent load are reconnaissance only; label them that way.
7. **Granite fixture.** It is being copied to ~/models/campaign/gguf/granite-3.1-1b-a400m-instruct-Q8_0.gguf (sha256 a52205df...). Do the scorer portability adaptation as a documented amendment (path mapping only).

8. **Success bar (owner, ~07:30Z).** The 5 CCs are not expected to close the whole gap to Strata. We need MEASURABLE improvements over stock llama.cpp, attributed per CC. The ordered final timings (P4) must show a clear win for at least some arms against A, and ideally against A+.
9. **Sources.** You may reverse engineer anything anyone has made: Strata source, other llama.cpp forks, papers, other engines. Turn what you learn into CC methodology, samples, helpers and verifiers. Record the source in each CC's SOURCE-MAP. CCs still never ship the finished diff; the JiuwenSwarm session builds it.
10. **Analysis CCs (owner, ~07:35Z).** Codex may analyse very thoroughly. Package the analysis methods as one or more analysis CCs. Examples:
    - Strata mechanism analysis
    - expert-routing profile analysis
    - TTFT phase breakdown (load, prefill per layer, expert copies, CPU vs GPU time)
    - memory and bandwidth analysis
    - gap attribution between llama.cpp and Strata

    These are NOT among the 5 builder CCs, because they don't build components. They are reusable, vetted analysis bundles with method, scripts/helpers, tests, verifier and pinned digests. Their outputs are artifacts that inform the builder CCs and the task graph, and they are shown in the UI as a separate CC kind ("analysis").
11. **Loop shape (owner, ~07:40Z): do, then lab, then report, then the next planner reads every past report.**
    - Each iteration has three steps:
      - (a) A JiuwenSwarm session builds or changes code using the chosen builder CCs.
      - (b) A lab run measures it under bin/capped.
      - (c) Analysis CCs run AFTER the lab run, and their findings go into that iteration's report.
    - The next iteration's planner reads ALL past reports (and earlier sessions and runs). It then replans: which CCs to use next, which capsules to revise, and which new CCs to add.
    - This visible loop is the main thing to show. The UI should make it obvious:
      - a timeline of iterations
      - each with its plan, the CCs it used, its diff, lab results, analysis artifacts and report
      - "what the planner learned and changed"
    - Keep each report self-contained, and link it to the next plan's decision record. Analysis before a run is allowed when it clearly helps, but the default is the post-lab report.
12. **Quantization stretch (owner, ~08:40Z). A stretch goal, after the 5 star CCs have measured results.**
    - **Scope.** Quantized-weight execution: how llama.cpp/ggml computes with IQ2_XXS and IQ4_NL weights on GB10 (CUDA mmq/mmvq and dequant paths, and the CPU expert lane with ARM repack). Strata/ds4 shares the GGUF block formats but ships its own kernels (`src/dsv41/ds4_iq.cu`, `ds4_iq_cpu.cpp`, `ds4_tq.cu`).
    - **Analysis CC first.** analysis.quant_kernel_profile: the share of TTFT and decode time spent in quantized matmul and dequant, GPU vs CPU, per quant type, for llama.cpp, compared with Strata's kernels where measurable.
    - **Then, only if kernel time is a material share:** a builder CC, e.g. a quantized expert matmul kernel builder or a CPU expert-lane repack builder. Its method is reverse-engineered from ds4_iq*, with the same weights and format and no requantization. Acceptance is a numeric tolerance on outputs plus the greedy hash where achievable.
    - **Do not requantize or convert the 232 GB model tonight.** It changes the model, breaks the same-weights comparison with Strata, and costs hours.
    - **The UI shows it** as an extra builder or analysis CC, not one of the 5 stars.
