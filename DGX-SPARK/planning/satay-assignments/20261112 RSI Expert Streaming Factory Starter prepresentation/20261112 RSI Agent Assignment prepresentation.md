# 20261112 RSI Agent Assignment prepresentation

## Mission

Understand and improve engine.expert_streaming as a reusable capability in the existing JiuwenSwarm factory. Start with the tagged baseline and existing evidence. Choose one bounded improvement that helps a subsequent agent perform the engine task. Do not resume paused work or launch a broad benchmark campaign automatically.

The representative task is: starting from the identified llama.cpp revision, improve the specified large-MoE workload under a frozen contract; integrate appropriate components, build the changed source, run it in the lab and return the supported result.

## Interpret the capsule correctly

The agent makes engineering decisions. The capsule supplies:
- STREAMING.md: integration guidance.
- EVIDENCE.md: methodology and interpretation.
- SOURCE-MAP.md: integration landmarks in llama.cpp.
- ONTOLOGY.yaml: provisional domain concepts and quantities.
- Eight component declarations with patch material and dependencies.
- applicability and engagement tools: inspect information and publish observations. They do not run inference or automatically apply all patches.

Existing supporting CCs provide source inspection, build submission/results, lab admission/execution and shared evidence. The task template makes engine.expert_streaming, factory.integration_skill, factory.methodology_ab, factory.builder, factory.engine_inspector, factory.lab_client and factory.evidence available. This is not a compulsory invocation order or a reason to build more capsules.

Discover actual call schemas through the installed CC discovery/description interface. Do not guess arguments. A single agent can combine several capsules in one decision cycle. Tools and written materials serve different roles; showing a catalog entry is not proof of use.

The shared source checkout, models, images and evidence store already hold most inputs. Use scoped references instead of passing complete state through successive node narratives. Each attempt records the actual source/configuration/CC/artifact identities it used. Pending plans can change; historical attempts cannot be rewritten.

Reuse Controller, Store, Jobs, Manager and existing story/replay tools. Simplified verification is intentional: no verifier agent after every call. Preserve useful correctness, artifact identity, evidence and resource checks.

## Engine mechanism

Demand fill reads selected expert-weight ranges before computation consumes them. Predictive reads try to make upcoming weights ready early enough to overlap useful work. Wrong predictions can waste I/O and displace useful pages. Readiness and phase counters help distinguish prediction accuracy from actual timely availability.

Streaming does not necessarily move expert computation to GPU. The baseline includes CPU-side expert execution and shared physical memory. Placement is a separate intervention.

Eight baseline components: mmap_advice, router_prefetch, expert_fill, expert_pregate, thread_names, expert_readiness, inflight_join and phase_stats. Catalog presence is not integration, enablement or benefit. Source prerequisites can remain installed with their switches off.

## A useful first RSI target

Inspect applicability ranking and evidence interpretation first. A bounded improvement could teach the capsule to distinguish missing evidence, a mechanism that did not engage, an engaged but late/wasteful mechanism, and a supported reason for one next action.

Other plausible targets are better handling of effective-configuration prerequisites or using per-token activity evidence in recommendations. Choose from the actual evidence; do not predeclare an optimization winner.

The outcome should be a better reusable capability: fewer avoidable invalid trials, faster useful diagnosis, better component selection, or an engine-performance gain. A new report or verifier alone is insufficient unless it demonstrably improves the task.

Guidance/tool changes can first use existing cases and a held-aside case where practical. Tool replay establishes tool behavior, not that the agent's decisions improved. Confirm agent-level claims with a bounded task invocation. Claim engine speed only from actual comparable engine runs.

If a change needs host code, identify that separately. Emitting missing-evidence fields does not enforce acceptance if the evaluator ignores them. A scheduler fix alone is not an expert-streaming capsule improvement.

## Work sequence

1. Inspect the capsule, task/contract, Run 4/5 evidence and export omissions.
2. Select one weakness attributable to reusable capability behavior.
3. Declare the hypothesis, acceptance criterion and maximum resource budget.
4. Create a candidate release without changing the baseline or its judge.
5. Exercise the changed behavior using the cheapest representative task.
6. Compare old/new versions with equivalent inputs and relevant conditions; record agent, capsule, host, model and configuration identities.
7. Return the versioned candidate, evidence, costs, failures and limitations.

Use progress and budget to decide when to stop, not a fixed iteration count. Negative results remain evidence. Do not weaken acceptance after observing them.

## Subsequent execution

Read jiuwenswarm/factory/tasks/expert-streaming-qwen36.json. It pins llama.cpp base cf34d311332e362198f0a41aca791adf226d814c7, model identity, baseline image and qwen36-bare-greedy-v1. Use it as a template for a separately identified bounded task, not an instruction to restart its eight-hour budget.

Source-checked CLI forms:
- jiuwenswarm factory init TASK_FILE
- jiuwenswarm factory run TASK_ID --grant process.exec --grant workspace.read --grant workspace.write --grant gpu.use
- jiuwenswarm factory resume TASK_ID with the same explicit grants when appropriate.
- jiuwenswarm factory export TASK_ID --out NEW_DIRECTORY

Run/resume can launch expensive real work. Execute only after the operator resumes work and the candidate task/resources are ready. Use the existing shared queue; do not start a competing worker or mutate an active task. Check installed help/current source before running. Do not refreeze an existing scored contract.

## Return

Explain what changed in the capsule, why it should help, the exact old/new versions, a reproducible invocation, observed before/after behavior, cost/correctness effects and what remains unproven. Hand back a reusable capability improvement, not only a faster manually tuned engine.
