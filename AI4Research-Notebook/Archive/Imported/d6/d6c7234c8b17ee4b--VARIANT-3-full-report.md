# AI4Research / OpenSolar — Architecture, Workflow, and Engineering Challenges

**A technical report**

Version 1.0 · 2026-09-10 · against commit `b0bf165f9`, branch `openJiuwen-Solar`

---

## Executive summary

AI4Research (packaged as OpenSolar, runtime name Solar) is a local-first
multi-agent execution framework. It compiles a natural-language goal through
several independently-validated stages into an immutable, hash-verified
execution contract, then executes that contract as a DAG across 102
interchangeable executors — roughly half of which depend on no model vendor at
all.

Its governing thesis is a division of labour:

> **Language models interpret semantics. Deterministic code validates
> structure, maintains references, freezes contracts, and schedules.**

The system serves both software delivery and automated scientific research
through one control plane, and requires research runs to emit structured,
schema-validated evidence rather than prose.

**Five findings this report defends:**

1. **The freeze is the architecture.** A single hash-verified boundary
   separates model negotiation from contract execution. Verification
   *recomputes* every planning stage rather than trusting recorded verdicts,
   and the criteria that will judge a run are frozen into the same hash.

2. **The model is constrained — but not fully prevented — from influencing its
   own assessment.** It cannot author citation spans and cannot edit
   carried-forward constraints. But the third "deterministic derivation"
   operates over a capsule identity the model itself selects; the intent
   fidelity reviewer can be **demoted to advisory** once the repair budget is
   spent; and the requirement semantic review is **advisory by design**. The
   guarantee is real but narrower than the project's own framing suggests.

3. **The system refuses to treat an attempt as an outcome** — at dispatch, at
   verification, and at delivery, independently.

4. **Capability is packaged as declarative units with declared effects** —
   including *risk* as a first-class axis — admitted through a registry that
   functions as a governance gate rather than an index.

5. **It works, once, demonstrably; it is not yet routinely reproducible.** A
   complete 15-node research run passed on 2026-09-03 with all gates passed,
   after a mid-run fix. The pre-release suite retained 34 itemized failures
   that were deliberately not suppressed.

The report also documents where the project's own documentation describes a
system that does not exist, and separates that clearly from what is built.

---

## Contents

**Part 0 — Framing**
§1 Scope and method · §1.3 Why this discipline was necessary

**Part I — The workflow**
§2 Overview · §3 Intake · §4 Intent compilation · §5 Requirement compilation ·
§6 Planning · **§7 The freeze** · §8 Scheduling · §9 Dispatch · §10 Operators
and the fleet · §11 Evidence, claims, delivery · §12 Orchestration

**Part II — Capability capsules**
§13 The abstraction · §14 Inventory · §15 The registry as gate · §16 Anatomy ·
§17 Trust classes · §18 Admission · §19 Lifecycle modules · §20 Design vs
implementation

**Part III — Verification**
§21 Three layers · §22 Result vocabulary · §23 Frozen evaluation policy ·
§24 Rapid smoke · §25 Activation proof · §26 Benchmarks · §27 Gates

**Part IV — Challenges**
§28 Method · §29 Themes · **§29.1 The system caught itself** · §30 Architect
investigations · **§31 Intrinsic vs
incidental** · §32 The deadlock

**Part V — Status and positioning**
§33 Where it stands · §34 Self-claims · §35 Comparative positioning ·
**§35b What is table stakes**

**Part VI — Appendices**
§36 Anticipated questions · §37 Discrepancy ledger · §38 Limitations ·
**§38b Counter-evidence not otherwise covered** · §39 Primary sources

*If you read only three sections: §7 (the freeze), §31 (what generalises),
§33 (actual status).*

---

## 1. Scope and method

### 1.1 What was examined

The source repository at commit `b0bf165f9`: 5,386 tracked files across Python
(control plane), TypeScript/Bun (runtime services), Bash (orchestration), React
(dashboard), and Electron (desktop).

Twelve parallel investigations were run over distinct subsystems — intent
compilation, requirement compilation, planning and freezing, scheduling,
dispatch, claims and evidence, evaluation, orchestration, capsule design
documents, memory and delivery, failure history, and comparative anchors — each
reading code directly and citing file and line.

### 1.2 Evidence discipline

Claims here are marked:

- **[verified]** — confirmed by reading the code or running a read-only query.
- **[doc]** — asserted by project documentation, not independently confirmed.
- **[inferred]** — a reasonable reading, flagged as such.

Nothing was executed: no installer, no test suite, no runtime. Every claim about
runtime behaviour is therefore documentary or static-analytic. This is a
deliberate limitation and is stated wherever it matters.

### 1.3 Why this discipline was necessary

**The project warns you about its own documentation, on its own front page.**
The README opens with a banner that, translated from the Chinese, reads:

> "The default formal path is **Intent Compiler → Requirement Compiler →
> Elastic Planner → frozen SchedulerInput → Scheduler → Operators/Gates**. The
> PRD/Contracts/task_graph compilation diagram below describes the *historical
> compatibility chain* and cannot be used to judge the current typed path. […]
> See the handover entry point, and **do not mistake architectural goals for
> accepted behaviour**."

That last clause is the correct posture toward every document in this
repository, and this report adopts it as a rule: **a design document is
evidence of intent, never evidence of behaviour.**

The warning is not merely prudent — it is *demonstrably necessary*, and the
README itself proves the point. The same banner asserts that "the Requirement
Compiler is still deterministic." **It is not.** The default compiler is now
LLM-based, with the deterministic implementation surviving only as an opt-in
legacy path (§5). The front-page caveat about stale documentation is itself
stale.

Accordingly, during this investigation:

- A claim about system status, taken from a handoff document, proved **wrong**
  because that document was a mid-arc snapshot in an append-only log that
  continued for another 230 lines. Two investigations repeated the error before
  a third resolved the timeline correctly. **In an append-only log, the last
  entry wins.**
- Two large design documents describing the capsule ecosystem proved to be
  **pre-implementation artifacts** whose central constructs have zero
  occurrences in the codebase.
- A documented repair-budget policy proved to have been **superseded** by a
  later commit that the documentation never reflected.

A discrepancy ledger appears at §37.

### 1.4 Naming

**AI4Research** is the repository, **OpenSolar** the packaging, **Solar** the
runtime and CLI (`~/.solar/`). They are one system. `openJiuwen-Solar` is the
main branch name, not a product. "jiuwenswarm" does not occur anywhere in the
tree. **AutoSci** is both the research workload and a real upstream project
this repo tracks parity against.

---

# PART I — THE WORKFLOW

## 2. Overview

```
user request
  → 1. intake
  → 2. intent compilation          LLM + deterministic validation
  → 3. requirement compilation     LLM + independent LLM review
  → 4. planning                    LLM decision + deterministic binding
  → 5. FREEZE                      immutable hash-verified contract
  → 6. scheduling                  deterministic DAG execution
  → 7. dispatch                    leased, scoped, idempotent
  → 8. operators and gates         capsules execute, evaluators judge
  → 9. delivery                    plan → draft → review → deliver
```

Three structural properties matter more than the stage list.

**It can refuse.** Intent compilation that fails validation or requires
clarification halts the pipeline. The planner may conclude the correct response
is a direct answer with no execution graph. Refusal and direct response are
first-class outcomes.

**Even trivial requests traverse the full compile chain.** A simple question
still passes through intent, requirement, and planning; the planner may then answer directly. The system does not fabricate a multi-node DAG to look busy,
nor does it let a request skip compilation by carrying a tag. [doc]

**Everything before the freeze is negotiation; everything after is contract
execution.** Bounded repair loops operate before the freeze. Nothing downstream
may renegotiate.

## 3. Stage 1 — Intake

