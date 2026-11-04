---
id: one-cc-spark-lab-handoff
status: proposed-runtime-unverified
source: November 2 AI4R meeting; pinned Strata source; shared factory brief and independent evaluation; local feasibility checks in this folder
last_reviewed: 2026-11-03
next_action: Reserve one identified GB10 and run the target gates with a protected evaluator
---
# Research lab handoff for the Strata serving-footprint trial

**Lab question.** Can the factory’s candidate serve the pinned IQ3_S model from less storage on one DGX Spark while preserving the agreed inference interface, routing, quality and speed? The factory can choose its implementation. The lab owns the comparison and returns a result even when the candidate fails. Read [the method and recovery drill](Recovery%20and%20evidence.md), then [target feasibility](Qualification.md).

| Handoff | Object and responsibility |
|---|---|
| Central AI4R to Software Factory | The [brief](../shared/examples/brief.json) names the target, pins, success criteria, available tools, budget and expected product. The CC is a reusable template pointing to its carriers. Selection alone gives the caller no execution grant. |
| Software Factory to Central Lab Manager | [Product](../shared/examples/product.json) identifies the candidate and includes the reviewable source/build record. The [evaluation](../shared/examples/evaluation.json) references the brief, baseline and candidate locks, target, workload and frozen evaluator policy. |
| Manager to trusted host worker | A lease binds the host, run, attempt, expiry, epoch, allowed image digests, volume and network permissions. Protect registry write, stop/restore and evaluation authority outside the guest. |
| Worker to JiuwenSwarm Lab Agent | A scoped assignment names the approved baseline or candidate, benchmark arm, fixture digest, parameters, permitted tools, budget and output location. Use only the image’s approved entrypoint and tool bindings. Disable guest shell/host-fallback paths unless the active profile explicitly exposes an isolated tool. |
| Lab to independent benchmark owner | Submit sealed raw request/response data, timings and host-sampled memory; submit content-addressed artifacts and independent API/router checks. Export quarantine receipts for incomplete work. |
| Benchmark to RSI / factory | Write the verdict, missing measurements, lock IDs and failed gate. RSI may propose a new factory rule and require a fresh product and evaluation. A lab agent cannot rewrite the evaluator, threshold or accepted release. |

## Placement and monitoring

Begin with one idle, exclusive GB10. Reserve the accelerator, measured CPU/memory/headroom and disk for distinct read-only source packs, candidate output, engine images and spill files. Account for CPU, GPU and page cache against the same unified RAM budget. A limit must leave space for the host worker. Stage immutable artifacts before launching the measured arm. If the machine cannot meet the exact requested profile, return the failed constraint. Three independently qualified Sparks can run independent evaluations; each comparison stays on its own exclusively leased host. Keep the Mac CPU smoke in a separate arm64 Linux VM profile. Native macOS Metal requires a separate carrier, reset procedure and independent qualification. Each attempt gets private writable scratch.

The trusted worker polls the central manager over authenticated TLS. Actual state comes from the host provider and the worker’s measured inventory. Central reconciles desired start, stop and restore with the observed epoch. Store each command before acknowledging it. Use an idempotency key per command and a new epoch on restore. Release scarce resources only after confirming the old session stopped. The lab itself runs the product and its bounded agent. Keep the complete AI4R control plane outside the lab.

Block direct lab-to-internet, peer and management traffic at the host or upstream network. Permit the scoped runner to use a controlled central gateway for approved artifact staging and, when configured, agent model requests. No public engine listener; the benchmark communicates on loopback or a private lab endpoint. Use a local spool for offline arms. Export protected host signals via OTLP and raw measurements by digest. Record gateway policy verdicts, identity, target and byte counts. Keep provider credentials on the gateway; authorize per-run artifact writes only. A network failure returns a retryable staging failure or quarantined partial evidence.

## Buildable acceptance slice

1. Implement one host worker with a lease and a default-deny network profile. Return the observed platform, driver, storage and denied-egress receipt. Repeat allocation and prove a second exclusive lease waits.
2. Stage the baseline from exact digests. Capture the resolved config, model pack and build IDs. Smoke the original inference interface. Preserve a stopped checkpoint and verify the restore set can be re-opened on a separate attempt.
3. Run the benchmark and capture exact requests, warmup, arm order, sample rows and independently sampled memory. Kill the candidate arm deliberately. Verify that the manager refuses stale results, recovers the baseline and reruns the candidate cleanly.
4. Score all required controls using the protected evaluator. Return the committed evidence manifest and verdict, then verify resource release and network policy teardown. Score incomplete evidence as inconclusive. Only the factory/review lane can publish a new release.

Implementation owners can begin with the [contract files](../shared/contracts/evaluation.schema.json). In the exported handoff preserve the sibling `shared` directory or supply its snapshot. The local drill requires only Python and the evaluation policy JSON.
