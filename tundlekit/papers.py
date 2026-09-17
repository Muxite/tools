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


# Common English words (the ~600 most frequent, plus words common in paper titles). Used by the small-caps rule
# and the single-name-line rule (MANIFEST §17.4, §17.8).
COMMON_WORDS = frozenset("""
a able about above accept according account across act action activity actually add address administration admit
adult affect after again against age agency agent agents ago agree agreement ahead air all allow almost alone along
already also although always am american among amount analysis and animal another answer any anyone anything appear
apply approach area argue arm around arrive art article artist as ask assume at attack attention attorney audience
author authority available avoid away baby back bad bag ball bank bar base be beat beautiful because become bed
before begin behavior behind believe benefit best better between beyond big bill billion bit black blood blue board
body book born both box boy break bring brother budget build building business but buy by call camera campaign can
cancer candidate capital car card care career carry case catch cause cell center central century certain certainly
chair challenge chance change character charge check child choice choose church citizen city civil claim class clear
clearly close coach cold collection college color come commercial common community company compare computer concern
condition conference congress consider consumer contain continue control cost could country couple course court
cover create crime cultural culture cup current customer cut dark data daughter day dead deal death debate decade
decide decision deep defense degree democrat democratic describe design despite detail determine develop development
die difference different difficult dinner direction director discover discuss discussion disease do doctor dog door
down draw dream drive drop drug during each early east easy eat economic economy edge education effect effort eight
either election else employee end energy enjoy enough enter entire environment environmental especially establish
even evening event ever every everybody everyone everything evidence exactly example executive exist expect
experience expert explain eye face fact factor fail fall family far fast father fear federal feel feeling few field
fight figure fill film final finally financial find fine finger finish fire firm first fish five floor fly focus
follow food foot for force foreign forget form former forward four free friend from front full fund future game
garden gas general generation get girl give glass go goal good government great green ground group grow growth guess
gun guy hair half hand hang happen happy hard have he head health hear heart heat heavy help her here herself high
him himself his history hit hold home hope hospital hot hotel hour house how however huge human hundred husband i
idea identify if image imagine impact important improve in include including increase indeed indicate individual
industry information inside instead institution interest interesting international interview into investment
involve is issue it item its itself job join just keep key kid kill kind kitchen know knowledge land language large
last late later laugh law lawyer lay lead leader learn learning least leave left leg legal less let letter level lie
life light like likely line list listen little live local long look lose loss lot love low machine magazine main
maintain major majority make man manage management manager many market marriage material matter may maybe me mean
measure media medical meet meeting member memory mention message method middle might military million mind minute
miss mission model models modern moment money month more morning most mother mouth move movement movie mr mrs much
multi music must my myself name nation national natural nature near nearly necessary need network never new news
newspaper next nice night no none nor north not note nothing notice now number occur of off offer office officer
official often oh oil ok old on once one only onto open operation opportunity option or order organization other
others our out outside over own owner page pain painting paper parent part participant particular particularly
partner party pass past patient pattern pay peace people per perform performance perhaps period person personal
phone physical pick picture piece place plan plant play player pm point police policy political politics poor
popular population position positive possible power practice prepare present president pressure pretty prevent
price private probably problem process produce product production professional professor program project property
protect prove provide public pull purpose push put quality question quickly quite race radio raise range rate rather
reach read ready real reality realize really reason receive recent recently recognize record red reduce reflect
region relate relationship religious remain remember remove report represent republican require research resource
respond response responsibility rest result return reveal rich right rise risk road rock role room rule run safe
same save say scene school science scientist score sea season seat second section security see seek seem sell send
senior sense series serious serve service set seven several sex sexual shake share she shoot short shot should
shoulder show side sign significant similar simple simply since sing single sister sit site situation six size
skill skin small smile so social society soldier some somebody someone something sometimes son song soon sort sound
source south southern space speak special specific speech spend sport spring staff stage stand standard star start
state statement station stay step still stock stop store story strategy street strong structure student study stuff
style subject success successful such suddenly suffer suggest summer support sure surface survey system systems
table take talk task tax teach teacher team technology television tell ten tend term test than thank that the
their them themselves then theory there these they thing think third this those though thought thousand threat
three through throughout throw thus time to today together tonight too top total tough toward town trade
traditional training travel treat treatment tree trial trip trouble true truth try turn tv two type under
understand unit until up upon us use usually value various very via victim view violence visit voice vote wait walk
wall want war watch water way we weapon wear week weight well west western what whatever when where whether which
while white who whole whom whose why wide wife will win wind window wish with within without woman wonder word work
worker world worry would write writer wrong yard yeah year yes yet you young your yourself
aware based benchmark benchmarks efficient evaluation framework frameworks generative graph improving large
learn learned methods modeling neural novel open optimization planning reasoning reinforcement retrieval review
robust scalable self study survey systematic tool tools toward towards understanding using vision
scientific discovery autonomous agentic automated automatic research researcher researchers assistant
assistants scientist scientists semantic metrics convergence verification specification enforcement
reliable reliability trustworthy safe safety secure securing security scaling coding code software
engineering execution runtime workflow workflows pipeline pipelines evidence claims citation citations
harness harnesses benchmarking evaluating measuring towards generalist collaborative collaboration
multimodal interactive interpretability hypothesis generation driven deterministic formal provable
web are was were has had been does did done any can how its new two use via not may who why
""".split())

