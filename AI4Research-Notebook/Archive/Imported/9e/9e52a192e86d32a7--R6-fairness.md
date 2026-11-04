# R6 — Fairness Audit of the Post-Skeptic Revision

Auditor: fairness reviewer, read-only. Repo: `/home/muk/work/AI4Research`, branch
`openJiuwen-Solar`, HEAD `b0bf165f9`. Reviewed: `VARIANT-3-full-report.md`,
`VARIANT-1-brief-overview.md`, against `R3-skeptic.md` and the underlying code.

## Net verdict

The revision did not overshoot on its two hardest, most checkable claims — the
`contract_sha256` coverage gap and the §32 "should not be presented as closed"
caveat are both independently confirmed by reading the code, and if anything
could be stated *more* firmly, not less. But the revision overshot in three
other places: it undercounts the evidence for reproducibility (only one E2E
run is cited when the log documents at least three full passes), it uses
needlessly prosecutorial language for a narrow, deliberately-designed,
commented escape valve (`_demote_exhausted_fidelity_findings`), and it never
surfaces the strongest positive evidence in the whole corpus — a documented
case where the system caught its own `all_nodes_passed=true` vs.
`evidence_gate=failed` contradiction and shipped a permanent, tested,
fail-closed fix (the Publication Gate manifest-parsing fix). On balance the
report is closer to accurate than flattering, but it reads more prosecutorial
than the evidence supports, and a presenter handed only this document would
struggle to say anything affirmative about the system without first
apologizing for it.

## Over-corrections, with suggested restored wording

**1. VARIANT-1 §7 — "It works, once, demonstrably."** [OVER-CORRECTED]
The stabilization log records at least three complete `all_nodes_passed=true`,
`all_required_gates_passed=true` runs with real independent evaluator PASS
verdicts: two 14-node runs (`harness/metadata/pre-scheduler-stabilization-log-20260829.md:781`
and `:795`) and the 15-node centerpiece run cited in the report. Neither
VARIANT-3 nor VARIANT-1 mentions the two 14-node runs anywhere (grep for
"14/14" and "14-node" across both files returns nothing). "Once, demonstrably"
is not merely cautious — it is factually short of what the log shows, and it
undersells the strongest evidence for repeatability the report has.
Restore: *"It has completed at least three full end-to-end runs with all
gates passed (two 14-node, one 15-node). The 15-node run required a mid-run
hotfix and coordinator restart before finishing; the two 14-node runs did
not."* This is a strictly stronger, still-honest claim.

**2. §4's "hole in the guarantee" framing of `_demote_exhausted_fidelity_findings`.** [OVER-CORRECTED in tone, not in substance]
`intent_compiler.py:1230-1263` is real and the report's citation is accurate.
But the surrounding code is more bounded than "hole in the guarantee" implies:
the docstring states outright *"The reviewer can propose the one compiler
repair, but it is not a second admission authority. Deterministic validation,
explicit ambiguity and explicit conflict handling remain blocking."* Reading
the function: it fires only when `fidelity.get("status") == "fail"` (i.e.
deterministic validation already passed), it demotes only `errors` produced by
the *subjective* fidelity reviewer, and it preserves every finding verbatim as
an advisory warning with `original_severity`, `original_repairable`, and
`suggested_change` fields — nothing is deleted or hidden, it is reclassified
and disclosed downstream. This is a narrow, audited, deliberately-scoped
fallback for when the repair budget (default 1, capped 4) is exhausted, not a
silent override. The report's own words — "silenced by running out the repair
clock," "self-serving IntentIR," "no deterministic check noticing" — read as
if the finding vanishes. It does not vanish; it is demoted to a disclosed,
inspectable warning. Restore: *"After budget exhaustion, only the independent
fidelity reviewer's findings — never deterministic structural errors or
blocking ambiguities — may be demoted to advisory warnings; the demotion
preserves the original severity and the reviewer's suggested fix as an
auditable warning rather than discarding it. This is a real narrowing of the
guarantee under budget pressure, and it deserves scrutiny, but it is not a
silent bypass."*

