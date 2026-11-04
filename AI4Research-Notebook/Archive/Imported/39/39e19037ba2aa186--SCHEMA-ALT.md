# Capability Capsule: the ledger schema (alternative version)

Status: proposal, 2026-09-21. It was written without reading the previous schema, so the two can be compared.
Companion files: `REPORT.md` explains why each part exists, paper by paper. `READ-LOG.md` records what was read.
Every decision that the evidence motivates but does not prove is marked **(design)**.

---

## 1. What it is, on one screen

A Capability Capsule is **not a file that describes a capability**. It is a set of **five kinds of record about one
capability, kept apart by who is allowed to write each one**:

| Record | Answers | Written by | Changes? | Key |
|---|---|---|---|---|
| **Declaration** | What does it need, what does it change, what does it promise, what may it spend? | the builder (a person or RSI) | never; a revision is a new Declaration | `decl_hash` |
| **Verdict** | Was this exact Declaration checked, by what, with what result? | the admission gate (code, calling named verifiers) | append-only | `decl_hash` + `policy_epoch` |
| **Standing** | Which Declaration is current for this name, and may it be used? | the librarian (code, under written rules) | a pointer that moves; every move is logged | `name` |
| **Binding** | In this sprint, which exact Declaration served which plan step, and why was it allowed? | the freeze (code) | append-only | `sprint_id` + `node_id` |
| **Finding** | What did screening, audit, drift probing or use reveal afterwards? | screeners, auditors, probes, the run recorder | append-only | the set of `decl_hash`es it concerns |

Four rules make this a schema rather than a folder of records:

1. **One writer per fact.** A fact about a capability lives in exactly one record kind. Only that record's writer can
   state it, and only that writer can be wrong about it.
2. **Declared and observed facts never share a record.** Observations (Findings) can move a Standing, for example to
   `suspect`. They never edit a Declaration. A builder never writes its own Verdict. **(design)**
3. **Every claim carries its assurance level**: `enforced`, `tested`, `audited` or `declared` (§2). A claim that
   nothing checks is allowed, but it has to say so.
4. **Everything downstream refers to a `decl_hash`, never to a name.** Revising, reverting and revoking then have a
   precise meaning, and so does invalidating the work that depended on a capability.

The Declaration is the part people usually call "the manifest". Its body has seven sections:

```
identity   who it is, what kind, how agent-core loads it, where it came from
ports      typed inputs and outputs
needs      three-valued predicates that must hold before it is offered, plus services it injects
changes    effects on named resources, each with a reversibility class and an ordinal risk
guarantees checks with ids, each with a runner outside the capability's write scope
budget     ceilings on tokens, time, cost, calls and iterations
members    only for composites: the pinned member hashes and how they are wired
```

---

## 2. Definitions

Terms are defined in the order they are used below.

- **Capability.** A unit of behaviour that an agent can invoke: a tool, an MCP server, a skill folder, a prompt
  section, a subagent, an agent template, or a composite of these. Model weights are never a capability here.
- **Capability Capsule (CC).** The schema layer: the five record kinds, their rules, and the code in the capsule
  layer that applies them. CC is a scheme, not a tool. It *uses* tools (the gate, the screener, the verifiers) and is
  not one of them (supervisor, 2026-09-21).
- **Capsule.** Informally, one capability together with its records. When precision matters, this document says
  *Declaration* or *Standing* instead.
- **Builder.** Whoever writes a Declaration: a person, or RSI.
- **Sprint.** One run of the AI4Research pipeline: intake, intent, requirement compilation, planning, freeze,
  scheduling, dispatch, operators with in-run gates, delivery of claims.
- **Run context.** The typed facts available at a decision point: the artifacts that exist, state variables, the
  services currently provided, resources and their modes, secrets by reference, network zone, and remaining budget.
  Predicates are evaluated against the run context.
- **Vocabulary.** A controlled, versioned list of names for artifact types, state variables, resource keys and service
  keys. A Declaration may use only names that are in the vocabulary. **(design)**
- **Predicate.** A named, code-evaluable condition over the run context. It evaluates to `true`, `false` or
  `unknown`. `unknown` is a result in its own right, not a kind of `false`.
