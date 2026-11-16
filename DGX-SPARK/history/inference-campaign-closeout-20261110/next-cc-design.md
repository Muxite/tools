# A useful CC first; a small improvement loop second

**Jetson evidence update:** [received Jetson findings](../jetson-campaign-closeout-20261110/README.md) and [specific CC design changes](../jetson-campaign-closeout-20261110/cc-design-delta.md) add a per-type graph-dispatch component, existing native builder support and new tool requirements. Earlier Jetson-unreceived statements below describe the prior inspection state.

**New evidence received:** [follow-up verification and corrections](followup-evidence/README.md) confirms up1 MUL_MAT passed and a historical live recovery rehearsal exists. Earlier unresolved statements below record the prior inspection state; do not use them as current negatives. Targeted reuse-hit/alias/graph tests and current integration readiness remain open.

Status: proposed implementation brief, November 10. This refines Friday's scope after the user's latest clarification: **one demonstrably useful tool or component is sufficient; orchestration, building and lab scenes are supporting extras.** The broader objective remains discovering the initial CC portfolio and Manager design through engine improvement.

Source basis: retained x86 campaign commit `ecaa4b0d1ed134d598993ca9f26e21745b0bbd4e`; local JiuwenSwarm CC v2 checkout `2889a1d6342e9baa7721648eca196bbce79a31d4` (README, protocol changes, declarations, runner and source-build materializer inspected). These are source observations, not a new runtime qualification.

## Concrete recommendation

Build **`cuda_profile_report`**, a finite read-only analysis CC wrapping and hardening the existing Nsight Compute CSV analyzer. Package **`q8_activation_reuse`** as a passive source-component CC with its patch, integration contract and qualification evidence. Reuse the existing Build CC. Let a small JiuwenSwarm agent read these materials, call the tool and propose a bounded experiment to our Manager adapter. A disposable local Docker environment can return the result. Integration with the other team's lab agent is extra.

These are two independently valuable deliverables. If only one is ready, demonstrate that one. The component already has scoped engine evidence; the tool is cheaper to qualify, can run on saved real evidence without GPU privileges, and exercises JiuwenSwarm's existing finite CC interface. Build/experiment execution should not be prerequisites for showing that the analysis tool works.

The tool reports what was measured and exposes candidate bottlenecks. The agent chooses an experiment, and a separate unprofiled comparison evaluates the result. Do not hard-code “profile means apply Q8 reuse”: the tool may find that this component is irrelevant.

## 1. Primary tool: cuda_profile_report

### Narrow job

Turn a supported long-form Nsight Compute CSV into an inspectable report: launch counts, measured kernel-duration totals, kernel-family breakdown, byte coverage, derived read or read+write bandwidth, and a clearly labelled small-kernel/low-throughput heuristic. Preserve exact kernel names and per-launch evidence. It does not run a profiler, infer unobserved CPU time, select an optimization, or declare the engine faster.

Reuse [ncu_summary.py](snapshot/campaign/cc/profilers/ncu_summary.py) and its existing tests/real captures. Existing code already scopes launch IDs by process, rejects duplicate metrics and mixed write coverage, converts units, and duration-weights metrics. Review before reuse: it currently removes every comma from a numeric value, groups template variants by a regex, labels its heuristic `launch_bound`, and lacks a CC-level input-size/provenance contract. Those are specific hardening tasks.

### Inputs and ownership

- A workspace handle and relative CSV path, expected SHA256, supported export-format revision, and optional capture-manifest path/hash. Read bounded ordinary files inside that handle. Reject absolute paths, traversal and symlinks escaping the workspace. The trusted-local runner is not an OS isolation boundary.
- Default proposed limits: 32 MiB CSV, 200,000 metric rows, 50,000 launch identities, 30-second call timeout. Make limits explicit and reject overflow without returning a deceptively complete report. No unbounded recursive discovery or output proportional to arbitrary kernel-name size.
- Capture manifest records its own schema, source `.ncu-rep` hash, CSV hash, tool version/export argv, engine image identities, model/workload identity, process/device scope, selected capture region and known replay/cache controls. Producer-supplied declarations remain declarations. A missing manifest still permits **unbound diagnostic analysis**, prominently marked; it cannot produce a comparison-ready claim.
- An export hash proves which bytes were analyzed. It does not prove NVIDIA produced them or the manifest's model/process claims are true. Cross-check observed CSV process IDs and available fields; surface contradictions.
- Read and hash the exact bounded byte buffer once, then parse those bytes. Avoid separate hash/read races. Use strict decoding with an explicit error; retain the input untouched. CSV headers and units identify a supported format, not arbitrary locale inference.

### Deterministic output

Return a compact JSON summary plus a full JSON artifact, both schema-versioned. Fields include input SHA/bytes, parser revision, analysis status, binding status, capture scope, warnings, counts of accepted/ignored rows, metric coverage, exact names and process/launch keys, duration/byte totals, and sorted family summaries with their member names.

