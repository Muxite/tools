# 29 — "Silent rot": what 2604.00392 actually says

Written 2026-09-10 by the capability-capsule panel (pts/9).
**[verified]** against `/home/muk/work/papers/2604.00392.txt`; line numbers are
that file's.

> ⚠ **This note exists because the panel had never read its own most important
> citation.** Notes `17-` §2.4, `18-`, `21-` and the report outline all lean on
> 2604.00392, and every one of them was working from a second-hand summary.
> Reading the source found the summary **materially wrong**. Corrections in §5.

*Beyond Task Completion: A Verification-vs.-Conformance Gap in Tool-Evolving
Agents* — Alibek Kaliyev (UT Austin) and Artem Maryanskyy (Uber),
arXiv 2604.00392v2 [cs.SE], 4 Jul 2026.

---

⚠ **Line references re-derived 2026-09-11.** Every paper line number in this
note was uniformly **+4** against `papers/2604.00392.txt` and has been
corrected. All quoted text was verbatim-correct; only the pointers were off.
Verified on five independent refs.

## 1. The real finding, and it is much stronger than we were claiming

The paper's central concept is **silent rot**, its own term (line 293):

> *"We say a preserved tool exhibits **silent rot** if it executes cleanly but
> records C=0.00 on the held-out suite. The rot is silent because no in-session
> signal flags it: **the verifier scores task outputs, not tools**, so a
> defective tool is rejected only indirectly, when a task that leaned on it
> fails."*

**Table 5** — every *distinct preserved* tool (222; CREATOR-style's 105 creation
events collapse to 84 distinct tools) replayed against a held-out conformance
suite for the capability it was built for:

| System | Tools | Mean C | Mean R | Silent rot % |
|---|---|---|---|---|
| One-Shot | 119 | 0.000 | 0.518 | **100.0%** |
| ToolMaker-style | 19 | 0.000 | 0.526 | **100.0%** |
| CREATOR-style | 84 | 0.049 | 0.536 | 91.7% |
| **Total** | **222** | **0.018** | 0.525 | **96.8%** |

**215 of 222 preserved tools score zero correctness on held-out inputs for their
own capability.** Of CREATOR-style's 84, seven (8.3%) score non-zero and exactly
one reaches C=1.00.

And they execute fine. Mean held-out robustness R is 0.52-0.54 across all three
systems (lines 302-303): *"they simply return wrong answers on inputs the agent
never saw."* Meanwhile the sessions carrying these libraries still pass about a
third of their verified tasks (TC 0.31-0.34, line 288).

## 2. The calibration argument — why 96.8% is not an artefact

The obvious objection is that the conformance suites are too hard. The paper
pre-empts it (line 309: *"the 96.8% is a discriminator, not a floor"*):

- **Hand-written reference implementations released with the benchmark score
  C=1.00 on all 16 capability suites.** The suites are passable.
- Suites are modest: five to six hidden unit inputs plus five to six adversarial
  probes per capability; per-tool suite sizes 10-22, **median 11** (lines
  285-288).
- A sharp anchored pair from the *same* protocol, model snapshot and harness
  (lines 294-308): `decode_arise_binary_records` records C=0.00 across 12 unseen
  inputs while nothing in-session flags it; `validate_records_against_schema`
  hits **C=1.00** on 11 held-out inputs, reproduced identically across seeds 0,
  1 and 2.

That last pair is the most useful single citation in the paper: **the framework
discriminates working synthesis from silent rot at the per-tool level.** The
failure is a property of unvalidated synthesis, not of the measurement.

## 3. What the paper actually is

Not a position paper — a **benchmark and audit-schema paper**.

**EvolveTool-Bench**: 99 tasks across three domains, with sessions structured
into six roles — **seed, gap, variant, composition, regression, adversarial**.

⚠ Those six roles are exactly the "six probe roles" note `19-` builds its
conformance-suite design on. **Note `19-` used them correctly**; this note simply
confirms the provenance.

Artifact-level measurements it defines and logs, alongside verified TC: tool
creation, raw reuse, **correct reuse, incorrect reuse**, utilisation,
composition, regression.

Its recommendation, and the sentence to quote in the report (lines 44-46):

> *"an audit schema of this shape – **verifier coverage, reuse decomposition,
> held-out conformance** – is the minimum a deployed tool-evolving agent should
> emit between releases."*

**"Between releases" is the phrase to notice.** The paper frames this as
continuous deployment hygiene for a long-running system, which is precisely the
deployment mode note `26-` targets.

## 3b. ⚠ The scope limit that matters most for a long-horizon argument

Added 2026-09-11, while planning the 20-minute prior-art talk. This was not
recorded anywhere in the notes or in `DATA.md`, and it is the first thing a
reader of §4 would ask.

§4, verbatim (`papers/2604.00392.txt:176`):

> "harness state resets between sessions so **library accumulation is
> per-session, not cross-session**."

**So this paper measures capabilities that are broken at birth. It does not
measure a library decaying over a long run.** Those are two different failure
modes and only the first one is measured here.

