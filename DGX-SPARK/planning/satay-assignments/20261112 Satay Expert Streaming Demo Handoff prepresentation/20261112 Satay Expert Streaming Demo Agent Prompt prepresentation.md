

> **Background engineering scope.** The [current integration prompt](<20261112 Satay Contract Driven Factory Integration Prompt prepresentation.md>) governs immediate priorities after the November 12 meeting. Protect Run 4/5 and reuse existing JiuwenSwarm components; broader research below is optional after demo readiness. Meeting notes have arrived; pending-note statements below are historical.

# 20261112 Satay Expert Streaming Demo Agent Prompt prepresentation

## Assignment

Prepare a convincing, technically accurate ten-minute demonstration of an AI4Research/JiuwenSwarm software factory using Capability Capsules to turn an existing llama.cpp codebase into an inference engine with expert streaming.

The audience should leave understanding one concrete claim:

**We give JiuwenSwarm a working engine, an engineering objective and relevant CCs. It uses the capsules’ expertise, tools and components to build expert streaming into that engine, test the result, and revise its decisions from evidence.**

This is an execution and presentation-readiness assignment. Deliver working software, a reproducible demonstration, the evidence behind it and clear explanatory material. A polished catalog or a pre-existing optimized image alone does not satisfy it. Build on the working system already developed on Satay; do not restart the project from the original handoff.

Satay is the Jetson Orin Nano. The main model is the existing Qwen3.6-35B-A3B quantization, approximately 20.8 GiB of weights on a machine with about 7.4 GiB usable shared memory. Verify the actual model and machine identities. Use existing assets and respect ongoing jobs. Granite can support quick development checks, but the presented result must show the large MoE use case.

The expanded development effort must not expand the presentation: retain one readable story and put deeper investigations in backup material. Our ten-minute slot ends with a working engine and a capsule/evidence handoff. The RSI presenter has a separate slot immediately afterward to show an improvement to a CC. Their profiling, development and improvement demonstration must not consume our time or become a prerequisite for our segment.

## Claude: lead an ambitious parallel engineering effort

Act as the lead investigator and integrator. Use many useful agents to accomplish substantial work quickly. Delegate independent research, source analysis, coding, profiling, integration review and presentation preparation to Codex workers. Use the operator's configured **Codex at maximum supported reasoning effort (“Codex max”)** where available. Resolve and record the actual installed model and effort setting; do not invent a model alias, assume a historical model called Codex-Max is intended, or fabricate CLI flags. Where maximum effort is unavailable, use the highest supported setting and report the limitation.

Give workers concrete outcomes, owned areas and evidence expectations, with freedom to choose their approach. Keep several productive investigations moving, integrate completed work frequently, and redirect workers when evidence invalidates an assumption. Parallel agents should produce a coherent working engine, not a collection of disconnected reports. Use a clear integration owner and coordinate edits; do not create an elaborate new agent-management framework just for this assignment.

Useful parallel areas include engine/source understanding; expert prediction and read scheduling; adaptive CPU/GPU use; low-overhead measurement and expert-activity views; capsule methodology and dynamic factory decisions; and the two-slide explanation and demo rehearsal. These are available workstreams, not a fixed execution graph or a requirement to assign exactly one agent to each.

Satay's resources remain scarce. Parallelize research and implementation, but serialize resource-heavy builds, GPU runs and scored experiments through the existing resource coordination mechanism. Do not interrupt the ongoing campaign or let workers overwrite one another's changes. Do not assume the coding models themselves must run on the Nano. Verify available execution resources and keep the demo engine's memory budget intact.

Maintain a known working demonstration while developing more ambitious candidates. Promote coherent, supported improvements into that path; preserve unfinished research separately. The goal is much more engineering progress, without making the presentation depend on every exploratory branch succeeding.

## What the audience must see

Begin with **exactly two preface slides**, then move into the system demonstration. These slides orient the audience; they are not a survey of the entire CC catalog.

