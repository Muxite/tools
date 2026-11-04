# V8: Adversarial third pass, 2026-09-21

Read and measure only. Nothing else was edited. Files as they stand now: `DESIGN.md` (1,204 lines), `deck/deck-draft.md`
(691), `asks/*.md`. Source: AI4Research `b0bf165f9`, agent-core `e23806c1`, sciencediscovery `cee1974`.

**Verdict.** Most of V7 landed, but two of V7's own findings were wrong. ScienceDiscovery's docs *do* say the package is
verified before the sandbox starts, and that reads verify the hash, so the design's wording there should stay. The new
text this round adds three real defects. The old implementation *does* have a fallback. The new §2.6 fingerprint row
compares two different hashes. And §3.5 lets judging stages become capsules without saying who may build their next
version, which reopens invariant 4.

## 1. V7 MUST items

| # | Verdict | Evidence |
|---|---|---|
| 1 Blind Curator direction | **LANDED** | deck:360 (THUS is now conditional); DESIGN:1109-1114 ("fails silently … exactly *The Blind Curator*'s result") |
| 2 Propagate claim-1 retraction | **LANDED** | DESIGN:478-479, :852; deck:321-325; routing-xiaoyang.md:42, :75-77; QUESTIONS-teammates.md:81-84. None still says "shadowing defence" |
| 3 Slide 12 title | **LANDED** | deck:437 "fully provides one of the five"; SAY :460-461 |
| 4 Name ScienceDiscovery; fix "no admission" | **PARTLY** | Named in DESIGN §5.1:940-954, claim 4 :1120-1121, deck:495, :504-506, :514. **But** DESIGN:951 "What it deliberately leaves out is judgment" and deck:505-506 "leaves the judging to the application" are wrong. `skill-self-evolution.md:15-22` (M1.5, 已实现, implemented) has agent proposals, a mandatory dry-run and publish "必须经过现有权限确认流程". :52 has user confirmation by default. :58 says "不让 Agent 静默 commit". :79 says the real commit needs a user's manual publish. :249-254: M2 plans baseline/candidate evaluation. That is an implemented human admission gate. It is not in DESIGN at all |
| 5 Slide 13 title | **LANDED** | deck:480; line under table :494-496 names VaG and ScienceDiscovery as multi-stage |
| 6 Read-status honesty | **PARTLY** | Paper2Agent is off slide 13 and has lost its ✅ (DESIGN:978). Cordis is off the main slides. GraSP is marked unread in Backup 1 (deck:615-617). **Still false:** RelAIBuild is ✅ at DESIGN:968 and "Read in full by an agent" at deck:611-613. Its summary header lists p1, 3-4, 9-13, 19-22 and 27-31 of 45, with no *Claims checked* table. DESIGN:451 still says GraSP was "Read in full", which contradicts deck:615 ("treated as unread"). No summary exists |
| 7 ScienceDiscovery source claims | **NOT LANDED, and V7 was wrong** | `skill-progressive-disclosure.md:56`: "verified against the recorded package hash before the sandbox starts". `cas.md:25`: "Reads verify the hash; typed reads additionally verify size and pool". DESIGN:946-948 is **correct as written**. Withdraw V7 MUST 7. The only nit is that `cas.md:9-27` could be `:7-25` |
| 8 Routing on slide 11 | **LANDED** | deck:399 "model routing ranks the filtered set"; SAY :419; coverage :682 |

Score: 5 LANDED, 2 PARTLY, 1 NOT LANDED and withdrawn.
## 2. New text, attacked on its own terms

**a. §2.2 "no generalist fallback … fails the plan with UNSATISFIABLE_CAPSULE" (DESIGN:263-265; deck:233-234). PARTLY FAILS.**
The code at `apo_plan_compiler.py:618-631` does emit `UNSATISFIABLE_CAPSULE`. `build_capsule_plan_ir` sets
`verdict: fail` (:856-893), and the whole-request path turns that into `decision="failed"`
(`elastic_planner.py:7067-7086`). But the function it calls has a fallback.
`capability_capsules.py:1172-1176` has "Priority 3: static default (fallback only)", which binds
`DEFAULT_CAPSULE_BY_LOGICAL_OPERATOR[op]` (:54-84) with `selection_mode="static_default_fallback"` when the classifier
matches nothing. `apo_plan_compiler.py:1392-1403` records "Static default fallback used". The per-node path in
`actor_runtime.py:111-134` swallows compile errors and dispatches anyway (Researcher nodes "passed with no capsule", `capability_capsules.py:1135-1140`).
The truthful form is: *the whole-request compiler fails a step with no matching capsule. The old code also had a
per-operator static-default fallback and a per-node path that ran without a capsule. The pipeline theory keeps the
first and drops the other two.*

**b. §2.5 old planner's filter (DESIGN:480-481). HOLDS.** `elastic_planner.py:4553-4643` filters on inputs and outputs
(:4587-4592), read, write and execute in both directions (:4599-4604), network (:4605-4609) and trust (:4617-4619),
before `_capsule_selection_prompt`. No `precondition` appears in the three planner files. Nits: no cost or risk; trust
is matched exactly.

