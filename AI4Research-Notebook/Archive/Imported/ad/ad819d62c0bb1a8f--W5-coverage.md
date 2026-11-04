# W5 coverage audit: what the room will ask, and where the story should answer it

Read-only audit, 2026-09-15. Both decks were read in slide order (faces first, then SAY, then IF ASKED), then
both reports. Nothing outside this file was changed.

**Locator key** (full paths used again in every proposal line):

| Key | File |
|---|---|
| `CD` | `notes/report-capsules/deck-src/build_deck.py` |
| `CR` | `notes/report-capsules/REPORT.md` |
| `GD` | `notes/report-general/build/build_deck.py` |
| `GR` | `notes/report-general/REPORT.md` |

Slide numbers are the build order, which matches `notes/overnight/render/*/slide-NN.png` and the crib lists in
both presenter packs. Capsule deck: 26 slides, 20:30. Workflow deck: 20 slides, 15:25. Sum 35:55 against a
40:00 target and a 45:00 maximum, so there are 245 spare seconds before the target is reached.

Rate used for costing: 2.3 spoken words per second, rounded up.

---

# Part 1. Capability Capsule talk

## 1.1 The 25 most likely questions, ranked

| # | Question | Who asks | Answered where today | Quote |
|---|---|---|---|---|
| 1 | What of this is built, and what is only proposed? | supervisor | slide face, divider 17 `CD:407`; slide 16 face `CD:389`; report `CR:200` | "Proposed: nothing here is built or measured yet" |
| 2 | Why not just use Alita-G? | supervisor | slide face 7 `CD:221-222`; rule slide 8 `CD:234-241` | "builds once for 1 fixed benchmark, then freezes / tools come from the questions they are scored on" |
| 3 | Does a self-built library raise task scores at all? | supervisor, hostile | IF ASKED slide 24 `CD:536-538`; report Table 7 row 7 `CR:362` | "Does a self-built library raise task scores at all: evidence both ways. Alita-G gained 8 points on its own questions; in Beyond Task Completion, 35.8% of tasks passed with self-made tools against 33.7% with the seed tools only" |
| 4 | What does one admission cost? | supervisor | IF ASKED slide 24 `CD:541-542`; slide face 24 names the falsifier only `CD:524`; report `CR:425` | "Costs Alita-G doesn't pay: the generalist on every step nothing fits, a suite author and an effect check for every admission, and re-running every capsule's tests on a schedule" |
| 5 | How would you know it is working, and what would stop it? | supervisor | slide faces 24 `CD:521-527` and 25 `CD:546-563`; report §5.2 Table 8 | "Wrong if gaps rarely come back: the cold path rarely fires" |
| 6 | Where does this run, who approves, what about credentials and network? | supervisor | slide face 26 `CD:595-596`; report App. G.8 `CR:797-802` | "Unattended runs cannot use approval-gated steps. Credentials, network (deny by default), multi-tenant runs, who approves?" |
| 7 | What stops a generated capsule from writing somewhere it should not? | supervisor | slide face 13 `CD:351`; slide face 21 `CD:465`; SAY 21 `CD:470-472`; report `CR:296-303` | "no capsule can write to the gate, the tests, the logs or the registry" |
| 8 | That 96.8% is from a different setup, so it does not transfer | supervisor, hostile | face strip `CD:256`; face point `CD:267`; IF ASKED `CD:279` | "1 model and 1 harness: this is the rate there, not a general rate" |
| 9 | How do you test a step that has no right answer? | supervisor, co-op | slide face 21 `CD:465`; SAY 21 `CD:467-469`; report `CR:275` | "tests check promises, not research answers; declared vs real effects is the new check" |
| 10 | Alita-G gained 8 points, so how can 96.8% of tools be broken? | supervisor, hostile | SAY 9 `CD:273-278`; report `CR:124` | "First, these are not Alita-G's tools, and nobody has tested its tools this way. Second, its tools came from the same GAIA questions it was scored on" |
| 11 | You cannot control for the model: 4 papers, 4 different models | supervisor, hostile | nowhere as a cross-paper point. Each paper is bounded on its own face strip (`CD:252`, `CD:288`, `CD:367`) and the control group is the 79 hand-written capsules, IF ASKED `CD:539-540` | nowhere |
| 12 | What happens when the builder never passes the gate? | supervisor | IF ASKED slide 18 `CD:429`; report `CR:279` | "Out of tries or time, the gap goes back to the build-decision agent" |
| 13 | Why can the implementation agent not see the tests? | co-op | slide face 13 `CD:350`; IF ASKED 18 `CD:427` | "code decides admission; the builder hears only admit or reject" |
| 14 | Will the generalist become the default path and route around the contracts? | supervisor | IF ASKED slide 19 `CD:445`; report Table 7 last row `CR:366`, App. G.3 `CR:742` | "The planner caps how many generalist steps a plan may have" |
| 15 | How does this map onto DeepSeek Harness? | supervisor | slide face 4 figure `CD:175`; the design-to-DSH mapping is report App. D Table D1 `CR:659-670` only, with no slide | nowhere in the design act |
| 16 | Why 2 sprints and 5 gate tries? | supervisor | slide face 25 row 7 `CD:560-561`; slide face 26 `CD:585-586`; the sources are IF ASKED `CD:574-575` | "Why 2 and 5: the 2nd sighting is the first confirmed repeat AllocBench's best policy waits for; 5 is the bound CoEvoSkills puts on its pass/fail oracle" |
| 17 | How does this differ from the Darwin Gödel Machine rewriting itself? | supervisor | slides 11 and 12 show DGM; the boundary is slide face 13 `CD:351` and slide 21 SAY `CD:472-473`. What the system may never change is report App. G.5 `CR:750-757` and IF ASKED `CD:478` | "What may change, most reversible first: the library by versions, then context and prompts" |
| 18 | What happens when an admitted capsule breaks later? | supervisor | slide face 23 `CD:499`; SAY 23 `CD:506-508`. The audit loop that catches it is report `CR:332`, App. G.2 `CR:731` | "Retired: a record; only a security reason stops sprints" |
| 19 | How does this sit on top of the freeze from the other talk? | co-op | slide face 19 `CD:434-435`; SAY 19 `CD:438-442`; report `CR:230` | "Generalist: bound at planning to steps nothing fits · judged by that step's frozen gates · lowest trust · leaves a gap record, never writes to the library" |
| 20 | Why these 5 papers? | co-op | divider 5 face `CD:186`; report §2 lead `CR:72`. The grouping logic is never on a face | "Each result, then the design rule it leads to" |
| 21 | Does building block a sprint? | co-op | slide face 8 `CD:235-236`; report `CR:208` | "R1 Using capsules and building capsules happen at the same time, on separate clocks: sprints never wait for a build" |
| 22 | Does the library grow without limit? | co-op | slide face 8 `CD:241`; slide face 23 `CD:496-500` | "R4 Duplicates are rejected: a close capsule is versioned, not copied" |
| 23 | How long does this take to build, and who does it? | supervisor | order of work on slide face 26 `CD:580-582`. Effort and owners appear nowhere in either document | nowhere |
| 24 | Why embeddings rather than the planner model? | supervisor | SAY 22 `CD:488-490`; slide face 25 row 6 `CD:558-559` | "Alita-G shows similarity is sensitive, so the 2 should be compared on the same candidates" |
| 25 | What if the suite author and the implementer share the same misreading? | supervisor, hostile | report `CR:288` only; nowhere in the deck | "A new research capability has no ground-truth oracle, so the suite author and the capsule author can share the same misreading of the task" |

