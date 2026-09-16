"""MANIFEST §13.1 / §13.7 (with §2.5, §2.6, §2.7, §2.8): bundle hardening, visible cases."""
import hashlib
import json
import os
import subprocess
import sys

import pytest

from helpers_core import (MARKER, by_rule, call, changelog_text, check_shape, commit_all, git, git_out,  # noqa: F401
                          gitenv, lint_tree, make_history, make_tundle, run_cli, tool_error, write)


def _clear_git_env(monkeypatch):
    for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        monkeypatch.delenv(k, raising=False)


def _state(root):
    return (git_out(root, "rev-parse", "HEAD"), git_out(root, "rev-list", "--count", "HEAD"),
            git_out(root, "for-each-ref", "--format=%(objectname) %(refname)"))


# ---------------------------------------------------------------- §13.1 git environment

def test_prune_ignores_git_dir_of_other_repo(tmp_path, gitenv, monkeypatch):  # noqa: F811
    """§13.1: with GIT_DIR pointing at another repository, prune rewrites only `root`."""
    other = make_tundle(tmp_path / "other")
    make_history(other, 4)
    clone = make_tundle(tmp_path / "clone")
    make_history(clone, 4)
    other_before = _state(other)
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    r = call("bundle_prune", root=clone, keep=2, yes=True)
    _clear_git_env(monkeypatch)
    assert r["pruned"] is True and r["total"] == 5
    assert git_out(clone, "rev-list", "--count", "HEAD") == "2"
    assert _state(other) == other_before
    assert git_out(other, "status", "--porcelain") == ""


def test_status_ignores_git_dir_and_work_tree(tmp_path, gitenv, monkeypatch):  # noqa: F811
    """§13.1: status reports root's own history even when GIT_DIR/GIT_WORK_TREE name another repository."""
    other = make_tundle(tmp_path / "other")
    make_history(other, 6)
    t = make_tundle(tmp_path / "t")
    write(t, "new.md", "x")
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(other))
    r = call("bundle_status", root=t)
    _clear_git_env(monkeypatch)
    assert r["history"] == 1
    assert r["last"]["subject"] == "tundle 2026.09.15.1: initial"
    assert [p["path"] for p in r["pending"]] == ["new.md"]


# ---------------------------------------------------------------- §13.1 prune deletes every other ref

def test_prune_deletes_remote_and_notes_refs(tmp_path, gitenv):  # noqa: F811
    """§13.1: remotes and notes refs pointing at dropped commits are deleted; dropped commits are gone."""
    root = make_tundle(tmp_path / "t")
    shas = [git_out(root, "rev-parse", "HEAD")] + make_history(root, 4)
    dropped = shas[:3]
    git(root, "update-ref", "refs/remotes/origin/main", dropped[1])
    git(root, "update-ref", "refs/notes/commits", dropped[0])
    git(root, "update-ref", "refs/remotes/origin/HEAD", dropped[2])
    r = call("bundle_prune", root=root, keep=2, yes=True)
    assert r["pruned"] is True
    refs = git_out(root, "for-each-ref", "--format=%(refname)").splitlines()
    assert refs == ["refs/heads/main"]
    for sha in dropped:
        assert git(root, "cat-file", "-e", sha, check=False).returncode != 0, sha
    assert git_out(root, "rev-list", "--count", "HEAD") == "2"


# ---------------------------------------------------------------- §13.1 byte-identical rebuild

