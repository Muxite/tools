# 11 — CAPSULE_ARCHITECTURE.md — full English digest

Source: `docs/CAPSULE_ARCHITECTURE.md`, 986 lines, Chinese, footer `v1.0`.
**Dated 2026-02-12** — its single commit, `aeca9f66f`; never modified since
[verified]. (The `2026-02-03` inside the file is the `created:` field of the
*fictional* example capsule at line 50, not the document's date. An earlier
draft of this digest made that mistake.)
Digested 2026-09-10 by the capability-capsule panel (pts/9).

> **Read this warning before quoting anything below.**
> This document is the *design* of capsules. It is **not** the shipped format.
> It specifies `apiVersion: capsule/v1` with sections
> `interface / permissions / guarantees / risks / verification / evolution`.
> The format actually loaded by the harness is
> `capability-capsule.v1.draft.json` with
> `contract / composition / effects / bindings / verification / operator_compatibility`.
> See `13-capsule-roadmap-and-open-questions.md` for the reconciliation table.
> Everything below is **the vision**, and much of it is unbuilt. Label it that
> way in the report and you are safe; present it as current behaviour and the
> supervisor will catch it.

Subtitle of the doc: *"Verifiable, composable, evolvable capability atoms."*

---

## 1. The motivating critique (§1.1)

The doc opens by indicting the Skill / MCP / Agent model. Translated in full —
this is the single best "before" slide in the project:

| Problem | Symptom | Consequence |
|---|---|---|
| Fuzzy boundaries | You don't know what resources it will access | Security risk |
| Nondeterministic execution | You don't know whether it will finish | Poor reliability |
| Unclear responsibility | When it breaks, you don't know who to ask | Hard to maintain |
| Hard to compose | Capabilities can't be reused with each other | Duplicated development |
| Unverifiable | You can only rely on test coverage | Latent bugs |

Note the framing: every row is an *epistemic* complaint. The objection is not
that skills don't work — it's that **you cannot know anything about them in
advance**. Capsules are a bet that declaring properties up front and checking
them mechanically beats discovering them at runtime.

## 2. Definition and SCARE (§1.2)

> **A Capsule is a self-closing, boundary-explicit, formally verifiable
> capability atom.**

```
Capsule = Specification + Implementation + Verification
```

**SCARE** — the five core properties:

| Letter | Property | Doc's phrasing |
|---|---|---|
| **S** | Safety | safety is verifiable |
| **C** | Completeness | completeness is verifiable |
| **A** | Accountability | responsibility is traceable |
| **R** | Risk | risk is quantifiable |
| **E** | Evolution | it can evolve |

Every one is "*-able*": the claim is about what you can *check*, not what the
capsule does. Worth making explicit in the presentation — it's the intellectual
core and it's easy to miss.

## 3. The six contracts (§2.1)

A capsule spec carries six named contracts. The doc's worked example is a
weather-query capsule; translated and annotated:

### 3.1 Interface Contract
`input.schema` (JSON Schema + examples), `output.schema`, and `errors[]` where
each error has `code`, `message`, and crucially **`recoverable: bool`**.
Declaring recoverability up front is what lets a scheduler decide to retry
without asking a model.

### 3.2 Permission Contract
```yaml
permissions:
  resources:
    - type: network        # network|filesystem|database|cache|system|capsule
      scope: "https://wttr.in/*"
      operations: [read]   # read|write|execute|delete
  denies:                  # explicitly declare what is NOT needed
    - type: filesystem
    - type: database
    - type: system
```
The `denies` block is the interesting half. Most permission systems only record
what you *may* do; recording what you have positively renounced makes
over-broad access detectable by diff rather than by audit.

### 3.3 Guarantee Contract
```yaml
guarantees:
  timing:
    max_duration: 5000ms
    typical_duration: 500ms
    timeout_behavior: return_cached_or_error   # error|return_cached|return_partial
  idempotency: true
  side_effects:
    - type: cache_write
      reversible: true
  resource_bounds:
    max_memory: 10MB
    max_cpu_time: 1000ms
    max_network_calls: 3
```
`idempotency` is load-bearing later: the ecosystem doc auto-caches idempotent
capsules and refuses to cache non-idempotent ones.

