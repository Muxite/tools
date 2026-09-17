"""Shared helpers for the round-5 bundle/papers/terms/docs tests (MANIFEST §17.3, §17.4, §17.5, §17.7).

Not a conftest. Test modules import it with `import helpers_r5b as h` (pytest puts tests/ on sys.path).
It builds on helpers_r4m (same conventions). Nothing here imports tundlekit at module level.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from helpers_r4m import (  # noqa: F401  (re-exported)
    REPO, OWNER as _OWNER, approved_zh, by_rule, check_shape, heading, installer, marker_txt, norm,
    paper_pages, rules, run_cli, sha256, skill_text, slash, summary_lines, term_count, term_keys_lower,
    tool_error, write,
)
import helpers_r4m as _r4m

_r4m.OWNER.setdefault("bundle_backup", "bundle")
_r4m.OWNER.setdefault("render_office", "render")
call = _r4m.call

NOW = "2026-09-16T10:00"
TODAY = "2026-09-16"


# ------------------------------------------------------------------------------------ fixtures-ish helpers
def no_office(monkeypatch, running=()):
    """§17.3: bundle_backup consults tundlekit.render.office_running(); pin it for the test."""
    from tundlekit import render

    monkeypatch.setattr(render, "office_running", lambda *a, **k: list(running))


def tundle(root) -> Path:
    """A minimal tundle root (§2.1: VERSION + CHANGELOG.md); no git needed."""
    root = Path(root)
    write(root / "VERSION", "2026.09.16.1\n")
    write(root / "CHANGELOG.md", "# Changelog\n\n<!-- tundle:changelog -->\n\n## 2026.09.16.1 · initial\n")
    write(root / "README.md", "# t\n")
    return root


def files_under(top) -> list:
    """Every file under top, relative, sorted, with `/`."""
    top = Path(top)
    return sorted(slash(p.relative_to(top)) for p in top.rglob("*") if p.is_file())


def make_readonly(path) -> Path:
    os.chmod(path, stat.S_IREAD)
    return Path(path)


def make_writable(path) -> None:
    try:
        os.chmod(path, stat.S_IREAD | stat.S_IWRITE)
    except OSError:
        pass


def temp_leftovers(folder) -> list:
    """Files in folder that look like temp files from an atomic write."""
    return [n for n in os.listdir(folder)
            if "tmp" in n.lower() and n not in ("tmp",)]


def b014(root):
    res = call("bundle_lint", root=str(root))
    check_shape(res)
    f = by_rule(res, "B014")
    assert len(f) <= 1
    return f


def b014_count(root) -> int:
    import re

    f = b014(root)
    if not f:
        return 0
    nums = [int(n) for n in re.findall(r"\b\d+\b", f[0]["message"])]
    return nums[0]


def source(path, **kw):
    return call("bundle_source", file=str(path), **kw)


def backup_files_arg() -> str:
    """§17.3 names the CLI form `FILE...` only; the schema's array property holds the files (`files` expected)."""
    import importlib

    importlib.import_module("tundlekit.bundle")
    from tundlekit import registry

    assert "bundle_backup" in registry.TOOLS, "bundle_backup is not registered (§17.3)"
    props = registry.TOOLS["bundle_backup"].input_schema.get("properties", {})
    arrays = [k for k, v in props.items() if v.get("type") == "array"]
    return "files" if "files" in props or not arrays else arrays[0]


def backup(files, reason, **kw):
    if not isinstance(files, list):
        files = [files]
    return call("bundle_backup", **{backup_files_arg(): [str(f) for f in files]}, reason=reason, **kw)


def snapshot_name(stem: str, reason: str, ext: str, date: str = TODAY) -> str:
    return f"{stem} (before {reason} {date}){ext}"


# ------------------------------------------------------------------------------------ README mirroring
# Rows copied from the real tundle setup/windows/README.md (§16.6, §17.3 "What it is" cells).
WINDOWS_ROWS = {
    "Git-2.55.0.5-64-bit.exe": "Git for Windows 2.55.0.5. **Install this first**: tundle's own "
                               "`tools\\tundle.ps1` needs its bash",
    "python-3.13.5-amd64.exe": "Python 3.13.5, 64-bit",
    "VisualStudioSetup.exe": "Visual Studio installer ⚠ downloads during install",
    "cmake-4.1.0-rc1-windows-x86_64.msi": "CMake 4.1.0-rc1 (release candidate)",
    "matlab_R2024b_Windows.exe": "MATLAB R2024b ⚠ needs a licence and downloads during install",
    "NVIDIA_app_v11.0.4.159.exe": "NVIDIA App 11.0.4.159 (drivers and control panel)",
    "balenaEtcher-2.1.0.Setup.exe": "balenaEtcher 2.1.0, writes ISOs to USB sticks",
    "7z2603-x64.exe": "7-Zip 26.03, x64",
    "7z2603-arm64.exe": "7-Zip 26.03, arm64",
    "winrar-x64-723.exe": "WinRAR 7.23, x64",
    "CrystalDiskInfo9_8_0.exe": "CrystalDiskInfo 9.8.0, drive health",
    "tsetup-x64.6.8.1.exe": "Telegram Desktop 6.8.1, x64",
    "WhatsApp Installer.exe": "WhatsApp desktop",
}


def windows_readme(names) -> str:
    rows = "".join(f"| `{n}` | {WINDOWS_ROWS[n]} |\n" for n in names)
    return ("# Windows setup\n\nInstallers for setting up a Windows machine.\n\n"
            "| File | What it is |\n|---|---|\n" + rows +
            "\n⚠ marks a stub installer that pulls the real package from the internet.\n")


def windows_setup(root, names) -> Path:
    """setup/windows/ with the given installers (distinct bytes) and a README listing them."""
    d = Path(root) / "setup" / "windows"
    write(Path(root) / "setup" / "README.md", "# Setup\n")
    for i, n in enumerate(names):
        installer(d / n, f"MZ installer {i} {n}\n".encode())
    write(d / "README.md", windows_readme(names))
    return d


# ------------------------------------------------------------------------------------ papers
def pdir(tmp_path) -> Path:
    d = Path(tmp_path) / "papers"
    d.mkdir(exist_ok=True)
    return d


def summarise(tmp_path, pid, page1, pages=8, refs_page=7, **kw):
    d = pdir(tmp_path)
    marker_txt(d / f"{pid}.txt", paper_pages(page1, pages, refs_page=refs_page))
    return call("papers_summary", id=pid, dir=str(d), **kw)


def title_of(res) -> str:
    first = summary_lines(res)[0]
    assert first.startswith("# ")
    return first.split(" · ", 1)[1]


def authors_of(res) -> str:
    return summary_lines(res)[2].split(" · arXiv ", 1)[0]


# ------------------------------------------------------------------------------------ translate
def terms(tmp_path, src, *targets, **kw):
    s = write(Path(tmp_path) / "src.md", src)
    ts = [write(Path(tmp_path) / f"t{i}.md", t) for i, t in enumerate(targets)]
    res = call("translate_terms", src=str(s), targets=[str(t) for t in ts], **kw)
    check_shape(res)
    return res


def about(res, term, rule=None):
    """Findings whose excerpt (or quoted message term) is `term`."""
    out = [f for f in res["findings"]
           if f["excerpt"].lower() == term.lower() or f"'{term}'".lower() in f["message"].lower()]
    return [f for f in out if rule is None or f["rule"] == rule]


def skip_without(path):
    if not Path(path).exists():
        pytest.skip(f"not present: {path}")
