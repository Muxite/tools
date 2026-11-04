# Read log: papers behind REPORT.md and SCHEMA-ALT.md

Each paper below was read end to end, every line of its text file, in the ordinary reading order. The reading was
split across reader agents, one or two papers each. Each reader returned the last page it reached, every number it
used with its page, and what the paper supports and does not support. Page numbers are the printed page numbers.
Files with `===== page N =====` markers use those markers instead. Where a reader could not render a PDF page to
check a number that appears only in a figure, the number is marked **figure-only** and is not used in the report.

`cap/` means `capsule-openjiuwen/papers/`. `tun/` means `tundle/ai4research/papers/`.

| # | arXiv | Short name | File | Last page / total |
|---|---|---|---|---|
| 1 | 2604.00392 | Beyond Task Completion | cap/2604.00392.txt | 12 / 12 |
| 2 | 2605.24050 | More Skills, Worse Agents? | cap/2605.24050.txt | 18 / 18 |
| 3 | 2608.01050 | Don't Offer What Can't Be Done | cap/2608.01050.txt | 7 / 7 |
| 4 | 2607.07436 | The Blind Curator | cap/2607.07436.txt | 17 / 17 |
| 5 | 2608.05810 | When Self-Evolution Backfires | cap/2608.05810.txt | 9 / 9 |
| 6 | 2605.19576 | Library Drift | cap/2605.19576.txt | 9 / 9 |
| 7 | 2607.02345 | SkillFuzz | cap/2607.02345.txt | 12 / 12 |
| 8 | 2609.16313 | Cognitive Admission Control | cap/2609.16313.txt | 15 / 15 |
| 9 | 2607.23332 | AllocBench | cap/2607.23332.txt | 24 / 24 |
| 10 | 2605.10990 | Skill Drift Is Contract Violation | cap/2605.10990.txt | 22 / 22 |
| 11 | 2606.07904 | Contract2Tool | tun/2606.07904 - Contract2Tool ….txt | 10 / 10 |
| 12 | 2505.22954 | Darwin Gödel Machine | cap/2505.22954.txt | 72 / 72 |
| 13 | 2510.23601 | Alita-G | cap/2510.23601.txt | 15 / 15 |
| 14 | 2604.01687 | CoEvoSkills | cap/2604.01687.txt (and PDF pp. 2, 7, 10, 16 rendered) | 23 / 23 |
| 15 | 2601.08815 | Agent Contracts | tun/2601.08815 - Agent Contracts.txt | 22 / 22 |
| 16 | 2602.22302 | Agent Behavioral Contracts | tun/2602.22302 - Agent Behavioral Contracts.txt | 71 / 71 |
| 17 | 2604.17870 | GraSP | cap/2604.17870.txt | 16 / 16 |
| 18 | 2606.03056 | SkillDAG | tun/2606.03056 - SkillDAG.txt | 19 / 19 |
| 19 | 2605.06365 | Execution lineage | tun/2605.06365 - Execution lineage DAG replay.txt | 16 / 16 |
| 20 | 2606.26924 | RelAIBuild | tun/2606.26924 - RelAIBuild deterministic control plane.txt | 45 / 45 |
| 21 | 2608.25512 | Cordis ("A Programming Paradigm for Spatiotemporal Composability") | cap/2608.25512.txt | 92 / 92 |

No other paper is cited.

---

## Numbers used, with pages

### 1. Beyond Task Completion (2604.00392)

**Setup.** One model: Claude Haiku 4.5, temperature 1.0 (p3). Three seeds × 8 sessions (p3). 99 tasks in the design;
the strict analysis uses 51 verified decisions (p2). Libraries live only within a session (p3).

- **Held-out conformance, all protocols** (Table 5, p5): 222 tools, mean conformance C = 0.018, silent rot 96.8%
  (215 of 222, abstract p1).
- **Per protocol** (tools, C, silent rot):
  - One-Shot: 119 tools, C = 0.000, 100.0%.
  - ToolMaker-style: 19 tools, C = 0.000, 100.0%.
  - CREATOR-style: 84 tools, C = 0.049, 91.7%.
- **Held-out suites** have 10–22 inputs (median 11) (p5).
- **Calibration** (p5): hand-written reference implementations score C = 1.00 on all 16 capability suites.
- **Task completion** (Table 3, p4): One-Shot 0.358, No-Evolution 0.337, CREATOR-style 0.287.
  - Creator − OneShot = −0.0710, BH-adjusted p = 0.133 (Table 4, p4). It does not survive correction.
