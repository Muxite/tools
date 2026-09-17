"""MANIFEST §16.3 docx_diff Markdown reduction, `emit_edits`, the list form of text_apply_edits, failure detail
(`lines`, `.py` string-literal-split hint) and docx paragraph text (<w:tab/>, <w:br/>, mc:Fallback).

.docx files are minimal zips written by hand (helpers_r4d.make_docx).
"""
from __future__ import annotations

import re

import pytest

import helpers_r4d as r4


def md_vs_docx(tmp_path, md, paras):
    m = r4.write(tmp_path / "report.md", md)
    d = r4.make_docx(tmp_path / "report.docx", paras)
    return r4.docx_diff(m, d)["changes"]


# ------------------------------------------------------------------------------------ Markdown reduction
def test_image_alt_text_with_brackets(tmp_path):
    """§16.3: image markup is stripped even when the alt text holds brackets; the alt text is kept."""
    md = "Before the figure.\n\n![Pipeline overview [2, Fig. 1]](fig/pipeline.png)\n\nAfter it.\n"
    assert md_vs_docx(tmp_path, md, ["Before the figure.", "Pipeline overview [2, Fig. 1]", "After it."]) == []


def test_list_numbers_kept_when_docx_has_them(tmp_path):
    """§16.3: a leading `N.` stays on both sides when the docx paragraph starts with it."""
    md = "Steps:\n\n1. Freeze the goal\n2. Run the gates\n3. Retire what fails\n"
    paras = ["Steps:", "1.  Freeze the goal", "2.  Run the gates", "3.  Retire what fails"]
    assert md_vs_docx(tmp_path, md, paras) == []


def test_list_numbers_dropped_when_docx_lacks_them(tmp_path):
    """§16.3: otherwise the number is removed on both sides."""
    md = "Steps:\n\n1. Freeze the goal\n2. Run the gates\n"
    assert md_vs_docx(tmp_path, md, ["Steps:", "Freeze the goal", "Run the gates"]) == []


def test_pagebreak_and_placeholder_lines_dropped(tmp_path):
    """§16.3: lines that are only `\\pagebreak` or a `{{...}}` placeholder are dropped."""
    md = ("Kept tools fail held-out tests.\n\n\\pagebreak\n\n{{excerpt:gates-table}}\n\n"
          "Gate every tool.\n\n\\newpage\n")
    assert md_vs_docx(tmp_path, md, ["Kept tools fail held-out tests.", "Gate every tool."]) == []


def test_fenced_code_is_one_paragraph_matching_line_breaks(tmp_path):
    """§16.3: a fenced block is 1 paragraph (lines joined with \\n), like a docx paragraph with <w:br/>."""
    md = "Run this:\n\n```\ntundle.sh status\ntundle.sh release\n```\n"
    paras = ["Run this:", ["tundle.sh status", "\n", "tundle.sh release"]]
    assert md_vs_docx(tmp_path, md, paras) == []


def test_fenced_code_change_is_one_replace(tmp_path):
    """§16.3: an edited code block is 1 replace whose old/new are the whole block, joined with \\n."""
    md = "Run this:\n\n```\ntundle.sh status\ntundle.sh release\n```\n"
    paras = ["Run this:", ["tundle.sh status", "\n", "tundle.sh release --dry-run"]]
    (c,) = md_vs_docx(tmp_path, md, paras)
    assert c["op"] == "replace"
    assert c["old"] == ["tundle.sh status\ntundle.sh release"]
    assert c["new"] == ["tundle.sh status\ntundle.sh release --dry-run"]


REPORT_MD = """# Capability Capsule Report

## 1. Summary

Kept tools fail **held-out** tests
in most runs [3, p. 4].

![Gate flow [2, Fig. 1]](fig/gates.png)

{{excerpt:gate-table}}

1. Freeze the goal
2. Run the gates

\\pagebreak

```
tundle.sh status
```

| Gate | Kept |
|---|---|
| unit | 222 |
"""

