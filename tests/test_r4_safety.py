"""Round-4 safety and robustness (MANIFEST §16.1): XML-safe edits, case-insensitive names, setup-table skips,
corrupt packages, rewrites, overflow, deduplicated inputs.

Directory errors and broken pipes are in test_r4_office.py."""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET

import pytest

import helpers_r4 as h


# ---------------------------------------------------------------- XML-safe text (§16.1)
def test_docx_replace_with_control_char_names_index_and_leaves_file(tmp_path):
    """§16.1: a `replace` with an XML-illegal control char is a ToolError naming the edit index; nothing written."""
    doc = h.make_docx(tmp_path / "r.docx", ["Alpha beta gamma.", "Delta epsilon."])
    before = doc.read_bytes()
    edits = [{"find": "Alpha", "replace": "ALPHA"},
             {"find": "Delta", "replace": "De\x01lta"}]
    with pytest.raises(h.tool_error()) as exc:
        h.call("text_apply_edits", path=doc, edits=edits, write=True)
    assert h.names_index(str(exc.value), 1)
    assert doc.read_bytes() == before


def test_docx_find_with_nonchar_is_refused(tmp_path):
    """§16.1: every `find` is validated too (U+FFFE is illegal in XML 1.0)."""
    doc = h.make_docx(tmp_path / "r.docx", ["Alpha beta gamma."])
    before = doc.read_bytes()
    with pytest.raises(h.tool_error()):
        h.call("text_apply_edits", path=doc, edits=[{"find": "Alpha\ufffe", "replace": "x"}], write=True)
    assert doc.read_bytes() == before


def test_text_file_lone_surrogate_replace_refused(tmp_path):
    """§16.1: lone surrogates are refused for text files; nothing is written."""
    md = h.write(tmp_path / "notes.md", "one two three\n")
    before = md.read_bytes()
    with pytest.raises(h.tool_error()) as exc:
        h.call("text_apply_edits", path=md, edits=[{"find": "two", "replace": "t\ud800o"}], write=True)
    assert h.names_index(str(exc.value), 0)
    assert md.read_bytes() == before


# ---------------------------------------------------------------- case-insensitive names (§16.1)
def test_bundle_source_refuses_lowercase_source_md(tmp_path):
    """§16.1: bundle_source refuses a SOURCE.md input case-insensitively, even with force."""
    f = h.write(tmp_path / "setup" / "tool" / "source.md", "# tool 1.0\n")
    with pytest.raises(h.tool_error()):
        h.call("bundle_source", file=f, write=True, force=True)


def test_setup_table_never_adds_lowercase_readme(tmp_path):
    """§16.1: bundle_setup_table treats `readme.md` as the README, never as an entry."""
    d = tmp_path / "setup" / "tool"
    h.write(d / "readme.md", "# Tool\n")
    (d / "tool-1.2.3-x64.exe").write_bytes(b"MZ")
    res = h.call("bundle_setup_table", dir=d)
    joined = "\n".join(res["added"])
    assert "tool-1.2.3-x64.exe" in joined
    assert "readme.md" not in joined.lower()


def test_b006_exempts_mixed_case_readme(tmp_path):
    """§16.1: the B006 exemption for README.md is case-insensitive."""
    root = tmp_path / "tundle"
    h.write(root / "VERSION", "2026.09.16.0\n")
    h.write(root / "CHANGELOG.md", "# Changelog\n\n<!-- entries -->\n")
    h.write(root / "setup" / "README.md", "# Setup\n")
    d = root / "setup" / "tool"
    h.write(d / "Readme.MD", "| File | What it is |\n|---|---|\n| `app-2.0.exe` | app 2.0 |\n")
    (d / "app-2.0.exe").write_bytes(b"MZ")
    res = h.call("bundle_lint", root=root)
    b006 = [f["path"] for f in res["findings"] if f["rule"] == "B006"]
    assert not any(p.lower().endswith("readme.md") for p in b006), b006


