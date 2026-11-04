**Muk's directives for Capability Capsule, binding on every version.** Recorded 2026-09-22. Newest first. When a
document disagrees with this note, this note wins.

## What CC is for (a)

**CC makes capabilities easier to pick, verify, improve and remove.** Underneath all four is the schema itself: the
Declaration (one unified schema, with optional parts), and how the capability itself is held.

| Verb | Why it is easier with the schema |
|---|---|
| **Pick** | inputs and outputs are known. Deterministic finding on declared requirements cuts out most options, and only then does semantic matching choose among the survivors. **Selection is cheap because it is strict**, and the documents must name exactly which requirements are checked |
| **Verify** | everything is declared, so each check has a target: held-out tests against the declaration, observed effects against declared effects, and the hash proving the checked thing is the run thing |
| **Improve** | performance and trust are logged. Parents and children are known through lineage and dependency hashes |
| **Remove** | spatiotemporal composability |

## Rewrite the deck and report around a clean a to g (2026-09-22, evening)

- **a to g first and foremost**, in both the deck and the report. Rewrite in logical order rather than trimming the old.
- **Deck:** far fewer slides; key stats on the slides, not in speaker notes; drop the "thus" strips so diagrams are
  bigger; no "questions for the room"; advantages may take two slides, each citing its paper.
- **Show the records:** one slide with each record (Declaration, Verdict, Standing, Finding, Binding) and what goes in
  it: where the hash, parentage and provenance live, and what a Finding is for. The Declaration's fields in
  standardised `section.field` names.
- **Diagrams must be right:** the planner never writes to a capsule; capsules are assigned to DAG nodes when the plan
  is frozen, and then do their job.
- **Verify the real AI4Research selection:** it does filter deterministically first (types, effects, network, proof
  classes, trust, admission), never on preconditions, then one model call reads the full rows of every eligible
  capsule.
- Run through the slides to check they work.

## Build onto openJiuwen, reuse what exists; a schema that is useful (2026-09-22, late)

- The goal is to **build onto openJiuwen**: where something already exists (in agent-core, jiuwenswarm, Symphony or
  AI4Research), use it rather than design a new one. CC is a schema that exists **to be useful**.
- Verify claims where possible; **never overclaim**; make it easy to show, with a real example, why CC is better.

## Length, content and defensibility (2026-09-22, late)

- **No time target.** The deck is as long or short as needed to get through all primary content effectively, and no
  longer. Explain the key parts, what a to g requires, and the justifications with data.
- **Make no claim that cannot be defended.** Every number sourced; every design choice marked as design.
- **Show today's state:** what jiuwenswarm skills and capabilities look like right now, how Symphony works, how a
  skill, Symphony and a capsule differ, and why CC is better for the openJiuwen system and for AI4Research's role.

## Start extra small, and do not be too strict (2026-09-22, late)

- The new CC library should be **extra small** to begin with.
- CC must **not be so strict that it stops AI4Research reaching its goals**: soften CC's checks and let more things
  run under CC. **Resolve the judge issue** (semantic research outputs can only be judged, and unmeasured judges
  used to block them), and rewrite the report and deck to match.

## Fit openJiuwen's own structure (2026-09-22, night)

- Everything in the schema must fit openJiuwen appropriately, **as its structure is recorded in this vault**
  ([[openJiuwen Landscape]], `agent-core/Core 00-06`, `jiuwenswarm/Swarm 00-05`): use its layers, its names and its
  existing mechanisms, and say where each CC record and mechanism lives in it.

## The library is a version tree; CC exposes, RSI chooses (2026-09-22, night)

- The schema must be really good for version tracking. The library it serves is a **tree of capabilities**: branches,
  parents and children, so RSI can pick a child or a parent to branch from.
- **RSI has its own selection policy.** CC does not choose for RSI. CC **stores and exposes useful information**,
  efficiently, and marks as **optional** whatever it cannot guarantee.
- **The split of who knows what is vital**, and not all of it is CC's responsibility: part is RSI's. CC exposes data
  and lets it be tracked effectively.

## Gates, inherited tests, and exempt generalists (2026-09-22, night)

- **Node gates.** Explain how the schema serves the gate every node must pass, and who writes it. An admitted capsule
  should very likely pass the part of the gate that comes from its own declaration.
- **Tests travel with the capsule.** The tests a capsule was verified with are associated with it, so RSI can build a
  child and show it is better: it passes the parent's tests and more, including tests RSI authors.
