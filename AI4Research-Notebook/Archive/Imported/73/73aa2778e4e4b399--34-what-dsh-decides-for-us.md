# 34 — What the DeepSeek Harness decides for us

Written 2026-09-10 by the capability-capsule panel (pts/9).
Sourced from the dsh panel's notes in `notes/deepseek-harness/`. ⚠ Everything
attributed to dsh here is **[repo-claim]** — that panel inspected the checkout at
`c291e7961a` but did not build or run it (their `03-` §7). Re-verify anything
that reaches a slide.

> "If we know we gotta use DeepSeek Harness, how does the report get more simple,
> and how are the decisions made for us so we can focus just on capability
> capsule?"

**A platform commitment converts open design questions into inherited
constraints.** Nine of our open questions are answered outright, several more are
narrowed, and the report loses roughly a third of its surface area. What is left
is exactly the capsule.

---

## 1. Decided outright — stop designing these

| Our question | dsh's answer | Source |
|---|---|---|
| **B2 — must capsule generation emit all three seam roles?** | **Yes, by definition.** `AGENTS.md`: "adding a capability means designing all three roles"; a seam is "complete, never one role." Service Definition + Provider + Consumer | `dsh 03-` §1 |
| **Q28-Q29 — concurrency model, single writer** | Durable data is **immutable and versioned**: a write "exclusively publishes a **version-named successor beside the unchanged source**." Committed generations are never renamed, replaced or deleted | `dsh 02-` §5 |
| **`30-` §3.2 — must plans pin versions?** | Not our design decision — **it is the platform's data discipline.** We conform | `dsh 02-` §5 |
| **`32-` §4 — in-runtime reversibility** | **Every plugin contribution returns a disposer**; unloading unwinds everything it contributed, with no residue | `dsh 02-` §1 |
| **`26-` §5 — is there containment?** | **Yes.** `ctx.sandbox` with four backends — bwrap, Landlock, Seatbelt, Windows ACL — and `sandbox-policy` is a **separate package from the backends**, so policy and mechanism swap independently. Consumers wrap argv at the call site | `dsh 03-` §6 |
| **`31-` — where does evidence live?** | The **session log**. "Model-visible ⟺ logged," asserted by a runtime invariant; new model-visible input *requires* a new session event | `dsh 02-` §5 |
| **`23-` §7.1 — who records invocation history?** | Same. Transcripts, telemetry and persistence all derive from durable session events | `dsh 02-` §5 |
| **`17-` §5.4 — may a generated capability modify the runtime?** | **Already decided against.** Self-modification (`extensions/`) is **deliberately unmounted in every shipped tree**, reasoning: dynamic package code reaches the real runtime | `dsh 03-` §7 |
| **`33-` — how do we measure generation cost?** | `ctx.tokenMeter` — replay token measurement, already a service | `dsh 03-` §3 |

**Two of these are worth more than the others.**

**B2 has been open since the first session and is now closed.** The seam is
defined as all three roles; emitting one is not emitting a capability. So capsule
generation must produce a Service Definition, at least one Provider, and a
Consumer — and the report can state that as a requirement inherited from the
host, not a design choice we have to defend.

**The self-modification stance is the bigger one.** Note `17-` §5.4 proposed "a
generated capsule MUST NOT alter the admission gate, the registry, or the
verifier" as our safety rule, and `28-` §6.1 already corrected the claim that
this was novel. On dsh it is not even a proposal — **the host already unmounts
self-modification in every shipped tree, for exactly our stated reason.** Our
rule becomes *conformance with the platform's existing position*, which is a much
easier thing to defend than a principle we invented.

## 2. Also inherited — capability plumbing we would otherwise design

`dsh 03-` §3 lists **71 `ctx.*` services**. Several are things our notes proposed
building:

| We wanted | dsh already has |
|---|---|
| a runtime invariant checker (`31-` §4.3) | **`ctx.invariants`** — a runtime invariant registry |
| effect ceiling and approval ownership | `ctx.approval`, `ctx.authorization`, `ctx.permissionPresets`, `ctx.credentials`; `dsh-user-approval` owns definition *and* implementation |
| a skills channel (`17-` §4.4) | `ctx.skills` |
| concurrency primitives (`30-`) | `ctx.jobs`, `ctx.subagents`, `ctx.agentTeams` |
| sandbox policy separate from mechanism (`26-` §5) | `ctx.sandboxPolicy` |
| an evidence store | `ctx.sessionPersistence`, `ctx.sessionProjections`, `ctx.sessionQuery` |
| token/cost accounting (`33-`) | `ctx.tokenMeter` |

And one that reframes a whole section: **dsh's generated `docs/tool-catalog.md`
declares, per tool, its `Requires` (the `ctx.*` services it injects) and its
`Writes / affects` (the session events it emits)** — described by the dsh panel
as "a machine-maintained capability manifest for the model surface"
(`dsh 03-` §4).

