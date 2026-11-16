---
id: muse-cc-lab-research
status: source-grounded-proposal-runtime-unverified
source: evidence/source-receipts.json; evidence/web-receipts.json; user attachment
last_reviewed: 2026-11-05
next_action: Review the optimization spectrum and concrete tool/lab needs with the team
---

> **Post-presentation revision, November 9:** [[Post-presentation design revision]] is the current conceptual reference. Contract, CC and release image are distinct. Tool/skill CCs support agents; component CCs supply engine functionality. The lab agent now sits outside the experiment Incus instance in a separate management container. Earlier diagrams/specimens below remain historical where they disagree.

> Retained detailed context. Current November6 direction is [[Alignment and decisions]]: immutable submitted images, test-only lab, and Factory-owned knowledge/telemetry. Earlier local-workbench/native-first options are superseded, not implementation evidence.

**Current presentation revision (November 5):** [[Design rationale]] and [[Inference layers and profiling]] record the compatible Builder, optional ontology, scoped lab build/debug loop, nested Docker/Incus capture and current terminology. [[Build challenges]] and [[Data to collect]] distinguish proposed integrations from qualified evidence. The retained detail below predates that presentation revision where its scope differs.

# Research document: tools and labs for a smaller Muse runtime

## The model we are presenting

We propose an agent-driven engineering loop that can improve inference software. Agents receive an objective, source, a pinned model, a target machine, permitted changes and a budget. They use callable tools to inspect, build and diagnose. A lab runs identified products under controlled conditions. Independent evaluation decides whether the evidence supports the objective. A separate responsible owner approves adoption.

This is a design for our **CC and lab modules**. We propose the connections to the Software Factory, agent orchestration and standardized benchmark owner; we do not assume authority over their complete architecture.

A **Capability Capsule** is a versioned package of named callable capabilities. The CC declaration explains what a tool does and its inputs/outputs; the release fixes supplied implementation bytes; the host binds a call and records execution. CC v2 supports native, image and registered agent bindings. Native coding sessions need not become CCs. A **lab** supplies the actual allocation, start/stop/restart, experiment state, controlled access and protected evidence. A CC can run in a lab, but its declaration does not create isolation or make a measurement true. See [CC v2](../CC%20and%20Strata%20delivery/CC%20Protocols/README.md).

The inference engine is a native binary/configuration/dependency product, possibly delivered in an image. In this workshop's working flow it is exposed as an implemented engine CC; its hot kernels remain native. A profiler can be an external tool with engine hooks; a benchmark client can be a separate process. A sidecar is a deployment option, not the definition of a CC. The general protocol also permits software products without CCs; that does not change our chosen engine-as-CC example.

The engine also needs an internal system description: components, relationships, state ownership, memory paths and constraints. The current request carries that external ontology through `desired.materials`; desired capabilities describe the engine itself. A coding agent reads the request to implement it. The [ontology explanation](Ontology%20and%20request%20CCs.md) corrects our earlier builder-tool example and obsolete root `system` field proposal.

**Current direction:** this remains an inference-module design proposal, not a prototype selection or project plan. Another contributor owns the ontology. CC v2 has since been integrated into JiuwenSwarm with native/image/material/service demonstrations; [implementation status](Implementation%20status.md) records the evidence. The central Muse memory/quality/speed objective remains unmeasured.

## The optimization spectrum we must support

The scope is approximately the engineering territory demonstrated by Strata and DwarfStar. That includes representation and algorithmic changes as well as memory plumbing. These are options for later project planning, not commitments to implement all of them. Each option must be tested against the same agreed standardized benchmark and speed requirements; applicability to Muse remains unproven.

