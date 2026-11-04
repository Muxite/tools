# jiuwenswarm: the openJiuwen product that already does part of what CC does

jiuwenswarm commit `02b37f47f`. The detailed evidence, with file:line, is in `../../merged/DERIVATION.md` stream D.
Here is what matters for the schema.

| jiuwenswarm today | What it shows | In the schema |
|---|---|---|
| **34 bundled skills:** 33 declare a name and description, 7 a version, 3 `allowed_tools`. None declares inputs, outputs, preconditions or effects. 25 ship scripts. 9 descriptions exceed 400 characters | real skills declare almost nothing, and `allowed_tools` is not enforced by the loader | imports enter as provisional; a person confirms effects; the importer proposes a short `summary` |
| **SkillPacks** (`kind: skillpack`): at least two members, referenced **by name**, plus a workflow graph. A disabled or missing member disables the pack (since `6f4eaa1b6`, 2026-09-17) | composites, and a member-state cascade, are already wanted | composites pin members **by hash**, so a member that *changed* is caught too; a withdrawn member suspends the composite |
| **Swarm Skills:** roles, workflow, `bind.md` limits, `dependencies.yaml` (skills and tools, `required`, explicit `[]`), read by a model at preflight; a Leader decides roles at run time | teams declare what they need, as prose | not admissible in v1, because the Leader plans (above the ceiling); dependencies imported as evidence |
| **Evolution:** a Teammate's experience is saved automatically and loaded next time; TTSE injects facts and tips with no approval dialog; Expert-Harness packages are hot-loaded after a person confirms | a capability's behaviour can change with no new version | **overlays**: hashed, and pinned per sprint or not loaded; a new overlay is a provisional revision |
| **RSI service:** hashes a published harness package; installation id from the hash; an active pointer with history and rollback; rollback refused while any RSI task runs | hash identity and a Standing-like pointer already exist | compatible: `decl_hash` and `body[]`; the librarian writes the pointer after a Verdict; the rollback guard becomes the concurrency rule |
| **Symphony evolution:** edge weights from `plan.outcome`; distilled skill packs | observation | `use_outcome` Findings; never admits anything |