⚠ **That is a partial effect declaration that already exists.** It is generated
by booting plugins rather than declared by the author, it is coarse, and it is
documentation rather than an admission input — but the report should acknowledge
it rather than claim nobody declares anything. The capsule's contribution
narrows, accurately, to: **author-declared, fine-grained, checked before
admission, and used by the scheduler** — rather than generated-after-the-fact and
used by humans.

## 3. Narrowed, not decided — two constraints that cost us something

**MCP is tools-only.** `dsh 03-` §7: one package (`mcp-client`), tools bridged
under server-qualified names; **MCP resources and prompts are not supported**, and
**nothing ships enabled**.

This trims note `17-` §4.4's "capsule as the single admission record across three
channels". On dsh the MCP surface is tools only, so the unification claim should
be stated over *tools*, not over MCP's full surface. Say the limit; it is the
host's, not ours.

**A2A is not in dsh at all.** No seam, no service, no package. So the A2A story
stays ours — and `23-` §3 already established that in AI4Research today it is a
third-party skill hitting a public relay. Under a dsh target, "capsule replaces
the A2A hop" means *the hop does not exist yet and the capsule is how it would be
built*, which is a cleaner claim than replacing something.

**PTC mode is a competing answer to selection bloat.** `dsh 03-` §5: under
`mode: ptc` the tool registry contributes a single `run_code` tool plus a
generated SDK, and nested calls re-enter the full guarded pipeline. That is a
different answer to tool-count pressure than our four-stage selection (`23-` §4)
— not incompatible, but the report should not present typed selection as the only
option when the host ships another.

## 4. What is left — and it is exactly the capsule

The dsh panel's own comparison (`dsh 05-` §3) lists what the capsule design has
that dsh does not. It is a short list, and it is our report:

1. **Formal pre/postconditions and declared effects per capability.** dsh's tool
   metadata is generated, not declared, and not a contract.
2. **A planner that selects capabilities from declarations.** dsh composition is
   not declaration-driven.
3. **Trust ranks and admission gating.** dsh's nearest equivalents are the sandbox
   and approval seams — containment and consent, not admissibility.
4. **Verification bundled with the capability.** dsh separates them: tests live
   apart from the code they test.

Add what this session established and nothing else:

5. **Silent rot and held-out conformance** (`29-`) — the empirical case.
6. **Typed retirement reasons and taint propagation** (`31-`).
7. **Declared state class, compensation, resource quarantine** (`32-`).
8. **The investment ladder and blast-radius-over-reuse rule** (`33-`).

## 5. How the report actually gets simpler

| Section (from `OUTLINE.md`) | Under a dsh commitment |
|---|---|
| §4 three channels / MCP / A2A | **Collapses to ~1 page.** dsh contains an MCP layer, tools-only; A2A absent. The four-layer table stays as framing; the comparison stops being a section |
| §5 where this sits in the harness | **Becomes concrete instead of speculative.** Seams, disposers, versioned successors — named mechanisms, not analogies |
| §5c deployment and threat model (`26-`) | **Halves.** Containment exists; the argument narrows to *"declared effects turn a sandbox from a guess into a policy"* — which was always the strongest sentence in it |
| §9 safety envelope | **Halves.** The no-self-modification rule is the host's existing stance; we conform and add the effect ceiling |
| concurrency (`30-`) | **Mostly inherited.** Versioned immutable writes are platform discipline. Ours: the gap lease, and monotonic admission |
| §7 the two gates | **Unchanged — this is the contribution** |
| §8 evaluation | **Unchanged, and cheaper**: `ctx.tokenMeter` and the session log make Track B measurable rather than proposed |

**Net: roughly a third less report, and the remainder is all capsule.**

The framing sentence for the opening:

> Targeting the DeepSeek Harness settles how capabilities are loaded, swapped,
> reverted, sandboxed and logged. What it does not settle — and what this report
> is about — is whether a capability should be allowed to run at all.

## 6. What to verify before this reaches a supervisor

All of §1-3 is **[repo-claim]** from another panel's inspection. The load-bearing
items to confirm against the dsh checkout:

- [ ] The three-role obligation in `AGENTS.md` — quoted, since B2 now rests on it.
- [ ] The versioned-successor rule for durable data — the concurrency story rests on it.
- [ ] `ctx.invariants` semantics — a registry of *what*, checked *when*? If it is
      startup-only it does not serve `31-` §4.3.
- [ ] That `extensions/` is unmounted in the shipped bundle, not merely optional.
- [ ] Whether `ctx.tokenMeter` measures live or only on replay — `33-` needs live.

## 7. Open questions this leaves

- **Q48 — Is the capsule a seam, or a layer above seams?** If a capsule *is* a
  seam, the manifest is the Service Definition's contract. If it sits above,
  it governs seams and is a separate registry. This is now the central design
  question and it did not exist before the platform was fixed.
- **Q49 — Does capsule admission run inside the Cordis plugin lifecycle** (a
  capsule is admitted at load and disposed at unload), or beside it?
- **Q50 — Does PTC mode change the selection story?** If capabilities reach the
  model as an SDK rather than tool schemas, stage-2 ranking may matter less and
  stage-0 typing more.
