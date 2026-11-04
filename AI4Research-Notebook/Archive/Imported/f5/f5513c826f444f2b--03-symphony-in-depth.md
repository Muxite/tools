# Symphony in depth: what openJiuwen already has, and where a Capability Capsule attaches

Written 2026-09-17. Read in source, in the local clones:

| Repo | HEAD | Date |
|---|---|---|
| `openjiuwen/agent-core` | `f1d7fd6923a6` | 2026-09-15 |
| `openjiuwen/jiuwenswarm` | `e12bcb31cf6b` | 2026-09-15 |
| `openjiuwen/skillhub` | `ff9c37f7a216` | 2026-09-15 |

Provenance marks: `[src]` = read in the source file named · `[readme]` = stated in
`openjiuwen/symphony/README.md`, which is Chinese; the gloss is mine and the Chinese is quoted where the
wording carries weight · `[mine]` = my inference, not a claim of the code.

This note supersedes the Symphony section of `tundle/ai4research/notes/report-general/OPENJIUWEN.md`
(written 2026-09-11 against an older clone). Symphony has grown since: retrieval and batch graph mutation
are in the tree now.

---

## 1. The one-sentence answer

Symphony gives a capability an **identity**, a **place in a relation graph**, a **route into a plan**, and a
**measurement**. It deliberately does not decide whether a capability is good enough to keep, and it never runs
one. Its own source says so:

> "The suite never executes a capability, computes an admission decision, or invents an overall composite
> score. Model-heavy metrics are opt-in."
> — `openjiuwen/symphony/evaluation/suite.py:85-87` `[src]`

And the interface that commits a change to the capability graph is documented as the step *after* someone else
has decided:

> "Narrow dependency used after an approved Skill asset change."
> — `openjiuwen/symphony/interfaces/graph.py:15` `[src]`

Those two sentences are the whole design brief for a Capability Capsule layer. **Symphony has left the approval
decision out on purpose, and has already cut the socket the approver plugs into.**

## 2. Module map and what actually runs

`openjiuwen/symphony/` holds 201 `.py` files `[src: find . -name "*.py" | wc -l`]. Subsystems:

| Directory | What it holds |
|---|---|
| `models/` | the public, immutable data model: `capability.py`, `fingerprint.py`, `evaluation.py`, `normalization.py` |
| `interfaces/` | the protocols a caller implements: `capability.py` (`CapabilityProvider`), `graph.py` (`SkillGraphUpdater`), `llm.py` (`SymphonyLLM`) |
| `shared/fingerprint/` | scanning, semantic extraction, IO normalisation, atomic `fingerprint.json` publication |
| `retrieval/` | `build/` (scanners, tree), `search/`, `llm/`, `common/prompts/`: the capability tree index |
| `orchestration/` | `graph/` (candidates, matcher), `planning/`, artifact lifecycle |
| `evaluation/` | `base.py`, `evaluators.py` (9 metrics), `suite.py` |
| `experience/` | trajectory parsing, experience library build and retrieval |
| `agent/` | the Agent-facing toolkit |
| `discovery/`, `flow/`, `observation/` | supporting |

Implementation status, as the README's own table states `[readme §实施状态]`:

| Domain | Status in the README | Note |
|---|---|---|
| Capability fingerprint 能力指纹 | 已实现 implemented | inventory, explicit Skill scan, semantic profile, IO normalisation, incremental cache, schema-versioned `fingerprint.json` |
| Capability retrieval 能力检索 | 待迁入 to be migrated in | ⚠ misleading. The code exists (97 files, 21,140 lines, the largest subsystem) and is lazily exported from `symphony/__init__.py`, so 待迁入 means **not yet composed into `SymphonyRuntime`**, not "not written". Unlike `experience/` it has no `API.md` for standalone use `[verify/V1]` |
| Capability orchestration 能力编排 | 已实现 implemented | relation graph, versioned artifacts, Fast/Beam planner, execution graph |
| Experience 经验沉淀 | 部分实现 partly | usable standalone, "尚未接入 `SymphonyRuntime`" not yet wired into the runtime |
| Capability evaluation 能力评估 | 已实现 implemented | registrable static and trajectory metrics, keeping reason, evidence, failure, suggestion |
| Agent Toolkit | 待迁入 to be migrated in | |
| Public `models` | 已实现 implemented | |