**Slide 1: the engine problem and the intervention.** Explain a token’s path through llama.cpp at the level needed to understand MoE execution, the selected experts’ weight reads, CPU/GPU computation and shared memory. Show the bottleneck when the selected weights are not resident. Contrast this with the added expert-fill and predictive-read behavior. Clearly distinguish software changes from configuration, and weight-read timing from expert placement. Label tokens correctly; do not replace tokens with “words” in speed or profiling figures.

**Slide 2: how the factory makes the change.** Show the existing engine and task brief entering the heavily revised AI4Research/JiuwenSwarm system; CC guidance and components informing the agent; integration and build producing an image; the lab producing evidence; and that evidence feeding the next decision. Show the shared evidence store and the agent’s ability to reconsider its approach. Explain component, callable tool and written guidance only as far as necessary to understand the demonstration. Skills and methods may sit together in a capsule; do not turn their naming into the main topic.

The demonstration then tells one continuous story:

1. **The starting engine already works.** Show plain, identified llama.cpp running the real large MoE in the lab and generating a short response. Show its configuration and a small baseline result card quickly. If the model is preloaded or results were measured earlier, label that honestly.
2. **The agent receives a clear engineering task.** Show the actual instruction, available resources and CCs, not just an animation of an agent box.
3. **The agent uses `engine.expert_streaming`.** Show which material it reads, which components it selects, which tools it invokes and why its decisions follow the current evidence. The capsule should be understandable as a capability to “build expert streaming,” not merely a folder containing patch files.
4. **The source changes are visible.** Show a concise architecture overlay and a meaningful source diff: what llama.cpp already did, what the components add, and where they connect. The audience must be able to connect the code change to the behavior described on slide 1.
5. **The changed source becomes a real image.** Show the Builder job and its result, including source/component identity and image identity. The displayed image must contain the demonstrated change.
6. **The lab runs that image and compares it with the baseline.** Show generated output, the scoped correctness result, evidence that expert streaming actually engaged, and a directly measured performance comparison.
7. **The result and handoff are clear.** End with what was built, what improved, what was retained or rejected, and the versioned CC and evidence available to the RSI presenter.

Aim for roughly two minutes of orientation and eight minutes of demonstration, including the brief handoff. Use real recordings and prepared measurements where a two-minute build or a twenty-minute comparison cannot fit live. Label live, recorded and historical material consistently. The audience must never be led to believe a completed long experiment occurred during a short screen transition.

## The task shown to the JiuwenSwarm agent

Prepare a real task brief along these lines, resolving the resource identities before the run:

> Starting from this identified, working llama.cpp revision, use the available expert-streaming capability to improve decode performance for the specified large MoE on Satay without changing generated output on the frozen test workload. Inspect the existing engine and evidence, choose and integrate appropriate components, build an identified candidate image, and use the lab to compare it with the baseline. If an approach fails, is incompatible, does not engage or does not improve the result, use the evidence to revise your next action. Return the source changes, image, comparison and explanation of your final decisions. Work within the declared resources and evaluation contract.

Give it explicit references to the source checkout/revision, model, baseline image/result, workload and correctness contract, relevant CC releases, build/lab capabilities, evidence workspace and resource budget. The brief should state the outcome and constraints rather than prescribe a patch-by-patch execution script or the expected winning settings.

## Make expert streaming understandable and substantial

Examine `engine.expert_streaming` in depth and develop it as a coherent engineering capability. It may combine components, integration guidance, experimental methods and supporting tools, while reusing shared Builder, Inspector, Lab and Evidence capabilities. The conceptual package matters more than a rushed rename of every existing CC. Label the current package layout accurately if consolidation is still in progress.

Explain and demonstrate the distinction between:

- **Demand-driven expert fill:** reading the needed nonresident expert-weight ranges in larger parallel operations before computation consumes them.
- **Predictive expert reads:** anticipating upcoming expert demand early enough to overlap useful reads with current work.
- **Supporting integration and observability:** exposing the required weight/routing information, validating effective settings, reporting engagement and making worker behavior inspectable.
- **Expert placement:** selecting CPU versus GPU execution and residency policy. The currently described fill/pregate components do not themselves move experts to the GPU; do not imply that they do.

