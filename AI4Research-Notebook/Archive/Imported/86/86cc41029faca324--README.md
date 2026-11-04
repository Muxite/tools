---
title: GPU workload profiling presentation
status: exploratory research briefing
tags: [AI4Research, GPU, workload-profiling, presentation]
---

# GPU workload profiling presentation

This folder contains the source deck, its code-driven diagram and chart builders, the downloaded chart pack, and the checked PowerPoint export. The briefing supports pre-build research and experiment planning. It keeps the measured RTX 5070 Ti results scoped to that system and does not claim GB10 results or settled chip requirements.

## Build and review

- Generate and validate the deck with [`build/generate_workload_profiling.mjs`](build/generate_workload_profiling.mjs).
- Core diagrams are defined once in [`build/presentation_diagrams.mjs`](build/presentation_diagrams.mjs), laid out with the pinned ELK.js build dependency, and emitted as editable native PowerPoint objects by [`build/diagram_renderer.mjs`](build/diagram_renderer.mjs).
- The generator imports [`reference/AI4Research Workload Profiling source.pptx`](reference/AI4Research%20Workload%20Profiling%20source.pptx), replaces the core diagrams from the canonical graph definitions, and inserts six measured-results slides after the experiment plan. The results come from [`reference/GPU Profiling Chart Pack.html`](reference/GPU%20Profiling%20Chart%20Pack.html), which embeds 41 data-backed charts. The checked revision has 31 slides: [`output/AI4Research Workload Profiling - Dense 2026-10-19 r9.pptx`](output/AI4Research%20Workload%20Profiling%20-%20Dense%202026-10-19%20r9.pptx). Later runs receive the next numbered filename.
- Graph definitions live in [`build/presentation_diagrams.mjs`](build/presentation_diagrams.mjs); ELK places and routes them, and [`build/diagram_renderer.mjs`](build/diagram_renderer.mjs) emits editable PowerPoint objects. [`build/chart_pack.mjs`](build/chart_pack.mjs) reads the embedded chart data, and [`build/measured_results.mjs`](build/measured_results.mjs) renders selected results as editable shapes. Six chart slides follow source slide 15; the source map is now slide 31. Core diagrams correspond to source slides 2–7, 9–11, 17–20, and 22–24.
- The same validated PPTX is copied to the Desktop. Review all 31 slide renders and the montage in [`review/`](review/). The six new results pages cite the chart IDs, local setup, and applicable sample counts and limits.
- The source-deck snapshot makes regeneration deterministic. The research notes below remain the factual reference and carry the detailed claims, limits, and bibliography.

The build uses the workspace's bundled `@oai/artifact-tool` and Python runtime, plus the pinned `elkjs` and `web-worker` packages in `build/package-lock.json`. From this folder in PowerShell, run:

```powershell
$runtimeDeps = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies'
$env:RUNTIME_NODE_MODULES = Join-Path $runtimeDeps 'node\node_modules'
$env:RUNTIME_PYTHON = Join-Path $runtimeDeps 'python\python.exe'
npm ci --prefix 'build'
& (Join-Path $runtimeDeps 'node\bin\node.exe') 'build\generate_workload_profiling.mjs'
```

The script locates the installed Presentations skill and bundled Artifact Tool from the user profile or the runtime environment variables. It checks that its source deck and linked research files exist and records their SHA-256 hashes in `review/build-provenance.json`. It exports all 25 full-size PNGs and a montage, runs the package/layout/import finalizer, and only then copies the validated deck to the Desktop.

## Research references

- [Research index](../README.md)
- [GB10 and RTX 5070 Ti profiling plan](../gb10-profiling-plan.md)
- [Pre-build recommendations and questions](../prebuild-recommendations.md)
- [Evidence log and open questions](../evidence-and-next-questions.md)
- [Planner implications](../planner-implications.md)
- [Presentation outline and claims boundary](../presentation-outline.md)
- [Literature review](../literature/README.md)

- [Diagram patterns and tooling](diagram-tooling-and-patterns.md) captures what worked in the Capsule decks and documents the ELK.js-to-native-PowerPoint workflow.

The deck’s final source map also lists the primary vendor, provider, operating-system, and research references used on individual slides.
