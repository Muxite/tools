# Rendered diagrams from the design vault

Everything here is derived output, not source. Edit the Mermaid block in the source page and re-render.

| Folder | Source |
|---|---|
| `capsule/` | Mermaid blocks in jiuwenswarm `docs/architecture/capsule/*.md` |
| `b1-design/` | jiuwenswarm `docs/architecture/b1-design.md` |
| `m1-design/` | jiuwenswarm `docs/architecture/m1-design.md` |
| `big-picture/` | jiuwenswarm `docs/architecture/big-picture.md` |
| `check/` | a rendering pass used to check `b1-design`/`m1-design` diagrams before they were placed in the vault |

**`architecture/`** (`components/`, `design/`, `presentations/`, `schemas/`, `traces/`) is older than the rest and
does not match any current source: it renders `huawei/ai4research-design/`, the standalone Obsidian vault that was
deleted on 2026-09-29 when jiuwenswarm `docs/architecture/` became the one source of truth (see the vault's README,
"Outside this repository"). Kept for now as a historical snapshot; safe to delete once nobody needs it.

Kept out of git on purpose: renders are large and reproducible from source.
