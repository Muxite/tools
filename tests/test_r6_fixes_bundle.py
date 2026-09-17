"""Round 6 fixes: bundle_backup naming and prune failures (MANIFEST §19.2) and SOURCE.md coverage edge cases
(§19.4), on top of §17.3, §17.8, §2.7, §2.8 and §0.4."""
from __future__ import annotations

import os

import pytest

import helpers_r6f as h

NO_FILE_LINE = "SOURCE.md has no - File: line"


@pytest.fixture
def pinned(monkeypatch):
    monkeypatch.setenv("TUNDLEKIT_NOW", h.NOW)
    return monkeypatch


def shared(tmp_path):
    """notes/cap/REPORT.md and notes/gen/REPORT.md sharing notes/versions/."""
    root = h.tundle(tmp_path / "t")
    versions = root / "notes" / "versions"
    versions.mkdir(parents=True)
    cap = h.write(root / "notes" / "cap" / "REPORT.md", "# capsule report\n")
    gen = h.write(root / "notes" / "gen" / "REPORT.md", "# general report\n")
    return root, versions, cap, gen


# ------------------------------------------------------------------------------------ §19.2 labels
def test_labels_in_names_for_files_below_versions_parent(tmp_path, pinned):
    """§19.2: the file's directory relative to the versions/ parent is the label."""
    root, versions, cap, gen = shared(tmp_path)
    res = h.backup([cap, gen], "restyle")
    want = [h.labelled("cap", "REPORT", "restyle", ".md"), h.labelled("gen", "REPORT", "restyle", ".md")]
    assert [os.path.basename(b["path"]) for b in res["backups"]] == want
    assert sorted(os.listdir(versions)) == want
    assert (versions / want[0]).read_text(encoding="utf-8") == "# capsule report\n"


def test_manifest_example_label_joins_parts_with_dash(tmp_path, pinned):
    """§19.2 example: notes/report-capsules/REPORT.md with versions/ at the tundle root."""
    root = h.tundle(tmp_path / "t")
    (root / "versions").mkdir()
    f = h.write(root / "notes" / "report-capsules" / "REPORT.md", "r\n")
    h.backup(f, "x")
    assert os.listdir(root / "versions") == [f"notes-report-capsules REPORT (before x {h.TODAY}).md"]


def test_file_next_to_versions_has_no_label(tmp_path, pinned):
    """§19.2: a file in the directory that contains versions/ keeps the plain §17.3 name."""
    root, versions, cap, gen = shared(tmp_path)
    f = h.write(root / "notes" / "REPORT.md", "top\n")
    h.backup(f, "cut")
    assert os.listdir(versions) == [h.snapshot_name("REPORT", "cut", ".md")]


def seed(versions):
    """Older snapshots for both folders and a legacy unlabelled one."""
    names = {
        "cap": [h.labelled("cap", "REPORT", "first pass", ".md", "2026-09-01")],
        "gen": [h.labelled("gen", "REPORT", "first pass", ".md", "2026-09-01"),
                h.labelled("gen", "REPORT", "restyle", ".md")],
        "legacy": [h.snapshot_name("REPORT", "old layout", ".md", "2026-08-01")],
    }
    for group in names.values():
        for n in group:
            h.write(versions / n, n)
    return names


def test_prune_of_one_folder_never_touches_the_other(tmp_path, pinned):
    """§19.2: superseded and prune match only the full label-plus-stem."""
    root, versions, cap, gen = shared(tmp_path)
    seeded = seed(versions)
    res = h.backup(cap, "restyle", prune=True)
    assert sorted(os.path.basename(x) for x in res["superseded"]) == seeded["cap"]
    assert sorted(os.listdir(versions)) == sorted(
        [h.labelled("cap", "REPORT", "restyle", ".md")] + seeded["gen"] + seeded["legacy"])


def test_overwrite_of_one_folder_never_touches_the_other(tmp_path, pinned):
    """§19.2: gen's same-reason snapshot is not cap's target: no refusal without overwrite, and with
    overwrite only cap's own snapshot is replaced."""
    root, versions, cap, gen = shared(tmp_path)
    seeded = seed(versions)
    gen_same = versions / h.labelled("gen", "REPORT", "restyle", ".md")
    h.backup(cap, "restyle")
    h.write(cap, "# capsule report v2\n")
    h.backup(cap, "restyle", overwrite=True)
    assert (versions / h.labelled("cap", "REPORT", "restyle", ".md")).read_text(encoding="utf-8") == \
        "# capsule report v2\n"
    assert gen_same.read_text(encoding="utf-8") == gen_same.name
    assert all((versions / n).is_file() for n in seeded["gen"] + seeded["legacy"] + seeded["cap"])


