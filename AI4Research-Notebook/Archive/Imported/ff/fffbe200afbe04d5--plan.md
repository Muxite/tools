# Human plan: CC architecture and M1 coordination

**Planning date:** October 14, 2026. **Target:** demonstrate the bounded Compiler → Planner → selected downstream research CC journey and complete its platform benchmark report by October 30. Compiler preflight through accepted `Research_Brief.json` is reusable component evidence within that journey; scope follows the current design and its authorized D19 amendment to PRD (4). This is a coordination plan, not a coding-task register. Use existing task records and the maintained [Immediate Plan](../../architecture/design-package/immediate-plan.md).

## October delivery path

| Date | SMART outcome | Owner / review role | Shared resources and dependency | Evidence / risk |
|---|---|---|---|---|
| Oct 14 | Preflight inputs and align existing 10 design tasks; create no replacement tasks. | Architecture Lead / CC Lead | Current package, confirmed PRD (4), existing task register | Task-to-design map and mismatches; stale input is the main risk. |
| Oct 15 | Package aligned work and complete independent RSI target design. | Architecture Lead / RSI Lead | Existing interfaces and protected evaluation profile | Design links to current interfaces; RSI stays independently buildable and off hot path. |
| Oct 16 midday | Run the one-shot coding comparison and kick off M2. | Study Lead / M2 Lead | Pinned inputs and saved evidence, M2 scope | Record input identities and unknowns; no matched without-condition implementation receipt is available. |
| Oct 19 | Review existing CC output. | CC Lead / Review Lead | Existing CC output and current assignment | Findings linked to artifacts; no generalist assigned. |
| Oct 20 | Deliver required pinned Screening/ranking CC handoff. | CC Lead / Review Lead | Existing pinned CC and lineage | Handoff and lineage available; RSI readiness is not a dependency. |
| Oct 21–23 | Complete existing CC verifier assignments. | Verification Lead / Review Lead | Existing CC assignments and verification contracts | Evidence linked to existing work; no new allocation. |
| Oct 26–28 | Run benchmark and compare available RSI evidence. | Benchmark Lead / Review Lead | Benchmark harness, available RSI candidate/evidence | Publish measured results and unavailable measures; candidate availability may limit comparison. |
| Oct 29 | Hold demo and M2 review. | M2 Lead / Review Lead | Current journey and benchmark evidence | Decisions, gaps and owners recorded; unresolved evidence remains explicit. |
| Oct 30 | Complete bounded full research journey and platform benchmark verdict. | Delivery Lead / Benchmark Lead | Integrated current path, platform and benchmark harness | Journey evidence plus verdict and limitations; do not infer acceptance from demo alone. |

**October gate:** demonstrate two representative requests and three successful repeats of the chosen demo case; reject an incompatible connection, a cycle and a missing required checking assignment before dispatch. Retain request, frozen graph, gate, output and benchmark evidence, with a works / works with limits / does not work verdict. The complete bounded journey and benchmark report are due Oct 30. The pinned CC handoff is due Oct 20 regardless of RSI design or service. RSI is optional to the hot path and cannot block core acceptance.

## November allocation: 15 human-days, eight work items

| Dates | SMART outcome | Owner / review role | Shared resources and dependency | Evidence / risk |
|---|---|---|---|---|
| Nov 2–3 | Generalist integrates already scoped components and closes recorded interface gaps. | Integration Lead / Review Lead | Oct 30 evidence, agent-produced generalist, library/runner, permitted tools, shared checking profiles and runtime access | Admit one generalist only after declared inputs/outputs and assigned checks pass; missing code/access postpones admission. Generalist work occurs only here. |
| Nov 4–5 | Three utilities each have a runnable example and interface note: extract/summarize, structured conversion, command/artifact execution. | Utility Lead / Review Lead | Existing component contracts | Each utility has one passing valid case and one rejected invalid case, with independent expectations; missing tools/access delays admission. |
| Nov 9–10 | Integrate agent-produced bounded MCTS search over eligible library candidates; one feasible request produces a validated frozen DAG. | Research Lead / Benchmark Lead | Agent output, MCTS library/configuration, pinned capsule catalogue, deterministic validator, October planner, fixed search/time limits | Record input/configuration pins, valid-plan rate, failures and planning time/cost; missing code or configuration delays acceptance, so retain the October baseline. |
| Nov 12–13 | Compare MCTS and the October planner on two feasible and three incompatible/resource-conflicting cases; record expected and observed outcomes. | Verification Lead / Review Lead | Pinned catalogue, independent expectations, frozen graphs, resource/effect contracts and run logs | Two feasible cases yield valid plans; three invalid cases are rejected before dispatch. Record valid-plan rate, failures and planning time/cost; retain baseline if the candidate fails. |
| Nov 16–17 | One two-CC composite case reaches accepted output or an attributable halt across the declared boundary. | Integration Lead / Review Lead | Utilities and interaction evidence | Composite evidence; no generalized claim from a single case. |
| Nov 19–20 | Compare one offline-fusion candidate against unchanged checks and record a further-study recommendation. | RSI Lead / Review Lead | Independent candidate and protected evaluation | Candidate comparison; checks remain unchanged. |
| Nov 23–24 | Benchmark integrated candidate and publish results and limits. | Benchmark Lead / Review Lead | Composite and baseline evidence | Measured benchmark record; missing measurements are unavailable, never zero. |
| Nov 26 | Complete December readiness review with owners, entry criteria, dependencies and blockers for each next experiment. | Planning Lead / Review Lead | November evidence and research-window proposals | Readiness record; undecided scope stays a proposal. |

**Capacity rule:** November has 15 human-days total across eight items. Dates are work windows, not a claim every role is full-time. Keep all assignments inside this pool; new work requires explicit reallocation. Names are maintained in the team spreadsheet; this plan assigns roles only. Spreadsheet owner-name fields remain under Muk's existing stewardship.

**Conditional gate, Nov 30:** proceed only if integrated journey evidence, benchmark record, and November readiness items are reviewable. The gate judges recorded outcomes, not task completion labels.

## Forward research windows

| Dates | Candidate direction | Exit |
|---|---|---|
| Dec 2026 | Generated checks, routing and composition | Bounded candidates with independent evaluation and explicit admission decision |
| Jan 4–15, 2027 | Spatiotemporal prototype | Demonstrated prototype and measured boundary |
| Feb 1–12 | Lifecycle study | Evidence for lifecycle behavior and unresolved cases |
| Mar 1–12 | External sandbox | Isolated boundary evidence and failure handling |
| Apr 1–16 | Automatic conversion | Conversion candidate compared against unchanged checks |
| May 3–14 | Goal/tool use | Bounded study with attributable evidence |
| May 31 | Final gate | Review outcomes and decide next scope |

**Common risk response:** missing code, access, independent cases or blocking interfaces keeps the dependent gate open; use the reserved dates for targeted repairs and reduce optional additions before moving the core delivery date. Do not count agent production as human work; a human review window begins when output is available. October 21–23 links existing verifier assignments rather than adding a second CC allocation. Architecture consumes shared CC outputs without duplicating their effort.

These are research windows, not implementation commitments. Keep architecture-shared contracts and resources linked from the maintained design; do not copy them into this schedule. Detailed owners and exact inputs must be set at each readiness review.
