---
type: process
tags: [process]
---

# How we work in this vault

*Reference, not for review: working practice, not design.*

**Order of work this sprint:** lock the [schemas](../schemas/schemas.md) first, then cut issues from the [six parts](../components/components.md), then build and verify.

1. **Schemas.** Everyone reviews every schema page. Questions go right under the part they are about as `> Q (name): ...`. Tick your box in the [sign-off tracker](../schemas/schemas.md#sign-off-tracker) when the page has what your component needs.
2. **Sign-off.** When a page's row has all four ticks, Muk sets `status: v1` in the page's properties.
3. **Issues.** Each issue is one unit from one section of a part page, written with the [issue template](issue-template.md), and may only depend on signed schemas. See the [filled example](example-evaluator.md).
4. **Build and verify.** The coder (human or AI) builds and runs the `builder` checks; Muk runs the `reviewer` checks; it works, it merges.

**Branch rules** (Xiaoyang, 2026-09-28):

- Everyone works on their own child branch of main.
- Never work on the same part in two child branches at the same time.
- Fetch main into your child branch before starting.
- A design needs design requirements, an architecture graph and priorities; Xiaoyang's code SOP covers the coding.

**Proposed for the code** (open until Xiaoyang's SOP settles them): two repositories, this vault and `cc` for the code, on Gitee, merged through a PR with one review; agent-core at jiuwenswarm's pin `9e339019`; Python 3.11 and Pydantic with `frozen=True, extra="forbid"`; CI runs `tools/sync.py --check`, the schema validator, and tests named by check id.

**Editing rules.**

- One fact lives in one page; other pages link to it.
- A schema page owns its fields. A part page owns what is inside its part. A trace owns the order of events. If two pages disagree, the schema page wins for fields and the part page for behaviour.
- Diagrams are Mermaid in code blocks. Keep them small: one component and its neighbours. Do not use `·` or other non-ASCII punctuation inside unquoted Mermaid labels; older Mermaid in Obsidian rejects it.
- Links are relative Markdown links, so they work in Obsidian and on GitHub or Gitee alike. Page properties use `[[name]]` links, which is what feeds Obsidian's graph.

Roles are on the [architect's role](architect-role.md) page.
