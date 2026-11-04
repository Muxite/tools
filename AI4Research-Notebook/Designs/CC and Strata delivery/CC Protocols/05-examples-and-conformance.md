---
id: cc-v2-examples-and-conformance
status: bounded-integration-evidence
source: November 4 CC v2 reference implementation
last_reviewed: 2026-11-04
next_action: Qualify remaining image and full native-host boundaries
---
# Examples and conformance evidence

Use [the reference host](reference/ccv2.py), [tests](reference/test_ccv2.py) and [MCP projection](reference/mcp_server.py). Run from this directory. The commands below are reproduction instructions; they do not themselves claim a passing result.

## Portable native example

[The portable package](reference/examples/portable/cc.yaml) includes [source](reference/examples/portable/tool.py). Validate and seal it, then use the emitted release identity:

```text
python reference/ccv2.py validate reference/examples/portable/cc.yaml
python reference/ccv2.py seal reference/examples/portable --store STORE
python reference/ccv2.py call RELEASE CAPABILITY --inputs INPUTS.json --store STORE --trusted-local
```

The package exposes `trim`, `empty`, `echo` and `write-text`. For example choose `trim` with `INPUTS.json` containing `{"text":"   "}`. A sealed release executes copied source; modifying the original package must not change prior release behavior. [The image binding](reference/examples/portable/image.yaml) and [Dockerfile](reference/examples/portable/Dockerfile) exercise the corresponding container interface when the image/daemon is available. Image declaration validity is separate from an actual successful image call.

## MAPIE: a real predictive method

[The MAPIE package](reference/examples/mapie/cc.yaml) uses [real method code](reference/examples/mapie/method.py), with three capabilities:

| Capability | Result |
|---|---|
| `fit_calibrate` | Fit/calibrate a predictor and return its model artifact. |
| `predict_intervals` | Consume that exact model artifact and return prediction intervals. |
| `evaluate` | Consume intervals plus labels and report observed coverage/width. |

[The integration runner](reference/integrations/mapie_demo.py) joins these through the same Host API, using a deterministic synthetic split and ordinary JSON data plus artifact references:

```text
python reference/integrations/mapie_demo.py --store STORE --report REPORT.json
```

Install the package's declared dependencies in the chosen environment first. This is a demonstration dataset, not a general scientific benchmark. Nominal coverage is not guaranteed empirical coverage on every dataset. A plausible numerical result does not prove protocol enforcement or method superiority. Serialized model artifacts are executable/trusted material; admit only trusted producers.

## What conformance must distinguish

| Boundary | Required observation |
|---|---|
| Declaration | Defaults, shared descriptors, broad JSON, malformed/unsupported semantics. |
| Sealing | Source copied/hashed; material tampering and changed author workspace distinguished. |
| Values | Missing/extra/wrong ports; ordinary JSON remains ordinary data. |
| Artifacts | Input digest verification, output containment, durable output identity. |
| Handles/effects | Host resolution, grant refusal, enforcement mode and observation limits. |
| Calls | Same-key deduplication; changed content conflicts; uncertain work not replayed. |
| Outcomes | Partial/error output, crashes, timeout ambiguity and unsupported guarantees. |
| Bindings | Native, actual image execution and registered-agent callback tested separately. |
| Requests | Exact open-pointer filling and fixed-field preservation; no invented implementation. |
| Migration | Unsupported v1 meanings reported instead of weakened. |
| MCP | Plain arguments and canonical receipt across discovery/call. |
| Research | Actual MAPIE artifact pipeline with observed metrics. |

## Observed evidence · November 4

| Path | Observed result | Limit |
|---|---|---|
| [MAPIE host pipeline](reference/integrations/mapie-report.json) | Actual fit/conformalize/predict-interval calls, artifact edges and evaluation completed. Heldout coverage **0.94**, mean width **1.7601173275650268**, n=50. | Deterministic synthetic split: train 60, calibration 50, seed 20261104; no general accuracy claim. |
| [Pinned upstream MCP client](reference/integrations/mcp-report.json) | Actual OpenJiuwen `StdioClient` discovered generated tools and ran all three MAPIE capabilities over stdio. Repeating the stable evaluate identity returned the same call receipt. | Deterministic caller, no live model and no complete JiuwenSwarm server. |
| [Pinned upstream native task](reference/integrations/native-report.json) | Real `TaskTool` child session and `SysOperation` edited a calculator, added regression code and passed two assertions; preexisting dirty tracked/untracked files survived unchanged. | Deterministic child driver; native lifecycle/adapter test, not live-model coding quality or full host-policy enforcement. |
| [Container feasibility probe](reference/research/cc-v2-environment/container/probe-report.json) | Four direct native cases passed. The image did not execute. | Docker Desktop engine unavailable; native/image equivalence unestablished. |
| [Environment identity](reference/integrations/environment-report.json) | Pinned source/interpreter/import identities and package versions retained. | Reduced dependency environment; `pip check` reports absent packages. Not a full JiuwenSwarm installation. |

The Host container probe also completed four native capabilities and verified returned artifact bytes/digest. Its actual image call failed before worker execution. [The probe companion](reference/research/cc-v2-environment/container/README.md) identifies the retained external Host report and attempt store. Docker remained unavailable after supported restart/relaunch because `sailor-ingest.sock` could not be renamed/accessed. A resolved registry manifest is image identity evidence, not successful image execution.

[Integration instructions](reference/integrations/README.md) and [tested dependency lock](reference/integrations/requirements-tested.lock) describe reproduction and the exact upstream pins. Scientific execution initially failed with a different scikit-learn version; the passing environment uses scikit-learn 1.5.2 and numpy 2.2.6. A cold-import timeout remains an unknown attempt; successful later evidence does not erase it. All six non-container experiment stages were rerun after final host hardening. The final-run summary records current implementation/adapter hashes and report digests. Earlier failed attempts remain in their original stores.

A negative scientific case with labels shifted by +1000 executed successfully and reported coverage 0.0. This demonstrates why execution state and scientific usefulness remain separate. No passing-image, full-deployment, GB10 or complete adversarial-resolution claim follows from these checks.

Production qualification additionally needs tenant/authentication, native provider permissions, remote retry/recovery/cancellation and the actual Factory-to-qualified-host measurement trial. See [03](03-calls-and-receipts.md), [04](04-provenance.md) and [11](11-factory-lab-handoff.md).

## Final development-cycle results

[The final-run summary](reference/integrations/final-run-summary.json) records six passing stages: 21 local regression tests, the MAPIE pipeline, scientific rejection replays, pinned upstream MCP calls, native task delegation and the native product handoff. The attempted image execution remains blocked by Docker Desktop; it is not counted as a pass.

Three independent adversarial reviewers exercised protocol/usability, coding and Factory/scientific cases. Their original findings and second-cycle findings were retained, fixed and independently rechecked. Added regressions cover external executable identity, changed PATH resolution, overlapping workspace leases, unavailable final observations, late responses after reconciliation, migration dispatch collisions, malformed interval data and optional boolean schemas.

[The Factory/Lab report](reference/integrations/factory-lab-report.json) uses the actual pinned Strata manifest reader and full file verification on a synthetic native product containing zero CCs. Tampering fails verification. The entrypoint is not executed, so this establishes artifact handoff and inspection rather than inference, engine loading or hardware measurement.
