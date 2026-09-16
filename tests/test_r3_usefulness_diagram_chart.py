"""MANIFEST §14.6 diagram and chart: fixed ranks, wrapped rows/columns, the pymupdf PNG fallback, and chart_bar
multi-line labels, value axis and highlight_color."""
import itertools
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers_diagram_text import boxes, diagram, inside, overlap, parse_svg, spec_of, tag  # noqa: E402

import helpers_deck as hd  # noqa: E402

PIPELINE = [("intent", "compile intent", "intent", "model"), ("bind", "bind capsules", "binding", "code"),
            ("freeze", "freeze", "freeze", "code"), ("dispatch", "dispatch", "dispatch", "code"),
            ("gates", "gates", "gates", "code")]
CHAIN = [(a[0], b[0]) for a, b in zip(PIPELINE, PIPELINE[1:])]


def render(spec, **kw):
    return diagram("diagram_render", spec=spec, **kw)


def ranks(res):
    return {k: v["rank"] for k, v in res["nodes"].items()}


def with_rank(nodes, **fixed):
    out = []
    for n in nodes:
        d = {"id": n[0], "label": n[1], "stage": n[2], "actor": n[3]}
        if n[0] in fixed:
            d["rank"] = fixed[n[0]]
        out.append(d)
    return out


def assert_valid_layout(res):
    b = boxes(res)
    canvas = (0, 0, res["width"], res["height"])
    for k, bx in b.items():
        assert inside(bx, canvas), k
    for m, n in itertools.combinations(b, 2):
        assert not overlap(b[m], b[n]), (m, n)


# ====================================================================== rank
def test_fixed_rank_is_kept():
    """§14.6: a node's `rank` fixes its rank; the other nodes keep their ranks and order."""
    res = render(spec_of(with_rank(PIPELINE[:3], freeze=4), CHAIN[:2]))
    assert ranks(res) == {"intent": 0, "bind": 1, "freeze": 4}
    b = boxes(res)
    assert b["intent"][2] <= b["bind"][0]
    assert b["bind"][2] <= b["freeze"][0]
    assert_valid_layout(res)


def test_fixed_rank_unconnected_node():
    """§14.6: an unconnected node with rank 2 sits in rank 2, right of rank 1 (LR)."""
    nodes = with_rank(PIPELINE[:2], ) + [{"id": "ledger", "label": "ledger", "actor": "record", "rank": 2}]
    res = render(spec_of(nodes, CHAIN[:1]))
    assert ranks(res)["ledger"] == 2
    b = boxes(res)
    assert b["ledger"][0] >= b["bind"][2]


def test_backward_edge_against_fixed_ranks():
    """§14.6: an edge going backward against fixed ranks is drawn (as a back edge); ranks stay fixed."""
    nodes = [{"id": "retire", "label": "retire", "rank": 2}, {"id": "admit", "label": "admit", "rank": 0},
             {"id": "use", "label": "use", "rank": 1}]
    res = render(spec_of(nodes, [("retire", "admit"), ("admit", "use")]))
    assert ranks(res) == {"retire": 2, "admit": 0, "use": 1}
    b = boxes(res)
    assert b["admit"][2] <= b["use"][0] and b["use"][2] <= b["retire"][0]
    root = parse_svg(res["svg"])
    edges = [(g.get("data-from"), g.get("data-to")) for g in root.iter()
             if tag(g) == "g" and "edge" in (g.get("class") or "").split()]
    assert ("retire", "admit") in edges
    assert_valid_layout(res)


@pytest.mark.parametrize("bad", [-1, 1.5, "2", True])
def test_bad_rank_is_a_problem(bad):
    """§14.6: rank is an integer >= 0."""
    res = diagram("diagram_validate", spec=spec_of([{"id": "a", "label": "A", "rank": bad}]))
    assert res["ok"] is False
    assert any("nodes[0].rank" in p for p in res["problems"])


