---
type: review
status: draft
tags: [review, packet]
---

# Bounded review packet

Bounded planner-to-freeze pilot; complete journey review is outside this packet

Baseline: `b9979ca38f982b757505300c02f4108724a07629`. Packet: `planner-v2.json`.

## Scope confirmation

Confirm affected owners, consumers, Gates, records, diagrams and fixtures before reviewing.
Unselected changes are inventory only. Report missing impact as a finding; do not certify this batch.

## Inputs

- `docs/architecture/capsule/toolchain.md` (impact), SHA-256 `6a3517032d5c9588d8d6b5e34dd0b8361c77e33c618fadf6b9b89dd2d385d725`
- `docs/architecture/contracts/services-v1.schema.json` (impact), SHA-256 `178c2b0cad15fb0601315060624d3749897531996b8c328f973c41bbf9a953f7`
- `docs/architecture/system/planner.md` (owner), SHA-256 `08637ec88ce737d7995a014c7fd1658ea979ee1e566995bdd9aee1d34800aef9`
- `docs/architecture/system/records.md` (impact), SHA-256 `8c04ef1200d86e06cf4e70d34a4af0ae008c9fdd18d521fc9a0a0dc0520647c3`
- `docs/product/SOURCE_FREEZE.md` (source-baseline), SHA-256 `b37b2d3f19989df7857d18197d193963559cfcbc1ca512ba6f4155253f9b2879`
- `docs/product/source-freeze-2026-10-02.json` (source-baseline), SHA-256 `eec8da6ffbda2f4576178ca460375bd7af0337b3a20ef5c39dbddf49827d6cf9`

## Exact source excerpts

### docs/product/prd-m1-full-2026-10-02.txt L75–L136

```text
75: ### 1.3 M1 Phase Model
76: 
77: M1 is organized into three coordinated tracks.
78: 
79: #### Track 1 — Phase 1 Static Research Baseline
80: 
81: This is the release-critical live research workflow.
82: 
83: It uses:
84: 
85: * A fixed, sequential Swarmflow Default DAG.
86: * Explicitly assigned Capability Capsules.
87: * A static Codex CLI model route.
88: * A fixed-flow Requirement / Intention Compilation path.
89: * One selected opportunity and one hypothesis execution path.
90: * Evaluator Gate control between governed workflow stages.
91: * Explicit human intervention when blocking infrastructure failures occur.
92: 
93: This track establishes the stable end-to-end scientific research baseline.
94: 
95: #### Track 2 — Required Offline RSI Validation
96: 
97: M1 also requires a bounded RSI capability operating independently of the live Phase 1 workflow.
98: 
99: The RSI track must:
100: 
101: * Operate only in its approved offline sandbox.
102: * Demonstrate the required Target 1 capsule-level improvement path.
103: * Preserve capsule contracts and the independent referee.
104: * Keep hidden evaluation material isolated from the proposer and candidate.
105: * Pass the required adversarial security and guardrail tests.
106: * Require human-controlled admission and activation.
107: 
108: Completion of this isolated RSI track is part of the M1 Definition of Done, but RSI does not modify the live Phase 1 research workflow during M1.
109: 
110: #### Track 3 — Phase 2 Dynamic Test Tracks
111: 
112: Phase 2 contains isolated experiments such as:
113: 
114: * Dynamic intention compilation.
115: * Cluster Mode / Leader Agent planning.
116: * Dynamic capability discovery.
117: * Heterogeneous model routing.
118: * OpenJiuwen Code Mode.
119: * Other explicitly approved dynamic behaviors.
120: 
121: **External Model Access Gate:** Non-Codex model-routing work remains isolated from the Phase 1 production path. Before the required model/API access is approved, Phase 2 model-routing work may proceed using interface design, registry/configuration work, candidate analysis, and mocked endpoints only. After access is approved, explicitly approved real-model integrations may be exercised within the isolated development/evaluation track, but they do not replace or modify the active Phase 1 Codex baseline without a separate product and architecture decision.
122: 
123: Phase 2 experiments are non-blocking with respect to M1 release acceptance unless explicitly promoted through a revised product and architecture decision.
124: 
125: 
126: ### 1.4 Core Product Invariants
127: 
128: The following invariants apply across M1.
129: 
130: #### Gate-Locked Advancement
131: 
132: No governed downstream workflow node may begin solely because the producing agent claims success.
133: 
134: An advancing Evaluator Gate decision must be durably recorded before downstream execution is released.
135: 
136: #### Contract-Bound Execution
```

## Review output

Use the roles and finding format in review-workflow.md. Cite evidence, not agreement.

## Selected diff

