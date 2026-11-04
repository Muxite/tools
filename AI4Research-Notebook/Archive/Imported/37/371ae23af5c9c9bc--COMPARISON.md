# Two versions of the Capability Capsule schema, compared

**Current** = `SCHEMA.md` v1.6, `deck/companion.md` and the deck, built through seven review rounds.
**Independent** = `alt/SCHEMA-ALT.md` and `alt/REPORT.md`, written on 2026-09-22 by a drafter that never saw the current
version, from the papers, the code, the supervisor's rulings and Muk's brief (`alt/BRIEF.md`).

The point is not to pick a winner. Each version has ideas the other lacks, and the merge should take the stronger idea
per row.

## 1. The shape

| | Current | Independent |
|---|---|---|
| Core idea | one hashed **manifest**, and eight records that name its hash | **five record kinds, split by who writes each**: Declaration, Verdict, Standing, Binding, Finding |
| Governing rule | eight invariants | four rules, the sharpest being "declared and observed facts never share a record", and "observation may withdraw authority; only a checked declaration may grant it" |
| How strongly a claim is backed | two **levels** per capsule: provisional, certified | an **assurance level per claim**: enforced, tested, audited, declared |
| Manifest sections | a flat field list (A1) | seven named sections: identity, ports, needs, changes, guarantees, budget, members |
| Everything observed later | separate records: availability events, composition reports (B7), gap records, verifier audit | one **Finding** record with kinds: composition, conflict observed, overlap, drift, audit violation, use outcome, gap |
| Readability | rules before definitions; needs a restructure | reads top to bottom: what it is, definitions, records, mechanisms, rejected |

**Record for record:**

| Current | Independent | Note |
|---|---|---|
| Manifest (A1) | Declaration | nearly the same content; the independent version groups it into sections and adds `summary` (400-character cap), `carrier`, `context_capsules`, `invariants`, `provides`/`injects` |
| Certificate (A2) | Verdict | both typed; the independent version adds ESCALATE, `policy_epoch`, and `invalidated_by`; the current version adds `precondition_parity[]`, `models_used`, `nearest[]`, `contribution` |
| Availability event (A3) | Standing | the same idea; the independent version keeps one moving pointer per name with a logged history, the current version an event log per hash |
| Verifier audit (A4) | inside Verdict (`verifiers[].measured_error`) | the independent version has no separate audit record |
| Run pin (B4) | Binding | close; the independent version adds `offer_hash`, `step_identity`, `resolved` services; the current version adds `selection_tokens`, `blocked[]`, `exit`, `claims[]` |
| Gap record (B2), composition report (B7) | Finding (kinds `gap`, `composition`) | unified in the independent version |
| Candidate package (B1) | the Declaration plus `lineage` | the independent version has no separate package |
| Plan step (B6), state vocabulary (B3) | vocabulary is a definition; plan steps are not a record | the current version is stronger on plan-step requirements and typed unmet outcomes |

## 2. Ideas only the independent version has

