---
title: Typed compatibility and safe abstention in capability selection
date: 2026-10-07
tags: [capsules, tool-selection, preconditions, abstention, research]
status: research-note
---

# Typed compatibility and safe abstention

This is a focused supplement to [[capsule-feeds]]. It examines the gap between retrieving a semantically relevant capability description and establishing that a capability is executable for the current task: its inputs are available and type-compatible, its preconditions hold, its effects are acceptable, and a safe no-match/clarify path exists. Sources are primary papers; evidence and architecture inference are separated below. None evaluates capsule retrieval with that full contract.

## Human summary

The evidence is convergent but indirect. Tool-use benchmarks show distinct failure stages for selection, schema grounding, argument binding and deciding that available tools are insufficient. Paired abstention experiments find that agents often act where they should stop, and stateful tool benchmarks show that dependencies may be learned from runtime state rather than descriptions. Classical planning offers an explicit formal model of action applicability (preconditions) and consequences (effects), but not capsule retrieval. The best next experiment combines these ingredients and keeps semantic retrieval recall distinct from executable eligibility.

## Source evidence

### ToolRobustBench: Stage-Wise Perturbation Evaluation and Failure Diagnosis for Tool-Calling Agents

- Zheng et al. arXiv v1, 2026-08-23. [Paper/version](https://arxiv.org/abs/2608.23635); [artifact](https://anonymous.4open.science/r/toolrobustbench/).
- **Full text:** §§3.1–3.5, §§4.1–4.3, §5, App. E, §9.
- **Evidence:** On deterministic local tools, 7 models are evaluated over 15,456 single-family records, separating tool selection, schema grounding, argument binding, feedback handling and end-to-end success. The scorer backtracks cascaded failures to their earliest stage. Clean baseline-row success averages 0.979 (three models reach 1.000), versus per-model four-family macro perturbed robustness of 0.664–0.766; observation perturbation is the main bottleneck.
- **Boundary:** Every anchor has a gold target tool. The study does not test open-set no-match, safe abstention, semantic type compatibility, or symbolic preconditions/effects. JSON-valid arguments are not proof of operational compatibility. This is a v1 preprint using sampled local tools and single-step cases.

### AgentAbstain: Do LLM Agents Know When Not to Act?

- Liu et al. arXiv v1, 2026-07-11. [Paper/version](https://arxiv.org/abs/2607.10059); [author data/project](https://agentabstain.github.io/).
- **Full text:** §§2.1–2.4, §§3.1–3.2, App. A.1.
- **Evidence:** 263 paired act/abstain tasks in 42 MCP sandboxes test whether agents complete an actable case and refuse/clarify on its minimal no-act variant. Categories include missing inputs, conflicting constraints, insufficient tools and runtime failure/evidence. A 100-pair sample receives 94%–98% “well-designed” ratings across three annotators. Across 17 models/4 harnesses, paired accuracy is 33.0%–59.5% (mean 45.7%); “Insufficient Tools” reaches 67%, while “Conflicting Evidence” reaches 28%. The paired metric captures both over- and under-abstention.
- **Boundary:** Insufficient-tools is agent-level abstention, not typed capsule retrieval. Environments expose 3–29 tools; evaluation combines tool-log checks with an LLM judge; each task runs once. Authors note scenario and deployment scope limits, judge bias, and missing multi-run variance. Refusal/clarification must occur before critical action; hedging after action does not count.

### ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities

- Lu et al. arXiv v2, 2025-04-16. [Paper/version](https://arxiv.org/abs/2408.04682); [author repo](https://github.com/apple/ToolSandbox).
- **Full text:** §§2–4, especially §3 and state-dependency/insufficient-information results; §7; App. A.2.
- **Evidence:** Authors implement 34 tools across 11 domains. The “Insufficient Information” scenario withholds a needed tool and tests for hallucinated tool names/arguments. State-dependency scenarios make execution contingent on mutable world state and sometimes require sequential calls; erroneous parallel calls lead to failures. App. A.2 perturbs tool catalogs and argument descriptions/types.
- **Boundary:** Interactive tool-use, not typed capsule retrieval. Inventory is modest; some tools use external services; milestone/minefield authoring is costly and user simulation can err (§7). Missing-tool cases are benchmark-authored, not eligibility computed from capability contracts.

### PlanBench: An Extensible Benchmark for Evaluating Large Language Models on Planning and Reasoning about Change

- Valmeekam et al. NeurIPS 2023 D&B; arXiv v4, 2023-11-26. [Paper/version](https://arxiv.org/abs/2206.10498).
- **Full text:** §§3–7, App. A.4.
- **Evidence / formal analogy:** Actions have parameters, state-predicate preconditions and add/delete effects; an action is executable only when its preconditions hold. PlanBench tests generation, verification, execution reasoning, reuse and replanning under explicit domain descriptions. In Blocksworld cost-optimal planning, 198/600 GPT-4 plans (33%) and 35/600 InstructGPT-3 plans (5.8%) succeeded. This formalizes why topical relevance does not imply present applicability.
- **Boundary:** Symbolic planning—not tool/capsule retrieval, JSON binding, runtime effect enforcement, or no-match abstention. The classical deterministic model is narrower than uncertain external APIs.

## What follows for a capsule experiment (inference, not a paper result)

Keep three decisions and scores distinct:

1. **Discovery/relevance:** retrieve candidates whose descriptions or declared capabilities may address the request. Score recall and ranking separately.
2. **Eligibility/binding:** check input presence and schema/type compatibility; current preconditions/state; dependency/version pins; allowed effects; required output/check coverage. Record which constraint failed. Semantic rank cannot waive a failed hard check.
3. **Decision:** bind only an eligible candidate or compatible composition; otherwise abstain, ask for missing information, or report no compatible capability. Score missed eligible options and unsafe/false-positive bindings separately, alongside over-abstention and task success.

### Minimal M2 experiment

- Build fixed registries with matched candidates that vary one contract property at a time: type-compatible vs incompatible ports; satisfied vs unsatisfied/stale preconditions; allowed vs forbidden effects; compatible vs mismatched schema versions; complete vs missing required checks. Include relevant-looking candidates that are ineligible, irrelevant-looking but eligible candidates, and truly no-match requests.
- Compare semantic top-k alone, semantic retrieval plus deterministic eligibility filter, and model-only judgment. On a separate split, include typed composite recipes with one unsatisfied member precondition and one incompatible intermediate output/input.
- Report (a) retrieval recall/rank of eligible capabilities, (b) binding precision/recall conditional on discovery, (c) false-positive binding rate/cost, (d) correct clarification/no-match abstention and unnecessary abstention, (e) effect violations and schema/type/precondition violations, (f) end-task success and latency/token cost. Use deterministic validators for schema, version, declared state and effects; blind task judges only for goal-level outcome. Do not collapse these into one “retrieval accuracy.”
- Paired task construction can adapt AgentAbstain: each actable request has minimal variants that remove a needed input, invalidate a precondition, prohibit an effect, or make the only candidate type-incompatible. The expected behavior must vary: ask when user information could resolve it; report no compatible capability when none is available; do not treat abstention as the universal best answer.

### Anti-patterns

- Call semantic nearest-neighbor score “compatibility,” or treat JSON/schema-valid args as proof of semantic type or state validity.
- Let the model infer preconditions/effects from a tool summary when those contracts can be structured and checked.
- Measure only task completion: an agent can choose an incompatible tool and still answer plausibly, or perform a damaging partial action before declining.
- Measure only abstention: a system that never binds would look safe under a no-action metric while failing every actable case. Use paired act/abstain examples and report both sides.
- Allow a successful match to imply authorization. Compatibility answers whether an action is applicable; policy and runtime gates decide whether its effects may execute.

## Evidence level and remaining gap

Full text reviewed for all four sources, using the section locators above; current arXiv version checked 2026-10-07. ToolRobustBench and AgentAbstain are v1 preprints. ToolSandbox is v2. PlanBench is v4 / NeurIPS 2023. Author code/data repositories were checked for ToolSandbox and AgentAbstain; paper claims are cited to papers, not project pages.

The literature still does not directly test a capability retriever that uses declared typed inputs/outputs plus state preconditions/effects to choose a capsule, reliably return *no compatible result* when appropriate, and calibrate that choice against a safe execution oracle. The minimal paired experiment above is therefore an open evidence proposal, not a claimed existing best practice.

Independent denominator and task-label audit: [audit note](typed-selection-audit.md).

