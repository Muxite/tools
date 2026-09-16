"""MANIFEST §13.6 (with §7.1 and §4.4): textlint masking/rules and Mermaid hardening, visible cases."""
from __future__ import annotations

import pytest

import helpers_diagram_text as ht


@pytest.fixture
def lint(tmp_path, monkeypatch):
    def run(body, **kw):
        return ht.lint_text(tmp_path, monkeypatch, body, **kw)
    return run


# ---------------------------------------------------------------- textlint

def test_fence_indented_under_list_item_is_masked(lint):
    """§13.6: a fence indented under a list item is masked; its content gives no findings."""
    body = ("# Setup\n"
            "\n"
            "- Install the tool first.\n"
            "\n"
            "    ```text\n"
            "    we don't; maybe? TODO: it's here\n"
            "    ```\n"
            "\n"
            "The tool is then ready.\n")
    res = lint(body)
    assert [(r, ln) for r, ln in ht.rules(res) if 5 <= ln <= 7] == []


def test_s006_in_heading(lint):
    """§13.6: S006 also applies to headings."""
    res = lint("# Report\n\n## Plan [TODO]\n\nThe plan is short.\n")
    assert ht.rules(res, "S006") == [3]


def test_s010_skips_comment_only_line(lint):
    """§13.6: S010 uses the first sentence with unmasked prose, skipping a comment-only line."""
    res = lint("# Report\n\n## Scope\n\n<!-- note -->\nThis section covers X.\n")
    assert ht.rules(res, "S010") == [6]


# ---------------------------------------------------------------- Mermaid import

def _parse(text):
    res = ht.diagram("diagram_from_mermaid", mermaid=text)
    return res["spec"], res["warnings"]


def test_style_prefixed_node_id_is_an_edge():
    """§13.6: `style-guide --> x` is an edge, not an ignored style statement."""
    spec, warnings = _parse("flowchart LR\nstyle-guide --> x\n")
    assert [n["id"] for n in spec["nodes"]] == ["style-guide", "x"]
    assert [(e["from"], e["to"]) for e in spec["edges"]] == [("style-guide", "x")]
    assert warnings == []


# ---------------------------------------------------------------- Mermaid export

def test_to_mermaid_refuses_keyword_id():
    """§13.6: a node id that is a Mermaid keyword (`end`) raises ToolError naming it."""
    spec = ht.spec_of([("start", "Start"), ("end", "Finish")], [("start", "end")])
    with pytest.raises(ht.tool_error()) as ei:
        ht.diagram("diagram_to_mermaid", spec=spec)
    assert "end" in str(ei.value)


def test_group_stage_round_trips():
    """§13.6: a group's stage survives to_mermaid -> from_mermaid."""
    spec = ht.spec_of([("a", "A", "claims", "model"), ("b", "B", "gates", "code")], [("a", "b")],
                      groups=[{"id": "hot", "label": "hot path", "nodes": ["a", "b"], "stage": "claims"}],
                      direction="LR")
    text = ht.diagram("diagram_to_mermaid", spec=spec)["mermaid"]
    back, _ = _parse(text)
    assert len(back["groups"]) == 1
    g = back["groups"][0]
    assert g["id"] == "hot" and g["nodes"] == ["a", "b"]
    assert g.get("stage") == "claims"


def test_edge_label_spaces_round_trip():
    """§13.6: edge label text is kept exactly, including surrounding spaces."""
    spec = ht.spec_of([("a", "A"), ("b", "B")], [{"from": "a", "to": "b", "label": " spaced "}])
    back, _ = _parse(ht.diagram("diagram_to_mermaid", spec=spec)["mermaid"])
    assert [e.get("label") for e in back["edges"]] == [" spaced "]


# ---------------------------------------------------------------- more cases

def test_tilde_fence_under_numbered_item(lint):
    """§13.6: a ~~~ fence indented (2 spaces) under a numbered item is masked."""
    body = ("# Steps\n"
            "\n"
            "1. Run the check.\n"
            "  ~~~\n"
            "  we can't; perhaps?\n"
            "  ~~~\n"
            "2. Read the output.\n")
    res = lint(body)
    assert [x for x in ht.rules(res) if 4 <= x[1] <= 6] == []


def test_s010_not_triggered_by_later_sentence(lint):
    """§13.6: only the first sentence with prose counts (after a code-only line)."""
    res = lint("# R\n\n## Data\n\n`inline only`\nThe data comes from logs. This section is short.\n")
    assert ht.rules(res, "S010") == []


def test_linkstyle_prefixed_id_with_shape():
    """§13.6: `linkStyle_x[Box] --> y` is a node definition, not an ignored linkStyle line."""
    spec, _ = _parse("flowchart LR\n  linkStyle_x[Box] --> y\n")
    nodes = {n["id"]: n for n in spec["nodes"]}
    assert nodes["linkStyle_x"]["label"] == "Box"
    assert len(spec["edges"]) == 1


def test_to_mermaid_refuses_keyword_group_id():
    """§13.6: a group id `end` is refused too, naming it."""
    spec = ht.spec_of([("a", "A")], groups=[{"id": "end", "label": "G", "nodes": ["a"]}])
    with pytest.raises(ht.tool_error()) as ei:
        ht.diagram("diagram_to_mermaid", spec=spec)
    assert "end" in str(ei.value)


def test_label_with_mermaid_syntax_round_trips():
    """§13.6: labels may contain any text (brackets, pipes, quotes, arrows)."""
    label = 'say "hi" | [x] --> {y} (z)'
    spec = ht.spec_of([{"id": "a", "label": label, "actor": "model"}, ("b", "B")],
                      [{"from": "a", "to": "b", "label": "a|b"}])
    back, _ = _parse(ht.diagram("diagram_to_mermaid", spec=spec)["mermaid"])
    nodes = {n["id"]: n for n in back["nodes"]}
    assert nodes["a"]["label"] == label
    assert back["edges"][0]["label"] == "a|b"