**c. §2.5 Symphony citations (DESIGN:500-505). HOLDS, with one internal contradiction.** `engine.py:14` is
`RecursiveSearchEngine`, a model-driven top-K walk. The tree is built with an LLM in `retrieval/build/tree/`
(`llm_runtime.py`, `one_shot.py`). Input and type matching happen afterwards in `input_matching.py`, which is used by
`plan_builder.py:35` and by Beam. Fast has its own check (`fast.py:543`), so "in its Beam planner" is incomplete. Retrieval
reaches planning as `candidate_ids` (`fast.py:170-172`). **Contradiction:** DESIGN:499-500 says ranking reads the
declared `description`, "so retrieval reads what was admitted". Five lines later, DESIGN:504, the fingerprint is "what
retrieval reads". Pick one.

**d. `content_hash` computed, not declared (DESIGN:349). FAILS outside §2.3.** Slide 8 still lists
`capsule_id, version, content_hash` as a manifest field row (deck:267). DESIGN §5.4:1065 puts `content_hash` in the
"Capsule manifest (§2.3)" column under a table whose header row says "written by: the author" (:1064). DESIGN:77
(§1.2) lists content hash under the Lineage part, while §2.3's `lineage` field (:359) does not. §2.3.1:414 ("The hashes
are manifest fields") is now ambiguous.

**e. `description` and the fingerprint row against §5.4. FAILS.**
(i) §5.4's "when to use it" row (DESIGN:1067) gives the capsule only `preconditions`, so the new `description` field is
missing from the table that exists to list what the manifest records.
(ii) The new §2.6 row (DESIGN:512) rejects on a mismatch between the derived fingerprint and the manifest's **content
hash**. Symphony's `content_hash` comes from the SKILL.md file (`agent/retrieval_toolkit.py:1554`,
`read_skill_file`), and DESIGN's own §5.4:1064, :1071 says so ("computed from the skill folder", file integrity).
The capsule's hash is over the canonical manifest (:349). The two can never be equal, so as written the row rejects
every capsule. It should compare the fingerprint's hash with the `components` entry for the file it hashed. The deck's
admission table (deck:350-358) does not show this row at all.

**f. §3.5 stage capsules (DESIGN:802-824). Consistent with §3.2 and with the supervisor's ruling. FAILS on four points.**
1. **Invariant 4.** It makes judging stages capsules, "an acceptance gate or an evaluation check" (:821), and
   "evaluation gates are the first milestone's natural unit" (:816). The improve loop, which authors capsule versions,
   is RSI's (:269). Invariant 4 (:224-225) and §4.2 (:891-892) forbid anything modifying "the verifier". §3.5 never
   says who may author a new version of a judging stage capsule. So RSI can propose a new version of a check that
   judges RSI's own candidates.
2. **Fixed-point lists disagree.** §3.5:819-820 lists the gate, store and registry, identity, exposure, and bind and
   freeze. Invariant 4 names "the gate, the registry or the verifier". rsi-saurav.md:76-77 names "the gate, the registry
   and capsule identity". The deck says "anything that admits, binds or pins" (deck:429-430). Only invariant 4 names
   the verifier. None names the certificate and exposure logs or the re-manifest tool, and §2.3.1:406 says that tool
   is the one place a damaged install could be laundered.
3. **"Exactly three points, and deliberately nowhere else"** (DESIGN:628; deck:410 THUS). §3.5 adds a fourth: pinning at
   run start, before planning (:812). §3.1:647 says binding is "never something a person hand-writes", but stage
   capsules are chosen by "the run's configuration" (:811).
4. **Local waivers as a standing regime** (:823-824). §2.3.1:409-411 defines a waiver as one person, one hash, one
   machine, "never enters the shared library". A team building the pipeline together cannot share a waived stage, and
   a waived *judging* stage is a gate nobody admitted. §7.3:1177 also registers M1 through `SkillGraphUpdater`, which
   cannot take a gate (§3.3:739-741). That conflicts with "evaluation gates are the first milestone's natural unit".

**g. §5.1 ScienceDiscovery line citations. All HOLD.** skill-library-management.md :30-35, :39, :74, :132, :153 and
:205-207 say what DESIGN says. skill-progressive-disclosure.md:56 and cas.md hold too (see MUST 7). Code exists
(services/api/src/skill-library-catalog.ts), so the present tense is fair. The one gap is the omitted human gate (MUST 4).

**h. §6 claim 4 (DESIGN:1119-1126; deck:534). HOLDS narrowly.** I found no system with a declared
pre/post/effects contract that an admission gate tests *and* a selection filter evaluates, bound by hash to pinned
versions. Nearest misses, none of them cited:
- **SkillWeaver** (2504.07079, summary read, p6): each API carries a declared **precondition** that an API-selection
  module filters on, and every API is honed as a unit test before it is kept. It lacks postconditions, effects,
  versions and hashes, and its test inputs are LLM-invented, not written from the contract. This is the closest
  in the literature.
