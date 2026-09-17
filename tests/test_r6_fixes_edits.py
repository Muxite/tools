"""Round 6 fixes: emitted edits into code (MANIFEST §19.1) and docx edits (§19.6), on top of §15.4, §15.5,
§16.3, §17.1 and §0.2."""
from __future__ import annotations

import json
import os

import pytest

import helpers_r6f as h

OLD = "Scores rose sharply this year"
KEEP = "Other paragraphs stay exactly as they were"


@pytest.fixture
def cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


# ------------------------------------------------------------------------------------ §19.1 escaping
def test_repro_quote_is_escaped_and_build_py_still_parses(cwd):
    """§19.1 reviewers' repro: `P1 = "Scores rose sharply this year"`, docx now says `Scores rose "sharply"
    this year`: the emitted replace escapes the quotes, and build.py parses after apply-edits."""
    h.write(cwd / "src" / "build.py", f'P1 = "{OLD}"\nP2 = "{KEEP}"\n')
    new = 'Scores rose "sharply" this year'
    res, edits, applied = h.emit_and_apply(cwd, [OLD, KEEP], [new, KEEP])
    assert res["edits_written"] == 1
    assert h.only_edit(edits) == {"find": OLD, "replace": 'Scores rose \\"sharply\\" this year', "count": 1}
    assert applied["ok"] is True, applied
    assert h.module_value(cwd / "src" / "build.py", "P1") == new
    assert h.module_value(cwd / "src" / "build.py", "P2") == KEEP


def test_trailing_backslash_is_escaped(cwd):
    """§19.1: a backslash (here the last character) is escaped, so the closing quote survives."""
    old = "Files are stored in the shared folder"
    new = "Files are stored in C:\\data\\"
    h.write(cwd / "src" / "build.py", f'WHERE = "{old}"\n')
    res, edits, applied = h.emit_and_apply(cwd, [old], [new])
    assert h.only_edit(edits)["replace"] == "Files are stored in C:\\\\data\\\\"
    assert applied["ok"] is True
    assert h.module_value(cwd / "src" / "build.py", "WHERE") == new


def test_docx_line_break_becomes_backslash_n(cwd):
    """§19.1/§16.3: a docx line break is `\\n` in the paragraph; in a "..." literal it is written as `\\n`."""
    old = "First line of the caption text"
    h.write(cwd / "src" / "build.py", f"CAPTION = '{old}'\n")
    res, edits, applied = h.emit_and_apply(cwd, [old], ["First line of the caption\nsecond line"])
    rep = h.only_edit(edits)["replace"]
    assert "\n" not in rep and "\\n" in rep
    assert applied["ok"] is True
    assert h.module_value(cwd / "src" / "build.py", "CAPTION") == "First line of the caption\nsecond line"


def test_json_literal_stays_valid(cwd):
    """§19.1: JSON targets use json.dumps escaping without the outer quotes."""
    h.write(cwd / "src" / "slides.json", json.dumps({"p": OLD, "q": KEEP}, indent=2) + "\n")
    new = 'Scores rose "sharply" in C:\\runs this year'
    res, edits, applied = h.emit_and_apply(cwd, [OLD, KEEP], [new, KEEP])
    assert h.only_edit(edits)["replace"] == json.dumps(new)[1:-1]
    assert applied["ok"] is True
    assert h.read_json(cwd / "src" / "slides.json") == {"p": new, "q": KEEP}


def test_triple_quoted_literal_keeps_plain_quotes(cwd):
    """§19.1: triple-quoted literals only escape backslashes and a run of 3 quotes."""
    h.write(cwd / "src" / "build.py", f'NOTE = """{OLD}"""\n')
    new = 'Scores rose "sharply" (as "planned") this year'
    res, edits, applied = h.emit_and_apply(cwd, [OLD], [new])
    assert h.only_edit(edits)["replace"] == new
    assert applied["ok"] is True
    assert h.module_value(cwd / "src" / "build.py", "NOTE") == new


# ------------------------------------------------------------------------------------ §19.1 not emitted
def _unsafe(cwd, source, new):
    h.write(cwd / "src" / "build.py", source)
    h.make_docx(cwd / "old.docx", [OLD])
    h.make_docx(cwd / "new.docx", [new])
    res = h.docx_diff("old.docx", "new.docx", search=["src"], emit_edits="edits.json")
    assert res["edits_written"] == 0
    assert res["not_emitted"] == [{"old_index": 0, "reason": "unsafe literal"}]
    assert h.read_json(cwd / "edits.json") == []
    assert h.read(cwd / "src" / "build.py") == source


