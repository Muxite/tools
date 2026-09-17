"""MANIFEST §17.5 translate_terms (one CJK share, slash terms before punctuation, line numbers on L findings)
and §17.7 docs (keyword checks on skills/<name>/SKILL.md and references/*.md)."""
from __future__ import annotations

import re

import pytest

import helpers_r5b as h

SRC = "The Gateway uses the UI to manage RetryBudget, CircuitBreaker and TokenBucket.\n"
ZH = "Gateway 用 界面 管理 RetryBudget、CircuitBreaker 和 TokenBucket。\n"


# ------------------------------------------------------------------------------------ one CJK share
def test_repro_ui_rendered_is_l003(tmp_path):
    """§17.5: the target is Chinese once term tokens are removed, so the approved rendering 界面 for UI gives
    L003 (info), not L001, although CamelCase terms make up most of its letters."""
    assert "界面" in (h.approved_zh("UI") or [])
    res = h.terms(tmp_path, SRC, ZH)
    assert [f["rule"] for f in h.about(res, "UI")] == ["L003"]
    assert res["counts"]["warning"] == 0
    assert h.term_count(res, "RetryBudget", 1) == 1


def test_repro_glossary_off_is_l001(tmp_path):
    """§16.6 with §17.5: glossary false keeps L001."""
    res = h.terms(tmp_path, SRC, ZH, glossary=False)
    assert [f["rule"] for f in h.about(res, "UI")] == ["L001"]


def test_repro_same_language_groups_target_as_cjk(tmp_path):
    """§17.5: the same share groups the target as CJK: with same-language it has no earlier CJK file (no
    findings), and the English back-translation is compared with the English source."""
    back = "The Gateway manages RetryBudget, CircuitBreaker and TokenBucket.\n"
    res = h.terms(tmp_path, SRC, ZH, back, compare="same-language")
    assert not [f for f in res["findings"] if f["path"].endswith("t0.md")]
    ui = h.about(res, "UI")
    assert [(f["rule"], f["path"].rsplit("/", 1)[-1]) for f in ui] == [("L001", "t1.md")]


def test_mostly_latin_target_still_l001(tmp_path):
    """§16.6/§17.5: a target that is Latin even after removing terms gets L001 although it contains 界面."""
    tgt = "The Gateway manages RetryBudget with the 界面 panel and many other English words here.\n"
    res = h.terms(tmp_path, SRC, tgt)
    assert [f["rule"] for f in h.about(res, "UI")] == ["L001"]


# ------------------------------------------------------------------------------------ slash terms
def test_slash_terms_before_period_and_comma(tmp_path):
    """§17.5: `TCP/IP.` and `CI/CD,` are still terms (path masking never takes trailing `.` or `,`)."""
    src = "The stack uses TCP/IP. Deploys go through CI/CD, then stop.\n"
    tgt = "该栈使用TCP/IP。部署走CI/CD，然后停止。\n"
    res = h.terms(tmp_path, src, tgt)
    assert h.term_count(res, "TCP/IP", 0) == 1 and h.term_count(res, "TCP/IP", 1) == 1
    assert h.term_count(res, "CI/CD", 0) == 1 and h.term_count(res, "CI/CD", 1) == 1
    assert res["findings"] == []


def test_slash_term_at_sentence_end_counted_in_target(tmp_path):
    """§17.5: a target that ends a sentence with the slash term still counts it."""
    res = h.terms(tmp_path, "我们使用 TCP/IP 协议栈\n", "We use TCP/IP.\n")
    assert h.term_count(res, "TCP/IP", 1) == 1
    assert h.about(res, "TCP/IP") == []


# ------------------------------------------------------------------------------------ line numbers
def test_l001_line_is_first_line_in_previous_file(tmp_path):
    """§17.5: L001 carries the first line of the term in the compared (previous) file."""
    src = "第一行没有术语。\n\n第三行提到 PlanGraph。\n第四行 PlanGraph 再次出现。\n"
    res = h.terms(tmp_path, src, "No term here.\nNone here either.\n")
    f = h.about(res, "PlanGraph", "L001")
    assert [x["line"] for x in f] == [3]


def test_l002_line_from_previous_target(tmp_path):
    """§17.5: with several targets, the line comes from the file compared with, not SRC."""
    src = "RetryBudget 很重要。\n"
    t0 = "Intro.\n\nMore.\nThe RetryBudget matters.\nRetryBudget again.\n"
    t1 = "RetryBudget 一次。\n"
    res = h.terms(tmp_path, src, t0, t1)
    l002 = [f for f in h.about(res, "RetryBudget", "L002") if f["path"].endswith("t1.md")]
    assert [f["line"] for f in l002] == [4]
    first = [f for f in h.about(res, "RetryBudget", "L002") if f["path"].endswith("t0.md")]
    assert [f["line"] for f in first] == [1]


def test_l003_line_and_same_language_line(tmp_path):
    """§17.5: L003 carries a line too; with same-language the line comes from the same-script file."""
    src = "Overview.\nThe UI shows RetryBudget.\n"
    res = h.terms(tmp_path, src, "界面 显示 RetryBudget 的 状态 和 数值。\n")
    assert [(f["rule"], f["line"]) for f in h.about(res, "UI")] == [("L003", 2)]
    zh = "界面 显示 RetryBudget 的 状态 和 数值。\n"
    back = "It shows RetryBudget.\n"
    res = h.terms(tmp_path, src, zh, back, compare="same-language")
    assert [(f["rule"], f["line"]) for f in h.about(res, "UI")] == [("L001", 2)]


def test_every_l_finding_has_int_line(tmp_path):
    """§17.5/§0.3: no L001/L002/L003 has `line: null` any more."""
    res = h.terms(tmp_path, SRC + "UI again and RetryBudget.\n", ZH, "Nothing.\n")
    assert res["findings"]
    assert all(isinstance(f["line"], int) and f["line"] >= 1 for f in res["findings"])


# ------------------------------------------------------------------------------------ docs (§17.7)
def has(text: str, pattern: str) -> bool:
    return re.search(pattern, text, re.I) is not None


@pytest.mark.parametrize("skill,pattern,why", [
    ("zh-en-translation", r"round[- ]trip[\s\S]{0,400}same-language|same-language[\s\S]{0,400}round[- ]trip",
     "--compare same-language for round trips"),
    ("tundle-bundle", r"bundle backup", "bundle backup"),
    ("tundle-bundle", r"<name>\.SOURCE\.md|\w\.SOURCE\.md", "per-file <name>.SOURCE.md"),
    ("deck-builder", r"tundlekit bundle backup", "bundle backup replaces the manual versions/ copy"),
    ("report-writing", r"tundlekit bundle backup", "bundle backup replaces the manual versions/ copy"),
    ("deliverable-review", r"tundlekit bundle backup", "bundle backup replaces the manual versions/ copy"),
])
def test_skill_mentions_round5(skill, pattern, why):
    """§17.7: each skill documents its round-5 point."""
    text = h.skill_text(skill)
    assert text, f"skills/{skill}/SKILL.md exists"
    assert has(text, pattern), f"{skill}: {why} ({pattern})"
