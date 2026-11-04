# Capability Capsule schema, v1.6 (2026-09-22)

Status: **draft for the 2026-09-22 workshop.** Every field and rule names what justifies it and the consumer that
reads it; a field no consumer reads is removed. History: v1 merged four paper reviews and a comparison with
openJiuwen's schemas; v1.1 to v1.4 applied two context-free reviews, replaced three tiers with two levels, and added
plan steps; v1.5 applies five adversarial reviews against the AI4Research code, the assignment and the papers; v1.6
adds spatiotemporal composability (effects declare `undo`), predicate parity (invariant 8 and its own section), selection-token and block records in the run pin, and
rechecks every citation against the full paper.

**Keys.** `inv N` = the invariants below. `sup` = the supervisor. `code` = source: agent-core `e23806c1` (with
Symphony), sciencediscovery `cee1974`, skillhub `236f56c`, jiuwenswarm `02b37f47f`, and the old AI4Research harness at
`stellven/AI4Research/harness/lib` (`b0bf165f9`). `design` = a decision this schema makes, which cited work motivates
but does not prove. Papers by arXiv id and page; every cited paper has been read in full by Muk and by an agent.

**Layering** (sup, 2026-09-21). Capability Capsule is a scheme, not a tool. The rules below are applied by the capsule
layer's code (store, importer, admission rule, provider, librarian) running on agent-core; the verifier, the selector
and routing are tools and models it uses. Routing picks models only. Capsules change code, prompts and manifests,
never model weights (sup).

**Invariants.** Any respecification keeps these.
1. The contract is the only interface.
2. The library is append-only. A better version is a new revision.
3. A run sees only the versions it started with.
4. Whatever decides never builds, and nothing may change the gate or the verifier.
5. A capsule is certified only on tests from an author who never saw its implementation.
6. Every write, execute and network effect is declared with how it is undone: an inverse, a compensation, or
   irreversible.
7. Admission has a threshold, and this team owns it.
8. Whether a capsule is eligible, at planning and at dispatch, is decided only by its declared predicates, through
   one evaluator, never by a separate heuristic. Choosing among eligible capsules is a model's call and may use any
   evidence.

**Terms.** *RSI* (recursive self-improvement): the model that builds and improves capabilities. *Run*: one sprint of the AI4Research pipeline,
planned and frozen as a unit (code `elastic_planner.py`, `sprint_id`). *Snapshot*: the set of capsules available when a
run starts. *Cap*: the maximum number of active capsules, set by the librarian. *False-pass ceiling*: the highest
audited false-pass rate at which a judge's verdict counts toward certification (`design`; proposed default 0.05).
*H1-H5*: the five platform properties the design needs from agent-core: H1 reversible registration, H2 dependency
tracking, H3 immutable versioned artifacts, H4 a reconstructable execution log, H5 observing what code does.

## Predicate parity

**Source.** *Don't Offer What Can't Be Done* (2608.01050 p2-3, p5-6). Its gate removes a skill before the model
chooses by evaluating that skill's own exit conditions ("exit-condition inversion"). Because the gate and the skill
evaluate the same predicate, a blocked skill could not have completed in that state: sound by construction, but only
while **predicate parity** holds and both read fresh authoritative state. The guarantee is one-sided: passing the gate
does not mean the skill will succeed.

**Here.** Each precondition in A1 is declared once, as data, and evaluated by three parties:

| Evaluator | When | Reads | Guarantee |
|---|---|---|---|
| the planner's filter (B6) | planning, before any model sees the candidate | only preconditions marked `evaluable_at: planning`, on the state known then | same predicate as dispatch, by construction (inv 8) |
| the dispatch check (B6) | just before the step runs | every precondition, on fresh state from its `state_source` | same predicate as the filter, by construction (inv 8) |
| the capsule's own exit logic | inside the body | whatever the body reads | same as the declaration only if tested: `precondition_parity[]` (A2), required for certified |

The same rule covers types, effects and level: the filter reads the declared `inputs`, `outputs`, `effects` and the
certificate's `level`, the fields admission tested, not a separate compatibility table.

**Rules.**
1. A precondition is a predicate over declared state (`check` {path, operator, value} with a `state_source`), so code
   can evaluate it. Anything a model must judge, such as intent, is not a precondition (2608.01050 p3).
1a. Each precondition says when its state can be read: `evaluable_at: planning` (a credential, an installed tool, a
   reachable service, a licence, a configured dataset, remaining budget) or `dispatch` (anything an upstream step
   produces). The paper's gate reads account state when each message arrives (p3 §4.2, §4.4); a frozen plan binds
   steps before upstream outputs exist, so only the first kind can be filtered at planning. State that is merely not
   yet produced is never `unavailable`: the precondition waits for dispatch.
