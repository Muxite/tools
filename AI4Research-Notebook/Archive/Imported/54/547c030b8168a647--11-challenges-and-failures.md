# AI4Research / OpenSolar — Challenges, Limitations, and Failure History

Repo: `/home/muk/work/AI4Research`, branch `openJiuwen-Solar`, HEAD `b0bf165f9`.
Scope: synthesis of everything that went wrong, is hard, or remains open across
the whole system (not a single subsystem). All timestamps below are the
project's internal fictional clock (2026), not real-world dates.

---

## Summary (5 bullets)

- The project keeps an unusually rigorous **append-only incident log**
  (`harness/metadata/pre-scheduler-stabilization-log-20260829.md`, 863 lines,
  ~46 numbered issues plus ~60 unnumbered "Web retry" narrative entries
  spanning 2026-08-29 → 2026-09-03). Read end-to-end, the timeline shows the
  pipeline going from *cannot reach the Scheduler at all* to a **full
  15/15-node E2E PASS** (`sprint-20260903-030314…`, confirmed again at
  `sprint-20260903-072109…`, `Closure=closed, all_nodes_passed=true`) by the
  end of the log. A snapshot mid-way through this arc
  (`migration-handoff-20260831.md`) is a **temporarily true but since-resolved**
  top blocker (Planner provider-schema rejection on `cpu_cores_min`) — it must
  not be reported as the current state.
- The **hardest unresolved-at-authoring-time class of bug** is not "the LLM is
  unreliable" but **interface/contract drift between layers that each pass
  their own local validation** — PlanIR vs. canonical schema mismatches,
  registry `node_id` vs. `implementation_node_id` dual identity, frozen
  SchedulerInput fields silently dropped by a downstream allowlist, artifact
  *type* identity conflated with artifact *instance* identity. These recur
  under different names roughly a dozen times in the log.
- A genuinely **open, structurally hard problem** is the Discovery
  semantic-scope defect: distinguishing "topical corpus coverage" (what a
  paper must be about) from "workflow/process/deliverable" requirements (what
  the *report* must do) inside natural-language requirement text, without
  hard-coding vocabulary. The docs explicitly forbid two easy-but-wrong fixes:
  adding stopwords to hide symptoms, and blaming "unstable LLM intelligence."
- Older architecture docs (`architect-investigation-001/002/003`,
  `DISPATCH-PROTOCOL.md`, `BUG5-ROOT-CAUSE.md`) document a distinct, earlier
  era (2026-04 to 2026-05) of **coordinator/dispatch concurrency bugs**:
  single-sprint scanners that starve concurrent sprints, tmux send-keys races
  that silently overwrite one dispatch with another, and a stale bash process
  running pre-fix code for 28 hours because bash loads its script into memory
  once at start. These are largely presented as fixed at the time, but the
  pattern (state split across multiple weakly-synchronized stores) recurs
  architecturally all the way into the 2026-09 Scheduler-projection bugs.
- The project is **explicit and quantified about its own limitations**: README
  "已知限制" lists 7 named limitations (single-machine only, two divergent
  runtime lines, version-metadata inconsistency across 3 sources, Desktop not
  production-signed, etc.), and the Phase 22 test report's most recent
  roll-up (2026-08-07) is `PASS=26, PASS_WITH_KNOWN_LIMITATIONS=68, FAIL=14,
  ENVIRONMENT_BLOCKED=2, NOT_AVAILABLE=22, NOT_TESTED=10` out of 142 Level-2
  features — i.e. roughly half the surface area is not a clean pass.

---

## Master issue inventory (pre-scheduler stabilization log)

All from `harness/metadata/pre-scheduler-stabilization-log-20260829.md`. The
log is append-only; status below reflects the **latest** entry touching each
issue, not the entry where it first appears. All 46 numbered rows are
[RESOLVED] within the log itself (each row states a fix + verification); the
important reading is the *unnumbered* narrative entries after row 46, which
contain the currently-relevant state. I give the numbered rows compactly and
the narrative entries in more depth where they matter for "what is hard."

### Numbered rows 1–46 (all [RESOLVED] as recorded)

