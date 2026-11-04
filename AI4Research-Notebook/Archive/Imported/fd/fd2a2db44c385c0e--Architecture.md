**Start here for the architecture.** A single, self-contained record of the design as of 2026-09-25 (end of day),
written so that a fresh session can pick up with no chat history and no memory files. Where a detail lives
elsewhere, this note links to it. Binding decisions are in [[Directives]] (newest first; when anything disagrees,
Directives wins).

## 1. What we are building

- **An AI4Research-style research pipeline, rebuilt on openJiuwen.** It runs on `agent-core` (pinned at
  `e23806c1`), with Symphony (an agent-core module) for indexing and, later, planning. Everything we write ships as
  **one extension package**; nothing in agent-core is edited. Good work goes upstream to openJiuwen as pull
  requests.
- **The old AI4Research harness (`stellven/AI4Research`) is an archive.** Its tools and code are never used or
  extended (Muk, 2026-09-24: "seriously fragile"). Its lessons, stage names and data formats may be reused, and
  whether its IR schema files may be adopted as data is still undecided (§10).
- **Capability Capsule (CC, 能力胶囊) is the schema layer.** Every capability declares what it takes, gives, needs,
  changes and guarantees, and it points at code by hash. It is a *scheme* that uses tools; it is never a tool.
  Thesis: *a 能力胶囊 is flexible in form and strict in verification and quality assurance.* See [[Capability
  Capsule]].

## 2. Team and roles, 25 September to 31 October 2026

| | Project role | Owns (component) |
|---|---|---|
| Muk | **architect**: designs the inside of M1 and M2 (structure, and what is possible); also codes | Capability Capsule |
| Ramika | **PRD**: sets the boundaries of M1 and M2 (what is in, what is out, what must be demonstrated) | verification |
| Xiaoyang | **primary coder** | model routing |
| Saurav | **blue team** (蓝军: attacks our work; our side is red in Chinese usage) | RSI |

- The team is in Canada, all in one place; Chinese holidays do not apply.
- Everyone can code; Xiaoyang writes the most.

## 3. Milestones

| | Running | Status |
|---|---|---|
| **M1** | one task through every stage; capsules and gates in every stage | build now (weeks 1–3) |
| **M2** | a few chained nodes; the planner decides by backward chaining; node gate; gap Finding | weeks 4–5 |
| **M3** | a library of about ten capsules; Verdict, Standing, librarian, held-out suites, calibrated judges, quality as a rate; Symphony `plan()` | designed now, not built this month |
| M4 | overlap and merge (composed and fused blocks) | later |
| M5 | install and uninstall mid-run | later |

- **One schema, progressively enforced.** Every field exists from day one. Each milestone's policy decides what is
  required; later milestones are code changes on our side, and capsule authors never migrate. See [[Milestone
  Ladder]].
- **Current scope is up to M3.** M4+ is only kept possible (§6).

## 4. The M1 architecture

M1 answers one task ("How many spaces are in `a b c`?" → `2`) through every stage. The stages are not simplified;
only **planning, dispatch and the library** are kept trivial. The detailed map is the M1 map (§11).

**The run, in AI4Research stage names (required in every diagram):**

1. **Intake** turns the request text into a RawIntent (kept by reference). The frontend is open; a CLI is the default.
2. **Intent compilation:**
   - CC `compile_intent` (a model) produces the IntentIR;
   - CC `review_fidelity` (an independent model) reviews it;
   - the **`decide_acceptance` gate** runs deterministic checks, then accepts, sends it to bounded repair, or
     asks the human to clarify or rejects.
3. **Requirement compilation:**
   - CC `compile_requirement` fills a RequirementIR template;
   - CC `review_requirement` is advisory only;
   - the **contract acceptance gate** validates it deterministically; a defect goes to bounded repair.
4. **Semantic contract:** the accepted RequirementIR. It holds want (integer), given (text), the allowed capsule and
   the checks. It is central: it drives the planner-binder and the step gate.
5. **Planner-binder, a pass-through:** hardwritten, no model, no selection. It resolves the contract's capsule id
   through Symphony's index and writes a one-step PlanIR.
6. **Freeze, a pass-through:** writes the **run contract**. That is one **Binding** per node (`decl_hash`, code
   sha256, Verdict), plus `semantic_contract_sha256`. That hash is not the schema's `contract_hash`.
