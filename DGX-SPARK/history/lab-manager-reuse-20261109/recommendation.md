# Recommendation: discover the system by improving real inference

## Primary work and resulting demo

Use a broad inference-improvement campaign to discover the Lab Manager responsibilities and initial CC portfolio. Strata and the collected papers/tools supply mechanisms to investigate, not a fixed design to copy. Pursue a supported improvement on the pinned Granite target, iterate across useful method families and retain negative/inconclusive results. Link actual operations and friction to Manager requirements and build, profiling/test, tool, methodology and component capabilities.

The build CC is an explicit deliverable. Other CC boundaries and component forms emerge from useful work: snippets, binaries, modules, classes/functions or integration instructions where supported by actual builds/tests. A small set of profiling/test CCs should cover observed needs rather than one wrapper per tool. Methodology CCs preserve reusable experimental procedures and failure lessons.

Choose a few valuable capabilities for Friday after observing what works. A combined build/image/test/evidence story is a strong option, not a requirement to prioritize packaging over optimization. A temporary deterministic lab adapter can unblock investigation without replacing the other team's lab agent. Never claim real acceptance/execution it did not perform.

## Ownership

| Owner | Responsibility |
|---|---|
| Coding agent + coding sandbox | Source edits, dependencies, builds, instrumentation, unit checks, build records |
| Builder-side CC/tool | Source/model/release inspection, repeatable build invocation, evidence-bound export/handoff preparation |
| Lab Manager/external controller | Durable job/attempt identity, admission, status, cancellation/reconciliation, evidence registration |
| Other team's lab agent | Select/provision the test sandbox, qualify GPU/profilers, run permitted tests, report results |
| Test sandbox | Execute immutable engine image and test workload; no source rebuild or broad admin grants |
| External evidence store | Persist logs/events/artifacts and checksums outside the test sandbox's failure/deletion boundary |

## Strong reuse candidates, subject to observed needs

- [Buildx/Bake](dossiers/buildx.md) and [BuildKit](dossiers/buildkit.md) for image builds/cache/provenance.
- Existing CC finite-call/receipt/artifact mechanisms, or an explicitly separate trusted client where M1 lacks CCv2. Current CCv2 source is a scope-reset branch; do not import its whole branch or instructions into M1.
- [Docker SDK](dossiers/docker-sdk.md) and [Incus API](dossiers/incus.md) on the lab team's controlled side.
- [Nsight maintained reports](dossiers/nsys.md) before custom trace parsing.

## Defer unless they remove a demonstrated gap

Temporal, dstack, SkyPilot, Dagger and MLflow add substantial capabilities but also another runtime/service/integration model. They are researched alternatives, not prescribed campaign dependencies. Revisit them if actual work justifies their cost. dstack's inspected isolation guide explicitly assumes mutual trust and documents broad host-access paths; do not equate its Docker jobs with the intended Incus boundary.

## Branch/source warning

The remotely observed `ai4research-m1` release resolves to `7b63ffd59cfae400a22d4ead1fd4209ea7982132`; see [remote observation](context/m1-release-remote.json). The older local tag differed. Recheck remotely before the developer creates a private demo branch. No branch was created here. The historical general-purpose Lab Manager is reference material, not the immutable-engine lab implementation.

Current CCv2 image finite calls do not implicitly attach GPUs and use `--pull=never`. Do not promise a GPU benchmark CC merely by declaring a GPU requirement. A local Docker config ID also is not a remotely pullable registry manifest digest.
