# 21 — Alita-G, read closely (arXiv 2510.23601)

Written 2026-09-10 by the capability-capsule panel (pts/9).

The user asked this panel to read Alita-G, so unlike the other tier-1/2 papers
this note **does** reproduce findings. Everything below is from the paper text
itself; section, equation and table numbers are the paper's own.

Alita-G is the closest existing system to the proposed direction (note `17-`
§2.1). Reading it closely changes four things in this panel's positioning, and
all four make the argument *stronger*, not weaker.

---

## 0. What it is, in one paragraph

A generalist "master agent" runs a suite of target-domain tasks K times, and is
prompted to externalise reusable sub-solutions as self-contained MCP tools
rather than only producing answers. MCPs harvested from successful runs are
abstracted by an LLM into parameterised primitives and accumulated into an
**MCP Box**. At inference time a specialised agent embeds the query, scores it
by cosine similarity against each MCP's `description ⊕ use_case`, filters by a
threshold, and runs a CodeAct loop over the survivors. Reported: **83.03%
pass@1 / 89.09% pass@3 on GAIA validation**, with **~15% fewer mean tokens per
example** than its own baseline (§4.2, Table 1).

Loop shape: generate → abstract → curate → retrieve → reuse. That is the same
shape as the proposed self-extension loop in `17-` §4.1, minus stages 5 and 6.

---

## 1. The only curation filter is task outcome

Equation 5 defines the raw MCP pool as

> `L = { MCP_i,j^(k) | π_master(x_i) = y_i, … }`

MCPs are collected **only from executions whose final answer was correct**.
There is no check on the tool itself: no contract, no declared effects, no
schema conformance, no interface test, no negative control. Correct answer ⇒
the tools produced along the way are kept.

⚠ **This upgrades a note `17-` claim from inference to citation.** `17-` §3
asserts "prior work gates on task success, not on the artifact." That is no
longer an inference about the field — it is Alita-G's own selection rule,
stated formally. **Cite Eq. 5 directly.**

This is also the precise point where 2604.00392 applies: it measures that high
task success coexists with tools scoring `C=0.00` on the held-out conformance
suite for the capability they were built for. Alita-G filters on exactly the
signal that paper shows is insufficient.

⚠ **Corrected 2026-09-11.** Previously "tools that violate their own
specifications" — the paraphrase `29-` §6 and the OUTLINE guardrails ban. The
synthesised tools carry no specification of their own; the suite is external.

## 2. Alita-G's curation rule is the one 2604.00392 measures failing

⚠⚠ **REWRITTEN 2026-09-10.** This section previously mapped Alita-G's four
abstraction transforms onto "three of 2604.00392's four failure modes". **Those
failure modes do not exist in that paper** — they came from a bad summary (see
`29-` §5). The mapping is withdrawn. The replacement needs no invented taxonomy
and is stronger.

The abstraction step (§3.3, Eq. 6) applies `LLM_abstract` to each raw MCP:
parameter generalization, context removal, interface standardization to FastMCP,
documentation enhancement. There is **no verification that the abstraction
succeeded** — no post-abstraction test, no signature check against the generated
docstring, no re-execution of the originating trajectory against the abstracted
tool.

Now put that beside 2604.00392's mechanism. Its in-session verifier *"scores
task outputs, not tools"* — **which is exactly Alita-G's Eq. 5 predicate**,
`π_master(x_i) = y_i`. So that paper does not merely happen to apply here. It
measures the failure rate of *precisely this curation rule*, on preserved tools,
at **96.8% (215 of 222)**.

And Alita-G's abstraction produces exactly the artifact class the term **silent
rot** describes: a tool generalised by an LLM to look reusable, which executes
cleanly, and is never replayed against held-out inputs for its own capability.

**The contrast for the report:**

> Alita-G's admission rule is "the task succeeded". 2604.00392 replayed 222
> tools admitted by that class of rule against held-out suites for their own
> capabilities: 96.8% scored zero, while executing cleanly and raising no
> in-session flag. **The rule the closest prior system curates on is the rule
> that was measured to admit broken artifacts at scale.**

