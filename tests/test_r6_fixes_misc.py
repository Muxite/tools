"""Round 6 fixes: device names and output paths (MANIFEST §19.3), text_xref renumbering (§19.5) and the
translate_terms `compared` location (§19.8), on top of §0.2, §0.4, §15.2, §17.2, §17.5 and §17.6."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

import helpers_r6f as h
from helpers_r3 import content

SPEC = {"nodes": [{"id": "a", "label": "Plan"}, {"id": "b", "label": "Run"}], "edges": [{"from": "a", "to": "b"}]}
CHART = {"categories": ["kept", "retired"], "values": [3, 1]}


@pytest.fixture
def work(tmp_path, monkeypatch):
    d = tmp_path / "work"
    d.mkdir()
    monkeypatch.chdir(d)
    return d


# ------------------------------------------------------------------------------------ §19.3 device names
DEVICE_CASES = [
    ("diagram_render", {"spec": SPEC, "out": "CON.png"}),
    ("diagram_render", {"spec": SPEC, "out": "NUL.svg"}),
    ("chart_bar", {"spec": CHART, "out": "AUX.svg"}),
    ("render_contact_sheet", {"images": ["missing.png"], "out_dir": "PRN"}),
    ("render_pdf", {"pdf": "missing.pdf", "out_dir": "LPT1"}),
]


def test_device_name_outputs_refused(work):
    """§19.3 reviewers' repro: device names (any extension) in output arguments are a ToolError on Windows;
    nothing is created in the current directory."""
    h.skip_unless_windows()
    for tool, args in DEVICE_CASES:
        with pytest.raises(h.tool_error()):
            h.call(tool, **args)
            pytest.fail(f"{tool} accepted {args}")
        assert h.listing(work) == [], (tool, args)


def test_deck_build_device_name_refused(work):
    """§19.3: deck_build out=COM1.pptx."""
    h.skip_unless_windows()
    pytest.importorskip("pptx")
    with pytest.raises(h.tool_error()):
        h.call("deck_build", spec={"meta": {"id": "dev"}, "slides": [content("Kept tools fail held-out tests")]},
               out="COM1.pptx")
    assert h.listing(work) == []


def test_render_office_device_dir_refused(work, tmp_path):
    """§19.3: render_office output dir CON."""
    h.skip_unless_windows()
    src = h.make_docx(tmp_path / "in" / "a.docx", ["Hello there"])
    with pytest.raises(h.tool_error()):
        h.call("render_office", src=str(src), out_dir="CON", backend="text")
    assert h.listing(work) == []


def test_emit_edits_device_name_refused(work, tmp_path):
    """§19.3: docx_diff emit_edits=NUL.json."""
    h.skip_unless_windows()
    a = h.write(tmp_path / "in" / "a.md", "Kept tools fail held-out tests.\n")
    b = h.write(tmp_path / "in" / "b.md", "Kept tools pass held-out tests.\n")
    with pytest.raises(h.tool_error()):
        h.docx_diff(a, b, emit_edits="NUL.json")
    assert h.listing(work) == []


def test_cli_stdout_output_writes_no_file(work, tmp_path, capsys):
    """§19.3: without -o, `diagram render` and `chart bar` print to stdout and write nothing."""
    import json

    spec = h.write(tmp_path / "in" / "d.json", json.dumps(SPEC))
    chart = h.write(tmp_path / "in" / "c.json", json.dumps(CHART))
    code, data, out, err = h.run_cli(capsys, ["diagram", "render", spec, "--json"])
    assert code == 0, err
    assert data["svg"].lstrip().startswith("<")
    code, data, out, err = h.run_cli(capsys, ["chart", "bar", chart, "--json"])
    assert code == 0, err
    assert h.listing(work) == []
    assert sorted(os.listdir(tmp_path / "in")) == ["c.json", "d.json"]


# ------------------------------------------------------------------------------------ §19.5 renumbering
A = "# Alpha Report\n\n## 4. Design\n\n### 4.2 Gates decide\n"
B = "# Beta Report\n\n## 3. Evaluation\n\n### 3.1 Runs\n"
SHARED = 'NOTE = "Design in §4.2, runs in §3.1"\n'


def test_shared_file_renumbered_for_every_report(work):
    """§19.5 reviewers' repro: `files=["shared.py=A", "shared.py=B"]` gets both reports' renumbering, whatever
    the argument order."""
    for order in (["a", "b"], ["b", "a"]):
        h.write(work / "a" / "REPORT.md", A)
        h.write(work / "b" / "REPORT.md", B)
        h.write(work / "shared.py", SHARED)
        files = [f"shared.py={x}/REPORT.md" for x in order]
        h.xref(files=files, renumber=["§4.2=§4.3", "§3.1=§3.2"], write=True)
        assert h.read(work / "shared.py") == 'NOTE = "Design in §4.3, runs in §3.2"\n', order
        assert "### 4.3 Gates decide" in h.read(work / "a" / "REPORT.md")
        assert "### 3.2 Runs" in h.read(work / "b" / "REPORT.md")


FIGS = "# Report\n\n## 1. Intro\n\nSee Fig. 1 and Fig. 2.\n\n*Fig. 1. One.*\n\n*Fig. 2. Two.*\n"


def test_two_sources_onto_one_target_refused(work):
    """§19.5: `Fig. 1=Fig. 3` with `Fig. 2=Fig. 3` is a ToolError; nothing is written."""
    h.write(work / "REPORT.md", FIGS)
    h.write(work / "deck.md", "Fig. 1 then Fig. 2\n")
    with pytest.raises(h.tool_error()):
        h.xref(files=["deck.md=REPORT.md"], renumber=["Fig. 1=Fig. 3", "Fig. 2=Fig. 3"], write=True)
    assert h.read(work / "REPORT.md") == FIGS
    assert h.read(work / "deck.md") == "Fig. 1 then Fig. 2\n"


APPX = ("# Report\n\n## 1. Intro\n\nSee App. E.4.\n\n## Appendix E. Extra runs\n\n### E.4 Detail\n\n"
        "### E.5 More\n")


def test_letter_rename_with_subsection_renumber_refused(work):
    """§19.5: renaming App. E and renumbering App. E.4 in one call is a ToolError; nothing is written."""
    h.write(work / "REPORT.md", APPX)
    h.write(work / "notes.md", "App. E.4 matters.\n")
    with pytest.raises(h.tool_error()):
        h.xref(files=["notes.md=REPORT.md"], renumber=["App. E=App. D", "App. E.4=App. E.6"], write=True)
    assert h.read(work / "REPORT.md") == APPX
    assert h.read(work / "notes.md") == "App. E.4 matters.\n"


# ------------------------------------------------------------------------------------ §19.8 compared
def _terms(tmp_path, src, *targets, **kw):
    s = h.write(Path(tmp_path) / "src.md", src)
    ts = [h.write(Path(tmp_path) / f"t{i}.md", t) for i, t in enumerate(targets)]
    res = h.call("translate_terms", src=str(s), targets=[str(t) for t in ts], **kw)
    h.check_shape(res)
    return res


def _name(path) -> str:
    return os.path.basename(path.replace("\\", "/"))


def test_l_findings_name_the_compared_file(tmp_path):
    """§19.8: each L finding carries `compared`, the file whose line is given (SRC for the first target, the
    previous target after that)."""
    src = "RetryBudget 很重要。\n"
    t0 = "Intro.\n\nMore.\nThe RetryBudget matters.\nRetryBudget again.\n"
    t1 = "RetryBudget 一次。\n"
    res = _terms(tmp_path, src, t0, t1)
    got = sorted((_name(f["path"]), _name(f["compared"]), f["line"]) for f in res["findings"]
                 if f["rule"] == "L002")
    assert got == [("t0.md", "src.md", 1), ("t1.md", "t0.md", 4)]


def test_every_l_finding_has_compared(tmp_path):
    """§19.8: no L001/L002/L003 finding lacks `compared`; it is never the finding's own file."""
    res = _terms(tmp_path, "The Gateway uses the UI and RetryBudget.\n", "界面 显示 状态。\n", "Nothing.\n")
    assert res["findings"]
    for f in res["findings"]:
        assert isinstance(f.get("compared"), str) and f["compared"], f
        assert _name(f["compared"]) != _name(f["path"])
