"""text_apply_edits: anchored find and replace in text and .docx files (MANIFEST §15.5, §15.10, §0.4).

The docx fixture is a hand-written package (as in tests/test_render_office.py) with a paragraph split across
several runs, plus styles, docProps and a binary media part that must survive byte for byte.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_r3rc as r3  # noqa: E402

TEXT = ("# Capability Capsule\n"
        "\n"
        "The capsule library holds 79 hand-written capsules.\n"
        "A capsule is admitted by the gate. The gate runs tests.\n"
        "Capsule report §2.3, App. A.1\n")


@pytest.fixture
def doc(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return r3.write(tmp_path / "script.md", TEXT)


def diff_lines(res, sign):
    return [ln[1:] for ln in res["diff"].splitlines() if ln.startswith(sign) and not ln.startswith(sign * 3)]


# ------------------------------------------------------------------ text files

def test_dry_run_reports_diff_and_changes_nothing(doc):
    """§15.5: without write, the edit is checked and diffed but the file is untouched."""
    before = doc.read_bytes()
    res = r3.apply_edits(edits=[{"find": "79 hand-written", "replace": "80 registered"}], path="script.md")
    assert res["ok"] is True
    assert res["applied"] == 1                       # pinned: a count
    assert res["failures"] == []
    assert "The capsule library holds 79 hand-written capsules." in diff_lines(res, "-")
    assert "The capsule library holds 80 registered capsules." in diff_lines(res, "+")
    assert doc.read_bytes() == before


def test_write_applies_edit(doc):
    """§15.5: with write the file is rewritten."""
    res = r3.apply_edits(edits=[{"find": "§2.3, App. A.1", "replace": "§2.4, App. A.2"}],
                         path="script.md", write=True)
    assert res["ok"] is True
    assert r3.read(doc) == TEXT.replace("§2.3, App. A.1", "§2.4, App. A.2")


def test_default_count_is_one_and_must_be_exact(doc):
    """§15.5: `gate` occurs twice, so a count-1 edit fails with found=2 and nothing is written."""
    before = doc.read_bytes()
    res = r3.apply_edits(edits=[{"find": "gate", "replace": "admission gate"}], path="script.md", write=True)
    assert res["ok"] is False
    assert [(f["find"], f["found"]) for f in res["failures"]] == [("gate", 2)]
    assert doc.read_bytes() == before


def test_count_two_replaces_both(doc):
    """§15.5: count=2 matches exactly 2 occurrences and replaces both."""
    res = r3.apply_edits(edits=[{"find": "gate", "replace": "admission gate", "count": 2}],
                         path="script.md", write=True)
    assert res["ok"] is True
    assert r3.read(doc).count("admission gate") == 2


def test_count_higher_than_occurrences_fails(doc):
    """§15.5: count=3 with 2 occurrences fails and reports found=2."""
    res = r3.apply_edits(edits=[{"find": "gate", "replace": "x", "count": 3}], path="script.md")
    assert res["ok"] is False
    assert res["failures"][0]["found"] == 2


def test_edits_apply_in_order(doc):
    """§15.5: each edit sees the result of the previous one."""
    edits = [{"find": "79 hand-written", "replace": "80 registered"},
             {"find": "80 registered capsules", "replace": "80 registered capsules and 5 inert ones"}]
    res = r3.apply_edits(edits=edits, path="script.md", write=True)
    assert res["ok"] is True
    assert res["applied"] == 2
    assert "holds 80 registered capsules and 5 inert ones." in r3.read(doc)


def test_all_or_nothing_and_later_edits_still_evaluated(doc):
    """§15.5: a failing edit blocks the write; later edits are evaluated against the text after the
    successful ones, so only the missing anchor is a failure."""
    before = doc.read_bytes()
    edits = [{"find": "79 hand-written", "replace": "80 registered"},
             {"find": "not in the file", "replace": "x"},
             {"find": "80 registered", "replace": "81 registered"}]
    res = r3.apply_edits(edits=edits, path="script.md", write=True)
    assert res["ok"] is False
    # pinned: index is 0-based
    assert [(f["index"], f["find"], f["found"]) for f in res["failures"]] == [(1, "not in the file", 0)]
    assert doc.read_bytes() == before


def test_every_failure_listed(doc):
    """§15.5: an edit that needs a failed edit's output fails too; both are listed with 0-based indexes."""
    edits = [{"find": "zzz", "replace": "yyy"}, {"find": "yyy", "replace": "x"}]
    res = r3.apply_edits(edits=edits, path="script.md")
    assert [(f["find"], f["found"]) for f in res["failures"]] == [("zzz", 0), ("yyy", 0)]
    assert [f["index"] for f in res["failures"]] == [0, 1]


