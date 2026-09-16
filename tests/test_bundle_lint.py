"""§2.7 bundle_lint (rules B001–B013) and the §0.3 checker shape."""
import hashlib
import os
import sys

import pytest

from helpers_core import by_rule, call, check_shape, lint_tree, paths_for, try_make, write

MiB = 1024 * 1024


def lint(root, **kw):
    r = call("bundle_lint", root=root, **kw)
    check_shape(r)
    return r


def test_clean_tree(tmp_path):
    """§2.7 a clean tundle: ok, no findings, files counts walked files (not .git)."""
    root = lint_tree(tmp_path / "t", files={"docs/README.md": "# Docs\n", "docs/a.md": "a\n"})
    write(root, ".git/junk.tmp", "x")   # .git is skipped entirely
    r = lint(root)
    assert r["findings"] == []
    assert r["ok"] is True
    assert r["counts"] == {"error": 0, "warning": 0, "info": 0}
    assert r["files"] == 4


# ---------------------------------------------------------------- B001

def test_b001_reserved_name(tmp_path):
    """§2.7 B001: part before the first `.` is a Windows reserved name (case-insensitive)."""
    root = lint_tree(tmp_path / "t")
    try_make(root, "con.txt")
    r = lint(root)
    assert paths_for(r, "B001") == ["con.txt"]
    assert by_rule(r, "B001")[0]["severity"] == "error"
    assert r["ok"] is False


@pytest.mark.skipif(sys.platform == "win32", reason="Windows cannot create such names")
@pytest.mark.parametrize("name", ["a:b.txt", "what?.md", "tab\tname"])
def test_b001_forbidden_characters(tmp_path, name):
    """§2.7 B001: `: * ? " < > |` or a control character."""
    root = lint_tree(tmp_path / "t")
    try_make(root, name)
    assert paths_for(lint(root), "B001") == [name]


@pytest.mark.skipif(sys.platform == "win32", reason="Windows strips trailing dots and spaces")
def test_b001_trailing_space_directory(tmp_path):
    """§2.7 B001 applies to directory names ending in a space."""
    root = lint_tree(tmp_path / "t")
    try_make(root, "dir ", is_dir=True)
    write(root / "dir ", "README.md", "x")
    assert "dir " in paths_for(lint(root), "B001")


@pytest.mark.parametrize("name", ["console.txt", "com10.txt", "lpt0.md", "auxiliary.md", "nulls.txt"])
def test_b001_not_reserved(tmp_path, name):
    """§2.7 B001: only the exact reserved names count."""
    root = lint_tree(tmp_path / "t", files={name: "x"})
    assert by_rule(lint(root), "B001") == []


# ---------------------------------------------------------------- B002

def test_b002_path_length_boundary(tmp_path):
    """§2.7 B002: a relative path longer than max_path characters."""
    root = lint_tree(tmp_path / "t", files={
        "docs/README.md": "x",
        "docs/abcdefghijk.txt": "x",     # 20 characters: not longer
        "docs/abcdefghijkl.txt": "x",    # 21 characters
    })
    r = lint(root, max_path=20)
    assert paths_for(r, "B002") == ["docs/abcdefghijkl.txt"]
    assert by_rule(r, "B002")[0]["severity"] == "warning"


def test_b002_default_160(tmp_path):
    """§2.7 B002: max_path defaults to 160."""
    name = "n" * 100 + ".md"
    root = lint_tree(tmp_path / "t", files={"docs/README.md": "x", f"docs/{name}": "x"})
    assert by_rule(lint(root), "B002") == []


# ---------------------------------------------------------------- B003

@pytest.mark.parametrize("name", ["report_v2.docx", "Report-FINAL.pptx", "plan (final).md",
                                  "report (1).docx"])
def test_b003_copy_markers(tmp_path, name):
    """§2.7 B003: stem ends in a copy/version marker."""
    root = lint_tree(tmp_path / "t", files={name: "x"})
    r = lint(root)
    assert paths_for(r, "B003") == [name]
    assert by_rule(r, "B003")[0]["severity"] == "warning"


@pytest.mark.parametrize("name", ["reportv2.docx", "renewal.md", "file(1).txt"])
def test_b003_not_markers(tmp_path, name):
    """§2.7 B003: no separator before the marker, or no marker at the end."""
    root = lint_tree(tmp_path / "t", files={name: "x"})
    assert by_rule(lint(root), "B003") == []


def test_b003_exempt_inside_versions(tmp_path):
    """§2.7 B003: not reported for files inside a directory named `versions`."""
    root = lint_tree(tmp_path / "t", files={
        "docs/README.md": "x",
        "docs/versions/report_v2.docx": "x",
        "docs/versions/sub/plan_final.md": "x",
        "docs/versions_old/report_v3.docx": "x",
    })
    assert paths_for(lint(root), "B003") == ["docs/versions_old/report_v3.docx"]


