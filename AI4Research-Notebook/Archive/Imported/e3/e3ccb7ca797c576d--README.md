# huawei/

What each folder is, as of 2026-09-25.

| Folder | What it is | Edit? |
|---|---|---|
| `tundle/` | The transfer bundle: latest decks, schema, notes, papers, the Obsidian vault (`obby/`) and code snapshots (`code/`). Start at `tundle/README.md`; for Capability Capsule, `tundle/obby/HANDOFF.md` | yes, then `tundlekit bundle release` |
| `capsule-openjiuwen/` | Capability Capsule work repository: `kb/` (knowledge base), `merged/` (schema, report and deck builders, layer 2, parts, the frozen presented deck), `verify/` (reviews). Branch `schema-v2.1-overnight`, not pushed, much of it uncommitted | yes |
| `tools/` | **tundlekit**: the CLI, MCP server and skills that build the decks and keep the tundle. Installed editable, so the deck builders import it from here | yes |
| `.heldout/tundlekit/` | tundlekit's held-out tests, kept away from the implementer on purpose | only when adding held-out tests |
| `openjiuwen/` | All `openJiuwen-ai` repositories (agent-core, jiuwenswarm, Symphony inside agent-core, …). M1 builds on agent-core | read only |
| `stellven/` | `AI4Research` and related clones. **Archived** for Capability Capsule: lessons only, never a build target | read only |
| `deepseek/` | `deepseek-ai/deepseek-harness` | read only |
| `Paper2Agent/` | a reference clone | read only |

Refresh the code snapshots in the tundle after changing `capsule-openjiuwen/` or `tools/`:

```
cd tools
tundlekit bundle snapshot . ../tundle/code/tundlekit --write
tundlekit bundle snapshot ../capsule-openjiuwen ../tundle/code/capsule-openjiuwen --exclude "*.pptx" --exclude "*.docx" --exclude "*.png" --exclude papers --write
```
