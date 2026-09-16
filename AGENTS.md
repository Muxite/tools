# AGENTS.md

How an AI agent (any vendor) uses this repository: as a toolbox through the CLI or the MCP server, with the
skills as instructions, and as a codebase to change and test.

## 1. Orientation

| Path | What it is |
|---|---|
| `MANIFEST.md` | the contract: every command, tool, argument, result and file format. If code and manifest disagree, the manifest wins |
| `tundlekit/` | the package: `registry.py` (tool registry), `cli.py`, `mcp_server.py`, 1 module per tool group |
| `skills/<name>/SKILL.md` | instruction packs (open Agent Skills format) that say when and how to use the tools |
| `examples/` | a deck spec, a diagram spec, a Mermaid flowchart and a chart spec to try the tools on |
| `tests/` | the test suite |

Install once (Python 3.10+), from the repository root:

```
pip install -e .[all]
```

## 2. Using the tools

There are 3 equivalent ways to run a tool. All return the same JSON result.

**CLI** (any agent that can run shell commands):

```
tundlekit tools --json
tundlekit bundle status --json
tundlekit deck lint examples/deck.json --json
tundlekit diagram render examples/diagram.json -o build/diagram.svg --json
```

- `--json` prints only the result JSON on stdout. Exit code 0 = success, 1 = a check found errors or the tool
  failed (`{"error": "..."}` on stdout, `tundlekit: <message>` on stderr), 2 = usage error.
- `tundlekit call <tool> --args '{...}'` runs **any** registered tool by name with a JSON object of arguments
  (or `--args-file args.json`). This is the simplest way to reach arguments that have no CLI flag:

  ```
  tundlekit call deck_lint --args '{"spec_path": "examples/deck.json", "max": "6:00"}'
  tundlekit call papers_peek --args '{"id": "2604.00392", "mode": "abstract", "dir": "papers"}'
  ```

  On PowerShell, put the JSON in a file and use `--args-file` if the quoting gets in the way.
- `tundlekit tools --json` lists every tool with its name, description, JSON Schema and annotations
  (`readOnlyHint`, `destructiveHint`).

**MCP** (agents that speak the Model Context Protocol): run `tundlekit-mcp` as a stdio server. Tools have the same
names and arguments as `tundlekit call` (`bundle_status`, `deck_build`, `diagram_render`, `chart_bar`,
`palette_get`, `text_lint`, `render_office`, `papers_fetch`, `translate_check`, …). Results come back as JSON text
plus `structuredContent`; failures come back with `isError: true` and a message.

**Python**: `import tundlekit.registry as reg; reg.load_all(); reg.call("palette_get", {})`.

Paths in arguments are relative to the working directory of the process (for the MCP server, the directory it was
started in). `bundle_prune` with `yes` rewrites git history and is marked destructive: run the dry run first and
follow the tundle-bundle skill.

## 3. Connecting the MCP server

If `tundlekit-mcp` is not on the agent's PATH (for example inside a virtual environment), use the absolute path
of the executable (`.venv/bin/tundlekit-mcp`, or `.venv\Scripts\tundlekit-mcp.exe` on Windows), or run the
module with that environment's Python: command `python`, args `["-m", "tundlekit.mcp_server"]`.
Add `"--root", "/path/to/tundle"` to the args to fix the default tundle for the bundle tools.

### Claude Code

Project scope: a `.mcp.json` file in the project root.

```json
{
  "mcpServers": {
    "tundlekit": {
      "type": "stdio",
      "command": "tundlekit-mcp",
      "args": []
    }
  }
}
```

The same entry can be added from the terminal with `claude mcp add tundlekit -- tundlekit-mcp`.

### Codex CLI

In `~/.codex/config.toml`:

```toml
[mcp_servers.tundlekit]
command = "tundlekit-mcp"
args = []
```

Or with a specific Python environment:

```toml
[mcp_servers.tundlekit]
command = "python"
args = ["-m", "tundlekit.mcp_server"]
```

### Gemini CLI

In `~/.gemini/settings.json` (user) or `.gemini/settings.json` (project):

```json
{
  "mcpServers": {
    "tundlekit": {
      "command": "tundlekit-mcp",
      "args": []
    }
  }
}
```

### Any other MCP client (generic stdio)

