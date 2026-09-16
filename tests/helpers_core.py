"""Shared helpers for the core (§0, §1, §12) and bundle (§2) tests.

Imported as `from helpers_core import ...` (pytest puts tests/ on sys.path). Nothing here imports
tundlekit at module level, so collection works before the package is implemented.
"""
from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
NOW = "2026-09-16T10:00"          # TUNDLEKIT_NOW used by default in git tests
TODAY = "2026.09.16"
MARKER = "<!-- entries -->"
AUTHOR = ("Test Author", "author@example.com")
COMMITTER = ("Test Committer", "committer@example.com")
BUNDLE_TOOLS = ["bundle_status", "bundle_release", "bundle_compare", "bundle_prune",
                "bundle_init", "bundle_lint", "bundle_verify"]


# ---------------------------------------------------------------- registry / cli access

def reg():
    """The registry module, with every tool module loaded."""
    from tundlekit import registry
    registry.load_all()
    return registry


def call(name, **args):
    """registry.call with keyword arguments (paths converted to str)."""
    r = reg()
    return r.call(name, {k: (str(v) if isinstance(v, Path) else v) for k, v in args.items()})


def tool_error():
    from tundlekit.registry import ToolError
    return ToolError


def run_cli(capsys, argv):
    """Run tundlekit.cli.main(argv); return (exit_code, stdout, stderr).

    §0.4: main returns an int. argparse usage errors may surface as SystemExit(2); both are accepted.
    """
    from tundlekit import cli
    capsys.readouterr()
    try:
        rc = cli.main([str(a) for a in argv])
    except SystemExit as e:  # argparse usage errors
        rc = e.code
    out, err = capsys.readouterr()
    return rc, out, err


def run_cli_json(capsys, argv):
    rc, out, err = run_cli(capsys, list(argv) + ["--json"])
    return rc, json.loads(out), err


def subprocess_env(**extra):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    for k in ("PYTHONIOENCODING", "PYTHONUTF8"):
        env.pop(k, None)
    env.update({k: str(v) for k, v in extra.items()})
    return env


# ---------------------------------------------------------------- git

@pytest.fixture
def gitenv(tmp_path, monkeypatch):
    """Isolate git from user/system config; fixed identity; fixed clock (§2.1 TUNDLEKIT_NOW)."""
    home = tmp_path / "_home"
    home.mkdir()
    gcfg = home / ".gitconfig"
    gcfg.write_text("", encoding="utf-8")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(gcfg))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_AUTHOR_NAME", AUTHOR[0])
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", AUTHOR[1])
    monkeypatch.setenv("GIT_COMMITTER_NAME", COMMITTER[0])
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", COMMITTER[1])
    for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_AUTHOR_DATE", "GIT_COMMITTER_DATE",
              "GIT_OBJECT_DIRECTORY", "GIT_CEILING_DIRECTORIES"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("TUNDLEKIT_NOW", NOW)
    return gcfg


def git(root, *args, env=None, check=True, input=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, env=e, timeout=120,
                       input=input)
    if check and p.returncode != 0:
        raise AssertionError(f"git {args} failed: {p.stderr.decode(errors='replace')}")
    return p


def git_out(root, *args, **kw):
    return git(root, *args, **kw).stdout.decode("utf-8").strip()


def commit_all(root, message, date=None, author=None, committer=None, allow_empty=False):
    env = {}
    if date:
        env["GIT_AUTHOR_DATE"] = date
        env["GIT_COMMITTER_DATE"] = date
    if author:
        env["GIT_AUTHOR_NAME"], env["GIT_AUTHOR_EMAIL"] = author
    if committer:
        env["GIT_COMMITTER_NAME"], env["GIT_COMMITTER_EMAIL"] = committer
    git(root, "add", "-A", env=env)
    msg = Path(root) / ".git" / "_msg_for_test"
    msg.write_bytes(message.encode("utf-8"))
    args = ["commit", "-q", "-F", str(msg)]
    if allow_empty:
        args.append("--allow-empty")
    git(root, *args, env=env)
    msg.unlink()
    return git_out(root, "rev-parse", "HEAD")


def changelog_text(entries=()):
    """A CHANGELOG.md like tundle's, with entries [(version, summary)] newest first."""
    s = "# Changelog\n\nOne entry per version, newest first.\n\n" + MARKER + "\n"
    for v, summary in entries:
        s += f"\n## {v}  (2026-09-15 18:27)\n\n{summary}\n\n_1 added, 0 modified, 0 removed, 0 renamed_\n"
    return s


def write(root, rel, data=""):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        p.write_bytes(data)
    else:
        p.write_bytes(data.encode("utf-8"))
    return p