Requests arrive through an HTTP status server (`ThreadingHTTPServer` bound to
`127.0.0.1:8765`, falling back through 8775; bound to `0.0.0.0` under WSL NAT,
with a token enforced only off-loopback) or through the `solar-harness.sh` CLI.
[verified]

Attachments enter as references rather than inline content. The intake returns
a session and intake status; it does not itself decide admissibility.

## 4. Stage 2 — Intent compilation

**Entry:** `harness/lib/intent_gateway.py` → `intent_compiler.run_pipeline`.

**Normalisation.** `normalize_input()` re-projects the raw request into a
canonical form, SHA-256 checked, failing closed on mismatch or empty text.
[verified]

**IntentIR v3** splits a *mechanical envelope* (11 required fields) from a
*semantic body* (goals, outcomes, constraints, ambiguities, conflicts,
unknowns). The model does not fill the whole schema — it fills a narrower
**authoring** schema. [verified]

**The critical detail:** deterministic code re-binds `source_quotes` into
`source_spans` itself. **The model never authors citation coordinates.**
Provenance is therefore structurally un-fabricable: the model cannot point at
text that is not there. [verified]

**Four artifacts, four questions.** The stage emits not one product but four,
each with its own schema:

| Artifact | Question | Author |
|---|---|---|
| IntentIR | what was asked? | model |
| validation | is it structurally sound? | deterministic code |
| fidelity | does it faithfully reflect the request? | **a second, independent model call** |
| acceptance | may we proceed? | deterministic gate |

The fidelity reviewer **cannot rewrite the artifact and cannot claim spans** —
it may only find fault. Generation and grading are different code paths by
construction. [verified]

**Refusal is enforced twice, in two modules.** `capture()` returns early with
`allow_autodispatch=False` on any non-accept decision, and `requirement_handoff()`
independently re-verifies both the decision and the SHA-256 before the next
stage may run. Defence in depth against out-of-order invocation. [verified]

**Budget — and a hole in the guarantee.** `SOLAR_INTENT_MAX_REPAIRS`, default
1, capped at 4. After exhaustion, only fidelity findings — never deterministic
errors or blocking ambiguities — may be demoted to advisory warnings, in
`_demote_exhausted_fidelity_findings()` (`intent_compiler.py:1230-1263`).
[verified]

**What this does and does not mean.** It is a *bounded, disclosed, deliberate*
escape valve, not an oversight. The function's docstring states the reasoning:

> "The reviewer can propose the one compiler repair, but it is not a second
> admission authority. Deterministic validation, explicit ambiguity and
> explicit conflict handling remain blocking. Preserve the reviewer's original
> severity and proposed change so the diagnostic is auditable."

So: only *subjective fidelity* findings are demoted — never deterministic
errors, explicit ambiguities, or conflicts, all of which stay blocking — and
the original severity is preserved for audit. The design decision is that a
review model must not become a second admission gate.

It is still a real limit on the guarantee, and worth stating plainly: a
fidelity objection **can** end up advisory. Reviewer independence is also
configured by `SOLAR_INTENT_REVIEWER_MODEL`. The honest summary is that the
no-self-grading property holds for structure and provenance, and is
deliberately softened for subjective judgement.

**Handoff.** The accepted IntentIR object, its SHA-256, and the acceptance
record. Not raw text. [verified]

## 5. Stage 3 — Requirement compilation

**Entry:** `harness/lib/requirement_compiler/semantic.py` and `evaluator.py`.

**RequirementIR v2** = an unchanged base envelope **plus** an optional additive
`semantic_contract`. Old readers still validate against the static template;
new readers get a strictly-versioned sub-schema. [verified]

**The compiler was changed from deterministic to LLM-based.** The deterministic
`compile_requirement_ir_legacy` survives verbatim but is opt-in only, currently
unused and untested. [verified]

**Constraint preservation.** The prior stage's constraint structure is deep-
copied into `semantic_contract.source_constraints` and guarded by a hard
equality check that raises
`SOURCE_CONSTRAINT_POLARITY_OR_CATEGORY_CHANGED`. **The model can add
interpretation beside constraints but cannot edit them at all.** [verified]

**Two different reviewers.** `evaluator.py` is the *deterministic* format and
reference evaluator (checks RF1–RF4). The *semantic* review is a separate LLM
call scored against a fidelity contract. These are frequently confused; they
are different mechanisms. [verified]

**Budget — and a documentation trap.** Project documentation describes split
repair counters, a 5-call ceiling, and a blocking review, introduced in commit
`f463b861b`. Commit `5ade9d9f3` **merged them back**: one shared counter, a
**3-call ceiling**, and an **advisory-only** review. Current code and its tests
agree with each other; the documentation was never updated. The code is
authoritative here. [verified by code and `git log -p`]

**This is a relaxed gate, not merely stale documentation — but a reasoned one.**
Commit `5ade9d9f3` changed the semantic review from **blocking to advisory**.
The code states why (`semantic.py:151-152`):

> "Structural compilation may receive one bounded retry. The independent
> semantic reviewer is advisory: deterministic schema/source/registry [checks
> remain blocking]."

The rationale matches the intent stage: an optional model-based judge must not
become a second availability gate on the pipeline. The trade is explicit — an
advisory review cannot stop a semantically poor requirement from proceeding,
while a blocking one would make provider flakiness fatal to every run.

**`selection_authority`** forces every hard retrieval restriction to cite
explicit source authority, enforced by `selection_authority_defects()`.
[verified]

**Anti-guessing by identity, not heuristics.** Discovery nodes bind to the
requirement's `discovery` object only via **exact `contract_id` string match**,
raising `ElasticPlannerError` on mismatch. There is no inference path by which
discovery could guess the wrong topic. [verified]

**Frozen enums.** Registry check IDs and intent source IDs are frozen as literal
JSON-Schema `enum` values in the schema actually sent to the provider, verified
by a test that inspects the over-the-wire schema. [verified]

**Handoff** is hash- and identity-exact: `requirement_ir_ref.sha256`,
`retrieval_contract_ref` equality, and delivery-manifest fidelity are all
checked deterministically before plan admission. [verified]

## 6. Stage 4 — Planning

**Entry:** `elastic_planner.py::run_elastic_planning_request`, which chains
`run_semantic_planning_pipeline` → `compile_and_freeze_execution_bundle` →
`verify_frozen_execution_chain`. [verified]

**Direct response.** The planner may answer from context alone, claiming no
execution. This is independently reviewed by a separate reviewer model and never
produces a SchedulerInput. [verified]

**Capsule binding.** `apo_plan_compiler.py` (`build_capsule_plan_node`,
`enumerate_physical_candidate_decisions`) binds abstract role → capability
capsule → physical operator, enforcing `operator_compatibility.forbidden` as a
**hard exclusion**. [verified]

**Deterministic derivations — the key point.** `unsatisfiable_nodes`,
`effect_union`, and `proof_obligations` are computed deterministically from
static capsule manifests. **They are not model output.** The run's declared
blast radius and its admissions of failure cannot be hallucinated. [verified]

**Plan schema enforces completeness.** In `capsule-plan.v1`, a node with
`selected: true` **must** carry a capsule id, dispatch task type, role, artifact
types, effect union, proof obligations, and at least one stage. A node with
`selected: false` **must** carry `unsatisfiable` and have **zero** stages. There
is no third state; a half-bound node cannot be represented. [verified]

**`binding-trace.v2`** audits requirement → owning node, artifact, and verifier.
It is a hard acceptance gate, giving per-requirement traceability. [verified]

**Budget.** `SOLAR_PLANNER_MAX_REPAIRS`, clamped to [0,4], default 1. [verified]

**Dead code, deliberately warned about.** `static_execution_compiler.compile_bundle`
is unused in the pipeline. Documentation warns against calling it as a "second
authoritative compile" — a real hazard, since the planner now freezes
internally. [verified]

## 7. Stage 5 — The freeze

This is the architecture's hinge and deserves its own treatment.

