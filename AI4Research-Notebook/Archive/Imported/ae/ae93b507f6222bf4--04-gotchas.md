# 04 — Gotchas

Things that will cost you hours if nobody tells you.

## 1. The README documents a dead architecture

`README.md` describes `request_envelope → requirement_ir → prd.md +
Contracts.yaml + task_graph.json`. **This is the historical compatibility
chain.** The README's own top banner says so. The current formal path is
Intent → Requirement → Elastic Planner → frozen SchedulerInput → Scheduler.

Always cross-check against `harness/metadata/NEW-MACHINE-START-HERE.md`.

## 2. `package.json` version is a lie

Root `package.json` says `"version": "3.0.0"`. The real release version is in
`VERSION`: `1.0.0-rc.9`. The README explicitly warns not to read the Bun
package metadata as the installer release version.

## 3. `lib/` and `tools/` are near-duplicates

`harness/lib/` and `harness/tools/` share many identically-named files
(`actor_lease.py`, `capability_registry.py`, `activation_proof.py`, ...).
Before editing, confirm which one the executing path imports. Editing the wrong
copy produces a change that appears correct and does nothing.

## 4. Source tree ≠ installed runtime

Repo `harness/` is source. Installed runtime is `~/.solar/harness/`.
`solar-harness.sh` resolves `HARNESS_DIR` from
`${HARNESS_DIR:-${SOLAR_HARNESS_DIR:-$HOME/.solar/harness}}` and forces
`PYTHONPATH` to the **active tree**, because a prior bug had campaign runners
inject `PYTHONPATH` externally, hiding a fresh-install failure where product-mode
intake rejected its own child process as path-inconsistent.

Symptom to watch for: you edit repo source, run the CLI, and nothing changes —
you're executing the installed runtime.

## 5. A submit receipt is not execution success

`graph_node_dispatcher` / `operator_runtime` produce submit/accept receipts.
An acknowledged submission does **not** mean the operator ran or produced valid
output. There is a recorded case of a `rapid_smoke` receipt returning PASS while
an **empty discovery** was handed downstream.

## 6. `rapid_smoke` doesn't prove quality

`SOLAR_TEST_MODE=rapid_smoke` must be set via **trusted environment**, never
from a user prompt keyword or operator output. It cuts evaluation cost and
cannot be used as evidence of scientific quality.

## 7. Two unrelated "distributed" systems

- `core/hive/` — mDNS (port 9876) + P2P + coordinator election + bidding.
  A **decision layer with no executor**; `onTaskAssigned` is effectively a stub.
- `harness/remote_dispatch.py` — SSH/rsync push to `actor-hosts.json` hosts.
  Works today, centralized, **zero** integration with HIVE.

Test matrices conflate these. "Make distribution work" is ambiguous — clarify.

## 8. Encoding damage in Chinese docs

`tests/journeys/phase22/journey-test-plan.md` opens with a BOM plus mojibake
(`ï»¿# Phase 22 çœŸå®ž...`) — a UTF-8 → CP1252 roundtrip. Other files may be
affected. Read with explicit encoding; don't "fix" a file's encoding as a
drive-by change, and don't assume garbled text means a corrupt file.

Related: `scripts/check-windows-filenames.py` exists because this repo has real
cross-platform filename hazards. Note also a directory name with **spaces**:
`harness/metadata/3-requirements compiler output/`.

## 9. Absolute Windows paths in tracked docs

`AGENTS.md` names the "brief report" as
`C:/Users/j50058254/Downloads/AI4RnD Feature List.xlsx`. That's a
machine-local path in a tracked file, and it conflicts with `CLAUDE.md`'s rule
against personal paths in tracked files. Don't copy that pattern; flag it if
you're cleaning up.

## 10. Dirty worktree + concurrent agents is the normal state

`AGENTS.md` says so outright. Always `git status` first. Preserve out-of-scope
changes. Never bulk-merge branches. Never destructively reset a shared tree.

## 11. Config defaults can silently disable a pipeline stage

Documented example: with runtime `codex` and no `--search` flag, panes launch
without web search and **research stalls at the human-search gate** — no error,
just a stall. When something hangs, check which config-derived flags were
actually applied, not just whether the process started.

## 12. Not every stage has a JSON Schema

Several boundaries are enforced by code, not schema. Specifically:
`harness/schemas/task-graph-state.schema.json` **exists but was not observed
being loaded** on the executing path — you cannot claim its constraints are
enforced. The stage-7/8 envelopes under `harness/metadata/` are **design
examples**, not enforced contracts.

Also: v1 requirement contracts do **not** cover the current v2 path. Don't grab
a similarly-named older schema.

## 13. Don't double-compile the execution bundle

The Elastic Planner freezes internally via
`compile_and_freeze_execution_bundle`. Calling
`static_execution_compiler.compile_bundle` afterwards creates a second
authoritative compile. Explicitly called out as wrong.

