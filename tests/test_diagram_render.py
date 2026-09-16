"""MANIFEST §4.2: diagram_render SVG structure, colours, tags, edges, groups, legend, note, output, PNG."""
import json
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers_diagram_text import (  # noqa: E402
    SVG_NS, attr, boxes, diagram, groups_with_class, inside, node_group, parse_svg, rect_box, shapes,
    spec_of, stage_colour, tag, tag_texts, texts, tint, tool_error,
)

FULL = {
    "title": "Capsule build path", "direction": "LR",
    "nodes": [
        {"id": "decide", "label": "build decision", "sub": "reads gap records", "stage": "build", "actor": "model"},
        {"id": "gate", "label": "admission gate", "stage": "gates", "actor": "code"},
        {"id": "lib", "label": "library\nappend-only · versioned", "stage": "library", "actor": "record"},
        {"id": "web", "label": "web search", "stage": "intent", "actor": "external"},
    ],
    "edges": [{"from": "decide", "to": "gate", "label": "manifest"},
              {"from": "gate", "to": "lib", "dashed": True},
              {"from": "web", "to": "decide"}],
    "groups": [{"id": "cold", "label": "cold path", "nodes": ["decide", "gate"], "stage": "build"}],
    "legend": "auto", "note": "(illustrative)",
}


def render(spec, **kw):
    res = diagram("diagram_render", spec=spec, **kw)
    return res, (parse_svg(res["svg"]) if res.get("svg") else None)


@pytest.fixture(scope="module")
def full():
    return render(FULL)


# §4.2 result keys
def test_result_keys(full):
    res, _ = full
    assert set(res) >= {"svg", "path", "png", "width", "height", "nodes", "warnings"}
    assert res["path"] is None and res["png"] is None
    assert isinstance(res["warnings"], list)
    assert set(res["nodes"]) == {"decide", "gate", "lib", "web"}
    for geo in res["nodes"].values():
        assert set(geo) >= {"x", "y", "w", "h", "rank"}


# §4.2 root element, xmlns, width/height/viewBox equal the result
def test_root_svg_dimensions(full):
    res, root = full
    assert root.tag == f"{{{SVG_NS}}}svg"
    w, h = res["width"], res["height"]
    assert float(root.get("width")) == pytest.approx(w)
    assert float(root.get("height")) == pytest.approx(h)
    vb = [float(v) for v in root.get("viewBox").replace(",", " ").split()]
    assert vb == pytest.approx([0, 0, w, h])


# §4.2 the first child is <title> when title is given
def test_title_is_first_child(full):
    _, root = full
    first = list(root)[0]
    assert tag(first) == "title"
    assert first.text == "Capsule build path"


# §4.2 node groups carry actor/stage classes and data-id
def test_node_group_classes(full):
    _, root = full
    for nid, actor, stage in [("decide", "model", "build"), ("gate", "code", "gates"),
                              ("lib", "record", "library"), ("web", "external", "intent")]:
        g = node_group(root, nid)
        classes = g.get("class").split()
        assert {"node", f"actor-{actor}", f"stage-{stage}"} <= set(classes)


# §4.1 defaults: stage dispatch, actor code
def test_defaults_stage_dispatch_actor_code():
    _, root = render({"nodes": [{"id": "a", "label": "plain"}]})
    classes = node_group(root, "a").get("class").split()
    assert "actor-code" in classes and "stage-dispatch" in classes


# §4.2 every label line and sub appear as text
def test_label_lines_and_sub_are_text(full):
    _, root = full
    assert "library" in texts(node_group(root, "lib"))
    assert "append-only · versioned" in texts(node_group(root, "lib"))
    decide = texts(node_group(root, "decide"))
    assert "build decision" in decide and "reads gap records" in decide


# §4.2 text is XML-escaped
def test_text_is_xml_escaped():
    res, root = render({"nodes": [{"id": "a", "label": "a < b & c > \"d\""}]})
    assert "a < b & c > \"d\"" in texts(node_group(root, "a"))


# §4.2 shape colours per actor
def _has_shape(g, fill, stroke, kinds=None):
    for s in shapes(g):
        if kinds and tag(s) not in kinds:
            continue
        f, st = attr(s, "fill"), attr(s, "stroke")
        if f == fill and st == stroke:
            return True
    return False


def test_model_colours(full):
    _, root = full
    c = stage_colour("build")
    assert _has_shape(node_group(root, "decide"), tint(c, 0.20), c)