VENUE_LINE = re.compile(
    r"(?i)^(published (as|in)|accepted (at|to)|under review|preprint|arxiv:|proceedings of|workshop on"
    r"|language resources and evaluation)"
    r"|(?i:manuscript no\.|\(will be inserted by the editor\)|\btransactions on\b)"
    r"|^<?(?:https?://|www\.)\S+>?$"
    r"|^[\w.-]+\.(?:com|org|net|io|edu|ai|dev)(?:/\S*)?$"
    r"|^<?[^\s@]*@\S+>?$")
TITLE_WORDS = 20
# Author marks after a name: `Smith1,`, `Smith1 2`, `Smith* 1`, `Smith*1`, `Smith†`, superscript digits.
_DIGIT_MARK = re.compile(r"[a-z][0-9]{1,2}(?:\s*,\s*[0-9]{1,2})*(?=\s*(?:[,*∗†‡§]|$|\s[A-Z0-9]))")
_SINGLE_MARK = re.compile(r"\b[A-Z][a-z]+(?:[0-9](?![0-9A-Za-z]|\.[0-9])|[∗*†])")
_SYMBOL_MARK = re.compile(r"[A-Za-z]\s?[*∗†‡§]|[†‡]")
_SUPERSCRIPT_MARK = re.compile(r"[A-Za-z.][¹²³⁴⁵⁶⁷⁸⁹⁰]")
_AFFILIATION = re.compile(r"\bIndependent Researcher\b|\bUniversit(?:y|ies)\b|\bInstitute\b|\bInc\.|\bLabs?\b"
                          r"|\bLtd\.|\bCorp\.|\bLLC\b|\bLaborator(?:y|ies)\b|github\.com|\S*@")
_SUFFIX_AFFILIATION = re.compile(r"Inc\.|Ltd\.|Corp\.|Labs?|LLC")
_AUTHOR_MARK = re.compile(r"[∗*†‡§¹²³⁴⁵⁶⁷⁸⁹⁰,]|(?<=[A-Za-z.])[0-9]")
_ADDRESS_ONLY = re.compile(r"(?i)^<?(?:https?://|www\.)\S+>?$|^[\w.-]+\.(?:com|org|net|io|edu|ai|dev)(?:/\S*)?$"
                           r"|^<?[^\s@]*@\S+>?$")
_SECTION_START = re.compile(r"(?i)^(abstract|introduction|[0-9]+\.?\s+introduction)\b")
_UPPER = "".join(chr(c) for c in range(65, 0x250) if chr(c).isupper() and chr(c).isalpha())
_LOWER = "".join(chr(c) for c in range(97, 0x250) if chr(c).islower() and chr(c).isalpha())
_SMALL_CAPS = re.compile(rf"(?<![{_UPPER}{_LOWER}0-9])([{_UPPER}]) ([{_UPPER}]{{2,}})(?![{_LOWER}0-9])")
_RUNNING_HEADER = re.compile(r"^[A-Z][\w-]+ et al\. \(\d{4}\)\s*")
_MONTH = (r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sept?(?:ember)?"
          r"|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?")
_DATE_LINE = re.compile(rf"(?i)^(?:{_MONTH}\s+(?:\d{{1,2}}(?:st|nd|rd|th)?,?\s+)?\d{{4}}"
                        rf"|\d{{1,2}}\s+{_MONTH},?\s+\d{{4}})$")
_TRAILING_MARKS = re.compile(r"(?:\s*(?:\(Full\)|[⋆∗*]))+$")
_SPACED_BREAK = re.compile(r"([A-Za-z]+)(-\s+| - )([A-Z]?[a-z]+)\b")
_ORG_LINE = re.compile(r"\bTeam\b(?=\s*(?:$|[&,(]))|\bCo\.(?=[\s,]|$)|\bTechnologies\b|\bLaborator(?:y|ies)\b")
_SPACED_MARKS = re.compile(r"[a-z] [0-9]{1,2}(?= [A-Z]|$)")
_PAIR = r"[A-Z][a-z]+(?:-[A-Z]?[a-z]+)?"
_NAME_PAIRS = re.compile(rf"^{_PAIR}(?: {_PAIR}){{1,2}}(?:(?:\s*,\s*(?:and\s+)?|\s+and\s+){_PAIR}(?: {_PAIR}){{1,2}})+,?$")
_SPACED_HYPHEN = re.compile(r"(?<![A-Za-z])([A-Z]{2,}) -(?=[A-Z])")
_NAME_WORD = re.compile(r"(?:[A-Z][a-z]+['’]?(?:[-'’][A-Za-z][a-z]*)*|[A-Z]\.)")
_ENDS_WITH_CONNECTOR = re.compile(r"(?i)(?:[&\-–]|(?<![&/])\b(?:and|of|for|the|with|to|in|on|a|an|via|from))$")
_PUNCT_END = re.compile(r"[^\w\s]$")
_MINOR_WORDS = frozenset("a an the and but or nor for of in on at to by as via vs with from into onto upon per".split())


def _common(word: str) -> bool:
    w = word.lower().rstrip(".")
    return w in COMMON_WORDS or (len(w) > 3 and w.endswith("s") and w[:-1] in COMMON_WORDS)


def _name_line(line: str) -> bool:
    """A single name line (MANIFEST §17.8): 2-6 capitalised words, no all-caps word, no common word."""
    words = line.split()
    if not 2 <= len(words) <= 6:
        return False
    for w in words:
        if not _NAME_WORD.fullmatch(w):
            return False
        if w.lower().rstrip(".") in COMMON_WORDS:
            return False
    return any(len(w) > 2 for w in words)


