---
id: activity-spark-benchmark-setup-prompt
status: complete
source: Sources/Prompts/2026-10-22-spark-benchmark-setup-approved-plan.txt
last_reviewed: 2026-10-22
next_action: Send spark-benchmark-setup to the deployment agent when ready
---
# Spark benchmark setup prompt

Created [[Resources/Coder Prompts/spark-benchmark-setup]] as an optional direct-host Docker/Compose deployment handoff. [[Resources/Coder Prompts/benchmark-runner]] retains case execution, scheduling, comparisons and exports and can run on another host. Shared local inference is added only when needed. Practical storage controls apply immediately without requiring the M2 capacity controller, VMs, registry or capsule factory.

Updated the coder index, infrastructure workstream, design reading routes and Home. The M2 Spark and lab design entrypoints now distinguish this immediate setup from their longer-term architecture. Existing model connections and app components can be prepared while runner implementation or human authentication is incomplete; readiness claims remain specific to what was actually verified.

The exact approved plan is captured in [[Sources/Prompts/2026-10-22-spark-benchmark-setup-approved-plan.txt]]. Pre-edit bytes and hashes are recorded in `Resources/review-batches/2026-10-22-spark-benchmark-split/before-receipt.json`. Validation results are in `Resources/review-batches/2026-10-22-spark-benchmark-split/validation.txt`.

This activity changes documentation only. No Spark access, container deployment, model download or benchmark campaign was performed.
