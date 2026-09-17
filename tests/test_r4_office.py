"""Round-4: defensive .pptx reading, directory errors and broken pipes (MANIFEST §16.1), and the §16.7
`office_check` tool and integral floats."""
from __future__ import annotations

import sys
import time

import pytest

import helpers_r4 as h

SLIDES = [("Kept tools fail held-out tests", "Body text one", "TIME 0:30\nSAY: first notes"),
          ("Gates decide what enters", "Body text two", "TIME 0:20\nSAY: second notes")]


# ---------------------------------------------------------------- defensive .pptx reading (§16.1)
@pytest.fixture
def no_notes_ph(tmp_path):
    p = h.make_pptx(tmp_path / "nonotes.pptx", SLIDES)
    return h.rewrite_parts(p, h.drop_notes_placeholder, r"ppt/notesSlides/notesSlide1\.xml")


@pytest.fixture
def no_geom(tmp_path):
    p = h.make_pptx(tmp_path / "nogeom.pptx", SLIDES)
    return h.rewrite_parts(p, h.drop_geometry, r"ppt/slides/slide\d+\.xml")


def test_inspect_notes_slide_without_placeholder(no_notes_ph):
    """§16.1: a notes slide without a notes placeholder counts as empty notes."""
    res = h.call("deck_inspect", pptx_path=no_notes_ph)
    assert res["slides"][0]["notes"] == ""
    assert "second notes" in res["slides"][1]["notes"]
    assert any("Body text one" in t for t in res["slides"][0]["texts"])


def test_inspect_shape_without_geometry_keeps_text(no_geom):
    """§16.1: a shape without recognised geometry is skipped for geometry, but its text is still read."""
    res = h.call("deck_inspect", pptx_path=no_geom)
    assert any("Body text one" in t for t in res["slides"][0]["texts"])
    assert any("Body text two" in t for t in res["slides"][1]["texts"])


@pytest.mark.parametrize("which", ["no_notes_ph", "no_geom"])
def test_lint_odd_pptx_does_not_crash(request, which):
    """§16.1: deck_lint reads such decks as ordinary content (checker shape, no crash)."""
    res = h.call("deck_lint", pptx_path=request.getfixturevalue(which))
    assert isinstance(res["ok"], bool)
    assert set(res["counts"]) >= {"error", "warning", "info"}


def test_diff_against_odd_pptx(tmp_path, no_notes_ph, no_geom):
    """§16.1: deck_diff handles both oddities; a dropped notes placeholder reads as emptied notes."""
    plain = h.make_pptx(tmp_path / "plain.pptx", SLIDES)
    res = h.call("deck_diff", old=plain, new=no_notes_ph)
    notes = [c for c in res["changes"] if c["field"] == "notes"]
    assert len(notes) == 1 and "first notes" in notes[0]["old"]
    res = h.call("deck_diff", old=plain, new=no_geom)
    assert [c for c in res["changes"] if c["field"] == "text"] == []


def test_render_text_backend_odd_pptx(tmp_path, no_notes_ph, no_geom):
    """§16.1: render_office text backend writes slide text for both oddities."""
    for i, src in enumerate((no_notes_ph, no_geom)):
        out = tmp_path / f"render{i}"
        res = h.call("render_office", src=src, out_dir=out, backend="text")
        assert res["backend"] == "text"
        slide1 = (out / "slide-01.txt").read_text(encoding="utf-8")
        assert "Body text one" in slide1
        if src is no_notes_ph and (out / "notes-01.txt").exists():
            assert (out / "notes-01.txt").read_text(encoding="utf-8").strip() == ""


# ---------------------------------------------------------------- directory errors (§16.1)
def test_papers_summary_with_summaries_file(tmp_path):
    """§16.1: `{dir}/summaries` being a file is a ToolError that says so."""
    h.paper_txt(tmp_path / "2401.01234.txt", [h.PAGE1, "Body.\n"])
    blocker = h.write(tmp_path / "summaries", "not a directory\n")
    with pytest.raises(h.tool_error()) as exc:
        h.call("papers_summary", id="2401.01234", dir=tmp_path, write=True)
    assert "summaries" in str(exc.value)
    assert blocker.read_text(encoding="utf-8") == "not a directory\n"


