# Verified Numbers Ledger + P0 Adjudications

Built 2026-09-11 against `/home/muk/work/AI4Research` @ **`b0bf165f9ab073aae23e45b3b2796973e5677eea`**
(confirmed by `git rev-parse HEAD`).

**Rule this file enforces:** no bare integer, count, percentage, version string or
date appears in the talk script or the companion report unless it has a row here.
Every row was produced by running the command, not by reading a note.

**Why the last column exists:** a trap silently avoided gets reintroduced by the
next drafter. A trap printed beside its correction cannot be.

---

## P0 adjudications — both closed

### P0(a) — the freeze-hash gap. RESOLVED in favour of R5.

R5 and R6 reached opposite `[verified]` conclusions; the ledger sided with R5 and
R6 was never rebutted. Re-read directly at HEAD, Tier-1:

| Proposition | Verdict | Evidence |
|---|---|---|
| `_runtime_node` emits `write_scope` | **TRUE** | `harness/lib/scheduler_input.py:448` — `"write_scope": [produce_paths.get(item) or item for item in produces]` |
| `verify_runtime_projection` re-derives from the hash-verified input and field-compares | **TRUE** | `scheduler_input.py:934-960` — builds `expected` from `value["graph"]["nodes"]`, compares against `graph["nodes"]`, returns `SCHEDULER_RUNTIME_PROJECTION_TAMPERED` on any divergence or unexpected key |
| `write_scope` is exempt via the mutable allowlist | **FALSE** | `RUNTIME_PROJECTION_NODE_FIELDS` has **54** names; `write_scope` is **not** among them → it *is* compared |
| `task_graph.contract.json` is hash-anchored | **TRUE** | `harness/lib/elastic_planner.py:7909-7910` — `task_graph_ref.sha256 != sha256_payload(graph)` → `evaluation_plan.task_graph_ref.hash_mismatch` |
| `human_review` is genuinely exempt | **TRUE** | `scheduler_input.py:74` — present in the allowlist, by design, as live scheduling state |

**Rebuttal to R6 (mandatory under the protocol).** R6 claimed
`verify_runtime_projection` "never re-derives `scheduler_input`." That describes
only the function's opening block; the re-derivation is at `:934-941`, inside the
same function. R6 separately claimed the graph is loaded "with no hash anchor" at
`:7778` — the anchor is 131 lines later at `:7909`. **Both R6 errors are
early-stop errors**: it stopped reading inside a long function, and stopped at a
load site without following to its validation site.

→ Generalised into hygiene rule **H5**: *when claiming a function does not do
something, cite the function's last line.*

R6 is correct on exactly one point, which R5 also conceded: `human_review`.

### P0(b) — duplicated filenames between `harness/lib` and `harness/tools`. SETTLED: **neither 198 nor 157.**

```
lib top-level files   : 283
tools top-level files : 279
SHARED FILENAMES      : 179
  byte-identical      : 120
  differing           :  59
(recursive-basename variant, for completeness: 346)
```

**179 / 120 / 59.** The shipped report's headline of **198** is unreproducible —
and is contradicted by *its own stated method line*, which says "179 regular
files, 120 byte-identical." R5's **157** is also not reproducible. Use 179/120/59
or omit the figure; it is not load-bearing for either deliverable.

---

## The ledger

