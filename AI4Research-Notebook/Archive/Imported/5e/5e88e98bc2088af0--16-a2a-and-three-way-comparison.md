# 16 — A2A reference, and the MCP / A2A / Capability-Capsule comparison

Written 2026-09-10 by the capability-capsule panel (pts/9).
Companion to `15-mcp-reference.md`. Sources fetched live from
`a2a-protocol.org` on 2026-09-10.

---

## 1. A2A in brief

**Agent2Agent (A2A), version 1.0.0.** Where MCP connects an agent to *tools*,
A2A connects an agent to *other agents*.

Its stated purpose, verbatim:

> *"enable agents to discover each other's capabilities, negotiate interaction
> modalities, manage collaborative tasks, and securely exchange information to
> achieve user goals **without needing access to each other's internal state,
> memory, or tools**."*

That last clause is the whole design. A2A assumes the remote agent is **opaque**
— a peer you delegate to, not a function you call.

### Core objects

| Object | Role |
|---|---|
| **Agent Card** | JSON metadata document: identity, capabilities, skills, endpoint, security schemes. The discovery unit. |
| **Task** | The fundamental unit of work; unique id, defined lifecycle, holds artifacts + message history |
| **Message** | One communication turn, role-tagged (`user` / `agent`) |
| **Part** | Smallest content unit — text, file reference, or structured data |
| **Artifact** | Task *output*, composed of Parts — explicitly distinct from status messages |

The Message/Artifact split is deliberate: **conversation is separated from
deliverable**. Compare with the capsule world's insistence on typed evidence
artifacts rather than chat output — same instinct, arrived at independently.

### Roles
- **A2A Client** — initiates requests on behalf of a user or system
- **A2A Server (Remote Agent)** — exposes A2A-compliant endpoints

### Transport
Three mandated bindings, all projecting one canonical data model:
1. **JSON-RPC 2.0** (synchronous)
2. **gRPC** (performance)
3. **HTTP+REST** (web integration)

Normative source is a Protocol Buffers file, `spec/a2a.proto`:
*"SDKs and any other derived forms MUST be regenerated from the proto rather
than edited manually."* Note the contrast with MCP, whose source of truth is a
**TypeScript** schema. Both picked a machine-checkable IDL; neither picked prose.

### Task lifecycle — A2A is stateful where MCP is not

```
TASK_STATE_SUBMITTED → WORKING → { COMPLETED | FAILED | CANCELED | REJECTED }
                          ↕
              INPUT_REQUIRED / AUTH_REQUIRED   (interrupted states)
```

Multi-turn work groups under a `contextId`; individual units under `taskId`.

**This is the sharpest structural difference from modern MCP.** MCP `2026-07-28`
abolished sessions and made every request self-contained. A2A does the opposite:
a Task is a **long-lived, resumable, explicitly-stateful object** with terminal
states. The reason is the workload — delegating a research job to a peer agent
is not a function call, and may run for minutes or hours.

`INPUT_REQUIRED` and `AUTH_REQUIRED` as *first-class interrupted states* are
worth a slide. Compare MCP's `resultType: "input_required"` and a capsule's
unsatisfied `preconditions` — **all three protocols independently concluded that
"I cannot proceed without more" must be a typed state, not an error.**

### Update delivery
1. **Polling** — `GetTask`
2. **Streaming** — persistent connection; requires `capabilities.streaming: true`;
   `TaskStatusUpdateEvent` / `TaskArtifactUpdateEvent`; events **MUST** be
   delivered in generation order without reordering
3. **Push notifications** — agent POSTs to a client webhook; requires
   `capabilities.pushNotifications: true`; plain HTTP regardless of binding

### Security
TLS mandated for all bindings. Schemes: API key, HTTP auth (Bearer/Basic),
OAuth 2.0 (auth code, client credentials, device code), OpenID Connect, mutual
TLS. Servers **MUST NOT** distinguish missing from forbidden resources — no
information leakage about what exists. Clients **MUST** send an `A2A-Version`
header.