## 1.2 Proposals: where each answer belongs in the story

| Q# | Placement | Exact text | Seconds |
|---|---|---|---|
| 3 | `notes/report-capsules/deck-src/build_deck.py:520`, slide 24, new face line between the track table and the bullets | `Evidence splits on whether a self-built library raises task scores, so track A runs 3 ways.` | 0 |
| 3 (alternative, if the face is full) | `notes/report-capsules/deck-src/build_deck.py:535`, slide 24, added SAY sentence | `Alita-G gained 8 points on its own questions and Beyond Task Completion found no difference beyond noise, so the 3-arm run settles it here.` | +10 |
| 4 | `notes/report-capsules/deck-src/build_deck.py:457`, slide 20, added SAY sentence after "the gate is code" | `Each admission costs 3 model sessions, an effect check, and a suite that is re-run for as long as the capsule lives.` | +10 |
| 8 | `notes/report-capsules/deck-src/build_deck.py:267-268`, slide 9, rewrite of the existing second face point | `These 222 tools come from 3 other tool-making methods on 1 model; Alita-G's tools were never tested this way.` | 0 (rewrite) |
| 11 | `notes/report-capsules/deck-src/build_deck.py:359`, slide 13, added SAY sentence at the end | `Each of the 3 results comes from a different model, so what carries across them is the pattern, and the control for my own numbers is the 79 hand-written capsules.` | +13 |
| 12 | `notes/report-capsules/deck-src/build_deck.py:457`, slide 20, added SAY sentence | `When the tries run out the gap goes back to the decider, and not building is a valid answer.` | +9 |
| 13 | `notes/report-capsules/deck-src/build_deck.py:350`, slide 13, rewrite of the R5 line | `code decides admission; the builder hears only admit or reject, a capped number of times` | 0 (rewrite) |
| 14 | `notes/report-capsules/deck-src/build_deck.py:434-435`, slide 19, rewrite of the bottom strip | `Generalist: bound at planning to steps nothing fits · capped per plan · judged by that step's frozen gates · lowest trust · leaves a gap record, never writes to the library` | 0 (rewrite) |
| 15 | `notes/report-capsules/deck-src/build_deck.py:508`, slide 23, added SAY sentence | `DeepSeek Harness publishes durable data as version-named successors, so append-only versioning is the platform's own rule, and a capsule is a plugin in a profile.` | +11 |
| 16 | `notes/report-capsules/deck-src/build_deck.py:560`, slide 25, rewrite of the row 7 assumption cell | `start values: 2 sprints from AllocBench, 5 gate tries from CoEvoSkills` | 0 (rewrite) |
| 17 | `notes/report-capsules/deck-src/build_deck.py:498-500`, slide 23, third line in the right-hand card | `The model weights stay fixed; the library and the prompts are what change` | 0 |
| 18 | `notes/report-capsules/deck-src/build_deck.py:508`, slide 23, added SAY sentence | `Every admitted capsule's suite is re-run on a schedule, so a capsule that breaks later is caught and retired.` | +9 |
| 20 | `notes/report-capsules/deck-src/build_deck.py:186`, divider 5, rewrite of the subtitle | `5 results: 1 shows the loop works, 3 show outcome-only judging fails, 1 shows when to build` | 0 (rewrite) |
| 23 | `notes/report-capsules/deck-src/build_deck.py:604`, slide 26, added SAY sentence | `Steps 1 to 7 change existing code and read what is already there, and step 8, the cold path, is the only new subsystem.` | +11 |
| 25 | `notes/report-capsules/REPORT.md:288`, already present as a limitation; add the deck IF ASKED at `notes/report-capsules/deck-src/build_deck.py:479` | `The suite author and the implementer can share one misreading of a new capability; the control group and the effects check are what catch it` | 0 (IF ASKED) |
| 4 (supporting, optional) | `notes/report-capsules/deck-src/build_deck.py:312`, slide 11, fourth bullet | `1 SWE-bench run of this loop costs about USD 22,000, against about USD 10,000 for either baseline` | 0 |

