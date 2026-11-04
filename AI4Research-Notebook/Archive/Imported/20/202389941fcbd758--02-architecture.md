# 02 — Architecture: Cordis, profiles, the loop, the log

Primary source: `docs/architecture.md` (160 lines). Everything below is
**[repo-claim]** unless marked otherwise; the claims are internally consistent
and corroborated by the package layout.

---

## 1. Cordis: the substrate

Cordis is a plugin framework built on a shared **context** (`ctx`). Plugins
contribute three things to it:

- **services** — mounted at a `ctx.<key>` (e.g. `ctx.tools`, `ctx.llm`, `ctx.fs`)
- **typed events** — via declaration merging into extensible maps
- **reversible effects** — `ctx.effect()` / `ctx.on()`

The load-bearing rule: **registrations are effects**. Every contribution goes
through `ctx.effect()` or `ctx.on()`, and a registry's `register()` returns its
disposer. Unloading a plugin unwinds everything it contributed. This is what
makes "replaceable from configuration" real rather than decorative — you can
swap a running component without leaving residue.

> "There is no privileged core to patch: you extend dsh by mounting a plugin
> beside the others."

The model adapter, tool registry, session log, and **the agent loop itself** are
all plugins.

## 2. Profiles and bundles: how a running dsh is composed

A running `dsh` is a plugin tree composed at boot from **ordered layers**.

- A **bundle** is a distribution format for Cordis config rows plus the code they
  mount. It declares itself in its own `package.json` under `dsh.bundle`.
- A **profile** is a named composition stored in the Harness home (`$DSH_HOME`).
  It lists the bundles it stacks, holds out-of-tree plugins, and keeps the user's
  `cordis.patch.yml`. Declared under `dsh.profile`.

**Shipped profiles:** `web`, `headless`, `sdk`, `sdk-minimal`, `acp`.

**Layer order**, applied to an empty entry list:

```
1. each bundle in the profile's listed order   (dsh-base first for web/headless/sdk/acp)
2. the profile's cordis.patch.yml
3. the home-level cordis.patch.yml
4. any --patch overlay
```

A patch targets a row **by id** and either replaces its whole config or inserts
new rows.

`dsh-base` is the shared first layer: model adapters, tools, persistence, sandbox
and approval policy, settings, credentials, telemetry. Then `dsh-web-app`,
`dsh-headless`, `dsh-sdk-app`, `dsh-acp-app` add their application. `dsh-sdk-minimal`
is the deliberate exception — one bundle owns its complete explicit tree and does
**not** apply `dsh-base`.

**Reload policy differs by profile, for a stated reason:** custom profiles default
to live patch reload, and the `web` profile is live; `headless`, `sdk`,
`sdk-minimal`, and `acp` apply all layers **once at startup**, because replacing a
one-shot or stdio application's dependencies after it owns work would invalidate
that lifecycle.

**The introspection command that makes this concrete:**

```sh
dsh --profile web --dump-config
```

Any row it prints can be replaced by a patch of your own. *(Not executed — the
checkout was not built. [repo-claim])*

### Application launch is a hard rule

Every supported Node application starts at the `dsh` CLI with a **named profile**.
Package bins, demos, and public-SDK argv escapes are **forbidden**, and
`scripts/verify-application-entrypoints.ts` classifies every package bin,
executable source, and root demo and rejects any Node application path that
bypasses `dsh`.

Even the **Python SDK** obeys this: its runtime wheel packages the normal `dsh`
CLI as `deepseek-harness-sdk-runtime-<platform>-<arch>` and launches
`dsh --profile sdk`. Python exposes profile selection + ordered patch files, not
a Cordis tree. That's why `python/` is only ~22 files — it is a thin client, not
a reimplementation.

Even the **Electron desktop app** obeys it: Electron starts a private Desktop Host
package under its bundled Node, which loads the bundled dsh backend. Unary RPC,
Remote streams, and version-matched client assets cross **versioned framed byte
pipes**, Node IPC is reserved for lifecycle control, and the renderer is reached
through a secure `dsh-app://` protocol — **no Web server and no loopback port**.

