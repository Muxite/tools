"""MANIFEST §15.6 `translate_terms` / `tundlekit translate terms SRC TGT [TGT...]`, §15.10 registration.

The zh source mirrors tundle's translation round-trip fixtures (notes/overnight/translation): Chinese prose
with Latin technical terms written directly against CJK characters.
"""
from __future__ import annotations

import pytest

import helpers_r3 as r3

ZH = (
    "# 架构说明\n"
    "\n"
    "我们把capability capsule交给Execution Broker执行，并通过MCP协议调用工具。\n"
    "每个capability capsule都有一个版本号，Execution Broker只租用一次。\n"
)

EN_KEEP = (
    "# Architecture\n"
    "\n"
    "We hand each capability capsule to the Execution Broker, and call tools over the MCP protocol.\n"
    "Every capability capsule has a version; the Execution Broker leases it once.\n"
)

EN_DROP = (
    "# Architecture\n"
    "\n"
    "We hand each capsule to the Execution Broker, and call tools over the MCP protocol.\n"
    "Every capsule has a version; the Execution Broker leases it once.\n"
)


def terms(src, targets):
    res = r3.call("translate_terms", src=str(src), targets=[str(t) for t in targets])
    r3.check_shape(res)
    assert isinstance(res["terms"], dict)
    for counts in res["terms"].values():
        assert len(counts) == 1 + len(targets)
    return res


def counts(res, term):
    """Counts for a term; keys are written as they first appear in SRC (§15.6)."""
    assert term in res["terms"], (term, sorted(res["terms"]))
    return res["terms"][term]


def test_registered_in_translate_read_only():
    """§15.10: translate_terms is registered by tundlekit.translate and is read-only."""
    t = r3.get_tool("translate_terms")
    assert t.annotations.get("readOnlyHint") is True
    assert t.input_schema.get("additionalProperties") is False
    assert {"src", "targets"} <= set(t.input_schema["properties"])


def test_terms_found_in_zh_source(tmp_path):
    """§15.6: Latin word runs between CJK letters and all-capital words are terms (ASCII classes, so `MCP协议`
    gives `MCP`), counted per file; keys are as first seen in SRC."""
    src = r3.write(tmp_path / "zh.md", ZH)
    tgt = r3.write(tmp_path / "en.md", EN_KEEP)
    res = terms(src, [tgt])
    assert set(res["terms"]) == {"capability capsule", "Execution Broker", "MCP"}
    assert counts(res, "capability capsule") == [2, 2]
    assert counts(res, "Execution Broker") == [2, 2]
    assert counts(res, "MCP") == [1, 1]


def test_terms_kept_no_findings(tmp_path):
    """§15.6: no L001/L002 when every count carries over unchanged."""
    src = r3.write(tmp_path / "zh.md", ZH)
    tgt = r3.write(tmp_path / "en.md", EN_KEEP)
    res = terms(src, [tgt])
    assert res["findings"] == []
    assert res["ok"] is True


def test_dropped_term_is_l001(tmp_path, monkeypatch):
    """§15.6: L001 (warning) for a term present before and absent now, on the target path; §17.5: `line` is the
    term's first line in the compared file (zh.md line 3)."""
    monkeypatch.chdir(tmp_path)
    r3.write(tmp_path / "zh.md", ZH)
    r3.write(tmp_path / "en.md", EN_DROP)
    res = terms("zh.md", ["en.md"])
    l001 = r3.by_rule(res, "L001")
    assert len(l001) == 1
    f = l001[0]
    assert f["severity"] == "warning"
    assert f["path"] == "en.md"
    assert f["line"] == 3  # §17.5 (was null under §15.6)
    assert "capability capsule" in f["message"].lower()
    assert counts(res, "capability capsule") == [2, 0]
    assert res["ok"] is True


def test_changed_count_is_l002(tmp_path):
    """§15.6: L002 (info) when a count changes and neither count is 0."""
    src = r3.write(tmp_path / "zh.md", ZH)
    tgt = r3.write(tmp_path / "en.md", EN_KEEP.replace("the Execution Broker leases", "it leases"))
    res = terms(src, [tgt])
    assert counts(res, "Execution Broker") == [2, 1]
    l002 = r3.by_rule(res, "L002")
    assert len(l002) == 1
    assert l002[0]["severity"] == "info"
    assert "execution broker" in l002[0]["message"].lower()
    assert r3.by_rule(res, "L001") == []


def test_each_target_compared_with_previous(tmp_path, monkeypatch):
    """§15.6: target 2 is compared with target 1, not with SRC."""
    monkeypatch.chdir(tmp_path)
    r3.write(tmp_path / "zh0.md", ZH)
    r3.write(tmp_path / "en1.md", EN_DROP)                 # drops the term: L001 on en1.md
    r3.write(tmp_path / "zh2.md", ZH.replace("capability capsule", "能力胶囊"))  # still 0: no finding
    res = terms("zh0.md", ["en1.md", "zh2.md"])
    assert counts(res, "capability capsule") == [2, 0, 0]
    assert [(f["rule"], f["path"]) for f in res["findings"]] == [("L001", "en1.md")]


def test_inline_code_and_urls_excluded(tmp_path):
    """§15.6: inline code, URLs and file paths are not terms."""
    src = r3.write(tmp_path / "zh.md",
                   "运行`ToolRegistry`命令。\n"
                   "见 https://example.com/DataLoader 页面。\n"
                   "以及 tools/PlanCompiler.py 文件。\n"
                   "我们使用MCP协议。\n")
    tgt = r3.write(tmp_path / "en.md", "Run the command; we use the MCP protocol.\n")
    res = terms(src, [tgt])
    assert set(res["terms"]) == {"MCP"}
    assert counts(res, "MCP") == [1, 1]


def test_camel_case_terms(tmp_path):
    """§15.6: CamelCase words (`[A-Z][a-z]+[A-Z]\\w*` or `[a-z]+[A-Z]\\w*`) are terms."""
    src = r3.write(tmp_path / "zh.md", "调度器使用TaskGraph，并调用planRepair函数。\n")
    tgt = r3.write(tmp_path / "en.md", "The scheduler uses the TaskGraph and calls a repair function.\n")
    res = terms(src, [tgt])
    assert set(res["terms"]) == {"TaskGraph", "planRepair"}
    assert counts(res, "TaskGraph") == [1, 1]
    assert counts(res, "planRepair") == [1, 0]
    assert [f["rule"] for f in res["findings"]] == ["L001"]


def test_cli_translate_terms(tmp_path, capsys):
    """§15.10/§0.4: `tundlekit translate terms SRC TGT --json`; warnings exit 0, and 1 with --strict."""
    src = r3.write(tmp_path / "zh.md", ZH)
    tgt = r3.write(tmp_path / "en.md", EN_DROP)
    code, data, out, err = r3.run_cli(capsys, ["translate", "terms", src, tgt, "--json"])
    assert code == 0, err
    assert [f["rule"] for f in data["findings"]] == ["L001"]
    code, data, out, err = r3.run_cli(capsys, ["translate", "terms", src, tgt, "--json", "--strict"])
    assert code == 1
