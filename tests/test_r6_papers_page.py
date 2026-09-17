"""Round 6: `papers_page` (MANIFEST §18.3, with §9, §15.8, §0.2-§0.4)."""
from __future__ import annotations

import os
import re

import pytest

import helpers_r6g as h

REPORT = """# Test report

## 1. Frame

Kosmos [2511.02824] runs for 12 hours. DSPy (arXiv 2310.03714v3) compiles prompts.
The survey 2507.01903v2 defines the field.

## 2. Systems

AI Scientist-v2 (2504.08066) and Arbor (2606.11926), and the gap survey 2608.05179.
An old paper, arXiv:cs/0112017, is cited too. Kosmos again: 2511.02824.
Not ids: 2513.01234, 2500.01234, 1.2504.08067, 2504.080671 and 79.4%.

## Appendix A. Sources

| Role | Source | Used for |
|---|---|---|
| Reference system | 2511.02824 Kosmos | Scale; 79.4% & 57.9% accuracy |
| Considered, not compared | 2504.08066 AI Scientist-v2, 2606.11926 Arbor | Why the comparator set is these systems |
| Mechanism | 2511.02824 Kosmos | Second row loses |
"""

CITED = ["2511.02824", "2310.03714", "2507.01903", "2504.08066", "2606.11926", "2608.05179", "cs/0112017"]

KOSMOS = [("Summary", "Runs **12-hour** discovery with a `world model`. ⭐ Key point."),
          ("How it works (p2-4)", "- **Agents**: data analysis\n  - nested item\n- Second item <script>"),
          ("Results (p5)", "| Metric | Value |\n|---|---|\n| Accuracy | 79.4% |"),
          ("Limitations (stated)", "- Statement accuracy 57.9%"),
          ("Relevance", "- REPORT.md §4: scale"),
          ("Useful content", "Extra section text.")]

DSPY = [("Summary", "Compiles prompts."), ("Relevance", "- a use"), ("The taxonomy (p5)", "Extra B."),
        ("Critical notes", "- a caveat"), ("Results", "- a result"), ("How it works", "- a mechanism"),
        ("Tools", "Extra A.")]


def corpus(tmp_path, report=REPORT, index=True):
    papers = tmp_path / "papers"
    h.summary(papers, "2511.02824", "Kosmos", "Kosmos: An AI Scientist", KOSMOS,
              meta=("Mitchener · FutureHouse · arXiv 4 Nov 2025", "", "Read: p1-10 in `notes/29.md`"))
    h.summary(papers, "2310.03714", "DSPy", "DSPy", DSPY, sep=":")
    h.summary(papers, "2507.01903", "AI4Research survey", "AI4Research survey", h.simple_sections("S"), sep="-")
    h.summary(papers, "2504.08066", "AI Scientist-v2", "AI Scientist-v2", h.simple_sections("A"))
    h.summary(papers, "2606.11926", "Arbor", "Arbor", h.simple_sections("B"))
    h.summary(papers, "cs/0112017", "Old", "An old paper", h.simple_sections("O"))
    if index:
        h.write(papers / "summaries" / "INDEX.md", h.index_text([
            ("1. Frame and surveys", ["⭐ 2507.01903 AI4Research survey", "2608.05179 Verification gap survey"]),
            ("2. End-to-end AI scientists (report §4)", ["2511.02824 Kosmos", "2504.08066 AI Scientist-v2"]),
            ("New observations made while summarising", ["2606.11926 Arbor"]),
            ("3. Orchestration, DAGs and runtimes (report §3.3, §5)",
             ["† 2310.03714 DSPy", "2504.08066 AI Scientist-v2"]),
        ]))
    rep = h.write(tmp_path / "REPORT.md", report)
    return papers, rep


@pytest.fixture
def built(tmp_path):
    papers, rep = corpus(tmp_path)
    out = tmp_path / "site" / "paper-summaries.html"
    out.parent.mkdir()
    return (h.build(papers, rep, out),) + h.page(out)


def test_cited_ids_first_seen_order_versions_dropped(built):
    """§18.3: ids first-seen, deduplicated, version dropped, bad months/embedded numbers skipped; result shape."""
    res, _, _ = built
    assert res["cited"] == CITED
    assert set(res) >= {"out", "papers", "cited", "missing", "sections", "warnings"}
    assert isinstance(res["out"], str) and os.path.isfile(res["out"]) and isinstance(res["papers"], int)
    assert all(set(s) >= {"name", "id", "papers"} for s in res["sections"])


def test_old_style_needs_arxiv_prefix(tmp_path):
    """§18.3: an old-style id without `arXiv:`/`arXiv ` is not cited; `arXiv ` (space) form is."""
    papers, rep = corpus(tmp_path, report="See cs/0112017 and arXiv hep-th/9901001 and 2511.02824.\n")
    res = h.build(papers, rep, tmp_path / "o.html")
    assert res["cited"] == ["hep-th/9901001", "2511.02824"]


