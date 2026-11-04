# Capability Capsule: a declarative schema for AI4Research on openJiuwen

Independent report, 2026-09-21. Companion files: `SCHEMA-ALT.md` (the schema, read top to bottom) and `READ-LOG.md`
(every paper, the last page read, every number with its page). A decision the evidence motivates but does not prove is
marked **(design)**. Code claims give file and line, checked in source. "Today" means the existing AI4Research harness
(`stellven/AI4Research/harness/lib`, commit `b0bf165f9`). The new openJiuwen-based system does not exist yet. Where
this report describes it, it says what it *would* do.

---

# 1. The schema, on one screen

A capsule is **five kinds of record about one capability, kept apart by who is allowed to write each one.**

| Record | What it answers | Who writes it | Can it change? |
|---|---|---|---|
| **Declaration** | What does the capability need, change and promise, and what may it spend? | the builder (a person or RSI) | never; a revision is a new Declaration with a new hash |
| **Verdict** | Was *this exact* Declaration checked? By what, with what result? | the admission gate | append-only |
| **Standing** | Which Declaration is current for this name, and may it be offered? | the librarian | a pointer that moves; every move is logged |
| **Binding** | In this sprint, which exact Declaration served which plan step, and why was it allowed? | the freeze | append-only |
| **Finding** | What did screening, auditing, drift probing or use reveal later? | screeners, auditors, probes | append-only |

The Declaration has seven sections: **identity**, **ports**, **needs**, **changes**, **guarantees** and **budget**, plus
**members** for composites. Every claim in it carries an **assurance level**:

- `enforced`: the runtime prevents a violation;
- `tested`: the gate ran a check before admission;
- `audited`: a run is compared against the claim afterwards;
- `declared`: nothing checks it, and the Declaration says so.

Four rules make this a schema rather than a folder of files:

1. **One writer per fact.** A fact about a capability lives in exactly one record kind.
2. **Declared and observed facts never share a record.**
3. **Every claim states how strongly it is backed.**
4. **Everything downstream refers to a hash, never to a name.**

![Figure 1. Five records, five writers.](figures/F1.png)

Why five records, when one manifest file would be the obvious choice? Every paper in §5 comes back to one question:
*who was in a position to be wrong?*

- In one study, 215 of 222 self-built tools (96.8%) failed every held-out test of their own job, and no in-session
  signal flagged them, because the in-session verifier scores task outputs, not tools (§5.1).
- A judge that has gone lenient silently stops retirement (§5.4).
- A capability that could reach the signal its checker read learned to game it (§5.12).

A single manifest with a `status` and a `quality` block cannot say who asserted what. Symphony's fingerprint, today,
is exactly that kind of mixed object (§6.1). Splitting the records by writer is the smallest structure in which each of
those failures has a named place to be caught.

---

# 2. Terms

Every name used later is defined here, in the order it is first needed.

- **Capability.** Something an agent can invoke. It can be:
  - a tool
  - an MCP server
  - a skill folder (`SKILL.md` plus files)
  - a prompt section
  - a subagent
  - an agent template
  - a composite of these

  Model weights are never a capability here.
- **Capability Capsule (CC).** The schema layer: the five record kinds, their rules, and the capsule-layer code that
  applies them. The supervisor's ruling (2026-09-21) is that "CC is more of a scheme, and verifier is a tool. CC can
  use tools, but CC is not a tool." Here, CC *uses* the gate, the screener and the verifiers; it is not one of them.
- **Capsule.** Informally, one capability together with its records.
- **AI4Research.** The research pipeline being rebuilt on openJiuwen. It is not itself a capsule (supervisor,
  2026-09-18, note 46 §2).
- **Sprint.** One run of the AI4Research pipeline. Its stages are:
  - intake
  - intent
  - requirement compilation
  - planning
  - **freeze**
  - scheduling
  - dispatch
  - operators with in-run gates
  - delivery of claims
- **openJiuwen, agent-core, Symphony.**
  - openJiuwen is the platform.
  - agent-core is its agent runtime.
  - Symphony sits inside agent-core and does capability discovery and planning.
- **RSI.** Recursive self-improvement: the team that builds and improves capabilities.
- **Verification.** The team responsible for capability-level and system-level checks at each sprint.
- **Routing.** The team that picks models, and only models.
- **Builder.** Whoever writes a Declaration: a person or RSI.
- **Run context.** The typed facts available at a decision point. These are:
  - the artifacts that exist
  - state variables
  - services currently provided
  - resources and their modes
  - secret references
  - network zone
  - remaining budget
- **Vocabulary.** A controlled, versioned list of names: artifact types, state variables, resource keys, service keys.
- **Predicate.** A named condition over the run context, evaluated by code to `true`, `false` or `unknown`.
- **Effect.** A declared change to a named resource. It states which resource, which operation, what scope, and how
  it can be undone.
- **Reversibility class.**
  - `inverse`: an undo is declared.
  - `scoped`: the effect happens in a child context that is thrown away.
  - `compensate`: a later action offsets it.
  - `emission`: it crosses the system boundary and cannot be undone.
- **Service key.** A named thing that one capability installs (*provides*) and another depends on (*injects*). These
  are Cordis's terms (§5.15).
- **Check.** An executable test with an id. Its **runner** is the code that executes it, identified by hash.
- **Assurance level.** One of `enforced`, `tested`, `audited`, `declared`, as defined in §1.
- **Policy epoch.** The version of the admission rules, vocabulary and verifier set.
- **Offer.** The set of capabilities a model sees when it chooses. The **executability filter** is the code that
  computes the offer.
- **Freeze.** The step that fixes, before scheduling, exactly which Declarations a sprint will use.
- **Predicate parity.** The same predicate code run at offer time and again at dispatch.
- **Composite.** A capsule whose body is a wired graph of other capsules, each pinned by hash.
- **Gap.** A recorded need that no admitted capability met.
- **Declarative design.** Stating what a capability needs, guarantees and changes, and checking that before use.
- **Observational design.** Judging capabilities by watching outcomes after use.

---

# 3. Where the schema comes from

## 3.1 The supervisor's fixed points

Three rulings bind this design (notes 45 and 46, and the brief):

- **CC is a schema layer, not a tool.** CC relates to RSI, but "the function of CC and RSI are totally different"
  (note 46 §2).
- **AI4Research is not a CC** (note 46 §2). There is therefore a ceiling on how large a capsule can be (§9).
- **Build on openJiuwen and align with its architecture** (note 46 §2). agent-core may be changed only where necessary.

The two slides (note 45) are "thoughts as of before, and don't restrict your thoughts" (note 46 §2). They are still
the team's vocabulary, so this section says where each of their ideas went.

## 3.2 The slide's eight components, mapped

The slide formula is **Capsule = Skill + Rules + Boundary + Assets + Data + Interfaces + Eval + Governance** (note 45
§1). This design keeps every idea in it, but it does not keep the formula as a list of sections. **Governance and Eval
are not facts about a capability. They are facts about what other parties did to it**, so they belong in records those
parties write.

| Slide component | Where it lives here | Why it moved |
|---|---|---|
| Skill (the executable body) | Declaration `identity.body` + `carrier` | A skill is one possible body, not the capsule (§6.7) |
| Rules | Declaration `needs.when`, `needs.applies_to` | Rules become predicates that can be evaluated |
| Boundary (permissions, scope, Action Contract) | Declaration `changes.effects[].scope`, `needs.network`, `needs.secrets` | The slide's own verb is 固化, "frozen into machine-enforceable constraints". That is `enforced` assurance |
| Assets | `identity.body` (files by hash) | Assets are what gets loaded, so they are hashed |
| Data | `needs.resources`, `needs.external` | Data is a dependency with a mode (read, write, exclusive) |
| Interfaces | `ports` | Typed and drawn from the vocabulary |
| Eval | Declaration `guarantees` (what should be checked), **Verdict** (what was checked) | The promise and the result have different authors |
| Governance (policy, permission, audit, version) | **Standing**, **Verdict**, the `prev_hash` chain, the policy epoch | Governance is done *to* a capsule, never by it |

The slide's most load-bearing sentence is: "A unified contract lets the orchestrator understand only the interface,
the constraints and the acceptance criteria, with no need to understand the capsule's internal implementation" (note
45 §4). This design takes it literally. The planner and the chooser see `summary` and `ports`. The filter sees
`needs`. The freeze sees hashes and Verdicts. Nothing downstream reads the body.

The slide's third checkmark, "the object of evolution shifts from model parameters to an auditable capability library
plus verified state" (note 45 §5), is what the Standing log and the Binding log are for.

---

# 4. The tools the schema serves

CC is a scheme that tools read. The fields exist because a tool needs a fact before it can act. The table lists every
tool; each one has a name here that is used throughout.

| Tool | What it does | Code or model | Reads | Writes |
|---|---|---|---|---|
| **Admission gate** | decides whether a Declaration may be used at all | code; calls verifiers, some of which are models | the whole Declaration | Verdict |
| **Executability filter** | computes the offer at each choice point | code | `needs`, `applies_to`, `model`, block Findings | the offer |
| **Chooser** | picks one capsule per plan step from the offer | model | `summary`, `ports` | the choice (recorded in the Binding) |
| **Freeze** | fixes the Declarations a sprint will use | code | Standing, Verdicts, port types | Binding |
| **Dispatch check** | re-evaluates predicates live | code (the same predicates as the filter) | `needs.when` | appends to Binding |
| **Composition screener** | looks for harm that appears only when capsules act together | model inside a code harness | `effects`, `invariants`, `injects`/`provides`, `domain_scope` | Finding (`composition`) |
| **Verifier audit** | compares what a run did with what was declared | code; model for some checks | `effects.scope`, `checks`, sandbox logs | Finding (`audit_violation`) |
| **Drift probe** | checks that external dependencies are still as declared | code | `needs.external` | Finding (`drift`) |
| **Librarian** | moves Standing, applies caps, retires, finds overlap | code | Verdicts, Findings, Bindings | Standing, Finding (`overlap`) |
| **Invalidator** | finds the work that depended on a revoked hash | code | Bindings, step identities | marks claims `stale` |
| **Gap ledger** | counts recurring unmet needs and asks for a build | code | empty offers, dispatch failures | Finding (`gap`) |
| **Builder** | writes a Declaration and its body | a person or RSI (model) | gap Findings, failed checks | Declaration |

