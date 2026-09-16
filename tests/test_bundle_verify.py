"""§2.8 bundle_verify."""
import hashlib

from helpers_core import by_rule, call, check_shape, lint_tree

PAYLOAD = b"the real installer\n"
SHA = hashlib.sha256(PAYLOAD).hexdigest()


def verify(root):
    r = call("bundle_verify", root=root)
    check_shape(r)
    return r


def _tree(tmp_path, files):
    return lint_tree(tmp_path / "t", files=files)


def test_verify_match(tmp_path):
    """§2.8 matching hash: no findings; checked entry with match true."""
    root = _tree(tmp_path, {"vendor/pkg/tool.zip": PAYLOAD,
                            "vendor/pkg/README.md": "readme",
                            "vendor/pkg/SOURCE.md": f"# Source\n\n- URL: https://example.org/tool.zip\n- SHA-256: `{SHA}`\n"})
    r = verify(root)
    assert r["findings"] == []
    assert r["ok"] is True
    assert r["checked"] == [{"source": "vendor/pkg/SOURCE.md", "file": "vendor/pkg/tool.zip",
                             "expected": SHA, "actual": SHA, "match": True}]


def test_verify_mismatch(tmp_path):
    """§2.8 mismatch: B012 with expected and actual in the message."""
    wrong = "ab" * 32
    root = _tree(tmp_path, {"vendor/pkg/tool.zip": PAYLOAD,
                            "vendor/pkg/SOURCE.md": f"- SHA-256: {wrong}\n"})
    r = verify(root)
    b012 = by_rule(r, "B012")
    assert len(b012) == 1
    assert b012[0]["severity"] == "error"
    msg = b012[0]["message"].lower()
    assert wrong in msg and SHA in msg
    assert r["ok"] is False
    assert len(r["checked"]) == 1
    assert r["checked"][0]["match"] is False
    assert r["checked"][0]["actual"].lower() == SHA


def test_verify_no_hash(tmp_path):
    """§2.8 no SHA-256 line: B013 `no hash recorded`; not in checked."""
    root = _tree(tmp_path, {"vendor/pkg/tool.zip": PAYLOAD,
                            "vendor/pkg/SOURCE.md": "- URL: https://example.org\n"})
    r = verify(root)
    b013 = by_rule(r, "B013")
    assert len(b013) == 1
    assert b013[0]["severity"] == "warning"
    assert "no hash recorded" in b013[0]["message"]
    assert b013[0]["path"] == "vendor/pkg/SOURCE.md"
    assert r["checked"] == []
    assert r["ok"] is True


def test_verify_placeholder_hash(tmp_path):
    """§2.8 a value that is not 64 hex characters (e.g. `<hash>`) is B013 `no hash recorded`."""
    root = _tree(tmp_path, {"vendor/pkg/tool.zip": PAYLOAD,
                            "vendor/pkg/SOURCE.md": "- SHA-256: `<hash>`\n"})
    r = verify(root)
    assert ["no hash recorded" in f["message"] for f in by_rule(r, "B013")] == [True]


def test_verify_cannot_tell_which_file(tmp_path):
    """§2.8 several candidate files and no `- File:` line: B013 `cannot tell which file`."""
    root = _tree(tmp_path, {"vendor/pkg/tool.zip": PAYLOAD,
                            "vendor/pkg/tool.sig": "sig",
                            "vendor/pkg/SOURCE.md": f"- SHA-256: {SHA}\n"})
    r = verify(root)
    b013 = by_rule(r, "B013")
    assert len(b013) == 1
    assert "cannot tell which file" in b013[0]["message"]
    assert r["checked"] == []


def test_verify_file_line_selects_target(tmp_path):
    """§2.8 a `- File:` line (backticks allowed) names the target relative to SOURCE.md."""
    root = _tree(tmp_path, {"vendor/pkg/tool.zip": PAYLOAD,
                            "vendor/pkg/tool.sig": "sig",
                            "vendor/pkg/SOURCE.md": f"- File: `tool.zip`\n- SHA-256: {SHA}\n"})
    r = verify(root)
    assert r["findings"] == []
    assert [(c["file"], c["match"]) for c in r["checked"]] == [("vendor/pkg/tool.zip", True)]


def test_verify_skips_git_dir(tmp_path):
    """§2.8 SOURCE.md files under .git are not checked."""
    root = _tree(tmp_path, {".git/sub/SOURCE.md": "- URL: nothing\n", ".git/sub/x.bin": "x"})
    r = verify(root)
    assert r["findings"] == [] and r["checked"] == []
