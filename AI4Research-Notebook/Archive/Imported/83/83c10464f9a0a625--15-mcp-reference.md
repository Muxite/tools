# 15 — MCP reference, for the capsule comparison

Written 2026-09-10 by the capability-capsule panel (pts/9).
Audience: CS students with prior agentic-AI experience.

> **Provenance.** Every normative statement below was fetched from
> `modelcontextprotocol.io` on 2026-09-10, **not recalled from memory**. This
> matters: the current revision (`2026-07-28`) postdates this model's training
> cutoff, and it changed the single most comparison-relevant part of the
> protocol. Anything you may already "know" about MCP's `initialize` handshake
> describes the **legacy** era.

---

## 0. The headline for your report

**MCP removed its initialization handshake and became a stateless protocol.**

| Era | Revisions | Model |
|---|---|---|
| **Legacy** | `2025-11-25` and earlier | session established by an `initialize` handshake |
| **Modern** | `2026-07-28` and later | **no handshake**; version, identity and capabilities travel as per-request metadata |

Spec, verbatim: *"There is no negotiation handshake. Every request carries its
protocol version, and the server accepts or rejects each request
independently."*

And: *"The Model Context Protocol (MCP) is a **stateless protocol**: all the
information needed to process a request is contained in the request itself. A
server processes each request independently; no state should be inferred from
previous requests, even those on the same connection or stream."*

This is a **convergence** with the capsule design, and it is the most
interesting thing you can say in the comparison. Both systems concluded that
capability metadata belongs *with the request*, declared and re-checked, rather
than in negotiated session state. See §7.

---

## 1. Architecture — the client/server model

Three roles (MCP takes explicit inspiration from the Language Server Protocol):

| Role | Definition |
|---|---|
| **Host** | The LLM application that initiates connections (IDE, chat app, agent runtime) |
| **Client** | A connector *inside* the host — one client per server connection |
| **Server** | A service providing context and capabilities |

The host↔client distinction is the one people get wrong. A host runs **many**
clients, each maintaining a 1:1 connection with one server. The client is a
multiplexing boundary, and it is where security policy lives — the host
mediates, so a server never sees another server's data.

### Feature directions

Capabilities flow **both ways**, which is easy to miss:

**Server → client** (things a server offers):
- **Resources** — context/data for the user or model
- **Prompts** — templated messages and workflows, user-controlled
- **Tools** — functions the model can execute

**Client → server** (things a client offers):
- **Elicitation** — server-initiated requests for more information from the user
- **Sampling** — server asks the *client's* LLM to complete something
- **Roots** — filesystem roots the server may operate within

Sampling is the conceptually strange one: the server can ask the client to run
an LLM call on its behalf. That inverts the usual dependency and is why
`sampling` is a negotiated client capability rather than assumed.

### Extensions (modern era)

Beyond the core protocol, opt-in extensions negotiated via a
`capabilities.extensions` map keyed by prefixed identifiers:

- `io.modelcontextprotocol/tasks` — **Tasks**: async execution of long-running
  operations, with polling, mid-flight input, durable handles
- `io.modelcontextprotocol/ui` — **MCP Apps**: interactive UI (charts, forms)
  rendered inline
- **Skills over MCP** — structured instructions for agent workflows, discovered
  and consumed through MCP

*"If one party supports an extension but the other does not, the supporting
party **MUST** either revert to core protocol behavior or reject the request."*

---

## 2. JSON-RPC 2.0 — and where MCP deviates

*"All messages between MCP clients and servers **MUST** follow the JSON-RPC 2.0
specification."* Three message types:

### Requests
```typescript
{ jsonrpc: "2.0"; id: string | number; method: string; params?: {...} }
```
- **MUST** include a string or integer ID.
- **Unlike base JSON-RPC, the ID MUST NOT be `null`.**
- The ID **MUST NOT** match any other in-flight request from the same sender.

