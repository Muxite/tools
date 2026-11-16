---
id: muse-final-build-challenges-md
status: current-design-proposal
source: November 6 accepted presentation plan and user steering; pinned sources in Evidence
last_reviewed: 2026-11-06
next_action: Use the final deck for design discussion; qualify implementation before claiming results
---

> **Post-presentation revision, November 9:** [[Post-presentation design revision]] is the current conceptual reference. Contract, CC and release image are distinct. Tool/skill CCs support agents; component CCs supply engine functionality. The lab agent now sits outside the experiment Incus instance in a separate management container. Earlier diagrams/specimens below remain historical where they disagree.

# Implementation challenges and qualification order

| Challenge | Why it matters | Bounded evidence |
|---|---|---|
| Actual Muse checkpoint, representation and fit | public source defaults do not confirm the selected gated model | approved config/weights/tokenizer/pack and actual runnable image |
| GPU/profiler path | current CC image foundation does not attach GPU/perf implicitly | known CUDA/NVTX fixture, separate Systems/Compute gates |
| Faithful image execution | digest alone does not protect writable root/mounts/dependencies | read-only code/inputs; effective mounts, injected libraries, loaded identity |
| Marker/counter coverage | missing hooks can mimic missing work or misattribute fused paths | source/build/manifest→loaded generation→raw trace correlation |
| Matched serving/correctness | workload/cache/token policy changes can masquerade as optimization | protected unprofiled trials and independent supplied checks |
| Factory evidence export | local files are not yet durable shared reference | all outcomes, manifest, receipt; retain unexported evidence |
| Resource accounting | integrated CPU/GPU memory and nested cgroups are not interchangeable views | allocation/quota/OOM probes and effective profile |

No implementation duration estimates or numerical complexity scores are asserted. Initial disposable CUDA qualification establishes lab capability only. Runtime persistence/module loading is deferred to [[Future experiments]], not a prerequisite.
