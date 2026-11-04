# So-what pass: Capability Capsule talk + report

Audience: 1 supervising engineer + co-op students who know LLM agents, not this codebase/papers. Uniform-keep slides are grouped into one row (so-what given once) to fit the word cap; only elements with a real cut/tighten candidate get their own row. Protected by the brief: R1-R6 slides (8, 13, 15), design overview (18), evaluation slides (24, 25) — grouped as "keep, protected" without re-litigating each bullet.

Slide-alone check (asked once, not per slide): all 26 slides communicate their headline claim from title + body alone; SAY restates it and adds one number, mechanism, or caveat, matching the brief. Two exceptions: slide 3 (MCP diagram) is denser than its point needs for an audience that already knows agent tooling; slide 19 (4-tick dispatch diagram) needs the SAY to be followed at 1:00 pace — both flagged below, neither a clear cut.

## 1. Slides

| Slide | Element (quote) | So what | Verdict | Sec |
|---|---|---|---|---|
| 1 | Title + subtitle | orients | keep | 0 |
| 2 | "AI4Research... 79 capsules hand-written" | sets baseline | keep | 0 |
| 2 | "system improves itself... keeping a library" | states the goal | keep | 0 |
| 2 | "built on DeepSeek Harness... everything is a plugin" | repeats slide 1 subtitle near-verbatim | cut | 5 |
| 2 | "system like this already exists (Alita-G)..." | frames the whole talk | keep | 0 |
| 2 | "Plan: background, then each result..., then full design" | pure roadmap, no content | cut | 6 |
| 3 | HOST/Client/Server diagram + labels | shows tool = 1 of 3 primitives | keep | 0 |
| 3 | "Extensions: tasks..., apps..., skills over MCP... illustrative" | none used later; already an IF-ASKED item | cut | 8 |
| 4 | 4 layer boxes + 4 DSH-property boxes | each reused later (versioning, logging, sandbox) | keep (all) | 0 |
| 6 | 4 numbered loop steps + result line | mechanism + the headline number | keep (all) | 0 |
| 7 | 5 table rows (what goes wrong vs AI4Research) | each row = 1 later design rule | keep (all) | 0 |
| 8 | R1-R4 | protected (design rule) | keep | 0 |
| 9 | intro line + 2 bold takeaways | states mechanism + bounds Alita-G's own claim | keep (all) | 0 |
| 10 | 1 bold takeaway | states the headline result | keep | 0 |
| 11 | 3 bullets + result | mechanism + doubled score | keep (all) | 0 |
| 12 | 4 bullets (task, node 1.67, node 2.00, hidden checker) | shows reward hacking is specific, not vague | keep (all) | 0 |
| 13 | 3 table rows + R3/R5 text | protected (design rule) | keep | 0 |
| 14 | 1 bold takeaway | states the headline number | keep | 0 |
| 15 | R6 | protected (design rule) | keep | 0 |
| 16 | 5 gap rows | each row = 1 thing the design must add | keep (all) | 0 |
| 18 | design diagram | protected (design overview) | keep | 0 |
| 19 | bottom bold line | ties the whole diagram together | keep | 0 |
| 20 | THUS line | states why parallel steps don't trigger a build | keep | 0 |
| 21 | THUS line | states the one new check (declared vs observed) | keep | 0 |
| 22 | THUS line | states why similarity can't admit a bad pick | keep | 0 |
| 23 | 4 bullets (version/specialization/new/retire) | defines the 4 outcomes §4.5 uses | keep (all) | 0 |
| 24 | 3 track rows + 4 bullets + THUS | protected (evaluation) | keep | 0 |
| 25 | 6 assumption rows + THUS | protected (evaluation) | keep | 0 |
| 26 | 8-step order list + 6 decision rows | supervisor-facing open questions | keep (all) | 0 |

Untouched slides not listed (1, 5, 6-26 minus rows above) had no element with a weak so-what; their bullets are grouped "keep" in the rows shown.

## 2. Report §1-§6 (tighten/cut only)

| Location | Text (quote) | So what | Verdict | Words |
|---|---|---|---|---|
| Front matter | "This report covers 4 subjects, in the same order as the presentation" + 4-bullet list | pure roadmap; reader can see headings | tighten to: "The report follows the presentation: background, evidence and rules, current state, then design, evaluation and order of work." | 35 |
| §1 para 2 | "Akin to how people learn new skills and become more proficient as they gain experience, agents need to learn and develop themselves as well." | restates prior sentence with a generic analogy | cut | 25 |
| §1 para 3 (after the 9-item list) | "Section 4 addresses each of these: the generalist capsule and selection in Sections 4.1 and 4.4, the decision to build in Section 4.2, implementation and evaluation in Section 4.3, modifying, retiring and managing the library in Section 4.5, handling failure in Sections 4.3 and 4.5, and provenance in the manifest of Section 4.3." | navigational only; the reader reaches Section 4 anyway | tighten to: "Section 4 addresses each of these." | 40 |
| §1.1 | "Optional extensions add long-running tasks, inline interactive apps and skills delivered over MCP" | none of the 3 recur anywhere later in the report | cut | 15 |

All other §1-§6 paragraphs and every table row (Tables 1-8) carry a citation, a number, or a design rule used later; none is a clear cut or tighten candidate.

## 3. Totals if every cut/tighten above is taken

- Slides: 19 seconds saved (of 20:30), 3 elements cut, 0 tightened (all-or-nothing cuts).
- Report §1-§6: 115 words saved across 3 tighten/cut edits (1 tighten also shortens, not just cuts).
- Combined: talk runs about 19 seconds shorter; report body about 115 words shorter, with no loss of any cited claim, number, or design rule.

## 4. Top 5 cuts, surest first

1. Slide 2, bullet "built on DeepSeek Harness, where every skill, tool, MCP server and agent is a plugin" — repeats the slide 1 subtitle almost word for word 45 seconds later.
2. Slide 2, bullet "Plan: background, then each research result and the design rule it leads to, then the full design" — a roadmap line with no claim in it.
3. Slide 3, footer "Extensions: tasks (long-running work), apps (inline UI), skills delivered over MCP... Example servers are illustrative" — none of these 3 extensions is used again; it's already listed as an IF-ASKED fallback in the notes.
4. Report front matter, the "This report covers 4 subjects" bullet list — a table of contents in prose; the section headings already do this job.
5. Report §1, "Akin to how people learn new skills and become more proficient..." — a generic analogy that adds nothing the prior sentence didn't already say to an audience that knows agents.
