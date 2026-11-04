---
id: cc-candidate-designs
status: proposed
source: Sources/Implementation Intent; Designs/CC Reference; Amendments/Planner Capability Gaps/README.md
last_reviewed: 2026-10-21
next_action: Use actual planner traces and repeated development failures to decide whether either candidate deserves implementation
---
# Candidate capsules: evidence before expansion

These are authoring proposals, not admitted capsules or proof of planner starvation. Existing Search, Screening and Delivery already handle evidence-related work. Implement a candidate only if a captured gap shows an independent reusable job is missing or difficult to test. Prefer a helper inside an existing carrier when that is sufficient. No proposed name reserves an official task, interface or acceptance ID.

## Structured evidence extraction

**Candidate job:** extract a requested set of structured facts from already captured, immutable documents while preserving exact source attribution. This is not web search or open-ended literature synthesis.

| Declaration concern | Proposed contract |
|---|---|
| Inputs | Captured document references/hashes, bounded extraction request, field schema, extraction limits |
| Output | One evidence table: requested field, extracted value or explicit unavailable reason, source ref/hash, exact byte/span locator and supporting quote; separate conflicting observations |
| Effects/dependencies | Read only explicitly bound documents; write only declared output artifact. No network, code execution, library mutation, account access or arbitrary file reads |
| Carrier | Reuse existing immutable capture/ref resolution, model bridge, output capture and protected host check machinery; deterministic parsers first for structured inputs |
| Mandatory host checks | Every source belongs to bound input; source hashes match; span resolves; quote matches captured bytes; no invented source; required fields accounted for; bounds enforced |
| Blind semantic check | Declaration/output-only assessment of internal consistency, explicit missing/conflicting values and whether stated interpretation follows the supplied quoted material. It cannot establish that the original quote is authentic |
| Failure behavior | Missing/unreadable source is explicit; ambiguous value remains unresolved. No invented value, fallback network lookup, hidden source substitution, or silent omission |

Development tests should include duplicate sources, conflicting dates, absent fields, Unicode spans, misleading table headers, unsupported conclusions, forged source refs, edited quotes, and prompt injection inside a source. Freeze independent held-out variants and their source truth outside tuner access. The producer receives the assigned case inputs only when evaluated; keys remain hidden.

## Evidence-to-claim checking

**Candidate job:** assess whether explicit claims are supported by specified captured evidence. It returns findings; it does not decide admission/release or rewrite the report being checked.

| Declaration concern | Proposed contract |
|---|---|
| Inputs | Explicit claim list, bound evidence bundle, scoped support rubric and permitted uncertainty vocabulary |
| Output | One assessment per claim: supported, contradicted, insufficient evidence, or out of scope; exact evidence references/spans and bounded rationale |
| Effects/dependencies | Read only assigned claims/evidence; emit declared assessment. No external retrieval, source rewriting, producer prompt access outside assigned job, self-activation or release authority |
| Carrier | Existing governed model bridge for semantic support assessment; deterministic citation/coverage checks outside it |
| Mandatory host checks | Claim coverage exactly matches inputs; references resolve into bound sources; quoted spans match; allowed labels only; all mandatory fields present |
| Blind semantic check | The runtime verifier checks this candidate's declaration and exact assessment output. It does not receive the candidate's original claim/evidence inputs or redo its support-assessment job |
| Assurance limit | Correct source links and plausible rationale do not prove semantic support. Independent held-out keys test the assessment job itself. Unsupported findings cannot grant release |

Tests should distinguish direct support, contradiction, missing evidence, outdated evidence, correlation versus causation, unsupported quantifiers, citation laundering, scientific negatives, and source injection. A correct insufficient-evidence assessment may be a substantive assessment result, not an infrastructure failure.

## Adoption rule

Capture the actual reusable gap, overlap with existing carriers, expected accuracy benefit, dependencies and authoring cost. Compare helper versus independent CC, then register the chosen bounded change in native project records. Write the declaration and independent conformance criteria before implementation. Admit only a new pinned version after required evidence; planner visibility and policy compatibility are separate checks. Mandatory gates remain protected and there is no recursive chain of reviewers.
