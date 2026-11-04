# 07 — Capability Capsules (report centerpiece)

All counts [verified 2026-09-10 @ `b0bf165f9`] by parsing the registry and
reconciling against disk.

## The one-sentence definition

> A **Capability Capsule** is a self-contained, boundary-explicit, formally
> verifiable unit of capability — it declares *what it needs, what it produces,
> what it touches, what must be true before and after, and who may run it* —
> so that the planner can select and compose capabilities without trusting a
> model's word for any of it.

The repo's own framing:

```
Capsule = Specification + Implementation + Verification
```

with the mnemonic **SCARE**:

| Letter | Property | Meaning |
|---|---|---|
| **S** | Safety | boundaries are verifiable |
| **C** | Completeness | completion is verifiable |
| **A** | Accountability | responsibility is traceable |
| **R** | Risk | risk is quantifiable |
| **E** | Evolution | the capsule can evolve under version control |

## The problem it solves

`docs/CAPSULE_ARCHITECTURE.md` states the motivation as a critique of the
Skill / MCP / Agent model:

| Problem | Symptom | Consequence |
|---|---|---|
| Fuzzy boundaries | You don't know what resources it will touch | Security risk |
| Nondeterministic execution | You don't know whether it will finish | Poor reliability |
| Unclear responsibility | When it breaks, nobody owns it | Hard to maintain |
| Hard to compose | Capabilities can't be reused together | Duplicated work |
| Unverifiable | You can only test, never prove | Latent bugs |

A capsule is the answer to each: declared effects, declared pre/postconditions,
declared owner, declared composition edges, declared verification.

**This is the strongest single narrative in the project.** For a presentation,
this table is your "before" slide and the capsule manifest is your "after".

## By the numbers

| Metric | Value |
|---|---|
| Registered capsules | **80** |
| — `capability` kind | 77 |
| — `guard` kind | 1 (`guard.secret-leak-guard`) |
| — `resource` kind | 2 (`resource.github-readonly`, `resource.repo-workspace`) |
| Manifests resolving on disk | 80 / 80 (zero dangling) |
| Unregistered capsule files on disk | **5** (inert by design) |
| Logical operators | 45 |
| Physical operators | 102 (52 provider-neutral native, 50 provider-bound) |
| Artifact types | 76 |
| Artifact conversions | **0** (registry present but empty) |
| Registry file | 950 lines |

⚠ `harness/metadata/NEW-MACHINE-START-HERE.md` says **68** registered
manifests. That count is **stale** — it is 80 today. Use 80, and mention the
drift if you're being careful.

## Where they live

```
harness/config/capability-capsules.registry.yaml   ← the gate (950 lines)
harness/config/capability-capsules/                ← 41 registered + 5 orphans
harness/capability-capsules/                       ← 39 registered, 0 orphans
harness/schemas/draft/capability-capsule.v1.draft.json  ← the schema
```

`manifest_path` is relative to **the registry file's own directory**, so
`../capability-capsules/x.yaml` reaches the second store. Two physical
directories, one logical registry.

### The registry is a gate, not an index

**Never activate a capsule by scanning the directory.** Registration is the
admission decision. Proof that this is deliberate: five capsule files sit on
disk *unregistered* and therefore inert —

```
cap.gemini-enhanced-search.yaml
cap.chatgpt-browser-agent.yaml
cap.notebooklm-enrichment.yaml
cap.advanced-optimization-reference-worker.yaml
cap.research-report-draft.yaml
```

Three of those are external-provider integrations. Leaving them written but
unregistered is exactly the "component-gated and off by default" policy from
`CLAUDE.md`, applied at capsule granularity. **Good slide material:** the
registry is a governance boundary you can point at.

Each registry entry carries: `capability_capsule_id`, `version`, `capsule_kind`,
`status`, `schema_ref`, `manifest_path`, `tags`, `owner`, and often
`default_operator_profile`.

## Anatomy of a capsule manifest

