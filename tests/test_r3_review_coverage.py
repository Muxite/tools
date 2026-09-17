"""review_coverage (MANIFEST §15.1, with §14.2 buckets, §14.4 footers, §0.3 findings, §15.10 registration).

Fixtures mimic notes/report-capsules/REPORT.md (numbered `## N.` / `### N.M` headings, design rules
`- R1: ...` and a rules table, `## References`, `## Appendix A.`) and deck-src/build_deck.py footers
such as `Capsule report §2.3, App. A.1 · Alita-G (arXiv 2510.23601) Tables 1 and 6`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_r3rc as r3  # noqa: E402

REPORT_LINES = [
    "# Capability Capsule in AI4Research",                                   # 1
    "",                                                                      # 2
    "This report covers the capsule design, in the order of the talk.",      # 3
    "",                                                                      # 4
    "## 1. The goal: agents that build and keep capabilities",               # 5
    "",                                                                      # 6
    "Capability Capsule declares, admits and selects capabilities.",         # 7
    "",                                                                      # 8
    "### 1.1 MCP is a protocol, not a tool",                                 # 9
    "",                                                                      # 10
    "MCP is a stateless client-server protocol.",                            # 11
    "",                                                                      # 12
    "### 1.2 DeepSeek Harness makes every layer a plugin",                   # 13
    "",                                                                      # 14
    "Every layer is a plugin.",                                              # 15
    "",                                                                      # 16
    "## 2. The evidence and the rules it leads to",                          # 17
    "",                                                                      # 18
    "- R1: capsules are built at the same time as they are used",            # 19
    "- R2: every sprint pins the exact capsule versions it uses",            # 20
    "",                                                                      # 21
    "### 2.1 Alita-G grows its own tool library",                            # 22
    "",                                                                      # 23
    "A self-growing tool library already works.",                            # 24
    "",                                                                      # 25
    "### 2.2 Where Alita-G falls short in research",                         # 26
    "",                                                                      # 27
    "Research runs are longer.",                                             # 28
    "",                                                                      # 29
    "## 3. AI4Research today has hand-written capsules",                     # 30
    "",                                                                      # 31
    "| Rule | Name |",                                                       # 32
    "|---|---|",                                                             # 33
    "| R3 | every capsule passes held-out tests |",                          # 34
    "",                                                                      # 35
    "## References",                                                         # 36
    "",                                                                      # 37
    '[1] Y. Shi, "A programming paradigm," arXiv:2608.25512, 2026.',         # 38
    "",                                                                      # 39
    "## Appendix A. Paper details",                                          # 40
    "",                                                                      # 41
    "### A.1 Alita-G [2]",                                                   # 42
    "",                                                                      # 43
    "### 7.1 Numbered detail inside the appendix",                           # 44
    "",                                                                      # 45
    "Detail.",                                                               # 46
    "",
]
BODY_SECTIONS = {"1", "1.1", "1.2", "2", "2.1", "2.2", "3"}


def base_slides():
    return [
        r3.content("Kumquat vortex", "Capsule report §1, §3",
                   r3.lines("R1  capsules are built at the same time as they are used",
                            "R2  every sprint pins the exact capsule versions it uses")),
        r3.content("Xylophone quartz", "Capsule report §2.1, App. A.1, App. A.2 Table A2"),
        r3.content("Zebra lantern",
                   "Capsule report §2.2 · Alita-G (arXiv 2510.23601) Tables 1 and 6",
                   r3.lines("R3  every capsule passes held-out tests")),
    ]


@pytest.fixture
def cov(tmp_path, monkeypatch):
    """run(slides=None, report_lines=None, cuts=None, **kw) -> result; paths are relative to tmp_path."""
    monkeypatch.chdir(tmp_path)

    def run(slides=None, report_lines=None, cuts=None, **kw):
        r3.write(tmp_path / "REPORT.md", "\n".join(report_lines or REPORT_LINES))
        r3.write_spec(tmp_path / "deck.json", base_slides() if slides is None else slides)
        args = {"report": "REPORT.md", "deck": "deck.json"}
        if cuts is not None:
            r3.write(tmp_path / "cuts.txt", cuts)
            args["cuts"] = "cuts.txt"
        args.update(kw)
        res = r3.review(**args)
        r3.assert_checker_shape(res)
        return res
    return run


def c001_sections(res):
    """{line: finding} for C001 (line is the report heading line)."""
    return sorted(f["line"] for f in r3.of(res, "C001"))


# ------------------------------------------------------------------ result shape and outline

def test_outline_lists_body_sections_and_slide_numbers(cov):
    """§15.1: outline has 1 entry per numbered level-2/3 body heading, with the slides that cover it."""
    res = cov()
    outline = {e["section"]: e for e in res["outline"]}
    assert set(outline) == BODY_SECTIONS                      # pinned: no `§`
    assert outline["2.1"]["slides"] == ["2"]                  # pinned: slide numbers are strings
    assert outline["2.2"]["slides"] == ["3"]
    assert outline["3"]["slides"] == ["1"]
    assert outline["2.1"]["heading"] == "Alita-G grows its own tool library"   # pinned: without its number
    assert outline["1"]["heading"] == "The goal: agents that build and keep capabilities"


def test_slides_list_numbers_titles_and_sections(cov):
    """§15.1: slides = [{number, title, sections}] for the content slides."""
    res = cov()
    slides = res["slides"]
    assert [s["number"] for s in slides] == ["1", "2", "3"]
    assert [s["title"] for s in slides] == ["Kumquat vortex", "Xylophone quartz", "Zebra lantern"]
    assert {"1", "3"} <= set(slides[0]["sections"])
    assert "2.1" in slides[1]["sections"]


def test_appendix_references_and_unnumbered_headings_ignored(cov):
    """§15.1 + §14.2: only numbered headings in the body bucket are sections (`### 7.1` under an appendix is not)."""
    res = cov()
    assert "7.1" not in {e["section"] for e in res["outline"]}
    assert all(f["line"] not in (1, 36, 40, 42, 44) for f in r3.of(res, "C001"))


# ------------------------------------------------------------------ coverage semantics

def test_bare_section_covers_only_level_two(cov):
    """§15.1: a footer `§1` covers section 1 but not 1.1 or 1.2 (C001 warnings on their heading lines)."""
    res = cov()
    found = r3.of(res, "C001")
    assert c001_sections(res) == [9, 13]
    assert all(f["severity"] == "warning" and f["path"] == "REPORT.md" for f in found)
    assert res["ok"] is True


def test_level_two_covered_through_level_three(cov):
    """§15.1: a level-2 section counts as covered when any of its level-3 sections is covered."""
    slides = base_slides()
    slides[0]["source"] = "Capsule report §1.1, §3"
    res = cov(slides)
    assert c001_sections(res) == [13]          # 1 is covered via 1.1; 1.2 is not


def test_subsection_footer_covers_only_that_subsection(cov):
    """§15.1: `§2.1` covers 2.1 only; with the `§2.2` slide gone, 2.2 is reported (2 stays covered via 2.1)."""
    slides = base_slides()[:2]
    res = cov(slides)
    assert c001_sections(res) == [9, 13, 26]


def test_several_sections_in_one_footer(cov):
    """§15.1: `§1, §3` cites both sections."""
    res = cov()
    lines = {f["line"] for f in r3.of(res, "C001")}
    assert 5 not in lines and 30 not in lines


def test_title_similarity_covers_section(cov):
    """§15.1 rule 2: a slide title equal to the heading text (number dropped) covers it, with no footer."""
    slides = base_slides() + [r3.content("MCP is a protocol, not a tool")]
    res = cov(slides)
    assert c001_sections(res) == [13]
    assert r3.of(res, "C002") == []


@pytest.mark.parametrize("threshold, covered", [(0.8, True), (0.81, False)])
def test_threshold_is_inclusive(cov, threshold, covered):
    """§15.1: similarity >= threshold covers. `alpha beta` vs `alpha bexx` has ratio exactly 0.8."""
    lines = REPORT_LINES[:29] + ["### 2.3 alpha beta", ""] + REPORT_LINES[29:]
    slides = base_slides() + [r3.content("alpha bexx")]
    res = cov(slides, report_lines=lines, threshold=threshold)
    c001 = {f["line"] for f in r3.of(res, "C001")}
    c002 = {f["line"] for f in r3.of(res, "C002")}
    assert (30 not in c001) is covered
    assert (4 not in c002) is covered


# ------------------------------------------------------------------ C002, C003, cuts

def test_c002_slide_covering_nothing(cov):
    """§15.1: C002 warning, path = deck, line = slide position (a slide with no footer and no similar heading)."""
    slides = base_slides() + [r3.content("Walrus meridian")]   # §16.5: an App.-only footer is not a C002
    res = cov(slides)
    found = r3.of(res, "C002")
    assert [(f["severity"], f["path"], f["line"]) for f in found] == [("warning", "deck.json", 4)]


def test_c003_footer_naming_missing_section(cov):
    """§15.1 + pinned details: C003 error for `§9` and `§2.9`, reported with the deck path and the slide
    position; ok is false."""
    slides = base_slides()
    slides[1]["source"] = "Capsule report §2.1, §2.9; §9"
    res = cov(slides)
    found = r3.of(res, "C003")
    assert len(found) == 2
    assert [(f["severity"], f["path"], f["line"]) for f in found] == [("error", "deck.json", 2)] * 2
    assert res["ok"] is False
    assert res["counts"]["error"] == 2


def test_no_c003_for_existing_sections_appendices_tables_or_papers(cov):
    """§15.1: the base footers (`App. A.2 Table A2`, `arXiv 2510.23601`, `Tables 1 and 6`) give no C003."""
    res = cov()
    assert r3.of(res, "C003") == []


def test_paper_sections_in_footer_segments_skipped(cov):
    """Pinned details: the real build_deck footer `arXiv 2510.23601 §3.3, Tables 3-5; Capsule report §2.2, Table 1`
    cites §3.3 of the paper (its segment has `arXiv` before the `§`), so there is no C003, and §2.2 is covered."""
    slides = base_slides()
    slides[2]["source"] = "arXiv 2510.23601 §3.3, Tables 3-5; Capsule report §2.2, Table 1"
    res = cov(slides)
    assert r3.of(res, "C003") == []
    assert res["slides"][2]["sections"] == ["2.2"]
    assert c001_sections(res) == [9, 13]
    assert res["ok"] is True


def test_paper_skip_is_per_segment(cov):
    """Pinned details: footers split at `;` and `·`. `§8` (before `arXiv` in its segment) and `§7` (another
    segment) are checked; `§9` (after `arXiv`) is skipped."""
    slides = base_slides()
    slides[2]["source"] = "Capsule report §2.2, §8 · Alita-G (arXiv 2510.23601) §9; §7"
    res = cov(slides)
    assert [(f["path"], f["line"]) for f in r3.of(res, "C003")] == [("deck.json", 3)] * 2


def test_paper_word_skips_segment(cov):
    """Pinned details: the whole word `paper` before a `§` also marks a paper citation; `newspaper` does not."""
    slides = base_slides()
    slides[2]["source"] = "Capsule report §2.2 · the Alita-G paper §5 · newspaper §6"
    res = cov(slides)
    assert [(f["path"], f["line"]) for f in r3.of(res, "C003")] == [("deck.json", 3)]


def test_cuts_file_suppresses_c001_and_c002(cov):
    """§15.1 + pinned details: cuts `§1.1` and `slide 4` suppress those findings; `#` starts a comment anywhere."""
    slides = base_slides() + [r3.content("Walrus meridian")]
    cuts = "# agreed cuts with the reviewer\n§1.1   # cut in review\n\nslide 4  # merged\n# §1.2 stays\n"
    res = cov(slides, cuts=cuts)
    assert c001_sections(res) == [13]
    assert r3.of(res, "C002") == []


# ------------------------------------------------------------------ rules C004-C006

def test_rules_from_lists_and_table_rows_match(cov):
    """§15.1: R1/R2 from list lines and R3 from a table row match the deck's `R<n>  name` lines."""
    res = cov()
    assert r3.of(res, "C004") == []
    assert r3.of(res, "C005") == []
    assert r3.of(res, "C006") == []