````diff
diff --git a/docs/architecture/capsule/toolchain.md b/docs/architecture/capsule/toolchain.md
index 1016d538e..848074bd1 100644
--- a/docs/architecture/capsule/toolchain.md
+++ b/docs/architecture/capsule/toolchain.md
@@ -192,13 +192,13 @@ In the order the [library](library.md#admission-the-only-way-in) gives:
 
 ## M03 Freeze: the Binding writer
 
-Freeze turns a [`run_plan`](../types/run-plan.md) into one Binding per step, before the run starts.
+Freeze consumes only the normalized [`run_plan`](../types/run-plan.md) identified by a committed VALID result from [planner validation](../system/planner.md#proposal-envelope-and-reference-semantics), then creates one Binding per step before dispatch. Production bootstraps from committed intake and its exact fixed-template envelope with no model turn or invented Brief; isolated planning validates the complete Brief-based proposal. Resolve exact snapshot/policy/config pins again and refuse changed/revoked dependencies. ExecutionProfile direct-call limits cover every reachable work/verifier/dependency hash before publication.
 
 ```python
-async def freeze(run_id: str, plan: dict, *, policy_ref: dict, vocabulary_ref: dict) -> dict[str, Ref]   # step_id -> Binding
+async def freeze(run_id: str, validation_ref: dict, *, policy_ref: dict, vocabulary_ref: dict) -> dict[str, Ref]   # step_id -> Binding
 ```
 
-`plan` is a `run_plan` value. For each step, freeze:
+Resolve validation_ref to the committed services-v1 plan_validation control Artifact, require VALID with zero findings, and resolve its validated_plan_ref to the normalized run_plan. Cross-check proposal, task, snapshot, config, policy and run identity against launcher-committed intake/config/library/provenance for production, or planning_reserved for the isolated experiment. Production does not fabricate a planning reservation. A naked plan dictionary, model assertion or wrong-run validation never authorizes freeze. The resolved `plan` is a run_plan value. For each step, freeze:
 
 1. resolves `capsule_name` and `gate_capsule_name` only through the immutable library snapshot whose hash is run_plan.library_snapshot_sha256, obtaining its exact decl_hash and Verdict. The launcher snapshots active aliases before validation. A planner's validated snapshot and freeze must match; freeze never substitutes a newly activated alias. Missing entries/pin mismatches refuse. Current revocation/security state may deny a snapshot version but cannot choose replacement code;
 2. re-hashes both pinned capsules' code and transitive needs.external closure from that snapshot/store (CARRIER_CHANGED), and refuses every dependency not admitted at snapshot creation or subsequently revoked (OPERATOR_NOT_ADMITTED); cycles, missing pins and snapshot mutation refuse freeze;
@@ -256,11 +256,11 @@ async def launch(prompt: str, channel: str, workspace: Path) -> str     # the ru
 `workspace` is the user's workspace folder; the input folder is `<workspace>/input/` (PRD 3.1.2). The run is bound to the local single-user profile, whose data dir is `get_user_workspace_dir()` (PRD 3.1.3; [integration](../system/integration.md#kv-the-record-stores-backing)). In this order:
 
 1. **Qualify** (PRD 3.1.5). If the prompt is blank or the input folder is unreadable, reject with exit 2 before minting run_id. Load and validate a pinned config snapshot and run doctor. Unavailable environment/security returns exit 4; do not begin an unprotected run.
-2. **Mint** the `run_id`. Resolve `P` and `V` from `config.yaml`'s `cc.policy_epoch` and `cc.vocabulary_sha256` ([M00c](#m00c-policy-publisher)). Resolve the immutable library snapshot and set PLAN.library_snapshot_sha256 to that exact hash. The fixed M1 plan template in `cc/launcher/plans/m1.json` must equal [the M1 pipeline](../m1/pipeline.md)'s wiring; validate this concrete snapshot-bound plan before freeze.
-3. `plan_ref = record_input(run_id, "run_plan", vocabulary_ref=V, value=PLAN, origin="control")`.
+2. **Mint** the `run_id`. Resolve `P` and `V` from `config.yaml`'s `cc.policy_epoch` and `cc.vocabulary_sha256` ([M00c](#m00c-policy-publisher)). Resolve the immutable library snapshot and set PLAN.library_snapshot_sha256 to that exact hash. The fixed M1 plan template in `cc/launcher/plans/m1.json` must equal [the M1 pipeline](../m1/pipeline.md)'s wiring; load its concrete snapshot-bound shape, with final validation after intake is committed.
+3. Prepare the fixed template and its provenance; no model planning or frozen Binding is needed yet.
 4. Build intake v2: classify supplied/configured local resources, bind immutable project_asset/validation_data snapshots, and extract text only from reference_document. Documents are added in path order under the fixed limits; excluded references are recorded in skipped. Then record_input stores the canonical intake and its source_text prompt projection, with exact source/hash/offset basis owned by [source_text](../types/source-text.md). Ordinary extraction/hint helpers create these inputs; no compile_intent capsule runs. Resource readability and ids are checked; baseline/dataset suitability is a later blueprint gate obligation.
-5. Prepare config/library/source-manifest Artifact pins and intake/source_text references. No successor can start from an event alone.
-6. `bindings = freeze(run_id, PLAN, policy_ref=P, vocabulary_ref=V)`; freeze emits `cc.run.frozen`.
+5. Commit config/library/source-manifest control Artifact pins and intake/source_text references. The trusted launcher publishes the complete planner_proposal envelope with task_ref=intake_ref, exact fixed PLAN, catalogue selections, policy-bounded budget, empty objective_bindings and proposal_source_ref to fixed-template provenance. Invoke deterministic validate with that proposal reference and exact task/library/policy pins. The trusted host publishes normalized run_plan first, then its VALID result; invalid or failed publication ends launch before freeze. PLAN and plan_ref for subsequent execution refer only to that normalized committed plan. No successor can start from an event alone.
+6. `bindings = freeze(run_id, validation_ref, policy_ref=P, vocabulary_ref=V)`; freeze rereads validation authority and emits cc.run.frozen only after complete publication.
 7. Commit run_started with all frozen Binding/config/library/source references, then emit `cc.run.started`. Invoke `cc.adapters.swarmflow.start_run(run_id, args={run_id, plan: PLAN, pins, inputs: {intake: intake_ref, source_text: source_text_ref}})`, where `pins` maps each step to its frozen Binding ref. This supplies every required launcher port in the production plan; optional intent_ir hints may be added only when explicitly prepared and bound.
 8. When the script returns its envelopes, emit `cc.run.finished` with them. On `CcHalt`, call [`halt`](#m03h-halt-host).
 
diff --git a/docs/architecture/contracts/services-v1.schema.json b/docs/architecture/contracts/services-v1.schema.json
index 064cc2def..e955c42da 100644
--- a/docs/architecture/contracts/services-v1.schema.json
+++ b/docs/architecture/contracts/services-v1.schema.json
@@ -6,13 +6,29 @@
     "retry_profile": {
       "type": "object",
       "additionalProperties": false,
-      "required": ["version", "profile_id", "max_execution_retries", "duplicate_policy", "recovery"],
+      "required": [
+        "version",
+        "profile_id",
+        "max_execution_retries",
+        "duplicate_policy",
+        "recovery"
+      ],
       "properties": {
-        "version": {"const": 1},
-        "profile_id": {"$ref": "#/$defs/id"},
-        "max_execution_retries": {"const": 0},
-        "duplicate_policy": {"const": "reuse_reserved_result"},
-        "recovery": {"const": "explicit_review"}
+        "version": {
+          "const": 1
+        },
+        "profile_id": {
+          "$ref": "#/$defs/id"
+        },
+        "max_execution_retries": {
+          "const": 0
+        },
+        "duplicate_policy": {
+          "const": "reuse_reserved_result"
+        },
+        "recovery": {
+          "const": "explicit_review"
+        }
       }
     },
     "id": {
@@ -193,7 +209,7 @@
         "selections",
         "objective_bindings",
         "budget",
-        "model_response_ref"
+        "proposal_source_ref"
       ],
       "properties": {
         "version": {
@@ -223,7 +239,7 @@
         },
         "objective_bindings": {
           "type": "array",
-          "minItems": 1,
+          "minItems": 0,
           "items": {
             "$ref": "#/$defs/objective_binding"
           }
@@ -246,13 +262,36 @@
             }
           }
         },
-        "model_response_ref": {
-          "$ref": "#/$defs/ref"
-        },
         "ext": {
           "$ref": "#/$defs/ext"
+        },
+        "proposal_source_ref": {
+          "$ref": "#/$defs/ref",
+          "description": "Committed captured model response for isolated proposal, or deterministic fixed-plan provenance for production; never fabricated model evidence."
         }
-      }
+      },
+      "allOf": [
+        {
+          "if": {
+            "properties": {
+              "plan": {
+                "properties": {
+                  "track": {
+                    "const": "isolated_experiment"
+                  }
+                }
+              }
+            }
+          },
+          "then": {
+            "properties": {
+              "objective_bindings": {
+                "minItems": 1
+              }
+            }
+          }
+        }
+      ]
     },
     "validation_request": {
       "type": "object",
@@ -1933,6 +1972,26 @@
               "maximum": 3
             }
           }
