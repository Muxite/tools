"""MANIFEST §15.7 `bundle_source` and `bundle_setup_table`, with §2.7 B006 and §2.8 verify; §15.10 registration.

File names are real ones from tundle's setup/windows and setup/linux READMEs. Expected program/version values
follow the revised §15.7 rules (architecture tokens stripped first), including the manifest's worked examples.
"""
from __future__ import annotations

import pytest

import helpers_r3 as r3

DATE = (2026, 3, 14)
DATE_TEXT = "2026-03-14"


def source(path, **kw):
    res = r3.call("bundle_source", file=str(path), **kw)
    assert set(res) >= {"path", "text", "sha256", "program", "version", "written"}
    return res


@pytest.mark.parametrize("name", ["bundle_source", "bundle_setup_table"])
def test_registered_in_bundle_not_read_only(name):
    """§15.10: registered by tundlekit.bundle; tools with a `write` flag are not read-only."""
    t = r3.get_tool(name)
    assert t.annotations.get("readOnlyHint") is not True
    assert t.input_schema.get("additionalProperties") is False
    assert "write" in t.input_schema["properties"]


@pytest.mark.parametrize("name,program,version", [
    ("python-3.13.5-amd64.exe", "python", "3.13.5"),
    ("cmake-4.1.0-rc1-windows-x86_64.msi", "cmake", "4.1.0-rc1"),
    ("CrystalDiskInfo9_8_0.exe", "CrystalDiskInfo", "9.8.0"),
    ("Git-2.55.0.5-64-bit.exe", "Git", "2.55.0.5"),
    ("jetbrains-toolbox-2.5.2.35332.exe", "jetbrains toolbox", "2.5.2.35332"),
    ("VSCodeUserSetup-x64-1.94.2.exe", "VSCodeUserSetup", "1.94.2"),
    ("ChromeSetup.exe", "ChromeSetup", ""),
    ("tsetup-x64.6.8.1.exe", "tsetup", "6.8.1"),
    ("NVIDIA-Linux-x86_64-570.169.run", "NVIDIA Linux", "570.169"),
    ("7z2603-x64.exe", "7z2603", ""),
    ("comet_installer_latest.exe", "comet installer latest", ""),
])
def test_program_and_version_guess(tmp_path, name, program, version):
    """§15.7: program/version guesses on real installer names (architecture tokens stripped first; a no-version
    program also gets `_`/`-` turned into spaces)."""
    f = r3.installer(tmp_path / name)
    res = source(f)
    assert res["version"] == version
    assert res["program"] == program


def test_compound_archive_extension(tmp_path):
    """§15.7: `.tar.gz` counts as 1 extension, so nvim-linux-x86_64.tar.gz gives `nvim linux` and no version."""
    f = r3.installer(tmp_path / "nvim" / "nvim-linux-x86_64.tar.gz", b"\x1f\x8b archive", DATE)
    res = source(f)
    assert (res["program"], res["version"]) == ("nvim linux", "")
    assert r3.norm_text(res["text"]) == r3.source_text("nvim linux", "", f.name, DATE_TEXT, r3.sha256(f))


def test_dry_run_text_exact(tmp_path):
    """§15.7: without write, the exact SOURCE.md text is returned and nothing is written."""
    f = r3.installer(tmp_path / "python-3.13.5" / "python-3.13.5-amd64.exe", b"python installer bytes", DATE)
    res = source(f)
    digest = r3.sha256(f)
    assert res["written"] is False
    assert res["sha256"].lower() == digest
    assert r3.norm_text(res["text"]) == r3.source_text("python", "3.13.5", f.name, DATE_TEXT, digest)
    assert not (f.parent / "SOURCE.md").exists()
    assert r3.slash(res["path"]).endswith("python-3.13.5/SOURCE.md")


def test_no_version_heading_has_no_trailing_space(tmp_path):
    """§15.7: an empty version gives a heading with no trailing space."""
    f = r3.installer(tmp_path / "chrome" / "ChromeSetup.exe", b"stub", DATE)
    res = source(f)
    first = res["text"].replace("\r\n", "\n").split("\n")[0]
    assert first == "# ChromeSetup"