def test_code_colours(full):
    _, root = full
    assert _has_shape(node_group(root, "gate"), "#ffffff", stage_colour("gates"))


def test_record_is_path_with_colours(full):
    _, root = full
    assert _has_shape(node_group(root, "lib"), "#ffffff", stage_colour("library"), kinds={"path"})


def test_external_colours_ignore_stage(full):
    _, root = full
    assert _has_shape(node_group(root, "web"), "#f6f6f6", "#4d4d4d")


# §4.2 dashed nodes have a stroke-dasharray
def test_dashed_node_has_dasharray():
    _, root = render({"nodes": [{"id": "a", "label": "x", "dashed": True}]})
    assert any(attr(s, "stroke-dasharray") for s in shapes(node_group(root, "a")))


# §4.2 tags MODEL / CODE, none on record and external
def test_tags(full):
    _, root = full
    assert tag_texts(node_group(root, "decide")) == ["MODEL"]
    assert tag_texts(node_group(root, "gate")) == ["CODE"]
    assert tag_texts(node_group(root, "lib")) == []
    assert tag_texts(node_group(root, "web")) == []


def test_tags_false_removes_tags():
    spec = dict(FULL, tags=False)
    _, root = render(spec)
    for nid in ("decide", "gate"):
        assert "MODEL" not in tag_texts(node_group(root, nid))
        assert "CODE" not in tag_texts(node_group(root, nid))


# §4.2 edges: group with data-from/to, path with marker-end referencing a marker in defs
def test_edges_have_marker_defined_in_defs(full):
    _, root = full
    edges = groups_with_class(root, "edge")
    assert sorted((g.get("data-from"), g.get("data-to")) for g in edges) == sorted(
        [("decide", "gate"), ("gate", "lib"), ("web", "decide")])
    marker_ids = {m.get("id") for d in root.iter(f"{{{SVG_NS}}}defs") for m in d.iter(f"{{{SVG_NS}}}marker")}
    for g in edges:
        paths = [e for e in g.iter() if tag(e) == "path" and attr(e, "marker-end")]
        assert paths, "edge path without marker-end"
        ref = attr(paths[0], "marker-end")
        assert ref.startswith("url(#") and ref.endswith(")")
        assert ref[5:-1] in marker_ids


def _edge(root, a, b):
    return [g for g in groups_with_class(root, "edge") if g.get("data-from") == a and g.get("data-to") == b]


def test_edge_label_and_dash(full):
    _, root = full
    (labelled,) = _edge(root, "decide", "gate")
    assert "manifest" in texts(labelled)
    (dashed,) = _edge(root, "gate", "lib")
    assert any(attr(p, "stroke-dasharray") for p in dashed.iter() if tag(p) == "path")


def test_duplicate_edges_render_twice():
    spec = spec_of([("a", "A"), ("b", "B")], [("a", "b"), ("a", "b")])
    _, root = render(spec)
    assert len(_edge(root, "a", "b")) == 2


# §4.2 groups: dashed rectangle before the nodes, label, contains members
def test_group_rect_dashed_labelled_and_before_nodes(full):
    _, root = full
    (grp,) = [g for g in groups_with_class(root, "group") if g.get("data-id") == "cold"]
    rects = [r for r in grp.iter() if tag(r) == "rect" and attr(r, "stroke-dasharray")]
    assert rects, "group has no dashed rect"
    assert "cold path" in texts(grp)
    order = list(root.iter())
    first_node = min(order.index(node_group(root, n)) for n in ("decide", "gate"))
    assert order.index(rects[0]) < first_node


def test_group_rect_contains_member_boxes(full):
    res, root = full
    (grp,) = [g for g in groups_with_class(root, "group") if g.get("data-id") == "cold"]
    rect = [r for r in grp.iter() if tag(r) == "rect" and attr(r, "stroke-dasharray")][0]
    outer = rect_box(root, rect)
    b = boxes(res)
    assert inside(b["decide"], outer) and inside(b["gate"], outer)


# §4.2 legend
def _legend(root):
    return groups_with_class(root, "legend")


def test_legend_auto_lists_present_actors(full):
    _, root = full
    (leg,) = _legend(root)
    t = texts(leg)
    for want in ("MODEL call", "CODE (deterministic)", "record", "external", "1 box = 1 model session"):
        assert want in t, (want, t)


