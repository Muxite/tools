# 25 — Evolution policy: who gets better, and what must never change

Written 2026-09-10 by the capability-capsule panel (pts/9), from the user's
follow-up brief. Read after `23-`.

> "The selection of general and specialised is a very big concern. With
> week-long self-running agents we could likely **never transition to only
> specialised** — we have to be able to do anything and everything to recover
> from failures or respond to a big discovery and change in actions. How do we
> decide how agents evolve, and should the general agent be getting better too?"

This is the deepest objection raised so far, and it does not weaken the
capsule direction. **It inverts Alita-G's thesis, and the inversion is the
report's strongest theoretical claim.**

---

## 1. Specialisation is a bet on a stationary task distribution

Alita-G's value proposition is generalist → domain expert as a **terminal
transformation**. That is sound *because its task distribution is fixed by
construction*: a curated suite, harvested K times, evaluated on the same
domain (`21-` §6). The distribution cannot move, so a specialist can never be
caught without a tool.

A week-long autonomous research run is **explicitly non-stationary**. The
brief names the mechanism precisely: a big discovery changes what the system
should be doing next. So does a failure. In both cases the task distribution
moves *during* the run, and it moves in a direction no prior harvest anticipated.

> **Specialisation is a bet that the task distribution will not move.
> Long-horizon autonomy is the case where that bet is guaranteed to lose.**

Therefore, for this system, **specialisation is a reversible, partial state —
not a destination.** The generalist is not a scaffold to be discarded once the
library is rich enough. It is the permanent recovery path.

This is a genuine structural disagreement with the closest prior work, stated
in its own terms, and it belongs early in the report's Part II.

## 2. The trap: specialising the recovery path destroys the recovery path

The obvious next move — feed the generalist's own successful trajectories back
into the generalist — is the one to argue against explicitly.

Whatever the generalist learns from, it drifts toward. Trained or prompted on
the distribution it has actually seen, it gets better at that distribution and
**worse at the ones it hasn't** — which are exactly the situations that invoke
it. The generalist is only ever called when the specialist path has failed or
found nothing. Optimising it against observed traffic optimises it against the
wrong sample.

> **The generalist's floor matters more than its ceiling.** Everything that
> narrows the floor to raise the ceiling is a bad trade for a recovery path.

Name this in the report. It is the kind of second-order failure that a
supervisor will respect being anticipated, and it is invisible in any benchmark
whose distribution is fixed.

## 3. So what *does* get better?

Split the question along the survey's own axis (2507.21046, "what to evolve":
Models · Context · Tools · Architecture). Alita-G evolves **Tools only** — its
master agent is frozen; all accumulated capability lives in the MCP Box. That
is worth stating plainly, because it is a deliberate and defensible choice, and
this design should keep most of it.

| Layer | Evolves? | Mechanism | Reversible? | Local cost |
|---|---|---|---|---|
| **Capability library** | **Yes — primary** | admit / promote / demote / retire capsules | **Yes** — retire un-registers | disk + index |
| **Context / memory** | Yes — secondary | accumulated evidence, prior runs, applicability scoping | Yes — evict | RAM, context window |
| **Generalist weights** | **No** | — | **No** | GPU-bound; see `24-` |
| **The referee** (gate, registry, verifier) | **Never** | — | — | — |

**The generalist gets better by having more admissible capabilities to reach
for — not by changing.** That is not a hedge. It is the same claim capsules
already make: capability is external, declared, and checkable, so it can be
added *and withdrawn*. Weight updates cannot be withdrawn; a capsule can.

This also keeps the safety story from `17-` §5.4 intact and makes it sharper by
separating two things that note conflated:

> **The actor may improve. The referee may not.**
> A generated capsule may never modify the admission gate, the registry, or the
> verifier. Everything else — which capabilities exist, which are admissible,
> which are preferred — is allowed to move, because all of it is reversible.

⚠ **Amended — do not contrast this against DGM as if DGM freezes nothing**
(`28-` §6.1). DGM's exploration process is already fixed and unmodifiable
(line 295), and the paper itself proposes "an unmodifiable part of the system to
be able to evaluate at halt the rest" as future work (line 642). The real
contrast is narrower and survives scrutiny: in DGM, **improvement and
irreversibility arrive together** — a self-modification is a new agent in the
archive, and there is no mechanism to withdraw a capability once it has shaped a
lineage. Here they are deliberately separated: capability is added and
*withdrawn* through the library, and what is frozen is the thing that decides
admission.

## 4. This is where Cordis earns its place in the report

