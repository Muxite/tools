# tundlekit manifest

This is the contract for `tundlekit`. Tests are written from this document alone, and the
implementation must satisfy it. If this document and a test disagree, this document wins.
Where this document is silent, the implementation may choose, and tests must not assume.

`tundlekit` turns the tooling and working rules in the **tundle** transfer bundle into tools that
**any** agent can use, whatever its vendor:

- a **CLI** (`tundlekit ...`), for agents that can run shell commands;
- an **MCP server** (`tundlekit-mcp`, stdio), for agents that speak the Model Context Protocol;
- **skills** (`skills/<name>/SKILL.md`, open Agent Skills format), for agents that load
  instruction packs;
- an **`AGENTS.md`** that says how to wire all 3 into common agents.

The sources are the files in tundle: `tools/tundle.sh`, `README.md`, `HISTORY-CLEANUP.md`,
`setup/README.md`, and, under `ai4research/`, `notes/report-general/build/{deckkit,palette,figures,render}.py`
plus `checks/*.py`, `papers/{fetch,body,peek}.py`, `translate/` (the `tcheck.py` checker, glossary, prompts and rules),
`notes/GUIDE-reports-and-presentations.md` and `notes/40-style-card.md`.

---

## 0. Global conventions

Notation: inside Markdown table cells, `\|` stands for a plain `|`; for example, a regex written `a\|b` is `a|b`.

### 0.1 Layout

```
tundlekit/__init__.py      __version__, MODULES           (given, do not change the MODULES list)
tundlekit/registry.py      @tool, ToolError, call, validate, load_all  (given, do not change behaviour)
tundlekit/cli_support.py   CliResult, common_flags, emit (given: how modules add CLI groups via add_cli)
tundlekit/cli.py           main(argv) -> int; console script `tundlekit`
tundlekit/mcp_server.py    main() -> int; console script `tundlekit-mcp`; also `python -m tundlekit.mcp_server`
tundlekit/__main__.py      `python -m tundlekit` == `tundlekit`
tundlekit/bundle.py        §2
tundlekit/deck.py          §3
tundlekit/diagram.py       §4
tundlekit/chart.py         §5
tundlekit/palette.py       §6
tundlekit/textlint.py      §7
tundlekit/render.py        §8
tundlekit/papers.py        §9
tundlekit/translate/       §10 (package; tcheck.py is vendored and unchanged apart from its glossary path)
skills/<name>/SKILL.md     §11
AGENTS.md, README.md       §12
pyproject.toml             §12
tests/                     visible tests
```

- Python ≥ 3.10. The core (CLI, MCP server, bundle, diagram, chart, palette, textlint, papers peek/body,
  translate) uses the **standard library only**.
- Optional extras: `office` = `python-pptx`, `Pillow`; `pdf` = `pymupdf`. A tool that needs a missing optional
  package raises `ToolError` whose message contains `not installed` and the pip package name.
- Importing any `tundlekit` module must not import an optional package at module level.
- Every module listed in `MODULES` registers its tools with `tundlekit.registry.tool` at import time.
  `tundlekit.translate` registers from `tundlekit/translate/__init__.py`.

### 0.2 Tool functions

- A tool is a plain function taking keyword arguments that match its JSON Schema, returning a JSON-serialisable
  `dict`. The same function is used by the CLI, by `tundlekit call`, and by the MCP server.
- Every tool schema has `"type": "object"` and `"additionalProperties": false`.
- Every tool has a non-empty description of at most 1024 characters.
- Paths in arguments are strings. Relative paths resolve against the process's current working directory.
- Paths in results are strings.
- User-facing failures raise `ToolError(message)`. Nothing else may escape for bad input.
- Tools that only read carry annotation `readOnlyHint: true`. `bundle_release`, `bundle_prune` and `bundle_init`
  carry `readOnlyHint: false`, and `bundle_prune` also carries `destructiveHint: true`.

### 0.3 Findings (all checkers)

Checkers return findings in 1 shape:

```json
{"rule": "S001", "severity": "error", "path": "report.md", "line": 12, "message": "...", "excerpt": "..."}
```

- `severity` is one of `error`, `warning`, `info`.
- `line` is 1-based, or `null` when the finding is not tied to a line.
- `path` is the path as given by the caller, or relative to the checked root for tree checks, always with `/`
  separators.
- Checker results always contain `"ok": bool`, `"findings": [...]` and `"counts": {"error": n, "warning": n, "info": n}`,
  where all 3 count keys are always present. `ok` is true when there are no `error` findings.
- Findings are sorted by `(path, line or 0, rule)`.

### 0.4 CLI

- Entry point `tundlekit.cli.main(argv: list[str] | None = None) -> int`. It never calls `sys.exit` itself.
  The console script wraps it.
- `tundlekit --version` prints `tundlekit <version>` and returns 0.
- Subcommands are `tundlekit <group> <command> [args]`. Groups and commands are listed in each section.
- Every command accepts `--json`, which prints the tool result as JSON (`indent=2`, `ensure_ascii=False`) to stdout
  and nothing else to stdout.
- Without `--json`, output is human-readable. Only bundle output text is specified (§2.9). Tests must use `--json`
  everywhere else.
- Exit codes: `0` success; `1` a check found errors (`ok` false), or a `ToolError`; `2` usage error (argparse).
  Checker commands accept `--strict`, which also makes warnings exit 1.
- On a `ToolError`, the CLI prints `tundlekit: <message>` to stderr and returns 1. With `--json` it also prints
  `{"error": "<message>"}` to stdout.
- `tundlekit tools [--json]` lists every registered tool. With `--json` it prints `{"tools": [<listing>...]}`,
  where each listing is `Tool.listing()`.
- `tundlekit call <tool-name> [--args JSON | --args-file PATH]` runs any registered tool through `registry.call`
  and prints its result as JSON. An unknown tool name gives exit 2 and a stderr message containing the name.
  Invalid arguments give exit 1, `{"error": ...}` on stdout, and a message naming the property.
- Stdout is written as UTF-8 even on Windows consoles.

### 0.5 MCP server

`tundlekit-mcp` speaks MCP over stdio: 1 JSON-RPC 2.0 message per line (UTF-8, `\n`-terminated) on stdin/stdout.
Stdout carries protocol messages only; logs go to stderr. The server exits 0 when stdin closes.

| Method | Behaviour |
|---|---|
| `initialize` | result `{"protocolVersion", "capabilities": {"tools": {"listChanged": false}}, "serverInfo": {"name": "tundlekit", "version": __version__}, "instructions": <non-empty string>}`. Supported versions: `2025-11-25`, `2025-06-18`, `2025-03-26`, `2024-11-05`. If the client's requested version is supported, it is echoed; otherwise the server answers `2025-11-25` |
| `notifications/initialized`, any other notification | no response |
| `ping` | result `{}` |
| `tools/list` | result `{"tools": [listing, ...]}` with every registered tool (all of `load_all()`), in registration order. No `nextCursor` |
| `tools/call` | params `{"name", "arguments"}` (arguments may be absent, meaning `{}`). On success: result `{"content": [{"type": "text", "text": <json.dumps(result)>}], "structuredContent": result, "isError": false}`. On `ToolError` or invalid arguments: result `{"content": [{"type": "text", "text": <message>}], "isError": true}`. On any other exception: the same with `isError: true` and a message starting `internal error:` |
| unknown tool name in `tools/call` | JSON-RPC error `-32602`, message containing the name |
| unknown method (request with an id) | JSON-RPC error `-32601` |
| a line that is not valid JSON | error `-32700`, `"id": null` |
| valid JSON that is not a request object (an array, a number, an object with no `method`) | error `-32600`, `id` taken from the object if present, else `null` |
| requests before `initialize` | answered normally (the server is lenient) |

Responses carry the request's `id` unchanged (string or number) and `"jsonrpc": "2.0"`. The server handles requests
in order and flushes after each response. Blank lines are ignored.