| Possible change | Reference mechanism | Workshop tool needed | Sensors / dyno needed |
|---|---|---|---|
| Avoid duplicate weight copies; map or share suitable buffers | Strata Spark `--mmap-experts`, native placement paths | Build/configure candidate; inspect weight and allocation layout | Load/serve peaks, mapped/resident pages, copy counts where exposed, TTFT and token rate |
| Bound expert residency and choose cache contents | Strata expert profiles; DwarfStar bounded expert cache | Versioned profile/config generation, workload analysis, restart | Hits/misses, executed expert work, memory, storage I/O, held-out latency |
| Stream weights or lookups from SSD | DwarfStar Spark SSD streaming; engine-specific backing stores | Prepare pack/storage layout, configure streaming and cache | Page faults/read bytes, queue/stall evidence, cache state, TTFT and decode speed |
| Change quantization or weight representation | Both references expose multiple model/pack formats | Convert/prepare identified weight pack; build compatible kernels | Pack size, load-time/repack peaks, numerical differences, standardized benchmark, memory and speed |
| Reuse buffers or change kernels/fusion | Native engine execution and backend-specific builds | Native coding/build tools; layer/tensor comparison | Allocation lifetimes, temporary peaks, device timing and diagnostic traces |
| Chunk prefill or overlap CPU/GPU/I/O work | Strata prefill/placement; DwarfStar streamed prefill | Configure supported chunk/scheduling controls; rebuild where needed | Prefill peak, host/device spans, I/O overlap and client TTFT |
| Change KV/session/state handling and reuse | Both references' continuation and state/recovery paths | State-case runner, session controls, candidate build | State size, context-dependent memory, interleaving/cancel/restore checks, warm vs fresh TTFT |
| Use or tune speculative decoding | Strata MTP; DwarfStar DSpark/MTP | Identify compatible drafter/target, configure candidate, verify accepted-state behavior | Drafter memory, acceptance rate, rollback/replay costs, actual sampling policy, quality and token rate |
| Adjust concurrency, batching and admission | Serving/scheduling paths in both references | Fixed-load client, configure scheduler and resource admission | Per-user vs aggregate rate, queue delay, peak memory and latency distribution |
| Explore approximate routing or reduced computation | Strata's documented DeepSeek Faster mode uses 5 of 6 experts | Explicit semantic-candidate configuration plus quality evaluation | Actual selected expert count, standardized benchmark and numerical/task differences; never report as unchanged computation |