### Result responses
```typescript
{ jsonrpc: "2.0"; id: string|number; result: { resultType: string; ... } }
```
- **MUST** echo the request ID; **MUST** include `result`.
- **MUST** include a **`resultType`** discriminator — this is new and important:
  - `"complete"` — finished, final content
  - `"input_required"` — incomplete, needs more info (an `InputRequiredResult`)
  - Extensions **MAY** add values, but only ones advertised via capabilities.
  - An unrecognized `resultType` **MUST** be treated as invalid.
  - Absent `resultType` **MUST** be read as `"complete"` (backward compat).

`input_required` makes "I need more from you" a **first-class protocol state**
rather than an error or a convention. Compare with a capsule's
`preconditions` — both refuse to let an under-specified call silently proceed.

### Notifications
```typescript
{ jsonrpc: "2.0"; method: string; params?: {...} }
```
- **MUST NOT** include an ID. The receiver **MUST NOT** respond.

### Error-code partitioning (a nice governance detail)

Standard JSON-RPC codes (`-32700`, `-32600`…`-32603`) for protocol failures.
JSON-RPC reserves `-32000`…`-32099` for implementations; **MCP subdivides it**:

| Range | Meaning |
|---|---|
| `-32000`…`-32019` | **legacy** — allocated ad hoc before the policy existed. New codes **MUST NOT** be allocated here; receivers **MUST NOT** assume meaning |
| `-32020`…`-32099` | **reserved for the MCP spec**; implementations **MUST NOT** emit undefined codes from this range |

Defined so far:

| Code | Name |
|---|---|
| `-32020` | `HeaderMismatch` |
| `-32021` | `MissingRequiredClientCapability` |
| `-32022` | `UnsupportedProtocolVersion` |

Retired and **MUST NOT** be emitted: `-32002` (resource not found → now `-32602`),
`-32042` (URL elicitation required, `2025-11-25` only).

### Message patterns
1. **Request/Response**
2. **Multi Round-Trip Requests (MRTR)** — server needs client input (sampling,
   elicitation, roots) to finish
3. **Subscribe and Notify** — `subscriptions/listen`; the response *is* an open
   stream of notifications, scoped to the request, **not** to the connection

### JSON Schema rules
Default dialect **2020-12**; implementations **MUST** support it.
Security-relevant: implementations **MUST NOT** automatically dereference `$ref`
values resolving to network URIs; opt-in fetching **MUST** be off by default.
Composition keywords (`anyOf`/`oneOf`/`allOf`/`$defs`) **SHOULD** be bounded
(depth, subschema count, time budget) to prevent schema-based DoS.

---

## 3. Lifecycle — MODERN (`2026-07-28`)

### There is no initialization

Every request carries, in its `_meta` field:

| `_meta` key | Type | Required | Purpose |
|---|---|---|---|
| `io.modelcontextprotocol/protocolVersion` | string | **Yes** | e.g. `"2026-07-28"` |
| `io.modelcontextprotocol/clientCapabilities` | ClientCapabilities | **Yes** | capabilities relevant to *this* request |
| `io.modelcontextprotocol/clientInfo` | Implementation | No | name + version (SHOULD send) |
| `io.modelcontextprotocol/logLevel` | LoggingLevel | No | min log level for this request |

Servers **SHOULD** return `io.modelcontextprotocol/serverInfo` in every result's `_meta`.

Hard requirements:
- A request missing a required field is malformed → server **MUST** reject with
  `-32602`; on HTTP, **MUST** be `400 Bad Request`.
- A server **MUST NOT** rely on capabilities the client did not declare. If it
  needs one, it **MUST** return `MissingRequiredClientCapabilityError` (`-32021`)
  with `data.requiredCapabilities`.
- ⚠ `clientInfo`/`serverInfo` are **self-reported and unverified**.
  Implementations **SHOULD NOT** change behavior based on them and **SHOULD NOT**
  rely on them for security decisions. *(A capsule-relevant point: identity
  claims in the protocol are decoration, not authentication.)*

### Version negotiation, per request
If the server doesn't implement the requested version it **MUST** return
`UnsupportedProtocolVersionError` (`-32022`) listing `supported`; the client
**SHOULD** pick a mutually supported version and retry.

