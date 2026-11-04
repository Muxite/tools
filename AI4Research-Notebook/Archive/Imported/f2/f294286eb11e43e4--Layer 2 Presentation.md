**The second deck, layer 2: what we build for M1, on which code, and who builds it.** Built 2026-09-24,
alongside the revision of the post-presentation deck. Layer 1 (2026-09-23) was the general form; layer 2 is
the technical design. It runs about 15 minutes, then discussion.

## Final state (seventh cut, 2026-09-24)

| | |
|---|---|
| Deck | `ai4research/capability-capsule/Capability Capsule - Layer 2.pptx` (source `capsule-openjiuwen/merged/`). **19 content slides at 14:05**, then **Reference A** (21 slides, for questions) and **Appendices B and C** (the post-presentation deck itself, read from its current `deck.json`) |
| Build | `merged/layer2/`: `figures/figs_l2.py` → `build_spec_l2.py` → `deck_l2.json` → `build_deck_l2.py`. The build copies the deck into the tundle |
| Isolation | `build_spec_l2.py` copies its helpers, because **importing `build_spec` rewrites the shared `deck.json`** |
| Links | every link fetched and recorded in the build script's `LINKS`; the post deck's registry is read with `ast`, not imported. Links in table cells work too |
| Notes | the post-deck form: **Main points**, then **Supplemental points** (facts and likely questions) |
| Rules | no code on any slide; every eyebrow carries its a-to-g letter; changes since 23 September are shown as **revised** versions of post slides, each naming the slide it replaces |

