"""MANIFEST §13.4 (with §3.1, §3.3, §4.1, §5): validation never crashes, visible cases."""
from __future__ import annotations

import json

import pytest

import helpers_deck as hd
import helpers_diagram_text as ht


def _deck_problem(the_spec, *needles):
    """§3.1/§13.4: deck spec problems surface as 1 ToolError (never a TypeError/ValueError)."""
    with pytest.raises(hd.ToolError()) as ei:
        hd.call("deck_lint", spec=the_spec)
    msg = str(ei.value)
    for n in needles:
        assert n in msg, msg
    return msg


# ---------------------------------------------------------------- wrong types

def test_deck_stage_list_is_a_problem():
    """§13.4: a content slide `stage` given as a list is a listed problem naming `stage`."""
    _deck_problem(hd.spec(hd.content(stage=["gates"])), "slides[0]", "stage")


def test_chart_stage_object_is_a_problem():
    """§13.4/§5: chart `stage` given as an object is a validation problem naming `stage`."""
    with pytest.raises(hd.ToolError()) as ei:
        hd.call("chart_bar", spec={"categories": ["a", "b"], "values": [1, 2], "stage": {"name": "gates"}})
    assert "stage" in str(ei.value)


def test_diagram_node_stage_list_is_a_problem():
    """§13.4/§4.3: diagram_validate lists a list-typed node stage as a problem, without raising."""
    spec = ht.spec_of([{"id": "a", "label": "A", "stage": ["gates"]}, ("b", "B")], [("a", "b")])
    res = ht.diagram("diagram_validate", spec=spec)
    assert res["ok"] is False
    assert any("stage" in p for p in res["problems"]), res["problems"]
    with pytest.raises(ht.tool_error()):
        ht.diagram("diagram_render", spec=spec)


# ---------------------------------------------------------------- numbers

def test_chart_huge_value_is_a_problem():
    """§13.4: 10**400 does not convert to a finite float: a validation problem, not OverflowError."""
    with pytest.raises(hd.ToolError()):
        hd.call("chart_bar", spec={"categories": ["a"], "values": [10 ** 400]})


def test_deck_time_with_5000_digit_minutes():
    """§13.4: notes.time minutes have at most 3 digits; a 5000-digit time is a problem naming `time`."""
    _deck_problem(hd.spec(hd.content(time="9" * 5000 + ":00")), "slides[0].notes.time")


# ---------------------------------------------------------------- control characters

def test_chart_category_control_char():
    """§13.4: control characters in chart text are problems."""
    with pytest.raises(hd.ToolError()):
        hd.call("chart_bar", spec={"categories": ["ok", "bell\x07"], "values": [1, 2]})


def test_deck_title_control_char():
    """§13.4: a control character in deck text is a problem naming the slide."""
    _deck_problem(hd.spec(hd.content(title="Bad \x01 title")), "slides[0]")


def test_diagram_label_control_char():
    """§13.4: a diagram label with a control character (not \\n or \\t) is a problem."""
    spec = ht.spec_of([("a", "fine\tlabel\nline 2"), ("b", "esc\x1bape")], [("a", "b")])
    res = ht.diagram("diagram_validate", spec=spec)
    assert res["ok"] is False
    assert any("nodes[1]" in p for p in res["problems"]), res["problems"]
    assert not any("nodes[0]" in p for p in res["problems"]), res["problems"]


def test_diagram_id_trailing_newline():
    """§13.1/§13.4: id patterns are full matches, so `a\\n` is not a valid id."""
    spec = ht.spec_of([("a\n", "A"), ("b", "B")])
    res = ht.diagram("diagram_validate", spec=spec)
    assert res["ok"] is False
    assert any("nodes[0]" in p for p in res["problems"]), res["problems"]


# ---------------------------------------------------------------- inserts, D001, files

def test_27_inserts_after_one_core_slide():
    """§13.4: more than 26 insert slides after 1 core slide is a validation problem."""
    slides = [hd.content()] + [hd.content(title=f"Insert {i}", insert=True) for i in range(27)]
    msg = _deck_problem(hd.spec(*slides))
    assert "insert" in msg.lower()


def test_d001_float_tolerance():
    """§13.4: 115 words at 0:50 and 2.3 words/s is exactly the cap: no D001."""
    say = " ".join(f"w{i}" for i in range(115))
    res = hd.call("deck_lint", spec=hd.spec(hd.content(time="0:50", say=say, source="s")),
                  words_per_second=2.3)
    hd.check_shape(res)
    assert hd.rules(res, "D001") == []


def test_times_file_in_missing_directory(tmp_path):
    """§13.4: deck_build validates times_file first; a missing parent directory -> ToolError, no deck written."""
    hd.need_office()
    out = tmp_path / "deck.pptx"
    with pytest.raises(hd.ToolError()):
        hd.call("deck_build", spec=hd.spec(hd.content(), id="talk"), out=str(out),
                times_file=str(tmp_path / "nowhere" / "times.json"))
    assert not out.exists()


def test_deck_spec_file_with_bom(tmp_path):
    """§13.4: spec files may start with a UTF-8 BOM."""
    p = tmp_path / "deck.json"
    p.write_bytes(b"\xef\xbb\xbf" + json.dumps(hd.spec(hd.content(source="s"))).encode("utf-8"))
    res = hd.call("deck_lint", spec_path=str(p))
    hd.check_shape(res)
    assert res["slides"] == 1


# ---------------------------------------------------------------- more wrong types and text

@pytest.mark.parametrize("node,needle", [
    ({"id": "c", "label": "C", "actor": 7}, "actor"),
    ({"id": "c", "label": 12}, "label"),
    ({"id": ["c"], "label": "C"}, "id"),
])
def test_diagram_node_wrong_types(node, needle):
    """§13.4: wrong-typed actor / label / id are listed problems naming the field."""
    spec = ht.spec_of([("a", "A"), ("b", "B"), node], [("a", "b")])
    res = ht.diagram("diagram_validate", spec=spec)
    assert res["ok"] is False
    assert any("nodes[2]" in p and needle in p for p in res["problems"]), res["problems"]


def test_diagram_direction_list():
    """§13.4: `direction` must be a string."""
    res = ht.diagram("diagram_validate", spec=ht.spec_of([("a", "A")], direction=["LR"]))
    assert res["ok"] is False
    assert any("direction" in p for p in res["problems"]), res["problems"]


def test_diagram_render_wrong_type_is_tool_error():
    """§13.4: diagram_render turns a wrong-typed field into 1 ToolError."""
    with pytest.raises(ht.tool_error()):
        ht.diagram("diagram_render", spec=ht.spec_of([("a", "A")], direction={"x": 1}))


def test_deck_say_backspace():
    """§13.4: notes text is written to PPTX too; a backspace in SAY is a problem."""
    _deck_problem(hd.spec(hd.content(say=hd.SAY25 + " \x08", source="s")), "slides[0]")


def test_deck_tab_and_newline_allowed():
    """§13.4: \\n and \\t are the allowed control characters."""
    body = {"kind": "lines", "items": ["col1\tcol2", "line\nbreak"]}
    res = hd.call("deck_lint", spec=hd.spec(hd.content(body=body, source="s")))
    assert res["slides"] == 1


def test_chart_title_form_feed():
    """§13.4: a control character in chart text (title) is a problem."""
    with pytest.raises(hd.ToolError()):
        hd.call("chart_bar", spec={"title": "Results\x0c", "categories": ["x"], "values": [3]})