Servers **MUST** implement `server/discover`; clients **MAY** call it up front
but may equally just fire an RPC and handle the error.

On HTTP the version also travels in the `MCP-Protocol-Version` header.

### Statelessness — the normative core
- Servers **MUST NOT** rely on prior requests over the same connection to
  establish context.
- Servers **SHOULD** handle requests from multiple tasks/threads/conversations.
- Servers **SHOULD NOT** require connection reuse for related operations.
- Clients **SHOULD NOT** treat a task/conversation as the lifetime boundary of
  the stdio process.
- **State spanning requests MUST be referenced by an explicit identifier the
  client passes on each request.**

*"An open connection, such as a STDIO process, is not a conversation or session."*

### Shutdown
No shutdown message exists in either era — it is **transport-level**:
- **stdio**: client closes the input stream → waits → `SIGTERM` → `SIGKILL`.
  Server **MAY** initiate by closing its output stream and exiting.
- **HTTP**: close the connection(s).

---

## 4. Lifecycle — LEGACY (`2025-06-18` … `2025-11-25`)

Worth knowing because nearly all deployed servers still speak it.

```
Client → initialize request     (protocolVersion, capabilities, clientInfo)
Server → initialize response    (protocolVersion, capabilities, serverInfo, instructions?)
Client → notifications/initialized
        ── operation phase ──
        transport-level disconnect
```

- Initialization **MUST** be the first interaction.
- Client **SHOULD NOT** send anything but pings before the `initialize` response.
- Server **SHOULD NOT** send anything but pings and logging before `initialized`.
- If the server doesn't support the requested version it **MUST** answer with one
  it does; if the client doesn't support *that*, it **SHOULD** disconnect.
- Both parties **MUST** respect the negotiated version and **only use
  capabilities that were successfully negotiated**.

Negotiated capabilities: client `roots`, `sampling`, `elicitation`,
`experimental`; server `prompts`, `resources`, `tools`, `logging`,
`completions`, `experimental`. Sub-capabilities: `listChanged`, `subscribe`.

### Dual-era interop
A "dual-era" implementation supports both. The server selects behavior from how
the client opens: modern `_meta` → stateless; `initialize` → legacy session.
Era is a property of the **server**, and clients **SHOULD** cache it for the
server process (stdio) or origin (HTTP). Legacy client + modern server
**fails** — legacy clients have no fall-forward path.

---

## 5. Transports and authorization

- **stdio** — server as child process; auth **SHOULD NOT** use the OAuth spec,
  credentials come from the environment.
- **Streamable HTTP** — the current HTTP transport (HTTP+SSE is deprecated).

Authorization is **OPTIONAL**, HTTP-only, and built on a deliberately narrow
subset of OAuth: **OAuth 2.1** (draft-13), RFC 6750 bearer tokens, RFC 8414 AS
metadata, **RFC 9728 Protected Resource Metadata** (servers **MUST** implement),
**RFC 8707 Resource Indicators** (clients **MUST** implement), RFC 9207 issuer
identification, and Client ID Metadata Documents (Dynamic Client Registration is
now **deprecated**, retained for compat).

Roles: MCP server = OAuth 2.1 **resource server**; MCP client = OAuth 2.1 client.

The three rules that matter most:

> MCP servers **MUST** validate that access tokens were issued specifically for
> them as the intended audience.
>
> MCP clients **MUST NOT** send tokens to the MCP server other than ones issued
> by the MCP server's authorization server.
>
> MCP servers **MUST NOT** accept or transit any other tokens.

`resource` (RFC 8707) **MUST** be sent on both authorization and token requests,
naming the canonical MCP server URI — **regardless of whether the AS supports it**.

Flow: unauthenticated request → `401` + `WWW-Authenticate` with
`resource_metadata` → fetch PRM → discover AS → register → PKCE + `resource` →
token → `Authorization: Bearer` on **every** request. Step-up: `403` +
`insufficient_scope` + `scope="…"`, client re-authorizes with the **union** of
old and newly challenged scopes.