Capsule proposals that add SAY: 63 seconds if all are taken, which moves the capsule deck from 20:30 to 21:33.

## 1.3 Keep as IF ASKED (pre-empting these would bloat the talk or read as defence)

| Question | 1-line answer | Source |
|---|---|---|
| What was pass@3, and how many harvests? | pass@3 reaches 89.09%, and the harvest ran 3 times | `CD:206`; `CR:469` |
| What is "distinct share"? | Tool clusters at similarity 0.7 divided by tools, the paper's own effective coverage | `CD:232`; `CR:471` |
| Why does Alita-G skip deduplication? | It is a stated choice, made to keep coverage of task variations | `CD:231`; `CR:472` |
| Is 16 points a lot on 25 questions? | 16 points is 4 of 25 questions | `CD:230`; `CR:473` |
| Are the CoEvoSkills ablations reliable? | The 41.1% and 42.4% ablations are single runs | `CD:301`; `CR:132` |
| Does the CoEvoSkills verifier see the code? | The verifier never sees the skill's code or the hidden tests | `CD:302`; `CR:530` |
| Can DGM modify its own archive loop? | The archive loop is fixed and cannot be modified by the agent | `CD:319`; `CR:538` |
| Does showing a price fix first-sight building? | A visible price did not help, tested on 1 model, Claude Haiku 4.5 | `CD:377`; `CR:554` |
| Why 10 sprints for the first verdict? | 5 times the 2-sprint threshold, so a capsule built at the threshold has several sprints to be bound | `CD:572-573`; `CR:372` |
| Why not build and use a capsule in the same sprint? | It would change what the freeze already sealed | `CD:443`; `CR:706` |
| What about A2A capsules? | A remote peer can never be verified statically, so an A2A capsule would always need approval | `CD:183`; `CR:590` |
| Does DSH support MCP resources and prompts? | DSH supports MCP tools only | `CD:171`; `CR:644` |
| How is a gap identified? | By the types it consumes and produces, its effects and its task type | `CD:458`; `CR:254` |
| Where does a rubric fit in a suite? | A different model from the builder grades it, and the verdict enters only as a recorded result | `CD:474-475`; `CR:275` |
| How many of the 79 can be tested without a right answer? | Unmeasured; held-out suites for a sample, step 6, will show it | `CD:476-477`; `CR:275` |

