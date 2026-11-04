# 46 — The supervisor's answers on Capability Capsule (chat, 2026-09-18)

**Source:** two screenshots in this folder, `../20260918_150108 (1).jpg` and `../20260918_150123 (1).jpg`,
of the **AI4Research-Waterloo** group chat. **Read in source** — transcribed off the images, English
original, no translation involved. Typos are the senders' own and are kept; `[sic]` marks the ones a reader
would otherwise take for a transcription error.

**Read this before [45-capability-capsule-supervisor-slides.md](45-capability-capsule-supervisor-slides.md).**
Answer 1 below demotes those two slides from specification to history, and answer 5 contradicts the framing
our design document is built on. Both are recorded in §3.

| | |
|---|---|
| Chat | AI4Research-Waterloo |
| Muk Chunpongtong | 2026-09-18 14:30 |
| Stellven Yuan (supervisor) | 2026-09-18 14:50 |
| Employee IDs | displayed in both screenshots; not copied here |
| Reaction | Muk 👍 on the supervisor's reply |

---

## 1. Muk → the chat, 2026-09-18 14:30

### 1.1 The four questions

> 1. What is not a capsule/should not be a capsule? This kinda asks the scale of what a capsule is. Capsules
>    probably shoud [sic] not be the verifying library or gate for other capsules.
> 2. Can capability capsule scope be reduced to the contract, identities, lineage, storage, and admission?
>    The improving system I showed is possibly closer to RSI, and the gate might be called verification.
> 3. Can we contact people who are working on OpenJiuwen? It seems jiuwenswarm has its own capability-creation
>    system, as well as Skill Symphony, which kind of acts like Capability Capsule but could have very
>    different policies and appears a lot less strict and validated.
> 4. How much should the new system be based on OpenJiuwen/JiuwenSwarm? Is there a requirement?

### 1.2 The understanding statement

Sent in the same exchange. **The screenshot cuts off mid-sentence**, and the "Return to the latest message"
pill covers part of the last visible line.

> My current understanding of capability capsule is that capsule can be a unit of the system at many sizes
> and acts like a wrapper for skills/tools/mcp/A2x, each capsule can be tested and verified individually.
> Additionally, it shares spatiotemporal composability from being based on Cordis paper, so items in
> capability capsule can be dynamically added or removed without system restart + turn on or off if there
> dependencies [sic] are unmet.
>
> AI4Research is exploratory, open-source, and built on OpenJiuwen. So perhaps we can do more
> ambitious/less researched areas tha… **[cut off by the screenshot; at least one further line is partly
> visible and not legible]**

> **The tail of this message is missing.** It is the only part of either screenshot that is not fully
> recovered. If the rest matters — and it is the sentence proposing what we aim at — re-screenshot it.

---

## 2. Stellven Yuan → Muk, 2026-09-18 14:50

Transcribed verbatim.

> Quicks [sic] answers to your questions on Capability Capsule (hereinafter referred to as CC):
>
> 1. Hope the two pictures can aswer [sic] your question. But, those two picture only shows the thoughts as
>    of before, and don't restrict your thoughts for your new design.
> 2. CC is schema layer, it could be related to most models, including RSI, but the function of CC and RSI
>    are totally different.
> 3. Not right now, no one in openJiuwen will spend their time to talk with you before you have a clear
>    understanding.
> 4. The new system will be developed on top of openJiuwen code base, and the architecture should be aligned
>    with openJiuwen.
> 5. You brought out some good thoughts, but AI4Research is not going to be a CC

---

## 3. What this settles

### 3.1 The two slides are history, not specification

> "those two picture only shows the thoughts as of before, and don't restrict your thoughts for your new design"

Note 45 was written on the assumption that the slides were the authoritative statement of the model and
outranked our own documents. **They are not.** They are prior thinking, offered as an answer to question 1,
and explicitly not binding.

Note 45 has been cut down accordingly: the transcription, the term index and the fabrication warning stay; the
consequences-for-our-design section is gone. The four things the slides have and our design does not — Assets as
a component, the SysML v2 chain, Ground Truth as a named component, the five capsule kinds — are now listed
there as **options worth a sentence each at the workshop**, not as gaps to close. The formal layer in particular
no longer needs to be adopted or argued down before Tuesday.

### 3.2 A capsule is a schema layer

> "CC is schema layer, it could be related to most models, including RSI, but the function of CC and RSI are
> totally different."

This is the answer to question 2, and it confirms the narrow scope — contract, identity, lineage, storage,
admission — in the supervisor's own words and in one phrase. **Schema layer** is now the term to use for what
the model is. It also settles the RSI overlap from the other direction: CC relates to RSI, but the two have
totally different functions, so the scope split that hands authoring and iteration to RSI is right.

Note what the answer does *not* do: it does not confirm or deny that the improving system shown on the slides
belongs to RSI. It says the functions differ. Do not read more into it than that.

### 3.3 AI4Research is not a capsule

> "You brought out some good thoughts, but AI4Research is not going to be a CC"

**This contradicts the framing our design document is built on.** `DESIGN.md` §1.1 currently reads:

> "The supervisor's framing is the test case to design against: **the whole of AI4Research should be
> expressible as one capsule**. If the abstraction cannot say that, it is the wrong abstraction."

That premise is withdrawn, and the consequence is not small. Scale invariance was the hardest requirement in
the design and that one test case was its whole justification; the strongest claim to novelty in the document
was that almost nothing in the literature treats a whole pipeline as a reusable versioned unit. **Both are
gone.**