+        },
+        {
+          "type": "object",
+          "additionalProperties": false,
+          "required": [
+            "kind",
+            "run_id",
+            "planning_request_id"
+          ],
+          "properties": {
+            "kind": {
+              "const": "planning"
+            },
+            "run_id": {
+              "$ref": "#/$defs/id"
+            },
+            "planning_request_id": {
+              "$ref": "#/$defs/id"
+            }
+          }
         }
       ]
     },
@@ -2229,6 +2288,33 @@
               }
             }
           }
+        },
+        {
+          "if": {
+            "properties": {
+              "scope": {
+                "properties": {
+                  "kind": {
+                    "const": "planning"
+                  }
+                }
+              },
+              "operation": {
+                "const": "turn"
+              }
+            }
+          },
+          "then": {
+            "properties": {
+              "prompt_content_ref": {
+                "properties": {
+                  "namespace": {
+                    "const": "public_artifact"
+                  }
+                }
+              }
+            }
+          }
         }
       ]
     },
@@ -2436,6 +2522,211 @@
               }
             }
           }
+        },
+        {
+          "if": {
+            "properties": {
+              "scope": {
+                "properties": {
+                  "kind": {
+                    "const": "planning"
+                  }
+                }
+              },
+              "state": {
+                "const": "complete"
+              }
+            }
+          },
+          "then": {
+            "properties": {
+              "reply_content_ref": {
+                "properties": {
+                  "namespace": {
+                    "const": "public_artifact"
+                  }
+                }
+              }
+            }
+          }
+        }
+      ]
+    },
+    "model_call_limits": {
+      "type": "object",
+      "minProperties": 1,
+      "patternProperties": {
+        "^[a-f0-9]{64}$": {
+          "type": "integer",
+          "minimum": 0
+        }
+      },
+      "additionalProperties": false
+    },
+    "planning_reservation": {
+      "type": "object",
+      "additionalProperties": false,
+      "required": [
+        "planning_request_id",
+        "request_sha256",
+        "task_ref",
+        "library_snapshot_ref",
+        "experiment_config_ref",
+        "policy_ref",
+        "model_id",
+        "deadline",
+        "max_model_calls"
+      ],
+      "properties": {
+        "planning_request_id": {
+          "$ref": "#/$defs/id"
+        },
+        "request_sha256": {
+          "$ref": "#/$defs/hash"
+        },
+        "task_ref": {
+          "$ref": "#/$defs/ref"
+        },
+        "library_snapshot_ref": {
+          "$ref": "#/$defs/ref"
+        },
+        "experiment_config_ref": {
+          "$ref": "#/$defs/ref"
+        },
+        "policy_ref": {
+          "$ref": "#/$defs/ref"
+        },
+        "model_id": {
+          "type": "string",
+          "minLength": 1
+        },
+        "deadline": {
+          "type": "string",
+          "format": "date-time"
+        },
+        "max_model_calls": {
+          "type": "integer",
+          "minimum": 1
+        }
+      }
+    },
+    "model_call_reservation": {
+      "type": "object",
+      "additionalProperties": false,
+      "required": [
+        "request_id",
+        "request_sha256",
+        "scope",
+        "ordinal",
+        "obs_id",
+        "turn",
+        "model_id",
+        "config_sha256",
+        "budget_ref",
+        "ceiling"
+      ],
+      "properties": {
+        "request_id": {
+          "$ref": "#/$defs/id"
+        },
+        "request_sha256": {
+          "$ref": "#/$defs/hash"
+        },
+        "scope": {
+          "allOf": [
+            {
+              "$ref": "#/$defs/model_call_scope"
+            },
+            {
+              "properties": {
+                "kind": {
+                  "enum": [
+                    "planning",
+                    "run"
+                  ]
+                }
+              }
+            }
+          ]
+        },
+        "ordinal": {
+          "type": "integer",
+          "minimum": 1
+        },
+        "obs_id": {
+          "$ref": "#/$defs/id"
+        },
+        "turn": {
+          "type": "integer",
+          "minimum": 1
+        },
+        "decl_hash": {
+          "$ref": "#/$defs/hash"
+        },
+        "dispatch_ref": {
+          "$ref": "#/$defs/ref"
+        },
+        "planning_ref": {
+          "$ref": "#/$defs/ref"
+        },
+        "model_id": {
+          "type": "string",
+          "minLength": 1
+        },
+        "config_sha256": {
+          "$ref": "#/$defs/hash"
+        },
+        "budget_ref": {
+          "$ref": "#/$defs/ref"
+        },
+        "ceiling": {
+          "type": "integer",
+          "minimum": 0
+        }
+      },
+      "allOf": [
+        {
+          "if": {
+            "properties": {
+              "scope": {
+                "properties": {
+                  "kind": {
+                    "const": "run"
+                  }
+                }
+              }
+            }
+          },
+          "then": {
+            "required": [
+              "decl_hash",
+              "dispatch_ref"
+            ],
+            "not": {
+              "required": [
+                "planning_ref"
+              ]
+            }
+          },
+          "else": {
+            "required": [
+              "planning_ref"
+            ],
+            "not": {
+              "anyOf": [
+                {
+                  "required": [
+                    "decl_hash"
+                  ]
+                },
+                {
+                  "required": [
+                    "dispatch_ref"
+                  ]
+                }
+              ]
+            }
+          }
         }
       ]
     }
