# 00 — Orientation: what DeepSeek Harness is

> Scope: `/home/muk/work/deepseek-harness`, cloned 2026-09-10 from
> `https://github.com/deepseek-ai/deepseek-harness.git`.
> Notes written by the deepseek-harness panel. **Read-only inspection** — nothing
> in the checkout was edited.

Provenance marks used throughout these notes:
- **[verified]** — confirmed by running a command against the checkout.
- **[repo-claim]** — the repo's own docs assert it; not independently tested.

---

## One-paragraph identity

**DeepSeek Harness (`dsh`)** is DeepSeek AI's open-source **agent harness** — the
runtime that sits between a model and the world: session log, system-prompt
assembly, tool registry, tool execution pipeline, agent loop, sandboxing,
persistence, and the UIs (Web, CLI, Electron desktop, SDK, ACP). It is *not* a
model and *not* an agent framework in the LangChain sense. It is the
Claude-Code / Codex-CLI category of product, released as an extensible platform.

Its single organizing claim is **"everything is a plugin"** — including the agent
loop itself. [repo-claim, structurally corroborated]

## Hard facts [verified]

| Fact | Value |
|---|---|
| License | MIT |
| Version at HEAD | `0.1.5-rc.2` (root `package.json`) |
| HEAD commit | `c291e7961a` — 2026-09-10 22:17 +0800 (same day as clone) |
| First commit | 2026-06-10 22:58 +0800 |
| Commits | **16,511** in ~3 months |
| Workspace packages | **268** under `packages/*/*/` |
| Package groups | 50 |
| TypeScript/TSX lines | ~858,000 |
| File counts | 3,352 `.ts` · 3,168 `.md` · 1,439 `.yaml` · 365 `.tsx` · 22 `.py` |
| Node engines | `^22.19 \|\| >=24`, pnpm workspaces, ESM everywhere |
| Agent Notes | 309 implemented · 21 proposed · 629 archived |
| `scripts/` gates | 215 scripts, of which **55** are `verify-*` |
| Session format | writer/released version **3**, evidence tag `dsh-v0.1.5-alpha.1` |

**Maturity: explicit developer preview.** The README states in bold:
*"THERE WILL BE COMPATIBILITY-BREAKING CHANGES."* `AGENTS.md` says public APIs
are pre-stable and every consumer must be updated in the same change. Treat any
API surface here as unstable — but note that *persisted session data* is
deliberately **not** treated as disposable (see 02, "Session log").

## Why it's interesting

1. **A named framework underneath.** It runs on [Cordis](https://github.com/cordiverse/cordis),
   vendored into `vendor/`, with an actual paper behind it —
   *A Programming Paradigm for Spatiotemporal Composability* (arXiv 2608.25512). [repo-claim]
2. **A formalized extension model.** The "capability seam" (Service Definition /
   Service Provider / Consumer) is defined in the glossary, enforced in review
   rules, and generated into `docs/capability-seams.md`. See 03.
3. **Agent-governance-as-code.** 150-line `AGENTS.md` + 55 machine gates + a
   mandatory, path-classified, frozen-archive Agent Note system. See 04.
4. **Bilingual by construction.** Nearly every doc exists as `X.md`, `X.zh.md`,
   and an `X.i18n.yaml` sidecar, gated by `pnpm run doc-sync`. That's ~3,168
   markdown files, most of them translation triplets.

## Relevance to the AI4Research / capability-capsule work

dsh's **capability seam** is a shipped, 268-package answer to a problem adjacent
to the one AI4Research's **capability capsule** addresses: how a research/agent
platform makes capabilities swappable, discoverable, and composable. The two
differ sharply in what they formalize (contracts + evidence gates vs. runtime
service roles + reversible effects). Cross-panel comparison is in
[05-comparison-and-takeaways.md](05-comparison-and-takeaways.md) — kept separate
so the AI4Research panels can take it or leave it.
