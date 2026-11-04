# Ask: Model routing ↔ Capability Capsule

From Muk (Capability Capsule) to Xiaoyang (Model routing), for the 2026-09-22 workshop. Rewritten 2026-09-22
against `SCHEMA.md` v1.6, which wins where they differ. One page, written to be argued with.

## The split

- **Routing chooses models only** (supervisor, 2026-09-21). It does not rank capsules. Binding a capsule to a plan
  step is a planning model's job, after the capsule layer's filter.
- **Model candidates are chosen at planning and frozen with the plan**, as AI4Research does today
  (*code* `execution_authority.py:24-25`, `:47-69`, which freezes each node's operator fields, `model` among them). Routing picks among them at run time.

## What I give you, what I need

| I give you | I need from you |
|---|---|
| each capsule's `model` dependencies, pinned by provider, model id and version | a model among the frozen candidates for each step |
| the certificate's `models_used[]`: the models its evidence covers | if `models_used` is non-empty, candidates drawn from it |
| a rule for the exception: a step that accepts provisional capsules may run another model, which raises `revalidation_pending`; any other step is blocked | the model that actually ran, with its version and parameters, written into the run pin (`bindings[].model`) |

## Why

| Rule | Evidence |
|---|---|
| evidence holds for the model it was measured with | `design`. In More Skills, Worse Agents? the two models failed differently at 202 skills: Haiku 4.5 mostly stopped invoking skills (65.9% of trajectories), Sonnet 4.6 mostly lost to wrong picks (2605.24050 Table 10, p17) |
| the run pin records the model | a claim must trace to the exact capsule and model that produced it (SCHEMA B4) |

## To settle together

- Whether candidates may later widen from pinned ids to a model family, with re-verification (default: pinned ids,
  widened only with re-verification).
- How routing reports a model outside the candidates, if it ever must.
