"""§2 bundle through the CLI: §0.4 exit codes and --json, §2.9 human-readable output."""
import json
import re

from helpers_core import (call, commit_all, gitenv, git_out, lint_tree, make_history, make_tundle,  # noqa: F401
                          run_cli, run_cli_json, write)


def _lines(out):
    return out.splitlines()


def test_status_text(capsys, tmp_path, gitenv):  # noqa: F811
    """§2.9 status: version/history/size lines and `changes:  none`."""
    root = make_tundle(tmp_path / "t", version="2026.09.15.1")
    rc, out, _ = run_cli(capsys, ["bundle", "status", "--root", root])
    assert rc == 0
    lines = _lines(out)
    assert any(ln.startswith("version:  ") and "2026.09.15.1" in ln for ln in lines)
    assert any(ln.startswith("history:  ") for ln in lines)
    assert any(ln.startswith("size:     ") for ln in lines)
    assert any(ln.startswith("changes:  none") for ln in lines)


def test_status_text_unreleased(capsys, tmp_path, gitenv):  # noqa: F811
    """§2.9 status: `changes:  {n} unreleased`."""
    root = make_tundle(tmp_path / "t")
    write(root, "a.txt", "a")
    write(root, "b.txt", "b")
    rc, out, _ = run_cli(capsys, ["bundle", "status", "--root", root])
    assert rc == 0
    assert any(ln.startswith("changes:  2 unreleased") for ln in _lines(out))


def test_status_json_matches_tool(capsys, tmp_path, gitenv):  # noqa: F811
    """§0.4 --json prints the tool result."""
    root = make_tundle(tmp_path / "t", version="2026.09.15.1")
    rc, data, _ = run_cli_json(capsys, ["bundle", "status", "--root", root])
    assert rc == 0
    assert data["version"] == "2026.09.15.1"
    assert data["history"] == 1


def test_release_text(capsys, tmp_path, gitenv):  # noqa: F811
    """§2.9 release: `released {new} ({stats_text})`."""
    root = make_tundle(tmp_path / "t", version="2026.09.15.1")
    write(root, "a.txt", "a")
    rc, out, _ = run_cli(capsys, ["bundle", "release", "Add a", "--root", root])
    assert rc == 0
    assert "released 2026.09.16.1 (1 added, 0 modified, 0 removed, 0 renamed)" in out


def test_release_text_prune_hint(capsys, tmp_path, gitenv):  # noqa: F811
    """§2.9 release: when prune_hint, also a line containing `prune`."""
    root = make_tundle(tmp_path / "t", version="2026.09.15.1")
    make_history(root, 10)
    write(root, "a.txt", "a")
    rc, out, _ = run_cli(capsys, ["bundle", "release", "Add a", "--root", root])
    assert rc == 0
    assert "released 2026.09.16.1 (" in out
    assert any("prune" in ln for ln in _lines(out))


def test_release_json(capsys, tmp_path, gitenv):  # noqa: F811
    """§2.3 via CLI --json."""
    root = make_tundle(tmp_path / "t", version="2026.09.16.1")
    write(root, "a.txt", "a")
    rc, data, _ = run_cli_json(capsys, ["bundle", "release", "Add a", "--root", root])
    assert rc == 0
    assert data["version"] == "2026.09.16.2"
    assert data["commit"] == git_out(root, "rev-parse", "HEAD")


def test_release_empty_summary_cli(capsys, tmp_path, gitenv):  # noqa: F811
    """§2.3 step 1 + §0.4: ToolError -> exit 1, `tundlekit: ` on stderr."""
    root = make_tundle(tmp_path / "t")
    write(root, "a.txt", "a")
    rc, _, err = run_cli(capsys, ["bundle", "release", "   ", "--root", root])
    assert rc == 1
    assert "tundlekit: " in err and "usage: release" in err


def test_compare_texts(capsys, tmp_path, gitenv):  # noqa: F811
    """§2.9 compare: the 3 messages."""
    root = make_tundle(tmp_path / "t", version="2026.09.16.2", commit=False)
    cases = [("2026.09.16.2", "same version: 2026.09.16.2"),
             ("2026.09.16.1", "this copy is newer: 2026.09.16.2 > 2026.09.16.1"),
             ("2026.09.18.1", "the other copy is newer: 2026.09.18.1 > 2026.09.16.2")]
    for i, (theirs, text) in enumerate(cases):
        other = tmp_path / f"o{i}"
        write(other, "VERSION", theirs + "\n")
        rc, out, _ = run_cli(capsys, ["bundle", "compare", other, "--root", root])
        assert rc == 0
        assert text in out