def _name_pairs_line(line: str) -> bool:
    """2 or more capitalised name pairs separated by commas or `and` (MANIFEST §19.7)."""
    if not _NAME_PAIRS.match(line):
        return False
    return not any(_common(w) for w in re.findall(r"[A-Za-z]+", line) if w != "and")


def _author_line(line: str) -> bool:
    """An author or affiliation line: e-mail, author marks after names, a comma list of 3+ capitalised words,
    a single name line, or an affiliation word (MANIFEST §16.6, §17.4, §19.7)."""
    if "@" in line or _SYMBOL_MARK.search(line) or _SUPERSCRIPT_MARK.search(line) or _SINGLE_MARK.search(line):
        return True
    if _AFFILIATION.search(line) or _ORG_LINE.search(line):
        return True
    if "·" in line and re.search(r"[A-Z][a-z]+ [A-Z][a-z]+", line):
        return True
    marks = len(_DIGIT_MARK.findall(line))
    if marks >= 2 or (marks and "," in line) or len(_SPACED_MARKS.findall(line)) >= 2:
        return True
    if "," in line:
        words = re.findall(r"[A-Za-z][A-Za-z'’.-]*", line)
        caps = [w for w in words if w[0].isupper() and not w.isupper()]
        if len(caps) >= 3 and len(caps) * 3 >= len(words) * 2:
            return True
    return _name_line(line) or _name_pairs_line(line)


def rejoin_small_caps(text: str) -> str:
    """`A LITA -G` -> `ALITA-G`, `D EEP R ESEARCH` -> `DEEP RESEARCH`, `U SING` -> `USING`, `T HE` -> `THE`,
    but `A SURVEY` stays (MANIFEST §17.4, §19.7)."""
    text = _SPACED_HYPHEN.sub(r"\1-", text)

    def join(m: re.Match) -> str:
        x, r = m.group(1), m.group(2)
        joined = (x + r).lower()
        common_r = r.lower() in COMMON_WORDS
        if _common(joined) and not (x in "AIO" and common_r):
            return x + r
        if len(r) < 3 or common_r or (x in "AIO" and len(r) < 4):
            return m.group(0)
        return x + r

    return _SMALL_CAPS.sub(join, text)


def _acronym_like(token: str) -> bool:
    letters = re.sub(r"[^A-Za-z]", "", token)
    return 2 <= len(letters) <= 5 and sum(c.isupper() for c in letters) >= 2 and token.isalnum()


def _later_casing(word: str, later: str, hyphen: bool = False) -> str | None:
    """The most frequent mixed casing (`MetaGPT`, `DSPy`, `MLE-bench`, `AFlow`) of `word` in the later text,
    even when the upper-case spelling is more frequent (small caps in the PDF)."""
    edge = r"[\w-]" if hyphen else r"[^\W_]"
    counts: dict[str, int] = {}
    for m in re.finditer(rf"(?<!{edge}){re.escape(word)}(?!{edge})", later, re.I):
        found = m.group(0)
        if any(c.islower() for c in found) and any(c.isupper() for c in found[1:]):
            counts[found] = counts.get(found, 0) + 1
    return max(counts, key=lambda k: counts[k]) if counts else None


def _title_case(title: str, later: str) -> str:
    """An ALL-CAPS title in title case, keeping acronyms that the paper uses later and taking mixed casings
    (`MetaGPT`) from the later text (MANIFEST §17.4, §19.7)."""
    cache: dict[str, bool] = {}
    mixed_cache: dict[tuple[str, bool], str | None] = {}

    def mixed(word: str, hyphen: bool = False) -> str | None:
        if (word, hyphen) not in mixed_cache:
            mixed_cache[(word, hyphen)] = _later_casing(word, later, hyphen) if len(word) > 1 else None
        return mixed_cache[(word, hyphen)]

    def kept(part: str) -> bool:
        if part not in cache:
            cache[part] = (_acronym_like(part) and not _common(part)
                           and re.search(rf"(?<![\w-]){re.escape(part)}(?![\w-])", later) is not None)
        return cache[part]

    # running headers that repeat the title are not "later text"
    title_words = {w.lower() for w in re.findall(r"[^\W_]+", title)}
    later = "\n".join(ln for ln in later.split("\n")
                      if not (len(re.findall(r"[^\W_]+", ln)) >= 2
                              and {w.lower() for w in re.findall(r"[^\W_]+", ln)} <= title_words))
    tokens = re.findall(r"[^\W_]+", title)
    if not any(re.search("[A-Za-z]", t) for t in tokens if not kept(t)):
        return title
    if any(re.search("[a-z]", t) for t in tokens if not kept(t)):
        return title
    out, first = [], True
    for piece in re.split(r"(\s+)", title):
        if not piece or piece.isspace():
            out.append(piece)
            continue
        core = piece.strip(":;,.!?()[]\"'")
        casing = mixed(core, True) if "-" in core else None
        if casing:
            out.append(piece.replace(core, casing, 1))
        elif ("-" in core and not any(_common(w) for w in core.split("-"))
              and re.search(rf"(?<![\w-]){re.escape(core)}(?![\w-])", later)):
            # keep a whole hyphenated token (`ALITA-G`) when the paper writes it that way
            out.append(piece)
        else:
            parts = re.split(r"([-/])", piece)
            done = []
            for k, part in enumerate(parts):
                m = re.match(r"^([\W_]*)([^\W_]+)(.*)$", part)
                if not m:
                    done.append(part)
                    continue
                pre, word, post = m.groups()
                casing = mixed(word)
                if casing:
                    new = casing
                elif kept(word):
                    new = word
                elif word.lower() in _MINOR_WORDS and not first and k == 0:
                    new = word.lower()
                else:
                    new = word[:1].upper() + word[1:].lower()
                done.append(pre + new + post)
            out.append("".join(done))
        first = piece.rstrip().endswith(":")
    result = "".join(out)

    # `Alloc Bench` -> `AllocBench` when the paper writes the joined word
    def glue(m: re.Match) -> str:
        casing = mixed(m.group(1) + m.group(2))
        return casing if casing else m.group(0)

    return re.sub(r"(?<![\w-])([A-Z][a-z]+) ([A-Z][a-z]+)(?![\w-])", glue, result)


