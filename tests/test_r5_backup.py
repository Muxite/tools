"""MANIFEST §17.3 new tool `bundle_backup` / `tundlekit bundle backup FILE... --reason TEXT [--prune] [--overwrite]
[--force-office]`: target directory, snapshot name, refusals, overwrite, mtime, `superseded` and `prune`, CLI,
registration (§0.2, §15.10). `tundlekit.render.office_running` is pinned in every test.
"""
from __future__ import annotations

import os

import pytest

import helpers_r5b as h

REPORT = "AI4Research General Report - Muk"
# §19.2: the file sits in general/, below the versions/ parent, so snapshot stems carry the label "general".
SNAP = f"general {REPORT}"


@pytest.fixture(autouse=True)
def _pinned(monkeypatch):
    monkeypatch.setenv("TUNDLEKIT_NOW", h.NOW)
    h.no_office(monkeypatch)


def layout(tmp_path):
    """tundle/ai4research/{versions/, general/<report>.docx}: the real tundle shape."""
    root = h.tundle(tmp_path / "tundle")
    versions = root / "ai4research" / "versions"
    versions.mkdir(parents=True)
    doc = h.installer(root / "ai4research" / "general" / f"{REPORT}.docx", b"PK docx v1", (2026, 9, 10))
    return root, versions, doc


# ------------------------------------------------------------------------------------ registration
def test_registered_not_read_only_and_destructive():
    """§17.3/§0.2: bundle_backup is registered, not read-only, destructiveHint true."""
    import tundlekit.bundle  # noqa: F401
    from tundlekit import registry

    assert "bundle_backup" in registry.TOOLS
    listing = registry.TOOLS["bundle_backup"].listing()
    ann = listing.get("annotations", {})
    assert ann.get("readOnlyHint") is False
    assert ann.get("destructiveHint") is True
    schema = listing["inputSchema"]
    assert schema["additionalProperties"] is False
    assert {"reason", "prune", "overwrite", "force_office"} <= set(schema["properties"])


# ------------------------------------------------------------------------------------ copy and name
def test_copies_to_nearest_versions_dir(tmp_path):
    """§17.3: the nearest versions/ walking up from the file; name `<stem> (before <reason> <date>)<ext>` with
    the TUNDLEKIT_NOW date; result `backups` with source, path, bytes."""
    root, versions, doc = layout(tmp_path)
    res = h.backup(doc, "last-quarter cut")
    name = h.snapshot_name(SNAP, "last-quarter cut", ".docx")
    assert (versions / name).read_bytes() == b"PK docx v1"
    assert len(res["backups"]) == 1
    b = res["backups"][0]
    assert os.path.samefile(b["path"], versions / name)
    assert os.path.samefile(b["source"], doc)
    assert b["bytes"] == len(b"PK docx v1")
    assert res["superseded"] == []
    assert doc.read_bytes() == b"PK docx v1"


def test_closer_versions_dir_wins(tmp_path):
    """§17.3: a versions/ in the file's own directory is nearer than one higher up."""
    root, versions, doc = layout(tmp_path)
    near = doc.parent / "versions"
    near.mkdir()
    h.backup(doc, "restyle")
    assert os.listdir(near) == [h.snapshot_name(REPORT, "restyle", ".docx")]
    assert os.listdir(versions) == []


def test_creates_versions_next_to_file_without_one(tmp_path):
    """§17.3: no versions/ up to the tundle root: `<file dir>/versions` is created."""
    root = h.tundle(tmp_path / "tundle")
    f = h.write(root / "notes" / "capsule REPORT.md", "# report\n")
    res = h.backup(f, "overnight")
    target = root / "notes" / "versions" / h.snapshot_name("capsule REPORT", "overnight", ".md")
    assert target.read_text(encoding="utf-8") == "# report\n"
    assert os.path.samefile(res["backups"][0]["path"], target)


