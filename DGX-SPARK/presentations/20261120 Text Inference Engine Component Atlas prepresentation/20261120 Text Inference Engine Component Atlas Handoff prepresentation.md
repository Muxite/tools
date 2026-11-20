# 20261120 Text Inference Engine Component Atlas Handoff prepresentation

## Start here

Open the [current component atlas](<./20261120 Text Inference Engine Component Atlas prepresentation.html>). It is the team's reference for what an inference engine contains and which Capability Capsule (CC) builds or operates each part. The target is text generation on one DGX Spark where the checkpoint exceeds unified memory.

This edition builds on the 20261118 edition. It adds four CC kinds, four components from the 2026-11-20 analysis, tool and analysis CCs, and per-component measured evidence from the DeepSeek V4.1 Flash runs on DGX Spark GB10.

For a short walkthrough, open **All CCs** to see the four kinds, then **Engine → Measured evidence**, then **Engine → Component map → Weight residency → Expert weight cache**.

## What changed in this edition

**CC kinds (data and UI).** Every CC record has a `ccKind`: `builder`, `tool`, `analysis` or `factory`. The All CCs tab has a kind legend with counts, a kind filter, a badge on every card, and a table that maps atlas CC IDs to JiuwenSwarm capsule directories. CC pages and component pages show the kind badge.

**Renamed.** The factory worker **Image builder** is now **Image assembler**, because names ending in "builder" are reserved for Builder CCs. Its IDs do not change (`factory.image_builder`, legacy `factory.builder`, prior `factory.build_image_builder`). The old name is kept as `formerNames`, shown on its pages and found by catalog search. No other existing CC name broke the rules.

**New components, each with a Builder CC:**

| Component (ID) | Builder CC | Endpoint subcomponent | Scope |
|---|---|---|---|
| Quantized matmul kernel (`backend.quantized_matmul_kernel`) | Quantized matmul kernel builder | Tensor execution backend → Quantized matmul kernels | In scope |
| CPU weight repack (`backend.cpu_weight_repack`) | CPU weight repack builder | Tensor execution backend → CPU expert lane kernels and weight repack | Conditional |
| Engram row cache (`weights.engram_row_cache`) | Engram row cache builder | Weight residency → Engram row cache | Conditional |
| Host expert store (`engine.host_expert_store`) | Host expert store builder | Weight residency → Expert store and admission policy (host expert tier) | Conditional |

Each new entry records the llama.cpp status at 9048bad8 and Strata evidence at ffa80d73. Notes that matter: llama.cpp has no IQ2_XXS repack path in `repack.cpp`; llama.cpp reads Engram rows on demand (`--lazy-mode`, `lazy_read`) with no row cache; llama.cpp keeps host experts in the OS page cache only.

**Quantization.** The pack compiler's contract choices now include hotness-aware mixed precision: a routing profile gives hot experts more bits and cold experts fewer. The "New quantization format" scenario lists the new builders and the tool and analysis CCs. Strata quantization sources are attached: `ds4_iq.cu` (GPU IQ kernels, IQ2_XXS block 66 B), `ds4_tq.cu`, `ds4_gguf.cu` (quantized matmul); `ds4_iq_cpu.cpp`, `ds4_mx_kern.inc` (CPU lane); `ds4_q6k.cuh`, `ds4_iq1m_codes.inc` (block decoder).

**Strata evidence on existing components.** Speculative decoder: `--dspark`, `--dspark-depth` and the DSpark drafter pack. Prefix state cache: ds4 conversation slots, restore points and `STRATA_DS4_REUSE`.

**Tool CCs (5):** Capped lab runner, Model quantizer, Pack converter, Native build runner, MoE cache size tuner.

**Analysis CCs (6):** Expert routing profile analysis, Request fault and I/O analysis, Quantized kernel profile analysis, Engine gap analysis, Expert copy replay analysis, Page residency analysis.

**Measured evidence.** Five components carry a status, one-line results and links to report copies. They appear on the component page, the builder CC page, the endpoint subcomponent card and **Engine → Measured evidence**:

| Component | Status | Main result | Report |
|---|---|---|---|
| Expert weight cache | Positive at 60 GiB (quiet) | Faster first token than same-budget stock A+ in all ten pairs per size: 27.08 s / 92.07 s saved at 512 / 2048 tokens; decode unchanged. 30 GiB iteration 1 negative; iteration 2 (direct seed, O_DIRECT) warm parity plus a cold-start win. | 60 GiB report-v3 |
| Weight placement planner | Small decode gain (screening) | +1.905 / +1.289 tok/s against pooled 30 GiB controls | pooled30 C2 |
| Runtime event recorder | Correct (functional) | 1,360 of 1,360 events, zero lost | C1 report-v3 |
| Expert demand predictor | Negative (screening) | 96 completed prefetches, none used | pooled30 C4 |
| Batch layout mapper | No effect beyond serving flags (screening) | With flags matched: +0.06 / +0.08 s TTFT, -1.96 / -1.91 tok/s | pooled30 C5 report-v2 |

The 60 GiB report-v3 appeared in the staging folder during this work and is used as the main 60 GiB result. The report-v2 screening figures (24.92 / 90.80 s) are kept as a superseded row. `final-headlines.json` is copied unchanged; its 60 GiB row is still the report-v2 figure, and the Measured evidence page says so.

**Evidence copies.** `evidence/` holds the reports, `final-headlines.json`, `STATUS.md`, `DECISIONS.md` and the pack conversion precedent (`convert_ds41_upstream.py`, `conversion.log`). Links in the atlas are relative, so the folder stays self-contained.

**Sources convention.** Every new entry links to exact files: llama.cpp paths at 9048bad8 and Strata paths at ffa80d73 (`src/dsv41/`), with a symbol and line. Local evidence copies use relative `evidence/...` paths. Component pages show these under **Sources at the pins**.

## Alignment with the JiuwenSwarm demo UI (presentation update)

The atlas now matches the demo UI catalog (`factory/ccs/atlas-names.json`, branch `demo/cc-star-ui-20261120`, 63 capsule directories: 19 builder, 11 tool, 22 analysis, 11 factory worker).

- **Kind legend.** Labels and the one-line definitions are word for word the UI legend: Builder, Tool, Analysis, Factory worker (`kinds.*.plain` in `edition.json`). Each legend entry shows atlas CCs and capsules per kind.
- **Capsules in the JiuwenSwarm catalog.** All CCs → a table of all 63 directories with title, kind, capsule directory and cc.yaml ID, what it builds or does, the related atlas component and the atlas CC when there is one (`capsuleCatalog`). Twelve directories carry an atlas CC; their titles and kinds are identical, which `build.py` and `verify_flip.py` check. The other 51 are listed, not added as full atlas CC entries.
- **Capsule claims.** Native build runner and Expert copy replay analysis no longer claim the `builder` and `routing_profile_analysis` directories, which the UI titles Image assembler and Expert routing profile analysis; their pages say where the job ships.
- **Spark campaign 2026-11-20.** Engine → Spark campaign 2026-11-20 (`#endpoint/campaign`, data in `campaign`): campaign counts from the factory stores (73 capped model launches, 28 factory homes, 87 planner decisions, 16 native build attempts, 538 observations, 5 starred builder CCs, 6 analysis CCs created), the five builder CCs C1 to C5 with what each built, build and verify, lab outcome and result label, the combined build D (null, screening), and the tool and analysis CCs that ran. The earlier Satay (Jetson) demo applied one engine CC; this campaign applied many on the target hardware.

Counts: 53 atlas CCs (36 builder, 5 tool, 6 analysis, 6 factory worker) and 63 capsule directories (19 builder, 11 tool, 22 analysis, 11 factory worker).

## CC kinds

Every CC is a packaged tool for agents: a method, helpers, tests, a verifier and pinned digests.