REPORT_DOCX = ["Capability Capsule Report", "1. Summary",
               "Kept tools fail held-out tests in most runs [3, p. 4].", "Gate flow [2, Fig. 1]",
               "1. Freeze the goal", "2. Run the gates", "tundle.sh status", "Gate", "Kept", "unit", "222"]


def test_in_sync_report_has_no_changes(tmp_path):
    """§16.3: an in-sync pair gives changes: [] (both orders)."""
    m = r4.write(tmp_path / "report.md", REPORT_MD)
    d = r4.make_docx(tmp_path / "report.docx", REPORT_DOCX)
    assert r4.docx_diff(m, d)["changes"] == []
    assert r4.docx_diff(d, m)["changes"] == []


def test_text_box_counted_once(tmp_path):
    """§16.3: text in mc:Fallback is ignored, so a text box's text appears once."""
    a = r4.make_docx(tmp_path / "a.docx", ["Intro.", r4.textbox_para("Box text")])
    b = r4.make_docx(tmp_path / "b.docx", ["Intro.", r4.textbox_para("Box words")])
    (c,) = r4.docx_diff(a, b)["changes"]
    assert sum(p.count("Box text") for p in c["old"]) == 1
    assert sum(p.count("Box words") for p in c["new"]) == 1


# ------------------------------------------------------------------------------------ emit_edits
OLD = ["Capsule report", "Kept tools fail held-out tests in most runs.", "Middle paragraph stays.",
       "Gate every tool before it enters the library.", "An unhinted closing line."]
NEW = ["Capsule report", "Kept tools fail held-out tests in 9 of 10 runs.", "Middle paragraph stays.",
       "Gate every tool before the library admits it.", "A reworded closing line."]


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    r4.write(tmp_path / "src" / "intro.py", f"# build\n\nINTRO = {OLD[1]!r}\n")
    r4.write(tmp_path / "src" / "close.md", f"# Close\n\n{OLD[3]}\n")
    r4.make_docx(tmp_path / "old.docx", OLD)
    r4.make_docx(tmp_path / "new.docx", NEW)
    return tmp_path


def test_emit_edits_one_object_per_file(project):
    """§16.3: replace changes with exactly 1 hint are written as [{path, edits}], 1 object per file."""
    res = r4.docx_diff("old.docx", "new.docx", search=["src"], emit_edits="edits.json")
    assert res["edits_written"] == 2
    got = r4.emitted_by_file(r4.read_json(project / "edits.json"))
    assert got == {"intro.py": [{"find": OLD[1], "replace": NEW[1], "count": 1}],
                   "close.md": [{"find": OLD[3], "replace": NEW[3], "count": 1}]}


def test_emitted_file_applies_across_files(project):
    """§16.3: text_apply_edits accepts the emitted list; each object edits its own file."""
    r4.docx_diff("old.docx", "new.docx", search=["src"], emit_edits="edits.json")
    res = r4.apply_edits(edits=r4.read_json(project / "edits.json"), write=True)
    assert res["ok"] is True
    assert NEW[1] in (project / "src" / "intro.py").read_text(encoding="utf-8")
    assert NEW[3] in (project / "src" / "close.md").read_text(encoding="utf-8")


def test_ambiguous_hint_not_emitted(project):
    """§16.3: a change whose old text occurs in 2 places is not emitted."""
    r4.write(project / "src" / "copy.md", f"{OLD[3]}\n")
    res = r4.docx_diff("old.docx", "new.docx", search=["src"], emit_edits="edits.json")
    assert res["edits_written"] == 1
    got = r4.emitted_by_file(r4.read_json(project / "edits.json"))
    assert list(got) == ["intro.py"]


def test_cli_emit_edits(project, capsys):
    """§16.3: CLI `--emit-edits PATH`."""
    code, data, out, err = r4.run_cli(capsys, ["text", "docx-diff", "old.docx", "new.docx", "--search", "src",
                                               "--emit-edits", "out.json", "--json"])
    assert code == 0, err
    assert data["edits_written"] == 2
    assert len(r4.read_json(project / "out.json")) == 2


