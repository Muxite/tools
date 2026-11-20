ROLE ui-data (preview port 5182, branch ui/data-views, worktree ~/predemo-spark/wt-ui-data)

Build reusable data viewers used throughout Factory runs:
- **JSON/YAML multi-view:**
  - **Views:**
    - readable: key/value cards with sensible labels
    - tree: collapsible, with search
    - table: for arrays of objects, sortable
    - raw: syntax highlighted, with a copy button
  - **Metadata:** each view shows a digest badge and the file size.
  - **YAML parsing:** use a YAML parser already in node_modules if one is present; otherwise write a small safe parser. Never eval.
- **Graph view:**
  - **Detect graph-shaped data:**
    - the task graph (taskgraph to_json)
    - ontology relations (ONTOLOGY.yaml, or the owner ontology .mmd)
    - contract, then tasks, then CCs
  - **Render it interactively:** pan/zoom, click a node for details, highlight replay progress.
  - **Library:** check node_modules for an existing graph or diagram library (reactflow, dagre, cytoscape, mermaid). If none exists, write a clean SVG layered layout.
  - **Raw:** keep the raw view available.
- **Diff viewer:** side-by-side and unified, per-file collapse, +/- stats, a file tree.
- **Log/terminal viewer:** virtualized, with filtering, severity colouring and timestamps.

Wire these into the existing panels (contract, ontology, task graph, artifacts, diffs, terminal). Add tests for the parsers and the graph detection.