7. **Schedule and dispatch:**
   - Kahn order with n = 1;
   - `needs.when` is re-checked on fresh state through the **evaluator** (PASS, FAIL or DEFER);
   - the node goes to the runner.
8. **Step gate:** runs the contract's checks and the check named by the capsule's `outputs[].check`.
9. **Delivery** answers the human. It is control, never a capsule.

**Around the run:**

- **Runner.** Every capsule call goes through it, the four model capsules and the tool alike. It:
  - reads the Declaration;
  - `loader.load` checks the sha256, then imports (refused with `CARRIER_CHANGED` on a mismatch);
  - `CapsuleTool.invoke` checks ports in and out;
  - PermissionEngine decides by `effect_class`;
  - runs the capsule;
  - appends the invocation to the node's Binding. Capsules that run *before* freeze append to a **stage record
    keyed by run id and stage** (*proposed*, awaiting Muk).
- **Store (simplified).** `gate.admit` checks the schema and `policy-m1`, then writes:
  - Declarations by `decl_hash`;
  - a minimal Verdict (pass, `decl_hash`, policy epoch);
  - code by sha256;
  - tests by id.
- **Symphony (index only).** Our provider (`capabilities()`, `source_snapshot()`) feeds `FingerprintService`.
  `plan()` is not used in M1.
- **Observability, from day one.** Spans (agent-core `harness/observability`), Bindings and invocations, and gate
  results, for every capsule call and every gate.

**The M1 capsule set is fixed; there is no library:**

- `compile_intent`, `review_fidelity`, `compile_requirement`, `review_requirement` (models);
- `count_spaces` (tool: text → integer, pure).

The requirement-compilation names are proposals. `regex` was dropped, because M1 has no selection.

**Outside M1 (the PRD sets this boundary):** library selection, planner intelligence, RSI, optimizer and merge, the
librarian, judges, meta-RSI.

## 5. Modules and where they plug into agent-core

Owners are proposals, written as writer · reviewer.

| Module | Does | agent-core seam | Owner |
|---|---|---|---|
| `cc/schema` | `capsule.schema.json`, `policy-m1.json`, validation | none | Muk |
| `cc/store`, `cc/gate` | admit and keep Declarations, code and tests by hash | `core/foundation/store/kv` (`ShelveStore`) | Xiaoyang · Muk; Muk · Ramika |
| `cc/provider` | feed admitted capsules to Symphony | `symphony/interfaces/capability.py` `CapabilityProvider`; ours is the first concrete one | Muk · Xiaoyang |
| `cc/skeleton`, `cc/stages` | intake, intent and requirement compilation, acceptance gates, repair | model calls through the runner | Xiaoyang · Muk |
| `cc/contract` | RequirementIR v2 + deterministic validation | none | Muk · Ramika |
| `cc/planner_binder` | pass-through plan; freeze → run contract | Symphony index | Muk · Xiaoyang |
| `cc/evaluator` | `needs.when` → PASS, FAIL or DEFER; one evaluator, two callers (dispatch now, planning at M2) | none | Muk |
| `cc/dispatch`, `cc/runner` | Kahn order; every capsule call | `Tool`, `ToolCard` (set `id` explicitly, since the default is a uuid), `LocalFunction`, `ToolMgr`; wraps `Tool.invoke` as `core/session/tracer/decorator.py` `decorate_tool_with_trace` does; `harness/security/permission_engine` | Xiaoyang · Muk |
| `cc/observe` | spans, Bindings, gate results | `harness/observability`, KV stores | Xiaoyang |

**Why the runner wraps the tool itself:** workflow `ToolComponent` calls skip rails today
(`core/workflow/components/tool/tool_comp.py`).

## 6. Rules the design keeps

- **Capsules assess or produce; control decides.** Gates, the planner, freeze and delivery are never capsules
  ([[The Ceiling]]).
- **A capsule points at code and never holds it** (`identity.carrier {ref, sha256}`). Leaf or composite, never
  both. No task is written inside a capsule.
- **No capsule is its own final judge.** Internal checks are allowed, but they are never evidence.
- **Block only for safety; label for quality.**
- **Everything is keyed by hash and append-only.** The one moving pointer is the latest version.
- **Declare first, then check.** The author declares `effect_class` (`pure`, `read_only`, `idempotent`,
  `compensable`, `irreversible`) and state; the gate checks them.
