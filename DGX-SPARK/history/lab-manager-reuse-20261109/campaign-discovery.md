# Core objective: let real improvement work reveal the system

The user clarified that determining the Lab Manager design and every initially needed CC is the most important goal. The mechanism is real engineering: improve inference on an existing model, explore the relevant body of methods, observe the work, then extract reusable tools, methodologies and components. Friday needs a few clear demonstrations from that work. Image handoff is necessary infrastructure, not sufficient campaign success.

## Evidence loop

Source/paper mechanism → applicability question → experiment → code/config/component candidate → build CC produces engine image → separate lab test → quality/performance/profile evidence → continue/reject → Manager/CC implication.

Capture each stage and its failures. Methods may change as evidence arrives. Preserve separate identities for model/representation, source change, component version, image, workload, test policy and attempt. A scientific negative can teach us about a useful tool; an attractive source abstraction can prove useless in practice.

## Portfolio to determine

| Family | Needed campaign outcome |
|---|---|
| Build CC | Actual repeatable image-producing capability used by the agent across iterations, with successful and failed build records |
| Profiling/test CCs | A small cohesive initial set for actual quality/state/performance/diagnostic needs; evidence of supported paths and missing coverage |
| Tool CCs | Independently useful engineering operations justified by observed work, with sensible grouping and thin upstream reuse |
| Methodology CCs | Reusable instructions, procedures, templates or workflows demonstrated through actual investigations and known failure cases |
| Component CCs | Useful engine assets whose form is learned: snippets, source modules, classes/functions, libraries, kernels or binaries plus integration guidance, compatibility and tests |

The taxonomy is required; exact names/counts/forms/algorithms are discovery outputs. Do not require CC packaging before every experiment, and do not finish with a purely speculative catalog. Distinguish implemented/qualified, reused unchanged, thin-adapter, missing, deferred and rejected capabilities. Track uncovered method families so the initial inventory's completeness has an explicit boundary.

## Manager design to determine

Use actual concurrency, staging delays, lost responses, crashes, export interruptions and repeated work to establish admission, asynchronous submission/status/cancel/results, attempts/ownership, durable records, artifact registration and recovery. The other team owns the lab agent and sandbox provisioning; we own learning what the Manager must do and exercising their agreed boundary. Compare simple existing-module/storage solutions against heavier services using observed need.

## What improvement means

Aim for a measured engine-execution gain on the pinned Granite target, with quality checked under a fixed relevant policy and workload. Investigate applicable runtime, routing/residency, memory, CPU/GPU overlap, representation, kernels, state and serving methods. Use repeated matched ordinary measurements; diagnostics explain them. A changed workload is not a gain under the original conditions. A tiny fully resident model cannot establish large-model expert-offloading claims.

If no supported improvement emerges within the available budget, retain failed/inconclusive experiments, explain the remaining bottleneck and recommend the next discriminating experiment. Do not fabricate success, and do not treat a successful handoff as an excuse to stop searching.

## Updated handoff

[Current two-machine prompt](two-machine/ORCHESTRATOR-PROMPT.md) carries the latest machine allocation and resumable-campaign instructions. [General coder prompt](coder-agent-prompt.md) retains the empirical-discovery foundation. Earlier demo-first versions are preserved byte-for-byte under `context/prior-demo-first/`; [receipts](context/prior-demo-first/receipts.json) retain their hashes. Software dossiers remain source research, not runtime acceptance or a mandatory adoption order.
