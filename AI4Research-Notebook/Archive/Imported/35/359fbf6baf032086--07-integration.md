# 10. Integration: what each consumer reads, and when it turns on

The schema exists to be useful. Every field is there because something reads it, and nothing is enforced
before its reader exists. This section names the readers.

## 10.1 The three teammate features

| Consumer | Reads from the Declaration | Attaches to what already exists | Turns on |
|---|---|---|---|
| **Verification** | `guarantees.checks[]`, `acceptance`, `ports.outputs[].check`, `changes.effects[]`; then the Verdict, and the suites a parent passed | `EvaluationSuite` (`symphony/evaluation/suite.py`), `GoalEvaluator.should_spot_check()` (`harness/goal/evaluation.py`) for judge calibration, `PackageReviewGate` (`symphony/flow/review.py`) for the static gate | one check at M1; suites, judges and quality at M3 |
| **RSI** | `identity.lineage`, Standing, and the suites a parent passed | joins RSI's own tree by `builder_ref` against `RsiTreeNode.parent_id` (`rsi/schema.py`) | M4 |
| **Model routing** | `needs.model`, `budget` | `ModelAllocator` (`agent_teams/models/allocator.py`) and `IntelliRouterModelClient`, neither of which reads anything about a capability today | M3 |

## 10.2 Verification is the largest consumer, and the point is simple

**Every check needs a target, and today there is none.** Nothing on any carrier says what a capability is
supposed to do: `ToolCard`'s entire behavioural surface is `parallel_safe`, `stateless` and `idempotent`,
and `SkillSpec` is a directory, a mode and an allow-list. So a test can only be written about a *task*,
which is why self-built tools pass their tasks and fail held-out tests of their own job.

A declaration is what turns a check into something that can be aimed. Three layers follow from it, and
they are different problems (see the Verify chapter): conformance is binary and static, correctness is
binary per case, and quality is a **rate over a window** that needs a declared minimum number of
observations before it means anything.

## 10.3 RSI: CC exposes, RSI chooses

CC stores and exposes information efficiently, and marks as optional whatever it cannot guarantee. It
does not choose for RSI. The split of who knows what is deliberate:

- **CC's side:** lineage, Standing, the suites a capsule passed, its quality rate, and the hash of
  everything involved. All of it readable, none of it interpreted.
- **RSI's side:** which parent to branch from, when to build, and what to try. CC never sets that policy.

A child must pass the parent's suites plus its own, which is the monotone rule. A merged block earns its
own quality record rather than inheriting one from its members.

## 10.4 Model routing: the first capability-level facts a router could use

Routing today keys on the endpoint (`IntelliRouterModelClient`, failover and retry across deployments)
and on the team member (`ModelAllocator`, round-robin, by-name or router-backed). Neither reads anything
about the capability being run. `needs.model` and `budget` are the first facts that would let a router
choose on what the work actually requires. CC supplies them and takes no view on the routing policy.

## 10.5 Why the integrations are small

Each one attaches to something that already exists, and none of them asks another team to change its
design. That is the test the schema has to pass: if an integration requires a teammate to rebuild, the
schema is asking for too much.
