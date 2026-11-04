# One-shot study: design inputs and implementation evidence

**Question.** What evidence can be observed in the bounded coding exercise with the pinned design input and Spec Kit versus the input without it? This is observational, not randomized, and cannot establish a Spec Kit or condition winner.

## October baseline and trial boundaries

The October 30 main-path result is an artifact-dataset baseline using generic Leader/SwarmFlow. It is not an integrated AI4Research Planner. The one-shot trial fixes four roles and replays worker data; it does not conduct interactive conversation. Record the exact configuration, inputs, outputs and run evidence so later integration can be compared without changing what this trial claims.

The approved semantic-check deviation checks declarations and produced output only. It does not establish source-level or complete intent-fidelity review. Report the lower fidelity assurance explicitly; do not present the baseline as full PRD compliance or as evidence that the workflow understood a live user conversation.

## Pinned conditions and recorded evidence

| Condition | Pinned input | Recorded observation | Limit |
|---|---|---|---|
| With Spec Kit | `origin/ai4r_test_with_spec_kit` at `73ed9e867d58a22ac57699913ecbd7f4d3619f2c` | M0 contains a compiler implementation. Historical R07 records six real-model cases, including accepted actionable/omission inputs and halted invalid or semantically rejected inputs. Historical R03 records 197 tests. | Historical counts are not fresh validation. R07 was not revalidated with this run. |
| Without Spec Kit | `origin/ai4r_test_without_spec_kit` at `a0d999af1788c764e30df5d1c29956464ae4808a`; input snapshot `c9e0cbf4cdd06ce9c56077a6bebff4cf38e8716c` | The snapshot records input only. | No implementation receipt is present for a matched outcome. |

**Fresh isolated local check, Oct 14:** the extracted with-condition compiler candidate was installed from its original `requirements.lock` in `compiler-review-env`, then run with `pytest -c pytest.ini tests -q`. JUnit records **209 tests: 207 passed, 2 failed** in 82.26 seconds. This local synthetic-fixture run made **no model/API calls** and does not measure semantic quality or real-model behavior.

1. `test_contract_bytes_match_registered_source_receipt` failed: `common.schema.json` expected SHA-256 `2e40a008…9818c880`, observed `f5f0e393…7adb4216`. Read-only comparison confirms the candidate and pinned source have the same Git blob, while the extracted/archive bytes differ: the candidate has 330 CRLF sequences in addition to 330 LF bytes; the pinned source has LF only. This points to line-ending transformation in the archived/extracted artifact, not a changed source schema. The candidate was not edited.
2. `test_actual_bridge_streaming_capture_overrun_terminates_with_bounded_raw_evidence` expected `output_limit` but observed `failed`. Its fixture launches a local Python process that emits 1 MB and sleeps; source code intends to set `output_limit` when the bounded reader detects overflow. The recorded assertion does not identify why the observed outcome was `failed`; treat this as an unresolved runtime-fixture failure, not a pass.

The saved [intent outputs](../../../../intent-outputs-extracted) include one accepted and one compiling provider result associated with `gpt-5.6-sol`; records do not attribute them to either condition. Frontend V07 is incomplete, V08 blocked by Docker, and the UI/container path remains unrun.

## Interpretation and reuse

The without-condition outcome remains unavailable, so condition-level completion, correctness, quality, time, model behavior, and efficiency cannot be compared. Token/cost data and matched evaluation are unavailable; unavailable is not zero. Do not claim Spec Kit won.

`standalone/intent_compiler/` is a **reuse candidate pending repair/reconciliation**: first preserve exact source bytes and diagnose the capture-overrun result, then reconcile interfaces with current blueprints and shared resources. These findings do not justify rebuilding the whole compiler or declaring this candidate a baseline. `intent-outputs-extracted/` remains useful for case review only, with unknown input attribution. Current architecture authority remains the maintained design package.

## What this tells us about design granularity

The compiler trial shows that the supplied contracts can support a substantial implementation with observable gates and evidence. It does not establish that the entire revised core journey can be built unattended, or that more design detail necessarily improves output. Keep the three-tier reading route; add detail where boundary failures expose ambiguity rather than expanding every page.

For the October 16 trial, pin the package, four-role configuration, artifact/worker-data inputs and initial output before human repairs. On October 19–20, map observed behavior and gaps to the trial’s actual boundary; distinguish generic Leader/SwarmFlow behavior from future AI4Research Planner integration. Record omitted behavior, invented interfaces, wiring failures and human repair effort separately. By October 26–28, use independent workflow cases to distinguish design ambiguity from implementation failure. The October 30 verdict is limited to the artifact-dataset baseline and its indexed evidence; it does not imply full journey integration or fidelity assurance.
