"""§2.6 bundle_init."""
import pytest

from helpers_core import MARKER, call, git, git_out, gitenv, make_tundle, tool_error, write  # noqa: F401

B005_DIRS = ["__pycache__", ".pytest_cache", ".benchmarks", ".ipynb_checkpoints", ".venv", "venv", "node_modules"]
B005_FILES = ["*.pyc", "*.tmp", "~$*", ".~lock.*#", "Thumbs.db", "desktop.ini", ".DS_Store", "._*"]


def _patterns(text):
    return {ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")}


def test_init_new_directory(tmp_path, gitenv):  # noqa: F811
    """§2.6 creates root, git init on main, VERSION today.0, no commit."""
    root = tmp_path / "fresh"
    r = call("bundle_init", root=root)
    assert r["version"] == "2026.09.16.0"
    assert (root / "VERSION").read_bytes() == b"2026.09.16.0\n"
    assert (root / ".git").exists()
    assert git_out(root, "symbolic-ref", "HEAD") == "refs/heads/main"
    assert git(root, "rev-parse", "--verify", "HEAD", check=False).returncode != 0


def test_init_created_list(tmp_path, gitenv):  # noqa: F811
    """§2.6 result created lists the relative paths written."""
    root = tmp_path / "b"
    r = call("bundle_init", root=root)
    assert sorted(r["created"]) == sorted(["VERSION", "CHANGELOG.md", ".gitignore", ".gitattributes"])


def test_init_changelog(tmp_path, gitenv):  # noqa: F811
    """§2.6 CHANGELOG first line `# Changelog`, contains the marker line and no entries."""
    root = tmp_path / "b"
    call("bundle_init", root=root)
    lines = (root / "CHANGELOG.md").read_text(encoding="utf-8").splitlines()
    assert lines[0] == "# Changelog"
    assert MARKER in lines
    after = lines[lines.index(MARKER) + 1:]
    assert not any(ln.startswith("## ") for ln in after)


def test_init_gitignore_and_gitattributes(tmp_path, gitenv):  # noqa: F811
    """§2.6 .gitignore with the B005 patterns; .gitattributes with `* -text`."""
    root = tmp_path / "b"
    call("bundle_init", root=root)
    pats = _patterns((root / ".gitignore").read_text(encoding="utf-8"))
    for f in ("*.pyc", "Thumbs.db", ".DS_Store"):
        assert f in pats
    for d in ("__pycache__", "node_modules"):
        assert d in pats or d + "/" in pats
    assert "* -text" in (root / ".gitattributes").read_text(encoding="utf-8").splitlines()


def test_init_existing_tundle_refused(tmp_path, gitenv):  # noqa: F811
    """§2.6 root/VERSION exists -> `already a tundle`."""
    root = make_tundle(tmp_path / "t")
    with pytest.raises(tool_error()) as ei:
        call("bundle_init", root=root)
    assert "already a tundle" in str(ei.value)


def test_init_keeps_existing_gitignore(tmp_path, gitenv):  # noqa: F811
    """§2.6 an existing .gitignore is not overwritten and not listed as created."""
    root = tmp_path / "b"
    write(root, ".gitignore", "mine-only\n")
    r = call("bundle_init", root=root)
    assert (root / ".gitignore").read_bytes() == b"mine-only\n"
    assert ".gitignore" not in r["created"]
    assert "VERSION" in r["created"]


def test_first_release_after_init(tmp_path, gitenv):  # noqa: F811
    """§2.6 the first release after init produces today.1."""
    root = tmp_path / "b"
    call("bundle_init", root=root)
    write(root, "doc.md", "hello\n")
    r = call("bundle_release", root=root, summary="first")
    assert r["version"] == "2026.09.16.1"
    assert r["previous"] == "2026.09.16.0"
    assert r["history"] == 1
    # stats are taken before VERSION/CHANGELOG are rewritten: all 5 files are new
    assert r["stats"] == {"added": 5, "modified": 0, "removed": 0, "renamed": 0}
