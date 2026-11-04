# Cross-agent reconciliation queue

Items where two independently verified findings need resolving before the
report asserts either. Do not paper over these — check both call sites.

## R1. Trust class: rank score OR exact-match gate?

- **My earlier finding [VERIFIED]** — `harness/lib/capsule_composition.py`
  defines `PLANNER_EXECUTION_TRUST_RANK = {"any": 0, "evidence_transform": 1,
  "measured_execution": 2}`, implying an ordered minimum-trust comparison.
- **Agent 3 finding [VERIFIED]** — `harness/lib/apo_plan_compiler.py`
  (`build_capsule_plan_node` / `enumerate_physical_candidate_decisions`)
  enforces `execution_trust` as an **exact-match gate, not a rank score**.

Both can be true: composition *search* may rank while plan *compilation*
requires exact match. **Resolve by reading both call sites** before the report
describes trust-class enforcement. Getting this wrong misstates a core
safety property.

## R2. Was the E2E schema fix actually applied?

Agent 3: the 2026-08-31 E2E failed with HTTP 400 `invalid_json_schema` because
`operator_requirements`' optional numeric fields were absent from the projected
schema's `required` array. Current `structured_output.project_schema` now
forces `required = all properties` for the OpenAI profile — but whether that IS
the fix for that specific failure is **unconfirmed**. Agent flagged it as an
open question.

Report must not claim the blocker is fixed without tracing commit → failure.

## R3. Requirement Compiler repair budget (RESOLVED)

Docs say split counters / 5-call ceiling (`f463b861b`); current HEAD is one
shared counter / 3-call ceiling / advisory review (`5ade9d9f3`).
**Resolution: cite code, not docs.** Logged as gotcha #23.

---

# CORRECTIONS TO MY EARLIER NOTES (verified 2026-09-10)

## C1. SCARE and the capsule design docs are ASPIRATIONAL — my note 07 over-credited them

Agent 9 read both capsule design docs in full (986 + 1139 lines) and
grep-checked them against code. Result: **both are pre-implementation Chinese
design/brainstorm artifacts, not as-built documentation.**

Zero hits in `harness/` or `core/` for: `capsule://` URIs, `capsule.invoke`
JSON-RPC, SCARE scoring, federation/marketplace.

Further divergences:
- Docs describe a **6-section** YAML contract; the real schema has **11**
  sections and is largely disjoint.
- Docs use `capsule://ns/name@version` URIs; the registry uses dot-namespaced
  IDs (`cap.foo`, `guard.foo`).
- Docs **never mention** `guard`/`resource` kinds, `operator_compatibility`,
  or the admission rejection codes — all later, independent additions.
- **SCARE is internally inconsistent**: a qualitative 5-property acronym in doc
  1, a 0–100 numeric score in doc 2. Never reconciled.
- No formal-verification formalism exists. "Verification" means string-
  expression pre/postconditions and invariants — **not proofs**. Terms like
  "symbolic verification" and "termination analysis" appear with no method.

**ACTION:** note 07 presents SCARE as core framing. Demote it. The report may
mention SCARE as *stated design intent* but must not present it as an
implemented property model, and must not imply formal verification.

## C2. `capability_token.check_path_access()` has NO production callers

[VERIFIED by grep] Only its own definition (`harness/lib/capability_token.py:50`,
`harness/tools/capability_token.py:41`) and `tests/harness/test_capability_token_runtime.py`.

Real filesystem confinement happens via `operatord.py`'s allowed-output-roots
and staged-publish mechanism instead.

**ACTION:** note 07 implies capability tokens scope worker permissions in
production. Correct this — the class exists and is tested, but the path-scoping
method is not wired into dispatch.

## C3. `unified_selector.py` is dead code — but the BINDING CHAIN IS LIVE

Agent 5 reported that binding `condition` values are parsed by
`unified_selector.py`, which has no callers, concluding the live path "never
consults logical-operators.json bindings." **That conclusion is too strong.**

[VERIFIED by grep]
- `unified_selector.py` — referenced ONLY by
  `tests/harness/test_unified_selector_binding_policy.py`. Dead in production. ✅
- BUT `harness/lib/logical_operator_router.py` **does** read the `bindings` key
  (`line 42-47`), and is imported by `harness/lib/actor_runtime.py:18`. ✅ LIVE