Eleven required top-level sections, per
`schemas/draft/capability-capsule.v1.draft.json`:

```
capability_capsule_id   # stable identity
capsule_kind            # capability | guard | resource
metadata                # name, description
applicability           # task_types, positive_signals, negative_signals
contract                # inputs, outputs, preconditions, postconditions, invariants
composition             # consumes, produces, compatible_with, incompatible_with, requires_after
effects                 # read, write, execute, network, cost, risk
bindings                # skills, mcp_capabilities, data_refs, secret_refs
verification            # self_check, external_verifier, pass_conditions
operator_compatibility  # preferred, forbidden
provenance              # owner
implementation          # trust_class, entrypoint  (not in `required`, but present in practice)
```

### Worked example — `cap.research-literature-discover`

Use this one in the report; it exercises every section meaningfully.

**applicability** — how the planner knows it's relevant:
```yaml
task_types:       [scientific-research, literature-discovery]
positive_signals: ["discover papers", "arxiv recommendations", "literature shortlist"]
negative_signals: ["mutate wiki", "verify claims"]
```
Negative signals are as important as positive ones — they stop the planner
reaching for a discovery capsule when the user asked for verification.

**contract** — the enforceable part:
```yaml
inputs.required:   discovery_query
outputs.required:  literature_discovery → schemas/evidence/literature_discovery.v1.schema.json
preconditions:     query_or_seed_present; live_network_authorized
postconditions:    shortlist_traceable; traceable_sources_recorded; study_protocol_traceable
```

**invariants** — the honesty guarantees, stated as prose but load-bearing:
> - A completed result never falls back to fixtures, synthetic candidates, or
>   memory-only candidates.
> - Scientific reliability is **not self-certified at discovery**; downstream
>   ingestion and claim verification decide evidentiary support.
> - Does not ingest selected papers directly.
> - Does not mutate durable research memory directly.
> - Missing protocol parameters remain **explicitly unresolved** rather than
>   silently invented.

That last invariant is the thesis of the whole system in one line, and it's a
great presentation quote.

**effects** — the security/audit surface, six axes:
```yaml
read:    [schemas/evidence/literature_discovery.v1.schema.json]
write:   [artifacts/scientific/literature_discovery/]
execute: [plugins/autosci/operators/scientific_lifecycle/evidence/registry.py]
network: [required public scientific search APIs and paper metadata feeds]
cost:    [bounded discovery and ranking cost]
risk:    [source APIs may be stale, unavailable, or biased]
```
Declaring **risk** as a first-class field — not just permissions — is unusual
and worth calling out.

**composition** — how capsules chain:
```yaml
compatible_with:   [cap.research-paper-ingest, cap.research-memory-update]
incompatible_with: [cap.research-experiment-run]
requires_after:    []
```

**operator_compatibility** — who may execute it:
```yaml
preferred: [autosci-literature-discover-worker]
forbidden: [BackendFullWorkflowRunner]
```
An explicit **forbidden** list, not just a preference. That's a hard constraint
on binding.

**implementation**:
```yaml
trust_class: evidence_transform
entrypoint:  plugins.autosci.operators.scientific_lifecycle.evidence.registry:execute_literature_discover
```

## Trust classes

From `harness/lib/capsule_composition.py`:

```python
EXECUTION_TRUST_CLASSES = {
    "measured_execution",      # actually ran something and measured it
    "evidence_transform",      # transformed evidence without new measurement
    "fixture_or_adapter_only", # test/glue only
    "unspecified",
}
PLANNER_EXECUTION_TRUST_RANK = {"any": 0, "evidence_transform": 1, "measured_execution": 2}
```

The **rank** is the important bit: the planner can demand a minimum trust
level. A claim requiring measured evidence cannot be satisfied by a capsule
that merely transforms existing evidence. This is how "don't let the model
claim it ran an experiment" is enforced structurally.

## The three capsule kinds