def test_versions_above_tundle_root_not_used(tmp_path):
    """§17.3: the walk stops at the tundle root."""
    (tmp_path / "versions").mkdir()
    root = h.tundle(tmp_path / "tundle")
    f = h.write(root / "docs" / "plan.md", "x\n")
    h.backup(f, "review")
    assert os.listdir(tmp_path / "versions") == []
    assert (root / "docs" / "versions" / h.snapshot_name("plan", "review", ".md")).is_file()


def test_mtime_kept(tmp_path):
    """§17.3: the copy keeps the modification time."""
    root, versions, doc = layout(tmp_path)
    h.backup(doc, "clarity pass")
    copy = versions / h.snapshot_name(SNAP, "clarity pass", ".docx")
    assert abs(os.stat(copy).st_mtime - os.stat(doc).st_mtime) < 2


def test_several_files(tmp_path):
    """§17.3: every file given is copied, in order; a dotted reason is allowed."""
    root, versions, doc = layout(tmp_path)
    py = h.write(root / "ai4research" / "general" / "build_reading.py", "print(1)\n")
    res = h.backup([doc, py], "v0.6 markers")
    assert [os.path.basename(b["path"]) for b in res["backups"]] == [
        h.snapshot_name(SNAP, "v0.6 markers", ".docx"),
        h.snapshot_name("general build_reading", "v0.6 markers", ".py")]
    assert sorted(os.listdir(versions)) == sorted(os.path.basename(b["path"]) for b in res["backups"])


# ------------------------------------------------------------------------------------ refusals
@pytest.mark.parametrize("reason", ["", "a/b", "a\\b", "x:y", "cut (2)", "why?", "a*b", 'say "hi"', "a<b", "a|b"])
def test_bad_reason_refused(tmp_path, reason):
    """§17.3: an empty reason or one with `()/\\:*?"<>|` is refused, and nothing is copied."""
    root, versions, doc = layout(tmp_path)
    before = h.files_under(root)
    with pytest.raises(h.tool_error()):
        h.backup(doc, reason)
    assert h.files_under(root) == before


def test_missing_file_refused_nothing_copied(tmp_path):
    """§17.3: a missing file refuses the whole call; the existing file is not copied either."""
    root, versions, doc = layout(tmp_path)
    with pytest.raises(h.tool_error()):
        h.backup([doc, doc.parent / "nope.docx"], "cut")
    assert os.listdir(versions) == []


def test_existing_target_needs_overwrite(tmp_path):
    """§17.3: an existing snapshot is refused unless overwrite; with it, the copy is replaced."""
    root, versions, doc = layout(tmp_path)
    name = h.snapshot_name(SNAP, "cut", ".docx")
    h.write(versions / name, "older snapshot")
    with pytest.raises(h.tool_error()):
        h.backup(doc, "cut")
    assert (versions / name).read_text(encoding="utf-8") == "older snapshot"
    res = h.backup(doc, "cut", overwrite=True)
    assert (versions / name).read_bytes() == b"PK docx v1"
    assert res["superseded"] == []
    assert not [n for n in os.listdir(versions) if "tmp" in n.lower()]


def test_office_running_refused_unless_forced(tmp_path, monkeypatch):
    """§17.3: while render.office_running() is non-empty the call is refused; force_office overrides."""
    root, versions, doc = layout(tmp_path)
    h.no_office(monkeypatch, ["WINWORD.EXE"])
    with pytest.raises(h.tool_error()):
        h.backup(doc, "cut")
    assert os.listdir(versions) == []
    res = h.backup(doc, "cut", force_office=True)
    assert len(res["backups"]) == 1


