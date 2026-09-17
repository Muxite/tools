"""MANIFEST §18.1 `report_build`: registration (§18.6), order of checks, guards (§18.4, §16.1), result shape,
core properties, package, page setup and the acceptance properties A1, A3, A5 (§18.1.4).
`tundlekit.render.office_running` is pinned to [] per test by conftest.py unless a test replaces it.
"""
from __future__ import annotations

import importlib
import os
import re
import zipfile
from pathlib import Path

import pytest

import helpers_r6r as h

@pytest.fixture(autouse=True)
def _author(monkeypatch):
    monkeypatch.setenv("TUNDLEKIT_AUTHOR", "Test Author")


# ------------------------------------------------------------------------------------ registration §18.6
def test_registration_and_schema():
    import tundlekit
    from tundlekit import registry

    importlib.import_module("tundlekit.report")
    mods = tundlekit.MODULES
    assert mods.index("report") == mods.index("claims") + 1
    listing = registry.TOOLS["report_build"].listing()
    schema = listing["inputSchema"]
    assert schema["additionalProperties"] is False
    assert set(schema["properties"]) == {"report", "out", "excerpts", "author", "overwrite", "force_office"}
    assert set(schema.get("required", [])) == {"report", "out"}
    ann = listing.get("annotations", {})
    assert ann.get("readOnlyHint") is False
    assert not ann.get("destructiveHint")


# ------------------------------------------------------------------------------------ result §18.1.4
def test_result_shape_and_counts(tmp_path):
    src = h.rich(tmp_path)
    res = h.build(src, tmp_path / "out.docx")
    assert set(res) >= {"out", "title", "author", "paragraphs", "tables", "figures", "excerpts", "page_breaks",
                        "words", "replaced", "warnings"}
    assert os.path.samefile(res["out"], tmp_path / "out.docx")
    assert res["title"] == "AI4Research: Workflow and Platform"
    assert res["author"] == "Test Author"
    assert (res["tables"], res["figures"], res["excerpts"], res["page_breaks"]) == (1, 2, 0, 1)
    assert res["replaced"] is False and res["warnings"] == []
    ps = h.paras(res["out"])
    assert res["paragraphs"] == len(ps)
    assert res["words"] == sum(len(t.split()) for _, t, _ in ps)


# ------------------------------------------------------------------------------------ order of checks
def test_missing_report_is_error_and_nothing_written(tmp_path):
    msg = h.build_error(tmp_path / "nope.md", tmp_path / "out.docx")
    assert msg and not (tmp_path / "out.docx").exists()


def test_invalid_utf8_is_error(tmp_path):
    src = tmp_path / "r.md"
    src.write_bytes(b"# T\n\nbad \xff\xfe byte\n")
    h.build_error(src, tmp_path / "out.docx")
    assert not (tmp_path / "out.docx").exists()


def test_bom_is_dropped(tmp_path):
    src = tmp_path / "r.md"
    src.write_bytes("﻿# Title\n\nBody text.\n".encode("utf-8"))
    res = h.build(src, tmp_path / "out.docx")
    assert res["title"] == "Title"
    assert h.paras(res["out"])[0][:2] == ("Heading1", "Title")


@pytest.mark.parametrize("name", ["out.txt", "out.docx.bak", "out"])
def test_out_must_end_in_docx(tmp_path, name):
    src = h.report(tmp_path, "# T\n")
    h.build_error(src, tmp_path / name)
    assert not (tmp_path / name).exists()


def test_out_suffix_any_case(tmp_path):
    src = h.report(tmp_path, "# T\n\nText.\n")
    res = h.build(src, tmp_path / "OUT.DOCX")
    assert zipfile.is_zipfile(res["out"])


def test_out_same_file_as_report(tmp_path):
    src = h.write(tmp_path / "same.docx", "# T\n\nText.\n")
    h.build_error(src, src)
    assert src.read_text(encoding="utf-8") == "# T\n\nText.\n"