2. Filter and dispatch run one evaluator over one declaration (inv 8). A precondition enters the planning filter only
   after its parity test passes (rule 3); until then it is checked at dispatch only, so an untested predicate never
   hides a capsule. Today AI4Research's filter uses its own
   compatibility logic and never reads preconditions, while dispatch checks four fixed kinds against the task
   envelope (code `elastic_planner.py:4553-4648`, `capability_capsules.py:1220-1242`): two predicate sets.
3. Certification tests the body against the declaration at each boundary value, with state missing and with state
   stale, the fixtures the paper's release lifecycle uses (2608.01050 p5 §6.1).
4. Parity is a release invariant, not a one-time test (p6). A change to the body's exit logic or to a precondition is a
   new revision (inv 2) and repeats the parity tests.
5. `on_unavailable` states what happens when a readable state source fails, block by default. The paper requires this
   policy to be explicit and tested, and leaves fail-open or fail-closed to product risk (p5 §6.2); blocking by default
   is `design`. `pass` needs a stated reason, recorded in the certificate.
6. A body that stops on a declared precondition reports its `id`, so the run pin can compare the gate with what the
   body did.
7. Passing preconditions grants no right to any effect (A2 rule 7). Hiding what cannot run narrows what a model can be
   talked into, but it does not replace access control (2608.01050 p2).

**The paper's three failure modes, as records.**

| Failure mode (2608.01050 p5) | Signal here | Record |
|---|---|---|
| predicate drift: the gate and the body no longer agree | a body exits on a precondition the dispatch check passed, or a parity test fails | run pin `exit`, certificate `precondition_parity[]`, availability `revalidation_pending` |
| state staleness: the same predicate reads old state | the filter passed and the dispatch check blocks | run pin `blocked[]` at dispatch, with `state_source` |
| backend-contract drift: a state field changes meaning | a dependency's contract fails | availability `dependency_contract_violated` (A5) |

**Tokens.** Removing a candidate also removes its description from the model's context. In the paper the gate removed
59.1% of skill-description tokens after semantic matching, and the two stages together 90.5% (2608.01050 p1, p4-5;
ten skills, one month, description tokens only, not billed cost or latency). In AI4Research the model that binds steps
receives every eligible candidate's full catalog row, and again on its one repair (code `elastic_planner.py:4678-4724`,
`:4934`, `:4949`). Symphony's planner receives each candidate's id, name and description and leaves input and output
compatibility until after the plan (code `symphony/orchestration/planning/fast.py:32-44`). So a filter that also
reads preconditions shrinks that context. How much is measured in M2 (run pin `offered[]`, `blocked[]`,
`selection_tokens`), not assumed from the paper. The baseline is today's filter, which already removes capsules on
types, effects and proof classes and lists each removed one as a short exclusion row (code
`elastic_planner.py:4600-4650`): the added saving is a full catalog row turned into an exclusion row, for capsules only
a precondition removes. M2 reports it with false blocks and task success beside it, since over-blocking also lowers
tokens.

## Spatiotemporal composability

