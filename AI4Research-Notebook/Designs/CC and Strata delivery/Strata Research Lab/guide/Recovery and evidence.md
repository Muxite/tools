---
id: one-cc-spark-lab-recovery
status: locally-exercised-synthetic-drill
source: Pinned tools/dgx_bench.py; Docker and Incus manuals; local recovery_drill.py and shared evaluation policy
last_reviewed: 2026-11-03
next_action: Repeat the interruption and stale-epoch checks against the real qualified host worker
---
# Recovery, forks and independent evidence

**Concrete savepoint.** A requester can ask for a save at any time. The normal lab save becomes usable after a benchmark arm completes and output is flushed. Store the input lock, run/attempt/epoch, root filesystem snapshot, each writable volume snapshot, toolchain/environment pins, exact requests, completed-arm receipts and next cursor in a protected manifest. A forced interruption preserves partial evidence under its original attempt. Only complete, verified arms can be reused.

| Operation | Preserved | Restore contract |
|---|---|---|
| Factory build | Commit, dependency lock, build context, image and separate model digests | Rebuild the source and verify the resulting product under its own qualification policy. A filesystem capture by itself does not document its build history. |
| Save container changes | Docker commit captures filesystem/config changes and pauses by default. Mounted volumes need a separate save. | Use a private diagnostic image, record parent digest and include separate volume receipts. Rebuild a reviewable release before promotion. [Docker commit](https://docs.docker.com/reference/cli/docker/container/commit/) |
| Stopped lab save | Root filesystem and independently enumerated mutable Incus volumes captured at the same quiesced boundary; input weights remain immutable. | Confirm attached-volume coverage. Quarantine incomplete snapshots. Recreate the engine, reload the model and rerun warmup. External receipts stay outside the save. [Incus backups](https://linuxcontainers.org/incus/docs/main/howto/instances_backup/) |
| Independent fork | Sealed parent checkpoint, accepted output hashes and immutable input references | New run ID, lease/token, private writable volumes, port namespace and output prefix. Record parent link and explicit changes. Avoid duplicating live GPU ownership or replaying external effects. |
| Live process restore | Docker CRIU is experimental, targets single-host use first; GPU state needs compatible CUDA checkpoint support. | Qualify the exact Linux/ARM, driver, CRIU, isolation mode and engine before advertising this feature. Strata’s documented Spark trial used driver 580.173; NVIDIA documents ARM support with the 595 driver generation. [Docker checkpoint](https://docs.docker.com/reference/cli/docker/checkpoint/) · [NVIDIA checkpoint](https://github.com/NVIDIA/cuda-checkpoint) |

### Store and score

Pin the benchmark before granting a lease. The [evaluation policy](../shared/examples/evaluation-policy.json) currently proposes a 15% reduction in unique pack bytes, no increase in peak shared memory, at least 95% of baseline prefill and decode speed and quality within 0.5 percentage points. Count all serving-required unique payloads including metadata, shared bases, scales and residuals; separately report engine-specific bytes when packaging or offloading moves files outside the pack. If the candidate needs another retained source pack to serve, count it. Host memory high-water evidence needs a stated source, sampling cadence and collection window. Record the effective batch, context, workload, seed, schedule and thermal state. The protected benchmark worker measures speed from raw token/time records and evaluates held-out replies, routing and interface checks. Never treat candidate-reported success as a gate. A broken required measurement produces inconclusive; a valid gate violation produces fail. Only a complete comparison can pass.

The native Spark harness writes per-arm config, metadata and JSONL sample rows, starts a fresh server per round and draws random prompt nonces. Give every attempt an empty output directory/tag. Record or pre-generate the actual request bytes, warmup and nonce sequence when exact replay is required. Keep raw partial arm data as diagnostic evidence and repeat the interrupted arm. When condition drift makes the sealed baseline incomparable, rerun the entire pair. Keep the effective prompting regime and cache semantics visible, and counterbalance order over repeated pairs. Strata’s prompt-tail checkpoint is a serving cache for prefix reuse. It cannot restore a model process after the lab is torn down. [Benchmark implementation](https://github.com/Niko1221/Strata/blob/c62d5e3a15b40ea51c96aae9e8d36928965f53ab/tools/dgx_bench.py#L141-L202) · [Prompt checkpoints](https://github.com/Niko1221/Strata/blob/c62d5e3a15b40ea51c96aae9e8d36928965f53ab/docs/PROMPT_CACHE_TAIL.md)

### Reproduce the local drill

Run `python recovery_drill.py` from this folder. When the policy travels separately, pass `--policy path/to/evaluation-policy.json`. The standard library script creates a temporary SQLite ledger, persists hashed blobs, closes and reopens the connection and exercises a failed comparison. The two tiny synthetic samples test protocol semantics. They do not estimate throughput, quality or memory.

| Injected condition | Expected and locally observed |
|---|---|
| Partial candidate arm followed by restart | Baseline receipt survives reopening; partial data stays diagnostic and verdict is inconclusive. |
| Restore request before old host stop | Fencing rejects reassignment. The drill simulates the external stop confirmation. |
| Delayed report from epoch 1 after granting epoch 2 | Worker admission rejects the stale report. |
| Repeated / altered evidence for a sealed arm | Identical bytes return the same receipt; changed bytes conflict. |
| Faulty candidate claims pass | Protected scoring ignores the claim and finds the wrong answer despite improved synthetic storage and equal rates. |
| Accepted evidence file altered | Rehash fails and scoring returns inconclusive. |

The script does not emulate live device ownership, a full CC parser, restartable snapshots, network enforcement or statistical acceptance. Its SQLite table is scoped to one synthetic run and its scorer reads locally generated fixture metrics; it is an executable behavior example. The real worker needs per-run keys, authenticated producer identities, cryptographic verification, transactional blob/receipt handling and a trusted host/scorer boundary.
