---
id: cc-demo-handoff-20261111
status: fallback-reference
source: Sources/Prompts/20261111 Task Switch to CC Demo prepresentation.txt
last_reviewed: 2026-11-11
next_action: Read the current Collaborative CC Demo Plan
---

> **OLD SCOPE: superseded November 11, 2026.** See [current plan](<20261111 Collaborative CC Demo Plan prepresentation.md>). Trace Reader is a fallback, not the main demo. Component, skill, Builder and real inference through a demo lab now form the main story. Original guidance below remains for parser acceptance and provenance.

# CC and demo restart handoff

## Deliverable and scope

User is switching back to CCs and the demo job. The preserved direction in `AI4Research-Notebook/Sources/Prompts/2026-11-10-one-useful-cc-demo.txt` says **one useful tool OR one component is the core demo; everything else is extra**. Do not make the whole Factory/lab implementation a prerequisite.

Recommended first route: **Trace Reader**, a finite `cuda_profile_report` tool that analyzes a saved long-form NCU CSV, called by a real JiuwenSwarm agent through our CC runner. This is the best-supported technical recommendation, not a claim the user explicitly chose this tool over every component. The user authorized resuming demo work; there is no new ready-to-run implementation claim.

The earlier workshop target was Friday, November 13, 2026. Today is November 11, America/Toronto. Verify any later deadline change rather than using stale “tomorrow.”

## What exists, freshly checked

- Runtime checkout: `C:/Users/m50066326/huawei/AI4Research-Development/ccv2-work`.
- HEAD checked November 11: `2889a1d6342e9baa7721648eca196bbce79a31d4`; `git status --short` produced no entries. Recheck at resume; do not assume this persists.
- This is our reduced CC-v2 JiuwenSwarm branch, not unmodified upstream develop and not the older M1 system. Read its `AGENTS.md`, `docs/architecture/README.md`, and `docs/architecture/ccv2/README.md` first.
- Runtime front door: `jiuwenswarm/ccv2/agent_mcp.py`; runner: `jiuwenswarm/ccv2/ccv2.py`; declarations: `demo/ccs/`; agent driver: `demo/run_agent.py`.
- Eight tools: cc_list, cc_describe, cc_material, cc_artifact, cc_call, cc_start, cc_instance, cc_stop. Operator grants and workspace supply authority; the model cannot expand it. Native tools are trusted-local, not OS isolation.
- Existing parser candidate: `research/inference-campaign-closeout-20261110/followup-evidence/source/cc/profilers/ncu_summary.py` (workspace-relative). Preserve the received snapshot; develop a separate maintained package.
- Real historical fixture: `C:/Users/m50066326/huawei/research/inference-campaign-closeout-20261110/followup-evidence/source/artifacts/ncu1/ncu.csv`. SHA-256 `1237b06752eef88c1b599b4c0389e55f56ee7b351e9fe53c7eed461dd42c442e`.
- Defect evidence and recommendations: `research/inference-campaign-closeout-20261110/followup-evidence/design-analysis.md`, `parser-probes.json`, `analysis_probes.py`, and `source/cc/profilers/README.md`.
- The major handbook remains `outputs/milestones/20261110/Muse-Spark-Inference-Factory-Handbook.md`. Read only relevant Trace Reader/backlog sections; do not restart the entire research survey.

The parser/probe findings below are recorded prior evidence, not tests rerun by this handoff. No demo implementation or live agent invocation was done in the presentation session.

## First implementation job

1. Inspect existing finite-CC examples, schemas, runner receipts and grants in the actual branch. Reuse its integration rather than inventing another runner or restoring removed M1 packages.
2. Copy the parser candidate into a focused maintained tool; retain the original fixture with provenance. Keep the first route stdlib-only, finite and read-only; no GPU/Docker/profiling privileges are needed to analyze saved CSV.
3. Harden parsing and report scope using the acceptance cases below. Preserve input hash, format, unit, process/device/capture identity, tool version and limitations.
4. Package as one native finite CC using the current schema, not an assumed new timeout field. Return a report artifact with strict JSON plus the existing invocation receipt.
5. Rehearse a real agent discovery/description/invocation using a registered input handle and least necessary grants. Retain transcript, request identity, result, report and receipt. CLI-only parsing is not the live-agent demo.
6. Have the agent explain the observations and propose a targeted next experiment. It must distinguish measured diagnostic facts, missing data, hypotheses and scientific performance claims.

