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
# A line that is only a references heading, optionally numbered (`7 References`, `7. REFERENCES`) or
# `References and Notes` (MANIFEST §9.2, §16.6).
REFERENCES = re.compile(r"^[ \t]*(?:[0-9]{1,2}(?:\.[0-9]{1,2})*\.?[ \t]+)?"
                        r"(References|REFERENCES|Bibliography|BIBLIOGRAPHY)"
                        r"(?:[ \t]+(?:and|AND|And)[ \t]+(?:Notes|NOTES))?[ \t]*$", re.M)


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


LAYOUT_RUN = re.compile(r"\S {5,}\S")
LAYOUT_SHARE = 0.20
LAYOUT_WARNING = ("the text looks like `pdftotext -layout` output (columns padded with spaces); "
                  "rerun papers_fetch with reextract to rewrite it from the PDF")


def layout_text(text: str) -> bool:
    """True when more than 20% of the non-blank lines have a run of 5+ spaces between 2 non-space characters
    (MANIFEST §14.7). Page marker lines are not counted."""
    lines = [ln for ln in text.split("\n") if ln.strip() and not MARKER.match(ln)]
    if not lines:
        return False
    padded = sum(1 for ln in lines if LAYOUT_RUN.search(ln))
    return padded > LAYOUT_SHARE * len(lines)


def references_page(pairs: list[tuple[int, str]]) -> int | None:
    """The first page N > 3 with a line that is only References/Bibliography (MANIFEST §9.2)."""
    return next((n for n, body in pairs if n > 3 and REFERENCES.search(body)), None)


# ---------------------------------------------------------------------------------------------- Markdown reports

MD_HEADING = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t#]*$")
REFERENCES_HEADING = re.compile(r"(?i)^(references|bibliography)\b")
APPENDIX_HEADING = re.compile(r"(?i)^appendix\b")
ARXIV_REF = re.compile(r"(?:arXiv|arxiv|ARXIV)(?::\s*|\s+)"
                       r"([0-9]{4}\.[0-9]{4,5}|[a-z-]+(?:\.[A-Z]{2})?/[0-9]{7})(?:v[0-9]+)?(?![0-9])")
REFERENCE_ENTRY = re.compile(r"^\s*\[(\d+)\]")
_FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})")


def read_input(path: str, what: str = "file") -> str:
    """Read a UTF-8 text input (BOM dropped, newlines normalised); a missing file is a ToolError."""
    p = Path(path)
    if not p.is_file():
        raise ToolError(f"{what} not found: {path}")
    try:
        return _read(p).lstrip("﻿")
    except OSError as exc:
        raise ToolError(f"cannot read {path}: {exc}") from None


def heading_buckets(lines: list[str]) -> list[str]:
    """The bucket of each line: body, appendix or references (MANIFEST §14.2). Fenced code is never a heading."""
    buckets, current, fence = [], "body", None
    for line in lines:
        m = _FENCE.match(line)
        if fence is not None:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
        elif m:
            fence = m.group(1)
        else:
            h = MD_HEADING.match(line)
            if h:
                level, text = len(h.group(1)), h.group(2).strip()
                if level <= 2:
                    current = "body"
                if level == 2 and REFERENCES_HEADING.match(text):
                    current = "references"
                elif level == 2 and APPENDIX_HEADING.match(text):
                    current = "appendix"
        buckets.append(current)
    return buckets


def reference_ids(lines: list[str], buckets: list[str]) -> dict[int, str | None]:
    """{n: arXiv id or None} for every `[n]` entry in the references bucket (version suffix stripped)."""
    entries: dict[int, list[str]] = {}
    current = None
    for line, bucket in zip(lines, buckets):
        if bucket != "references":
            current = None
            continue
        m = REFERENCE_ENTRY.match(line)
        if m:
            current = int(m.group(1))
            entries.setdefault(current, [])
        elif MD_HEADING.match(line):
            current = None
        if current is not None:
            entries[current].append(line)
    refs = {}
    for n, text in entries.items():
        m = ARXIV_REF.search("\n".join(text))
        refs[n] = m.group(1) if m else None
    return refs


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


