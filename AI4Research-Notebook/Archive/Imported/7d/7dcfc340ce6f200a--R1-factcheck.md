# R1 Fact-Check — VARIANT-3-full-report.md

Repo: /home/muk/work/AI4Research, branch openJiuwen-Solar, HEAD b0bf165f9 (confirmed via `git rev-parse HEAD`).

## Verdict summary

Roughly 70 discrete factual claims were checked against the live tree (grep,
`wc -l`, JSON/YAML parsing of registries, and direct reads of cited files).
This report is unusually well-sourced: nearly every counted quantity, file
path, function name, line range, and quoted string checks out exactly,
including the hardest ones (the `verify_frozen_execution_chain` line range,
the `capability_admission.py` 35-line/5-code claim, the 80/77/1/2 capsule
split, the 5 unregistered files by exact name, the capsule-plan.v1
conditional schema, and every number in the §33 2026-09-03 E2E claim).

**1 clear overstatement found** (load-bearing, in the executive-summary-level
"52 vendor-neutral operators" claim). **2 minor precision slips** (a rounded
average, an approximate role count that contradicts its own hedge, a
function-range off-by-a-few). **0 wrong counts, 0 fabricated quotes, 0 false
negative claims.**

- Claims checked: ~70
- Wrong: 0
- Overstated: 1 (severe/load-bearing) + 2 minor
- Confirmed correct: ~65
- Unverifiable in the time available: ~2

## ERRORS FOUND

### 1. [OVERSTATED — load-bearing] §10 "Physical operators (102)" table: the 52 "vendor-neutral" row mischaracterizes 33 of the 52 operators it counts

**Report's exact wording (§10, table + surrounding text):**
> | Vendor-neutral native | 52 | `model_provider_neutral: true`, backend `research_operator_registry`, `execution_trust: evidence_transform` — deterministic Python |
> ...63 of 102 are enabled; 93 are marked available. **That 52/50 split is the
> design thesis expressed as inventory: half the fleet has no model vendor.**

**What is actually true**, from `harness/config/physical-operators.json`
(102 operators total, confirmed):

- The 52/50 split is real as a *count*: 52 operators have no `provider` field
  at all, and the other 50 have an explicit provider (`openai:15,
  anthropic:11, google:7, local:5, browser:5, glm:4, deepseek:3` — this half
  of the table is exactly right).
- But of those 52, only **19** actually satisfy `model_provider_neutral:
  true` **and** `backend: research_operator_registry` **and**
  `execution_trust: evidence_transform` simultaneously (verified: `all3
  match: 18`, `neutral flag true: 19`, `backend registry: 19` — the
  flag/backend sets are identical and near-identical to the trust-class set).
- The remaining **33** operators (e.g. `autosci-paper-ingest-worker`,
  `autosci-paper-analyze-worker`, `autosci-graph-update-worker`,
  `autosci-idea-worker`) have `model_provider_neutral: null`, `backend:
  "command"` (not `research_operator_registry`), and `execution_trust: null`
  — i.e. those three fields are simply **absent from the manifest**, not set
  to the values the report attributes to them. They happen to shell out to a
  deterministic local Python script (`plugins/autosci/bin/autosci_bridge.py
  run --action ...`), so they probably *are* effectively vendor-neutral in
  practice — but the report states specific field values as fact for all 52
  when they hold for only 19.

**Proof:**
```
$ python3 -c "... no-provider count ..." -> 52
$ python3 -c "... model_provider_neutral True among the 52 ... " -> 19
$ python3 -c "... field missing entirely among the 52 ..." -> 33
harness/config/physical-operators.json: entry 'autosci-paper-ingest-worker'
  {'backend': 'command', 'model_provider_neutral': None,
   'execution_trust': None, 'provider': None}
```

