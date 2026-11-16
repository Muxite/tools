# Single-file handoff: discover Lab Manager and CCs by improving inference

Prepared November 9, 2026. Send this entire Markdown file to the orchestrating coder agent. It supersedes the earlier demo-first prompt. It includes instructions, essential research context and reference URLs; no adjacent files are required. Original PDFs/source snapshots are not embedded, but direct upstream links and inspected revisions are included so references can be retrieved selectively.

**User priority:** determine the Lab Manager design and initial CC portfolio empirically by improving real inference. Build one reusable image-producing CC, discover a small profiling/test set and valuable tool/methodology/component CCs, then demonstrate a few by Friday, November 13. Preserve separate coding and test sandboxes and external crash-surviving control/evidence.

**Evidence boundary:** the research workstation collected sources, read code/papers and validated its package. It did not run target GPU, Incus/Docker, inference, profiling, current live CCs or crash-recovery qualification. Historical synthetic demonstrations are not new inference results. Do not report research recommendations as measured adoption benefits.

## How to use this file

Follow Part I as the task instructions. Use Part II as research leads, not a prescribed implementation. Establish the current campaign state before starting new work; preserve completed experiments and coordinate existing workers. Begin implementation on the development machine and verify real interfaces with the lab-agent owner.

# Part I — Orchestrator instructions

# Discover our Lab Manager and initial CC system by improving real inference

You are the orchestrating coding agent for an empirical inference-engine improvement campaign. Your most important job is to discover the Lab Manager design and initial set of useful Capability Capsules (CCs) by doing real engineering work on an existing model and inference engine. We want a real improvement and a reconstructable account of what made it possible. Friday's demonstration is a few selected results of this campaign, not its organizing objective.

Use the whole relevant body of methods: investigate sources and papers, profile, form hypotheses, change code/configuration/components, build images, test in the lab, compare outcomes, learn and iterate. Choose methods from evidence and adapt them to your role. Do not simply implement a tool catalog we prescribed, or stop when image delivery works. Delegate bounded work to coding/research/review agents where useful and preserve their actual assignments, activities and outputs.

## 1. Preserve these boundaries

There are two separate sandboxes:

1. **Coding sandbox:** the coding agent edits source, installs development dependencies, builds and instruments here.
2. **Test sandbox in our lab:** runs tests against the identified inference-engine image. It is disposable and may crash.

The product we build and send to our lab is the runnable inference-engine image, not the coding sandbox. The engine has its own launch interface; do not turn the whole engine into a CC.

The other team owns the lab agent and final sandbox choice/provisioning. Yes, their lab agent can build/provision the test sandbox from declared requirements. Agree the handoff with them; do not prescribe their Incus commands, privileged flags or final topology in our application manifest.

Our responsibility is discovering and implementing the useful core of Lab Manager and the initial CC system, including image building, then validating these through real inference-improvement work. Preserve a concrete image-and-input handoff, careful records, and test control/evidence that survive a test-sandbox crash. Any Lab Manager/controller code is deterministic coordination, not another reasoning lab agent. Collaborate with the other team on the boundary; their ownership of the lab agent does not remove our responsibility to determine what Lab Manager needs.

Use practical temporary coding and testing arrangements for development. They need adequate source/model/dataset/cache/trace/output storage and permissions, but are not the final platform specification.

## 2. Primary objective: discover by improving

Use an existing model as the fixed experimental target and aim to improve its execution through an inference engine. Primary target: `ibm-granite/granite-3.1-1b-a400m-instruct` on RTX5070Ti/48 GB RAM. Keep the model's task quality observable while improving measured latency, throughput, memory/resource use or another explicitly chosen execution objective. Changing model weights is not required; distinguish engine changes, representation/quantization changes and workload changes.

The two main outputs are:

1. **A justified Lab Manager design:** responsibilities, interfaces, scheduling/admission, experiment/attempt state, durable data, cancellation/recovery and actual implementation gaps, derived from observed needs.
2. **An initial CC portfolio:** the build CC, a small number of profiling/test CCs, useful tool and methodology CCs, and reusable component CCs incorporated into engine builds. Determine their boundaries and initial membership from work actually performed.

Pursue a real measured improvement. Establish a trustworthy baseline, explore different useful hypotheses, reject failures and iterate on promising candidates. Do not declare the campaign complete merely because a smoke test or handoff succeeds. If no improvement is supported within the available budget, report that plainly with failed hypotheses, blockers and the next best experiment; never alter tests to manufacture a win.

Treat the initial approximately one-day pilot as the first checkpoint, not a reason to freeze a narrow methodology. Continue staged work toward Friday, November 13, 2026 within available resources. Separate campaign/experiment/build/GPU time and model/agent costs so the owner can assess further work. Preserve time for synthesis and demo rehearsal.

## 3. Explore the relevant methods, then choose experiments

Study the entire Strata source as a reference system: inventory it broadly and trace relevant mechanisms deeply. Reverse-engineer composition, dependencies, routing, expert slots/residency, CPU/GPU work, memory tiers, state, kernels, instrumentation, builds and tests. Do not assume Granite is compatible with Strata or import its assumptions indiscriminately.

Survey and evaluate applicable methods, including runtime configuration, expert routing/placement/caching/prefetch, CPU/GPU and transfer overlap, memory/buffer/state management, prefill/decode paths, batching/concurrency, graph/launch overhead, kernels/fusion, precision/representation, instrumentation and measurement improvements. These are an exploration map, not a required implementation checklist. Use papers and the collected tools to expand the search where justified. Do not confine the work to one preselected optimization or repeatedly measure the same idea.

For each promising source/paper claim, record its original conditions, whether it applies here, the local hypothesis, a discriminating experiment, required observations and a result. Distinguish reproducing a claim from adapting its mechanism under different conditions. Begin with cheap screens, then deepen the useful directions.

Keep an evolving experiment portfolio. Prioritize expected information about the factory as well as potential engine gain; periodically identify neglected method families and explain why they are attempted, deferred or inapplicable. Avoid exhaustive blind parameter sweeps. A small fully GPU-resident model may not stress expert offloading: use clearly labeled focused component tests, trace replay or explicit supported constraints where useful, and never call those full-scale offloading evidence.

Freeze the relevant quality/workload/measurement policy before assessing a candidate. Use quick existing checks to screen, plus path-specific checks when changes affect decode, routing, KV/cache reuse or asynchronous state. Run unprofiled repeated matched baseline/candidate measurements and inspect A/A noise. Profile representative questions separately with Nsight Systems and targeted Nsight Compute; reuse saved reports. Do not score profiler replay timings as ordinary inference speed.

## 4. Discover and implement the initial CC portfolio

Use this functional taxonomy to organize discovery, not to prescribe package counts, algorithms, class boundaries or APIs:

