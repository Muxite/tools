# 17 — Self-extending capability capsules: prior art, papers, and design

Written 2026-09-10 by the capability-capsule panel (pts/9).

**The new goal, as stated:** capability capsules become an abstraction over
*AI-native functions* that let **AI build AI** (agent builds agent). The agent
system must be able to **search for capabilities → understand them → find
frameworks → build something skill-like → plug it back into itself, ready for
use.** "Skills mixed with MCP mixed with A2A, and standardized." Must integrate
with the DeepSeek harness (see `16-…` §4 — that phrase needs clarifying).

This note covers: who else is doing this, the paper landscape, and a concrete
design + implementation + evaluation plan.

> **Citation hygiene.** arXiv IDs marked ✅ were confirmed by live search on
> 2026-09-10. IDs marked ⚠ are from model recall and **must be verified before
> they appear in a report** — wrong arXiv IDs are exactly the error a supervisor
> spots. Verify with `arxiv.org/abs/<id>`.

---

## 1. The honest headline

**This is an active, crowded research area, and one system has already built
almost exactly what is being proposed.**

That is not a reason to abandon the direction. It is a reason to (a) position
against the prior art deliberately, and (b) claim the part that is genuinely
open. Walking into a supervisor meeting proposing Alita's architecture without
knowing Alita exists would be the worst outcome of this project.

---

## 2. Who else is doing this

### 2.1 The closest match — Alita / Alita-G ⚠ READ FIRST

| | |
|---|---|
| **Alita** | *"Generalist Agent Enabling Scalable Agentic Reasoning with Minimal Predefinition and Maximal Self-Evolution"* — arXiv **2505.20286** ✅ |
| **Alita-G** | *"Self-Evolving Generative Agent for Agent Generation"* — arXiv **2510.23601** ✅ |

Alita's design principle is *"Simplicity is the ultimate sophistication"*:
minimal predefinition, maximal self-evolution. It **dynamically generates,
adapts and reuses MCPs** based on the demands of each task.

Alita-G goes further and is the direct analogue of the proposed direction: a
generalist agent runs a curated suite of domain tasks, **synthesizes candidate
MCPs from successful trajectories**, abstracts them to **parameterized
primitives**, and consolidates them into an **"MCP Box"** — turning a generalist
into a domain expert. Reported: **83.03% pass@1 / 89.09% pass@3 on GAIA
validation** (claimed SOTA), with **~15% fewer mean tokens per example** than a
strong baseline.

**Read this as the shape of the proposal:** search → build → abstract → curate →
plug back in. The "MCP Box" is functionally "the capsule registry".

**What this means for positioning.** Alita-G already demonstrates
trajectory → MCP synthesis → curation → reuse. What it does **not** demonstrate
is a *contract and admission layer*: there is no declared effect set, no
pre/postcondition contract, no fail-closed admission gate, no operator
compatibility, no provenance-based trust tier. Alita curates for **usefulness**;
capsules would curate for **admissibility**. That distinction is the project's
strongest available claim to novelty — and §2.4's paper says it is the exact
thing the field is getting wrong.

⚠ **Amended 2026-09-10 after reading the paper in full — see note `21-`.**
Three corrections to the paragraph above, all of which strengthen it:

- The MCP Box **also has no lifecycle at all** — append-only accumulation, with
  no versioning, promotion, demotion, retirement or status field. It lacks not
  only the admission layer but everything in note `19-`'s lifecycle machine.
- "Curates for usefulness" is now a **citation, not an inference**: Alita-G's
  Eq. 5 collects MCPs solely from executions where `π_master(x_i) = y_i`.
  Correct final answer ⇒ the tools produced along the way are kept, unchecked.
- ⚠ **Corrected 2026-09-11.** This bullet previously read that Alita-G's
  abstraction step "explicitly targets hidden dependencies, interface violations
  and specification drift — the same list as §2.4". That was the fabricated
  vocabulary of `29-` §5.1 re-attributed to a *second* paper: those three terms
  occur **zero** times in 2510.23601 as well, and the "same list as §2.4"
  cross-reference dangled once §2.4 was rewritten. What §3.3 actually names:
- Alita-G's abstraction step (§3.3) names four transformations — **Parameter
  Generalization, Context Removal, Interface Standardization, Documentation
  Enhancement** — and performs all four with a single unverified LLM rewrite
  (Eq. 6). The contrast to draw is **not** "they ignore the problem" but
  **"they prompt for it, we check for it."** That is fairer and lands harder,
  and it survives the correction unchanged.