**What is produced.** `compile_and_freeze_execution_bundle` emits ten or more
chained artifacts terminating in `capsule_plan.json`, `physical_plan.json`,
`evaluation_plan.json`, `scheduler_input.json`, and `run_contract.frozen.json`.
[verified]

**How it is sealed.** Canonical-JSON SHA-256 (`sha256_payload`) chains every
artifact by reference. `contract_sha256` hashes the frozen dictionary minus
itself. [verified]

**Why it is more than a checksum.** `verify_frozen_execution_chain`
(`elastic_planner.py:7748-8052`) **recomputes every stage — including re-running
`compile_scheduler_input` — rather than trusting stored verdicts.** A tampered
or stale bundle fails even if its own recorded verdict says "pass".
Verification re-derives and compares; it does not read a claim. [verified]

**What else is frozen.** The `test_policy` — the rules by which the run will be
judged — is frozen into the SchedulerInput hash. [verified]

**What the hash does and does not cover.** An earlier draft of this report
claimed that `write_scope` and artifact-name text sit outside the integrity
boundary and are mutable post-freeze. **That claim was wrong and is retracted.**

Direct verification: `verify_runtime_projection`
(`scheduler_input.py:849-961`) compares *every* field of the frozen-derived
expected node against the runtime node, and additionally rejects any extra key
not present in a 54-name allowlist
(`RUNTIME_PROJECTION_NODE_FIELDS`, `scheduler_input.py:42`), returning
`SCHEDULER_RUNTIME_PROJECTION_TAMPERED`. **`write_scope` is not in that
allowlist**, so it is compared and protected. The check is invoked from at
least eight production call sites, including `operator_runtime.py:102`,
`graph_scheduler.py:3138` and `:4111`, `graph_node_dispatcher.py:278`,
`multi_task_runner.py:3548`, and `execution_authority.py:260`. [verified]

The one genuinely mutable-and-undetected field is **`human_review`**, which *is*
in the allowlist — deliberately, since human review state must change at
runtime. That is a design decision, not a gap.

**The freeze holds.** State it as strong, and note only that mutable runtime
state (assignments, attempts, dispatch ids, human review) is allowlisted by
design.

> Before the freeze the system is negotiating with a model.
> After it, the system is executing a contract.

## 8. Stage 6 — Scheduling

**Projection.** `scheduler_input.py::prepare_runtime_graph` builds the runtime
graph; `verify_runtime_projection` **fully re-derives the projection from the
frozen source and byte-compares it**. This is anti-tamper, not a shape check.
[verified]

**The immutable/mutable split.** The frozen contract holds static node fields
and hash-pinned references. A separate `task_graph_state.json` ledger holds
status, attempt counts, leases, dispatch ids, revision, and events. The contract
never moves; only the ledger does. [verified]

**Node lifecycle.** Roughly 14 statuses across pending, active, terminal, and
human-review groups, funnelled through `set_node_status`, `mark_node_result`,
and `enter_node_human_review` / `commit_human_review_resume`. [verified]

**Readiness.** `ready_nodes()` walks `topo_order()` — Kahn's algorithm, cycles
raise `ValueError` — gated by dependency-pass status and a policy-conditioned
human-review carve-out. [verified]

**Write-scope conflicts.** `write_scope_conflict` performs prefix-overlap
detection; **a missing scope is treated as exclusive-writer**, which is the
fail-safe direction. Batched by `_batch_ready_nodes` alongside effect-based
exclusivity. [verified]

**Concurrency.** `concurrency_policy.effective_max_parallel`, dynamic
backlog-autoscaled limits, and builder-pool replica grouping. [verified]

**The tick.** `graph_scheduler.py` is a pure function library with no loop.
`multi_task_runner.py` drives progress with `while True: schedule_once();
sleep(interval)`. [verified]

**Failure propagation.** `terminalize_dependency_blocked_nodes` auto-skips
downstream nodes; `reopen_recovered_dependency_nodes` can reverse this, guarded
against reopening passed or terminal-sprint nodes. [verified]

**A schema that is not enforced.** `harness/schemas/task-graph-state.schema.json`
exists but is **loaded nowhere** on the executing path — grep-confirmed, and
its field shape does not match the real ledger. The project's own onboarding
document says so. It is therefore not an enforced contract. [verified]

## 9. Stage 7 — Dispatch

**Filesystem mailbox, not RPC.** `operator_runtime.submit()` writes an inbox
JSON file; the `operatord.py` daemon consumes it and writes `result.json`. All
guarded by `flock` plus atomic temp-rename. Any language that can read and write
files can host an operator. This is the same seam the TypeScript↔Python
`codex-bridge` uses. [verified]

**Idempotency.** `capsule_execution_gate.py` fingerprints the envelope with
`sha256(json.dumps(sort_keys=True))`, deduplicates on task id plus fingerprint
via `dispatch-dedup.json`, and rate-limits via `capsule-cooldown.json`. A
scheduler retry cannot re-run expensive work. [verified]

**Leases.** `operator_runtime.py` uses a per-operator lease file with dead-PID
and stale-heartbeat reclaim. `actor_lease.py` implements a fuller state machine
(`READY/LEASED/RUNNING/FINALIZING` plus exception states) but sits on the
less-used path. [verified]

**A partially-wired control.** `capability_token.py` describes file, shell,
network, and git allow/deny scopes — but its `check_path_access()` method has
**no production callers** (only its own definition and one test).
Actual filesystem confinement is enforced by `operatord.py`'s allowed-output-
roots and staged-publish mechanism. The token layer is therefore designed but
not wired. [verified by grep]

**Backends.** `_build_command` dispatches `claude-cli`, `command`,
`research_operator_registry`, and `local/dummy/echo`, with an unknown-backend
no-op fallback. `physical-operators.json` names a `desktop_bridge` value for
which **no dispatch branch exists**. [verified]

**Provider redirection.** `ANTHROPIC_BASE_URL` is overridden inside
`_claude_print_command()`, pointing the same `claude` CLI at an
Anthropic-compatible endpoint when the provider is GLM/Zhipu. [verified]

**Receipt is not evidence.** `research_orchestration/dispatch.py` returns
`status: "awaiting_external"`. Real evidence is the chain
`result.json` → `graph-callback.json` → evaluator `eval.json` PASS. [verified]

## 10. Stage 8 — Operators, and the operator fleet

**Logical operators (45).** Abstract roles with graded requirements, e.g.
`DeepArchitect` requires `architecture_reasoning: 4`, `long_context: 3`,
`multi_agent_coordination: 3`, with `cost_hint` and concurrency limits. Fifteen
capability dimensions are in use; the most common are `scientific_evidence`
(20 operators), `research_synthesis` (14), and `data_extraction` (8). Roles skew
research-ward: nine knowledge-extractors, six evaluators, four builders, three
planners, and 15 `scientific-*` roles. [verified]

**Routing.** 44 of 45 roles are bound to ordered candidate lists averaging 2.75
candidates, with conditions `always` (74), `quota_ok` (24),
`plugin_autosci_available` (20), and `emergency_only` (3). [verified]

**A dead selector, a live mechanism.** `unified_selector.py` parses these
conditions and has **no production callers** — but `logical_operator_router.py`
reads the same `bindings` key and *is* imported by `actor_runtime.py`. One
implementation is dead; the binding mechanism is live. [verified by grep]

**⚠ A name collision worth flagging.** Two unrelated things are called
`bindings`: the routing candidate lists in `logical-operators.json`, and the
`skills` / `mcp_capabilities` / `required_guard_capsules` block inside a capsule
manifest. Different concepts, same word, both load-bearing.

**Physical operators (102), in two families:**