- **Review rules from week 1, so that M3–M5 stay possible:**
  - load only through the runner, one record per load;
  - address capsules by `decl_hash`;
  - write `lineage.parent` and never overwrite a version;
  - keep Symphony's plan shape;
  - resolve capsules only through Symphony's index;
  - dispatch on `identity.kind`;
  - no shared mutable state.

## 7. Getting to M2 (the planner)

- **What the planner does:** a hard filter, then backward chaining over declared ports, with a depth limit and a
  cycle check.
  - Two fits is an error; it never guesses.
  - Preconditions are checked through the same evaluator, and only at planning when no upstream step changes the
    state they read.
  - Nothing fits: return `needs_input`, or write a gap Finding.
  - Output uses Symphony's plan shape.
- **Chain by our own declared ports.** Symphony's graph waits for M3.
- **Settle during M1**, or M2 means migrating records:
  - the contract's typed want/given and allowed-capsule set;
  - one type vocabulary with an owner (reuse Symphony's type-compatibility check in
    `shared/fingerprint/normalization.py`);
  - a `state_source` field for preconditions (missing from the JSON);
  - the gap Finding's fields (agree them with RSI).
- **Also needed for M2:**
  - freeze and dispatch for n nodes, with Bindings recording edges;
  - node-gate ownership (verification);
  - M2's boundaries (PRD).

## 8. Symphony: tools versus skills

- **Where the restriction is.** `capability_type` is a free string for providers and fingerprints
  (`normalization.py:428` keeps unknown types). Four checks restrict non-skills:
  - the graph build (`orchestration/graph/build.py:161`);
  - observations (`observation/contracts.py:161`);
  - skill-pack rendering (`flow/render.py:228`);
  - the retrieval scanners (skill or plugin only).
- **Why it exists:** jiuwenswarm, Symphony's only consumer, executes plan nodes as skills (its orchestration rail
  requires `symphony_compose_graph` before `skill_tool`).
- **M1 is not blocked.** It uses the index only, and our runner executes tools itself. A week-2 test should
  confirm a `tool` descriptor is indexed.