def test_c004_rule_in_one_document_only(cov):
    """§15.1 + pinned details: C004 warning for a rule missing from the deck (report path and line) and for one
    missing from the report (deck path and slide position)."""
    slides = base_slides()
    slides[2]["body"] = r3.lines("R8  a rule the report never states")
    res = cov(slides)
    found = r3.of(res, "C004")
    assert sorted((f["severity"], f["path"], f["line"]) for f in found) == [
        ("warning", "REPORT.md", 34), ("warning", "deck.json", 3)]     # R3 from the report's table row
    by_path = {f["path"]: f for f in found}
    assert "R3" in by_path["REPORT.md"]["message"]
    assert "R8" in by_path["deck.json"]["message"]


def test_c005_rule_names_differ(cov):
    """§15.1: C005 info when the first names of a rule have similarity < 0.5."""
    slides = base_slides()
    slides[0]["body"] = r3.lines("R1  capsules are built at the same time as they are used",
                                 "R2  zqk vvv wxy")
    res = cov(slides)
    found = r3.of(res, "C005")
    assert [(f["severity"], f["path"], f["line"]) for f in found] == [("info", "REPORT.md", 20)]
    assert "R2" in found[0]["message"]


def test_c006_rule_on_several_slides(cov):
    """§15.1: C006 info (deck path, slide position) when a rule appears on more than 1 slide; the message lists each slide."""
    slides = base_slides()
    slides[1]["body"] = r3.lines("R1  capsules are built at the same time as they are used")
    res = cov(slides)
    found = r3.of(res, "C006")
    assert len(found) == 1
    f = found[0]
    assert f["severity"] == "info" and f["path"] == "deck.json"
    assert f["line"] in (1, 2)                                   # pinned: a slide position
    assert "R1" in f["message"] and "1" in f["message"] and "2" in f["message"]
    assert res["ok"] is True


