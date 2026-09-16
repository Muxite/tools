"""§2.3 bundle_release."""
import pytest

from helpers_core import (MARKER, call, changelog_text, git, git_out, gitenv, make_history,  # noqa: F401
                          make_tundle, tool_error, write)


def _entry(version, stamp, summary, stats):
    # §2.3 step 6: blank, heading, blank, summary, blank, stats; every inserted line ends in \n
    return f"\n## {version}  ({stamp})\n\n{summary}\n\n_{stats}_\n"


def test_release_first_of_day(tmp_path, gitenv):  # noqa: F811
    """§2.3 step 5: old date != today -> today.1; §2.3 step 8 result."""
    root = make_tundle(tmp_path / "t", version="2026.09.15.1")
    write(root, "notes.md", "hello\n")
    r = call("bundle_release", root=root, summary="Added notes")
    assert r["version"] == "2026.09.16.1"
    assert r["previous"] == "2026.09.15.1"
    assert r["stats"] == {"added": 1, "modified": 0, "removed": 0, "renamed": 0}
    assert r["stats_text"] == "1 added, 0 modified, 0 removed, 0 renamed"
    assert r["commit"] == git_out(root, "rev-parse", "HEAD")
    assert len(r["commit"]) == 40
    assert r["history"] == 2
    assert r["prune_hint"] is False


def test_release_same_day_increments(tmp_path, gitenv):  # noqa: F811
    """§2.3 step 5: old date == today -> today.(N+1)."""
    root = make_tundle(tmp_path / "t", version="2026.09.16.3")
    write(root, "x.txt", "x")
    assert call("bundle_release", root=root, summary="s")["version"] == "2026.09.16.4"


def test_release_clock_behind_never_goes_backwards(tmp_path, gitenv):  # noqa: F811
    """§2.3 step 5: new <= old -> <old date part>.(N+1)."""
    root = make_tundle(tmp_path / "t", version="2026.09.20.2")
    write(root, "x.txt", "x")
    r = call("bundle_release", root=root, summary="s")
    assert r["version"] == "2026.09.20.3"
    assert r["previous"] == "2026.09.20.2"


def test_release_writes_version_file(tmp_path, gitenv):  # noqa: F811
    """§2.1/§2.3 step 6: VERSION written as `<version>\\n`."""
    root = make_tundle(tmp_path / "t", version="2026.09.15.1")
    write(root, "x.txt", "x")
    call("bundle_release", root=root, summary="s")
    assert (root / "VERSION").read_bytes() == b"2026.09.16.1\n"


def test_release_changelog_byte_exact(tmp_path, gitenv):  # noqa: F811
    """§2.3 step 6: entry inserted after the marker; the rest kept byte for byte."""
    root = make_tundle(tmp_path / "t", version="2026.09.15.1")
    before = (root / "CHANGELOG.md").read_bytes().decode("utf-8")
    write(root, "notes.md", "hello\n")
    call("bundle_release", root=root, summary="Added notes")
    head, tail = before.split(MARKER + "\n", 1)
    expected = head + MARKER + "\n" + _entry("2026.09.16.1", "2026-09-16 10:00", "Added notes",
                                             "1 added, 0 modified, 0 removed, 0 renamed") + tail
    assert (root / "CHANGELOG.md").read_bytes() == expected.encode("utf-8")


def test_release_changelog_keeps_crlf_lines(tmp_path, gitenv):  # noqa: F811
    """§2.3 step 6: existing line endings of other lines are kept; inserted lines end in \\n."""
    cl = (b"# Changelog\r\n\r\nIntro\r\n" + MARKER.encode() + b"\n"
          b"\r\n## 2026.09.15.1  (2026-09-15 18:27)\r\n\r\nold\r\n\r\n_1 added, 0 modified, 0 removed, 0 renamed_\r\n")
    root = make_tundle(tmp_path / "t", version="2026.09.15.1", changelog=cl.decode())
    assert (root / "CHANGELOG.md").read_bytes() == cl
    assert git_out(root, "status", "--porcelain") == ""
    write(root, "a.txt", "a")
    call("bundle_release", root=root, summary="CRLF test")
    head, tail = cl.split(MARKER.encode() + b"\n", 1)
    stats = "1 added, 0 modified, 0 removed, 0 renamed"
    expected = head + MARKER.encode() + b"\n" + _entry("2026.09.16.1", "2026-09-16 10:00", "CRLF test",
                                                       stats).encode() + tail
    assert (root / "CHANGELOG.md").read_bytes() == expected


