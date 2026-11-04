# 13 — Capsules: roadmap and open questions

The "how to do better" half of the capsule deliverable, framed as **proposed
next steps** and **questions for discussion** rather than defect findings.
Written 2026-09-10 by the capability-capsule panel (pts/9).

Supersedes the framing (not the evidence) of Part A in
`10-doing-better-and-toolchain.md`. Every claim here was verified by running a
command against the checkout at `b0bf165f9`; `10` retains the raw command
trail.

Companion digests: `11-` (architecture doc, English), `12-` (ecosystem doc,
English).

> **Adversarially reviewed 2026-09-10.** An independent agent with no access to
> this panel's reasoning re-derived every claim from the repository and attacked
> the four headline items (§0, R5, R6, R9). It confirmed 7 errors and 11
> overreaches, all corrected in place and flagged inline with ⚠. Every count,
> every "not implemented" claim, and R3/R7/R9's figures survived attack
> unchanged — those are safe to publish. Corrections are marked so the report
> author can see what moved and why.

---

## 0. The reconciliation table — read this first

The single most useful artifact for the report. The design docs and the shipped
schema describe the same intent in **two incompatible vocabularies**, and no
document in the repo maps between them. Here is the map:

| `CAPSULE_ARCHITECTURE.md` (design) | `capability-capsule.v1.draft.json` (shipped) | Status |
|---|---|---|
| `apiVersion: capsule/v1`, `kind: Capsule` | `capability_capsule_id`, `capsule_kind` | renamed; kinds differ in meaning |
| `interface` (input/output/errors) | `contract` (inputs/outputs/preconditions/postconditions/invariants) | **shipped is richer** — pre/post/invariants were promoted out of `verification` |
| `permissions` (resources/denies) | `effects` (read/write/execute/network/cost/risk) | reframed: *effects declared* rather than *permissions granted*. `denies` survives only as **free-text per-axis nullification** — see note below |
| `interface.errors[]` (code/message/**`recoverable`**) | — absent — | **gap**: no error contract at all; `recoverable` appears in 0 of 85 manifests [verified] |
| `guarantees` (timing/idempotency/side_effects/bounds) | — mostly absent — | **gap**: no declared timing, no idempotency flag, no resource bounds |
| `risks` (cost/privacy/availability) | `effects.cost`, `effects.risk` (free text) | downgraded from structured to prose |
| `verification` (pre/post/invariants/test_cases) | `verification` (self_check/external_verifier/pass_conditions) | both exist; contents redistributed |
| `evolution` (compatibility/deprecation/constraints) | — absent — | **gap**: the E in SCARE has no shipped surface |
| — absent — | `applicability` (task_types/positive/negative signals) | **shipped-only**: how selection actually happens |
| — absent — | `composition` (consumes/produces/compatible_with/incompatible_with/requires_after) | **shipped-only**: explicit composition edges |
| — absent — | `operator_compatibility` (preferred/forbidden) | **shipped-only**: who may run it |
| — absent — | `bindings`, `provenance` | **shipped-only**, both schema-required |
| — absent — | `implementation` (trust_class/entrypoint) | **not in the schema at all** — survives via `additionalProperties: true`, present in only **21 of 80** registered manifests [verified] |

**The headline for the report:** the shipped format is *not* a degraded version
of the design — it is a **different, more operational design**. It dropped the
formal-verification and self-description apparatus (`guarantees`, `evolution`,
`denies`) and added the things a real scheduler needs (`applicability`,
`operator_compatibility`, `bindings`, `provenance`). That is a defensible
engineering trade, and saying so plainly is stronger than either praising the
vision or criticising the implementation.

**Four genuinely missing pieces** form the natural roadmap: **declared
timing/idempotency**, a **structured `denies` list**, the **evolution
contract**, and — the one easiest to overlook — an **error contract**.

⚠ **Precision on `denies`.** An earlier draft of this note claimed `denies` had
"no shipped equivalent". That is falsifiable in one grep and was wrong.
`capsule_composition.py:38` defines
`_NO_EFFECT_TOKENS = {"", "none", "none by default", "no network", "disabled", "forbidden"}`
and uses it to drop an effect axis from a capsule's effect set; **26 of 85
manifests** actually carry such a token [verified]. The supportable claim is
narrower: there is no *structured, per-resource-type* denial list — only
free-text per-axis nullification. That is still a real weakness (it is not
diffable, and "none by default" is a default, not a renunciation), but state it
that way.

⚠ **The error contract is the gap most likely to be missed.** The shipped
`contract` block has properties `inputs / outputs / preconditions /
postconditions / invariants` and **no error field whatsoever** [verified].
`11-…` §3.1 calls `recoverable` the thing "that lets a scheduler decide to
retry without asking a model", and §9 makes the Fallback combinator depend on
declared error codes. So the missing error contract is not cosmetic — it is
load-bearing for two other designed features.

---

## 1. Proposed roadmap

Ordered by (impact ÷ effort). Effort estimates are the panel's judgement, not
the repo's — mark them as such if they go in the deliverable.

### R1. Reconcile the design docs with the shipped schema
**Effort: S (hours).  Impact: high.**
Either mark `CAPSULE_ARCHITECTURE.md` §2 as historical design rationale — the
README already does exactly this for its own pipeline section, so the precedent
and the wording exist — or publish the mapping table above. Today a newcomer
reading the flagship design doc will author a capsule the loader rejects.
Cheapest high-value fix available.

### R2. Add a registry ↔ documentation consistency check
**Effort: S (a ~20-line script + CI hook).  Impact: medium-high.**

Three independent drift examples, all verified, all catchable by one check:

**(a) A live route names an unregistered capsule.**
`feature_parity_routes.v1.json` maps the `/paper-draft` route (coverage
`partial`) to `solar_capability: cap.research-report-draft`. That id appears
**0 times** in the registry [verified] and therefore can never be admitted.
This also settles Q3 below — see the note there.

**(b) One route, three different answers.** For `/ask`:

| Source | Says |
|---|---|
| `autosci-workflow-map.md` | `cap.research-knowledge-query` |
| `feature_parity_routes.v1.json` (live) | `cap.research-memory-update` |
| `phase2-capsule-report.md:111` | *"Should `cap.research-knowledge-query` be added for `/ask` answer-only mode? — Not in Phase 2 deliverables."* |

`cap.research-knowledge-query` exists in exactly 3 files, all under
`docs/integrations/autosci/`, and in neither the registry nor on disk
[verified]. **Framing correction:** this is not *undetected* drift — the phase-2
report shows the capsule was **deliberately deferred**. The defect is that
`autosci-workflow-map.md` still renders a deferred capsule as an active
mapping, and that three artifacts disagree about one route.

**(c) The registry contains a dangling schema reference to itself.**
Four entries carry `schema_ref: draft/capability-capsule.v1.draft.json`,
missing the `schemas/` prefix, which resolves from neither `harness/` nor
`harness/config/` [verified]:
`cap.understand-anything-{chat,domain-analysis,knowledge-graph,tour}-builder`.
All four are `draft` status, so R3's arithmetic is unaffected — but a broken
path *inside the file that is the admission gate* is the most persuasive
possible argument for this check. **Found by adversarial review, not by either
panel's original pass.**

### R3. Promote the schema out of `draft`, or make the status honest
**Effort: M.  Impact: high (governance).**
74 of 80 registered capsules are `status: stable` while every one of them
carries `schema_ref: schemas/draft/capability-capsule.v1.draft.json`, and the
governing ADR is `Status: Draft` [verified]. Instance stability is being
asserted above contract stability; if the draft schema moves, 74 "stable"
capsules change meaning. Either freeze `v1` or introduce an explicit
`stable-against-draft` status.

### R4. Measure the token-optimisation claims, or relabel them as targets
**Effort: S to measure lazily; M to implement.  Impact: medium (credibility).**
The figures appear only in `CAPSULE_ECOSYSTEM_DESIGN.md` and nowhere else in
the repo; `benchmarks/` holds one unrelated MLX script [verified]. Precisely:
94% at lines **404, 505, 1120**; 75% at line **1121 only** [verified].

That last detail sharpens the point considerably. Line 1121 is in the doc's
**closing summary** — and §2.2 Strategy 2, where index compression is actually
specified, never states a percentage at all. It gives only a 40→10 token
illustration. So "index compression: 75%" is a summary-only figure with **no
derivation anywhere in its own section**. Measuring the *index-compression* claim is nearly free —
tokenise the current registry index versus a compressed form. **Do not let a
"94% token savings" claim reach a slide unqualified.**

### R5. Populate the artifact-conversion registry, or document why it is empty
**Effort: M.  Impact: high (unblocks composition).**
`artifact-conversions.v1.json` contains
`{"schema_version": …, "conversions": []}` — zero entries [verified].

⚠ **Scope this claim carefully.** An earlier draft called it "the cleanest
designed-built-not-populated example in the codebase". That does not survive:
a **second adapter registry exists and is populated** —
`harness/config/artifact-adapter-capsules.registry.yaml` carries 3 adapters
with real `source_artifacts → target_artifacts` edges, and is consumed by
`apo_plan_compiler.py`, `capability_capsules.py`, a CI checker
(`tools/check_artifact_adapter_registry.py`) and its own tests [verified].

The accurate, still-useful claim: `artifact-conversions.v1.json` is read by
**`capsule_composition.py` alone** (`CONVERSIONS_PATH`, line 20), so the
*composition-search* conversion graph specifically has no edges — while typed
adapter routing works elsewhere. Whether that is intentional is unknown: there
is no ADR, comment, or issue explaining it. Panel A's posture is the right one —
*"verify intent before calling it a gap."* Downgrade impact accordingly and ask
rather than assert.

### R6. Give capsules a quality feedback loop — they currently have none
**Effort: M.  Impact: high (this is the biggest structural gap found).**

There are **three unrelated capability-quality systems** in the harness
[verified]. An earlier draft of this note said two, and mis-attributed
`capability-scorer.sh` to the second — corrected here:

| | (1) Capability Capsules | (2) Plugin Capabilities | (3) Capability Graph |
|---|---|---|---|
| Storage | 80 YAML manifests + `capability-capsules.registry.yaml` | `plugin_capabilities` in `state.db` | `capability-graph.jsonl` under `~/.solar/harness/` |
| Populated from | hand-authored manifests, explicit registration | the plugin loader (`_load_plugins_from_loader()`, `capability_registry.py:84`) | **scraped from sprint `eval.md` "能力覆盖清单" sections** by `hooks/capability-scorer.sh` |
| Used for | planning, admission, composition, dispatch | provider selection by capability level 1–5 | generating `harness/needs-improvement.md` |
| Quality machinery | **none** | `evolution_engine.py` (854 lines): `scorecard()`, `promote()`, `demote_degraded()`, `recommend()`, `run_loop()` | ✅/⚠️/❌ tallies + `quality_score` |

`capability-scorer.sh` contains **zero** references to `plugin_capabilities`,
`state.db`, or `sqlite` [verified] — it is system (3), not system (2). So the
`used_count >= 3` threshold in `needs-improvement.md` belongs to the
`eval.md`-scraping graph, and has nothing to do with either capsules or the
evolution engine.

`evolution_engine.py` contains **zero** occurrences of the string "capsule"
[verified]. Stronger still, and confirmed by adversarial review: **no file
anywhere in the repo contains both "capsule" and "scorecard", or both "capsule"
and "plugin_capabilities"** (excluding `.git`/`outputs`).

So the earlier reading — "the capsule scorer is silent because it needs
`used_count >= 3`" — was wrong in an important way. It is not that capsule
scoring is mis-thresholded; **capsule scoring does not exist.** The 80 capsules
have no scorecard, no health status, no promotion or demotion path, and no
runtime feedback of any kind.

Meanwhile `CAPSULE_ARCHITECTURE.md` §7 already designed the right thing:
`v_capsule_health` classifies a capsule `healthy` / `degraded` / `slow` by
comparing **measured** duration against the **declared** `max_duration`, and
`sys_capsules` carries `invoke_count` / `success_count` / `avg_duration_ms` /
`total_cost`.

Two framings, pick per audience:
- *Minimal:* report how many of the 80 capsules have ever been invoked — the
  honest coverage signal. **The mechanism already exists**: 
  `harness/lib/evidence_ledger.py:42-43,72-75` accepts and persists
  `capability_capsule_id` and `capsule_kind` on every entry [verified]. What is
  missing is any *aggregation* over it — and this checkout contains no ledger
  data carrying capsule ids at all. So the number is cheap to start producing,
  which makes this the lowest-cost item on the list, not a blocked one.
- *Principled:* build the promise-vs-reality comparison the design already
  specifies. It also unblocks the ecosystem doc's `avg_latency_ratio` and
  `cost_accuracy` trust terms (`12-…` §1.3.3), which are the mechanism that makes
  an over-optimistic spec self-penalising. Blocked on R10 (capsules declare no
  timing today), so R10 → R6 is the natural order.

### R7. Give the deprecated alias an expiry
**Effort: XS.  Impact: low-medium (hygiene).**
The ADR (2026-05-24) accepts `execution_capsule_id` "for one migration cycle at
the loader boundary only"; the schema file is titled *"Solar Execution Capsule
v1 (Deprecated Alias)"*. Still accepted, with no date and no cycle definition
[verified]. "One migration cycle" is unmeasurable — deprecations need a version
number to expire at.

### R8. Document the two-directory rule
**Effort: XS.  Impact: low, but removes a recurring question.**
`harness/capability-capsules/` (39 manifests) and
`harness/config/capability-capsules/` (46: 41 registered + 5 unregistered) both
resolve via the registry's `manifest_path`, which is relative to the registry
file's own directory [verified]. No document states which directory a new
capsule belongs in.

### R9. Unblock the shared dependency, then drive one route to `full`
**Effort: M for the shared dependency; L for a full end-to-end promotion.  Impact: high (demonstration value).**

**Re-verified 2026-09-10 against the live config** — the claim holds and is
current, not stale. Source of truth is
`harness/plugins/autosci/config/feature_parity_routes.v1.json` (cite this, not
`unification-status.md`):

- **28 routes: 17 `partial`, 11 `gated`, 0 `full`** — unchanged from the
  2026-07-02 status entry, with a character-identical gated list.
- The file was last modified `523040fb2` on **2026-07-21**, *after* that status
  entry. So it is not a stale document: it is current, and nothing has been
  promoted in the ~7 weeks since.

Reading the `limitations` field across all 17 partial routes shows these are
**not 17 independent problems**:

| Blocker | Partial routes |
|---|---|
| **Review LLM provider only** | 5 — `/exp-design`, `/exp-eval`, `/novelty`, `/rebuttal`, `/review` |
| **Both** Review LLM *and* compile/PDF | 3 — `/paper-draft`, `/paper-plan`, `/research` |
| **compile/PDF only** | 1 — `/ingest` |
| Blocked by neither | 8 |
| | **5 + 3 + 1 + 8 = 17 ✓** |

⚠ An earlier draft of this note presented these as 8 / 4 / 8, which sums to 20 —
it double-counted the three routes needing both. Corrected above.

`/review` states it directly: *"final_acceptance_ready requires configured
OpenAI-compatible Review LLM provider, command bridge, or ..."*

**Revised recommendation.** Configuring the Review LLM provider is a single
infrastructure change that removes the *sole* remaining blocker from **5 of 17**
partial routes (~30%), and a *necessary but insufficient* step for 3 more. That
is still the best leverage available — better than promoting one route in
isolation — but it is not "half", and `/paper-draft`, `/paper-plan` and
`/research` will **not** promote on that change alone. The eight
routes blocked by neither dependency are the cheapest individual candidates,
since their remaining limitations are local evidence-shape issues:

`/ask`, `/check`, `/discover`, `/exp-pilot-eval`, `/exp-status`, `/ideate`,
`/init`, `/survey`

Best single candidate: **`/discover`** → `cap.research-literature-discover`.
⚠ Caveat: `/discover`'s own limitation reads *"Live provider proof remains
optional/provider-mode; local wiki source proof must not be labeled as
live_provider"* — a live-network/provider dependency, not a purely local
evidence-shape fix. The recommendation stands on demonstration value; do not
oversell it as cheap.
That is the same capsule used as the worked example throughout `11-`/`13-`, so
promoting it would let the deliverable demonstrate one capability end-to-end —
manifest → admission gate → dispatch → accepted evidence — on a specimen the
audience has already been shown.

⚠ **Do not present "0 full" as a maturity indictment.** Side-effect policy
across the 28 routes is 16 `approval_required`, 8 `dry_run_only`, 4 `none`
[verified]. The 11 gated routes are the destructive ones (`/reset`, `/edit`,
`/exp-run`, `/paper-compile`), deliberately held behind approval per the
component-gating policy. `gated` is a policy state, not a failure state — say
so explicitly or the number reads worse than it is.

### R10. Close the three schema gaps from §0
**Effort: L.  Impact: high, but this is real design work, not cleanup.**
Declared `timing` + `idempotency` would unlock result caching and timeout
policy; a `denies` list would make over-broad effect declarations diffable; an
`evolution` contract would let the four monotonicity rules
(`11-…-digest-en.md` §14) actually be enforced at version promotion. Present as
direction, not as a task.

---

## 2. Open questions for discussion

Genuine questions — the answers are not visible from the repo, and each would
change what "better" means.

**Q1. Is the ecosystem design still the intended direction?**
`CAPSULE_ECOSYSTEM_DESIGN.md` specifies federation across Claude/GPT/Gemini
agents, Ed25519-signed capsules, SCARE-score-ranked remote routing, and four
governance tiers. None of it exists in `harness/lib/`. Given that OpenSolar
explicitly positions itself as **local-first and not a multi-tenant control
plane** (`00-orientation.md`), is the federation layer still wanted — or has
the project's identity moved away from it? This is the most consequential
question in the set, and the report should ask it rather than assume either way.

**Q2. Should `applicability` signals stay keyword-based?**
Selection currently keys off `task_types` / `positive_signals` /
`negative_signals` — literal strings like "discover papers", "arxiv
recommendations". The ecosystem doc's §2.4 argues *for* exactly this (a
non-LLM parser in front of selection, 0 tokens, deterministic). Is the keyword
surface a deliberate commitment to that principle, or an interim measure
awaiting embeddings? The answer determines whether growing to 300 capsules is
fine or a scaling problem.

**Q3. ~~Are the five unregistered capsules gated or drifting?~~ — ANSWERED: at
least one is drifting.**
Promoted from question to finding by adversarial review.

`cap.gemini-enhanced-search`, `cap.chatgpt-browser-agent`,
`cap.notebooklm-enrichment` are external-provider integrations, and leaving them
unregistered is consistent with `CLAUDE.md` component-gating. But
**`cap.research-report-draft` is different**: the live route config maps
`/paper-draft` (coverage `partial`) to it, and it appears **0 times** in the
registry [verified]. An active route names a capsule that cannot be admitted.

This directly contradicts Panel A's note 07, which asserts all five are
*"inert by design"* and *"exactly the component-gated and off by default
policy"*. That reading is not supportable for `cap.research-report-draft`.
**Adjudicated in Panel B's favour on the evidence; note 07 should be corrected.**

The remaining genuine question is narrower: is `cap.research-report-draft`
awaiting registration, or has `/paper-draft` been repointed without the route
config following?

**Q4. What is the relationship between capsule `effects` and the capability token?**
`capability_token.py` (105 lines) carries file/shell/network/git allow-deny
scopes with expiry; capsule `effects` declares read/write/execute/network.
These are two permission vocabularies over the same actions. Is one derived
from the other, or are they maintained independently — and if independently,
what happens when they disagree?

**Q5. ~~Does version promotion enforce the four evolution rules?~~ — ANSWERED: no.**
Resolved by this panel, recorded here because the answer matters.
`CAPSULE_ARCHITECTURE.md` §6.1 requires that a new version pass all prior test
cases, only narrow permissions, only shorten timing, and only extend output
schemas. The only `promote()` in the tree is
`evolution_engine.promote(capability, eval_pass, regression_pass)`, which gates
on two booleans **supplied by the caller** and then updates a row in
`capability_scorecards`. It never reads a capsule manifest, a version, a
permission set, a timing guarantee, or an output schema [verified].

All 8 cases in
`tests/foundation/capability_capsule/phase22_capability_capsule_evolution_and_version_promotion_cases.json`
carry `execution_status: DESIGNED_NOT_YET_IMPLEMENTED` [verified], and that
file's own contract states: *"end-to-end capsule migration/version rollback as
one transaction was not found."* Its `generation_policy` also notes the
contracts were "treated as provisionally correct per user instruction" — these
are generated specifications, not passing tests. **Do not cite this file as
evidence of coverage.**

The remaining open question is the useful one: *should* capsule version
promotion be gated on the four monotonicity rules, given that capsules today
declare neither timing nor permissions to compare (see §0 and R10)?

**Q6. Is `capsule_kind` the right classification axis?**
Shipped kinds (`capability` / `guard` / `resource`) classify by *role in the
permission system*. The ecosystem doc's compressed index proposes
`Q=Query / A=Action / M=Monitor / T=Transform` — classification by *what the
capsule does*. Both are useful and they are orthogonal. Should manifests carry
both?

---

## 3. Framing advice for the deliverable

Given a mixed audience — one supervisor who knows the system, two people
onboarded the day before, and presenters five days in — the safest and most
persuasive structure is:

1. **Lead with the epistemic critique** (`11-…` §1). Everyone with agentic-AI
   experience has been bitten by a tool whose blast radius they couldn't
   predict. That table earns attention in one slide.
2. **Show one real manifest** — `cap.research-literature-discover.yaml`. Its
   invariants ("never falls back to fixtures"; "missing protocol parameters
   remain explicitly unresolved rather than being silently invented") make the
   abstraction concrete and are quotable verbatim.
3. **Show the gate, not the document** — the ADR's runtime gate and its five
   fail-closed reasons prove capsules constrain execution rather than describe it.
4. **Then, and only then, the roadmap.** With §0's reconciliation table as the
   framing device, the gaps read as a deliberate trade plus known next steps,
   which is both more accurate and more credible than a defect list.

**Three claims to avoid**, each of which the supervisor could puncture:
- "Capsules are formally verified." The symbolic-verification phase is designed,
  not built. Say *"contract-checked at admission, with formal verification as
  designed future work."*
- "94% token savings." Unmeasured design estimate (R4).
- "80 capsules are stable." They are *marked* stable, against a draft schema (R3).