`tundlekit-mcp --root PATH` sets the default root for bundle tools (otherwise the server's working directory).

---

## 1. Registry (given)

`tundlekit/registry.py` is provided and is part of the contract: `ToolError`, `Tool`, `TOOLS`, `tool()`,
`validate()`, `call()` and `load_all()`. Tests may test it directly.

---

## 2. bundle: tundle maintenance (port of `tools/tundle.sh`)

A **tundle** is a folder under git that holds a `VERSION` file, a `CHANGELOG.md` with a `<!-- entries -->` marker,
and content. `tundlekit bundle` replaces `tundle.sh`/`tundle.ps1` on any OS, with no Git Bash needed. It keeps the
on-disk formats identical, so both tools can run on the same tundle.

### 2.1 Common

- `root` argument (CLI `--root`). If omitted, walk up from the current directory to the first directory that holds
  both `VERSION` and `CHANGELOG.md`. If none is found, raise `ToolError` containing `no tundle found`.
- Git is run as a subprocess (`git -C <root> ...`). If git is missing: `ToolError` containing `git not found`.
- **Clock**: "now" is local time, unless the environment variable `TUNDLEKIT_NOW` is set to
  `YYYY-MM-DDTHH:MM` or `YYYY-MM-DDTHH:MM:SS`, which is then used as now.
- **Version** format: `YYYY.MM.DD.N` (N ≥ 0, no leading zeros required or stripped). Versions are ordered as tuples
  of 4 integers. `VERSION` is read with whitespace/CR/LF stripped, and written as `<version>\n`.
- A `VERSION` that doesn't match the format raises `ToolError` containing `invalid VERSION`, in every command that reads it.
- Sizes are in bytes. `content_bytes` is the total size of files under root, excluding `.git`.
  `git_bytes` is the total size of files under `.git`.

### 2.1a Pinned details

- `largest` paths are relative to root with `/`. Size ties are broken by ascending path.
- `pending` paths are exactly as `git status --porcelain` prints them (an untracked directory is `newdir/`).
- `last.date` is the author date (`%ai`).
- `bundle_lint` never raises for a malformed or missing `VERSION`: it reports B010 instead.
- B010's version match is exact: the heading is `## {VERSION}` followed by whitespace or the end of the line.
- Path rules: B009 is reported on the PDF path, and B012/B013 on the `SOURCE.md` path. B006 is reported on the unlisted entry's path, and B007 on the `README.md` path, with the table line number and the missing name in the message. B008, B002, B011 and B001 are reported on the entry's own path, with `line` null. Every finding has an `excerpt` key (possibly empty).
- B004 groups files per `versions` directory.
- In MCP, an `isError` result has no `structuredContent`. An `initialize` without `protocolVersion` gets `2025-11-25`.
- argparse usage errors may surface from `cli.main` as `SystemExit(2)`. This is the only exception to "never calls sys.exit".
- `tools/list` and `tundlekit tools` follow `MODULES` order.

### 2.2 `bundle_status` / `tundlekit bundle status`

Result:

```json
{"root": "...", "version": "2026.09.15.1",
 "last": {"date": "2026-09-15 18:27:00 +0200", "subject": "tundle 2026.09.15.1: ..."},
 "history": 1, "prune_hint": false,
 "content_bytes": 123, "git_bytes": 456,
 "pending": [{"status": "M", "path": "README.md"}],
 "largest": [{"path": "setup/x.iso", "bytes": 999}]}
```

- `last` is `null` and `history` is `0` when the repository has no commits.
- `history` is the number of commits reachable from HEAD. `prune_hint` is `history > 10`.
- `pending` has 1 entry per line of `git status --porcelain`. `status` is the 2-char XY code with spaces stripped
  (`??` for untracked). `path` is the path as git prints it (for a rename, the new path).
- `largest`: the 5 largest files under root, excluding `.git`, in descending size order, ties broken by path.

### 2.3 `bundle_release` / `tundlekit bundle release "SUMMARY"`

Arguments: `summary` (string, required), `root`.

1. If `summary` is empty or only whitespace: `ToolError` containing `usage: release`.
2. If `CHANGELOG.md` has no line exactly equal to `<!-- entries -->`: `ToolError` containing `<!-- entries -->`.
   Nothing is staged or changed.
3. `git add -A`. If nothing is staged (`git diff --cached --quiet` succeeds): `ToolError` containing
   `nothing to release`.
4. **Stats** from `git diff --cached --name-status --find-renames`: count lines whose status letter is `A`, `M`,
   `D` or `R` (the first character). Other letters are ignored.
   `stats_text` = `"{A} added, {M} modified, {D} removed, {R} renamed"`.
5. **New version**. `today` = now as `YYYY.MM.DD`. If the date part of the old version equals `today`, new =
   `today.(N+1)`; otherwise new = `today.1`. If new ≤ old (a clock behind the last device), new =
   `<old date part>.(N+1)`. Versions never go backwards.
6. Write `VERSION`. Insert after the **first** `<!-- entries -->` line:
   ```
   <blank line>
   ## {new}  ({YYYY-MM-DD HH:MM})
   <blank line>
   {summary}
   <blank line>
   _{stats_text}_
   ```
   Everything else in `CHANGELOG.md` is kept byte for byte, including the existing line endings of other lines.
   Inserted lines end in `\n`. `summary` is written as given (stripped of leading/trailing whitespace).
7. Stage `VERSION` and `CHANGELOG.md`, then commit with message `tundle {new}: {summary}`.
8. Result: `{"version": new, "previous": old, "stats": {"added", "modified", "removed", "renamed"},
   "stats_text", "commit": <full sha>, "history": n, "prune_hint": n > 10}`.

Stats are taken before `VERSION` and `CHANGELOG.md` are rewritten. The commit uses git's configured identity. If none
is configured, git's own error comes back as a `ToolError`.

### 2.4 `bundle_compare` / `tundlekit bundle compare OTHER`

Arguments: `other` (path, required), `root`.
If `other` has no `VERSION` file: `ToolError` containing `no VERSION`.
Result `{"mine", "theirs", "other": <path as given>, "result": "same" | "this_newer" | "other_newer"}`.

### 2.5 `bundle_prune` / `tundlekit bundle prune [KEEP] [--yes]`

Arguments: `keep` (integer, default 5), `yes` (boolean, default false), `root`.

Checks, in order:
1. `keep < 1`: `ToolError` containing `KEEP must be at least 1`.
2. `git status --porcelain` not empty: `ToolError` containing `unreleased changes`.
3. More than 1 local branch: `ToolError` containing `more than one branch`.

Then with `total` = number of commits reachable from HEAD:
- `total <= keep`: result `{"pruned": false, "dry_run": false, "total", "keep", "kept_subjects": [...all...], "dropped_subjects": []}`.
- Otherwise `kept_subjects` = subjects of the newest `keep` commits (newest first), `dropped_subjects` = the rest
  (newest first).
  - Without `yes`: result `{"pruned": false, "dry_run": true, "total", "keep", "kept_subjects", "dropped_subjects"}`.
    Nothing changes (same HEAD sha, same refs).
  - With `yes`: rebuild the newest `keep` commits on a new root commit, oldest first. Each new commit has the same
    tree, full message (byte-exact), author name/email/date and committer name/email/date as the original. Point the
    current branch at the rebuilt tip. Delete every ref under `refs/tags`, `refs/original` and `refs/stash`. Expire
    all reflogs now. Run `git gc --prune=now` (`--aggressive` is allowed). Result
    `{"pruned": true, "dry_run": false, "total", "keep", "kept_subjects", "dropped_subjects", "git_bytes_before", "git_bytes_after"}`.
    Afterwards `git rev-list --count HEAD` equals `keep`. The working tree, `VERSION` and `CHANGELOG.md` are unchanged.
    `git cat-file -e <dropped sha>` fails for every dropped commit.

### 2.6 `bundle_init` / `tundlekit bundle init [PATH]`

Arguments: `root` (path; CLI positional, default the current directory).
- If `root/VERSION` exists: `ToolError` containing `already a tundle`.
- Create `root` if missing. Run `git init` if `root` is not a git work tree root, on branch `main`.
- An existing `CHANGELOG.md` is never overwritten. If it has the `<!-- entries -->` line it is kept; otherwise
  `ToolError` containing `<!-- entries -->`, and nothing is written.
- Write `VERSION` = `{today}.0`, a `CHANGELOG.md` (when missing) whose first line is `# Changelog` and which contains the
  `<!-- entries -->` line and no entries, a `.gitignore` with the same patterns as tundle's (§2.7 B005 list), and a
  `.gitattributes` containing the line `* -text`. Do not overwrite an existing `.gitignore` or `.gitattributes`.
- Result `{"root", "version", "created": [relative paths written]}`. No commit is made.
- The first `release` after `init` produces `{today}.1`.

### 2.7 `bundle_lint` / `tundlekit bundle lint`

Arguments: `root`, `max_path` (int, default 160), `large_mb` (number, default 500).
Walks every file and directory under root, skipping `.git` entirely. Paths in findings are relative, with `/`.
Result: checker shape (§0.3) plus `"files": <number of files walked>`.

| Rule | Severity | Finding |
|---|---|---|
| B001 | error | a file or directory name that contains any of `: * ? " < > \|` or a control character, ends with a space or `.`, or whose part before the first `.` is, case-insensitively, a Windows reserved name (`CON PRN AUX NUL COM1`–`COM9` `LPT1`–`LPT9`) |
| B002 | warning | a relative path longer than `max_path` characters |
| B003 | warning | a file **not inside any directory named `versions`** whose stem (name without the last extension) ends in a copy/version marker: matches, case-insensitively, `(?:[ _\-.]\(?\|\()(?:v\d+\|final\|new\|old\|copy\|backup)\)?$`, or `\s\(\d+\)$`, or ` - copy(?: \(\d+\))?$` |
| B004 | info | inside a `versions` directory, 2 or more files with the same document key. Key = the stem with 1 trailing ` (…)` group removed, plus the extension. 1 finding per key, on the first path in sorted order |
| B005 | warning | junk. A directory named `__pycache__`, `.pytest_cache`, `.benchmarks`, `.ipynb_checkpoints`, `.venv`, `venv` or `node_modules` (reported once; not descended into). A file matching `*.pyc`, `*.tmp`, `~$*`, `.~lock.*#`, `Thumbs.db`, `desktop.ini`, `.DS_Store` or `._*` |
| B006 | error | a file directly inside `setup/<dir>/` (any direct subdirectory of `setup/`) that is not listed in that directory's `README.md` table. `README.md` and `SOURCE.md` are exempt. A direct subdirectory `setup/<dir>/<sub>/` must be listed too, as `` `<sub>/` `` or `` `<sub>` ``. If `README.md` is missing, every entry is a B006 finding |
| B007 | error | a `setup/<dir>/README.md` table row that names an entry that doesn't exist |
| B008 | warning | a top-level directory without `README.md`. Exempt: hidden directories (name starts with `.`), `tools`, and junk directories (B005) |
| B009 | warning | `X.pdf` next to `X.docx` or `X.pptx` (same directory, same stem) with an older modification time than that source |
| B010 | error | `VERSION` missing or malformed; `CHANGELOG.md` missing or without the marker; or the first `## ` heading after the marker doesn't start with `## {VERSION}` (skipped when there are no entries and VERSION ends in `.0`) |
| B011 | info | a file larger than `large_mb` MiB; the message contains the size in MiB |
| B012 | error | a `SOURCE.md` checksum mismatch (see §2.8 `verify`) |
| B013 | warning | a `SOURCE.md` whose hash or target file can't be determined (see §2.8) |

**Table listing (B006/B007).** A table row is a line starting with `|`, excluding the header row and the `|---|`
separator row. Its first cell is parsed for backtick spans, and each span's content, trimmed, is an entry name.
A name ending in `/` names a directory. A row whose first cell has no backtick span is ignored.

### 2.8 `bundle_verify` / `tundlekit bundle verify`

Checks every `SOURCE.md` under root, skipping `.git`.
- The hash is the value of the first line matching `^\s*-\s*SHA-256:\s*` followed by 64 hex characters. Backticks
  around it are allowed, and the comparison ignores case. If there is no such line, or the value is not 64 hex
  characters (for example `<hash>`): B013, "no hash recorded".
- The target file is the value of a `- File:` line (relative to the SOURCE.md directory; backticks allowed) if one
  exists. Otherwise it is the only regular file in the same directory other than `README.md` and `SOURCE.md`.
  If there are none or several: B013, "cannot tell which file". A `- File:` that doesn't exist: B013.
- Mismatch: B012 with expected and actual in the message.

Result: checker shape plus `"checked": [{"source", "file", "expected", "actual", "match"}]` for every SOURCE.md where
both hash and file were found (`source` and `file` relative to root).

### 2.9 Human-readable output (without `--json`)

Tests may check these substrings:
- status: lines starting `version:  `, `history:  ` (only when commits exist), `size:     `, and either
  `changes:  none` or `changes:  {n} unreleased`.
- release: `released {new} ({stats_text})`. When `prune_hint`, also a line containing `prune`.
- compare: `same version: {v}`, `this copy is newer: {mine} > {theirs}`, or `the other copy is newer: {theirs} > {mine}`.
- prune: `nothing to clear`, `dry run`, or `cleared: {keep} versions kept`.
- lint/verify: 1 line per finding, `{path}:{line or 0}: {rule} {severity}: {message}`, then a summary line.

---

## 3. deck: presentations from a JSON spec (after `deckkit.py`)

Needs the `office` extra (python-pptx, Pillow). `deck_lint` on a **spec** needs nothing optional.

### 3.1 Spec

A deck spec is a JSON object, passed either as `spec` (an object) or as `spec_path` (a `.json` file). Exactly 1 of the
2 is required; otherwise `ToolError`. Relative paths inside a spec resolve against the spec file's directory, or the
current directory when `spec` is given inline.

```json
{
  "meta": {"id": "capsule", "title": "…", "logo": "logo.png", "inserts": "shown",
           "budget": {"target": "40:00", "max": "45:00"}, "words_per_second": 2.3},
  "slides": [
    {"type": "title", "title": "…", "subtitle": "…", "byline": "…", "notes": {"time": "0:15", "say": "…"}},
    {"type": "divider", "title": "The evidence", "subtitle": "…", "notes": {"time": "0:05"}},
    {"type": "content", "eyebrow": "Research", "title": "96.8% of kept tools fail held-out tests",
     "stage": "gates", "source": "Beyond Task Completion, Table 4", "insert": false,
     "demonstrated_by": {"paper": "Beyond Task Completion (arXiv 2604.00392)", "setup": "99 tasks, 222 kept tools"},
     "phase": {"in": "goal text", "out": "frozen contract"},
     "body": {"kind": "bullets", "items": ["…"]},
     "thus": "…",
     "notes": {"time": "0:45", "say": "…", "asked": ["Why cap tries: …"]}}
  ]
}
```

- `meta` is optional, and every meta field is optional. `inserts` ∈ `shown | hidden | off` (default `shown`).
  `budget` defaults to target `40:00`, max `45:00`. `words_per_second` defaults to 2.3.
- `type` ∈ `title | divider | content`, default `content`.
- `stage` (content only, optional) is a key of `palette.STAGE` (§6).
- `body.kind`:
  - `bullets`: `items` [str]
  - `lines`: `items` [str], optional `mono` bool
  - `table`: `rows` [[cell]] with at least 1 row, all rows the same length; optional `widths` [number], 1 per column
  - `figure`: `path` to an existing PNG/JPEG
  - `excerpt`: `text` str; optional `caption`
  - `chart`: `categories` [str], `values` [number], optional `highlight` (index or category), `unit`, `takeaway`
- `notes.time` is `M:SS` (1+ digit minutes, exactly 2 digit seconds < 60) and required on every slide. `say` is
  optional (default empty). `asked` is optional.
- `insert: true` is allowed only on content slides that come after at least 1 core content, title or divider slide.

**Validation.** Every problem is collected, then 1 `ToolError` is raised whose message lists each problem with a
JSON-path prefix such as `slides[3].notes.time:`. Unknown `type`, `stage` or `body.kind`; a missing `title` on
content/divider/title slides; a missing figure file; table rows of unequal length; `widths` of the wrong length;
chart categories and values of different lengths; a bad `inserts` value; and a bad time format are all problems.

### 3.1a Pinned details

- Insert letters restart after **every** core slide, including title and divider slides.
- "Over" means strictly greater: a total equal to the target is `ok`; equal to the max is `over target`.
- A partial `meta.budget` falls back to the default for each missing key.
- `insert: true` on a title or divider slide is a validation problem.
- `meta.logo` is used when the file exists; a missing logo file is ignored.
- `say_words` is 0 for a slide without SAY. `svg` is absent or null in chart results when `out` is given.
- With inserts `off`, `insert_seconds` is still the sum of the insert slides' times, and `total_time` is `core_time`.

### 3.2 `deck_build` / `tundlekit deck build SPEC.json -o OUT.pptx [--inserts MODE] [--times-file PATH]`

Arguments: `spec` | `spec_path`, `out` (required), `inserts` (overrides meta), `times_file`.

The built deck:
- slide size 13.333 × 7.5 inches; blank layout; 1 PowerPoint slide per spec slide (minus `off` inserts).
- **content slide**: an eyebrow text box in upper case; the title text box, exactly the title; a rule under the title;
  the source footer (if given); the slide number box, whose text is exactly the number; the body; the strips; the
  logo (if `meta.logo` exists). With `demonstrated_by`, a strip whose text is
  `DEMONSTRATED BY   {paper}  ·  {setup}`. With `thus`, a strip whose text is `THUS   {thus}`. With `phase`, a strip
  whose text is `IN   {in}        OUT   {out}`.
- **numbering**: core content slides are numbered 1, 2, 3… in order; title and divider slides also advance the core
  counter but show no number. An insert slide after core slide n is numbered `n` + `a`, `b`, … (the letter restarts
  after each core slide).
- **bullets** are paragraphs `•  {item}`; **table** is a native table whose cell text equals the spec cells
  (`str(cell)`), with the first row as header; **figure** is a picture scaled to fit 11.8 × 5.3 in, keeping aspect ratio;
  **excerpt** is a shape whose text frame holds the excerpt lines in a monospace font; **chart** is a native
  PowerPoint bar chart with 1 series, the given categories and values, data labels on, the highlighted point in a stage
  colour and the other points grey, and the takeaway (if any) as bold text beneath.
- **title slide**: title, subtitle and byline text boxes; **divider**: dark background, `title` and `subtitle` text boxes.
- **notes** (every slide): the lines below joined with `\n`, where optional parts are omitted when empty:
  ```
  INSERT: optional slide; delete or hide it and the talk flows unchanged     (insert slides only)
  TIME {time}
  SAY: {say}
  IF ASKED:
  - {asked[0]}
  - …
  ```
- **inserts mode**: `shown`, inserts are normal slides; `hidden`, insert slides have `show="0"` on their `p:sld`
  element; `off`, insert slides are absent from the file.

Result:

```json
{"out": "...", "core_slides": 10, "insert_slides": 2, "inserts": "shown",
 "core_seconds": 600, "insert_seconds": 90, "core_time": "10:00", "total_time": "11:30",
 "budget": {"target": "40:00", "max": "45:00", "status": "ok"},
 "ledger": null,
 "warnings": ["slide 3: ..."],
 "slides": [{"number": "1", "type": "title", "title": "...", "insert": false, "seconds": 15, "say_words": 12}]}
```

- `core_slides` counts non-insert spec slides of any type. `insert_slides` counts insert spec slides, even when
  `off`. `slides` lists every spec slide in spec order. `number` is `null` for title and divider slides.
- Times are formatted `M:SS` (minutes unpadded). `budget.status` is `ok`, `over target` or `OVER BUDGET`, from
  `core_seconds`.
- `times_file`: a JSON object file `{deck_id: seconds, deck_id + "_inserts": seconds}` shared by several decks.
  Build writes `meta.id` (required when `times_file` is given, else `ToolError`), creating the file if needed.
  `ledger` = `{"path", "decks": {id: seconds}, "combined_seconds", "combined_time", "status"}`, where
  `combined_seconds` sums the non-`_inserts` entries and `status` compares that sum to the budget. With inserts `off`,
  the `_inserts` entry is written as 0.
- **warnings**: each string starts with `slide {number or position}: `. Build warns when estimated text height
  exceeds its box (the deckkit heuristic: characters per line = `(width_in - 0.1) * 72 / (size_pt * k)` with k=0.5,
  or 0.6 for monospace; each line is `size*1.2/72` in tall), when a table is estimated to run past the slide bottom,
  when a strip's text is too long for 1 line, and when the core time exceeds the budget max. A spec whose single
  bullet is 2,000 characters long must produce at least 1 warning; a spec with 3 short bullets must produce none.
- The output file's parent directory must exist, otherwise `ToolError`. An existing `out` is overwritten.

### 3.3 `deck_lint` / `tundlekit deck lint (SPEC.json | DECK.pptx)`

Arguments: `spec` | `spec_path` | `pptx_path` (exactly 1), `words_per_second` (default: meta, else 2.3),
`target`, `max` (M:SS; default: meta budget, else 40:00/45:00).

For a `.pptx`: a slide is **content** if some text frame's whole text matches `^\d+[a-z]?$` (its number); it is an
**insert** if its notes start with `INSERT:`; its **title** is the text of the text frame containing the run with the
largest font size (the first such frame in shape order); `TIME` and `SAY` are parsed from the notes format above
(`SAY:` runs to the next line starting with `IF ASKED:` or `MUST HIT:`, or to the end).

"Words" = whitespace-separated tokens. "Face text" = all text on the slide (for a spec: title, eyebrow, subtitle,
byline, body text, strips, table cells, takeaway).

| Rule | Severity | Finding |
|---|---|---|
| D001 | error | SAY words > seconds × words_per_second |
| D002 | warning | a core content slide with fewer than 20 SAY words |
| D003 | error | a title containing an em dash `—` |
| D004 | error | notes containing `MUST HIT` or `The point of this slide` |
| D005 | warning | SAY containing, case-insensitively, `I'm not going to`, `I am not going to`, `I'm not claiming`, `I'll show`, `I will show`, `this talk will` or `that's fine for` (straight or curly apostrophe) |
| D006 | error | an insert slide whose face text or SAY matches `(?i)\b(as we saw\|as i said\|as mentioned\|next slide\|coming up)\b` |
| D007 | error | a non-insert slide whose face text or SAY mentions an insert slide by number, `(?i)\bslide\s+\d+[a-z]\b` |
| D008 | error / warning | core total over max (error); over target (warning). `line` null, `path` the deck |
| D009 | warning | a content slide with no source footer (spec: no `source`; pptx: not checked) |
| D010 | warning | face text containing `et al.` or matching `\bEq\.?\s*\d` |
| D011 | warning | a title longer than 90 characters |
| D012 | error | a slide without a TIME (pptx) |

For findings, `path` is the spec/pptx path (or `<spec>` for inline specs) and `line` is the 1-based slide position in
the file (spec order). The result is the checker shape plus
`{"core_seconds", "insert_seconds", "core_time", "slides": n}`.

### 3.4 `deck_inspect` / `tundlekit deck inspect DECK.pptx`

Argument: `pptx_path` (required).

Works on any `.pptx`. Result `{"path", "slides": [{"index", "number", "title", "texts", "notes", "seconds",
"say_words", "insert", "hidden"}]}`. `index` is 1-based. `texts` is every text frame's text in shape order (table cells
row by row, after the frames). `number` is the matched slide-number text or `null`. `seconds` is `null` without
TIME. `hidden` is true when the slide has `show="0"`.