## 1.4 Phrasing that reads as reactionary or defensive

| Where | Exact text | Why | Story-form replacement |
|---|---|---|---|
| `CD:267-268`, slide 9 face | "These 222 tools are not Alita-G's; Alita-G's own tools were never tested on new inputs." | Rebuts a comparison the slide never draws, in the "not X" shape | "These 222 tools come from 3 other tool-making methods on 1 model; Alita-G's tools were never tested this way." |
| `CD:273-278`, slide 9 SAY | "So how did Alita-G gain 8 points? First, these are not Alita-G's tools, and nobody has tested its tools this way. Second, its tools came from the same GAIA questions it was scored on, the kind of input a fitted tool can still pass." | Rhetorical question plus a numbered rebuttal; the objection is raised in order to be answered | "Alita-G's 8 points came from tools built on the same GAIA questions it was scored on, the kind of input a fitted tool passes. Its paper also shows 1 tool reused on a different question, so the evidence goes both ways." (saves about 13 seconds) |
| `CD:472`, slide 21 SAY | "A new version isn't a duplicate of the capsule it replaces." | Answers an objection nobody has raised yet, in the "not X" shape | "The duplicate check compares a candidate with every registered capsule except the one it versions." |
| `CD:166`, slide 3 SAY | "Quick one on MCP, because people use it to mean tool." | Announces why the slide exists and corrects the audience before they speak | "MCP is a client-server protocol for reaching tools, data and prompts." The slide title "MCP is a protocol, not a tool" is a definition the guide asks for; keep it. |
| `CD:539-540`, slide 24 IF ASKED | "so a failure belongs to the generated capsule, not the tests; this holds only once the hand-written ones pass" | Correct and well placed. Listed so it is not mistaken for defence and cut | no change |
| `CD:521-524`, slide 24 face | "Wrong if real effects almost never differ…", 3 bullets | Stating in advance what would disprove the design is the argument, not a rebuttal | no change |

