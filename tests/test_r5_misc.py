"""Round 5: changed-line hints (MANIFEST §17.2, on top of §15.4) and review_coverage, diagram png, fignums and
office_check (§17.6, on top of §15.1, §16.5, §4.2, §7.2, §16.7, §0.4)."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_r5 as h  # noqa: E402


@pytest.fixture
def cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


# ------------------------------------------------------------------ changed-line hints (§17.2)
LONG = "Gate every tool before admission by the independent suite"
ITEMS = [LONG, "Budgets cap each run at forty minutes", "Owners review kept capsules monthly"]
BUILD_PY = "ITEMS = [\n" + "".join(f"    {s!r},\n" for s in ITEMS) + "]\n"


def test_deck_diff_hint_from_changed_line(cwd):
    """§17.2 reviewers' repro: the whole old text box is not a literal in build.py, but its changed line is
    (line 3); the hint points there, not at the longest line (line 2)."""
    h.write(cwd / "build.py", BUILD_PY)
    old = h.build(cwd / "old.pptx", [h.lines_slide("Budget rules for every run", ITEMS)])
    h.edit_line(old, cwd / "new.pptx", ITEMS[1], "Budgets cap each run at thirty minutes")
    res = h.deck_diff("old.pptx", "new.pptx", search=["build.py"])
    assert h.hints(res, "text") == [["build.py:3"]]


def test_docx_diff_hint_from_changed_line(cwd):
    """§17.2: a docx paragraph with line breaks; its changed second line is a literal on line 3."""
    h.write(cwd / "build.py", BUILD_PY)
    h.make_docx(cwd / "old.docx", ["Intro.", [ITEMS[0], "\n", ITEMS[1], "\n", ITEMS[2]]])
    h.make_docx(cwd / "new.docx", ["Intro.", [ITEMS[0], "\n", "Budgets cap each run at an hour", "\n", ITEMS[2]]])
    (c,) = h.docx_diff("old.docx", "new.docx", search=["build.py"])["changes"]
    assert [x.replace("\\", "/") for x in c["hint"]] == ["build.py:3"]


def test_whole_string_still_wins(cwd):
    """§17.2: step 1 (the whole old string) comes first and stops the search."""
    h.write(cwd / "a.md", "\n".join(ITEMS) + "\n")
    h.write(cwd / "build.py", BUILD_PY)
    h.make_docx(cwd / "old.docx", [[ITEMS[0], "\n", ITEMS[1], "\n", ITEMS[2]]])
    h.make_docx(cwd / "new.docx", [[ITEMS[0], "\n", "Budgets cap each run at an hour", "\n", ITEMS[2]]])
    (c,) = h.docx_diff("old.docx", "new.docx", search=["a.md", "build.py"])["changes"]
    assert [x.replace("\\", "/") for x in c["hint"]] == ["a.md:1"]


# ------------------------------------------------------------------ review_coverage (§17.6)
def test_alternate_content_shape_rule_is_read(cwd):
    """§17.6 reviewers' repro: an `mc:AlternateContent` shape holding `R9: ...` counts as a deck rule, once."""
    h.need_pptx()
    h.write(cwd / "REPORT.md", "# Capsule Report\n\n## 2. Gates decide what enters\n\n"
                               "R9: every gate runs in under a minute\n")
    deck = h.build(cwd / "deck.pptx", [h.r3.content("Gates decide what enters", source="Capsule report §2")])
    slide_index = len(h.open_deck(deck).slides) - 1
    h.inject_xml(deck, slide_index, h.alternate_content("R9: every gate runs in under a minute"))
    res = h.review(report="REPORT.md", deck="deck.pptx")
    assert h.of(res, "C004") == []
    assert h.of(res, "C005") == []
    assert h.of(res, "C006") == []


def test_rule_name_prefers_table_row(cwd):
    """§17.6: R4 is first mentioned in a requirements bullet list, then defined in the rules table; the table
    name is compared with the deck, so there is no C005."""
    h.write(cwd / "REPORT.md", "\n".join([
        "# Capsule Report", "",
        "## 2. Requirements", "",
        "- R4: the planner never waits for a build to finish before it plans the sprint", "",
        "## 3. Rules", "",
        "| Rule | Name |", "|---|---|",
        "| R4 | Duplicates are rejected; close capsules are versioned |", "",
    ]))
    h.write_spec(cwd / "deck.json", [
        h.r3.content("Requirements", source="Capsule report §2"),
        h.r3.content("Rules", source="Capsule report §3",
                     body={"kind": "lines", "items": ["R4  Duplicates are rejected"]}),
    ])
    res = h.review(report="REPORT.md", deck="deck.json")
    assert h.of(res, "C004") == []
    assert h.of(res, "C005") == []


# ------------------------------------------------------------------ diagram png (§17.6)
def test_png_pointing_at_directory_is_tool_error(tmp_path):
    """§17.6: `png` naming an existing directory is a ToolError; the directory is left alone."""
    target = tmp_path / "figures"
    target.mkdir()
    (target / "keep.txt").write_text("x", encoding="utf-8")
    spec = {"nodes": [{"id": "a", "label": "alpha"}, {"id": "b", "label": "beta"}],
            "edges": [{"from": "a", "to": "b"}]}
    with pytest.raises(h.tool_error()):
        h.call("diagram_render", spec=spec, png=str(target))
    assert target.is_dir()
    assert h.listing(target) == ["keep.txt"]


# ------------------------------------------------------------------ fignums (§17.6)
FIG_REPORT = "# R\n\n*Fig. 1. One.*\n\n*Fig. 1. Again.*\n\nSee Fig. 7 here.\n"


@pytest.mark.skipif(os.name != "nt", reason="Git Bash drive spellings exist only on Windows")
def test_fignums_same_file_two_spellings_reported_once(tmp_path):
    """§17.6: the report is in `paths` as `C:/...` and in `refs` as `/c/...`: 1 file, so F005 appears once."""
    p = h.write(tmp_path / "report.md", FIG_REPORT)
    win = str(p).replace("\\", "/")
    bash = "/" + win[0].lower() + win[2:]
    res = h.call("text_fignums", paths=[win], refs=[bash])
    h.assert_checker_shape(res)
    assert sorted((f["rule"], f["line"]) for f in res["findings"]) == [("F001", 5), ("F005", 7)]


# ------------------------------------------------------------------ office_check (§17.6)
@pytest.fixture
def broken_process_list(monkeypatch):
    import tundlekit.render as render

    def fail(*args, **kwargs):
        raise OSError("tasklist is not available")

    monkeypatch.setattr(render.subprocess, "run", fail)
    monkeypatch.setattr(subprocess, "run", fail)
    return render


def test_office_check_unknown_state(broken_process_list):
    """§17.6: when tasklist/ps fails, office_check reports ok false and an error message."""
    res = h.call("office_check")
    assert res["ok"] is False
    assert isinstance(res["error"], str) and res["error"]


def test_office_check_unknown_state_cli(broken_process_list, capsys):
    """§17.6/§0.4: the CLI exits 1 and the JSON result carries ok false and error."""
    code, data, _, _ = h.run_cli(capsys, ["office", "check", "--json"])
    assert code == 1
    assert data["ok"] is False and data["error"]
