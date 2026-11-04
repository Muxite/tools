---
id: cc-v2-integration-evidence
status: candidate
source: Sources/Prompts/2026-11-04-cc-v2-7.txt
last_reviewed: 2026-11-04
next_action: Repeat these bounded demonstrations before extending the integration claims
---

# Integration evidence and repeatable demos

These are bounded feasibility checks against unmodified official source. They do not establish production readiness, an LLM's coding quality, or enforcement by the full JiuwenSwarm server.

## Exact sources and environment

- JiuwenSwarm: official `git@github.com:openJiuwen-ai/jiuwenswarm.git`, commit `26acdaddae1fa0daf0f888f8012f0284a2548204`.
- Its declared OpenJiuwen agent-core pin: `4dbaa84ca568af3f181da4f9cd26b713a5b73039`, fetched from official `https://github.com/openJiuwen-ai/agent-core.git`.
- MAPIE v1.1.0: official `https://github.com/scikit-learn-contrib/MAPIE.git`, commit `90db8996a8c38c8e6574a901a1700ba889c3ac58`.

The exact checkouts and Python3.12 virtual environment are outside this notebook, at `C:/Users/m50066326/huawei/research/cc-v2-environment`. Existing `openjiuwen/jiuwenswarm` and `openjiuwen/agent-core` checkouts were not modified. `environment-report.json` captures clean source status, interpreter and imported-module hashes, installed versions, and the actual `pip check` result. `requirements-tested.lock` pins the packages installed for these paths. Install it into a new virtual environment, then install the exact agent-core and MAPIE source checkouts with `pip install --no-deps -e SOURCE`. Add the exact JiuwenSwarm checkout to the import path when running `environment_evidence.py` (the script does this itself).

This is a reduced dependency environment. `pip check` reports agentdescent, intelli-router and matplotlib absent; tested modules import and run without them. Do not describe this as a complete JiuwenSwarm installation. An upstream LFS video download returned404; code checkout succeeded with `GIT_LFS_SKIP_SMUDGE=1`. No core source was patched. Scientific execution initially failed with scikit-learn1.9.1 (`__sklearn_tags__`); the passing environment uses scikit-learn1.5.2 and numpy2.2.6. An initial cold package-import call hit60s and remains an unknown attempt in the external store. A quoted absolute Python command was rejected by the native shell allowlist; the passing native example uses allowlisted `python -B test_calculator.py`.

## Observed runs

`mapie_demo.py` seals `examples/mapie` and calls three operations: `fit_calibrate` produces a fitted/conformalized model artifact; `predict_intervals` consumes it and produces intervals; `evaluate` consumes those intervals and returns coverage, mean width and count. MAPIE's actual `SplitConformalRegressor.fit`, `.conformalize`, and `.predict_interval` execute from the pinned source. Synthetic seed20261104, training60, calibration50, heldout50: coverage0.94, mean width1.7601173275650268. A valid evaluation with heldout labels shifted+1000 executes successfully and reports coverage0.0. Execution completion does not imply a favorable scientific result. Full receipts retain exact inputs and artifact digests in `mapie-report.json`.

`upstream_mcp_demo.py` imports the real pinned OpenJiuwen `StdioClient`, connects over actual stdio to `mcp_server.py`, discovers all three generated tools/schemas, and completes the same artifact pipeline. Host `invoke_tool` injects its stable invocation identity before the transport call; duplicated evaluate invocation returns the same call receipt. Tool arguments supplied by the deterministic client are not produced by a live model. This demonstrates the OpenJiuwen client boundary used by JiuwenSwarm, not complete JiuwenSwarm server orchestration. `mcp-report.json` contains schemas and results.

`upstream_native_demo.py` creates an isolated real Git worktree. A real upstream `TaskTool` creates an isolated child session and runs prepare/cleanup hooks. Its explicitly deterministic child driver calls real upstream `SysOperation` local filesystem and shell operations to repair a tracked calculator, add an untracked regression script, and execute two assertions. Hashes prove a preexisting dirty tracked note and a preexisting untracked scratch file survive unchanged. The CC host captures before/after workspace changes and the execution artifact. `native-report.json` includes exact dispatch inputs, operation results, Git status and diff. This tests native delegation/lifecycle and actual work, without a live LLM or the complete JiuwenSwarm code-agent factory. Native policy assurance in the receipt identifies the selected host route; it does not claim every production policy was tested.

## Run again

From `reference`, using a Python environment installed as above:

```powershell
python integrations/mapie_demo.py --store C:/path/out/mapie-store --report integrations/mapie-report.json
python integrations/upstream_mcp_demo.py --store C:/path/out/mcp-store --report integrations/mcp-report.json
python integrations/upstream_native_demo.py --root C:/path/out --report integrations/native-report.json
python integrations/environment_evidence.py --environment C:/path/cc-v2-environment --report integrations/environment-report.json --lock integrations/requirements-tested.lock
```

Use a fresh MCP store for a new release/fixture. The native example creates a fresh fixture worktree each run. Local native execution is trusted code, and the model pickle is only for locally generated trusted artifacts. Artifact digest verification identifies bytes; it does not make arbitrary pickle content safe to load.

The MAPIE native binding names `requirements-lock.txt` inside the sealed bundle. Its exact dependency/source pins are therefore release content. This records intended dependencies; it does not attest all installed library bytes. `mapie-artifacts/inputs.json`, `model.pkl`, and `intervals.json` preserve the exact small fixture and artifact bytes; their digests appear in the report. The pickle is a trusted local demonstration artifact.

The scientific review found fixed confidence metadata and malformed-interval broadcasting/inversion defects in the initial capsule. `mapie_negative_replays.py` checks the corrected release against mismatched and multidimensional bounds, inverted intervals, nonfinite bounds, nonfinite labels, and empty arrays; mathematically invalid cases are rejected. Nonfinite caller JSON is rejected before a call is created. A separately fitted 50% confidence MAPIE model now produces metadata reporting 0.5, derived from the loaded pinned model rather than the capsule's training default. `mapie-replays-report.json` preserves these results and identifies the earlier reviewer-reported failures. The default 90% model pipeline and valid zero-coverage case both still execute successfully.


`factory_lab_demo.py` demonstrates a native product handoff without wrapping that product in a CC. It produces a small native Strata schema2 engine-component archive containing fixture text, then passes the archive artifact to the inspection CC. The worker calls the actual `strata_control.engine_component.read_manifest` and `verify(full=True)` from Strata commit `c62d5e3a15b40ea51c96aae9e8d36928965f53ab`. `factory-lab-report.json` preserves the product, manifest and payload digests, native loader hash, successful inspection and rejected tampered-payload receipt. `native-product-fixture.zip` is the exact synthetic handoff product and contains zero reusable CC declarations. Its CPU backend is manifest fixture data; its entrypoint is never executed, and this reports no loaded engine, GPU, inference or performance measurement. The native product retains its own manifest instead of being relabeled a CC. Run it with `python integrations/factory_lab_demo.py --root C:/path/out/factory-lab --strata-source C:/path/Strata --report integrations/factory-lab-report.json`.
