---
id: nuwa-speaker-script
status: current
source: output/Nuwa Talk rev3.pptx
last_reviewed: 2026-10-23
next_action: Rehearse timing aloud
---
# Nuwa rev3 speaker script

## Slide 1

TIME 0:25. Nuwa researches a named person and drafts an instruction skill containing inferred models, decision heuristics, voice and limits. It approximates a public record; it does not recover private cognition or train weights. Our question is whether the human-to-skill methodology offers a useful additional input to AI4Research's Capability Capsule Factory. We should assess that narrow contribution critically.
SOURCES
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/SKILL.md
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/references/skill-template.md

## Slide 2

TIME 0:55. Yes, narrowly: Nuwa offers a human-to-skill authoring interface for the CC Factory. A name and target trait become a scoped research request, followed by a candidate instruction skill. An extracted procedure is only a candidate input; AI4R must attach evidence and qualify task behavior. AI4R already has its own approach to evidence-backed capabilities. Nuwa does not supply a better assurance system. We borrow its person-and-trait research workflow; our factory retains responsibility for operationalizing a candidate, testing task behavior and admitting a capsule. Nuwa's fidelity scores and structural checks cannot establish research capability. The value claim is an interface design judgment, with actual authoring and task benefits still unmeasured.
SOURCES
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/SKILL.md
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/references/extraction-framework.md
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/references/skill-template.md
LOCAL CONTEXT
Designs/CC Reference.md; Designs/skills-to-cc-mapping.md. Design-value assessment, not an implemented integration or measured task gain.

## Slide 3

TIME 1:05. Nuwa scopes a person and requested trait, then asks a host agent to research six streams: writings, conversations, expression, outside views, decisions and timeline. It saves sources, confidence and distinctions between direct statements, reports and inference. Primary-source preference and contradictions are useful research practices for this human-to-skill input. They are prescriptions, not proof that extraction is correct. A user-specified trait can bias source selection: first ask whether the person's documented record supports that trait, and retain contrary examples. Public repetition may reflect branding or repeated quotations. Firsthand material may still be inaccurate or selective. These source heuristics should inform candidate authoring, while AI4R's evidence process remains responsible for checking claims and capability behavior.
SOURCES
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/SKILL.md
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/references/extraction-framework.md
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/references/fidelity-scorecard.md

## Slide 4

TIME 1:00. The product of exploration is a set of inferred models and rules. Nuwa asks for three to seven models that recur in at least two domains, generate new judgments and distinguish the person's perspective. It asks for five to ten concrete decision heuristics with cases, plus limits and tensions. These are subjective extraction filters, not validation of truth or utility. Distinctiveness can reward idiosyncrasy even when a generic method works better. The Karpathy examples here paraphrase the repository's skill; we have not independently verified these attributions. For AI4R's human-to-skill interface, treat every extracted model as a candidate with traceable support, counterevidence and an explicit scope. A rule only becomes a useful capability after our own task checks.
SOURCES
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/SKILL.md
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/references/extraction-framework.md
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/examples/andrej-karpathy-perspective/SKILL.md
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/references/skill-template.md

## Slide 5

TIME 0:45. A request such as Karpathy plus reliability review can guide research and yield candidate questions about task coverage, tool failures and reproducibility. This example illustrates how a requested human trait becomes explicit draft rules. It does not show that Karpathy would answer this way or that the generated skill improves an AI4R review. These are familiar review questions that a generic checklist may produce equally well. The name can help a user express the requested perspective, but it provides no authority for an answer. The factory must test the resulting rules against the same task evidence and a competent baseline.
SOURCES
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/examples/andrej-karpathy-perspective/SKILL.md

## Slide 6

TIME 0:50. Nuwa's assurance is weak for capability claims. First, reconstructing a person from public material while targeting a chosen trait invites selection bias and attribution errors. Second, half the fidelity score rewards stance and style: 30 and 20 points. The remaining categories address boundary honesty, sources and structure, but none directly measures AI4R task improvement. Third, the prescribed behavioral test uses three known-position questions, one unfamiliar question and one style sample. Independent answer and judging agents are a useful separation, and the rubric recommends extra judges for important conclusions, but separate LLM agents can share model biases; this is not independent empirical task evidence. Fourth, the saved placeholder probe passed all six structural checks without sources. Missing or untyped sources return success, while keyword matches stand in for semantic checks. This demonstrates a checker defect, not that every Nuwa skill is poor. Its scores cannot justify admitting a research capability; AI4R retains its own evidence, behavioral tests and admission.
SOURCES
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/references/skill-template.md
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/references/fidelity-scorecard.md
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/scripts/quality_check.py
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/examples/elon-musk-perspective/FIDELITY.md