| Kind | Delivers | Name rule | Count |
|---|---|---|---|
| Builder CC | Code for a component or subcomponent | `<Component> builder` | 36 |
| Tool CC | A verified receipt or artifact from operating an existing tool or system | Named for the tool job, for example "Pack converter" | 5 |
| Analysis CC | Findings or a report from evidence such as traces, counters and profiles | `<Subject> analysis` | 6 |
| Factory worker CC | A factory artifact: brief, contract, work orders, source integration, image or verdict | Named for the factory job and its handoff | 6 |

Builder and factory CCs link to the component they deliver or invoke (`builds`, `factoryCapabilities`). Tool and analysis CCs link to the components they operate on or study (`operates`); they never appear as builders. `build.py` and `verify_flip.py` both check the name rules.

## Atlas CC IDs and capsule directories

The JiuwenSwarm capsule directories use component-style names; the atlas calls the same CCs "<Component> builder". Code was not renamed. IDs and digests come from the 2026-11-20 final snapshot (`final-snapshot/capsules`, `capsule-releases.json`).

| Atlas CC | Atlas ID | Capsule directory | cc.yaml ID | Version |
|---|---|---|---|---|
| Expert weight cache builder | `engine.build_expert_weight_cache` | `expert_weight_cache` | `engine.build_expert_weight_cache` | 1.4.1 |
| Weight placement planner builder | `placement.build_weight_placement_planner` | `weight_placement_planner` | `placement.build_weight_placement_planner` | 1.2.1 |
| Expert demand predictor builder | `routing.build_expert_demand_predictor` | `expert_demand_predictor` | `routing.build_expert_demand_predictor` | 1.2.1 |
| Batch layout mapper builder | `batch.build_batch_layout_builder` | `batch_layout_mapper` | `engine.build_batch_layout_mapper` | 1.1.4 |
| Runtime event recorder builder | `observability.build_runtime_event_recorder` | `observability_event_recorder` | `observability.build_runtime_event_recorder` | 1.1.4 |
| Image assembler (factory worker) | `factory.image_builder` | `builder` | `factory.builder` | 1.1.2 |
| Capped lab runner | `tool.capped_lab_runner` | `lab_client` | `factory.lab_client` | 1.2.4 |
| MoE cache size tuner | `tool.moe_cache_size_tuner` | `cache_size_pareto` | `analysis.cache_size_pareto` | 1.0.0 |
| Expert routing profile analysis | `analysis.expert_routing_profile` | `routing_profile_analysis` | `analysis.expert_routing_profile` | 1.3.0 |
| Request fault and I/O analysis | `analysis.request_fault_io` | `request_fault_io_analysis` | `analysis.request_fault_io` | 1.1.1 |
| Quantized kernel profile analysis | `analysis.quant_kernel_profile` | `quant_kernel_profile` | `analysis.quant_kernel_profile` | 1.0.0 |
| Engine gap analysis | `analysis.engine_gap` | `spark_gap_analysis` | `factory.spark_gap_analysis` | 1.8.2 |

Capsule IDs that differ from atlas IDs are registered as aliases, so `#cc/engine.build_batch_layout_mapper`, `#cc/factory.spark_gap_analysis` and `#cc/analysis.cache_size_pareto` open the right page. Notes: the `builder` capsule ("Native build job") carries the job shown as the Native build runner tool CC; Expert copy replay analysis ships inside `routing_profile_analysis` (copy timing); Page residency analysis, Model quantizer and Pack converter have no capsule directory yet.

## Counts

- **46 components:** 27 in-scope engine components, 9 conditional extensions, 6 factory capabilities and 4 host providers.
- **53 CCs:** 36 builder, 5 tool, 6 analysis and 6 factory worker CCs.
- **101 actions:** 76 engine and host actions and 25 factory actions (unchanged; the new components perform existing actions).
- **65 engine handoffs** (58 plus 7 for the new components) and **20 work orders** (unchanged). The new builders are not yet assigned to a work order.
- The endpoint map has 8 groups and 26 subcomponents covering 36 engine and extension IDs.

## Naming rules and decisions to carry forward

