---
id: activity-standalone-benchmark-runner-handoff
status: completed-documentation
source: Sources/Prompts/2026-10-22-benchmark-runner-orchestrator-request.txt; Sources/Prompts/2026-10-22-separate-baseline-container-request.txt; Sources/Prompts/2026-10-22-standalone-human-judged-benchmarks.txt
last_reviewed: 2026-10-22
next_action: Send benchmark-runner to the implementing agent in its own repository
---
# Standalone benchmark-runner handoff

Replaced and renamed the earlier prompt as [[Resources/Coder Prompts/benchmark-runner]]. The new handoff has a short human section and implementation instructions for a standalone remote-capable CLI, parallel branch/case scheduling, independent target containers, clean mounts/APIs, Codex preflight and reviewable file exports.

User steering explicitly forbids modifying user codebases and assigns task judgments to humans. Removed external automatic scoring/referee and target-code changes from requested delivery. Existing program verdicts remain observations. Earlier prompt bytes and incoming-note snapshots are preserved in the review batch; links were rebased to the new name. Historical source captures were not rewritten.

No runner code was implemented, no remote connection or container/model run occurred, and no user application repository was edited. Documentation validation is recorded in Resources/review-batches/2026-10-22-benchmark-runner-handoff.