---

# Part 2. Workflow talk

## 2.1 The 25 most likely questions, ranked

| # | Question | Who asks | Answered where today | Quote |
|---|---|---|---|---|
| 1 | Is any of this built, or is it a design? | supervisor | slide face 20 `GD:391` covers the next steps only; the built parts are implied by the file:line source strips; report App. B `GR:744-758` | "Proposed. None of this is built or measured yet." |
| 2 | Is there an external benchmark result? | supervisor | slide face 13 `GD:250`; report `GR:379` | "External benchmark scores / 0" |
| 3 | What does the freeze cost you? | supervisor | IF ASKED slide 7 `GD:152`; slide face 18 challenge 4 `GD:354-357`; report `GR:181-187` | "The cost: no plan-level search, so the plan cannot change when execution shows it was wrong" |
| 4 | "No model decides after the freeze" is not true, 20 of 43 checks are rubrics | supervisor, hostile | slide face 5 `GD:97`; slide face 10 `GD:196`; IF ASKED 4 `GD:82-83` | "code checks every model output; 20 of the 43 checks are rubrics, judged by a model" |
| 5 | Where does it run, and can it run unattended on a shared server? | supervisor | slide face 18 challenge 6 `GD:362-364`; the trust scope is IF ASKED 9 `GD:186`; report `GR:248-249` | "This trust model holds for 1 user on 1 machine; a shared, unattended server needs a different one" |
| 6 | What stops a planted sentence in a paper from steering the run? | supervisor | slide face 9 `GD:178`; SAY 9 `GD:184-185`; report `GR:246-247` | "untrusted text reaches an agent with shell, files and network only on the CLI-agent path" |
| 7 | Does the hash prevent tampering, or only detect it? | supervisor, hostile | nowhere in deck or report; `notes/overnight/Q2-how-hashes-work.md:61-65` | "It does not stop an edit, only detect one afterwards, and only where something re-computes" |
| 8 | Why TruthInsightBench first? | supervisor | SAY 14 `GD:268`; report `GR:392-401` | "This is the first external test worth running, because what it scores is verification" |
| 9 | Whose 11% to 16% is that? | supervisor, hostile | face strip 14 `GD:263`; report `GR:396-397` | "TruthInsightBench (arXiv 2609.05079) · 4 coding agents, 1 frozen model, 6 dimensions" |
| 10 | What does a run cost in tokens, money and wall-clock time? | supervisor | nowhere. Table 5 `GR:374-381` records nodes, files and gates and no cost | nowhere |
| 11 | Why not re-plan when execution shows the plan was wrong? | supervisor | IF ASKED 18 `GD:374`; slide face 18 challenge 4; report `GR:186-187`, `GR:656` | "#4: keeping the freeze trades away the re-planning Arbor and Kosmos do every cycle" |
| 12 | Why DeepSeek Harness? | supervisor | slide face 16 `GD:308-314`; face strip `GD:307` | "Claw-SWE-Bench (arXiv 2606.12344) · coding: harness 27.4 points, model 29.4" |
| 13 | Are the state-of-the-art numbers self-reported? | supervisor, hostile | IF ASKED 15 `GD:301`; report Table 6 caption `GR:526-527` | "Every result here is the authors' own measurement, except openJiuwen, which is a code read" |
| 14 | Was the 14-node run actually a pass, and how many runs have failed? | supervisor, hostile | slide face 13 `GD:247`; report `GR:376`. The run ledger and the rule against quoting a run count are in `notes/LEDGER-VERIFIED-NUMBERS.md:99-112` only | "passing-flag counts are not a reliable measure" (`LEDGER-VERIFIED-NUMBERS.md:111-112`) |
| 15 | 34 regression failures: what are they? | supervisor | slide face 13 `GD:248`; SAY 13 `GD:255-256`; report `GR:377` | "the 34 failures are kept as known debt, from old fixtures that the current frozen-plan preflight rejects and from Windows path failures, rather than relaxed away" |
| 16 | How much does the cue-word rule miss? | supervisor | slide face 17 `GD:329-330`; report `GR:332-333` | "recall of the cue-word rule unmeasured (operators.py:1183)" |
| 17 | Why is the unsupported-claims list always empty? | supervisor, hostile | IF ASKED 11 `GD:224-225`; report `GR:304-307` | "Claims judged insufficient or not supported still become report conclusions, so the unsupported list stays empty" |
| 18 | Why these 4 reference systems? | co-op | SAY 15 `GD:294`; report `GR:411-412` | "These are the 4 systems I compare against, chosen to span the design space" |
| 19 | What happens when a node fails? | co-op | slide face 8 figure `GD:158`; SAY 8 `GD:162-165` | "B fails its frozen gate and goes back for repair with the findings" |
| 20 | Can a frozen plan be edited after the fact? | co-op | slide face 7 `GD:136-137` | "Tested: a frozen node's priority set to 999 fails verification, though its stored verdict says PASS." |
| 21 | Why allow the CLI-agent path at all? | supervisor | SAY 9 `GD:182-183` | "codex exec gets a shell, files and network, and nothing observes what it does, so that's where generality lives and trust doesn't" |
| 22 | Which models does it actually run on? | co-op | nowhere. Slide face 3 `GD:57` gives operator counts, and no model is named for AI4Research in either report | nowhere |
| 23 | Is the span hash enforced? | supervisor, hostile | IF ASKED 11 `GD:223`; report `GR:334`, App. B `GR:745` | "A span that fails its re-hash is dropped silently; no gate reads the span flag" |
| 24 | How does this differ from openJiuwen auto_research? | supervisor | slide face 15 row `GD:287-288`; report §5.4 Table 8 `GR:599-608` | "openJiuwen auto_research (code read) / LLM manager; contract per round / host code rejects illegal moves / no published evaluation" |
| 25 | What is next, and what unblocks the most? | supervisor | slide face 20 `GD:392-399`; SAY `GD:401-404` | "The question that unblocks the most is Q-G4, which benchmark to run first, because it gives the first external number." |