def test_fstring_with_brace_not_emitted(cwd):
    """§19.1 reviewers' repro: an f-string target and new text containing `{appendix}`."""
    _unsafe(cwd, f'P1 = f"{OLD}"\n', "Scores rose sharply this year, see {appendix}")


def test_raw_string_needing_escape_not_emitted(cwd):
    """§19.1: a raw string target whose new text needs escaping (a quote)."""
    _unsafe(cwd, f'P1 = r"{OLD}"\n', 'Scores rose "sharply" this year')


# ------------------------------------------------------------------------------------ §19.1 existing target
def test_emit_edits_refuses_existing_python_file(cwd):
    """§19.1: emit_edits onto an existing non-JSON file (victim.py) is a ToolError; the file is untouched."""
    h.write(cwd / "src" / "notes.md", f"# Notes\n\n{OLD}\n")
    victim = h.write(cwd / "victim.py", "print('keep me')\n")
    h.make_docx(cwd / "old.docx", ["Notes", OLD])
    h.make_docx(cwd / "new.docx", ["Notes", "Scores rose steeply this year"])
    with pytest.raises(h.tool_error()):
        h.docx_diff("old.docx", "new.docx", search=["src"], emit_edits="victim.py")
    assert h.read(victim) == "print('keep me')\n"


def test_emit_edits_overwrites_previous_edits_list(cwd):
    """§19.1: a previous emitted-edits file (a JSON list) may be overwritten."""
    h.write(cwd / "src" / "notes.md", f"# Notes\n\n{OLD}\n")
    h.write(cwd / "edits.json", json.dumps([{"path": str(cwd / "x.md"), "edits": []}]))
    h.make_docx(cwd / "old.docx", ["Notes", OLD])
    h.make_docx(cwd / "new.docx", ["Notes", "Scores rose steeply this year"])
    res = h.docx_diff("old.docx", "new.docx", search=["src"], emit_edits="edits.json")
    assert res["edits_written"] == 1
    (obj,) = h.read_json(cwd / "edits.json")
    assert obj["edits"][0]["replace"] == "Scores rose steeply this year"


def test_docx_diff_not_read_only():
    """§19.1/§0.2: docx_diff writes with emit_edits, so it is annotated readOnlyHint false."""
    import tundlekit.textlint  # noqa: F401
    from tundlekit import registry

    assert registry.TOOLS["docx_diff"].annotations.get("readOnlyHint") is False


# ------------------------------------------------------------------------------------ §19.1 needles
def test_short_or_time_needles_give_no_hint(cwd):
    """§19.1 reviewers' repro: needles shorter than 8 characters or without a letter (the time `1:30`, the
    1-character `A`) are skipped."""
    for old, new, source in [("1:30", "1:45", 'TIME = "1:30"\n'), ("A", "B", 'GRADE = "A"\n')]:
        h.write(cwd / "src" / "timing.py", source)
        h.make_docx(cwd / "old.docx", ["Talk length and grading", old])
        h.make_docx(cwd / "new.docx", ["Talk length and grading", new])
        (c,) = h.docx_diff("old.docx", "new.docx", search=["src"])["changes"]
        assert c["hint"] == [], old


def test_empty_edits_with_missing_path_ok(cwd):
    """§19.1: an empty edits list is ok even when `path` names a missing file; nothing is created."""
    res = h.apply_edits(edits=[], path=str(cwd / "missing.md"), write=True)
    assert res["ok"] is True
    assert h.listing(cwd) == []


# ------------------------------------------------------------------------------------ §19.6 docx edits
def _one(path):
    (par,) = h.body_paragraphs(path)
    return h.run_texts(par)


def test_minimal_span_inside_one_run(cwd):
    """§19.6: the changed span (`brown`→`red`) lies inside the bold run, so only that run changes; the plain
    runs keep their text."""
    d = h.make_docx(cwd / "a.docx", [h.p("The ", h.r("quick brown", "<w:b/>"), " fox jumps")])
    res = h.apply_edits(edits=[{"find": "quick brown fox", "replace": "quick red fox"}], path=str(d), write=True)
    assert res["ok"] is True, res
    assert [(t, b) for t, _, b, _ in _one(d)] == [("The ", False), ("quick red", True), (" fox jumps", False)]


