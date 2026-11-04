# Capability Capsules — report outline

**Deliverable 2, standalone.** Does not merge with the general-workflow panel's
`report/VARIANT-*`. Written 2026-09-10 by the capability-capsule panel (pts/9).

- **Reader:** the supervisor — knows the system deeply, will check numbers, will
  probe the status claim first and the novelty claim second. **Second audience
  (`26-` Q27):** whoever administers the server this would run on. They have
  different standards, and §5c is written for them.
- **Purpose, in the user's words:** *better understanding of the subject.* An
  explanatory and positioning document, not a status memo.
- ⚠ **Register — decided 2026-09-11.** This bullet and the next used to pull
  against each other: "better understanding" invites a survey, "design proposal"
  demands a position. **The position wins, and it is how the understanding gets
  delivered** — a reader learns more from one argued claim they can push against
  than from a neutral tour of nine papers. So:
  - **Opinionated about the *what*.** Verification is required before a
    self-authored capability is usable. Three papers, three levels, stated flat.
  - **Informational about the *how*.** Mechanism, thresholds, whether a capsule
    is a seam — all marked proposed, never asserted.
  - **Every fact earns its place by supporting a design claim.** Background that
    does not load-bear belongs in an appendix or in the
    `who-checks-the-tools` artifact, which is already the informational
    deliverable. The report must not duplicate it.
  - The test for any paragraph: *could a competent stranger with the same nine
    PDFs have written this?* If yes, it is survey material and probably belongs
    elsewhere. The synthesis is the part that is ours.
  - ⚠ The failure mode to guard: confidence leaking across that line. Both
    claims corrected this session — "the immutable referee is ours" and the
    fabricated failure modes — were opinions wearing evidence's clothes.
- ⚠ **Centre of gravity, per the user 2026-09-10:** *"you don't really have to
  reference back to AI4Research as much… the most important thing is our goal
  and not what code we currently have."* This is a **design proposal grounded in
  the literature**, not a system report. Verified repo facts appear where they
  *support a design claim* — never as a tour of the codebase. Part I is
  deliberately short; the argument is Part II.
- ⚠ **PENDING, raised by the user 2026-09-11 while drafting §1 — not yet
  decided.** §1 (why capsules should exist) and §6 (prior art) overlap heavily,
  because the research does not merely motivate the design, it *shapes* it. The
  user's framing: *"a lot of these traits can be inferred but a person couldn't
  say it's a real problem until they see paper contents."* The complaints in §1
  are reachable a priori and therefore persuade nobody on their own; they only
  become load-bearing once measured. Currently §1 and §6 sit ~5,000 words apart,
  so the reader carries an unevidenced claim across half the report.
  **Proposed fix** — split §1 by epistemic status rather than moving §6:
  **§1a** the a priori complaints, explicitly labelled as prediction; **§1b** one
  paragraph discharging them (222 tools, 215 at zero on held-out conformance).
  §6 keeps the *comparative* work and loses only the reveal. The 20-min talk
  already orders it this way — evidence before proposal — and that ordering was
  forced by the slot rather than chosen, which is mild evidence it is right.
  **Settle this against the user's actual §1 draft, not in the abstract.**
- **Format:** written report, no deck (B7). Structured so a deck can be **cut
  from it** later for the supervisor + co-op students, without rewriting.
- **Target length:** ~9,000–12,000 words. ⚠ **Rebalanced:** §§1–3 compress to
  ~2,000 words total (was ~3,500); the inventory numbers, reconciliation table
  and route breakdown move to appendices. §§5b–8 carry the weight.
- **Provenance:** every claim marked `[verified]` or `[repo-claim]`, with file
  paths and line numbers.

---

## The spine

> **Alita-G shows an agent can build its own capability library and measurably
> improve — 83.03% pass@1 on GAIA, at ~15% lower token cost. It curates that
> library on one signal: did the task succeed. 2604.00392 replayed 222 tools
> admitted by that class of rule against held-out suites for their own
> capabilities: **96.8% scored zero correctness**, while executing cleanly and
> raising no in-session flag. A capability capsule is the missing filter: the
> conformance contract that decides whether a self-built capability may enter
> the library, and which one is selected at run time.**

⚠ **Use the number, not the paraphrase** (`29-`). "Tools violate their own
specifications" was our summary's wording, not the paper's. Its own term —
**silent rot** — is more precise and far more forceful.

