# 23 — Generalist, specialist, and what replaces the A2A hop

Written 2026-09-10 by the capability-capsule panel (pts/9), from the user's
design brief of the same date. Repo claims verified at `b0bf165f9`.

This note records the architecture the user is actually proposing, which is
**not** Alita-G's, and the open questions it opens. Read after `21-`.

---

## 1. The brief, restated

> Alita-G is **not the structure we want**. What it does demonstrate is that
> RAG-enhanced tool selection and **specialised rather than generalised agents**
> can be very powerful — the GAIA results are the evidence.
>
> The problem: a **generalist has to keep existing** in a long-running agentic
> system like AI4Research. Today, the generalist reaches a specialist over
> **A2A**. **The capability capsule replaces that.**
>
> Meanwhile the master agent produces loads of MCPs from tasks. So: who is the
> master agent? Which tasks go to the master and which to the specialist? The
> specialist *needs* MCPs to work, but at the start of a run all we have is a
> library of previous MCPs lying around. Does a task escalate to the master when
> the specialist can't find an MCP for it? **How do we quantify whether an MCP is
> good enough?**

Everything here is interlinked; the note keeps them together deliberately.

---

## 2. The structural gap in Alita-G that this exposes

The sharpest observation in the brief, and it is not in the paper's own framing:

**In Alita-G the master agent and the specialised agent are different *phases*,
not co-resident *roles*.** The master runs offline over a curated task suite to
build the MCP Box (§3.2); the specialist runs at inference with the Box frozen
(§3.5). Nothing routes between them at run time. There is no escalation path,
no "the specialist couldn't find a tool, hand it back", no online growth of the
Box during a session.

⚠ **Confirmed by the user 2026-09-10:** *"master specialist being diff phases is
something we can't do, so the A2A connection to capcap is there."* The phase
split is ruled out, so the capsule replacing the A2A hop (§3) is **settled
architecture**, not a proposal to be argued for. The report should present it as
a decision with a rationale, not as an option.

That is a legitimate design for a benchmark harness. It does not survive contact
with a **long-running** system, which is exactly what AI4Research is: the
generalist cannot be a build-time artifact that is discarded, because new gaps
keep arriving. So the brief's question — *who is the master, and what routes
where* — is not a detail Alita-G left out. **It is the question its architecture
does not have to answer and ours does.**

This is worth stating plainly in the report. It converts "we differ from
Alita-G" from a positioning claim into a structural one.

## 3. What the A2A hop actually is today [verified]

The generalist→specialist hop the capsule is meant to replace is **not** a
first-party architectural layer. It is a third-party **skill**:

- `skills/a2a-hub/SKILL.md` — version 1.3.0, `user-invocable: true`,
  describing the **MoltBot A2A Hub**, "a public registry and relay for AI
  agents", base URL `https://a2a-hub.fly.dev`.
- Register → receive `agentId` + `apiKey`; search the registry; relay messages;
  stream responses. Agent Cards carry `skills[]` with id/name/description/tags.
- `skills/a2a-hub/_meta.json` — published by an external owner id, not by this
  project.

So the current specialist boundary runs through **an externally hosted public
relay, reached with a remote API key, over agent cards whose skill list is
free-text description and tags.** There is no effect declaration, no contract,
no artifact typing, no trust class, and no local record of what the peer did.

**This makes the replacement argument much stronger than a protocol comparison.**
The pitch is not "capsules are a nicer A2A". It is:

> Today the boundary between our generalist and a specialist is an opaque
> remote relay we do not control, selected on free-text tags. A capability
> capsule turns that boundary into a locally-admitted contract with declared
> effects, typed inputs and outputs, and a trust class.

That is also the honest place to note the limit already recorded in `17-` §4.4:
where the peer really is remote and opaque, the capsule can constrain the
*boundary* but never statically verify the peer, so such capsules cap at
`evidence_transform` and require approval.

## 4. "How do we quantify whether an MCP is good enough?"

