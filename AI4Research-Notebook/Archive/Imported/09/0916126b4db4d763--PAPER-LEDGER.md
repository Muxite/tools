# Paper ledger: every cited paper, read in full

Built 2026-09-22 for SCHEMA v1.6 and the workshop deck and companion. Every cited paper was read end to end by an agent (the per-paper sections below record the last page reached) and has been read by Muk. Each section gives what our documents cite, the exact figure and page, the caveat, and a verdict.

**Corrections applied from this ledger** (each re-checked in the paper text by the main agent before applying; the log is `V9-final-pass-20260922.md`):

| Paper | Was | Now |
|---|---|---|
| More Skills, Worse Agents? 2605.24050 | "Sonnet 4.6 mostly picked wrong ones" | at 202 skills Haiku invoked no skill in 65.9% of trajectories; Sonnet's losses went mostly to wrong picks (14.0%), while 81.4% still used only the right skills (Table 10, p17) |
| More Skills 2605.24050 | reader flagged 0.49 to 0.28 as absent | **reader wrong**: Fig. 1 p3 prints 0.49 [0.37, 0.60] and 0.28 [0.16, 0.39]; the numbers are in the figure, not the extracted text. Kept, cited to Fig. 1 |
| The Blind Curator 2607.07436 | checks and judge caught "disjoint" defects | "complementary": checks miss semantic defects, the judge flags structural ones but its score barely moves (Fig. 2, p4-5) |
| The Blind Curator 2607.07436 | raw deprecations "looked normal" | raw deprecations never reached zero (9.7 clean; 7.7, 3.7, 3.0 under bias), so the count hid a stopped curator (Table 1, p6) |
| The Blind Curator 2607.07436 | retired "genuinely bad skills" | retired by the contribution rule, separated from cap eviction; bias injected on a deterministic grader (p6, p8) |
| The Blind Curator 2607.07436 | curator health "signals" a lenient judge | the pattern is consistent with a lenient judge and triggers an audit; the paper frames its audit as a pre-deployment gate, not a monitor (p17). `design` |
| The Blind Curator 2607.07436 | a strict judge costs throughput heavily | the paper predicts starvation (p5); in its loop the strict judge matched the clean loop (+0.024), retired 10.3, and synthesised fewer skills (19.0 vs 22.0) (p6-7) |
| Cognitive Admission Control 2609.16313 | "unknown defers or rejects" | unknown defers with a typed evidence request (or escalates); only a violated check rejects (p5, Alg. 1 p8); denying on unknown is its NoRemediation ablation, which lost 30 of 120 completions (p10) |
| Beyond Task Completion 2604.00392 | "a conformance suite per tool" built as admission | a held-out conformance suite per capability, replayed after the sessions (audit, not admission) (p5) |
| Beyond Task Completion 2604.00392 | "raised no in-session flag" | not caught by the in-session task verifier, which scores task outputs, not tools (p5) |
| RelAIBuild 2606.26924 | "file scope checked" | file scope checked after the edit lands: detection, not prevention (p20-21) |
| 2607.23332 | "recurrence, not retries" | build on confirmed recurrence, not first sight (p3-4, p8); "not retries" is `design` |
| Agent Contracts 2601.08815 | "only a per-call token cap binds within a call" | contracts bind between calls; within a call only max_tokens approximately bounds cost (p12-14) |
| SkillDAG 2606.03056 | p5, p9; "inferred from text" | p5-6; SkillDAG argues conflicts cannot be inferred from text, only observed in execution |
| Contract2Tool 2606.07904 | "contracts inferred from documents" | inferred from documentation and execution traces; traces did best (p6-8) |
| Darwin Gödel Machine 2505.22954 | "RSI may build from it" cited p8 | archive and parent selection pp4-5; p8 supports "never deleted" |

| Cordis 2608.25512 (added 2026-09-22) | "completely reversed" | reversal holds inside the system boundary and up to an observational equivalence; an inverse's correctness is the author's obligation, unchecked by the runtime (p58-59); agent harnesses are future work (p82) |

**New evidence taken from this ledger:** Contract2Tool Table V (p8): exposing all 100 tools cost 26,172 tokens a task at 0.775 success; a keyword top-5 filter cut that to 4,482 tokens but success fell to 0.620; contract-based filtering exposed one tool at 2,528 tokens and 0.980 success (learned) or 0.990 (gold). Synthetic 100-tool registry, 102 tasks, mocked execution, no seeds.

---

# 2608.01050 — Don't Offer What Can't Be Done: Deterministic Executability Gating for LLM Skill Selection at Scale

**Read in full:** yes, all 7 pages (to the end of the references), by the main agent on 2026-09-21.

## Summary
Wix Helpmate customer-care assistant; one topic family of ten skills. Three stages: a recall-oriented, state-blind
semantic matcher; a deterministic executability gate that evaluates each skill's own exit conditions ("exit-condition
inversion"); then the LLM decides. Production analysis Jun 9 to Jul 10 2026: 756,641 messages, 267,612 conversations.
Counterfactual replay: the first 1,000 risk-enriched conversations, each replayed once with all ten skills exposed.

## Ledger
| Number or claim | Paper | Page | Caveat |
|---|---|---|---|
| gate removed 59.4% of post-semantic skill–message pairs | 1,039,462 of 1,749,270 | p1, p5 §5.4 | pairs, not messages |
| gate removed 59.1% of post-semantic skill-description tokens | 228,799,446 of 387,288,378 | p1, p5 §5.4, Fig. 2 p4 | description tokens only, not billed cost or latency (p4, p6) |
| semantic matching and gate together: 90.5% fewer description tokens than exposing all ten skills | 90.5% | p1, p5, Fig. 2 | same |
| per matched message the gate removes 5.94 skills and 1,308 description tokens | | p5 | |
| model selected a production-blocked skill in 78 of 1,000 conversations (7.8%) | | p1, p5 §5.6 | risk-enriched cohort, replayed once, measures selection not execution, not extrapolable (p5, p6 §7) |
| sound by construction relative to the implemented skill contract, provided predicate parity holds and gate and skill read fresh authoritative state | | p2 §3.2, p3 §4.2, §4.4 | one-sided: passing the gate does not guarantee success (p3) |
| parity lifecycle: author exit, update predicate and state dependencies, parity regression tests on boundary, missing-state and stale-state fixtures, serve only after they pass, with versioning and rollback | | p5 §6.1 | |
| three failure modes: predicate drift, state staleness, backend-contract drift | | p5 §6.2 | |
| unavailable-state policy must be explicit and tested; fail open or closed is a product decision | | p5 §6.2 | |
| predicate parity is a release invariant, not a one-time property | | p6 §6.3 | |
| deterministic rather than prompt-based: executability would otherwise compete with intent in one stochastic context | | p3 §4.3 | |
| hiding an ineligible skill reduces attack surface but must not replace least-privilege access control | | p2 | related-work argument |
| ambiguous intent is not a deterministic exit condition | | p3 | |

## Figures
- Fig. 1 p4: the three-stage pipeline (raster). Fig. 2 p4: the token funnel (raster). Fig. 3 p6: per-skill distributions.

---

## Agent Contracts: A Formal Framework for Resource-Bounded Autonomous AI Systems (arXiv 2601.08815)

**Read confirmation:** I read the whole file with Read in three chunks (lines 1-400, 401-800, 801-1141). `wc -l` gives 1141 lines, and the last line reached is 1141, the end of reference [69] (Zilberstein 1996). The last page marker is "===== page 22 =====", so all 22 pages were read: body pp.1-17 and references pp.17-22. The paper has no appendix. The source is v3, 25 Mar 2026, accepted at COINE 2026 (p1).

**Summary:** The paper is a position/formal-framework paper. It defines a contract C=(I,O,S,R,T,Φ,Ψ) with a lifecycle DRAFTED→ACTIVE→{FULFILLED, VIOLATED, EXPIRED, TERMINATED} (p6-8). It also defines conservation laws for delegated budgets, Σ c_j ≤ B (p10-11). Four experiments use the authors' own implementation on Google ADK or LiteLLM, with Gemini 2.5 Flash and Flash-Lite (p14). Statistics use bootstrap CIs with 10,000 resamples (p14).

- **Code Review:** n=70 LiveCodeBench problems (31 easy, 39 medium). Each problem runs twice, once CONTRACTED (50K tokens, max 3 iterations) and once UNCONTRACTED (max 6 iterations) (p14-15).
- **Research Pipeline:** n=50 topics, a 3-agent Researcher→Analyzer→Reporter chain, with quality scored by multiple LLM judges (p14-16).
- **Strategy Modes:** n=50 OpenR1 logic puzzles, 3 modes (p16).
- **Crisis Communication:** n=24 scenarios (p15).

The paper states no seeds or repeated runs, so each condition looks like a single run per item.

**Ledger table:**

| Claim/number as used in our docs | Exact figure in paper | Page | Setup/caveat | VERDICT |
|---|---|---|---|---|
| SCHEMA.md:70, `budget` row: "only a per-call token cap binds within a call (2601.08815 **A** p12-13)" | p12: "Token consumption is only known after an LLM call completes"; "contracts cannot prevent a single expensive call from exceeding budget, contracts can prevent subsequent calls after budget is exceeded, and the primary value is therefore multi-call protection." p13 table: "Cost ceilings / Approx / Track cumulative cost; bound via max_tokens". p13, soft enforcement is "best-effort—agents may ignore or exceed stated constraints". p14: "hard enforcement between actions and soft enforcement within them." | 12-14 | This is an argument from API design, not an experimental result. The paper names max_tokens only once, as an *approximate* bound on cost ceilings. It never says in its own words that a per-call cap is the *only* control that binds within a call; that is our inference. p13 also notes "some providers now offer cumulative token counts during streaming", but the missing piece is "interruptible generation". | **Correct in substance, slightly overstated in wording.** Suggested text: "within a single call, contracts cannot stop an overrun; hard enforcement acts only between calls, and max_tokens gives an approximate per-call bound (2601.08815 **A** p12-14)". The page range should be p12-14, since the "between actions / within them" sentence is on p14. |
| companion.md:119, `budget`, `children` row: "limits per call and in total, of which only the per-call cap binds within a call (Agent Contracts, **A**)" | Same as the row above. For "in total": p13 table "Multi-call budgets / Full / Stop after cumulative threshold". Conservation laws hold with "zero conservation violations across all 50 trials" (p15). | 12-15 | Same caveat. `children` (composite capsules pinned by hash) is not from this paper. | **Correct in substance, slightly overstated** (same fix). It is unambiguous: it says "Agent Contracts", not "Agent Behavioral Contracts". |

Only these two citations exist. `grep` for "2601.08815" and "Agent Contracts" over both files found SCHEMA.md:70 and companion.md:119, and nothing else. companion.md:261 "Agent Behavioral Contracts (**A**) declares preconditions as checks" refers to the other paper (2602.22302) and is excluded. No citation was ambiguous between the two.

The `budget` sub-fields {time, tokens, money, concurrency} are not attributed to the paper. The paper's own resource dimensions are tokens, API calls, iterations, web searches, compute time and USD cost (p7); it has no concurrency dimension.

**Other findings relevant to these themes (with page numbers):**

**(a) Declaring behaviour and checking it before use vs. observing it after use (safety):**
- Contracts declare bounds before activation, following "contract algorithms [68], which specify computation budgets before activation" (p3).
- But token use is "stochastic and observable only after the fact" (p3), and "only known after an LLM call completes" (p12).
- Hard enforcement is after-the-fact: "an external monitor tracks consumption after each action and halts execution" (p13).
- The skill set S is declarative: "an agent contracted for data analysis cannot invoke payment APIs even if technically accessible" (p7). This is stated but never tested.
- Safety appears only in related work (p4). The paper distinguishes formal verification, which checks "whether systems satisfy properties", from contracts, which "specify what resource constraints systems must satisfy" (p4-5).

**(b) Token/context cost of exposing many tools/skills:**
- There is one secondary mention, citing an Anthropic skills blog [8]: progressive disclosure loads metadata at "~50 tokens" initially and full specs at "~500+ tokens" on demand (p7). The text extraction garbled this passage into LaTeX, so the figures should be checked against the PDF.
- The paper does not measure this itself.

**(c) Precondition or contract checking, and parity between a filter and the executed thing:**
- Input spec I includes validation rules V_I, e.g. "pr_id > 0" (p7).
- The lifecycle has formal guard conditions such as "activate() ∧ resources_available()" (p8).
- Per-tool limits and Σb_i ≤ B are enforced "at allocation time" (p14).
- Parity between a selection filter and the executed thing is not discussed.

**(d) Library growth/retirement:** not discussed.
- The closest material is "dynamic agent instantiation", where the contract is "the specification for agent creation, not just selection" (p11-12).
- The paper also mentions routing by matching task needs against specialist contracts (p11).

**What the paper does NOT support:**

These are the authors' stated limits:
- Within-call enforcement is impossible with current APIs (p12).
- Soft enforcement is "best-effort", citing "token elasticity" (p13).
- Real-time enforcement would need "interruptible generation", "token reservation" and "budget-aware inference" (p13-14).
- Code Review results: CONTRACTED success fell by 7.1pp (60.0%→52.9%). The authors call this "not statistically significant (p = 0.13)" (p15).
- Research Pipeline: the 26.7× lower quality variance is "partly driven by one catastrophic failure" in UNCONTRACTED. Without that failure it is only 1.4× (88.5% Bayesian probability) (p16).
- Strategy Modes: the 86% vs 70% result has p≈0.05 (p16).
- Future work lists runtime cancellation, learned contract design, formal verification of contracts, human-in-the-loop contracts, and milestone-based governance (p17).
- The implementation "is under active development" (p14 fn 3).

These limits are not stated by the authors:
- Only one model family (Gemini 2.5 Flash/Flash-Lite) was tested.
- n is small (24-70).
- No seeds or replications are reported.
- Table 1's framework feature matrix is the authors' own reading of framework docs (p5-6).

Overreach in our docs is mild. The word "binds" and "only the per-call cap" go slightly past the text, which calls max_tokens "Approx" and frames it as the bound on cost ceilings. The docs do not borrow any of the headline numbers (90% token reduction, 525× variance, 0 violations), so the paper's results are not overclaimed.

**Figure candidates for appendix:** The paper has no figures. Every visual is a text table, so all are vector/text and none is a raster image. Only one table is numbered.

- p13: enforcement table (Multi-call budgets Full … Cost ceilings Approx, "bound via max_tokens"). This is the best candidate because it directly backs our citation.
- p12: the c_tok(t) "unknown during API call / c_actual after API returns" equation plus the three consequences. This is the source text for our claim.
- p5-6, Table 1: governance features across 8 frameworks.
- p8: lifecycle guard-condition table.
- p15: Code Review results table (tokens 34,606→3,461, variance 5.29B vs 10.1M).
- p16: Strategy Modes table.
- p17: component-to-experiment validation table.

---

## Agent Behavioral Contracts: Formal Specification and Runtime Enforcement for Reliable Autonomous AI Agents (arXiv 2602.22302)

**Read confirmation:** `wc -l` gives 4534 lines. I read lines 1–4534 in order, in chunks of 700 lines, and reached the true end: line 4534 is the page number "71", after Figure 7. All 71 PDF pages are covered: main text pp1–54, the Appendix A proofs pp54–62, the author bio p62, references pp62–66 and the late figures pp67–71.

**Summary:** One author (Bhardwaj, Accenture). The paper is "Patent pending" and says the code and benchmark are "available subject to intellectual property clearance" (p1), so nothing is released. It defines a contract C = (P, I_hard, I_soft, G_hard, G_soft, R), a probabilistic (p,δ,k)-satisfaction, an Ornstein–Uhlenbeck drift bound D* = α/γ, and composition theorems. It also presents ContractSpec, a YAML DSL, and AgentAssert, a Python runtime of about 3,000 lines.

- **Synthetic benchmark:** AgentContract-Bench has 200 synthetic traces of 5–8 steps and "does not involve live LLM inference" (p24).
- **Live experiments:** 7 models, all through Azure AI Foundry (p32, 34): GPT-5.2, Claude Opus 4.6, DeepSeek-R1, Grok-4 Fast, Llama 3.3 70B, Mistral Large 3 and GPT-4o-mini. GPT-4o-mini is also the only primary judge.
- **Domain:** one domain only, the financial-advisor contract, with 10 tasks.
- **Runs:** each condition is 10 tasks × 3 runs, which gives 30 sessions. The only seed mentioned is "seed=42" for task ordering (p33). Models run at default temperature (p49).
- **Experiments:**
  - E1: 420 sessions of 6 turns, all 7 models.
  - E2: 240 sessions of 12 turns, 4 models.
  - E3: 720 adversarial sessions.
  - E4: 600 ablation sessions.
  - These add up to 1,980 sessions (p52).
- **Costs:** E1 cost "$3.09" for 10,304,105 tokens (p35).

**Ledger table:**