Opening line of the document (shorter, lands first):

> *A capability capsule is a contract that decides whether a capability is
> allowed to run. That mattered when humans wrote the capabilities. It becomes
> load-bearing when the system starts writing them itself.*

**Three claims the whole report defends**, each citable:

1. Prior work's curation signal is task outcome. *(Alita-G Eq. 5)*
2. Prior work's fix for artifact quality is unverified LLM rewriting.
   *(Alita-G §3.3, Eq. 6)*
3. Capability-library duplication is an observed failure, not a hypothetical.
   *(Alita-G Table 4: effective coverage 1.00 → 0.51)*

**And one structural claim that inverts Alita-G's thesis** (`25-`) — this is the
report's strongest theoretical move and should be visible in the abstract:

> Alita-G treats generalist → specialist as a **terminal transformation**. That
> is sound because its task distribution is fixed by construction. A research
> system running unattended for a week has no such guarantee: a failure or a
> discovery moves the distribution mid-run. **Specialisation is therefore a
> reversible state, not a destination** — which is precisely why capability
> belongs in a library of declared, admissible, retirable contracts rather than
> in the agent.

---

## Part I — What exists  *(~2,000 w total — keep it tight)*

Part I earns its place only by making Part II legible. Everything here is in
service of one thing: the reader needs to know what a capsule *is* before the
argument about what it should become can land. Resist the tour.

### §1. The problem capsules were built for  *(~800 w)*
The five epistemic complaints from `11-` §1 — **accurate renderings only**,
never note `07-`'s embellished ones (`14-` A-4). Land the framing explicitly:
every row is an epistemic complaint. The objection is not that skills don't
work; it's that you cannot know anything about them in advance.

### §2. What a capsule is today  *(~900 w — halved)*
- `Capsule = Specification + Implementation + Verification`, then SCARE, with
  the observation that every property is "*-able*" — a claim about what you can
  **check**, not about what the capsule does.
- One real manifest, `cap.research-literature-discover.yaml`: `contract`,
  `effects`, `verification`. One invariant quoted in full — *"Missing protocol
  parameters remain explicitly unresolved rather than being silently
  invented."*
- The runtime admission gate and its five fail-closed reasons, implemented
  **and tested** (`capability_capsules.py:1317-1379`;
  `tests/harness/test_capability_capsules.py:164,223`).
- **The contract doing real work** — new, from `22-`: the artifact registry's
  `minimum_execution_trust` schema enum is what makes the unguarded index at
  `capsule_composition.py:106` safe. A small, concrete example that these are
  enforced contracts and not documentation.
- ⚠ **Numbers move to Appendix A.** Keep exactly two in the body, because each
  does argumentative work: **80 registered capsules** (the library size the
  scaling argument is calibrated against) and the **76-entry artifact-type
  registry** (the typing that makes stage-0 selection possible). The rest —
  77/1/2, 74 stable / 6 draft, 0 dangling, 45 logical / 102 physical, the 52/50
  provider-neutral split — are inventory, not argument.

### §3. Honest status  *(~500 w — one page, then move on)*
Release candidate; schema is `draft`; 28 AutoSci routes — 17 partial, 11 gated,
0 full — with `gated` explained as a **policy** state in the same breath
(16 of 28 are `approval_required`; the gated ones are the destructive ones).

The corrected E2E status, `STATUS-CORRECTED.md`'s wording, now independently
verified by this panel at `pre-scheduler-stabilization-log-20260829.md:863`:
a complete 15-node run on 2026-09-03 with all required gates passed, which
required a mid-run fix and coordinator reload, against a pre-release regression
of `606 passed / 34 failed / 8 skipped` whose failures were deliberately
retained as itemised known debt.

Being first to state the limitation is what buys credibility for §§6–8. ⚠ Under
the new framing this is a **credibility deposit, not a status report** — state
it once, plainly, in a paragraph, and do not return to it. The route breakdown
detail goes to Appendix A.

### §4. Three acquisition channels, one admission record  *(~1,400 w)*
Skills, MCP, A2A. The layering table (`16-` §4) — MCP answers *how do I reach
a tool*, A2A *how do I delegate to a peer*, the plugin seam *can I replace this
without touching consumers*, the capsule *may I run this, and what will it do
to me*. Then the three convergences (`16-` §3) as evidence the abstraction is
real rather than rhetorical.