# ------------------------------------------------------------------------------------ superseded and prune
def seed_versions(versions):
    old = h.snapshot_name(SNAP, "last-quarter cut", ".docx", "2026-09-15")
    older = h.snapshot_name(SNAP, "first pass", ".docx", "2026-09-01")
    keep = [f"{SNAP} (annotated, code locations, 2026-09-15).docx",       # not a (before ...) snapshot
            h.snapshot_name(SNAP, "last-quarter cut", ".pdf", "2026-09-15"),  # other extension
            h.snapshot_name("AI4Research General Presentation - Muk", "clarity pass", ".pptx", "2026-09-15"),
            h.snapshot_name(f"{SNAP} v2", "cut", ".docx", "2026-09-15")]    # other stem
    for n in [old, older, *keep]:
        h.write(versions / n, n)
    return [old, older], keep


def test_superseded_lists_older_before_snapshots(tmp_path):
    """§17.3: `superseded` lists the older `(before ...)` snapshots of the same stem and extension; `(annotated
    ...)` and other stems/extensions are not listed; nothing is deleted without prune."""
    root, versions, doc = layout(tmp_path)
    old, keep = seed_versions(versions)
    res = h.backup(doc, "review")
    assert sorted(os.path.basename(p) for p in res["superseded"]) == sorted(old)
    for n in old + keep:
        assert (versions / n).is_file()


def test_prune_deletes_only_superseded(tmp_path):
    """§17.3: with prune the superseded snapshots are deleted; the new snapshot and every other file stay."""
    root, versions, doc = layout(tmp_path)
    old, keep = seed_versions(versions)
    res = h.backup(doc, "review", prune=True)
    assert sorted(os.path.basename(p) for p in res["superseded"]) == sorted(old)
    assert sorted(os.listdir(versions)) == sorted(keep + [h.snapshot_name(SNAP, "review", ".docx")])


def test_annotated_only_never_superseded(tmp_path):
    """§17.3: snapshots whose parentheses don't start with `before ` are never superseded, even with prune."""
    root, versions, doc = layout(tmp_path)
    ann = f"{SNAP} (annotated 2026-09-15).docx"
    h.write(versions / ann, "a")
    res = h.backup(doc, "cut", prune=True)
    assert res["superseded"] == []
    assert (versions / ann).is_file()


# ------------------------------------------------------------------------------------ CLI
def test_cli_backup_json(tmp_path, capsys):
    """§17.3/§0.4: `tundlekit bundle backup FILE FILE --reason TEXT --json`."""
    root, versions, doc = layout(tmp_path)
    md = h.write(doc.parent / "notes.md", "n\n")
    code, data, out, err = h.run_cli(capsys, ["bundle", "backup", doc, md, "--reason", "cut", "--json"])
    assert code == 0, err + out
    assert [os.path.basename(b["path"]) for b in data["backups"]] == [
        h.snapshot_name(SNAP, "cut", ".docx"), h.snapshot_name("general notes", "cut", ".md")]
    assert data["superseded"] == []


def test_cli_backup_prune_flag(tmp_path, capsys):
    """§17.3: `--prune` deletes the superseded snapshots."""
    root, versions, doc = layout(tmp_path)
    old, keep = seed_versions(versions)
    code, data, out, err = h.run_cli(capsys, ["bundle", "backup", doc, "--reason", "review", "--prune", "--json"])
    assert code == 0, err + out
    assert not any((versions / n).exists() for n in old)


def test_cli_backup_bad_reason_exit_1(tmp_path, capsys):
    """§17.3/§0.4: a refused reason is a ToolError: exit 1, `{"error": ...}` on stdout."""
    root, versions, doc = layout(tmp_path)
    code, data, out, err = h.run_cli(capsys, ["bundle", "backup", doc, "--reason", "a/b", "--json"])
    assert code == 1
    assert data and "error" in data
    assert os.listdir(versions) == []


def test_cli_backup_needs_reason(tmp_path, capsys):
    """§17.3/§0.4: `--reason` is required (usage error, or a ToolError for an empty reason)."""
    root, versions, doc = layout(tmp_path)
    code, data, out, err = h.run_cli(capsys, ["bundle", "backup", doc, "--json"])
    assert code in (1, 2)
    assert os.listdir(versions) == []
