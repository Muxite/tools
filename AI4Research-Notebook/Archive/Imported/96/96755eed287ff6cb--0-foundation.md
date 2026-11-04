# Foundation: what a capability declares, and how the capability itself is held

**One unified schema for every kind of capability,** with a required core and optional parts that are declared when
they apply. Everything CC does (pick, verify, improve, remove) reads these fields. Source of truth:
`merged/SCHEMA.md` §3.1.

## The Declaration's fields

**One schema, whole from day one; what is staged is how much of it is enforced.** A field is declared
in the schema from the start and sits inert until the component that reads it exists, so nothing is
redesigned later and a system with parts missing still works demonstrably. The milestone column below
says when each part *starts being enforced*, not when it is invented.

**Enforced at M1, ten fields:** `identity.name`, `identity.kind`, `identity.carrier`,
`identity.body[].sha256`, `identity.summary`, `ports.inputs[]`, `ports.outputs[]`, `needs.when[]`,
`changes.effect_class`, `guarantees.checks[]`.

Everything else is optional until the milestone that needs it: `identity.lineage` at M4 (RSI),
`needs.model` and `budget` at M3 (routing), `guarantees.acceptance`, `evals` and the quality criterion
at M3, `changes.provides` and `invariants` at M2, `overlays`, `load_mode` and `exempt` at M3, and
`members[]` with `structure` at M4 (the merge engine).

**Every enforced field is a cost** -- work for whoever writes a capsule, and a check the gate must run.
That is the reason the core is ten fields rather than forty.

**A capsule holds a set of capabilities, and n = 1 is the degenerate case.** A single tool is a capsule
of one; a bundle is several loaded as one body under `PluginSpec`; a composite carries `members[]`, each
independently admitted, plus the internal `structure` that wires them. All three are placed by the same
rule, which is what "flexible in form" means.

The table lists every section of the Declaration, what is required and what is optional, and which of the four
verbs reads it. The rule of thumb: a field is required when a check, a filter or a revocation cannot work without
it, and optional when it only helps where it applies.

Written by the builder (a person, or RSI). It is immutable: any change is a new Declaration with a new hash.