- **Service key.** A name for something one capability installs into the shared environment and another capability
  reads. It is Cordis's *coeffect key*: *provides* means install, *injects* means depend on.
- **Effect.** A declared change to a named resource: which resource, which operation, what scope, and how it can be
  undone.
- **Reversibility class.** How an effect can be undone:
  - `inverse`: an undo action is declared.
  - `scoped`: the effect happens in a child context that is discarded.
  - `compensate`: a later action offsets it.
  - `emission`: it crosses the system boundary (a message sent, a paid call made) and cannot be undone.
- **Check.** An executable test with an id: an output schema, a postcondition, an invariant, a property test, a
  golden case or an evaluation suite.
- **Runner.** The code that executes a check, identified by hash.
- **Assurance level.** How strongly a claim is backed:
  - `enforced`: the runtime prevents a violation, for example with a sandbox write scope or a budget cut-off.
  - `tested`: the gate executed a check before admission.
  - `audited`: a check compares the claim with what a run actually did, after the fact.
  - `declared`: nothing checks it.
- **Policy epoch.** The version of the admission rules, vocabulary and verifier set. A Verdict is valid only for the
  epoch it was issued under.
- **Offer.** The set of capabilities a model is shown when it chooses. The **executability filter** is the code that
  computes the offer.
- **Freeze.** The pipeline step that fixes, before scheduling, exactly which Declarations a sprint will use.
- **Predicate parity.** The same predicate code, run on the same inputs, at offer time and again at dispatch.
- **Composite.** A capsule whose body is a wired graph of other capsules, each pinned by `decl_hash`.
- **Gap.** A recorded need that no admitted capability met. It is the builder's input.

---

## 3. The records

In the tables below, **Reader** names the tool that consumes a field. A field with no reader is not in the schema.

### 3.1 Declaration

The Declaration is immutable and content-addressed. `decl_hash` is SHA-256 over the canonical serialisation of every
field below, together with the hashes of the body's files. The hash is taken over the canonical Declaration, not over
any harness-specific rendering of it.

#### identity

| Field | Type | Reader | Why it exists |
|---|---|---|---|
| `name` | vocabulary-safe string, stable across revisions | librarian, planner, people | the handle a Standing points from |
| `version_label` | free text | people | for humans only; identity is `decl_hash` |
| `kind` | `tool \| mcp \| skill \| prompt \| subagent \| agent \| composite` | binder | picks the carrier |
| `carrier` | `{spec: ToolCard\|McpServerSpec\|SkillSpec\|PromptSectionSpec\|PluginSpec\|AgentTemplateSpec, ref}` | binder | how agent-core loads it, unchanged (REPORT §7) |
| `body` | list of `{path, sha256}` | gate, binder | what is actually loaded; a hash mismatch at load aborts the load |
| `summary` | at most 400 characters | the choosing model, Symphony retrieval | the only prose the chooser sees |
| `lineage` | `{parent: decl_hash?, builder, build_trigger: gap_id?, context_capsules: [decl_hash], diagnosis_inputs: [ref]}` | librarian, verifier audit | revert target; `context_capsules` lists what was in the builder's context, so contamination can be traced to descendants (REPORT §5.5) |

#### ports

| Field | Type | Reader |
|---|---|---|
| `inputs[]` | `{name, artifact_type (vocab), required, schema_ref}` | executability filter, composition wiring, Symphony |
| `outputs[]` | `{name, artifact_type (vocab), schema_ref, check_id}` | composition wiring, gate |

Every output names the check that validates it. An output with no check has assurance `declared`.

#### needs

| Field | Type | Reader |
|---|---|---|
| `when[]` | `{id, predicate (vocab expression), max_age_s, on_unknown: defer\|exclude, parity_check: check_id}` | executability filter, dispatch (same code) |
| `external[]` | `{kind: package\|url\|api\|image\|dataset, value, role: operational}` | drift probe (librarian), gate |
| `injects[]` | `{service_key, interface_version_range}` | spatiotemporal manager, screener |
| `resources[]` | `{resource_key, mode: read\|write\|exclusive}` | executability filter, scheduler, screener |
| `secrets[]` | `{ref}`: names only, never values | gate (the secret must exist), screener |
| `network` | `none \| allowlist[...] \| open` | executability filter, sandbox |
| `model` | `{tool_calling?, min_context?, modalities?}` | **routing** reads this as a constraint; it is never a choice |
| `applies_to` | `{task_types[], domain_scope}` | executability filter; out-of-scope runs are refused |

