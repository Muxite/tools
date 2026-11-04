**Presentation 3: what Muk does for the team as architect, 25 September to 31 October 2026.** Built 2026-09-25.
It is short: 12 slides, 12:45 planned. It is code-facing, and one slide cuts to the shared M1 design.

## The roles for this month (Muk, 2026-09-25)

| | Project role | Component (unchanged) |
|---|---|---|
| Muk | **architect**: leads the overall design, not the PRD; also Capability Capsule owner; also codes | CC |
| Xiaoyang | **primary coder** | routing |
| Ramika | **PRD** | verification |
| Saurav | **blue team** (蓝军, the attacking side in Chinese usage, where our side is red) | RSI |

- Everyone can code, but the primary coder writes the most.
- Muk's reasoning for the combination: owning CC means knowing what both verification and RSI need.

## What was made

| | Where |
|---|---|
| Deck | `tundle/ai4research/architecture/Architecture - Sep to Oct - Presentation 3.pptx`; source `capsule-openjiuwen/merged/pres3/` (`build_spec_p3.py` → `deck_p3.json` → `build_deck_p3.py`) |
| **Shared M1 design** (draft 0, for the team to edit in the week of 28 September) | `capsule-openjiuwen/team/M1-DESIGN.md`: what done means, the M1 run as a Mermaid diagram with agent-core plug-in points, modules and interfaces with proposed owners, M2 changes, records, review rules, a failure and blue-team table, decisions with defaults |
| **Shared schema explainer** (draft 0) | `capsule-openjiuwen/team/SCHEMA-EXPLAINED.md`: every field (what, why, writer and reader, from which milestone), a Mermaid diagram of where each section plugs in, the `count_spaces` seed as a whole example (it passes the M1 gate), and known mismatches between the JSON and the text |
| Diagram renderer | `team/render_mermaid.py` (Edge headless and Mermaid from jsDelivr). The Markdown is the source; the slides use `team/rendered/*.png` |

## Decisions

- **The roadmap is the layer 2 ladder**, dated as follows:
  - M1 in weeks 1–3 (28 September to 16 October);
  - M2 in week 4;
  - week 5 is M2 hardening and slack.
  - M3 is not expected this month; M3 to M5 are designed in, not built.
- **Three experiments:**
  - (1) parity and tamper;
  - (2) authoring cost, with one Declaration written by a teammate from the guide alone;
  - (3) blue-team drills on M1 (week 3) and on M2 (week 5).
- **Seam contract tests against the agent-core pin are deferred** (Muk): "lets worry about upstream later since it
  could break our system even if we tried to prepare."
- **The shared docs live as Markdown in a git repository.** Which repository the team shares is **not decided**. The
  `team/` folder is self-contained so it can be moved. `capsule-openjiuwen` has no remote.
- **Module owners are proposed, not agreed:** Muk takes the schema, gate, evaluator and seeds; Xiaoyang takes the
  store, skeleton, loader, CapsuleTool, dispatcher and records; the planner-binder is shared.

## Finding while writing the explainer

**`capsule.schema.json` and the §3.1 text of `SCHEMA.md` disagree field by field.** It is the same class of bug as
those found after 23 September.

- The JSON refuses unknown fields in `identity`, `ports`, `needs`, `changes`, `guarantees`, `budget` and each effect.
  So a Declaration written to the text is rejected; `identity.version_label` is an example.
- **8 mismatches are in fields M1 requires:**
  - `type` / `artifact_type`;
  - `outputs[].check` / `check_id`;
  - the precondition's shape (flat against nested);
  - four precondition fields missing from the JSON;
  - `on_unknown` `block` / `exclude`;
  - `evaluable_at: both`;
  - effect classes, five against four;
  - `carrier` / `code_id`.
- **16 more are elsewhere.**
- **One is inside the JSON itself:** `kind: judge` against `anchor: judged`.
- `state` and `test_aids` are a proposal, not a mismatch.

A first list said "ten". A Sonnet review found it incomplete (`check` / `check_id`, `external`, `injects`,
`provides`), and a full audit followed. The list is in SCHEMA-EXPLAINED §8. **WP0 fixes the M1 fields first; the
JSON wins until then.**

