"""MANIFEST §7 via the CLI (§0.4): --json output, exit codes, --strict, rule options, ToolError."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers_diagram_text import cli, cli_json, write  # noqa: E402


@pytest.fixture
def here(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_lint_error_exit_1(here, capsys):
    write(here / "r.md", "We went.\n")
    code, res, _ = cli_json(capsys, ["text", "lint", "r.md", "--json"])
    assert code == 1
    assert res["ok"] is False
    assert [(f["rule"], f["path"], f["line"]) for f in res["findings"]] == [("S002", "r.md", 1)]


def test_lint_clean_exit_0(here, capsys):
    write(here / "r.md", "The tool works.\n")
    code, res, _ = cli_json(capsys, ["text", "lint", "r.md", "--json"])
    assert code == 0 and res["ok"] is True


def test_lint_warning_exit_0_and_strict_exit_1(here, capsys):
    write(here / "r.md", "It may be wrong.\n")
    code, res, _ = cli_json(capsys, ["text", "lint", "r.md", "--json"])
    assert code == 0 and res["counts"]["warning"] == 1
    code, _, _ = cli_json(capsys, ["text", "lint", "r.md", "--strict", "--json"])
    assert code == 1


def test_lint_rules_and_ignore_options(here, capsys):
    write(here / "r.md", "We may be — late; now.\n")
    _, res, _ = cli_json(capsys, ["text", "lint", "r.md", "--rules", "S001,S005", "--json"])
    assert sorted(f["rule"] for f in res["findings"]) == ["S001", "S005"]
    _, res, _ = cli_json(capsys, ["text", "lint", "r.md", "--ignore", "S001", "--json"])
    assert sorted(f["rule"] for f in res["findings"]) == ["S002", "S003", "S005"]


def test_lint_max_words_option(here, capsys):
    write(here / "r.md", "one two three four.\n")
    _, res, _ = cli_json(capsys, ["text", "lint", "r.md", "--max-words", "3", "--json"])
    assert [f["rule"] for f in res["findings"]] == ["S009"]


def test_lint_several_paths(here, capsys):
    write(here / "a.md", "We went.\n")
    write(here / "b.md", "Our turn.\n")
    _, res, _ = cli_json(capsys, ["text", "lint", "a.md", "b.md", "--json"])
    assert [f["path"] for f in res["findings"]] == ["a.md", "b.md"]
    assert set(res["stats"]) == {"a.md", "b.md"}


def test_lint_missing_path_toolerror(here, capsys):
    code, out, err = cli(capsys, ["text", "lint", "missing.md", "--json"])
    assert code == 1
    assert "error" in json.loads(out)
    assert err.startswith("tundlekit: ")


def test_fignums_exit_codes(here, capsys):
    write(here / "r.md", "*Fig. 1. a*\n\nSee Fig. 1.\n")
    write(here / "deck.txt", "Fig. 5\n")
    code, res, _ = cli_json(capsys, ["text", "fignums", "r.md", "--json"])
    assert code == 0 and res["ok"] is True
    code, res, _ = cli_json(capsys, ["text", "fignums", "r.md", "--refs", "deck.txt", "--json"])
    assert code == 1
    assert [(f["rule"], f["path"]) for f in res["findings"]] == [("F005", "deck.txt")]


def test_wordcount_json(here, capsys):
    write(here / "r.md", "# A\none two\n")
    code, res, _ = cli_json(capsys, ["text", "wordcount", "r.md", "--json"])
    assert code == 0
    (sec,) = res["files"]["r.md"]["sections"]
    assert (sec["heading"], sec["words"], sec["delta"]) == ("# A", 2, None)