# ------------------------------------------------------------------ pptx input

def test_pptx_deck_matches_spec(tmp_path, monkeypatch):
    """§15.1 with §3.3/§14.4: a built .pptx gives the same slides, footers and C001 findings as its spec."""
    pytest.importorskip("pptx")
    monkeypatch.chdir(tmp_path)
    r3.write(tmp_path / "REPORT.md", "\n".join(REPORT_LINES))
    r3.write_spec(tmp_path / "deck.json", base_slides())
    r3.build_pptx(tmp_path / "deck.json", tmp_path / "deck.pptx")
    res = r3.review(report="REPORT.md", deck="deck.pptx")
    r3.assert_checker_shape(res)
    assert [s["number"] for s in res["slides"]] == ["1", "2", "3"]
    assert [s["title"] for s in res["slides"]] == ["Kumquat vortex", "Xylophone quartz", "Zebra lantern"]
    assert c001_sections(res) == [9, 13]
    assert r3.of(res, "C002") == [] and r3.of(res, "C004") == []


def test_pptx_bullet_rules(tmp_path, monkeypatch):
    """Pinned details: in a built .pptx, bullets read `•  R1 ...`; those lines are rules too."""
    pytest.importorskip("pptx")
    monkeypatch.chdir(tmp_path)
    slides = base_slides()
    slides[0]["body"] = {"kind": "bullets", "items": [
        "R1  capsules are built at the same time as they are used",
        "R2  every sprint pins the exact capsule versions it uses"]}
    r3.write(tmp_path / "REPORT.md", "\n".join(REPORT_LINES))
    r3.write_spec(tmp_path / "deck.json", slides)
    r3.build_pptx(tmp_path / "deck.json", tmp_path / "deck.pptx")
    res = r3.review(report="REPORT.md", deck="deck.pptx")
    r3.assert_checker_shape(res)
    assert r3.of(res, "C004") == [] and r3.of(res, "C005") == []