Fair to Alita-G — this was measured after their design, and their results stand
— while locating the contribution exactly.

## 3. Library rot is measured, not predicted

§5.2, Table 4, over generation iterations k = 1…5 on GAIA validation:

| k | #MCPs | #Clusters (τ=0.7) | Coverage ratio | Mean sim. | Avg. acc. |
|---|---|---|---|---|---|
| 1 | 26 | 26 | 1.00 | 0.28 | 80.00 |
| 2 | 46 | 41 | 0.89 | 0.31 | 81.82 |
| 3 | 74 | 52 | 0.70 | 0.30 | 83.03 |
| 4 | 102 | 60 | 0.59 | 0.32 | 83.03 |
| 5 | 128 | 65 | 0.51 | 0.34 | 83.63 |

(Coverage ratio = #Clusters / #MCPs, the paper's own effective-coverage
measure; clusters are connected components of the ≥0.7-similarity graph.)

The library grows 26 → 128 while independent capability families grow only
26 → 65. New-cluster yield per iteration decays +15, +11, +8, +5. Accuracy is
flat from k=3 to k=4 while 28 MCPs are added. The paper's own reading: later
iterations "predominantly introduce near-duplicates or narrow variants of
existing capabilities", and k=3 is chosen as the stopping point for that reason.

⚠ **Notes `17-` §4.5 and §5.2 treat duplication growth as a predicted risk.**
It is an observed one, quantified, in the closest prior system, at a library
size (128) barely larger than this project's current 80 capsules. Rewrite those
sections to cite Table 4.

This is the empirical justification for `DUPLICATE_CAPABILITY` as an admission
rejection reason (`17-` §4.3), and it is much stronger evidence than SkillDAG
alone, because it is measured *inside the very architecture being proposed*.

## 4. Selection is flat retrieval, and it is fragile

Selection is cosine similarity between the query embedding and
`description ⊕ use_case` (§3.4, Eqs. 8–10), with a fixed threshold τ. Two
ablations show how much rides on that choice:

**Table 3 — threshold sensitivity (GAIA subset, n=25):**

| τ | 0.65 | 0.70 | 0.75 | 0.80 | 0.85 | 0.90 |
|---|---|---|---|---|---|---|
| Accuracy | 76.0 | **84.0** | 80.0 | 76.0 | 76.0 | 68.0 |

**Table 5 — embedding encoder sensitivity (same subset):**

| Encoder | text-embedding-3-large | -3-small | Qwen3-Embedding-8B | NV-Embed-v2 | BGE-M3 |
|---|---|---|---|---|---|
| Accuracy | **84.0** | 80.0 | 76.0 | 72.0 | 72.0 |

A **16-point swing** from one retrieval hyperparameter, and a **12-point swing**
from the choice of embedding model — on end-task accuracy, with the capability
library held constant. Top-k selection is also tested: it peaks lower (80.0 vs
84.0) and the paper calls it *"generally"* worse — but it is **not** worse at
every setting: at the last threshold top-k scores 72.0 against 68.0 (Table 3).
⚠ Narrowed 2026-09-11 from "uniformly worse or equal".

⚠ **This is the strongest available argument for typed selection**, and it maps
onto the user's stated emphasis: select on whether the capability *matches a
spec*, not on whether its prose description *looks similar*. Capsules already
carry the machinery — `composition.consumes` / `produces` over the 76-entry
artifact-type registry, `operator_compatibility`, and the trust floor — which is
an exact, checkable match rather than a tunable similarity.

Note `17-` §4.5 currently lists embeddings as mitigation step 3. **Demote them
further:** Alita-G shows embedding retrieval is not merely insufficient at
scale, it is a live accuracy variable even at n=74.

---

## 5. Two further facts worth carrying

**The MCP Box has no lifecycle.** It is append-only accumulation. There is no
versioning, no promotion, no demotion, no retirement, no status field, no
provenance record beyond the originating `use_case` string. Note `17-` §2.1
says Alita-G lacks a contract and admission layer; it also lacks everything in
note `19-`'s lifecycle state machine. Say both.

