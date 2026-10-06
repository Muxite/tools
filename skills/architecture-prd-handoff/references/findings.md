# Maintained findings: architecture and PRD handoffs

These findings come from a documentation reconciliation and package cleanup performed on 2026-10-06. They describe observed outcomes, not runtime validation. Project identifiers and machine paths are omitted so the guidance can transfer between repositories.

## Branch history can enlarge a small documentation delivery

**Observed:** A proposed documentation PR showed tens of thousands of additions because its branch included unrelated history.

**Consequence:** Reviewing the latest commit alone did not establish the requested scope.

**Correction:** Compare the entire head-to-destination diff before publication. Build a focused branch from the destination base and apply only the intended documents and necessary link repairs. Preserve the original branch instead of discarding unrelated work.

**Limit:** A large diff may legitimately contain required source material or rendered assets. Size signals a need to inspect scope, not an automatic rejection.

## Compatibility pages can create competing maintained designs

**Observed:** A canonical build package coexisted with dozens of compatibility pages and older architecture directories. Future edits would need repeated reconciliation across entrypoints.

**Consequence:** Readers could follow older material as if it were current design, and maintainers could miss duplicate guidance.

**Correction:** When the user chooses one maintained package, retain a small navigation entrypoint, consolidate repeated handoff guidance, and preserve superseded designs through a short index of exact Git revisions. Verify the history objects and paths before deletion. Save uncommitted drafts separately if needed.

**Limit:** Multiple maintained packages can be valid for distinct audiences or supported versions. Consolidation requires the user's intended authority model; it is not a universal directory rule.

## Verbatim fidelity includes stored bytes and line endings

**Observed:** A received PRD needed byte-for-byte preservation. Raw Git content and text-mode reads of authored files also produced apparent diagram differences because line endings were normalized during reading.

**Consequence:** Visual agreement or a working-file comparison could miss Git conversion; text normalization could also falsely report a semantic change.

**Correction:** Hash the received bytes and compare them with the package source and Git-stored or fresh-checkout bytes. Use narrowly scoped attributes when needed to prevent conversion. Use normalized text comparisons only for explicitly semantic checks, and byte comparisons for fidelity claims.

**Limit:** Authored documents may follow repository formatting conventions. Do not impose byte preservation on all prose or treat normalized equality as proof of source fidelity.

## Active and historical links have different destinations

**Observed:** An active decision record needed the current package, while older task records described an earlier architecture document that was being removed.

**Consequence:** Redirecting both to current architecture would silently change the meaning of historical records.

**Correction:** Repair active references to current maintained design. Pin historical references to the original document at an exact retained commit and mark their historical purpose. Check fragments and actual Git paths, not just the shape of the URL.

**Limit:** Historical prose containing an old filename is not necessarily a live navigation link. Preserve recorded meaning rather than mechanically rewriting every occurrence.

## Complete clause accounting does not prove semantic agreement

**Observed:** Repetitive coverage rows mixed requirement mappings with task allocations and repeated disclaimers. They could be consolidated while retaining every numbered clause.

**Consequence:** A heading count could conceal omitted bullets, exclusions, failure outcomes, or phase obligations; old task ownership could be mistaken for current product intent.

**Correction:** Maintain compact clause-to-responsibility mappings, verify missing and duplicate identities, and separately review exact requirement meaning. Keep common scope conditions once where readers can find them. Let the native specification workflow reconcile concrete task allocations.

**Limit:** The requirement identity scheme belongs to the source. Do not assume a fixed count, numbered headings, or one row per heading for every project.

## High-level architecture must leave implementers room without losing obligations

**Observed:** Design pages prescribed a particular boundary-model library and a reserved trial interface identifier. These could be replaced by responsibility and handoff requirements. Mandatory semantic, schema, and policy sources still needed preservation.

**Consequence:** Private implementation recommendations could appear mandatory, while removing all detail would discard real interoperability and acceptance obligations.

**Correction:** Retain responsibilities, information meaning, authority, trust boundaries, persistence, deployment, failure behavior, and required contracts. Label payload examples and native-code observations as references. Leave concrete representation, code structure, task allocation, and detailed tests to the implementation workflow.

**Limit:** A product-required wire format or schema is a design obligation. “Agents decide” cannot defer an unresolved high-level outcome or erase a mandatory contract.

## A successful trial is narrower than milestone completion

**Observed:** The first trial intentionally excluded portions of the full milestone and needed those exclusions to remain explicit after cleanup.

**Consequence:** A simplified package could imply that completing the trial satisfied all milestone obligations.

**Correction:** State trial inclusions, exclusions, and architectural exit meaning alongside the full delivery obligations. Keep delivery phases distinct from runtime and implementation stages.

**Limit:** Concrete acceptance criteria and test procedures can be generated later; the package must still establish the intended product scope and outcome.

## Local verification must be followed by publication verification

**Observed:** The cleaned package was checked locally, pushed, and then compared file-by-file with the actual destination commit. Source bytes and diagrams were verified separately from link and clause accounting.

**Consequence:** A successful push alone would not prove that the destination branch contained the reviewed package or excluded unrelated files.

**Correction:** Record the reviewed base and tree, inspect the complete delivery diff, publish within authorization, then verify destination identity and published bytes. Report documentation checks separately from unrun runtime tests.

**Limit:** These checks establish documentation fidelity and scope. They do not establish runnable compatibility, passing implementation tests, or readiness to merge under another project's governance.

## Existing reference tooling has a narrower contract

**Observed:** Repository inspection showed that `tundlekit text xref` resolves report-style references, not Markdown package URLs and fragments. Package checks needed separate inspection of inline, reference, shortcut, image, and Markdown-bearing text links.

**Consequence:** Reusing the command as a general package validator would overstate verification.

**Correction:** Match each check to the tool's declared contract. Record unsupported or skipped checks explicitly. Add reusable tooling only after a recurring need justifies a new contract and meaningful tests.

**Limit:** No general Markdown package validator is added by this documentation update. External URLs and renderer-specific anchor rules may need separate checks.

## Updating this document

Add demonstrated findings with their evidence and limits. Distinguish a user preference from a repository requirement and both from a reusable correction. Consolidate repetitions; retire advice contradicted by later evidence. Do not append full conversation transcripts, local artifact paths, or project requirements. Promote guidance into the skill when it changes decisions across realistic future tasks.