| Idea | Why it matters | Take it? |
|---|---|---|
| **Assurance level on every claim** (enforced, tested, audited, declared) | states exactly how far each promise is backed; answers "declared is not enforced" per field, not per capsule | yes: finer than two levels; could sit beside provisional and certified |
| **Checks are admission evidence only if the capability cannot reach them**: runner outside the write scope, signal from the harness, not self-owned | the Darwin Gödel Machine lesson taken to its conclusion: the node removed the *signal*, not the checker | yes |
| **`context_capsules` in lineage**: what was in the builder's context | lets a harmful capsule's descendants be found and suspended (When Self-Evolution Backfires) | yes; the current version has `build_context` in the certificate, similar |
| **Replacement compatibility and "no new powers"** on revision | a revision must still serve its dependents and add no undeclared write, delete or emission | yes |
| **`provides` / `injects` service keys** (Cordis's coeffects) | makes spatial composability concrete: a provider cannot be retired while an admitted capsule injects a key only it provides | yes |
| **Reversibility class `scoped`** and `emission` policies (withhold until the freeze is safe, or compensate) | closer to Cordis §6.1 than inverse/compensation/irreversible | yes |
| **Set-level marginal gain at admission** (`NEGATIVE_MARGINAL_GAIN`) | a capsule that passes alone but lowers the slot's joint result is rejected | compare with the current availability rule 1 |
| **`summary` capped at 400 characters, and the chooser sees only `summary` and `ports`** | a concrete token budget for selection | yes |
| **Overlap puts the newer capsule on DEFER** until a person picks | handles More Skills, Worse Agents' crowding directly | discuss |
| **Evidence floor, and retirement suspended while the judge is too lenient** | turns The Blind Curator into a rule, not a health signal | yes |
| **Ledger integrity**: `prev_hash` on every append-only entry | tampering and reordering become detectable | yes |
| **A capsule is whatever the freeze binds to one plan node** (the ceiling) | a crisp answer to "how big can a capsule be" | discuss |
| **Code findings not in the current version**: agent-core's RSI module (`openjiuwen/rsi/schema.py`), `SkillUseRail.enabled_skills` as the offer for skills, `PluginSpec` as the carrier, the MCP client dropping annotations and output schemas, skillhub's review bound to bytes, ScienceDiscovery's "never trusted from frontmatter" | integration evidence, pending verification | verified in source; take |
| **Symphony fed with no change**: supply `content_hash` and I/O so its model extraction is skipped | a cheaper integration than the current version's | verified in source; take |

## 3. Ideas only the current version has

| Idea | Keep? |
|---|---|
| **Predicate parity** as a named section, `evaluable_at` (planning or dispatch), parity before a precondition enters the filter, and the paper's three failure modes as records | yes; the independent version has parity checks and `max_age_s` but not the planning-time distinction |
| **Two levels** and where each may run (`accepts_provisional`, and the rule that such steps need a deterministic output check) | yes, alongside assurance levels |
| **Tokens measured against today's filter** in M2, with `selection_tokens`, `blocked[]` and false blocks | yes |
| **Plan-step records and typed unmet requirements** (`needs_input`, `unsatisfiable_capsule`, ...) | yes |
| **Verified gaps in the agent-core and Symphony hooks** (graph takes only skills, subagents and agents; mutation needs a model; binder has no hash check; load records in memory) | yes; the independent version found some of these too |
| **Imports enter as provisional**, with an importer per source | yes; the independent version wraps MCP and A2A but has no import path |
| **Floating dependencies with contracts** (A5) | yes; the independent version has `external[]` with a drift probe |
| **The SkillFuzz field mapping and co-loading rule** | yes; the independent version has an equivalent screening mechanism |
| **Falsifiable advantages, milestones, the deck** | yes |

## 4. Where they disagree

| Question | Current | Independent | To decide |
|---|---|---|---|
| unknown precondition | blocks by default (`on_unavailable: block`) | required: DEFER with a typed request; optional: exclude | the independent version follows Cognitive Admission Control more closely |
| a judge with no measured error | advisory only, cannot certify | may admit, but only under a risk ceiling set by policy | a policy choice for verification |
| retirement by cap | librarian evicts under the cap | lowest-use capsule with no dependents, from Binding counts | compatible; the independent version is more specific |
| the Symphony graph | a gap: only skills, subagents, agents | the capsule layer feeds it descriptors; non-skill kinds do not enter | agree in substance |

## 5. Suggested merge

1. Take the independent version's **structure**: records split by writer, one Finding record, definitions before use.
   It fixes the current version's readability problem outright.
2. Keep the current version's **mechanisms**: predicate parity with `evaluable_at`, two levels plus provisional
   steps, tokens in M2, plan steps and typed unmet outcomes, imports.
3. Add the independent version's **per-claim assurance levels**, check-reachability rules, `context_capsules`,
   replacement compatibility, service keys, and ledger integrity.
4. Take the independent report's **paper-by-paper section** (§5, each paper ending in the tool, the fields and the
   impact on each team) as the spine Muk wants to talk through, and its **comparison section** (§7, fingerprint versus
   Declaration, "is a capsule a skill?") as the answer to the Symphony and skillhub questions.
5. **Fact-check done (2026-09-22).** A Sonnet reviewer checked the numbers, code and supervisor quotes. It found five
   problems, all fixed: the 96.8% was framed as a self-grading error rate (it is held-out test failure); the
   pre-commit-gate result lost its upper-bound caveat; RelAIBuild's 0.5% lost its "indicative" hedge; and two slips in
   READ-LOG. Its pass was priority-first, not exhaustive. The main agent then confirmed the new integration findings
   in source: `RsiTreeNode` (`rsi/schema.py:97-111`), `SkillUseRail(enabled_skills=...)`
   (`harness/rails/skills/skill_use_rail.py:78, :95, :255-259`), `PluginSpec` (`harness/schema/extension_spec.py:146-164`),
   and the MCP client keeping only name, description and input schema (`core/foundation/tool/mcp/client/sse_client.py:331-338`).
