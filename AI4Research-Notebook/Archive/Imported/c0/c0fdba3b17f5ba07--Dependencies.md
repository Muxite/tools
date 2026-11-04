**This is (d): what CC itself depends on.** For M1 the list is short: agent-core (a pinned commit; which line
is open, see [[Open Questions]]), our own skeleton, and three seed tools. Symphony enters at M3 and the teams at
the rungs that read their records ([[Layer 2 Presentation]]).

The full list: systems and code (agent-core, Symphony, the workflow's stages), teams
(RSI, verification, routing), models (chooser, fit reviewer, measured judges, the generalist) and materials (papers,
rulings, the 2026-09-15 report, a sandbox, one vocabulary). Diagram: `capsule-openjiuwen/merged/figures/D1.png`.
A capability's **own** dependencies are not (d): they are Declaration fields, pinned by default, or unpinned with a
purpose at a cost to trust ([[Capability Capsule]]).

Each dependency is a record both sides agree on; nothing in it says how the other side does its work. Asks:
`capsule-openjiuwen/asks/`.

| On | The capsule layer needs | It gives back |
|---|---|---|
| agent-core | loading through its binder, tool-call spans, the trajectory store; configuration only (LLM extraction off, SkillUseRail experience text pinned or off, skill truncation off, one agent per sprint) | Declarations with carriers and declared effects; only admitted hashes |
| Symphony | its planner fed by a provider, its graph updated on each change | available capsules, a snapshot per run, declared ports |
| Saurav, RSI | the build decision and implementation roles; Declarations with `context_capsules`; never a direct write | gap Findings with generalist trajectories, counted over sprints; typed rejections. RSI's own gate (target cases, no held-out) is kept as evidence only, so RSI needs no change |
| Ramika, verification | the suite author role (held-out suites from the Declaration alone); parity fixtures; measured judge error; the audit loop | the checks to run; Bindings to trace failures to exact hashes |
| Xiaoyang, routing | a model among the frozen candidates, recorded in the Binding | `needs.model` constraints; the models each capsule's evidence covers |
| skillhub, ScienceDiscovery | import sources and patterns | nothing they must change |
| jiuwenswarm | skills, SkillPacks as import sources; overlays (teammate experience, TTSE) pinned per sprint or not loaded | a hash-pinned version of the SkillPack cascade it already ships (since `6f4eaa1b6`) |

- **agent-core** fully provides one of the five platform properties needed (H1 reversible registration). H2 dependency tracking is done by the capsule layer; H3 immutable artifacts is the new store; H4 is the trajectory archive, once wired; H5 sees tool calls only.
- **Verification works at three levels**: the capability at admission, the system at each sprint, and the verifier itself through its audit.

## (d) widened, 2026-09-23

Muk: **do not confine (d) to the three teammate features.** Every decision here also lands on parts of
the workflow nobody owns as a "feature" — the planner, the freeze, the scheduler, dispatch, retry, node
gates, attribution, delivery, gap handling, and now intake and intent
([[Every Stage Applies Capabilities]]). Those impacts are what a reviewer will probe, and three of them
are genuine costs of merging: scheduler granularity, whole-block retry, and coarser attribution.

The full table is in [[Impacts on the Workflow]]. Where the layer physically attaches in the code is
[[Where It Attaches]] — led by Symphony's `CapabilityProvider`, because openJiuwen already has the
sockets.