| # | Symptom (compressed) | Root cause (compressed) | Status |
|---|---|---|---|
| 1 | `/api/sprints` polling timeouts | rebuilt sprint index per-request | RESOLVED (single-flight cache) |
| 2 | Intent artifacts written outside selected runtime | defaulted to `Path.home()`, ignored `HARNESS_DIR` | RESOLVED |
| 3 | `intake_cli_failed` after accepted Requirement | consumer repeated the same stale `Path.home()` default | RESOLVED |
| 4 | Planner dropped requirement R5 during repair | discovery-preservation helper unconditionally re-added owned reqs | RESOLVED |
| 5 | Capsule couldn't truthfully own protocol requirement | discovery ABI promises only a shortlist, not resolution fields | RESOLVED (moved ownership downstream) |
| 6 | Coordinator kept reverting `active`→`drafting` | legacy PRD gate ran before typed Scheduler dispatch could | RESOLVED |
| 7 | Valid bounded repair (add ownership) rejected | repair-preservation check forbade *any* added ownership | RESOLVED |
| 8 | Accepted Planner result not observed by Coordinator | watcher didn't cover nested typed adapter result path | RESOLVED |
| 9 | Valid "resolve-or-report-unresolved" chains rejected | reviewer treated optional resolution as mandatory | RESOLVED |
| 10 | Scheduler completed a node then went silent | Coordinator didn't watch typed runtime projection file | RESOLVED (first genuine Scheduler-stage defect, "report only" per original scope) |
| 11 | Needed new Coordinator cycle after every node | wake set omitted runtime state file | RESOLVED |
| 12 | Command capability/attribution leaked out of runtime | duplicated PATH/home resolution in Scheduler process env | RESOLVED |
| 13 | GUI showed missing-DAG warnings despite Scheduler progress | terminal reconciliation read legacy locations | RESOLVED |
| 14 | Launcher bound wrong port (8766 vs locked 8767) | port range/mode not propagated into tmux child | RESOLVED |
| 15 | State revision regressed (15→14) under concurrent writers | no lock/optimistic-revision check on read-modify-write | RESOLVED (per-ledger lock + revision check) |
| 16 | — | verification-only row (fresh E2E proved Scheduler could advance) | N/A |
| 17 | Discovery returned empty shortlist despite 11 provider hits | entire Planner goal (incl. workflow text) used as per-paper coverage authority | RESOLVED |
| 18 | `sparsification` treated as missing despite synonyms present | exact lexical matching, no vocabulary normalization | RESOLVED |
| 19 | Fidelity reviewer oscillated on discovery ownership | reviewer misread scope-context as duplicate-ownership | RESOLVED |
| 20 | Accepted handoff not admitted after Coordinator restart | correct startup admission fence (not a bug) | N/A — by design |
| 21 | Discovery worker escaped selected runtime via parent `tools/` | resolver trusted any parent `.git` as authorization | RESOLVED (opt-in env var required) |
| 22 | Shortlist emptied by generic leftover words (`type`, `answer`) | topical filter too permissive | RESOLVED |
| 23 | Recovery alias lookup missed prefixed labels | required exact whole-label match | RESOLVED |
| 24 | Discovery worker stuck in stale 15-min cooldown | closeout recovery rewrote timestamp of an already-finished op | RESOLVED |
| 25 | Coverage-recovery query still missed a specialist paper | only queried OpenAlex, not arXiv | RESOLVED |
| 26 | Sprint stuck in `drafting` despite accepted Planner output | Coordinator "forgot" admission once live lease released | RESOLVED (persistent admission cache) |
| 27 | Shortlist emptied by grammatical residue (`oriented`,`supported`) | deliverable-vocabulary filter left partial matches | RESOLVED |
| 28 | `extract_methods` used fixture data instead of real papers | bridge ignored Scheduler `artifact_routes`, fixture fallback | RESOLVED |
| 29 | Registered capability rejected as "not allowlisted" | adapter kept a stale 4-node allowlist | RESOLVED |
| 30 | Discovery queried for generic phrase, 0 papers retained | composition expansion replaced named objective with generic text | RESOLVED |
| 31 | Coordinator restarts revived unrelated historical sprint | watchdog trusted stale pane-lease file | RESOLVED (durable admission lease) |
| 32 | Final report was fixture content, not KV-cache landscape | report planning ignored frozen artifact routes | RESOLVED |
| 33 | Report title malformed (`for the project "..."`) | title-extraction regex too narrow | RESOLVED |
| 34 | **Unattended run failed at Planner composition review** | reviewer found discovery protocol fields not carried to report | [RESOLVED by later rows] — recorded as designed no-intervention failure |
| 35 | Study-protocol fields had no executable artifact route | discovery didn't materialize a `study_protocol` payload | RESOLVED |
| 36 | Legacy report-plan fallback produced untraceable section | represented protocol as unresolved with empty trace | RESOLVED |
| 37 | Unrelated pre-existing regressions noted, not fixed | out of scope for this defect | [OPEN, out-of-scope, explicitly logged not silently dropped] |
| 38 | Bridge dropped `study_protocol` despite native update | bridge adapters not updated in step with native operators | RESOLVED |
| 39 | Report-plan bridge misreported its own schema identity | legacy bridge reused final-report adapter identity | [OPEN — "recorded only," strict IO-contract parity unresolved] |
| 40 | Report used generic heading, not supplied title | title extractor missed `report "<title>"` form | [OPEN — "recorded only," non-blocking] |
| 41 | Title fidelity still wrong with coordinated phrasing | strict/loose title regexes didn't cover new Planner phrasing | [OPEN at row 41, RESOLVED at row 42] |
| 42 | (fix for 41) | extended quoted-title grammar to coordinated forms | RESOLVED |
| 43 | Ingestion failed: "no candidates" despite 3 relevant papers found | workflow-instruction text treated as mandatory paper-topic coverage | [RESOLVED later, in the shared-contract/semantic work] |
| 44 | Cockpit rebuild flipped 8 stale sessions to `interrupted` | official kill-path side effect, by design | N/A — documented, not a defect |
| 45 | Clean source transfer missing 118 schema-tree assets | runtime baseline had static deps never tracked at canonical paths | RESOLVED (migration closure inventory) |
| 46 | Migration fixture rejected for missing new required fields | historical fixture predated current schema | RESOLVED |

### Narrative entries after row 46 (the substantive "how hard is this" material)

These are the entries that matter most for "Challenges." Key ones, in
chronological order (all citations `harness/metadata/pre-scheduler-stabilization-log-20260829.md`):

1. **Semantic-contract repair, 2026-08-30** (~L59-66): replaced deterministic
   Requirement compilation (which flattened constraint expressions) with
   schema-bound LLM generation + independent fidelity review; added a
   source-linked structured retrieval contract so Discovery executes a
   contract object instead of re-inferring intent from prose.
2. **Unattended semantic-contract E2E FAIL, 2026-08-31T03:53Z** (~L68-71):
   `intake_cli_failed`. Root cause traced to a Requirement-stage model call —
   `checkable` property was `const`-only with no `type` key, rejected by the
   provider at the JSON-Schema-submission boundary (HTTP 400
   `invalid_json_schema`). **This is a provider-schema-compatibility defect,
   not semantic model failure** — the log is explicit: "Do not label this as
   demonstrated semantic rejection." RESOLVED same day (~L76-79): added
   `type: boolean` while keeping `const: true`.
3. **`minimum_candidates=1` misread as a user requirement, 2026-08-31T04:24Z**
   (~L82): the compiler's *operational default* (nonempty-handoff floor) was
   indistinguishable, in the reviewer's eyes, from a user-authored quantity
   requirement. RESOLVED via a **single shared, versioned semantic-contract
   schema** consumed identically by compiler and reviewer
   (`schemas/compiler/requirement-semantic-contract.v1→v3.json`), eliminating
   the class of "compiler and reviewer disagree because they were prompted
   with differently-worded policy text."
4. **Planner DAG schema rejected: `Missing 'cpu_cores_min'` in `required`,
   2026-08-31 "Final no-intervention E2E"** (~L179): resource-contract fields
   (`cpu_cores_min`, `memory_mb_min`, `gpu_required`) were optional in the
   canonical schema but the OpenAI-compatible strict-schema submission
   required all properties be listed as `required`. `codex_compatible_schema`
   did not project that optionality. **This is exactly the blocker described
   in `migration-handoff-20260831.md` (see next section) — and it is
   RESOLVED** by the subsequent multi-provider structured-output overhaul
   (`structured-output-compatibility-20260831.md`): optional-and-non-nullable
   fields get a synthesized nullable wrapper on submission and nulls are
   restored to "unset" on the way back, while explicit `0`/`false` are
   preserved.
5. **Multi-provider structured-output rebuild, 2026-08-31 "当前工作树"**
   (~L192 onward, Chinese): a single provider-schema projection layer now
   sits in front of Intent/Requirement/Planner/direct-answer/fixed-research
   calls across 11 registry models across 6 provider families (OpenAI,
   Anthropic, Zhipu, DeepSeek, Gemini, local). Explicit non-goals stated:
   "不增加自动模型切换或无界重试，不放宽来源门禁" (no automatic model
   switching or unbounded retry; no relaxed source gate). Final regression:
   284 passed, 0 failed.