# ====================================================================== wrap
def test_wrap_lr_rows():
    """§14.6: LR with wrap 2 lays ranks out in rows of 2; row k+1 below row k; x resets per row."""
    res = render(spec_of([n[:2] for n in PIPELINE], CHAIN, wrap=2))
    b = boxes(res)
    r = ranks(res)
    assert r == {"intent": 0, "bind": 1, "freeze": 2, "dispatch": 3, "gates": 4}
    rows = [["intent", "bind"], ["freeze", "dispatch"], ["gates"]]
    for upper, lower in zip(rows, rows[1:]):
        assert max(b[n][3] for n in upper) <= min(b[n][1] for n in lower)
    for row in rows[:2]:
        assert b[row[0]][2] <= b[row[1]][0]            # rank order within a row
    assert b["freeze"][0] < b["bind"][0]                # x resets
    assert b["gates"][0] < b["dispatch"][0]
    assert_valid_layout(res)


def test_wrap_tb_columns():
    """§14.6: TB with wrap 2 wraps columns; column k+1 right of column k; y resets."""
    res = render(spec_of([n[:2] for n in PIPELINE], CHAIN, direction="TB", wrap=2))
    b = boxes(res)
    cols = [["intent", "bind"], ["freeze", "dispatch"], ["gates"]]
    for left, right in zip(cols, cols[1:]):
        assert max(b[n][2] for n in left) <= min(b[n][0] for n in right)
    for col in cols[:2]:
        assert b[col[0]][3] <= b[col[1]][1]
    assert b["freeze"][1] < b["bind"][1]
    assert_valid_layout(res)


def test_wrap_with_legend_and_note_stays_inside():
    """§14.6: wrapped layouts still keep boxes apart and inside the canvas, with a legend and a note."""
    res = render(spec_of(PIPELINE, CHAIN, wrap=3, note="(illustrative)", legend=True))
    assert_valid_layout(res)


@pytest.mark.parametrize("bad", [0, -2, 1.5, "2"])
def test_bad_wrap_is_a_problem(bad):
    """§14.6: wrap is an integer >= 1."""
    res = diagram("diagram_validate", spec=spec_of([("a", "A")], wrap=bad))
    assert res["ok"] is False
    assert any("wrap" in p for p in res["problems"])


# ====================================================================== PNG fallback
def _only_pymupdf(monkeypatch, tmp_path):
    pytest.importorskip("pymupdf")
    for p in ("C:/Program Files/Inkscape", "C:/Program Files (x86)/Inkscape",
              "/Applications/Inkscape.app", "/usr/bin/inkscape", "/usr/bin/rsvg-convert",
              "/opt/homebrew/bin/rsvg-convert", "/usr/local/bin/rsvg-convert"):
        if Path(p).exists():
            pytest.skip(f"a converter is installed at a fixed location: {p}")
    monkeypatch.setitem(sys.modules, "cairosvg", None)
    monkeypatch.setenv("PATH", "")
    monkeypatch.chdir(tmp_path)


def test_png_fallback_pymupdf(monkeypatch, tmp_path):
    """§14.6: with no other converter, pymupdf converts the SVG."""
    _only_pymupdf(monkeypatch, tmp_path)
    out, png = tmp_path / "pipeline.svg", tmp_path / "pipeline.png"
    res = render(spec_of(PIPELINE, CHAIN, title="Capsule build path"), out=str(out), png=str(png))
    assert res["png"] == str(png)
    data = png.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    import pymupdf

    pix = pymupdf.Pixmap(str(png))
    assert pix.width / pix.height == pytest.approx(res["width"] / res["height"], rel=0.03)


def test_render_backends_reports_pymupdf(monkeypatch, tmp_path):
    """§14.6: render_backends.svg_to_png reports `pymupdf` when it is the only converter."""
    _only_pymupdf(monkeypatch, tmp_path)
    import importlib

    importlib.import_module("tundlekit.render")
    from tundlekit import registry

    assert registry.call("render_backends", {})["svg_to_png"] == "pymupdf"


