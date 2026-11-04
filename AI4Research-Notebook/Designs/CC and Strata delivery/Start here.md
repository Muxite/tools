---
id: cc-strata-method
status: proposed
source: Sources/Prompts/2026-11-02-cc-strata-methodology.txt
last_reviewed: 2026-11-02
next_action: Walk the existing Strata baseline through the schema register before drafting slides
---
# Production plan for the CC feature workshop

**Decision for November 3.** Can a feature owner bring a pinned inference engine, expose its useful operations as capabilities, have the Software Factory build a candidate and recover enough independent lab evidence to decide the next build? The first example is Strata on one DGX Spark. A credible negative result completes the loop.

Read [contract choices](Contract%20choices.md), [agent assignments and folder specification](Production%20assignments.md), then [the feature talk](Feature%20talk.md). This folder is the production plan. The finished implementation handoff and the shorter feature deck are its outputs.

## The example all authors follow

| Owner | Input | Output the next owner consumes |
|---|---|---|
| CC Factory | Prepared Strata checkout, engine and model requirements, qualified hardware profile | A candidate category package containing callable build, qualify or measure operations, their typed ports, effects, checks and dependency pins. Existing admission decides which operations enter the pool. |
| Software Factory | Research objective, admitted CCs, baseline source, target and build recipe | A specific candidate engine and weight-pack reference, provenance and comparison request. Its own build pipeline can be distributed as a CC bundle. Each invocation produces a separately identified product. |
| Central Lab Manager | Requested comparison, budget, release pins, current host inventory | A fenced lease, bound inputs and private execution environment. It owns allocation, network policy, stop and restore. |
| Lab Agent and benchmark | Lease-scoped instructions, immutable products and fixtures | Raw per-arm measurements and failure evidence. The benchmark evaluates results against frozen criteria. The agent can vary only settings allowed by the assignment. |
| RSI and feature owner | Independent verdict, original recipe and signed evidence references | A proposed change to the factory recipe, a rebuilt product and a new comparison. The opener carries a reviewed PR through merge and closure. |

**First run.** Package and replay the upstream baseline; check that the wrapper preserves its output and failure behavior. **Second run.** Change one expert storage representation while preserving logical tensor identity, routing, model, fixtures and benchmark settings. Keep disk bytes, peak shared memory, prefill, decode and quality as separate outcomes. Do not require the compression idea to succeed for the CC integration to pass.

## Source precedence and scope

The November 2 meeting and follow-up direct this proposal. Central AI4R stays outside the sandbox. Reviewed research code, accidental-breakage isolation and monitored egress are the pilot threat model. The earlier whole-lab deck supplies recovery and observability requirements; its writable in-lab AI4R service conflicts with this pilot. Record the delta on the new lab overview. M1 remains the implementation baseline, M2a is an existing design proposal and its seven Stage 1 exits retain their own scope. The November workshop JSON and diagrams are candidate designs. Reconcile field meanings before any promotion.

Start at [[Designs/ai4r_m2a/README]], [[Designs/Inference Engine Software Factory - Design Impact]], [[Designs/Superagent and Strata - Source Review]], [[Designs/Capability Capsule Factory Feature]], [[Designs/Sandbox Lab Design]] and [[Presentation Library/Presentation Guide]]. The previous 13-slide workshop package under the workspace outputs is the detailed reference for this short feature talk.

## Production order

1. **First 30 minutes, editor and CC owner.** Freeze the decision, source pins, one candidate, identifiers and handoff boundaries. Identify each disagreement explicitly. Release a one-page brief to the contributors.
2. **Next 60–90 minutes, parallel work.** CC and labs owners map native contracts and produce valid/invalid case pairs. Evidence owner traces the Strata build and benchmark paths. Slide owner sketches from the same handoffs. Give each file exactly one writer.
3. **Next 45 minutes, integration.** Trace one successful run and one stale or failed attempt across both folders. Resolve who enforces each check and who can publish. Freeze the illustrated records; generate slide excerpts from them.
4. **Final 30–45 minutes, independent read-through.** Review the exported folders with only their contents, render the deck, rehearse and fix the highest-impact discrepancy first. These are workshop preparation estimates. Runtime qualification has its own backlog.

**Stop rule.** Defer a topic if it changes neither the two Strata runs, a trust boundary, the resource budget nor a required interface. Keep one extension row for Mac/Metal, Muse Spark and robotics to check generality. Reopen orchestration choices only for a named unmet requirement.

## November 2 design revision

The top-level Strata checkout and revised CC vision now have two detailed design entrypoints: [Capability capsules](Capability%20capsules/Start%20here.md) and [Research labs](Research%20labs/Start%20here.md). Use these for the proposed image-backed template and application-boundary savepoint. The earlier workshop schema is retained as a requirements example.

## November 3 single-CC workshop

[[Designs/CC and Strata delivery/CC and Software Factory/README|CC and Software Factory]] and [[Designs/CC and Strata delivery/Strata Research Lab/README|Strata Research Lab]] now own the single-CC proposal. Factory briefs, products and evaluations are companion records. The November 2 image template and November 3 interchange forms remain historical design inputs.

## November 3 protocol specification

[CC Protocol v2](CC%20Protocols/README.md) defines the current v2 declaration, native/image/agent bindings, call protocol and provenance model. The workshop records remain the source for migration and comparison.
