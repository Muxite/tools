---
id: capsule-reference-review-batch-2026-10-21
status: reviewed
source: AI4Research-Development/jiuwenswarm-m1@98bd9d913f9ddae5f0d6a3ae256bff10f25ee743; captured latest remote d3d7f565c6c05ccf764fe0780fde149b7dc89b95
last_reviewed: 2026-10-21
next_action: Recompute the source manifest against the exact code checkout used by any future adapter or run.
---
# Capsule reference source review batch

This batch records a read-only source inspection for [[Designs/CC Reference]] and [[Experiments/CC Accuracy Study]]. Inspected candidate was clean at `98bd9d913f9ddae5f0d6a3ae256bff10f25ee743` (`ai4r_M1`). The parent task also captured latest remote `d3d7f565c6c05ccf764fe0780fde149b7dc89b95` in a separate review worktree; capsule, native, and check files cited in these references were compared and unchanged. This is a bounded file comparison, not full repository equivalence or a product acceptance claim.

## Coverage

Reviewed implementation roles: compiler host and Intent, Requirements, Planner, semantic Verifier, Search, Screening, Hypothesis, Builder, Benchmark, Scientific Evaluation, Delivery; also the capsule registration assets, shared serializer, bridge, library, binder, runner, protected checks and gate. Reviewed declaration catalog and compiler/planner prompts. Checked test inventory for the compiler, planner/native, verifier/gate, screening, search, science, Builder, Benchmark, Delivery, and stage checks. No tests were run in this documentation review; no model call, live retrieval, Builder execution, or benchmark occurred.

The code has one fixed host Intention Compiler node containing two distinct capsules, Intent then Requirements. The Planner is an optional planned-path capsule; static authored plan is also supported. The Verifier is a separate reviewer role, not a producer stage. Benchmark is model-free host orchestration. These distinctions are reflected in the detailed pages and are not fabricated into additional CCs.

Known evidence limits: source declarations and passing local tests (where tests are later run) cannot prove live adapter fidelity, accepted runtime, effective model route, actual cost, semantic accuracy, or deployment isolation. The current study adapter remains pending audit. The semantic reviewer must see declaration and exact output only. Held-out materials and outcomes are not present in this vault.

## File SHA-256 manifest

Paths below are relative to `AI4Research-Development/jiuwenswarm-m1` at the candidate commit. Values are SHA-256 over exact file bytes. Recompute before relying on this inventory after checkout changes.