## Slide 7

TIME 1:00. We propose three input interfaces to the Capsule Factory. An observed runtime gap produces a diagnosed requirement brief. A paper, repository and data provide a method to reproduce and adapt. A person's name plus target trait initiates human-focused source research and skill drafting, taking inspiration from Nuwa. This third route is Nuwa's relevant contribution. All routes produce candidates; AI4R owns the contract, body, evidence package, independent qualification and existing admission gate. A name cannot establish competence, and Nuwa's fidelity grade cannot replace our checks. Source preparation is separately authorized and pinned before offline build work. This is a proposed interface, not a claim of deployed integration or adoption of Nuwa's assurance system.
SOURCES
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/SKILL.md
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/references/extraction-framework.md
LOCAL CONTEXT
User direction, 2026-10-23: three factory inputs. Designs/Capability Capsule Factory Feature.md; Designs/Per Lab Capability Factory Design.md. Proposed M2 extension, not implemented interfaces.

## Slide 8

TIME 0:50. Trial the interface as an authoring tool first: choose one person, a defensible target trait and a strong corpus. Draft a candidate skill using the research and extraction workflow. Check attribution and contrary evidence; record unsupported rules, corrections, human effort and authoring cost. If the candidate is worth continuing, take it through AI4R qualification. The task comparison uses a plain reviewer, a generic checklist and the human-derived rules, all with the same frozen sources, task evidence, model, tools and runtime budget. Blind scoring on unseen tasks tests incremental utility. A useful interface can reduce the effort of specifying a capability without proving the human-inspired rules outperform a generic method. Report those outcomes separately.
SOURCES
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/SKILL.md
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/references/fidelity-scorecard.md
LOCAL CONTEXT
Designs/skills-to-cc-mapping.md; separate proposal, not a revision to the maintained accuracy study.

## Slide 9

TIME 0:30. Our recommendation is selective: borrow Nuwa's person-and-trait research workflow as a possible third input to the Capability Capsule Factory. We already have our own approach to evidence-backed capability production. Nuwa's reconstruction, tiny fidelity test and permissive structural checker provide insufficient assurance for that role. A familiar persona can be an accessible way to request a skill; the resulting artifact remains a candidate. Judge the interface by the useful candidates it produces and the effort it saves, then require ordinary AI4R task qualification and admission.
SOURCES
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/SKILL.md
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/references/skill-template.md
LOCAL CONTEXT
Designs/skills-to-cc-mapping.md; Designs/Capability Capsule Factory Feature.md

## Slide 10

BACKUP. All arms receive the same frozen expert-source excerpts and task evidence. The plain reviewer gets no added procedure. The generic arm gets a length-matched general review checklist. The extracted-method arm gets neutral rules and limits produced through the Nuwa-inspired process. Hold the model, tools, permissions and runtime budgets fixed, freeze unseen tasks and scoring before generation, and blind human assessment. Judge supported useful objections, missed failure modes, unsupported claims, uncertainty, latency and cost. Record corpus preparation and authoring effort separately from runtime cost. This identifies the increment beyond a generic checklist, not the causal effect of each Nuwa phase. A later voice ablation can test whether persona framing helps or hurts. No experimental result is claimed.
SOURCES
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/references/fidelity-scorecard.md
LOCAL CONTEXT
Designs/skills-to-cc-mapping.md; Luna adversarial review, 2026-10-23.

## Slide 11

BACKUP. This is downstream of authoring. A human-derived instruction skill is a candidate body, not a capsule contract or permission grant. Pin source evidence, cutoff and rule support; define one bounded task with typed inputs and inspectable outputs. AI4R supplies tool/effect/budget constraints, task-level tests, versioning and admission. The semantic verifier remains declaration-and-output-only; source- and input-dependent checks belong in the protected host path. A Nuwa fidelity report can describe the approximation but cannot qualify this capsule. This is a proposed integration, not implemented deployment.
SOURCES
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/SKILL.md
https://github.com/alchaincyf/nuwa-skill/blob/7812110bf7e5a2b01b6aa5a738568044121bbfa2/references/skill-template.md
LOCAL CONTEXT
Designs/CC Reference.md; Designs/skills-to-cc-mapping.md
