

> **EARLIER GUIDANCE: superseded for the current demo.** Use [the November 12 expert-streaming prompt](<20261112 Satay Expert Streaming Demo Agent Prompt prepresentation.md>). This file remains a dated technical/history reference; its generic build order, thread-naming emphasis and old pending-result statements do not define the current assignment.

# 20261111 Collaborative CC Demo Plan prepresentation

Presentation target: 10 minutes inside a 15-minute slot. Prepared November 11, 2026. This plan follows the new collaborative demo request; the previous Trace Reader-only route remains a fallback. This is a presentation and implementation brief, not evidence of a completed new engine run.

## Implementation authority

[The Satay implementation handoff](<20261111 Satay CC Factory Implementation prepresentation.md>) specifies the current build assignment, including iterative replanning and shared evidence. Earlier suggestions here are presentation context; the new handoff controls implementation choices. No direct node-to-node prose handoff is an authoritative evidence path.

## The story

**Presentation boundary:** the ten minutes belong entirely to the CC/software-factory presenter. RSI profiling, diagnosis and the next improvement are on the RSI presenter’s separate time. End with a brief artifact handoff; RSI results are not a readiness requirement for this talk.

Take an identified inference engine, add a reusable component with guidance from a CC skill, invoke a Builder CC to produce an identified image, and send it through a minimal Lab Manager to a demo lab that really executes inference. Close by showing what the component, skill and Builder contributed, then hand the source, image and evidence to the RSI owner. Their profiling and next improvement happen in their separate presentation segment.

Keep four artifacts visible throughout: component version, integration diff, image identity, lab report. The audience should see the same identities carry across the handoffs.

The lab control software is a demonstration harness. The inference execution must be real if the presentation says the engine works. A simulated output only demonstrates the handoff interface.

## Current engine milestone

[Current source, queue status and revised coder priorities](<20261111 CC Demo Engine Milestone prepresentation.md>). Verified main/jetson/c1 pin: `682c6377da20d9229ef1fdb705f63a7a751d14cb`. This update governs component selection and measurements.

## Earlier component candidate and integration sequence

**Historical fallback, superseded as the primary recommendation by the current c2 milestone:** the existing per-weight-type gate/up unfusion patch, initially limited by the demo's admission rules to the validated Orin workload with Q4_K experts. This recommendation depends on the current engine being compatible with the preserved llama.cpp source and model. Confirm the current engine first; do not assume that the engine now under development is the historical engine.

Source: `C:/Users/m50066326/huawei/research/jetson-campaign-closeout-20261110/snapshot/campaign/cc/moe_dispatch_sm87/patches/03-unfuse-ids-by-type.patch`. Historical base: `31288c9c66e59377f7788d920678a565bb89dd37`.

The saved campaign's Q4_K-expert result was approximately +23.64% decode throughput; Q8_0 regressed approximately 6.21%. These are historical observations, not promises for the current engine. BF16 has additional activation-rounding considerations. Prefer Q4_K for the first demonstration if its exact model and working baseline remain available.

Patch 03 replaces patch 01; do not stack them. Despite its folder name, patch 03 contains no architecture guard. Enforce demo applicability explicitly in integration/preflight. Its setting is `GGML_CUDA_J_UNFUSE_IDS_TYPES=q4_K`; clear the legacy `GGML_CUDA_J_MMF_IDS` alias and all inherited optimization overrides for the OFF control. Each setting needs a fresh process. A printed enabled setting is not proof that the changed execution path ran.

Build in this order:

1. **Baseline contract:** identify current engine source, Jetson host/runtime, model bytes, exact runnable command and baseline output.
2. **Builder CC adapter:** establish that this engine can be built and delivered through the real CC runtime. This is the critical integration risk; prove it before slide polishing.
3. **Component CC and integration skill:** package the patch plus applicability, integration, validation and rollback guidance; show a real coding agent reading it and producing a diff.
4. **Minimal Manager and demo lab:** accept the image, run fixed checks on the actual Jetson, return evidence through Manager.
5. **Evidence handoff:** package the source, component, build and lab evidence for the next presenter. Profiling and further optimization belong to the RSI owner’s separate work. Trace Reader remains an optional alternative CC demonstration, not a required profiling segment.

These are separate responsibilities, not five new services. The skill and component can use CC-v2 passive materials. The build operation is executable. Do not invent a new capsule schema or restore the removed M1/RSI stack.

## Ten-minute running order

