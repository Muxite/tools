"""MANIFEST §9.2 papers_body, §9.3 papers_peek, §9.4 papers_list (hand-written text fixtures)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_misc as h  # noqa: E402

MARKER_PAGES = [
    "Title Of Paper\nAbstract\nWe study hyph-\nenated words and Foo-\nBar things.\n",
    "References\nThis page mentions early references.\n",
    "Method   with\t\tspaces\n",
    "Results\nReferences to prior work are here.\n",
    "Conclusion\n  REFERENCES  \n[1] Some cite.\n",
    "Appendix text\n",
]

FF_PAGES = ["Intro\nline", "Two", "Three", "Body four\nReferences\n[1] x", "Five"]


@pytest.fixture
def papers(tmp_path):
    h.write_marker_txt(tmp_path / "2401.11111.txt", MARKER_PAGES)
    h.write_ff_txt(tmp_path / "2401.22222.txt", FF_PAGES)
    h.write_marker_txt(tmp_path / "2401.33333.txt", ["One\n", "References\n", "Three\n"])
    return tmp_path


def body(capsys, pid, d, *extra):
    return h.run_cli(["papers", "body", pid, "--dir", d, *extra, "--json"], capsys)


# ------------------------------------------------------------------------------------------ §9.2 body

def test_body_default_range_stops_at_references(papers, capsys):
    """§9.2: references page = first page N > 3 with a line that is only References/REFERENCES/...; default 1..it."""
    code, data, _, _ = body(capsys, "2401.11111", papers)
    assert code == 0
    assert data["id"] == "2401.11111"
    assert data["pages"] == 6
    assert data["references_page"] == 5
    assert data["start"] == 1
    assert data["end"] == 5
    lines = data["text"].split("\n")
    assert [ln[: ln.index("]") + 1] for ln in lines] == ["[p1]", "[p2]", "[p3]", "[p4]", "[p5]"]
    assert all(ln.startswith(f"[p{i}] ") for i, ln in enumerate(lines, 1))
    assert "[p6]" not in data["text"]
    assert data["truncated"] is False
    assert data["chars"] == len(data["text"])


def test_body_hyphen_join_and_whitespace(papers, capsys):
    """§9.2: hyphen breaks before lower case are joined; single newlines become spaces; space/tab runs collapse."""
    code, data, _, _ = body(capsys, "2401.11111", papers)
    assert code == 0
    lines = data["text"].split("\n")
    assert "Title Of Paper Abstract We study hyphenated words and Foo- Bar things." in lines[0]
    assert "Method with spaces" in lines[2]
    assert "\t" not in data["text"]


def test_body_explicit_range(papers, capsys):
    """§9.2: --start/--end select pages."""
    code, data, _, _ = body(capsys, "2401.11111", papers, "--start", "2", "--end", "3")
    assert code == 0
    assert (data["start"], data["end"]) == (2, 3)
    lines = data["text"].split("\n")
    assert len(lines) == 2
    assert lines[0].startswith("[p2] ") and lines[1].startswith("[p3] ")
    assert data["references_page"] == 5


def test_body_start_only_ends_at_references(papers, capsys):
    """§9.2: without --end the range ends at the references page."""
    code, data, _, _ = body(capsys, "2401.11111", papers, "--start", "4")
    assert code == 0
    assert data["end"] == 5
    assert [ln[:4] for ln in data["text"].split("\n")] == ["[p4]", "[p5]"]


def test_body_no_references_after_page_3(papers, capsys):
    """§9.2: a References line on page <= 3 does not count; the range runs to the last page."""
    code, data, _, _ = body(capsys, "2401.33333", papers)
    assert code == 0
    assert data["references_page"] is None
    assert data["end"] == 3
    assert data["pages"] == 3
    assert len(data["text"].split("\n")) == 3


def test_body_truncation(papers, capsys):
    """§9.2: text is cut to max_chars and truncated is true."""
    _, full, _, _ = body(capsys, "2401.11111", papers)
    code, data, _, _ = body(capsys, "2401.11111", papers, "--max-chars", "30")
    assert code == 0
    assert data["truncated"] is True
    assert data["text"] == full["text"][:30]


def test_body_form_feed_format(papers, capsys):
    """§9: pdftotext output (form feeds) is accepted; references detection works the same."""
    code, data, _, _ = body(capsys, "2401.22222", papers)
    assert code == 0
    assert data["pages"] == 5
    assert data["references_page"] == 4
    assert data["end"] == 4
    lines = data["text"].split("\n")
    assert [ln[:4] for ln in lines] == ["[p1]", "[p2]", "[p3]", "[p4]"]
    assert "Intro line" in lines[0]


def test_body_missing_text_mentions_fetch(tmp_path, capsys):
    """§9.2: a missing text file gives ToolError containing 'fetch'."""
    code, data, _, err = body(capsys, "2401.44444", tmp_path)
    assert code == 1
    assert "fetch" in data["error"]
    assert "fetch" in err


# ------------------------------------------------------------------------------------------ §9.3 peek: abstract

def peek(**args):
    return h.call_tool("papers_peek", args)


def test_abstract_starts_at_word_abstract(tmp_path):
    """§9.3: from the first whole word 'abstract' (not 'abstraction'); single newlines become spaces."""
    h.write_raw(tmp_path / "2401.55555.txt",
                "Our abstraction layer\nAbstract\nWe propose X.\nIt works well.\nMore text here")
    data = peek(id="2401.55555", mode="abstract", dir=str(tmp_path))
    assert data["id"] == "2401.55555"
    assert data["abstract"] == "Abstract We propose X. It works well. More text here"


def test_abstract_chars_limit(tmp_path):
    """§9.3: `chars` characters long."""
    h.write_raw(tmp_path / "2401.55555.txt", "Intro\nABSTRACT\nWe propose a long method here.\n")
    data = peek(id="2401.55555", mode="abstract", dir=str(tmp_path), chars=20)
    assert data["abstract"] == "ABSTRACT We propose "


def test_abstract_without_word_starts_at_beginning(tmp_path):
    """§9.3: with no 'abstract' the text starts at the beginning."""
    h.write_raw(tmp_path / "2401.55556.txt", "Plain intro\nsecond line")
    data = peek(id="2401.55556", mode="abstract", dir=str(tmp_path))
    assert data["abstract"] == "Plain intro second line"


def test_abstract_cli(tmp_path, capsys, monkeypatch):
    """§9.3: `tundlekit papers abs ID --chars N` (dir defaults to the current directory)."""
    h.write_raw(tmp_path / "2401.55557.txt", "x\nAbstract here and more words")
    monkeypatch.chdir(tmp_path)
    code, data, _, _ = h.run_cli(["papers", "abs", "2401.55557", "--chars", "13", "--json"], capsys)
    assert code == 0
    assert data["abstract"] == "Abstract here"


# ------------------------------------------------------------------------------------------ §9.3 peek: grep

GREP_LINES = [
    "preamble needle zero",
    "===== page 1 =====",
    "alpha",
    "beta NEEDLE one",
    "gamma",
    "===== page 2 =====",
    "delta",
    "  needle two  ",
    "epsilon",
    "zeta",
]


@pytest.fixture
def grepdir(tmp_path):
    h.write_raw(tmp_path / "2401.66666.txt", "\n".join(GREP_LINES) + "\n")
    return tmp_path


def grep(d, pattern, **kw):
    return peek(id="2401.66666", mode="grep", dir=str(d), pattern=pattern, **kw)


def test_grep_pages_lines_case_insensitive(grepdir):
    """§9.3: case-insensitive; line is 1-based; page is 0 before the first marker."""
    data = grep(grepdir, "needle", context=0)
    assert data["id"] == "2401.66666"
    assert [(x["page"], x["line"]) for x in data["hits"]] == [(0, 1), (1, 4), (2, 8)]
    assert [x["text"] for x in data["hits"]] == ["preamble needle zero", "beta NEEDLE one", "needle two"]
    assert data["truncated"] is False


def test_grep_context_lines_joined(grepdir):
    """§9.3: text is lines line-context..line+context, stripped and joined with 1 space."""
    data = grep(grepdir, "needle two", context=1)
    assert data["hits"] == [{"page": 2, "line": 8, "text": "delta needle two epsilon"}]


def test_grep_default_context_is_2(grepdir):
    """§9.3: context defaults to 2."""
    data = grep(grepdir, "^gamma$")
    assert data["hits"][0]["text"] == "alpha beta NEEDLE one gamma ===== page 2 ===== delta"


def test_grep_max_hits_truncates(grepdir):
    """§9.3: stops after max_hits; truncated true if more existed."""
    data = grep(grepdir, "needle", context=0, max_hits=2)
    assert [x["line"] for x in data["hits"]] == [1, 4]
    assert data["truncated"] is True


def test_grep_invalid_regex(grepdir):
    """§9.3: an invalid regex gives ToolError."""
    with pytest.raises(h.tool_error()):
        grep(grepdir, "(unclosed")


def test_grep_cli(grepdir, capsys, monkeypatch):
    """§9.3: `tundlekit papers grep ID REGEX --context C --max-hits H`."""
    monkeypatch.chdir(grepdir)
    code, data, _, _ = h.run_cli(
        ["papers", "grep", "2401.66666", "ne+dle", "--context", "0", "--max-hits", "1", "--json"], capsys)
    assert code == 0
    assert data["hits"] == [{"page": 0, "line": 1, "text": "preamble needle zero"}]
    assert data["truncated"] is True


# ------------------------------------------------------------------------------------------ §9.4 list

@pytest.fixture
def library(tmp_path):
    (tmp_path / "2401.12345.pdf").write_bytes(b"%PDF-1.4 fake")
    h.write_marker_txt(tmp_path / "2401.12345.txt", ["a\n", "b\n", "c\n"])
    (tmp_path / "2402.00001v2.pdf").write_bytes(b"%PDF-1.4 fake")
    h.write_ff_txt(tmp_path / "2312.99999.txt", ["one", "two"])
    (tmp_path / "notes.txt").write_text("not a paper", encoding="utf-8")
    (tmp_path / "random.pdf").write_bytes(b"%PDF-1.4 fake")
    (tmp_path / "README.md").write_text("# papers", encoding="utf-8")
    (tmp_path / "summaries").mkdir()
    (tmp_path / "summaries" / "2401.12345 - Some Title.md").write_text("# Some Title", encoding="utf-8")
    return tmp_path


def test_list_entries(library):
    """§9.4: every pdf/txt with a valid-id stem, sorted by id; pdf/txt flags; pages from the text file."""
    data = h.call_tool("papers_list", {"dir": str(library)})
    papers = data["papers"]
    assert [p["id"] for p in papers] == ["2312.99999", "2401.12345", "2402.00001v2"]
    by = {p["id"]: p for p in papers}
    assert (by["2401.12345"]["pdf"], by["2401.12345"]["txt"], by["2401.12345"]["pages"]) == (True, True, 3)
    assert (by["2402.00001v2"]["pdf"], by["2402.00001v2"]["txt"], by["2402.00001v2"]["pages"]) == (True, False, None)
    assert (by["2312.99999"]["pdf"], by["2312.99999"]["txt"], by["2312.99999"]["pages"]) == (False, True, 2)


def test_list_summary_paths(library):
    """§9.4: summary is the path of summaries/{id} - *.md, else null."""
    by = {p["id"]: p for p in h.call_tool("papers_list", {"dir": str(library)})["papers"]}
    s = by["2401.12345"]["summary"]
    assert s is not None
    assert Path(s).name == "2401.12345 - Some Title.md"
    assert Path(s).parent.name == "summaries"
    assert by["2402.00001v2"]["summary"] is None
    assert by["2312.99999"]["summary"] is None


def test_list_default_dir_is_cwd(library, capsys, monkeypatch):
    """§9: dir defaults to the current directory."""
    monkeypatch.chdir(library)
    code, data, _, _ = h.run_cli(["papers", "list", "--json"], capsys)
    assert code == 0
    assert len(data["papers"]) == 3


def test_list_empty_dir(tmp_path):
    """§9.4: no papers gives an empty list (§14.7 adds missing_summary, also empty)."""
    data = h.call_tool("papers_list", {"dir": str(tmp_path)})
    assert data["papers"] == []
    assert data.get("missing_summary", []) == []


@pytest.mark.parametrize("name", ["papers_body", "papers_peek", "papers_list"])
def test_readers_are_read_only(name):
    """§0.2: tools that only read carry readOnlyHint true."""
    assert h.registry().TOOLS[name].annotations.get("readOnlyHint") is True
