"""MANIFEST §7.3 text_wordcount (sections, front matter, totals, git baseline deltas)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers_diagram_text import cli_json, commit_all, git, init_repo, text, write  # noqa: E402

DOC = ("# Title\nalpha beta\n\n## Part  \none two three\n#### deep\nfour\n"
       "### Third\n\n")


def sections(res, name):
    return [(s["heading"], s["words"], s["delta"]) for s in res["files"][name]["sections"]]


def test_sections_and_total(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "r.md", DOC)
    res = text("text_wordcount", paths=["r.md"])
    # level-4 headings do not start a section; their line is body text
    assert sections(res, "r.md") == [("# Title", 2, None), ("## Part", 6, None), ("### Third", 0, None)]
    f = res["files"]["r.md"]
    assert f["total"] == 8
    assert f["total_delta"] is None


def test_front_matter_section(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "r.md", "some intro words\n# A\nx y\n")
    res = text("text_wordcount", paths=["r.md"])
    assert sections(res, "r.md") == [("(front matter)", 3, None), ("# A", 2, None)]
    assert res["files"]["r.md"]["total"] == 5


def test_empty_front_matter_omitted(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "r.md", "\n\n# A\nx\n")
    res = text("text_wordcount", paths=["r.md"])
    assert sections(res, "r.md") == [("# A", 1, None)]


def test_several_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "a.md", "# A\none\n")
    write(tmp_path / "b.md", "# B\none two\n")
    res = text("text_wordcount", paths=["a.md", "b.md"])
    assert res["files"]["a.md"]["total"] == 1
    assert res["files"]["b.md"]["total"] == 2


@pytest.fixture
def repo(tmp_path, monkeypatch):
    repo = init_repo(monkeypatch, tmp_path)
    write(repo / "docs" / "r.md", "# Title\nalpha beta\n## Old part\none two three\n## Gone\nx\n")
    commit_all(repo, "base")
    git(repo, "tag", "base")
    write(repo / "docs" / "r.md",
          "# Title\nalpha beta gamma delta\n## Old part\none\n## Brand new\nfresh words here\n")
    commit_all(repo, "edit")
    monkeypatch.chdir(repo)
    return repo


def test_baseline_deltas(repo):
    res = text("text_wordcount", paths=["docs/r.md"], baseline="base")
    assert sections(res, "docs/r.md") == [("# Title", 4, 2), ("## Old part", 1, -2), ("## Brand new", 3, "new")]
    f = res["files"]["docs/r.md"]
    assert f["total"] == 8
    assert f["total_delta"] == 8 - 6


def test_baseline_file_not_in_ref(repo):
    write(repo / "docs" / "later.md", "# Later\nsome words\n")
    commit_all(repo, "later")
    res = text("text_wordcount", paths=["docs/later.md"], baseline="base")
    assert sections(res, "docs/later.md") == [("# Later", 2, None)]
    assert res["files"]["docs/later.md"]["total_delta"] is None


def test_cli_wordcount_baseline(repo, capsys):
    code, res, _ = cli_json(capsys, ["text", "wordcount", "docs/r.md", "--baseline", "base", "--json"])
    assert code == 0
    assert res["files"]["docs/r.md"]["total_delta"] == 2
