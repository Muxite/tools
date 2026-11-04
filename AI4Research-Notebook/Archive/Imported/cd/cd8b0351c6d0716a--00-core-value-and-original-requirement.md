# Core value and original requirement

19 October 2026 · aligned to Stellven's 16 October request supplied by the user · focused static assessment with one Luna agent

## What we are trying to achieve

**AI4R uses research papers to identify and deliver worthwhile improvements to itself.** The requested feature is a complete improvement loop:

Paper → assess value against AI4R's current capabilities → choose a bounded improvement → produce PRD/design → implement → independently evaluate → admit/integrate if it helps.

Reading a paper or exposing its code as a tool can support that loop. The outcome must be an evidenced improvement to AI4R. Adding a useful scientific method can expand AI4R's capabilities; improving planning, verification, intake or implementation can improve its existing workflow. Neither should be called a gain without evaluating the relevant behavior against a baseline.

## Where Paper2Agent is valuable

The current repository provides two useful parts: a source-reviewed paper reading package, and a workflow for turning existing research code into source-backed, tested MCP tools. These can reduce effort in understanding a method and constructing an executable candidate.

It does not supply the full requested loop: judging value specifically to AI4R, identifying a capability gap, creating an AI4R feature PRD/design, implementing the corresponding platform change, and demonstrating an improvement to AI4R. A paper without a usable repository also needs an implementation path beyond Paper2MCP's existing-code wrapping route.

**Research verdict:** useful as a component and design reference. The distinctive AI4R feature is the value-assessment-to-delivery loop around it. A successful paper package or MCP conversion alone does not satisfy Stellven's requirement.

## Capability Capsules and containers

Here, CC means **Capability Capsule**. CCs provide a reusable, typed, versioned unit in which a new capability can be packaged, evaluated and admitted. A candidate new CC or an improved existing CC is a practical first target for autonomous feature addition. Changes to the planner, application or shared infrastructure may need ordinary code/design changes as well; the capsule format does not make every product change plug-and-play.

A container is optional support for dependency isolation and reproducible execution. It is not the core improvement mechanism. Scope it only when a selected capability needs a separate runtime, using the [container proposal](06-paper2agent-cc-container-proposal.md).

## Smallest meaningful pilot

Choose one paper relevant to a named AI4R gap and use the existing AI4R behavior as the baseline. Have AI4R produce a concise assessment: expected benefit, evidence from the paper, overlap with current capabilities, implementation fit, cost and uncertainty, then a go/defer/no-go decision.

For a go, generate a small PRD/design, implement one bounded new or improved CC, compare it with the baseline on independently prepared cases, and automatically admit it only if the predeclared benefit and regression criteria pass within its authorized scope. Include an irrelevant or redundant paper case to check that the system can reject a poor investment. A correct no-go is evidence of useful screening, but does not demonstrate the full feature-addition loop.

The autonomy target is retained: execution and admission can proceed within a previously authorized class of changes. Independent evaluation and protected admission remain outside the candidate's control. The pilot should not require a fresh manual approval at every internal stage, nor imply permission to rewrite the evaluator or promotion policy.

Judge the pilot by whether AI4R selected a worthwhile improvement, delivered the specified behavior, and demonstrated the expected gain without material regressions. Record source fidelity, runnable packaging and container behavior as supporting evidence where applicable.

## Effect on earlier notes

The paper-to-CC and container estimates cover supporting parts of the request. They are **not estimates for the complete autonomous paper-to-AI4R-improvement feature**. Size the value-assessment, PRD/design, implementation orchestration, independent comparison and controlled integration work separately after choosing the pilot. This workstream remains one possible part of M2.

Source basis at Paper2Agent commit `8c2d059165ef8cdcb70dbea76655b9c2b55b38e6`: [input routing](C:/Users/m50066326/huawei/other-repos/Paper2Agent/skills/paper2agent/SKILL.md), [reviewed paper package](C:/Users/m50066326/huawei/other-repos/Paper2Agent/skills/paper2agent/paper2skill/SKILL.md), and [source-backed method wrapping](C:/Users/m50066326/huawei/other-repos/Paper2Agent/skills/paper2agent/paper2mcp/SKILL.md). These were inspected as source material; no conversion or implementation was executed.
