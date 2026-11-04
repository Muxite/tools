**The schema is the deliverable, and it is machine-readable (Muk, 2026-09-23).** Agreeing the schema and
data structure early is what unblocks other people, so the normative artifact now lives beside the prose:

In the tundle these are in `ai4research/capability-capsule/`.

| File | What it is |
|---|---|
| `merged/capsule.schema.json` | **Shape**: JSON Schema 2020-12 for the Declaration. Marks almost nothing required |
| `merged/policy-m1.json` | **Gate**: what the M1 epoch insists on. Versioned, relaxable, recorded on each Verdict |
| `merged/validate_capsule.py` | Runs either or both against a Declaration |
| `merged/examples/` | A real capability, the same one as declared today (the gate rejects it, and prints why), and a composite |

Required-ness lives in the gate, not the schema, because a required field in a shared schema can never be
taken back ([[Inspiration from Other Software]], Protocol Buffers). That is also what makes progressive
activation a mechanism: M2 and M3 are **new profiles, not a new schema**. **Tools come later** -- a field
whose consumer does not exist yet is present, typed and inert.

---

**A 能力胶囊 is flexible in form and strict in verification and quality assurance.** That is the thesis
line, added 2026-09-23, and both halves are load-bearing: flexibility of form is what makes adoption
cheap, strictness of verification is what makes flexibility safe.

**A capsule holds a set of capabilities. n = 1 is the degenerate case** — a single capability is a capsule
of one, and anything can be a capsule. One schema, with optional sections that switch on by type, so the
librarian places every item by the same rule. A capsule may contain its own DAG (`members[]` +
`structure`) and be placed in the outer DAG as a block.

A capsule can also **represent the verification of a task**, which matters most for non-deterministic
work where the output can only be judged rather than checked — but it is never the thing that judges
([[The Ceiling]]).

→ [[What Is In The Library]] for every shape a capsule can take, [[Overlap and Merge]] for how bigger
ones come to exist, [[Quality Not Just Correctness]] for what "strict" means.

---

**A schema: the contract every capability declares, and the records kept about it.** It is a scheme that uses tools
(the gate, filter, screener, verifiers, librarian) and is never a tool itself. Source of truth:
`capsule-openjiuwen/merged/SCHEMA.md`, **v2.10b** (2026-09-24; §0 is the reference by function; §0.6 and §4.3a plan,
schedule and multiplicity; §4.5a state, undo and the author's liability; §4.5b node gates; §4.9b what a capsule
promises to keep stable; §4.13a the capability tree; §4.14 exempt generalists). The sections below were written at
v2.5 to v2.8 and still hold; what changed after the presentation is in [[Post-Presentation Decisions]].

## What it does: four verbs on one schema

| Verb | Easier because |
|---|---|
| **Pick** | inputs and outputs are known; code removes every capsule whose declared requirements do not fit, then a model chooses among the few left. Cheap *because* strict → [[Predicate Parity]] |
| **Verify** | everything is declared, so every check has a target; hashes prove the checked thing is the run thing; observed effects are compared with declared ones → [[Declared vs Observed]] |
| **Improve** | performance and trust are logged by others than the builder; parents and children known through lineage and hashes; gaps feed builds → [[Self-Improvement]] |
| **Remove** | spatiotemporal composability: needs, provided services and each effect's undo are declared |

Underneath: the Declaration (one unified schema, required core, optional parts) and the capability itself, **held by
carrier and hash**, never inside the Declaration. A capsule **points at code and never holds it**: a leaf carries
`identity.carrier` and `identity.body[].sha256`; a composite carries `members[]` and a DAG, never both:

| Kind | agent-core carrier | Hashed |
|---|---|---|
| tool | `ToolCard` | source files |
| skill | `SkillSpec` (`SKILL.md` folder) | every file |
| MCP server | `McpServerSpec` | local files, or endpoint and version if remote |
| A2A agent | the A2A client | endpoint and version; the card is metadata only |
| agent, subagent | `AgentTemplateSpec` | template files |
| composite | its members | each member's `decl_hash` |

## A capsule holds no task (v2.5)

A Declaration describes a capability, never a use (invariant 12): no step, task type, stage, workflow, capsule to run
with, or worker. Today's manifests write uses in (task types in 85 of 85, `requires_after` naming a capsule in 42).
Uses live in the Plan step (planner), the Binding (freeze: `bound[]` primary, context, dependency, plus fallbacks) and
the Binding's `invocations[]` (dispatch: one per run, so fan-out items, attempts and fallbacks are each recorded).
Fan-out is on the Plan step (`over`, `gather`); the capsule never knows it is mapped. Still six records.

## Node gates, inherited suites, exempt generalists, the tree (v2.7)

- **Node gate = three parts, three writers** (§4.5b): step acceptance (requirement compiler, from the request),
  capsule checks (the author promises, the check's author writes the runner), artifact-type checks (vocabulary
  owner). Today the capsule manifest's own claims become model-judged items. An admitted capsule very likely passes
  its own part; the step's part tests this request. Each verdict names its part, so blame lands on the capsule or on
  the fit.
- **Suites travel with the lineage** (§4.7): the Verdict lists every suite; a child inherits them. RSI reads visible
  suites and adds cases; sealed ones only as pass or fail. Better = passes all inherited suites, its new cases, and a
  fresh held-out addition from verification.
- **`guarantees.exempt {reason: generalist}`** (§4.14): level `exempt`, below provisional. Several generalists (Codex,
  Claude), named in the run contract's `generalists[]`. Exempt from the library's verification policies, bound by every
  plan gate. Only `generalist` is an accepted reason.
