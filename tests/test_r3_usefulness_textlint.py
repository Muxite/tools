"""MANIFEST §14.1 text_lint, §14.2 text_wordcount and §14.3 text_fignums (review round 2 usefulness fixes).

Inputs are modelled on the real ai4research report: tables whose cells hold semicolons and questions,
"no capsule may write", an "Open questions" section, and `[2, Eq. (5)]` citation locators.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers_diagram_text import (  # noqa: E402
    assert_checker_shape, cli_json, lint_text, rules, text, tool_error, write,
)


@pytest.fixture
def lint(tmp_path, monkeypatch):
    def run(body, **kw):
        return lint_text(tmp_path, monkeypatch, body, **kw)
    return run


def sentence(n, stem="word"):
    """1 sentence of exactly n words (no hedges, no first person)."""
    return " ".join(["Tools"] + [f"{stem}{i}" for i in range(1, n)]) + "."


LONG_CELL = " ".join(f"cell{i}" for i in range(60))


# ====================================================================== §14.1 tables
def test_table_row_semicolon_not_s005(lint):
    """§14.1: S005 skips table rows (real report glossary rows use semicolons)."""
    body = ("# Terms\n\n"
            "| Step | Author | What it does |\n"
            "|---|---|---|\n"
            "| Fill requirements | A model | Fills in values only; the valid ids are fixed lists |\n"
            "| Validate | Deterministic code | Runs 7 kinds of check; finds every quote |\n")
    assert rules(lint(body), "S005") == []


def test_prose_semicolon_still_s005(lint):
    """§14.1 only exempts table rows: a semicolon in prose right after a table is still S005."""
    body = ("| Kind | Note |\n|---|---|\n| gate | exit code; timeout |\n\n"
            "The gate passes; the node closes.\n")
    assert rules(lint(body), "S005") == [5]


def test_table_row_question_not_s007(lint):
    """§14.1: S007 skips table rows (Appendix B style question tables)."""
    body = ("# Review\n\n| Question | Answer | Section |\n|---|---|---|\n"
            "| Does it verify claims? | Without an experiment, no. | 2.7 |\n"
            "| Is the span hash enforced? | Spans are re-hashed. | 2.7 |\n")
    assert rules(lint(body), "S007") == []


def test_long_table_row_not_s009(lint):
    """§14.1: S009 skips table rows, however many words a cell holds."""
    body = f"| Term | Meaning |\n|---|---|\n| capsule | {LONG_CELL} |\n"
    assert rules(lint(body), "S009") == []


def test_table_rows_not_in_stats(lint):
    """§14.1: table rows count neither as sentences nor as list items in stats."""
    body = ("The registry holds 80 entries. The planner binds them.\n\n"
            "| Term | Meaning |\n|---|---|\n"
            "| gate | A check. It decides PASS or FAIL. |\n"
            "| freeze | The point at which the plan is hashed. |\n")
    st = lint(body)["stats"]["report.md"]
    assert st["sentences"] == 2
    assert st["list_items"] == 0


def test_table_row_other_rules_still_apply(lint):
    """§14.1 exempts S005, S007 and S009 only: an em dash in a table row is still S001."""
    body = "| Term | Meaning |\n|---|---|\n| gate | A check — PASS or FAIL |\n"
    assert rules(lint(body), "S001") == [3]


# ====================================================================== §14.1 S003 `may`
@pytest.mark.parametrize("body", [
    "No capsule may write to the library directly.\n",
    "A server may use any transport it supports.\n",
    "The writer may sign the verifier record.\n",
    "An executor may repair the implementation but not change the hypothesis.\n",
    "The ids a model may name come from fixed lists in the schema.\n",
])
def test_may_as_permission_not_s003(lint, body):
    """§14.1: `may` followed by a word outside the hedge list gives permission and is not S003."""
    assert rules(lint(body), "S003") == []


@pytest.mark.parametrize("follow", ["be", "have", "well", "also", "not", "help", "seem", "lead", "cause"])
def test_may_hedge_followers_s003(lint, follow):
    """§14.1: `may` + be/have/well/also/not/help/seem/lead/cause is a hedge."""
    res = lint(f"The search may {follow} matter here.\n")
    lines = rules(res, "S003")
    assert lines and set(lines) == {1}


def test_may_hedge_real_sentence(lint):
    """§14.1: the real report's "the search may be incomplete" is still flagged."""
    res = lint("A targeted search found no such system, though the search may be incomplete.\n")
    assert rules(res, "S003") == [1]


