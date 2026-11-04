# AI4Research notes and CC v2 handoff

Start with [the continuation guide](TRANSFER/CONTINUE.md). It states what works, what remains open, and how to resume on another machine.

## Current task

[CC Protocol v2](<AI4Research-Notebook/Designs/CC and Strata delivery/CC Protocols/README.md>) includes the declaration standard, reference host, MCP projection, native coding-subagent example, scientific examples and preserved v1 history.

The recorded November 4 run passed 21 local tests, real pinned OpenJiuwen MCP calls and replay, native task delegation with actual code edits/tests, MAPIE scientific cases, and native Strata product inspection. Actual container execution was blocked by the source machine's Docker startup failure. Live-model behavior, full deployment and GPU inference remain unqualified.

## Major notes

| Topic | Start here |
|---|---|
| Whole notebook | [Home](AI4Research-Notebook/Home.md), [project overview](<AI4Research-Notebook/Project Overview.md>) and [active stage](<AI4Research-Notebook/Active Stage.md>) |
| Current CC work | [CC v2](<AI4Research-Notebook/Designs/CC and Strata delivery/CC Protocols/README.md>) |
| Factory and Strata delivery | [Workshop/design route](<AI4Research-Notebook/Designs/CC and Strata delivery/Start here.md>) |
| Lab/runtime architecture | [M2a](AI4Research-Notebook/Designs/ai4r_m2a/README.md) and [lab overview](<AI4Research-Notebook/Designs/Labs and Capability Capsules.md>) |
| Research and verification history | [Experiments](<AI4Research-Notebook/Experiments/Experiment Register.md>) and [activities](<AI4Research-Notebook/Activities/Activity Register.md>) |
| Product/design source documents | [Artifact library](<AI4Research-Notebook/Resources/Artifact Library.md>) |
| Presentations | [Deck catalog](<AI4Research-Notebook/Presentation Library/Deck Catalog.md>) and [latest reviewed decks](Presentations/2026-11-03/) |
| RSI reference designs | [RSI design](<Supplementary/RSI Design Docs/DESIGN - RSI M1 v0.2.md>) |
| User intent and provenance | [Prompt register](<AI4Research-Notebook/Sources/Prompt Register.md>) and [transfer inventory](TRANSFER/source-files.json) |

The notebook uses Obsidian wiki links. Open `AI4Research-Notebook` as a vault for that navigation; ordinary Markdown links also work on GitHub. Historical Windows paths and original receipts are evidence of the old machine, not paths to reuse.

## Verify and run

Python 3.12 and Git are recommended. From the repository root:

```text
python TRANSFER/verify_transfer.py
python TRANSFER/bootstrap.py --profile basic --run
```

For the pinned scientific and upstream-integration environment:

```text
python TRANSFER/bootstrap.py --profile integration --run
```

Use `--plan` to inspect setup without changing anything. Dependencies and upstream repositories are fetched into ignored local directories. Supply your own model access and hardware configuration when advancing beyond deterministic demonstrations.

This replaces the repository's active contents at the user's request. The former toolbox remains in Git history at `bfd34b69f1823fece8e95645f7bea3b442f226bd`. [Transfer scope and exclusions](TRANSFER/CONTINUE.md#transfer-scope).