6. **Capability-contract audit, C1–C5, 2026-08-31**: five distinct
   architectural gaps in how capability declarations reach Planner/Scheduler
   — inconsistent availability filtering, incomplete semantic contract
   projection, no planning feedback loop on semantic-fit rejection, mutable
   dispatch authority (definitions resolved live instead of frozen), and
   resource-contract loss before `SchedulerInput`. All five implemented and
   verified; final regression 100+ tests, still explicitly caveated:
   "static availability is a declaration gate, not proof every capability
   works... unknown positive context/remote capacity blocks rather than
   inventing values."
7. **`ENVIRONMENT_BLOCKED` — provider capacity, 2026-08-31T06:31Z**: model
   subprocess returned "Selected model is at capacity." A genuine external
   dependency failure, explicitly distinguished in the log from a schema or
   semantic defect. Not a product bug.
8. **Unknown-check-ID and semantic overconstraint, 2026-08-31T06:36Z**: an
   invented `check.claim_evidence_resolved.v1` suffix consumed the single
   repair budget before the real semantic issue (over-conjunctive corpus
   coverage across 5 method families) could be repaired. RESOLVED via
   "immutable contract v2" instantiating registry/check identity as actual
   enums in the provider schema (not just prompt prose) — this is the same
   "make the machine-checkable contract structural, not textual" pattern
   recurring across the whole log.
9. **`define_study_protocol` grounding gap, 2026-08-31T05:24Z**: composition
   catalog admitted exactly one candidate capsule
   (`cap.requirement-compiler-audit`) for a node that needed
   protocol-authoring semantics the audit capsule doesn't have. The log is
   explicit this is "a plan-to-capability grounding gap for the generated
   node, not... an observed provider failure, or a Scheduler defect... It
   does not prove that every possible alternative plan is impossible." This
   became capability-contract gap **C3** above (bounded planning feedback),
   fixed in the C1–C5 work.
10. **Artifact producer-identity ambiguity (`ARTIFACT_PRODUCER_DUPLICATE`),
    2026-09-01** (~L258 area, table-based-artifact section): PlanIR
    `artifact_type` was conflated with global instance identity, so a
    legitimate `ingestion→analysis` same-type transition was rejected.
    RESOLVED by rebinding producer identity to `(producer node, artifact_type)`
    pairs with explicit ambiguity failure ("`ARTIFACT_PRODUCER_AMBIGUOUS`...
    禁止猜测" — forbidding guessing) rather than best-effort resolution.
11. **`SCHEDULER_RUNTIME_PROJECTION_TAMPERED`**: SchedulerInput froze
    `retrieval_contract` and `execution_authority` as immutable fields, but
    the Graph Scheduler's *separate* static-field allowlist for its own
    state-ledger save omitted them — so saving mutable state silently
    stripped frozen fields, and the next Scheduler tick's strict hash check
    correctly rejected its own prior write. Log: "This is a static field
    contract drift between three interfaces... not Planner output error,
    also should not be fixed by relaxing the tamper gate." RESOLVED by adding
    the two fields to the allowlist, not weakening the check.
12. **`unknown_node` registry rejection** despite the capability actually
    being registered: Scheduler used `scheduled_node_id` (frozen, per-graph)
    while two of three operator-family registries used only `node_id`
    (reusable implementation identity), so composition-expanded nodes had no
    match. RESOLVED by making all three families route on the frozen
    `implementation_node_id`.
13. **Final E2E success achieved, 2026-09-03** (`sprint-20260903-030314…`,
    later reconfirmed `sprint-20260903-072109…`): 14/15-node and 15/15-node
    full pipeline runs, `Closure=closed`, `all_nodes_passed=true`,
    `all_required_gates_passed=true`, real arXiv/local-PDF evidence, byte-
    verified output files, independent evaluator `PASS`. This is the
    high-water mark of the log and directly precedes the `ai4research-main`
    release-prep entry at the very end of the file.
14. **Pre-release aggregate regression, 2026-09-03 (last entry)**: 606
    passed / 34 failed / 8 skipped across 22 affected test files. The log
    explicitly refuses to hide this: "失败不能被隐藏或记为全绿" (failures
    cannot be hidden or recorded as all-green) — the 34 failures are
    triaged as known regression debt (stale fixtures expecting removed
    legacy behavior, preflight-rejected old fixtures, registry drift), not
    silently fixed or excluded from the count.

---

## Current top blockers

### If read as of `migration-handoff-20260831.md` (a snapshot mid-arc):

**[RESOLVED — but described here because the task explicitly asks about it]**
The last E2E at that snapshot failed before Scheduler:

> "Planner 决策为 generate，DAG 生成调用被模型接口拒绝。最终状态
> failed/planning_failed；没有 SchedulerInput、冻结执行包、Scheduler、worker
> 或报告。" (`harness/metadata/migration-handoff-20260831.md:13`)

Exact mechanism (`migration-handoff-20260831.md:17-26`):

- Schema: `harness/schemas/planning/plan-ir.semantic.structured.v2.schema.json`,
  specifically the model-facing generation schema built by
  `harness/lib/intent_compiler.py::codex_compatible_schema`.
- Field: `$defs/operator_requirements/properties` contained `cpu_cores_min`,
  `memory_mb_min`, `gpu_required` as optional properties, but the `required`
  array did not list them.
- Model/provider behavior: the OpenAI-compatible provider's Structured
  Outputs mode requires **every** object property to appear in `required`
  (optionality expressed instead via nullable typing). The provider rejected
  the request outright with HTTP 400 `invalid_json_schema`, "Missing
  'cpu_cores_min'" — **before any model generation occurred**. No PlanIR was
  produced; this is a submission-time schema-compatibility rejection, not a
  semantic judgment by the model.
- Explicit framing in the doc: "这是模型调用合同兼容性缺陷，不是 LLM 智力
  退化、旧 Requirement 输出、CPU 资源不足或服务容量错误" (this is a
  model-call contract compatibility defect, not LLM intelligence degradation,
  stale Requirement output, CPU resource scarcity, or service capacity
  error) — `migration-handoff-20260831.md:26`.

**Resolution** (confirmed in the primary log, not in the handoff doc, since
the handoff doc predates the fix): the multi-provider structured-output
rebuild (`structured-output-compatibility-20260831.md`) introduced a
submission-time schema projector that marks optional-and-non-nullable fields
as nullable in the copy sent to the provider, and restores `null`→"unset" on
the way back, while explicitly preserving real `0`/`false`/`null` values
(`structured-output-compatibility-20260831.md:23-32`). This class of defect
does not recur in the log after that point through the eventual 15/15 E2E
pass on 2026-09-03.

### The genuinely still-open items at end of log (2026-09-03, pre-`ai4research-main` release)

1. **Report-plan bridge schema-identity mismatch** (row 39): the bridge
   claims artifact identity `scientific_report.v1` for what the frozen route
   declares `scientific_report_plan.v1`. "Strict IO-contract parity remains
   unresolved" — masked by tolerant payload loading, not fixed.
