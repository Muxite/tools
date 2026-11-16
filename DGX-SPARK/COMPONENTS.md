# Component and capability map

The factory improves an inference engine using tools, reusable implementation components and methods. The entries below are derived from the captured declarations, not a claim that every package is integrated or qualified. Historical39-package counts refer to an earlier snapshot.

## Responsibility map

| Area | Packages / source | Current role |
|---|---|---|
| Decisions and execution | branch_workbench, engine_factory_loop, Store/taskgraph/controller/supervisor | Evidence-bound choices, durable budgets, branch-to-cycle lineage and recovery |
| Construction | builder, engine_component, integration_skill, engine_inspector | Apply identified changes, prepare dependencies, build and inspect actual configuration |
| Lab and evidence | lab_client, lab_lifecycle, inference_lab, standard_benchmark, evidence, evidence_digest_lab | Bounded execution, admission/cleanup, raw result ingestion and efficient scoped reads |
| Strata configuration/components | expert_streaming, strata_fixed_placement, strata_prefill_chunk, strata_verified_drafting | Streaming/placement/prefill/drafting material; each has separate source and correctness obligations |
| Diagnostics | deep_profile, numerical_investigation_lab, expert_prediction | Trace design, same-history numerical analysis and offline prediction evaluation |
| Research alternatives | expert_cache_lab, heterogeneous_placement_lab, gpu_kernel_lab, memory_residency_lab, precision_lab, kv_reuse_lab, serving_scheduler_lab, ssd_streaming_lab | Research/component jobs; a synthetic or subsystem win is not an integrated engine gain |
| Experimental methods and factory cost | methodology_* packages, cc_workflow_lab, native_inventory_once, cc_qualification | Hypotheses, diagnosis, ablation, followup, scoped verification and reusable workflow cost checks |

The expert-streaming package includes expert_fill, expert_pregate, mmap_advice, router_prefetch, thread_names, expert_readiness, inflight_join and phase_stats materials. Read its SOURCE-MAP, integration and evidence records before selecting one. Jetson CPU-expert behavior and the Spark fixed-placement engine are different deployments.

## Exact package inventory