## 3. The three event domains

Picking the right domain is described as "the first decision in most changes":

| Domain | Nature | Use when |
|---|---|---|
| **Session events** | durable facts appended to the log, broadcast on `session/event` | the fact must survive a reload |
| **Agent events** (`agent/*`) | live, carry an `Agent` handle | observe or intercept work in flight |
| **Capability events** (`fs/*`, `tools/*`, `telemetry/*`) | attach policy/adapters to a seam | extend without importing the loop |

Some events are **waterfalls** — `agent/pre-step`, `agent/request`, `llm/stream`,
and the three `tools/*` events. **Waterfall listeners MUST call `next()`** to
delegate; returning without it short-circuits the chain. `agent/turn-stopping` is
serial and has no `next()`. Closed unions end in `assertNever`; merge-extensible
unions fall through a documented default.

## 4. Turn / step / round

From `docs/glossary.md` — the vocabulary is used strictly:

- **turn** — one drain of admitted input in a session; ends after the model and
  its tools stop, or a terminal policy intervenes.
- **step** — one model request **plus the tool executions caused by its response**.
  A turn contains zero or more steps.
- **round** — an *outer policy* iteration containing a turn (a goal round, or one
  fresh-agent Ralph attempt). Round counters belong to that policy and do **not**
  count every turn.

### The loop, verbatim structure

```text
turn/start
  claim next-step input plus one queued message
  assemble prompt sections + tool schemas; project runtime context
  -> agent/pre-step                   reject | enter(messages, startsRequestSeries?)
     reject, or a first enter rewritten empty -> close the turn with no step
     step/start
     agent/request -> prepareCall (cancellation commits neither system nor users)
     reconcile system/message using the prepared call capability
     append entered messages as user/message; log request/header and request/context
     derive and freeze model history from the log
     stream the bound prepared call -> llm/stream -> agent/assistant-stream start
       agent/assistant-stream chunk*
       assistant/message | assistant/attempt -> agent/assistant-stream end
     tool/call* -> tools/pre-execute -> tools/execute -> tools/post-execute -> tool/result*
     step/end
     tools owe another request, or next-step input arrived -> claim -> next step
  -> agent/turn-stopping
turn/end
```

Details worth carrying:

- **One inbox.** All input reaches the driver through a single inbox. Some
  messages wake it immediately; **injected context waits in the inbox until
  another message does**. (`agent.inject()` is how you add model-facing context.)
- **`agent/pre-step` decides accepted input.** Listeners may rewrite or reject
  claimed messages. A rejected or empty first claim closes a **durable turn with
  no step** — i.e. an empty turn is still a logged fact.
- **Two-phase commit around routing.** `agent/request` + `prepareCall()` resolve
  the actual route *before* the system prompt and accepted user messages are
  committed. Cancellation during either async phase commits **neither**.
- **Retries do not repeat assembly or `agent/pre-step`.** Every attempt
  reconciles the same rendered assembly; users are appended only on the first.
- **The system prompt travels only as `system/message` history.** An empty
  rendering *clears* all active system nodes, so no stale prompt stays
  model-visible. Prompt-cache-capable routes append non-empty updates after the
  cached prefix; incapable routes consolidate at the first system node.
- **The loop sends immutable requests while keeping cancellation live**, and
  reuses message-freeze provenance only for identities it has fully frozen.

## 5. The session log — the most opinionated part

> **"Model-visible ⟺ logged."** Anything that reaches a model request must be
> reconstructable from the session log, **and a runtime invariant asserts it**.
> A new model-visible input therefore *requires a new session event*.

That is the single strongest architectural commitment in the repo, and it has
teeth: adding model-visible context means extending `SessionEventMap` and
rendering from the log, not sneaking a string into a prompt builder.

Mechanics:

- `deriveMessages()` projects model history from the log.
- Each `assistant/message` **embeds the exact compact timed stream that produced
  it**. `assistant/attempt` retains settled failed / retried / cancelled /
  stream-error attempts **without adding model history**. Fork, resume,
  transcripts, telemetry, and persistence all derive from these durable
  settlements; live UI incrementality comes from the process-local
  `agent/assistant-stream`.
