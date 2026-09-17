"""claims_trace round 4 (MANIFEST §16.4, on top of §15.3, §0.3, §0.4).

Fixtures model notes/report-capsules/REPORT.md (`[2, Table 6]` locators, `Section 2.1` prose, appendix tables
whose caption cites a paper) and notes/report-general/REPORT.md (`Kosmos (2511.02824) ... (p2, p4)` and the
Table A1 rows that pair a name with an id), with small `===== page N =====` papers.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_r4c as r4  # noqa: E402

CAPSULE = [
    "# Capability Capsule in AI4Research",                                                         # 1
    "",                                                                                            # 2
    "## 2. The evidence",                                                                          # 3
    "",                                                                                            # 4
    "On the 165-question GAIA validation set, Alita-G reports 83.03% pass@1 with its library. "
    "The gain over 75.15% is 7.88 points [2, Table 2].",                                           # 5
    "",                                                                                            # 6
    "Changing the threshold moves accuracy by 16 points on 25 questions [2, Table 6].",            # 7
    "",                                                                                            # 8
    "The library holds 128 tools [2, Table 6].",                                                   # 9
    "",                                                                                            # 10
    "The share of distinct tools falls to 50% at the end [2].",                                    # 11
    "",                                                                                            # 12
    "Every one of 1024 runs was logged, and 3048 were replayed [3].",                              # 13
    "",                                                                                            # 14
    "An uncited paragraph mentions 4242 runs.",                                                    # 15
    "",                                                                                            # 16
    "Section 12, Sec. 14, Eq. 15, Equation 16, Step 22, Phase 23, Level 44 and R16 repeat 83.03% [2].",  # 17
    "",                                                                                            # 18
    "10. Alita-G stays at 83.03% [2].",                                                            # 19
    "",                                                                                            # 20
    "## References",                                                                               # 21
    "",                                                                                            # 22
    '- [2] J. Qiu et al., "Alita-G," arXiv:2510.23601, Oct. 2025.',                                # 23
    "",                                                                                            # 24
    '- [3] A. Kaliyev, "Beyond task completion," arXiv:2604.00392v2, Jul. 2026.',                  # 25
    "",                                                                                            # 26
    "## Appendix A. Paper details",                                                                # 27
    "",                                                                                            # 28
    "### A.1 Alita-G [2]",                                                                         # 29
    "",                                                                                            # 30
    "| Setting | Accuracy |",                                                                      # 31
    "|---|---|",                                                                                   # 32
    "| With library | 83.03% |",                                                                   # 33
    "| Without library | 75.15% |",                                                              # 34
    "",                                                                                            # 35
    "*Table A2. Alita-G results on GAIA [2, Table 2].*",                                           # 36
    "",                                                                                            # 37
    "| Setting | Count |",                                                                         # 38
    "|---|---|",                                                                                   # 39
    "| Uncited appendix table | 606 |",                                                            # 40
    "",                                                                                            # 41
    "*Table A3. An uncited appendix table.*",                                                      # 42
    "",                                                                                            # 43
    "Appendix prose repeats 83.03% [2].",                                                          # 44
    "",
]

GENERAL = [
    "# AI4Research General Report",                                                                # 1
    "",                                                                                            # 2
    "## 4. The state of the art",                                                                  # 3
    "",                                                                                            # 4
    "### 4.2 Kosmos",                                                                              # 5
    "",                                                                                            # 6
    "Kosmos (2511.02824) is built for scale. Experts rated 79.4% of 102 statements accurate, "
    "including 85.5% of data-analysis statements (p2, p4).",                                       # 7
    "Synthesis statements were rated accurate 57.9% of the time (p4).",                            # 8
    "",                                                                                            # 9
    "### 4.3 Arbor",                                                                               # 10
    "",                                                                                            # 11
    "On Terminal-Bench, Arbor scores 77.36 held out against 71.70 for Claude Code (p8).",          # 12
    "",                                                                                            # 13
    "Arbor also ran 300 merges (p. 3).",                                                           # 14
    "",                                                                                            # 15
    "## Appendix A. Sources",                                                                      # 16
    "",                                                                                            # 17
    "| Role | Source | Used for |",                                                                # 18
    "|---|---|---|",                                                                               # 19
    "| Reference system | 2511.02824 Kosmos | Scale; 79.4% statement accuracy |",                  # 20
    "| Reference system | 2606.11926 Arbor | Held-out merge gate; 77.36 against 71.70 |",          # 21
    "",                                                                                            # 22
    "*Table A1. The sources read in full, and what each is used for.*",                            # 23
    "",
]


@pytest.fixture
def ws(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    r4.write_paper(tmp_path / "papers", "2510.23601", [
        "We use the GAIA validation set of 165 questions and 16 threshold settings.",
        "Table 2: Alita-G reaches 83.03% pass@1, against 75.15% without the library, a gain of 7.88 points.",
        "The distinct ratio falls to 0.50 once the library holds 128 tools.",
        "Table 6: accuracy moves by 16 points on 25 questions.",
    ])
    r4.write_paper(tmp_path / "papers", "2604.00392",
                   ["We logged 1024 runs and replayed 3048."] * 4 + ["Again 1024 runs.", "No numbers."])
    r4.write_paper(tmp_path / "papers", "2511.02824", r4.pages(
        "Kosmos runs up to 10 parallel tasks per cycle.",
        "Experts rated 79.4% of 102 statements as accurate, including 85.5% of data-analysis statements.",
        None,
        "Synthesis statements were accurate 57.9% of the time.",
    ))
    r4.write_paper(tmp_path / "papers", "2606.11926", r4.pages(
        None, None, None, None, None, "The coordinator performed 300 merges.", None,
        "Held-out scores: Claude Code 71.70, Arbor 77.36.",
    ))
    r4.write(tmp_path / "CAPSULE.md", "\n".join(CAPSULE))
    r4.write(tmp_path / "GENERAL.md", "\n".join(GENERAL))
    return tmp_path


@pytest.fixture
def cap(ws):
    return r4.by_key(r4.trace("CAPSULE.md"))


@pytest.fixture
def gen(ws):
    return r4.by_key(r4.trace("GENERAL.md"))


# ------------------------------------------------------------------ [n] reports
def test_dash_reference_entries_resolve(cap):
    """§16.4: `- [n] ... arXiv:ID` entries map [n] to the id (version suffix stripped, §15.3)."""
    assert cap[("CAPSULE.md", 5, "7.88")]["papers"] == ["2510.23601"]
    assert cap[("CAPSULE.md", 13, "1024")]["papers"] == ["2604.00392"]


def test_paragraph_scope_for_uncited_sentence(cap):
    """§16.4 scope: sentence 1 of line 5 has no citation, so it uses the paragraph's [2]."""
    for n, pages in (("165", [1]), ("83.03%", [2])):
        c = cap[("CAPSULE.md", 5, n)]
        assert c["status"] == "located" and sorted(c["pages"]) == pages
        assert c["citations"] == [2]


