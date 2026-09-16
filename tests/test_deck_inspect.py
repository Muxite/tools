"""deck_inspect (MANIFEST §3.4)."""
import pytest

from helpers_deck import ToolError, call, content, make_pptx, spec, title_slide


@pytest.fixture(autouse=True)
def _pptx():
    pytest.importorskip("pptx")


def test_inspect_handmade_deck(tmp_path):
    # §3.4: index 1-based, number, texts in shape order, notes, seconds, say_words, insert, hidden
    p = make_pptx(tmp_path / "h.pptx", [
        {"texts": [("Welcome", 40), ("by me", 16)], "notes": "TIME 0:15\nSAY: one two three"},
        {"texts": [("Findings", 30), ("3", 10)], "notes": "TIME 1:05\nSAY: a b c d\nIF ASKED:\n- q1"},
        {"texts": [("Detail", 30), ("3a", 10)], "hidden": True,
         "notes": "INSERT: optional slide; delete or hide it and the talk flows unchanged\nTIME 0:30"},
        {"texts": [("No notes", 30)]},
    ])
    res = _inspect(p)
    sl = res["slides"]
    assert [s["index"] for s in sl] == [1, 2, 3, 4]
    assert [s["number"] for s in sl] == [None, "3", "3a", None]
    assert sl[0]["texts"] == ["Welcome", "by me"]
    assert sl[1]["texts"] == ["Findings", "3"]
    assert sl[1]["notes"] == "TIME 1:05\nSAY: a b c d\nIF ASKED:\n- q1"
    assert [s["seconds"] for s in sl] == [15, 65, 30, None]
    assert sl[0]["say_words"] == 3 and sl[1]["say_words"] == 4
    assert [s["insert"] for s in sl] == [False, False, True, False]
    assert [s["hidden"] for s in sl] == [False, False, True, False]
    assert isinstance(res["path"], str)


def _inspect(p):
    """§3.4 does not name the argument; use the schema's single required property
    (else `pptx_path` or `path`, whichever exists)."""
    from helpers_deck import get_tool

    schema = get_tool("deck_inspect").input_schema
    req = schema.get("required", [])
    props = schema.get("properties", {})
    key = req[0] if len(req) == 1 else ("pptx_path" if "pptx_path" in props else "path")
    return call("deck_inspect", **{key: str(p)})


def test_inspect_table_cells_after_frames(tmp_path):
    # §3.4: table cells row by row, after the frames
    p = make_pptx(tmp_path / "t.pptx", [
        {"texts": [("Table slide", 30), ("1", 10)], "table": [["h1", "h2"], ["c1", "c2"]],
         "notes": "TIME 0:30"},
    ])
    res = _inspect(p)
    assert res["slides"][0]["texts"] == ["Table slide", "1", "h1", "h2", "c1", "c2"]


def test_inspect_built_deck(tmp_path):
    # §3.4 on a §3.2-built deck with hidden inserts
    pytest.importorskip("PIL")
    s = spec(title_slide(), content(title="Core", time="0:40", say="alpha beta"),
             content(title="Ins", insert=True, time="0:20"), inserts="hidden")
    out = tmp_path / "b.pptx"
    call("deck_build", spec=s, out=str(out))
    sl = _inspect(out)["slides"]
    assert len(sl) == 3
    assert [x["number"] for x in sl] == [None, "2", "2a"]
    assert [x["hidden"] for x in sl] == [False, False, True]
    assert [x["insert"] for x in sl] == [False, False, True]
    assert [x["seconds"] for x in sl] == [15, 40, 20]
    assert sl[1]["say_words"] == 2
    assert "Core" in sl[1]["texts"]


def test_inspect_missing_file(tmp_path):
    # §0.2: bad input raises ToolError
    with pytest.raises(ToolError()):
        _inspect(tmp_path / "missing.pptx")