| CC family | What to learn and produce |
|---|---|
| Build CC | A repeatable agent-invoked capability that consumes identified source/recipe/component inputs and produces the runnable engine image plus build evidence. This is an explicit initial deliverable. |
| Profiling/test CCs | A small cohesive set for useful quality/state checks, unprofiled measurement, bounded Systems/Compute capture and saved-report analysis; group operations by actual reusable task, not one CC per executable. |
| Tool CCs | Source/config/model inspection, trace/counter handling, data preparation, artifact/image handling or other independently useful operations revealed by the campaign. |
| Methodology CCs | Reusable agent instructions, experimental procedures, templates, decision rules or composed workflows learned from actual investigations. Include prerequisites, worked evidence, failure cases and limits; use executable helpers where they add value. |
| Component CCs | Reusable engine implementation assets with integration guidance. The right form may be snippets, source modules, classes/functions, libraries, kernels or binaries; determine it empirically. |

For component candidates, record interface/data shapes, supported model/layout/backend/precision, state and memory ownership, dependencies, build/ABI requirements, actual integration steps and tests. Package the agent instructions needed to incorporate the asset correctly. Demonstrate a real integrated candidate build and relevant test when feasible. Do not publish a supposed reusable component just because one source file can be copied.

Start with ordinary commands/scripts/existing tools, capture how they are used, and extract CC boundaries when those operations become understandable. Do not force every experiment to wait for packaging, but do not leave the final portfolio as hypothetical labels. Build the small useful set supported by observed work, including the build CC and a few tested profiling/test/tool/methodology examples. Identify promising components and integrate/qualify the valuable ones within budget.

For every initially needed capability, maintain a row with real motivating operations/experiment IDs, inputs/outputs/effects, reusable instructions or implementation, dependencies, tests/failures, evidence status, component incorporation versus external use, and recommendation: existing tool unchanged, thin adapter, new CC, combine with another CC, defer or reject. Distinguish demonstrated essentials from likely but untested needs. Do not claim the inventory covers every future engine; list remaining coverage gaps.

Judge a proposed CC by engineering usefulness and reusable boundary. Record repeated manual effort and friction, not merely tool-call frequency. Capture counterexamples where the proposed abstraction gets in the way. Revisit methodology/CC boundaries after the next experiment rather than treating the first design as final.

If the lab receiver is not ready, use a small deterministic reference adapter behind the agreed boundary for local integration testing so discovery can continue. Label it temporary. Never claim the actual team's lab accepted or executed a request it did not receive.

## 5. Inspect existing work before coding

Read applicable repository instructions and locate existing implementation surfaces. This single file contains the complete mission plus the research findings, source pins, useful links, handoff example and practical first steps below. You do not need a separate research bundle. The research behind it inspected 27 software candidates and collected 13 papers. Treat source review as a lead for qualification, never as a runtime result. Retrieve only the linked upstream references needed for the current task, recording their exact versions and any changes since the inspected pins.

The workshop asks for a private demo branch from the M1 release on AI4Research-Main. Last remote observation resolved `ai4research-m1` to `7b63ffd59cfae400a22d4ead1fd4209ea7982132`, while a local tag differed. Recheck remote identity, record the chosen base and use an independent demo checkout. Do not alter another agent's checkout or push/merge without authorization.

Current CCv2 was inspected separately at `2889a1d6342e9baa7721648eca196bbce79a31d4`. It is not present in the inspected M1 release and its branch deliberately removes older machinery. Do not cherry-pick its whole branch or scope-reset instructions into M1. Reuse the narrow necessary capability/client integration, or run it as an explicitly separate builder tool where appropriate. Demonstrate what actually works on the selected branch.

Another agent is already running the Granite/Strata campaign. Establish a concrete task/interface split, consume its source/build/measurement/decision records, and coordinate complementary experiments and component work. You may orchestrate or contribute additional bounded work with clear ownership; do not create a competing uncontrolled campaign or duplicate GPU measurements. Convert useful observed operations into our CC and Manager discoveries. If its logs are incomplete, repair prospective capture and mark historical gaps rather than inventing missing operations.

## 6. Create the temporary development path

Use the development machine, not the research workstation, for builds and GPU execution. Known target context: Ubuntu 24.04, Docker, RTX5070Ti, 48 GB system RAM, unrelated existing containers. GPU use is exclusive during tests; CPU/storage use may not be.

Inspect actual capacity and versions before setting CPU/RAM/PID/shared-memory/storage/capture limits. Leave headroom for host, controller and existing services. Persist coding source/worktrees, dependency/build caches, datasets and logs outside disposable writable container layers. Mount model/reference inputs read-only where practical. Keep credentials external and scoped.

Build through a controlled builder-side Docker/Buildx interface. Do not put host Docker/Incus sockets, coding-agent credentials or broad host mounts in the engine image or its test container. Do not stop unrelated containers, prune shared resources or change host-wide GPU/profiling settings automatically.

## 7. Implement the build CC, image making and transfer

Prefer a versioned Dockerfile with BuildKit/Buildx/Bake behind the build CC. Reuse the actual engine recipe or adapt a qualified reference. Choose engine adaptation or construction based on the experiment's needs; do not build a new engine merely for a presentation. The build CC should be useful across candidate iterations and record failures as well as successful images.

Primary model: `ibm-granite/granite-3.1-1b-a400m-instruct`. Verify the exact checkpoint/configuration and representation. Do not assume Strata executes Granite or that any model/GPU speed estimate is established.

The engine image contains executable/runtime dependencies. Keep model weights and datasets separate and identified unless a real requirement justifies baking them in. Avoid shipping the compiler and entire development environment unnecessarily.

Record source commit/tree/patch, base-image identity, dependencies/locks, build settings/tool versions, platform, image identity and executable hash. Retain build stdout/stderr and any genuine provenance output. BuildKit provenance availability depends on exporter/image store; inspect the exported object and do not pretend a Docker archive retained embedded attestations if it did not.

Default transfer: a Docker image archive plus SHA-256/size and expected loaded image/config identity. If an existing registry is used, use a pullable immutable manifest reference. Distinguish archive hash, Docker config ID, platform manifest digest and multi-platform index digest. A local `sha256:...` image ID alone is not a remotely pullable artifact.

## 8. Use existing capability mechanisms without constraining discovery

Engine-delivery inspection/handoff preparation and saved-report analysis are useful low-friction starting candidates, not the required focus or limits of the portfolio. Select useful tools from the actual experiment sequence.

Consume actual model configuration or bounded GGUF metadata, observed image/build evidence, declared invocation and logical input/output roles. Produce a readable compatibility/facts report, unresolved requirements, validation outcome and handoff YAML. Keep operations independently useful and group related capabilities in one CC where appropriate.

Check facts you can actually observe. Do not certify image contents from an agent's description or call metadata checks numerical correctness. A saved Nsight report-analysis capability is a valuable alternative if a real compatible report exists; use maintained report utilities before custom parsing.

Show an actual agent discovering/describing/invoking the capability and inspecting its receipt/artifacts. Existing finite CC image execution does not implicitly attach GPUs and may use `--pull=never`; do not widen the runner just to demonstrate a GPU benchmark CC. Existing source-change materialization produces a CC payload directory, not a general OCI-image builder.