**⚠ Reframed after the user's brief (`23-` §3).** Lead with what the A2A hop
*actually is here today* — not a protocol comparison but a verified fact:
`skills/a2a-hub/SKILL.md` is a **third-party skill** (v1.3.0, external owner)
pointing at MoltBot's **public relay** at `a2a-hub.fly.dev`, reached with a
remote API key, selecting peers from agent cards whose skill list is free-text
description and tags. No effect declaration, no contract, no artifact typing,
no trust class, no local record of what the peer did.

> Today the boundary between our generalist and a specialist is an opaque remote
> relay we do not control, selected on free-text tags. A capability capsule
> turns that boundary into a locally-admitted contract with declared effects,
> typed inputs and outputs, and a trust class.

That is a far stronger claim than "capsules are a nicer A2A", and it is
checkable. Keep the honest limit attached: where the peer really is remote and
opaque, the capsule constrains the *boundary* and can never statically verify
the peer, so such capsules cap at `evidence_transform` and require approval.

### §5. Where this sits in the harness  *(~1,000 w)*  ⚠ **still gated on B2**
dsh as "everything is a plugin": the seam is the socket, the capsule is the
contract. Cordis makes effects **reversible**; capsules make them
**reviewable**; and reversal is observational, not physical — retiring a capsule
un-registers it and does **not** un-publish the evidence it produced
(`20-` §7.4).

**⚠ This section is now load-bearing rather than contextual (`25-` §4).** Under
the reversibility argument, Cordis stops being background colour: an evolution
step that is reversible can be taken speculatively, because it can be withdrawn
when the distribution moves; an irreversible one must be right in advance, which
for a non-stationary distribution nobody can guarantee. Hence the decision rule:
**prefer the most reversible mechanism that achieves the improvement.** And the
caveat stays attached — reversal is observational, so retiring a bad capsule
does not retract the evidence it produced. *That is an argument for strict
admission, not for sufficient retirement* — the thesis, reached from a second
direction.

*Open dependency (B2):* must capsule generation emit all three seam roles
(Service Definition / Provider / Consumer)?

### §5b. Generalist and specialist  *(~1,800 w)*  **NEW — the architecture**
The section that makes this a design document rather than a survey. Source:
`23-`, `25-`.

- **The structural gap in Alita-G**: master and specialist are different
  *phases*, not co-resident *roles*. The master builds the Box offline; the
  specialist runs at inference with it frozen. Nothing routes between them at
  run time. Fine for a benchmark harness; it does not survive a long-running
  system. **The routing question is not a detail they left out — it is the
  question their architecture never has to answer and ours does.**
- **Why the generalist is permanent**: specialisation is a bet that the task
  distribution will not move; week-long autonomy is the case where that bet is
  guaranteed to lose.
- **The trap, named explicitly**: the generalist is only invoked when the
  specialist path found nothing, so training it on observed traffic optimises
  it against the wrong sample. **Specialising the recovery path destroys the
  recovery path.** Its floor matters more than its ceiling.
- **What evolves, then**: the capability library (primary, reversible), context
  and memory (secondary, reversible), *not* generalist weights, and **never the
  referee**. → *The actor may improve. The referee may not.* Contrast DGM, where
  improvement and irreversibility arrive together.
- **Routing**: plan-time acquisition, run-time recovery. The generalist may
  reopen the contract; it may never reinterpret it — the exact principle
  `STATUS-CORRECTED.md` extracted from the `final_report` deadlock. The system
  already learned this lesson once, expensively; reuse it.
- **Cold start**: a long-running system inherits whatever the last run left.
  Alita-G has no cold-start problem because its Box is built against the target
  domain in advance. This is what makes provenance scoping and the `19-`
  lifecycle load-bearing rather than tidy.

### §5c. Where this runs, and what that makes the gate  *(~1,600 w)*  **NEW**
Source: `26-`. **This is the motivation for the two gates and must come before
them.** It is also the section that survives contact with someone who has to
approve running this on a shared machine.

- **Two deployment modes, one system.** Interactive workstation (a human is
  present to approve) and multi-day autonomous server (nobody is). **The
  admission gate exists for the second.** Models are API-based, so local compute
  is not the binding constraint — egress and cost are.
