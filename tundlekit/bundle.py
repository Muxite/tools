"""bundle: tundle maintenance, a port of tundle's tools/tundle.sh (MANIFEST.md §2).

A tundle is a git work tree holding VERSION, a CHANGELOG.md with a `<!-- entries -->` marker, and content.
The on-disk formats match tundle.sh exactly, so both tools can run on the same tundle.
"""
from __future__ import annotations

import datetime as _dt
import fnmatch
import hashlib
import os
import re
import stat as _stat
import subprocess
from pathlib import Path

from tundlekit.registry import ToolError, tool

MARKER = "<!-- entries -->"
KEEP_DEFAULT = 5
PRUNE_HINT_AT = 10
MiB = 1024 * 1024

# Same patterns as tundle's .gitignore (§2.6, §2.7 B005).
GITIGNORE = """\
# Caches and work leftovers: never part of a release
__pycache__/
*.pyc
.pytest_cache/
.benchmarks/
.ipynb_checkpoints/
.venv/
venv/
node_modules/
*.tmp

# Office and editor lock files
~$*
.~lock.*#

# OS clutter
Thumbs.db
desktop.ini
.DS_Store
._*
"""
GITATTRIBUTES = """\
# Store every file byte-for-byte: no line-ending conversion, so copies match on Windows, Linux and the phone.
* -text
"""
CHANGELOG = """\
# Changelog

One entry per version, newest first. `tundlekit bundle release` writes the entries. Clearing git
history never removes them, so this file keeps the full lineage even when git only
remembers the last few versions.

<!-- entries -->
"""

JUNK_DIRS = {"__pycache__", ".pytest_cache", ".benchmarks", ".ipynb_checkpoints", ".venv", "venv", "node_modules"}
JUNK_FILES = ["*.pyc", "*.tmp", "~$*", ".~lock.*#", "Thumbs.db", "desktop.ini", ".DS_Store", "._*"]
RESERVED = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {f"LPT{i}" for i in range(1, 10)}
BAD_CHARS = set(':*?"<>|')
COPY_MARKERS = [
    re.compile(r"(?:[ _\-.]\(?|\()(?:v\d+|final|new|old|copy|backup)\)?$", re.I),
    re.compile(r"\s\(\d+\)$", re.I),
    re.compile(r" - copy(?: \(\d+\))?$", re.I),
]
NAME_VERSION = re.compile(r"(?<=[^\W\d_])-v\d+$", re.I)
VERSION_RE = re.compile(r"([0-9]{4})\.([0-9]{2})\.([0-9]{2})\.([0-9]+)")
HASH_LINE = re.compile(r"^\s*-\s*SHA-256:\s*(.*)$")
FILE_LINE = re.compile(r"^\s*-\s*File:\s*(.*)$")

# Variables that would point git at another repository than root (§13.1).
GIT_ENV_BLOCKLIST = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
                     "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR", "GIT_NAMESPACE", "GIT_CEILING_DIRECTORIES")
