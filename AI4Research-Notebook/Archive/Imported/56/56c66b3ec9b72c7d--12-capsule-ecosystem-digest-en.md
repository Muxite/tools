# 12 — CAPSULE_ECOSYSTEM_DESIGN.md — full English digest

Source: `docs/CAPSULE_ECOSYSTEM_DESIGN.md`, 1139 lines, Chinese, v1.0 / 2026-02-03.
Digested 2026-09-10 by the capability-capsule panel (pts/9).

> **Section numbers below are the SOURCE's own**, corrected after adversarial
> review found an earlier draft had renumbered them (inventing §1.5–§1.7 and
> §3.1). Cite these; they resolve in the Chinese original.

> **Status warning.** Essentially **none of this is implemented.** No `capsule://`
> resolver, no JSON-RPC endpoint, no federation layer, no trust scoring, no
> governance tiers, no compressed index, no L1/L2/L3 cache exist in
> `harness/lib/`. This document is a design proposal. It is extremely useful as
> the **future-work / roadmap** half of the deliverable, and actively dangerous
> if presented as system behaviour.

The document is organised around three questions it poses to itself:

1. How does the capsule system extend — what are the protocols and standards?
2. How are capsules used and triggered — and how do you minimise token cost?
3. How do capsules compose?

---

# Part 1 — The extension protocol

## 1.1 The five-layer protocol stack

| Layer | Name | Contents |
|---|---|---|
| **5** | **Discovery** | Registry protocol: search / publish / subscribe. `capsule://registry.solar.ai/discover`. **DNS-SD / mDNS for local discovery.** |
| **4** | **Trust** | **Ed25519** signatures (author identity), **SHA-256** hashes (content integrity), **SCARE score** (quality proof) |
| **3** | **Composition** | DAG dependency graph, type-compatibility checking, spec-derivation algorithm |
| **2** | **Execution** | JSON-RPC 2.0 invocation, resource isolation (cgroups/sandbox), live metrics (latency/cost/status) |
| **1** | **Specification** | `capsule/v1` YAML, the six contracts, SemVer semantics |

⚠ This is a **different stack** from the 4-layer one in `CAPSULE_ARCHITECTURE.md`
§3.1 (`Identity / Verification / Execution / Composition`). Trust and Discovery
are new; Identity has been folded into Specification. Neither doc mentions the
other. Pick one for any diagram and say which you used.

Note the Trust layer names concrete primitives — Ed25519 and SHA-256 — which is
unusually specific for an unbuilt design. Of these, **only SHA-256 hashing
actually appears in the shipped code**, in `capsule_composition.py`, used for
reproducibility of composition-search payloads rather than for content trust.

## 1.2.1 The capsule URI standard

```
capsule://<namespace>/<name>@<version>[?<params>]

capsule://solar.core/weather-query@1.0.0
capsule://community.utils/json-parser@2.1.0?locale=zh-CN
capsule://org.acme/internal-tool@latest
```

| Part | Meaning | Example |
|---|---|---|
| `namespace` | organisation / scope | `solar.core`, `community.utils` |
| `name` | capsule name | `weather-query` |
| `version` | SemVer | `1.0.0`, `^1.0`, `latest` |
| `params` | optional | `locale=zh-CN`, `timeout=5000` |

The namespace is what the governance model (§1.4) keys off — the tier you are
in is encoded in your name.

## 1.2.2 Invocation: JSON-RPC 2.0 extension

```json
{ "jsonrpc": "2.0", "method": "capsule.invoke",
  "params": {
    "capsule_id": "capsule://solar.core/weather-query@1.0.0",
    "input": { "location": "Beijing" },
    "context": {
      "caller": "capsule://solar.agent/orchestrator@1.0.0",
      "trace_id": "abc-123-def",
      "budget": { "max_cost": 0.01, "max_duration_ms": 5000 }
    }}, "id": 1 }
```

Response carries `output` plus
`metadata.verification.{preconditions_passed, postconditions_passed}`.

Two design points worth calling out:
- **The caller is itself a capsule URI.** Capsules invoke capsules; there is no
  privileged "user" caller. This is what makes composition uniform.
- **A per-call budget is part of the request.** Cost control is in the protocol,
  not bolted on.

## 1.2.3 Capability advertisement

An agent publishes what it offers:

```yaml
apiVersion: capsule-registry/v1
kind: CapsuleProvider
metadata:
  provider_id: "agent://claude.anthropic/opus@4.5"
capabilities:
  provides: [capsule://solar.core/weather-query@1.0.0, ...]
  consumes: [capsule://solar.mcp/filesystem@1.0.0, ...]
endpoints:
  invoke:   "https://.../capsule/invoke"
  discover: "https://.../capsule/discover"
trust:
  signature: "ed25519:base64..."
  scare_scores: { weather-query: 85, email-search: 78 }
```

Note `provides` **and** `consumes` — an agent declares its dependencies as well
as its offerings, which is what makes federation-wide dependency resolution
possible in principle.

## 1.3 Multi-agent federation

Three heterogeneous agents (Claude / GPT-5 / Gemini), each with a local Capsule
Runtime, all sitting on a shared **Capsule Federation Layer** containing a
Registry (discovery), a Router, a Trust Verifier, and a Shared Capsule
Repository.

```typescript
interface FederationRegistry {
  register(capsule, provider): Promise<RegistrationResult>;
  discover(query: DiscoveryQuery): Promise<CapsuleInfo[]>;
  subscribe(pattern, callback): Subscription;
  verify(capsuleId, signature): Promise<VerificationResult>;
}
interface DiscoveryQuery {
  namespace?, capabilities?, min_scare_score?, providers?, exclude_providers?
}
```

`min_scare_score` as a *query filter* is the sharpest idea here: you don't ask
for a capsule, you ask for a capsule **above a quality threshold**.

### Cross-agent invocation, five steps

1. **Intent → local match.** User asks; Agent A searches locally, finds `weather-query@1.0.0`.
2. **Capability check.** "Can I execute this?" Yes → run locally (fastest). No → step 3.
3. **Federation lookup.** "Who can execute it?" → `[Agent B (SCARE 90), Agent C (SCARE 75)]`.
4. **Route & invoke.** Choose the highest SCARE score; JSON-RPC to Agent B.
5. **Verify & return.** Check response signature → check postconditions → return.

Local-first with remote fallback, ranked by trust score. Step 5 re-checks
postconditions **on the caller's side** — you do not take the remote agent's
word that its own contract was satisfied.

## 1.3.3 Trust and reputation

Three dimensions, then a weighted sum:

```yaml
static_trust:     # from spec analysis
  scare_score, spec_completeness, test_coverage        # each 0-100
dynamic_trust:    # from execution history
  success_rate            # 0-100
  avg_latency_ratio       # 0-10  — measured latency ÷ promised latency
  cost_accuracy           # 0-100 — how good the cost estimate was
community_trust:  # reputation
  usage_count, positive_reviews, incident_count
```

```
trust_score = static_trust * 0.3 + dynamic_trust * 0.5 + community_trust * 0.2
```

**Dynamic trust carries the most weight (0.5).** And two of its three terms are
comparisons of *promise vs. reality* — `avg_latency_ratio` and `cost_accuracy`
both measure whether the capsule's declared guarantees were honest. That is the
mechanism that makes the whole "declare your contract" scheme self-correcting:
lying in your spec lowers your trust score. Excellent presentation material, and
it connects directly to `v_capsule_health` in the architecture doc.

## 1.4 Governance — four tiers

| Tier | Namespace | Maintainer | Requirement | Review |
|---|---|---|---|---|
| 1 **Core** | `solar.core.*` | Solar core team | SCARE ≥ 90, 100% test coverage | mandatory code review + formal verification |
| 2 **Verified** | `verified.*` | certified developers | SCARE ≥ 70, signature verification | automated tests + community review |
| 3 **Community** | `community.*` | anyone | basic spec completeness | automated static checks |
| 4 **Experimental** | `experimental.*` | *(source states none)* | none | none — use at own risk |

The shipped system has a cruder but working analogue: `status: stable|draft` in
the registry, plus registration itself as the admission decision. The four-tier
model is a natural roadmap item and maps onto the existing `owner` field.

---

# Part 2 — Triggering and token economics

## 2.1 Four trigger types

| Type | Mechanism | Example |
|---|---|---|
| **Explicit** | direct call | `/capsule weather-query {"location":"Beijing"}` |
| **Intent** | NL → intent parse → capsule | "what's the weather in Beijing" → `weather-query` |
| **Event** | cron / webhook / file watch | `cron: "0 9 * * *"` → `daily-report` |
| **Composition** | data flow between capsules | `A.output → B.input`; `A.success → [B,C]` fan-out; `[A,B,C].all → D` join |

The shipped analogue of *Intent* is the `applicability` block on every manifest
(`task_types`, `positive_signals`, `negative_signals`) — a keyword-matching
surface for selection. That is a real, working instance of trigger type 2.