`SymphonyRuntime` today composes **only** `OrchestrationService` `[readme §当前可运行接口]`. `FingerprintService`,
`EvaluationSuite` and the experience domain are importable on their own but are not yet part of the runtime
facade. So anything built on Symphony now wires three objects itself, not one.

## 3. What a capability *is* to Symphony

`CapabilityDescriptor` `[src: models/capability.py:61-79]` — provider-owned metadata:

```
capability_id, capability_type, name, description, source, available,
inputs: tuple[CapabilityIO], outputs: tuple[CapabilityIO],
classification, tags, content_hash, semantic_content (excluded from dumps), metadata
```

`CapabilityIO` `[src: models/capability.py:15-23]` is `name, type, description, required, default, metadata`,
with sensitive defaults redacted on construction.

`CapabilityFingerprint(CapabilityDescriptor)` `[src: models/fingerprint.py:29-44]` adds:

```
version = "1.0.0", static_data, semantic_profile, quality: QualityResult | None,
failures: tuple[FailureReason], evidence: tuple[EvidenceRef], suggestions: tuple[ImprovementSuggestion]
```

`SemanticProfile` `[src: models/capability.py:45-52]` is `summary, capabilities, use_cases, limitations,
keywords` — all free text, all retrieval-oriented.

⚠ Two things to notice, because they define the gap:

1. **`version` is not published.** The `FingerprintArtifact` serialiser dumps each fingerprint with
   `exclude={"version", "static_data"}` `[src: models/fingerprint.py:141]`. The artifact carries a
   `schema_version` for the envelope `[src: models/fingerprint.py:128]`, not a per-capability behaviour version.
2. **There is no contract.** A grep for `precondition|postcondition|effect|held.?out|holdout|test_suite|golden|
   regression` over all 201 `.py` files returns **0** `[src]`. `semantic_profile.limitations` is the nearest
   thing, and it is prose for a retriever to read, not a condition anything checks.

The fingerprint is built from `SKILL.md` alone as the semantic input; the rest of the asset is used only for a
security hash `[readme §FingerprintService]`. Extra model calls are off by default, and when
`enable_llm_extraction`/`enable_llm_evaluation` are on without an injected model the result is an explicit
configuration error — "缺少模型时返回明确配置错误，不会默认判定通过" (a missing model returns an explicit
configuration error; it never defaults to a pass) `[readme]`. That fail-closed instinct is the same one the
capsule design needs, and it is worth citing as shared ground rather than as a difference.

## 4. The capability graph: versioned, atomic, and already transactional

Artifact layout `[readme §图产物生命周期]`:

```
graph_artifact_root/
├── cache/relation_matches.json      # not part of a published version
├── current.json                     # the pointer, switched atomically
├── mutation_requests.json           # idempotency records for batch mutations
├── .publish.lock
├── versions/<version>/graph.json    # immutable
└── .build_runs/                     # staging
```

Rules the README states, all of which the capsule layer inherits for free `[readme]`:

- a build stages into `.build_runs/`, moves atomically into an immutable version directory, then atomically
  publishes `current.json`;
- a failed or cancelled build never switches the pointer, and the last good version stays readable;
- the schema major version is checked on read and an unsupported version is rejected;
- builds on one service instance are mutually exclusive; full builds and batch mutations share a process lock
  and a version compare-and-set.

### The batch mutation seam

`SkillGraphUpdater` `[src: interfaces/graph.py:14-48]` is three methods with identical shapes:

```python
async def add_skills(changed_skill_ids, *, request_id: str, source_revision: str) -> GraphMutationResult
async def update_skills(...)     # same signature
async def delete_skills(...)     # same signature
```

Semantics `[readme §SymphonyGraphEngine]`:

| Call | When | What the graph does |
|---|---|---|
| `add_skills()` | a batch of new Skills is already persisted | add nodes, compute relations old↔new and new↔new |
| `update_skills()` | a batch of existing Skills changed | replace nodes, invalidate their in- and out-edges, recompute affected relations from the new fingerprint |
| `delete_skills()` | a batch was removed from the target inventory | remove nodes, edges, and neighbour / IO / text lookup references |

And the constraints:

