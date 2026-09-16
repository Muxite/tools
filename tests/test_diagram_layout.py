"""MANIFEST §4.2 Layout: ranks, back edges, rank ordering along the main axis, no overlaps, canvas,
cross-axis spec order, determinism, box width vs label length."""
import itertools
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers_diagram_text import boxes, diagram, inside, node_group, overlap, parse_svg, spec_of, texts  # noqa: E402


def render(spec):
    return diagram("diagram_render", spec=spec)


def ranks(res):
    return {k: v["rank"] for k, v in res["nodes"].items()}


# §4.2 rank = longest path from a source
def test_chain_ranks():
    res = render(spec_of([("a", "A"), ("b", "B"), ("c", "C")], [("a", "b"), ("b", "c")]))
    assert ranks(res) == {"a": 0, "b": 1, "c": 2}


def test_longest_path_rank():
    res = render(spec_of([("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")],
                         [("a", "d"), ("a", "b"), ("b", "c"), ("c", "d")]))
    assert ranks(res) == {"a": 0, "b": 1, "c": 2, "d": 3}


def test_all_sources_rank_zero():
    res = render(spec_of([("a", "A"), ("b", "B"), ("c", "C")], [("a", "c"), ("b", "c")]))
    assert ranks(res) == {"a": 0, "b": 0, "c": 1}


# §4.2 back edges (DFS from nodes in spec order) are ignored for ranking
def test_two_cycle_back_edge_ignored():
    res = render(spec_of([("a", "A"), ("b", "B")], [("a", "b"), ("b", "a")]))
    assert ranks(res) == {"a": 0, "b": 1}


def _assert_main_axis(res, direction):
    b = boxes(res)
    r = ranks(res)
    lo, hi = (0, 2) if direction == "LR" else (1, 3)
    for m, n in itertools.permutations(b, 2):
        if r[n] == r[m] + 1:
            assert b[n][lo] >= b[m][hi], f"{n} (rank {r[n]}) not beyond {m} (rank {r[m]})"


BRANCHY = spec_of(
    [("src", "source"), ("x1", "first branch with a longer label"), ("x2", "second"),
     ("x3", "third"), ("y", "merge point"), ("z", "sink")],
    [("src", "x1"), ("src", "x2"), ("src", "x3"), ("x1", "y"), ("x2", "y"), ("x3", "z"), ("y", "z")])


# §4.2 LR: every node of rank r+1 lies right of every node of rank r
def test_lr_rank_ordering():
    _assert_main_axis(render(dict(BRANCHY, direction="LR")), "LR")


# §4.2 no overlaps, everything inside the canvas
@pytest.mark.parametrize("direction", ["LR", "TB"])
def test_no_overlap_and_inside_canvas(direction):
    res = render(dict(BRANCHY, direction=direction, note="a fairly long note under the diagram"))
    b = boxes(res)
    canvas = (0, 0, res["width"], res["height"])
    for k, box in b.items():
        assert inside(box, canvas), k
    for m, n in itertools.combinations(b, 2):
        assert not overlap(b[m], b[n]), (m, n)


def test_wide_fan_out_no_overlap():
    nodes = [("root", "root")] + [(f"n{i}", f"child number {i} " + "x" * (i * 3)) for i in range(8)]
    edges = [("root", f"n{i}") for i in range(8)]
    res = render(spec_of(nodes, edges))
    b = boxes(res)
    for m, n in itertools.combinations(b, 2):
        assert not overlap(b[m], b[n]), (m, n)


# §4.2 same-rank nodes keep spec order along the cross axis (no crossings to reduce here)
def test_unconnected_nodes_keep_spec_order_lr():
    res = render(spec_of([("c", "C"), ("a", "A"), ("b", "B")]))
    y = {k: v["y"] for k, v in res["nodes"].items()}
    assert y["c"] < y["a"] < y["b"]


# §4.2 deterministic: byte-identical SVG
def test_deterministic_svg():
    spec = dict(BRANCHY, title="t", note="n", groups=[{"id": "g", "label": "G", "nodes": ["x1", "x2"]}])
    assert render(spec)["svg"] == render(spec)["svg"]


# §4.2 box width grows with the longest label line
def test_width_grows_with_label():
    res = render(spec_of([("short", "abcd"), ("long", "a" * 40)]))
    assert res["nodes"]["long"]["w"] > res["nodes"]["short"]["w"]


def test_width_follows_longest_line_of_multiline_label():
    res = render(spec_of([("one", "ab"), ("two", "ab\n" + "m" * 40)]))
    assert res["nodes"]["two"]["w"] > res["nodes"]["one"]["w"]


# §4.2 lines are never truncated
def test_long_label_not_truncated():
    label = "an intentionally very long label that must appear in full, never cut short"
    res = render(spec_of([("a", label)]))
    assert label in texts(node_group(parse_svg(res["svg"]), "a"))
