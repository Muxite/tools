"""deck spec input and validation (MANIFEST §3.1, §3.2 arguments, §0.2)."""
import json

import pytest

from helpers_deck import ToolError, call, content, divider, make_png, need_office, spec, title_slide, write_json


@pytest.fixture(autouse=True)
def _office():
    need_office()


def build_err(tmp_path, the_spec, **kw):
    """deck_build must raise ToolError (§3.1 validation); returns the message."""
    with pytest.raises(ToolError()) as ei:
        call("deck_build", spec=the_spec, out=str(tmp_path / "x.pptx"), **kw)
    return str(ei.value)


def test_minimal_spec_without_meta_builds(tmp_path):
    # §3.1: meta is optional; type defaults to content
    s = {"slides": [{"title": "Only slide", "eyebrow": "E",
                     "body": {"kind": "bullets", "items": ["a"]}, "notes": {"time": "0:30"}}]}
    res = call("deck_build", spec=s, out=str(tmp_path / "a.pptx"))
    assert res["inserts"] == "shown"
    assert res["slides"][0]["type"] == "content"
    assert (tmp_path / "a.pptx").is_file()


def test_spec_and_spec_path_both_given_is_error(tmp_path):
    # §3.1: exactly 1 of spec / spec_path
    p = write_json(tmp_path / "s.json", spec(content()))
    with pytest.raises(ToolError()):
        call("deck_build", spec=spec(content()), spec_path=str(p), out=str(tmp_path / "x.pptx"))


def test_neither_spec_nor_spec_path_is_error(tmp_path):
    # §3.1
    with pytest.raises(ToolError()):
        call("deck_build", out=str(tmp_path / "x.pptx"))


def test_spec_path_builds_same_as_inline(tmp_path):
    # §3.1: spec may come from a .json file
    s = spec(title_slide(), content(title="From a file"))
    p = write_json(tmp_path / "deck.json", s)
    res = call("deck_build", spec_path=str(p), out=str(tmp_path / "f.pptx"))
    assert [x["title"] for x in res["slides"]] == ["Deck title", "From a file"]


def test_unknown_slide_type(tmp_path):
    # §3.1: unknown type is a problem, with a JSON-path prefix
    s = spec(content(), content(type="closing"))
    msg = build_err(tmp_path, s)
    assert "slides[1]" in msg


def test_unknown_stage(tmp_path):
    # §3.1: stage must be a palette.STAGE key
    msg = build_err(tmp_path, spec(content(stage="nonsense")))
    assert "slides[0].stage" in msg


def test_unknown_body_kind(tmp_path):
    # §3.1
    msg = build_err(tmp_path, spec(content(body={"kind": "video", "items": []})))
    assert "slides[0].body" in msg


def test_missing_title_on_content_slide(tmp_path):
    # §3.1: a missing title is a problem
    s = content()
    del s["title"]
    msg = build_err(tmp_path, spec(title_slide(), s))
    assert "slides[1]" in msg
    assert "title" in msg


def test_missing_figure_file(tmp_path):
    # §3.1: a missing figure file is a problem
    msg = build_err(tmp_path, spec(content(body={"kind": "figure", "path": "nope.png"})))
    assert "slides[0].body" in msg


def test_table_rows_unequal_length(tmp_path):
    # §3.1: all rows the same length
    body = {"kind": "table", "rows": [["a", "b"], ["c"]]}
    msg = build_err(tmp_path, spec(content(body=body)))
    assert "slides[0].body" in msg


def test_chart_categories_values_length_mismatch(tmp_path):
    # §3.1
    body = {"kind": "chart", "categories": ["a", "b", "c"], "values": [1, 2]}
    msg = build_err(tmp_path, spec(content(body=body)))
    assert "slides[0].body" in msg


def test_bad_inserts_value_in_meta(tmp_path):
    # §3.1: inserts ∈ shown | hidden | off
    msg = build_err(tmp_path, spec(content(), inserts="sometimes"))
    assert "meta.inserts" in msg


@pytest.mark.parametrize("bad", ["0:5", "1:60", ":30", "1.30"])
def test_bad_time_formats(tmp_path, bad):
    # §3.1: M:SS, 1+ digit minutes, exactly 2 digit seconds < 60
    msg = build_err(tmp_path, spec(content(), content(time=bad)))
    assert "slides[1].notes.time" in msg


@pytest.mark.parametrize("good,seconds", [("0:59", 59), ("12:05", 725)])
def test_good_time_formats(tmp_path, good, seconds):
    # §3.1 time format; §3.2 slides[].seconds
    res = call("deck_build", spec=spec(content(time=good)), out=str(tmp_path / "t.pptx"))
    assert res["slides"][0]["seconds"] == seconds


def test_missing_notes_time(tmp_path):
    # §3.1: notes.time is required on every slide
    s = divider()
    s["notes"] = {"say": "no time here"}
    msg = build_err(tmp_path, spec(content(), s))
    assert "slides[1].notes" in msg


def test_several_problems_reported_in_one_error(tmp_path):
    # §3.1: every problem is collected into 1 ToolError
    s = spec(content(stage="bogus"), content(time="7"), content(body={"kind": "nope"}))
    msg = build_err(tmp_path, s)
    assert "slides[0].stage" in msg
    assert "slides[1].notes.time" in msg
    assert "slides[2].body" in msg


def test_insert_on_first_slide_is_error(tmp_path):
    # §3.1: insert only after at least 1 core content, title or divider slide
    build_err(tmp_path, spec(content(insert=True), content()))


def test_relative_figure_path_resolves_against_spec_file_dir(tmp_path, monkeypatch):
    # §3.1: relative paths inside a spec file resolve against the spec file's directory
    d = tmp_path / "specdir"
    d.mkdir()
    make_png(d / "fig.png", 800, 400)
    p = write_json(d / "deck.json", spec(content(body={"kind": "figure", "path": "fig.png"})))
    other = tmp_path / "elsewhere"
    other.mkdir()
    monkeypatch.chdir(other)
    res = call("deck_build", spec_path=str(p), out=str(tmp_path / "o.pptx"))
    assert res["core_slides"] == 1


def test_relative_out_resolves_against_cwd(tmp_path, monkeypatch):
    # §0.2: relative paths resolve against the current working directory; results are strings
    monkeypatch.chdir(tmp_path)
    res = call("deck_build", spec=spec(content()), out="rel.pptx")
    assert isinstance(res["out"], str)
    assert (tmp_path / "rel.pptx").is_file()


def test_unknown_argument_rejected(tmp_path):
    # §0.2: schemas have additionalProperties false
    with pytest.raises(ToolError()):
        call("deck_build", spec=spec(content()), out=str(tmp_path / "x.pptx"), colour="red")


def test_result_is_json_serialisable(tmp_path):
    # §0.2
    res = call("deck_build", spec=spec(title_slide(), content()), out=str(tmp_path / "j.pptx"))
    json.dumps(res)
