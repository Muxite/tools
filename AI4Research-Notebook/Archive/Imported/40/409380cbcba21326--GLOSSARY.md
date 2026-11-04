# Glossary — AI4Research / OpenSolar

Calibrated to the audience floor: **CS students who have done agentic AI work.**
Assumes DAGs, tool calling, JSON Schema, CI. Assumes nothing about this system.

Each entry: plain definition → analogy where useful → why it matters.

---

## The pipeline artifacts

**IR (Intermediate Representation)**
A typed, validated data structure the system compiles the user's request into,
rather than passing prose to the next stage. *Analogy: a compiler's AST — you
don't hand raw source to the code generator.* The whole architecture is built
on compiling NL into successive IRs.

**IntentIR** (`intent-ir.v3`)
"What did the user actually ask for?" Splits a **mechanical envelope**
(11 required fields) from a **semantic body** (goals, outcomes, constraints,
ambiguities, conflicts, unknowns). The model fills an even narrower *authoring*
schema; deterministic code rebinds `source_quotes` → `source_spans` itself, so
the model can never author citation coordinates.

**RequirementIR** (v2)
"What would satisfy the request?" An unchanged base envelope **plus** an
optional additive `semantic_contract`. The original constraint AST from
IntentIR is deep-copied in and guarded by an equality check — the model may add
interpretation beside constraints but can never edit them.

**PlanIR** (`plan-ir.v2`)
"How should it be done, and by what?" The Planner's semantic plan, before it is
compiled into executable form.

**SchedulerInput** / **frozen run contract** (`run-contract-frozen.v2`)
The immutable, hash-verified execution authority produced at the end of
planning. *Analogy: a lockfile.* Nothing downstream may renegotiate it.

**The freeze**
The moment planning ends and execution begins. Canonical-JSON SHA-256 chains
every artifact; `verify_frozen_execution_chain` **recomputes every stage** and
compares hashes rather than trusting stored verdicts. *This is the single most
important concept in the system.*

---

## Capability packaging

**Capability Capsule**
A self-contained unit of capability that declares, in one YAML manifest: its
inputs/outputs, preconditions, postconditions, invariants, **effects**
(read/write/execute/network/cost/risk), composition edges, bindings,
verification, and which operators may execute it. *Analogy: a function
signature that also declares its side effects and who's allowed to call it.*
80 registered (77 capability, 1 guard, 2 resource).

**Capsule kinds**
`capability` (does work, produces artifacts), `guard` (constrains — e.g.
secret-leak detection), `resource` (grants scoped access — e.g. repo workspace).

**Effects**
Six declared axes per capsule: `read`, `write`, `execute`, `network`, `cost`,
`risk`. Declaring **risk** as first-class, not just permissions, is unusual.

**effect_union**
The union of all selected capsules' effects for a run — computed
deterministically from static manifests, **not** LLM output. *The run's blast
radius, known before anything executes.*

**proof_obligation**
A verification duty attached to a plan node that must be discharged for the
node to count as passed.

**unsatisfiable node**
A plan node the Planner could not bind to any capsule. The schema makes a node
either fully bound (`selected: true`) **or** explicitly `unsatisfiable` — there
is no third state, so a half-bound node cannot be emitted.

**trust class / `execution_trust`**
`measured_execution` (ran and measured something), `evidence_transform`
(transformed existing evidence without new measurement),
`fixture_or_adapter_only`, `unspecified`. *Prevents a capsule that merely
reshapes evidence from satisfying a claim that requires measurement.*
⚠ Enforcement differs by call site — see the reconciliation note.

**The registry** (`capability-capsules.registry.yaml`)
The admission gate. A capsule on disk but not in the registry is **inert**;
5 such files exist deliberately. *Never activate by directory scan.*

---

## Operators (execution)

**Logical operator** (45)
An abstract role with graded capability requirements, e.g. `DeepArchitect`
needs `architecture_reasoning: 4`. *Analogy: an interface.*

**Physical operator** (102)
A concrete executor: provider, model, backend, command. *Analogy: an
implementation.* Splits into **52 provider-neutral native** workers
(`model_provider_neutral: true`, deterministic research code) and **50
provider-bound** model operators (OpenAI, Anthropic, Google, GLM, DeepSeek,
local, browser).

**⚠ `bindings` — TWO DIFFERENT MEANINGS**
| In `logical-operators.json` | In a capsule manifest |
|---|---|
| logical operator → ordered **candidate actor list**, each with `priority` and a `condition` (`always`, `quota_ok`, `plugin_autosci_available`, `emergency_only`) | the capsule's `skills`, `mcp_capabilities`, `data_refs`, `secret_refs`, `required_guard_capsules`, `required_resource_capsules` |
Unrelated concepts, same word. Both are live.

**Operator inbox**
A filesystem queue (JSON files + flock + atomic tmp-rename) used instead of
RPC, so operators can be written in any language. *Analogy: a job queue backed
by a directory.* Also how the TypeScript↔Python `codex-bridge` coordinates.

**Envelope**
The task request handed to an operator.

**Receipt vs evidence**
A submit **receipt** means "the task was accepted for execution." It is **not**
proof anything ran. Real evidence is `result.json` → `graph-callback.json` →
evaluator `eval.json` PASS. *A documented failure mode — say this out loud.*

