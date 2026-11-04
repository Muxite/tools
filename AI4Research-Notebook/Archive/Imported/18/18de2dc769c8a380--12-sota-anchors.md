# SoTA Comparative Anchors — AI4Research / OpenSolar (Solar)

Repo: /home/muk/work/AI4Research, branch openJiuwen-Solar, HEAD b0bf165f9
Method: grep + read only, read-only investigation, no web access. All external
references below are cited file:line. Analogues I propose (not found in repo)
are explicitly marked `[MY SUGGESTED ANALOGUE - unverified]`.

## Summary

- The repo tracks a concrete upstream project called **AutoSci** (a native
  skills-based research-agent CLI, expected checked out as a sibling repo
  `../AutoSci`) via dedicated parity tooling, route matrices, and a
  self-reported **"not full parity"** runtime audit — this is the strongest,
  most falsifiable comparison surface in the repo.
- A large, explicit self-authored competitive-positioning document
  (`docs/SOLAR_UNIQUENESS_ANALYSIS.md`, in Chinese) names and scores Solar
  against Copilot, Cursor, Windsurf, Claude Code, Devin, Aider, Cline, AutoGPT,
  LangGraph/LangChain, CrewAI, and ChatGPT Agent across 12 dimensions —
  entirely self-claimed, non-adversarially-verified, and internally admits
  weaker model-flexibility and macOS lock-in.
- A dedicated benchmark-adapter layer (`harness/lib/agent_arena_benchmark.py`,
  `harness/lib/benchmark/`) enumerates **real, named, published benchmarks**
  it intends to (or does) adapt to: SWE-bench / SWE-bench Pro, Terminal-Bench
  2.0, BrowseComp, OSWorld, GAIA, WebArena, tau-bench — with explicit
  "does not claim a leaderboard result unless actually run" language, and one
  fully sourced adapter design doc (Terminal-Bench 2.0) citing arXiv, GitHub,
  and vendor blog sources with URLs.
- A demo content pack (`harness/demo-rsi/source-pack/`) cites nine real,
  named papers on recursive self-improvement / self-refinement / verifier
  reward models / automated science (Good 1965, STaR, Self-Refine, Reflexion,
  Tree-of-Thoughts, "Let's Verify Step by Step", **The AI Scientist** /Sakana
  AI, Coscientist) as demo seed material — the pack's own metadata flags
  citation details as "best-effort... MUST be verified," i.e. not vetted.
- The system's own architecture vocabulary (frozen hash-verified task
  contracts, capability capsules with declared effects/pre/postconditions,
  logical/physical operator indirection, filesystem-based dispatch, lease +
  capability-token scoping, activation-proof telemetry with write-scope
  coverage) has no internal citations to prior art at all — the neutral
  mechanism catalogue below is my own vendor-neutral restatement for a web
  researcher to check against published literature.

---

## Upstream & Parity Findings

### AutoSci (primary tracked upstream)

Files:
- `harness/tools/autosci_upstream_parity.py` — a same-prompt comparison
  runner: it runs Solar's own `autosci_bridge.py research` entrypoint and
  optionally an externally configured upstream CLI (via `--upstream-command`,
  a JSON argv template with `{prompt}` substitution) on the identical prompt,
  then diffs six semantic fields: `intent`, `workflow_stages`, `input_type`,
  `language`, `deliverable_type`, `required_evidence` (lines 1-24, 90-120).
  If no upstream command is configured it reports `PARTIAL` /
  `upstream_command_not_configured` rather than fabricating a comparison
  (lines 96-104).
- `harness/tools/autosci_parity_inventory.py` — a deterministic route-parity
  auditor. `DEFAULT_NATIVE_REPO = REPO_ROOT.parent / "AutoSci"` (line 16),
  i.e. it expects a sibling checkout of the actual AutoSci project at
  `../AutoSci`. It scans `AutoSci/i18n/en/skills/*/SKILL.md` and
  `AutoSci/.claude/skills/*/SKILL.md` (lines 60-68) to discover the native
  skill set, then cross-references Solar's own route config
  (`harness/plugins/autosci/config/feature_parity_routes.v1.json`), operator
  bindings, capability registry, plugin manifest, logical/physical operator
  configs, and evidence-schema-to-gate mapping (`GATE_BY_SCHEMA`, lines 29-46)
  to compute per-skill coverage status.
- `harness/plugins/autosci/bin/autosci_parity_bridge.py`,
  `autosci_bridge.py` — the actual physical-operator bridge into AutoSci
  backend actions.
- `harness/schemas/evidence/autosci_feature_parity.v1.schema.json` and
  `harness/evaluators/scientific/autosci_feature_parity_gate.py` — a typed
  evidence schema + deterministic gate that fails a "Phase 19" gate if any
  native skill has no Solar route (`missing` status).

### AutoSci feature inventory (28 native skills tracked)

