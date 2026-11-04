# 38 — AllocBench, read in full

Written 2026-09-10 by the capability-capsule panel (pts/9).
**[verified]** against `/home/muk/work/papers/2607.23332.{pdf,txt}` — downloaded
and extracted this session; line numbers are that `.txt`'s.

**AllocBench: Measuring Online Tool Allocation Capability in LLM Agents** —
Daniel Wang and Andrew Xu, **Yale University**. arXiv **2607.23332v2 [cs.LG]**,
31 Jul 2026. ⚠ **Preprint** — not a published conference paper. Cite accordingly.

Note `33-` §4 cited this from the abstract page. **The substance held up** — but
that was luck, not process, and the full read adds an architectural prescription
we did not have.

---

## 1. The question, and why the design is good

> *"Existing evaluations ask whether a model can write a correct tool, choose an
> available tool, or select from a growing library. They largely leave a more
> fundamental decision unmeasured: **when should the agent create a tool?**"*

**The setup.** A stream of `T = 60` problems drawn from `N = 8` latent numeric
families (LCGs, modular exponentiation, continued fractions, CRT systems,
Josephus, iterated modular quadratic maps, xorshift, modular matrix powers).
Budget `B = 3`. Per episode, **3 families are "hot"** (0.85 of the mass, recurring
13-23 times) and **5 are "traps"** (0.15, recurring 1-6 times). Streams are
rejection-sampled so **at least one trap appears within the first 3 slots**. 24
seeds. Models are verified to be approximately unable to solve the problems
without a script, so allocation genuinely matters.

**The optimal policy is simple and stated up front: pass on first sight, build on
confirmed recurrence.** Committing to a class's first instance forfeits one
occurrence if you wait, but spending budget on a trap forfeits an entire hot
class.

### The framing ladder — this is the contribution

Four renderings of **identical latent sequences**, so the optimal policy is the
same at every rung and the only thing that changes is the *act* being asked for:

| Rung | What the model does |
|---|---|
| **R0 abstract** | coloured balls; free-text KEEP/PASS |
| **R1 declarative** | real numeric problems; KEEP/PASS **tool calls**, no code |
| **R2 code** | keeping requires a non-empty `solve(inputs)` — **payoff is independent of code correctness** |
| **R3 full** | reusable script, tested and rerun on later instances |

**Metric — first-sight commitment**: the fraction of commitments made on a
class's *first* occurrence. Lower is better; the optimum passes every first
instance. Paired with **Score** = realised utility / hindsight optimum, reported
only on R0-R2 because R3 confounds allocation with script-writing ability.

## 2. ⭐ The result

Table 1 (line 357), pooled first-sight commitment — **lower is better**:

| Model | R0 abstract | R1 declarative | R2 code | R3 full | Fails at |
|---|---|---|---|---|---|
| Claude Haiku 4.5 | 28% | 33% | **99%** | 100% | R2 |
| Claude Opus 4.8 | **4%** | 0% | **92%** | 99% | R2 |
| GPT-5.4-mini | 15% | 29% | **85%** | 88% | R2 |
| GPT-5.6 Sol | 24% | 0% | 39% | **100%** | R3 |

**Opus goes from 4% to 92% the moment code emission is required.**

Two controls make this sharp:

1. **R1 causes no shift in any model.** Real numeric problems with declarative
   claims preserve allocation. **So the failure is not caused by mathematical
   reasoning** — it is caused by being asked to write code.
2. **R2 does not check code correctness.** Merely *requiring* a script destroys
   allocation. It is not the difficulty of writing correct code; it is the
   framing.

GPT-5.6 Sol survives R2 at 39% — so allocation under code requirement is
demonstrably possible — but collapses to 100% at R3, when forced through
`write_script` / `run_script` tools.

### The transcripts (line 368-377) — quote these

**Abstract frame**, Opus: *"Still gathering information; too early to commit a
keep."* And: *"Red has now appeared 3 times in 7 draws — a strong rate. With 53
draws left, keeping red should yield many more."*

**Tool frame**, Opus, on the **first problem of the stream**: *"I'll write a
script for this bit-manipulation problem type."* Budget appears only near
exhaustion: *"I have 1 write left."*

> *"The models do not consider waiting for recurrence evidence at all, and
> scripts are reused only reactively when a class later returns."*

## 3. It is not economic ambiguity — the price check

Appendix E (lines 1307-1320) makes the build cost **visible**, at charges
K ∈ {0, 10, 20, 24}:  ⚠ (the 20 was missing before 2026-09-11)

- **R0's first-sight hazard falls as price rises**, tracking the hindsight
  optimum, which itself drops to ~1% commitment at K = 24.
- **R2 stays pinned near 100% across the entire surface** — including at K = 24.

> **Abstract allocation responds to price. Code-required allocation is
> behaviourally inelastic.**

⚠ **This is the most important operational finding for us and it was not in the
abstract.** *Telling the agent what building costs does not change what it does.*
A capability budget communicated in a prompt will not work. **A budget has to be
an enforced gate, not a stated price.**