def test_prune_keeps_encoding_header_byte_exact(tmp_path, gitenv):  # noqa: F811
    """§13.1: a commit with `encoding ISO-8859-1` and a Latin-1 author is rebuilt byte-identical minus parents."""
    root = make_tundle(tmp_path / "t")
    make_history(root, 1)
    tree = git_out(root, "rev-parse", "HEAD^{tree}")
    parent = git_out(root, "rev-parse", "HEAD")
    raw = (f"tree {tree}\nparent {parent}\n".encode()
           + b"author J\xf6rg M\xfcller <jm@example.com> 1789000000 +0200\n"
           + b"committer J\xf6rg M\xfcller <jm@example.com> 1789000100 +0200\n"
           + b"encoding ISO-8859-1\n\nR\xe9sum\xe9 of the caf\xe9\n\nbody line\n")
    latin = git(root, "hash-object", "-t", "commit", "-w", "--stdin", input=raw).stdout.decode().strip()
    git(root, "update-ref", "refs/heads/main", latin)
    commit_all(root, "after", date="2026-09-16T12:00:00+00:00", allow_empty=True)
    call("bundle_prune", root=root, keep=2, yes=True)
    new_root = git_out(root, "rev-list", "--max-parents=0", "HEAD")
    expected = b"".join(line for line in raw.splitlines(keepends=True) if not line.startswith(b"parent "))
    assert git(root, "cat-file", "commit", new_root).stdout == expected


# ---------------------------------------------------------------- §13.1 ASCII-only versions

def test_arabic_indic_version_is_invalid(tmp_path, gitenv):  # noqa: F811
    """§13.1: VERSION digits are ASCII only; Arabic-Indic digits give `invalid VERSION`."""
    root = make_tundle(tmp_path / "t")
    write(root, "VERSION", "٢٠٢٦.٠٩.١٥.١\n")
    with pytest.raises(tool_error()) as ei:
        call("bundle_status", root=root)
    assert "invalid VERSION" in str(ei.value)


# ---------------------------------------------------------------- §13.1 links are not followed

def _make_dir_link(link, target):
    """A directory junction (Windows) or symlink; skip if the platform refuses."""
    if sys.platform == "win32":
        p = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True)
        if p.returncode != 0 or not os.path.lexists(link):
            pytest.skip("cannot create a junction here")
    else:
        try:
            os.symlink(str(target), str(link), target_is_directory=True)
        except (OSError, NotImplementedError):
            pytest.skip("cannot create a symlink here")


def _remove_dir_link(link):
    if os.path.lexists(link):
        try:
            os.rmdir(link) if sys.platform == "win32" else os.unlink(link)
        except OSError:
            pass


def test_lint_does_not_follow_junction_loop(tmp_path):
    """§13.1: a link inside root pointing back at root is 1 entry and is not descended into."""
    root = lint_tree(tmp_path / "t", files={"docs/README.md": "x", "docs/a.md": "a", "docs/b_v2.md": "b"})
    base = call("bundle_lint", root=root)
    link = root / "docs" / "loop"
    _make_dir_link(link, root)
    try:
        r = call("bundle_lint", root=root)
    finally:
        _remove_dir_link(link)
    check_shape(r)
    assert r["files"] in (base["files"], base["files"] + 1)
    assert all(not f["path"].startswith("docs/loop/") for f in r["findings"])
    assert len(by_rule(r, "B003")) == len(by_rule(base, "B003")) == 1


# ---------------------------------------------------------------- §13.1 lint/verify ignore

def test_lint_ignore_rule_and_rule_glob(tmp_path):
    """§13.1: ignore `B003` drops the rule everywhere; `B003:papers/*` only under papers/."""
    root = lint_tree(tmp_path / "t", files={"notes_v2.md": "x", "papers/README.md": "r",
                                            "papers/draft_final.md": "y"})
    full = call("bundle_lint", root=root)
    assert sorted(f["path"] for f in by_rule(full, "B003")) == ["notes_v2.md", "papers/draft_final.md"]
    r = call("bundle_lint", root=root, ignore=["B003"])
    check_shape(r)
    assert by_rule(r, "B003") == []
    r = call("bundle_lint", root=root, ignore=["B003:papers/*"])
    check_shape(r)
    assert [f["path"] for f in by_rule(r, "B003")] == ["notes_v2.md"]