# ---------------------------------------------------------------- setup_table skips (§16.1)
def test_setup_table_skips_junk_and_backtick_names(tmp_path):
    """§16.1: junk files and names with a backtick (or `|`) are listed in `skipped`, never added."""
    d = tmp_path / "setup" / "tool"
    d.mkdir(parents=True)
    (d / "Thumbs.db").write_bytes(b"x")
    (d / "we`ird-1.0.exe").write_bytes(b"MZ")
    (d / "good-1.0.exe").write_bytes(b"MZ")
    bad = ["Thumbs.db", "we`ird-1.0.exe"]
    if sys.platform != "win32":
        (d / "pi|pe-1.0.exe").write_bytes(b"MZ")
        bad.append("pi|pe-1.0.exe")
    res = h.call("bundle_setup_table", dir=d)
    joined = "\n".join(res["added"])
    assert "good-1.0.exe" in joined
    for name in bad:
        assert name not in joined
    skipped = {s["name"]: s for s in res["skipped"]}
    assert set(bad) <= set(skipped)
    assert all(s["reason"] for s in res["skipped"])


def test_pipe_line_in_fence_is_not_a_table(tmp_path):
    """§16.1: a `|` line inside a fenced code block is never taken as a table."""
    d = tmp_path / "setup" / "tool"
    fence = "```\n| not | a table |\n|---|---|\n```\n"
    readme = h.write(d / "README.md", "# Tool\n\n" + fence)
    (d / "app-3.1.exe").write_bytes(b"MZ")
    res = h.call("bundle_setup_table", dir=d, write=True)
    assert res["written"] is True
    text = readme.read_text(encoding="utf-8")
    assert fence in text
    after = text.split(fence, 1)[1]
    assert "`app-3.1.exe`" in after
    assert "| File | What it is |" in after


# ---------------------------------------------------------------- corrupt packages (§16.1)
def test_corrupt_document_xml_is_tool_error(tmp_path):
    """§16.1: a bad deflate stream in word/document.xml is a ToolError for docx_diff and text_apply_edits."""
    good = h.make_docx(tmp_path / "good.docx", ["Same text."])
    bad = h.corrupt_entry(h.make_docx(tmp_path / "bad.docx", ["Same text."]), "word/document.xml")
    with pytest.raises(h.tool_error()):
        h.call("docx_diff", old=good, new=bad)
    with pytest.raises(h.tool_error()):
        h.call("text_apply_edits", path=bad, edits=[{"find": "Same", "replace": "Other"}])


def test_corrupt_image_part_does_not_block_edit(tmp_path):
    """§16.1: text_apply_edits decompresses only the parts it needs; other parts are copied raw."""
    doc = h.corrupt_entry(h.make_docx(tmp_path / "img.docx", ["Keep this.", "Change me."], image=True),
                          "word/media/image1.png")
    res = h.call("text_apply_edits", path=doc, edits=[{"find": "Change me", "replace": "Changed"}], write=True)
    assert res["ok"] is True
    assert "Changed." in h.docx_text(doc)


# ---------------------------------------------------------------- rewrites keep the file (§16.1)
def test_apply_edits_keeps_permission_bits(tmp_path):
    """§16.1: the atomic rewrite keeps the original permission bits."""
    md = h.write(tmp_path / "a.md", "old text\n")
    if not h.chmod_works(md, 0o640):
        pytest.skip("chmod has no effect on this platform")
    h.call("text_apply_edits", path=md, edits=[{"find": "old", "replace": "new"}], write=True)
    import os

    assert (os.stat(md).st_mode & 0o777) == 0o640
    assert md.read_text(encoding="utf-8") == "new text\n"


def test_apply_edits_writes_through_symlink(tmp_path):
    """§16.1: a rewrite goes to the symlink's target; the link stays a link."""
    if not h.can_symlink(tmp_path):
        pytest.skip("symlinks not permitted")
    import os

    target = h.write(tmp_path / "real" / "t.md", "alpha\n")
    link = tmp_path / "link.md"
    os.symlink(target, link)
    h.call("text_apply_edits", path=link, edits=[{"find": "alpha", "replace": "beta"}], write=True)
    assert link.is_symlink()
    assert target.read_text(encoding="utf-8") == "beta\n"


# ---------------------------------------------------------------- overflow (§16.1)
@pytest.mark.parametrize("geom", [{"x": 1e12}, {"w": 1e-9}])
def test_geometry_out_of_bounds_is_validation_problem(tmp_path, geom):
    """§16.1: geometry outside 0..1000 in (w, h >= 0.01) is a validation problem (ToolError)."""
    h.need_pptx()
    block = {"kind": "point", "text": "hello", "x": 1, "y": 2, "w": 5, "h": 1}
    block.update(geom)
    spec = h.deck_spec(h.content_slide("Geometry", [block]))
    with pytest.raises(h.tool_error()) as exc:
        h.call("deck_build", spec=spec, out=tmp_path / "g.pptx")
    assert list(geom)[0] in str(exc.value)


