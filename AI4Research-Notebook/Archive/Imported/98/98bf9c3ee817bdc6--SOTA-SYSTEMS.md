# SoTA register: systems that do AI4Research's job, and how

Written 2026-09-11. **Every paper below was downloaded to `papers/` and its title
checked against the extracted text.** Figures carry a page reference from the
extraction (`pN`) and were read in source this session. Anything read only in an
abstract says so. Do not add a number here that has not been read from the `.txt`.

⚠ Corrected 2026-09-11 after `review/R1-adversarial.md`; the per-paper detail now lives
in `papers/summaries/` (one file per paper).

Re-run a check: `python papers/peek.py grep <id> "<regex>"`.
Add a paper: `python papers/fetch.py <arxiv-id>`.

---

## 0. The field, framed by two surveys

**2507.01903, AI4Research survey** (Chen et al., v2 Aug 2025). Five task families:
scientific comprehension, academic survey, scientific discovery, academic writing,
academic peer review (keywords and contents, p1-2). AI4Research covers all five
through one control plane.

**2608.05179, Autonomous Research Agents: the Verification Gap** (Ding et al., Jun
2026). ⭐ **The organising frame for the SoTA section.** It codes 24 runnable systems:

- 83% release code; only 38% release seeds or execution traces; only 38% report any
  novelty-verification method (p1)
- Of 9 closed-loop (L4) systems, 7 are mechanical re-runs and 1 is author-claimed
  without an external check; **no LLM-era system demonstrates an externally validated
  in-loop oracle** (p1)
- "an LLM acting as reviewer is now as common as benchmarking (62%)" (p74); ⚠ 62% is
  16 of 26 coded entries, including 2 study/position works
- Recommends "a pre-committed task specification that fixes the metric, the split, and
  the success threshold before the run" (p28)
- **The verification ladder** (Fig. 3, p43-48). ⚠ It ranks **research areas**, not
  systems (Table 8, p44); any per-system tier below is this register's own assignment.
  I sound formal verifier · II
  executable test on held-out data · III simulator or physical oracle · IV citation
  grounding · V learned verifier · VI human expert · VII weak inter-agent or
  infrastructural signal · VIII the model's own judgment. "Most LLM-agent subareas …
  rely heavily on the lower tiers (IV–VIII)" (p43)
- Limitation it states: coding rates are "directional audit evidence", since
  second-coder agreement was lower for autonomy, novelty and selection (p1)

## 1. End-to-end AI scientists