- **The sentence the section is built around:**
  > On a single-user workstation, "what will this capability do to me" is a
  > hygiene question. On a shared server running unattended for days, holding
  > API credentials with network egress, it is an **access-control** question.
- **Why this workload class is genuinely new**: every other server workload runs
  code a human wrote and someone reviewed. This one writes code, admits it, and
  runs it, with no human between those steps. Ordinary server security has no
  story for that. Lead with this.
- **The threat model** — seven threats, tabulated (`26-` §4). Give **T5 (prompt
  injection through retrieved content)** its own paragraph: a system that reads
  untrusted documents to decide what capability to build has an injection
  surface no benchmark measures, and it is the reason **the referee must be
  mechanical, not model-driven**. Determinism in the gate is a *security*
  property, not just a reproducibility one.
- **The honest limit, stated before anyone asks**: a capsule is **admission, not
  containment**. Admission decides whether a capability is allowed to run;
  containment limits what it can do regardless. Admission without containment is
  a system that trusts its own analysis.
  > The admission contract is necessary and not sufficient. It is what makes
  > containment tractable — **declared effects are what turn a sandbox from a
  > guess into a policy.**
- **Positioning, checkable and modest**: the self-evolving-agents survey names
  automated verification *and* sandboxing as the field's open safety problems.
  This design addresses one and specifies the other. That is a better claim than
  novelty.

---

## Part II — What it becomes

### §6. Prior art, and what is actually ours  *(~1,600 w)*
Name Alita-G first and plainly — the worst outcome is a supervisor who knows it
and a presenter who doesn't. Then the four findings from `21-`:

1. Curation filter is task outcome (Eq. 5) — the mechanism, not an inference.
2. ⚠ **Corrected 2026-09-11** — this row previously read "Alita-G targets
   hidden dependencies, interface violations and spec drift". Those terms occur
   **zero** times in 2510.23601; it was the withdrawn `29-` §5.1 vocabulary
   re-attributed to Alita-G. Alita-G's §3.3 abstraction names four
   transformations — Parameter Generalization, Context Removal, Interface
   Standardization, Documentation Enhancement — and performs all four with a
   single unverified LLM rewrite (Eq. 6). **The contrast: they prompt for it,
   we check for it.** Fair to them, and it locates the contribution precisely.
3. Duplication growth is measured (Table 4), at a library size barely larger
   than this project's 80.
4. Selection is fragile flat retrieval — 16-point swing across τ, 12 across
   encoders, library held constant.
5. ⚠ **No library management, and it is a stated refusal** (`27-`) — the
   strongest single piece of evidence in the report. `retire`, `deprecat`,
   `version`, `dedup`, `prune`, `evict`, `delete`, `remove`, `adversarial`:
   **zero occurrences**, and the one `lifecycle` hit is in their own related-work
   section crediting another system. §3.3 verbatim: *"Unlike traditional
   clustering approaches, our method preserves the diversity of MCP
   implementations to maximize coverage of potential task variations."* And
   Eq. 7 gives `M = |L|` — **Eq. 7 specifies no filter.** ⚠ Not "no filter exists": the prose names one twice and defines it nowhere (`27-`).
6. ⚠ **There is no per-tool quality measure at all** — not even tool
   correctness. Eq. 5's predicate is task-level and binary, so every MCP from a
   successful trajectory is kept, including ones never called or actively
   unhelpful.
7. ⚠ **They built the dedupe test and used it as a thermometer.** §5.2 computes
   connected components over the ≥0.7-similarity graph — that *is* a dedupe
   procedure — and uses it only to explain the plateau. **Their remedy for
   library rot is to stop generating at k=3.**

Close this list with the fairness note (`27-` §6), so it reads as literate
rather than point-scoring: for a fixed benchmark suite the choice is
proportionate, the paper is candid about the plateau, and the results stand.
**Alita-G proves the loop is worth building, and shows exactly where it stops
scaling. We propose to keep going.**

Then the surrounding landscape at citation depth: the survey taxonomy
(2507.21046) with this project placed in it explicitly; DGM (2505.22954) as the
"AI builds AI" reference point that concedes provable self-improvement is
impractical; CoEvoSkills (2604.01687) as the argument *for* the direction;
SkillDAG (2606.03056) as the independent statement of the scaling problem.

