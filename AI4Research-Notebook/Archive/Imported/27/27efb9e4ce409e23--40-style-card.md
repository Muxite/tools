# Style card — the user's writing voice

Derived 2026-09-11 from the §1 draft (169 prose words across 7 sentences, plus
three bullet lists). **Small sample — treat as provisional and update it.**
Purpose: let an agent draft report prose the user will recognise as their own.

## Measured

| Feature | Value |
|---|---|
| Mean prose sentence | **24 words** (range 9–35) |
| Prose : list ratio | ~169 prose words carrying **16 bullets** across 3 lists |
| First person | **none** — no "we", no "I", no reader address |
| Hedging vocabulary | **none in sample** — everything declarative |
| Contractions | none |

## The signature: lists carry the load

Prose states a position, then a list does the enumeration. Prose sentences are
long and unhedged; the lists are short, verb-first, and parallel:

> - Exploring the capability space
> - Deciding whether to use any skills
> - Choosing a skill to use and deciding if a new skill should be made

Gerund-led, no terminal punctuation, no sub-bullets. When the user needs to
enumerate, they break to a list rather than extending a sentence.

## Habits to reproduce

- **Triads.** "hand-write, hand-verify, or predict"; "minimizing extra costs,
  prioritizing reliability and recovery, and preventing catastrophic failure."
  Three-part parallel structures appear whenever a point needs weight.
- **Define by function, never by formalism.** "Capability Capsule is a system
  that utilizes X to provide Y and allows Z." Not "a capsule is a tuple of…".
- **One analogy, brief, then dropped.** The human-learning comparison runs a
  single sentence and is never extended. Do not build an extended metaphor.
- **Formal connectives:** "Thus", "Akin to". Not "so", not "like".
- **Slashes for near-synonym sets:** "abilities/tools/skills/MCP",
  "skills/MCPs/tools". Compresses a category rather than listing it.
- **Inline gap markers:** `[footnote this def]` — the user flags a hole and
  keeps writing rather than stopping. Preserve this habit in drafts.
- **Numerals for small numbers:** "merge into 1 abstraction" (not "one").
- **Technical density is high and deliberate.** MCP, A2A, agentic loops are used
  without gloss. The register assumes a reader who builds agents.

## What to avoid

- Hedging that the user did not ask for. The sample has **zero** hedges; adding
  "arguably", "it seems", "to some extent" will not read as their voice.
  Uncertainty is carried by explicit status labels (`[proposed]`), not by
  softened prose.
- First-person plural. Do not introduce "we" — the sample is impersonal
  throughout, describing the system rather than the authors.
