---
id: nuwa-presentation
status: completed-documentation
source: ../../../Sources/Prompts/2026-10-23-nuwa-person-to-skill-and-orange.txt; ../../../Sources/Prompts/2026-10-23-nuwa-ai4r-methodology-and-luna.txt; references/source-review.md
last_reviewed: 2026-10-23
next_action: Trial one person-plus-trait authoring request, then qualify any candidate through AI4R
---
# Nuwa rev3: what AI4Research can learn

Open [Nuwa Talk rev3.pptx](output/Nuwa%20Talk%20rev3.pptx). **Nine main slides and two hidden backups**, planned **7:20**. The factory slide now presents three proposed entry interfaces: observed capability gap, paper/repo/data, and person name plus trait. Speaker notes include the script and pinned sources. Timing remains an estimate, not an aloud rehearsal.

Rev3 uses burnt orange, terracotta and warm cream. The story starts with Nuwa turning a person's documented thinking into a skill. AI4Research is the purpose of the assessment: where the idea and methodology could help, what to imitate, what to improve, and how to test it. The deck does not reuse Paper2Agent's workflow or present persona roleplay as the research objective. Earlier rev2 files remain for history.

## Main story

| Slide | Point | Planned time |
|---|---|---|
| 1 | A person becomes an AI skill, with potential AI4R value | 0:25 |
| 2 | Explicit answer: yes narrowly, as a human-to-skill input to the CC Factory | 0:55 |
| 3 | Explore: six research streams, source discipline and validation criteria | 1:05 |
| 4 | Extract: models, rules, evidence criteria and utility to AI4R | 1:00 |
| 5 | A Karpathy-derived benchmark-review example illustrates the mechanism | 0:45 |
| 6 | Weak fidelity assurance: resemblance-heavy scoring, tiny tests and source-free lint passes | 0:50 |
| 7 | Three proposed interfaces feed one shared CC-factory lifecycle | 1:00 |
| 8 | A bounded trial tests human-to-skill authoring utility, then task qualification | 0:50 |
| 9 | Borrow the human-to-skill interface; AI4R owns capability evidence and qualification | 0:30 |
| 10 | Hidden backup: plain, generic-checklist and extracted-method arms | |
| 11 | Hidden backup: governed CC binding and checks | |

The proposed interfaces separate route-specific evidence and authoring from the shared candidate package, independent qualification and ordinary admission. It is an M2 proposal, not a built pipeline or an admitted capability. A flat workflow comes before any composite. Source preparation keeps its own authority boundary.

## Adversarial review and revision

At the user's request, **gpt-6-luna** adversarially reviewed the draft, pinned source snapshots and AI4R context. The [raw report](../../../Resources/review-batches/2026-10-23-nuwa-orange/luna-adversarial-review.txt) is retained. Its findings led to visible qualifications on value and the example, an explicit host-agent label, a stronger factory diagram, a generic-checklist control, clearer output labels and shorter headings.

The comparison now gives every arm the same frozen expert-source excerpts and task evidence. It compares a plain reviewer, a length-matched generic checklist, and a neutral Nuwa-derived procedure under matched model/tools/runtime budgets. Unseen tasks and scoring freeze first. Authoring cost is separate. This tests incremental task usefulness beyond generic prompting; it does not isolate every extraction phase or establish persona fidelity.

## Files

- [Editable deck](output/Nuwa%20Talk%20rev3.pptx), [speaker script](speaker-script.md), [contact sheet](review-orange/contact-sheet.jpg).
- [Builder](build_pptx.py), [finalizer](finalize.mjs), [PowerPoint render script](render.ps1).
- [Source review](references/source-review.md), [original source receipts](references/source-receipts.json).
- [Final artifact validation](.build-orange/Nuwa%20Talk%20rev3%20human-interface-reviewed.validation.json).
- Original [checker probe](review/checker-probe.json): a structural finding from 2026-10-22, not a persona-quality experiment.

The GitHub API confirmed on 2026-10-23 that main still points to `7812110bf7e5a2b01b6aa5a738568044121bbfa2`. The primary agent reread the research/extraction/generation/validation instructions, template, rubric and checker. Selected snapshots retain the MIT license. No Nuwa installation, skill generation, AI4R integration, admission or comparative accuracy result is claimed.

All final slides are rendered through PowerPoint and inspected individually. The finalizer checks package integrity, slide geometry, preserved Segoe UI text, editable backup tables and first-party import. Sources and notes remain embedded. The original Nuwa checkpoint also recorded Paper2Agent rev9 link errors. That observation is historical: [[Sources/Prompts/2026-10-23-paper2agent-final-rev8.txt]] confirms rev9 deliberately removed and rev8 final. Current library checks are in [[Resources/Validation Report]]; this correction does not rerun or broaden the presentation checks.

To rebuild, run the builder with the bundled Python runtime, finalize to a fresh output revision, then render and inspect that exact file. The finalizer preserves existing outputs. Historical builder/notes snapshots are under `history/rev2/`.

## Value-first order (retained)

Moved the former slide 5 to slide 2 on 2026-10-23. The former slides 2–4 are now slides 3–5. All other slides retain their order. That reorder preserved content, style, notes and timing at the time. The subsequent method-detail revision changes only the two explanation slides, factory interface diagram and their notes. The prior deck is retained under `history/rev3-before-value-first/`.

## Method-detail revision

The latest request adds concrete method detail without adding slides. Slide 3 distinguishes general mental models, case-supported decision rules, limits/tensions and model-derived research directions. Slide 4 explains the six research streams, saved source/confidence records, first-hand preference and prescribed validation checks. Qualitative selection filters and checklist targets do not prove semantic quality. Examples paraphrase the repository's Karpathy skill.

Slide 7 shows three proposed entry interfaces to a common factory: an observed gap becomes a requirement brief, paper/repo/data supplies an implementation to reproduce/adapt, and a person plus target trait becomes a scoped research/extraction request. The shared stage authors a candidate with a contract, body and evidence before independent qualification and ordinary admission. Source acquisition remains separately authorized. None of these diagrams is evidence of deployed factory interfaces.

The method-detail tables and three-interface diagram received a bounded Luna spot-check against the pinned sources, with no concrete blockers. The final package passed structural, layout, font, editable-table and import checks. Unchanged slides and notes match their retained prior XML exactly; changed slides 3, 4 and 7 were rendered and visually inspected.

## Pipeline order and direct value answer

Slide 2 now explicitly asks whether Nuwa-skill's methodology is valuable to AI4Research and answers yes as a design pattern for evidence-backed capability authoring. Measured task gain remains an open experiment. Slides 3 and 4 now follow Nuwa's pipeline: explore/research first, then extract mental models and decision rules. Subsequent example, pitfalls and factory slides retain their order.

## Human-to-skill scope correction (current)

This supersedes earlier broad endorsements in the historical revision notes. Nuwa's relevant contribution is the human-to-skill research/extraction input. AI4R already has its own evidence-backed capability approach. Slide 2 answers yes narrowly and sends a draft to factory qualification instead of directly to an AI4R agent. The validation critique now specifies scoring weights, question count and the source-free placeholder probe. Separate LLM judges are a useful safeguard but do not establish independent task validity. Authoring utility and downstream task gain are separate outcomes. Current edits preserve the native package through `revise_human_interface.py`; the legacy builder content is synchronized but was not used for this edit.