- `harness/lib/logical_operator_registry.py:33` also reads `bindings`.
- `harness/lib/apo_plan_compiler.py:37,145` **does** read
  `logical-operators.json` (for `logical_operators` definitions).

**Conclusion:** one *selector implementation* is dead; the binding mechanism is
live through a different module. Do not tell the audience the binding table is
unused.

## C4. ⚠ NAME COLLISION: two different things called `bindings`

This will confuse readers and presenters if not called out explicitly.

| `bindings` in... | Means |
|---|---|
| `logical-operators.json` (top level) | logical operator → ordered **candidate actor list** with `priority` + `condition` (`always`, `quota_ok`, `plugin_autosci_available`, `emergency_only`) |
| a **capsule manifest** | the capsule's `skills`, `mcp_capabilities`, `data_refs`, `secret_refs`, `required_guard_capsules`, `required_resource_capsules` |

`apo_plan_compiler.py:650,665,687` reads the **capsule** kind;
`logical_operator_router.py:42` reads the **routing** kind. Different concepts,
same word. **Define both in the glossary.**

## C5. `task-graph-state.schema.json` — CONFIRMED not loaded

Agent 4 grep-verified it is loaded nowhere on the executing path, and its field
shape doesn't even match the real runtime ledger. This upgrades gotcha #12 from
"not observed" to **confirmed**. The project's own onboarding doc says so too.

## C6. No `desktop_bridge` backend exists

Agent 5 found `_build_command` covers `claude-cli`, `command`,
`research_operator_registry`, `local/dummy/echo`, plus an unknown-backend no-op
fallback. `physical-operators.json` lists a `desktop_bridge` value but no
dispatch branch implements it. Flag as a finding.

## C7. ⚠ SCOPING TRAP: there are TWO unrelated "memory" systems

Agent 10 found that `docs/` describes two different things under the same word,
and only one is part of the pipeline this report is about.

| System | What it is | Wired into the harness pipeline? |
|---|---|---|
| **Harness research memory** | `context_store.py` / `context_projection.py` + evidence-gated capsule memory updates | **YES** — this is the report's subject |
| **Solar personal-assistant memory** | `core/ontology/` — Big-Five personality, episodic/semantic/procedural memory for the assistant itself | **NO** — populated (if at all) outside the harness pipeline |

**Consequence for the report:** many `docs/MEMORY_*.md`, `ONTOLOGY_*.md`, and
`PERSONA_ENGINE_DESIGN.md` files describe the *second* system. Citing them as
if they describe the research pipeline would be wrong. There is **no
research-paper knowledge graph called "ontology"** in this codebase.

Likewise `mempalace` and the vendored MIA memory-serve daemon are confirmed
**off-by-default / standalone**, with no capsule references.

**ACTION:** the report must scope "memory" explicitly to the harness path and
say in one line that a separate assistant-memory subsystem exists but is out of
scope. Otherwise a reader who greps `docs/` will think we missed something.

## C8. `context_projection.py` — the actual context mechanism

[VERIFIED by agent 10] Budgeted projection (default **8,000 tokens**) over an
append-only session event log: include high-value events, summarize low-value
ones, drop on budget overflow, redact secrets, with fail-open KB lookups.

This is the concrete answer to "how does it avoid dumping everything into a
prompt" — good report material, and a familiar idea for the audience.

## C9. Recurring-bug datapoint for the Challenges section

**Report title parsing** recurred across rows **32, 33, 39, 40, 41, 42** of
`pre-scheduler-stabilization-log-20260829.md` — six entries for one problem
area. Eventually addressed with a domain-term / CJK-bigram relevance gate that
**fails closed**. Separately, the "report-plan schema identity" bug (row 39)
was logged and **explicitly left unfixed**.

A bug that recurs six times is a *design-pressure* signal, not a coding slip —
strong material for the intrinsic-vs-incidental analysis.

## C10. "Finished" ≠ "accepted"

`acceptance_closeout.py` distinguishes a node that merely **dispatched/finished**
from one that is **accepted** (external evaluator verdict PASS *and* graph
status flipped). `accepted-artifact-export.py` applies a stricter gate again for
wiki export.

This is the same "receipt ≠ evidence" principle appearing a third time, at the
delivery boundary. **Recurring theme worth naming explicitly in the report:**
*at every boundary, the system refuses to treat an attempt as an outcome.*
