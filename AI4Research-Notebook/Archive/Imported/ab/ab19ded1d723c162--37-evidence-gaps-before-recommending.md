# 37 — What we still need before we can recommend a capsule design

Written 2026-09-10 by the capability-capsule panel (pts/9).

> "What data to cover next to be able to recommend what cap cap should look like?"

**The blunt assessment: the *justification* is finished and the *specification*
has almost no evidence behind it.** Every number in the notes is someone else's.
A recommendation — an actual manifest schema someone could implement — currently
rests on reasoning, not measurement.

This note is a work plan: each unresolved design decision, the evidence that
would settle it, and what it costs to get.

---

## 0. What is already done — do not gather more of this

Saying this first, so the remaining effort goes where it is needed.

| Question | Status |
|---|---|
| **Why gate at all?** | **Closed.** Three independent papers at three levels: tools are broken (2604.00392, 96.8% at C=0.00), skills are worthless unverified (CoEvoSkills, 30.7-34.1% vs a 30.6% baseline), agents break their own gate (DGM node 114). `29-`, `35-`, `36-` |
| **Who else does this?** | **Closed.** Six systems compared from source. `28-` |
| **Is the referee idea novel?** | **Closed — it isn't**, and we say so. `28-` §6.1 |
| **Where does it run / threat model?** | **Closed enough.** `26-`, and dsh settles most of it. `34-` |
| **What does verification cost?** | **Closed.** Audit overhead is millisecond-scale; 4.1 verification cycles + 2.4 oracle rounds per capability; DGM $22k vs $10k. `33-` |

**Adding more prior art now has near-zero marginal value.** The next unit of
effort belongs in §1 and §2.

---

## 1. ⭐ Highest value: measure our own system

**This is the gap that matters.** A supervisor will ask "what does *your* data
say," and today the answer is "the literature's data." Everything below is
read-only, cheap, and produces numbers nobody else has.

### 1.1 The manifest census — what the contract vocabulary actually does

We know three data points already and they are the most useful facts in the notes:
`implementation` in **21 of 85**, `version` in **43 of 85**, `recoverable` in
**0 of 85** (`14-` A-3, `13-`). Extend that to every field.

**Produce:** for all 85 manifests, per-field population counts, value
distributions for enumerated fields, and co-occurrence.

**Settles:**
- Which contract fields are **alive, vestigial, or dead** — the single best
  guide to what a v2 schema should keep, drop, or make required.
- Whether `effects`'s four axes (read/write/execute/network) are actually used
  discriminatively or collapse to a couple of patterns.
- Whether `composition.consumes/produces` is populated densely enough for typed
  selection (`23-` §4 stage 0) to work **at all**. **If it is sparse, the entire
  stage-0 recommendation is unfounded** — this is the highest-risk assumption in
  the design.

**Cost:** an hour, read-only. **Do this first.**

### 1.2 The gate-outcome census — has admission ever rejected anything?

We have asserted throughout that the admission gate is real, implemented and
tested. We have **never checked whether it fires in practice**.

**Produce:** occurrences of each of the five rejection reasons across run
history, logs, and evidence ledgers; distribution over reasons; whether any
non-test rejection exists.

**Settles:** whether the gate is load-bearing or ceremonial. **If it has never
rejected a real capability, that is a finding — and it should be in the report,
because a supervisor may already know it.**

### 1.3 The gap census — what does demand look like?

**Produce:** how often the planner emits `unsatisfiable_nodes`, and whether the
same gap recurs.

**Settles:** the routing question (`23-` §5), the cold-start question (`23-` §6),
and `33-` Q44 — expected reuse `n` is unestimatable without recurrence data, and
recurrence is a far better proxy than a model's prediction (AllocBench, §2.1).

### 1.4 Effect-declaration divergence — the one real experiment

Take a sample of existing capsules, run them, compare **observed** effects
against **declared** effects.

**Settles:** whether `EFFECT_UNDECLARED` (`17-` §4.3) — the highest-value
proposed rejection reason — detects anything on *hand-written* capsules. If
humans already under-declare, that is a strong result and it argues the check is
needed before self-generation, not after.

⚠ **This one needs execution, so it is blocked by the read-only rule** and needs
the user's permission. It is the only item here that does.

---

## 2. Papers: two to finish, one to read properly

### 2.1 AllocBench (2607.23332) — **read in full, it is cited as tier-1**

⚠ We have cited it from **the abstract page only**. That is precisely the mistake
that produced the fabricated failure modes in `29-` §5, in slow motion. Its
finding — that models allocate near-optimally in the abstract and fail entirely
when writing code — is now load-bearing for `33-` §4 and for the claim that "should
this capability exist?" cannot be delegated.

**Needed from it:** the actual budget formalisation (what is `B`, what counts as a
tool), the failure-mode taxonomy per model, and whether it proposes any mechanism
rather than only measuring. **Highest-priority read.**

### 2.2 SkillDAG (2606.03056) — read the scaling results, not the mechanism

We have its mechanism and its headline. **We do not have the curve.** The stage-0
typed-selection recommendation rests on their claim that ranking "stays robust as
the pool grows 10× where a fixed seeding–diffusion pipeline degrades."

**Needed:** the actual scaling numbers, the library sizes tested, the edge-type
ablation (which of `depends_on` / `specializes` / `similar_to` / `conflicts_with`
carries the benefit), and the cost of maintaining the graph.

**Why it matters:** if most of the benefit comes from `conflicts_with` alone, the
recommendation is much smaller and cheaper than a full typed graph.

### 2.3 CostBench (2511.02734) — abstract is probably enough