| Time | Screen and presenter action | What the audience learns |
| --- | --- | --- |
| 0:00–1:00 | Inference-engine task and the three CC roles: component, skill, executable tool | How CCs contribute to the software factory |
| 1:00–2:00 | Baseline engine on Orin, selected component, applicability and expected behavior | What reusable code is being added and why |
| 2:00–4:30 | Real agent discovers the CC, reads the integration skill, applies the component and handles one bounded integration/configuration issue | The skill guides engineering; the component changes engine behavior |
| 4:30–6:30 | Builder CC invocation: dependency preparation, build logs, receipt and identified image | An executable capability turns source changes into a deployable artifact |
| 6:30–8:45 | Send the image through Manager to the demo lab; show real inference, effective configuration and correctness evidence | The image actually runs and evidence follows the artifact |
| 8:45–9:30 | Recap component version → integration diff → build/image identity → lab report | The reusable factory workflow and what each CC contributed |
| 9:30–10:00 | Hand the source, image and evidence bundle to the RSI presenter | A clean collaboration boundary; profiling and further improvement follow in their segment |

Use five or six slides as anchors, with the middle of the talk on the actual demo screen. Keep detailed architecture and historical benchmark tables in backup material.

Do the full dependency acquisition and build before rehearsal and retain the real invocation. For the talk, use a short recording of that invocation with its receipt, or a rehearsed warm build if it fits. Label recordings and cached builds. A historical warm Jetson rebuild took about 141 seconds; the initial native build took about 3,154 seconds. Do not make the two-minute build segment wait for a full cold build; use a labeled recording of a real invocation when necessary. Do not run the compiler concurrently with scored inference measurements.

Readiness ends at the working image, demo-lab result and complete handoff. Do not wait for J-OM12 profiling, a second candidate or an RSI speedup to rehearse this CC presentation.

## Coder work orders and acceptance

| Owner | Implement or adapt | Required demonstration evidence |
| --- | --- | --- |
| Current inference-engine owner | Supply source commit, model/tokenizer identities, JetPack/L4T/CUDA information, baseline command and fixed test input; confirm component compatibility | A baseline image actually runs on the intended Orin Nano; model fits the chosen context/workload |
| CC runtime and integration owner | Reuse reduced CC-v2; expose component materials and integration skill; agent applies the patch in an owned checkout | Real JiuwenSwarm transcript with discovery/material reads, source diff, applicability result and CC receipt for executable calls |
| Build owner | Adapt existing Jetson `cc/build_engine`; add explicit dependency preparation or a pinned prepared build environment; handle long build calls | Dependency identities, build logs, exit state, image ID/digest, source/patch hashes, and an image transport reference that the lab can actually obtain |
| Demo lab owner | Small deterministic submit/status/result path; fixed runner outside the tested container; evidence ingestion through Manager | Accepted job, verified image identity after transfer, actual inference output, correctness result, logs, failure/cleanup status and durable evidence acknowledgment |
| RSI owner, separate segment | Receive the source, image and evidence; own profiling and subsequent improvement on their time | For this talk: agree on the handoff contents only. Their later results are not a CC-demo acceptance gate. |
| Presentation owner | Maintain narrative, exact screen sequence, evidence labels and fallback recording | One timed rehearsal at or below ten minutes, with no ambiguous live/recorded/simulated claims |

### Two build gaps that must be resolved

The current `agent_mcp.py` `cc_call` delegates to `Host.call` without passing a timeout; `Host.call` defaults to 60 seconds. Make the build deadline an operator-controlled setting passed to the existing call path, and check outer agent/request timeouts. Do not invent a YAML timeout field. If interactive progress requires asynchronous jobs, implement explicit job identity/status/cancel and retain completion records, but that is an extension, not an existing feature. A client timeout must not be reported as proof that child compiler or BuildKit work stopped.

The preserved Jetson builder compiles natively and explicitly installs no packages. It assumes GCC, CMake, Ninja, Git, Docker/Buildx and JetPack CUDA already exist. To claim “gets dependencies and builds,” add a real dependency preparation step with a recorded recipe or use a qualified pinned build environment. Separate host driver/runtime prerequisites from fetched build dependencies; do not attempt a JetPack upgrade during the demo. NVIDIA documents the Jetson container/runtime relationship at https://developer.nvidia.com/embedded/jetson-cloud-native .

### Minimal lab boundary

Submit an image reference plus expected identity, model/config/test references and run ID. The runner verifies identity, starts the container, runs fixed input and correctness checks, records exit/cleanup state, then sends the result bundle to Manager. Manager persists it and returns an acknowledgment. Keep the runner and evidence outside the tested container.