def _fetch_one(arxiv_id: str, root: Path, base: str, before_download, reextract: bool = False) -> dict:
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
        if reextract and txt.is_file():
            # Extract beside the old text first, so a failed or impossible re-extraction keeps it.
            fresh = txt.with_name(txt.name + ".new")
            created.append(fresh)
            res["warning"] = _extract_text(pdf, fresh)
            if fresh.is_file():
                os.replace(fresh, txt)
        elif not txt.is_file():
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
    "TUNDLEKIT_ARXIV_BASE, else https://arxiv.org/pdf/. reextract rewrites an existing {id}.txt from the PDF "
    "(use it when the text is pdftotext -layout output). A failure for 1 id never stops the others.",
    {"type": "object",
     "properties": {
         "ids": {"type": "array", "items": {"type": "string"},
                 "description": "arXiv ids, e.g. 2401.00001 or cs/0112017"},
         "dir": {"type": "string", "description": "papers directory (default: current directory)"},
         "base_url": {"type": "string", "description": "PDF base URL (default https://arxiv.org/pdf/)"},
         "delay": {"type": "number", "minimum": 0, "description": "seconds between downloads (default 3)"},
         "reextract": {"type": "boolean",
                       "description": "rewrite {id}.txt from the PDF even if it exists (default false)"},
     },
     "required": ["ids"],
     "additionalProperties": False},
    readOnlyHint=False,
    openWorldHint=True,
)
def papers_fetch(ids: list[str], dir: str | None = None, base_url: str | None = None,
                 delay: float = 3, reextract: bool = False) -> dict:
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

    results = [_fetch_one(i, root, base, before_download, bool(reextract)) for i in ids]
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
    "collapsed, cut to max_chars (default 90000). With appendix, the default end is the last page. "
    "layout_text flags pdftotext -layout text (then refetch with reextract). Needs {id}.txt from papers_fetch.",
    {"type": "object",
     "properties": {
         "id": {"type": "string", "description": "arXiv id"},
         "dir": {"type": "string", "description": "papers directory (default: current directory)"},
         "start": {"type": "integer", "description": "first page (default 1)"},
         "end": {"type": "integer", "description": "last page (default the references page, else the last)"},
         "max_chars": {"type": "integer", "minimum": 0, "description": "cap on returned text (default 90000)"},
         "appendix": {"type": "boolean",
                      "description": "read past the references: the default end becomes the last page"},
     },
     "required": ["id"],
     "additionalProperties": False},
    readOnlyHint=True,
)
def papers_body(id: str, dir: str | None = None, start: int | None = None, end: int | None = None,
                max_chars: int = 90000, appendix: bool = False) -> dict:
    if max_chars is None or max_chars < 0:
        raise ToolError("max_chars must be at least 0")
    raw = _text_for(id, dir)
    pairs = split_pages(raw)
    ref_page = references_page(pairs)
    last = max((n for n, _ in pairs), default=0)
    start = 1 if start is None else start
    if end is None:
        end = last if appendix else (ref_page or last)
    joined = "\n".join(f"[p{n}] {_compact(body)}" for n, body in pairs if start <= n <= end)
    text = joined[:max_chars]
    layout = layout_text(raw)
    return {"id": id, "pages": last, "references_page": ref_page, "start": start, "end": end,
            "text": text, "chars": len(text), "truncated": len(joined) > max_chars,
            "layout_text": layout, "warnings": [LAYOUT_WARNING] if layout else []}


# ---------------------------------------------------------------------------------------------- peek

def _abstract(text: str, chars: int) -> str:
    m = re.search(r"(?i)\babstract\b", text)
    begin = m.start() if m else 0
    return re.sub(r"(?<!\n)\n(?!\n)", " ", text[begin:begin + chars])


