---
id: inference-factory-one-useful-cc-20261110
status: user-scope-refined-concrete-design-proposed
source: Sources/Prompts/2026-11-10-one-useful-cc-demo.txt; research/inference-campaign-closeout-20261110/next-cc-design.md
last_reviewed: 2026-11-10
next_action: Request targeted missing evidence, then qualify one useful CC before expanding the supporting demo loop
---
# One useful CC is the Friday core

**Jetson closeout now received:** [[Designs/Inference Factory - Empirical Discovery/Jetson closeout and CC implications|Per-type graph dispatch and portable-tool implications]]. Saved Orin results recompute to +23.64% Q4_K, +19.21% BF16 and −6.21% Q8; target qualification stays local. One useful CC remains sufficient for Friday.


**Follow-up evidence correction:** [[Designs/Inference Factory - Empirical Discovery/Follow-up evidence|Raw records now confirm up1 MUL_MAT passed and the recovery demo ran once]]. Targeted reuse-hit/alias/graph qualification is still missing; the profile parser has an unavailable-as-zero defect. The prior Jetson transfer block is resolved; see the Jetson closeout update above. One useful CC remains the demo core.


The user's latest direction narrows the required demo to **one useful tool OR one engine component CC**. More orchestration, building and profiling is welcome but optional. A simple mock lab is sufficient; final lab provisioning remains the other team's responsibility. This corrects any interpretation of the previous build-to-result/recovery sequence as a mandatory Friday pipeline. The central goal remains learning the useful CCs and Manager responsibilities through real engine improvement.

The proposed richer story is: a JiuwenSwarm agent uses a profiling tool, reads a component's integration contract, proposes a falsifiable experiment, integrates it into a pinned base engine, invokes a builder CC, and submits a request through Manager to a simple execution fixture. The agent chooses the hypothesis; Manager deterministically coordinates attempts and evidence. The end-to-end loop is an extension, not the definition of a successful one-CC demo.

## Proposed first deliverables

[Detailed design](../../../research/inference-campaign-closeout-20261110/next-cc-design.md) recommends a finite read-only **cuda_profile_report** CC, reusing the campaign's actual Nsight Compute parser, plus passive **q8_activation_reuse** component materials. The first tool has precise scope, input hashes, bounded file/row sizes, strict metric/unit/identity handling, deterministic outputs, honest heuristic labels and raw-fixture/property verification. It can run without GPU/Docker privileges; live profiler capture is separate and explicitly labelled if recorded.

The component is a real source patch with a scoped Granite +2.17% result. It applies to eligible unfused single-token Q8 matvec activation quantization, not general MoE expert caching. Tensor aliasing, graph replay, stream ownership, persistent scratch memory, exact base/patch identity and fresh-process OFF/ON are critical integration details. Existing host-mock tests do not automatically qualify CUDA alias/graph behavior. Preserve the exact measured scope and request missing raw evidence.

Reuse the existing Build CC rather than inventing a build service. Current JiuwenSwarm CC v2 supports finite tools and passive materials; native code is trusted-local, finite image calls have only workspace mounts, and same-key calls replay receipts. GPU profiling/Docker builds do not fit a generic unprivileged image CC without additional provider support. Existing source_build.py builds CC payloads, not engine OCI images. CC v2 is on a separate scope-reset branch: M1 demo-base compatibility must be checked instead of whole-branch cherry-picking.

## Tools motivated by actual failures

After the profile tool/component, prioritize engagement probes, measurement-window observation (swap/faults/contention), paired result assessment, image handoff verification and pinned model/workload fetch. Reuse existing campaign code and upstream tools. Keep each operation's evidence/unknown states separate; avoid a giant all-purpose optimizer capsule.

[Self-contained agent evidence request](../../../research/inference-campaign-closeout-20261110/next-agent-evidence-request.md) asks for existing CUDA qualification and engagement evidence, representative profiler inputs and capture identity, real Build CC invocation/records, JiuwenSwarm readiness and contradictory qualification/rehearsal claims. It requests read-only inspection first, not resumed GPU work. No CC implementation, new profile run or JiuwenSwarm integration has been claimed in this design pass.