def make_tundle(root, version="2026.09.15.1", files=None, commit=True, changelog=None, date=None):
    """A git-backed tundle on branch main. Returns root (Path)."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True, capture_output=True, timeout=60)
    write(root, "VERSION", version + "\n")
    if changelog is None:
        changelog = changelog_text([(version, "initial")]) if not version.endswith(".0") else changelog_text()
    write(root, "CHANGELOG.md", changelog)
    write(root, ".gitattributes", "* -text\n")
    for rel, data in (files or {}).items():
        write(root, rel, data)
    if commit:
        commit_all(root, f"tundle {version}: initial", date=date or "2026-09-15T18:27:00+02:00")
    return root


def make_history(root, n, start=1):
    """Add n empty commits c{start}..c{start+n-1}; return their shas oldest first."""
    shas = []
    for i in range(start, start + n):
        date = f"2026-09-16T{8 + i // 60:02d}:{i % 60:02d}:00+00:00"   # increasing, after make_tundle's commit
        shas.append(commit_all(root, f"c{i}", date=date, allow_empty=True))
    return shas


def dir_size(path, exclude_git=False):
    total = 0
    for dp, dns, fns in os.walk(path):
        if exclude_git and ".git" in dns:
            dns.remove(".git")
        for f in fns:
            fp = os.path.join(dp, f)
            if os.path.isfile(fp) and not os.path.islink(fp):
                total += os.path.getsize(fp)
    return total


# ---------------------------------------------------------------- lint helpers

def lint_tree(root, files=None, dirs=(), version="2026.09.16.1", init_git=True):
    """A lint-clean tundle (no commit needed) plus extra files/dirs."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    if init_git:
        subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True, capture_output=True, timeout=60)
    write(root, "VERSION", version + "\n")
    write(root, "CHANGELOG.md", changelog_text([(version, "x")]))
    for rel, data in (files or {}).items():
        write(root, rel, data)
    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)
    return root


def by_rule(result, rule):
    return [f for f in result["findings"] if f["rule"] == rule]


def paths_for(result, rule):
    return sorted(f["path"].rstrip("/") for f in by_rule(result, rule))


def try_make(parent, name, is_dir=False):
    """Create an entry with an exact name, or skip if this OS/filesystem refuses or renames it."""
    parent = Path(parent)
    parent.mkdir(parents=True, exist_ok=True)
    try:
        p = os.path.join(str(parent), name)
        if is_dir:
            os.mkdir(p)
        else:
            with open(p, "wb") as f:
                f.write(b"x")
    except (OSError, ValueError):
        pytest.skip(f"cannot create {name!r} on this platform")
    if name not in os.listdir(parent):
        pytest.skip(f"platform altered the name {name!r}")
    return name


def check_shape(result):
    """§0.3 checker result shape."""
    assert isinstance(result["ok"], bool)
    assert isinstance(result["findings"], list)
    assert set(result["counts"]) >= {"error", "warning", "info"}
    for sev in ("error", "warning", "info"):
        assert result["counts"][sev] == sum(1 for f in result["findings"] if f["severity"] == sev)
    assert result["ok"] == (result["counts"]["error"] == 0)
    keys = [(f["path"], f["line"] or 0, f["rule"]) for f in result["findings"]]
    assert keys == sorted(keys)
    for f in result["findings"]:
        assert set(f) >= {"rule", "severity", "path", "line", "message", "excerpt"}
        assert f["severity"] in ("error", "warning", "info")
        assert "\\" not in f["path"]
        assert f["line"] is None or (isinstance(f["line"], int) and f["line"] >= 1)


# ---------------------------------------------------------------- MCP

def mcp_argv(*extra):
    return [sys.executable, "-m", "tundlekit.mcp_server", *map(str, extra)]


def mcp_run(messages, cwd, extra_args=(), argv=None, timeout=90):
    """Send all lines at once, close stdin, return (returncode, [parsed responses], raw stdout, stderr).

    messages: dicts/lists/ints are JSON-encoded; str items are sent verbatim.
    """
    lines = []
    for m in messages:
        lines.append(m if isinstance(m, str) else json.dumps(m))
    data = ("\n".join(lines) + "\n").encode("utf-8")
    p = subprocess.Popen(argv or mcp_argv(*extra_args), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=str(cwd), env=subprocess_env())
    try:
        out, err = p.communicate(input=data, timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        p.communicate()
        raise AssertionError("MCP server did not exit after stdin closed")
    raw = out.decode("utf-8")
    responses = [json.loads(line) for line in raw.split("\n") if line.strip()]
    return p.returncode, responses, raw, err.decode("utf-8", errors="replace")


def req(id_, method, params=None):
    m = {"jsonrpc": "2.0", "id": id_, "method": method}
    if params is not None:
        m["params"] = params
    return m


def note(method, params=None):
    m = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        m["params"] = params
    return m


class McpProcess:
    """Interactive server: write a line, read a response line with a timeout."""

    def __init__(self, cwd, extra_args=()):
        self.p = subprocess.Popen(mcp_argv(*extra_args), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, cwd=str(cwd), env=subprocess_env())
        self.q: queue.Queue = queue.Queue()
        threading.Thread(target=self._reader, daemon=True).start()
        threading.Thread(target=self.p.stderr.read, daemon=True).start()

    def _reader(self):
        for line in self.p.stdout:
            self.q.put(line)
        self.q.put(None)

    def send(self, msg):
        self.p.stdin.write((json.dumps(msg) + "\n").encode("utf-8"))
        self.p.stdin.flush()

    def recv(self, timeout=60):
        line = self.q.get(timeout=timeout)
        assert line is not None, "server closed stdout"
        return json.loads(line.decode("utf-8"))

    def close(self, timeout=60):
        try:
            self.p.stdin.close()
        except OSError:
            pass
        try:
            return self.p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self.p.kill()
            raise AssertionError("MCP server did not exit after stdin closed")
