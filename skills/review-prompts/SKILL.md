---
name: review-prompts
description: Reusable briefs for independent reviewers of a report or deck - a so-what pass (keep, cut or merge every element), a first-time-reader pass (where a newcomer gets lost), an adversarial pass over the fixed flaw-class table, and a fact-check pass (every claim against an opened source and page). Each brief has fixed inputs, a protected list, and a fixed output table, and runs in a fresh context that reports findings without rewriting. Says which tundlekit commands produce each input (deck inspect, render office, review coverage, claims trace). Use when a deliverable is built and needs review before it goes out, when dispatching reviewer agents, or when asked for a so-what, readability, adversarial or fact-check review.
---

# Reviewer briefs

4 briefs, 1 reviewer each. Fill in the inputs, hand the brief to a reviewer that has **not** written or edited the
deliverable (a fresh context: a new agent session, or a person), collect the output table, then apply and
propagate the fixes yourself. The reviewer reports; it never rewrites the deliverable.

| Brief | Asks | Output table |
|---|---|---|
| [so-what](prompts/so-what.md) | does every section, paragraph, bullet, row and slide earn its place? | `Element · So what · Verdict` (keep, cut or merge) |
| [first-time-reader](prompts/first-time-reader.md) | where does a reader with only the stated background get lost? | `Where · Confusion · Fix` |
| [adversarial-flaw-classes](prompts/adversarial-flaw-classes.md) | which known flaw classes occur, and where? | `Flaw class · Found · Fix` |
| [fact-check](prompts/fact-check.md) | is every number and claim in an opened source, on the cited page? | `Claim · Source opened · Page · Verdict` |

Run them after the deliverable builds cleanly and the mechanical checks pass (deliverable-review skill, steps 1-3).
Order: fact-check and adversarial first (they change content), then so-what (it cuts), then first-time-reader
on the result.

## Producing the inputs

Give the reviewer text, not binaries. Every brief lists which of these it needs.

| Input | CLI | MCP tool |
|---|---|---|
| deck text: every slide's title, text frames, table cells, notes, time, insert and hidden flags | `tundlekit deck inspect DECK.pptx --json` | `deck_inspect` |
| slide and page images, notes files, contact sheets (for layout and "slides alone" checks) | `tundlekit render office DECK.pptx -o .review/deck` | `render_office` |
| report text | the Markdown source; for a .docx, `tundlekit render office REPORT.docx -o .review/report --backend text` | `render_office` |
| report ↔ deck coverage: which slide covers which section, rule names on both sides | `tundlekit review coverage REPORT.md DECK.pptx --cuts cuts.txt --json` | `review_coverage` |
| every cited number with its status (located, derived, ledgered, untraced, no_source) and pages | `tundlekit claims trace REPORT.md --papers papers --ledger LEDGER.md --json` | `claims_trace` |
| style findings, to exclude from the review (already mechanical) | `tundlekit text lint REPORT.md --json` | `text_lint` |
| paper text for the fact-checker | `tundlekit papers body ID --dir papers`, `tundlekit papers grep ID "REGEX" --dir papers` | `papers_body`, `papers_peek` |

Also give each reviewer:

- **the audience description**: who reads or hears it, what they already know, what they do not (for example:
  "1 supervising engineer, expert, will ask hard questions; 2 colleagues onboarded 1 day before, CS students who
  have built LLM agents; they know tool calling, DAGs, JSON Schema, git; they do not know this codebase or its
  terms"), and hard constraints (English only, time slot, page limit)
- **the protected list**: elements the owner has decided and the reviewer must not propose to cut or reorder
  (for example the design-rule slides, the design overview, the evaluation slides, agreed cuts). The reviewer may
  still report a factual error inside a protected element
- **the scope**: which files, sections or slides, and the word cap for the review

## Rules for every review

- **Fresh context.** A reviewer who wrote the text reads what was meant, not what was written.
- **Findings, not rewrites.** The reviewer quotes the element, names the problem and proposes the smallest exact
  edit. The orchestrator applies edits.
- **Quote, then locate.** Every finding carries a location (slide number, section and line, table and row) and the
  quoted text.
- **Propagate.** For each finding, search the report, the deck script or spec, the notes and the figure sources
  for every other instance of the same problem, and fix all of them. The reviewer lists the other instances it
  saw; the orchestrator searches for the rest (`tundlekit text xref`, plain text search, `tundlekit deck inspect`).
- **Severity**: must (wrong, misleading, or blocks understanding), should (weakens the deliverable), nice.
- **Verdict first.** Each review opens with a 3-5 line verdict, then the table.

## After the reviews

1. Apply must-fix items, then should-fix items, through the build script or spec (never by hand in the built file).
2. Propagate every fix (above), rebuild, re-render, re-run `tundlekit review coverage` and `tundlekit claims trace`.
3. Record: 1 table per review in the plan or handoff notes (`Flaw class · Found · Fix` or the brief's own table),
   what was applied, what was declined and why, and what is left for the owner.
