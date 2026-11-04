# openJiuwen: what it is, and what AI4Research's relationship to it is

Written 2026-09-11. Sources: the four repos cloned to `C:\Users\mukch\projects\work\`
and the openJiuwen paper `papers/2608.27969` (read in full).

| Repo | HEAD read | Notes |
|---|---|---|
| `agent-core` | `6ecf8218` (2026-09-11), ⚠ untagged (`git describe`: `v0.1.16.post5-256-g6ecf8218`); package version 0.1.18 | 2,415 commits since 2025-12-20; 2,530 `.py` files under `openjiuwen/` |
| `jiuwenswarm` | `b7da9ef98` (2026-09-11) | ⚠ **2,537 commits** since 2026-03-03 (1,613 is its `.py` file count); package name `workswarm` 0.2.5.beta1 |
| `sciencediscovery` | `537107e` (2026-09-11) | 609 commits since 2026-08-14 |
| `deepsearch` | `62aa0e3` (2026-08-07) | |
| `AI4Research` | `b0bf165f9` (2026-09-08) | the same commit every `[verified]` mark in `notes/` attests to |

Provenance marks as in `HANDOFF.md` §3: `[verified]` = read in source this session ·
`[paper]` = stated in 2608.27969 · `[web]` = GitHub/WebFetch page, not re-checked.

---

## ⚠ 0. Two corrections to the existing notes

1. ⚠ **"jiuwenswarm is not a thing" is wrong outside the repo.** `00-orientation.md`,
   `GLOSSARY.md` and `report/VARIANT-3-full-report.md` §1.4 all say the string does not
   occur in the AI4Research tree. That is still true `[verified]`, but
   `github.com/openJiuwen-ai/jiuwenswarm` is a real repository and openJiuwen's
   flagship multi-agent product `[verified]`. Anyone who says "jiuwenswarm" almost
   certainly means that, not AI4Research.
2. ⚠ **"`openJiuwen-Solar` is only a branch name" understates it.** It is also the
   **product name**. The pipx package is `openjiuwen-solar`
   (`distribution/pipx/pyproject.toml:6`), the installer banner reads
   "OpenJiuwen Solar" (`lib/installer/wizard.sh:148`), and the release title is
   "OpenJiuwen Solar v1.0.0-rc.9" (`docs/RELEASE-CHECKLIST.md:15`) `[verified]`.

## 1. The relationship, stated exactly

**AI4Research ships under the openJiuwen name but does not run on openJiuwen code.**
At `b0bf165f9`, zero files import `openjiuwen`, and no dependency file names
`openjiuwen`, `agent-core` or `jiuwenswarm` `[verified]`: the only hits for `jiuwen`
are branch names, CI triggers, the package and installer branding, and release
notes. Command:

```
rg -i "from openjiuwen|import openjiuwen|openjiuwen[>=<~ ]|agent-core|jiuwenswarm" AI4Research
```

So "implementing on top of openJiuwen" is **a direction, not the current state**. The
report must say which of these it means:

- Rebrand only: AI4Research stays its own runtime inside the openJiuwen family
- Port: AI4Research's stages are rebuilt on agent-core primitives (mapping in §5)
- Contribute: AI4Research's contract layer becomes an openJiuwen module

~~Open question Q-G1: which platform?~~ **Decided by the user 2026-09-11: the
DeepSeek Harness for now ("more certain"); the contract layer is to be *added to*
openJiuwen later (the "Contribute" option above), not a runtime port.** The openJiuwen
paper itself names the DeepSeek Harness as a peer harness with "plugin-level
composability" `[paper p1-2]`, so the two are alternatives, not layers.

## 2. What openJiuwen is

An open-source agent platform from Huawei (Apache 2.0) `[verified: LICENSE]`. Its own
overview describes three parts: **Core** (SDK and runtime), **Studio** (low-code visual
orchestration) and **Ops** (evaluation and observability)
(`agent-core/docs/en/1. Product Overview.md`) `[verified]`. It names Pangu, Qwen and
DeepSeek as supported model families.

### The GitHub organisation (10 repos) `[web]`

| Repo | Role |
|---|---|
| `agent-core` (Python) | the SDK: agents, workflow engine, harness, teams, evolution |
| `agent-core-java` | Java port |
| `jiuwenswarm` | flagship multi-agent product built on agent-core; chat-app channels; Skill Hub; skill self-evolution |
| `agent-studio` | zero/low-code visual development |
| `agent-runtime` | production deployment and management |
| `agent-memory` | long-term memory module |
| `agent-infer` | vLLM-based inference for agentic workloads |
| `skillhub` | skill hosting and distribution |
| `deepsearch` | deep search and research framework; README: "Segment-level provenance / Validated citations" (`README.md:29-31`) |
| `sciencediscovery` | "all-in-one AI research workstation" |

`jiuwenswarm/pyproject.toml` pins agent-core by git revision `14a7fe2d…` `[verified]`,
so jiuwenswarm really is built on agent-core.

## 3. agent-core, module by module `[verified]`

| Module | What it holds |
|---|---|
| `core/single_agent` | `ReActAgent`, the current single-agent API |
| `core/workflow` | `WorkflowAgent` engine; components `flow/` (start, end, branch, loop), `llm/` (LLM call, ReAct, **questioner**, **intent detection**), `tool/`, `resource/` (memory, knowledge retrieval), `condition/` |
| `core/graph` | graph executor with a **Pregel** engine (`core/graph/pregel/engine.py`): async parallel node execution, channels, checkpointed state |
| `core/session`, `core/runner` | sessions, interrupt/resume, `Runner.resource_mgr` (process-global) |
| `core/sys_operation`, `core/security` | local and sandboxed file/shell operations |
| `harness/` | **DeepAgent**: ReAct inner loop + task loop, **Rails**, tools, subagents, workspace, tiered permission engine (`security/`: `tiered_policy`, `file_guard`, `shell_ast`), **Goal Mode** (`goal/`), LSP feedback (`lsp/`), declarative manifest assembly (`manifest/`) |
| `agent_teams/` | leader + teammates; **Swarm Flow** workflow engine (`agent_teams/workflow/engine/`) |
| `symphony/` | capability assets: fingerprint, retrieval tree, **capability graph and orchestration planner**, evaluation, experience |
| `agent_evolving/` | skill and prompt evolution, trajectory evaluators, online RL |
| `rsi/` | recursive self-improvement: `harness_rsi` (auto-harness) and `artifact_rsi/paper_opt/auto_research` (§6) |
| `extensions/` | A2A, MCP, OTel tracing, context evolver, checkpointers, stores |

Architecture rule worth quoting (`.claude/rules/architecture.md:20-23`): "Cards are
static metadata, serializable and transportable; Configs are runtime objects holding
resources and state. This separation enables Cards to cross process boundaries (e.g.,
A2A protocol) while Configs remain process-local singletons." That is the same split AI4Research makes between a
frozen contract and the mutable ledger.

### The design, in the paper's words `[paper]`

2608.27969 organises the harness around 2 properties:

- **Structural Composability**: one execution substrate, an Inner Loop (bounded
  ReAct step loop) inside an Outer Loop (task-level continuation, retry, recovery),
  reused unchanged by single agents, delegated sub-agents and multi-agent Swarm Flow
  (§3.1.1)
- **Rails**: cross-cutting capabilities (security, memory, planning, context,
  delegation, human interaction) attach to lifecycle hooks as
  ρ = (H_ρ, f_ρ, p_ρ), with explicit priority so composition order is metadata, plus
  visibility gating g(ρ, u) per execution subject (§3.1.2, Eq. 1-3)
- **Swarm Flow operators**: `budget()`, `parallel()`, `compact()`, `pipeline()`,
  `agent_session()`, `human()`, `return` (§3.1.3)
- **Runtime Adaptivity** around a *fixed* model policy π: Context Management
  (progressive compression, offload to handles), **Goal Mode** (continue / complete /
  blocked, separated from hard resource caps; self, independent or hybrid
  assessment), LSP-driven passive feedback, and Self-Reflection across tasks (§3.2)

Results `[paper, Tables 1-2]`: SWE-bench Verified **82.6%** (Claude Opus 4.5, high), and
Terminal-Bench 2.1 **87.19%** (GPT-5.6 Sol) and **84.04%** model-matched on Fable 5
against Claude Code's 83.8% (⚠ openJiuwen at "high" reasoning effort, Claude Code at
"xhigh", Table 1). Two limitations the paper states itself:

- Leaderboard comparisons differ in prompts, tools and implementations, so they are
  "system-level comparisons rather than controlled estimates of the contribution of
  the harness alone" (§4.3)
- No ablations of individual mechanisms yet (§5)

**Scope note for the report:** every openJiuwen number is on **coding** benchmarks.
None measures research work.

### Swarm Flow engine, the part closest to AI4Research's scheduler `[verified]`

`agent_teams/workflow/AGENTS.md`: a workflow is a Python script (`META={...}` +
`async def run(args)`) using `agent()` / `parallel()` / `pipeline()` / `phase()`. The
engine is kept business-agnostic and carries:

- `journal.py`: **content-addressed resume** keyed by call path + signature, so a
  resumed run replays cached calls instead of paying again
- `budget.py`: a `BudgetLedger` with **single writer** (the backend records, the
  engine only reads), enforced both per model call (a rail force-finishes) and at
  engine entry
- `concurrency.py`: three-level admission (L1 max workflows, default 16; L2 agents per
  run, default min(16, cpu−2); L3 total agents, default 64)
- **Iron rule 2**: "structured output goes through a tool, not prompt parsing". Workers
  submit results through `StructuredOutputTool` with a JSON schema

## 4. Symphony: openJiuwen's own capability-graph layer `[verified]`

`openjiuwen/symphony/README.md` (Chinese; gloss mine). "Trees for retrieval, graphs
for orchestration":

- **Capability fingerprint**: semantic profile, normalised I/O, tags, content hash,
  quality result, written atomically with a schema version (implemented)
- **Capability graph + planner**: relation edges (`can_feed`), versioned immutable
  `graph.json`, atomic `current.json` switch, Fast (one LLM call) or Beam planning,
  output is a `planned_graph` in JGF v2 (implemented)
- **Retrieval tree** and **Agent Toolkit**: "to be migrated in" (not implemented)
- **Evaluation**: registered static and trajectory metrics that keep reason, evidence,
  failure and suggestion; it deliberately **does not fix admission thresholds**
- **Graph evolution from runtime evidence**: only strongly verified success, or an
  edge-level failure with an explicit evidence reference, may change weights; weak
  evidence, network errors and truncated traces are kept "for audit only"

This is directly relevant to both reports. It is openJiuwen's answer to "which
capability, composed how", and it overlaps AI4Research's capsule composition search.

## 5. Mapping AI4Research stages onto openJiuwen `[proposed]`

What exists in openJiuwen for each AI4Research stage. "Gap" means nothing in
agent-core does the job today.

| AI4Research stage | Nearest openJiuwen primitive | Fit |
|---|---|---|
| Intent compilation (IntentIR + validation + fidelity + acceptance) | `workflow/components/llm/intent_detection_comp.py`, `questioner_comp.py`; `StructuredOutputTool` | partial: intent *routing* and clarification exist; no typed IR, no deterministic re-binding of source spans |
| Requirement compilation (constraints locked, independent review) | Goal Mode goal + independent assessment | partial: a goal, not a contract |
| **Freeze** (hash-verified contract with evaluation criteria inside) | Swarm Flow journal (content-addressed replay); Symphony immutable graph versions; auto_research host-validated `SubtaskContract` per round | **gap**: nothing freezes a whole plan *and its grading rules* before execution |
| Scheduler (DAG, write-scope conflicts, readiness) | `core/graph` Pregel engine; Swarm Flow `parallel`/`pipeline` | good fit for execution; no write-scope conflict model |
| Dispatch (leases, idempotency, fingerprint dedup) | journal signature replay; ConcurrencyGovernor L1-L3; BudgetLedger | good fit, and stronger on budget |
| Logical/physical operators | `AbilityManager` + Card/Config split; model resolver | partial |
| Capability capsules | Symphony fingerprints + graph; Skills + skillhub; Rails | partial: no declared pre/postconditions or trust class; effects only as a tool-level `idempotent` flag on `ToolCard` (`core/foundation/tool/base.py:53-60`) |
| Gates and evaluators | Goal Mode; `agent_evolving/evaluator`; Symphony `EvaluationSuite` | partial: evaluators exist; nothing is frozen per run |
| Claims and evidence ABI | `deepsearch` segment-level provenance; `sciencediscovery` Claim / EvidenceItem / EvidenceLink + CAS | partial: provenance exists; no per-claim verdict (artifact-level review does have closed decisions and finding codes) and no no-upgrade gate |
| Security | harness tiered policy, file guard, shell AST, `PermissionInterruptRail` | **stronger than AI4Research's general tool-permission layer**, whose `capability_token.check_path_access()` has no production callers (VARIANT-3 §9); AI4Research's enforcement is limited to experiment sandboxing (no network, bounded writes) and write-scope scheduling |

Thus the port is uneven. openJiuwen supplies the execution substrate, concurrency,
budget and security that AI4Research built by hand over files and tmux. AI4Research
supplies what openJiuwen lacks: **the typed contract and its freeze**.

## 6. openJiuwen already has its own auto-research pipeline `[verified]`

`openjiuwen/rsi/artifact_rsi/paper_opt/auto_research/` is an end-to-end research
pipeline inside agent-core. This is the most important finding for the SoTA section:
the comparison is not only against external systems.

- **Modules**: `topic_survey` → `experiment_design` → `code_implementation` →
  `experiment_execution` → `reflection` → `reporting` (LaTeX paper via skills
  `ts-plan`, `ts-write`, `ts-figure`, `ts-review`, `ts-latex`), plus a standalone
  `paper_scoring`
- **Control**: an LLM **manager** emits a `ManagerDecision` (`EXECUTE` with a
  `SubtaskContract`, `DONE`, or `BLOCKED`). `pipeline/transitions.py` is titled
  "Host-side validation for manager decisions, contracts, and DONE claims" and rejects
  illegal moves deterministically: e.g. "execution requires a ready implementation",
  "failed execution must be repaired via code_implementation before another
  execution", "cannot mark … completed without a successful report id", and a `DONE`
  is rejected while requirements are pending (f-strings `f"DONE rejected: {reason}"`
  at `transitions.py:602` and `f"pending requirements: …"` at `:614`)
- **Budgets** (`configs/pipeline.default.yaml`): max 50 rounds, 3 surveys, 4 code
  retries, 6 design revisions, 4 execution retries, 3 reporting retries
- **Claim status**: `modules/reporting/evidence.py` is "a host-only, no-model-call"
  classification of how new numbers compare to prior-paper numbers
- **Paper scoring**: a dual rubric (general: soundness, clarity, contribution;
  experiment: question alignment, controls, statistics, reproducibility,
  claim-evidence alignment) with 5 rubric samples at temperature 0

**The design thesis is the same as AI4Research's** (the model decides, the host
validates), **but the contract is per round, not per run.** AI4Research freezes one
global plan with its grading rules inside the hash, then executes. openJiuwen's
manager renegotiates a contract every round, and the host only checks that each move
is legal. That is the sharpest single contrast between the two systems. It is also
the freeze-versus-adaptivity trade the openJiuwen paper argues for ("decisions made
before execution … become progressively stale", 2608.27969 p3), though that sentence
is about framework decisions within one coding task, not research-plan freezing.

## 7. sciencediscovery: openJiuwen's research workstation `[verified]`

- TypeScript/Node control plane; runtime core with 4 ports (`ContextAssembler`,
  `ModelClient`, `ToolDispatcher`, `RunEventSink`) and a frozen port registry
  (`docs/architecture/runtime-core.md`)
- **Does not use agent-core.** `services/gateway/pyproject.toml`: "The agent loop,
  model clients, MCP client, and web providers all run natively in the Node control
  plane, so nothing here needs a web framework, an agent framework, or the vendor
  harness."
- Provenance model (`docs/en/explanation/review-provenance.md`): SHA-256 CAS for
  code, stdout, prompts and responses; every model turn gets a Prompt Manifest;
  sentence-level `Claim` → `EvidenceItem` (mcp-record, paper, execution, artifact,
  remote-job, user-input) → `EvidenceLink` (`supports` / `context` / `contradicts`);
  `fullTextRetrieved` becomes true only after a successful PDF extraction
- Review is **advisory**: "Findings are read-only and do not mutate an Artifact or
  force another run"
- Self-described: "not a multi-user production service", for "trusted local or
  workstation use" (README) `[web]`, the same positioning as AI4Research

## 8. Open questions

- ~~Q-G1 Target platform~~ **Decided 2026-09-11: the DeepSeek Harness for now.**
- ~~Q-G2 Port or contribution~~ **Decided 2026-09-11: add the contract layer to
  openJiuwen (contribution), later.** §5's mapping becomes the design brief for that layer.
- **Q-G3** Should the report compare against openJiuwen's own `auto_research` by name?
  It is the most direct competitor, and it is internal to the platform.
