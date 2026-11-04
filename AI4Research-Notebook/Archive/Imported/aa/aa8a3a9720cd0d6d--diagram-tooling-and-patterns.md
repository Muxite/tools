---
title: Diagram patterns and authoring tools for workload profiling
status: working guide
tags: [presentation, diagrams, workload-profiling]
---

# Diagram patterns and authoring tools

## What the Capsule decks do well

The most useful references are `tundle/ai4research/capability-capsule/Capability Capsule - Presentation.pptx` and `Capability Capsule - Layer 2.pptx`. Their strongest process diagrams make the system legible quickly:

- Slide 10 of *Capability Capsule - Presentation*: five numbered stages, short action verbs, inputs and outputs in each node, and a bottom-line rule.
- Slide 14 of *Capability Capsule - Presentation*: the system is grouped into control, workflow and library lanes; a bracket labels the scope; repeated units are aligned to reveal the pattern.
- Slides 12 and 23 of *Capability Capsule - Layer 2*: the sequence is explicit, participant columns stay fixed, messages are labeled, and the caption states what the path proves.
- Across both decks: green, orange and purple distinguish responsibilities or decision types; color carries meaning, while labels remain readable in grayscale.

For workload profiling, reuse these patterns to show the lifecycle and its evidence: **authorize → launch one pinned capsule → observe host and task phases → join evidence by run ID → update the historical record**. Draw queues, fallbacks, shared resources, and branches as real paths; label arrows with the event or data transferred. Keep the measurement boundary visible, especially when telemetry is host-global.

## Tool comparison and recommendation

| Need | Tool | Best use | Limitation to plan for |
|---|---|---|---|
| Canonical graph source | [`build/presentation_diagrams.mjs`](build/presentation_diagrams.mjs) | Defines slide nodes, labels, semantic roles, groups, and edges once | The renderer owns visual styling and layout |
| Automatic graph geometry | [ELK.js](https://github.com/kieler/elkjs) | Layered placement and orthogonal edge routing | It computes layout; the deck renderer supplies shapes and styling |
| Editable PowerPoint output | Artifact Tool | Emits each node, label, routed edge, and arrowhead as a native slide object | Rendered slides still need visual collision and readability checks |
| Manual diagram editing | diagrams.net / draw.io | Useful for free-form team diagrams and visual exploration | Its PowerPoint integration inserts diagram imagery; it is not the final deck-generation path |

Recommended workflow for this deck:

1. Define each technical diagram in the shared graph source. Keep node labels concise, identify machine-dependent paths, and label important edges with the transferred data or decision.
2. Run the pinned ELK.js 0.12.0 build in layered mode with orthogonal routing to calculate positions and routes. `web-worker` 1.4.1 supplies ELK's Node worker; both exact versions live in `build/package-lock.json`. Fit each graph into a fixed slide region while preserving legible text sizes.
3. Render route segments, arrowheads, panel labels, and nodes as native PowerPoint objects through Artifact Tool. Place optional edge labels only where the routed path has clear space, so labels do not cover nodes. Use role-based colors for CPU/runtime, GPU, memory/links, measurement, records, and decisions.
4. Render and inspect every affected slide; fix crowded labels, crossed edges, and unclear flow before exporting the final deck.

The deck uses ELK.js for graph placement and routing, then Artifact Tool for native PowerPoint output. This keeps one canonical graph definition in code while allowing presenters to move or restyle individual slide objects. The renderer replaces only the specified core-diagram slides; evidence tables and other slide content remain intact. draw.io remains an optional visual exploration tool; its exports are not used as final slide objects.

Measured-result pages use the same code-generated workflow. [`reference/GPU Profiling Chart Pack.html`](reference/GPU%20Profiling%20Chart%20Pack.html) embeds chart specifications and plotted values; [`build/chart_pack.mjs`](build/chart_pack.mjs) parses it, and [`build/measured_results.mjs`](build/measured_results.mjs) renders a selected subset as editable bars and a resource-signature heatmap. Each page records its chart ID, machine scope, measurement caveat, and source table in its footer or speaker notes. The remaining embedded charts stay available in the reference HTML instead of being copied wholesale into the briefing.

## Example source

The profiling runner, GPU hierarchy, memory models, observability layers, and other diagrams are specified in [`build/presentation_diagrams.mjs`](build/presentation_diagrams.mjs). These describe proposed processes and research plans; they do not claim that the runner or AI4Research integration is implemented.

## Sources

- Local examples: the two Capability Capsule presentations above; inspected slides are rendered in [`review/capsule-references/`](review/capsule-references/).
- ELK.js describes itself as a layout engine for directed node-link diagrams with explicit ports, with no rendering or styling: [ELK.js project](https://github.com/kieler/elkjs).
- draw.io documents its PowerPoint integration and regenerated diagram imagery: [Embed diagrams in PowerPoint](https://www.drawio.com/docs/integrations/microsoft/powerpoint-diagrams/).