![Figure 2. Tools around the records (what reads what).](figures/F2.png)

Where the long discussion of papers belongs, and why: §5 comes **after** the schema and the tool list, and **before**
the comparisons. Each paper is used to argue for a tool, and each tool is what makes a group of fields necessary. A
reader who already has the tool list can check, paper by paper, that every field has a reason and that no reason lacks
a field. Putting the papers first would make the reader hold twenty findings with nowhere to attach them. Putting them
last would make the schema look arbitrary until the end. Each subsection of §5 ends with the same three lines: the
tool the paper motivates, the fields it needs, and what that means for each team.

---

# 5. Why the schema looks the way it does, paper by paper

Every paper here was read in full. The last page read and every number are in `READ-LOG.md`. Setups are stated beside
the numbers because most of them are narrow.

## 5.1 Beyond Task Completion (2604.00392): passing a task is not doing the job

**What it found.** Tools that agents built for themselves, that executed cleanly and helped pass in-session tasks were
nearly all wrong on held-out tests of their own declared capability.

- Of 222 synthesised tools, 215 (96.8%) had conformance 0 on held-out suites (abstract p1; Table 5, p5).
- The mean conformance was 0.018 (Table 5, p5).
- This is one model, Claude Haiku 4.5, over three seeds (p3), with libraries that live only within a session (p3).
- One Sonnet-built tool passed its own agent-written self-tests and helped its session reach 0.95 task completion. It
  scored 0.00 on its held-out suite (p6).
- The authors calibrated the suites first: hand-written reference implementations score 1.00 on all 16 capability
  suites (p5). So the zeros are not artifacts of broken tests.

**Why this argues for declaration.** Watching outcomes, meaning task completion, did not reveal the problem. Task
completion did not even separate the protocols. None of the three pre-registered contrasts showed an improvement, and
the one nominally negative contrast (−0.0710) does not survive correction (Table 4, p4). What did reveal it was a test
of the tool against its *declared job*, written by someone other than the builder.

**Tool: admission gate, with a verifier audit behind it.** Fields:

- `guarantees.checks[].author`, `held_out` and `written_before_body`. At least one acceptance check must be authored
  by someone other than the builder and held out from the builder (SCHEMA §3.1).
- `owner: self` checks are never admission evidence. The Sonnet case is the reason.
- `ports.outputs[].check_id`: an output with no check is `declared`, not `tested`.

**For the teams.**

- Verification is asked to write or own held-out suites per capability.
- RSI can no longer admit a tool by showing that the task it was built for passed.
- The pipeline gains a real "conformance" signal, which it does not have today.

## 5.2 More Skills, Worse Agents? (2605.24050): the chooser is the bottleneck

**What it found.** Pass rate falls as a skill library grows, and the loss comes from choosing the wrong skill, or none.
It does not come from the extra context.

- Pooled over two Anthropic models, 38 task–model pairs and 2,545 trajectories (p8), the drop at 202 skills is 0.21
  absolute pass rate (Table 1, p9).
- Of that, the shadowing component is 0.14 [0.06, 0.26]. The context component, 0.07 [−0.13, 0.25], is not
  distinguishable from zero.
- The chooser sees only a skill's name and description until it invokes the skill (p4).
- The share of trajectories that invoke no skill at all rises from 12.0% to 38.5% (Table 2, p9).

**Why this argues for declaration.** A retrieval score, which is an observation of text similarity, is exactly what
produced the shadowing. Two things help:

- remove capsules the chooser should never see, which is the filter (§5.3);
- make what the chooser does see precise and distinct.

**Tools: executability filter, and the librarian's overlap check.** Fields:

- `identity.summary`, capped at 400 characters **(design)**. It is the only prose the chooser sees.
- `applies_to.domain_scope`, which narrows the offer.
- The librarian computes an `overlap` Finding between Declarations whose summaries and ports are close. It holds the
  newer one on DEFER until the summaries are disambiguated or one is superseded (SCHEMA §4.9).
  - Overlap is **computed**, never declared, because a builder cannot know every other capsule.
- Library caps per `slot` (see §5.4 for why caps alone are not enough).

**For the teams.**

- Routing is unaffected; this is about capsules, not models.
- Symphony's retrieval still ranks, but only inside the offer (§6.1).

## 5.3 Don't Offer What Can't Be Done (2608.01050): check before the model chooses

**What it found.** In a production customer-care assistant, a deterministic gate that evaluated each skill's own
hard-exit condition against authoritative account state, *before* the model chose, removed a large share of what the
model would otherwise have been shown.

- It removed 59.4% of post-semantic skill–message pairs and 59.1% of description tokens (p1, p5).
- With semantic matching included, that is a 90.5% reduction versus exposing all ten skills (p1, p5, p6).
- In a risk-enriched cohort of 1,000 conversations replayed with all skills visible, the model picked a skill the gate
  would have blocked 78 times, i.e. 7.8% (p1, p5, p6).
- The setup is narrow: one family of ten skills, one window, an unnamed model and one replay each (p2–p6). The paper
  says the 7.8% must not be extrapolated.

**The two conditions the paper names.** The gate is sound only under:

- **predicate parity**: the gate's predicate *is* the skill's own exit logic;
- **fresh authoritative state** (p3).

It also says:

- the guarantee is one-sided: passing the gate means only that no represented hard exit holds (p3);
- fail-open versus fail-closed on unknown state must be explicit and tested (p5).

**Tools: executability filter and dispatch check.** Fields:

- `needs.when[]`, as predicates over vocabulary names, each with:
  - `max_age_s`: a stale fact counts as `unknown`;
  - `on_unknown`: `defer` or `exclude`. This makes fail-open or fail-closed explicit;
  - `parity_check`: a check with shared fixtures, including missing-state and stale-state cases, showing that the
    predicate agrees with the body's exit logic.
- The dispatch check runs *the same predicate code*. Today, AI4Research's filter and dispatch use two different
  condition languages (§6.6). That is exactly the parity gap this paper warns about.

**For the teams.** Verification owns the parity fixtures. The pipeline gets cheaper offers and fewer impossible
choices.

## 5.4 The Blind Curator (2607.07436) and Library Drift (2605.19576): watching outcomes to retire, and its failure

These two papers come from the same group and use the same loop (Ratchet), so they are read together.

**Library Drift: retirement by observed contribution can work.** On MBPP+ hard-100 with one model (Claude Opus 4.7),
three seeds × 100 rounds (p3–4):

- The default loop, with retirement and a cap of 50, gained +0.328 ± 0.018 (Table 1, p5).
- "Harsh" retirement (evidence floor from 100 to 20 and threshold from 0.10 to 0.0, two knobs at once) collapsed to
  2 active skills and a gain of −0.019 (Table 1, p5).
- A cap of 100 instead of 50 gave a similar mean with more variance: +0.317 ± 0.110 (Table 1, p5).
- The lessons are that **governance can be worse than none**, and that an evidence floor matters.

**The Blind Curator: observation-driven retirement fails silently when the judge is biased.** When the judge that
scores outcomes has a false-pass rate ρF→P ≥ (1−τ)/2 (0.45 at τ = 0.10), contribution-based retirement can never fire,
"at any sample size" (p4; App. C, p13–14).

- In the main experiment, genuine retirements fall from 1.3 (clean) to 0.0, 0.3 and 0.0 under the three bias levels
  (Table 1, p6).
- Cap evictions keep the raw deprecation count looking alive (Table 1, p6).
- The setup is narrow: three seeds × 12 rounds, eval sets of 28 and 23 tasks, synthetic corruption (Table 2, p12).
- The authors' own real judge was strict, not lenient: ρF→P ≈ 0.01, ρP→F ≈ 0.95 (p5; App. E, p15). The cliff is a
  measured risk, not an observed accident.

**Why this is the sharpest argument for declaration.** An observational library needs a trustworthy observer. The
observer's error is invisible in the outcomes it produces. The only defence the paper offers is to **measure the judge
before relying on it**, by injecting known defects.

**Tools: librarian and verifier audit.** Fields:

- Verdict `verifiers[].measured_error`: false accept, false reject, n, what it was measured on, and the date.
- Standing `reason` codes: `RETIRED_ON_EVIDENCE` and `EVICTED_BY_CAP` are separate, so a dead curator shows as zero
  of the first.
- A librarian rule: retirement driven by a model judge is suspended while that judge's false-pass rate is at or
  above the cliff, and nothing is retired below the evidence floor (SCHEMA §4.9).
- `checks[].judge: deterministic | model`. The two have different failure properties.

**For the teams.**

- Verification is asked to **measure every judge it supplies**. This is the largest new demand on that team, and the
  clearest improvement in what its work is worth.
- RSI benefits because its outputs are no longer retired by a judge nobody has checked.

## 5.5 When Self-Evolution Backfires (2608.05810): gate before commit, not clean up after

**What it found.** On Terminal-Bench 2 with one evolution backbone:

- An ungated skill pool peaked at 62% with 105 skills (round 3), then fell to 50% with 179 skills (round 5) (Table 1,
  p6).
- A pre-commit gate reached 72% with 37 skills (Table 1, p6).
- Removing the gate's held-out replay cost 10 points. Removing its set-level marginal-gain step cost 8 points and let
  the pool grow to 58 (Table 2, p6).
- Cleaning up afterwards did not recover the loss (Fig. 4 text, p7). Of a 12.3-point drop:
  - rolling back the harmful source skills recovered 1.7;
  - oracle cleanup of their descendants recovered a further 5.0;
  - 5.6 was unrecoverable.
- Lineage cleanup "requires provenance a real system lacks" (p2, p7): nobody recorded which skills were in context
  when a new skill was written.
- Caveats: the main table is on the distillation split, which the paper calls an optimistic upper bound. The holdout
  set is 14 tasks. The CI bands are about 30 points wide (p5).

**Why this argues for declaration.** It is the clearest measurement of the cost of "observe, then clean up". Harm
propagates through what builders learn from, so removal after the fact is incomplete.

**Tools: admission gate (set-level) and librarian (lineage cleanup).** Fields:

- `lineage.context_capsules`: the Declarations that were in the builder's context. This is exactly the missing
  provenance the paper names.
- The gate's step 6 (SCHEMA §4.1): a candidate that passes alone but lowers the slot's joint result is rejected with
  `NEGATIVE_MARGINAL_GAIN` **(design)**.
