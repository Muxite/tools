# Post-presentation evidence addendum

This supplements `evidence-register.md`; previous pinned technical sources remain applicable. Workshop directions are supplied design input, not proof of deployment.

| Record | Meaning and limit |
|---|---|
| November 6 workshop takeaways, supplied November 9 | New architecture framing: intent/ontology to contract, tool and component CCs, standalone engine release, separate lab management |
| Original attachment retained under notebook Sources/Prompts | Byte-identical source with SHA-256 in capture-manifest.json |
| Contract/release specimen replacing whole-engine CC framing | Illustrative proposed artifact, not a validated new schema or existing engine image |
| Containerized management agent outside experiment instance | Proposed failure separation; same-host/kernel/GPU faults still require external recovery |
| Workflow checkpoints | Persisted stage, attempt/generation, resource identities, deadlines and export records; not a live CUDA snapshot |
| Previous completed engine CC specimen | Historical only; does not define the revised product-release interface |
| CC schema a838b970 and prior local demonstrations | Unchanged existing implementation evidence; proposed Factory/lab integration not thereby implemented |

No Muse inference, crash injection, driver reset, Incus GPU qualification or performance experiment ran during this revision. SkyDiscover remains an exploration item from workshop notes, without an integration or performance claim.

## Later November 9 feasibility review

The user's follow-up asks for one Software Factory boundary and a feasibility comparison of a lab agent versus asynchronous API control. The current recommendation is a Manager API, durable job record and deterministic external executor. It is a proposal, not an implementation commitment. Optional diagnostic reasoning stays in Factory and submits follow-ups through the same API.

Incus provides asynchronous operation primitives ([REST API](https://linuxcontainers.org/incus/docs/main/rest-api/)), non-replayed live events requiring state re-fetch after reconnect ([events](https://linuxcontainers.org/incus/docs/main/events/)), and restricted TLS/project authorization ([authorization](https://linuxcontainers.org/incus/docs/main/authorization/)). These support infrastructure control but do not supply the proposed whole-experiment job semantics. Nested GPU/profiler behavior remains untested on the target.
