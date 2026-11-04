**Not everything is needed early.** The ladder is organised by **what is running**, and by what each rung
lets us demonstrate. Recorded 2026-09-23, Muk's recommendation; M1 made concrete on 2026-09-24
([[Layer 2 Presentation]]). An older ladder organised by which schema clauses were implemented used the same
names M1 to M5 with different meanings; it was deleted, so do not cite it.

## One schema, progressively activated

The most important framing, and the one that answers the usual objection to staged schemas:

> **The schema is whole from day one. What is staged is how much of it is enforced.**

A field is declared in the schema from the start and sits **inert** until the component that reads it
exists. `needs.model` means nothing until routing reads it; `lineage` means nothing until RSI reads it;
`members[]` means nothing until the merge engine runs. So nothing is redesigned later, parts can be
missing while the system still demonstrably works, and the ladder describes **activation, not
construction**.

## The rungs

| | What is running at the end | What it proves |
|---|---|---|
| **M1** | **One node.** Minimal Declaration; the body's existing content hash checked before load; one predicate evaluator shared by the planner's filter and dispatch; one Binding per run; a minimal Verdict (pass, `decl_hash`, policy epoch) | the thing checked is the thing that ran, and a declared precondition is evaluable |
| **M2** | **A few chained nodes.** Output ports feeding input ports by declared type, the dispatch re-check on fresh state, a node gate, a gap Finding when nothing fits | a wrong capability is caught before it poisons the nodes downstream |
| **M3** | **A library (~10 capsules).** Verdict, Standing, versions, the librarian, held-out suites, judges calibrated by spot checks, quality as a rate | admission is cheap enough to run on every capsule |
| **M4** | **Overlap and merge.** Edge evidence, qualified pairs and structures, merged capsules with derived Declarations and pinned members, block-level suites, A/B/A-B coexisting | bigger blocks can be placed at higher quality, and RSI has material to improve. See [[Overlap and Merge]] |
| **M5** | **Spatiotemporal composability.** Install and uninstall mid-run, dependents notified, registrations undone in reverse | the library can change under a running system, *within stated limits* |

## Enforced at M1

`identity.name`, `identity.kind`, `identity.carrier`, `identity.body[].sha256`, `identity.summary`,
`ports.inputs[]`, `ports.outputs[]`, `needs.when[]`, `changes.effect_class`, `guarantees.checks[]`.

Declared but inert until their consumer exists: `lineage` (RSI, M4); `needs.model` and `budget`
(routing, M3); `guarantees.evals`/`acceptance` and the quality criterion (M3, see
[[Quality Not Just Correctness]]); `changes.provides`/`invariants`; `overlays`; `load_mode`; `exempt`;
and **`members[]` + `structure`** (the merge engine, M4).

**Why field count matters.** Every *enforced* field is work for the capsule's author and a check the gate
must run. A large required core discourages the adoption the whole design depends on.

## Off the ladder entirely

**Ranking, sorting and retrieval.** Symphony already does this and it works: `retrieval/`, `evaluation/`,
`discovery/`, `graph_engine.py`, `orchestration/`, `experience/`. CC decides *what Symphony may index*;
it does not rank. The seam is one protocol with two methods — see [[Where It Attaches]].

## M1, concretely (2026-09-24)

A fresh build on openJiuwen, not on the AI4Research harness. Three seed tools: **`count_spaces`** (text →
integer, pure) is the M1 task, run as one node; `regex` gives the planner a real choice; `parse_txt` (path →
text, `read_only`) feeds the first chained run, `parse_txt → count_spaces`, at **M2**. Planning is ports first
(Symphony's `plan()` at M3), execution is our own Kahn runner, versions are a linked list. Full design, work
packages and the loader: [[Layer 2 Presentation]].

## The lesson M1 answers, from the archive

`stellven/AI4Research/harness/capability-capsules/cap.research-claim-extract.yaml` declares
`preconditions: [{check: source_evidence_present, description: "..."}]`: **a name and a sentence of prose that
nothing evaluates.** The planner's hard filter never read preconditions; dispatch checked four fixed kinds; four
readers of one precondition gave four answers. Measured on 2026-09-24 (`merged/fleet_report.py`): **0 of 85**
manifests satisfy M1, though almost nothing is truly absent. Those manifests carry *more* fields than M1
enforces, mostly prose no machine reads. CC's core is **smaller**, just evaluable.

## How M1 to M5 will be judged

Four arms on real research tasks: (1) no library; (2) a library without admission; (3) a library curated by
observation; (4) a library under this schema. **It must beat arm 3, not only arm 1.** Known risks: effects are
seen only at tool-call level; provisional admission changes the freeze; declared ports change Symphony's graph;
over-blocking.

Related: [[Every Stage Applies Capabilities]], [[Overlap and Merge]], [[Quality Not Just Correctness]],
[[What openJiuwen Is Missing]], [[Symphony Flow]], [[Capability Capsule]].