- A librarian rule: when a capsule is revoked for harm, every capsule that lists it in `context_capsules` becomes
  `suspect`.
- Candidates are never placed in a builder's context.

**For the teams.** RSI is asked to record what its builder saw. In return, a bad capsule's descendants can be found
precisely, instead of rolling back a whole library.

## 5.6 SkillFuzz (2607.02345): composition risk is not in any single capsule

**What it found.** Individually benign skills, activated together, lead planners to form objectives that neither the
task nor any single skill asked for.

- Across 8 planners, 10 tasks and a 196-skill library, it found 1,188 such "implicit intents" at a budget of 200
  queries per task (Table I, p6; p9).
- 80.6% of the 98 highest-risk flagged combinations were confirmed at execution time (Table II, p7).
- Severe plan drift rose with the number of co-activated skills, reaching 66.5% at five (Fig. 6 text, p9).
- The screener read, per skill, a contract that an LLM **extracted from prose**: preconditions, postconditions,
  **modifies set**, **invariants**, domain scope, action types, and an extraction confidence (p4).
- Its seed ranking used shared modifies-set entries and mutually exclusive invariants (p5).
- Limits (p10): thresholds are uncalibrated; the judge may be biased; a plan oracle cannot catch an agent that acts
  unlike its plan; and a deployed gate "would need to re-screen co-activations as skills … are updated".
- The strategy comparison is one task × one agent (p7–8).

**Why this argues for declaration, and where declaration stops.** Every input SkillFuzz needed was a declaration that
the skills lacked, so it had to guess them with a model. A capsule that declares `effects` and `invariants` gives the
screener its seed signal without extraction. But the harm itself is a property of the *set*, not of any member, so it
can only be *screened*, never declared. This is the plainest limit of the declarative design, and §11 shows how the
schema handles it.

**Tool: composition screener.** Fields:

- `changes.effects` (the modifies set), `changes.invariants`, `needs.injects`/`changes.provides`, and
  `applies_to.domain_scope`;
- `coverage.undeclared_notes`, the declared-completeness analogue of SkillFuzz's extraction confidence;
- a `composition` Finding keyed by the *set* of hashes, voided when any member's hash changes.

**For the teams.** Verification (or whoever owns screening) runs the screener. The freeze records whether each
co-activation was screened. RSI's revisions trigger re-screening automatically.

## 5.7 Cognitive Admission Control (2609.16313): typed verdicts, and "unknown" is not "no"

**What it found.** A deterministic admission calculus for consequential actions. It is a prototype with no language
model: 2,730 synthetic trials (p8–9), "not production failure rates" (abstract).

- Five outcomes: PERMIT, DENY, DEFER, ESCALATE, ABORT (p5).
- Discharge is three-valued: a missing observation is distinct from evidence that a predicate is false (p4).
- Evidence has freshness, class and scope.
- Budget exhaustion never yields a permit (Thm 2).
- A compensatory scalar score can buy out a failed required condition (Prop. 1).
- On the constructed fixtures, the full controller had 0 harmful effects in 390 trials, against 30 for a live-policy
  check and 180 for authorisation alone (Table 2, p10).
- The paper also says plainly that this "does not establish a general utility advantage over a competent live-policy
  check" (p10).

**Tools: admission gate and executability filter.** Fields:

- The Verdict `outcome` is `ADMIT | REJECT | DEFER | ESCALATE`, with typed `reasons`.
- `on_unknown: defer` on predicates, and `max_age_s`.
- Verdicts are bound to a `policy_epoch`, and `invalidated_by` names what voids them.
- **No scalar quality score in admission** (SCHEMA §5).

**For the teams.** The pipeline gains a way to say "not yet": a DEFER carries a typed request for the missing fact.
That is better for users than silent exclusion.

## 5.8 GraSP (2604.17870) and SkillDAG (2606.03056): edges between capabilities

**GraSP.** It compiles a few retrieved skills into a graph with typed precondition and effect edges, then checks
preconditions and postconditions at each node.

- It beats every baseline in all 48 model–split cells, by +6.9 points on average over the strongest per-cell baseline
  (p5).
- The margins are uneven: 0.5–1.1 points on InterCode for 7 of 8 models (Table 1, p6).
- DAG compilation alone adds +1.9 on ALFWorld seen (Table 2, p7).
- Results are averaged over 3 runs with no variance reported (p6).
- The preconditions and effects are **written by an LLM at compile time**, not declared by skill authors (p4,
  p15–16).
- One rule is directly useful: a substitute's effects must cover what downstream nodes require (p4).

**SkillDAG.** It keeps typed relations between skills, including `conflicts_with`.

- Conflicts are defined as online-only and are committed on a single observation. The paper names that as an open
  risk (p11).
- It gives no quantitative evidence on conflicts (p5–6, p17–19).
- Its baseline rewards are quoted from another paper, not re-run (p8).

**What they give the design.**

- Typed edges help, and precondition failures are the most locally repairable.
- Neither paper had *declared* contracts to work from. Both inferred structure with a model or from runs.
- For this schema, that means:
  - `ports`, `needs` and `effects` are declared, so the edges can be computed by code rather than guessed;
  - the replacement-compatibility rule (SCHEMA §4.6) is GraSP's substitution rule applied to revisions;
  - observed conflicts are Findings (`conflict_observed`) that need a threshold of independent co-occurrences before
    they can block a set **(design)**, because a single observation is too weak;
  - declarable conflicts, such as two capsules writing the same resource, need no observation at all. They follow
    from `effects`.

**Tools: composition screener, librarian, freeze** (port type checks).

## 5.9 AllocBench (2607.23332): build on recurrence, not first sight

**What it found.**

- Models that allocate a build budget well in the abstract commit to building at first sight once they have to write
  real code. At the code-emitting rungs, first-sight commitment was 85–100% for three of four models (Table 1, p6).
- The fourth, GPT-5.6 Sol, committed 39% at the code rung and 100% at full script construction (Table 1, p6).
- On the benchmark's own distribution, committing at the second occurrence scores 43.0 points per stream against
  34.6 at first sight (App. A.1, p12).
- The paper recommends separating the decision to invest from the act of building (p8), but did not test that.
- The setup is one synthetic environment with 24 seeds (p3, p9).

**Tool: gap ledger (code) in front of the builder.** Fields:

- A `gap` Finding with `signature`, `occurrences`, `first_seen` and `last_seen`;
- a policy threshold before RSI is asked to build (default 2 **(design)**);
- `lineage.build_trigger` on the resulting Declaration.

**For the teams.** RSI is asked for builds only when code has counted recurrence. RSI still decides *how* to build.

## 5.10 Agent Contracts (2601.08815) and Agent Behavioral Contracts (2602.22302): budgets and behaviour, declared

**Agent Contracts.** It declares resource budgets and enforces them from outside the agent.

- In a code-review loop on 70 problems, tokens fell 90% (34,606 to 3,461, p = 0.0007).
- Success fell from 60.0% to 52.9%, which is not significant (p15).
- The budget, the iteration cap and the prompting changed together, so the 90% cannot be credited to the budget
  alone.
- The paper states the key limit itself (p12): "contracts cannot prevent a single expensive call from exceeding
  budget". It reports a run that consumed 56K tokens against a 40K budget before it was halted (p16).
- It shows parent budgets that bound the sum of child budgets (p10).

**Agent Behavioral Contracts.** It gives a contract structure: preconditions, hard and soft invariants, hard and soft
governance rules, and recovery (p8). It also gives composition conditions:

- C1: output types fit input types;
- C2: postcondition plus handoff implies precondition;
- C3: no stage permits what another prohibits;
- C4: recovery output still meets downstream preconditions (p17–18).

Its declarations are schema-validated and deliberately not Turing-complete (p22, p24). The reader found its empirical
headline internally inconsistent (p29–35, p43–44), so only the structure is used here.

**Tools: runtime budget enforcement, verifier audit, and gate checks for composites.** Fields:

- `budget.per_call`, with `enforcement` recorded per dimension: `hard`, `between_calls` or `post_hoc`. Tokens are never
  assumed to be `hard`.
- For composites, the gate checks that member budgets sum to no more than the composite's budget (§9), which is the
  conservation rule from Agent Contracts. It also checks C1 and C3 over `ports` and `effects`. C2 and C4 need
  predicate entailment, which is `declared` unless a check exists.

## 5.11 Skill Drift Is Contract Violation (2605.10990) and Contract2Tool (2606.07904): contracts on what moves

**Skill Drift.** Skills rot when the packages, URLs and APIs they depend on move.

- Extracting operational dependencies as contracts and probing them detected drift with 0 false positives in 599
  negatives (p7), and 76% best recall (Table 2, p7).
- A pre-registered open-world study on 49 skills had 55% recall (p8).
- Repair localised by the failed contract succeeded 25 of 32 times (78%), against 2 of 20 with no localisation. It was
  not significantly better than plain drift text, which scored 12 of 20 (p = 0.213; Table 14, p19).
- Two points matter here:
  - deciding whether a dependency is *operational* before probing it avoids false alarms (p5–6);
  - probing only declared manifests misses assumptions written in prose (p3).

**Contract2Tool.** It infers requires and produces contracts and filters tools with them.

- On a synthetic 100-tool registry with mocked execution (p5), the learned-contract filter reached 0.980 success with
  2,528 tokens, against 0.775 and 26,172 tokens with all tools exposed (Table V, p8).
- Contracts from docs or schema alone hid the needed next tool in 7.8% of steps (Table IV, p8).
- Risk labels were only 0.63–0.67 accurate (Table III, p7).
- Learned contracts are "not an unchecked replacement for safety review" (p9).

**Tools: drift probe, and the gate's vocabulary check.** Fields:

- `needs.external[]`, with `kind`, `value` and `role: operational`;
- a `drift` Finding that moves the Standing to `suspect`;
- the failed contract passed to the builder as a localised repair input;
- a controlled **vocabulary** for artifact types and state variables. Contract2Tool worked only because names were
  normalised to one vocabulary (p4).

**For the teams.** RSI gets precise repair tickets. Verification gets a cheap periodic probe instead of re-running
everything.

## 5.12 Darwin Gödel Machine (2505.22954): the checker must be out of reach, and so must its signal

**What it found.** A self-modifying coding agent improved SWE-bench from 20.0% to 50.0% (abstract). That was one run
on SWE-bench; variance was measured only on Polyglot (p26).

