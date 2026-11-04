---
id: cc-v2-06-distribution-and-interoperability
status: v2-reference-implementation
source: November 4 CC v2 revision
last_reviewed: 2026-11-04
next_action: Qualify selected adapter and consumer evidence policy
---
# Distribution and transport companions

Recipients need immutable contract/material identity and an eligible adapter. Native sealed source bundles are first-class; OCI is one binding choice. Import/mirror bytes without changing identity, then admit under local policy.

| Surface | Responsibility |
|---|---|
| Callable API | Host admission, calls, artifacts and receipts shared with CLI. |
| CLI | Run from a folder, or validate/seal/call for explicit release management; see [README](README.md). |
| MCP | One capability becomes a tool with plain arguments; bridge supplies release/key and canonical receipt. |
| JiuwenSwarm | Host-registered agent; retain native session and permission behavior. |
| A2A | Negotiated delegated-task transport; explicit versioned CC routing required. Generic chat is insufficient. |

Transport does not automatically supply authority or deduplication. Preserve structured receipts and error status; for text-only clients emit the same canonical JSON receipt. Reject conflicting copies. Model interpretation of prose cannot recover authority.

Project finite capabilities into the current generated MCP tool discovery. Served capabilities appear in package/runner discovery and require explicit start authority; a service can itself expose MCP or another native API, but the bridge must support that interface rather than guess methods. Passive materials can be mapped to resources/prompts by a separately supported adapter. Pin bindings through invocation; upgrades cannot silently switch active calls. Tenant/principal comes from trusted host context. Keep artifact identity separate from expiring access URLs and publication authority.

Configure MCP server grants once as session authorization. Each invocation inherits only the selected capability's declared effects. Model arguments do not select grants or verification policy. Normal MCP dispatch runs no semantic checker; a negative optional assessment is data, not a transport failure. Required acceptance policies remain host/caller choices. Execution failures still carry `isError`.

The host `invoke_tool` wrapper rejects a caller-supplied `_cc_key` and injects stable host invocation identity before transport retries. Use this wrapper to retain deduplication across reconnects. A generic raw MCP client without it has no effect-retry guarantee. Generated MCP schemas retain boolean JSON Schema semantics. Gateway cancellation does not prove downstream cessation. [09](09-upstream-coding-integration.md) retains pinned source gaps. Deployed durability/A2A interoperability require their own evidence; local MCP projection is not that evidence.
