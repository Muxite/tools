# What this campaign teaches us

**New evidence received:** [follow-up verification and corrections](followup-evidence/README.md) confirms up1 MUL_MAT passed and a historical live recovery rehearsal exists. Earlier unresolved statements below record the prior inspection state; do not use them as current negatives. Targeted reuse-hit/alias/graph tests and current integration readiness remain open.

Evidence scope: source and retained records from x86 commit `ecaa4b0d1ed134d598993ca9f26e21745b0bbd4e`, plus separate host runtime captures. Read [preservation and audit scope](README.md). No fresh GPU experiments were run here.

## Results worth keeping central

| Finding | Evidence and interpretation | Demo value |
|---|---|---|
| A real, small full-engine code gain exists | [D040](snapshot/campaign/decisions/D040-release-speed-and-pap-retraction.md). Saved job `job-85805b616c/att-1` has 24 clean completions. Same image, `GGML_CUDA_Q8_REUSE=0/1`, otherwise matched Q8_0 tg128 arguments. Medians 793.178 → 810.429 t/s, +2.1749%. | Strong example of component integration with bounded qualification, not a dramatic live speed claim. |
| Large runtime gains do not mean we wrote a faster engine | [D044](snapshot/campaign/decisions/D044-e1-cache-cpushare-frontier.md) and D045–D048 record cache/CPU-share/speculation and placement changes using upstream llama.cpp. D044 compares S2/C3 within up1, avoiding a simple cross-version speed comparison. | Recorded context supporting reuse rather than a custom scheduler/kernel rewrite. |
| Small proxies can select the wrong design | Granite static offload beat cache; Qwen caching changed the result. Granite→Qwen planner was about 7× pessimistic. Hybrid harness success reversed in full-engine testing. | Demonstrate measured applicability and a rejected candidate, rather than presenting one universal factory policy. |
| Mechanism engagement must precede timing | Static-hot patch never engaged; ngram produced zero drafts; one prompt terminated at the first token. | A tiny engagement/test CC can prevent a whole wasted campaign. |
| State belongs in the experiment contract | Cache-history-dependent output, mmap warm/cold differences, batch/verify-shape numerical floors. | Request needs reset/warmup/prompt-template policy, not just command + image. |
| Measurement needs host context | PAP provisional gain shrank from +9.8% to +1.5%; swap contaminated overnight arms; SMT was poor on this host. | Evidence and invalidation matter more than a polished speed chart. |
| Integration failures survive extensive unit testing | Flat/nested record mismatch, containerd identity confusion, missing ELF tooling, invalid UTF-8 crash, stale factory expectations. | Real saved external-tool outputs and producer/consumer contract tests are high-value reuse. |

Raw engine result and independent arithmetic are linked from [README](README.md); see [record-audit.json](record-audit.json).

## Manager design implications, ordered by observed cost

1. **Pinned submission, explicit attempts and evidence references.** Bind image identities, actual per-test model/input bytes, test definition, runtime flags/env, component revision and assessment policy. Preserve original request and each attempt; late/foreign/conflicting results cannot replace accepted evidence. Source: [Manager findings](snapshot/campaign/MANAGER-DESIGN.md), [lab adapter](snapshot/campaign/bin/lab).
2. **Separate execution, evidence completeness, cleanup and scientific assessment.** Exit zero is not numerical correctness. Interrupted coverage is not a pass. A timeout/cancel request is not proof the sandbox stopped. Reconcile owned work before replacement. Keep unscored/invalid/parser-error outcomes explicit.
3. **Evidence outside the disposable target, with a stated failure domain.** The adapter journals with fsync and exports with staged copying/hash checks. This supports sandbox/process-loss reasoning; same-host storage does not establish host-loss durability. `last_durable_bytes` based on file size/mtime is not a remote acknowledged trace offset. End-to-end crash-during-chain and power-loss guarantees remain unqualified.
4. **Observe measurement eligibility continuously.** Quiet process names missed swap; include swap-in/out, faults, pressure, CPU/IO contention, GPU occupancy and sample coverage. Polling at 0.25/0.5 seconds is an observed maximum of samples, not guaranteed true transient peak. Distinguish device-total and per-process memory. Own processes by PID/start identity or labelled container/cgroup; avoid broad `pkill -f`.
5. **Store large artifacts and redact before ordinary evidence export.** Disk was 94% full and important artifacts were only local. Separate content-addressed artifacts from Git metadata. Define retention and failure behavior when capture cannot continue. Redact ordinary logs at capture; handle any restricted originals under an explicit policy. Do not silently change bytes while retaining old hashes.
6. **Keep lab-provider ownership external.** We build the inference-engine image and declare requirements; the other team's lab agent chooses/provisions the test environment. Local Docker and offline x86/Jetson compatibility receipts do not prove remote lab delivery or acceptance. GPU concurrency remains procedural because the campaign explicitly removed its lock; no new locking policy was implemented here.

