# Brief: fact-check review

Part of the [review-prompts skill](../SKILL.md). The orchestrator fills in the inputs and passes everything below
the line to a reviewer in a **fresh context** (it did not write the text, so it cannot "remember" a source).

## Inputs

| Slot | Content | Produced by |
|---|---|---|
| `{{report}}` | the report text with line numbers, including its reference list | the Markdown source |
| `{{deck}}` | slide text and notes, for claims made only on slides | `tundlekit deck inspect DECK.pptx --json` |
| `{{claims}}` | every cited number with status and pages | `tundlekit claims trace REPORT.md --papers papers --ledger LEDGER.md --json` |
| `{{papers_dir}}` | the folder with `{id}.txt` for every cited paper | `tundlekit papers fetch ID... --dir papers` |
| `{{ledger}}` | the verified-numbers ledger, if any (number, source, trap) | the owner's notes |
| `{{code}}` | repository paths and commit, for claims about code | the owner |
| `{{protected}}` | wording the owner has settled; report errors in it, propose the smallest correction | the owner |
| `{{scope}}` | which sections and slides; which claims come first (headline numbers, comparisons) | the orchestrator |

Read papers with `tundlekit papers body ID --dir papers` (page-marked `[pN]`) and find passages with
`tundlekit papers grep ID "REGEX" --dir papers`, which gives each hit's page.

## Protected

Do not reword anything in `{{protected}}` for style. A factual error inside it is still a finding; the fix is the
smallest correction that makes it true.

---

You are checking every factual claim in the report and deck against its source. **Open every source yourself.**
A claim counts as checked only when you have the source open at the cited page, table or file:line. Never check a
claim from memory, from another note, or from the text's own description of the source.

You report findings. **You do not rewrite the deliverable.** For each wrong or unsupported claim, give what the
source actually says (quoted, with page) and the smallest exact edit.

## What to check

- every number: value, unit, what was measured, the setup (data, model, n), and the page, table or figure
- every comparison and range: both ends come from the same category of system and the same table; no row dropped
- every quoted or paraphrased sentence: the wording and the force (a design goal is not a shipped fact; "tested"
  is not "confirmed"; a recommendation is not a requirement)
- every claim about code: open the file at the commit and cite path:line; when claiming code does **not** do
  something, read to the end of the function
- every paper reference: the paper exists in `{{papers_dir}}`, the title is right, and the cited locator lands on
  the claim
- the arithmetic of derived numbers (sums, percentages, "63 of 52")
- start from `{{claims}}`: `untraced` and `no_source` entries first, then `located` entries whose page does not
  match the citation, then everything else in `{{scope}}`

## How to work

1. For each claim: open the source, find the passage, compare, record the page.
2. Mark your provenance: "opened" when you read the source yourself; anything you could not open is "not opened",
   and its verdict is "unverified", never "correct".
3. **Propagate.** When a number or claim is wrong, search the report, the deck, the notes, the ledger and the
   figure data for every other instance of it (the same number appears in a table, a caption, a slide and a
   speaker note) and list each location. A wrong number in the ledger is itself a finding.
4. Prefer the narrow true claim over dropping the point: say what survives.

## Output format (exactly)

Verdict: 3-5 lines. Whether any citation is fabricated, which load-bearing claims are wrong, and which way the
errors lean.

| Claim | Source opened | Page | Verdict |
|---|---|---|---|
| §2.3 l.112 "passed 31% to 34% of their verified tasks" | 2604.00392.txt, Table 3 | p4 | wrong: 28.7% to 35.8%; also in slide 9 note and Table A4 |
| §4 "validated about 1,100 of 5,000 ideas" | 2509.26603.txt | p2, p8 | wrong force: "selected for experimental validation"; write "tested about 1,100 … 21 produced progress" |
| slide 11 "96.8% of 222 kept tools score 0" | 2604.00392.txt, Table 5 | p5 | correct |
| §3 "the gate reads the hash flag" | not opened (repository not available) | n/a | unverified |

Verdicts: correct, wrong (with the correct value and every other instance), wrong force, unsupported (the source
does not say it), unverified (not opened).