- each call is **one transaction publishing at most one immutable graph version**. ⚠ Corrected 2026-09-18
  by verification (`verify/V1-symphony-core.md`): a call whose provider shows no actual content change
  returns `status="noop"` with `version == previous_version` and writes nothing
  (`orchestration/mutation_service.py:240-265`). So an admission decision does not guarantee a new
  version exists to point at, and a capsule layer calling this must read the returned status rather than
  assume it published;
- **one call carries one kind of operation only**;
- **"Skill 身份变化应显式执行 delete 后再 add，不使用 update 隐式改 ID"** — an identity change must be an
  explicit delete then add; `update` must never silently change an id;
- `source_revision` must name the persisted, immutable Skill inventory;
- `request_id` makes a retry idempotent after a lost response;
- if any validation, matcher or publication step fails, `current.json` still points at the complete old version;
- **"自演进模块只依赖 `SkillGraphUpdater` 协议"** — the self-evolution module depends on this protocol alone: it
  need not read the graph directory, pre-compute fingerprints, or know how the matcher works.

⚠ The third bullet is the same rule the capsule design already adopted independently ("a contract change means a
new capsule id"). That is a point of agreement to cite, not a novelty to claim `[mine]`.

## 5. Planning, and how run evidence is allowed to change the graph

`OrchestrationConfig(mode="fast")` plans with a single LLM call; `mode="beam"` uses a bidirectional beam search.
Both read the same versioned graph and accept `candidate_ids`, `disabled_capability_ids`, a language, and a
progress callback. The output is a `planned_graph`: a minimal JGF v2 single graph whose edges keep only the
`can_feed` relations the chosen plan states. `no_plan` and `needs_input` still return a valid graph, with
`metadata.reason` and `metadata.missing_inputs` present only when non-empty `[readme §Fast、Beam 与运行时过滤]`.

Dynamic observation is **off by default**. With `dynamic_graph_enabled=True`, a caller submits a
`GraphEvolutionInput` through `engine.submit_observation(...)`, and `[readme]`:

- run evidence produces a **separate observation revision and never rewrites the static `graph.json`**;
- only a **strongly verified success**, or an **edge-level failure carrying an explicit evidence reference and
  attributed to `orchestration`**, updates weights;
- weak evidence, external service errors, permission errors, network errors and truncated trajectories are kept
  **for audit only**;
- the graph engine does not parse session JSON and **will not guess a failing edge when edge-level evidence is
  missing**.

This is a careful, conservative evidence policy, and the capsule's own evidence rules should be stated as
compatible with it rather than as a replacement `[mine]`.

## 6. Evaluation: nine metrics and a deliberate hole

`EvaluationSuite` takes registered synchronous or asynchronous evaluators `[src: evaluation/suite.py:179]`.
Built in `[src: evaluation/evaluators.py]`:

| Kind | `metric_id` | Line |
|---|---|---|
| static | `structure_conformance` | 147 |
| static | `description_quality` | 212 |
| static | `classification_consistency` | 251 |
| trajectory | `success_rate` | 311 |
| trajectory | `latency` | 395 |
| trajectory | `accuracy` | 441 |
| trajectory | `completeness` | 563 |
| trajectory | `capability_selection` | 624 |
| trajectory | `composition_effectiveness` | 649 |

Each metric keeps `status`, an optional `[0,1]` `score`, `reason`, redacted `evidence`, `failures` and
`suggestions` `[src: models/evaluation.py:223-234]`. Trajectories are handed in by the caller as
`EvaluationCase` / `CapabilityCall`; **Symphony does not execute the capability** `[readme §能力评估]`.
Aggregation uses only samples where `score is not None`; a window is `error` only when every sample failed to
score `[readme]`.

The hole, stated three times in the source `[src]`:

- `evaluation/suite.py:86` — "The suite never executes a capability, computes an admission decision, or invents
  an overall composite score."
- `evaluation/evaluators.py:432` — latency: "Latency was observed without applying a target or admission
  threshold."
- `evaluation/suite.py:662` — "Raw observations were aggregated without a target or admission threshold."

`register()` is a public extension point, so a capsule-specific evaluator (contract conformance, held-out pass,
no-regression-against-predecessor, duplicate check) can be added to the same suite rather than beside it `[mine]`.

## 7. How jiuwenswarm actually consumes Symphony

765 lines across jiuwenswarm mention `symphony` `[src: grep -rn symphony --include=*.py | wc -l`]. The shape:

