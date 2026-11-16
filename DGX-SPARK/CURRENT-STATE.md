# Current state at capture

This page summarizes retained evidence inspected on the Spark. No engine benchmark or factory test suite was rerun while assembling the package. Exact capture time, factory HEAD, branch, dirty paths and per-file hashes are in REMOTE-SNAPSHOT.json.

## Hardware transition and source identity

Active work lives under `/home/user2/software-factory-spark-20261113` on the DGX Spark. Historical SSH access used the operator's existing user2 connection. The old Orin Nano target was sm_87; Spark build records use native ARM64 and SM121/CUDA13. Use actual current host inspection before execution, not those historical configuration values alone.

Factory source at capture: `sources/cc-dgx-spark`; committed base `e6099f4210442ef81ec9a54c4d7f11acbe98896e` follows `1ada3481c`, `2e06e4b50` and `c7891472b`. The source was committed during collection; the final capture records a clean working tree. The packaged hashes identify the selected bytes. Source branch lineage includes cc-siminfeng; the exact captured branch is in REMOTE-SNAPSHOT.json.

November 13 factory setup used `c7891472b399aecba42735df19b8c80451231355`. The separately built shi3z Strata fork used `52470278377b1d1e6d248399c4bbbdd754ac4680` with ggml `3cf03257f219afbe7334045ff7c6a06ac68c627d`; its approximately 59-second success was build/help launch only. The chosen existing DeepSeek executable was Strata 0.1.56 at `ffa80d73133ea5c548aefe57889a16e8085a938f`; the November 13 check matched asset sizes/mtimes, not fresh full hashes. Those setup facts are historical, not the latest campaign baseline.

## Measured engine results

The night campaign used locally source-qualified fixed-placement Strata `89ae0ee6123597636ef162dec826230186c00f3b`, the pinned DeepSeek pack, full-six routing and CPU8. It is not an unmodified upstream benchmark.

| Result | Evidence and limit |
|---|---|
| Long-prefill pg4096/tg16, chunk256 to1024 | Native prefill+decode latency 28.221 to17.717 seconds; 37.22% lower, 1.593x combined output rate. Decode stays about14.8 tokens/s. A-C-C-A, four fresh processes, one repeated speed prompt; excludes startup/tokenization/client latency. |
| Adapted eight-shot ARC16 |16/16 in each arm/repeat, exact generated tokens and finish reasons match. Sixteen unique questions, not64 independent questions and not broad quality certification. |
| pg512/tg128 | Pooled combined-rate gain24.38%, but control variation is material and long outputs differ between profiles. Exact-output gate fails; no promotion. |
| 76 to68 billion-byte expert budget | About8GB more observed host-available headroom. No repeatable speed gain or exact total GPU-memory saving established. |
| Numerical followup | At output index49 after49 identical prior tokens, full129,280-logit vectors differ: baseline token10367 wins over32187 by0.0573387; candidate reverses order by0.3701553; maximum absolute vector difference1.2083893. This identifies same-history output divergence, not its first layer or cause. |

The numerical capture work retained truncated-dump failures and an adapter newline bug, then used a bounded FIFO-to-RAM capture and corrected importer. Baseline data was re-imported without rerunning the GPU just to fix a CPU parser. Captured timing is instrumented and is not a new speed result. Observer overhead, repeatability, causal localization and quality noninferiority remain open.

## Factory progress

- The November15 export records39 top-level CC packages,47 including nested components, and1114 tests passed/1 skipped. These are snapshot-specific historical results, not a fresh certification of subsequent dirty changes.
- The earlier actual JiuwenSwarm CPU investigation completed in1029.05 seconds, created/refined/pruned branches and retained an inconclusive verdict. GPU campaigns described alongside it were manually operated; do not attribute them to that agent.
- Later source adds branch-to-cycle binding, fresh CPU campaign specifications, scoped prefill qualification and numerical investigation. Offline/Host tests do not yet prove a fresh connected live-agent branch-to-GPU interruption/recovery cycle.
- A later two-turn/300-second CPU mission published useful immutable findings but hit the controller timeout. It is not a successfully completed turn. Its recorded817,802 input tokens include745,856 cached;9,602 output includes3,200 reasoning. This single mission is not a matched cost improvement.
- The earlier standalone ARM64 export image is `sha256:4e25f0ec7200b28f348aa0a3ce753ea1c5b5306e70ea8cee525ae03d862fafa3`. Export verification does not establish clean-host restoration or include newer uncommitted development automatically.

Native component speedups, synthetic memory savings and reduced response bytes are scoped component/tool findings. None may be relabeled an integrated Strata gain or multiplied together.