| System | Paper | How it works | Verification signal (ladder tier) | Headline, verified |
|---|---|---|---|---|
| **The AI Scientist** (Sakana; Nature 2026) | 2606.15497 | idea → code → experiments (agentic tree search, experiment manager) → manuscript → self-review | executes every experiment node; LLM Automated Reviewer (VIII); manuscript numbers must come from executed outputs, enforced by **prompt instructions** ("Do not hallucinate data. Data must either be loaded from .npy files or copied from the JSON summaries", p37; "Do not hallucinate new citations", p39); humans filtered outputs at each stage (p5) | 1 of 3 workshop submissions accepted, scores 6, 7, 6 = 6.33 (p5); workshop acceptance 70% vs 32% main track (p6); failure modes include "many types of hallucinations such as inaccurate citations" (p6-7) |
| **AI Scientist-v2** | 2504.08066 | removes template dependency; progressive agentic tree search run by an experiment-progress manager over 4 stages; VLM figure feedback | execution; LLM/VLM node selection (VIII) | predecessor of the above; ⭐ the accepted paper had ~57% train/test overlap and a figure contradicting its claim, found by the authors, not by peer review (p11-12) |
| **Agent Laboratory** (AMD) | 2501.04227 | human idea → literature review → experimentation (`mle-solver`) → report writing (`paper-solver`); PhD/Postdoc role agents; co-pilot mode | execution; VI (human feedback per stage); VIII (LLM reward model and reviewer) | 84% cost decrease vs prior autonomous methods (p1); ⭐ automated reviewer 6.1/10 vs humans 3.8/10 (p2); co-pilot scored higher than autonomous (p2) |
| **Co-Scientist** (Google) | 2502.18864 | Supervisor parses the goal, allocates worker agents: Generation, Reflection, Ranking, Evolution, Proximity, Meta-review; **tournament** ranking of hypotheses (p5) | VIII in loop; III/VI for in-vitro validation | drug-repurposing candidates for AML validated in vitro (p2) |
| **Kosmos** (Edison) | 2511.02824 | **structured world model** shared by data-analysis and literature agents; up to 10 tasks per cycle; up to 12 h, 200 rollouts (p1-2) | II (code) and IV (literature) per statement | 79.4% of statements accurate: **85.5% data-analysis, 82.1% literature, 57.9% synthesis** (p4); every statement cited to code or a primary source |
| **Robin** (FutureHouse) | 2505.13400 | literature agents Crow and Falcon (both PaperQA2-based) + data-analysis agent Finch; lab-in-the-loop (p2) | III (wet lab) | ripasudil proposed and validated for dry AMD (p1) |
| **AI-Researcher** (HKU) | 2505.18705 | literature → hypothesis → implementation → manuscript; introduces Scientist-Bench (22 papers) | VIII (LLM code-review and paper-review agents, p4-5) | 93.8% "completeness" judged by a code-review agent (p10); mean ratings vs human target papers are **negative** (e.g. −1.49, −2.11 on −3..+3), "comparable" counts ratings ≥ −1 (Table 2, p12) |
| **InternAgent-1.5** (Shanghai AI Lab) | 2602.08990 | 3 subsystems: Generation, Verification, Evolution; a planner builds a **flow graph** whose nodes run when dependencies are satisfied (p6, p9) | II/III for discovery tasks | GAIA, HLE, GPQA, FrontierScience (p1); read at abstract level |
| **DeepScientist** (Westlake) | 2509.26603 | discovery as Bayesian optimisation; "hypothesize, verify, analyze" hierarchy; Findings Memory | II | ~5,000 ideas, ~1,100 **selected for experimental validation (tested)**, **21** led to progress, 20,000 GPU-hours (p1-2); ⚠ "validated" in the abstract means tested, not confirmed; **~60% of a sample of failed trials died from implementation errors** (p8, p17); "validation and filtering the new bottleneck" (p2); 3 human experts filtered hallucinations (p5) |
| **openJiuwen auto_research** | agent-core `rsi/…/auto_research` | manager LLM + **host-validated `SubtaskContract` per round** | II (execution), VIII (paper scoring) | no published evaluation found; see `OPENJIUWEN.md` §6 |

## 2. Literature and deep research

| System / benchmark | Paper | Mechanism | Verified numbers |
|---|---|---|---|
| **PaperQA2** | 2409.13740 | dense retrieval → LLM **re-rank and contextual summarisation (RCS)** → answer; Citation Traversal tool (p3) | matches or beats subject experts on 3 literature tasks; 2.34 ± 1.99 contradictions per paper, 70% validated by experts (abstract, p1) |
| **OpenScholar** | 2411.14199 | RAG over 45M open-access papers + self-feedback loop | **without retrieval**, GPT-4 fabricated **78–90%** of citations to recent literature (p1); OpenScholar-8B beats GPT-4o by 5% on correctness (p1) |
| **DeepResearch Bench** | 2506.11763 | 100 PhD-level tasks, 22 fields; RACE (report quality) + FACT (citation accuracy) | ⚠ citation accuracy **39.36 to 94.04 across all 16 systems**; **77.96 (OpenAI DR) to 90.24 (Perplexity DR) among the 4 deep-research agents**; 94.04 is Claude-3.5 w/ search, an "LLM with search tools" row; effective citations 4.35 to 111.21 (Table 1, p6) |
| **ReportBench** | 2508.15804 | reverse-engineered prompts from arXiv surveys; checks cited content against sources, validates uncited claims on the web | cited-statement match 72.94% (Gemini DR) to 78.87% (OpenAI DR); reference recall 1-4% for every system (Table 1, p7) |
| **Who is the agent to blame?** | 2608.24306 | localises each error to the agent that introduced it; 4 types: hallucination, uncited input reliance, uncited output, insufficient citations | **84.7% of final-report errors in AI-Q originate at the orchestrator**, ~31% of them hallucinations (p1) |
| **MR DRE** | 2601.13217 | multi-turn report revision | agents regress on **16–27%** of previously covered content and citation quality when revising (p1) |
| **urlhealth** | 2604.03173 | citation URL liveness | **3–13%** of citation URLs hallucinated across 10 LLMs and deep-research agents; 5–18% non-resolving; deep-research agents pooled 10.7% vs 4.8% for search-augmented LLMs (p1, p5) |
| openJiuwen **deepsearch** | repo README | query planning → hybrid retrieval → fusion → generation; "segment-level provenance" | no benchmark reported in README `[web]` |