What survives: capsules still wrap units at many sizes — nothing withdrew that — so one contract shape across
the range from a function to a team of agents is still load-bearing, and composite capsules are still cheap.
**Where the ceiling sits is now an open question**, somewhere at or above a sub-pipeline, and nobody has said
where. That is the sharpest thing to ask next.

Applied on branch `supervisor-answers-20260918`, cut rather than hedged — see §5.

### 3.4 openJiuwen is a requirement, and its people are not available yet

> "The new system will be developed on top of openJiuwen code base, and the architecture should be aligned
> with openJiuwen."

Question 4 asked whether there was a requirement. There is: **build on the openJiuwen code base, align the
architecture with openJiuwen.** This is stronger than the default we were proceeding on ("independent,
designed so contributing upstream stays possible") and it raises the value of the Symphony seam work.

> "Not right now, no one in openJiuwen will spend their time to talk with you before you have a clear
> understanding."

No contact with the openJiuwen team yet, and the condition is on us: a clear understanding first. The default
in the supervisor question list — ask the returning co-ops once they start — stands, but the openJiuwen
Toronto route is closed for now. Read it as a bar to clear, not a refusal.

---

## 4. Still open

Answered here: what is not a capsule (partly — via "schema layer" and "not AI4Research"), the scope
reduction, openJiuwen contact, openJiuwen dependency.

**Not answered, and still live:**

- Publication, repository and licence, handover at month four, model providers, spend.
- What the system should actually be able to do — the concrete target task.
- How strict admission should be, and what makes this a success or a stop.
- Whether the 80 existing capsule manifests carry over.
- **Where the ceiling sits.** AI4Research is not a capsule; a team of agents presumably is. Nothing says where
  the line falls, and the design now has a gap exactly where its top end used to be. The sharpest question to
  ask next.
- **What `避免能力现实` on the slide was meant to say** (note 45 §3). Lower stakes now that the slides are
  prior thinking rather than spec, but it is one line in a reply.
- **The tail of Muk's own 14:30 message** (§1.2), which is cut off in the screenshot.

---

## 5. What changed in the base documents

Applied 2026-09-18 on branch `supervisor-answers-20260918` in the capsule design workspace. The rule followed
throughout: **where a passage existed only to serve the withdrawn premise, it was cut, not hedged.**

| Document | Change |
|---|---|
| `DESIGN.md` header | dated revision note pointing here |
| `DESIGN.md` §1.1 | retitled *A schema layer over units of more than one size*. The whole-pipeline test case and the "if the abstraction cannot say that, it is the wrong abstraction" line are gone; the range now tops out at a team of agents, and "scale invariance" is restated as **one contract shape across the sizes the design does claim** |
| `DESIGN.md` §2.4 | rescoped from "a function to a pipeline" to "a function to a team"; pipeline-sized cost language generalised to large bodies. The four change-rows and the SkillPager and GraSP findings all survive |
| `DESIGN.md` §3.2 | **cut entirely.** *Recursion: the pipeline is itself a capsule* is replaced by *Composite capsules, and the ceiling on them*, which keeps the composition rule and records the withdrawal, including of the novelty claim that rested on it |
| `DESIGN.md` §6, claims 4 and 5 | claim 4 no longer says a whole system can be versioned and swapped; claim 5 now states the openJiuwen alignment requirement and that this design meets it without upstream change |
| `DESIGN.md` §7.1, §7.2 | M5 no longer promises the AI4Research pipeline as one capsule; the risk list drops "pipeline-sized" |
| `DESIGN.md` §5.2, §5.3 | the undefined label "the scale-invariance claim" replaced by "one contract shape across sizes" in four places |
| `notes/08-swot-by-scale.md` | **L6 cut entirely** — the level row, the matrix row and its SWOT. Recommendation 4 no longer declares L6 the aim; the L3 threat no longer argues against the supervisor's withdrawn framing. L0–L5 and the whole temporal axis are untouched, and the note's L3×T2 recommendation is *confirmed* by "CC is schema layer" |
| `notes/12-capsule-as-noun.md` | marked **confirmed**: "the function of CC and RSI are totally different" is this note's thesis in the supervisor's words. §3c's size example corrected |
| `asks/rsi-saurav.md` | the overlap section now opens with the supervisor's ruling instead of proposing a split; the composite-capsule paragraph keeps its point and states the ceiling |
| `asks/verification-ramika.md` | candidate body size range corrected |
| `asks/QUESTIONS-teammates.md` | the "an abstraction that can wrap anything" framing corrected to *almost* anything, with the schema-layer phrase and the ceiling stated; one stale pointer into the supervisor list removed |
| `asks/QUESTIONS-supervisor.md` | new *Answered on 2026-09-18* block; **S2, question 4 and question 6 removed** as answered; S1 narrowed to the ceiling question; the opening understanding paragraph corrected |
| `docs-read/BRIEF.md` | superseded-notice only. The brief is left as written because four reading reports were produced against it |
| notes 45 and 46 here | 45 collapsed to the record — transcription, term index, fabrication warning. The consequences live in this note |

**Not changed, on purpose:** `DESIGN.md` §2.1's invariants (none of them depended on the premise), the
literature findings and every ⧗ marker, and `notes/00`–`07`, `09`–`11`, `13` and the overnight sweeps, which
are records of what was read rather than claims about scope.