Account for prerequisite code that remains installed but disabled because later components depend on it. A dormant dependency is not a successful optimization. Also distinguish source dependencies from run-time enablement: enabling every switch because its patch is present is not an acceptable strategy.

Show how the complete capability fits into llama.cpp. At minimum, explain the model-loading and mapped-weight path, how expert identities and weight ranges become available, the relevant graph/execution-context integration, the fill workers and predictive scheduling, and how the existing computation consumes the weights. Identify unchanged parts such as model weights and mathematical operations where that is actually true. Explain what happens when a prediction is wrong, a read is late, or the feature is disabled.

Use exact paths and symbols from the chosen source revision for the detailed backup view. The inspected patch set touches `src/llama-context.cpp` and `.h`, adds `src/llama-expert-fill.h`, and changes model/mapping support including `src/llama-model.cpp`, `src/llama-model-loader.cpp` and `src/llama-mmap.cpp`. These are investigation landmarks, not a substitute for checking the current implementation. Verify the routing/graph hooks and explain their actual semantics. Keep the main diagram readable; put the fuller source map in backup material.

## Expand the capability and its methodology

Do more than replay one successful setting. Strengthen the capsule’s ability to help an agent decide **when expert streaming is appropriate, which approach to try, what evidence is missing, and when to stop or change direction**.

Treat expert streaming as a major inference-engine capability worth substantial development. Expand its observability, adaptive policies, CPU/GPU use and experimental methodology. Deliver the strongest coherent working capability that the available time and hardware support. Do not settle for wrapping a fixed patch sequence if useful engineering progress is possible.

Make the capsule useful beyond one winning configuration: it should identify suitability, discover missing evidence, select and combine components, explain tradeoffs, adapt decisions and retain lessons from unsuccessful attempts. Improve its written methods, tools and component contracts together where needed. A richer catalog alone is not the outcome.

Investigate useful adaptation of prediction depth, read timing, read granularity, inflight work, reader concurrency and memory use. Seek policies that respond to the workload and observed conditions rather than a collection of magic constants. Expose why a policy changes its decision, what actually changed, and whether the change helped. Prefer a few well-supported capabilities over many switches with no evidence of engagement.

The methodology should help distinguish “predicted the right expert” from “its weights were ready before demand,” and fewer page faults from lower end-to-end decode time. Separate load, prompt processing and decode before attributing costs. Whole-run copy time is not automatically a decode bottleneck; CPU-side residual time is not automatically proven expert-matmul time. Traced runs explain behavior; use untraced runs to score speed.

Expose the relevant engineering choices to the agent through the capability. It should not be trapped in a catalog that prevents it from asking a useful question or testing a justified setting. At the same time, keep trials bounded and evidence-backed. Treat a failed idea as retained knowledge, not a reason to hide the run or force a positive result.

Keep the acceptance type appropriate to the module. A performance component must demonstrate a meaningful performance outcome. An observability component should deliver its promised signal within an agreed overhead bound, not be rejected simply because it does not speed up inference. A change to scoring rules requires a new declared evaluation contract and fresh confirmation, not retroactive relabeling of an old result.

Any capability strengthening done for this preparation is part of the delivered baseline CC. Coordinate a clean version boundary with the RSI presenter so they can demonstrate their own subsequent CC improvement without confusing it with engine-component integration in our segment. Do not delay the working demonstration indefinitely to pursue a broader research agenda.

## Make expert activity and engineering changes visible

Build the missing profilers and observation tools that let a user understand what the engine is doing. The audience should be able to answer: which experts were selected, which were predicted, whether their weights were ready in time, where their computation occurred, what had to be read, and where execution waited.

Provide a readable view tied to actual run data. Useful options include a layer-by-token expert activity map; predicted versus selected experts; timely, late and unused speculative reads; and a phase-aware CPU/GPU/read timeline. Choose the views that explain the real mechanism. Distinguish logical expert identifiers from physical weight ranges, and explain aggregation or sampling. Do not imply that an operating-system residency sample proves continuous residency.

Connect the engineering view to the behavior view: show the component applied, the meaningful source change, the reason for the change, effective configuration, the image built and the resulting observations. The user should be able to point at the architecture diagram and see what the CC added there. A compact “what changed and why” panel is more useful than a scrolling wall of agent messages.