def test_diagram_png_failure_creates_no_parent(tmp_path, monkeypatch):
    """§16.1: diagram_render creates the PNG's parent directory only after a converter succeeds."""
    import types

    fake = types.ModuleType("cairosvg")

    def boom(*a, **k):
        raise RuntimeError("converter failed")

    fake.svg2png = boom
    monkeypatch.setitem(sys.modules, "cairosvg", fake)
    monkeypatch.setitem(sys.modules, "pymupdf", None)
    monkeypatch.setitem(sys.modules, "fitz", None)
    monkeypatch.setenv("PATH", "")
    png = tmp_path / "newdir" / "deeper" / "d.png"
    spec = {"nodes": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}], "edges": [{"from": "a", "to": "b"}]}
    with pytest.raises(h.tool_error()):
        h.call("diagram_render", spec=spec, png=png)
    assert not (tmp_path / "newdir").exists()


# ---------------------------------------------------------------- broken pipes (§16.1)
def test_cli_broken_pipe_is_quiet():
    """§16.1: a broken stdout pipe gives no traceback and exit 0."""
    code, err = h.run_into_closed_pipe(["tools", "--json"])
    assert "Traceback" not in err, err
    assert "Exception ignored" not in err, err
    assert code == 0, err


# ---------------------------------------------------------------- office_check (§16.7)
@pytest.fixture
def render_mod():
    import importlib

    return importlib.import_module("tundlekit.render")


def test_office_check_running(monkeypatch, render_mod):
    """§16.7: Word running -> ok false, name listed."""
    monkeypatch.setattr(render_mod, "office_running", lambda *a, **k: ["WINWORD.EXE"])
    res = h.call("office_check")
    assert res == {"running": ["WINWORD.EXE"], "ok": False}


def test_office_check_clear(monkeypatch, render_mod):
    """§16.7: nothing running -> ok true."""
    monkeypatch.setattr(render_mod, "office_running", lambda *a, **k: [])
    assert h.call("office_check") == {"running": [], "ok": True}


def test_office_check_cli_exit_codes(monkeypatch, capsys, render_mod):
    """§16.7: the CLI exits 1 when ok is false, 0 otherwise."""
    monkeypatch.setattr(render_mod, "office_running", lambda *a, **k: ["WINWORD.EXE"])
    code, data, _, _ = h.run_cli(capsys, ["office", "check", "--json"])
    assert code == 1 and data["ok"] is False and data["running"] == ["WINWORD.EXE"]
    monkeypatch.setattr(render_mod, "office_running", lambda *a, **k: [])
    code, data, _, _ = h.run_cli(capsys, ["office", "check", "--json"])
    assert code == 0 and data["ok"] is True


def test_office_check_wait_is_bounded(monkeypatch, capsys, render_mod):
    """§16.7: `--wait 1` with Office still running returns within about 3 s."""
    monkeypatch.setattr(render_mod, "office_running", lambda *a, **k: ["WINWORD.EXE"])
    t0 = time.monotonic()
    code, data, _, _ = h.run_cli(capsys, ["office", "check", "--wait", "1", "--json"])
    assert time.monotonic() - t0 < 3.5
    assert code == 1 and data["ok"] is False


def test_office_check_is_read_only(render_mod):
    """§16.7: office_check is registered and read-only."""
    from tundlekit import registry

    listing = registry.TOOLS["office_check"].listing()
    assert listing["annotations"]["readOnlyHint"] is True


# ---------------------------------------------------------------- integral floats (§16.7)
def test_integral_float_rank_and_wrap():
    """§16.7: `rank: 1.0` and `wrap: 3.0` are accepted as integers."""
    spec = {"wrap": 3.0,
            "nodes": [{"id": "a", "label": "A"}, {"id": "b", "label": "B", "rank": 1.0},
                      {"id": "c", "label": "C"}],
            "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}]}
    assert h.call("diagram_validate", spec=spec)["ok"] is True
    res = h.call("diagram_render", spec=spec)
    assert res["nodes"]["b"]["rank"] == 1