## 2.2 Proposals: where each answer belongs in the story

| Q# | Placement | Exact text | Seconds |
|---|---|---|---|
| 1 | `notes/report-general/build/build_deck.py:44`, slide 2, new bullet before the plan bullet | `Everything up to the challenges is code read in source at commit b0bf165f9; the next steps are proposed` | 0 |
| 3 | `notes/report-general/build/build_deck.py:137`, slide 7, new face line under the tested box | `Search happens inside steps only, so a plan cannot change when execution shows it was wrong.` | 0 |
| 7 | `notes/report-general/build/build_deck.py:145`, slide 7, added SAY sentence at the end | `A hash detects an edit after the fact, wherever something recomputes; it does not prevent one and it does not authenticate an author.` | +10 |
| 5 | `notes/report-general/build/build_deck.py:178`, slide 9, new face line above the THUS strip | `This trust model covers 1 user on 1 machine; a shared unattended server needs a different one.` | 0 |
| 8 | `notes/report-general/build/build_deck.py:261`, slide 14, rewrite of the title | `TruthInsightBench scores verification: published agents reach 11% to 16% on control testing` | 0 (rewrite) |
| 13 | `notes/report-general/build/build_deck.py:292`, slide 15, new face line above the THUS strip | `Every result here is the authors' own measurement, except openJiuwen, which is a code read.` | 0 |
| 17 | `notes/report-general/build/build_deck.py:212`, slide 11, new face line under the confidence point | `A claim judged insufficient becomes a report conclusion, so the unsupported list stays empty.` | 0 |
| 11 | `notes/report-general/build/build_deck.py:300`, slide 15, added SAY sentence | `Arbor and Kosmos re-plan every cycle, and the freeze trades that away for grading rules that are fixed before the run.` | +10 |
| 23 | `notes/report-general/build/build_deck.py:334`, slide 17, third item in the challenge 2 evidence cell | `a failed span is dropped and no gate reads it` | 0 |
| 18 | `notes/report-general/build/build_deck.py:291`, slide 15, new face line above the table (the table drops to y = 1.9) | `The 4 systems span the design space: generation first, scale, a mechanical held-out check, and the same thesis` | 0 |
| 14 | `notes/report-general/build/build_deck.py:259`, slide 13, new IF ASKED line | `Passing-flag counts are not a reliable measure here, and this talk offers none` | 0 (IF ASKED) |
| 10 | `notes/report-general/REPORT.md:381`, §3.1, after Table 5 | no text proposed: no source records token cost, money or wall-clock time for a sprint. Measuring one sprint would produce the sentence | n/a |