`when` is evaluated in three-valued logic. For a required predicate, `unknown` gives **DEFER** with a typed request
for the missing fact, not exclusion. The default for optional predicates is `exclude`. **(design)**

A fact older than `max_age_s` counts as `unknown`. Each predicate names a `parity_check`: a check with shared
fixtures, including missing-state and stale-state cases, which shows that the predicate agrees with the body's own
hard-exit logic.

#### changes

| Field | Type | Reader |
|---|---|---|
| `effects[]` | `{id, resource_key, op: read\|write\|create\|delete\|emit, scope, reversibility, risk}` | executability filter, screener, sandbox, verifier audit |
| `effects[].scope` | a path glob, namespace or table: the write scope | sandbox (`enforced`), audit (`audited`) |
| `effects[].risk` | ordinal `{severity, blast_radius, irreversibility}`, each `low\|med\|high` | gate policy (which assurance is required) |
| `provides[]` | `{service_key, interface_version, commutative: bool}` | spatiotemporal manager, screener |
| `invariants[]` | `{id, statement, check_id?}`: what must stay true, e.g. "inputs are read-only" | screener (mutually exclusive invariants), audit |

`emission` effects must name a policy: `withhold_until_freeze_ok` or `compensate:{capsule}`. No inverse is claimed for
them.

#### guarantees

| Field | Type | Reader |
|---|---|---|
| `checks[]` | `{id, kind, runner: {ref, sha256}, author, written_before_body: bool, held_out: bool, signal_source: harness\|capsule, owner: external\|self, judge: deterministic\|model, assurance}` | gate, verifier, audit |
| `acceptance` | a list of check ids that must pass for admission | gate |
| `evals[]` | `{suite_ref, sha256, metric, threshold, held_out: bool}` | gate, verification team |

Three constraints apply to checks. The gate enforces them **(design)**:

- A check whose runner lies inside the capability's own `effects[].scope` is ineligible for `acceptance`.
- A check whose `signal_source` is `capsule` is ineligible for `acceptance`. The evidence has to be produced by the
  harness, not by the code under test.
- Checks with `owner: self` are kept as documentation. They are never admission evidence.
- At least one acceptance check must have an `author` other than the builder, and must be `held_out` from the builder.
- Checks with `judge: model` must name a verifier whose error has been measured (§3.2) before they can be used for
  admission above the lowest risk class.

#### budget

| Field | Type | Reader |
|---|---|---|
| `per_call` | `{tokens?, wall_s?, cost?, tool_calls?, iterations?}` | runtime, scheduler |
| `enforcement` | per dimension: `hard` (the runtime stops it) \| `between_calls` (checked after each model or tool call) \| `post_hoc` | verifier audit, scheduler |
| `on_exhaust` | `fail \| return_partial` | runtime, dispatch |
| `context_cost_tokens` | the size of what the chooser is shown (`summary` plus `ports`) | executability filter, librarian |

A budget is a ceiling. A capability that exhausts its budget is never considered to have passed. Token budgets cannot
stop a single model call from overshooting, because the cost of a call is known only after it returns. That is why
`enforcement` is recorded per dimension and never assumed to be `hard` (REPORT §5.10).

#### members (composites only)

| Field | Type | Reader |
|---|---|---|
| `members[]` | `{role, decl_hash}` | gate, binder |
| `wiring[]` | `{from: role.output, to: role.input}` | gate (type check), screener |
| `derived` | computed by the gate, never written by the builder | gate |

The gate computes the union of the members' `needs`, `effects` and `provides`. The composite's own declared `needs`
and `changes` must cover that union. Otherwise the composite is rejected with `UNDECLARED_MEMBER_EFFECT`.

#### coverage (optional, one field)

`coverage.undeclared_notes`: free text in which a builder states what the Declaration knowingly leaves out. The
screener gives such capsules higher priority.