2. **CLI failure-summary misattribution**: repeatedly observed (at least 3
   separate entries) that the CLI's generic upstream error message blames
   "Intent Compiler did not produce an accepted IntentIR" even when
   `intent_acceptance.json` says accepted and the real failure is a
   downstream Requirement-review subprocess error. Logged each time as "known
   remaining issue, not silently counted as fixed."
3. **Composition/materialization contract gap** (2026-09-03, "多论文产物被
   冻结为单文件写入范围"): composition/capsule validation proves artifact
   *type* chains compose, but never proves *cardinality* (`many` vs single
   file) or *materialization kind* is consistent with the selected physical
   worker's actual write behavior. A `many`-output capsule got silently
   compiled into a single-file `write_scope`, causing a hard runtime
   `scope_violation`. Diagnosed, not yet fixed at time of last entry:
   "本条只完成诊断与方案记录，未修改Harness" (this entry only completed
   diagnosis and a plan record; Harness was not modified).
4. **Session-timeline narrative projection hides history under high-frequency
   polling** (2026-09-03): 716 raw session-scoped events collapse to 2
   visible timeline entries because `typed_scheduler_tick`/`watchdog_restart`
   polling entries drown out milestone events; a general fix is proposed
   (semantic-category retention + tick compression + count caps) but
   explicitly deferred: "用户随后明确要求不做普适source修复" (the user then
   explicitly requested not doing the general source fix, only cleaning up
   this run's projection).
5. **Pre-existing regression debt**: 34 failing tests carried forward into
   the `ai4research-main` release candidate, explicitly not hidden (see
   inventory item 14 above).

---

## Thematic analysis

### (a) Getting structured/schema-conformant output from LLMs reliably

The single largest recurring theme by volume. Roughly a third of all
numbered/narrative entries are some variant of "the provider or the model
rejected/misused a JSON Schema." Concrete failure modes observed: `const`-only
properties without a `type` key (unresolved-narrative entry 2), optional
properties absent from `required` under OpenAI's strict-schema mode
(top blocker, above), recursive-schema incompatibility with Gemini's native
mode (handled by defaulting Gemini to JSON MIME + local validation instead of
native schema — `structured-output-compatibility-20260831.md:53-56`), and
provider capacity/transient failures indistinguishable from schema errors
until diagnosed (`ENVIRONMENT_BLOCKED` entry). The project's answer is not
"trust the model more" but **build one shared projection/validation layer**
(`harness/lib/structured_output.py`, `structured_model.py`) so every stage
submits a provider-safe copy of the *same* authoritative schema and validates
the response against the original, never a relaxed one.

### (b) Semantic vs. structural validation boundaries

Recurs as: workflow/deliverable language leaking into topical-coverage
filters (rows 17, 22, 23, 27, entry 43); numeric operational defaults
(`minimum_candidates=1`) being misread as user requirements (entry 3);
Reviewer subjectively enumerating new objections across bounded-repair rounds
(late narrative entry "Intent 最终 LLM Reviewer 不再成为第二准入权威" — the
project eventually converts *exhausted-repair, deterministically-valid*
candidates to `pass_with_warnings` rather than let an LLM reviewer be a
second unbounded admission authority). The general lesson stated explicitly
in `NEW-MACHINE-START-HERE.md:120-123`: don't attribute this class of bug to
"unstable LLM intelligence" and don't suppress it with stopword lists —
distinguish *what the schema/DSL can express* from *what the model chose to
express*, and fix the former.

### (c) Contract/schema drift and identity across versions

Requirement semantic contract went v1→v2→v3 (semantic-retrieval-contract.md);
PlanIR authoring schema vs. canonical schema diverged on `workspace_reads`
then `route` (2026-09-01 entries) — two schemas meant to describe "the same"
object drifted independently. SchedulerInput vs. Graph Scheduler static-field
allowlist drift (item 11 above). Two independent registries keyed identity
differently (`node_id` vs `implementation_node_id`, item 12). This is
effectively **N-way schema consistency without a single source of truth**,
and the fixes are uniformly "add a regression asserting the two definitions
are identical," not "trust one and assume the other follows."

### (d) Distinguishing a submitted task from an executed one

Row 32 (fixture report content shipped as if real), the `paper_analyze`
legacy-bridge entry ("legacy paper analyzer 伪成功并丢失冻结论文输入" —
bridge reported outer `ok=true, exit 0` while inner evidence was
`status=failed`), and the run-manifest entry near the end of the log
("Publication Run Manifest 绑定 Scheduler 状态快照" — a report claimed
`Evidence Gate`/`Closure-status` fields that the model had to *invent*
because the true Scheduler ledger state wasn't available to it at
publication time) are all instances of this theme: a node/process can exit 0
and *look* complete while the actual work product is fixture data, a
different artifact, or an unrecorded state. The recurring fix pattern is
**evidence-first completion**: bind completion claims to the actual
ledger/evidence bytes, never to process exit codes or textual success
markers alone.

### (e) Evidence integrity and anti-fabrication

Explicit anti-patterns rejected throughout: "不能靠补 stopwords 来隐藏问题"
(don't hide the problem behind stopwords), "不通过关闭本地校验或自动换
provider 来继续" (don't continue by turning off local validation or
auto-switching providers), "不得填充 CPU、内存或 GPU 默认要求"（don't
backfill resource defaults), "不预先保证它是最后一个问题" (don't promise
this is the last issue), "失败不能被隐藏或记为全绿" (failures cannot be
hidden or recorded as all-green — final release entry). AGENTS.md codifies
this as policy: "Do not weaken a success condition or delete a known
limitation merely to turn a result green" (`AGENTS.md:71-72`).

### (f) Concurrency, leases, write-scope conflicts

Two distinct eras: (1) 2026-04/05 coordinator-level concurrency bugs
(`architect-investigation-001/002`, `DISPATCH-PROTOCOL.md`) — single-sprint
scanner starving concurrent sprints, tmux send-keys races silently
overwriting one dispatch with another, no per-pane occupancy tracking; (2)
2026-08/09 Scheduler-level concurrency — state-revision regression under
concurrent writers (row 15, fixed with optimistic revision + per-ledger
lock), and a diagnostic concurrent Scheduler tick correctly rejected by
compare-and-swap ("stale scheduler state revision: expected 56, found 57").
The project's answer converged on the same primitive both times: **durable,
versioned, single-writer-enforced state with explicit conflict rejection**,
never silent overwrite.

### (g) Cross-platform portability (Windows/WSL/macOS)

`portability-audit-20260830.md` is a full audit: Linux Node/npm absent from
default WSL PATH (Windows npm silently resolves instead — flagged as a
misconfiguration trap, not something to "fix" by copying node_modules); 32
personal-path and 28 old-backend-address literal matches, triaged (most are
non-defects — test fixtures, Docker's declared layout — but several are real,
e.g. an Obsidian-vault default pointing at a former user's vault); Windows
directory-handle `fsync` doesn't support the POSIX pattern the atomic-write
journal assumed (fixed per-platform, not by disabling durability — narrative
entry "Windows publication durability 兼容问题"); `bwrap` sandbox absent on
WSL PATH, silently falls back to a bundled fallback (explicitly flagged as
"a warning, not a root cause" the one time it co-occurred with a real
failure, so as not to misdiagnose). README's known-limitations item 1
("单机优先" — single-machine first) generalizes this: lease/mailbox/event
mirror/tmux/SQLite all assume a shared local filesystem.

### (h) Quota, cost, and provider dependence

`ENVIRONMENT_BLOCKED` model-capacity failure (narrative entry 7); Semantic
Scholar HTTP 429 rate-limiting recurring across multiple live runs, handled
by exponential backoff (60/120/240s) and — critically — a "local-seed
fallback" that must be **structurally distinguished** from a genuine empty
result (the `inconclusive`-vs-`failed` provider-status entry). Registry
entries for 11 models across 6 providers each need separately-verified
schema/transport support; the doc is explicit that "registry 名称不证明对应
账号/接口实际提供该模型" (a registry name does not prove the corresponding
account/interface actually serves that model) — `structured-output-compatibility-20260831.md:46`.

### (i) Migration and runtime/source divergence

`migration-handoff-20260830.md` and `-20260831.md` document a real historical
gap: 118 schema-tree assets existed only in the authoritative runtime and
were never tracked at canonical Git paths (row 45). The fix — a 165→170→173
file portable SHA-256 inventory plus an offline Git-blob audit — is a
structural answer to "how do you know the runtime and the repo agree,"
applicable to essentially any long-lived local-first system with a live
deployment that outpaces its own commits.

### (j) Test-vs-product failure attribution

Consistently disciplined: row 37 records unrelated pre-existing test
failures as "outside the study-protocol handoff... existed in untouched
paths," not silently fixed or hidden; the final release entry keeps 34
failing tests as recorded debt rather than excluding them from the count;
multiple entries distinguish "Windows temp-directory PermissionError in the
test runner" from an actual product failure and say so explicitly each time
("这些失败均保留为已知回归债务，未通过放宽产品门禁...来修改" — these
failures remain recorded as known regression debt, not resolved by relaxing
product gates).

---

## Architectural challenges (architect-investigation-*.md)

### #001 — Coordinator dispatch starvation (`architect-investigation-001.md`)

`get_latest_sprint_file()` is a **single-sprint scanner**: it returns only
the one file with the largest mtime. When multiple sprints flip to `active`
within the same coordinator poll interval, only the most-recently-touched one
is ever dispatched — the others are permanently invisible because any later
sprint's newer mtime keeps winning the "latest" comparison forever
(`architect-investigation-001.md:6, 43, 72`). Root design mismatch: the
per-sprint `check_state_changed()` function is correctly scoped per-sprint,
but it is **never called** for sprints the single-file scanner didn't select
— "两者拼起来就是: 同一时刻最多只能感知 1 个 sprint 状态变更" (put
together, at most 1 sprint's state change can be perceived at a time,
`:82`). Fix proposed: for-loop over all sprint status files each poll, or a
periodic orphan-sweep fallback. Secondary noise found in the same
investigation: corrupted `status.json` files missing an `id` field flooding
logs, and an arithmetic bug in a notification script from `grep -c`'s
exit-1-with-output-"0"\n behavior.

### #002 — Dispatch overlap / tmux send-keys race (`architect-investigation-002-dispatch-overlap.md`)

`dispatch_to_pane` has **no per-pane busy mutex** — it only checks for an
idle shell prompt. When sprint A's dispatch text is still sitting in the
input box (Enter not yet consumed / verification not yet passed) and sprint
B's dispatch fires, B's pre-unlock `Ctrl-U` **clears A's un-submitted text**
before A ever reaches the builder pane — "send-keys 在视觉上是'追加'语义,
C-u 让它变'覆盖'语义" (send-keys is visually "append" semantics, C-u turns
it into "overwrite" semantics, `:45`). A secondary failure mode: the
verification step's dual-keyword match can be fooled by a *previous* task's
residual pane output. Three concrete design holes identified: no per-pane
occupancy record, destructive pre-unlock, and spoofable verification. Fix:
per-pane assignment tracking with a 30-minute non-preemption window,
persisted to `.pane-assignments` (this file is later referenced in row 31 of
the stabilization log as itself becoming a *source* of stale-authorization
bugs — the fix for #002 needed a further fix once the coordinator's admission
semantics changed).

