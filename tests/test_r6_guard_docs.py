"""Round 6: Office guard for Excel (MANIFEST §18.4), docs (§18.5) and registration (§18.6, §0.2, §0.4)."""
from __future__ import annotations

import inspect
import os
import re

import pytest

import helpers_r6g as h

try:  # captured before the per-test stub (tests/conftest.py) replaces it
    import tundlekit.render as _render
    ORIGINAL_OFFICE_RUNNING = _render.office_running
except Exception:  # collection must still succeed
    ORIGINAL_OFFICE_RUNNING = None


@pytest.fixture(autouse=True)
def _now(monkeypatch):
    monkeypatch.setenv("TUNDLEKIT_NOW", "2026-09-17T10:00")


# ------------------------------------------------------------------------------------ §18.4 guard
def test_apply_edits_xlsx_target_uses_all_apps_and_is_refused(tmp_path, monkeypatch):
    """§18.4: a `.xlsx` target → office_running(all_apps=True); with only EXCEL.EXE running it is refused."""
    calls = h.office_stub(monkeypatch, default=[], all_apps=["EXCEL.EXE"])
    x = h.write(tmp_path / "sheet.xlsx", "alpha\n")
    with pytest.raises(h.tool_error()):
        h.call("text_apply_edits", edits=[{"find": "alpha", "replace": "beta"}], path=x, write=True)
    assert calls and all(calls)
    assert x.read_text(encoding="utf-8") == "alpha\n"


def test_apply_edits_docx_target_uses_default(tmp_path, monkeypatch):
    """§18.4: a `.docx` target with only EXCEL.EXE running is not refused; the guard calls office_running()."""
    calls = h.office_stub(monkeypatch, default=[], all_apps=["EXCEL.EXE"])
    d = h.make_docx(tmp_path / "a.docx", ["Kept tools fail held-out tests."])
    res = h.call("text_apply_edits", edits=[{"find": "Kept", "replace": "Most"}], path=d, write=True)
    assert res["ok"] is True
    assert calls == [False]


def test_backup_xlsx_uses_all_apps(tmp_path, monkeypatch):
    """§18.4: bundle_backup of a `.xlsx` calls office_running(all_apps=True) and refuses, copying nothing."""
    calls = h.office_stub(monkeypatch, default=[], all_apps=["EXCEL.EXE"])
    x = h.write(tmp_path / "work" / "tests.xlsx", "PK sheet")
    with pytest.raises(h.tool_error()):
        h.call("bundle_backup", files=[x], reason="cut")
    assert calls and all(calls)
    versions = tmp_path / "work" / "versions"
    assert not versions.exists() or os.listdir(versions) == []


def test_backup_non_xlsx_still_guarded_with_default(tmp_path, monkeypatch):
    """§18.4: other file types use office_running() (still guarded); EXCEL.EXE alone does not block them."""
    calls = h.office_stub(monkeypatch, default=[], all_apps=["EXCEL.EXE"])
    m = h.write(tmp_path / "work" / "notes.md", "text")
    res = h.call("bundle_backup", files=[m], reason="cut")
    assert len(res["backups"]) == 1
    assert calls == [False]


def test_report_build_uses_default_guard(tmp_path, monkeypatch):
    """§18.4/§18.1: report_build writes .docx only, so it calls office_running() without all_apps."""
    calls = h.office_stub(monkeypatch, default=[], all_apps=["EXCEL.EXE"])
    rep = h.write(tmp_path / "REPORT.md", "# A report\n\nOne paragraph.\n")
    h.call("report_build", report=rep, out=tmp_path / "out.docx")
    assert calls == [False]
    assert (tmp_path / "out.docx").is_file()


def test_office_running_signature_kept():
    """§18.4: office_running(all_apps=False) keeps its signature."""
    assert ORIGINAL_OFFICE_RUNNING is not None
    param = inspect.signature(ORIGINAL_OFFICE_RUNNING).parameters["all_apps"]
    assert param.default is False


def test_apply_edits_xlsx_force_and_dry_run(tmp_path, monkeypatch):
    """§18.4/§17.1: a dry run is never guarded; force_office overrides the Excel refusal."""
    h.office_stub(monkeypatch, default=["EXCEL.EXE"], all_apps=["EXCEL.EXE"])
    x = h.write(tmp_path / "book.xlsx", "gamma\n")
    edit = [{"find": "gamma", "replace": "delta"}]
    assert h.call("text_apply_edits", edits=edit, path=x)["ok"] is True
    assert h.call("text_apply_edits", edits=edit, path=x, write=True, force_office=True)["ok"] is True
    assert x.read_text(encoding="utf-8") == "delta\n"


# ------------------------------------------------------------------------------------ §18.5 docs
def test_report_writing_reading_pages_section():
    """§18.5: report-writing has `## Reading pages` with source, helpers, inlining, xref and rebuild points."""
    sec = h.section(h.skill("report-writing"), "Reading pages")
    assert sec, "no `## Reading pages` section"
    for needle in ("annotated", "between(", "section(", "data:image/png;base64", "{{excerpt:",
                   "tundlekit text xref", "X002", "X003", "tundlekit papers page", "papers_page",
                   "tundlekit report build", "report_build"):
        assert needle in sec, needle