From `docs/integrations/autosci/autosci-solar-feature-parity-matrix.md`
(full table read at lines 63-89 of that file): the 28 AutoSci slash-skills
are `/ask`, `/check`, `/daily-arxiv`, `/discover`, `/edit`, `/exp-design`,
`/exp-eval`, `/exp-pilot-eval`, `/exp-pilot-run`, `/exp-run`, `/exp-status`,
`/ideate`, `/ingest`, `/init`, `/novelty`, `/paper-compile`, `/paper-draft`,
`/paper-plan`, `/poster`, `/prefill`, `/rebuttal`, `/refine`, `/research`,
`/reset`, `/review`, `/setup`, `/survey`, `/visualize`. Each is mapped to a
Solar capability capsule, logical operator, backend action, evidence ABI
schema, a coverage status (`full`/`partial`/`gated`/`missing`), and a side-
effect policy (`none`/`dry_run_only`/`approval_required`).

Coverage snapshot (same file, "Inventory Snapshot" table): 28 native skills
scanned, 28 Solar routes configured, 0 missing, 0 full, 18 partial, 10
approval-gated, 0 blocked.

### Self-reported non-parity (important honesty signal)

The same doc's "Audit-Adjusted Runtime Completion" section (referencing
`docs/integrations/autosci/audit/migrated-autosci-parity-audit-2026-06-25.md`)
states the migrated runtime is **"not full parity"**: SkillGen PDF ingestion
failed semantic validation, integrated `/research` did not run an
end-to-end lifecycle, experiment deploy used fixture evidence, and paper
compile did not produce a PDF. Final runtime verdict: `failed`. Breakdown:
0 native-full runtime stages, 5 partial, 4 gated-unexecuted, 1 fixture-only,
5 schema-only, 4 failed, 4 missing stages. As a result the project
deliberately keeps `coverage_status=full` unused in its own route config
until "source-grounded, non-fixture runtime evidence" proves otherwise.

Related parity/upstream files not deep-dived (listed for completeness):
`docs/UPSTREAM-EXPORT-REQUEST.md`, `tools/semantic_parity_audit_matrix.py`,
`tools/semantic_parity_runtime_proof.py`,
`docs/product/lane4-deepdive-parity-report.md`,
`tests/harness/test_frontdoor_ingress_parity.py`,
`docs/integrations/autosci/full-parity-progress-report.md`,
`docs/integrations/autosci/parity-to-unification-handoff.md`,
`docs/integrations/autosci/native-parity-gap-matrix.md`,
`tests/harness/research_orchestration/fixtures/upstream_research_parity_contracts.json`.

---

## External References Table