| Family | Count | Character |
|---|---|---|
| Vendor-neutral native | 52 | Defined by the **absence of a `provider` field**. **19** carry `model_provider_neutral: true`, of which **18** have the full triple (adding backend `research_operator_registry` + `execution_trust: evidence_transform`; the 19th is `measured_execution`). The remaining **33** (e.g. `autosci-paper-ingest-worker`) leave those fields null and use backend `command`. |
| Provider-bound | 50 | OpenAI 15, Anthropic 11, Google 7, local 5, browser 5, GLM 4, DeepSeek 3 |

63 of 102 are enabled; 93 are marked available. Roughly half the fleet has no model vendor. Note the qualifier: only 63 of 102
operators are enabled, so the *enabled* split is not necessarily 52/50.
[verified]

## 11. Stage 9 — Evidence, claims, and delivery

### 11.1 The evidence ABI

**33 schemas** in `harness/schemas/evidence/` define every research artifact,
sharing a common envelope with hash-checkable artifacts and provenance.
[verified] *(Note: the onboarding document names only about seven of these; it
describes a subset, not the ABI.)*

### 11.2 The claim lifecycle

```
literature_discovery → research_paper → research_method
                                      → research_claims → claim_verdict
                                      → scientific_report_plan → scientific_report
                                      → publication_bundle
```

**The anti-fabrication mechanism.** A claim in `research_claims.v1` carries a
`citation_span` including **`source_text_sha256`** — hash-binding the claim to
the exact source text. A fabricated citation is structurally detectable rather
than merely unlikely. [verified]

**Verdicts** are drawn from a closed set, with anti-upgrade, overclaim, and
scope-mismatch checks. An outcome with no collected results maps to
*inconclusive* — **never** to *supported*. [verified]

**Separation of powers by contract.** Discovery does not ingest; ingestion does
not verify. The literature-discovery capsule states outright that it "does not
ingest selected papers directly", "does not mutate durable research memory
directly", and that "scientific reliability is not self-certified at discovery".
The pipeline's stages are forbidden from doing each other's jobs. [verified]

**Study protocol.** Discovery must record search strategy, source selection,
time range, inclusion and exclusion criteria — and **unresolved fields must
remain explicitly unresolved rather than be invented**. [verified]

### 11.3 Memory — and a scoping warning

**There are two unrelated memory systems**, and much of the documentation
describes the wrong one:

| System | Wired into this pipeline? |
|---|---|
| Harness research memory — `context_store.py`, `context_projection.py`, evidence-gated capsule updates | **Yes** |
| `core/ontology/` — Big-Five personality, episodic/semantic/procedural memory for the assistant itself | **No** |

Many `docs/MEMORY_*.md`, `ONTOLOGY_*.md`, and `PERSONA_ENGINE_DESIGN.md` files
describe the second. **There is no research-paper knowledge graph called
"ontology" in this system.** `mempalace` and a vendored memory daemon are
off-by-default standalone components with no capsule references. [verified]

**How context is actually assembled.** `context_projection.py` builds a budgeted
projection — default **8,000 tokens** — over an append-only session event log:
retain high-value events, summarise low-value ones, drop on overflow, redact
secrets, with fail-open knowledge-base lookups. This is the concrete answer to
"how does it avoid stuffing everything into a prompt". [verified]

**Durable memory is evidence-gated.** `memory_update_gate.py` and
`graph_update_gate.py` require `evidence_ids`; deletion requires an
`approval_ref`. [verified]

### 11.4 Delivery

```
report-plan → (optional) plan review → draft / synthesize → deliver → (optional) publication
```

Report plan and report are **deliberately separate schemas**: the plan is strict
and closed (purpose, requirement bindings, study protocol) and decides which
claims are includable; the report is a looser narrative contract. Markdown never
replaces structured evidence. [verified]

**Acceptance is not completion.** `acceptance_closeout.py` distinguishes
*finished* (dispatched) from *accepted* (external evaluator verdict PASS **and**
graph status flipped). `accepted-artifact-export.py` applies a stricter gate
again for export. [verified]

## 12. Orchestration and the control plane

**Incarnations and sprints.** An incarnation is a tmux pane running one persona
(pm, planner, builder, evaluator, plus lab); a sprint is a status/contract/events
triple. A default start launches four panes. [verified]

**Coordination.** `coordinator.sh` polls sprint status files and dispatches via
tmux `send-keys`. Two historical bugs are instructive: `send-keys` sending text
and Enter together outran the CLI's input buffer and dropped the Enter (fixed by
splitting with a delay); and on macOS APFS, editing file *contents* does not
update the parent directory's mtime, so directory-level change detection missed
updates entirely (fixed by per-file mtime scanning). [verified]

**Pane leases.** A `flock` plus JSON TTL scheme prevents concurrent `send-keys`
racing into a single-threaded terminal UI. [verified]

**Autopilot** reclaims dead panes, resolves deadlocks, diagnoses fault classes,
and drains queues. [verified]

**Event ledger.** SQLite WAL plus JSONL dual-write, in a strict order: SQLite
must succeed before JSONL. [verified]

**Distribution — two unrelated things.** `core/hive/` implements mDNS discovery
(port 9876), P2P transport, coordinator election, and a task-bidding protocol.
**It is decision-only**: `onTaskAssigned` merely logs to console and
`onTaskCompleted` only updates a credits ledger (`core/hive/index.ts:167-195`),
with **zero** cross-references between `core/hive/` and `harness/`. Actual remote
execution uses a separate, conventional SSH/rsync push driven by
`actor-hosts.json`. HIVE is therefore not working distributed execution.
[verified]

---

# PART II — CAPABILITY CAPSULES

## 13. The abstraction

A **Capability Capsule** is a single YAML manifest describing one unit of
capability. Conceptually it is a function signature that also declares its side
effects, its obligations, and who is permitted to invoke it.

The design intent is stated as a critique of the prevailing Skill / MCP / Agent
model: [doc]

| Problem | Symptom | Consequence |
|---|---|---|
| Fuzzy boundaries | unknown what resources will be touched | security risk |
| Nondeterministic execution | unknown whether it will finish | poor reliability |
| Unclear ownership | when it breaks, nobody owns it | unmaintainable |
| Not composable | capabilities cannot be reused together | duplicated work |
| Unverifiable | only testable, never provable | latent defects |

The capsule answers each with a declaration: declared effects, declared
pre/postconditions, declared owner, declared composition edges, declared
verification.

## 14. Inventory

| Metric | Value |
|---|---|
| Registered capsules | **80** |
| — `capability` | 77 |
| — `guard` | 1 (`guard.secret-leak-guard`) |
| — `resource` | 2 (`resource.github-readonly`, `resource.repo-workspace`) |
| Manifests resolving on disk | 80 / 80 — zero dangling |
| Unregistered files on disk | 5 — inert by design |
| Registry file | 950 lines |

All verified by parsing the registry and reconciling against disk.

> **Correction to project documentation:** the onboarding document states 68
> registered manifests. The true current figure is **80**.

Manifests live in two directories — `harness/config/capability-capsules/` (41)
and `harness/capability-capsules/` (39) — with `manifest_path` resolved relative
to the registry file's own directory, so `../capability-capsules/` reaches the
second store.

## 15. The registry is a gate, not an index

Registration is the admission decision. Five capsule files exist on disk
**unregistered and therefore inert**:

```
cap.gemini-enhanced-search.yaml
cap.chatgpt-browser-agent.yaml
cap.notebooklm-enrichment.yaml
cap.advanced-optimization-reference-worker.yaml
cap.research-report-draft.yaml
```

Three are external-provider integrations. Leaving them written but unregistered
implements the project's "component-gated and off by default" policy at capsule
granularity. Directory scanning to auto-activate is explicitly forbidden.

This is a governance boundary expressed as a concrete artifact rather than a
policy document.

## 16. Anatomy

Eleven required sections, per `schemas/draft/capability-capsule.v1.draft.json`:

| Section | Consumed by |
|---|---|
| `capability_capsule_id` | identity |
| `capsule_kind` | admission |
| `metadata` | humans |
| `applicability` | planner selection |
| `contract` | validation |
| `composition` | composition search |
| `effects` | security and audit |
| `bindings` | resource and skill resolution |
| `verification` | gates |
| `operator_compatibility` | binding |
| `provenance` | accountability |

Plus `implementation` (trust class and entrypoint), present in practice though
not in the required list.

### Worked example — `cap.research-literature-discover`

**Applicability**, including negative signals:
```yaml
task_types:       [scientific-research, literature-discovery]
positive_signals: ["discover papers", "arxiv recommendations", "literature shortlist"]
negative_signals: ["mutate wiki", "verify claims"]
```
Negative signals prevent the planner reaching for discovery when asked for
verification. Declaring when a capability must *not* apply is uncommon.

**Effects**, on six axes — note `risk` as first-class:
```yaml
read:    [schemas/evidence/literature_discovery.v1.schema.json]
write:   [artifacts/scientific/literature_discovery/]
execute: [plugins/autosci/.../evidence/registry.py]
network: [required public scientific search APIs and paper metadata feeds]
cost:    [bounded discovery and ranking cost]
risk:    [source APIs may be stale, unavailable, or biased]
```

**Invariants** — the load-bearing honesty guarantees:

> - A completed result never falls back to fixtures, synthetic candidates, or
>   memory-only candidates.
> - Scientific reliability is not self-certified at discovery; downstream
>   ingestion and claim verification decide evidentiary support.
> - Does not ingest selected papers directly.
> - Does not mutate durable research memory directly.
> - Missing protocol parameters remain explicitly unresolved rather than being
>   silently invented.

**Operator compatibility**, with a hard exclusion:
```yaml
preferred: [autosci-literature-discover-worker]
forbidden: [BackendFullWorkflowRunner]
```

## 17. Trust classes

```python
EXECUTION_TRUST_CLASSES = {
    "measured_execution",       # ran something and measured it
    "evidence_transform",       # reshaped existing evidence
    "fixture_or_adapter_only",  # test or glue only
    "unspecified",
}
PLANNER_EXECUTION_TRUST_RANK = {"any": 0, "evidence_transform": 1, "measured_execution": 2}
```

A goal requiring measured evidence cannot be satisfied by a capsule that merely
transforms evidence. This is a **structural block on an agent claiming it ran
an experiment**.

> **Open discrepancy:** `capsule_composition.py` defines an ordered *rank*,
> while `apo_plan_compiler.py` enforces `execution_trust` as an **exact-match
> gate**. The working hypothesis is that rank filters during search while exact
> match governs plan-node compilation. This report does not assert a single
> mechanism; both call sites are cited. See ledger item 9 in §37.

## 18. Admission

`capability_admission.py` is 35 lines and rejects on five grounds:

```
CAPSULE_NOT_STABLE                # status != stable
VERIFICATION_CONTRACT_MISSING     # no self-checks / pass conditions / external requirement
IMPLEMENTATION_UNDECLARED
NO_SELECTABLE_PHYSICAL_OPERATOR
TASK_TYPE_UNDECLARED
```

Its docstring supplies the necessary caveat:

> "Declaration checks are not live execution evidence. Per-node
> I/O/effect/trust checks and dynamic operator availability remain separate
> deterministic gates."

Admission is **necessary, not sufficient**. Being admitted means well-formed and
bindable — not that it will work.

*Note: admission reads `verification.self_checks`,
`implementation.declared`, and `operator_compatibility.selectable_preferred`,
none of which are raw manifest field names — implying it operates on a
normalised form produced by the compatibility loader.* [inferred]

## 19. Lifecycle modules

| Concern | Module | Lines |
|---|---|---|
| Registry, loader, runtime gate | `capability_capsules.py` | 1,423 |
| Static admission | `capability_admission.py` | 35 |
| Composition search | `capsule_composition.py` | 703 |
| Pre-dispatch gate | `capsule_execution_gate.py` | 194 |
| Node capability hints | `capability_inference.py` | 279 |
| Activation proof | `capability_activation_proof.py` | 871 |
| Use→effect telemetry | `capability_effects.py` | 203 |
| Lease scoping | `capability_token.py` | 105 |
| Plugin capability store | `capability_registry.py` | 305 |

**Composition search** performs a bounded typed search over the capsule graph
using the artifact-type registry (76 types), validating against a schema and
hashing payloads with SHA-256 for reproducibility.

> **Observation, not defect:** `artifact-conversions.v1.json` contains **zero**
> conversions, although three `adapter.*` capsules are registered for artifact
> conversion and the conversion registry is loaded by composition search. The
> adapters exist; the conversion graph is empty. Whether composition is intended
> to operate on exact type matches only is an open question.

## 20. What is design rather than implementation

Two large design documents — `CAPSULE_ARCHITECTURE.md` (986 lines) and
`CAPSULE_ECOSYSTEM_DESIGN.md` (1,139 lines) — were read in full and
cross-checked against code. **Both are pre-implementation design artifacts.**

Grep-verified as having **zero occurrences** in `harness/` or `core/`:

- `capsule://ns/name@version` URI addressing
- `capsule.invoke` JSON-RPC protocol
- SCARE numeric scoring
- the federated multi-vendor marketplace, Ed25519 signing, trust tiers

Further divergences:

| Design documents | Implementation |
|---|---|
| 6-section YAML contract | 11-section schema, largely disjoint |
| URI-addressed capsules | dot-namespaced ids (`cap.foo`) |
| no mention of guard/resource kinds | both exist |
| no `operator_compatibility` | central to binding |
| SCARE as 5 qualitative properties (doc 1) **and** a 0–100 score (doc 2) | neither implemented |

**On "formal verification":** the documents use terms such as *symbolic
verification* and *termination analysis* with no accompanying method. **There is
no formal-verification formalism in this system.** "Verification" means schema
validation, string-expression pre/postconditions, and prose invariants. Any
positioning against formal-methods literature must be on those terms.

The **SCARE** mnemonic (Safety, Completeness, Accountability, Risk, Evolution)
may be presented as *stated design intent*. It must not be presented as an
implemented property model.

---

# PART III — VERIFICATION

## 21. Three layers, three authorities

| Layer | Authority | What it can prove |
|---|---|---|
| **Journey tests** (25) | primary acceptance evidence | that a realistic task completed through production entrypoints |
| **Regression tests** | detects breakage, localises faults | **not** the product verdict |
| **Atomic matrix** (142 L2 features, 1,502 reviewed rows from 2,047 historical) | diagnostic only | detailed behaviour; **never overrides journey evidence** |

## 22. The result vocabulary

| State | Meaning |
|---|---|
| `PASS` | realistic task completed; minimum success conditions met |
| `PASS_WITH_KNOWN_LIMITATIONS` | core completed; a real variant or edge case remains |
| `FAIL` | an implemented path failed, or output missed minimum conditions |
| `NOT_TESTED` | no accepted journey exercised it |
| `ENVIRONMENT_BLOCKED` | a *named* platform, credential, or provider prevented execution |
| `NOT_AVAILABLE` | the behaviour is not implemented |

Two rules give this teeth:

> "A journey may prove only the feature paths that it actually exercised."

> "Do not weaken a success condition or delete a known limitation merely to turn
> a result green."

Results may never be copied across file formats, platforms, providers, or
failure branches. Distinguishing *environment-blocked* and *not-available* from
*failure* is the difference between an honest and a flattering status report.

## 23. Frozen evaluation policy

`test_policy` — the evaluator bindings and rules that will judge the run — is
**frozen into the SchedulerInput hash** at plan time. Evaluation budget is
risk-tiered and capped at one semantic evaluator. A run therefore cannot alter
how it will be graded. [verified]

## 24. Rapid smoke mode

`SOLAR_TEST_MODE=rapid_smoke` injects a frozen reduced `test_policy` via
`elastic_planner_adapter.py::_trusted_test_policy`. It is **environment-variable
only and structurally not promptable** — no keyword in a user request or
operator output can enable it. [verified]