Workflow proposals that add SAY: 20 seconds if both are taken, which moves the workflow deck from 15:25 to 15:45.

## 2.3 Keep as IF ASKED (pre-empting these would bloat the talk or read as defence)

| Question | 1-line answer | Source |
|---|---|---|
| Is the 1-sentence design rule measured? | It is a design target translated from Chinese, not a measurement | `GD:68-69`; `GR:757` |
| What are the 80 registry entries? | 77 capabilities, 1 guard and 2 resources; 74 of the 79 manifests are registered | `GD:70`; `GR:48` |
| Can the model overrule a rejection? | A fidelity objection becomes a warning once the repair budget is spent, so a review model never becomes a second gate | `GD:105-106`; `GR:747` |
| What is in a dispatch tick? | Lock the graph, refuse if a guard fails, reconcile, apply approval, build the ready set, admit and lease, save the ledger | `GD:166-167`; `GR:208-214` |
| How many nodes run at once? | Up to 8 per tick, ordered by priority then id | `GD:168`; `GR:212` |
| Does a retry repeat a paid call? | Work envelopes are fingerprinted, so a retry never repeats a paid call | `GD:170`; `GR:219` |
| Does the cue-word rule match badly? | It matches by prefix, so "founded" counts as "found", and any digit makes a claim testable | `GD:221-222`; `GR:280-281` |
| What are the 6 benchmark dimensions worth? | Evidence auditability 45, robustness 15, control testing 15, cross-dataset generalisation 10, novelty 10, falsifiability 5 | `GD:274-275`; `GR:394-395` |
| Does Arbor use a model in its gate? | A secondary model call extracts the metric its gate compares | `GD:302`; `GR:488-490` |
| Does the harness effect hold for strong models? | It shrinks from 27.4 points on Qwen 3.6-flash to 12.5 on GLM 5.1, and covers coding only | `GD:321-322`; `GR:556-557` |
| Is any openJiuwen code shared? | 0 imports at `b0bf165f9` | `GD:323`; `GR:597` |
| Is human review the fallback? | Experts judge verifiable claims correctly 60.8% of the time | `GD:347`; `GR:639` |
| How many runs have passed? | Passing-flag counts are not a reliable measure and none is offered | `notes/LEDGER-VERIFIED-NUMBERS.md:111-112` |
| What does a run cost? | No source records token cost or wall-clock time for a sprint | gap; Table 5 `GR:374-381` |
| Which models does it run? | Not named in either report; 102 physical operators are defined and 63 enabled | gap; `GR:49` |

## 2.4 Phrasing that reads as reactionary or defensive