def test_span_across_runs_goes_to_first_run(cwd):
    """§19.6 reviewers' repro: plain `Alpha` + italic `\\t beta`, `Alpha\\t beta`→`Gamma`: the changed span
    crosses runs, so all of `Gamma` goes into the first run and the emptied italic run is removed."""
    d = h.make_docx(cwd / "a.docx", [h.p("Alpha", h.r("\t beta", "<w:i/>"))])
    res = h.apply_edits(edits=[{"find": "Alpha\t beta", "replace": "Gamma"}], path=str(d), write=True)
    assert res["ok"] is True, res
    assert _one(d) == [("Gamma", False, False, False)]
    assert "<w:i/>" not in h.document_xml(d) and "w:tab" not in h.document_xml(d)


def test_hyperlink_run_edited_in_place(cwd):
    """§19.6: text inside a w:hyperlink run is edited there; the hyperlink stays."""
    link = '<w:hyperlink r:id="rId9">' + h.r("the setup guide") + "</w:hyperlink>"
    d = h.make_docx(cwd / "a.docx", [h.p("Read ", link, " first.")])
    res = h.apply_edits(edits=[{"find": "Read the setup guide", "replace": "Read the install guide"}],
                        path=str(d), write=True)
    assert res["ok"] is True, res
    assert _one(d) == [("Read ", False, False, False), ("the install guide", False, False, True),
                       (" first.", False, False, False)]
    assert 'r:id="rId9"' in h.document_xml(d)


def test_emptied_runs_removed(cwd):
    """§19.6: a run left with no text is removed."""
    d = h.make_docx(cwd / "a.docx", [h.p("Keep this ", h.r("(draft) ", "<w:i/>"), "sentence.")])
    res = h.apply_edits(edits=[{"find": "this (draft) sentence", "replace": "this sentence"}], path=str(d),
                        write=True)
    assert res["ok"] is True, res
    assert h.texts(d) == ["Keep this sentence."]
    assert all(t for t, *_ in _one(d))
    assert "<w:i/>" not in h.document_xml(d)


def test_tracked_deletion_is_not_text(cwd):
    """§19.6: text in w:del is not text: a find in it occurs 0 times; edits around it leave it alone."""
    deleted = '<w:del w:id="1" w:author="R"><w:r><w:t>obsolete words </w:t></w:r></w:del>'
    d = h.make_docx(cwd / "a.docx", [h.p("Kept ", deleted, "text here")])
    miss = h.apply_edits(edits=[{"find": "obsolete words", "replace": "x"}], path=str(d))
    assert [f["found"] for f in miss["failures"]] == [0]
    hit = h.apply_edits(edits=[{"find": "Kept text here", "replace": "Kept text there"}], path=str(d), write=True)
    assert hit["ok"] is True, hit
    assert h.texts(d) == ["Kept text there"]
    assert "obsolete words " in h.document_xml(d)


@pytest.mark.skipif(os.name != "nt", reason="Windows file attributes")
def test_hidden_attribute_preserved(cwd):
    """§19.6: the Hidden attribute survives the atomic replace on Windows."""
    d = h.make_docx(cwd / "a.docx", ["Status is draft for now"])
    h.set_attrs(d, h.HIDDEN)
    try:
        res = h.apply_edits(edits=[{"find": "draft", "replace": "final"}], path=str(d), write=True)
        assert res["ok"] is True, res
        assert h.get_attrs(d) & h.HIDDEN
        assert h.texts(d) == ["Status is final for now"]
    finally:
        h.clear_attrs(d)


def test_keyboard_interrupt_during_replace_restores(cwd, monkeypatch):
    """§19.6/§17.1: a KeyboardInterrupt on the 2nd replace still restores the 1st target; no temp file stays."""
    a = h.make_docx(cwd / "a.docx", ["Alpha paragraph text"])
    b = h.write(cwd / "b.md", "beta text\n")
    before = (a.read_bytes(), b.read_bytes())
    real = os.replace
    calls = []

    def flaky(src, dst, *args, **kw):
        calls.append(dst)
        if len(calls) == 2:
            raise KeyboardInterrupt
        return real(src, dst, *args, **kw)

    monkeypatch.setattr(os, "replace", flaky)
    edits = [{"path": str(a), "edits": [{"find": "Alpha", "replace": "ALPHA"}]},
             {"path": str(b), "edits": [{"find": "beta", "replace": "BETA"}]}]
    with pytest.raises((KeyboardInterrupt, h.tool_error())):
        h.apply_edits(edits=edits, write=True)
    monkeypatch.setattr(os, "replace", real)
    assert (a.read_bytes(), b.read_bytes()) == before
    assert h.listing(cwd) == ["a.docx", "b.md"]
