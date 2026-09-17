"""MANIFEST §16.6: papers_summary titles, papers_index_check (P006/P007, `## How`, profile), papers_peek grep
`width` with anchored patterns, and translate_terms (masking, `/` terms, list markers, sub-terms, English-only
lines, glossary L003, compare same-language). Results follow §0.2/§0.3.
"""
from __future__ import annotations

import pytest

import helpers_r4m as h


def pdir(tmp_path):
    d = tmp_path / "papers"
    d.mkdir()
    return d


# ------------------------------------------------------------------------------------ papers_summary
LEDGER_P1 = ("Published as a conference paper at ICLR 2026\n"
             "LEDGER: A Provenance Ledger for\n"
             "Auditing LLM Agents\n"
             "Alice Smith1, Bob Jones2, Carol White1\n"
             "1University of Somewhere\n"
             "ABSTRACT\n")


def test_summary_skips_venue_line_and_joins_upper_case_continuation(tmp_path):
    """§16.6: the `Published as ...` line is skipped; `Auditing LLM Agents` continues the title (not empty, no
    `@`, no author marks, title < 20 words); the author list stops it and becomes `authors`."""
    d = pdir(tmp_path)
    h.marker_txt(d / "2601.00001.txt", h.paper_pages(LEDGER_P1, 10, refs_page=9))
    res = h.call("papers_summary", id="2601.00001", dir=str(d))
    lines = h.summary_lines(res)
    assert lines[0] == "# 2601.00001 · LEDGER: A Provenance Ledger for Auditing LLM Agents"
    # §17.4: author marks are stripped from `authors` (was kept verbatim under §15.8)
    assert lines[2] == "Alice Smith, Bob Jones, Carol White · arXiv 2601.00001 · 10 pp (8 body)"
    assert h.slash(res["path"]).endswith("summaries/2601.00001 - LEDGER.md")


def test_summary_small_caps_rejoined(tmp_path):
    """§16.6: `A LITA -G` (small caps split by the PDF) is rejoined to `ALITA-G`, also in the short name."""
    d = pdir(tmp_path)
    p1 = ("A LITA -G: Self-Evolving Agents via Tool Generation\n"
          "Jiahao Qiu, Xuan Qi, Tongcheng Zhang\n"
          "Abstract\n")
    h.marker_txt(d / "2510.23601.txt", h.paper_pages(p1, 6))
    res = h.call("papers_summary", id="2510.23601", dir=str(d))
    assert h.summary_lines(res)[0] == "# 2510.23601 · ALITA-G: Self-Evolving Agents via Tool Generation"
    assert h.slash(res["path"]).endswith("summaries/2510.23601 - ALITA-G.md")


def test_summary_numbered_references_heading(tmp_path):
    """§16.6: `7 References` counts as the references page, so body = that page - 1."""
    d = pdir(tmp_path)
    p1 = "Agents that audit their own tools\nJane Doe, John Roe, Max Mustermann\n"
    h.marker_txt(d / "2602.00002.txt", h.paper_pages(p1, 12, refs_page=8, refs_line="7 References"))
    res = h.call("papers_summary", id="2602.00002", dir=str(d), short="Audit")
    assert h.summary_lines(res)[2].endswith("· arXiv 2602.00002 · 12 pp (7 body)")


# ------------------------------------------------------------------------------------ papers_index_check
INDEX = "# Paper summaries\n\n{n} summaries.\n\n| Paper | Line |\n|---|---|\n{rows}"


def index_tree(tmp_path, ids=("2502.10855", "2310.03714"), index=True, body=h.SUMMARY_BODY):
    d = pdir(tmp_path)
    for pid in ids:
        h.marker_txt(d / f"{pid}.txt", h.paper_pages("A paper title with words\nA. Author, B. Author, C. D\n", 4))
        h.summary_file(d, pid, "S" + pid[-2:], body=body)
    if index:
        h.write(d / "summaries" / "INDEX.md",
                INDEX.format(n=len(ids), rows="".join(f"| {pid} | x |\n" for pid in ids)))
    return d