def test_missing_summary_listed_warned_and_noticed(built):
    """§18.3: a cited id with no summary gets no card, and is in `missing`, the notice and a warning."""
    res, _, root = built
    assert res["missing"] == ["2608.05179"]
    assert "no summary for 2608.05179" in res["warnings"]
    notice = root.find("div", id="missing")
    assert "notice" in notice.classes and "2608.05179" in notice.text()
    assert h.card(root, "2608.05179") is None
    assert len(h.articles(root)) == 6


def test_no_notice_when_nothing_missing(tmp_path):
    """§18.3: the notice appears only when some id is missing; papers equals the cited count."""
    papers, rep = corpus(tmp_path, report="Kosmos 2511.02824 and DSPy 2310.03714.\n")
    res = h.build(papers, rep, tmp_path / "o.html")
    _, root = h.page(tmp_path / "o.html")
    assert res["missing"] == [] and res["warnings"] == [] and res["papers"] == 2
    assert root.find(id="missing") is None
    assert root.find("p", cls="lede").clean() == "2 papers cited in REPORT.md, 1 card each, grouped as in the summary index."


def test_grouping_by_numbered_index_sections(built):
    """§18.3: numbered sections in INDEX order, trailing `(...)` removed, cited order within a group; a row after an
    unnumbered heading is not assigned; the first assignment wins; `Other` is last; nav links."""
    res, _, root = built
    assert h.groups(root) == [
        ("s-frame-and-surveys", "Frame and surveys", ["p-2507-01903"]),
        ("s-end-to-end-ai-scientists", "End-to-end AI scientists", ["p-2511-02824", "p-2504-08066"]),
        ("s-orchestration-dags-and-runtimes", "Orchestration, DAGs and runtimes", ["p-2310-03714"]),
        ("s-other", "Other", ["p-2606-11926", "p-cs-0112017"]),
    ]
    assert [(s["name"], s["id"]) for s in res["sections"]] == [(g[1], g[0]) for g in h.groups(root)]
    assert res["sections"][3]["papers"] == ["2606.11926", "cs/0112017"]
    links = root.find("div", cls="controls").find("nav").find_all("a")  # nav: `#s-{slug}` + span.n card count
    assert [a.attrs["href"] for a in links] == ["#" + g[0] for g in h.groups(root)]
    assert [a.find("span", cls="n").clean() for a in links] == ["1", "2", "1", "2"]
    assert links[1].clean() == "End-to-end AI scientists 2"


def test_missing_index_puts_everything_in_other(tmp_path):
    """§18.3: no INDEX.md is not an error: 1 group `Other`, and a warning `no index: {path}`."""
    papers, rep = corpus(tmp_path, index=False)
    res = h.build(papers, rep, tmp_path / "o.html")
    _, root = h.page(tmp_path / "o.html")
    assert [g[0] for g in h.groups(root)] == ["s-other"]
    assert any(w.startswith("no index: ") and "INDEX.md" in w for w in res["warnings"])


def test_card_heading_and_meta(built):
    """§18.3: h3 = span.id + heading without the `{id} ·` prefix; meta joins non-empty lines, inline code kept."""
    _, _, root = built
    art = h.card(root, "2511.02824")
    h3 = art.find("h3")
    assert h3.find("span", cls="id").clean() == "2511.02824"
    assert h3.clean() == "2511.02824 Kosmos: An AI Scientist"
    meta = art.find("p", cls="meta")
    assert meta.clean() == "Mitchener · FutureHouse · arXiv 4 Nov 2025 Read: p1-10 in notes/29.md"
    assert [c.clean() for c in meta.find_all("code")] == ["notes/29.md"]
    assert h.card(root, "2310.03714").find("h3").clean() == "2310.03714 DSPy"
    assert h.card(root, "2507.01903").find("h3").clean() == "2507.01903 AI4Research survey"


def test_in_the_report_line(built):
    """§18.3: `Used for` cell per id (comma-split cells, first occurrence wins); no line when unknown."""
    _, _, root = built
    eyebrow = lambda pid: [p.clean() for p in h.card(root, pid).find_all("p", cls="eyebrow")]  # noqa: E731
    assert eyebrow("2511.02824") == ["In the report: Scale; 79.4% & 57.9% accuracy"]
    assert eyebrow("2606.11926") == eyebrow("2504.08066") == ["In the report: Why the comparator set is these systems"]
    assert eyebrow("2310.03714") == []