---

## 6. Security — the ten attack classes

The framing statement, which is **the crux of your comparison**:

> *"While MCP itself cannot enforce these security principles at the protocol
> level, implementors **SHOULD**: build robust consent and authorization
> flows…"*

MCP states its own limit plainly: it is a **transport and description**
protocol, and safety is delegated to the host. Its three principles are user
consent and control, data privacy, and tool safety — all enforced by the host,
none by the wire format.

Also note, directly relevant to capsule `provenance`:
> *"descriptions of tool behavior such as annotations should be considered
> untrusted, unless obtained from a trusted server."*

| # | Attack | Mechanism | Key mitigation |
|---|---|---|---|
| 1 | **Confused deputy** | Proxy server with a static third-party client ID + dynamic registration + a consent cookie → attacker registers a client with `redirect_uri: attacker.com`; the AS skips consent because the cookie exists; the code lands at the attacker | Proxy **MUST** implement per-client consent *before* forwarding; exact-match `redirect_uri`; `__Host-` signed cookies; single-use `state` set **only after** consent |
| 2 | **Token passthrough** | Server accepts a token not issued for it, forwards it downstream. Breaks audience isolation, rate limiting, and the audit trail | **MUST NOT** accept any token not explicitly issued for the MCP server |
| 3 | **SSRF** | Malicious server puts internal URLs in `WWW-Authenticate` / PRM / AS metadata → client fetches `169.254.169.254` and leaks cloud credentials | Require HTTPS; block private/loopback/link-local ranges; validate redirect targets; egress proxy; beware DNS-rebinding TOCTOU |
| 4 | **State handle hijacking** | *(Replaces "session hijacking" in the stateless era.)* Server mints a state handle; attacker guesses or steals it and passes it as a tool argument | Servers **MUST** verify all inbound requests and **MUST NOT** treat possession of a handle as authentication; bind handles server-side as `<user_id>:<handle>` from the **verified token** |
| 5 | **Local server compromise** | Malicious startup command in client config; malicious payload in the server binary; DNS rebinding onto a localhost server | Clients with one-click config **MUST** show the exact untruncated command and get explicit approval; sandbox; prefer stdio or authenticated IPC |
| 6 | **OAuth URL injection** | Server returns `javascript:` as the authorization endpoint → XSS; or shell metacharacters → RCE when the client opens the URL via a shell | **MUST** allow only `http(s)`; **MUST** reject `javascript:`/`data:`/`file:`/`vbscript:`; **MUST NOT** use a shell to open URLs |
| 7 | **stdio proxy escalation** | XSS → steal proxy auth token → ask the proxy to spawn an arbitrary "server" command → RCE | Sandbox spawned processes; CSP; restrict/log stdio spawning |
| 8 | **Mix-up attacks** | A malicious AS induces the client to send a code issued by an honest AS to the attacker's token endpoint | RFC 9207 `iss` validation against the recorded issuer. **PKCE alone does not prevent this** — the client sends `code_verifier` to the attacker |
| 9 | **Localhost redirect impersonation** | Attacker uses a legitimate client's CIMD URL as `client_id` and binds any localhost port; the user sees the legitimate client's name | AS-side warnings for localhost-only redirects; display redirect hostname |
| 10 | **Scope inflation** | Server publishes every scope; client requests them all; one stolen token has enormous blast radius | Progressive least-privilege: minimal initial scope, step-up via targeted `WWW-Authenticate` challenges; never `*`/`all`/`full-access` |

Icons get their own hardening rules (HTTPS/`data:` only, no credentials,
magic-byte sniffing, size limits) because SVG can carry executable content.

---

## 7. MCP vs Capability Capsules — the comparison

### They are not competitors. Your own repo proves it.

The shipped capsule schema has **`bindings.mcp_capabilities`**. A capsule
*binds* MCP capabilities; it does not replace them. The repo also ships
`harness/schemas/draft/mcp-capability.v1.draft.json` — "Solar MCP Capability
Registry Entry v1" — requiring `capability`, `provider`, `level`,
`endpoint_type`, and adding `input_schema`, `output_schema`,
`auth_requirements`, `rate_limits`.