---

## 4. diagram: SVG diagrams (after `figures.py` and `palette.py`)

Standard library only. Rules carried over: **colour = stage, style = actor, 1 box per model call, a legend whenever
more than 1 actor is shown, nothing depends on colour alone**.

### 4.1 Spec

```json
{"title": "Capsule build path", "direction": "LR",
 "nodes": [{"id": "decide", "label": "build decision", "sub": "reads gap records", "stage": "build", "actor": "model"},
           {"id": "gate", "label": "admission gate", "stage": "gates", "actor": "code", "dashed": false},
           {"id": "lib", "label": "library\nappend-only · versioned", "stage": "library", "actor": "record"}],
 "edges": [{"from": "decide", "to": "gate", "label": "manifest", "dashed": false}],
 "groups": [{"id": "cold", "label": "cold path", "nodes": ["decide", "gate"], "stage": "build"}],
 "legend": "auto", "tags": true, "note": "(illustrative)"}
```

- `id` matches `^[A-Za-z_][A-Za-z0-9_-]*$` and is unique across nodes and groups.
- `label` is a non-empty string; `\n` makes multiple lines.
- `stage` is a `palette.STAGE` key (default `dispatch`). `actor` ∈ `model | code | record | external` (default `code`).
- `direction` ∈ `LR | TB` (default `LR`).
- `legend` ∈ `auto | true | false` (JSON `true`/`false` or the string `"auto"`; default `auto`).
- Edges reference existing node ids. Self-loops are a validation problem. Duplicate edges are allowed.
- Groups reference existing node ids; a node may belong to at most 1 group.
- Validation collects every problem into 1 `ToolError` with JSON-path prefixes (`nodes[2].stage: ...`).

### 4.2 `diagram_render` / `tundlekit diagram render SPEC.json [-o OUT.svg] [--png OUT.png]`

Arguments: `spec` | `spec_path` | `mermaid` (Mermaid text, §4.4) | `mermaid_path` (exactly 1), `out` (optional .svg
path), `png` (optional .png path).

Result `{"svg": <text, only when out is absent>, "path": <out or null>, "png": <path or null>, "width", "height",
"nodes": {id: {"x", "y", "w", "h", "rank"}}, "warnings": [...]}`. `x`, `y` are the **top-left** corner of the node box in SVG user units. `svg` may be absent or `null` when `out` is given.

SVG requirements:
- Well-formed XML; root `<svg xmlns="http://www.w3.org/2000/svg" width="W" height="H" viewBox="0 0 W H">` with W and H
  equal to the result's width and height. When `title` is given, the first child is `<title>` with that text.
- Each node is `<g class="node actor-{actor} stage-{stage}" data-id="{id}">` holding its shape and 1 or more `<text>`
  elements. Every line of the label appears as the text content of a `<text>` or `<tspan>`, and `sub` likewise.
  Text is XML-escaped.
- Shape colours: `model`, fill `palette.tint(STAGE[stage], 0.20)` and stroke `STAGE[stage]`; `code`, fill `#ffffff`
  and stroke `STAGE[stage]`; `record`, a `<path>` with a folded corner, fill `#ffffff`, stroke `STAGE[stage]`;
  `external`, fill `#f6f6f6` and stroke `#4d4d4d`. Colours are written as lower-case `#rrggbb`. `dashed` nodes have a
  `stroke-dasharray`.
- With `tags` false, no node has a `class="tag"` text. With `tags` true (default), every model node contains a `<text class="tag">MODEL</text>` and every code node a
  `<text class="tag">CODE</text>`. Record and external nodes have no tag.
- Each edge is `<g class="edge" data-from="{from}" data-to="{to}">` holding a `<path>` with `marker-end` referencing
  an arrow marker defined in `<defs>`. Dashed edges have `stroke-dasharray`. A label becomes a `<text>` inside the group.
- Each group is `<g class="group" data-id="{id}">` holding a dashed rectangle drawn **before** (under) the nodes,
  plus a `<text>` label. The rectangle contains every member node's box.
