"""Round 5: docx edits and emitted edits (MANIFEST §17.1, on top of §15.4, §15.5, §16.3, §0.2, §0.4)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_r5 as h  # noqa: E402


@pytest.fixture
def cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


# ------------------------------------------------------------------------------------ run-level tabs
def test_tab_stop_definition_is_not_text(cwd):
    """§17.1: `w:tabs/w:tab` in `w:pPr` never reads as text; only the run-level tab is `\\t`."""
    h.make_docx(cwd / "old.docx", ["Intro.", h.tabstop_para(["Name", "\t", "Value"])])
    h.make_docx(cwd / "new.docx", ["Intro.", h.tabstop_para(["Name", "\t", "Amount"])])
    (c,) = h.docx_diff("old.docx", "new.docx")["changes"]
    assert c["old"] == ["Name\tValue"]
    assert c["new"] == ["Name\tAmount"]


def test_leading_tab_find_does_not_match_tab_stop(cwd):
    """§17.1: the tab stop is not text, so `\\tName` occurs 0 times."""
    d = h.make_docx(cwd / "a.docx", [h.tabstop_para(["Name", "\t", "Value"])])
    res = h.apply_edits(edits=[{"find": "\tName", "replace": "\tKey"}], path=str(d))
    assert res["ok"] is False
    assert [(f["index"], f["found"]) for f in res["failures"]] == [(0, 0)]


def test_edit_never_writes_into_ppr(cwd):
    """§17.1: an edit at the paragraph start leaves `w:pPr` schema-shaped (no w:t inside w:tabs)."""
    d = h.make_docx(cwd / "a.docx", ["Intro.", h.tabstop_para(["Name", "\t", "Value"])])
    before = h.document_xml(d)
    tabs = before[before.index("<w:pPr>"):before.index("</w:pPr>")]
    res = h.apply_edits(edits=[{"find": "Name\tValue", "replace": "Key\tNew value"}], path=str(d), write=True)
    assert res["ok"] is True, res
    h.assert_ppr_schema_shaped(d)
    assert h.paragraphs(d) == ["Intro.", "Key\tNew value"]
    assert tabs in h.document_xml(d)


# ------------------------------------------------------------------------------------ page breaks
def test_page_break_reads_as_form_feed(cwd):
    """§17.1: `<w:br w:type="page"/>` is `\\f`, a plain `<w:br/>` stays `\\n` (§16.3)."""
    h.make_docx(cwd / "old.docx", [h.para(["End of part one", "\f", "Part two", "\n", "second line"])])
    h.make_docx(cwd / "new.docx", [h.para(["End of part one", "\f", "Part two", "\n", "last line"])])
    (c,) = h.docx_diff("old.docx", "new.docx")["changes"]
    assert c["old"] == ["End of part one\fPart two\nsecond line"]


def test_newline_find_never_touches_page_break(cwd):
    """§17.1: a `\\n` find does not match a page break; a `\\f` find does."""
    d = h.make_docx(cwd / "a.docx", [h.para(["End of part one", "\f", "Part two"])])
    miss = h.apply_edits(edits=[{"find": "one\nPart", "replace": "one Part"}], path=str(d))
    assert [f["found"] for f in miss["failures"]] == [0]
    hit = h.apply_edits(edits=[{"find": "one\fPart", "replace": "one\fChapter"}], path=str(d))
    assert hit["ok"] is True, hit


# ------------------------------------------------------------------------------------ emitted edits
def test_short_and_partial_hints_not_emitted(cwd):
    """§17.1 reviewers' repro: `# Method`→`Methods` hints inside "Methodology overview" and cell `12`→`13`
    inside `YEAR = 2012`; neither is a whole paragraph or ≥ 12 characters with a letter: nothing is emitted,
    and both are listed in `not_emitted`."""
    h.write(cwd / "src" / "build.py", 'TITLE = "Methodology overview"\nYEAR = 2012\n')
    h.write(cwd / "old.md", "# Method\n\n| Year | Count |\n|---|---|\n| 2024 | 12 |\n")
    h.make_docx(cwd / "new.docx", ["Methods", "Year", "Count", "2024", "13"])
    res = h.docx_diff("old.md", "new.docx", search=["src"], emit_edits="edits.json")
    assert [(c["op"], c["old_index"]) for c in res["changes"]] == [("replace", 0), ("replace", 4)]
    assert res["edits_written"] == 0
    assert h.emitted(cwd / "edits.json") == []
    ne = res["not_emitted"]
    assert sorted(x["old_index"] for x in ne) == [0, 4]
    assert all(isinstance(x["reason"], str) and x["reason"] for x in ne)


def test_whole_paragraph_markdown_hint_emitted_with_absolute_path(cwd):
    """§17.1: a Markdown paragraph between blank lines is a whole-paragraph hint; the path is absolute."""
    old = "Kept tools fail held-out tests in most runs."
    new = "Kept tools fail held-out tests in 9 of 10 runs."
    h.write(cwd / "src" / "notes.md", f"# Notes\n\n{old}\n\nAnother paragraph.\n")
    h.make_docx(cwd / "old.docx", ["Notes", old])
    h.make_docx(cwd / "new.docx", ["Notes", new])
    res = h.docx_diff("old.docx", "new.docx", search=["src"], emit_edits="edits.json")
    assert res["edits_written"] == 1
    assert res["not_emitted"] == []
    (obj,) = h.read_json(cwd / "edits.json")
    assert os.path.isabs(obj["path"])
    assert h.same_file(obj["path"], cwd / "src" / "notes.md")
    assert obj["edits"] == [{"find": old, "replace": new, "count": 1}]


def test_markdown_hint_inside_longer_paragraph_not_emitted(cwd):
    """§17.1: the old text is only part of a Markdown paragraph (no blank line after it)."""
    old = "Kept tools fail held-out tests in most runs."
    h.write(cwd / "src" / "notes.md", f"# Notes\n\n{old}\nThe gate caught all of them.\n")
    h.make_docx(cwd / "old.docx", ["Notes", old])
    h.make_docx(cwd / "new.docx", ["Notes", "Kept tools fail held-out tests in 9 of 10 runs."])
    res = h.docx_diff("old.docx", "new.docx", search=["src"], emit_edits="edits.json")
    assert res["edits_written"] == 0
    assert [x["old_index"] for x in res["not_emitted"]] == [1]


def test_empty_edit_list_is_ok(cwd):
    """§17.1: `text_apply_edits` accepts `[]` (the emitted file when nothing was emitted)."""
    h.write(cwd / "a.md", "alpha\n")
    res = h.apply_edits(edits=[], write=True)
    assert res["ok"] is True
    assert res["failures"] == []
    assert h.listing(cwd) == ["a.md"]


def test_empty_edit_file_cli(cwd, capsys):
    """§17.1/§0.4: `text apply-edits EMPTY.json --write --json` exits 0."""
    h.write(cwd / "e.json", "[]\n")
    code, data, _, err = h.run_cli(capsys, ["text", "apply-edits", "e.json", "--write", "--json"])
    assert code == 0, err
    assert data["ok"] is True


# ------------------------------------------------------------------------------------ writes
@pytest.mark.skipif(os.name != "nt", reason="an open handle blocks replacement only on Windows")
def test_all_or_nothing_restores_first_file_when_second_is_locked(cwd):
    """§17.1: the second replace fails (the target is held open); the first target is restored and named."""
    a = h.write(cwd / "a.md", "alpha text\n")
    b = h.write(cwd / "b.md", "beta text\n")
    edits = [{"path": str(a), "edits": [{"find": "alpha", "replace": "ALPHA"}]},
             {"path": str(b), "edits": [{"find": "beta", "replace": "BETA"}]}]
    with open(b, "rb"):
        with pytest.raises(h.tool_error()) as exc:
            h.apply_edits(edits=edits, write=True)
    assert "a.md" in str(exc.value)
    assert h.read(a) == "alpha text\n"
    assert h.read(b) == "beta text\n"
    assert h.listing(cwd) == ["a.md", "b.md"]


def test_read_only_target_refused_without_temp_files(cwd):
    """§17.1: a read-only target is a ToolError ("read-only") and no temp file is left."""
    p = h.write(cwd / "notes" / "a.md", "alpha text\n")
    h.make_read_only(p)
    try:
        with pytest.raises(h.tool_error()) as exc:
            h.apply_edits(edits=[{"find": "alpha", "replace": "ALPHA"}], path=str(p), write=True)
        assert "read-only" in str(exc.value)
        assert h.read(p) == "alpha text\n"
        assert h.listing(cwd) == ["notes/a.md"]
    finally:
        h.make_writable(p)


def test_read_only_second_target_refused_before_any_write(cwd):
    """§17.1: in the list form, a read-only second target is refused before the first file is touched."""
    a = h.write(cwd / "a.md", "alpha text\n")
    b = h.write(cwd / "b.md", "beta text\n")
    h.make_read_only(b)
    try:
        with pytest.raises(h.tool_error()) as exc:
            h.apply_edits(edits=[{"path": "a.md", "edits": [{"find": "alpha", "replace": "ALPHA"}]},
                                 {"path": "b.md", "edits": [{"find": "beta", "replace": "BETA"}]}], write=True)
        assert "read-only" in str(exc.value)
        assert h.read(a) == "alpha text\n"
        assert h.listing(cwd) == ["a.md", "b.md"]
    finally:
        h.make_writable(b)


# ------------------------------------------------------------------------------------ office guard
@pytest.fixture
def office_open(monkeypatch):
    import tundlekit.render as render

    monkeypatch.setattr(render, "office_running", lambda *a, **k: ["WINWORD.EXE"])
    return render


def test_office_guard_refuses_docx_write(cwd, office_open):
    """§17.1: `write` on a .docx is refused while Office runs; the dry run is allowed."""
    d = h.make_docx(cwd / "a.docx", ["Kept tools fail held-out tests."])
    before = d.read_bytes()
    edit = [{"find": "Kept", "replace": "Most"}]
    assert h.apply_edits(edits=edit, path=str(d))["ok"] is True
    with pytest.raises(h.tool_error()):
        h.apply_edits(edits=edit, path=str(d), write=True)
    assert d.read_bytes() == before


def test_office_guard_force_and_text_files(cwd, office_open):
    """§17.1: `force_office` overrides; text files are never guarded."""
    d = h.make_docx(cwd / "a.docx", ["Kept tools fail held-out tests."])
    m = h.write(cwd / "a.md", "Kept tools\n")
    edit = [{"find": "Kept", "replace": "Most"}]
    assert h.apply_edits(edits=edit, path=str(d), write=True, force_office=True)["ok"] is True
    assert h.paragraphs(d) == ["Most tools fail held-out tests."]
    assert h.apply_edits(edits=edit, path=str(m), write=True)["ok"] is True


def test_office_guard_cli_flag(cwd, office_open, capsys):
    """§17.1/§0.4: CLI exit 1 without `--force-office`, 0 with it."""
    d = h.make_docx(cwd / "a.docx", ["Kept tools fail held-out tests."])
    h.write(cwd / "e.json", h.dump([{"find": "Kept", "replace": "Most"}]))
    code, data, _, _ = h.run_cli(capsys, ["text", "apply-edits", "e.json", d.name, "--write", "--json"])
    assert code == 1 and "error" in data
    code, data, _, err = h.run_cli(capsys, ["text", "apply-edits", "e.json", d.name, "--write",
                                            "--force-office", "--json"])
    assert code == 0, err
    assert h.paragraphs(d) == ["Most tools fail held-out tests."]