⚠ **Do not present this block as "the capsule guarantee format" — the source
contradicts itself.** §8.1 of the same document gives *different values for the
same weather-query capsule*: `timeout_behavior: error` (not
`return_cached_or_error`), `max_network_calls: 1` (not 3), `side_effects: []`,
a `denies` list without `system`, and `assert:` instead of `expect:`. Worse,
the value shown above — `return_cached_or_error` — **is not a member of the
enum** its own type system declares in §2.2
(`'error' | 'return_cached' | 'return_partial'`). Quote either block only with
that caveat attached.

### 3.4 Risk Contract
`cost` with concrete declared values — `typical: $0.0001`, `max: $0.001`,
`billing_model: per_call` — so a planner can price a plan before running it.

`privacy` and `availability` are **fully specified in the §2.1 YAML too**, not
merely as TypeScript types: `privacy` carries `data_collected`,
`data_retention`, `third_party_sharing`; `availability` carries
`external_dependencies` with `service` / `fallback` / `sla`. Declaring an
upstream SLA and a named fallback *inside the capability contract* is a
distinctive idea and worth a slide of its own.

### 3.5 Verification Contract
`preconditions`, `postconditions`, `invariants`, `test_cases`.

### 3.6 Evolution Contract
`compatibility.backward` / `.forward`, `deprecation`, `version_constraints`.
**This has no counterpart in the shipped schema** — a genuine roadmap item.

## 4. Specification type system (§2.2)

Declared as TypeScript interfaces: `InterfaceContract`, `PermissionContract`
(with `ResourcePermission` carrying `type / scope (glob) / operations /
conditions[]`), `GuaranteeContract`, `RiskContract`, `VerificationContract`,
`EvolutionContract`. Note `ResourcePermission.conditions` — conditional
permissions ("network allowed only if X") are designed but never appear in a
shipped manifest.

## 5. Protocol stack (§3.1)

Four layers, bottom-up:

| Layer | Name | Concern |
|---|---|---|
| 4 | Composition Protocol | how capsules combine into bigger capabilities |
| 3 | Execution Protocol | how a capsule is invoked and run |
| 2 | Verification Protocol | how a capsule is verified and certified |
| 1 | Identity Protocol | how a capsule is uniquely named and addressed |

⚠ The **ecosystem doc uses a different 5-layer stack** for the same system
(`Spec → Execution → Composition → Trust → Discovery`). The two stacks are not
the same and neither doc acknowledges the other. If you put a protocol-stack
diagram on a slide, pick one and say which.

## 6. Identity: the capsule URI (§3.2)

```
capsule://<namespace>/<name>@<version>[/<instance>]

capsule://solar.core/weather-query@1.0.0
capsule://solar.office/email-search@2.1.0/instance-abc123
```
- `namespace`: reverse-domain style (`solar.core`, `user.sihaoli`)
- `name`: lowercase + hyphens
- `version`: SemVer, pre-release tags allowed

**Not implemented.** Shipped ids are flat strings (`cap.research-paper-ingest`)
with a separate `version` field in the registry. No URI scheme exists in
`harness/lib/`.

## 7. Verification protocol — four phases (§3.3)

The most technically ambitious part of the document.

| Phase | When | Checks |
|---|---|---|
| **Static** | pre-deploy | schema validation, type checking, permission-declaration completeness, dependency resolution |
| **Symbolic** | pre-deploy | precondition *satisfiability*, postcondition *reachability*, invariant preservation, **termination analysis** |
| **Runtime** | during | input validation, permission enforcement, resource monitoring, output validation |
| **Post-execution** | after | postcondition check, side-effect audit, cost accounting |

The symbolic phase is a formal-methods claim — satisfiability and termination
analysis over capsule contracts. Nothing in the repo implements it. Shipped
verification is the static phase only (`capability_admission.py`, 35 lines)
plus runtime evidence checks. **Be careful here**: "formally verifiable" in the
subtitle refers to this unbuilt phase.

## 8. Execution protocol (§3.4)

Request = `{capsule_uri, input, context, options}` where
`ExecutionContext = {caller, session_id, trace_id, permissions[], deadline}`.
Response = `{success, output?, error?, metadata}` where
`ExecutionMetadata = {capsule_uri, duration_ms, cost, resources_used,
verification_result}`.