# ------------------------------------------------------------------------------------ §19.2 prune failures
def _undeletable(monkeypatch, path):
    """Hold the file open on Windows (unlink fails); elsewhere refuse unlink for that path."""
    if os.name == "nt":
        return open(path, "rb")
    real_unlink, real_remove = os.unlink, os.remove

    def guard(real):
        def fn(p, *a, **k):
            if os.path.abspath(p) == os.path.abspath(path):
                raise PermissionError(13, "Permission denied", str(p))
            return real(p, *a, **k)
        return fn
    monkeypatch.setattr(os, "unlink", guard(real_unlink))
    monkeypatch.setattr(os, "remove", guard(real_remove))
    return open(path, "rb")


def test_undeletable_snapshot_listed_only_as_not_pruned(tmp_path, pinned):
    """§19.2: a snapshot that cannot be deleted is under `not_pruned`, never under `pruned`."""
    root, versions, cap, gen = shared(tmp_path)
    stuck = versions / h.labelled("cap", "REPORT", "first pass", ".md", "2026-09-01")
    gone = versions / h.labelled("cap", "REPORT", "second pass", ".md", "2026-09-05")
    h.write(stuck, "stuck")
    h.write(gone, "gone")
    with _undeletable(pinned, stuck):
        res = h.backup(cap, "restyle", prune=True)
    assert stuck.is_file() and not gone.exists()
    assert [os.path.basename(p) for p in h.not_pruned_paths(res)] == [stuck.name]
    assert stuck.name not in [os.path.basename(p) for p in h.pruned_paths(res)]
    assert gone.name in [os.path.basename(p) for p in h.pruned_paths(res)]


def test_cli_exits_1_when_a_snapshot_is_not_pruned(tmp_path, pinned, capsys):
    """§19.2/§0.4: `bundle backup --prune` exits 1 when a snapshot could not be deleted; the copy is made."""
    root, versions, cap, gen = shared(tmp_path)
    stuck = h.write(versions / h.labelled("cap", "REPORT", "first pass", ".md", "2026-09-01"), "stuck")
    with _undeletable(pinned, stuck):
        code, data, out, err = h.run_cli(capsys, ["bundle", "backup", cap, "--reason", "restyle", "--prune",
                                                  "--json"])
    assert code == 1, out + err
    assert data is not None and [os.path.basename(p) for p in h.not_pruned_paths(data)] == [stuck.name]
    assert (versions / h.labelled("cap", "REPORT", "restyle", ".md")).is_file()


# ------------------------------------------------------------------------------------ §19.4 coverage
def test_junk_file_is_not_the_other_file(tmp_path):
    """§19.4: desktop.ini is never an "other file", so a SOURCE.md without `- File:` covers the installer."""
    root = h.tundle(tmp_path / "t")
    d = root / "setup" / "tools" / "inkscape"
    exe = h.installer(d / "inkscape-1.4.3.msi")
    h.write(d / "desktop.ini", "[.ShellClassInfo]\n")
    h.write(d / "SOURCE.md", f"# Inkscape 1.4.3\n\n- SHA-256: {h.sha256(exe)}\n")
    assert h.b014_count(root) == 0
    ver = h.call("bundle_verify", root=str(root))
    assert [(c["file"], c["match"]) for c in ver["checked"]] == [("setup/tools/inkscape/inkscape-1.4.3.msi", True)]


def ambiguous(tmp_path):
    root = h.tundle(tmp_path / "t")
    d = h.windows_setup(root, ["7z2603-x64.exe", "7z2603-arm64.exe"])
    h.write(d / "SOURCE.md", f"# 7-Zip 26.03\n\n- SHA-256: {h.sha256(d / '7z2603-x64.exe')}\n")
    return root, d


def test_ambiguous_source_md_covers_none(tmp_path):
    """§19.4: 2 installers and a SOURCE.md without `- File:`: B014 counts both; B013 says why."""
    root, d = ambiguous(tmp_path)
    assert h.b014_count(root) == 2
    lint = h.call("bundle_lint", root=str(root))
    assert any(NO_FILE_LINE in f["message"] for f in h.by_rule(lint, "B013"))


def test_all_writes_nothing_in_ambiguous_dir(tmp_path):
    """§19.4: `bundle_source DIR` (all) writes no per-file stubs there and lists both installers in `skipped`."""
    root, d = ambiguous(tmp_path)
    before = h.files_under(root)
    res = h.call("bundle_source", file=str(d), write=True)
    assert h.files_under(root) == before
    assert not [r for r in res["results"] if r.get("written")]
    for name in ("7z2603-x64.exe", "7z2603-arm64.exe"):
        (s,) = h.skipped_for(res, name)
        assert s["reason"] == "SOURCE.md has no - File: line; add one"


def test_cli_all_lists_skipped_reason(tmp_path, capsys):
    """§19.4/§0.4: `bundle source DIR --all --write --json` shows the skipped installers and writes nothing."""
    root, d = ambiguous(tmp_path)
    before = h.files_under(root)
    code, data, out, err = h.run_cli(capsys, ["bundle", "source", d, "--all", "--write", "--json"])
    assert data is not None, out + err
    assert h.files_under(root) == before
    assert len(h.skipped_for(data, "7z2603-arm64.exe")) == 1

