**M1 note, 2026-09-24.** M1 is a fresh build on openJiuwen ([[Layer 2 Presentation]]), with its own skeleton:
request → requirements → plan → freeze → dispatch → gate → delivery → answer. The file and line references below
are to the **archived** AI4Research harness: they show where the same stages sit today and are lessons, not
places to build.

**Corrected 2026-09-23 — see [[Every Stage Applies Capabilities]].** The old reading of this note was that
CC lives at three stages and that "intake, intent and requirement compilation never see capabilities."
That line is **superseded**: every stage that does work picks, binds and runs a capsule.

**CC's *control* acts at the planning, freeze and dispatch stages,** plus the in-run gates and delivery.
Admission, the audit loop and the librarian run outside the sprint. **CC is upstream of Symphony:** its
provider lists only admitted capsules, and Symphony retrieves and ranks within them.

**Plan and schedule (v2.5, schema §4.3a).** The planner writes Plan steps and never names a capsule (as today,
`elastic_planner.py:1328-1329`); supply reshapes the plan only through port types. Code expands and filters, models
choose, the freeze writes one Binding per step. **The workflow's scheduler keeps order, the cap of 8, conflict
hold-backs, worker leases and retries**; CC supplies only declared write scopes, resource modes and `parallel_safe`.
Dispatch appends one invocation per run. Diagrams: `capsule-openjiuwen/merged/figures/S1.png`, multiplicity `M1.png`, position `P1.png`; code locations in
`capsule-openjiuwen/kb/repos/ai4research-workflow.md` (planner filter `elastic_planner.py:4553-4648`, freeze
`execution_authority.py:47-94`, dispatch `operator_runtime.py:796-815`, `capability_capsules.py:1220-1242`).

## In the AI4Research workflow

| Stage | What the schema supplies or records |
|---|---|
| intake, intent | **the work of each stage is a capsule too** (`intent → IntentIR`), picked and bound like any other; only CC's control machinery is absent here |
| planning | a filter on declared types, effects, planning-evaluable predicates and level; a model binds each step; a second model reviews the fit, in bounded repair; if nothing fits, the step binds to the generalist (if allowed), and a gap Finding is written |
| freeze | plan, run contract, each Binding's hash, Verdict, pre-approved fallbacks, pinned overlays and model candidates |
| dispatch | the live hash must equal the pin (new); the same predicates re-evaluated on fresh state; a DEFER waits, then falls back; steps with overlapping write scopes never run together |
| operators, gates | effects observed at tool-call level; exits and gate verdicts recorded |
| claims | each claim records its Binding, so revocation marks exactly its claims stale; generalist claims are never marked supported |

**Tokens**: today's binding prompt carries a full catalog row for each eligible capsule, and repeats it on repair; a removed capsule shrinks to a short exclusion row. A precondition adds removals beyond today's type and effect filter. The saving is measured in M2 against today's filter. → [[Predicate Parity]]

## Where each part lives in openJiuwen (v2.7, schema §4.17a)

- **Declaration = a Card** (Card vs Config, `.claude/rules/architecture.md:31`: no session or runner in a Card), which
  is invariant 12. Loading goes through `AbilityManager`/`Runner.resource_mgr`, the extension binder, or
  `create_harness(manifest, provider=...)`, fed from CC's hashed store.
- **Invocation = a harness-protocol Turn** (agent capsule) **or item** (tool capsule); `TurnResult` gives usage and cost.
  A pause and resume on one session is one invocation; a retry after a terminal failure is a new one.
- **Approvals** = `PermissionEngine` `ASK` (jiuwenswarm ships permissions off; a CC sprint turns them on);
  `{instance}` scope = a `SESSION` sandbox. **Context taint** = no reuse of the session, or a Session VCS fork.
- **Generalists = harness providers** (`codex`, `claudecode`, `native`, `dsh`), one `AgentTemplateSpec` each.
- **Trajectories** are `agent_evolving`'s OTLP `Trajectory`, consumed. **RSI's tree** joins by `builder_ref`.
- **Names:** a CC *Plan step* is an AI4Research plan node, not an agent-core *Step* (one agent-loop cycle).

## In openJiuwen

| Hook (agent-core `e23806c1`) | Use |
|---|---|
| Symphony `CapabilityProvider` (atomic) | list only available skill, subagent and agent capsules (its graph takes no other kinds); tool, MCP and A2A capsules go through the filter and binder |
| Symphony `SkillGraphUpdater` | add, update or delete on each availability change |
| `apply_extension_hot` | load a capsule from the immutable store, after the capsule layer checks its hash |
| `before_tool_call` rail | tool calls compared with declared effects |
| `VerificationRail`-style allow-list | enforces which tools a capsule may call; effects themselves are enforced only in the sandbox (bash reaches any path, `mcp__*` passes) |
| `SkillUseRail(enabled_skills)` | applies the offer for skills; its experience text and `max_total_chars` truncation are pinned or switched off |
| `LoadRecord.refs`, `TrajectoryStore` | Bindings, via a new rail |

Gaps the capsule layer fills: every graph change calls a model; the binder loads by name with no hash check, so loading goes through the immutable store; load records live in memory, so a new rail saves Bindings. Nothing in agent-core must change; it needs configuration only. **Revised for M1 (2026-09-24):** loading goes through our own ~30-line loader with a hash check, and one `CapsuleTool` wrapper guards every call path, because the workflow `ToolComponent` path skips `AbilityManager`, the rails and the permission engine. What changes: the declared filter runs before Symphony's planner, which today leaves I/O compatibility until after the plan. Declared ports replace model-proposed edges. → [[openJiuwen Landscape]], [[Dependencies]]
