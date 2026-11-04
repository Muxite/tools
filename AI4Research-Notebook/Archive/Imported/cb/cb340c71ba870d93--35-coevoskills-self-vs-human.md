# 35 — CoEvoSkills: self-built vs human-curated, precisely

Written 2026-09-10 by the capability-capsule panel (pts/9).
**[verified]** against `/home/muk/work/papers/2604.01687.txt`; line numbers that
file's. Benchmark: SkillsBench, Claude Opus 4.6 with Claude Code.

⚠ **This note corrects notes `17-` §2.5 and `28-`.** Both record "agent-created
skills beat human-curated ones." **Stated bare, that is contradicted by the
paper's own baselines** — and the correct version is far better for us.

---

## 1. The full ladder, not the two endpoints

Fig. 4, §4.2 (lines 524-530) [verified]:

| Condition | Pass rate |
|---|---|
| No skills | **30.6%** |
| CoT-guided self-generation (structured 5-step prompt) | 30.7% (±5.2) |
| SkillsBench self-generated baseline | 32.0% (±3.1) |
| Anthropic's naive Skill-Creator | 34.1% |
| **Human-curated skills** | **53.5%** |
| **CoEvoSkills** | **71.1%** |

CoEvoSkills beats no-skill by **+40.5pp** and human-curated by **+17.6pp**.

**But look at rows 2-4.** Three separate self-generation approaches — including
Anthropic's own skill-creator and a deliberately structured chain-of-thought
variant — land at **30.7%, 32.0% and 34.1%**, against a no-skill baseline of
**30.6%**.

> **Unverified self-generation is worth approximately nothing, and it is roughly
> twenty points *worse* than human curation.**

The paper's own conclusion (lines 530-533):

> *"This confirms that skill generation without co-evolutionary verification is
> insufficient **regardless of the generation strategy**: the gains of
> CoEvoSkills originate from the **iterative verification loop, not from the
> skill-creation prompt itself**."*

## 2. The correction, and why it helps

| Don't say | Say |
|---|---|
| "Agents write better skills than humans" | **"Agents *with a verification loop* write better skills than humans. Agents without one write skills worth about as much as no skills at all."** |

The paper's own "Takeaway 1" is headlined *"Agents can create better skills than
humans"* — so the loose reading has a quotable source. **Do not lean on it.** A
supervisor who reads §4.2 will find the three baselines immediately, and the
narrower claim is the one that survives.

**And the narrower claim is the stronger one for this project.** It says the
entire value of self-generation is contributed by verification. That is our
thesis, measured, from the positive direction — and it pairs exactly with
2604.00392 (`29-`) measuring the same thing from the negative direction:

> Unverified generation produces artifacts that are **broken** (96.8% at C=0.00)
> and **worthless** (30.7-34.1% vs a 30.6% baseline). Add verification and the
> same generators produce artifacts that **beat human experts** (71.1% vs 53.5%).

Two independent papers, opposite methods, one conclusion: **the verification
loop is the product.** This is the best single pairing of citations available to
the report.

## 3. How long verification takes to pay off

Fig. 2, §4.5 (lines 674-683) [verified] — pass rate by evolution round:

| Round | Pass rate | Note |
|---|---|---|
| 0 (one-shot, no verification) | *(no figure stated)* | **on par with no-skill baseline** — ⚠ the ≈30.6% here before 2026-09-11 was our inference; the paper states only "on par", and Fig. 2 plots ~32% |
| 2 | 44% | still below human-curated |
| 3 | **63%** | **overtakes human-curated (53.5%)** |
| 5 | 75% | converged |

**It takes three rounds of verification to beat a human.** Round 0 — which is
what every "let the agent write a skill" implementation actually does — is worth
nothing.

⚠ **A discrepancy to be careful with:** §4.2 reports the headline as **71.1%**
while §4.5 says the curve converges "at 75% by round 5". Likely different
measurement scopes (aggregate figure vs. the traced dynamics). **Cite 71.1% as
the headline** and do not present 75% as the same quantity.

**Cost, and it belongs in `33-`** (lines 681-683): each task requires on average
**4.1 verification cycles and 2.4 Ground Truth Oracle rounds** to converge. That
is a real, published per-capability verification cost, and the paper notes
"convergence within five rounds keeps the evolution cost practical."