def _cut(text: str, mid: int, width: int) -> str:
    """At most `width` characters of text, centred on offset `mid` (MANIFEST §14.7, §16.6)."""
    if len(text) <= width:
        return text
    lo = max(0, min(mid - width // 2, len(text) - width))
    return text[lo:lo + width]


def _hit_text(lines: list[str], i: int, lo: int, hi: int, m: re.Match, width: int | None) -> str:
    """Lines lo..hi-1 stripped and joined; with width, cut around the match `m` found in line i itself."""
    parts = [s.strip() for s in lines[lo:hi]]
    joined = " ".join(parts)
    if width is None:
        return joined
    offset = sum(len(p) + 1 for p in parts[:i - lo])
    raw = lines[i]
    lead = len(raw) - len(raw.lstrip())
    own = len(parts[i - lo])
    start = min(max(m.start() - lead, 0), own)
    end = min(max(m.end() - lead, start), own)
    return _cut(joined, offset + (start + end) // 2, width)


def _grep(text: str, pattern: str, context: int, max_hits: int,
          width: int | None = None) -> tuple[list[dict], bool]:
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
        m = rx.search(line)
        if m:
            if len(hits) >= max_hits:
                truncated = True
                break
            lo, hi = max(0, i - context), min(len(lines), i + context + 1)
            hits.append({"page": page, "line": i + 1, "text": _hit_text(lines, i, lo, hi, m, width)})
    return hits, truncated


@tool(
    "papers_peek",
    "Peek into a fetched paper's text. mode abstract: the text from the first word 'abstract' (or the "
    "start), `chars` long (default 2200). mode grep: case-insensitive regex `pattern` over lines, each hit "
    "with its page, line number and `context` lines around it (default 2), at most max_hits (default 12). "
    "width cuts each hit to that many characters around the match. Use it to trace a number to its page. "
    "Needs {id}.txt from papers_fetch in dir.",
    {"type": "object",
     "properties": {
         "id": {"type": "string", "description": "arXiv id"},
         "mode": {"type": "string", "enum": ["abstract", "grep"]},
         "dir": {"type": "string", "description": "papers directory (default: current directory)"},
         "chars": {"type": "integer", "minimum": 0, "description": "abstract length (default 2200)"},
         "pattern": {"type": "string", "description": "regex for grep mode"},
         "context": {"type": "integer", "minimum": 0, "description": "lines around each hit (default 2)"},
         "max_hits": {"type": "integer", "minimum": 0, "description": "hit cap (default 12)"},
         "width": {"type": "integer", "minimum": 1,
                   "description": "grep: cut each hit's text to at most this many characters, centred on the match"},
     },
     "required": ["id", "mode"],
     "additionalProperties": False},
    readOnlyHint=True,
)
def papers_peek(id: str, mode: str, dir: str | None = None, chars: int = 2200, pattern: str | None = None,
                context: int = 2, max_hits: int = 12, width: int | None = None) -> dict:
    if mode not in ("abstract", "grep"):
        raise ToolError(f"mode must be abstract or grep, got {mode!r}")
    for name, value in (("chars", chars), ("context", context), ("max_hits", max_hits)):
        if value is None or value < 0:
            raise ToolError(f"{name} must be at least 0")
    if width is not None and (isinstance(width, bool) or not isinstance(width, int) or width < 1):
        raise ToolError("width must be a positive integer")
    if mode == "grep" and not pattern:
        raise ToolError("grep mode needs a pattern")
    text = _text_for(id, dir)
    if mode == "abstract":
        return {"id": id, "abstract": _abstract(text, chars)}
    hits, truncated = _grep(text, pattern, context, max_hits, width)
    return {"id": id, "hits": hits, "truncated": truncated}


# ---------------------------------------------------------------------------------------------- list

@tool(
    "papers_list",
    "List the papers in dir (default the current directory): every {id}.pdf or {id}.txt with a valid arXiv "
    "id, whether the PDF and text exist, the page count, whether the text looks like pdftotext -layout "
    "output (layout_text), and the path of summaries/{id} - *.md if written; missing_summary lists the ids "
    "without one.",
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
                                            "layout_text": False, "summary": None})
        entry[p.suffix[1:]] = True
    for arxiv_id, entry in found.items():
        stem = stored_name(arxiv_id)
        if entry["txt"]:
            try:
                text = _read(root / (stem + ".txt"))
                entry["pages"] = page_count(text)
                entry["layout_text"] = layout_text(text)
            except OSError:
                entry["pages"] = None
        summaries = sorted((root / "summaries").glob(glob_escape(stem) + " - *.md"))
        if summaries:
            entry["summary"] = str(summaries[0])
    papers = [found[k] for k in sorted(found)]
    return {"papers": papers, "missing_summary": [p["id"] for p in papers if p["summary"] is None]}


# ---------------------------------------------------------------------------------------------- summaries

SUMMARY_HEADINGS = ("## Summary", "## How it works", "## Results", "## Limitations", "## Relevance")
BAD_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|\x00-\x1f]')
SUMMARY_FILE = re.compile(r"(.+?) - .*\.md")
INDEX_COUNT = re.compile(r"(\d+) summaries")


VENUE_LINE = re.compile(r"(?i)^(published as|accepted (at|to)|under review|preprint|arxiv:|proceedings of|"
                        r"workshop on)")
TITLE_WORDS = 20
# Author marks after a name: `Smith1,`, `Smith1 2`, `Smith* 1`, `Smith*1`, `Smith†`, superscript digits.
_DIGIT_MARK = re.compile(r"[a-z][0-9]{1,2}(?:\s*,\s*[0-9]{1,2})*(?=\s*(?:[,*∗†‡§]|$|\s[A-Z0-9]))")
_SYMBOL_MARK = re.compile(r"[A-Za-z]\s?[*∗†‡§]|[†‡]")
_SUPERSCRIPT_MARK = re.compile(r"[A-Za-z.][¹²³⁴⁵⁶⁷⁸⁹⁰]")
_CAPITALISED = re.compile(r"\b[A-Z][A-Za-z'’.-]*")
_SECTION_START = re.compile(r"(?i)^(abstract|introduction|[0-9]+\.?\s+introduction)\b")
_SMALL_CAPS = re.compile(r"(?<![A-Za-z])([A-Z]) ([A-Z]{2,})(?![a-z])")
_SPACED_HYPHEN = re.compile(r"(?<![A-Za-z])([A-Z]{2,}) -(?=[A-Z])")


def _author_line(line: str) -> bool:
    """An author list: an e-mail `@`, author marks after names, or a comma list of 3+ capitalised words."""
    if "@" in line or _SYMBOL_MARK.search(line) or _SUPERSCRIPT_MARK.search(line):
        return True
    marks = len(_DIGIT_MARK.findall(line))
    if marks >= 2 or (marks and "," in line):
        return True
    if "," in line:
        words = re.findall(r"[A-Za-z][A-Za-z'’.-]*", line)
        caps = [w for w in words if w[0].isupper()]
        if len(caps) >= 3 and len(caps) * 3 >= len(words) * 2:
            return True
    return False


def rejoin_small_caps(text: str) -> str:
    """`A LITA -G` -> `ALITA-G`, `D EEP R ESEARCH` -> `DEEP RESEARCH` (MANIFEST §16.6)."""
    prev = None
    while prev != text:
        prev = text
        text = _SMALL_CAPS.sub(r"\1\2", text)
    return _SPACED_HYPHEN.sub(r"\1-", text)


def _title_and_authors(page1: str) -> tuple[str, str]:
    """Title and author line of a paper's first page (MANIFEST §15.8, §16.6)."""
    lines = page1.split("\n")
    start = None
    for i, ln in enumerate(lines):
        text = ln.strip()
        if not text or VENUE_LINE.match(text):
            continue
        if len(text.split()) > 3:
            start = i
            break
    if start is None:
        return "", ""
    parts, last = [lines[start].strip()], start
    for i in range(start + 1, len(lines)):
        text = lines[i].strip()
        words = len(" ".join(parts).split())
        if (not text or words >= TITLE_WORDS or _author_line(text) or VENUE_LINE.match(text)
                or _SECTION_START.match(text)):
            break
        parts.append(text)
        last = i
    title = rejoin_small_caps(" ".join(" ".join(parts).split()))
    authors = next((ln.strip() for ln in lines[last + 1:] if ln.strip()), "")
    return title, authors


def _clean_short(short: str) -> str:
    return BAD_FILENAME_CHARS.sub("", short).strip()


@tool(
    "papers_summary",
    "Draft the skeleton of a paper summary in the INDEX format (title, authors, arXiv id, page counts, then "
    "Summary / How it works / Results / Limitations / Relevance headings) from {id}.txt in dir. With write, "
    "saves it as summaries/{id} - {short}.md (never overwrites); short defaults to the title before its first "
    "colon, at most 40 characters.",
    {"type": "object",
     "properties": {
         "id": {"type": "string", "description": "arXiv id"},
         "dir": {"type": "string", "description": "papers directory (default: current directory)"},
         "short": {"type": "string", "description": "short name for the file name"},
         "write": {"type": "boolean", "description": "write the file (default false: only return the text)"},
     },
     "required": ["id"],
     "additionalProperties": False},
    readOnlyHint=False,
)
def papers_summary(id: str, dir: str | None = None, short: str | None = None, write: bool = False) -> dict:
    pairs = split_pages(_text_for(id, dir))
    pages = max((n for n, _ in pairs), default=0)
    ref_page = references_page(pairs)
    body = ref_page - 1 if ref_page else pages
    page1 = next((text for n, text in pairs if n == 1), pairs[0][1] if pairs else "")
    title, authors = _title_and_authors(page1)
    name = _clean_short(short if short is not None else title.split(":", 1)[0][:40])
    if not name:
        name = stored_name(id) if short is None else ""
    if not name:
        raise ToolError(f"short name {short!r} is empty once characters invalid in file names are removed")
    text = "\n".join([
        f"# {id} · {title}", "",
        f"{authors} · arXiv {id} · {pages} pp ({body} body)",
        "Read: <pages read>", "",
        "\n\n".join(SUMMARY_HEADINGS),
    ]) + "\n"
    sdir = _paper_dir(dir) / "summaries"
    target = sdir / f"{stored_name(id)} - {name}.md"
    if os.path.lexists(sdir) and not sdir.is_dir():
        raise ToolError(f"cannot write summaries: {sdir} exists and is a file, not a directory")
    if write:
        if os.path.lexists(target):
            raise ToolError(f"refusing to overwrite {target}")
        try:
            sdir.mkdir(parents=True, exist_ok=True)
        except (OSError, ValueError) as exc:
            raise ToolError(f"cannot create the summaries directory {sdir}: {exc}") from None
        _write_new_atomic(target, text.encode("utf-8"))
    return {"path": str(target), "text": text, "written": bool(write)}


def _write_new_atomic(target: Path, data: bytes) -> None:
    """Write a new file atomically: a temp file in the same directory, then moved into place without ever
    replacing an existing file (MANIFEST §16.1)."""
    import tempfile

    try:
        fd, tmp = tempfile.mkstemp(prefix=".tundlekit-", suffix=".tmp", dir=str(target.parent))
    except (OSError, ValueError) as exc:
        raise ToolError(f"cannot write {target}: {exc}") from None
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        try:
            os.chmod(tmp, 0o666 & ~_umask())
        except OSError:
            pass
        if os.name == "nt":
            os.rename(tmp, target)                  # fails when the target exists
        else:
            try:
                os.link(tmp, target)                # fails when the target exists
            except FileExistsError:
                raise
            except OSError:                         # no hard links here: check, then replace
                if os.path.lexists(target):
                    raise FileExistsError(str(target)) from None
                os.replace(tmp, target)
    except FileExistsError:
        raise ToolError(f"refusing to overwrite {target}") from None
    except (OSError, ValueError) as exc:
        raise ToolError(f"cannot write {target}: {exc}") from None
    finally:
        _remove(Path(tmp))


def _umask() -> int:
    try:
        mask = os.umask(0o022)
        os.umask(mask)
        return mask
    except (OSError, AttributeError):
        return 0o022


def _base_id(arxiv_id: str) -> str:
    return re.sub(r"v[0-9]+$", "", arxiv_id)


def _mentions(text: str, arxiv_id: str) -> bool:
    forms = {arxiv_id, stored_name(arxiv_id), _base_id(arxiv_id), stored_name(_base_id(arxiv_id))}
    return any(re.search(r"(?<![\w.])" + re.escape(f) + r"(?![0-9])", text) for f in forms)


def _finding(rule: str, path: str, line: int | None, message: str, excerpt: str = "",
             severity: str = "warning") -> dict:
    return {"rule": rule, "severity": severity, "path": path.replace("\\", "/"), "line": line,
            "message": message, "excerpt": excerpt}


# Name-plus-id citations (MANIFEST §16.4, used by P005): a paragraph with a page locator that holds an arXiv id,
# or names a paper that a table row of the report pairs with an id.
PAGE_LOCATOR = re.compile(r"\(\s*pp?\.?\s*[0-9]+(?:\s*[,–-]\s*(?:pp?\.?\s*)?[0-9]+)*\s*\)"
                          r"|(?<![A-Za-z])pp?\.\s*[0-9]+")
BARE_ID = re.compile(r"(?<![0-9.])([0-9]{4}\.[0-9]{4,5})(?:v[0-9]+)?(?![0-9]|\.[0-9])")
_TABLE_RULE = re.compile(r"^\s*\|?\s*:?-{3,}")
_LIST_START = re.compile(r"^[ \t]*(?:[-*+•]|[0-9]{1,9}[.)])(?:[ \t]+|$)")
_MD_MARKUP = re.compile(r"\[([^\]]*)\]\([^)]*\)|[*_`]+")


def _ids_in(text: str) -> list[str]:
    """arXiv ids in text: `arXiv:` forms and bare new-style ids, in order, without versions."""
    found = [(m.start(), m.group(1)) for m in ARXIV_REF.finditer(text)]
    found += [(m.start(), m.group(1)) for m in BARE_ID.finditer(text)]
    out: list[str] = []
    for _, i in sorted(found):
        if i not in out:
            out.append(i)
    return out


def _table_cells(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", body)]


def _plain_cell(cell: str) -> str:
    return " ".join(_MD_MARKUP.sub(lambda m: m.group(1) or "", cell).split())


def _blocks(lines: list[str]) -> list[list[int]]:
    """Paragraphs as lists of 0-based line indexes; each list item and each table row is its own block."""
    blocks: list[list[int]] = []
    current: list[int] = []
    for k, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("|") or not stripped or MD_HEADING.match(line):
            if current:
                blocks.append(current)
            current = []
            if stripped.startswith("|") and not _TABLE_RULE.match(line):
                blocks.append([k])
            continue
        if _LIST_START.match(line) and current:
            blocks.append(current)
            current = []
        current.append(k)
    if current:
        blocks.append(current)
    return blocks


def named_citations(lines: list[str]) -> list[tuple[int, str]]:
    """(1-based line, arXiv id) for every name-plus-id citation with a page locator (MANIFEST §16.4).

    `lines` should already have fenced code blanked. Table rows that pair a name with 1 id define names; a
    paragraph (or table row) with a locator cites every id it holds and every paper it names."""
    names: dict[str, str] = {}
    for line in lines:
        if not line.lstrip().startswith("|") or _TABLE_RULE.match(line):
            continue
        cells = _table_cells(line)
        ids = {i for c in cells for i in _ids_in(c)}
        if len(ids) != 1:
            continue
        (only,) = ids
        for cell in cells:
            plain = _plain_cell(cell)
            if _ids_in(plain) or not re.search(r"[A-Za-z]{2}", plain) or len(plain) > 60:
                continue
            names.setdefault(plain, only)
    name_rx = [(re.compile(r"(?<!\w)" + re.escape(n) + r"(?!\w)"), i) for n, i in names.items()]

    cited: list[tuple[int, str]] = []
    for block in _blocks(lines):
        text = "\n".join(lines[k] for k in block)
        if not PAGE_LOCATOR.search(text):
            continue
        for k in block:
            cited += [(k + 1, i) for i in _ids_in(lines[k])]
            cited += [(k + 1, i) for rx, i in name_rx if rx.search(lines[k])]
    return cited


def _blank_fences(lines: list[str]) -> list[str]:
    out, fence = [], None
    for line in lines:
        m = _FENCE.match(line)
        if fence is not None:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
            out.append("")
        elif m:
            fence = m.group(1)
            out.append("")
        else:
            out.append(line)
    return out


def _has_heading(lines: list[str], heading: str) -> bool:
    """A heading counts when a line starts with it; `## How it works` also accepts any `## How ` heading."""
    if any(ln.startswith(heading) for ln in lines):
        return True
    if heading.strip() == "## How it works":
        return any(ln.startswith("## How ") for ln in lines)
    return False


def _check_profile(profile) -> dict[str, list[str]]:
    if profile is None:
        return {}
    if not isinstance(profile, dict):
        raise ToolError("profile must be an object mapping summary ids to lists of headings")
    out = {}
    for key, value in profile.items():
        if not isinstance(value, list) or not all(isinstance(h, str) and h.strip() for h in value):
            raise ToolError(f"profile[{key!r}] must be a list of non-empty heading strings")
        arxiv_id = id_from_stem(str(key)) or str(key)
        out[_base_id(arxiv_id)] = value
    return out


@tool(
    "papers_index_check",
    "Check a papers folder against its summaries: P001 a paper with no summaries/{id} - *.md, P002 a summary "
    "not mentioned in INDEX.md, P003 an INDEX.md 'N summaries' count that is wrong, P004 a summary missing one "
    "of the Summary / How ... / Results / Limitations / Relevance headings (profile maps a summary id to its "
    "own heading list), P006 no INDEX.md; with report, P005 an arXiv id cited in the report (references, or "
    "name + id with a page locator) that has no summary, and P007 (info) a report with no resolvable citations.",
    {"type": "object",
     "properties": {
         "dir": {"type": "string", "description": "papers directory (default: current directory)"},
         "index": {"type": "string", "description": "INDEX.md path (default {dir}/summaries/INDEX.md)"},
         "report": {"type": "string", "description": "a Markdown report whose citations are checked"},
         "profile": {"type": "object",
                     "additionalProperties": {"type": "array", "items": {"type": "string"}},
                     "description": "summary id -> required headings, overriding the default list"},
     },
     "additionalProperties": False},
    readOnlyHint=True,
)
def papers_index_check(dir: str | None = None, index: str | None = None, report: str | None = None,
                       profile: dict | None = None) -> dict:
    root = _paper_dir(dir)
    if not root.is_dir():
        raise ToolError(f"no such directory: {root}")
    profiles = _check_profile(profile)
    index_path = index if index is not None else str(root / "summaries" / "INDEX.md")
    index_shown = index if index is not None else "summaries/INDEX.md"
    index_text = read_input(index_path, "index") if os.path.lexists(index_path) else None
    report_text = read_input(report, "report") if report is not None else None

    papers = {}
    for p in sorted(root.iterdir()):
        arxiv_id = id_from_stem(p.stem) if p.suffix in (".pdf", ".txt") and p.is_file() else None
        if arxiv_id and (arxiv_id not in papers or p.suffix == ".txt"):
            papers[arxiv_id] = p.name
    summaries = []                                  # (file name, id)
    sdir = root / "summaries"
    if sdir.is_dir():
        for p in sorted(sdir.iterdir()):
            m = SUMMARY_FILE.fullmatch(p.name) if p.is_file() else None
            arxiv_id = id_from_stem(m.group(1)) if m else None
            if arxiv_id:
                summaries.append((p.name, arxiv_id))
    summarised = {_base_id(i) for _, i in summaries}

    findings = []
    if index_text is None:
        findings.append(_finding("P006", index_shown, None,
                                 f"{index_shown} is missing: the summaries have no index"))
    for arxiv_id, name in papers.items():
        if _base_id(arxiv_id) not in summarised:
            findings.append(_finding("P001", name, None, f"{arxiv_id} has no summary in summaries/"))
    for name, arxiv_id in summaries:
        shown = f"summaries/{name}"
        if index_text is not None and not _mentions(index_text, arxiv_id):
            findings.append(_finding("P002", shown, None, f"{arxiv_id} is not mentioned in {index_shown}"))
        try:
            lines = _read(sdir / name).split("\n")
        except OSError as exc:
            raise ToolError(f"cannot read {sdir / name}: {exc}") from None
        required = profiles.get(_base_id(arxiv_id), SUMMARY_HEADINGS)
        missing = [h for h in required if not _has_heading(lines, h)]
        if missing:
            findings.append(_finding("P004", shown, None, f"{arxiv_id} summary lacks " + ", ".join(missing)))
    for n, line in enumerate((index_text or "").split("\n"), 1):
        for m in INDEX_COUNT.finditer(line):
            if int(m.group(1)) != len(summaries):
                findings.append(_finding("P003", index_shown, n, f"{index_shown} says {m.group(1)} summaries, "
                                         f"but there are {len(summaries)} summary files", line.strip()[:80]))
    if report_text is not None:
        lines = _blank_fences(report_text.split("\n"))
        cited: list[tuple[int, str]] = []
        for n, (line, bucket) in enumerate(zip(lines, heading_buckets(lines)), 1):
            if bucket == "references":
                cited += [(n, m.group(1)) for m in ARXIV_REF.finditer(line)]
        cited += named_citations(lines)
        seen = set()
        for n, arxiv_id in sorted(cited):
            base = _base_id(arxiv_id)
            if base in seen or base in summarised:
                continue
            seen.add(base)
            findings.append(_finding("P005", report, n, f"{arxiv_id} is cited in the report but has no summary",
                                     lines[n - 1].strip()[:80]))
        if not cited:
            findings.append(_finding("P007", report, None, "no resolvable citations in the report: P005 needs "
                                     "[n] references with arXiv ids, or name + id citations with (pN) locators",
                                     severity="info"))
    findings.sort(key=lambda f: (f["path"], f["line"] or 0, f["rule"]))
    counts = {sev: sum(1 for f in findings if f["severity"] == sev) for sev in ("error", "warning", "info")}
    return {"ok": counts["error"] == 0, "findings": findings, "counts": counts, "papers": len(papers),
            "summaries": len(summaries)}


# ---------------------------------------------------------------------------------------------- CLI

def add_cli(groups) -> None:
    p = groups.add_parser("papers", help="fetch and read arXiv papers")
    cmds = p.add_subparsers(dest="command", required=True)

    c = cmds.add_parser("fetch", help="download PDFs and extract text")
    c.add_argument("ids", nargs="+", metavar="ID")
    c.add_argument("--dir")
    c.add_argument("--base-url", dest="base_url")
    c.add_argument("--delay", type=float, default=3)
    c.add_argument("--reextract", action="store_true", help="rewrite {id}.txt from the PDF even if it exists")
    common_flags(c)
    c.set_defaults(handler=_cli_fetch)

    c = cmds.add_parser("body", help="print the main body, 1 line per page")
    c.add_argument("id", metavar="ID")
    c.add_argument("--dir")
    c.add_argument("--start", type=int)
    c.add_argument("--end", type=int)
    c.add_argument("--max-chars", dest="max_chars", type=int, default=90000)
    c.add_argument("--appendix", action="store_true", help="default end is the last page, not the references")
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
    c.add_argument("--width", type=int, help="cut each hit to at most this many characters around the match")
    common_flags(c)
    c.set_defaults(handler=_cli_grep)

    c = cmds.add_parser("list", help="list papers in a directory")
    c.add_argument("--dir")
    common_flags(c)
    c.set_defaults(handler=_cli_list)

    c = cmds.add_parser("summary", help="draft a summary skeleton (INDEX format)")
    c.add_argument("id", metavar="ID")
    c.add_argument("--dir")
    c.add_argument("--short")
    c.add_argument("--write", action="store_true", help="write summaries/{id} - {short}.md")
    common_flags(c)
    c.set_defaults(handler=_cli_summary)

    c = cmds.add_parser("index-check", help="check summaries against papers and INDEX.md")
    c.add_argument("--dir")
    c.add_argument("--index")
    c.add_argument("--report")
    c.add_argument("--profile", metavar="JSON",
                   help="JSON object (or a file holding it): summary id -> list of required headings")
    common_flags(c, checker=True)
    c.set_defaults(handler=_cli_index_check)


def _cli_summary(args) -> CliResult:
    r = papers_summary(args.id, dir=args.dir, short=args.short, write=args.write)
    head = f"wrote {r['path']}" if r["written"] else f"would write {r['path']} (use --write)"
    return CliResult(r, f"{head}\n\n{r['text']}")


def _cli_index_check(args) -> CliResult:
    profile = None
    if args.profile is not None:
        import json

        text = args.profile
        if not text.lstrip().startswith("{") and Path(text).is_file():
            text = read_input(text, "profile")
        try:
            profile = json.loads(text)
        except ValueError as exc:
            raise ToolError(f"--profile is not valid JSON: {exc}") from None
    return CliResult(papers_index_check(dir=args.dir, index=args.index, report=args.report, profile=profile))


def _cli_fetch(args) -> CliResult:
    r = papers_fetch(args.ids, dir=args.dir, base_url=args.base_url, delay=args.delay,
                     reextract=args.reextract)
    lines = []
    for x in r["results"]:
        if x["status"] == "failed":
            lines.append(f"{x['id']}: FAILED {x['error']}")
        else:
            pages = f", {x['pages']} pages, {x['chars']} chars" if x["txt"] else ", no text"
            lines.append(f"{x['id']}: {x['status']}{pages}" + (f" ({x['warning']})" if x["warning"] else ""))
    return CliResult(r, "\n".join(lines))


def _cli_body(args) -> CliResult:
    r = papers_body(args.id, dir=args.dir, start=args.start, end=args.end, max_chars=args.max_chars,
                    appendix=args.appendix)
    head = (f"## {r['id']}: {r['pages']} pages, references at p{r['references_page']}, "
            f"showing p{r['start']}-p{r['end']}, {r['chars']} chars")
    tail = "\n[... truncated]" if r["truncated"] else ""
    warn = "".join(f"\nwarning: {w}" for w in r["warnings"])
    return CliResult(r, f"{head}\n{r['text']}{tail}{warn}")


def _cli_abs(args) -> CliResult:
    r = papers_peek(args.id, "abstract", dir=args.dir, chars=args.chars)
    return CliResult(r, f"### {r['id']}\n{r['abstract']}")


def _cli_grep(args) -> CliResult:
    r = papers_peek(args.id, "grep", dir=args.dir, pattern=args.pattern, context=args.context,
                    max_hits=args.max_hits, width=args.width)
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
             + ("  layout-text" if p["layout_text"] else "")
             + (f"  summary={p['summary']}" if p["summary"] else "") for p in r["papers"]]
    if r["missing_summary"]:
        lines.append("no summary: " + ", ".join(r["missing_summary"]))
    return CliResult(r, "\n".join(lines) or "no papers")
