# What Symphony is for, how it works end to end, and a correction to note 03

Written 2026-09-18, source read at `agent-core` `f1d7fd6923a6` (2026-09-15).

Marks: `[src]` read in the file named · `[readme]` from `symphony/README.md`, which is Chinese; glosses are
mine and the Chinese is quoted where wording carries weight · `[mine]` my inference.

⚠ **This note corrects note `03-symphony-in-depth.md` and `DESIGN.md` §3.3.** I claimed Symphony has no
admission decision and does not create capabilities. Both claims were **wrong**. Symphony has a complete
capability-creation and admission pipeline in `symphony/flow/`, which I did not open because my greps searched
for `admission`, `precondition` and `held-out`, and that subsystem uses none of those words. The corrected
position is in §5, and it is narrower and more defensible than the original.

## 1. What Symphony is made for

Symphony's own one-line self-description `[readme]`:

> `openjiuwen.symphony` 是 openJiuwen 的能力资产发现、指纹、评估、检索、编排和经验沉淀领域模块

*Symphony is openJiuwen's domain module for capability-asset **discovery, fingerprinting, evaluation,
retrieval, orchestration and experience precipitation**.*

The word doing the most work is **能力资产 (capability asset)**. Symphony's subject is not a tool call and not
an agent: it is an *asset* that exists before and after any run, has an identity, accumulates a quality record,
and can be found, composed, and eventually distilled out of what happened. That is a library-management module,
not an execution framework, and it explains every boundary it draws.

Its stated non-goals are unusually explicit `[readme]`: Symphony does not implicitly guess or scan application
directories, does not read application config, **does not register or execute the caller's capabilities**, and
does not depend on any concrete caller's code. The caller supplies everything through an Adapter. `SkillFolderScanner`
only scans a root the caller explicitly hands it.

The architectural slogan is "**检索用树，编排用图**" — *trees for retrieval, graphs for orchestration*
`[readme]`. Browsing a hierarchy is how an agent narrows down; a relation graph is how a plan gets composed.

## 2. The parts, by weight

`[src: find + wc]` — about 50,000 lines of Python:

| Subsystem | Files | Lines | What it does |
|---|---|---|---|
| `retrieval/` | 97 | 21,140 | capability tree index: build, scanners, search, and its own LLM backends |
| `orchestration/` | 29 | 8,369 | relation graph, candidate generation, matcher, Fast/Beam planners, artifact lifecycle |
| `shared/fingerprint/` | 20 | 5,333 | scanning, semantic profile, IO normalisation, atomic `fingerprint.json` |
| `discovery/` | 6 | 3,225 | skill filesystem and directory toolkits |
| `experience/` | 12 | 2,949 | trajectory parsing, experience library, retrieval over it |
| `flow/` | 11 | 2,734 | **evidence → recipe → capability package → review → install** |
| `agent/` | 2 | 2,336 | the agent-facing toolkit (one 95 KB file) |
| `evaluation/` | 4 | 2,019 | nine registrable metrics |
| `observation/` | 5 | 1,160 | runtime evidence into graph-weight revisions |
| `models/`, `interfaces/` | 12 | 1,134 | the public data model and the four protocols |

⚠ The README's implementation-status table calls retrieval **待迁入 ("awaiting migrate-in")**, yet it is the
largest subsystem in the tree. Independent verification settled what the label means: the code exists and is
lazily exported from `symphony/__init__.py`, so 待迁入 marks **"not yet composed into `SymphonyRuntime`"**
rather than "not written". It has no `API.md` for standalone use, unlike `experience/`, so using it means
reading the source `[verify/V1-symphony-core.md]`.

## 3. The part I missed: `symphony/flow/`

This is a complete capability-creation lifecycle, and `DEFAULT_FLOW_ENABLED = True`
`[src: orchestration/config.py:7]`.

### The data model `[src: flow/models.py]`

Three schema-versioned artifacts: `symphony.experience_recipe.v1`, `symphony.capability_package.v1`,
`symphony.package_review.v1`. Content hashing is canonical-JSON plus SHA-256 (`content_hash`, `sha256_hex`).

```
RecipeEvidence      一条不可变的执行证据  (one immutable piece of execution evidence)
                    trace_id · query · outcome · graph · ingested_at

ExperienceRecipe    可复用编排方案  (a reusable orchestration scheme)
                    recipe_id · version:int · status · grade
                    applicability · combination_structure · execution_narrative
                    quality · provenance · schema_version
```

Three lifecycles are already named, and they are the ones a capsule library needs `[src: models.py:15-40]`:

| Axis | Values |
|---|---|
| `status` | `draft` → `active` → **`deprecated`** |
| `grade` | `candidate` → **`verified`** |
| review `verdict` | `approved` · `rejected` · **`needs_human_review`** |