| Kind | Count | Role |
|---|---|---|
| `capability` | 77 | Does work; produces artifacts |
| `guard` | 1 | Constrains — `guard.secret-leak-guard` |
| `resource` | 2 | Grants scoped access — `resource.github-readonly`, `resource.repo-workspace` |

Capsules can require guards and resources via
`bindings.required_guard_capsules` / `required_resource_capsules`. So a
capability that needs repo access must *declare* the resource capsule rather
than just reaching for the filesystem.

## Admission — the static gate

`harness/lib/capability_admission.py` is 35 lines and rejects on five reasons:

```
CAPSULE_NOT_STABLE                # status != stable
VERIFICATION_CONTRACT_MISSING     # no self_checks / pass_conditions / external_required
IMPLEMENTATION_UNDECLARED         # implementation.declared falsy
NO_SELECTABLE_PHYSICAL_OPERATOR   # operator_compatibility has no selectable preferred
TASK_TYPE_UNDECLARED              # no task_types
```

Its docstring carries a caveat worth quoting verbatim in the report:

> Declaration checks are not live execution evidence. Per-node
> I/O/effect/trust checks and dynamic operator availability remain separate
> deterministic gates.

So admission is **necessary, not sufficient**. Being admitted means the capsule
is well-formed and bindable — not that it will work.

## The capsule lifecycle (module map)

| Stage | Module | Lines | What it does |
|---|---|---|---|
| Load + registry + runtime gate | `capability_capsules.py` | 1423 | Registry, compatibility loader, runtime gate; normalizes legacy `execution_capsule_id` |
| Static admission | `capability_admission.py` | 35 | The 5 rejection reasons above |
| Composition search | `capsule_composition.py` | 703 | Deterministic registry audit + **bounded typed composition search** |
| Pre-dispatch gate | `capsule_execution_gate.py` | 194 | Idempotency fingerprint, dedup, cooldown |
| Node capability hints | `capability_inference.py` | 279 | Fills `required_capabilities` a planner forgot |
| Activation proof | `capability_activation_proof.py` | 871 | Proves capability is *activated*, not merely installed |
| Use→effect telemetry | `capability_effects.py` | 203 | Correlates dispatch intent → what the worker actually cited |
| Lease scoping | `capability_token.py` | 105 | Token expiry + file/shell/network/git allow/deny scopes |
| Plugin capability DB | `capability_registry.py` | 305 | Persists plugin capabilities into `state.db` |

### Composition search

`capsule_composition.py` does a **bounded typed search** over the capsule graph
using the artifact type registry (76 types) and the conversion registry. It
validates against `composition-candidate-search.v1.schema.json` and hashes
payloads with SHA-256 for reproducibility. Effects considered when composing:
`read, write, execute, network`.

⚠ `artifact-conversions.v1.json` currently holds **zero conversions**, even
though three `adapter.*` capsules are registered for artifact conversion
(`adapter.requirement-ir-to-design-brief`,
`adapter.patch-diff-to-verification-pack`, `adapter.artifact-type-bridge`).
The adapters exist; the conversion graph is empty. Report this as an
observation, not a defect — verify intent before calling it a gap.

### Execution gate

`capsule_execution_gate.py` computes an **idempotency fingerprint** and keeps
two state files:
```
harness/run/dispatch-dedup.json    # has this exact dispatch already happened?
harness/run/capsule-cooldown.json  # is this capsule rate-limited right now?
```
This is what stops a scheduler retry loop from re-running an expensive capsule.

### Activation proof — the strongest idea here

`capability_activation_proof.py` exists to answer *"can it actually be used?"*
rather than *"is the status green?"*. It checks four things:

1. Default dispatch text contains intent/capability context.
2. DAG graph-node dispatch receives the same context.
3. Real runtimes produce observable artifacts.
4. **Negative controls** do not falsely select unrelated capabilities.

And it states its own limit honestly:

> Boundary: no benchmark can prove an LLM's private reasoning. We prove the
> worker-visible prompt/context, runtime calls, and produced artifacts.

