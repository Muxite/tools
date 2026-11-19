# 20261120 DeepSeek Spark Coding Handoff prepresentation

This handoff is for the November 20 llama.cpp demo. The older Strata campaigns provide historical evidence and reusable CC materials. Start with [the engineering plan](<20261120 DeepSeek Spark CC Engineering Plan prepresentation.md>) and use [the outline](<20261120 DeepSeek on DGX Spark Demo Outline prepresentation.md>) for the stage sequence.

## First coding assignment

1. Inspect the current Spark checkout, Git status and project checkpoint. Preserve existing Strata work. Start separate owned checkouts for llama.cpp and the active factory code. The atlas revision is `9048bad8d6e3a0f9f1726e238e451181c7e02613`. If the existing Spark checkout lacks that commit, obtain the pinned upstream commit in the separate checkout. Record source pins and any source mismatch.
2. Use the existing [retained model identity](../../reference/night-evidence/input-identities/assets/deepseek-full-identity-v1.json) to draft the llama.cpp admission card. Bind the four backbone shards plus the required Engram, drafting off. Check tensor roles, encoding, tokenizer, shard resolution and the lazy path. Keep model paths and observed receipts in local records. Use the current verified launcher and lab tooling for the admission request. Target work is gated on separate experiment admission.
3. Implement the smallest useful version of **CC 1, Expert Weight Residency Builder**. Deliver deterministic placement from a checked budget and trace, effective configuration and a slot lifetime interface. Add focused CPU fixtures for an infeasible budget, two context reservations, admission or bypass, and eviction while a consumer holds a slot. Start with a static budget and bounded demand fallback.
4. Implement **CC 2, Expert Weight Streaming Builder**, against a supported CPU/mapped expert consumer. Locate selected IDs, original GGUF ranges and the final reader. Implement bounded demand reads and same-key coalescing, then prove byte fidelity, short-read behavior and safe lifetime through that reader. Use a reversible integration switch. If the chosen path needs a new compact-weight consumer, identify that requirement and land the smallest fixture-proven prototype first. Preserve exact expert selections and mixture weights.
5. Wire the CC declarations and receipts into the existing JiuwenSwarm/Codex material, build and lab interfaces. Use the reference tree for discovery and fixtures. Apply implementation changes in complete source checkouts. Deliver branch and commit IDs, CPU check outcomes, planned engagement counters and a short admission request for the first Spark run. Keep CC 3, Routed Expert Execution Builder, at work-order level until the prefill profile supports it.

## Shared interface and first experiment

- Use `(checkpoint identity, layer, expert, packed layout)` as the semantic weight key. Bind a slot lease to its buffer generation. Read completion makes it ready. The last reader's release or backend completion makes it eligible for reuse. Keep memory reservation, outstanding I/O bytes and active leases independently observable.
- Start with stock A, candidate with switches off A′ and candidate with both features B. A/A′ should agree on greedy output and effective settings. Then check actual path engagement, exact token/stop identity, memory and intended fallback behavior before timed runs. Hold the full model, seed, prompt identity, context, physical ceiling and cache conditions fixed across the scored arms. Pin both binaries and use the winning digest on stage.
- Keep Engram and routed-expert bytes and waits separate. Use existing lazy Engram behavior in both arms. Measure a short-input decode workload and a long-input prefill diagnostic before deciding which result to score. File-backed residency can overlap OS page cache. Use host measurements and effective placement to account for copies.
- CPU fixture execution and source work are the first milestone. Prepare a bounded hardware admission request covering asset paths, memory floor, process/image identities, launch and cleanup scope, time budget and stop conditions. Keep existing services and other workloads intact. Keep older requests and measurement outputs as historical evidence.

## Component ownership

The atlas separates eight high-level responsibilities. This synopsis gives the coding agent the handoffs needed for the demo.

| Component | Responsibility relevant to the demo |
|---|---|
| Completion service | Streams the working completion and exposes client timing. |
| Generation runtime | Forms prompt and decode batches. It owns prompt chunk admission. |
| Token processing and sampling | Preserves tokenizer, sampling and greedy output checks. |
| Model execution | Computes authoritative route IDs and mixture weights. Co-owns grouped expert execution. |
| Model preparation and loading | Resolves the checkpoint, tokenizer and original packed byte ranges. |
| Sequence state | Reserves KV and recurrent state within the shared physical memory budget. |
| Weight residency | Owns placement, expert slots, demand reads, readiness and optional future prefetch. |
| Tensor execution backend | Provides the reader completion boundary and grouped CPU/CUDA kernels. |

The atlas’s **96 GiB** illustration uses 52 GiB fixed, 8 GiB workspace and 4 GiB headroom. Raising the sequence reservation from 8 to 16 GiB reduces the expert slot budget from 24 to 16 GiB. Actual admission uses observed allocations and headroom. One physical allocation is charged once.

## Reuse and evidence

- [Complete CC catalog](<../../reference/factory-source/docs/architecture/factory/20261113 CC Catalog and Lab Integration postpresentation.md>) and [cache and SSD methods](../../reference/factory-source/docs/architecture/factory/RESEARCH-CACHE-IO.md).
- [Exact engine source pin](https://github.com/ggml-org/llama.cpp/tree/9048bad8d6e3a0f9f1726e238e451181c7e02613) and [external implementation precedent](https://github.com/wici-ai/inferssd/blob/main/docs/architecture.md).
- The retained J-XS4 policy replay is summarized in the engineering plan. Its raw capture is an operator-local fixture. The included `expert_cache_lab` package has a portable fixture for checking the interface before obtaining a target-model trace.