- Legend: shown when `legend` is true, or `auto` with 2+ distinct actors among nodes. `<g class="legend">` holds 1 entry
  per actor present, with the texts `MODEL call`, `CODE (deterministic)`, `record`, `external`. When a model node is
  present, it also holds the text `1 box = 1 model session`. It is inside the canvas and doesn't overlap any node.
- `note` becomes `<text class="note">` inside the canvas.
- `font-family` includes `sans-serif`.

Layout:
- Back edges are found by depth-first search from nodes in spec order, and ignored for ranking.
- `rank` = the longest path length from a source over the remaining edges (sources have rank 0).
- `LR`: x increases strictly with rank (every node of rank r+1 lies right of every node of rank r); `TB`: y does.
- No 2 node boxes overlap. All boxes, the legend, labels and the note lie inside `0..width × 0..height`.
- Nodes in the same rank keep spec order along the cross axis, unless the implementation reduces crossings
  (a barycentre pass is allowed). The layout is deterministic: the same spec gives byte-identical SVG.
- A box's width grows with its longest label line. A 40-character label gives a wider box than a 4-character one.
  Lines are never truncated.

PNG: when `png` is given, convert with the first available of the Python module `cairosvg`, the `rsvg-convert`
executable, or `inkscape`. If none is available: `ToolError` containing `no SVG to PNG converter`, and no `.png` file is left behind. The SVG is still
written when `out` is given.

### 4.3 `diagram_validate` / `tundlekit diagram validate SPEC.json`

Returns `{"ok": bool, "problems": [str]}` without raising for spec problems. Also accepts `mermaid`/`mermaid_path`.

### 4.4 Mermaid subset: `diagram_from_mermaid`, `diagram_to_mermaid`

`diagram_from_mermaid(mermaid | mermaid_path)` → `{"spec": <diagram spec>, "warnings": [...]}`.
`diagram_to_mermaid(spec | spec_path)` → `{"mermaid": <text>}`.
CLI: `tundlekit diagram from-mermaid FILE.mmd`, `tundlekit diagram to-mermaid SPEC.json`.

Accepted input:
- First non-blank, non-comment line: `flowchart` or `graph`, then a direction `LR | RL | TB | TD | BT`. `TD` and `BT`
  map to `TB`, and `RL` maps to `LR`. A missing direction means `TB`.
- `%%` comment lines are ignored. Blank lines are ignored.
- **Node shapes → actor**: `id[label]` → code; `id(label)` → model; `id>label]` → record; `id[(label)]` → record;
  `id{{label}}` → external. Labels may be wrapped in double quotes, which are removed. `<br>`, `<br/>` and `<br />` in
  labels become `\n`.
- A bare `id` refers to an existing node, or creates a code node labelled with the id.
- `:::name` after a node sets its stage when `name` is a `palette.STAGE` key. Otherwise it adds a warning and keeps
  the default stage.
- **Edges**: `-->`, `---`, `==>`, `-.->` (dashed), `-.-` (dashed); labels as `-->|text|`, `-.->|text|` or
  `-- text -->`. Chains `A --> B --> C` give 2 edges. `A & B --> C` gives 2 edges.
- `subgraph id [label]` or `subgraph id` … `end` → a group whose members are the nodes first defined or referenced
  inside it (and not already in another group).
- `classDef`, `class`, `style`, `linkStyle` and `click` lines are ignored with 1 warning each.
- Any other line: `ToolError` containing `line {n}`, where n counts physical lines of the input (blank and comment lines included), starting at 1.
- Node ids must match the §4.1 id pattern (ASCII only); anything else is an error.
- The spec's node order is the order of first appearance.

`to_mermaid` output starts with `flowchart {direction}` and uses the shapes above, `:::{stage}` on every node, `-.->`
for dashed edges and `|label|` for labels. `from_mermaid(to_mermaid(spec))` gives back the same nodes (id, label,
stage, actor), edges (from, to, label, dashed), groups and direction. `sub` is folded into the label as a second
line, which is the only allowed loss.

---

## 5. chart: bar charts as SVG

`chart_bar` / `tundlekit chart bar SPEC.json [-o OUT.svg]`. Arguments: `spec` | `spec_path`, `out`.

Spec: `{"title"?, "categories": [str], "values": [number], "n"?: [int], "highlight"?: int | str,
"unit"?: str (default ""), "takeaway"?: str, "orientation"?: "horizontal" | "vertical" (default horizontal),
"max"?: number, "decimals"?: int, "stage"?: STAGE key (default "gates")}`.

- Validation (1 `ToolError` listing problems): categories non-empty; the same length as values (and as `n`, when
  given); values finite and ≥ 0 (a negative value gives the message `negative values are not supported`); a highlight
  index in range, or a highlight string that is one of the categories; `max` ≥ every value when given; stage valid.
- Axis maximum = `max` if given, else the largest value, or 1 when all values are 0.
- Each bar is `<rect class="bar" data-label="{category}" data-value="{value}">`. The highlighted bar has class
  `bar highlight` and fill `STAGE[stage]`; other bars have fill `#9a9a9a`. Bar length (width when horizontal, height
  when vertical) is proportional to value / axis maximum, to within 0.5 px. A value of 0 has length 0.
- Each bar has a `<text class="value">` data label: the value formatted with `decimals` places (default 0 when every
  value is an integer, else 1), followed by `unit`.
- Category labels appear as text. With `n`, the label is `{category} (n={n})`.
- `takeaway` is `<text class="takeaway" font-weight="bold">`. `title` is `<title>` and a visible heading.
- Result `{"svg" (when no out), "path", "width", "height", "bars": [{"label", "value", "length", "highlight"}]}`.

---

## 6. palette

`tundlekit.palette` exposes `INK`, `GREY`, `HAIR`, `PALE`, `STAGE`, `OUTCOME` and `PPT` with the same values as
tundle's `palette.py`:

```
INK "#000000"  GREY "#4d4d4d"  HAIR "#9a9a9a"  PALE "#ececec"
STAGE intent #0072B2, binding #2A8FA8, freeze #7B3FA0, dispatch #D98200, gates #008A63,
      claims #B8527F, build #3D4FB0, library #8C5A2B, external #6b6b6b
OUTCOME passed #008A63, failed #D55E00, skipped #bdbdbd, running #D98200, ready #0072B2, pending #ffffff
PPT = STAGE values without "#", upper-case
```

`tint(hexcolor, amount=0.18)` mixes with white: each channel becomes `round(255 - (255 - c) * amount)`, and the
result is a lower-case `#rrggbb`. It accepts input with or without `#`. Invalid input raises `ValueError`.

Tool `palette_get` / `tundlekit palette show` → `{"stage": STAGE, "outcome": OUTCOME, "ink": INK, "grey": GREY,
"hair": HAIR, "pale": PALE, "rules": [str, ...]}`, where `rules` states colour = stage, style = actor, 1 box per model
call, legend, and no reliance on colour alone.

---

## 7. textlint: report prose and numbering checks (after the style card and `checks/`)

Standard library only.

### 7.1 `text_lint` / `tundlekit text lint PATH... [--rules S001,S002] [--ignore S003] [--max-words N]`

Arguments: `paths` [str] (files; directories are walked for `*.md` and `*.txt`), `rules` [str] (default all),
`ignore` [str], `max_words` (default 42). Unknown rule ids: `ToolError`. Missing path: `ToolError`.

**Masking.** Before any rule runs, these are replaced by spaces (so columns keep their positions) and never produce
findings: fenced code blocks (``` or ~~~, including the fence lines), inline code spans, HTML comments, URLs
(`http://`, `https://`), and the `(target)` part of Markdown links and images. YAML front matter (a `---` block at
line 1) is masked too.

**Suppression.** `<!-- lint-ignore S003 S005 -->` suppresses the listed rules on its own line and on the next line.
`<!-- lint-ignore -->` with no ids suppresses every rule on those lines.

**Structure.** A heading is a line starting with 1–6 `#` and a space. Prose is every line that is not masked, not a
heading, not a table separator row, and not blank. List items are prose.

| Rule | Severity | Finding |
|---|---|---|
| S001 | error | an em dash `—` (headings included) |
| S002 | error | first person in prose or headings: the whole words `we`, `our`, `ours` (any case), `us` (not all-caps `US`), or `I` followed by a space and a lower-case letter |
| S003 | warning | hedges, whole words: `arguably`, `seems`, `seem`, `seemingly`, `perhaps`, `somewhat`, `possibly`, `might`, lower-case `may`, and the phrases `to some extent`, `it appears` (case-insensitive except for `may`) |
| S004 | error | contractions with `'` or `’`: a word ending in `n't`, `'re`, `'ve`, `'ll`, `'d` or `'m`, and the words `it's`, `that's`, `there's`, `what's`, `here's`, `let's`, `who's` (case-insensitive) |
| S005 | warning | a semicolon in prose |
| S006 | error | status markers or placeholders: `⚠`, `[verified]`, `[proposed]`, `[doc]`, `[repo-claim]`, `[TODO`, `[TBD`, `[footnote`, `TODO:`, `XXX` (bracketed ones case-insensitive) |
| S007 | warning | a question in prose: a prose line (not a heading) where a `?` ends a sentence, i.e. is followed by whitespace, end of line, or a closing quote/bracket |
| S008 | error | `et al.` outside an exempt section. A heading whose text (after the `#`s) matches `(?i)^(references\|bibliography\|appendix a\b)` starts an exempt section. The section ends at the next heading of the same or a higher level (the same or fewer `#`s) |
| S009 | warning | a sentence longer than `max_words` words |
| S010 | warning | a section whose first prose sentence starts with `This section`, `In this section`, `Here we` or `This chapter` (case-insensitive) |
| S011 | warning | jargon: `\bEq\.?\s*\(?\d` or `\bpp\b` (the abbreviation, not `pp.` page ranges followed by a digit) |

**Sentences.** Prose is split into sentences per paragraph (consecutive prose lines that are not list items form 1
paragraph; each list item is its own paragraph). A sentence ends at `.`, `!` or `?` followed by whitespace or the end,
except after the abbreviations `e.g.`, `i.e.`, `et al.`, `vs.`, `Fig.`, `Eq.`, `No.`, `approx.`, `cf.` and a decimal
point between digits. A finding for a sentence is reported on the line where the sentence starts.

Result: checker shape plus `"stats": {path: {"sentences", "words", "mean_sentence_words", "max_sentence_words",
"list_items"}}`. `mean_sentence_words` is rounded to 1 decimal place and is 0 with no sentences. The stats cover prose
sentences, list items included.

Excerpts show the matched text (at most 80 characters of context).

### 7.2 `text_fignums` / `tundlekit text fignums REPORT.md... [--refs FILE...]`

Arguments: `paths` [str], `refs` [str] (other files whose mentions must resolve against the reports).

- **Captions**: a line (stripped) starting `![Fig. {P}{N}.`, `*Fig. {P}{N}.`, `**Fig. {P}{N}.` or `Fig. {P}{N}.`, and
  for tables `*Table {P}{N}.`, `**Table {P}{N}.` or `Table {P}{N}.`, where P is an optional upper-case letter prefix
  and N an integer. Figures and tables, and each prefix, are numbered independently per file.
- F001 error: a caption number that is duplicated (reported on the 2nd and later occurrences).
- F002 error: a gap in a numbering sequence (reported once per gap, `line` null).
- F003 error: a numbering sequence that doesn't start at 1.
- F004 error: captions out of ascending order (once per sequence).
- F005 error: a mention `Fig. {P}{N}` or `Table {P}{N}` in a non-caption line of a report, or anywhere in a `refs`
  file, that doesn't match a caption in any of the `paths` files. A mention preceded within the same line by `arXiv`,
  or by the whole word `paper` (so `newspaper` does not count), is skipped (it points into a cited paper).
- Result: checker shape plus `"captions": {path: {"Fig": {prefix: [numbers]}, "Table": {...}}}`, where the prefix key
  for no prefix is `""`. Every file in `paths` has an entry, and both `"Fig"` and `"Table"` keys are always present (possibly `{}`).

