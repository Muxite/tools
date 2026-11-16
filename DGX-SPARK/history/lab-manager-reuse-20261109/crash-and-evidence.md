# Crash survival and honest evidence completeness

## Failure domain

Keep job/attempt state, operation capture and durable artifact storage outside the disposable test sandbox. A sidecar inside the same outer sandbox is not sufficient protection against that outer sandbox crashing/deleting. The other team's lab agent and our Manager must use the same failure-domain interpretation.

A target-instance crash should fail or interrupt the active attempt, not kill the external controller or prevent future tests. It does not mean continuing the exact live CUDA/KV state. Reconcile actual owned resources, confirm cessation, create a new attempt and repeat declared preparation/warmup.

## Retain before, during and after

Before execution, durably register handoff/image/workload/test-tool identities, budgets, attempt ID, permitted controls and expected artifacts. Record consequential operation intent before invoking it and outcome afterward. Missing outcome means unknown, not success.

Continuously export stdout/stderr, bounded structured events and finalized trace segments to external storage. Flush/rotate at practical boundaries. Large binary profiler reports may only become valid on normal finalization; preserve partial bytes as diagnostic and record whether the report is parseable.

An acknowledged durable segment must survive target-instance destruction. Data still in engine/profiler/device buffers at crash can be lost; no software can retroactively persist it. Report the last durable sequence/time, expected versus collected coverage, partial report validity and loss interval. Incomplete evidence must not support a completed performance claim.

## Failure matrix

| Event | Required observation |
|---|---|
| Engine exits nonzero | Raw exit/logs retained; attempt failed; controller remains responsive |
| Test sandbox stops/crashes | External record survives; evidence through last acknowledged segment remains hash-valid; no false pass |
| Event/network disconnect | Reconcile actual operation/process state using stable IDs; do not blindly submit again |
| Controller restarts | Reopen durable record, locate existing resources, avoid duplicate execution |
| Cancel | Requested, stopping and confirmed-stopped are distinct; retain partial evidence |
| Export fails/storage fills | Retain protected staging, flag incomplete registration, stop new admission before dropping required evidence |
| Late result from old attempt | Retain as diagnostic or reject stale ownership; never overwrite newer accepted result |
| Host power/GPU fault | Suspend admission and request platform recovery; same-host storage alone does not prove host-loss durability |

## Recording all engineering work

Use actual agent event streams/hooks plus command/process wrappers where available. Preserve native records alongside normalized indexes. Link campaign, agent/task, operation, build, release, job and attempt IDs. Log test commands, inputs, outcomes and artifact references, including failed/blocked/skipped cases. Capture descendant/background jobs or explicitly state the coverage gap. Store concise decision summaries rather than private chain-of-thought. Redact secrets and never log full credential environments.

Test recording itself: successful command, nonzero exit, timeout, interrupted agent/runner and background child. A human-written summary does not establish complete operation capture. [OTel](dossiers/otel.md) can transport telemetry, but is not the accepted experiment ledger or a guarantee of losslessness.

## Demonstration boundary

Use a controlled engine process/sandbox stop, not deliberate host OOM, driver reset or device failure. No target crash injection ran during this research task. Actual tester must provide resource identity, raw logs, hashes and stop confirmation. Successful restart of a different fixture does not prove the engine's quality.
