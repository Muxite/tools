# 56: Capability Capsule, deck v5: research told as what happened, compressed; pre-workshop rundown (2026-09-22, late night)

Builds on note 55. Branch `schema-v2.1-overnight` in `capsule-openjiuwen`, commit `74aa5c0`; not pushed.

## What changed

- **Muk's directives** (obby Directives): "link to research" means what each study did and what it showed, not
  numbers and arXiv ids; spend slides on that rather than tables that add attack surface; compress, make each slide
  mean more; individual code items are illustrative and open to change, the deck only has to show it can work.
- **Deck v5, 32 slides (was 37).** The two advantage tables became six two-study slides (what they did, what
  happened, so CC, proved wrong if). The closest design, Don't Offer What Can't Be Done, is told the same way in (e).
  Cut: the appendix tables, the research-behind table, real multiplicity, the cold path, "Most designs observe".
  Folded into slides that stay: the records table, the carrier table, "start extra small", the second Remove slide.
- **Report:** §2f gains "What each study did, and what it showed" (fourteen studies); Appendix A lists the openJiuwen
  and AI4Research parts CC uses.
- **Fixes, each verified in the paper:** the 0.49 to 0.28 endpoints of More Skills are read off an image, so every
  document cites the printed drop, 0.21 [0.15, 0.27]; Cognitive Admission Control's 120 to 90 is the variant that
  cannot fetch missing evidence, not "denying on unknown"; judge thresholds tagged design; the chooser, not the
  planner, binds a generalist; the refuse list includes a failed node gate. A Sonnet check of all fourteen study
  claims found none wrong.
- **Recounted:** 42 of the 85 manifests name another `cap.*` in `composition.requires_after` (46 fill it, 4 name only a
  guard). The 85 span two folders; `harness/capability-capsules` alone has 39.
- **Open point, offered to Muk as a small v2.9:** a claim is not marked stale when a later step writes to a resource it
  read. Recording what each claim read, at which version, would close it.

## SkillFuzz wording (after Muk's question)

- Slide 18 no longer says every screener input was a declaration the skills lacked (the paper never compared
  declared and extracted contracts); it says SkillFuzz had to infer contracts from prose and CC supplies them.
- Its disproof line now fits both studies: a screened set still drifts as often as an unscreened one, or a drifted
  dependency goes unseen.
- The 4.7% single-skill drift rate was read off Fig. 6 and is dropped; the printed "rare for singleton activations"
  and "fourteen-fold" (p9) stay.

## Citation audit and jiuwenswarm (late night)

- All notes are point form now, and nothing the argument needs lives only in the notes.
- A Sonnet audit of the report's 100 paper citations found four defects, each re-verified: SkillFuzz (our inference
  stated as its finding), Darwin Gödel Machine (the archive keeps every compiling variant, it does not prune on
  score), Cognitive Admission Control (Prop. 1 folded into the Table 2 trials, page p6 not p4-5) and The Blind
  Curator (true retirements are 0.3 at q=0.45, 0.0 at q=0.2 and q=0.7, against a clean 1.3). No figure-read values
  remained.
- Also fixed earlier: CoEvoSkills' ablation removes the verifier's diagnostic feedback, not the separation;
  Don't Offer's 7.8% is a risk-enriched cohort; Contract2Tool learned 0.980 against correct 0.990.
- **jiuwenswarm Auto Permission** added to the openJiuwen slide and report Appendix A.5: a per-call ToolCapability
  (category, operation family, resource class, static side effects, risk tier), an expected-effects comparison, a
  reviewer route by risk and an append-only hashed audit. Its facts are derived from tool names and permissions
  ship disabled, so it is the nearest existing thing to declared effects, one level below CC.

## Deliverables (tundle copies)

`Capability Capsule Merged Deck - Muk.pptx`, `Capability Capsule Merged Report - Muk.docx`,
`Capability Capsule Schema v2.8 - Muk.md`, `Capability Capsule Workshop Rundown - Muk.html` (also a private artifact:
https://claude.ai/artifact/7k4KSvDnX8Qmuzp2amDYJF).
