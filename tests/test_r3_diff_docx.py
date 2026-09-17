"""MANIFEST §15.4 `docx_diff` / `tundlekit text docx-diff` (docx vs docx, docx vs Markdown), §15.10 registration.

The .docx files are minimal zips written by hand (word/document.xml only, as §8.3's text backend reads).
"""
from __future__ import annotations

import pytest

import helpers_r3 as r3

REPORT = [
    "AI4Research Capability Capsule Report",
    "1. Summary",
    "Kept tools fail held-out tests in most runs.",
    "The Execution Broker leases each capability for one run.",
    "2. Recommendations",
    "Gate every tool before it enters the library.",
]


def diff(old, new, **kw):
    res = r3.call("docx_diff", old=str(old), new=str(new), **kw)
    assert isinstance(res["changes"], list)
    for c in res["changes"]:
        assert set(c) >= {"op", "old", "new", "old_index", "new_index", "hint"}
        assert c["op"] in ("replace", "insert", "delete")
        assert isinstance(c["old"], list) and isinstance(c["new"], list)
        assert isinstance(c["hint"], list)
    return res


def test_registered_in_textlint_read_only():
    """§15.10: docx_diff is registered by tundlekit.textlint; §19.1: it writes emit_edits, so not read-only."""
    t = r3.get_tool("docx_diff")
    assert t.annotations.get("readOnlyHint") is False
    assert t.input_schema.get("additionalProperties") is False
    assert {"old", "new", "search"} <= set(t.input_schema["properties"])


def test_identical_docx(tmp_path):
    """§15.4: identical content gives []."""
    a = r3.make_docx(tmp_path / "a.docx", REPORT)
    b = r3.make_docx(tmp_path / "b.docx", REPORT)
    assert diff(a, b)["changes"] == []


def test_replaced_paragraph(tmp_path):
    """§15.4: a changed paragraph is 1 `replace` with old and new paragraph lists."""
    a = r3.make_docx(tmp_path / "a.docx", REPORT)
    edited = list(REPORT)
    edited[3] = "The Execution Broker leases each capability for a single run."
    b = r3.make_docx(tmp_path / "b.docx", edited)
    (c,) = diff(a, b)["changes"]
    assert c["op"] == "replace"
    assert c["old"] == [REPORT[3]]
    assert c["new"] == [edited[3]]
    assert (c["old_index"], c["new_index"]) == (3, 3)      # pinned: 0-based


def test_inserted_paragraph(tmp_path):
    """§15.4: an added paragraph is an `insert` with old []."""
    a = r3.make_docx(tmp_path / "a.docx", REPORT)
    b = r3.make_docx(tmp_path / "b.docx", REPORT[:3] + ["A new paragraph about gates."] + REPORT[3:])
    (c,) = diff(a, b)["changes"]
    assert c["op"] == "insert"
    assert c["old"] == []
    assert c["new"] == ["A new paragraph about gates."]
    assert (c["old_index"], c["new_index"]) == (3, 3)


def test_deleted_paragraph(tmp_path):
    """§15.4: a removed paragraph is a `delete` with new []."""
    a = r3.make_docx(tmp_path / "a.docx", REPORT)
    b = r3.make_docx(tmp_path / "b.docx", REPORT[:5])
    (c,) = diff(a, b)["changes"]
    assert c["op"] == "delete"
    assert c["old"] == [REPORT[5]]
    assert c["new"] == []
    assert (c["old_index"], c["new_index"]) == (5, 5)


def test_empty_paragraphs_skipped(tmp_path):
    """§15.4: empty paragraphs are skipped."""
    a = r3.make_docx(tmp_path / "a.docx", REPORT)
    b = r3.make_docx(tmp_path / "b.docx", [REPORT[0], "", [], REPORT[1], REPORT[2], "", *REPORT[3:], ""])
    assert diff(a, b)["changes"] == []