# ====================================================================== §14.1 S007 question sections
def test_open_questions_section_exempt_from_s007(lint):
    """§14.1: prose under a heading containing `question` is exempt from S007."""
    body = ("# Report\n\n## 7. Open questions\n\n"
            "Which store holds the shared library? The design leaves it open.\n\n"
            "- Who approves a retirement?\n")
    assert rules(lint(body), "S007") == []


def test_question_exemption_ends_at_same_level_heading(lint):
    """§14.1: the exemption lasts until a heading of the same or a higher level."""
    body = ("## Open questions\n\nWhich store holds it?\n\n"
            "### Owners\n\nWho decides?\n\n"
            "## Directions\n\nWhy not now?\n")
    assert rules(lint(body), "S007") == [11]


def test_question_exemption_case_insensitive(lint):
    """§14.1: `Questions a reviewer will ask` (capital Q) is exempt too."""
    body = "## Appendix B. Questions a reviewer will ask\n\nWhat does the freeze cost?\n"
    assert rules(lint(body), "S007") == []


def test_questions_elsewhere_still_s007(lint):
    """§14.1: a question under an unrelated heading is still S007."""
    body = "## 6. Challenges\n\nWhy does the hash not stop tampering?\n"
    assert rules(lint(body), "S007") == [3]


# ====================================================================== §14.1 S011 citation brackets
@pytest.mark.parametrize("body", [
    "Alita-G keeps every tool from a correct run [2, Eq. (5)].\n",
    "The distinct share falls to 51% [2, Eq. (5), Tables 3-4].\n",
    "The merge tool is the only promotion path [3, pp. 4-5].\n",
    "The suite came before the tool [12, pp 7].\n",
])
def test_numbered_citation_bracket_exempt_from_s011(lint, body):
    """§14.1: text inside a citation bracket starting with a number is exempt from S011."""
    assert rules(lint(body), "S011") == []


def test_eq_outside_bracket_still_s011(lint):
    """§14.1: the exemption covers the bracket only; `Eq. (5)` in running prose is still S011."""
    res = lint("As Eq. (5) shows, the share falls [2].\n")
    assert rules(res, "S011") == [1]


def test_unnumbered_bracket_still_s011(lint):
    """§14.1: a bracket that does not start with a number is not a citation locator."""
    res = lint("The share falls [see Eq. (5)].\n")
    assert rules(res, "S011") == [1]


# ====================================================================== §14.1 file-wide suppression
def test_file_ignore_suppresses_listed_rules_everywhere(lint):
    """§14.1: `<!-- lint-file-ignore S003 S009 -->` anywhere suppresses those rules in the whole file."""
    body = ("# Notes\n\nThe result may be stale.\n\n" + sentence(50) + "\n\n"
            "Some text; more text.\n\n<!-- lint-file-ignore S003 S009 -->\n")
    res = lint(body)
    assert rules(res, "S003") == []
    assert rules(res, "S009") == []
    assert rules(res, "S005") == [7]


def test_file_ignore_without_ids_suppresses_nothing(lint):
    """§14.1: with no ids, lint-file-ignore suppresses nothing."""
    body = "<!-- lint-file-ignore -->\n\nThe result may be stale; we checked.\n"
    res = lint(body)
    assert sorted(rules(res)) == [("S002", 3), ("S003", 3), ("S005", 3)]


def test_file_ignore_is_per_file(tmp_path, monkeypatch):
    """§14.1: the suppression applies to the file that holds the comment only."""
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "a.md", "<!-- lint-file-ignore S003 -->\nIt may be late.\n")
    write(tmp_path / "b.md", "It may be late.\n")
    res = text("text_lint", paths=["a.md", "b.md"])
    assert_checker_shape(res)
    assert [(f["path"], f["rule"]) for f in res["findings"]] == [("b.md", "S003")]


# ====================================================================== §14.1 S012 band check
def test_s012_short_sentences(lint):
    """§14.1 S012: info, 1 per file, line null, when the mean prose sentence length is outside [15, 25]."""
    body = "\n".join(sentence(5) for _ in range(6)) + "\n"
    res = lint(body)
    f = [x for x in res["findings"] if x["rule"] == "S012"]
    assert len(f) == 1
    assert f[0]["severity"] == "info"
    assert f[0]["line"] is None
    assert f[0]["path"] == "report.md"
    assert res["ok"] is True
    assert res["counts"]["info"] == 1


def test_s012_inside_band_no_finding(lint):
    """§14.1 S012: a mean of 20 words is inside the default band."""
    body = "\n\n".join(sentence(20) for _ in range(6)) + "\n"
    assert rules(lint(body), "S012") == []