Tier 2. Read only if the report claims the system reasons about its own budget.

### 2.4 Not needed

The survey, Alita-G, SkillWeaver, CoEvoSkills, DGM and 2604.00392 are read to
sufficient depth. **Do not re-open them** except to verify a specific quote.

---

## 3. dsh: five [repo-claim]s to convert to [verified]

`34-` §6 already lists these; repeating because they gate the design, not just
the prose. All are single greps in the dsh checkout.

1. The three-role obligation in `AGENTS.md` — **B2 rests on it.**
2. The versioned-successor durable-data rule — the concurrency design rests on it.
3. **`ctx.invariants` semantics** — a registry of *what*, checked *when*? If it
   is startup-only it does not serve runtime invariant monitoring (`31-` §4.3),
   and that changes the recommendation.
4. That `extensions/` is unmounted in the shipped bundle, not merely optional.
5. Whether `ctx.tokenMeter` measures live or only on replay.

**Plus one new question that determines the shape of everything:** does a
capsule *become* a seam, or govern seams? (`34-` Q48). Settling it needs the
`Service` base class and one real seam package read directly.

---

## 4. The decision → evidence map

The compact version. Each row is a design decision that cannot honestly be made
without the evidence beside it.

| Design decision | Evidence needed | Where | Blocked? |
|---|---|---|---|
| Which fields a v2 manifest requires | manifest census | §1.1 | no |
| Whether typed stage-0 selection is viable | `consumes/produces` density | §1.1 | no |
| Whether the gate is real | rejection-reason census | §1.2 | no |
| How to estimate expected reuse | gap recurrence | §1.3 | no |
| Whether `EFFECT_UNDECLARED` earns its place | declared vs observed effects | §1.4 | **needs execution permission** |
| How much typed-graph machinery to recommend | SkillDAG edge ablation | §2.2 | no |
| Whether to impose a capability budget | AllocBench full read | §2.1 | no |
| Capsule as seam, or above seams | dsh `Service` + one seam package | §3 | no |
| Whether runtime invariant monitoring is available | `ctx.invariants` semantics | §3 | no |
| Conformance suite size and shape | **already settled** — 2604.00392: 5-6 hidden + 5-6 adversarial, median 11 | `29-` | done |
| Retirement reason vocabulary | **derived, not measured** — accept as a proposal | `31-` | accepted |
| State class vocabulary | **derived, not measured** — accept as a proposal | `32-` | accepted |

**The last two rows are deliberate.** Some of the design is reasoned rather than
measured, and the report should say which parts those are rather than implying
everything is evidence-backed. That distinction is what `29-` cost us.

---

## 5. Suggested order

1. **Manifest census** (§1.1) — an hour, unblocks the most decisions, and gives
   the report *its own* headline number.
2. **AllocBench in full** (§2.1) — closes a citation risk we have already been
   burned by once.
3. **Gate-outcome census** (§1.2) — cheap, and potentially a finding.
4. **dsh verification** (§3) — five greps, converts B2 from claimed to verified.
5. **SkillDAG scaling results** (§2.2) — sizes the selection recommendation.
6. **Gap census** (§1.3).
7. **Effect-divergence experiment** (§1.4) — ask the user first.

Items 1-4 are a day's work and would move the report from "well-argued" to
"evidence-backed on its own system," which is the difference the supervisor will
actually notice.

## 6. The honest framing for the report

Whatever we gather, the recommendation should be explicit about its own footing:

> The case for an admission contract is empirical and rests on three independent
> results. The *specific shape* of the contract proposed here is derived from
> that evidence plus the constraints of the target platform — it is a design
> proposal, not a measured optimum, and the fields most likely to change are
> the ones marked as such.

Saying that costs nothing and pre-empts the obvious challenge.

---

## ⭐ Manifest census — run 2026-09-11 `[verified]`

Read-only, over both manifest directories in `AI4Research/harness`.

| Measure | Result |
|---|---|
| Manifests | **79** (39 `capability-capsules/` + 40 `config/capability-capsules/`) |
| `composition:` block present | **79 / 79** |
| `consumes` populated (non-empty) | **79 / 79 — 100%** |
| `produces` populated (non-empty) | **79 / 79 — 100%** |
| `compatible_with` non-empty | 75 / 79 |
| `requires_after` non-empty | 46 / 78 |
| `incompatible_with` non-empty | 37 / 79 |

**The highest-risk assumption is validated, not falsified.** Stage-0 typed
selection rests on `composition.consumes/produces` being densely populated. It is
populated everywhere, and with *typed identifiers* rather than free text.

⚠ **But the census found a heterogeneity problem nobody had flagged.** There are
**two type vocabularies**, split cleanly by directory:

| Form | Count | Example |
|---|---|---|
| `schema_ref:` — JSON Schema path | 39 (114 refs) | `schemas/evidence/claim_verdict.v1.schema.json` |
| `type:` — artifact type id | 40 | `artifact.optimizer_graph` |

Both are exact-matchable, so stage 0 works *within* each family. Neither family
can match the other without a normalisation layer. **That layer is now a
prerequisite of the design, not an optimisation** — and it is a concrete,
scoped piece of work rather than an open question.

**Second finding, unlooked-for:** the manifests already ship a partial
SkillDAG-style edge vocabulary — `compatible_with`, `incompatible_with`,
`requires_after`. That maps onto `composes_with`, `conflicts_with` and
`depends_on`. The structural-selection argument therefore has repo support as
well as literature support; `requires_before` is absent, and acyclicity is not
checked anywhere.