Source basis: pinned Strata [Spark guide](https://github.com/Niko1221/Strata/blob/ffa80d73133ea5c548aefe57889a16e8085a938f/docs/DGX_SPARK_LINUX.md), [native operation overview](https://github.com/Niko1221/Strata/blob/ffa80d73133ea5c548aefe57889a16e8085a938f/docs/HOW_IT_WORKS.md), pinned DwarfStar [Spark guide](https://github.com/antirez/ds4/blob/b3f50180ec2c7324892be1f50bc83555ccb8d5e7/docs/DGX_SPARK.md), [model formats](https://github.com/antirez/ds4/blob/b3f50180ec2c7324892be1f50bc83555ccb8d5e7/docs/MODELS.md), and [speculation semantics](https://github.com/antirez/ds4/blob/b3f50180ec2c7324892be1f50bc83555ccb8d5e7/docs/SPECULATIVE_DECODING.md). This is mechanism reuse and design inspiration, not transference of their benchmark results.

Two distinctions matter. A smaller context, fewer requests or shorter outputs is a changed workload, not a memory gain under matched conditions. Quantization, reduced expert computation or changed sampling may be legitimate candidates in this design, but require explicit quality assessment and must remain distinguishable from semantics-preserving engineering. DwarfStar's default nonzero-temperature speculative mode is documented as opportunistic; its exact-sampling option is distinct. Do not assume every speculative configuration preserves the target distribution.

The agent does not need a separate capsule for each kernel. It needs a small set of reusable inspect/build/configure/observe/check/trial tools, a description of the engine's supported controls, source access, and the lab facilities to test the resulting candidate. That is our module contribution.

## The target is specific, but feasibility is not established

The [Meta announcement](https://research.meta.ai/blog/muse-spark-open) identifies Muse Spark Open as an 816B-total/42B-active MoE model. The [public model page](https://huggingface.co/meta-models/Muse-Spark-Open-816B-A42B) identifies the target repository. The public API reported revision `0fb02478b02565b2ce7fc57e6051c91172774ac9` and manual gating on November 4. That is an observed repository revision, **not an approved checkpoint for our experiment**. Raw configuration and README requests returned 401. We have not checked operators, tensor layouts, tokenizer behavior or exact execution requirements.

A simple storage calculation sets expectations: 816 billion parameters × 4 bits / 8 is **408 billion bytes (408 GB)**, before scales, metadata, activations, KV/state and temporary buffers. At two bits it is still 204 GB. These are illustrative arithmetic estimates, not a measured model-pack size. MoE's 42B active parameters reduce active computation; they do not eliminate the need to store or retrieve other weights. A 40 GB runtime would likely depend on streaming, selective residency or another validated representation. Its quality and speed remain research questions.

[NVIDIA's hardware guide](https://docs.nvidia.com/dgx/dgx-spark/hardware.html) describes the 128 GB Spark configuration with a 20-core Arm CPU, shared CPU/GPU memory and 273 GB/s bandwidth. The [current product page](https://www.nvidia.com/en-us/products/workstations/dgx-spark/) also lists OEM 64 GB options. Probe the assigned machine rather than assuming its SKU, free capacity or SSD. One physical pool must support engine data, file cache, OS and tools; RAM plus GPU memory must not be added as independent capacity.

The first question is consequently **which engine can correctly execute this checkpoint on the assigned Spark?** No running local baseline currently exists. Model recognition, a successful build, or a generic compatible API does not answer that question.

## What we learn from Strata

Reviewed source: [Niko1221/Strata at ffa80d7](https://github.com/Niko1221/Strata/tree/ffa80d73133ea5c548aefe57889a16e8085a938f). Findings are from targeted source inspection, not fresh hardware execution.

Strata separates setup/control, serving and model-specific native execution. Setup discovers hardware and prepares compatible engine/model configurations. The server handles prompts, scheduling, sessions and diagnostics. Native engines implement operators, tensor layouts, expert routing, state and generation. Its Spark guide documents Qwen and DeepSeek paths; we did not establish a Muse backend in the reviewed material.

The useful engineering mechanisms are concrete:

- **Placement and duplication control.** Its [Spark guide](https://github.com/Niko1221/Strata/blob/ffa80d73133ea5c548aefe57889a16e8085a938f/docs/DGX_SPARK_LINUX.md) uses mapped experts and Spark-specific setup to avoid unnecessary duplication. This motivates a memory-breakdown sensor and explicit residency settings, not copying a flag into an unsupported Muse engine.
- **Native packaging.** [engine_component.py](https://github.com/Niko1221/Strata/blob/ffa80d73133ea5c548aefe57889a16e8085a938f/strata_control/engine_component.py) handles `engine-component.json` schema 2, payload hashes and platform/backend requirements. Preserve this manifest when the product is Strata. A CC release is a different object; the lab must still verify the actual loaded binary and effective configuration.
- **Cheap intake.** [gguf_preflight.py](https://github.com/Niko1221/Strata/blob/ffa80d73133ea5c548aefe57889a16e8085a938f/strata_control/gguf_preflight.py) bounds metadata/directory inspection without reading tensor payloads. Reuse the pattern; this GGUF parser is not a Safetensors-to-engine converter or proof of numerical validity.
- **Diagnostics.** [telemetry.py](https://github.com/Niko1221/Strata/blob/ffa80d73133ea5c548aefe57889a16e8085a938f/serve/telemetry.py) samples NVML and OS/psutil observations. Its bounded live history and unavailable readings are useful for diagnosis, not a durable accepted run record. The lab independently persists samples.
- **Profile construction.** [make_profile.py](https://github.com/Niko1221/Strata/blob/ffa80d73133ea5c548aefe57889a16e8085a938f/tools/make_profile.py) explicitly says the full shipped ranking makes the default base-first construction a no-op; `--reorder` or `--no-base` changes that policy. A successful tool exit is insufficient: inspect whether the proposed artifact actually changed.
- **Path-specific traces.** The Qwen routing writer and DeepSeek `DS4_TRACE`/`DS4_PROF` surfaces require different parsers. A routing record is not automatically a timestamped request timeline. Drafted/rejected work must be distinguished from accepted output. Unsupported trace coverage must remain visible.

Strata's [standard benchmark protocol](https://github.com/Niko1221/Strata/blob/ffa80d73133ea5c548aefe57889a16e8085a938f/docs/BENCHMARK_PROTOCOL.md) is explicitly a draft with pilot validation pending. It offers useful fixture/identity discipline; it is neither standardized benchmark nor an accepted Muse quality evaluator.

## What we learn from DwarfStar

Reviewed source: [antirez/ds4 at b3f5018](https://github.com/antirez/ds4/tree/b3f50180ec2c7324892be1f50bc83555ccb8d5e7), presented upstream as DwarfStar. Treat it as a separate implementation, not an interchangeable Strata component.

Its [Spark guide](https://github.com/antirez/ds4/blob/b3f50180ec2c7324892be1f50bc83555ccb8d5e7/docs/DGX_SPARK.md) and [Makefile](https://github.com/antirez/ds4/blob/b3f50180ec2c7324892be1f50bc83555ccb8d5e7/Makefile) supply a concrete CUDA/GB10 build path and examples of SSD-streamed models. Its [testing guide](https://github.com/antirez/ds4/blob/b3f50180ec2c7324892be1f50bc83555ccb8d5e7/docs/TESTING.md) exposes `--dump-tokens`, `--dump-logits`, `--dump-logprobs` and server `--trace`, plus checkpoint-matched continuation tests and state recovery cases. These inspire correctness tools and a diagnostic adapter. They do not prove Muse support or predict its performance.

The directly relevant lesson is that **bounded residency and SSD access are engineered paths**, with format-, operator- and backend-specific behavior. Exposing a cache budget alone does not implement them. Host memory estimation in `ds4_linux_memory.h` also distinguishes available from nonmovable memory; a reported available-byte count is not a measured safe allocation budget.

Both reviewed repositories have MIT root licenses; individual bundled code, model artifacts and evaluation data retain their own terms. Pin dependencies and review their applicable licenses before reuse. The research workspace does not redistribute model weights.

## Together Compiler is the loop reference

[Together's technical article](https://www.together.ai/blog/together-compiler-continual-compilation-for-ai-inference) describes agents optimizing code for a model, hardware and workload, using persistent engines, fast screening and fuller evaluation. The transferable idea is **make candidate experiments cheap enough to guide repeated search, then validate survivors under realistic conditions**. Our design supports reusable preparation/build artifacts, cheap compatibility/numerical checks and full-engine trials. Persistent-engine reuse or hot reload can reduce search overhead when a backend supports qualified state reset and loaded-identity tracking; clean restart remains an available path. The headline 252× is experiment throughput, not a promised inference gain.

No Together Compiler implementation was located in the previously investigated official article/paper/alphaXiv links and named public repositories. The current linked-page inspection does not change that result; it does not rule out private code or an unrelated repository name. See [evidence boundary](Evidence.md). Use its methodology, not an assumed source dependency.

Our mapping is: target brief/model/source/hardware → candidate engine or reusable CC → cheap compatibility and correctness checks → diagnostic run → paired full trials → standardized benchmark owner evaluation → evidence-backed next candidate. No agent may redefine acceptance to make its candidate pass.

## Practical engineering conclusion

We can design and implement the CC adapters and lab workflow with ordinary Python, native engine builds, Linux resource controls and a small protected worker. We cannot yet claim Muse will run at 40 GB or preserve standardized benchmark and latency targets. The largest unknown is the supported, correct Muse execution baseline, followed by unified-memory enforcement and the streaming speed/quality tradeoff.

Build reusable tool interfaces around real upstream surfaces. Use ordinary engine adapters and the existing lab boundary; add specialized trace decoders for supported backends. [Tools](Tools.md), [schema and communication](CC%20schema%20and%20lab%20communication.md), and [lab internals](Lab%20internals%20and%20telemetry.md) make that proposal concrete.