**The 19 slides:** the five ideas · the final target, with M1 as its first rung · what is in a 能力胶囊, now ·
the skeleton (capsule parts and control parts) · the first capsules each stage needs · the stack · our modules
and their interfaces · from pointer to running code · one tool call, with a model and without · running a skill
(a new agent per invocation) · one request end to end (13 messages) · records and storage · what Symphony is
and how it meets us · the planner-binder · what can go wrong, where it is caught · designed in, not built yet ·
where I fit best · where to start (the work in order, and today's decisions).

**Known issue, 2026-09-25:** `tundlekit deck lint layer2/deck_l2.json` (which now times only the Main points)
finds 6 slides whose Main points alone exceed their time: the title, the five ideas and the final target, plus
reference slides 22, 23 and 25; slide 25 also says "next slide" while being a reference slide. Not changed.

## Muk's decisions (2026-09-24)

- **M1 is on openJiuwen, a fresh start.** The original AI4Research tools and implementation are an archive,
  "seriously fragile and not good to extend". They appear only as lessons. The one lesson kept: four readers of
  one precondition gave four answers, which is why there is **one** shared evaluator.
- **No M1 spike yet.** The deck presents code ideas.
- **Seeding.** Three seed capsules, all tools, all tested deterministically:
  - `count_spaces`: text → integer, pure. **The M1 task**, run as one node. An example and a test fixture, not the product;
  - `regex`: text and a pattern → array, pure, seeded so the planner has a real choice;
  - `parse_txt`: path → text, `read_only`.
  - `parse_txt → count_spaces` on a file is **the first chained run, M2**.
  - Seed Declarations were drafted and pass the M1 gate with `validate_capsule.py`. They lived in a session
    scratchpad, not the repo, with placeholder hashes.
- **Planning: ports first, Symphony later.** Match the requirement's want and given to declared ports. Symphony's
  `plan()` always calls a model, even to accept an edge; it uses the same `(name, type)` rule, so switching later
  changes no Declaration.
- **The planner-binder:** contract, hard filter, exactly one survivor, the freeze binds (M1, in WP3); backward
  chaining at M2; scoring and Symphony's `plan()` at M3. It follows kube-scheduler's filter, then score.
- **Execution: our own Kahn runner**, written for n nodes. Nothing in agent-core *runs* a plan in topological
  order (the workflow engine runs Pregel supersteps).
- **Versions: a linked list for M1.** `lineage.parent` keeps the tree, but M1 never branches and plans with the
  latest version only; a rollback is a new node (`rollback_of`). Reuse jiuwenswarm's
  `.archive/versions/index.json`. A deliberate M1 subset of "a tree, not a chain".
- **M1 stores a minimal Verdict** (pass, `decl_hash`, policy epoch). The full Verdict and Standing stay at M3.
- **Capsules** run on the workflow side and as post-freeze executors; their outputs go to gates, then delivery,
  and neither is CC. **No delivery capsule**: claim verification feeds the gate, and delivery is control.
- **Requirements is control in M1.** Its assessing steps may become capsules later, as the post deck allows.
- **Tools and MCP need no agent.** Each skill invocation gets a new agent, discarded after. Nothing waits for tasks.
- **Merge, fusion and optimisation are back-burnered:** possible in the data structure, with no code in M1.
- **Depth or breadth is open**, left for the room. The deck states no lean.
- **Later milestones are code changes on our side; capsule authors never migrate.**
- **Where agent-core has no answer, borrow a shipping pattern from big-company software** and cite it.
- **Roles, one slide:** "I think I fit best in development and implementation", to see closely how CC integrates
  and how other authors will use it. The authoring guide comes out of writing the seeds. Other teams appear only
  as what CC needs from them and gives back.

## How the code gets in

- **Our own ~30-line loader**, not `harness.tool.file`, to shrink the blast radius. A sha256 check before import.
- **One `CapsuleTool` wrapper** applies the checks on every path, including workflow `ToolComponent` calls, which
  skip rails. Its precedent is inside agent-core: `decorate_tool_with_trace` (`core/session/tracer/decorator.py`)
  already wraps every tool in a proxy that replaces `invoke`, applied by `ToolMgr.get_tool`.
- Set `ToolCard.id` explicitly, because the default is a uuid.
- **Designed in, not built yet: what M1 must not block.** Load only through our loader, one record per load, the
  reverse unbind kept (M5); address everything by `decl_hash` (merge); write `lineage.parent` and never overwrite
  (branching); keep Symphony's plan shape (scoring); dispatch on `identity.kind` (skills and MCP); no shared
  mutable state (parallel runs).
- **Work packages:** WP0 (schema fixes, and the state decision below) through WP6 (the Kahn runner, then the M2
  chain). Shipped as an extension package (rails, a provider, a wrapper), with no fork of agent-core.

## What agent-core showed (read in source at `e23806c1`)

- **Symphony finds and plans, and never runs.** `plan()` returns a JGF graph of capability ids with a status of
  `ready`, `needs_input` or `no_plan`; the agent then runs the skills through its ordinary tools. The agent-to-planner
  tool `symphony_compose_graph` is defined in jiuwenswarm; agent-core only names it.
- **No concrete `CapabilityProvider` exists** in agent-core. CC's would be the first. `FingerprintService` reads the
  snapshot, the capabilities, then the snapshot again, and rejects the read if it moved. Declared ports map onto
  `CapabilityIO`.
- **What runs a capability:** a tool or MCP tool through `AbilityManager`, or a workflow `ToolComponent` with **no
  model** (`tool_comp.py:61-70`); a skill is `SKILL.md` text a model reads and acts on, so it **needs an agent**; an
  A2A remote agent through `Runner.run_agent` → `RemoteAgent`.
- **The workflow tool path bypasses `AbilityManager`, every rail and the permission engine.** So CC guards the tool,
  not only the agent.
- **agent-core drops MCP tool annotations** (`readOnlyHint` and the rest); MCP's spec says clients must treat them as
  untrusted anyway.
- **No hash, signature or version on any extension spec or load path**; load records are kept only in memory.
- **Reused as they are:** `extension_binder` binds and unbinds in reverse order; the permission engine decides
  `ALLOW`, `ASK` or `DENY`.

## Symphony today (checked 2026-09-24)

- **One consumer.** Of the local openJiuwen repos only jiuwenswarm imports `openjiuwen.symphony`, and everything is
  **off by default** (`symphony.enabled`, `evolution.enabled`, `skill_retrieval.enabled`). jiuwenswarm uses the
  retrieval tree, `plan()` (fast mode only), the evolution rail and flow skill packs; not the experience retriever
  or `EvaluationSuite`. skillhub's `openjiuwen-skillsdispatch` package is imported by nothing.
- **Young and still moving.** agent-core's first commit is 2026-07-29 (29 commits, all within 90 days, still
  migrating the skill-pack adapter on 09-21); jiuwenswarm since 2026-06-09 (69 commits). Main author: lin-xiaoyu.