def test_prune_texts(capsys, tmp_path, gitenv):  # noqa: F811
    """§2.9 prune: `nothing to clear`, `dry run`, `cleared: {keep} versions kept`; KEEP positional, --yes."""
    root = make_tundle(tmp_path / "t")
    make_history(root, 4)                   # 5 commits
    rc, out, _ = run_cli(capsys, ["bundle", "prune", "--root", root])
    assert rc == 0 and "nothing to clear" in out
    rc, out, _ = run_cli(capsys, ["bundle", "prune", "2", "--root", root])
    assert rc == 0 and "dry run" in out
    assert git_out(root, "rev-list", "--count", "HEAD") == "5"
    rc, out, _ = run_cli(capsys, ["bundle", "prune", "2", "--yes", "--root", root])
    assert rc == 0 and "cleared: 2 versions kept" in out
    assert git_out(root, "rev-list", "--count", "HEAD") == "2"


def test_prune_json_dry_run(capsys, tmp_path, gitenv):  # noqa: F811
    """§2.5 via CLI --json."""
    root = make_tundle(tmp_path / "t")
    make_history(root, 3)
    rc, data, _ = run_cli_json(capsys, ["bundle", "prune", "1", "--root", root])
    assert rc == 0
    assert data["dry_run"] is True and data["kept_subjects"] == ["c3"]


def test_init_cli_positional(capsys, tmp_path, gitenv):  # noqa: F811
    """§2.6 CLI positional PATH."""
    root = tmp_path / "newt"
    rc, data, _ = run_cli_json(capsys, ["bundle", "init", root])
    assert rc == 0
    assert data["version"] == "2026.09.16.0"
    assert (root / "VERSION").read_text(encoding="utf-8") == "2026.09.16.0\n"


def test_init_cli_default_cwd(capsys, tmp_path, gitenv, monkeypatch):  # noqa: F811
    """§2.6 PATH defaults to the current directory."""
    root = tmp_path / "here"
    root.mkdir()
    monkeypatch.chdir(root)
    rc, _, _ = run_cli(capsys, ["bundle", "init"])
    assert rc == 0
    assert (root / "VERSION").exists() and (root / "CHANGELOG.md").exists()


def _finding_line(f):
    return f"{f['path']}:{f['line'] or 0}: {f['rule']} {f['severity']}: {f['message']}"


def test_lint_text_lines_and_exit_codes(capsys, tmp_path):
    """§2.9 lint: 1 line per finding in the given format; §0.4 exit 1 on errors."""
    root = lint_tree(tmp_path / "t", files={"docs/a.md": "x", "b_v2.md": "x", "junk.tmp": "x"})
    write(root, "VERSION", "2026.09.16.5\n")   # B010 error
    rc, data, _ = run_cli_json(capsys, ["bundle", "lint", "--root", root])
    assert rc == 1
    assert data["ok"] is False
    rc2, out, _ = run_cli(capsys, ["bundle", "lint", "--root", root])
    assert rc2 == 1
    lines = _lines(out)
    for f in data["findings"]:
        assert _finding_line(f) in lines
    assert len(lines) >= len(data["findings"]) + 1


def test_lint_warnings_exit_0_strict_exit_1(capsys, tmp_path):
    """§0.4 warnings alone exit 0; --strict makes warnings exit 1."""
    root = lint_tree(tmp_path / "t", files={"docs/a.md": "x"})   # B008 warning only
    rc, data, _ = run_cli_json(capsys, ["bundle", "lint", "--root", root])
    assert rc == 0
    assert data["counts"]["warning"] >= 1 and data["counts"]["error"] == 0
    rc, _, _ = run_cli(capsys, ["bundle", "lint", "--root", root, "--strict"])
    assert rc == 1


def test_lint_clean_exit_0(capsys, tmp_path):
    """§0.4 exit 0 on success, even with --strict."""
    root = lint_tree(tmp_path / "t")
    rc, _, _ = run_cli(capsys, ["bundle", "lint", "--root", root, "--strict"])
    assert rc == 0


def test_verify_text_and_exit(capsys, tmp_path):
    """§2.9 verify: finding lines; §0.4 exit 1 on a mismatch."""
    root = lint_tree(tmp_path / "t", files={"vendor/pkg/t.zip": "x", "vendor/pkg/SOURCE.md": "- SHA-256: " + "1" * 64})
    rc, data, _ = run_cli_json(capsys, ["bundle", "verify", "--root", root])
    assert rc == 1
    assert [f["rule"] for f in data["findings"]] == ["B012"]
    rc, out, _ = run_cli(capsys, ["bundle", "verify", "--root", root])
    assert rc == 1
    assert _finding_line(data["findings"][0]) in _lines(out)
    assert re.search(r"B012 error: ", out)


def test_status_root_from_cwd_cli(capsys, tmp_path, gitenv, monkeypatch):  # noqa: F811
    """§2.1 --root omitted: walk up from the current directory."""
    root = make_tundle(tmp_path / "t", version="2026.09.13.4", files={"sub/x.txt": "x"})
    monkeypatch.chdir(root / "sub")
    rc, data, _ = run_cli_json(capsys, ["bundle", "status"])
    assert rc == 0 and data["version"] == "2026.09.13.4"