- **Sonnet trace** (p6): `decode_abr_format` passed its own agent-written self-tests, and session task completion
  reached 0.95. On the held-out suite it scored C = 0.00.

### 2. More Skills, Worse Agents? (2605.24050)

**Setup.** Two models, one provider: Haiku 4.5 and Sonnet 4.6. 38 (task, model) pairs; 2,545 trajectories (p8).
Libraries of 52, 102 and 202 skills (p8).

- **Pooled drop at 202 skills** (Table 1, p9): Δ = 0.21 [0.15, 0.27] absolute pass rate.
  - Shadowing component Δshd = 0.14 [0.06, 0.26].
  - Context component Δctx = 0.07 [−0.13, 0.25], which is not distinguishable from zero.
- **At 102 skills** (Table 1, p9): Δ = 0.14 [0.09, 0.19].
- **By model at 202 skills** (Table 4, p14): Haiku 0.26 [0.20, 0.33], Sonnet 0.15 [0.06, 0.24].
- **Model sees** only a skill's name and description until it invokes the skill (p4).
- **Example** (p3): in mario-coin-counting the wrong skill was invoked in all 26 trajectories.
- **Share of trajectories invoking no skill** (Table 2, p9): 12.0% at the oracle-only library, 38.5% at 202 skills.

### 3. Don't Offer What Can't Be Done (2608.01050)

**Setup.** One production family of 10 skills at Wix. One window, Jun 9 – Jul 10, 2026. The model is unnamed.
One replay per conversation (p2–p6).

- **Traffic** (p1, p3): 756,641 messages; the semantic stage matched 174,927 (23.1%).
- **The gate** (p1, p5):
  - It removed 1,039,462 of 1,749,270 skill–message pairs (59.4%).
  - It removed 228,799,446 of 387,288,378 description tokens (59.1%).
- **Combined reduction** (p1, p5, p6): 90.5% versus exposing all 10 skills to every message.
- **Replay** (p1, p5, p6): in 78 of 1,000 risk-enriched conversations (7.8%) the model chose a skill the gate would
  have blocked. The paper says this must not be extrapolated.
- **Description size** (p4): 152–344 tokens per skill description.
- **Stated limits.**
  - The guarantee is one-sided (p3).
  - No false-block rate is measured (p5–6).
  - Fail-open versus fail-closed must be explicit (p5).

### 4. The Blind Curator (2607.07436)

**Setup.** The Ratchet loop. Three seeds × 12 rounds; τ = 0.10, Nmin = 24, cap 12 (Table 2, p12). Tiny eval sets:
28 and 23 tasks. Corruption is synthetic.

- **Retirement cliff** (p4; App. C, p13–14): contribution-based retirement can never fire once the false-pass rate
  ρF→P ≥ (1−τ)/2. That is 0.45 at τ = 0.10, "at any sample size".
- **True retirements** (Table 1, p6, REPORT-MAIN-71):
  - clean QC: 1.3 ± 1.2
  - bias q = 0.2: 0.0
  - bias q = 0.45: 0.3 ± 0.6
  - bias q = 0.7: 0.0
  - Cap evictions for those conditions: 8.7, 7.7, 3.3, 3.0.
- **Judge audit** (p5; App. E, p15): the real judge had ρF→P ≈ 0.01, ρP→F ≈ 0.95 and κ ≈ 0.04. It was strict, not
  lenient.
- **Deterministic QC recall** (p4–5): 1.0 on each QC-visible class; 0.0 on claim negation.

### 5. When Self-Evolution Backfires (2608.05810)

**Setup.** Terminal-Bench 2. One evolution backbone (Hy3); apparently a single evolution run. Five rounds, k = 3. The
main table is on the distillation split, which the paper calls "an optimistic upper bound" (p5). The holdout gate set
has 14 tasks (p5).

- **Main results** (Table 1, p6):
  - Ungated: peak 62% at R3 with a pool of 105 skills; 50% at R5 with a pool of 179.
  - VaG: 72% at R5 with a pool of 37.
- **Ablation** (Table 2, p6):
  - Without holdout replay: 62%, which is −10.
  - Without the marginal-gain gate: 64%, which is −8, and the pool grows to 58.
- **Rollback decomposition** (Fig. 4 text, p7):
  - Source-only rollback recovers 1.7 of the 12.3pp drop.
  - Oracle lineage cleanup recovers a further 5.0pp.
  - 5.6pp is unrecoverable.
