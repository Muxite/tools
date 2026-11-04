# Evidence and claim boundaries

## Paper2Agent reported results

Primary source: Miao et al., *Paper2Agent*, Nature (2026), https://www.nature.com/articles/s41586-026-11044-y. Repository snapshot: https://github.com/jmiao24/Paper2Agent/tree/8c2d059165ef8cdcb70dbea76655b9c2b55b38e6.

- AlphaGenome benchmark: 15 novel questions, five runs. Paper2Agent mean 100.0% (±0.0) versus Claude + repository 78.7% (±4.4). The deck's bar labels show only means; notes carry dispersion.
- Tutorial-derived biology benchmark: 300 questions. Paper2Agent with Sonnet 4 91.2% (±1.6) versus Claude Code direct repository access with Sonnet 4 80.3% (±2.3), reported P<0.0001.
- Corpus automation: 74 of 100 papers were agentified, with 599 proposed tools; 593 passed automated validation. This pass criterion is not a scientific-quality or adoption measure.
- Generalization: 42 execution tasks drawn from 10 non-biology computational papers scored 98.1% (±0.8) across five runs.
- Resource layer: on 100 synthesis questions across 26 data/discovery papers, Paper2Agent scored 89.0% (±3.1) versus browser-use baseline 82.0% (±3.8), with reported 34× lower cost and 15× faster execution.

## What those results do not establish

The paper does not evaluate whether any research paper is strategically valuable to AI4Research or the company, whether AI4Research can generate a suitable PRD/design and implement a product-level change, or whether AI4Research improves before versus after integration. These are the questions a pilot must measure.

## Integration proposal

The proposed path from Paper2Agent output to an AI4Research feature, Capability Capsule, optional container, and evaluation/admission is a design hypothesis. Check the Capsule fields against `AI4Research_private_planning/ai4r_muk/outputs/m1-core-review-2026-10-14/design-package-compact/` before treating them as an implementation contract. Containerization is optional, and its value depends on reproducibility/isolation needs and operational cost.
