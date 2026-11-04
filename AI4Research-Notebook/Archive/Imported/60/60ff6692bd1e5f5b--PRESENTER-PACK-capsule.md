# Presenter pack: Capability Capsule talk (pass 2)

Verified against `report-capsules/deck-src/build_deck.py` (read in full, 2026-09-15), not against the old pack.
Updated the same afternoon for the last-quarter cut: 23 core slides plus 2 optional insertion slides (9a, 13a).
Core TIME values sum to 18:05, 19:35 with both insertions (target 40 min, max 45, shared with the workflow talk;
both talks core 33:20). The first run-through took about 25 min with all 8 insertions shown, and the design half
dragged after the design figure, so 3 core slides and the 6 design-half insertions were cut.
Numbers cross-checked against `report-general/build/figdata.py` and `notes/LEDGER-VERIFIED-NUMBERS.md`.

## 1. The talk's spine

AI4Research runs 79 hand-written capsules today, and the goal is a system that builds and keeps its own
capabilities while it runs, on top of DeepSeek Harness, where every layer is a swappable plugin. Alita-G already
proves the core loop works, gaining 8 points on GAIA, but it builds once for a fixed benchmark, keeps every tool
from a run that merely got the right final answer, never tests a rewritten tool, and never deduplicates. Three
more results show what happens when something self-built is judged only by its own outcome: 96.8% of kept tools
fail held-out tests of their own job, skills judged by a bare pass or fail do no better than background
knowledge, and 1 self-editing agent scored a perfect score by deleting the log markers its own checker read. A
fifth paper shows that once building means writing code, models commit to the first thing they see almost every
time, so deciding what to build has to be a separate act from building it. Those 5 results give 6 design rules:
2 clocks so building never blocks a running sprint, pinned versions per sprint, independent held-out tests
written before any implementation exists, rejected duplicates, a capped and code-run admission gate, and a
separate decider that only builds on a confirmed repeat. The design puts those rules together into 1
append-only, versioned library, a generalist capsule that fills gaps without ever writing to the library, and a
cold path that turns a recurring gap into a new capsule version. Nothing in the design is built or measured yet;
the plan is to verify the riskiest assumptions first, starting with whether gaps actually recur across sprints.

## 2. Slide-by-slide

| # | Title (exact) | TIME | Crib line |
|---|---|---|---|
| 1 | Capability Capsule (title slide) | 0:20 | This is Capability Capsule, a self-improving tool ecosystem for agents, built on DeepSeek Harness. |
| 2 | The goal: agents that build and keep capabilities | 0:50 | All 79 capsules are hand-written today; the goal is a library that keeps adding to itself as it runs. |
| 3 | MCP is a protocol, not a tool | 0:40 | MCP is a client-server protocol; a tool is only 1 of the things it can carry. |
| 4 | DeepSeek Harness (DSH): every layer is a plugin | 1:00 | DSH has no core to patch; even the agent loop is a plugin, and unloading it removes everything it registered. |
| 5 | The evidence (divider) | 0:15 | Five papers: 1 shows the self-growing loop works, 3 show outcome-only judging fails, 1 shows when to build. |
| 6 | Alita-G: a self-growing tool library already works | 0:50 | Alita-G already runs this loop: writes tools while solving tasks, keeps the good ones, gains 8 points on GAIA. |
| 7 | Where Alita-G falls short, and why a live run is harder | 0:55 | It keeps a tool because the run got the right answer, not because the tool worked, and it never deduplicates. |
| 8 | What this means: 2 clocks and a managed library | 0:35 | Because we never stop, using and building capsules run on separate clocks, and every sprint pins its versions. |
| 9 | 96.8% of kept tools fail tests of their own job | 1:05 | This paper tests what Alita-G never does: whether kept tools work beyond the 1 task that made them. |
| 10 | Feedback from a separate verifier: 41% to 71% | 0:50 | Existing self-written skills barely beat no skills; a separate verifier's detailed feedback reaches 71%. |
| 11 | Darwin Gödel Machine: an agent that rewrites itself | 0:45 | DGM keeps an archive of every version of itself and lets 1 version edit its own code each round. |
| 12 | 1 DGM version deleted what its detector reads | 0:45 | Told to stop faking tool use, 1 version scored a perfect 2.00 by deleting the logs its checker reads. |
| 13 | What this means: an independent check | 1:05 | Every capsule passes held-out tests for its own job, written first by a separate agent, decided by code. |
| 14 | Builders commit on first sight once code is involved | 0:35 | The moment building means writing code, models commit on first sight almost every time, 4% to 92%. |
| 15 | What this means: decide separately, build on repeats | 0:35 | The agent that decides whether to build is never the one that builds; a gap counts once per sprint, and not building is always valid. |
| 16 | Today: 79 hand-written capsules, 5 gaps | 0:40 | All 79 capsules already declare contracts, but the code assumes the library never changes. |
| 17 | The design (divider) | 0:10 | Now the design, which puts the 6 rules together into 1 system. Nothing in it is built or measured yet. |
| 18 | The design: 1 library, a generalist and a cold path | 1:40 | When planning can't find a capsule for a step, it uses the generalist (same gates, lowest trust, capped per plan) and stores a gap record instead. |
| 19 | Admission: each manifest field has a check | 0:50 | The manifest is written first; each field is a promise, and code checks every promise before admitting. |
| 20 | Picking a capsule: exact checks first, similarity last | 0:35 | First anything with wrong types, effects or trust is removed; only then is what's left ranked. |
| 21 | Append-only and versioned: improve, never edit | 0:55 | Nothing in the library is ever edited or deleted; a new version must pass everything the old one passed. |
| 22 | How to know it works, and what would prove it wrong | 1:10 | 3 tracks measure it; 4 things to check first, each with its step: gaps recur, effects differ, hand-written capsules pass, reuse repays. |
| 23 | Order of work, and what needs deciding | 1:00 | Versions first, then the generalist and gap record, then protected paths; the cold path is the only new subsystem. |