**The repo already has an answer for skills, and nobody has pointed it at
capsules.** `harness/lib/skill_capsule_bridge.py` [verified]:

**A five-level quality ladder** (`LEVEL_RANK`, lines 20-26):

| Level | Rank |
|---|---|
| `broken` | 0 |
| `discoverable` | 1 |
| `injectable` | 2 |
| `executable` | 3 |
| `effective` | 4 |

**A provenance ordering** (`SOURCE_RANK`, lines 28-33): `agents-skills` 4 >
`solar-native` 3 > `claude-skills` 2 > `codex-skills` 1.

And — the important part — **selection is already two-stage**
(`query_skill_candidates`, lines 757-805):

1. **A hard admissibility floor, applied before any scoring.**
   `min_level` defaults to `"injectable"`; anything below rank 2 is dropped
   outright. Quality is a *gate*, not a term in the ranking.
2. **Then a weighted relevance score** over the survivors: exact required alias
   `+120`, exact signal `+60 + 8·hits`, fuzzy substring `+8·hits`,
   `level_rank × 5`, a small bonus for prompt-surface skills. Deterministic
   tie-break, top-`limit` (default 6).

**This is the hierarchical structure the brief is reaching for, already built —
for skills, not for capsules or MCPs.** Alita-G, by contrast, is single-stage:
one cosine threshold, no quality floor, no ordering of provenance.

⚠ **This also settles the embeddings disagreement in `17-` §4.5.** The brief
says embeddings are very important; that amendment said typed matching should
displace them. Both are right about different stages, and the repo's own design
shows why:

| Stage | Question | Primitive | Must be |
|---|---|---|---|
| 0 | Is this capability *type-compatible* with the gap? | `composition.consumes/produces` over the 76 artifact types; effect ceiling; trust floor | exact, checkable |
| 1 | Is it *good enough to consider*? | quality ladder + provenance rank | ordered, gating |
| 2 | Which of the admissible ones is *most relevant*? | **embeddings** | ranked, tunable |
| 3 | Did the one we picked *conform*? | contract / schema / invariant check | fail-closed |

**Embeddings belong at stage 2 and nowhere else.** Alita-G's fragility (Tables 3
and 5: 16-point swing across τ, 12 across encoders) is not evidence against
embeddings — it is evidence against using them as the *admission* decision with
nothing above or below them. Inside a typed, quality-floored candidate set, a
bad threshold costs you rank order, not correctness. Note `17-` §4.5 is amended
accordingly.

## 5. The routing question — genuinely open

*Does a task escalate to the master when the specialist cannot find an MCP?*

This is the design decision the brief has not settled, and it should be an
explicit open question in the report rather than a guess. The shape of the
choice:

| Option | Mechanism | Cost |
|---|---|---|
| **Escalate on miss** | Specialist attempts stage 0; empty admissible set ⇒ hand to generalist, which solves the task *and* emits a draft capsule for the gap | Latency spike on cold gaps; generalist must stay resident |
| **Escalate on low confidence** | Escalate when the best stage-2 score is below a floor, not only when the set is empty | Needs a calibrated threshold — the exact fragility Alita-G's Table 3 warns about |
| **Plan-time routing** | The planner decides at freeze time, from `unsatisfiable_nodes`, before execution begins | Fits the existing freeze thesis; cannot react to a mid-run gap |
| **Always generalist first** | Generalist plans, specialist executes admissible nodes | Simple; forfeits Alita-G's efficiency result |

**Plan-time routing is the one that fits this codebase**, because gap detection
already exists there: the planner emits `unsatisfiable_nodes` (`17-` §4.1 stage
0), and the freeze contract says adaptation happens *before* the freeze. An
escalate-on-miss path at execution time would be a component re-deriving
capability after the contract is sealed — structurally the same mistake as the
`final_report` deadlock in `STATUS-CORRECTED.md`. Worth saying out loud: **the
system already has a documented incident about exactly this failure shape.**