Use explicit SI units: seconds, bytes, decimal GB/s. Bandwidth denominator is summed profiled kernel duration. It is **not** whole-inference bandwidth, wall time or concurrent-device utilization. Report `read` versus `read+write` scope. Missing write bytes do not become measured zero writes. Zero duration, negative/nonfinite values and duplicate required metrics are errors. Unknown optional metrics are ignored and counted. No NaN/Infinity JSON.

Rename `launch_bound` to `small_kernel_low_throughput_candidate` (or similarly literal wording). Its recorded policy is duration <5 µs AND DRAM throughput <5% of reported peak. This is a heuristic, not proof that launch overhead dominates. Report exact count and share of **summed kernel duration**, never share of end-to-end runtime. Do not extrapolate a speedup from that share.

Group families for navigation but retain the exact launch records. Do not merge identical launch IDs from different processes. Keep multi-process reports partitioned; an agent must explicitly choose scope rather than silently pooling. Repeated export headers are acceptable only when structurally identical. Require an explicit numeric grammar: support validated thousands grouping, reject ambiguous decimal-comma values rather than turning `1,5` into `15`. Do not clamp out-of-range percentages blindly; document metric-specific semantics and expose unsupported values.

The authoritative result is deterministic for identical input, parser and policy. Put invocation time/receipt ID outside the deterministic analysis body. Emit no partial success after malformed required rows. An error receipt names the input hash and failure class without echoing private CSV content.

### Verification that earns trust

1. Independent hand-computed fixture: at least two processes sharing launch IDs, multiple kernel names and known units. Assert byte/time arithmetic and weighted averages, not merely current implementation output.
2. Real campaign capture: preserve exact CSV hash and check a few launches against their raw metric rows. The campaign parser reports roughly 222 GB/s and 600 launches for its documented fixture; use exact arithmetic/appropriate tolerance, not a hard-coded claim that every capture has those numbers.
3. Reject truncation, missing/duplicate required fields, zero/nonfinite duration, partial write coverage, malformed numeric grouping, unsupported units, inconsistent repeated headers, path escape, hash mismatch and size/row-limit overflow.
4. Assert invariants: row order does not affect output; valid unit conversion preserves results; splitting a kernel family leaves global totals unchanged; adding unused optional metrics changes only coverage diagnostics; two-process identity collision does not collapse launches.
5. Real CC runner test and one real JiuwenSwarm agent tool call. Check receipt, artifact, workspace effects, replay semantics and absence of network/Docker/GPU requirements. A CLI run alone does not qualify the CC integration.

## 2. Component: q8_activation_reuse

This is not a profiler recommendation manufactured for the demo. The campaign measured a +2.1749% full-engine Q8_0 tg128 gain on Granite with the same release image toggled OFF/ON. Saved evidence and exact arithmetic are in [record-audit.json](record-audit.json). Qualification remains narrow; no speed claim on Jetson, Qwen or a new upstream base follows from it.

### What is integrated

A source patch against full llama.cpp commit `31288c9c66e59377f7788d920678a565bb89dd37`, touching the CUDA backend. The [design](snapshot/campaign/cc/q8_reuse/DESIGN.md) reuses activation quantization only for eligible unfused Q8_0 `MUL_MAT`, contiguous F32 single-token input `[N,1,1,1]`, F32 non-overlapping output, stream zero, and a non-concurrent evaluation. It does not cover MoE `MUL_MAT_ID`, all quantization types, batched prompt processing or every fused path.

The CC should contain the patch, a machine-readable applicability/qualification manifest, source license/provenance, integration instructions, exact build settings and evidence references. A passive material bundle fits the existing CC v2 implementation; a component need not be an executable tool. Agent instructions are part of the integration contract, but cannot widen execution authority.

### Integration must check

- Base commit, patch SHA, resulting tree/affected files, target architecture/toolchain and required CMake targets. Build in an isolated staged source copy. Reject a different base instead of silently fuzz-applying or treating a rebase as qualified.
- This component may allocate persistent scratch for each distinct padded activation width until backend destruction. Record this memory cost; a speed improvement is not a memory improvement. It cannot be advertised as a hard-budget mechanism.
- Cache eligibility requires tensor identity, data pointer, shape, strides and stream. Overlapping writes, other executed operations and successful fusions invalidate reuse. Graph replay must retain valid scratch addresses and record fresh producer quantizations. No cache entry crosses evaluations. This state discipline is the substantive component contract.
- `GGML_CUDA_Q8_REUSE` is read once per process; exactly `0` disables it. `false` does not. Separate processes for OFF/ON. Existing graph-disable flags also use presence semantics: record unset versus set explicitly, not just values.
- Do not use the demonstrated `.so` swap as the integration mechanism. Strict ABI analysis disagreed; that result only covered one exact pair. Source build and runtime qualification are clearer.

### Qualification gates and unresolved evidence

