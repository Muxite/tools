Skills are the unit of capability. Symphony finds and chains them. Several evolution tracks improve them, and so does the harness itself. The mechanisms live in agent-core ([[Core 06 Evolution and Symphony]]). This note covers what the product turns on, and the defaults.

## Skills

A skill is a directory with a `SKILL.md`. Bundled skills are under `jiuwenswarm/resources/agent/workspace/skills/`, and include `agent-creator`, `plugin-creator`, `swarmskill-creator`, `skill-creator-normal` and `pptx-generator`. A **Swarm Skill**, also called a Team Skill, packages a successful team collaboration, often as a Swarmflow script. The **Swarm Skills Hub** (`swarmskills.openjiuwen.com`) is for searching, installing, remixing and publishing skills.

## Symphony, for many installed skills

> *"a tree for retrieval, a graph for orchestration."* — `docs/en/Symphony.md`

- **Skill Retrieval** builds a local tree index of installed skills and gives the agent directory-browsing tools, so it does not inject hundreds of skills into the prompt.
- **Skill Orchestration** builds a skill graph whose edges mean "this output can feed that input". It turns candidate skills into a **confirmable execution route**, and walks backwards to find upstream skills when an input is missing. In Cluster mode, the route can guide the Leader's dispatch.
- Orchestration improves from real usage, through a graph-evolution rail. See [[openJiuwen Landscape]].
- In the code, `jiuwenswarm/symphony/` is its **own sub-package**: `openjiuwen-skillsdispatch` 0.1.0, *"skill indexing, retrieval, and orchestration"*. It builds on agent-core's `openjiuwen.symphony`.

## Evolution tracks

| Track | Switch (default) | Writes | Approval |
|---|---|---|---|
| **Skill self-evolution** | `react.evolution.skill_evolution` (**false**) | an experience layer that is loaded with the skill. `SKILL.md` is rewritten only by an explicit `/evolve_rebuild` | Single Agent and Team Leader: user approval when `auto_save: false`, which is the default. **Teammate: always saved automatically** |
| **TTSE** (two-track) | `react.ttse.enabled` (**false**). Agent mode only | a FACT/TIP bank at `workspace/.ttse/bank.json`, plus system-prompt guidance | **none**: *"does not rewrite SKILL.md or show an approval dialog"* |
| **Auto Harness** | on demand, or **scheduled** (e.g. every 48 h) | **Meta Harness**: source changes → **PR, which needs review**. **Expert Harness**: a package that is **hot-loaded** after build and verify | Meta: PR review. Expert: **user confirmation** before hot-load (`docs/en/AutoHarness.md:60`) |

Skill self-evolution is triggered by a self-check every five eligible iterations for a single agent, or after each completed team task for a Leader. It can also be run with `/evolve <skill>`. Experience can be inspected, simplified, rebuilt and rolled back.

⚠ **Does jiuwenswarm keep evolved skills without human review?** The website implies it is fully automatic. The shipped defaults say otherwise: skill evolution is **off**, and when it is on, Single Agent and Leader changes are **approval-gated**. But two paths keep changes **without human review**: **teammate** experience and **TTSE** facts and tips. **Expert-Harness** packages are hot-loaded only after a user confirms (`AutoHarness.md:60`; corrected 2026-09-22, an earlier version of this note said no approval). `docs/en/SkillSelfEvolution.md:40-55`, `TTSE.md`, `AutoHarness.md` §1.2, and `resources/config.yaml:732`.

Sources: docs/en/{Skills,SwarmSkills,Symphony,SkillSelfEvolution,TTSE,AutoHarness}.md, jiuwenswarm/resources/config.yaml, jiuwenswarm/resources/agent/workspace/skills/, jiuwenswarm/agents/harness/common/{rails/symphony,rsi,auto_harness}/