- **`exempt`.** A schema field that exempts a capsule from the library's verification policies, so the generalist (the
  low-trust do-anything capsule) exists and RSI has material to improve on instead of everything failing unexplained.
  **More than one generalist may exist** (for example a Codex generalist and a Claude generalist). Exempt capsules are
  still bound by the plan's gates when used in AI4Research.

## Authors answer for state and undo; CC declares first, then checks (2026-09-22, evening)

- Capabilities are not inherently stateless: an MCP server over a live Postgres database changes state, and undo is
  not guaranteed. Spatiotemporal composability does not undo a context poisoned by bad tools that were later removed.
- **Responsibility goes to the author.** What happens inside a capability is the author's. The author must declare up
  front what it changes, whether it is idempotent, how it is undone (or that it cannot be), and what it touches.
  CC's liability is checking the declaration against what is observed, so problems are found before use, not the
  hard way.
- **Composition keys off the declared class:** pure and idempotent capabilities compose freely; compensable ones
  compose with the undo path tracked; irreversible or undeclared ones are gated.

## A capsule holds no task, and multiplicity is real (2026-09-22, afternoon)

- **A capsule is an abstraction** pulled from the library and told to do a task through its inputs and outputs. It
  never has tasks written into it: no step, node, sprint, workflow, stage, task type, upstream capsule or worker. That
  would make it specific instead of the general tool for the task. **CC is a schema.**
- **The planner does not hold a list of capsules and schedule them.** Plan steps say what is needed; the Binding and
  its invocations say what filled it. Keep the workflow mostly as it is.
- **The schema must handle real multiplicity:** the same capsule on many steps and in many sprints, several capsules
  in one step, fan-out over items, retries and fallbacks, and who owns each.

## The thesis

- CC is **a schema that serves the AI4Research workflow and its tools, built on agent-core in openJiuwen.**
- In the workflow, capabilities must be right, because each one feeds the following nodes. A wrong capability
  propagates errors.
- Other systems **observe**: Symphony's fingerprint, Skill Drift probing skills, Alita-G checking results. CC
  **declares**, because a declaration can be verified and found wrong.
- CC must ensure every admitted capability's effects match its declaration.

## a to g

- **Structure.** Key slides at the start answer each letter. The main body then elaborates each part and why. Never
  one compressed page.
- **(c) Position.** CC sits at the **planning, freeze and dispatch** stages of the workflow. Say where in the system
  and the code, and what it touches, with research behind it.
- **(d) Dependencies** means what **CC itself** depends on:
  - other systems (agent-core code, Symphony, the workflow's stages);
  - materials;
  - other teams and models.

  It is *not* a capability's internal dependencies. Those are handled inside the schema: pinned by default, or
  unpinned by an author who writes the dependency's purpose.
- **(e) Similar designs.** Symphony first, then other similar designs, then papers with similar traits.
- **(f) Better.** That leads into why CC is better.
- **(g) Feasibility.** Much of this has been done before, but never combined into one schema.

## How to write

- **Organise the rationale by function**: "we do X because of paper A; we do Y because of papers B and C". Never
  paper by paper.
- **Justify every component.** If it is not crucial to function, do not write it. Keep the worked example.
- **Focus on the schema** and how the schema supports tools, not the tools themselves.
- **Quote code lightly.** An abstract location such as "the planner's filter" is fine.
- **The content must answer these directly:**
  - How does the schema support self-improvement?
  - How does it help verification?
  - How does it help the librarian keep capsules versioned and structured, so we know what each is derived from?
  - Who carries past performance?
  - What carries trust?
  - What helps RSI?
- **Show the fields** of the schema and what they should be, including how the capability itself is held (skill,
  tool, MCP, A2A).
- **Say how capabilities are retrieved** in the proposed system, based on the research.
- **Include spatiotemporal composability.**

## Research base

- **Tuesday's (2026-09-15) papers:** Cordis, Alita-G, Beyond Task Completion, CoEvoSkills, Darwin Gödel Machine,
  AllocBench, SkillWeaver, SkillDAG.
- **The group's reading list:** Cognitive Admission Control, The Blind Curator, More Skills Worse Agents, SkillFuzz,
  SkillProbe, When Self-Evolution Backfires, AllocBench, Skill Drift Is Contract Violation.
- **Every cited paper is read in full.** Look deeper; no slop.

## Process

- **Record everything important in the tundle obby vault, organised.** Update existing notes; keep the vault clean.
- **Reviews use Sonnet** (not Haiku, not Opus), one at a time. Verify every finding in source.
- **Store research, materials and repos as markdown** in `capsule-openjiuwen/kb/` to build the documents from.
- **Close review agents when they are done.**

→ [[HANDOFF]], [[Capability Capsule]]
