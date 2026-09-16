"""MANIFEST §14.5 deck_build: lists of blocks with positions and sizes, the `point` block, chart_type and
highlight_color, and figures that shrink to fit above the THUS strip."""
from __future__ import annotations

import pytest

from helpers_deck import (
    EMU_PER_INCH, ToolError, build, call, charts, content, frame_is_bold, iter_shapes, make_png, need_office,
    pictures, point_fill, rules, spec,
)

IN = EMU_PER_INCH
TOL = 0.03


def inches(v):
    return v / IN


def box(sh):
    return inches(sh.left), inches(sh.top), inches(sh.left + sh.width), inches(sh.top + sh.height)


def text_shape(slide, startswith):
    hits = [sh for sh in iter_shapes(slide.shapes) if sh.has_text_frame and sh.text_frame.text.startswith(startswith)]
    assert hits, f"no text shape starting with {startswith!r}"
    return hits[0]


def table_shape(slide):
    hits = [sh for sh in iter_shapes(slide.shapes) if getattr(sh, "has_table", False) and sh.has_table]
    assert len(hits) == 1
    return hits[0]


def run_sizes(tf):
    return {r.font.size.pt if r.font.size is not None else (p.font.size.pt if p.font.size else None)
            for p in tf.paragraphs for r in p.runs if r.text.strip()}


BULLETS = {"kind": "bullets", "items": ["Models propose", "Code checks"]}
TABLE = {"kind": "table", "rows": [["Step", "Author"], ["Compile intent", "A model"], ["Validate", "Code"]]}


@pytest.fixture(autouse=True)
def _office():
    need_office()


# ====================================================================== lists of blocks
def test_body_list_stacks_blocks_top_to_bottom(tmp_path):
    """§14.5: without positions, blocks stack top to bottom in the body area."""
    res, prs = build(tmp_path, spec(content(body=[BULLETS, TABLE])))
    slide = prs.slides[0]
    b = box(text_shape(slide, "•  Models propose"))
    t = box(table_shape(slide))
    assert b[1] < t[1]
    assert b[3] <= t[1] + TOL
    assert b[1] >= 1.38 and t[3] <= 7.5
    assert res["warnings"] == []


def test_body_single_block_still_accepted(tmp_path):
    """§14.5: `body` may still be a single block."""
    _, prs = build(tmp_path, spec(content(body=BULLETS)))
    assert text_shape(prs.slides[0], "•  Models propose").text_frame.text == "•  Models propose\n•  Code checks"


def test_block_positions_in_inches(tmp_path):
    """§14.5: a block's x, y, w, h are inches."""
    block = {"kind": "point", "text": "Models propose, code checks", "x": 1.0, "y": 2.0, "w": 6.0, "h": 0.8}
    _, prs = build(tmp_path, spec(content(body=[block, dict(BULLETS, x=7.5, y=2.0, w=5.0, h=3.0)])))
    slide = prs.slides[0]
    assert box(text_shape(slide, "Models propose, code checks")) == pytest.approx((1.0, 2.0, 7.0, 2.8), abs=TOL)
    assert box(text_shape(slide, "•  Models propose")) == pytest.approx((7.5, 2.0, 12.5, 5.0), abs=TOL)


def test_block_size_in_points(tmp_path):
    """§14.5: a block's `size` sets its text size in pt."""
    _, prs = build(tmp_path, spec(content(body=[dict(BULLETS, size=14)])))
    assert run_sizes(text_shape(prs.slides[0], "•  Models propose").text_frame) == {14}


def test_point_block(tmp_path):
    """§14.5: `point` is 1 bold line of 20 pt text."""
    text = "The freeze fixes the grading rules before anything runs"
    _, prs = build(tmp_path, spec(content(body={"kind": "point", "text": text})))
    sh = text_shape(prs.slides[0], text)
    assert sh.text_frame.text == text
    assert frame_is_bold(sh.text_frame)
    assert run_sizes(sh.text_frame) == {20}


def test_warnings_apply_per_block(tmp_path):
    """§14.5: the warning rules apply to each block of a list."""
    long_block = {"kind": "bullets", "items": ["x" * 2000]}
    res, _ = build(tmp_path, spec(content(body=[{"kind": "point", "text": "Short point"}, long_block])))
    assert res["warnings"]
    assert all(w.startswith("slide 1: ") for w in res["warnings"])


def test_positioned_block_too_small_warns(tmp_path):
    """§14.5: a positioned block whose text overflows its own box is warned about."""
    items = ["A capsule is a contract for 1 capability, written in YAML, with typed inputs and outputs"] * 4
    block = {"kind": "bullets", "items": items, "x": 1.0, "y": 2.0, "w": 3.0, "h": 0.5}
    res, _ = build(tmp_path, spec(content(body=[block])))
    assert any(w.startswith("slide 1: ") for w in res["warnings"])


def test_bad_block_in_list_is_a_problem(tmp_path):
    """§14.5 with §3.1 validation: a bad block inside the list is reported under slides[0].body."""
    with pytest.raises(ToolError()) as exc:
        call("deck_build", spec=spec(content(body=[BULLETS, {"kind": "video"}])), out=str(tmp_path / "o.pptx"))
    assert "slides[0].body" in str(exc.value)


def test_point_without_text_is_a_problem(tmp_path):
    """§14.5: point needs `text` (str)."""
    with pytest.raises(ToolError()) as exc:
        call("deck_build", spec=spec(content(body={"kind": "point"})), out=str(tmp_path / "o.pptx"))
    assert "slides[0].body" in str(exc.value)


