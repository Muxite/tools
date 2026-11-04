**The second goal: agents that build, check and keep their own capabilities while research runs last days and weeks.**
It comes from the 2026-09-15 capsule report (`tundle/ai4research/capability-capsule/older/AI4Research Capability Capsule Report - Muk.docx`,
§1, §4, App. G). v2.1 had lost it; v2.2 restores it (schema §4.0, §4.12-4.16; v3 report §6, `kb/functions/3-improve.md`). Diagram:
`capsule-openjiuwen/merged/figures/F8.png`.

## Why the library is versioned, append-only and monotone

- **Versioned:** every change is a new hash, so a sprint can pin what it uses.
- **Append-only:** nothing is edited or deleted, and a retirement is a tombstone.
- **Monotone:** a new version passes everything its predecessor passed, plus new cases.

## Three clocks around one library

| Clock | Pace | Does | Writes |
|---|---|---|---|
| hot | every sprint; cheap; never waits | offer, bind or generalist, freeze, dispatch | Plan steps, Bindings, gap Findings |
| cold | when gaps recur, or an audit or duplicate starts an update; rare and costly | build decision, suite author, implementation, gate, librarian | Declarations, Verdicts; the librarian alone writes Standing |
| audit | on a schedule, by blast radius and staleness | replays held-out suites, drift probes, verifier audits, invariants on real outputs | Findings only; the librarian acts on them |

**The sprint is the reuse boundary.** A capsule admitted mid-sprint is used from the next sprint.

The hot path must work even if the cold path never admits anything.

## The generalist capsule

- **Binding.** Bound to a step nothing fits, instead of failing the plan with `UNSATISFIABLE_CAPSULE` as today
  (`apo_plan_compiler.py:626`). **Only** where every output type has a deterministic or reference gate; a judge-only
  step never binds it. It is admitted once, on a conformance suite of sample step contracts.
- **Contract and method.** Its contract comes from the Plan step. It works by writing a script and running it in the
  sandbox, so the work can be re-run.
- **Trust.** The lowest. Its claims are never marked supported, and the delivery lists every generalist step.
- **Writes.** Never the library. It leaves a gap Finding with its trajectory and cost.
- **Control.** It is controlled by the sprint's run contract:
  - `generalist_fallback`: on or off;
  - `authoring`: off, propose or build;
  - `generalist_cap`: the most generalist steps per plan.
- **Weights.** Fixed.

## The cold path: four roles, separate sessions

| Role | Owner | Never sees | Why |
|---|---|---|---|
| build decision | RSI | drafts | first-sight commitment 85-99% once code is involved (AllocBench) |
| suite author | verification | the generalist's work, drafts | tests written first beat overfit tools (Beyond Task Completion) |
| implementation | RSI | the suite; it gets admit or reject, capped | an uncapped loop learns the suite |
| gate | capsule layer, code | anything a capsule writes | the Darwin Gödel Machine gamed its checker's signal |

- **When a build happens.** Recurrence counts sprints, not nodes, with a threshold of 2. The build budget is a hard
  limit, never a price shown to the builder.
- **Four update options:**
  - a new version, which must be monotone;
  - a specialisation, where the parent stays;
  - a new capsule;
  - no build.
- **Retirement reason sets the policy** (one table, schema §4.7):
  - an effect violation aborts running steps and quarantines the capsule;
  - revoked provenance or a security revocation aborts, and every capsule built with it in context becomes suspect;
  - declining task success only demotes.
- **Records of the cold path.** "No build" and a spent build each leave a Finding. Replay details are hidden from the
  builder roles (`visibility: builder_hidden`). The suite is bound to the Declaration's `contract_hash`.
- **Exploration** (design). A quota lets inactive capsules be offered on steps that do not require certified ones, so they can
  earn evidence.

## Never grading itself

- **Protected components.** No capsule may write to the gate, the suites, the logs admission reads, or the record
  stores.
- **What the system may change:** the library and context, reversibly. Never model weights, and never the gate.
- **Unattended runs.** On an unattended server, every approval point becomes a rejection or a wait: imports, overlap
  picks, inverses, DEFER requests, and carriers that need approval. The run's `effect_ceiling` bounds everything.


## RSI is uniform, 2026-09-23

Once every stage applies capabilities ([[Every Stage Applies Capabilities]]), **RSI improves everything
through one mechanism** — a research operator, a stage's work, or a merged block — with no special case,
degenerate n = 1 capsules included.

**Merging is how RSI gets material.** A recurring, high-quality structure becomes a merged capsule with A
and B as `co_parents`; RSI can then branch from the block or from either member.
→ [[Overlap and Merge]], [[Versioning and A-prime]].

**The split of who knows what is unchanged and vital:** CC stores and exposes, efficiently, and marks as
optional whatever it cannot guarantee. **RSI chooses.** CC never sets RSI's policy. The join between the
two trees is `builder_ref` against `RsiTreeNode.parent_id`.

A child must pass the parent's suites plus its own — the monotone rule — and a *block* earns its own
quality record rather than inheriting one from its members ([[Quality Not Just Correctness]]).