⚠ **Upgraded from assertion to citation — see note `27-`.** The full lexical
audit is there: `retire`, `deprecat`, `version`, `dedup`, `prune`, `evict`,
`delete`, `remove`, `adversarial` all occur **zero** times in the paper; the
single `lifecycle` hit is in the *related-work* section crediting another
system. And non-consolidation is a **stated design choice**, §3.3 verbatim:
*"Unlike traditional clustering approaches, our method preserves the diversity
of MCP implementations to maximize coverage of potential task variations."*
Use `27-` whenever this claim is made — it is the report's strongest single
piece of evidence.

**Self-extension is not regression-free, and the paper says so.** Table 6
reports Wrong→Right flips of 9/12/13 against Right→Wrong flips of **1/1/0**
across the three MCP Box generations. The report should not claim self-extension
is regression-free; Alita-G's own honesty here is a good model to follow.
(The paper attributes the two regressions to agent reasoning errors rather than
to MCP usage, which is an interpretation, not a measurement.)

---

## 6. Two observations to hold for Q&A only

Both concern experimental design. Phrase them as observations, **not**
accusations — the paper is transparent about both, and a supervisor may raise
either first.

1. **The MCP Box is built from the evaluation set.** §5.2: "Each iteration runs
   the master agent once over the entire validation set to harvest additional
   MCPs", and results are then reported on GAIA validation. Tools are harvested
   from the same task set they are scored on. This is disclosed, and it is
   defensible for a domain-specialisation claim — the framing is "generalist →
   domain expert *across a set of tasks*", not held-out generalisation — but it
   does bound what the GAIA number demonstrates.
2. **"Directly comparable" needs qualifying.** ⚠ Note `17-` §5.1 calls GAIA a
   directly comparable benchmark. Alita-G runs a Manager Agent on
   **Claude-Sonnet-4** and a Web Agent on **GPT-4.1** (§4.1), with
   `text-embedding-3-large` at τ=0.7, under pass@1 / pass@3. A comparison that
   does not match that stack and protocol is not like-for-like, and AI4Research
   is a scientific-research-lifecycle system rather than a GAIA agent. Soften
   the claim to "the benchmark the closest prior work reports on" and state the
   configuration gap explicitly.

---

## 7. What this means for the report

> ⚠ **Corrected 2026-09-11.** The block below previously read "It identifies
> hidden dependencies, interface violations and specification drift as the
> problems to solve." Those three terms are the fabricated vocabulary withdrawn
> in `29-` §5.1 — they occur zero times in 2604.00392, and attributing them to
> *Alita-G* compounded the error by attaching them to the wrong paper. This was
> the last known instance, and it sat in the most quotable paragraph in the
> note. Replaced with what Alita-G actually does: an unverified LLM rewrite.

The positioning in `17-` §3 survives intact and gets sharper. Restated with
this reading:

> Alita-G demonstrates that an agent can build its own capability library and
> measurably improve — 83.03% pass@1 on GAIA, at ~15% lower token cost. It
> curates that library on one signal: did the task succeed. Its remedy for
> artifact quality is an unverified LLM rewrite (§3.3, Eq. 6), with no per-tool
> check at any point. And its own Table 4 shows the library filling with
> near-duplicates as it grows.
>
> A capability capsule is the missing filter — at admission, and at selection.

Three concrete report claims this note licenses, all citable:

1. Prior work's curation signal is task outcome. **(Eq. 5)**
2. Prior work's fix for artifact quality is unverified LLM rewriting. **(Eq. 6, §3.3)**
3. Capability-library duplication is an observed failure, not a hypothetical.
   **(Table 4: coverage ratio 1.00 → 0.51)**

---

## 8. Cross-references

- `17-` §2.1, §3, §4.5, §5.1, §5.2 — all amended against this note.
- `19-` — the lifecycle machinery Alita-G's MCP Box has none of.
- `22-` — trust classes; the typed alternative to similarity selection.
- 2604.00392 — the measurement of what Alita-G's curation rule admits.
  ⚠ Reworded 2026-09-11: Alita-G names no failure modes (zero occurrences).
- 2606.03056 (SkillDAG) — the same scaling argument, made independently.
