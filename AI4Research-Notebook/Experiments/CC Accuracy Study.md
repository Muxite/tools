---
id: cc-accuracy-study
status: proposed
source: AI4Research-Development/jiuwenswarm-m1@98bd9d913f9ddae5f0d6a3ae256bff10f25ee743; Experiments/Development-Cases/README.md; Resources/review-batches/2026-10-21-capsules/README.md
last_reviewed: 2026-10-21
next_action: Complete runnable M1 adapter and challenge-case custody audits, then freeze a signed study manifest before any model run.
---
# CC accuracy study

> **Proposed and unrun.** This design has no observed results, no held-out examples or answers, and no claim that CCs improve accuracy. Current M1 source is a candidate implementation; the study adapter and live runtime path remain unqualified.

Links: [[Workstreams/CC Effectiveness]] · [[Workstreams/Lab Infrastructure]] · [[Home]] · [[Resources/M1 Readiness]] · [[Designs/CC Reference]]

## Question and estimand

For frozen bounded research tasks, does having the producer use the pinned M1 capsule declaration, body, and producer-side workflow improve answer accuracy and useful coverage, when the semantic reviewer sees the same pinned declaration and exact output only, and all arms use the same protected deterministic checks and gate? The primary contrast is producer CC against a matched plain producer, conditional on the shared verifier and mandatory checks. This estimates the producer-side bundle contribution under a fixed review system. It does not estimate a verifier-only gain, planner quality in general, or broad model superiority.

The user requirement is that the semantic verifier receives the capsule declaration and exact output only. It must not receive the producer's task inputs or hidden key and must not redo the task. Input-aware deterministic predicates remain in a separate host check path. This is a fixed boundary in every arm, case, and scorer procedure.

## Arms

| Arm | Producer | Review and gate | Purpose |
|---|---|---|---|
| A — Raw/plain | General agent receives the frozen prompt and task fixtures; no CC-specific declaration/body/template | No review or release in this diagnostic arm; preserve and score producer output only | Reference producer quality before checking |
| B — Plain + same checks | General agent receives the same frozen prompt and task fixtures, with the same model/tools/budget as A/C | Same protected checks, independent declaration/output-only verifier, gate, policies and profiles as C | Plain producer through the protected release path |
| C — CC + checks | Frozen exact CC set/body/declarations for the case | Exact same reviewer input construction, verifier version/model/prompt/profile, mandatory checks and gate | Producer CC treatment |

Run three distinct observable paths: A is plain raw output scored before protected review and never released; B is plain output through frozen checks/verifier/gate; C is CC output through those identical checks/verifier/gate. The primary comparisons are B versus C (producer CC effect under matched checking) and A versus C (whole-bundle diagnostic, with review-path difference disclosed). For the common study-release metric, A's substantive raw answer counts as a study answer delivered for scoring even though it bypasses the gate; it is never a product release. In B/C, study release means a substantive answer passed by the gate. Preserve gate status separately. Do not compare B/C gate false-acceptance to A because A has no gate.

Keep producer effective model/version, route, sampling settings, context limits, tools, connector evidence, output limits, wall-clock limit, fresh-state policy, and total task-level worker+verifier call/token/tool budget identical. The total cap covers CC and verifier overhead together; B/C do not receive extra budget to offset their check path. Record actual per-call effective identity and usage. Use the exact same verifier declaration, model and profile for B/C; reviewer prompt payload hashes match the same declaration/output boundary required by the treatment. Verifier receives no original task prompt or fixture. The scorer may see the case and key only after outputs are frozen and blinded.

If raw A consumes model budget, hold a common per-case total budget across all arm paths and count every call. Do not grant B or C an extra verifier call. Missing cost/token telemetry is null with reason, never zero. Pin effective route/model per call; a model/router change invalidates a pair or is explicitly analyzed as a protocol deviation.

## Scope and first case set

