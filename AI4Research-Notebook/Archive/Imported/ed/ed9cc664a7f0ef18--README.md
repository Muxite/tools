# DeepSeek Harness — inspection notes

Notes on **`@deepseek-ai/dsh`**, the DeepSeek AI open-source agent harness.
Written 2026-09-10 from a fresh clone at `/home/muk/work/deepseek-harness`
(HEAD `c291e7961a`, version `0.1.5-rc.2`).

```
/home/muk/work/
├── AI4Research/        ← other panels' subject (not touched here)
├── deepseek-harness/   ← this panel's subject (READ-ONLY, never edited)
└── notes/
    ├── …               ← AI4Research panels' notes
    └── deepseek-harness/  ← you are here
```

**Mode: read-only.** The checkout was inspected but never built, run, or
modified. No file outside this directory was edited.

---

## Read in this order

| # | File | What's in it |
|---|---|---|
| 00 | [00-orientation.md](00-orientation.md) | What dsh is, hard numbers, maturity, why it's interesting |
| 01 | [01-repo-map.md](01-repo-map.md) | Layout, the 50 package groups, which docs are generated |
| 02 | [02-architecture.md](02-architecture.md) | Cordis, profiles/bundles, event domains, the turn loop, the session log, agent scope |
| 03 | [03-capability-seams-and-tools.md](03-capability-seams-and-tools.md) | The seam model, 71 services, the shipped tool surface, PTC mode, sandboxing |
| 04 | [04-conventions-and-governance.md](04-conventions-and-governance.md) | Agent Notes, the 55 gates, code rules, the prose standard, PR process |
| 05 | [05-comparison-and-takeaways.md](05-comparison-and-takeaways.md) | seam vs. capsule vs. MCP vs. A2A; practices worth stealing. **Cross-panel — optional** |

## Provenance marking

- **[verified]** — confirmed by running a command against the checkout.
- **[repo-claim]** — the repo's docs assert it; not independently tested.

Nothing in these notes was executed against a *running* dsh. Behavioral claims
about the loop, profiles, sandboxing, and tool execution are **[repo-claim]** —
read from `docs/`, corroborated by the package layout, but not observed. Counts,
file layout, and git facts are **[verified]**.

## The 60-second version

dsh is an **agent harness** — the runtime between a model and the world — built
on the claim that **everything is a plugin, including the agent loop**. It runs
on [Cordis](https://github.com/cordiverse/cordis) (vendored into `vendor/`), where
plugins contribute services, typed events, and **reversible effects** to a shared
context. A running instance is a plugin tree composed at boot from ordered layers:
bundles → profile patch → home patch → `--patch` overlay, all inspectable with
`dsh --profile web --dump-config`, and every printed row replaceable.

Its two strongest architectural commitments:

1. **The capability seam** — Service Definition / Service Provider / Consumer.
   Because filesystem and subprocess share one execution world, swapping one
   provider pair moves Bash, PTY, and LSP to a remote sandbox with no forks.
2. **Model-visible ⟺ logged** — anything reaching a model request must be
   reconstructable from the append-only session log, asserted by a runtime
   invariant. Adding model-visible context *requires* a new session event.

Around that: 268 packages, 71 `ctx.*` services, 55 CI `verify-*` gates, per-file
100% coverage on package sources, a mandatory dated decision-record system with a
frozen append-only archive, and an enforced prose standard that bans metaphors.

**Pre-stable APIs, production-grade data discipline.** The project will break your
code and refuses to break your sessions.

## Facts a reader will want handy

| | |
|---|---|
| Repo | `github.com/deepseek-ai/deepseek-harness` · MIT |
| Version / HEAD | `0.1.5-rc.2` · `c291e7961a` (2026-09-10) |
| Age / commits | first commit 2026-06-10 · **16,511 commits** |
| Scale | 268 packages · 50 groups · ~858k TS/TSX lines · 71 `ctx.*` services |
| Docs | 3,168 `.md` (mostly en/zh/i18n triplets) · 55 `verify-*` gates |
| Agent Notes | 309 implemented · 21 proposed · 629 archived |
| Session format | version **3**, released as of `dsh-v0.1.5-alpha.1` |
| Runs on | Node `^22.19 \|\| >=24`, pnpm workspaces, ESM only |
| Surfaces | Web UI · CLI · Electron desktop · TS SDK · Python SDK · ACP |
| Profiles | `web` · `headless` · `sdk` · `sdk-minimal` · `acp` |
| Try it | `npx @deepseek-ai/dsh web` → `http://127.0.0.1:3080` |

## Open questions this pass did not answer

1. **Does it build and run?** Nothing was installed or executed. `pnpm install &&
   pnpm run build && pnpm dsh web` would confirm the developer-preview claim and
   let `--dump-config` be captured for real.
2. **What does the DeepSeek LLM adapter actually send?** `docs/deepseek-llm-api-wire-extensions.md`
   and `packages/llm/deepseek-llm-api-extensions/` were not read; the wire-level
   extensions beyond the OpenAI-ish shape are unexamined.
3. **How good is PTC mode in practice?** The mechanism is documented; no
   measurement of its token or reliability effect is published or reproduced.
4. **What's in the 629 archived Agent Notes?** They're frozen and explicitly not
   authority for current behavior, but they are the design history of the whole
   project and were only sampled.
5. **`docs/postmortem/` was not read** — likely the highest-signal-per-page
   directory in the repo for anyone wanting to know where this design broke.