def test_uncited_paragraph_has_no_claims(ws):
    """§16.4 scope: a paragraph with no citation at all still yields nothing."""
    assert r4.numbers_at(r4.trace("CAPSULE.md"), 15) == set()


def test_exclusion_words_rule_ids_and_list_markers(ws):
    """§16.4 exclusions: numbers after Section/Sec./Eq./Equation/Step/Phase/Level/R, and list markers."""
    res = r4.trace("CAPSULE.md")
    assert r4.numbers_at(res, 17) == {"83.03%"}
    assert r4.numbers_at(res, 19) == {"83.03%"}


def test_percent_matches_decimal_with_trailing_zero(cap):
    """§16.4 percentages: `50%` is located by `0.50` on page 3."""
    c = cap[("CAPSULE.md", 11, "50%")]
    assert c["status"] == "located" and c["pages"] == [3]
    assert not r4.is_weak(c)


def test_weak_integer_with_table_locator(cap):
    """§16.4: 16 and 25 are weak but page 4 holds `Table 6` (locator_match); 128 is only on page 3."""
    for n in ("16", "25"):
        c = cap[("CAPSULE.md", 7, n)]
        assert c["status"] == "located" and r4.is_weak(c) and r4.is_locator_match(c), n
    c = cap[("CAPSULE.md", 9, "128")]
    assert c["status"] == "located" and r4.is_weak(c) and not r4.is_locator_match(c)
    assert sorted(cap[("CAPSULE.md", 7, "16")]["pages"]) == [1, 4]


def test_weak_on_five_pages_only(cap):
    """§16.4: 1024 (≥ 1000) matches on 5 pages, so it is weak; 3048 matches on 4 pages and is not."""
    assert r4.is_weak(cap[("CAPSULE.md", 13, "1024")])
    assert sorted(cap[("CAPSULE.md", 13, "1024")]["pages"]) == [1, 2, 3, 4, 5]
    assert not r4.is_weak(cap[("CAPSULE.md", 13, "3048")])


def test_decimals_and_percentages_on_one_page_not_weak(cap):
    """§16.4: weak needs an integer below 1000 without `%` or 5+ pages."""
    assert not r4.is_weak(cap[("CAPSULE.md", 5, "7.88")])
    assert not r4.is_weak(cap[("CAPSULE.md", 5, "83.03%")])


def test_t003_for_weak_without_locator_match(ws):
    """§16.4: T003 (info) for 165 (line 5), 128 (line 9) and 1024 (line 13); not for 16/25 (line 7)."""
    res = r4.trace("CAPSULE.md")
    t3 = r4.of(res, "T003")
    assert sorted(f["line"] for f in t3) == [5, 9, 13]
    assert {(f["severity"], f["path"]) for f in t3} == {("info", "CAPSULE.md")}
    assert res["ok"] is True