diff --git a/docs/architecture/system/planner.md b/docs/architecture/system/planner.md
index 31b1a5fe8..af56fb588 100644
--- a/docs/architecture/system/planner.md
+++ b/docs/architecture/system/planner.md
@@ -12,48 +12,106 @@ tags: [system, planner, isolated-experiment]
 
 # Isolated capability planner and deterministic plan validation
 
-PRD 3.2.4, 4.1.2 and 6.12 permit the native Cluster Mode Leader to discover admitted capabilities and plan in an isolated experiment. The planner is an orchestration service, not a capsule. Phase 1 supplies its fixed plan to the same validator and never invokes this model planner.
+PRD 6.12 permits the native Cluster Mode Leader and dynamic capability discovery in an isolated experiment; 4.1.2 supplies its admitted catalogue and pinning rules. PRD 3.2.4 supplies extracted constraints, not permission for dynamic production planning. The planner is an orchestration service, not a capsule. Phase 1 supplies its fixed plan to the same validator and never invokes this model planner.
 
 ## Placement and interface
 
 The sole public wire-shape owner is [services-v1 JSON Schema](../contracts/services-v1.schema.json): planner_request, planner_proposal, validation_request, plan_validation and error. API positional arguments below are shorthand for these closed request objects. Proposal/result references use the common id/hash encoding; their artifacts validate against the matching schema before publication.
 
-`cc/planning/service.py` owns planning; `cc/planning/validate.py` owns pure validation; `cc/adapters/leader.py` alone imports the native team types. Reuse `LeaderSpec` and `TeamAgentSpec.build` from agent-core `9e339019`, `openjiuwen/agent_teams/schema/blueprint.py`, and `is_team_plan_enabled` from `runtime/team_plan.py`. This reuses Leader identity/configuration, not unrestricted native delegation or native plan approval as CC authorization. The default planner model is `gpt-6.1-sol` through the protected model bridge. Model support is checked at startup; an unavailable configured model gives `MODEL_UNAVAILABLE`, with no silent substitution.
+`cc/planning/service.py` owns planning; `cc/planning/validate.py` owns pure validation; `cc/adapters/leader.py` alone imports the native team types. Reuse `LeaderSpec` and `TeamAgentSpec.build` from agent-core `9e339019`, `openjiuwen/agent_teams/schema/blueprint.py`, and `is_team_plan_enabled` from `runtime/team_plan.py`. This reuses Leader identity/configuration, not unrestricted native delegation or native plan approval as CC authorization. The default planner model is `gpt-6.1-sol` through the protected model bridge. Model support is checked before enabling that experiment; an unavailable configured model gives `MODEL_UNAVAILABLE`, with no silent substitution. A disabled planner's model check does not block fixed production readiness, whose own configured route has separate mandatory checks.
 
 The authoritative planning API is `propose(task_ref, library_snapshot_ref, experiment_config_ref, request_id) -> PlanProposalRef`. `task_ref` is an immutable validated `research_brief`; snapshot entries expose capability names, exact versions/hashes, ports, effects, limits and admitted status, without hidden fixtures or credentials. The proposal contains the canonical `run_plan`, pinned capability selections, an objective-to-output mapping, budget estimates, and references to the three inputs. These metadata accompany the plan in an immutable proposal artifact; they do not extend `run_plan` invisibly. [Environment](environment.md) owns `cc.planner` keys: model_id defaults gpt-6.1-sol, proposal_timeout_s 120, max_nodes 32, max_proposals_per_submission 1, and required prompt_sha256 when enabled. Policy bounds remain authoritative. A request is one model proposal; no automatic model retry or autonomous repair loop occurs.
 
 `validate(plan_ref, task_ref, library_snapshot_ref, policy_ref, request_id) -> PlanValidationRef` is independently callable and makes no model call. Its schema records exact input references, VALID/INVALID and structured findings. Only VALID includes a normalized immutable plan reference and has zero findings; INVALID requires findings and cannot carry a validated plan. Normalization canonicalizes bytes without rearranging nodes, adding capabilities or inventing bindings. Invalid references produce `INVALID_REFERENCE`; wrong type/version gives `TYPE_MISMATCH`; changed request bytes give `REQUEST_CONFLICT`. Proposal timeout/cancellation is terminal for that request. An identical duplicate returns existing proposal/current state; explicit resubmission uses a fresh request identity and preserved prior evidence.
 
