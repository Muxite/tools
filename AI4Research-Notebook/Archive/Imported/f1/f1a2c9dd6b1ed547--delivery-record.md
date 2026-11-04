---
type: schema
id: cc.delivery.v1
status: proposed
owner: "Xiaoyang"
first_needed: "B1"
written_by:
  - "[[run]]"
read_by:
  - "[[request-to-contract]]"
stored_by:
  - "[[run]]"
traces:
  - "[[b1-one-task]]"
tags: [schema]
---

# Delivery · `cc.delivery.v1`

**What it is.** What goes back to the human: the answer, or why there is none. From B3 it also carries claims, each with how well it is supported.

**Rules that matter most here:** INV-5 (the answer points at Artifacts). The product honesty policy applies: a system fault is never presented as the human's fault.

## What: the core

Extends [`cc.common.v1`](common.md), with `scope.run_id`.

| Field | Type | Req | From | State | Description |
|---|---|---|---|---|---|
| `status` | `enum(answered, clarify, rejected, failed, needs_input)` | req | B1 | proposed | Closed on purpose, because the frontend switches on it |
| `answer` | `map<string, Ref(artifact)>` | opt | B1 | proposed | For `answered`: each `want` name to the Artifact holding it, found through the run contract's `yields` |
| `missing_inputs` | `list<object>` | opt | B2 | proposed | For `needs_input`: what is missing, each `{name, type}` |
| `message` | `text` | opt | B1 | proposed | The question for `clarify`; the reason for `rejected` and `failed`, in plain words |
| `fault` | `enum(system, input)` | opt | B1 | proposed | For `failed`, `rejected` and `clarify`: whose fault it was. The frontend must never blame the human for a system fault |
| `assumption_ids` | `list<id>` | opt | B1 | proposed | Which of the contract's `assumptions` to show with the answer, by `assumption_id` (no copy of their text, INV-5) |
| `claims` | `list<object>` | opt | B3 | proposed | Each claim in the answer, with how well it is supported |
| `claims[].claim_id` | `id` | req | B3 | proposed | Example: `claim-3` |
| `claims[].text` | `text` | req | B3 | proposed | The claim as delivered |
| `claims[].artifacts` | `list<Ref(artifact)>` | req | B3 | proposed | The Artifacts it rests on |
| `claims[].verifications` | `list<Ref(verification_result)>` | req | B3 | proposed | The Verification results that checked it |
| `claims[].status` | `enum(supported, unsupported)` | req | B3 | proposed | By the policy's claim rule, at delivery. Whether it has since gone stale is not stored (INV-2): it is a query over later Standing moves and `invalidation` Findings |
| `claims[].labels` | `list<reg(label)>` | opt | B3 | proposed | Why it is weaker than it looks. Example: `["judge_unmeasured"]` |
| `withheld` | `list<id>` | opt | B3 | proposed | Claims held back under the policy's `require_supported` |

## How: lives elsewhere

| Rule | Where |
|---|---|
| how a claim's status follows from its Verification results; how fault is attributed | policy `gates` |
| whether unsupported claims are withheld or delivered with a label | policy `delivery` |
| how our statuses map to A2A and E2A | the [Delivery](../components/run.md#delivery) page |

## Reuse

| Existing | Where | Verdict |
|---|---|---|
| `E2AResponse` | jiuwenswarm `common/e2a/models.py:164` | **reuse as is** as the carrier: the Delivery is its body. Transport fields are not repeated |
| A2A `TaskState` | agent-protocol `A2A/cpp-sdk/include/types.h:135` | **adapt** by mapping: `answered` to COMPLETED; `clarify` and `needs_input` to INPUT_REQUIRED; `rejected` to REJECTED; `failed` to FAILED |
| claim verdict vocabulary | AI4Research `schemas/evidence/claim_verdict.v1.schema.json` | **lesson**: consider `partially_supported` and per-claim limitations at B3 |

## Extension points

- Claim labels come from the shared label registry.
- `ext.<component>`. A new `status` is v2, by design.
