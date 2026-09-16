"""MANIFEST §4.4: Mermaid subset import (diagram_from_mermaid) and export (diagram_to_mermaid)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers_diagram_text import diagram, tool_error  # noqa: E402


def parse(text):
    res = diagram("diagram_from_mermaid", mermaid=text)
    assert set(res) >= {"spec", "warnings"}
    return res["spec"], res["warnings"]


def nodes(spec):
    return {n["id"]: n for n in spec["nodes"]}


def edge_list(spec):
    return [(e["from"], e["to"], e.get("label") or "", bool(e.get("dashed", False))) for e in spec.get("edges", [])]


def stage(n):
    return n.get("stage", "dispatch")


def actor(n):
    return n.get("actor", "code")


# §4.4 header and direction mapping
@pytest.mark.parametrize("header,direction", [
    ("flowchart LR", "LR"), ("flowchart TB", "TB"), ("graph TD", "TB"), ("flowchart", "TB"),
])
def test_direction(header, direction):
    spec, _ = parse(f"{header}\n  a --> b\n")
    assert spec.get("direction", "LR") == direction


# §4.4 shapes -> actors
@pytest.mark.parametrize("line,label,act", [
    ("n1[Plain box]", "Plain box", "code"),
    ("n1(Round box)", "Round box", "model"),
    ("n1>Flag]", "Flag", "record"),
    ("n1[(Store)]", "Store", "record"),
    ("n1{{Outside}}", "Outside", "external"),
])
def test_shapes(line, label, act):
    spec, _ = parse(f"flowchart LR\n  {line}\n")
    n = nodes(spec)["n1"]
    assert n["label"] == label
    assert actor(n) == act


# §4.4 quoted labels, <br> variants
def test_quoted_label_quotes_removed():
    spec, _ = parse('flowchart LR\n  a["Hello (world)"]\n')
    assert nodes(spec)["a"]["label"] == "Hello (world)"


@pytest.mark.parametrize("br", ["<br>", "<br/>", "<br />"])
def test_br_becomes_newline(br):
    spec, _ = parse(f"flowchart LR\n  a[top{br}bottom]\n")
    assert nodes(spec)["a"]["label"] == "top\nbottom"


# §4.4 bare ids
def test_bare_id_creates_code_node_labelled_with_id():
    spec, _ = parse("flowchart LR\n  alpha --> beta\n")
    n = nodes(spec)
    assert n["alpha"]["label"] == "alpha" and actor(n["alpha"]) == "code"
    assert n["beta"]["label"] == "beta"


def test_bare_id_refers_to_existing_node():
    spec, _ = parse("flowchart LR\n  a(Thinker)\n  a --> b\n")
    n = nodes(spec)
    assert n["a"]["label"] == "Thinker" and actor(n["a"]) == "model"
    assert len(spec["nodes"]) == 2


# §4.4 :::stage
def test_class_suffix_sets_stage():
    spec, warnings = parse("flowchart LR\n  a[Check]:::gates --> b(Build):::build\n")
    n = nodes(spec)
    assert stage(n["a"]) == "gates" and stage(n["b"]) == "build"
    assert warnings == []


def test_unknown_class_suffix_warns_and_keeps_default():
    spec, warnings = parse("flowchart LR\n  a[Check]:::sparkly\n")
    assert stage(nodes(spec)["a"]) == "dispatch"
    assert len(warnings) == 1


# §4.4 edges
@pytest.mark.parametrize("arrow,dashed", [("-->", False), ("---", False), ("==>", False),
                                          ("-.->", True), ("-.-", True)])
def test_edge_kinds(arrow, dashed):
    spec, _ = parse(f"flowchart LR\n  a {arrow} b\n")
    assert edge_list(spec) == [("a", "b", "", dashed)]


def test_pipe_labels():
    spec, _ = parse("flowchart LR\n  a -->|yes| b\n  b -.->|maybe later| c\n")
    assert edge_list(spec) == [("a", "b", "yes", False), ("b", "c", "maybe later", True)]


def test_chain_gives_two_edges():
    spec, _ = parse("flowchart LR\n  a --> b --> c\n")
    assert edge_list(spec) == [("a", "b", "", False), ("b", "c", "", False)]


def test_inline_shapes_on_edge_line():
    spec, _ = parse("flowchart LR\n  a[Start] --> b{{API}}\n")
    n = nodes(spec)
    assert n["a"]["label"] == "Start" and actor(n["b"]) == "external"
    assert edge_list(spec) == [("a", "b", "", False)]


# §4.4 comments and blank lines ignored
def test_comments_and_blank_lines_ignored():
    spec, warnings = parse("%% a leading comment\n\nflowchart LR\n  %% inside\n\n  a --> b\n")
    assert [n["id"] for n in spec["nodes"]] == ["a", "b"]
    assert warnings == []


# §4.4 subgraphs
def test_subgraph_with_label():
    spec, _ = parse("flowchart LR\n  subgraph cold [Cold path]\n    a --> b\n  end\n  b --> c\n")
    (g,) = spec["groups"]
    assert g["id"] == "cold" and g["label"] == "Cold path"
    assert g["nodes"] == ["a", "b"]


def test_subgraph_without_label():
    spec, _ = parse("flowchart LR\n  subgraph hot\n    x[One]\n    y[Two]\n  end\n")
    (g,) = spec["groups"]
    assert g["id"] == "hot" and g["nodes"] == ["x", "y"]


# §4.4 ignored statements, 1 warning each
def test_style_lines_ignored_with_one_warning_each():
    text = ("flowchart LR\n  a --> b\n  classDef hot fill:#f00\n  class a hot\n  style b fill:#0f0\n"
            "  linkStyle 0 stroke:#00f\n  click a callback\n")
    spec, warnings = parse(text)
    assert len(warnings) == 5
    assert edge_list(spec) == [("a", "b", "", False)]


# §4.4 any other line -> ToolError containing line {n}
def test_unknown_line_is_error_with_line_number():
    with pytest.raises(tool_error()) as exc:
        parse("flowchart LR\n  a --> b\n  this is not mermaid ???\n")
    assert "line 3" in str(exc.value)


# §4.4 node order = first appearance
def test_node_order_is_first_appearance():
    spec, _ = parse("flowchart LR\n  z --> y\n  x[Later]\n  y --> x\n")
    assert [n["id"] for n in spec["nodes"]] == ["z", "y", "x"]


# §4.4 mermaid_path
def test_mermaid_path(tmp_path):
    p = tmp_path / "d.mmd"
    p.write_text("flowchart LR\n  a --> b\n", encoding="utf-8")
    res = diagram("diagram_from_mermaid", mermaid_path=str(p))
    assert edge_list(res["spec"]) == [("a", "b", "", False)]


# §4.4 to_mermaid output
def test_to_mermaid_header_stage_and_edges():
    spec = {"direction": "TB",
            "nodes": [{"id": "a", "label": "A", "stage": "build", "actor": "model"},
                      {"id": "b", "label": "B"}],
            "edges": [{"from": "a", "to": "b", "label": "go", "dashed": True}]}
    text = diagram("diagram_to_mermaid", spec=spec)["mermaid"]
    assert text.splitlines()[0].strip() == "flowchart TB"
    assert ":::build" in text and ":::dispatch" in text
    assert "-.->" in text and "|go|" in text


def test_to_mermaid_default_direction_is_lr():
    text = diagram("diagram_to_mermaid", spec={"nodes": [{"id": "a", "label": "A"}]})["mermaid"]
    assert text.splitlines()[0].strip() == "flowchart LR"


# §4.4 round trip
ROUND = {
    "direction": "LR",
    "nodes": [
        {"id": "decide", "label": "build decision", "stage": "build", "actor": "model"},
        {"id": "gate", "label": "admission gate", "stage": "gates", "actor": "code"},
        {"id": "lib", "label": "library\nappend-only · versioned", "stage": "library", "actor": "record"},
        {"id": "api", "label": "vendor API", "stage": "external", "actor": "external"},
        {"id": "lonely", "label": "no edges here", "stage": "claims", "actor": "code"},
    ],
    "edges": [
        {"from": "decide", "to": "gate", "label": "manifest", "dashed": False},
        {"from": "gate", "to": "lib", "label": "", "dashed": True},
        {"from": "api", "to": "decide", "label": "docs", "dashed": True},
        {"from": "gate", "to": "decide", "label": "", "dashed": False},
    ],
    "groups": [{"id": "cold", "label": "cold path", "nodes": ["decide", "gate"]}],
}


def _norm_nodes(spec):
    return [(n["id"], n["label"], stage(n), actor(n)) for n in spec["nodes"]]


def _norm_groups(spec):
    return [(g["id"], g.get("label"), list(g["nodes"])) for g in spec.get("groups", [])]


def roundtrip(spec):
    text = diagram("diagram_to_mermaid", spec=spec)["mermaid"]
    back = diagram("diagram_from_mermaid", mermaid=text)["spec"]
    return back


def test_round_trip_preserves_spec():
    back = roundtrip(ROUND)
    # order is not part of the round-trip promise, so compare as sorted collections
    assert sorted(_norm_nodes(back)) == sorted(_norm_nodes(ROUND))
    assert sorted(edge_list(back)) == sorted(edge_list(ROUND))
    assert sorted((i, lbl, sorted(ns)) for i, lbl, ns in _norm_groups(back)) == \
        sorted((i, lbl, sorted(ns)) for i, lbl, ns in _norm_groups(ROUND))
    assert back.get("direction", "LR") == "LR"


def test_round_trip_folds_sub_into_label():
    spec = {"nodes": [{"id": "a", "label": "main", "sub": "detail line", "actor": "model"}]}
    back = roundtrip(spec)
    assert back["nodes"][0]["label"] == "main\ndetail line"
