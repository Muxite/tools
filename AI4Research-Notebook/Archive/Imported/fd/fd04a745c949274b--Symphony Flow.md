**The central finding of 2026-09-23: openJiuwen already implements almost exactly the merge algorithm we
were about to design.** It appears in none of the `kb/repos/` notes. Verified in source at agent-core
`e23806c1`, under `openjiuwen/symphony/flow/`.

## What is already built

| Proposed in [[Overlap and Merge]] | Already built | Where |
|---|---|---|
| a capsule holds a set of capabilities and its own DAG | `ExperienceRecipe.combination_structure` — `{type, direction, nodes{}, edges[{source,target,relation}], loop_guards}`; `capability_ids` returns the node set; `topological_order()` orders the internal DAG | `flow/models.py:118`; `flow/distill.py:355` |
| n = 1 is the degenerate case | the structure is a graph; one node is a valid graph | `flow/models.py` |
| merge when the pair recurs **and** is high quality | `qualified_edges(records, min_edge_support, min_edge_success_rate=0.8)` — an A→B edge qualifies only on **both** enough occurrences and a high enough success rate | `flow/distill.py:195` |
| a similar structure recurring, not just a pair | `group_by_structure()` + `structure_signature()` group whole trajectories by their qualified-edge signature | `flow/distill.py:216`, `:188` |
| **failing parts are never merged** | grouping key = a trajectory's **successful** edges ∩ globally qualified edges. The docstring is explicit: failing edges contribute to edge-quality statistics only and never participate in grouping | `flow/engine.py` `distill()` docstring |
| the block is graded as a block | `resolve_status_grade(...)` → `grade ∈ {candidate, verified}` with `min_successes_verified` and `min_pack_success_rate_verified` | `flow/distill.py:402`, `:418` |
| A, B and A-B coexist as versioned items | immutable `recipes/<id>/vN.json` + a `current` pointer; `content_identity()` hashes structure but **not counts**, so a new version appears only on real change | `flow/store.py:35`; `flow/models.py:172` |
| the merged block is gated before use | `PackageReviewGate.review_static()` — ten deterministic checks (structure, dependencies, code safety, secrets, artifact paths, integrity, naming, materials, permissions, licence) → `approved｜rejected｜needs_human_review`, then an isolated `LLMPackageReviewAgent` with no tools and no filesystem | `flow/review.py:144`, `:62` |
| packaged and installable | `CapabilityPackager.build_package()` → `package_id = "cap-" + sha256[:12]`, `integrity` hash, `verify_package_integrity()`; `SkillAdapter`/`SkillPackAdapter` render it | `flow/packager.py:30`, `:78`; `flow/render.py` |

There is even a `break_cycles()` pass (`distill.py:255`) and port normalisation
(`_normalize_capability_ports`, `distill.py:123`).

The distill docstring, worth quoting directly: *批处理蒸馏：全局边统计 → 结构分组 → 叙事 → 版本化落盘* —
batch distillation: global edge statistics → structural grouping → narrative → versioned persistence.

## What is missing, and it is exactly the schema

| Gap in `symphony/flow` | What CC adds |
|---|---|
| a recipe has **no declaration** — no ports, effects, preconditions or guarantees on the block | the merged capsule gets a Declaration derived from its members: ports from the boundary of the internal DAG, `changes` covering the union of members', `needs` the union minus what members satisfy internally |
| **no lineage** — A-B is not linked back to A and B | `identity.lineage`: `parent` / `co_parents` = A and B, `relation: composes`, `builder` |
| grade is decided by **observed success counts only** — no held-out test of the block | A-B must pass the **union of its members' suites** plus its own (the schema's existing monotone rule). See [[Quality Not Just Correctness]] |
| members are referenced by id, **not pinned by hash** | `members[] {role, decl_hash}` pins internals at merge; §4.11's unpin-with-a-purpose is the only exception. See [[Versioning and A-prime]] |
| nothing checks the block's **declared** effects against observed ones | the admission gate CC already specifies |

## Why it matters

This is the strongest answer available to (g) feasibility and to "build onto openJiuwen": **the hard,
stateful part is built and running; CC is the contract layer over it.** It led the feasibility argument in the
presentation. For M1 it is **not used**: merge is back-burnered, and `flow` is where M4 starts
([[Layer 2 Presentation]]).

**Also a correction to our own notes:** `SkillManifestParser`
(`symphony/shared/fingerprint/parser.py:129`) already reads `inputs`/`outputs` from `SKILL.md`
frontmatter — only `SkillUseRail` is blind to them. And the Symphony README's status table is stale:
retrieval is implemented, not 待迁入. Trust the code, not the README.

Related: [[openJiuwen Landscape]], [[What openJiuwen Is Missing]], [[Overlap and Merge]],
[[Where It Attaches]].
