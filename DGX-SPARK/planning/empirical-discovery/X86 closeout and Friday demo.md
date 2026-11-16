---
id: inference-factory-x86-closeout-20261110
status: inspected-records-demo-selection-proposed
source: Sources/Prompts/2026-11-10-campaign-closeout-inspection.txt; research/inference-campaign-closeout-20261110/source/CLOSEOUT.md
last_reviewed: 2026-11-10
next_action: Prepare and rehearse the smallest build-component-test demo; preserve campaign scope and unqualified claims
---
# X86 closeout: what we learned and what to demo

**Follow-up evidence correction:** [[Designs/Inference Factory - Empirical Discovery/Follow-up evidence|Raw records now confirm up1 MUL_MAT passed and the recovery demo ran once]]. Targeted reuse-hit/alias/graph qualification is still missing; the profile parser has an unavailable-as-zero defect. Jetson ZIP transfer is pending authentication. One useful CC remains the demo core.


**Latest Friday scope — one useful CC:** [[Designs/Inference Factory - Empirical Discovery/One useful CC demo|One tool OR one component is sufficient]]. Build/agent/Manager/mock-lab integration is optional enrichment. Prioritize concrete, reliable contracts and verifiable outputs; the full recovery pipeline is not a required demo.


The objective remains [[Designs/Inference Factory - Empirical Discovery/README|discovering Lab Manager and useful initial CCs through real inference improvement]]. The user asked to preserve the entire supplied closeout, read the findings and derive a smaller Friday demo. This is an evidence review, not authorization to resume GPU work or rewrite the implementation.

[Preserved package](../../../research/inference-campaign-closeout-20261110/README.md) contains the byte-exact ZIP, committed campaign snapshot, separate raw job/overnight logs, exported bundles and available Nsight reports. Commit: `ecaa4b0d1ed134d598993ca9f26e21745b0bbd4e`, branch `x86/c2-resume`. The source host HEAD and local origin ref matched; its evidence stream was modified. The original three handoff files match committed bytes. Image tar, weights, reference logits and other large ignored materials remain on the source host. This is not a full host backup. Jetson evidence was not independently acquired.

## Changed understanding

The earlier reported “no full-engine win yet” is superseded for **Granite Q8_0 Q8 reuse**. Offline arithmetic on the retained same-image OFF/ON job gives 793.178 → 810.429 t/s, **+2.1749%**, 24 clean completions in that saved job. We checked 914 stdout/stderr hashes across 54 saved attempt results and 1,100 files against 54 export manifests, without missing/mismatched files. These are record integrity/arithmetic checks, not new GPU measurements or independent proof of origin.

Larger Qwen gains use upstream placement/cache/speculation levers. Keep those separate from our code gain and from representation changes. Granite-to-Qwen transfer predictions often failed; a successful hybrid harness lost in the engine. Proxy and host applicability are first-class evidence, not universal factory defaults. Relayed Jetson UMA conclusions remain unverified here.

## Manager and CC lessons

Prioritize pinned producer/consumer contracts and actual input identity; separate execution, cleanup, evidence completeness and scientific verdict; retain new attempts without overwriting old ones. Capture outside the disposable target, but state sandbox/process versus host-loss limits. Observe swap/fault/CPU/IO interference and sampler coverage. Parser failure cannot destroy execution evidence. Capture-time privacy controls and a large-artifact store are concrete needs.

Initial small portfolio: build CC and patch/component contract; engagement + paired quality testing; matched measurements/resource observation; bounded profiler capture/analysis; handoff/model-inspection tools; and freeze/A-A/paired-A-B/retained-negative methodologies. Q8 reuse and KV fix are scoped component examples, not an entire engine CC. Reuse Buildx/Bake, CMake, Docker, llama.cpp and NVIDIA tools before creating infrastructure.

## Friday selection and readiness

[Demo plan](../../../research/inference-campaign-closeout-20261110/friday-demo.md): **one component → Build CC → identified engine image → bounded real inference test → evidence**, optionally interrupted sandbox and a new attempt after confirmed stop. Other team owns lab-agent provisioning. Agree an existing envelope with them; a local adapter demonstration is labelled local. Large-model results supply recorded context. The user values learning tools/methods/components beyond the demo.

The existing recovery script displays a historic novmm-4 build; it does not build/transfer images and only has recorded dry validation. MANAGER-DESIGN claims a rehearsal occurred, but the script's saved validation says live Docker was not run. D044 claims an up1 backend test passed; CLOSEOUT says it was not run. Use weaker claims until raw proof or a new rehearsal resolves them. Three factory tests fail and are reportedly stale. A reference's batch-shape numerical floor diagnoses a gate problem; it does not by itself prove task-level or generated-conversation equivalence.

[Bounded developer handoff](../../../research/inference-campaign-closeout-20261110/developer-handoff.md) defines concrete prep. No services were stopped or GPU tests launched in this inspection. CLOSEOUT reports owner services restored and a prior public-history email exposure. No history rewrite or public redistribution was performed. Original bytes are retained; display/export needs privacy review before sharing.

Detailed [assessment](../../../research/inference-campaign-closeout-20261110/assessment.md) and [audit](../../../research/inference-campaign-closeout-20261110/record-audit.json) distinguish observed records, reported host state, interpretations and unqualified capabilities. Final Incus/remote receiver integration, hard VRAM cap and host-loss survival remain open.
