# Concrete CC design changes after reading both machines

One useful tool OR component is still Friday's required core. Jetson adds a **clearer component story**, not a requirement to show both machines or build a larger platform.

## Component option: per-type MoE graph dispatch

If the Jetson is available for the demo, consider `moe_gateup_dispatch` with **Q4_K only** as the component example. It shows a recorded ~24% improvement and a Q8 counterexample, with an obvious role for applicability and tests. Keep x86's Q8 activation reuse as a separate candidate. Do not claim the Orin result on the RTX machine.

The integration contract must encode these details:

- **Exact payload:** patch 03 SHA256 `1369518f3b16e4a5d0330355bab75b98674ee3109d43ab5dcc4f8a240834148f` against llama.cpp `31288c9c66e59377f7788d920678a565bb89dd37`. It replaces patch 01; do not stack 03 with 01 or the earlier combined-01-02 patch. The component's dependency/conflict declaration should enforce this before a build.
- **What it changes:** selected single-token `MUL_MAT_ID` gate/up GLU fusion predicates. It does not globally disable fusion or replace all matrix kernels. Existing standalone dispatch selects the implementation. In Q4_K on Orin this is MMVQ with Q8_1 activation quantization, not a promised tensor-core MMQ path. BF16 may use MMF and changes activation rounding.
- **Requested versus effective policy:** names are case-sensitive: `q4_K`, not `Q4_K`. Source currently ignores unknown names. CC integration must reject unknown/unqualified selections instead of claiming the switch is engaged. Empty/unset list is not necessarily OFF if legacy `GGML_CUDA_J_MMF_IDS` is inherited; the old flag unions BF16 into the selection. Build the OFF environment deliberately and record both variables, including unset state.
- **Process lifetime:** selection is parsed once. Start fresh processes for arms and never change the environment after capture/initialization expecting a different graph. Record canonical startup selection log. That line proves policy selection, not that an eligible node actually took the changed path; confirm graph/kernel evidence separately.
- **Applicability:** patch 03 has no hard architecture guard, despite the directory name `sm87`. Package acceptance is narrower than syntactic enablement: local Orin/Granite/selected weight types only. Q8 is a measured performance rejection; other types/shapes/architectures are unqualified. No broad default from an env-list parser.
- **Numerics:** mixing in Q4 weights already has quality loss versus BF16. Same-model fusion OFF/ON is a different comparison from quantization-versus-BF16. The printed KLD 0.060395 in both arms is not a new zero-KLD computation-preserving proof. Keep baseline, candidate and reference identities separate.
- **Verification level:** use an engine graph containing both selected expert projections and GLU, repeated decode/graph replay, nonselected type and multi-token controls. Single-op `test-backend-ops` is supporting coverage only. Ensure nonzero executed case counts—Jetson's Q4 kernel screen ran zero cases because a pipeline uppercased the type.

For automated integration, the coding agent reads passive component materials, checks exact base/conflicts/target, stages source, invokes the existing target-aware builder, and submits a bounded experiment. A patch applying successfully is not acceptance. Identified build output, engaged mechanism, numerical policy and unprofiled local measurements remain distinct gates.

## Tool priorities supported by both campaigns

| Priority | Specific CC | Contract detail to build, not just a feature label |
|---|---|---|
| First portable tool | `cuda_profile_report` | Existing x86 long-form NCU parser, bounded/hashed input, null-with-reason metrics, validated identities/units, finite totals, explicit capture completeness. Jetson NCU is permission-blocked, so accept recorded supported exports; do not require live counter access. Nsight Systems is a separate schema/backend, not an implied supported format. |
| Next | `engine_preflight` | Inspect the exact image/tool/version's capabilities and effective startup settings for a bound request: supported flag names, selected model/template, context, precision, graph policy, component selection and expected runtime/platform. Separate observed from declared fields. Execute any help/probe through the existing provider; do not add another privileged executor. Unsupported/unknown means reject or needs-information, not silently remove an experimental variable. |
| Next | `run_evidence_summary` | Join results, stderr and telemetry by attempt and recorded time interval. Distinguish exit/trigger/kill/cleanup, retain invalid/unscored arms, record warm-up exclusion and aggregation policy. Derive per-device bytes/IO from cumulative deltas; record units, sampling gaps/resets and global scope. Do not sum Jetson shared DRAM with process/cgroup readings. |
| Supporting method/tool | `graph_engagement_check` | Per-component observed path/case assertions, including zero-case rejection, graph versus isolated-op scope, eligible-node count and captured graph policy. Reuse engine counters/NSYS inventory first; do not assume one generic operation benchmark exercises every component. |

The GGUF tensor-manifest tool is also worth reusing for the cross-host identity question. It should compare exact file hashes first, then name/type/shape/payload identities while separately reporting tokenizer/template/metadata differences. A filename or global quantization label is insufficient. This can be a tool method before becoming another CC.

## Build CC reuse, not parallel implementations

Jetson already has a native target extension: `--target jetson-orin`, arm64/sm_87 build settings, ccache normalization, extra targets and build evidence. The x86 builder snapshot hard-codes amd64/sm_120. Reconcile the two versions with shared input/output contract tests and per-target recipes. Preserve distinct base images/runtime requirements. Do not simply pass CUDA architecture 87 to the x86 image recipe and call it a Jetson build.

Retain actual binary hashes even if builds are not bit-reproducible. Source/recipe identity and output-byte identity answer different questions. Build cache is optional speed state; its presence does not qualify output. Keep cold/warm time, cache stats and stage/failure evidence. Native Jetson builds are too long to assume live in a one-CC demo; prebuild or rehearse a known warm path.

## Manager design consequences

Manager owns explicit attempt/dependency state and response collection; agents choose experiments, and the other team owns final lab provisioning. Implement a wait/status primitive against recorded attempts instead of rebuilding fragile shell polling. Preserve a completion record tied to process/container generation; do not equate vanished PID with completed science.

Submission/admission must pin context, requested runtime, actual platform, memory domain and guarantee class. Cgroup limits are not proven CUDA caps on either system. Preserve watchdog trigger, attempted action, observed termination and cleanup independently; a triggered threshold with exit zero is not automatically watchdog_killed. Zram policy and safety thresholds are host-specific and do not transfer verbatim to x86.

Durable result export needs a completeness manifest of the actual file graph and an explicit acknowledgement/failure domain. Git branch presence and narrative “all logs committed” failed to include referenced raw files. Our research copies improve preservation of what was committed, not evidence of an implemented host-failure-resilient store.

## Friday selection

**Tool-first:** a real JiuwenSwarm call to a verified profile/evidence tool, with useful normal output and one misleading-input rejection. **Component-first on Jetson:** use the Q4_K dispatch component, exact patch/build record and baseline/candidate/negative-control evidence; add a live same-image test only after owner/host readiness and rehearsal. **Optional extension:** agent → component → target-aware builder → Manager request → simple Docker fixture → assessed result. None requires a final sandbox product, a new loader, both hosts live, or universal optimization claims.
