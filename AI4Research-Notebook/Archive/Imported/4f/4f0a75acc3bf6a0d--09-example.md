# 12. Worked example: `research.retrieval`

A realistic AI4Research capability: gather sources for a research question and land a provenance-complete source
pack. Today it exists as `cap.research-retrieval.yaml` (§10). What follows is how it *would* look and move in the new
system. Hashes are abbreviated. The composition finding in step 2 is **illustrative**, not observed.

## 12.1 The Declaration

```yaml
identity:
  schema_version: "2.8"
  name: research.retrieval
  version_label: "2.0"
  kind: skill
  carrier: {spec: PluginSpec, ref: plugins/research-retrieval}   # skill folder + fetch MCP server
  body:
    - {path: skills/research-retrieval/SKILL.md, sha256: 9f1c…}
    - {path: skills/research-retrieval/fetch.py, sha256: 41aa…}
    - {path: mcp/fetch-server.json,              sha256: c07e…}
  load_mode: context_injected                                    # a skill shares the agent's context
  summary: "Find and fetch real sources for one research question; write sources.jsonl, evidence.jsonl and raw extracts. Does not summarise or judge relevance."
  lineage: {parent: null, builder: person:muk, build_trigger: null, context_capsules: [], diagnosis_inputs: []}
ports:
  inputs:
    - {name: question, artifact_type: artifact.research_question, required: true, schema_ref: schemas/question.v1}
    - {name: scope_hints, artifact_type: artifact.scope_hints, required: false, schema_ref: schemas/scope.v1}
  outputs:
    - {name: source_pack, artifact_type: artifact.source_pack, schema_ref: schemas/source_pack.v1, check_id: pack_schema}
needs:
  when:
    - {id: has_question, check: {path: artifacts.research_question, operator: present, value: true}, state_source: sprint artifacts,
       evaluable_at: planning, max_age_s: 0, on_unknown: defer, on_unavailable: block, parity_check: parity_has_question}
    - {id: budget_ok, check: {path: budget.remaining.cost_usd, operator: ">=", value: 2.0}, state_source: sprint budget ledger,
       evaluable_at: planning, max_age_s: 30, on_unknown: defer, on_unavailable: block, parity_check: parity_budget}
  injects: [{service_key: svc.search_provider, interface_version_range: ">=1 <2"}]
  resources: [{resource_key: ws:sprint_artifacts, mode: write}]
  network: {allowlist: [search.provider.example, "*.arxiv.org", "*.doi.org"]}
  model: {tool_calling: true, min_context: 32000}
  external:
    - {kind: package, value: httpx, pin: {version: "0.28.1", sha256: 3e1f…}}
    - {kind: service, value: search API, pin: {endpoint: "https://search.provider.example/v1/search", version: v1}}
    - {kind: secret, value: secret.search_api_key, guard: guard.secret_leak}      # re-checked at dispatch
changes:
  effect_class: compensable                                      # checked against the effects below
  effects:
    - {id: write_pack, resource_key: ws:sprint_artifacts, op: write, scope: "artifacts/{sprint}/research/**", idempotent: false, reversibility: scoped, risk: {severity: low, blast_radius: low, irreversibility: low}, assurance: enforced}
    - {id: query_out, resource_key: ext:search_provider:queries, op: emit, scope: "HTTPS GET to allowlist", idempotent: true, reversibility: emission, policy: withhold_until_freeze_ok, risk: {severity: med, blast_radius: low, irreversibility: high}, assurance: enforced}
  provides: []
  invariants:
    - {id: extracts_are_fetched, statement: "Extract files contain fetched bytes, never model-authored text", check_id: extract_bytes_match}
    - {id: evidence_resolves, statement: "Every evidence row resolves to a span in its source's extract", check_id: span_resolves}
    - {id: question_read_only, statement: "The question artifact is not modified"}
guarantees:
  checks:
    - {id: pack_schema, kind: output_schema, runner: {ref: verif/pack_schema.py, sha256: 77b2…}, author: team:verification, written_before_body: true, held_out: false, signal_source: harness, owner: external, anchor: deterministic, assurance: tested}
    - {id: span_resolves, kind: invariant, runner: {ref: verif/span_check.py, sha256: e3d9…}, author: team:verification, written_before_body: true, held_out: false, signal_source: harness, owner: external, anchor: deterministic, assurance: tested}
    - {id: extract_bytes_match, kind: invariant, runner: {ref: verif/fetch_log_compare.py, sha256: 5a10…}, author: team:verification, written_before_body: true, held_out: false, signal_source: harness, owner: external, anchor: deterministic, assurance: audited}
    - {id: golden_questions, kind: eval_suite, runner: {ref: verif/retrieval_suite.py, sha256: 0c4f…}, author: team:verification, written_before_body: true, held_out: true, signal_source: harness, owner: external, anchor: judged, assurance: tested}
    - {id: parity_has_question, kind: property_test, runner: {ref: verif/parity/has_question.py, sha256: 1b2b…}, author: team:verification, written_before_body: false, held_out: false, signal_source: harness, owner: external, anchor: deterministic, assurance: tested}
    - {id: parity_budget, kind: property_test, runner: {ref: verif/parity/budget.py, sha256: 8e8e…}, author: team:verification, written_before_body: false, held_out: false, signal_source: harness, owner: external, anchor: deterministic, assurance: tested}
  acceptance: [pack_schema, span_resolves, golden_questions, parity_has_question, parity_budget]
  evals: [{suite_ref: verif/retrieval_suite.py, sha256: 0c4f…, metric: "fraction of questions with ≥3 resolvable sources", threshold: 0.8, held_out: true}]
budget:
  per_call: {cost_usd: 2.0, wall_s: 900, tool_calls: 60}
  enforcement: {cost_usd: between_calls, wall_s: hard, tool_calls: hard}
  on_exhaust: return_partial
  context_cost_tokens: 180
coverage:
  undeclared_notes: "Relevance of sources is not checked here; that is source-validation's job."
```

