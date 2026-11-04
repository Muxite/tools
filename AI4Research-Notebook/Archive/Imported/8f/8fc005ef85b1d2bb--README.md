# AI4Research workload profiling deck

Final file: `AI4Research Workload Profiling.pptx` (12 main slides, 22 appendix slides, about 13 minutes of core time).
Status: an early, exploratory briefing. All measured numbers come from an imported report from another machine (RTX 5070 Ti, 140 runs and 1,760 container starts, 2 to 12 repeats per point, not audited). There are no GB10 results.

## Rebuild

From this folder (Python 3.12, matplotlib, `tundlekit` installed; PowerPoint closed):

```
python figs1.py && python figs1b.py && python figs1c.py && python figs1d.py
python build_spec.py
tundlekit deck lint deck.json
tundlekit deck build deck.json -o "AI4Research Workload Profiling.pptx"
tundlekit render office "<abs path to pptx>" -o "<abs path>/review" --backend powerpoint
```

## Files

| File | What it is |
|---|---|
| `build_spec.py` | Writes `deck.json`: main order, new slides, tweaks. Imports `build_spec_base.py` |
| `build_spec_base.py` | Slide content reused from the earlier 30-slide version |
| `figs1.py`, `figs1b.py`, `figs1c.py`, `figs1d.py`, `figlib.py`, `palette_local.py` | Figure scripts (diagrams and charts) and drawing helpers. Output goes to `figures/` as PNG |
| `planner_baselines.py` | Reproduces the toy planner numbers (40, 26.5, 22.9, 21.0) from the measured pair slowdowns |
| `future-path.md` | Open decisions, schema asks and missing evidence |
| `review/` | Rendered slide images and speaker notes from the last build |
| `reviews/` | Adversarial reviews, mock presentations and the diagram check (history) |
| `old/` | Earlier decks and spec copies |

## Notes

- Diagrams are PNG images made by the scripts, not editable PowerPoint shapes. To change one, edit its script and rebuild.
- Data source: `../../sources/2026-10-16-shared-gpu/report.md` and `chart-data.json`.
- MuxFlow slide: read from the full paper (arXiv 2303.13803). Its production utilization gain (26% to 76%) excludes the predictor and matching; the paper names the company only as CompanyX.
