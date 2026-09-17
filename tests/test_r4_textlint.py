"""MANIFEST §16.8 text_lint: permission `may` (be + past participle, `may not`), quoted hedges, S007 ask lists,
S005 captions and blockquotes. Rules from §7.1 and §14.1 otherwise unchanged.
"""
from __future__ import annotations

import pytest

import helpers_r4m as h


@pytest.mark.parametrize("sentence", [
    "Capsules may be bound to a slot at build time.",
    "Tools may be chained by the planner.",
    "Any adapter may be used here.",
    "The report may be written in Markdown.",
    "The flag may not change after the freeze.",
])
def test_permission_may_not_a_hedge(tmp_path, sentence):
    """§16.8: `may be` + past participle (irregular list or -ed/-en) and `may not` are not S003."""
    res = h.lint(tmp_path, f"# Notes\n\n{sentence}\n", rules=["S003"])
    assert h.by_rule(res, "S003") == []


@pytest.mark.parametrize("sentence", [
    "The cache may be useful for retries.",
    "This path may be slower on Windows.",
])
def test_may_be_adjective_still_a_hedge(tmp_path, sentence):
    """§16.8: `may be` + an adjective stays a hedge."""
    res = h.lint(tmp_path, f"# Notes\n\n{sentence}\n", rules=["S003"])
    assert h.lines_of(res, "S003") == [3]


def test_quoted_hedge_skipped(tmp_path):
    """§16.8: S003 skips text inside double quotes; the same phrase unquoted still fires."""
    body = ('# Notes\n\n'
            'The reviewer flagged the phrase "to some extent" in the abstract.\n\n'
            'The gain holds to some extent.\n')
    res = h.lint(tmp_path, body, rules=["S003"])
    assert h.lines_of(res, "S003") == [5]


def test_ask_list_questions_skipped(tmp_path):
    """§16.8: list items under a line ending in `:` that contains `ask` are not S007; a later question is."""
    body = ("# Handover\n\n"
            "Ask the supervisor:\n\n"
            "- Which slot does the capsule bind to?\n"
            "- Who approves the release?\n\n"
            "Is the gate deterministic? It is.\n")
    res = h.lint(tmp_path, body, rules=["S007"])
    assert h.lines_of(res, "S007") == [8]


def test_s005_skips_captions_and_blockquotes(tmp_path):
    """§16.8: S005 ignores caption lines (§7.2 forms) and blockquote lines; ordinary prose still fires."""
    body = ("# Results\n\n"
            "*Fig. 2. Build path; the gate is dashed.*\n\n"
            "Table 1. Scores; higher is better.\n\n"
            "> The reviewer wrote: fast; cheap.\n\n"
            "The build is fast; the gate is slow.\n")
    res = h.lint(tmp_path, body, rules=["S005"])
    assert h.lines_of(res, "S005") == [9]