### 3.2 Verdict

| Field | Type |
|---|---|
| `decl_hash`, `policy_epoch` | the subject, and the rules it was judged under |
| `outcome` | `ADMIT \| REJECT \| DEFER \| ESCALATE` |
| `reasons[]` | typed codes, for example `VOCAB_UNKNOWN_NAME`, `CHECK_FAILED:<id>`, `CHECK_UNKNOWN:<id>`, `RUNNER_IN_WRITE_SCOPE`, `UNDECLARED_MEMBER_EFFECT`, `DEPENDENCY_UNADMITTED`, `SCREEN_PENDING` |
| `checks_run[]` | `{check_id, runner_sha256, result: pass\|fail\|unknown, evidence_sha256}` |
| `verifiers[]` | `{id, version, measured_error: {false_accept, false_reject, n, measured_on, date}?}` |
| `screening[]` | ids of the Findings consulted |
| `invalidated_by` | the triggers that void this Verdict: a change to a dependency's `decl_hash`, the policy epoch, or a verifier version |
| `issued_at`, `issuer` | the gate's own version hash |

Two rules govern Verdicts:

- A Verdict whose verifier has no `measured_error` may still ADMIT, but only at a risk ceiling set by policy. **(design)**
- A budget that ran out while checking yields DEFER, never ADMIT.

### 3.3 Standing

| Field | Type |
|---|---|
| `name` | the key |
| `current` | a `decl_hash`, or null |
| `state` | `proposed \| candidate \| admitted \| suspect \| deprecated \| revoked \| retired` |
| `previous[]` | earlier `decl_hash`es, most recent first; these are the revert targets |
| `reason` | a typed code: `ADMITTED`, `SUPERSEDED`, `RETIRED_ON_EVIDENCE`, `EVICTED_BY_CAP`, `REVERTED`, `REVOKED_SECURITY`, `REVOKED_HARM`, `SUSPECT_DRIFT`, `SUSPECT_AUDIT` |
| `since`, `by` | when the pointer last moved, and which tool moved it |
| `slot` | the library partition and the cap it counts against |

`RETIRED_ON_EVIDENCE` and `EVICTED_BY_CAP` are separate codes on purpose. A raw count of deprecations can hide a
curator that has stopped retiring anything for cause (REPORT §5.4).

**Ledger integrity.** Every append-only record (Verdict, Binding, Finding, and each Standing move) carries `prev_hash`,
the hash of the previous entry in its log. Deleting or reordering entries is then detectable. **(design)**

The allowed transitions are listed in §4.7. Only `admitted` capsules can be offered in a new sprint. `suspect`
capsules keep serving sprints that are already frozen, but they are not offered in new ones.

### 3.4 Binding

| Field | Type |
|---|---|
| `sprint_id`, `node_id` | |
| `decl_hash`, `verdict_ref` | exactly what ran, and why it was allowed to |
| `offer_hash` | a hash of the offered set the model chose from |
| `choice_ref` | the model call that chose; a model choice is recorded, never trusted as a fact |
| `predicates[]` | `{id, value, context_sha256}` at offer time; dispatch re-evaluates them and appends its own values |
| `resolved[]` | `{service_key, provider_decl_hash}`: the committed view, i.e. which provider each injected key resolved to |
| `findings_consulted[]` | composition Findings that covered this co-activation, or `unscreened` |
| `step_identity` | `h(decl_hash, input artifact hashes, predecessor step identities)` |

### 3.5 Finding

| Field | Type |
|---|---|
| `kind` | `composition \| conflict_observed \| overlap \| drift \| audit_violation \| use_outcome \| gap` |
| `subjects[]` | `decl_hash`es: one for most kinds, a set for composition |
| `context` | a task signature or node type |
| `producer` | `{tool, version, model?, thresholds}` |
| `score`, `text` | for example drift δ and intent text, or a violated check id and a diff excerpt |
| `status` | `plan_only \| confirmed \| refuted \| unreviewed` |
| `action` | `none \| block_set \| move_to_suspect \| revalidate \| open_gap` |

A `gap` Finding also carries `{signature, occurrences[sprint_id], first_seen, last_seen}`.

