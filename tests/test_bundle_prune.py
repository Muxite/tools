"""§2.5 bundle_prune."""
import pytest

from helpers_core import (call, commit_all, dir_size, git, git_out, gitenv, make_history,  # noqa: F401
                          make_tundle, tool_error, write)


def _raw_without_parents(root, sha):
    raw = git(root, "cat-file", "commit", sha).stdout
    return b"\n".join(line for line in raw.split(b"\n") if not line.startswith(b"parent "))


def _refs(root):
    return git_out(root, "for-each-ref", "--format=%(objectname) %(refname)")


@pytest.fixture
def seven(tmp_path, gitenv):  # noqa: F811
    """A tundle with commits c1..c7 (c1 is the tundle's initial commit renamed)."""
    root = make_tundle(tmp_path / "t", version="2026.09.16.7", files={"a.txt": "a\n"})
    git(root, "commit", "-q", "--amend", "-m", "c1")
    shas = [git_out(root, "rev-parse", "HEAD")]
    shas += make_history(root, 6, start=2)
    return root, shas


def test_prune_keep_below_one(seven):
    """§2.5 check 1: keep < 1 -> `KEEP must be at least 1`."""
    root, _ = seven
    with pytest.raises(tool_error()) as ei:
        call("bundle_prune", root=root, keep=0)
    assert "KEEP must be at least 1" in str(ei.value)


def test_prune_dirty_tree(seven):
    """§2.5 check 2: porcelain not empty -> `unreleased changes`."""
    root, _ = seven
    write(root, "dirty.txt", "x")
    with pytest.raises(tool_error()) as ei:
        call("bundle_prune", root=root, keep=3, yes=True)
    assert "unreleased changes" in str(ei.value)


def test_prune_two_branches(seven):
    """§2.5 check 3: more than 1 local branch."""
    root, _ = seven
    git(root, "branch", "side")
    with pytest.raises(tool_error()) as ei:
        call("bundle_prune", root=root, keep=3, yes=True)
    assert "more than one branch" in str(ei.value)
    assert git_out(root, "rev-list", "--count", "HEAD") == "7"


def test_prune_nothing_to_clear(seven):
    """§2.5 total <= keep: pruned false, dry_run false, all subjects kept."""
    root, _ = seven
    r = call("bundle_prune", root=root, keep=10)
    assert r == {"pruned": False, "dry_run": False, "total": 7, "keep": 10,
                 "kept_subjects": ["c7", "c6", "c5", "c4", "c3", "c2", "c1"], "dropped_subjects": []}


def test_prune_default_keep_is_5_dry_run(seven):
    """§2.5 keep default 5; without yes: dry run, nothing changes."""
    root, _ = seven
    head, refs = git_out(root, "rev-parse", "HEAD"), _refs(root)
    r = call("bundle_prune", root=root)
    assert r == {"pruned": False, "dry_run": True, "total": 7, "keep": 5,
                 "kept_subjects": ["c7", "c6", "c5", "c4", "c3"], "dropped_subjects": ["c2", "c1"]}
    assert git_out(root, "rev-parse", "HEAD") == head
    assert _refs(root) == refs


def test_prune_yes_rebuilds_history(seven):
    """§2.5 with yes: newest keep commits rebuilt on a new root; result fields."""
    root, shas = seven
    # Record the kept trees first: gc --prune=now removes the original commits (§2.5).
    old_trees = [git_out(root, "rev-parse", f"{old}^{{tree}}") for old in shas[-3:]]
    r = call("bundle_prune", root=root, keep=3, yes=True)
    assert r["pruned"] is True and r["dry_run"] is False
    assert r["total"] == 7 and r["keep"] == 3
    assert r["kept_subjects"] == ["c7", "c6", "c5"]
    assert r["dropped_subjects"] == ["c4", "c3", "c2", "c1"]
    assert isinstance(r["git_bytes_before"], int) and isinstance(r["git_bytes_after"], int)
    assert git_out(root, "rev-list", "--count", "HEAD") == "3"
    new = git_out(root, "rev-list", "--reverse", "HEAD").split()
    assert git_out(root, "rev-list", "--max-parents=0", "HEAD") == new[0]
    assert git_out(root, "symbolic-ref", "HEAD") == "refs/heads/main"
    for tree, nw in zip(old_trees, new):
        assert tree == git_out(root, "rev-parse", f"{nw}^{{tree}}")


def test_prune_preserves_metadata_byte_exact(tmp_path, gitenv):  # noqa: F811
    """§2.5 same tree, full message (byte-exact), author and committer name/email/date."""
    root = make_tundle(tmp_path / "t", version="2026.09.16.3")
    make_history(root, 2)
    write(root, "b.txt", "b\n")
    commit_all(root, "multi line subject\n\nbody line 1\nbody line 2\n",
               date="2026-03-04T05:06:07+05:30", author=("Ana Author", "ana@example.org"),
               committer=("Cy Committer", "cy@example.org"))
    write(root, "c.txt", "c\n")
    commit_all(root, "last one", date="2026-04-01T23:59:59-07:00")
    kept = git_out(root, "rev-list", "-n", "2", "HEAD").split()[::-1]
    before = [_raw_without_parents(root, s) for s in kept]
    call("bundle_prune", root=root, keep=2, yes=True)
    new = git_out(root, "rev-list", "--reverse", "HEAD").split()
    assert [_raw_without_parents(root, s) for s in new] == before


def test_prune_removes_dropped_objects_and_refs(seven):
    """§2.5 tags/original/stash refs deleted; dropped commits no longer exist."""
    root, shas = seven
    git(root, "tag", "v-old", shas[1])
    git(root, "tag", "-a", "v-ann", "-m", "annotated", shas[2])
    git(root, "update-ref", "refs/original/refs/heads/main", shas[0])
    write(root, "a.txt", "stashed change\n")
    git(root, "stash")
    assert git_out(root, "status", "--porcelain") == ""
    call("bundle_prune", root=root, keep=3, yes=True)
    assert git_out(root, "for-each-ref", "refs/tags", "refs/original", "refs/stash") == ""
    for dropped in shas[:4]:
        assert git(root, "cat-file", "-e", dropped, check=False).returncode != 0


def test_prune_keeps_working_tree(seven):
    """§2.5 working tree, VERSION and CHANGELOG.md unchanged."""
    root, _ = seven
    files = {p: (root / p).read_bytes() for p in ("VERSION", "CHANGELOG.md", "a.txt")}
    call("bundle_prune", root=root, keep=2, yes=True)
    for p, data in files.items():
        assert (root / p).read_bytes() == data
    assert git_out(root, "status", "--porcelain") == ""