def _rejoin_breaks(title: str, later: str) -> str:
    """`Com- mercial` -> `Commercial`, `Alloca - Tion` -> `Allocation` (MANIFEST §19.7)."""
    low = later.lower()

    def seen(word: str) -> bool:
        return re.search(rf"(?<![\w-]){re.escape(word.lower())}(?![\w-])", low) is not None

    def fix(m: re.Match) -> str:
        left, sep, right = m.groups()
        title_case = right[:1].isupper()
        glued = left + (right.lower() if title_case else right)
        hyphened = f"{left}-{right}"
        if seen(hyphened) and not seen(glued):
            return hyphened
        if seen(glued):
            return glued
        if sep == " - ":
            return glued if not _common(right) or _common(glued) else m.group(0)
        if title_case:
            return hyphened
        if _common(right) and (left.isupper() or _common(left)) and not _common(glued):
            return hyphened
        return glued

    return _SPACED_BREAK.sub(fix, title)


def _clean_title(title: str) -> str:
    title = _RUNNING_HEADER.sub("", title)
    title = re.sub(r"\s+([:;,])", r"\1", title)
    return _TRAILING_MARKS.sub("", title).strip()


def _clean_authors(line: str) -> str:
    """Authors without marks, cut at the first affiliation word (MANIFEST §17.4)."""
    line = line.strip()
    if _ADDRESS_ONLY.match(line):                    # an e-mail or URL line after the title is the author line
        return line
    m = _AFFILIATION.search(line)
    if m:
        cut = m.start()
        if _SUFFIX_AFFILIATION.fullmatch(m.group(0)):
            # `Bo Li∗ Acme Inc.`: the organisation name goes too, back to the last author mark or comma (§17.8)
            marks = [k.end() for k in _AUTHOR_MARK.finditer(line, 0, cut)]
            if marks:
                cut = marks[-1]
        line = line[:cut]
    line = line.replace("·", ",")
    line = re.sub(r"[∗*†‡§⋆⋄¹²³⁴⁵⁶⁷⁸⁹⁰]", " ", line)
    line = re.sub(r"(?<=[A-Za-z.])[0-9]{1,2}(?:\s*,\s*[0-9]{1,2})*(?![0-9])", " ", line)
    line = re.sub(r"(?<![A-Za-z0-9])[0-9]{1,2}(?:\s*,\s*[0-9]{1,2})*(?![0-9A-Za-z])", " ", line)
    line = re.sub(r"\s*,(?:\s*,)*", ", ", line)
    line = " ".join(line.split())
    return line.strip(" ,")


def _run_line(text: str) -> bool:
    return 1 <= len(text.split()) <= 2


def _pick_authors(lines: list[str]) -> str:
    """The author line after the title: skips date lines and a leading e-mail line when a name line follows
    within 2 lines; never a section heading such as `Abstract` (MANIFEST §19.7)."""
    rest = [ln for ln in lines if ln and not _DATE_LINE.match(ln)]
    if not rest or _SECTION_START.match(rest[0]):
        return ""
    if _ADDRESS_ONLY.match(rest[0]):
        for ln in rest[1:3]:
            if _SECTION_START.match(ln):
                break
            clean = _clean_authors(ln)
            if "@" not in ln and clean and (_name_line(clean) or _name_pairs_line(clean)
                                            or (_author_line(ln) and not _AFFILIATION.search(ln))):
                return clean
    return _clean_authors(rest[0])


