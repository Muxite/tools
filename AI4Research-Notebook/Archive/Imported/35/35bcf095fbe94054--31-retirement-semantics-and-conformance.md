# 31 — Retirement is not one thing: typed reasons, and how conformance is checked

Written 2026-09-10 by the capability-capsule panel (pts/9), from the user's
design brief. Continues `30-`.

> "Single writer should be done, there should be a lock on who can write. Not
> sure about policy if the capability is retired mid-run. Runs aren't free or
> that cheap, but retirement could be due to TC or other concerns. Then how is
> the conformance verified? Should retirement be a clear signal that the MCP
> isn't to be trusted? Could we attach **'why' metadata which changes the
> action**?"

**Yes — and it should be stronger than metadata.** The reason should be a *typed
field*, and the type should *select the policy*. That resolves the mid-run
question, which is otherwise unanswerable.

---

## 1. Settled: single writer, with two locks that are not the same lock

**Decision: the registry has a single writer.** An admission service serialises
all writes; agents propose, it commits. [decided by the user 2026-09-10]

Two clarifications worth recording, because conflating them causes bugs:

**A single writer does not remove the need for versioning.** It solves
*write–write* conflict. It does nothing about *read staleness*: a planner can
freeze a plan against version N while the writer is publishing N+1. The frozen
plan must still pin `capsule_id@version` (`30-` §3.2). Single-writer is
necessary and not sufficient.

**There are two distinct locks.**

| Lock | Scope | Prevents |
|---|---|---|
| **Registry write lock** | the registry as a whole | two admissions corrupting the index |
| **Gap lease** | one capability gap | two agents *building the same thing* (`30-` §3.4) |

The second is not a registry lock at all — the agents holding it are not writing
yet. Both are needed; neither substitutes for the other.

## 2. The core move: retirement is not one thing

Today `retired` is a single state doing at least six jobs, and that is exactly
why "what happens mid-run" has no answer. A capsule superseded by a better
version and a capsule caught doing undeclared network I/O are both "retired",
and they demand opposite responses.

Split it. **`retirement_reason` is a typed enum, and it selects the policy:**

| `retirement_reason` | Trust signal? | Plans running now | Evidence already produced | Future planning |
|---|---|---|---|---|
| `superseded` | **No** | continue | valid | prefer the successor |
| `deprecated` | **No** | continue | valid | not selectable |
| `redundant` | **No** | continue | valid | not selectable; points at survivor |
| `performance_regression` (TC) | weak | continue | valid | not selectable |
| `conformance_failed` | **Yes** | continue, **flag the run** | **taint downstream** | blocked |
| `effect_violation` | **Yes — security** | **abort + quarantine** | **taint + audit** | blocked, **lineage blocked** |
| `provenance_revoked` | **Yes — security** | **abort** | **taint whole lineage** | blocked, **lineage blocked** |

**Answering the user's question directly: retirement is *not* uniformly a signal
that the capability isn't to be trusted.** Four of the seven reasons carry no
trust implication at all. Only the bottom three do, and only the bottom two
justify destroying an expensive run.

## 3. Why "abort" is almost always the wrong action

The user's constraint — *runs aren't free or that cheap* — is the right one to
design against, and it points somewhere better than abort.

Recall `20-` §7.4: **reversal is observational, not physical.** Retiring a
capsule un-registers it; it does **not** un-publish the evidence it already
produced. So aborting a run buys almost nothing: the suspect artifacts are
already written, and killing the run merely means you also lose the good ones.

The useful action is not stopping. It is **taint propagation**:

> Mark every artifact downstream of the retired capsule's outputs as suspect,
> and let the run finish.

This is strictly more informative than an abort and strictly cheaper. A report
you know to distrust in three specific places is worth far more than no report.

**And the project already has the vocabulary for it.** The six-state result enum
— `PASS`, `PASS_WITH_KNOWN_LIMITATIONS`, `FAIL`, `NOT_TESTED`,
`ENVIRONMENT_BLOCKED`, `NOT_AVAILABLE` — means a run whose capsule was retired
for conformance mid-flight lands naturally as **`PASS_WITH_KNOWN_LIMITATIONS`
plus a taint record naming the capsule, the version, and the reason.** No new
vocabulary needed.

This is also, precisely, what the team already did once by hand: they read the
evidence, found the gate had failed, and **retracted their own passing run**
(`STATUS-CORRECTED.md`). Typed retirement reasons plus taint propagation is that
incident turned into a mechanism.

**The two exceptions that do justify abort** are `effect_violation` and
`provenance_revoked`, and for the same reason: they are not quality events, they
are *security* events (`26-` §4). A capability doing undeclared things, or one
whose generating lineage is compromised, is an active hazard for as long as the
run continues — and under multi-day autonomous operation that is a long time.
Cost stops being the deciding factor when the failure is adversarial.

