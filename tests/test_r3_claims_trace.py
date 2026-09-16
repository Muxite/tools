"""claims_trace (MANIFEST §15.3, with §7.1 sentences, §14.2 buckets, §9 text formats, §0.3, §15.10).

Fixtures mimic notes/report-capsules/REPORT.md (`[n] ... arXiv:ID` references, version suffixes, citations
such as `[6, App. E]`), papers/*.txt (`===== page N =====` markers, or pdftotext form feeds) and
notes/LEDGER-VERIFIED-NUMBERS.md (numbered Markdown tables of verified values).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_r3rc as r3  # noqa: E402

REPORT = [
    "# Capability Capsule in AI4Research",                                                    # 1
    "",                                                                                       # 2
    "## 1. The evidence",                                                                     # 3
    "",                                                                                       # 4
    "Alita-G reaches 83.03% accuracy on GAIA validation with 165 questions [2].",             # 5
    "In 2025, 3 agents built 222 tools, and 96.8% of them fail held-out tests [3].",          # 6
    "The distinct share of tools falls to 51% as the library grows [2].",                     # 7
    "Section §12 and Fig. 14 and Table 15 describe 4242 runs [2, Table 16].",                 # 8
    "CoEvoSkills lifts pass rates from 41% to 71% [4].",                                      # 9
    "A detector-scored DGM version reached 1,124.7 points [5].",                              # 10
    "The census found 606 passing tests [2].",                                                # 11
    "Mean routing candidates are 2.75 per role [2].",                                         # 12
    "No citation here, although 777 is a number.",                                            # 13
    "The survey reports 314 systems [7].",                                                    # 14
    "An unknown entry reports 315 systems [9].",                                              # 15
    "Both papers report 1024 runs [2, 3].",                                                   # 16
    "",                                                                                       # 17
    "## References",                                                                          # 18
    "",                                                                                       # 19
    '[2] J. Qiu et al., "Alita-G: Self-evolving generative agent," arXiv:2510.23601, Oct. 2025.',  # 20
    "",                                                                                       # 21
    '[3] A. Kaliyev and A. Maryanskyy, "Beyond task completion," arXiv:2604.00392v2, Jul. 2026.',  # 22
    "",                                                                                       # 23
    '[4] H. Zhang et al., "CoEvoSkills," in Proc. COLM, 2026, arXiv 2604.01687.',             # 24
    "",                                                                                       # 25
    '[5] J. Zhang et al., "Darwin Godel Machine," in Proc. ICLR, 2026, arXiv:2505.22954.',    # 26
    "",                                                                                       # 27
    '[7] A. Author, "A survey without a preprint," J. Example, vol. 12, 2024.',               # 28
    "",                                                                                       # 29
    "## Appendix A. Paper details",                                                           # 30
    "",                                                                                       # 31
    "Appendix numbers such as 888 are not claims [2].",                                       # 32
    "",
]

LEDGER = "\n".join([
    "# Verified Numbers Ledger",
    "",
    "Rule: no bare number such as 4242 appears unless it has a row here.",
    "",
    "| # | Quantity | Value | Trap |",
    "|---|---|---|---|",
    "| 6 | Mean routing candidates | **2.75** | derived: 121 candidates / 44 roles |",
    "| 13 | Regression suite | 606 passed / 34 failed | none |",
    "| 14 | Unrelated | 42420 | none |",
    "| 15 | Alita-G accuracy | 83.03% | none |",
    "| 16 | Survey size | 314 | none |",
    "",
])

EXPECTED = {  # (line, number) -> (status, pages)
    (5, "83.03%"): ("located", [2]),
    (5, "165"): ("located", [1, 3]),
    (6, "222"): ("located", [1]),
    (6, "96.8%"): ("located", [2]),
    (7, "51%"): ("located", [3]),
    (8, "4242"): ("untraced", []),
    (9, "41%"): ("located", [1]),
    (9, "71%"): ("located", [1]),
    (10, "1,124.7"): ("located", [1]),
    (11, "606"): ("ledgered", None),
    (12, "2.75"): ("derived", None),
    (14, "314"): ("ledgered", None),
    (15, "315"): ("no_source", None),
    (16, "1024"): ("located", [2]),
}


def key(c):
    """Pinned details: `number` is the token as written (commas kept, no sign)."""
    return (c["line"], c["number"])


@pytest.fixture
def trace(tmp_path, monkeypatch):
    """Writes the report, papers and ledger; run(ledger=True, report=REPORT, **kw) -> result."""
    monkeypatch.chdir(tmp_path)
    papers = tmp_path / "papers"
    r3.write_paper(papers, "2510.23601", [
        "We evaluate on the GAIA validation set of 165 questions.",
        "Alita-G reaches 83.03% average accuracy.",
        "The distinct ratio is 0.51 at the end,\nstill over 165 questions.",
    ])
    r3.write_paper_ff(papers, "2604.00392", [
        "We study 222 kept tools.",
        "Of these, 96.8 percent fail, over 1,024 runs.",
    ])
    r3.write_paper(papers, "2604.01687", ["The pass rate rises from 0.41 to 0.71."])
    r3.write_paper(papers, "2505.22954", ["The detector-scored version reached 1124.7 points."])
    r3.write(tmp_path / "LEDGER.md", LEDGER)

    def run(ledger=True, report=REPORT, **kw):
        r3.write(tmp_path / "REPORT.md", "\n".join(report))
        args = {"report": "REPORT.md", "papers": "papers"}
        if ledger:
            args["ledger"] = "LEDGER.md"
        args.update(kw)
        res = r3.claims(**args)
        r3.assert_checker_shape(res)
        return res
    return run


def by_key(res):
    return {key(c): c for c in res["claims"]}


# ------------------------------------------------------------------ claims and statuses

def test_claims_and_statuses(trace):
    """§15.3: exactly 1 entry per (sentence, number) with the expected status."""
    res = trace()
    got = by_key(res)
    assert set(got) == set(EXPECTED)
    assert {k: c["status"] for k, c in got.items()} == {k: v[0] for k, v in EXPECTED.items()}
    for c in res["claims"]:
        assert set(c) >= {"path", "line", "number", "citations", "papers", "status", "pages"}
        assert c["path"] == "REPORT.md"


def test_located_pages_marker_format(trace):
    """§15.3: pages are the 1-based pages (from `===== page N =====`) where the number was found."""
    got = by_key(trace())
    for k, (status, pages) in EXPECTED.items():
        if status == "located":
            assert got[k]["pages"] == pages, k
            assert all(isinstance(p, int) for p in got[k]["pages"])


def test_form_feed_pages_and_percent_without_sign(trace):
    """§15.3/§9: a pdftotext paper is paged by form feeds; `96.8%` matches `96.8` written without `%`."""
    got = by_key(trace())
    assert got[(6, "222")]["pages"] == [1]
    assert got[(6, "96.8%")]["pages"] == [2]


def test_percent_matches_decimal(trace):
    """§15.3: `51%` matches `0.51`; `41%` and `71%` match `0.41` and `0.71`."""
    got = by_key(trace())
    assert got[(7, "51%")]["status"] == "located"
    assert got[(9, "41%")]["status"] == got[(9, "71%")]["status"] == "located"


def test_comma_thousands_both_ways(trace):
    """§15.3: commas are removed on both sides (`1,124.7` ↔ `1124.7`, `1024` ↔ `1,024`)."""
    got = by_key(trace())
    assert got[(10, "1,124.7")]["pages"] == [1]
    assert got[(16, "1024")]["pages"] == [2]


def test_excluded_numbers(trace):
    """§15.3: years, single digits, numbers after `§`/`Fig.`/`Table` and citation contents yield no claim."""
    got = by_key(trace())
    assert sorted(n for (line, n) in got if line == 6) == ["222", "96.8%"]
    assert [n for (line, n) in got if line == 8] == ["4242"]
    assert not any(n in ("2025", "3", "12", "14", "15", "16", "2") for (_, n) in got)


def test_only_cited_body_sentences(trace):
    """§15.3/§14.2: uncited sentences, the references bucket and the appendix bucket give no claims."""
    lines = {line for (line, _) in by_key(trace())}
    assert 13 not in lines
    assert not any(line >= 18 for line in lines)


def test_citations_and_papers_fields(trace):
    """§15.3: `[2, 3]` cites both; ids come from `arXiv:ID` with the version suffix stripped."""
    got = by_key(trace())
    c = got[(16, "1024")]
    assert sorted(c["citations"]) == [2, 3]
    assert sorted(c["papers"]) == ["2510.23601", "2604.00392"]
    assert got[(9, "41%")]["papers"] == ["2604.01687"]          # `arXiv ID` form
    assert got[(8, "4242")]["citations"] == [2]


def test_no_source_findings(trace):
    """§15.3: a citation without an arXiv id ([7]) or not in the reference list ([9]) is no_source, T002 info."""
    res = trace(ledger=False)
    t2 = r3.of(res, "T002")
    assert [(f["severity"], f["path"], f["line"]) for f in t2] == [
        ("info", "REPORT.md", 14), ("info", "REPORT.md", 15)]


def test_ledger_applies_to_no_source(trace):
    """Pinned details: a ledger row turns a no_source number (314, cited as [7]) into ledgered; no T002 for it."""
    res = trace()
    got = by_key(res)
    assert got[(14, "314")]["status"] == "ledgered"
    assert got[(15, "315")]["status"] == "no_source"
    assert [f["line"] for f in r3.of(res, "T002")] == [15]


def test_bold_ledger_cell_is_a_token(trace):
    """Pinned details: `**2.75**` in a ledger cell counts as the token 2.75 (and that row says derived)."""
    assert by_key(trace())[(12, "2.75")]["status"] == "derived"


def test_claims_ordered_by_line_then_position(trace):
    """Pinned details: claims are ordered by line, then position in the line."""
    res = trace()
    assert [key(c) for c in res["claims"]] == sorted(EXPECTED, key=lambda k: (k[0], REPORT[k[0] - 1].index(k[1])))


def test_plain_number_never_matches_decimal_fraction(tmp_path, trace):
    """Pinned details: `51` (no `%`) is not located by the `0.51` on page 3."""
    report = REPORT[:4] + ["The distinct share ends at 51 of every 100 tools [2]."] + REPORT[16:]
    got = by_key(trace(report=report))
    assert got[(5, "51")]["status"] == "untraced"
    assert got[(5, "100")]["status"] == "untraced"


def test_no_split_inside_brackets_or_after_app(trace):
    """Pinned details: `[6, App. E]`-style citations are never split, and `App.` is an abbreviation, so each
    sentence keeps its number and its citation (the real report cites `[6, App. E]`)."""
    report = REPORT[:4] + [
        "Commitment stayed near 222 even as the price rose [3, App. E].",
        "The count 165 is given in App. B of the paper [2].",
        "Tab. 3 and Sec. 4 of Refs. 2 list 83.03% [2].",
    ] + REPORT[16:]
    got = by_key(trace(report=report))
    assert got[(5, "222")]["status"] == "located"
    assert got[(5, "222")]["citations"] == [3]
    assert got[(6, "165")]["status"] == "located"
    assert got[(7, "83.03%")]["citations"] == [2]


def test_untraced_findings(trace):
    """§15.3: each untraced entry is a T001 warning at the sentence's line; warnings keep ok true."""
    res = trace()
    t1 = r3.of(res, "T001")
    assert [(f["severity"], f["path"], f["line"]) for f in t1] == [("warning", "REPORT.md", 8)]
    assert res["ok"] is True