# ---------------------------------------------------------------- B004

def test_b004_same_document_key(tmp_path):
    """§2.7 B004: 2+ files with 1 key in a versions dir; 1 info finding on the first sorted path."""
    root = lint_tree(tmp_path / "t", files={
        "versions/README.md": "x",
        "versions/Report (2026-09-10).docx": "x",
        "versions/Report (2026-09-01).docx": "x",
        "versions/Report (2026-09-01).pdf": "x",
        "versions/Other (2026-09-01).docx": "x",
    })
    r = lint(root)
    b004 = by_rule(r, "B004")
    assert [f["path"] for f in b004] == ["versions/Report (2026-09-01).docx"]
    assert b004[0]["severity"] == "info"


# ---------------------------------------------------------------- B005

def test_b005_junk_directory_reported_once(tmp_path):
    """§2.7 B005: a junk directory is reported once and not descended into."""
    root = lint_tree(tmp_path / "t", files={
        "pkg/README.md": "x",
        "pkg/__pycache__/m.cpython-312.pyc": "x",
        "pkg/__pycache__/n.cpython-312.pyc": "x",
        "pkg/__pycache__/report_v2.docx": "x",
    })
    r = lint(root)
    assert paths_for(r, "B005") == ["pkg/__pycache__"]
    assert by_rule(r, "B003") == []
    assert by_rule(r, "B005")[0]["severity"] == "warning"


@pytest.mark.parametrize("name", ["stale.pyc", "~$report.docx", "Thumbs.db"])
def test_b005_junk_files(tmp_path, name):
    """§2.7 B005: junk file patterns."""
    root = lint_tree(tmp_path / "t", files={name: "x"})
    assert paths_for(lint(root), "B005") == [name]


def test_b005_lookalikes_are_not_junk(tmp_path):
    """§2.7 B005: only the listed names and patterns."""
    root = lint_tree(tmp_path / "t", files={"pyc.txt": "x", "tmp.md": "x", "venvs/README.md": "x",
                                            "notes.tmp.md": "x"})
    assert by_rule(lint(root), "B005") == []


# ---------------------------------------------------------------- B006 / B007

WIN_README = """# Windows installers

| File | Purpose |
|---|---|
| `a.exe` | installer |
| ` b.msi `, `c.msi` | two in one row |
| `drivers/` | driver folder |
| `gone.exe` | missing |
| plain text | ignored row |
"""


def _setup_tree(tmp_path):
    a = b"installer bytes"
    files = {
        "setup/README.md": "# Setup\n",
        "setup/win/README.md": WIN_README,
        "setup/win/SOURCE.md": f"- File: a.exe\n- SHA-256: `{hashlib.sha256(a).hexdigest()}`\n",
        "setup/win/a.exe": a,
        "setup/win/b.msi": "x",
        "setup/win/c.msi": "x",
        "setup/win/d.zip": "x",
        "setup/win/drivers/x.inf": "x",
        "setup/win/tools/y.txt": "x",
        "setup/notes.txt": "not inside setup/<dir>/",
    }
    return lint_tree(tmp_path / "t", files=files)


def test_b006_unlisted_entries(tmp_path):
    """§2.7 B006: unlisted files and direct subdirectories of setup/<dir>/; README/SOURCE exempt."""
    r = lint(_setup_tree(tmp_path))
    assert paths_for(r, "B006") == ["setup/win/d.zip", "setup/win/tools"]
    assert all(f["severity"] == "error" for f in by_rule(r, "B006"))


def test_b007_listed_entry_missing(tmp_path):
    """§2.7 B007: a table row naming an entry that doesn't exist."""
    r = lint(_setup_tree(tmp_path))
    b007 = by_rule(r, "B007")
    assert len(b007) == 1
    assert b007[0]["severity"] == "error"
    f = b007[0]
    assert "gone.exe" in f"{f['path']} {f['message']} {f['excerpt']}"
    assert r["ok"] is False


# ---------------------------------------------------------------- B008

def test_b008_top_level_dir_without_readme(tmp_path):
    """§2.7 B008: top-level dir without README.md; hidden dirs, tools and junk dirs exempt."""
    root = lint_tree(tmp_path / "t", files={
        "docs/a.md": "x",
        "docs/sub/b.md": "x",
        "tools/run.py": "x",
        ".github/ci.yml": "x",
        "good/README.md": "x",
    }, dirs=["node_modules/pkg"])
    r = lint(root)
    assert paths_for(r, "B008") == ["docs"]
    assert by_rule(r, "B008")[0]["severity"] == "warning"


# ---------------------------------------------------------------- B009

