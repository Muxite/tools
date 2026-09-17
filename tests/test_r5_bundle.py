"""MANIFEST §17.3 bundle (round 5): per-file `<name>.SOURCE.md` coverage (B014, verify), where bundle_source
writes, `--all` with 1 entry per installer, `--force` refused in batch mode, README "What it is" split, compact
version exclusions, and read-only targets (§17.1 rules via `_atomic_write`). Results follow §0.2/§0.3/§0.4.
"""
from __future__ import annotations

import os

import pytest

import helpers_r5b as h


# ------------------------------------------------------------------------------------ coverage
def test_source_md_covers_only_its_file_line(tmp_path):
    """§17.3: a SOURCE.md covers exactly the file in its `- File:` line; the other installer in the same
    directory is still counted by B014 (§14.8 folder coverage no longer applies)."""
    root = h.tundle(tmp_path / "t")
    d = h.windows_setup(root, ["7z2603-x64.exe", "7z2603-arm64.exe"])
    x64 = d / "7z2603-x64.exe"
    h.write(d / "SOURCE.md", f"# 7-Zip 26.03\n\n- File: 7z2603-x64.exe\n- SHA-256: {h.sha256(x64)}\n")
    assert h.b014_count(root) == 1


def test_per_file_source_md_covers_its_file(tmp_path):
    """§17.3: `<name>.SOURCE.md` covers `<name>`; with one for each installer B014 is clean."""
    root = h.tundle(tmp_path / "t")
    names = ["7z2603-x64.exe", "7z2603-arm64.exe", "winrar-x64-723.exe"]
    d = h.windows_setup(root, names)
    h.write(d / "7z2603-x64.exe.SOURCE.md", f"# 7-Zip 26.03\n\n- SHA-256: {h.sha256(d / names[0])}\n")
    assert h.b014_count(root) == 2
    for n in names[1:]:
        h.write(d / f"{n}.SOURCE.md", f"# x\n\n- SHA-256: {h.sha256(d / n)}\n")
    assert h.b014(root) == []


def test_verify_checks_per_file_source_md(tmp_path):
    """§17.3/§2.8: bundle_verify checks `<name>.SOURCE.md` files too: a match is listed in `checked`, a changed
    installer is B012."""
    root = h.tundle(tmp_path / "t")
    d = h.windows_setup(root, ["7z2603-x64.exe", "winrar-x64-723.exe"])
    h.write(d / "winrar-x64-723.exe.SOURCE.md", f"# WinRAR 7.23\n\n- SHA-256: {h.sha256(d / 'winrar-x64-723.exe')}\n")
    res = h.call("bundle_verify", root=str(root))
    h.check_shape(res)
    assert [(c["source"], c["file"], c["match"]) for c in res["checked"]] == [
        ("setup/windows/winrar-x64-723.exe.SOURCE.md", "setup/windows/winrar-x64-723.exe", True)]
    h.installer(d / "winrar-x64-723.exe", b"changed bytes")
    res = h.call("bundle_verify", root=str(root))
    assert [f["path"] for f in h.by_rule(res, "B012")] == ["setup/windows/winrar-x64-723.exe.SOURCE.md"]
    assert res["ok"] is False


# ------------------------------------------------------------------------------------ where bundle_source writes
def test_single_installer_writes_source_md(tmp_path):
    """§17.3: a directory with no other installer gets `SOURCE.md`."""
    d = tmp_path / "setup" / "tools" / "inkscape-1.4.3"
    f = h.installer(d / "inkscape-1.4.3.msi")
    res = h.source(f, write=True)
    assert res["written"] is True
    assert os.path.basename(res["path"]) == "SOURCE.md"
    assert (d / "SOURCE.md").is_file()


