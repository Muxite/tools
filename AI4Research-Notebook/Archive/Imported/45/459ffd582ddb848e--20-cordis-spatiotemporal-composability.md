# 20 — Cordis: spatiotemporal composability, and what it changes

Read 2026-09-10 by the capability-capsule panel (pts/9).
⚠ **Gap flagged 2026-09-10 (note `30-` §4).** This note reads Cordis almost
entirely for its **temporal** half — revertible effects, retirement ordering,
Thm 70. The paper gives equal weight to **spatial** composability, and its
unifying result is explicitly about interleaving: *"the mediation induces an
observational equivalence up to which the effects of distinct components
interleave without disturbing one another."* That is the formal frame for
**concurrent agents sharing a capability library**, which is now a live design
question. The spatial half needs its own pass.

**arXiv 2608.25512** — *A Programming Paradigm for Spatiotemporal Composability*,
Yifan Shi (Peking University / DeepSeek-AI), Wei Zhang, Tianyi Cui.
PDF + text at `/home/muk/work/papers/2608.25512.{pdf,txt}`.

This is the formal substrate under the DeepSeek Harness. It matters more than
its tier-3 placement suggested, for three reasons: it argues our exact use case,
it supplies formal vocabulary we lack, and **it forces a correction to one claim
already in our comparison table.**

---

## 1. The paper argues our case, unprompted

§1.2.2 is titled **"Self-Evolving Agent Harnesses"** and is one of only two
motivating examples in the paper. Its scenario:

> *"A future harness may generate and deploy modifications to its own components
> while continuously serving requests. Model-synthesized reusable tools provide a
> narrower precursor to component-level self-modification."*

Its stated failure modes, without temporal composability:
- every self-modification forces a full restart, discarding process-local state;
- at self-modification frequency, cumulative unavailability is substantial and
  in-flight tasks are repeatedly disrupted;
- **"even worse, a faulty self-modification can disable the very process needed
  to recover."**

Without spatial composability:
- each module must detect and adapt to its dependencies appearing, disappearing
  or changing identity, by ad hoc means;
- **"a naive code-replacement strategy may silently break dependents or introduce
  circular dependencies that surface only at reload time."**

Two things follow for the deliverable.

**(a) The immutable-referee rule now has a citation.** `17-…` §5.4 proposes that
a generated capsule must never modify the admission gate, registry, or verifier.
"A faulty self-modification can disable the very process needed to recover" is
that argument, made independently, in the substrate paper of the harness we must
integrate with. Use it.

**(b) "Silently break dependents … surface only at reload time" is the same
phenomenon** as the reuse failure the presenter identified from 2604.00392 — a
change that produces no error at the moment it happens and a wrong outcome
later. One paper observes it at the *tool* level, the other at the *component*
level. That correspondence is worth a slide: it is not a quirk of LLM-generated
code, it is a known hazard of dynamic composition, and it has a known shape.

---

## 2. The two dimensions, defined