def test_lint_reads_every_block(tmp_path):
    """§14.5 with §3.3: face text covers every block of a list (D010 in the second block)."""
    body = [{"kind": "point", "text": "Kept tools fail"}, {"kind": "bullets", "items": ["Zheng et al. show it"]}]
    res = call("deck_lint", spec=spec(content(body=body, source="Beyond Task Completion, Table 4")))
    assert [f["line"] for f in rules(res, "D010")] == [1]


# ====================================================================== charts
CHART = {"kind": "chart", "categories": ["kept", "passed", "failed"], "values": [222, 7, 215], "highlight": 2}


def test_chart_type_line(tmp_path):
    """§14.5: chart_type `line` makes a native line chart with the same data."""
    _, prs = build(tmp_path, spec(content(body=dict(CHART, chart_type="line"))))
    ch = charts(prs.slides[0])
    assert len(ch) == 1
    assert "LINE" in ch[0].chart_type.name
    assert list(ch[0].plots[0].categories) == ["kept", "passed", "failed"]
    assert list(ch[0].plots[0].series[0].values) == pytest.approx([222, 7, 215])


def test_chart_type_bar_explicit(tmp_path):
    """§14.5: chart_type `bar` (the default) is a bar chart."""
    _, prs = build(tmp_path, spec(content(body=dict(CHART, chart_type="bar"))))
    name = charts(prs.slides[0])[0].chart_type.name
    assert "BAR" in name or "COLUMN" in name


@pytest.mark.parametrize("key,hexval", [("failed", "D55E00"), ("claims", "B8527F"), ("running", "D98200")])
def test_highlight_color_keys(tmp_path, key, hexval):
    """§14.5: highlight_color takes a STAGE or OUTCOME key."""
    _, prs = build(tmp_path, spec(content(body=dict(CHART, highlight_color=key))))
    ser = charts(prs.slides[0])[0].plots[0].series[0]
    assert point_fill(ser, 2) == hexval
    assert point_fill(ser, 0) != hexval


def test_highlight_color_default_gates(tmp_path):
    """§14.5: highlight_color defaults to gates."""
    _, prs = build(tmp_path, spec(content(body=CHART)))
    assert point_fill(charts(prs.slides[0])[0].plots[0].series[0], 2) == "008A63"


@pytest.mark.parametrize("extra", [{"chart_type": "pie"}, {"highlight_color": "red"}])
def test_bad_chart_options_are_problems(tmp_path, extra):
    """§14.5: unknown chart_type or highlight_color keys are validation problems."""
    with pytest.raises(ToolError()) as exc:
        call("deck_build", spec=spec(content(body=dict(CHART, **extra))), out=str(tmp_path / "o.pptx"))
    assert "slides[0].body" in str(exc.value)


# ====================================================================== figure shrink
def test_figure_below_block_shrinks_above_thus(tmp_path):
    """§14.5: a figure without h fits between the block above it and the THUS strip."""
    make_png(tmp_path / "tall.png", 600, 1200)
    body = [{"kind": "point", "text": "The library only grows"}, {"kind": "figure", "path": str(tmp_path / "tall.png")}]
    s = spec(content(body=body, thus="Retirement needs its own gate",
                     demonstrated_by={"paper": "Alita-G (arXiv 2510.23601)", "setup": "128 tools"}))
    res, prs = build(tmp_path, s)
    slide = prs.slides[0]
    pic = pictures(slide)
    assert len(pic) == 1
    p = box(pic[0])
    above = box(text_shape(slide, "The library only grows"))
    thus = box(text_shape(slide, "THUS"))
    assert p[1] >= above[3] - TOL
    assert p[3] <= thus[1] + TOL
    assert p[3] <= 6.9 + TOL
    assert (p[2] - p[0]) / (p[3] - p[1]) == pytest.approx(0.5, rel=0.02)


def test_figure_between_strips_shrinks(tmp_path):
    """§14.5: a single figure sits between the DEMONSTRATED BY strip and the THUS strip."""
    make_png(tmp_path / "tall.png", 500, 1000)
    s = spec(content(body={"kind": "figure", "path": str(tmp_path / "tall.png")}, thus="Keep the gate fixed",
                     demonstrated_by={"paper": "Beyond Task Completion (arXiv 2604.00392)", "setup": "99 tasks"},
                     phase={"in": "goal text", "out": "frozen contract"}))
    _, prs = build(tmp_path, s)
    slide = prs.slides[0]
    p = box(pictures(slide)[0])
    top_strip = box(text_shape(slide, "IN"))
    thus = box(text_shape(slide, "THUS"))
    assert p[1] >= top_strip[3] - TOL
    assert p[3] <= thus[1] + TOL


def test_figure_without_strips_runs_to_body_bottom(tmp_path):
    """§14.5: with no THUS strip the limit is 6.9 in."""
    make_png(tmp_path / "tall.png", 400, 1600)
    body = [{"kind": "point", "text": "A tall figure"}, {"kind": "figure", "path": str(tmp_path / "tall.png")}]
    _, prs = build(tmp_path, spec(content(body=body)))
    p = box(pictures(prs.slides[0])[0])
    assert p[3] <= 6.9 + TOL
    assert p[1] >= box(text_shape(prs.slides[0], "A tall figure"))[3] - TOL