def test_populated_directory_writes_per_file_source(tmp_path):
    """§17.3: with other installers in the directory, bundle_source writes `<name>.SOURCE.md`, which passes
    bundle_verify; SOURCE.md is not created."""
    root = h.tundle(tmp_path / "t")
    d = h.windows_setup(root, ["python-3.13.5-amd64.exe", "7z2603-x64.exe"])
    res = h.source(d / "python-3.13.5-amd64.exe", write=True)
    assert h.slash(res["path"]).endswith("setup/windows/python-3.13.5-amd64.exe.SOURCE.md")
    assert (d / "python-3.13.5-amd64.exe.SOURCE.md").is_file()
    assert not (d / "SOURCE.md").exists()
    ver = h.call("bundle_verify", root=str(root))
    assert [c["match"] for c in ver["checked"]] == [True]
    assert h.b014_count(root) == 1


def test_per_file_source_refuses_overwrite_without_force(tmp_path):
    """§15.7 with §17.3: an existing `<name>.SOURCE.md` is only replaced with force."""
    d = tmp_path / "setup" / "w"
    a = h.installer(d / "winrar-x64-723.exe")
    h.installer(d / "7z2603-x64.exe")
    h.source(a, write=True)
    with pytest.raises(h.tool_error()):
        h.source(a, write=True)
    assert h.source(a, write=True, force=True)["written"] is True


# ------------------------------------------------------------------------------------ --all
ALL_NAMES = ["python-3.13.5-amd64.exe", "matlab_R2024b_Windows.exe", "7z2603-x64.exe", "7z2603-arm64.exe",
             "winrar-x64-723.exe", "CrystalDiskInfo9_8_0.exe", "tsetup-x64.6.8.1.exe", "VisualStudioSetup.exe"]


def test_all_one_entry_per_installer_and_b014_clean(tmp_path):
    """§17.3: `bundle_source DIR` (all) gives 1 entry per uncovered installer in a populated setup/windows/,
    each a `<name>.SOURCE.md`; after write, B014 is clean and every file verifies."""
    root = h.tundle(tmp_path / "t")
    d = h.windows_setup(root, ALL_NAMES)
    assert h.b014_count(root) == len(ALL_NAMES)
    dry = h.source(d)
    assert len(dry["results"]) == len(ALL_NAMES)
    assert all(r["written"] is False for r in dry["results"])
    assert not [n for n in os.listdir(d) if "SOURCE" in n]
    res = h.source(d, write=True)
    got = sorted(os.path.basename(r["path"]) for r in res["results"])
    assert got == sorted(f"{n}.SOURCE.md" for n in ALL_NAMES)
    assert h.b014(root) == []
    ver = h.call("bundle_verify", root=str(root))
    assert len(ver["checked"]) == len(ALL_NAMES) and all(c["match"] for c in ver["checked"])
    assert h.source(d, write=True)["results"] == []


def test_all_uses_readme_names(tmp_path):
    """§17.3 + §16.6: the batch takes program and version from the README rows."""
    root = h.tundle(tmp_path / "t")
    d = h.windows_setup(root, ALL_NAMES)
    got = {os.path.basename(r["path"]): (r["program"], r["version"]) for r in h.source(d)["results"]}
    assert got["7z2603-x64.exe.SOURCE.md"] == ("7-Zip", "26.03")
    assert got["python-3.13.5-amd64.exe.SOURCE.md"] == ("Python", "3.13.5")
    assert got["matlab_R2024b_Windows.exe.SOURCE.md"] == ("MATLAB", "R2024b")
    assert got["tsetup-x64.6.8.1.exe.SOURCE.md"] == ("Telegram Desktop", "6.8.1")


def test_all_with_force_is_refused(tmp_path):
    """§17.3: `force` in batch mode is a ToolError, and nothing is written."""
    root = h.tundle(tmp_path / "t")
    d = h.windows_setup(root, ALL_NAMES[:3])
    with pytest.raises(h.tool_error()):
        h.source(d, write=True, force=True)
    assert not [n for n in os.listdir(d) if "SOURCE" in n]


def test_cli_all_force_exits_1(tmp_path, capsys):
    """§17.3/§0.4: `bundle source DIR --all --force --json` is a ToolError: exit 1 and `{"error": ...}`."""
    root = h.tundle(tmp_path / "t")
    d = h.windows_setup(root, ALL_NAMES[:2])
    code, data, out, err = h.run_cli(capsys, ["bundle", "source", d, "--all", "--write", "--force", "--json"])
    assert code == 1, out + err
    assert data and "error" in data


