---
id: amendment-cc-accuracy-verification
status: proposed-user-authorized-preparation
source: User-authorized amendment preparation, 2026-10-21
last_reviewed: 2026-10-21
next_action: Prepare isolated held-out challenge protocol and scorer fixture
---
# CC Accuracy Verification

**Package ID:** `AM-CCAV-001` · **Priority:** first · **Status:** proposed user-authorized preparation, not product acceptance.

Read this package in order: this overview, [evidence snapshot](Evidence.md), then [manifest](manifest.json). Its required reading is portable within this folder. M1 commit `d3d7f565c6c05ccf764fe0780fde149b7dc89b95` is a captured code baseline, not a deployment claim. The evidence snapshot records the conflicting branch PRD pointers; resolve those in native project records before changing product obligations.

## Purpose and baseline

Measure whether a proposed work CC produces correct, supported outputs across predeclared held-out challenge cases. This package improves testability by making correctness claims falsifiable and by separating development/calibration cases from held-out scoring. A producer receives the specific case input only when that case is assigned for evaluation; it cannot browse the suite, keys, expected outputs, hidden-result history, or later cases. The runtime semantic verifier never receives the original input. This package does not expand the verifier's input surface or make a verifier a second author.

M1 currently pins a CC declaration and implementation closure, captures outputs, runs deterministic checks, then assigns separately budgeted semantic review. In `SemanticVerifier.review`, the model payload contains the subject declaration and exact output only. The producer receives its assigned input; the semantic verifier does not receive that original input. Neither receives hidden answer keys or evaluator-only outcomes. The protected host can check input-dependent obligations separately. Whether these mechanisms improve accuracy is the hypothesis to test.

## Proposed amendment and compatibility

Add an offline evaluation protocol around existing CC invocation and release. Compare three arms over the same predeclared cases and budget: (A) raw/plain producer output without M1 checks, (B) raw/plain producer output with the frozen deterministic checks and existing output-only semantic review, and (C) candidate CC output with the same deterministic checks and same output-only semantic review. Freeze suite identity, oracle, gates, reviewer profile, metrics, error categories, coverage, budgets, and candidate pins before scoring. Assign one case input to the producer for that run only. Keep the suite, keys, expected outputs, unassigned case inputs, per-case hidden results, and final-evaluation feedback evaluator-owned. Release only approved aggregate and bounded non-leaking feedback.

Keep current declaration/output-only runtime verification, deterministic checks, `ProtectedGate`, output capture, and host-owned release unchanged. Preserve all maintained `TASK-*`, `AC-*`, and `IF-*` identities; this package adds `AM-CCAV-AC-*` criteria only. Any future change to review inputs requires a separate design decision and compatibility review; it is outside this package.

## Acceptance criteria

- `AM-CCAV-AC-01`: the frozen evaluator records the exact candidate declaration and implementation hashes, suite version, challenge-set commitment, scorer version, limits, and predeclared metric thresholds before the run.
- `AM-CCAV-AC-02`: run the three arms on identical frozen cases and identical declared budgets; only arm A omits M1 checks, while arms B/C use the same deterministic gates and existing output-only semantic review. Record arm identity and exact producer/check/reviewer pins per case.
- `AM-CCAV-AC-03`: a candidate gets only the input assigned to its current case. Attempts to list/read the suite, keys, expected outputs, unassigned cases, prior per-case hidden outcomes, or final-evaluation feedback are denied and recorded.
- `AM-CCAV-AC-04`: a controlled probe confirms semantic verifier request contains declaration and exact candidate output plus independently pinned instructions/criteria only; no original input values or hidden evaluation data enter the request.
- `AM-CCAV-AC-05`: frozen gate selection binds to exact outputs. Record per arm, separately: correct, wrong, abstained, invalid-output, deterministic-rejected, verifier-rejected, pre-execution blocked, evaluator-error, and accepted counts. Report accuracy on adjudicated outputs, abstention and coverage rates, blocked/incomplete rates, false accepts/rejects, per-stratum metrics, uncertainty, and limits; never merge blocked cases into correct or silently drop them.
- `AM-CCAV-AC-06`: missing required output, schema failure, timeout, unavailable verifier/check, or failed deterministic check yields non-advancing status; infrastructure/policy block is distinguished from a wrong answer or abstention.
- `AM-CCAV-AC-07`: held-out aggregate metrics reproduce from retained evaluator-owned raw records; a score alone never activates a candidate.
- `AM-CCAV-AC-08`: repeated runs, leakage attempts, malformed scorer output, or observed outcomes cannot replace suite, threshold, evaluator identity, gates, or candidate pin.
- `AM-CCAV-AC-09`: record oracle answerability, candidate correctness, gate disposition, study release, scientific classification and operational termination as separate axes. A correct scientific FAIL/INCONCLUSIVE is a substantive answer; abstention is not automatically incorrect. Blocking a wrong candidate is prevented error; blocking a correct candidate is false rejection. Neither is silently categorized as operational failure. Show all denominators and unavailable values.

## Observable negative scenarios

Attempted suite listing or hidden key/expected-output read, access to unassigned case inputs, prompt injection asking for answers or prior hidden outcomes, evaluator mutation, post-result threshold/gate change, missing case, evaluator crash, and a polished but unsupported candidate answer must each result in denied access or explicit non-advancing status with attributable evidence. The assigned case input is available to its producer during that invocation. A candidate that passes a sample while failing a required stratum remains rejected or blocked under the frozen policy.

## Required evidence and rollback

Retain the immutable candidate source and declaration, challenge-set commitment and custody identity, scorer/test implementation hashes, environment and resource config, raw per-case evaluator records in evaluator custody, aggregate report, runner invocation and gate decisions, failed/blocked observations, and an export checksum. Candidate output logs must be scrubbed of credentials before export.

Rollback means selecting the previously admitted implementation binding for future plans. Keep the candidate, evaluation records, and rejection evidence; do not edit old run records or erase hidden custody. Verify by inspecting the next frozen plan and confirming it binds the prior version.

## Minimal evidence snapshot

See [Evidence.md](Evidence.md) for the exact M1 verifier payload and gate ownership excerpt, with source SHA-256 receipts. This is a small portable source bundle; the full repository remains the coder's source of truth for changes.
