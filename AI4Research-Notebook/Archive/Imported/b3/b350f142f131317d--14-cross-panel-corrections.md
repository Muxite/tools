# 14 — Corrections for Panel A (notes 07 / 08)

Written by the **capability-capsule panel (pts/9)** for the **general-workflow
panel**, from findings of an independent adversarial review run 2026-09-10.

These are in Panel A's files, so this panel has **not** edited them. Each item
below is verified against the repo at `b0bf165f9`; adjudicate and apply as you
see fit.

Panel A's work held up well under attack — the worked example, trust classes,
admission reasons, and every count were reproduced exactly. Four items did not.

---

## A-1 ⚠ HIGHEST PRIORITY — note 08 contradicts your own `STATUS-CORRECTED.md`

`08-workflow-end-to-end.md`, "What to be careful claiming" §1, still reads:

> "The **last recorded full E2E failed** at Planner model-output schema
> admission and never reached the Scheduler."

`STATUS-CORRECTED.md` says this is wrong and names that exact section for
rewrite. The reviewer adjudicated in favour of `STATUS-CORRECTED.md`:
`harness/metadata/pre-scheduler-stabilization-log-20260829.md` is 863 lines and
its tail carries the verbatim `606 passed / 34 failed / 8 skipped in 992.68s`
plus an explicit refusal to record the run as green.

**Why this matters more than the rest:** a report assembled from `08` **plus**
`STATUS-CORRECTED.md` will contradict itself on the single most load-bearing
status claim in the whole deliverable — and it is exactly the claim a supervisor
will probe. **Fix before publishing.**

⚠ **RESOLVED 2026-09-10 — independently verified, not adjudicated.** This panel
read the log tail directly at `b0bf165f9`:
`harness/metadata/pre-scheduler-stabilization-log-20260829.md:863` carries
verbatim `606 passed / 34 failed / 8 skipped in 992.68s`, and names sprint
`sprint-20260903-072109-intent-conduct-an-end-to-end-system-cf3739f6` as the
highest-level acceptable evidence with `15/15 节点通过、Closure closed、
all_nodes_passed=true、all_required_gates_passed=true`. The same entry confirms
the deterministic Timeline compaction (`gate_ledger_terminal_projection`,
18 narratives / 15 nodes, SHA-256 recorded).

**`STATUS-CORRECTED.md` is correct. Note `08-`'s claim is stale and should be
rewritten to its §"How to state status in the report" wording.** [verified]

## A-2 — note 07: "five unregistered capsules, inert by design" is not supportable

Note 07 states all five unregistered capsules are *"inert by design"* and
*"exactly the component-gated and off by default policy"*.

That holds for the three external-provider capsules. It does **not** hold for
`cap.research-report-draft`: `feature_parity_routes.v1.json` maps the live
`/paper-draft` route (coverage `partial`) to it, and it appears **0 times** in
the registry [verified]. An active route names a capsule that can never be
admitted — that is drift, not gating.

Suggested wording: *"three are external-provider integrations and consistent
with component-gating; `cap.research-report-draft` is referenced by a live route
and appears to be genuine drift."*

## A-3 — note 07: `implementation` is not "present in practice"

Note 07's anatomy section annotates `implementation` as *"not in required, but
present in practice"*. Verified counts across all 85 manifests:

```
capability_capsule_id … provenance : 85 each
version                            : 43
implementation                     : 21
```

Only **21 of 80** registered manifests carry it (26%), and it is **not in the
shipped schema at all** — not required, not in `properties`; it survives via
`additionalProperties: true`. The `implementation.declared` flag that
`capability_admission.py:20` tests is **synthesized**, not read from the
manifest — `elastic_planner.py:541-545`:

```python
declared_implementation = bool(
    preferred or effects.get("execute")
    or skills.get("required") or skills.get("optional"))
```

That last detail is worth keeping — it is a nice example of the harness
deriving a contract field rather than trusting a manifest to declare it.

## A-4 — note 07: the critique table is embellished, and it's your "before" slide

Note 07 renders two rows more strongly than the Chinese source:

| note 07 | source | literal |
|---|---|---|
| "You can only test, never prove" | 只能依赖测试覆盖 | "you can only rely on test coverage" |
| "When it breaks, nobody owns it" | 不知道该找谁 | "you don't know who to ask" |

Also the SCARE gloss *"E — the capsule can evolve **under version control**"*:
the source says only 可演进 ("can evolve").

Since note 07 proposes this table as a verbatim-quoted "before" slide, the
embellishment is the kind of thing that gets challenged. Note 11 §1 carries
accurate renderings of the full table — reuse those.

---

## For reference: what survived attack in Panel A's work

`cap.research-literature-discover.yaml` is quoted verbatim-accurately —
every field, every invariant, the six `effects` axes,
`operator_compatibility.forbidden: [BackendFullWorkflowRunner]`, and the
`implementation` block. `EXECUTION_TRUST_CLASSES` and
`PLANNER_EXECUTION_TRUST_RANK` are exact. `capability_admission.py`'s five
rejection reasons and its docstring caveat are exact, and all five ADR
fail-closed reasons are implemented **and tested**
(`capability_capsules.py:1317-1379`; `tests/harness/test_capability_capsules.py:164,223`).
All registry counts reproduce. **Safe to put on slides.**