Points to notice:

- **The two prose invariants from today's manifest are now bound to checks.** They are `span_resolves` and
  `extract_bytes_match`.
- **`extract_bytes_match` compares against the harness's fetch log**, so its `signal_source` is `harness` and not the
  capsule's own claim (the Darwin Gödel Machine lesson, §5).
- **The third invariant has no check, and says so.** Its assurance is `declared`.
- **The relevance judge inside `golden_questions` is a model** (`anchor: judged`). The Verdict must therefore record
  its measured error, and it counts toward certification only under the false-pass ceiling.
- **Both predicates are `evaluable_at: planning`**: the question exists before planning, and the budget is known.
  So both enter the filter, once their parity checks pass, and dispatch evaluates them again on fresh state.

## 12.2 Admission

1. **Vocabulary.** Every name used is in the vocabulary: `artifact.research_question`, `ws:sprint_artifacts`,
   `svc.search_provider`, and the rest.
2. **Hashes.** The body hashes match.
3. **Structure.**
   - Every runner lives in verification's repository, outside `artifacts/{sprint}/research/**`.
   - Every acceptance check has `signal_source: harness`.
   - `svc.search_provider` is provided by an admitted capsule, `provider.search.v1`, and the secret's guard
     `guard.secret_leak` is admitted.
4. **Sandbox run.** The sandbox allows writes only under `artifacts/{sprint}/research/**` and network only to the
   allowlist. The acceptance checks run on a held-out set of questions. One attempted write to `/tmp/cache` fails the
   first run with `EFFECT_OUT_OF_SCOPE`. The builder moves the cache into scope and re-declares, which produces a new
   hash, and the run passes.
5. **Screening against likely partners.** The partners are `research.source_validation`, `guard.secret_leak` and
   `report.draft`.
   - Code pass: no shared write keys. `report.draft` reads `artifact.source_pack`, which is an ordinary data edge.
   - The model pass flags `{research.retrieval, report.draft}`: the plan drifts toward drafting text into the extracts
     directory (illustrative). The invariant clash check matches it against `extracts_are_fetched`, and a sandbox
     confirmation run shows the drift.
   - The Finding gets `action: block_set` for co-activation *in the same node*. Being on different nodes, connected by a
     data edge, stays allowed.
6. **Set-level value.** The slot's held-out replay does not fall.
7. **Verdict.** `ADMIT` at level `certified`, with:
   - `checks_run` for the five acceptance checks;
   - `precondition_parity` for `has_question` and `budget_ok`: boundary, missing and stale state, all passed;
   - `verifiers: [{id: relevance-judge, version: 3, measured_error: {false_pass: 0.04, false_fail: 0.11, n: 200,
     corpus: "defect-injected packs", date: 2026-09-20}}]` (illustrative values). At 0.04 the judge is under the
     0.05 ceiling, so its verdict counts toward certification;
   - `screening: [F-0192]`;
   - `invalidated_by: [dep:provider.search.v1, policy_epoch, verifier:relevance-judge]`: the Verdict lapses if the
     search provider's pinned version changes, if the admission policy is revised (a new `policy_epoch`), or if the
     judge is re-audited.