A `conflict_observed` Finding records a joint failure seen during use. It can set `action: block_set` only after
reaching a policy threshold of independent co-occurrences. One observation is not enough (REPORT §5.8). **(design)**

---

## 4. Mechanisms

Each mechanism is code unless it is marked **[model]**.

### 4.1 Admit (the gate)

1. Parse the Declaration and check every name against the vocabulary. An unknown name gives `REJECT` with
   `VOCAB_UNKNOWN_NAME`.
2. Hash the body files and compare them with `body[]`.
3. Check the structure:
   - no acceptance check has its runner inside the write scope, or a `capsule` signal source;
   - a composite's `derived` is covered by its declared `needs` and `changes`;
   - every `injects` key is provided by some admitted capsule, or is marked optional.
4. Run the acceptance checks in a sandbox whose write scope is the declared `effects[].scope`.
   - Any write outside that scope fails the Declaration with `EFFECT_OUT_OF_SCOPE`. The sandbox turns the effect
     claim from `declared` into `enforced` for that run.
5. Screen compositions (§4.5) against the admitted capsules it is likely to co-activate with. Findings that are not
   back yet give DEFER with `SCREEN_PENDING`, or ADMIT with a narrowed offer scope, as policy decides. **(design)**
6. Check set-level value. Replay a held-out set with the active slot, with and without the candidate. A candidate
   that passes alone but lowers the slot's joint result is REJECTED with `NEGATIVE_MARGINAL_GAIN` (REPORT §5.5).
   **(design)**
7. Write the Verdict. On ADMIT, the librarian moves the Standing.

### 4.2 Offer (the executability filter)

At each choice point, code evaluates `needs.when`, `resources`, `network`, `applies_to` and `model` against the run
context. It also applies any `block_set` Findings for the capsules already bound. Then:

- `false`: the capsule is excluded, with a reason code.
- `unknown` on a `defer` predicate: the capsule is held out, and a typed request for the missing fact is raised.
- `true`: the capsule is offered. The model sees `summary` and `ports` only.

Ranking inside the offer is a tool that the scheme uses under these rules. It never re-admits a capsule that the
filter excluded.

### 4.3 Bind and freeze

- **[model]** The model binds each plan step to one capsule from its offer.
- Code then checks port types across the plan, the admission state and the resolved services, and writes Bindings.
- The freeze rejects any Binding whose `decl_hash` is no longer the Standing's `current`, or whose Standing is not
  `admitted`.

### 4.4 Dispatch (predicate parity)

Dispatch re-runs the same predicate code over the live run context and appends the values to the Binding. If a value
flips from `true` to `false`, dispatch refuses. If it flips to `unknown`, dispatch defers. There is never a second,
different precondition language at dispatch.

### 4.5 Screen compositions

The screener is a tool that is **[model]** inside. It reads:

- `effects` (shared resources written by more than one capsule);
- `invariants` (mutually exclusive statements);
- `injects` and `provides` (shared services, and whether they are commutative);
- `applies_to.domain_scope`;
- `coverage.undeclared_notes`.

It writes `composition` Findings keyed by the *set* of `decl_hash`es. Those Findings are used in three places:

- **Offer:** a `block_set` excludes a capsule when its partners are already bound.
- **Freeze:** the Binding records which Findings covered each co-activation. If none did, it records `unscreened`.
- **Re-screen:** a new `decl_hash` for any member voids the Findings about that set.

### 4.6 Revise, revert, revoke: invalidation

- **Revise:** a new Declaration gets a new hash and a new Verdict. The Standing moves only when the new Verdict is
  ADMIT, and the old hash is pushed onto `previous`.
  - *Replacement compatibility:* the gate checks that the new version still serves its dependents. Its outputs must
    cover every port that an admitted dependent consumes. Its `provides` must cover every key an admitted dependent
    injects, within the declared interface version range.
  - *No new powers:* its `effects` must not add a write, delete or emission that is not already declared, unless the
    dependents are re-screened.
  - If these checks fail, the revision is admitted under a new `name`, not as a replacement. **(design)**
