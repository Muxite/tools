---
id: experiment-first-cc-demo
status: proposed
source: Sources/Prompts/2026-10-20-cc-demo-dependencies.txt; Sources/Prompts/2026-10-20-m1-development-checkout.txt
last_reviewed: 2026-10-21
next_action: Follow the updated three-arm CC Accuracy Study and current baseline
---
# First CC demos and their dependencies

**Current reading route:** [[Experiments/CC Accuracy Study]] owns the new three-arm comparison (raw, plain with checks, CC with the same checks). The pre-check CC output is a diagnostic, not a substitute control arm. [[Resources/Current Baseline]] records the newly captured d3d7f56 snapshot and responsive Docker Desktop. The original dependency observations and preliminary comparison below remain dated inspection history.

**Recommendation:** demonstrate Scientific Evaluation with the generic Verifier first, then Requirements, then Screening. Start with supplied, frozen text/JSON fixtures. No hardware workload needs to run to demonstrate whether the capsule applies a registered rule correctly.

## Source candidate and implementation status

The user supplied `Stellven/jiuwenswarm`, branch `ai4r_M1`. The separate development clone is [jiuwenswarm-m1](../../AI4Research-Development/jiuwenswarm-m1), checked out clean at `98bd9d913f9ddae5f0d6a3ae256bff10f25ee743`. It is a shallow clone, independent of the older JiuwenSwarm folders.

This branch has actual `jiuwenswarm/research` code: capsule workers, deterministic checks, gates, library/admission, scheduling, and the governed model bridge. Source presence does not establish runtime acceptance. The initial readiness audit concerned the older `jiuwenswarm` checkout and must not be used to conclude that this new branch lacks implementation.

The branch's own architecture/instructions differ from the older checkout, including its compact-package and scope wording. Keep those source versions distinct. Reconcile architectural differences before modifying code; this inspection changes no product contract.

## Demo order

| Order | Capsule and purpose | Demonstration | What the result would establish |
|---|---|---|---|
| 1 | Scientific Evaluation plus Verifier | Frozen blueprint and supplied baseline/treatment values: valid PASS, valid FAIL, missing-value INCONCLUSIVE, and planted wrong classification/threshold | Registered-rule correctness, missing-evidence handling, and rejection of an incorrect verdict |
| 2 | Requirements, with Intent as its input | Preserve a supplied request's constraints, deliverables, and evidence obligations; expose conflicting or missing mandatory information | Whether the compiler preserves intent without fabricating requirements |
| 3 | Screening plus Verifier | Supplied candidates and a pinned rubric: dependency exclusion, exact totals, ties, and no eligible candidate | Deterministic selection correctness and explainable non-selection; not proof that novelty scores are objectively true |

Scientific Evaluation is the clearest first oracle: the host can independently recompute its classifications from fixed values and rules. Its current [worker](../../AI4Research-Development/jiuwenswarm-m1/jiuwenswarm/research/capsules/evaluation.py) makes a model call, while checks remain outside the worker. A correct scientific FAIL or INCONCLUSIVE is an accepted result, not a broken pipeline. A false PASS is wrong; a blocked malformed output is a contract failure. Keep these outcomes distinct.

For Requirements, the model verifier cannot by itself establish fidelity to unseen original inputs. Host checks and independent scoring against the actual request remain essential. For Screening, arithmetic/filter/ranking correctness and subjective scoring quality need separate evaluation.

Defer Search, Builder, Research Benchmark, and a complete autonomous journey until the bounded demos work: they add external retrieval, generated-code execution, measurement custody, and resource qualifications that are unnecessary for the first verification comparison.

## JiuwenSwarm and Codex execution paths

The older checkout selects its ordinary [Codex subscription adapter](../../jiuwenswarm/jiuwenswarm/server/runtime/agent_adapter/interface_codex.py) in place of the native harness. That adapter explicitly rejects tools, teams, skills, and attachments. It supports a text-only raw baseline with fixture contents included as text; do not label it a demonstrated full native-harness comparison.

The newly supplied M1 branch additionally has [GovernedBridge](../../AI4Research-Development/jiuwenswarm-m1/jiuwenswarm/research/bridge.py), which dispatches the fixed route through the subscription service's `invoke_governed`/`invoke_governed_traced` path. Its capsule workers use the bridge rather than each constructing an API client. Optional API providers also exist, but they are unnecessary for the initial fixed Codex route.

The proposed comparison is:

1. Raw JiuwenSwarm Codex text turn, given the frozen question, rules, values, and common requested output format.
2. CC worker output before checking, retained as evidence. Analyze this as the declaration/instruction treatment; do not weaken the product gate to obtain it.
3. The complete CC path: worker output, deterministic checks, fresh verifier context, and gate release/halt.

Keep both arms on the same observed Codex model/settings, fixtures, fresh conversation state, and total budget. The verifier must not inherit the worker conversation. Retain exact prompts, outputs, check results, model-route observations, and elapsed time. Model/verifier agreement alone is not independent correctness evidence; use the frozen rule oracle.

Current contracts reject/halt without an automatic repair loop. The earlier conversational suggestion of one correction attempt is a future experimental variant, not current M1 behavior.

## Dependencies and readiness

| Dependency | Observed state or requirement |
|---|---|
| Development source | Clean branch `ai4r_M1`, commit above; source remains unchanged |
| Linux Docker engine | Required by supplied deployment; `docker` is not available in installed WSL distro `Ubuntu-24.04` |
| Image build | [Dockerfile.app](../../AI4Research-Development/jiuwenswarm-m1/deploy/m1/Dockerfile.app) pins Python 3.12, Node 22, uv, dependency lock, and installs the qualified Codex runtime; not built here |
| Operator inputs | Valid operator config, exact policy/static-template/evaluation-profile references where required, admitted capsule catalog and captured input resources; empty YAML starts inspection only |
| Model account | Dedicated application Codex/ChatGPT account session; configured fixed route and model readiness. No API key is the initial plan |
| Governed execution | Protected resource/budget/binding prerequisites reported by `/api/v1/readiness`; follow [deployment guidance](../../AI4Research-Development/jiuwenswarm-m1/deploy/m1/README.md), not just the fact a web page loads |
| Study fixtures | Frozen blueprint, values, Brief and expected classification; independent keys outside worker/verifier context |
| Hardware | No GPU or future hardware required for supplied-result classification; actual performance claims need actual hardware and measurements |

On this workstation the default Python lacks `workswarm`, `openjiuwen`, `openai-codex-cli-bin`, and FastAPI, and the older checkout's `.venv` is absent. The container build is the supplied reproducible dependency path; no package installation was attempted here.

The one-use bootstrap URL is an authentication credential, not experiment evidence. Never save its actual value in this vault. The web inspection UI and readiness are separate from successful research execution.

Measure released-answer correctness, incorrect releases, answer coverage, appropriate abstentions, avoidable abstentions, and operational failures separately. An unanswerable case handled honestly is different from a wrong answer; refusing everything still does not demonstrate useful research capability.
