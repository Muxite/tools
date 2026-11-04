# High-resolution PNGs of all the decks, diagrams and figures (2026-09-25)

Everything here is derived from its source, so edit the source and export again.

| Folder | What | Size |
|---|---|---|
| `1-presented-2026-09-23/` | Capability Capsule, exactly as presented on 23 September (26 slides) | 3200×1800 |
| `1b-post-presentation/` | the post-presentation deck, a-to-g order (45 slides) | 3200×1800 |
| `1c-post-presentation-part-a/` | section a of the post deck (4 slides) | 3200×1800 |
| `2-layer-2/` | layer 2: 19 core slides, then Reference A and Appendices B and C (78 slides) | 3200×1800 |
| `3-architecture-plan/` | presentation 3, the architect plan for 25 September to 31 October (12 slides) | 3200×1800 |
| `diagrams/` | the team docs' Mermaid diagrams (`M1-DESIGN-*`, `SCHEMA-EXPLAINED-1`); the M1 map and the big-picture (M4) map, each in its expanded and blackbox views | up to 6400×14000 |
| `figures/` | the standalone figures behind the slides, including the schema figures; these are sharper than a slide export | as drawn |

**Sources:**

- The decks are in `capsule-openjiuwen/merged/`, and presentation 3 is in `merged/pres3/`. The slides were exported
  through PowerPoint.
- The team diagrams are in `capsule-openjiuwen/team/` (render them with `render_mermaid.py`).
- The maps are in `merged/figures/big-picture/` (`m1_picture.py`, `big_picture.py`), captured through Edge headless.

This folder is kept out of the tundle on purpose: about 80 MB of images would bloat its git history.