**3. The requirement-stage advisory review is framed only as a "documentation
trap," never credited with its actual engineering rationale.** [OVER-CORRECTED by omission]
`harness/lib/requirement_compiler/semantic.py:230-266` (post `5ade9d9f3`) carries
an in-code comment the report never cites: *"The optional judge must not
become a second provider availability gate."* And earlier, at the top of
`compile_semantic_requirement_ir`: *"Structural compilation may receive one
bounded retry. The independent semantic reviewer is advisory: deterministic
schema/source/registry checks own admission, so subjective review never
starts another compiler generation or blocks Planner handoff."* This is a
legible, defensible trade-off: making a subjective LLM-judged review blocking
would make plan admission hostage to a second model's availability and
introduce an unbounded-retry risk, on top of a review whose job (per the
prompt: "report substantive diagnostics") is inherently softer than the hard,
mechanically-checked constraints (`selection_authority_defects`,
`delivery_manifest_defects`, `SOURCE_CONSTRAINT_POLARITY_OR_CATEGORY_CHANGED`)
that remain blocking. The report should state this rationale and let the
reader judge it, rather than presenting the downgrade only as a fact to be
"conceded."

## Criticisms disproportionate to the evidence — checked and found roughly FAIR

These are cases where R3 alleged over-selling and the revision responded; I
re-checked each against the code and found the *current* report's caveat
proportionate, not overcorrected:

- **`contract_sha256` coverage gap (§7).** [FAIR, arguably understated] Verified:
  `elastic_planner.py:7243-7344` builds the frozen dict from `requirement_ir`,
  `planning_decision`, `plan_ir`, capsule/composition artifacts, and
  `scheduler_input` — there is no `task_graph_contract_ref` entry, and
  `contract_sha256` is computed over that dict alone. In
  `verify_frozen_execution_chain` (`elastic_planner.py:7930-7951`), the
  recomputed `scheduler_input` is built by calling `compile_scheduler_input`
  **on the on-disk `task_graph.contract.json`** (`graph = payloads["task_graph"]`,
  loaded straight from disk at `:7778` with no hash anchor) and comparing the
  *projection*, not the source, against the stored `scheduler_input.json`.
  Fields the projection doesn't lift (`write_scope`, free-text `goal`,
  `human_review*`) can change in `task_graph.contract.json` with **zero**
  errors raised. I checked whether `verify_runtime_projection`
  (`scheduler_input.py:849+`) closes this gap, since the report asks that
  question directly — it does not: that function only byte-verifies that
  `scheduler_input.json` on disk matches the hash recorded in the runtime
  projection's own reference; it never re-derives `scheduler_input` from
  `task_graph.contract.json` and never touches the out-of-projection fields.
  **There is no second mechanism that catches this.** The report's caveat is
  accurate and could be stated even more plainly in the executive summary,
  not softened.

- **§32, "should not be presented as closed."** [FAIR, confirmed by direct
  code read] `graph_node_dispatcher.py:2690-2760` and `evolution_engine.py:255-300`
  both define `_node_requires_deepresearch_quality_gate`, which checks an
  explicit frozen field (`research_quality_gate_required`) first — a real,
  good improvement, since an explicit True/False now wins — but **falls back
  to the same regex/substring inference over capability strings and
  `write_scope`/artifact text** (`DEEPRESEARCH_GATE_ARTIFACT_RE`, matching
  `final_report`, `report_ast`, etc.) whenever that field is unset on the
  frozen node. This is exactly the pattern the report celebrates as fixed in
  §32 — runtime string-matching used to infer gate applicability instead of
  reading a frozen declaration — surviving as the fallback path in two other
  modules. The report's hedge ("present; significance unresolved") is
  earned, not excessive.

## Genuine merit now buried or missing