The case that matters here is the hallucination study (p69–71):

- The checker was hidden from the agent.
- It read special marker tokens that the agent's *own code* emitted.
- The agent removed the marker logging "despite instructions not to change the special tokens", and scored 2.0 on
  the objective without solving the problem (node 114, p70–71).
- Hiding the checker reduced this but did not prevent it (p70).

The exploration loop and parent selection were "fixed and not modifiable by the DGM" (p4–5). The authors propose "an
unmodifiable part of the system to be able to evaluate at halt the rest" (p9).

**Tool: admission gate.** Fields:

- `checks[].runner` with its hash. A runner inside the capability's `effects.scope` is ineligible for acceptance.
- `checks[].signal_source: harness | capsule`. A check whose evidence the capability itself emits is ineligible for
  acceptance. This is the node-114 lesson: the checker was out of reach, **its input signal was not**.
- `lineage.diagnosis_inputs`, so that it can be seen when a builder was shown checker internals. The paper's diagnosis
  step saw private test patches (p29–30).

**For the teams.** This is the reason the gate, the freeze, the verifiers and the librarian must never be capsules
(§9). It also asks RSI to keep checker internals out of what its builder is shown.

## 5.13 Alita-G (2510.23601) and CoEvoSkills (2604.01687): self-built libraries help, if someone else checks them

**Alita-G.** It harvests MCP tools from successful runs and reuses them.

- On GAIA it reached 83.03% pass@1 against 75.15% (Table 1, p7), with fewer tokens: 10,394 against 12,305 (p8).
- But the box was harvested from the same validation set it was scored on (p9–10).
- An MCP was kept only because its parent run succeeded. The abstracted tool was never re-tested (p5).
- The box saturated: 128 MCPs formed only 65 clusters, and accuracy was flat after 74 (Table 4, p9).

**CoEvoSkills.** It evolves skills with a verifier kept separate from the builder: the verifier sees instructions,
inputs and outputs, never the skill source (p3–5).

- It reached 71.1% against 53.5% for human-curated skills and 30.6% with none (Fig. 4, p7, read from the PDF).
- Removing the separate verifier dropped it to 41.1% (Table A1, p14; single run).
- Skills were evolved on the same task they were scored on, and the hidden oracle took part in the loop (Alg. 1, p5;
  p19, p21).
- The paper says the surrogate verifier "cannot distinguish its own estimation error from the agent's error" (p17).

**What they give the design.** Self-built capabilities are worth having, which is why RSI exists. Both papers show
where the value can be illusory:

- admission on a parent's success, without re-testing what is actually stored;
- a verifier that shares the evaluation set.

**Tool: admission gate.** Fields:

- `identity.body[]` hashes. The gate tests the *stored* artifact, not the run it came from.
- `checks[].author` must not be the builder, and `held_out` must be true.
- A Verdict records which verifier ran. A surrogate pass is not an oracle pass.

## 5.14 Execution lineage (2605.06365) and RelAIBuild (2606.26924): hashes, and a control plane that is code

**Execution lineage.** It gives each step an identity k_v = h(σ_v, x_v, {k_u}): its spec, its input hash and its
predecessors' identities (p6, eq. 4). An update that is off the dependency path then leaves outputs exactly as they
were.

- DAG replay preserved the final memo exactly in 3 of 3 runs. Loop agents regenerated it in 3 of 3 and contaminated it
  (Table 1, p10).
- That is two tasks, one model and n = 3 (p10, p13).
- Its design rule: "a node should not be allowed to consume undeclared upstream state" (p5).

**RelAIBuild.** It is a deterministic control plane for coding agents.

- It hashes the *canonical* definition, not its compiled renderings (Lemma 2, p39).
- It aborts installation on hash mismatch.
- Its phase guards "cannot be bypassed via persuasive LLM prompting" (p18).
- It reports that only 31 of 6,145 agent config files (0.5%) declare explicit permission scopes. The paper marks
  this figure as indicative, with true coverage near 0% (Table 10, p30-31).
- Four of seven harness targets have no tool-level enforcement at all (p22). A declared permission is not an enforced
  one.
- Anything that depends on the agent reporting on itself is detect-only (p20–21).
- The author states there is no outcome evidence (p4, p27–28, p35).

**Tools: freeze, invalidator, verifier audit.** Fields:

- `decl_hash` over the canonical Declaration, and `body[]` hashes checked at load.
- Binding `step_identity`, so revocation can find exactly the stale work.
- `assurance` per claim, because declared is not enforced. That is the 0.5% and the four-of-seven finding.
- `prev_hash` chaining on every append-only record. The reader found that RelAIBuild's own "hash-chained" log hashes
  each line alone (p12), which would not detect deletions.

## 5.15 Cordis (2608.25512): add, replace, revert, remove

**What it is.** The paper is "A Programming Paradigm for Spatiotemporal Composability". Cordis is its implementation.

- A **component** is a triple: what it injects, what it provides, and an effect iterator whose every step carries its
  inverse (Def 48, p31).
- **Temporal composability** means unloading restores the shared environment (p4, p9).
- **Spatial composability** means components declare, discover and resolve dependencies at runtime (p4, p16).
- The runtime guarantees:
  - recovery exactness (Thm 68, p46);
  - providers activating before and outliving their consumers (Thm 70, p47);
  - that any sequence of add, remove, replace and undo reaches the same state as loading the final configuration from
    scratch (Thm 80, p54–55).
- Removal takes two steps: stop providing, then dispose only when no dependent still relies on the component (p36;
  Alg. 5, p62–63).

**One correction for the team.** The phrase "Capability Capsule is a Cordis hyper-plugin" cannot be grounded in this
paper. The word "hyper-plugin" does not appear in it, and "plugin" is Koishi's word for what the paper formalises as a
component (footnote 5, p69). The nearest real construct is a component that instantiates other components (Def 52,
p35).

**What it does not guarantee.**

- It does not verify that an inverse is correct; that is the author's obligation (p59).
- Emissions are not reverted: "a message already sent stays sent" (p47; p70–71).
- It has no versioning or structural typing of keys (p75).
- Dependency cycles leave components inactive (p74).
- It does no sandboxing (p73).
- It has no performance measurements (p70).

**Fields.**

