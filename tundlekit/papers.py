"""papers: fetch arXiv papers and read them compactly (MANIFEST.md §9, after tundle's papers/*.py).

A papers directory holds {id}.pdf and {id}.txt, with '/' in old-style ids stored as '_'. The text
format written by fetch is, for each page N, '\\n\\n===== page N =====\\n' plus the page text; readers
also accept pdftotext output, whose pages are separated by form feeds.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from glob import escape as glob_escape
from pathlib import Path

from tundlekit import __version__
from tundlekit.cli_support import CliResult, common_flags
from tundlekit.registry import ToolError, tool

DEFAULT_BASE = "https://arxiv.org/pdf/"
USER_AGENT = f"tundlekit/{__version__} (paper reading; +https://arxiv.org/help/api)"
# Always used with fullmatch (MANIFEST §13.1): `$` would accept a trailing newline. ASCII digits only.
NEW_ID = re.compile(r"[0-9]{4}\.[0-9]{4,5}(v[0-9]+)?")
OLD_ID = re.compile(r"[a-z-]+(\.[A-Z]{2})?/[0-9]{7}(v[0-9]+)?")
OLD_STEM = re.compile(r"([a-z-]+(?:\.[A-Z]{2})?)_([0-9]{7}(?:v[0-9]+)?)")
MARKER = re.compile(r"^===== page (\d+) =====[ \t]*$", re.M)
REFERENCES = re.compile(r"^\s*(References|REFERENCES|Bibliography|BIBLIOGRAPHY)\s*$", re.M)


# ---------------------------------------------------------------------------------------------- ids and files

def valid_id(arxiv_id: str) -> bool:
    return bool(NEW_ID.fullmatch(arxiv_id) or OLD_ID.fullmatch(arxiv_id))


def stored_name(arxiv_id: str) -> str:
    return arxiv_id.replace("/", "_")


def id_from_stem(stem: str) -> str | None:
    """The arXiv id a file stem stands for, or None when the stem is not a valid id."""
    if NEW_ID.fullmatch(stem):
        return stem
    m = OLD_STEM.fullmatch(stem)
    return f"{m.group(1)}/{m.group(2)}" if m else None


def _paper_dir(dir: str | None) -> Path:
    return Path(dir) if dir else Path.cwd()


def _read(path: Path) -> str:
    with open(path, encoding="utf-8", errors="replace") as f:   # universal newlines
        return f.read()


def _text_for(arxiv_id: str, dir: str | None) -> str:
    if not isinstance(arxiv_id, str) or not valid_id(arxiv_id):
        raise ToolError(f"invalid arXiv id: {arxiv_id!r}")
    path = _paper_dir(dir) / (stored_name(arxiv_id) + ".txt")
    if not path.is_file():
        raise ToolError(f"no text for {arxiv_id} ({path} is missing): run `tundlekit papers fetch {arxiv_id}` first")
    try:
        return _read(path)
    except OSError as exc:
        raise ToolError(f"cannot read {path}: {exc}") from None


def split_pages(text: str) -> list[tuple[int, str]]:
    """(page number, page text) pairs from either text format. Empty form-feed pages are skipped."""
    markers = list(MARKER.finditer(text))
    if markers:
        pairs = []
        for k, m in enumerate(markers):
            end = markers[k + 1].start() if k + 1 < len(markers) else len(text)
            body = text[m.end():end]
            body = body[1:] if body.startswith("\n") else body
            pairs.append((int(m.group(1)), body.rstrip("\n")))
        return pairs
    return [(n, body) for n, body in enumerate(text.split("\f"), 1) if body.strip()]


def page_count(text: str) -> int:
    pairs = split_pages(text)
    return max((n for n, _ in pairs), default=0)


# ---------------------------------------------------------------------------------------------- fetch

class _Failed(Exception):
    """A per-id failure with a message for the result."""


def _remove(*paths: Path) -> None:
    for path in paths:
        try:
            if path.is_file() or path.is_symlink():
                path.unlink()
        except OSError:
            pass


def _write_atomic(path: Path, data: bytes) -> None:
    part = path.with_name(path.name + ".part")
    try:
        part.write_bytes(data)
        os.replace(part, path)
    finally:
        _remove(part)


def _extract_text(pdf: Path, txt: Path) -> str | None:
    """Write txt from pdf. Returns a warning when no extractor exists; raises _Failed when extraction fails."""
    from tundlekit.render import load_pymupdf, native_stdout_to_stderr

    pymupdf = load_pymupdf()
    if pymupdf is not None:
        try:
            with native_stdout_to_stderr(), pymupdf.open(str(pdf)) as doc:
                parts = []
                for n, page in enumerate(doc, 1):
                    parts.append(f"\n\n===== page {n} =====\n")
                    parts.append(page.get_text("text"))
        except Exception as exc:  # pymupdf raises its own types for damaged files
            raise _Failed(f"text extraction failed: {exc}") from None
        _write_atomic(txt, "".join(parts).encode("utf-8"))
        return None
    exe = shutil.which("pdftotext")
    if exe is None:
        return "no text extractor: install pymupdf (pip install pymupdf) or put pdftotext on PATH"
    part = txt.with_name(txt.name + ".part")
    try:
        proc = subprocess.run([exe, "-layout", "-enc", "UTF-8", str(pdf), str(part)],
                              capture_output=True, text=True, errors="replace", timeout=300)
        if proc.returncode != 0 or not part.is_file():
            raise _Failed(f"pdftotext failed: {proc.stderr.strip() or proc.returncode}")
        os.replace(part, txt)
    except (OSError, subprocess.SubprocessError) as exc:
        raise _Failed(f"pdftotext failed: {exc}") from None
    finally:
        _remove(part)
    return None


def _download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read()
    except urllib.error.HTTPError as exc:
        raise _Failed(f"HTTP {exc.code} for {url}") from None
    except Exception as exc:  # URLError, timeouts, http.client.IncompleteRead, ...
        raise _Failed(f"download failed for {url}: {type(exc).__name__}: {exc}") from None


def _fetch_one(arxiv_id: str, root: Path, base: str, before_download) -> dict:
    res = {"id": arxiv_id, "status": "failed", "pdf": None, "txt": None, "pages": None, "chars": None,
           "error": None, "text": False, "warning": None}
    if not isinstance(arxiv_id, str) or not valid_id(arxiv_id):
        res["error"] = f"invalid arXiv id: {arxiv_id!r}"
        return res
    pdf = root / (stored_name(arxiv_id) + ".pdf")
    txt = root / (stored_name(arxiv_id) + ".txt")
    created: list[Path] = []
    try:
        if pdf.is_file():
            status = "present"
        else:
            before_download()
            url = base.rstrip("/") + "/" + arxiv_id
            data = _download(url)
            if not data.startswith(b"%PDF-"):
                raise _Failed(f"not a PDF: {url} returned {len(data)} bytes that do not start with %PDF-")
            created.append(pdf)
            _write_atomic(pdf, data)
            status = "downloaded"
        if not txt.is_file():
            created.append(txt)
            res["warning"] = _extract_text(pdf, txt)
        text = _read(txt) if txt.is_file() else None
    except Exception as exc:  # 1 id's failure never stops the others (MANIFEST §13.5)
        _remove(*created, *(p.with_name(p.name + ".part") for p in created))
        res["error"] = str(exc) if isinstance(exc, _Failed) else f"{type(exc).__name__}: {exc}"
        return res
    res.update(status=status, pdf=str(pdf))
    if text is not None:
        res.update(txt=str(txt), pages=page_count(text), chars=len(text), text=True)
    return res


@tool(
    "papers_fetch",
    "Download arXiv papers as {id}.pdf into dir (default the current directory) and extract {id}.txt with "
    "page markers, for reading with papers_body and papers_peek. A PDF already present is not downloaded "
    "again. Waits `delay` seconds (default 3) between downloads. Base URL: base_url, else "
    "TUNDLEKIT_ARXIV_BASE, else https://arxiv.org/pdf/. A failure for 1 id never stops the others.",
    {"type": "object",
     "properties": {
         "ids": {"type": "array", "items": {"type": "string"},
                 "description": "arXiv ids, e.g. 2401.00001 or cs/0112017"},
         "dir": {"type": "string", "description": "papers directory (default: current directory)"},
         "base_url": {"type": "string", "description": "PDF base URL (default https://arxiv.org/pdf/)"},
         "delay": {"type": "number", "minimum": 0, "description": "seconds between downloads (default 3)"},
     },
     "required": ["ids"],
     "additionalProperties": False},
    readOnlyHint=False,
    openWorldHint=True,
)
def papers_fetch(ids: list[str], dir: str | None = None, base_url: str | None = None,
                 delay: float = 3) -> dict:
    if delay is None or delay < 0:
        raise ToolError("delay must be at least 0")
    base = base_url or os.environ.get("TUNDLEKIT_ARXIV_BASE") or DEFAULT_BASE
    root = _paper_dir(dir)
    try:
        root.mkdir(parents=True, exist_ok=True)
    except (OSError, ValueError) as exc:
        raise ToolError(f"cannot create {root}: {exc}") from None
    downloads = 0

    def before_download():
        nonlocal downloads
        if downloads and delay:
            time.sleep(delay)
        downloads += 1

    results = [_fetch_one(i, root, base, before_download) for i in ids]
    return {"results": results, "ok": all(r["status"] != "failed" for r in results)}


# ---------------------------------------------------------------------------------------------- body

def _compact(body: str) -> str:
    body = re.sub(r"-\n(?=[a-z])", "", body)
    body = re.sub(r"\n+", " ", body)          # single newlines become spaces; 1 page stays 1 line
    body = re.sub(r"[ \t]+", " ", body)
    return body.strip()


@tool(
    "papers_body",
    "Return a paper's main body compactly for reading: pages start..end (default page 1 to the references "
    "page, else the last page), each as one '[pN] text' line with hyphenated breaks joined and whitespace "
    "collapsed, cut to max_chars (default 90000). Needs {id}.txt from papers_fetch in dir.",
    {"type": "object",
     "properties": {
         "id": {"type": "string", "description": "arXiv id"},
         "dir": {"type": "string", "description": "papers directory (default: current directory)"},
         "start": {"type": "integer", "description": "first page (default 1)"},
         "end": {"type": "integer", "description": "last page (default the references page, else the last)"},
         "max_chars": {"type": "integer", "minimum": 0, "description": "cap on returned text (default 90000)"},
     },
     "required": ["id"],
     "additionalProperties": False},
    readOnlyHint=True,
)
def papers_body(id: str, dir: str | None = None, start: int | None = None, end: int | None = None,
                max_chars: int = 90000) -> dict:
    if max_chars is None or max_chars < 0:
        raise ToolError("max_chars must be at least 0")
    pairs = split_pages(_text_for(id, dir))
    ref_page = next((n for n, body in pairs if n > 3 and REFERENCES.search(body)), None)
    last = max((n for n, _ in pairs), default=0)
    start = 1 if start is None else start
    end = (ref_page or last) if end is None else end
    joined = "\n".join(f"[p{n}] {_compact(body)}" for n, body in pairs if start <= n <= end)
    text = joined[:max_chars]
    return {"id": id, "pages": last, "references_page": ref_page, "start": start, "end": end,
            "text": text, "chars": len(text), "truncated": len(joined) > max_chars}


# ---------------------------------------------------------------------------------------------- peek

def _abstract(text: str, chars: int) -> str:
    m = re.search(r"(?i)\babstract\b", text)
    begin = m.start() if m else 0
    return re.sub(r"(?<!\n)\n(?!\n)", " ", text[begin:begin + chars])


def _grep(text: str, pattern: str, context: int, max_hits: int) -> tuple[list[dict], bool]:
    try:
        rx = re.compile(pattern, re.I)
    except re.error as exc:
        raise ToolError(f"invalid regex {pattern!r}: {exc}") from None
    lines = text.split("\n")
    form_feed = not MARKER.search(text)
    hits, page, truncated = [], 0, False
    feeds = 0
    for i, line in enumerate(lines):
        if form_feed:
            lead = len(line) - len(line.lstrip("\f"))
            page = 1 + feeds + lead
            feeds += line.count("\f")
        else:
            m = MARKER.match(line)
            if m:
                page = int(m.group(1))
        if rx.search(line):
            if len(hits) >= max_hits:
                truncated = True
                break
            lo, hi = max(0, i - context), min(len(lines), i + context + 1)
            hits.append({"page": page, "line": i + 1,
                         "text": " ".join(s.strip() for s in lines[lo:hi])})
    return hits, truncated


@tool(
    "papers_peek",
    "Peek into a fetched paper's text. mode abstract: the text from the first word 'abstract' (or the "
    "start), `chars` long (default 2200). mode grep: case-insensitive regex `pattern` over lines, each hit "
    "with its page, line number and `context` lines around it (default 2), at most max_hits (default 12). "
    "Use it to trace a number to its page. Needs {id}.txt from papers_fetch in dir.",
    {"type": "object",
     "properties": {
         "id": {"type": "string", "description": "arXiv id"},
         "mode": {"type": "string", "enum": ["abstract", "grep"]},
         "dir": {"type": "string", "description": "papers directory (default: current directory)"},
         "chars": {"type": "integer", "minimum": 0, "description": "abstract length (default 2200)"},
         "pattern": {"type": "string", "description": "regex for grep mode"},
         "context": {"type": "integer", "minimum": 0, "description": "lines around each hit (default 2)"},
         "max_hits": {"type": "integer", "minimum": 0, "description": "hit cap (default 12)"},
     },
     "required": ["id", "mode"],
     "additionalProperties": False},
    readOnlyHint=True,
)
def papers_peek(id: str, mode: str, dir: str | None = None, chars: int = 2200, pattern: str | None = None,
                context: int = 2, max_hits: int = 12) -> dict:
    if mode not in ("abstract", "grep"):
        raise ToolError(f"mode must be abstract or grep, got {mode!r}")
    for name, value in (("chars", chars), ("context", context), ("max_hits", max_hits)):
        if value is None or value < 0:
            raise ToolError(f"{name} must be at least 0")
    if mode == "grep" and not pattern:
        raise ToolError("grep mode needs a pattern")
    text = _text_for(id, dir)
    if mode == "abstract":
        return {"id": id, "abstract": _abstract(text, chars)}
    hits, truncated = _grep(text, pattern, context, max_hits)
    return {"id": id, "hits": hits, "truncated": truncated}


# ---------------------------------------------------------------------------------------------- list

@tool(
    "papers_list",
    "List the papers in dir (default the current directory): every {id}.pdf or {id}.txt with a valid arXiv "
    "id, whether the PDF and text exist, the page count, and the path of summaries/{id} - *.md if written.",
    {"type": "object",
     "properties": {"dir": {"type": "string", "description": "papers directory (default: current directory)"}},
     "additionalProperties": False},
    readOnlyHint=True,
)
def papers_list(dir: str | None = None) -> dict:
    root = _paper_dir(dir)
    if not root.is_dir():
        raise ToolError(f"no such directory: {root}")
    found: dict[str, dict] = {}
    for p in root.iterdir():
        if p.suffix not in (".pdf", ".txt") or not p.is_file():
            continue
        arxiv_id = id_from_stem(p.stem)
        if arxiv_id is None:
            continue
        entry = found.setdefault(arxiv_id, {"id": arxiv_id, "pdf": False, "txt": False, "pages": None,
                                            "summary": None})
        entry[p.suffix[1:]] = True
    for arxiv_id, entry in found.items():
        stem = stored_name(arxiv_id)
        if entry["txt"]:
            try:
                entry["pages"] = page_count(_read(root / (stem + ".txt")))
            except OSError:
                entry["pages"] = None
        summaries = sorted((root / "summaries").glob(glob_escape(stem) + " - *.md"))
        if summaries:
            entry["summary"] = str(summaries[0])
    return {"papers": [found[k] for k in sorted(found)]}


# ---------------------------------------------------------------------------------------------- CLI

def add_cli(groups) -> None:
    p = groups.add_parser("papers", help="fetch and read arXiv papers")
    cmds = p.add_subparsers(dest="command", required=True)

    c = cmds.add_parser("fetch", help="download PDFs and extract text")
    c.add_argument("ids", nargs="+", metavar="ID")
    c.add_argument("--dir")
    c.add_argument("--base-url", dest="base_url")
    c.add_argument("--delay", type=float, default=3)
    common_flags(c)
    c.set_defaults(handler=_cli_fetch)

    c = cmds.add_parser("body", help="print the main body, 1 line per page")
    c.add_argument("id", metavar="ID")
    c.add_argument("--dir")
    c.add_argument("--start", type=int)
    c.add_argument("--end", type=int)
    c.add_argument("--max-chars", dest="max_chars", type=int, default=90000)
    common_flags(c)
    c.set_defaults(handler=_cli_body)

    c = cmds.add_parser("abs", help="print the abstract")
    c.add_argument("id", metavar="ID")
    c.add_argument("--dir")
    c.add_argument("--chars", type=int, default=2200)
    common_flags(c)
    c.set_defaults(handler=_cli_abs)

    c = cmds.add_parser("grep", help="search the text with a regex")
    c.add_argument("id", metavar="ID")
    c.add_argument("pattern", metavar="REGEX")
    c.add_argument("--dir")
    c.add_argument("--context", type=int, default=2)
    c.add_argument("--max-hits", dest="max_hits", type=int, default=12)
    common_flags(c)
    c.set_defaults(handler=_cli_grep)

    c = cmds.add_parser("list", help="list papers in a directory")
    c.add_argument("--dir")
    common_flags(c)
    c.set_defaults(handler=_cli_list)


def _cli_fetch(args) -> CliResult:
    r = papers_fetch(args.ids, dir=args.dir, base_url=args.base_url, delay=args.delay)
    lines = []
    for x in r["results"]:
        if x["status"] == "failed":
            lines.append(f"{x['id']}: FAILED {x['error']}")
        else:
            pages = f", {x['pages']} pages, {x['chars']} chars" if x["txt"] else ", no text"
            lines.append(f"{x['id']}: {x['status']}{pages}" + (f" ({x['warning']})" if x["warning"] else ""))
    return CliResult(r, "\n".join(lines))


def _cli_body(args) -> CliResult:
    r = papers_body(args.id, dir=args.dir, start=args.start, end=args.end, max_chars=args.max_chars)
    head = (f"## {r['id']}: {r['pages']} pages, references at p{r['references_page']}, "
            f"showing p{r['start']}-p{r['end']}, {r['chars']} chars")
    tail = "\n[... truncated]" if r["truncated"] else ""
    return CliResult(r, f"{head}\n{r['text']}{tail}")


def _cli_abs(args) -> CliResult:
    r = papers_peek(args.id, "abstract", dir=args.dir, chars=args.chars)
    return CliResult(r, f"### {r['id']}\n{r['abstract']}")


def _cli_grep(args) -> CliResult:
    r = papers_peek(args.id, "grep", dir=args.dir, pattern=args.pattern, context=args.context,
                    max_hits=args.max_hits)
    lines = []
    for h in r["hits"]:
        lines += [f"--- {r['id']} p{h['page']} L{h['line']}", h["text"]]
    if r["truncated"]:
        lines.append("[... more hits]")
    return CliResult(r, "\n".join(lines) or "no hits")


def _cli_list(args) -> CliResult:
    r = papers_list(dir=args.dir)
    lines = [f"{p['id']}  pdf={'yes' if p['pdf'] else 'no'}  txt={'yes' if p['txt'] else 'no'}  "
             f"pages={p['pages'] if p['pages'] is not None else '-'}"
             + (f"  summary={p['summary']}" if p["summary"] else "") for p in r["papers"]]
    return CliResult(r, "\n".join(lines) or "no papers")