It reduces evaluation cost. It does **not** prove quality: a documented incident
records a rapid PASS receipt that did not prevent an **empty discovery** being
handed downstream.

## 25. Activation proof

`capability_activation_proof.py` asks *"can this actually be used?"* rather than
*"is the status green?"* — four conceptual checks across thirteen proof
functions:

1. Default dispatch text carries intent and capability context.
2. DAG graph-node dispatch receives the same context.
3. Real runtimes produce observable artifacts.
4. **Negative controls**: unrelated capabilities are *not* falsely selected.

Coverage telemetry (`broker_coverage`) derives from an append-only
`events.jsonl` ledger: total actions, contracted actions, coverage percentage,
unscoped writes, policy denials, lease denials, pending human approvals.

Its stated boundary is a model of intellectual honesty:

> "No benchmark can prove an LLM's private reasoning. We prove the
> worker-visible prompt/context, runtime calls, and produced artifacts."

`capability_effects.py` complements it by correlating three observable
artifacts — the dispatch intent file (what was made visible), handoff and
evaluation files (what the worker actually cited), and resource-usage telemetry
— and likewise disclaims access to private reasoning.

## 26. Benchmarks

A benchmark-adapter layer names real published benchmarks as integration
targets: **SWE-bench / SWE-bench Pro, Terminal-Bench 2.0 (via Harbor), GAIA,
OSWorld, WebArena, BrowseComp, tau-bench**, with MLE-bench named as future work.
The Terminal-Bench adapter design cites arXiv, GitHub, and vendor sources with
URLs. The layer carries explicit language that it **does not claim a leaderboard
result unless actually run**. [verified]

Internal benchmarks (`agent_arena_benchmark`, `capability_fusion_benchmark`,
`capability_certification_suite`) are wired as CLI subcommands.

## 27. Gates

Roughly fifty scripts under `scripts/`, split into `check-*` gates and `smoke-*`
tests. `check-harness-plumbing.sh` is explicitly **quota-free**: it verifies
install, layout, preflight, coordinator, and dispatch artifact plumbing without
consuming model quota. Live agent behaviour still requires manual verification.

---

# PART IV — CHALLENGES

## 28. Method

Findings are drawn primarily from an 863-line append-only stabilisation log
containing roughly 46 numbered issue rows plus extensive narrative entries, and
from three architect investigations. The log's append-only nature is important:
**later entries resolve earlier ones**, and nearly all numbered rows are
resolved. Reading only the first half produces a badly misleading picture — as
this investigation initially demonstrated on itself.

## 29. Thematic analysis

### (a) Getting schema-conformant output from LLMs

The single largest source of failure. The decisive example: a planning call
returned HTTP 400 `invalid_json_schema` because optional numeric fields in
`operator_requirements` were absent from the projected schema's `required`
array — OpenAI strict mode demands that *every* property appear in `required`.

An earlier instance: a const-only `checkable` field was rejected at the request
boundary with *"schema must have a 'type' key"* — a provider-side constraint,
not a semantic failure of the generated content.

**Provider dialects are not interchangeable.** OpenAI's strict-schema rule,
Gemini's rejection of certain recursive schemas, and Claude's conservative
recursive-contract handling are all genuine, differing constraints. A
multi-provider system needs a schema-projection layer as a first-class
component.

### (b) Separating semantic from structural validation

The unresolved **Discovery semantic-scope defect**: a run's workflow
instruction — "research-type end-to-end research undertaking; one-off answer" —
was treated as mandatory *paper-topic coverage*. Providers returned 11
candidates and relevance accepted 3, but that impossible process-language
coverage requirement emptied the shortlist, and the ingestion node failed with
*"Discovery evidence contains no candidates."* Five downstream nodes cancelled.

The project explicitly refuses the two easy escapes: it forbids adding stopwords
to hide the problem, and forbids attributing it to "unstable LLM intelligence".
Distinguishing *corpus-selection criteria* from *process and deliverable
obligations* inside free text — without hard-coding vocabulary that breaks on
paraphrase, and without relying solely on model judgement — is a genuine open
problem.

### (c) Contract and schema drift

Maintaining both an LLM-facing "authoring" schema and a canonical system schema
for the same artifact is necessary — models need flatter schemas — and
guarantees drift unless a test asserts equivalence. Compounded here by version
identity questions (a "report-plan schema identity" issue was logged and
explicitly left unfixed).

### (d) Attempt versus outcome

Adapters reporting `ok=true, exit 0` while wrapping internally-failed work is a
general hazard for any orchestrator built on subprocess bridges. The system's
answer — evidence-first completion bound to actual ledger content — is a general
pattern rather than a local patch.

### (e) Concurrency and multi-writer state

Local-first coordination over files, tmux, and SQLite requires explicit
versioning and locking or it corrupts silently. The same class of bug —
state-revision regression, terminal input races, frozen-field allowlist drift —
recurred across two eras of the codebase, suggesting a structural cost of
choosing local-first with no external consensus store.

### (f) Brittle natural-language extraction

Report-title extraction recurred across **six** log rows (32, 33, 39, 40, 41,
42). One failure is memorable: the planner wrote *report titled or organized as
"…"*, the strict quoted-title pattern did not match the intervening words, and
an older unquoted fallback captured `or organized as "…` as the title. A
domain-term relevance gate that **fails closed** was eventually added.

A bug recurring six times in one area is design pressure, not carelessness.

### (g) Portability

Windows/WSL friction — directory-handle fsync incompatibility, Node/npm PATH
confusion where WSL finds Windows `npm`, absent sandbox tooling — is real but
incidental to supporting Windows-hosted WSL as a first-class target.

## 29.1 The best evidence for the thesis: the system caught itself

The strongest single piece of evidence that "refuse to treat an attempt as an
outcome" is a practice rather than a slogan is an incident where **the system's
own closure flag was found to be lying, and the project fixed the flag rather
than accepting the pass.** [verified, stabilisation log]

On 2026-09-02 a run froze a 14-node graph, executed every node, and materialised
all eight requested deliverables. The old Publication Gate and run closure duly
recorded **PASS / closed**, with `all_nodes_passed=true`.

Then someone checked the *contents*. The delivered
`research_run_manifest.json` declared, about itself:

```
evidence_gate.status = failed_for_full_requested_scope
closure_status       = open_degraded
failed_gates         = [non-empty]
```

and the delivered `poster.html` displayed "Evidence Gate: Not Passed". Six
sources had parsed, but two were excluded by source assessment, leaving four
selected sources with insufficient method, comparison, and metric coverage.

The project's conclusion, translated:

> "The old closure's `all_nodes_passed=true` conflicts with the research truth
> of the deliverable, so this sprint can only prove physical execution and
> eight-file delivery — it cannot serve as a complete E2E PASS."

**They retracted their own passing run.** The permanent fix was scoped to the
boundary: the Publication Gate now parses the run manifest from the exact
delivery list, and if the manifest declares failed, blocked, rejected, or
not-passed status — or a non-empty `failed_gates` — publication **must FAIL**
and closure may not mark the run completed. A regression test was added with a
negative case that self-reports evidence-gate failure.

This is also a caution for any reader of this report: **`all_nodes_passed=true`
is a flag that has been observed to be wrong.** Prefer content acceptance over
closure flags.

## 30. Architect investigations

- **#001 Coordinator dispatch starvation** — a helper returned a single result
  where an iterate-all loop was required, so only one sprint was ever serviced.
- **#002 Dispatch overlap / terminal race** — driving sub-agents by injecting
  keystrokes into a terminal is inherently racy; the project's own proposed
  remedy is a dispatch-queue model.
- **#003 Multi-builder parallelism** — feasibility analysis for concurrent
  builders.

## 31. Intrinsic versus incidental

The most useful distinction for a reader deciding what generalises.