| # | Figure | Verified value | Command / source | Wrong value in circulation |
|---|---|---|---|---|
| 1 | Registered capsules | **80** — 77 capability, 1 guard, 2 resource; 80 unique ids, 80 unique `manifest_path` | `capability-capsules.registry.yaml` → `capsules` | **68** in several docs |
| 2 | `cap.*.yaml` files on disk | **79** | `find harness -name 'cap.*.yaml'` | — |
| 3 | On disk but **unregistered** (inert) | **5** — `advanced-optimization-reference-worker`, `chatgpt-browser-agent`, `gemini-enhanced-search`, `notebooklm-enrichment`, **`research-report-draft`** | registry `manifest_path` basenames vs disk | "inert by design" — **`research-report-draft` is genuine drift**, named by a live `/paper-draft` route |
| 4 | Logical operators | **45** | `logical-operators.json` → `logical_operators` (dict) | — |
| 5 | Bound roles | **44** | same → `bindings` | — |
| 6 | Mean routing candidates | **2.75** (121 candidates / 44 roles) | same, summed | **2.8** — still wrong in `07-` and `09-` |
| 7 | `Scientific*` logical roles | **21**, of which **20** bound | `logical-operators.json` keys | ⚠ "15 `scientific-*` roles" has **no reproducible referent** — not logical roles (21), not physical operators (0). Do not use it. |
| 8 | Physical operators | **102** | `physical-operators.json` → `operators` | — |
| 9 | …enabled | **63** | same | Do not quote 102 as a capability count |
| 10 | …declaring no `provider` | **52** | same | "52 vendor-neutral operators" **mischaracterises 33 of the 52** (all three fields null, backend `command`). Only **18** carry the full triple. Upper bound, not a headline. |
| 11 | Evidence schemas | **33** | `ls harness/schemas/evidence/*.schema.json \| wc -l` | onboarding doc implies ~7 |
| 12 | Version | **1.0.0-rc.9** | `cat VERSION` | `package.json` **3.0.0** is stale |
| 13 | Regression suite | **606 passed / 34 failed / 8 skipped in 992.68s** | stabilization log **:862** | — |
| 14 | …failure breakdown | 2 report/publication fixtures referencing unmaterialised files; **20** old Scheduler/Dispatcher fixtures rejected by current frozen-PlanIR preflight *before* their assertion; 5 composition-registry expectations stale; 7 fixed-workflow incl. Windows-direct WSL/Bash paths | log **:862** | — |
| 15 | AutoSci parity | 28 skills scanned, 28 routes configured, 0 missing, **0 full**, 18 partial, 10 approval-gated | `docs/integrations/autosci/autosci-solar-feature-parity-matrix.md:21-31` | ⚠ **doc claim, not a live scan** — `../AutoSci` does not exist on this machine, so `autosci_parity_inventory.py` cannot run |
| 17 | Intent-stage model calls | **58 receipts** across **25** live cases, all carrying `duration_ms` | `metadata/2-*/live-25-prompt-pipeline-20260826/*/model_call_receipts.json` | — |
| 18 | …call latency | min **6.7 s** · median **13.9 s** · max **66.3 s** · total **1,124.7 s** | same, aggregated | ⚠ One stage, one machine, one provider, August 2026. **Not a system latency figure**, and there is no system latency figure. |
| 16 | lib/tools shared filenames | **179** (120 identical, 59 differing) | see P0(b) | **198** (shipped), **157** (R5) — both unreproducible |

---

## Run ledger — the conflation trap

A numbers table cannot catch a *merge*; the error is a borrowed property, not a
wrong integer. **These two runs are never named in the same sentence without this
table in view.**

| | **Run A** | **Run B** |
|---|---|---|
| Date | 2026-09-02 | 2026-09-03 |
| Sprint | (14-node) | `sprint-20260903-072109-intent-conduct-an-end-to-end-system-cf3739f6` |
| Nodes | 14, all executed | **15/15 passed** |
| Delivered | all 8 requested files | — |
| Recorded | `all_nodes_passed=true`, closure PASS | closure `closed`, `all_nodes_passed=true`, `all_required_gates_passed=true` |
| Outcome | The log's own conclusion, **translated** from `…log:638`: *"this sprint can only prove physical execution and eight-file delivery; it cannot count as a complete E2E PASS."* The delivered `research_run_manifest.json` itself declared `evidence_gate.status=failed_for_full_requested_scope` and `closure_status=open_degraded`; `poster.html` likewise displayed `Evidence Gate: Not Passed`. **All six** input sources had parsed, but H2O and SnapKV were excluded by source assessment, leaving four, with insufficient method/comparison/metric coverage. ⚠ "Retracted" is **not** the log's word — verified: zero occurrences of 撤回/撤销/收回/作废 nearby; the source verb is 冲突 ("conflicts with"), and the retraction-like effect is the permanent fix at `:639`, i.e. future behaviour. Fair as characterisation, never inside quotation marks. | **Accepted** — the project's own highest-level evidence, *with* a mid-run hotfix and coordinator restart |
| Source | log **:638** | log **:863** |
| Used for | the self-retraction argument (script §3.2) | the status claim |

Two further 14-node passes exist at log **:781** and **:795**. **Run C** = log **:793-796**,
`sprint-20260903-030314-intent-conduct-an-end-to-end-system-6619dfa8`, 2026-09-03: intent gen 0 had the
"only these 5" fidelity catch and 1 bounded repair; requirement and plan accepted first time; 14/14 nodes at
attempt 1; ledger revision 106; closure `closed`, `all_nodes_passed=true`, `all_required_gates_passed=true`;
8 files delivered; the run manifest marked evidence gate and closure `pending_*` at publication and the
deterministic evaluator and scheduler closure gave the final verdict afterwards. **Run C is the run the workflow
report describes** (§2.1 example, Table 5, Table 6, App. C). It is NOT Run A: on 2026-09-15 an overnight edit
attached Run A's evidence-gate failure to Run C in Tables 5 and 6 and deck slide 13; corrected the same day.
Per `VARIANT-3:1188`, **do not quote a run count** — at least one recorded pass was
later retracted by the project, so passing-flag counts are not a reliable measure.

