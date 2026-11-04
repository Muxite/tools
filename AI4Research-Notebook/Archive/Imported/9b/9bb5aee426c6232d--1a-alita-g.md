# Patch 1a. Alita-G against the 96.8%: whose tools were measured

Written overnight 2026-09-14. Companion to `notes/overnight/Q1-alita-g-vs-96-percent.md`. Line numbers are those of the files as read tonight; anchors are verbatim. Every number is checked in Q1 §2.

Numbering: all 17 tables in `REPORT.md` are numbered, and there is no unnumbered table to copy. Option A (below) inserts the table in §2.3 as Table 2, which renumbers Tables 2 to 6 in the body and 4 deck footers. Option B puts the same table in Appendix A.2 as Table A2, which renumbers only 5 appendix captions and no body or deck reference. Apply A or B, not both.

## Option A. Table in §2.3 (as requested)

### A1. Lead-in, table and caption, right after the §2.3 heading

```
FILE: notes/report-capsules/REPORT.md  (lines 110-112)
ANCHOR (old, verbatim):
### 2.3 Beyond Task Completion: 96.8% of kept tools fail tests of their own job

Beyond Task Completion [3] asks how well self-made tools work on inputs beyond the task that produced them,
NEW:
### 2.3 Beyond Task Completion: 96.8% of kept tools fail tests of their own job

The result below and the Alita-G result were measured on different tools, benchmarks and models (Table 2).

| Paper | Tools measured | Benchmark | Model | Scored on |
|---|---|---|---|---|
| Alita-G [2] | Its own MCP Box, harvested from the GAIA validation set | GAIA validation, 165 questions | Claude Sonnet 4 with GPT-4.1 | The final answer on the same 165 questions [2, Table 1] |
| Beyond Task Completion [3] | 222 tools from 3 other tool-creating protocols (One-Shot, ToolMaker-style, CREATOR-style) | EvolveTool-Bench, 99 tasks, 3 seeds by 8 sessions | Claude Haiku 4.5 | Each tool on held-out tests of its own capability, median 11 inputs [3, Table 5] |

*Table 2. The 2 results of Sections 2.1 and 2.3 measure different tools on different inputs.*

Beyond Task Completion [3] asks how well self-made tools work on inputs beyond the task that produced them,
```

### A2. The flat sentence, in the paragraph that compares the 2 results

```
FILE: notes/report-capsules/REPORT.md  (line 124)
ANCHOR (old, verbatim):
The same mechanism bounds the Alita-G result. Alita-G reports its gain on the same GAIA questions its tools were harvested from.
NEW:
The same mechanism bounds the Alita-G result. The 96.8% was measured on tools written by 3 other protocols, and Alita-G's own tools were never replayed on held-out inputs. Alita-G reports its gain on the same GAIA questions its tools were harvested from.
```

The sentence "Thus, the evidence on why Alita-G improved points both ways, ..." later in the same paragraph is kept unchanged. Bullet line 119 ("Alita-G's rule was not tested directly, since its own tools were never replayed") now overlaps A2; keep it, since the list bounds the 96.8% and A2 bounds the comparison.

### A3. Renumbering forced by A1 (every later report-table reference)

Paper-table citations such as `[2, Table 4]`, `[3, Table 5]`, `[6, Table 1]`, `[4, Table A1]` do not change. Only these do:

```
FILE: notes/report-capsules/REPORT.md
line 162:  (Table 2)                         -> (Table 3)
line 170:  *Table 2. Outcome-only judgment   -> *Table 3. Outcome-only judgment
line 186:  (Table 3)                         -> (Table 4)
line 196:  *Table 3. What the current code   -> *Table 4. What the current code
line 573:  The 5 gaps of Table 3,            -> The 5 gaps of Table 4,
line 204:  (Table 4).](../report-general/    -> (Table 5).](../report-general/
line 215:  *Table 4. The design rules        -> *Table 5. The design rules
line 242:  (Table 5). Thus, the figures      -> (Table 6). Thus, the figures
line 252:  *Table 5. Proposed roles          -> *Table 6. Proposed roles
line 336:  [3] (Table 6).                    -> [3] (Table 7).
line 344:  *Table 6. Evaluation tracks.*     -> *Table 7. Evaluation tracks.*

FILE: notes/report-capsules/deck-src/build_deck.py  (source footers)
line 331:  "Capsule report §2.7, Table 2; Table 4"   -> "Capsule report §2.7, Table 3; Table 5"
line 401:  "Capsule report §4, Fig. 8; Table 4"      -> "Capsule report §4, Fig. 8; Table 5"
line 437:  "Capsule report §4.2, Fig. 10, Table 5"   -> "Capsule report §4.2, Fig. 10, Table 6"
line 503:  "Capsule report §5, Table 6"              -> "Capsule report §5, Table 7"
```