| Source | SHA-256 |
|---|---|
| `jiuwenswarm/research/compiler.py` | `e126ec140c3f9c9f721197950c5d84f7a322f2e733ba852bcd067e1fb7039482` |
| `jiuwenswarm/research/native.py` | `9757e216631d0042b9b666c53df3e7fac52d394f935cca263644e03f63e832cb` |
| `jiuwenswarm/research/gate.py` | `9a3ead19679d170fda062c394591b579c38916f8186c02af935852fecc8a039a` |
| `jiuwenswarm/research/library.py` | `5969fe2626a21bde00b6a6812244bf4c82126e099194464534988e7978531182` |
| `jiuwenswarm/research/binding.py` | `01b088f6b2aba477c59618f439d2851e0c5224c59777e88c4ba4ac0f880f72db` |
| `jiuwenswarm/research/planning.py` | `4248c206d268db7bd6d8a69ae30147cb82be22105269192a03b99ef6dec91f4f` |
| `jiuwenswarm/research/runner.py` | `affcb51f2c9830b146afafa3321ad35159b56d6bcfe57840f7c5604b564c3998` |
| `jiuwenswarm/research/bridge.py` | `173c65511ea0fa220c974d4160dab02dbe3dafcb9a37fe618e592d7d974a5ae3` |
| `jiuwenswarm/research/capsules/intent.py` | `b435b3768f7b8f8b2eff020646dfc6a18860838ed52ff424ba05db15e9fde4aa` |
| `jiuwenswarm/research/capsules/requirements.py` | `8246a365226b6428879e2eee18ec0d051414d231dd8263e21b662cead46fa324` |
| `jiuwenswarm/research/capsules/planner.py` | `dc42c5acc321cdd40fca8b1c41525c1e2aaf34f56874e05ab3662d93cf30996e` |
| `jiuwenswarm/research/capsules/search.py` | `1147867b79850e932424e9d73ca3570513e8f07d9f448bab3e60e6d61fae9ac4` |
| `jiuwenswarm/research/capsules/screening.py` | `88f77276cd790d195c30c98b9292b674d6894d2a24d7701218de558cca68a76f` |
| `jiuwenswarm/research/capsules/hypothesis.py` | `b49477b5af030596beee117c031d7ef5de5cf973c3ce28cb8a91d8084f1fa19f` |
| `jiuwenswarm/research/capsules/builder.py` | `6f22f84c73b4241e0354fdf79fea4512cd7f59f7871c46340f9875a3e19bb9c9` |
| `jiuwenswarm/research/capsules/benchmark.py` | `7c73ca66ab3e8d5574b2e265556aee5e3b5c003ad2eb76de1f66e8146070500c` |
| `jiuwenswarm/research/capsules/evaluation.py` | `81d52afaec25360212914b248402488fb0ddb8af0a12437ba31f451f96ba9ff4` |
| `jiuwenswarm/research/capsules/delivery.py` | `aba1a429086aedd283a0e9e3168f41abfaa95da4d536dafb00c83a8cdcfa3b81` |
| `jiuwenswarm/research/capsules/assets.py` | `d3658775d5b9a1ae00d9157ca9be6f4c69d5252d37b35324c5655b16179b2598` |
| `jiuwenswarm/research/capsules/_common.py` | `c9762ca9f85258b520c4185654ef691997a1830787212f04b0f54b8a725238fa` |
| `jiuwenswarm/research/checks/compiler.py` | `cad4a123f43b98ea9b9e4f5aa57e89d78edcaffad5033f47f60e9843a13d5d98` |
| `jiuwenswarm/research/checks/verifier.py` | `680f93e57f97fe080b28ae4deb12e67a1017526747ad62ce92dfb420c0ea019b` |
| `jiuwenswarm/research/checks/research.py` | `e8ff02ca977c5ba8b063de610d9de3f110320f56980983e880a491fd3ab28aac` |
| `jiuwenswarm/research/checks/stages.py` | `7ca492f74e6d3665d66b5d0afe1113ec48947bd55e1477fe43bbdf42546d7285` |
| `jiuwenswarm/research_assets/catalog.json` | `298025fd375d5af3bf411116073d56d9f8648dd45e6b27673a384dc75fef8e50` |
| `jiuwenswarm/research_assets/compiler/intent.txt` | `b6405d7e05f52be3887d620c8eb8056c4977a1f520ee6d5db5f31db2bb0a18e9` |
| `jiuwenswarm/research_assets/compiler/requirements.txt` | `0016eb120f9f4133f16a90915026103ca312bdc58c08f5a155efb5a1dbc76f4` |
| `jiuwenswarm/research_assets/compiler/verifier.txt` | `89018d720c6ce3dffdcd4da1da6af0af39e1e45ee951e4f8bb12b9095d0251c8` |
| `jiuwenswarm/research_assets/planner/planner.txt` | `f65422fa2fbfbfc2976e46d3060acb0c2661742f53890d2b596f53060243ad5` |
| `tests/integration/research/test_native_runtime.py` | `1ec370207363d46340574ca7b4dc9e156da09ef64b16793d55a441c8d1d1c9d1` |
| `tests/unit_tests/research/test_plan_validation.py` | `b708b6bb3647462851033a54689d3c56270570f62c3ab3b57be63e06f14220a2` |

Declaration content hashes are independently pinned in the catalog: Intent `cfad31534c5abd2ae3620323f4e8c91a2ace4fe22d8544a447343ff5b783c32f`; Requirements `4b297be4dbf5b7bb052a9440728f5b60b42d1da188973e60cd8f8eaf7edf756b`; Verifier `e16e59a51f93751116bf1a210ff6188a87c3e8b396335a603896d9e0177c5e66`; Planner `460e6ce34e47048ec1c57a75326ffc001664ae127714df8722f78262efe40358`. These are catalog declaration pins, not inferred runtime hashes.

## Specific evidence references

- Intent/Requirements orchestration and unaccepted-output handling: `jiuwenswarm/research/compiler.py`; focused unit tests `tests/unit_tests/research/test_compiler.py` and `test_compiler_registration.py`.
- Planner one-shot native dispatch: `jiuwenswarm/research/native.py`; integration `tests/integration/research/test_planner_native.py`; structural tests `test_plan_validation.py`, `test_planning.py`, and `test_binding.py`.
- Search/scoring/experimental stages: `tests/unit_tests/research/test_search.py`, `test_search_connectors.py`, `test_search_scope_binding.py`, `test_screening.py`, `test_ranking_helper.py`, `test_science.py`, `test_stage_checks.py`.
- Build, benchmark and report: `test_builder.py`, `test_builder_launcher.py`, `test_empirical_results.py`, `test_delivery.py`, `test_delivery_content.py`, plus executor/provisioning integration tests.
- Review and gate: `test_gate.py`, verifier predicate coverage in `test_compiler_registration.py`, runner and integration gate tests.

Tests were inspected by path, not executed in this batch. Consult the maintained M1 package for current contract detail and the exact source commit for implementation; this batch is a traceability index, not a second code authority.
