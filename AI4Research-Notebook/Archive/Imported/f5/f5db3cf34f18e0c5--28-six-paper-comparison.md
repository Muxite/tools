# 28 — Six systems compared: sentiment, features, and what to steal from each

Written 2026-09-10 by the capability-capsule panel (pts/9).
All six read this session at abstract + mechanism + results depth. Claims are
**[verified]** against the local `pdftotext` extractions in
`/home/muk/work/papers/`; line numbers are those files'.

⚠ The "don't spoil the papers" rule (HANDOFF §3.4) is **lifted for these six** —
the user asked for this comparison directly.

Purpose: they overlap and are not the same. Each contributes a distinct trait,
and the report should cite all six for different jobs.

---

## 1. One line each

| Paper | arXiv | The one-sentence version |
|---|---|---|
| **Alita-G** | 2510.23601 | Harvest MCP tools from successful trajectories, LLM-abstract them into a Box, retrieve by cosine similarity. *Generalist → domain expert.* |
| **SkillWeaver** | 2504.07079 | Propose skills, **practise** them, then **hone** them with auto-generated unit tests until they are robust APIs. *Practice makes reusable.* |
| **CoEvoSkills** | 2604.01687 | Generate multi-file **skill packages**, verified by an informationally-isolated **surrogate verifier that co-evolves** with the generator. *Verification without ground truth.* |
| **SkillDAG** | 2606.03056 | Model inter-skill relations as a **typed DAG** the agent queries and edits at run time, with structural checks on every commit. *Selection is structural, not similarity.* |
| **DGM** | 2505.22954 | An archive of coding agents that **rewrite their own code**, validated empirically on benchmarks. *Open-ended self-improvement.* |
| **Survey** | 2507.21046 | The field's taxonomy — what / when / how / where to evolve — plus evaluation paradigms and the open safety problems. *The vocabulary.* |

## 2. The comparison table

This is the table to adapt for the report. Every cell is from the paper.

| | **Alita-G** | **SkillWeaver** | **CoEvoSkills** | **SkillDAG** | **DGM** |
|---|---|---|---|---|---|
| **Unit of capability** | MCP tool (single function) | Web API function | **Multi-file skill package** | Skill (id + applicability + body) | The agent's own source code |
| **What evolves** (survey axis) | Tools | Tools | Tools | **Tools + the relations between them** | **Architecture** |
| **Admission signal** | **Task outcome only** (Eq. 5) | Reward model judges the practice trajectory | **Surrogate test assertions**, then a ground-truth oracle | Evidence-backed edge proposal | **Benchmark score** |
| **Artifact-level verification** | **None** | **Yes** — auto-generated unit tests + debug loop (Stage III) | **Yes** — deterministic test assertions from a separate session | Structural checks, not behavioural | Benchmark only |
| **Library management** | **None**, explicitly declined (§3.3) | Iterative refinement of individual APIs | Iterative refinement across 5 rounds | **Yes** — five typed edge types incl. `conflicts_with`, dedupe via `similar_to` | Archive of all **viable** agents — children that fail to compile or lose editing ability are **discarded** (⚠ corrected 2026-09-11) |
| **Selection mechanism** | Cosine similarity, threshold τ | Library lookup | — | **Typed graph traversal + conflict exclusion** | Parent sampling from archive |
| **Reversibility** | None | None | None | **Append-only log with rollback** | Archive = lineage, no rollback |
| **What is frozen** | everything except the Box | the harness | the oracle | the structural invariants | **archive maintenance + parent selection** (line 295) |
| **Headline result** | GAIA 83.03 pass@1, −15% tokens | WebArena +31.8% **relative** (22.6→29.8 = +7.2pp), real sites +39.8% relative, weak-agent transfer +54.3% **relative** (9.2→14.1 = +4.9pp) | **71.1% vs 53.5% human-curated** — but unverified self-generation scores 30.7-34.1% against a 30.6% baseline (`35-`) | ALFWorld/SkillsBench 67.1% success, +12.8 over best baseline; Ret@K 65.5 → 78.2 | SWE-bench 20.0 → 50.0, Polyglot 14.2 → 30.7 |

## 3. Overall sentiment — where each sits on the spectrum

Ordered by **how much they trust the artifact they produced**, least to most
paranoid. This ordering is the report's most useful framing device.