- **No roadmap.** The only status table (symphony `README.md`, 09-04) is stale; no CHANGELOG or design doc.
- **Pins diverge.** jiuwenswarm pins agent-core `b6db2733` (09-20), which is not an ancestor of `e23806c1`. Choose
  which line to pin to ([[Open Questions]]).
- **Ask the Symphony builders:** is a deterministic `plan()` path coming, is the provider protocol stable, and do
  they want an admitted-only provider?

## Borrowed patterns (links checked 2026-09-24)

| Pattern | Source | How CC uses it |
|---|---|---|
| Lockfile `integrity` | npm | the carrier hash at bind |
| `ValidatingAdmissionPolicy` with CEL, in-process | Kubernetes | the gate and one predicate language |
| filter, then score | kube-scheduler | the planner-binder |
| Binary Authorization | Google | bind verifies the Verdict (an attestation) and does not re-test |
| Provenance | SLSA | the Binding |
| `<uses-permission>` | Android | `effect_class` declared up front, severe effects set to ASK at run time |
| never add a required field | Protocol Buffers | required-ness lives in the policy, not the schema |
| `needs`, CAS and action cache, Deployment against StatefulSet | GitHub Actions, Bazel, Kubernetes | ordering, content addressing, stateless against stateful capsules |

## State and tests (Muk, 2026-09-24): proposed for schema v2.11, decided in WP0

- **The author declares whether a capsule holds state:** `changes.state {kind, scope, reset}`, with `kind` one of
  `none` (count_spaces, regex), `reads_external` (parse_txt), `session` (within one run), `persistent` (across runs).
  A whole-capsule view on top of the per-effect `idempotent`, `reversibility` and `undo` of §4.5a.
- **Handling by kind:** none → unit cases, replayed any time; reads_external → each test ships its fixture, and
  `needs.when` is checked at dispatch; session → fresh state per invocation, parallel only if isolated; persistent →
  testable only with a declared reset or snapshot, otherwise observed at lower standing, retry per `effect_class`.
- **Optional `guarantees.test_aids`** (example inputs, fixtures, a reset command) go to RSI and are **never
  evidence**: no capsule is its own final judge.
- **Tests are saved by id**, inputs stored by hash, so a child version can run its parent's tests. The record keeps
  the latest test id and result; in M1 that sits with the minimal Verdict.

## How it got here

1. **First draft** targeted AI4Research's harness (tmux pane operators, four precondition readers, the 0/85 fleet
   gap). Replaced the same day once Muk moved M1 to openJiuwen.
2. **Seeding** cut: the pipeline skeleton (request → requirements → plan → freeze → dispatch → gate → delivery →
   answer, every step new control code) and the three seeds.
3. **24 content slides at 19:35**, with "What changed since 23 September" and a-to-g at layer 2 (defining the
   Verdict and the Binding); Sonnet review fixes applied.
4. **25 slides at 14:55**: what to touch, do and test; "Why these choices" against ten shipping patterns.
5. **18 slides at 13:35**: final read-through; no code on slides; revised post slides.
6. **19 slides at 14:05**, the final: the technical-design views (stack, module interfaces, the end-to-end
   sequence, records and storage, failure modes) and "Designed in, not built yet". Earlier slides moved to Reference A.

An HTML version was published as an artifact (https://claude.ai/artifact/R4MuGkGqCxFVTZjKN315p9). Its sync was
**paused** behind the pptx, with 60 orphaned image assets that can be deleted with Muk's approval.

Related: [[Milestone Ladder]], [[Where It Attaches]], [[Symphony Flow]], [[What openJiuwen Is Missing]],
[[Post-Presentation Decisions]], [[HANDOFF]].