Do not edit/commit/push/deploy unrelated runtime work. The branch explicitly prohibits restoring the old compiler, capsule pipeline, RSI or benchmark stack. Port 5175 is its documented local web-host port. Existing login/setup instructions are in the runtime README; do not copy credentials into handoff artifacts.

## Acceptance and evidence boundary

| Case | Required behavior |
|---|---|
| Real saved capture | Correct independent kernel grouping, units, sums and weighted counters; retain input identity. |
| Writes not captured | null/unavailable per class, never measured zero. |
| Ambiguous numeric `1,5` | Reject instead of stripping commas into 15; define supported numeric grammar. |
| Missing process identity | Reject; do not aggregate into an anonymous process. |
| Aggregate overflow/nonfinite output | Explicit structured error; strict JSON disallows infinity/NaN. |
| Missing/duplicate required metrics or unsupported units | Structured input-invalid result distinct from a scientific negative. |
| Very large or malicious input | Bounded bytes/rows/fields and safe path access under granted workspace. |
| Whole launch absent | Capture completeness unknown without independently identified completion evidence. Hashes prove bytes, not truth/completeness. |
| Invocation replay | Same invocation key follows runner replay semantics; preserve receipt and avoid duplicate execution. |

Prior fixture report: 600 launches, 2226.88 microseconds summed kernel duration and 221.852565 GB/s effective DRAM-read bandwidth. Recompute against an independent reference before using these as acceptance values. These are historical profiled RTX observations, not new Muse/Spark results, wall-clock inference speed or proof of optimization causality. Preserve original captures when available; derived exports reference originals.

## Rehearsal story

Agent receives a question about saved profiling evidence; discovers and invokes Trace Reader; gets attributed observations with unavailable metrics explicit; handles one malformed input honestly; proposes the next useful experiment. Show what the tool makes reliable and reusable. A simulated lab is permitted as a demonstration aid but must be labeled and cannot substitute for the real CC call.

## Optional extension, only after the core works

Show a component patch plus Builder CC producing an identified variant, then a lightweight lab demonstration. Q8 reuse is a candidate, not already qualified: missing reuse-hit/alias/state/shape-change/graphs-disabled/numerical checks remain. Compare the same workload or token region; identical profiler launch-skip/count does not select equivalent work when the optimization removes launches. No latency improvement should be claimed from diagnostic timing alone.

If Trace Reader integration is blocked, the existing verdict tool is a fallback candidate; separate invalid evidence from a valid negative before demonstrating it. Do not switch silently or spend the core budget on Builder service lifecycle, live Spark provisioning or the whole catalog.

## Current architecture constraints for later integration

Use the companion presentation handoff. In particular, Lab Agent may conduct many runs and containers, diagnose failures, create lab scripts and retain brief-local working data. It uses selected tools and exposed engine signals to collect useful evidence. Evidence transfer calls Lab Manager, which stores and acknowledges it. The local brief store is isolated from other Lab Agents. Substantial product-code development stays in Factory.

## What remains unqualified

No current Muse/Spark baseline, accepted checkpoint/reference, exact benchmark policy or Spark profiler/provider path has been established here. No new GPU experiment, measured CC advantage or live Trace Reader demo is claimed. Old source text saying Jetson access is still blocked is stale: closeout was received, but missing raw files and evidence limits remain. Do not transfer RTX/Jetson findings to Spark.

## Copyable restart instruction

Resume the CC demo using this handoff. First inspect the current reduced CC-v2 checkout and the saved NCU parser/fixture. Implement the smallest reliable finite Trace Reader CC, prove its boundary behavior, and rehearse one real JiuwenSwarm agent invocation with retained artifacts and receipt. Preserve unrelated work and original captures. Keep the lab interface deck as a reference; one useful CC is the core, broader build/component/lab integration is optional. Report actual results and concrete blockers, never simulated evidence as a live run.
