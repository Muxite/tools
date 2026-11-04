# Q1. Why Alita-G gains 8 points while 96.8% of kept tools score 0

Overnight 2026-09-14. Every number was checked tonight against the file cited. Bare line numbers are those of `papers/2510.23601.txt` (Alita-G, [2]) and `papers/2604.00392.txt` (Beyond Task Completion, [3]).

## 1. The short answer

The 2 numbers were measured on different tools. The 96.8% is 215 of 222 tools written by 3 other tool-making protocols with Claude Haiku 4.5 in the harness of Beyond Task Completion, each replayed on hidden inputs for its own job, and Alita-G's tools were never tested that way. Alita-G's 83.03% is an end-task score on the same 165 GAIA questions its tools were harvested from, and a tool fitted to a question and retrieved again for that question passes there even if it fails on every other input, which is the mechanism [3] gives for task scores staying flat while tools score 0. Alita-G's gain is 13 questions turning right and 0 turning wrong, and 1 case study shows a tool built on one question solving a different one, so some transfer exists but its size is unmeasured. The link between the papers is logical (both keep a tool because the task passed), not empirical, and the experiment that would connect them has not been run.

## 2. The 2 results side by side

| Paper | System whose tools were measured | Benchmark and n | Models | What was scored | Result |
|---|---|---|---|---|---|
| Alita-G [2] | Its own MCP Box, harvested "over the entire validation set" [471; 355] | GAIA validation, 165 questions (never printed; 13 flips over 165 is 7.88 points, equal to 83.03 minus 75.15) | Claude-Sonnet-4 manager, GPT-4.1 web agent [343-347] | Final answers "on the same GAIA validation set" [585] | pass@1 75.15% to 83.03%; tokens 12,305 to 10,394 [Table 1, 381-391] |
| Beyond Task Completion [3] | 222 tools from 3 reimplemented protocols: One-Shot 119, ToolMaker-style 19, CREATOR-style 84 [Table 5, 278-283]; not Alita-G's | EvolveTool-Bench, 99 tasks; 3 seeds by 8 sessions per protocol [37, 173-174] | Claude Haiku 4.5, temperature 1.0 [170-172] | Each tool on a held-out suite for its capability, median 11 inputs [279-284] | 215 of 222 (96.8%) score C=0.00; those sessions still pass 0.31 to 0.34 of verified tasks [283, 288] |

## 3. Why both can be true

The mechanism is [3]'s own paragraph "Why C=0.00 coexists with unchanged TC" [310-325]: the in-session verifier scores "the one call the task needed, an input structurally within the regime the tool was just fit to, so an overfit tool can pass it; the conformance suite draws from the capability's full contract". One-Shot has the highest task completion [Table 3] and 100% silent rot [Table 5].

Alita-G scores on the distribution the agent saw. Verified in Table 6 [606-611], 3 generations: Wrong to Right 13, Right to Wrong 0, MCP calls 2.4 per question and 3.4 on improved questions. A tool fitted to a question and retrieved for that same question would produce every flip with 0 held-out correctness; the data are consistent with that and do not show it. Verified in the case study [623-699, Figs. 2 and 3]: a raw MCP from a harlequin-shrimp paper question is abstracted into `extract_pdf_measurement` and later solves a Freon-12 volume question the baseline got wrong (55 mL against 20 mL). That is 1 instance; the paper does not say how many of the 13 improved questions used a tool from another question. The 3.4 against 2.4 calls is a correlation, not per-tool attribution, since Eq. (5) [233] keeps every MCP from a run whose answer was correct.

## 4. What is not known

- Alita-G's tools were never replayed on held-out inputs; `test` occurs 4 times in the paper, all benchmark testing [`27-`, §1]
- The 96.8% is 1 model, 1 harness, 3 "-style" adaptations [362-369]; rates at Sonnet or larger "could change" [373-375]; a Sonnet pilot shows the pattern on 1 tool, no rate [329-334]
- Born broken against decay: [3] resets its library between sessions [176-177]; decay evidence is Alita-G Table 4, coverage 1.00 to 0.51 [`DATA.md` §4]
- Alita-G reports no seeds, confidence intervals or standard errors for GAIA (text search: none); the gain is 13 questions of 165
- No held-out GAIA split exists in Alita-G, so nothing separates fitted tools from reusable ones
- Whether an abstraction rewrite like Eq. (6) changes the rate is unmeasured; none of the 3 protocols in [3] is Alita-G's pipeline

## 5. If asked in the talk

- Are the 96.8% Alita-G's tools? No: 222 tools from One-Shot, ToolMaker-style and CREATOR-style, Claude Haiku 4.5 [3, Table 5]. Alita-G's tools have never been replayed.
- Are the suites too hard? Hand-written references score 1.00 on all 16 suites, tests were written before any tool existed, and 7 of 84 CREATOR-style tools score above 0, 1 at 1.00 on all 3 seeds [309-325].
- Would Alita-G's tools rot at 96.8%? Unknown. Different model, and [3] says Sonnet-scale rates could differ [373-375].
- Does 83.03% prove the tools work? It proves the answers were right on the questions the tools came from [471, 585]: 13 net questions of 165, no variance reported, 1 case of cross-question reuse [Figs. 2 and 3].
- Does the tool cause the gain? 3.4 against 2.4 calls [2, Table 6] is a correlation, not per-tool attribution.

## 6. What would settle it

Harvest the MCP Box from 1 half of GAIA validation and score both halves, so the held-out half measures reuse and the harvest half measures fitting. Then replay every MCP in the Box on a held-out suite for its capability, with hand-written references as calibration, as [3] did.

## 7. Current wording that overstates or understates

- `REPORT.md` line 124: accurate, but the paragraph comparing the 2 results never says the 96.8% is other systems' tools; only bullet 119 does. Patch `1a` fixes this
- `build_deck.py` lines 251-253, "Agents write and keep tools while solving tasks, as in Alita-G": the slide face never says whose tools the bars are. Patch `1a` adds the line
- `build_deck.py` line 264, "They don't crash": overstates. Mean robustness is 0.52 to 0.54, so about half of adversarial inputs run without crashing [287-290, 300-301]; the paper says "execute cleanly"
- `REPORT.md` line 76 and the deck `ALITA` strip, "165 questions": not printed in the paper; it follows from 13 flips being 7.88 points. Be ready to say so