Do not let any deliverable slide from "silent rot" to "drift over a week-long
autonomous run". The long-horizon decay claim has separate evidence — Alita-G's
Table 4, where effective coverage falls 1.00 → 0.51 as the Box grows 26 → 128
(`21-` §4, `27-` §3). Keep the two citations attached to the two claims:

| Failure mode | Evidence | Source |
|---|---|---|
| Capabilities are **born broken** | 96.8% of 222 tools at C=0.00 | 2604.00392 Table 5 |
| Libraries **decay as they grow** | effective coverage 1.00 → 0.51 | Alita-G Table 4 |

Neither is caught by outcome-gating, which is the actual joint thesis and is
stronger stated as two rows than blurred into one.

## 4. Their own honesty, worth copying

The pre-specified contrast — adapted decision-split synthesis vs. unvalidated
one-shot — comes out at **−7.1 pp, 95% CI [−13.9, −0.1]**, and they report it as
**not significant after the pre-registered BH correction**, calling it *"a
hypothesis-generating signal, not a confirmed effect."*

They also exclude the API-orchestration domain from the main TC denominator
until its verifiers are complete, and report unverified tasks separately rather
than crediting them.

This is the calibration posture the report should mirror, and it pairs well with
the six-state result vocabulary the project already has (`18-` §4.3).

## 5. ⚠ Corrections to this panel's notes

**5.1 — The "four named failure modes" in `17-` §2.4 are not in the paper.**

Note `17-` §2.4 attributes four failure modes to 2604.00392: *specification
drift, hidden dependencies, incomplete validation, interface violations*, plus
mitigations including *"multi-stage verification pipelines"*. Full-text
case-insensitive counts:

| Phrase | Occurrences |
|---|---|
| `specification drift` | **0** |
| `hidden dependenc` | **0** |
| `incomplete validation` | **0** |
| `interface violation` | **0** |
| `multi-stage verification` | **0** |

**None of them appear.** They came from a second-hand summary and must be
removed everywhere they occur. The paper's vocabulary is *silent rot*,
*held-out conformance*, *reuse decomposition*, *verifier coverage*, and *audit
schema*.

**This is the single most dangerous error found in the notes so far** — not
because the conclusion changes (it does not; it gets stronger) but because
fabricated failure-mode names in the report's most load-bearing citation are
exactly what a supervisor who opens the PDF would catch first.

**5.2 — Note `21-` §2's mapping table is invalid.**

Note `21-` built its "cleanest contrast available" on mapping Alita-G's four
abstraction transforms onto "three of 2604.00392's four failure modes." Those
failure modes do not exist, so the mapping goes.

**The replacement is better**, and needs no invented taxonomy:

> 2604.00392's in-session verifier *"scores task outputs, not tools"* — which is
> **exactly Alita-G's Eq. 5 predicate**, `π_master(x_i) = y_i`. So this paper
> does not merely happen to apply to Alita-G. It measures the failure rate of
> precisely Alita-G's curation rule, on preserved tools, at **96.8%**.

Alita-G's abstraction step produces exactly the artifact class silent rot
describes: a tool that has been generalised by an LLM to look reusable, executes
cleanly, and is never replayed against held-out inputs for its own capability.
The two papers fit together without any interpretive work at all.

**5.3 — What survives unchanged.** The thesis, and it is now better supported:

- Task completion does not certify the library. *(the paper's opening line)*
- Curating on task outcome admits broken artifacts at scale. *(96.8%)*
- The fix is held-out, artifact-level conformance checking. *(their audit
  schema; our admission gate)*

## 6. What this licenses the report to say

Replace every vague "tools violate their own specifications" with the number:

> Across 222 tools synthesised by three tool-creating protocols, **96.8% scored
> zero correctness when replayed against a held-out suite for the capability
> they were built for** — while executing cleanly, raising no in-session flag,
> and sitting in sessions that still passed a third of their verified tasks.
> Hand-written reference implementations score 1.00 on the same suites. The
> in-session verifier scores task outputs, not tools.

**That is the entire argument for an admission contract, in one paragraph, with
a citation.** It is far more forceful than anything the notes contained before,
and it converts the capsule proposal from engineering preference into a response
to a measured, named, reproducible failure.

## 7. Follow-ups

- ⚠ `2604.00392` cites **EvoSkill** [Alzubi et al. 2026] and **CoEvoSkills**
  [Zhang et al. 2026] as *distinct* systems. Note `17-` §6 corrected
  "EvoSkills" → "CoEvoSkills" for 2604.01687, which remains right — but EvoSkill
  is a real, separate system and the report should not conflate them.
- The paper's protocol names — One-Shot, ToolMaker-style, CREATOR-style — are
  reimplementations, not the original systems. Do not report the numbers as
  "CREATOR scores 91.7% silent rot".
- Its pilot is **Claude Haiku 4.5 at temperature 1.0**, verified subset. State
  the scale honestly; the authors do.
