---
name: architecture-prd-handoff
description: Reconcile architecture with a current PRD and prepare a maintained design package for an independent implementation workflow. Use for design audits, PRD replacements, architecture cleanup, or documentation handoffs; not ordinary runtime implementation.
---

# Architecture and PRD handoff

Produce product and design inputs that an independent implementer can navigate without inventing responsibilities, authority, or failure behavior. Preserve the user's chosen level of detail and the repository's native specification workflow. This skill does not grant permission to publish, push, merge, or implement runtime changes.

Read [the maintained findings](references/findings.md) when replacing sources, consolidating a package, or preparing delivery. They record demonstrated failure patterns and their limits, rather than universal project conventions.

## Establish authority and preservation

Inspect repository instructions, the requested destination branch, its current base, and working-tree changes. Compare the proposed delivery against that base before editing: a small commit can carry a large inherited diff. Preserve unrelated work and start a focused branch from the intended base when needed.

Identify the current PRD, authorized amendments, architecture decisions, native specification/coding records, and historical context. State which sources control product intent and which records control implementation ownership. Existing task and interface identities should be reconciled through the native workflow, not silently replaced or promoted into competing requirements.

Preserve received source bytes when verbatim fidelity is required. Record origin, receipt date, and a byte hash without inferring an author revision from a filename. Protect those bytes from Git line-ending conversion. For an authorized amendment, identify the affected clauses and behavior differences instead of claiming unchanged compliance.

Before removing or replacing designs, use the user's chosen preservation method. A verified snapshot preserves uncommitted drafts; a retained Git commit with verified paths preserves committed material. Confirm the saved bytes or Git objects exist before removing the live copy. A commit identifier alone cannot preserve an uncommitted draft. Label historical references as optional context, with exact revisions; do not rewrite their recorded design to imply current authority.

## Reconcile meaning and responsibilities

Map each applicable requirement to its architectural responsibility and source location. Check the exact bullets, exclusions, delivery obligations, and failure cases, not just numbered headings. Missing, duplicate, or empty mappings are defects; complete mappings are evidence of accounting, not proof of agreement.

Walk input, preparation, planning, execution, verification, persistence, release, and delivery, including offline paths where present. At each boundary establish producer, consumer, necessary information, authority, and the outcome when input is missing or invalid. Distinguish declarations from run-specific assignments, observations from assessments, and assessments from release decisions. Use a glossary where source terms overlap.

Keep delivery phases, implementation stages, runtime phases, and workflow roles separate unless sources establish their equivalence. A bounded trial needs explicit inclusions, exclusions, and architectural exit meaning; it does not imply full milestone completion.

For a vocabulary migration, keep one canonical crosswalk and apply display conventions across prose, tables and diagrams. Explain component containment, inputs, outputs and authority rather than treating related names as interchangeable. Put a former-name note beside the first renamed-slice mention on each maintained page; preserve source bytes, clause titles and registered identifiers unless their migration is separately authorized.

Retain trust boundaries, effect controls, evidence access, independent acceptance ownership, deployment topology, durable state, and recovery behavior where the product requires them. Resolve high-level outcomes for cancellation, unavailable environments, invalid evidence, persistence failure, and interactive versus headless operation. A scientific negative may be a valid result; distinguish it from infrastructure failure.

Keep producer claims separate from acceptance evidence. Explain reusable checks versus bound obligations and where verification ends; do not invent recursive reviewers. A high-level owner or failure outcome cannot be deferred as a private implementation detail. Record unresolved product choices rather than declaring readiness without them.

Leave private structure, concrete APIs, serialization, algorithms, prompts, detailed acceptance criteria, and tests to the owning specification workflow unless the source requires them or a demonstrated interoperability problem makes a design contract necessary. Preserve mandatory schemas and policy sources; label illustrative payloads and dependency observations as reference material.

## Prepare the maintained reading package

Frontload the reading order: authoritative PRD, architecture overview and decisions, then the relevant trial or delivery scope. Consolidate repeated navigation and handoff instructions. If one maintained package is requested, remove competing live designs and retain a short historical index rather than creating a second maintained archive.

Close the required reading graph inside the package when portability is requested. Identify repository code, live development instructions, tooling, external bibliography, and optional history as external prerequisites or references. The design package must not imply that it contains the runnable implementation environment.

Repair active incoming repository links to current package destinations. For historical records, point removed references to their original committed versions. Preserve recorded ownership and design; do not update historical prose into new requirements.

Keep affected diagrams consistent with prose. Render and inspect changed diagrams when tooling permits; check source and rendered references even when diagrams are unchanged.

## Verify the actual claims

Check package links, fragments, images, diagram references, and active incoming links. Include Markdown-bearing text files, reference and shortcut links, and declared manifest references. Separate required internal dependencies from optional historical and external references. Record skipped checks rather than counting them as passes.

The existing `tundlekit text xref` command (MCP tool `text_xref`) can check report-style section, appendix, figure, and table references where applicable. It is not a Markdown URL, fragment, portable-package, or PRD semantic validator. Use appropriate repository checks or inspect those separately; do not invent a tool name or claim unsupported coverage.

Verify immutable sources using byte hashes, including Git-stored or fresh-checkout bytes. Compare diagram sources and views as appropriate. Check requirement accounting and independently inspect semantic agreement, trial exclusions, authority, and high-level failure outcomes. Documentation checks do not establish runtime compatibility or implementation readiness.

Review representative paths: source replacement preserves bytes; package cleanup retains required reading; historical records retain their original context; focused delivery excludes unrelated commits. Scope any independent review to real contradictions when delegation is authorized.

## Deliver and maintain findings

Review the full diff against the actual destination base, including deletions and necessary link repairs. Leave runtime code and coding records unchanged unless separately authorized. Report exactly what was checked, what was skipped, and which questions remain.

Commit and publish only within the user's authorization and repository rules. Recheck the destination before pushing; do not force away concurrent changes. After publication, verify the destination commit and published file bytes against the reviewed tree. A local commit or successful upload alone is not evidence of the final published contents.

For future work, add findings only when supported by an observed failure or verified limitation. Record the symptom, consequence, reusable correction, evidence, and scope limit. Consolidate duplicates; promote a finding into the workflow only when it changes future decisions. Keep project identifiers and temporary paths out of general instructions.