- **The old AI4Research itself**: selection filters on declared types, effects and trust (item b). Plans are frozen
  with `sha256` refs (`apo_plan_compiler.py:1237-1240`). Admission is static only (`capability_admission.py`
  `rejection_reasons`). So claim 4's real delta over our own predecessor is the *behavioural* admission test plus
  preconditions. Say so.
- **ScienceDiscovery**: hash-bound pins and a human publish gate, but no contract. **VaG (2608.05810)**: deterministic
  SchemaCritic and A-B replay, no contract. **skillhub**: review and zip hash, no contract. **ABC (2602.22302)**: no library.

## 3. New contradictions across DESIGN, deck and asks

- **N1. Quarantine.** rsi-saurav.md:69-70 says direct writes land "in quarantine: stored, but bindable by no run".
  The fix for V7 N7 is correct in substance, but "quarantine" appears nowhere in DESIGN. It is §2.3.1 row two, "not
  loaded" (:400), and it is not an exposure state, because §2.2's table covers admitted versions only (:293-300). Use
  "not loaded (§2.3.1 row two)", or add the state to both tables.
- **N2.** routing-xiaoyang.md:44-46 and QUESTIONS-teammates.md:78-79 offer to *add* "a normalised description". It
  already exists (DESIGN:353), and ranking must read it (:499).
- **N3.** deck:424-425 still says "the capsule layer's own path". DESIGN:783-785 names `apply_extension_hot`.
- **N4.** DESIGN:1022-1023 ("genuinely open") and deck:66-67 state one contract shape as a claim. :1133 says untested.
- **N5.** DESIGN:1107 and :815 (`RawIntent v2`) cite old code the banner (:40-41) says is never referred to.

## 4. Ranked fix list

**MUST before tomorrow**
1. **§2.6 fingerprint row (DESIGN:512).** Replace "content hash" with "the fingerprint's file hash equals that file's
   `components` entry". As written, it rejects every capsule, and §5.4:1064, :1071 shows why.
2. **ScienceDiscovery's human gate.** Replace DESIGN:951 "leaves out judgment" and deck:505-506 "leaves the judging to
   the application" with: *it has an implemented human-confirmed publish gate over dry-run diffs
   (skill-self-evolution.md:15-22, :52, :79), plans baseline/candidate evaluation (:249-254), and leaves automated
   scoring and gating to the application (skill-library-management.md:39). What it has no place for is a declared
   contract for that gate to test.* Otherwise the first reader who knows ScienceDiscovery will catch it.
3. **§3.5 and invariant 4.** State that judging stage capsules (gates, evaluation checks) are authored and versioned
   only outside RSI, and that the verifier is on the fixed-point list. Reconcile the fixed-point lists at DESIGN:224,
   :819-820, rsi-saurav.md:76-77 and deck:429 into one list, and include the re-manifest tool.
4. **§2.2 "no generalist fallback" (DESIGN:263-265, deck:233-234).** Restate it as in 2a. The old code had a static
   per-operator fallback (`capability_capsules.py:1172-1176`), and the design deliberately drops it.
5. **Read status.** Remove ✅ from RelAIBuild (DESIGN:968) and move it to "partially read" in Backup 1 (deck:611-613).
   Change GraSP's "Read in full" (DESIGN:451) to match deck:615.
6. **Slide 8 `content_hash` row (deck:267)** and §5.4:1065: mark it computed and store-indexed, not a manifest field.

**SHOULD**
7. Resolve §2.5: retrieval reads `description` (:499) or the fingerprint (:504), not both.
8. Add `description` to §5.4:1067. Put the fingerprint row on slide 10.
9. "Exactly three points" (DESIGN:628, deck:410): say "for work capsules", given §3.5's run-start pin.
10. §3.5 waivers against §2.3.1's one-machine definition. "Gates are M1's unit" against M1 via `SkillGraphUpdater`.
11. RSI ask: "quarantine" → "not loaded (§2.3.1)". Routing ask: state that ranking reads the declared `description`.
12. Slide 11 IF ASKED: name `apply_extension_hot` (deck:424-425).
13. Claim 4: name SkillWeaver and the old AI4Research filter as nearest misses, with the delta.
14. Remove "genuinely open" (DESIGN:1022-1023) and "across every size" (deck:66-67).
15. Still open from V7: `resources` enforced with no H-row (DESIGN:357); 2608.08453 without ⧗ (DESIGN:1076).

**COULD**
16. DESIGN:946-948 is correct; credit V7's error. Tighten `cas.md:9-27` to `:7-25`. 17. §2.5: old filter also used proof classes; Fast also input-matches (`fast.py:543`). 18. deck:680 "Four things genuinely change" against DESIGN:431 "Five". AllocBench 92%: name the model (deck:243).