def _title_and_authors(page1: str, later: str = "") -> tuple[str, str]:
    """Title and author line of a paper's first page (MANIFEST §15.8, §16.6, §17.4, §19.7)."""
    lines = [_RUNNING_HEADER.sub("", ln.strip()) if _RUNNING_HEADER.match(ln.strip()) else ln.strip()
             for ln in page1.split("\n")]

    def skipped(text: str) -> bool:
        return not text or bool(VENUE_LINE.search(text) or _DATE_LINE.match(text))

    def cont(j: int, parts: list[str], words_limit: int = TITLE_WORDS) -> bool:
        if j >= len(lines):
            return False
        text = lines[j]
        if not text or VENUE_LINE.search(text) or _SECTION_START.match(text) or _DATE_LINE.match(text):
            return False
        if len(" ".join(parts).split()) >= words_limit:
            return False
        if _author_line(text):
            joined = " ".join(parts)
            strong = ("@" in text or _AFFILIATION.search(text) or _ORG_LINE.search(text)
                      or _SYMBOL_MARK.search(text) or _SINGLE_MARK.search(text) or _DIGIT_MARK.search(text)
                      or _SUPERSCRIPT_MARK.search(text) or "·" in text
                      or len(_SPACED_MARKS.findall(text)) >= 2)
            if strong:
                return False
            if joined.endswith(":") and not _name_line(text):
                return True
            return bool(_ENDS_WITH_CONNECTOR.search(joined) or joined.endswith(","))
        return True

    start = None
    run = False
    for i, text in enumerate(lines):
        if skipped(text):
            continue
        n = len(text.split())
        if n > 3:
            start = i
            break
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if _run_line(text) and nxt and (text.endswith(":") or not _PUNCT_END.search(text)) \
                and _run_line(nxt) and not _PUNCT_END.search(nxt) and cont(i + 1, [text]):
            start, run = i, True
            break
        if text.endswith(":") and n <= 2 and cont(i + 1, [text]):
            start = i
            break
        if n >= 2 and cont(i + 1, [text]):
            start = i
            break
    if start is None:
        return "", ""
    parts, last = [lines[start]], start
    j = start + 1
    if run:
        while (j < len(lines) and _run_line(lines[j]) and not _PUNCT_END.search(lines[j])
               and len(" ".join(parts + [lines[j]]).split()) <= TITLE_WORDS and cont(j, parts, TITLE_WORDS + 1)):
            parts.append(lines[j])
            last = j
            j += 1
    while cont(j, parts):
        parts.append(lines[j])
        last = j
        j += 1
    title = _clean_title(rejoin_small_caps(" ".join(" ".join(parts).split())))
    rest = "\n".join(lines[last + 1:]) + "\n" + later
    title = _clean_title(_rejoin_breaks(_title_case(title, rest), rest))
    return title, _pick_authors(lines[last + 1:])


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
    later = "\n".join(text for n, text in pairs if n != 1)
    title, authors = _title_and_authors(page1, later)
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


# ---------------------------------------------------------------------------------------------- paper page

# Cited ids (MANIFEST §18.3): new-style with a valid month, version dropped; old-style only after `arXiv:`/`arXiv `.
PAGE_NEW_ID = re.compile(r"(?<![0-9.])([0-9]{2}(?:0[1-9]|1[0-2])\.[0-9]{4,5})(?:v[0-9]+)?(?![0-9])")
PAGE_OLD_ID = re.compile(r"arXiv(?::[ \t]*| )([a-z-]+(?:\.[A-Z]{2})?/[0-9]{7})(?:v[0-9]+)?(?![0-9])")
# Ids in INDEX rows and report tables: new-style as above, old-style bare (or stored with `_`).
_ROW_OLD_ID = re.compile(r"(?<![\w/.-])([a-z-]+(?:\.[A-Z]{2})?)[/_]([0-9]{7})(?:v[0-9]+)?(?![0-9])")
_USED_FOR_PART = re.compile(r"\s*(?:([0-9]{2}(?:0[1-9]|1[0-2])\.[0-9]{4,5})"
                            r"|([a-z-]+(?:\.[A-Z]{2})?/[0-9]{7}))(?:v[0-9]+)?\s+\S")