def test_verify_ignore_b013(tmp_path):
    """§13.1: bundle_verify takes `ignore` too."""
    root = lint_tree(tmp_path / "t", files={"vendor/p/a.zip": "a", "vendor/p/SOURCE.md": "- URL: x\n"})
    assert len(by_rule(call("bundle_verify", root=root), "B013")) == 1
    r = call("bundle_verify", root=root, ignore=["B013"])
    check_shape(r)
    assert r["findings"] == []


# ---------------------------------------------------------------- §13.1 SOURCE.md targets outside root

def test_source_file_outside_root_is_b013(tmp_path):
    """§13.1: `- File: ../outside` resolves outside root: B013, no exception, nothing outside is read."""
    payload = b"outside payload\n"
    root = lint_tree(tmp_path / "t", files={
        "vendor/p/SOURCE.md": f"- File: ../../../outside.bin\n- SHA-256: {hashlib.sha256(payload).hexdigest()}\n"})
    (tmp_path / "outside.bin").write_bytes(payload)
    r = call("bundle_verify", root=root)
    check_shape(r)
    b013 = by_rule(r, "B013")
    assert [f["path"] for f in b013] == ["vendor/p/SOURCE.md"]
    assert r["checked"] == []
    lint = call("bundle_lint", root=root)
    assert [f["path"] for f in by_rule(lint, "B013")] == ["vendor/p/SOURCE.md"]


# ---------------------------------------------------------------- §13.7 / §2.6 bundle_init

def test_init_refuses_changelog_without_marker(tmp_path, gitenv):  # noqa: F811
    """§2.6/§13.7: an existing CHANGELOG.md without the marker -> ToolError naming it; nothing is written."""
    root = tmp_path / "b"
    write(root, "CHANGELOG.md", "# My own log\n\n- something happened\n")
    with pytest.raises(tool_error()) as ei:
        call("bundle_init", root=root)
    assert MARKER in str(ei.value)
    assert (root / "CHANGELOG.md").read_bytes() == b"# My own log\n\n- something happened\n"
    assert not (root / "VERSION").exists()
    assert not (root / ".gitignore").exists()
    assert not (root / ".gitattributes").exists()


# ---------------------------------------------------------------- more cases

def test_release_ignores_git_index_file(tmp_path, gitenv, monkeypatch):  # noqa: F811
    """§13.1: GIT_INDEX_FILE is removed from git's environment; the root's own index is used."""
    t = make_tundle(tmp_path / "t")
    write(t, "a.md", "a\n")
    stray = tmp_path / "stray.index"
    monkeypatch.setenv("GIT_INDEX_FILE", str(stray))
    r = call("bundle_release", root=t, summary="with index env")
    monkeypatch.delenv("GIT_INDEX_FILE")
    assert not stray.exists()
    assert git_out(t, "status", "--porcelain") == ""
    assert "a.md" in git_out(t, "show", "--name-only", "--format=", r["commit"]).splitlines()


def test_lint_reports_non_ascii_version_as_b010(tmp_path):
    """§13.1 + §2.1a: lint never raises for a bad VERSION; Devanagari digits give B010."""
    root = lint_tree(tmp_path / "t")
    write(root, "VERSION", "२०२६.०९.१६.२\n")
    r = call("bundle_lint", root=root)
    check_shape(r)
    assert by_rule(r, "B010")


def test_cli_lint_ignore_repeatable(tmp_path, capsys):
    """§13.1: CLI `--ignore` is repeatable."""
    root = lint_tree(tmp_path / "t", files={"x_old.md": "x", "cache.tmp": "x"})
    rc, out, _ = run_cli(capsys, ["bundle", "lint", "--root", root, "--json"])
    assert {f["rule"] for f in json.loads(out)["findings"]} >= {"B003", "B005"}
    rc, out, _ = run_cli(capsys, ["bundle", "lint", "--root", root, "--ignore", "B003", "--ignore", "B005",
                                  "--json"])
    assert rc == 0, out
    assert not {f["rule"] for f in json.loads(out)["findings"]} & {"B003", "B005"}