And `CAPSULE_ARCHITECTURE.md` §5.1 states the relationship outright: MCP sits at
**P4** in the trust ladder, with the conversion path **"MCP → wrap in
specification → Capsule"**. Capsules are proposed as a **trust tier above**
MCP, not an alternative to it.

**Say this early in the presentation.** A comparison framed as "capsules vs MCP"
is a category error that the supervisor will catch; framed as "capsules are a
governance layer that can wrap MCP", everything else follows.

### The axis that actually distinguishes them

| | MCP | Capability Capsule |
|---|---|---|
| **Layer** | wire protocol (transport + description) | governance/contract layer over a capability |
| **Answers** | *how do I call it?* | *may I call it, and what will it do?* |
| **Declares** | name, input/output JSON Schema, annotations | contract (pre/post/invariants), **effects**, bindings, verification, operator compatibility, provenance |
| **Enforcement** | ⚠ **explicitly none at protocol level** — delegated to the host | admission gate with **five fail-closed reasons** |
| **Trust of self-description** | annotations "should be considered untrusted" | `provenance` + registry admission is the trust decision |
| **Effects/blast radius** | not modeled | `effects` (read/write/execute/network/cost/risk); plan-level `effect_union` |
| **Composition** | none in core protocol | typed composition + derived specs + `proof_obligations` |
| **Selection** | host/model decides from tool descriptions | `applicability` signals + deterministic admission |

**The one-line thesis:** *MCP standardizes how a model reaches a tool; capsules
try to make what the tool will do checkable before it runs.* MCP's own spec
concedes the second problem is out of scope — which is precisely the gap the
capsule design claims.

### Convergences worth naming (these strengthen both)

1. **Both went stateless.** MCP `2026-07-28` moved capability + version metadata
   onto every request. Capsules were always per-invocation declarations. Two
   independent designs reached "re-declare and re-check, don't negotiate once".
2. **Both externalize state as explicit handles.** MCP: *"State that needs to
   span multiple requests MUST be referenced by an explicit identifier."*
   Capsules: typed evidence artifacts passed between nodes.
3. **Both distrust self-description.** MCP: annotations and `clientInfo` are
   untrusted. Capsules: `status`, registration, and admission are the trust
   decision, not the manifest's own claims.
4. **Both make "need more input" a first-class state.** MCP's
   `resultType: "input_required"` ≈ a capsule's unsatisfied `preconditions` and
   the planner's `unsatisfiable_nodes`.

### Divergences to be careful about

- **Maturity is not comparable.** MCP is a public, versioned, multi-vendor
  standard with SDKs, an extension process, and a documented threat model.
  Capsules are one project's internal design, `draft` schema, 80 instances,
  0 external adopters. Comparing them as peers on *adoption* would be
  indefensible; compare them on *what they attempt*.
- **MCP has a real security specification.** 10 documented attack classes with
  normative mitigations, and an OAuth 2.1 profile. The capsule docs have a
  `permissions`/`risks` contract that is **partly unimplemented** (`13-…` §0)
  and no threat model at all. **If the report claims capsules are "safer than
  MCP", it will not survive contact with the supervisor.** The honest claim is
  that they secure *different layers*: MCP secures the channel and the
  authorization; capsules aim to constrain the *semantics* of what runs.
- **MCP explicitly declines to model effects.** Not an oversight — a scope
  decision, since the host owns consent. Capsules take the opposite bet. That is
  a genuine design disagreement and the most interesting slide in the deck.

---

## 8. Still to do

**Google A2A has not been researched by this panel.** Everything above is MCP.
A2A is agent-to-agent (peer delegation, Agent Cards, task lifecycle) and sits at
a *third* layer again — likely closer to the capsule ecosystem doc's federation
design (`12-…` §1.5) than to MCP. Worth a dedicated pass before the three-way
comparison is drafted.
