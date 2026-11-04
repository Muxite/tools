# 32 — Stateful capabilities: declared state discipline, sagas, and Cordis

Written 2026-09-10 by the capability-capsule panel (pts/9), from the user's
design brief. Continues `30-` and `31-`.

> "Latest Claude MCP is stateless-first but implementation might not be
> stateless. Plugins and tools like this are used to control all sorts of things,
> like a PostgreSQL database. If agents are writing these plugins, they must know
> whether to enforce locks and when. So there could be a case where run A changes
> the state of an MCP server and breaks it — then we shouldn't use that MCP. This
> might also be a difficult task to check conformity of. Simple would be to
> restrict to only stateless or sequential items but that's a very major
> restriction, might cause a significant slowdown. Relevance of saga pattern,
> sounds a bit like Cordis."

---

## 1. The category error worth naming first

**Protocol statelessness is not effect statelessness**, and the distinction is
load-bearing.

MCP rev `2026-07-28` dropped the initialization handshake and became
stateless-first, carrying per-request `_meta` (`15-` §3-4). That is a statement
about **the transport**: each request is self-contained, so a server need not
remember a session.

It says nothing whatsoever about whether **the world behind the tool** has state.
An MCP server fronting PostgreSQL is stateless in exactly the sense that HTTP is
stateless in front of a bank.

⚠ This is a genuinely easy mistake to make in a report, and the report should
make the distinction explicitly, because it is the clearest single illustration
of what a capsule adds:

> MCP standardises how a capability is *reached*, and deliberately says nothing
> about what it *does* — its annotations are explicitly untrusted (`15-` §6).
> The capsule is where the state discipline gets declared.

## 2. The inversion: plugins should not decide when to lock

The user's framing — *"if agents are writing these plugins, they must know
whether to enforce locks and when"* — contains the problem and, inverted, the
answer.

**They shouldn't.** Asking a generated plugin to correctly implement locking is
asking the least trustworthy component in the system to get the hardest
concurrency problem right, silently, with no way to check that it did.

> **The capability declares its state discipline. The runtime derives the lock.**

That is the same inversion as the rest of the capsule thesis — declare, don't
decide — applied to concurrency. It is also the only version that is *checkable*:
a declaration can be validated against observed behaviour; a hand-rolled lock
inside generated code cannot.

## 3. State class: a gradient, not a binary

The user is right that "restrict to stateless or sequential" is too blunt.
Replace the binary with a declared class, and let the class *buy* parallelism:

| `state_class` | Meaning | Scheduler policy |
|---|---|---|
| `pure` | reads and writes no external state | unlimited parallelism |
| `read_only` | reads external state, writes none | parallel; may observe torn reads |
| `idempotent_write` | applying twice ≡ applying once | parallel and **retry-safe** |
| `transactional` | writes atomic and isolated by the resource itself | parallel; delegate to the resource's isolation level |
| `stateful_exclusive` | mutates shared state non-atomically | **exclusive lock on the named resource** |
| `session_bound` | only meaningful as an ordered call sequence | serialise the whole sequence; never interleave |

⚠ **This is not a new invention — it is the missing field the design docs
already specified.** `13-`/HANDOFF §5.1 lists **declared timing/idempotency** as
one of the four genuinely missing contract pieces (alongside the structured
`denies` list, the evolution contract, and the error contract). The design
anticipated this; the shipped schema dropped it. The user has arrived
independently at *why it mattered*, which is a much better argument for
reinstating it than "the design doc says so."

**Locking needs a resource identity, not just a class.** `stateful_exclusive`
alone is unschedulable — exclusive with respect to *what?* The declaration has to
name the resource:

```yaml
effects:
  write:
    state_class: stateful_exclusive
    resource: "postgres://analytics/public.experiments"
```

There is already a place to hang this: **`resource` is an existing capsule kind**
— 2 of the 80 registered capsules are resource capsules [verified, `07-`]. Resource
identity and resource health belong there.

### Why this is not the feared slowdown

Exclusivity costs parallelism only for the capabilities that declare it, and in a
research pipeline those are a minority. Literature discovery, evidence
transformation, synthesis, drafting — the bulk of the fleet — are `pure` or
`read_only`. The genuinely destructive, state-mutating operations are a small
set, and suggestively, they are **already the gated ones**: 11 of 28 routes are
gated specifically because they are destructive (`13-` R9). The correlation is
not proof that gated ≡ stateful, but it indicates the exclusive set is bounded
and already identified.

**So the declaration does not slow the system down — it is what lets everything
else run in parallel safely.** Today, without the declaration, the only safe
policy is to treat everything as exclusive.

## 4. Sagas, Cordis, and where each applies

The user's instinct that these are related is right, and the difference between
them is exactly the design boundary.

| | **Cordis revertible effects** | **Saga compensation** |
|---|---|---|
| Who supplies the undo | **the runtime holds the inverse** | **the developer writes it** |
| Exactness | exact inverse | *semantic* undo — an apology, not an unsend |
| Granularity | one component's context transformation | a business-level transaction |
| Isolation | non-interference is a proved property | **none** — intermediate states are visible |
| Applies when | the effect is inside the runtime's context | **the effect has escaped it** |