## Aligned with the M1 map, and diagrams standardised (2026-09-25, later)

Muk: "we have decided to do symphony in stage 1 and author a few capability capsules and a few gates". The M1 map
and [[Directives]] (2026-09-25) are the proposed workflow.

**Changed in the deck and both team docs (draft 1):**

- **Capsules run in intent and requirement compilation.** There are five M1 capsules (compile_intent,
  review_fidelity, compile_requirement, review_requirement, count_spaces) and three gates (decide_acceptance,
  contract acceptance, the step gate).
- **The semantic contract is central.**
- **The planner-binder and freeze are pass-throughs.** `regex` is dropped, because M1 has no selection.
- **One runner makes every capsule call.**
- **Symphony indexes from M1** through our provider; `plan()` waits for M3.
- **Observability exists from day one.**
- **The M1 schedule is re-planned:** it is wider than layer 2 assumed, so week 4 is the buffer.
- **A new ladder figure** is `merged/pres3/figs_p3.py`, which reuses layer 2's drawing.

**Where the maps differed, standardised to the better approach.** The criteria were the AI4Research workflow, the
Directives, and layer 2's code findings.

| Difference | Chosen | Why |
|---|---|---|
| M4 hot loop: "REQUEST: intake, requirement, ? requirement capsules" | the AI4Research stages, as in the M1 map | the Directive requires them in every diagram, and they match notes/08 and research/01-05 |
| M4 tags: request, freeze and delivery [M2]; dispatch [M4] | M1, or M1–M4 where a stage grows | all these stages run in M1 |
| Freeze output: "frozen DAG, one Binding per step" against "run contract" | **the run contract, holding one Binding per node**, plus the contract's hash | "run contract" is the workflow's name; the Binding stays the schema's per-node record |
| M4 call path: loader, CapsuleTool, `BEFORE_TOOL_CALL` rail, PermissionEngine | **the runner:** loader, CapsuleTool, PermissionEngine, run, Binding | the Directive's call sites; layer 2 found the workflow tool path skips rails, so the runner is the guard |
| "OBSERVATIONS" against "OBSERVABILITY" | observability [M1] | the Directive |
| Unnamed requirement-compilation capsules | `compile_requirement`, `review_requirement` (proposed) | the same names in every diagram |
| M1 map evaluator: "one evaluator, two callers" | "M1 caller: dispatch; M2 adds planning" | the planner is a pass-through in M1 |

**Source edits:**

- `merged/figures/big-picture/big_picture.py`: hot-loop blocks, tags and links. It was regenerated; a backup of
  the version before is in the session's temp folder.
- `m1_picture.py`: three labels. It was regenerated.

**The artifact pages are not republished yet.** (M1 map https://claude.ai/artifact/Xh72oWggRhSTc5WuuXh5GS; big
picture https://claude.ai/artifact/NFknMZ8ow37Tyc98tUTpAn.)

**Adversarial review (Sonnet), applied:**

- a stale schema render;
- the ladder figure;
- the parity point moved onto the slide;
- the lineage example: `relation` with `parent: null`. The text requires `relation` for a root, but no value fits,
  so this is logged in SCHEMA-EXPLAINED §8.

**Not applied:** the time budget. Muk asked for a short deck; the budget field is build metadata and did not drive
cuts.

## Final state (2026-09-25, end of day)

- **Final adversarial review (Sonnet):** one low finding, applied: "reviews within a day" was unsourced and is now
  "prompt design reviews". The review found no other problems: the code citations were checked against `e23806c1`;
  names, capsules, gates, owners and weeks are consistent across the deck, both docs and both maps; the builder
  reports no overflow.
- **Preview page:** https://claude.ai/artifact/J6fpUeAMeGfsE8ptk9fEnm. It shows the slide images with their speaker
  notes, planned times and the cut-away cue. It is private until Muk shares it.
- **High-resolution PNGs** of every deck (presentations 1 and 2, the post deck, Part A, presentation 3), the team
  diagrams, both maps (expanded and blackbox) and the standalone figures are in `huawei/slides-png/` (81 MB). They are
  kept out of the tundle because of their size; see its README.
- **Symphony tool capsules** were explained to Muk. Four checks keep non-skills out of Symphony's planning (the graph
  build, observations, skill-pack rendering, and the retrieval scanners). The cause is that jiuwenswarm executes plan
  nodes as skills. The recommendation is an additive upstream PR (configurable graph types; tool nodes in
  observations); a skill-wrapper adaptor is the fallback only. M1 needs neither.

