Every way in and out of jiuwenswarm, plus where tools run and who approves them.

## Ways in

| Kind | What | Code |
|---|---|---|
| UIs | Web workbench, TUI (a separate `jiuwenswarm-tui` package), CLI, desktop app (Windows, macOS, HarmonyOS PC) | `jiuwenswarm/channels/`, `packages/jiuwenswarm-tui` |
| IDE and browser | VS Code, JetBrains, a browser extension | `channels/ide`, `channels/browser` |
| IM | Feishu, DingTalk, WeCom, personal WeChat, Xiaoyi · Telegram, Discord, Slack, WhatsApp | `gateway/channel_manager/im_platforms/` |
| **A2A** | a Gateway-side A2A server (`A2AChannel`), plus outbound A2A to external agents | `gateway/channel_manager/protocol/a2a` |
| **ACP** | Agent Client Protocol, e.g. VS Code's ACP client (`jiuwenswarm-acp`) | `gateway/channel_manager/protocol/acp`, `jiuwenswarm/acp/` |
| SSH | a protocol channel | `gateway/channel_manager/protocol/ssh` |
| Process SDKs | thin Python and TypeScript clients. Each call spawns a single `jiuwenswarm-process` and talks over pipes. *"not another Agent engine"* | `sdks/` |
| Scheduled tasks | cron jobs that start agent work | `gateway/cron`, `runtime/cron` |

Every one of these is converted into **E2A** at the Gateway ([[Swarm 01 Processes and Message Flow]]). The E2A adapters also project responses back out to ACP and A2A (`common/e2a/adapters.py`).

## Ways out

- **MCP**: the agent consumes external MCP servers, configured per the MCP Configuration doc and handled in `server/runtime/mcp/`.
- **A2UI**: agents return standard UI messages (forms, confirmations, comparisons) that only the Web channel renders (`server/runtime/a2ui/`).
- **Extensions and plugins**: `jiuwenswarm/extensions/` (hooks, an extension SDK, an AgentOS router) and **harness packages**, which are loaded at runtime. Auto Harness's Expert packages are delivered this way ([[Swarm 03 Skills, Symphony, Self-Evolution]]).

## Sandbox: `jiuwenbox`

A **lightweight Linux sandbox service** shipped in the same repo (`jiuwenbox/`). It is a FastAPI server that runs each sandbox under **`bubblewrap`** with static, policy-based filesystem rules. It handles file transfer, search and command execution. It runs only on Linux. It is auto-started at boot only when `sandbox.startup_mode` is set explicitly in config (`agent_ws_server.py:1559-1582`), and `/sandbox enable` can start it at runtime. On the agent-core side it is one of the `extensions/sys_operation/sandbox` providers ([[Core 05 Session, Context, Memory]]).

## Tool permissions

This uses agent-core's `allow / ask / deny` engine ([[Core 02 DeepAgent Harness]]) with product policy on top:

- ⚠ The README says tools ask for approval by default. **The shipped config disagrees:** `permissions.enabled: false` (`resources/config.yaml:1130`, and both distributed templates), which makes every call `allow`. Approval only happens once a user enables it.
- Tiered policy maps a call's severity to an action. In **normal** mode: LOW and MEDIUM → allow, HIGH and CRITICAL → ask. In **strict** mode: MEDIUM → ask, CRITICAL → deny. Explicit rules override this.
- There is a workspace whitelist for file access (`/add-dir`), built-in rules for sensitive operations, and persisted approvals.
- ⚠ *"Only when `channel_id` belongs to the engine's set (`web` / `acp` / `cli`, etc.) are tool permission checks performed; others may skip."* — `docs/en/ToolPermissionsSecurity.md` §1. The docs don't name the rest of the set, and I didn't trace it in the code. Which channels actually skip the check is **unverified**. Check before assuming that IM channels are gated. With the shipped default (permissions disabled), no channel asks.

## Multi-instance

Several isolated instances, each with its own workspace, config and ports, can run on one machine, for example dev and prod, or one per user. `JIUWENSWARM_CONFIG_DIR` relocates the config.

Sources: README.md, pyproject.toml [project.scripts], docs/en/{Channels,A2A,A2UI,ACP_Client_Config,MCPConfiguration,ToolPermissionsSecurity,MultiInstance,E2A-protocol}.md, sdks/README.md, jiuwenbox/README.md, jiuwenswarm/{channels,gateway/channel_manager,server/runtime,extensions}/