8. **Standing.** The librarian sets `research.retrieval → 7c2e…`, `admitted`, reason `ADMITTED`.
9. **Symphony.** It receives an `add_skills` mutation. The capsule layer's `CapabilityProvider` now returns this
   descriptor with `content_hash = 7c2e…` and I/O taken from `ports`.

## 12.3 Offered and bound in a sprint

1. **Offer.** Sprint S-311 plans a node "gather sources" that consumes `artifact.research_question`. At the choice
   point, the filter evaluates the predicates:
   - `has_question`: true.
   - `budget_ok`: true. Remaining cost is 5.40, read 3 s ago.
   - `network`: the sprint's network zone permits the allowlist.

   The node's task type ("research") is on the Plan step only. The capsule declares no task, so it is offered because
   its input port takes `artifact.research_question` and its predicates hold.

   So `research.retrieval` is offered, alongside one other retrieval capsule. A third, whose declared network zone
   the sprint does not permit, is blocked and appears to the chooser as a one-line exclusion. The chooser sees two
   summaries and their ports: 180 + 210 tokens (illustrative).
2. **Bind.** The chooser binds `research.retrieval`.
3. **Freeze.** The freeze writes a Binding:

```yaml
sprint_id: S-311
snapshot_id: snap-0311
plan_hash: 4be0…
step_id: n4.gather_sources
bound:
  - {decl_hash: 7c2e…, role: primary, verdict_ref: V-0457, level: certified}
  - {decl_hash: 9d41…, role: dependency, verdict_ref: V-0391, level: certified}   # guard.secret_leak, closed at bind
fallbacks: [{decl_hash: 88a1…, verdict_ref: V-0460}]
offered: [7c2e…, 88a1…]
blocked: [{decl_hash: 3b07…, predicate: network_zone, where: planning}]
offer_hash: 2d9a…
selection_tokens: 390          # illustrative; measured in M2
choice_ref: call:planner/8841
predicates:
  - {id: has_question, value: true, context_sha256: aa01…}   # at the offer
  - {id: budget_ok, value: true, context_sha256: aa01…}
resolved:
  - {service_key: svc.search_provider, provider_decl_hash: 51f0…}
findings_consulted: [F-0192]    # report.draft is on step n6, not co-activated
invocations: []                 # dispatch appends one per run
prev_hash: …
```

4. **Dispatch.** Dispatch re-runs both predicates on the live context. `budget_ok` is still true (3.10 remaining after
   an earlier node), and the live hash equals the pin, so the operator runs. Dispatch appends an invocation:

```yaml
- invocation_id: S-311/n4/1
  item_key: null                # not a fan-out step
  attempt: 1
  decl_hash: 7c2e…              # the primary; a fallback run would name 88a1…
  operator: research-worker-2   # assigned by the workflow, never named in the Declaration
  model: {model_id: routing-choice, version: …}
  predicates: [{id: has_question, value: true}, {id: budget_ok, value: true}]   # on fresh state
  inputs_hash: …
  step_identity: h(7c2e…, sha(question), {k(n2), k(n3)})
```
   - The query emissions are allowed because the policy is `withhold_until_freeze_ok` and the freeze succeeded.
   - agent-core loads the verified body through `apply_extension_hot`, and the skill is added to
     `SkillUseRail.enabled_skills` for this node.
5. **What the run records.**
   - Output artifact hashes.
   - The sandbox's filesystem and network logs.
   - The fetch log.

   The audit compares them against `effects`. There are no writes outside scope and every host is on the allowlist.
   `extract_bytes_match` passes, and a `use_outcome` Finding is written.
6. **Delivery.** Claims delivered at the end of S-311 carry the step identities they depend on, and the invocation's
   `claims[]` lists them.
7. **The same capsule again.** The plan also has node n7, "gather sources for the follow-up question". It gets its own
   Binding to the same `7c2e…` and its own invocations, and its step identity differs because its input does. Had the
   planner asked for sources for each of 12 sub-questions, n4 would carry `over: {input: questions, max_parallel: 4}`:
   12 invocations with `item_key` 1 to 12, four at a time, each writing under its own `{instance}` path.

## 12.4 Revised

Two weeks later the drift probe hits the pinned endpoint `https://search.provider.example/v1/search` and gets a 301 to
`/v2/search`.