+`validate.py` performs pure computation over resolved immutable values. Its trusted service host resolves authorized references and asks the supervisor to publish the normalized plan before a VALID result that references it. INVALID publishes only its findings/result. The API returns the committed result reference, never an in-memory authorization; the diagrams' validator-to-store edges mean this host operation, not filesystem permission for model output or pure validation code.
+
 ## Validation and dispatch authority
 
-Validate unique nodes, topological order/acyclicity, reachable terminal outputs, exact typed ports or an explicitly pinned adapter, availability of every launcher input, dependency closure, admitted versions, effect/permission bounds, maximum nodes, cumulative declared resource/time limits, and required Gate profiles. Every mandatory Brief objective must map to a declared final output and criterion reference. This checks structural coverage; it does not claim to prove scientific success. Mechanical helpers are launcher preparation or fixed work-capsule internals, not arbitrary planner nodes. The model cannot supply source code as a plan node.
+Validate unique nodes, topological order/acyclicity, reachable terminal outputs, exact typed ports or an explicitly pinned adapter, availability of every launcher input, dependency closure, admitted versions, effect/permission bounds, maximum nodes, cumulative declared resource/time limits, and required Gate profiles. In the isolated Brief-based planner contract, every mandatory requirement must map to a declared final output and criterion reference; the production intake-based bootstrap below verifies its exact fixed template instead. This checks structural coverage; it does not claim to prove scientific success. Mechanical helpers are launcher preparation or fixed work-capsule internals, not arbitrary planner nodes. The model cannot supply source code as a plan node.
+
+The supervisor accepts only a committed VALID result matching the exact proposal/input hashes, then freeze resolves and pins dependencies from that same snapshot, checking current revocation without substituting an alias. Neither model prose, native task approval, nor a stored proposal can release a node. After dispatch begins, the graph is immutable. A failed node follows normal halt/review; the planner receives no permission to rewrite a live plan.
+
+### Proposal envelope and reference semantics
+
+`validation_request.plan_ref` identifies the immutable `planner_proposal` Artifact, including its embedded `run_plan`, selections, objective bindings and budget. A bare `run_plan` is insufficient because it omits those validation inputs. `plan_validation.plan_ref` echoes that proposal reference; `validated_plan_ref` identifies the separately published, normalized `run_plan` Artifact. This distinction also applies to the fixed production plan: the trusted launcher creates its proposal envelope from the published fixed plan and catalogue without a model call. `proposal_source_ref` resolves either the captured experimental model response or the launcher's deterministic fixed-plan provenance Artifact. The latter records the published template hash and input pins and never pretends to be model evidence.
+
+There are two task entry contracts, selected by the immutable plan track. Experimental `propose` requires a validated Brief and nonempty mandatory-objective bindings. Production validates before the Requirement capsule exists, so its launcher-created envelope uses the committed `intake` as `task_ref`, contains empty `objective_bindings`, and must exactly match the published fixed-plan template apart from authorized pins. It validates structural wiring, profiles, dependencies and budgets before freeze; Requirement and later stage Gates establish source-grounded requirements and scientific acceptance during execution. The validator does not invent a pre-run Brief or claim early semantic coverage. An experimental envelope cannot use the production empty-binding rule, and production cannot replace its fixed template with a model proposal. `offline_rsi` is not a planner-entry track; its controller follows its independently bounded lifecycle.
+
+Validation cross-checks envelope task/library/config references with launcher-committed production inputs/provenance or the experimental planning_reserved record, and with caller references. Its policy pin must be the authorized effective policy for that exact configuration. Proposal selections must cover every retained work step exactly once, have no extra step IDs, match capability names in the embedded plan, and resolve the named declaration hashes in the pinned snapshot. Verifier and external dependency closure come from that snapshot and applicable profile, not model-invented selection rows. The plan's snapshot hash must agree with the catalogue reference. Missing, duplicate or inconsistent rows produce INVALID before freeze.
+
+For the experimental Brief contract, `objective_bindings[].objective_id` names `research_brief.mandatory_requirements[].requirement_id`; it is not a new free-text objective namespace. Each mandatory requirement has at least one binding to an existing final output port and an independently authored applicable criterion reference. Every criterion must belong to the frozen policy/profile closure for that task and output. A model-supplied criterion cannot weaken the requirement or create a new acceptance rule. Optional preferences may inform proposal reasoning but cannot replace mandatory coverage. An ablated output remains an explicitly omitted study output; it cannot satisfy a mandatory requirement. Coverage is structural, while scientific truth is evaluated later by the governed workflow.
+
+### Who decides what
+
+| Decision | Authority | Permitted input from planner | Durable evidence / owning contract |
+|---|---|---|---|
+| M1 scope and track | frozen PRD plus recorded deployment agreement | none | [source freeze](../../product/SOURCE_FREEZE.md), [track boundaries](experiments.md) |
+| Task requirements | production intake then governed Brief; experimental validated Brief and explicit clarification before freeze | explain missing/contradictory information | intake/Brief Artifacts and source references |
+| Available versions and active defaults | library admission and authenticated human activation | select only catalogue members | [library](../capsule/library.md), snapshot and admission records |
+| Candidate capability arrangement | experimental planner, once per authorized request | exact step selections and typed bindings | immutable proposal with source capture |
+| Executable structural validity | deterministic validator under pinned policy | proposed arrangement only | PlanValidation and normalized plan |
+| Execution permissions, budgets and checks | developer-authored frozen profiles; trusted broker enforces | estimates and admissible references | profile pins, frozen Bindings, broker reservations |
+| Dispatch/release | supervisor from committed evidence | none | [lifecycle](lifecycle.md), Verification and release/experimental advance |
+| Scientific acceptance | frozen protocol, measurement authority and independent criteria | none after freeze | [evaluation](../m1/evaluation.md) and report evidence |
+| Retry, replacement or another proposal | authenticated human using explicit fresh request/attempt | structured failure findings | prior evidence preserved; no automatic repair or live rewiring |
+
+### Codex provider and pre-freeze authority
 
