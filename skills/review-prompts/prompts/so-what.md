# Brief: so-what review

Part of the [review-prompts skill](../SKILL.md). The orchestrator fills in the inputs and passes everything below
the line to a reviewer in a **fresh context** (it has not written or edited the deliverable).

## Inputs

| Slot | Content | Produced by |
|---|---|---|
| `{{audience}}` | who reads or hears it, what they know, what they do not | the owner's audience note |
| `{{deck}}` | every slide: number, title, text, table cells, notes (SAY / IF ASKED), time | `tundlekit deck inspect DECK.pptx --json` |
| `{{report}}` | the report text, with section numbers and line numbers | the Markdown source |
| `{{coverage}}` | which slides cover which sections | `tundlekit review coverage REPORT.md DECK.pptx --json` |
| `{{protected}}` | elements that stay, whatever the review finds | the owner |
| `{{scope}}` | which slides and sections; the word cap for the review | the orchestrator |

## Protected

Do not propose to cut, merge or reorder anything in `{{protected}}`. Typical entries: design-rule slides and their
report paragraphs, the design overview figure, evaluation slides, sections the owner already cut or kept, the
open-questions table. Group protected elements into 1 row each with verdict "keep (protected)". A factual error
inside a protected element is still reported.

---

You are reviewing a report and its presentation for **{{audience}}**. Your question, for **every section,
paragraph, bullet, table row and slide**, is: **so what?** What does this element give this audience that the
argument needs? If there is no answer, the element is cut. If its answer is the same as another element's, the two
are merged.

You report findings. **You do not rewrite the deliverable.** Where you propose a tightened wording, give the exact
replacement text in the Verdict cell; the orchestrator decides and applies it.

## How to work

1. Read the deck once, slide 1 to the end, without going back. Then read the report once.
2. For each element in `{{scope}}`, write its so-what in at most 12 words: what it establishes, defines, bounds or
   decides. "Orients", "states the headline number", "defines the term used on slide 9" are answers.
   "Background", "context" and "interesting" are not.
3. Give a verdict:
   - **keep**: it has a so-what nobody else carries
   - **cut**: no so-what for this audience (roadmaps the reader can see, restated sentences, generic analogies,
     items never used later, meta talk about the talk)
   - **merge**: its so-what duplicates another element; name the other element (a table and a diagram saying the
     same thing become 1 diagram)
   - **tighten**: keep the point, cut words; give the replacement text (counts as keep)
4. Elements whose verdict is plainly keep may share 1 row ("slides 9-12, all bullets: mechanism plus the headline
   number, keep (all)"), to stay within the word cap. Every cut, merge or tighten gets its own row.
5. **Slides-alone check** (once for the deck): can each slide's point be followed from its title and body alone,
   and does the SAY restate it and add a little (a number, a mechanism, a caveat)? List exceptions.
6. **Propagate.** When an element is cut or merged, search the report, the deck notes and the other slides for
   every other instance of the same content (a repeated roadmap, the same analogy, the same restated sentence) and
   list each one in its own row.

## Output format (exactly)

Verdict: 3-5 lines. How much can be cut, where the argument drags, and whether the slides alone carry the talk.

| Element | So what | Verdict |
|---|---|---|
| slide 2, bullet 3: "Plan: background, then each result, then the design" | none: a roadmap the audience sees anyway | cut |
| §1 para 2: "Akin to how people learn new skills…" | restates the previous sentence with a generic analogy | cut |
| slide 13 table + slide 14 diagram | both show which role reads which file | merge into slide 14's diagram |
| §1 para 3: "Section 4 addresses each of these: …" (40 words) | navigation only | tighten to "Section 4 addresses each of these." |
| slides 18, 24, 25 | protected (design overview, evaluation) | keep (protected) |

Then: "Other instances found:" with 1 line per location, or "none".
