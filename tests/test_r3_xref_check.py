"""text_xref: resolving references and renumbering (MANIFEST §15.2, with §7.2 captions, §0.3, §15.10).

Fixtures mimic notes/report-capsules/REPORT.md (`## N.` / `### N.M`, `## Appendix A.` / `### A.1`, captions
`![Fig. 1. ...](...)` and `*Table A2. ...*`), deck-src/build_deck.py footers, and the `between(...)` /
`section(...)` markers that notes/report-general/build/checks/check_markers.py checks.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_r3rc as r3  # noqa: E402

REPORT = [
    "# Capability Capsule in AI4Research",                                   # 1
    "",                                                                      # 2
    "## 1. The goal",                                                        # 3
    "",                                                                      # 4
    "### 1.1 MCP is a protocol",                                             # 5
    "",                                                                      # 6
    "![Fig. 1. MCP as a client-server protocol.](fig/fig-mcp.png)",          # 7
    "",                                                                      # 8
    "## 4. The design",                                                      # 9
    "",                                                                      # 10
    "### 4.2 Count repeats per sprint",                                      # 11
    "",                                                                      # 12
    "### 4.3 Admission: each manifest field has a check",                    # 13
    "",                                                                      # 14
    "*Fig. 9. Admission gate.*",                                             # 15
    "",                                                                      # 16
    "### 4.4 Picking a capsule",                                             # 17
    "",                                                                      # 18
    "*Fig. 10. Picking a capsule.*",                                         # 19
    "",                                                                      # 20
    "### 4.21 A deliberately awkward number",                                # 21
    "",                                                                      # 22
    "*Table 1. Design rules.*",                                              # 23
    "",                                                                      # 24
    "## References",                                                         # 25
    "",                                                                      # 26
    '[2] J. Qiu et al., "Alita-G," arXiv:2510.23601, Oct. 2025.',            # 27
    "",                                                                      # 28
    "## Appendix A. Paper details",                                          # 29
    "",                                                                      # 30
    "### A.1 Alita-G [2]",                                                   # 31
    "",                                                                      # 32
    "*Table A2. Alita-G results.*",                                          # 33
    "",                                                                      # 34
    "## Appendix C. Manifest fields",                                        # 35
    "",                                                                      # 36
    "## Appendix D. DSH facts",                                              # 37
    "",                                                                      # 38
    "### D.4 Plugins unload cleanly",                                        # 39
    "",
]

DECK = [
    "from deckkit import Deck",                                                                     # 1
    "",                                                                                             # 2
    'd = Deck("capsule")',                                                                          # 3
    's = d.slide("1 Goal", "The goal", "Capsule report §1, §1.1, Fig. 1", stage="build")',          # 4
    's = d.slide("2", "Evidence", "Capsule report §2.3, App. A.1, App. A.2 Table A2 · '
    'Alita-G (arXiv 2510.23601) Tables 1 and 6, §3.3")',                                            # 5
    's = d.slide("3", "Admission", "Capsule report §4.3, Fig. 9, App. C; other fields in App. C")',  # 6
    's = d.slide("4", "Picking", "Capsule report §4.4, Fig. 10; Table 1")',                         # 7
    's = d.slide("5", "Plugins", "Capsule report App. D.4; Fig. 12")',                              # 8
    's = d.slide("6", "Repeats", "Capsule report §4.2 and §4.21")',                                 # 9
    "",
]

READING = [
    "def between(start, end, src=None):",                      # 1
    "    return start",                                        # 2
    "",                                                        # 3
    "",                                                        # 4
    "def section(num, nxt=None):",                             # 5
    "    return num",                                          # 6
    "",                                                        # 7
    "",                                                        # 8
    "PAGES = [",                                               # 9
    '    between("## 1. The goal", "## 4. The design"),',      # 10
    '    section("4.2"),',                                     # 11
    '    section("4.9"),',                                     # 12
    '    between("Alita-G", "## Appendix C."),',               # 13
    "]",                                                       # 14
    "",
]


@pytest.fixture
def ws(tmp_path, monkeypatch):
    """Writes REPORT.md, build_deck.py and reading.py (LF) into tmp_path and chdirs there."""
    monkeypatch.chdir(tmp_path)

    def setup(newline="\n", report=REPORT, deck=DECK):
        r3.write(tmp_path / "REPORT.md", newline.join(report))
        r3.write(tmp_path / "build_deck.py", newline.join(deck))
        r3.write(tmp_path / "reading.py", newline.join(READING))
        return tmp_path
    setup()
    return setup


def run(files=("build_deck.py",), **kw):
    res = r3.xref(report="REPORT.md", files=list(files), **kw)
    r3.assert_checker_shape(res)
    return res


# ------------------------------------------------------------------ X001

def test_x001_missing_targets(ws):
    """§15.2: `§2.3`, `App. A.2` (line 5) and `Fig. 12` (line 8) have no target; each is its own error."""
    res = run()
    found = r3.of(res, "X001")
    assert sorted(f["line"] for f in found) == [5, 5, 8]
    assert all(f["severity"] == "error" and f["path"] == "build_deck.py" for f in found)
    assert res["ok"] is False
    assert res["edits"] == []


def test_mentions_after_arxiv_or_paper_are_skipped(ws):
    """§15.2 (as §7.2): mentions preceded on the line by `arXiv` or the whole word `paper` are skipped;
    `newspaper` does not count, and a mention before `arXiv` is still checked."""
    ws(deck=DECK[:3] + [
        'a = "Alita-G (arXiv 2510.23601) §3.3 and Fig. 4"',     # 4: skipped
        'b = "the paper reports Fig. 4 and Table 7"',           # 5: skipped
        'c = "a newspaper printed Fig. 4"',                     # 6: X001
        'd = "§6 · Alita-G (arXiv 2510.23601) §3.3"',           # 7: X001 for §6 only
    ])
    res = run()
    assert [f["line"] for f in r3.of(res, "X001")] == [6, 7]


def test_existing_targets_resolve(ws):
    """§15.2: sections, `App. X`, `App. X.n`, `Fig. n` and `Table Pn` from headings and captions all resolve."""
    deck = DECK[:4] + ['s = d.slide("2", "Evidence", "§4 and §4.4; App. A, App. A.1, App. D.4; Table A2; Fig. 10")']
    ws(deck=deck)
    res = run()
    assert res["findings"] == []
    assert res["ok"] is True


def test_several_references_on_one_line_checked_separately(ws):
    """§15.2: `§1.1, Fig. 7, Table 3` gives 2 findings (Fig. 7 and Table 3) on the same line."""
    ws(deck=DECK[:3] + ['x = "Capsule report §1.1, Fig. 7, Table 3"'])
    res = run()
    assert [f["line"] for f in r3.of(res, "X001")] == [4, 4]


# ------------------------------------------------------------------ X002

def test_x002_markers_not_found_exactly_once(ws):
    """§15.2: `section("4.9")` (marker `### 4.9 `, absent) and `between("Alita-G", ...)` (3 times) are warnings;
    `section("4.2")` matches `### 4.2 ` once (not `### 4.21 `)."""
    res = run(files=["reading.py"])
    found = r3.of(res, "X002")
    # pinned: path and line are the .py file and the call line
    assert [(f["severity"], f["path"], f["line"]) for f in found] == [
        ("warning", "reading.py", 12), ("warning", "reading.py", 13)]
    text = " ".join(f["message"] + " " + f["excerpt"] for f in found)
    assert "4.9" in text and "Alita-G" in text
    assert r3.of(res, "X001") == []
    assert res["ok"] is True


# ------------------------------------------------------------------ renumbering

def test_swap_dry_run_plans_edits_and_changes_nothing(ws, tmp_path):
    """§15.2: `Fig. 9=Fig. 10` with `Fig. 10=Fig. 9` is a swap; without write only edits are listed."""
    before = {p: p.read_bytes() for p in tmp_path.iterdir()}
    res = run(renumber=["Fig. 9=Fig. 10", "Fig. 10=Fig. 9"])
    # pinned: old/new are the reference texts
    assert sorted((e["path"], e["line"], e["old"], e["new"]) for e in res["edits"]) == [
        ("REPORT.md", 15, "Fig. 9", "Fig. 10"), ("REPORT.md", 19, "Fig. 10", "Fig. 9"),
        ("build_deck.py", 6, "Fig. 9", "Fig. 10"), ("build_deck.py", 7, "Fig. 10", "Fig. 9")]
    assert {p: p.read_bytes() for p in tmp_path.iterdir()} == before


def test_swap_write(ws, tmp_path):
    """§15.2: with write the swap is applied simultaneously to the files and the report captions."""
    run(renumber=["Fig. 9=Fig. 10", "Fig. 10=Fig. 9"], write=True)
    deck = r3.read(tmp_path / "build_deck.py").split("\n")
    report = r3.read(tmp_path / "REPORT.md").split("\n")
    assert deck[5] == DECK[5].replace("Fig. 9", "Fig. 10")
    assert deck[6] == DECK[6].replace("Fig. 10", "Fig. 9")
    assert report[14] == "*Fig. 10. Admission gate.*"
    assert report[18] == "*Fig. 9. Picking a capsule.*"
    assert deck[7] == DECK[7]                                    # Fig. 12 untouched


def test_whole_figure_references_only(ws, tmp_path):
    """§15.2: `Fig. 1=Fig. 2` changes `Fig. 1` but neither `Fig. 10` nor `Fig. 12`."""
    res = run(renumber=["Fig. 1=Fig. 2"], write=True)
    assert {(e["path"], e["line"]) for e in res["edits"]} == {("build_deck.py", 4), ("REPORT.md", 7)}
    deck = r3.read(tmp_path / "build_deck.py").split("\n")
    report = r3.read(tmp_path / "REPORT.md").split("\n")
    assert deck[3] == DECK[3].replace("Fig. 1", "Fig. 2")
    assert report[6].startswith("![Fig. 2. MCP")
    assert report[18] == REPORT[18] and deck[6] == DECK[6] and deck[7] == DECK[7]


def test_whole_section_references_only(ws, tmp_path):
    """§15.2: `§4.2=§4.5` changes `§4.2` and heading `### 4.2`, never `§4.21` / `### 4.21`."""
    res = run(renumber=["§4.2=§4.5"], write=True)
    assert sorted((e["path"], e["line"], e["old"], e["new"]) for e in res["edits"]) == [
        ("REPORT.md", 11, "§4.2", "§4.5"), ("build_deck.py", 9, "§4.2", "§4.5")]
    deck = r3.read(tmp_path / "build_deck.py").split("\n")
    report = r3.read(tmp_path / "REPORT.md").split("\n")
    assert deck[8] == 's = d.slide("6", "Repeats", "Capsule report §4.5 and §4.21")'
    assert report[10] == "### 4.5 Count repeats per sprint"
    assert report[20] == REPORT[20]


def test_appendix_renumber(ws, tmp_path):
    """§15.2: `App. D.4=App. D.5` changes the reference and the `### D.4` heading."""
    run(renumber=["App. D.4=App. D.5"], write=True)
    deck = r3.read(tmp_path / "build_deck.py").split("\n")
    report = r3.read(tmp_path / "REPORT.md").split("\n")
    assert deck[7] == 's = d.slide("5", "Plugins", "Capsule report App. D.5; Fig. 12")'
    assert report[38] == "### D.5 Plugins unload cleanly"


def test_report_prose_renumbered(ws, tmp_path):
    """Pinned details: references in the report's own prose are renumbered too, with the headings and captions."""
    report = REPORT[:11] + ["As §4.2 and Fig. 10 show, repeats are counted (see §4.21)."] + REPORT[12:]
    ws(report=report)
    res = run(renumber=["§4.2=§4.3", "§4.3=§4.2", "Fig. 10=Fig. 11"], write=True)
    lines = r3.read(tmp_path / "REPORT.md").split("\n")
    assert lines[10] == "### 4.3 Count repeats per sprint"
    assert lines[11] == "As §4.3 and Fig. 11 show, repeats are counted (see §4.21)."
    assert lines[12] == "### 4.2 Admission: each manifest field has a check"
    assert lines[18] == "*Fig. 11. Picking a capsule.*"
    report_edits = sorted((e["line"], e["old"], e["new"]) for e in res["edits"] if e["path"] == "REPORT.md")
    assert report_edits == [(11, "§4.2", "§4.3"), (12, "Fig. 10", "Fig. 11"), (12, "§4.2", "§4.3"),
                            (13, "§4.3", "§4.2"), (19, "Fig. 10", "Fig. 11")]