| System / work | Where referenced | Role (per repo) |
|---|---|---|
| **AutoSci** (native skills research CLI) | `harness/tools/autosci_upstream_parity.py`, `autosci_parity_inventory.py`, `harness/plugins/autosci/*`, `docs/integrations/autosci/*` | Tracked upstream/competitor for feature parity; expected sibling checkout `../AutoSci` |
| **SWE-bench / SWE-bench Verified / SWE-bench Pro** | `harness/lib/agent_arena_benchmark.py` PUBLIC_BENCHMARKS list (swebench.com, scale.com/blog/swe-bench-pro); `docs/SOLAR_UNIQUENESS_ANALYSIS.md` dimension 11 (cites Claude Opus 4.5 + Live-SWE-agent 79.2%, Gemini 3 Pro 77.4%, Claude Sonnet 4.5 45.8%, Claude 3.7 Sonnet 62.3%, "Nov 2025") | Benchmark integration target; comparison metric cited as self-claim evidence |
| **Terminal-Bench 2.0 / Harbor framework** | `harness/docs/benchmark/terminal-bench-2.md` (cites LangChain blog, Harbor GitHub README, Terminal-Bench GitHub, arXiv:2601.11868, Harbor Registry — full URLs given); `harness/lib/benchmark/terminal_bench.py`, `harbor_adapter.py` | Benchmark adapter target, implemented via Harbor's `harbor run --dataset terminal-bench@2.0` CLI shape |
| **BrowseComp** (OpenAI) | `harness/lib/agent_arena_benchmark.py` (openai.com/index/browsecomp) | Benchmark integration target |
| **OSWorld** | same file (os-world.github.io) | Benchmark integration target |
| **GAIA** | same file (huggingface.co/datasets/gaia-benchmark/GAIA) | Benchmark integration target |
| **WebArena** | same file (webarena.dev) | Benchmark integration target |
| **tau-bench** (Sierra Research) | same file (github.com/sierra-research/tau-bench) | Benchmark integration target |
| **MLE-bench** | `harness/docs/benchmark/terminal-bench-2.md` line ~19 ("future adapters e.g. SWE-bench, OSWorld, MLE-bench") | Named as future adapter target, not yet implemented |
| **Hermes Agent (NousResearch)** | `harness/lib/agent_arena_benchmark.py` `HERMES_REPO = "https://github.com/nousresearch/hermes-agent.git"` | Vendored comparison agent for arena benchmark |
| **Claude Code** | Pervasive throughout repo (`CLAUDE.md`, docs, `docs/SOLAR_UNIQUENESS_ANALYSIS.md` comparison tables) | Both the underlying runtime/overlay this ships as ("Claude Code overlay" per `CLAUDE.md`) AND a named competitor in self-claim comparison tables |
| **MCP / Model Context Protocol** | `harness/docs/managed-agent-runtime.md`, `harness/docs/architecture/mcp-policy-guard-rationale.md`, `core/mcp/*`, `docs/SOLAR_UNIQUENESS_ANALYSIS.md` (cites "MCP 协议" as Claude Code's extensibility mechanism, scored ⭐⭐⭐⭐) | Integration mechanism used by the project itself (own MCP servers under `core/mcp/`) and cited as a competitor capability |
| **Copilot (GitHub/Microsoft)** | `docs/SOLAR_UNIQUENESS_ANALYSIS.md` (comparison tables throughout) | Named competitor, self-claim comparison only |
| **Cursor** | same doc | Named competitor, self-claim comparison |
| **Windsurf (Codeium)** | same doc, §4.1 competitor overview table | Named competitor, self-claim comparison |
| **Devin (Cognition)** | same doc, multiple dimension tables | Named competitor, self-claim comparison |
| **Aider** | same doc, §4.1 table | Named competitor, self-claim comparison |
| **Cline** | same doc, dimension 6 (model flexibility) | Named competitor, self-claim comparison |
| **AutoGPT** | same doc, multiple dimensions | Named competitor, self-claim comparison |
| **LangGraph / LangChain** | same doc (multi-agent orchestration dimension); also LangChain blog cited as a factual source in the Terminal-Bench adapter doc | Named competitor (self-claim) AND cited as a factual third-party source for the Terminal-Bench evidence base |
| **CrewAI** | `docs/SOLAR_UNIQUENESS_ANALYSIS.md`, multi-agent dimension | Named competitor, self-claim comparison |
| **ChatGPT Agent (OpenAI)** | same doc, §4.1 and execution-scope dimension | Named competitor, self-claim comparison |
| **The AI Scientist** (Lu et al., Sakana AI, arXiv:2408.06292) | `harness/demo-rsi/source-pack/source-notes/aiscientist2024.md`, `sources.json` | Cited as real published work in a demo research-report seed corpus (topic: recursive self-improvement); citation flagged "best-effort... verify" |
| **Self-Refine** (Madaan et al., arXiv:2303.17651) | `harness/demo-rsi/source-pack/source-notes/selfrefine2023.md` | Same demo corpus |
| **Reflexion** (Shinn et al., arXiv:2303.11366) | `harness/demo-rsi/source-pack/sources.json` | Same demo corpus |
| **Tree of Thoughts** (Yao et al., arXiv:2305.10601) | same file | Same demo corpus |
| **"Let's Verify Step by Step"** (Lightman et al., OpenAI, arXiv:2305.20050) | `harness/demo-rsi/source-pack/source-notes/verifystepwise2023.md` | Same demo corpus |
| **STaR** (Zelikman et al., arXiv:2203.14465) | `sources.json` | Same demo corpus |
| **Coscientist** (Boiko et al., Nature 624, 2023) | `sources.json` | Same demo corpus |
| **"Speculations Concerning the First Ultraintelligent Machine"** (I.J. Good, 1965) | `sources.json` | Same demo corpus |
| **"Concrete Problems in AI Safety"** (Amodei et al., arXiv:1606.06565) | `sources.json` | Same demo corpus |
| **arXiv (as a data source)** | `harness/lib/hf_paper_insight/providers/arxiv_provider.py`, `arxiv_metadata.py` (both under `harness/lib/` and duplicated under `harness/tools/`) | Live integration target — literature discovery data source, not just a citation |
| **Semantic Scholar, DeepXiv, web search** | `docs/integrations/autosci/autosci-solar-feature-parity-matrix.md` "Remaining Non-Full Surfaces" | Named as external knowledge/API sources AutoSci parity depends on but Solar has not fully wired |

---

## Project's Own Uniqueness Claims (self-claims — NOT independently verified)

Source: `docs/SOLAR_UNIQUENESS_ANALYSIS.md` (Chinese-language internal doc,
dated 2026-02-03, "based on actual ~/.solar/solar.db runtime data" per its own
header). These are the project's marketing/positioning claims, not verified
facts, and describe what reads as an earlier/parallel "ontology + evolver +
persona" subsystem layer distinct from the TaskGraph/freeze/capability-capsule
architecture described in the current project context — flag this
discrepancy for the web researcher.

- Positions itself as a "self-evolving agent," not a coding assistant:
  programming is described as a substrate capability, not the product.
- Claims a three-layer memory architecture (episodic/semantic/procedural) plus
  an "ontology" snapshot and automatic reflection loop that no competitor in
  its comparison set has (§2.2/4.3 dimension 2).
- Claims system-level autonomous scheduling via macOS `launchd` (a
  self-optimizer job at 03:00, an "ontology reflector" at 04:00, a 5-minute
  task-queue executor, an HN monitor) as a differentiator vs. all listed
  competitors (§2.1.3, dimension 1) — explicitly macOS-only, acknowledged as
  a "cross-platform" weakness (§4.6).
- Provides a 12-dimension scored comparison matrix (autonomy, memory,
  personalization, multi-agent collaboration, execution breadth, model
  flexibility, persistence, self-evolution, extensibility, system
  integration, benchmark performance, governance/safety) against Claude Code,
  Cursor, Devin, AutoGPT, LangGraph, giving Solar 58/60 vs. next-best
  LangGraph at 31/60 (§4.4) — a self-authored score, not derived from any
  external benchmark run.
- Claims a governance concept it calls "监护人" (guardian) plus a "第一规律"
  (First Law) requiring confirmation before external communication, compared
  favorably to Devin's sandbox isolation and Claude Code's permission
  prompts (dimension 12).
- Explicitly concedes two weak dimensions: model flexibility (Claude-centric,
  routes other models only through an internal "brain-router" MCP) and
  cross-platform reach (macOS-only deep integration).
- Benchmark-performance claim (dimension 11) is inherited, not measured: it
  attributes SWE-bench Verified numbers to the underlying Claude model, not
  to anything Solar itself ran.

Other doc titles named in scope but not deep-read in this pass (their
existence is confirmed; content not exhaustively summarized here):
`docs/SOLAR_EVOLUTION_ANALYSIS.md`, `SOLAR_EVOLUTION_REPORT_V3.md` (+ `_OUTLINE`, `_APPENDIX_D`),
`SOLAR_TECHNICAL_REPORT_V2.md` (+ `_OUTLINE`), `AI_NATIVE_OS_ARCHITECTURE.md`,
`DISTRIBUTED_DEPLOYMENT_ANALYSIS.md`, `COMMUNITY_NEURAL_NETWORK_DESIGN.md`,
`docs/insights/2026-02-11_agent-memory-mechanisms.md`,
`docs/insights/AI-Agent-Memory-Mechanisms.md`. A follow-up pass should read
these in full before finalizing a SoTA report, since they likely contain
further self-claims about memory/evolution architecture comparable to
published agent-memory literature.

---

## Benchmarks

| File | What it measures | Standard/published benchmark used? |
|---|---|---|
| `harness/lib/agent_arena_benchmark.py` (+ `harness/tools/` duplicate) | Cross-agent reproducible benchmark harness; explicitly states it "does not claim Solar-Harness is on an external leaderboard unless the public benchmark adapter is actually configured and run." Ships a registry of 8 named public benchmarks (see table above) with per-benchmark adapter env vars and a JSON score-file contract. First supported suite is an internal "Solar smoke suite." | Yes — SWE-bench(-Pro), Terminal-Bench, BrowseComp, OSWorld, GAIA, WebArena, tau-bench (adapters scaffolded, not all shown as executed) |
| `harness/lib/benchmark/` package (`schemas.py`, `registry.py`, `harbor_adapter.py`, `terminal_bench.py`, `reports.py`, `runner.py`) | A formal `BenchmarkAdapter` protocol reusing Solar's own DAG dispatch/pane assignment/event ledger/artifact registry/evaluator chain, so external benchmarks plug into the same infrastructure as production tasks | Yes — Terminal-Bench 2.0 via Harbor is the first implemented adapter (`harness/docs/benchmark/terminal-bench-2.md`), citing arXiv:2601.11868 (89 tasks, frontier agents score below 65%) |
| `harness/lib/capability_fusion_benchmark.py` (+ `harness/tools/` duplicate) | NOT a performance benchmark by its own docstring — measures "integration quality": manifest validity, capability-registry exposure, health visibility, dispatch auto-injection, local runtime smoke, pane-level availability, with a weighted scoring rubric (manifest 15, registry 20, health 15, dispatch 20, runtime 20, pane 10) | No — internal integration-completeness score only |
| `harness/thunderomlx_cache_benchmark_agent.py` / `harness/tools/thunderomlx_cache_benchmark_agent.py` | Not deep-read this pass; name suggests local MLX inference cache performance benchmarking | Not established as a published benchmark |
| `benchmarks/mlx_quantization_bench.py` | Not deep-read; likely local MLX quantization microbenchmark | Not a published benchmark |
| `harness/tools/platform_workflow_benchmark.py`, `heavy_proof_benchmark.py`, `fixed_research_benchmark.py` | Not deep-read this pass | Unknown — flagged for follow-up |

---

## Integrations (competitive/ecosystem signal)

`harness/plugins/` directory names (each likely a wrapper/bridge around, or
inspired by, an identically-named external project — names alone are
suggestive, not confirmed without reading each plugin's manifest):
`gemini_deep_research`, `gepa_optimizer`, `addy-agent-skills`,
`agency-agents`, `atlas`, `autoresearch`, `autosci` (the tracked upstream,
see above), `browser-use`, `empirical-research`, `everything-claude-code`,
`gstack`, `markitdown` (matches Microsoft's MarkItDown), `mermaid`, `mineru`
(matches OpenDataLab's MinerU PDF parser), `mirage`, `obsidian`,
`openai-agents-python` (matches OpenAI's Agents SDK), `owl` (possibly
CAMEL-AI's OWL multi-agent framework), `qmd`, `ruflo`, `superpowers`,
`understand-anything`.

`integrations/` top-level: `gemini_deep_research`, `gepa_optimizer`,
`obsidian-wiki-bridge.sh`, `obsidian-wiki-export.sh`, `obsidian-wiki.sh`,
`solar-config-server.py`, `wiki-capture-server.py`,
`wiki-solar-db-import.py`.

`components.d/` skills/component packages named in scope: `codex-bridge`
(OpenAI Codex integration), `mempalace`, `skills-browser`, `skills-calendar`,
`skills-md`, `skills-obsidian`, `skills-office`. Per `CLAUDE.md`, these are
meant to be "component-gated and off by default" unless a manifest says
otherwise — i.e. this is a large *optional* integration surface, not core
runtime behavior.

Own MCP servers: `core/mcp/git-server.ts`, `core/mcp/index.ts` — the project
both consumes MCP (per `docs/SOLAR_UNIQUENESS_ANALYSIS.md`'s framing of
Claude Code's MCP protocol) and implements its own MCP servers.

---

## Neutral Mechanism Catalogue

This is the primary payload for the external web-research assistant. Each
entry: neutral name, 2-4 sentence description in outside vocabulary (no
project jargon), and a candidate analogue I am suggesting for verification —
none of these analogues come from the repo itself.

1. **Multi-stage NL-to-typed-IR compilation before execution.**
   The system takes a natural-language goal and passes it through multiple
   compiler stages (`intent_compiler.py`, `requirement_compiler/`,
   `intent_engine_adapter.py`) to produce a structured, schema-validated
   intermediate representation (an "intent IR" and "requirement IR", see
   `harness/schemas/compiler/intent-ir.semantic.v1.schema.json`) before any
   execution graph is built, rather than letting an LLM plan step-by-step at
   run time.
   `[MY SUGGESTED ANALOGUE - unverified]`: resembles a traditional compiler's
   front-end (lexing/parsing/semantic-analysis passes before codegen), or a
   staged NLU pipeline (intent classification -> slot filling -> structured
   query) as used in older task-oriented dialogue systems.

2. **Separation of LLM-generated semantics from deterministic structural
   validation.** LLM output populates the "meaning" fields of a document
   (e.g., `intent-ir.semantic.v1.schema.json` marks certain fields as
   semantic/model-authored), while separate deterministic code (schema
   validators, `architecture_guard.py`-style checks) enforces structure,
   types, and invariants independent of model behavior.
   `[MY SUGGESTED ANALOGUE - unverified]`: resembles the separation between a
   parser/AST (structure) and a type-checker or linter (semantic
   correctness) in compiler design, or schema validation layered on top of
   free-text LLM output in structured-output/function-calling systems.

3. **Independent fidelity/acceptance review artifacts, separate from
   generation.** Evidence schemas such as `artifact_review.v1`, gate scripts
   under `harness/evaluators/scientific/*_gate.py`, and a
   `capability_certification_suite.py` produce standalone pass/fail verdict
   artifacts about a generated deliverable, authored by a different code
   path than the one that generated the deliverable.
   `[MY SUGGESTED ANALOGUE - unverified]`: resembles a CI/CD "verify" stage
   separate from "build," or generator/discriminator separation in
   adversarial or actor-critic setups (though here the "critic" is rule-based
   or a separate LLM call, not co-trained).

4. **Immutable, hash-verified execution contract ("freeze") between planning
   and execution.** `harness/lib/execution_authority.py` computes a SHA-256
   digest (`digest()`, lines 18-20) over a fixed field-set of operator
   definitions (`OPERATOR_FIELDS`, excluding runtime state/credentials) and
   binds that hash into the scheduler/dispatcher path, so the executable
   contract cannot silently drift from what was planned/reviewed.
   `[MY SUGGESTED ANALOGUE - unverified]`: resembles a package manager's
   lockfile (e.g. `package-lock.json`/`Cargo.lock`) that pins a dependency
   graph by content hash, or a build system's frozen build graph /
   content-addressed build description (e.g. Bazel action graphs, Nix
   derivations).

5. **Capability packaging with declared effects, pre/postconditions,
   invariants, and trust classes.** Capability "capsules" (YAML files under
   `harness/config/capability-capsules/*.yaml`) declare applicability
   signals, typed input/output contracts, `preconditions`/`postconditions`
   checks, invariants (e.g. "an outcome without collected results maps to
   inconclusive, never to supported"), and an `effects` block covering
   read/write/execute/network/cost, plus composition rules
   (`compatible_with`/`incompatible_with`/`requires_after`).
   `[MY SUGGESTED ANALOGUE - unverified]`: resembles capability-based
   security models (object-capability systems), Unix capability bits, or
   effect systems in programming-language theory (e.g. algebraic effects,
   Haskell's IO/effect typeclasses) applied to LLM tool invocation instead of
   syscalls.

6. **Logical-vs-physical operator indirection with capability-graded routing
   and conditional failover.** `harness/config/logical-operators.json` and
   `physical-operators.json` (with a lockfile,
   `physical-operators.json.lock`) separate an abstract role name (e.g.
   `ScientificClaimVerifier`) from the concrete backend/model/CLI that
   fulfills it at a given time, allowing routing decisions and failover
   without changing the planned graph.
   `[MY SUGGESTED ANALOGUE - unverified]`: resembles a service mesh's
   logical-service-name-to-endpoint indirection (e.g. Kubernetes Services,
   DNS-based service discovery), or a database query planner's logical plan
   vs. physical plan separation.

7. **Filesystem-queue IPC for language-agnostic operator dispatch.** Workers
   (operators) are dispatched via files written to and read from disk
   (`.intent.json`-style dispatch artifacts referenced in
   `capability_effects.py`; queue/inbox-style modules in `harness/lib/`)
   rather than an in-process API or RPC call, so any language/process that
   can read/write files can act as an operator.
   `[MY SUGGESTED ANALOGUE - unverified]`: resembles classic Unix
   maildir/spool-directory queues, or a poor-man's message queue implemented
   over a shared filesystem (as sometimes used before adopting a real broker
   like RabbitMQ/Kafka).

8. **Lease + capability-token scoping of worker permissions.**
   `harness/lib/capability_token.py` and pane/lease-gate logic referenced in
   `activation_proof.py` (`lease_denied_count` field) time-box and
   permission-scope what an individual dispatched worker/pane is allowed to
   touch, distinct from the static capability-capsule declaration.
   `[MY SUGGESTED ANALOGUE - unverified]`: resembles short-lived cloud IAM
   session tokens / STS AssumeRole leases, or distributed-lock leases (e.g.
   etcd/Zookeeper leases) applied to task execution rights rather than
   resource locks.

9. **Idempotency fingerprinting with dedup and cooldown.** Multiple modules
   (`event_ledger.py`, `capability_activation_proof.py`, `runtime_bridge.py`,
   `session_tools.py`) reference idempotency handling to avoid re-triggering
   an already-completed or in-flight action, implying a fingerprint/hash-key
   dedup scheme plus some cooldown window logic (not fully read this pass —
   flagged for deeper follow-up).
   `[MY SUGGESTED ANALOGUE - unverified]`: resembles idempotency keys in
   payment/API systems (e.g. Stripe's `Idempotency-Key` header), or
   at-least-once message queue consumers deduplicating via a message ID.

10. **DAG scheduling with write-scope conflict avoidance and human gates.**
    `harness/lib/architecture_guard.py` reads a `write_scope` field per
    task-graph node (`_write_scope()`); `activation_proof.py` tracks
    `contracted_actions`/`unscoped_write_count`/`human_approval_pending` as
    telemetry fields, implying the scheduler avoids concurrent writes to the
    same declared scope and can pause a node for human approval.
    `[MY SUGGESTED ANALOGUE - unverified]`: resembles a build system's
    output-path conflict detection (e.g. Bazel's exclusive output
    ownership) combined with a CI "manual approval" gate step, or optimistic
    concurrency control keyed on declared write-sets (as in some
    transactional schedulers).

11. **Evidence-first research pipeline with anti-fabrication invariants and
    structured verdicts.** The AutoSci-facing capability capsules (e.g.
    `cap.research-external-claim-verification.yaml`) hard-code invariants
    such as "verdicts are restricted to supported / partially_supported /
    not_supported / inconclusive" and "an outcome without collected results
    maps to inconclusive, never to supported," with every evidence artifact
    schema-typed (`research_claims.v1`, `claim_verdict.v1`, etc.) and gated
    by a dedicated evaluator script per schema.
    `[MY SUGGESTED ANALOGUE - unverified]`: resembles closed-world,
    typed-verdict fact-verification pipelines in NLP research (e.g. FEVER-
    style claim verification with SUPPORTS/REFUTES/NOT ENOUGH INFO labels),
    or software test frameworks that default to "inconclusive"/"skip" rather
    than a false pass when evidence is missing.

12. **"Activation proof" testing with negative controls.**
    `harness/lib/activation_proof.py` and `capability_activation_proof.py`
    generate a JSON proof artifact with a `broker_coverage` section (7
    required subfields: `total_actions`, `contracted_actions`,
    `coverage_pct`, `unscoped_write_count`, `policy_denied_count`,
    `lease_denied_count`, `human_approval_pending`) derived from an
    append-only `events.jsonl` ledger, explicitly disclaiming "access to
    private model reasoning" (`capability_effects.py` docstring) — i.e. it
    proves a capability was *actually exercised and observably had effect*,
    not merely declared/available, and appears designed to also validate
    that a control case (capability absent/denied) is correctly rejected.
    `[MY SUGGESTED ANALOGUE - unverified]`: resembles mutation testing or
    "canary"/negative-control assertions in experiment design (a treatment
    is only credited if the corresponding negative control fails as
    expected), or feature-flag "exposure logging" used to prove a feature
    was actually served, not just deployed.

---

## Numbered SoTA Research Questions

1. Which published agent frameworks compile natural-language intent into a
   validated, typed intermediate representation (schema-checked) before any
   execution planning, as opposed to an LLM planner/ReAct loop that plans and
   acts interleaved? Is there a name for this design pattern in the agents
   literature?
2. Is there published academic or industry work on "effect-declaring"
   capability manifests for LLM/agent tools (declared read/write/execute/
   network/cost fields, pre/postconditions, invariants) — analogous to
   capability-based security or effect systems, but targeted at LLM tool use?
3. What is the closest published or industry prior art to a "frozen,
   hash-verified execution contract" gating an agent framework's transition
   from planning to execution (i.e., an immutable plan hash checked before
   dispatch)?
4. Do any competing agent frameworks (AutoGPT, LangGraph, CrewAI, MetaGPT,
   OpenHands, AutoGen) implement a logical-operator/physical-operator
   indirection layer with capability-graded routing and automatic failover
   between backends, and how is it typically described in their docs?
5. Is filesystem-based (file-drop / spool-directory) IPC a documented,
   named pattern in any published multi-agent or multi-process AI
   orchestration system, and if so what are its known tradeoffs versus
   RPC/message-queue based dispatch?
6. What is the current state of the art for automated claim extraction and
   verification from scientific literature (e.g., FEVER, SciFact, and
   successors), and what benchmarks/datasets are considered standard for
   evaluating an LLM-based claim-verification pipeline in 2025-2026?
7. Are there published benchmarks or frameworks specifically for evaluating
   "automated scientist" pipelines end-to-end (idea generation -> experiment
   -> paper -> review), beyond Sakana AI's "The AI Scientist"? What has been
   published critiquing or replicating that work since 2024?
8. How does AutoSci (the specific project referenced by this repo, apparently
   a skills-based CLI research assistant with slash-commands like
   `/discover`, `/ideate`, `/exp-run`, `/paper-compile`) compare in
   architecture and capability to other named "AI Scientist"-style systems
   (Sakana's AI Scientist, ResearchAgent, agent-laboratory, Coscientist)?
   Is AutoSci a published/documented open-source project, and what is its
   actual feature set per its own documentation?
9. What is the current SoTA and standard benchmark suite for terminal/CLI
   coding agents (SWE-bench Verified, SWE-bench Pro, Terminal-Bench 2.0) as
   of the repo's stated "Nov 2025" reference point, and do the specific
   scores cited in this repo's internal doc (Claude Opus 4.5 + Live-SWE-agent
   79.2%, Gemini 3 Pro 77.4%) match publicly reported leaderboard results?
10. Is "Harbor" (harbor-framework/harbor, cited as the official harness for
    Terminal-Bench 2.0) an independently verifiable, actively maintained
    open-source project, and what other benchmark suites does it support
    besides Terminal-Bench 2.0?
11. What published work exists on "activation proof" or "exposure proof"
    style verification that a software capability was not just present but
    actually invoked and had an observable effect, especially in the context
    of LLM tool-use auditing?
12. Do any published agent-security frameworks require a scoped, time-limited
    "lease" or capability token per dispatched sub-task/worker, analogous to
    cloud IAM temporary credentials, and is this a recognized pattern in
    agent-sandboxing literature (e.g. OpenHands', Devin's, or e2b/Daytona/
    Modal/runloop sandbox designs)?
13. What is the state of the art in 2025-2026 for persistent, cross-session
    agent memory architectures (episodic/semantic/procedural taxonomy), and
    how does that taxonomy compare to what this repo's internal doc claims
    (three-layer memory + "ontology" snapshot + reflection loop)? Is this
    taxonomy drawn from a specific published memory-architecture paper?
14. Are DAG-based task schedulers with declared "write-scope" conflict
    avoidance a recognized pattern in either classical build systems (Bazel,
    Buck) or in any published multi-agent orchestration framework, and how
    do they typically handle write-write conflicts between concurrent
    agents/tasks?
15. What is the current competitive and technical positioning of Claude Code,
    Cursor, Devin, Windsurf, GitHub Copilot, Aider, and Cline as of
    2026 — specifically on autonomy, persistent memory, and multi-agent
    orchestration — independent of this repo's self-scored comparison table?
16. Is there a recognized SoTA framework or benchmark for measuring
    "integration completeness" or "capability fusion" of an agent platform's
    plugin ecosystem (as opposed to task-completion accuracy), comparable to
    this repo's `capability_fusion_benchmark.py` approach?
17. What published or well-known frameworks explicitly separate
    "LLM-generated semantic content" from "deterministic structural
    validation" as two distinct pipeline stages, and is there a common name
    for this design pattern (e.g. "guardrails," "structured output
    validation," "constitutional AI")?
18. Does BPMN, Temporal, Airflow, Dagster, or Prefect (durable workflow
    engines) offer a documented analogue to this repo's "frozen execution
    contract" and "human approval gate" pattern for AI agent orchestration,
    and are any of them actually used underneath comparable agent
    frameworks?
19. What independent, third-party evaluations (if any) exist of Sakana AI's
    "The AI Scientist" and its successors, and what are the documented
    failure modes (e.g., overclaiming, review gaming) that a claim-
    verification-focused system like this repo's AutoSci-parity pipeline
    would need to guard against?
20. Are "logical operator" / "physical operator" as terms of art used in any
    published agent-orchestration or database-inspired agent-routing
    literature, or is this closer to a database query-optimizer borrowing
    that this repo has made on its own?
21. What is the current SoTA for automated experiment design and execution
    by LLM agents (e.g. for ML research), and what benchmarks (if any) test
    end-to-end idea-to-experiment-to-verified-result pipelines specifically
    (as opposed to single-step code generation)?
22. How mature/adopted is the Harbor + Terminal-Bench 2.0 ecosystem as of
    2026, and are there competing terminal-agent benchmarks that have gained
    more traction (e.g., from OpenAI, Anthropic, or academic labs)?
23. Is there a recognized taxonomy in the agent-security literature for
    "trust classes" of capabilities (as this repo's capsules imply via
    `guard.*` vs `cap.*` vs `resource.*` capsule kinds), comparable to
    trust-level models in OS security or zero-trust architecture?
24. What is the state of the art for filesystem-scoped or file-based
    multi-agent task dispatch in production systems (as opposed to
    message-broker-based dispatch), and are there known scalability or
    reliability limits documented for that approach?
25. Given this repo's explicit self-report of "not full parity" with AutoSci
    on core research-lifecycle stages (PDF ingestion, end-to-end `/research`
    lifecycle, real experiment execution, PDF compilation), what would a
    rigorous, third-party benchmark protocol look like for comparing two
    "automated research assistant" systems on those specific stages?

---

## Open Questions (for follow-up, not yet resolved in this pass)

- What is AutoSci, concretely and independently of this repo — is it a
  public open-source project with its own repository/docs, and does its own
  documentation support or contradict the 28-skill feature list this repo
  attributes to it? This repo only shows Solar's *inventory of* AutoSci
  (expected at sibling path `../AutoSci`), not AutoSci's own source.
- `docs/SOLAR_EVOLUTION_ANALYSIS.md`, `SOLAR_EVOLUTION_REPORT_V3.md`,
  `SOLAR_TECHNICAL_REPORT_V2.md`, `AI_NATIVE_OS_ARCHITECTURE.md`,
  `DISTRIBUTED_DEPLOYMENT_ANALYSIS.md`, `COMMUNITY_NEURAL_NETWORK_DESIGN.md`,
  and both `docs/insights/*` files were confirmed to exist but not read in
  full this pass — likely contain additional self-claims and possibly more
  external references (especially the memory-mechanisms insight docs).
- Idempotency/dedup/cooldown mechanics were only located by filename grep,
  not read in full — the actual fingerprinting algorithm and cooldown window
  semantics are unverified.
- `harness/tools/platform_workflow_benchmark.py`, `heavy_proof_benchmark.py`,
  `fixed_research_benchmark.py`, `thunderomlx_cache_benchmark_agent.py`, and
  `benchmarks/mlx_quantization_bench.py` were not read — unclear whether any
  reference a published benchmark.
- The `harness/plugins/` directory names (`markitdown`, `mineru`, `owl`,
  `openai-agents-python`, `browser-use`, etc.) strongly suggest wrapped
  integrations of identically-named external open-source projects, but no
  plugin manifest was opened to confirm which are real integrations vs.
  internally-named modules that merely share a common word.
- The Chinese-language `docs/SOLAR_UNIQUENESS_ANALYSIS.md` describes a
  "solar.db," "ontology," "@Evolver," and "14 agents" architecture that does
  not obviously match the TaskGraph/capability-capsule/freeze architecture
  emphasized elsewhere in the repo and in the project context given for this
  task — it's unclear whether this is a legacy/parallel product generation,
  a different subsystem, or aspirational/marketing material never fully
  implemented. Worth clarifying with the repo owner before treating its
  claims as representative of the current system.
