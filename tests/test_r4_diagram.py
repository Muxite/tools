"""MANIFEST §16.7 diagram parts: group-aware wrap, the pymupdf PNG fallback keeping arrowheads and dashes,
Mermaid `%% rank` / `%% wrap` round trip, and integral floats. Layout invariants from §4.2/§14.6 still hold.
"""
from __future__ import annotations

import itertools

import pytest

import helpers_r4m as h


def render(spec, **kw):
    return h.call("diagram_render", spec=spec, **kw)


def rows_of(res, ids):
    b = h.boxes(res)
    return [b[i] for i in ids]


# ------------------------------------------------------------------------------------ group-aware wrap
def test_wrap_never_splits_a_group():
    """§16.7: ranks 2 and 3 would fall in different rows with wrap 3; as 1 group they share a row, and the
    group frame holds both members."""
    nodes, edges = h.chain(6)
    res = render({"nodes": nodes, "edges": edges, "wrap": 3,
                  "groups": [{"id": "g", "label": "G", "nodes": ["a2", "a3"]}]})
    b = h.boxes(res)
    assert h.same_band(b["a2"], b["a3"])
    assert b["a2"][2] <= b["a3"][0]
    frame = h.group_frames(res["svg"])["g"]
    for m in ("a2", "a3"):
        x0, y0, x1, y1 = b[m]
        assert frame[0] <= x0 and frame[1] <= y0 and x1 <= frame[2] and y1 <= frame[3]
    h.assert_layout_ok(res)


def test_group_wider_than_wrap_gets_own_row():
    """§16.7: a group spanning 4 ranks with wrap 2 gets a row of its own (extended), shared with no other node."""
    nodes, edges = h.chain(6)
    members = ["a1", "a2", "a3", "a4"]
    res = render({"nodes": nodes, "edges": edges, "wrap": 2,
                  "groups": [{"id": "wide", "label": "wide", "nodes": members}]})
    b = h.boxes(res)
    for m, n in itertools.combinations(members, 2):
        assert h.same_band(b[m], b[n]), (m, n)
    for outside in ("a0", "a5"):
        assert not any(h.same_band(b[outside], b[m]) for m in members), outside
    h.assert_layout_ok(res)


def test_group_frames_never_overlap_in_wrapped_layout():
    """§16.7: 2 groups in a wrapped chain: frames don't overlap and each contains its members."""
    nodes, edges = h.chain(7)
    groups = [{"id": "g1", "label": "first", "nodes": ["a1", "a2"]},
              {"id": "g2", "label": "second", "nodes": ["a3", "a4", "a5"]}]
    res = render({"nodes": nodes, "edges": edges, "wrap": 3, "groups": groups})
    frames = h.group_frames(res["svg"])
    assert not h.overlap(frames["g1"], frames["g2"])
    b = h.boxes(res)
    assert h.same_band(b["a3"], b["a5"])
    assert h.same_band(b["a1"], b["a2"])


def test_interleaved_groups_do_not_overlap():
    """§16.7: members of 2 groups in the same rank: frames never overlap; when the layout had to move a group,
    a warning names it."""
    nodes = [{"id": i, "label": i} for i in ("src", "x1", "y1", "x2")]
    edges = [{"from": "src", "to": n} for n in ("x1", "y1", "x2")]
    groups = [{"id": "g1", "label": "one", "nodes": ["x1", "x2"]}, {"id": "g2", "label": "two", "nodes": ["y1"]}]
    res = render({"nodes": nodes, "edges": edges, "groups": groups})
    frames = h.group_frames(res["svg"])
    assert not h.overlap(frames["g1"], frames["g2"])
    for w in res["warnings"]:
        assert isinstance(w, str)
    h.assert_layout_ok(res)


# ------------------------------------------------------------------------------------ PNG fallback
def two_nodes(dashed=False):
    return {"nodes": [{"id": "a", "label": "alpha"}, {"id": "b", "label": "beta"}],
            "edges": [{"from": "a", "to": "b", "dashed": dashed}]}


def test_pymupdf_fallback_draws_arrowheads(monkeypatch, tmp_path):
    """§16.7: before rasterising, markers become drawn `<path>` arrowheads, so the SVG given to pymupdf has no
    marker-end and the edge group holds more than the line itself."""
    h.only_pymupdf(monkeypatch, tmp_path)
    seen = h.spy_pymupdf(monkeypatch)
    res = render(two_nodes(), out=str(tmp_path / "d.svg"), png=str(tmp_path / "d.png"))
    assert (tmp_path / "d.png").read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    assert seen, "pymupdf received the SVG"
    pre = seen[-1]
    assert "marker-end" not in pre
    root = h.svg_root(pre)
    edge = next(g for g in root.iter() if h.tag(g) == "g" and "edge" in (g.get("class") or "").split())
    assert len([e for e in edge.iter() if h.tag(e) in ("path", "polygon")]) >= 2
    assert isinstance(res["warnings"], list)
    # the written SVG itself is unchanged: it still uses the marker
    assert "marker-end" in (tmp_path / "d.svg").read_text(encoding="utf-8")


def test_pymupdf_fallback_arrowhead_pixels(monkeypatch, tmp_path):
    """§16.7: the rasterised PNG shows ink beside the line just before the target box (an arrowhead)."""
    h.only_pymupdf(monkeypatch, tmp_path)
    res = render(two_nodes(), png=str(tmp_path / "d.png"))
    b = res["nodes"]["b"]
    n = h.dark_pixels_near_arrow_tip(tmp_path / "d.png", b["x"], b["y"] + b["h"] / 2, width=res["width"])
    assert n > 0


def test_pymupdf_fallback_keeps_dashes(monkeypatch, tmp_path):
    """§16.7: dashed strokes survive the conversion (still dashed in the pre-raster SVG)."""
    h.only_pymupdf(monkeypatch, tmp_path)
    seen = h.spy_pymupdf(monkeypatch)
    render(two_nodes(dashed=True), png=str(tmp_path / "d.png"))
    assert seen and "stroke-dasharray" in seen[-1]
    assert "marker-end" not in seen[-1]


# ------------------------------------------------------------------------------------ Mermaid and floats
def test_mermaid_export_writes_rank_and_wrap():
    """§16.7: `%% rank <id> <n>` and `%% wrap <n>` comments, read back by from_mermaid."""
    spec = {"direction": "LR", "wrap": 2,
            "nodes": [{"id": "a", "label": "a"}, {"id": "b", "label": "b", "rank": 3}],
            "edges": [{"from": "a", "to": "b"}]}
    text = h.call("diagram_to_mermaid", spec=spec)["mermaid"]
    lines = [ln.strip() for ln in text.splitlines()]
    assert "%% rank b 3" in lines
    assert "%% wrap 2" in lines
    assert not any(ln.startswith("%% rank a") for ln in lines)
    back = h.call("diagram_from_mermaid", mermaid=text)["spec"]
    assert back.get("wrap") == 2
    got = {n["id"]: n.get("rank") for n in back["nodes"]}
    assert got == {"a": None, "b": 3}


def test_integral_floats_accepted():
    """§16.7: `rank: 1.0` and `wrap: 3.0` are integers; 1.5 is still a problem."""
    ok = h.call("diagram_validate", spec={"nodes": [{"id": "a", "label": "a", "rank": 1.0}], "wrap": 3.0})
    assert ok["ok"] is True, ok["problems"]
    bad = h.call("diagram_validate", spec={"nodes": [{"id": "a", "label": "a", "rank": 1.5}]})
    assert bad["ok"] is False
