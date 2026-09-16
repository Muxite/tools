"""deck_lint on specs and on .pptx files (MANIFEST §3.3, §0.3)."""
import pytest

from helpers_deck import (SAY25, ToolError, call, check_shape, content, divider, make_pptx, rules, spec,
                          title_slide, write_json)


def words(n):
    return " ".join(f"w{i}" for i in range(n))


def lint(the_spec, **kw):
    res = call("deck_lint", spec=the_spec, **kw)
    check_shape(res)
    return res


def clean(**kw):
    """A content slide that triggers no rule."""
    kw.setdefault("source", "Some paper, Table 1")
    return content(**kw)


# ------------------------------------------------------------------ shape
def test_clean_spec_is_ok(tmp_path):
    # §3.3 / §0.3 result shape
    res = lint(spec(title_slide(), clean(), clean(time="1:00")))
    assert res["ok"] is True
    assert res["findings"] == []
    assert res["counts"] == {"error": 0, "warning": 0, "info": 0}
    assert res["slides"] == 3
    assert res["core_seconds"] == 15 + 30 + 60
    assert res["insert_seconds"] == 0
    assert res["core_time"] == "1:45"


def test_inline_spec_path_is_placeholder_and_line_is_position():
    # §3.3: path <spec> for inline specs; line = 1-based slide position
    res = lint(spec(title_slide(), clean(), clean(title="Bad — title")))
    f = rules(res, "D003")
    assert len(f) == 1
    assert f[0]["path"] == "<spec>"
    assert f[0]["line"] == 3
    assert f[0]["severity"] == "error"
    assert res["ok"] is False


def test_spec_path_given_is_reported(tmp_path):
    # §3.3 / §0.3: path is the spec path as given, with / separators
    p = write_json(tmp_path / "deck.json", spec(clean(title="A — B")))
    res = call("deck_lint", spec_path=p.as_posix())
    check_shape(res)
    assert rules(res, "D003")[0]["path"] == p.as_posix()


def test_exactly_one_source_required(tmp_path):
    # §3.3: spec | spec_path | pptx_path, exactly 1
    with pytest.raises(ToolError()):
        call("deck_lint")
    p = write_json(tmp_path / "d.json", spec(clean()))
    with pytest.raises(ToolError()):
        call("deck_lint", spec=spec(clean()), spec_path=str(p))


# ------------------------------------------------------------------ D001 / D002
def test_d001_over_rate():
    # §3.3 D001: 24 words > 10 s x 2.3 = 23
    res = lint(spec(clean(time="0:10", say=words(24))))
    f = rules(res, "D001")
    assert len(f) == 1 and f[0]["severity"] == "error" and f[0]["line"] == 1


def test_d001_custom_rate_argument():
    # §3.3: words_per_second argument; 45 words > 20 s x 2 = 40
    res = lint(spec(clean(time="0:20", say=words(45))), words_per_second=2)
    assert len(rules(res, "D001")) == 1
    res = lint(spec(clean(time="0:20", say=words(45))), words_per_second=3)
    assert rules(res, "D001") == []


def test_d002_short_say_on_core_content():
    # §3.3 D002: a core content slide with fewer than 20 SAY words
    res = lint(spec(title_slide(say="hi"), clean(say=words(19)), clean(say=words(20))))
    f = rules(res, "D002")
    assert [x["line"] for x in f] == [2]
    assert f[0]["severity"] == "warning"
    assert res["ok"] is True


def test_d002_not_for_insert_slides():
    # §3.3 D002 applies to core content slides only
    res = lint(spec(clean(), clean(insert=True, say="short")))
    assert rules(res, "D002") == []


# ------------------------------------------------------------------ D003 - D005
def test_d003_em_dash_in_title_any_type():
    # §3.3 D003
    res = lint(spec(title_slide(title="Tools — safely"), divider(title="Part — two"), clean()))
    assert [x["line"] for x in rules(res, "D003")] == [1, 2]


def test_d003_not_for_eyebrow_or_say():
    # §3.3 D003 is about titles only
    res = lint(spec(clean(eyebrow="Research — 2026", say=SAY25 + " — ok")))
    assert rules(res, "D003") == []


def test_d004_must_hit_in_say():
    # §3.3 D004
    res = lint(spec(clean(say=SAY25 + " MUST HIT the numbers")))
    f = rules(res, "D004")
    assert len(f) == 1 and f[0]["severity"] == "error"


def test_d004_point_of_this_slide_in_asked():
    # §3.3 D004: notes include IF ASKED lines
    res = lint(spec(clean(asked=["The point of this slide is cost"])))
    assert len(rules(res, "D004")) == 1


@pytest.mark.parametrize("phrase", ["I'm not going to", "this talk will"])
def test_d005_defensive_phrases(phrase):
    # §3.3 D005, case-insensitive
    res = lint(spec(clean(say=SAY25 + f" {phrase} explain it.")))
    f = rules(res, "D005")
    assert len(f) == 1 and f[0]["severity"] == "warning"


# ------------------------------------------------------------------ D006 / D007
def test_d006_back_reference_on_insert():
    # §3.3 D006: an insert slide whose SAY says "as we saw"
    res = lint(spec(clean(), clean(insert=True, say=SAY25 + " As we saw before.")))
    f = rules(res, "D006")
    assert [x["line"] for x in f] == [2]
    assert f[0]["severity"] == "error"


