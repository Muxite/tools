# 22 — `execution_trust`: rank or exact match? Both. (B3 / R1 resolved)

Written 2026-09-10 by the capability-capsule panel (pts/9).
All claims **[verified]** against `AI4Research` @ `b0bf165f9`, branch
`openJiuwen-Solar`, by reading the call sites named below.

`research/_RECONCILE.md` **R1** records two verified findings in conflict: is
`execution_trust` an ordered rank score, or an exact-match gate? The other
panel's `report/TALK-SPINE.md` currently advises conceding the point in Q&A as
unresolved.

**It is resolvable, and it should not be conceded.** Both findings are correct
about different layers. There are **three** trust vocabularies, and the two
semantics disagree exactly where they meet — which is itself a finding worth
putting in the report.

---

## 1. Three vocabularies

| Constant | Location | Kind | Members |
|---|---|---|---|
| `EXECUTION_TRUST_CLASSES` | `harness/lib/capsule_composition.py:27-32` | **unordered set** | `measured_execution`, `evidence_transform`, `fixture_or_adapter_only`, `unspecified` |
| `PHYSICAL_EXECUTION_TRUST_CLASSES` | `harness/lib/apo_plan_compiler.py:41-46` | **unordered set** | same four |
| `PLANNER_EXECUTION_TRUST_RANK` | `harness/lib/capsule_composition.py:33-37` | **ordered map** | `any: 0`, `evidence_transform: 1`, `measured_execution: 2` |

The rank map is **not** a ranking of the class set. It is missing
`fixture_or_adapter_only` and `unspecified`, and it adds `any`, which is not a
trust class at all. Its domain is a different field: the artifact-type
registry's `minimum_execution_trust` policy, whose schema enum
(`harness/schemas/planning/artifact-type-registry.v1.schema.json`) is exactly
`["any", "evidence_transform", "measured_execution"]`.

That alignment is why the unguarded lookup
`PLANNER_EXECUTION_TRUST_RANK[policy]` at `capsule_composition.py:106` cannot
raise `KeyError`: the schema constrains the domain to the map's keys. Every
*other* call site guards defensively (`if x not in trust_rank: return False`),
because those read capsule-authored values, which come from the wider class set.

**This is a good example for the report of a contract doing real work** — the
schema enum is what makes an unguarded dictionary index safe.

## 2. Where it behaves as a rank

Planner-side, trust is a **monotone floor: stronger satisfies weaker.**

- `capsule_composition.py:88-110` — `minimum_execution_trust_for_artifacts()`
  takes the **maximum** rank across a node's output artifact types, so a plan
  step inherits the strongest floor any of its outputs demands. Artifact types
  with no declared policy intentionally mean `any`.
- `elastic_planner.py:2172-2176` — plan repair rejects a substitution unless
  `trust_rank[admitted] >= trust_rank[removed]`.
- `elastic_planner.py:2317-2330` and `:2439-2452` — the same comparison for
  replacement-producer and surviving-producer repair paths, taking the
  strongest replacement by rank.
- `elastic_planner.py:4301-4315` — derives, per output artifact type, the set
  of trust classes whose rank is `>= ` the required minimum.

## 3. Where it behaves as an exact-match gate

Operator binding is **exact string equality**, with no ordering at all.

`harness/lib/apo_plan_compiler.py:991-998`:

```python
operator_trust = str(spec.get("execution_trust") or "unspecified")
if operator_trust not in PHYSICAL_EXECUTION_TRUST_CLASSES:
    reasons.append("OPERATOR_EXECUTION_TRUST_INVALID")
if required_execution_trust not in PHYSICAL_EXECUTION_TRUST_CLASSES:
    reasons.append("CAPSULE_EXECUTION_TRUST_INVALID")
elif (
    required_execution_trust != "unspecified"
    and operator_trust != required_execution_trust
):
    reasons.append("EXECUTION_TRUST_UNSATISFIED")
```

`unspecified` on the capsule side is a wildcard that disables the check. Any
other value requires the operator's class to match **exactly**.

Capsule-authored values are validated against the class set, not the rank map,
at `capsule_composition.py:405-415` and `elastic_planner.py:531`.

## 4. The consequence — the part worth reporting

**A `measured_execution` operator does not satisfy a capsule requiring
`evidence_transform`, even though the planner ranks it strictly higher.**

The planner reasons about trust as a ladder you may climb; the operator binder
treats it as a label you must match. Both are defensible in isolation:

- The planner's monotonicity is what makes plan repair sound — you can never
  repair a plan into something less trustworthy.
- Exact match at binding is arguably the safer default, since
  `fixture_or_adapter_only` is genuinely not comparable to the other classes
  (a fixture is not a weaker measurement, it is a different kind of thing),
  and a total order over the four would be a fiction.

But the two are not reconciled anywhere, and nothing in the repo documents the
split. A capsule author reading `PLANNER_EXECUTION_TRUST_RANK` would reasonably
expect stronger-satisfies-weaker at dispatch, and would be wrong.

**Report framing:** this is a roadmap item, not a defect. The fix is a design
decision the team has not made — either promote the rank to the binding layer
for the three orderable classes, or state explicitly in the schema that
`execution_trust` is a nominal label and remove the temptation of the rank map.
It is a good, small, concrete example of the report's larger theme: **the
contract vocabulary is real, and it is not yet uniform across the layers that
consume it.**

## 5. The floor is almost entirely unused

`harness/config/artifact-types.v1.json` — **76 artifact types, of which 1
declares `minimum_execution_trust`** [verified]:

```
schema:schemas/evidence/experiment_result.v1.schema.json
  minimum_execution_trust: measured_execution
  lineage_family: experiment
```

The other 75 omit the field and therefore default to `any`.

Do not report this as neglect. The one type that carries a floor is
**experiment results** — the single artifact class where "was this actually
measured, or transformed from something else?" is the question that matters.
The mechanism is built, wired into the planner's repair logic, and applied
where it earns its place.

The honest statement is that the trust floor is **implemented and deliberately
narrow**, and that its coverage is a policy decision the team can revisit as
self-generated capabilities arrive — which is precisely when a capsule of
unknown provenance producing an `experiment_result` becomes the interesting
case.

---

## 6. Disposition

- **B3 / `_RECONCILE.md` R1: resolved.** Not a contradiction — a layer split.
  Both prior findings stand.
- ⚠ `report/TALK-SPINE.md` advises conceding this in Q&A as unresolved. That
  advice is now stale, but the file belongs to the other panel — hand this note
  over rather than editing it. Added to `14-cross-panel-corrections.md` as A-5.
- For the capsule report: use it in the "what a capsule is today" section as
  evidence the contract vocabulary is genuinely enforced, and in the roadmap as
  a named, small, tractable inconsistency.