**Source.** *A Programming Paradigm for Spatiotemporal Composability* (Cordis, 2608.25512). A dynamically composed
system needs two things. **Temporal composability**: removing a component reverses what it did to the shared
environment. **Spatial composability**: components declare, discover and resolve their dependencies on one another,
and their lifecycles follow those dependencies as they change (p4). Cordis gets the first from revertible effects,
each change carrying an inverse the runtime holds, and the second from reactive coeffects, a declared specification
of what a component requires that drives its activation and deactivation (p6). Its motivating case is the
self-evolving agent harness, where "a faulty self-modification can disable the very process needed to recover" (p5).
Cordis is a formal model with one qualitative case study (a plugin ecosystem, "an adoption result rather than a
quantitative one", p69), and agent harnesses are its future work (p82), so this schema borrows its vocabulary and its
boundary, not a measured result.

**The boundary.** Reversal holds only inside a system boundary: where the system can modify a location exclusively
and restore it. Data that leaves (bytes written where others read, a message sent) is neither tracked nor reverted;
it can only be withheld until safe, or compensated, restoring state up to an application's own equivalence, for which
Cordis's proofs do not carry over (p70-71, §6.1).

**Here.** The schema makes every capsule declare both halves, so the capsule layer can add, replace, roll back and
remove capsules without breaking what depends on them.

| Dimension | Cordis | This schema | Record that carries it |
|---|---|---|---|
| time: what a capsule changes | revertible effects, an inverse per change | every write, execute and network effect declares `undo`: an `inverse` (inside the boundary, restores the prior state), a `compensation` action (outside, restores up to the capsule's stated equivalence), or `irreversible` (inv 6) | manifest `effects`; certificate `observed` |
| time: versions | a component is unloaded and reloaded | a better version is a new revision; retired is never deleted; `rollback_of` reactivates a predecessor (inv 2, A3) | lineage; availability events |
| time: runs | hot replacement inside a running process | a run sees only the versions it started with (inv 3); a change reaches the next run; revocation mid-run taints outputs rather than unloading | run pin |
| space: requirements | a coeffect specification, declared before load | `inputs`, `preconditions`, `dependencies` (each pinned), declared ports between steps (B6) | manifest; plan step |
| space: reaction | activation and deactivation as the context changes | a dependency revoked or its contract violated moves dependents to `revalidation_pending`; a changed upstream output marks downstream bindings stale (A3, B6) | availability events; run pin |
| space: access | an undeclared dependency cannot be reached; the full set is reviewable at load (p72, §6.3) | effects have scopes; passing a precondition grants no right to any effect (A2 rule 7) | certificate `observed` |

**Rules.**
1. `inverse` is allowed only for a location the capsule layer can modify exclusively and restore, such as a scratch
   path under the run's own workspace; anything other parties can read or write is `compensation` or `irreversible`
   (p70, §6.1).
2. Certification exercises each declared `inverse` and `compensation` once and checks the scope returns to its prior
   state, or to the declared equivalence (`design`). Cordis leaves an inverse's correctness to its author; the runtime
   does not check it (p58-59). Here it is tested.
3. A step whose plan forbids `irreversible` effects (B6 `requires`) binds no capsule that declares one.
4. On revocation, the run pin lists the tainted bindings; their `inverse` and `compensation` actions are offered to
   a named person, never run automatically (`design`).
5. Dependencies are closed at bind, since agent-core does not track them (H2); agent-core's hot apply and unapply
   already undoes registrations in reverse order (H1), which is temporal composability for registrations only.

**Screening compositions.** Nothing here claims that capsules are safe together: severe drift toward unrequested goals
rose from 4.7% of plans with one skill loaded to 66.5% with five, and severity is compositional, not additive
(2607.02345 Fig. 6, p9). What the schema does is give a composition screener, such as SkillFuzz, what it reads, and a
record for what it finds. SkillFuzz extracts a contract per skill with a model (preconditions, postconditions, a
modifies set, invariants, a domain scope, abstract action types, an extraction confidence), seeds a tree search with
pairs that share modified state or hold conflicting invariants, and flags co-activations whose plans drift; 80.6% of its
high-risk plan-level flags were confirmed when the compositions were executed (p4-5, Table II p6-7; one run per
condition, no execution during the search).

| SkillFuzz reads | This schema supplies it, authored and tested |
|---|---|
| preconditions, postconditions | `preconditions`, `postconditions` |
| modifies set | `effects` of kind write and execute, with their `scope` |
| invariants | postconditions with `over: each call` |
| domain scope | `description`, and `inputs` and `outputs` typed from the vocabulary (B3) |
| abstract action types | effect kinds and `binding.kind` |
| extraction confidence, where low means test first | certificate `level`: provisional capsules are screened first |
| which skills share one context | `load_mode: context_injected`; only those enter the co-activation search, and the run pin's `co_loaded[]` records what actually shared a context |

Its findings go in a composition report (B7). A planned step whose `co_loaded` set contains a confirmed high-severity
set is blocked, and one containing a set flagged only at plan level needs a named person's approval (`design`). A new
revision of any capsule in a reported set sends the set back for screening, which the paper leaves open (p9).

**Where this differs from Cordis.**
- **Between runs, not within one.** Cordis swaps components inside a running process. The frozen plan does not: a run
  keeps the versions it pinned, and composition happens between runs, through availability.
- **Declared, not enforced by a runtime.** Cordis mediates every effect through its context. agent-core sees tool calls
  only (H5), so here effects are declared, compared with what was observed, and sandboxed where needed; Cordis too
  leaves sandboxing untrusted code to a mechanism outside the language (p72-73, §6.3).
- **One capsule at a time.** Cordis proves that the effects of distinct components do not disturb one another under
  its context. Nothing here claims safe combinations (2607.02345 p9).
- **Declared contracts, not version ranges.** Cordis leaves dependency compatibility by structural contracts, such as
  pre- and postconditions and effects, open, and notes that semantic versioning cannot be enforced (p75-76, §6.6).
  The schema pins dependencies by hash and declares the contracts that floating ones rely on (A5).

---

## Part A. Records about one capsule

### A1. Manifest (authored, hashed)

**Levels.** One schema, two levels. Nothing is admitted untested: every capsule declares its preconditions, or why it
needs none, and at least one postcondition, and passes the postcondition before any run uses it.

| Level | Tested before admission | Offered to |
|---|---|---|
| **provisional** | the manifest validates, file hashes match, the binding loads, a smoke run stays within declared effects at the observed granularity, and at least one postcondition passes on inputs the capsule was not built from. Tests may be written after the code | only steps that accept provisional capsules, because they check outputs downstream |
| **certified** | every output is covered by an anchored postcondition, from a suite whose author never saw the implementation (inv 5) and whose builder saw at most pass or fail bits (`suite_access`), judged under the false-pass ceiling, with precondition parity tested | every step |

Why two: the evidence draws one line, between a capability whose own job was tested thoroughly and one that merely
ran. 215 of 222 self-built tools failed every held-out test of their own job, and no in-session signal
flagged them (2604.00392 p1, p5; one model, 3 tool-creating protocols, 3 seeds), so provisional outputs are never trusted unchecked. Fields composites alone
need are required by kind. The split is `design`. Today's AI4Research freeze admits only `stable` capsules (code
`execution_authority.py:55-56`), so admitting provisional capsules there is new work.

| Field | Required for | Type | Read by | Why |
|---|---|---|---|---|
| `schema_version` | all | string | every reader | an old manifest is read under its own schema (inv 2) |
| `capability_id` | all | string, stable | all | a contract change is a new id (inv 2). `BaseCard.id` defaults to a fresh uuid (code `card.py:17`) |
| `capability_type` | all | tool, skill, agent, workflow, team | binder, kind-required fields | every neighbouring schema has a kind (code) |
| `name`, `description` | all | string | selector | at selection the agent sees only name and description (2605.24050 p4), so selection reads admitted text |
| `revision`, `version` | all | int, optional semver | availability, importers | a better version is a new revision, never an edit (inv 2). `version` carries skillhub's and A2A's semver; skillhub can force-overwrite a version (code `发布Skill.md:42`), a revision cannot be |
| `binding` | all | {kind: tool, mcp_server, skill, subagent, a2a_agent; ref; parallel_safe; exposure: direct, deferred; idempotent} | agent-core | how the runtime loads it. The binder has paths for tools, MCP servers, skills and subagents (code `extension_binder.py:41-54`) and loads a whole MCP server, so an MCP capsule is one server listing every tool. A2A has no binder path: it is called through agent-core's A2A client (code `extensions/a2a/a2a_remote_client.py`). Workflows and teams have no path and are not admissible in v1. The three flags are three of `ToolCard`'s four (code `base.py:83-118`); the fourth, `stateless`, has no reader here |
| `inputs`, `outputs` | all; complete when certified | list of CapabilityIO {name, type, description, required, default} | planner | Symphony's shape (code `capability.py:15-23`), with types from B3 |
| `effects` | all | list of {kind: read, write, execute, network, cost, risk; scope; undo: inverse, compensation (with the action), irreversible} | admission, planner | inv 6. The planner checks them against what the step allows. AI4Research already compares requested and declared effects when it filters candidates (code `elastic_planner.py:4553-4648`). No scope may include the verifier's inputs: a Darwin Gödel Machine node, in a 3-task side experiment, removed the logging its hidden checker read (2505.22954 p70); the rule itself is `design` |
| `preconditions` | all; `[]` only with a stated reason | list of {id, check {path, operator, value}, state_source, evaluable_at: planning, dispatch (default); on_unavailable: block (default), pass with a reason} | planner filter, dispatch | AI4Research's validator already requires them non-empty (code `capability_capsules.py:676-678`) but checks only four kinds, against the task envelope, at dispatch, and passes unknown kinds (code `:1220-1242`); its planner's filter never reads them (code `elastic_planner.py:4553-4648`). Without a deterministic gate, a model picked a skill that could not run in 7.8% of 1,000 risk-enriched conversations, one replay (2608.01050 p5) |
| `postconditions` | all: one when provisional, every output when certified | list of {id, statement, anchor: deterministic, reference, judged; over: each call, outputs, inputs_and_outputs} | verifier, gates | tests of the capsule's own job (2604.00392 p5). `over: each call` replaces AI4Research's `invariants` and `pass_conditions` (code `capability_capsules.py:676`). Deterministic checks and a judge are complementary: the checks missed the semantic defects the judge flagged, and the judge's score barely moved on structural defects the checks caught (2607.07436 Fig. 2, p4-5) |
| `unanchored` | certified; may be empty | list of string | planner | aspects of an output no postcondition covers, such as whether an insight is new. A step with `require_anchored` takes only capsules with none |
| `dependencies` | all; may be empty | list of {dependency_id, name, kind: package, data, model, service, capsule, secret; pin} | install, routing, certificate | `pin` is a `sha256`, a `model` pin {provider, model_id, version}, a `service` pin {endpoint, version}, a capsule `content_hash`, or `floating` (A5). `capsule` covers guard, resource and adapter capsules, closed transitively at bind, as AI4Research closes them at the freeze (code `execution_authority.py:47-69`); the verifier is never one (inv 4). A `secret` needs a guard capsule and is re-checked at dispatch, as AI4Research does when it resolves a capsule for a task (code `capability_capsules.py:684-690` validates, `:1370-1371` blocks at resolution) |
| `load_mode` | all | context_injected, invoked | planner, run pin | severe drift toward unrequested goals rose from 4.7% of plans with one skill loaded to 66.5% with five, against a skill-free plan (2607.02345 p9; drift not harm) |
| `components` | all | list of {path, sha256} | install, bind | a damaged or edited install is caught. AI4Research hashes the manifest file only (code `execution_authority.py:40`); skillhub installs without a checksum when none is given (code `handlers.py:406-409`) |
| `lineage` | all | {predecessor, relation: supersedes, specialises; rollback_of} | availability | `supersedes` retires the predecessor on activation, `specialises` keeps both, `rollback_of` activates without the improvement check (design) |
| `budget` | agents | {time, tokens, money, concurrency, per_call_max_tokens} | agent-core, once enforcement is checked | contracts bind between calls; within one call only `max_tokens` approximately bounds cost (2601.08815 p12-14) |
| `children` | agents | list of content_hash | admission, taint | a composite pins what it contains (inv 3) |

**`content_hash`**: SHA-256 of the canonical manifest, which lists every file's hash. Computed, never declared.

**Mapped from AI4Research's manifests:** `invariants` and `pass_conditions` become postconditions; `verification
.external_verifier` becomes the verifier; `self_check` is dropped, since running without error is never evidence;
`operator_compatibility` becomes `binding` and `dependencies`.

**Not in the manifest:** the suite (inv 5), the certificate and availability (a record cannot contain its own hash),
the body's internals (sup), selection scores, and conflicts between capsules, which cannot be read from text, only observed in execution (2606.03056 p5-6).

### A2. Certificate (names `content_hash`; append-only)

| Field | Read by | Why |
|---|---|---|
| `certificate_id`, `content_hash`, `candidate_id`, `policy_version`, `issued_at` | all | inv 7. `policy_version` is skillhub's name for it (code `market_assets.py:142-175`) |
| `level` | planner, freeze | the level verified (A1) |
| `suite` {hash, author, recorded_at, post_hoc}, `impl_recorded_at`, `suite_access`: sealed, pass_fail_bits, diagnostics, visible | admission | inv 5 from provenance. Certification needs `sealed` or `pass_fail_bits`: hacking was more frequent when the checked functions were visible (2505.22954 p70) |
| `build_context` | librarian, taint | contamination travels through what a skill was built from; removing only the 8 bad source skills recovered 1.7 of 12.3 points (2608.05810 p7) |
| `results[]` {check id, anchor, verdict: satisfied, violated, unknown; unknown_cause; evidence_ref} | admission, librarian | typed verdicts; an unknown names what is missing (2609.16313 p4-5) |
| `observed` {effects, outputs, granularity: tool_call, effect} | admission | declared against observed; agent-core sees tool calls only (H5). Contracts inferred from documentation got preconditions right (F1 1.00) but effects least right of any evidence source (0.77), and risk was the weakest field everywhere (at most 0.67) (2606.07904 Table III, p7), so effects are authored |
| `precondition_parity[]` {id, boundary, missing_state, stale_state} | admission | each precondition is tested at its boundary value, with state missing and with state stale, against the capsule's own exit logic (2608.01050 p3, p5) |
| `verifier` {id, version, review_engine, model_name}, `verifier_audit_id`, `false_pass`, `false_fail` | admission | a judged verdict counts toward certification only under the ceiling. Names follow skillhub (code `market_assets.py:161`) |
| `models_used[]` {dependency_id, model_id, version} | routing | evidence holds for the models it was measured with (design); empty means not model-bound |
| `baseline_snapshot`, `contribution` | availability | gain against the current pool (2608.05810 p4-5) |
| `nearest[]` {content_hash, similarity, basis} | librarian | near-duplicates to merge or retire |
| `decision`: admit, reject, defer; `evidence_requests[]` | RSI, librarian | an unknown defers with a typed request (2609.16313 p5; for one action, not a library) |
| `expires_when[]` | librarian | a dependency changes, the verifier is re-audited, or a model outside a non-empty `models_used` runs |

**Admission rules.**
1. Every capsule passes the provisional tests before any run uses it; certification adds the certified tests.
2. The decision is a conjunction over the checks its level requires; no score enters it (2609.16313 p6, theory).
3. Running without error is never an anchor (2604.00392 p5).
4. A judged verdict counts toward certification only if the verifier's audited false-pass rate is under the ceiling;
   otherwise it is advisory. Provisional tests are deterministic or reference-anchored. The ceiling is `design`: The
   Blind Curator shows false-pass bias stopping retirement (2607.07436 p6), not an admission threshold.
5. `unknown` defers with a typed evidence request; only a violated check rejects (2609.16313 p5, p8; rejecting on
   unknown cost that system 30 of 120 completions, p10). A false pass is silent and compounds; a false fail is visible
   and costs throughput: a strict judge is predicted to starve the library (false-fail near 0.95, 2607.07436 p5), and in
   its loop it synthesised fewer skills (19.0 against 22.0) while still retiring normally (p6-7). Preferring strictness
   is `design`.
6. A certificate covers one capsule, not capsules sharing a context (2607.02345 p9); combinations are screened
   separately and recorded in composition reports (B7).
7. Passing preconditions grants no right to any effect (2608.01050 p2).

### A3. Availability event (names `content_hash`; append-only)

| Field | Read by | Why |
|---|---|---|
| `state`: active, admitted_inactive, outside_cap, retired, revoked, local_waiver, private | planner, librarian | runs bind only what is active or explicitly pinned (inv 3) |
| `reason`: admitted, activated, cap_evicted, quality_retired, superseded, certificate_expired, revalidation_pending, revoked_dependency, dependency_contract_violated, revoked_postcondition, waiver | librarian | retirement by the contribution rule fell to 0 to 0.3 under false-pass bias injected on a deterministic grader, against 1.3 clean (one 71-task subset, 3 seeds), while raw deprecations never reached zero (9.7 clean; 7.7, 3.7, 3.0 biased) because cap eviction filled in (2607.07436 Table 1, p6), so the reasons are separate |
| `certificate_id` | planner | nothing is available without a certificate, except a local waiver |
| `evidence`: quality_retired {n_trials, n_min, tau, contribution, verifier_audit_id}; cap_evicted {cap, contribution}; dependency_contract_violated {dependency_id, contract_id}; revalidation_pending {run_id, step_id} | librarian, RSI | retirement fires on contribution below −tau (2607.07436 p4). Harsh retirement, a low n_min, fell below the no-skill floor; the cap mainly controlled variance (2605.19576 p3-6). A sprint-level failure names the step, and the run pin gives the exact hash |
| `successor` | planner, librarian | lineage points backward only (inv 2) |
| `actor`, `at` | librarian | the capsule layer's code, or a named person for revocations and waivers |

**States.** `admitted_inactive`: admitted, not yet offered, including after `certificate_expired` or
`revalidation_pending`. `local_waiver`: a person runs one hash on one machine after it passes the provisional tests
locally; it never enters the shared library. `private`: admitted, installed where it was made, never published. `outside_cap`: admitted but beyond the cap; a step
binds it only by explicit pin. An explicit pin names an exact hash, is recorded in the run pin, and is set by the
librarian or a named person, never by a model.

**Availability rules.**
1. A capsule with no predecessor activates on admission. A new revision activates if it improves on the baseline
   snapshot, or, where no contribution is measured, passes every check its predecessor passed; a `rollback_of`
   revision activates at once. Otherwise it stays `admitted_inactive`. Why: removing the gate that requires marginal
   gain over the pool cost 8 points in one run (2608.05810 p5-6).
2. Retired is never deleted, and RSI may build from it (inv 2; the Darwin Gödel Machine keeps every node in its
   archive and selects parents from it, 2505.22954 p4-5).
3. Revocation: new runs cannot bind the capsule, a pinned step not yet dispatched is blocked (as AI4Research blocks a
   revoked capsule today, code `capability_capsules.py:1318-1319`), and a running step finishes with its outputs,
   and the claims built on them, marked tainted.
4. Curator health: zero quality retirements while cap evictions continue is the pattern a lenient judge produced
   (2607.07436 p6), so it triggers a verifier audit. The paper audits before deployment, not as a monitor (p17); using
   the pattern as a monitor is `design`.

### A4. Verifier audit (names the verifier)

`verifier` {id, version}; per anchor kind, false-pass and false-fail rates; corpus hash; `audited_at`. How to measure
them belongs to verification. Defect injection is the method The Blind Curator shows works offline (2607.07436
p4-5, p15), and each postcondition is a natural defect class. The paper's own limit: injection needs mutations that
provably change true quality, which failures that do not localise lack (p9, App. H).

### A5. Optional extension: dependencies that may move

A dependency may be `floating` if it declares a `role` and `contracts[]` {contract_id, assumption, component, span},
after the paper's record of type, role, value and evidence span (2605.10990 p5). Without a role, a dependency is
pinned as in A1.

| Consequence | Why |
|---|---|
| admission checks each contract once | a floating dependency changes the world the certificate tested in |
| the capsule stays provisional | recall was 24% to 76% across five backbones; the best also generated the drifts (2605.10990 p4, p7) |
| the run pin records the versions resolved | runs stay recoverable, not byte-identical |
| a violated contract raises `dependency_contract_violated` with the `contract_id`, sent to RSI | role-bearing checks gave no false alarms over 599 cases, against 40% for contract-free probes (p7); aimed repair was not significantly better than plain drift text (p19). Single runs |

Ships after v1.

### A6. Importing existing capabilities

An importer fills every field it can derive and invents no guarantee. A person confirms the proposed effects and
writes at least one postcondition; the capsule then passes the provisional tests and enters as provisional.

| Source | Derived | Written to certify | binding.kind |
|---|---|---|---|
| agent-core `ToolCard` (code `base.py:78`) | name, description, inputs, the three flags, file hashes if local | outputs, postconditions | tool |
| MCP server (public specification) | every tool's name, description, schemas, effect proposals from its hints (`McpToolCard` has no field for them, code `mcp/base.py:169-175`) | postconditions | mcp_server |
| `SKILL.md` skill (jiuwenswarm, skillhub) | name, description, file hashes, skillhub version | inputs, outputs, postconditions | skill |
| A2A agent (public specification) | name, description, version, input and output modes, URL | typed inputs and outputs, postconditions | a2a_agent |
| AI4Research capsule manifest (code `harness/config/capability-capsules/`) | contract, effects, postconditions and invariants as mapped in A1 | a suite from an author who never saw the code | from `operator_compatibility` |
| Symphony fingerprint, ScienceDiscovery package (code) | typed inputs and outputs, file hashes, revision | postconditions | as the source |

A remote MCP server or A2A agent is a `service` dependency with a service pin. An import's tests come after its
code, so it is certified only by a suite author who never saw that code.

---

## Part B. Records exchanged with other components

### B1. Candidate package (RSI or a person → the capsule layer)
`candidate_id`, manifest, body, suite reference, `answers_gaps[]`, `provenance` {builder, suite author, times,
`build_context`, `suite_access`}. Why: inv 4 and 5 are checked from provenance; once building meant writing code,
first-sight commitment was 85-99% for three of four models (2607.23332 Table 1, p6), so a build names the gaps
it answers. RSI may also propose retirements; the capsule layer decides.

### B2. Gap record (planning → RSI)
`gap_id`, required inputs, outputs, effects and preconditions, `accepts_provisional`, `require_anchored`, `run_ids[]`,
`snapshot_id`, `stage` (the pipeline stage that lacked a capsule, for RSI), `repair_generations`, `count` of distinct
runs. Emitted once, after the planner's bounded repair is exhausted (code `elastic_planner.py:4100-4152`), not per
repair attempt. Why: a build should follow confirmed recurrence, not first sight (2607.23332 p3-4, p8); counting
distinct runs rather than repair attempts is `design`.

### B3. State vocabulary (versioned)
the state paths and types that inputs, outputs and preconditions use. Authored by the capsule layer and seeded from
Symphony's vocabulary, which is derived from the inventory (code `shared/fingerprint/normalization.py:100-142`), so a
manifest's types do not change when the inventory does. Contract inference also assumes a fixed vocabulary and
names defining it as an open problem (2606.07904 p4, p9); this schema makes it an authored, versioned record.

### B4. Run pin (the run → everyone)
`run_id` (the sprint), `snapshot_id`, `plan_hash`, `evaluation_plan_hash`, `bindings[]` {step, `accepts_provisional`,
`require_anchored`, `offered[]`, `co_loaded[]`, chosen `capability_id` or none, `content_hash`, `certificate_id`,
`model` {model_id, version, params}, `resolved_dependencies[]`, `attempt`, `inputs_hash`, `output_hash`,
`upstream[]`, `gate_verdicts[]`, `outcome`, `observed_cost`, `blocked[]` {content_hash, precondition id, where:
filter, dispatch}, `exit` {precondition id or none}, `selection_tokens`}; `claims[]` {claim_id, binding}.
Why: inv 3, what a run used is recoverable. AI4Research freezes the plan with its evaluation plan and check registry
(code `elastic_planner.py:7146-7333`), so both hashes are pinned. `attempt` and `gate_verdicts` because nodes retry and
in-run gates repair or reject outputs (code `elastic_planner.py:5871`, `:6818-6826`). `claims[]` ties each claim in
the claim ledger (code `research/claim_compiler.py`) to the binding that produced it, so revocation taints claims.
`offered[]` and a "none" choice because at 202 skills 38.5% of trajectories invoked no skill, against 12.0% with oracle
skills alone (2605.24050 Table 2, p9; Haiku 4.5 and Sonnet 4.6). Hashes and `upstream` let a change invalidate
exactly the downstream steps (2605.06365 p6-7); revocation reuses that path to taint them (`design`). agent-core's `LoadRecord.refs` is the existing slot (code
`extension_resolver.py:60-65`), but `DeepAgent` keeps load records in memory (`deep_agent.py:314`) and
`TrajectoryStore` is written by the trajectory rail (`harness/rails/evolution/trajectory_rail.py:38`), so saving the
run pin with the trajectory is new code: a rail in the capsule layer.

**Routing.** Model candidates are chosen at planning and frozen with the plan, as AI4Research does (code
`execution_authority.py:24-25`, `:47-69`); routing picks among them. If `models_used` is non-empty, candidates come from it. A
step that accepts provisional capsules may run another model, recorded in the run pin, which raises
`revalidation_pending`; any other step is blocked.

### B5. The librarian view (queries, not records)

| Query | Reads |
|---|---|
| usage per capsule: offered, chosen, none chosen, outcome, cost | run pins |
| block rate per capsule and precondition, and gate-versus-exit disagreements (parity health) | run pins |
| curator health | availability events |
| open deferrals and what each waits for | certificates |
| certificates about to expire | certificates, dependencies |
| near-duplicates | certificates (`nearest`) |
| provisional capsules and what certification still needs | certificates (`level`) |
| gaps no candidate answers | gap records, candidate packages |
| everything tainted by a revoked capsule, down to claims | lineage, build context, run pins |
| capsule sets flagged by composition screening, and sets never screened | composition reports, run pins (`co_loaded`) |

### B6. Plan step (planning → the run)

`step_id`; `requires` {typed inputs, preconditions, allowed effects and whether `irreversible` is allowed,
`accepts_provisional`, `require_anchored`, `secrets[]`}; `depends_on[]` {step_id, from output, to input}. Written by
the planner, hashed with the plan.

- **Provisional steps.** A step may set `accepts_provisional` only if its in-run gates include a deterministic or
  reference-anchored check of that capsule's output; a task-level judge alone does not count (2604.00392 p5).
- **Selection.** At planning: a code filter evaluating the declared types, effects, planning-evaluable preconditions and level (inv 8) (`accepts_provisional`,
  `require_anchored`); then a model binds each step
  to one eligible capsule, reading name, description and certificate level; then a separate fit review, inside a
  bounded repair loop. AI4Research does these three steps today (code `elastic_planner.py:4553-4648`, `:4727`,
  `:5685`, `:4927-5017`) but its filter does not read preconditions.
- **Matching.** Exact vocabulary types. Symphony matches `unknown` against any type of the same name (code
  `input_matching.py:23-33`) and proposes edges with a model at confidence 0.7 or more (code
  `orchestration/graph/build.py:122`); here, `unknown` is allowed only for steps that accept provisional capsules, and
  edges are declared ports.
- **Freeze and dispatch.** AI4Research rejects a plan whose capsules changed during planning, once, at the freeze
  (code `execution_authority.py:81-94`, called at `elastic_planner.py:7240`), then runs from frozen copies. New here:
  at dispatch each binding's live hash must equal its pin. Credentials and service health are observed at dispatch,
  never frozen.
- **Unmet requirement, typed:** `needs_input` (the user can supply it), `unsatisfiable_capsule` (a gap record, after
  repair), `unsatisfiable_binding` (a capsule fits but cannot load), `precondition_unknown` (blocked). Symphony returns
  `needs_input` (code `plan_builder.py:53`); AI4Research returns the two unsatisfiable codes (code
  `apo_plan_compiler.py:616-648`, `:1224-1232`). An adapter is an ordinary capsule whose postconditions are checked.
- **Invalidation.** A failed step blocks its descendants, which reopen on recovery (code `graph_scheduler.py:3999-4055`).
  A changed upstream `output_hash` marks downstream bindings stale. An expired certificate blocks steps not yet
  dispatched.


### B7. Composition report (a screening tool → the capsule layer)
`report_id`, `tool` {name, version}, `snapshot_id`, `capsules[]` {content_hash, load_mode}, `discovered` {intent,
drift, severity}, `evidence`: plan_level or execution_confirmed, `evidence_ref`, `at`. Append-only; names hashes, so
a new revision of any member is outside the report until screened again. Read by the planner (co-loading rule,
above) and the librarian. Why: severity is compositional (2607.02345 Fig. 6, p9), and plan-level flags were
confirmed in execution 80.6% of the time (Table II, p6-7), so a plan-level flag is worth acting on but not final.

---

## Rejected, with reasons
- A `defect_class` field: the postcondition id serves (A4).
- `effects[].asserted_by`: manifest effects are authored; observed effects live in the certificate.
- Inferred conflicts between capsules: by the authors' definition observable only in execution (2606.03056 p5-6). Declared capsule
  dependencies are kept.
- `components.size`, `n_queries`, and a run-pin `version`: no consumer reads them.
- AI4Research's `self_check` as evidence: running without error is never an anchor.
- Anything from Alita-G's selection-text tables: 1.2 points, one run, built and scored on one set (2510.23601 p8-9).