def test_out_is_directory_or_parent_missing(tmp_path):
    src = h.report(tmp_path, "# T\n")
    (tmp_path / "dir.docx").mkdir()
    h.build_error(src, tmp_path / "dir.docx")
    h.build_error(src, tmp_path / "missing" / "out.docx")
    assert not (tmp_path / "missing").exists()


def test_out_checked_before_parse_problems(tmp_path):
    """Order 2 before 4: a bad `out` is reported, not the report's problems."""
    src = h.report(tmp_path, "# T\n\n#### too deep\n")
    msg = h.build_error(src, tmp_path / "out.txt")
    assert "line 3" not in msg


def test_parse_problems_before_hand_edit_guard(tmp_path):
    """Order 4 before 5: a garbage existing `out` is not mentioned while the report has problems."""
    src = h.report(tmp_path, "# T\n\n#### too deep\n")
    out = h.write(tmp_path / "out.docx", "not a zip")
    msg = h.build_error(src, out)
    assert "line 3:" in msg and "overwrite" not in msg
    assert out.read_text() == "not a zip"


# ------------------------------------------------------------------------------------ problems §18.1.1
def test_problems_collected_in_line_order(tmp_path):
    src = h.report(tmp_path, "# T\n\n![Fig. 1. x](missing.png)\n\n#### deep\n\n{{toc}}\n")
    msg = h.build_error(src, tmp_path / "out.docx")
    pos = [msg.find(f"line {n}:") for n in (3, 5, 7)]
    assert all(p >= 0 for p in pos) and pos == sorted(pos), msg
    assert "unknown placeholder" in msg
    assert not (tmp_path / "out.docx").exists()


@pytest.mark.parametrize("body, line", [
    ("# T\n\n![Fig. 1. x](https://example.com/a.png)\n", 3),
    ("# T\n\n![Fig. 1. x](//cdn.example.com/a.png)\n", 3),
    ("# T\n\ntext\n\n```python\ncode = 1\n", 5),
    ("# T\n\n##\n", 3),
    ("# T\n\n| a | b |\nplain\n", 3),
    ("# T\n\n| a | b |\n|---|---|\n| 1 | 2 | 3 |\n", 5),
    ("# T\n\n> - a list in a quote\n", 3),
    ("# T\n\n- \n", 3),
    ("# T\n\nbad \x01 control\n", 3),
])
def test_single_problem_reports_its_line(tmp_path, body, line):
    src = h.report(tmp_path, body)
    msg = h.build_error(src, tmp_path / "out.docx")
    assert re.search(rf"line {line}: ", msg), msg
    assert not (tmp_path / "out.docx").exists()


def test_non_image_figure_is_problem(tmp_path):
    h.write(tmp_path / "fake.png", "this is text, not a PNG")
    src = h.report(tmp_path, "# T\n\n![Fig. 1. fake](fake.png)\n")
    assert "line 3: " in h.build_error(src, tmp_path / "out.docx")


# ------------------------------------------------------------------------------------ Office guard §18.4
def test_office_guard_refuses_and_force_builds(tmp_path, monkeypatch):
    seen = []
    h.no_office(monkeypatch, ["WINWORD.EXE"], seen)
    src = h.report(tmp_path, "# T\n\nText.\n")
    msg = h.build_error(src, tmp_path / "out.docx")
    assert "refusing" in msg and "WINWORD.EXE" in msg
    assert not (tmp_path / "out.docx").exists()
    assert seen and not any(seen), "report_build uses office_running() without all_apps"
    assert h.build(src, tmp_path / "out.docx", force_office=True)["out"]


def test_excel_only_does_not_block(tmp_path, monkeypatch):
    h.no_office(monkeypatch, lambda all_apps: ["EXCEL.EXE"] if all_apps else [])
    src = h.report(tmp_path, "# T\n\nText.\n")
    assert Path(h.build(src, tmp_path / "out.docx")["out"]).is_file()