def test_deck_builder_scaffold_is_a_template():
    """§18.5/§11: deck-builder has `## Deck scaffold` with `source: Report §N` stubs and no scaffold command."""
    text = h.skill("deck-builder")
    sec = h.section(text, "Deck scaffold")
    assert sec, "no `## Deck scaffold` section"
    assert '"source": "Report §' in sec
    assert '"time"' in sec
    for needle in ("tundlekit deck lint", "tundlekit review coverage", "tundlekit deck pack", "--check"):
        assert needle in sec, needle
    assert "tundlekit deck scaffold" not in text
    assert "deck_pack" in text


def test_other_skills_mention_new_commands():
    """§18.5: deliverable-review has `report build` and `deck pack --check`; paper-reading has `papers page`."""
    review = h.skill("deliverable-review")
    assert "report build" in review
    assert "deck pack" in review and "--check" in review
    assert "papers page" in h.skill("paper-reading")


@pytest.mark.parametrize("doc", ["README.md", "AGENTS.md"])
def test_readme_and_agents_list_new_commands(doc):
    """§18.6/§12: README.md and AGENTS.md list the 3 new commands."""
    text = (h.REPO / doc).read_text(encoding="utf-8")
    for cmd in ("report build", "deck pack", "papers page"):
        assert cmd in text, cmd


# ------------------------------------------------------------------------------------ §18.6 registration
def test_modules_list():
    """§18.6: `report` goes after `claims`."""
    import tundlekit

    assert tundlekit.MODULES == ["bundle", "deck", "diagram", "chart", "palette", "textlint", "review", "claims",
                                 "report", "render", "papers", "translate"]


@pytest.mark.parametrize("name,props", [
    ("report_build", {"report", "out", "excerpts", "author", "overwrite", "force_office"}),
    ("deck_pack", {"pptx_path", "out", "force", "check"}),
    ("papers_page", {"report", "out", "dir", "index", "title"}),
])
def test_new_tools_registered(name, props):
    """§18.6/§0.2: registered, argument names as listed, readOnlyHint false, no destructiveHint."""
    from tundlekit import registry

    tools = registry.load_all()
    assert name in tools
    listing = tools[name].listing()
    schema = listing["inputSchema"]
    assert schema["type"] == "object" and schema["additionalProperties"] is False
    assert set(schema["properties"]) == props
    ann = listing.get("annotations", {})
    assert ann.get("readOnlyHint") is False
    assert not ann.get("destructiveHint")
    assert 0 < len(listing["description"]) <= 1024


def test_tools_listing_order(capsys):
    """§18.6: `tundlekit tools` lists report_build right after claims_trace."""
    code, data, _, _ = h.run_cli(capsys, ["tools", "--json"])
    assert code == 0
    names = [t["name"] for t in data["tools"]]
    assert names.index("report_build") == names.index("claims_trace") + 1


@pytest.mark.parametrize("argv", [["report", "build"], ["deck", "pack"], ["papers", "page"]])
def test_cli_commands_exist(argv, capsys):
    """§18.6: the 3 CLI commands exist (argparse help exits 0)."""
    code, _, out, _ = h.run_cli(capsys, argv + ["--help"])
    assert code == 0
    assert "--json" in out


@pytest.mark.parametrize("argv", [
    ["report", "build", "missing.md", "-o", "out.docx", "--excerpts", "ex", "--author", "A B", "--overwrite",
     "--force-office", "--json"],
    ["deck", "pack", "missing.pptx", "--check", "PACK.md", "--strict", "--json"],
    ["deck", "pack", "missing.pptx", "-o", "PACK.md", "--force", "--json"],
    ["papers", "page", "missing.md", "-o", "p.html", "--dir", ".", "--index", "I.md", "--title", "T", "--json"],
])
def test_cli_flags_accepted_missing_input_exits_1(argv, tmp_path, monkeypatch, capsys):
    """§18.6/§0.4: every listed flag parses (not exit 2); a missing input is a ToolError: exit 1 + {"error"}."""
    monkeypatch.chdir(tmp_path)
    code, data, _, err = h.run_cli(capsys, argv)
    assert code == 1, err
    assert isinstance(data, dict) and "error" in data


def test_pyproject_extras_unchanged():
    """§18.6/§12: pyproject keeps `office` = python-pptx + Pillow; no new required dependency."""
    text = (h.REPO / "pyproject.toml").read_text(encoding="utf-8")
    assert re.search(r'office\s*=\s*\[\s*"python-pptx"\s*,\s*"Pillow"\s*\]', text)
    m = re.search(r"^dependencies\s*=\s*\[(.*?)\]", text, re.M | re.S)
    assert m is None or m.group(1).strip() == ""