-The supervisor accepts only a VALID result matching the exact proposal/input hashes, then freeze re-resolves and pins dependencies. Neither model prose, native task approval, nor a stored proposal can release a node. After dispatch begins, the graph is immutable. A failed node follows normal halt/review; the planner receives no permission to rewrite a live plan.
+The planner uses the same replaceable `ModelProvider` boundary as capsules; the configured production-era transport is Codex app-server, not direct provider routing. [Environment](environment.md) owns the exact bridge frames, authorization scopes and capture rules; [model authentication](model-auth.md) owns credential custody. The Leader adapter supplies bounded prompt/context and native identity only. It never creates a second model client, imports auth files, spawns tools or gains native delegation authority.
+
+The experimental entry allocates its real run identity at intake, before freeze; `run_started` is still committed only after complete freeze. Before a planning turn, the supervisor commits `planning_reserved` in that run's SystemRecord namespace, pinning the exact task, library, configuration, policy, request bytes, model, deadline and call limit. Prompt bytes are captured through an authorized public Artifact in that same run. The authenticated planning scope is `{kind: planning, run_id, planning_request_id}`; it grants one bounded model turn and public capture to this reservation without a Binding. The bridge checks the registered reservation, principal and configured model rather than trusting the supplied scope. Fixed production envelopes use no planning scope and make zero planner turns. The planner receives the bounded reply, not credential bytes or executable broker descriptors. A failed reservation/capture write prevents proposal publication and dispatch. A duplicate turn attaches to the same reserved result; an uncertain interrupted turn requires explicit review, never automatic resubmission.
+
+### Resource accounting
+
+Proposal budget numbers are estimates to validate, not authority to expand policy. The validator derives step/Gate/dependency limits from the pinned declarations and profiles and rejects unbounded required call closures or a total above the applicable run policy. Sequential M1 execution includes verifier calls and admitted external dependencies in those bounds. Unknown token/money telemetry remains unavailable and cannot prove a budget pass.
+
+Before every actual public model call, the trusted broker commits `model_call_reserved` against the authorized scope's remaining call limit. The supervisor accounts the planning turn plus all work, nested and Gate model calls against the same run ceiling; `budget.maximum_model_calls` means that total, not a fresh counter after freeze. Planning additionally has its own pre-freeze one-proposal limit under the same real run identity. Validation includes already consumed reservations and rejects an allowance too small for their count plus the required remaining call closure. Private RSI/oracle calls retain their private owning reservations and never leak their counters or captures into public evidence. A declaration with a bounded skill-turn loop does not establish a bound for arbitrary tool-side model calls, so both use broker enforcement. Exhaustion refuses the call and halts the dependent step; no partial output is treated as success. Deadline expiry/cancellation use the model bridge's existing capture/reap rules. Runtime accounting and negative fixtures are required downstream evidence; model estimates or schema validation alone do not demonstrate enforcement.
 
 ```mermaid
 sequenceDiagram
     participant E as Experimental entry
-    participant P as Native Leader adapter
+    participant P as Leader adapter / Codex bridge
     participant V as Deterministic validator
     participant S as Supervisor/store
-    E->>S: reserve request + immutable task/config/catalogue
-    E->>P: propose(task, snapshot, config, request_id)
-    P->>S: persist raw response + PlanProposal
-    E->>V: validate(exact proposal and pins)
-    V->>S: persist PlanValidation
+    E->>S: allocate run identity, commit planning_reserved + input pins
+    E->>P: one authorized planning-scope turn
+    P->>S: commit required capture, then PlanProposal
+    E->>V: validate(proposal Artifact ref and exact pins)
     alt INVALID
+        V->>S: commit INVALID PlanValidation with findings
         S-->>E: findings / clarification required
     else VALID
-        S->>S: freeze bindings, then governed dispatch
+        V->>S: commit normalized run_plan, then VALID PlanValidation
+        S->>S: freeze complete Bindings, then dispatch
     end
 ```
 
 Rejection returns findings to the experimental entry. A human may supply a new Brief or authorize another proposal. Dynamic Intention Compiler clarification occurs only in its separately enabled experiment before freeze. The planner has catalogue-read and model-call access only; it cannot activate aliases, inspect private RSI fixtures, write policies, or execute proposed workload code.
 
+```mermaid
+flowchart LR
+    E[cc/experiments/entry.py] -->|planner_request / reserved run| P[cc/planning/service.py]
+    P -->|bounded prompt| L[cc/adapters/leader.py]
+    L -->|planning-scope ModelBridgeRequest| B[Protected Codex ModelProvider]
+    B -->|captured reply reference| P
+    P -->|planner_proposal Artifact| S[Trusted supervisor / immutable store]
+    E -->|validation_request / proposal ref| V[cc/planning/validate.py]
+    V -->|PlanValidation / normalized run_plan| S
+    S -->|committed VALID + exact pins| F[cc/freeze.py]
+    F -->|complete frozen Bindings| R[Supervisor / governed runner]
+    C[Admitted library snapshot / profiles] -->|read-only exact versions and bounds| P
+    C -->|closure and policy authority| V
+```
+
+The validator is a pure ordinary module in the monolith; the Leader is an orchestration adapter; the bridge is a protected internal process boundary. None becomes an admitted capability capsule. The diagram denotes API direction, not permission to let an untrusted model connect directly to store, freeze or runtime.
+
 ## Evidence, precedent and replacement
 
 Freeze resolves the exact reviewed library snapshot, not current active aliases. Test activation between validation and freeze: the old validated version remains pinned, unless current revocation denies it; no substitute is selected. Any snapshot mismatch produces zero dispatches. An isolated ablation disabling a capability is valid only if it has no required downstream output; otherwise reject it. Replacements must preserve exact output ports/schema versions. M1 does not synthesize missing data or install input substitutes to make a skipped required producer appear successful.
 