def test_write_preserves_crlf(ws, tmp_path):
    """§15.2: write keeps CRLF line endings in both the report and the checked file."""
    ws(newline="\r\n")
    run(renumber=["Fig. 9=Fig. 10", "Fig. 10=Fig. 9"], write=True)
    deck_b = (tmp_path / "build_deck.py").read_bytes()
    report_b = (tmp_path / "REPORT.md").read_bytes()
    assert r3.crlf_only(deck_b) and r3.crlf_only(report_b)
    assert "*Fig. 10. Admission gate.*\r\n" in report_b.decode("utf-8")
    assert "Fig. 9; Table 1" in deck_b.decode("utf-8")


def test_findings_computed_before_renumbering(ws):
    """§15.2: renumbering `Fig. 1=Fig. 12` does not clear the X001 for the existing `Fig. 12` mention."""
    res = run(renumber=["Fig. 1=Fig. 12"])
    assert sorted(f["line"] for f in r3.of(res, "X001")) == [5, 5, 8]
    assert res["edits"]


# ------------------------------------------------------------------ CLI and registration

def test_cli_renumber_write(ws, tmp_path, capsys):
    """§15.2/§0.4: `tundlekit text xref REPORT --in FILE --renumber OLD=NEW --write --json`; X001 exits 1."""
    code, data, _, _ = r3.run_cli(capsys, ["text", "xref", "REPORT.md", "--in", "build_deck.py",
                                           "--renumber", "App. D.4=App. D.5", "--write", "--json"])
    assert code == 1
    assert len([f for f in data["findings"] if f["rule"] == "X001"]) == 3
    assert "App. D.5" in r3.read(tmp_path / "build_deck.py")
    assert "### D.5 Plugins" in r3.read(tmp_path / "REPORT.md")


def test_registration_text_xref():
    """§15.10: text_xref lives in textlint, is not read-only, and has a strict schema."""
    t = r3.get_tool("textlint", "text_xref")
    assert t.annotations.get("readOnlyHint") is not True
    assert t.input_schema.get("additionalProperties") is False
    assert {"report", "files", "renumber", "write"} <= set(t.input_schema["properties"])
    assert t.func.__module__ == "tundlekit.textlint"
