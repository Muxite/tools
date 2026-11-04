# Future path for workload profiling

Status: proposal. Nothing here is built. Measured numbers come from the unaudited RTX 5070 Ti report (`sources/2026-10-16-shared-gpu/report.md`). No GB10 result exists.

## The vision

AI4Research runs its models locally on the DGX Spark. Every agent capsule's model calls become GPU work (prefill and decode), the verifier adds many short calls, the builder and benchmark run experiment code, and the router decides which local models stay resident. Profiling each capsule alone gives the records for planning, pairing and routing. Today (M1) the models are remote, so none of this is measured on AI4Research yet.

## What would change the direction

| Outcome | Consequence |
|---|---|
| Step 1 finds a small GPU share in a real local-model run | Drop the pairing case. Keep local-model routing and the experiment capsules (benchmark, builder POC) |
| Test 1 finds no usable DCGM or Nsight counters on the GB10 | Stop counter profiling. Keep timing, memory and cgroup records |
| The predictor does not beat a one-bit GPU-heavy label on held-out pairs | Put the label in declarations. Profiles feed memory budgets and routing only |
| The predictor beats the label by more than the repeat spread | Propose the protected profile input and admission clause, ahead of parallel branches |
| The GB10 exposes knobs that give sensitivity curves | Start the chip-facing report: sensitivity per workload with intervals |

## Open decisions for the owners

1. **Owner.** Who runs the GB10 campaign and keeps the record store. Not named yet.
2. **Quiet-window policy.** The GB10 is the single M1 product host (D35). The sidecar launcher never preempts a core run (`sidecar/README.md:103`). A window is idle-only or scheduled.
3. **Capture boundary.** `sidecar/README.md:107` says no profiling integration or product telemetry. Owner ruling 9 (`side-systems/owner-rulings.md:123`) says no continuous CPU or GPU sampling in run capture. Profiling must stay a separate research-side store, or the owners amend these.
4. **Planner target.** The slowdown error the planner needs. It must exceed the repeat spread (x1.7 to x2.4 for LLM beside training over two runs), so measure repeat variance first.

## Schema changes to propose (to the declaration, planner and check owners)

- A protected profile input beside `resource_inventory` and `plan_policy`, hashed at freeze, feeding `resource_feasibility` (the execution-profile seam, `run-plan.md:645`). It must not live in declaration `ext`, `max_limits`, inventory quantities or the Planner output.
- An admission resource clause so self-tests and evidence runs can record peaks, with a statement of whether the host was quiet.
- A usage clause kind in the conformance record, so a declared `wall_s` or memory claim is checked against observation by host checks (the verifier capsule cannot do this: it sees only the declaration and the output).
- The image digest in the profile join key, next to `declaration_sha256`.
- Reuse the benchmark runner's `hardware_inventory` record (`benchmark-runner.md:78`) for machine state.

## Evidence still missing

- A real capsule run broken into remote wait, CPU, local GPU and I/O.
- Anything on the GB10, including whether cgroup memory accounting sees GPU allocations on unified memory and how file cache is charged.
- More than 4 task families, and more than 2 repeats per pair.
- CPU work competing with GPU work for the shared pool.
- Quality per model for the router. Only cost is measured.
- MPS, MIG, NVDEC.
- Agentic dynamics: data-dependent run length, bursts, tool waits, KV reuse, model swaps.

## Chip questions, later

Solo records on one chip cannot separate bandwidth from compute from capacity. Each chip question needs a controlled change (working-set and context sweeps, power or clock caps if exposed, MPS thread percentage as an SM proxy), real capsule traces to replay, and a simulator calibrated on the baseline (Accel-Sim, with Chakra traces as input; its fidelity for a unified-memory pool is unverified). The output a chip team can use is a per-workload sensitivity with intervals. Decode being bandwidth-bound is already well known, so the new content would be the agent mix and the unified-memory pool.
