"""text_xref and review_coverage round 4 (MANIFEST §16.5, on top of §15.1, §15.2, §0.3, §0.4).

Layout mirrors the tundle: notes/report-capsules/REPORT.md, notes/report-general/REPORT.md with its
REPORT-annotated.md variant, and notes/report-general/build/build_reading.py, whose `between(..., src=CAPSULE)`
slices resolve through module-level `NAME = (... / "...REPORT-annotated.md").read_text()` assignments.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_r4c as r4  # noqa: E402

CAP = "notes/report-capsules/REPORT.md"
GEN = "notes/report-general/REPORT.md"

CAP_TEXT = "\n".join([
    "# Capability Capsule in AI4Research",      # 1
    "",                                         # 2
    "## 2. The evidence",                       # 3
    "",                                         # 4
    "### 2.8 AllocBench",                       # 5
    "",                                         # 6
    "## 4. The design",                         # 7
    "",                                         # 8
    "### 4.2 Count repeats per sprint",         # 9
    "",                                         # 10
    "*Fig. 9. Admission gate.*",                # 11
    "",                                         # 12
    "```",                                      # 13
    "### 5.1 Not a heading",                    # 14
    "See §4.2 inside code.",                    # 15
    "```",                                      # 16
    "",                                         # 17
    "### 4.21 A deliberately awkward number",   # 18
    "",
])
GEN_TEXT = "# General Report\n\n## 3. Evaluation\n\n### 3.5 Only general\n\n## 4. Later\n"
READING = "\n".join([
    "import pathlib",                                                                       # 1
    "",                                                                                     # 2
    "HERE = pathlib.Path(__file__).parent",                                                 # 3
    "ROOT = HERE.parents[2]",                                                               # 4
    'REPORT = (HERE.parent / "REPORT-annotated.md").read_text(encoding="utf-8")',           # 5
    'CAPSULE = (ROOT / "notes/report-capsules/REPORT-annotated.md").read_text(encoding="utf-8")',  # 6
    'OLD = (HERE / "archive/REPORT-old.md").read_text(encoding="utf-8")',                   # 7
    "",                                                                                     # 8
    "def between(start, end, src=REPORT, after=0):",                                        # 9
    "    return src[src.find(start):src.find(end)]",                                        # 10
    "",                                                                                     # 11
    'A = between("Only in the annotated general", "## 4.")',                                # 12
    'B = between("The 5 gaps as read in source", "\\n\\n## ", src=CAPSULE)',                 # 13
    'C = between("Only in the annotated general", "## 4.", src=CAPSULE)',                   # 14
    'D = between("The 5 gaps as read in source", "## 4.", CAPSULE)',                        # 15
    'E = between("anything", "else", src=OLD)',                                             # 16
    'F = between("x", "y", src=UNBOUND)',                                                   # 17
    "",
])


@pytest.fixture
def ws(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    r4.write(tmp_path / CAP, CAP_TEXT)
    r4.write(tmp_path / GEN, GEN_TEXT)
    r4.write(tmp_path / "notes/report-general/REPORT-annotated.md",
             "# General Report\n\n## 3. Evaluation\n\nOnly in the annotated general text.\n\n## 4. Later\n")
    r4.write(tmp_path / "notes/report-capsules/REPORT-annotated.md",
             "# Capsule\n\n## 3. Today\n\nThe 5 gaps as read in source.\n\n## 4. The design\n")
    r4.write(tmp_path / "notes/report-general/build/build_reading.py", READING)
    return tmp_path


# ------------------------------------------------------------------ text_xref: pairing, exclude, skips
def test_file_report_pairs_without_report(ws):
    """§16.5: `FILE=REPORT` entries pair each file with its own report; `report` is omitted."""
    r4.write(ws / "deck/capsule.py", 'a = "Source: §2.8"\nb = "Source: §3.5"\n')
    r4.write(ws / "deck/general.py", 'a = "Source: §2.8"\nb = "Source: §3.5"\n')
    res = r4.run_xref(files=[f"deck/capsule.py={CAP}", f"deck/general.py={GEN}"])
    assert r4.where(res, "X001") == [("deck/capsule.py", 2), ("deck/general.py", 1)]


def test_directory_pair_and_exclude_globs(ws):
    """§16.5: a directory may be paired too; `exclude` globs drop walked files."""
    r4.write(ws / "pack/a.md", "Slide 2 cites §9.1.\n")
    r4.write(ws / "pack/old/legacy.md", "Slide 9 cites §9.2.\n")
    res = r4.run_xref(files=[f"pack={CAP}"], exclude=["*legacy*"])
    assert r4.where(res, "X001") == [("pack/a.md", 1)]


def test_numbered_citation_bracket_skipped(ws):
    """§16.5: `[5, App. H]` is a paper citation; a bracket not starting with a number is still checked."""
    r4.write(ws / "f.md", "DGM result, §2.8 [5, App. H].\nOur own note [App. H].\n")
    res = r4.run_xref(report=CAP, files=["f.md"])
    assert r4.where(res, "X001") == [("f.md", 2)]


def test_other_report_mentions_skipped(ws):
    """§16.5: with the capsule report paired, `general report §3.5` and `other report §7` are skipped,
    but a reference before those words is checked."""
    r4.write(ws / "f.md", "Source: §2.8; general report §3.5\n§9.9; see the general report §3.5\n"
                          "The other report §7 says so.\n")
    res = r4.run_xref(report=CAP, files=["f.md"])
    found = r4.of(res, "X001")
    assert [f["line"] for f in found] == [2]
    assert "9.9" in found[0]["message"] + found[0]["excerpt"]


def test_own_report_name_is_checked(ws):
    """§16.5: `General report §3.9` is checked when the paired report is the general report."""
    r4.write(ws / "f.md", "General report §3.5, §3.9\n")
    res = r4.run_xref(files=[f"f.md={GEN}"])
    assert r4.where(res, "X001") == [("f.md", 1)]


def test_cli_pairs_and_exclude(ws, capsys):
    """§16.5/§0.4: `text xref --in FILE=REPORT --exclude GLOB --json` without the positional report."""
    r4.write(ws / "pack/a.md", "Slide 2 cites §9.1.\n")
    r4.write(ws / "pack/b_legacy.md", "Slide 9 cites §9.2.\n")
    code, data, _, _ = r4.run_cli(capsys, ["text", "xref", "--in", f"pack={CAP}", "--exclude", "*legacy*",
                                           "--json"])
    assert code == 1
    assert [(f["path"], f["line"]) for f in data["findings"]] == [("pack/a.md", 1)]


# ------------------------------------------------------------------ text_xref: slice sources
def test_slice_sources_resolved_from_module_assignments(ws):
    """§16.5: src=CAPSULE (keyword or 3rd positional) checks the capsule annotated file; calls without src use
    the module default REPORT-annotated.md; only line 14 is an X002."""
    res = r4.run_xref(report=GEN, files=["notes/report-general/build/build_reading.py"])
    assert r4.where(res, "X002") == [("notes/report-general/build/build_reading.py", 14)]


def test_unresolvable_source_is_x003_info(ws):
    """§16.5: `src=OLD` (file missing) and `src=UNBOUND` (no assignment) are skipped with X003 info."""
    res = r4.run_xref(report=GEN, files=["notes/report-general/build/build_reading.py"])
    x3 = r4.of(res, "X003")
    assert [(f["severity"], f["line"]) for f in x3] == [("info", 16), ("info", 17)]
    assert all(f["path"] == "notes/report-general/build/build_reading.py" for f in x3)
    assert res["ok"] is True


def test_section_second_argument_used_as_written(ws):
    """§16.5: `section('4.2', '### 4.21 ...')` builds `### 4.2 ` from arg 1 only; arg 2 is looked up as is."""
    r4.write(ws / "slices.py", "def section(num, nxt):\n    return num\n\n\n"
                               "A = section('4.2', '### 4.21 A deliberately')\n"
                               "B = section('4.21', '### 4.9 ')\n")
    res = r4.run_xref(report=CAP, files=["slices.py"])
    assert r4.where(res, "X002") == [("slices.py", 6)]


# ------------------------------------------------------------------ text_xref: renumbering safety
def test_fenced_code_holds_no_targets(ws):
    """§16.5: `### 5.1` inside a fence is not a target."""
    r4.write(ws / "f.md", "Cites §5.1 and §4.2.\n")
    assert r4.where(r4.run_xref(report=CAP, files=["f.md"]), "X001") == [("f.md", 1)]


def test_fenced_code_never_renumbered(ws):
    """§16.5: `§4.2=§4.5` changes the heading but not the `§4.2` inside the fence (line 15)."""
    res = r4.run_xref(report=CAP, files=[], renumber=["§4.2=§4.5"], write=True)
    lines = r4.read(ws / CAP).split("\n")
    assert lines[8] == "### 4.5 Count repeats per sprint"
    assert lines[14] == "See §4.2 inside code."
    assert [(e["path"], e["line"]) for e in res["edits"]] == [(CAP, 9)]


def test_renumber_keeps_spelling(ws):
    """§16.5: `Fig.9`→`Fig.10`, `§ 4.2`→`§ 4.3`, `Fig. 09`→`Fig. 10`."""
    r4.write(ws / "f.md", "See Fig.9, § 4.2 and Fig. 09.\n")
    r4.run_xref(report=CAP, files=["f.md"], renumber=["Fig. 9=Fig. 10", "§4.2=§4.3"], write=True)
    assert r4.read(ws / "f.md") == "See Fig.10, § 4.3 and Fig. 10.\n"


def test_heading_renumber_updates_slice_markers(ws):
    """§16.5: renumbering heading 4.2 also rewrites markers that quote its text, and lists them in edits."""
    r4.write(ws / "reading.py", 'def between(a, b):\n    return a\n\n\n'
                                'X = between("### 4.2 Count repeats per sprint", "### 4.21 A deliberately")\n')
    res = r4.run_xref(report=CAP, files=["reading.py"], renumber=["§4.2=§4.5"], write=True)
    text = r4.read(ws / "reading.py")
    assert 'between("### 4.5 Count repeats per sprint", "### 4.21 A deliberately")' in text
    assert ("reading.py", 5) in {(e["path"], e["line"]) for e in res["edits"]}


# ------------------------------------------------------------------ review_coverage
CAP12 = "every capsule that the builder writes is replayed against the held out"
JUNK = " ".join(["qqqq", "zzzz", "wwww", "vvvv", "jjjj", "kkkk", "xxxx", "yyyy", "bbbb"] * 3)
RC_REPORT = [
    "# Capability Capsule",                                                                         # 1
    "",                                                                                             # 2
    "## 2. The evidence",                                                                           # 3
    "",                                                                                             # 4
    "- R1: every sprint pins versions; the planner records each pin in the snapshot and refuses "
    "to plan when a pin is missing",                                                                # 5
    f"- R2: {CAP12} suite before any planner may bind it to a live sprint of the research platform "
    "under review by humans and agents alike in every region",                                     # 6
    "R5: ship only admitted capsules. every admitted capsule keeps its suite and its owner forever",  # 7
    "**R3.** gates decide what enters",                                                             # 8
    "",                                                                                             # 9
    "### 2.1 Alita-G grows its own library",                                                        # 10
    "",                                                                                             # 11
    "#### 2.1.3 Deeper detail on growth",                                                           # 12
    "",                                                                                             # 13
    "| Rule | Name |",                                                                              # 14
    "|---|---|",                                                                                    # 15
    "| **R4** | every kept capsule has an owner and a review date |",                               # 16
    "",                                                                                             # 17
    "## References",                                                                                # 18
    "",                                                                                             # 19
    '[1] A. Author, "Paper," arXiv:2501.00001, 2025.',                                              # 20
    "",                                                                                             # 21
    "## Appendix A. Paper details",                                                                 # 22
    "",                                                                                             # 23
    "### A.1 Alita-G",                                                                              # 24
    "",                                                                                             # 25
    "## Appendix B. Inventory",                                                                     # 26
    "",
]


def rc_slides():
    return [
        r4.content("Kumquat vortex", "Capsule report §2.1.3", r4.lines(
            "R1  every sprint pins versions — shown here with the three planner states from Table 4 and the log",
            f"R2  {CAP12} {JUNK}",
            "R5  track kept tools. every admitted capsule keeps its suite and its owner forever",
            "R3  gates decide what enters",
            "R4  every",
            "kept capsule has an owner and a review date")),
        r4.content("Walrus meridian", "Capsule report App. A.1"),
        r4.content("Quartz lantern", "Capsule report Appendix B"),
    ]


@pytest.fixture
def cov(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    def run(slides=None, deck="deck.json"):
        r4.write(tmp_path / "REPORT.md", "\n".join(RC_REPORT))
        r4.write_spec(tmp_path / "deck.json", rc_slides() if slides is None else slides)
        if deck.endswith(".pptx"):
            r4.build_pptx(tmp_path / "deck.json", tmp_path / deck)
        return r4.run_review(report="REPORT.md", deck=deck)
    return run


def test_short_rule_names_and_forms(cov):
    """§16.5: names cut at `;`/` — `/`.`, at most 12 words; `**R3.**`, `| **R4** |`, `R5:` forms are rules;
    C005 compares short names, so only R5 (`ship only admitted capsules` vs `track kept tools`) differs."""
    res = cov()
    assert r4.of(res, "C004") == []
    assert [(f["path"], f["line"]) for f in r4.of(res, "C005")] == [("REPORT.md", 7)]
    assert "R5" in r4.of(res, "C005")[0]["message"]


def test_deeper_section_footer_covers_ancestor(cov):
    """§16.5: `§2.1.3` names an existing level-4 heading: no C003, and 2.1 (and 2) are covered."""
    res = cov()
    assert r4.of(res, "C003") == []
    assert r4.of(res, "C001") == []
    assert {e["section"]: e["slides"] for e in res["outline"]}["2.1"] == ["1"]


def test_missing_deeper_section_is_c003(cov):
    slides = rc_slides()
    slides[0]["source"] = "Capsule report §2.1, §2.1.9"
    assert r4.where(cov(slides), "C003") == [("deck.json", 1)]


def test_appendix_only_slides_are_not_c002(cov):
    """§16.5: `App. A.1` and `Appendix B` footers cover appendices; a footer-less, unmatched slide is C002."""
    slides = rc_slides() + [r4.content("Zebra orbit")]
    assert r4.where(cov(slides), "C002") == [("deck.json", 4)]


def test_pptx_continuation_lines_joined(cov):
    """§16.5: in a built .pptx, `R4  every` + `kept capsule has ...` is 1 rule name (no C005 for R4)."""
    pytest.importorskip("pptx")
    res = cov(deck="deck.pptx")
    assert [f["line"] for f in r4.of(res, "C005")] == [7]
    assert r4.of(res, "C002") == [] and r4.of(res, "C004") == []