## 3. Claim extraction and verification

| System | Paper | Mechanism | Verified numbers |
|---|---|---|---|
| **Claimify** (Microsoft) | 2502.10855 | LLM pipeline: **Selection → Disambiguation → Decomposition**; a sentence that "cannot be disambiguated" is excluded (p4-5) | sentence-level coverage accuracy 91.8%, element-level 87.9%; entailment 99.0% (Tables 1-2, p6-7) |
| **AFEV** | 2506.07446 | iterative atomic-fact decomposition, evidence rerank, per-fact verification | SoTA on 5 datasets (abstract) |
| **FactReview** | 2604.04074 | extracts review claims, grounds them in literature, **executes released code under a fixed repair budget** | 89.5% precision, **79.7% recall**, 84.3% F1 claim recovery on 354 human-verified claims (p1, p5); removing execution evidence changes **17.0%** of claim statuses (p1) |
| **AI4Research** | `operators.py:1180-1265`, `delivery.py:41-239` | **regex cue words** select sentences; testability by a second regex without word boundaries; `verify_claim` is a deterministic decision table whose literature-only verdict rests on a **case-insensitive substring match**, while span SHA-256 re-verification only filters which spans pass downstream (see `REPORT.md` §3.5) | none measured |

## 4. Benchmarks for research agents

| Benchmark | Paper | What it scores | Best result reported |
|---|---|---|---|
| **MLE-bench** | 2410.07095 | 75 Kaggle competitions | o1-preview + AIDE: bronze or better in **16.9%** (p1) |
| **PaperBench** | 2504.01848 | replicate 20 ICML 2024 papers; 8,316 rubric tasks; LLM judge | best agent **21.0%**; on a 3-paper subset ML PhDs 41.4% vs o1 26.6% (p1-2) |
| **ScienceAgentBench** | 2410.05080 | 102 tasks from 44 papers, output is a program | **32.4%** alone, 34.3% with expert knowledge, 42.2% o1-preview (p1) |
| **ResearchClawBench** | 2606.07591 | 40 tasks, 10 domains, target paper hidden, expert rubrics; ⚠ **graded by GPT-5.1** against those rubrics (p10) | best agent Claude Code **21.5**; best LLM Claude-Opus-4.7 20.7; failures cluster in protocol mismatch, evidence mismatch, missing scientific core (p2) |
| **Terminal-Bench 2.0** | 2601.11868 | 89 terminal tasks | frontier <65% at release (p1) |
| **DeepResearch Bench** | 2506.11763 | see §2 | |

AI4Research's position: ⚠ only **Terminal-Bench 2.0 has an adapter package**
(`harness/lib/benchmark/`, Harbor); SWE-bench, GAIA, OSWorld, WebArena, BrowseComp and
tau-bench are plug-in slots in `agent_arena_benchmark.py` that need an external runner
command. There is an explicit rule not to claim a leaderboard result unless one is run.
**No external score exists.**