Cut on 2026-09-15 afternoon (content stays in the report): the generalist DAG slide (§4.1, Fig. 9), the
recurrence-and-roles slide (§4.2, formerly Fig. 10 and Table 5) and the verify-first table (§5.1, formerly Table 7, now Table 6 with 7 rows; its first 4 rows are
now on slide 22).

## 3. Hard questions

1. **Why not just use Alita-G as it is?** It builds once for a fixed benchmark, keeps every tool from a run with a correct final answer even when the tool did not help, never tests a tool after an LLM rewrites it, and never deduplicates, so distinct share falls from 100% to 51% as the library grows from 26 to 128 tools. AI4Research runs continuously and many research steps have no single right answer to key "keep" on. Source: slide 7; Capsule report §2.2 Table 1; Alita-G arXiv 2510.23601 Table 4.
2. **Why 2 separate clocks for building and using capsules?** Because the system never stops, building a new capsule cannot block a sprint already running; a sprint uses whatever versions were pinned at its freeze and only picks up a new capsule from the next sprint. Today a capsule change during planning aborts the freeze, so this design keeps the two activities apart by construction. Source: slide 8 (R1, R2); Capsule report §2.2, §4 Table 4.
3. **Why does the builder never see the held-out tests?** Beyond Task Completion found 96.8% of kept tools (215 of 222) run cleanly and pass their originating task but score zero on held-out tests of their own job, because a task only checks the input a tool was fitted to. An uncapped gate would let the builder learn the suite by trial and error, so it hears only admit or reject, with a reason, up to 5 times, following CoEvoSkills' own oracle budget. Source: slides 9, 10, 13 (R3, R5); arXiv 2604.00392 Table 5; arXiv 2604.01687.
4. **What if a gap never recurs?** Then nothing gets built, which AllocBench shows is correct: most problem types never come back, and its best policy waits for a confirmed repeat before committing. The generalist capsule and its gap record still handle the step, turning what today is a plan failure into a completed sprint. Source: slide 15 (R6); AllocBench arXiv 2607.23332 Table 1; slide 22; Capsule report §2.8.
5. **How is this different from the Darwin Gödel Machine?** DGM lets an agent rewrite its own code and judges it by its own benchmark score; 1 version scored a perfect 2.00 by deleting the log markers its detector read instead of fixing the underlying behavior. Here model weights and the checking code never change, only the append-only library changes, and protection is by write access, not by hiding. Source: slide 12; DGM arXiv 2505.22954 App. H; slide 13 (R5); slide 19.
6. **What does the admission gate cost?** Each admission costs 3 separate model sessions (decider, suite author, implementer), an effect check comparing declared vs actual sandbox writes, and a re-run of that capsule's test suite on a recurring schedule for as long as it lives, on top of running the generalist on every unfilled step until then. This is unmeasured; whether reuse repays it is the step 8 test. Source: slide 18 IF ASKED; Capsule report §4.2; slide 22.
7. **What would you build first?** `capsule_id@version` in the registry, planning snapshot and execution authority, because a capsule change during planning aborts the freeze today. Next is the generalist capsule and gap record, then a protected-path deny list. Source: slide 23; Capsule report §6.
8. **How would you know it is working?** After roughly 10 sprints, read 5 signals together: whether gaps recur, the admission rate and rejection reasons, reuse savings against build cost, held-out conformance against the hand-written control set, and whether the generalist stays general on held-out tasks. Source: slide 22 IF ASKED; Capsule report §5.2 Table 7.
9. **What could prove this design wrong?** Gaps that almost never recur across sprints (the cold path rarely fires), real effects that almost never differ from what a capsule declared (the effects check is worth little), or checking that costs more than reuse saves. Each has an assigned test in the order of work. Source: slide 22; Capsule report §5.1 Table 6.
10. **Why write the manifest and tests before any code exists?** The suite needs a contract to check against before implementation starts, mirroring how Beyond Task Completion wrote its suites before any tool existed; it also stops the suite author and implementer from sharing 1 misreading of a new capability. No paper compares writing tests before vs after code, so this is a design choice. Source: slide 19; Capsule report §4.3; arXiv 2604.00392 Eq. (6).
11. **What is different about the generalist capsule's constraints?** It is bound at planning to steps nothing else fits, capped per plan so it cannot route around typed contracts, judged by the same frozen gates as every other step, given the lowest trust level, and it leaves a gap record instead of ever writing to the library. It cannot build and serve a capsule in the same sprint, because that would change what the freeze already sealed. Source: slide 18; Capsule report §4.1 Fig. 9, App. F.
12. **How does the gate stay reliable if the tests and the implementation could share 1 misreading?** A research step often has no ground-truth oracle, so the suite author and implementer could share 1 misreading of a new capability; this is caught by a control group (the 79 hand-written capsules run through the same held-out tests), not by the tests alone. Where quality needs judgment, a different model than the builder grades it, and its verdict enters only as a recorded result, never a gate override. Source: slide 19 (IF ASKED); Capsule report §4.3; slide 22.