def test_release_stats_all_kinds(tmp_path, gitenv):  # noqa: F811
    """§2.3 step 4: A/M/D/R counted from `git diff --cached --name-status --find-renames`."""
    body = "line one\nline two\nline three\nline four\n"
    root = make_tundle(tmp_path / "t", files={"mod.txt": "m\n", "del.txt": "d\n", "ren.txt": body})
    write(root, "mod.txt", "m2\n")
    (root / "del.txt").unlink()
    (root / "ren.txt").rename(root / "renamed.txt")
    write(root, "add.txt", "new\n")
    write(root, "add2.txt", "new2\n")
    r = call("bundle_release", root=root, summary="mixed")
    assert r["stats"] == {"added": 2, "modified": 1, "removed": 1, "renamed": 1}
    assert r["stats_text"] == "2 added, 1 modified, 1 removed, 1 renamed"


def test_release_commit_message_and_clean_tree(tmp_path, gitenv):  # noqa: F811
    """§2.3 step 7: VERSION and CHANGELOG.md committed; message `tundle {new}: {summary}` (stripped)."""
    root = make_tundle(tmp_path / "t", version="2026.09.15.1")
    write(root, "x.txt", "x")
    call("bundle_release", root=root, summary="  Tidy up  \n")
    assert git_out(root, "log", "-1", "--format=%B") == "tundle 2026.09.16.1: Tidy up"
    assert git_out(root, "status", "--porcelain") == ""
    assert git_out(root, "show", "HEAD:VERSION") == "2026.09.16.1"
    text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "\nTidy up\n" in text


def test_release_empty_summary(tmp_path, gitenv):  # noqa: F811
    """§2.3 step 1: empty summary -> ToolError `usage: release`."""
    root = make_tundle(tmp_path / "t")
    write(root, "x.txt", "x")
    with pytest.raises(tool_error()) as ei:
        call("bundle_release", root=root, summary="")
    assert "usage: release" in str(ei.value)


def test_release_missing_marker(tmp_path, gitenv):  # noqa: F811
    """§2.3 step 2: no marker line -> ToolError naming it; nothing staged or changed."""
    root = make_tundle(tmp_path / "t", changelog="# Changelog\n\nno marker here\n")
    write(root, "x.txt", "x")
    head = git_out(root, "rev-parse", "HEAD")
    with pytest.raises(tool_error()) as ei:
        call("bundle_release", root=root, summary="s")
    assert "<!-- entries -->" in str(ei.value)
    assert git_out(root, "rev-parse", "HEAD") == head
    assert git_out(root, "status", "--porcelain") == "?? x.txt"
    assert (root / "VERSION").read_bytes() == b"2026.09.15.1\n"


def test_release_nothing_to_release(tmp_path, gitenv):  # noqa: F811
    """§2.3 step 3: nothing staged -> ToolError `nothing to release`."""
    root = make_tundle(tmp_path / "t")
    head = git_out(root, "rev-parse", "HEAD")
    with pytest.raises(tool_error()) as ei:
        call("bundle_release", root=root, summary="s")
    assert "nothing to release" in str(ei.value)
    assert git_out(root, "rev-parse", "HEAD") == head


def test_release_prune_hint(tmp_path, gitenv):  # noqa: F811
    """§2.3 step 8: prune_hint = history > 10."""
    root = make_tundle(tmp_path / "t")
    make_history(root, 9)                    # 10 commits
    write(root, "x.txt", "x")
    r = call("bundle_release", root=root, summary="s")
    assert r["history"] == 11
    assert r["prune_hint"] is True


def test_release_twice_same_day(tmp_path, gitenv):  # noqa: F811
    """§2.3 step 5: consecutive releases on 1 day count up; newest entry first."""
    root = make_tundle(tmp_path / "t", version="2026.09.15.1")
    write(root, "a.txt", "a")
    call("bundle_release", root=root, summary="first")
    write(root, "b.txt", "b")
    r = call("bundle_release", root=root, summary="second")
    assert r["version"] == "2026.09.16.2"
    assert r["previous"] == "2026.09.16.1"
    text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    assert text.index("## 2026.09.16.2  (") < text.index("## 2026.09.16.1  (") < text.index("## 2026.09.15.1  (")