### 2.2 Tool creation — the established line

| System | Idea | arXiv |
|---|---|---|
| **Voyager** | The canonical skill library: on learning a new capability, write it as a JavaScript function into a growing **Skill Library**, retrieve and reuse on similar future tasks. Minecraft, intrinsic-motivation-driven exploration. | 2305.16291 ⚠ |
| **CREATOR** | **Disentangles abstract tool *creation* from concrete tool *usage*** for modularity | 2305.14318 ⚠ |
| **LATM** (LLMs as Tool Makers) | Split a strong "tool maker" model from a cheap "tool user" model | 2305.17126 ⚠ |
| **CRAFT** | Retrieval over a crafted toolset | 2309.17428 ⚠ |
| **TroVE** | Induces reusable verified toolboxes for programmatic tasks | 2401.12869 ⚠ |
| **SkillWeaver** | Web agents self-improve by discovering skills, **practising** them, and distilling practice into robust plug-and-play APIs. WebArena +31.8%, real sites +39.8%; APIs from strong agents lift weaker agents **up to +54.3%** | **2504.07079** ✅ |
| **ATLASS / Live-SWE-Agent** | **Reactive** tool creation — build the tool when a capability gap is hit | ✅ named in survey |
| **ToolGen** | Encodes tools as **tokens** for efficient retrieval from very large libraries | 2410.03439 ⚠ |

CREATOR's creation/usage split is worth stealing: it is the same boundary the
capsule design already draws between *specification* and *implementation*.

### 2.3 Agents designing agents — the architecture line

| System | Idea | arXiv |
|---|---|---|
| **ADAS** (Automated Design of Agentic Systems) | Meta Agent Search — an agent searches the space of *agent designs* | 2408.08435 ⚠ |
| **Darwin Gödel Machine** | Open-ended evolution of self-improving agents that **rewrite their own code**. SWE-bench **14.2% → 30.7%**; improvements **generalize across foundation models**; ablations show both self-improvement *and* open-ended search are necessary | **2505.22954** ✅ |
| **AgentSquare / EvoAgent** | Population-based mutation + selection over agent configurations | ✅ named in survey |
| **AFlow** | Workflow-graph search | ✅ named in survey |
| **Alita-G** | Generalist → domain expert via MCP generation | 2510.23601 ✅ |

DGM is the reference point for "AI builds AI" credibility — and for its honesty:
the original Gödel-machine ideal required *provably* beneficial self-changes,
which DGM concedes is impractical, substituting empirical benchmark improvement.
**That concession is exactly where a capsule-style contract layer earns its
place**: you cannot prove the change is beneficial, but you *can* mechanically
check that the artifact conforms to a declared contract before admitting it.

### 2.4 ⭐ The paper that justifies the whole project

**"Beyond Task Completion: A Verification-vs.-Conformance Gap in Tool-Evolving
Agents"** — arXiv **2604.00392** ✅

⚠⚠ **REWRITTEN 2026-09-10 — the original text here was wrong.** It listed four
"named failure modes" (specification drift, hidden dependencies, incomplete
validation, interface violations) and a "multi-stage verification pipeline"
mitigation. **None of those phrases occur anywhere in the paper** — they came
from a second-hand summary, and this note was the source the rest of the panel's
work copied from. Full close read and correction: note `29-`.

**What the paper actually says.** Its concept is **silent rot** — a synthesised
tool that *executes cleanly* but scores zero on a held-out conformance suite for
the capability it was built for. *"The rot is silent because no in-session signal
flags it: the verifier scores task outputs, not tools."*

The measurement (Table 5, 222 preserved tools, three tool-creating protocols):

| System | Tools | Mean C | Silent rot % |
|---|---|---|---|
| One-Shot | 119 | 0.000 | **100.0%** |
| ToolMaker-style | 19 | 0.000 | **100.0%** |
| CREATOR-style | 84 | 0.049 | 91.7% |
| **Total** | **222** | **0.018** | **96.8%** |

Calibration: hand-written reference implementations score **C=1.00 on all 16
capability suites**, so the suites are passable; mean held-out robustness is
0.52-0.54, so the tools run and return *wrong values*; and the sessions carrying
these libraries still pass a third of their verified tasks.

