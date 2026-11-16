---
id: muse-final-presenter-script-md
status: current-design-proposal
source: Sources/Prompts/2026-11-09-post-presentation-workshop-takeaways.txt
last_reviewed: 2026-11-09
next_action: Use revised slides for design discussion and qualify the proposed interfaces
---

# Presenter script for the Factory boundary and asynchronous lab proposal

Approximately nine minutes for the ten main slides. Section titles follow the revised slide sequence.

## 1. Software Factory and its lab boundary (60s)

All Factory components sit inside one boundary. The input is system ontology plus plaintext; the asterisk marks that the ontology format is still unknown. Intent and ontology become a contract; the builder uses tool and component CCs to produce the engine image. The Lab Manager is the lab gateway. The builder submits a job, receives its ID, and continues other work. Our starting recommendation is an external deterministic worker. It runs the bounded playbook and returns evidence through the Manager, without requiring a resident reasoning agent.

## 2. CCs are reusable capabilities, distinct from the release contract (50s)

A CC describes a reusable capability and how to use its implementation. Tool CCs operate on the production line; component CCs become parts of the product. A contract can select many capabilities without becoming a capsule itself. Capability production can reuse the factory workflow with source-specific agents. We can compose capabilities for one job or retain a tested composite for later reuse.

## 3. Tools across the Muse inference engine (65s)

The five layers locate concrete work: API and requests, scheduling and state, model operations, expert-weight access, and CUDA execution. The token router chooses experts within a layer. Residency policy decides where those selected weights are and how they are obtained. Prefill and decode need separate trials. We attach tools where a measurement can answer a specific question, rather than collecting GPU utilization without an explanation.

## 4. Two CC roles produce different reusable outputs (50s)

The builder needs inspected source boundaries, checked instrumentation patches, prepared model data and reproducible builds. The lab needs identified launches, correctness results, protected client timings and bounded profiler captures. Each capability declares useful outputs. A profiler report remains an artifact; it need not become a new CC. Component capabilities have integration interfaces and tests, while tool capabilities are invoked to do work.

## 5. NVTX CC: reusable judgment support and repeatable edits (60s)

NVTX adds meaningful labels to the execution timeline. A reusable skill and deterministic helpers support source inspection, placement plans and checked patches. The builder then produces a new image. Executed coverage checks tell us whether those labels actually appeared. Host ranges do not mean GPU completion, and fused kernels may not preserve every source boundary. Native engine counters still explain expert misses and residency.

## 6. Crash-surviving lab control and immutable engine deployment (70s)

The external worker and protected trial runner sit in a management container outside the experiment Incus instance. The worker uses scoped Incus access and fixed stage wrappers. A durable job table in Factory tracks state, claims and exports. An engine crash therefore does not directly kill the controller, although shared-host driver or kernel failure remains a separate recovery boundary. Several jobs can be queued; one Spark admits only one active scored or profiling GPU job.

## 7. A playbook spends profiling effort only where needed (65s)

The worker follows approved deterministic stages. Correctness comes first, then representative timing without heavy profiling. Systems captures a timeline only when needed. Compute investigates selected kernels in a separate attempt. Persist stage and attempt records as the playbook proceeds. On a crash, retain available evidence, confirm the old process stopped, and retry only within budget using a new generation. Recovery resumes the workflow; it does not claim to restore CUDA or KV-cache state. A cancel request or stale heartbeat is not proof that prior work stopped. Factory agents can analyze saved evidence and submit another bounded job.

## 8. Combine profiler data with engine facts and matched trials (60s)

Client timings show the serving result. Systems and Compute help explain execution. Engine hooks supply routing, cache, placement and state facts that external profilers cannot infer. The Factory retains the combined evidence, including missing coverage. A permitted runtime configuration can be retested with the same image. A missing marker or source fix produces a new build. A fundamental requirement change needs an explicit contract revision.

## 9. Together Compiler (TKCC): potential evolution (50s)

Persistent engines and tiered tests can reduce repeated initialization work. They also need compatible loading interfaces, safe replacement, state reset, graph recapture and recovery. These are additional engine features. We retain the idea as an evolution and first measure our own setup costs. Together's experiment-throughput results do not predict Muse inference speed on Spark.

## 10. Start with attributable experiments; evolve when evidence justifies it (50s)

The first useful loop is an identified image, asynchronous job submission, bounded tests and evidence retained in Factory. Reuse existing Factory dispatch and storage where possible. Otherwise a single job table and polling worker are enough to begin; a new message broker or resident lab LLM is not a prerequisite. We can improve both production tools and engine components through the same workflow. The next design question is which evidence authorizes which change and which retest. We start with a domain-specific ontology and a small set of practical capabilities, then expand only where the evidence shows value.

Appendices support detailed questions about operations, observability, qualification, contracts, release packaging, NVTX helpers, future experiments and resource limits.