## 5. Compiled intent, contracts, and plan-then-execute

| Work | Paper | Relevance |
|---|---|---|
| **LLMCompiler** | 2312.04511 | planner emits a DAG of function calls, task-fetching unit dispatches, executor runs in parallel; up to 3.7× latency and 6.7× cost savings vs ReAct (p1) |
| **DSPy** | 2310.03714 | LM pipelines as declarative modules; a *compiler* optimises prompts and demos against a metric (p1) |
| **AFlow** | 2410.10762 | MCTS over code-represented workflows; +5.7% average over baselines (p1) |
| **MetaGPT** | 2308.00352 | SOPs encoded as role pipelines; agents verify intermediate results (p1) |
| **Magentic-One** | 2411.04468 | Orchestrator plans, tracks progress, **re-plans** on error (p1-2) |
| **Agint** | 2511.19635 | NL → **typed, effect-aware code DAGs**; 6 type floors TEXT → TYPED → SPEC → STUB → SHIM → PURE (p2-3; the abstract shortens this to 4); effects tracked by the runtime; no benchmark evaluation (p9) |
| **PlanCompiler** | 2604.13092 | **typed node registry, static graph validation, topological compilation; executes a prevalidated graph**; 44/50 schema-trap tasks vs 20/50 (GPT-4.1) and 26/50 (Claude); $0.356 vs $2.140 vs $18.391 total (p1) |
| **RunAgent** | 2605.00798 | agentic language with IF/GOTO/FORALL; per-step constraints and rubrics (p1) |
| **Intent-to-Execution Integrity** | 2605.16976 | agents are structurally compilers; 4 integrity properties: tool, instruction, judgment, data-flow (p1) |
| **CaMeL** | 2503.18813 | privileged LLM plans from the trusted query only; quarantined LLM reads untrusted data; interpreter enforces capabilities; **77%** of AgentDojo tasks with provable security vs 84% undefended (p1) |
| **Design patterns vs prompt injection** | 2506.08837 | **plan-then-execute**: a fixed plan formed before any untrusted data; that data "cannot inject instructions that make the agent deviate from its plan" (p5) |
| **Agent Contracts** | 2601.08815 | C = (I, O, S, R, T, Φ, Ψ), including **success criteria Φ** fixed up front; resource budgets with **conservation laws** for delegation; 90% token reduction, 525× lower variance (p1) |
| **Agent Behavioral Contracts** | 2602.22302 | C = (P, I, G, R); runtime enforcement; drift bound D* = α/γ; 88–100% hard-constraint compliance (p1) |
| **Safe LLM agents survey** | 2608.14590 | 38 studies (PRISMA): LLM-generated PDDL is syntactically valid but only **24–35%** semantically correct (p4; the abstract generalises this to "NL-to-formal translation"); the **verifier tax**: blocking 94% of unsafe actions can leave <5% safe task completion (p1), ⚠ **a single study, GRADE certainty "Very Low"** (p3, p8) |

## 6. Orchestration and runtime layers

| Work | Paper | Relevance |
|---|---|---|
| **openJiuwen** | 2608.27969 | Inner/Outer Loop + Rails + Swarm Flow; see `OPENJIUWEN.md` |
| **Swarm Skills** | 2605.10052 | openJiuwen team + Renmin; extends the Anthropic Skills standard with roles, workflows, execution bounds; self-evolution scored on Effectiveness, Utilization, Freshness (p1) |
| **Ledger** | 2608.00808 | **deterministic** runtime layer, no LM calls: execution state of observed / modified / attempted; SWE-bench Verified 56.2 → 64.2 (GPT-5 mini), 75.8 → 81.0 (MiniMax M2.5), cost −28.9% / −31.8% (p1) |

## 7. Autonomous optimization with a held-out gate

