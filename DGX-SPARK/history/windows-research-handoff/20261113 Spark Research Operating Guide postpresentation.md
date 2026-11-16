# 20261113 Spark Research Operating Guide postpresentation

This is an engineering workspace. Its existing folder name retains the earlier demo checkpoint date; no new presentation is being produced.

## Where work lives

- Agent reasoning and subscription authentication: this Windows machine.
- Spark: `user2@100.105.127.48`.
- Owned remote root: `/home/user2/software-factory-spark-20261113`.
- Existing shared queue: `/home/user2/rsi-expert-streaming-spark-002/paired-retry-001/jobq`.
- Local sources, tools and verified evidence: this folder.

The SSH wrapper disables agent forwarding and uses a minimal remote job environment. No provider login, subscription token, SSH private key or credential directory is staged. The source archive contains repository-tracked code, templates and artifacts, not machine account state. Existing user projects and models stay in place. One 12.1 GB owned model copy is retained specifically to control page-cache ownership; it is verified against the original.

## Everyday commands

From PowerShell, set the tool once:

```powershell
$tool = 'D:\AI4Research\Software Factory Spark\20261120 Spark Factory Demo prepresentation\tools\spark.py'
python $tool inspect
python $tool status REQUEST-ID
python $tool logs REQUEST-ID
python $tool cancel REQUEST-ID
```

The other operations are `stage LOCAL-FILE OWNED-RELATIVE-PATH`, `submit REQUEST-ID LOCAL-REQUEST-JSON`, and `fetch OWNED-RELATIVE-PATH LOCAL-FILE`. Submission requires a reviewed script path/hash, argument array, finite timeout, queue class and explicit resource budget. Build requests require a clean owned source path and exact commit in `source_identity`. Heavy jobs require nonempty `input_hashes`; GPU-class requests require an immutable `image_identity`. When `model_identity` is provided, its admitted path, byte count and full SHA-256 are checked before submission and execution. The local wrapper also attests the versioned runner hash. Declare model identity for every model experiment. The first qualification requests retained source identity in their resulting build records; later requests use the stricter v3 admission checks. These controls do not sandbox arbitrary code.

Use unique IDs for changed inputs. Repeating an identical request ID returns its original job. Changing the inputs behind an existing ID is rejected. Stage/fetch refuse differing files at an existing path. Use versioned files for script changes. `remote_v3.py` is the current runner. It includes the v2 cancellation fix and checks pinned inputs before submission and execution; v1 is retained as failed-cleanup history. Do not run old implementation drafts merely because they are present.

Job completion means a terminal queue state plus the corresponding result, not a successful SSH call. SSH disconnection does not cancel a submitted job. On reconnection, inspect/status before resubmitting. Fetch compares SHA-256 before accepting evidence. The current fetch operation supports individual files up to 16 MiB; large artifacts require an explicit transfer plus checksum receipt.

## Resource and ownership rules

Submit builds as `build` and inference as `gpu`, including CPU-heavy inference, so the shared queue excludes builds and other participating inference. Only participating jobs are serialized: inspect unrelated host activity before measurements. Use eight compilation workers initially. Inference probes use eight CPUs, finite container memory, no swap, no network and read-only model mounts. Do not raise budgets or parallelize heavy jobs without a new measured rationale.

The default build request has a 90-minute bound. Inference has an inner 300-second bound and an outer queue bound. Cancel only an owned request ID. The v2 runner stays alive while the child handles TERM and removes its owned container. Graceful cancellation and timeout were tested with real dummy containers; abrupt host failure still requires ownership reconciliation on return.

Never reset the existing JiuwenSwarm checkout, change drivers, globally install packages, prune shared Docker data, kill processes by name, or clear the host page cache. Owned file paths must resolve inside the workspace. Docker membership is powerful; this ownership discipline is not a hostile-code security sandbox.

## Build reuse

`build_cycle_v2.py` is the qualified prototype: clean owned source, pinned CUDA13 runtime, SM121, eight workers, persistent configuration-keyed objects, and fresh images containing only the newly packaged application files. It builds completion, bench and server. It does not claim parity with the historical seven-tool builder or produce a portable archive on every iteration.

Keep verified images for runtime-only changes. The current source has a harmless stderr marker used to verify incremental compilation. The original baseline image remains available. Do not mistake that marker for an inference optimization.

## Memory experiments

`inference_probe_v3.py` is the qualified CPU memory/SSD probe. It uses the existing GPT-OSS-20B MXFP4 model, an owned verified copy, mmap, disabled repacking, a 512-token context and a fixed 64-token greedy workload. It advises eviction only for the owned file, never shared originals. Check cgroup I/O during output; a cap or cache miss alone is insufficient.

The 8 GiB tests exercise a model larger than the allocated budget, not larger than Spark's physical RAM. Full GPU allocation accounting, larger-than-physical-memory validation, broad quality assessment and cross-engine benchmarking remain separate tasks.

## Evidence and candidate CCs

See the handoff and evidence index in this folder. The pinned factory Store/taskgraph implementation records this locally directed work. Some execution records were reconciled after completion from actual queue IDs; those are explicitly labeled imports, not newly dispatched jobs or remote agent dialogue.

Two material-only CC candidates are in `capsules`: `factory.methods.spark_build_iteration` and `factory.methods.memory_budget_qualification`, version 0.1.1. They passed the existing CC v2 declaration loader. They are not centrally installed or advertised as callable tools. Remote paths with the `-v0.1.1` suffix are current; earlier unsuffixed capsule drafts had an invalid material kind and are historical failures.