- **Versioning and immutable generations.** JSONL v0 is `session.jsonl[.zstd]`;
  v1+ are `session.vN.jsonl[.zstd]`. Committed generation paths are **never
  renamed, replaced, or deleted**. A write-open encodes, verifies, and
  exclusively publishes a version-named successor *beside* the unchanged source.
  A read-open uses the in-memory migrated result and publishes nothing.
  Each migration package owns exactly one `vN -> vN+1` step.
- **Forward-compatibility is strict by default.** `SessionEventMap` members are
  required-on-read: a build that does not know an event type **refuses the log**
  unless the event carries `ignorable: true`. Only *structural* format changes
  bump `SESSION_FORMAT_VERSION`.
- **Prereleases count.** An alpha/beta/RC publication establishes released
  session-format obligations; GitHub's prerelease flag "does not make persisted
  user data disposable."
- **Projection seam.** `dsh-session-projection` owns `ctx.sessionProjections`:
  registered units fold committed events incrementally, host consumers read typed
  state via `stateOf()`, carriers batch cropped client views via `snapshot()`. A
  host reader must either require the service at activation or fail explicitly —
  **silently defaulting a missing value is forbidden**.

Reading this: pre-stable *APIs*, but production-grade *data* discipline. The
project is willing to break your code and not willing to break your sessions.

## 6. Agent scope — per-agent worlds

From the glossary; this is the mechanism behind personas and per-agent toolsets.

- A contribution (tool, prompt section, variable, restriction, listener) is either
  **global** or **scoped** to exactly one scope key. **Two levels, flat** —
  scoped registrations do **not** inherit down to subagents.
- Subtree behavior is expressed with **lineage data** (`parentSession`, durable
  `delegationDepth`, runtime `subagentDepth`), **never** with scope structure.
  Lineage never affects visibility.
- **Shadowing** is most-specific-wins: a scoped tool/section/variable replaces its
  same-named global twin for that scope alone.
- A **restriction** (`tools.restrict`) filters the *global* tool set for one scope
  and composes by intersection; scope-local registrations merge after the filter.
  A filtered-away tool is **absent from the prompt AND refuses execution,
  indistinguishably from a nonexistent one** — no information leak about what
  exists.
- The **setup window** (`CreateAgentOptions.setup`) is the creation slot where a
  creator composes an agent's scoped world: after the scope and agent object
  exist, but before publication, `agent/session-start`, or first prompt assembly.
  **Setup registers; it never drives the agent.**

## 7. Where new behavior goes

`docs/architecture.md` ends with a routing table. Abridged:

| Goal | Mechanism |
|---|---|
| Add a model provider | register its adapter on `ctx.llm` |
| Add a model-facing capability | register on `ctx.tools`; its schema joins prompt assembly |
| Give one session a different capability set | compose an agent preset (service rows need an `isolate` realm) |
| Add shell / persistent terminal execution | register a `ctx.shell` / `ctx.terminals` backend |
| Add a human command | register on `ctx.commands` — dispatches **without a model turn** |
| Add background work | register on `ctx.jobs`; `job_*` tools collect or stop it |
| Confine spawned processes | use a `ctx.sandbox` backend; consumers wrap argv before spawning |
| Intercept a request/tool/turn | its `agent/*` or `tools/*` event |
| Add model-facing context | `agent.inject()` — lands in the next admitted request |
| Add durable session state | extend `SessionEventMap`; render and replay from the log |
| Fork a session at a turn boundary | `ctx.agents.create({ sessionId, seed, meta: {...} })` |
| Store sessions in a new backend | implement `SessionPersistence` over the shared handle scaffolding |
| Scope a registration to one agent | use that agent's `agent.ctx` |

And the governing rule: **"Plugins, not loop changes."** New behavior goes on
documented extension points; changing `agent-loop` requires updating
`docs/architecture.md` in the same change.