The first controlled challenge should be narrow: Scientific Evaluation with frozen blueprint, values, and registered rule oracle, followed by producer/semantic-reviewer challenge cases for Intent and Requirements, then Screening. The six synthetic development tasks in [[Experiments/Development-Cases/README]] provide supplementary daily research work: intent normalization, brief construction, code repair, experiment design, reporting with missing values, and literature synthesis. The Intent/Brief fixture formats are synthetic task adapters, not actual M1 `qualified-intake`/`intent-ir`/Research Brief contracts. They cannot establish M1 acceptance without an adapter audit.

Create additional M1 contract-level accuracy cases as development cases only after source contract mapping. Include source-attributed Intent/Brief, plan choice, evidence-grounded Search, Screening ranking and abstention, Hypothesis rule validity, Builder code correctness, Benchmark receipt/arithmetic, Evaluation classification, and Delivery fidelity. Planner challenges should record all eligible candidate pins, policy, resource inventory and binder reasons. Optional gates can be added only if admitted and policy-compatible. The required stages and mandatory profiles are fixed; no arm may remove or weaken them.

Use task-specific oracle checks where exact expected behavior is available (schemas, rule arithmetic, source refs, IDs, file tests, invariants), plus a blind task-specific rubric for open-ended quality. Do not use model agreement as correctness evidence. Freeze exact prompts, fixtures, scoring anchors, critical errors, source commit, adapter, model/tool pins and analysis before execution.

## Accuracy and outcome ledger

Record orthogonal labels at each layer. Do not force all behavior into one mutually exclusive five-way outcome, because correctness, blocking, answerability, release, scientific meaning, and operations describe different things:

| Axis | Values and interpretation |
|---|---|
| Oracle answerability | `answerable`, `unanswerable`, `unknown`; fixed by custodian key for the case |
| Candidate correctness | `correct`, `incorrect`, `abstain`, `unjudged`, `none`; score producer artifact independently of the gate |
| Semantic assessment | Per-criterion finding and verifier verdict; false acceptance is wrong candidate marked advancing, false rejection is correct candidate marked non-advancing |
| Deterministic checks | Per-check `PASS`, `FAIL`, `INCONCLUSIVE`/unavailable; compare to host oracle and runtime evidence |
| Gate decision | `accepted`, `blocked`, `error`, `not_applied`; record reason and whether the block is justified |
| Study release | `answer`, `abstention`, `none`; A counts raw substantive answer as a study answer for scoring, never product release; B/C require gate acceptance for answer release |
| Scientific classification | Per-metric and overall `PASS`, `FAIL`, `CONDITIONALLY_ACCEPTABLE`, `INCONCLUSIVE`, or `not_applicable`; compare against frozen rules |
| Operational status | `completed`, `interrupted`, `timeout`, `budget_cap`, `provider/runtime/connector/executor failure`, `invalidated`; operation failure cannot be scored as candidate wrongness |

Summarize correct answers released, incorrect answers released, correct answers blocked (false rejection), incorrect answers blocked (correct rejection), appropriate abstentions, avoidable abstentions, and operational failures separately. A wrong answer blocked is a desirable gate outcome; a correct answer blocked is a false rejection. Do not conflate them. An answerable case with a bad candidate that is correctly blocked is neither an abstention nor a false acceptance. A genuine scientific `INCONCLUSIVE` is a classification, not an abstention, unless the task contract explicitly defines it as “not answering”; preserve both axes. A legitimate scientific `FAIL` or registered `CONDITIONALLY_ACCEPTABLE` can be a correct delivered answer. A verifier timeout is operational failure, never false rejection. A mechanical check that correctly blocks a malformed output is a correct rejection; missing/failed check infrastructure is operational failure.

For each class and layer report numerator, denominator, rate (null when denominator is zero), case/repetition rows, and adjudication. False acceptance means a wrong candidate advances at that layer; false rejection means a correct candidate is denied at that layer. The host check may use bound inputs/runtime refs under its own authority. Semantic reviewer challenge pairs must keep declaration and exact output bytes as the entire reviewer-facing evidence; hidden task facts remain with custodian and scorer. Report reviewer confusion separately from deterministic checks and final gate action.

