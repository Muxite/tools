"""MANIFEST "16.6 pinned details": author marks end a title, case-insensitive Setup tokens, compact versions with
no architecture token, same-language compare for the first file of a script, and sub-term dedup in targets."""
from __future__ import annotations

import pytest

import helpers_r4m as h


def test_star_digit_author_marks_end_title(tmp_path):
    """16.6 pinned: `* 1` marks after names make an author line, which ends the title."""
    d = tmp_path / "papers"
    p1 = ("An LLM Compiler for Parallel Function Calling\n"
          "Sehoon Kim * 1 Suhong Moon * 1 Ryan Tabrizi 1\n"
          "Abstract\n")
    h.marker_txt(d / "2312.04511.txt", h.paper_pages(p1, 4))
    lines = h.summary_lines(h.call("papers_summary", id="2312.04511", dir=str(d)))
    assert lines[0] == "# 2312.04511 · An LLM Compiler for Parallel Function Calling"
    # §17.4: author marks are stripped from `authors`
    assert " ".join(lines[2].split()).startswith("Sehoon Kim Suhong Moon Ryan Tabrizi · arXiv 2312.04511")


@pytest.mark.parametrize("name,program,version", [
    ("tailscale-setup-1.102.4.exe", "tailscale", "1.102.4"),
    ("7z2409.exe", "7z", "24.09"),
])
def test_pinned_name_guesses(tmp_path, name, program, version):
    """16.6 pinned: a lower-case `setup` word is removed once a version is found; a compact version may follow
    the program directly."""
    res = h.call("bundle_source", file=str(h.installer(tmp_path / name)))
    assert (res["program"], res["version"]) == (program, version)


def terms(tmp_path, src, *targets, **kw):
    s = h.write(tmp_path / "src.md", src)
    ts = [h.write(tmp_path / f"t{i}.md", t) for i, t in enumerate(targets)]
    res = h.call("translate_terms", src=str(s), targets=[str(t) for t in ts], **kw)
    h.check_shape(res)
    return res


def test_same_language_first_of_script_is_silent(tmp_path):
    """16.6 pinned: with same-language, the first CJK file has no earlier CJK file, so it gets no findings
    (with `previous` it gets L001 for the dropped term)."""
    src = "The PlanGraph orders work.\n"
    zh = "计划图安排工作。\n"
    res = terms(tmp_path, src, zh)
    assert [f["rule"] for f in res["findings"]] == ["L001"]
    res = terms(tmp_path, src, zh, compare="same-language")
    assert res["findings"] == []


def test_sub_term_dedup_in_targets(tmp_path):
    """16.6 pinned: in a target, `IDs` inside `acceptance IDs` is not counted, so an English target with the same
    two uses keeps the counts and gives no L002."""
    res = terms(tmp_path, "IDs 很重要。每条都有 acceptance IDs 用于追踪\n",
                "IDs matter. Each item has acceptance IDs for tracing.\n")
    assert h.term_count(res, "IDs", 0) == 1
    assert h.term_count(res, "IDs", 1) == 1
    assert h.term_count(res, "acceptance IDs", 1) == 1
    assert res["findings"] == []
