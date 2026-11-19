---
id: cc-v2-builder-profile
status: draft-extension
source: November 19 builder-CC pre-demo (Satay), research reports on artifacts and contract lineage
last_reviewed: 2026-11-19
next_action: Exercise on the five starred engine builder CCs; promote only what survives
---
# Builder profile (`cc-builder/1`, draft)

An optional profile for a CC that **builds or changes a part of a program** from a work order. It adds no field to the closed core objects. The core schemas stay unchanged. A host or work order selects the profile explicitly. Everything here is an **extension**; nothing is required of ordinary CCs.

## Why a bundle, not only a tool

A builder CC is shipped as a pinned bundle, so an agent that adopts it receives more than a callable:

| In the bundle (materials, hashed in the release index) | What the agent gets |
|---|---|
| guide and method | how to do the job, what "done" means, what must never be claimed |
| ontology slice and source map | the engine vocabulary and exact places in the code, verified against a pinned base |
| component manifest | the diff to make: files, gate, markers, invariants, rollback |
| tests and a `verify` capability | checks the CC runs on itself before it may report done |
| pinned hashes | a reviewer can approve its behaviour once and recognise the same bytes again |

Because the format and digests are standard, an approver reviews the bundle once and knows exactly what an agent will be handed.

## Work order (inputs)

The caller supplies, as artifacts or JSON: `contract` (what must hold; the ontology slice is part of it), `work_order` (repository, **full Git base commit**, component identity, allowed source paths, required checks, required evidence stages) and optionally `defaults` already fixed by the requester. The CC never edits the contract.

## Door-builder semantics

1. **Create or modify.** Resolve whether the component already exists in the base tree. If absent, create it. If present, modify it to match the work order and say which happened (`created` or `modified`). If the existing part conflicts with the work order, report a conflict instead of adding a second copy.
2. **Defaults.** If the work order is silent on a detail, choose a sensible default and record it as an entry `{pointer, value, chosen_by: "cc", reason}`. The CC does not refuse for lack of a detail and does not hide the choice.
3. **Verify before done.** The CC reports done only if every required check passed. A check that could not be run is `not_run`, never `pass`. Execution and acceptance are recorded separately: an execution can succeed while acceptance fails.

## Outputs (artifacts, `{uri, sha256}` as in core)

| Port | Content |
|---|---|
| `diff` | raw Git patch; with a `cc-source-change/1` descriptor binding repository, base, patch, expected tree |
| `build_record` | actual build command, observed base and tree, flags, toolchain identity, wall time, cache effects (`cc-build/1`) |
| `verification_receipt` | check ids, checker identity, verdicts (`PASS`, `FAIL`, `INCONCLUSIVE`, `UNAVAILABLE`, plus `NOT_RUN`) and evidence bound to the exact diff bytes |
| `activation_observation` | what proves the component actually ran (a `cc-observation/1` signal): the marker line, effective settings read back from the engine, and the log verbosity needed to see it |
| `defaults_chosen` | the list above |

A plain tool leaves the agent to guess whether the change engaged. The activation observation is the part that closes that gap: output parity alone can pass while the component never ran (observed on Satay 2026-11-19: with the default load mode the patch was silently inactive and the output still matched stock).

## Evidence stage

Each result entry names its stage, digest-bound after artifact capture by a host-finalized evidence index (not a field on `{uri, sha256}`): `fixture`, `native_cc_execution`, `compile`, `runtime_acceptance`, `hardware_measurement`. A later stage must never be inferred from an earlier one. A compile result carries no performance claim.

## Completion rule

A work order closes only when execution `succeeded`, completeness is `complete`, all declared artifact references resolve, and every required check is `PASS`. Issue verification evidence before closing: retain the candidate and its build and activation evidence, run the verifier on those exact bytes, then return the verifier's already-issued receipt.

## Open points
- A formal JSON schema for the work order, build record and verification entries is not written; the prototype fields above are descriptive.
- The core has no `kind: builder` or `stage` field, and adding either to closed objects would conflict with the existing schemas. Keep both in the profile and evidence index.
- Contract lineage: the M1 contract is the Research Brief. The factory's own contract JSON is a downstream translation with no importer; its A/B gate scores only `eval_ms_per_token`, so a prefill or TTFT target needs an added scoring rule before a factory run can score it.
