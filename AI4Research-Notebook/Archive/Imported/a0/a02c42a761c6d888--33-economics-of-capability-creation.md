# 33 — What a capability costs: the investment ladder

Written 2026-09-10 by the capability-capsule panel (pts/9), from the user's
question. Paper figures **[verified]** against the local extractions; the two new
papers in §4 verified against their arXiv abstract pages.

> "Agents can often write one-off scripts very quickly (a little skill), MCPs
> take more time, and actually testing, adversarial review, concurrency stuff
> will take even longer."

The intuition is right about *engineering* time and **wrong about runtime cost**,
and the inversion is the most useful thing in this note.

---

## 1. What the papers actually report

Cost is under-reported across the set, but three papers give hard figures.

**DGM — the price of self-improvement** [verified, 2505.22954 lines 2099-2108]:

| Run | Cost |
|---|---|
| One DGM run on SWE-bench | **~USD 22,000** |
| One baseline run (no self-improve, *or* no open-ended exploration) | ~USD 10,000 |
| Reference: Claude 3.5 Sonnet, SWE-bench, 60 tasks | $350 |
| Reference: o3-mini, Polyglot, 60 tasks | $5 |

So **the premium for self-improvement is roughly 2.2× — about USD 12,000 per
run** — and the paper notes the process "takes weeks and incurs significant API
costs" (line 675). This is the single best cost datapoint in the literature for
"what does it cost to let a system improve itself", and it is not small.

**2604.00392 — the price of auditing** [verified, lines 334-339]:

> *"Per-task audit overhead is **dominated by the LLM calls themselves** —
> manifest emission, reuse decomposition, and per-tool source dumping add
> **millisecond-scale latency and bounded disk I/O**, so the layer is **cheap
> enough to leave on in production**."*

Their tool execution runs in an in-process sandbox with a **five-second
wall-clock limit** (line 177), and their conformance suites are median 11 inputs.

**Alita-G — the operating saving** [verified]: 12,305 → 10,394 mean tokens per
example, **−15.5%**, from having a curated library at all.

**SkillDAG** [verified, line 912]: indexing costs one embedding call per skill
per view, two views. Negligible.

**CoEvoSkills — the per-capability verification cost** [verified, 2604.01687
lines 681-683]: convergence takes on average **4.1 verification cycles and 2.4
ground-truth oracle rounds per task**, and the authors note that "convergence
within five rounds keeps the evolution cost practical." This is the only
published figure for what verifying one capability actually costs.

⚠ **And it makes §3's ladder a step function, not a gradient** (`35-` §1): an
*unverified* tool scores 30.7-34.1% against a 30.6% no-skill baseline — rung 2
buys essentially nothing — while verified skills reach 71.1%. **The value is not
distributed along the ladder; almost all of it sits at rungs 3-4.**

## 2. The inversion

> **Generation has low fixed cost and high marginal cost. Verification has high
> fixed cost and low marginal cost.**

Generation is LLM calls, every time, per capability, forever — DGM's $12,000
premium is exactly this. Verification, once the harness exists, is a bounded
sandbox execution plus millisecond bookkeeping, and the paper that measured it
says leave it on in production.

**Verification amortises. Generation does not.**

Where the user's intuition holds exactly: the **fixed** cost of verification is
genuinely large, and it is paid up front in engineering — fixture resources,
adversarial suites, concurrency probes (`32-` §5), the held-out suite discipline.
That cost is real, one-time, and currently unpaid. `32-` Q41 (does a fixture
resource exist?) is the largest single item in it.

So the honest framing for the report:

> The expensive part of a conformance gate is **building it once**, not running
> it. The expensive part of self-extension is **generating**, every time. A
> project that already intends to generate capabilities has already accepted the
> larger recurring cost; the gate is the smaller one, and it is the one that
> amortises.

## 3. The investment ladder

The user's gradient, made explicit. Each rung costs more and buys something
different:

| Rung | Artifact | Marginal cost | What it buys | Enters the library? |
|---|---|---|---|---|
| **0** | Inline code, used once, discarded | ~0 | nothing beyond the task | **No** |
| **1** | Saved script — "a little skill" | low | retrievable by a human | No |
| **2** | Parameterised tool / MCP | moderate — abstraction is LLM work | reuse across tasks | Only with a contract |
| **3** | Capsule: contract, declared effects, held-out conformance suite | **the fixed cost** | admissibility; silent rot caught | Yes, as `draft` |
| **4** | + state class, compensation, concurrency probes, adversarial review | higher, but mostly one-time infrastructure | safe under concurrency and external state | Yes, promotable to `stable` |

**Rung 0 is a real option and the notes have been ignoring it.** Not everything
should become a capability. That is the anti-bloat policy, and it is the direct
answer to Alita-G's measured duplication (`27-` §4) and to the open question
about unbounded growth versus a fixed budget per domain.

## 4. ⭐ AllocBench — a paper about exactly this, and its finding is bad news

**AllocBench: Measuring Online Tool Allocation Capability in LLM Agents** —
arXiv **2607.23332**, Daniel Wang and Andrew Xu, submitted 25 Jul 2026, revised
31 Jul 2026. [verified against the arXiv abstract page]

⚠ Note the name: **AllocBench**, not "AlloBench" — secondary sources render it
both ways. Same class of error as the CoEvoSkills/EvoSkills mix-up (`17-` §6).

Its opening frames the user's question better than this note does:

> *"Creating a reusable tool is an investment: an agent pays a fixed cost now in
> exchange for the potential of future reuse. Therefore, a user should prefer an
> agent that creates a small number of highly reusable tools, rather than many
> one-offs."*