def test_url_and_install_used(tmp_path):
    """§15.7: `url` and `install` replace the placeholders."""
    f = r3.installer(tmp_path / "cmake" / "cmake-4.1.0-rc1-windows-x86_64.msi", b"msi", DATE)
    url = "https://github.com/Kitware/CMake/releases/download/v4.1.0-rc1/cmake-4.1.0-rc1-windows-x86_64.msi"
    res = source(f, url=url, install="msiexec /i cmake-4.1.0-rc1-windows-x86_64.msi /qn")
    assert r3.norm_text(res["text"]) == r3.source_text(
        "cmake", "4.1.0-rc1", f.name, DATE_TEXT, r3.sha256(f), url=url,
        install="msiexec /i cmake-4.1.0-rc1-windows-x86_64.msi /qn")


def test_write_then_verify_passes(tmp_path):
    """§15.7: a written SOURCE.md passes bundle_verify (§2.8)."""
    root = r3.make_tundle(tmp_path / "tundle")
    f = r3.installer(root / "setup" / "windows" / "python-3.13.5" / "python-3.13.5-amd64.exe",
                     b"real enough", DATE)
    res = source(f, write=True)
    assert res["written"] is True
    written = f.parent / "SOURCE.md"
    assert written.is_file()
    assert r3.norm_text(written.read_text(encoding="utf-8")) == r3.norm_text(res["text"])
    v = r3.call("bundle_verify", root=str(root))
    r3.check_shape(v)
    assert v["findings"] == []
    assert v["ok"] is True
    assert [(c["source"], c["file"], c["match"]) for c in v["checked"]] == [
        ("setup/windows/python-3.13.5/SOURCE.md", "setup/windows/python-3.13.5/python-3.13.5-amd64.exe", True)]


def test_refuses_to_overwrite_without_force(tmp_path):
    """§15.7: an existing SOURCE.md is not overwritten unless `force`."""
    f = r3.installer(tmp_path / "git" / "Git-2.55.0.5-64-bit.exe", b"git", DATE)
    existing = r3.write(f.parent / "SOURCE.md", "# hand written\n")
    with pytest.raises(r3.tool_error()):
        source(f, write=True)
    assert existing.read_text(encoding="utf-8") == "# hand written\n"
    res = source(f, write=True, force=True)
    assert res["written"] is True
    assert existing.read_text(encoding="utf-8").startswith("# Git 2.55.0.5")


def test_cli_bundle_source(tmp_path, capsys):
    """§15.10: `tundlekit bundle source FILE --url URL --json`."""
    f = r3.installer(tmp_path / "inkscape" / "inkscape-1.4.3.msi", b"ink", DATE)
    code, data, out, err = r3.run_cli(capsys, ["bundle", "source", f, "--url", "https://inkscape.org/release/",
                                               "--json"])
    assert code == 0, err
    assert data["program"] == "inkscape" and data["version"] == "1.4.3"
    assert "- Source:     https://inkscape.org/release/" in data["text"]
    assert data["written"] is False


# ------------------------------------------------------------------------------------ setup table

WIN_README = """# Windows setup

Installers for setting up a Windows machine.

| File | What it is |
|---|---|
| `Git-2.55.0.5-64-bit.exe` | Git for Windows 2.55.0.5 |
| `ChromeSetup.exe` | Google Chrome ⚠ downloads during install |

⚠ marks a stub installer that pulls the real package from the internet.
"""


def setup_dir(root, names, readme=WIN_README):
    d = root / "setup" / "windows"
    for n in names:
        r3.installer(d / n)
    if readme is not None:
        r3.write(d / "README.md", readme)
    return d


def table(d, **kw):
    res = r3.call("bundle_setup_table", dir=str(d), **kw)
    assert set(res) >= {"added", "written"}
    return res