## Maps republished, and the Opus review (2026-09-25, afternoon)

- **Republished in place:** M1 map https://claude.ai/artifact/Xh72oWggRhSTc5WuuXh5GS (v10) and big picture
  https://claude.ai/artifact/NFknMZ8ow37Tyc98tUTpAn (v9). Before overwriting, both live pages were read: neither
  had content the local sources lacked.
- **First review on Opus**, following Muk's new rule. It found no linkStyle or dangling-edge errors. It did find
  real gaps in the M4 map, all fixed:
  - the runner was drawn in the wrong order and in the wrong place. It now runs loader → CapsuleTool →
    PermissionEngine → run → Binding, as a shared service;
  - the run contract now holds one Binding per node, plus `semantic_contract_sha256`, and the runner appends
    invocations;
  - tags changed: admission and verifiers are M1–M3; library, freeze and delivery are M1–M4;
  - observability now takes gates and the request stage;
  - the repair loops and the reject/clarify path are drawn;
  - there is an evaluator;
  - a duplicate `SCH` id was renamed `SCHD`.
- **M1 map changes:**
  - runner links go to all four model capsules;
  - "runs this capsule" now starts from "run";
  - `semantic_contract_sha256` is named apart from the schema's `contract_hash`.
- **Design gap found, and a proposal (Muk to confirm).** Capsules in intent and requirement compilation run before
  freeze, when no Binding exists. Their invocations go to a **stage record keyed by run id and stage**, with the
  Binding's shape (`M1-DESIGN.md` §5, §8).
- **For Muk:** `Directives.md` contradicts itself. The 2026-09-25 section says "No capsule in delivery", then says
  the runner rule "Supersedes … 'no delivery capsule'". Both maps follow "no capsule in delivery".
- The page template moved to Mermaid 12 and ELK 1.0.0 (done in another session). The big map needs well over 30 s
  to lay out headless, so PNG captures use a 150 s budget.

## The PRD sets M1's boundaries; Muk designs the inside (2026-09-25, late)

- Muk: "PRD is gonna decide boundaries and stuff for m1 etc, so ill be designing how to structure the inside of m1
  and whats possible."
- **Deck:**
  - slide 2 has the new split;
  - slide 5 is now "Inside the boundaries: how I would structure M1 and M2";
  - the Ramika rows ask for the boundaries and acceptance criteria.
- **`M1-DESIGN.md`:** its "Where this sits" says the same.
- **M1 map** (v11): the "not in M1" box is now "OUTSIDE M1 · the PRD sets this boundary", and the header says so. The
  M4 map was not touched.
- **Settled with Muk:** the slides stay focused on his role in general; the component asks (PRD, routing,
  verification, RSI) are not a slide.
- **The AI4Research IR, checked in source (corrects what was first said):**
  - RequirementIR v2 (`solar.requirement_ir.v2`) is emitted by `harness/lib/requirement_compiler`;
  - `requirements[].check` must be a registered check id bound to an output (`semantic.py` `semantic_defects`:
    `UNKNOWN_CHECK`, `REQUIREMENT_CHECK_NOT_BOUND_OUTPUT`). It is not prose;
  - the standalone `schemas/requirement-ir.schema.json` describes v1 only, and is stale;
  - v2 carries its own `semantic_contract` field (`solar.requirement_semantics.v1`).
- **Still missing for M1:** typed want/given and the allowed capsule.
- **Undecided (Muk):** whether to adopt the schema files as data.

Related: [[Layer 2 Presentation]], [[Milestone Ladder]], [[Open Questions]], [[Directives]].
