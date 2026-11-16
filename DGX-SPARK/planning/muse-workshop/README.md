---
id: muse-final-readme-md
status: current-design-proposal
source: Sources/Prompts/2026-11-09-post-presentation-workshop-takeaways.txt
last_reviewed: 2026-11-10
next_action: Use the Muse procedure handbook to select a bounded tool or component and qualify the model/provider prerequisites
---

> **Session closed, November 9:** [[Resources/Handoffs/muse-design-20261109/Session closeout]]. The final dated PPTX is in Downloads. Resume focused design from [[Resources/Handoffs/muse-design-20261109/Start here]].


> **Continue here:** [[Resources/Handoffs/muse-design-20261109/Start here]]. Input label: **System ontology + plaintext***. *The ontology format is unknown at time of writing; no delivered template is assumed.*


> **Latest feasibility recommendation, November 9:** [[Asynchronous lab manager and executor]] proposes a Factory Lab Manager API plus deterministic external executor. The earlier always-present reasoning lab agent is optional, not a starting requirement. The Manager is the Factory’s logical lab gateway. This recommendation remains a design proposal.

# Muse Spark: CC and inference-lab workshop

**Current focus — November 10:** [[Designs/Inference Factory - Empirical Discovery/Muse Spark procedures and CC handbook|Muse Spark Open on DGX Spark 128 GB: procedures and CC portfolio]]. Muse/Spark is the primary engine target; RTX/Jetson campaigns supply supporting evidence and reusable tools, not target qualification. The illustrated handbook uses named capability cards, six diagrams and multi-CC node toolkits; it maps 11 procedures to 12 tool candidates, four component families, Field Guide methodology and a conditional Specialist agent role. One useful CC remains sufficient for Friday.

**Supporting experiments:** [[Designs/Inference Factory - Empirical Discovery/README|Granite/RTX and Jetson campaign findings]] inform the tools and procedures. Their gains do not qualify Muse/Spark. The current handbook supplements the retained workshop design; the runtime remains unqualified.

**Current proposal:** plaintext intent and system ontology feed requirements compilation. The resulting contract guides a builder agent swarm using tool/skill CCs and component CCs. The deliverable is a runnable immutable engine image, with its own runtime interface, sent to the lab.

[[Post-presentation design revision]] is the current interpretation of the workshop takeaways. The earlier [[Post-presentation contract and ontology]] preserves the first meeting notes. Prior deck artifacts remain retained as historical versions.

The proposed Factory Lab Manager accepts asynchronous jobs and returns a job ID so the builder can continue other work. A deterministic executor in a separate management container outside the experiment Incus instance stages immutable submissions and follows a bounded correctness/benchmark/profiling playbook. A reasoning lab agent is optional; existing Factory agents can analyze results and request bounded follow-ups. Durable experiment checkpoints and all available evidence return to Software Factory knowledge and telemetry. Recovery recreates identified software and reruns declared trials; it does not promise live CUDA-state restoration.

CC Factory is capability production within Software Factory. Reusing shared planning/build/evaluation workflows is the proposed direction. Tool CCs improve the factory; component CCs provide reusable parts of its engine product. The contract is not a capsule and the whole engine is not a CC wrapper.

## Reading route

- [[Presentation outline]], [[Presenter script]] and [[Presentation speaker notes]] for the revised deck.
- [[Post-presentation design revision]] for conceptual corrections and recovery rationale.
- [[Tools]], [[NVTX engineering CC]], [[Inference layers and profiling]] for capability design and measurements.
- [[Resource provisioning]], [[Future experiments]] for qualification and conditional persistence work.
- [[Evidence]] and [[Implementation status]] for pinned sources and limits.

The editable deck and revision outputs are maintained under `outputs/muse-inference-workshop-20261105`. No actual Muse engine, DGX Spark profiling qualification or performance measurement is claimed by this task.

