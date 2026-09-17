"""MANIFEST §15.8 `papers_summary` and `papers_index_check`, with §9 text formats; §15.10 registration.

Page 1 of the fixture papers follows the real tundle paper texts (ai4research/papers/*.txt): a title line,
then an author line. Summary files follow ai4research/papers/summaries (INDEX.md and `{id} - {short}.md`).
"""
from __future__ import annotations

import pytest

import helpers_r3 as r3

LLMC_P1 = ("An LLM Compiler for Parallel Function Calling\n"
           "Sehoon Kim * 1 Suhong Moon * 1 Ryan Tabrizi 1 Nicholas Lee 1\n"
           "Abstract\n"
           "The reasoning capabilities of the recent LLMs\n")
LLMC_TITLE = "An LLM Compiler for Parallel Function Calling"
LLMC_AUTHORS = "Sehoon Kim Suhong Moon Ryan Tabrizi Nicholas Lee"  # §17.4: marks stripped (whitespace collapsed)

AFLOW_P1 = ("\n"
            "AFLOW: AUTOMATING AGENTIC WORKFLOW GENERATION\n"
            "Jiayi Zhang, Jinyu Xiang, Zhaoyang Yu\n"
            "ABSTRACT\n"
            "We present AFLOW, a framework for workflow search.\n")  # §17.4: AFLOW stays an acronym


def papers_dir(tmp_path):
    d = tmp_path / "papers"
    d.mkdir()
    return d


def summary(**kw):
    res = r3.call("papers_summary", **{k: (str(v) if k == "dir" else v) for k, v in kw.items()})
    assert set(res) >= {"path", "text", "written"}
    return res


@pytest.mark.parametrize("name,read_only", [("papers_summary", False), ("papers_index_check", True)])
def test_registered_in_papers(name, read_only):
    """§15.10: registered by tundlekit.papers; papers_index_check is read-only, papers_summary is not."""
    t = r3.get_tool(name)
    assert (t.annotations.get("readOnlyHint") is True) is read_only
    assert t.input_schema.get("additionalProperties") is False


def test_summary_dry_run_text(tmp_path):
    """§15.8: the skeleton text; title = first page-1 line with >3 words, authors = next line,
    body = references page - 1 (§9.2)."""
    d = papers_dir(tmp_path)
    r3.marker_txt(d / "2312.04511.txt", r3.paper_pages(LLMC_P1, 12, refs_page=10))
    res = summary(id="2312.04511", dir=d)
    assert res["written"] is False
    assert r3.norm_text(res["text"]) == r3.skeleton("2312.04511", LLMC_TITLE, LLMC_AUTHORS, 12, 9)
    assert not (d / "summaries").exists()


def test_summary_default_short_and_write(tmp_path):
    """§15.8: the default short name is the title before the first `:`, and write creates summaries/."""
    d = papers_dir(tmp_path)
    r3.marker_txt(d / "2410.10762.txt", r3.paper_pages(AFLOW_P1, 6, refs_page=5))
    res = summary(id="2410.10762", dir=d, write=True)
    assert res["written"] is True
    target = d / "summaries" / "2410.10762 - AFLOW.md"
    assert target.is_file()
    assert r3.slash(res["path"]).endswith("summaries/2410.10762 - AFLOW.md")
    assert r3.norm_text(target.read_text(encoding="utf-8")) == r3.skeleton(
        "2410.10762", "AFLOW: Automating Agentic Workflow Generation", "Jiayi Zhang, Jinyu Xiang, Zhaoyang Yu", 6, 4)


def test_summary_default_short_truncated_to_40(tmp_path):
    """§15.8: with no `:`, the whole title truncated to 40 characters, then trimmed."""
    d = papers_dir(tmp_path)
    r3.marker_txt(d / "2312.04511.txt", r3.paper_pages(LLMC_P1, 4))
    res = summary(id="2312.04511", dir=d)
    assert r3.slash(res["path"]).endswith("summaries/2312.04511 - An LLM Compiler for Parallel Function Ca.md")


