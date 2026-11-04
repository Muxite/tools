# R7 — Consistency Audit & Short-Talk Readiness

Scope: VARIANT-1 (215 ln), VARIANT-2 (451 ln), VARIANT-3 (1329 ln), cross-checked
against GLOSSARY.md and AUDIENCE.md. New constraint: **the talk is short.**

---

## 1. Contradiction table

| # | Claim | VARIANT-1 says | VARIANT-2 says | VARIANT-3 says | Which is right |
|---|---|---|---|---|---|
| 1 | **End-to-end run count/status** — the single most important status claim in the set | §7: "At least three full end-to-end runs have completed with all gates passed — two of 14 nodes and one of 15." | §5: "A complete 15-node end-to-end research run passed on 2026-09-03... " — one run, no mention of any 14-node runs. | §33 (and Executive Summary Finding 5, and Discrepancy Ledger #3): exactly **one** demonstrated run — the 15/15-node run of 2026-09-03. Ledger #3 explicitly records that an earlier handoff doc's claim of an E2E run was *failed and never re-accepted*, superseded by the 15/15 pass. Recommended formulation is explicitly singular: "a complete 15-node end-to-end research run." | **V2/V3 are right; V1 is unsupported and contradicted by V3's own ledger.** V1's "two of 14 nodes" runs appear nowhere else and directly conflict with the ledger's account that the only other E2E attempt on record *failed*. This must be fixed before the supervisor sees more than one document — it is exactly the kind of claim a hostile expert will cross-check. |
| 2 | **Research-question count in the SoTA briefing**, cited by V3 | — | §6 contains questions numbered 1–33 (33 total). | §35: "a companion briefing document describes thirteen mechanisms in vendor-neutral terms with **twenty-eight** research questions." | **V2 is right (33); V3 undercounts by 5.** Minor but a real number mismatch between documents describing each other. |
| 3 | **Average routing candidates per logical operator** | — | M7: "a routing table maps each role to an ordered candidate list (**average 2.8** candidates)" | §10: "44 of 45 roles are bound to ordered candidate lists averaging **2.75** candidates" | V3 is the verified figure (labelled [verified]); V2's 2.8 is a rounding drift, not sourced as independently verified. V1 doesn't state the number, so no exposure there — but V2 and V3 should agree exactly since V2 claims commit-verified provenance. |
| 4 | **AutoSci parity unit label** | not mentioned | "tracks a real upstream research-agent project called AutoSci across 28 **native capabilities**" | "tracks a real upstream, AutoSci, across 28 native **skills**" | Same number, different noun. Cosmetic, but sloppy for a document (V2) whose whole premise is "verified by direct code inspection" — pick one term and use it in both. |
| 5 | **Self-score numbers** (project's own scoring document) | not mentioned | Gives the actual numbers: "58/60, placing LangGraph at 31/60" | §34 states "twelve dimensions... not independently validated" but **drops the 58/60 and 31/60 numbers entirely** | Not a contradiction, but an unexplained asymmetry: the more skeptical document (V3) has *less* of the self-serving number than the neutral briefing (V2). A supervisor reading V3 alone won't know the score is 58/60 — which is arguably the single most "hostile-to-hype" fact in the whole set and belongs in V3, not just V2. |
| 6 | **"A run cannot soften its own passing criteria"** | §5 (THE FREEZE): stated flatly, no caveat — "A run therefore cannot later soften its own passing criteria." | Not stated with this framing; M4 instead raises an open question about whether the freeze is "meaningfully stronger than conventional checksumming." | §7: the claim about `test_policy` being frozen is true and confirmed — **but** the same section adds "What the hash does NOT cover" — `write_scope`, artifact-name text, and human-review state live in `task_graph.contract.json`, which is **not** referenced by `contract_sha256`, and can be edited post-freeze without invalidating the hash. V3 explicitly says "Any presentation of it should state that boundary." | **V1 states the strong claim without the caveat V3 says must accompany it.** The specific claim (grading rules can't be softened) is technically true — `test_policy` really is hashed — but V1 presents the freeze's integrity as broader than V3's own analysis supports, and omits the one nuance V3 flags as mandatory for any presentation of this mechanism. |
| 7 | **Model self-grading characterisation** | §4: describes the demotion of fidelity findings to advisory (`_demote_exhausted_fidelity_findings()`) and that requirement-stage review is "advisory by design." | Not detailed to this depth (M3 mentions the reviewer "cannot rewrite the artifact"). | §4 confirms both V1 claims *and* adds a third gap V1 omits: if `SOLAR_INTENT_REVIEWER_MODEL` is unset, "the same model reviews its own output." | Not contradictory, but V1 and V3 no longer fully agree on completeness — V3 has one more self-grading gap than V1 reports. Given the supervisor is exactly the audience who will ask "so can it ever grade itself?", this third gap should be at minimum in V1's backup material. |
| 8 | **Regression suite figure** | §7: "606 passed, 34 failed, 8 skipped" | (not explicit, but consistent — see §5, itemized failures) | §33: "606 passed / 34 failed / 8 skipped" | **Consistent across all three.** No issue. |
| 9 | **Capsule counts (80/77/1/2), logical (45), physical (102), artifact types (76), evidence schemas (33), journey tests (25), L2 features (142), atomic rows (1,502), tracked files (5,386), capability dimensions (15)** | Matches where stated | Matches | Matches, all [verified] | **Consistent.** These numbers were checked individually and agree everywhere they appear. |
| 10 | **Vendor-neutral split (52) and the 19-of-52 refinement** | §5: states 52, notes "only 63 of the 102 are enabled, and only 19 of the 52 carry the full vendor-neutral field set" | §2 table states 52 plainly, without the 19-of-52 or 63-of-102 caveats (M9/M5 area doesn't restate it either) | §10: states 52, with the 19-of-52 breakdown and the 63/102-enabled caveat, matching V1 exactly | **Consistent where both give detail; V2 is simply less caveated.** Not wrong, since V2's own framing note (§5, "Declared does not mean enforced") gestures at the same caution generally — but a careful external reader comparing V1 and V2 could walk away thinking 52 is a cleaner number than it is. Acceptable given V2's role, but worth a one-line addition. |
| 11 | **HIVE / capability token / trust-class discrepancy** | Not mentioned at all | Not mentioned at all (out of scope — not one of the 13 mechanisms) | Fully covered: HIVE is decision-only with zero cross-references to `harness/` (§12); the capability-token path-checker has no production callers (§9, ledger #6); the trust-class rank-vs-exact-match discrepancy is explicitly left unresolved (§17, ledger #9) | **No contradiction — but see cross-reference bug below (item 2 in the broken-refs list): §17's own pointer to the trust-class discrepancy write-up ("See §22") does not land on relevant content.** |

**Net verdict on the contradiction audit:** everything that is pure inventory (headcounts, schema counts, suite figures) is solid across all three documents — someone was disciplined about keeping those in sync. The failures are concentrated exactly where the task predicted they would be: **status/narrative claims** (the run count) and **claims about the strength of a guarantee** (the freeze). Item 1 is a real defect that must be fixed before the talk, not a nitpick.

---

## 2. Broken cross-references (VARIANT-3)

1. **§1.3, line 157: "A discrepancy ledger appears at §9."** — §9 is "Stage 7 — Dispatch." The discrepancy ledger is actually **§37**. This is a genuine broken reference, and it's in the report's own methodology section, which is a bad place for one.
2. **§17, line 750: "See §22."** — attached to the trust-class rank-vs-exact-match discrepancy. §22 is "The result vocabulary" (PASS/FAIL/etc.), which has nothing to do with trust classes. The correct target is almost certainly **§37** (discrepancy ledger #9), which *does* correctly self-cite §17 in the other direction (line 1270: "unresolved; both call sites cited (§17)"). So the ledger→§17 link works; the §17→ledger link is broken.
3. **Informal subsection references ("§29b", line 1229) don't match the TOC's numbering scheme.** §29's subsections are headed `### (a)`, `### (b)`, … `### (g)` — never given numeric labels like "29a"/"29b" anywhere in the document body. "§29b" is decodable by a careful reader (it's "Separating semantic from structural validation," the discovery semantic-scope defect) but it's an invented numbering convention that doesn't appear as an actual heading. Not fatal, but inconsistent with the otherwise-precise §-numbering used everywhere else, and worth fixing to "§29(b)" or giving the subsections real numbers.

All other `§NN` references checked (§1, §1.3, §2–§39, §5, §7, §9 [dispatch as a legitimate target elsewhere], §14, §17, §20, §22, §31, §32, §33, §35, §35b, §37) resolve correctly to existing headings.

---

## 3. Proposed minimal spine for a SHORT talk

Given the new constraint, assume 8–10 minutes of speaking, not V1's full ~10-minute reading time as currently paced (V1 as written is closer to a 12–15 minute spoken talk once the table and the bug story are delivered aloud). Target beats and rough time budget:

| Beat | Content | Time |
|---|---|---|
| 1. The one idea | The freeze: "model interprets meaning, code freezes and executes a contract." State it as the one sentence to remember. | 60s |
| 2. What it's for | One line: local dev-machine tool, two workloads (code + research), research must emit structured evidence not prose. | 30s |
| 3. One request, end to end | The 9-stage table, but spoken as a narrative, not read row by row — pick 3–4 stages to actually narrate (intake→intent, the freeze, dispatch, delivery), gesture at the rest. | 2.5 min |
| 4. Capsules, briefly | One sentence: "a capsule is a typed function signature with declared effects." Give the invariant quote ("admit what you do not know, do not grade your own work") — this is the best single line in the document and should survive any cut. | 60s |
| 5. Honest status (moved up — see below) | 606/34/8, one demonstrated 15-node run with a mid-run fix, release-candidate maturity, "not yet unattended." State this plainly and early-ish, not buried at the end. | 90s |
| 6. What's real vs aspirational | One line: two design docs describe a marketplace/signing/trust-score system that isn't built; "verification" here means schema checks, not formal proof. | 45s |
| 7. Close | A short, punchy closer — see §3 assessment below for what to use instead of the full deadlock story. | 45s |

Total: ~7–8 minutes, leaving room for Q&A, which is where the supervisor will actually spend their attention.

---

## 4. What to cut from VARIANT-1 to fit a short slot

Be ruthless. Specific cuts, quoting what to drop:

- **§5 "How capabilities reach hardware" — cut the whole section from the main line.** The logical/physical operator split, the 45/102 numbers, the routing-candidate mechanics, and the 52/63/19 vendor-neutral caveat chain are precisely the kind of depth that belongs in backup slides. Replace with a single spoken sentence: "plans bind to roles, not models, so a quota outage doesn't break the run" — and drop the paragraph of caveats entirely from the main line.
- **§6 "Three things worth noticing" — cut two of the three bullets.** Keep "claims are hash-bound to their sources" (concrete, memorable, directly supports the anti-fabrication theme). Cut "it refuses to treat an attempt as an outcome" (three sub-bullets of internal mechanism detail — dispatch receipt vs evaluator, hash recomputation, finished vs accepted) and cut "its tests use negative controls" — both are backup material, not spine.
- **§3, the stage table — trim from 9 rows to a spoken 4–5.** As written it is a full pipeline reference table (good for a *reading* document) but too dense to read aloud in a short talk. Keep Intake→Intent, THE FREEZE, Dispatch, Delivery; compress Requirement/Planning/Scheduling into one connecting sentence.
- **§4's capsule bullet list ("When it applies... Composition... Who may run it") — cut to one sentence plus the two invariant quotes.** The six-item bulleted anatomy is reference material, not a spoken beat.
- **The "5 capsule files sit on disk unregistered" detail** — true and interesting, but it's a footnote-level fact, not spine. Cut from the main line, keep as backup ("what happens if someone drops a new capsule file in?").

## 5. Is VARIANT-1 front-loaded correctly, or does the important content arrive too late?

**Too late, and this matters more now that the talk is short.** As currently ordered, §7 ("Where it actually stands" — the honest status, the 606/34/8 figure, "not yet routinely reproducible unattended") is the **second-to-last** section, arriving after the reader/listener has already absorbed capsules, operators, and "three things worth noticing." In a short talk that content may simply not be reached, or will land as a rushed afterthought right before the closing story — exactly backwards for an audience whose most important member (the supervising SWE) is "hostile to hype" and will judge the talk primarily on whether the status claim is honest and arrives *before* they've had to ask for it.

**Recommendation:** pull a compressed version of §7 forward to immediately follow §1 (the one idea) — as a single "here's what's actually built vs. what's still proving itself" beat, 60–90 seconds, before the worked example. Keep the fuller status discussion (documentation gaps, AutoSci non-parity, maturity language) as the closing beat too if useful, but the *first* honest-status statement should not arrive at minute 8 of an 8-minute talk. It should not lead either — leading with limitations before establishing what the system does would itself read as apologetic — so the right slot is beat 2 or 5 of the proposed spine above (§3), not first and not last-only.

## 6. Three things that should be BACKUP material only

1. **The logical/physical operator routing mechanics** (§5 in full: 45/102 breakdown, routing conditions, the 52/63/19 vendor-neutral caveat chain). Surface only if asked "does it depend on one AI vendor?"
2. **The capsule anatomy bullet list and the "5 unregistered files" detail** (§4). Surface only if asked "how do you add a new capability?" or "what stops someone from just adding a rogue capsule?"
3. **"Three things worth noticing" minus the citation-hashing bullet** — i.e., the attempt-vs-outcome three-way distinction and the negative-controls testing detail (§6). Surface only if asked "how do you know it actually ran, not just that it was dispatched?" or "how are capabilities tested?"

---

## 7. Opening and closing assessment

**Opening (§1, "The one idea").** Works well and should not change much. The compiler analogy is the single clearest framing in the whole set, lands in one paragraph, and gives the one-sentence takeaway the audience profile explicitly asks for ("the freeze is a lockfile" is even suggested in AUDIENCE.md — **note: V1 never actually uses the word "lockfile"** in its own text, even though the Glossary uses it as the canonical analogy for this exact concept. That's a missed opportunity and a minor consistency gap against AUDIENCE.md's own prescribed technique — worth adding one clause: "a frozen contract — think of a dependency lockfile" — to §1 or §3's freeze row.)

**Closing (§8, the deadlock bug story).** As written, it is too much detail for a SHORT talk closer. It's an excellent piece of writing — precise, well-sourced, and it does double duty as a demonstration of the thesis — but it requires ~90 seconds to set up (the filename substring match, the scheduler's re-inference, the quoted diagnosis, the quoted fix principle, plus the closing caveat that the same pattern still appears elsewhere in the codebase) before it pays off. In a short talk that is a large fraction of the remaining budget spent on one anecdote, and it risks the talk ending on "there's still a similar bug pattern elsewhere in the codebase" — a hedge, right before Q&A, which is not the note you want to hand to a hostile-to-hype supervisor as their last impression before they start asking questions.

**Proposed alternative closers**, in order of preference:
- **(a) Compress to the punchline only:** "Late in the project the scheduler once tried to infer meaning from a filename after the contract was frozen — and got it wrong. The fix wasn't a patch, it was a rule: nothing after the freeze may re-derive meaning that wasn't already in the contract. That's the whole thesis, learned the hard way." One breath, ~20 seconds, keeps the "thesis meeting its own implementation" payoff, drops the reconstruction of the bug mechanics and the still-present-elsewhere caveat (which moves to backup/Q&A).
- **(b) Close on the status line instead**, if beat 5 was already moved earlier in the talk per §5 above: end on "release candidate, demonstrated once end-to-end, not yet reproducible unattended — and we're telling you that up front because that's the same discipline the system itself is built around." This ties the honest-status theme directly to the closing and is arguably a stronger, more talk-appropriate note for a short slot than a bug anecdote.
- Either way, **the "still appears elsewhere in the codebase" caveat should move to backup/Q&A** ("has this pattern been fully eliminated?") rather than be the last sentence spoken.

---

## 8. Redundancy

Said three times, only needs saying once (as prose, not reference material — some repetition across a brief/briefing/full-report trio is expected and fine; flagging only where it's the *same* framing repeated with no added value):

- **"Language models interpret semantics, deterministic code validates/freezes/schedules"** — appears near-verbatim as the lead thesis in V1 §1, V2 §1 ("The stated design thesis"), and V3's executive summary. This is fine and probably should stay in all three (it's the anchor sentence) — but the *elaboration* around it (the "hard line" framing, "negotiation vs contract execution") is also repeated nearly word-for-word across all three. Not a defect, just worth knowing the deck can lean on any one of the three sources for this line without needing to check for drift — they agree.
- **The capsule invariant quotes** ("Missing protocol parameters remain explicitly unresolved..." and "Scientific reliability is not self-certified at discovery...") appear in V1 §4 and are echoed in substance (not verbatim) in V2's M12 and V3's capsule/discovery sections. Fine — these are good quotes and bear repeating in the talk and in backup.
- **The 606/34/8 regression figure and "not yet routinely reproducible unattended"** appear near-identically in all three. Correctly so — this is the honest-status anchor and should be consistent everywhere, which it is.

## 9. Gaps — present in none of the three

- **No document states, in one place, exactly how many total end-to-end attempts have been made and what happened to the ones that didn't succeed.** V3's ledger entry #3 implies at least one prior E2E run *failed*, but no document gives a clean tally (attempted / failed / succeeded). This is precisely the number a hostile supervisor will ask for, and right now the presenters have no clean answer to give — V1 currently answers with a number (three) that appears to be wrong.
- **AUDIENCE.md's own prescribed analogies aren't fully used where prescribed.** "The freeze is a lockfile" and "logical→physical operators are like an interface vs implementation" are both listed in AUDIENCE.md as the intended technique for V1, but V1's actual text doesn't use either phrase (it uses "compiler" for the freeze, and no explicit interface/implementation language for operators). Not wrong, but a gap against the brief that set up these documents.
- **No document gives the presenters a one-line answer to "why should I believe 80 capsules and 606 tests over a system that might just be well-decorated conventional code?"** — V3 §35b comes closest ("the individual parts are mostly known techniques... what is less usual is the combination"), but that framing doesn't appear in V1 or V2's own voice, and it's exactly the kind of pre-empting sentence a short talk needs in the room, not just in backup reading.

## 10. Handoff-readiness verdict (VARIANT-2)

**Mostly stands alone, with two soft dependencies worth checking:**

- V2 opens by declaring itself self-contained ("you do not need access to the codebase") and largely delivers on that — mechanisms are described in neutral prose, jargon is defined inline, and it doesn't assume the reader has seen V1 or V3.
- **Soft dependency 1:** §5's line "A companion briefing document describes thirteen mechanisms..." (in V3, not V2 itself — V2 doesn't reference V1/V3 by name, which is correct). No issue found in V2's own text referencing the other documents.
- **Soft dependency 2:** the AutoSci discussion (§5) assumes the external assistant will accept "a real upstream research-agent project" and "not at full parity" at face value without ever explaining what AutoSci *is* beyond one sentence — an external reader with web access may reasonably go looking for "AutoSci" as a public project and not find a matching public entity, since the term is internal to this codebase's comparison tooling. Worth one added clause clarifying that AutoSci is treated here as an internally-tracked comparison target, not necessarily a publicly indexed project, so the assistant doesn't waste a search cycle looking for it externally.
- **Minor:** the 2.8-candidates figure (item 3 in the contradiction table) is presented in V2 as if independently derived ("Provenance: everything in §§1–3 and §5 was verified by direct code inspection") — §4 (where this number lives) falls outside that verified range, so the 2.8 vs V3's 2.75 discrepancy is technically within V2's own disclosed "briefer's own guesses" carve-out for §4 analogues, but the *number* itself reads as a fact, not a guess, and should match V3 exactly since both claim code-level grounding.

**Overall: fit to send as-is, with the AutoSci clarification and the 2.75/2.8 fix as the only real pre-send corrections.**