def test_setup_table_dry_run_rows(tmp_path):
    """§15.7: 1 row per unlisted entry, sorted, in the pinned format; nothing written without `write`."""
    d = setup_dir(tmp_path, ["Git-2.55.0.5-64-bit.exe", "ChromeSetup.exe",
                             "python-3.13.5-amd64.exe", "inkscape-1.4.3.msi"])
    before = (d / "README.md").read_bytes()
    res = table(d)
    assert res["written"] is False
    assert [r.strip() for r in res["added"]] == [
        "| `inkscape-1.4.3.msi` | inkscape 1.4.3 |",
        "| `python-3.13.5-amd64.exe` | python 3.13.5 |",
    ]
    assert (d / "README.md").read_bytes() == before


def test_setup_table_write_inserts_after_last_row(tmp_path):
    """§15.7: rows go directly after the last row of the first table; other text is untouched; B006 clean."""
    root = r3.make_tundle(tmp_path / "t")
    d = setup_dir(root, ["Git-2.55.0.5-64-bit.exe", "ChromeSetup.exe", "tailscale-setup-1.102.4.exe"])
    assert r3.b006_paths(root) == ["setup/windows/tailscale-setup-1.102.4.exe"]
    res = table(d, write=True)
    assert res["written"] is True
    text = (d / "README.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    expected = WIN_README.replace(
        "| `ChromeSetup.exe` | Google Chrome ⚠ downloads during install |\n",
        "| `ChromeSetup.exe` | Google Chrome ⚠ downloads during install |\n"
        "| `tailscale-setup-1.102.4.exe` | tailscale setup 1.102.4 |\n")
    assert text == expected
    assert r3.b006_paths(root) == []


def test_setup_table_creates_readme(tmp_path):
    """§15.7: with no README.md, one is created holding a `| File | What it is |` table."""
    root = r3.make_tundle(tmp_path / "t")
    d = setup_dir(root, ["7z2603-x64.exe", "CrystalDiskInfo9_8_0.exe"], readme=None)
    res = table(d, write=True)
    assert res["written"] is True
    lines = (d / "README.md").read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")
    assert "| File | What it is |" in lines
    i = lines.index("| File | What it is |")
    assert lines[i + 1] == "|---|---|"
    assert r3.row_cells(lines[i + 2]) == ["`7z2603-x64.exe`", "7z2603"]
    assert lines[i + 3] == "| `CrystalDiskInfo9_8_0.exe` | CrystalDiskInfo 9.8.0 |"
    assert r3.b006_paths(root) == []


def test_stub_installers_flagged(tmp_path):
    """§15.7: a name with Setup/Installer/Loader/latest and no version gets the ⚠ note; versioned ones don't."""
    d = setup_dir(tmp_path, ["comet_installer_latest.exe", "DiscordSetup.exe",
                             "VSCodeUserSetup-x64-1.94.2.exe", "winrar-x64-723.exe"], readme=WIN_README)
    rows = {r3.row_cells(r)[0]: r.strip() for r in table(d)["added"]}
    assert set(rows) == {"`comet_installer_latest.exe`", "`DiscordSetup.exe`",
                         "`VSCodeUserSetup-x64-1.94.2.exe`", "`winrar-x64-723.exe`"}
    note = " ⚠ check: may download during install"
    assert rows["`comet_installer_latest.exe`"].endswith(note + " |")
    assert rows["`DiscordSetup.exe`"].endswith(note + " |")
    assert "⚠" not in rows["`VSCodeUserSetup-x64-1.94.2.exe`"]
    assert rows["`VSCodeUserSetup-x64-1.94.2.exe`"] == "| `VSCodeUserSetup-x64-1.94.2.exe` | VSCodeUserSetup 1.94.2 |"
    assert "⚠" not in rows["`winrar-x64-723.exe`"]


def test_cli_setup_table(tmp_path, capsys):
    """§15.10: `tundlekit bundle setup-table DIR --json`."""
    d = setup_dir(tmp_path, ["Git-2.55.0.5-64-bit.exe", "ChromeSetup.exe", "OBS-Studio-30.2.3-Windows-Installer.exe"])
    code, data, out, err = r3.run_cli(capsys, ["bundle", "setup-table", d, "--json"])
    assert code == 0, err
    assert [r.strip() for r in data["added"]] == [
        "| `OBS-Studio-30.2.3-Windows-Installer.exe` | OBS Studio 30.2.3 |"]
    assert data["written"] is False