## Frozen challenge construction and custody

The proposer/tuner must not see held-out cases before freezing its design. At the assigned evaluation, the producer receives the held-out prompt and task fixtures it needs to do the case; withholding those inputs would make the task impossible. A distinct custodian, who does not tune producer prompts, verifier instructions, thresholds, check profile or gate policy, creates and assigns at least three held-out task cases and a separate verifier challenge set before tuning starts. Holdout identities, prompts, fixtures, answer keys, expected labels, and input hashes live in an access-controlled manifest. The assigned producer sees only its case inputs at execution; other proposers/tuners, the verifier, and study adapters receive neither the key nor unrelated cases. The verifier sees only the capsule declaration and exact output. The ordinary scorer receives the minimum task inputs/key after outputs are immutable and blinded. No held-out prompt, fixture, key, identity, or result is stored in this notebook.

Before first run, custodian records a keyed manifest digest, allowed audience, access log, and escrow/release procedure. The protocol, source pins, adapter, scoring rules, analysis code, and development manifest are frozen before held-out generation is opened to the independent custodian. Tuning on a held-out output or label retires the case. After all arm outputs are immutable and blinded, custodian releases only the minimum scorer materials to independent scorers; producer and verifier never receive keys. An alleged leakage retires the case before labels are inspected for that run. Do not infer held-out scores or fabricate outcomes.

Held-out scoring should include planted wrong-but-plausible answers, correct answers, valid scientific negatives, answerable abstention traps, unanswerable/insufficient-evidence cases, malformed-but-structural candidates, and operational faults injected outside model semantics. Ensure both positive and negative cases exist in each important class; otherwise rate is undefined and reported `null` with reason, never zero.

## Repetitions, randomization and scoring

For the initial development pilot, run three paired repetitions per task. Randomize arm order within each repetition and counterbalance order across a task. Use fresh conversation/workspace state and exact byte-identical inputs in each pair. Do not repair or rerun a system output. Preserve failed, interrupted, capped and invalidated records. This is a feasibility/rubric pilot with descriptive summaries only; do not claim statistical generality or significance.

Blind scorers receive the output, task prompt/fixture and key only after run closure. They do not see arm label, model trace or condition. Use one independent scorer plus adjudication by a second independent scorer for any critical error disagreement or any 2-point-or-greater difference on a 0–4 dimension. Preserve each initial score and adjudicated score. Scoring key is case-specific: exact oracle fields and critical-error rules precede four dimensions (factual support, required coverage, reasoning/decision quality, and usable format), each 0–4. A critical violation can mark incorrect even when averaged dimensions are high. Exact validators should be executable where possible and frozen before runs.

Primary accuracy comparison is B vs C among complete, protocol-valid pairs, by task and overall descriptive paired difference; also report A vs C as a whole-bundle diagnostic and A producer-only quality before checks. Report raw distributions, critical-error rate, answer correctness/coverage, answerability-stratified abstention, operational failure, false acceptance/rejection, and per-layer confusion counts with denominators. Do not build a blended score that treats failure or abstention as zero. With three repetitions, present every pair and avoid inferential claims.

Resource summaries include per-call stage, requested/effective provider and model, route, call ID when available, duration, input/output tokens, tool calls, cost/currency, and unavailable reasons. Report status counts and observed resource values for every arm, including failed runs. Paired usage/time summaries require both sides measured; nulls remain missing. A sensitivity analysis may include otherwise-comparable completed cases with documented deviations, clearly labeled exploratory and excluded from primary analysis.

## M1-specific readiness and compatibility

Current source-level roles and obligations are indexed in [[Designs/CC Reference]]. That reference is pinned to the inspected `ai4r_M1` candidate `98bd9d9`; a later remote `d3d7f56` was checked for capsule/native/check file changes and those cited files were unchanged. The current branch contains different contracts from an older JiuwenSwarm design package; keep those versions labeled. Compatibility is judged against the exact pinned declaration/ports/check profile and test fixtures used by the actual adapter.