**Lease**
A time-bounded exclusive claim on an operator or tmux pane, with stale/dead
reclaim. Prevents two schedulers driving the same worker.

**Capability token**
A scoped permission object (file/shell/network/git allow+deny paths).
⚠ Its `check_path_access()` has **no production callers** — real filesystem
confinement is `operatord`'s allowed-output-roots + staged publish.

---

## Scheduling

**Task graph / DAG**
The runtime execution graph projected from the frozen contract. ~14 node
statuses; readiness via Kahn's algorithm topological order; cycles raise.

**`task_graph_state`**
The **mutable** ledger (status, attempts, leases, dispatch ids, revision,
events) kept strictly separate from the **immutable** frozen contract.

**write_scope**
A declared set of paths a node will write. Prefix-overlap detection prevents
concurrently scheduling two nodes that would collide; a missing scope is
treated as exclusive-writer (fail-safe).

**Human gate**
A node status requiring human review. Blocks dependents by default; a graph
policy `on_human_review: warn_and_continue` can let them proceed.

**direct_response**
The Planner may answer from context alone — no scheduler, no workers. Even
simple queries still traverse Intent → Requirement → Planner first.

---

## Verification

**Three-layer test strategy**
1. **Journey tests** — primary acceptance evidence (realistic task, production
   entrypoint, retained outputs). 25 defined.
2. **Regression tests** — detect breakage, localize faults. Do *not* establish
   the product verdict.
3. **Atomic matrix** — diagnostic only. 142 L2 features, 1,502 reviewed atomic
   rows (from 2,047 historical). **Never overrides journey evidence.**

**Six-state result vocabulary**
`PASS` / `PASS_WITH_KNOWN_LIMITATIONS` / `FAIL` / `NOT_TESTED` /
`ENVIRONMENT_BLOCKED` / `NOT_AVAILABLE`. A journey proves **only** the paths it
actually exercised — results may never be copied across platforms, providers,
formats, or failure branches.

**`test_policy`** — evaluator/testing rules **frozen into** the SchedulerInput
hash at plan time, so they can't be softened at runtime.

**`SOLAR_TEST_MODE=rapid_smoke`**
A reduced-cost evaluation mode injected via **trusted environment variable
only** — never triggerable from a prompt or operator output. Documented case:
a rapid PASS receipt did **not** prevent an empty discovery being handed
downstream. *It does not prove quality.*

**Activation proof**
Testing that a capability is **actually usable**, not merely installed — 4
conceptual checks across 13 proof functions, including **negative controls**
(confirming unrelated capabilities are *not* falsely selected). States its own
limit: it cannot prove an LLM's private reasoning, only the worker-visible
prompt, runtime calls, and produced artifacts.

---

## Research (AutoSci) domain

**Evidence ABI** — 33 schemas in `harness/schemas/evidence/` defining every
research artifact.

**Claim** (`research_claims.v1`) — a extracted assertion carrying a
`citation_span` with `source_text_sha256`, hash-binding it to the exact source
text. *Makes fabricated citations structurally detectable.*

**Verdict** (`claim_verdict.v1`) — the adjudication of a claim, with
anti-upgrade / overclaim / scope-mismatch checks.

**study_protocol** — the recorded search strategy, source selection, time
range, inclusion/exclusion criteria, and **unresolved fields**. Missing
parameters must stay explicitly unresolved rather than be invented.

**Report plan vs report** — separate schemas. The plan decides which claims are
includable; the report is drafted prose. Markdown never replaces structured
evidence.

---

## Runtime / orchestration

**Incarnation** — a tmux pane running one agent persona (pm / planner /
builder / evaluator, + lab). Default start launches 4.

**Sprint** — a run unit: `status.json` + contract + events.

**Coordinator** — polls sprint status files and dispatches. (A documented
macOS/APFS bug: editing file *contents* doesn't bump directory mtime, so
directory-level change detection missed updates; fixed with per-file mtime
scanning.)

**Autopilot** — autonomously reclaims dead panes, resolves deadlocks,
diagnoses fault classes, drains queues.

**Status server** — `ThreadingHTTPServer` on `127.0.0.1:8765` (fallback
8765–8775); binds `0.0.0.0` under WSL NAT; token enforced only off-loopback.

**HIVE** — a distributed layer (mDNS on 9876, P2P, coordinator election,
bidding). **Decision-only**: `onTaskAssigned` merely `console.log`s and
`onTaskCompleted` only updates a credits ledger. **Zero** cross-references
between `core/hive/` and `harness/`. Not working distributed execution.

**Remote dispatch** — a *separate*, static SSH/rsync push mechanism using
`actor-hosts.json`. Unrelated to HIVE.

---

## Naming

**AI4Research = OpenSolar = Solar.** The GitHub repo is `Stellven/AI4Research`;
packaging/docs say OpenSolar; the CLI is `solar` and runtime state lives in
`~/.solar/`. `openJiuwen-Solar` is the **main branch name**, not a product.
"jiuwenswarm" does not appear anywhere in the tree.

**AutoSci** — the scientific-research workload (and an upstream project this
repo tracks parity against).
