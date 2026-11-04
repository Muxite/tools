# Design coverage and review

**Reading level: AI reference; design audit.** This is the single maintained design-review account, not a coding handoff or runtime acceptance report. The first human route is [README](README.md); details and contracts are linked underneath it.

## Baseline and source differences

The prior package, including local edits and the interrupted reference draft, was copied byte-for-byte to `architecture-checks-2026-10-07/three-tier-before` outside the repository; every copy hash was verified. The interrupted broad reference draft had 60 contracts and 178 example/context records. It is superseded by six critical schemas plus shared definitions and concise field contracts for other major boundaries.

The current received PRD is the unchanged October 7 download. Differences from the previous receipt include §1.10 change classification/canonical synchronization, §1.11 US01–US20, §6.2.1 verification governance and §6.2.2 incremental implementation. Product changes additionally require explicit intake/default/readiness outcomes, measured baseline/treatment/delta, scientific rationale, report consistency, read-only inspection and visible lifecycle results. Output conformance now references Node Execution Contract plus applicable CC declarations. Architecture dispositions appear in the coverage below; development governance remains outside the design package.

## Observed Intent outputs

`intent-output-1.zip` contained an ACCEPTED run for “research on data lake retrieval algorithm”. Its IR repeated the topic, had null desired outcome, and listed missing research questions/methods/evaluation/deliverable/timeframe. The verifier passed fidelity and omission preservation while explicitly denying Brief readiness. This demonstrates a missing **usability acceptance obligation**, not proof that all omitted experimental details must be demanded at Intent. The revised boundary blocks absent purpose/result, preserves uncertainty and asks for clearer intent without automatically conducting clarification.

`intent-output-2.zip` was exported in COMPILING state, with a RUNNING compiler attempt and no accepted IR. It provides incomplete snapshot evidence, not a completed compiler-quality result. Both archives put UTF-8 text/JSON in anonymous `.bin` members; the revised inspection boundary requires readable named artifacts and derived views. These observations motivate design changes; they do not prove that documentation alone caused every implementation defect.

## PRD and user-story responsibility map

The [clause index](coverage-allocation.md) maps every current numbered heading. The table below checks the specific user-visible journey without repeating the PRD stories. Each is realized within Phase 1; Phase 2 RSI and Phase 3 efforts remain separately covered by [phase details](phase-details.md).

| Story | Specific source | Architectural realization | Owner document |
|---|---|---|---|
| US01 | 5.2.1–5.2.2 | Pre-flight explicitly checks mandatory services/model/workspace; no dispatch if unavailable | [research-design.md](research-design.md) |
| US02 | 3.1.1, 3.1.3 | Original objective and effective profile attribution | [reference/other-contracts.md](reference/other-contracts.md) |
| US03 | 3.1.2–3.1.3 | Qualified local context and explicit required-input rejection | [research-design.md](research-design.md) |
| US04 | 3.2.3–3.2.6 | Constraints/targets and attributed authorized defaults | [reference/intent-and-requirements.md](reference/intent-and-requirements.md) |
| US05 | 3.2.7, 5.3.1 | Inspect accepted Brief, assumptions and underlying records | [artifact-inspection.md](artifact-inspection.md) |
| US06 | 3.3.5–3.3.6, 5.3.1 | Cited ideas and exact source evidence | [research-design.md](research-design.md) |
| US07 | 3.4.3–3.4.7, 5.3.1 | Scores, rationale and selected/rejected dispositions | [reference/other-contracts.md](reference/other-contracts.md) |
| US08 | 3.5.2, 3.5.4–3.5.5, 5.3.1 | Inspectable registered hypothesis and test protocol | [research-design.md](research-design.md) |
| US09 | 3.6.2–3.6.5 | Bounded POC and mechanical readiness before empirical work | [placement.md](placement.md) |
| US10 | 3.7.2–3.7.4 | Matched baseline/treatment values, delta and raw evidence | [reference/other-contracts.md](reference/other-contracts.md) |
| US11 | 3.8.4–3.8.6, 3.9.2 | Measurement-to-registered-criterion reasoning; negative result delivered | [research-design.md](research-design.md) |
| US12 | 5.1.1, 5.3.1–5.3.2 | Run/stage/status distinguish progress, checking, completion and halt | [artifact-inspection.md](artifact-inspection.md) |
| US13 | 5.1.2, 5.3.3 | Retained failed attempt, reasons and authorized fresh correction | [failure-and-human.md](failure-and-human.md) |
| US14 | 5.1.3, 5.6.3 | Observed enforceable limits and unavailable telemetry | [model-routing.md](model-routing.md) |
| US15 | 3.9.2, 3.9.4 | Readable report consistent with saved verdict | [artifact-inspection.md](artifact-inspection.md) |
| US16 | 3.9.3–3.9.4 | Audience-scoped experiment/evidence retrieval | [reference/other-contracts.md](reference/other-contracts.md) |
| US17 | 5.1.2, 5.3.1 | Read-only previous-run inspection without execution | [artifact-inspection.md](artifact-inspection.md) |
| US18 | 5.6.2 | Durable defaults outside run/workspace lifetime; effective freeze | [placement.md](placement.md) |
| US19 | 5.4.2–5.4.3, 3.9.4 | Pre-effect confinement and scoped authorized transfer | [placement.md](placement.md) |
| US20 | 5.4.4 | Authenticated local data inspection/removal; scoped lifetime | [artifact-inspection.md](artifact-inspection.md) |

## Scenario walkthrough

These are expected design outcomes, not observed runtime test passes. Executable fixtures and measured verifier criteria remain implementation verification work.