Do not widen semantic reviewer input to original task input. M1 declarations/profile require `declaration_and_output`; protected deterministic checks have separately explicit input/runtime evidence. Do not use optional planner-selected gates as substitutes for mandatory checking profiles. Any proposed exception must name the exact contract, implementation, and failing test, with narrow scope and owner. Per-CC containerization is a deployment decision distinct from whole-lab isolation; see [[Designs/cc-containerization-and-lab-isolation]].

Before runs, audit and freeze: accepted library standing and declaration/body/check/profile hashes; planner static/planned mode and full effective policy; run/resource pins; worker and verifier model routes and total budget; immutable output capture; blind scorer/key separation; and an adapter that maps each study fixture into the real M1 port contract without changing meaning. Verify that SemanticVerifier sees only exact declaration/output bytes. Verify deterministic checks use only authorized refs. Run local deterministic tests and target-specific gated integration tests only after dependencies and authorization are ready; report skips and missing live prerequisites as such. Source-level read-through is not runtime evidence.

## Candidate amendments before a production claim

These are bounded study-harness amendments, not accepted changes to M1 product contracts:

1. Add an immutable attempt ledger that joins producer output ref/hash, declaration pin, reviewer input hash, semantic findings/verdict, deterministic check results, gate decision, and operational exit reason without exposing hidden labels. This permits layer-by-layer false-acceptance/rejection accounting.
2. Add a custodian-only challenge runner that injects frozen declaration/output pairs into the actual declaration/output-only Verifier boundary and independently compares assessment plus final gate to labels. The key store must be unreachable from worker, verifier, and ordinary run adapters.
3. Extend study capture to include candidate snapshot cardinality, selectable pins, plan policy, resource inventory, effective required stages, proposal, and binder rejection codes. This tests whether optional-gate availability is limited by catalog, policy or proposal choice while preserving mandatory checks.
4. Add task-specific executable oracles for arithmetic/schema/source refs and synthetic code tasks, plus a blinded rubric for judgments without exact labels. Audit scorers independently on boundary examples before opening holdout labels.

Do not change worker prompts, declarations, thresholds, required stages, checking profiles, reviewer context, or gate release rules during the primary comparison. Any accuracy-driven product amendment found by development cases needs a new version pin and fresh held-out suite; never tune against held-out outcomes.

## Version pins and records

Freeze repository SHA, declarations, carrier bodies, prompts, shared helper, check runner/bundle, checking profile, model route/settings, connector/tool versions, container/runtime/dependency lock, fixture and prompt hashes, rubric, adapter and analysis code. Store raw artifacts by content hash and keep immutable per-arm traces. Include model/verifier call records and actual resource null reasons. Raw results format is documented in [[Experiments/raw-results-schema]].

The three-arm recorder is [accuracy_ledger.py](tools/accuracy_ledger.py) with seven checks in [test_accuracy_ledger.py](tools/test_accuracy_ledger.py). Its current row fields include case/repetition/arm, answerability, candidate correctness, gate, study release, scientific result, operational failure reason, elapsed time, usage, input/configuration hashes, and prompt/output refs. Before the first run, extend/freeze its adapter sidecar so `prompt_ref` identifies the exact producer prompt/fixture package, and append-only external records capture every worker/verifier call with stage, requested/effective route/model, call ref, timing, tokens/cost when available, and missing-measurement reasons. Bind that sidecar by content hash from each ledger row or output envelope. The existing `configuration_sha256` must describe the matched protocol envelope; arm-specific prompt hashes stay in `prompt_ref`. Verify pairing by case inputs/configuration while retaining different prompts as intended treatment. Run and review the seven ledger tests after any schema change. The older two-arm analyzer is not the primary recorder for this three-arm, layer-specific design. No results are generated by this document.

## Interpretation

Evidence from this pilot can establish how these frozen configurations performed on these cases under this runtime and budget. It cannot establish a general CC effect, universal verifier accuracy, future held-out performance beyond the custodied sample, or production reliability. Null, unavailable, unrun and held-out values stay explicitly so.