Most clients (Cursor, VS Code, Cline, Continue, Goose, …) accept the same `mcpServers` shape:

```json
{
  "mcpServers": {
    "tundlekit": {
      "command": "python",
      "args": ["-m", "tundlekit.mcp_server", "--root", "."]
    }
  }
}
```

The transport is plain stdio: 1 JSON-RPC 2.0 message per line on stdin and stdout, logs on stderr, and the
server exits when stdin closes. A minimal session:

```text
→ {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "demo", "version": "0"}}}
← {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-06-18", "capabilities": {"tools": {"listChanged": false}}, "serverInfo": {"name": "tundlekit", "version": "..."}, "instructions": "..."}}
→ {"jsonrpc": "2.0", "method": "notifications/initialized"}
→ {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
→ {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "palette_get", "arguments": {}}}
```

A tiny client without an MCP library:

```python
import json
import subprocess

proc = subprocess.Popen(["tundlekit-mcp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
                        encoding="utf-8")


def rpc(msg):
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()
    return json.loads(proc.stdout.readline()) if "id" in msg else None


rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}})
rpc({"jsonrpc": "2.0", "method": "notifications/initialized"})
print(rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
           "params": {"name": "palette_get", "arguments": {}}})["result"]["structuredContent"])
proc.stdin.close()
proc.wait()
```

## 4. Installing the skills

Each skill is a folder `skills/<name>/` holding `SKILL.md` (and sometimes `references/`). Copy or link the whole
folder into the agent's skills directory; the folder name must stay the same as the skill name.

| Agent | Skills directory |
|---|---|
| Claude Code | `~/.claude/skills/` (user) or `.claude/skills/` (project) |
| Codex CLI | `~/.codex/skills/` (user) or `.codex/skills/` (project) |
| Agents that read the shared layout | `.agents/skills/` in the project |
| Anything else | point the agent at `skills/<name>/SKILL.md`, or paste the file into its instructions |

Copy all skills (macOS, Linux, Git Bash):

```
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/
```

Link instead of copying, so updates to this repository show up at once:

```
mkdir -p ~/.codex/skills
for d in skills/*/; do ln -s "$PWD/$d" ~/.codex/skills/"$(basename "$d")"; done
```

Windows PowerShell (a directory junction needs no admin rights):

```
New-Item -ItemType Directory -Force "$HOME\.claude\skills"
Get-ChildItem skills -Directory | ForEach-Object { New-Item -ItemType Junction -Path "$HOME\.claude\skills\$($_.Name)" -Target $_.FullName }
```

The skills name CLI commands (`tundlekit deck build ...`) and the matching MCP tools (`deck_build`), so they work
with either connection. They need `tundlekit` installed where the agent runs.

| Skill | Use it when |
|---|---|
| `tundle-bundle` | keeping, releasing, comparing, copying or pruning a tundle; setup tables and SOURCE.md |
| `deck-builder` | writing, building, timing or fixing a presentation |
| `diagram-maker` | a figure, flowchart or bar chart is needed |
| `report-writing` | writing or checking report prose |
| `deliverable-review` | before a report or deck goes out |
| `paper-reading` | fetching, reading, citing or summarising papers |
| `zh-en-translation` | reading, quoting or translating Chinese ↔ English technical text |
| `held-out-build-gate` | building a capability with independent, held-out tests |

## 5. Working on this repository

- Read `MANIFEST.md` first. Changes to behaviour start as manifest changes.
- `tundlekit/registry.py`, the `MODULES` list in `tundlekit/__init__.py` and `tundlekit/cli_support.py` are given:
  do not change their behaviour.
- The core uses the standard library only. Optional packages (python-pptx, Pillow, pymupdf) are imported inside
  the functions that need them; a missing one raises a `ToolError` naming the package.
- Tools take keyword arguments matching their JSON Schema and return JSON-serialisable dicts; user-facing failures
  raise `ToolError`.
- Skills: `name` equals the folder name, the description says what the skill does and when to use it (≤ 1024
  characters), the body stays under 500 lines, no vendor-specific tool names, and every command or MCP tool it
  names must exist.

Run the tests from the repository root:

```
python -m pytest
python -m pytest -q tests/test_skills_structure.py tests/test_docs_agents_readme.py
```

Tests that need an optional package or an external program (git, LibreOffice, a PDF renderer) skip when it is
missing.