def test_without_ledger_everything_unlocated_is_untraced(trace):
    """§15.3: the ledger is optional; without it 606 and 2.75 are untraced."""
    res = trace(ledger=False)
    got = by_key(res)
    assert got[(11, "606")]["status"] == "untraced"
    assert got[(12, "2.75")]["status"] == "untraced"
    assert sorted(f["line"] for f in r3.of(res, "T001")) == [8, 11, 12]


def test_ledger_only_consulted_for_unlocated_numbers(trace):
    """§15.3: 83.03% has a ledger row but is located; 4242 in ledger prose and 42420 in a cell do not count."""
    got = by_key(trace())
    assert got[(5, "83.03%")]["status"] == "located"
    assert got[(8, "4242")]["status"] == "untraced"


def test_summary_has_all_statuses(trace):
    """§15.3: summary counts every status, with all 5 keys present."""
    res = trace()
    assert res["summary"] == {"located": 9, "derived": 1, "ledgered": 2, "untraced": 1, "no_source": 1}


def test_numbers_use_only_their_own_sentence_citations(trace):
    """§15.3: 222 is in paper [3], so a sentence citing only [2] cannot locate it."""
    report = REPORT[:4] + ["The census found 222 items [2].", "Another 222 items were kept [3]."] + REPORT[16:]
    got = by_key(trace(report=report))
    assert got[(5, "222")]["status"] == "untraced"
    assert got[(6, "222")]["status"] == "located"
    assert got[(6, "222")]["pages"] == [1]


