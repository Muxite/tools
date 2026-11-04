# 09 — Report & Presentation Kit

Raw material for the deliverable. Everything here traces to a source in the
repo; citations are repo-relative paths.

## The three-sentence pitch

> AI4Research (OpenSolar) is a local-first multi-agent execution framework that
> compiles a natural-language goal into a **frozen, hash-verified execution
> contract** before anything runs. LLMs interpret semantics; deterministic code
> validates structure, freezes contracts, and schedules. Capability is packaged
> as **Capability Capsules** — units that declare their own inputs, outputs,
> preconditions, effects, risks, and who is allowed to execute them — so the
> planner composes verified capability instead of trusting a model's word.

## Numbers worth putting on a slide

| Figure | Value | Source |
|---|---|---|
| Registered capability capsules | **80** (77 capability, 1 guard, 2 resource) | `harness/config/capability-capsules.registry.yaml` |
| Logical operators | **45** | `harness/config/logical-operators.json` |
| Physical operators | **102** | `harness/config/physical-operators.json` |
| — provider-neutral native | **52** | `model_provider_neutral: true` |
| — provider-bound model ops | **50** | openai 15, anthropic 11, google 7, local 5, browser 5, glm 4, deepseek 3 |
| Capability dimensions | **15** graded 1–5 | `required_capabilities` |
| Artifact types | **76** | `harness/config/artifact-types.v1.json` |
| Logical→physical bindings | 44 bound, **2.8 candidates avg** | `logical-operators.json` `bindings` |
| Failover conditions | `always` 74, `quota_ok` 24, `plugin_autosci_available` 20, `emergency_only` 3 | same |
| Pipeline stages | **9** intake→delivery | `NEW-MACHINE-START-HERE.md` |
| Tracked files | 5,386 | `git ls-files` |
| Version | `1.0.0-rc.9` | `VERSION` |

All [verified 2026-09-10 @ `b0bf165f9`].

## Quotable lines from the source

On the design thesis (`NEW-MACHINE-START-HERE.md`):
> LLM 解释语义，确定性代码校验结构、维护引用、冻结合同和调度。
> *(LLMs interpret semantics; deterministic code validates structure, maintains
> references, freezes contracts, and schedules.)*

On capsule honesty (`cap.research-literature-discover.yaml`):
> Missing protocol parameters remain explicitly unresolved rather than being
> silently invented.

> Scientific reliability is not self-certified at discovery; downstream
> ingestion and claim verification decide evidentiary support.

On the limits of testing (`capability_activation_proof.py`):
> Boundary: no benchmark can prove an LLM's private reasoning. We prove the
> worker-visible prompt/context, runtime calls, and produced artifacts.

On admission being insufficient (`capability_admission.py`):
> Declaration checks are not live execution evidence.

On evidence discipline (`AGENTS.md`):
> Do not weaken a success condition or delete a known limitation merely to turn
> a result green.

> A journey may prove only the feature paths that it actually exercised.

## Suggested slide outline (~14 slides)

1. **Title** — AI4Research / OpenSolar, `1.0.0-rc.9`, local-first multi-agent execution framework
2. **The problem** — the Skill/MCP/Agent critique table from `CAPSULE_ARCHITECTURE.md` (fuzzy boundaries → security risk; nondeterministic → unreliable; unclear ownership → unmaintainable; uncomposable → duplicated; unverifiable → latent bugs)
3. **The thesis** — LLM interprets / deterministic code validates. One line, big type.
4. **Pipeline overview** — the 9-stage mermaid diagram from note 08, including the dashed *refuse* and *direct_response* paths
5. **Compile before you run** — Intent → Requirement → Plan, each with independent validation + fidelity + acceptance artifacts
6. **The freeze** — `SchedulerInput` + `run-contract-frozen.v2`, hash-verified, immutable. *Before freeze: negotiating with a model. After freeze: executing a contract.*
7. **Capability Capsule: definition** — Spec + Impl + Verification; SCARE
8. **Capsule anatomy** — the 11 sections, annotated
9. **Worked example** — `cap.research-literature-discover`, focusing on invariants and the six-axis `effects` block (incl. `risk` as first-class)
10. **The registry is a gate** — 80 registered, 5 deliberately unregistered and inert
11. **Binding chain** — capsule → logical operator (45) → physical operator (102), with the failover-condition breakdown
12. **The 52/50 split** — half the fleet is provider-neutral; vendor independence as architecture, not aspiration
13. **Verification culture** — three test layers, six-state result vocabulary, negative controls, "a submit receipt is not execution"
14. **Status & honest limits** — RC maturity; last full E2E failed at Planner schema admission; Discovery semantic defect open; HIVE has no executor