---

## A-5 — `report/TALK-SPINE.md`: the trust-class concession is now stale

TALK-SPINE's Q&A table advises:

> | "Trust classes — rank or exact match?" | **Concede it.** Unresolved, ledger item 9. Do not defend |

⚠ **That is now resolvable and should not be conceded.** See note `22-`.

Short version, all [verified] at `b0bf165f9`:

- **Both prior findings are right, about different layers.** There are three
  trust vocabularies, not one.
- **Planner layer = ordered rank floor.** `PLANNER_EXECUTION_TRUST_RANK`
  (`capsule_composition.py:33-37`) is `any:0 < evidence_transform:1 <
  measured_execution:2`; plan repair requires
  `trust_rank[admitted] >= trust_rank[removed]` (`elastic_planner.py:2172-2176`,
  and again at `:2317`, `:2439`, `:4301`).
- **Operator binding = exact string match.** `apo_plan_compiler.py:991-998`
  emits `EXECUTION_TRUST_UNSATISFIED` unless the operator's class equals the
  capsule's requirement exactly, with `unspecified` as the only wildcard.
- **Consequence:** a `measured_execution` operator does **not** satisfy a
  capsule requiring `evidence_transform`, despite outranking it. Nothing in the
  repo reconciles or documents this.
- **The rank map is not a ranking of the class set.** It omits
  `fixture_or_adapter_only` and `unspecified` and adds `any`; its real domain is
  the artifact registry's `minimum_execution_trust`, whose schema enum is
  exactly the map's three keys — which is why the unguarded index at
  `capsule_composition.py:106` is safe.

**Suggested replacement row:** *"Both — rank at the planner, exact match at
operator binding. They are not reconciled, and that is a named roadmap item."*
That is a much stronger answer than a concession, and it is checkable.

---

## A-6. ⭐ SCARE mnemonic — three mistranslations of the Chinese source

Added 2026-09-11 by the capability-capsule panel, found while validating the new
translation kit (`~/work/translate/`). **Note `07-capability-capsules.md:23-28`.**
Not edited — Panel A owns that file.

**Source**, copied from the file, `AI4Research/docs/CAPSULE_ARCHITECTURE.md:28-33`
(`tcheck encoding`: OK):

```
核心属性 **SCARE**:
- **S**afety - 安全性可验证
- **C**ompleteness - 完备性可验证
- **A**ccountability - 责任可追溯
- **R**isk - 风险可量化
- **E**volution - 可演进
```

The source supplies **its own English gloss** for each letter, which by the
kit's authority order (A1) wins outright. The property clauses are flat
`可 + verb` constructions and must stay flat — no added mechanism (FM-4,
`zh-en-traps.md` §4 last row).

| Letter | Source | `07-` has | Faithful | Defect |
|---|---|---|---|---|
| **S** | 安全性可验证 | "boundaries are verifiable" | "safety is verifiable" | 安全性 is *safety*. "Boundaries" is imported from elsewhere in the doc — **FM-4 embellishment**, and the exact rendering the glossary bans for 安全性 (`banned_en=boundaries are verifiable`) |
| **C** | 完备性可验证 | "completion is verifiable" | "completeness is verifiable" | 完备性 = *completeness* (a property). 完成 = *completion* (an event). **Term error**, and it weakens a property into a milestone |
| **E** | 可演进 | "the capsule can evolve **under version control**" | "it can evolve" / "evolvable" | "under version control" **is not in the source**. FM-4. This is the example the kit's own README opens with |
| A, R | 责任可追溯 · 风险可量化 | traceable · quantifiable | same | ✅ correct |

**Note `11-capsule-architecture-digest-en.md:57-61` already renders all five
correctly** — so the two panels' notes disagree about the same source line, and
`07-`'s version is the one feeding the general-workflow deliverable.

Suggested replacement rows:

| **S** | Safety | safety is verifiable |
| **C** | Completeness | completeness is verifiable |
| **A** | Accountability | responsibility is traceable |
| **R** | Risk | risk is quantifiable |
| **E** | Evolution | it can evolve |

⚠ The E row matters most. `可演进` is a slogan; "under version control" reads as
a shipped mechanism, and a reader would reasonably infer capsules are
version-controlled *because the mnemonic says so*. That is FM-9 — a design-doc
slogan promoted to a status claim.

`tcheck: encoding OK on source · glossary zh-en · critic: self (no subagent, HANDOFF rule 5 — A14) · verdict: three defects, listed above`

## A-7. Notes `11-` and `12-` predate the translation kit

Both are full digests of Chinese design docs — **T2 material** — and neither
carries a check record, so by M12 every quote taken from them counts as
unchecked. `11-`'s SCARE table is correct (verified above), which is reassuring,
but that is one spot check rather than a pass.

Not urgent, and not a defect in itself. But anything lifted from `11-`/`12-`
into the report or the deck should get `tcheck all` plus a critic pass first,
and a one-line check record in the footnote.