## 4. Reinforcement learning does not rescue it

Qwen2.5-Coder-14B-Instruct (q8_0 GGUF), QLoRA + PPO, no demonstrations, with an
asymmetric critic that observes the true latent class rate. 20 steps × 25
episodes.

- R0 first-sight commitment: **74% → 6%.**
- Generalises to **lexical reskins** (coins in a chest, arrows in a quiver) —
  near-zero, so it learned the policy, not the vocabulary.
- Generalises to the same choice issued through a **zero-argument tool call**.
- ⚠ **Breaks at R1** — earlier than any frontier model's failure point. Base and
  post-trained Qwen become statistically indistinguishable the moment a numeric
  problem is shown.

Score (Table 2, line 497), percent of hindsight optimum:

| | R0 | R1 | R2 |
|---|---|---|---|
| Qwen-14B base | 74.8% | 49.2% | 61.2% |
| Qwen-14B post-trained | **79.6%** | **34.8%** | **41.7%** |

Post-training lifts R0 to frontier level (79.6% vs GPT-5.6 Sol's 78.3%) and
**leaves R1/R2 no better**. The authors attribute the R2 drop to a code-emission
channel limitation of a 14B model rather than to allocation timing.

## 5. ⭐ Their prescription — and it is directly actionable

Lines 556-563:

> *"Our results indicate that current models cannot simultaneously manage budget
> allocation and tool creation. This suggests that tool-building agent systems
> should **separate the abstract decision to invest from the process of creating
> the tool**. For example, the R3 task streams could be split with one agent
> outputting declarative claims when building is optimal (R1), and a different
> agent constructing the desired tools."*

**This is an architectural recommendation, not just a measurement**, and it lands
directly on three of our open questions:

- **`33-` Q45 — who enforces rung 0?** Answer: a *separate component* from the
  builder. Not the generating agent, and not a prompt instruction to it.
- **`30-` §3.4 — the gap lease.** The lease registry already sees every intent to
  build before any building happens. **It is the natural home for the invest
  decision**, and AllocBench says that decision must live outside the builder.
- **`23-` §5 — plan-time versus run-time routing.** This strengthens the
  plan-time recommendation considerably. The planner emitting `unsatisfiable_nodes`
  is operating in something close to R1 — declarative claims about what is
  needed, with no code in hand. **That is exactly the frame where models still
  allocate well.** The moment the decision moves inside the building step, it is
  in R3, where every model tested fails.

> **Design rule: the decision to build and the act of building must be different
> steps, in different frames, and the budget must be enforced by the first.**

## 6. Their explanation (conjecture, and labelled as such)

Lines 541-554: coding post-training datasets (DeepSWE and similar) present
streams of **unrelated problems with independent rewards**. Episodes share no
state, so a tool built while solving one problem has no expected future value —
there is no gradient toward reserve behaviour. Reasoning models additionally
carry explicit length and efficiency penalties, favouring solving the visible
instance directly.

They note both OpenAI and Anthropic have stated they use RL on coding datasets,
and explicitly leave the mechanistic account to future work.

## 7. A framing worth borrowing

Lines 576-581 distinguish two failure modes that tool benchmarks conflate:

- **the policy is absent** (base Qwen), versus
- **the policy is present but suppressed by framing** (every frontier model).

Useful vocabulary for our own evaluation section: a capability that fails is not
necessarily a capability that is missing.

## 8. Limitations — state these if we cite it

- **One synthetic environment.** Engineered classes and streams; real tasks have
  ambiguous class boundaries, shifting frequencies, incomplete reusability, and
  an unknown number of classes. 24 streams.
- ⚠ **Both GPT models ran at `reasoning effort=none`**, because the OpenAI
  endpoint rejected tools with reasoning enabled. The authors argue the paired
  design holds this fixed within model, and that the wall persists across
  capability levels — but it is a real caveat and a supervisor may spot it.
- The RL study uses a **privileged critic** and does not demonstrate
  non-privileged learnability, nor that post-training *cannot* fix R3.
- Score is calibrated against a hindsight optimum that is not implementable
  online, so it is a **relative** measure only.
- **Preprint**, cs.LG.

## 9. What changes in our notes

- `33-` §4 — substance confirmed; add the ladder table, the R2-without-correctness
  control, and the **price-inelasticity** finding, which is new and important.
- `33-` Q46 (a per-session capability budget) — **answered in shape**: yes, but it
  must be externally enforced, because a stated price provably does not change
  behaviour.
- `30-` §3.4 — the gap lease gains a second, stronger justification: it is the
  separation AllocBench prescribes, not merely stampede control.
- `23-` §5 — plan-time acquisition is now supported by evidence rather than by
  analogy to the freeze contract.
- `17-` §7 Q4 (unbounded growth vs fixed budget) — reframe: the question is not
  the size of the budget but **who holds it**.
