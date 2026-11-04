---
id: experiment-register
status: active
source: Active Stage
last_reviewed: 2026-10-23
next_action: Qualify the three-arm accuracy study and inspect lab runtime receipts
---
# Experiments

**Current accuracy protocol:** [[Experiments/CC Accuracy Study]]. The older general-work pilot below remains development material and cannot establish the updated accuracy claim. [[Designs/Lab Progression]] records whether real Docker checks have been performed; unit tests alone are not lab acceptance.

First implementation target: [[Experiments/First CC Demo|Demo order, the supplied ai4r_M1 code, and Codex dependencies]].

| Experiment | Question | State | Method |
|---|---|---|---|
| CC accuracy comparison | What do declarations and checks add on matched tasks? | Proposed, unrun | [[Experiments/CC Accuracy Study]] |
| Lab lifecycle | Can isolated runs export evidence and clean up without loss? | Synthetic Docker smoke verified; actual M1 and durable VM qualification pending | [[Designs/Lab Progression]] and [[Resources/lab/README]] |
| Per-CC containerization | What isolation/reproducibility benefits justify its overhead? | Proposed, unrun | [[Designs/cc-containerization-and-lab-isolation]] |
| Skill conversion | Does a converted skill become a useful, dependable CC? | Proposed, unrun | [[Designs/skills-to-cc-mapping]] |
| Future-hardware workload model | Can an abstraction predict a relevant hardware requirement? | Problem definition pending | [[Workstreams/Workload Characterization]] |

Use [[Templates/Experiment]] for each executed campaign. A protocol, a passing software test, and a research result are different artifacts.

## Historical development material

[[Experiments/cc-effectiveness-protocol]], [[Experiments/cc-pilot-case-catalog]], and [[Experiments/cc-pilot-task-prompts]] retain the earlier general-work pilot. They are not the current three-arm accuracy protocol or protected held-out cases.
