# 00 — Orientation

## The name problem (read this first)

This project goes by several names. They are the same thing:

| Name | Where it's used |
|---|---|
| **AI4Research** | GitHub repo name (`Stellven/AI4Research`), the product/UI-facing name |
| **OpenSolar** | The name used in `CLAUDE.md`, `AGENTS.md`, the installer, and packaging |
| **Solar** | The runtime itself; the CLI is `solar`, runtime state lives in `~/.solar/` |
| `openJiuwen-Solar` | The **main branch name**, not a separate project |

**"jiuwenswarm" is not a thing in this repo.** [verified] The literal string
does not appear in the tree. If someone refers to "jiuwenswarm", they most
likely mean this project (via the `openJiuwen-Solar` branch) or specifically
the `core/hive/` distributed layer. Ask before assuming.

There is also no separate "swarm project" — swarm-like behavior is a built-in
capability of OpenSolar, not an external dependency.

## What it actually is

A **local-first multi-agent execution framework** that compiles natural-language
goals into a governed task graph and runs it across swappable AI / CLI / tool
operators.

It is explicitly **not**:
- a cloud SaaS
- a multi-tenant production control plane
- "just launching several agents in tmux" (though tmux is used for panes)

The core design thesis, stated in the repo's own words [repo-claim]:

> **LLMs interpret semantics; deterministic code validates structure, maintains
> references, freezes contracts, and schedules.**

So: `Intent Compiler`, the default `Requirement Compiler`, and the
`Elastic Planner` are LLM-based. Validation, acceptance, freezing, and
scheduling are deterministic code. Do not blur that boundary — a lot of the
repo's bug history is exactly that boundary being violated.

## Two workloads, one control plane

The same pipeline serves both:

1. **Product Delivery** — software engineering tasks (write code, fix bugs,
   run tests, review).
2. **AutoSci / DeepResearch** — scientific research workflows: literature
   discovery, paper ingestion, method extraction, claim evaluation, report
   planning, report writing.

Research tasks produce **structured evidence artifacts**, not one-shot chat
answers. That's the point of the whole design.

## Maturity — be honest about this

- `VERSION` is `1.0.0-rc.9`. [verified]
- Root `package.json` says `"version": "3.0.0"` — this is **stale and must not
  be read as the release version**. [verified, and the README explicitly warns
  about it]
- Self-described status: Release Candidate. Suitable for local trial,
  architecture research, and controlled team experiments. [repo-claim]
- Not all platform/tool paths have passed acceptance. The repo maintains an
  elaborate taxonomy specifically so that untested things are not marked
  passing — see [03-conventions-and-rules.md](03-conventions-and-rules.md).

## Scale

[verified]
- 5,386 tracked files
- 2.6 GB on disk, of which 2.0 GB is `.git` (53 remote branches of parallel
  agent history)
- Polyglot: Python (harness), TypeScript/Bun (core), Bash (control plane),
  React/Vite (dashboard), Electron (desktop)

## Language

The repo is **bilingual**. `README.md`, `harness/metadata/*`, and the Phase 22
test plans are largely in Chinese; `CLAUDE.md`, `AGENTS.md`, `INSTALL.md`, and
most inline code comments are in English. Some Chinese docs are
encoding-damaged — see [04-gotchas.md](04-gotchas.md).
