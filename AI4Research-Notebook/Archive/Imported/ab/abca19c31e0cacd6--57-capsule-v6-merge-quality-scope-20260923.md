# 57: Capability Capsule v6 — scope, overlap and merge, quality as a rate, schema v2.9 (2026-09-23)

Builds on note 56. Branch `schema-v2.1-overnight` in `capsule-openjiuwen`; not pushed, not committed yet.

## The thesis line everything now hangs off

> **A 能力胶囊 is flexible in form and strict in verification and quality assurance.**

Flexibility of form makes adoption cheap; strictness of verification makes flexibility safe. It opens
both deliverables.

## Muk's directions this session

- **Every stage applies capabilities.** In his words: *"this does not mean the whole workflow becomes a
  cap cap itself, but it means each stage can apply capabilities."* The unit is the **work a stage
  does**, not the stage. This **supersedes** the old "CC lives at three stages; intake, intent and
  requirement compilation never see capabilities" claim, which was corrected in `SCHEMA.md §0.5`,
  `kb/repos/ai4research-workflow.md`, `kb/report/00-front.md §2c` and the deck.
- **A capsule holds a set of capabilities; n = 1 is the degenerate case.** One schema with optional
  sections switching on by type, so the library places everything by the same rule.
- **Nothing that decides is ever a capsule.** Reconciling two of Muk's statements: a capsule may produce
  an **assessment**, never a **decision**. So faithfulness-of-IntentIR and `cap.research-claim-verify`
  stay legal; the gate, admission and the librarian never are. Enforced by the existing
  protected-components rule on **write access**, which is checkable where "is this judging?" is not.
- **Overlap and merge**, with **no split operation**. A, B and A-B all coexist; internals lock on merge.
- **Quality, not just correctness** — a rate over a window, with a declared minimum observation count.
- **One schema, progressively activated**: the schema is whole from day one; what is staged is how much
  is enforced. Answers the usual objection to staged schemas.
- **Cite the biggest company, one question each, spread across the whole deck** — framed as
  "inspiration from other software", which plays well at Huawei.
- **Show impacts beyond the three teammate features**, and show where the layer lands in code.
- **A diagram of what is in the library and what a capsule can be.**

## The central finding: `symphony/flow/` already implements most of the merge engine

Verified in source at agent-core `e23806c1`, and absent from all three `kb/repos/` notes:

| Proposed | Already built |
|---|---|
| a capsule holding a set with its own DAG | `ExperienceRecipe.combination_structure` — nodes, edges, direction, loop guards |
| merge on recurrence **and** quality | `qualified_edges(min_edge_support, min_edge_success_rate=0.8)` |
| **failing parts never merge** | grouping uses a trajectory's *successful* edges only; the docstring is explicit |
| the block graded as a block | `resolve_status_grade` → `candidate` / `verified` |
| A, B and A-B coexisting, versioned | immutable `recipes/<id>/vN.json`; `content_identity()` versions on real change, not counts |
| a gate before use | `PackageReviewGate.review_static()` — ten deterministic checks, then an isolated reviewer with no tools or filesystem |
| content-hashed packages | `CapabilityPackager` → `package_id = "cap-" + sha256[:12]` |

**What it lacks is exactly the schema:** no declaration on the block, no lineage to A and B, no held-out
test, members referenced by id rather than pinned by hash. Four gaps, and that is the whole of CC's
addition to it. This is now the strongest answer to (g).

**Two corrections to our own notes:** `SkillManifestParser` already reads `inputs`/`outputs` from
`SKILL.md` frontmatter (only `SkillUseRail` is blind); and the Symphony README's status table is stale —
retrieval is implemented, not 待迁入.

## The seven verified absences (the "why CC" evidence)

No effects/preconditions/guarantees on any carrier (`ToolCard` has only `parallel_safe`, `stateless`,
`idempotent`); no version on any carrier spec; no hash on any load path; no durable record of what was
installed (`_load_records` is an in-memory dict); no capability lineage outside `RsiTreeNode.parent_id`;
no gate keyed on a capability; no capability-aware model routing. Each verified in source.

## Deliverables

| | |
|---|---|
| Schema | `merged/SCHEMA.md` **v2.9** — new §0.7 (what is required when), §0.5 rewritten, new §4.9a (overlap and merge), §4.5c extended with quality as a rate, §4.10 gains the assess/decide line and the held-open question, milestone tags on §4.5b/4.5c/4.6/4.13a/4.14 |
| Deck | `merged/build_spec_v6.py` → `deck.json` → pptx. **34 slides, 18 figures** (v5: 34 slides, 9 figures). Builds with no layout warnings, planned 40:10 against a 50:00 max. The five evidence slides are imported from `build_spec.py` by title, so no printed number can drift |
| Report | 1844 lines, 26 figures. New chapters: §8 Merge, §10 Integration, §11 Impacts. §12.6 is the merge worked example on `intent → IntentIR → faithfulness`. §15 is the ladder. **The .docx build is pending: `tundlekit` refuses while PowerPoint is open** |
| Figures | `merged/figures/figs_v6.py` — 13 new: `stages`, `library`, `merge`, `quality`, `scope`, `gaps`, `reuse`, `decl`, `capsule-dag`, `compose-limits`, `mechanisms`, `impacts`, `attach`. `palette.py` gains a greyscale `MILESTONE` ramp and `badge()`, deliberately not a hue so it never competes with the stage colours |
| Vault | 12 new notes in `tundle/obby/`, 8 updated. Link-checked: no orphans, no broken links |

## The milestone ladder, redefined

M1 one node · M2 a few chained nodes · M3 a library (~10) · M4 overlap and merge · M5 composability.
Organised by **what is running**, not by which schema clauses are implemented — the old `Plan and
Phases` ladder is superseded and now points at `[[Milestone Ladder]]`.

**Off the ladder entirely:** ranking, sorting and retrieval. Symphony ships them and they work.

## Industry references

Verified this session: Google BigQuery materialized-view recommender (keep both forms), Microsoft Power
Automate Process Mining (who approves), NVIDIA TensorRT layer fusion (not every pair may merge), Amazon
Step Functions nested workflows (a block with its own graph, monotone versions), Google Bazel (pin
internals, rebuild on demand). Seven further candidate anchors are listed in `kb/materials/inspiration.md`
and **must be verified before they ship**. Three research agents were still fishing for more
non-AI precedent when this note was written.

## Open

- The `.docx` build, once PowerPoint is closed.
- Verification pass (Sonnet, one at a time) over the changed sections only.
- Folding in whatever the industry-research agents return.
- Nothing is committed yet.