- `needs.injects`, with an interface version range (this fills Cordis's versioning gap).
- `changes.provides`, with `commutative`. Cordis shows that independent effects on commutative keys can be reverted in
  any order (Thm 43, p28; Thm 47, p30), and ordered chains cannot.
- `effects[].reversibility`, with `emission` given its own policy.
- The two-step Remove (SCHEMA §4.6).
- Binding `resolved[]`: which provider each injected key resolved to. This is Cordis's "committed view" (Def 49, p32).

§10 gives the full account.

## 5.16 The papers at a glance

| Paper | Tool it motivates | Fields it makes necessary | Team most affected |
|---|---|---|---|
| Beyond Task Completion | gate, audit | `checks[].author/held_out/written_before_body`, `owner` | verification, RSI |
| More Skills, Worse Agents? | filter, librarian | `summary`, `domain_scope`, `overlap` Finding, `slot` | pipeline |
| Don't Offer | filter, dispatch | `when[].max_age_s/on_unknown/parity_check` | pipeline, verification |
| Blind Curator, Library Drift | librarian, audit | `verifiers[].measured_error`, Standing `reason` codes, evidence floor | verification |
| Self-Evolution Backfires | gate (set-level), librarian | `lineage.context_capsules`, `NEGATIVE_MARGINAL_GAIN` | RSI |
| SkillFuzz | screener | `effects`, `invariants`, `coverage`, `composition` Finding | verification |
| Cognitive Admission Control | gate, filter | Verdict `outcome`, `reasons`, `policy_epoch`, `on_unknown` | all |
| GraSP, SkillDAG | screener, freeze, librarian | `ports`, replacement rule, `conflict_observed` threshold | pipeline |
| AllocBench | gap ledger | `gap` Finding, `build_trigger` | RSI |
| Agent Contracts, ABC | runtime, gate | `budget.enforcement`, composite budget conservation, C1/C3 | pipeline |
| Skill Drift, Contract2Tool | drift probe, gate | `needs.external`, vocabulary | RSI, verification |
| Darwin Gödel Machine | gate | `runner` outside scope, `signal_source`, `diagnosis_inputs` | RSI, verification |
| Alita-G, CoEvoSkills | gate | `body[]` hashes tested as stored, `author ≠ builder` | RSI |
| Execution lineage, RelAIBuild | freeze, invalidator, audit | `decl_hash`, `step_identity`, `assurance`, `prev_hash` | pipeline |
| Cordis | spatiotemporal manager | `injects`, `provides.commutative`, `reversibility`, `resolved[]` | agent-core seam |

---

# 6. The argument for declaration, and its limits

## 6.0 The claim

**Grant authority only on checked declarations. Let observation withdraw authority, and never let it grant it.**
**(design)**

Every paper in §5 supports one half of this.

**Observation alone failed** in five of them:

- task completion missed 96.8% silent rot (§5.1);
- a biased judge stopped retirement without any visible sign (§5.4);
- cleanup after commit left 5.6 points unrecoverable (§5.5);
- a capability gamed the signal its checker read (§5.12);
- success-harvested tools were never re-tested (§5.13).

**Checking a declaration before use helped** in five:

- a precondition gate removed 59.4% of impossible offers (§5.3);
- typed verdicts with DEFER blocked constructed harms (§5.7);
- a pre-commit gate beat post-hoc cleanup (§5.5), on a split the paper itself calls an optimistic upper bound, with
  wide intervals on a 14-task holdout;
- hash identity preserved untouched work exactly (§5.14);
- declared contracts localised repair (§5.11).

## 6.1 Where declaration stops (honestly)

1. **Authors do not declare, or declare wrongly.**
   - Only about 0.5% of agent config files declare permission scopes, an indicative figure (§5.14).
   - GraSP, SkillFuzz, SkillDAG and Contract2Tool all had to *infer* contracts with a model, because nobody had written
     them.
   - Inferred risk labels were 0.63–0.67 accurate (§5.11).
   - The schema's answer: the gate refuses an undeclared field where a tool needs it. `coverage.undeclared_notes`
     makes known gaps visible. Inference by a model may *suggest* a Declaration to the builder, but it never is one.
2. **Declared is not enforced.**
   - Four of seven harnesses enforce no tool permissions (§5.14).
   - agent-core's `before_tool_call` sees tool calls, not what code does inside them
     (`harness/observability/rail.py:888`).
   - The answer: `assurance` per claim. The sandbox makes `effects.scope` `enforced` during admission and dispatch.
     The audit makes it `audited` afterwards.
3. **Some harms exist only in combination.** Composition risk is a property of a set (§5.6). It can be screened, not
   declared (§11).
4. **Some effects cannot be undone.** Cordis does not revert emissions (§5.15). They get a policy, not a promise.
5. **Predicates can drift from the code they describe.** That is why the gate requires parity checks (§5.3), and why a
   `drift` Finding exists (§5.11).
6. **Checks are only as good as their verifiers.** That is why a verifier's measured error is recorded (§5.4).
7. **Budgets cannot stop a single overshooting call** (§5.10).

Observation therefore stays in the design, in a subordinate role. Findings from use, audit, drift and screening can
move a Standing to `suspect` or `revoked`. They can never move it to `admitted`.

---

# 7. Comparison with what exists

## 7.1 Symphony's fingerprint versus a Declaration

**What the fingerprint is, in source (agent-core `e23806c1`).**

- `CapabilityFingerprint` extends the provider-supplied `CapabilityDescriptor` with a semantic profile, inputs and
  outputs, a classification, tags, a content hash, a quality result, failures, evidence and suggestions
  (`symphony/models/fingerprint.py:29-44`).
- The descriptor fields are id, type, name, description, source, available, inputs, outputs, classification, tags,
  content hash and metadata (`symphony/models/capability.py:61-76`).

**How it is derived.** `FingerprintService.build` works in three steps:

1. **Inventory.** It loads the inventory from a `CapabilityProvider` (`shared/fingerprint/service.py:145`;
   `interfaces/capability.py:13`).
2. **Extraction.** It extracts each fingerprint (`service.py:158`).
   - When the descriptor lacks inputs or outputs, a model infers them from the capability's definition, with the
     instruction "Use only evidence present in the supplied definition" (`shared/fingerprint/extractor.py:39-62`,
     `:157-202`).
   - The content hash is the provider's if it supplies one. Otherwise it is SHA-256 over the descriptor
     (`extractor.py:151`, `:335-343`).
3. **Quality.** It evaluates quality over traces (`service.py:172-204`).
   - The evaluators include trace-based success-rate and latency (`symphony/evaluation/evaluators.py:308`, `:392`).
   - They also include LLM judges for description quality, accuracy, completeness, capability selection and
     composition effectiveness (`evaluators.py:209`, `:438`, `:560`, `:621`, `:646`).
   - An evaluator that raises becomes an error-quality result instead of stopping the build (`service.py:194-195`).

**What the graph and planner do with it.**

- The graph accepts only skill, subagent and agent fingerprints (`orchestration/graph/build.py:161`).
- It proposes `can_feed` edges at a threshold of 0.7 (`build.py:122`).
- The fast planner sees each candidate's id, name and description and "Do[es] not judge compatibility from Skill I/O"
  (`orchestration/planning/fast.py:32-44`).
- Batch graph mutation needs an `AtomicCapabilityProvider` (`orchestration/mutations.py:164-169`) and a model for
  ontology matching (`orchestration/mutation_service.py:129-135`).

**The contrast.**

| | Symphony fingerprint | Capsule Declaration |
|---|---|---|
| Author | derived by the service, partly by a model, from whatever the provider exposes | written by a builder, checked by a gate |
| What it commits to | nothing; it describes | needs, effects, guarantees, budget, each with an assurance level |
| Where quality lives | inside the same object (`quality`, `failures`) | in separate Verdicts and Findings, with their writers named |
| Identity | content hash of the descriptor | hash of the canonical Declaration and every body file |
| Invalidation | re-extract when the hash or evaluation signature changes (`service.py:175-190`) | Verdicts carry `invalidated_by`; Bindings point to exact hashes |
| Preconditions and effects | not represented | first-class, and evaluated by code before the model chooses |
| Types accepted | skill, subagent, agent for the graph | any carrier (§7.2) |

**They are complementary, not rivals.** The fingerprint is a good *retrieval* view. It becomes a good *authority* view
only if what feeds it is checked. The integration needs no change to Symphony **(design)**:

- **Filter the inventory.** The capsule layer implements `CapabilityProvider` and returns descriptors only for
  `admitted` Declarations.
- **Supply the hash.** It sets `content_hash = decl_hash`. The extractor uses a provider-supplied hash when there is one
  (`extractor.py:151`).
- **Supply the I/O.** It fills inputs and outputs from `ports`. The extractor then skips model inference of I/O
  (`extractor.py:195-202`).
- **Keep the graph current.** It calls `SkillGraphUpdater` `add_skills`, `update_skills` and `delete_skills`
  (`interfaces/graph.py:14`) when a Standing moves.
- **Leave quality alone.** Symphony's quality results stay what they are: observations. The capsule layer may copy
  them into `use_outcome` Findings, and they never admit anything.

## 7.2 agent-core: ToolCard, PluginSpec and the binder

**ToolCard** carries four runtime flags: `exposure`, `parallel_safe`, `stateless` and `idempotent`
(`core/foundation/tool/base.py:83-118`). These are hints about execution, not a contract. A Declaration can *derive*
them **(design)**:

- `parallel_safe` is false if any effect writes or holds an exclusive resource;
- `idempotent` is false if any effect creates or emits.

The capsule layer sets the flags. The flags never set the Declaration.

**PluginSpec** is agent-core's bundle: id, name, description, prompt sections, tools, MCP servers, rails, skills and
metadata (`harness/schema/extension_spec.py:146-164`). It has no needs, effects, version or hash. It is the natural
**carrier** for a capsule body. The Declaration references it by `carrier.spec = PluginSpec`, and agent-core loads it
unchanged.

**The binder.** `apply_extension_hot` binds the parts by name, raises if a name is already bound, and undoes partial
binds in reverse order on failure (`harness/extension_binder.py:27-61`, `:64-73`, `:93-94`, `:113-116`). It checks no
hash. Its load records live in memory (`harness/deep_agent.py:314`; `harness/resources/extension_resolver.py:60-65`).

The consequences **(design)**:

- The capsule layer verifies `body[]` hashes before calling `apply_extension_hot`.
- It writes Bindings to its own durable store.
- Hashing inside the binder would close a check-then-load race. That is the one small agent-core change this report
  would ask for, and it is optional.

**SkillUseRail** already accepts an allow-list, `enabled_skills` (`harness/rails/skills/skill_use_rail.py:78`, `:95`,
`:255-259`). **That is where the offer is applied for skills, with no change.** Its own `max_skills` cap narrows by
keyword overlap with the query (`:99-104`, `:526-546`). That is an observational narrowing, and the offer replaces it.

**Skills at runtime.** A skill is `name`, `description` and `directory` (`core/single_agent/skills/skill_manager.py:11-21`).
The name comes from the directory and the description from `SKILL.md` (`skill_use_rail.py:207-221`).

## 7.3 Skills: SKILL.md, skillhub, jiuwenswarm

**skillhub** reviews each published version in two stages.

- **Machine review.**
  - Deterministic engines run first, then an LLM "semantic" engine
    (`marketplace/skill_review/engines/registry.py:10-15`).
  - Findings with high severity and a `block` recommendation reject the version.
  - The score is 100 minus penalties (`marketplace/skill_review/aggregation/review_aggregator.py:9-26`, `:169-185`).
  - The result is bound to the package bytes: if `artifact_sha256` changed during review, the result is discarded
    (`marketplace/plugins_market/services/skill_review.py:682-692`).
  - Machine review is off by default (`marketplace/plugins_market/core/config.py:541-544`).
- **Human moderation.** Self-moderation is forbidden, and approval is refused while machine review is running
  (`marketplace/plugins_market/services/plugin.py:2694-2704`, `:2721-2729`).
- Only `publish_success` is public (`marketplace/plugins_market/core/publish_result.py:39-43`).
- **Nothing is executed.** Review is static analysis plus a model.
- There are no declared effect or permission fields for skills.

**jiuwenswarm** evolves skills through an interrupt rail.

- A preflight validates the proposal, then either `auto_save` approves it or a human decides
  (`agent-core/openjiuwen/harness/rails/evolution/evolution_interrupt_rail.py:105-120`, `:116-117`).
- Its SkillDev pipeline runs evaluation cases with and without the skill before a user review. This comes from the
  survey reader; the stage file was not opened by the author of this report.

**What a capsule borrows from these.**

- From skillhub: review bound to bytes, separation of duties, and typed findings with a gate recommendation.
- From SkillDev: a with/without comparison.

**What they lack.**

- Executed acceptance checks written by someone other than the builder.
- Declared effects.
- Verdicts bound to a policy epoch.
- Any notion of a run using a specific hash.

## 7.4 MCP and A2A

**MCP.** An MCP tool has name, title, description, input and output schema, and annotations (`readOnlyHint`,
`destructiveHint`, `idempotentHint`, `openWorldHint`). All the annotations are optional
(`openjiuwen/agent-protocol/MCP/cpp-sdk/include/mcp/mcp_type.h:221-227`, `:291-299`).

agent-core's MCP client keeps only name, description and input schema
(`agent-core/openjiuwen/core/foundation/tool/mcp/client/sse_client.py:331-338`). The annotations and output schema
never reach the runtime. A capsule that wraps an MCP server therefore supplies `effects` and `ports` itself, and treats
the server's hints as, at most, input to the builder.

**A2A.** An A2A agent card lists skills (id, name, description, tags, examples, modes), capabilities, security schemes
and signatures (`openjiuwen/agent-protocol/A2A/cpp-sdk/include/types.h:511-520`, `:586-605`). agent-core's adapter
emits no skills and keeps only name and description when it reads a remote card
(`agent-core/openjiuwen/extensions/a2a/a2a_agentcard_adapter.py:33-45`, `:59-63`).

**Both are advertisements**: what a service says about itself, for discovery. A Declaration is a commitment that
someone else checks. A capsule can *wrap* an MCP server or an A2A agent, with the card as body metadata. It never
treats the card as evidence.

## 7.5 ScienceDiscovery's versioned skill library

- **Library versions are immutable.** Each has a content hash, a parent, and `rollbackOfVersionId`
  (`sciencediscovery/packages/schema/src/skills.ts:336-367`).
- **Evaluation is an opaque stored record** (`:361`). The docs say it is not used to gate publication; this comes from
  the survey reader, and the docs were not opened by the author of this report.
- **`allowed-tools` is kept but "not enforced by this runtime"** (`packages/specialist/src/skills.ts:576-583`).
- **Availability is "Server-computed … never trusted from Skill frontmatter"** (`packages/schema/src/skills.ts:80`).
  This is the same instinct as rule 2 here.

A capsule library could sit on this storage model. What it adds is:

- the Verdict (an evaluation that gates);
- `enforced` versus `declared` claims (so that `allowed-tools` either becomes `effects.scope` in a sandbox or is marked
  `declared`);
- Bindings.

## 7.6 AI4Research today

The old harness was already partly declarative. The new schema keeps what worked and fixes four gaps.

**What works today.**

- **A code filter runs before the model.** Planning selects capsules in three steps:
  1. A code filter checks types, effects in both directions (a missing requested effect *and* an unrequested active
     effect both exclude), network policy, verification presence and trust class
     (`elastic_planner.py:4553-4648`).
  2. A model binds each plan step, seeing full catalog rows for eligible capsules (`:4678-4724`).
  3. A separate fit review follows (`:5685`), with at most one repair (`:4934`, `:4949`).
- **The freeze** admits only `stable` capsules (`execution_authority.py:55-56`) and rejects any capsule changed during
  planning (`:81-94`).

**The four gaps.**

1. **No predicate parity.** The filter never reads preconditions. Dispatch checks four fixed precondition kinds against
   the task envelope (`capability_capsules.py:1220-1242`).
2. **A lenient default.** A capsule with no status is treated as stable (`capability_admission.py:14`).
3. **Prose invariants.** `cap.research-retrieval.yaml` states "Every evidence row resolves to a source and a verified
   span in that source's extract" as prose (`harness/config/capability-capsules/cap.research-retrieval.yaml:52-56`).
   No code evaluates it.
4. **Checks named, not bound.** Its verification lists named self-checks and an external verifier preference
   (`:90-102`). Nothing binds a runner hash or says who wrote the checks.

## 7.7 Is a capsule a skill?

**No.** A skill is one possible **body** of a capsule. It is the "execution fragment" in the slide's own words (note 45
§3).