## 9. Derive the Lab Manager design and handoff from execution

Keep a live responsibility/interface map of Builder, build CC, Lab Manager, other team's lab agent, test sandbox and evidence store. For every observed delay, failure, manual coordination step or missing record, decide whether it belongs in Manager policy, a callable CC, a component, the lab provider, or agent reasoning. Cite the operation that motivated the decision.

Derive requirements for asynchronous submit/status/cancel/result, exclusive GPU admission, queueing versus actual capacity, attempt identity, image/input staging, leases/ownership/reconciliation, timeout/retry policy, evidence export and coverage. Compare a small module with existing storage/dispatch against larger services; implement the minimum needed to exercise real experiments. Do not settle the design from diagrams alone, or build an unnecessary queue/registry/service stack.

Exercise representative duplicate delivery, engine/sandbox failure, interrupted control/export and recovery. Record the concrete request/result/lifecycle that worked and the unresolved boundaries. The other team owns reasoning/provisioning in its lab agent; we own identifying and validating Manager needs and an agreed integration boundary.

Use the inline handoff YAML in Appendix D as an illustrative draft, not a final schema or agreed team API. Resolve it against actual build and system behavior. Include only necessary fields:

- Handoff ID and version.
- Engine image transport, immutable identity, platform and build-record reference.
- Model, workload and optional tool-image identities.
- Supported argv and logical read-only inputs/writable outputs.
- Required GPU/runtime/tool capabilities and bounded resource/time requirements.
- Requested readiness/smoke/benchmark/profile checks and fixed policy identity.
- Expected evidence artifacts and external export/registration requirements.
- Unresolved information that blocks admission.

One engine image is enough; additional images need explicit real roles. Do not invent a service graph. The lab agent chooses/provisions a compatible test sandbox, accepts, rejects or requests information, then returns tracked status/result references. Receipt/acceptance is different from execution and passing tests.

Require hash/identity validation before expensive execution. Reject unresolved identities, incompatible platforms, unsupported requirements and unapproved mounts/controls. No arbitrary host shell scripts in YAML.

## 10. Test sandbox crashes must not destroy testing or evidence

Keep the test controller/Lab Manager and durable evidence outside the disposable test sandbox's failure boundary. A sidecar in the same outer instance is insufficient if that instance crashes or is deleted.

Before execution, durably save the complete request, image/build/model/workload/tool identities, budgets, job and attempt IDs, expected outputs and operation intent. Capture stdout/stderr and structured events continuously to external storage. Flush/rotate finalized trace segments at practical boundaries; preserve original profiler files and exported summaries.

When the test sandbox crashes:

- The external controller remains responsive and can run future tests.
- Already acknowledged durable logs/artifacts/trace segments survive and remain hash-verifiable.
- The active attempt becomes failed/interrupted/unknown as supported by observations, never an automatic pass.
- Record last durable sequence/time, expected/collected coverage and incomplete or unparseable trace files.
- Reconcile actual owned processes/instances and confirm old execution stopped before replacement work.
- Retry as a new attempt of the same identified image/workload with declared preparation/warmup repeated.
- Reject stale ownership or conflicting late results; preserve diagnostics without overwriting accepted evidence.

Do not promise preservation of data that was still buffered on GPU/in process/in an unfinished profiler report at crash. Make loss explicit and invalidate affected comparisons. If host power/storage loss is in scope, same-host directories alone are insufficient; state the actual protected failure domain and required independent storage.

Do not deliberately cause host OOM, driver resets or GPU faults on the shared server. Demonstrate a controlled engine failure and a controlled test-sandbox termination. The coding sandbox must remain separate and intact.

## 11. Record all work, tests and major operations as discovery data

Set up durable recording before substantive work. Use native Claude/Codex event streams/hooks where available and wrappers/process observation to cover commands and descendants. Test actual capture coverage; a logged shell invocation may hide background work.

Link campaign, agent/task, operation, build, release, job and attempt IDs. Record assignments, source changes, relevant configuration, command/working directory, start/end/duration, exit status, raw output/artifacts, tests and concise decisions. Include failed, skipped, blocked, timed-out and unknown cases. Capture consequential intent before execution and result afterward. Do not use private chain-of-thought as a deliverable.

Keep records outside the sandboxes whose crashes they must survive. Preserve raw native streams alongside normalized indexes; avoid concurrent-write corruption. Redact secrets and never dump credentials or entire environments. Missing recording must be visible; repair it before starting further consequential experiments.

For each experiment, retain the method attempted, tool/component dependencies, preparation/build/test/analysis costs, failures and interpretation. Link observations to proposed CCs and Manager decisions. Maintain negative results and discarded components/methodologies. This activity record is the empirical basis for deciding the initial system; it is a first-class campaign deliverable, not retrospective documentation written just before Friday.

## 12. Acceptance: useful discovery, real improvement work, then demo

Deliver three connected results:

1. **Inference campaign:** pinned baseline, breadth/applicability map, source-backed hypotheses, actual candidate changes and component integrations, quality checks, matched raw measurements and the best supported improvement. Make rejected/inconclusive results and remaining gaps equally inspectable. Do not claim improvement without evidence or substitute a changed workload for a win.
2. **Initial system definition:** justified Lab Manager design plus the initial CC inventory across build, profiling/test, tools, methodologies and components. Identify what is implemented and qualified, reused, still missing, unnecessary or deferred, with references to actual work. Include integration instructions and tests for incorporated components.
3. **Friday demonstration:** select a few capabilities that proved valuable during the campaign. Show a real agent invoking them, the engine image they help produce/test, and an observable result. Choose the examples from strongest evidence rather than building a separate polished toy. Keep the demo 5–8 minutes; pre-stage heavy downloads/compilation and label earlier recordings.

For the image/lab/recovery part, prove with real artifacts:

1. Agent uses the useful CC/tool and retains its actual receipt.
2. Engine image builds and its exported bytes/loaded identity match recorded expectations.
3. Handoff is generated from real observations; a missing identity or tampered archive is rejected.
4. Separate test sandbox executes one short real engine smoke test under the agreed lab interface.
5. Controlled test-sandbox termination leaves external control and already exported evidence intact; partial coverage is explicit.
6. Old execution is confirmed stopped, then a distinct new attempt runs. No duplicate execution from repeated request delivery.
7. Coding work, build history, test history and results remain reconstructable after restart.

Use small fixtures for plumbing tests but label them. They do not replace the real optimization campaign. Use Nsight Systems and targeted Nsight Compute where applicable and qualify/report any unavailable functionality. A generation smoke test is not a model-quality guarantee.

Deliver the campaign evidence, best candidate engine image, build CC, a small tested initial profiling/test set, useful tool/methodology CCs, empirically justified component assets/integration guidance, Lab Manager design and exercised interfaces, private demo branch and rehearsed runbook. Separate live results, earlier recordings, fixtures and untested integration. Reuse existing software aggressively; add infrastructure only where an observed need justifies it.

