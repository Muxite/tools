ROLE ui-cc (preview port 5181, branch ui/cc-views, worktree ~/predemo-spark/wt-ui-cc)

Build a first-class "Capability Capsules" tab with its own nav entry. Add CC tags/chips wherever a CC appears in runs, the timeline or the graph, each linking to the CC view. Hold it to a high standard.

For each CC:
- **Header:** name, what it builds (component/subcomponent), kind (builder), version, sealed digest with a verified badge, pinned file hashes.
- **Sections:**
  - Method summary from GUIDE/METHOD.
  - Ontology slice from ONTOLOGY.yaml (component, capability, regions, observation points, quantities), linked to the owner ontology files.
  - Acceptance criteria and tests.
  - Verifier: what run.py checks, plus the latest verify receipt if one exists.
  - Samples and helpers, in a code viewer.
  - Source map: which llama.cpp files and functions it touches, and which Strata mechanism it was reverse-engineered from.
  - Artifacts produced in runs (diffs, build records, receipts), linking into the run replay.
  - Results: per-arm measurement deltas when available.
- **Contract:** which contract clauses it serves.

**Catalog overview:** a grid of the 5 star CCs, marked starred, plus the factory/support CCs in a secondary section.

**Backend:** add endpoints if needed (/api/factory/capsules, /api/factory/capsules/{name}/file?path=), with path confinement and pytest tests. Reuse factory capsules.py (capsule_rows) where possible.