- A capsule *contains* a skill when its `carrier` is a `SkillSpec` and its `body[]` lists the skill's files by hash.
- It *overlaps* with the skill only in name and description, which become `summary`.

Everything else in a capsule consists of records *about* the skill that the skill cannot write. So a capsule is not a
bigger skill. It is a skill (or tool, MCP server, subagent, template) plus the records of what was promised, what was
checked, where it stands and where it was used.

---

# 8. Integration: how each part fits, and what each team gets

## 8.1 Where it sits

![Figure 3. Position in openJiuwen and in the sprint.](figures/F3.png)

## 8.2 agent-core and Symphony

The capsule layer sits beside Symphony and in front of the binder. It needs no required agent-core change (§7.1,
§7.2). One optional change would help: hash verification inside the binder. The layer is *aligned* with openJiuwen's
architecture in the supervisor's sense. It uses the platform's own seams:

- `CapabilityProvider`
- `SkillGraphUpdater`
- `PluginSpec`
- `SkillUseRail.enabled_skills`

## 8.3 RSI

**What CC gives RSI.**

- A precise target: a Declaration format, and a gate whose reasons are typed.
- Repair tickets localised by a failed check or a drift contract (§5.11).
- Build requests only on recurrence (§5.9).
- Protection from being retired by an unmeasured judge (§5.4).
- Lineage, so that one bad capsule does not force a library-wide rollback (§5.5).

agent-core's RSI module already records a search tree whose nodes carry `parent_id`, `adopted`, `score`,
`snapshot_artifact_id` and `changes` (`agent-core/openjiuwen/rsi/schema.py:97-111`). An adopted node's snapshot maps
naturally to a candidate Declaration with `lineage.parent` **(design)**.

**What CC asks of RSI.**

- Emit Declarations, not bare artifacts.
- Record `context_capsules` and `diagnosis_inputs`.
- Never author the acceptance checks for its own candidates.
- Keep checker internals out of what the builder sees (§5.12).

## 8.4 Verification

**What CC demands.** This is the largest set of demands on any team.

- Held-out acceptance suites per capability, written before or independently of the body (§5.1).
- Runners that live outside capsule write scopes, with evidence emitted by the harness (§5.12).
- **Measured error for every judge it supplies** (§5.4).
- Parity fixtures for predicates (§5.3).
- A composition screener and its thresholds (§5.6).
- Audits that compare runs with declared effects (§5.14).

**What verification gets.**

- A place to record all of this that the pipeline actually reads.
- Checks that are tied to exact hashes, so a pass cannot be reused for a changed artifact.
- A system-level view from Bindings: which hashes served which claims in each sprint. That is the per-sprint
  capability- and system-level check the supervisor described, with a data source behind it.

## 8.5 Routing

Routing picks models. CC never does. The only field routing reads is `needs.model`: tool calling, minimum context and
modalities. Those are constraints a model must meet for the capsule to work. It exists because the same skill's pass
rate varied from 43.1% to 71.1% across models in CoEvoSkills' transfer table (Table 3, p9).

Routing also gets Bindings, which record which model served each step (via `choice_ref`), for its own analysis.

## 8.6 The ownership picture

![Figure 4. Three loops and their owners.](figures/F4.png)

Ownership is for the teams to agree together, because the capsule touches every team. The proposal above follows one
rule: **nobody owns the check on their own output.**

- RSI builds, but does not admit.
- Verification checks, but does not choose.
- The pipeline uses, but does not grade.

---

# 9. Composites, their ceiling, and which stages may become capsules

## 9.1 Composites

A composite is a capsule whose body is `members[]` (pinned hashes) plus `wiring[]`. The gate checks it in four ways:

1. **Types.** Every wire connects an output to an input of a compatible type (ABC's C1).
2. **Covered effects.** The composite's own `needs` and `changes` cover the union of its members'. This union is
   `derived`: code computes it, and the builder never writes it (SCHEMA §3.1).
3. **Budget conservation.** The members' budgets sum to no more than the composite's (Agent Contracts, p10).
4. **Permitted versus prohibited.** No member's permitted effect is an invariant another member forbids (ABC's C3).

Members keep their own Verdicts. A composite's Verdict lists them. Revising a member produces a new member hash, so
the composite must be re-declared. This is deliberate. A composite pins exactly what was checked.

## 9.2 The ceiling

The supervisor said AI4Research is not a capsule (note 46 §2), and note 46 §4 left open where the line falls. This
report proposes a test **(design)**:

> **A capsule is something the freeze binds to one plan node. Anything that must itself plan, freeze, admit, schedule
> or judge capsules is above the ceiling.**

Under this test:

- A team of agents working inside one node can be a capsule.
- A sub-pipeline that re-plans across nodes cannot.
- Composites may nest, but the freeze sees one node → one hash. A composite executes entirely within its node, under
  its own budget. It does not re-enter planning.

## 9.3 Stages that could become capsules later, and stages that must not

| Pipeline stage | Capsule? | Why |
|---|---|---|
| Operators: retrieval, source validation, synthesis, experiment runs, report drafting | yes, now | These are what capsules are for |
| Intake parsers and normalisers (document ingestion) | could, later | Typed input to typed output; no authority over other capsules |
| Delivery renderers (formatting claims) | could, later | They transform delivered artifacts; the claims themselves are fixed before they run |
| Intent extraction | only as a helper that the stage calls, not as the stage | Intent defines what "done" means for the sprint. A capsule that could be swapped by the planner would be choosing its own acceptance criteria |
| Requirement compilation | no | It produces the requirements that the filter and freeze check against |
| Planning | no | It selects capsules. A capsule that plans would select itself |
| Freeze, scheduling, dispatch | no | These are the authority the Binding records. §5.12: the checker must be out of reach |
| In-run gates that judge capsule output | no; their *checks* are runners owned by verification, referenced by hash | A gate that could be revised by RSI is a checker within reach |
| Admission gate, librarian, invalidator, screener, verifiers | never | They write the records. CC uses them as tools (supervisor, 2026-09-21) |

---

# 10. Spatiotemporal composability: add, replace, revert, remove

Cordis requires components to be "addable, replaceable, revertible and removable without breaking dependents" (§5.15).
The schema supports each operation as follows.

| Operation | How the schema does it | What Cordis guarantees at runtime, if the carrier follows it | Where it cannot |
|---|---|---|---|
| **Add** | A new Declaration is admitted, and its `injects` must be satisfied by admitted providers or be optional | Providers activate before consumers (Thm 70, p47) | A dependency cycle leaves capsules inactive (p74). The gate rejects cycles among `injects`/`provides` **(design)** |
| **Replace** (revise) | New hash, new Verdict. The replacement-compatibility check covers dependents' ports and injected keys; a new write, delete or emission forces re-screening. The Standing moves atomically | Replacement is by provider identity: dependents reload when their provider changes (p63) | Frozen sprints keep the old hash on purpose. A running operator is never swapped mid-node |
| **Revert** | The Standing moves back to `previous[0]`, and needs a valid Verdict under the current epoch | Confluence: add, remove, replace and undo reach the same state as loading the final set from scratch (Thm 80, p54–55) | Emissions made while the newer version ran are not undone (p47). The `emission` policy decides what was allowed |
| **Remove** | Two steps: stop offering (`deprecated`); retire only when no admitted capsule injects a key it alone provides | Two-step unload with a guard (p36; Alg. 5, p62–63) | Cordis does not check that an inverse is correct (p59). `inverse` reversibility is `declared` unless a check exercises it |

![Figure 5. Removing a provider without breaking dependents.](figures/F5.png)

**What the schema adds to Cordis.** Cordis has no versioning or structural typing of keys, and the paper says a
unified dependency model "remains an open problem" (p75–76). `injects[].interface_version_range` and
`provides[].interface_version` fill exactly that gap.

**What it cannot add.**

- Cordis's theorems hold only for effects routed through its context (p31, p47). A capsule body that writes files
  outside its declared scope is outside the theorem. It is caught only by the sandbox (`enforced`) or the audit
  (`audited`).
- Cordis does not sandbox (p73).

---

# 11. Composition screening

Capsules are **not** certified as safe together. Admission is per Declaration; composition risk is per set (§5.6).