- Em-dash asides. The sample uses none; it uses commas and full stops.
- Rhetorical questions in body prose (headings are fine — "What is capability
  capsule?").
- Extended metaphor, scene-setting, or an anecdotal opener.

## ⭐ How the user handles uncertainty — structural, not lexical

**Updated 2026-09-11 from a second sample (406 prose words, mean 23.9 — the
24-word mean held).** The earlier card said "no hedging register observed."
Wrong conclusion from too small a sample. The register exists; it is just not
carried in the prose.

The user states a claim **flat**, then attaches a **labelled limitations list**:

> In GAIA benchmark of real world tasks, Alita-G reports 83.03% pass@1 using the
> generated tool library, relative to 75.15% without the tool library.
> Additionally, token consumption falls -15.5%.
> There are two primary limitations to this info:
> - The tool library is derived from the same validation set as the score is
>   reported on…
> - GAIA totals are not directly comparable between systems…

**So: never soften the sentence. Add the list.** Writing "Alita-G reports a
promising 83.03%, though this may not generalise" is the wrong voice twice — it
weakens the claim *and* buries the limit. The user's form asserts fully, then
bounds explicitly. Same pattern for the two kinds of human approval (numbered
list) and the nine agent capabilities.

⚠ **The risk this creates, and the drafting rule that follows.** Because the
prose register is uniformly assertive, an unmeasured claim reads exactly like a
measured one. The user's own draft produced *"This provides a control where we
know TC=1.0"* — a measurement nobody has taken. **When drafting in this voice,
carry status in an explicit marker or a limitations bullet, never in the verb.**
The flat sentence is correct style; the missing bound is the defect.

## Open — resolve with a second sample

- ~~No hedging register observed~~ — **resolved 2026-09-11**, see the section
  above. It is structural, not lexical.
- No example yet of how the user cites evidence inline, or transitions between
  sections.

## Third sample (rev0 full draft, measured 2026-09-15)

Measured the full `Report rev0 (original, before Claude edits).docx`, the un-edited user draft, not just the two prior excerpts (those came from this same document). Sample: 30 prose sentences, 587 words, plus 6 lists, 3 pseudo-headings, and 2 unfinished placeholder lines excluded from counts. `rev2.txt` (Claude-expanded) was checked only to confirm which rev0 sentences are genuinely the user's: the bare `2604.00392` citations became `[2]`/`[3]` in rev2, confirming the numeric-ID habit below is the user's own, not an editing artifact.

| Feature | Value |
|---|---|
| Sample | 587 prose words / 30 sentences |
| Mean sentence length | 19.6 words (range 5-42) |
| Sentence-initial connectives | 6/30 (20%): Thus, Akin to, Then, Additionally, While, When |
| First person | 1 sentence, 2 uses of "we"; the same TC=1.0 sentence already flagged as a defect |
| Hedges / contractions / em dashes / semicolons | 0 of each |
| Colons introducing lists | 6, mostly "There are N ... :" |
| Numerals vs. spelled-out | split by function, not size (below) |
| List terminal punctuation | mixed by list type (below) |
| Triads | 2, both in one paragraph, not repeated elsewhere in the draft |

**Confirmed:** triads, slash synonym-sets, "Thus"/"Akin to", zero hedges, contractions and em dashes, define-by-function, structural claim-bounding, rhetorical questions confined to headings.

**Refined:**
- The 24-word mean was an artifact of the two prior excerpts; the full draft's mean is 19.6 (range 5-42) because short list-introducing and transitional sentences pull it down. Treat 15-25 words as the working band.
- Connectives are broader than "Thus/Akin to": add "Then", "Additionally" as sentence openers, and "While"/"When" as subordinate-clause openers.
- Numerals vs. spelled-out is not about number size: numerals mark technical or measured quantities (1 abstraction, 2 clock loops, 11/17 capabilities, 83.03%, TC=1.0); spelled-out words mark discourse quantifiers ("two limitations", "two types of human approval").
- List item form is not uniformly gerund-first with no punctuation: that holds for noun-phrase action lists only. Full-sentence list items (human-approval types, Alita-G limitations) end in periods. A third form exists too: term colon gloss ("Skills: how to reason and perform a workflow").

**Resolved from "Open" above:**
- Inline citation: a named system or paper takes a verb ("Alita-G reports 83.03%..."); other work is cited as a bare identifier used as subject or possessive, no author names, no "et al." ("2604.00392 was testing...", "2604.00392's 96.8%... failure rate").
- Section transitions: the first sentence of a section states the subject's function, mechanism, or current status directly, never a framing sentence like "this section discusses...".

**Exemplars (verbatim), 3 marked claim-bounding [B]:**
> Capability Capsule is a system in AI4Research that utilizes the DeepSeek Harness to provide additional abilities to agents and allows agents to continuously create, verify, update, and use abilities, thus creating a self-improving agent system.
> Akin to how people learn new skills and become more proficient as they gain more experience, agents will need to learn and develop themselves as well.
> As agentic loops get longer, reaching days and weeks, there are more abilities/tools/skills/MCP that are required for the agent to work effectively, far beyond what humans can hand-write, hand-verify, or predict the agent will need.
> In GAIA benchmark of real world tasks, Alita-G reports 83.03% pass@1 using the generated tool library, relative to 75.15% without the tool library.
> [B] There are two primary limitations to this info:
> [B] Alita-G is offline and has a clear order, general first, specialist later. While this is good for short term runs that do not need new plugins to adapt to situations, and good for concurrency handling, it does not work for AI4Research.
> This is similar to what 2604.00392 was testing, and allow avoiding 2604.00392's 96.8% agent-authored tool failure rate.
> The build decision is held by the abstraction agent, thus avoiding the AllocBench first-time-overcommit issue.
> 2 clock loops, connected by the library that they read from and write to.
> [B] There are two types of human approval:

**Drafting rules for agents:**
1. Open a section with the subject's function or current status, not a framing sentence ("this section covers...").
2. Default to 15-25 words per sentence; allow one longer definitional sentence per paragraph, not more.
3. Bound a claim right after asserting it: "There are N limitations to this:" plus a list, never a hedge word.
4. Never hedge in the verb (no arguably/seems/may/might/perhaps/somewhat); carry uncertainty in a marker or a bullet instead.
5. Use numerals for technical or measured quantities; spell out small numbers used as discourse quantifiers ("two limitations").
6. Cite a named system or paper with a verb ("X reports..."); cite other work as a bare identifier used as subject or possessive, not an author name.
7. Compress a near-synonym set with a slash ("skills/MCPs/tools") instead of listing it in prose.
8. Match list form to content: gerund/noun-phrase items take no terminal punctuation; full-sentence items end in periods; term lists read "Term: gloss."
9. Save triads for one point that needs rhetorical weight; do not force one into every list.
10. No em dashes, semicolons, or contractions; no first-person "we" except inside the already-flagged defect sentence.