It tests allocation under a **fixed budget** in two settings — an abstract
text formulation and a code-construction task. The finding:

> *"Every frontier model we test — Claude Haiku, Claude Opus, GPT-5.4-mini, and
> GPT-5.6 Sol — acts **near-optimally in the abstract framing but fails to
> transfer this ability to script-writing**."*

And it is not a prompting artifact. The first three models fail **even when the
scripts are not evaluated**; GPT-5.6 Sol stays selective under that weaker
manipulation and collapses only at full construction. A Qwen model policy-trained
for abstract allocation generalises across held-out lexical variations but sees
**no improvement at script allocation**.

**Why this matters more than any cost figure.** The models *know the right
policy* and cannot execute it while actually writing code. Therefore:

> **The "should this capability exist at all?" decision cannot be delegated to
> the agent that would build it.** It has to be a system-level policy.

That is a direct empirical argument for widening the admission gate. Until now
the notes have framed it as "is this artifact sound?" AllocBench says it must
also cover **"should this artifact exist?"** — and that the generating agent is
measurably the wrong component to ask. Rung 0 of §3 has to be enforced from
outside.

This is a **tier-1 read** and it changes §4.3 of note `17-`.

⚠ **Now read in full — see note `38-`.** The substance above held up, but two
findings were not in the abstract and both matter:

1. **R2 does not check code correctness.** Merely *requiring* a script collapses
   allocation (Opus 4% → 92%), while R1 — real numeric problems, declarative
   claims, no code — causes no shift at all. The failure is the framing, not the
   reasoning and not the difficulty of writing correct code.
2. **Stating the price does not help.** With a *visible* build charge, abstract
   allocation tracks the optimum downward while code-required commitment stays
   pinned near 100% across the whole surface. **A budget in a prompt will not
   work; a budget must be an enforced gate.** That answers Q46 in shape.

And their prescription is architectural: *"tool-building agent systems should
separate the abstract decision to invest from the process of creating the tool."*

**Also found — CostBench**, arXiv **2511.02734** (Liu, Qian, Su, Zong, Huang, He,
Fung; Nov 2025, rev. Jun 2026): a cost-centric benchmark for multi-turn
cost-optimal *planning*, in a travel domain with tool-cost variation and dynamic
blocking events. Agents frequently fail to find cost-optimal solutions even
statically, and performance drops ~40% under dynamic conditions. **Tier 2** — it
concerns cost-aware planning rather than capability-creation economics, but it is
the nearest thing to a cost-reasoning benchmark and worth citing if the report
claims the system reasons about its own budget.

## 5. The decision rule — two axes, and reuse is the secondary one

Naively this is amortisation: build if `n · s > c_gen + c_ver`, for `n` expected
reuses and `s` saving per reuse. Alita-G puts `s` at roughly 15% of per-task
tokens.

But amortisation alone gives the wrong answer for the dangerous cases, so the
rule needs a second axis — **blast radius**, which capsules can read off the
declared effects and state class (`32-` §3):

| | **Low blast radius** (`pure`, `read_only`) | **High blast radius** (`stateful_exclusive`, external writes) |
|---|---|---|
| **Low expected reuse** | **Rung 0-1.** Inline it. Do not admit. | **Rung 4 or refuse.** One destructive miss costs more than the entire verification budget |
| **High expected reuse** | **Rung 3.** Contract + conformance suite | **Rung 4.** Full treatment |

> **Reuse decides whether it is worth building. Blast radius decides how much
> rigour — and it overrides reuse.**

A single-use capability that writes to a shared database gets the full treatment
or does not run, no matter how poor the amortisation. That asymmetry is the whole
argument compressed into a scheduling rule.

## 6. The economics predict saturation — and Alita-G measured it

`s` is not constant. As the library fills, each new capability overlaps more with
what exists, so its marginal saving falls. Eventually `n · s < c_gen + c_ver` and
building stops paying.

**That is exactly Alita-G's Table 4.** Effective coverage falls 1.00 → 0.51 while
tools grow 26 → 128; accuracy is flat from k=3 to k=4 while 28 tools are added;
the authors stop at k=3. They did not describe it as economics, but it is: **the
marginal capability stopped being worth its generation cost.**

This is a nice closing move for the report — a predicted effect with an
independent measurement, and it turns "when do we stop generating?" from a
hand-wave into a question with a shape:

> Stop when the marginal capability's expected saving no longer covers its
> generation and verification cost. Alita-G's effective-coverage ratio is a
> usable proxy, and it comes with a published baseline.

## 7. Open questions

- **Q43 — What is `s` here?** Alita-G's 15% is for GAIA-style tasks with a
  particular stack. A research-lifecycle task may amortise very differently, and
  nobody has measured it for this system.
- **Q44 — How is `n` estimated at admission time?** Expected reuse is a
  prediction, and AllocBench says models are bad at acting on it. A conservative
  proxy — has this capability gap recurred before? — may beat any estimate.
- **Q45 — Who enforces rung 0?** If the generating agent cannot be trusted to
  decline (§4), something else must. The gap-lease registry (`30-` §3.4) already
  sees every intent to build and is the natural place.
- **Q46 — Is there a per-session capability budget?** AllocBench's fixed-`B`
  framing is directly implementable and would make the constraint explicit rather
  than emergent.
- **Q47 — Does the verification fixed cost get counted honestly?** A report that
  claims the gate is cheap must say cheap *per capability, after the harness
  exists*, and state the harness cost separately.
