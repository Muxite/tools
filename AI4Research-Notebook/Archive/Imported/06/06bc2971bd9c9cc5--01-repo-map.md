# 01 — Repo map

Top level of `/home/muk/work/deepseek-harness`:

```
vendor/       Vendored Cordis source (pinned SHAs; manifest in vendor/README.md)
packages/     268 workspaces, @deepseek-ai/dsh-<name>, at packages/<group>/<pkg>/
apps/         cli · web · desktop (Electron) · desktop-host (private)
python/       Python SDK/runtime (only 22 .py files — thin client over the CLI)
native/       @deepseek-ai/node-addon-system (Node native addon source of record)
benchmarks/   performance gates (session-open, conversation-fold, agent-continuation)
.agents/      skills/ (12 repo-owned agent skills) + notes/ (Agent Notes)
docs/         architecture, generated catalogs, subsystems, cookbook, postmortems
scripts/      215 scripts; 55 of them verify-* gates
website/      VitePress projection of selected bilingual docs
snapshots/    recorded-session replay fixtures
```

`CLAUDE.md` at root and at `packages/` are **symlinks to `AGENTS.md`** — edit the
real file. [repo-claim, stated in AGENTS.md]

---

## `vendor/` — the framework, pinned

```
cordis  cosmokit  group  hmr  include  loader  logger-console  schemastery  timer
```

These are pinned source copies of the Cordis ecosystem, rescoped to
`@deepseek-ai/*` and marked `private: true`. Updating them follows a documented
sync procedure with upstream SHAs, then re-applying logged local modifications.
`@deepseek-ai/cordis` is a **peerDependency of every harness package**.

Reading this: DeepSeek did not merely depend on Cordis, they took ownership of
the copy. That's a strong signal the framework is load-bearing and that upstream
drift was considered a real risk.

## `packages/` — the 50 groups

Grouped by capability family. The full authoritative table is
`packages/README.md`; here are the ones that carry the most weight:

**Spine**
- `core/` — `agent`, `agent-loop`, `session`, `system-prompt`, `tools`, `scope`,
  `agent-default-model`, `agent-tool-presentation`. The product API spine.
- `session/` — durable data plane: persistence seam + backends, projection seam,
  log-backed titles, reporting.
- `session-query/` — retrieval: logical corpus, lineage, SQLite full-text search.
- `typert/` — type-graph generator, loader, runtime registry (powers RPC).
- `api/` + `host/` + `client/` — Remote BFF, HTTP route server, browser half.

**Execution capabilities** (each is a seam — see 03)
- `llm/` — `llm` (definition), `llm-deepseek`, `llm-pi-ai`, `llm-retry`,
  `token-meter`, `deepseek-llm-api-extensions`.
- `shell/` · `subprocess/` · `terminal/` (PTY) · `fs/` · `lsp/` · `web/` ·
  `code-runtime/` · `sandbox/` (bwrap / Landlock / Seatbelt / Windows ACL) ·
  `e2b/` (remote-runtime POC).

**Agent-level capabilities**
- `subagent/` — delegation seam + `subagent` / `subagent_fork` tools.
- `workflow/` — workflow seam + worker-thread engine + `workflow` / `ralph` tools.
- `jobs/` — kind-agnostic background jobs (`job_list` / `job_output` / `job_kill`).
- `goal/` — durable same-session objective with phases and a round cap.
- `plan/` — plan mode as logged state.
- `schedule/` — session-local scheduled follow-ups.
- `compaction/` — context compaction seam.
- `skill/` — skill provider registry + filesystem provider + `skill` tool.
- `mcp/` — **one** package, `mcp-client`. Bridges external MCP servers' *tools*
  only; MCP resources and prompts are explicitly **not supported**. Nothing
  ships enabled; opt in per server.
- `extensions/` — the agent inspecting and mounting **its own** Cordis plugins
  (`tool-cordis`, `cordis-host-runner`, `cordis-client-runner`, `ui-cordis`).
  Deliberately **not in any shipped tree** — dynamic package code reaches the
  real runtime.
- `hooks/` — **Claude Code and Codex hook bridges** + shared wire-protocol lib.

**Composition and boundaries**
- `bundle/` — `base`, `web-app`, `headless`, `sdk-app`, `sdk-minimal`, `acp-app`.
- `preset/` — per-session agent composition from preset `cordis.yml`.
- `boot/` — shared profile/application boot glue.
- `sdk/` — JSON-RPC protocol + TypeScript client/server.
- `acp/` — automation-only Agent Client Protocol server.
- `interaction/` — approval/interaction seams, permission preset, commands,
  `ask_user_question`.
- `credentials/` · `settings/` · `identity/` · `storage/` · `workspace/` ·
  `attachment/` · `spill/` (tool-result overflow) · `guard/` (loop hygiene +
  tool timeouts) · `webhook/` (external events → Workspace Sessions).

**Support** (lower compatibility expectations, per `packages/README.md`)
- `test-support/`, `runtime-diagnostics/`, `util/`, `experimental/`, `e2b/`.

## `docs/` — note the generated files

Several docs are **generated and freshness-gated in CI** — do not hand-edit, and
do cite them as ground truth rather than prose:

| File | Generator |
|---|---|
| `docs/tool-catalog.md` | `gen-tool-catalog` — **boots each tool plugin** and reads `ctx.tools.schemas()` |
| `docs/config-catalog.md` | config field extraction |
| `docs/module-graph.md` | `gen-module-graph` |
| `docs/capability-seams.md` | seam graph |
| `docs/event-producer-consumer.md` | event map |
| `docs/persistence-catalog.md`, `docs/graph-atlas.md` | generated |

The tool-catalog generator is worth calling out: it boots plugins on a real
context because a tool schema **is not statically knowable** (runtime-spread
enums, concatenated descriptions, config-driven names, raw-JSON-Schema MCP
tools). A completeness guard globs `packages/*/tool-*` and fails if a package is
missing from the boot manifest — so a new tool cannot be silently undocumented.

## Where to start reading

1. `README.md` → `AGENTS.md` → `docs/architecture.md` (160 lines, dense, worth it)
2. `docs/glossary.md` — one canonical term per concept; the vocabulary is used
   with precision everywhere else
3. `packages/README.md` — the group table
4. `docs/cordis-primer.md` / `docs/cordis-tutorial/` — if Cordis is unfamiliar
5. `.agents/notes/implemented/architecture/` — 309 dated decision records; this
   is where the *why* lives