| System | Paper | How it works | Verification signal (ladder tier) | Headline, verified |
|---|---|---|---|---|
| **Arbor** (living technical report, p1) | 2606.11926 | "separates autonomous research into a long-lived coordinator and short-lived executors" (p2) + **Hypothesis Tree Refinement** (p1); coordinator loop is six steps, "Observe, Ideate, Select, Dispatch, Backpropagate, and Decide" (p7); node = ⟨hypothesis, insight, metadata⟩ (p6), metadata carrying "an implementation reference such as a git branch or commit" (p6; the schema says branch, p31); each executor "materializes the corresponding intervention in an isolated git worktree" (p6) and is hypothesis-bound: "the returned score would no longer be evidence about the assigned node" if it changed the hypothesis (p8) | **II** — "Promotion is guarded by a held-out merge gate: the candidate is evaluated on Etest in a fresh worktree and is merged into Mbest only if it improves over the current best" (p8); enforced at the tool level: the merge tool "is the only path through which a candidate branch can be promoted" (p28); dev/test split is real, "36 development tasks and 53 held-out test tasks" (p8) | Terminal-Bench 2.0: "Claude Code achieves the highest development score (75.00), but its held-out score drops to 71.70; Arbor has a lower development score (72.22), but reaches the best held-out score (77.36)" (p10, Table 2); MLE-Bench Lite **86.36% Any Medal / 77.27% gold** with GPT-5.5 (p11); ablation **81.82%** full vs 63.64% w/o tree vs 54.54% w/o insight feedback (p12) |

Setup, for reproducibility: Claude Opus 4.6 for both roles unless stated (p9);
48-hour wall clock for all real-research runs (p9); "default Arbor budget is 20
coordinator cycles with maximum tree depth 2" (p9); merge threshold 5.0% of dev
improvement (Table 7, p29); Avg@3 for stochastic methods (p9); 20.12M-43.19M
tokens across six cost logs (p13).

⚠ Three cautions before citing Arbor as "the mechanical gate":
- **A model can supply the number the gate compares.** "If no valid JSON block
  is found ... a secondary LLM call reads the full command output and extracts
  the primary metric as a percentage" (p30). The *comparison* is mechanical;
  the *measurement* need not be. The paper never says "no model decides the
  merge".
- **How often Etest runs is not consistent across the paper.** Algorithm 1
  calls it every cycle on the argmax-dev candidate (p7, line 11); Algorithm 2
  fires it only past the 5% threshold (p26, p29); the task protocol says "The
  test set is evaluated only once after the search completes, to report
  held-out performance" (p33). Do not assert any one of the three as the
  system's behaviour.
- **Six tasks, one suite.** "Our experiments are an initial probe of autonomous
  research rather than a complete benchmark for scientific discovery" (p22).
  Table 2 reports single values with no visible standard deviation despite the
  Avg@3 claim.

## Numbers not to use

| Number | Why |
|---|---|
| "DRBench citation accuracy 78% to 94%" from a web summary, **and** ⚠ this register's own earlier "77.96 to 94.04" | Both mix categories. Use 39.36-94.04 (all 16 systems) or 77.96-90.24 (the 4 deep-research agents), Table 1 of 2506.11763 |
| "DeepScientist validated 1,100 ideas" | 1,100 were *tested*; 21 produced progress (2509.26603 p2) |
| "84.7% of errors originate at the orchestrator" without naming the system | It is AI-Q only, whose orchestrator writes the report (2608.24306 p1) |
| Any tier as "the survey's tier" for a system | Per-system tiers are ours. The survey is stronger than "it ranks areas": "The ladder classifies checks, not systems ... locating a system on the ladder means decomposing its output rather than awarding it a single grade" (2608.05179 p48). It names none of Kosmos, Arbor, AI4Research or openJiuwen |
| Arbor "no model decides the merge" | Not in the paper. The merge tool is the only promotion path (p28), but the compared metric may come from "a secondary LLM call" (p30) |
| Any InternAgent-1.5 benchmark score | architecture read in full, results tables not read |
| AI-Researcher "comparable to human" percentages without the definition | "comparable" means rated ≥ −1.0, i.e. somewhat worse; means are negative |
| openJiuwen "8,463 stars" and similar | GitHub page, changes daily, irrelevant to the argument |