## A small initial CC portfolio grounded in work

| Family | Initial reusable unit | Reuse directly | Remaining work |
|---|---|---|---|
| Build | Source + patch stack → engine image + build record | [Build CC](snapshot/campaign/cc/build_engine/README.md), CMake, Buildx/Bake, ccache | Eliminate contradictory identity prose; transfer/receiver verification and target-base compatibility. |
| Test | Engagement and paired-quality assessment | Engine counters, perplexity/KLD tooling, [verdict](snapshot/campaign/cc/verdict) | Model-specific fixtures; reference floors; distinguish post-hoc diagnosis from frozen acceptance. |
| Test | Frozen matched runner + resource observations | Overnight runner, [resource observer](snapshot/campaign/cc/resource_observe), existing lab measurements | Pull ad hoc peak sampling and swap/fault controls into one owned contract; don't create another executor. |
| Profiling | Capture and interpret a bounded diagnostic | [Profiler wrappers](snapshot/campaign/cc/profilers), [Nsight analysis](snapshot/campaign/cc/nsys_decode) | Real capability checks and perturbation comparison; never report profiled time as ordinary speed. |
| Tools | Image handoff, model inspection, pinned fetch | [Handoff](snapshot/campaign/cc/engine_handoff), [model inspector](snapshot/campaign/cc/model_inspect), existing HF client | Real receiver exchange; hybrid/SSM model support; fetcher is still missing. |
| Methodology | Freeze → A/A → engagement → paired A/B → retain/reject | Five project skills reported in CLOSEOUT (outside this campaign-only source capture), plus retained decision and attempt records | Explicit measured applicability; predictions scored by model/host, no universal heuristic promotion. |
| Component | Q8 reuse; KV defect fix separately | [Component integration contracts](snapshot/campaign/cc/components/COMPONENTS.md), patch stack | Qualified Granite/base only. Rebase requires full requalification. Binary swap is exact-pair evidence, not general ABI compatibility. |

Not each script deserves a CC. Plan/cache/spec simulators stay labelled predictions. gpu_budget remains cooperative infrastructure, not a hard VRAM cap. Keep rejected hybrid/static-hot/PAP artifacts as useful negatives. BuildKit, Docker, llama.cpp and NVIDIA tools already supply most mechanisms; our useful code is binding contracts, collecting evidence and making results interpretable.

## Uncertainties and corrections before presenting

- **up1 correctness contradiction:** D044 says 2517/2517 MUL_MAT passed; CLOSEOUT explicitly says no backend-ops run. `artifacts/up1gate` contains six text captures, not that backend report. Use the weaker qualification until the raw report is located or testing is repeated.
- **Demo contradiction:** MANAGER-DESIGN says demo rehearsal repeated the chain. The supplied demo validation says Docker/live execution was NOT RUN, and its tracked output directory has no result.json. Prior adapter fault tests do exist, but they do not establish this script's live readiness or 5–8-minute timing.
- **Quality claims need narrower language:** a reference's own numerical floor explains a failed fixed gate, but post-hoc amendment is not a pre-registered pass. X2's teacher-forced KLD/verify-batch probe is not broad task-level or distributional equivalence of generated conversations. Preserve exact-output claims only on the prompts where observed.
- **Host heuristics are not general policy:** four threads, CPU-share 0.9, MTP n=3 and mmap are measured candidates on this host/model/workload. Do not publish “never SMT” or “cache default” as universal rules, particularly on Jetson UMA.
- **Factory tests:** 3 failing expectations are reported as stale; this explanation has not been independently rerun here. Fix and re-run before using the factory chain as Friday's dependency.
- **Reproducibility:** two sets of 20 runtime files matched in one pair of builds. That is valuable exact-pair evidence, not proof all future builds or image archives are reproducible.
- **Snapshots and state:** host HEAD and local origin ref matched, but the working tree had a modified evidence stream. Owner services being restored is reported in CLOSEOUT, not a fresh GPU/process-state audit here. No settings/services were changed.

This supersedes the earlier “no engine win yet” snapshot for the specific Granite Q8_0 evidence. It does not promote the whole campaign, remote lab, hard-memory-cap mechanism or Jetson lane to qualified status.
