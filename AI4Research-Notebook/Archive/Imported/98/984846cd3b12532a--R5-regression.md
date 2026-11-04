# R5 — Regression fact-check of corrected VARIANT-3 / VARIANT-1

Repo: /home/muk/work/AI4Research @ b0bf165f9 (openJiuwen-Solar). Read-only. All
line numbers verified directly against checked-out source unless noted.

## Verdict summary

| # | Claim | Verdict |
|---|---|---|
| 1 | `_demote_exhausted_fidelity_findings` at 1230-1263, demotes FAIL to advisory on budget exhaustion | CONFIRMED |
| 2 | `SOLAR_INTENT_REVIEWER_MODEL`; same model reviews itself if unset | CONFIRMED |
| 3 | `contract_sha256` doesn't cover task_graph, write_scope/artifact-name/human-review mutable undetected | **WRONG for write_scope; self-contradicts report's own §8. Partially right only for human_review.** |
| 4 | Same filename/path string-matching gate-inference bug at graph_node_dispatcher.py / evolution_engine.py | CONFIRMED as residual **fallback** path (not primary); hedge is fair, and slightly understates that the primary path was fixed |
| 5 | ≥3 full runs, two of 14 nodes, one of 15, all gates passed | CONFIRMED, exact quotes below |
| 6 | 19/52 operators carry neutral+registry+evidence_transform; 33 null+command | **OVERSTATED**: only 18 satisfy all three; a 19th satisfies only two of three (execution_trust is `measured_execution`, not `evidence_transform`) |
| 7 | eval(~30, exec(~18, shell=True~14, dup filenames 198, no lockfile, ~575 suppressions | eval/exec/shell=True/lockfile/575 all CONFIRMED exactly; **198 duplicated filenames is WRONG** (actual ~157–359 depending on method, no method reproduces 198) |
| 8 | README banner says Requirement Compiler "still deterministic"; default compiler is LLM-based | CONFIRMED, translation fair |
| 9 | 2.75 avg candidates, 15 scientific-* roles, core/hive/index.ts:167-195 | CONFIRMED exactly, including secondary numbers (74/24/20/3, dimension counts 20/14/8) |

---

## Claims that are WRONG or OVERSTATED (with exact replacement text)

### Claim 3 — the freeze hash gap (most serious finding; report's own centerpiece)

**What is actually true:**

- `frozen["contract_sha256"] = sha256_payload(frozen)` (`elastic_planner.py:7345`) hashes a
  dict of `*_ref: {id, sha256}` pointers, including `scheduler_input_ref` (sha256 of the
  full `scheduler_input.json`).
- `scheduler_input.json`'s node data is built by `_runtime_node()`
  (`scheduler_input.py:390-460`), which *derives* `write_scope` from
  `artifact_contract.produces` + `produce_paths` — i.e. `write_scope` is inside the
  hash-pinned artifact, not outside it.
- `verify_runtime_projection()` (`scheduler_input.py:849-955`) is called at every
  `assign_ready()` (`graph_scheduler.py:3138`, and 5+ other dispatch entry points) and
  **re-derives every node's `write_scope`/`read_scope`/routes from the hash-verified
  `scheduler_input.json` and raises `SCHEDULER_RUNTIME_PROJECTION_TAMPERED`** (via
  `ValueError` in `assign_ready`) if the on-disk `task_graph.json` disagrees. This is a
  real, enforced, deterministic anti-tamper check on `write_scope` — the report's own §8
  says so almost verbatim ("fully re-derives the projection from the frozen source and
  byte-compares it. This is anti-tamper, not a shape check.").
- Separately, `verify_frozen_execution_chain()` (`elastic_planner.py:7748-8052`) loads
  `task_graph.contract.json` and calls `compile_scheduler_input(graph, ...)` to
  **recompute** `scheduler_input.json` from it and diffs the two
  (`recomputed_scheduler_input != scheduler_input` → `scheduler_input.recomputed_mismatch`,
  line ~8016). It also checks `evaluation_plan.task_graph_ref.sha256 == sha256_payload(graph)`
  (line 7909-7910), which transitively pins `task_graph.contract.json` through the
  `evaluation_plan_ref` chain into `contract_sha256`. So `task_graph.contract.json` tamper
  IS caught by re-derivation, contrary to "not referenced by hash... can be edited after
  the freeze without invalidating the hash."
- The ONE part that is genuinely true: `human_review` is explicitly listed in
  `RUNTIME_PROJECTION_NODE_FIELDS` (`scheduler_input.py:74`), the allow-listed **mutable**
  node fields excluded from the byte-comparison — so human-review state legitimately
  changes post-freeze without tripping `verify_runtime_projection`. That is by design
  (it's live scheduling state, not contract content), not a gap comparable to write_scope.
- "artifact-name text" is not grounded to any specific field in the code; unverifiable as
  written.

**Verdict: WRONG for `write_scope` and for `task_graph.contract.json`; the report
contradicts itself two paragraphs apart (§7 "no deterministic check noticing" vs. §8
"fully re-derives... byte-compares it... anti-tamper, not a shape check" — both describing
the same mechanism). "human-review state" is legitimately excluded by design, but citing it
alongside write_scope as an equivalent security gap is misleading.**

**Suggested replacement text for §7 "What the hash does NOT cover":**

> `contract_sha256` itself is a hash of pointers (`*_ref.sha256`), not a hash of raw
> artifact content — but every field that matters, including `write_scope`, is reachable
> either directly (`scheduler_input_ref` covers the derived `write_scope` inside
> `scheduler_input.json`) or transitively (`task_graph.contract.json` is pinned through
> `evaluation_plan.task_graph_ref` and independently re-derived by
> `verify_frozen_execution_chain`'s `compile_scheduler_input` recomputation). Separately,
> `verify_runtime_projection`, invoked at every scheduling tick, re-derives `write_scope`
> from the hash-verified source and fails closed on divergence. The one field that is
> genuinely, deliberately excluded from tamper detection is runtime `human_review` state
> (`RUNTIME_PROJECTION_NODE_FIELDS`), because it is live scheduling state, not frozen
> contract content — this is by design, not a gap.

### Claim 6 — 52/19 operator split

Actual counts from `harness/config/physical-operators.json` (`operators`, 102 total, 52
with no `provider`):
- 18 operators have `model_provider_neutral: true` **and** `backend:
  "research_operator_registry"` **and** `execution_trust: "evidence_transform"` (all three).
- 1 more operator (`experiment_run_worker`) has `model_provider_neutral: true` and
  `backend: "research_operator_registry"` but `execution_trust: "measured_execution"`, not
  `evidence_transform`.
- 33 operators leave all three fields null, with `backend: "command"`.
- 18 + 1 + 33 = 52. ✓ arithmetic closes, but the report's "19... carry
  `model_provider_neutral: true` + backend `research_operator_registry` + `execution_trust:
  evidence_transform`" folds the 19th operator into a bucket it doesn't actually match.

**Suggested replacement:** "18 of the 52 carry the full triple
(`model_provider_neutral: true` + `research_operator_registry` backend +
`execution_trust: evidence_transform`); a 19th (`experiment_run_worker`) matches on the
first two fields but declares `execution_trust: measured_execution`; the remaining 33
leave all three null with `backend: command`." VARIANT-1's phrasing ("19 of the 52 carry
the full vendor-neutral field set") has the same imprecision.

### Claim 7 — duplicated filenames (198)

Grepped/counted directly:
- `eval(` in `harness/`: **30** occurrences — CONFIRMED as stated (~30).
- `exec(` in `harness/`: **18** — CONFIRMED (~18).
- `shell=True` in `harness/`: **14** — CONFIRMED (~14).
- No Python lockfile (`poetry.lock`/`uv.lock`/`Pipfile.lock`/`requirements*.lock`) at repo
  root — CONFIRMED.
- `noqa`/`type: ignore`/`pylint: disable` comments in `harness/**/*.py`: **575** exactly —
  CONFIRMED (~575), matches precisely once `pragma: no cover` is excluded from the count.
- Duplicated filenames between `harness/lib/` and `harness/tools/`: tried multiple
  methodologies, none reproduces 198:
  - top-level only (`-maxdepth 1`) both dirs: **157** shared basenames.
  - `lib` recursive vs `tools` top-level: 158; `lib` top-level vs `tools` recursive: 157.
  - fully recursive both dirs, unique shared basenames: **315**.
  - fully recursive, summing file-count multiplicities for shared names: 761 files / 359
    min-pairs.
  198 is not produced by any of these. **This number is WRONG.**

**Suggested replacement:** "Duplicated filenames between `harness/lib/` and
`harness/tools/`: 157 at the top level of each directory (359 pairs if subdirectories are
included). Some are byte-identical; this remains a real maintenance hazard, but the report
should not cite a specific total without stating the counting method, since it varies by
2x depending on whether subdirectories are included."

---

## Confirmed claims (spot-checked with exact evidence)

- **Claim 1**: `_demote_exhausted_fidelity_findings` is defined at `harness/lib/intent_compiler.py:1230`, ends at line ~1263 (`_assert_schema(advisory, ...)` / `return advisory`). Called at line 1437, only when `validation.status == "pass"` and `fidelity.status == "fail"` **after** the repair loop (`for generation in range(_configured_intent_max_repairs() + 1)`) has exhausted its budget. It converts every `fidelity.errors` entry to a `warnings` entry, flips `fail`→`warning` on checks, and sets `status = "pass_with_warnings"`. No other deterministic check in `intent_compiler.py` re-examines those demoted findings before `decide_acceptance()` — the report's characterization is accurate, not overstated.
- **Claim 2**: `SOLAR_INTENT_REVIEWER_MODEL` / `SOLAR_INTENT_REVIEWER_PROVIDER` exist (`harness/solar-harness.sh:4126-4128`, `harness/metadata/README.md:106`). `model_from_environment("reviewer")` → `stage_model("intent","reviewer")` (`intent_compiler.py:351-354`) resolves via `SOLAR_INTENT_REVIEWER_MODEL` → `SOLAR_INTENT_MODEL` → `SOLAR_LLM_MODEL` → `""`; same fallback chain (swap `REVIEWER`→`COMPILER`) governs `compile_model`. `create_model()` (`structured_model.py:220-256`) defaults empty model/provider to canonical provider `"openai"` with the registry's default model. If none of the intent-stage env vars are set, `compiler_model` and `reviewer_model` are literally identical objects (same provider, same model). `run_pipeline()` never compares `compiler_model` vs `reviewer_model` for independence (unlike `elastic_plan.py:93-95`, which explicitly sets an `independence` flag for the *planner* reviewer — no equivalent exists in `intent_compiler.py`). Confirmed precisely.
- **Claim 4**: `graph_node_dispatcher.py:2754` and `evolution_engine.py:243` both define `_node_requires_deepresearch_quality_gate` with an identical shape: check explicit `node.get("research_quality_gate_required")` first, else fall back to a capability regex plus `REPORT_ARTIFACT_RE`/`DEEPRESEARCH_GATE_ARTIFACT_RE` matching over `write_scope` and artifact-text strings. `harness/metadata/pre-scheduler-stabilization-log-20260829.md` (§ "六附件复跑：Survey Synthesis...", ~line 848-852) documents this exact bug live in production (`final_report_plan.json` misclassified as a final DeepResearch report by the `final_report` substring rule) and its fix: nodes **with** `evaluation_binding` now require the explicit `research_quality_gate_required=true` flag; nodes **without** `evaluation_binding` ("legacy") still use the old text heuristic. The pattern genuinely persists as a documented, intentional fallback for legacy nodes, not a fully-fixed dead code path. The report's hedge ("whether relapsed or parallel unfixed instances was not resolved") is fair — it undersells slightly that the primary path (nodes with `evaluation_binding`) was fixed, and the fallback is a known, accepted residual for legacy nodes rather than an untouched relapse.
- **Claim 5**: `pre-scheduler-stabilization-log-20260829.md` documents three distinct full-pass runs:
  - sprint `a0e3b398` (line ~781): *"最终图为 14/14 passed；Scheduler Closure 为 closed、all_nodes_passed=true、all_required_gates_passed=true，sprint status 为 passed/completed"*.
  - sprint `6619dfa8` (line ~800): *"最终 runtime ledger revision 106、run_status=completed、passed=14。Scheduler-owned Closure 为 closed、all_nodes_passed=true、all_required_gates_passed=true"*.
  - sprint `cf3739f6` (line ~854/863): *"该sprint最终runtime revision 530、15/15 nodes passed、run_status=completed"*, later reconfirmed: *"15/14... 15/15节点通过、Closure closed、all_nodes_passed=true、all_required_gates_passed=true"*.
  Two 14-node, one 15-node, all with `all_required_gates_passed=true`. CONFIRMED exactly as stated (and VARIANT-1's "606 passed, 34 failed, 8 skipped" pre-release suite figure and "63 of 102 enabled" figure both check out exactly too).
- **Claim 8**: `README.md:7` (checked out): *"当前 Requirement Compiler 仍为 deterministic；Discovery 语义缺陷尚未解决。"* — translation "the Requirement Compiler is still deterministic" is fair and literal. `harness/lib/requirement_compiler/compiler.py:284-291`: `compile_requirement_ir()` docstring reads *"Compile semantics with an LLM; old literal flattening is explicit opt-in."* and only calls `compile_requirement_ir_legacy()` (deterministic) when an explicit legacy flag/work_dir-absent branch is hit; otherwise it requires `work_dir` and runs the LLM path. Default path is LLM-based; legacy deterministic path is opt-in only. CONFIRMED.
- **Claim 9**: `harness/config/logical-operators.json`: 45 `logical_operators`; capability-dimension histogram over all `required_capabilities` keys gives exactly 15 distinct dimensions, top three `scientific_evidence: 20`, `research_synthesis: 14`, `data_extraction: 8` — all exact matches. `primary_role` values starting with `scientific-` sum to exactly **15** across the 45 roles (`scientific-paper-ingestor:2, scientific-memory-updater:2, scientific-claim-extractor:2, scientific-experiment-runner:2, scientific-report-writer:2, scientific-literature-discoverer:1, scientific-source-assessor:1, scientific-code-evidence-mapper:1, scientific-experiment-designer:1, scientific-claim-verifier:1`). `bindings`: 44 of 45 roles bound, 121 total candidates, average exactly **2.75**, condition counts `always:74, quota_ok:24, plugin_autosci_available:20, emergency_only:3` — all exact matches. `core/hive/index.ts` is 438 lines; lines 167-195 are exactly `setupSchedulerCallbacks`'s `scheduler.onTaskCompleted` handler, which only calls `this.ledger.rewardForTask(...)` / `this.ledger.penalty(...)` — confirms "only updates a credits ledger." All CONFIRMED.

---

## New errors introduced by the corrections

1. **§7 "What the hash does NOT cover" directly contradicts §8's own description of
   `verify_runtime_projection`**, published two paragraphs later in the same document. This
   is the most serious new error: a corrected claim that undermines the report's own next
   section. It reads as if two different reviewing passes wrote adjacent paragraphs without
   reconciling them.
2. **The 19/52 operator split (§ table / VARIANT-1 §5) is a rounding-up of 18 exact matches
   plus 1 partial match**, stated as if all 19 satisfy the same three-field test. Minor but
   should be corrected since the report elsewhere emphasizes precision as its defining
   virtue (§1.3: "a design document is evidence of intent, never evidence of behaviour" /
   demand for exact verification).
3. **The 198 duplicated-filenames figure in §38b has no reproducible basis.** Every
   methodology tried lands between 157 and 359 depending on whether subdirectories are
   included — never 198. Given the section is explicitly framed as "counter-evidence" meant
   to be checked ("Verify each count yourself with grep/find. Report ACTUAL numbers"), this
   is exactly the kind of claim the correction pass should have re-derived and didn't.

## Any claim still marked [verified] that should be downgraded

- §7, "What the hash does NOT cover" paragraph — every sentence in it is marked
  `[verified]` but is wrong/overstated per Claim 3 above. Should be downgraded to
  "corrected" and rewritten per the suggested replacement text.
- The 19/52 operator-split line (wherever it carries a `[verified]` tag) should be
  downgraded to reflect the 18-exact/1-partial breakdown.
- The §38b table row "Duplicated filenames... | 198" should be downgraded and replaced
  with a sourced, method-stated number (157, stating the method), since no verification
  method reproduces 198.