def test_list_form_all_or_nothing(tmp_path, monkeypatch):
    """§16.3: one failing edit in any file means no file is written."""
    monkeypatch.chdir(tmp_path)
    a = r4.write(tmp_path / "a.md", "alpha text\n")
    b = r4.write(tmp_path / "b.py", "BETA = 'beta text'\n")
    edits = [{"path": "a.md", "edits": [{"find": "alpha", "replace": "ALPHA"}]},
             {"path": "b.py", "edits": [{"find": "gamma", "replace": "GAMMA"}]}]
    res = r4.apply_edits(edits=edits, write=True)
    assert res["ok"] is False
    assert a.read_text(encoding="utf-8") == "alpha text\n"
    assert b.read_text(encoding="utf-8") == "BETA = 'beta text'\n"


# ------------------------------------------------------------------------------------ failure detail
def test_failure_lines_for_text_file(tmp_path):
    """§16.3: failures list the line number of each occurrence."""
    p = r4.write(tmp_path / "plan.md", "# Plan\nthe gate runs\nmiddle\nthe gate again\n")
    res = r4.apply_edits(edits=[{"find": "the gate", "replace": "a gate"}, {"find": "absent", "replace": "x"}],
                         path=str(p))
    assert [(f["index"], f["found"], f["lines"]) for f in res["failures"]] == [(0, 2, [2, 4]), (1, 0, [])]


def test_failure_lines_for_docx_are_paragraph_indices(tmp_path):
    """§16.3: for .docx, `lines` holds paragraph indices (0-based, as docx_diff's §15.4 indices)."""
    d = r4.make_docx(tmp_path / "a.docx", ["Intro.", "The gate runs tests.", "Middle.", "Every gate runs tests."])
    (f,) = r4.apply_edits(edits=[{"find": "runs tests", "replace": "tests"}], path=str(d))["failures"]
    assert f["lines"] == [1, 3]


PY = 'SLIDES = [\n    dict(say=("The broker leases each capability "\n              "for one run only.")),\n]\n'


def test_py_string_literal_split_hint(tmp_path):
    """§16.3: a find that only matches across a Python string-literal split gets a hint naming the line."""
    p = r4.write(tmp_path / "build.py", PY)
    (f,) = r4.apply_edits(edits=[{"find": "The broker leases each capability for one run only.",
                                  "replace": "x"}], path=str(p))["failures"]
    assert f["found"] == 0
    m = re.fullmatch(r"spans a string-literal split at line (\d+)", f.get("hint") or "")
    assert m and int(m.group(1)) in (2, 3), f


def test_no_split_hint_outside_py(tmp_path):
    """§16.3: the hint is only for .py files."""
    p = r4.write(tmp_path / "build.md", PY)
    (f,) = r4.apply_edits(edits=[{"find": "The broker leases each capability for one run only.",
                                  "replace": "x"}], path=str(p))["failures"]
    assert f["found"] == 0 and not f.get("hint")
    assert f["lines"] == []


# ------------------------------------------------------------------------------------ docx paragraph text
def test_find_with_tab(tmp_path):
    """§16.3: <w:tab/> is \\t for find matching."""
    d = r4.make_docx(tmp_path / "a.docx", [["Name", "\t", "Value"]])
    res = r4.apply_edits(edits=[{"find": "Name\tValue", "replace": "Name\tNew value"}], path=str(d), write=True)
    assert res["ok"] is True, res
    assert "New value" in r4.document_xml(d)


def test_find_with_line_break(tmp_path):
    """§16.3: <w:br/> is \\n for find matching."""
    d = r4.make_docx(tmp_path / "a.docx", [["first line", "\n", "second line"]])
    res = r4.apply_edits(edits=[{"find": "first line\nsecond", "replace": "first line\nthird"}], path=str(d))
    assert res["ok"] is True, res


def test_text_box_find_counts_once(tmp_path):
    """§16.3: text boxes count once (mc:Fallback ignored)."""
    d = r4.make_docx(tmp_path / "a.docx", ["Intro.", r4.textbox_para("Box text")])
    res = r4.apply_edits(edits=[{"find": "Box text", "replace": "Box words", "count": 1}], path=str(d))
    assert res["ok"] is True, res
