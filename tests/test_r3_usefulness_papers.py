"""MANIFEST §14.7 papers: body `appendix`, grep `width`, fetch `reextract`, layout-text detection and
papers_list `missing_summary`."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_misc as h  # noqa: E402

PAGES = [
    "Alita-G: self-evolving agents\nAbstract\nWe build a tool library from correct runs.\n",
    "Method\nThe distinct share falls from 100% to 51% at 128 tools.\n",
    "Results\nTable 3 lists the accuracy per benchmark.\n",
    "Conclusion\nReferences\n[1] Some cited work.\n",
    "Appendix A\nPrompt templates used for tool abstraction.\n",
    "Appendix B\nFull per-task results with the held-out split.\n",
]

LAYOUT_PAGES = [
    "Table 3: accuracy\nMethod        GAIA      PathVQA\nAlita-G       83.0      60.2\n"
    "Baseline      75.0      52.1\nNotes follow in the text.\n",
    "Tools         128       51%\nPlain prose line here.\n",
]


@pytest.fixture
def library(tmp_path):
    h.write_marker_txt(tmp_path / "2510.23601.txt", PAGES)
    h.write_marker_txt(tmp_path / "2604.00392.txt", LAYOUT_PAGES)
    h.write_raw(tmp_path / "2606.11926.pdf", "%PDF-1.4 not really")
    (tmp_path / "summaries").mkdir()
    h.write_raw(tmp_path / "summaries" / "2510.23601 - Alita-G.md", "# Alita-G\n")
    return tmp_path


def body(pid, d, **kw):
    return h.call_tool("papers_body", {"id": pid, "dir": str(d), **kw})


# ====================================================================== appendix
def test_body_default_stops_at_references(library):
    """§9.2 unchanged: the default end is the references page."""
    r = body("2510.23601", library)
    assert (r["references_page"], r["start"], r["end"]) == (4, 1, 4)
    assert "[p5]" not in r["text"]


def test_body_appendix_runs_to_last_page(library):
    """§14.7: with appendix, the default end becomes the last page."""
    r = body("2510.23601", library, appendix=True)
    assert r["end"] == 6
    assert "[p5] Appendix A" in r["text"] and "[p6] Appendix B" in r["text"]
    assert r["references_page"] == 4


def test_body_appendix_explicit_end_wins(library):
    """§14.7: appendix only changes the default end."""
    r = body("2510.23601", library, appendix=True, end=5)
    assert r["end"] == 5
    assert "[p6]" not in r["text"]


def test_body_appendix_cli(library, capsys):
    """§14.7: CLI `--appendix`."""
    code, data, _, _ = h.run_cli(["papers", "body", "2510.23601", "--dir", library, "--appendix", "--json"], capsys)
    assert code == 0
    assert data["end"] == 6


# ====================================================================== grep width
def test_grep_width_cuts_around_match(tmp_path):
    """§14.7: `width` cuts each hit's text to at most width characters, centred on the first match."""
    line = "x" * 300 + " held-out merge gate " + "y" * 300
    h.write_marker_txt(tmp_path / "2606.11926.txt", ["before\n" + line + "\nafter\n"])
    r = h.call_tool("papers_peek", {"id": "2606.11926", "mode": "grep", "dir": str(tmp_path),
                                    "pattern": "merge gate", "width": 60})
    assert len(r["hits"]) == 1
    t = r["hits"][0]["text"]
    assert len(t) <= 60
    assert "merge gate" in t
    assert "x" in t and "y" in t


def test_grep_without_width_is_unchanged(tmp_path):
    """§9.3: without width the full context text is returned."""
    line = "x" * 300 + " held-out merge gate " + "y" * 300
    h.write_marker_txt(tmp_path / "2606.11926.txt", [line + "\n"])
    r = h.call_tool("papers_peek", {"id": "2606.11926", "mode": "grep", "dir": str(tmp_path),
                                    "pattern": "merge gate", "context": 0})
    assert r["hits"][0]["text"] == line