| Section | Field | Required? | What it should be | Read by (verb) |
|---|---|---|---|---|
| identity | `name`, `version_label`, `schema_version` | required | a stable name; free-text version; the schema version it is read under | pick, improve |
| | `kind` | required | tool, mcp, skill, prompt, subagent, agent, composite | pick, verify |
| | `carrier` | required | the agent-core spec it loads through (below) | verify, remove |
| | `body[]` | required | every file, each with its SHA-256; a remote service is pinned by endpoint and version instead | verify |
| | `summary` | required | at most 400 characters; the only prose a model reads when choosing | pick |
| | `load_mode` | required | `invoked` (behind a boundary) or `context_injected` (shares the agent's context) | pick, remove |
| | `lineage` | required: `parent` (empty for a root), `relation`, `builder`; the rest optional, kept when the builder supplies it | parent, relation (supersedes, specialises, rollback_of, migrated_from), `build_trigger`, `context_capsules`, provenance (generating model, prompt, trajectory) | improve, remove |
| | `overlays[]` | optional | evolved experience, guidance or packages loaded with it, each hashed | verify |
| ports | `inputs[]`, `outputs[]` | required | each with a type from one versioned vocabulary; each output names the check that validates it | pick, verify |
| needs | `when[]` (preconditions) | required; empty only with a stated reason | predicates `{path, operator, value}`, each with `state_source`, `max_age_s`, what happens when the fact is unknown or its source is down, and a parity check | pick, verify |
| | `external[]` (the capability's own dependencies) | required; may be empty | each pinned (hash, model id and version, endpoint and version, or capsule hash), **or** unpinned with `purpose`, `role` and `contracts` (optional) | improve, remove |
| | `network` | required | none, an allowlist, or open | pick, verify |
| | `resources[]`, `injects[]`, `model` | optional | resources with a mode; services it needs; model constraints (never a model choice) | pick, remove |
| changes | `effect_class` | required | `pure`, `idempotent`, `compensable` or `irreversible`: the author's attestation for the whole capability, checked against its effects | pick, verify, remove |
| | `effects[]` | required; empty only if it changes nothing | per effect: resource (`ws:` inside the capsule layer's boundary, `ext:` outside it), operation (read, write, create, delete, emit, execute), scope, `idempotent`, reversibility (inverse, scoped, compensate, emission; only compensate or emission on `ext:`), risk with blast radius | verify, remove |
| | `provides[]`, `invariants[]` | optional | services it installs; invariants, each with a check | remove, verify |
| guarantees | `exempt` | optional; only `reason: generalist` | a do-anything capsule outside the library's verification policies; plan gates still apply, level `exempt` | pick, verify |
| | `checks[]`, `acceptance` | required (unless exempt); at least one postcondition | each check: kind (including negative controls), anchor (deterministic, reference, judged), runner hash, author, held out or not, where its signal comes from | verify |
| budget | `per_call`, `enforcement`, `on_exhaust` | required for agents; optional otherwise | limits between calls, and how each is enforced | verify |
| members | `members[]`, `wiring[]` | composites only | members keyed by role, each pinned by hash; one Declaration may fill several roles | remove |
| coverage | `undeclared_notes` | optional | what the builder knowingly leaves out | verify |

**Computed by the gate, never written by the builder:**

- `decl_hash`: over everything;
- `contract_hash`: over everything but the body, so a suite written first is bound to the contract;
- agent-core's runtime flags;
- a composite's derived needs and changes;
- `context_cost_tokens`.

**A Declaration describes a capability, never a use** (invariant 12). It names no step, plan, workflow, stage,
task type, capsule to run before or after it, or worker. It is told what to do through its inputs. A capability valid
only for some inputs says so with `needs.when` predicates over them, never with a task list. The uses live in the Plan
step, the Binding and the Binding's invocations (chapter "Plan and schedule").

**Why both a class and per-effect undo.** Each effect's `reversibility` and `idempotent` flag is what verification
checks, one effect at a time. The `effect_class` is the author's one-word summary of the whole capability, which the
planner, the scheduler and dispatch read to decide retries, fan-out and approval without re-deriving it. The gate
checks that the two agree, so the summary can never be kinder than the effects behind it.

**The author answers for what the capability does** (invariant 13). CC cannot see inside a remote database,
so the author declares up front what it touches, whether each change is idempotent, and how it is undone or that it
cannot be. CC answers for checking that declaration against what it observes. A mismatch is a typed reason and a
Standing move recorded against the builder. **There is no numeric trust score.**

## Three trust levels, and trust per claim

A level says **how far a capsule's results can be trusted**, and it is earned by what was tested before admission.
The levels exist because passing a task is not proof of doing the job: 215 of 222 self-built tools failed held-out
tests of their own job while no in-session signal flagged them (Beyond Task Completion, 2604.00392 p1, p5). But a low
level does not stop a capsule from running. It decides what its results support: that is the rule that keeps CC
from being so strict that AI4Research cannot do its work (below).

| | Exempt (generalists only) | Provisional | Certified |
|---|---|---|---|
| tested before admission | enrolled, not admitted on a job: loads, stays within its declared effects, refuses a protected write, completes sample step contracts under their gates | loads, stays within its declared effects in a sandbox run, and passes one postcondition on inputs it was not built from | every output covered by a check written by someone who never saw the code; a judged check counts only if the judge's error is measured and low enough; predicate parity tested |
| may bind | a step nothing else fits, named by the run contract, where every output has a gate of any kind | any step that does not require certified capsules | any step |
| its claims are | never `supported` | `supported` only where every gating check is deterministic, reference-based or a calibrated judge; otherwise labelled | `supported` where its checks pass |

**Block only for safety, label for quality** (invariant 14). A check refuses a run only for identity or safety.
Everything about quality changes what a result is worth, recorded on each delivered claim with a reason, not whether it
may run:

| Refuses the run (identity and safety) | Labels the claims (quality) |
|---|---|
| the body's hash is not the pinned hash | the capsule is provisional, not certified |
| a write to a protected component | a gating judge is not yet calibrated |
| an observed effect outside the declaration | the capsule is a generalist (exempt) |
| an irreversible effect without its approval | an input the result rests on is unsupported or stale |
| a revoked capsule, or one suspect for security or harm | |
| a failed node gate (the workflow decides repair or fail, as today) | |

**Exempt** is for generalists only: do-anything capsules with no job of their own, so there is nothing to
admit them on. Several may exist, such as a Codex and a Claude generalist.

Each individual claim also carries an assurance, in the order enforced > tested > audited > declared. So a
certified capsule can still say honestly that one promise is only declared.

## How the capability itself is held

**What a skill is, in agent-core.** A `SKILL.md` folder of instructions and scripts, described by a `SkillSpec`. The
harness's `SkillUseRail` offers skills through an allow-list (`enabled_skills`); the agent sees each description and
loads a skill when it chooses to. A skill has no typed interface and declares no effects. A capsule wraps it and
adds both.

The Declaration never contains the capability's code. It **names and hashes** it, and says which agent-core carrier
loads it.

| Kind | Carrier (agent-core) | What is hashed | How it is loaded |
|---|---|---|---|
| tool | `ToolCard` | the tool's source files | the binder, as a tool |
| MCP server | `McpServerSpec` | local: its files. Remote: pinned by endpoint and version | the binder, as a whole server |
| skill | `SkillSpec` (a `SKILL.md` folder) | every file in the folder | the binder, with the offer applied through `SkillUseRail`'s allow-list |
| A2A agent | the A2A client | pinned by endpoint and version; its card is metadata, never evidence | the A2A client |
| subagent, agent template | `AgentTemplateSpec` | the template files | the binder |
| prompt section | `PromptSectionSpec` | the text | the binder |
| bundle | `PluginSpec` (tools, MCP, skills; **no rails**, which would put a capsule in reach of the checks) | every file | the binder |
| composite | its members | each member's `decl_hash` | through each member's carrier |

**Why:**

- The Declaration holds a hash and a carrier, and loading goes through the capsule layer's immutable store, because
  agent-core's binder loads by name with no hash check. The hash proves that what ran is what was checked (Execution
  lineage; RelAIBuild).
- Real skills declare almost nothing today: of 34 jiuwenswarm skills, none declares inputs, outputs or effects. So an
  **importer** proposes what it can derive, a person confirms the effects, and the capsule enters as provisional.