Trim to ~8 by merging 5+6, 8+9, and 11+12.

## Diagrams to draw

1. **Pipeline flow** — mermaid in note 08. The dashed refusal paths are the
   interesting part; don't drop them for tidiness.
2. **Capsule anatomy** — one manifest, 11 labeled sections, with each section
   annotated by *who consumes it*: `applicability`→planner selection,
   `contract`→validation, `effects`→security/audit, `composition`→search,
   `operator_compatibility`→binding, `verification`→gates.
3. **Binding chain** — three stacked layers (capsule / logical / physical) with
   fan-out arrows and condition labels (`always`, `quota_ok`,
   `plugin_autosci_available`, `emergency_only`).
4. **Research lifecycle** — the capsule DAG from note 08.
5. **Before/after freeze** — a timeline split by one vertical bar. Left side
   labeled "LLM negotiation, bounded repairs (≤5 calls)", right side
   "deterministic execution against an immutable contract". Probably the single
   most valuable diagram.

## Narrative arcs that work

**Arc A — "Trust, but structurally verify."**
Problem table → capsule as the answer → registry as gate → trust classes →
activation proof with negative controls → honest limits. Best for a technical
audience.

**Arc B — "The freeze."**
Follow one request through all 9 stages; the freeze is the climax; everything
before is negotiation, everything after is contract execution. Best for a mixed
audience — it's a story, not a taxonomy.

**Arc C — "Vendor independence."**
52 provider-neutral operators vs 50 provider-bound; logical/physical split;
`quota_ok` failover; `ANTHROPIC_BASE_URL` override. Best if the audience cares
about lock-in or cost.

Arc B is the safest default; fold A's capsule material into stages 4–5.

## Things to get right (accuracy guardrails)

- **80 capsules, not 68.** `NEW-MACHINE-START-HERE.md` says 68; it's stale.
- **Don't cite the README's pipeline.** It documents the *historical*
  PRD/Contracts/task_graph chain and says so itself.
- **Don't say version 3.0.0.** `package.json` is stale; `VERSION` is authoritative.
- **Don't present HIVE as working distributed execution.** It's a decision
  layer with no executor wired to the harness.
- **Don't claim end-to-end passes.** Last recorded full E2E failed at Planner
  schema admission; subsequent fixes were offline-validated only.
- **Don't present the atomic feature matrix as coverage.** It's the diagnostic
  layer; journeys are the acceptance evidence.
- **Distinguish designed / built / accepted.** The repo does; a report that
  flattens them is less accurate than its own source.

## Open questions worth raising in the report

These are genuine observations, not defects — flag them as questions:

1. **Empty conversion registry.** Three `adapter.*` capsules are registered for
   artifact conversion, but `artifact-conversions.v1.json` has zero entries.
   Is composition search operating without a conversion graph by design?
2. **Five unregistered capsules.** Deliberate gating, or drift? Three are
   external providers (Gemini, ChatGPT browser, NotebookLM), which suggests
   deliberate.
3. **Registered-count drift.** 68 → 80 without the onboarding doc updating.
4. **`lib/` vs `tools/` duplication.** Which is authoritative per module?
5. **Two distribution architectures** (HIVE P2P vs SSH/rsync remote dispatch)
   conflated in test matrices as one feature.
6. **`task-graph-state.schema.json`** exists but wasn't observed being loaded
   on the executing path — is it enforced?

## Source citations

Primary, in order of usefulness:

```
harness/metadata/NEW-MACHINE-START-HERE.md          current pipeline + schema table
docs/CAPSULE_ARCHITECTURE.md                        capsule concept, SCARE, problem table (37 KB)
docs/CAPSULE_ECOSYSTEM_DESIGN.md                    ecosystem design (79 KB, not yet read in depth)
harness/config/capability-capsules.registry.yaml    the registry (950 lines)
harness/schemas/draft/capability-capsule.v1.draft.json   capsule schema
harness/capability-capsules/cap.research-literature-discover.yaml   worked example
harness/schemas/planning/capsule-plan.v1.schema.json     planner output contract
harness/config/logical-operators.json               45 logical ops + bindings + workflow vocab
harness/config/physical-operators.json              102 physical ops
harness/lib/capability_admission.py                 the 5 rejection reasons (35 lines)
harness/lib/capsule_composition.py                  trust classes, bounded search
harness/lib/capability_activation_proof.py          activation vs installation
AGENTS.md                                           verification culture, result vocabulary
```

**Not yet read in depth** — worth a pass before finalizing:
`docs/CAPSULE_ECOSYSTEM_DESIGN.md` (79 KB) and the remainder of
`docs/CAPSULE_ARCHITECTURE.md` (only the first ~2 KB was read closely).