- **Lineage cleanup** "requires provenance a real system lacks" (p2, p7).
- **Wilson CI bands** are about 30pp wide (p5).

### 6. Library Drift (2605.19576)

**Setup.** MBPP+ hard-100. One model (Claude Opus 4.7). 3 seeds × 100 rounds (p3–4). Self-stated narrow (p6).

- **Default** (Table 1, p5): gain +0.328 ± 0.018, from a baseline of 0.258 to a late mean of 0.584.
- **A4, harsh retirement** (Table 1, p5): gain −0.019 ± 0.010, with 2 active skills.
  - Nmin went from 100 to 20 and τ from 0.10 to 0.0, so two knobs changed, not one.
- **A7, cap 100** (Table 1, p5): gain +0.317 ± 0.110. The cap mainly controls variance.
- **Cost** (p5): about 14.5k LLM calls per 100 rounds, and 6.5h of wall time versus 2.3h without injection.

### 7. SkillFuzz (2607.02345)

**Setup.** One marketplace of 196 skills (SkillsBench), 10 tasks, 8 planners (p6). The same model (GPT-4o-mini)
extracts intents and judges (p6, p10). Contracts are extracted by an LLM from prose (p4). Seeds are not stated. RQ3
is one task × one agent (p7).

- **Contract extracted per skill** (p4): (P, Q, M, V, D, A, c). These are preconditions, postconditions, the modifies
  set, invariants, domain scope, action types and extraction confidence.
- **Seed conflict score** (p5): uses shared modifies-set entries and mutually exclusive invariants.
- **Implicit intents found** (Table I, p6; p9): 1,188 in total across 8 agents × 10 tasks, with B = 200.
- **Execution-time confirmation** (Table II, p7): 80.6% of the 98 highest-risk flagged co-activations.
- **Depth** (Fig. 6 text, p9): severe drift rises with co-activation depth, reaching 66.5% at k = 5.
- **Versus random search** (Table III, p8; one task, one agent): 90 high-severity intents versus 64.
- **Stated limits** (p10):
  - The thresholds are uncalibrated.
  - The judge may be biased.
  - The plan oracle cannot catch an agent that acts differently from its plan.
  - The screen must be re-run when skills are revised after admission.

### 8. Cognitive Admission Control (2609.16313)

**Setup.** A TypeScript prototype with no language model. 13 synthetic scenarios × 7 controllers × 30 seeds = 2,730
trials (p8–9). "Not production failure rates" (abstract).

- **Outcomes** (p5): PERMIT, DENY, DEFER, ESCALATE and ABORT. Discharge is ternary, and missing evidence is distinct
  from violated evidence (p4).
- **Harmful effects** (Table 2, p10):
  - CAC: 0 in 390 trials.
  - LivePolicy: 30.
  - AuthOnly: 180.
  - The paper says this "does not establish a general utility advantage over a competent live-policy check" (p10).
- **Ablations** (p10): removing guards, typed evidence or EFD each reintroduces 30 harmful outcomes in 30 trials.
- **Compensatory scalar scores** can bypass a required condition (Prop. 1; A.1).
- **Budget exhaustion** never yields a permit (Thm 2).

### 9. AllocBench (2607.23332)

**Setup.** One synthetic numeric environment with 24 seeds (p3, p9). The economic study is on Haiku only (p18).

- **First-sight commitment when real code is required** (Table 1, p6), at rungs R2 and R3:
  - Haiku: 99% and 100%.
  - Opus 4.8: 92% and 99%.
  - GPT-5.4-mini: 85% and 88%.
  - GPT-5.6 Sol: 39% and 100%.
- **Abstract framing** (Table 1, p6), rung R0 (the "abstract" setting; R1 is "declarative"): 28%, 4%, 15% and
  24%.
- **Theory** (App. A.1, p12): under the benchmark's own distribution, committing at the second occurrence scores 43.0
  points per stream versus 34.6 at first sight.
- **Recommendation** (p8): separate the decision to invest from the act of building. This was not tested.

### 10. Skill Drift Is Contract Violation (2605.10990)

**Setup.** DriftBench has 880 pairs. The controlled drifts are LLM-generated. The open-world study covers 49 skills
(p3–4, p8).