def test_digit_boundaries(tmp_path, trace):
    """§15.3: `165` is not located inside `1650`, `2165` or `165.5`."""
    r3.write_paper(tmp_path / "papers", "2510.23601", ["We ran 1650 and 2165 tasks, scoring 165.5."])
    got = by_key(trace())
    assert got[(5, "165")]["status"] == "untraced"


def test_extra_files_use_report_references(tmp_path, trace):
    """§15.3: `files` are checked the same way, with the report's reference list."""
    r3.write(tmp_path / "talk.md", "The distinct share falls to 51% [2].\nNothing to see in 99 here.\n")
    res = trace(files=["talk.md"])
    extra = [c for c in res["claims"] if c["path"] == "talk.md"]
    assert [(c["line"], str(c["number"]), c["status"], c["pages"]) for c in extra] == [
        (1, "51%", "located", [3])]


# ------------------------------------------------------------------ CLI and registration

def test_cli_trace(tmp_path, trace, capsys):
    """§15.3/§0.4: `tundlekit claims trace REPORT --papers DIR --ledger L --json`; `--strict` fails on T001."""
    trace()
    code, data, _, _ = r3.run_cli(capsys, ["claims", "trace", "REPORT.md", "--papers", "papers",
                                           "--ledger", "LEDGER.md", "--json"])
    assert code == 0
    assert data["summary"]["derived"] == 1
    code, _, _, _ = r3.run_cli(capsys, ["claims", "trace", "REPORT.md", "--papers", "papers",
                                        "--ledger", "LEDGER.md", "--strict", "--json"])
    assert code == 1


def test_registration_claims_module():
    """§15.10: `claims` follows `review` in MODULES; claims_trace is registered and read-only."""
    from tundlekit import MODULES

    i = MODULES.index("textlint")
    assert MODULES[i + 1:i + 3] == ["review", "claims"]
    t = r3.get_tool("claims", "claims_trace")
    assert t.annotations.get("readOnlyHint") is True
    assert t.input_schema.get("additionalProperties") is False
    assert {"report", "papers", "ledger", "files"} <= set(t.input_schema["properties"])
    assert t.func.__module__ == "tundlekit.claims"