def test_legend_auto_without_model_has_no_session_line():
    spec = spec_of([("a", "A", None, "code"), ("b", "B", None, "record")], [("a", "b")])
    _, root = render(spec)
    (leg,) = _legend(root)
    t = texts(leg)
    assert "CODE (deterministic)" in t and "record" in t
    assert "MODEL call" not in t and "external" not in t
    assert "1 box = 1 model session" not in t


def test_legend_auto_single_actor_absent():
    spec = spec_of([("a", "A", None, "code"), ("b", "B", None, "code")], [("a", "b")])
    _, root = render(spec)
    assert _legend(root) == []


def test_legend_false_hides_legend():
    _, root = render(dict(FULL, legend=False))
    assert _legend(root) == []


def test_legend_true_single_model_actor():
    spec = spec_of([("a", "A", None, "model")], legend=True)
    _, root = render(spec)
    (leg,) = _legend(root)
    t = texts(leg)
    assert "MODEL call" in t and "1 box = 1 model session" in t
    assert "CODE (deterministic)" not in t


# §4.2 legend inside the canvas and not overlapping any node
def test_legend_rects_inside_canvas_and_clear_of_nodes(full):
    res, root = full
    (leg,) = _legend(root)
    canvas = (0, 0, res["width"], res["height"])
    node_boxes = list(boxes(res).values())
    for r in [e for e in leg.iter() if tag(e) == "rect"]:
        rb = rect_box(root, r)
        assert inside(rb, canvas)
        for nb in node_boxes:
            assert not (rb[0] < nb[2] and nb[0] < rb[2] and rb[1] < nb[3] and nb[1] < rb[3])


# §4.2 note
def test_note_text(full):
    _, root = full
    notes = [e for e in root.iter() if tag(e) == "text" and "note" in (e.get("class") or "").split()]
    assert len(notes) == 1
    assert "".join(notes[0].itertext()).strip() == "(illustrative)"


# §4.2 font-family includes sans-serif
def test_font_family_sans_serif(full):
    res, _ = full
    assert "font-family" in res["svg"] and "sans-serif" in res["svg"]


# §4.2 out: file written, path returned, svg text not returned
def test_out_writes_file(tmp_path):
    out = tmp_path / "d.svg"
    res = diagram("diagram_render", spec=FULL, out=str(out))
    assert res["path"] == str(out)
    assert res.get("svg") is None
    root = parse_svg(out.read_text(encoding="utf-8"))
    assert float(root.get("width")) == pytest.approx(res["width"])


# §4.2 spec_path and mermaid inputs
def test_spec_path_input(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps(FULL), encoding="utf-8")
    res = diagram("diagram_render", spec_path=str(p))
    assert set(res["nodes"]) == {"decide", "gate", "lib", "web"}


def test_mermaid_input():
    res = diagram("diagram_render", mermaid="flowchart LR\n  a[Alpha] --> b(Beta)\n")
    root = parse_svg(res["svg"])
    assert "actor-model" in node_group(root, "b").get("class").split()


# §4.2 PNG: no converter -> ToolError, SVG still written
def _no_converters(monkeypatch, tmp_path):
    for p in ("C:/Program Files/Inkscape", "C:/Program Files (x86)/Inkscape",
              "/Applications/Inkscape.app", "/usr/bin/inkscape", "/usr/bin/rsvg-convert",
              "/opt/homebrew/bin/rsvg-convert", "/usr/local/bin/rsvg-convert"):
        if Path(p).exists():
            pytest.skip(f"a converter is installed at a fixed location: {p}")
    monkeypatch.setitem(sys.modules, "cairosvg", None)
    monkeypatch.setenv("PATH", "")
    monkeypatch.chdir(tmp_path)


def test_png_without_converter_errors_but_writes_svg(monkeypatch, tmp_path):
    _no_converters(monkeypatch, tmp_path)
    out, png = tmp_path / "x.svg", tmp_path / "x.png"
    with pytest.raises(tool_error()) as exc:
        diagram("diagram_render", spec=FULL, out=str(out), png=str(png))
    assert "no SVG to PNG converter" in str(exc.value)
    assert out.exists()
    parse_svg(out.read_text(encoding="utf-8"))


def test_png_with_converter(tmp_path):
    try:
        import cairosvg  # noqa: F401
    except Exception:
        if not (shutil.which("rsvg-convert") or shutil.which("inkscape")):
            pytest.skip("no SVG to PNG converter installed")
    png = tmp_path / "x.png"
    res = diagram("diagram_render", spec=FULL, png=str(png))
    assert res["png"] == str(png)
    assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