Require a baseline build and candidate OFF/ON; CUDA backend correctness plus targeted aliasing/stale-input/shape-switch/graph-capture-replay controls; an observed engagement indicator; exact or declared-tolerance numerical comparison; and matched unprofiled repeats. Saved PPL/KLD uses a clipped uint16 log-probability format, so nonzero self-baseline error must be measured. Do not present PPL equality as raw-logit bit identity.

Keep existing accepted qualification distinct from newly collected gates. Ask the campaign lead for which alias/graph cases actually ran on CUDA versus host mocks. If not run, retain the gap and prioritize bounded cases; no blanket GPU correctness claim. Instrumenting counters can alter the binary/timing, so identify diagnostic and timing builds separately and keep hot-path instrumentation out of speed arms.

## 3. Build and JiuwenSwarm integration details

Reuse [Build CC](snapshot/campaign/cc/build_engine/README.md) rather than JiuwenSwarm's `source_build.py`: the latter materializes CC payloads, not inference-engine OCI images. Inputs are full source commit, component content hashes, pinned base images, build target/configuration and new output directory. Outputs are image transport artifact + build record + binary/linkage identity + logs, including stage-specific failures.

Record archive SHA, platform manifest/config/index identities and local run_ref separately. A receiver must verify the delivered platform image and artifact; config digest alone is not the whole transport/admission contract. Do not assume a local image ID is pullable remotely. Preserve build provenance separately if image save/load drops attestations.

Current JiuwenSwarm CC v2 already has `cc_list`, `cc_material`, `cc_call`, artifact receipts and passive methodology materials. Native tool execution is **trusted_local**. Existing finite image CCs mount only workspace handles; they do not provide GPU or Docker-host handles. Therefore use a read-only finite tool for profile analysis and a deliberately operator-authorized native builder adapter on the development host. Do not put the Docker socket in a generic analysis CC or mount arbitrary host paths to bypass the runner.

Same `cc_call` key replays its receipt without rerunning. Fresh builds/experiments need fresh operation/attempt identities; retries are not changes to an old record. Existing default finite-call timeout is 60 seconds; configure a realistic explicit build deadline instead of relying on warm-cache timing. A timed-out build may have surviving Docker/BuildKit work: return unknown/cleanup-needed until owned work is reconciled, not “stopped” merely because the client exited.

The available CC v2 implementation is a separate scope-reset branch. Friday's requested M1 demo base may not contain it. Check the exact demonstration branch/base with the owner and port only the necessary CC capability integration. Do not restore removed compiler/RSI machinery, merge the whole scope-reset branch blindly, or claim base compatibility from a local prototype.

## 4. Minimal agent/Manager/lab experiment

The agent reads the tool report and component applicability, states a falsifiable hypothesis, and submits a small experiment: same Granite Q8_0 model/workload, baseline/candidate/OFF/ON, declared reset/warmup, fixed precision/context/token length, frozen correctness and speed criteria, bounded capture and timeout, evidence destination. It may conclude the component is inapplicable. Manager deterministically validates, creates attempts and records outcomes; it does not invent the scientific hypothesis. Local Docker is a test provider fixture, not the other team's lab agent.

Execution, measurement validity, numerical assessment, completeness and cleanup are separate result fields. A rejected hypothesis is useful data. Numerical gates are frozen before outcomes; post-hoc interpretation is retained as a new assessment, not a rewritten pass. Keep profiled and unprofiled arms separate. A full live loop is extra; a useful tool call or source-component integration with verified records is enough for the core demo.

## 5. Next tools, ranked after these two

| Priority | Tool | Concrete need | Reuse and narrow boundary |
|---|---|---|---|
| Next | Engagement probe | Compiled-but-unused hot patch; zero speculative drafts | Per-mechanism counters/log contracts. Return engaged/not-engaged/unknown with evidence, not timing validity or correctness. |
| Next | Measurement-window observer | Swap and concurrent work invalidated apparent wins | Existing resource_observe + proc/cgroup sensor adapters. Emit rates, sample coverage and contamination reasons; unknown is not zero. |
| Next | Paired result assessor | +2% gain, noisy PAP, batch-shape floors | Existing verdict + saved runs. Match identities/state/conditions, preserve exclusion rules, report uncertainty and numerical policy; refuse mismatched comparisons. |
| Later | Image handoff verifier | Index/config confusion, absent remote artifacts | Existing engine_handoff archive reader + content hashes. Acceptance and executable run reference remain distinct. |
| Later | Pinned model/workload fetch | Long downloads and contaminated measurements | huggingface_hub/curl plus revision/content hash and pause policy. Model delivery is separate from the engine image. |

Nsight Systems token-interval analysis remains useful but is a second profiling tool: its current parser assumes one process and a specific logits-D2H byte-size marker. It must prove marker applicability before reporting per-token idle gaps; missing kernel detail in CUDA graph traces is not zero compute. Do not widen the first CC to support every profiler format.