| Dimension | Definition (paper's own terms) | Static analogue |
|---|---|---|
| **Temporal** | *upon removal of a component, the modifications it made to the shared environment must be completely and safely reversed* — tracking every resource allocation, event registration and state mutation, and guaranteeing orderly reclamation | lexical scoping, RAII, bracket patterns |
| **Spatial** | *components must declare, discover and resolve their dependencies on one another in a structured and verifiable manner* — managing dependency topology and coordinating lifecycles as dependencies change | module import resolution |

The paper's framing: in the *static* setting both are solved problems; in the
*dynamic* setting — components arriving and departing at runtime — both get
much harder, because effects are no longer lexically scoped and dependencies can
appear, disappear, or **change identity** during execution.

That is precisely the setting a self-extending capsule library creates.

---

## 3. The mechanisms, and what each gives us

### 3.1 Effects and coeffects — the vocabulary we were missing
The paper's key move: **effects** formalize how a computation *modifies* its
environment; **coeffects** formalize what it *requires from* its environment.
Existing effect/coeffect systems are compile-time over lexically fixed scopes;
this paper lifts both to runtime.

Mapping onto what capsules already declare:

| Cordis | Capsule equivalent | State |
|---|---|---|
| effects | `effects` (read/write/execute/network/cost/risk) | declared, prose, unverified |
| coeffects | `contract.preconditions`, `bindings`, `composition.requires_after` | declared, partially checked |

**We have the two halves and no name for the pair.** Adopting the
effect/coeffect vocabulary costs nothing, connects the design to an established
literature, and — critically — is the *same vocabulary the target harness uses*.

### 3.2 Revertible effects → the retirement mechanism, formalized
*"Every context transformation carries an explicit inverse that the runtime
holds."* Tracked effects are reverted in **LIFO order**; unloading a parent
**cascades to its children** because instantiation is itself a tracked effect of
the parent.

This is the real answer to `19-…` §4's `retired` state. Retirement is **not**
"set a status field to retired". It is *running the inverse*. And cascade means
retiring a capsule that others were composed on top of is well-defined rather
than a dangling-reference hunt.

### 3.3 Reactive coeffects → temporal validity, solved differently than expected
A component declares required coeffects as a specification; **every context
change is classified against that specification as activating, deactivating, or
neutral**, and that classification drives the component's activation and
deactivation.

`19-…` §6 framed the temporal problem as *"a composition that was valid may
silently expire."* Cordis's answer is that **it does not silently expire — it
deactivates.** The dependent goes out of service automatically when what it
depends on goes away.

That is a stronger guarantee than the periodic regress probe I proposed, and the
two are complementary: reactive coeffects prevent *structural* breakage
(the dependency is gone), the regress probe catches *semantic* breakage
(the dependency is still there but now behaves differently). **Both are needed,
and saying why is a good slide.**

### 3.4 The fiber lifecycle — a state machine to copy rather than invent
A component instance is a **fiber**: an *inertial* state machine over
`LOADING / ACTIVE / UNLOADING / INACTIVE`. Inertial means **once a transition
begins it runs to completion before the system responds to a target-state
change** — reload and unload chain into each other rather than interleaving.

`19-…` §4.1 proposes a capsule lifecycle
(`proposed → draft → probationary → stable → deprecated → retired`). These are
different axes and should not be conflated:

- **Cordis fiber state** = *is this capability currently mounted and serving?*
- **Capsule lifecycle state** = *has this capability earned the right to be
  mounted at all?*

Capsule lifecycle is the **admission** axis; fiber state is the **runtime** axis.
A `probationary` capsule is one whose fiber may go ACTIVE but under attenuated
capabilities (§3.5). Keeping the two axes separate is the cleanest way to
explain how capsules sit on top of the harness rather than duplicating it.

### 3.5 Capability-based access control — the admission gate, in the substrate
§6.3 is the most directly relevant passage in the paper:

> *"A component can only access dependencies it has declared; an undeclared
> access raises an error… The `inject` declaration acts as a capability request,
> and the context proxy acts as a capability mediator. Since these requests are
> declared statically, **the complete set of proxy-mediated capabilities a
> component requires is known before it runs, letting the orchestrator review and
> approve them at load time rather than discovering accesses as they happen.**"*

That is the capsule admission thesis, stated as a property of the runtime.
The consequences for our design are large and mostly good:

1. **Undeclared coeffect access already fails.** The `EFFECT_UNDECLARED` check
   proposed in `17-…` §4.3 has partial enforcement in the substrate for the
   *coeffect* half. Our contribution narrows to the **effect** half (what it
   writes/executes/reaches), which the runtime does not classify semantically.
2. **Interception gives us the effect ceiling for free.** Access-control metadata
   is carried by the context; the provider checks each call; an orchestrator can
   constrain any component's access *without modifying the provider*, and it can
   be installed or removed at runtime **without triggering a reload**. That is
   exactly the mechanism for capping a `probationary` capsule's effects and
   lifting the cap on promotion.
3. **Sandboxing is explicitly out of scope for the language level.** The paper
   states that language-level access control is insufficient for untrusted code
   and requires an external execution boundary, with the untrusted component
   reaching host dependencies through a bridge whose host-side fiber can be
   **attenuated**. Generated capsules are untrusted code by definition, so this
   is the honest architecture: capsule + bridge + attenuated fiber, not capsule
   alone.

---

## 4. ⚠ Correction required to our comparison table

`16-…` §3 currently says, of the "Effects declared?" row: MCP ❌, A2A ❌,
capsule ✅. Read strictly against dsh/Cordis that is **misleading**, and the
supervisor could puncture it.

Cordis models effects **and** coeffects, formally, with a runtime, a calculus, and
metatheory carrying composability from one component to a whole system. On the
formal treatment of effects it is **ahead of** the capsule design, not behind it.

The corrected distinction:

| | Cordis / dsh | Capability capsule |
|---|---|---|
| Effects modelled for | **composability** — so they can be reverted and interleaved without interference | **admissibility** — so they can be reviewed, capped, and refused |
| Effect content | structural: allocations, registrations, mutations, dependency bindings | semantic: what it reads/writes/executes/reaches, cost, risk |
| Question answered | *can this be cleanly removed and safely composed?* | *should this be allowed to run at all, and what will it do to my evidence?* |
| Verification | type system + runtime tracking | contract pre/post/invariants + evidence |

So the honest line for the report:

> **Cordis makes effects reversible. Capsules make effects reviewable. Neither
> substitutes for the other — and a self-extending system needs both.**

That is a better claim than the original anyway: it is defensible, it is
specific, and it positions capsules as *complementary to the harness they must
plug into* rather than as a competing effect system.

---

## 5. Design changes this forces

1. **Adopt effect/coeffect vocabulary** in the capsule contract. Rename nothing
   yet; add the mapping (§3.1) to the report so the two systems are legible
   together.
2. **Retirement = run the inverse**, not a status flag (§3.2). Rewrite `19-…`
   §4.2 `retire()` accordingly.
3. **Two lifecycle axes, kept separate** (§3.4): admission state (capsule) vs
   fiber state (runtime). Do not merge them.
4. **Probationary effect capping via interception** (§3.5.2) — a concrete,
   already-supported mechanism rather than a proposal.
5. **Both breakage checks** (§3.3): reactive coeffects for structural, regress
   probes for semantic. Neither alone is sufficient.
6. **Generated capsules are untrusted code** → the architecture is
   capsule + external sandbox bridge + attenuated fiber (§3.5.3), not
   capsule alone. This should be stated in the safety envelope.
7. **Correct the comparison table** (§4) before it reaches a slide.

---

## 6. Where it belongs in the deliverable

- **Slide 9 (four layers)** — unchanged, but now with the Cordis citation under
  the seam layer.
- **Slide 12 (the divergence)** — must be **rewritten** per §4. "Nobody else
  models effects" is false. "Nobody else models effects *for admissibility*" is
  true and sharper.
- **New material for the safety slide** — the "faulty self-modification can
  disable the very process needed to recover" argument (§1a).
- **Backup slide** — the effect/coeffect mapping table (§3.1), for the
  supervisor question "how does this relate to what the harness already does?",
  which is now very likely to be asked.

---

## 7. The formal core (§2–§4), and what it changes

Read 2026-09-10: §2 preliminaries, §3.1 revertible effects, §3.2 reactive
coeffects, §3.3 context paradigm and observational equivalence, §3.4
independence and commutativity, §4.3.2–4.3.3 metatheory.

### 7.1 What an "effect" formally is — and why our `effects` block is not one

An effect is modelled as

```
Γ → Γ × (Γ → Γ)
```

— applied to the current context it yields the modified context **together with
an explicit inverse**. Tracking composes that inverse onto an accumulator:

```
∂Γ ≔ Γ × (Γ → Γ)          state γ, accumulator φ
track(f,g)(γ,φ) = (f(γ), φ ∘ g)
recover(γ,φ)    = (φ(γ), id)
```

Two results make this compositional rather than bookkeeping:

- **Thm 5** — `track` is a **monoid homomorphism**: tracking a sequence of
  effects one at a time equals tracking their composite at once. A whole
  component's effects can be reasoned about as one effect.
- **Twisted composition** — `(f₁,g₁) ∘ (f₂,g₂) = (f₁∘f₂, g₂∘g₁)`. Inverses
  accumulate in the opposite order. **LIFO teardown is an algebraic consequence,
  not an implementation choice.**
- **Soundness invariant** — `φ(γ) = γ₀`. Every state reached by tracked effects
  whose inverses revert them satisfies it, and recovery carries such a state back
  to the initial context.

> **The design consequence, and it is uncomfortable:** a capsule's `effects`
> block is a **prose label** — `write: artifacts/scientific/literature_discovery/`.
> A Cordis effect is a **transformation paired with its inverse**. These are not
> the same kind of object, and the gap between them is the real distance between
> the two systems. Saying "capsules declare effects" alongside Cordis without
> that caveat overstates what a capsule declaration is.

Two honest options for the report:
1. Keep `effects` as a *review* artifact (admissibility) and say so plainly —
   the §4 framing. **Recommended.**
2. Require generated capsules to supply inverses for their declared effects,
   making capsule effects revertible in Cordis's sense. Much stronger, much
   harder, and only tractable for context-level effects (§7.4).

### 7.2 Coeffect operations *are* effects — the unification

```
set(k,v) = σ ↦ (σ[k ↦ v],  λσ′. σ′ ∖ k)
```

A registration returns **its own revocation**. The paper states the synergy
directly: *"coeffect operations are effects, and effects are revertible."*

Satisfaction is a decidable predicate over a finite domain:

```
σ ⊧ d ≔ ∀k ∈ d. k ∈ dom(σ)
notify_d(σ,σ′) = activating | deactivating | neutral
```

And the key sentence for us:

> *"Since all mutations to σ pass through effect functions … changes to
> satisfaction are detectable at each effect boundary. This is the algebraic
> basis of reactivity: **the effect system guarantees that every coeffect change
> is observed.**"*

**Capsule reading:** a capsule's `bindings` + `contract.preconditions` are a
coeffect specification `d`. The harness can already classify every context change
against it. So "did this capsule's dependencies change under it?" is answerable
**by construction** — we do not need to build detection, only to decide policy.

### 7.3 Retirement safety is a theorem

**Theorem 70 (Ordering).** A fiber begins a transition only where its
dependencies are provided; and — the half that matters — *a provider withdraws a
binding only after every dependent that resolved it has deactivated*, with the
resolution a transition installs against not shifting under it (coherence).

> `19-…` §4.2 proposed that `retire()` "cascades to dependents". That is not a
> feature we need to design: **it is a proved property of the substrate.** The
> capsule layer decides *when* to retire; the harness guarantees retirement
> cannot happen out from under a live dependent.

### 7.4 ⚠ Observational equivalence — the most important limit in the paper

Recovery is **not** literal state restoration. §3.3.2 is explicit that this is an
idealization: `free` does not restore the heap layout `malloc` disturbed, and a
generative name is not restored by an inverse that discards it. Every equality in
§3 is read up to **observational equivalence** ≃ — two states are related when no
sequence of the key's operations distinguishes them.

**Reversal is observational, not physical.**

This is the sharpest finding in the whole reading, because of what it implies
for a *research* system. Cordis reverts **context** effects — registrations,
bindings, allocations, subscriptions. The effects that matter most in AI4Research
are exactly the ones outside that boundary:

| Effect | Revertible in Cordis's sense? |
|---|---|
| service registration, dependency binding | ✅ yes |
| in-process allocations, subscriptions | ✅ yes |
| **files written to `artifacts/`** | ❌ no |
| **papers ingested, research wiki mutated** | ❌ no |
| **network calls made to providers** | ❌ no |
| **claims recorded in the evidence ledger** | ❌ no |

> **Retiring a capsule un-registers it. It does not un-publish the evidence it
> produced.**

So there is a layer the composability substrate explicitly does not cover, and it
is precisely the layer capsules exist for. Concretely, `retire()` needs a second
half the harness cannot supply:

- **evidence quarantine** — mark every artifact produced by a retired capsule as
  `provenance_retired`, so downstream claims can be re-examined rather than
  silently inheriting a withdrawn capability's output;
- **compensation, not reversal** — for non-revertible effects the honest
  operation is a compensating action plus a record, never a claim of undo;
- **the evidence ledger is the only durable record** of what a retired capsule
  did, which raises `13-…` R6 from "nice feedback loop" to **a prerequisite for
  safe retirement**.

This also gives the deck a genuinely strong line:

> **Cordis can un-register a capability. Only the capsule layer can account for
> what it already did.**

### 7.5 Independence, and what `incompatible_with` is really asserting

To lift local guarantees to interleaved components, every transformation of one
must commute with every transformation of the other — **forward maps and yielded
inverses alike** (Def 42). Two results discharge this:

- **Thm 45** — operations at **distinct keys** are independent outright.
- **Lemma 66** — every sequence of steps is pairwise independent, because every
  key carries a commutativity **witness** in its coeffect (Def 46).

**Capsule reading, and a concrete improvement:** capsule
`composition.incompatible_with` is an unjustified assertion of
*non-independence*, hand-written, with no witness and no check. Cordis's
discipline is the opposite — independence is either structural (distinct keys) or
carries a proof witness.

> **Proposal:** require `incompatible_with` entries to name the shared resource
> or key that causes the conflict, rather than naming a capsule. That makes the
> claim checkable, makes it *derivable* from `effects` overlap for the common
> case, and stops a self-generating system from accumulating incompatibility
> assertions nobody can verify. Cheap, concrete, and directly traceable to §3.4.

### 7.6 What we may and may not claim

| Claim | Status |
|---|---|
| "We adopt the effect/coeffect **vocabulary**" | ✅ supported |
| "Retirement ordering is guaranteed by the substrate" | ✅ Thm 70 |
| "Every coeffect change is observed" | ✅ §3.2.2 |
| "Capsules declare effects like Cordis does" | ❌ **false** — §7.1 |
| "Retiring a capsule reverts its effects" | ❌ **false** — §7.4, observational only |
| "We adopt the **formalism**" | ❌ not yet — we have read the definitions and theorem statements, not verified the proofs, and have implemented none of it |

## 7. Reading status

**Read:** abstract, §1 (all), §2 preliminaries, §3.1–§3.4 (revertible effects,
reactive coeffects, context paradigm, observational equivalence, independence),
§4.3.2–§4.3.3 metatheory, §5.1.3 component lifecycle, §6.3 access control and
sandboxing, §6.4 language independence. Definitions and theorem *statements*
were read; **proofs were read only where the statement was load-bearing** (Thm 5,
7, 45, 70).

**Still unread:** §3.1.3 effect iterators in detail, §4.1–§4.2 the calculus and
its operational semantics, §5.1.1–5.1.2 effect/coeffect operations, §5.2
component loader and hot module replacement, §5.3 the Koishi case study, §6.1–6.2
and §6.5–6.7, §7 related work.

Nothing in §7 of this note depends on the unread parts. The honest claim remains
**"we adopt the vocabulary and cite the guarantees"**, not "we adopt the
formalism" — see §7.6.
