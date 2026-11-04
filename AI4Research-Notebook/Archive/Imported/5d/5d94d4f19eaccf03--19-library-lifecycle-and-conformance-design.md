# 19 — Library lifecycle and conformance design

Written 2026-09-10 by the capability-capsule panel (pts/9), from the
presenter's reading of **2604.00392** plus repo verification.

This note turns that paper's diagnostic programme into a concrete design for
capability capsules, and specifies the component it implies but that does not
exist today: **a library interface**.

---

## 1. Why this failure mode is worse here than in the paper's setting

The paper's harm model is a tool that works once and degrades on reuse. Two
properties of AI4Research amplify that:

1. **Evidence compounds.** The research lifecycle is a chain —
   discover → ingest → extract → claim → verify → report. A tool that returns a
   plausible-but-wrong value at *discovery* does not fail; it **propagates**.
   Every downstream artifact inherits the error while carrying a valid-looking
   evidence trail. Task completion stays green the entire way.
2. **Long horizons hide it.** These runs are long, and reuse across stages is
   the point of the design. The window between a tool being synthesized and the
   reuse that exposes its overfitting is exactly where the system is least
   observable.

This is why the existing manifests already carry invariants like
*"Missing protocol parameters remain explicitly unresolved rather than being
silently invented"* and *"A completed result never falls back to fixtures,
synthetic candidates, or memory-only candidates."* Those invariants were written
against **hand-authored** capsules. Under self-generation, the entity writing
the invariant is the same entity that benefits from weakening it.

> **The design consequence:** invariants must be authored and checked by
> something that is not the generator, against inputs the generator did not
> choose. That is the whole argument for a held-out conformance suite.

---

## 2. The six probe roles, as a capsule conformance suite

The paper's session roles map onto per-capsule obligations. Proposal: **every
self-generated capsule must ship a conformance suite covering all six**, and the
suite is generated *from the manifest*, not from the implementation.

| Role | What it proves about a capsule | Concrete form here |
|---|---|---|
| **Seed** | baseline behaviour with existing capabilities only | run the parent task with the library frozen pre-generation |
| **Gap** | the capability was genuinely missing | admission **must** reject if an existing capsule already satisfies the contract → this *is* the dedupe check |
| **Variant** | it generalizes past the input that motivated it | **held-out inputs satisfying the declared `contract.inputs`, generated from the schema, never from the trajectory** |
| **Compose** | it chains | drive it through `composition.consumes/produces` against a real downstream capsule |
| **Regress** | earlier behaviour survives library change | re-run prior capsules' suites **after** admission — the probe nobody builds |
| **Adversarial** | edge cases the generator didn't consider | schema-boundary and malformed inputs; declared `preconditions` must reject rather than silently accept |

**Variant is the load-bearing one.** Overfitting to the input the agent had in
mind is defeated only by inputs the agent never saw. Generating them from
`contract.inputs.schema_ref` rather than from the trajectory is what makes this
mechanical — and it is another argument for the **manifest-first inversion**
(`18-…` §3.5): you cannot generate held-out inputs from a schema that was
reverse-engineered from the implementation.

**Regress is the one that justifies a library interface.** It is not a property
of a capsule; it is a property of *the library after a change*. Nothing can run
it except a component that owns the whole collection.

---

## 3. Measurement discipline

### 3.1 The separation, stated as a rule
**Task completion never counts as evidence about the library.** Two independent
verdicts per run: one for the answer, one for the artifact. Never a single
headline number.

### 3.2 Verifier coverage — the team already has the vocabulary
The paper's "report verifier coverage, exclude unverified tasks from TC claims"
maps **exactly** onto the project's existing six-state result enum
(`notes/research/07-benchmarks-evaluation.md`):

`PASS` · `PASS_WITH_KNOWN_LIMITATIONS` · `FAIL` · `NOT_TESTED` ·
`ENVIRONMENT_BLOCKED` · `NOT_AVAILABLE`

plus its explicit anti-copy rule: *"Never copy a green result to file formats,
platforms, providers, failure branches, or other variants that the journey did
not use."*

