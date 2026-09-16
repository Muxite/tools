"""§2.1 common rules and §2.2 bundle_status."""
from pathlib import Path

import pytest

from helpers_core import (call, commit_all, dir_size, git, gitenv, make_history, make_tundle,  # noqa: F401
                          tool_error, write)


def test_status_basic_fields(tmp_path, gitenv):  # noqa: F811
    """§2.2 version, last {date, subject}, history, prune_hint."""
    root = make_tundle(tmp_path / "t", version="2026.09.15.1", date="2026-09-15T18:27:00+02:00")
    r = call("bundle_status", root=root)
    assert r["version"] == "2026.09.15.1"
    assert r["last"] == {"date": "2026-09-15 18:27:00 +0200", "subject": "tundle 2026.09.15.1: initial"}
    assert r["history"] == 1
    assert r["prune_hint"] is False
    assert r["pending"] == []
    assert Path(r["root"]).resolve() == root.resolve()


def test_status_no_commits(tmp_path, gitenv):  # noqa: F811
    """§2.2 last is null and history 0 when the repository has no commits."""
    root = make_tundle(tmp_path / "t", commit=False)
    r = call("bundle_status", root=root)
    assert r["last"] is None
    assert r["history"] == 0
    assert r["prune_hint"] is False


def test_status_history_counts_commits(tmp_path, gitenv):  # noqa: F811
    """§2.2 history = commits reachable from HEAD; prune_hint = history > 10."""
    root = make_tundle(tmp_path / "t")
    make_history(root, 10)
    r = call("bundle_status", root=root)
    assert r["history"] == 11
    assert r["prune_hint"] is True


def test_status_pending_codes(tmp_path, gitenv):  # noqa: F811
    """§2.2 pending: 1 entry per porcelain line, XY code with spaces stripped, ?? for untracked."""
    root = make_tundle(tmp_path / "t", files={"a.txt": "a\n", "b.txt": "b\n"})
    write(root, "a.txt", "changed\n")          # " M"
    (root / "b.txt").unlink()                   # " D"
    write(root, "new.txt", "n\n")               # "??"
    write(root, "staged.txt", "s\n")
    git(root, "add", "staged.txt")              # "A "
    r = call("bundle_status", root=root)
    got = sorted((p["status"], p["path"]) for p in r["pending"])
    assert got == sorted([("M", "a.txt"), ("D", "b.txt"), ("??", "new.txt"), ("A", "staged.txt")])


def test_status_pending_rename_uses_new_path(tmp_path, gitenv):  # noqa: F811
    """§2.2 for a rename, path is the new path."""
    root = make_tundle(tmp_path / "t", files={"old.txt": "some content\nline 2\nline 3\n"})
    git(root, "mv", "old.txt", "new.txt")
    r = call("bundle_status", root=root)
    assert r["pending"] == [{"status": "R", "path": "new.txt"}]


def test_status_sizes(tmp_path, gitenv):  # noqa: F811
    """§2.1 content_bytes = files under root excluding .git; git_bytes = files under .git."""
    root = make_tundle(tmp_path / "t", files={"data/blob.bin": b"x" * 5000})
    git(root, "status")   # settle the index so the tool's own `git status` leaves .git unchanged
    git(root, "status")
    r = call("bundle_status", root=root)
    assert r["content_bytes"] == dir_size(root, exclude_git=True)
    assert r["git_bytes"] == dir_size(root / ".git")
    assert r["git_bytes"] > 0


def test_status_largest(tmp_path, gitenv):  # noqa: F811
    """§2.2 largest: 5 largest files excluding .git, descending size, relative path."""
    files = {f"f{i}.bin": b"x" * (1000 * i) for i in range(1, 8)}
    files["sub/big.bin"] = b"y" * 20000
    root = make_tundle(tmp_path / "t", files=files)
    r = call("bundle_status", root=root)
    assert r["largest"] == [
        {"path": "sub/big.bin", "bytes": 20000},
        {"path": "f7.bin", "bytes": 7000},
        {"path": "f6.bin", "bytes": 6000},
        {"path": "f5.bin", "bytes": 5000},
        {"path": "f4.bin", "bytes": 4000},
    ]


def test_root_discovered_by_walking_up(tmp_path, gitenv, monkeypatch):  # noqa: F811
    """§2.1 root omitted: walk up from the cwd to the first dir with VERSION and CHANGELOG.md."""
    root = make_tundle(tmp_path / "t", version="2026.09.14.2", files={"deep/er/x.txt": "x"})
    monkeypatch.chdir(root / "deep" / "er")
    r = call("bundle_status")
    assert r["version"] == "2026.09.14.2"


def test_no_tundle_found(tmp_path, gitenv, monkeypatch):  # noqa: F811
    """§2.1 no tundle found walking up -> ToolError."""
    d = tmp_path / "empty" / "dir"
    d.mkdir(parents=True)
    monkeypatch.chdir(d)
    with pytest.raises(tool_error()) as ei:
        call("bundle_status")
    assert "no tundle found" in str(ei.value)


def test_invalid_version_status(tmp_path, gitenv):  # noqa: F811
    """§2.1 a malformed VERSION raises ToolError containing `invalid VERSION`."""
    root = make_tundle(tmp_path / "t")
    write(root, "VERSION", "banana\n")
    with pytest.raises(tool_error()) as ei:
        call("bundle_status", root=root)
    assert "invalid VERSION" in str(ei.value)


def test_version_read_strips_crlf(tmp_path, gitenv):  # noqa: F811
    """§2.1 VERSION is read with whitespace/CR/LF stripped."""
    root = make_tundle(tmp_path / "t")
    write(root, "VERSION", b"  2026.09.15.7 \r\n")
    assert call("bundle_status", root=root)["version"] == "2026.09.15.7"