def test_appendix_table_rows_with_citing_caption(cap):
    """§16.4 scope: rows of a table whose caption cites [2] are checked; an uncited table and appendix prose
    are not."""
    assert cap[("CAPSULE.md", 33, "83.03%")]["status"] == "located"
    assert cap[("CAPSULE.md", 34, "75.15%")]["pages"] == [2]
    assert not any(line in (40, 44) for (_, line, _) in cap)


# ------------------------------------------------------------------ name + (pN) reports
def test_name_with_id_and_page_locator(gen):
    """§16.4 citation styles: `Kosmos (2511.02824) ... (p2, p4)` makes the paragraph's numbers claims."""
    got = {n: c for (_, line, n), c in gen.items() if line == 7}
    assert set(got) == {"79.4%", "102", "85.5%"}          # the id itself is not a number
    for c in got.values():
        assert c["status"] == "located" and c["papers"] == ["2511.02824"]
        assert sorted(c["stated_pages"]) == [2, 4]


def test_second_sentence_own_locator(gen):
    """§16.4: 57.9% (line 8, `(p4)`) uses the paragraph's paper and is located on its stated page."""
    c = gen[("GENERAL.md", 8, "57.9%")]
    assert c["status"] == "located" and c["pages"] == [4]
    assert c["papers"] == ["2511.02824"]
    assert 4 in c["stated_pages"]


def test_stated_page_makes_weak_integer_a_locator_match(ws):
    """§16.4: 102 is weak but located on its stated page 2, so no T003 for line 7."""
    res = r4.trace("GENERAL.md")
    c = r4.by_key(res)[("GENERAL.md", 7, "102")]
    assert r4.is_weak(c) and r4.is_locator_match(c)
    assert 7 not in [f["line"] for f in r4.of(res, "T003")]


def test_name_resolved_through_report_table_row(gen):
    """§16.4: `Arbor ... (p8)` has no id in its paragraph; Table A1 pairs Arbor with 2606.11926."""
    for n in ("77.36", "71.70"):
        c = gen[("GENERAL.md", 12, n)]
        assert c["papers"] == ["2606.11926"]
        assert c["status"] == "located" and c["pages"] == [8]
        assert c["stated_pages"] == [8]
        assert not r4.is_weak(c)


def test_p_dot_locator_mismatch_gives_t003(ws):
    """§16.4: `(p. 3)` states page 3, but 300 (weak) is only on page 6: T003 at line 14."""
    res = r4.trace("GENERAL.md")
    c = r4.by_key(res)[("GENERAL.md", 14, "300")]
    assert c["status"] == "located" and c["pages"] == [6] and c["stated_pages"] == [3]
    assert not r4.is_locator_match(c)
    assert [(f["line"], f["severity"]) for f in r4.of(res, "T003")] == [(14, "info")]


def test_uncited_source_table_rows_are_not_claims(gen):
    """§16.4: Table A1's caption cites no paper, so its rows (lines 20-21) are not claims."""
    assert not any(line >= 16 for (_, line, _) in gen)


# ------------------------------------------------------------------ T004
def test_t004_when_no_claims(ws):
    """§16.4: 0 claims gives a T004 warning and ok stays true."""
    r4.write(ws / "EMPTY.md", "# R\n\n## 1. Intro\n\nKosmos ran 200 cycles, uncited.\n")
    res = r4.trace("EMPTY.md")
    assert res["claims"] == []
    t4 = r4.of(res, "T004")
    assert len(t4) == 1 and t4[0]["severity"] == "warning"
    assert res["ok"] is True
    assert set(res["summary"]) == {"located", "derived", "ledgered", "untraced", "no_source"}


def test_t004_for_name_and_id_without_locator(ws):
    """§16.4: a name with its id but no page locator is not a citation style, so still T004."""
    r4.write(ws / "NOLOC.md", "# R\n\n## 1. Intro\n\nKosmos (2511.02824) rated 79.4% of 102 statements.\n")
    res = r4.trace("NOLOC.md")
    assert res["claims"] == [] and len(r4.of(res, "T004")) == 1


def test_no_t004_when_claims_exist(ws):
    assert r4.of(r4.trace("CAPSULE.md"), "T004") == []


def test_cli_t004_warning_exit_codes(ws, capsys):
    """§0.4 with §16.4: T004 alone exits 0; `--strict` makes the warning exit 1."""
    r4.write(ws / "EMPTY.md", "# R\n\nNothing cited.\n")
    code, data, _, _ = r4.run_cli(capsys, ["claims", "trace", "EMPTY.md", "--papers", "papers", "--json"])
    assert code == 0 and [f["rule"] for f in data["findings"]] == ["T004"]
    code, _, _, _ = r4.run_cli(capsys, ["claims", "trace", "EMPTY.md", "--papers", "papers", "--strict", "--json"])
    assert code == 1
