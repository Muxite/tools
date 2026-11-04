# 4. Maintenance

**Use one canonical name and home per shared concept.** Update documents with behavior changes.

## Writing and naming

- Use plain technical English. Lead with the action.
- Prefer bullets, tables and diagrams. Leave space between ideas.
- New document paths: lowercase kebab-case. Preserve `README.md` as the established entrypoint convention.
- Existing paths, schema keys and identifiers: exact canonical spelling, including `Research_Brief.json`.
- Check path spelling against Git case-sensitively. Windows can hide mistakes that Linux/WSL exposes.
- Maintain Mermaid source. Label inputs, outputs, boundaries and responsibilities. Use the same color meaning and a legend. Register rendered views.

## Documentation and glossary

- Maintain terms in the [shared glossary](../glossary.md). Update prose, diagrams and agent instructions together.
- Review meaning changes for impact and compatibility. Prose edits do not rename machine contracts.
- Keep new authored text consistently formatted. Preserve immutable source bytes.
- Immediate: [README](../README.md), [M1 design](../m1-design.md), [principles](../principles.md). Keep their existing 3,400-word target.
- Topic: affected components. Reference: relevant contracts/examples. Review changed meanings across affected tiers, not every page.
- Update required English/Chinese counterparts in the same change. Agents help alignment. People review consequential meaning.

## Integrity review

Check PRD coverage, producer/consumer compatibility, feasibility, permissions, phase exits and failure paths. Include unavailable prerequisites, scientific negatives and stale evidence. Use [coverage](../coverage.md), [placement](../placement.md), [guard design](../guard-design.md) and [RSI](../offline-rsi.md).

Ready to specify needs resolved shared behavior. Ready to connect needs integration evidence. M1 completion needs its exits. Record human review separately from AI/document checks.
