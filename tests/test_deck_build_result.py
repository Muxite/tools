"""deck_build: the result dict, budget, times ledger, warnings, output path (MANIFEST §3.2)."""
import json
import re

import pytest

from helpers_deck import SAY25, ToolError, build, call, content, divider, need_office, spec, title_slide


@pytest.fixture(autouse=True)
def _office():
    need_office()


def test_result_counts_and_times(tmp_path):
    # §3.2 result: core/insert counts and seconds; M:SS times; total = core + inserts
    s = spec(title_slide(time="0:15"), content(time="4:00"), content(time="1:30", insert=True),
             divider(time="0:05"), content(time="5:40"))
    res, _ = build(tmp_path, s)
    assert res["core_slides"] == 4
    assert res["insert_slides"] == 1
    assert res["core_seconds"] == 15 + 240 + 5 + 340
    assert res["insert_seconds"] == 90
    assert res["core_time"] == "10:00"
    assert res["total_time"] == "11:30"
    assert res["ledger"] is None
    assert res["out"].endswith("out.pptx")


def test_result_slides_entries(tmp_path):
    # §3.2: slides lists every spec slide; number null for title/divider; say_words = SAY word count
    s = spec(title_slide(title="T", say="one two three"), content(title="C", time="0:45", say=SAY25),
             content(title="I", insert=True, time="0:20", say="a b"))
    res, _ = build(tmp_path, s)
    got = [(x["number"], x["type"], x["title"], x["insert"], x["seconds"], x["say_words"]) for x in res["slides"]]
    assert got == [(None, "title", "T", False, 15, 3), ("2", "content", "C", False, 45, 25),
                   ("2a", "content", "I", True, 20, 2)]


def test_budget_defaults_and_ok(tmp_path):
    # §3.2 / §3.1: budget defaults 40:00 / 45:00
    res, _ = build(tmp_path, spec(content(time="5:00")))
    assert res["budget"] == {"target": "40:00", "max": "45:00", "status": "ok"}


def test_budget_over_target(tmp_path):
    # §3.2: status from core_seconds; meta budget used
    res, _ = build(tmp_path, spec(content(time="3:00"), budget={"target": "2:00", "max": "4:00"}))
    assert res["budget"]["status"] == "over target"
    assert res["budget"]["target"] == "2:00" and res["budget"]["max"] == "4:00"


def test_budget_over_budget_and_warning(tmp_path):
    # §3.2: OVER BUDGET; a warning when core time exceeds the budget max
    res, _ = build(tmp_path, spec(content(time="50:00")))
    assert res["budget"]["status"] == "OVER BUDGET"
    assert res["warnings"], "core time above max must warn"


def test_inserts_do_not_count_toward_budget(tmp_path):
    # §3.2: status comes from core_seconds only
    s = spec(content(time="1:00"), content(time="10:00", insert=True), budget={"target": "2:00", "max": "3:00"})
    res, _ = build(tmp_path, s)
    assert res["budget"]["status"] == "ok"


def test_times_file_created(tmp_path):
    # §3.2 times_file: {id: core, id_inserts: inserts}, created if needed
    tf = tmp_path / "deck-times.json"
    s = spec(content(time="2:00"), content(time="0:30", insert=True), id="capsule")
    res, _ = build(tmp_path, s, times_file=str(tf))
    data = json.loads(tf.read_text(encoding="utf-8"))
    assert data == {"capsule": 120, "capsule_inserts": 30}
    led = res["ledger"]
    assert led["decks"]["capsule"] == 120
    assert led["combined_seconds"] == 120
    assert led["combined_time"] == "2:00"
    assert led["status"] == "ok"
    assert isinstance(led["path"], str)


def test_times_file_combines_decks(tmp_path):
    # §3.2: combined_seconds sums the non-_inserts entries of every deck; status compares the sum
    tf = tmp_path / "times.json"
    tf.write_text(json.dumps({"general": 1500, "general_inserts": 600}), encoding="utf-8")
    s = spec(content(time="16:00"), id="capsule")
    res, _ = build(tmp_path, s, times_file=str(tf))
    data = json.loads(tf.read_text(encoding="utf-8"))
    assert data["general"] == 1500 and data["general_inserts"] == 600
    assert data["capsule"] == 960 and data["capsule_inserts"] == 0
    led = res["ledger"]
    assert led["combined_seconds"] == 2460
    assert led["combined_time"] == "41:00"
    assert led["status"] == "over target"
    assert led["decks"]["capsule"] == 960


def test_times_file_requires_meta_id(tmp_path):
    # §3.2: meta.id is required when times_file is given
    need_office()
    with pytest.raises(ToolError()):
        call("deck_build", spec=spec(content()), out=str(tmp_path / "x.pptx"),
             times_file=str(tmp_path / "t.json"))


def test_long_bullet_warns(tmp_path):
    # §3.2: a single 2,000-character bullet must produce at least 1 warning, prefixed "slide ..: "
    res, _ = build(tmp_path, spec(content(body={"kind": "bullets", "items": ["x" * 2000]})))
    assert res["warnings"]
    assert all(re.match(r"^slide [^:]+: ", w) for w in res["warnings"])
    assert any(w.startswith("slide 1: ") for w in res["warnings"])


def test_three_short_bullets_no_warnings(tmp_path):
    # §3.2: 3 short bullets produce no warning
    res, _ = build(tmp_path, spec(content(body={"kind": "bullets", "items": ["one", "two", "three"]})))
    assert res["warnings"] == []


def test_long_strip_warns(tmp_path):
    # §3.2: a strip whose text is too long for 1 line warns
    long = "a very long conclusion " * 20
    res, _ = build(tmp_path, spec(content(thus=long)))
    assert any(w.startswith("slide 1: ") for w in res["warnings"])


def test_long_table_warns(tmp_path):
    # §3.2: a table estimated to run past the slide bottom warns
    rows = [["h1", "h2"]] + [[f"r{i}", "value"] for i in range(30)]
    res, _ = build(tmp_path, spec(content(body={"kind": "table", "rows": rows})))
    assert any(w.startswith("slide 1: ") for w in res["warnings"])


def test_out_parent_missing_is_error(tmp_path):
    # §3.2: the output's parent directory must exist
    need_office()
    with pytest.raises(ToolError()):
        call("deck_build", spec=spec(content()), out=str(tmp_path / "no" / "such" / "x.pptx"))


def test_existing_out_is_overwritten(tmp_path):
    # §3.2: an existing out is overwritten
    from pptx import Presentation

    out = tmp_path / "out.pptx"
    out.write_bytes(b"old junk")
    call("deck_build", spec=spec(content(), content()), out=str(out))
    assert len(Presentation(str(out)).slides) == 2