This is the report's single most confidence-outstripping-evidence moment: a
number the report treats as a headline finding ("the design thesis expressed
as inventory") is real, but the *mechanism description* attached to it
(three specific field values) is fabricated-by-generalization for 63% of the
operators it covers. Recommend correcting §10 and the anticipated-questions
line in §36 ("the more informative number is 52 of 102 executors being
vendor-neutral") to note that the 52 figure is defined by *absence of a
`provider` field*, of which only 19 carry the cited `model_provider_neutral /
research_operator_registry / evidence_transform` triple; the other 33 are
`backend: "command"` operators with no provider metadata at all (inferred
vendor-neutral by omission, not declared).

### 2. [MINOR / precision] §10 "averaging 2.8 candidates" — actual average is 2.75

`harness/config/logical-operators.json` `bindings`: 44 bound roles, 121 total
candidates, 121/44 = **2.75...**, not 2.8. Small (would round to 2.8 only
with looser rounding); not worth a severity flag on its own, but noted since
§10 is otherwise number-perfect.

### 3. [MINOR / precision] §10 "some fourteen `scientific-*` roles" — actual count is 15

Counting `logical_operators[*].primary_role` values that literally start
with `scientific-` in `harness/config/logical-operators.json` gives **15**
(`scientific-paper-ingestor`×2, `scientific-memory-updater`×2,
`scientific-claim-extractor`×2, `scientific-experiment-runner`×2,
`scientific-report-writer`×2, plus 5 singletons). The role breakdown
immediately preceding it in the same sentence — "nine knowledge-extractors,
six evaluators, four builders, three planners" — is exactly right (9/6/4/3
confirmed). The "fourteen" is hedged with "some," so this is not presented
as [verified]-grade, but it is off by one from the true count and should
either be corrected to 15 or left unhedged-but-approximate language as is.

### 4. [MINOR / precision] §12 "core/hive/index.ts:167-190" for the HIVE `onTaskAssigned`/`onTaskCompleted` logging claim

`setupSchedulerCallbacks` (containing both callbacks) actually spans lines
167–195/196 in `core/hive/index.ts`, not 167–190 (the `onTaskCompleted`
block's closing brace and callback body runs to ~195). The *substance* of
the claim is exactly right — `onTaskAssigned` only does
`console.log(...)` (line 169-170) and `onTaskCompleted` only touches the
credits ledger via `this.ledger.rewardForTask` / `this.ledger.penalty`
(lines 172-195) — and the "zero cross-references between `core/hive/` and
`harness/`" claim is independently confirmed (no hits either direction). The
line range is just slightly short of the true function boundary.

## Overstatements (beyond #1 above)

None found beyond the items above. Notably, several claims that *looked*
like candidates for overstatement turned out to be precisely accurate on
inspection:

- §14's "41" and "39" capsule counts per directory are NOT raw file counts
  (`harness/config/capability-capsules/` actually holds 46 `.yaml` files on
  disk) — they are counts of *registered* manifests resolving to each
  directory via `manifest_path` (41 relative + 39 via `../capability-capsules/`
  = 80, matching the registry's `capsules.capability=77 + guard=1 +
  resource=2`). This reads ambiguous on first pass but is fully self-
  consistent and correctly derived — not an error.
- §18's [inferred] claim that admission reads normalized field names
  (`verification.self_checks` plural) that don't match the raw manifest
  (which uses `self_check` singular, confirmed in
  `harness/capability-capsules/cap.research-literature-discover.yaml`) is
  actually correct, appropriately flagged as inference rather than overclaimed
  as verified.

## Unverifiable claims

- The "final runtime verdict `failed`; 0 native-full stages" line in §33
  (AutoSci parity) could not be pinned to a single exact source file in the
  time available; `coverage_status` and parity-gate machinery exist and are
  real (`harness/evaluators/scientific/autosci_feature_parity_gate.py`,
  `harness/plugins/autosci/config/feature_parity_routes.v1.json` — confirmed
  28 routes, matching "28 native skills"), but the specific verdict string
  and "0 native-full stages" figure were not independently re-derived from a
  parity-audit artifact within budget. Not flagged as wrong — just not
  independently reproduced.
- §37 ledger item #12 ("README pipeline description... historical, superseded
  by the typed path") was not independently checked against the current
  README wording.

## Claims confirmed correct (representative, not exhaustive)

- HEAD `b0bf165f9`, branch `openJiuwen-Solar`, 5,386 tracked files
  (`git ls-files | wc -l` = 5386) — exact.
- `verify_frozen_execution_chain` at `elastic_planner.py:7748-8052` — exact
  (function starts line 7748, `return errors` at line 8052, next `def` at
  8055).
- `capability_admission.py` — exactly 35 lines, exactly the 5 rejection
  codes in the order given, docstring quote verbatim.
- Registry: 950-line `capability-capsules.registry.yaml`, 80 capsules
  (77 capability / 1 guard / 2 resource), 0 dangling, exactly the 5 named
  unregistered files with 0 false positives/negatives.
- 45 logical operators (exact); 15 capability dimensions (exact list);
  `scientific_evidence`=20, `research_synthesis`=14, `data_extraction`=8
  (exact); DeepArchitect required_capabilities quoted verbatim.
- 44/45 roles bound; conditions `always`=74, `quota_ok`=24,
  `plugin_autosci_available`=20, `emergency_only`=3 — all exact.
- 102 physical operators; 63 enabled; 93 available — exact.
- 33 evidence schemas — exact file count in `harness/schemas/evidence/`.
- §16 worked example (`cap.research-literature-discover`) — every quoted
  block (applicability, effects on all 6 axes, all 5 invariants,
  operator_compatibility) matches the YAML verbatim.
- §17 `EXECUTION_TRUST_CLASSES` / `PLANNER_EXECUTION_TRUST_RANK` — verbatim
  code match; rank-vs-exact-match discrepancy independently confirmed
  (`capsule_composition.py` rank dict vs `apo_plan_compiler.py` exact-match
  gate at lines ~990-997).
- §19 module line-count table — all 9 modules match `wc -l` exactly
  (1423/35/703/194/279/871/203/105/305).
- §20 grep-verified absences — `capsule://` = 0, `capsule.invoke` = 0, and
  `SCARE` = 0 hits anywhere under `harness/` or `core/` (9 hits total in the
  repo, all confined to the two named design docs); doc line counts 986 and
  1,139 exact.
- §21/§28: 863-line stabilisation log — exact; 142 L2 features, 1,502
  reviewed rows, 2,047 historical rows — all exact, sourced directly from
  `tests/platform/phase22/atomic_feature_matrix.json`'s `counts` block.
- §6 capsule-plan.v1 conditional schema — exact match: `selected:true` →
  required `[capability_capsule_id, dispatch_task_type, role, artifact_types,
  effect_union, proof_obligations]` + `stages.minItems:1`; `selected:false` →
  required `[unsatisfiable]` + `stages.maxItems:0`.
- §5 budgets: `SOLAR_INTENT_MAX_REPAIRS` default 1 cap 4, and
  `SOLAR_PLANNER_MAX_REPAIRS` clamp `[0,4]` default 1 — both exact, code
  quoted correctly.
- §5 requirement-compiler budget/documentation-trap claim — fully verified
  via `git show`: commit `f463b861b` introduced "3 compiler + 2 reviewer =
  5 calls" with split `structural_repairs`/`semantic_repairs` counters;
  commit `5ade9d9f3` collapsed this to one shared `calls` counter with a
  hard `calls >= 3` ceiling and an explicitly advisory semantic reviewer
  (comment: "subjective review never starts another compiler generation or
  blocks Planner handoff") — exactly as described.
- §9 negative claims: `capability_token.check_path_access()` has callers only
  in `tests/harness/test_capability_token_runtime.py` (confirmed, no
  production callers); `unified_selector.py` has no import outside its own
  test file, while `logical_operator_router.py` is imported by
  `harness/lib/actor_runtime.py` — confirmed; `desktop_bridge` appears in
  `physical-operators.json`/schemas but has **no branch** in
  `operatord.py::_build_command` — confirmed by reading the full function
  body.
- §12 HIVE: `core/hive/discovery/mdns.ts` exists and port `9876` is present;
  zero cross-references between `core/hive/` and `harness/` confirmed by
  grep in both directions.
- §26 benchmarks: SWE-bench Pro, SWE-bench Verified, BrowseComp, OSWorld,
  GAIA (with the exact HuggingFace URL cited), WebArena, tau-bench (with the
  exact GitHub URL cited) all present in
  `harness/lib/agent_arena_benchmark.py`; MLE-bench appears as "future
  adapters" language in `harness/docs/benchmark/terminal-bench-2.md`,
  matching "named as future work" exactly; "does not claim... unless
  actually run" is a near-verbatim paraphrase of the module's own docstring.
- §33 (the single highest-stakes section): every number reproduced exactly
  from `harness/metadata/pre-scheduler-stabilization-log-20260829.md`:
  sprint id `sprint-20260903-072109-intent-conduct-an-end-to-end-system-
  cf3739f6`, 15/15 nodes, `run_status=completed`, `all_nodes_passed=true`,
  `all_required_gates_passed=true`, closure closed, runtime revision 530,
  PID `779798` → `828727`, `606 passed / 34 failed / 8 skipped in 992.68s`.
  The narrative claims about the mid-run fix (reused original worker
  artifacts/sidecar/frozen plan, no hand-written graph) and the timeline
  compaction (deterministic projection from the gate ledger's terminal
  `status_transition` records, record IDs preserved, tagged
  `gate_ledger_terminal_projection`, originals backed up and SHA-256 hashed)
  are faithful, non-spun translations of the (Chinese-language) log entries
  at lines 848 and 855-861.
- `package.json` version `3.0.0` vs `VERSION` file `1.0.0-rc.9` — exact.

## Recommended corrections (exact replacement text)

**§10, replace the "Vendor-neutral native" table row and its follow-on
sentence:**

> | Vendor-neutral native | 52 | no `provider` field declared; of these, 19
> carry the full `model_provider_neutral: true` +
> `backend: research_operator_registry` + `execution_trust:
> evidence_transform` triple (deterministic Python via the registry
> adapter), while the other 33 are `backend: "command"` operators (e.g.
> `autosci-*-worker`) that shell out to local deterministic Python scripts
> but simply carry no vendor-neutrality metadata at all |
>
> 63 of 102 are enabled; 93 are marked available. The 52/50 split — defined
> by presence or absence of a `provider` field — is the design thesis
> expressed as inventory: half the fleet declares no model vendor, though
> only 19 of that half are explicitly flagged as such in the manifest; the
> other 33 are vendor-neutral by omission rather than by declaration.

**§10, footnote-style addition to §36's anticipated-questions answer** ("Is 80
capsules a lot?"): change "the more informative number is 52 of 102
executors being vendor-neutral" to "...52 of 102 executors declaring no
model provider (19 of which are explicitly flagged vendor-neutral; the
remaining 33 simply omit provider metadata)."

**§10, minor:** "averaging 2.8 candidates" → "averaging 2.75 candidates."

**§10, minor:** "some fourteen `scientific-*` roles" → "some fifteen
`scientific-*` roles."

**§12, minor:** "`core/hive/index.ts:167-190`" → "`core/hive/index.ts:167-195`"
(the `setupSchedulerCallbacks` method containing both callbacks).
