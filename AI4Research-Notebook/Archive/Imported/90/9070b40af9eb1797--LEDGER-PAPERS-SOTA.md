# SoTA Paper Ledger — workflow half

Built 2026-09-11. **Rule: a paper not opened is not cited.**

⚠ **Provenance standard used here.** Rows below are confirmed at **abstract
level**, fetched from `arxiv.org/abs/` and quoted verbatim. That is sufficient
for abstract-level claims and is recorded as such. It is **not** "we read the
paper." Any claim about a paper's *method, tables, or numbers* requires the full
PDF and is marked NOT YET OPENED until then.

This standard exists because this corpus already shipped a fabricated paper
summary — four invented failure modes, copied into four documents, which
survived a full adversarial review because every grep pointed at the repository
and nobody opened the PDF.

---

## Confirmed — abstract level, verbatim

### `arXiv:2606.07718` — Horstmann et al., submitted 2026-06-05
*A case study of evaluating AI agents on a neuroscience data-to-discovery pipeline*

**The load-bearing quotes:**

> "agents can solve several pipeline stages, suggesting stage-level automation is
> tractable"

> "Solving the end-to-end pipeline requires stringing together successes across
> all stages, which is beyond agents' current abilities."

> agents "struggle most **without a pre-defined criterion**, when they must
> instead use their scientific judgment to assess their current solution"

Other named challenges: computational resource management; generalization to
held-out data; visual interpretation of intermediate outputs for self-evaluation.
Domain: fly optogenetics. Agents: general-purpose coding agents (names NOT in the
abstract — **do not name them without the PDF**).

**Why this matters most.** The third quote names *absence of a pre-defined
criterion* as a primary failure cause. The freeze puts evaluation criteria inside
the plan's integrity hash **before the run starts** — it is precisely the remedy
to the named cause. This is external validation of the system's least-common
mechanism, from a source with no stake in it.

**Second use:** it reframes "we have one demonstrated end-to-end run, with a
mid-run fix, not yet unattended" from an apology into a **field-level
observation**. End-to-end composition is where the field is stuck, not just this
project.

⚠ Stage count and agent identities are NOT established. Do not state them.

### `arXiv:2605.08956` — position paper
*Agentic AI Scientists Are Not Built For Autonomous Scientific Discovery*

> "A growing body of work pursues AI scientists capable of end-to-end autonomous
> scientific discovery. This position paper argues that although they already
> function as co-scientists, agentic AI scientists are not built for autonomous
> scientific discovery…"

Four challenges, as stated: (1) problem selection is influenced by the McNamara
fallacy; (2) LLM training corpora omit tacit procedural and failure knowledge of
laboratory practice; (3) preference optimisation compresses output diversity
toward consensus; (4) most scientific benchmarks measure single-turn prediction
accuracy and lack feedback from physical experiments back to the computational
model.

Architectural recommendations include **"the establishment of a centralized
preregistration repository for all AI-generated hypotheses."**

**Note the adjacency:** preregistration is the same shape as the freeze — commit
to what you are testing, and how you will judge it, *before* you run. Worth one
sentence; do not overstate it into a claim of equivalence.

**Explicitly a position paper, not experiments.** Say so when citing.

### `arXiv:2605.31468` — Qian et al. (19 authors), submitted 2026-05-29
*AutoSci: A Memory-Centric Agentic System for the Full Scientific Research Lifecycle*

**This is the upstream AI4Research explicitly tracks.** Four modules: **SciMem**
(schema-governed memory, long-term knowledge vs active research memory),
**SciFlow** (five-stage lifecycle, literature understanding → rebuttal),
**SciDAG** (DAG-shaped multi-agent operators + stage templates), **SciEvolve**
(feedback signals → versioned updates).

The architectural parallel to this system is direct: memory subsystem, staged
pipeline, DAG operators, evolution engine.

⚠ **The fetched abstract reports no quantitative results.** Do not attribute
benchmark numbers to this paper. Open question #1 below.

---

## NOT YET OPENED — do not cite

| Paper | Why wanted |
|---|---|
| ResearchClawBench `arXiv:2606.07591` | 40 tasks / 10 domains, end-to-end eval — the closest thing to a yardstick |
| TruthInsightBench `arXiv:2609.05079` | evidence-grounded, 40 blind tasks |
| Google Co-Scientist (Nature 2026) | multi-agent generate/debate/evolve; pipeline structure |
| FutureHouse Robin | hypothesis generation from literature |

One search returned frontier figures (Claude-Opus-4.7 ≈ 20.7, frontier mean
≈ 26.5) on an unstated scale. **Unverified. Do not use.**

---

## Questions for a parallel web agent

1. Does **AutoSci (2605.31468)** report quantitative results? On what benchmark,
   with what numbers? The abstract shows none.
2. Which autonomous-research systems **fix evaluation criteria before running**,
   or freeze an execution contract? 2606.07718 names the absence of a pre-defined
   criterion as a failure cause — has anyone built the remedy?
3. Which systems **bind extracted claims to source text by hash**, making
   fabricated citations structurally detectable?
4. Is **"verification recomputes rather than reads a stored verdict"** described
   in agent-systems literature under another name?
5. What do **ResearchClawBench / TruthInsightBench** actually score, on what
   scale, and what are current frontier numbers?
6. Has any published system reported a **fully unattended end-to-end research
   run**? This decides whether the honest-status beat is an apology or an
   observation.
7. Do **Co-Scientist** or **Robin** publish a pipeline stage structure comparable
   to a nine-stage DAG?
8. Is there a **2026 survey** of autonomous research agents with a comparison axis
   set worth adopting rather than inventing?