- **Rails**: `jiuwenswarm/agents/harness/common/rails/symphony/orchestration_rail.py`,
  `retrieval_context_processor.py`, `tool_stream_events.py`, plus `skill_retrieval_prompt_rail.py`.
  Symphony is reached through the harness's Rail mechanism, not called directly by business code.
- **Tools**: `agents/harness/common/tools/symphony_toolkits.py`, `skill_retrieval_toolkits.py`.
- **An adapter layer**: `jiuwenswarm/symphony/adapter.py`, `build.py`, `graph_state.py`, `graph_storage.py`,
  `skill_retrieval/runtime.py` — the app converts its own skill identity into Symphony `capability_id`s, as the
  README requires ("应用 Adapter 负责把内部能力标识转换为公共领域的 `capability_id`").
- **An evolution overlay**: `jiuwenswarm/symphony/evolution/` (2,821 lines) `[src: wc -l]`.

⚠ **What that evolution module mostly evolves is the graph, not the library — but not entirely.**
Verification found a second, config-gated pathway: `_try_distill_skill_packs`
(`jiuwenswarm/symphony/evolution/service.py:358-452`) synthesises new **skill-pack** artifacts from qualified
successful edge sequences, with an LLM-written task description, and `symphony/service.py:704-740` surfaces
each as its own graph node of `type: skill_pack`. Its `member_ids` always reference pre-existing skills, so it
composes rather than invents — but "never authors a capability" was an oversimplification on my part. Evolution
is disabled by default and the pathway is inert unless deliberately enabled `[verify/V3-jiuwenswarm.md]`. `evolution/models.py` defines
`OVERLAY_SCHEMA_VERSION = "symphony.dynamic_overlay.v3"`, events `plan.created` / `plan.outcome`, outcomes
`success | failure | no_plan | needs_input`, the single relation `can_feed`, and four failure-attribution modes
(`all_edges`, `terminal_edge`, `explicit`, `success_only`) `[src: evolution/models.py:7-30]`. It aggregates plan
outcomes into edge-weight overlays. It never authors a capability.

The only production call of the batch mutation API in jiuwenswarm is in a test
(`tests/unit_tests/symphony/test_fingerprint_adapter.py:281`) `[src]`. **The `SkillGraphUpdater` socket is cut
but, in this repository, not yet plugged into a real approval pipeline.**

## 8. What openJiuwen does for capability creation today

`jiuwenswarm/resources/agent/workspace/skills/` ships 33 built-in skills, four of which are authoring skills:
`skill-creator`, `skill-creator-normal`, `skill-omni-creation`, `swarmskill-creator`, plus `agent-creator`,
`plugin-creator` and `rsi-program-dataset-creator` `[src: ls]`.

`skill-creator-normal` is the substantive one: 619 lines of `SKILL.md`, three sub-agents (`analyzer.md`,
`comparator.md`, `grader.md`), and scripts `run_eval.py`, `run_loop.py`, `aggregate_benchmark.py`,
`quick_validate.py`, `package_skill.py`, `improve_description.py`, plus an HTML eval viewer `[src: find]`.

Its loop `[src: SKILL.md:11-19]`: decide what the skill does → draft → write a few test prompts → run them →
**help the user evaluate qualitatively and quantitatively** → show the user the results in a viewer → rewrite
from the user's feedback → repeat → expand the test set.

The grader sub-agent is well written and knows its own hazard: "A passing grade on a weak assertion is worse
than useless — it creates false confidence" `[src: agents/grader.md:9]`, and it is asked to critique the
assertions as well as grade against them.

⚠ But note what this pipeline is and is not `[src: SKILL.md:53-56]`:

- **test cases are optional and the user decides**: "Should we set up test cases to verify the skill works? …
  Suggest the appropriate default based on the skill type, but let the user decide";
- the expectations, the implementation and the grading all happen **inside one session under one user's
  direction** — there is no held-out split and no separation between the author and the grader's inputs;
- the verdict is an **LLM judgment plus a human's reading of a viewer**; nothing deterministic gates
  publication;
- the loop ends when the user is satisfied, not when a threshold is met.