Provide low-overhead routine evidence and richer opt-in diagnostic profiles where useful. Capture only the information needed to resolve the question. Identify sources, phases, units, sampling and coverage; missing observations are unknown, not zero. Distinguish measured expert selection from prediction, and directly measured timing from inferred attribution. An animation must be driven by real evidence, with live versus replay clearly labeled.

Measure instrumentation overhead once for the relevant release and mode, and recheck when changes can materially affect it. Use untraced runs for scored speed. A profiler is successful when its signal is correct and useful within its declared overhead budget; it need not make inference faster. Do not attempt a comprehensive profiling product before delivering the few views that make this demonstration understandable.

## Make adaptive CPU/GPU use a first-class research objective

Investigate and implement useful adaptive placement or workload splitting where the engine and hardware support it. Determine whether the useful choice occurs before a run, between workloads, between prefill and decode, or safely within execution. State exactly which level works. Automatically selecting a configuration is a valid capability, but manual tuning and a static sweep are not runtime adaptation.

The policy should consider the complete cost of computation, weight access, staging or extra copies, synchronization, memory pressure, page-cache displacement and decision overhead. Satay's CPU and GPU share physical memory; GPU allocation does not create extra RAM. Verify local allocation/cache behavior and backend support. Do not import a discrete-GPU cache strategy and assume its published gain transfers.

Show the observation that triggered a decision, the actual placement or split selected, and its measured effect. Seek stable behavior and an understandable fallback when evidence is weak or resources change. Demonstrate that any runtime switching respects graph/backend constraints, memory lifetimes and completion ordering. Investigate oscillation and switching cost before presenting a dynamic controller as an improvement.

Preserve the mathematical router's selected experts. Do not silently drop experts, change model bytes, alter quantization or reduce the workload to manufacture a speedup. Timing-only streaming should retain the existing frozen byte-identical output contract. If a separate CPU/GPU execution path changes floating-point behavior, declare an appropriate numerical and output-quality contract before scoring that experiment; do not relax the main comparison after observing a failure. Label that result separately.

## Research that produces decisions

Use primary research, relevant source implementations and the campaign's own evidence. Ask workers to propose competing theories, not merely collect references. For each promising idea, record its mechanism, required conditions, predicted observable effect, cheapest useful discriminator, rejection criterion and actual outcome. Clearly distinguish published results, local observations, replay estimates and confirmed improvements.

Start with these hypotheses, refine or replace them from current evidence, and avoid an exhaustive parameter search:

| Hypothesis | Cheapest useful investigation | Evidence against it |
| --- | --- | --- |
| Timely useful reads matter more than maximum prediction recall. Reducing speculation when storage or memory is pressured can lower decode latency. | Use a short trace to separate correct predictions from readiness before demand; screen one bounded adaptive policy against the fixed policy. | Reduced speculative traffic increases demand stalls, worsens tail latency, or does not improve untraced performance. |
| Retaining weights by expected avoided stall per byte can beat popularity alone. | Use existing traces to screen a cost-aware admission/retention policy under the same total memory budget before implementing an expensive variant. | Extra allocations displace useful mapped pages, physical reads rise, or a higher hit rate fails to lower runtime. |
| Prefill and decode may favor different CPU/GPU choices. | Establish whether an actual compute/access/synchronization crossover exists for representative expert workloads, then confirm any promising choice in the engine. | No useful crossover exists on Satay, or staging, memory pressure and switching costs erase the benefit. |
| Adaptive inflight reads or reader concurrency can outperform a fixed high thread count under changing contention. | Compare one plausible bounded policy with the current setting; observe demand stalls, CPU contention and storage behavior. | The controller oscillates, adds overhead or fails to improve untraced latency under matched conditions. |

These are research candidates, not promised wins or four mandatory features. Prefer investigations that unblock several decisions. Reuse negative results so different agents do not rediscover the same dead end. Trace replay can reject weak ideas cheaply, but cannot establish final speed when execution timing and cache feedback change.

Primary starting references:

- [NVIDIA CUDA for Tegra: memory management](https://docs.nvidia.com/cuda/cuda-for-tegra-appnote/index.html#memory-management): shared physical DRAM does not make allocation and caching behavior identical. Check the installed device/runtime; do not assume all features in current documentation exist locally.
- [Fiddler](https://arxiv.org/html/2402.07033v3): investigate measured CPU compute versus GPU compute plus transfer cost and token-count sensitivity. Its discrete-GPU experiments do not establish a Jetson speedup.
- [MoE-Infinity](https://arxiv.org/abs/2401.14361v3): investigate activation-trace-informed prefetch and retention. On Satay, establish whether the benefit is avoiding storage reads, demand stalls or other costs.
- [llama.cpp CLI reference](https://github.com/ggml-org/llama.cpp/blob/master/tools/cli/README.md): static CPU-MoE and tensor-placement controls are useful comparison points. Verify actual options against the pinned source/build; these controls alone do not supply runtime adaptation.
- [OpenAI reasoning guide](https://developers.openai.com/api/docs/guides/reasoning) and [subagent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents): consult installed tooling for supported reasoning settings and delegation, rather than assuming a universal “max” invocation.

## Keep validation lean and decision-focused

Reduce redundant testing, not the standard of evidence. Do not build a comprehensive new test framework, write tests that mirror implementation details, or rerun every historical suite after each edit. Reuse qualified artifacts and checks when their source, inputs, environment and evaluation contract still apply. A changed command or configuration must invalidate a stale result; a failed result is not completion.

Use cheap source inspection, existing traces, narrow checks and early rejection during development. Small-model smoke runs can catch integration errors; they do not establish large-MoE correctness, resource feasibility or performance. Reserve expensive real-model comparisons for credible candidates and the final integrated image. Do not launch broad parameter grids because many agents are available.

Match checks to the changed risk:

- Presentation or guidance edits: inspect accuracy, links and consistency; no engine rerun unless behavior changed.
- Observability: verify representative signals against the real execution path, coverage and overhead.
- Streaming/read scheduling: confirm actual engagement, output preservation and targeted boundary/failure behavior.
- Placement, concurrency or memory-lifetime changes: use focused numerical, ordering and resource checks for the affected path.
- Model, quantization or expert-selection changes: treat as a separate quality tradeoff, with its own declared evaluation; these are not required for the primary demo.
- Factory orchestration changes: verify the affected durable-job, resume or evidence-integrity behavior rather than retesting unrelated engine functions.

Use a small, predeclared paired baseline/candidate confirmation for the finalist, with matched model, workload, placement where applicable, thermal/power conditions and declared cache state. The amount of repetition should be justified by observed variability and claim size. Exploratory screening is not independent confirmation. Do not repeatedly measure until a favorable result appears; report small or noisy effects as inconclusive within the budget.

Finish with one meaningful integrated review: the task actually invoked the capsules, the shown source became the identified image, the real large MoE ran, the changed path engaged, correctness passed its declared contract and the claimed improvement has direct evidence. Broaden checks only when a new change, failure or unresolved concern warrants it.

## AI4Research and dynamic decision-making

This must be a genuine major evolution of the AI4Research M1/JiuwenSwarm system, targeting `AI4Research-Main` and using the CC-v2 implementation as donor code. Preserve real Git lineage and recognizable user-facing task/session entrypoints where useful. Replace the old CC approach and rigid planning/scheduling assumptions for this workflow. An adapter around the old fixed pipeline does not meet the requested direction.

The agent must be able to inspect, integrate, test, wait, investigate, revise, retry, keep, leave dormant or revert as evidence warrants. These are available actions, not a mandatory sequence that always reaches the same answer. Show at least one authentic evidence-backed decision change from the actual run; a labeled failure case is acceptable for explaining recovery but must not be passed off as a spontaneous discovery.

Use durable, queryable evidence rather than treating the preceding node’s narrative as the next node’s truth. The task’s history should explain what the agent knew, why it chose the next action and what changed its mind. A build or lab job must survive a turn ending, and reconnecting must not silently duplicate work.

Protect the evaluation reference, evidence integrity and execution authority from modification by the candidate-under-test. Keep that separate from the ability to revise engineering plans. Do not claim that a “fixed core” alone proves measurements are valid or that native tools are automatically sandboxed. Show what the current system actually enforces.

## Evidence and presentation quality

Use a genuinely unmodified source baseline at the identified revision, with the agreed placement/workload configuration. Merely disabling switches in an already patched engine is a useful control but is not the same as the plain-source baseline. Keep model bytes, prompt, generation settings and relevant conditions matched for the principal comparison. If additional tuning changes the result, present it as a separate comparison.

Freeze the exact correctness reference and protocol before scoring. Byte-identical greedy generated text is a scoped non-regression check for this workload, not universal model-quality proof. Present requested/effective settings and actual component engagement alongside it. Use direct baseline-to-final measurements rather than multiplying incremental component ratios.

The catalog’s reported 1.18× engine gain and 1.28× with additional tuning are useful prior evidence. They are not acceptance targets to reproduce by adjusting the judge. Reconfirm what applies to the presented revisions. If fresh evidence disagrees, explain it and use the supported result. Prefer one strong, traceable comparison over a crowded table of unrelated historical numbers.

Do not quietly plant a defect to manufacture an RSI success. If the adjacent segment uses a deliberately introduced performance problem, agree the version and disclose it as a controlled demonstration. It must not be presented as an organically discovered defect in the production system.

The final demonstration should be easy to follow without reading the catalog. Use an architecture view, a compact task/decision view, a small source diff, a build receipt and a clear result card. Keep package/module versions, source revisions and image identities accessible without overwhelming the main screen. Explain the mechanism in plain language and keep detailed technical evidence in the backup view.

## Deliverables and readiness

Deliver:

- The functioning expanded expert-streaming capability and the JiuwenSwarm/AI4Research changes needed to use it dynamically, with supported adaptive behavior clearly separated from unfinished candidates.
- Useful expert-activity and change-observability views, their underlying data, and declared measurement overhead.
- A compact research decision record: theories investigated, outcomes, rejected ideas, and promising next improvements for RSI.
- A reproducible plain-source baseline and candidate run, with the integrated source, component/release identities, image identities and evidence bundle.
- The exact task instruction and resource references used by the agent, plus its real invocation and decision history.
- Two concise preface slides, a source-grounded llama.cpp integration diagram and a deeper backup explanation of expert streaming.
- A rehearsed ten-minute screen sequence and labeled recordings for slow steps, with a clear fallback if the live run is unavailable.
- A versioned handoff to the RSI presenter identifying the CC baseline, available telemetry/evidence, and what our segment has already established.
- An updated current-status note that distinguishes completed, measured, proposed and still-running work, and marks earlier conflicting demo guidance superseded.

Meeting notes will arrive later. Prepare the working demonstration and explanatory material now, leaving room for those notes to refine the story. Do not invent meeting decisions or wait for them before making progress.

## Reference snapshot

The supplied `Satay CC Catalog (1).html` is a work-in-progress snapshot received November 12, 2026; SHA-256 `4974faa3f00d143abcd8217877aebff405048401b0ebda18907fe8e3c143f7e9`. Its implementation/results claims are source claims, not independent verification by this prompt.

The catalog cites JiuwenSwarm `608656eb` and siminfeng `3224d20`. A read-only fetch during prompt preparation found newer tips: JiuwenSwarm `ai4r/iterative-cc-factory` at `b1cee120b851de5ce82d279689c726f4a9f7a904`, and siminfeng `main` at `3bff22b45e3c883644fa8f345f446da501177d87`. The inspected expert-fill/pregate manifests identify llama.cpp base `cf34d311332e362198f0a410c466d1e940287d02`. Reconcile these with current work; do not reset an active checkout to match this snapshot.

This prompt supersedes the earlier generic six-capsule implementation order and the thread-naming-only main demo. The current centerpiece is **building expert streaming into an existing llama.cpp engine**, with a real measured result and a separate subsequent RSI segment. It does not require replacing unrelated working modules or completing all nine catalog capsules.
