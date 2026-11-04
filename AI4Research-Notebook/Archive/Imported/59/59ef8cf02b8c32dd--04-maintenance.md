# 4. Maintenance

**Keep names and meanings consistent. Update docs with design changes.**

## Writing and naming

| Item | Rule |
|---|---|
| Writing | Plain English. Action first. Bullets, tables, space. |
| New paths | Lowercase kebab-case. Keep established `README.md`. |
| Existing identifiers | Exact spelling, including `Research_Brief.json`. |
| Links | Check Git case. Windows can hide Linux/WSL errors. |
| Diagrams | Mermaid. Label boundaries, inputs/outputs, responsibilities. Render/register. |

## Documentation and glossary

- [Glossary](../glossary.md): canonical terms. Align prose, diagrams, agent instructions. Prose edits do not rename contracts.
- Immediate reading: [README](../README.md), [M1 design](../m1-design.md), [principles](../principles.md). Retain 3,400-word target.
- Detail: affected components, contracts/examples. Review changed meanings.
- English/Chinese: agents help maintain future counterparts. Update required versions together. Human review for consequential meaning.
- Preserve source bytes. Git-tracked context supports role rotation.

## Integrity review

Check coverage, compatibility, feasibility, permissions, exits, failure paths. Record missing prerequisites, scientific negatives, stale evidence.

Specification needs resolved shared behavior. Connection needs integration evidence. M1 completion needs phase exits. Human review and AI/document checks stay distinct.

[Coverage](../coverage.md) | [Placement](../placement.md) | [Guard design](../guard-design.md) | [RSI](../offline-rsi.md)