Every invocation is traced and priced by construction.

## 9. Composition protocol — five combinators (§3.5)

| # | Type | Semantics |
|---|---|---|
| 1 | **Sequential** | steps with `output_as` binding and per-step `condition` |
| 2 | **Parallel** | branches + `merge.strategy: all \| any \| majority` |
| 3 | **Conditional** | `condition` → `if_true` / `if_false` capsule |
| 4 | **Loop** | `over` a collection, `as` a variable, `collect_as` results |
| 5 | **Fallback** | `primary` + ordered `fallbacks[]` each with `on_error: [CODES]` or `[ANY]` |

Fallback keys off the *declared error codes* from the Interface Contract — the
contract's `recoverable` flag and error codes are what make automatic degradation
possible.

## 10. Composition spec derivation (§3.6)

> **Key insight: a composite capsule's specification can be derived from its
> children's.**

This is the intellectual payoff of the whole design. For sequential `A → B`:

```
input(A→B)       = input(A)
output(A→B)      = output(B)
permissions(A→B) = permissions(A) ∪ permissions(B)
duration(A→B)    = duration(A) + duration(B)
cost(A→B)        = cost(A) + cost(B)
precond(A→B)     = precond(A)
postcond(A→B)    = postcond(B) ∧ (postcond(A) → precond(B))
```

For parallel `A || B`:
```
input   = input(A) ∪ input(B)
output  = output(A) × output(B)      # product, not union
duration = max(duration(A), duration(B))
cost     = cost(A) + cost(B)
```

For conditional `if C then A else B`:
```
output   = output(A) ∪ output(B)
duration = max(...)
cost     = max(cost(A), cost(B))     # only one branch runs
```

The sequential postcondition line is the one to put on a slide:
`postcond(B) ∧ (postcond(A) → precond(B))` — composing two capsules generates a
**proof obligation** that A's postcondition implies B's precondition. That is
exactly the `proof_obligations` field that survives into the shipped
`capsule-plan.v1.schema.json`. **This is the clearest thread connecting the
vision to the built system** — trace it explicitly in the report.

## 11. Runtime architecture (§4.1)

Four stacked components:

```
Capsule Registry          (specs of all verified capsules)
        ↓
Verification Engine       [Static | Symbolic | Runtime Guard | Post Auditor]
        ↓
Execution Sandbox         [Resource Limiter | Network Filter | Time Guard | Cost Meter]
        ↓
Capsule Executor          (actually runs the capsule)
```

Built today: the Registry (as a YAML admission list). Partially: static
verification. **Not built**: symbolic verifier, the sandbox with its four
enforcement components, the executor as a distinct isolated layer. Solar
instead dispatches to *operators* (workers), which is a different execution
model — capsules constrain who may run, they do not themselves sandbox.

## 12. Execution flow (§4.2)

`Request → Resolve → Verify → Execute → Audit → Response`

1. **Resolve** — URI → spec from Registry
2. **Verify** — input schema, caller permission, preconditions, resource quota
3. **Execute** — create isolated sandbox, inject permitted resource access,
   start timer + cost meter, run, capture output and side effects
4. **Audit** — postconditions? invariants held? side effects match declaration?
   resource use within bounds?
5. **Response** — return output, record metadata, update statistics

Step 4's "side effects match declaration" is the accountability mechanism: the
capsule is checked against its own promises after the fact.

## 13. Integration with existing systems (§5.1) — the P0–P6 ladder

Capsules are inserted at the **top** of the existing capability priority order:

| Priority | Mechanism | Note |
|---|---|---|
| **P0** | **Capsule** | verified capsule — *highest trust* |
| P1 | Shortcut | system shortcut command |
| P2 | Script | script cache |
| P3 | Skill | imperative skill |
| P4 | MCP | external service |
| P5 | Agent | multi-step collaboration |
| P6 | Code Gen | code generation |

Conversion paths:
```
Skill  → add specification → Capsule
Script → add specification → Capsule
MCP    → wrap in specification → Capsule
```