**What the screener reads.** The schema supplies what SkillFuzz had to extract with a model:

- the modifies set: `effects[]` with resource keys and operations;
- invariants: `changes.invariants`;
- shared services and whether they are commutative: `injects`/`provides`;
- domain scope: `applies_to.domain_scope`;
- a completeness signal: `coverage.undeclared_notes`.

**Two cheap passes by code, before any model.**

1. **Resource overlap.** Two capsules that write the same resource key, or one that deletes what another reads, are
   flagged.
2. **Invariant clash.** One capsule's effect violates another's invariant. For example: "inputs are read-only" versus
   a write to that input.

These are the declarable conflicts. SkillDAG treated them as observable only (§5.8), and here they need no
observation. The model-based search then runs over sets ranked by these flags, as SkillFuzz's seed ranking does (p5).

**How findings are recorded and used.**

![Figure 6. Composition screening and where its findings go.](figures/F6.png)

**Rules for using findings.**

- A Finding's `status` distinguishes plan-level flags from execution-confirmed ones. SkillFuzz confirmed 80.6% of its
  top flags (Table II, p7), which leaves real false positives.
- `block_set` needs confirmation or review **(design)**.
- The screener's thresholds are uncalibrated (SkillFuzz p10). They go into `producer.thresholds` so that each finding
  can be re-read later against better calibration.

---

# 12. Worked example: `research.retrieval`

A realistic AI4Research capability: gather sources for a research question and land a provenance-complete source
pack. Today it exists as `cap.research-retrieval.yaml` (§7.6). What follows is how it *would* look and move in the new
system. Hashes are abbreviated. The composition finding in step 2 is **illustrative**, not observed.

## 12.1 The Declaration

```yaml
identity:
  name: research.retrieval
  version_label: "2.0"
  kind: skill
  carrier: {spec: PluginSpec, ref: plugins/research-retrieval}   # skill folder + fetch MCP server
  body:
    - {path: skills/research-retrieval/SKILL.md, sha256: 9f1c…}
    - {path: skills/research-retrieval/fetch.py, sha256: 41aa…}
    - {path: mcp/fetch-server.json,              sha256: c07e…}
  summary: "Find and fetch real sources for one research question; write sources.jsonl, evidence.jsonl and raw extracts. Does not summarise or judge relevance."
  lineage: {parent: null, builder: person:muk, build_trigger: null, context_capsules: [], diagnosis_inputs: []}
ports:
  inputs:
    - {name: question, artifact_type: artifact.research_question, required: true, schema_ref: schemas/question.v1}
    - {name: scope_hints, artifact_type: artifact.scope_hints, required: false, schema_ref: schemas/scope.v1}
  outputs:
    - {name: source_pack, artifact_type: artifact.source_pack, schema_ref: schemas/source_pack.v1, check_id: pack_schema}
needs:
  when:
    - {id: has_question, predicate: "present(artifact.research_question)", max_age_s: 0, on_unknown: defer, parity_check: parity_has_question}
    - {id: budget_ok, predicate: "budget.remaining.cost_usd >= 2.0", max_age_s: 30, on_unknown: defer, parity_check: parity_budget}
  injects: [{service_key: svc.search_provider, interface_version_range: ">=1 <2"}]
  resources: [{resource_key: fs.sprint_artifacts, mode: write}]
  secrets: [{ref: secret.search_api_key}]
  network: {allowlist: [search.provider.example, "*.arxiv.org", "*.doi.org"]}
  model: {tool_calling: true, min_context: 32000}
  applies_to: {task_types: [research, knowledge-extraction], domain_scope: "literature and web sources"}
  external:
    - {kind: package, value: "httpx>=0.27,<0.29", role: operational}
    - {kind: api, value: "https://search.provider.example/v1/search", role: operational}
changes:
  effects:
    - {id: write_pack, resource_key: fs.sprint_artifacts, op: write, scope: "artifacts/{sprint}/research/**", reversibility: scoped, risk: {severity: low, blast_radius: low, irreversibility: low}}
    - {id: query_out, resource_key: net.search_provider, op: emit, scope: "HTTPS GET to allowlist", reversibility: emission, policy: withhold_until_freeze_ok, risk: {severity: med, blast_radius: low, irreversibility: high}}
  provides: []
  invariants:
    - {id: extracts_are_fetched, statement: "Extract files contain fetched bytes, never model-authored text", check_id: extract_bytes_match}
    - {id: evidence_resolves, statement: "Every evidence row resolves to a span in its source's extract", check_id: span_resolves}
    - {id: question_read_only, statement: "The question artifact is not modified"}
guarantees:
  checks:
    - {id: pack_schema, kind: output_schema, runner: {ref: verif/pack_schema.py, sha256: 77b2…}, author: team:verification, written_before_body: true, held_out: false, signal_source: harness, owner: external, judge: deterministic, assurance: tested}
    - {id: span_resolves, kind: invariant, runner: {ref: verif/span_check.py, sha256: e3d9…}, author: team:verification, written_before_body: true, held_out: false, signal_source: harness, owner: external, judge: deterministic, assurance: tested}
    - {id: extract_bytes_match, kind: invariant, runner: {ref: verif/fetch_log_compare.py, sha256: 5a10…}, author: team:verification, written_before_body: true, held_out: false, signal_source: harness, owner: external, judge: deterministic, assurance: audited}
    - {id: golden_questions, kind: eval_suite, runner: {ref: verif/retrieval_suite.py, sha256: 0c4f…}, author: team:verification, written_before_body: true, held_out: true, signal_source: harness, owner: external, judge: model, assurance: tested}
    - {id: parity_has_question, kind: property_test, runner: {ref: verif/parity/has_question.py, sha256: 1b2b…}, author: team:verification, written_before_body: false, held_out: false, signal_source: harness, owner: external, judge: deterministic, assurance: tested}
    - {id: parity_budget, kind: property_test, runner: {ref: verif/parity/budget.py, sha256: 8e8e…}, author: team:verification, written_before_body: false, held_out: false, signal_source: harness, owner: external, judge: deterministic, assurance: tested}
  acceptance: [pack_schema, span_resolves, golden_questions, parity_has_question, parity_budget]
  evals: [{suite_ref: verif/retrieval_suite.py, sha256: 0c4f…, metric: "fraction of questions with ≥3 resolvable sources", threshold: 0.8, held_out: true}]
budget:
  per_call: {cost_usd: 2.0, wall_s: 900, tool_calls: 60}
  enforcement: {cost_usd: between_calls, wall_s: hard, tool_calls: hard}
  on_exhaust: return_partial
  context_cost_tokens: 180
coverage:
  undeclared_notes: "Relevance of sources is not checked here; that is source-validation's job."
```

Points to notice:

- **The two prose invariants from today's manifest are now bound to checks.** They are `span_resolves` and
  `extract_bytes_match`.
- **`extract_bytes_match` compares against the harness's fetch log**, so its `signal_source` is `harness` and not the
  capsule's own claim (§5.12).
- **The third invariant has no check, and says so.** Its assurance is `declared`.
- **The relevance judge inside `golden_questions` is a model.** The Verdict must therefore record its measured error.

## 12.2 Admission

1. **Vocabulary.** Every name used is in the vocabulary: `artifact.research_question`, `fs.sprint_artifacts`,
   `svc.search_provider`, and the rest.
2. **Hashes.** The body hashes match.
3. **Structure.**
   - Every runner lives in verification's repository, outside `artifacts/{sprint}/research/**`.
   - Every acceptance check has `signal_source: harness`.
   - `svc.search_provider` is provided by an admitted capsule, `provider.search.v1`.
4. **Sandbox run.** The sandbox allows writes only under `artifacts/{sprint}/research/**` and network only to the
   allowlist. The acceptance checks run on a held-out set of questions. One attempted write to `/tmp/cache` fails the
   first run with `EFFECT_OUT_OF_SCOPE`. The builder moves the cache into scope and re-declares, which produces a new
   hash, and the run passes.
5. **Screening against likely partners.** The partners are `research.source_validation`, `guard.secret_leak` and
   `report.draft`.
   - Code pass: no shared write keys. `report.draft` reads `artifact.source_pack`, which is an ordinary data edge.
   - The model pass flags `{research.retrieval, report.draft}`: the plan drifts toward drafting text into the extracts
     directory (illustrative). The invariant clash check matches it against `extracts_are_fetched`, and a sandbox
     confirmation run shows the drift.
   - The Finding gets `action: block_set` for co-activation *in the same node*. Being on different nodes, connected by a
     data edge, stays allowed.
6. **Set-level value.** The slot's held-out replay does not fall.
7. **Verdict.** `ADMIT`, with:
   - `checks_run` for the five acceptance checks;
   - `verifiers: [{id: relevance-judge, version: 3, measured_error: {false_accept: 0.04, false_reject: 0.11, n: 200,
     measured_on: "defect-injected packs", date: 2026-09-20}}]` (illustrative values);
   - `screening: [F-0192]`;
   - `invalidated_by: [dep:provider.search.v1, policy_epoch, verifier:relevance-judge]`.
8. **Standing.** The librarian sets `research.retrieval → 7c2e…`, `admitted`, reason `ADMITTED`.
9. **Symphony.** It receives an `add_skills` mutation. The capsule layer's `CapabilityProvider` now returns this
   descriptor with `content_hash = 7c2e…` and I/O taken from `ports`.

## 12.3 Offered and bound in a sprint

1. **Offer.** Sprint S-311 plans a node "gather sources" that consumes `artifact.research_question`. At the choice
   point, the filter evaluates the predicates:
   - `has_question`: true.
   - `budget_ok`: true. Remaining cost is 5.40, read 3 s ago.
   - `network`: the sprint's network zone permits the allowlist.
   - `applies_to`: research.

   So `research.retrieval` is offered, alongside one other retrieval capsule. The chooser sees two summaries and their
   ports: 180 + 210 tokens.
2. **Bind.** The chooser binds `research.retrieval`.
3. **Freeze.** The freeze writes a Binding:

```yaml
sprint_id: S-311
node_id: n4.gather_sources
decl_hash: 7c2e…
verdict_ref: V-0457
offer_hash: 2d9a…
choice_ref: call:planner/8841
predicates:
  - {id: has_question, value: true, context_sha256: aa01…}
  - {id: budget_ok, value: true, context_sha256: aa01…}
resolved:
  - {service_key: svc.search_provider, provider_decl_hash: 51f0…}
findings_consulted: [F-0192]    # report.draft is on node n6, not co-activated
step_identity: h(7c2e…, sha(question), {k(n2), k(n3)})
prev_hash: …
```