So openJiuwen's answer to "where do new capabilities come from" is **an assisted authoring skill with
human review**. That is a fair design for a product where a person is present. It is exactly the design that
the 2026 literature says fails when the person is removed — see `04-*` notes on the blind-curator and
LLM-judge results.

## 9. Where a Capability Capsule attaches

Four sockets already exist. None of them needs a change to openJiuwen `[mine, from the protocols in §3-§6]`:

| Socket | Symphony side | Capsule side |
|---|---|---|
| `CapabilityProvider` / `AtomicCapabilityProvider` `[src: interfaces/capability.py]` | reads an inventory plus a stable `SourceSnapshot` | the capsule library **is** the provider; the snapshot id is the library revision |
| `EvaluationSuite.register()` `[src: evaluation/suite.py:179]` | runs registered metrics, keeps reason and evidence, sets no threshold | the capsule layer registers contract-conformance, held-out-pass, no-regression and duplicate metrics, **and owns the threshold** |
| `SkillGraphUpdater` `[src: interfaces/graph.py:14]` | commits an approved batch as one immutable graph version | the capsule layer calls it **after** admission, with `request_id` = the admission decision id and `source_revision` = the library revision |
| `submit_observation(GraphEvolutionInput)` `[readme §Fast、Beam 与运行时过滤]` | updates edge weights from strongly verified evidence only | the capsule layer supplies the verified run evidence it already collects |

The division of labour that falls out:

```
                     decides / owns                        already provided by Symphony
Capsule layer  ->  the contract (pre/post, effects)   |   identity, content hash, semantic profile
                   held-out tests and the gate        |   9 measurement metrics, evidence records
                   the admission threshold            |   (deliberately absent)
                   version lineage and predecessors   |   immutable graph versions, atomic publish
                   duplicate / specialise decision    |   Skill equivalence groups (default off)
                   execution and its sandbox          |   (Symphony never executes)
                                          ->  SkillGraphUpdater  ->  graph, retrieval, planning
```

⚠ One overlap to handle honestly rather than ignore: Symphony's retrieval tree has **Skill equivalence groups**
("检索树中的 Skill 等价群"), which deterministically merge Skills whose core capability is the same or close,
across platform, vendor, API/CLI and input-form differences; it keeps apart Skills that share only keywords, share
only an incidental function, or are complementary steps. It is controlled by
`SkillIndexBuildConfig.equivalence_enabled` and is **off by default** `[readme §检索树中的 Skill 等价群]`. That is
openJiuwen's answer to the duplicate problem, at retrieval time. The capsule's duplicate rule acts earlier, at
admission. The design document must say why both are wanted, or drop one.

## 10. Verified negatives, for the design document's "what is missing" table

Each of these is a command anyone can rerun in `openjiuwen/agent-core/openjiuwen/symphony` at `f1d7fd6923a6`:

| Claim | Command | Result |
|---|---|---|
| no pre/postconditions, no effects, no held-out tests, no regression notion | `grep -rniE "held.?out\|holdout\|test_suite\|golden\|regression\|precondition\|postcondition" --include=*.py .` | 0 hits |
| admission appears only as something explicitly *not* done | `grep -rniE "admission\|admit" --include=*.py .` | 3 hits, all disclaimers |
| the per-capability `version` never reaches the published artifact | `models/fingerprint.py:141` | `exclude={"version", "static_data"}` |
| the batch mutation API has no production caller in jiuwenswarm | `grep -rn "add_skills\|update_skills\|delete_skills" --include=*.py` in jiuwenswarm | 1 hit, in a unit test |

## 11. Open questions to settle before writing the design

1. Does the capsule library sit **inside** jiuwenswarm's adapter layer (as a second provider beside the skill
   folder), or beside it as its own service with its own store? The adapter contract allows either.
2. `SymphonyRuntime` composes only orchestration today. Does the capsule layer wire `FingerprintService` and
   `EvaluationSuite` itself, and accept that this changes when openJiuwen finishes the runtime facade?
3. Equivalence groups versus the admission-time duplicate rule (§9).
4. Symphony never executes a capability. Whose sandbox runs the held-out tests, and does it belong to the
   capsule layer or to the harness?
5. The Toronto interns own openJiuwen. Which of the four sockets, if any, would need a change there, and can
   the design be stated so that the answer is "none"?