def test_whitespace_and_curly_quotes_normalised(tmp_path):
    """§15.4: whitespace is collapsed and curly quotes are folded before alignment."""
    a = r3.make_docx(tmp_path / "a.docx", ['The "freeze" step comes first.', "Two  spaces   here."])
    b = r3.make_docx(tmp_path / "b.docx", ["The “freeze” step comes first.", "Two spaces here."])
    assert diff(a, b)["changes"] == []


def test_changes_carry_raw_paragraph_text(tmp_path):
    """§15.4 (pinned): old/new hold the raw paragraph text, not the normalised form used for alignment."""
    old_p = "The “freeze”  step comes first."
    new_p = "The “freeze” step comes   last."
    a = r3.make_docx(tmp_path / "a.docx", ["Intro.", old_p])
    b = r3.make_docx(tmp_path / "b.docx", ["Intro.", new_p])
    (c,) = diff(a, b)["changes"]
    assert (c["op"], c["old"], c["new"]) == ("replace", [old_p], [new_p])
    assert (c["old_index"], c["new_index"]) == (1, 1)


MD ="""# AI4Research Capability Capsule Report

## 1. Summary

Kept tools fail **held-out** tests
in most runs.

The `Execution Broker` leases each capability for *one* run.

- first bullet
- second bullet
"""

MD_PARAS = [
    "AI4Research Capability Capsule Report",
    "1. Summary",
    "Kept tools fail held-out tests in most runs.",
    "The Execution Broker leases each capability for one run.",
    "first bullet",
    "second bullet",
]


def test_docx_against_markdown_equal(tmp_path):
    """§15.4: Markdown is reduced to paragraphs (blocks joined, headings/emphasis/code marks stripped,
    list items separate), so matching content gives []."""
    d = r3.make_docx(tmp_path / "report.docx", MD_PARAS)
    m = r3.write(tmp_path / "report.md", MD)
    assert diff(d, m)["changes"] == []


def test_markdown_against_docx_either_order(tmp_path):
    """§15.4: a .md may be old and the .docx new; a changed bullet is a replace."""
    edited = list(MD_PARAS)
    edited[5] = "second bullet, reworded"
    d = r3.make_docx(tmp_path / "edited.docx", edited)
    m = r3.write(tmp_path / "report.md", MD)
    (c,) = diff(m, d)["changes"]
    assert c["op"] == "replace"
    assert c["old"] == ["second bullet"]
    assert c["new"] == ["second bullet, reworded"]


def test_hint_for_first_old_paragraph(tmp_path, monkeypatch):
    """§15.4: hint is as for deck_diff, for the first old paragraph; a relative search gives relative hint paths."""
    monkeypatch.chdir(tmp_path)
    src = tmp_path / "src"
    script = r3.write(src / "build_report.py",
                      "from docx import Document\n\n"
                      "doc = Document()\n"
                      f"doc.add_paragraph({REPORT[5]!r})\n")
    a = r3.make_docx(tmp_path / "a.docx", REPORT)
    b = r3.make_docx(tmp_path / "b.docx", REPORT[:5] + ["Gate every tool, then admit it."])
    (c,) = diff(a, b, search=["src"])["changes"]
    assert [r3.slash(h) for h in c["hint"]] == ["src/build_report.py:4"]
    assert r3.hint_matches(c["hint"][0], script, 4)


def test_cli_text_docx_diff(tmp_path, capsys):
    """§15.10: `tundlekit text docx-diff OLD NEW --json`."""
    a = r3.make_docx(tmp_path / "a.docx", REPORT)
    b = r3.make_docx(tmp_path / "b.docx", REPORT[:4])
    code, data, out, err = r3.run_cli(capsys, ["text", "docx-diff", a, b, "--json"])
    assert code == 0, err
    assert [c["op"] for c in data["changes"]] == ["delete"]
    assert data["changes"][0]["old"] == REPORT[4:6]