1. **DGM — maximal ambition, minimal artifact scrutiny.** It changes the most
   (its own code) and checks the least about *how* — a benchmark score is the
   whole gate. Candid about the risk: modifications "optimized solely for
   benchmark performance might inadvertently introduce vulnerabilities or
   behaviors misaligned with human intentions, even if they improve the target
   metric" (lines 614-616).
2. **Alita-G — maximal pragmatism.** Cheapest possible curation (did the task
   succeed), no artifact check, no lifecycle, strong results. Optimised for a
   fixed distribution.
3. **SkillWeaver — practice-based confidence.** Adds a genuine artifact loop:
   synthesise, generate test cases, execute, debug, repeat. Verification is
   LLM-judged but it *is* artifact-level.
   ⚠ **Corrected 2026-09-11.** This bullet previously cited SkillWeaver as
   "honest about the ceiling: these artifacts still *'pose challenges for formal
   verification and precise composition'*". That sentence is SkillWeaver
   describing **Agent Workflow Memory and ICAL** — prior work it criticises to
   motivate its own structured APIs — not a self-assessment. Same failure mode
   as the original incident: a paper's characterisation of someone else's work,
   read back as its own admission. SkillWeaver states no such limit.
4. **CoEvoSkills — adversarial-ish verification.** The Surrogate Verifier is "a
   separate LLM session without inheriting the generator's biases" (lines
   137-139) that synthesises deterministic assertions from task instructions,
   inputs and produced artifacts. Closest in spirit to a conformance gate.
5. **SkillDAG — structural paranoia.** Doesn't verify behaviour at all; instead
   constrains *relations*, and refuses commits that break acyclicity or
   non-contradiction. The only one of the six with reversibility.

**Nobody in this set checks declared effects.** That gap is consistent across
all six and is the capsule contribution.

## 4. The trait to steal from each

| From | Steal | Why |
|---|---|---|
| **Alita-G** | The **loop shape** — gap → build → abstract → curate → reuse — and the measured evidence of library rot | It proves the loop works and shows exactly where it stops scaling (`27-`) |
| **SkillWeaver** | **Practice before admission.** Do not admit on first synthesis; execute the candidate against generated cases and debug first | Turns admission from a static check into an earned status. Maps directly onto `draft` → `stable` promotion (`19-`) |
| **SkillWeaver** | **Capability transfer**: strong-agent APIs lift weaker agents up to +54.3% **relative** (GPT-4o-mini 9.2 → 14.1 = +4.9pp — ⚠ not percentage points) | The argument that a capsule library is an asset independent of the model that made it — supports provider-neutrality |
| **CoEvoSkills** | **Informational isolation of the verifier** — a separate session that does not inherit the generator's biases | The practical, buildable version of "the referee is not the actor". Cheaper than our immutability rule and complementary to it |
| **CoEvoSkills** | ⚠ **The ablation, not the headline** (`35-`): unverified self-generation lands at the no-skill baseline; three rounds of verification are needed to overtake humans | **The verification loop is the entire delta.** Best positive-direction evidence for the whole thesis |
| **CoEvoSkills** | Skills as **multi-file packages**, not single functions | A capsule already bundles spec + implementation + verification; this is independent confirmation that the unit should be a package |
| **SkillDAG** | **Typed relations as first-class**: `depends_on`, `specializes`, `similar_to`, `conflicts_with`, `composes_with` (five types — ⚠ the fifth was missing before 2026-09-11) | `conflicts_with` ≈ our `operator_compatibility.forbidden`; `depends_on` ≈ `composition.consumes`. Their `similar_to` is the dedupe signal Alita-G measured and never wired up |
| **SkillDAG** | **Propose-then-commit with structural invariants + append-only rollback** | This is an admission gate for *relations*. Nearest existing analogue to the capsule gate, and it is reversible |
| **DGM** | **Archive as lineage** — "a traceable lineage of modifications" (⚠ not "every version retained") | Provenance and rollback, which `17-` §5.4 requires and the repo lacks (`13-` Q5) |
| **Survey** | The **taxonomy** and the three evaluation horizons | Structures the report and signals literacy |

## 5. Four independent convergences

Convergence across independently designed systems is evidence the abstraction is
real. These are stronger arguments than any feature table.

