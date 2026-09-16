"""MANIFEST §14 usefulness fixes: text_lint, text_wordcount and text_fignums (§14.1-§14.3).

Companion to the other tests/test_r3_usefulness_*.py files (helpers in helpers_usefulness.py).
"""
from __future__ import annotations

import hashlib  # noqa: F401
import json  # noqa: F401
import re  # noqa: F401
import sys
from pathlib import Path

import pytest  # noqa: F401

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_usefulness as h  # noqa: E402
from helpers_usefulness import gitenv  # noqa: E402,F401  (fixture)


# ===================================================================== from the textlint group

@pytest.fixture
def lint(tmp_path, monkeypatch):
    def run(body, **kw):
        return h.lint_text(tmp_path, monkeypatch, body, **kw)
    return run


def words(n, lead="Capsules"):
    return " ".join([lead] + [f"term{i}" for i in range(1, n)]) + "."


def wc(tmp_path, monkeypatch, name, body, **kw):
    monkeypatch.chdir(tmp_path)
    h.write(tmp_path / name, body)
    return h.call("text_wordcount", paths=[name], **kw)["files"][name]


def test_table_row_with_semicolon_and_question(lint):
    """§14.1: a table row holding both `;` and `?` gives neither S005 nor S007."""
    body = ("| Question | Answer |\n|---|---|\n"
            "| What happens when no capsule fits? | The node is unsatisfiable; the plan fails at the freeze |\n")
    res = lint(body)
    assert h.lines(res, "S005") == [] and h.lines(res, "S007") == []


def test_table_row_contraction_still_s004(lint):
    """§14.1 exempts only S005/S007/S009: a contraction in a table row is still S004."""
    body = "| Term | Meaning |\n|---|---|\n| gate | It doesn't move |\n"
    assert h.lines(lint(body), "S004") == [3]


def test_may_counts_only_hedge_uses(lint):
    """§14.1: in 1 line, only the hedging `may` is flagged."""
    res = lint("A server may use caching, and the cache may well be stale.\n")
    assert len(h.of(res, "S003")) == 1


def test_level3_question_heading_ended_by_level2(lint):
    """§14.1: a level-3 question heading is ended by a level-2 heading."""
    body = ("## Body\n\nPlain text.\n\n### Question log\n\nIs the hash enforced?\n\n"
            "## Next\n\nIs it recomputed?\n")
    assert h.lines(lint(body), "S007") == [11]


def test_question_list_items_exempt(lint):
    """§14.1: list items under a question heading are prose and exempt too."""
    body = "## 7. Open questions this adds\n\n- Who owns the ledger?\n- Which gate retires a tool?\n"
    assert h.lines(lint(body), "S007") == []


def test_bracket_exemption_keeps_other_rules(lint):
    """§14.1: the bracket exemption is for S011; an em dash inside is still S001."""
    res = lint("The share is a ratio [2, Eq. 6 — revised].\n")
    assert h.lines(res, "S011") == []
    assert h.lines(res, "S001") == [1]


def test_file_ignore_covers_headings(lint):
    """§14.1: file-wide S001 suppression includes headings."""
    body = "# Capsules — the design\n\nText — more text.\n\n<!-- lint-file-ignore S001 -->\n"
    assert h.lines(lint(body), "S001") == []


def test_file_ignore_keeps_other_rules(lint):
    """§14.1: only the listed rules are suppressed."""
    body = "We checked it; it may be fine.\n<!-- lint-file-ignore S003 -->\n"
    assert sorted(h.pairs(lint(body))) == [("S002", 1), ("S005", 1)]


def test_s012_long_sentences(lint):
    """§14.1: a mean of 26 is above the band; exactly 5 sentences are enough."""
    body = "\n\n".join(words(26) for _ in range(5)) + "\n"
    res = lint(body)
    f = h.of(res, "S012")
    assert len(f) == 1 and f[0]["line"] is None and f[0]["severity"] == "info"
    assert res["ok"] is True


def test_buckets_all_zero_keys_present(tmp_path, monkeypatch):
    """§14.2: the 3 bucket keys are always present."""
    f = wc(tmp_path, monkeypatch, "r.md", "# Only body\nsome words here\n")
    assert f["buckets"] == {"body": 3, "appendix": 0, "references": 0}


def test_tables_true_explicit(tmp_path, monkeypatch):
    """§14.2: tables defaults to true; giving it explicitly changes nothing."""
    body = "# T\n| a | b |\n"
    assert wc(tmp_path, monkeypatch, "r.md", body, tables=True)["total"] == 5


def test_bound_refs_skip_arxiv_mentions(tmp_path, monkeypatch):
    """§14.3 with §7.2: the arXiv/paper skip still applies in a bound refs file."""
    monkeypatch.chdir(tmp_path)
    h.write(tmp_path / "a.md", "Fig. 1. A.\n")
    h.write(tmp_path / "plan.md", "The paper shows Fig. 7.\narXiv 2604.00392 Table 4.\n")
    res = h.call("text_fignums", paths=["a.md"], refs=["plan.md=a.md"])
    assert h.of(res, "F005") == []
