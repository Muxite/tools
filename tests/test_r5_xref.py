"""Round 5: text_xref slice sources, end markers, other-report skip, renumber scope and the appendix cascade
(MANIFEST §17.2, on top of §15.2, §16.5, §0.3, §0.4)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_r5 as h  # noqa: E402

GEN = "notes/report-general/REPORT.md"
BUILD = "notes/report-general/build/build.py"


@pytest.fixture
def cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


# ------------------------------------------------------------------ X001 against the slice source
def test_x001_checked_against_resolved_slice_source(cwd):
    """§17.2: build.py's default slice source (REPORT-annotated.md) resolves, so its references are checked
    against that file; a Markdown file paired with the same report is still checked against the report."""
    h.write(cwd / GEN, "# General Report\n\n## 2. Old\n\n### 2.1 Old detail\n")
    h.write(cwd / "notes/report-general/REPORT-annotated.md",
            "# General Report\n\n## 5. New\n\n### 5.1 New detail\n")
    h.write(cwd / BUILD, "\n".join([
        "import pathlib",                                                             # 1
        "HERE = pathlib.Path(__file__).parent",                                       # 2
        'REPORT = (HERE.parent / "REPORT-annotated.md").read_text(encoding="utf-8")',  # 3
        "",                                                                           # 4
        "def between(start, end, src=REPORT):",                                       # 5
        "    return src",                                                             # 6
        "",                                                                           # 7
        'A = "Source: General report §5.1"',                                          # 8
        'B = "Source: General report §2.1"',                                          # 9
        "",
    ]))
    h.write(cwd / "pack.md", "Slide 3: General report §5.1\nSlide 4: General report §2.1\n")
    res = h.xref(files=[f"{BUILD}={GEN}", f"pack.md={GEN}"])
    assert h.where(res, "X001") == [(BUILD, 9), ("pack.md", 1)]


# ------------------------------------------------------------------ X002 end markers
END_REPORT = "\n".join([
    "# General Report",                                    # 1
    "",                                                    # 2
    "## 3. Evaluation",                                    # 3
    "",                                                    # 4
    "There are two limitations of the pilot.",             # 5
    "Only before the section.",                            # 6
    "",                                                    # 7
    "## 4. Design",                                        # 8
    "",                                                    # 9
    "### 4.2 Count repeats per sprint",                    # 10
    "",                                                    # 11
    "There are two limitations here too.",                 # 12
    "",
])
END_PY = "\n".join([
    "def between(start, end):",                                          # 1
    "    return start",                                                  # 2
    "",                                                                  # 3
    'A = between("### 4.2 Count", "There are two limitations")',         # 4
    'B = between("### 4.2 Count", "Only before the section")',           # 5
    'C = between("There are two limitations", "### 4.2 Count")',         # 6
    "",
])


def test_end_marker_needs_one_occurrence_after_start(cwd):
    """§17.2 reviewers' repro: the end marker "There are two limitations" occurs twice, once after the start
    marker: no X002 (line 4). An end marker only before the start (line 5) and a repeated start (line 6) are."""
    h.write(cwd / "REPORT.md", END_REPORT)
    h.write(cwd / "slices.py", END_PY)
    res = h.xref(report="REPORT.md", files=["slices.py"])
    assert h.where(res, "X002") == [("slices.py", 5), ("slices.py", 6)]


# ------------------------------------------------------------------ other-report skip
def test_other_report_skip_limited_to_same_clause(cwd):
    """§17.2: `our final report §4.2` is checked (`final` is never a name), `capsule report §4.2` is skipped,
    a `;` ends the clause, and `this`/`the` are never names."""
    h.write(cwd / GEN, "# General Report\n\n## 3. Evaluation\n\n### 3.5 Only general\n\n## 4. Later\n")
    h.write(cwd / "notes.md", "\n".join([
        "As our final report §4.2 says.",               # 1  checked
        "As the capsule report §4.2 says.",             # 2  skipped
        "See the capsule report; §4.2 is ours.",        # 3  checked
        "As this report §4.2 says.",                    # 4  checked
        "As the report §4.2 says.",                     # 5  checked
        "As the general report §3.5 says.",             # 6  own name, resolves
        "",
    ]))
    res = h.xref(files=[f"notes.md={GEN}"])
    assert h.where(res, "X001") == [("notes.md", 1), ("notes.md", 3), ("notes.md", 4), ("notes.md", 5)]


# ------------------------------------------------------------------ renumber scope
ALPHA = "# Alpha Report\n\n## 4. Design\n\n### 4.2 Gates decide\n"
BETA = "# Beta Report\n\n## 3. Evaluation\n\n### 3.1 Runs\n"
BETA_42 = BETA + "\n## 4. Later\n\n### 4.2 Other gates\n"


def _two_reports(cwd, beta):
    h.write(cwd / "alpha/REPORT.md", ALPHA)
    h.write(cwd / "beta/REPORT.md", beta)
    h.write(cwd / "deck-a.md", "Alpha slide cites §4.2.\n")
    h.write(cwd / "deck-b.md", "Beta slide cites §3.1 and §4.2.\n")
    return ["deck-a.md=alpha/REPORT.md", "deck-b.md=beta/REPORT.md"]


def test_renumber_applies_only_to_report_holding_the_target(cwd):
    """§17.2: `§4.2=§4.3` changes alpha and its paired file; beta's file keeps its (broken) `§4.2`."""
    files = _two_reports(cwd, BETA)
    res = h.xref(files=files, renumber=["§4.2=§4.3"], write=True)
    assert sorted((e["path"], e["line"]) for e in res["edits"]) == [("alpha/REPORT.md", 5), ("deck-a.md", 1)]
    assert h.read(cwd / "deck-a.md") == "Alpha slide cites §4.3.\n"
    assert h.read(cwd / "deck-b.md") == "Beta slide cites §3.1 and §4.2.\n"
    assert "### 4.3 Gates decide" in h.read(cwd / "alpha/REPORT.md")