### #003 — Multi-builder parallelism feasibility (`architect-investigation-003-multi-builder.md`)

Conditional recommendation: **not safe short-term**, feasible mid-term after
worktree refactoring. Core blocker: all builder panes currently share one
git worktree directory (`lib/worktree.sh:22` hardcodes
`.worktrees/builder`), so two concurrent builders editing the same file
would race at the git level with no protection. Secondary risks assessed as
manageable with modest changes: watchdog respawn logic generalizes cleanly
to N builder indices; dispatch load-balancing needs `choose_builder_pane()`
rewritten from hardcoded-single-pane to round-robin or load-aware (using the
`PANE_CURRENT_SPRINT`/`PANE_ASSIGN_TS` state that #002's fix introduces).

---

## Memory isolation and cross-session challenges

**Important scoping note**: `docs/MEMORY_ISOLATION_PROBLEM.md`,
`docs/MEMORY_LOSS_ANALYSIS.md`, and `docs/SES_CLOSED_LOOP_ANALYSIS.md` are all
dated **2026-02-04/05**, i.e. a much earlier era of the project than the
harness pipeline work above, and they read as **design/proposal documents**
written at the moment a problem was discovered, not as closed-loop
incident reports. None of the three contains an internal "fixed, verified"
marker; they end in "立即行动"/"待执行" (immediate action / pending) task
lists. Status should be read as **[UNKNOWN — likely superseded by the
current single-runtime harness architecture, not confirmed fixed in these
docs themselves]**.

- **Memory isolation problem** (`docs/MEMORY_ISOLATION_PROBLEM.md`): a
  guardian ("监护人") observed that work done in one Claude Code window
  (iMessage task processing) was completely invisible to a parallel window
  (community neural-net + memory-system work), even though the content
  existed in that other window's `.jsonl` transcript and was never written to
  the shared semantic-memory database. Root cause diagnosed as four stacked
  problems: `.jsonl` transcripts are per-window and inaccessible cross-window;
  `session.md` checkpoint files are **overwritten**, not merged, so only the
  last-checkpointed window's state survives; semantic memory is written only
  on an explicit user "remember" cue, losing most content; and even
  successful writes only sync every 30 minutes (`docs/MEMORY_ISOLATION_PROBLEM.md:99-104`).
  Proposed remedies: a shared SQLite hub (`evo_memory_semantic`,
  `evo_memory_episodic`, `evo_session_index` tables) with real-time
  post-message hooks — presented as design, not verified-shipped code.
- **Memory loss analysis** (`docs/MEMORY_LOSS_ANALYSIS.md`): a concrete
  incident — of 4 parallel windows' work, 2 were fully recovered (saved to
  `docs/`/`core/` files) and 2 were **permanently lost** because nothing
  forced persistence before window closure. Same root causes as above, plus:
  "不依赖用户主动保存" (don't depend on the user proactively saving) is
  listed as an improvement goal, implying the *current* design at time of
  writing did depend on that.
- **SES closed-loop analysis** (`docs/SES_CLOSED_LOOP_ANALYSIS.md`): a
  self-critique of the project's own self-evaluation system — it generates
  scores and suggestions but has **no execution/tracking/verification
  loop** ("评估 → 建议 → (结束)" — evaluate → suggest → (end),
  `docs/SES_CLOSED_LOOP_ANALYSIS.md`), and its scores were computed from a
  single data row ("evo_tool_calls 只有 1 条记录 (刚配置)" — only 1 record,
  just configured) yet presented with confidence. This is a meta-level
  instance of theme (e) — evidence integrity — applied to the project's own
  introspection tooling.

These three documents are useful evidence of the project's honest-failure
culture (surfacing its own memory/evaluation gaps in writing) but should
**not** be cited as descriptions of the current harness architecture's
memory model, which is a different, later subsystem (SQLite-backed,
single-runtime, file-locked — see README "已知限制" item 1 and item 3).

---

## AutoSci Phase 22 integration log (docs/integrations/autosci/phase-22-progress-log.md)

4,043-line historical decision/execution log; sampled rather than read in
full given size. Governing policy is stated at the top of `AGENTS.md`: three
layers of test evidence (real-task journeys as primary acceptance evidence,
regression tests as a detection layer, and a full atomic-test workbook as
diagnostic reference), with an explicit rule never to "weaken a success
condition or delete a known limitation merely to turn a result green"
(`AGENTS.md:71-72`).

Most recent aggregate roll-up found in the log ("Known Issues Final
Integration," logged 2026-08-07, explicitly stated to supersede the prior
2026-07-30 roll-up and downgrade "inference-only" positive verdicts unless
backed by an actual production journey or entrypoint test):

| Verdict | Count |
|---|---|
| PASS | 26 |
| PASS_WITH_KNOWN_LIMITATIONS | 68 |
| FAIL | 14 |
| ENVIRONMENT_BLOCKED | 2 |
| NOT_AVAILABLE | 22 |
| NOT_TESTED | 10 |
| **Total (Level 2 features)** | **142** |

Validation summary for that roll-up: targeted regression 89 passed/3
skipped; full pytest collection 7029 items, 0 collection errors; J01–J24
journey suite 15 passed/11 skipped; broad root shards 2101 passed/179
failed/6 errors (non-deduplicated); one harness sub-shard **incomplete, no
terminal summary** — explicitly recorded as incomplete, not passed.
Explicitly named open limits: broad pytest non-green; macOS not rerunnable
on the Windows/WSL host used; live providers not rerun without fresh
authorization; external Discord/WeChat and hosted-account revocation paths
untested.

Later entries in the log (through 2026-08-27, after this roll-up) show
continued incremental fixes converging with the pre-scheduler stabilization
log's themes: absolute-path resolution for subprocess model calls, frozen
SchedulerInput identity corrections, native-Windows launch translation for
AutoSci bridge operators, and a live 10-candidate arXiv/Europe-PMC discovery
run. One explicitly flagged remaining design limitation as of 2026-08-27:
"controller-added external input bindings are hash-checked and
route-constrained but are not cryptographically rooted in a separate
immutable controller authority artifact" — an unresolved trust-boundary gap,
explicitly not fabricated a fix for in that entry.

Given the size and continuation of this log, its state should be read as
**[PARTIALLY OPEN — most recent full roll-up shows ~59% PASS/PASS_WITH_LIMITATIONS,
~10% FAIL, ~23% NOT_AVAILABLE/NOT_TESTED, dated 2026-08-07; individual items
continued to be fixed afterward but no later full roll-up was located in the
sampled portions of this file]**.

---

## Intrinsic vs. incidental challenges

This is the most useful lens for a report reader deciding what generalizes.

### Intrinsic (would recur for anyone building this class of system)

1. **Provider structured-output dialects are not interchangeable.** OpenAI's
   strict-schema mode (`required` must list every property), Gemini's
   rejection of certain recursive schemas, and Claude's conservative
   recursive-contract handling are all real, differing constraints — not
   implementation mistakes. Any multi-provider LLM-orchestration system needs
   a provider-schema projection layer as a first-class component, not an
   afterthought. (Theme a)
2. **Natural-language requirements do not cleanly separate "what to retrieve"
   from "what to deliver."** The Discovery semantic-scope defect (workflow
   language bleeding into topical-coverage filters) is a genuine NLP/semantics
   problem: distinguishing corpus-selection criteria from process/deliverable
   obligations inside free text, without either hard-coding vocabulary
   (which breaks on paraphrase) or making the boundary purely a matter of LLM
   judgment (which the project explicitly refuses to rely on alone — it
   insists on a machine-checkable contract, `semantic-retrieval-contract.md`).
   This generalizes to any system compiling free-text intent into structured
   execution plans. (Theme b)
3. **"Did this actually happen" is intrinsically hard to certify from process
   exit codes alone.** Bridges that report `ok=true, exit 0` while wrapping
   internally-failed work is a general problem for any orchestration layer
   built on subprocess adapters over legacy tools — the fix (evidence-first
   completion bound to actual ledger content) is a general pattern, not a
   one-off patch. (Theme d, e)
4. **Multi-writer state under a local coordination substrate (files + tmux +
   SQLite) needs explicit versioning/locking or it will silently corrupt.**
   This is true of any single-machine multi-agent orchestrator using
   filesystem state as the source of truth; the project's repeated discovery
   of the same class of bug (state-revision regression, tmux input-box races,
   frozen-field allowlist drift) across two different eras of the codebase
   suggests this isn't a one-time oversight but a structural cost of the
   architecture choice (local-first, no external consensus store). (Theme f)
5. **N independently-evolving schemas describing "the same" object will
   drift** unless a test explicitly asserts their equivalence. This is a
   general software-engineering truth, sharpened here by having *both* an
   LLM-facing "authoring" schema and a "canonical" schema for several
   artifact types (PlanIR, SchedulerInput) for good reasons (LLMs need
   simpler/flatter schemas than the canonical system does) — the tension
   between those two needs is intrinsic to LLM-in-the-loop structured
   generation. (Theme c)

### Incidental (specific to this implementation's choices/history)

1. **The single-sprint-scanner dispatch bug** (#001) is a straightforward
   implementation bug (returning one result from what should be an iterate-
   all loop) — nothing about multi-agent orchestration requires that
   specific mistake; it's incidental to how `get_latest_sprint_file()`
   happened to be written.
2. **The tmux send-keys dispatch race** (#002) is incidental to the specific
   choice of driving sub-agents via tmux `send-keys` string injection rather
   than a structured IPC/queue mechanism. A different transport (message
   queue, RPC) would not have this failure mode at all — the project's own
   P2 proposal (a dispatch-queue model) implicitly concedes this.
3. **BUG5** (stale bash process running pre-fix code for 28 hours) is
   incidental to using long-running interpreted shell processes without a
   restart-on-change mechanism; any long-lived process with hot-reload
   expectations has this risk, but it isn't intrinsic to the *problem
   domain* (multi-agent research orchestration) — it's intrinsic to *bash
   daemons specifically*.
4. **Windows/WSL portability friction** (fsync-on-directory-handle
   incompatibility, node/npm PATH confusion, bwrap absence) is incidental to
   the project's choice to support Windows-hosted-WSL as a first-class
   deployment target; a Linux-only or container-only system would not carry
   this cost.
5. **Version-metadata inconsistency across 3 sources** (`VERSION`, pipx
   package, root Bun package — README known-limitation #5) and **two
   divergent runtime lines** (`harness/` vs `core/` — known-limitation #2)
   are incidental consequences of this project's specific migration/fork
   history (README explicitly frames #6 as "Fork 与 upstream 链接仍需清理"),
   not something inherent to the problem domain.
6. **The report-title-extraction regex saga** (rows 33, 40, 41, 42 — multiple
   rounds of "the Planner phrased the title slightly differently and the
   parser missed it") is incidental brittleness in a hand-written natural-
   language extraction grammar; a different design (e.g., requiring the
   title as a separate structured field rather than parsing it out of
   generated prose) would sidestep the whole class of bug. The project
   itself seems aware of this — later fixes generalize the grammar rather
   than special-casing, but the recurrence across 4 rows suggests the
   underlying design choice (extract-from-prose) is the incidental source.

---

## Self-stated limitations (verbatim quotes)

### README.md "已知限制" (Known Limitations), `README.md:897-926`

> **1. 单机优先** — 当前 lease、mailbox、event mirror、tmux 与 SQLite 假设共享
> 本地文件系统。它们适合工作站级 orchestration，不等同于容错分布式
> scheduler。
> ("Single-machine first — lease, mailbox, event mirror, tmux, and SQLite all
> assume a shared local filesystem. They suit workstation-level
> orchestration; they are not equivalent to a fault-tolerant distributed
> scheduler.")
>
> **2. 两条运行时演进线** — `harness/` 是当前产品主线；`core/` 中部分
> TypeScript 模块仍是 compatibility / scaffold implementation。两者尚未收敛
> 为单一 canonical runtime。
> ("Two runtime evolution lines — `harness/` is the current product main
> line; some TypeScript modules in `core/` remain compatibility/scaffold
> implementations. The two have not yet converged into a single canonical
> runtime.")
>
> **3. 状态面较多** — spec、runtime state、closure、event ledger、gate
> ledger、evidence ledger、mailbox、tmux/process state 同时存在。虽然可
> 审计，但也增加 reconciliation 与 schema migration 成本。
>
> **4. Live Provider 不可由 Doctor 完全证明** — 安装、依赖与文件系统检查
> 通过，不意味着模型认证、quota、网络、工具权限与真实 delegation 一定成功。
>
> **5. 版本 metadata 尚需统一** — 当前至少存在：`VERSION`: `1.0.0-rc.9`；
> pipx package: `1.0.0rc9`；root Bun package: `3.0.0`。发行流程应定义单一
> version source of truth。
>
> **6. Fork 与 upstream 链接仍需清理** — 部分历史安装、pipx 与文档
> metadata 仍引用 OpenSolar upstream。
>
> **7. Desktop 仍非正式生产发行** — 当前构建配置尚不能替代 code signing、
> notarization、hardened runtime、auto-update 与 release provenance。

### README.md "系统边界与成熟度" table, `README.md:162-176`

Explicitly marks: DAG Scheduler / Gate-Evidence Ledger / Requirement Compiler
/ React Dashboard as "已实现" (implemented); `core/` Bun/TypeScript as
"可选、演进中... 不是主控制面等价替代" (optional, evolving — not an
equivalent substitute for the main control plane); Electron Desktop as
"可打包、仍需硬化... 不等同于已签名生产桌面发行版" (packageable, still
needs hardening — not equivalent to a signed production desktop release);
multi-machine distributed scheduling as "未完成" (not complete); multi-tenant
isolation as "不在当前边界内" (not in current scope) — "不应将本地 status
server 暴露为公网服务" (the local status server should not be exposed as a
public service).

### AGENTS.md anti-gaming policy, `AGENTS.md:71-72`

> "When sources disagree, preserve and report the disagreement. Do not weaken
> a success condition or delete a known limitation merely to turn a result
> green."

### Pre-scheduler stabilization log, repeated framing across many entries

> "Do not label this as demonstrated semantic rejection or a Scheduler
> failure." (re: Requirement schema rejection,
> `pre-scheduler-stabilization-log-20260829.md` ~L69)

> "不要归因成笼统的'LLM 智能不稳定'，也不要靠补 stopwords 来隐藏问题。"
> (Do not attribute this to vague "unstable LLM intelligence," and do not
> hide the problem by patching in stopwords.)
> — `harness/metadata/NEW-MACHINE-START-HERE.md` §4 (source: `pre-scheduler-stabilization-log-20260829.md` narrative and cross-referenced from `NEW-MACHINE-START-HERE.md:120-123`)

> "失败不能被隐藏或记为全绿" (Failures cannot be hidden or recorded as
> all-green.) — final pre-release entry of the stabilization log.

---

## Roadmap gaps (planned, not done)

From `harness/ROADMAP.md` (待评估 — "to be evaluated" section):
> "Agent 间消息协议 — 协调器已覆盖 80%，等真实使用暴露需求" (Inter-agent
> message protocol — coordinator already covers 80%, waiting on real usage to
> expose requirements) — never marked done in this file.
> "Task 依赖 DAG — 等需要并行多任务时实现" (Task dependency DAG — implement
> when parallel multi-tasking is needed) — this item is effectively
> superseded by the later typed-Scheduler/PlanIR DAG work described in the
> stabilization log, but ROADMAP.md itself was not updated to reflect that;
> read it as a stale artifact from an earlier architecture generation, not a
> currently-accurate backlog.

From `harness/TODO-next-session.md` (dated 2026-04-17, revised 2026-05-21):
- Coordinator TypeScript/Bun rewrite explicitly **downgraded from P0 to P1
  architecture debt**, gated behind reproducing the `.coordinator-state`
  corruption bug again plus producing a formal `task_graph.json`
  (`TODO-next-session.md:5-9, 32-36`) — an explicit "don't do this rewrite
  speculatively" guardrail.
- `save_state` writing literal `":"` corruption — root cause **never fully
  located** at time of writing ("根因仍未完全定位"); only a monitoring/
  minimal-fix patch applied, explicitly not the full coordinator rewrite
  (`:21-26`).
- Whisper/subconscious-hook injection unverified in live sessions
  (`:13-17`).
- "论文方案落地 (arxiv 2603.16856)" — an Online Experiential Learning
  sprint-distillation loop — explicitly deferred: "依赖 P0/P1 稳定后再做"
  (depends on P0/P1 stabilizing first) (`:48-51`).
- Browser tool consolidation (browser-use vs. playwright) left as an open
  verify-or-delete decision (`:53-56`).

From `harness/PLANNER-INBOX.md`: four `[PROMPT-QUARANTINE]` entries from
2026-07-08, all unchecked (`- [ ]`), showing prompts containing a stray
`/skills` slash-command fragment that got quarantined rather than
auto-executed — evidence of an input-sanitization guard functioning as
designed, but also an unresolved/un-triaged inbox at time of last commit
touching this file.

---

## Key references (file:line)

- `harness/metadata/pre-scheduler-stabilization-log-20260829.md` — full
  863-line append-only log; rows 1–46 plus ~30 unnumbered narrative sections
  from 2026-08-29 through 2026-09-03 (final entry: pre-`ai4research-main`
  release aggregate regression, 606 passed/34 failed/8 skipped).
- `harness/metadata/migration-handoff-20260831.md:1-69` — the "current top
  blocker" snapshot (superseded within days by the structured-output fix).
- `harness/metadata/migration-handoff-20260830.md:1-100` — superseded
  predecessor checkpoint; documents the 118-schema-asset migration gap.
- `harness/metadata/structured-output-compatibility-20260831.md:1-112` — the
  fix for the top blocker; multi-provider schema-projection design.
- `harness/metadata/semantic-retrieval-contract.md:1-117` — the Requirement
  semantic contract architecture (v1→v3) underlying theme (b) and (c) fixes.
- `harness/metadata/portability-audit-20260830.md:1-80` — full portability
  findings table (theme g).
- `harness/metadata/NEW-MACHINE-START-HERE.md:103-125` — §4 "已遇到的问题与
  解决状态," containing the explicit "don't blame LLM intelligence / don't
  hide with stopwords" warning.
- `harness/BUG5-ROOT-CAUSE.md:1-54` — stale-process-loads-old-code root
  cause, dated 2026-04-20, RESOLVED via coordinator restart.
- `harness/needs-improvement.md:1-4` — auto-generated, currently empty
  ("无低分能力" — no low-scoring capabilities), i.e. no open capability-
  quality alerts at last generation.
- `harness/architect-investigation-001.md:1-175`,
  `harness/architect-investigation-002-dispatch-overlap.md:1-150`,
  `harness/architect-investigation-003-multi-builder.md:1-90+` — 2026-05-03
  coordinator/dispatch architecture investigations (theme f, architectural
  section).
- `harness/DISPATCH-PROTOCOL.md` — bug catalog including "Bug 1: send-keys
  吞键" (`:6`), "Bug 2: mtime 目录级检测漏检" (`:26`), "Bug: get_latest_sprint_file
  跳终态导致 handle_passed 永远不触发" (`:236`), "bug #9 僵尸 pidfile 回归
  修复" (`:366`), "运行时补偿失效根因 (Bug #5)" (`:462`).
- `harness/ROADMAP.md:55-57`, `harness/TODO-next-session.md:1-88`,
  `harness/PLANNER-INBOX.md:1-4` — roadmap-gaps section.
- `docs/MEMORY_ISOLATION_PROBLEM.md`, `docs/MEMORY_LOSS_ANALYSIS.md`,
  `docs/SES_CLOSED_LOOP_ANALYSIS.md` — 2026-02-04/05 design-proposal docs,
  status unconfirmed within the files themselves.
- `docs/integrations/autosci/phase-22-progress-log.md` — 4043 lines, sampled;
  most recent full roll-up dated 2026-08-07.
- `README.md:162-176` (系统边界与成熟度), `README.md:897-926` (已知限制).
- `AGENTS.md:1-100` (Phase 22 verification strategy and anti-gaming policy).

---

## Open questions

1. **Did the `ai4research-main` release actually land with 34 known-failing
   tests as debt, or were they resolved before/after the branch merge into
   `openJiuwen-Solar`?** The stabilization log ends at the release-prep
   step; this repo checkout's current HEAD (`b0bf165f9`, "merge:
   ai4research-main into openJiuwen-Solar") postdates that log, so a current
   test run would be needed to know whether that debt is still present.
2. **Is the memory-isolation/cross-window problem (2026-02) still applicable
   to the current single-runtime harness architecture**, or was it fully
   superseded by the 2026-08/09 single-runtime, admission-lease-based
   Coordinator design? The docs don't cross-reference each other, and no
   later document explicitly closes the loop on the 2026-02 memory docs.
3. **What is the actual current Phase 22 Level-2 pass rate** — the
   2026-08-07 roll-up (PASS=26/142, PASS_WITH_LIMITATIONS=68/142) predates
   the 2026-08-27+ fixes visible in the same log's later entries and the
   full pre-scheduler stabilization arc; no later full 142-row roll-up was
   located in the sampled portions of the 4043-line file. A full re-read (or
   a query against `phase-22-test-report.xlsx` / `phase-22-l2-issue-register.md`,
   neither of which this investigation opened) would be needed for a current
   number.
4. **Row 39's report-plan schema-identity mismatch and the CLI
   failure-misattribution bug** are both explicitly logged as "not fixed" at
   their respective entries and were not revisited later in the sampled
   material — worth confirming whether they were addressed in commits after
   the log's last entry.
5. **The composition/materialization cardinality gap** (diagnosed
   2026-09-03, fix not yet applied at time of that entry) is the most
   recently-identified open architectural gap in the whole corpus and is a
   good candidate for "most likely still open right now" if a report needs
   one concrete current risk to name.