Line 206 of the deck ("Capsule report §2.2, Table 1") is unchanged. Other notes that quote report table numbers were not checked tonight.

## Option B. Same table in Appendix A.2, no body renumbering

### B1. Table before Table A2

```
FILE: notes/report-capsules/REPORT.md  (lines 461-463)
ANCHOR (old, verbatim):
### A.2 Beyond Task Completion [3]

| Protocol | Tools | Mean correctness | Silent rot |
NEW:
### A.2 Beyond Task Completion [3]

The 96.8% was measured on tools written by 3 other protocols, and Alita-G's own tools were never replayed on held-out inputs (Table A2).

| Paper | Tools measured | Benchmark | Model | Scored on |
|---|---|---|---|---|
| Alita-G [2] | Its own MCP Box, harvested from the GAIA validation set | GAIA validation, 165 questions | Claude Sonnet 4 with GPT-4.1 | The final answer on the same 165 questions [2, Table 1] |
| Beyond Task Completion [3] | 222 tools from 3 other tool-creating protocols (One-Shot, ToolMaker-style, CREATOR-style) | EvolveTool-Bench, 99 tasks, 3 seeds by 8 sessions | Claude Haiku 4.5 | Each tool on held-out tests of its own capability, median 11 inputs [3, Table 5] |

*Table A2. The 2 results of Sections 2.1 and 2.3 measure different tools on different inputs.*

| Protocol | Tools | Mean correctness | Silent rot |
```

### B2. Flat sentence in §2.3, pointing at the appendix

```
FILE: notes/report-capsules/REPORT.md  (line 124)
ANCHOR (old, verbatim):
The same mechanism bounds the Alita-G result. Alita-G reports its gain on the same GAIA questions its tools were harvested from.
NEW:
The same mechanism bounds the Alita-G result. The 96.8% was measured on tools written by 3 other protocols, and Alita-G's own tools were never replayed on held-out inputs (Table A2). Alita-G reports its gain on the same GAIA questions its tools were harvested from.
```

### B3. Renumbering forced by B1 (captions only; no body line cites A2 to A6)

```
FILE: notes/report-capsules/REPORT.md
line 470:  *Table A2. Share of preserved tools   -> *Table A3. Share of preserved tools
line 480:  *Table A3. Verified task completion   -> *Table A4. Verified task completion
line 502:  *Table A4. SkillsBench                -> *Table A5. SkillsBench
line 524:  *Table A5. Share of tool commitments  -> *Table A6. Share of tool commitments
line 543:  *Table A6. What each system checks    -> *Table A7. What each system checks
```

## Deck, slide 9 (Beyond Task Completion)

The slide face never says whose tools the bars are. This adds 1 bold takeaway line under the existing one, using the file's own `point()` helper (`d.tb`, bold, ink 202020). The chart loses 0.25 in of height to make room; the checker in `deckkit._check` passes (second line: 1 line at 17 pt, ends at 6.97 in, footer at 7.02 in).

```
FILE: notes/report-capsules/deck-src/build_deck.py  (lines 256-260)
ANCHOR (old, verbatim):
          hl_color=RED, y=3.1, h=3.05)
point(s, "They run cleanly but give wrong answers on inputs they were not built from. The task checks only the "
         "input a tool was fitted to, so it still passes.", y=6.2, size=18)
NEW:
          hl_color=RED, y=3.1, h=2.8)
point(s, "They run cleanly but give wrong answers on inputs they were not built from. The task checks only the "
         "input a tool was fitted to, so it still passes.", y=5.92, size=18)
point(s, "Alita-G was scored on the questions its tools came from; its tools were never tested on new inputs.",
      y=6.6, size=17)
```

(18 words.) Matching SAY tweak, same slide:

```
FILE: notes/report-capsules/deck-src/build_deck.py  (lines 264-267)
ANCHOR (old, verbatim):
"they give wrong answers on inputs they weren't built from, and a task only checks the input the tool "
            "was fitted to. So how did Alita-G gain 8 points? Its tools came from the same GAIA questions it was "
            "scored on, the kind of input a fitted tool can still pass. "
NEW:
"they give wrong answers on inputs they weren't built from, and a task only checks the input the tool "
            "was fitted to. So how did Alita-G gain 8 points? First, these are not Alita-G's tools, and nobody has "
            "tested its tools this way. Second, its tools came from the same GAIA questions it was "
            "scored on, the kind of input a fitted tool can still pass. "
```

Optional, same SAY, line 264: "They don't crash" -> "They run". Mean robustness is 0.52 to 0.54, so they run without crashing on about half of adversarial inputs [2604.00392.txt, 287-290, 300-301]; "don't crash" overstates.

Time: the SAY gains about 15 words; leave TIME at "1:05" or set "1:10".