def test_sections_order_and_open(built):
    """§18.3: div.summary, then details in canonical order (Critical notes = Limitations), then extras in file
    order; only Results is open."""
    _, _, root = built
    art = h.card(root, "2310.03714")
    assert len(art.find_all("div", cls="summary")) == 1
    assert h.details_labels(art) == [("How it works", False), ("Results", True), ("Critical notes", False),
                                     ("Relevance", False), ("The taxonomy (p5)", False), ("Tools", False)]
    assert h.details_labels(h.card(root, "2511.02824")) == [
        ("How it works (p2-4)", False), ("Results (p5)", True), ("Limitations (stated)", False),
        ("Relevance", False), ("Useful content", False)]


def test_block_markdown(built):
    """§18.3: strong/code inline, nested bullets, tables in div.tbl, escaped text, ⭐ removed."""
    _, raw, root = built
    art = h.card(root, "2511.02824")
    summ = art.find("div", cls="summary")
    assert [s.clean() for s in summ.find_all("strong")] == ["12-hour"]
    assert [c.clean() for c in summ.find_all("code")] == ["world model"]
    assert "world model. Key point." in summ.clean()
    how = art.kids("details")[0]
    assert any(li.find("ul") and "nested item" in li.find("ul").clean() for li in how.find("ul").kids("li"))
    assert "Second item <script>" in how.clean()
    table = art.kids("details")[1].find("div", cls="tbl").kids("table")[0]
    assert [c.clean() for c in table.find("thead").find_all("th")] == ["Metric", "Value"]
    assert [c.clean() for c in table.find("tbody").find_all("td")] == ["Accuracy", "79.4%"]
    assert "⭐" not in raw
    assert "&amp;" in raw and "<script>" not in raw.replace("<script>", "", 1)


def test_skeleton(built):
    """§18.3: doctype, html lang, charset, viewport, title, wrap > h1, controls with #q and #count."""
    _, raw, root = built
    assert raw.startswith("<!doctype html>")
    assert root.find("html").attrs.get("lang") == "en"
    metas = root.find("head").find_all("meta")
    assert any(m.attrs.get("charset", "").lower() == "utf-8" for m in metas)
    assert any(m.attrs.get("name") == "viewport" for m in metas)
    wrap = root.find("body").kids("div")[0]
    assert "wrap" in wrap.classes
    assert root.find("title").clean() == "Paper summaries" == wrap.find("h1").clean()
    assert root.find("input", id="q").attrs.get("type") == "search"
    assert "count" in root.find("span", id="count").classes


def test_self_contained(built):
    """§18.3: no <link>, no src, every href starts with `#`, 1 inline script; light/dark colour tokens."""
    _, raw, root = built
    assert root.find_all("link") == []
    assert all("src" not in e.attrs for e in root.elements())
    assert all(e.attrs["href"].startswith("#") for e in root.elements() if "href" in e.attrs)
    scripts = root.find_all("script")
    assert len(scripts) == 1 and scripts[0].text().strip()
    assert not re.search(r"url\(\s*['\"]?https?:|@import", raw)
    css = root.find("style").text()  # colour tokens on :root, redefined for dark (both forms)
    assert re.search(r":root\s*\{[^}]*--[\w-]+\s*:", css)
    assert "@media (prefers-color-scheme: dark)" in css
    assert ':root:not([data-theme="light"])' in css
    assert re.search(r':root\[data-theme="dark"\]\s*\{[^}]*--[\w-]+\s*:', css)


def test_deterministic_and_overwrites(tmp_path):
    """§18.3: identical inputs give byte-identical output; an existing out is overwritten; no temp files left."""
    papers, rep = corpus(tmp_path)
    out = h.write(tmp_path / "out" / "p.html", "stale")
    first = (h.build(papers, rep, out), out.read_bytes())[1]
    [os.utime(f, (1_000_000_000, 1_000_000_000)) for f in (papers / "summaries").iterdir()]
    h.build(papers, rep, out)
    assert out.read_bytes() == first
    assert os.listdir(out.parent) == ["p.html"]


def test_missing_inputs_and_cli(tmp_path, capsys):
    """§18.3/§0.4: missing report or dir → ToolError; the CLI exits 0 with warnings, 1 with --strict; --title."""
    papers, rep = corpus(tmp_path)
    for bad in ((papers, tmp_path / "nope.md"), (tmp_path / "nodir", rep)):
        with pytest.raises(h.tool_error()):
            h.build(*bad, tmp_path / "o.html")
    out = tmp_path / "p.html"
    code, data, _, _ = h.run_cli(capsys, ["papers", "page", rep, "-o", out, "--dir", papers,
                                          "--title", "Reading & notes", "--json"])
    assert code == 0 and data["missing"] == ["2608.05179"]
    raw, root = h.page(out)
    assert root.find("title").clean() == "Reading & notes" == root.find("h1").clean()
    assert "Reading &amp; notes" in raw
    code, _, _, _ = h.run_cli(capsys, ["papers", "page", rep, "-o", out, "--dir", papers, "--strict", "--json"])
    assert code == 1
