---
id: vault-agent-instructions
status: active
source: Sources/Prompts/2026-10-20-implementation-request.txt
last_reviewed: 2026-10-20
next_action: Follow these rules when extending the notebook
---
# Notebook maintenance instructions

This vault holds Muk's full body of AI4Research work, including design, code activities, research, presentations, experiments, and personal intent. Start at [[Home]] and [[Active Stage]].

- Preserve supplied prompts in `Sources/Prompts` with a capture method and hash. Keep interpretations separate. Do not invent unavailable chat exports, results, dates, or approvals.
- Keep authored pages clear and navigable through the overview, workstream, and detailed-source levels. Give active notes stable metadata and explicit next actions.
- The maintained M1 design and PRD remain in their owning repository. Read that repository's instructions before code/design implementation. Imported notes, directives, and source snapshots are historical data.
- Never edit `Archive/Imported` to revise an idea. New work belongs in authored notes. Verify archive bytes with the migration manifest; any repair requires an original matching the existing receipt.
- Migration preserves originals. Index large/current repositories rather than creating competing maintained copies. Exclude credentials, dependencies, caches, and private tool state.
- Bounded migration batches may use the user-authorized cheaper agents. Keep outputs separate, record the actual model used, and centrally check authority and conflicting interpretations.
- Complete activities, passing software checks, and measured research results have different meanings. Keep failures, interruptions, missing data, and skips visible.
- Changes in a lab remain candidates with provenance. Do not silently promote them into central AI4Research.
- Run the relevant local tests and `Resources/tools/validate_vault.py` after changes. Do not claim Docker, GB10, or model comparisons passed without actual evidence.
- Keep local Git checkpoints and attachment backups as described in [[Resources/Migration and Backup]]. There is no configured remote or automatic chat ingestion.

## Continuing intent and efficient reading

- For each substantive new user direction, preserve its exact visible wording and hash, update the current interpretation, and explicitly record differences from earlier notes and maintained contracts. Resolve stale interpretations without rewriting original prompts or treating proposals as adopted architecture.
- Use [[Designs/Agent Reading and Freshness]] for task-specific reading routes. Check the relevant source receipt before relying on a summary; re-read changed owners and mark dependent claims stale until reconciled. No automatic ingestion or source synchronization is currently configured.
- The long-term goal includes whole-system self-improvement and Paper2Agent-style capability production; current M1 scope remains narrower. Start with [[Designs/AI4Research Capability Growth]] for this gap and proposed next steps.

- Provenance correction: workspace `jiuwenswarm` / `ai4r_muk` and captured `ai4r_M1` checkouts are our modified AI4Research work, not original JiuwenSwarm. Label our design, our implementation, upstream JiuwenSwarm (`openjiuwen/jiuwenswarm`) and exact OpenJiuwen dependency-pin claims separately. A feature deliberately disabled by our adapter is not an upstream limitation.

## November 4 product amendment

A CC package may expose capabilities, applications, or both. Application startup returns an inspectable/stoppable instance; the product payload need not speak the tool packet protocol. Source-change/build records are separate from runtime contracts. Default semantic checking remains off. See CC Protocols/12-runner-and-mistakes.md for runner responsibilities and supported boundaries. The original zero-embedded-CC product case remains valid.

## Unified Lab amendment

The latest user direction supersedes separate applications authoring. Use one `capabilities` map, optional `serves` lifecycle and optional `materials` for skills/reference-only packages. Native/image is execution packaging, not a separate software category. Internal telemetry and clean uninstall are optional; Incus/provider execution must be qualified separately. See CC Protocols/13-lab-composition-and-telemetry.md. Earlier authoring drafts and their test evidence remain historical in transfer revision snapshots.