### The pipeline `[src: flow/engine.py]`

```
ingest(evidence)                  append immutable execution evidence
  → distill()                     deterministic structural distillation
      · mine recurring capability subgraphs from all evidence
      · keep an edge when support >= min_edge_support and success_rate >= min_edge_success_rate
      · compute quality: success_count, execution_count, pack_success_rate
      · resolve_status_grade() -> (status, grade) by threshold
      · narrative distillation of applicability + execution_narrative (LLM, template fallback)
  → _save_recipe_versioned()      versioned recipe storage
  → review_and_prepare_install()  the gate (below)
  → _publish_approved_package()   publish + install preparation
```

Supporting calls: `get_recipe`, `list_recipes`, `get_candidate`, `list_candidates`, `acknowledge_candidate`,
and **`review_history(package_id)`** — an audit trail of every review a package received `[src: engine.py]`.
⚠ Its docstring says v1 returns only the most recent review, but `store.read_reviews()` returns every review
file ever saved for that package id. A docstring-versus-behaviour mismatch, in our favour: the full trail is
there `[verify/V2-symphony-flow.md]`.

`codegen.py` turns a skill pack in JSON Graph Format into a **SwarmFlow script**; `render.py` turns the unified
package into a composed Skill directory; `privacy.py` redacts distilled text and installable materials before
any of it is written `[src]`.

### The gate `[src: flow/review.py]`

`PackageReviewGate.review_static()` runs **ten deterministic checks**, every one of them static:

`_check_structure` · `_check_dependencies` · `_check_code_safety` · `_check_secrets` ·
`_check_artifact_paths` · `_check_integrity` · `_check_meta_naming` · `_check_materials` ·
`_check_permissions` · `_check_license`

⚠ Verification read all ten bodies rather than their names, and reports that `_check_code_safety` is a
**token blacklist** — it searches candidate scripts for forbidden tokens. That is not static analysis and it
is certainly not sandboxing. It is worth knowing how thin the strongest-sounding check actually is
`[verify/V2-symphony-flow.md]`.

Then, and only then, an optional LLM review agent runs. The ordering is the important part
`[src: review.py:96-131]`:

1. static checks first; **if they do not return `approved`, the method returns immediately and the model is
   never called**;
2. **no review agent configured → `needs_human_review`**, with an explicit failed check recording why;
3. **review agent throws → `needs_human_review`**;
4. **agent returns an unrecognised verdict → `needs_human_review`**.

So the model can only ever *downgrade* a statically-approved package; it can never rescue a statically-failed
one, and every uncertainty resolves to a human rather than to a pass. **This is exactly the architecture
DESIGN.md §2.6 proposes — deterministic veto, model advisory, fail closed — and Symphony got there first**
`[mine]`.

## 4. The thresholds, and the number worth arguing about

`resolve_status_grade` `[src: distill.py:377-390]`:

```python
if success_count >= min_successes_verified and pack_success_rate >= min_pack_success_rate_verified:
    return RECIPE_STATUS_ACTIVE, RECIPE_GRADE_VERIFIED
if success_count >= min_successes_candidate:
    ...
```

Shipped defaults `[src: orchestration/config.py:7-13]`:

| Setting | Default |
|---|---|
| `DEFAULT_FLOW_ENABLED` | `True` |
| `DEFAULT_FLOW_MIN_EDGE_SUPPORT` | `1` |
| `DEFAULT_FLOW_MIN_EDGE_SUCCESS_RATE` | `0.8` |
| `DEFAULT_FLOW_MIN_SUCCESSES_CANDIDATE` | `1` |
| **`DEFAULT_FLOW_MIN_SUCCESSES_VERIFIED`** | **`1`** |
| `DEFAULT_FLOW_MIN_PACK_SUCCESS_RATE_VERIFIED` | `0.8` |

⚠ **One successful execution promotes a recipe to `verified` by default.** The grade that reads as a quality
guarantee is, out of the box, evidence of a single success. That is worth raising at the workshop, and it is
precisely the failure the literature keeps describing: a capability scored on the runs it was born from. It is
a configuration default, not a design flaw, and it is trivially changed — but defaults are what ship `[mine]`.

Independent verification traced the whole path and confirmed it, with three caveats I had missed and which
must be stated alongside the claim or it overstates `[verify/V2-symphony-flow.md]`:

1. **The run must contain at least one capability-to-capability edge.** A single solo capability produces no
   recipe at all, so "one execution" means one execution that composed at least two capabilities. The edge
   gate itself is vacuous at n=1: `min_edge_support=1` and `min_edge_success_rate=0.8` are both trivially
   satisfied by a single success.
2. **`verified` is a grade, not publication.** Packaging, the ten static checks and the optional LLM review
   still stand between a verified recipe and an installed capability. The weak threshold governs what gets
   *called* verified, not what gets shipped.
