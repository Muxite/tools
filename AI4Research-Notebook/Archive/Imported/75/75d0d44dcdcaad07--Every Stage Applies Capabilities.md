**Muk's scope decision, 2026-09-23, in his words: "this does not mean the whole workflow becomes a cap
cap itself, but it means each stage can apply capabilities."**

`intent → IntentIR` is the *work* the intent stage does, and that work is a capability.
`intent → IntentIR → faithfulness` is several capabilities chained, and because that chain runs almost
every time, it is worth merging into one capsule ([[Overlap and Merge]]). Each part is still tested
individually, so each stays reusable elsewhere.

> **The unit is the work a stage does, not the stage.**

The workflow keeps its shape: stages, ordering, scheduling and gates all stay exactly where they are.
What changes is that a stage's work is supplied by a declared capsule instead of being hardcoded.

## This changes answer (c)

The previous design said CC lives at **three** stages — planning, freeze and dispatch — and that
"intake, intent and requirement compilation never see capabilities" (`SCHEMA.md §0.5`,
`kb/repos/ai4research-workflow.md:5`). **That line is superseded.** Every stage that does work picks,
binds and runs a capsule. Planning, freeze and dispatch remain special only in that they are where CC's
*control* acts. See [[Position in the Pipeline]].

## Say the boundary before anyone else does

The supervisor ruled on 2026-09-18 that **"AI4Research is not going to be a CC."** This proposal is not
that claim and must not be allowed to resemble it. One line, early, in Muk's own framing:

> The workflow does not become a capsule. Each stage *applies* capabilities.

## Why this is the right scope

- **It makes the merge system self-demonstrating.** The intent chain runs almost every sprint, so it
  carries the highest edge support in the system — the first candidate the merge algorithm would ever
  propose. It replaces the abstract A-B worked example: it is real, and its frequency is obvious to
  everyone in the room.
- **It makes RSI uniform.** One mechanism improves everything — a research operator, a stage's work, a
  merged chain — with no special case, degenerate n = 1 capsules included. See [[Self-Improvement]].
- **It costs nothing in the schema.** A stage's capsule uses the same fields; the merged chain uses the
  set case (`members[]` + `structure`) already scheduled for M4 in [[Milestone Ladder]].

## The honest cost

Work the workflow depends on to run at all now comes from the library, which **widens the blast radius**:
a bad admission could degrade intent compilation, not only one research node. Two containment rules, both
already in the schema:

- work the workflow cannot proceed without is **`certified` only** — never provisional, never bound to a
  generalist, never `exempt`;
- the gate stays protected (§4.16.4), so the thing that would catch a bad capsule is never itself one.

What is and is not allowed to be a capsule is [[The Ceiling]]. Impacts on each part of the workflow are
in [[Impacts on the Workflow]].

Related: [[Capability Capsule]], [[Open Questions]], [[Milestone Ladder]].
