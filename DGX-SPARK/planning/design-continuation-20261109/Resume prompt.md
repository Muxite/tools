# Resume prompt

Continue the Muse Spark Open / DGX Spark CC and inference-lab **design**, using Start here.md and Design continuation.md in this handoff. Do not restart the research or assume the proposed lab exists.

Preserve contract != CC != image, the two CC roles, immutable testing and Factory-owned evidence. All Software Factory components are inside one boundary; Lab Manager is the gateway to an external executor and Incus. Current input label is “System ontology + plaintext*”; the ontology representation is unknown at time of writing.

The latest recommendation is an asynchronous Manager API with durable jobs and a deterministic worker, with optional reasoning in Factory. It is not yet an approved implementation choice. One builder can have many jobs outstanding; one Spark serializes scored/profiling GPU work.

Start by drafting one concrete release/job/result example and an end-to-end sequence covering normal completion, failure, cancellation and evidence export. Identify what can use existing CC/Factory interfaces and what remains unknown. Then propose the smallest first implementation slice and its qualification criteria. Keep implementation separate until requested. Update the notebook and revise slides only where the design discussion changes them.
