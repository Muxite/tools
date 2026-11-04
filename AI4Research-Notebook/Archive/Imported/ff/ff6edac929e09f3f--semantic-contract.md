---
type: schema
id: cc.contract.v1
status: proposed
owner: "Muk, Ramika"
first_needed: "B1"
external_writers: "the requirement_capsule, stored by the runner as a semantic_contract Artifact"
written_by: []
read_by:
  - "[[plan-and-freeze]]"
  - "[[run]]"
  - "[[verification]]"
stored_by:
  - "[[run]]"
traces:
  - "[[b1-one-task]]"
tags: [schema]
---

# Semantic contract · `cc.contract.v1`

**What it is.** The accepted statement of what the run must do:
- what it *wants* back;
- what it is *given*;
- which capsules it *allows*;
- what it may change;
- the requirements the result must meet, each with its checks.

It is AI4Research's RequirementIR, typed so that the planner can act on it in code.

**In M1 its value is the PRD's Research Brief.** The `requirement_capsule` writes it in the Requirement Compilation stage, before freeze. The four PRD fields are the `brief`. Each target metric is also a `must` requirement of kind `metric`, `applies_to: run`, with the check `check.metrics_reported.v1`; freeze adds it to the last step's Binding (INV-9). `want` is the report; `given` is the request and the ingested documents. Requirement acceptance (the Evaluator gate on the Brief) accepts it; then freeze pins the Default DAG's remaining steps against it.

**Rules that matter most here:** INV-9 (every `must` requirement has a check), INV-4 (no generalist or gate settings here).

## What: the core

The `requirement_capsule` produces it, so it is the `value` of an [Artifact](artifact.md) of type `semantic_contract`; the Artifact carries the envelope, and this table is the value's schema. A draft becomes *the* contract when requirement acceptance passes that Artifact: in M1 the Evaluator gate on the Brief, before freeze; the run contract cites both. What it was compiled from is not repeated in the value: the capsule call's Observation names it in `inputs` (INV-5).

| Field | Type | Req | From | State | Description |
|---|---|---|---|---|---|
| `want` | `list<Port>` | req | B1 | proposed | The typed results the run must return; at least one. Example: `[{"name": "report", "type": "report"}]` |
| `given` | `list<object>` | req | B1 | proposed | The typed inputs the run starts with. May be empty |
| `given[].name` | `string` | req | B1 | proposed | Example: `text` |
| `given[].type` | `reg(port_type)` | req | B1 | proposed | Example: `text` |
| `given[].artifact_ref` | `Ref(artifact)` | req | B1 | proposed | The Artifact holding the value (the request text, an ingested document) |
| `brief` | `object` | req | B1 | proposed | The PRD's Research Brief: the four fields below |
| `brief.research_question` | `text` | req | B1 | proposed | The core research question, in one or two sentences. Example: `Can 4-bit quantisation keep a 7B model within 1% accuracy on our benchmark?` |
| `brief.domain_boundaries` | `list<string>` | req | B1 | proposed | What is in and out of scope for the research. Example: `["in: post-training quantisation", "out: retraining"]` |
| `brief.compute_constraints` | `object` | req | B1 | proposed | The hardware and compute limits the POC and Benchmarking stages must stay within: `{hardware, max_runtime_s, max_tokens}`, each optional. Example: `{"hardware": "1x A100", "max_runtime_s": 3600}` |
| `brief.target_metrics` | `list<object>` | req | B1 | proposed | The evaluation metrics and targets, each `{metric_id, name, target, direction}`, where `direction` is `higher` or `lower`. Each has a requirement of kind `metric`. Example: `{"metric_id": "m-1", "name": "accuracy_drop", "target": 0.01, "direction": "lower"}` |
| `allowed_capsules` | `list<string>` | opt | B1 | proposed | Capsule names that may be bound. Absent in M1: the Default DAG fixes the capsules. From B2, a set; when absent, the policy's `binding` default applies. Example: `["search_capsule", "screening_capsule"]` |
| `requirements` | `list<object>` | req | B1 | proposed | What the result must satisfy; the rows below |
| `requirements[].requirement_id` | `id` | req | B1 | proposed | Example: `req-1` |
| `requirements[].kind` | `reg(requirement_kind)` | req | B1 | proposed | What sort of requirement it is. A kind may define a `body`. Example: `artifact_fields` |
| `requirements[].origin` | `enum(user, policy)` | req | B1 | proposed | `policy` for a requirement added by the program (e.g. evidence honesty), so it stays distinguishable from what the user asked |
| `requirements[].statement` | `text` | req | B1 | proposed | What must hold, in one sentence. Example: `The report states the 4-bit model's accuracy drop against the 1% target.` |
| `requirements[].priority` | `enum(must, should, may)` | req | B1 | proposed | Only `must` can fail the run |
| `requirements[].source_refs` | `list<id>` | opt | B2 | proposed | The IntentIR goals, outcomes or constraints it came from. Absent in M1, which has no IntentIR |
| `requirements[].check_ids` | `list<id>` | req | B1 | proposed | The checks that test it. A `must` names at least one whose `applies_at` is `node` or `both`, so the live result is checked (INV-9); requirement acceptance refuses the contract otherwise |
| `requirements[].applies_to` | `string` | req | B1 | proposed | Which result it checks: a `want` name, or `run` for the run as a whole |
| `requirements[].body` | `json` | opt | B3 | proposed | Kind-specific detail. For `discovery`: `subject`, `inclusion_criteria`, `exclusion_criteria`, `coverage`, `time_range`, `source_refs`, and `minimum_candidates` when the user stated one |
| `scope` | `object` | req | B1 | proposed | The most the run may change |
| `scope.effect_ceiling` | `enum(pure, read_only, idempotent, compensable, irreversible)` | req | B1 | proposed | No bound capsule may have a stronger `effect_class`. Example: `compensable` |
| `scope.network` | `enum(none, egress, ingress, both)` | req | B1 | proposed | The network access the run may use |
| `scope.forbidden` | `list<string>` | opt | B1 | proposed | What the user ruled out. Example: `["exempt"]` means no generalists |
| `assumptions` | `list<object>` | opt | B1 | proposed | What compilation assumed, shown to the human with the answer. Each is `{assumption_id, source_ref, statement}` |