Close on the distinction: **prior work curates for usefulness; capsules curate
for admissibility.**

### §7. The two gates — the contribution  *(~2,200 w)*
The section note `17-` conflates and this report separates.

**7a. Admission-time conformance.** The eight proposed rejection reasons
(`17-` §4.3), with `EFFECT_UNDECLARED` as the highest-value and most defensible:
compare the declared effect set against the statically-observed effect set of
the generated implementation, and fail closed on divergence. A mechanical,
testable answer to the gap between what a capability declares and what it
actually does. `DUPLICATE_CAPABILITY` argued from
Alita-G Table 4. `NEGATIVE_CONTROL_FAILED` reuses `capability_activation_proof.py`,
which already runs negative controls.

**7b. Selection-time conformance** — *the user's actual emphasis.* Present it
as the **four-stage model** (`23-` §4), not as "typed matching instead of
embeddings":

| Stage | Question | Primitive | Must be |
|---|---|---|---|
| 0 | type-compatible with the gap? | `consumes`/`produces` over 76 artifact types, effect ceiling, trust floor | exact |
| 1 | good enough to consider? | quality ladder + provenance rank | ordered gate |
| 2 | most relevant of the admissible? | **embeddings** | ranked, tunable |
| 3 | did the pick conform? | contract / schema / invariant | fail-closed |

Two things make this land:

- **The repo already does this for skills** [verified].
  `skill_capsule_bridge.py` has a five-level quality ladder
  (`broken`→`effective`), a provenance ordering (`SOURCE_RANK`), and
  `query_skill_candidates` applies a **hard `min_level` floor before any
  scoring**, then ranks. Alita-G is single-stage: one cosine threshold, no
  quality floor, no provenance ordering. **The hierarchical structure exists;
  it has simply never been pointed at capsules.** This also answers "how do we
  quantify whether a capability is good enough" with something already built.
- **Local hardware forces the same ordering** (`24-`). Alita-G's 83.03% rests on
  hosted `text-embedding-3-large`; its Table 5 shows 12 points lost to
  open-source encoders. This project runs `all-MiniLM-L6-v2` with Chroma,
  locally — smaller than anything it ablated. On this hardware similarity is the
  *weakest* signal available, so it cannot carry the admission decision; inside a
  typed, floored candidate set a bad threshold costs rank order, not correctness.

Two independent arguments — architectural and hardware — converging on the same
stage ordering. Say that they converge.

**7c. The manifest-first inversion**, which makes both gates possible: write the
capsule manifest *first* and generate the implementation against it. The
manifest **is** the understanding step — if the agent cannot write the contract,
it has not understood the capability. Spec-after-the-fact, which is Alita-G's
order, is exactly the pattern 2604.00392 measures failing.

**7d. The self-extension loop** (`17-` §4.1), with stages 0, 7 and part of 8
marked as already built. The pitch is *close the loop*, not *build a new thing*
— more accurate and more achievable.

**7e. The cost asymmetry that makes this affordable** (`24-` §3):
**admission is expensive and rare; selection is cheap and constant.**
Conformance checking runs once per candidate, off the critical path, and a
capsule sits in `draft` until it passes. Alita-G has the opposite shape — cheap
curation, all the weight on per-task selection. We move cost from the hot path
to the cold path, and off the accelerator. For a workstation running a week-long
job, cold-path compute is substantial and currently idle.

**7f. One named inconsistency, honestly** (`22-`): trust is a monotone rank at
the planner and an exact string match at operator binding, so a
`measured_execution` operator does not satisfy a capsule requiring
`evidence_transform`. Small, concrete, tractable — and a good instance of the
report's theme that the contract vocabulary is real but not yet uniform across
the layers that consume it.

### §8. Evaluation  *(~1,400 w)*
Two tracks, never one number — 2604.00392's central recommendation.

- **Track A — task performance.** GAIA (with the comparability caveat from
  `21-` §6: their stack is Claude-Sonnet-4 + GPT-4.1, τ=0.7, pass@1/pass@3),
  SWE-bench, and the repo's own AutoSci routes.