Cordis formalises *revertible effects, in which every context transformation
carries an inverse that the runtime holds*. That works precisely because the
effect is mediated — the runtime saw it and can undo it.

**A write to PostgreSQL is not mediated.** It left. And `20-` §7.4 already
established the general form of this for capsules: **reversal is observational,
not physical** — retiring a capsule does not un-publish the evidence it produced.

That is the saga situation exactly. So:

> **Where the effect stays inside the runtime, Cordis-style revertible effects
> apply and the substrate holds the inverse. Where the effect escapes to external
> state, saga-style compensation applies — and the capability must declare its
> compensating action as part of its contract.**

This yields a new contract field with real teeth:

```yaml
compensation:
  action: cap.experiments-rollback@v2
  scope: "rows written by this invocation"
  guarantees: semantic          # never claims exactness
```

And it is **checkable at admission**, which is the point:

- *Structural:* a capability declaring external `write` effects with
  `state_class` above `idempotent_write` **must** declare a compensation, or it
  is rejected. That is a new rejection reason —
  `COMPENSATION_UNDECLARED` — alongside the eight in `17-` §4.3.
- *Behavioural:* on a fixture resource, apply the capability, apply its
  compensation, and assert the resource satisfies its declared pre-state
  invariant.

**No system in the six-paper comparison has anything like this**, because none of
them models effects at all. It is a direct, defensible extension of the thesis
into the stateful case.

## 5. "How do you check conformity of that?" — the honest answer

The user is right that this is hard, and it exposes a **real limit of the
admission method in `31-` §4.1**.

⚠ **Held-out conformance replay tests a capability in isolation against fixed
inputs. It cannot see interaction failures.** A capability can score C=1.00 on
its own suite and still take a lock and never release it, exhaust a connection
pool, or leave a transaction open. **Silent rot is a per-tool property; state
corruption is a per-system one.**

Say this plainly in the report rather than letting a supervisor find it.

What *is* mechanically checkable, cheaply, on a fixture resource:

| Probe | Asserts | Catches |
|---|---|---|
| **Idempotency** | apply twice ≡ apply once | a false `idempotent_write` claim |
| **Isolation** | two concurrent invocations, invariants hold after both | a false `transactional`/parallel-safe claim |
| **Compensation** | apply → compensate → pre-state invariant holds | an unsound or missing undo |
| **Leak** | after return: no lock held, no open transaction, no retained connection | the exact "run A breaks the server" failure |
| **Sequence** | out-of-order calls are rejected, not silently accepted | a mis-declared `session_bound` |

These are ordinary, cheap, deterministic tests. They belong in the same cold-path
suite as the conformance replay (`31-` §4.2), and the **leak probe is the one
that directly targets the user's scenario**.

The residual, stated honestly: **a declared state class narrows the blast radius;
it does not eliminate it.** Same posture as `26-` §5 — admission is not
containment. A capability can still corrupt state in a way the fixture does not
model. What the declaration buys is that the corruption becomes *attributable*:
you know which capability claimed what, and the claim was checked.

## 6. When run A does break the server

The user's scenario needs a distinction `31-` does not yet make. Two different
objects are damaged, and they need separate actions:

1. **The capability** is retired with `retirement_reason: effect_violation` —
   security-class, so per `31-` §3 running plans **abort**.
2. **The resource is now degraded**, and no amount of retiring capabilities fixes
   it. It needs its own action: **resource quarantine**.

> Retiring the capability stops the bleeding. It does not heal the patient.

So resource capsules need health state, and the scheduler needs to treat a
quarantined resource as unavailable — which cascades: every capability whose
`effects.*.resource` names it becomes unschedulable until the resource is cleared.
That cascade is derivable *because the resource was declared*, which is another
argument for §3's resource identity.

**And this is where the taint model from `31-` §3 pays off.** Every artifact
produced by any capability touching that resource after the corrupting write is
suspect — not just artifacts from the offending capability. Resource-scoped taint
is wider than capability-scoped taint, and only the declaration makes it
computable.

## 7. Open questions

- **Q38 — Are locks advisory or enforced?** A declaration the runtime trusts, or
  a runtime that actually holds the lock? Enforced is the only version that
  survives a lying declaration — and generated capabilities are exactly the case
  where declarations may lie.
- **Q39 — What granularity is a resource?** Server, database, schema, table, row?
  Too coarse and everything serialises; too fine and the scheduler cannot reason
  about overlap.
- **Q40 — Who writes the compensation?** If the same generator writes the
  capability and its undo, both share the same misunderstanding — the CoEvoSkills
  isolation problem (`28-` §4), one level up.
- **Q41 — Does a fixture resource exist to test against?** All of §5 assumes one.
  Building it may be the single most valuable piece of test infrastructure here.
- **Q42 — What clears a resource quarantine?** Almost certainly a human, at least
  initially.
