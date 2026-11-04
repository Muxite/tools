# 01 — Repo Map

Root: `/home/muk/work/AI4Research`

All paths in the repo's own docs are **relative to the repo root**. After
install, `harness/` in the repo corresponds to the approved runtime under
`~/.solar/harness/`. Don't confuse source tree with installed runtime.

## The five areas that matter

Per `CLAUDE.md`, these are the canonical areas:

| Dir | Language | Role |
|---|---|---|
| `harness/` | Python + Bash | The operational control plane. **This is where most real work happens.** |
| `core/` | TypeScript / Bun | Runtime support, daemon, dashboard server, hive |
| `components.d/` | Bash manifests | Defines installable components |
| `kernel/` | Markdown | Source material for the generated Claude Code kernel |
| `scripts/` | Bash / Python / TS | Packaging, privacy, install-matrix, release gates |
| `docs/` | Markdown | Public documentation and release notes |

## `harness/` — the control plane

The biggest and most important tree. [verified]

```
harness/
├── lib/                    # Python modules — the actual pipeline implementation
│   ├── intent_compiler.py          # stage 1
│   ├── intent_gateway.py           # stage 1 entry
│   ├── requirement_compiler/       # stage 2 (semantic.py, evaluator.py)
│   ├── intent_consumer.py          # stage 3 entry
│   ├── elastic_planner.py          # stage 3 — planning + freeze
│   ├── scheduler_input.py          # stage 4 — frozen bundle -> runtime graph
│   ├── graph_scheduler.py          # stage 4 — dependency-driven ticking
│   ├── graph_node_dispatcher.py    # stage 5 — ready node -> operator request
│   ├── operator_runtime.py         # stage 5 — lease / submit / accept / result
│   └── symphony/status-server.py   # GUI/CLI intake HTTP surface
├── tools/                  # CLI-invocable counterparts (operatord.py, adapters)
├── schemas/                # JSON Schemas: compiler/ planning/ evidence/ + others
├── plugins/autosci/        # research operators
├── evaluators/scientific/  # research gates
├── config/                 # capability-capsules.registry.yaml, logical/physical-operators.json
├── metadata/               # stage-by-stage design examples + handoff docs
├── status-server/          # HTTP control plane + React dashboard
├── solar-harness.sh        # main entrypoint: start incarnations, sprints, intent-gateway
├── coordinator.sh / .ts    # coordination loop
└── DISPATCH-PROTOCOL.md    # tmux dispatch bug root-causes and fixes
```

`harness/lib/` and `harness/tools/` have **substantial overlap** — many files
appear in both (e.g. `actor_lease.py`, `capability_registry.py`). Treat `lib/`
as the importable library and `tools/` as the invocable surface, but verify
which one a given path uses before editing; editing the wrong copy is a real
failure mode here.

## `core/` — TypeScript runtime

```
core/
├── daemon/server.ts        # `bun run dev` / `bun run daemon`
├── dashboard/server.ts     # `bun run dashboard`
├── hive/                   # distributed layer (see below)
├── agent/ engine/ executor/ orchestrator/ flow/ scheduler-ish
├── llm/ intent/ memory/ ontology/ persona/
└── ui/ security/ plugin/ mcp/
```

### `core/hive/` — read the warning

HIVE (Heterogeneous Intelligent Virtual Ecosystem) is a **Phase 2-complete
distributed task execution engine**: mDNS discovery (port 9876), P2P transport,
coordinator election, a task-market protocol with bidding.

**It is a decision layer only.** It determines *who* should execute a task; it
has no mechanism to actually run one. Its `onTaskAssigned` callback is
effectively a stub, and there is **no wiring between HIVE and the harness
executor**. [repo-claim, consistent with the tree layout]

Meanwhile `harness/` does remote dispatch independently via SSH/rsync to hosts
listed in `actor-hosts.json` — completely separate from HIVE's P2P network.

So there are **two unrelated distribution architectures** in this repo, and
some test matrices conflate them as one feature. If a task says "make the swarm
work", clarify which one is meant.

## `components.d/` — the install unit

14 components, each just a `component.sh` (plus `hooks.json` for `kernel`):
[verified]

```
autosci  codex-bridge  core-runtime  daemons  harness  kernel  mempalace
skills-browser  skills-calendar  skills-md  skills-obsidian  skills-office
solar-max  status-daemon
```

Default components are `harness,autosci` (which pull in `kernel`). [repo-claim]
Experimental/optional integrations should stay **component-gated and off by
default** unless their manifest says otherwise — this is a `CLAUDE.md` rule.

## `tests/`

```
tests/
├── journeys/phase22/       # ← PRIMARY acceptance evidence (see 03-conventions)
├── platform/phase22/       # atomic_feature_matrix.json — diagnostic layer
├── core/ harness/ integrations/ distribution/ repository/
├── research/ workflow/ skills/ ui/ vertical/ desktop/ foundation/
└── quarantine/             # broken tests parked here rather than mislabeled
```

The `quarantine/` directory is a convention worth respecting: a broken
fixture/runner gets repaired or quarantined, **never** recorded as a product
failure.

## Other roots

- `app/`, `desktop/`, `web/` — Electron desktop app and web surfaces
- `skills/` (40 dirs), `agents/`, `hooks/`, `rules/`, `templates/` — Claude Code
  overlay material
- `codex-bridge/` — async file-based contract protocol for Codex/OpenAI backend
- `outputs/` — 151 MB of run evidence; `outputs/phase22-real-journeys/<run-id>/`
  is the canonical journey evidence location
- `runtime/`, `distribution/`, `deploy/`, `integrations/`, `benchmarks/`
- `mempalace/`, `library/`, `frameworks/`, `demos/`, `lib/`, `tools/`, `bin/`

## Root files you'll actually open

| File | Why |
|---|---|
| `AGENTS.md` | **The detailed maintainer guide.** Highest-value single file. |
| `CLAUDE.md` | Public contributor guide; small, points at AGENTS.md |
| `harness/metadata/NEW-MACHINE-START-HERE.md` | Current pipeline + schema contract table. Second-highest value. |
| `DESIGN.md` | **Mandatory** before touching the React GUI; token front matter is the single source of truth |
| `README.md` | 28 KB, Chinese, partly historical — see gotchas |
| `INSTALL.md` | Install flow, components, flags, layout |
| `VERSION` | `1.0.0-rc.9` — the real version |