| Challenge | Designed outcome | Boundary |
|---|---|---|
| Actionable request, optional omissions | Intent schema passes; verifier accepts usable purpose/result; method and experiment details remain downstream | [intent-design.md](intent-design.md) |
| Topic-only request | Shape/fidelity may pass; semantic usability is INCONCLUSIVE; gate halts before Requirements | [intent-design.md](intent-design.md) |
| Conflicting constraints / invented goal / missing exclusion | Valid shape cannot rescue invalid interpretation; verifier reports failed/unclear obligation | [reference/intent-and-requirements.md](reference/intent-and-requirements.md) |
| Candidate instruction injection | Treat content as evidence; no policy change or replacement interpretation | [guard-design.md](guard-design.md) |
| Malformed compiler/verifier or stale/swapped subject | Mechanical checks halt; no old decision reused | [reference/checking.md](reference/checking.md) |
| Verifier/model unavailable or timeout | No acceptance; preserve available evidence and actionable environment reason | [failure-and-human.md](failure-and-human.md) |
| Persistence failure | No successor readiness; do not claim unavailable evidence is durable | [capsules.md](capsules.md) |
| Headless / browser disconnect / restart | Headless never waits; disconnect preserves execution; restart pauses without replay | [failure-and-human.md](failure-and-human.md) |
| Scientific rejection | Correct scientific FAIL receives infrastructure acceptance and goes to Delivery | [reference/checking.md](reference/checking.md) |
| In-progress export / unavailable telemetry | Incomplete state or unsupported observation remains explicit, never a complete pass | [artifact-inspection.md](artifact-inspection.md) |
| RSI hidden leak / referee edit / promotion bypass | Contain/reject, retain violation evidence, no secret export or activation | [offline-rsi.md](offline-rsi.md) |
| Wrong sidecar target/version / missing capability | Compatibility/readiness blocks before submission through ordinary client boundary | [automation.md](automation.md) |

## Human review and quality checks

The immediate route explains the complete system, CC/verifier/gate ownership, Intent versus Requirements, routing/RSI placement, container/browser access, readable evidence and phase direction. Deep explanations retain purpose, connections, broad approach, passing/blocking behavior, authority and rationale. Review it without tier 3 and answer:

1. What does the system do from intake to delivered evidence?
2. Who writes each major artifact and who may release it?
3. Why do deterministic checks and semantic assessment both exist?
4. What distinguishes Intent, Requirements and registered experimental criteria?
5. Where do routing and RSI connect, and what authority do they lack?
6. What is built now, what does each phase add, and what does a user see after a halt?

Reference quality checks cover schema/field agreement, source spans and exact references, verdict/control distinctions, consumer compatibility and shared version authority. Mechanical checks validate critical schemas/examples, deliberate invalid cases, source hashes, current clause/story coverage, link/fragment closure and a copied standalone folder. All maintained Mermaid views are audited; changed sources and SVG/PNG projections are rendered and visually inspected. Executed results and remaining limitations are recorded below.

## Conflicts, risks and limits

- D5 deliberately retains two compiler generations despite the PRD's single-pass wording; D6 retains local packaging/persistence exceptions. Source text stays unchanged; no literal zero-difference claim is made.
- Historical CC machine/prose requiredness, network, predicates, ports, budget and exemption shapes are resolved in one current field/schema contract. Historical maturity labels do not override M1 phases. Existing implementation v2.11 declarations need explicit adapter reconciliation.
- Separate producer/verifier contexts do not guarantee independent errors. A schema and a readable view cannot prove scientific truth or actual enforcement.
- Three levels reduce first-reading burden but risk stale summaries; shared links, schema/field checks and diagram-source ownership constrain duplication.
- The old very-condensed experiment remains outside this maintained package and predates the new detail. It must not silently substitute for these current contract inputs.
- Required product Change Records/verification summaries are source obligations outside this design. Existing repository governance must reconcile their realization without inventing duplicate design-owned workflow cards.
- This revision changes documentation only. Runtime code, installed endpoint support, containment and M1 completion remain unestablished by these checks.

## Executed documentation checks — October 7, 2026

- Preserved checkpoint: all 346 baseline file hashes rechecked successfully. Original CC machine/semantic/policy sources and the prior packaged PRD match the checkpoint; the current packaged PRD is byte-identical to the latest download.
- `python reference/validate.py`: PASS for six critical Draft 2020-12 schemas plus shared definitions, 34 indexed example/context records, 12 deliberate invalid cases, exact content references/source-span bounds and selected cross-record gate relationships. Both Intent and Requirements have linked checking/assessment/decision examples.
- Coverage/navigation: 188 current numbered PRD headings, US01–US20, 939 package-local links/fragments, catalog versions/phase associations, required field-summary inventories and the five-document immediate route (4,282 whitespace-delimited words, including diagram text).
- Diagrams: 26 maintained Mermaid blocks rendered to SVG and PNG with Mermaid CLI 12.0.0; source/projection hash closure passes. Contact-sheet inspection covered every maintained view, with enlarged inspection of the system and sidecar access views. A temporary filename collision was corrected and all views regenerated; obsolete projections/index anchors were removed.
- Portability: copied the entire folder with byte verification to an independent validation location and ran the same validator there successfully. Required current references and schema resolution do not depend on repository siblings or online schema retrieval.
- Repository hygiene: `git diff --check` passes. Incoming architecture/product/task entrypoints point to the current PRD and reading route; the reference ignore exception is restricted to this package. Existing task/interface identities remain unchanged.

These checks establish document structure and selected design relationships. Clause/story links are architecture traceability, not proof of every source bullet or runtime behavior. Source support, model/verifier error rates, authorization, durable commit behavior, adapter reconciliation with historical declarations, and actual containment need implementation evidence. The topic-only and scientific-negative records illustrate intended outcomes; the second downloaded ZIP remains an incomplete execution snapshot. No application implementation, commit or push was performed.
