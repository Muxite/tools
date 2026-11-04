---
id: paper2agent-architecture-source-review
status: reviewed-bounded-sources
source: local Paper2Agent checkout and maintained jiuwenswarm design package
last_reviewed: 2026-10-21
next_action: Revisit if current Paper2Agent skill or maintained M1 architecture changes, or if a concrete integration proposal is authorized
---
# Paper2Agent: architecture source review

## Receipt and scope

This is a bounded architecture review of Paper2Agent materials and their possible relationship to AI4Research. It is not a product decision, a full review of the Paper2Agent paper, a runtime evaluation, or an authorization to integrate code.

- Paper2Agent repository: `Paper2Agent/`, Git revision `8c2d059165ef8cdcb70dbea76655b9c2b55b38e6`.
- AI4Research architecture repository: `jiuwenswarm/`, Git revision `889682f0afc3d06c2ad88e71534483a31d2eb560`.
- Reviewer model recorded for this bounded pass: **gpt-6-luna**.
- Review scope: Paper2Agent `README.md` and root skill entrypoint `skills/paper2agent/SKILL.md`; current AI4Research design overview, capsule model, library/checking contract, decision register, run-plan reference, RSI workbench; and the older Paper2Agent evidence note named below. All 21 source pins in the batch receipt are listed in [source-receipt.json](source-receipt.json); this narrative summarizes only the bounded sources listed below.
- Limit: source documentation only. No full skill execution, tool behavior audit, paper-result verification, compatibility build, or acceptance testing was performed. Hashes bind the reviewed local bytes; they do not establish remote freshness or runtime behavior.

| Reviewed source | SHA-256 |
|---|---|
| `Paper2Agent/README.md` | `68406de69cb02985c152e6bce989d053b31fb8eee21109dfe2d2583c11ab594a` |
| `Paper2Agent/skills/paper2agent/SKILL.md` | `02a5847a646c8851ccb881d7bc7c8cdcf71a7dac9746eb6ceb3e87e21d13a7dc` |
| `jiuwenswarm/docs/architecture/design-package/README.md` | `736558f7afb66842f673577ae66b85a27685451f112828a42da567a0a19f20bb` |
| `jiuwenswarm/docs/architecture/design-package/2-capability-capsules.md` | `09a4079654a0ac50289d6cd0deb1b33c6ffa7936957bcaaedea7958303758673` |
| `jiuwenswarm/docs/architecture/design-package/capability-capsules/library-and-checking.md` | `c12709033b92946f2d3ec192320cc3e5ab37facd382ecc5b78bf7119b8e12be9` |
| `jiuwenswarm/docs/architecture/design-package/method/decisions.md` | `609825aef49d7d5c040485726cf73600a7bd52ebab0562774eeca0564ccaaa71` |
| `jiuwenswarm/docs/architecture/design-package/reference/run-plan.md` | `7c3867f8914d32a49be90c2f30fea58275e1a7b64548b130b20d643280c7ba7a` |
| `jiuwenswarm/docs/architecture/design-package/side-systems/rsi-workbench.md` | `66918a59cc4416d0fde089926f0be730cfdcce4e07ba7868d78928cc629e89d2` |
| `jiuwenswarm/docs/research/paper2agent/presentation/references/evidence-notes.md` | `4b876147a3325217ac4d098581bad976103e96e16b481763dfc15e1f1a7cff6c` |



## Findings

The Paper2Agent README describes a workflow that turns research papers and associated repositories into interactive research agents, including MCP servers and skills. It describes coordinated specialist work, testing, and packaging. That makes Paper2Agent a plausible source of reusable *acquisition and extraction methods*â€”for example, turning methods, code, and tutorials into candidate tools with documentation and test evidence.

This does not by itself show that generated tools are suitable AI4Research CCs, that the process improves scientific correctness, or that AI4Research should adopt Paper2Agentâ€™s orchestration wholesale. A paper-derived tool candidate would still need AI4Researchâ€™s own declaration, exact immutable implementation/dependency pins, independent compatible checks, protected admission, and evaluation against a real need. Generated artifacts, notebook summaries, and executable CC versions are different objects with different owners.

The maintained M1 design currently supports bounded `agent` and `tool` CCs. Composite CC creation/execution is deferred; the designâ€™s future composition work permits multiple work subnodes in a node, but preserves each memberâ€™s own pinned contract and authority. The binder and protected host own plan freezing, permissions, checks, and release. M1â€™s semantic verifier receives a declaration and exact output only. M1 RSI is separately bounded and off the hot path; it does not authorize system-wide self-modification. These constraints mean a future Paper2Agent-derived intake/factory should be framed as a candidate workflow behind current host controls, not as an implicit extension of M1.

The ultimate whole-system self-improvement direction across research, design, coding, and runs was absent from the earlier `Implementation Intent`; the latest intent extension now records it, while M1 contracts still do not specify or implement that complete loop. Reusable acquisition stages and a composite/factory model may be useful future architecture, but they need their own source-backed problem, output obligations, evaluator, authority boundary, and decision. Do not infer approval from an old presentation note or from Paper2Agent presence in the workspace.

## Stale-note warning

The older [evidence notes](../../../../jiuwenswarm/docs/research/paper2agent/presentation/references/evidence-notes.md) explicitly direct readers to compare against `AI4Research_private_planning/.../design-package-compact/`. The current repository instructions retire that compact package (D27); it remains historical only. Therefore that link cannot define the current capsule schema or integration contract. The evidence note remains useful as a dated source of reported Paper2Agent claims and as a warning that integration was only a hypothesis. Recheck reported study metrics against the primary paper before using them in a decision or external presentation.

## Suggested next review, if integration is pursued

1. Before execution-level claims, inspect the relevant Paper2Skill or Paper2MCP component instructions and scripts at this pinned checkout; this review only inspected the README and root router skill.
2. Identify one concrete repeated AI4Research need and compare Paper2Agent-derived output with existing native CCs, code, and JiuwenSwarm/OpenJiuwen capabilities.
3. Define an intake stage that emits traceable candidate artifacts and evidence, not an admitted CC by default.
4. Write the candidate CC declaration and independently checkable criteria first; preserve verifier input isolation and protected host checks.
5. Evaluate usefulness, correctness, reproducibility, and authoring/runtime cost with a frozen comparison. Consider composition or containerization only if the case demonstrates a gap and the existing dispatch boundary can preserve host authority.

No claim of perfect or exhaustive source coverage is made. A changed source invalidates the affected finding until its owner is re-read; no automatic refresh or adoption mechanism is implied.