def test_d006_not_on_core_slide():
    # §3.3 D006 applies to insert slides only
    res = lint(spec(clean(say=SAY25 + " as we saw before, next slide")))
    assert rules(res, "D006") == []


def test_d007_core_mentions_insert_number():
    # §3.3 D007: a non-insert slide mentioning "slide 4a"
    res = lint(spec(clean(), clean(say=SAY25 + " see slide 4a for detail")))
    f = rules(res, "D007")
    assert [x["line"] for x in f] == [2]


def test_d007_plain_number_is_fine():
    # §3.3 D007 needs a letter suffix
    res = lint(spec(clean(say=SAY25 + " see slide 4 for detail")))
    assert rules(res, "D007") == []


# ------------------------------------------------------------------ D008 - D011
def test_d008_over_max_error_line_null():
    # §3.3 D008: core total over max is an error with line null and path the deck
    res = lint(spec(clean(time="3:00")), target="1:00", max="2:00")
    f = rules(res, "D008")
    assert len(f) == 1
    assert f[0]["severity"] == "error" and f[0]["line"] is None and f[0]["path"] == "<spec>"


def test_d008_over_target_warning():
    # §3.3 D008: over target is a warning
    res = lint(spec(clean(time="1:30")), target="1:00", max="2:00")
    f = rules(res, "D008")
    assert len(f) == 1 and f[0]["severity"] == "warning"


def test_d008_defaults_from_meta_budget():
    # §3.3: target/max default to the meta budget
    res = lint(spec(clean(time="1:30"), budget={"target": "1:00", "max": "5:00"}))
    assert [x["severity"] for x in rules(res, "D008")] == ["warning"]
    res = lint(spec(clean(time="30:00")))
    assert rules(res, "D008") == []


def test_d009_missing_source_on_content_only():
    # §3.3 D009 (spec)
    s = content()
    s.pop("source", None)
    res = lint(spec(title_slide(), s, clean()))
    f = rules(res, "D009")
    assert [x["line"] for x in f] == [2]
    assert f[0]["severity"] == "warning"


def test_d010_et_al_in_face_text():
    # §3.3 D010: face text includes body text
    res = lint(spec(clean(body={"kind": "bullets", "items": ["Smith et al. found it"]})))
    f = rules(res, "D010")
    assert len(f) == 1 and f[0]["severity"] == "warning"


def test_d011_long_title():
    # §3.3 D011: longer than 90 characters
    res = lint(spec(clean(title="t" * 91), clean(title="u" * 90)))
    assert [x["line"] for x in rules(res, "D011")] == [1]


def test_findings_sorted():
    # §0.3: sorted by (path, line or 0, rule)
    s = spec(clean(title="X — " + "y" * 95, say="short"), clean(time="9:00"))
    res = lint(s, target="1:00", max="2:00")
    ids = [(f["line"] or 0, f["rule"]) for f in res["findings"]]
    assert ids == sorted(ids)
    assert ids[0] == (0, "D008")


# ------------------------------------------------------------------ pptx mode
def test_pptx_mode_basic(tmp_path):
    # §3.3 pptx: content = has a number frame; insert = notes start INSERT:; TIME/SAY from notes
    pytest.importorskip("pptx")
    p = make_pptx(tmp_path / "d.pptx", [
        {"texts": [("Opening", 40)], "notes": "TIME 0:20\nSAY: hello"},
        {"texts": [("RESEARCH", 11), ("Kept tools fail", 30), ("2", 10)],
         "notes": "TIME 0:10\nSAY: " + words(24) + "\nIF ASKED:\n- a question here"},
        {"texts": [("Extra", 30), ("2a", 10)],
         "notes": "INSERT: optional slide; delete or hide it and the talk flows unchanged\nTIME 1:00\nSAY: tiny"},
    ])
    res = call("deck_lint", pptx_path=p.as_posix())
    check_shape(res)
    assert res["slides"] == 3
    assert res["core_seconds"] == 30
    assert res["insert_seconds"] == 60
    assert [x["line"] for x in rules(res, "D001")] == [2]
    assert rules(res, "D002") == []
    assert rules(res, "D009") == []
    assert all(f["path"] == p.as_posix() for f in res["findings"] if f["line"] is not None)


def test_pptx_mode_d012_missing_time(tmp_path):
    # §3.3 D012: a slide without a TIME
    pytest.importorskip("pptx")
    p = make_pptx(tmp_path / "d.pptx", [
        {"texts": [("Title", 40)], "notes": "TIME 0:10"},
        {"texts": [("No time", 30), ("2", 10)], "notes": "SAY: " + SAY25},
    ])
    res = call("deck_lint", pptx_path=str(p))
    check_shape(res)
    f = rules(res, "D012")
    assert [x["line"] for x in f] == [2]
    assert f[0]["severity"] == "error"
    assert res["ok"] is False


def test_lint_built_deck_matches_spec_times(tmp_path):
    # §3.3 pptx parsing of a §3.2-built deck
    pytest.importorskip("pptx")
    pytest.importorskip("PIL")
    s = spec(title_slide(time="0:15"), clean(time="1:00"), clean(time="0:40", insert=True))
    out = tmp_path / "b.pptx"
    call("deck_build", spec=s, out=str(out))
    res = call("deck_lint", pptx_path=str(out))
    check_shape(res)
    assert res["core_seconds"] == 75
    assert res["insert_seconds"] == 40
    assert res["core_time"] == "1:15"
    assert res["slides"] == 3