- **Track B — capability conformance.** Admission rate, effect-declaration
  divergence, post-hoc invariant violation, schema conformance, negative-control
  precision, duplication rate, provenance completeness. **Plus** Alita-G's
  effective-coverage ratio (#clusters / #MCPs), which comes with a published
  baseline to compare against: 1.00 → 0.51 over 26 → 128 tools.
- **⭐ Track B has a built-in control group — the 79 existing capsules.**
  Measured 2026-09-11 `[verified]`, across both manifest directories:

  | Field | Populated |
  |---|---|
  | `contract`, `effects`, `verification`, `provenance`, `applicability` | **79 / 79** |
  | `invariants`, `preconditions`, `postconditions` | **79 / 79** |
  | `negative_signals` | **79 / 79** |
  | `composition.consumes` / `produces` (typed) | **79 / 79** |

  These are **human-authored** capsules — largely AutoSci skills carrying
  contracts — so they are the hand-written reference set, and the conformance
  experiment gets a baseline for free: *human-written scores X on these suites,
  generated scores Y, same suites.*

  **Why this matters more than it looks.** 2604.00392's 96.8% is credible only
  because hand-written reference implementations score **C=1.00 on all sixteen
  suites** — without that control, "96.8% failed" could be an artifact of a harsh
  test rather than a real defect. Anyone else proposing this experiment has to
  *build* the control group first. This project already has one, fully
  contracted. State it in §8; it is a genuine methodological advantage and it
  costs nothing to claim.

  ⚠ **Honest limit.** "Populated" means the key exists and is non-empty. Whether
  each invariant is *substantive* rather than vacuous is **unmeasured**. The
  claim is that the contract surface is complete, not that every contract is
  strong. Do not upgrade this to "79 verified capsules".

  ⚠ Consequence for `NEGATIVE_CONTROL_FAILED` (§7a): 79/79 declare
  `negative_signals`, so negative controls are runnable against the existing
  library **today**, not only against future generated capsules.
- **⚠ Track C — generality retention** (`25-` §6). **New, and nobody in the
  literature reports it.** Generalist success on a held-out, deliberately
  off-distribution task set, measured periodically over a long run; plus
  escalation rate over time, recovery success rate, library churn, and
  time-to-first-admissible on a novel gap. The first is the one that matters and
  it is cheap — but it is **only measurable if a task set is deliberately kept
  out of capability acquisition**. Note this is the opposite discipline to
  Alita-G's, which harvests from the set it reports on (`21-` §6); frame it as a
  concrete methodological improvement, not a criticism.

**The headline experiment, stated as a pre-registered prediction:** run
self-extension with the conformance gate off, measure both tracks; re-run with
it on. Predicted shape — **Track A roughly flat, Track B sharply improved.**
Stating the prediction in advance is more persuasive than a post-hoc chart and
survives the result coming out differently. **Proposed, not run** — both repos
are read-only, so the report says "the experiment we will run".

Then the three horizons (static → short-horizon adaptive → long-horizon
lifelong), noting the third is where the interesting failures live and the one
everyone skips — and that Alita-G's Table 4 is already a short-horizon instance
of it. Do not claim self-extension is regression-free; Alita-G reports
Right→Wrong flips of 1/1/0.

Close by showing off the evaluation discipline the team already has
(`research/07-benchmarks-evaluation.md`): the six-state result enum with its
anti-copy rule, the three-layer test strategy, the explicit authority ranking of
evidence sources. A vocabulary that distinguishes "not tested" and "environment
blocked" from "fail" is exactly what conformance measurement needs, and most
teams don't have it.

### §9. Safety envelope  *(~900 w)*
Bounded self-extension with an **immutable referee**: a generated capsule may
never modify the admission gate, the registry, or the verifier.

⚠ **Do not claim the immutable referee as our contribution** (`28-` §6.1). DGM
already freezes its archive maintenance and parent selection, and explicitly
proposes *"an unmodifiable part of the system to be able to evaluate at halt the
rest"* as future work. The defensible framing:

> Every self-improving system freezes something. The open question is not
> *whether* to freeze a referee but **what the referee should check** — and our
> answer is declared effects, contracts and typed artifacts, checked
> mechanically, before admission.

The narrower DGM contrast that does survive: there, **improvement and
irreversibility arrive together**; here they are deliberately separated.

Paired with: new capsules enter `draft`, never `stable`; first N invocations
`dry_run_only` (the policy exists — 8 of 28 routes use it); effect ceiling
inherited from the authorizing task; provenance mandatory; rollback required;
generation rate-limited via `capsule-cooldown.json`.

### §10. Open questions  *(~500 w)*
Ending on questions fits the roadmap framing and invites the supervisor in.

Grouped, because there are now fifteen and a flat list would read as
indecision. Each group is a decision the supervisor can actually make.

**Architecture** — *who does what*
1. Who is the master agent: a distinct resident generalist, the existing Elastic
   Planner, or one model under a different profile? *(Q7)*
2. Plan-time routing or run-time escalation — and if run-time, what confidence
   floor, calibrated how, without reintroducing Alita-G's threshold fragility?
   *(Q8)*
3. Does capsule→dsh integration target the seam roles directly — must generation
   emit all three? *(B2; gates §5)*

**Evolution** — *what is allowed to change*
4. Is the generalist ever allowed to change — context and memory only, or
   eventually weights? *(Q13)*
5. What task set is deliberately held out, so generality retention is measurable
   at all? *(Q14)*
6. Who arbitrates when specialist and generalist can both serve a task? *(Q15)*
7. When does a capability get retired? *(Q16)*

**Library** — *how it stays healthy*
8. What is the quality ladder for capsules — reuse `skill_capsule_bridge`'s five
   levels, or define a capsule-specific one, and what observations feed it given
   `13-` R6? *(Q9)*
9. Cold start: does a capsule harvested in one domain stay admissible in
   another, and does provenance decay? *(Q10)*
10. May the library grow *during* a run, or only between runs? Mid-run growth
    conflicts with the freeze contract. *(Q11)*
11. Unbounded growth, or a fixed budget per domain à la Alita-G's curated Box?

**Deployment and security** — *the group with a second audience* (`26-` §8)
12. Which mode is the design target — interactive workstation, autonomous
    server, or both with different admission policies? *(Q22; recommendation:
    both, strict by default, relaxable only interactively)*
13. Who owns the API credentials and what is their scope — per-run, per-user, or
    a shared service identity? Decides how bad T1 is. *(Q23)*
14. What egress is permitted by default? Deny-by-default with declared
    allowances is the only policy that matches the effect vocabulary; anything
    else makes `network` declarations advisory. *(Q24)*
15. Is the run multi-tenant? If so T6 is primary and provenance scoping becomes
    mandatory. *(Q25)*
16. **Does the sandbox get built?** If not, the report must say plainly that
    admission is the only control and what that leaves open. *(Q26)*

**Envelope** — *what the machine can afford* (`24-` §5, now conditional)
17. What is the cold-path budget between runs? *(Q19)*
18. Retention policy for invocation history — the only store that grows with
    *use* rather than library size. *(Q20)*
19. Is a larger encoder worth its footprint, given that under the staged design
    it only reorders an already-admissible set? **A good candidate for a small
    experiment.** *(Q21)*

**Framing**
20. Who owns the effect ceiling, and at what granularity?
21. Research contribution or internal capability? *(Decides whether Tracks B/C
    need to be publishable.)*
22. Is the ecosystem/federation design still intended? ⚠ Note this question
    changes under server deployment — federation reads differently when the
    system is already a service. *(`13-` Q1)*

### Appendices
- A: ⚠ **the inventory** — full capsule counts, operator fleet, the 52/50
  provider-neutral split, the 28/17/11/0 route breakdown — moved out of the body
  under the new framing.
- A2: design ↔ shipped reconciliation table (`13-` §0).
- B: the four genuinely missing contract pieces — declared timing/idempotency,
  a structured `denies` list, the evolution contract, and an **error contract**
  (`recoverable` appears in 0 of 85 manifests).
- C: verified arXiv reference list (`17-` §9).
- D: what this report does not claim, and why.

---

## Claims this report will not make

Carried from `18-` §6 as amended:

| Not this | This |
|---|---|
| "Capsules are formally verified" | "Contract-checked at admission; formal verification is designed future work" |
| "94% token savings" | Design-doc estimate, unmeasured — cite as a target or omit |
| "80 capsules are stable" | "Marked stable, against a draft schema" |
| "Capsules are safer than MCP/A2A" | "They secure a different layer — semantics and blast radius, not channel or identity" |
| "0 routes at full = immature" | "11 of those are deliberately gated destructive operations" |
| "This is novel" | "Trajectory→tool synthesis is established; the admission and selection contract is the open part" |
| ⚠ "Alita-G targets hidden dependencies / interface violations / spec drift" | **Same fabrication, second paper — zero occurrences in 2510.23601.** §3.3 names Parameter Generalization, Context Removal, Interface Standardization, Documentation Enhancement (`17-` §2.1, corrected 2026-09-11) |
| ⚠ 2604.00392's "four failure modes" | **Fabricated by our summary — zero occurrences in the paper.** Say *silent rot*: 96.8% of 222 tools at C=0.00 on held-out conformance (`29-`) |
| "Alita-G ignores tool quality" | "Its curation rule *is* the rule measured admitting broken artifacts at 96.8%" (`21-` §2, rewritten) |
| "The immutable referee is our contribution" | "Every system freezes something; DGM names it as future work. We specify **what it checks**" (`28-` §6.1) |
| "GAIA is directly comparable" | "The benchmark the closest prior work reports on" |
| "Self-extension is regression-free" | Alita-G reports Right→Wrong flips of 1/1/0 |
| "Trust classes are unresolved" | Resolved — rank at the planner, exact match at binding (`22-`) |
| "Embeddings are the wrong primitive" | "Embeddings rank; they do not admit" — stage 2 of four (`23-` §4) |
| "We replace A2A" | "We replace the *current* A2A hop, which is a third-party skill hitting a public relay" (`23-` §3) |
| "Specialisation is the goal" | "Specialisation is a reversible state; the generalist is the permanent recovery path" (`25-`) |
| MiniLM parameter/dimension figures | ⚠ **[unverified]** — model-card recall. Confirm before publishing (`24-` §1) |
| "Alita-G forgot library management" | "It declines consolidation explicitly, with coverage as the rationale" (`27-` §2) |
| "Capsules make the system secure" | "Capsules are admission, not containment. They make containment tractable" (`26-` §5) |
| "Local compute is the constraint" | Conditional — models are API-based; egress and cost bind instead (`26-` §7) |

## Open before drafting

- ~~**B8**~~ — delivered 2026-09-10; captured in `23-`, `24-`, `25-`.
- **B2** — the dsh seam-role question. Gates §5 and part of §8.
- ~~**B9**~~ — partly answered: API-based models, server deployment for long
  runs. `24-` reframed as conditional; §7b's hardware argument is now the
  *interactive-mode* case and should be presented as such.
- **B10** — the security questions (Q22–Q27). §5c can be outlined but not
  finalised without at least Q22 and Q24.
- **B6** — re-verify the 28/17/11/0 route figures if >1 week passes.
- **Verify before publishing** — the MiniLM parameter/dimension figures in
  `24-` §1 are from model-card recall, not measured.
- The user is still reading papers and will continue. Expect further reframing;
  §5b and §7b are the sections most likely to move.


---

## ⚠ Addendum 2026-09-10 — the six-paper comparison

Note `28-` compares Alita-G, SkillWeaver, CoEvoSkills, SkillDAG, DGM and the
survey. Three things from it change the outline:

1. **§6 gains a spectrum, not just a list.** Order the prior art by *how much
   they trust the artifact they produced*: DGM (benchmark score only) → Alita-G
   (task outcome) → SkillWeaver (unit tests + debug loop) → CoEvoSkills
   (isolated surrogate verifier) → SkillDAG (structural invariants +
   reversibility). **None of the six checks declared effects.** That sentence is
   the contribution claim, and it is checkable.
2. **§7b gains independent confirmation.** SkillDAG states outright that
   "selecting the right subset becomes a **structural problem rather than a
   similarity-matching one**" — the same conclusion as Alita-G's Tables 3/5 from
   the opposite direction. Two papers, opposite methods, same finding.
3. **§7a and §9 gain two traits worth stealing**: SkillWeaver's
   **practice-before-admission** (execute against generated cases and debug
   *before* the capability is admitted — maps onto `draft` → `stable`), and
   CoEvoSkills' **informational isolation of the verifier** (a separate session
   that does not inherit the generator's biases — the buildable complement to
   our immutability rule).

Also: SkillDAG's typed edges (`depends_on`, `specializes`, `similar_to`,
`conflicts_with`) with acyclicity and non-contradiction checks on every commit,
plus an append-only log with rollback, is **the nearest existing analogue to the
capsule admission gate** — and it is reversible. Cite it in §5 alongside Cordis.