def test_cli_all_lists_every_installer(tmp_path, capsys):
    """§17.3: the CLI batch reports 1 result per installer."""
    root = h.tundle(tmp_path / "t")
    d = h.windows_setup(root, ALL_NAMES[:5])
    code, data, out, err = h.run_cli(capsys, ["bundle", "source", d, "--all", "--json"])
    assert code == 0, err + out
    assert len(data["results"]) == 5


# ------------------------------------------------------------------------------------ README cell split
@pytest.mark.parametrize("name,program,version", [
    ("7z2603-x64.exe", "7-Zip", "26.03"),
    ("python-3.13.5-amd64.exe", "Python", "3.13.5"),
    ("matlab_R2024b_Windows.exe", "MATLAB", "R2024b"),
])
def test_readme_cell_split(tmp_path, name, program, version):
    """§17.3: the "What it is" cell splits at the first digit-led token that contains `.` (or is R20xx[ab]);
    text after it (`, x64`, `, 64-bit`, `⚠ needs a licence ...`) is dropped. `7-Zip` is not the version."""
    d = h.windows_setup(tmp_path, [name, "WhatsApp Installer.exe"])
    res = h.source(d / name)
    assert (res["program"], res["version"]) == (program, version)
    assert h.heading(res["text"]) == f"# {program} {version}"


# ------------------------------------------------------------------------------------ compact versions
@pytest.mark.parametrize("name", ["backup-2024.zip", "office2016.exe", "foo-100.exe"])
def test_no_compact_version_from_years_or_hundreds(tmp_path, name):
    """§17.3: compact versions never come from 19xx/20xx groups or groups ending in 00."""
    res = h.source(h.installer(tmp_path / name))
    assert res["version"] == ""
    assert h.heading(res["text"]) == f"# {res['program']}"
    assert res["program"]


@pytest.mark.parametrize("name,program,version", [
    ("7z2603-x64.exe", "7z", "26.03"),
    ("winrar-x64-723.exe", "winrar", "7.23"),
])
def test_compact_versions_still_found(tmp_path, name, program, version):
    """§16.6 unchanged by §17.3: `2603` -> 26.03, `723` -> 7.23 (no README row)."""
    res = h.source(h.installer(tmp_path / name))
    assert (res["program"], res["version"]) == (program, version)


# ------------------------------------------------------------------------------------ read-only targets
def test_readonly_source_md_refused_without_temp_files(tmp_path):
    """§17.3/§17.1: replacing a read-only SOURCE.md (force) is a ToolError that says "read-only"; the file is
    unchanged and no temp file is left."""
    d = tmp_path / "setup" / "tools"
    f = h.installer(d / "inkscape-1.4.3.msi")
    target = h.write(d / "SOURCE.md", "# old\n")
    before = sorted(os.listdir(d))
    h.make_readonly(target)
    try:
        with pytest.raises(h.tool_error()) as exc:
            h.source(f, write=True, force=True)
        assert "read-only" in str(exc.value).lower()
        assert target.read_text(encoding="utf-8") == "# old\n"
        assert sorted(os.listdir(d)) == before
    finally:
        h.make_writable(target)


def test_readonly_readme_refused_by_setup_table(tmp_path):
    """§17.3: bundle_setup_table write on a read-only README.md is refused up front; no temp file is left."""
    d = tmp_path / "setup" / "windows"
    h.installer(d / "winrar-x64-723.exe")
    readme = h.write(d / "README.md", "| File | What it is |\n|---|---|\n")
    before = sorted(os.listdir(d))
    h.make_readonly(readme)
    try:
        with pytest.raises(h.tool_error()) as exc:
            h.call("bundle_setup_table", dir=str(d), write=True)
        assert "read-only" in str(exc.value).lower()
        assert sorted(os.listdir(d)) == before
    finally:
        h.make_writable(readme)