def test_s012_needs_five_sentences(lint):
    """§14.1 S012 needs at least 5 sentences."""
    body = " ".join(sentence(4) for _ in range(4)) + "\n"
    assert rules(lint(body), "S012") == []


def test_s012_excludes_list_items(lint):
    """§14.1 S012: list items are not prose sentences for the band check."""
    body = ("\n\n".join(sentence(20) for _ in range(5)) + "\n\n"
            + "".join(f"- item {i}\n" for i in range(30)))
    assert rules(lint(body), "S012") == []


def test_s012_excludes_table_rows(lint):
    """§14.1 S012: table rows are excluded too; 3 prose sentences are fewer than 5."""
    body = (" ".join(sentence(3) for _ in range(3)) + "\n\n| a | b |\n|---|---|\n"
            + "".join(f"| Row {i}. | Cell. |\n" for i in range(10)))
    assert rules(lint(body), "S012") == []


def test_s012_band_argument(lint):
    """§14.1: `band` [low, high] replaces the default band."""
    body = "\n".join(sentence(5) for _ in range(6)) + "\n"
    assert rules(lint(body, band=[3, 8]), "S012") == []
    assert rules(lint(body, band=[6, 30]), "S012") == [None]


def test_s012_cli_band(tmp_path, monkeypatch, capsys):
    """§14.1: CLI `--band 15,25`."""
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "r.md", "\n".join(sentence(5) for _ in range(6)) + "\n")
    code, res, _ = cli_json(capsys, ["text", "lint", "r.md", "--json"])
    assert code == 0 and [f["rule"] for f in res["findings"]] == ["S012"]
    code, res, _ = cli_json(capsys, ["text", "lint", "r.md", "--band", "3,8", "--json"])
    assert code == 0 and res["findings"] == []


def test_s012_rule_filter(lint):
    """§7.1/§14.1: S012 is a known rule id for `rules` and `ignore`."""
    body = "\n".join(sentence(5) + " It may be so." for _ in range(3)) + "\n"
    only = lint(body, rules=["S012"])
    assert {f["rule"] for f in only["findings"]} == {"S012"}
    assert rules(lint(body, ignore=["S012"]), "S012") == []


# ====================================================================== §14.2 wordcount
def sections(res, name):
    return [(s["heading"], s["words"], s["delta"]) for s in res["files"][name]["sections"]]


def test_baseline_file_deltas(tmp_path, monkeypatch):
    """§14.2: baseline_file compares with another file, with the same delta rules as baseline."""
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "old.md", "# Report\none two three\n## 1. Goal\na b c d\n## Removed\nx y\n")
    write(tmp_path / "new.md", "# Report\none two three four five\n## 1. Goal\na b\n## 2. Added\nfresh words here\n")
    res = text("text_wordcount", paths=["new.md"], baseline_file="old.md")
    assert sections(res, "new.md") == [("# Report", 5, 2), ("## 1. Goal", 2, -2), ("## 2. Added", 3, "new")]
    assert res["files"]["new.md"]["total"] == 10
    assert res["files"]["new.md"]["total_delta"] == 1


def test_baseline_and_baseline_file_exclusive(tmp_path, monkeypatch):
    """§14.2: giving both baseline and baseline_file is a ToolError."""
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "a.md", "# A\none\n")
    write(tmp_path / "b.md", "# A\none two\n")
    with pytest.raises(tool_error()):
        text("text_wordcount", paths=["a.md"], baseline="HEAD", baseline_file="b.md")


def test_baseline_file_cli(tmp_path, monkeypatch, capsys):
    """§14.2: CLI `--baseline-file PATH`."""
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "old.md", "# A\none\n")
    write(tmp_path / "new.md", "# A\none two three\n")
    code, res, _ = cli_json(capsys, ["text", "wordcount", "new.md", "--baseline-file", "old.md", "--json"])
    assert code == 0
    assert res["files"]["new.md"]["sections"][0]["delta"] == 2
    assert res["files"]["new.md"]["total_delta"] == 2


BUCKET_DOC = (
    "intro line words\n"
    "# AI4Research report\nalpha beta\n"
    "## 1. The goal\none two three four\n"
    "### 1.1 Terms\nfive six\n"
    "## References\n[1] Arbor paper 2606.11926\n"
    "### Extra refs\n[2] Kosmos\n"
    "## Appendix A. Sources\ns1 s2 s3\n"
    "### A.1 Detail\nd1\n"
    "## Appendix B. Questions a reviewer will ask\nq1 q2\n"
)