## 4. "Then how is the conformance verified?"

Two different times, by two different mechanisms. Conflating them is why this
looks harder than it is.

### 4.1 At admission — the held-out replay

This is 2604.00392's own method, and the paper effectively hands over the
protocol (`29-`):

- preserve the capability's source at admission;
- replay it against a **held-out conformance suite for the capability it claims
  to implement** — not for the task that produced it;
- their suites are modest: five or six hidden unit inputs plus five or six
  adversarial probes, **median 11 inputs per tool**;
- score per-tool correctness `C`; admit only on a passing threshold.

Two methodological requirements, both non-negotiable, both borrowed:

1. **The suite must be held out.** The generator never sees it, or the
   capability is fitted to it and the measurement is worthless. This is the
   entire reason 2604.00392's 96.8% is credible.
2. **The suite must not be authored by the generator.** CoEvoSkills' surrogate
   verifier is *"a separate LLM session without inheriting the generator's
   biases"* (`28-` §4). Same session writing both code and tests produces tests
   that agree with the code.

### 4.2 After admission — the suite becomes a regression suite

This is the part that actually triggers retirement, and nobody in the six papers
does it. It is also nearly free, because **admission already built the asset**:

> The held-out conformance suite written to admit a capability is re-run against
> it on the cold path, between runs, for as long as it stays in the library.

A capability that passed at admission and fails later gets
`retirement_reason: conformance_failed`. That is *regression testing for
capabilities*, and it is exactly what 2604.00392 prescribes — its closing
recommendation is an audit schema of verifier coverage, reuse decomposition and
held-out conformance, emitted **"between releases."**

It also fits the cost shape from `24-` §3: admission is expensive and rare,
selection is cheap and constant, and re-verification is cold-path work on a
server that has idle capacity between runs.

### 4.3 The other three triggers

Conformance replay is one of four ways a capsule can lose standing:

| Trigger | Detects | Cost | Reason emitted |
|---|---|---|---|
| **Conformance replay** (cold path) | drift, rot, environment change | cheap, batched | `conformance_failed` |
| **Invariant monitoring** (runtime) | declared invariants violated on real outputs | varies — cheap for structural invariants | `conformance_failed` |
| **Effect divergence** (runtime) | observed effects ∉ declared effects | needs instrumentation | `effect_violation` |
| **Evidence ledger** (`13-` R6) | task-completion decline over N invocations | free, it is already recorded | `performance_regression` |

The fourth is the "TC" case the user named — and it is deliberately the weakest
signal, because task completion is exactly the signal 2604.00392 showed cannot
see silent rot. **A capability failing on TC should be demoted before it is
retired**; a capability failing conformance should be retired directly. That
asymmetry is the whole thesis, expressed as a policy.

## 5. What the "why" field has to carry

Not a free-text string. For the policy table in §2 to be machine-actionable:

```yaml
retirement:
  reason: conformance_failed        # the typed enum — selects policy
  detected_by: conformance_replay   # which of the four triggers fired
  detected_at: 2026-09-10T14:22:03Z
  evidence_ref: <ledger record id>  # the failing run, replayable
  supersedes_with: cap.x@v3         # required iff reason is superseded/redundant
  taint_scope: downstream           # none | outputs | downstream | lineage
  lineage_id: <generating trajectory id>   # required for provenance_revoked
```

`taint_scope` is the field that does the work at run time, and it is derivable
from `reason` — so it should be *validated against* the reason rather than set
independently, or the two drift apart.

**And a retirement record is itself append-only.** Under `30-`'s discipline, a
retirement is a new version publishing beside the source, never an edit. That is
what lets a frozen plan holding `cap.x@v2` keep resolving while `cap.x` is
retired for new planning.

## 6. Open questions

- **Q33 — Who may retire?** The admission service on evidence, an operator, or
  an agent? `effect_violation` should probably be automatic and immediate;
  `deprecated` is a human call.
- **Q34 — Is taint transitive across runs?** If run A produced a tainted
  artifact and run B consumed it, B's outputs are tainted too. That needs
  artifact lineage, which the evidence ledger may or may not carry.
- **Q35 — Can a retirement be reversed?** A conformance failure caused by a
  transient environment fault is not the capability's fault. Reinstatement needs
  its own gate, or `ENVIRONMENT_BLOCKED` needs to be distinguishable from
  `FAIL` at replay time — the six-state enum already makes that distinction, so
  use it.
- **Q36 — How often does conformance replay run?** Per commit, nightly, on
  library change? Cost is low but not zero, and it scales with library size.
- **Q37 — What is the admission threshold on `C`?** 2604.00392 reports C=0.00 vs
  C=1.00 as a sharp split, but a threshold policy still has to be chosen.