-Store writes proposals, raw turns, validation results and effective configuration through the trusted supervisor; all carry request/run correlation and immutable pins. This borrows typed component binding from [Kubeflow](https://www.kubeflow.org/docs/components/pipelines/reference/component-spec/) and deterministic rejection of invalid build graphs from [Bazel's dependency graph](https://bazel.build/concepts/dependencies). A model proposes, a deterministic authority admits executable structure. The Leader adapter can be replaced behind `propose`; validator changes require replaying the plan fixtures and updating its policy pin.
+Store writes proposals, raw turns, validation results and effective configuration through the trusted supervisor. Pre-freeze evidence carries the allocated run/request identity; that identity does not imply `run_started`, a successful plan or any dispatch. Failed planning leaves its preserved refusal/capture evidence under the same identity. This borrows typed component binding from [Kubeflow](https://www.kubeflow.org/docs/components/pipelines/reference/component-spec/) and explicit dependency closure from [Bazel's dependency graph](https://bazel.build/concepts/dependencies). Policy-selected decisions separated from enforcement follow [Open Policy Agent's philosophy](https://www.openpolicyagent.org/docs/philosophy). These are borrowed patterns, not claims that those systems prove our validator correct. A model proposes; the deterministic validator authorizes structure; the supervisor enforces persisted execution. The Leader adapter can be replaced behind `propose`; validator changes require replaying the plan fixtures and updating its policy pin.
 
 Fixtures independently exercise a valid fixed plan, missing producer, wrong type/version, cycle, unreachable objective, unavailable alias, forbidden effect, budget overrun, missing Gate and model timeout. Also verify an INVALID result and a failed validation write cause zero dispatches. A SkillFuzz-style fixture campaign varies input shape and planted faults without adding autonomous peer reviewers or runtime fuzzing to M1.
+
+The [adversarial design review](../reviews/2026-10-05-adversarial-design.md) maps malicious proposals, forged refs, budget understatements and interruption windows to refusal evidence. Optimization first measures proposal latency, rejection rate, committed call count and objective coverage on that fixture set. Cache only immutable catalogue/schema/prompt formatting by their full pins; never reuse a model proposal for a different request, weaken checks for speed, or select a live alias to avoid a cache miss. A prompt/provider revision creates new evidence under the same interfaces and is compared offline against the frozen fixtures. No performance target or improvement is claimed before measurement.
diff --git a/docs/architecture/system/records.md b/docs/architecture/system/records.md
index 510caba14..cab110498 100644
--- a/docs/architecture/system/records.md
+++ b/docs/architecture/system/records.md
@@ -16,12 +16,14 @@ This page owns internal control records, implemented in `cc/records.py`. It supp
 
 ## Closed envelope and store API
 
-`put_system(record: SystemRecord) -> SystemRef` and `get_system(ref: SystemRef) -> SystemRecord` use [storage](storage.md)'s publication, hashes, conflicts and recovery. SystemRef is closed `{id:id, sha256:sha256}`. SystemRecord is closed `{schema_version:1, kind:enum(run_started,dispatch_reserved,lifecycle,release,human_review,rsi_session,rsi_trial,rsi_security_clearance,oracle_session,oracle_closure,oracle_result,oracle_security_block,oracle_security_clearance,oracle_quota,rsi_attempt,activation), id:id, run_id:id?, session_id:id?, at:time, previous_ref:SystemRef?, payload:object}`. Schema_version/kind/id/at/payload are required; absent optional correlation keys are omitted. Each variant has the closed required payload below. Unknown fields and wrong scopes fail before publication.
+`put_system(record: SystemRecord) -> SystemRef` and `get_system(ref: SystemRef) -> SystemRecord` use [storage](storage.md)'s publication, hashes, conflicts and recovery. SystemRef is closed `{id:id, sha256:sha256}`. SystemRecord is closed `{schema_version:1, kind:enum(planning_reserved,model_call_reserved,run_started,dispatch_reserved,lifecycle,release,human_review,rsi_session,rsi_trial,rsi_security_clearance,oracle_session,oracle_closure,oracle_result,oracle_security_block,oracle_security_clearance,oracle_quota,rsi_attempt,activation), id:id, run_id:id?, session_id:id?, at:time, previous_ref:SystemRef?, payload:object}`. Schema_version/kind/id/at/payload are required; absent optional correlation keys are omitted. Each variant has the closed required payload below. Unknown fields and wrong scopes fail before publication.
 
 The separate `DATA/cc/system/<id>/` commit namespace accepts only these kinds and authorized writers. Use the same temp-directory/fsync/rename protocol as CC records, never JSONL append as atomic authority. JSONL lifecycle/attempt logs are rebuildable projections. Oracle quota has its own protected root and cannot be read through the ordinary store or exported. SystemRef cannot substitute for a CC record Ref. One supervisor serializes writes; the private oracle serializes its own reservations.
 
 | Kind / writer / scope | Exact payload fields | Identity / conditions |
 |---|---|---|
+| planning_reserved / supervisor / run_id | [services-v1 planning_reservation](../contracts/services-v1.schema.json) owns the closed payload | real experimental run allocated at intake; immutable task/library/config/policy/model/deadline/call pins committed before bridge access; same identity/bytes reuse, changed bytes conflict; no Binding or run_started required yet |
+| model_call_reserved / supervisor / run_id | [services-v1 model_call_reservation](../contracts/services-v1.schema.json) owns the closed payload | run requires exact declaration/dispatch linkage; planning requires planning_ref; obs_id/turn permit direct-call quota reconstruction, ordinal counts aggregate calls; reserve before forwarding, uncertain calls never refunded |
 | run_started / supervisor / run_id | plan_ref:Ref(artifact), intake_ref:Ref(artifact), config_sha256:sha256, library_snapshot_sha256:sha256, source_manifest_sha256:sha256, track:enum(production,offline_rsi,isolated_experiment), binding_refs:list<Ref(binding)> | run-start-<run_id>; references committed first; freezes complete source/config/library context |
 | dispatch_reserved / supervisor / run_id or admission session_id | caller:enum(dispatch,nested,gate,admission), step_id:id?, attempt:integer, obs_id:id, dispatch_id:sha256, request_sha256:sha256, binding_ref:Ref(binding)?, input_refs:map<string,Ref(artifact)>, parent_obs_id:id?, ordinal:integer? | dispatch-<dispatch_id>; reserve before effects; dispatch requires run/step/binding; nested/gate require parent/ordinal; admission requires session |
 | lifecycle / supervisor / run_id | step_id:id?, attempt:integer?, state:enum(pending,running,evaluating,halted,completed,aborted), dispatch_ref:SystemRef?, observation_ref:Ref(observation)?, verification_ref:Ref(verification)?, release_ref:SystemRef?, reason:Reason? | append-only sequence linked by previous_ref; completed step requires release_ref; halted requires reason |
@@ -30,9 +32,15 @@ The separate `DATA/cc/system/<id>/` commit namespace accepts only these kinds an
 | rsi_session / offline controller / session_id | target_decl_hash:sha256, parent_decl_hash:sha256, export_id:id, model_id:string, config_sha256:sha256, policy_epoch:id, evaluator_sha256:sha256, execution_profile_sha256:sha256, state:enum(preparing,running,closing,closed,stopped,blocked,finished,no_candidate), oracle_session_id:id?, incumbent_trial_ref:TrialRef?, oracle_closure_ref:OracleRef?, final_result_ref:OracleRef?, security_block_ref:OracleRef?, clearance_ref:SystemRef?, reason:Reason? | sequence linked by previous_ref; parent/model/config/policy/evaluator/profile immutable; closing/closed require closure/incumbent refs; finished/no_candidate require final evidence; security blocked requires incident ref |
 | rsi_trial / offline controller / session_id | target_decl_hash:sha256, parent_decl_hash:sha256, trial_decl_hash:sha256, declaration:json, files:list<TrialFile>, visible_suite_result_refs:list<Ref(observation)>, policy_ref:Ref(policy), permitted_paths_sha256:sha256, config_sha256:sha256, evaluator_sha256:sha256 | immutable implementation snapshot only; TrialFile is closed {path:string, sha256:sha256, content_ref:Ref(artifact)}; exact local file coverage, no hidden bytes; parent snapshot may precede oracle session creation and uses controller session_id |
 | rsi_security_clearance / authenticated human terminal / session_id | request_id:id, actor:string, target_decl_hash:sha256, execution_profile_sha256:sha256, security_block_ref:OracleRef, remediation_refs:list<SystemRef>, boundary_report_ref:Ref(artifact), reason:text | authenticated explicit clearance; nonempty remediation refs and current passing report required; label alone cannot clear oracle latch |
-| oracle_quota / private oracle / session_id | request_id:id, trial_ref:TrialRef, request_sha256:sha256, loop_set_sha256:sha256, purpose:enum(baseline,proposal,ablation,final), ordinal:integer, lifetime_ordinal:integer?, state:enum(reserved,complete,interrupted), passed:integer?, failed:integer?, reason:Reason? | serialized private commit reserves session ordinal 1–30 and lifetime ordinal 1–90 for loop queries; final uses ordinal1, omits lifetime_ordinal and has separate once/session reservation after closed; uncertain queries never refunded |
+| oracle_quota / private oracle / session_id | request_id:id, trial_ref:TrialRef, request_sha256:sha256, loop_set_sha256:sha256, purpose:enum(baseline,proposal,ablation,final), ordinal:integer, lifetime_ordinal:integer?, state:enum(reserved,complete,interrupted), passed:integer?, failed:integer?, reason:Reason? | serialized private commit reserves session ordinal 1ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã…“30 and lifetime ordinal 1ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã…“90 for loop queries; final uses ordinal1, omits lifetime_ordinal and has separate once/session reservation after closed; uncertain queries never refunded |
 | rsi_attempt / offline controller / session_id | Exact closed Attempt entry owned by [RSI engine](../capsule/rsi-engine.md#attempt-record) | attempt_id is the record id; previous_entry_sha256 links entries; no hidden cases |
 
+### Public model-call reservation semantics
+
+model_call_reserved is valid only for planning/run scopes. Its run linkage must agree with the envelope. Resolve dispatch_ref and its Binding for run calls, or planning_ref to planning_reserved for a pre-freeze planner call. The broker chooses obs_id/turn from the trusted call reservation; callers cannot select a fresh audit identity to reset the direct ceiling. Reconstruct direct calls grouped by exact obs_id/decl_hash and aggregate calls by run; both identities survive a crash. Missing or inconsistent authority blocks forwarding.
+
+budget_ref identifies the committed effective ConfigSnapshot before validation and the accepted complete proposal afterward. Cross-check config and policy; a model-created standalone quota object has no authority. ceiling is the minimum of policy/config and validated-plan limits, including already reserved planning calls. Reject ordinal above ceiling. The scope/request byte hash deduplicates exact replay; changed bytes conflict. Planning uses its single authorized turn; run direct ceilings are pinned by ExecutionProfile. The proposal's budget never refunds spent calls or extends an elapsed deadline.
+
 ### Private RSI control records
 
 TrialRef and OracleRef encode the same closed id/hash pair as SystemRef, with distinct namespace/kind authorization. A TrialRef resolves only to a controller-written rsi_trial in the private controller evidence root. OracleRefs resolve only through the oracle's authenticated API; ordinary get_system, manifests and benchmark exports cannot fetch private oracle records. Public Ref(Candidate) cannot be accepted in either position. For the parent trial, the controller allocates its session identity before begin_session; the oracle-issued identity is stored separately as oracle_session_id.
````
