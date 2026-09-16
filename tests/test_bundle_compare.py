"""§2.4 bundle_compare."""
import pytest

from helpers_core import call, gitenv, make_tundle, tool_error, write  # noqa: F401


@pytest.fixture
def mine(tmp_path, gitenv):  # noqa: F811
    return make_tundle(tmp_path / "mine", version="2026.09.16.2", commit=False)


def _other(tmp_path, version):
    d = tmp_path / "other"
    write(d, "VERSION", version + "\n")
    return d


@pytest.mark.parametrize("theirs,result", [
    ("2026.09.16.2", "same"),
    ("2026.09.16.1", "this_newer"),
    ("2026.09.16.3", "other_newer"),
])
def test_compare_results(tmp_path, mine, theirs, result):
    """§2.4 result same | this_newer | other_newer."""
    other = _other(tmp_path, theirs)
    r = call("bundle_compare", root=mine, other=str(other))
    assert r == {"mine": "2026.09.16.2", "theirs": theirs, "other": str(other), "result": result}


def test_compare_other_without_version(tmp_path, mine):
    """§2.4 other has no VERSION -> ToolError `no VERSION`."""
    d = tmp_path / "empty"
    d.mkdir()
    with pytest.raises(tool_error()) as ei:
        call("bundle_compare", root=mine, other=str(d))
    assert "no VERSION" in str(ei.value)


def test_compare_other_invalid_version(tmp_path, mine):
    """§2.1 a malformed VERSION raises `invalid VERSION` in every command that reads it."""
    other = _other(tmp_path, "2026-09-16")
    with pytest.raises(tool_error()) as ei:
        call("bundle_compare", root=mine, other=str(other))
    assert "invalid VERSION" in str(ei.value)


def test_compare_relative_other_kept_as_given(tmp_path, mine, monkeypatch):
    """§0.2 relative paths resolve against the cwd; §2.4 `other` is the path as given."""
    _other(tmp_path, "2026.09.17.1")
    monkeypatch.chdir(tmp_path)
    r = call("bundle_compare", root=mine, other="other")
    assert r["other"] == "other"
    assert r["result"] == "other_newer"