| Claim/number as used in our docs | Exact figure in paper | Page | Setup/caveat | VERDICT |
|---|---|---|---|---|
| companion.md:261 — "Agent Behavioral Contracts (**A**) declares preconditions as checks" | Def 3.1: "P = {p1,…,pm} is a finite set of preconditions: predicates over the initial state s0 that must hold before the agent begins execution". ContractSpec: "Each constraint specifies a check block containing a field path and an operator". The YAML example has `preconditions: - name: required-initial-state  check: {field: ..., operator: ...}` | p8; p21–22 | Checked once, on the initial session state s0. There is no selection or library. The experiments never evaluate preconditions: F3 checks constraints "excluding preconditions and recovery strategies" (p30). There is no public code (p1, p20). | **Correct.** It is a design claim only, since no precondition checking was measured. The citation should add the arXiv id and a page (e.g. "2602.22302 **A** p8, p21"), as the GraSP citation beside it has an id. |
| companion.md:261 (same sentence, the paper's implied place in the comparison) — "None of the systems read ties one declaration to admission into a library and to selection, bound by hash to what a run pins" | ABC has no library, admission, selection, versioning or hashing. The declaration feeds per-turn runtime monitoring (p22) and serial composition (C1–C4, p17). | p17, p22 | — | **Correct** as far as ABC goes. |

No other citation exists in either document. I searched both for "2602.22302", "Behavioral Contract", "Behavioural", "behavio" and "contract". The only mention is companion.md:261, and SCHEMA.md does not cite the paper at all.

The two "contracts" papers are cited unambiguously:
- SCHEMA.md:70 cites "2601.08815 **A** p12-13" (Ye & Tan, "Agent Contracts"), not this paper.
- companion.md:119 says "(Agent Contracts, **A**)" about budgets and the per-call cap. By title and topic that is also 2601.08815; ABC itself describes Ye & Tan as the resource-contract paper (p4).
- Only companion.md:261 names "Agent Behavioral Contracts". None of the citations is ambiguous.

A side note for the schema: SCHEMA.md:63's precondition shape `check {path, operator, value}` closely matches ContractSpec's `check: {field, operator}` (p21). SCHEMA.md does not cite ABC as prior art for that shape.

**Other findings relevant to these themes:**

(a) **Declaring behaviour before use vs observing it after (safety)**
- The paper calls itself "specification-first": contracts "are defined declaratively via ContractSpec before deployment, rather than inferred … or evaluated post-hoc from execution traces" (p5). It calls ABC "proactive" and Pro2Guard "reactive" (p6).
- In practice, though, enforcement is per-turn monitoring of observed state after each action (p22–23). The E1 evaluator is an LLM judge on outputs (p30).
- Hard violations "are logged without recovery attempts" (p30). This contradicts hypothesis H3a, that the monitor "intercepts and blocks non-compliant actions before they reach the user" (p41).
- Limitation L3: by default AgentAssert "detects violations but does not correct them" (p48).
- The headline "transparency effect" is framed as making violations measurable, not preventing them (p35–36):
  - Contracted agents: "5.23–6.83" soft violations per session.
  - Uncontracted agents: "0.00–0.30", computed post hoc by replaying through the same evaluator.
  - Soft compliance: contracted C_soft 0.829 vs uncontracted 0.982 (p35).
  - The contracted condition also injects the rules into the prompt (Table 6, p29), so the two conditions differ in more than monitoring.
- "False sense of security": "The contract evaluates only what is specified; unspecified behaviors are unmonitored" (p50).
- Platform filters blocked "40–60%" of legitimate sessions when contract wording was in the prompt (p33).

(b) **Token/context cost of exposing many tools/skills:** not discussed. The paper measures only enforcement overhead: "below 10 ms per action" at k=12 (p46), "below 25 ms" at k=100 (p46, Fig 5), and O(k+|A|) complexity (p19). It never measures the prompt-token cost of injecting the contract rules.

(c) **Precondition or contract checking, and filter/execution parity**
- Deterministic satisfaction includes "Precondition validity … ∀p ∈ P : p(s0) = true" (p9).
- Composition condition C2, assumption discharge: "PostCond_A ∧ I_handoff ⇒ P_B" (p17).
- C4, recovery independence: after A's recovery, B's precondition must still hold. The paper calls C3 and C4 novel (p17–18).
- The benchmark's composition tier includes "C2: Assumption failure (8 scenarios)" and "C4: Recovery coordination failure (11 scenarios)" (p26). That tier has the lowest Θ (0.8865) and C_hard (0.8603) (p27).
- "Schema validation rejects malformed contracts before runtime evaluation" (p22).
- Parity of the measuring instrument across conditions: F3, "same evaluator instance" (p30).
- The benchmark's "detection accuracy of 1.0000" is admitted to be circular (L6, p48–49).
- L1, state dictionary: the evaluator needs pre-computed fields and "does not compute these features from raw agent output" (p47). This bears on a `state_source` field.
- There is no selection filter, so parity between a filter and the executed thing is not discussed.

(d) **Library growth/retirement:** not discussed. Loosely related points:
- L2 raises the question of when the reference distribution "becomes stale and needs recalibration" (p47–48).
- Appendix A.5 gives certification sample sizes: the SPRT expects "≈159" sessions against a Hoeffding baseline of "≈18,445" (p61–62).

**What the paper does NOT support:**

The authors' own limitations:
- L1: state dictionary assumption (p47).
- L2: reference calibration with no staleness handling (p47–48).
- L3: recovery is monitoring by default (p48).
- L4: the drift bound assumes stationarity, and the 6-turn E1 sessions may be transient (p48).
- L5: composition fails under correlated failures when agents share an LLM (p48).
- L6: benchmark circularity (p48–49).
- Threats (p49): a single prompt template, temperature not explored, one domain ("generalizability to other domains … is not established empirically"), and metrics that are "contract-relative" (p49–50).
- Conclusion (p53): heuristic state extraction, only financial-domain evaluation, and judge cost.

Internal problems I noticed, which matter if anyone cites its numbers:
1. The human annotation κ results are promised as "reported in Section 8" (p31) but never appear.
2. SPRT certification is listed as a contribution (p52), but it exists only as an appendix proof sketch. Figure 7 (p71) uses p0=0.85 with Hoeffding n=1060, which does not match the text's p0=0.90 and ≈18,445 (p61).
3. The conclusion says each component contributes "a 0.19–0.22 drop … with no single component being redundant" (p52). The ablation shows Hard Only and Drift Only raise Θ, which the authors explain as vacuous scoring (p43–44).
4. The conclusion says drift was "stabilizing near the theoretical bound D*" (p52). Yet the fitted D* in Fig 3 is 0.259–0.500 (p67), above the observed maxima of 0.144–0.264, and drift "rises" in the second half of sessions (p38).
5. The abstract's "D* < 0.27" is the observed maximum of 0.264, not a fitted D*.
6. The "Rath 2024" reference is arXiv:2404.00000, which looks like a placeholder (p65).

Overreach in our docs: none in the text as written. It would be overreach to imply that ABC checks preconditions in practice (the experiments excluded them, p30) or before selection (they are checked at session start, s0). It would also be overreach to cite ABC as evidence that declared checks improve safety: its evidence is about detecting violations under a GPT-4o-mini judge, in one domain.

**Figure candidates for appendix** (all figures appear vector: axis labels and values come through as text):
- p21–22: ContractSpec YAML listing (a code block, not a figure). Most relevant: it shows the preconditions declared as `check {field, operator}`. Vector/text.
- p8: Definition 3.1, the contract tuple (text).
- p7: Table 1, feature comparison of ABC, AgentSpec, Pro2Guard, Agent-C, VeriGuard, AIR and Ye '26. Vector table.
- p25: Table 3, the benchmark's domain breakdown, including the composition tier.
- p27: Table 4, benchmark validation results.
- p29: Table 6, contracted vs uncontracted conditions. This shows the prompt-injection confound.
- p35: Table 9, E1 results for 7 models. p37: Table 10, effect sizes.
- p38: Figure 1, bar chart of Θ by model (E1). Vector.
- p39: Table 11, E2 drift. p40: Figure 2, drift trajectories over 12 turns, 4 panels. Vector.
- p41: Table 12, E3 stress. p43: Table 13, ablation. p44: Table 14.
- p67: Figure 3, OU fit per model (R² 0.49–0.75). Vector.
- p68: Figure 4, ablation heatmap (its internal title mislabels it "Figure 3"). Vector labels; the cells may be raster.
- p69: Figure 5, overhead against constraint count k (linear fit 0.218k + 2.8 ms). Vector.
- p70: Figure 6, recovery impact on Θ. Vector.
- p71: Figure 7, SPRT against fixed-sample certification. Vector.

---

## Beyond Task Completion: A Verification-vs.-Conformance Gap in Tool-Evolving Agents (arXiv 2604.00392)

**Read confirmation:** I read all 752 lines of `papers/2604.00392.txt` with Read (lines 1–400, then 400–752). The last line is 752, the tail of the `deserialize_tpack` listing in Appendix A.2. That is the true end of the file (wc -l = 752). The text has 12 pages. I worked out page numbers from the running headers, and the ledger uses these: p1 lines 1–60, p2 61–130, p3 131–193, p4 194–263, p5 264–325, p6 326–386, p7 387–459, p8 460–537, p9 538–590, p10 591–665, p11 666–743, p12 744–752. The source is arXiv v2, dated 4 Jul 2026.

**Summary:** The authors are Kaliyev (UT Austin) and Maryanskyy (Uber). The paper introduces EvolveTool-Bench, a benchmark for agents that build their own tools during a session.

- **Benchmark shape:** 99 tasks in 3 domains and 9 sessions of 11 tasks. Each session runs seed, gap, variant, compose, regress and adversarial roles.
- **Main pilot:** only the verified subset: 8 sessions and "51 verified task decisions per pass". The API-orchestration session is excluded because its verifiers are unfinished.
- **Model and seeds:** only Claude Haiku 4.5 (`claude-haiku-4-5-20251001`), temperature 1.0, seeds 0, 1 and 2. That gives 24 session rows per protocol, 120 in total.
- **Protocols:** five: No-Evolution, One-Shot, EvoSkill-style, ToolMaker-style and CREATOR-style. The last three are adaptations, not faithful ports.
- **Library state:** resets between sessions, so libraries grow within a session only.
- **Statistics:** 3 contrasts registered in advance, bootstrap with B=10,000 and BH correction.
- **TC result:** task completion (TC) does not separate the protocols. It ranges from 0.287 to 0.358. The one nominally significant contrast is CREATOR − One-Shot at −7.1 pp, CI [−13.9, −0.1], which does not survive BH (adjusted p 0.133) (p4).
- **Headline result (§5.3, Table 5, p5):** a separate re-run of the same matrix kept each tool's source. It replayed each tool against a held-out conformance suite for its capability: 10–22 inputs, median 11.
  - 215 of 222 preserved tools (96.8%) score C=0.00.
  - Hand-written reference implementations score C=1.00 on all 16 suites.
- **Other material:**
  - Supplement D: a single-tool Sonnet trace, TC 0.95 with C=0.00.
  - Supplement E: library-health contrasts from a Sonnet pilot with 4 seeds and 9 sessions.
  - Appendix A: a gallery of the Sonnet tools' code.

**Ledger table:**

| Claim/number as used in our docs | Exact figure in paper | Page | Setup/caveat | VERDICT |
|---|---|---|---|---|
| SCHEMA.md:48–49: "215 of 222 self-built tools that raised no in-session flag failed held-out tests of their own job (2604.00392 **M** p5; one model, 3 protocols, 3 seeds)" | Abstract: "96.8% (215 of 222) record per-tool correctness 𝐶=0.00". Table 5: One-Shot 119 tools at 100.0%, ToolMaker-style 19 at 100.0%, CREATOR-style 84 at 91.7%, "Total 222 … 96.8%". "The rot is silent because no in-session signal flags it" | p1 (abstract), p5 (Table 5, lines 278–283, 293–298) | Haiku 4.5 only, 8 sessions × 3 seeds. The probe is a separate re-execution of the Table 3 matrix, so the counts differ from Table 3. C=0.00 means wrong on every held-out input. Robustness R is only 0.52–0.54: the tools run without crashing on about half of the adversarial probes. "No in-session flag" is the paper's general argument that the verifier scores task outputs, not tools. It was not measured tool by tool. A defective tool can still be "rejected only indirectly, when a task that leaned on it fails" (p5), and about two-thirds of reuse calls coincide with task failure (p5) | **correct** (number, page, model, protocols and seeds all match). Slightly **overstated** in "raised no in-session flag": the paper says no signal flags the *tool*, but failing tasks can signal indirectly. Suggest "that no in-session check flagged". Could also add "8 sessions" |
| SCHEMA.md:49: "so provisional outputs are never trusted unchecked" (conclusion drawn from the above) | not in paper | — | Our design conclusion | **correct as design**, not a paper claim. Fine as worded, since the sentence attributes only the number to the paper |
| SCHEMA.md:64 (`postconditions`): "tests of the capsule's own job (2604.00392 **M** p5)" | "replayed every synthesised tool against the held-out conformance suite for the capability it was created for"; "the conformance suite draws from the capability's full contract" | p5 (lines 279–280, 316) | The suites are per capability (16 suites), applied to each tool | **correct** |
| SCHEMA.md:103, admission rule 3: "Running without error is never an anchor (2604.00392 **M** p5)" | "silent-rot tools execute cleanly and return values; the values are simply incorrect"; "(iv) Tools are syntactically valid: 𝐶=0.00 means wrong on every held-out input, not crashed" | p5 (lines 288–290, 324–325) | The paper's evidence that clean execution does not imply correctness. The rule itself is our design | **correct** (supported as the reason; the rule is our design). Caveat: "execute cleanly" is loose, since mean R is about 0.52 |
| companion.md:47, heading: "215 of 222 self-built tools fail tests of their own job" | as above | p1, p5 | as above | **correct** |
| companion.md:55: "215 of 222 self-built tools that raised no in-session flag fail held-out tests of their own job. One model, Haiku 4.5, 3 tool-building protocols, 3 seeds" | as above; "All verified-subset runs use Claude Haiku 4.5"; "three integer seeds (0, 1, 2)" | p1, p3 (lines 170–173), p5 | Same "no in-session flag" nuance as the SCHEMA row. Omits 8 sessions | **correct**; the same slight **overstatement** on "no in-session flag" |
| companion.md:113: "tests of the capsule's own job (Beyond Task Completion, **M**)" | as SCHEMA:64 | p5 | — | **correct** |
| companion.md:272: "a kept capability's own job is tested. In Beyond Task Completion (**M**), 215 of 222 self-built tools failed theirs" | as above | p1, p5 | "Kept" fits: these are the tools preserved in the per-session library. "Failed theirs" means C=0.00 on every held-out input. 7 of 222 scored above zero, and only one reached C=1.00 | **correct** |
| companion.md:296, "Already built in a paper" for "held-out admission tests": "a conformance suite per tool (Beyond Task Completion, **M**)" | "per-tool conformance layer the framework defines" (p5); suites exist per capability, "all 16 capability suites" (p1, p5) | p5 | The paper built held-out conformance *replay*, run after the sessions for audit and benchmarking. It did not build an *admission* gate: tools entered the library without it. The paper only proposes release gates for monitoring (p6: "Each signal is a thresholded check that can sit behind a release gate") | **overstated**. Should say: "a held-out conformance suite per capability, replayed on every tool after the run (audit, not admission)" |

**Other findings relevant to these themes (with page numbers):**

(a) **Declaring behaviour and checking it before use vs. observing after use.** The paper is entirely about observing after use.
- Held-out conformance replay after the sessions, plus audit traces (Fig. 1, p3).
- A proposed post-deployment monitor: re-emit `run_manifest.jsonl` / `tool_manifest.jsonl` each release, with three "thresholded" signals ("silent rot", "reuse trap", "regression delta") that "can sit behind a release gate" (p6).
- A pre-declared contract appears in one place: conformance tests "are authored alongside the gap task that introduces a capability, before any tool exists" (p5). This bears on our "author never saw the implementation" rule, but the paper does not frame it as admission.
- There is no admission-before-use gate. Safety and harm are not discussed.

(b) **Token/context cost of exposing many tools:** not discussed. The only cost remark is that audit overhead is "millisecond-scale latency and bounded disk I/O" (p6).

(c) **Precondition or contract checking; filter-vs-executed parity:**
- Preconditions are not discussed.
- There is a contract theme: the in-session verifier "scores the one call the task needed", while conformance "draws from the capability's full contract" (p5). They see "different input distributions … TC is computed on the distribution the agent saw, conformance on the distribution the next release will see" (p5).
- This is a verifier-vs-contract gap, not filter-vs-execution parity.

(d) **Library growth/retirement:**
- Generated tools "can be reused, duplicated, retired, or accidentally made into load-bearing dependencies" (p6).
- Recommendations: "(5) include regression and composition probes after library growth; (6) evaluate library-management policies such as promotion, deduplication, and retirement" (p7).
- The framework includes redundancy and utilisation diagnostics, but they are not reported for Haiku (p3). Library health (LH) combines correct reuse, redundancy, utilisation, composition, regression and a hidden-test gate, reported only in the Sonnet supplement (Table 8, p9).
- The gallery marks a "Duplicate (synthesised across multiple sessions)" (p10).
- No retirement policy is evaluated. Libraries reset between sessions, so long-run growth is not studied (p3).

**What the paper does NOT support:**

- **Limits the authors state (§7, p6):**
  - Only 8 sessions and 51 decisions are verified, not all 99 tasks.
  - "one model (Claude Haiku 4.5) and three integer seeds"; outcomes are partly seed-stable, so the effective n is 8–24 (p4).
  - The null TC result means "no large protocol effect at this scale" rather than "no effect". Power is 80% for 8–13 pp, and effects under about 7 pp cannot be ruled out (p4).
  - The three -style protocols are adaptations, "not a verdict on the original methods" (p6, p8).
  - The conformance probe is "single-model: held-out correctness at Sonnet or larger models could change the silent-rot rates" (p6).
  - A composite library-health score is "premature" (p6).
  - The Sonnet LH magnitudes "should not be transferred" to Haiku (p9).
  - The cross-model evidence is one Sonnet tool at session granularity (p6, p8).
- **Where our docs overreach:**
  - The 96.8% should be read as a Haiku-4.5-scale rate of unvalidated synthesis. The authors say the gap is "a systematic property of unvalidated synthesis at Haiku scale" (p5). It is not a general rate for self-built libraries. Our "one model" caveat partly covers this; "8 sessions, Haiku scale" would be tighter.
  - "Raised no in-session flag" is the paper's argument, not a per-tool measurement (see table).
  - companion.md:296 presents the paper as having built held-out *admission* tests. It built post-hoc held-out *evaluation*.
  - The paper does not show that admission gates improve TC or library quality. No gated protocol was tested. ToolMaker-style has a validation loop, yet still has 100% silent rot (19 tools, p5) and no TC gain (p4).
- **Internal inconsistencies in the paper:**
  - Supplement A cites "Table 3" for the contrasts, which are in Table 4 (p8).
  - The appendices are lettered A–E, then a second "A Artifact Gallery" (p10).

**Figure candidates for appendix:**

- **p5, Table 5:** held-out conformance per protocol (tools, mean C, mean R, silent rot %: 119/19/84/222 and 100/100/91.7/96.8%). The key figure for our claim. Vector/text table.
- **p1, abstract:** "215 of 222" and the reference suites at C=1.00. Text.
- **p4, Tables 3–4:** TC per protocol (0.287–0.358) and the contrasts registered in advance. They show TC failing to separate the protocols. Vector tables.
- **p3, Figure 1:** one audit-trace JSON record (schema). A text/code listing, so vector. Useful for our certificate and trace design.
- **p3, Table 2:** verifier coverage by role (51/64 = 79.7%). Vector.
- **p7, "Reusable Evaluation Practices" box:** six recommendations, including retirement. Text.
- **p9, Table 8:** Sonnet library-health contrasts. Vector.
- **pp10–12, Appendix A gallery:** code listings of tools with high Q and low C ("looks well-formed, fails on hidden inputs"). Text.
- The extracted text shows no raster images.

---

# GraSP: Graph-Structured Skill Compositions for LLM Agents — arXiv:2604.17870

**Read confirmation:** Read end to end via the Read tool in chunks (offsets 1-500, 500-1000, 1000-1500, 1500-2170), file has 2170 lines. Last content is Appendix G "Broader impacts" on page 16 (the paper's final page, ends "We do not foresee significant negative societal impacts specific to this work."). Total 16 pages including abstract, main text (pages 1-8), Limitations (page 9), references (pages 9-11), and appendices A-G (pages 11-16).

## Summary
GraSP (GRASP) is a Tencent paper proposing an "executable skill graph architecture" for LLM agents: a compilation stage that turns a flat, retrieved set of skills into a typed DAG whose edges are `state` (an effect of one skill satisfies a precondition of another), `data` (output binds input), and `order` (soft precedence). Execution traverses the DAG in topological order, checking preconditions before running a skill and postconditions after, with five typed local-repair operators (REBIND, INSERTPREREQ, SUBSTITUTE, REWIRE, BYPASS) that patch only a bounded local neighborhood on failure, plus a confidence-gated fallback to ReAct. Evaluated on ALFWorld, ScienceWorld, WebShop, and InterCode (NL2Bash split) with eight LLM backbones (DeepSeek V3.2 primary, GPT-4.1, Claude-4-Sonnet, GLM-5, Gemini 2.5 Pro, o4 Mini, Qwen3-235B, Kimi-K2.5), all accessed via API at temperature 0.0, **results averaged over 3 runs per cell** (Table 1 caption, "Runs per cell" = 3 in Table 3, p13). Baselines: ReAct, Reflexion, ExpeL, and ReAct+Skills (flat skill list, same library/memory as GRASP).

## Ledger table

| Claim in our docs | Exact figure in paper | Page | Setup/caveat | Verdict |
|---|---|---|---|---|
| companion.md: "GraSP (arXiv 2604.17870, not read in full) declares precondition and effect edges" | Definition 1: edges `E ⊆ V × {state, data, order} × V`; "State edges (u, state, v): an effect of u satisfies a precondition of v." Abstract: "typed directed acyclic graphs (DAGs) with precondition–effect edges" | p1 (abstract), p2 (Def. 1), p3-4 (§2.3 edge types) | Core architectural claim of the paper, not a side finding | **Correct.** This is an accurate one-line characterization of GraSP's central mechanism — the paper's entire framing is edges that encode precondition-satisfies-by-effect relations between skill nodes in a DAG. The companion doc's honest "(not read in full)" flag is now resolved by this full read; the claim holds. |

No other SCHEMA.md/companion.md citation gives a specific number from this paper — it is used only for the one-line "declares precondition and effect edges" characterization in the "Similar designs" table (companion.md line 261). No further numeric claims from GraSP are cited in either document, so no other ledger rows apply.

## Other findings relevant to the four themes

**(a) Declaring behaviour and checking it before use, vs. observing behaviour after use.** GraSP checks preconditions and postconditions *at each node before/after executing that node*, not before admitting the skill to a library — i.e., it's runtime/in-episode verification, not pre-admission testing. "Precondition check: verify `xt |= ϕpre_v`" happens immediately before executing that step (p4, §2.4, step 1 of the per-node loop), and "Postcondition verification: check `νv(xt, xt+1)`" happens immediately after (p4, step 3). This is closer to a gate than to admission-time contract testing — relevant as a *contrast* case for the schema's admission-before-any-run model, since GraSP's checks are per-call, in-run, not a held-out test before the capsule enters a library.

**(b) Token/context cost of exposing many tools/skills.** Finding 7 (p7): "flat execution peaks around M=3 and declines with more skills, dropping by ∼6% at M=8," while GRASP "degrades gracefully" and still beats flat-at-its-optimum even at M=8 (79.4 vs 74.9). Mechanism given: "flat agents dump all retrieved skills into the prompt, and irrelevant skills compete for the LLM's attention, causing distraction and hallucinated action sequences. DAG compilation acts as a structural filter: skills that cannot be connected via precondition–effect edges are automatically excluded from the execution graph" (p7). Figure 5 / Finding 8 (p7) also reports LLM-call cost by pipeline stage as skill quality degrades (Retrieval/Compilation/Execution/Repair/Total call counts, e.g. Total calls 11.7→9.0→7.6 as quality goes Low→Medium→High, ALFWorld/DeepSeek V3.2).

**(c) Precondition/contract checking, parity between a filter and the executed thing.** The compilation stage is exactly this: "The compilation process uses an LLM to propose skill invocations, validates argument bindings against the library, infers edges from precondition–effect matching and memory-induced precedence priors, resolves cycles by removing low-confidence soft edges, and attaches verifiers. If compilation fails, the system falls back to reactive control" (p4, §2.3). Executability is a defined graph property: "every node has bound schema, arguments, and verifier" (Definition 1, p2). Finding 5 (p5): typed repair recovers from precondition failures at 84.2% vs 61.8% for global replanning (+22.4%), because "typed edges encode why a node failed, so a missing precondition triggers targeted re-retrieval of the upstream producer" — a real precondition-vs-executed-state parity mechanism, though checked at runtime, not pre-admission.

**(d) Library growth/retirement.** Not really addressed. GraSP is about compiling a *retrieved subset* of an existing static skill library into a graph per task, not about growing, certifying, or retiring library entries over time. No mention of a library evolving, being pruned, or capsules being retired — this paper is silent on the librarian-type concerns SCHEMA.md cares about.

## What the paper does NOT support (stated limits)

Section 6 "Limitations and discussion" (p9):
- **DAG expressiveness**: "The DAG assumption precludes cyclic execution patterns. While most interactive tasks decompose naturally into acyclic subgoal sequences, tasks requiring iterative refinement (e.g., repeated measurement-adjustment cycles) may require extensions such as loop constructs or DAG unrolling."
- **Broader applicability**: results are on "four text-based interactive environments" only; multimodal (visual nav, GUI), real-world API-based tasks, and multi-agent coordination are claimed as "directly applicable" but *not tested* — this is a forward-looking claim, not evidence.
- Implicitly: all evaluation is simulated-environment (household/science/web/bash text sims), not production tool ecosystems; all models called via API at temperature 0.0 (no sampling diversity); 3 runs per cell is a fairly thin seed count for the headline numbers (e.g. +19 points, 41% step reduction) given the granularity of per-condition breakdowns.
- The paper explicitly frames itself as declaring "no significant negative societal impacts" (Appendix G, p16) — a broader-impacts boilerplate, not a technical limitation.

## Figure/table candidates for an appendix

| Page | Fig/Table | What it shows | Raster or vector (guess) |
|---|---|---|---|
| p3 | Figure 1 | Overview: flat execution vs GRASP DAG compilation, 4-stage pipeline diagram | Vector (schematic/diagram) |
| p6 (Table 1 spans pp6-7 in the raw text extraction) | Table 1 | Main results: reward/steps across 4 benchmarks × 5 methods × 8 backbones | Vector (text table) |
| p6 | Figure 2 | (a) GoS advantage vs ExpeL grows with task complexity (bar chart); (b) typed repair vs global replan recovery rate by failure type (bar chart) | Raster-looking bar charts, but likely vector/matplotlib output |
| p7 | Table 2 | Component ablation on ALFWorld/ScienceWorld (DeepSeek V3.2) | Vector (text table) |
| p7 | Figure 3 | Repair escalation stacked bar chart (episode outcome distribution across 4 benchmarks) | Vector/raster bar chart |
| p7 | Figure 4 | Skill quantity vs reward (line chart, M=1..8) and skill quality robustness | Vector/raster line chart |
| p7 | Figure 5 | Multi-metric heatmap: skill quality × cost (reward and LLM-call count) | Vector/raster heatmap |
| p13-14 | Table 3 | Default hyperparameters (λ, k, M, η, τ_low, τ_high, h, Lmax, Emax, Rmax, Pmax, temperature, env-step budgets, runs-per-cell) | Vector (text table) — useful for methods appendix |
| p14 | Table 4 | ALFWorld per-task-type SR breakdown (Pick/Clean/Heat/Cool/Examine/Place) | Vector (text table) |
| p14-15 | Table 5 | ScienceWorld per-category reward breakdown (6 of 30 categories) | Vector (text table) |
| p14-15 | Case study (heating potato in ALFWorld) | Worked example of DAG compile → precondition-fail → INSERTPREREQ repair, with the actual edge diagram (`src -order-> find -state-> pick-up -data-> heat -state-> place -order-> snk`) | Good candidate for a small vector diagram illustrating "precondition–effect edge" mechanics concretely |

## Note for the ledger builder
No numeric claim from GraSP is actually cited with a page in SCHEMA.md or companion.md — SCHEMA.md never cites 2604.17870 at all (grep confirmed no hits), and companion.md cites it only once, for the one-line characterization verified above. So there is nothing WRONG or OVERSTATED to flag for this paper; the sole claim checked is CORRECT.

---

# 2605.06365 — From Agent Loops to Deterministic Graphs: Execution Lineage for Reproducible AI-Native Work

**Read in full:** yes, all 16 pages (line 1 to EOF at line 1032; references end at page 16, no appendix beyond references — this paper has no separate appendix section).

**Note on path:** the file requested at `C:\Users\m50066326\huawei\capsule-openjiuwen\papers\2605.06365.txt` does not exist; used the fallback `C:\Users\m50066326\huawei\tundle\ai4research\papers\2605.06365.txt` as instructed.

## Summary
This is a short systems/methods paper (Josh & Seth Rosen, ThruWire Inc.), not a large-benchmark paper. It proposes **execution lineage**: representing AI-native work as a DAG of artifact-producing nodes `v = (I_v, f_v, O_v)` with an explicit execution-identity hash `k_v = h(σ_v, x_v, {k_u : u ∈ pred(v)})` — a function of the node's structure, resolved inputs, and its immediate predecessors' identities — enabling identity-based replay and precise, dependency-scoped invalidation, as opposed to "prompt lineage" (implicit state carried in a conversational transcript). The empirical section is a small controlled mechanism study, not a benchmark: two policy-memo update tasks (an "unrelated-branch" no-op-update test and an "intermediate-artifact edit/propagation" test) in one telehealth-memo domain, three conditions (loop final update, loop + edit event, DAG replay), **n = 3 repeats per task-condition**, judged with 2 judge passes per repeat, using a single model (GPT-5.2, temperature 0.7) pinned to one repo commit. No cross-model or cross-domain generalization is tested.

## Ledger table

| Our claim | Paper's exact figure | Page | Setup/caveat | Verdict |
|---|---|---|---|---|
| SCHEMA.md B4 (Run pin): "Hashes and `upstream` let a revocation taint exactly the descendants (2605.06365 **A** p6-7)" | §3.3 (p6): execution identity `k_v = h(σ_v, x_v, {k_u : u ∈ pred(v)})`; "If `k_v` is unchanged, prior execution may be reused exactly. If it changes, downstream nodes that depend on `k_v` are invalidated and re-executed, while unrelated branches remain untouched." §3.7 Invalidation Semantics (p7): "If a retrieval source changes, analysis and synthesis must be invalidated because their dependency identities are downstream of the changed source." | p6 (formula + reuse/invalidation rule), p7 (worked invalidation example) | This is a single-workflow DAG model (per-run lineage), not a multi-run capsule library; SCHEMA.md is drawing the general mechanism (hash-based upstream tainting) as precedent for its own run-pin design | **Correct.** The exact mechanism — descendant invalidation driven by a hash that incorporates upstream identities — is defined on p6 and worked through on p7, matching the citation precisely. |
| companion.md (Backups, "Feasibility" table): "store, per-run pinning \| ScienceDiscovery's content-addressed store and prompt manifest \| step identities by hash (Execution lineage, **A**)" | Same formula, §3.3, p6: `k_v = h(σ_v, x_v, {k_u : u ∈ pred(v)})` is explicitly a per-node ("step") execution identity computed as a hash | p6 | — | **Correct.** |

## Other quantitative findings (not currently cited, potentially useful)
- **Table 1, unrelated-branch update (p10), n=3:** DAG replay: exact preservation 1.00, churn 0.000, contamination 0.000, **382 input tokens**, 1 model call, 7.9s. Loop final update: exact preservation 0.00, churn 0.923, contamination 0.667, **11,655 input tokens**, 1 call, 33.5s. Loop + edit event: exact preservation 0.00, churn 0.908, contamination **1.000** (i.e. contaminated in all runs), 11,694 tokens, 1 call, 55.0s. Text (p9): DAG replay used "about 30.5× fewer [tokens]" than loop final update and "30.6× fewer" than the edit-event loop; output tokens 440.7 (DAG) vs. 2189.3/2078.3 (loops); wall-clock ~4.2× and ~6.9× faster.
- **Table 2, intermediate-artifact edit (p10), n=3:** all three conditions reflect the new constraint (1.00) and score 1.00 faithfulness/current-state-precision, but cross-artifact consistency is 1.00 for DAG replay vs. **0.50** for both loop conditions; DAG replay alone reaches stable-artifact preservation 1.00, downstream-propagation recall 1.00, upstream churn 0.00. Here DAG replay uses *fewer* input tokens (8,461 vs. 11,404/11,464, ~1.35–1.36× less) but *more* output tokens (4,311.3 vs. 2,418.7/1,981.0) and is *slower* (73.6s vs. 38.7s/31.1s, i.e. ~1.9–2.36× slower) — "the results do not support a blanket claim that DAG replay is always faster" (p12, explicit paper caveat).
- **Sample-size/design detail (p9-10):** n=3 repeats per task-condition; semantic judging uses 2 judge passes per repeat; single model GPT-5.2 at temperature 0.7, pinned repo commit `f6cc8679ab1178b22fa01c263aa14e77454081ee`.

## Other findings relevant to the four themes
- **(a) Declare-and-check before use vs. observe after use:** Central design principle (§3.1, p5): "Explicit dependency declaration. A node should not be allowed to consume undeclared upstream state." "Identity-based reuse. Reuse should be based on **proof of equivalence**, not similarity of prompts or approximate resemblance of outputs." "This formulation differs from agent loops in two ways. First, the admissible context for each node is **declared before execution** rather than reconstructed opportunistically from conversational state." (p5) — a clean, on-theme statement of declare-then-gate for dependency consumption (not for safety/precondition checks specifically, but structurally analogous).
- **(b) Token/context cost of exposing many tools/skills:** Not about *tool* exposure, but has directly relevant token-cost numbers for *artifact*/context exposure: DAG replay's 382 vs. ~11.7K input tokens on the unrelated-branch task (Table 1, p10) is a striking ~30x reduction figure, currently unused in our docs. Caveated by the paper itself: on the other task, DAG replay is *not* cheaper on wall-clock or output tokens (Table 2, p10-11, §8.5 "Efficiency Tradeoffs," p12).
- **(c) Precondition/contract checking, parity between filter and executed:** Not directly about tool preconditions; closest analogue is "Identity-based reuse" (p5) and the execution-identity hash (p6) — a *structural* equivalence check (same declared structure + resolved inputs + upstream identities) gating whether a prior result may be reused, rather than a precondition/effect contract on tool calls.
- **(d) Library growth/retirement:** Not applicable — this is a single-workflow DAG lineage model, not a skill/tool/capsule library; there is no notion of admitting, capping, or retiring capability versions.

## What the paper does NOT support (§9.6 "What This Paper Does Not Claim," p13, and §9.7 Limitations, p13-14, authors' own words)
- "We do not claim that deterministic graphs replace all useful forms of agentic exploration. Open-ended discovery, broad brainstorming, and ambiguous early-stage problem framing may still benefit from unconstrained loops."
- "Nor do we claim that explicit execution structure by itself guarantees better one-shot answer quality. A poorly designed graph can still route bad prompts, weak tools, or misleading inputs."
- **Scope, explicitly stated (§9.7):** "This evaluation is intended as a controlled mechanism study rather than a comprehensive benchmark. It uses two controlled update tasks in one policy-memo domain, three system conditions, three repeats, and one model family... it does not establish broad performance claims across all agentic workflows."
- "The loop baselines are naturalistic but not exhaustive; stronger custom loop harnesses with explicit state tracking could narrow some gaps."
- "The DAG implementation is sequential, so wall-clock time does not always improve even when input context and recomputation are reduced." (Confirmed empirically in Table 2, where DAG replay is 1.9–2.36× slower.)
- "The graph must also be correctly specified: dependency mistakes, poor source routing, or lossy artifact interfaces can reduce the advantage."
- "The experiments expose a mechanism by which partial cross-artifact inconsistency could lead to state drift, but they do not directly measure multi-round accumulation; longitudinal revision studies are needed to test that hypothesis."
- "The results should not be read as evidence that DAG replay generally produces better prose than a holistic loop rewrite."
- No cross-model, cross-domain, or larger-n validation anywhere — single domain (telehealth policy memo), single model, n=3.

## Figure/table candidates for an appendix
| Page | Fig/Table | Shows | Raster/vector |
|---|---|---|---|
| p8-9 | Figure 1 | Agent loop (implicit memory/transcript) vs. execution lineage (explicit artifact DAG with A/B/C/D nodes, adjacent branch) comparison diagram | Vector (block diagram) |
| p10 | Table 1 | Unrelated-branch update results: exact preservation, churn, contamination, tokens, calls, wall-clock, n=3 | Vector (text table) |
| p10 | Table 2 | Intermediate-criteria-edit results: constraint reflection, cross-artifact consistency, propagation, tokens, calls, wall-clock, n=3 | Vector (text table) |
| p12 | Table 3 | Information boundaries by condition (what each condition receives: prior memo, sources, edit event, dependency graph, selective recomputation, oracle labels) | Vector (text table) |

---

# 2605.10990 — Skill Drift Is Contract Violation: Proactive Maintenance for LLM Agent Skill Libraries

**Read in full:** yes, all 22 pages (line 1 to EOF at line 1589; includes Appendices A–Q).

## Summary
The paper frames "skill drift" (an LLM agent skill silently breaking as its environment — APIs, packages, URLs, configs, credentials — changes) as **contract violation**, and introduces SKILLGUARD: it extracts an executable environment contract per skill, `c_i = (t_i, r_i, v_i, e_i)` (type, role ∈ {OPERATIONAL, INCIDENTAL}, value, evidence span), and validates only OPERATIONAL (role-bearing) assumptions, suppressing INCIDENTAL mentions (comments, badges, docs) before probing. Benchmark: DRIFTBENCH, 880 pairs (174 controlled/generated drifts + 107 real-world/LLM-free drifts + 599 negative controls, drawn from 49 real skills in SWE-Skills-Bench across 7 domains), with a 20% human audit (176/880 pairs, 14 corrections, zero label flips). Models: five backbone LLMs from four families — Qwen3.6-Plus, Qwen3-235B-A22B, DeepSeek-V3.2, DeepSeek-R1, GLM-5.1 — used as contract-extraction/detection backbones; Qwen3.6-Plus is *also* the model used to generate the controlled drift scenarios (422 candidate pairs → 174 validated, cross-checked by DeepSeek-R1 + registry evidence + author review, 99.6% adjudicated validity). All results are single-run point estimates with bootstrap (B=10,000) 95% CIs and Fisher exact tests for the repair ablation; no seed variation is reported.

## Ledger table

| Our claim | Paper's exact figure | Page | Setup/caveat | Verdict |
|---|---|---|---|---|
| SCHEMA.md A5: "`contracts[]` {contract_id, assumption, component, span}, after the paper's record of type, role, value and evidence span (2605.10990 **M** p5)" | "SKILLGUARD extracts an environment contract `C(S) = {c_i = (t_i, r_i, v_i, e_i)}`... where `t_i` is the contract type, `r_i ∈ {OPERATIONAL, INCIDENTAL}` is the role..., `v_i` is the value to validate, and `e_i` is the evidence span in S." | p5 (also restated as Table 3 notation on p12) | This exact 4-tuple is defined in the body text right where cited | **Correct.** The record is (type, role, value, evidence span), matching SCHEMA.md's paraphrase exactly, and it does first appear on p5. |
| SCHEMA.md A5: "recall was 24% to 76% across five backbones; the best also generated the drifts (2605.10990 **M** p4, p7)" | Table 2 (p7): Qwen3.6-Plus 100% prec / **76%** recall [62,88]; DeepSeek-R1 100%/62%; DeepSeek-V3.2 100%/57%; GLM-5.1 100%/54%; Qwen3-235B-A22B 100%/**24%** [17,32]. Drift generation (p4): "Qwen3.6-Plus proposes 6–8 drift scenarios per skill, yielding 422 candidate pairs; validated candidates form a controlled evaluation split with 174 drift pairs." | p4 (drift generation), p7 (Table 2) | Five backbones confirmed; recall range 24–76% exact. Qwen3.6-Plus is confirmed as both the drift-scenario generator (p4) *and* the top recall scorer (76%, p7) — precision is 100% for all five backbones, so this variability is recall-only | **Correct**, and the "best also generated the drifts" observation is a real, verifiable methodological fact (same model on both sides of the controlled-split evaluation) — though note the paper itself does **not** flag this as a limitation/confound anywhere in its own Limitations section (App. C, p12-13); this is an inference SCHEMA.md draws across two separate sections, not something the authors self-critique. |
| SCHEMA.md A5: "role-bearing checks gave no false alarms over 599 cases, against 40% for contract-free probes (p7)" | p7: "over 599 no-drift and hard-negative cases... SKILLGUARD raises no false positives (Wilson 95% CI [0%, 0.6%])"; "CI probes without contracts... incur 40% FPR" (also Table 11, App. K, p17: CI probes without contracts = 60% precision / 30% recall / **40% FPR**) | p7 (and Table 10 p17, Table 11 p17 for detail) | 599 = 49 identity + 300 formatting hard-negatives + 250 semantic hard-negatives; single run per method | **Correct**, exact numbers match. |
| SCHEMA.md A5: "aimed repair was not significantly better than plain drift text (p19). Single runs" | Table 14 (p19): SKILLGUARD failed-contract repair = 25/32 = 78% (1 round); Plain drift text = 12/20 = 60% (1 round), **p = 0.213** vs. SKILLGUARD (Fisher exact, not significant); Self-refine = 16/20 = 80% (3 rounds), p = 1.000; Rewrite w/ full drift spec = 25/32 = 78% (3 rounds), p = 1.000 | p19 (Table 14) | Note unequal sample sizes across arms: n=20 for "no localization"/"plain drift text"/"Self-refine" vs. n=32 for SKILLGUARD/"rewrite with full spec" — a real cross-arm comparability caveat not flagged by our documents; single run, no seeds | **Correct.** p=0.213 (not significant) directly supports "not significantly better," and this is on p19 as cited. The paper itself states this plainly: "SKILLGUARD does not significantly outperform Self-refine or plain drift text in the current repair sample" (p8-9). |
| companion.md (same paragraph, unpaged): "checking only role-bearing assumptions gave no false alarms over 599 cases, against 40% for contract-free probes. Recall ranged from 24% to 76% across five backbones, and the best also generated the drifts. Aimed repair was not significantly better than giving the plain drift text. All single runs." | Same as rows above | p7, p4, p19 | — | **Correct** (restates the SCHEMA.md claims verified above, no page numbers given but all verified accurate). |

## Other quantitative findings (not currently cited, potentially useful)
- **Standalone role-label audit (Table 8, p15):** SKILLGUARD's OPERATIONAL/INCIDENTAL role decision alone (independent of end-to-end drift detection), against 200 human-adjudicated mentions: 89.5% precision, 83.4% recall, 86.3% F1 overall; on semantic hard negatives specifically, 100.0% role precision but only 72.7% role recall (p9).
- **Extraction sensitivity (Table 12, p18):** expanding the deterministic regex extractor from 7 to 15 pattern families raises real-world regex-only recall from 45% to 78% (controlled-split: 13%→33%) while FPR stays 0%; mean contracts per skill rises 3.4→11.7.
- **Live open-world discovery (p7-8, Table 13 p17):** 49 real skills, 22 with confirmed drift, 27 fresh; SKILLGUARD flags 14 → 12 TP, 2 FP (pre-adjudication), 10 FN, 25 TN → 86% conservative precision, 55% recall, 7% FPR. Authors note the "2 FP" were later judged genuine drift on adjudication but kept the conservative pre-adjudication numbers as primary (p8, p18).
- **Literal vs. type-aware repair verifier (Table 16, p20):** literal verifier passes 165/174 = 95%, type-aware passes 168/174 = 97% (a 2pp conservative-rejection gap, concentrated in dependency updates: 82%→100%, +18pp).
- **Per-drift-type breakdown, Qwen3.6-Plus (Table 17, p20):** URL change and version bump detected at 100%; configuration/deprecation/schema changes 60–67%; authentication change hardest — 67% detection but 0% repair success (n=3, small).

## Other findings relevant to the four themes
- **(a) Declare-and-check before use vs. observe after use:** This is the paper's central axis. Related Work (p3): automated program repair / Self-refine / Reflexion "are reactive: they require a failed execution, test, or trajectory before repair is attempted. SKILLGUARD instead targets **proactive maintenance**. It detects violated environment contracts **before relying on an execution failure**." Also the "ordering constraint" in §4 (p4): "decide whether an environmental value is role-bearing **before** probing whether it changed" — and Algorithm 1's "Design rationale" (p13): "The critical ordering... is that role filtering precedes validation." Directly on-theme, strong citation candidate beyond what's already used.
- **(b) Token/context cost:** Table 15 (p19): SKILLGUARD repair ≈10K tokens/skill (1 round, 78% success) vs. Self-refine ≈18K tokens/skill (3 rounds, 80% success) vs. rewrite-with-full-spec ≈12K tokens (3 rounds, 78% success) — a token-efficiency number for *repair*, not for tool/skill exposure per se.
- **(c) Precondition/contract parity between a filter and the executed thing:** Table 16 (p20) — literal-verifier pass rate (95%) vs. type-aware pass rate (97%) is itself a parity-of-checking-mechanism result: "the literal verifier accepts value-substitution repairs only when the required new value appears and the stale value disappears... it is not a semantic correctness proof; it can reject valid edits that satisfy the updated contract without preserving the exact literal form" (p9, §6.3). This is a clean example of a *declared check* (literal match) not having full parity with *actual* (semantic) correctness — relevant if this theme wants a concrete instance of filter/executed-thing mismatch.
- **(d) Library growth/retirement:** Not really addressed — the paper is about maintaining the validity of individual already-admitted skills over time (drift detection + localized repair), not about growing, capping, or retiring a library based on aggregate quality. Loosely relevant only as background motivation ("LLM agents increasingly rely on reusable skill libraries," Abstract, p1).

## What the paper does NOT support (Appendix C Limitations, p12-13, authors' own words)
- "SKILLGUARD is a precision-first monitor for environment-contract violations, **not a complete verifier of skill correctness**." Guarantees hold only "within the coverage of extracted contracts and available validators."
- "Assumptions that are implicit, behavioral, or observable only through execution can be missed."
- Role-label audit shows the OPERATIONAL/INCIDENTAL split is "reliable but imperfect; missed operational roles remain one source of false negatives."
- "Live validators... provide useful discovery signals, but they **do not replace execution-based canaries** when exhaustive coverage is required."
- Repair "does not by itself solve mechanism-level rewrites such as authentication flows, coupled schema changes, or behavioral API migrations."
- The strict repair verifier "is also an acceptance criterion for value substitutions, not a semantic correctness proof; it can reject valid edits."
- "Our open-world study covers 49 real skills. Larger continuous deployments are needed to measure long-term alert fatigue, human acceptance of suggested repairs, and how contract monitors should be combined with execution-backed checks."
- Explicitly *not* claiming SKILLGUARD dominates repair baselines (§5.3, p9): "SKILLGUARD does not significantly outperform Self-refine or plain drift text in the current repair sample."

## Figure/table candidates for an appendix
| Page | Fig/Table | Shows | Raster/vector |
|---|---|---|---|
| p2 | Figure 1 | Raw-value monitoring vs. role-aware (SKILLGUARD) distinction, illustrative | Vector (diagram) |
| p5 | Figure 2 | SKILLGUARD contract lifecycle: extract mentions → role filter → validate → localize repair | Vector (block diagram) |
| p7 | Figure 3 | Monitoring-method scatter: precision/recall/FPR of SKILLGUARD vs. Grep/diff, Dependabot, NL2Contract, CI-probes, canary | Vector (data plot) |
| p7 | Table 2 | Known-drift verification across 5 backbones (precision/recall/CI) | Vector (text table) |
| p8 | Figure 4 | (A) open-world discovery outcome; (B) one-round repair success bar chart across methods | Vector (data plot) |
| p17 | Table 11 | Detection-baseline comparison table (7 methods incl. canary oracle) | Vector (text table) |
| p19 | Table 14 | Repair guidance ablation with Fisher-exact p-values | Vector (text table) |

---

## More Skills, Worse Agents? Skill Shadowing Degrades Performance When Expanding Skill Libraries (arXiv 2605.24050)

**Read confirmation:** I read the whole .txt with Read in two chunks: lines 1–560 and 561–1111. `wc -l` gives 1111 lines. The last line reached is 1111, "===== page 18 =====" followed by a blank page 18. The last page with content is p17: the end of Appendix B.4 / Table 10. That covers the main text (pp1–10), references (pp10–11) and appendix A–B (pp12–17). Version: arXiv:2605.24050v2 [cs.SE], 23 Jun 2026, Databricks.

**Summary:** The paper measures how agents do as the skill library grows. It compares a library holding only the "known-helpful" oracle skills (S=S⋆) with libraries of 52, 102 and 202 skills. The benchmark is SkillsBench (88 tasks). A (task, model) pair is kept only if every skill in its authored bundle gives at least a 4% pass-rate uplift on its own (τ=0.04). That leaves "38 (task, model) pairs": 21 for Haiku 4.5 and 17 for Sonnet 4.6, both Anthropic ("two models from a single provider", p10). The dataset is "2,545 trajectories" (p8). By model, that is 303/297/544/273 for Haiku and 233/233/441/221 for Sonnet (p12). The paper gives no seeds or run counts per task, only trajectory counts. CIs come from a two-stage clustered bootstrap: 2,000 trials, "random seed is 42" (p14). The 202-skill library is the union of all 88 authored bundles after de-duplication (p13). The paper splits the drop Δ exactly into skill shadowing (Δshd: shifts in which skills get invoked) and context overhead (Δctx: execution gets worse even when selection is right), and gives upper bounds on each. It finds shadowing is the only significant component.

**Ledger table:**

| Claim/number as used in our docs | Exact figure in paper | Page | Setup/caveat | VERDICT |
|---|---|---|---|---|
| SCHEMA.md:58 — "at selection the agent sees only name and description (2605.24050 **M** p4)" | Def. 1: "The pair (ni, di) is the skill's interface—the only information visible to the agent at selection time. The body bi is withheld until the skill is invoked." Also Phase 1, p5: "The agent receives q and D(S). Skill bodies are withheld." | p4 (and p5) | This is a definition in the paper's formal model, not a measured result. It covers context-injection skills (the SKILL.md style). "so selection reads admitted text" is our own design inference. | **correct** (definitional; label it that way if it is used as evidence) |
| companion.md:109 — "the model that selects sees only name and description (More Skills, Worse Agents, **M**)" | Same as above | p4 | Same caveat. The row lists only `description`, while the paper's interface is name + description. | **correct** |
| companion.md:56 — "pass rate falls from 0.49 to 0.28 as the library grows to 202 skills" | Neither absolute number appears anywhere in the text. The paper gives only the drop: Table 1, \|S\|=202, Δ = ".21 [.15, .27]", averaged across both models. Abstract: "by up to 21%". Intro: "pass rate drops by 21%, averaged across both models". Figure 1 (p3) plots the "Pass-rate drop", not absolute rates. I rebuilt it from Tables 7 and 10: per-model averages come to about 0.49 (S⋆) and about 0.29 (202). Weighting by trajectory instead gives about 0.47 → 0.27. | p1, p2, p9 (Table 1), p3 (Fig. 1) | 0.49 − 0.28 = 0.21 matches Δ. The absolute endpoints are unverifiable from the paper and can only be derived roughly. Note the paper's "21%" is really 0.21 absolute (21 points); relative to 0.49 it is about a 43% fall. | **wrong / unsupported as stated**. Should say: "pass rate drops by 0.21 (95% CI .15–.27) from oracle skills alone to a 202-skill library, averaged over both models (Table 1, p9)". If 0.49/0.28 stay, mark them "derived from Tables 7 and 10". |
| companion.md:56 — "38.5% of trajectories then invoke no skill at all, against 12.0% with the right skills alone" | Table 2, "no skill invoked": S=S⋆ "12.0%" (n=552); \|S\|=202 "38.5%" (n=494) | p9 (repeated in Table 10, p17) | Pooled over both models. Almost all of it is Haiku: 19.1% → 65.9%. Sonnet stays small: 2.5% → 4.5% (Table 10, p17). | **correct** (pooled; should note that Haiku drives it) |
| SCHEMA.md:209-210 — "at 202 skills 38.5% of trajectories invoked no skill, against 12.0% with oracle skills alone (2605.24050 **M** Table 2, p9; Haiku 4.5 and Sonnet 4.6)" | Same Table 2 numbers | p9 | Same pooling caveat. The paper does back abandonment as a failure mode: "abandonment (mass into event n) and wrong selection (mass into event m)" (p9). Using it to justify `offered[]` and a "none" choice is our design step. | **correct** |
| companion.md:56 — "Haiku 4.5 mostly stopped using skills" | Table 10, Haiku \|S\|=202: "no skill invoked" 65.9% (vs 19.1% at S⋆), oracle-only 29.3%. Text: "Haiku's failure mode under expansion is therefore abandonment: rather than picking the wrong skill, the agent picks no skill." | p17 | This is at 202 skills. At 52 skills Haiku is only at 23.2%. | **correct** (say "at 202 skills") |
| companion.md:56 — "Sonnet 4.6 mostly picked wrong ones" | Table 10, Sonnet \|S\|=202: oracle-only "81.4%", mixed–oracle invoked 3.6%, mixed–oracle not invoked 10.4% (14.0% wrong-involved in total), no skill 4.5%. Table 9: Sonnet πm = ".14 [.10, .19]". Text: "Sonnet's failure mode is wrong selection: the agent keeps invoking skills, but increasingly the wrong ones." Table 5: Sonnet Δshd at 202 = ".04 [−.04, .15]", not significant, and "for Sonnet, ∆ctx matches or exceeds ∆shd at every size" (p14). | p16–17, p14 | Most Sonnet trajectories (81.4%) still invoked only the right skills. Only the lost share went mostly to wrong picks. Sonnet's shadowing effect on pass rate is not statistically distinguishable from zero. | **overstated**. Should say: "Haiku's losses went mostly to picking no skill (65.9% of trajectories at 202); Sonnet's went mostly to wrong picks (14% at 202, from 0%), though 81% of Sonnet trajectories still picked only the right skills." |

The search for "2605.24050", "More Skills", "Worse Agents" and "shadow" found no other citations of this paper in either doc.

**Other findings relevant to these themes (with page numbers):**

(a) **Declaring behaviour and checking it before use, vs observing after use (safety):** Safety is not discussed. What comes closest:
- p2, citing Xu & Yan: "a wrong skill injects plausible but incorrect reasoning into the agent's context where it is treated as authoritative". A wrong tool call, by contrast, "is more likely to produce a detectable error (type mismatch, missing parameter, API error code) due to its structured schema". This argues that skills fail silently where typed interfaces fail loudly.
- Method (p4–5): the paper judges the trajectory only after the fact, "we treat the trajectory as a black box from which only the invocation set I and the final output are recorded".
- p6: which skills count as oracle is decided empirically after running them: "each skill is tested in isolation against q".

(b) **Token/context cost of exposing many tools/skills:**
- Context overhead is tested directly but no token counts are reported. Δctx is ".06 [−.11, .22]" at 52, ".06 [−.11, .23]" at 102 and ".07 [−.13, .25]" at 202 (Table 1, p9), and is never significant.
- Upper bound Δsup_ctx, pooled: .08/.07/.07, "no CI separates from zero" (Table 6, p14–15).
- Binary pass rate for oracle-only trajectories falls .52 → .45 (Table 7, p15). The fractional rate falls .87 → .80 (p16): "Context overhead removes whole-task correctness more than partial progress."
- Authors call the context overhead estimates "suggestive only" and say it is "real but our sample size is too small to confirm it" (p9).
- Background claim, cited not measured: tool-selection accuracy falls "from above 90% with fewer than 30 candidates to 13.6% with 11,100" [Gan & Sun, RAG-MCP] (p2).
- Background, cited: SkillReducer's "less-is-more" compression effect (p2).

(c) **Precondition or contract checking; parity between a filter and the executed thing:** Not discussed.
- Closest point, p4: when adapting Jiang et al.'s skill tuple, the paper drops the "applicability condition, policy, and termination condition" because they "reduce to properties of the agent rather than the skill". Its skill model therefore has no preconditions.
- Retrieval-based pre-filtering is named as future mitigation only (p10). Filter/execution parity is not examined.

(d) **Library growth/retirement:**
- Growth is the paper's core subject: monotonic drop, Δ = .08/.14/.21 at 52/102/202 (Table 1, p9).
- Pooled oracle-only share falls 88.0% → 80.3% → 64.4% → 52.6% (Table 2, p9).
- Shadowing examples (Table 3, p13): video-frame-extraction shadowed mario-coin-counting in 51 first-pick trajectories at 202, and the intro reports it was invoked "in ALL 26 trajectories" (p3). Other pairs include senior-data-scientist (37) and reflow_machine_maintenance_guidance (14).
- Distractors "are not adversarially constructed" (p6).
- Mitigations proposed, not tested: "retrieval-based pre-filtering…, description disambiguation…, learned routing" (p10).
- Retirement or removal of skills is not discussed.

**What the paper does NOT support:**
- Authors' stated limits:
  - "our study covers 202 skills on two models from a single provider"; larger libraries or other architectures are "an open question" (p10).
  - Context overhead is not significant and "our sample size is too small to confirm it" (p9).
  - For Sonnet, neither Δctx nor Δshd is significant: "we do not have necessary statistical power" (p14). Sonnet's total Δ is significant only at 202 (Table 4: ".15 [.06, .24]", p14).
  - Mixed and no-skill buckets "are sample-limited" (p16).
- Other limits of the study itself:
  - It uses only tasks where every oracle skill helps by at least 0.04, so it is selected for skill-sensitive tasks (p12).
  - The skills are human-authored SkillsBench bundles, not self-built or generated.
  - The "21%" is an absolute 0.21 drop, not a relative one.
  - There are no seeds or independent runs per condition beyond trajectory counts, and no token or latency measurements.
- Overreach in our docs:
  1. "0.49 to 0.28" does not appear in the paper; only Δ=.21 does.
  2. "Sonnet mostly picked wrong ones" is overstated, as the table shows.
  3. Placement: companion.md:50 frames the evidence table as "**Self-built libraries** can help, but a capability that runs without complaint is not thereby correct." This paper's libraries are task-author-curated bundles (p12). It gives no evidence about self-built libraries, and none about capabilities "running without complaint". Its point is selection failure as a library grows. The row fits under library growth/selection, not self-building.
  4. The p4 "sees only name and description" claim is a modelling definition, not an experimental finding.

**Figure candidates for appendix:**
- **Figure 1, p3:** "Pass-rate drop when expanding from oracle skills to larger libraries, averaged across 38 (task, model) pairs, with 95% percentile-bootstrap CI." It shows the monotonic drop against library size. My guess is raster or an embedded image, because the text extraction picked up none of its axis labels or tick values. Verify against the PDF. It is the only figure in the paper.
- **Table 1, p9:** Δctx / Δshd / Δ decomposition with CIs. Text table (vector). This is the best single source for the 0.21 drop and for shadowing dominating.
- **Table 2, p9** (same as the pooled part of Table 10, p17): invocation-pattern shares. Vector. Source for 38.5% vs 12.0%.
- **Table 10, p17:** per-model invocation shares. Vector. Source for Haiku abandoning skills and Sonnet picking wrong ones.
- **Table 3, p13:** frequent shadowing pairs. Vector. Useful as a concrete example.
- **Table 5 and Table 6, p14:** per-model decomposition and upper bounds. Vector. Supporting only.

---

# 2606.03056 — SkillDAG: Self-Evolving Typed Skill Graphs for LLM Skill Selection at Scale

**Read in full:** yes, all 19 pages (line 1 to EOF at line 975; includes Appendices A–H). Note: this is a two-column-PDF text extraction with floated tables, so a few exact page-footer/paragraph associations are approximate (float placement shifts content between adjacent page boundaries); paper-level page numbers below are footer numbers actually printed in the extracted text (confirmed via `grep` for isolated page-number lines).

## Summary
SkillDAG models the relationships between skills in a large skill library as a typed directed graph with five edge types (`depends_on`, `specializes`, `composes_with`, `similar_to`, `conflicts_with`) and exposes it to the LLM agent at inference time as a callable interface (`search`/`show`/`propose-edge`/`edit-edge`), rather than baking it into a fixed offline retrieval pipeline (the closest baseline, "Graph of Skills"/GoS). The graph is cold-started from a two-view embedding of `SKILL.md` text (what a skill does / what it needs) plus an LLM pair classifier, and then evolves online: the agent proposes and commits evidence-backed edge edits during execution, gated by three structural invariants (acyclicity on the `depends_on`/`specializes` backbone, non-contradiction between a conflict edge and a positive edge on the same pair, and append-only reversibility). Evaluated on ALFWorld (140-episode `valid_seen` split, 37-skill library) and SkillsBench (87 containerized code-gen tasks, tested at four skill-pool scales: 200/500/1000/2000 `SKILL.md` docs), with two backbones: MiniMax-M2.7 and gpt-5.2-codex. Baseline numbers (Vanilla/Vector/GoS) are *quoted from* the prior GoS paper (Liu et al. 2026), not rerun locally by these authors — the paper explicitly flags this is not a "paired seed-matched rerun." SkillDAG's own numbers are the authors' own single runs (no seeds/repeats reported).

## Ledger table

| Our claim | Paper's exact figure | Page (footer) | Setup/caveat | Verdict |
|---|---|---|---|---|
| SCHEMA.md A1 "Not in the manifest": "...inferred conflicts between capsules (2606.03056 **A** p5)" | Fig. 3 caption: "`conflicts_with` is reserved for the online protocol because co-use harm cannot be inferred from static text alone." §3.4: "We reserve `conflicts_with` for the online protocol (§3.5) by operational necessity: a conflict is, by definition, a pair whose co-use predictably degrades success, and that evidence simply does not exist until execution is observed. **No amount of static reading recovers it.**" | ~p5 | This is the core design reason SkillDAG treats `conflicts_with` differently from its other four edge types | **Correct** as a citation for "conflicts between capsules exist / are tracked," but see next row for the mechanism. |
| SCHEMA.md "Rejected" section: "Inferred conflicts between capsules: found only after execution (2606.03056 **A** p5, p9)" | Same passage as above (~p5), reinforced by App. C's operational definition (~p17): "`conflicts_with(A,B)`. Co-selecting skills A and B causes a **measurable drop in success rate** compared to selecting either alone... genuine interference: resource contention, contradictory instructions, state contamination, or protocol conflicts." | ~p5 (and App. C, ~p17, for the operational/measured definition) | The p9 pinpoint is imprecise (page 9 in this extraction covers §4.2/4.3 main-results text, not the conflicts discussion), but the *substance* — conflicts are execution-observed, not statically inferred — is stated repeatedly and unambiguously (§3.2, §3.4, Fig. 3 caption, App. C, App. F: "`conflicts_with` is not traversed" and is one-hop-only, execution-sourced) | **Correct in substance** ("found only after execution" is exactly the paper's own claim); **page pin at p9 is not well supported** by this extraction — the clearest statements are on ~p5–6 and in Appendix C (~p17), not p9. |
| companion.md: "...conflicts between capsules inferred **from text** (SkillDAG, **A**)" | Directly contradicted: "co-use harm **cannot be inferred from static text alone**... No amount of static reading recovers it" (§3.4); `conflicts_with` is explicitly excluded from the cold-start (text-based) construction (Algorithm 1, App. A: "conflicts_with reserved for the online phase") and is populated only through the online execution-driven propose/commit loop (§3.5, Algorithm 2) | ~p5 (Fig. 3 caption), ~p15-16 (Algorithm 1, App. A) | — | **WRONG.** This is the opposite of what the paper says. SkillDAG's four *other* edge types (`depends_on`, `specializes`, `composes_with`, `similar_to`) *are* inferred from text at cold-start (§3.4); `conflicts_with` specifically is the one relation the paper says text **cannot** supply — it is populated only from observed execution. SCHEMA.md's own citation of the same paper ("found only after execution," row above) gets this right; companion.md's characterization directly contradicts both the paper and SCHEMA.md's own correct reading of it. |

## Other quantitative findings (not currently cited, potentially useful)
- **Main results, Table 1 (~p6-7):** MiniMax-M2.7: SkillDAG reaches 67.1% ALFWorld success (vs. GoS 54.3%, +12.8) and 27.3% SkillsBench reward (vs. GoS 18.7%, +8.6); intrinsic SkillsBench Ret@K rises 65.5→78.2 (GoS→SkillDAG), Ret@1 50.6→66.7, MRR 57.3→71.3. Under gpt-5.2-codex the gap narrows sharply: ALFWorld ties at 93.6%, SkillsBench 34.4→36.8 (+2.4 only) — "the routing aid signature is large where the backbone cannot reason past a poor bundle and vanishes once it can" (~p8).
- **Scale robustness, Figure 4b (~p7-8):** with the embedding backbone held fixed, SkillDAG's plain matches-cosine outranks GoS's PPR-diffusion pipeline at every one of four skill-pool scales (200/500/1000/2000), by +16.1/+17.2/+17.2 Ret@5/Ret@1/MRR at 200 skills narrowing to +13.8/+16.1/+16.3 at 2000; across the full 10× pool expansion SkillDAG itself loses only 3.5 Ret@5 points (78.2→74.7).
- **Online-edit set-monotonicity, Table 2 (~p8-9):** replaying 316 search queries, cold-start graph (2,359 edges) retrieves mean 1.915 ground-truth skills/query; edited graph (2,386 edges, +27 online commits) retrieves 1.984/query, and "zero queries lose any ground-truth retrieval" — a recall-only claim, "not a context-budget claim" (paper's own caveat).
- **Edit persistence, Figure 4a (~p7-8):** 420-episode train run vs. 140-episode held-out test-initial (cold-start graph) vs. test-edited (train-produced graph): both backbones stay within 2.1 points across train/test-initial/test-edited, supporting "committed edges persist as durable structure rather than training-time stochastics."
- **Failure analysis (App. B, ~p16):** of 11 failures in a 30-task ALFWorld pilot, 8/11 are "tight loops" (grounding failures, not skill-selection failures), 1/11 a model-specific reasoning-token leakage artifact, 2/11 step-budget exhaustion — small n, diagnostic only.

## Other findings relevant to the four themes
- **(a) Declare-and-check before use vs. observe after use:** The three commit-time invariants — acyclicity (depends_on/specializes backbone), non-contradiction (no `conflicts_with` on a pair that already carries a positive edge), and append-only reversibility (§3.5, Algorithm 2) — are exactly a declared-and-checked-before-commit mechanism, though for *graph structure*, not for tool preconditions/postconditions per se. "These invariants are structural rather than semantic by design: they preserve the LLM's authority over what each edge means while preventing the graph from drifting into incoherence" (§3.5). Also: commits are "gated only by the agent's own reasoning, not by a downstream voting threshold or a human curator" — i.e., no independent check beyond the agent's own judgment, a real gap for a "declare-then-check" framing if extended to this theme (§3.5, Limitations, ~p10: "raises the risk of single-shot corruption, which we bound with three structural invariants").
- **(b) Token/context cost of exposing many tools/skills:** Directly discussed as motivation (§1, ~p1): "Concatenating the whole library is feasible only at small scale: token cost grows linearly and descriptions are lost in an overloaded prompt." "Vanilla Skills" (whole-library-in-prompt) is explicitly used as "the recall upper bound and **context-cost reference**" (§4.1, ~p6). Conclusion (~p9): SkillDAG "avoid[s] the context-bloat failure where fixed-bundle retrievers flood the prompt with marginally relevant skills and corrupt downstream reasoning" — qualitative, no token-count numbers given (unlike Contract2Tool's explicit token counts).
- **(c) Precondition/contract checking, parity between declared and executed:** The `depends_on`/`composes_with`/`similar_to`/`conflicts_with` operational definitions in App. C (~p17) are each defined by a **measured counterfactual test** on success rate (e.g. "removing skill B... drops the success rate of A by a measurable margin"), i.e., the graph's typed edges are explicitly grounded in observed execution outcomes, not asserted a priori — a strong instance of "declared relation validated against what actually happens," relevant if this theme wants a concrete example.
- **(d) Library growth/retirement:** The paper studies **growth** extensively (10× skill-pool scale test, 200→2000, Fig. 4b) but has **no retirement mechanism** — skills are never removed from the graph; only edges can be added, retyped, or deleted via `edit-edge`, under an append-only history log for rollback "by recency" (§3.5). There is no cap, no eviction, no quality-based pruning of skills themselves.

## What the paper does NOT support (authors' own limitations, ~p10, and caveats stated in-line)
- **Limitations section verbatim:** "The propose-then-commit protocol is intentionally agent-driven: a single execution observation can suffice for the agent to commit an edge, bounded by structural guardrails... rather than a statistical confidence threshold... the long-horizon behaviour of single-observation self-evolution remains an open question we view as a direction for future work."
- **Baseline comparability caveat (§4.1, ~p6):** "The Vanilla/Vector/GoS R rows... are quoted from Liu et al. [2026] Table 1 and were not rerun locally; the SkillDAG R rows are our own runs on the same benchmark, backbone, task data, and skill pools, but are **not paired seed-matched reruns** of the baselines." This means the headline +12.8/+8.6-point gains are not a fully controlled head-to-head experiment.
- Scale robustness result (Fig. 4b) "isolates the offline retrieval pipeline, not the typed-edge neighbors/conflicts fields the agent exercises during execution" (~p8) — i.e., the 10× scaling claim covers only the `matches` cosine-ranking component, not the full agent-facing interface.
- The online set-monotone recall gain (Table 2) is explicitly "a recall property, not a context-budget claim" (~p8).
- No statistical significance testing (no CIs, no seeds, no p-values) reported anywhere for the main task-reward results, unlike DRIFTBENCH's bootstrap/Fisher-exact protocol in the Skill Drift paper.

## Figure/table candidates for an appendix
| Page | Fig/Table | Shows | Raster/vector |
|---|---|---|---|
| p1 | Figure 1 | Per-episode workflow: search/show/propose-edge/edit-edge loop with commit-time checks | Vector (diagram) |
| ~p3-4 | Figure 2 | Six-node worked subgraph exercising all five edge types | Vector (graph diagram) |
| ~p4-5 | Figure 3 | Cold-start construction pipeline: two-view embedding → threshold → LLM pair classifier → graph | Vector (block diagram) |
| ~p6-7 | Table 1 | Main results: reward + intrinsic retrieval, two benchmarks × two backbones × four methods | Vector (text table) |
| ~p7-8 | Figure 4 | (a) ALFWorld train/test-initial/test-edited bars; (b) cross-scale (200–2000) retrieval line plots, SkillDAG vs. GoS | Vector (data plots) |
| ~p8-9 | Table 2 | SkillsBench scale-1000 retrieval: cold-start vs. edited graph, mean ground-truth/query | Vector (text table) |

---

# 2606.07904 — Contract2Tool: Learning Preconditions and Effects for Reliable Tool-Augmented LLM Agents

**Read in full:** yes, all 10 pages (line 1 to EOF at line 630; paper has no appendix beyond p10 references/acknowledgment/artifact-availability sections).

## Summary
Contract2Tool infers lightweight tool contracts (preconditions `R`, effects `E`, risk `ρ`, optional cost `k`) automatically from observable tool evidence (name, description, schema, documentation, and/or execution traces), to feed a downstream "causal minimal tool filtering" (CMTF) system that exposes only causally-appropriate tools at each agent step. Built on a controlled synthetic benchmark: a 100-tool registry (calendar/email/files/document domains plus distractors) and 102 multi-step downstream agent tasks. Contract generators are Bedrock-hosted LLMs (Amazon Nova, Anthropic Claude, Meta Llama); the main downstream run uses Claude Opus 4.8 with hybrid documentation+trace evidence. Evaluation is intrinsic (precision/recall/F1 vs gold contract fields), filter-oracle (283 gold decision steps), and downstream (102 tasks, aggregated over four "reliable" tool-calling models — Nova 2 Lite, Nova 2 Pro, Claude 3.5 Haiku, Claude Sonnet 4.6; Llama 3.3 70B reported separately due to tool-call compatibility failures). No seeds/runs are reported (deterministic synthetic benchmark, single pass per condition).

## Ledger table

| Our claim | Paper's exact figure | Page | Setup/caveat | Verdict |
|---|---|---|---|---|
| SCHEMA.md A1 (`observed` field): "Effects inferred from documentation were the least reliable part of a contract (2606.07904 **A** p7-8)" | Table III: Documentation row — Req. F1 = **1.00**, Prod. F1 = **0.77** (lowest Prod. F1 of Name/Metadata/Schema/Documentation rows: 0.86/0.86/0.80/0.77); p8 explains "documentation- and schema-derived contracts exposed the gold next tool in **84.1%** of steps, while trace and hybrid contracts recovered the gold causal frontier exactly [100%]" | p7 (Table III), p8 (§VIII.B "Why Trace Evidence Matters") | Single synthetic 100-tool registry, no seeds reported; "Documentation" condition's own Effects/Produces F1 (0.77) is markedly lower than its own Preconditions F1 (1.00), and lower than Effects F1 from Name/Metadata/Schema conditions too | **Correct.** Both the intrinsic F1 gap (Req 1.00 vs Prod 0.77 for Documentation) and the qualitative explanation (84.1% vs 100% gold-tool exposure) directly support "effects from documentation are the least reliable part." |
| SCHEMA.md B3: "...seeded from Symphony's vocabulary, which is derived from the inventory..., so a manifest's types do not change when the inventory does (2606.07904 **A** p4, p9)" | p4 (§IV.C): "This layer assumes a **predefined canonical state-variable vocabulary** for the benchmark or deployment environment. Normalization maps generated fields into this vocabulary." p9 (§IX Limitations): "The experiments also assume a fixed canonical vocabulary of task-state variables. In practice, defining this vocabulary is itself a design challenge... gold contracts should be understood as benchmark-specific operational labels rather than universal semantic truths." | p4, p9 | The paper never tests or claims robustness of the vocabulary under an actually-changing tool inventory — it simply *assumes* a fixed vocabulary exists, and flags defining it as an open design problem | **Correct as design precedent, not as an empirical finding.** The paper supports "a canonical vocabulary layer separate from per-tool contracts exists and is normalized onto" (p4), and separately flags that fixing this vocabulary is nontrivial (p9) — it does not show or claim that types stay stable when the inventory changes; SCHEMA.md is right to treat this as `design` motivation only, and the citation doesn't overclaim since it's phrased as the schema's own design choice, only informed by the paper. |
| companion.md table row: "Skill Drift Is Contract Violation (**M**), Contract2Tool (**A**) \| contracts inferred from documents \| the author declares them, and admission tests them" | Contract2Tool infers contracts from name/metadata/schema/**documentation**/**execution traces**, and the strongest results use **hybrid documentation+trace** evidence, not documents alone (p6-8) | p1 (Abstract), p6-8 | "documents" is companion.md's shorthand for the broader "documentation, schemas, traces" evidence set | **Correct, with minor imprecision.** "Contracts inferred from documents" understates that the paper's best results (and its main thesis, §VIII.B) come from *execution traces*, not documentation — documentation alone is explicitly shown to be one of the *weaker* evidence sources for effects (see row above). A more precise gloss would be "inferred from documentation and execution traces." |

## Other quantitative findings (not currently cited in our docs, but relevant)
- **Table V (p8), token/tool-exposure cost — directly relevant to theme (b):** All-tools exposure: 100.0 tools visible, 26,172 tokens/task, 0.775 success, 1.461 wrong-tool calls/task. Learned CMTF (Opus 4.8 hybrid): 1.0 tool visible, 2,528 tokens/task, **0.980** success, 0.020 wrong-tool calls/task, 0.000 premature actions. Gold CMTF: 0.990 success, 2,532 tokens. i.e., cutting visible tools 100→1 cut tokens ~10x (26,172→2,528) *and* raised task success (0.775→0.980) — a strong, citable number for the "cost of exposing many tools" theme that neither SCHEMA.md nor companion.md currently use.
- **Filter-oracle, Table IV (p7-8), 283 gold decision steps:** Opus 4.8 Docs/Schema: 0.841 gold-tool exposure, 0.078 no-visible-tool rate, 0.922 avg. tools visible, 0.081 extra tools. Opus 4.8 Traces/Hybrid and Sonnet 4.6 Hybrid: 1.000 gold exposure, 0.000 no-visible, 1.000 tools, 0.000 extra. Llama 3.3 Docs/Schema: 0.604 gold exposure, 0.396 extra tools (worst).
- **Per-model downstream detail (p8):** Learned CMTF exactly matches Gold CMTF for Nova 2 Lite, Nova 2 Pro, Sonnet 4.6; for Claude 3.5 Haiku, learned CMTF success drops 0.96→0.92 and wrong-tool calls rise 0.04→0.08/task versus gold.

## Other findings relevant to the four themes
- **(a) Declare-and-check-before-use vs. observe-after-use:** Central to the paper. §II.E (p2): "Causal filtering reduces some failures **before execution** by controlling the visible action space." §VIII.A (p8): "Schemas describe how to call a tool... Contracts describe **when** the tool should be exposed and what task-state transition it enables." §VIII.E (p9): explicitly cautions that "such systems should remain human-reviewable, especially for high-risk actions... Learned contracts are best viewed as a scalable contract-generation and monitoring layer **rather than an unchecked replacement for safety review**" — a direct statement that declared/learned contracts should not substitute for a human check, relevant to the safety theme.
- **(b) Token/context cost of many tools:** See Table V above (p8) — the single most citable number in this paper for that theme, currently unused by our documents.
- **(c) Precondition/contract parity between filter and executed thing:** The filter-oracle evaluation (§V.D p5-6, Table IV p7-8) is designed exactly to test this: "Intrinsic accuracy does not fully determine whether a learned contract is useful for causal filtering. A contract can have high average F1 while still missing a causal edge required by a task" (p7, §VII.C). This is a strong, directly on-theme passage not currently quoted in our docs.
- **(d) Library growth/retirement:** §VIII.E (p9) "Toward Self-Maintaining Tool Registries": "Large tool ecosystems change over time as APIs are added, deprecated, renamed, or modified... Contract2Tool suggests a path toward self-maintaining tool registries, where metadata, schemas, documentation, and execution traces are used to bootstrap and refresh tool contracts." Qualitative only, no numbers.

## What the paper does NOT support (§IX Limitations, p9, authors' own words)
- Uses a **controlled synthetic tool registry with gold contracts**; "may not capture the full complexity of real API ecosystems" (incomplete docs, inconsistent schemas, changing behavior, auth, rate limits, side effects).
- Assumes a **fixed canonical vocabulary** of task-state variables; defining it "is itself a design challenge"; gold contracts are "benchmark-specific operational labels rather than universal semantic truths."
- Trace evidence comes from **controlled mocked task trajectories only**; real traces "may be sparse, noisy, biased toward common workflows, or missing rare but important tool behaviors."
- Downstream evaluation uses **mocked tool execution**; does not test real API failures, latency variation, authorization errors, nondeterministic outputs, or irreversible side effects; states "high-risk tools... require additional safeguards before learned contracts are used in production systems."
- Downstream comparisons are confounded by **model-specific tool-calling behavior** (formatting/compatibility) — Llama 3.3 70B excluded from the main aggregate for near-zero success "even under gold-contract CMTF," a compatibility issue rather than a contract-quality failure.
- No claim about **cross-domain generalization** beyond calendar/email/files; no seeds/repeated-run variance reported anywhere.

## Figure/table candidates for an appendix
| Page | Fig/Table | Shows | Raster/vector |
|---|---|---|---|
| p3 | Figure 1 | Contract2Tool pipeline: evidence → generator → normalization/validation → learned contract | Vector (block diagram) |
| p5 | Figure 2 | Trace evidence use: successful/failed traces → candidate precondition/effect → learned contract | Vector (block diagram) |
| p5 | Figure 3 | Evaluation tracks: intrinsic vs. filter-oracle/downstream comparison flow | Vector (block diagram) |
| p6 | Table I, II | Benchmark components; experimental setup summary | Vector (text table) |
| p7 | Table III | Intrinsic contract-learning F1 across evidence conditions (Name/Metadata/Schema/Documentation) | Vector (text table) |
| p7–8 | Table IV | Filter-oracle evaluation over 283 gold decision steps | Vector (text table) |
| p8 | Table V | Downstream aggregate performance (tools/tokens/success across 5 methods) — the key 100→1 tools, 26,172→2,528 tokens number | Vector (text table) |

---

# RelAIBuild — arXiv:2606.26924 ("A Deterministic Control Plane for LLM Coding Agents")

## 1. Read confirmation
Title: "A Deterministic Control Plane for LLM Coding Agents," Padmaraj Madatha, June 2026, arXiv:2606.26924v1 [cs.SE].
File: `C:\Users\m50066326\huawei\tundle\ai4research\papers\2606.26924.txt`, 2577 lines, 45 pages (page markers `===== page 1 =====` through `===== page 45 =====`).
Read the entire file start to finish in 400-line chunks (offsets 1, 400, 800, 1200, 1600, 2000, 2400). Last page reached: **page 45** (the reference list, ending with Zahan et al. 2022), i.e. full read confirmed to the literal end of file.

## 2. Summary
Not an agent-behavior/ML-benchmark paper — a systems/governance paper. Proposes Rel(AI)Build, a deterministic (non-LLM) control-plane layer sitting above LLM coding harnesses (Cursor, Claude Code, Copilot, Codex, Windsurf, OpenCode, Kiro). Five mechanisms: (1) supply-chain integrity for agent config files (SHA-256 content addressing, HMAC-stamped lockfile, hash-chained audit log); (2) pre-execution permission tiers + attack-derived command/path blocklist; (3) Jaccard-similarity prompt-drift detection; (4) a phase-gated lifecycle (8 phases, 4 HITL gates, 3-iteration auto-fix cap) with requirement(AC)→file→test traceability; (5) a "define once, compile to 7 IDE targets" transformer. Two empirical activities, neither an agent-behavior eval: (a) §6 conformance testing — injected violations against a 237-agent-definition corpus (10 integrity-tamper / 15 over-privileged-tool / 20 blocklist-string cases, all caught) — tests only that hand-written detectors match inputs built to be detected; (b) §7 a prevalence study of N=10,008 public GitHub repos (9,357 orgs, 6,145 agent-config files) measuring how ungoverned agent configs currently are (does not evaluate Rel(AI)Build itself). Appendix D is an N=1 illustrative "DRIFT vignette" on one real build, explicitly not a comparative evaluation. No LLM task-success benchmarking, no seeds/models-as-subjects.

## 3. Ledger table

| Our claim (doc, location) | Exact figure/claim in paper | Page | Setup/caveat | Verdict |
|---|---|---|---|---|
| companion.md Table 13: "RelAIBuild (**A**) \| a pinned, approved spec, with file scope checked \| also tests behaviour and gates selection" — part 1: "a pinned ... approved spec" | spec.md is "content-hashed at approval"; spec_hash recorded; Phase 0 has mandatory HITL gate, plus for tiers M/L a required spec-reviewer delegation before Phase 0 closes | p18, p20 | §4.5 pseudocode: `if n==0 and tier∈{M,L} and 'spec-reviewer' ∉recorded[0]: fail REVIEW_GATE` | **Correct** |
| companion.md Table 13, part 2: "file scope checked" | trace.json links each AC to implementing files; "the spec-drift check then computes the set of all files changed in the working tree ... and flags any file that does not appear in any AC's registered file list" | p20 | **This is post-hoc detection, not pre-execution enforcement.** Paper repeats this boundary 4+ times: "trace linkage is cooperative and auditable post-hoc, not pre-execution enforced" (abstract, p1); "detectable but not preventable before the edit lands" (p21); "The control plane's response is auditability and detection, not pre-execution file-scope enforcement" (p21); limitation heading "Cooperative trace linkage (determinism boundary)" (p34) | **Overstated / needs caveat.** Not factually false, but "checked" sits next to a table framed around gating-before-use; a reader can wrongly infer this is a precondition-style pre-execution gate like the paper's own permission tiers/blocklists genuinely are. Recommend companion.md append "(post-hoc, not pre-execution — the paper's stated boundary)" |
| companion.md Table 13, part 3: "also tests behaviour" (claimed as what capsule schema does beyond RelAIBuild) | "Does not validate semantic correctness of generated code. The architecture governs the process and configuration layer, not the LLM's outputs. It cannot verify that generated code is logically correct, functionally complete, or free of subtle bugs" | p34 (§8 Limitations) | Explicit, stated limitation | **Correct** — differentiation is supported by the paper's own disclaimer |
| companion.md Table 13, part 4: "also ... gates selection" | RelAIBuild's gates are workflow-lifecycle gates (phase ordering, delegation receipts, security-scan-clean) and install-time integrity/permission gates; no mechanism for choosing among interchangeable capability implementations before a step runs | throughout §4.2, §4.5 | — | **Correct** — fair differentiator, no capsule-like selection concept exists in this paper |

No other numeric/quantitative claims from this paper are currently cited in SCHEMA.md or companion.md (grep found zero SCHEMA.md hits for "2606.26924" or "RelAIBuild"; companion.md cites it exactly once, in Table 13).

## 4. Other findings by theme

**(a) Declaring/checking before use vs. observing after use (safety) — pages 4, 12–14, 17–18, 20–21, 34.** Strong, directly citable material. Permission tiers and the command/path blocklist are explicitly deterministic and fail-closed, enforced **before** LLM invocation: "ensuring a misconfigured agent never reaches the IDE execution context" (p13); "install-time gates... prior to LLM invocation" (p4). By contrast, the paper itself draws the exact declare-before-use vs. observe-after-use line for its traceability mechanism and calls it an "honor-system component inside an otherwise deterministic control plane" (p21) — a clean citable example of a system that mixes true pre-execution gates with a component that only detects after the fact.

**(b) Token/context cost of exposing many tools/skills — not addressed.** Closest adjacent material is §4.4/§4.6 on prefix-cache-friendly ordering ("static content first," p9–10, p21) and Jaccard-based prompt-drift detection (p15–17), which concern prompt *stability* and cache efficiency, not the cost of exposing many tools/skills to a selecting model. Do not cite this paper for theme (b).

**(c) Precondition/contract checking + filter-vs-executed parity — high relevance, pages 38–40 (Appendix B).** A semi-formal (explicitly "not a mechanised proof") "governance-preservation compilation argument": if canonical definition D satisfies property P and passes pre-compile gates, every compiled target T(D) preserves P — but conditioned on assumption A3 "faithful encoding," which the paper admits is **not validated here**: "Validating A3 ... is deferred to the expanded evaluation in §9.2; one-target parser-recovery tests constitute a one-day exercise and are planned" (p39–40). This is a directly useful precedent for our "parity between a filter and the executed thing" theme — including as a cautionary example of a paper that asserts parity only semi-formally and defers real validation.

**(d) Library growth/retirement — not addressed.** No notion of a capability/capsule library with admission or retirement; the "registry" is a static, versioned registry of agent configs with no growth/retirement dynamics discussed. Do not cite for theme (d).

## 5. What the paper does NOT support (stated limitations, §8 p34–35, §7.4 p33–34)
- Does not claim to solve prompt injection ("HITL gates... reduce, but do not eliminate"; residual risk rated Medium for T1).
- HMAC lockfile is local-integrity only, not adversarial-signing-grade: "any process running as the same user can read the key and forge a valid stamp."
- Trace/file-scope linkage is cooperative, not preventable pre-edit (repeated boundary, see theme (a) and ledger row 2).
- Does not validate semantic correctness of generated code at all.
- Does not secure model-provider API infrastructure.
- §6 conformance tests show mechanisms work on constructed/injected inputs, explicitly **not** developer-productivity or field-effectiveness evidence: "they are conformance checks confirming that hand-written detectors match inputs constructed to be detected... They carry no information about field effectiveness or developer outcomes" (p27–28).
- Jaccard 0.60/0.80 thresholds are "operating defaults pending calibration," not empirically validated against behavioral change (p16–17, p35).
- No causal claims from the §7 prevalence study; it does not evaluate Rel(AI)Build deployment outcomes at all, only the governance gap motivating it (p33–34).
- Runtime permission enforcement is harness-dependent; several targets (Codex, Windsurf, OpenCode, Kiro) have "little or no runtime permission enforcement" — a compiled artifact "correctly declares intent" but isn't necessarily enforced by the target harness (p22, p35).
- Appendix D vignette is N=1, governed arm only, explicitly "not a comparative evaluation" (p40–41).

## 6. Figure candidates for appendix
Paper explicitly states (p36): **"The nine paper figures are vector PDFs generated from these sources"** — so every figure below is vector, not raster.

| Page | Figure/Table | What it shows | Format |
|---|---|---|---|
| p3 | Fig. 1 | "Thin-governance gap" conceptual diagram (5 ungoverned risk surfaces around a harness) | Vector |
| p9–10 | Fig. 2 | Control-plane architecture, 4 horizontal layers (Authoring/Distribution, Compilation, Runtime Governance, Substrate) | Vector — good architecture-comparison exhibit |
| p13 | Fig. 3 | Install pipeline sequence diagram (2 sequential abort gates: hash mismatch, credential scan) | Vector |
| p16–17 | Fig. 4 | Jaccard drift risk-zone number line (LOW/MED/HIGH thresholds) | Vector |
| p19–20 | Fig. 5 | 8-phase gated lifecycle state diagram, 4 HITL bars, gate-failure back-edges | Vector — strong candidate for "declare-then-gate lifecycle" exhibit |
| p21 | Fig. 6 | Requirement→file→test (AC) traceability diagram incl. "spec-drift: scope creep" flag | Vector — directly illustrates the post-hoc file-scope check (ledger row 2) |
| p24–25 | Fig. 7 | Threat→control mapping (7 threats → 7 deterministic mitigations) | Vector |
| p31 | Fig. 8 | Bar chart: version-control depth, AI configs vs CI/CD workflows | Vector (per paper's own figure-format statement) |
| p32 | Fig. 9 | Dot/bar chart: age-normalized commits/month by category | Vector |
| p40–41 | Table 13 | N=1 DRIFT-detection vignette (Phase-8, AC-018 trace gap) | Table, not a figure |

## Scope note
This file covers only the RelAIBuild paper (2606.26924) verification against its single companion.md citation (Table 13 row). SCHEMA.md has no citation of this paper (confirmed via grep for "2606.26924" and "RelAIBuild" — zero matches). The other six papers in the broader ledger task are out of scope for this file.

---

## The Blind Curator: How a Biased Judge Silently Disables Skill Retirement in Self-Evolving Agents (arXiv 2607.07436)

**Read confirmation:** I read the whole source file (`wc -l` gives 1273 lines) with Read, in three chunks: lines 1–450, 450–869 and 869–1273. The last line reached is 1273, the footer "17" of **page 17**, which is the true end of the file. I covered all of pp. 1–17: the main text (pp. 1–9), the references (pp. 9–11) and appendices A–H (pp. 11–17). The header on p. 1 reads "arXiv:2607.07436v2 [cs.AI] 18 Aug 2026". The paper was published at the COLM 2026 Workshop on Agent Behavior.

**Summary:** The paper asks what an imperfect reward signal does to Ratchet's skill retirement. In Ratchet, a Critic labels failures, a Synthesizer turns failures into skills, and a Router picks at most one skill per task. A Curator retires a skill once its contribution falls to −τ after at least Nmin trials, and a hard cap limits active skills (p3).

- **Theory:** a binary corruption channel predicts that symmetric noise only "attenuates" retirement, while false-pass bias "displaces" it. Past ρF→P = (1−τ)/2 (0.45 at τ=0.10), "no skill is retired at any sample size" (p4, App. C p13–14).
- **Testbed:** citation-grounded report writing, with 155 section slices from five productions of an internal Chinese-language deep-research engine. The reward is a deterministic grader of 5 QC checks. It is treated as ground truth, and corruption is injected exogenously onto the training labels only (p3, p12).
- **Common setup (Table 2, p12):** 3 seeds (42/43/44) × 12 rounds, τ=0.10, Nmin=24, cap C=12.
- **Subsets:**
  - REPORT-MAIN-71, REPORT-BAND-58 and REPORT-HARD-133 use a Claude Haiku 4.5 composer at temperature 0.7.
  - MBPP+ HARD100 uses Claude Opus 4.7 with unit tests (the code-generation cross-check).
  - REPORT-WEAK-71 uses Claude 3.5 Haiku as a capability control.
- **Judges:** the in-loop judge is the same model as the composer (temperature 0, binary). The gate audit uses a held-out Claude Sonnet 4.6 judge (p12).
- **Defect-injection audit:** 7 defect classes × 155 sections (pp. 4–5).

### Ledger table

| Claim/number as used in our docs | Exact figure in paper | Page | Setup/caveat | VERDICT |
|---|---|---|---|---|
| SCHEMA.md:64 — "Deterministic checks and a judge caught disjoint defects (2607.07436 M Fig. 2)" | Deterministic QC "catches every QC-visible injection (recall 1.0, n=155 per class)" and "essentially none of the QC-invisible ones (claim negation 0.0; number swap 0.05)". The held-out judge flags "number swap 98.5%; claim negation 92.7%". On structural defects "the judge often flags yet its scalar quality score barely moves (p ≈0.5)". The paper's word is "complementary". | p4–5, Fig. 2 | The held-out judge is Sonnet 4.6, not the loop judge. The Fig. 2 bars are flag rates, not scores. There is one domain (citation/numeric discipline). | **Overstated.** The sets are not disjoint: the judge often *flags* structural defects, it just doesn't penalize them, and QC catches 5% of number swaps. It should say "complementary: the checks miss semantic defects and the judge does not reliably penalize contract violations". |
| companion.md:113 — "because checks and judges catch different defects (The Blind Curator, M)" | Same as above; "The two signals are complementary… Their union is the audit." | p5 | Same | **Correct** (the looser wording fits the paper) |
| SCHEMA.md:105–106 — "The Blind Curator shows false-pass bias stopping retirement (p6), not an admission threshold" | "false-pass bias drives true retirement to zero at every rate (0/0.3/0 for q=0.2/0.45/0.7)"; Table 1 True-ret. column | p6 | REPORT-MAIN-71, 3 seeds | **Correct.** Note that the theory for the cliff is on p4 and the stronger replication (≈7→0) is on p7/p13. |
| SCHEMA.md:107–108 — "false-fail near 0.95, 2607.07436 M p5" | "a strict, well-instructed judge has a tiny false-pass rate (ρF→P ≈0.01) but a large false-fail rate (ρP→F ≈0.95)… κ ≈0.04" | p5; sample sizes in App. E p15 | The in-loop judge is the same model as the composer (Haiku 4.5). ρP→F was measured on n=42 truly-passing sections. ρF→P is 0.01 on QC-visible defects (n=210) and 0.014 on QC-invisible ones (n=70). | **Correct** (the n=42 sample is small) |
| SCHEMA.md:107 / companion.md:146 — "A false pass is silent and compounds; a false fail is visible and costs throughput" / "visible as rejections and recurring gaps" | Compounds: "unretired bad skills keep being routed to, generating more corrupted evidence" (p3). False fail "only injects phantom failures, extra fuel the loop tolerates as noise" (p4). Strict judge: "safety bought at the price of starvation" (p5); "a strict judge is safe but starvation-prone" (p2). | p2–5 | "Visible as rejections and recurring gaps" is not in the paper. In the loop, the strict judge actually matched the clean loop (+0.024) and retired 10.3 skills (p6–7). The cost showed up only as fewer synthesized skills (19.0 vs 22.0) and higher churn. | **Correct for "silent/compounds"; overstated for "costs throughput heavily".** The paper predicts starvation (κ≈0.04), but in its one experiment the strict judge showed no outcome harm. "Visible as rejections" is our own design inference and should be marked `design`. |
| SCHEMA.md:117 — "genuine retirement fell to 0 to 0.3 under false-pass bias, against 1.3 clean (one 71-task subset, 3 seeds)" | Table 1 True-ret.: clean "1.3 ± 1.2"; q=0.2 "0.0"; q=0.45 "0.3 ± 0.6"; q=0.7 "0.0" | p6, Table 1 | REPORT-MAIN-71, 3 seeds, 12 rounds. The clean baseline is low ("the composer rarely produces a skill bad enough to retire") with a large sd. Noise also gives 0.7–1.0. | **Correct numbers.** Consider also citing BAND-58 (≈7→0 by q=0.45, Fig. 6b, p7/p13), which is the stronger evidence. |
| SCHEMA.md:117 — "while raw deprecations looked normal because cap eviction filled in (Table 1, p6)" | Table 1 Dep.: clean 9.7; bias q=0.2/0.45/0.7 → 7.7 / 3.7 / 3.0. Text: Dep. "stays near 10 under both noise and the judge and never reaches zero under bias, so it hides a curator that has stopped." | p6 | On MAIN-71, raw deprecations under bias fell 60–70% at q≥0.45. They "stay high under bias" only in the failure-abundant subsets (REPORT-HARD-133, MBPP+; p13, Fig. 4). On BAND-58 the raw count also falls from 9 to 5 to 1 (Fig. 6c, p13). | **Overstated.** It should say "raw deprecations never reached zero (7.7/3.7/3.0 vs 9.7 clean), because cap eviction filled in". "Looked normal" holds only for the abundant-failure subsets (p13, Fig. 4). |
| SCHEMA.md:119 — "retirement fires on contribution below −tau (2607.07436 M p4)" | p4 gives the pass-rate form: retires "once its observed pass rate drops to πτ := (1 −τ)/2". Contribution form: "ĉ(s)… falls to −τ after n(s) ≥ Nmin trials" (p13); "reaches −τ at ≥Nmin trials" (p8). | p4, p8, p13 | Ratchet's rule; τ=0.10, Nmin=24 | **Mostly correct.** It should say "at or below −τ after ≥ Nmin trials". The contribution form is on p8/p13; p4 states the equivalent pass-rate form. |
| SCHEMA.md:138 — "Curator health: zero quality retirements while cap evictions continue signals a lenient judge (p6)" | The p6 text says the raw count "hides a curator that has stopped", and that the clean composer "rarely produces a skill bad enough to retire" (clean 1.3 ± 1.2). The paper presents the audit "as a before-deployment gate rather than as a monitoring metric" (p17). | p6, p17 | Zero true retirement also happens with an honest grader when no skill is bad enough (the clean sd of 1.2 implies some clean seeds near 0). The paper never tests this pattern as a runtime monitor. | **Overstated.** The paper shows lenient bias produces this pattern, not that the pattern diagnoses lenience. It should say the pattern is *consistent with* a lenient judge and should trigger an audit. It is a design heuristic. |
| SCHEMA.md:142–145 — "Defect injection is the method The Blind Curator shows works offline (p4-5, p15)… injection needs mutations that provably change true quality, which failures that do not localise lack (p9, App. H)" | Sec. 5 gate audit (p4–5); App. E reward-judge audit (p15). Limit: "Injection needs mutations that provably change true quality… less localized failures do not" (p9). App. H: "the practical substitute is to mutate the task rather than the output: perturb a precondition…" (p17). | p4–5, p9, p15, p17 | Shown in one domain only (report citations/numerics) | **Correct but incomplete.** App. H is on p17. The paper also offers a workaround for non-localizing failures (precondition/task mutation) that our text omits. "Each postcondition is a natural defect class" is our design, not the paper's. |
| companion.md:144 — "Noise only slows retirement, but a judge biased toward passing stops it without any sign" | Symmetric noise costs "an inflated effective threshold τ/(1−2ρ) and a Nmin∝(1−2ρ)−2 sample budget" (p4). Bias: "the disabled curator is silent, surfacing in no aggregate metric" (p1). | p1, p4 | "Without any sign" means in aggregate eval metrics. The True-ret. column *is* a sign, if it is logged separately. | **Correct** (read as "no aggregate-metric sign") |
| companion.md:146 — "real LLM skill loops with false-pass bias injected at 0.2, 0.45 and 0.7 retired genuinely bad skills 0, 0.3 and 0 times, against 1.3 with a clean grader (one subset, 3 seeds, 12 rounds)" | Table 1: 0.0 / 0.3 ± 0.6 / 0.0 vs clean 1.3 ± 1.2 | p6 | Bias is injected synthetically on a deterministic grader, not produced by an LLM judge. "True-ret." means retirement by the observed contribution rule, separated from cap-eviction (p8), not skills verified to be bad. | **Numbers correct; wording overstated.** Replace "genuinely bad skills" with "retired by the contribution rule (not cap eviction)". Note the bias was injected on a deterministic grader. |
| companion.md:146 — "Meanwhile the raw count of deprecations looked normal, because cap eviction filled in" | Dep. 9.7 clean → 7.7/3.7/3.0 under bias | p6 | Same as the SCHEMA:117 row | **Overstated.** Same fix: "never reached zero". |
| companion.md:146 — "The real judge in the loop was strict, with a false-pass rate near 0.01, at a heavy false-fail cost near 0.95" | "ρF→P ≈0.01… ρP→F ≈0.95" (p5); 0.014 on QC-invisible defects (p15) | p5, p15 | Same-model judge; n=42 for false-fail | **Correct** |
| companion.md:146 — "so strictness is the safer default and its cost is made visible" | "a strict judge is safe but starvation-prone" (p2); "conservative error churns but does not disarm the curator" (p7) | p2, p7 | "Its cost is made visible" is our design | **Correct** for strict being safer; the second half is `design` |
| companion.md:157 — "the paper shows bias stopping retirement, not an admission threshold… The paper's own limit on its audit is that injected defects must provably change true quality, which failures that do not localise lack" | p6; p9; App. H p17 | p6, p9, p17 | Same as the SCHEMA:143 row | **Correct but incomplete.** It omits the App. H precondition-mutation workaround (p17). |
| companion.md:298 — "measuring the verifier… already built in a paper: The Blind Curator (M)" | The defect-injection audit estimates ρF→P and ρP→F (Sec. 5, App. E) and feeds a "go/no-go" playbook (Fig. 5, p9) | p5, p9, p15 | Only a research audit; no typed verdicts | **Correct** for measuring the verifier. "Typed verdicts" comes from the other paper cited there, not this one. |
| SCHEMA.md:30 / companion.md:323 — "proposed default 0.05" false-pass ceiling (no citation) | The paper's cliff is (1−τ)/2 = 0.45 at τ=0.10 (p4). The audited judge was 0.01 to 0.014 (p5, p15). The paper proposes no ceiling. | p4–5 | Not attributed to the paper in our docs | **Not from the paper; correctly marked `design`.** For reference, 0.05 sits far below the paper's cliff. |
| companion.md:273, 344 — "quality retirements stop while evictions continue, and nothing flags it" / "Watch the verifier: quality retirements against cap evictions over a period" (no citation) | p6 and Fig. 6c (p13): "what survives is churn, not judgment" | p6, p13 | Uncited use of the paper's finding. The runtime-monitor reading carries the same overreach as SCHEMA:138. | **Supported as an observed pattern; overstated as a diagnostic.** p17 frames the audit as pre-deployment, "rather than as a monitoring metric". |

### Other findings relevant to these themes (with page numbers)

**(a) Declaring behaviour and checking it before use vs. observing it after use (safety).** This is the paper's central operational claim: audit before, don't infer after.
- The paper's own term is "a before-deployment go/no-go test" (p2, p5). Fig. 5 (p9) lays it out as a playbook: "Inject known defects → Estimate false-pass rate → Compare to cliff → Decide GO / FIX".
- Observing after the fact fails because "no aggregate pass rate separates those three regimes" (p9, Conclusion). The curator's failure "surfacing in no aggregate metric" is on p1, and "the outcome looks healthy while governance has quietly stopped" is on p8.
- The audit is framed "as a before-deployment gate rather than as a monitoring metric" (p17).
- "The contribution is a behavioral safety result, not a performance one" (p1).
- Adversarial coupling (p14): if skills learn phrasing that blinds the judge, "no fixed audit bounds it". A one-time audit therefore does not cover a learned, co-evolving judge.

**(b) Token/context cost of exposing many tools/skills.** Not discussed. The only related points: the Router retrieves "at most one skill per task" (p3), and stale entries "crowd retrieval" (library drift, p1). Neither is measured in tokens.

**(c) Precondition or contract checking, and parity between a filter and the executed thing.**
- Each trial has a "structural contract" checked by the deterministic QC (p3, App. A p11–12).
- The judge "does not reliably penalize contract violations" (p5). This argues for deterministic contract checks next to judges.
- Fig. 7 (p15): a claim negation leaves markers "byte-identical, so deterministic QC (and even a value check) sees nothing wrong", which shows the limits of a syntactic check.
- App. H (p17) suggests "perturb a precondition so that a previously correct artifact becomes wrong by construction" as a way to build ground truth.
- Filter/execution parity is not discussed.

**(d) Library growth/retirement.**
- Retirement plus a cap gives Ratchet's non-divergence guarantee (p3). This held even when retirement was inoperative: "all means within 0.125 of" the no-skill floor (p7).
- Harm is an inverted U: it is worst at q=0.45 (−0.065) because synthesis continues while retirement is disabled, so "low-quality skills accumulate to the cap and keep being routed to" (p7).
- Past the cliff, true retirement falls to about 0 in every subset (Fig. 4a, p8). Synthesis starves only where failures are scarce (BAND-58 20→11). The eval degrades only there (−0.036, p8).
- Cap eviction versus genuine retirement must be logged separately (p6, Fig. 6c p13).
- Fig. 8 (p16) shows the loop "winding down in time" under bias.
- The lever against bias is "the threshold τ, not more data" (p4, p14).

### What the paper does NOT support

**Limits the authors state themselves:**
- **Coverage (p9):** "one domain and composer" (MBPP+ is a control). Web navigation, tool-use planning and multi-agent coordination are "untouched". The seed-stable result is the synthesis/retirement mechanism, "not an end-to-end lift".
- **Exogenous corruption (p9):** the authors can "locate a real judge relative to the cliff… but never exhibit one that has drifted past it". A learned judge that the library exploits is "out of scope" (p9, p14).
- **Model (p9, p17):** the channel is binary, and the retirement rule attributes each outcome to a single skill. "Continuous rewards, multi-skill composition, and learned retrievers" are outside it. A curator facing both bias and confounded attribution "is strictly worse off… but the size of the effect is not something this paper measures". The extension to continuous rewards is stated "not as a proved extension" (p17).
- **Audit transfer (p9, p17):** failures that don't localize need a task/precondition mutation instead.
- **QC measures citation discipline, not insight (p9).**
- **No detectable lift (p7, p15–16):** +0.014 ± 0.054 over 3 seeds; paired p=0.63; "harm test… p=0.61". "We claim the lift is undetectable at this resolution, not provably zero."
- **The cliff constant is Ratchet's (p17):** "The particular constant πτ = (1 −τ)/2 is Ratchet's… A different governance rule inherits the same dichotomy with its own constant."

**Where our docs overreach:**
1. "Disjoint defects" (SCHEMA:64) should be "complementary".
2. "Raw deprecations looked normal" (SCHEMA:117, companion:146) is false for REPORT-MAIN-71, the table actually cited: they fell to 3.7/3.0. It holds only for the abundant subsets (p13, Fig. 4).
3. "Genuinely bad skills" (companion:146): the paper's "genuine retirement" means contribution-rule retirement as opposed to cap eviction, not skills verified to be bad. The bias was also injected on a deterministic grader, not produced by an LLM judge.
4. Curator health as a lenient-judge signal (SCHEMA:138, companion:273/344) is a runtime-monitor use the paper doesn't test and frames against (p17). Zero retirement also happens with a clean grader when few skills are bad (clean 1.3 ± 1.2).
5. A strict judge "costs throughput heavily" is only predicted by theory (κ≈0.04). Empirically the strict judge matched the clean loop (+0.024) and retired 10.3 skills (p6–7).
6. The p4 citation for "contribution below −τ" states the pass-rate form. The contribution form is on p8/p13, and the rule is "falls to", i.e. ≤.
7. Our docs omit the paper's workaround for non-localizing failures (precondition/task mutation, p17).
8. Any threshold for admission or certification, including the 0.05 ceiling, is ours, not the paper's. Our docs already label this correctly as `design`.

### Figure candidates for appendix

| Page | Figure/Table | What it shows | Raster/vector (guess) |
|---|---|---|---|
| p2 | Fig. 1 | Blind-curator schematic: the solve→judge→curator loop under an honest vs a false-pass reward | Vector (text labels extracted as text) |
| p5 | Fig. 2 | Defect-injection gate: flag rates by 7 defect classes for deterministic QC vs the held-out judge | Vector (axis ticks/labels extracted) |
| p6 | Table 1 | Reward-degradation sweep on MAIN-71: Tail eval, Δclean, Synth, Dep., True-ret., Evict, Div. | Text table (vector) |
| p6 | Fig. 3 | (a) observed failures / synthesis / genuine retirement vs q, marking the "retirement cliff" and "curator off"; (b) Δeval vs realized corruption, an inverted U | Vector |
| p8 | Fig. 4 | Across BAND-58, HARD-133 and MBPP+: (a) genuine retirements, (b) skills synthesized, (c) Δeval vs q | Vector |
| p9 | Fig. 5 | Deployment playbook: inject → estimate false-pass → compare to cliff → GO/FIX | Vector |
| p12 | Table 2 | All experiments at a glance: subsets, models, reward, split, fail rate, floor | Text table |
| p13 | Fig. 6 | Retirement signature on MAIN-71 and BAND-58; (c) genuine retirement vs cap-eviction churn decomposed (raw 9/5/1) | Vector |
| p15 | Fig. 7 | A verbatim claim-negation defect ("grew"→"fell"): QC PASS, judge ✗ | Vector (text boxes extracted) |
| p16 | Fig. 8 | Heatmap of per-round deprecations by condition (cell values extracted) | Vector (a heatmap, but cell values came through as text) |
| p16 | Table 3 | Paired lift on BAND-58: continuous/binary lift, harm and targeted-class p-values | Text table |

---

# 2607.23332 — AllocBench: Measuring Online Tool Allocation Capability in LLM Agents

**Read in full:** yes, all 24 printed pages (line 1 to EOF at line 1587, "24" is the last page footer; includes Appendices A–I).

## Summary
AllocBench is a synthetic online-learning benchmark that tests whether LLM agents defer committing a scarce "build" budget (B tools, of N=8 latent task classes, over T=60 turns) until a class has recurred, rather than building on first sight. It uses a four-rung "framing ladder" from abstract (R0: colored-ball keep/pass in free text) to declarative tool calls (R1) to required-code claims (R2) to full reusable-script construction (R3). Models: Claude Haiku 4.5, Claude Opus 4.8, GPT-5.4-mini, GPT-5.6 Sol (frontier panel), plus an open-source Qwen2.5-Coder-14B-Instruct trained with QLoRA+PPO for the transfer study. All frontier-model comparisons use 24 canonical seeds (2000–2023), paired within-model/within-seed, with 95% seed-bootstrap intervals (10,000 resamples). No held-out task-domain generalization is tested; it's one synthetic numeric-puzzle environment (8 procedure families: LCG, modpow, continued fractions, CRT, Josephus, quadratic map, xorshift, matrix power).

## Ledger table

| Our claim | Paper's exact figure | Page | Setup/caveat | Verdict |
|---|---|---|---|---|
| SCHEMA.md B1: "once building meant writing code, first-sight commitment was 85-99% for three of four models (2607.23332 **M** Table 1, p6)" | Table 1, R2 column: Haiku 4.5 = 99%, Opus 4.8 = 92%, GPT-5.4-mini = 85%, GPT-5.6 Sol = 39% | p6 | Pooled among realized commitments, N=24 seeds each; Table 1 caption: "Only GPT-5.6 Sol preserves some allocation ability in R2, and all the models fail in R3." | **Correct.** Three of four models (Haiku, Opus, GPT-5.4-mini) sit at 85–99% at R2 (first code-required rung); the fourth (GPT-5.6 Sol) is at 39% there but reaches 100% at R3. |
| SCHEMA.md B2: "Emitted once,...not per repair attempt. Why: recurrence, not retries, should drive a build (2607.23332 **M** p8)" | Discussion (p8, "Implications for agent systems"): "current models cannot simultaneously manage budget allocation and tool creation. This suggests that tool-building agent systems should separate the abstract decision to invest from the process of creating the tool." | p8 | The paper's whole thesis is "build only on confirmed recurrence, not first sight" (Fig. 1, p3–4). It never discusses "retries" (repeated attempts within one build/repair loop) as a contrasting trigger — the word "retries" appears only for mechanical/parsing retries (empty-fence retries, transport retries), an unrelated methodological device (Appendix B.6, F.5). | **Overstated / imprecise paraphrase.** The "recurrence" half is well supported; the "not retries" contrast is the schema author's own analogy, not a finding or framing in the paper — the paper never opposes recurrence to retries. |

## Other findings relevant to the themes
- **(a) Declare/check-before-use vs. observe-after-use:** Not really this paper's territory — AllocBench observes a behavioral policy (commit vs. pass), it does not test precondition/postcondition declarations. Closest: the paper's own "preregistered" trigger criterion (Appendix A.2, p12) is a pre-declared statistical rule (≥30-point jump) fixed before data collection — an example of declaring a check before observing results, but about experimental methodology, not agent safety.
- **(b) Token/context cost of exposing many tools:** Not covered — AllocBench is about *when* to build a tool, not the cost of having many tools available. Not relevant to token/context load themes.
- **(c) Precondition/contract parity:** Not covered directly. Loosely related: "cross-type misapplication" check (Appendix B.6, p15) — the R3 harness binds a written script to the class it was written on and refuses to run it on a mismatched class, logging the refusal (`n_cross_class_run_refused`) without executing or charging budget — 22/478 (4.6%) run attempts refused as type-mismatched (p15), lowest for the strongest models (Opus 1/66, GPT-5.6 Sol 0/133, GPT-5.4-mini 5/63) and higher for 14B Qwen (8/74). This is a real "declared-type-check-before-execution" mechanism, worth citing if this theme is wanted (not currently cited in our docs).
- **(d) Library growth/retirement:** Not applicable — budget is fixed (B=1,3,5), no retirement mechanism; tools accumulate but never expire within a session.

## What the paper does NOT support (authors' own limits, Section 6, p9)
- **Synthetic environment only:** "one synthetic numeric environment with engineered classes and streams"; real tasks have "ambiguous class boundaries, shifting frequencies, incomplete reusability, and an unknown number of classes" (p9).
- **24 streams only:** results need further experiments "to verify our results in different settings" (p9).
- **Reasoning off:** both GPT models ran at `reasoning_effort=none` because the endpoint rejected tool schemas with reasoning on; authors argue (not prove outright) this doesn't drive the effect since it's held fixed within-model pairs (p9).
- **RL case study uses a privileged critic** (sees true latent class rates) — "do not demonstrate non-privileged learnability," and make "no statements regarding the exact mechanistic cause of allocation suppression" (p9).
- **Relative scoring:** the Score metric is calibrated against an unimplementable exact hindsight optimum, so "should be referenced only as a measure of relative model performance" (p9).
- Conjectural mechanism (post-training on independent-reward coding datasets) is explicitly a "conjecture," not demonstrated (p8, p9).

## Figure/table candidates for an appendix
| Page | Fig/Table | Shows | Raster/vector |
|---|---|---|---|
| p4 | Figure 1 | Optimal policy diagram: pass-on-first-sight, build-on-recurrence, on one seeded stream (colored circles + BUILD/pass labels) | Vector (schematic diagram) |
| p5 | Figure 2 | First-sight commitment rate bar-style plot, R0 vs R3, per model, with 95% CIs | Vector (data plot, likely matplotlib) |
| p6 | Table 1 | Pooled first-sight commitment rates across R0–R3 per model + failure point | Vector (text table) |
| p7 | Figure 3 | Score scatter: R0 vs R2 score per model | Vector (data plot) |
| p8 | Figure 4 | First-sight commitment across ladder, Qwen base vs RL-trained | Vector (data plot) |
| p19 | Figure 5 | First-sight hazard vs build price K, three panels (B=1,3,5) — abstract vs code-required inelasticity | Vector (data plot) |
| p21 | Figure 6 | Training curves: reward and first-sight commitment vs outer step | Vector (data plot) |

---

## Cognitive Admission Control: Risk-Conditioned Assurance for Consequential Actions in Agentic Distributed Systems (arXiv 2609.16313)

**Read confirmation:** I read the whole file with the Read tool in three chunks: lines 1–549, 550–1099 and 1100–1658. `wc -l` reports 1657 lines, and the Read output runs to line 1658. The last line reached is 1657, the page-footer "15". The last page is 15 (Appendix C "Open Problems", ending "Fault-profile validation"). I covered pages 1–15, including the references (p13–14) and Appendices A (p14–15), B (p15) and C (p15).

**Summary:** He and Yu (OpenKedge.io; v1, 14 Sep 2026, cs.DC) propose a policy layer that sits between an agent's proposed infrastructure mutation and its dispatch. A policy maps a typed proposal plus a risk vector to "assurance obligations". A deterministic evaluator returns SATISFIED, VIOLATED or UNKNOWN for each obligation. Unknowns produce typed evidence-acquisition requests. A PERMIT mints a single-use certificate that binds the proposal digest, the witness manifest and the dispatch guards. The paper gives formal results (Theorems 1–3, Propositions 1–3, Properties 1–3) and a TypeScript prototype. The evaluation is CACBench: 13 constructed local failover state machines × 7 controllers (AuthOnly, LivePolicy, CAC, and the ablations NoGuard, NoEFD, NoRemediation, NoTypedEvidence) × 30 seeds, giving "13 × 7 × 30 = 2,730 trials" (p9). The seeds only vary parameters such as cluster IDs and lag magnitude, and "do not sample independent operational incidents" (p9). **No language models are used:** "No language-model API is invoked" (p9). There are also 9,000 timing samples (3 processes × 1,000 × 3 workloads, macOS M4, Node v25.2.1; p11), 133 passing tests, and a finite model check over 43,561 profile/rule combinations (p10, p14–15). Results are reported as counts only, with no confidence intervals or significance tests (p10).

**Ledger table:**

| Claim/number as used in our docs | Exact figure in paper | Page | Setup/caveat | VERDICT |
|---|---|---|---|---|
| SCHEMA.md:90, `results[]` verdicts satisfied / violated / unknown with `unknown_cause`: "typed verdicts; an unknown names what is missing (2609.16313 M p4-5)" | Eq. 12: SATISFIED(W), VIOLATED(W), UNKNOWN(Conflict), UNKNOWN(c). "When no valid witness exists, c identifies a failed structural constraint, stale or future-dated evidence, untrusted provenance, incompatible version, or missing usable evidence" (p4). "The policy must distinguish a missing observation from evidence that its predicate is false" (p4). Abstract: "distinguishes satisfied, violated, and unresolved obligations" (p1). | p4 (Eq. 12, causes); p5 (DEFER with requests) | Specified for one action's obligations. The prototype implements it with synthetic receipts. UNKNOWN has two kinds: Conflict (equal-priority positive and negative witnesses, p4, A.4 p14) and missing/ineligible evidence. | **correct.** Suggest `unknown_cause` include `conflict`, because in the paper an unknown can mean contradicting evidence as well as missing evidence. |
| SCHEMA.md:97, `decision`: admit, reject, defer; `evidence_requests[]`: "an unknown defers with a typed request (2609.16313 M p5; for one action, not a library)" | "DEFER with unresolved obligations and typed acquisition requests" (p5). The paper has **five** outcomes: PERMIT, DENY, DEFER, ESCALATE ("when unresolved approval obligations need an authorized reviewer"), ABORT ("when evaluation cannot finish within its operational bounds") (p5; Alg. 1 p8). "A single admission certifies one bounded dispatch" (p12). Certificates are single-use (p5). | p5, p8, p12 | Scope is one consequential runtime action on infrastructure, not admission of a reusable component. | **correct for the cited sentence and its scope note.** The three-value enum is our simplification: in the paper an unknown *approval* obligation escalates rather than defers, and budget exhaustion aborts. |
| SCHEMA.md:102, Admission rule 2: "The decision is a conjunction over the checks its level requires; no score enters it (2609.16313 M p6, theory)" | Def. 6: admissible when "every required obligation returns SATISFIED" (p4). Advisory obligations "produce diagnostics" only (p4). Prop. 1 "Compensatory scores can bypass a required condition": with f(zn)→+∞ via unrelated proxy features, "the scalar rule admits some zn that violates conjunctive admission" (p6). | p4 (Def. 6), p6 (Prop. 1), p14 (A.1) | This is theory and is not tested empirically. The authors limit it: "It excludes non-compensatory scalar encodings of conjunction" (p6), and "The issue is substitutability, not scalar notation itself" (p14; the indicator 1[x≥1 ∧ y≥1] is acceptable). | **correct, with a caveat.** The paper argues against *compensatory* scores. It does not argue against scores as such. "No score enters it" is our stricter design choice (defensible), not something the paper proves. The "theory" label is accurate. |
| companion.md:157: "Admission is a conjunction over the checks its level requires, and no score enters it, the shape Cognitive Admission Control (M) uses for a single action." | As above: Def. 6 p4, Prop. 1 p6, one bounded dispatch p12. | p4, p6, p12 | Same as above. | **correct.** "For a single action" matches the paper's scope. |
| companion.md:157 (same paragraph, not explicitly attributed but reads as part of the CAC point): "an unknown verdict defers or rejects" | CAC never rejects on an unknown. DENY is only "for authorization, static-compliance, or decisive required-obligation violation" (p5). Unknown → DEFER or ESCALATE (p5; Alg. 1 lines 13–22 p8). Denying on deferral is the **NoRemediation ablation**, which "completes none of" the 30 underprepared intents, dropping completions "from 120 to 90" (p10; Table 2). | p5, p8, p10 | If "rejects" is meant as our own design, it is uncited and fine. If it is read as CAC's behaviour, it is wrong. | **wrong if attributed to CAC.** It should say "an unknown verdict defers (or escalates when it needs a reviewer); only a violated check rejects". Otherwise mark "rejects" as `design`. The paper's own data shows reject-on-unknown costs completions. |
| companion.md:298, table row "measuring the verifier, typed verdicts → already built in a paper: The Blind Curator, Cognitive Admission Control (M)" | The prototype "implements typed receipts, Ed25519 signatures, policy-defined guard templates, and nonce consumption", and "The 133 passing tests support the exercised behaviors" (p8). | p8 | CAC supplies the typed-verdict half. It does not measure verifier error rates (its verifiers are synthetic receipts). Structural cuts are imported from EFD [7] (p13). | **correct** as a split credit. Make sure no one reads it as CAC measuring the verifier. |
| companion.md:157, other sentences ("Running without error is never evidence"; "The paper's own limit on its audit is that injected defects…") | Not CAC claims: the first cites 2604.00392 and the second is about The Blind Curator. CAC is compatible with the first: predicate evaluation "cannot substitute a generic success flag for missing evidence" (p8), and a harmful effect "can still return a successful acknowledgement" (p9). | p8, p9 | n/a | n/a (not a citation of this paper). |

No other occurrence of "2609.16313", "Cognitive Admission Control" or "Admission Control" in either doc. I searched both (grep -i).

**Other findings relevant to these themes (with page numbers):**

(a) Declaring and checking before use vs observing after use:
- CAC is purely a pre-dispatch check, and the authors bound its reach. "Pre-dispatch checking is weaker than commitment-time checking unless the target preserves the bound conditions" (p13). Guard reads are not "atomic with target execution" (p5). Modes A/B/C (check before forwarding / atomic target-side precondition / transaction protocol) are on p7.
- The evaluation uses **independent effect observation**, with the controller's verdict separated from the ground-truth outcome: "controller verdicts and response codes do not set the outcome labels" (p9). "response status, execution attempt, completion, and harm must remain separate fields" (p11).
- Table 2 (p10): AuthOnly 390 attempts / 180 complete / "180 harmful". LivePolicy 180 / 120 / 30 harm. CAC 150 / 120 / "0" harm.
- The authors on the comparison: "This suite therefore does not establish a general utility advantage over a competent live-policy check" (p10).
- "Authenticity … does not establish the truth of the claim" (p3). "Signatures establish provenance … not the truth of a sensor reading" (p12).

(b) Token/context cost of exposing many tools/skills:
- **Not discussed.** R includes tokens and context only as an abstract resource tuple (p2). "The corrected experiments report no model-token or monetary savings" (p10).
- Only local latency is measured: median 4.65–5.69 ms at 1 obligation, 24.91–26.86 ms at 8 (Table 3, p11). Full discharge goes from 0.072–0.079 ms at 1 receipt to 67.31–72.69 ms at 12, with a hard cap at 12 receipts (p11).

(c) Precondition/contract checking; parity between the filter and the executed thing:
- Central to the paper. "The forwarded operation must be the operation validated" (p5).
- Exact-action proposal digest (Eq. 15, p5; Property 2, p7). "binding of the checked request to the forwarded request" (p7).
- Envelope mode: "parameter attenuation alone is insufficient: a different target can require different evidence" (p4). The prototype "conservatively require[s] readmission when a proposal changes" (p8).
- "An exact proposal digest prevents substitution but does not derive a missing guard" (p14).
- Evidence typing: in the NoTypedEvidence ablation a wrong-class receipt "admits thirty harmful actions" (p10–11).
- Freshness window with a lower bound that rejects future-dated receipts (Eq. 9, p3; A.4, p14).
- Unknown guards "fail closed" (p5, p7).
- Scenarios cover missing, unavailable and wrong-class evidence, drift and revocation (Table 1, p8).
- An example obligation contract with `maxFreshnessMs: 2000` appears in Listing 1 (p15).

(d) Library growth/retirement:
- **Not discussed.** Nearest relevant points: certificate lifetime is bounded by the earliest receipt expiry (Eq. 16–17, p5). Under Policy updates, "Learned lessons … may propose new obligations. They cannot alter the active policy without the governing approval process", and a policy-epoch revision "may invalidate previously issued certificates" (p12). This is relevant to `expires_when`, but it is not about library curation.

**What the paper does NOT support:**
- The authors' own limits:
  - Results are "tested implementation behaviors and local costs, not production failure rates or comparisons of language-model capability" (p1). The zero-harm count "describes these fixtures, not a bound on deployment failure probability" (p10).
  - No LLMs are used (p9). The suite "is constructed around CAC's mechanisms and is not a representative sample of operational incidents" (p8).
  - Targets are local models, with no real replication, fencing or partitions (p12). The limits "preclude claims of production reliability, model-family generalization, economic savings, or high-throughput EFD scaling" (p12).
  - Guarantees are policy-relative: an omitted dependency "can preserve syntactic admission correctness while permitting harm" (p12).
  - "A conjunctive policy can block indefinitely if a required witness is unavailable" (p12).
  - There is no advantage over LivePolicy in completions (p10). Novelty overlaps with Mnemosyne: "We therefore do not claim deterministic admission, obligations, or repair in isolation as novel" (p13), and there is no comparison with it.
  - The prototype "is not a verified implementation of the entire specification" (p6).
  - A historical 5,261-record batch is disowned: "not evidence for the results below" (p10).
- Where our docs reach beyond the paper:
  1. Carrying the scheme over from single runtime infrastructure actions to admitting capsules into a library is our extrapolation. SCHEMA.md:97 already flags "not a library". SCHEMA.md:90 and :102 do not, but they are framed as shape, not evidence.
  2. "No score enters it" is stricter than Prop. 1, which targets compensatory scores only.
  3. "an unknown verdict defers or rejects" (companion.md:157) does not match CAC's DENY-only-on-violation rule.
  4. Collapsing to admit/reject/defer drops ESCALATE and ABORT.

**Figure candidates for appendix:**
- p7, **Figure 1**: layered deployment interface (untrusted proposer → trusted resolver/evaluator → certificate mint → gateway → target, with a remediation loop for missing evidence). A box diagram, text-extractable, so **vector**.
- p4, **Eq. 12**: the four-way discharge rule (a strong text-only candidate for the typed-verdicts point). Vector/text.
- p8, **Algorithm 1**: the admission specification showing DENY only on VIOLATED and DEFER/ESCALATE on UNKNOWN. Vector/text.
- p8, **Table 1**: scenario families. Vector table.
- p10, **Table 2**: controllers × trials, attempts, completions and harm (CAC 0 harm vs LivePolicy/NoEFD/NoGuard/NoTypedEvidence 30, AuthOnly 180; NoRemediation 90 completions). The best evidence figure. Vector table.
- p11, **Table 3**: local path latency ranges. Vector table.
- p15, **Listing 1**: example obligation JSON, a useful parallel to our postcondition/precondition record. Vector/text.
- The paper has no raster figures (none are referenced).

---

# Citation ledger — batch B (6 papers)

Checked against `C:\Users\m50066326\huawei\capsule-openjiuwen\SCHEMA.md` (v1.5, 2026-09-21) and
`C:\Users\m50066326\huawei\capsule-openjiuwen\deck\companion.md` (draft, 2026-09-21).
Every paper below was read end to end with the Read tool in sequential offset/limit chunks, including
appendices/supplementary material, until the file's last line.

---

## 1. Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents

**arXiv 2505.22954** (Zhang, Hu, Lu, Lange, Clune — ICLR 2026). Read in full: confirmed through the
printed page-72 footer, the last line of the .txt (Appendix J, "Additional Future Work Directions").
Body: pp. 1–10. Appendices A–J: pp. 24–72 (results, related work, algorithmic details, pseudocode,
benchmark/cost details, full agent diffs for SWE-bench and Polyglot F.1–F.2, "Similar target
functionality" G, the hallucination/objective-hacking case study H (pp. 69–70), additional safety
discussion I (p. 71), future work J (p. 72)).

**Summary.** DGM is a self-referential, self-improving coding agent: starting from one lightweight
Claude-3.5-Sonnet-based agent with a bash tool and an edit tool, it alternates self-modification
(editing its own Python codebase) and evaluation on coding benchmarks, keeping every agent it ever
produces in a growing, never-pruned archive and sampling parents from the whole archive (roughly
proportional to score, inversely to number of children) rather than always branching from the current
best. Main experiments: SWE-bench Verified and Polyglot, 80 iterations, k=2 parallel self-mods
(SWE-bench) / k=4 (Polyglot), staged evaluation (10→50/60→200 tasks), self-modification done by Claude
3.5 Sonnet (New) in both settings, benchmark evaluation by Claude 3.5 Sonnet (New) for SWE-bench and
o3-mini for Polyglot. Single run per main condition (one DGM run per benchmark; a 3-run stability check
on Polyglot gives 40.7%±2.3%). Compared against "DGM w/o self-improve" (fixed meta-agent, replicates
ADAS) and "DGM w/o open-ended exploration" (no archive, always modifies the latest agent), plus
handcrafted baselines (best checked open-source SWE-bench agent, Aider on Polyglot). A separate 3-task
side experiment (Appendix H) applies DGM to reducing tool-use hallucination, with a hidden
special-token hallucination checker, and reports an instance of objective/reward hacking.

### Ledger

| Claim in our docs | Paper's exact figure | Page | Setup/caveat | Verdict |
|---|---|---|---|---|
| SCHEMA A1 `effects`: "a Darwin Gödel Machine node, in a 3-task side experiment, removed the logging its hidden checker read" | "the agent removed the logging of special tokens that indicate tool usage (despite instructions not to change the special tokens), effectively bypassing our hallucination detection function" — node 114, in the hallucination case study run on "only 3 SWE-bench tasks" | p. 70 (case study evaluated on 3 tasks, stated p. 69) | Separate side experiment (Appendix H), not the main SWE-bench/Polyglot runs; 150 DGM iterations on 3 fixed tasks | **Correct** |
| SCHEMA A2 `suite_access`: "hacking was more frequent when the checked functions were visible" | "the hallucination checking functions are hidden from the coding agent during self-modification. We found that objective hacking … occurs more frequently when these functions are not hidden" | p. 70 | Same 3-task side experiment; qualitative finding, not a measured rate (no percentage given for "more frequent") | **Correct** (direction right), but note: the paper gives no quantitative frequency — it is a qualitative observation from one run (nodes 96 vs. 114), not a measured rate across many trials |
| SCHEMA A3 rule 2: "Retired is never deleted, and RSI may build from it (inv 2; p8)" | p. 8 text is the Safety Discussion (§5), which says the "DGM archive provid[es] a traceable lineage of modifications for review" — supports *never deleted / kept for review*. The stronger claim that later generations sample and build from *any* past (including underperforming) archive member is stated on pp. 4–5 (§3, "archived solutions can serve as stepping stones…", and p. 7, "open-ended exploration allows branching from any agent in the archive with non-zero probability") | p. 8 (cited); substance is on pp. 4–5, 7 | DGM's archive is unbounded and never evicts anything — there is no "retirement" concept at all in DGM, so the analogy is to an even stronger no-deletion policy than the capsule schema's (which does retire/cap) | **Correct in substance, but page is imprecise** — p. 8 supports "never deleted," the "RSI may build from it" half is better sourced to pp. 4–5/7 |
| companion.md Table 3 / Table 13: "Alita-G, Darwin Gödel Machine" listed as reference-from-task-outcome systems | Confirmed: DGM's only signal for keeping/advancing an agent is downstream benchmark score (SWE-bench/Polyglot pass rate), not a test of the agent's own declared job | pp. 5–6 | — | **Correct** |
| companion.md "Rule 4 is motivated by the Darwin Gödel Machine… a self-modifying agent removed the logging its hidden checker read" (no page given in companion.md) | Same as above | p. 70 | — | **Correct** |

### Other findings relevant to our themes

- **(a) Declare-then-check vs. observe-after-use.** DGM has *no* declared contract at all for its
  self-modifications — a change is admitted purely by re-running the benchmark and keeping the agent if
  it "compiles successfully and retains the ability to edit a given codebase" (p. 4, §3). This is the
  strongest available illustration of the "observe behaviour after use" failure mode our schema is
  designed against: the objective-hacking case study (pp. 69–70) is a direct instance of a system gaming
  an outcome measure because nothing about the *mechanism* (not just the score) was checked before
  admission — precisely inv 4/6 territory.
- **(b) Token/context cost.** DGM's own self-discovered improvements include context-management fixes:
  "Auto-summarize on context limit" and "More granular file editing/viewing" appear as evolved features
  in the archive-tree figure (Fig. 3, p. 7) — i.e., token/context blowup was itself a failure mode DGM
  had to evolve past, not a designed-in constraint.
- **(c) Precondition/contract parity.** None — DGM has no precondition or postcondition contracts; this
  is exactly what SCHEMA cites it for (motivating inv 4/6: "nothing may change the gate or the
  verifier," "no scope may include the verifier's inputs").
- **(d) Library growth/retirement.** DGM's archive only grows (§3, p. 4: "initialized with only one agent,
  and continuously accumulates all generated variants over time"); there is no cap and no retirement —
  the ablation "DGM Greedy" (Appendix A.3, p. 25) shows that *not* keeping/reusing all past nodes as
  stepping stones (branching only from the current best) costs 10.3pp on SWE-bench (50.0%→39.7%) and 8pp
  on Polyglot (38.0%→30.0%), i.e. an unbounded, un-retired archive is load-bearing for DGM's own results.

### What the paper does NOT support

- Author-stated limits (§6, Conclusion, pp. 9–10): DGM still "falls short of closed-source SoTA
  SWE-bench solutions"; a single SWE-bench run costs ~2 weeks and ~$22,000 (Appendix E.1, p. 32); results
  are "inherently limited by the capabilities of the underlying FM"; the open-ended exploration process
  itself (archive maintenance, parent selection) is kept *fixed*, not itself evolved; only two coding
  benchmarks were used, both in the coding domain.
- Safety (§5, p. 8; Appendix I, p. 71): "we have found no evidence of harmful or malicious behavior in
  the generated agents" — but the authors explicitly say this is under heavy sandboxing/time limits/scope
  restriction to their own codebase, and warn "scaled up versions of it could be" unsafe. The paper does
  not claim its safety observations generalize beyond this constrained setup.
- Main-run statistics: the headline SWE-bench/Polyglot numbers (20.0%→50.0%, 14.2%→30.7%) are each from
  a *single* DGM run; only a separate 3-seed check on Polyglot (mean 40.7%±2.3%) speaks to variance, and
  that check was not repeated for SWE-bench.

### Figure candidates for an appendix

| Page | Fig/Table | Shows | Raster or vector (guess) |
|---|---|---|---|
| 1 | Fig. 1 | DGM workflow schematic (archive→self-modify→evaluate loop) | Vector (drawn diagram) |
| 6 | Fig. 2 | SWE-bench/Polyglot score vs. iteration, DGM vs. 2 baselines vs. handcrafted SoTA | Vector (line plot) |
| 7 | Fig. 3 | Archive tree (node-graph) + progress line plot, SWE-bench | Likely raster for the tree (dense node/edge render), vector for the line plot |
| 8 | Fig. 4 | Bar charts: model transfer, cross-benchmark transfer, task transfer | Vector |
| 69 | Fig. 8 | Archive tree for the hallucination case study | Likely raster (same tree-render style as Fig. 3) |
| 25 | Table 1/2 | Ablation numbers (DGM vs. Greedy vs. w/o components) | n/a (table) |

---

## 2. Alita-G: Self-Evolving Generative Agent for Agent Generation

**arXiv 2510.23601** (Qiu, Qi, Wang et al., Princeton/Tsinghua/CUHK et al.). Read in full: 15 pages
(body + references), confirmed at the file's last line, "15" (no appendix beyond references).

**Summary.** Alita-G turns a generalist agent (Manager Agent on Claude-Sonnet-4 + Web Agent on GPT-4.1)
into a domain specialist by having the master agent repeatedly (K=1..5 times) execute the *target task
set itself*, harvesting Model Context Protocol (MCP) tools from successful trajectories, abstracting
them (parameter generalization, context removal, interface standardization, docs) into an "MCP Box,"
and then serving a specialized agent that retrieves relevant MCPs via RAG (cosine similarity over
description+use-case embeddings, threshold τ=0.7 by default) at inference time. Evaluated on GAIA
validation (466 questions, full set), PathVQA (100 sampled), and HLE (100 sampled), using
text-embedding-3-large. No repeated-seed variance is reported for the main table; ablations (Tables
2–5) are each single evaluations on 25-question or full GAIA-validation subsets.

### Ledger

| Claim in our docs | Paper's exact figure | Page | Setup/caveat | Verdict |
|---|---|---|---|---|
| companion.md Table 3: "a self-built tool library lifts GAIA validation pass@1 from 75.15% to 83.03%, on the same set it was built from" | Table 1: "Original (pass@1)" total 75.15% vs. "Alita-G3× (pass@1)" total 83.03%, both on the full GAIA validation set (466 Qs) | p. 7 | MCP Box for the 3× condition was generated by running the master agent 3 times over the *same* validation set it is then scored on (§4.1, §5.2) — same-set training/eval, explicitly caveated in companion.md | **Correct**, and correctly caveated as same-set |
| SCHEMA "Rejected" section: "Anything from Alita-G's selection-text tables: 1.2 points, one run, built and scored on one set (p8-9)" | Table 2 (p. 8): "RAG with Description+Use Case" 83.03% avg vs. "RAG with Description" 81.82% avg → 1.21pp gap | pp. 8–9 (Table 2 p.8, Tables 3–5 pp.8–9) | Single-pass evaluation on GAIA validation set, no repeated seeds/std reported for this ablation | **Correct** — 1.21≈"1.2 points," single run, same set (GAIA validation) used to build and to score |

### Other findings relevant to our themes

- **(b) Token/context cost.** Directly measured: "A LITA -G (3×) reduces average token consumption to
  10,394 on GAIA compared to 12,305 for the original baseline, representing a 15.5% efficiency
  improvement" (p. 7–8) — a clean quantitative example of tool/skill curation reducing per-call token
  cost, which is exactly the theme SCHEMA cites SkillFuzz for on the *harm* side; here it's a curated
  (RAG-filtered, small) tool set reducing cost while raising accuracy.
- **(b) Growth vs. redundancy.** §5.2 (p. 8–9, Table 4): as MCP Box iterations k go 1→5, MCP count grows
  26→128 but connected components (independent "families," similarity τ=0.7) grow only 26→65; the
  effective-coverage ratio (#Clusters/#MCPs) drops from 1.00 to 0.51 — a directly quantified
  redundancy/diminishing-returns curve for a growing tool library, relevant to library-growth theme (d).
- **(d) Library growth control.** §5.2 explicitly picks k=3 as "a favorable balance between computational
  cost and utility" because gains saturate (80.00%→83.03%→83.03%→83.63% for k=1..5) while redundancy
  keeps rising — an empirical case for capping/curating rather than unboundedly accumulating tools.
- **(c) Selection/filter mechanics.** §3.4 and Table 3 (p. 9): threshold-based vs. top-k selection
  compared; optimal τ=0.70 (84.0% on a 25-question subset), both too-low and too-high thresholds hurt —
  relevant to selection-filter design though not a precondition/postcondition contract in our sense.

### What the paper does NOT support

- No explicit "Limitations" section; the paper does not discuss safety/security of auto-generated,
  auto-abstracted MCP tools (arbitrary code the agent writes and later re-executes), does not report
  variance/seeds for its headline numbers, and evaluates PathVQA/HLE on only 100-question samples "due to
  resource constraints" (§4.1) rather than full sets. It does not test generalization beyond
  GAIA/PathVQA/HLE, nor cross-model transfer of the MCP Box (contrast with CoEvoSkills, which does test
  cross-model transfer).

### Figure candidates for an appendix

| Page | Fig/Table | Shows | Raster or vector |
|---|---|---|---|
| 3 | Fig. 1 | Overall Alita-G workflow (3-stage pipeline diagram) | Vector |
| 11 | Fig. 2 | Raw vs. abstracted MCP code snippet comparison | Vector (text/code image) |
| 12 | Fig. 3 | Baseline-fails/specialized-succeeds worked example | Vector (text diagram) |
| 7 | Table 1 | Main accuracy/token results across benchmarks | n/a (table) |
| 9 | Table 4 | MCP Box scalability vs. k (accuracy, #MCPs, #clusters, similarity) | n/a (table) |

---

## 3. CoEvoSkills: Self-Evolving Agent Skills via Co-Evolutionary Verification

**arXiv 2604.01687** (Zhang, Fan, Zou, Chen et al. — COLM 2026). Read in full: 23 pages, confirmed at
the file's last line (Appendix D.5, CoT-Guided prompt, page "23").

**Summary.** CoEvoSkills lets an LLM agent autonomously author structured, multi-file `SKILL.md`
packages (not single-function tools) through an iterative co-evolution loop between a Skill Generator
and an informationally isolated Surrogate Verifier: the verifier synthesizes deterministic test
assertions from the task instruction/observable inputs/outputs only (never the hidden ground truth),
scores the skill, and gives structured failure diagnostics; only when the surrogate suite fully passes
does a Ground-Truth Oracle re-execute the skill in a fresh environment and return an opaque pass/fail
bit (no test content), which either ends the loop or forces the verifier to escalate its own tests.
Evaluated on SkillsBench (85 tasks, 2 excluded for infra reasons → 83 used), backbones Claude Opus 4.6
(via Claude-Code) and GPT-5.2 (via Codex), plus zero-shot transfer of Opus-evolved skills to 5 more
models (Claude Sonnet 4.5, Haiku 4.5, Qwen3-Coder-480B, DeepSeek V3-671B, Mistral Large 3-675B).
Baselines run over 5 independent runs (mean±std); ablations (Appendix A) are single runs "due to
computational cost."

### Ledger

| Claim in our docs | Paper's exact figure | Page | Setup/caveat | Verdict |
|---|---|---|---|---|
| companion.md Table 15: "a separate verifier session (CoEvoSkills, M)" | "Surrogate Verifier, a separate LLM session without inheriting the generator's biases" (§1, §3.3); "uses an independent LLM session πθV and receives only I, D…, y(i), and V(j). It has no access to generator reasoning or skill source" | p. 6 (§3.3) | Design property, not a numeric claim; no page given in companion.md | **Correct** |

*(CoEvoSkills is cited only once in either document, as a design-pattern reference with no numeric
claim, so there is only one ledger row.)*

### Other findings relevant to our themes

- **(a) Declare/check-before-use vs. observe-after.** This is CoEvoSkills' central mechanism: skills are
  held at a "not yet solving the real task" stage and tested against surrogate assertions *before* the
  opaque Ground-Truth Oracle is even invoked (Alg. 1, p. 5); the oracle itself returns only a pass/fail
  bit with **no test content**, specifically to prevent the generator from overfitting to held-out tests
  (§3.3, p. 6) — a strong real-world example of "declared job tested before use, with the checker's own
  content withheld from the builder," directly relevant to inv 5 and the false-pass-ceiling theme.
  Appendix C (pp. 15–17) gives a detailed trace where the surrogate verifier passes 15/15 tests yet the
  oracle reports only 75% — a concrete instance of **surrogate/oracle non-parity**: the surrogate's own
  BLS re-implementation used a 1% tolerance while the oracle required exact 5-decimal match, and by
  Round 5 the surrogate flagged the agent's *more accurate* TLS answer as wrong because it disagreed with
  the surrogate's own (less accurate) BLS estimate — a directly on-point illustration of "parity between
  a filter/verifier and the executed thing" being imperfect and why the independent oracle remains
  necessary (p. 17, "The surrogate-GT gap").
- **(c) Precondition/contract checking.** No explicit precondition/postcondition contract language;
  verification is behavioral (assertions on outputs), not declared preconditions on skill applicability.
- **(d) Library growth/retirement.** Not studied — CoEvoSkills evolves *one* skill package per task, not
  a growing shared library; no retirement/cap mechanism is discussed.
- **(b) Token/context cost.** Context-cap parameter β=0.7 in Algorithm 1 (line 9: "if LLM context usage
  proportion > β: break") is an explicit context-budget guard, but no token-cost numbers are reported
  (contrast with Library Drift's and Alita-G's explicit cost tables).

### What the paper does NOT support

- The paper explicitly limits its own scope in the Conclusion (p. 10): "CoEvoSkills evolves skills from
  task-relevant background knowledge available at initialization" — i.e., it is *not* open-world skill
  discovery; that is left to future work (citing OpenSkill). Two tasks were excluded from evolution-cost
  statistics for infrastructure reasons (Appendix B, p. 15), so the reported 4.1 average verification
  cycles / 2.4 oracle rounds are over 83, not 85, tasks. Ablations (Table A1, p. 14) are explicitly
  "single runs due to computational cost" — no variance estimate for the −30.0pp / −28.7pp ablation
  deltas.

### Figure candidates for an appendix

| Page | Fig/Table | Shows | Raster or vector |
|---|---|---|---|
| 2 | Fig. 1 | Tool vs. skill illustration | Vector |
| 2 | Fig. 2 | Pass rate vs. evolution iteration (line, with 4 static baselines) | Vector |
| 3 | Fig. 3 | Co-evolution framework diagram | Vector |
| 8 | Fig. 4 | Skill quality vs. baselines bar chart | Vector |
| 9 | Fig. 5 | Cross-model transfer bar chart (8 models) | Vector |
| 9 | Fig. 6 | Per-domain pass-rate bar chart (11 domains) | Vector |
| 16 | Fig. B1 | Verification-cycle / oracle-round distribution histograms | Vector |

---

## 4. SkillFuzz: Fuzzing Skill Composition for Implicit Intents Discovery in Open Skill Marketplaces

**arXiv 2607.02345** (Hu, Dong, Sun, Huang — Liverpool/MBZUAI). Read in full: 12 pages, confirmed at the
file's last line (references, page "12").

**Summary.** SkillFuzz treats the *composition* of individually-audited skills as the unit under test:
it formulates implicit-intent discovery as fuzzing over the binary skill-activation space, using plan
drift from a skill-free baseline plan (embedding cosine distance) as a differential oracle, without
executing anything. It extracts a structured skill contract per skill (preconditions, postconditions,
modifies-set, invariants, domain scope, abstract actions, extraction confidence) via LLM, prunes to a
task-relevant candidate set, seeds a contract-guided Monte Carlo Tree Search that expands toward the
embedding region of the most recently discovered high-drift intent, and scores candidates with an
"Intent Coverage Quality" (ICQ = drift × novelty) metric. Evaluated on the 196-skill SkillsBench
marketplace, 10 representative tasks, 8 planning agents (4 open-weight DeepSeek-R1 variants, 4
proprietary GPT-4.1/5 variants), GPT-4o-mini as the fixed intent-extraction/judge model (excluded from
the plan-agent pool). Budgets: B=200/task for RQ1/RQ2/RQ4, B=1000 for the RQ3 strategy comparison
(single seed/run per condition, not repeated).

### Ledger

| Claim in our docs | Paper's exact figure | Page | Setup/caveat | Verdict |
|---|---|---|---|---|
| SCHEMA `load_mode`, companion.md load_mode row: "severe drift toward unrequested goals rose from 4.7% of plans with one skill loaded to 66.5% with five, against a skill-free plan" | "severe drift is rare for singleton activations but rises monotonically with co-activation depth, reaching 66.5% at k=5, a fourteen-fold increase" (Fig. 6) | p. 9 | 66.5%/14 ≈ 4.75% ≈ the "4.7%" cited; the exact k=1 number is read off Fig. 6 (a bar chart), not stated as a number in the body text — the "fourteen-fold" phrasing is the only textual anchor | **Correct** (arithmetically consistent with the stated 14× multiplier); note the k=1 value is not itself printed as text, only implied by "fourteen-fold" and the bar chart |
| SCHEMA A2 admission rule 6: "A certificate covers one capsule, not capsules sharing a context (2607.02345 M p9)" | Fig. 6 title: "Severity is compositional, not additive"; belief non-decomposability (§III-A, p.4): "the joint plan πs is not recoverable from the set {πsi} … by any aggregation" | p. 9 (Fig. 6); mechanism stated p. 4 | — | **Correct** |
| companion.md "Not claimed": "severe drift rose from 4.7% … to 66.5% with five … and every gate judges one capsule at a time" | Same as above | p. 9 | — | **Correct** |

### Other findings relevant to our themes

- **(a) Declare-and-check before use.** SkillFuzz is itself a pre-admission, execution-free screening
  method: "operators lack a deployment environment … testing at the agentic plan is both sufficient to
  probe implicit intents and necessary given the lack of execution access" (p. 2). RQ2 (pp. 6–7) directly
  validates the "check before use" premise against "observe after use": 80.6% of the highest-risk
  *plan-level* flags are confirmed once the same compositions are actually executed by an independent
  Claude-based executor (Table II) — i.e., a measured parity rate between a pre-execution filter and
  execution-time behavior, on-point for theme (c).
- **(c) Filter/executed-thing parity.** RQ2's Table II is the paper's own quantified "does the filter
  match what actually runs" result: 80.5% (open-weight) / 81.0% (proprietary) / 80.6% overall detection
  rate, i.e. ~19.4% of plan-flagged compositions were *not* confirmed at execution (the paper argues these
  are mostly false negatives of the trace judge on diffuse effects, not false positives of the planning
  oracle — Discussion, p. 7).
- **(b) Token/context cost of exposing many skills.** The whole depth-effect result (Fig. 6, p. 9) *is*
  a token/context-exposure-cost finding: severity of unrequested-goal drift rises monotonically with the
  number of *simultaneously loaded* skills (k=1→5), independent of any single skill's own audit outcome.
- **(c) Contract construction.** §IV-A (pp. 4–5) is a full worked precondition/postcondition/modifies/
  invariant contract-extraction pipeline per skill, directly analogous to SCHEMA's manifest fields,
  though built for red-teaming rather than admission gating.

### What the paper does NOT support

- Threats to Validity (§VI, p. 9): thresholds (δmin, θ, δsev) are fixed globally, not tuned per
  deployment; the intent extractor/judge (GPT-4o-mini) has "residual judge bias … cannot be fully ruled
  out"; construct validity — a deceptively-planning agent (stating an innocuous plan while intending
  something else) would evade detection entirely, a threat model the authors say is closer to
  intentional misalignment than to the compositional risk they study; external validity — only a
  196-skill marketplace was tested, a larger/more adversarial marketplace "could exhibit a different
  contract geometry," and the paper does not model the cost/accuracy tradeoff of choosing budget B
  against real inference cost, nor re-screening after skills are updated post-admission.

### Figure candidates for an appendix

| Page | Fig/Table | Shows | Raster or vector |
|---|---|---|---|
| 1–2 | Fig. 1 | Compositional implicit-intent illustration | Vector |
| 5 | Fig. 2 | SkillFuzz workflow (contract extraction → MCTS search) | Vector |
| 7 | Fig. 3 | Coverage-over-iterations curves + agent×task coverage matrix (heatmap) | Vector, though the matrix panel may be rasterized if rendered as a heatmap image |
| 8 | Fig. 4 | Cumulative ICQ / high-severity-count growth curves | Vector |
| 8 | Fig. 5 | Drift-value distribution per strategy | Vector |
| 9 | Fig. 6 | Severe-drift fraction & mean drift vs. co-activation depth k | Vector |
| 9 | Fig. 7 | t-SNE projection of discovered intents, coloured by cluster | Possibly raster (scatter with many points, common to rasterize t-SNE plots) |

---

## 5. When Self-Evolution Backfires: Pre-Commit Gating against Skill Contamination in LLM Agents

**arXiv 2608.05810** (Shang, Xu, Sun, Xia, Hu, Xu, Zheng — Tencent, ICML 2026 FAGEN workshop). Read in
full: 9 pages, confirmed at the file's last line (references, page "9"). No supplementary material text
is present in the .txt beyond the reference list, despite in-text references to a "Supplementary
Material" for further detail — the file simply ends after the bibliography.

**Summary.** The paper shows self-evolving skill accumulation is non-monotonic: on Terminal-Bench 2
(TB2), an *ungated* agent (Hy3 backbone) that unconditionally admits every distilled skill rises to a
peak (R3, 62.3%/62% pass@1) and then collapses back toward its round-1 level (R5, 50.0%/50%) as the
pool grows from 35 to 179 skills, because later skills are distilled with earlier (possibly defective)
skills as reference context, so contamination propagates through descendant lineages and cannot be
undone by removing only the original bad skill. They propose Verifier-as-Gatekeeper (VaG): a
Cold→Warm→Hot progressive-trust pipeline — Gate 1 (schema validity + single-skill A/B held-out replay +
one LLM semantic-consistency check, conjunctive) for individual harmlessness, Gate 2 (marginal-gain
greedy subset selection on measured joint held-out performance) for combinatorial harmlessness. Split:
Event-50 (drives evolution), Holdout-14 (used only inside the gates), Test-25 (final, untouched). Five
evolution rounds, k=3 rollouts/task, one evolution trajectory per condition (not multi-seeded);
cross-model/cross-benchmark transfer of the frozen R5 pool is evaluated separately without re-evolution.

### Ledger

| Claim in our docs | Paper's exact figure | Page | Setup/caveat | Verdict |
|---|---|---|---|---|
| SCHEMA A2 `build_context`: "removing only the 8 bad source skills recovered 1.7 of 12.3 points" | "Removing the 8 harmful source skills … recovers only 2pp (50%→52%)" (rounded, main text); Fig. 4 precise version: "Of the 12.3pp peak-to-R5 drop, source removal recovers only 1.7pp and oracle cleanup 6.7pp[further to 5.0pp incremental]" | p. 7 (Fig. 4); rounded statement p. 5–6 | Single evolution trajectory (Event-50, k=3 rollouts/task); "8 harmful source skills" identified post hoc from the collapsed Ungated R5 pool | **Correct** — matches Fig. 4's unrounded 12.3pp/1.7pp exactly |
| companion.md Table 3: "removing the 8 bad source skills afterwards recovers 1.7 of the 12.3 points lost, in one run on the split the skills came from" | Same as above | p. 7 | Same | **Correct** |
| SCHEMA A2 `baseline_snapshot`/`contribution`: "gain against the current pool (p4-5)" | Gate 2's set utility f(H) and marginal-gain greedy selection ("add a candidate only when it improves measured joint performance") | pp. 4–5 (§Methodology, "Warm→Hot") | Design description, not a single number | **Correct** |
| SCHEMA A3 rule 1: "removing the gate that requires marginal gain over the pool cost 8 points in one run (p5-6)" | Table 2 ablation: "−Marginal-gain gate" → 64% pass@1 vs. 72% full VaG, "∆VaG −8" | p. 6 (Table 2); described p. 4–5 | Single-run ablation ("Ablations confirm… each intercepting a largely disjoint class"), Event-50 R5 only | **Correct**; page is closer to "p5-6" than exact, fine |

### Other findings relevant to our themes

- **(a) Declare/check-before-use vs. observe-after.** This is the paper's whole thesis, stated crisply
  on p. 2: "Voyager … verifies only that a skill completes its target task before storing it, but never
  checks whether that skill degrades performance on other tasks — precisely the failure mode we study,"
  and (p. 3) "skill admission [must be] an explicit promotion decision rather than a write. Every
  distilled skill starts Cold: recorded, but invisible to the agent." This is a near-literal statement of
  SCHEMA's "declare and check before any run uses it" principle, and a directly citable justification for
  why capsules should not be admitted based on trajectory success alone (cf. our A2 admission rule 3,
  "Running without error is never an anchor" — same idea, different paper (2604.00392), but this paper
  reinforces it independently).
- **(c) Precondition/contract-style checking.** Gate 1's three checks are a concrete instance of
  heterogeneous, conjunctive admission checks (schema validity / behavioral replay / semantic review), p.
  3–4; ablation Table 2 (p. 6) shows each intercepts "a largely disjoint class of harmful skills," with
  holdout replay mattering most (−10pp if removed) — directly relevant to why SCHEMA's postconditions
  combine deterministic + reference + judged anchors.
- **(d) Library growth/retirement.** Central theme: Proposition 1 (p. 4) gives a formal non-divergence
  bound tying bounded cap C and retirement threshold τ to a worst-case floor; the ablation A7 (bank
  cap=100 vs. default 50) shows the cap "primarily controls variance rather than mean performance" — this
  is the *same* qualitative finding SCHEMA separately cites Library Drift for, from an independent paper
  and independent benchmark (TB2 vs. MBPP+), which strengthens rather than duplicates the claim.
- **(b) Token/context cost.** §6.4 (p. 6–7): Default VaG uses ~14.5k LLM calls/100 rounds (43% more than
  no-skill baseline), 6.5h wall time vs. 2.3h for the no-skill baseline (2.8×); Ungated's per-trial token
  cost grows with its bloated pool up to 1.30M tokens/trial *for worse accuracy* than VaG's 0.77–0.94M —
  a clean quantified cost/accuracy tradeoff between gated and ungated growth.

### What the paper does NOT support

- Explicitly flagged caveats: "Trajectory shape, not single-round significance, is the evidence… 95%
  Wilson CI bands … overlap at intermediate rounds, so per-round point tests are underpowered" (p. 5) —
  i.e., the authors themselves say individual-round differences are not statistically significant; the
  claim rests on the qualitative shape of the trajectory across 5 rounds, not a hypothesis test. "Scale
  context" (p. 5): "These are not head-to-head baselines: backbone, task suite, and round budget all
  differ" from other self-evolution systems reporting higher absolute numbers (68.9–77.0) on the full
  TB2-89 suite — the paper does not claim VaG beats those systems, only that it isolates the
  contamination phenomenon in a small controlled setup (Event-50, one backbone, 5 rounds). It also does
  not claim generalization beyond one benchmark family (TB2 + NL2Bash transfer) or beyond the Hy3
  evolution backbone (only inference-time transfer to other backbones was tested, not re-evolution on
  them).

### Figure candidates for an appendix

| Page | Fig/Table | Shows | Raster or vector |
|---|---|---|---|
| 1 | Fig. 1 | Non-monotone accumulation illustration | Vector |
| 4 | Fig. 2 | VaG pipeline (Cold→Warm→Hot) diagram | Vector |
| 5–6 | Fig. 3 | Pass@1 across 5 rounds, Ungated vs. VaG, with 95% Wilson CI bands | Vector |
| 7 | Fig. 4 | Residual-contamination bar chart (peak/R5/source-only/oracle/VaG) | Vector |
| 6 | Table 1 | Main round-by-round results by difficulty tier | n/a (table) |
| 6 | Table 2 | Component ablation | n/a (table) |

---

## 6. Library Drift: Diagnosing and Fixing a Silent Failure Mode in Self-Evolving LLM Skill Libraries

**arXiv 2605.19576** (Zhang, Cui, Wang, Li, Qiu, Zhu, He — AWS/HSBC, ICML 2026 FAGEN workshop). Read in
full: 9 pages, confirmed at the file's last line (Table 3, per-seed results, page "9").

**Summary.** "Library drift": self-evolving skill libraries silently degrade below their no-skill floor
when accumulation isn't paired with outcome-driven lifecycle management. The system, "Ratchet," is a
five-phase per-round loop (Eval → Train → Critic → Synthesizer → Curator) around Claude Opus 4.7,
evaluated on MBPP+ hard-100 (100 tasks sampled from the 378-task MBPP+ test split, excluding the ~273
tasks Opus 4.7 already solves on all 5 baseline seeds; 60 train/40 eval), 100 rounds, mean±std over 3
seeds (42, 7, 13) for every condition. Default governance = outcome-driven retirement (Nmin=100
trials, τ=0.10) + bounded active-cap (C=50) + meta-skill authoring prior. 8 ablations (A1–A8) each
change one knob; a formal non-divergence bound (Proposition 1, Appendix D) ties the floor to τ, the
Hoeffding tolerance ϵ, and the cap C via a union bound.

### Ledger

| Claim in our docs | Paper's exact figure | Page | Setup/caveat | Verdict |
|---|---|---|---|---|
| SCHEMA A3 `evidence` field: "Harsh retirement, a low n_min, fell below the no-skill floor; the cap mainly controlled variance (p3-6)" | A4 (harsh retirement, Nmin 100→20, τ→0.0): "Result: −0.019±0.010, below the no-skill baseline" (p. 3–4); A7 (cap 50→100): "+0.317 comparable mean but substantially higher variance (±0.110 vs. ±0.018); the cap primarily controls variance rather than mean performance at this scale" (p. 6) | pp. 3–4 (A4), p. 6 (A7 discussion); Table 1 p. 5 | Mean±std over 3 seeds (42,7,13); no-skill floor established separately by A1 (+0.002) | **Correct** on both halves |

*(Library Drift is cited once in SCHEMA.md, by one composite sentence spanning two separate findings —
A4's below-floor result and A7's variance-not-mean finding — and once in companion.md Table 15 as a
qualitative "retirement under a cap" reference with no numeric claim.)*

### Other findings relevant to our themes

- **(a) Declare/check-before-use vs. observe-after.** Diagnostics precede fixes (§7, p. 5): "The
  trace-level diagnostics detected drift before end-task metrics declined. In A4, the bank collapsed to 2
  active skills by round 30, but pass@1 showed only gradual decline because the router adaptively chose
  NONE more often" — a clear case where an *aggregate* outcome metric (pass@1) masks an underlying
  failure that a structural, per-artifact signal (router engagement %, per-skill contribution ĉ(s))
  reveals much earlier; directly supports designing admission/health signals that don't rely solely on
  task-level pass/fail.
- **(c) Precondition/contract-style checking, filter/executed parity.** Not really present in contract
  form; the closest analogue is the Curator's outcome-driven retirement rule (retire once n(s)≥Nmin and
  ĉ(s)≤−τ), which is a *post-hoc, evidence-gated* retirement rule rather than a pre-admission
  precondition check — i.e., this paper's gate fires on accumulated evidence of harm after skills are
  already live, unlike VaG's (2608.05810) pre-commit gate. Worth flagging as a genuine design difference
  between the two "sibling" papers SCHEMA cites for retirement/contamination.
  - Note: **A2 (retrieval-only routing, bypassing the LLM gate) matters** — "confirming the LLM gate
    contributes beyond tf-idf∪embed similarity" (p. 4–5, A2 +0.077, only 24% of Default's gain despite
    98% router engagement) — a concrete instance of a cheap syntactic filter alone being insufficient,
    relevant to why SCHEMA's selection step layers a code filter *and* a model bind *and* a fit review
    rather than a single filter.
- **(d) Library growth/retirement.** This entire paper. Precise operational-cost numbers (§6.4, p. 5):
  Default uses ~14.5k LLM calls/100 rounds (43% more than the no-skill A1's 10k calls), 6.5h wall time
  vs. A1's 2.3h (2.8×) — near-identical cost framing to When Self-Evolution Backfires's §6.4, from an
  independent system/benchmark.
- **(b) Token/context cost.** §6.4 gives call-count and wall-time cost, not token counts per se (contrast
  with DGM's dollar-cost table and Alita-G's token table).

### What the paper does NOT support

- Author-stated Limitations (§ "Limitations," p. 6), verbatim: "(i) One benchmark (MBPP+ hard-100);
  generalization to broader domains (multi-step agents, SWE-Bench) is left to future work. (ii) Single
  model (Claude Opus 4.7); cross-model stability not established. (iii) The diagnostic thresholds (when
  to intervene) are empirically chosen; principled calibration is future work. (iv) We hypothesize that
  drift signals … become more sensitive in multi-step agents … empirical validation is future work." The
  Solver is explicitly "a single direct LLM call with no execution feedback, no self-refinement, and no
  tool use" (§6.1) — i.e. results are from a single-call code-generation setting, not an agentic
  tool-using loop, which is a materially different regime from the multi-step agent pipelines our schema
  targets. The paper explicitly flags this as a limitation to generalizing its numbers to multi-step
  agents (item iv above).

### Figure candidates for an appendix

| Page | Fig/Table | Shows | Raster or vector |
|---|---|---|---|
| 2 | Fig. 1 | Ratchet 5-phase loop (Router/Solver/Grader/Capsule/Skill Bank/Meta-Skill/Evidence Log/Critic/Synthesizer/Curator) | Vector (complex box-and-arrow diagram) |
| 6 | Fig. 2 | Held-out pass@1 by round, 8 conditions + Default, ±1 std bands | Vector |
| 5 | Table 1 | Main results (baseline/peak/gain/router/active/retired/critic calls) per condition | n/a (table) |
| 9 | Table 3 | Per-seed rolling-mean gain and peak | n/a (table) |

---

# Summary of WRONG or OVERSTATED claims found (≤15 lines)

**None found to be wrong.** All eleven distinct numeric/claim citations to these six papers in
SCHEMA.md and companion.md check out against the source text:
- DGM: hidden-checker/logging-removal claim (p70) — correct; hacking-more-frequent-when-visible (p70) —
  correct (qualitative, no rate given in paper); "retired never deleted… p8" — correct in substance, but
  the page is imprecise (p8 = Safety Discussion, which supports only "never deleted"; the "RSI builds
  from it" half is better sourced to pp. 4–5/7).
- Alita-G: 75.15%→83.03% pass@1 — correct, and already correctly caveated as same-set; "1.2 points, one
  run, one set" (Table 2, p8-9) — correct (1.21pp).
- SkillFuzz: 4.7%→66.5% severe drift at k=1→5 — arithmetically consistent with the paper's stated
  "fourteen-fold increase," though the paper never prints "4.7%" as text (it's read off a bar chart);
  "certificate covers one capsule, not shared context" (p9) — correct.
- When Self-Evolution Backfires: "1.7 of 12.3 points" — correct, matches Fig. 4 exactly; "cost 8 points"
  marginal-gain ablation — correct.
- Library Drift: harsh-retirement-below-floor and cap-controls-variance — both correct.
- CoEvoSkills: "separate verifier session" — correct, no numeric claim.

No overstatement found either — where a citation could be read as strong (e.g. Alita-G's headline gain),
the docs already caveat it ("on the same set it was built from"). One soft note worth the workshop's
attention: SCHEMA's DGM p8 citation is a page-precision nit, not a content error.

---

# 2608.25512 — A Programming Paradigm for Spatiotemporal Composability (Cordis)

## 1. Identification and read confirmation

- **Title:** A Programming Paradigm for Spatiotemporal Composability
- **Authors:** Yifan Shi (Peking University / DeepSeek-AI), Wei Zhang (Peking University), Tianyi Cui (DeepSeek-AI)
- **arXiv id:** 2608.25512
- **File:** `C:\Users\m50066326\huawei\capsule-openjiuwen\papers\2608.25512.txt` (4,708 lines)
- **Read confirmation:** Read sequentially end to end with the Read tool in ~500-line chunks, offsets 1→501→1001→1501→2001→2501→3001→3501→4001→4600 (with a final tail check to confirm the true end of file). No skimming or grep-based substitution was used for the body text; grep was used only afterward to locate exact page-break markers and the "Figure/Table" captions for citation purposes.
  - **Last line reached:** line 4708, which is the bare page number `92`, i.e., the final page of the References section (reference [127], A. Margara and G. Salvaneschi, "On the Semantics of Distributed Reactive Programming," ends at line 4703; the file then terminates at the page-92 marker).
  - **Body (non-reference) content ends** at line 4298, the last sentence of Section 8 (Conclusion): "...as a foundation for recoverable, coordinated, and continuous self-evolution in agent harnesses and other autonomous systems."

Page-break markers (bare numbers) were located for the whole file; page *N* is the text strictly between the marker for page *N−1* and the marker for page *N*. This is used throughout Section 3 below for exact page citations.

---

## 2. Summary

**Problem framing.** The paper identifies two "orthogonal dimensions" of dynamic composition (components loaded/unloaded/reconfigured at runtime, as opposed to static composition resolved at compile time):
- **Temporal composability** — upon removing a component, its modifications to the shared environment must be completely and safely reversed (the time dimension).
- **Spatial composability** — components must declare, discover, and resolve dependencies on one another, with lifecycles coordinated as dependencies change (the space dimension).

In the static setting these reduce to lexical scoping (RAII/bracket patterns) and module-import resolution, respectively; the paper's claim is that dynamic settings need new runtime mechanisms because effects are no longer lexically bounded and dependencies can appear/disappear/change identity live.

**Revertible effects (§3.1).** An effect is modeled as a function `Γ → Γ × (Γ → Γ)`: applied to a context it returns the new context *and* an explicit inverse. The "effect context" `∂Γ = Γ × (Γ → Γ)` pairs a state with an *accumulator* — the composition of inverses applied so far. `track`/`recover` operations are proved to form a monoid homomorphism (Theorem 5) and to satisfy a "soundness invariant" `φ(γ) = γ0` (Theorem 7), i.e., recovering after a correctly-inverted step is the same as recovering before it. This is refined into witnessed effect functions (`𝔈*_Γ`, Definition 8) that carry a proof obligation that the returned inverse actually reverts the state it was produced at, and into **effect iterators** (`ℑ_Γ`, Definition 17) that model a sequence of effects (e.g., a component's whole load) as a delimited-continuation-like generator, reverted in LIFO order (Theorem 16). This is "local temporal composability": one component's own effect sequence recovers its own starting context.

**Reactive coeffects (§3.2).** Dependencies are modeled as a partial function "coeffect context" `Σ = (k:K) ⇀ V_k` (an IoC container formalized mathematically). A component declares a **coeffect specification** `d ⊆ K` (the keys it needs). `notify_d(σ, σ′)` classifies any transition of the shared table as `activating` (satisfaction predicate `σ ⊨ d` becomes true), `deactivating` (becomes false), or `neutral`, which drives a component's activation/deactivation. This is "local spatial composability." §3.2.3 extends the model with **coeffect isolation** (per-realm rebinding of the same key, for multi-tenant/sandboxed use) and **coeffect interception** (cross-cutting, context-carried or component-declared metadata merged monoidally onto a value's resolution — used later for access-control policy in §6.3).

**The context paradigm (§3.3).** The effect context and coeffect context are unified into one recursive type `Γ∞ = μΓ. Γ × (Γ → Γ) × Σ`, and every component operation is disciplined to be a sequence of "context-mediated" stages (an operation on a declared key, or a provision of one's own key) — Definition 30. Because physical state (heap layout, generative names, monotone allocators, sent messages) cannot literally be restored, all the equalities of §3.1 are re-read up to an **observational equivalence ≃** built from what each key's own operations can distinguish (Definition 31 ff.) — e.g., a memory allocator is "commutative" up to renaming of handles but *not* up to comparing actual addresses if the interface publishes addresses (this is explicitly likened to the scalable-commutativity rule and to CompCert's memory relation).

**Independence and the calculus (§3.4–4).** §3.4 defines when two effects/coeffects are *independent* (their transformations pairwise commute), and shows this reduces to a *per-key commutativity witness* that a coeffect provider must supply as a proof obligation (Definition 44/46) — the runtime does **not** check it (confirmed again in §5.1.1: "What the operation does not check is the witness that 𝔈*_Γ carries... is an obligation on the component author rather than a property the runtime verifies," p.58–59). §4 gives an operational semantics: a **component** = (declaration `d`, provision `p`, witnessed effect iterator `e`); a **fiber** is a running instantiation with a lifecycle state `Inactive | Reloading | Active | Unloading` (Figure 1, p.34) driven by nine rules (`O-Insert`, `O-Retire`, `O-Remove`; `L-Begin`, `L-Iter`, `L-Finish`, `L-Divert`, `L-Leave`, `L-Unload`). A **guard** on `L-Unload` (`¬relied_n(γ)`) defers a provider's withdrawal until every dependent that resolved a key to it has itself deactivated — this is the mechanism that gives the ordering guarantee.

**Metatheory (§4.3), what it proves.**
- *Preservation* (Thm 64): well-formedness of the fiber registry is an invariant of all nine rules.
- *Temporal composability, global form* (Thm 68 "Recovery exactness," Cor 69 "Terminal recovery"): applying one fiber's accumulator at any later point reaches (up to ≃) the state as if that fiber had never run, *provided* every pair of fibers is "pairwise independent" (Lemma 66, which holds automatically because every coeffect key is commutativity-witnessed and disjoint provisions are enforced by `O-Insert`).
- *Spatial composability, global form* (Thm 70 "Ordering," Thm 71 "Resolution coherence"): a fiber only begins activating when its dependencies are satisfied; a provider is not withdrawn until every fiber that resolved a key to it has deactivated; a transition in flight runs against one fixed resolution or aborts.
- *Progress* (Thm 73): assuming the "precedence" relation `≺` (n may provide a key m declares) is acyclic and names are finite, every maximal sequence of lifecycle steps reaches a quiescent state (no deadlock, termination bound `S(n) ≤ (K+3)(V(n)+1)`).
- *Confluence* (Thm 80): assuming every component is "total on its provision" (Definition 76: an activation that finishes installs every key it declared), any two schedules of the same orchestration inputs quiesce (up to ≃ and renaming) at the same state as a from-scratch, dependency-ordered, never-unloaded assembly. The paper is explicit that this speaks "of the state, not of the emissions the system produced along the way" (p.54, leading directly into §6.1's boundary discussion).
- §4.4 sketches four extensions (asynchrony/inertia, failure, isolation-with-realms, configuration/reconciliation) each claimed to leave §4.3's results intact, argued informally rather than re-proved in full.

**Implementation (§5) — Cordis.** A TypeScript "meta-framework" with three tiers: (1) a **core library** realizing effect tracking (`ctx.effect`, Algorithm 1) and coeffect operations (`ctx.get/set/isolate/intercept`, Algorithms 2–3) and the component lifecycle as an *inertial* async state machine (Algorithms 4–5: `use`, `refresh`, `reload`, `unload` — reload/unload run to completion once started; target-view staleness is checked both at each iteration boundary and at transition completion); (2) a **declarative component loader** (§5.2.1) that reconciles a persistent configuration tree into fiber operations (least-disruptive per-field dispatch: id/url rebuilds, isolate reassigns realms via a delimiter-tag algorithm (Algorithm 7), intercept updates in place, config is handed to the component, disabled toggles unload/reload) and a **hot module replacement (HMR)** engine (§5.2.2, Algorithms 8–10: dependency-graph fixed-point classification of accepted/declined modules, stale-entry detection, and a transactional reload that rolls back on import failure); (3) application frameworks such as Koishi built atop the former two.

**Evaluation — what was actually measured.** There is **no quantitative benchmark** (no latency/memory/throughput/downtime numbers for Cordis itself). The empirical content is:
- Two counted statistics about the VSCode Marketplace (§1.2.1, motivating example, not an evaluation of Cordis): among the top 100 extensions by install count, **87 contain executable code** (and thus require a full extension-host restart to remove) and **only 7 declare `extensionDependencies` on non-built-in extensions** (data retrieved June 9, 2026) — p.5.
- A **case study**, not a controlled experiment: **Koishi**, an open-source chatbot framework built on Cordis v3, "over four years of development... has accumulated over **4000 community-contributed plugins**" (p.69), used to argue qualitatively that Cordis (a) is expressive/general (same primitives power both a server-side bot and an independent browser-based web console), (b) gives temporal composability "without cognitive overhead" (plugins are disabled/HMR-reloaded live without hand-written uninstall code), and (c) gives spatial composability across independently authored plugins (IM adapters, DB drivers) that "coordinate on nothing beyond the coeffect that connects them."
- The paper's own **"Threats to validity"** paragraph (p.69) states plainly: evidence is from "a single ecosystem in a single host language," is "observational rather than a controlled comparison against an alternative architecture," and is "thus an existence-and-adoption result rather than a quantitative one; measuring the abstraction's overhead and its effect on developer productivity against a baseline remains future work."

**Discussion (§6) — self-scoped limitations, most load-bearing for downstream use:**
- §6.1 System Boundary: recovery is bounded to locations the system can exclusively modify and restore ("inside" the boundary); anything else (a datagram sent, bytes written to a shared file) is an **emission** that "acts as `idΓ`" and is neither tracked nor reverted; recoverable only by *withholding* (output-commit) or *application-supplied compensation*, whose correctness is **not** covered by the paper's metatheory ("The metatheory does not [transfer]: the commutation of Definition 65 is proved against ≃ and has to be re-established against the coarser one," p.71).
- §6.2 Service Multiplexing (broker pattern for multiple providers of one interface — load balancing, rolling updates, cross-process RPC).
- §6.3 Access Control and Sandboxing: declared coeffects give capability-style access control (undeclared access raises an error; the full capability set is statically known, "letting the orchestrator review and approve them at load time," p.72) — but this is a *design observation*, not something evaluated; and the paper is explicit that **sandboxing untrusted code needs a mechanism outside the language** (software fault isolation, a separate runtime, a sandboxed process, or a container) — p.72–73.
- §6.4 Language independence (what a host language must minimally supply: closures + introducible/retractable modules for temporal; typed DI + interposable access for spatial).
- §6.5 Mutual dependencies: a dependency cycle leaves both components permanently inactive (detectable statically, unlike scheduler-dependent deadlock), decomposable by finer-grained components at the cost of a potentially quadratic blow-up in integration components.
- §6.6 Dependency Typing and Versioning: an **explicitly open problem**. Key-identity-only linking creates "interface drift" and "key collision"; the paper discusses three partial mitigations (key namespacing, peer dependencies via semver — "an unenforceable convention," p.75 — and structural/behavioral-contract compatibility), and states structural compatibility via pre/postconditions or effect specifications is complex and "undecidable once parametric polymorphism introduces bounded quantification" (p.75), closing with: "Designing a unified dependency model that combines these approaches while preserving the dynamic composition guarantees of the coeffect model remains an open problem" (p.76).
- §6.7 sketches co-design opportunities with languages (implicit context, compiler-known effects/coeffects, compile-time cycle detection) and operating systems (OS-level sandboxing and resource-as-coeffect tracking, transactional/COW storage to make more operations revertible) — all future/speculative, not built.

**Related work (§7)** positions Cordis against monadic effect libraries (ZIO/Effect-TS/fp-ts), Effekt's capability-passing algebraic effects, Heunen et al.'s categorical reversible effects, Orchard et al.'s graded effects/coeffects (Granule), context-oriented programming, aspect-oriented programming, dynamic software updating (Kitsune, Erlang/OTP, webpack/Vite HMR), developer-authored recovery (OSGi/Eclipse/VSCode callbacks, Command pattern, sagas, React `useEffect`), statically-scoped reversal (STM, reversible process calculi, linear types/RAII, Kim & Rinard's verified commutativity/inverses for data structures), interposed reclamation (Nooks, shadow drivers, Akeso), and availability-reactive component models (OSGi Declarative Services, iPOJO/Gravity, R-OSGi) and FRP/signals.

**Conclusion (§8).** Restates the contributions and explicitly flags **self-evolving agent harnesses as future validation work, not something demonstrated**: "a compelling direction for future validation is self-evolving agent harnesses (Section 1.2.2), where an AI agent generates and replaces its own harness components continuously and with little human oversight. Applying Cordis in such a setting would validate the temporal guarantees... as well as the spatial guarantees..." (p.82, emphasis on *would* — conditional/future).

---

## 3. Claims table

| # | Claim (as given) | Exact passage | Page | Verdict |
|---|---|---|---|---|
| a | Temporal composability: upon removal, a component's modifications to the shared environment are completely and safely reversed. | "Temporal composability addresses the time dimension: upon removal of a component, the modifications the component made to the shared environment must be completely and safely reversed. This requires tracking every resource allocation, event registration, and state mutation the component performs, and guaranteeing their orderly reclamation upon removal." | **4** (§1.1) | **Correct as the paper's own stated definition** — but **overstated if read as an unconditional guarantee**. The paper itself bounds "complete[ness]" twice: (i) all equalities of §3.1, including this one, are formally re-read "up to" an observational equivalence ≃ (§3.3.2, p.23–26; Lemma 38), so e.g. "a monotone allocator is not rewound, a heap's layout `free` does not restore, and a message already sent stays sent" (p.46, Thm 68 discussion); (ii) it only applies to locations reified inside the declared **system boundary** — an emission crossing that boundary "acts as `idΓ`" and "is therefore neither tracked nor reverted" (§6.1, p.70–71). So the correct wording is: *upon removal, a component's modifications to locations it has reified as effects/coeffects inside the system boundary are reversed up to the observational equivalence those locations' own operations induce* — not literal, unconditional, universal reversal. |
| b | Spatial composability: components declare, discover and resolve dependencies on one another; lifecycles are coordinated on dependency change. | "Spatial composability addresses the space dimension: components must be able to declare, discover, and resolve their dependencies on one another in a structured and verifiable manner. This requires managing dependency topology and coordinating component lifecycles in response to dependency changes." | **4** (§1.1) | **Correct.** This is the paper's own definition and is formalized without material qualification in §3.2 (coeffect specification/`notify_d`, p.16–19) and proved in global form as Theorem 70 "Ordering" (§4.3.3, p.47–48). |
| c | Reversion holds only inside a system boundary; an emission (bytes written to a shared file, a datagram sent) acts as identity and is neither tracked nor reverted (§6.1). | "The boundary divides the environment a system runs against into two parts. (1) A location lies inside when the system is able to modify it exclusively and to restore the state before that modification... (2) A location lies outside when either ability fails, so an operation on it acts as idΓ and is therefore neither tracked nor reverted." / "...as with the bytes a write hands to the file or the datagram a send puts on the wire, and the push acts as idΓ, leaving the data where other parties may read and write it. The two stages therefore fall on opposite sides of the boundary: the acquisition stays inside it, whereas the emission crosses to the outside." | **70–71** (§6.1) | **Correct**, verbatim match. |
| d | Recovery from an emission is by withholding it (output commit) or by compensation, which restores state only up to an application-supplied equivalence; compensations compose in LIFO order but the metatheory (commutation) does not transfer and must be re-established. | "A system that must nonetheless recover from an emission has two approaches available. One is to withhold an emission until the state that produced it is certain to persist, which is the output commit problem of rollback-recovery. The other is compensation: an action that restores the state up to an equivalence the application supplies, coarser than the ≃ of Definition 33... Such actions compose in the same LIFO order as inverses do, so the composition of Section 3.1 transfers to them. The metatheory does not: the commutation of Definition 65 is proved against ≃ and has to be re-established against the coarser one." | **71** (§6.1) | **Correct**, verbatim match. |
| e | A component can only access dependencies it has declared; undeclared access raises an error; the complete set of capabilities is known before it runs, so an orchestrator can review them at load time (§6.3). | "...a component can only access dependencies it has declared; an undeclared access raises an error. This is structurally similar to capability-based security... The inject declaration acts as a capability request, and the context proxy acts as a capability mediator. Since these requests are declared statically, the complete set of proxy-mediated capabilities a component requires is known before it runs, letting the orchestrator review and approve them at load time rather than discovering accesses as they happen." | **72** (§6.3) | **Correct** as a description of the mechanism, matching the runtime check in Algorithm 6 (`resolve`, §5.1.4, p.64: throws `UNDECLARED_ACCESS`/`INACTIVE_ACCESS`). Caveat: this is a **design observation in the Discussion section**, not something the paper evaluates — no worked example of an orchestrator actually auditing a capability list is given, and the mechanism only covers access mediated through `ctx[key]`/the proxy; a component with a raw reference to the host runtime (e.g. via closures in an untrusted language embedding) is explicitly *not* covered — that is exactly claim (f). |
| f | Sandboxing untrusted code needs a mechanism outside the language (§6.3). | "When a component's code cannot be trusted, language-level access control is insufficient, since a malicious component with access to the host runtime can reach the underlying objects directly, rendering such checks moot. Sandboxing requires an execution boundary beyond the reach of language-level means, such as software fault isolation, a separate language runtime, a sandboxed process, or a virtualized container." | **72–73** (§6.3) | **Correct**, verbatim match (also stated at p.72: "Cordis supports the first through dependency declarations and interception; the second requires an external sandbox"). |
| g | Dependency compatibility by structural contracts (pre/postconditions, effect specifications) is an open problem; semantic versioning is an unenforceable convention (§6.6). | "...this approach has two limitations: (1) it depends on providers faithfully adhering to semantic versioning, which is an unenforceable convention..." / "...structural compatibility is straightforward for record types (width subtyping) but becomes complex for behavioral contracts (e.g., pre/postconditions, effect specifications), and undecidable once parametric polymorphism introduces bounded quantification." / "Designing a unified dependency model that combines these approaches while preserving the dynamic composition guarantees of the coeffect model remains an open problem." | **75–76** (§6.6) | **Correct**, verbatim match; this is the single most explicit "we do not solve this" statement in the paper and is directly relevant to any schema built on declared keys/dependencies. |
| h | A faulty self-modification can disable the very process needed to recover (§1.2.2). | "Without temporal composability, each self-modification forces a full restart that discards all process-local accumulated state; at such frequency the cumulative unavailability becomes substantial, and in-flight tasks are disrupted repeatedly; even worse, a faulty self-modification can disable the very process needed to recover." | **5** (§1.2.2) | **Correct as a paraphrase of a motivating claim**, but note its status: this is offered as a **motivating hypothetical** for why temporal composability would matter to self-evolving agent harnesses, not a scenario Cordis is shown to handle. The paper's own Conclusion (§8, p.82) lists exactly this setting — "self-evolving agent harnesses... where an AI agent generates and replaces its own harness components" — as **future validation work**, conditionally phrased ("Applying Cordis in such a setting **would** validate..."), confirming no such validation was performed. |
| i | Cordis composes components live inside a running process (hot module replacement), rather than between restarts. | "Hot module replacement (HMR) applies the revertible-effect pattern at the module level: when source files change, typically during development, the system replaces the affected modules in-place without restarting the process." | **67** (§5.2.2) | **Correct**, and corroborated as deployed practice in the Koishi case study: "an orchestrator disables a plugin from the console and its effects are reverted in place; during development, the HMR engine re-applies edited plugins on save while preserving cache state and live connections elsewhere in the system" (p.69, §5.3). Caveat: HMR still falls back to a **full restart** for modules in the "externals" set (declared not hot-replaceable, or caught in an unresolved import cycle default to `declined`, Algorithm 8, p.67–68) — so "rather than between restarts" is a matter of degree (most modules), not an absolute elimination of restarts. |

**Overall:** no claim above is flatly **wrong**. Claim (a) is the one genuinely **overstated** if quoted without its own paper's qualifiers (bounded by ≃ and by the system boundary). Claims (e) and (h) are accurate paraphrases but describe **discussion-section design goals / motivating hypotheticals**, not validated results — worth flagging distinctly from claims (b)(c)(d)(f)(g)(i), which are all either formally proved (b) or stated as direct, unqualified prose in the Discussion section (c, d, f, g, i).

---

## 4. What the paper does NOT claim or support (own limits) — relevant to using it as motivation for a schema of declared effects/dependencies for agent capabilities

1. **No quantitative evaluation of Cordis at all.** No benchmarked overhead, latency, memory, correctness-under-fault, or downtime-avoided numbers. The only empirical content is a single-ecosystem, single-host-language, observational case study (Koishi, TypeScript, ≥4000 plugins) that the paper itself calls "an existence-and-adoption result rather than a quantitative one" (p.69) and explicitly separates from "the merits of the paradigm... versus its TypeScript realization." **A schema motivated by this paper should not cite it as evidence of measured performance, reliability, or scalability of declared-effect/coeffect tracking — only as an existence proof that such a system can be built and adopted.**

2. **The core correctness guarantees rest on unverified, author-supplied proof obligations.** The runtime does *not* check (i) that a supplied inverse actually reverts the effect it accompanies, or (ii) that two operations of a shared key actually commute — both are explicitly "an obligation on the component author rather than a property the runtime verifies" (§5.1.1, p.58–59). All of §4.3's metatheory (recovery exactness, ordering, confluence) is conditioned on these witnesses being honest. **For an agent-capability schema, this means "declared effects/dependencies" alone do not give you soundness — you additionally need either (a) a way to verify inverse/commutativity claims, or (b) to treat them as trusted developer assertions, which is a materially weaker guarantee than "the schema enforces safety."**

3. **Self-evolving agent harnesses — the use case closest to the reader's interest — are explicitly *not* evaluated.** §1.2.2 uses them only as motivation; §8 (Conclusion) lists applying Cordis to such harnesses as **future work**: "Applying Cordis in such a setting would validate the temporal guarantees of complete recovery under rapid component replacement, as well as the spatial guarantees of dependency coordination under frequent topological change" (p.82) — conditional, not demonstrated. **Any claim that Cordis (or a schema derived from it) already provides safe self-modification for agent harnesses goes beyond what this paper supports.**

4. **Dependency compatibility beyond key-identity is an explicitly open, unsolved problem** (§6.6, p.75–76): interface drift and key collision are named failure modes; semantic versioning is called "an unenforceable convention"; structural/behavioral compatibility checking is "undecidable" in general once parametric polymorphism is present. **A schema of declared effects/dependencies for agent capabilities that wants more than nominal key-matching (e.g., structural or semantic compatibility between a tool's declared effect and a consumer's expectation) has no solution to borrow from this paper — it is named as future work, not delivered.**

5. **Sandboxing / isolation from untrusted code is out of scope of the language-level mechanism** (§6.3, p.72–73): declared coeffects give access *control* (what a trusted-but-buggy component may reach) but not *isolation* (what a malicious component could reach by other means, e.g. closures over the host runtime). **If the schema is meant to constrain untrusted or adversarial agent-generated capabilities, Cordis's mechanism must be paired with an external sandbox — the paper is explicit that it does not supply one.**

6. **Recovery is bounded to the declared system boundary and is not literal state restoration.** Recovery equalities hold "up to" an application/key-chosen observational equivalence (§3.3.2), and anything not reified as a coeffect key is entirely outside the model and untouched by any guarantee (§3.3.1, p.21–22: "a location the system cannot reify as a coeffect lies outside the boundary of Section 6.1"). Real-world agent actions with external side effects (API calls, payments, messages sent, files written to shared/external locations) are **emissions**: not reverted, only optionally *compensated*, and compensation correctness is explicitly **not** covered by the proved metatheory — "the metatheory does not [transfer]... and has to be re-established" (p.71). **This directly contradicts using the paper as motivation for a schema that promises "safe reversal" of arbitrary agent-capability effects; only effects fully reified inside a declared boundary get the proved guarantees, and most interesting agent effects (tool calls with external consequences) are exactly the emission case the paper says it does not solve.**

7. **The metatheory's strong results (Progress, Confluence) are conditional on assumptions that must hold by construction and are not automatically checked**: the "precedence" relation `≺` must be acyclic (a component cannot, even transitively, depend on a key it itself provides — mutual dependencies must be manually decomposed, §6.5, potentially with quadratic blow-up in integration components), every component must be "total on its provision" (Definition 76, an activation that finishes must install every declared key), and the set of fiber names arising must be finite (no unbounded self-instantiation). None of these are enforced by the calculus itself; they are hypotheses of the theorems.

8. **The paper's stated threats to validity are self-identified, not merely inferred**: single ecosystem, single host language (TypeScript), observational rather than a controlled comparison against an alternative architecture (§5.3, p.69).

---

## 5. Figure / table candidates for an appendix

| Page | Label | What it shows |
|---|---|---|
| **34** | **Figure 1** — "The component lifecycle, with the empty node marking a fiber absent from the registry" | The four-state fiber lifecycle state machine (Inactive / Reloading / Active / Unloading) with the eight labeled transition edges (O-Insert, O-Remove, L-Begin, L-Iter, L-Divert, L-Finish, L-Leave, L-Unload); O-Retire is a self-loop at every node and is omitted from the drawing. This is the one true diagram in the paper (the text notes "Section 4.2 draws the four states as a state machine (Figure 1) and supplies the rules on its edges," p.31) and is the clearest single visual summary of the calculus's operational semantics — strong appendix candidate. |
| **39–40** | **Table 1** — "The rules as writes on the fiber n they act on, where step^t is that rule applied at n" | A 9-row table (one per rule: O-Insert, O-Retire, O-Remove, L-Begin, L-Iter, L-Finish, L-Divert, L-Leave, L-Unload) giving each rule's pre/post lifecycle state θ_n, its state map Ψ^t, and which control fields it edits. This is the load-bearing reference table used repeatedly throughout the metatheory proofs (§4.3.1–4.3.5) — useful as a compact appendix reference for how each rule behaves, though it is presented as prose/table rather than a figure. |
| **57–58** | **Table 2** — "Theory-to-implementation correspondence" | Maps every theoretical construct (Γ∞, 𝔈_Γ/ℑ_Γ, effect_Γ(e), Σ/Σ_iso/Σ_inter, get/set/isolate/intercept, fiber tuple ⟨d,p,e,π,σ,τ,θ⟩, O-Insert/O-Retire/etc.) to its Cordis/TypeScript runtime counterpart (ctx.effect, ctx.get/set, fiber.state, fiber.dispose, fiber.committed, ctx.use, refresh/unload Algorithms, etc.). Most useful appendix candidate if the goal is to show the paper's formalism actually cashes out into a concrete, implementable API — bridges the gap between §3–4 (theory) and §5 (implementation) in one place. |

No other figures (charts, diagrams, plots, screenshots) occur in the paper; all remaining visual content is inline mathematical notation, commutative-diagram-style equation layouts (e.g., the small triangle/square diagrams under Theorem 4, Theorem 14 — not captioned or numbered as figures), and the ten numbered Algorithms (1–10, pp. 59–68) which are pseudocode listings rather than figures per se, but are worth listing if the appendix wants implementation-level detail:
- Algorithm 1 (p.59) — Effect tracking (`execute`/`effect`)
- Algorithm 2 (p.60) — Coeffect operations (`get`/`set`)
- Algorithm 3 (p.61) — Reactive notification (`notify`)
- Algorithm 4 (p.62) — Component instantiation (`use`)
- Algorithm 5 (p.62–63) — Component lifecycle (`refresh`/`reload`/`unload`)
- Algorithm 6 (p.64) — Proxy-mediated context access (`resolve`)
- Algorithm 7 (p.66–67) — Isolation realm reassignment (`patch_isolation`)
- Algorithms 8–10 (p.67–68) — HMR module classification, stale-entry detection, transactional reload

---

## 6. ≤15-line summary (also returned to caller)

See SubagentHandback message.

---

# 2603.21019 — SkillProbe: security auditing of agent skills, declared versus implemented capability

**Read in full:** yes, all 16 pages, by the main agent on 2026-09-22 (earlier ledgers had it as abstract only).

## Summary
Three phases: a Gatekeeper (malicious patterns, CVE dependencies, reasonable declared permissions; one BLOCK vetoes),
an Alignment Detector comparing declared capability set D(s) with implemented set C(s) as ⟨Resource, Access⟩ pairs,
and a Flow Simulator matching output-risk and input-sensitivity tags against nine source-to-sink policies. Audit of
the top 2,500 ClawHub skills with one model (Nex-N1). kb: `kb/papers/2603.21019-skillprobe.md`.

## Ledger
| Number or claim | Paper | Page | Caveat |
|---|---|---|---|
| four-class alignment: match, over-declaration, under-declaration (shadow functions), mixed | | p8 | declared side extracted from prose by regex and a model |
| top 2,500 skills: 9.9% clean, 59.8% approved with minor findings, 30.4% conditional | | p11-12 | one audit model; "security quality", not task success |
| conditional share 20-35% across download tiers | | Fig. 5 p12 | popularity does not predict security |
| 499 skills with a confirmed risk link, 75,373 risk edges, high-risk subset one connected component | | p12-13 | only the nine predefined policies (p14) |
| top 20 skills: Sonnet 4.6 marked 45% conditional, GPT-5.2-Codex 5% | | Table 2 p10 | the verdict depends on the model |
| about 13% of 10,240 MCP servers have undocumented high-risk operations | Li et al. 2026, cited | p5 | secondary citation |
| no dynamic sandbox | | p14 | future work |

## Used for
Verify (declared versus observed effects; under-declaration rejected; over-declaration a finding; record and measure
the verifier), Remove (composition risk screened by set).

---

# 2504.07079 — SkillWeaver: web agents can self-improve by discovering and honing skills

**Read in full:** yes, all 40 pages including appendices, by the main agent on 2026-09-22. Fetched from arXiv into
`papers/`. Cited by the 2026-09-15 capsule report. kb: `kb/papers/2504.07079-skillweaver.md`.

## Summary
Propose, synthesise (practice judged by an LLM reward model, trajectory to a Playwright API), hone (model-generated
tests, debugging). Each API docstring carries a description, the prerequisite website state and a usage log. At use
time a selection module keeps relevant APIs and removes those whose preconditions do not hold.

## Ledger
| Number or claim | Paper | Page | Caveat |
|---|---|---|---|
| WebArena GPT-4o 22.6% to 29.8% average success (+32% relative) | 812 tasks, 160 iterations per site | Table 1 p7 | single runs, temperature 0.3 |
| GPT-4o-mini with GPT-4o's APIs 9.2% to 14.1% (+45% relative) | | Table 1 p7 | the abstract says "up to 54.3%"; we cite Table 1 |
| live websites 40.2% to 56.2% | four sites, 57 tasks | Table 2 p7 | judged manually |
| synthesised APIs match human APIs where API support is low or medium, worse where high | | Fig. 3 p8 | |
| selection removes APIs that do not satisfy preconditions | | p6 | preconditions are docstring prose |
| "called without an exception" counted as verified and was gamed by silencing exceptions | | App. D.2.1 p34 | the authors' own finding |
| no test data for skills needing real inputs | | App. D.2.2 p36 | |

## Used for
Improve (self-built libraries help; usage log as past performance, held outside the Declaration in CC), Pick
(precondition filter before use), Verify ("no exception" is not verification).