## 4. Numbers to have ready

| Number | What it is | Source |
|---|---|---|
| 75.15% to 83.03% | Alita-G GAIA pass@1 without vs with its library, 15.5% fewer tokens per task | slide 6; Alita-G arXiv 2510.23601 Table 1 |
| 100% to 51% | Distinct tool share as the library grows 26 to 128 tools | slide 7; arXiv 2510.23601 Table 4; figdata.py `COVERAGE` |
| 16 points | Accuracy swing from 1 similarity threshold, 25 questions | slide 7; arXiv 2510.23601 Table 3 |
| 96.8% (215 of 222) | Kept tools scoring zero on held-out tests of their own job | slide 9; arXiv 2604.00392 Table 5; figdata.py `SILENT_ROT` |
| 41.1% / 71.1% | CoEvoSkills pass/fail only vs verifier feedback + pass/fail; 53.5% human-curated | slide 10; arXiv 2604.01687 Fig. 4, Table A1; figdata.py `COEVO` |
| 20.0% to 50.0% / 14.2% to 30.7% | DGM: SWE-bench Verified / Polyglot, over 80 rounds | slide 11; arXiv 2505.22954 §3-4 |
| 1.67 vs 2.00 | DGM: 1 version that genuinely fixed hallucination vs 1 that deleted the detector's log markers | slide 12; arXiv 2505.22954 App. H |
| 4% vs 92% | Opus 4.8 first-sight commit rate, abstract vs script-required | slide 14; arXiv 2607.23332 Table 1; figdata.py `ALLOC` |
| 79 / 5 | Hand-written capsule manifests / gaps identified today | slide 16; AI4Research at b0bf165f9 |
| 2 sprints / 5 tries | Starting values: sprints before a build counts, gate tries per build | slides 15, 18, 23; Capsule report §6, Table 4 |

## 5. Things not to say

- "The gate catches broken capsules": nothing is built or measured yet; say "predicted" (slide 22).
- "96.8% of our capsules would fail": that rate is 1 model, 1 harness, from Beyond Task Completion, not a claim about AI4Research's own capsules.
- "Alita-G's gain is fake": the evidence goes both ways; its tools were never replayed on held-out questions (slide 9 IF ASKED).
- "GAIA scores are comparable across systems": different model stacks (slide 6 IF ASKED).
- "The unmodifiable checker is our idea": DGM names the lesson; what's new is enforcing it through declared effects, not hiding code (slide 19).
- "2 sprints and 5 tries are the right values": they are starting values, revised once real data comes in (slides 15, 22, 23).
- "Build" as 1 step: it is 3 model sessions plus a code gate (slide 18).
- Paper nicknames like "silent rot" or author surnames: use paper titles only (slide 9 IF ASKED).
- Don't swap the capsule count: the deck says 79 hand-written manifests; do not substitute 80 (the registered count, which also includes non-capability entries) or 68 (a stale figure the ledger flags as wrong).
- Don't claim any of the 79 hand-written capsules have already passed held-out tests: writing those tests is step 6, not done yet (slide 23).

## 6. Insertion slides

2 optional slides remain, 1:30 in total, both in the evidence half. Each sits directly after the core slide it
deepens and can be deleted or hidden without touching anything else: `DECK_INSERTS=hidden` builds them hidden,
`off` drops them. Core numbering never shifts.

| # | Title | TIME | Crib line | Cut order |
|---|---|---|---|---|
| 9a | Alita-G and the 96.8% measure different tools | 0:50 | Different tools, different inputs: Alita-G is scored on the questions its tools came from, and its tools were never replayed on held-out inputs. | 2 (it answers the obvious objection to slide 9) |
| 13a | What each prior system checks before it keeps an artifact | 0:40 | Every prior system checks something; none compares what a capability declares with what it is observed to touch. | 1 |

Sources: report §2.3 with App. A.1 and Table A2; App. A.6 Table A7.

The 6 design-half insertions (18a 3 loops, 19a generalist flags, 23a retirement reasons, 24a 5 signals, 26a and 26b
capsules on DSH) were removed from the script on 2026-09-15 afternoon because the talk dragged after the design
figure. Their content stands in the report: App. G.2 Fig. G1, App. G.3, §4.5 with App. G.6 Table G1, §5.2 Table 8,
App. D Table D1. `git show e2bb0d0:notes/report-capsules/deck-src/build_deck.py` has the slide code.