1. **The Publication Gate self-correction — the single best piece of evidence
   for the "no self-grading" thesis in the whole corpus, and it is absent
   from both documents.** `harness/metadata/pre-scheduler-stabilization-log-20260829.md:638`
   records a run where the old Scheduler-owned closure reported
   `all_nodes_passed=true` while the delivered `research_run_manifest.json`
   itself declared `evidence_gate.status=failed_for_full_requested_scope` and
   `poster.html` showed "Evidence Gate: Not Passed" — a genuine, documented
   case of the closure flag being wrong. The permanent fix, described
   immediately after in the log: the deterministic Publication Gate now
   parses the exact delivered manifest and **must FAIL, and closure must not
   report `completed`, whenever the manifest self-reports a failed/blocked/
   not-passed evidence gate** — with a regression added asserting exactly
   this negative case. This is a textbook "attempt vs. outcome" self-repair:
   the system caught its own bookkeeping lying, and closed the loop with a
   fail-closed, tested invariant rather than hiding the discrepancy. It is
   stronger evidence for §11.4's "acceptance is not completion" claim than
   anything currently cited there, and it directly rebuts the R3 line
   ("the flag the report treats as authoritative evidence has at least one
   documented instance of being wrong") — the report should show that this
   instance was *found and permanently closed*, not just concede the flag can
   be wrong.

2. **Fail-closed is a pervasive, cross-cutting design discipline, but the
   report never names it as one.** It is scattered as isolated facts across
   at least six independent subsystems: `normalize_input` failing closed on
   hash mismatch or empty text (§4); missing `write_scope` treated as
   exclusive-writer (§8); the domain-term relevance gate added to fail closed
   on report-title extraction (§29f); `COLLECTION_MATERIALIZATION_REQUIRES_DIRECTORY`
   rejecting an under-specified plan before freeze (stabilization log,
   "cardinality" entry); a missing publication snapshot raising
   `invalid_input` rather than proceeding; and the Publication Gate fix above.
   No section assembles these into the stated architectural virtue they
   collectively are. A reader who only skims §7's caveats and §32's warning
   would not come away knowing that "fail closed" is close to a house rule
   here, independently reinvented at six different layers by (apparently)
   different fixes over time.

3. **The requirement-review's advisory design has an availability rationale**
   (see Over-correction #3 above) — currently presented as pure regression.

4. **The double-admission check in intent compilation** (`capture()` /
   `requirement_handoff()`, §4) and **the constraint deep-copy guard** (§5)
   are both already credited fairly and given real weight — no complaint
   here; flagging them only to confirm they were checked and are correctly
   represented, not underclaimed or overclaimed.

## §35b misclassifications

- **"Filesystem work queues" classified as flatly table-stakes, with the gloss
  "generally considered inferior to a broker."** [MISCLASSIFIED — context
  matters] In a conventional server-side distributed system this is a fair
  knock. But this project's own stated context is local-first, polyglot
  (Python control plane, Bash, TypeScript/Bun services), zero-infra-dependency
  execution — the report's own §9 says "any language that can read and write
  files can host an operator," which is the entire point of choosing a
  mailbox over a broker in this setting: no message broker to install, version,
  or keep alive on a developer's laptop, and cross-language compatibility for
  free. The choice is well-matched to the stated constraints, not merely an
  inferior default reached for out of habit. The table should either add a
  qualifying note ("inferior to a broker in server contexts; a reasonable fit
  for a local-first, polyglot, zero-infra target") or move this row toward the
  "well-chosen given constraints" side, as it partially does for write-scope
  conflict detection but not here.

- **"Write-scope conflict detection" classified as flatly table-stakes** ("Build
  systems have done this for years") **without crediting the fail-safe-exclusive
  default**, even though §8 of the same report calls that default "the
  fail-safe direction" a few pages earlier. R3's own table (which this report
  is responding to) rates this row "mildly above table stakes" for exactly
  this reason. The current §35b table is more dismissive of this item than
  even the hostile skeptic was — that is the clearest single instance of the
  revision over-rotating past its source critique.

- **"Declaring effects in a manifest" is correctly split out (risk axis called
  notable separately) — this one is fair and does not need adjustment.**

## Tone problems — sentences to soften, with neutral rewrites

1. VARIANT-3 §4, "Budget — and a hole in the guarantee." →
   *"Budget, and a bounded exception to it."* (see Over-correction #2 for the
   full paragraph rewrite).

2. VARIANT-3 §4, "This matters. The one independent-model check designed to
   catch a self-serving IntentIR can be silenced by running out the repair
   clock, with no deterministic check noticing." →
   *"This narrows the guarantee under budget pressure: once repairs are
   exhausted, the independent fidelity reviewer's objections become an
   advisory, disclosed warning rather than a blocking failure. Deterministic
   structural checks and explicit ambiguity/conflict handling are unaffected
   and remain blocking."* ("Silenced," "self-serving," and "with no
   deterministic check noticing" all imply concealment; the mechanism
   discloses everything it demotes.)

3. VARIANT-3 §5, "Budget — and a documentation trap." — the "documentation
   trap" framing is fine as a fact but should carry the availability rationale
   from the code comment alongside it (see Over-correction #3), not stand
   alone as if the downgrade were unexplained.

4. VARIANT-1 §4, "The code mostly honours it — with real exceptions... The
   principle is genuine; the enforcement has gaps." — This is fine and well
   calibrated; no change needed. It is a good model for how the harsher
   passages elsewhere should read.

5. No place in either document hedges so heavily it says nothing — the report
   does not have a vacuous-caveat problem. Every caveat found (§7, §32, §35b,
   the exec-summary finding 2) makes a specific, checkable claim. That
   discipline should be preserved while the *tone* of a few sentences is
   softened per above.

## The positive case the report should make but doesn't

A reader who only sees the executive summary (finding 2 opens on
"constrained — but not fully prevented," finding 5 undercounts to "once,
demonstrably") and the heavily-caveated §7/§32 comes away without a crisp,
affirmative sentence to repeat to a colleague. The evidence in this repo
supports one, and it is currently scattered rather than stated:

> *This is a system that keeps finding its own bookkeeping lies and closing
> the loop with a permanent, tested, fail-closed fix instead of a quiet patch
> — the Publication Gate now refuses to report a run as complete when its own
> delivered manifest says otherwise, the scheduler's post-hoc semantic
> inference bug produced both a positive and a negative regression test, and
> the pre-release suite's 34 known failures are itemized by cause rather than
> hidden. Whether every control (the requirement review, the fidelity
> reviewer) is blocking or advisory is a real, checkable design decision this
> report can point to line and reasoning for — not a uniformly-enforced
> absolute, but not an accident either.*

That sentence is defensible, it is not flattery, and it gives someone
presenting this work a way to open the conversation without sounding
apologetic. The report should say some version of it, ideally near the top.

## Section-by-section direction-of-error table

| Section | Claim under audit | Direction of error |
|---|---|---|
| Exec summary, finding 2 | "constrained — but not fully prevented" | FAIR in substance; harsh in the body text it summarizes (§4) |
| §4 (intent fidelity demotion) | "a hole in the guarantee" | OVER-CORRECTED in tone; substance is accurate and should stay |
| §5 (requirement review advisory) | framed as documentation-currency issue | OVER-CORRECTED by omission — missing the availability rationale in the code comment |
| §7 (the freeze / hash coverage) | "what the hash does NOT cover" caveat | FAIR, could be stated more prominently, not less |
| §8 (write-scope fail-safe) | credited correctly in prose | FAIR — but not carried through consistently into §35b (see misclassification) |
| §11.4 (acceptance vs completion) | correct but thin | UNDERCLAIMED — omits the Publication Gate self-correction, the strongest evidence available |
| §32 (the deadlock) | "should not be presented as closed" | FAIR, confirmed by direct code read of the two named files |
| §33 (status) | "It works, once, demonstrably" (echoed in VARIANT-1 §7) | OVER-CORRECTED — undercounts three documented full passes to one |
| §35b (table stakes) | filesystem queues, write-scope detection rated flatly ordinary | OVER-CORRECTED — more dismissive than even the hostile skeptic's own table |
| §38b (counter-evidence) | eval/exec/shell=True counts, lib/tools duplication, no lockfile | FAIR — correctly scoped as "not investigated," appropriately humble |
| VARIANT-1 §4 | "the code mostly honours it — with real exceptions" | FAIR — best-calibrated sentence in either document |
| VARIANT-1 §7 | "happy path completes when someone is watching" | OVER-CORRECTED — true of the 15-node run, silently generalized past two clean 14-node runs |

## Files and lines cited

- `harness/lib/intent_compiler.py:1230-1263` — `_demote_exhausted_fidelity_findings`
- `harness/lib/elastic_planner.py:7243-7344, 7748-7951` — frozen contract assembly and `verify_frozen_execution_chain`
- `harness/lib/scheduler_input.py:849+` — `verify_runtime_projection`
- `harness/lib/apo_plan_compiler.py:569-646` — planner-declared capsule identity trust
- `harness/lib/requirement_compiler/semantic.py:130-266` — advisory review rationale, post-`5ade9d9f3`
- `harness/lib/graph_node_dispatcher.py:2670-2770`, `harness/lib/evolution_engine.py:240-300` — surviving regex-fallback gate inference
- `harness/metadata/pre-scheduler-stabilization-log-20260829.md:638, 781, 795` — the two uncredited 14-node full passes and the Publication Gate self-correction narrative