That rule **is** the conformance discipline, already written down, already
enforced. `NOT_TESTED` and `ENVIRONMENT_BLOCKED` being distinct from `FAIL` is
precisely what "exclude unverified from TC" requires.

> **Presentation point:** the project independently arrived at the measurement
> hygiene the paper argues for. Show the enum and the anti-copy rule as evidence
> of readiness, not as a coincidence.

### 3.3 Reuse decomposition
Raw reuse is not a success metric. Track separately:
`reuse_correct` · `reuse_incorrect` · `reuse_declined`
(selected but rejected by preconditions — a **good** outcome, and invisible
unless counted).

`reuse_incorrect` is the number that matters and the one a pass-rate benchmark
cannot see.

---

## 4. The Library Interface — the missing component

Verified absences in the current system:
- Registry statuses are **only** `stable` and `draft` [verified] — no
  probation, deprecation, or retirement.
- **No library-level dedupe.** The `dedup` machinery that exists is
  dispatch-level (`dispatch-dedup.json`) and session-level, not "is this capsule
  already in the library".
- **No retirement path at all.**
- Capsule quality has **no** feedback loop (`13-…` R6).

Under human authorship those absences are tolerable — the library grows slowly
and a person notices duplicates. Under self-generation they are the failure
mode.

### 4.1 Proposed lifecycle

```
        ┌──────────┐  conformance suite (§2) passes
        │ proposed │──────────────┐
        └────┬─────┘              ▼
   rejected  │             ┌──────────────┐
     ◀───────┘             │    draft     │  admitted, dry_run_only
                           └──────┬───────┘
                    N successful  │  observed invocations
                    + regress OK  ▼
                           ┌──────────────┐
                           │ probationary │  live, effects capped
                           └──────┬───────┘
                    sustained     │  conformance + no invariant violations
                                  ▼
                           ┌──────────────┐
                           │    stable    │
                           └──────┬───────┘
        superseded / conformance regression / disuse
                                  ▼
                           ┌──────────────┐
                           │  deprecated  │  selectable only by existing plans
                           └──────┬───────┘
                                  ▼
                           ┌──────────────┐
                           │   retired    │  tombstoned, never deleted
                           └──────────────┘
```

`probationary` is the state the current registry lacks and most needs: admitted
and live, but effect-capped and under measurement. It is where the variant and
adversarial probes actually earn their keep.

### 4.2 Operations

| Operation | Contract |
|---|---|
| `propose(manifest)` | validate against schema; run admission (§ existing 5 reasons + `17-…` §4.3 additions) |
| `dedupe(manifest)` | reject if an existing capsule's contract subsumes it — the **Gap** probe, enforced |
| `admit(manifest)` | register at `draft`; provenance mandatory |
| `promote(id)` | requires observed invocations + a passing regress probe **across the library**, not just self-checks |
| `demote(id)` | on conformance regression or invariant violation |
| `retire(id)` | **run the inverse** — retirement is effect reversal, not a status flag (see `20-…` §3.2); cascades to dependents; tombstone the record, never delete |
| `query(intent)` | typed/structural retrieval, not flat similarity (see `17-…` §4.5) |
| `audit()` | emit the observability trace (§5) |

**Deliberate asymmetry:** promotion requires library-wide evidence; demotion
requires only local evidence. Cheap to demote, expensive to promote. Under
self-generation that asymmetry is the safety property.

### 4.3 What already exists to build on
- Registry + admission gate + 5 fail-closed reasons — **exists, tested**
- `capsule_execution_gate.py` idempotency fingerprint + cooldown — reusable for
  rate-limiting generation
- `evidence_ledger.py` already accepts `capability_capsule_id` and
  `capsule_kind` (`13-…` R6 / O1) — the observability spine is half-built
- `capability_activation_proof.py` already runs **negative controls** — the
  adversarial probe has a precedent in-tree
- Six-state result enum — the verdict vocabulary

The library interface is mostly **wiring existing parts into a state machine**,
not new invention. Say that; it makes the proposal credible.

---

## 5. Observability

Adopt an audit record per capsule invocation, emitted through the existing
evidence ledger:

```
capsule_id · version · lifecycle_state · task_id · role(seed|gap|variant|…)
tools_available_before · selected · selection_reason
outcome · reuse_outcome(correct|incorrect|declined)
declared_effects · observed_effects · divergence
verifier_status · invariant_results · provenance{model, prompt_hash, parent_task}
```

`declared_effects` vs `observed_effects` is the row that makes
`EFFECT_UNDECLARED` measurable rather than aspirational.

**Borrow from dsh:** its invariant that anything model-visible must be
reconstructable from the session log is a stronger accountability guarantee than
declared effects alone, because it covers *inputs* too
(`notes/deepseek-harness/05-…` §2). For diagnosing an overfitted tool, the input
the generator saw is exactly what you need.

---

## 6. On spatiotemporal composability

The instinct is right, and it lands on the integration target rather than away
from it. Split the term:

- **Spatial** — which capsules may coexist and compose *at one moment*. Partly
  built: `composition.compatible_with` / `incompatible_with` / `requires_after`,
  typed search over 76 artifact types, and derived composite specs.
- **Temporal** — whether a composition that was valid **remains** valid after the
  library changes. **Nothing addresses this.** It is the Regress probe, promoted
  to a property of the system.

Under self-generation, temporal validity is the harder half: the library changes
continuously, so every prior composition is a standing claim that can silently
expire.

Two mechanisms worth pulling in, both from the harness capsules must integrate
with:

1. **Retirement as disposal.** dsh treats *registrations as effects* — every
   contribution returns a disposer, so unmounting is total and a live capability
   can be withdrawn mid-session (`notes/deepseek-harness/05-…` §2). That is a
   working answer to "how do you retire a capability without leaving dangling
   references", and it is the mechanism the `retired` state should be built on
   rather than reinvented.
2. **Tombstone, never delete.** dsh's durable data is immutable and versioned
   with adjacent-only migration. Retired capsules should follow the same rule so
   historical evidence stays interpretable — a research claim from six months
   ago must remain explicable even after the capsule that produced it is gone.

✅ **Now read** — see `20-cordis-spatiotemporal-composability.md`. Three
revisions to this section follow from it:

1. **Retirement is effect reversal**, not a status transition (§4.2 above,
   corrected).
2. **Temporal validity is not only a probe.** Cordis's reactive coeffects mean a
   dependent *deactivates* when what it depends on goes away, rather than
   silently expiring. That handles **structural** breakage; the regress probe
   handles **semantic** breakage (dependency still present, now behaves
   differently). Both are required, for different failure modes.
3. **Two lifecycle axes, kept separate**: the capsule lifecycle here is the
   *admission* axis; Cordis's fiber state machine
   (`LOADING/ACTIVE/UNLOADING/INACTIVE`) is the *runtime* axis. Do not merge
   them — a `probationary` capsule is one whose fiber may go ACTIVE under
   attenuated capabilities.

---

## 7. Effect on the deliverable

Additions to `18-…`:

- **§4.1 Track B** gains: verifier coverage %, reuse decomposition
  (correct/incorrect/declined), and effect divergence.
- **New slide, after the conformance gate (slot ~16b):** the library lifecycle
  state machine (§4.1). It is the most concrete artifact in Act II and answers
  "what would you actually build?" in one picture.
- **Reframe slide 17:** the headline experiment becomes *task success and library
  health measured separately, with the gate off then on* — sharper than the
  earlier phrasing.
- **New claim available:** *"the project already has the measurement vocabulary
  this requires"* — the six-state enum and anti-copy rule (§3.2). Cheap,
  verifiable, and it makes the proposal look ready rather than aspirational.
- **New open question for the closing slide:** should library management
  (promotion, dedupe, retirement) be a **capsule-kind of its own** — a
  `library` or `curator` capsule governed by the same contract discipline it
  enforces? Attractive symmetry, but it collides with the hard safety rule that
  a generated capsule must never modify the registry or the gate
  (`17-…` §5.4). **Resolution: the curator may be a capsule, but must be
  human-authored and permanently ineligible for self-modification.**