- **The capability tree** (§4.13a): every Declaration ever submitted is a node; CC stores and exposes (guaranteed from
  its own records, optional what the builder supplies); **RSI's policy chooses where to branch**; CC never ranks nodes
  and keeps no score.

## Start small, block only for safety, label for quality (v2.8)

- **Invariant 14:** a run is refused only for identity or safety (hash, protected write, undeclared effect,
  irreversible effect without approval, revoked or security-suspect, failed node gate). Quality shortfalls are labels
  on the delivered claims, with a reason (`judge_unmeasured`, `judge_demoted`, `exempt`, `input_unsupported`, `revoked`).
- **Judges always gate** (§4.5c). Standing per judge, model and artifact type: unmeasured (label), calibrated (30+
  items with injected defects: supported, audited), measured (200+, under 0.05: certification). 5% of judged passes are
  spot-checked, so judges calibrate in normal use. Retirement still needs a measured judge.
- **Softer:** provisional capsules and generalists may bind to judged steps; a step opts into `requires_certified`; a
  sprint may set `require_supported_delivery`. A person confirms only writes, deletes, emissions, executions and `ext:`.
- **Extra small library:** about ten seed capsules, caps of 1-3, generalists for the rest, import first on a recurring gap.

## Where it lives in openJiuwen (schema §4.17a)

CC adds records and checks and replaces nothing: the Declaration is a Card (openJiuwen already keeps session and
runner out of Cards); an invocation is a harness-protocol Turn, or an item for a tool; generalists are harness providers
(`codex`, `claudecode`, `native`, `dsh`); approvals are the `PermissionEngine`'s `ASK`; trajectories are
`agent_evolving`'s, consumed. Details: [[Position in the Pipeline]].

## Authors answer for state and undo (v2.6)

Capabilities are not inherently stateless (an MCP server over a live database), undo is not guaranteed, and removing a
bad capability does not clean a context it shaped. **The author declares, CC checks** (invariant 13):
`changes.effect_class` (pure, idempotent, compensable, irreversible), per-effect `idempotent`, `ws:` or `ext:`
resources (external effects only compensate or emission). The gate runs claimed-idempotent capabilities twice and each
declared undo once; a remote body's interface is fingerprinted and compared at every dispatch; a revoked context
capsule taints every invocation it shared a context with. Retries, fan-out, exploration and approval follow the class.
**No numeric trust score:** a mismatch is a typed reason and a Standing move, recorded against the builder.

## What the supervisor settled

| Date | Ruling |
|---|---|
| 2026-09-18 | CC is a schema layer. The slides do not restrict the design. AI4Research itself is not a capsule |
| 2026-09-21 | "CC is more of a scheme, and verifier is a tool. CC can use tools, but CC is not a tool." Verification covers the system and capability levels at each sprint. Capsules never change model weights. agent-core changes only where necessary |
| 2026-09-22 | No page or time limit; quality, logic and flow decide |

## Two goals

1. **Safe use:** check what a capability declares before any sprint relies on it.
2. **Safe self-improvement:** agents build, check and keep their own capabilities while long runs continue. → [[Self-Improvement]]

## Six records, one writer each

| Record | Written by | Answers |
|---|---|---|
| Declaration | the builder (a person or RSI) | what it needs, changes, promises, spends. Seven sections: identity, ports, needs, changes, guarantees, budget, members. A `contract_hash` covers everything but the body, so a suite written before the code is bound to its contract |
| Verdict | the admission gate (code) | was this exact hash checked, how, at which level; RSI's own result is kept only as `builder_gate` evidence |
| Standing | the librarian, **only** | which hash is current for a name, and may it be offered. Findings can move it only toward less authority |
| Plan step | the planner | what a node requires; the sprint's run contract (generalist flags, unattended) |
| Binding | the freeze, then dispatch | exactly what ran where, with fallbacks, pinned overlays, predicate values, and claims with a status (supported, unsupported, stale). The freeze checks the sprint's snapshot, so an admission during planning never aborts a sprint |
| Finding | screeners, audits, probes | what was learned later: gap, drift, composition, audit violation, and more |

**Rule:** observation may withdraw authority, and only a checked declaration may grant it.

## Key rules

- **Backing:** two levels per capsule (provisional, certified) and an assurance per claim (enforced, tested, audited,
  declared).
- **Invariants:** fourteen (12 no task in a capsule, 13 the author answers for state and undo, 14 block only for
  safety). The most cited are:
  - a sprint sees only the versions it started with;
  - nothing may change the gate, the suites, or what admission reads;
  - eligibility comes only from declared predicates. → [[Predicate Parity]]
- **Pinning:** everything a sprint loads is pinned by hash: the body, **overlays** (evolved experience, TTSE guidance,
  hot-loaded packages), composite members and fallbacks.
- **Dependencies:** pinned by default. An author may **unpin** one only by writing its **purpose**, role and contracts,
  at a cost to trust: the capsule stays provisional. Why: given the failed contract, one-round repair rose from 10% to
  78% (2605.10990 p8-9; not significant against plain drift text, 60%).
- **Composability in space and time** (terms from Cordis, 2608.25512): each capsule declares what it needs and how each
  effect is undone (inverse, scoped, compensate, emission). It changes between sprints, never within one.
- **Composition is screened, never certified.** The schema supplies what SkillFuzz needs; 80.6% of its high-risk plan
  flags were confirmed in execution.
- **Composites** are gated by their members, pinned by hash. Team skills stay out of v1, because their Leader plans.

## Why a schema

Each tool the new system needs answers a failure a paper measured, and each needs the same facts about a capability. →
[[Evidence]], [[Declared vs Observed]]