def test_renumber_ambiguous_across_reports_is_tool_error(cwd):
    """§17.2: both reports hold §4.2: a ToolError naming both, and nothing is written."""
    files = _two_reports(cwd, BETA_42)
    with pytest.raises(h.tool_error()) as exc:
        h.xref(files=files, renumber=["§4.2=§4.3"], write=True)
    msg = str(exc.value).replace("\\", "/")
    assert "alpha/REPORT.md" in msg and "beta/REPORT.md" in msg
    assert h.read(cwd / "deck-a.md") == "Alpha slide cites §4.2.\n"


def test_renumber_report_selects_one(cwd):
    """§17.2: `renumber_report` picks beta; alpha and its file stay as they are."""
    files = _two_reports(cwd, BETA_42)
    h.xref(files=files, renumber=["§4.2=§4.3"], renumber_report="beta/REPORT.md", write=True)
    assert h.read(cwd / "deck-a.md") == "Alpha slide cites §4.2.\n"
    assert h.read(cwd / "alpha/REPORT.md") == ALPHA
    assert h.read(cwd / "deck-b.md") == "Beta slide cites §3.1 and §4.3.\n"
    assert "### 4.3 Other gates" in h.read(cwd / "beta/REPORT.md")


def test_cli_renumber_report(cwd, capsys):
    """§17.2/§0.4: `--renumber-report REPORT`."""
    files = _two_reports(cwd, BETA_42)
    code, data, _, err = h.run_cli(capsys, ["text", "xref", "--in", *files, "--renumber", "§4.2=§4.3",
                                            "--renumber-report", "alpha/REPORT.md", "--json"])
    assert data is not None and "edits" in data, (code, err)
    assert sorted(e["path"] for e in data["edits"]) == ["alpha/REPORT.md", "deck-a.md"]


# ------------------------------------------------------------------ appendix cascade
CASCADE = "\n".join([
    "# Capsule Report",                                                    # 1
    "",                                                                    # 2
    "## 1. Introduction",                                                  # 3
    "",                                                                    # 4
    "See App. E.4, Appendix E, Table E4, Fig. E1 and Figure E1; the E4 variant is unrelated.",  # 5
    "",                                                                    # 6
    "## Appendix E. Extra runs",                                           # 7
    "",                                                                    # 8
    "### E.4 Detail",                                                      # 9
    "",                                                                    # 10
    "*Table E4. Extra numbers.*",                                          # 11
    "",                                                                    # 12
    "*Fig. E1. Extra chart.*",                                             # 13
    "",
])
CASCADE_D = CASCADE.replace("App. E.4, Appendix E, Table E4, Fig. E1 and Figure E1",
                            "App. D.4, Appendix D, Table D4, Fig. D1 and Figure D1") \
    .replace("## Appendix E.", "## Appendix D.").replace("### E.4", "### D.4") \
    .replace("*Table E4.", "*Table D4.").replace("*Fig. E1.", "*Fig. D1.")
FOOTERS = ('SOURCE = "Capsule report App. E.4, Appendix E.4, App. E"\n'
           'CAPTION = "Table E4 · Fig. E1 · Figure E1"\n')


def test_appendix_cascade_renames_every_form(cwd):
    """§17.2 reviewers' repro: `App. E=App. D` renames the heading, `### E.4`, `App. E.4`, `Appendix E.4`,
    `Table E4`, `Fig. E1` and `Figure E1` in the report and the paired footers, keeping each spelling."""
    h.write(cwd / "REPORT.md", CASCADE)
    h.write(cwd / "footers.py", FOOTERS)
    h.xref(files=["footers.py=REPORT.md"], renumber=["App. E=App. D"], write=True)
    assert h.read(cwd / "REPORT.md") == CASCADE_D
    assert h.read(cwd / "footers.py") == ('SOURCE = "Capsule report App. D.4, Appendix D.4, App. D"\n'
                                          'CAPTION = "Table D4 · Fig. D1 · Figure D1"\n')


def test_appendix_cascade_refuses_existing_letter_unless_swapped(cwd):
    """§17.2: D already exists: `App. E=App. D` alone is a ToolError; the swap is allowed."""
    report = CASCADE.replace("## Appendix E. Extra runs", "## Appendix D. Setup\n\n### D.1 Machines\n\n"
                                                          "## Appendix E. Extra runs")
    h.write(cwd / "REPORT.md", report)
    h.write(cwd / "footers.py", FOOTERS)
    with pytest.raises(h.tool_error()):
        h.xref(files=["footers.py=REPORT.md"], renumber=["App. E=App. D"], write=True)
    assert h.read(cwd / "REPORT.md") == report
    h.xref(files=["footers.py=REPORT.md"], renumber=["App. E=App. D", "App. D=App. E"], write=True)
    text = h.read(cwd / "REPORT.md")
    assert "## Appendix E. Setup" in text and "### E.1 Machines" in text
    assert "## Appendix D. Extra runs" in text and "### D.4 Detail" in text