def test_non_finite_ledger_sum_is_tool_error(tmp_path):
    """§16.1: a ledger sum that is not finite is a validation problem, not a crash."""
    h.need_pptx()
    times = h.write(tmp_path / "times.json", '{"other": 1e308, "more": 1e308}')
    spec = h.deck_spec(h.content_slide("Ledger", {"kind": "bullets", "items": ["a"]}))
    with pytest.raises(h.tool_error()):
        h.call("deck_build", spec=spec, out=tmp_path / "l.pptx", times_file=times)


def test_excerpt_caption_that_does_not_fit_is_warning(tmp_path):
    """§16.1: a caption that doesn't fit gives a warning, is omitted, and no box gets a negative height."""
    h.need_pptx()
    block = {"kind": "excerpt", "text": "line one\nline two", "caption": "CAPTION-XYZ",
             "x": 1, "y": 2, "w": 6, "h": 0.2}
    out = tmp_path / "e.pptx"
    res = h.call("deck_build", spec=h.deck_spec(h.content_slide("Excerpt", [block])), out=out)
    assert any("caption" in w.lower() for w in res["warnings"]), res["warnings"]
    xml = h.all_part_text(out, "ppt/slides/slide")
    assert 'cy="-' not in xml
    assert "CAPTION-XYZ" not in xml


def test_chart_axis_with_subnormal_max(tmp_path):
    """§16.1: chart axis ticks handle any positive maximum, including subnormal floats."""
    res = h.call("chart_bar", spec={"categories": ["a", "b"], "values": [5e-324, 0], "axis": True})
    root = ET.fromstring(res["svg"])
    assert any("axis" in (g.get("class") or "").split() for g in root.iter("{http://www.w3.org/2000/svg}g"))
    low = res["svg"].lower()
    assert "nan" not in low and "inf" not in low


# ---------------------------------------------------------------- deduplicated inputs (§16.1)
def test_docx_diff_search_dedups_slash_forms(tmp_path):
    """§16.1: `C:/x` and `C:\\x` naming the same file are 1 search input (1 hint, not 2)."""
    old = h.make_docx(tmp_path / "old.docx", ["The broker leases each capability once."])
    new = h.make_docx(tmp_path / "new.docx", ["The broker leases every capability once."])
    notes = h.write(tmp_path / "src" / "notes.md", "intro\n\nThe broker leases each capability once.\n")
    fwd, back = str(notes).replace("\\", "/"), str(notes).replace("/", "\\")
    res = h.call("docx_diff", old=old, new=new, search=[fwd, back])
    assert len(res["changes"]) == 1
    assert len(res["changes"][0]["hint"]) == 1, res["changes"][0]["hint"]


@pytest.mark.skipif(sys.platform != "win32", reason="Git Bash drive form is a Windows spelling")
def test_docx_diff_search_accepts_git_bash_form(tmp_path):
    """§16.1: `/c/x` (Git Bash) names the same file as `C:/x`; together they give 1 hint."""
    old = h.make_docx(tmp_path / "old.docx", ["Gates decide what enters the library."])
    new = h.make_docx(tmp_path / "new.docx", ["Gates decide what leaves the library."])
    notes = h.write(tmp_path / "notes.md", "Gates decide what enters the library.\n")
    res = h.call("docx_diff", old=old, new=new, search=[h.git_bash_form(notes), str(notes)])
    assert len(res["changes"]) == 1
    assert len(res["changes"][0]["hint"]) == 1, res["changes"][0]["hint"]


def test_text_xref_files_dedup(tmp_path):
    """§16.1: `files` given twice in different spellings are checked once (1 X001, not 2)."""
    report = h.write(tmp_path / "report.md", "# Report\n\n## 1. Intro\n\nText.\n")
    script = h.write(tmp_path / "deck.md", "See §9 for details.\n")
    res = h.call("text_xref", report=report,
                 files=[str(script).replace("\\", "/"), str(script).replace("/", "\\")])
    assert len([f for f in res["findings"] if f["rule"] == "X001"]) == 1