It is a **benchmark and audit-schema paper** (EvolveTool-Bench, 99 tasks, three
domains, sessions in six roles — seed / gap / variant / composition / regression
/ adversarial, which is where note `19-`'s six probe roles come from). Its
recommendation: *"verifier coverage, reuse decomposition, held-out conformance –
is the minimum a deployed tool-evolving agent should emit **between releases**."*

**This is the capsule thesis, stated by an independent paper, as an empirical
finding about exactly the system being proposed.** If the presentation has one
citation, make it this one. It converts "capsules are nice engineering hygiene"
into "capsules address a measured failure mode of self-extending agents."

### 2.5 Skill graphs and scale — closest to capsule composition

| System | Relevance | arXiv |
|---|---|---|
| **SkillDAG** — *Self-Evolving Typed Skill Graphs for LLM Skill Selection at Scale* | Skills as **typed DAG nodes**, typed by I/O specification; hierarchical composition; addresses **selection degradation as the library grows**, replacing linear search with graph+type retrieval | **2606.03056** ✅ |
| **CoEvoSkills** — *Self-Evolving Agent Skills via Co-Evolutionary Verification* | Co-evolutionary framework producing multi-file skill *packages*. Two findings that matter: **agent-created skills beat human-curated ones** (they capture reasoning patterns and tool-use strategy, not just code), and skills are **portable across model families** | **2604.01687** ✅ |
| **ReCreate** — *Reasoning and Creating Domain Agents Driven by Experience* | Experience-driven domain-agent creation | **2601.11100** ✅ |

**SkillDAG is the single most important design read after Alita-G.** It is
independently solving the problem the capsule registry will hit at scale: with
80 capsules, `applicability` keyword matching is fine; at 800 self-generated
ones it is not. SkillDAG's answer — type the skills and search the graph rather
than the list — is exactly what `composition.consumes/produces` + the 76-entry
artifact type registry already position capsules to do. **The existing typed
composition search is the asset here; say so.**

⚠⚠ **Corrected 2026-09-10 — see note `35-`.** "Self-evolved skills beat
human-curated" is **true only with the verification loop**, and stating it bare
is contradicted by the paper's own baselines [verified]: three unverified
self-generation methods score **30.7% / 32.0% / 34.1%** against a **30.6%**
no-skill baseline, while human-curated scores **53.5%** and CoEvoSkills **71.1%**.

> **Agents *with* a verification loop write better skills than humans. Agents
> without one write skills worth about as much as no skills at all** — and about
> twenty points worse than human curation.

The paper's own words: the gains "originate from the iterative verification loop,
not from the skill-creation prompt itself." **This is a much stronger argument for
the capsule direction than the loose version**, and it pairs with 2604.00392
(`29-`) as the same finding from the opposite direction.

CoEvoSkills' "portable across model families" result is the argument for keeping
capsules provider-neutral — which the repo's 52/50 provider-neutral operator
split already does.

### 2.6 The organizing survey

**"A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve on the
Path to Artificial Super Intelligence"** — arXiv **2507.21046** ✅
(+ curated list: `github.com/XMUDeepLIT/Awesome-Self-Evolving-Agents`)

Use its four-axis taxonomy as the report's skeleton — it is the field's own
vocabulary, and adopting it signals literacy:

| Axis | Categories | Where this project sits |
|---|---|---|
| **What to evolve** | Models · Context · **Tools** · Architecture | **Tools** (primary), drifting toward Architecture |
| **When to evolve** | intra-test-time · **inter-test-time** | **inter-test-time** (build the capability, then reuse) |
| **How to evolve** | reward-based · imitation/demonstration · population-based | likely **imitation from successful trajectories**, as Alita-G |
| **Where** | general · specialized (coding, GUI, finance, medical) | **specialized: scientific research** — the existing AutoSci lifecycle |

Its safety section states the concern directly: *"unconstrained generation of
code risks creating tools with exploitable vulnerabilities,"* naming **automated
verification and sandboxing** as critical open problems. Both are capsule
territory — and note the capsule design *already specifies* a sandbox
(`11-…` §11) that was never built.

Its three evaluation paradigms should structure the benchmarking plan (§5):
**static assessment**, **short-horizon adaptive**, **long-horizon lifelong**.

---

## 3. Where this leaves the positioning

**Occupied by prior art:** trajectory→tool synthesis, MCP generation, skill
libraries, typed skill graphs, self-improving code, curation into a reusable box.

**Genuinely open — and defensible as the contribution:**

1. **A conformance/admission contract for self-generated capabilities.**
   §2.4 shows the field measures the failure and lacks the fix. Capsules already
   have the vocabulary: `contract` (pre/post/invariants), `effects`,
   `verification`, `operator_compatibility`, `provenance`.
   ⚠ **And a conformance/selection contract**, which this note originally
   conflated with admission. Choosing *which* capability runs is a second,
   distinct place the same contract applies — see the amendment to §4.5.
2. **Fail-closed admission of *self-authored* artifacts.** The existing gate has
   five rejection reasons and is implemented and tested. Nobody in §2 gates
   generated tools this way — they gate on task success.
3. **Unifying the three layers under one declaration.** Skills, MCP servers and
   A2A peers are three different acquisition channels; a capsule can be the
   single admission record for all three (`bindings.skills`,
   `bindings.mcp_capabilities`, and a proposed `bindings.a2a_agents`).
   **This is the "standardized" part of the supervisor's brief, and it is real.**
4. **Effect declaration for generated capabilities.** No system in §2 makes a
   generated tool declare its blast radius before admission.

**One-line pitch:**
> *Prior work has shown agents can build their own tools. It has also shown
> those tools silently violate their own specifications. Capability capsules are
> the admission contract that decides whether a self-built capability is allowed
> to become part of the system.*

---

## 4. Design

### 4.1 The self-extension loop

Mapping the supervisor's five verbs onto concrete stages:

```
  ┌─ 0. GAP DETECTION ──────────────────────────────────────┐
  │   planner emits `unsatisfiable_nodes`  ← ALREADY EXISTS  │
  └────────────────────┬────────────────────────────────────┘
                       ▼
  1. SEARCH      find candidate capabilities
                 channels: capsule registry → skills → MCP servers
                 → A2A agent cards → code/paper retrieval
                       ▼
  2. UNDERSTAND  normalize a candidate into a DRAFT CAPSULE
                 (contract, effects, bindings) — the "understanding"
                 IS the manifest; if it can't be written, it isn't understood
                       ▼
  3. FRAMEWORK   choose the implementation substrate
                 (existing skill · new MCP server · A2A delegation · code)
                       ▼
  4. BUILD       synthesize implementation + self-checks
                       ▼
  5. VERIFY      conformance gate — §4.3.  ← THE CONTRIBUTION
                       ▼
  6. ADMIT       register in the capsule registry; status starts `draft`
                       ▼
  7. USE         normal admission + dispatch    ← ALREADY EXISTS
                       ▼
  8. OBSERVE     evidence ledger → promote / demote  ← R6 in note 13
                       └──────────► back to 1
```

**Stages 0, 7 are already built. Stage 8 is note 13's R6 gap. Stages 1–6 are
the new work.** Framing the project as "close the loop" rather than "build a
new thing" is both more accurate and much more achievable.

### 4.2 The key design decision: the capsule is the *understanding artifact*

Do not treat capsule generation as a documentation step after building a tool.
**Invert it**: the agent must write the capsule manifest *first*, and the
manifest is the specification the implementation is then generated against and
checked against.

Why this matters — ⚠ **rewritten 2026-09-11**, as this block was grounded in
the withdrawn failure-mode list and cross-referenced a §2.4 that no longer
contains it. The real argument is stronger. What 2604.00392 measured is a tool
that executes cleanly and is *wrong for the capability it claims to implement*.
A specification written after the code, from the code, cannot catch that — it
faithfully documents whatever the code does, including the parts that are wrong.
Writing the manifest first makes three otherwise-unobservable things checkable:
- **Undeclared effects** surface when you must declare `effects` and
  `composition.consumes` up front.
- **Output nonconformance** becomes checkable because `contract.inputs/outputs`
  carry `schema_ref`s.
- **Capability mismatch** — the silent-rot case itself — becomes testable,
  because there is a declared contract to replay held-out inputs against.

This is also what distinguishes the design from Alita-G, where the MCP is
abstracted *from* successful trajectories — spec-after-the-fact, exactly the
pattern §2.4 measures failing.

### 4.3 The conformance gate — the novel component

Extends the existing 5-reason admission gate with checks specific to
*self-authored* capsules. Proposed rejection reasons:

| Reason | Check |
|---|---|
| `CONTRACT_UNSATISFIABLE` | preconditions cannot be met by any producible artifact |
| `EFFECT_UNDECLARED` | static analysis finds a syscall/network/write not in `effects` |
| `EFFECT_ESCALATION` | declared effects exceed the parent task's authorized envelope |
| `SCHEMA_NONCONFORMANT` | emitted output fails its own `outputs.schema_ref` |
| `INVARIANT_VIOLATED` | a declared invariant fails on the verification corpus |
| `NEGATIVE_CONTROL_FAILED` | capsule selected for a task it declares as a `negative_signal` |
| `DUPLICATE_CAPABILITY` | semantically equivalent capsule already registered |
| `PROVENANCE_UNVERIFIED` | generating trajectory/model/prompt not recorded |

`EFFECT_UNDECLARED` is the highest-value one and the most defensible research
contribution: **compare the declared effect set against the statically-observed
effect set of the generated implementation, and fail closed on divergence.**
That is a mechanical, testable answer to the gap between what a capability
declares and what it actually does.

`NEGATIVE_CONTROL_FAILED` reuses an idea the repo already has —
`capability_activation_proof.py` already runs negative controls (`07-…`).

### 4.4 Unifying skills / MCP / A2A

The capsule becomes the **single admission record** regardless of channel:

```yaml
bindings:
  skills:           { required: [], optional: [...] }   # exists
  mcp_capabilities: { ... }                             # exists
  a2a_agents:       [ ... ]                             # PROPOSED
```

Per-channel implications:
- **Skill** — local code; full static effect analysis possible; highest trust.
- **MCP** — declared tool schema, but MCP models **no effects** and its
  annotations are explicitly untrusted (`15-…` §6). The capsule must supply the
  effect declaration MCP lacks. *This is the cleanest illustration of the
  capsule/MCP relationship: the capsule adds what MCP deliberately omits.*
- **A2A** — the peer is **opaque by design** (`16-…` §1), so effects can never
  be statically verified. A2A-bound capsules must therefore be capped at
  `trust_class: evidence_transform` at best, never `measured_execution`, and
  should require `approval_required` side-effect policy. **An honest design
  states this limit rather than pretending otherwise.**

### 4.5 Scale: don't let the registry become a linear scan

At 80 hand-written capsules, `applicability` keyword matching works. Under
self-generation the count grows without bound, and SkillDAG (§2.5) documents
the selection degradation that follows. Mitigation, in order of cost:

1. Use the **existing** typed composition search over
   `composition.consumes/produces` + the 76 artifact types — this is already a
   typed graph, which is what SkillDAG argues for.
2. Add `DUPLICATE_CAPABILITY` at admission so the library does not accumulate
   near-identical capsules.
3. Only then consider embeddings/ToolGen-style token retrieval.

⚠ **Amended 2026-09-10 — items 2 and 3 were both mis-ranked (note `21-`).**

**Duplication is measured, not predicted.** Alita-G Table 4: the MCP Box grows
26 → 128 across k=1…5 while independent capability families grow only 26 → 65,
so its own effective-coverage ratio falls **1.00 → 0.51**, and accuracy is flat
from k=3 to k=4 while 28 MCPs are added. The paper stops at k=3 for that reason.
This happens at a library size barely larger than this project's current 80.
`DUPLICATE_CAPABILITY` therefore has empirical backing from the closest prior
system, and should be argued from Table 4 rather than from SkillDAG alone.

**Embeddings should be demoted further than item 3 suggests.** Alita-G's
selection is cosine similarity over `description ⊕ use_case`, and it is a live
accuracy variable even at n=74: accuracy swings 76/84/80/76/76/**68** across
τ ∈ [0.65, 0.90] (Table 3), and 84 → 72 across embedding encoders (Table 5).
A 16-point end-task swing from one retrieval hyperparameter, with the library
held constant, is not a scaling caveat — it is an argument that similarity is
the wrong primitive for this decision.

⚠⚠ **Refined 2026-09-10 after the user's brief — the wording above was too
blunt.** Embeddings are not the problem; embeddings *as the admission decision,
with nothing above or below them*, are. The staged form (`23-` §4, and the
repo's own `query_skill_candidates` already works this way for skills):

| Stage | Question | Primitive |
|---|---|---|
| 0 | type-compatible with the gap? | `consumes`/`produces`, effects, trust floor — **exact** |
| 1 | good enough to consider? | quality ladder + provenance — **ordered gate** |
| 2 | most relevant of the admissible? | **embeddings** — ranked, tunable |
| 3 | did the pick conform? | contract / schema / invariant — **fail-closed** |

Inside a typed, quality-floored candidate set a bad threshold costs rank order,
not correctness. Note `24-` adds the hardware reason for the same ordering: this
project runs `all-MiniLM-L6-v2` locally, smaller than any encoder in Alita-G's
Table 5 ablation.

---

## 5. Testing, benchmarking, and conditions for use

### 5.1 Two metric tracks — keep them separate

§2.4's central recommendation. Never report a single number.

**Track A — task performance** (does the system get better?)
- GAIA (Alita-G's benchmark)
- SWE-bench / Polyglot (DGM's)
- The repo's own AutoSci research lifecycle routes

⚠ **"Directly comparable" was too strong (note `21-` §6).** Alita-G runs a
Manager Agent on Claude-Sonnet-4 and a Web Agent on GPT-4.1, with
`text-embedding-3-large` at τ=0.7, under pass@1 / pass@3. Any comparison that
does not match that stack and protocol is not like-for-like, and AI4Research is
a research-lifecycle system rather than a GAIA agent. Say "the benchmark the
closest prior work reports on", and state the configuration gap.

**Track B — capability conformance** (are the artifacts sound?) — *the novel one*
| Metric | Definition |
|---|---|
| **Admission rate** | generated capsules passing the gate, first attempt |
| **Effect-declaration divergence** | statically-observed effects ∖ declared effects |
| **Post-hoc invariant violation rate** | admitted capsules later violating a declared invariant |
| **Schema conformance rate** | outputs validating against own `schema_ref` |
| **Negative-control precision** | rate of *not* selecting on `negative_signals` |
| **Duplication rate** | semantically redundant capsules admitted |
| **Provenance completeness** | admitted capsules with a full generating record |

**The headline experiment the report should propose:** reproduce §2.4's gap
*inside this system*, then show the gate closes it. Concretely — run
self-extension with the conformance gate disabled, measure Track A and Track B;
re-run with it enabled. The expected and interesting result is **Track A roughly
flat, Track B sharply improved**. That is a publishable shape, and it directly
answers "why bother with capsules".

### 5.2 Evaluation horizons (survey §2.6's three paradigms)

1. **Static** — a fixed corpus of capability gaps; measure generated-capsule quality.
2. **Short-horizon adaptive** — perturbed task variants; does self-extension
   generalize or overfit to the trajectory that produced it?
3. **Long-horizon lifelong** — N sequential tasks; watch for **capability-library
   rot**: duplication growth, selection degradation, and *catastrophic
   forgetting* of skills displaced by newer near-duplicates.

Long-horizon is the one everyone skips and where the interesting failures live.

⚠ **Partly already observed.** Alita-G's Table 4 is a short-horizon instance of
exactly this: duplication growth and saturation within five iterations. Use its
effective-coverage ratio (#clusters / #MCPs) as a ready-made Track B metric with
a published baseline to compare against — 1.00 → 0.51 over 26 → 128 tools. Also
note Alita-G reports Right→Wrong regressions of 1/1/0 (Table 6): **do not claim
self-extension is regression-free.**

### 5.3 Testing the machinery itself

- **Unit** — each new rejection reason, with a crafted violating capsule per reason.
- **Negative controls** — extend `capability_activation_proof.py`, which already
  does this for activation.
- **Adversarial** — a red-team suite of capsules that *try* to pass the gate
  while under-declaring effects. This is the analogue of the adversarial review
  in `13-…`, and the most valuable test asset.
- **Golden corpus** — freeze N generated capsules as regression fixtures.
- **Determinism** — same gap + same seed ⇒ same admission verdict. The gate
  must be deterministic even though the generator is not. **Non-negotiable:
  the whole architecture rests on `CLAUDE.md`'s "LLMs interpret semantics;
  deterministic code validates structure."**

### 5.4 Conditions for use — the safety envelope

Self-extension is `effect_escalation_requires_human` territory. Proposed gates:

| Condition | Rule |
|---|---|
| **Effect ceiling** | A generated capsule's effects **MUST NOT** exceed the authorizing task's envelope. Escalation ⇒ human approval (the ADR reason already exists). |
| **Default status** | Newly admitted capsules enter as `status: draft`, never `stable`. Promotion requires observed successful invocations — ties directly to note 13 R6. |
| **Network/write quarantine** | First N invocations run `dry_run_only`; the repo already has this side-effect policy (8 of 28 routes use it). |
| **No self-modification of the gate** | A generated capsule **MUST NOT** be able to alter admission, the registry, or the gate itself. Encode as a permanent `incompatible_with` / forbidden effect. **This is the one hard safety invariant.** ⚠ *See the correction below — the DGM contrast as originally written was overstated.* |
| **Provenance mandatory** | Record generating model, prompt, trajectory, and parent task. Without it, incident analysis is impossible. |
| **Rollback** | Every admission reversible; the phase22 file already notes end-to-end version rollback "was not found" (note 13 Q5) — this makes it a requirement, not a nicety. |
| **Rate limiting** | Cap capsules generated per task/session — reuse `capsule-cooldown.json`. |

⚠⚠ **Corrected 2026-09-10 after reading DGM properly — see `28-` §6.1.** The
original text here claimed the immutable referee distinguishes this proposal
from DGM. **It does not, and the claim would not survive a supervisor who knows
the paper** [verified against `2505.22954.txt`]:

- DGM **already freezes its meta-loop** — line 295: *"the open-ended exploration
  process (i.e., archive maintenance, parent selection) is fixed and not
  modifiable by the DGM, which we leave as an avenue for future work."*
- DGM **explicitly proposes the immutable referee** — line 642: *"an option
  worth exploring is to create an unmodifiable part of the system to be able to
  evaluate at halt the rest."*

The immutable referee is therefore **not this project's invention**. The
honest, and stronger, framing:

> Every self-improving system freezes something. DGM freezes archive
> maintenance and parent selection, and names an unmodifiable evaluator as
> future work. The open question is not *whether* to freeze a referee but
> **what the referee should check.** Our answer: declared effects, contracts and
> typed artifacts, checked mechanically, before admission.

That relocates the contribution from "we have a referee" to "we specify what it
inspects" — true, defensible, and more interesting. The rule itself stands
unchanged; only the novelty claim around it was wrong.

---

## 6. Recommended reading order

1. **2604.00392** — verification-vs-conformance gap *(the justification)*
2. **2510.23601** — Alita-G *(the closest existing system)*
3. **2606.03056** — SkillDAG *(the scaling problem you will hit)*
4. **2507.21046** — self-evolving agents survey *(the vocabulary)*
5. **2604.01687** — CoEvoSkills *(evidence self-built beats hand-built)*
6. **2505.22954** — Darwin Gödel Machine *(the "AI builds AI" reference point)*
7. **2505.20286** — Alita *(original MCP-generation formulation)*

---

## 7. Open questions for the supervisor

1. **What does "the DeepSeek harness" mean?** (`16-…` §4 — provider vs separate
   system. Blocks the integration interface.)
2. **Is Alita-G known to the team?** If the goal is to reproduce it, say so and
   scope accordingly. If to go beyond it, the conformance layer (§3) is the way,
   and the project should be framed that way from the start.
3. **Research contribution or internal capability?** Determines whether Track B
   metrics (§5.1) need to be publishable or merely operational.
4. **Is unbounded capability growth in scope?** Or a fixed capability budget per
   domain, à la Alita-G's curated MCP Box?
5. **Who owns the effect ceiling?** Effect escalation needs a human; at what
   granularity — per capsule, per task, per session?


---

## 8. Reading triage

**Tier 1 — must read (4).** These four carry the argument. Everything the
report needs to *claim* comes from 1 and 2; everything it needs to *survive
questions about* comes from 3 and 4.

| arXiv | Title | Why it's tier 1 |
|---|---|---|
| **2604.00392** | Beyond Task Completion: A Verification-vs.-Conformance Gap in Tool-Evolving Agents | The empirical justification for the whole project. Short, and every section is usable. |
| **2510.23601** | Alita-G: Self-Evolving Generative Agent for Agent Generation | The closest existing system to the proposal. Not knowing this in the meeting is the main risk. |
| **2507.21046** | A Survey of Self-Evolving Agents | **Force multiplier** — its taxonomy structures the report *and* it covers Voyager, CREATOR, ToolGen, ADAS, AFlow, AgentSquare, so those drop to cite-only. |
| **2606.03056** | SkillDAG: Self-Evolving Typed Skill Graphs for LLM Skill Selection at Scale | The scaling failure self-generation causes, and the closest external work to capsule typed composition. |

**Tier 2 — skim, or have open during the meeting (3).** Read abstract +
results; you need the headline numbers, not the method.

| arXiv | Title | The one thing to take |
|---|---|---|
| **2505.22954** | Darwin Godel Machine | The canonical "AI builds AI" citation. SWE-bench 14.2 → 30.7%; concedes provable self-improvement is impractical — which is the opening for a conformance layer. |
| **2604.01687** | CoEvoSkills | Self-evolved skills **beat human-curated** ones, and are portable across model families. The empirical argument *for* the direction. |
| **2504.07079** | SkillWeaver | Practice-then-distil loop; strong-agent APIs lift weak agents up to +54.3%. Useful if capability transfer comes up. |

**Tier 3 — cite-only.** Do not read now. The survey covers all of them, and
they are background the audience already assumes. Have the IDs to hand so a
reference can be produced on demand: 2505.20286 (Alita — superseded by
Alita-G), 2305.16291 (Voyager), 2305.14318 (CREATOR), 2305.17126 (LLMs as Tool
Makers), 2309.17428 (CRAFT), 2401.12869 (TroVE), 2601.11100 (ReCreate),
2408.08435 (ADAS), 2410.06153 (AgentSquare), 2410.10762 (AFlow), 2302.04761
(Toolformer), 2305.15334 (Gorilla), 2307.16789 (ToolLLM), 2410.03439 (ToolGen),
2608.25512 (Cordis — read only if dsh internals become load-bearing).

---

## 9. Verified arXiv IDs

**All IDs below were verified against the arXiv API on 2026-09-10** by
retrieving each entry's actual title. The earlier ✅/⚠ split in this note is
superseded by this table — every ID here is confirmed.

One correction the verification caught: `2604.01687` is **CoEvoSkills**, not
"EvoSkills" as secondary sources render it.

### Read in this order

| # | arXiv | Title | Why |
|---|---|---|---|
| 1 | **2604.00392** | Beyond Task Completion: A Verification-vs.-Conformance Gap in Tool-Evolving Agents | **The justification.** Agents build tools that pass tasks and violate their own specs |
| 2 | **2510.23601** | Alita-G: Self-Evolving Generative Agent for Agent Generation | **The closest existing system.** Trajectory → MCP → abstraction → "MCP Box" |
| 3 | **2606.03056** | SkillDAG: Self-Evolving Typed Skill Graphs for LLM Skill Selection at Scale | The scaling problem self-generation creates |
| 4 | **2507.21046** | A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve… | The field's vocabulary and taxonomy |
| 5 | **2604.01687** | CoEvoSkills: Self-Evolving Agent Skills via Co-Evolutionary Verification | Self-built skills beat human-curated; portable across model families |
| 6 | **2505.22954** | Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents | The "AI builds AI" reference point. SWE-bench 14.2 → 30.7% |
| 7 | **2505.20286** | Alita: Generalist Agent Enabling Scalable Agentic Reasoning with Minimal Predefinition and Maximal Self-Evolution | Original MCP-generation formulation |

### Tool creation

| arXiv | Title |
|---|---|
| **2305.16291** | Voyager: An Open-Ended Embodied Agent with Large Language Models |
| **2305.14318** | CREATOR: Tool Creation for Disentangling Abstract and Concrete Reasoning of Large Language Models |
| **2305.17126** | Large Language Models as Tool Makers |
| **2309.17428** | CRAFT: Customizing LLMs by Creating and Retrieving from Specialized Toolsets |
| **2401.12869** | TroVE: Inducing Verifiable and Efficient Toolboxes for Solving Programmatic Tasks |
| **2504.07079** | SkillWeaver: Web Agents can Self-Improve by Discovering and Honing Skills |
| **2601.11100** | ReCreate: Reasoning and Creating Domain Agents Driven by Experience |

### Agents designing agents

| arXiv | Title |
|---|---|
| **2408.08435** | Automated Design of Agentic Systems |
| **2410.06153** | AgentSquare: Automatic LLM Agent Search in Modular Design Space |
| **2410.10762** | AFlow: Automating Agentic Workflow Generation |

### Tool use / retrieval background

| arXiv | Title |
|---|---|
| **2302.04761** | Toolformer: Language Models Can Teach Themselves to Use Tools |
| **2305.15334** | Gorilla: Large Language Model Connected with Massive APIs |
| **2307.16789** | ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs |
| **2410.03439** | ToolGen: Unified Tool Retrieval and Calling via Generation |

### ⭐ Added 2026-09-10 — capability economics (note `33-`)

Both verified against their arXiv abstract pages on 2026-09-10.

| arXiv | Title | Tier |
|---|---|---|
| **2607.23332** | **AllocBench: Measuring Online Tool Allocation Capability in LLM Agents** (Wang & Xu, Jul 2026) — creating a tool is an investment under a fixed budget; frontier models allocate near-optimally in the abstract and **fail to transfer it to script-writing**. ⚠ *AllocBench*, not "AlloBench" | **1** |
| **2511.02734** | CostBench: Evaluating Multi-Turn Cost-Optimal Planning and Adaptation… (Liu et al., Nov 2025, rev. Jun 2026) — cost-centric benchmark; agents miss cost-optimal plans, ~40% drop under dynamic conditions | 2 |

### Context

| arXiv | Title |
|---|---|
| **2608.25512** | A Programming Paradigm for Spatiotemporal Composability — the Cordis paper underlying the DeepSeek Harness |

Curated tracking list: `github.com/XMUDeepLIT/Awesome-Self-Evolving-Agents`