# ------------------------------------------------------------------------------------ hand-edit guard
def test_rebuild_without_changes_replaces(tmp_path):
    src = h.rich(tmp_path)
    out = tmp_path / "out.docx"
    h.build(src, out)
    res = h.build(src, out)
    assert res["replaced"] is True and res["warnings"] == []


def test_hand_edited_output_refused_then_overwrite(tmp_path):
    src = h.rich(tmp_path)
    out = tmp_path / "out.docx"
    h.build(src, out)
    h.call("text_apply_edits", edits=[{"find": "Which platform the work moves to",
                                        "replace": "Which platform we move to", "count": 1}],
           path=str(out), write=True)
    before = out.read_bytes()
    msg = h.build_error(src, out)
    assert "overwrite" in msg and "1" in msg
    assert out.read_bytes() == before
    res = h.build(src, out, overwrite=True)
    assert res["replaced"] is True
    assert "Which platform the work moves to" in h.texts(out)


def test_unreadable_existing_output_refused(tmp_path):
    src = h.report(tmp_path, "# T\n\nText.\n")
    out = h.write(tmp_path / "out.docx", "garbage, not a package")
    assert "overwrite" in h.build_error(src, out)
    assert out.read_text() == "garbage, not a package"
    assert h.build(src, out, overwrite=True)["replaced"] is True


# ------------------------------------------------------------------------------------ A1, A3, A5
def test_a1_round_trip_rich(tmp_path):
    src = h.rich(tmp_path)
    out = h.build(src, tmp_path / "out.docx")["out"]
    assert h.diff(str(src), out) == []
    assert h.diff(out, str(src)) == []


def test_a3_document_xml_deterministic(tmp_path, monkeypatch):
    monkeypatch.delenv("TUNDLEKIT_NOW", raising=False)
    src = h.rich(tmp_path)
    a = h.build(src, tmp_path / "a.docx")["out"]
    b = h.build(src, tmp_path / "b.docx")["out"]
    assert h.part(a, "word/document.xml") == h.part(b, "word/document.xml")
    doc = h.part(a, "word/document.xml").decode("utf-8")
    assert "w:rsid" not in doc
    ids = [int(x.get("id")) for x in h.xml(a).iter(h.WP + "docPr")]
    assert ids == list(range(ids[0], ids[0] + len(ids))) and len(ids) == 2


def test_a3_whole_file_deterministic_with_now(tmp_path, monkeypatch):
    monkeypatch.setenv("TUNDLEKIT_NOW", h.NOW)
    src = h.rich(tmp_path)
    a = h.build(src, tmp_path / "a.docx")["out"]
    b = h.build(src, tmp_path / "b.docx")["out"]
    assert Path(a).read_bytes() == Path(b).read_bytes()
    with zipfile.ZipFile(a) as z:
        assert all(i.date_time == (1980, 1, 1, 0, 0, 0) for i in z.infolist())


def test_a5_readers(tmp_path):
    out = h.build(h.rich(tmp_path), tmp_path / "out.docx")["out"]
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
    assert h.body(out) is not None
    docx = pytest.importorskip("docx")
    assert docx.Document(out).paragraphs


# ------------------------------------------------------------------------------------ CLI §0.4, §18.6
def test_cli_build_and_error(tmp_path, capsys):
    src = h.report(tmp_path, "# T\n\nAn ![inline](x.png) image.\n")
    code, data, _, _ = h.run_cli(capsys, ["report", "build", src, "-o", tmp_path / "o.docx", "--json"])
    assert code == 0 and data["warnings"] and data["warnings"][0].startswith("line 3: ")
    code, data, _, err = h.run_cli(capsys, ["report", "build", tmp_path / "none.md", "-o", tmp_path / "p.docx",
                                            "--json", "--author", "X"])
    assert code == 1 and "error" in data and err.startswith("tundlekit: ")