def test_p004_accepts_any_how_heading(tmp_path):
    """§16.6: `## How Claimify works` satisfies the "How it works" heading."""
    body = h.SUMMARY_BODY.replace("## How it works (p2-4)", "## How Claimify works")
    d = index_tree(tmp_path, ids=("2502.10855",), body=body)
    res = h.call("papers_index_check", dir=str(d))
    h.check_shape(res)
    assert h.by_rule(res, "P004") == []


def test_profile_overrides_required_headings(tmp_path):
    """§16.6: `profile` maps a summary id to its own heading list; other summaries keep the default list."""
    d = index_tree(tmp_path)
    h.summary_file(d, "2502.10855", "S55", body="## Summary\nx\n\n## Verdict\ny\n")
    res = h.call("papers_index_check", dir=str(d), profile={"2502.10855": ["## Summary", "## Verdict"]})
    h.check_shape(res)
    assert h.by_rule(res, "P004") == []
    res = h.call("papers_index_check", dir=str(d), profile={"2502.10855": ["## Summary", "## Method"]})
    p004 = h.by_rule(res, "P004")
    assert len(p004) == 1
    assert "2502.10855" in p004[0]["message"] + p004[0]["path"]


def test_missing_index_is_p006_not_error(tmp_path):
    """§16.6: a missing INDEX.md is a P006 warning, never a ToolError; ok stays true."""
    d = index_tree(tmp_path, index=False)
    res = h.call("papers_index_check", dir=str(d))
    h.check_shape(res)
    p006 = h.by_rule(res, "P006")
    assert len(p006) == 1
    assert p006[0]["severity"] == "warning"
    assert res["ok"] is True
    assert res["summaries"] == 2


def test_p007_report_without_citations(tmp_path):
    """§16.6: a report with no resolvable citations gives P007 (info) and no P005."""
    d = index_tree(tmp_path)
    report = h.write(tmp_path / "report.md", "# Report\n\n## 1. Intro\n\nPlain prose with no sources.\n")
    res = h.call("papers_index_check", dir=str(d), report=str(report))
    h.check_shape(res)
    p007 = h.by_rule(res, "P007")
    assert len(p007) == 1 and p007[0]["severity"] == "info"
    assert h.by_rule(res, "P005") == []


# ------------------------------------------------------------------------------------ papers_peek grep width
def test_grep_width_anchored_pattern(tmp_path):
    """§16.6: the width cut is centred on the match in the hit's own line, so `^Table` stays in the snippet."""
    d = pdir(tmp_path)
    before = "alpha " * 40
    after = "omega " * 40
    page = f"{before}\nTable 3: Accuracy of every agent on the held-out split\n{after}\n"
    h.marker_txt(d / "2603.00003.txt", [page])
    res = h.call("papers_peek", id="2603.00003", mode="grep", dir=str(d), pattern="^Table", context=1, width=60)
    (hit,) = res["hits"]
    assert len(hit["text"]) <= 60
    assert "Table 3" in hit["text"]


# ------------------------------------------------------------------------------------ translate_terms
def terms(tmp_path, src, *targets, **kw):
    s = h.write(tmp_path / "src.md", src)
    ts = [h.write(tmp_path / f"t{i}.md", t) for i, t in enumerate(targets)]
    res = h.call("translate_terms", src=str(s), targets=[str(t) for t in ts], **kw)
    h.check_shape(res)
    return res


def test_url_masking_stops_at_cjk(tmp_path):
    """§16.6: the URL mask stops at the first non-ASCII character, so the MCP after it still counts (2 in all)."""
    res = terms(tmp_path, "我们使用MCP协议/接口。详见https://x.org获取MCP信息\n", "We use MCP.\n")
    assert h.term_count(res, "MCP", 0) == 2
    assert "MCP" in res["terms"]