3. **No code in `agent-core` overrides these defaults outside unit tests.** `SymphonyFlowEngine` is
   dependency-injected into `SymphonyRuntime` by an external caller, so whether production uses the shipped
   values is a question about the host application and is not answerable from this repository.

So the accurate sentence for the workshop is: *out of the box, a recipe reaches the `verified` grade on the
strength of a single successful two-capability run* — not *a capability ships after one success*.

## 5. The correction, stated precisely

**What I said in note 03 and DESIGN.md §3.3:** Symphony has no admission decision, no capability creation, and
no version lineage; the capsule layer supplies all three.

**What is actually true:**

| Capability | Symphony | Note |
|---|---|---|
| creates capabilities from execution evidence | **yes** | `flow/distill.py` |
| versioned storage of the created artifact | **yes** | `_save_recipe_versioned`, `version: int` |
| lifecycle states including retirement | **yes** | `draft`/`active`/`deprecated` |
| a promotion grade | **yes** | `candidate`/`verified` |
| an admission gate | **yes** | `PackageReviewGate`, 10 static checks + optional LLM |
| fail-closed to human review | **yes** | three separate paths to `needs_human_review` |
| an audit trail of decisions | **yes** | `review_history(package_id)` |
| content hashing | **yes** | canonical JSON + SHA-256 |

My grep in note 03 searched for `admission|admit|precondition|postcondition|held.?out|test_suite|regression`.
`flow/` uses `review`, `verdict`, `grade` and `distill`. **The words were the reason I missed a 2,734-line
subsystem, and "grep found nothing" was not evidence of absence.** Worth remembering the next time I assert a
negative `[mine]`.

### What is genuinely still missing

The gap is narrower than I claimed and sharper. Symphony's admission is **observational**: it asks "did this
combination succeed often enough in production?" Every one of its ten checks is **static** — structure,
dependencies, code safety, secrets, paths, integrity, naming, materials, permissions, licence. **Nothing
executes the candidate capability to find out whether it works.**

So what the capsule adds, stated exactly:

1. **Behavioural admission, not just static and observational.** A held-out suite, written from the contract
   before any implementation exists, executed in a sandbox. Symphony never runs the candidate.
   ⚠ Sharpened by verification: the *data model* for a golden value already exists —
   `EvaluationCase.expected_output` (`models/evaluation.py:133`), consumed by `AccuracyEvaluator`
   (`evaluators.py:521`). It is caller-supplied, and Symphony neither owns the expected values nor executes
   anything to produce the actual ones. So the gap is execution and ownership, not vocabulary, and the capsule
   layer can express its held-out results **in Symphony's existing evaluation types** rather than inventing
   new ones `[verify/V1-symphony-core.md]`.
2. **A checkable contract.** Symphony's `applicability` is `{task_description, trigger_conditions}`, and both
   are **LLM-distilled prose** with a template fallback `[src: flow/narrative.py:58, engine.py:506-507]`. Prose
   applicability is readable by a planner and checkable by nothing — and prose matching is the exact mechanism
   behind the 21% shadowing loss in DESIGN.md §1.3. The capsule wants preconditions a deterministic gate can
   evaluate against live state.
3. **No-regression against the predecessor.** Symphony versions recipes but never re-tests an old version's
   behaviour against a new one.
4. **Declared versus observed effects.** Symphony has no effect declaration at all, so there is nothing to
   compare a sandboxed run against.
5. **Recurrence as a gate on *building*, not just a statistic.** `min_successes_verified = 1` means the
   threshold exists but is not defended.

That is a better contribution statement than the one in the current draft: **not "Symphony left admission out"
but "Symphony admits on static safety and observed success; the capsule adds behavioural proof against a
contract."** Both are real gates. They catch different things, and a library probably wants both `[mine]`.

## 6. What this changes in DESIGN.md

1. §3.3's table and the "deliberate gap" framing are wrong and need rewriting around §5 above.
2. The §2.6 gate design should **cite Symphony's ordering as precedent** rather than present it as novel.
   Arguing for a design the platform already uses is much easier than arguing for a new one.
3. §5.1 should compare against `symphony/flow/` directly — it is nearer prior art than `skill-creator-normal`.
4. The `needs_human_review` verdict is a third outcome my design does not have. Admit/reject is a binary;
   Symphony's three-way split with fail-closed-to-human is better, and the capsule should adopt it.
5. §7.2's milestones should assume recipes, versioned storage and a review gate **already exist** and are
   extended, not built. That makes M1 and M3 substantially cheaper and the whole plan more credible.

## 7. Still unread

`retrieval/` (21k lines, the largest subsystem and the one the README mislabels), `discovery/`,
`experience/`, and `agent/retrieval_toolkit.py`. The retrieval side is where the shadowing question lives, so
it is the next thing to read.