def test_grep_width_cli(tmp_path, capsys):
    """§14.7: CLI `--width`."""
    h.write_marker_txt(tmp_path / "2606.11926.txt", ["a" * 200 + "Kosmos" + "b" * 200 + "\n"])
    code, data, _, _ = h.run_cli(["papers", "grep", "2606.11926", "kosmos", "--dir", tmp_path,
                                  "--width", "40", "--json"], capsys)
    assert code == 0
    t = data["hits"][0]["text"]
    assert len(t) <= 40 and "Kosmos" in t


# ====================================================================== reextract
def _present(tmp_path):
    pytest.importorskip("pymupdf")
    h.make_pdf(tmp_path / "2510.23601.pdf", ["fresh extracted page text"])
    h.write_raw(tmp_path / "2510.23601.txt", "\n\n===== page 1 =====\nstale layout text\n")


def test_fetch_keeps_existing_text_by_default(tmp_path):
    """§9.1 unchanged: an existing .txt is not rewritten."""
    _present(tmp_path)
    r = h.call_tool("papers_fetch", {"ids": ["2510.23601"], "dir": str(tmp_path),
                                     "base_url": "http://127.0.0.1:9/pdf", "delay": 0})
    assert r["results"][0]["status"] == "present"
    assert "stale layout text" in (tmp_path / "2510.23601.txt").read_text(encoding="utf-8")


def test_fetch_reextract_rewrites_text(tmp_path):
    """§14.7: reextract rewrites the .txt from the PDF even if it exists."""
    _present(tmp_path)
    r = h.call_tool("papers_fetch", {"ids": ["2510.23601"], "dir": str(tmp_path),
                                     "base_url": "http://127.0.0.1:9/pdf", "delay": 0, "reextract": True})
    assert r["ok"] is True
    assert r["results"][0]["status"] == "present"
    text = (tmp_path / "2510.23601.txt").read_text(encoding="utf-8")
    assert "fresh extracted page text" in text
    assert "stale layout text" not in text
    assert r["results"][0]["pages"] == 1


def test_fetch_reextract_cli(tmp_path, capsys):
    """§14.7: CLI `--reextract`."""
    _present(tmp_path)
    code, data, _, _ = h.run_cli(["papers", "fetch", "2510.23601", "--dir", tmp_path, "--base-url",
                                  "http://127.0.0.1:9/pdf", "--delay", "0", "--reextract", "--json"], capsys)
    assert code == 0
    assert "fresh extracted page text" in (tmp_path / "2510.23601.txt").read_text(encoding="utf-8")


# ====================================================================== layout text
def test_body_layout_text_detected(library):
    """§14.7: more than 20% of non-blank lines with a 5+ space run -> layout_text true and a warning."""
    r = body("2604.00392", library)
    assert r["layout_text"] is True
    assert any("reextract" in w for w in r["warnings"])


def test_body_plain_text_not_layout(library):
    """§14.7: ordinary text -> layout_text false; warnings is always present."""
    r = body("2510.23601", library)
    assert r["layout_text"] is False
    assert r["warnings"] == []


def test_list_layout_text_and_missing_summary(library):
    """§14.7: papers_list entries carry layout_text; the result carries missing_summary."""
    data = h.call_tool("papers_list", {"dir": str(library)})
    by = {p["id"]: p for p in data["papers"]}
    assert by["2604.00392"]["layout_text"] is True
    assert by["2510.23601"]["layout_text"] is False
    assert all(isinstance(p["layout_text"], bool) for p in data["papers"])
    assert sorted(data["missing_summary"]) == ["2604.00392", "2606.11926"]


def test_list_missing_summary_empty(tmp_path):
    """§14.7: no papers -> missing_summary is an empty list."""
    data = h.call_tool("papers_list", {"dir": str(tmp_path)})
    assert data["papers"] == [] and data["missing_summary"] == []
