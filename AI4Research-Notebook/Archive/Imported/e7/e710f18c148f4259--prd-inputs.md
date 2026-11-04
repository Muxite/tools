---
type: process
tags: [process, prd]
---

# PRD alignment

How the design follows the [PRD](prd.md) (owner Ramika). This page maps each PRD feature to the design and to what Capability Capsule (CC) contributes, lists the tools M1 needs, the choices we made where the PRD is silent, and our questions back to the PRD. Build steps: B1 = Phase 1 (the M1 path), B2 = Phase 2 tests, B3 = the parallel tracks ([overview](../design/overview.md#build-steps-b1-to-b3-inside-m1)).

## Each PRD feature, and where it lives

| PRD feature | In the design | What CC contributes | Step |
|---|---|---|---|
| Codex CLI integration (first step) | [routing](../components/run.md#routing): one model for every call | the model on every Observation | B1, first |
| Ingestion | [ingestion and intake](../components/request-to-contract.md#ingestion-and-intake) | prompt and documents stored as hashed Artifacts | B1 |
| Requirement Compilation | [requirement compilation](../components/request-to-contract.md#requirement-compilation): `requirement_capsule`, then requirement acceptance, before freeze | the Research Brief as the [semantic contract](../schemas/semantic-contract.md)'s `brief`; its checks | B1 |
| Search & Ideation, Screening, Hypothesis, POC Implementation | [the Default DAG](../components/run.md#the-default-dag): `search`, `screening`, `hypothesis`, `poc` | one Declaration per stage capsule; typed outputs (`idea_set`, `screening_result`, `hypothesis`, `poc_bundle`) | B1 |
| Benchmarking | the `benchmark` step: `benchmark_runner` (`tool`) | `benchmark_result` Artifact, checked by the gate | B1 |
| Evaluation, Evaluator (verifier module) | [verification](../components/verification.md): the Evaluator gate on the Research Brief and after every step | the Stage Evidence Bundle as the [Verification request](../schemas/verification-record.md); tier 1 checks from the Declaration; `pass`, `fail`, `blocked` as the result | B1 |
| Delivery | the `report` step's `report_capsule`, then [delivery](../components/run.md#delivery) | `report` Artifact; the [Delivery](../schemas/delivery-record.md) record | B1 |
| Capability Capsule | [capsule](../capsule/capsule.md) | the Declaration as the machine-readable `make_capsule.md`; the with-and-without experiment | B1 |
| Operators | `op.deepsearch`, `op.codesearch`, `op.workspace_io` as `tool` capsules | admission is the whitelist; `needs.external` pins which stage may call which | B1 |
| Planner, Phase 1 | [plan and freeze](../components/plan-and-freeze.md): pass-through emits the Default DAG | freeze pins each capsule version, and the verifier, by hash | B1 |
| Planner, Phase 2 (Cluster Mode) | beside the baseline | our chaining planner and gap Findings, for comparison | B2 |
| Intention Compilers | Phase 1: template mapping (control). Phase 2: the Leader Agent | Phase 2 only: the IntentIR and `decide_acceptance` | B1, B2 |
| Builder | Phase 1: stage capsules write text and Markdown. Phase 2: Code Mode for POC | `patch`, `test_report` port types | B1, B2 |
| RSI integration | [RSI](../components/rsi.md) on sample DAG fixtures | lineage, Candidates, admission; fixtures are B1 runs' records | B3 |
| Model routing (dynamic) | [routing](../components/run.md#routing) | `needs.model` in every Declaration, unread until then | B3 |
| Foundational models | one model, no switching | | B1 |
| Data foundations | Task Memory and Coding Memory for context | our store holds only CC records | B1 |
| Harness core | JiuwenSwarm's runtime and Swarmflow | the runner and the gate inside the script | B1 |
| Visibility | Swarmflow's run tree, team token budget, tool logs | Observations joined to the run tree | B1 |
| Installer, CLI, web app, UI, message channels | JiuwenSwarm's own (`jiuwenswarm-start`, web workbench, TUI) | none: we build no frontend | B1 |
| Account management | JiuwenSwarm's permission whitelist | `effect_class` mapped to ALLOW, ASK, DENY | B1 |
| System configuration | `~/.jiuwenswarm/config/config.yaml` | the policy holds CC's own values, pinned by hash | B1 |

## The tools M1 needs

Every schema field is served by a tool; a field with no tool yet is stored but not used ([early and later capsules](../capsule/stages.md)).

| Tool | Serves | Step | Proposed owner |
|---|---|---|---|
| Codex CLI connection | the single model | B1, first | Xiaoyang |
| Default DAG script (intake, template mapping, requirement acceptance, the six steps, delivery) | Plan, RawIntent, Delivery | B1 | Xiaoyang |
| M1 capsules: six stage skills, `verifier_capsule` and `benchmark_runner`, each with its Declaration | the Declaration; the port types | B1 | Xiaoyang (skills), Muk (Declarations), Ramika (`verifier_capsule`) |
| operators as `tool` capsules | `needs.external`, the whitelist | B1 | Xiaoyang, Muk |
| author kit (`cc check`, `cc hash`) | the Declaration: shape, hashes, local tests | B1 | Muk |
| admission | Candidate, Declaration, checks: writes test cases, Verdict, Standing | B1 | Muk, Ramika |
| records store and code store | every CC record; code by hash | B1 | Xiaoyang, Muk |
| planner-binder (pass-through), freeze | Plan, run contract with budgets | B1 | Muk |
| precondition evaluator | `needs.when` | B1 | Muk |
| runner (`agent()` wrapper, operator rail) | Observation, Artifact | B1 | Xiaoyang, Muk |
| Evaluator gate: tier 1 check runners, the verifier call, the fold, triage | Verification, checks | B1 | Ramika, Xiaoyang |
| `make_capsule.md` experiment harness | the two arms and their comparison | B1 | Muk, Ramika |
| chaining planner beside Cluster Mode; Leader Agent with IntentIR and `decide_acceptance`; Code Mode POC | Phase 2 tests | B2 | Xiaoyang, Muk |
| dynamic planner: Cluster Mode, with Symphony `plan()` and the CC provider as an option | the dynamic planner track | B3 | Muk, Xiaoyang |
| RSI and its importer, on sample DAG fixtures | Candidates, Findings | B3 | Saurav |
| dynamic routing | `needs.model`, budgets | B3 | Xiaoyang |
| calibrated judges, sealed suites, librarian | `certified` level, Standing moves | B3 | Ramika, Muk |

Not needed for M1: our own CLI or frontend (dropped: the PRD uses JiuwenSwarm's), the composer and fuser ([composition](../capsule/composition.md)), installing capsules mid-run.

## Choices we made where the PRD is silent

1. **The Research Brief is the M1 value of the semantic contract**, in a new `brief` object; target metrics are also `must` requirements of kind `metric`. Requirement Compilation and its acceptance (the Evaluator gate on the Brief) run before freeze, so the run contract pins the rest of the run against the accepted Brief.
2. **Phase 1 intention compilation replaces** `compile_intent`, `review_fidelity` and `decide_acceptance` for M1. They return in B2 with the Leader Agent.
3. **Ingested documents become `file` Artifacts**, listed in the RawIntent's `attachments`. Intake reads them through `op.workspace_io`, which the Default DAG template allows control code to call.
4. **Benchmarking runs a capsule**, `benchmark_runner` (a `tool`), so every step and every gate has a pinned, observed call.
5. **`fail` and `blocked`** are defined once, in policy [`gates`](../schemas/policy.md): `fail` when a check fails, `blocked` when no verdict can be reached.
6. **Triage** gives the developer three answers: `pass` (advance anyway), `repair` (run the step again, at most twice) or `fail` (end the run). A 600 s timeout counts as `fail`. Both the gate result and the triage are Verification results.
7. **Operators are `tool` capsules** (`op.deepsearch`, `op.codesearch`, `op.workspace_io`); the permission rail's ALLOW list is generated from admission.
8. **Token budgets are per step** (60000 for the Brief and each step, 20000 per verifier call), pinned in the run contract; the team ceiling stays in `config.yaml`.
9. **RSI submits under track names**, so nothing it builds reaches the M1 path without a person.
10. **Our `run_id` is Swarmflow's run id**; Observations join the run tree through `ext.swarmflow`.
11. **Policy epochs run side by side**: `b1` for the M1 path and one epoch per B2 or B3 track; each run pins one.

## Questions back to the PRD

1. **Codex CLI adapter.** In jiuwenswarm (`common/config.py:44-46`) Codex is an external CLI team member, not a model provider; agent-core has a `CodexHarness` (`harness_providers/codex/harness.py:95`). Is the M1 model Codex as the agent harness for each node (our reading), or a Codex-backed LLM provider we must build?
2. **`BLOCKED`.** Is choice 5 what the PRD means? What may the developer do at triage (choice 6)?
3. **The Research Brief schema.** Who owns it? Are the four fields and their shapes in the [semantic contract](../schemas/semantic-contract.md) right? May it be accepted before the rest of the DAG is pinned (choice 1)?
4. **`make_capsule.md`.** Is it a template authors fill in, or generated from the Declaration? We propose generated. Our experiment keeps the shared port types in both arms, so it answers "are per-capsule schemas and acceptance rules required?", not "are any schemas required?" ([its limit](../capsule/capsule.md#the-make_capsulemd-experiment)). Is that the question the PRD means?
5. **Ingestion.** Do ingested documents become Artifacts (choice 3)? Is PDF text extraction ingestion's job or `DeepSearch`'s?
6. **Benchmarking.** Is a `benchmark_runner` capsule acceptable (choice 4)? Where does the POC harness run: the workspace, or a Code Mode worktree?
7. **The semantic verifier's `FAIL`.** CC holds that an uncalibrated judge never ends a run on its own. We read the PRD as compatible: a verifier `FAIL` halts the run and a person decides. Is that right?
8. **Token budgets.** Per step, per run, or only the team ceiling? What values?
9. **`Agent.md`** (PRD 4.2). Where is it, and do its states match Swarmflow's (run: running, paused, completed, failed, stopped)?
10. **M1 acceptance.** What run counts as done: for example, a set of prompts that reach Delivery with every stage `PASS` or triaged?
11. **Our records store.** The PRD wants no custom database schema in M1. CC's records (Declarations, Verdicts, Observations, Verification results) live in agent-core's existing KV store, with no new database. Is that acceptable, or must they live in Task Memory?
12. **The dynamic planner track.** We align it to Cluster Mode, the PRD's future default, with Symphony `plan()` only as an option. Agreed?
13. **Verified citations.** Delivery in M1 wants "verified citations". The verifier (from `citation-reviewer`) checks citations in tier 2 at the `report` step, but per-claim support labels on the Delivery come in B3. Is the tier 2 check enough for M1?
14. **The verifier's place.** The PRD says Phase 1 generates sample data for the Verifier as a parallel track, yet puts the Evaluator gate in M1. We put the gate and `verifier_capsule` on the M1 path, uncalibrated, with a person deciding every `fail`; calibration is the parallel track (B3). Agreed?

15. **Operators' own models and stores.** DeepSearch's local search needs Milvus and an embedding API; CodeSearch runs its own LLM loop on every search. Both conflict with "one model through Codex" and "no custom database". Which endpoints may they use in M1? ([fit with the code](../design/integration.md#fit-with-the-code))
16. **Operators' packaging.** deepsearch and codesearch pin agent-core `0.1.17` and `0.1.10.post3`; jiuwenswarm pins `9e339019`. We propose running them as separate services. Agreed?
17. **Porting the skills.** `idea-tree-team` and `evolve-design` call engines from sciencediscovery's own runtime, and `assessment-screening` is written for catalyst materials (activity, stability and sustainability rubrics). Porting means rewriting them against our ports, and the Hypothesis and Screening rubrics are new. Who writes them?
18. **Citation checks and the network.** `citation-reviewer` checks one citation per call, through MCP literature search and the web. May the verifier use the network in M1, and how many citations per report are checked?

## Evidence CC gives for acceptance

Every run leaves, without extra work: the run contract (which capsule version ran at each step, by hash, and the Verdict that admitted it); one Observation per capsule call, joined to the run tree; one Verification result per gate decision and per triage; the Delivery. So an acceptance criterion can be a query over records: "every step passed or was triaged", "every call used an admitted capsule", "tokens per stage under X".

## Dependencies and risks

| | Risk | Owner |
|---|---|---|
| Codex as a model provider | not in jiuwenswarm today (question 1) | Xiaoyang |
| agent-core pin | jiuwenswarm pins `9e339019`; our reading is at `e23806c1` | Xiaoyang |
| human wait | `human()` times out after 600 s; a long triage ends the run | Ramika, Xiaoyang |
| the verifier | uncalibrated in M1; its accuracy is unknown until B3 | Ramika |
| schema sign-off | issues cannot be cut until the schemas they touch are signed | everyone |

Details of the seams: [where CC connects](../design/integration.md).