### 7.3 `text_wordcount` / `tundlekit text wordcount PATH... [--baseline GITREF]`

Sections start at headings of level 1–3. Words are whitespace tokens of the section body (heading line excluded).
A leading section without a heading is named `(front matter)` and is omitted when it has 0 words.
Result `{"files": {path: {"sections": [{"heading", "words", "delta"}], "total", "total_delta"}}}`. `heading` is the
stripped heading line. With `baseline`, `git show {ref}:{path relative to the repo root}` is read from the file's git
repository: `delta` is the difference for a heading also present in the baseline, the string `"new"` otherwise, and
`total_delta` is the total difference. Without a baseline, or if the file isn't in the ref, `delta` and `total_delta`
are `null`.

---

## 8. render: pages, slides and contact sheets (after `render.py`)

Argument names (tool schemas): `render_pdf(pdf, out_dir, dpi, first, last)`; `render_contact_sheet(images, out_dir, cols, rows, thumb_width)`; `render_office(src, out_dir, backend)`; `render_backends()`. In the CLI, `-o` is `out_dir`.

### 8.1 `render_pdf` / `tundlekit render pdf FILE.pdf -o DIR [--dpi 110] [--first N] [--last M]`

Needs pymupdf. Writes `page-001.png`, `page-002.png`, … (3-digit, numbered by page number) into `out_dir`, creating it
if needed. Result `{"pages": <pages in the PDF>, "files": [paths rendered]}`. `first`/`last` are 1-based and inclusive.
A non-PDF or missing file gives `ToolError`.

### 8.2 `render_contact_sheet` / `tundlekit render sheet IMAGE... -o DIR [--cols 4] [--rows 3] [--thumb-width 480]`

Needs Pillow. Images are taken in the given order, `cols × rows` per sheet, written as `contact-01.png`, `contact-02.png`, …
Each thumbnail keeps its aspect ratio at `thumb_width` wide (no upscaling beyond the original width). It is labelled
with the number at the end of the file stem, leading zeros stripped (`slide-07` → `7`, `page-000` → `0`), or the whole
stem if it doesn't end in digits. Sheet width = `cols * (thumb_width + 14) + 14`. Result `{"sheets": [paths]}`. No
images: `ToolError`.

### 8.3 `render_office` / `tundlekit render office FILE.(pptx|docx) -o DIR [--backend auto|powerpoint|libreoffice|text]`

- Refuses (`ToolError` containing `refusing`) when `out_dir` is a filesystem root, the user's home directory, the
  directory containing the source, an ancestor of the source, or a directory containing `.git`. It never opens or
  modifies the source: the source is copied to `out_dir/src.<ext>` and only the copy is used.
- `out_dir` is created if missing, and its existing contents are removed first (so stale renders never survive), **but only when it is safe to empty** (§13.2). It must not exist yet, be empty, or contain the marker file `.tundlekit-render`, which every render writes into its `out_dir`. Otherwise: `ToolError` containing `refusing`.
- Backend `powerpoint` (Windows, pywin32, Office installed): before starting, `tundlekit.render.office_running()`
  (a function returning a list of running `POWERPNT.EXE`/`WINWORD.EXE` names) is checked. If it is non-empty:
  `ToolError` containing `refusing` and the process name. `.pptx` exports `slide-NN.png` at 1600 × 900; `.docx`
  exports a PDF, then pages as in §8.1.
- Backend `libreoffice`: the executable is `TUNDLEKIT_SOFFICE` if set, else `soffice`/`libreoffice` on PATH, else
  standard install locations. It converts to PDF headless, then renders pages (`slide-NN.png` for decks,
  `page-NNN.png` for documents).
- Backend `text` (always available, stdlib only for `.docx`; `.pptx` needs python-pptx): `.pptx` writes
  `slide-NN.txt` (the first line `TITLE: <first text frame>`, then the other frames separated by blank lines)
  and `notes-NN.txt`; `.docx` writes `paragraphs.txt`, 1 line per paragraph `[<style id or Normal>] <text>`, read
  from `word/document.xml` with `zipfile`.
- `auto`: `powerpoint` if available, else `libreoffice` if available, else `text`. A named backend that is unavailable
  raises `ToolError` containing `not available`.
- For decks, rendered with any backend, `notes-NN.txt` is written from python-pptx when it is installed.
- After a PNG render, contact sheets are made (§8.2) when Pillow is installed.
- Result `{"backend", "kind": "slides" | "pages" | "text", "count", "files", "sheets", "warnings"}`.
  `warnings` includes `"{k} render(s) under 10 KB"` when any PNG is smaller than 10,240 bytes.
- Unsupported extension: `ToolError` containing `unsupported`.

### 8.4 `render_backends` / `tundlekit render backends`

→ `{"powerpoint": bool, "libreoffice": str | null (path), "pymupdf": bool, "pillow": bool, "pptx": bool,
"svg_to_png": str | null}`.

---

## 9. papers: arXiv papers for reading (after `papers/fetch.py`, `body.py`, `peek.py`)

`dir` argument (default: current directory) holds `{id}.pdf` and `{id}.txt`. Old-style ids (`cs/0112017`) are stored
with `/` replaced by `_`.

**Id format**: `^\d{4}\.\d{4,5}(v\d+)?$` or `^[a-z-]+(\.[A-Z]{2})?/\d{7}(v\d+)?$`. Anything else is a per-id failure
`invalid arXiv id`.

**Text format** written by fetch: for each page N (1-based), `\n\n===== page {N} =====\n` followed by the page text.
Readers also accept pdftotext output (pages separated by form feeds `\f`; empty pages skipped, numbered by position).

Argument names: `papers_fetch(ids, dir, base_url, delay)` (`delay` is a number); `papers_body(id, dir, start, end, max_chars)`; `papers_peek(id, mode, dir, chars, pattern, context, max_hits)`; `papers_list(dir)`. Result ids are always reported in their original form (`cs/0112017`), `page` values are integers, and a missing text file raises `ToolError` in body and peek. For failed ids, `pdf` and `txt` are null.

### 9.1 `papers_fetch` / `tundlekit papers fetch ID... [--dir D] [--base-url URL] [--delay S]`

- Base URL: argument, else environment `TUNDLEKIT_ARXIV_BASE`, else `https://arxiv.org/pdf/`. The URL is
  `base.rstrip("/") + "/" + id`. The request sends a `User-Agent` header containing `tundlekit`.
- A PDF already present is not downloaded again (status `present`). A downloaded body that doesn't start with `%PDF-`
  is a failure (`not a PDF`), and nothing is left on disk for that id.
- `delay` seconds (default 3) are slept **between** actual downloads only (never before the first or after the last).
- Text extraction (when `{id}.txt` is missing): pymupdf if installed, else `pdftotext` on PATH, else the id status
  carries `"text": false` with a warning. The download is still kept.
- Errors for 1 id never stop the others.
- Result `{"results": [{"id", "status": "downloaded" | "present" | "failed", "pdf", "txt", "pages", "chars",
  "error"}], "ok": <no failures>}`. `pdf`/`txt` are paths or null. `pages` and `chars` describe the text file when it
  exists, else null. `error` is null unless failed.
- CLI exit code 1 if any id failed.

### 9.2 `papers_body` / `tundlekit papers body ID [--dir D] [--start N] [--end M] [--max-chars C]`

The references page is the first page N > 3 that has a line consisting only of `References`, `REFERENCES`,
`Bibliography` or `BIBLIOGRAPHY` (surrounding whitespace allowed). Default range: page 1 to the references page, if
one exists, else to the last page. Within each page, hyphenated line breaks before a lower-case letter are joined,
single newlines become spaces, and runs of spaces/tabs collapse to 1 space. Each page is emitted as `[p{N}] {text}` on
its own line. Result `{"id", "pages", "references_page", "start", "end", "text", "chars", "truncated"}`, where `text`
is cut to `max_chars` (default 90000). A missing text file: `ToolError` containing `fetch`.

### 9.3 `papers_peek` / `tundlekit papers abs ID [--chars N]` and `tundlekit papers grep ID REGEX [--context C] [--max-hits H]`

Arguments: `id`, `mode` (`abstract` | `grep`), `dir`, `chars` (default 2200), `pattern`, `context` (default 2),
`max_hits` (default 12).
- `abstract`: text from the first case-insensitive whole word `abstract` (or the start), `chars` long, with single
  newlines replaced by spaces. → `{"id", "abstract"}`.
- `grep`: case-insensitive regex over lines. → `{"id", "hits": [{"page", "line", "text"}], "truncated"}`. `line` is
  the 1-based line in the text file, `page` is the current page number (0 before the first marker), and `text` is
  lines `line-context … line+context` stripped and joined with 1 space. It stops after `max_hits`
  (`truncated` true if more existed). An invalid regex: `ToolError`.

### 9.4 `papers_list` / `tundlekit papers list [--dir D]`

→ `{"papers": [{"id", "pdf": bool, "txt": bool, "pages", "summary"}]}`, sorted by id. It covers every `*.pdf` or
`*.txt` whose stem is a valid id (old-style ids with `_`). `pages` is counted from the text file, else null.
`summary` is the path of `summaries/{id} - *.md` inside `dir` if one exists, else null.

---

## 10. translate: zh ↔ en translation checks (vendored `tcheck.py`)

`tundlekit/translate/tcheck.py` is tundle's `translate/checks/tcheck.py`, unchanged except that `DEFAULT_GLOSSARY`
points to `tundlekit/translate/data/glossary.tsv`. The rules, traps and prompts are in `tundlekit/translate/data/`
and `tundlekit/translate/prompts/`. The vendored unit tests live in `tests/test_tcheck_vendored.py` and must pass.

Argument names: `translate_check(mode, src, tgt, direction, domains, glossary, repair)`, `domains` a list of strings (CLI: `--domains` takes 1 or more values). `translate_resources(name)`. tcheck's own usage errors (SystemExit) are returned as `exit_code` 2, never raised.

Tool `translate_check` / `tundlekit translate check MODE SRC [TGT] [--dir zh-en|en-zh] [--domains D...] [--glossary PATH] [--repair OUT]`:
- `mode` ∈ `encoding | spans | glossary | glossary-slice | all`. `tgt` is required for `spans`, `glossary` and `all`
  (else `ToolError`). `direction` (default `zh-en`) is required by tcheck for `glossary`, `glossary-slice` and `all`.
  `domains` is an optional list. `glossary` is an optional TSV path. `repair` applies to `encoding` only.
- It runs `tcheck.main([...])` in-process, capturing stdout and stderr.
- Result `{"exit_code", "ok": exit_code == 0, "output": <stdout>, "errors": <stderr>}`. The CLI prints the output and
  returns the exit code.

Tool `translate_resources` / `tundlekit translate resources [--name NAME]`: without `name`,
`{"resources": [names]}` listing every file in `data/` and `prompts/` as `data/<file>` or `prompts/<file>`. With
`name`, `{"name", "text"}`. An unknown name gives `ToolError`.

---

## 11. Skills

Each skill is `skills/<name>/SKILL.md` in the open Agent Skills format:

```
---
name: <name>                  # equals the directory name; ^[a-z0-9]+(-[a-z0-9]+)*$; ≤ 64 chars
description: <≤ 1024 chars, says what it does AND when to use it>
---
<body: Markdown instructions, < 500 lines>
```

- Skills are agent-agnostic: no vendor-specific tool names (e.g. no `Bash(`, `Read(`, `mcp__`). They refer to the
  tools as CLI commands (`tundlekit …`) and name the equivalent MCP tool (`deck_build` …).