def test_slash_terms(tmp_path):
    """§16.6: `TCP/IP` is a term; its parts are not counted separately."""
    res = terms(tmp_path, "The stack uses TCP/IP everywhere.\n", "该栈处处使用TCP/IP。\n")
    assert res["terms"]["TCP/IP"] == [1, 1]
    assert h.term_count(res, "TCP", 0) == 0
    assert h.term_count(res, "IP", 0) == 0


def test_list_markers_stripped_from_runs(tmp_path):
    """§16.6: a `- ` list marker is not part of a run term."""
    res = terms(tmp_path, "- build cache 很重要\n- 另一个 retry budget\n", "- build cache matters\n")
    keys = h.term_keys_lower(res)
    assert "build cache" in keys
    assert "retry budget" in keys
    assert not any(k.startswith(("-", "*")) for k in keys)


def test_sub_term_not_counted_separately(tmp_path):
    """§16.6: `IDs` inside the run `acceptance IDs` is not a separate term."""
    res = terms(tmp_path, "每条需求都有 acceptance IDs 用于追踪\n", "Each item has acceptance IDs.\n")
    assert h.term_count(res, "acceptance IDs", 0) == 1
    assert h.term_count(res, "IDs", 0) == 0


def test_english_only_lines_give_no_run_terms(tmp_path):
    """§16.6: an English-only line contributes no run terms (CamelCase/caps terms still count)."""
    res = terms(tmp_path, "Plain words only here\nThe PlanGraph runs\n", "计划图运行\n")
    keys = h.term_keys_lower(res)
    assert "plain words only here" not in keys
    assert not any(" " in k for k in keys)
    assert "plangraph" in keys


def test_glossary_l003_on_cjk_hop(tmp_path):
    """§16.6: a mostly-CJK target that uses the approved zh rendering (glossary `UI` -> 界面) gets L003 (info)
    instead of L001; with glossary false it stays L001."""
    zh = h.approved_zh("UI")
    assert zh, "glossary row for UI is approved"
    src = "The UI shows each step.\nThe UI updates live.\n"
    tgt = f"{zh[0]}显示每一个步骤。\n{zh[0]}会实时更新。\n"
    res = terms(tmp_path, src, tgt)
    ui = [f for f in res["findings"] if f["excerpt"] == "UI" or "'UI'" in f["message"]]
    assert [f["rule"] for f in ui] == ["L003"]
    assert ui[0]["severity"] == "info"
    assert zh[0] in ui[0]["message"]
    res = terms(tmp_path, src, tgt, glossary=False)
    assert [f["rule"] for f in res["findings"] if "UI" in f["message"]] == ["L001"]


def test_compare_same_language_catches_drift(tmp_path):
    """§16.6: en -> zh -> en. With `previous`, the back-translation that lost PlanGraph is compared with the zh
    file (count 0) and is silent; with `same-language` it is compared with the English source and gets L001."""
    src = "The PlanGraph orders each RetryBudget.\n"
    zh = "计划图为每个RetryBudget排序。\n"
    back = "The plan graph orders each RetryBudget.\n"
    res = terms(tmp_path, src, zh, back)
    back_path = h.slash(tmp_path / "t1.md")
    assert not [f for f in res["findings"] if f["path"].endswith("t1.md") and "PlanGraph" in f["message"]]
    res = terms(tmp_path, src, zh, back, compare="same-language")
    hits = [f for f in res["findings"] if f["path"].endswith("t1.md") and "PlanGraph" in f["message"]]
    assert [f["rule"] for f in hits] == ["L001"], back_path


def test_compare_bad_value_is_error(tmp_path):
    """§16.6/§0.2: `compare` is `previous` or `same-language`; anything else is refused."""
    with pytest.raises(h.tool_error()):
        terms(tmp_path, "The PlanGraph.\n", "计划图。\n", compare="nearest")