| Package | Version | Scope | Callable capabilities |
|---|---|---|---|
| [factory.branch_workbench](reference/factory-source/jiuwenswarm/factory/ccs/branch_workbench/cc.yaml) | 1.1.0 | top-level | create, fork, refine, record, prune, status, ready, compare, attach |
| [factory.builder](reference/factory-source/jiuwenswarm/factory/ccs/builder/cc.yaml) | 1.1.0 | top-level | submit, status, cancel, result |
| [factory.cc_qualification](reference/factory-source/jiuwenswarm/factory/ccs/cc_qualification/cc.yaml) | 1.1.0 | top-level | inspect_package, verify_unit, assess_admission |
| [factory.cc_workflow_lab](reference/factory-source/jiuwenswarm/factory/ccs/cc_workflow_lab/cc.yaml) | 1.0.0 | top-level | analyze_receipts, design_workflow, benchmark_fixture, run_batch |
| [factory.deep_profile](reference/factory-source/jiuwenswarm/factory/ccs/deep_profile/cc.yaml) | 1.0.0 | top-level | plan, analyze |
| [factory.engine_component](reference/factory-source/jiuwenswarm/factory/ccs/engine_component/cc.yaml) | 1.0.0 | top-level | material-only |
| [factory.engine_factory_loop](reference/factory-source/jiuwenswarm/factory/ccs/engine_factory_loop/cc.yaml) | 1.1.0 | top-level | status, select, execute, collect, abandon, stop |
| [factory.engine_inspector](reference/factory-source/jiuwenswarm/factory/ccs/engine_inspector/cc.yaml) | 1.1.0 | top-level | inspect, preflight, verify_effective_config, inspect_strata |
| [factory.evidence](reference/factory-source/jiuwenswarm/factory/ccs/evidence/cc.yaml) | 1.1.0 | top-level | plan_get, plan_patch, query, read, publish |
| [factory.evidence_digest_lab](reference/factory-source/jiuwenswarm/factory/ccs/evidence_digest_lab/cc.yaml) | 1.0.0 | top-level | index, project |
| [engine.expert_cache_lab](reference/factory-source/jiuwenswarm/factory/ccs/expert_cache_lab/cc.yaml) | 1.0.0 | top-level | validate, replay, predict |
| [factory.expert_prediction](reference/factory-source/jiuwenswarm/factory/ccs/expert_prediction/cc.yaml) | 1.0.0 | top-level | evaluate |
| [engine.expert_streaming](reference/factory-source/jiuwenswarm/factory/ccs/expert_streaming/cc.yaml) | 2.1.0 | top-level | applicability, engagement, evidence_query, evidence_read, evidence_publish, inspect, inspect_strata, preflight, verify_effective_config, build_submit, build_status, build_cancel, build_result, lab_submit, lab_status, lab_cancel, lab_result, lab_ab_submit, lab_ab_status, lab_ab_result |
| [factory.components.expert_fill](reference/factory-source/jiuwenswarm/factory/ccs/expert_streaming/components/expert_fill/cc.yaml) | 1.1.0 | nested component | material-only |
| [factory.components.expert_pregate](reference/factory-source/jiuwenswarm/factory/ccs/expert_streaming/components/expert_pregate/cc.yaml) | 1.1.0 | nested component | material-only |
| [factory.components.expert_readiness](reference/factory-source/jiuwenswarm/factory/ccs/expert_streaming/components/expert_readiness/cc.yaml) | 1.0.0 | nested component | material-only |
| [factory.components.inflight_join](reference/factory-source/jiuwenswarm/factory/ccs/expert_streaming/components/inflight_join/cc.yaml) | 1.0.0 | nested component | material-only |
| [factory.components.mmap_advice](reference/factory-source/jiuwenswarm/factory/ccs/expert_streaming/components/mmap_advice/cc.yaml) | 1.1.0 | nested component | material-only |
| [factory.components.phase_stats](reference/factory-source/jiuwenswarm/factory/ccs/expert_streaming/components/phase_stats/cc.yaml) | 1.0.0 | nested component | material-only |
| [factory.components.router_prefetch](reference/factory-source/jiuwenswarm/factory/ccs/expert_streaming/components/router_prefetch/cc.yaml) | 1.1.0 | nested component | material-only |
| [factory.components.thread_names](reference/factory-source/jiuwenswarm/factory/ccs/expert_streaming/components/thread_names/cc.yaml) | 1.1.0 | nested component | material-only |
| [engine.gpu_kernel_lab](reference/factory-source/jiuwenswarm/factory/ccs/gpu_kernel_lab/cc.yaml) | 1.0.0 | top-level | evaluate, benchmark |
| [engine.heterogeneous_placement_lab](reference/factory-source/jiuwenswarm/factory/ccs/heterogeneous_placement_lab/cc.yaml) | 1.0.0 | top-level | plan, execute_reference, overlap_schedule |
| [factory.inference_lab](reference/factory-source/jiuwenswarm/factory/ccs/inference_lab/cc.yaml) | 1.2.1 | top-level | inspect_evidence, diagnose, ablation, followup, cache_protocol, propose, profile_plan, analyze_profile, evaluate_prediction, test_scope, query, read, publish, apply_prefill, apply_drafting, status, select, execute, collect, stop, qualify_prefill, lab_submit, lab_status, lab_result, lab_cancel |
| [factory.integration_skill](reference/factory-source/jiuwenswarm/factory/ccs/integration_skill/cc.yaml) | 1.1.0 | top-level | evidence_query, evidence_read, evidence_publish, inspect, inspect_strata, preflight, verify_effective_config, build_submit, build_status, build_cancel, build_result, lab_submit, lab_status, lab_cancel, lab_result, lab_ab_submit, lab_ab_status, lab_ab_result |
| [engine.kv_reuse_lab](reference/factory-source/jiuwenswarm/factory/ccs/kv_reuse_lab/cc.yaml) | 1.0.0 | top-level | prefix, allocator, estimate, verify |
| [factory.lab_client](reference/factory-source/jiuwenswarm/factory/ccs/lab_client/cc.yaml) | 1.1.0 | top-level | submit, status, cancel, result, ab_submit, ab_status, ab_result |
| [factory.lab_lifecycle](reference/factory-source/jiuwenswarm/factory/ccs/lab_lifecycle/cc.yaml) | 1.0.0 | top-level | status, recover |
| [engine.memory_residency_lab](reference/factory-source/jiuwenswarm/factory/ccs/memory_residency_lab/cc.yaml) | 1.0.0 | top-level | plan, verify, native_experiment |
| [factory.methodology_ab](reference/factory-source/jiuwenswarm/factory/ccs/methodology_ab/cc.yaml) | 1.0.0 | top-level | material-only |
| [factory.methodology_ablation](reference/factory-source/jiuwenswarm/factory/ccs/methodology_ablation/cc.yaml) | 1.0.0 | top-level | ablation |
| [factory.methodology_diagnosis](reference/factory-source/jiuwenswarm/factory/ccs/methodology_diagnosis/cc.yaml) | 1.0.0 | top-level | diagnose |
| [factory.methodology_followup](reference/factory-source/jiuwenswarm/factory/ccs/methodology_followup/cc.yaml) | 1.0.0 | top-level | followup |
| [factory.methodology_hypothesis](reference/factory-source/jiuwenswarm/factory/ccs/methodology_hypothesis/cc.yaml) | 1.0.0 | top-level | propose |
| [factory.methodology_out_of_core](reference/factory-source/jiuwenswarm/factory/ccs/methodology_out_of_core/cc.yaml) | 1.0.0 | top-level | cache_protocol |
| [factory.methodology_transfer_lab](reference/factory-source/jiuwenswarm/factory/ccs/methodology_transfer_lab/cc.yaml) | 0.1.0 | top-level | assess_transfer, design_trial, analyze_abba |
| [factory.native_inventory_once](reference/factory-source/jiuwenswarm/factory/ccs/native_inventory_once/cc.yaml) | 1.0.0 | top-level | material-only |
| [factory.numerical_investigation_lab](reference/factory-source/jiuwenswarm/factory/ccs/numerical_investigation_lab/cc.yaml) | 1.0.0 | top-level | replay_spec, compare_logits, first_divergence, capture_plan, import_capture |
| [engine.precision_lab](reference/factory-source/jiuwenswarm/factory/ccs/precision_lab/cc.yaml) | 1.0.0 | top-level | quantize, evaluate, calibrate, memory_plan |
| [engine.serving_scheduler_lab](reference/factory-source/jiuwenswarm/factory/ccs/serving_scheduler_lab/cc.yaml) | 1.0.0 | top-level | schedule, analyze, compare, verify |
| [engine.ssd_streaming_lab](reference/factory-source/jiuwenswarm/factory/ccs/ssd_streaming_lab/cc.yaml) | 1.0.0 | top-level | plan, evaluate, read_fixture |
| [factory.standard_benchmark](reference/factory-source/jiuwenswarm/factory/ccs/standard_benchmark/cc.yaml) | 1.0.0 | top-level | submit, status, result |
| [engine.strata_budget_workbench](reference/factory-source/jiuwenswarm/factory/ccs/strata_budget_workbench/cc.yaml) | 1.0.0 | top-level | apply, verify_startup, summarize_memory |
| [engine.strata_fixed_placement](reference/factory-source/jiuwenswarm/factory/ccs/strata_fixed_placement/cc.yaml) | 1.0.0 | top-level | material-only |
| [engine.strata_prefill_chunk](reference/factory-source/jiuwenswarm/factory/ccs/strata_prefill_chunk/cc.yaml) | 1.3.0 | top-level | apply, coverage |
| [engine.strata_prefill_workbench](reference/factory-source/jiuwenswarm/factory/ccs/strata_prefill_workbench/cc.yaml) | 1.1.0 | top-level | inspect, design, apply, verify_profile, submit, status, result, query, read, publish, diagnose, ablation, followup, test_scope, qualify_profile, loop_status, select, execute, collect, stop |
| [engine.strata_throughput_workbench](reference/factory-source/jiuwenswarm/factory/ccs/strata_throughput_workbench/cc.yaml) | 1.1.1 | top-level | inspect_evidence, inspect, design, apply, verify_profile, query, read, publish, diagnose, ablation, followup, test_scope, loop_status, select, execute, collect, stop, propose |
| [engine.strata_verified_drafting](reference/factory-source/jiuwenswarm/factory/ccs/strata_verified_drafting/cc.yaml) | 1.0.0 | top-level | apply |

Full material paths are in [COMPONENTS.json](COMPONENTS.json). The package declarations remain the source of interface detail. The top-level inventory includes the newer numerical investigation package; counts are discovery information, not the objective.
