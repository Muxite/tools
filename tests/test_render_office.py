"""MANIFEST §8.3 render_office."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_misc as h  # noqa: E402


def read(p) -> str:
    return Path(p).read_text(encoding="utf-8")


@pytest.fixture
def deck(tmp_path):
    pytest.importorskip("pptx")
    return h.make_pptx(tmp_path / "src" / "talk.pptx", [
        (["Hello Title", "body one", "body two"], "note one"),
        (["Second slide"], None),
    ])


@pytest.fixture
def report(tmp_path):
    return h.make_docx(tmp_path / "src" / "report.docx", [
        ("Heading1", ["Introduction"]),
        (None, ["Hello ", "world"]),
        ("Quote", ["Cited text"]),
    ])


def office(capsys, src, out, backend="text"):
    return h.run_cli(["render", "office", src, "-o", out, "--backend", backend, "--json"], capsys)


# ------------------------------------------------------------------------------------------ text backend

def test_text_backend_pptx_slide_files(deck, tmp_path, capsys):
    """§8.3: .pptx text backend writes slide-NN.txt: 'TITLE: <first frame>' then the other frames, blank-line separated."""
    out = tmp_path / "render"
    code, data, _, _ = office(capsys, deck, out)
    assert code == 0
    assert data["backend"] == "text"
    assert data["kind"] == "text"
    assert read(out / "slide-01.txt").rstrip("\n") == "TITLE: Hello Title\n\nbody one\n\nbody two"
    assert read(out / "slide-02.txt").rstrip("\n") == "TITLE: Second slide"


def test_text_backend_pptx_notes_files(deck, tmp_path, capsys):
    """§8.3: notes-NN.txt holds each slide's notes."""
    out = tmp_path / "render"
    code, _, _, _ = office(capsys, deck, out)
    assert code == 0
    assert read(out / "notes-01.txt").strip() == "note one"
    assert (out / "notes-02.txt").is_file()
    assert read(out / "notes-02.txt").strip() == ""


def test_text_backend_pptx_result_lists_files(deck, tmp_path, capsys):
    """§8.3: result shape; files lists what was written; no PNG render means no sheets."""
    out = tmp_path / "render"
    code, data, _, _ = office(capsys, deck, out)
    assert code == 0
    for key in ("backend", "kind", "count", "files", "sheets", "warnings"):
        assert key in data, key
    names = {Path(f).name for f in data["files"]}
    assert {"slide-01.txt", "slide-02.txt"} <= names
    assert data["sheets"] == []
    assert isinstance(data["warnings"], list)


def test_text_backend_docx_paragraphs(report, tmp_path, capsys):
    """§8.3: .docx text backend writes paragraphs.txt, 1 line per paragraph '[<style id or Normal>] <text>'."""
    out = tmp_path / "render"
    code, data, _, _ = office(capsys, report, out)
    assert code == 0
    assert data["backend"] == "text"
    assert data["kind"] == "text"
    lines = read(out / "paragraphs.txt").splitlines()
    assert lines == ["[Heading1] Introduction", "[Normal] Hello world", "[Quote] Cited text"]
    assert "paragraphs.txt" in {Path(f).name for f in data["files"]}


def test_text_backend_docx_needs_no_pptx(report, tmp_path, capsys, monkeypatch):
    """§8.3: the .docx text backend is stdlib only (works with python-pptx unimportable)."""
    monkeypatch.setitem(sys.modules, "pptx", None)
    code, _, _, _ = office(capsys, report, tmp_path / "render")
    assert code == 0
    assert (tmp_path / "render" / "paragraphs.txt").is_file()


# ------------------------------------------------------------------------------------------ source handling

def test_source_copied_and_untouched(deck, tmp_path, capsys):
    """§8.3: the source is copied to out_dir/src.<ext>; the source is never modified."""
    before = h.snapshot(deck)
    out = tmp_path / "render"
    code, _, _, _ = office(capsys, deck, out)
    assert code == 0
    assert (out / "src.pptx").read_bytes() == before[0]
    assert h.snapshot(deck) == before


def test_docx_source_copied(report, tmp_path, capsys):
    """§8.3: .docx copy is out_dir/src.docx."""
    out = tmp_path / "render"
    code, _, _, _ = office(capsys, report, out)
    assert code == 0
    assert (out / "src.docx").read_bytes() == report.read_bytes()


def test_out_dir_created(report, tmp_path, capsys):
    """§8.3: out_dir is created if missing."""
    out = tmp_path / "a" / "b" / "c"
    code, _, _, _ = office(capsys, report, out)
    assert code == 0
    assert out.is_dir()