def test_write_preserves_crlf(tmp_path, monkeypatch):
    """Pinned details: line endings of text files are preserved (CRLF stays CRLF, including the edited line)."""
    monkeypatch.chdir(tmp_path)
    p = r3.write(tmp_path / "crlf.md", TEXT.replace("\n", "\r\n"))
    res = r3.apply_edits(edits=[{"find": "admitted by the gate.", "replace": "admitted by the gate only."}],
                         path="crlf.md", write=True)
    assert res["ok"] is True
    data = p.read_bytes()
    assert r3.crlf_only(data)
    assert data.decode("utf-8") == TEXT.replace("gate.", "gate only.", 1).replace("\n", "\r\n")


def test_missing_file_is_tool_error(tmp_path, monkeypatch):
    """§0.2: a missing file raises ToolError."""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(r3.tool_error()):
        r3.apply_edits(edits=[{"find": "a", "replace": "b"}], path="nope.md")


# ------------------------------------------------------------------ docx

@pytest.fixture
def docx(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return r3.make_docx(tmp_path / "report.docx", [
        ("Heading1", ["Capability Capsule"]),
        (None, ["Alita-G builds ", "its own", " tool library once."]),
        (None, ["Beyond Task Completion checks ", "kept tools."]),
    ], extra_parts=r3.EXTRA_PARTS)


def test_docx_multi_run_edit(docx):
    """§15.5: a find spanning 3 runs is applied; the replacement lands in the first affected run and the
    affected text leaves the others; every other package part is byte-identical."""
    before = r3.docx_parts(docx)
    res = r3.apply_edits(edits=[{"find": "builds its own tool", "replace": "grows a"}],
                         path="report.docx", write=True)
    assert res["ok"] is True
    paras = r3.docx_paragraphs(docx)
    assert paras == ["Capability Capsule", "Alita-G grows a library once.",
                     "Beyond Task Completion checks kept tools."]
    runs = r3.docx_runs(docx)[1]
    assert runs[0] == "Alita-G grows a"
    assert "".join(runs[1:]) == " library once."
    after = r3.docx_parts(docx)
    assert set(after) == set(before)
    for name in before:
        if name != "word/document.xml":
            assert after[name] == before[name], name


def test_docx_dry_run_diff_by_paragraph(docx):
    """§15.5: a docx dry run leaves the file unchanged; the diff has paragraphs as lines."""
    before = docx.read_bytes()
    res = r3.apply_edits(edits=[{"find": "kept tools", "replace": "every kept tool"}], path="report.docx")
    assert res["ok"] is True
    assert "Beyond Task Completion checks kept tools." in diff_lines(res, "-")
    assert "Beyond Task Completion checks every kept tool." in diff_lines(res, "+")
    assert docx.read_bytes() == before


def test_docx_find_across_paragraphs_fails(docx):
    """§15.5: `find` must lie within 1 paragraph."""
    before = docx.read_bytes()
    res = r3.apply_edits(edits=[{"find": "once.Beyond", "replace": "x"}], path="report.docx", write=True)
    assert res["ok"] is False
    assert res["failures"][0]["found"] == 0
    assert docx.read_bytes() == before


# ------------------------------------------------------------------ CLI and registration

def test_cli_edits_file_and_write(doc, tmp_path, capsys):
    """§15.5/§0.4: `tundlekit text apply-edits EDITS.json FILE --write --json`; failures exit 1."""
    r3.write(tmp_path / "edits.json", json.dumps([{"find": "79", "replace": "80"}]))
    code, data, _, _ = r3.run_cli(capsys, ["text", "apply-edits", "edits.json", "script.md", "--write", "--json"])
    assert code == 0 and data["ok"] is True
    assert "holds 80 hand-written" in r3.read(doc)
    code, data, _, _ = r3.run_cli(capsys, ["text", "apply-edits", "edits.json", "script.md", "--json"])
    assert code == 1
    assert data["ok"] is False and data["failures"][0]["found"] == 0


def test_registration_text_apply_edits():
    """§15.10: text_apply_edits lives in textlint, is not read-only, and has a strict schema."""
    t = r3.get_tool("textlint", "text_apply_edits")
    assert t.annotations.get("readOnlyHint") is not True
    assert t.input_schema.get("additionalProperties") is False
    assert {"edits", "path", "write"} <= set(t.input_schema["properties"])
    assert t.func.__module__ == "tundlekit.textlint"