Note `20-` §7.4 established: Cordis makes effects **reversible**, capsules make
them **reviewable**, and reversal is *observational, not physical* — retiring a
capsule un-registers it and does not un-publish the evidence it produced.

Under §3 that stops being a technicality and becomes the design's load-bearing
property:

- An evolution step that is **reversible** can be taken speculatively, because
  it can be withdrawn when the distribution moves.
- An evolution step that is **irreversible** must be right in advance — which,
  for a non-stationary distribution, is not a guarantee anyone can give.

So the answer to "how do we decide how agents evolve" has a principled form
rather than a taste-based one:

> **Prefer the most reversible mechanism that achieves the improvement.**
> Library before context, context before weights, and never the referee.

And the honest caveat stays attached: reversal is observational. Retiring a bad
capsule stops it being selected; it does not retract the evidence it already
produced, or the downstream conclusions built on that evidence. **That is an
argument for admission being strict, not for retirement being sufficient** —
which is the whole thesis, arrived at from a different direction.

## 5. Consequences for the routing question in `23-` §5

If the generalist is permanent, plan-time routing (`23-` §5) needs one addition:
**the generalist must remain reachable at run time for failure recovery**, even
though capability *acquisition* stays at plan time.

The distinction that resolves the tension with the freeze contract:

- **Acquisition is plan-time.** New capabilities enter the library before the
  freeze, are admitted, typed, and included in the frozen plan. This preserves
  the freeze thesis.
- **Recovery is run-time.** When a frozen node fails, the generalist may be
  invoked to *diagnose and re-plan* — but re-planning means producing a new
  frozen plan, not re-deriving capability inside the sealed one.

That reads as: **the generalist may reopen the contract; it may never
reinterpret it.** Which is exactly the principle
`STATUS-CORRECTED.md` extracted from the `final_report` deadlock — the Scheduler
may only execute gate IDs already frozen, and must not re-infer semantics at
runtime. The system already learned this lesson once, expensively. Reuse the
principle rather than rediscovering it.

## 6. A measurable version of the concern

The brief's worry — that we drift toward specialisation and lose recovery
capability — is testable, and it is a Track B metric nobody in the literature
reports:

| Metric | Definition | Why it matters |
|---|---|---|
| **Generality retention** | Generalist success rate on a held-out, deliberately off-distribution task set, measured periodically over a long run | Directly detects erosion of the recovery path |
| **Escalation rate over time** | Fraction of tasks the specialist path cannot serve | Should *fall* as the library matures; a rise signals distribution shift |
| **Recovery success rate** | Of escalated tasks, the fraction the generalist resolves | The floor that matters. Should be flat |
| **Library churn** | Admissions minus retirements per unit time | Distinguishes a growing library from a thrashing one |
| **Time-to-first-admissible** | On a novel gap, latency until an admissible capability exists | The cold-start cost `23-` §6 names |

The first is the important one, and it is cheap: **hold out a set of tasks the
system is never allowed to harvest capabilities from, and re-run them
periodically.** Generality retention is only measurable if something is
deliberately kept out of the training distribution — the same discipline as a
test set, applied to capability acquisition.

⚠ Note this cuts against Alita-G's protocol, where the Box is harvested from
the evaluation set (`21-` §6). Our version needs the opposite discipline, and
saying so is a concrete methodological improvement rather than a criticism.

## 7. Open questions this adds

- **Q13 — Is the generalist ever allowed to change?** Context and memory only,
  or eventually weights? If weights, what becomes of reversibility, and what is
  the local compute cost (`24-`)?
- **Q14 — What is deliberately held out?** Without a protected off-distribution
  task set, generality retention cannot be measured at all.
- **Q15 — Who arbitrates when specialist and generalist disagree?** Both may be
  able to serve a task; the specialist is cheaper, the generalist is broader.
- **Q16 — Does the specialist ever *lose* a capability?** Retirement is in the
  lifecycle (`19-`); nothing yet decides when to pull the trigger.

---

## 8. The paragraph this yields for the report

> Alita-G transforms a generalist into a domain expert, and treats that as the
> destination. That is sound when the task distribution is fixed. A research
> system running unattended for a week has no such guarantee: a failure or a
> discovery moves the distribution mid-run, and the only thing that can respond
> is a generalist that was never narrowed. **Specialisation, for us, is a
> reversible state rather than a destination** — and that is precisely why
> capability belongs in a library of declared, admissible, retirable contracts
> rather than in the agent. The actor may improve. The referee may not. And
> what improves the actor should be the most reversible mechanism that works.