1. **Drift Finding.** The probe writes `drift` Finding F-0240, and the librarian sets `research.retrieval` to
   `suspect`, reason `SUSPECT_DRIFT`.
   - Sprints already frozen keep running on `7c2e…`.
   - New sprints are not offered it. Their offer holds the other retrieval capsule, or is empty, in which case a `gap`
     Finding opens.
2. **Repair ticket.** RSI receives it: the failed pin `external[service]`, the old and new values, and the evidence.
   It returns Declaration `b913…` with `lineage.parent: 7c2e…`, `context_capsules: [7c2e…]`, the service pinned to v2,
   and a changed `fetch.py` hash.
3. **Admission of the revision.**
   - The gate re-runs acceptance.
   - Replacement compatibility holds: same output port and type; no new write, delete or emission.
   - The Finding about `{7c2e…, report.draft}` is voided for the new hash, and a re-screen is queued. Until it returns,
     the policy admits with the block kept provisionally.
   - Verdict: ADMIT.
4. **Standing.** `current: b913…`, `previous: [7c2e…]`, reason `ADMITTED`. Symphony gets `update_skills`.

## 12.5 Revoked

The audit of sprint S-340 finds that `b913…` put the API key in the query string, i.e. in URLs that reach third-party
logs. This is an `audit_violation` against the declared use of `secret.search_api_key`.

1. **Revoke.** The librarian sets `revoked`, reason `REVOKED_SECURITY`.
2. **Find the affected work.** The invalidator lists every invocation that ran `b913…`: 14 nodes in 6 sprints
   (illustrative). Claims whose step identities descend from those nodes are marked `stale`, not deleted.
3. **Lineage.** Any admitted capsule with `b913…` in `context_capsules` becomes `suspect` (none in this case).
4. **Revert.** The Standing would revert to `previous[0] = 7c2e…`, but that version is `suspect` for drift. The revert is
   refused, and the offer for "gather sources" falls back to the other retrieval capsule.
5. **Gap.** Where that capsule is not applicable, a `gap` Finding opens. By the recurrence rule (§6) it reaches RSI only if it recurs.

![Figure 14. research.retrieval over time: admitted, bound, drifted, revised, revoked.](figures/F7.png)

## 12.6 The merge example: the chain that runs every sprint

The abstract A-B of §8 has a concrete instance, and it is the first candidate the algorithm would ever
propose, because it has the highest support in the system.

**The chain.** `intent -> IntentIR -> faithfulness`. Each part is the *work of a stage* (§2c): a
capability with an input, an output, declarable effects and a checkable postcondition. Each is admitted
and tested on its own, so each stays reusable elsewhere after the merge.

**The gate is outside the block.** `faithfulness` **assesses**: it emits a Finding about the IntentIR.
The gate **decides**. By §4.10's rule a capsule may assess but never decide, so the merge candidate is
the first three and the gate evaluates the resulting block exactly as it evaluates any node. Drawn this
way, the gate sitting visibly outside the merged block is the clearest single picture of the rule.

**Why it qualifies.** The chain runs in almost every sprint by construction, so it does not have to wait
for statistical recurrence: it is seeded from known workflow structure (§8). Its edges carry both high
support and a high success rate, which is what `qualified_edges` requires.

**What the merged capsule looks like.**

- `identity.lineage`: `relation: merge`, `parent` and `co_parents` naming the three members.
- `members[]`: three entries, each pinned by `decl_hash`, with the internal `structure` wiring
  IntentIR's output into faithfulness's input by declared port type.
- `ports`: the boundary of that internal DAG -- the raw intent in, the IntentIR and its assessment out.
- `changes`: the union of the members'. `needs`: the union minus what the members satisfy internally.
- `guarantees.checks[]`: the union of the three members' suites, plus at least one check of the block's
  own contract. **It does not inherit a quality record**: the block earns its own rate (§4.5c).

**What it costs.** The three nodes become one, so they take one lease and the union of their write
scopes; a failure anywhere inside retries the whole block; and a gap inside is attributed to the block
rather than to the member. Those are the trades in §11.1, and they are the reason a merge is approved by
a person rather than applied automatically.

**When `intent -> IntentIR` is revised.** The block keeps its pinned hash and keeps running. It is marked
stale against the new version, not invalid. A merged capsule over the new version is a *candidate*, built
only when something asks for the chain again and the new version passes replacement compatibility. If the
old version were revoked rather than superseded, the block would move to `suspect` with
`MEMBER_UNAVAILABLE`.