Begin with a concise task split, evidence-capture check and reconstruction of the existing campaign's baseline/current work. Then run the engineering loop, periodically synthesize what it teaches us about the Manager and CCs, and continue autonomously. Ask only for genuinely missing host access, credentials through the approved mechanism, or unresolved ownership/budget decisions that block execution. The central question throughout is: **what did real inference-improvement work teach us to build, reuse or avoid?**


# Part II — Research findings and implementation leads

## Appendix A — Known facts and integration traps

### Model and hardware

- Development/test target is Ubuntu 24.04 Server, Docker installed, RTX5070Ti and 48 GB host RAM. Other containers are running. Owner promises exclusive GPU use during tests; that does not establish exclusive CPU, RAM or storage access. Discover actual capacities and budgets.
- Primary model is [IBM Granite-3.1-1B-A400M-Instruct](https://huggingface.co/ibm-granite/granite-3.1-1b-a400m-instruct). The [configuration](https://huggingface.co/ibm-granite/granite-3.1-1b-a400m-instruct/raw/main/config.json) inspected identifies `GraniteMoeForCausalLM`, 24 layers, hidden size 1024, 32 experts/layer, eight experts/token, eight KV heads and BF16 weights. Pin the actual checkpoint, tokenizer, template and representation used; the linked main branch is mutable.
- [llama.cpp's Granite MoE implementation](https://github.com/ggml-org/llama.cpp/blob/master/src/models/granite-moe.cpp) is a plausible reference path; qualification remains necessary. No Strata–Granite compatibility or 5070Ti token-rate estimate was established.
- Small fully resident Granite execution can expose routing and engine overhead, but will not naturally reproduce the pressure of large-model expert offloading. Distinguish real model execution, controlled component tests and replay/simulation. CPU-offload flags are not automatically adaptive expert-slot management.

### Strata source reference

Use [Strata at ffa80d73133ea5c548aefe57889a16e8085a938f](https://github.com/Niko1221/Strata/tree/ffa80d73133ea5c548aefe57889a16e8085a938f) as the initial research pin. A different local checkout had `c62d5e3a15b40ea51c96aae9e8d36928965f53ab`; do not silently conflate them. Inspect current repository instructions before editing.

Useful concrete seams in the pinned tree:

| Source location | What to investigate and why |
|---|---|
| `src/core/layer.cpp` | Router outputs expert IDs/weights; expert combination is another step. Routing, residency and dispatch are different facts. |
| `include/strata/core/expert_cache.hpp` | Residency table and slot storage map `(layer, expert)` to location. Storage/cache policy is not itself expert computation. |
| `include/strata/core/expert_source.hpp` | Adapter between activations, routed experts, CPU/GPU execution and memory. Comments identify stale-data and double-weighting hazards. |
| `include/strata/core/hit_hook.hpp` | Two-phase resident-GPU work and CPU misses illustrate overlap and dependency boundaries. Historical component-time improvements did not automatically improve token latency. |
| `strata_control/journal.py`, `calibration_jobs.py` | Operation identity, bounded local journals, worker ownership and cancellation patterns. A running record after a crash is not proof a worker is alive. |
| `strata_control/engine_component.py`, `packaging/` | Native engine packaging, hashes and compatibility checks. Preserve native product metadata instead of relabeling it a CC. |
| `tests/`, `serve/test_fatal_recovery.py`, CPU/CUDA component tests | Existing inexpensive fixtures and examples of failure/reload/state behavior. Fake-engine tests are not inference tests. |

Source comments reporting measurements are upstream claims under their conditions, not reproduced campaign results. Useful initial component hypotheses include expert-weight access, residency mapping, trace extraction, dispatch integration and state-safe buffer reuse; choose only where actual investigation establishes a reusable boundary.

### CCv2 and M1 are not the same branch

The workshop repository is [Stellven/jiuwenswarm](https://github.com/Stellven/jiuwenswarm). The remotely observed M1 release commit was `7b63ffd59cfae400a22d4ead1fd4209ea7982132`. The separately inspected CCv2 implementation was `2889a1d6342e9baa7721648eca196bbce79a31d4` in that project. Recheck access and revisions; this file supplies no credentials and does not assert those refs remain unchanged.

Important inspected behavior:

- `docs/architecture/ccv2/README.md` and `jiuwenswarm/ccv2/agent_mcp.py` expose `cc_list`, `cc_describe`, `cc_material`, `cc_call`, service lifecycle and artifact registration. Use real receipts and inspect state/completeness/diagnostics.
- `demo/ccs/workspace_inspect/cc.yaml` is a small finite native capability example; `demo/ccs/compute_service/build_image.py` demonstrates building an application and recording its local image/config ID. Its payload is synthetic compute, not inference.
- `jiuwenswarm/ccv2/ccv2.py` finite image execution uses read-only mounts/filesystem, output staging, dropped capabilities and no implicit pull. It accepts workspace mounts, not arbitrary device/process handles. There is no implicit `--gpus` merely because a declaration names GPU use.
- Native CC bindings are trusted local commands, not an OS security sandbox. Controlled builder-side Docker access must not leak into the engine/test container.
- `jiuwenswarm/ccv2/source_build.py` verifies a pinned Git change and materializes a CC payload/package. It is not a general OCI image-builder interface. It checks base/tree identity and rejects unresolved submodules/LFS rather than inventing complete inputs.
- CCv2 is absent from the inspected M1 release. Its own branch deliberately removed older M1 machinery; importing that entire branch is not an acceptable way to add one capability. Reuse/port narrowly or explicitly run a separate client tool, preserving the workshop branch requirement.
- Earlier replay behavior depended on bound resource state; do not promise that arbitrary state changes preserve call identity. Do not confuse MCP transport success, successful execution and passing assessment.

## Appendix B — Reuse candidates and what remains ours

These are candidates from research, not a mandatory tool stack. Use actual experiment friction to select them. No percentage of coding effort saved has been measured.

| Candidate and primary reference | Reusable contribution | Boundary or caution |
|---|---|---|
| [Incus API](https://linuxcontainers.org/incus/docs/main/rest-api/), [events](https://linuxcontainers.org/incus/docs/main/events/), [GPU](https://linuxcontainers.org/incus/docs/main/reference/devices_gpu/), [Docker nesting](https://linuxcontainers.org/incus/docs/main/faq/) | Outer instance lifecycle, async operations, projects and device setup. Lab-agent team can build/provision sandbox. | Incus operation IDs are not experiment IDs. Lost events need reconciliation. Nested GPU/profiler path is unqualified; final sandbox policy is lab-owned. |
| [Docker Python SDK](https://docker-py.readthedocs.io/en/stable/containers.html) | Inner-container launch, inspect, logs, wait, resource settings and stop. | Client timeout is not stop confirmation. Our/lab adapter still owns authorization, resource identity and cleanup scope. |
| [Buildx Bake](https://docs.docker.com/build/bake/), [cache backends](https://docs.docker.com/build/cache/backends/) | Declarative repeated image builds, build targets and cross-machine cache. Strong build-CC substrate. | Record actual source/base/build outputs; no guaranteed bitwise reproduction. Heavy builds interfere with timed GPU jobs. |
| [BuildKit provenance](https://docs.docker.com/build/metadata/attestations/slsa-provenance/) | Build facts/attestations and dependencies recorded by build tooling. | Exporter and image store affect retention. Verify actual export; provenance is not correctness or a complete reproducibility proof. |
| [ORAS](https://oras.land/docs/quickstart/) | Push/pull/discover non-image OCI artifacts and attach manifests/reports to image subjects. | Optional. Archive plus hashes is enough initially. Registry/referrer/authentication availability needs checking. |
| [Nsight Systems analysis](https://docs.nvidia.com/nsight-systems/AnalysisGuide/index.html) | Maintained statistics scripts, exports and post-processing recipes. Avoid writing a raw trace parser first. | Keep raw report and tool version. NVTX host duration is not GPU completion; expert identities require engine observations. |
| [Nsight Compute Python report API](https://docs.nvidia.com/nsight-compute/PythonReportInterface/index.html), [profiling guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html) | Read selected kernel metrics and reports programmatically. | Record invocation, units, replay and cache settings. Counter permissions belong to qualified lab setup; diagnostics are not ordinary speed results. |
| [Compute Sanitizer](https://docs.nvidia.com/compute-sanitizer/ComputeSanitizer/index.html) | Existing memcheck/synchronization/race diagnostics. | Tool/path support must be verified. Do not score sanitizer overhead as engine performance. |
| [GenAI-Perf](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html) | Serving load generation and request/token measurements. | Requires a compatible server adapter. It is not numerical quality evaluation or a direct-executable benchmark. |
| [KernelBench](https://github.com/ScalingIntelligence/KernelBench) | Timing/evaluation helpers, profiling entry points and adversarial test examples. | Kernel-level scope; current EVAL.md labels some protections WIP. Inspect real tests rather than assuming all checks are complete. |
| [BenchExec](https://github.com/sosy-lab/benchexec) | Process-tree accounting, Linux resource-control and timeout examples. | Solver-oriented CPU framework; nested cgroups, GPU memory and asynchronous CUDA require separate qualification. |
| [OpenTelemetry resilience](https://opentelemetry.io/docs/collector/resiliency/) | Existing buffering/retry transport and file-backed persistent queues. | Not the accepted scientific evidence ledger. Persistent volumes do not guarantee no loss/duplicates or replace backups. |
| [Testcontainers Python](https://testcontainers-python.readthedocs.io/en/latest/) | Disposable integration-service fixtures, readiness and cleanup. | Not Incus isolation, GPU exclusivity or stale-worker fencing. Run against an appropriately scoped daemon. |
| [dstack tasks](https://dstack.ai/docs/concepts/tasks/), [fleets](https://dstack.ai/docs/concepts/fleets/), [isolation](https://dstack.ai/docs/guides/tenant-isolation/) | On-prem SSH fleets, GPU jobs/queues and lifecycle may remove substantial custom scheduling. | Inspected isolation guide assumes mutual trust and documents host SSH/networking access. Adds a server and policy model; not a drop-in Incus guarantee. |
| [Dagger Python](https://docs.dagger.io/reference/sdks/python/) | Programmable shared container build/test pipelines. | Compare against Bake before adopting a second pipeline engine; not a durable experiment manager. |
| [Temporal Python](https://docs.temporal.io/develop/python) | Durable workflow history, retries, worker and cancellation patterns. | Adds service/replay/versioning obligations. Activity retries still need idempotent external effects; cancellation does not prove GPU work stopped. |
| [SkyPilot managed jobs](https://docs.skypilot.ai/en/latest/examples/managed-jobs.html) | Controller/recovery patterns and remote GPU scheduling examples. | Relaunching a job is not resuming a partially measured arm. Additional fleet/control plane may exceed our current needs. |
| [MLflow](https://mlflow.org/docs/latest/ml/tracking/) | Metrics/history/artifact browsing. | Optional view over retained evidence; tracking success is not accepted quality/performance evidence. |
| [restic](https://restic.readthedocs.io/en/stable/040_backup.html) | Ordinary evidence/ledger backup and restore. | Quiesce/export state consistently; restored files are not live CUDA state or proof old execution stopped. |
| [ReproZip](https://docs.reprozip.org/en/latest/) | Trace dependency/file access and package command-line experiments. | Linux permissions, secret capture and redistribution need care. Cannot package target GPU/host driver state. |
| [Popper](https://github.com/getpopper/popper) | Reproducible container-workflow conventions/examples. | Useful pattern; don't add another runner unless it removes a real gap. |
| [MLPerf LoadGen](https://github.com/mlcommons/inference/tree/master/loadgen) | Load-generator/SUT separation and explicit scenarios. | Using it does not make our Granite case an official MLPerf result; full suite is not necessary for Friday. |

Read the pinned source examples in Appendix F selectively before reuse. Root project licenses do not automatically cover every dependency, model or documentation/tool binary. Do not redistribute NVIDIA executables or proprietary material based on a GitHub project's unrelated license.

### Concrete code/test locations worth opening first

| Project | Locations inspected or selected |
|---|---|
| Incus | `client/operations.go`, `client/incus_instances.go`, `test/suites/container_devices_gpu.sh`, `test/suites/projects.sh`, `doc/rest-api.yaml` |
| Docker SDK | `docker/models/containers.py`, `docker/api/container.py`, `tests/integration/models_containers_test.py` |
| Buildx/BuildKit | `bake/bake.go`, `tests/bake.go`; `docs/attestations/slsa-provenance.md`, `client/client_test.go` |
| ORAS | `cmd/oras/root/push.go`, `attach.go`, `push_test.go`, `attach_test.go` |
| KernelBench | `src/kernelbench/eval.py`, `timing.py`, `profile.py`, `kernel_static_checker.py`, `unit_tests/test_eval_adversarial.py`, `unit_tests/test_eval_timing.py` |
| OTel | `exporter/exporterhelper/README.md`; contrib `extension/storage/filestorage/README.md`, `client_test.go` |
| dstack | `mkdocs/docs/guides/tenant-isolation.md`, `mkdocs/docs/concepts/tasks.md`, `src/dstack/_internal/server/background/pipeline_tasks/runs/active.py`, termination tests |
| Testcontainers | `src/testcontainers/core/container.py`, `tests/core/test_container.py` |
| Fiddler | `src/fiddler/infer.py`, `mixtral.py`, `benchmarks/latency.py`, `microbench.py` |
| MoE-Infinity | `moe_infinity/memory/expert_tracer.py`, `expert_prefetcher.py`, `core/prefetch/expert_residency.cpp`, `tests/cpp/unit/prefetch/test_expert_residency.cpp` |
| FlexGen | `flexllmgen/flex_opt.py`, `pytorch_backend.py`, `compression.py` |

## Appendix C — Papers as experiments, not promised speedups

Read selectively. For each usable claim, record original conditions, local applicability, experiment and evidence. The results of these papers were not reproduced here.

| Paper / original reference | Design question |
|---|---|
| [Reliable Benchmarking: Requirements and Solutions](https://www.sosy-lab.org/research/pub/2019-STTT.Reliable_Benchmarking_Requirements_and_Solutions.pdf) | What must controlled resource/process measurement guarantee? |
| [Serving DNNs like Clockwork](https://arpangujarati.github.io/pdfs/osdi2020_paper.pdf) | Which decisions should a central controller own to preserve predictable execution? |
| [Microsecond-scale Preemption for Concurrent GPU-accelerated DNN Inferences](https://ipads.sjtu.edu.cn/_media/publications/reef-osdi22.pdf) | How is GPU preemption different from canceling a lab job? |
| [MLPerf Inference Benchmark](https://arxiv.org/pdf/1911.02549) | How should the load generator remain independent from the system under test? |
| [KernelBench: Can LLMs Write Efficient GPU Kernels?](https://arxiv.org/pdf/2502.10517) | How can tests and measurements guide iterative agent work? |
| [The Popper Convention](https://raw.githubusercontent.com/systemslab/popper-paper/master/paper/paper.pdf) | How can an experiment be an inspectable executable workflow? |
| [Fiddler: CPU-GPU Orchestration for Fast Inference of Mixture-of-Experts Models](https://arxiv.org/pdf/2402.07033) | What observations distinguish transfer overhead from CPU expert work? |
| [MoE-Infinity: Offloading-Efficient MoE Model Serving](https://arxiv.org/pdf/2401.14361) | Which expert activation traces support prefetch/residency decisions? |
| [FlexGen: High-Throughput Generative Inference with a Single GPU](https://arxiv.org/pdf/2303.06865) | Which memory-tier policies and batching assumptions must a result preserve? |
| [PowerInfer: Fast Large Language Model Serving with a Consumer-grade GPU](https://arxiv.org/pdf/2312.12456) | What does activation-aware heterogeneous execution imply for tool inputs? |
| [Efficient Memory Management for Large Language Model Serving with PagedAttention](https://arxiv.org/pdf/2309.06180) | Which cache/state policies must images and experiments identify? |
| [Gandiva: Introspective Cluster Scheduling for Deep Learning](https://www.usenix.org/system/files/osdi18-xiao.pdf) | How can measured job behavior inform scheduling rather than assumptions? |
| [ReproZip: The Reproducibility Packer](https://www.theoj.org/joss-papers/joss.00107/10.21105.joss.00107.pdf) | How can accessed dependencies be discovered without guessing? |

Practical applicability notes:

- Fiddler's inspected README describes a research prototype supporting 16-bit Mixtral-8x7B, with CPU/AVX caveats. It is a mechanism/microbenchmark reference, not a drop-in Granite backend.
- MoE-Infinity supplies concrete request/expert tracing, prefetch and residency code/tests. The present repository snapshot has evolved beyond the original paper; pin the version and distinguish simulation, component and end-to-end findings.
- FlexGen emphasizes latency-insensitive high-batch throughput. Do not transfer those claims to single-request interactive MoE decode.
- PowerInfer activation sparsity is not synonymous with MoE expert routing; KV paging in PagedAttention is not expert-weight caching. Keep terminology/counters separate.
- REEF demonstrates genuine GPU scheduling/preemption mechanisms under platform-specific assumptions. Do not deploy its driver/runtime experiments on the shared host or call a container stop microsecond GPU preemption.
- Clockwork's actual artifact locator is https://gitlab.mpi-sws.org/cld/ml/clockwork (from the PDF appendix). A guessed GitHub locator failed; no verified Clockwork source pin was obtained. Use the paper for design inspiration unless you can independently retrieve/verify its artifact.
- KernelBench's `fast_p` combines correctness with a speed threshold, a useful distinction. Reuse helpers only after checking timer semantics and adversarial behavior under the selected version.

## Appendix D — Inline proposed handoff YAML

This is deliberately incomplete and not dispatchable. It is an illustrative conversation with the lab-team agent, not a final CC schema, ontology or team-approved API. Fill actual values from observed files and supported behavior. Required `null` fields and unresolved requirements must prevent dispatch. The lab agent chooses and provisions the test sandbox.

```yaml
# ILLUSTRATIVE, INCOMPLETE, NOT DISPATCHABLE. This is not a final team API or CC declaration.
format: engine-lab-handoff-draft/0
status: draft
handoff_id: granite-demo-to-be-assigned
release:
  role: inference-engine
  platform: linux/amd64
  transport:
    kind: docker-archive
    artifact: engine-image.docker.tar
    sha256: null
    bytes: null
  expected_image_config_id: null
  build_record: build-record.json
  executable_sha256: null
inputs:
  model:
    repository: ibm-granite/granite-3.1-1b-a400m-instruct
    revision: null
    manifest: model-manifest.json
    manifest_sha256: null
  workload:
    artifact: workload.json
    sha256: null
invocation:
  argv: null
  mounts:
    - {input: model, access: read-only, role: model-files}
    - {input: workload, access: read-only, role: workload}
    - {role: results, access: write}
sandbox_requirements:
  os: linux
  gpu: {vendor: nvidia, count: 1}
  required_runtime_compatibility: null
  network_after_staging: none
  isolation_and_provisioning_owner: lab-team
  resource_limits: null
tests:
  requested: [readiness, generation-smoke]
  policy_reference: null
  profiling: {requested: false, tool_and_version: null}
evidence:
  control_and_durable_storage_outside_test_sandbox: required
  outputs: [stdout.log, stderr.log, events.jsonl, result.json, artifact-manifest.json]
  crash_outcome: interrupted-attempt-with-partial-coverage
  resume: new-attempt-after-confirmed-stop
unresolved:
  - Fill actual image, executable, model and workload identities from observed bytes.
  - Confirm supported engine argv, CUDA compatibility, limits and test policy.
  - Agree lab acknowledgement/status/result transport with its owner.

```

A receiver acknowledgement should distinguish `received`, `accepted`, `rejected`, and `needs-information`. Later execution status and test verdict are separate. The Manager should retain both submitted intent and effective execution identities/configuration.

## Appendix E — Evidence-based discovery artifacts

Do not implement a large schema platform to start. Ordinary JSONL/JSON/YAML/CSV and versioned files are sufficient where the existing system has no appropriate interface. Use stable IDs and raw artifact references. The following records describe needed meaning; adapt serialization to real interfaces.

### Operation record

Identify campaign, agent/task, parent operation, operation, build/release or experiment/attempt, tool/version, working directory, safe command/configuration, input references, start/end timestamps, duration, outcome/exit status, output references and evidence gaps. Persist intent before consequential work and outcome afterward. Missing outcome remains unknown. Keep unredacted credentials out of artifacts. Capture background descendants or mark coverage limits.

### Experiment record

Include the question/source claim, rationale for trying this method, baseline and candidate identities, component changes, workload/quality/measurement policy, resource state, preparation/warmup, repetitions, raw samples, correctness/state outcomes, trace references/coverage, decision and next question. Capture setup/build/run/analysis cost and dead ends.

### CC discovery row

Include family, independently useful purpose, actual motivating operations/experiments, inputs/outputs/effects, dependencies/state, code and/or reusable methodology, candidate boundary, reuse versus new implementation, tests/failures, component integration evidence, current qualification and remaining gaps. Group coherent capabilities; do not make a capsule for every command. Retain rejected abstractions and why they failed.

### Component integration record

Record supplied snippet/module/library/kernel/binary and its version, required agent instructions, interface/data shape/layout/precision/backend/ABI assumptions, state ownership/lifetimes, dependencies, integration patch, actual consumer build/image and tests. A binary without its integration contract or a snippet that only worked once is not yet a useful reusable component.

### Lab Manager decision record

Link each design choice to observed operations/failures: what the Builder needed, what the lab agent already provides, the simplest adequate Manager responsibility, alternatives/reuse considered, observed adapter effort, implemented behavior and open qualification. Cover asynchronous jobs, actual GPU admission versus queue depth, attempts, ownership/fencing, image/input transport, result registration, cancellation, export interruption, reconciliation and cleanup.

### Crash evidence acceptance

The declared failure domain is initially the disposable test sandbox/process, not arbitrary host loss. Store controller state and durable acknowledged evidence outside that sandbox. Verify preserved bytes after a controlled sandbox termination. Last durable segment/time, missing interval, partial report validity and finalization status must be explicit. A new attempt does not inherit a claim of uninterrupted successful measurement. If host loss is also required, arrange a genuinely independent storage/control boundary and test it separately.

## Appendix F — Inspected source revisions

These commits identify source snapshots reviewed/collected on November 9, 2026, not supported release recommendations. Verify required behavior at your chosen dependency pin and check applicable license files. Source examples are leads; no downloaded code was run by the research task.

| Project | Inspected immutable source |
|---|---|
| benchexec | [`fbd04593289bba1e586b9432101f7cca60eef79a`](https://github.com/sosy-lab/benchexec/tree/fbd04593289bba1e586b9432101f7cca60eef79a) |
| buildkit | [`24736c239527cde8a26e897380507a4ec5402c70`](https://github.com/moby/buildkit/tree/24736c239527cde8a26e897380507a4ec5402c70) |
| buildx | [`b8a908fd6b0f8d66b52e7ea39c1acc96435eceff`](https://github.com/docker/buildx/tree/b8a908fd6b0f8d66b52e7ea39c1acc96435eceff) |
| dagger | [`e18cc07cd4ec04e09439c98aa8291d842f84dae0`](https://github.com/dagger/dagger/tree/e18cc07cd4ec04e09439c98aa8291d842f84dae0) |
| docker-sdk | [`e734fd5a5508bc1062a28a51dc2f31ae47af7a2f`](https://github.com/docker/docker-py/tree/e734fd5a5508bc1062a28a51dc2f31ae47af7a2f) |
| dstack | [`6d70e5813af7ea762ed7316951419e61fbf882f4`](https://github.com/dstackai/dstack/tree/6d70e5813af7ea762ed7316951419e61fbf882f4) |
| fiddler | [`227715bfd6e8c731b29548eab01d9919c4fe9564`](https://github.com/efeslab/fiddler/tree/227715bfd6e8c731b29548eab01d9919c4fe9564) |
| flexgen | [`004ffef82b46e8dc8685c55d0cdda650bdaf1269`](https://github.com/FMInference/FlexGen/tree/004ffef82b46e8dc8685c55d0cdda650bdaf1269) |
| genai-perf | [`24f6b9af4db5f7bba335b622ab776ef261a66fc3`](https://github.com/triton-inference-server/perf_analyzer/tree/24f6b9af4db5f7bba335b622ab776ef261a66fc3) |
| incus | [`9822d70101275f3dcdc06d50e6f6c2660b1abf19`](https://github.com/lxc/incus/tree/9822d70101275f3dcdc06d50e6f6c2660b1abf19) |
| kernelbench | [`423217d9fda91e0c2d67e4a43bf62f96f6d104f1`](https://github.com/ScalingIntelligence/KernelBench/tree/423217d9fda91e0c2d67e4a43bf62f96f6d104f1) |
| mlflow | [`af4a5aa5e6c54abf40512aac861693540d700c6f`](https://github.com/mlflow/mlflow/tree/af4a5aa5e6c54abf40512aac861693540d700c6f) |
| mlperf | [`3fbc329939999c13d0a7b5e67fb2092287e06047`](https://github.com/mlcommons/inference/tree/3fbc329939999c13d0a7b5e67fb2092287e06047) |
| moe-infinity | [`fc51c95bed9883ad08e6cafa67bc1074da34738e`](https://github.com/TorchMoE/MoE-Infinity/tree/fc51c95bed9883ad08e6cafa67bc1074da34738e) |
| oras | [`0f52f9a467842af2534559d609f49a0d1d140bc4`](https://github.com/oras-project/oras/tree/0f52f9a467842af2534559d609f49a0d1d140bc4) |
| otel | [`ba211217a132e28bd8bf5b8e19778abcaa60bf84`](https://github.com/open-telemetry/opentelemetry-collector/tree/ba211217a132e28bd8bf5b8e19778abcaa60bf84) |
| otel-contrib | [`a87899c1ebb8c5acc682257bf518fa02e98453e3`](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/a87899c1ebb8c5acc682257bf518fa02e98453e3) |
| popper | [`aa3f3b5d7e1374fcd4ae2bd3b12ec9db936d0e33`](https://github.com/getpopper/popper/tree/aa3f3b5d7e1374fcd4ae2bd3b12ec9db936d0e33) |
| reef | [`8750974f2d6655525a2cc317bf2471914fe68dab`](https://github.com/SJTU-IPADS/reef-artifacts/tree/8750974f2d6655525a2cc317bf2471914fe68dab) |
| reprozip | [`44687ce73efe7a889bf7a1ea982258e2d965c766`](https://github.com/VIDA-NYU/reprozip/tree/44687ce73efe7a889bf7a1ea982258e2d965c766) |
| restic | [`c734245fd3ae9bcac8ab3aaafb4482d4b5d0ae92`](https://github.com/restic/restic/tree/c734245fd3ae9bcac8ab3aaafb4482d4b5d0ae92) |
| skypilot | [`f3a7247ff986ad810a6656dba3577ced72f1f8e9`](https://github.com/skypilot-org/skypilot/tree/f3a7247ff986ad810a6656dba3577ced72f1f8e9) |
| temporal | [`c46e6156694e93a12d6e666cec1691fd02a067a7`](https://github.com/temporalio/samples-python/tree/c46e6156694e93a12d6e666cec1691fd02a067a7) |
| testcontainers | [`6146aa1170f415fcc825ed9bddc4eacbeb937a12`](https://github.com/testcontainers/testcontainers-python/tree/6146aa1170f415fcc825ed9bddc4eacbeb937a12) |

## Appendix G — Start without the research bundle

1. Reconstruct what the existing agent has already built/run and identify current source/model/workload/image identities. Keep its completed work; establish a nonconflicting task split.
2. Verify capture of a successful operation, a failed operation and a background child, outside disposable sandboxes. Mark historical gaps.
3. Reproduce or qualify the actual baseline. Record available environment/resources, quick quality/state checks, unprofiled repeatability and a representative profile where useful.
4. Choose a varied, evidence-led experiment portfolio. Use source/paper mechanisms to expand it; build candidates via the reusable build CC and run them in the separate test sandbox through the agreed lab boundary.
5. After each useful iteration, update the Manager design and CC/component/methodology inventory with actual evidence. Keep ordinary tools where wrappers add no value. Do not postpone all synthesis until Friday.
6. Select a few proven capabilities and the strongest supported engine result for the 5–8-minute demonstration. Keep crash/evidence behavior inspectable and report unqualified integration honestly.

Do not wait for the full bibliography to be read or every potential tool to be packaged. The core is useful autonomous engineering that reveals the system we need. This one-file handoff is enough to begin; follow primary links only when they answer the next concrete question.

## Appendix H — New Strata study: evidence and useful questions

This continuation keeps the user's focus central: the real improvement campaign should determine Manager and initial CC needs; these are candidate seams, not a prescribed catalog. The maintained notebook now preserves this priority and the sandbox/ownership/crash distinctions in its current entrypoints. No notebook or research bundle is required to use this file.

### Observed here, distinct from model results

At Strata `ffa80d73133ea5c548aefe57889a16e8085a938f`, **23 existing upstream CPU-only tests passed**: `tools.test_make_profile` (7), `tools.test_make_profile_mix` (2), `tools.test_bench_eviction` (14). Commands were `python -B -m unittest -v MODULE` with bytecode disabled; the source's tracked state stayed unchanged. They use synthetic profiles/traces/cache policies, not an engine/GPU performance run.

A bounded probe wrote seven incomplete bytes to a temporary trace; both `make_profile.read_trace` and `bench_eviction.read_trace` returned empty results without reporting truncation. Another probe observed the default tuning `machine_identity()` keys (`cpu_count`, `machine`, `processor`, `release`, `system`) and `incomparable_reasons({}, {}) == []`.

An additional `tools.test_conversation_cache_parity` suite was **blocked during import by absent `jinja2`**, before actual test cases ran. The unittest loader's single failure is not a model test. Qualify dependencies in the development environment; do not infer that the state gate or engine failed. Raw logs and full source/hash receipts were retained by the research task, but this one-file handoff makes no runtime claim beyond these described CPU observations.

### New reuse/consideration leads

All paths below are relative to the [inspected Strata revision](https://github.com/Niko1221/Strata/tree/ffa80d73133ea5c548aefe57889a16e8085a938f). Retrieve the exact file at that revision when needed.

| Seam | Evidence and implication |
|---|---|
| No-op transformations | `tools/make_profile.py` preserves the complete base ranking before considering new trace pairs by default; its tests verify this. Candidate verification should inspect meaningful artifact/config differences, not merely successful exit. |
| Geometry-specific tooling | Profile tools fix 48 layers and default to 512 experts; Granite has 24/32. A generic-looking wrapper can still be invalid. Discover/adapt geometry and trace format before reuse. |
| Workload weighting as methodology | `make_profile_mix.py` normalizes each trace before weighting, unlike raw-count aggregation. A long request, one request and one task category are different sampling units; declare the objective and test on separately selected inputs. |
| Partial trace finalization | `collect_profile_traces.py` skips nonempty existing paths; the incomplete-tail probe shows why size alone cannot establish completion. Manager should distinguish captured/finalized/validated/registered and keep attempt identity/coverage. |
| Cheap cache-policy screen | `bench_eviction.py` supplies fill-only, LRU, decayed LFU and offline oracle with warm/cold and global/per-layer choices. Oracle reads the future. Simulation hit rate does not include actual transfer/swap/compute costs or prove speed. The simulator's baseline comment is not a complete inventory of today's enabled adaptive engine paths. |
| Explicit candidate change classes | `strata_control/tune_knobs.py` stores diffs, backend/family conditions, bounds and exact/placement/nonrepeatable/quality classes. Reuse the pattern, not its specific knob bounds or a mandatory single-knob-only methodology. |
| History versus A/B comparison | `tune_history.py` checks same-build history and can reject different engine identities, which are intentionally different in engine A/B tests. Build a comparison policy with explicit changed/control roles. Required unknown fields must fail admission separately; two unknown keys do not establish comparable conditions. |
| Integrity versus compatibility | `tune_history.file_identity` samples by default; `conversation_file.cpp` uses sampled session compatibility fingerprints. Neither is a full artifact SHA-256. `engine_component.verify` hashes all native payloads only with `full=True`; default hashes entrypoint and checks sizes. Record verification scope. |
| Component synchronization contract | `include/strata/core/exchange_storage.hpp` requires CPU readers/H2D transfers to finish before commit; the class publishes atomic slot IDs but does not perform/synchronize transfers. Host-array tests check aliases/guards/duplicate commits, not CUDA correctness. Component CC must include ownership/lifetime/synchronization instructions and actual integration tests. |
| Health is more than process liveness | `serve/test_fatal_recovery.py` uses a fake engine that emits fatal errors while remaining alive. The intended behavior invalidates health, retains failed request and avoids blind replay; only a later request reloads. Useful lifecycle fixtures do not establish real inference correctness. |
| State is more than tokens/KV | Snapshot/validation and conversation-cache-parity tests cover recurrent/indexer/draft/PLE/layer ownership/checkpoints and missing evidence. Real model A → unrelated B → A versus fresh A is a useful reset question. Adapt actual state families; Strata's validator is not automatically Granite's. |
| Partial restore and async save | `conversation_state.cpp` distinguishes validation rejection before mutation from transfer failure; snapshot code exposes completion joins. A “save started” message/file existence is not finalized, exportable state, and a partially applied restore may require recreation. |
| Identity-aware bounded retry | `serve/test_session_save_retry.py` stops on unknown estimates, process replacement/death or inappropriate error classes. `strata_control/runtime.py` reconciles owned markers/creation time rather than trusting PID/lease alone. Avoid host-wide memory-pressure scripts and blind relaunch. |
| Convenience persistence versus evidence durability | `strata_control/atomic.py` writes temp+rename; tuning history appends JSONL and skips damaged rows. These patterns do not supply a complete fsync/concurrent-writer/acknowledgement/ownership protocol for Manager evidence. |

Promising experiment choices include a no-op detector, profile-weighting comparison, offline policy headroom screen followed by a real candidate, state-safe component integration, effective-launch/integrity validation, controlled interrupted trace collection and stale-owner recovery. Choose based on actual campaign observations. Several can share a small CC; do not create one capsule for each row.