**Intrinsic — would recur for anyone building this class of system:**

1. Provider structured-output dialects differ irreconcilably; schema projection
   must be first-class.
2. Free-text requirements do not cleanly separate *what to retrieve* from *what
   to deliver*.
3. "Did this actually happen" cannot be certified from exit codes alone.
4. Multi-writer local state needs explicit versioning or it corrupts silently.
5. Maintaining both model-facing and canonical schemas for one object
   guarantees drift.

**Incidental — consequences of this implementation's choices:**

1. The single-sprint scanner bug — an ordinary coding error.
2. The terminal `send-keys` race — a consequence of choosing keystroke
   injection over structured IPC.
3. A stale shell daemon running pre-fix code for 28 hours — a consequence of
   long-lived bash processes without restart-on-change.
4. Windows/WSL friction — a consequence of the chosen deployment target.
5. Version metadata inconsistent across three sources, and two divergent runtime
   lines — consequences of migration and fork history.
6. Report-title regex brittleness — a consequence of parsing a title out of
   prose instead of requiring it as a structured field.

## 32. The deadlock that proves the thesis

Late in development a run stalled. A node had passed its actual frozen gate —
the worker exited 0, the artifact was generated and non-empty, and an
independent evaluation sidecar returned PASS — yet the scheduler refused to
accept it, re-blocking every minute.

The frozen node declared exactly one gate. The frozen evaluation plan contained
no research-quality gate. But the completion-confirmation code **re-inferred
semantics at runtime from capability and path text**, and the node's write scope
contained `final_report_plan.json`, which a `final_report` substring rule
misread as a final research report. It therefore demanded a gate the frozen
contract never required.

The diagnosis names the boundary precisely:

> "This is a conflict between the frozen contract and the Scheduler's post-hoc
> semantic inference — not a Planner output, model call, schema validation, or
> worker failure."

The remedy is a principle, not a patch:

> "The Scheduler may only execute gate IDs already frozen in the EvaluationPlan;
> it must not re-infer semantics from runtime filenames or paths. If a node
> class genuinely requires such a gate, the Elastic Planner must add it before
> freezing, and a pre-freeze validator must reject its absence — rather than the
> Scheduler injecting it after the fact."

Both positive and negative regressions were added: a frozen report-plan node
passes even when its path contains `final_report`; a node explicitly requiring
the extra gate still fails closed when that gate is missing.

This is the clearest illustration of why the freeze boundary matters: the
defect was a component re-deriving meaning after the contract was sealed.

**The fix is real but partial.** Nodes carrying an `evaluation_binding` are
fixed: they require an explicit `research_quality_gate_required=true` and no
longer infer the gate from text. But the **legacy fallback path remains**, and
the same shape — runtime string matching over node fields to infer gate
applicability — is still present in `graph_node_dispatcher.py:2670-2770` and
`evolution_engine.py:240-300` for nodes without that binding. The stabilisation
log records this pattern causing a production stall. So: fixed where the frozen
contract declares a binding, still inferential where it does not. [verified]

---

# PART V — STATUS AND POSITIONING

## 33. Where the system actually stands

**How many runs have passed?** More than one run has recorded
`all_nodes_passed=true`, including two 14-node runs. But **at least one of those
was subsequently retracted by the project itself** after content acceptance
found the deliverable's own manifest declaring an evidence-gate failure (§29.1).
Passing-flag counts are therefore not a reliable measure here, and this report
does not offer one. The 2026-09-03 run below is the project's own
highest-level accepted evidence.

**Demonstrated.** On 2026-09-03, sprint
`sprint-20260903-072109-intent-conduct-an-end-to-end-system-cf3739f6`, driven by
a real prompt plus six attachments, completed **15/15 nodes**, `run_status=completed`,
`all_nodes_passed=true`, `all_required_gates_passed=true`, *closure* (the run's terminal bookkeeping
record) closed, and final runtime revision 530. [verified in the stabilisation log]

**With these caveats, stated plainly:**

1. The run deadlocked mid-flight (§32). A permanent fix was written and
   deployed and the coordinator reloaded (PID 779798 → 828727). The next normal
   scheduler tick then reused the *original* worker artifacts, the *original*
   independent PASS sidecar, and the *original* frozen plan to advance the node.
   No graph was hand-written, no gate fabricated, no model re-invoked.
2. The session timeline file for that run was compacted — deterministically,
   from the authoritative gate ledger's terminal transitions, preserving record
   ids and tagged with its derivation source, with originals backed up and
   hashed.
3. Pre-release regression stood at **606 passed / 34 failed / 8 skipped**. The
   failures were itemised by cause and **deliberately retained** as known debt;
   the log explicitly refuses to relax gates or fabricate artifacts to reach
   green.

**Not demonstrated.** Routine unattended reproducibility.

**Upstream parity.** The project tracks a real upstream, **AutoSci**, across 28
native skills, and reports its own migrated runtime as **not at full parity**
(final runtime verdict `failed`; 0 native-full stages). It deliberately leaves
`coverage_status=full` unused until non-fixture runtime evidence justifies it.

**Recommended formulation:**

> The architecture is built and has demonstrated a complete 15-node end-to-end
> research run with all required gates passed. That run required a mid-run fix
> and coordinator reload, and the pre-release suite retains 34 known failures
> the maintainers declined to hide. Release Candidate maturity — demonstrated,
> not yet routinely reproducible unattended.

## 34. Self-claims

The repository contains a self-authored document scoring the system against
Copilot, Cursor, Windsurf, Claude Code, Devin, Aider, Cline, AutoGPT,
LangGraph/LangChain, CrewAI, and ChatGPT Agent across twelve dimensions. It is
**not independently validated** and should be treated as a statement of intent.
It does concede weaker model flexibility and macOS lock-in.

## 35. Comparative positioning

*This section is pending external research.* A companion briefing document
describes thirteen mechanisms in vendor-neutral terms with thirty-three research questions, for assessment against published work. Provisional judgement: the
individual mechanisms have plausible analogues (lockfiles, effect systems,
capability security, service-mesh indirection, FEVER-style verdict taxonomies);
the *combination* — particularly a hash-verified freeze that recomputes rather
than trusts, and effect-declaring capability manifests with a `risk` axis — is
the part most worth testing for novelty.

## 35b. What is table stakes, and what is not

An expert reader will discount a report that presents ordinary engineering as
discovery. An honest split:

**Standard practice — competent, unremarkable:**

| Mechanism | Why it is ordinary |
|---|---|
| Hash-chaining artifacts | Content addressing is decades old |
| Filesystem work queues | A well-known pattern. Generally inferior to a broker — but a defensible fit here, since it gives language-agnostic operators on a single workstation with no broker to install |
| Leases with stale reclaim | Standard distributed-systems hygiene |
| Idempotency fingerprints | Routine in any retrying system |
| Topological DAG scheduling | Textbook |
| Write-scope conflict detection | Build systems have done this for years. The fail-safe default (undeclared scope treated as exclusive) is the right choice and not universal |
| Logical/physical indirection | Interface versus implementation |
| Declaring effects in a manifest | Package manifests, Android permissions, Docker capabilities |

**Genuinely less common, and worth defending as such:**

| Mechanism | Why it is uncommon |
|---|---|
| Verification that **recomputes** rather than reads a recorded verdict | Most systems trust their own stored result |
| **Evaluation criteria inside the plan's integrity hash** | Prevents a run from re-grading itself; rarely seen |
| Closed verdict vocabulary with **enforced** anti-copy rules | Distinguishing not-tested / environment-blocked / not-available from failure, and forbidding result reuse across variants |
| **Negative applicability signals** on capabilities | Declaring when a tool must *not* be selected |
| **Negative controls** in capability testing | Confirming unrelated capabilities are *not* selected |
| Citation spans **hash-bound** to source text | Aimed squarely at fabricated citations |
| A test layer that **disclaims** what it cannot prove | Rare institutional honesty |