| Where | Exact text | Why | Story-form replacement |
|---|---|---|---|
| `GD:82-83`, slide 4 IF ASKED | "\"No model decides after the freeze\" is too strong: 20 of the 43 registered checks are rubrics judged by a model" | Quotes a claim the slide never makes and then retracts it, the "not X but Y where X was never shown" shape. SAY already says the accurate version at `GD:79-80` | "20 of the 43 registered checks are rubrics a model judges; scheduling, routing and admission are code" |
| `GD:177`, slide 9 face | "'Compile' here is the 6 model calls drawn on slide 4, each one checked by code." | Defends the diagram against a charge of hiding model calls in a box, and points at a slide by number | "Compile is the 6 model calls of the pipeline, each one followed by code that checks it." |
| `GD:391`, slide 20 face | "Proposed. None of this is built or measured yet." | "Proposed." is a label-then-point fragment | "None of these 4 steps is built or measured." |
| `GD:252`, slide 13 THUS | "demonstrated end to end, but not yet routinely without someone attending" | The "but not yet" clause concedes rather than states | "demonstrated end to end; an unattended run from a prompt alone has not finished" |
| `GD:234`, slide 12 table | "trust declared at all / 21 of 79 manifests / (empty)" | A row with an empty verdict cell reads as an aside dropped into a table about paths | Move to the slide 12 THUS strip: "21 of 79 manifests declare a trust class, so most evidence carries no declared class" |
| `GR:629`, §6 | "The lead is a design property, not a result, since Rel(AI)Build (2606.26924) already content-hashes its specification" | Correct, sourced and load-bearing. Listed so it is not mistaken for defence and cut | no change |

---

# Part 3. The 10 proposals to apply first

| Order | Talk | Q# | Placement | Exact text | Seconds |
|---|---|---|---|---|---|
| 1 | workflow | 1 | `notes/report-general/build/build_deck.py:44`, slide 2 bullet | `Everything up to the challenges is code read in source at commit b0bf165f9; the next steps are proposed` | 0 |
| 2 | capsule | 16 | `notes/report-capsules/deck-src/build_deck.py:560`, slide 25 row 7 | `start values: 2 sprints from AllocBench, 5 gate tries from CoEvoSkills` | 0 |
| 3 | capsule | 8 | `notes/report-capsules/deck-src/build_deck.py:267-268`, slide 9 face point | `These 222 tools come from 3 other tool-making methods on 1 model; Alita-G's tools were never tested this way.` | 0 |
| 4 | workflow | 3 | `notes/report-general/build/build_deck.py:137`, slide 7 face line | `Search happens inside steps only, so a plan cannot change when execution shows it was wrong.` | 0 |
| 5 | capsule | 3 | `notes/report-capsules/deck-src/build_deck.py:520`, slide 24 face line | `Evidence splits on whether a self-built library raises task scores, so track A runs 3 ways.` | 0 |
| 6 | workflow | 13 | `notes/report-general/build/build_deck.py:292`, slide 15 face line | `Every result here is the authors' own measurement, except openJiuwen, which is a code read.` | 0 |
| 7 | capsule | 20 | `notes/report-capsules/deck-src/build_deck.py:186`, divider 5 subtitle | `5 results: 1 shows the loop works, 3 show outcome-only judging fails, 1 shows when to build` | 0 |
| 8 | workflow | 5 | `notes/report-general/build/build_deck.py:178`, slide 9 face line | `This trust model covers 1 user on 1 machine; a shared unattended server needs a different one.` | 0 |
| 9 | capsule | 4 | `notes/report-capsules/deck-src/build_deck.py:457`, slide 20 SAY | `Each admission costs 3 model sessions, an effect check, and a suite that is re-run for as long as the capsule lives.` | +10 |
| 10 | workflow | 7 | `notes/report-general/build/build_deck.py:145`, slide 7 SAY | `A hash detects an edit after the fact, wherever something recomputes; it does not prevent one and it does not authenticate an author.` | +10 |

**Total added: 20 seconds.** Both decks together move from 35:55 to 36:15, against a 40:00 target.

Taking every proposal in Parts 1.2 and 2.2 adds 83 seconds and gives 37:18.