- Every `tundlekit <group> <command>` shown in a skill must be a real CLI command, and every MCP tool name mentioned
  (a `snake_case` word in backticks that starts with a registered tool's group prefix, e.g. `` `deck_build` ``) must
  be registered.
- Supporting files may sit next to SKILL.md (`references/*.md`); every relative link in SKILL.md must resolve.

Required skills:

| name | covers |
|---|---|
| `tundle-bundle` | keeping a tundle: the latest-only rule, status → release → compare → copy; history clearing (when, how, and what is approved or not approved to clear, from HISTORY-CLEANUP.md); lint and verify; setup tables and SOURCE.md |
| `deck-builder` | writing a deck spec and building it: the deck structure template, slide-writing rules, speaker-note rules (SAY / IF ASKED, no MUST HIT, no meta or defensive lines), the timing table and words budget, insertion slides, the deck↔report 1-argument rule, then `deck lint` |
| `diagram-maker` | diagrams by the stage/actor rules; the spec and the Mermaid subset; when to reproduce a paper's figure versus draw your own; charts via `chart bar` |
| `report-writing` | the style card voice and drafting rules, the claim → labelled limitations list pattern, the report rules and the deck element → report element mapping, `text lint`, `text fignums`, `text wordcount` |
| `deliverable-review` | the review procedure: build from the script, render, contact sheets, read slides alone, the adversarial pass over the flaw-class table, propagate fixes, record the review; the hard rules (Office closed, back up first, no markers in deliverables) |
| `paper-reading` | fetch, list, abs, grep, body; cite by title and arXiv id, never by nickname or author; trace every number to a page; the summary file format |
| `zh-en-translation` | tiers T0/T1/T2, the T2 pipeline with a separate translator and a fresh-context critic, the quoting convention, `translate check` modes; the rules and prompts via `translate resources` |
| `held-out-build-gate` | building a capability safely: a manifest first; a suite author who writes visible and held-out tests from the manifest alone; an implementer who never sees held-out tests; capped gate attempts that reveal only admit/reject plus a reason; an adversarial review when attempts run out |

---

## 12. Packaging and docs

- `pyproject.toml`: project `tundlekit`, version from `tundlekit.__version__` (static duplicate allowed),
  `requires-python >= 3.10`, no required dependencies, extras `office = ["python-pptx", "Pillow"]`,
  `pdf = ["pymupdf"]`, `all` = both, `dev` = all + pytest. Console scripts `tundlekit = tundlekit.cli:console`
  and `tundlekit-mcp = tundlekit.mcp_server:console` (`console()` calls `sys.exit(main())`). Package data includes
  `tundlekit/translate/data/*` and `tundlekit/translate/prompts/*`.
- `README.md`: what the kit is, install (`pip install -e .[all]`), the command overview, and where the skills are.
- `AGENTS.md`: how an agent uses the repo, with MCP configuration snippets for at least Claude Code (`.mcp.json`),
  Codex CLI (`config.toml` `[mcp_servers.tundlekit]`), Gemini CLI (`settings.json`) and a generic stdio client;
  how to install the skills (copy or link `skills/<name>` into the agent's skills directory); how to run the tests.
  Every CLI command in AGENTS.md and README.md must exist.
- `tests/` runs with `python -m pytest` from the repo root. Tests that need an optional package or an external program
  skip when it is missing.

---

## 13. Hardening (review round 1)

These rules come from an adversarial review of the first implementation. Where they are stricter than earlier
sections, this section wins.

### 13.1 bundle
- Every git subprocess runs with these variables removed from its environment: `GIT_DIR`, `GIT_WORK_TREE`,
  `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_COMMON_DIR`, `GIT_NAMESPACE`,
  `GIT_CEILING_DIRECTORIES`. With `GIT_DIR` pointing at another repository, release, prune and status still act
  only on `root`.
- `bundle_prune` with `yes` deletes **every** ref except `refs/heads/<current branch>`: tags, remotes, notes, stash,
  `refs/original`, the `ORIG_HEAD` and `FETCH_HEAD` files, and anything else. Afterwards no dropped commit is
  reachable or present.
- Rebuilt commits are byte-identical to the originals apart from their `parent` lines, including extra headers such
  as `encoding`. Write the raw object with `git hash-object -t commit -w --stdin`. A `gpgsig` header is dropped,
  because it would no longer be valid.
- `VERSION` digits are ASCII only (`[0-9]`). All id and version patterns use full matches, so a trailing newline
  never matches.
- `bundle_lint` and `bundle_status` never follow symlinks or Windows junctions/reparse points. A link counts as
  1 entry and is not descended into.
- `bundle_lint` and `bundle_verify` take `ignore` (a list of strings; CLI `--ignore`, repeatable). An entry `RULE`
  drops that rule everywhere. `RULE:GLOB` drops it for paths matching the glob (`fnmatch` on the relative
  `/`-separated path).
- A `SOURCE.md` target (`- File:`) that resolves outside root, is on another drive, or can't be read is a B013
  finding. It never raises, and nothing outside root is ever read.

### 13.2 render_office safety
- Refusal checks compare **real** locations, using `os.path.realpath`, `os.path.samefile` and `os.stat`
  (`st_dev`/`st_ino`). Admin-share paths (`\localhost\C$\...`), `\?\` paths, junctions, and case or `..` variants
  of a protected directory are all refused.
- Protected directories:
  - filesystem roots;
  - the home directory **and every ancestor of it**;
  - the current working directory and every ancestor of it;
  - the source's directory and every ancestor of it;
  - any directory containing `.git`.
- The emptying rule in §8.3 (the `.tundlekit-render` marker) applies on top of these.
- An `out_dir` string that isn't a valid path (for example one containing `|` or a NUL, or naming a device) gives
  `ToolError`.
- Links inside `out_dir` are removed as links. Their targets are never touched.

### 13.3 MCP server
- The server never exits on bad input.
- Responses are serialised with `ensure_ascii=True`, so lone surrogates survive as `\udXXX` escapes.
- Input that can't be parsed, for any reason (including `RecursionError` from deep nesting), gives `-32700`.
- Any exception while handling 1 message gives an error response (`-32603` for requests), and the server continues.

### 13.4 Validation never crashes
- Every spec field with a fixed type is type-checked first: strings such as `stage`, `actor`, `id`, `label`, `kind`,
  `direction` and `time`, plus numbers and lists. A wrong type is a listed validation problem, never a `TypeError`.
- Numbers must convert to finite floats, so `10**400` is a problem rather than an `OverflowError`.
- `notes.time` minutes have at most 3 digits.
- Text that will be written to SVG or PPTX may not contain control characters other than `\n` and `\t`. Deck, chart
  and diagram validation reports them as problems.
- More than 26 insert slides after 1 core slide is a validation problem.
- D001 compares with a tolerance: a finding only when `words > seconds * rate + 1e-9`.
- `deck_build` validates `times_file` before writing the deck: it must be a readable JSON object or absent, and its
  parent directory must exist.
- Spec files and times files may start with a UTF-8 BOM.
- `slide all: ` is the prefix for deck-level warnings, such as the budget warning.

### 13.5 Per-item failures stay per item
- `papers_fetch`: any exception while downloading or extracting 1 id, including `http.client` errors such as
  `IncompleteRead`, makes that id `failed`, and its partial files are removed. The other ids continue.
- Messages that native libraries print (for example MuPDF warnings) never reach stdout. With `--json`, stdout holds
  only the JSON.
- `translate_check` passes file arguments to tcheck in a way that works for names starting with `-`.

### 13.6 textlint and Mermaid
- A fenced code block indented under a list item (any indentation) is masked like any other fence.
- S006 also applies to headings.
- S010 uses the first sentence that has unmasked prose text, skipping masked-only lines and image-only lines.
- Mermaid ignored statements (`classDef`, `class`, `style`, `linkStyle`, `click`) are recognised only when the keyword
  is followed by whitespace, so `style-guide --> x` is an edge between nodes `style-guide` and `x`.
- `diagram_to_mermaid` raises `ToolError`, naming the id, when a node or group id is a Mermaid keyword (`end`,
  `subgraph`, `graph`, `flowchart`, `style`, `class`, `classDef`, `click`, `linkStyle`; case-insensitive) or contains
  `--`, `-.`, `==` or `&`.
- Labels may contain any text, including `\r`, which is written as a line break.
- Edge label text is kept exactly, including surrounding spaces.
- A group's `stage` round-trips through a `%% group <id> stage <stage>` comment line.

### 13.7 bundle_init
- See §2.6: an existing `CHANGELOG.md` is kept if it has the marker, and refused if it doesn't.

---

## 14. Usefulness fixes (review round 2: real tundle material)

A usefulness review ran every tool on the real reports, decks, papers and bundle. These rules fix the friction it found.
Where they conflict with earlier sections, this section wins.

### 14.1 text_lint
- **Tables.** S005, S007 and S009 skip table rows. Table rows count neither as sentences nor as list items in `stats`.
- **S003 `may`.** Lower-case `may` is a hedge only when the next word is `be`, `have`, `well`, `also`, `not`,
  `help`, `seem`, `lead` or `cause`. In "a server may use", `may` gives permission and is not flagged.
- **S007.** Prose under a heading whose text contains `question` (case-insensitive) is exempt, until a heading of the
  same or a higher level.
- **S011.** Text inside a citation bracket that starts with a number, such as `[2, Eq. (5)]` or `[3, pp. 4-5]`, is exempt.
- **File-wide suppression.** `<!-- lint-file-ignore S003 S009 -->` anywhere in a file suppresses those rules in the
  whole file; with no ids it suppresses nothing.
- **Band check.** New rule **S012** (info), 1 per file with `line` null: the file's mean prose sentence length
  (list items and table rows excluded) is outside `band`. The argument `band` is `[low, high]`, default `[15, 25]`;
  CLI `--band 15,25`. It needs at least 5 sentences.

### 14.2 text_wordcount
- `baseline_file` (CLI `--baseline-file PATH`) compares with another file, with the same delta rules as `baseline`.
  `baseline` and `baseline_file` are mutually exclusive, and giving both is a `ToolError`.
- **Buckets.** A level-2 heading whose text matches `(?i)^(references|bibliography)\b` starts the `references`
  bucket, and one matching `(?i)^appendix\b` starts `appendix`. Every other heading is in `body`, and deeper
  headings inherit their parent's bucket. Each file result gains `"buckets": {"body": n, "appendix": n,
  "references": n}`, and each section entry gains `"bucket"`.
- `tables` (bool, default true; CLI `--no-tables`): when false, table rows are left out of the counts.

### 14.3 text_fignums
- `refs` entries may be `FILE=REPORT`. Mentions in that refs file are then resolved against that report only
  (`REPORT` must also be in `paths`). A plain `FILE` resolves against all reports, as before.

### 14.4 deck_lint
- `pptx_path` may also be a list of paths (CLI: several positional paths). Each deck is linted, and findings carry
  their deck's path.
- `times_file` (CLI `--times-file`) with pptx input: each deck's core seconds is compared with the entry named by
  that deck's id. The id is the file stem, unless `ids` (a list, the same length as the paths) gives it.
  **D013** (error, `line` null) is reported when they differ. D008 then uses the **combined** core time of every
  non-`_inserts` id in the times file (the entries for decks given take their measured values).
- **D014** (warning): face text or SAY containing an em dash `—`, a double period that is not part of `...`, or
  2 spaces between a lower-case letter or `.,;:)` and a capital letter (mid-sentence). Titles are covered by D003,
  and D014 does not repeat them.
- D014's mid-sentence double space means exactly 2 spaces (3 or more is a deliberate gutter, as in the
  phase strip).
- D005 also matches `I'll go through`, `I'm going to show`, `I will go through`, and `Instead I'll`.
- **D009 for pptx.** A content slide has a footer when some text frame whose top is at or below 6.9 in holds
  non-empty text other than the slide number.

### 14.5 deck_build
- `body` may be a single block (as before) or a **list of blocks**. Each block may carry optional `x`, `y`, `w`,
  `h` (inches) and `size` (pt). Without positions, the blocks stack top to bottom in the body area, and the warning
  rules apply to each block.
- `highlight_color` defaults to the slide's `stage` when it has one, else `gates`.
- A new block kind, **`point`**: `{"kind": "point", "text": str}`, 1 bold line of 20 pt text.
- Chart blocks take `chart_type`, `bar` (default) or `line`, and `highlight_color`, a `palette.STAGE` key or an
  `OUTCOME` key (default `gates`).
- A figure block without an explicit `h` shrinks to fit between the lowest strip or block above it and the THUS
  strip (or 6.9 in), so it never runs past the body area.

### 14.6 diagram and chart
- A node may carry `rank` (an integer ≥ 0), which fixes its rank. Layout keeps the rank ordering invariant for the
  remaining nodes. Where an edge goes backward against fixed ranks, it is drawn as a back edge.
- `wrap` (integer ≥ 1, spec level): in `LR`, ranks are laid out in rows of at most `wrap` ranks. Row k+1 sits below
  row k, and x resets at each row. The rank-order invariant then applies within a row. In `TB` it wraps columns in
  the same way. Boxes still never overlap and stay inside the canvas.
- **PNG fallback.** When no other converter exists, pymupdf converts the SVG, if it is installed.
  `render_backends.svg_to_png` reports `pymupdf` in that case.
- `chart_bar`: `\n` in a category label makes separate lines (`<tspan>`). `axis: true` draws a value axis with
  gridlines and tick labels (`<g class="axis">`). `highlight_color` accepts `STAGE` or `OUTCOME` keys and
  overrides `stage` for the highlight.

### 14.7 papers
- `papers_body` gains `appendix` (bool, CLI `--appendix`): the default end becomes the last page.
- `papers_peek` grep gains `width` (int, CLI `--width`). When set, each hit's `text` is cut to at most `width`
  characters, centred on the first match.
- `papers_fetch` gains `reextract` (bool, CLI `--reextract`): the `.txt` is rewritten from the PDF even if it exists.
- **Layout text.** `papers_body` results and each `papers_list` entry carry `"layout_text": bool`. It is true when
  more than 20% of the non-blank lines contain a run of 5 or more spaces between 2 non-space characters, which is
  what `pdftotext -layout` output looks like. `papers_body` then adds a `"warnings"` entry suggesting `reextract`
  (the `warnings` list is always present).
- `papers_list` gains `"missing_summary": [ids]`.

### 14.8 bundle_lint
- **B005 and .gitignore.** A junk entry that git ignores (`git check-ignore`) is reported as `info`, not
  `warning`, with the message noting that the entry still travels with a copied folder.
- **New rule B014** (info, 1 finding, `line` null, path `setup`): the count of installer files under `setup/<dir>/`
  that have no `SOURCE.md` in their directory. A `<program>-<version>/` folder that has a SOURCE.md counts as
  covered. No finding when the count is 0 or there is no `setup/`.

### 14.9 render_office
- The text backend's `TITLE:` line uses the same title rule as `deck_inspect` (the largest font).

---

## 15. New tools (review round 2)

All of these are standard library only unless stated. The conventions of §0 apply.

### 15.1 `review_coverage` / `tundlekit review coverage REPORT.md DECK [--cuts FILE] [--threshold X]`

Checks that a report and its deck cover the same argument.

Arguments:
- `report` (path, required): a Markdown report.
- `deck` (path, required): a `.pptx` (needs python-pptx) or a deck spec `.json`.
- `cuts` (optional): a path to a text file of agreed cuts, 1 per line, in the form `§2.7` or `slide 12`; `#` starts
  a comment.
- `threshold`: a number, default 0.6.

**Sections** are the report's level-2 and level-3 headings in the body bucket (§14.2), identified by the leading
`N.` or `N.M` in the heading text. Headings without a number are ignored. **Slides** are the deck's content slides,
each with its number, title and source footer (§14.4 D009 rule; a spec's `source`).

A section is **covered** by a slide when either of these holds:
1. The slide's footer mentions `§N` or `§N.M`, where a bare `§N` covers only the level-2 section `N`. In
   `Capsule report §2.3, App. A.1`, the footer cites `§2.3`; in `§1, §3`, it cites both.
2. The normalised similarity (`difflib.SequenceMatcher` ratio on lower-cased text with punctuation removed and
   whitespace collapsed) between the heading text (without its number) and the slide title is ≥ `threshold`.

A level-2 section also counts as covered when any of its level-3 sections is covered.

**Rules** are lines matching `^\s*[-*]?\s*R(\d+)\b[.:)]?\s+(.*)` in the report body, or table rows whose first cell
is `R<n>` (the name is the second cell). In the deck, they are text-frame lines or table first cells matching the
same pattern. Names are trimmed.

Findings:

| Rule | Severity | Finding |
|---|---|---|
| C001 | warning | a report section covered by no slide and not listed in `cuts` |
| C002 | warning | a content slide that covers no section and is not in `cuts` |
| C003 | error | a footer `§N[.M]` that names no section of the report |
| C004 | warning | a rule `R<n>` present in only 1 of the 2 documents |
| C005 | info | a rule `R<n>` whose first names in report and deck have similarity < 0.5 |
| C006 | info | a rule `R<n>` that appears on more than 1 deck slide (each slide listed in the message) |

`path` in findings is the report path for C001, C003, C004 and C005, and the deck path for C002 and C006. `line` is
the report line, or the slide position.

Result: checker shape, plus `"outline": [{"section", "heading", "slides": [slide numbers]}]` and
`"slides": [{"number", "title", "sections": [...]}]`.

**15.1–15.5 pinned details** (from the test authors' questions)

- **review_coverage fields.**
  - `outline[].section` is the number without `§` (`"2.1"`), and `heading` is the heading text without its number.
  - Slide numbers are strings.
  - A `cuts` entry `slide N` names the displayed slide number. `#` starts a comment anywhere on a line.
- **review_coverage finding locations.** C003, C002 and C006 findings, and C004 findings for rules present only in
  the deck, use the deck path and the slide position as `line`. The other findings use the report path and line.
- **review_coverage footers.** Footers are split into segments at `;` and `·`. A `§` mention in a segment that
  contains `arXiv` or the whole word `paper` before it cites a paper, not the report, so it is skipped
  (`arXiv 2510.23601 §3.3` is not a C003).
- **review_coverage rules.**
  - The rule line pattern also accepts a leading bullet `•`, and a table first cell that is exactly `R<n>`.
  - "Report body" means the body bucket.
- **text_xref edits.** `old`/`new` are the reference texts. References in the report's prose are renumbered too.
- **text_xref markers.** A reference matches only as a whole: `§4.2` does not match inside `§4.2.1`. X002 markers are
  the string-literal first 2 arguments. Literals starting with a newline, or blank after stripping, are skipped. The
  finding's path and line are the `.py` file and the call line.
- **claims_trace numbers.**
  - `arXiv:ID` and `arXiv ID` numbers are excluded.
  - `number` is the token as written, without a sign.
  - Duplicate citations within a sentence are removed.
  - Claims are ordered by line, then position.
  - A number without `%` never matches a decimal fraction.
- **claims_trace sentences.**
  - Sentence splitting never splits inside `[...]`.
  - `App.`, `Tab.`, `Sec.`, `Ref.` and `Refs.` join the §7.1 abbreviation list, which applies to text_lint as well.
- **claims_trace ledger.**
  - Markdown emphasis around a cell value (`**2.75**`) is ignored.
  - When both a derived row and a plain row match, `derived` wins.
  - The ledger also applies to `no_source` numbers: a ledger match gives `derived` or `ledgered` instead of `no_source`.
- **text_apply_edits.**
  - `applied` is the count of edits applied.
  - `failures[].index` is 0-based.
  - Occurrences are counted like `str.count` (non-overlapping).
  - Line endings of text files are preserved.
- **Missing files.** Any missing input file for a §15 tool is a `ToolError`.

### 15.2 `text_xref` / `tundlekit text xref REPORT.md --in FILE... [--renumber OLD=NEW ...] [--write]`

Resolves cross-references against a report.

Arguments: `report` (path), `files` (list of paths to check, such as deck scripts, specs and presenter packs),
`renumber` (list of `OLD=NEW` strings), `write` (bool).

- **Targets** in the report:
  - sections `§N`, `§N.M`, from numbered headings;
  - appendices `App. X` and `App. X.n`, from headings `## Appendix X.` and `### X.n`;
  - figures `Fig. Pn` and tables `Table Pn`, from captions (§7.2).
- **References** in `files`: every `§N(.M)*`, `App. X(.n)?`, `Fig. P?n` and `Table P?n`.
  - A mention preceded on the same line by `arXiv` or the whole word `paper` is skipped, as in §7.2.
  - When a single line mentions several references (`§2.2, Table 1`), each is checked separately.
- **X001** (error): a reference with no target. **X002** (warning): a report marker that a Python file slices on
  appears other than once in the report. Markers are string-literal first arguments of calls named `between` or
  `section`; `section("N")` means the marker `### N `.
- **Renumbering.** `renumber` entries such as `Fig. 9=Fig. 10`, `§4.2=§4.3` or `App. D.4=App. D.5` are applied
  simultaneously, so swaps work, to references in `files` and to the matching headings and captions in `report`.
  - Only whole references are replaced: `Fig. 1` never matches inside `Fig. 10`, and `§4.2` never matches inside
    `§4.21`.
  - Without `write`, the result lists the planned edits (`{"path", "line", "old", "new"}`) and nothing changes.
  - With `write`, the files are rewritten, preserving line endings (UTF-8).
- Result: checker shape plus `"edits": [...]`. Findings are computed before renumbering.

### 15.3 `claims_trace` / `tundlekit claims trace REPORT.md --papers DIR [--ledger LEDGER.md] [--in FILE...]`

Traces every cited number to a page in its source. Arguments: `report`, `papers` (dir), `ledger`, `files`.

- **References** are parsed from the report's references bucket. Each `[n]` entry maps to an arXiv id when the entry
  contains `arXiv:ID` or `arXiv ID` (version suffix stripped).
- **Claims.** Each sentence (§7.1 splitting) in the body bucket that contains at least 1 citation `[n]` or
  `[n, ...]` (n an integer; several may appear) and at least 1 number yields its numbers.
  - A number is a token matching `(?<![\w.])\d+(?:[.,]\d+)*%?` (a `-` or `−` directly before it is ignored).
  - Excluded: the citation brackets' contents, numbers directly after `§`, `Fig.`, `Table`, `App.` or `arXiv`,
    4-digit years 1900–2099 without a decimal or `%`, and single-digit integers without `%`.
  - For each number, the cited papers' text (`{papers}/{id}.txt`, either text format) is searched page by page.
    Numbers use only the cited references of their own sentence.
  - A number is **located** when its text (commas removed) appears in a page's text (commas removed), with no
    digit or `.digit` directly before or after. For a percentage `P%`, the match may also be `P` or `P/100`
    written as a decimal (`51%` ↔ `0.51`; `96.8%` ↔ `0.968`).
- **Ledger** (optional): a Markdown file whose table rows contain the number (as a whole token) in a cell. A row
  whose text contains `derived` (case-insensitive) marks the number **derived**; any other matching row marks it
  **ledgered**. The ledger is checked only for numbers not located.
- **Output.** 1 entry per (sentence, number):
  `{"path", "line", "number", "citations": [n], "papers": [ids], "status": "located" | "derived" | "ledgered" | "untraced" | "no_source", "pages": [ints]}`.
  - `no_source` means none of the sentence's citations resolves to a paper that has a text file.
- **Findings:** **T001** (warning) for each `untraced` entry, **T002** (info) for each `no_source` entry.
- **Result:** checker shape plus `"claims": [...]` and `"summary": {status: count}` (all 5 keys present).
- `files` (optional): extra Markdown files checked the same way, using the report's reference list.

### 15.4 `deck_diff` / `tundlekit deck diff OLD.pptx NEW.pptx [--search PATH...]` and `docx_diff` / `tundlekit text docx-diff OLD NEW [--search PATH...]`

These carry hand edits back into build scripts. Arguments: `old`, `new`, `search` (list of paths).

**`deck_diff`** (needs python-pptx) compares `deck_inspect` outputs. Slides are paired by number text when both have
one, else by title similarity ≥ 0.6, else by position.

Result:

```json
{"changes": [{"slide", "field": "title" | "text" | "notes" | "hidden" | "added" | "removed" | "moved",
              "old", "new", "diff", "hint": ["path:line"]}]}
```

- `slide` is the new slide's number, or its position when it has no number; for `removed`, it is the old one's.
- `old` and `new` are strings (or booleans for `hidden`, positions for `moved`).
- `diff` is a unified diff for `text`, `title` and `notes`, and null otherwise.
- Text changes are compared per text frame (a changed frame gives 1 `text` change).
- `hint` holds up to 3 locations, as `path:line`, where the old string occurs in the files under `search`
  (directories are walked for `.py`, `.json` and `.md`). If the old string doesn't occur, the tool tries its longest
  line of 12 or more characters. Otherwise `hint` is `[]`.
- An identical deck gives `changes: []`.

**`docx_diff`** compares 2 `.docx` files, or a `.docx` with a `.md` file (either order).
- Paragraphs come from `word/document.xml` (as in §8.3's text backend), skipping empty ones.
- Markdown is reduced to paragraphs:
  - blank-line-separated blocks are joined into 1 line;
  - headings, emphasis (`*`, `_`), inline code backticks, and link and image markup (the text is kept) are stripped;
  - list items and table cells each become their own paragraph, and table separator rows are dropped;
  - fenced code lines are kept as individual paragraphs.
- Paragraphs are normalised (whitespace collapsed, curly quotes and apostrophes folded to straight ones), then
  aligned with `difflib.SequenceMatcher`.
- Result `{"changes": [{"op": "replace" | "insert" | "delete", "old": [str], "new": [str], "old_index", "new_index", "hint"}]}`,
  where `hint` is as above for the first old paragraph. Identical content gives `[]`.

Pinned: `docx_diff` indices are 0-based, and `old`/`new` hold the raw (un-normalised) paragraph text. `deck_diff`
`moved` positions are 1-based. Hint paths are formed by joining the `search` entry with the path found while walking
it, so they are relative when the entry was relative. A file given directly in `search` is searched too.

### 15.5 `text_apply_edits` / `tundlekit text apply-edits EDITS.json FILE [--write]`

Anchored find and replace. Arguments: `edits` (a list, or CLI a JSON file), `path`, `write`. Each edit is
`{"find": str, "replace": str, "count": int (default 1)}`.
- Each `find` must occur exactly `count` times in the file's current text. Edits apply in order, each to the result
  of the previous one.
- If any edit fails, nothing is written, and the result lists every failure (later edits are still evaluated against
  the text as it stands after the successful ones).
- `.docx` files are edited paragraph by paragraph inside `word/document.xml`, where `find` must lie within 1 paragraph.
  An edit whose `find` spans several runs is still applied: the replacement goes into the first affected run, and
  the affected text is removed from the other runs. Every other file in the package is copied unchanged.
- Without `write`, the tool is a dry run.
- Result `{"ok", "applied", "failures": [{"index", "find", "found"}], "diff"}`. `diff` is a unified diff (paragraphs
  as lines for `.docx`). `ok` is true when there are no failures.

### 15.6 `translate_terms` / `tundlekit translate terms SRC TGT [TGT...]`

Checks that technical terms carry over. Arguments: `src`, `targets` (list).

- **Terms** are found in `SRC`:
  - CamelCase words (`[A-Z][a-z]+[A-Z][A-Za-z0-9]*` or `[a-z]+[A-Z][A-Za-z0-9]*`);
  - words of 2+ capital letters (`[A-Z]{2,}[A-Za-z0-9]*`);
  - all patterns use ASCII classes only, so a term followed directly by CJK text (`MCP协议`) is still `MCP`, and a
    run of ASCII words counts when bordered by CJK letters, CJK punctuation, spaces next to CJK, or line ends;
  - maximal runs of 2–4 ASCII words (letters, digits, `-`) joined by single spaces that have a non-ASCII letter
    (such as CJK) or line start/end on both sides. Only runs made entirely of such words count.
  - Inline code, URLs and file paths are excluded.
- Counting is case-insensitive, on whole words (ASCII word boundaries). Term keys are written as they first appear
  in `SRC`.
- **Findings** for each target in order, compared with the previous file (`SRC` for the first):
  - **L001** (warning): a term with count > 0 in the previous file and 0 in this one;
  - **L002** (info): the count changed and neither count is 0.
  - Findings carry the target path, and `line` is null.
- Result: checker shape plus `"terms": {term: [count in SRC, count in each target...]}`.

### 15.7 `bundle_source` and `bundle_setup_table`

**`bundle_source`** / `tundlekit bundle source FILE [--url URL] [--install CMD] [--write] [--force]`
- Arguments: `file`, `url`, `install`, `write`, `force`.
- Writes `SOURCE.md` in the file's directory. It refuses (`ToolError`) to overwrite an existing one unless `force`
  is given.
- Contents:

  ```
  # {program} {version}

  - File:       {name}
  - Source:     {url or <official download URL>}
  - Downloaded: {file mtime date YYYY-MM-DD}
  - SHA-256:    {hash}
  - Install:    {install or <steps>}
  ```

- The stem is the file name without its extension. Compound archive extensions (`.tar.gz`, `.tar.xz`, `.tar.bz2`,
  `.tar.zst`) count as 1 extension, so `nvim-linux-x86_64.tar.gz` gives `nvim linux` and no version.
- First, architecture tokens are removed from the stem: `x86_64`, `x86-64`, `x64`, `x86`, `amd64`, `arm64`,
  `aarch64`, `win64`, `win32`, `64-bit`, `32-bit` (case-insensitive, only when delimited by the start, the end or
  one of `-_. `). The separators around a removed token collapse to 1.
- `version` is the first match of `(?<![0-9])v?([0-9]+(?:[._][0-9]+)+(?:-?rc[0-9]+)?)` in the result (group 1),
  with underscores turned into dots, or empty (the heading then has no trailing space). Examples:
  `tsetup-x64.6.8.1` gives `tsetup` and `6.8.1`; `NVIDIA-Linux-x86_64-570.169` gives `NVIDIA Linux` and `570.169`;
  `CrystalDiskInfo9_8_0` gives `CrystalDiskInfo` and `9.8.0`; `cmake-4.1.0-rc1-windows-x86_64` gives `cmake` and
  `4.1.0-rc1`; `7z2603-x64` gives `7z2603` and no version.
- `program` is the text before the version (the whole architecture-stripped stem when there is no version), with
  `_` and `-` turned into spaces, runs of spaces collapsed, and a trailing separator or a trailing separate `v`
  token removed, then trimmed.
- Without `write`, the tool returns the text only.
- Result `{"path", "text", "sha256", "program", "version", "written"}`.
- A written file passes `bundle_verify`.

**`bundle_setup_table`** / `tundlekit bundle setup-table DIR [--write]`
- Arguments: `dir`, `write`.
- Adds 1 table row per entry that §2.7 B006 would report, in sorted order, to `DIR/README.md`:
  `` | `name` | {program} {version} |``, using the `bundle_source` guesses.
- Stub installers (a name containing `Setup`, `Installer`, `Loader` or `latest`, case-insensitive, with no version)
  get ` ⚠ check: may download during install` appended.
- Existing rows and all other text are untouched. Rows go directly after the last row of the first table, or, if
  there is no table, a table with header `| File | What it is |` and `|---|---|` is appended (creating README.md
  if needed).
- Result `{"added": [rows], "written": bool}`. After a write, B006 is clean for that directory.

### 15.8 `papers_summary` and `papers_index_check`

**`papers_summary`** / `tundlekit papers summary ID [--dir D] [--short NAME] [--write]`
- Arguments: `id`, `dir`, `short`, `write`.
- Writes `{dir}/summaries/{id} - {short}.md`, creating the directory. It refuses (`ToolError`) to overwrite, or
  when the text file is missing.
- The skeleton follows the INDEX format:

  ```
  # {id} · {title}

  {authors} · arXiv {id} · {pages} pp ({body} body)
  Read: <pages read>

  ## Summary

  ## How it works

  ## Results

  ## Limitations

  ## Relevance
  ```

- `title` is the first non-empty line of page 1 with more than 3 words, joined with each following line that
  starts with a lower-case letter (a wrapped title), with whitespace collapsed and stripped.
- `short` defaults to the title's text before the first `:`, truncated to 40 characters. Characters invalid in file
  names (`\/:*?"<>|`) are removed, and the result is trimmed.
- `authors` is the next non-empty line after the title's last line, stripped.
- `body` is the references page − 1 (§9.2), or `pages` when there is none.
- Result `{"path", "text", "written"}`.

**`papers_index_check`** / `tundlekit papers index-check [--dir D] [--index PATH] [--report REPORT.md]`
- Arguments: `dir`, `index` (default `{dir}/summaries/INDEX.md`), `report`.
- Summary files are `{dir}/summaries/{id} - *.md`.
- Result: checker shape plus `"papers"`, `"summaries"` (counts).

| Rule | Severity | Finding |
|---|---|---|
| P001 | warning | a paper (valid id with `.txt` or `.pdf`) with no summary file |
| P002 | warning | a summary file whose id is not mentioned in INDEX.md |
| P003 | warning | INDEX.md states a count (`(\d+) summaries`) that differs from the number of summary files |
| P004 | warning | a summary missing any of the headings `## Summary`, `## How it works`, `## Results`, `## Limitations`, `## Relevance` (a heading counts when it starts with that text) |
| P005 | warning | with `report`, an arXiv id cited in its references section that has no summary |

### 15.9 Doc-only skill: `review-prompts`

`skills/review-prompts/SKILL.md` and `skills/review-prompts/prompts/{so-what,first-time-reader,adversarial-flaw-classes,fact-check}.md`
hold reusable reviewer briefs, each with a fixed output table:

| Brief | Output table |
|---|---|
| so-what | `Element · So what · Verdict` (keep, cut or merge), for every section, paragraph, bullet, row and slide |
| first-time-reader | `Where · Confusion · Fix` |
| adversarial-flaw-classes | `Flaw class · Found · Fix`, with the full GUIDE §8 flaw-class table |
| fact-check | `Claim · Source opened · Page · Verdict` |

Each brief states:
- its inputs (deck inspect output, report text, audience description, protected list);
- that the reviewer runs in a fresh context and reports findings without rewriting;
- how findings are propagated (search for every other instance).

The skill says which tundlekit tools produce each input: `deck_inspect`, `render_office`, `review_coverage`,
`claims_trace`. Each prompt file links back to SKILL.md, or needs no links.

### 15.10 Registration

New modules are added to `MODULES` after `textlint`, in this order:
- `review`, with `review_coverage` and CLI group `review` (command `coverage`);
- `claims`, with `claims_trace` and CLI group `claims` (command `trace`).

The other new tools extend existing modules:
- `text_xref`, `text_apply_edits` and `docx_diff` in `textlint` (CLI `text xref`, `text apply-edits`, `text docx-diff`);
- `deck_diff` in `deck` (CLI `deck diff`);
- `translate_terms` in `translate` (CLI `translate terms`);
- `bundle_source` and `bundle_setup_table` in `bundle` (CLI `bundle source`, `bundle setup-table`);
- `papers_summary` and `papers_index_check` in `papers` (CLI `papers summary`, `papers index-check`).

Read-only annotations: `review_coverage`, `claims_trace`, `deck_diff`, `docx_diff`, `papers_index_check` and
`translate_terms` are read-only. The tools with a `write` flag are not. The skills that cover these areas
(deck-builder, report-writing, deliverable-review, paper-reading, tundle-bundle, zh-en-translation) mention the new
commands, and `review-prompts` is added to the required-skills table of §11.