# State files in .git that name commits outside the refs namespace.
PSEUDO_REFS = ("ORIG_HEAD", "FETCH_HEAD", "MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "BISECT_HEAD", "AUTO_MERGE")
SIGNATURE_HEADERS = (b"gpgsig", b"gpgsig-sha256")
FILE_ATTRIBUTE_REPARSE_POINT = 0x400

ROOT_PROP = {"type": "string", "description": "tundle root; default: walk up from the current directory"}


# ---------------------------------------------------------------- common helpers

def _now() -> _dt.datetime:
    """Local time, or TUNDLEKIT_NOW (YYYY-MM-DDTHH:MM[:SS]) when set (§2.1)."""
    value = os.environ.get("TUNDLEKIT_NOW")
    if not value:
        return _dt.datetime.now()
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            return _dt.datetime.strptime(value.strip(), fmt)
        except ValueError:
            pass
    raise ToolError(f"invalid TUNDLEKIT_NOW {value!r}: expected YYYY-MM-DDTHH:MM or YYYY-MM-DDTHH:MM:SS")


def _today() -> str:
    return _now().strftime("%Y.%m.%d")


def parse_version(text: str) -> tuple[int, int, int, int]:
    m = VERSION_RE.fullmatch(text)
    if not m:
        raise ToolError(f"invalid VERSION {text!r}: expected YYYY.MM.DD.N")
    return tuple(int(g) for g in m.groups())


def read_version(folder: str | os.PathLike, missing: str | None = None) -> str:
    """VERSION of a folder, stripped and validated. `missing` is the error message when there is none."""
    path = Path(folder) / "VERSION"
    if not path.is_file():
        raise ToolError(missing or f"no VERSION file in {folder}")
    try:
        text = path.read_bytes().decode("utf-8-sig").strip()
    except (OSError, UnicodeDecodeError) as e:
        raise ToolError(f"invalid VERSION in {folder}: {e}") from None
    parse_version(text)
    return text


def _is_tundle(folder: Path) -> bool:
    return (folder / "VERSION").is_file() and (folder / "CHANGELOG.md").is_file()


def find_root(root: str | None = None) -> Path:
    """The tundle root: `root` as given (made absolute), else the first ancestor of the cwd holding both files."""
    if root is not None:
        path = Path(os.path.abspath(root))
        if not path.is_dir():
            raise ToolError(f"not a directory: {root}")
        return path
    here = Path(os.path.abspath(os.getcwd()))
    for folder in (here, *here.parents):
        if _is_tundle(folder):
            return folder
    raise ToolError(f"no tundle found (no folder with VERSION and CHANGELOG.md) from {here} upwards")


def _git(root: Path, *args: str, input: bytes | None = None, env: dict | None = None,
         check: bool = True) -> subprocess.CompletedProcess:
    """Run `git -C root ...` with bytes I/O. Raises ToolError with git's stderr when check and git fails."""
    full_env = {k: v for k, v in os.environ.items() if k.upper() not in GIT_ENV_BLOCKLIST}
    full_env.update(env or {})
    try:
        proc = subprocess.run(["git", "-C", str(root), *args], input=input, capture_output=True,
                              env=full_env, stdin=None if input is not None else subprocess.DEVNULL)
    except FileNotFoundError:
        raise ToolError("git not found: install git and make sure it is on PATH") from None
    if check and proc.returncode != 0:
        err = _text(proc.stderr).strip() or _text(proc.stdout).strip() or f"exit code {proc.returncode}"
        raise ToolError(f"git {args[0]} failed: {err}")
    return proc


def _text(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def _git_out(root: Path, *args: str, **kw) -> str:
    return _text(_git(root, *args, **kw).stdout)


def _lines(output: str) -> list[str]:
    """Output lines without terminators; leading spaces are kept (porcelain status codes need them)."""
    return [ln for ln in output.split("\n") if ln != ""]


def _require_worktree_root(root: Path) -> None:
    """Refuse to run git commands that would act on an enclosing repository."""
    top = _git_out(root, "rev-parse", "--show-toplevel").strip()
    try:
        same = bool(top) and os.path.samefile(top, root)
    except OSError:
        same = False
    if not same:
        raise ToolError(f"{root} is not the top folder of its git work tree ({top or 'none'})")


def _has_head(root: Path) -> bool:
    return _git(root, "rev-parse", "-q", "--verify", "HEAD^{commit}", check=False).returncode == 0


def _history(root: Path) -> int:
    if not _has_head(root):
        return 0
    return int(_git_out(root, "rev-list", "--count", "HEAD").strip())


def _pending(root: Path) -> list[dict]:
    out = _git_out(root, "status", "--porcelain", env={"GIT_OPTIONAL_LOCKS": "0"})
    pending = []
    for line in _lines(out):
        code, path = line[:2], line[3:]
        if code[0] in "RC" and " -> " in path:
            path = path.split(" -> ", 1)[1]
        pending.append({"status": code.replace(" ", ""), "path": path})
    return pending


def _is_link(entry: os.DirEntry) -> bool:
    """A symlink, a junction, or a directory reparse point: 1 entry, never followed (§13.1)."""
    try:
        if entry.is_symlink():
            return True
        is_junction = getattr(entry, "is_junction", None)
        if is_junction is not None and is_junction():
            return True
        st = entry.stat(follow_symlinks=False)
    except OSError:
        return True
    return bool(getattr(st, "st_file_attributes", 0) & FILE_ATTRIBUTE_REPARSE_POINT) and _stat.S_ISDIR(st.st_mode)


def walk(top: str | os.PathLike, skip_git: bool = True):
    """Like os.walk (top-down, sorted) but never follows links: yields (dirpath, dirs, files, links).

    The caller may prune `dirs` in place. `files` are non-link files; `links` are link entries of any kind.
    """
    stack = [os.fspath(top)]
    while stack:
        dirpath = stack.pop()
        try:
            with os.scandir(dirpath) as it:
                entries = sorted(it, key=lambda e: e.name)
        except OSError:
            continue
        dirs, files, links = [], [], []
        for entry in entries:
            if skip_git and entry.name == ".git":
                continue
            if _is_link(entry):
                links.append(entry.name)
            elif entry.is_dir(follow_symlinks=False):
                dirs.append(entry.name)
            else:
                files.append(entry.name)
        yield dirpath, dirs, files, links
        stack.extend(os.path.join(dirpath, d) for d in reversed(dirs))


def _files(top: Path):
    """(relative posix path, size) of every file under top, skipping .git folders and links."""
    for dirpath, _, filenames, _ in walk(top):
        for name in filenames:
            full = os.path.join(dirpath, name)
            try:
                size = os.stat(full, follow_symlinks=False).st_size
            except OSError:
                continue
            yield os.path.relpath(full, top).replace(os.sep, "/"), size


def _tree_bytes(top: Path) -> int:
    if not top.is_dir():
        return top.stat().st_size if top.is_file() else 0
    total = 0
    for dirpath, _, filenames, _ in walk(top, skip_git=False):
        for name in filenames:
            try:
                total += os.stat(os.path.join(dirpath, name), follow_symlinks=False).st_size
            except OSError:
                pass
    return total


def human_size(n: int) -> str:
    size = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{int(size)} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{n} B"


# ---------------------------------------------------------------- status

@tool("bundle_status",
      "Show a tundle's state: VERSION, last release, history length (prune_hint when over 10), content and .git "
      "sizes, unreleased changes (git status) and the 5 largest files.",
      {"type": "object", "properties": {"root": ROOT_PROP}, "additionalProperties": False},
      readOnlyHint=True)
def bundle_status(root: str | None = None) -> dict:
    top = find_root(root)
    version = read_version(top)
    _require_worktree_root(top)
    history = _history(top)
    last = None
    if history:
        date, _, subject = _git_out(top, "log", "-1", "--no-show-signature", "--format=%ai%x00%s").rstrip(
            "\n").partition("\x00")
        last = {"date": date, "subject": subject}
    pending = _pending(top)
    files = list(_files(top))
    largest = sorted(files, key=lambda f: (-f[1], f[0]))[:5]
    return {
        "root": str(top),
        "version": version,
        "last": last,
        "history": history,
        "prune_hint": history > PRUNE_HINT_AT,
        "content_bytes": sum(size for _, size in files),
        "git_bytes": _tree_bytes(top / ".git") if (top / ".git").exists() else 0,
        "pending": pending,
        "largest": [{"path": p, "bytes": s} for p, s in largest],
    }


# ---------------------------------------------------------------- release

def _marker_index(lines: list[bytes]) -> int | None:
    marker = MARKER.encode()
    for i, line in enumerate(lines):
        if line.rstrip(b"\n").rstrip(b"\r") == marker:
            return i
    return None


def next_version(old: str, today: str) -> str:
    """§2.3 step 5: count up within a day; never go backwards."""
    old_date, _, old_n = old.rpartition(".")
    new = f"{today}.{int(old_n) + 1}" if old_date == today else f"{today}.1"
    if parse_version(new) <= parse_version(old):
        new = f"{old_date}.{int(old_n) + 1}"
    return new


@tool("bundle_release",
      "Release a tundle: stage everything (git add -A), bump VERSION (YYYY.MM.DD.N), add a CHANGELOG.md entry "
      "after the <!-- entries --> marker with the summary and change counts, and commit as 'tundle <version>: "
      "<summary>'.",
      {"type": "object",
       "properties": {"summary": {"type": "string", "description": "what changed, 1 line"}, "root": ROOT_PROP},
       "required": ["summary"], "additionalProperties": False},
      readOnlyHint=False, destructiveHint=False)
def bundle_release(summary: str, root: str | None = None) -> dict:
    summary = summary.strip()
    if not summary:
        raise ToolError('usage: release "what changed" (the summary is empty)')
    top = find_root(root)
    old = read_version(top)
    changelog_path = top / "CHANGELOG.md"
    if not changelog_path.is_file():
        raise ToolError(f"no CHANGELOG.md with a {MARKER} line in {top}")
    changelog = changelog_path.read_bytes()
    lines = changelog.splitlines(keepends=True)
    at = _marker_index(lines)
    if at is None:
        raise ToolError(f"CHANGELOG.md has no line {MARKER}: add it where new entries should go")
    _require_worktree_root(top)

    _git(top, "add", "-A")
    if _git(top, "diff", "--cached", "--quiet", check=False).returncode == 0:
        raise ToolError("nothing to release: no changes since the last release")

    counts = {"A": 0, "M": 0, "D": 0, "R": 0}
    for line in _lines(_git_out(top, "diff", "--cached", "--name-status", "--find-renames", "--no-color")):
        if line[0] in counts:
            counts[line[0]] += 1
    stats = {"added": counts["A"], "modified": counts["M"], "removed": counts["D"], "renamed": counts["R"]}
    stats_text = f"{counts['A']} added, {counts['M']} modified, {counts['D']} removed, {counts['R']} renamed"

    now = _now()
    new = next_version(old, now.strftime("%Y.%m.%d"))
    entry = f"\n## {new}  ({now.strftime('%Y-%m-%d %H:%M')})\n\n{summary}\n\n_{stats_text}_\n".encode("utf-8")
    marker_line = lines[at] if lines[at].endswith(b"\n") else lines[at] + b"\n"
    new_changelog = b"".join(lines[:at]) + marker_line + entry + b"".join(lines[at + 1:])

    version_path = top / "VERSION"
    old_version_bytes = version_path.read_bytes()
    _write_bytes(version_path, f"{new}\n".encode())
    _write_bytes(changelog_path, new_changelog)
    try:
        _git(top, "add", "--", "VERSION", "CHANGELOG.md")
        _git(top, "commit", "-q", "-F", "-", input=f"tundle {new}: {summary}".encode("utf-8"))
    except ToolError:
        # Leave the tundle as it was before the bump (changes stay staged, as after `git add -A`).
        _write_bytes(version_path, old_version_bytes)
        _write_bytes(changelog_path, changelog)
        _git(top, "add", "--", "VERSION", "CHANGELOG.md", check=False)
        raise
    history = _history(top)
    return {
        "version": new,
        "previous": old,
        "stats": stats,
        "stats_text": stats_text,
        "commit": _git_out(top, "rev-parse", "HEAD").strip(),
        "history": history,
        "prune_hint": history > PRUNE_HINT_AT,
    }


def _write_bytes(path: Path, data: bytes) -> None:
    tmp = path.with_name(path.name + ".tundlekit-tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


# ---------------------------------------------------------------- compare

@tool("bundle_compare",
      "Compare this tundle's VERSION with the copy at `other`: result is same, this_newer or other_newer. "
      "Use it before editing (work on the newest copy) and before replacing a copy.",
      {"type": "object",
       "properties": {"other": {"type": "string", "description": "path of the other tundle copy"},
                      "root": ROOT_PROP},
       "required": ["other"], "additionalProperties": False},
      readOnlyHint=True)
def bundle_compare(other: str, root: str | None = None) -> dict:
    mine = read_version(find_root(root))
    theirs = read_version(other, missing=f"no VERSION file in {other}: not a tundle copy")
    a, b = parse_version(mine), parse_version(theirs)
    result = "same" if a == b else "this_newer" if a > b else "other_newer"
    return {"mine": mine, "theirs": theirs, "other": other, "result": result}


# ---------------------------------------------------------------- prune

def _rebuilt_commit(raw: bytes, parent: str | None) -> bytes:
    """The raw commit with its parent lines replaced by `parent` and signature headers dropped (§13.1)."""
    header, sep, message = raw.partition(b"\n\n")
    out, skipping = [], False
    for line in header.split(b"\n"):
        if line.startswith(b" "):  # continuation of a multi-line header
            if not skipping:
                out.append(line)
            continue
        key = line.split(b" ", 1)[0]
        skipping = key in SIGNATURE_HEADERS
        if skipping or key == b"parent":
            continue
        out.append(line)
        if key == b"tree" and parent:
            out.append(b"parent " + parent.encode("ascii"))
    return b"\n".join(out) + sep + message


def _rebuild(top: Path, shas_oldest_first: list[str]) -> str:
    """Recreate commits on a new root, byte-identical apart from parents. Returns the new tip."""
    parent = None
    for sha in shas_oldest_first:
        raw = _git(top, "cat-file", "commit", sha).stdout
        if not raw.startswith(b"tree "):
            raise ToolError(f"cannot read commit {sha}")
        parent = _git_out(top, "hash-object", "-t", "commit", "-w", "--stdin",
                          input=_rebuilt_commit(raw, parent)).strip()
    return parent


@tool("bundle_prune",
      "Clear old git history: keep only the newest `keep` versions (default 5), rebuilt with the same trees, "
      "messages, authors and dates; delete tags, stashes and refs/original; expire reflogs; git gc. Without "
      "yes=true it is a dry run that lists kept and dropped versions. Refuses with unreleased changes or more "
      "than 1 branch.",
      {"type": "object",
       "properties": {"keep": {"type": "integer", "description": "versions to keep (>= 1)", "default": KEEP_DEFAULT},
                      "yes": {"type": "boolean", "description": "really rewrite history", "default": False},
                      "root": ROOT_PROP},
       "additionalProperties": False},
      readOnlyHint=False, destructiveHint=True)
def bundle_prune(keep: int = KEEP_DEFAULT, yes: bool = False, root: str | None = None) -> dict:
    if keep < 1:
        raise ToolError("KEEP must be at least 1")
    top = find_root(root)
    _require_worktree_root(top)
    if _git_out(top, "status", "--porcelain").strip("\n"):
        raise ToolError("unreleased changes: release or discard them first")
    branches = _lines(_git_out(top, "for-each-ref", "--format=%(refname)", "refs/heads"))
    if len(branches) > 1:
        raise ToolError(f"more than one branch ({len(branches)}): tundle uses a single branch")

    commits = []
    if _has_head(top):
        for line in _lines(_git_out(top, "log", "--no-show-signature", "--no-color", "--format=%H%x1f%s", "HEAD")):
            sha, _, subject = line.partition("\x1f")
            commits.append((sha, subject))
    total = len(commits)
    kept, dropped = commits[:keep], commits[keep:]
    result = {"pruned": False, "dry_run": False, "total": total, "keep": keep,
              "kept_subjects": [s for _, s in kept], "dropped_subjects": [s for _, s in dropped]}
    if total <= keep:
        return result
    if not yes:
        result["dry_run"] = True
        return result

    branch = _git(top, "symbolic-ref", "-q", "HEAD", check=False)
    branch_ref = _text(branch.stdout).strip()
    if branch.returncode != 0 or not branch_ref.startswith("refs/heads/"):
        raise ToolError("HEAD is not on a branch: check out the tundle's branch first")
    git_dir = Path(_git_out(top, "rev-parse", "--absolute-git-dir").strip())
    before = _tree_bytes(git_dir)

    old_head = _git_out(top, "rev-parse", "HEAD").strip()
    tip = _rebuild(top, [sha for sha, _ in reversed(kept)])
    if _git_out(top, "rev-parse", f"{tip}^{{tree}}") != _git_out(top, "rev-parse", "HEAD^{tree}"):
        raise ToolError("rebuilt history does not match HEAD's files; nothing was changed")
    _git(top, "update-ref", "-m", f"tundlekit prune: keep {keep}", branch_ref, tip, old_head)

    # Anything else pointing at old commits would keep them alive: delete every other ref (§13.1).
    for ref in _lines(_git_out(top, "for-each-ref", "--format=%(refname)")):
        if ref != branch_ref:
            _git(top, "update-ref", "--no-deref", "-d", ref, check=False)
    left = [r for r in _lines(_git_out(top, "for-each-ref", "--format=%(refname)")) if r != branch_ref]
    if left:
        raise ToolError(f"could not delete refs: {', '.join(left)}")
    common_dir = Path(_git_out(top, "rev-parse", "--path-format=absolute", "--git-common-dir").strip())
    for folder in {git_dir, common_dir}:
        for name in PSEUDO_REFS:
            try:
                (folder / name).unlink()
            except FileNotFoundError:
                pass
            except OSError as e:
                raise ToolError(f"could not delete {folder / name}: {e}") from None
    _git(top, "reflog", "expire", "--expire=now", "--expire-unreachable=now", "--all")
    _git(top, "gc", "--prune=now", "--quiet")

    result.update(pruned=True, git_bytes_before=before, git_bytes_after=_tree_bytes(git_dir))
    return result


# ---------------------------------------------------------------- init

@tool("bundle_init",
      "Make a folder a new tundle: git init (branch main) if needed, VERSION <today>.0, a CHANGELOG.md with the "
      "<!-- entries --> marker, and tundle's .gitignore and .gitattributes (existing ones are kept). No commit.",
      {"type": "object",
       "properties": {"root": {"type": "string", "description": "folder to set up; default the current directory"}},
       "additionalProperties": False},
      readOnlyHint=False, destructiveHint=False)
def bundle_init(root: str | None = None) -> dict:
    top = Path(os.path.abspath(root if root is not None else os.getcwd()))
    if top.exists() and not top.is_dir():
        raise ToolError(f"not a directory: {top}")
    if (top / "VERSION").exists():
        raise ToolError(f"{top} is already a tundle (VERSION exists)")
    changelog = top / "CHANGELOG.md"
    if os.path.lexists(changelog):
        try:
            lines = changelog.read_bytes().splitlines(keepends=True)
        except OSError as e:
            raise ToolError(f"cannot read {changelog}: {e}") from None
        if _marker_index(lines) is None:
            raise ToolError(f"{changelog} exists but has no line {MARKER}: add that line where entries "
                            "should go, or move the file away")
    top.mkdir(parents=True, exist_ok=True)

    probe = _git(top, "rev-parse", "--show-toplevel", check=False)
    top_level = _text(probe.stdout).strip()
    try:
        is_root = probe.returncode == 0 and os.path.samefile(top_level, top)
    except OSError:
        is_root = False
    if not is_root:
        _git(top, "init", "-q", "--initial-branch=main")

    version = f"{_today()}.0"
    created = []
    for name, content in (("VERSION", f"{version}\n"), ("CHANGELOG.md", CHANGELOG),
                          (".gitignore", GITIGNORE), (".gitattributes", GITATTRIBUTES)):
        path = top / name
        if name != "VERSION" and os.path.lexists(path):
            continue  # never overwrite CHANGELOG.md, .gitignore or .gitattributes
        path.write_bytes(content.encode("utf-8"))
        created.append(name)
    return {"root": str(top), "version": version, "created": created}


# ---------------------------------------------------------------- findings

def _finding(rule, severity, path, message, line=None, excerpt=""):
    return {"rule": rule, "severity": severity, "path": path, "line": line, "message": message,
            "excerpt": excerpt}


def _checker_result(findings: list[dict], **extra) -> dict:
    findings.sort(key=lambda f: (f["path"], f["line"] or 0, f["rule"]))
    counts = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        counts[f["severity"]] += 1
    return {"ok": counts["error"] == 0, "findings": findings, "counts": counts, **extra}


def _apply_ignore(findings: list[dict], ignore: list[str] | None) -> list[dict]:
    """Drop findings matched by `RULE` or `RULE:GLOB` entries (glob on the relative `/` path)."""
    if not ignore:
        return findings
    everywhere, scoped = set(), []
    for item in ignore:
        rule, sep, pattern = item.partition(":")
        if sep:
            scoped.append((rule.strip(), pattern.strip()))
        else:
            everywhere.add(rule.strip())
    return [f for f in findings
            if f["rule"] not in everywhere
            and not any(f["rule"] == rule and fnmatch.fnmatchcase(f["path"], pat) for rule, pat in scoped)]


IGNORE_PROP = {"type": "array", "items": {"type": "string"},
               "description": "findings to drop: RULE (everywhere) or RULE:GLOB (paths matching the glob)"}


def _rel(top: Path, path: str | os.PathLike) -> str:
    return os.path.relpath(path, top).replace(os.sep, "/")


def _read_text(path: Path) -> str:
    return path.read_bytes().decode("utf-8", errors="replace")


# ---------------------------------------------------------------- verify

def _clean_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value.startswith("`") and value.endswith("`"):
        value = value[1:-1].strip()
    return value


def _verify_source(top: Path, source: Path, findings: list[dict], checked: list[dict]) -> None:
    rel = _rel(top, source)
    lines = _read_text(source).splitlines()
    expected, hash_line = None, None
    for i, line in enumerate(lines, 1):
        m = HASH_LINE.match(line)
        if m:
            hash_line = i
            value = _clean_value(m.group(1))
            hexes = re.match(r"`?([0-9a-fA-F]{64})`?(?![0-9a-zA-Z])", value)
            if hexes:
                expected = hexes.group(1)
            break
    if expected is None:
        findings.append(_finding("B013", "warning", rel, "no hash recorded (add a `- SHA-256: <64 hex>` line)",
                                 hash_line, lines[hash_line - 1].strip() if hash_line else ""))

    folder = source.parent
    target, file_line = None, None
    for i, line in enumerate(lines, 1):
        m = FILE_LINE.match(line)
        if m:
            file_line = i
            name = _clean_value(m.group(1))
            problem = _target_problem(top, folder, name)
            if problem:
                findings.append(_finding("B013", "warning", rel,
                                         f"cannot tell which file: `- File: {name}` {problem}", i, line.strip()))
            else:
                target = folder / name
            break
    if file_line is None:
        candidates = sorted(p for p in folder.iterdir()
                            if p.is_file() and not p.is_symlink() and not _is_special(p.name))
        if len(candidates) == 1:
            target = candidates[0]
        else:
            what = "no file" if not candidates else f"{len(candidates)} files"
            findings.append(_finding("B013", "warning", rel, f"cannot tell which file the hash is for ({what} next "
                                     "to it; add a `- File: <name>` line)"))
    if expected is None or target is None:
        return

    digest = hashlib.sha256()
    try:
        with open(target, "rb") as f:
            for block in iter(lambda: f.read(MiB), b""):
                digest.update(block)
    except OSError as e:
        findings.append(_finding("B013", "warning", rel,
                                 f"cannot read {_rel(top, target)}: {e.strerror or e}", file_line))
        return
    actual = digest.hexdigest()
    match = actual == expected.lower()
    checked.append({"source": rel, "file": _rel(top, target), "expected": expected, "actual": actual,
                    "match": match})
    if not match:
        findings.append(_finding("B012", "error", rel,
                                 f"checksum mismatch for {_rel(top, target)}: expected {expected}, actual {actual}",
                                 hash_line, lines[hash_line - 1].strip()))


def _inside(base: str, path: str) -> bool:
    base, path = os.path.normcase(base), os.path.normcase(path)
    try:
        return os.path.commonpath([base, path]) == base
    except ValueError:  # another drive
        return False


def _target_problem(top: Path, folder: Path, name: str) -> str | None:
    """Why a `- File:` value can't be used, or None. Nothing outside root is touched (§13.1)."""
    if not name or "\0" in name:
        return "is empty or invalid"
    if os.path.isabs(name) or os.path.splitdrive(name)[0] or name.startswith(("/", "\\")):
        return "is an absolute path (it must be relative to SOURCE.md)"
    candidate = os.path.join(folder, *re.split(r"[\\/]", name))
    try:
        if not (_inside(os.path.abspath(top), os.path.normpath(os.path.abspath(candidate)))
                and _inside(os.path.realpath(top), os.path.realpath(candidate))):
            return "is outside the tundle"
        st = os.stat(candidate)
    except (OSError, ValueError):
        return "does not exist or can't be read"
    if not _stat.S_ISREG(st.st_mode):
        return "is not a regular file"
    return None


def _verify(top: Path) -> tuple[list[dict], list[dict]]:
    findings, checked = [], []
    for dirpath, _, filenames, _ in walk(top):
        for name in filenames:
            if name.lower() == "source.md":
                _verify_source(top, Path(dirpath) / name, findings, checked)
    checked.sort(key=lambda c: c["source"])
    return findings, checked


@tool("bundle_verify",
      "Check every SOURCE.md in a tundle: the file it describes (a `- File:` line, or the only other file in its "
      "folder) must match the recorded `- SHA-256:` hash. B012 = mismatch (error), B013 = hash or file unknown.",
      {"type": "object", "properties": {"root": ROOT_PROP, "ignore": IGNORE_PROP}, "additionalProperties": False},
      readOnlyHint=True)
def bundle_verify(root: str | None = None, ignore: list[str] | None = None) -> dict:
    top = find_root(root)
    findings, checked = _verify(top)
    return _checker_result(_apply_ignore(findings, ignore), checked=checked)


# ---------------------------------------------------------------- lint

def _name_problem(name: str) -> str | None:
    bad = sorted({c for c in name if c in BAD_CHARS or ord(c) < 32 or ord(c) == 127})
    if bad:
        shown = " ".join(c if c.isprintable() else repr(c) for c in bad)
        return f"name contains characters that don't work everywhere: {shown}"
    if name.endswith((" ", ".")):
        return "name ends with a space or a dot"
    if name.split(".", 1)[0].upper() in RESERVED:
        return f"{name.split('.', 1)[0]} is a reserved name on Windows"
    return None


def _copy_marker(stem: str) -> bool:
    """B003: the stem ends in a copy/version marker. `Name-v2` (hyphen right after a letter) is a name (§16.6)."""
    if not any(p.search(stem) for p in COPY_MARKERS):
        return False
    return not NAME_VERSION.search(stem)


def _is_junk_file(name: str) -> bool:
    return any(fnmatch.fnmatchcase(name, pat) for pat in JUNK_FILES)


SPECIAL_NAMES = ("readme.md", "source.md")
FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def _is_special(name: str) -> bool:
    """README.md or SOURCE.md, in any letter case (§16.1)."""
    return name.lower() in SPECIAL_NAMES


def _find_ci(folder: str | os.PathLike, name: str) -> str | None:
    """The entry of folder whose name equals name case-insensitively (the exact spelling first), or None."""
    try:
        entries = sorted(os.listdir(folder))
    except OSError:
        return None
    if name in entries:
        return name
    return next((e for e in entries if e.lower() == name.lower()), None)


def _fenced(lines: list[str]) -> list[bool]:
    """For each line, whether it is part of a fenced code block (fence lines included)."""
    out, fence = [], None
    for line in lines:
        if fence is None:
            m = FENCE_OPEN.match(line)
            if m:
                fence = m.group(1)
            out.append(fence is not None)
        else:
            out.append(True)
            m = FENCE_OPEN.match(line)
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and \
                    not line.strip()[len(m.group(1)):].strip():
                fence = None
    return out


def _table_rows(text: str):
    """(line number, first-cell names, line) for each body row of the Markdown tables in text (fences skipped)."""
    lines = text.splitlines()
    fenced = _fenced(lines)
    is_row = [ln.startswith("|") and not f for ln, f in zip(lines, fenced)]
    is_sep = [row and "-" in ln and set(ln.strip()) <= set("|-: ") for ln, row in zip(lines, is_row)]
    for i, line in enumerate(lines):
        if not is_row[i] or is_sep[i]:
            continue
        if i + 1 < len(lines) and is_sep[i + 1]:
            continue  # header row
        yield i + 1, _first_cell_names(line), line


def _cells(line: str) -> list[str]:
    """The cells of a table row; `|` inside backtick spans and `\\|` don't split."""
    cells, cell, in_code, i = [], [], False, 1 if line.startswith("|") else 0
    while i < len(line):
        c = line[i]
        if c == "`":
            in_code = not in_code
        elif c == "\\" and i + 1 < len(line) and line[i + 1] == "|":
            cell.append("|")
            i += 2
            continue
        elif c == "|" and not in_code:
            cells.append("".join(cell).strip())
            cell = []
            i += 1
            continue
        cell.append(c)
        i += 1
    if "".join(cell).strip():
        cells.append("".join(cell).strip())
    return cells


def _first_cell_names(line: str) -> list[str]:
    cells = _cells(line)
    if not cells:
        return []
    return [span.strip() for span in re.findall(r"`([^`]*)`", cells[0]) if span.strip()]


def _atomic_write(path: str | os.PathLike, data: bytes) -> None:
    """Write data to path atomically (§16.1): a temp file next to the target, then replace.

    A symlink is written through to its target, and an existing file keeps its permission bits.
    """
    target = os.path.realpath(path) if os.path.islink(path) else os.path.abspath(path)
    try:
        mode = _stat.S_IMODE(os.stat(target).st_mode)
    except OSError:
        mode = None
    folder, base = os.path.split(target)
    tmp = None
    try:
        for n in range(100):
            candidate = os.path.join(folder, f".{base}.{os.getpid()}.{n}.tundlekit-tmp")
            try:
                fd = os.open(candidate, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o666)
            except FileExistsError:
                continue
            tmp = candidate
            break
        else:
            raise OSError(f"cannot create a temporary file in {folder}")
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        if mode is not None:
            os.chmod(tmp, mode)
        os.replace(tmp, target)
        tmp = None
    finally:
        if tmp is not None:
            try:
                os.unlink(tmp)
            except OSError:
                pass


def _readme_path(folder: Path) -> Path:
    """folder's README.md in whatever letter case it has, or folder/README.md when there is none."""
    return folder / (_find_ci(folder, "README.md") or "README.md")


def _lint_setup_dir(top: Path, folder: Path, findings: list[dict]) -> None:
    readme = _readme_path(folder)
    listed: set[str] = set()
    if readme.is_file():
        rel_readme = _rel(top, readme)
        for lineno, names, line in _table_rows(_read_text(readme)):
            for name in names:
                is_dir = name.endswith("/")
                bare = name.rstrip("/")
                listed.add(bare)
                target = folder / bare
                exists = target.is_dir() if is_dir else target.exists()
                if not bare or not exists:
                    findings.append(_finding("B007", "error", rel_readme,
                                             f"table lists {name}, which doesn't exist in {_rel(top, folder)}/",
                                             lineno, line.strip()))
    for entry in _unlisted(folder, listed):
        path = folder / entry
        kind = "folder" if path.is_dir() else "file"
        where = "README.md table" if readme.is_file() else "README.md table (there is no README.md)"
        findings.append(_finding("B006", "error", _rel(top, path),
                                 f"{kind} {entry} is not listed in {_rel(top, folder)}/{where}"))


def _listed_names(folder: Path) -> set[str]:
    """Entry names (without a trailing `/`) named in the first cells of folder/README.md's tables."""
    readme = _readme_path(folder)
    if not readme.is_file():
        return set()
    return {name.rstrip("/") for _, names, _ in _table_rows(_read_text(readme)) for name in names}


def _unlisted(folder: Path, listed: set[str]) -> list[str]:
    """Entries of a setup/<dir>/ folder that B006 reports, sorted."""
    return [entry for entry in sorted(os.listdir(folder))  # links count as entries too
            if entry != ".git" and not _is_special(entry) and entry not in listed]


def _lint_changelog(top: Path, findings: list[dict]) -> None:
    version = None
    if not (top / "VERSION").is_file():
        findings.append(_finding("B010", "error", "VERSION", "VERSION is missing"))
    else:
        try:
            version = read_version(top)
        except ToolError as e:
            findings.append(_finding("B010", "error", "VERSION", str(e)))
    path = top / "CHANGELOG.md"
    if not path.is_file():
        findings.append(_finding("B010", "error", "CHANGELOG.md", "CHANGELOG.md is missing"))
        return
    lines = _read_text(path).split("\n")
    stripped = [ln.rstrip("\r") for ln in lines]
    if MARKER not in stripped:
        findings.append(_finding("B010", "error", "CHANGELOG.md", f"CHANGELOG.md has no {MARKER} line"))
        return
    if version is None:
        return
    at = stripped.index(MARKER)
    heading = next((i for i in range(at + 1, len(stripped)) if stripped[i].startswith("## ")), None)
    if heading is None:
        if not version.endswith(".0"):
            findings.append(_finding("B010", "error", "CHANGELOG.md",
                                     f"no CHANGELOG entry for VERSION {version}", at + 1, MARKER))
        return
    if not re.match(rf"## {re.escape(version)}(\s|$)", stripped[heading]):
        findings.append(_finding("B010", "error", "CHANGELOG.md",
                                 f"newest CHANGELOG entry doesn't match VERSION {version}",
                                 heading + 1, stripped[heading]))


@tool("bundle_lint",
      "Check a tundle's files against its rules: portable names (B001), path length (B002), copy/version "
      "markers like _v2 or (final) (B003), duplicate snapshots in versions/ (B004), junk files (B005), "
      "setup/<dir>/README.md tables (B006/B007), top-level README.md (B008), stale PDFs (B009), "
      "VERSION/CHANGELOG agreement (B010), large files (B011) and SOURCE.md checksums (B012/B013).",
      {"type": "object",
       "properties": {"root": ROOT_PROP,
                      "max_path": {"type": "integer", "description": "longest relative path allowed",
                                   "default": 160},
                      "large_mb": {"type": "number", "description": "report files larger than this (MiB)",
                                   "default": 500},
                      "ignore": IGNORE_PROP},
       "additionalProperties": False},
      readOnlyHint=True)
def bundle_lint(root: str | None = None, max_path: int = 160, large_mb: float = 500,
                ignore: list[str] | None = None) -> dict:
    top = find_root(root)
    findings: list[dict] = []
    junk: list[tuple[str, bool]] = []      # (relative path, is a folder): B005, severity decided below
    uncovered = 0                          # B014
    n_files = 0
    for dirpath, dirnames, filenames, linknames in walk(top):
        folder = Path(dirpath)
        rel_dir = _rel(top, folder) if folder != top else ""
        parts = rel_dir.split("/") if rel_dir else []
        in_versions = "versions" in parts
        keep_dirs = []
        for d in dirnames:
            if d == ".git":
                continue
            rel = f"{rel_dir}/{d}" if rel_dir else d
            _lint_name(rel, d, max_path, findings)
            if d in JUNK_DIRS:
                junk.append((rel, True))
                continue
            keep_dirs.append(d)
            if not rel_dir and not d.startswith(".") and d != "tools" and not (folder / d / "README.md").is_file():
                findings.append(_finding("B008", "warning", rel, "top-level folder without README.md"))
        dirnames[:] = keep_dirs

        for name in linknames:  # a link is 1 entry: name checks only, never followed
            n_files += 1
            _lint_name(f"{rel_dir}/{name}" if rel_dir else name, name, max_path, findings)
        names = filenames
        present = set(names)
        for name in names:
            n_files += 1
            rel = f"{rel_dir}/{name}" if rel_dir else name
            full = folder / name
            _lint_name(rel, name, max_path, findings)
            stem, ext = os.path.splitext(name)
            if not in_versions and _copy_marker(stem):
                findings.append(_finding("B003", "warning", rel,
                                         "looks like a copy or old version: replace the file instead"))
            if _is_junk_file(name):
                junk.append((rel, False))
            elif (len(parts) >= 2 and parts[0] == "setup" and not _is_special(name)
                  and not _source_covers(top, parts)):
                uncovered += 1
            try:
                stat = os.stat(full, follow_symlinks=False)
            except OSError:
                continue
            if stat.st_size > large_mb * MiB:
                findings.append(_finding("B011", "info", rel,
                                         f"large file: {stat.st_size / MiB:.1f} MiB (over {large_mb:g} MiB)"))
            if ext.lower() == ".pdf":
                _lint_pdf(folder, rel, stem, stat.st_mtime, present, findings)

        if parts and parts[-1] == "versions":
            _lint_versions(rel_dir, names, findings)
        if len(parts) == 2 and parts[0] == "setup":
            _lint_setup_dir(top, folder, findings)

    ignored = _git_ignored(top, junk)
    for rel, is_dir in junk:
        name = rel.rsplit("/", 1)[-1]
        what = f"junk folder {name} (caches don't belong in a tundle)" if is_dir else f"junk file {name}"
        if rel in ignored:
            findings.append(_finding("B005", "info", rel, f"{what}; git ignores it, but it still travels with a "
                                     "copied folder"))
        else:
            findings.append(_finding("B005", "warning", rel, what))
    if uncovered:
        findings.append(_finding("B014", "info", "setup",
                                 f"{uncovered} installer file(s) under setup/ have no SOURCE.md "
                                 "(tundlekit bundle source FILE --write)"))
    _lint_changelog(top, findings)
    findings.extend(_verify(top)[0])
    return _checker_result(_apply_ignore(findings, ignore), files=n_files)


def _source_covers(top: Path, parts: list[str]) -> bool:
    """A file in setup/<dir>/... is covered by a SOURCE.md in its own folder or its setup/<dir>/<sub>/ folder."""
    return _covered(top.joinpath(*parts), top.joinpath(*parts[:3]) if len(parts) >= 3 else None)


def _has_source(folder: Path) -> bool:
    name = _find_ci(folder, "SOURCE.md")
    return name is not None and (folder / name).is_file()


def _covered(folder: Path, sub: Path | None) -> bool:
    return _has_source(folder) or (sub is not None and _has_source(sub))


def _git_ignored(top: Path, entries: list[tuple[str, bool]]) -> set[str]:
    """The relative paths among entries that git ignores (`git check-ignore`); empty outside a work tree."""
    if not entries:
        return set()
    data = b"".join(rel.encode("utf-8") + b"\0" for rel, _ in entries)
    try:
        proc = _git(top, "check-ignore", "-z", "--stdin", input=data, check=False)
    except ToolError:  # git not installed: nothing counts as ignored
        return set()
    if proc.returncode not in (0, 1):
        return set()
    return {p.decode("utf-8", "replace") for p in proc.stdout.split(b"\0") if p}


def _lint_name(rel: str, name: str, max_path: int, findings: list[dict]) -> None:
    problem = _name_problem(name)
    if problem:
        findings.append(_finding("B001", "error", rel, problem))
    if len(rel) > max_path:
        findings.append(_finding("B002", "warning", rel, f"path is {len(rel)} characters (limit {max_path})"))


def _lint_pdf(folder: Path, rel: str, stem: str, mtime: float, present: set[str], findings: list[dict]) -> None:
    for name in sorted(present):
        src_stem, src_ext = os.path.splitext(name)
        if src_stem != stem or src_ext.lower() not in (".docx", ".pptx"):
            continue
        try:
            newer = (folder / name).stat().st_mtime > mtime
        except OSError:
            continue
        if newer:
            findings.append(_finding("B009", "warning", rel, f"PDF is older than {name}: export it again"))
            return


def _lint_versions(rel_dir: str, names: list[str], findings: list[dict]) -> None:
    groups: dict[str, list[str]] = {}
    for name in names:
        stem, ext = os.path.splitext(name)
        key = re.sub(r" \([^()]*\)$", "", stem) + ext
        groups.setdefault(key, []).append(name)
    for key, members in groups.items():
        if len(members) >= 2:
            members.sort()
            findings.append(_finding("B004", "info", f"{rel_dir}/{members[0]}",
                                     f"{len(members)} snapshots of {key}: keep the newest, older ones may go",
                                     excerpt=", ".join(members)))


# ---------------------------------------------------------------- source / setup table (§15.7)

ARCH_TOKEN = re.compile(r"(?<![^-_. ])(?:x86_64|x86-64|x64|x86|amd64|arm64|aarch64|win64|win32|64-bit|32-bit)"
                        r"(?![^-_. ])", re.I)
VERSION_GUESS = re.compile(r"(?<![0-9])v?([0-9]+(?:[._][0-9]+)+(?:-?rc[0-9]+)?)")
SEPARATORS = "-_. "
COMPOUND_EXTS = (".tar.gz", ".tar.xz", ".tar.bz2", ".tar.zst")
STUB_WORDS = re.compile(r"setup|installer|loader|latest", re.I)
STUB_NOTE = " ⚠ check: may download during install"
MATLAB_VERSION = re.compile(r"(?<![^-_. ])(R20[0-9]{2}[ab])(?![^-_. ])")
COMPACT_VERSION = re.compile(r"(?<![0-9])([0-9]{3,4})[-_. ]*$")
SETUP_TOKENS = (
    re.compile(r"(?:^|[-_. ])(?:user ?)?(?:setup|installer|install)$", re.I),               # separate word
    # CamelCase part: starts with a capital letter, the rest in any case
    re.compile(r"(?<=[^\W_])(?:U(?i:ser)(?i:s)|(?:U(?i:ser))?S)(?i:etup)$"),
    re.compile(r"(?<=[^\W_])(?:U(?i:ser)(?i:i)|(?:U(?i:ser))?I)(?i:nstall(?:er)?)$"),
)


def strip_arch(stem: str) -> str:
    """Remove architecture tokens delimited by the ends or `-_. `; the separators around each collapse to 1."""
    while True:
        m = ARCH_TOKEN.search(stem)
        if not m:
            return stem
        before, after = stem[:m.start()], stem[m.end():]
        if before and after:
            after = after[1:]          # keep the separator before the token
        elif before:
            before = before[:-1]       # token at the end: drop its separator
        elif after:
            after = after[1:]          # token at the start: drop its separator
        stem = before + after


def installer_stem(name: str) -> str:
    """The name without its extension; compound archive extensions count as 1 (§15.7)."""
    lower = name.lower()
    for ext in COMPOUND_EXTS:
        if lower.endswith(ext) and len(name) > len(ext):
            return name[:-len(ext)]
    return os.path.splitext(name)[0]


def _find_version(stem: str) -> tuple[str, str] | None:
    """(version, text before it) from an architecture-stripped stem, or None (§15.7, §16.6)."""
    m = VERSION_GUESS.search(stem)
    if m:
        return m.group(1).replace("_", "."), stem[:m.start(1)]
    m = MATLAB_VERSION.search(stem)
    if m:
        return m.group(1), stem[:m.start(1)]
    m = COMPACT_VERSION.search(stem)
    if m:
        digits, before = m.group(1), stem[:m.start(1)]
        attached = before and before[-1] not in SEPARATORS
        if before.strip(SEPARATORS) and (not attached or len(before) >= 2):
            cut = len(digits) - 2
            return f"{digits[:cut]}.{digits[cut:]}", before
    return None


def _clean_program(text: str) -> str:
    program = re.sub(r" +", " ", text.replace("_", " ").replace("-", " "))
    program = program.rstrip(SEPARATORS)
    return re.sub(r"(?:^| )v$", "", program).rstrip(SEPARATORS).strip()


def _drop_setup_token(program: str) -> str:
    """Remove 1 trailing Setup/UserSetup/Installer/Install token, a separate word or a CamelCase part (§16.6)."""
    for pattern in SETUP_TOKENS:
        m = pattern.search(program)
        if m and program[:m.start()].strip(SEPARATORS):
            return _clean_program(program[:m.start()])
    return program


def guess_program(name: str, is_dir: bool = False) -> tuple[str, str]:
    """(program, version) guessed from an installer's file name (§15.7, §16.6)."""
    original = name if is_dir else installer_stem(name)
    stem = strip_arch(original)
    found = _find_version(stem)
    version, program = found if found else ("", stem)
    program = _clean_program(program)
    if version:
        program = _drop_setup_token(program)
    if not program and not version:  # the name was nothing but architecture tokens
        program = re.sub(r" +", " ", original.replace("_", " ").replace("-", " ")).strip(SEPARATORS)
    return program, version


def _readme_guess(folder: Path, name: str) -> tuple[str, str] | None:
    """(program, version) from the "What it is" cell of the folder's README row for name (§16.6), or None."""
    readme = _find_ci(folder, "README.md")
    if readme is None:
        return None
    try:
        text = _read_text(folder / readme)
    except OSError:
        return None
    for _, names, line in _table_rows(text):
        if name not in names:
            continue
        cells = _cells(line)
        if len(cells) < 2:
            continue
        what = re.split(r"[,⚠]", cells[1], maxsplit=1)[0].strip()
        tokens = what.split()
        at = next((i for i, t in enumerate(tokens) if t[:1].isdigit()), len(tokens))
        program, version = " ".join(tokens[:at]), " ".join(tokens[at:])
        if program or version:
            return program, version
    return None


def _heading(program: str, version: str) -> str:
    return f"{program} {version}" if version else program


def _sha256_file(path: str | os.PathLike) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(MiB), b""):
            digest.update(block)
    return digest.hexdigest()


@tool("bundle_source",
      "Draft (or with write=true, write) the SOURCE.md next to an installer: program and version guessed from the "
      "file name (or taken from the folder's README.md row), download URL, file date, SHA-256 and install steps. "
      "A written SOURCE.md passes bundle_verify. An existing SOURCE.md is only replaced with force=true. With a "
      "directory as `file`, does this for every installer under setup/<dir>/ that has no SOURCE.md (existing ones "
      "are skipped) and returns {results: [...]}.",
      {"type": "object",
       "properties": {"file": {"type": "string",
                               "description": "the installer file, or a directory to cover every installer in it"},
                      "url": {"type": "string", "description": "official download URL"},
                      "install": {"type": "string", "description": "install steps or silent install command"},
                      "write": {"type": "boolean", "description": "write SOURCE.md (default: return the text only)",
                                "default": False},
                      "force": {"type": "boolean", "description": "replace an existing SOURCE.md",
                                "default": False}},
       "required": ["file"], "additionalProperties": False},
      readOnlyHint=False, destructiveHint=False)
def bundle_source(file: str, url: str | None = None, install: str | None = None, write: bool = False,
                  force: bool = False) -> dict:
    for label, value in (("url", url), ("install", install)):
        if value is not None and ("\n" in value or "\r" in value):
            raise ToolError(f"{label} must be 1 line")
    if os.path.isdir(file):
        return {"results": [_source_one(path, url, install, write, force=False)
                            for path in _uncovered_installers(Path(os.path.abspath(file)))]}
    if not os.path.isfile(file):
        raise ToolError(f"not a file or directory: {file}")
    name = os.path.basename(os.path.abspath(file))
    if _is_special(name):
        raise ToolError(f"{name} describes an installer; pass the installer file itself")
    return _source_one(file, url, install, write, force, strict=True)


def _source_one(file: str | os.PathLike, url: str | None, install: str | None, write: bool, force: bool,
                strict: bool = False) -> dict:
    """The single-file bundle_source. Without strict, an existing SOURCE.md is skipped (written false)."""
    file = os.fspath(file)
    name = os.path.basename(os.path.abspath(file))
    try:
        digest = _sha256_file(file)
        mtime = os.stat(file).st_mtime
    except OSError as e:
        raise ToolError(f"cannot read {file}: {e.strerror or e}") from None
    folder = os.path.dirname(file)
    program, version = _readme_guess(Path(os.path.abspath(folder or ".")), name) or guess_program(name)
    text = "\n".join([
        f"# {_heading(program, version)}",
        "",
        f"- File:       {name}",
        f"- Source:     {url if url is not None else '<official download URL>'}",
        f"- Downloaded: {_dt.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')}",
        f"- SHA-256:    {digest}",
        f"- Install:    {install if install is not None else '<steps>'}",
    ]) + "\n"
    existing = _find_ci(folder or ".", "SOURCE.md")
    path = os.path.join(folder, existing or "SOURCE.md")
    result = {"path": path, "text": text, "sha256": digest, "program": program, "version": version,
              "written": False}
    if existing is not None and not force:
        if not strict:
            result["skipped"] = "SOURCE.md already exists"
            return result
        if write:
            raise ToolError(f"{path} already exists: pass force to replace it")
    if write:
        try:
            _atomic_write(path, text.encode("utf-8"))
        except OSError as e:
            raise ToolError(f"cannot write {path}: {e.strerror or e}") from None
        result["written"] = True
    return result


def _setup_base(folder: Path) -> Path | None:
    """The `setup` folder whose B014 rules apply to a bundle_source directory; None: folder is a setup/<dir>/."""
    for candidate in (folder, *folder.parents):
        if _is_tundle(candidate):
            return candidate / "setup"
    for candidate in (folder, *folder.parents):
        if candidate.name == "setup":
            return candidate
    if (folder / "setup").is_dir():
        return folder / "setup"
    return None


def _uncovered_installers(folder: Path) -> list[Path]:
    """Files under folder that B014 counts (installers under setup/<dir>/ without a SOURCE.md), 1 per folder."""
    base = _setup_base(folder)
    if base is None:  # a plain folder: treat it as a setup/<dir>/ folder of its own
        base, start = folder.parent, folder
    elif _inside(os.path.abspath(base), os.path.abspath(folder)):
        start = folder
    elif _inside(os.path.abspath(folder), os.path.abspath(base)):
        start = base
    else:
        return []
    found = []
    for dirpath, dirnames, filenames, _ in walk(start):
        dirnames[:] = [d for d in dirnames if d not in JUNK_DIRS]
        here = Path(dirpath)
        parts = Path(os.path.relpath(here, base)).parts
        if not parts or parts[0] in (os.curdir, os.pardir):
            continue  # files directly in setup/ are not counted
        sub = base.joinpath(*parts[:2]) if len(parts) >= 2 else None
        if _covered(here, sub):
            continue
        installers = [n for n in filenames if not _is_special(n) and not _is_junk_file(n)]
        if installers:
            found.append(here / installers[0])  # 1 SOURCE.md per folder: the first installer in sorted order
    return found


def _insert_rows(text: str, rows: list[str], title: str) -> str:
    """README text with rows added after the last row of its first table, or with a new table appended.

    Lines inside fenced code blocks never count as a table (§16.1).
    """
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    fenced = _fenced([ln.rstrip("\r\n") for ln in lines])
    is_row = [ln.startswith("|") and not f for ln, f in zip(lines, fenced)]
    first = next((i for i, row in enumerate(is_row) if row), None)
    if first is None:
        body = "".join(f"{r}{newline}" for r in rows)
        table = f"| File | What it is |{newline}|---|---|{newline}{body}"
        if not text:
            return f"# {title}{newline}{newline}{table}"
        if not text.endswith(("\n", "\r")):
            text += newline
        return text + newline + table
    last = first
    while last + 1 < len(lines) and is_row[last + 1]:
        last += 1
    if not lines[last].endswith(("\n", "\r")):
        lines[last] += newline
    lines[last + 1:last + 1] = [f"{r}{newline}" for r in rows]
    return "".join(lines)


@tool("bundle_setup_table",
      "Add a README.md table row for every entry of a setup/<dir>/ folder that the table doesn't list yet (the "
      "B006 findings), with the program and version guessed from the name; stub installers get a warning note. "
      "Junk files and names with a backtick or | are never added; they are listed in `skipped`. "
      "Returns the rows; write=true adds them to README.md.",
      {"type": "object",
       "properties": {"dir": {"type": "string", "description": "the setup/<dir>/ folder"},
                      "write": {"type": "boolean", "description": "update README.md (default: rows only)",
                                "default": False}},
       "required": ["dir"], "additionalProperties": False},
      readOnlyHint=False, destructiveHint=False)
def bundle_setup_table(dir: str, write: bool = False) -> dict:
    folder = Path(os.path.abspath(dir))
    if not folder.is_dir():
        raise ToolError(f"not a directory: {dir}")
    rows, skipped = [], []
    try:
        entries = _unlisted(folder, _listed_names(folder))
    except OSError as e:
        raise ToolError(f"cannot read {dir}: {e.strerror or e}") from None
    for entry in entries:
        is_dir = (folder / entry).is_dir()
        if (is_dir and entry in JUNK_DIRS) or (not is_dir and _is_junk_file(entry)):
            skipped.append({"name": entry, "reason": "junk (bundle lint B005): delete it instead of listing it"})
            continue
        if "`" in entry or "|" in entry:
            skipped.append({"name": entry, "reason": "the name contains a backtick or |, which a table row "
                                                     "cannot hold: rename it"})
            continue
        program, version = guess_program(entry, is_dir=is_dir)
        what = _heading(program, version)
        if not version and STUB_WORDS.search(entry):
            what += STUB_NOTE
        shown = f"{entry}/" if is_dir else entry
        rows.append(f"| `{shown}` | {what} |")
    written = False
    if write and rows:
        readme = _readme_path(folder)
        try:
            text = readme.read_bytes().decode("utf-8") if os.path.exists(readme) else ""
        except (OSError, UnicodeDecodeError) as e:
            raise ToolError(f"cannot read {readme}: {e}") from None
        try:
            _atomic_write(readme, _insert_rows(text, rows, folder.name).encode("utf-8"))
        except OSError as e:
            raise ToolError(f"cannot write {readme}: {e.strerror or e}") from None
        written = True
    return {"added": rows, "skipped": skipped, "written": written}


# ---------------------------------------------------------------- CLI

def add_cli(groups) -> None:
    from tundlekit.cli_support import common_flags

    p = groups.add_parser("bundle", help="tundle maintenance: status, release, compare, prune, init, lint, verify")
    cmds = p.add_subparsers(dest="command", metavar="COMMAND", required=True)

    def command(name, help, handler, checker=False, root=True):
        c = cmds.add_parser(name, help=help)
        if root:
            c.add_argument("--root", help="tundle root (default: walk up from the current directory)")
        common_flags(c, checker=checker)
        c.set_defaults(handler=handler)
        return c

    command("status", "version, history length, sizes, unreleased changes", _cli_status)
    c = command("release", "stage everything, bump VERSION, add a CHANGELOG entry, commit", _cli_release)
    c.add_argument("summary", metavar="SUMMARY", help="what changed")
    c = command("compare", "which of this copy and the copy at OTHER is newer", _cli_compare)
    c.add_argument("other", metavar="OTHER", help="path of the other tundle copy")
    c = command("prune", "keep only the newest KEEP versions (dry run without --yes)", _cli_prune)
    c.add_argument("keep", metavar="KEEP", type=int, nargs="?", default=KEEP_DEFAULT,
                   help=f"versions to keep (default {KEEP_DEFAULT})")
    c.add_argument("--yes", action="store_true", help="really rewrite history")
    c = command("init", "make a folder a new tundle", _cli_init, root=False)
    c.add_argument("path", metavar="PATH", nargs="?", default=".", help="folder (default: current directory)")
    c = command("lint", "check files against the tundle rules (B001-B013)", _cli_lint, checker=True)
    c.add_argument("--max-path", type=int, default=160, help="longest relative path allowed (default 160)")
    c.add_argument("--large-mb", type=float, default=500, help="report files larger than this, MiB (default 500)")
    c.add_argument("--ignore", action="append", metavar="RULE[:GLOB]", help="drop findings (repeatable)")
    c = command("source", "draft or write the SOURCE.md next to an installer", _cli_source, root=False)
    c.add_argument("file", metavar="FILE", help="the installer file (a directory with --all)")
    c.add_argument("--all", action="store_true",
                   help="FILE is a directory: draft or write a SOURCE.md for every installer that has none")
    c.add_argument("--url", help="official download URL")
    c.add_argument("--install", metavar="CMD", help="install steps or silent install command")
    c.add_argument("--write", action="store_true", help="write SOURCE.md")
    c.add_argument("--force", action="store_true", help="replace an existing SOURCE.md")
    c = command("setup-table", "add README.md table rows for unlisted setup entries", _cli_setup_table, root=False)
    c.add_argument("dir", metavar="DIR", help="the setup/<dir>/ folder")
    c.add_argument("--write", action="store_true", help="update README.md")
    c = command("verify", "check SOURCE.md checksums", _cli_verify, checker=True)
    c.add_argument("--ignore", action="append", metavar="RULE[:GLOB]", help="drop findings (repeatable)")


def _cli_status(args):
    from tundlekit.cli_support import CliResult

    r = bundle_status(root=args.root)
    lines = [f"version:  {r['version']}"]
    if r["last"]:
        lines.append(f"last:     {r['last']['date']}  {r['last']['subject']}")
        lines.append(f"history:  {r['history']} version(s) (clear back to {KEEP_DEFAULT} when over "
                     f"{PRUNE_HINT_AT}: tundlekit bundle prune, see HISTORY-CLEANUP.md)")
    lines.append(f"size:     content {human_size(r['content_bytes'])}, .git {human_size(r['git_bytes'])}")
    if not r["pending"]:
        lines.append("changes:  none")
    else:
        lines.append(f"changes:  {len(r['pending'])} unreleased (run: tundlekit bundle release \"what changed\")")
        lines += [f"  {p['status']:>2} {p['path']}" for p in r["pending"][:20]]
        if len(r["pending"]) > 20:
            lines.append(f"  ... {len(r['pending']) - 20} more")
    if r["largest"]:
        lines.append("largest:")
        lines += [f"  {human_size(f['bytes']):>10}  {f['path']}" for f in r["largest"]]
    return CliResult(r, "\n".join(lines))


def _cli_release(args):
    from tundlekit.cli_support import CliResult

    r = bundle_release(summary=args.summary, root=args.root)
    lines = [f"released {r['version']} ({r['stats_text']})"]
    if r["prune_hint"]:
        lines.append(f"history has {r['history']} versions: time to clear it "
                     "(tundlekit bundle prune, see HISTORY-CLEANUP.md)")
    return CliResult(r, "\n".join(lines))


def _cli_compare(args):
    from tundlekit.cli_support import CliResult

    r = bundle_compare(other=args.other, root=args.root)
    if r["result"] == "same":
        text = f"same version: {r['mine']}"
    elif r["result"] == "this_newer":
        text = f"this copy is newer: {r['mine']} > {r['theirs']} ({r['other']})"
    else:
        text = f"the other copy is newer: {r['theirs']} > {r['mine']}; copy it over this one"
    return CliResult(r, text)


def _cli_prune(args):
    from tundlekit.cli_support import CliResult

    r = bundle_prune(keep=args.keep, yes=args.yes, root=args.root)
    if r["total"] <= r["keep"]:
        return CliResult(r, f"history has {r['total']} version(s); nothing to clear (keep={r['keep']})")
    lines = [f"history: {r['total']} versions"]
    lines += [f"  keep  {s}" for s in r["kept_subjects"]]
    lines += [f"  drop  {s}" for s in r["dropped_subjects"]]
    if r["dry_run"]:
        lines += ["", "dry run: nothing changed. Re-run with --yes to clear (see HISTORY-CLEANUP.md)."]
    else:
        lines.append(f"cleared: {r['keep']} versions kept, .git now {human_size(r['git_bytes_after'])} "
                     f"(was {human_size(r['git_bytes_before'])})")
        lines.append("other copies still hold the old history: replace them with this copy "
                     "(don't git pull between them)")
    return CliResult(r, "\n".join(lines))


def _cli_init(args):
    from tundlekit.cli_support import CliResult

    r = bundle_init(root=args.path)
    lines = [f"new tundle {r['version']} in {r['root']}"]
    lines += [f"  created {p}" for p in r["created"]]
    lines.append('next: add content, then tundlekit bundle release "what changed"')
    return CliResult(r, "\n".join(lines))


def _cli_lint(args):
    from tundlekit.cli_support import CliResult

    return CliResult(bundle_lint(root=args.root, max_path=args.max_path, large_mb=args.large_mb,
                                 ignore=args.ignore))


def _cli_source(args):
    from tundlekit.cli_support import CliResult

    is_dir = os.path.isdir(args.file)
    if args.all and not is_dir:
        raise ToolError(f"--all needs a directory: {args.file}")
    if is_dir and not args.all:
        raise ToolError(f"{args.file} is a directory: add --all to cover every installer in it")
    r = bundle_source(file=args.file, url=args.url, install=args.install, write=args.write, force=args.force)
    if args.all:
        lines = []
        for one in r["results"]:
            state = ("skipped (SOURCE.md exists)" if one.get("skipped")
                     else "wrote" if one["written"] else "would write")
            lines.append(f"{state} {one['path']}: {_heading(one['program'], one['version'])}")
        if not lines:
            lines.append("every installer already has a SOURCE.md")
        elif not args.write:
            lines.append("(dry run: add --write to create the SOURCE.md files)")
        return CliResult(r, "\n".join(lines))
    text = r["text"].rstrip("\n")
    text += f"\n\nwrote {r['path']}" if r["written"] else "\n\n(dry run: add --write to create SOURCE.md)"
    return CliResult(r, text)


def _cli_setup_table(args):
    from tundlekit.cli_support import CliResult

    r = bundle_setup_table(dir=args.dir, write=args.write)
    lines = list(r["added"]) or ["every entry is already listed"]
    lines += [f"skipped {s['name']}: {s['reason']}" for s in r.get("skipped", [])]
    if r["added"]:
        lines.append("added to README.md" if r["written"] else "(dry run: add --write to update README.md)")
    return CliResult(r, "\n".join(lines))


def _cli_verify(args):
    from tundlekit.cli_support import CliResult

    return CliResult(bundle_verify(root=args.root, ignore=args.ignore))
