---
id: strata-lab-replay
status: proposed-runtime-unverified
source: Sources/Prompts/2026-11-02-cc-image-template.txt
last_reviewed: 2026-11-02
next_action: Prove baseline, interrupted arm and independent fork on one qualified Spark
---
# Running and forking a capsule in a research lab

Central AI4R sends an experiment template and a locked product release. The host pulls each required image and model shard, mounts pinned inputs read-only and launches the lab. A scoped JiuwenSwarm session operates the declared tools. The protected host worker retains stop, lease, network policy and recovery authority. A central manager can run on the same physical machine as the factory if reservations and trust domains are separate.

## Host and network contract

| Action | Producer and transport | Admission, failure and retry |
|---|---|---|
| Request | Software Factory submits signed template/lock refs and bound parameters over authenticated HTTPS. | Manager verifies identity, content digests, operation, experiment budget, host policy and requested placement. Persist before acknowledgement and deduplicate by request ID. |
| Place | Worker long-polls over mTLS with a recent inventory. Central grants run/attempt, generation, epoch, deadline and run-scoped artifact access. | Atomically reserve CPU, shared RAM, scratch and device. Use one exclusive GB10 for a comparison. No double-counting GPU and CPU RAM on Spark. Refuse a fourth concurrent exclusive trial when all three Sparks are occupied. |
| Stage | Worker resolves image platform, manifests, exact model and disk needs. Execute the native reader/component checks and a known input. | Fail a bad digest or incompatible device before the trial. On the Mac, advertise Linux ARM CPU through a VM first. Native Metal needs a separately qualified carrier and reset procedure. |
| Run | Lab Agent gets only the approved operations, parameters and budget. Engine uses a private endpoint. Host collector observes resource use independently. | New dependency or extra privileges require a new lock. Lease expiry fences the old epoch. Require confirmed stop or external isolation before replacing an old exclusive claim. |
| Communicate | Host routes external traffic through the central gateway. Offline runs stage inputs and spool telemetry locally. | Deny peer labs, metadata, alternate DNS, arbitrary proxying and direct internet over IPv4/IPv6. Broker authenticated model calls separately; keep provider and registry credentials outside the engine. Observe route, timing, bytes and verdict. |
| Collect | Host sends OTLP and uploads content-addressed output, logs and pinned sample records through scoped ingestion. | Authenticate events by run/epoch and deduplicate by producer and message ID. Out-of-order events request replay. Seal a result after required objects verify. A missing quality or host measurement yields inconclusive. |

Use the illustrative [lab wire schema](contracts/lab-message.schema.json) for the workshop control vocabulary. It describes message shape. Durable transactions, scope checks, lease expiry, monotonic ordering and workload isolation require the host and manager implementations. Keep the same logical run ID across a retry; a deliberate experimental fork gets a fresh run ID with a parent savepoint reference. Proposed persistence keys are `(run,attempt,epoch,producer,messageId)` and content digest.

## Three useful meanings of save

| Request from the researcher | What to persist | What the next worker can do |
|---|---|---|
| “Keep this edited environment.” | Commit the private container’s changed filesystem/config to an image candidate, record its parent and diff, review for credentials and retain the digest. Treat source changes as recipe inputs for a clean rebuild. | Start fresh processes in the same captured filesystem. Docker’s commit excludes mounted volumes. [Docker commit](https://docs.docker.com/reference/cli/docker/container/commit/) |
| “Retry or branch this experiment.” | Drain the current arm; flush benchmark rows and inputs; stop or quiesce writers; save instance root and each writable volume; record release lock, effective config, host profile, request tape, seeds, completed-arm receipts, dependencies and external-effect receipts in one manifest. | Restore private writable copies and mount immutable inputs by digest. Recreate processes, credentials and warmup. Preserve old partial samples as diagnostics. Restart an interrupted arm from its beginning in a fresh directory. Incus custom volumes need explicit backup. [Incus backup](https://linuxcontainers.org/incus/docs/main/howto/instances_backup/) |
| “Continue from this exact decode instruction.” | Requires supported CPU/process, GPU/driver and engine checkpoint facilities, device compatibility and a consistent I/O boundary. Strata session KV/prompt checkpoints serve a separate purpose. | Offer this mode only for a qualified hardware/driver combination after an interrupted-token continuation test. The default pilot uses application-boundary replay. [Docker checkpoint](https://docs.docker.com/reference/cli/docker/checkpoint/) · [NVIDIA CUDA checkpoint](https://github.com/NVIDIA/cuda-checkpoint) |

A client can ask for a save during any arm. Return a pending ID promptly. Return a sealed savepoint only once all required files, receipts and snapshots exist and verify. If the machine dies before sealing, select the previous complete point. No external write rolls back with a lab image. Child forks get separate scratch, output path, identity, token and resource reservation. A live parent can continue after sealing if it retains its lease. On a single exclusive Spark the child queues or uses a different qualified Spark; hardware changes must be visible in the result.

## First hardware acceptance

1. **Baseline A/A.** Same release, model and actual request tape. Run two independent arms on the same idle host, enforce warmup and capture noise. Confirm resource/latency sensors work on this GB10. Set tolerances from baseline evidence before scoring A/B.
2. **Stop and recover.** Kill the engine mid-arm. Preserve partial JSONL, stop the worker, expire its token, restore from the last sealed checkpoint with new credentials, rerun only the interrupted arm. Confirm completed receipts are not duplicated.
3. **Deliberate fork.** Clone a sealed savepoint, change only an approved experiment parameter with a new binding if needed, and verify isolation of writable volumes and results. Confirm source inputs remain immutable and a stale host cannot publish to the child.
4. **Real comparison.** Collect complete unique deployable bytes, peak host shared memory, prefill and decode tokens/s and held-out quality. Report confidence and missing evidence. A failsafe result can be “candidate smaller, decode below gate”; RSI submits a recipe revision for a fresh build.

Use external host/gateway observations for policy enforcement. The reviewed-code pilot and unprivileged Incus/private Docker path require an actual denied-egress probe, GPU launch, stopped backup and restore before the host is advertised. These are design acceptance tests, not results.

**Inspectable savepoint.** Compare the [sealed-manifest schema](contracts/arm-savepoint.schema.json) with the [synthetic example](contracts/arm-savepoint.example.json). Before sealing, enumerate writable mounts independently on the host and require exact coverage, unique mount and arm IDs, retrievable content for every digest and a valid receipt for each completed arm. A schema cannot prove snapshot consistency.

## November 3 single-CC workshop

[[Designs/CC and Strata delivery/CC and Software Factory/README|CC and Software Factory]] and [[Designs/CC and Strata delivery/Strata Research Lab/README|Strata Research Lab]] now own the single-CC proposal. Factory briefs, products and evaluations are companion records. The November 2 image template and November 3 interchange forms remain historical design inputs.