## How: lives elsewhere

| Was here | Now lives in |
|---|---|
| `generalists_allowed` | policy `generalists`; a user's refusal goes in `scope.forbidden` |
| "only `must` fails the run; a deterministic check blocks" | policy `gates`, `blocking` |
| default `minimum_candidates`; the cap on search queries | policy `discovery` |
| `search_queries` (how to search) | `ext.hints.search_queries` in the discovery requirement |
| the default when `allowed_capsules` is absent | policy `binding` |
| how the scope is derived from outcome classes | the [Requirement compilation](../components/request-to-contract.md#requirement-compilation) page |

## Reuse

| Existing | Where | Verdict |
|---|---|---|
| `CapabilityIO` | agent-core `symphony/models/capability.py:15` | **adapt**: `want` uses the same `Port` shape the provider publishes |
| `ArtifactRef {name, type, source}` | `symphony/orchestration/planning/models.py:9` | **adapt**: `given` matches it by name and type, so Symphony's `missing_inputs` logic works unchanged |
| `plan(candidate_ids=...)` | `symphony/orchestration/service.py:241` | **reuse as is** from B3: `allowed_capsules` is passed as `candidate_ids` |
| RequirementIR v2 | AI4Research `harness/schemas/compiler/requirement-semantics.v2.schema.json`; `harness/lib/requirement_compiler/semantic.py:215-233` | **adapt**: its requirement rows kept, with `check` becoming `check_ids`; `kind`, `origin` and assumption sources restored. Dropped: `delivery_manifest` (a file-delivery spec, back if the PRD includes code delivery), `selection_authority`, and on each requirement `checkable`, `disposition`, `semantic_role` and `acceptance.required_values`. New: `want`, `given`, `allowed_capsules`, `scope`, `applies_to`, `body` |
| A4P intent scope and mandate | agent-protocol `A4P/src/a4p/intent/` | **do not reuse** for B1 to B3 (signed per-action authorisation). Its lesson matches ours: what and how are kept in separate keys |

## Extension points

- A new requirement kind is a registry row, a `body` schema and a check. The core does not change.
- `ext.<component>`, e.g. `ext.hints`.