---

## Forbidden phrases

| Never write | Write instead |
|---|---|
| "the last recorded full E2E failed at Planner schema admission" | **Superseded.** ⚠ `08-workflow-end-to-end.md:206-209` and `09-report-presentation-kit.md:126` are **stale and must not be drafted from.** Use the run ledger above. |
| "52 vendor-neutral operators" (unqualified) | "52 declare no provider; 18 carry the full vendor-neutral triple" |
| "2.8 candidates" | "2.75" |
| "68 capsules" | "80" |
| "version 3.0.0" | "1.0.0-rc.9" |
| "N runs have passed" | "passing-flag counts are not a reliable measure here, and this report does not offer one" |
| "198 duplicated filenames" | "179 shared filenames, 120 byte-identical" |
| "15 scientific-* roles" | "21 `Scientific*` logical roles, 20 bound" |

---

## Translation provenance

Two passages in these deliverables are translated from Chinese. Both were run
through the kit at `/home/muk/work/translate/`.

| Source | Used for | tcheck | Critic |
|---|---|---|---|
| `…log-20260829.md:638` | the self-acceptance incident (talk §3.2, run ledger above) | OK — 0 failures, 0 warnings | fresh subagent · **faithful-with-fixes**, applied |
| `…log-20260829.md:862` | the regression-suite row and its failure breakdown | OK — 0 failures, 0 warnings | fresh subagent · **faithful-with-fixes**, applied |

Full translations, the Chinese originals copied from the file, and a
*do-not-restore* table of four renderings the source does not support live in
`report/TALK-15MIN-WORKFLOW-SCRIPT.md` under **Source note**.

**Translation never upgrades evidence.** The log is the project's own record of
what it did and concluded. A translated sentence from it is a faithful rendering
of that record — not independent confirmation that the record is correct.

### Line 862, translated in full

> Before release, an aggregate regression was run over 22 affected Python test
> files: `606 passed / 34 failed / 8 skipped in 992.68s`. Failures are not to be
> hidden or recorded as all-green: 2 old report/publication pass fixtures
> reference relative files that were not in fact materialised; 20 old
> Scheduler/Dispatcher fixtures are rejected by the current frozen PlanIR
> preflight before reaching their target assertion; 5 old composition registry
> expectations are inconsistent with the current registry; 7 fixed-workflow items
> cover failures from Windows directly running WSL/Bash paths and from old
> contract fixtures. All of these failures are retained as known regression debt;
> they were not modified by loosening product gates, fabricating artifacts, or
> making downstream accommodate the old fixtures.

2 + 20 + 5 + 7 = 34, matching the `34 failed` in the protected span.

## Method notes for whoever extends this

- **H1 saved two false findings while building this file.** A naive extractor
  reported *"0 `scientific-*` roles"* and *"1 registered capsule"* — both wrong,
  both caused by guessing the JSON/YAML shape instead of inspecting it. Neither
  corpus was at fault. **Inspect the structure before reporting an absence.**
- **`rg` is a shell function here and `grep` is aliased to `ugrep`.** With stderr
  redirected a broken invocation returns a silent empty result that reads as
  "zero hits." Prefer Python for counts; run a positive control before any
  negative conclusion.
- **Read append-only logs to the end.** `migration-handoff-20260831.md` is a
  mid-arc snapshot with ~230 lines of log after it. Two agents independently
  drafted the wrong status from it. The last entry wins.


---

## Critic record

Fresh subagent critic (`prompts/critic.md`), source opened and read independently.

**Verdict: faithful-with-fixes.** Three findings, all applied:

| # | FM | Sev | Was | Now |
|---|---|---|---|---|
| 1 | FM-7 | medium | "…include Windows directly running WSL/Bash paths, **together with** old contract fixture failures" | "…**cover failures from** Windows directly running WSL/Bash paths **and from** old contract fixtures" — the old wording read as a category *outside* the 7, breaking 2+20+5+7=34 for an English reader |
| 2 | FM-6 | low | "files that were **never** materialised" | "were **not in fact** materialised" — 并未 is emphatic negation of a fact, not a temporal universal |
| 3 | FM-1/M7 | low | unlisted term, no row | pending glossary row filed for 研究真值 |

**Three of my own pre-critic self-fixes were confirmed correct**, and one was
confirmed as the *only* safe option: 失败不能被隐藏 cannot be rendered "cannot be
hidden," because failures obviously *could* be — that rendering would be false.
"Are not to be" is right and should not move.

**One self-fix was refined**: 作为 is categorial, so "cannot **count as**" is a
tighter fit than "cannot serve as". Truth conditions unchanged.

**No omissions in either passage** — every clause, hedge, quantifier and list
item accounted for, both directions.