Point 4 and that caveat are the best "intellectual honesty" material in the
repo. Negative controls in a capability test suite are rare.

Similarly `capability_effects.py` correlates three observable artifacts —
dispatch `.intent.json` (what was made visible), handoff/eval files (what the
worker actually cited), and `sys_resource_usage` telemetry — and explicitly
"does not claim access to private model reasoning."

## Capsules → operators: the binding chain

```
Capability Capsule  (what capability is needed, with contract + effects)
        │  operator_compatibility.preferred / forbidden
        ▼
Logical Operator    (45)  role + required_capabilities with levels 1-5
        │  logical-operators.json → bindings: ordered candidates + condition
        ▼
Physical Operator   (102) concrete actor: provider, model, backend, command
```

**Logical operators** (45) declare a `primary_role` and graded
`required_capabilities`, e.g.:

```json
"DeepArchitect": {
  "primary_role": "planner",
  "required_capabilities": {"architecture_reasoning": 4, "long_context": 3,
                            "multi_agent_coordination": 3},
  "cost_hint": "high",
  "concurrency": {"max_parallel": 6, "singleton": false}
}
```

15 capability dimensions in use, most common: `scientific_evidence` (20 ops),
`research_synthesis` (14), `data_extraction` (8), `long_context` /
`code_impl` / `test_execution` / `academic_critique` (7 each). Roles skew
research: `knowledge-extractor` (9), `evaluator` (6), `builder` (4),
`planner` (3), plus ~14 `scientific-*` roles. Cost hints: 28 low, 9 medium,
7 high.

**Bindings** map each logical operator to an ordered candidate list:

```json
"DeepArchitect": {"candidates": [
  {"actor_id": "mini-claude-opus-planner",        "priority": 1, "condition": "always"},
  {"actor_id": "mini-codex-gpt55-medium-planner-1","priority": 4, "condition": "quota_ok"},
  ...]}
```

44 of 45 logical operators are bound, averaging **2.8 candidates** each.
Conditions: `always` (74), `quota_ok` (24), `plugin_autosci_available` (20),
`emergency_only` (3). **This is the failover and quota story** — a slide on its
own.

**Physical operators** (102) are the concrete fleet, and split in two:

| Group | Count | Character |
|---|---|---|
| Provider-neutral native | 52 | `model_provider_neutral: true`, backend `research_operator_registry`, `execution_trust: evidence_transform`, deterministic AutoSci code |
| Provider-bound model ops | 50 | openai (15), anthropic (11), google (7), local (5), browser (5), glm (4), deepseek (3) |

Other distributions: backend `command` (65), `research_operator_registry` (19),
`claude-cli` (14); plane `headless` (43), `interactive_browser` (7);
`enabled: true` for 63 of 102, `available: true` for 93.

That 52/50 split *is* the architecture thesis in data form: **half the fleet
doesn't depend on any model vendor at all.**

## The capsule plan artifact

`schemas/planning/capsule-plan.v1.schema.json` (`solar.capsule_plan_ir.v1`) is
what the Planner emits. Per-node it requires:

```
node_id, logical_operator, selected, stages
```

and then a conditional that's the schema's smartest feature:

- if `selected: true` → **must** have `capability_capsule_id`,
  `dispatch_task_type`, `role`, `artifact_types`, `effect_union`,
  `proof_obligations`, and `stages` with ≥1 item.
- if `selected: false` → **must** have `unsatisfiable`, and `stages` must be
  **empty**.

So the schema makes it structurally impossible to emit a node that is neither
properly bound nor explicitly declared unsatisfiable. Plan-level fields include
`effect_union` (the union of all capsule effects — your blast radius),
`proof_obligations`, `unsatisfiable_nodes`, and a `verdict` of `pass`/`fail`.

**`effect_union` and `unsatisfiable_nodes` are excellent presentation
material**: the plan tells you, before anything runs, exactly what the run may
touch and exactly what it could not figure out how to do.