**The unifying virtue, which the mechanism-by-mechanism view hides:** the system
defaults to **fail-closed** in at least six independent subsystems — undeclared
write scope is treated as exclusive; a missing gate declaration fails rather
than passes; discovery with no traceable candidates fails at the next boundary;
an outcome with no results maps to inconclusive, never supported; the
Publication Gate refuses to publish on a self-declared failed manifest; and the
relevance gate added after the title bug fails closed. Consistent fail-closed
defaulting across independently-written subsystems is a cultural property, and
it is harder to achieve than any individual mechanism listed above.

**The fair summary:** the individual parts are mostly known techniques. What is
less usual is the *combination*, and the consistency with which the project
refuses to let a component grade itself. Whether that combination is novel is a
question for external research (§35), not something this report should assert.


---

# PART VI — APPENDICES

## 36. Anticipated questions

**"Is this just a workflow engine with LLMs bolted on?"**
Partly, deliberately. The distinctive parts are that the plan is *compiled from
natural language through validated stages*, that the plan freezes with its own
evaluation criteria inside the hash, and that verification recomputes rather
than trusts. Airflow does not compile intent; an agent loop does not freeze.

**"Does the freeze not make it inflexible?"**
Yes, by design — that is the trade. Adaptation happens in bounded repair loops
*before* the freeze. §32 shows what happens when a component tries to adapt
after it.

**"Has it actually worked end to end?"**
Once, demonstrably, on 2026-09-03, with a mid-run fix. Not yet routinely
unattended. See §33.

**"Is 80 capsules a lot?"**
It is enough to cover the research lifecycle and part of software delivery. The
more informative number is 52 of 102 executors being vendor-neutral.

**"What is formally verified?"**
Nothing, in the formal-methods sense. Despite the vocabulary in the design
documents, verification here is schema validation, string-expression
pre/postconditions, and prose invariants. §20.

**"Why two directories of capsules and two things called `bindings`?"**
Accumulated history. Both are real and both are load-bearing; see §14 and §10.

**"What is the weakest part?"**
Three candidates: the unresolved discovery semantic-scope defect (§29, theme b); the
capability-token layer being designed but not wired (§9); and documentation that
describes an unimplemented ecosystem (§20).

**"Your §17 says trust classes are enforced two different ways. Which is it?"**
Unresolved, and flagged as such. `capsule_composition.py` defines an ordered
rank; `apo_plan_compiler.py` enforces exact match. The likely explanation is
that rank filters during search and exact match governs plan-node compilation,
but this report does not assert that. It is ledger item 9 and the most
exploitable gap in the document — concede it rather than defend it.

**"What does a run cost, and how long does it take?"**
Not measured here. Nothing was executed. The plan declares a `cost_hint` per
logical operator (28 low, 9 medium, 7 high) and evaluation budget is
risk-tiered and capped at one semantic evaluator, but no wall-clock or token
figures were gathered. An honest "we did not measure it" is the answer.

**"Is the effect declaration actually enforced at runtime, or just documented?"**
Partly unknown, and this is a genuine weakness. Effects are *declared* in every
manifest and the union is computed deterministically at plan time. But the
adjacent permission control — `capability_token.check_path_access()` — has no
production callers, and no code path was found that gates dispatch on the
declared `risk` axis. Treat declared-and-enforced as an open question.

**"Why should we trust this report?"**
Every claim is marked verified, documentary, or inferred, and §1.3 and §37
record where this investigation was itself wrong. Nothing was executed, so all
runtime claims are static or documentary.

## 37. Discrepancy ledger

| # | Discrepancy | Resolution |
|---|---|---|
| 1 | Docs say 68 registered capsules | **80** verified |
| 2 | Docs describe split repair counters, 5-call ceiling | superseded: one counter, **3-call** ceiling, advisory review |
| 3 | Handoff doc says last E2E failed and was never re-accepted | **superseded**: 15/15 pass on 2026-09-03 |
| 4 | Capsule design docs describe URI addressing, JSON-RPC, marketplace, SCARE scoring | **zero occurrences in code** |
| 5 | `task-graph-state.schema.json` presumed enforced | **loaded nowhere**; shape does not match the ledger |
| 6 | `capability_token.check_path_access()` presumed to scope workers | **no production callers** |
| 7 | Binding conditions presumed unused because `unified_selector.py` is dead | selector dead, **mechanism live** via `logical_operator_router.py` |
| 8 | `desktop_bridge` backend in config | **no dispatch branch** |
| 9 | Trust class: rank versus exact match | **unresolved**; both call sites cited (§17) |
| 10 | Evidence ABI presumed ~7 schemas | **33** |
| 11 | `artifact-conversions.v1.json` | **empty**; open question |
| 12 | README pipeline description | **historical**, superseded by the typed path |
| 13 | `package.json` version `3.0.0` | stale; `VERSION` is `1.0.0-rc.9` |
| 14 | Two unrelated memory systems | only the harness path is in scope |
| 15 | **This report's own earlier claim** that `write_scope` sits outside the freeze hash | **Retracted.** `write_scope` is absent from the 54-name mutable allowlist and is byte-compared by `verify_runtime_projection`. Only `human_review` is deliberately mutable (§7) |

## 38. Limitations of this report

- **Nothing was executed.** No installer, tests, or runtime. All runtime claims
  are static-analytic or documentary.
- **Coverage is uneven.** Twelve subsystems were examined in depth; the desktop
  application, browser operators, and several design documents were not.
- **Some Chinese-language material is encoding-damaged** in the repository and
  was recovered by re-decoding; minor transcription risk remains.
- **One trust-class discrepancy is unresolved** (§17, ledger #9).
- **Comparative positioning is pending** external research (§35).

## 38b. Counter-evidence not otherwise covered

An adversarial review of this report surfaced material that no subsystem
investigation had covered, because none was scoped to look for it. It is
recorded here rather than omitted, since its absence would flatter the subject.

| Finding | Count | Significance |
|---|---|---|
| `eval(` occurrences in `harness/` | ~30 | Not individually audited; no security review was performed |
| `exec(` occurrences | ~18 | as above |
| `shell=True` occurrences | ~14 | as above |
| Names present in **both** `harness/lib/` and `harness/tools/` (top-level) | 198 | Of these, 179 are regular files and **120 are byte-identical**. A real maintenance hazard and a trap when editing. Counts vary by method — this one is `comm -12` over the two top-level listings |
| Python dependency lockfile | **none** | Requirements files exist; no lockfile pins transitive versions |
| Lint/type suppressions | ~575 | Never sampled for justification |

**None of these were investigated in depth**, and none should be reported as
defects without that work. They are listed because a reader is entitled to know
what was *not* examined. In particular, **this report contains no security
assessment**, and the presence of dynamic execution constructs in a system that
runs model-authored plans is exactly where such an assessment would start.


## 39. Primary sources

```
AGENTS.md                                          verification culture
harness/metadata/NEW-MACHINE-START-HERE.md         pipeline and schema map
harness/metadata/pre-scheduler-stabilization-log-20260829.md   863-line issue log
harness/lib/elastic_planner.py                     planning and freeze
harness/lib/apo_plan_compiler.py                   capsule and operator binding
harness/lib/scheduler_input.py, graph_scheduler.py DAG execution
harness/lib/graph_node_dispatcher.py, operator_runtime.py, tools/operatord.py
harness/config/capability-capsules.registry.yaml   80 capsules
harness/schemas/draft/capability-capsule.v1.draft.json
harness/schemas/planning/*.schema.json             plan and freeze contracts
harness/schemas/evidence/*.schema.json             33 evidence schemas
harness/config/logical-operators.json, physical-operators.json
harness/lib/capability_activation_proof.py         activation proof
docs/CAPSULE_ARCHITECTURE.md, CAPSULE_ECOSYSTEM_DESIGN.md   design intent only
```

*End of report.*
