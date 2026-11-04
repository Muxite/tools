---
id: presentation-production-review
status: active
source: Tundle code/tundlekit/skills/deck-builder/SKILL.md; tundle AI4Research deck plans and review notes
last_reviewed: 2026-10-21
next_action: Select the authoring workflow that matches the next requested deliverable
---
# Presentation production and review

## Author from a clear source of truth

If the deck uses TundleKit, author the JSON spec as the source of truth and rebuild the editable PowerPoint from it. Carry hand edits back into the source spec before rebuilding. If the deck uses another native workflow, preserve its source format and build path rather than introducing a duplicate format. Keep figures, source notes, the claim ledger, and the rendered deck version-linked.

## Suggested sequence

1. Complete [[Templates/Presentation Brief]] and draft the one-sentence argument.
2. List the slide takeaways; check that they support the argument in order.
3. Attach the primary evidence and source to each factual slide; write visible qualifications where needed.
4. Draft the speaker script and timing. Keep details the audience does not need on-screen in speaker notes.
5. Run the native linter and correct all errors. Explain any warning left open.
6. Build the editable deck and inspect the build report for overflow or budget warnings.
7. Render the full deck, inspect every slide and the whole-deck contact sheet at presentation size, and run the [[Templates/Review Checklist]].
8. Check that notes and citations survived rendering, then package the presented deck with its source, sources, evidence, and review record.

The installed TundleKit guide also provides `deck inspect`, `deck diff`, `review coverage`, `deck pack --check`, and hyperlink validation. Use the commands only when authoring in that project. Its rules about backup before editing an existing deck, rendering and reviewing every slide, and keeping the source spec authoritative are project-specific tooling requirements.

## Separate required checks from useful extras

| Stage | Minimum useful review |
|---|---|
| Argument | Clear audience, purpose, one argument, useful sequence, open questions visible |
| Evidence | Claims trace to sources; result labels and limitations are accurate |
| Design | Hierarchy, purposeful space, readable data, consistent visual encoding |
| Build | Linter and build warnings checked; no overflow |
| Delivery | Rendered slides inspected; timing rehearsed; source and shown version retained |

Use [[Templates/Review Checklist]] to record pass, change made, or a concrete reason a check does not apply.