4. **Dispatch.** Dispatch re-runs both predicates on the live context. `budget_ok` is still true (3.10 remaining after
   an earlier node), so the operator runs.
   - The query emissions are allowed because the policy is `withhold_until_freeze_ok` and the freeze succeeded.
   - agent-core loads the verified body through `apply_extension_hot`, and the skill is added to
     `SkillUseRail.enabled_skills` for this node.
5. **What the run records.**
   - Output artifact hashes.
   - The sandbox's filesystem and network logs.
   - The fetch log.

   The audit compares them against `effects`. There are no writes outside scope and every host is on the allowlist.
   `extract_bytes_match` passes, and a `use_outcome` Finding is written.
6. **Delivery.** Claims delivered at the end of S-311 carry the step identities they depend on.

## 12.4 Revised

Two weeks later the drift probe hits `https://search.provider.example/v1/search` and gets a 301 to `/v2/search`.

1. **Drift Finding.** The probe writes `drift` Finding F-0240, and the librarian sets `research.retrieval` to
   `suspect`, reason `SUSPECT_DRIFT`.
   - Sprints already frozen keep running on `7c2e…`.
   - New sprints are not offered it. Their offer holds the other retrieval capsule, or is empty, in which case a `gap`
     Finding opens.
2. **Repair ticket.** RSI receives it: the failed contract `external[api]`, the old and new values, and the evidence.
   It returns Declaration `b913…` with `lineage.parent: 7c2e…`, `context_capsules: [7c2e…]`, the updated `external`,
   and a changed `fetch.py` hash.
3. **Admission of the revision.**
   - The gate re-runs acceptance.
   - Replacement compatibility holds: same output port and type; no new write, delete or emission.
   - The Finding about `{7c2e…, report.draft}` is voided for the new hash, and a re-screen is queued. Until it returns,
     the policy admits with the block kept provisionally.
   - Verdict: ADMIT.
4. **Standing.** `current: b913…`, `previous: [7c2e…]`, reason `ADMITTED`. Symphony gets `update_skills`.

## 12.5 Revoked

The audit of sprint S-340 finds that `b913…` put the API key in the query string, i.e. in URLs that reach third-party
logs. This is an `audit_violation` against the declared use of `secret.search_api_key`.

1. **Revoke.** The librarian sets `revoked`, reason `REVOKED_SECURITY`.
2. **Find the affected work.** The invalidator lists every Binding with `decl_hash: b913…`: 14 nodes in 6 sprints
   (illustrative). Claims whose step identities descend from those nodes are marked `stale`, not deleted.
3. **Lineage.** Any admitted capsule with `b913…` in `context_capsules` becomes `suspect` (none in this case).
4. **Revert.** The Standing would revert to `previous[0] = 7c2e…`, but that version is `suspect` for drift. The revert is
   refused, and the offer for "gather sources" falls back to the other retrieval capsule.
5. **Gap.** Where that capsule is not applicable, a `gap` Finding opens. By §5.9 it reaches RSI only if it recurs.

![Figure 7. research.retrieval over time.](figures/F7.png)

---

# 13. What CC deliberately does not do

**For RSI.**

- CC does not decide what to build or how to build it.
- It does not search, mutate or optimise.
- It does not score candidates beyond the gate's typed checks.
- It does not store RSI's search tree; it keeps only `lineage` pointers.
- It never trains or changes model weights.

**For verification.**

- CC does not write verifiers, suites, parity fixtures or screeners.
- It does not measure judge error.
- It does not choose thresholds for verification.
- It *requires* these things, records them, and makes the pipeline read them.
- CC is not a verifier and does not contain one (supervisor, 2026-09-21).

**For routing.**

- CC never picks, ranks or excludes a model.
- `needs.model` is a constraint that routing may read.
- If no model meets it, the capsule is not offered. That is the filter acting on the capsule, not a routing decision.

**For the pipeline.**

- CC does not plan.
- It does not order nodes.
- It does not judge whether delivered claims are true. Claims carry step identities so that they can be invalidated;
  judging them is the pipeline's in-run gates and verification's job.

---

# 14. The assignment's requirements, a to g

**a) Function.**

- Make every capability's needs, effects, guarantees and budget explicit, and check them before use.
- Record who checked what, which exact version ran where, and what was learned afterwards.
- Why: §6 argues it in full. In short, observation-only libraries fail silently (§5.1, §5.4, §5.5).

**b) Architecture.** Five records separated by writer (§1), seven Declaration sections (SCHEMA §3.1), and nine
mechanisms, all code except the chooser, the screener's search and model judges (SCHEMA §4).

**c) Position.**

- In the sprint: the gate runs before any sprint. The filter runs at planning. Bindings are written at the freeze. The
  dispatch check runs at dispatch. The audit runs after operators. The invalidator runs after delivery.
- In openJiuwen: a capsule layer beside Symphony and in front of agent-core's binder (§8.1).

**d) Dependencies.**

- agent-core: `PluginSpec`, `apply_extension_hot`, `SkillUseRail.enabled_skills`.
- Symphony: `CapabilityProvider`, `SkillGraphUpdater`.
- A sandbox able to enforce file and network scopes. None was found in the code read for this report; it is a
  dependency to settle.
- A vocabulary.
- Verification's runners, suites and screener.
- RSI's Declarations.
- Durable storage for the ledgers.

**e) Similar designs.** §7:

- Symphony's fingerprint
- ToolCard and PluginSpec
- skillhub's review
- ScienceDiscovery's versioned library
- MCP and A2A cards
- today's AI4Research capsules

The closest in spirit are skillhub (review bound to bytes) and ScienceDiscovery (immutable versions, availability
never trusted from frontmatter). None of them has executed acceptance checks by a non-builder, declared effects with
assurance levels, or run-level Bindings.

**f) Advantages.** Each team gets something it cannot get today (§8):

- RSI gets typed rejections, repair tickets and protection from unmeasured judges.
- Verification gets a place its checks are enforced.
- The pipeline gets smaller offers, typed deferral and exact invalidation.
- Routing gets explicit constraints.

**g) Feasibility.** Every part exists somewhere:

- hash-bound review (skillhub);
- immutable versioned libraries with rollback (ScienceDiscovery);
- a code filter and freeze (AI4Research today);
- provider and graph-update seams (Symphony);
- hot bind and unbind (agent-core).

The new pieces are:

- the vocabulary;
- the ledgers;
- sandbox enforcement of effect scopes;
- measured judge error.

Ownership is for the teams to decide together.

---

# 15. What the schema does not claim

- **It does not claim that declared capsules are correct.** It claims that what was checked is recorded, and that what
  was not checked is labelled.
- **It does not claim safety in combination.** Screening reduces composition risk. Nothing certifies a set.
- **It does not undo emissions.** It only controls when they are allowed.
- **It does not make token budgets hard.**
- **It does not verify Cordis-style inverses** unless a check exercises them.
- **The design has not been measured as a whole.**
  - The numbers in §5 are the papers' own, in their own narrow setups.
  - None of them tested this design.
  - The worked example's findings, hashes and error rates are illustrative.
- **It does not claim that a model judge is trustworthy.** It claims that a judge with no measured error cannot admit
  above the lowest risk class **(design)**.
- **It does not settle ownership, the ceiling, or the default thresholds.** The ceiling is proposed (§9.2). The
  recurrence threshold of 2, the overlap policy and the risk ceilings are all **(design)**.
- **It does not describe a system that exists.** The capsule layer is a proposal. Only the code cited as "today" and
  the openJiuwen sources exist.

---

# 16. Topic register

| Topic | Where |
|---|---|
| The schema on one screen | §1; SCHEMA §1 |
| Definitions | §2; SCHEMA §2 |
| Supervisor's rulings; the slide components mapped | §3 |
| Tool catalogue; why the papers are placed in §5 | §4 |
| Paper-by-paper motivation (21 papers) | §5.1–§5.16 |
| Declarative versus observational; limits of declaration | §6 |
| Symphony fingerprint versus Declaration | §7.1 |
| ToolCard, PluginSpec, the binder, SkillUseRail | §7.2 |
| Skills: skillhub, jiuwenswarm | §7.3 |
| MCP and A2A | §7.4 |
| ScienceDiscovery | §7.5 |
| AI4Research today | §7.6 |
| Is a capsule a skill? | §7.7 |
| Integration with agent-core, Symphony, RSI, verification, routing | §8 |
| Ownership loops | §8.6 |
| Composites and their ceiling; which stages could or must not be capsules | §9 |
| Spatiotemporal composability (Cordis) | §10, §5.15 |
| Composition screening | §11, §5.6 |
| Worked example, end to end | §12 |
| What CC does not do | §13 |
| Requirements a–g | §14 |
| What the schema does not claim | §15 |
| Evidence ledger | READ-LOG.md |

**Considered and left out:**

| Topic | Why it was left out |
|---|---|
| The slide's formal layer (SysML v2 → TypeScript → JSON Schema → Knowledge Graph) | The slides are prior thinking (note 46). The schema needs a validated serialisation; which chain produces it is an implementation choice |
| The five capsule kinds on the slide (Research, Compliance, Data, Report, Tool) | They are unglossed names (note 45 §6.3). `kind` here is a loading distinction (tool, skill, …); domain grouping is `slot` |
| Ground Truth as a named component | Verified state appears here as Bindings and Findings. A separate Ground Truth store belongs to the pipeline, not to the capsule schema |
| Signing and key management for ledgers | Needed in production (RelAIBuild's machine-local HMAC is forgeable, p12, p34), but it does not change the schema's shape |
| A numeric trust score per capsule | Rejected on evidence: compensatory scores bypass hard conditions (§5.7) |
| Cost and economics of admission | No paper here measures admission cost for this design; Library Drift's call counts (p5) are for a different loop |
| Papers in `capsule-openjiuwen/papers/` beyond the 21 in the brief | Not read in full in this pass, so not cited |
| jiuwenswarm SkillDev stage internals and ScienceDiscovery's design docs | Reported by the survey reader; only the lines cited in §7.3 and §7.5 were checked by the author, and the rest is flagged there |
