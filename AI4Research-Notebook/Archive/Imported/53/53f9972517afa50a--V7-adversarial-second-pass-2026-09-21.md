# V7: Adversarial second pass on the Capability Capsule design, 2026-09-21

Reviewer: adversarial agent, read-and-measure only. No design, deck or ask file was edited.

Scope: `DESIGN.md` (1,142 lines), `deck/deck-draft.md` (main slides 1–15, Backup 1, Backup 2), `asks/*.md` (5 files),
the V6 fix list (`verify/V6-adversarial-2026-09-21.md` §7), paper summaries in `tundle/ai4research/papers/summaries/`
and close-read notes 20–38, and openJiuwen source: `agent-core` `e23806c10732`, `sciencediscovery` `cee1974d4631`,
`skillhub` `236f56c101d9`, `jiuwenswarm` `02b37f47fbef`. Line numbers below are for the files as they stand now.

**Verdict in two sentences.** Most of the V6 fixes landed where they were aimed: the identity scheme, the RSI ask,
the "no prior system" claim, the platform choice, the H1/H5 facts and a real position slide. Three problems remain.
The retraction of the filter-fixes-shadowing and judge-fails-safe claims stopped at §6: it did not reach §2.5, §4.2,
slides 9 and 10, or the routing ask. Slide 12's title contradicts its own table. And the surviving contribution
(§6 claim 4) was never tested against the strongest competitor, openJiuwen's own ScienceDiscovery skill library. That
system already carries one versioned identity through proposal, human-approved publish, per-run pinning, recall and
a provenance manifest, and the design misdescribes it as having no admission step.

---

## 1. The ten MUST items from V6 §7