def test_buckets(tmp_path, monkeypatch):
    """§14.2: References/Appendix level-2 headings start buckets; deeper headings inherit; the rest is body."""
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "r.md", BUCKET_DOC)
    f = text("text_wordcount", paths=["r.md"])["files"]["r.md"]
    assert f["buckets"] == {"body": 11, "appendix": 6, "references": 6}
    assert sum(f["buckets"].values()) == f["total"]
    by = {s["heading"]: s["bucket"] for s in f["sections"]}
    assert by == {
        "(front matter)": "body", "# AI4Research report": "body", "## 1. The goal": "body",
        "### 1.1 Terms": "body", "## References": "references", "### Extra refs": "references",
        "## Appendix A. Sources": "appendix", "### A.1 Detail": "appendix",
        "## Appendix B. Questions a reviewer will ask": "appendix",
    }


def test_bibliography_bucket_case_insensitive(tmp_path, monkeypatch):
    """§14.2: `(?i)^(references|bibliography)\\b`."""
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "r.md", "# T\na b\n## BIBLIOGRAPHY\nc d e\n")
    f = text("text_wordcount", paths=["r.md"])["files"]["r.md"]
    assert f["buckets"] == {"body": 2, "appendix": 0, "references": 3}


TABLE_DOC = "# Terms\nTwo words\n\n| Term | Meaning |\n|---|---|\n| gate | A check |\n"


def test_tables_counted_by_default(tmp_path, monkeypatch):
    """§7.3/§14.2: by default table rows are whitespace tokens like any other line."""
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "r.md", TABLE_DOC)
    f = text("text_wordcount", paths=["r.md"])["files"]["r.md"]
    assert f["total"] == 14


def test_tables_false_leaves_rows_out(tmp_path, monkeypatch):
    """§14.2: tables=false leaves table rows out of the counts."""
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "r.md", TABLE_DOC)
    f = text("text_wordcount", paths=["r.md"], tables=False)["files"]["r.md"]
    assert f["sections"][0]["words"] == 2
    assert f["total"] == 2


def test_no_tables_cli(tmp_path, monkeypatch, capsys):
    """§14.2: CLI `--no-tables`."""
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "r.md", TABLE_DOC)
    code, res, _ = cli_json(capsys, ["text", "wordcount", "r.md", "--no-tables", "--json"])
    assert code == 0 and res["files"]["r.md"]["total"] == 2


# ====================================================================== §14.3 fignums
def _fig_files(tmp_path):
    write(tmp_path / "report-a.md", "![Fig. 1. The pipeline](f1.png)\n\nSee Fig. 1.\n")
    write(tmp_path / "report-b.md", "*Fig. 1. One.*\n\n*Fig. 2. Two.*\n\n*Fig. 3. Three.*\n")
    write(tmp_path / "deck-plan.md", "Slide 4 reuses Fig. 3 from the report.\n")


def test_refs_bound_to_one_report(tmp_path, monkeypatch):
    """§14.3: `FILE=REPORT` resolves that refs file's mentions against REPORT only."""
    monkeypatch.chdir(tmp_path)
    _fig_files(tmp_path)
    res = text("text_fignums", paths=["report-a.md", "report-b.md"], refs=["deck-plan.md=report-a.md"])
    assert_checker_shape(res)
    f = [x for x in res["findings"] if x["rule"] == "F005"]
    assert [(x["path"], x["line"]) for x in f] == [("deck-plan.md", 1)]


def test_plain_refs_resolve_against_all_reports(tmp_path, monkeypatch):
    """§14.3: a plain FILE still resolves against all reports."""
    monkeypatch.chdir(tmp_path)
    _fig_files(tmp_path)
    res = text("text_fignums", paths=["report-a.md", "report-b.md"], refs=["deck-plan.md"])
    assert [x for x in res["findings"] if x["rule"] == "F005"] == []


def test_refs_bound_cli(tmp_path, monkeypatch, capsys):
    """§14.3 through the CLI `--refs FILE=REPORT`."""
    monkeypatch.chdir(tmp_path)
    _fig_files(tmp_path)
    code, res, _ = cli_json(capsys, ["text", "fignums", "report-a.md", "report-b.md",
                                     "--refs", "deck-plan.md=report-b.md", "--json"])
    assert code == 0 and res["ok"] is True
    code, res, _ = cli_json(capsys, ["text", "fignums", "report-a.md", "report-b.md",
                                     "--refs", "deck-plan.md=report-a.md", "--json"])
    assert code == 1
    assert [x["rule"] for x in res["findings"]] == ["F005"]