def test_out_dir_emptied_first(report, tmp_path, capsys):
    """§8.3: existing contents of out_dir are removed first (stale renders never survive).

    §8.3/§13.2: emptying a non-empty out_dir is only allowed when it holds the `.tundlekit-render` marker.
    """
    out = tmp_path / "render"
    (out / "old").mkdir(parents=True)
    (out / ".tundlekit-render").write_bytes(b"")
    (out / "slide-09.png").write_bytes(b"stale")
    (out / "old" / "x.txt").write_text("stale", encoding="utf-8")
    code, _, _, _ = office(capsys, report, out)
    assert code == 0
    assert not (out / "slide-09.png").exists()
    assert not (out / "old").exists()
    assert (out / "paragraphs.txt").is_file()


# ------------------------------------------------------------------------------------------ refusals

def assert_refused(code, data, err):
    assert code == 1
    assert "refusing" in data["error"]
    assert "refusing" in err


def test_refuses_source_directory(report, capsys):
    """§8.3: out_dir = the directory containing the source is refused; nothing is removed."""
    before = h.snapshot(report)
    code, data, _, err = office(capsys, report, report.parent)
    assert_refused(code, data, err)
    assert h.snapshot(report) == before


def test_refuses_ancestor_of_source(tmp_path, capsys):
    """§8.3: an ancestor of the source is refused."""
    src = h.make_docx(tmp_path / "a" / "b" / "r.docx", [(None, ["x"])])
    code, data, _, err = office(capsys, src, tmp_path / "a")
    assert_refused(code, data, err)
    assert src.is_file()


def test_refuses_dir_containing_git(report, tmp_path, capsys):
    """§8.3: a directory containing .git is refused."""
    out = tmp_path / "repo"
    (out / ".git").mkdir(parents=True)
    (out / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    code, data, _, err = office(capsys, report, out)
    assert_refused(code, data, err)
    assert (out / ".git" / "HEAD").is_file()


def test_refuses_home_directory(report, tmp_path, capsys, monkeypatch):
    """§8.3: the user's home directory is refused."""
    home = tmp_path / "home"
    home.mkdir()
    (home / "keep.txt").write_text("keep", encoding="utf-8")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    assert Path.home() == home
    code, data, _, err = office(capsys, report, home)
    assert_refused(code, data, err)
    assert (home / "keep.txt").is_file()


def test_refuses_filesystem_root(report, tmp_path, capsys, monkeypatch):
    """§8.3: a filesystem root is refused (deletion and copying are disabled for safety in this test)."""
    root = Path(tmp_path.anchor)
    h.forbid_writes(monkeypatch)
    code, data, _, err = office(capsys, report, root)
    assert_refused(code, data, err)


# ------------------------------------------------------------------------------------------ backends

def test_unsupported_extension(tmp_path, capsys):
    """§8.3: an unsupported extension gives ToolError containing 'unsupported'."""
    src = tmp_path / "src" / "notes.txt"
    src.parent.mkdir()
    src.write_text("hello", encoding="utf-8")
    code, data, _, _ = office(capsys, src, tmp_path / "render")
    assert code == 1
    assert "unsupported" in data["error"]


def test_named_unavailable_backend(report, tmp_path, capsys):
    """§8.3: a named backend that is unavailable raises ToolError containing 'not available'."""
    backends = h.call_tool("render_backends")
    if backends["powerpoint"]:
        pytest.skip("PowerPoint automation is available here")
    code, data, _, _ = office(capsys, report, tmp_path / "render", backend="powerpoint")
    assert code == 1
    assert "not available" in data["error"]


def test_auto_falls_back_to_text(report, tmp_path, capsys):
    """§8.3: auto = powerpoint if available, else libreoffice if available, else text."""
    backends = h.call_tool("render_backends")
    if backends["powerpoint"] or backends["libreoffice"]:
        pytest.skip("a visual backend is available here")
    code, data, _, _ = office(capsys, report, tmp_path / "render", backend="auto")
    assert code == 0
    assert data["backend"] == "text"


def test_office_running_is_a_list():
    """§8.3: tundlekit.render.office_running() returns a list of running POWERPNT.EXE/WINWORD.EXE names."""
    from tundlekit import render

    names = render.office_running()
    assert isinstance(names, list)
    assert set(names) <= {"POWERPNT.EXE", "WINWORD.EXE"}


def test_powerpoint_refuses_when_office_running(deck, tmp_path, capsys, monkeypatch):
    """§8.3: backend powerpoint checks office_running() first and refuses, naming the process."""
    from tundlekit import render

    if not h.call_tool("render_backends")["powerpoint"]:
        pytest.skip("PowerPoint automation is not available")
    calls = []

    def busy():
        calls.append(1)
        return ["POWERPNT.EXE"]

    monkeypatch.setattr(render, "office_running", busy)
    before = h.snapshot(deck)
    code, data, _, err = office(capsys, deck, tmp_path / "render", backend="powerpoint")
    assert code == 1
    assert "refusing" in data["error"] and "POWERPNT.EXE" in data["error"]
    assert calls
    assert h.snapshot(deck) == before