def test_png_fallback_cli(monkeypatch, tmp_path, capsys):
    """§14.6 through the CLI."""
    import json

    _only_pymupdf(monkeypatch, tmp_path)
    (tmp_path / "s.json").write_text(json.dumps(spec_of(PIPELINE, CHAIN)), encoding="utf-8")
    from tundlekit import cli

    capsys.readouterr()
    code = cli.main(["diagram", "render", "s.json", "-o", "s.svg", "--png", "s.png", "--json"])
    out = capsys.readouterr().out
    assert code == 0, out
    assert (tmp_path / "s.png").read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


# ====================================================================== chart_bar
def tspan_texts(root):
    return [[(t.text or "").strip() for t in el if tag(t) == "tspan"] for el in root.iter(f"{{{hd.SVG_NS}}}text")]


@pytest.mark.parametrize("orientation", ["horizontal", "vertical"])
def test_chart_newline_label_tspans(orientation):
    """§14.6: `\\n` in a category label makes separate <tspan> lines."""
    _, root = hd.chart_svg(spec={"categories": ["kept tools\n(held-out)", "passed"], "values": [222, 7],
                                 "orientation": orientation})
    groups = tspan_texts(root)
    want = ["kept tools", "(held-out)"]
    assert any(g[i:i + 2] == want for g in groups for i in range(len(g))), groups


def axis_groups(root):
    return hd.find_class(root, "g", "axis")


def test_chart_axis():
    """§14.6: `axis: true` draws a value axis with gridlines and tick labels in <g class="axis">."""
    _, root = hd.chart_svg(spec={"categories": ["AI Scientist-v2", "Kosmos", "Arbor"], "values": [57, 57.9, 80],
                                 "axis": True, "unit": "%"})
    g = axis_groups(root)
    assert len(g) == 1
    lines = [e for e in g[0].iter() if tag(e) in ("line", "path", "polyline")]
    assert len(lines) >= 2
    ticks = []
    for e in g[0].iter(f"{{{hd.SVG_NS}}}text"):
        t = hd.text_of(e).strip().rstrip("%").strip()
        try:
            ticks.append(float(t))
        except ValueError:
            pass
    assert len(ticks) >= 2
    assert all(0 <= t <= 80 * 1.5 for t in ticks)


def test_chart_no_axis_by_default():
    """§14.6: without axis there is no axis group."""
    _, root = hd.chart_svg(spec={"categories": ["a", "b"], "values": [1, 2]})
    assert axis_groups(root) == []


@pytest.mark.parametrize("key,colour", [("failed", "#d55e00"), ("library", "#8c5a2b"), ("skipped", "#bdbdbd")])
def test_chart_highlight_color(key, colour):
    """§14.6: highlight_color accepts STAGE or OUTCOME keys."""
    _, root = hd.chart_svg(spec={"categories": ["kept", "failed"], "values": [222, 215], "highlight": 1,
                                 "highlight_color": key})
    bars = hd.find_class(root, "rect", "bar")
    assert hd.fill_of(bars[1]) == colour
    assert hd.fill_of(bars[0]) == "#9a9a9a"


def test_chart_highlight_color_overrides_stage():
    """§14.6: highlight_color overrides stage for the highlight."""
    _, root = hd.chart_svg(spec={"categories": ["kept", "failed"], "values": [222, 215], "highlight": "failed",
                                 "stage": "intent", "highlight_color": "failed"})
    assert hd.fill_of(hd.find_class(root, "rect", "bar")[1]) == "#d55e00"


def test_chart_bad_highlight_color():
    """§14.6: an unknown highlight_color is a validation problem."""
    with pytest.raises(hd.ToolError()):
        hd.call("chart_bar", spec={"categories": ["a"], "values": [1], "highlight": 0, "highlight_color": "red"})
