# 05 — Comparison and takeaways

> **Cross-panel note.** The deepseek-harness panel did **not** inspect the
> AI4Research checkout. The capsule facts below are quoted from the AI4Research
> panels' own notes ([../07-capability-capsules.md](../07-capability-capsules.md),
> [../16-a2a-and-three-way-comparison.md](../16-a2a-and-three-way-comparison.md)),
> not independently verified here. dsh facts are **[repo-claim]** from its docs
> unless marked [verified]. **Take or leave this note** — it is offered as
> comparison material for the capsule report, not as a finding about AI4Research.

---

## 1. The two systems are answering different questions

| | **AI4Research capability capsule** | **DeepSeek Harness capability seam** |
|---|---|---|
| Unit | a declared capability: spec + implementation + verification | a swappable capability: Service Definition + Provider(s) + Consumer(s) |
| Declared in | a YAML manifest, gated by a registry file | TypeScript — an abstract class or concrete registry owning a `ctx.<key>` |
| Primary guarantee | *what it touches, what must be true before/after, who may run it* (SCARE) | *any provider can be swapped without forking consumers* |
| Enforcement | registry admission, schema, evidence gates | the type system + Cordis effects + 55 CI gates |
| Composition | planner selects and composes capsules by declared edges | Cordis config rows, layered by profile/bundle/patch |
| Runtime story | capsules gate what the planner may invoke | seams are live services; unloading a plugin unwinds its registrations |
| Scale [verified/quoted] | 80 registered capsules | 71 `ctx.*` services across 268 packages |

Put plainly: **a capsule is a contract about a capability; a seam is a socket for
a capability.** They are complementary, not competing. A capsule answers "may I
run this and what will it do to me?" A seam answers "can I replace this without
touching anything else?"

The clean framing for the report, if it's wanted:

- **MCP** — a wire protocol for reaching *external* tools.
- **A2A** — a protocol for agents talking to agents.
- **dsh seam** — an *in-process* role contract making capabilities substitutable.
- **capsule** — a *declarative* contract making capabilities admissible.

Different layers of the same stack. dsh actually *has* an MCP layer
(`packages/mcp/mcp-client`, tools only, nothing enabled by default), so it sits
at the seam layer and consumes the MCP layer — which is evidence the layering is
real and not just a rhetorical device.

## 2. What dsh has that the capsule design (per our notes) does not

These are the places where dsh is worth citing as prior art:

1. **Reversibility as a first-class primitive.** "Registrations are effects" —
   every contribution returns a disposer, so unmounting is total. A capsule
   registry can admit and reject; effects let you *withdraw* a live capability
   mid-session. If capsules ever want hot-swap, this is the mechanism to copy.

2. **Model-visible ⟺ logged, asserted at runtime.** Anything reaching a model
   request must be reconstructable from the session log, enforced by a runtime
   invariant. This is a stronger accountability guarantee than "declared effects,"
   because it holds for *inputs* too, not just side effects. Our notes record
   capsule **Accountability** as "responsibility is traceable" — dsh's version
   makes the *entire model context* replayable.

3. **Immutable, versioned durable data with adjacent-only migration.** Committed
   session generations are never renamed, replaced, or deleted; a write-open
   publishes a version-named successor *beside* the source; unknown event types
   **refuse the log** unless flagged `ignorable`. And prerelease publication
   creates real obligations. Compare with the capsule notes' concern about schema
   drift (`v1.draft.json`) and registry/disk reconciliation.

4. **Generated documentation as ground truth.** `docs/tool-catalog.md` is produced
   by *booting each plugin* and reading real schemas, with a completeness guard
   that fails if a `packages/*/tool-*` package is missing from the manifest.
   That is the direct antidote to the stale-count problem our own notes flag
   (`NEW-MACHINE-START-HERE.md` saying 68 when the answer is 80). **If one idea
   from dsh goes into the "how to do better" section, make it this one:
   *a count that appears in prose is a count that will go stale; generate it or
   gate it.***

5. **A resolved answer to tool-surface bloat: PTC mode.** Instead of N tool
   schemas, expose one `run_code` tool plus a generated SDK in the runtime's
   language; nested calls re-enter the full guarded pipeline and are individually
   logged. Our notes list "token optimization unmeasured" as an open capsule
   question — PTC is a shipped, differently-shaped answer worth citing, though
   dsh publishes no measurement either.

6. **A closed, machine-checked decision-record system.** 309 implemented / 21
   proposed / 629 archived Agent Notes, path-encoded lifecycle and class, frozen
   append-only archive, no index by policy. See
   [04-conventions-and-governance.md](04-conventions-and-governance.md) §1.

## 3. What the capsule design has that dsh does not

Being fair in the other direction:

- **Formal pre/postconditions and declared effects per capability.** dsh's tool
  catalog records `Requires` and `Writes / affects` per *tool package*, which is
  the same instinct — but it is documentation output, not an admission gate. dsh
  has nothing corresponding to SCARE's **Completeness** ("completion is
  verifiable") or **Risk** ("risk is quantifiable").
- **A planner that selects capabilities from declarations.** dsh composition is
  authored by humans in config layers, not selected by a planner at runtime.
- **Trust ranks / admission gating.** dsh's nearest equivalents are the sandbox
  policy, permission presets, and the approval seam — runtime confinement rather
  than declarative trust classification.
- **Verification bundled with the capability.** dsh separates these: tests live
  in the package, the coverage gate is repo-wide (per-file 100% on
  `packages/*/*/src`), and there's no per-capability evidence artifact.

So the honest comparative sentence is: **dsh formalizes substitutability and
replayability; capsules formalize admissibility and verification.** Neither
subsumes the other.

## 4. Practices worth stealing regardless of the report

Ranked by how cheap they are to adopt here:

1. **One home per fact; current-state prose.** Their doc standard, gated by
   `verify-doc-budgets` and `verify-doc-refs`. Our note tree already has known
   duplication and a recorded self-contradiction (see `../14-cross-panel-corrections.md`).
2. **Status in the path.** `proposed/` → `implemented/` → `archived/`, so moving
   the file *is* the state transition, and `archived/` is explicitly stripped of
   authority. Directly applicable to our `notes/` tree.
3. **Generate every number that appears in prose**, or gate its freshness in CI.
4. **"Report only commands run."** Their agent instruction, and a good match for
   our `[verified]` / `[repo-claim]` marking.
5. **Ban metaphors and vague nouns in technical prose** — `contract`, `boundary`,
   `shape` reserved for their literal meanings.
6. **`Known Limitations and Deferred Work` is a required README section**, with an
   explicit allowlist for exemptions. An honest-limits section that is *mandatory
   by gate* is much harder to quietly drop than one that is merely customary.

## 5. Caveats before citing dsh anywhere public

- It is **0.1.5-rc.2, three months old, explicit developer preview**, with
  "THERE WILL BE COMPATIBILITY-BREAKING CHANGES" in bold in the README. Do not
  present it as a settled standard.
- Nothing here was **built or run**. Every behavioral claim is from its docs.
- The 16,511-commit / 268-package figures are [verified] by inspection, but they
  measure *activity and surface*, not maturity or adoption.
- The Cordis paper (arXiv 2608.25512) is cited by the README; the panel did not
  read it.