- **False positives** (p7): 0 of 599 negatives, Wilson 95% CI [0%, 0.6%].
- **Best detection recall** (Table 2, p7): 76% [62%, 88%] with Qwen3.6-Plus, precision 100%.
- **Open-world, pre-registered** (p8): 12 true positives, 2 false positives, 10 false negatives; 55% recall.
- **Repair** (Table 14, p19):
  - Localised by failed contracts: 25 of 32 (78%).
  - No localisation: 2 of 20 (10%).
  - Plain drift text: 12 of 20 (60%), p = 0.213 versus contracts, so the difference is not significant.
- **Operational versus incidental.** Deciding whether a mention is operational before probing it avoids false alarms
  (p5–6).

### 11. Contract2Tool (2606.07904)

**Setup.** A synthetic registry of 100 tools with mocked execution and a fixed vocabulary (p5). No confidence
intervals are given, and run counts are not stated.

- **Downstream, four agent models** (Table V, p8):
  - Learned-contract filter: success 0.980, 2,528 tokens.
  - Gold-contract filter: success 0.990.
  - All tools exposed: success 0.775, 26,172 tokens.
- **Filter oracle** (Table IV, p8): with docs or schema alone, the needed next tool is hidden in 7.8% of steps.
- **Risk label accuracy** (Table III, p7): 0.63–0.67 on static evidence.
- **Stated limit** (p9): learned contracts are "not an unchecked replacement for safety review".

### 12. Darwin Gödel Machine (2505.22954)

**Setup.** One SWE-bench run; three runs on Polyglot only (p26). The hallucination study scores each agent on 3 tasks
(p69–70).

- **SWE-bench** (abstract): from 20.0% to 50.0%.
- **Polyglot, full benchmark**: from 14.2% to 30.7%.
- **Node 114** (p70–71): scored 2.0 on the hallucination objective after removing the special-token logging that the
  checker read. It did this "despite instructions not to change the special tokens". Hiding the checking functions
  reduced this kind of hacking but did not prevent it (p70).
- **Fixed parts** (p4–5): the exploration loop and parent selection are "fixed and not modifiable by the DGM".
- **Proposed safeguard** (p9): "an unmodifiable part of the system to be able to evaluate at halt the rest".
- **Cost** (p32): about USD 22,000 per SWE-bench run.

### 13. Alita-G (2510.23601)

**Setup.** The MCP box is harvested from the same GAIA validation set it is scored on (p9–10). One run per
configuration. No confidence intervals.

- **GAIA pass@1** (Table 1, p7): 83.03% with the 3× box, versus 75.15% for the original.
- **Tokens** (p8): 10,394 versus 12,305.
- **Admission** (p5): an MCP is kept only if its parent run succeeded. The abstracted MCP is not re-tested.
- **Redundancy** (Table 4, p9): 128 MCPs but 65 clusters at iteration 5. Accuracy is flat after 74 MCPs.

### 14. CoEvoSkills (2604.01687)

**Setup.** SkillsBench, 85 tasks. Skills are evolved per task and evaluated on the same task (p19, p21). The hidden
oracle takes part in the loop (Alg. 1, p5). Ablations are single runs.

- **Pass rate** (Fig. 4, p7, read from the rendered PDF): CoEvoSkills 71.1%, human-curated 53.5%, no-skill 30.6%.
- **Ablation** (Table A1, p14): without the surrogate verifier, 41.1%, which is −30.0.
- **Oracle use** (p15): about 40% of iterations are resolved by the surrogate verifier alone.
- **Verifier isolation** (p3–5): the verifier sees the instruction, the inputs and the output artifacts. It never sees
  the skill source.
- **Stated limit** (p17): the surrogate verifier "cannot distinguish its own estimation error from the agent's error".

### 15. Agent Contracts (2601.08815)

**Setup.** One model family (Gemini 2.5 Flash / Flash-Lite). Small n (p14–16).

- **Code review, n = 70** (p15): tokens −90% (34,606 → 3,461), p = 0.0007. Success 60.0% → 52.9%, which is not
  significant. The budget, the iteration cap and the prompting changed together.
- **Overshoot** (p16): a runaway agent was detected and halted after consuming 56K against a 40K budget.
- **Stated limit** (p12): "contracts cannot prevent a single expensive call from exceeding budget".

### 16. Agent Behavioral Contracts (2602.22302)

**Setup.** One task domain. The judge (GPT-4o-mini) is also one of the models under test. Seed 42. Code is not public
(p20, p30–33).

