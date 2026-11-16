---
id: muse-workshop-luna-review
status: historical-review-with-user-disposition
source: November 4 user request; luna_workshop_review subagent; evidence/luna-review-receipt.json
last_reviewed: 2026-11-05
next_action: Apply the review findings within the clarified design scope
---

> **Post-presentation revision, November 9:** [[Post-presentation design revision]] is the current conceptual reference. Contract, CC and release image are distinct. Tool/skill CCs support agents; component CCs supply engine functionality. The lab agent now sits outside the experiment Incus instance in a separate management container. Earlier diagrams/specimens below remain historical where they disagree.

> Retained detailed context. Current November6 direction is [[Alignment and decisions]]: immutable submitted images, test-only lab, and Factory-owned knowledge/telemetry. Earlier local-workbench/native-first options are superseded, not implementation evidence.

# Luna adversarial review

The user requested another review with a Luna subagent asking questions. A separate read-only subagent was configured as `gpt-6-luna`, high reasoning, without inherited conversation history. It received this workspace and the relevant CC v2 owner paths. This is a separate model review, not human approval, a runtime test or proof of feasibility. The reviewer could not introspect its own model identity; the configured model is recorded by the coordinating agent.

## Principal finding

**The ontology is a coherent proposed description, but it is not yet an implemented factory construction contract.** Current CC v2 requests do not interpret companion ontology artifacts. The proposal needs an owner, a binding to a concrete factory assignment, a small versioned structure/checker and a known-engine fixture. None requires an unapproved CC v2 extension.

## Prioritized findings

| Priority | Question / finding | Source and counterexample | Minimal action |
|---|---|---|---|
| High | What actually consumes and enforces the ontology? | [Ontology request integration](Ontology%20and%20request%20CCs.md#how-this-fits-the-current-request-protocol), lines 49–60; [CC construction owner](../CC%20and%20Strata%20delivery/CC%20Protocols/02-compiler-and-release.md), lines 40–57. A valid request can coexist with ignored companion metadata | Treat construction guidance as conditional on a domain adapter; name the assignment binding and owner before calling it an operative contract |
| High | Which properties are requirements, design choices, build facts or runtime observations? | [Description meanings](Ontology%20and%20request%20CCs.md#three-linked-descriptions-three-meanings), lines 18–28. A product hash can bind an as-built file while its runtime residency claims are false | Distinguish requirement, tunable, build-derived and runtime-verified properties. Keep actual residency/observations in generation-specific evidence |
| Medium | What precisely travels with the engine? | [Description provenance](Ontology%20and%20request%20CCs.md#three-linked-descriptions-three-meanings), line 28. Shipping desired policy as editable runtime metadata could confuse policy ownership | Ship versioned as-built metadata plus the source-request reference. Preserve desired requirements and owner policy independently in provenance |
| Medium | Are `system.inspect` and `system.conformance` settled interfaces? | [Candidate tools](Tools.md#minimum-capability-contracts), lines 41–42; [construction plan](Ontology%20and%20request%20CCs.md#construction-plan-and-deliverables), lines 84–86 | Keep candidate operation names provisional until the first schema/fixture shows exactly what each validates |

The desired/declaration/as-built/measured split, external standardized benchmark authority and loaded-generation requirement are strengths. Existing counterexamples cover invalid CC fields, copied Qwen/DeepSeek architecture assumptions, unverified 40 GB limits, conflicting pictures, self-certification and unnecessary internal capsule calls. The reviewer found no reason to widen CC v2 or move standardized benchmark/system ownership into this module proposal.

## Questions surfaced to the user

1. **Who owns the inference-domain ontology and companion bundle?** Options: our module team proposes/maintains it with architecture-owner approval; inference-engine team owns it; or protocol team owns an official domain profile. The related technical gap is which actual factory assignment binds the digests.
2. **What may the first optimization change?** Options: placement/cache/buffer reuse with unchanged model precision/computation; also quantization under separate quality evaluation; or engine/standardized benchmark owners define the allowed set. Fixed requirements must not be relaxed by candidate generation.
3. **What anchors the model-free prototype?** Options: pinned Strata manifest/configuration, pinned DwarfStar build/configuration, or defer until Muse baseline selection. Structural plumbing does not establish model correctness or performance.

These questions were presented through asynchronous user input. Their original choices are retained as review history; the November 5 disposition below records the user answers.

## Review disposition — November 5

The user answered the questions: another contributor is assigned the inference-system ontology; our module proposal should illustrate and support it. CC v2 is open to change. The optimization scope follows the broad Strata/DwarfStar engineering spectrum, and prototype selection belongs to later project planning. The named benchmark is removed from the active design; assume an externally supplied standardized benchmark.

The review remains useful for construction-contract and claim/evidence separation findings. Its suggestion to freeze the old schema and select a first prototype is not a current constraint. The newer focused protocol and implementation now use `desired.materials` and `serves`, superseding our root `system` proposal. [Current schema](CC%20schema%20and%20lab%20communication.md) and [implementation status](Implementation%20status.md) record that correction. This earlier reviewer did not review or approve the delivered branch; the coding agent's own summary contains a separate attributed review.