INDEX_SECTION = re.compile(r"^##\s+\d+\.\s+(.*)$")
_INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`)")
_BULLET = re.compile(r"^(\s*)[-*]\s+(.*)$")
_PAGE_CANON = (("summary", "Summary"), ("how ", "How it works"), ("results", "Results"),
               ("limitations", "Limitations"), ("critical notes", "Limitations"), ("relevance", "Relevance"))
PAGE_TITLE = "Paper summaries"


def page_cited_ids(text: str) -> list[str]:
    """arXiv ids cited anywhere in text, first-seen order, deduplicated, versions dropped (MANIFEST §18.3)."""
    found = [(m.start(1), m.group(1)) for m in PAGE_NEW_ID.finditer(text)]
    found += [(m.start(1), m.group(1)) for m in PAGE_OLD_ID.finditer(text)]
    out: list[str] = []
    for _, i in sorted(found):
        if i not in out:
            out.append(i)
    return out


def _first_row_id(line: str) -> str | None:
    found = [(m.start(1), m.group(1)) for m in PAGE_NEW_ID.finditer(line)]
    found += [(m.start(), f"{m.group(1)}/{m.group(2)}") for m in _ROW_OLD_ID.finditer(line)]
    return min(found)[1] if found else None


def _esc(text: str) -> str:
    import html

    return html.escape(text)


def _inline_html(text: str) -> str:
    out = []
    for part in _INLINE.split(text):
        if not part:
            continue
        if len(part) > 4 and part.startswith("**") and part.endswith("**"):
            out.append("<strong>" + _esc(part[2:-2]) + "</strong>")
        elif len(part) > 2 and part.startswith("`") and part.endswith("`"):
            out.append("<code>" + _esc(part[1:-1]) + "</code>")
        else:
            out.append(_esc(part))
    return "".join(out)


def _page_cells(line: str) -> list[str]:
    return [c.replace("\\|", "|") for c in _table_cells(line)]


def _md_block(lines: list[str]) -> str:
    """Paragraphs, nested `-`/`*` bullets and pipe tables as HTML (MANIFEST §18.3)."""
    out: list[str] = []
    para: list[str] = []
    stack: list[int] = []                       # indents of the open <ul>s

    def flush_para():
        if para:
            out.append("<p>" + _inline_html(" ".join(para)) + "</p>")
            para.clear()

    def close_lists():
        while stack:
            out.append("</li></ul>")
            stack.pop()

    i = 0
    while i < len(lines):
        raw = lines[i]
        if (raw.strip().startswith("|") and i + 1 < len(lines) and lines[i + 1].strip().startswith(("|", ":", "-"))
                and re.fullmatch(r"\|?[\s:|-]+\|?", lines[i + 1].strip()) and "-" in lines[i + 1]):
            flush_para()
            close_lists()
            head = _page_cells(raw)
            j = i + 2
            body = []
            while j < len(lines) and lines[j].strip().startswith("|"):
                body.append(_page_cells(lines[j]))
                j += 1
            out.append('<div class="tbl"><table><thead><tr>'
                       + "".join(f"<th>{_inline_html(c)}</th>" for c in head) + "</tr></thead><tbody>")
            for row in body:
                out.append("<tr>" + "".join(f"<td>{_inline_html(c)}</td>" for c in row) + "</tr>")
            out.append("</tbody></table></div>")
            i = j
            continue
        i += 1
        m = _BULLET.match(raw)
        if m:
            flush_para()
            indent = len(m.group(1).expandtabs(4))
            if not stack or indent > stack[-1]:
                out.append("<ul><li>")
                stack.append(indent)
            else:
                while len(stack) > 1 and indent < stack[-1]:
                    out.append("</li></ul>")
                    stack.pop()
                out.append("</li><li>")
            out.append(_inline_html(m.group(2).strip()))
        elif not raw.strip():
            flush_para()
            close_lists()
        elif stack and raw[:1] in (" ", "\t"):
            out.append(" " + _inline_html(raw.strip()))
        else:
            close_lists()
            para.append(raw.strip())
    flush_para()
    close_lists()
    return "".join(out)


def _parse_summary(text: str, arxiv_id: str) -> dict:
    lines = text.replace("⭐ ", "").replace("⭐", "").split("\n")
    first = lines[0].lstrip("# ").strip() if lines else ""
    heading = re.sub(r"^" + re.escape(arxiv_id) + r"\s*[·:-]\s*", "", first)
    meta: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    for line in lines[1:]:
        if line.startswith("## "):
            sections.append((line[3:].strip(), []))
        elif sections:
            sections[-1][1].append(line)
        elif line.strip():
            meta.append(line.strip())
    keyed: dict[str, list[tuple[str, list[str]]]] = {}
    extra = []
    for label, body in sections:
        key = next((canon for prefix, canon in _PAGE_CANON if label.lower().startswith(prefix)), None)
        if key:
            keyed.setdefault(key, []).append((label, body))
        else:
            extra.append((label, body))
    return {"heading": heading, "meta": " ".join(meta), "keyed": keyed, "extra": extra}


def _card_html(arxiv_id: str, text: str, used_for: str | None) -> str:
    s = _parse_summary(text, arxiv_id)
    parts = [f'<article class="paper" id="p-{re.sub(r"[./]", "-", arxiv_id)}">',
             f'<h3><span class="id">{_esc(arxiv_id)}</span> {_esc(s["heading"])}</h3>']
    if used_for is not None:
        parts.append(f'<p class="eyebrow">In the report: {_inline_html(used_for)}</p>')
    if s["meta"]:
        parts.append(f'<p class="meta">{_inline_html(s["meta"])}</p>')
    for _, body in s["keyed"].get("Summary", []):
        parts.append('<div class="summary">' + _md_block(body) + "</div>")
    for key in ("How it works", "Results", "Limitations", "Relevance"):
        opened = " open" if key == "Results" else ""
        for label, body in s["keyed"].get(key, []):
            parts.append(f"<details{opened}><summary>{_esc(label)}</summary>{_md_block(body)}</details>")
    for label, body in s["extra"]:
        parts.append(f"<details><summary>{_esc(label)}</summary>{_md_block(body)}</details>")
    parts.append("</article>")
    return "\n".join(parts)


def _used_for(report_lines: list[str]) -> dict[str, str]:
    """{id: Used for cell} from the report's pipe tables with a `Used for` header cell; first occurrence wins."""
    lines = _blank_fences(report_lines)
    out: dict[str, str] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not (line.lstrip().startswith("|") and i + 1 < len(lines) and _TABLE_RULE.match(lines[i + 1])):
            i += 1
            continue
        header = [c.lower() for c in _page_cells(line)]
        col = header.index("used for") if "used for" in header else None
        j = i + 2
        while j < len(lines) and lines[j].lstrip().startswith("|"):
            cells = _page_cells(lines[j])
            if col is not None and col < len(cells):
                for k, cell in enumerate(cells):
                    if k == col:
                        continue
                    for part in cell.split(","):
                        m = _USED_FOR_PART.match(part)
                        if m:
                            out.setdefault(m.group(1) or m.group(2), cells[col])
            j += 1
        i = j
    return out


def _index_sections(index_text: str) -> tuple[list[str], dict[str, str]]:
    """(section names in first-appearance order, {id: section name}) from INDEX.md (MANIFEST §18.3)."""
    order: list[str] = []
    section_of: dict[str, str] = {}
    current = None
    for line in _blank_fences(index_text.split("\n")):
        m = INDEX_SECTION.match(line)
        if m:
            current = re.sub(r"\s*\([^()]*\)\s*$", "", m.group(1)).strip()
            if current not in order:
                order.append(current)
            continue
        if re.match(r"^##\s", line):
            current = None
            continue
        if current is not None and line.startswith("|"):
            found = _first_row_id(line)
            if found and found not in section_of:
                section_of[found] = current
    return order, section_of


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "group"


def _write_replace_atomic(target: Path, data: bytes) -> None:
    """Write target atomically, replacing an existing file (a build artifact)."""
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
        os.replace(tmp, target)
    except (OSError, ValueError) as exc:
        raise ToolError(f"cannot write {target}: {exc}") from None
    finally:
        _remove(Path(tmp))


PAGE_CSS = """
:root{
  --bg:#f7f6f3; --ink:#1c1b19; --ink-2:#4d4b47; --mute:#807d77; --rule:#cfccc5;
  --card:#ffffff; --code:#eeece6; --hi:#e6e3dc;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#181817; --ink:#e8e6e1; --ink-2:#c1beb7; --mute:#8f8c85; --rule:#3a3936;
    --card:#20201e; --code:#2a2a27; --hi:#2f2e2b;
  }
}
:root[data-theme="dark"]{
  --bg:#181817; --ink:#e8e6e1; --ink-2:#c1beb7; --mute:#8f8c85; --rule:#3a3936;
  --card:#20201e; --code:#2a2a27; --hi:#2f2e2b;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"Source Sans 3","Segoe UI",system-ui,Helvetica,Arial,sans-serif;
  font-size:15.5px;line-height:1.5;padding-block:32px 64px;padding-inline:clamp(16px,4vw,48px)}
.wrap{max-width:860px;margin:0 auto}
h1,h2,h3{font-family:"Source Serif 4",Georgia,"Times New Roman",serif;font-weight:600;text-wrap:balance;margin:0}
h1{font-size:2rem;line-height:1.15}
.lede{color:var(--ink-2);margin:8px 0 20px;max-width:65ch}
.controls{display:flex;flex-wrap:wrap;gap:12px 16px;align-items:center;
  border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);padding:12px 0;margin-bottom:28px}
input#q{flex:1 1 220px;min-width:0;font:inherit;padding:8px 10px;border:1px solid var(--rule);
  background:var(--card);color:var(--ink)}
input#q:focus{outline:2px solid var(--ink);outline-offset:1px}
nav{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:.9rem}
nav a{color:var(--ink-2);text-decoration:none;border-bottom:1px solid transparent}
nav a:hover,nav a:focus{border-bottom-color:var(--ink);color:var(--ink);outline:none}
nav .n{color:var(--mute);font-variant-numeric:tabular-nums}
.count{color:var(--mute);font-size:.9rem;font-variant-numeric:tabular-nums}
section.group{margin-top:36px}
section.group h2{font-size:1.25rem;letter-spacing:.01em;padding-bottom:6px;border-bottom:2px solid var(--ink);
  margin-bottom:16px}
.paper{background:var(--card);border:1px solid var(--rule);padding:18px 20px;margin-bottom:14px;overflow-wrap:anywhere}
.paper h3{font-size:1.1rem;line-height:1.3}
.paper .id{font-family:"JetBrains Mono",Consolas,ui-monospace,monospace;font-weight:500;
  font-size:.8em;color:var(--mute);font-variant-numeric:tabular-nums;margin-right:4px}
.eyebrow{margin:6px 0 0;font-size:.82rem;letter-spacing:.04em;text-transform:uppercase;color:var(--mute)}
.meta{margin:6px 0 10px;color:var(--ink-2);font-size:.9rem}
.summary p{margin:0 0 8px}
.summary ul{margin:0 0 8px}
details{border-top:1px solid var(--rule);padding:8px 0 4px}
details:last-child{padding-bottom:0}
summary{cursor:pointer;font-weight:600;font-size:.92rem;letter-spacing:.02em;color:var(--ink-2);list-style:none;
  display:flex;gap:8px;align-items:baseline}
summary::-webkit-details-marker{display:none}
summary::before{content:"+";font-family:ui-monospace,monospace;width:1em;color:var(--mute)}
details[open]>summary::before{content:"\\2013"}
summary:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
details p{margin:8px 0}
details ul,.summary ul{padding-left:1.2em}
details li,.summary li{margin:3px 0}
code{font-family:"JetBrains Mono",Consolas,ui-monospace,monospace;font-size:.86em;background:var(--code);padding:0 3px}
strong{font-weight:600}
.notice{border:1px solid var(--ink);padding:10px 14px;margin-bottom:20px}
.tbl{overflow-x:auto;margin:8px 0}
table{border-collapse:collapse;font-size:.9rem;font-variant-numeric:tabular-nums}
th,td{border:1px solid var(--rule);padding:4px 8px;text-align:left;vertical-align:top}
th{background:var(--hi);font-weight:600}
.hide{display:none}
.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
@media (max-width:480px){body{font-size:15px}.paper{padding:14px}}
"""

PAGE_JS = """
(function(){
  var q=document.getElementById('q'), count=document.getElementById('count'),
      papers=[].slice.call(document.querySelectorAll('article.paper')),
      groups=[].slice.call(document.querySelectorAll('section.group'));
  var texts=papers.map(function(p){return p.textContent.toLowerCase();});
  function run(){
    var v=q.value.trim().toLowerCase(), shown=0;
    papers.forEach(function(p,i){var ok=!v||texts[i].indexOf(v)>-1;p.classList.toggle('hide',!ok);if(ok)shown++;});
    groups.forEach(function(s){s.classList.toggle('hide',!s.querySelector('article.paper:not(.hide)'));});
    count.textContent=v?(shown+' of '+papers.length+' shown'):(papers.length+' papers');
  }
  q.addEventListener('input',run); run();
})();
"""


@tool(
    "papers_page",
    "Build a self-contained HTML page (no external requests, light/dark, inline filter) with 1 card per arXiv "
    "paper the report cites, from dir/summaries/{id} - *.md, grouped by the numbered sections of INDEX.md "
    "(others under 'Other'), with an 'In the report' line from the report's 'Used for' table column. Cited ids "
    "without a summary are listed and warned about. Overwrites out (a build artifact); output is deterministic.",
    {"type": "object",
     "properties": {
         "report": {"type": "string", "description": "the Markdown report whose cited papers get cards"},
         "out": {"type": "string", "description": "output HTML file (its directory must exist)"},
         "dir": {"type": "string", "description": "papers directory holding summaries/ (default: current directory)"},
         "index": {"type": "string", "description": "INDEX.md path (default {dir}/summaries/INDEX.md)"},
         "title": {"type": "string", "description": "page title (default 'Paper summaries')"},
     },
     "required": ["report", "out"],
     "additionalProperties": False},
    readOnlyHint=False,
)
def papers_page(report: str, out: str, dir: str | None = None, index: str | None = None,
                title: str | None = None) -> dict:
    from tundlekit.render import check_path_string

    check_path_string(out, "out")
    report_text = read_input(report, "report")
    root = _paper_dir(dir)
    if not root.is_dir():
        raise ToolError(f"no such directory: {root}")
    target = Path(out)
    if not target.parent.is_dir():
        raise ToolError(f"the directory of out does not exist: {target.parent}")
    if target.is_dir():
        raise ToolError(f"out is a directory: {out}")
    title = PAGE_TITLE if title is None else title
    warnings: list[str] = []

    index_path = index if index is not None else str(root / "summaries" / "INDEX.md")
    if Path(index_path).is_file():
        order, section_of = _index_sections(read_input(index_path, "index"))
    else:
        order, section_of = [], {}
        warnings.append(f"no index: {index_path}")

    cited = page_cited_ids(report_text)
    used_for = _used_for(report_text.split("\n"))
    sdir = root / "summaries"
    cards: dict[str, str] = {}
    missing: list[str] = []
    for arxiv_id in cited:
        found = (sorted(sdir.glob(glob_escape(stored_name(arxiv_id)) + " - *.md"), key=lambda p: p.name)
                 if sdir.is_dir() else [])
        found = [p for p in found if p.is_file()]
        if not found:
            missing.append(arxiv_id)
            warnings.append(f"no summary for {arxiv_id}")
            continue
        cards[arxiv_id] = _card_html(arxiv_id, read_input(str(found[0]), "summary"), used_for.get(arxiv_id))

    grouped: dict[str, list[str]] = {}
    for arxiv_id in cards:
        grouped.setdefault(section_of.get(arxiv_id, "Other"), []).append(arxiv_id)
    names = [n for n in order if n != "Other"] + ["Other"]
    sections, nav, body = [], [], []
    used_slugs: dict[str, int] = {}
    for name in names:
        ids = grouped.get(name)
        if not ids:
            continue
        slug = _slug(name)
        used_slugs[slug] = used_slugs.get(slug, 0) + 1
        sid = "s-" + (slug if used_slugs[slug] == 1 else f"{slug}-{used_slugs[slug]}")
        sections.append({"name": name, "id": sid, "papers": list(ids)})
        nav.append(f'<a href="#{sid}">{_esc(name)} <span class="n">{len(ids)}</span></a>')
        body.append(f'<section class="group" id="{sid}"><h2>{_esc(name)}</h2>\n'
                    + "\n".join(cards[i] for i in ids) + "\n</section>")

    n = len(cards)
    lines = ["<!doctype html>",
             '<html lang="en"><head><meta charset="utf-8">'
             '<meta name="viewport" content="width=device-width, initial-scale=1">',
             f"<title>{_esc(title)}</title><style>{PAGE_CSS}</style></head>",
             '<body><div class="wrap">',
             f"<h1>{_esc(title)}</h1>",
             f'<p class="lede">{n} papers cited in {_esc(Path(report).name)}, 1 card each, '
             f"grouped as in the summary index.</p>"]
    if missing:
        lines.append('<div class="notice" id="missing"><strong>No summary on file for:</strong> '
                     + _esc(", ".join(missing)) + ". These are cited in the report but not summarised, "
                     "so they have no card.</div>")
    lines += ['<div class="controls"><label class="sr-only" for="q">Filter</label>'
              '<input id="q" type="search" placeholder="filter by any word, number or id" autocomplete="off">'
              '<span class="count" id="count"></span>',
              "<nav>" + "".join(nav) + "</nav></div>"]
    lines += body
    lines.append(f"</div><script>{PAGE_JS}</script></body></html>")
    _write_replace_atomic(target, ("\n".join(lines) + "\n").encode("utf-8"))
    return {"out": out, "papers": n, "cited": cited, "missing": missing, "sections": sections,
            "warnings": warnings}


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

    c = cmds.add_parser("page", help="build an HTML page of the summaries of the papers a report cites")
    c.add_argument("report", metavar="REPORT.md")
    c.add_argument("-o", "--out", required=True, metavar="OUT.html")
    c.add_argument("--dir")
    c.add_argument("--index")
    c.add_argument("--title")
    common_flags(c, checker=True)
    c.set_defaults(handler=_cli_page)


def _cli_page(args) -> CliResult:
    r = papers_page(args.report, args.out, dir=args.dir, index=args.index, title=args.title)
    lines = [f"wrote {r['out']}: {r['papers']} papers in {len(r['sections'])} sections"]
    lines += [f"warning: {w}" for w in r["warnings"]]
    return CliResult(r, "\n".join(lines), exit_code=1 if args.strict and r["warnings"] else 0)


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