def test_summary_wrapped_title(tmp_path):
    """§15.8: a title line joins the following lines that start lower-case; authors is the line after them."""
    d = papers_dir(tmp_path)
    p1 = ("Towards effective extraction and evaluation\n"
          "of factual claims\n"
          "Dasha Metropolitansky, Jonathan Larson\n"
          "Abstract\n")
    r3.marker_txt(d / "2502.10855.txt", r3.paper_pages(p1, 9, refs_page=8))
    res = summary(id="2502.10855", dir=d)
    assert r3.norm_text(res["text"]) == r3.skeleton(
        "2502.10855", "Towards effective extraction and evaluation of factual claims",
        "Dasha Metropolitansky, Jonathan Larson", 9, 7)
    assert r3.slash(res["path"]).endswith("summaries/2502.10855 - Towards effective extraction and evaluat.md")


def test_summary_explicit_short(tmp_path):
    """§15.8: `short` names the file."""
    d = papers_dir(tmp_path)
    r3.marker_txt(d / "2312.04511.txt", r3.paper_pages(LLMC_P1, 4))
    res = summary(id="2312.04511", dir=d, short="LLMCompiler", write=True)
    assert (d / "summaries" / "2312.04511 - LLMCompiler.md").is_file()
    assert res["written"] is True


def test_summary_no_references_page(tmp_path):
    """§15.8: body is the page count when there is no references page."""
    d = papers_dir(tmp_path)
    r3.marker_txt(d / "2312.04511.txt", r3.paper_pages(LLMC_P1, 7))
    res = summary(id="2312.04511", dir=d)
    assert r3.norm_text(res["text"]).split("\n")[2] == f"{LLMC_AUTHORS} · arXiv 2312.04511 · 7 pp (7 body)"


def test_summary_refuses_overwrite(tmp_path):
    """§15.8: it refuses to overwrite an existing summary."""
    d = papers_dir(tmp_path)
    r3.marker_txt(d / "2312.04511.txt", r3.paper_pages(LLMC_P1, 4))
    existing = r3.write(d / "summaries" / "2312.04511 - LLMCompiler.md", "# kept\n")
    with pytest.raises(r3.tool_error()):
        summary(id="2312.04511", dir=d, short="LLMCompiler", write=True)
    assert existing.read_text(encoding="utf-8") == "# kept\n"


def test_summary_missing_text_is_error(tmp_path):
    """§15.8: a missing text file is a ToolError."""
    d = papers_dir(tmp_path)
    (d / "2312.04511.pdf").write_bytes(b"%PDF-1.4\n")
    with pytest.raises(r3.tool_error()):
        summary(id="2312.04511", dir=d, write=True)
    assert not (d / "summaries").exists()


def test_cli_papers_summary(tmp_path, capsys):
    """§15.10: `tundlekit papers summary ID --dir D --short NAME --json`."""
    d = papers_dir(tmp_path)
    r3.marker_txt(d / "2312.04511.txt", r3.paper_pages(LLMC_P1, 4))
    code, data, out, err = r3.run_cli(capsys, ["papers", "summary", "2312.04511", "--dir", d,
                                               "--short", "LLMCompiler", "--json"])
    assert code == 0, err
    assert data["written"] is False
    assert data["text"].startswith("# 2312.04511 · " + LLMC_TITLE)


# ------------------------------------------------------------------------------------ index check

INDEX = """# Paper summaries: index

{n} summaries, one per paper text in `papers/`.

## 1. Frame and surveys
| Paper | One line |
|---|---|
| 2310.03714 DSPy | Compiles declarative LM calls |
| 2312.04511 LLMCompiler | Plans parallel function calls |
"""


def index_tree(tmp_path, n=2):
    d = papers_dir(tmp_path)
    for pid in ("2310.03714", "2312.04511"):
        r3.marker_txt(d / f"{pid}.txt", r3.paper_pages(LLMC_P1, 4))
    r3.summary_file(d, "2310.03714", "DSPy")
    r3.summary_file(d, "2312.04511", "LLMCompiler")
    r3.write(d / "summaries" / "INDEX.md", INDEX.format(n=n))
    return d