| # | V6 MUST item | Verdict | What decides it |
|---|---|---|---|
| 1 | Take the certificate out of the hashed manifest; add a revocation or exposure record; name it in §2.2 and M1 | **LANDED**, with one leftover | DESIGN:356-359 ("Not in the manifest, on purpose"); :287-288 (exposure record); :335-336 (revocation is a new record); :1105 (M1 includes "the certificate and exposure records"); deck:275-276. **Leftover:** `content_hash` is still listed as a manifest field *and* defined as "the hash of the manifest" (DESIGN:345; deck:265). That is the C1 self-reference on a smaller scale. State that the hash is computed over the manifest with `content_hash` excluded, or that it is the store key and not a field |
| 2 | Rewrite `asks/rsi-saurav.md` and Saurav's block in `QUESTIONS-teammates.md` | **LANDED**, with one new defect | rsi-saurav.md:8-15 (the split, quoted from the supervisor), :28-30 ("RSI does not change a capsule's body"), :66-74 (*If the answer is no*); QUESTIONS-teammates.md:35-38 ("Settled: the build loop is yours"). **New defect (N7):** rsi-saurav.md:69-70 says a direct write "lands as *admitted, outside the active cap*" *until admission has run*. That puts an unadmitted version into an admitted exposure state, bindable by pin, which contradicts DESIGN:394 (uncertified means not loaded) and the ask's own item 1 |
| 3 | Withdraw "the one check no prior system performs" | **LANDED**; the replacement overclaims | grep finds no "no prior system" or "one check" anywhere. DESIGN:32-34, :910 (RelAIBuild credited); deck:499-501. **But** slide 13's new title, "Every prior system checks one stage" (deck:470), is false by the design's own §5.2:909. There, *When Self-Evolution Backfires* has pre-commit admission *and* trust tiers, which is exposure, and only Hot skills enter the prompt, which is selection. Slide 13's own row for that paper names two stages (deck:481) |
| 4 | Rewrite §6 claims 1 and 3 and slide 14; move the size claim off; make claim 2 conditional | **PARTLY** | §6 (DESIGN:1044-1071) and slide 14 (deck:516-528) are rewritten well. **Not propagated.** (a) Claim 1's retraction is contradicted by DESIGN:472 ("Step 1 is the direct answer to skill shadowing"), DESIGN:849 ("the deterministic filter is the shadowing defence"), deck:319 (slide 9 SAY: "the direct answer to picking the wrong entry"), routing-xiaoyang.md:42-43 and :75, and QUESTIONS-teammates.md:82-83. (b) Claim 2's body still says "a degraded judge produces rejections rather than silent acceptance" (DESIGN:1051-1052), and slide 10's THUS strip says the same (deck:354). The Blind Curator shows the opposite for a false-pass judge: it fails *silently* (summary, *Summary*, p6-8) |
| 5 | Main-slide citations that fail the read-in-full rule; fix deck:17 and the appendix | **PARTLY** | Slide 15 now cites only SkillFuzz, which has a *Claims checked* table. DarwinX is off slide 13. The four ⧗ papers moved to Backup 1 (deck:604-609). **Still false:** deck:17, "Every paper cited on slides 1 to 15 is read in full, by the author and by an agent". Cordis (slide 7 footer) is partial: its summary says the calculus (§3-4) was not read. Paper2Agent (slide 13 IF ASKED, deck:503) has no summary and no close-read note. The ✅ legend (DESIGN:44-47, :1139-1141) is misapplied at DESIGN:910 to RelAIBuild, whose summary read selected pages and has no claims table, and at DESIGN:920 to Paper2Agent, which was read in source only (`verify/V5`). Unread citations with no ⧗ remain: 2608.08453 (DESIGN:102, :1018, and §1.3's "each read in a source"), SkillPager 2606.00822 (DESIGN:437, "full read outstanding" but no ⧗), 2609.14119 (DESIGN:1030), CordisBench 2609.01600 (DESIGN:960). GraSP is "read in full" (DESIGN:445; Backup 1 deck:599) and SkillProbe is "read" (DESIGN:546; Backup 2), but neither has a summary or a close-read note |
| 6 | Add one position slide: agent-core, Symphony, the four models, the layer's calls in and out | **PARTLY** | Slide 11 (deck:379-421) is now a real position picture in the supervisor's layout, with Bind/Freeze/Execute. **Model routing is missing from it.** There is no box, no arrow and no owner for ranking, although §2.5 step 3 and §4.2 put ranking with routing and V6 asked for "filter before routing". The coverage table then claims "Slide 11 shows each neighbouring model's calls in and out" (deck:667). DESIGN has no matching figure, so the slide cites §3.1/§3.3/§4.2 for a picture that exists only in the deck |
| 7 | Fix the slide-1 function and §1.4 (selection ranking not ours; adding is RSI's) | **LANDED**, one leftover | deck:25 ("decides which capabilities are admitted, and which admitted versions a run may use"); DESIGN:194. **Leftover:** DESIGN:191 still says "Ranking: routing, or this model, open at the workshop", against DESIGN:469 and :845 and slide 9, which give ranking to routing |
| 8 | Delivery standard, "accountable" and Ground Truth on a main slide | **LANDED** | deck:100-102; DESIGN:162 |
| 9 | State agent-core as the route; drop "whichever passes the probe" | **LANDED**, one leftover | DESIGN:785-787, :813-815; deck:428-462; "Whichever passes" is gone. DSH is now only a reachable provider (`harness_providers/dsh/` exists). **Leftover:** the revision banner at DESIGN:15-16 still says the design "defers the DSH-versus-agent-core-versus-custom choice to a schedule decision" |
| 10 | H5 and the §4.1 facts; H1 exists; ToolCard; re-index; C11 skill-only graph | **LANDED**, with small errors | DESIGN:791-801, :810, :1027, :715-723, :761-762; deck:436-462. Errors: the H1 citation `extension_binder.py:27,45` points `:45` at an MCP bind *inside* apply, and the unapply is at `:64`. DESIGN:138 (§1.4, "compared against observed effects in a sandboxed run") and DESIGN:583 (§2.7 hole 3, "in a sandbox") still assume the observing sandbox that §4.1 says agent-core lacks. Slide 12's title is wrong (see N4) |

Score: 6 LANDED (four of them with leftovers), 3 PARTLY (items 4, 5 and 6), 0 NOT LANDED.

---

## 2. New contradictions and leftovers

Each has both locations. N marks a new contradiction introduced by this round; L marks an old claim that should have
gone.

**N1. `content_hash` still hashes a manifest that contains it.** DESIGN:345 lists `content_hash` in the manifest's
field table and defines it as "the hash of the manifest". Slide 8 (deck:265) does the same. This is the remaining
half of C1.

**N2 (L). The claim that the filter answers shadowing is withdrawn in §6 and asserted everywhere else.**
Withdrawn at DESIGN:1046-1048 and deck:526, :534-540. Still asserted at DESIGN:472, DESIGN:849, deck:319,
routing-xiaoyang.md:42-43 ("The deterministic filter is the shadowing defence") and :75, and QUESTIONS-teammates.md:82-83
("That filter is the defence against a measured 21-point pass-rate loss"). Routing is the one teammate whose
agreement this claim is used to win, so the ask repeats the claim the design retracted.

**N3. Claim 2 is made conditional in its title but not in its body, and slide 10 is not changed at all.**
DESIGN:1050-1052: "once the verifier's false-pass rate is measured … so a degraded judge produces rejections rather
than silent acceptance." Deck:354, slide 10 THUS: the same sentence with no condition. *The Blind Curator* summary
says the curator fails **silently** under false-pass bias, and the raw deprecation count and the eval score look
normal (Summary; Table 1 p6). A lenient judge produces silent acceptance. The strip on the slide that the Blind Curator
demonstrates says the opposite of the Blind Curator.

**N4. Slide 12's title contradicts its own table.** Deck:428, "agent-core provides four of the five properties",
and the SAY at deck:451, "Four are there or nearly there". The table on the same slide (deck:436-440) and
DESIGN:791-795 give H1 yes, H2 **no**, H3 graph artifacts only (the store is new work), H4 only once wired, and H5 tool
calls only. At most one is fully there. DESIGN:1083 says "H2 is missing".

**N5. Slide 13's title contradicts §5.2 and the slide's own rows.** "Every prior system checks one stage" (deck:470)
sits against DESIGN:909, where VaG has admission plus tiers, which are prior art for exposure, and against deck:481,
"three critics before commit, then trust tiers". The line under the table (deck:484, "some do more than this design at
that stage") softens it, but the title is what is read.

**N6. §5.1 misdescribes ScienceDiscovery as having no admission.** DESIGN:895-896: "What it lacks is admission: a
snapshot pins whatever was selected, whether or not anything checked it." ScienceDiscovery's own documents say
otherwise. `docs/zh/explanation/skill-self-evolution.md:13-21, 50-58, 221-247`: an agent calls
`propose_skill_library_update` and creates a *pending proposal*. Every automatic update must be dry-run for diff,
diagnostics and conflicts. Publishing needs the user's confirmation. "不让 Agent 静默 commit Skill Library" (the agent
never silently commits). "发布只创建新版本，不改写历史版本" (publish only creates a new version, never rewrites
history). These stages are marked 已实现, implemented. M2 plans "evaluation-assisted publish" with baseline/candidate
comparison. `skill-library-management.md:25-40, 339-380` adds immutable library versions, a per-run head-to-version
pin, deterministic recall, and a Prompt Manifest that records library version and package hash. The gate is a human,
not a contract check, and there is no declared contract. It is still an admission step, and it is the nearest system
to the whole design (see §5).

**N7. The RSI fallback puts an unadmitted version into an admitted state.** rsi-saurav.md:69-70 against DESIGN:293
(the state is "admitted, outside the active cap") and DESIGN:394 (uncertified means not loaded).

**N8 (L). The DSH deferral survives in the banner.** DESIGN:15-16 against DESIGN:785-787.

**N9 (L). Ranking ownership.** DESIGN:191 ("routing, or this model, open") against DESIGN:469, :845 and deck:308.

**N10. §1.4 and §2.7 still promise sandboxed effect observation.** DESIGN:138 ("compared against observed effects in a
sandboxed run") and DESIGN:583 ("admission compares declared against observed effects in a sandbox") against
DESIGN:797-801 (tool-call granularity on agent-core; an observing sandbox is new work) and deck:349.

**N11 (L). Paper2Agent is both "no admission gate" and "M3's gate, built and shipping".** DESIGN:920 and deck:503
against DESIGN:1087-1092. It is also marked ✅ at DESIGN:920, but nothing records an agent reading the paper, only a
source read in `verify/V5`. (§7 is deferred, but the contradiction reaches a main-slide speaker note.)

**N12. One contract shape across sizes: load-bearing, untested, or open ground?** DESIGN:67 ("narrower and still
load-bearing") and deck:65-66 (slide 2 SAY: "It is a wrapper with one contract shape across every size this design
claims") sit against DESIGN:1071 ("Not claimed as an advantage … untested") and deck:526 and :563-565. DESIGN:965
("the space is genuinely open: nobody … treating a composition unit as one contract shape across sizes") is the old
novelty claim, still standing.

**N13. The read-status line at the top of the deck is false.** Deck:17 against the Cordis summary ("Not re-read: the
calculus and metatheory (§3-4)") and against Paper2Agent on slide 13's notes. Backup 1 lists GraSP and RelAIBuild as
"Read in full by an agent" (deck:597-602). GraSP has no summary or note, and the RelAIBuild summary lists partial pages.

**N14 (L). The term `admission record` survives after the rename to certificate.** deck:93 (slide 3, Governance
row), routing-xiaoyang.md:37, verification-ramika.md:39. It is not a manifest field any more, so this is terminology
only. Use "certificate".

**N15. Is the certificate written once, or appended to?** DESIGN:357-359 says the certificate "is written once …
Revoking a capsule appends to both". Say that revocation appends a revocation record beside the certificate, not to it.

**N16. The deck's coverage table overstates slide 11.** deck:667 ("shows each neighbouring model's calls") against
slide 11, which has no routing (item 6).

**N17 (L). Assets and Data are amended in one table and declined in the next.** DESIGN:140-141 ("amended, see
below") against DESIGN:164 ("Decline") and deck:79 ("two declined").

**N18. The runtime is assumed to enforce manifest fields that no H-row covers.** DESIGN:192 ("the declared effects and
write scope the runtime enforces"), :351 ("the write scope the scheduler uses"), :352 ("a bound the runtime enforces")
and :627 ("under leases and declared write scopes"). None of H1–H5 asks agent-core to enforce a capsule's
`resources` or `effects.write`. agent-core's nearest field is `ToolCard.parallel_safe`, a boolean. This is a missing
row in requirement (d).

**N19 (L). Two predictions about the gate-off arm.** DESIGN:1127 ("arm two should be at or below arm one") against
DESIGN:81-86 (Alita-G, an outcome-only library, +7.9 pp). C4 is unresolved. §7 is deferred, but the premise is in §1.3.

**N20. Units that were never skills enter "through this model's own binding path", which has no mechanism.**
DESIGN:761-762 and deck:417-418. The capsule layer "declares and the harness executes" (deck:70-71), so it has no
execution path of its own. agent-core does have one: `apply_extension_hot` binds tools, MCP servers, rails, skills and
subagents onto a live `DeepAgent` (`harness/extension_binder.py:27-60`). A gate could be a rail and a model-call
wrapper a tool. Name that path. As written, "our own path" sounds like a second runtime.

Leftovers checked and **gone**: "no prior system", "library loop", `admission_record` as a manifest field,
`write_scope` as a separate field (DESIGN:618 now only records the correction), "nothing in openJiuwen provides",
"Whichever passes the probe", and the capsule model building or improving capsules. DSH as a live candidate is gone
except in the banner (N8).

---

## 3. Paper claims on main slides 1–15, checked against summaries

**Read status of every paper cited on slides 1–15, including speaker notes.**

| Paper | Slide | Summary with *Claims checked*, or note 20–38 | Rule |
|---|---|---|---|
| Alita-G 2510.23601 | 4, 13 | notes 21, 27 | pass |
| Beyond Task Completion 2604.00392 | 4, 10 | note 29 | pass |
| Library Drift 2605.19576 | 4, 9 | claims table | pass |
| More Skills, Worse Agents? 2605.24050 | 4, 14 | claims table | pass |
| Darwin Gödel Machine 2505.22954 | 6, 13 | note 36 | pass |
| Cordis 2608.25512 | 7 (footer) | note 20; the summary itself says partial | pass by the rule, but contradicts deck:17 "read in full" |
| AllocBench 2607.23332 | 7 | note 38 | pass |
| CoEvoSkills 2604.01687 | 7, 13 | note 35 | pass |
| Don't Offer What Can't Be Done 2608.01050 | 9 | claims table | pass |
| The Blind Curator 2607.07436 | 10 | claims table | pass |
| When Self-Evolution Backfires 2608.05810 | 10, 13, 15 | claims table | pass |
| Cognitive Admission Control 2609.16313 | 10 | claims table | pass |
| SkillFuzz 2607.02345 | 15 | claims table | pass |
| **Paper2Agent** | 13 IF ASKED (deck:503) | **none** (only `verify/V5`, a source read) | **FAIL** |
| RelAIBuild 2606.26924 | 13 IF ASKED, unnamed ("file-scope drift checks") | summary, **no claims table, partial pages** | borderline. It is unnamed on the slide, so it passes; if it is named, it fails |

**Claims that go beyond the summary.**

1. **Slide 10 THUS (deck:354): "a degraded judge produces rejections rather than silent acceptance."** It contradicts
   the paper on the slide. Under false-pass bias the curator fails *silently*, and the eval score and deprecation count
   look normal (Blind Curator summary, Summary and Table 1 p6). **MUST.**
2. **Slide 9 SAY (deck:319): "Step one is the direct answer to picking the wrong entry."** The 2608.01050 summary
   says the paper measures selection only, with no end-task effect (claims row e). The 2605.24050 summary says most of
   the shift at 202 skills is *no skill invoked*, 38.5% against 8.9% wrong (claims row b), and that its distractors are
   "not skills whose preconditions fail". The design's own §6 claim 1 now says this. **MUST.**
3. **Slide 4 table and SAY (deck:138, :151-152): Library Drift, "retiring what does not earn its place carries the
   gain".** The summary's claims row b says "no run removes retirement or the cap". The paper *names* retirement as
   load-bearing, but no ablation removes it. Say "the paper names retirement and the authoring prior as load-bearing".
   DESIGN:94-95 is worded the same way. **SHOULD** (V6 item 16, not landed).
4. **Slide 15 row and IF ASKED (deck:561, :580-581), and DESIGN:561: "most of the drift is out of task scope, which
   declared effects do not show."** The SkillFuzz summary says "*many* intents are about the task's scope". Its
   taxonomy is Unsanctioned Data Analysis 43%, Audio/Video Side-Effect 26%, Covert Resource Creation 22% and
   Unauthorized Tool Invocation 10% (RQ4, Fig. 7 p9-10). That puts 58% in categories that are writes, resource creation
   or tool calls, which effect labels could at least partly see. "Most" is not supported. Use "much", or "the largest
   cluster (43%)". **SHOULD.**
5. **Slide 7 IF ASKED (deck:240-241) and DESIGN:274-275: "commitment on first sight rising to 92%."** That is Claude
   Opus 4.8 at R2 only. Haiku 4.5 is 99% and GPT-5.4-mini is 85% (note 38:60-62). Name the model or give the range.
   **COULD.**
6. **Slide 14 IF ASKED (deck:539-540) and DESIGN:1047-1048: "the distractors could all run".** The summary says the
   distractors are "relevant-looking but unhelpful" and "not skills whose preconditions fail". That supports "were not
   inexecutable", but not the word "all". **COULD.**
7. **Slide 10 SAY (deck:359-360): "genuine retirement all but stopped".** This is literal, but the clean baseline is
   1.3 per run and the unbiased real judge retired 10.3 (Table 1 p6). The IF ASKED line covers the 0.45 point but not
   the small base. **COULD.**

Checked and **supported**: Alita-G 75.15 → 83.03, 165 questions, Sonnet 4 with GPT-4.1 (note 21:24, :203).
Beyond Task Completion: 215/222, median 11, Haiku 4.5, 3 seeds × 8 sessions (note 29; paper lines 173, 201).
More Skills: 0.49 → 0.28 and up to 68%. DGM: 2.00 by deleting the marker code (note 36:120-146); compile and keep
the ability to edit code (note 36:44-45). CoEvoSkills: 41.1% without the surrogate verifier against 42.4% with
background alone, and 71.1% (paper lines 928, 958, 967). 2608.01050: 1,039,462 of 1,749,270 pairs from 174,927
matched messages, 7.8% replay, with the parity proviso now on slide 9 (deck:322-323). 2608.05810: 1.7 of 12.3, about
a seventh, one run on the distillation split. Blind Curator setup: 12 rounds, 3 seeds, q ∈ {0.2, 0.45, 0.7}; 0.45 as a
derived point; strict grader with ρP→F ≈ 0.95. CAC: satisfied/violated/unknown, certificate, single actions. SkillFuzz:
196 skills, 10 tasks, 8 planners, k ≤ 5, 4.7% → 14.5% → 66.5%, harm never judged, prose skills only.

---

## 4. The openJiuwen citations added this round, checked against source

| Citation (where) | What the source shows | Verdict |
|---|---|---|
| `symphony/orchestration/graph/build.py:161` (DESIGN:717) | `if fingerprint.type not in {"skill", "subagent", "agent"}` → registry error | **Correct** |
| `symphony/orchestration/mutation_service.py:230` (DESIGN:720) | the check is at `:228` (`request.source_revision != target_snapshot.snapshot_id`), and `:230` is its message | **Correct** (off by two) |
| `symphony/graph_engine.py:113-121` (DESIGN:722) | `plan(query, candidate_ids=…, *, …, disabled_capability_ids=…)` | **Correct** |
| `symphony/evaluation/suite.py:85-87`, `interfaces/graph.py:15` (DESIGN:682, :686) | verbatim at `e23806c10732` | **Correct** |
| `harness/extension_binder.py:27,45` (DESIGN:791) | `:27` is `apply_extension_hot` ("On failure, unapplies refs already bound"). `:45` is `_bind_mcp` inside apply. The reverse-order undo is `unapply_extension_hot` at **`:64`** ("Undo bindings … (reverse order)") | **Miscited**: use `:27,64`. The substance is correct: tools, MCP servers, rails, prompt sections, skills and subagents are applied and unapplied |
| `symphony/orchestration/artifacts.py` (DESIGN:793) | exists, graph artifacts | **Correct** |
| `agent_evolving/trajectory/store.py:135` (DESIGN:794) | `FileTrajectoryStore`, "Append-only JSONL archive of canonical trajectories" | **Correct** |
| `harness/observability/rail.py:888-949` (DESIGN:795) | `before_tool_call` opens an `execute_tool` span with tool name, call id and args | **Correct** |
| `harness/security/permission_engine/core.py:272` (DESIGN:795) | `async def check_permission(self, tool_name, …)` | **Correct** |
| `core/foundation/tool/base.py:78-108` (DESIGN:810) | `exposure` :83, `parallel_safe` :92, `stateless` :100, and `idempotent` at **:109** | **Correct** in substance; the range misses `idempotent` by one line |
| `harness_providers/dsh/` (DESIGN:809) | exists | **Correct** |
| `skillhub/docs/zh/4. 用户指南/发布Skill.md:43-54` (DESIGN:886) | :43 "提交后新版本进入审核；市场对外版本在审核通过前不会切换"; table :48-54 | **Correct**, with one omission. The AI/rule review (审查中) runs only when `MARKET_SKILL_REVIEW_ENABLED` is set (:50). Administrator approval is unconditional. "enters AI or rule review and then administrator approval" should say the first is optional |
| `sciencediscovery/docs/en/explanation/cas.md:9-27` (DESIGN:891) | SHA-256 OCI-layout CAS; `put` publishes "by an atomic, non-replacing hard link"; `read(hash)` "to retrieve bytes"; `verify(hash)` "to retrieve and re-hash" | **Overstated.** "hash verification on every read" is **not** what it says. `read` does not re-hash, and `:51` says integrity checks and the Reviewer use `verify`, while content, diffs and previews use `read`. Say "hash verification on demand (`verify`)" |
| `sciencediscovery/…/skill-progressive-disclosure.md:34-37,54-57` (DESIGN:893) | :34-37 is the staged read-only package and a snapshot manifest "recording each staged skill id, revision, version, and package hash"; :56 says staging exists so a mid-run edit cannot break "the fixed revision and package hash recorded in the Prompt Manifest"; :65 says "an execution can be replayed against an exact package" | **Overstated.** Nothing in these lines, or anywhere in `docs/`, says the staged package is **verified against the hash before the sandbox starts**. The documents say the hash is *recorded* and the package is *frozen*. "Pinned and recorded by package hash" is supported; "verified before the sandbox starts" is not. The V6 wording, repeated here, has no source line |
| `symphony/models/fingerprint.py:29-44`, `flow/narrative.py:25`, `discovery/skillfs.py:480, 615-618` (DESIGN:1017, :1027) | fields as tabled; `index_state` missing/fresh/stale; `"indexed-stale"` | **Correct** |
| Slide 12 IF ASKED (deck:459-460): ScienceDiscovery "already has an observing sandbox runner with an egress gateway" | `sandbox-execution.md` (V6's read: Bubblewrap, seccomp, egress gateway) | Not re-checked line by line this round. It was consistent with V6 |

**Missed in-family source, the most important finding of this pass.** `sciencediscovery/docs/zh/explanation/skill-library-management.md`
and `skill-self-evolution.md` (commit `3792cd6`, "publish reviewed drafts to libraries"; types in
`packages/schema/src/skills.ts:149-233`) are openJiuwen's own design for the layer this document proposes. They
cover a versioned skill library, atomic batch commits, rollback, a self-evolution write-back API with an
`evaluation` summary and `baselineVersionId`, agent *proposals* that are never silently committed, human-confirmed
publish, per-run resolution of `head` to a fixed version, deterministic recall, and a Prompt Manifest carrying
`skillLibraryRefs` and package hashes. The design's non-goals (skill-library-management.md:39) explicitly exclude
"判分…门控回滚" (scoring and gate/rollback logic) and leave the publish decision to the application layer. That is
the socket a capsule admission gate fits into, and the best alignment argument available to the design. It is not
cited anywhere.

---

## 5. §6 and slide 14, re-judged claim by claim

| # | Claim | Strongest competitor | Verdict | Reason |
|---|---|---|---|---|
| 1 | Removes what cannot run before anything chooses | 2608.01050 (deployed, same mechanism); GraSP (compile-time precondition rejection); Symphony's `plan(disabled_capability_ids=…)` | **SURVIVES as a property, not as an advantage** | It is now honest about shadowing. But it is adoption of 2608.01050, not something the design does better. The falsifier tests whether the filter is implemented correctly ("a candidate it passed fails a precondition it declared"), not whether it beats anything. The retraction is also undone in §2.5, §4.2, slide 9 and the routing ask (N2) |
| 2 | Cannot silently stop working, once false-pass is measured | *The Blind Curator*'s own prescription (audit the false-pass rate by defect injection before use, p5, p9) | **WEAKENED** | The conditional is right, and it is the paper's recommendation adopted, not a difference. The body sentence still has the direction wrong (N3). The falsifier checks only that a ceiling rule exists. It cannot catch the case the paper warns about, a false-pass rate measured on injected defects that does not match real failures (summary, Limitations) |
| 3 | The exact capability set a run used is recoverable | **ScienceDiscovery**: the Prompt Manifest records library version, skill ids, revisions and package hashes per run, and "an execution can be replayed against an exact package" (skill-progressive-disclosure.md:65; runtime-behavior.md:36) | **WEAKENED to parity** | True, and correctly not called replay any more. But openJiuwen already implements it in a sibling. It beats Symphony, skillhub and jiuwenswarm, not openJiuwen |
| 4 | One contract through admission, exposure, selection and provenance | **ScienceDiscovery skill library plus self-evolution** (above): one versioned identity through proposal and publish, mount and whitelist, recall, and manifest, with a human gate and M2 baseline/candidate evaluation planned. **RelAIBuild**: one content-hashed spec carried through phase gates, AC→file→test traceability, hash-gated install and an append-only audit log, but for coding-agent builds (summary p20-21). **VaG**: admission, tiers and prompt exposure in one loop, with no versions | **WEAKENED, but defensible if restated** | No system read carries a *declared behavioural contract* (preconditions, postconditions, effects) that admission *tests* and selection *filters on*. ScienceDiscovery carries an *identity*, not a contract, and gates by a person. RelAIBuild carries a spec in another domain. VaG has no versioned identity. Two problems in the wording. (i) "every stage checks the same declaration" is overstated: exposure checks certificates and exposure state, and provenance checks hashes, not the declaration. Only admission and selection read the contract. (ii) The claim does not name ScienceDiscovery, so the first openJiuwen reader who knows it will read claim 4 as unaware. **Defensible restatement:** "the same declared contract is what admission tests and what selection filters on, and both are bound by hash to what a run pins. ScienceDiscovery already carries the identity through those stages and leaves the gate to the application. This design supplies the contract and the gate." |
| 5 | Builds on agent-core and aligns with openJiuwen | ScienceDiscovery again: openJiuwen's own library and self-evolution design is TypeScript and not agent-core; openJiuwen's executed admission is in `rsi/artifact_rsi/program_opt/` | **WEAKENED** | Honest about the new work (store, entry path, observing sandbox). The falsifier only covers skill-shaped capsules. Alignment with openJiuwen is argued from Symphony alone. It ignores that openJiuwen's library model (ScienceDiscovery) and its admission engine (`rsi/`) are both elsewhere, and V6 SHOULD 18 (why admission is in CC when openJiuwen puts it in RSI) is still unaddressed |

**Is claim 4 a defensible contribution?** Yes, narrowly, and only after the restatement above. I found no system that
carries a declared precondition/postcondition/effects contract into both an executed admission gate and a
deterministic selection filter, bound by hash to per-run pins. I did find one in openJiuwen that does everything
around it except the contract and the automated gate, and the design does not mention it. Until it does, claim 4 is
exposed to exactly the "adoption, not contribution" falsifier it names.

---

## 6. Requirements a to f, re-judged

| Req | Verdict | One line |
|---|---|---|
| **a. Function** | **ANSWERED** | Slide 1 and §1.4 now agree: admit, and expose to runs; never build or rank. Only DESIGN:191's "ranking open" is left over |
| **b. Architecture** | **ANSWERED** | C1/C2 fixed, effects taxonomy adopted, H5 granularity honest. The remaining defect is `content_hash` as a self-referencing field (N1) |
| **c. Position** | **ANSWERED** (one omission) | Slide 11 is a real position picture in the supervisor's layout with Bind/Freeze/Execute. Model routing, one of the four models, is not on it, and DESIGN has no matching figure |
| **d. Dependencies** | **WEAK** | The platform side is now the best-evidenced slide in the deck, apart from its title (N4). The dependencies on RSI, routing and verification appear on no main slide (§4.2 is cut, deck:667). What depends on this model, and what fails if it is late, is still not stated. The sandbox owner and the definition of "different author" are open. Runtime enforcement of `resources` and `effects.write` is assumed without an H-row (N18) |
| **e. Similar designs** | **WEAK** | Broad and more honest (RelAIBuild, VaG tiers, skillhub, ScienceDiscovery CAS). But the nearest system, ScienceDiscovery's library and self-evolution design, is missing and §5.1 misdescribes it (N6), and slide 13's title overclaims (N5) |
| **f. Advantages** | **WEAK** | Now honest and falsifiable, which is a real improvement. After honesty, claims 1–3 are adoption or parity, and claim 5 is a requirement met. The only difference is claim 4, which needs its restatement and the ScienceDiscovery comparison to hold |

---

## 7. Ranked fix list

**MUST before tomorrow**

1. **Slide 10 THUS (deck:354) and §6 claim 2 body (DESIGN:1051-1052).** Replace "a degraded judge produces
   rejections rather than silent acceptance" with the conditional: "with a measured false-pass rate and a ceiling on
   it, a lenient judge is detected and its verdicts drop to advisory". As it stands, the strip contradicts the paper
   in the slide's own DEMONSTRATED BY.
2. **Propagate claim 1's retraction.** Change DESIGN:472, DESIGN:849, slide 9 SAY (deck:319),
   routing-xiaoyang.md:42-43 and :75, and QUESTIONS-teammates.md:82-83 from "direct answer to shadowing" or "the
   shadowing defence" to "removes provably inexecutable candidates. It is not shown to fix the no-skill-invoked
   failure that dominates at scale."
3. **Slide 12 title and SAY (deck:428, :451).** "four of the five" is false against the table on the same slide. Use
   something like "agent-core has one property fully, three in part, and lacks one".
4. **Name ScienceDiscovery's skill library and self-evolution design in §5.1, §6 claim 4 and slide 13's SAY, and
   correct DESIGN:895-896.** It has an admission step (proposal, dry-run, human-confirmed publish, append-only versions,
   per-run pinning, recall, a hash manifest; M2 plans baseline/candidate evaluation). Restate claim 4 as in §5 above:
   *the declared contract that admission tests and selection filters on, bound by hash to what runs*. Say that
   ScienceDiscovery leaves the gate to the application layer (skill-library-management.md:39), and that this design
   supplies it. This is also the strongest "aligned with openJiuwen" argument available.
5. **Slide 13 title (deck:470).** "Every prior system checks one stage" is contradicted by VaG on the same slide. Use
   something like "Each prior system covers part of the path. None carries a declared contract through it."
6. **Read-status honesty.** Fix deck:17: Cordis is partial, and Paper2Agent on slide 13's notes has no agent read.
   Either drop Paper2Agent from slide 13's IF ASKED or mark it unread. Remove ✅ from RelAIBuild (partial pages, no
   claims table) and Paper2Agent in DESIGN §5.2, and fix Backup 1's "Read in full by an agent" for GraSP and RelAIBuild.
7. **Correct the two overstated ScienceDiscovery source claims (DESIGN:891-893).** "hash verification on every read"
   should be "on `verify`". "verified against the recorded package hash before the sandbox starts" has no source line;
   say "frozen and recorded by package hash".
8. **Add model routing to slide 11**: ranking within the filtered set, between "Symphony plan over the filtered ids"
   and bind. Fix the coverage line at deck:667.

**SHOULD**

9. Fix `content_hash` self-reference (N1): say the hash is over the manifest with `content_hash` excluded, or make
   it the store key rather than a field (DESIGN:345, deck:265).
10. Fix the RSI ask's fallback (rsi-saurav.md:69-70): an unadmitted direct write must be "not loaded" (row 2 of
    §2.3.1), not "admitted, outside the active cap".
11. Put one line per teammate dependency on a main slide (requirement d). For each, say what this model needs from
    them and what fails without it. Add an H-row or a note for runtime enforcement of `resources` and `effects.write`
    (N18).
12. Remove "sandboxed run" and "in a sandbox" at DESIGN:138 and :583, or qualify them as tool-call level on agent-core.
13. Library Drift wording on slide 4 and DESIGN:94-95: "the paper names retirement and the authoring prior as
    load-bearing". No ablation removes retirement.
14. SkillFuzz "most of the drift is out of task scope" (deck:561, :580; DESIGN:561): use "much", or cite the 43%
    cluster. The other 58% are writes, resource creation and tool calls.
15. Resolve N12: either drop "load-bearing" (DESIGN:67), slide 2's "one contract shape across every size" and §5.3's
    "space genuinely open" (DESIGN:965), or stop calling the size claim untested. It cannot be both.
16. Name the entry path for non-skill capsules as agent-core's `apply_extension_hot`, which binds tools, rails and
    subagents (N20), rather than "this model's own binding path".
17. Address openJiuwen placing admission in `rsi/program_opt` (V6 SHOULD 18). The ScienceDiscovery comparison from
    MUST 4 makes this one sentence.
18. Clean up the leftovers: the DSH banner (DESIGN:15-16), "ranking open" (DESIGN:191), `admission record` (deck:93
    and two asks), Assets/Data "amended" versus "declined" (DESIGN:140-141), certificate "written once" versus
    "appends to both" (DESIGN:357-359), and Paper2Agent as both "no gate" and "M3's gate" (DESIGN:920 against
    :1087-1092).
19. Add ⧗ to the unread citations with no mark: 2608.08453 (DESIGN:102, :1018), SkillPager (DESIGN:437), 2609.14119
    (DESIGN:1030), CordisBench (DESIGN:960). Either give GraSP and SkillProbe a note, or mark them.

**COULD**

20. Fix `extension_binder.py:27,45` to `:27,64`, and `base.py:78-108` to `:78-112`.
21. State that skillhub's AI/rule review is flag-gated (`MARKET_SKILL_REVIEW_ENABLED`, 发布Skill.md:50).
22. AllocBench 92%: name Opus 4.8, or give the 85–99% range.
23. "the distractors could all run": drop "all".
24. Slide 10 SAY: give the Blind Curator clean baseline, 1.3 retirements per run.
25. C4 and §7.4's prediction (deferred with (g), but the premise is in §1.3).
26. "Four things genuinely change" against five rows (DESIGN:425, deck:665-666).