---

## Pass 2 (2026-09-15): §4 re-checked against the papers

Builds on `../overnight/Q3-sota-verification.md` (25 claims). New findings:

| Finding | Source | Action taken |
|---|---|---|
| The invented "exec" rung label is unnecessary. The survey files its own "newest 2026 AI scientists" sub-area at **Tier V**, signal "externalized checking apparatus (mixed)" | 2608.05179 p76 (Table 17), definition p44 | "exec" removed from REPORT.md §4 and Table 6; every rung is now the survey's, with 5 rungs defined (II, IV, V, VI, VIII) |
| AI Scientist-v2's individual workshop scores are **6, 6 and 7**, not 6, 7 and 6 | 2504.08066 p9 | Corrected in §4.1; n added (3 of the workshop's 43 submissions) |
| "Arbor: a held-out merge gate with **no model**" survived in the §4.3 heading, Table A1 and the slide-15 table after Q3 cut it from the body | "Numbers not to use" above; 2606.11926 p28 (tool-level), p30 (secondary LLM call extracts the metric) | Replaced everywhere with "enforced by the merge tool". The p30 caveat is now a limitation bullet in §4.3, not only an IF ASKED note |
| Kosmos reports different verbs per statement type: data analysis statements were **reproducible**, literature statements **validated against primary sources**, synthesis statements **accurate** | 2511.02824 p4 | §4.2 no longer flattens all 3 to "accurate" |
| "Kosmos links its evidence but does not gate it" is an absence claim the paper does not make | 2511.02824 p2, p4 | Rewritten to what is sourced: it cites every statement and measures accuracy afterwards |
| Arbor's setup was missing: Terminal-Bench 2.0 is **89 shell tasks split 36 development / 53 held-out**, with **Claude Opus 4.6** in both roles | 2606.11926 p8, p9 | Added to §4.3 |
| TruthInsightBench's n was missing: **40 blind tasks from 40 peer-reviewed studies across 10 domains** | 2609.05079 p1 | Added to §3.2 and to the slide-14 DEMONSTRATED BY strip |
| OpenScholar's 78-90% fabrication figure is **GPT-4**, not GPT-4o | 2411.14199 p1 | REPORT.md App. E.7 still says GPT-4o; raised as a cross-ref, App. E is another lane |

All Table A1 numbers were re-located this pass: PlanCompiler 44/50 against 20/50 (2604.13092 p1) and "constraint
evasion under partial enforcement" 13 of 22 failures (p3, p17); CaMeL 77% against 84% (2503.18813 p1); CREDENCE 0.811
(2606.19819 p21); FactReview 79.7% recall and 17.0% of statuses (2604.04074 p5, p1); DeepFact 27.0% of non-adversarial
test claims unsupported (2603.05912 p8) and experts 60.8% (p5); Claw-SWE-Bench 27.4 pp against 29.4 pp and 19.1%
against 73.4% (2606.12344 p1, p11); Rel(AI)Build content-hashed specification (2606.26924 p20) and cooperative trace
linkage (p1).

### Systems considered and left out of §4

All 4 are already in `papers/`, read with page references in §1 above, and are now named in REPORT.md §4 and Table A1
so a reader does not have to ask why they are absent. The common reason: the strongest check each admits is a wet lab
or a human, which AI4Research has no path to.

| System | Paper | Strongest check |
|---|---|---|
| Co-Scientist (Google) | 2502.18864 | Model tournament, then in vitro validation (p2, p5) |
| Robin (FutureHouse) | 2505.13400 | Laboratory confirmation of ripasudil for dry AMD (p1) |
| Agent Laboratory (AMD) | 2501.04227 | Human feedback per stage; co-pilot mode scores higher than autonomous (p1-2) |
| Towards End-to-End Automation of AI Research (Sakana) | 2606.15497 | Workshop peer review, repeating AI Scientist-v2's experiment (p2) |