## 14. Never auto-activate capsules by directory scan

68 capsule manifests are registered in
`harness/config/capability-capsules.registry.yaml`. Scanning
`harness/capability-capsules/` and activating what you find is explicitly
forbidden.

## 15. Known open semantic issue

As of the last recorded check: the **Discovery semantic defect was not
resolved**, and the Requirement Compiler had been changed from deterministic to
LLM-based with the old constraint AST preserved separately. Last full E2E
failed at Planner model output schema admission and **never reached the
Scheduler** — the user then halted repair and migrated.

Later fixes exist in the tree (`structured-output-compatibility-20260831.md`)
but were **source repairs with offline validation only** — not deployed to the
old runtime, not re-accepted online. **Do not claim end-to-end passes.**

Current status lives in
`harness/metadata/pre-scheduler-stabilization-log-20260829.md` — read its
latest entries before assuming any listed bug is still open.

## 16. Documentation is aspirational in places

`NEW-MACHINE-START-HERE.md` warns directly: *don't mistake architecture goals
for accepted behavior*, and *don't treat design examples as implemented
features*. Apply that lens to every design doc in `docs/` — there are ~50 of
them and many are proposals (`*_DESIGN.md`), not descriptions of shipped code.

---

## Additions from the capsule deep-dive (2026-09-10)

## 17. The registered-capsule count is stale in the onboarding doc

`harness/metadata/NEW-MACHINE-START-HERE.md` states **68** registered capsule
manifests. [verified] the registry now holds **80** (77 capability, 1 guard,
2 resource), all resolving on disk with zero dangling entries.

**If you put 68 in a report, it will be wrong.** Use 80, and consider noting
the drift as an observation.

## 18. Capsules live in two directories, one registry

```
harness/config/capability-capsules/    41 registered + 5 unregistered
harness/capability-capsules/           39 registered + 0 unregistered
```

`manifest_path` resolves relative to **the registry file's own directory**, so
`../capability-capsules/...` reaches the second store. If you resolve paths
relative to `harness/` instead, roughly half will appear missing.

## 19. Five capsule files on disk are unregistered — and that's the point

```
cap.gemini-enhanced-search.yaml
cap.chatgpt-browser-agent.yaml
cap.notebooklm-enrichment.yaml
cap.advanced-optimization-reference-worker.yaml
cap.research-report-draft.yaml
```

They are **inert**, because the registry is a governance gate, not an index
(see gotcha #14). Three are external-provider integrations, consistent with
`CLAUDE.md`'s "component-gated and off by default". Do not describe these as
missing, broken, or a packaging bug without checking intent — and **do not
register them**, since that would be a code change and an activation decision.

## 20. The artifact conversion registry is empty

`harness/config/artifact-conversions.v1.json` contains **zero** conversions,
while three `adapter.*` capsules are registered for artifact conversion and
`capsule_composition.py` loads the conversion registry for typed composition
search. 76 artifact types are defined; nothing converts between them.

Report as an open question, not a defect — the composition search may be
intended to operate on exact type matches for now.

## 21. `capability_admission.py` field names don't match the manifest schema

The admission checker reads `verification.self_checks`,
`verification.external_required`, `implementation.declared`, and
`operator_compatibility.selectable_preferred`. The capsule manifest schema
defines `verification.self_check` (singular),
`verification.external_verifier.required`, and
`operator_compatibility.preferred`, and does not require `implementation` at
all.

That strongly implies admission runs against a **normalized/derived** capsule
form produced by `capability_capsules.py`'s compatibility loader, not against
the raw YAML. Don't quote the raw manifest fields as if admission reads them
directly — trace through the loader first if the report needs that detail.

## 22. Physical operators have two different shapes

Of 102 entries, **52 carry `model_provider_neutral: true`** with no `provider`,
`plane`, `cost_tier`, or `auth_mode` — these are native AutoSci workers behind
`research_operator_registry`. The other 50 are vendor-bound model/CLI
operators with full provider metadata.

Naively aggregating `provider` across all 102 yields "52 = None", which reads
like missing data but is a real architectural distinction. Report it as the
split it is.

## 23. Requirement Compiler repair budgets: the docs describe a superseded model

[VERIFIED by code + `git log -p`]

`harness/metadata/semantic-retrieval-contract.md` and
`NEW-MACHINE-START-HERE.md` describe **split repair counters, a 5-call
ceiling, and a blocking semantic review** — introduced in commit `f463b861b`.

Commit `5ade9d9f3` **merged them back**: one shared counter, a **3-call
ceiling**, and an **advisory-only** review. Current HEAD code and its tests
agree with each other; the docs were never updated.

Cite the code, not the doc. This is a live example of the repo's own warning
that documentation lags implementation.
