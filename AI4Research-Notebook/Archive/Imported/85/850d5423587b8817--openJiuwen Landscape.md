The platform and its neighbours: the facts that still hold after 2026-09-21. Read in source and independently re-verified. Long versions: `capsule-openjiuwen/notes/03`, `07`, `13`, `docs-read/`, and `verify/V1` to `V9`. How the capsule layer plugs in: [[Position in the Pipeline]].

## The goal

*"A layered architecture that covers the full lifecycle of an AI Agent, from development and runtime to deployment and operations."* **An AgentOS for production multi-agent work.** Capability reuse already appears in four of their repositories. AI4Research is **exploratory**, which buys two freedoms a product lacks: it can afford to be **strict** and **slow**. It owes one thing back: staying **prod-eligible**, meaning globally unique identity, effects declared across hosts, admission records others can audit, and no assumption that a person is watching.

## The siblings, and three ways to use the framework

| | Uses agent-core how | Relevant because |
|---|---|---|
| **jiuwenswarm** | broadly: seven subsystems, 800+ import sites | the integration hub; installs built-in skills by plain copy, with no hash |
| **deepsearch** | only `core`, behind one adapter it owns | the pattern to copy: take `core`, wrap it in one seam, build above it |
| **ScienceDiscovery** | declined agent-core; MCP-native, TypeScript | closest in purpose; **already has a versioned skill library with per-run pinning and recall**, and leaves judgment to the application. See [[Declared vs Observed]] |
| **skillhub** | distribution | review and approval before a version goes live; its CLI skips the hash check when the server sends none |

## agent-core

- `harness/extension_binder.py`: hot apply and unapply, with reverse-order undo. That's reversible **registration**, not reversible effects.
- `harness/security/`: pre-execution policy. It decides; it does not record.
- `harness/observability/`: tool calls with arguments and results, as spans. It doesn't see the effects of code that runs.
- `harness_providers/`: swaps whole harnesses (native, DSH, Claude Code, Codex) behind one protocol.
- `ToolCard`: `exposure`, `parallel_safe`, `stateless`, `idempotent`. **Nothing about preconditions, effects or trust.**

## Symphony: 检索用树，编排用图, trees for retrieval, graphs for orchestration

- **Retrieval** is semantic first: a model navigates a capability tree it built (`RecursiveSearchEngine`). Type matching happens later, in the Beam planner. Retrieval is not yet composed into `SymphonyRuntime`.
- **The fingerprint is derived**, not declared: descriptor, `content_hash`, typed I/O, semantic profile (model-written prose, off by default), quality, failures, evidence. It can't fail a test, but it can **disagree with a manifest**, and that disagreement is checkable. See [[Capability Capsule]].
- **`flow/` has a real gate**: ten static checks, then optional model review that can only downgrade, falling back to `needs_human_review`. Nothing executes the candidate. A recipe reaches `verified` on one successful run.
- **Evaluation**: six of nine metrics are model judges, and those are off by default.
- **The execution graph takes only skill, subagent and agent nodes.**
- **The least documented subsystem**: 0.69% inline comments against `core`'s 3.31%. Read the code, not the README.
- **trajectory v2** is freezing an evidence format. Consume it rather than design one.

## DeepSeek Harness and Cordis

Reachable from agent-core as a harness provider; **not the platform**. Worth borrowing as vocabulary rather than runtime: a *seam* is a definition, a provider and consumers; the sandbox fails closed and reports `full` or `partial` enforcement; tools are typed on both sides. Cordis reversal is **observational**: it reverts registrations and bindings, never files written or messages sent.

## Governance gaps

A4P signs tokens but does not archive or audit them. The published lifecycle policy is an empty stub, and its link returns 404. No document anywhere defines a skill or capability contract schema.
