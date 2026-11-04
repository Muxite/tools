# Materials: the sources the schema answers to

## Supervisor rulings (tundle notes 45 and 46; the chat of 2026-09-21 and 2026-09-22)

| Date | Ruling |
|---|---|
| 2026-09-18 | "CC is schema layer, it could be related to most models, including RSI, but the function of CC and RSI are totally different." The new system is built on openJiuwen, with its architecture aligned to openJiuwen. AI4Research itself is not a capsule. The earlier slides "don't restrict your thoughts" |
| 2026-09-21 | "CC is more of a scheme, and verifier is a tool. CC can use tools, but CC is not a tool." Verification covers the capability and system levels at each sprint. Capsules never change model weights. agent-core changes only where necessary |
| 2026-09-22 | No page or time limit: quality, logic and flow decide |

**The supervisor's slides (2026-09-18).** They are prior thinking, not a specification, but they give the team's
vocabulary:

- the formula: Capsule = Skill + Rules + Boundary + Assets + Data + Interfaces + Eval + Governance;
- the adjectives: self-contained, composable, verifiable, governable;
- the key sentence: "a unified contract lets the orchestrator understand only the interface, the constraints and the
  acceptance criteria, with no need to understand the capsule's internal implementation".

## The 2026-09-15 capsule report (Tuesday; tundle `AI4Research Capability Capsule Report - Muk.docx`)

**The goal.** Agents that build, check and keep their own capabilities while research runs last days and weeks. They
must be able to:

- explore the capability space;
- decide whether to use a skill, and which;
- decide whether to make, modify or retire one;
- implement and evaluate it;
- manage the library as it grows;
- trace a failure to its downstream impact;
- keep provenance.

**Rules R1-R6:**

- **R1** Using and building run at the same time, on separate clocks.
- **R2** Every sprint pins exact versions.
- **R3** Every capsule passes held-out tests of its own capability.
- **R4** Duplicates are rejected; close capsules are versioned.
- **R5** The check is independent of the builder, and cannot be written to by any capsule.
- **R6** The agent that decides never builds; builds follow recurrence.

**The design:**

- a generalist capsule for steps nothing fits;
- a cold path whose model roles run in separate sessions (build decision, suite author, implementation), plus a code
  gate;
- three loops around one library: hot, cold and audit;
- four-stage selection, where exact stages eliminate and embeddings only rank;
- an append-only, versioned library with monotone versions;
- protected components;
- unattended runs, where an approval request becomes a rejection.

## Teammates

| Who | Area | What they need from the schema |
|---|---|---|
| Saurav | RSI (builds and improves capabilities) | gap Findings with trajectories, typed rejections, drift Findings naming the broken assumption, lineage, a Declaration format to build against |
| Ramika | verification | the declared checks to run, held-out suites, measured judges, Bindings to trace a sprint failure to exact hashes |
| Xiaoyang | routing (models only) | `needs.model` constraints; the models each capsule's evidence covers |
