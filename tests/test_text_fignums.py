"""MANIFEST §7.2 text_fignums (captions, F001-F005, prefixes, tables, refs, arXiv/paper skip) and §0.3."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers_diagram_text import assert_checker_shape, rules, text, write  # noqa: E402


@pytest.fixture
def fig(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    def run(body, name="report.md", refs=None, extra=None):
        write(tmp_path / name, body)
        paths = [name]
        for n, b in (extra or {}).items():
            write(tmp_path / n, b)
            paths.append(n)
        args = {"paths": paths}
        if refs:
            for n, b in refs.items():
                write(tmp_path / n, b)
            args["refs"] = list(refs)
        res = text("text_fignums", **args)
        assert_checker_shape(res)
        return res
    return run


def test_clean_report(fig):
    body = ("# R\n\n![Fig. 1. Overview](a.png)\n\nAs Fig. 1 shows, it works.\n\n"
            "*Fig. 2. Detail*\n\nFig. 2 adds detail.\n")
    res = fig(body)
    assert res["ok"] is True and res["findings"] == []
    assert res["captions"]["report.md"]["Fig"] == {"": [1, 2]}


def test_caption_forms_recognised(fig):
    body = ("![Fig. 1. a](a.png)\n*Fig. 2. b*\n**Fig. 3. c**\nFig. 4. d\n"
            "*Table 1. t*\n**Table 2. u**\nTable 3. v\n")
    res = fig(body)
    cap = res["captions"]["report.md"]
    assert cap["Fig"] == {"": [1, 2, 3, 4]}
    assert cap["Table"] == {"": [1, 2, 3]}
    assert res["findings"] == []


def test_caption_indented_line_is_stripped(fig):
    res = fig("   *Fig. 1. indented*\n")
    assert res["captions"]["report.md"]["Fig"] == {"": [1]}


# F001
def test_f001_duplicate_reported_on_later_occurrences(fig):
    res = fig("*Fig. 1. a*\n*Fig. 2. b*\n*Fig. 2. c*\n*Fig. 2. d*\n")
    assert rules(res, "F001") == [3, 4]
    assert all(f["severity"] == "error" for f in res["findings"])


# F002
def test_f002_gap_line_null(fig):
    res = fig("*Fig. 1. a*\n*Fig. 3. b*\n")
    assert rules(res) == [("F002", None)]
    assert res["ok"] is False


def test_f002_once_per_gap(fig):
    res = fig("*Fig. 1. a*\n*Fig. 3. b*\n*Fig. 5. c*\n")
    assert rules(res, "F002") == [None, None]
    res = fig("*Fig. 1. a*\n*Fig. 2. b*\n*Fig. 6. c*\n")
    assert rules(res, "F002") == [None]


# F003
def test_f003_not_starting_at_one(fig):
    res = fig("*Fig. 2. a*\n*Fig. 3. b*\n")
    assert [r for r, _ in rules(res)] == ["F003"]


# F004
def test_f004_out_of_order_once(fig):
    res = fig("*Fig. 1. a*\n*Fig. 3. b*\n*Fig. 2. c*\n*Fig. 4. d*\n")
    assert [r for r, _ in rules(res)] == ["F004"]


# prefixes and tables are independent sequences
def test_prefix_sequences_independent(fig):
    res = fig("*Fig. 1. a*\n*Fig. 2. b*\n*Fig. E1. c*\n*Fig. E2. d*\n*Fig. G1. e*\n")
    assert res["findings"] == []
    assert res["captions"]["report.md"]["Fig"] == {"": [1, 2], "E": [1, 2], "G": [1]}


def test_prefix_sequence_checked_separately(fig):
    res = fig("*Fig. 1. a*\n*Fig. E2. b*\n")
    assert [r for r, _ in rules(res)] == ["F003"]


def test_tables_independent_of_figures(fig):
    res = fig("*Fig. 1. a*\n*Fig. 2. b*\n*Table 1. t*\n")
    assert res["findings"] == []
    res = fig("*Fig. 1. a*\n*Table 2. t*\n")
    assert [r for r, _ in rules(res)] == ["F003"]


# F005
def test_f005_unresolved_mention(fig):
    res = fig("*Fig. 1. a*\n\nSee Fig. 1 and Fig. 4.\n")
    assert rules(res) == [("F005", 3)]
    assert res["findings"][0]["severity"] == "error"


def test_f005_table_mention(fig):
    res = fig("*Table 1. a*\n\nTable 2 lists more.\n")
    assert rules(res) == [("F005", 3)]


def test_f005_arxiv_and_paper_mentions_skipped(fig):
    body = ("*Fig. 1. a*\n\nIn arXiv 2604.00392, Fig. 7 shows it.\n"
            "The original paper shows it in Fig. 9.\n")
    assert fig(body)["findings"] == []


def test_f005_resolves_across_report_files(fig):
    res = fig("*Fig. 1. a*\n", name="a.md", extra={"b.md": "Fig. 1 is in the other file.\n"})
    assert res["findings"] == []


def test_f005_refs_file(fig):
    res = fig("*Fig. 1. a*\n*Fig. 2. b*\n", refs={"deck.txt": "footer: Fig. 2\nfooter: Fig. 3\n"})
    assert [(f["rule"], f["path"], f["line"]) for f in res["findings"]] == [("F005", "deck.txt", 2)]
    assert "deck.txt" not in res["captions"]


def test_f005_prefixed_mention(fig):
    res = fig("*Fig. E1. a*\n\nSee Fig. E1 and Fig. E2.\n")
    assert rules(res) == [("F005", 3)]