def check(d, **kw):
    res = r3.call("papers_index_check", dir=str(d), **kw)
    r3.check_shape(res)
    return res


def test_index_clean(tmp_path):
    """§15.8: a consistent folder has no findings; `papers` and `summaries` are counts."""
    res = check(index_tree(tmp_path))
    assert res["findings"] == []
    assert res["ok"] is True
    assert res["papers"] == 2
    assert res["summaries"] == 2


def test_p001_paper_without_summary(tmp_path):
    """§15.8 P001: a paper with no summary file."""
    d = index_tree(tmp_path)
    r3.marker_txt(d / "2504.01848.txt", r3.paper_pages(LLMC_P1, 4))
    res = check(d)
    p001 = r3.by_rule(res, "P001")
    assert len(p001) == 1
    assert p001[0]["severity"] == "warning"
    assert "2504.01848" in p001[0]["message"] + p001[0]["path"]
    assert res["papers"] == 3
    assert [f["rule"] for f in res["findings"]] == ["P001"]


def test_p002_summary_not_in_index(tmp_path):
    """§15.8 P002: a summary file whose id INDEX.md never mentions."""
    d = index_tree(tmp_path, n=3)
    r3.marker_txt(d / "2411.04468.txt", r3.paper_pages(LLMC_P1, 4))
    r3.summary_file(d, "2411.04468", "Magentic-One")
    res = check(d)
    p002 = r3.by_rule(res, "P002")
    assert len(p002) == 1
    assert "2411.04468" in p002[0]["message"] + p002[0]["path"]
    assert [f["rule"] for f in res["findings"]] == ["P002"]


def test_p003_count_mismatch(tmp_path):
    """§15.8 P003: INDEX.md states `N summaries` that differs from the summary file count."""
    res = check(index_tree(tmp_path, n=59))
    assert [f["rule"] for f in res["findings"]] == ["P003"]
    assert res["findings"][0]["severity"] == "warning"


def test_p004_missing_heading(tmp_path):
    """§15.8 P004: a summary without `## Limitations`; `## How it works (p2-4)` counts as a heading."""
    d = index_tree(tmp_path)
    r3.summary_file(d, "2312.04511", "LLMCompiler",
                    body="## Summary\nx\n\n## How it works (p3-5)\n- a\n\n## Results (p1-2)\n- b\n\n## Relevance\nc\n")
    res = check(d)
    p004 = r3.by_rule(res, "P004")
    assert len(p004) == 1
    assert "2312.04511" in p004[0]["message"] + p004[0]["path"]
    assert [f["rule"] for f in res["findings"]] == ["P004"]


def test_p005_report_citation_without_summary(tmp_path):
    """§15.8 P005: with `report`, an arXiv id cited in its references with no summary."""
    d = index_tree(tmp_path)
    report = r3.write(tmp_path / "report.md",
                      "# Report\n\n## 1. Intro\n\nText [1].\n\n## References\n\n"
                      "[1] DSPy: Compiling Declarative Language Model Calls. arXiv:2310.03714.\n"
                      "[2] Beyond Task Completion. arXiv 2604.00392.\n")
    res = check(d, report=str(report))
    p005 = r3.by_rule(res, "P005")
    assert len(p005) == 1
    assert "2604.00392" in p005[0]["message"]
    assert "2310.03714" not in p005[0]["message"]


def test_cli_index_check(tmp_path, capsys):
    """§15.10/§0.4: `tundlekit papers index-check --dir D --json`; warnings exit 0, --strict exits 1."""
    d = index_tree(tmp_path, n=7)
    code, data, out, err = r3.run_cli(capsys, ["papers", "index-check", "--dir", d, "--json"])
    assert code == 0, err
    assert [f["rule"] for f in data["findings"]] == ["P003"]
    code, data, out, err = r3.run_cli(capsys, ["papers", "index-check", "--dir", d, "--json", "--strict"])
    assert code == 1
