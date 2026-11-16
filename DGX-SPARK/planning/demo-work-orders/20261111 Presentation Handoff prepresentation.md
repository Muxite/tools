---
id: presentation-handoff-20261111
status: historical-presentation-reference
source: Sources/Prompts/20261111 Task Switch to CC Demo prepresentation.txt
last_reviewed: 2026-11-11
next_action: Read the current Collaborative CC Demo Plan
---

> **OLD SCOPE: superseded November 11, 2026.** See [current plan](<20261111 Collaborative CC Demo Plan prepresentation.md>). This deck is earlier full-lab architecture background, not a finished deck for the new ten-minute collaborative demo. Latest, final and complete below refer only to that older deck. Its illustrative contracts are not the demo implementation.

# Presentation handoff

Eight-slide light-theme Software Factory / lab interface deck is saved. This is a pre-presentation design, not evidence that the system has been implemented or qualified.

## Authoritative deliverables

- Downloads: `C:/Users/m50066326/Downloads/20261111 Software Factory Lab Interface prepresentation.pptx`.
- Export source: `C:/Users/m50066326/huawei/outputs/lab-manager-design-20261111/download-v5/20261111 Software Factory Lab Interface prepresentation.pptx`. SHA-256 `a5531b49f6c0b178bc7dff0abb8bba16b22a8be692efc1e770a7b4a945ca60a3`.
- Live deck: https://chatgpt.com/space/page_c705578f4ddc81918d6bb593581ba225 . Reconnect using this page ID; old artifact-session references expire.
- Editable source: `C:/Users/m50066326/huawei/outputs/lab-manager-design-20261111/factory-interface.mjs`.
- Local exporter: same directory, `export-pptx.mjs`. Use a fresh output directory AND receipt filename on each export; finalizer refuses existing receipt paths. Latest validation: `.pptx-build/validation-v5.json`.
- Contract illustrations: same directory, `examples-v3/`, and `20261111 Software Factory Lab Interface Examples prepresentation.zip`. They are synthetic illustrative contracts, not execution evidence. They predate the final local-store/diagnosis clarifications; align these semantics before implementation.

## Decisions that supersede earlier slides and handoffs

1. Software Factory contains jiuwenswarm coding agents, Builder CC, tooling/catalogs, Lab Manager and primary telemetry/results. Spark lab environment is outside Factory.
2. Lab Manager is deterministic: task/caller/lab mappings, queue/dispatch, status/cancel/result, ingestion and retrieval. No scientific planner or autonomous repair inside Manager.
3. Lab Agent owns investigating the question and returning useful data and a justified verdict. It may perform many runs with multiple containers, adjust parameters, set up environments and create lab scripts. Substantial engine/product code belongs to Factory.
4. A failed simple test triggers diagnosis and useful further observations, not automatic return to Factory. Engine internal signals are exposed for lab analysis. Missing evidence and uncertain hypotheses stay explicit.
5. Each brief has an isolated local working store and credentials; no access to other lab briefs. Agent and runs read/write their own data. Working-data retention is separate from upload-spool cleanup.
6. Evidence transfer MUST call Lab Manager's interface. Manager writes factory stores and acknowledges durable receipt. There is no direct lab-to-factory-store write path. Coders can read authorized factory journals/logs/results to improve later work.
7. Spark diagram says **selected tools**, not CCs. Available/recommended/selected sets remain distinct; recommendations do not grant permission. Builder is an existing CC tool, not a separate factory subsystem.
8. Preserve submitted image; identify local patches, variants, runs/attempts and observations. One active task per Spark is only a dispatch default, not one run/container. Reconcile or stop/fence old execution before retries.
9. JSONL lab-event/v1, original captures and durable receipts; no invented zeros, complete-evidence claims, or scientific verdict from a timeout. Execution, verdict, evidence completeness and cleanup are distinct.

## Validation and remaining gaps

All eight slides rendered. Luna wording/adversarial reviews drove earlier repairs; final route correction was visually inspected. PPTX package/layout/import checks passed. No claim of native PowerPoint execution or new Spark tests. A source-script export recreates the editable deck; keep the live deck and local source in sync.

No need to continue polishing this deck during the CC/demo switch. The major November 10 handbook is preserved unchanged. Current detailed interpretation: [[Designs/20261111 Lab Agent Experiment Autonomy prepresentation]].

## Style to preserve

Light theme, diagrams with real payloads and clear containment, useful density, short box labels, no team-workload rationale. User naming: `YYYYMMDD Title prepresentation.ext` or `YYYYMMDD Title postpresentation.ext`; no em dashes in filenames. Keep internal code/schema filenames intact. Nothing establishes that the presentation has already happened, so retain prepresentation.