def test_report_rules_only_from_body_bucket(cov):
    """Pinned details: a rule line under the appendix is not a report rule, so the deck's R9 is deck-only."""
    slides = base_slides()
    slides[1]["body"] = r3.lines("R9  appendix-only rule")
    lines = REPORT_LINES[:-1] + ["- R9: appendix-only rule", ""]
    res = cov(slides, report_lines=lines)
    assert [(f["path"], f["line"]) for f in r3.of(res, "C004")] == [("deck.json", 2)]


# ------------------------------------------------------------------ CLI and registration

def test_cli_json_with_cuts_and_threshold(tmp_path, monkeypatch, capsys):
    """§15.1/§0.4: `tundlekit review coverage REPORT DECK --cuts F --threshold X --json`; warnings exit 0."""
    monkeypatch.chdir(tmp_path)
    r3.write(tmp_path / "REPORT.md", "\n".join(REPORT_LINES))
    r3.write_spec(tmp_path / "deck.json", base_slides())
    r3.write(tmp_path / "cuts.txt", "§1.2\n")
    code, data, _, _ = r3.run_cli(capsys, ["review", "coverage", "REPORT.md", "deck.json",
                                           "--cuts", "cuts.txt", "--threshold", "0.9", "--json"])
    assert code == 0
    assert [f["line"] for f in data["findings"] if f["rule"] == "C001"] == [9]
    code, _, _, _ = r3.run_cli(capsys, ["review", "coverage", "REPORT.md", "deck.json", "--strict", "--json"])
    assert code == 1


def test_cli_exit_1_on_c003(tmp_path, monkeypatch, capsys):
    """§0.4: an error finding (C003) exits 1."""
    monkeypatch.chdir(tmp_path)
    slides = base_slides()
    slides[0]["source"] = "Capsule report §1, §3, §8"
    r3.write(tmp_path / "REPORT.md", "\n".join(REPORT_LINES))
    r3.write_spec(tmp_path / "deck.json", slides)
    code, data, _, _ = r3.run_cli(capsys, ["review", "coverage", "REPORT.md", "deck.json", "--json"])
    assert code == 1
    assert data["ok"] is False


def test_registration_review_module():
    """§15.10: `review` follows `textlint` in MODULES; review_coverage is registered, read-only, strict schema."""
    from tundlekit import MODULES

    i = MODULES.index("textlint")
    assert MODULES[i + 1] == "review"
    t = r3.get_tool("review", "review_coverage")
    assert t.annotations.get("readOnlyHint") is True
    assert t.input_schema["type"] == "object"
    assert t.input_schema.get("additionalProperties") is False
    assert {"report", "deck", "cuts", "threshold"} <= set(t.input_schema["properties"])
    assert set(t.input_schema.get("required", [])) == {"report", "deck"}
    assert 0 < len(t.description) <= 1024
    assert t.func.__module__ == "tundlekit.review"