Agents may serve an **extended Agent Card** after authentication, revealing more
capability detail to authorized callers than to anonymous ones. That is a
graduated-disclosure idea with no MCP or capsule equivalent, and it is directly
relevant to a self-extending system that must decide how much of its capability
surface to expose.

---

## 2. The three-layer model — the framing to open with

The three are **not competitors**. They answer different questions, and a
comparison that treats them as alternatives will be dismissed immediately.

```
        ┌──────────────────────────────────────────────┐
  A2A   │  agent  ⇄  agent        (peer delegation)    │  opaque peers
        ├──────────────────────────────────────────────┤
CapCap  │  agent  →  its own future capabilities       │  self-extension
        ├──────────────────────────────────────────────┤
  MCP   │  agent  →  tool         (capability access)  │  transparent tools
        └──────────────────────────────────────────────┘
```

- **MCP** — *how do I call a tool?* Downward, to transparent capabilities.
- **A2A** — *how do I delegate to a peer?* Sideways, to opaque agents.
- **Capability Capsule (new direction)** — *how do I acquire a capability I do
  not yet have, verify it, and install it into myself?* **Inward and forward.**

The third axis is genuinely unoccupied by the other two protocols. Neither MCP
nor A2A says anything about **where a capability comes from**, how it is
**admitted**, or what must be **true of it before it is trusted**. MCP assumes
tools exist; A2A assumes peers exist. That is the gap the new capsule direction
claims, and it is a defensible claim.

⚠ **But see `17-…` §2** — the gap is *unoccupied by these protocols*, not
unoccupied by the field. Several research systems are already there.

---

## 3. Feature-by-feature comparison

| Dimension | MCP (2026-07-28) | A2A (1.0.0) | Capability Capsule (proposed) |
|---|---|---|---|
| **Relationship** | agent → tool | agent ⇄ agent | agent → its own capabilities |
| **Counterparty** | transparent (schema known) | **opaque** (internals hidden by design) | self / self-authored |
| **Discovery unit** | `server/discover`, tool list | **Agent Card** | capsule registry + `applicability` |
| **State model** | **stateless**; explicit handles | **stateful Tasks**, resumable, terminal states | declarative contract per invocation |
| **Wire format** | JSON-RPC 2.0 | JSON-RPC 2.0 / gRPC / REST | *(none — not a wire protocol)* |
| **Source of truth** | TypeScript schema | Protobuf (`a2a.proto`) | JSON Schema (`capability-capsule.v1.draft.json`) |
| **Effects declared?** | ❌ no | ❌ no | ✅ read/write/execute/network/cost/risk — **but see note below on Cordis/dsh** |
| **Pre/postconditions?** | ❌ no | ❌ no | ✅ + invariants |
| **Admission control** | host consent (out of protocol) | auth + Agent Card | ✅ **fail-closed gate, 5 reasons** |
| **Composition** | ❌ none in core | task delegation chains | ✅ typed + derived specs + proof obligations |
| **Provenance / trust** | annotations "untrusted" | TLS + auth schemes | `provenance`, `trust_class`, registration |
| **"Need more input"** | `resultType:"input_required"` | `TASK_STATE_INPUT_REQUIRED` | unsatisfied `preconditions` |
| **Security spec** | ✅ 10 attack classes, OAuth 2.1 | ✅ TLS, 5 schemes, leakage rules | ❌ **none** |
| **Maturity** | multi-vendor standard, SDKs | v1.0.0 standard, SDKs | internal, `draft`, 80 instances, 0 external users |

### Three convergences worth a slide

All three arrived independently at the same three conclusions:

1. **"I need more input" is a typed state**, not an error
   (MCP `input_required` · A2A `INPUT_REQUIRED` · capsule `preconditions`).
2. **Deliverables are separated from conversation**
   (A2A Artifacts vs Messages · capsule typed evidence artifacts · MCP Resources
   vs tool text).