If the mock Manager lives on the same Jetson, it can demonstrate a logical transfer using a verified local image reference. Do not describe that as a network image transfer. For a separate host, exercise an actual registry pull or archive export/import and verify identity after transport; a local image ID is not a downloadable address.

The demo needs no autonomous test designer, multi-lab scheduler, general recovery framework or complete lab agent. Preserve distinct execution, correctness, evidence-completeness and cleanup states. An error is a visible failed/blocked attempt, not generated sample output.

## Evidence needed before calling it ready

- A real agent uses the CC runtime, not only a shell script with a CC label.
- The build record links the integrated component and source to the exact delivered image.
- The receiving Jetson executes that image with the declared model and configuration.
- Correctness checks use a reference and tolerance chosen before viewing the candidate result. Successful text generation alone is a smoke test.
- A claimed speedup uses matched workloads, warm-up, token counts, power/thermal conditions and repeated unprofiled runs. Keep profiler timing separate. The rehearsal establishes whether the chosen protocol fits; use prepared measurements in the talk.
- Component engagement is observed separately from configuration. If using Q4_K, do not describe its standalone path as BF16 MMF.
- The RSI handoff contains source/patch/build identities, executable command, raw results, configuration and failures. An engine patch alone demonstrates optimization, not improved reusable factory capability.
- A missing live connection triggers a labeled recording of a real run. The saved RTX NCU demo is a second fallback and remains labeled historical RTX evidence.

## Does the supplied file match

The pasted file's opening distinction matches: factory work improves candidates within a task; RSI improves reusable skills/tools/verifiers/workflows across tasks. Keep that sentence.

Its full Lab Agent lifecycle is a future architecture, not this demo's implementation. Label the demo as a fixed harness with a real engine run. Keep evidence routed through Lab Manager, which owns ingestion/storage acknowledgment; let the lab runner produce the report. The independent acceptance boundary should remain even if implemented by simple fixed checks and a human reviewer.

The expert-placement experiment is explicitly a proposed Strata/Spark experiment. It is not evidence for Orin Nano and is a poor main example for this ten-minute component demo. Move it to backup/future-work material and use the Orin component as the main walkthrough.

The proposed RSI collaborator improving one engine is useful, and, in the RSI presenter’s separate segment, the reusable improvement should be explicit: for example, a versioned integration skill requiring dtype-specific eligibility and OFF-control hygiene, or a benchmark tool enforcing matched settings. Present this as a proposal until tested on fresh tasks; one successful engine result does not establish cross-task RSI gains.

The handoff ZIP contains byte-identical copies of the three supplied Markdown handoffs and the Downloads PPTX. Its examples ZIP and manifest have no identical same-named Downloads files. The old demo handoff intentionally treats component/build/lab as optional; this new plan changes that priority for the collaborative presentation. Active handoffs and notebook entrypoints have since been updated; older main-demo instructions are marked superseded. Original bytes are retained in the superseded-handoff backup.

## Source trail and unresolved input

Runtime checkout: `C:/Users/m50066326/huawei/AI4Research-Development/ccv2-work`, inspected clean at `2889a1d6342e9baa7721648eca196bbce79a31d4`. The November 5 demonstration summary records earlier real agent CC calls, including a synthetic image service; those are not inference-engine or Trace Reader qualification.

Jetson assessment: `C:/Users/m50066326/huawei/research/jetson-campaign-closeout-20261110/assessment.md`. Read patch 03's addendum and final qualification update, rather than treating the older opening paragraphs as the final state. Campaign snapshots are read-only reference inputs for adaptation.

Current Builder source: `cc/build_engine/` in siminfeng at the verified pin. The November 10 local snapshot is historical comparison material.

Trace Reader starting point and acceptance cases: `C:/Users/m50066326/Downloads/20261111 CC Demo Handoff prepresentation.md`. Its NCU fixture is historical RTX data; a hardened NCU CSV parser is not automatically a Jetson Nsight Systems reader.

Pasted source SHA-256: `b1da9dd57947030169bfbe1cab1e09c625c1e4cd991447bdc8cc77a2c5f33fca`.

Current engine source: https://github.com/Muxite/siminfeng . Remote main and jetson/c1 verified at `682c6377da20d9229ef1fdb705f63a7a751d14cb`; current paths are rooted at the repository, not campaign/. See the Engine Milestone for evidence status and component selection. Individual coder ownership is still unassigned. No new GPU run, build, runtime invocation or revised slide deck is claimed by this investigation.