**This is an excellent slide.** The claim is not "replace skills and MCP" but
"anything can be promoted to a capsule by adding a specification, and once
promoted it is trusted more." It reframes capsules as a *trust tier* rather
than a competing technology. It also predicts `skill_to_capsule_compiler.py`
(323 lines), which exists and implements exactly the first conversion path.

## 14. Evolution mechanism (§6.1)

SemVer with constraint syntax (`^1.0.0`, `~1.0.0`, `1.0.0`). The four
**evolution rules** are the valuable part:

1. A new version **must pass all old versions' test cases**.
2. Permissions may only **narrow**, never widen (except MAJOR).
3. Timing guarantees may only **shorten**, never lengthen (except MAJOR).
4. Output schema may only **extend**, never remove fields (except MAJOR).

These are monotonicity constraints that make upgrades safe by construction.
Nothing in the shipped registry enforces them — versions are plain strings and
there is no promotion check. `tests/foundation/capability_capsule/phase22_capability_capsule_evolution_and_version_promotion_cases.json`
suggests intent to test this; worth reading before claiming it is unenforced.

## 15. Capability growth model (§6.2)

Three tiers:
1. **Atomic capsules** — minimal, indivisible (`weather-query`, `send-email`)
2. **Composite capsules** — built from atomics (`weather-and-notify`)
3. **Meta capsules** — capsules that *generate other capsules*
   (`capsule-generator`, `capsule-migrator`)

Growth path:
```
need → match → no match? → generate atomic capsule → verify → register
          ↓                        ↓
       execute            composable? → generate composite
                                 ↓
                          meta-pattern? → generate meta capsule
```

Self-extension is designed in from the start. Compare with the shipped
`cap.research-workflow-evolve` capsule — the research pipeline has a workflow
self-evolution stage, which is the same idea landed in one domain.

## 16. Data model — IaST system tables (§7.1)

Three tables and two views:

- **`sys_capsules`** — identity, the six specs as JSON columns,
  `implementation_type` (script/skill/mcp/composite) + `implementation_ref`,
  `verification_status` (pending/verified/failed) + report + timestamp, and
  **usage statistics**: `invoke_count`, `success_count`, `avg_duration_ms`,
  `total_cost`.
- **`sys_capsule_compositions`** — `composition_type`, `composition_spec`, and
  the **`derived_spec`** produced by §3.6's algorithm.
- **`sys_capsule_executions`** — full audit row: input, output, error,
  `precondition_result`, `postcondition_result`, `invariant_result`,
  duration/cost/resources, and `side_effects`.
- **`v_available_capsules`** — verified capsules with computed `success_rate`.
- **`v_capsule_health`** — classifies capsules `degraded` (success rate < 90%,
  tested first) / `slow` (avg duration > declared `max_duration`) / `healthy`.
  Note `WHERE invoke_count > 0`: it covers only capsules that have actually run.
  And `v_available_capsules` computes `success_rate` with **no `ELSE` default**,
  so a never-invoked capsule reads as a perfect 1.0 — an optimistic default for
  precisely the unproven capsules, which cuts against the honesty argument the
  design otherwise makes.

  ⚠ **The health comparison is also broken as written.** `max_duration` is
  stored as the string `"5000ms"`, so
  `avg_duration_ms > json_extract(spec_guarantees, '$.timing.max_duration')`
  compares a number against text in SQLite and will not do what it appears to.
  If the "promise vs. reality" comparison goes on a slide, this is the sharper
  and more honest version of the point.

`v_capsule_health` is directly relevant to the "capability scoring is silent"
finding: the design always intended health to be computed from **observed
execution history against declared guarantees**. That comparison — promised
duration vs. measured duration — is the honest quality signal, and it is
currently not being produced.

## 17. The doc's own next steps (§9)

1. Implement Capsule Runtime — the core execution engine
2. Implement Verification Engine — static / symbolic / runtime
3. Migrate existing Skills — e.g. weather-fetch → capsule
4. Build Capsule Registry — local registry
5. Implement the composition engine

Status today: (4) done, (5) done (`capsule_composition.py`), (3) has a compiler,
(1) and (2) not done in the form described. **The doc has had exactly one commit,
2026-02-12, and has never been revised**, so it still lists finished work as pending — worth noting as a
documentation-hygiene item rather than a technical one.
