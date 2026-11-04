# 05 — Branches & History

[verified 2026-09-10 against commit `b0bf165f9`]

## Remote

Only **one** remote is configured locally:

```
origin  https://github.com/Stellven/AI4Research.git
```

⚠ `AGENTS.md` refers to pushing to **both `origin` and `stellven`** — a
`stellven` remote does **not exist** in this checkout. Either the second remote
needs adding, or that instruction is stale. Confirm with the owner before any
push workflow.

## Current branch

`openJiuwen-Solar` — this is the main branch and, per `AGENTS.md`, the **sole
publishing branch**. `origin/HEAD` points at it.

## Branch landscape

53 remote branches. The naming prefixes tell you the origin of the work:

| Prefix | Count-ish | Meaning |
|---|---|---|
| `codex/*` | ~30 | Work by Codex/OpenAI agents. The dominant category. |
| `task/*` | 4 | Scoped task branches |
| `claude/*` | 1 | Claude-authored branch |
| `docs/`, `ci/`, `fix/`, `pkg/`, `system/`, `security-fix-*` | few | Self-explanatory |
| bare names | `main`, `ai4research-main`, `opensolar-main`, `memrl-clean`, `solar-windows-runtime` | long-lived lines |

**Implication:** this is a repo where many AI agents committed in parallel.
Branch archaeology matters more than usual, and `AGENTS.md`'s hash-ledger
integration gate exists precisely because subject lines are unreliable here.

## Most recently active (by committer date)

```
2026-09-08  origin/openJiuwen-Solar        ← main
2026-09-08  origin/ai4research-main
2026-08-31  origin/system/whole-system-e2e-20260828
2026-08-26  origin/task/elastic-planner-static-boundary-v1
2026-08-26  origin/codex/integrate-requirement-compiler
2026-08-26  origin/revert-47-codex/integrate-requirement-compiler
2026-08-24  origin/task/research-evidence-to-poc-demo-continuation
2026-08-24  origin/opensolar-main
2026-08-20  origin/claude/research-evidence-poc-vqy1cw
2026-08-20  origin/solar-windows-runtime
```

Note the pair `codex/integrate-requirement-compiler` and
`revert-47-codex/integrate-requirement-compiler` on the same day — that
integration was merged and reverted. Relevant context if you touch the
Requirement Compiler.

## The three "main"-ish branches

| Branch | Role |
|---|---|
| `openJiuwen-Solar` | **Current main / sole publishing branch** |
| `ai4research-main` | Actively merged *into* `openJiuwen-Solar` (HEAD is such a merge) |
| `opensolar-main` | The packaging/OpenSolar line; stale since 2026-08-24 |
| `main` | Present but not the working line |

HEAD (`b0bf165f9`) is `merge: ai4research-main into openJiuwen-Solar`, so those
two lines are being reconciled.

## Recent commit themes

```
b0bf165f9  merge: ai4research-main into openJiuwen-Solar
cab32f937  fix(harness): pipeline repairs, reasoning capsules, credential presence
3f534a0a9  fix(harness): persist end-to-end research pipeline repairs
5ade9d9f3  fix(harness): stabilize structured research pipeline
02616a8ed  merge: reconcile structured output contracts with ai4research-main
1ac314bd2  fix(planner,runtime,dashboard): planner runtime, dispatch, evaluation
1689d9379  fix: normalize structured model output contracts
b7d5afd05  docs: publish GitHub migration handoff instructions
cae374a59  docs: hand off final E2E blocker and migration state
f463b861b  fix: freeze requirement admission identities, split repair budgets
```

The pattern is clear: **the active work is stabilizing structured model output
contracts through the research pipeline**, plus a machine migration. Several
commits are `docs:` commits that *record a blocker* rather than fix it — this
repo treats "write down the unattended failure" as a deliverable. Follow that
convention.

## Migration document trail

In `harness/metadata/`, newest last:

```
pre-scheduler-stabilization-log-20260829.md   ← per-issue log: cause, fix, verification
portability-audit-20260830.md
migration-handoff-20260830.md                 ← functions, evidence, original re-test prompts
migration-handoff-20260831.md                 ← last E2E + migration state
structured-output-compatibility-20260831.md   ← current worktree repairs
MIGRATION-CODEX-PROMPT-20260831.md
semantic-retrieval-contract.md                ← design/compat boundary
NEW-MACHINE-START-HERE.md                     ← the index; start here
```

Historical migration product code pinned at
`f463b861bf47bddff46cc2ce3de151dcd8d78992`.

Read the stabilization log's **latest** entries before treating any listed bug
as still open — many are fixed and the log is append-only.