1. **Similarity alone is insufficient for selection.** SkillDAG states it
   outright — "selecting the right subset becomes a **structural problem rather
   than a similarity-matching one**" — and Alita-G's Tables 3 and 5 demonstrate
   it from the other direction (16-point swing across τ, 12 across encoders).
   **Two papers, opposite methods, same conclusion.** This is the strongest
   available support for the stage-0 typed filter (`23-` §4).
2. **The artifact needs its own check, separate from the task.** SkillWeaver
   (unit tests), CoEvoSkills (surrogate assertions), 2604.00392 (the measured
   gap) all say it. Alita-G and DGM are the two that don't, and both are the
   ones curating on outcome.
3. **Verification must not inherit the generator's biases.** CoEvoSkills builds
   this in; DGM names its absence as a risk; our design takes the strongest form
   (a mechanical, immutable referee — `25-` §3, `26-` §4 T5).
4. **Libraries need structure once they are large.** SkillDAG's whole premise;
   Alita-G's Table 4 measures the cost of not having it.

## 6. ⚠ Two corrections to this panel's own notes

**6.1 — The DGM contrast in `17-` §5.4 and `25-` §3 is overstated.**

Those notes contrast our immutable referee against DGM "which rewrites its own
code". That is too glib in two ways [verified]:

- **DGM already freezes its meta-loop.** Line 295: *"the open-ended exploration
  process (i.e., archive maintenance, parent selection) is fixed and not
  modifiable by the DGM, which we leave as an avenue for future work."*
- **DGM explicitly proposes the immutable referee as future work.** Line 642:
  *"an option worth exploring is to create an **unmodifiable part of the system**
  to be able to evaluate at halt the rest."*

So the immutable referee is **not our invention** — the most aggressive
self-modifying system in the literature names it as the thing it lacks. Claiming
novelty there is exactly the kind of overreach a supervisor who knows DGM would
puncture.

**The honest and stronger framing:**

> Every self-improving system freezes something. DGM freezes its archive
> maintenance and parent selection, and names an unmodifiable evaluator as
> future work. The open question is not *whether* to freeze a referee but
> **what the referee should check.** Our answer: declared effects, contracts,
> and typed artifacts — checked mechanically, before admission.

That relocates the contribution from "we have a referee" to "we specify what it
inspects", which is both true and more interesting.

**6.2 — DGM independently states the verification-vs-conformance gap.**
Lines 614-617: if benchmarks "do not fully capture all desired agent properties
(e.g., safety and robustness), the self-improvement loop could **amplify
misalignment over successive generations**." That is 2604.00392's finding, from
a safety angle, in a paper published earlier. Cite both together — a measured
result plus an independent prediction of the same failure is a much stronger
pairing than either alone.

## 7. How to cite each in the report

| Paper | The job it does | Where |
|---|---|---|
| **2604.00392** | The empirical justification | Part II opening |
| **Alita-G** 2510.23601 | The closest system; the loop; library rot | §6 prior art |
| **SkillDAG** 2606.03056 | Independent confirmation that selection is structural | §7b selection |
| **CoEvoSkills** 2604.01687 | Verifier isolation; skills-as-packages; self-built beats human-curated | §7a admission, §9 safety |
| **SkillWeaver** 2504.07079 | Practice-before-admission; capability transfer | §7a, §9 promotion |
| **DGM** 2505.22954 | Self-improvement's ceiling; every system freezes something | §9 safety envelope |
| **Survey** 2507.21046 | Taxonomy, horizons, open safety problems | §1 framing, §8 evaluation |

## 8. The paragraph this yields

> Six systems, one direction. DGM changes the most and checks the least, gating
> self-modification on a benchmark score while candidly noting that a metric
> which misses safety will amplify misalignment across generations. Alita-G is
> the cheapest and most effective of the tool-builders, curating on task outcome
> alone. SkillWeaver adds practice and unit tests; CoEvoSkills adds a verifier
> deliberately isolated from the generator; SkillDAG abandons behavioural
> verification entirely and instead constrains the *relations* between skills,
> refusing any commit that breaks acyclicity or non-contradiction. Read together,
> the field has independently converged on four things: similarity is not enough
> for selection, the artifact needs a check the task cannot provide, the checker
> must not inherit the generator's biases, and libraries need structure once they
> grow. **What none of the six does is require a capability to declare what it
> will touch before it is allowed to run.**