- **For M2/M3, recommended: an upstream PR.** Configurable graph types (defaulting to today's three), and tool nodes
  allowed in observations; the skill-pack check stays. Fallback: wrap tools as skills (this adds a model hop).

## 9. The major schemas, and what is needed up to M3

The full ranked list is in [[Post-Meeting 2026-09-25 - Schema Map]]. It traced the M4 map: 16 schemas, ranked by
edges.

- **The two most connected:**
  - the **Capability Capsule Declaration** (36 edges, 11 components);
  - the **observability record** (30 edges).
- **Then:** Binding and run contract, Verdict, semantic contract, Plan, Finding, Standing, the Symphony descriptor and
  plan graph, the candidate package, the test suite and check registry, request and intent, delivery,
  preconditions, and the policy.
- **Not defined at all yet, and needed from M1:** the observability record and the candidate package (an author's
  submission to `gate.admit`).
- **Out of scope until M4+:** the workflow version (meta-RSI), merged candidates, the Declaration's `members`,
  `structure`, `wiring` and `evolution`, RSI reading lineage, Symphony flow and merge.

## 10. The original RequirementIR (AI4Research), assessed

- **What it is:** `solar.requirement_ir.v2`, emitted by `harness/lib/requirement_compiler`. A model fills a template
  the program owns; deterministic checks admit it; the reviewer is advisory. Budget: 3 calls, 1 repair.
- **What each requirement holds:** `source_refs`, `acceptance`, and a `check` that must be a registered check id
  (`config/evaluation-checks.v1.json`: 43 checks, 23 deterministic).
- **Good:**
  - traceability and coverage admission;
  - hash-pinned handoffs;
  - model writes, code admits;
  - format checks passed on 25/25 native runs and 23/25 live runs.
- **Bad:**
  - across 110 live requirements, only 4 checks were used, and **all 4 are semantic (judged)**, so nothing could
    block;
  - statements are templated from the intent text;
  - there is no typed want/given and no capsule;
  - the model path is unevaluated;
  - the standalone schema describes v1.
- **For M1, keep the skeleton, and:**
  - add typed want/given and allowed capsules;
  - add at least one deterministic check per requirement;
  - write a v2 schema file.

IntentIR v3 (`harness/schemas/compiler/intent-ir.v3.schema.json`) can be used as it is.

## 11. Where everything is

| What | Where |
|---|---|
| Shared team docs (the team edits these) | `capsule-openjiuwen/team/`: `M1-DESIGN.md` (draft 1.1), `SCHEMA-EXPLAINED.md` (every field, and the JSON-against-text audit: 8 mismatches in M1 fields, 16 more), `examples/count_spaces.json`, `render_mermaid.py`. Copy in `tundle/ai4research/architecture/team/` |
| Normative schema | `capsule-openjiuwen/merged/capsule.schema.json`, `policy-m1.json`, `validate_capsule.py`; text `SCHEMA.md` v2.10b |
| M1 map | source `capsule-openjiuwen/merged/figures/big-picture/m1_picture.py`; page https://claude.ai/artifact/Xh72oWggRhSTc5WuuXh5GS |
| Big-picture (M4) map | `big_picture.py`, same folder; page https://claude.ai/artifact/NFknMZ8ow37Tyc98tUTpAn |
| Presentation 3 (architect plan, 13 slides) | `tundle/ai4research/architecture/`; source `capsule-openjiuwen/merged/pres3/` (`figs_p3.py` → `build_spec_p3.py` → `build_deck_p3.py`); preview https://claude.ai/artifact/J6fpUeAMeGfsE8ptk9fEnm |
| Earlier decks | `tundle/ai4research/capability-capsule/` (presented 09-23, post-presentation, Part A, layer 2) |
| High-resolution PNGs of every deck and diagram | `huawei/slides-png/` (outside the tundle; README there) |
| Papers used in presentations 1–3 | `tundle/ai4research/papers/papers-used-in-presentations-1-3.txt` |
| agent-core source | `huawei/openjiuwen/agent-core/openjiuwen` at `e23806c1` |
| The archive | `huawei/stellven/AI4Research` |

## 12. Open decisions and blockers (as of 2026-09-25)

1. **Which repository the team shares.** `capsule-openjiuwen` has no remote.
2. **The contract:**
   - adopt the AI4Research IR files as data?
   - add typed want/given, allowed capsules, and deterministic checks to RequirementIR;
   - who owns the IR schemas.
3. **WP0 schema fixes:**
   - the M1-field mismatches;
   - `state_source`;
   - `lineage.relation` for a root;
   - `judge`/`judged`.
4. **Module owners and frozen interfaces.**
5. **A routing interface:** `pick(needs.model, context) → {model_id, version, params}`, with `review_fidelity` on a
   different model family from `compile_intent`.
6. **PRD boundaries and acceptance criteria** for M1 and M2.
7. **Small decisions with defaults:**
   - pin `e23806c1`;
   - the pre-freeze stage record;
   - index-only for tool capsules;
   - CLI frontend;
   - the "no capsule in delivery" contradiction in [[Directives]] 2026-09-25, which Muk should fix.
8. **Next investigation:** the schemas up to M3, starting with the observability record and the candidate package
   ([[Post-Meeting 2026-09-25 - Schema Map]]).

## 13. How we work

- **Record decisions in this vault as they happen.** Update existing notes and keep them clean;
  [[Directives]] holds Muk's binding rules.
- **Adversarial reviews use Opus** (since 2026-09-25), one reviewer at a time. Check every finding in source before
  applying it.
- **Evidence standard:**
  - cite code by `path:line`;
  - never cite a value read off a figure;
  - mark design as design;
  - never overclaim.
- **Builds and tooling:**
  - `.pptx` and `.docx` builds refuse while PowerPoint is open: ask Muk to close it, never force;
  - Python `write_text` writes CRLF on this machine, so patch files with bytes;
  - the tundle is released with `tools/tundle.sh release "…"` and pruned to 5 versions
    (`tools/tundle.sh prune --yes`); `code/` in the tundle is a snapshot, refreshed with
    `tundlekit bundle snapshot` and never edited in place.
- **Experiments this month:**
  - parity and tamper;
  - authoring cost;
  - blue-team drills.

  Contract tests against the agent-core pin are deferred.

Related: [[HANDOFF]], [[Directives]], [[Capability Capsule]], [[Milestone Ladder]], [[Presentation 3 - Architect]],
[[Post-Meeting 2026-09-25 - Schema Map]], [[Layer 2 Presentation]], [[Open Questions]].
