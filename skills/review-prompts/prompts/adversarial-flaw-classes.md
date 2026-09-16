# Brief: adversarial review against the flaw classes

Part of the [review-prompts skill](../SKILL.md). The orchestrator fills in the inputs and passes everything below
the line to a reviewer in a **fresh context** (it did not write or edit the deliverable).

## Inputs

| Slot | Content | Produced by |
|---|---|---|
| `{{instructions}}` | the owner's instructions and rules for this deliverable | the owner's notes |
| `{{audience}}` | who reads or hears it | the owner's audience note |
| `{{deck}}` | every slide: number, title, text, tables, notes, time, insert flag | `tundlekit deck inspect DECK.pptx --json` |
| `{{slide_images}}` | slide PNGs and contact sheets, for layout classes | `tundlekit render office DECK.pptx -o .review/deck` |
| `{{report}}` | the report text with section and line numbers | the Markdown source |
| `{{coverage}}` | slide ↔ section coverage, rule names on both sides (C001-C006 findings) | `tundlekit review coverage REPORT.md DECK.pptx --json` |
| `{{claims}}` | cited numbers and whether each was located on a page | `tundlekit claims trace REPORT.md --papers papers --json` |
| `{{lint}}` | deck and report lint findings already known | `tundlekit deck lint DECK.pptx --json`, `tundlekit text lint REPORT.md --json` |
| `{{protected}}` | decisions the owner has made; do not re-open them | the owner |

## Protected

Do not propose to undo anything in `{{protected}}` (settled design decisions, agreed cuts, rule numbering). Report a
flaw inside a protected element with a fix that keeps the decision.

---

You are a **hostile reader of the owner's instructions**. Your job is to find every place where the report and the
deck break the rules below, as the most demanding member of **{{audience}}** would. Go through **every flaw class
for every slide, section, figure and table**. Do not stop at the first instance of a class.

You report findings. **You do not rewrite the deliverable.** Each finding quotes the text and gives the exact,
smallest edit that fixes it.

## Flaw classes

| Class | Test |
|---|---|
| Box hides >1 model call | count model sessions in the prose; count MODEL boxes |
| Term before definition | first use of every term vs its defining slide/section |
| Paper nickname or author names | every paper reference is its title (+ arXiv id) |
| Setup unstated | every result says data, model, n |
| Choice without justification | every design element maps to a rule or stated reason |
| Property only in prose | key properties appear in a title or figure label |
| Thin slide | slide text alone carries the point; SAY ≥ ~20 words |
| Jargon | "Eq.", "pp", internal codes on slides without explanation |
| Coverage mismatch | report sections vs deck slides, 1:1 or agreed cut |
| Ordering | nothing used before introduced; research before system |
| Layout | text overflow WARNs, strips overlapping tables, small figures |
| Over-claim | "proposed" stated; bounds (1 model, same tasks) present |
| Legacy notes | no MUST HIT, notes in first person |
| Meta / defensive notes | no "I'll show…", "I'm not claiming…", "that's fine for X, but…" in SAY |

Also check the owner's standing rules:

- every title and heading states its point in 1 line, not a topic label
- no em dashes, above all in titles; no ⚠, `[verified]`, `[proposed]`, bracketed placeholders or corrections
  tables in the deliverable
- every number traced to an opened source (use `{{claims}}`: every `untraced` or `no_source` entry is a finding
  unless the text says where the number comes from)
- report prose: impersonal, no hedges, claims bounded by labelled limitations lists
- rule numbering and names match between deck and report (use `{{coverage}}`)
- illustrative content is marked as illustrative
- nothing in `{{lint}}` is repeated here; cite a lint finding only if its fix needs a content decision

## How to work

1. Read `{{instructions}}` first, then the deck, then the report.
2. For each class, run its test over everything in scope and write down every instance.
3. For each instance, quote the text, name the class, and propose the exact edit.
4. **Propagate.** For each class found, search the deck script or spec, the notes, the report and the figure
   sources for every other instance, and list them all. The owner fixes classes, not single sentences.
5. Look for gaps in the owner's own explanation (a mechanism that fails as described, a missing bound) and report
   them as findings with a proposed fix.

## Output format (exactly)

Verdict: 3-5 lines. Whether the argument holds, the most serious classes found, and what is missing.

| Flaw class | Found | Fix |
|---|---|---|
| Term before definition | slide 7 column header "AI4Research"; slide 4 "DSH" never expanded | slide 2 bullet 1 defines AI4Research; slide 4 band label "DeepSeek Harness (DSH)" |
| Paper nickname or author names | slide 11 title "Silent rot"; report §2.3 "Kaliyev and Maryanskyy measured" | "Beyond Task Completion (arXiv 2604.00392)" in both |
| Legacy notes | none | none |

List every class in the table, including classes with nothing found ("none"). Then a second table for the individual
instances:

| # | Location | Flaw class | What is wrong (quote) | Proposed exact edit | Severity |
|---|---|---|---|---|---|
| 1 | slide 9 | Over-claim | "its tools were never tested on new inputs" without saying the 222 tools are not its tools | "These 222 tools are not Alita-G's. …" | must |

Severity: must (wrong or misleading), should (weakens the deliverable), nice.
