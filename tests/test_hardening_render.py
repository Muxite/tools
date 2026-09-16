"""MANIFEST §13.2 (with §8.3): render_office out_dir safety, visible cases.

Safety: every refusal target is inside tmp_path, so a buggy implementation can only delete test data.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_misc as h  # noqa: E402

MARK = ".tundlekit-render"


@pytest.fixture
def report(tmp_path):
    return h.make_docx(tmp_path / "src" / "report.docx", [(None, ["Hello"])])


def office(capsys, src, out):
    return h.run_cli(["render", "office", src, "-o", out, "--backend", "text", "--json"], capsys)


def refused(code, data):
    return code == 1 and data is not None and "refusing" in data.get("error", "")


# ---------------------------------------------------------------- §8.3 marker rule

def test_non_empty_dir_without_marker_refused(report, tmp_path, capsys):
    """§8.3/§13.2: an out_dir holding an unrelated file and no marker is refused; the file is kept."""
    out = tmp_path / "mine"
    out.mkdir()
    (out / "thesis.txt").write_text("precious", encoding="utf-8")
    code, data, _, _ = office(capsys, report, out)
    assert refused(code, data), data
    assert (out / "thesis.txt").read_text(encoding="utf-8") == "precious"
    assert sorted(p.name for p in out.iterdir()) == ["thesis.txt"]


def test_render_writes_marker(report, tmp_path, capsys):
    """§8.3: every render writes the `.tundlekit-render` marker into out_dir; a re-render is then allowed."""
    out = tmp_path / "render"
    code, _, _, _ = office(capsys, report, out)
    assert code == 0
    assert (out / MARK).is_file()
    code, _, _, _ = office(capsys, report, out)
    assert code == 0
    assert (out / MARK).is_file()


def test_existing_empty_dir_is_used(report, tmp_path, capsys):
    """§8.3: an existing empty out_dir is fine."""
    out = tmp_path / "empty"
    out.mkdir()
    code, _, _, _ = office(capsys, report, out)
    assert code == 0
    assert (out / "paragraphs.txt").is_file()


def test_marker_dir_is_emptied(report, tmp_path, capsys):
    """§8.3: with the marker present, unrelated old contents are removed."""
    out = tmp_path / "render"
    (out / "sub").mkdir(parents=True)
    (out / MARK).write_bytes(b"")
    (out / "sub" / "old.png").write_bytes(b"old")
    (out / "old.txt").write_bytes(b"old")
    code, _, _, _ = office(capsys, report, out)
    assert code == 0
    assert not (out / "sub").exists() and not (out / "old.txt").exists()


# ---------------------------------------------------------------- §13.2 protected directories

def test_cwd_refused(report, tmp_path, capsys, monkeypatch):
    """§13.2: the current working directory is protected (even when it carries the marker)."""
    cwd = tmp_path / "work"
    cwd.mkdir()
    (cwd / MARK).write_bytes(b"")
    (cwd / "keep.txt").write_text("keep", encoding="utf-8")
    monkeypatch.chdir(cwd)
    code, data, _, _ = office(capsys, report, cwd)
    assert refused(code, data), data
    assert (cwd / "keep.txt").is_file()


def test_ancestor_of_home_refused(report, tmp_path, capsys, monkeypatch):
    """§13.2: every ancestor of the home directory is protected."""
    top = tmp_path / "users"
    home = top / "me"
    home.mkdir(parents=True)
    (home / "keep.txt").write_text("keep", encoding="utf-8")
    (top / MARK).write_bytes(b"")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    code, data, _, _ = office(capsys, report, top)
    assert refused(code, data), data
    assert (home / "keep.txt").is_file()


@pytest.mark.skipif(sys.platform != "win32", reason="\\\\?\\ paths are Windows-only")
def test_extended_length_form_of_source_dir_refused(report, capsys):
    """§13.2: a `\\\\?\\` spelling of the source's directory is refused; the source is untouched."""
    srcdir = report.parent
    (srcdir / MARK).write_bytes(b"")
    before = h.snapshot(report)
    out = "\\\\?\\" + os.path.abspath(str(srcdir))
    code, data, _, _ = office(capsys, report, out)
    assert refused(code, data), data
    assert h.snapshot(report) == before


# ---------------------------------------------------------------- §13.2 invalid path strings

@pytest.mark.skipif(sys.platform != "win32", reason="`|` is a valid name character on POSIX")
def test_pipe_in_out_dir_is_tool_error(report, tmp_path, monkeypatch):
    """§13.2: an out_dir that isn't a valid path gives ToolError."""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(h.tool_error()):
        h.call_tool("render_office", {"src": str(report), "out_dir": "bad|name", "backend": "text"})


# ---------------------------------------------------------------- more cases

def test_home_itself_via_dotdot_refused(report, tmp_path, capsys, monkeypatch):
    """§13.2: the home directory, spelled with `..`, is refused even with the marker present."""
    home = tmp_path / "people" / "ana"
    (home / "docs").mkdir(parents=True)
    (home / MARK).write_bytes(b"")
    (home / "docs" / "cv.txt").write_text("cv", encoding="utf-8")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    code, data, _, _ = office(capsys, report, str(home / "docs" / ".."))
    assert refused(code, data), data
    assert (home / "docs" / "cv.txt").is_file()


def test_hidden_file_only_dir_is_refused(report, tmp_path, capsys):
    """§8.3: a directory holding only an unrelated hidden file is not empty and has no marker: refused."""
    out = tmp_path / "hid"
    out.mkdir()
    (out / ".settings").write_text("s", encoding="utf-8")
    code, data, _, _ = office(capsys, report, out)
    assert refused(code, data), data
    assert (out / ".settings").is_file()


def test_previous_render_dir_is_reused(report, tmp_path, capsys):
    """§8.3: a previous render's out_dir (it has the marker) is emptied and reused."""
    out = tmp_path / "r"
    assert office(capsys, report, out)[0] == 0
    (out / "extra").mkdir()
    (out / "extra" / "note.md").write_text("n", encoding="utf-8")
    code, data, _, _ = office(capsys, report, out)
    assert code == 0, data
    assert not (out / "extra").exists()
    assert (out / MARK).exists()