That is a recommendation, not a decision. Flag it for the supervisor.

## 6. The cold-start problem the brief names

> "at the start of the run, we just have a library of previous MCPs lying
> around"

Alita-G has no cold-start problem because its Box is built offline against the
target domain before evaluation begins (and, per `21-` §6, against the very set
it reports on). A long-running system inherits whatever the last run left.

This makes two things load-bearing that Alita-G never needs:

- **Provenance and applicability scope on every capsule**, so a capability
  harvested from an unrelated domain is not offered for this one. Capsules have
  `provenance` in all 85 manifests [verified] — the field exists; what is
  missing is a *decay or scoping policy* over it.
- **The library lifecycle in `19-`** — promotion, demotion, retirement. An
  append-only Box (which is all Alita-G has, `21-` §5) guarantees the cold-start
  library degrades over time rather than improving.

## 7. Four further critiques from the brief, and where they land

1. **"Alita-G doesn't track MCPs in terms of previous inputs and
   observability."** Correct — an MCP carries `{code, description, use_case}`
   (Eq. 4) and nothing about its invocation history. There is no per-tool record
   of what it was called with, what it returned, or whether it failed. This is
   note `13-` R6 (no capsule quality feedback loop) restated from the outside,
   and it is why stage 1's quality ladder currently has nothing to read.
2. **"Doesn't focus on spatiotemporal composability like Cordis / dsh."**
   Correct, and note `20-` has the vocabulary: Cordis makes effects
   **reversible**; capsules make them **reviewable**; an MCP Box entry is
   neither. Retirement ordering is a proved property of the Cordis substrate,
   and Alita-G's Box has no retirement at all.
3. **"The multi-execution strategy could be inefficient due to the stochastic
   distribution."** ⚠ **The paper's own numbers confirm this.** Table 4: from
   k=3 to k=4, 28 MCPs are added and only **8** new clusters; accuracy is
   **flat** (83.03 → 83.03). The paper attributes multi-execution's value to
   "the stochasticity of MCP discovery" — the same mechanism that makes it
   wasteful past k=3. This is a strong point and it is citable.
4. **"Alita-G isn't testing or doing adversarial review on its MCPs, so edge
   cases could ruin effectiveness."** Correct — there is no test step anywhere
   in §3. The only signal is that the *task* succeeded once. This is precisely
   the red-team suite proposed in `17-` §5.3, and the adversarial review this
   panel's own notes went through (HANDOFF §6) is a usable model for it.

## 8. "MCPs must be abstracted and have a datatype associated"

The brief calls this possibly a must-have, and describes it as "skill discovery
on MCPs". It maps exactly onto machinery that already exists:
`composition.consumes` / `produces` over the **76-entry artifact-type registry**
[verified]. Alita-G's abstraction step produces parameters and docstrings but
**no type identity** — its tools are discoverable only through prose.

So the claim to make is narrow and true: *typing the capability is what turns
selection from similarity into matching, and this project already has the type
registry to do it.* That is stage 0 above.

---

## 9. Open questions this note adds

To the report's §10, and to HANDOFF:

- **Q7 — Who is the master agent?** A distinct resident generalist, the existing
  Elastic Planner, or a role the same model plays under a different profile?
- **Q8 — What routes where?** Plan-time (recommended, §5) or run-time
  escalation? If run-time, what is the confidence floor, and how is it
  calibrated without reintroducing Alita-G's threshold fragility?
- **Q9 — What is the quality ladder for capsules?** Reuse
  `skill_capsule_bridge`'s five levels, or define a capsule-specific one? And
  what observations feed it, given `13-` R6?
- **Q10 — Cold start.** Does a capsule harvested in one domain remain admissible
  in another, and does provenance decay?
- **Q11 — Online growth.** May the library grow *during* a run, or only between
  runs? Growing mid-run conflicts with the freeze contract.
- **Q12 — the compute envelope.** See note `24-`; it constrains all of the above.