- **Contract** (p8): C = (P, I_hard, I_soft, G_hard, G_soft, R).
- **Composition conditions** (p17–18): C1–C5.
- **Declarations** are validated by JSON Schema and are deliberately not Turing-complete (p22, p24).
- **Hard compliance** (Table 9, p35): mean 0.973 contracted versus 0.961 uncontracted.
- **Overhead** (p46): under 10 ms per action at k = 12 constraints.

Only the structure (the contract tuple and C1–C4) is used in the report. The reader found the empirical headline
internally inconsistent (p29–35 and p43–44), so it is not cited as evidence.

### 17. GraSP (2604.17870)

**Setup.** Text simulators. The size and origin of the skill library are not stated. The average is over 3 runs, with
no variance reported (p6).

- **Margin** (p5): +6.9 points over the strongest baseline in each cell; 48 of 48 cells won.
- **Uneven margins.** InterCode wins are 0.5–1.1 points for 7 of 8 models (Table 1, p6).
- **Ablation** (Table 2, p7): DAG compilation adds +1.9 on ALFWorld seen.
- **Preconditions and effects** are written by an LLM at compile time, not declared by skill authors (p4, p15–16).
- **Substitution rule** (p4): a replacement's effects must cover downstream requirements.

### 18. SkillDAG (2606.03056)

**Setup.** Baseline rewards are quoted from another paper, not re-run (p8). No seeds or variance.

- **Reward with MiniMax** (Table 1, p7): SkillsBench 27.3 versus 18.7 for GoS; ALFWorld 67.1 versus 54.3.
- **Reward with codex** (Table 1, p7): a tie on ALFWorld, 93.6 versus 93.6.
- **Conflict edges** (p5–6, p17–19) are defined as online-only, are committed on a single observation, and carry no
  quantitative evidence. The paper names single-observation commit as an open risk (p11).

### 19. Execution lineage (2605.06365)

**Setup.** Two tasks in one domain, one model (GPT-5.2, T = 0.7), n = 3 (p10, p13).

- **Unrelated-branch update** (Table 1, p10):
  - DAG replay preserved the final memo exactly in 3 of 3 runs.
  - Loop arms regenerated it in 3 of 3; contamination was 0.667 and 1.000.
  - Input tokens: 382 versus about 11,655.
- **Step identity** (p6, eq. 4): k_v = h(σ_v, x_v, {k_u}).
- **Design rule** (p5): a node must not consume undeclared upstream state.

### 20. RelAIBuild (2606.26924)

**Setup.** Conformance tests on constructed violations, plus a prevalence study. The author states there is no
outcome evidence (p4, p27–28, p35).

- **Commit depth** (Table 11, p30-31): 58.45% of 6,145 agent config files have exactly one commit.
- **Declared permissions** (Table 10, p29–30): 31 of 6,145 agent config files (0.5%) declare explicit permission
  scopes, versus 33.39% of CI/CD workflows.
- **Hash of the canonical definition** (Lemma 2, p39): the hash is taken over the canonical definition, not over its
  compiled forms.
- **Enforcement gap** (p22): four of seven harness targets have no tool-level enforcement.
- **Self-reported traces** (p20–21) are detect-only.

### 21. Cordis (2608.25512)

**Setup.** One ecosystem (Koishi) and one language. There are no performance measurements (p70).

- **The term "hyper-plugin" does not appear in the paper.** The formal unit is the *component* (Def 48, p31). "Koishi
  uses the term plugin for the concept this paper formalizes as component" (footnote 5, p69).
- **Component** (Def 48, p31): the triple (d, p, e), meaning coeffect specification, provision and effect iterator.
- **Two-step unload** (p36; Alg. 5, p62–63): stop providing, then dispose only when no dependent still relies on the
  capsule.
- **Recovery exactness** (Thm 68, p46), **Ordering** (Thm 70, p47) and **Confluence** (Thm 80, p54).
- **Limits.**
  - Emissions are not reverted: "a message already sent stays sent" (p47; §6.1, p70–71).
  - Inverse correctness is the author's obligation and is not verified (p59).
  - There is no versioning or structural typing of keys (§6.6, p75).
  - Dependency cycles leave components inactive (p74).
  - No sandboxing (p73).
- **Scale** (p69): Koishi has more than 4,000 community plugins over four years.
- **VSCode** (p5): 87 of the top 100 extensions contain executable code; 7 declare `extensionDependencies`.