- **Revert:** the Standing moves back to `previous[0]`. This needs a valid Verdict for that hash under the current
  epoch; if there is none, the old hash is re-admitted first.
- **Revoke:** the state becomes `revoked`, and every Binding that contains the hash is listed. Delivered claims whose
  step identities depend on those Bindings are marked `stale`. They are not deleted.
- **Remove** (retire from the library) is guarded, as in Cordis: the capsule stops being offered first. Its record is
  closed only when no admitted capsule injects a service it alone provides.

### 4.7 Standing transitions

```
proposed --(build)--> candidate --(Verdict ADMIT)--> admitted
candidate --(Verdict REJECT)--> retired
admitted --(Finding: drift | audit_violation | block)--> suspect --(revalidate ADMIT)--> admitted
suspect --(revalidate REJECT)--> revoked
admitted --(superseded, or cap pressure)--> deprecated --(no dependents)--> retired
any --(security or harm)--> revoked
```

Where one of these moves is judged by a model, the judge's measured error is attached to the Verdict (§3.2).

### 4.8 From gap to build

- A `gap` Finding is opened when the offer for a step is empty, or when every offered capsule failed at dispatch.
- Recurrence is counted by code over task signatures. RSI is asked to build only when the count reaches the policy
  threshold (default 2, **(design)**) and the library slot has room.
- RSI returns a Declaration with `lineage.build_trigger`, and the Declaration enters at §4.1.

### 4.9 Library caps

Each `slot` has a cap. When admitting a capsule would exceed the cap, the librarian must first `deprecate` one: the
lowest-use capsule, among those no admitted capsule depends on. Use counts come from Bindings, not from self-report.
**(design)**

The librarian works under four further rules:

- **Evidence floor.** A capsule is never retired on outcome evidence below a declared minimum number of Bindings.
  Retirement driven by a model judge is suspended while that judge's measured false-pass rate is at or above the cliff
  for the retirement threshold in use (REPORT §5.4).
- **Overlap.** The librarian computes an `overlap` Finding between Declarations whose `summary` and `ports` are close.
  It never declares one. An overlap puts the newer capsule on DEFER until a person or policy picks: disambiguate the
  summaries, supersede one capsule, or keep both in different slots (REPORT §5.2).
- **Lineage cleanup.** When a capsule is revoked for harm, every admitted capsule whose `lineage.context_capsules`
  contains its hash moves to `suspect`.
- **Candidates stay out of view.** Candidates and rejected Declarations are never offered to a model, and are never
  placed in a builder's context.

---

## 5. What was rejected, and why

| Alternative | Why it was not taken |
|---|---|
| One manifest file with a `status` field and a `quality` block inside it | It mixes author claims, gate results and observed quality in one object, so there is no telling who asserted what. Symphony's `CapabilityFingerprint` does exactly this (REPORT §6.1). |
| A fingerprint derived by a model from the capability's text | Useful for retrieval, but it is an observation of the text, not a commitment. It stays as a Finding-like view inside Symphony and feeds retrieval only. |
| Scalar "quality score" admission | A compensatory score can buy out a failed hard requirement. Hard conditions stay as separate typed checks (REPORT §5, Cognitive Admission Control). |
| The slide's eight components as eight sections (Rules, Boundary, Skills, Assets, Data, Interfaces, Eval, Governance) | Governance and Eval are not facts about the capability. They are the Verdict and Standing records. Assets and Data are `body[]` and `needs.resources`. Rules and Boundary are `needs` and `changes.scope`. Mapped in REPORT §3. |
| Prose preconditions and invariants, as in today's AI4Research manifests | Nothing can evaluate prose. Invariants may keep a statement, but acceptance uses only checks with runners. |
| Similarity-based "same capability" detection for revisions | A hash proves identity; similarity does not (REPORT §5, Execution lineage and RelAIBuild). |
| Letting a capsule be the gate, the verifier, the freeze or the scheduler | These must sit outside what they judge (REPORT §5, Darwin Gödel Machine; §9). |
| Treating AI4Research itself as a capsule | Ruled out by the supervisor, 2026-09-18. |
| Selection of models by capsules | Routing picks models. `needs.model` is a constraint that routing reads, never a choice. |
