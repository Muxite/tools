---
id: nuwa-source-review
status: reviewed-source-and-proposal
source: https://github.com/alchaincyf/nuwa-skill/tree/7812110bf7e5a2b01b6aa5a738568044121bbfa2; ../../../skills-to-cc-mapping.md; ../../../Capability Capsule Factory Feature.md
last_reviewed: 2026-10-23
next_action: Assess one human-to-skill authoring request; independently qualify any useful candidate
---
# Rev3 claim ledger and source review

Nuwa is an instruction skill that guides a host agent to research a person and generate a person-perspective skill. Its artifact is Markdown/YAML instructions plus source and research files, with helper scripts. It does not train model weights. The primary agent personally reread the relevant pinned source on 2026-10-23; GitHub's main-commit API still returned `7812110bf7e5a2b01b6aa5a738568044121bbfa2`.

| Slide | Claim | Evidence and status |
|---|---|---|
| 1 | Person evidence becomes mental models, heuristics, voice, values and limits | Core SKILL.md and skill-template.md. Public-record approximation, not access to private cognition. |
| 3–4 | Models, rules, six research dimensions, source and validation criteria | Core Phases 1–5, extraction-framework.md and Karpathy example. Three model filters are qualitative; case support is required for rules. First-hand ratio and known/new-question checks are prescribed targets, not guarantees. |
| 5 | Karpathy example emphasizes deployment reliability, hard cases and implementation evidence | Pinned example skill. Task and questions are our illustration; added value over a generic reviewer is explicitly untested. |
| 2 | Extracted procedures could help hypotheses, experiment design and critique | Our AI4R proposal, informed by Nuwa's source-first extraction, criticism and model-derived research directions. No measured gain. |
| 6 | Persona authority, incomplete evidence and familiar tests are risks | Assessment of template and fidelity rubric. Not a claim that every Nuwa output fails. |
| 6 | Empty-content input passed all six structural checks | Saved 2026-10-22 probe of quality_check.py; missing sources return success. No fidelity evaluation rerun. |
| 7 | Three entry interfaces could share a CC-factory lifecycle | Latest user direction plus proposed M2 factory context. Gap diagnosis, source reproduction and person/trait research differ before common candidate authoring, qualification and admission. No implementation claimed. |
| 8–10 | Three-arm comparison tests incremental value beyond generic prompting | Proposal refined after Luna review. Same corpus/task evidence/model/tools/budget; generic checklist length-matched; no result claimed. |
| 11 | A skill needs declared ports, needs/effects/budgets, versioning and normal admission for governed CC use | Local CC Reference and skills-to-CC notes. Verifier remains declaration + output; input-dependent checks are separate. |

Nuwa's useful methodological features are primary-source priority, saved research, separation of public statement/third-party report/inference, retention of contradictions, model-specific fact gathering and bounded refinement. AI4R can imitate these in procedure authoring without reproducing celebrity voice or copying Nuwa's runtime assumptions. Its topic-skill variant also supports neutral synthesis, though the main presentation explains its person-to-skill product first.

Its fidelity rubric evaluates stance, style, uncertainty, source transparency and structure. These do not establish scientific-review improvement. Separate LLM judges can share biases. The template asks for explicit inference labels, while some examples keep source judgments internal. Actual output checks must enforce evidence rather than trust a structural checklist. Runtime-specific paths and large research/context costs also need adaptation; no fixed six-agent swarm is proposed as an AI4R requirement.

The three-arm trial freezes expert-source excerpts and task evidence across plain reviewer, generic checklist and extracted procedure. It measures supported objections, missed failures, unsupported claims, uncertainty, latency and cost on new tasks with blind scoring. It can support a bounded usefulness claim. It cannot isolate the causal contribution of every phase, prove a person has been replicated or justify automatic adoption.

The raw Luna report remains in the dated review batch. Historical rev2 source review is preserved as a `.snapshot` under `history/rev2/`. This revision supersedes the earlier factory-first narrative and the interim claim that AI4R is merely an optional connection. AI4R value is the central question; integration details remain proposals rather than implementation facts.

## Method and entry-interface refinement

The table examples paraphrase the Karpathy skill: understanding through construction is a model; inspecting data before model training is a heuristic; reconstruction versus speed is a tension; tail-failure evidence is a model-derived research direction. These are source-snapshot examples, not independent verification of the person's private cognition. The core prescribes at least two domains, generative power and distinctiveness for a model. It also uses repeated claims as a research signal; repetition does not prove truth.

The third interface accepts a name and trait as research intent. Public evidence must support the requested trait before the factory drafts a method. The first interface diagnoses a real gap from run/task evidence rather than assuming every failure means a missing capability. The paper/repo/data path reproduces and adapts supplied method evidence. These routes can converge on common candidate/check/admission machinery, but route-specific evidence and validation remain necessary. This presentation refines the proposed direction; it does not replace maintained architecture contracts.

## Current ordering and value judgment

Slide 2 states a positive assessment of design utility while distinguishing it from unmeasured task-quality gain. Slide 3 presents source exploration and slide 4 presents its extracted models/rules. The source-supported method and all empirical boundaries remain unchanged.

## Critical scope correction (supersedes broader value endorsement)

Nuwa contributes a person-plus-trait research/extraction interface, not a superior general method for evidence-backed capabilities. AI4R retains its own evidence, qualification and admission. Source reread confirmed stance30/style20/uncertainty20/source15/structure15 in the fidelity rubric, with 3 known-position, 1 unfamiliar and 1 style question. This tests a small sample of persona fidelity, not AI4R task performance. The rubric separates answering and judging agents and recommends extra judges for important conclusions; these safeguards do not eliminate shared-model bias. The checker returns success for absent or untyped source sections. The saved placeholder passed6/6; it was content-free boilerplate, not a zero-byte file. This proves a lint weakness, not universal poor persona output. Our proposed trial now distinguishes source attribution, corrections and authoring effort from independently measured downstream task utility.