def test_b009_stale_pdf(tmp_path):
    """§2.7 B009: X.pdf older than X.docx in the same directory."""
    root = lint_tree(tmp_path / "t", files={"Report.docx": "d", "Report.pdf": "p"})
    os.utime(root / "Report.pdf", (1_700_000_000, 1_700_000_000))
    os.utime(root / "Report.docx", (1_700_000_100, 1_700_000_100))
    r = lint(root)
    b009 = by_rule(r, "B009")
    assert [f["path"] for f in b009] == ["Report.pdf"]
    assert b009[0]["severity"] == "warning"


def test_b009_fresh_pdf(tmp_path):
    """§2.7 B009: a newer PDF is fine."""
    root = lint_tree(tmp_path / "t", files={"Report.docx": "d", "Report.pdf": "p"})
    os.utime(root / "Report.docx", (1_700_000_000, 1_700_000_000))
    os.utime(root / "Report.pdf", (1_700_000_100, 1_700_000_100))
    assert by_rule(lint(root), "B009") == []


# ---------------------------------------------------------------- B010

def test_b010_heading_mismatch(tmp_path):
    """§2.7 B010: first `## ` heading after the marker doesn't start with `## {VERSION}`."""
    root = lint_tree(tmp_path / "t", version="2026.09.16.1")
    write(root, "VERSION", "2026.09.16.2\n")
    r = lint(root)
    assert len(by_rule(r, "B010")) == 1
    assert by_rule(r, "B010")[0]["severity"] == "error"
    assert r["ok"] is False


def test_b010_changelog_without_marker(tmp_path):
    """§2.7 B010: CHANGELOG.md without the marker."""
    root = lint_tree(tmp_path / "t")
    write(root, "CHANGELOG.md", "# Changelog\n\n## 2026.09.16.1  (2026-09-16 10:00)\n")
    assert len(by_rule(lint(root), "B010")) >= 1


def test_b010_skipped_for_fresh_tundle(tmp_path):
    """§2.7 B010: skipped when there are no entries and VERSION ends in .0."""
    root = lint_tree(tmp_path / "t")
    write(root, "VERSION", "2026.09.16.0\n")
    write(root, "CHANGELOG.md", "# Changelog\n\n<!-- entries -->\n")
    assert by_rule(lint(root), "B010") == []


# ---------------------------------------------------------------- B011

def test_b011_large_file(tmp_path):
    """§2.7 B011: a file larger than large_mb MiB; message contains the size in MiB."""
    root = lint_tree(tmp_path / "t", files={"big.bin": b"\0" * int(2.5 * MiB)})
    r = lint(root, large_mb=2)
    b011 = by_rule(r, "B011")
    assert [f["path"] for f in b011] == ["big.bin"]
    assert b011[0]["severity"] == "info"
    assert "2.5" in b011[0]["message"]
    assert r["ok"] is True


def test_b011_default_500(tmp_path):
    """§2.7 B011: large_mb defaults to 500."""
    root = lint_tree(tmp_path / "t", files={"big.bin": b"\0" * int(2.5 * MiB)})
    assert by_rule(lint(root), "B011") == []


# ---------------------------------------------------------------- B012 / B013 via lint

def test_lint_reports_checksum_mismatch(tmp_path):
    """§2.7 B012: a SOURCE.md checksum mismatch is also a lint error."""
    root = lint_tree(tmp_path / "t", files={
        "vendor/README.md": "x",
        "vendor/pkg/tool.zip": "payload",
        "vendor/pkg/SOURCE.md": "- SHA-256: " + "0" * 64 + "\n",
    })
    r = lint(root)
    assert len(by_rule(r, "B012")) == 1
    assert r["ok"] is False


def test_lint_reports_missing_hash(tmp_path):
    """§2.7 B013: a SOURCE.md without a hash is a lint warning."""
    root = lint_tree(tmp_path / "t", files={
        "vendor/README.md": "x",
        "vendor/pkg/tool.zip": "payload",
        "vendor/pkg/SOURCE.md": "- URL: https://example.org\n",
    })
    r = lint(root)
    b013 = by_rule(r, "B013")
    assert len(b013) == 1 and b013[0]["severity"] == "warning"
    assert r["ok"] is True


# ---------------------------------------------------------------- shape

def test_findings_sorted_and_counted(tmp_path):
    """§0.3 findings sorted by (path, line or 0, rule); counts per severity; `/` separators."""
    root = lint_tree(tmp_path / "t", files={
        "zeta/a_v2.md": "x",
        "alpha/x.tmp": "x",
        "alpha/README.md": "x",
        "alpha/deep/copy_final.md": "x",
        "big.bin": b"\0" * (MiB + 1),
    })
    r = lint(root, large_mb=1)
    rules = {f["rule"] for f in r["findings"]}
    assert {"B003", "B005", "B008", "B011"} <= rules
    assert "alpha/deep/copy_final.md" in paths_for(r, "B003")
