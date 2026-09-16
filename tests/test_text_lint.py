"""MANIFEST §7.1 text_lint (rules S001-S011, masking, suppression, structure, sentences, stats)
and §0.3 checker conventions."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers_diagram_text import assert_checker_shape, lint_text, rules, text, tool_error, write  # noqa: E402


@pytest.fixture
def lint(tmp_path, monkeypatch):
    def run(body, **kw):
        return lint_text(tmp_path, monkeypatch, body, **kw)
    return run


# ------------------------------------------------------------------ S001 em dash
def test_s001_em_dash_in_prose(lint):
    res = lint("Plain text — with a dash.\n")
    assert rules(res) == [("S001", 1)]
    assert res["findings"][0]["severity"] == "error"
    assert res["ok"] is False


def test_s001_em_dash_in_heading(lint):
    assert rules(lint("# Title\n\n## Part — two\n\nFine.\n")) == [("S001", 3)]


def test_s001_em_dash_in_code_span_is_masked(lint):
    assert rules(lint("Use `a — b` here.\n")) == []


# ------------------------------------------------------------------ S002 first person
@pytest.mark.parametrize("body", [
    "We tested the tool.\n",
    "The method is ours.\n",
    "The tool helped us.\n",
    "Our method works.\n",
    "I think the tool works.\n",
])
def test_s002_positive(lint, body):
    assert rules(lint(body)) == [("S002", 1)]


@pytest.mark.parametrize("body", [
    "The US market grew.\n",
    "Trust the user and focus.\n",
    "Type I Error rates stayed flat.\n",
    "The answer weighed heavily.\n",
])
def test_s002_negative(lint, body):
    assert rules(lint(body)) == []


def test_s002_in_heading(lint):
    assert rules(lint("## What we learned\n\nThe tool works.\n")) == [("S002", 1)]


# ------------------------------------------------------------------ S003 hedges
@pytest.mark.parametrize("body", [
    "The tool seems fine.\n",
    "This is arguably best.\n",
    "Perhaps not.\n",
    "It might work.\n",
    "It may work.\n",
    "To some extent the tool works.\n",
    "It appears correct.\n",
])
def test_s003_positive(lint, body):
    res = lint(body)
    assert rules(res) == [("S003", 1)]
    assert res["findings"][0]["severity"] == "warning"
    assert res["ok"] is True


@pytest.mark.parametrize("body", [
    "In May the tool shipped.\n",
    "The tool seemed fine.\n",
    "The mayor spoke.\n",
])
def test_s003_negative(lint, body):
    assert rules(lint(body)) == []


# ------------------------------------------------------------------ S004 contractions
@pytest.mark.parametrize("body", [
    "The tool doesn't work.\n",
    "They're done.\n",
    "It's done.\n",
    "Let's go.\n",
    "The tool doesn’t work.\n",
    "That's the result.\n",
])
def test_s004_positive(lint, body):
    assert rules(lint(body)) == [("S004", 1)]


@pytest.mark.parametrize("body", [
    "The model's output is fine.\n",
    "The tools' outputs are fine.\n",
])
def test_s004_negative(lint, body):
    assert rules(lint(body)) == []


def test_s004_excerpt_shows_match(lint):
    res = lint("The runs don't stop.\n")
    assert "don't" in res["findings"][0]["excerpt"]


# ------------------------------------------------------------------ S005 semicolon
def test_s005_semicolon_in_prose(lint):
    res = lint("First part; second part.\n")
    assert rules(res) == [("S005", 1)]
    assert res["findings"][0]["severity"] == "warning"


def test_s005_not_in_code_span_or_heading(lint):
    assert rules(lint("## Part; two\n\nUse `a; b` inline.\n")) == []


# ------------------------------------------------------------------ S006 markers
@pytest.mark.parametrize("body", [
    "⚠ check this value.\n",
    "The result [verified] holds.\n",
    "The result [Verified] holds.\n",
    "See [TODO add the table].\n",
    "TODO: fix this.\n",
    "The value XXX stays.\n",
])
def test_s006_positive(lint, body):
    res = lint(body)
    assert rules(res) == [("S006", 1)]
    assert res["findings"][0]["severity"] == "error"


# ------------------------------------------------------------------ S007 questions
@pytest.mark.parametrize("body", [
    "Why does it fail? Nobody knows.\n",
    "Is the tool done?\n",
])
def test_s007_positive(lint, body):
    res = lint(body)
    assert rules(res) == [("S007", 1)]
    assert res["findings"][0]["severity"] == "warning"


@pytest.mark.parametrize("body", [
    "See https://example.org/a?b=1 now.\n",
    "The regex a?b matches.\n",
    "## Why?\n\nBecause.\n",
])
def test_s007_negative(lint, body):
    assert rules(lint(body)) == []


# ------------------------------------------------------------------ S008 et al.
def test_s008_outside_exempt(lint):
    res = lint("Smith et al. showed the effect.\n")
    assert rules(res) == [("S008", 1)]
    assert res["findings"][0]["severity"] == "error"


def test_s008_references_section_exempt(lint):
    assert rules(lint("# Report\n\nText.\n\n## References\n\nSmith et al. 2020.\n")) == []


def test_s008_exemption_covers_deeper_and_ends_at_same_level(lint):
    body = ("## References\n\nA et al. x.\n\n### Sub\n\nB et al. y.\n\n"
            "## Next\n\nC et al. z.\n")
    assert rules(lint(body)) == [("S008", 11)]


def test_s008_appendix_a_exempt_appendix_b_not(lint):
    body = "## Appendix A. Sources\n\nA et al. x.\n\n## Appendix B\n\nB et al. y.\n"
    assert rules(lint(body)) == [("S008", 7)]


# ------------------------------------------------------------------ S009 long sentences
def test_s009_default_max_words_42(lint):
    over = " ".join(["word"] * 43) + ".\n"
    at = " ".join(["word"] * 42) + ".\n"
    assert rules(lint(over)) == [("S009", 1)]
    assert rules(lint(at)) == []


def test_s009_custom_max_words(lint):
    assert rules(lint("one two three four five six.\n", max_words=5)) == [("S009", 1)]
    assert rules(lint("one two three four five.\n", max_words=5)) == []


def test_s009_reported_where_sentence_starts(lint):
    body = "Short one.\nalpha beta gamma delta epsilon zeta\neta theta.\n"
    res = lint(body, max_words=5)
    assert rules(res) == [("S009", 2)]
    assert res["findings"][0]["severity"] == "warning"


# ------------------------------------------------------------------ S010 section openers
@pytest.mark.parametrize("opener", [
    "This section explains the tool.",
    "In this section, the tool is shown.",
    "This chapter covers the tool.",
])
def test_s010_positive(lint, opener):
    res = lint(f"# Intro\n\n{opener}\n")
    assert [r for r, _ in rules(res)] == ["S010"]
    assert res["findings"][0]["severity"] == "warning"


def test_s010_only_first_sentence(lint):
    assert rules(lint("# Intro\n\nThe tool is small. This section explains it.\n")) == []


# ------------------------------------------------------------------ S011 jargon
@pytest.mark.parametrize("body", [
    "See Eq. 3 for details.\n",
    "See Eq.(4) there.\n",
    "A gain of 3 pp overall.\n",
])
def test_s011_positive(lint, body):
    res = lint(body)
    assert rules(res) == [("S011", 1)]
    assert res["findings"][0]["severity"] == "warning"


@pytest.mark.parametrize("body", [
    "See pp. 12-15 of the book.\n",
    "The app works.\n",
    "Equation 3 holds.\n",
])
def test_s011_negative(lint, body):
    assert rules(lint(body)) == []


# ------------------------------------------------------------------ masking
@pytest.mark.parametrize("body", [
    "Intro.\n\n```\nwe — don't; TODO: x\n```\n\nEnd.\n",
    "Intro.\n\n~~~python\nour = maybe; it's\n~~~\n\nEnd.\n",
    "<!-- we — TODO: -->\nFine.\n",
    "Visit https://example.com/we/our;x now.\n",
    "Read [the guide](docs/we-may-fail.md) now.\n",
    "---\ntitle: We may — fail\n---\n\nFine text.\n",
])
def test_masked_regions_produce_no_findings(lint, body):
    assert rules(lint(body)) == []


def test_link_text_is_not_masked(lint):
    assert rules(lint("See [what we did](notes.md) there.\n")) == [("S002", 1)]


def test_text_after_code_span_still_checked(lint):
    assert rules(lint("Run `x` and we go.\n")) == [("S002", 1)]


def test_line_numbers_after_fence(lint):
    assert rules(lint("```\ncode\n```\nWe go.\n")) == [("S002", 4)]


# ------------------------------------------------------------------ suppression
def test_suppress_listed_rule_on_next_line(lint):
    assert rules(lint("<!-- lint-ignore S003 -->\nIt may work.\n")) == []


def test_suppress_only_listed_rules(lint):
    assert rules(lint("<!-- lint-ignore S003 -->\nWe may work.\n")) == [("S002", 2)]


def test_suppress_all_rules(lint):
    assert rules(lint("<!-- lint-ignore -->\nWe may — work.\n")) == []


def test_suppress_does_not_reach_two_lines_down(lint):
    assert rules(lint("<!-- lint-ignore S003 -->\nFine.\nIt may work.\n")) == [("S003", 3)]


def test_suppress_on_same_line(lint):
    assert rules(lint("We may go. <!-- lint-ignore S002 S003 -->\n")) == []


# ------------------------------------------------------------------ rules / ignore / errors
def test_rules_filter(lint):
    assert rules(lint("We — may go.\n", rules=["S001"])) == [("S001", 1)]


def test_ignore_filter(lint):
    assert sorted(rules(lint("We — may go.\n", ignore=["S002"]))) == [("S001", 1), ("S003", 1)]


def test_unknown_rule_is_toolerror(lint):
    with pytest.raises(tool_error()):
        lint("Fine.\n", rules=["S999"])


def test_missing_path_is_toolerror(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(tool_error()):
        text("text_lint", paths=["nope.md"])


def test_directory_walk_md_and_txt_only(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "docs" / "a.md", "We go.\n")
    write(tmp_path / "docs" / "sub" / "b.txt", "We go.\n")
    write(tmp_path / "docs" / "c.py", "We go.\n")
    res = text("text_lint", paths=["docs"])
    assert_checker_shape(res)
    names = sorted(f["path"].rsplit("/", 1)[-1] for f in res["findings"])
    assert names == ["a.md", "b.txt"]


# ------------------------------------------------------------------ §0.3 shape, sorting, counts
def test_findings_sorted_across_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "b.md", "Fine.\nIt may — work; we go.\n")
    write(tmp_path / "a.md", "We go.\n\nIt may go.\n")
    res = text("text_lint", paths=["b.md", "a.md"])
    assert_checker_shape(res)
    assert [(f["path"], f["line"], f["rule"]) for f in res["findings"]] == [
        ("a.md", 1, "S002"), ("a.md", 3, "S003"),
        ("b.md", 2, "S001"), ("b.md", 2, "S002"), ("b.md", 2, "S003"), ("b.md", 2, "S005")]
    assert res["counts"] == {"error": 3, "warning": 3, "info": 0}


def test_clean_file(lint):
    res = lint("# Title\n\nThe tool works well.\n")
    assert res["ok"] is True
    assert res["findings"] == []
    assert res["counts"] == {"error": 0, "warning": 0, "info": 0}


# ------------------------------------------------------------------ sentences and stats
def stats(res, name="report.md"):
    return res["stats"][name]


def test_stats_basic(lint):
    s = stats(lint("One two three. Four five six seven.\n"))
    assert (s["sentences"], s["words"], s["mean_sentence_words"], s["max_sentence_words"],
            s["list_items"]) == (2, 7, 3.5, 4, 0)


def test_stats_mean_rounded(lint):
    s = stats(lint("Go. Go now. Go now.\n"))
    assert s["sentences"] == 3
    assert s["mean_sentence_words"] == 1.7
    assert s["max_sentence_words"] == 2


def test_stats_empty(lint):
    s = stats(lint("# Only a heading\n"))
    assert s["sentences"] == 0 and s["words"] == 0 and s["mean_sentence_words"] == 0


def test_stats_list_items(lint):
    s = stats(lint("- Alpha beta.\n- Gamma delta epsilon.\n"))
    assert s["list_items"] == 2
    assert s["sentences"] == 2


def test_sentence_spans_lines_in_paragraph(lint):
    s = stats(lint("Alpha beta\ngamma delta.\n"))
    assert (s["sentences"], s["words"]) == (1, 4)


def test_paragraph_break_ends_sentence(lint):
    s = stats(lint("Alpha beta\n\ngamma delta\n"))
    assert s["sentences"] == 2


@pytest.mark.parametrize("body", [
    "Use a tool, e.g. a parser. Done.\n",
    "Smith vs. Jones went on. Done.\n",
    "The value is 3.5 now. Done.\n",
    "See Fig. 3 for it. Done.\n",
])
def test_abbreviations_do_not_split(lint, body):
    assert stats(lint(body))["sentences"] == 2