3. **Self-description is not trusted.** MCP: annotations and `clientInfo` are
   untrusted and **SHOULD NOT** drive security decisions. A2A: extended cards
   only after auth; no leakage of what exists. Capsules: registration, not the
   manifest's own claim, is the trust decision.

### The divergence that defines the capsule pitch

MCP states plainly that it **cannot enforce security at the protocol level** and
delegates to the host. A2A secures the *channel* and the *identity*, but says
nothing about what the remote agent will do. **Neither models effects.**

So the honest one-line positioning:

> **MCP standardizes access. A2A standardizes delegation. Capability capsules
> attempt to standardize *admission* — what must be true about a capability
> before the system is allowed to acquire and run it.**

⚠ **Do not claim capsules are "more secure" than either.** They have no threat
model and no security specification, while both MCP and A2A do. The claim is
that they secure a **different thing**: not the channel, not the identity, but
the *semantics and blast radius* of what runs.

---

## 4. RESOLVED — the DeepSeek harness is a real system, now cloned

An earlier version of this note treated "the DeepSeek harness" as ambiguous,
because in the AI4Research checkout DeepSeek appears only as a model provider
(3 physical operators). **That reading was wrong.**

`dsh` — **DeepSeek Harness** — is DeepSeek AI's open-source *agent harness*,
cloned 2026-09-10 to `/home/muk/work/deepseek-harness` from
`github.com/deepseek-ai/deepseek-harness`. A separate panel has inspected it;
their notes are in `notes/deepseek-harness/`. **Read those before designing any
integration** — do not re-derive.

Key facts from that panel [verified by them]: MIT licence, `0.1.5-rc.2`,
**16,511 commits in ~3 months**, **268 workspace packages**, ~858k TS lines,
built on **Cordis** (arXiv 2608.25512), organizing claim *"everything is a
plugin"* — including the agent loop. Explicit developer preview:
*"THERE WILL BE COMPATIBILITY-BREAKING CHANGES."*

### The integration surface is the "capability seam"

dsh's central abstraction, and the thing capsules must plug into:

| Role | What it is |
|---|---|
| **Service Definition** | a Cordis `Service` owning its `ctx.<key>` — an abstract class or concrete registry, **never a TS `interface`** |
| **Service Provider** | one or more implementations |
| **Consumer** | packages injecting the service — commonly a model-facing tool |

*"The seam is the complete capability, never one role."* Adding a capability
means designing all three roles. 71 distinct `ctx.*` services exist, including
`ctx.skills`, `ctx.tools`, `ctx.agents`, `ctx.subagents`, `ctx.sandbox`,
`ctx.invariants`, `ctx.approval`, `ctx.authorization`.

### Which corrects §2's three-layer model to four

The dsh panel's framing is better than the one earlier in this note, and this
note defers to it:

- **MCP** — wire protocol for reaching *external* tools
- **A2A** — protocol for agents talking to agents
- **dsh seam** — an *in-process role contract* making capabilities **substitutable**
- **capability capsule** — a *declarative contract* making capabilities **admissible**

> **A capsule is a contract about a capability; a seam is a socket for a
> capability.** A capsule answers *"may I run this, and what will it do to me?"*
> A seam answers *"can I replace this without touching anything else?"*

Complementary, not competing. Evidence the layering is real rather than
rhetorical: **dsh already contains an MCP layer** (`packages/mcp/mcp-client`,
tools only, nothing enabled by default), so it demonstrably sits *above* MCP
and consumes it.

### What this means for the self-extension design

A generated capsule must ultimately become a **seam** to be usable in dsh —
meaning capsule generation has to emit all three roles, not just an
implementation. That is a sharper and more testable target than "build a skill",
and `ctx.invariants` / `ctx.approval` / `ctx.sandbox` are plausible hooks for
the conformance gate in `17-…` §4.3.

⚠ The dsh panel's note 05 §5 is titled *"Caveats before citing dsh anywhere
public."* Read it before the harness appears in any slide.
