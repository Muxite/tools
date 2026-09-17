"""MANIFEST §16.6 bundle naming (on top of §15.7): trailing Setup/UserSetup removal, MATLAB-style `R20xxa/b`
versions, compact 3/4-digit versions, README "What it is" reuse, `bundle source DIR --all`, and B003 names.
"""
from __future__ import annotations

import pytest

import helpers_r4m as h


def source(path, **kw):
    res = h.call("bundle_source", file=str(path), **kw)
    return res


@pytest.mark.parametrize("name,program,version", [
    ("matlab_R2024b_Windows.exe", "matlab", "R2024b"),
    ("winrar-x64-723.exe", "winrar", "7.23"),
    ("7z2603-x64.exe", "7z", "26.03"),
    ("VSCodeUserSetup-x64-1.94.2.exe", "VSCode", "1.94.2"),
    ("InternetHostingToolSetup-v5.6.1.exe", "InternetHostingTool", "5.6.1"),
])
def test_round4_name_guesses(tmp_path, name, program, version):
    """§16.6: `R2024b` is a version; `723` -> 7.23 and `2603` -> 26.03 when there is no dotted version; a trailing
    Setup/UserSetup token leaves the program once a version was found. The heading is `# program version`."""
    res = source(h.installer(tmp_path / name))
    assert (res["program"], res["version"]) == (program, version)
    assert h.heading(res["text"]) == f"# {program} {version}"


@pytest.mark.parametrize("name,program", [
    ("DiscordSetup.exe", "DiscordSetup"),
    ("WhatsApp Installer.exe", "WhatsApp Installer"),
])
def test_setup_token_kept_without_version(tmp_path, name, program):
    """§16.6: the Setup/Installer token is removed only when a version was found."""
    res = source(h.installer(tmp_path / name))
    assert (res["program"], res["version"]) == (program, "")


def test_dotted_version_wins_over_compact_group(tmp_path):
    """§16.6: a compact 3-digit group is used only when the name has no dotted version."""
    res = source(h.installer(tmp_path / "tool-123-x64-2.4.1.exe"))
    assert res["version"] == "2.4.1"


README = ("# Windows setup\n\n| File | What it is |\n|---|---|\n"
          "| `mystery-build.exe` | Acme Studio 2024.3, desktop editor |\n"
          "| `loader.exe` | Acme Loader ⚠ downloads during install |\n")


def test_readme_cell_provides_program_and_version(tmp_path):
    """§16.6: a README row for the file gives program and version: the cell text before the first `,` or `⚠`,
    split at the first token that starts with a digit."""
    d = tmp_path / "setup" / "windows"
    h.write(d / "README.md", README)
    res = source(h.installer(d / "mystery-build.exe"))
    assert (res["program"], res["version"]) == ("Acme Studio", "2024.3")
    assert h.heading(res["text"]) == "# Acme Studio 2024.3"
    res = source(h.installer(d / "loader.exe"))
    assert (res["program"], res["version"]) == ("Acme Loader", "")


def test_source_all_writes_each_uncovered_directory(tmp_path):
    """§16.6: `bundle_source` with a directory writes a SOURCE.md next to every B014-counted installer that has
    none; existing ones are skipped. Result `{"results": [...]}`; written files pass bundle_verify."""
    root = tmp_path / "t"
    setup = root / "setup" / "windows"
    h.write(setup / "README.md", "| File | What it is |\n|---|---|\n| `git/` | Git |\n| `py/` | Python |\n"
                                 "| `node/` | Node |\n")
    git = h.installer(setup / "git" / "Git-2.55.0.5-64-bit.exe")
    py = h.installer(setup / "py" / "python-3.13.5-amd64.exe")
    h.installer(setup / "node" / "node-v20.17.0-x64.msi")
    kept = h.write(setup / "node" / "SOURCE.md", "# node kept\n")
    res = h.call("bundle_source", file=str(root / "setup"), write=True)
    assert set(res) >= {"results"}
    written = sorted(h.slash(r["path"]) for r in res["results"] if r.get("written"))
    assert len(written) == 2
    assert written[0].endswith("git/SOURCE.md") and written[1].endswith("py/SOURCE.md")
    assert (git.parent / "SOURCE.md").is_file() and (py.parent / "SOURCE.md").is_file()
    assert kept.read_text(encoding="utf-8") == "# node kept\n"
    assert h.call("bundle_verify", root=str(root))["ok"] is True


def test_source_all_dry_run_writes_nothing(tmp_path):
    """§16.6: without write, the batch returns the texts only."""
    d = tmp_path / "setup" / "linux" / "cmake"
    h.installer(d / "cmake-4.1.0-rc1-windows-x86_64.msi")
    res = h.call("bundle_source", file=str(tmp_path / "setup"))
    assert len(res["results"]) == 1
    assert res["results"][0]["written"] is False
    assert res["results"][0]["version"] == "4.1.0-rc1"
    assert not (d / "SOURCE.md").exists()


def test_cli_source_all(tmp_path, capsys):
    """§16.6: `tundlekit bundle source DIR --all --json`."""
    h.installer(tmp_path / "setup" / "w" / "a" / "winrar-x64-723.exe")
    code, data, out, err = h.run_cli(capsys, ["bundle", "source", tmp_path / "setup", "--all", "--json"])
    assert code == 0, err + out
    assert [(r["program"], r["version"]) for r in data["results"]] == [("winrar", "7.23")]


def test_b003_hyphen_version_attached_to_name(tmp_path):
    """§16.6: `AI Scientist-v2.md` is a name (no B003); `report_v2.md` and `report -v2.md` still fire."""
    root = h.lint_tree(tmp_path / "t", {
        "notes/AI Scientist-v2.md": "x",
        "notes/report_v2.md": "x",
        "notes/report -v2.md": "x",
    })
    assert h.b003_paths(root) == ["notes/report -v2.md", "notes/report_v2.md"]


@pytest.mark.parametrize("name", ["report v2.md", "report.v2.md", "report (v2).md", "Draft-final.md"])
def test_b003_other_forms_still_fire(tmp_path, name):
    """§16.6: separated `v2` forms fire, and the other markers are unchanged."""
    root = h.lint_tree(tmp_path / "t", {name: "x"})
    assert h.b003_paths(root) == [name]