## 2.2 Token optimisation — the five strategies

The doc calls this "the key question: how do we minimise token consumption?"
All numbers below are the **document's own estimates**; none is measured
anywhere in the repo (see `13-…-open-questions.md`, item R4).

### Strategy 1 — Lazy specification loading
Three levels of detail, loaded on demand:

| Level | When | Content | Cost |
|---|---|---|---|
| 0 | always | index only: `{id, keywords}` | ~20 tokens each |
| 1 | after match | interface: `{input, output, errors}` | ~100 tokens each |
| 2 | before execution | full specification | ~500 tokens each |

Claim: 10 capsules go from 5,000 tokens → ~300 tokens (**94% saving**).

### Strategy 2 — Index compression
```
before:  {"capsule_id":"capsule://solar.core/weather-query@1.0.0", "name":..., ...}
         ~150 chars ≈ 40 tokens
after:   "C1:weather-query:weather,temp:Q"
         ~35 chars ≈ 10 tokens
format:  <shortID>:<name>:<keywords>:<type>
         type ∈ Q=Query, A=Action, M=Monitor, T=Transform
```
Claim: **75% saving**. The `Q/A/M/T` taxonomy is a compact capability
classification that does not exist in the shipped schema — the shipped analogue
is `capsule_kind` (`capability`/`guard`/`resource`), which classifies by *role in
the permission system* rather than by *what the capsule does*. Both would be
useful; only one exists.

### Strategy 3 — Result caching
| Tier | Store | TTL | Hit cost |
|---|---|---|---|
| L1 | in-memory, per session | end of session | 0 tokens, 0 ms |
| L2 | SQLite, local persistent | configurable, default 1 h | 0 tokens, ~1 ms |
| L3 | federation shared | configurable | 0 tokens, ~50 ms |

Cache key = `hash(capsule_id + input + version)`. **Idempotent capsules are
cached automatically; non-idempotent ones are never cached** — which is exactly
why `guarantees.idempotency` is a declared field.

The shipped system has a relative of this: `capsule_execution_gate.py` keeps
`dispatch-dedup.json` and `capsule-cooldown.json`. That is dedup + rate
limiting, not result caching — related idea, different purpose. Don't conflate
them in the report.

### Strategy 4 — Batch invocation
3 separate calls ≈ 150 tokens and 3 round trips; one `batch([...])` ≈ 80 tokens
and 1 round trip.

### Strategy 5 — Spec dehydration
Strip the spec to only what execution needs:
```
{ id: "C1", input: ["location:string:required"], timing: [5000, 500], idempotent: true }
```
~500 tokens → ~30 tokens (**94%**). Note the positional encoding
(`timing: [max, typical]`) — schema knowledge is moved out of the payload and
into the reader.

### 2.3 Metrics tracked per capsule
```typescript
tokens:  { spec_loading, input_encoding, output_decoding, total }
compute: { duration_ms, memory_mb, cpu_time_ms }
network: { calls, bytes_sent, bytes_received }
cost:    { api_cost, compute_cost, total_cost }
```
Token consumption is treated as a **first-class resource alongside CPU and
network** — arguably the most distinctive idea in the document, and a good
framing line for an agentic-AI audience.

### 2.4 The optimised invocation flow

1. **Intent recognition** — a *lightweight* parser: keyword matching + regex,
   **no LLM**, 0 tokens.
2. **Index lookup** — against the compressed in-memory index, 0 tokens.
3. **Cache check** — L1 → L2; a hit returns at 0 tokens.
4. **Minimal spec loading** — only input schema, timing, and
   `implementation_ref`. ~30 tokens.
5. **Execute** in sandbox with metrics collection, then update cache.

Bottom line claimed: **cache hit = 0 tokens; cache miss ≈ 30–50 tokens, versus
~500 tokens traditionally.**

Step 1 is the strategically important one and the easiest to miss: the design
deliberately puts a **non-LLM parser in front of capsule selection**. This is
the same "LLMs interpret semantics; deterministic code validates structure"
thesis from `CLAUDE.md`, applied to routing. Worth making explicit — it ties the
capsule design back to the project's stated core principle.

---

# Part 3 — Composition

## 3.2 The composition DSL

A fluent TypeScript API over the five combinators:

```typescript
const weatherToNote = weatherQuery.pipe(noteSave)
  .withMapping({ "body": "$.temperature + ' - ' + $.description" });

parallel([ weatherQuery.with({location:"Beijing"}).as("beijing"), ... ]);
conditional("input.use_cache === true", cachedWeather, weatherQuery);
loop("output.has_more === true", fetchPage, { max_iterations: 10 });
fallback([ weatherQuery, cachedWeather, defaultWeather.with({temp:"N/A"}) ]);
```

Summarised in the doc's closing block as the operator set
`pipe (>>)`, `parallel ([])`, `conditional (?)`, `loop (while)`, `fallback (||)`.

`.withMapping()` is the escape hatch that makes otherwise-incompatible capsules
composable — see below.

## 3.3 Type compatibility

For `A >> B` the rule is:

```
A.output_schema ⊇ B.input_schema      (A's output is a superset of B's input)
```

- Extra fields in A's output are fine.
- A missing or renamed field is incompatible — `{temp: number}` does not satisfy
  `{temperature: string}`.
- Fix: insert a mapping layer, `.withMapping({"temperature": "$.temp.toString()"})`.

Three stated rules:
1. **Structural subtyping** — more fields OK, fewer not; optional may become required.
2. **Covariance / contravariance** — outputs may be more specific, inputs more general.
3. **Mapping conversion** — supply a conversion function when types don't line up;
   its validity is checked **statically at composition time**.

Rule 3 is precisely what the shipped `adapter.*` capsules and the
`artifact-conversions.v1.json` registry are for. **That registry is currently
empty**, which means the conversion half of composition has a designed home and
no contents — the single cleanest "designed, built, not populated" example in
the codebase, and a strong roadmap item.

## 3.4 Derived-spec algorithm

`deriveSpec(composition)` computes the composite's timing, permissions, risk and
idempotency from its children. Per combinator:

| Combinator | max_duration | cost (max) | idempotency | permissions |
|---|---|---|---|---|
| **sequence** | Σ children | Σ children | `all(children)` | resources = ∪; denies = ∩ |
| **parallel** | max | Σ (all branches run) | `all(children)` | ∪ / ∩ |
| **conditional** | max | **max** (only one branch runs) | `all(children)` | ∪ (either could run) |
| **loop** | base × `max_iterations` | base × iters | **always `false`** | inherited |
| **fallback** | Σ (worst case: try all) | Σ | `all(children)` | ∪ / ∩ |

Three details worth keeping:
- **`denies` intersects while `resources` unions.** You keep a denial only if
  *every* child renounced it. This is the correct conservative direction and
  shows the permission algebra was thought through.
- **Loops are unconditionally non-idempotent** — a blunt but safe rule.
- **Fallback's typical cost is the primary's**, while max cost is the sum:
  the design distinguishes expected from worst case throughout.

Typical-case derivation differs from worst case per combinator
(`conditional` uses `avg`, `loop` uses `iters/2`, `fallback` uses `children[0]`),
so a plan can be priced both optimistically and pessimistically.

## 3.5 The composed worked example (source lines 1014–1099)

**The best demo asset in Part 3, and easy to miss.** The source closes with a
complete `kind: ComposedCapsule` — a daily-report generator — plus **its
machine-derived specification**, showing §3.4's algorithm applied end to end:

```
sequence:
  ├─ parallel( 4 source capsules )
  ├─ formatter
  └─ parallel( note-save , fallback( email-send → push-notify ) )
```

Derived spec (computed, not hand-written):
```yaml
max_duration: 35000        # summed across the sequence
denies: [filesystem]       # survived the ∩ across every child
idempotency: false         # a non-idempotent child poisons the whole
```

Three reasons to put this on a slide:
1. It is the **only** end-to-end composed artifact in either design doc.
2. `denies: [filesystem]` is a **concrete `denies` in action** — directly
   relevant to the reconciliation table's discussion of what the shipped format
   dropped (`13-…` §0).
3. `idempotency: false` demonstrates the derivation rules doing real work:
   one non-idempotent leaf makes the entire composite non-cacheable, which is
   exactly the safety property the algebra exists to compute.

## Closing summary (the doc's own)

- **Extension**: 5-layer stack; `capsule://ns/name@version`; JSON-RPC 2.0;
  federation + trust; governance `Core → Verified → Community → Experimental`.
- **Triggering / tokens**: `Explicit / Intent / Event / Composition`;
  lazy loading (94%), index compression (75%), L1/L2/L3 caching, batching,
  dehydration.
- **Composition**: 5 patterns, a DSL, structural-subtyping compatibility,
  automatic spec derivation.
