"""chart_bar SVG bar charts (MANIFEST §5)."""
import json
import math

import pytest

from helpers_deck import (SVG_NS, ToolError, all_svg_text, call, chart_svg, classes, fill_of, find_class,
                          svg_root, text_of, write_json)


def bars(root):
    return find_class(root, "rect", "bar")


def hlen(rect):
    return float(rect.get("width"))


def err(**args):
    with pytest.raises(ToolError()) as ei:
        call("chart_bar", **args)
    return str(ei.value)


def test_bars_have_label_and_value_attributes():
    # §5: <rect class="bar" data-label data-value>, 1 per category
    _, root = chart_svg(spec={"categories": ["kept", "passed", "failed"], "values": [222, 7, 215]})
    bs = bars(root)
    assert [b.get("data-label") for b in bs] == ["kept", "passed", "failed"]
    assert [float(b.get("data-value")) for b in bs] == [222, 7, 215]


def test_result_shape_without_out():
    # §5 result: svg when no out, path, width, height, bars
    res, _ = chart_svg(spec={"categories": ["a", "b"], "values": [1, 3]})
    assert isinstance(res["svg"], str)
    assert res["path"] is None
    assert res["width"] > 0 and res["height"] > 0
    assert [(b["label"], b["value"], b["highlight"]) for b in res["bars"]] == [("a", 1, False), ("b", 3, False)]
    json.dumps(res)


def test_highlight_by_index_default_stage():
    # §5: highlighted bar class "bar highlight", fill STAGE[gates]; others #9a9a9a
    res, root = chart_svg(spec={"categories": ["a", "b", "c"], "values": [1, 2, 3], "highlight": 2})
    bs = bars(root)
    assert "highlight" in classes(bs[2])
    assert "highlight" not in classes(bs[0]) and "highlight" not in classes(bs[1])
    assert fill_of(bs[2]) == "#008a63"
    assert fill_of(bs[0]) == fill_of(bs[1]) == "#9a9a9a"
    assert [b["highlight"] for b in res["bars"]] == [False, False, True]


def test_highlight_uses_given_stage():
    # §5: stage selects the highlight colour
    _, root = chart_svg(spec={"categories": ["a", "b"], "values": [1, 2], "highlight": 0, "stage": "freeze"})
    assert fill_of(bars(root)[0]) == "#7b3fa0"


def test_no_highlight_all_grey():
    # §5: bars other than the highlighted one are grey
    _, root = chart_svg(spec={"categories": ["a", "b"], "values": [1, 2]})
    assert {fill_of(b) for b in bars(root)} == {"#9a9a9a"}


def test_lengths_proportional_horizontal():
    # §5: length (width when horizontal) proportional to value / axis max, within 0.5 px
    vals = [10, 25, 40, 5]
    res, root = chart_svg(spec={"categories": list("abcd"), "values": vals})
    bs = bars(root)
    full = hlen(bs[2])
    assert full > 0
    for b, v in zip(bs, vals):
        assert abs(hlen(b) - full * v / 40) <= 0.5
    for b, r in zip(bs, res["bars"]):
        assert abs(r["length"] - hlen(b)) <= 0.5


def test_zero_value_has_zero_length():
    # §5: a value of 0 has length 0
    res, root = chart_svg(spec={"categories": ["zero", "some"], "values": [0, 4]})
    assert hlen(bars(root)[0]) == 0
    assert res["bars"][0]["length"] == 0


def test_value_labels_integers_with_unit():
    # §5: default 0 decimals when every value is an integer, followed by unit
    _, root = chart_svg(spec={"categories": ["a", "b"], "values": [3, 12], "unit": "%"})
    labels = [text_of(t).strip() for t in find_class(root, "text", "value")]
    assert sorted(labels) == sorted(["3%", "12%"])


def test_value_labels_one_decimal_for_floats():
    # §5: default 1 decimal when some value is not an integer
    _, root = chart_svg(spec={"categories": ["a", "b"], "values": [1.24, 2]})
    labels = [text_of(t).strip() for t in find_class(root, "text", "value")]
    assert sorted(labels) == sorted(["1.2", "2.0"])


def test_value_labels_explicit_decimals():
    # §5: decimals places
    _, root = chart_svg(spec={"categories": ["a", "b"], "values": [96.8, 3.2], "decimals": 2, "unit": " %"})
    labels = [text_of(t).strip() for t in find_class(root, "text", "value")]
    assert sorted(labels) == sorted(["96.80 %", "3.20 %"])


def test_category_labels_with_n():
    # §5: with n, the label is "{category} (n={n})"
    _, root = chart_svg(spec={"categories": ["kept", "dropped"], "values": [5, 7], "n": [222, 99]})
    texts = [t.strip() for t in all_svg_text(root)]
    assert "kept (n=222)" in texts
    assert "dropped (n=99)" in texts


def test_category_labels_plain():
    # §5: category labels appear as text
    _, root = chart_svg(spec={"categories": ["alpha", "beta"], "values": [5, 7]})
    texts = [t.strip() for t in all_svg_text(root)]
    assert "alpha" in texts and "beta" in texts


def test_takeaway_bold_and_title():
    # §5: takeaway <text class="takeaway" font-weight="bold">; title is <title> and a visible heading
    _, root = chart_svg(spec={"title": "Pass rates", "categories": ["a"], "values": [1],
                              "takeaway": "Most fail"})
    tk = find_class(root, "text", "takeaway")
    assert len(tk) == 1
    assert text_of(tk[0]).strip() == "Most fail"
    assert tk[0].get("font-weight") == "bold"
    titles = [text_of(t) for t in root.iter(f"{{{SVG_NS}}}title")]
    assert "Pass rates" in titles
    assert "Pass rates" in [t.strip() for t in all_svg_text(root)]


def test_out_writes_file(tmp_path):
    # §5: out path; result path
    out = tmp_path / "chart.svg"
    res = call("chart_bar", spec={"categories": ["a", "b"], "values": [1, 2]}, out=str(out))
    assert out.is_file()
    root = svg_root(out.read_text(encoding="utf-8"))
    assert len(bars(root)) == 2
    assert isinstance(res["path"], str)
    assert res.get("svg") is None


def test_spec_path(tmp_path):
    # §5: spec_path
    p = write_json(tmp_path / "c.json", {"categories": ["x", "y", "z"], "values": [1, 2, 3]})
    res = call("chart_bar", spec_path=str(p))
    assert [b["label"] for b in res["bars"]] == ["x", "y", "z"]


def test_negative_value_message():
    # §5: negative values are not supported
    msg = err(spec={"categories": ["a", "b"], "values": [1, -2]})
    assert "negative values are not supported" in msg


def test_length_mismatch():
    # §5: categories and values the same length
    err(spec={"categories": ["a", "b"], "values": [1]})


def test_empty_categories():
    # §5: categories non-empty
    err(spec={"categories": [], "values": []})


def test_highlight_index_out_of_range():
    # §5: a highlight index in range
    err(spec={"categories": ["a", "b"], "values": [1, 2], "highlight": 2})


def test_max_below_value():
    # §5: max >= every value
    err(spec={"categories": ["a", "b"], "values": [1, 20], "max": 10})


def test_non_finite_value():
    # §5: values finite
    err(spec={"categories": ["a"], "values": [math.inf]})