## 4. Where human curation wins, and where it actively hurts

§4.4, Fig. 6 (lines 618-623) [verified]:

- Self-evolved beat human-curated in **9 of 11 domains**.
- Largest margins: **Finance +56.9pp**, **Cybersecurity +23.2pp**.
- The pattern is **non-uniform**: domains where human curation already works well
  (**Energy, Robotics**) see diminishing returns from evolution; domains where
  human curation adds little see the largest gains.
- **In Natural Science, human-curated skills *degrade* performance** relative to
  no skills at all, while self-evolved skills improve it (lines 661-663).

Takeaway 3, verbatim (lines 666-670):

> *"Human-curated skills can actively degrade agent performance in certain
> domains; co-evolutionary optimization bridges this gap by discovering
> procedures aligned with how LLM agents actually reason."*

**Two of eleven domains is not nothing.** The honest reading is that human
curation is *unreliable*, not that it is bad — which matches the SkillsBench
finding the paper opens with (line 83): human-curated skills "yield **highly
uneven** gains."

## 5. The most useful part: what the artifacts actually look like

Appendix C, Table C3 (lines 1176-1194) [verified] — exoplanet transit detection:

| | **Human-curated** | **Self-evolved** |
|---|---|---|
| Size | **1,096 lines across 5 `SKILL.md`** | **64 lines `SKILL.md` + 142 lines Python** |
| Executable code | **None — documentation only** | **9 callable functions** |
| Algorithm guidance | lists BLS, TLS, Lomb-Scargle **equally** | **prescribes TLS, with justification** |
| Period refinement | 2-line tip: "refine candidates" | two-stage search: broad, then ±2% narrow |
| Alias detection | "check for aliasing" — one sentence | a function testing P, 2P, P/2 automatically |
| Precision handling | **not addressed** | enforces 5-decimal output formatting |

**5 skills and 1,096 lines of prose became 1 skill and 206 total lines that
performs better.**

And the patterns were *earned*, not written (lines 1196-1202): the two-stage
period search "emerged after Versions 2 and 3 both failed at 75%"; the sigma-clip
ordering became "a hard pipeline constraint with an explicit 3σ threshold, after
the agent learned that 2σ clips" were insufficient.

> **Humans wrote a comprehensive, neutral manual. The agent wrote an opinionated,
> executable contract — and every opinion in it was paid for by a failure.**

### Why this matters more than the headline number

This is the finding to put in the report, because it describes **exactly what a
capsule is**:

- **Prescriptive, not enumerative.** The human doc lists three algorithms
  neutrally; the evolved skill commits to one and justifies it. A contract picks.
- **Executable, not descriptive.** Nine callable functions versus zero — the
  artifact *is* the capability, not advice about it.
- **Edge cases as enforced constraints.** "Check for aliasing" becomes a function
  that tests P, 2P and P/2. A passing mention becomes a machine-checked
  invariant. This is precisely the move from documentation to contract.
- **Failures encoded as structure.** A 3σ threshold exists because 2σ failed.

**The self-evolved artifact converged on the shape of a capsule manifest without
being asked to.** That is convergence evidence of the kind `28-` §5 catalogues,
and it is the strongest available answer to "why should a capability declare
anything?" — because when a verification loop is allowed to shape an artifact,
declaration is what it produces.

## 6. Corrections to apply

- `17-` §2.5 — "agent-created skills beat human-curated ones" ⇒ add the
  verification qualifier and the three baselines.
- `28-` §2 headline row and §4 — same.
- `33-` §1 — add the 4.1 verification cycles / 2.4 oracle rounds figure; and
  §3's ladder now has empirical grounding: **rung 2 (unverified tool) ≈ the
  no-skill baseline; rungs 3-4 (verified) = 71.1%.** The ladder is a step
  function in value, not just a cost gradient.

## 7. One limit the paper states about itself

*"CoEvoSkills evolves skills from task-relevant background knowledge available
at initialization. A natural extension is **open-world** skill evolution."* —
⚠ corrected 2026-09-11: the bracketed "[ended]" invented the wrong word.
"Open-world" is a named research setting the paper cites OpenSkill for. —
so this is refinement within a known task family, **not open-ended discovery of
capabilities nobody specified.** Worth knowing before citing it as evidence that
agents can build arbitrary capabilities: they were told what to build.