| Entity | Naming rule | Example |
|---|---|---|
| Builder CC | Name it by the component it delivers. Specify the requirement and the choices set by the contract. | **Expert router builder** delivers code for an **Expert router**. |
| Tool CC | Name it for the tool job. It returns a verified receipt or artifact, not engine code. | **Pack converter** returns converted shards and a per-tensor read-back receipt. |
| Analysis CC | Name it `<Subject> analysis`. Its verifier recomputes the findings from the same inputs. | **Expert copy replay analysis** turns replayed copies into a copy-time share of TTFT. |
| Factory worker CC | Name the factory job and its handoff. Do not end the name in "builder". | **Workflow orchestrator** dispatches agents with the required builders. |
| Engine component | Name the software responsibility. | **Host expert store** owns the RAM tier of whole experts and its admission policy. |
| Host provider | Name the external service and the interface the engine relies on. | The storage subsystem supplies checkpoint byte ranges. |

Keep **code or artifact delivered**, **behavior when used** and **acceptance evidence** separate. Label measured results as screening or quiet, quote numbers exactly as the report states them, and link the report copy in `evidence/`. Keep stable IDs; when renaming, add the old name to `renames` in `edition.json` (it becomes `formerNames`) and keep the old IDs as aliases.

## Edit, rebuild and verify

The authoring source is `src/` in this folder. `build.py` builds on the [November 17 source](<../20261117 Text Inference Engine Atlas prepresentation/src>) (a sibling folder in this repository) and its sibling standalone HTML, and takes the title from the folder name.

| Change | Authoritative files |
|---|---|
| Original 38 workers: names, deliverables, contract choices, consumers and evidence | `memory.json`, `runtime.json`, `factory.json`; IDs and component names in `components.txt` |
| Components added in this edition and their builders; tool and analysis CCs; kind definitions; renames; capsule map; measured evidence | `edition.json` |
| Endpoint subcomponents, llama.cpp and Strata source anchors, local evidence links | `endpoint-data.js` |
| Operating interfaces and host services | `*_interfaces.json`, including `host_interfaces.json` |
| Assignments, prerequisites and work-order receipts | `orders.json`, `engine_orders.py`, `order_handoffs.json` |
| Opening map, handoffs, guided traces and readiness gates | `assemblies.js`, `path_stages.js`, `guided.js`, `engine_review.js` |
| Catalog, kind badges, tool and analysis pages, measured and source blocks | `kinds.js`, `kinds.css` |
| Report copies | `evidence/` |

Run from PowerShell with Python, Node and Playwright available. The endpoint verifier also needs a llama.cpp checkout at the pin, given by the `LLAMA_CPP_PIN_DIR` environment variable (HEAD 9048bad8) and the Strata clone at `~/huawei/Strata` (commit ffa80d73 present).

```powershell
Set-Location 'DGX-SPARK/presentations/20261120 Text Inference Engine Component Atlas prepresentation/src'
python -B build.py
python -B verify_flip.py
python -B verify.py
python -B verify_endpoint.py '../20261120 Text Inference Engine Component Atlas prepresentation.html'
```

This edition was not copied to the Desktop or D:. If it is published later, copy the HTML together with the `evidence/` folder, or the evidence links will break.

## Verified state

On 2026-11-20 `verify_flip.py`, `verify.py` and `verify_endpoint.py` passed on the generated HTML. The browser checks covered all 53 CCs, 46 components, 101 actions, 65 handoffs and 20 work orders in both perspectives; kind filters, badges and name rules; tool and analysis pages; measured evidence and its local links; llama.cpp and Strata source anchors; the renamed worker; history, keyboard, mobile layout and offline rendering. The HTML SHA-256 is recorded in the final report of this edition's session.

## Open items

- The new builders have no work order yet. Adding one requires a new job in the original construction data.
- Quantized kernel profile analysis has a static inventory only; the runtime share of quantized matmul and dequantization is unmeasured.
- Model quantizer, Pack converter and Page residency analysis have no capsule directory yet.
- A qualifying run for the Muse Spark Open target remains open.
