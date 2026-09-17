"""Claim tracing: cited numbers to source pages (MANIFEST.md §15.3).

Every sentence in a report's body that cites a reference `[n]` and states a number is checked against the text of
the cited arXiv papers (fetched with `tundlekit papers fetch`), page by page. Numbers that no page shows can be
backed by a ledger of verified numbers instead.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path

from tundlekit.cli_support import CliResult, common_flags
from tundlekit.papers import ARXIV_REF, MD_HEADING, heading_buckets, read_input, split_pages, stored_name
from tundlekit.registry import ToolError, tool
from tundlekit.textlint import native_path, path_key

STATUSES = ("located", "derived", "ledgered", "untraced", "no_source")
EXCERPT_WIDTH = 80
WEAK_PAGES = 5

# ---------------------------------------------------------------------------------------------- masking

_FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})")
_INLINE_CODE = re.compile(r"(`+)(?!`).+?(?<!`)\1(?!`)")
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
_URL = re.compile(r"https?://[^\s<>\"'`)\]]+")
_LINK_TARGET = re.compile(r"\]\([^()\n]*\)")


def _blank(m: re.Match) -> str:
    return re.sub(r"[^\n]", " ", m.group(0))


def _mask(text: str) -> list[str]:
    """Lines with fenced code, inline code, HTML comments, URLs and link targets blanked (columns kept)."""
    text = _HTML_COMMENT.sub(_blank, text)
    lines, fence = [], None
    for line in text.split("\n"):
        m = _FENCE.match(line)
        if fence is not None:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
            lines.append("")
            continue
        if m:
            fence = m.group(1)
            lines.append("")
            continue
        line = _INLINE_CODE.sub(_blank, line)
        line = _URL.sub(_blank, line)
        lines.append(_LINK_TARGET.sub(lambda mm: "]" + " " * (len(mm.group(0)) - 1), line))
    return lines


# ---------------------------------------------------------------------------------------------- sentences

_LIST_ITEM = re.compile(r"^[ \t]*(?:[-*+•]|\d{1,9}[.)])(?:[ \t]+|$)")
_TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}")
_SENTENCE_END = re.compile(r"[.!?]+[\"'”’)\]]*(?=\s|$)")
ABBREVIATIONS_ANY_CASE = ("e.g.", "i.e.", "vs.", "approx.", "cf.", "et al.")
ABBREVIATIONS_EXACT = ("Fig.", "Eq.", "No.", "App.", "Tab.", "Sec.", "Ref.", "Refs.")


def _paragraphs(lines: list[str], keep) -> list[list[int]]:
    """Groups of 0-based line indexes: consecutive prose lines; each list item starts its own paragraph."""
    paras: list[list[int]] = []
    current: list[int] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        prose = (keep(i) and stripped and not MD_HEADING.match(line) and not stripped.startswith("|")
                 and not _TABLE_SEPARATOR.match(line) and not re.fullmatch(r"[-*_ ]{3,}", stripped))
        if not prose:
            if current:
                paras.append(current)
            current = []
            continue
        if _LIST_ITEM.match(line) and current:
            paras.append(current)
            current = []
        current.append(i)
    if current:
        paras.append(current)
    return paras


def _is_abbreviation(text: str, end: int) -> bool:
    """Whether the `.` just before `end` ends an abbreviation (or is a decimal point)."""
    head = text[:end]
    for abbr in ABBREVIATIONS_EXACT:
        if head.endswith(abbr) and (len(head) == len(abbr) or not head[-len(abbr) - 1].isalnum()):
            return True
    low = head.lower()
    for abbr in ABBREVIATIONS_ANY_CASE:
        if re.search(r"(?<![A-Za-z])" + re.escape(abbr).replace(r"\ ", r"\s+") + r"$", low):
            return True
    return False


def _own_sentence_ends(text: str) -> list[int]:
    """Offsets just after each sentence end in 1 paragraph (§7.1 with the §15 pins, never inside `[...]`)."""
    ends, depth, pos = [], 0, 0
    while pos < len(text):
        ch = text[pos]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth = max(0, depth - 1)
        elif ch in ".!?" and depth == 0:
            m = _SENTENCE_END.match(text, pos)
            if m:
                if not (ch == "." and _is_abbreviation(text, pos + 1)):
                    ends.append(m.end())
                pos = m.end()
                continue
        pos += 1
    return ends


def split_sentences(text: str) -> list[tuple[int, int]]:
    """(start, end) offsets of the sentences in 1 paragraph.

    Uses textlint's splitter when it provides one, so text_lint and claims_trace agree on sentences.
    """
    try:
        from tundlekit.textlint import sentence_ends
    except ImportError:
        sentence_ends = _own_sentence_ends
    spans, start = [], 0
    ends = [e for e in sentence_ends(text)                  # a page locator `p. 3` does not end a sentence
            if not (re.search(r"(?<![\w.])pp?\.$", text[:e].rstrip("\"'”’)]"))
                    and re.match(r"\s*\d", text[e:]))]
    for end in [*ends, len(text)]:
        if end > start and text[start:end].strip():
            spans.append((start, end))
        start = max(start, end)
    return spans


# ---------------------------------------------------------------------------------------------- numbers

CITATION = re.compile(r"\[\s*(\d+)\s*((?:,[^\[\]]*)?)\]")
NUMBER = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)*%?")
EXCLUDED_PREFIX = re.compile(r"(?:§|\bFig\.|\bTable|\bApp\.|\barXiv:?|(?i:\bSection|\bSec\.|\bEq\.|\bEquation|\bStep"
                             r"|\bPhase|\bLevel)|\b[RCS])\s*$")
YEAR = re.compile(r"(?:19|20)\d\d")
BARE_ID = r"\d{4}\.\d{4,5}(?:v\d+)?"
PAREN_ID = re.compile(r"\(\s*(?:arXiv:?\s*)?(" + BARE_ID + r")\s*\)", re.IGNORECASE)
ARXIV_ID = re.compile(r"\barXiv(?::\s*|\s+)(" + BARE_ID + r")(?![\d.])", re.IGNORECASE)
ANY_ID = re.compile(r"(?<![\w.])(" + BARE_ID + r")(?![\w]|\.\d)")
PAGE_PAREN = re.compile(r"\(\s*(pp?\.?\s?\d+(?:\s*[-–]\s*\d+)?(?:\s*,\s*pp?\.?\s?\d+(?:\s*[-–]\s*\d+)?)*)\s*\)")
PAGE_DOT = re.compile(r"(?<![\w.])pp?\.\s?(\d+)(?:\s*[-–]\s*(\d+))?")
PAGE_NUMBERS = re.compile(r"pp?\.?\s?(\d+)(?:\s*[-–]\s*(\d+))?")
LOCATOR_KIND = re.compile(r"\b(Table|Tab\.|Fig\.|Figure)\s?([A-Z]?\d+)\b")
LIST_MARKER = re.compile(r"^([ \t]*(?:[-*+•]|\d{1,9}[.)]))(?=[ \t]|$)")
MAX_RANGE = 50


def _strip_id(arxiv_id: str) -> str:
    return re.sub(r"v\d+$", "", arxiv_id)


def _pages_in(text: str) -> list[int]:
    pages = []
    for m in PAGE_NUMBERS.finditer(text):
        first = int(m.group(1))
        last = int(m.group(2)) if m.group(2) else first
        if last < first or last - first > MAX_RANGE:
            last = first
        pages += [n for n in range(first, last + 1) if n not in pages]
    return pages


@dataclass
class _Locator:
    pages: list = field(default_factory=list)       # stated pages
    items: list = field(default_factory=list)       # (kind, id) such as ("Table", "6")

    def add(self, other: "_Locator") -> None:
        self.pages += [p for p in other.pages if p not in self.pages]
        self.items += [i for i in other.items if i not in self.items]

    def __bool__(self) -> bool:
        return bool(self.pages or self.items)


def _bracket_locator(extra: str) -> _Locator:
    """Locator parts of a citation bracket after its number: `Table 6`, `Fig. 2`, `p. 4`."""
    loc = _Locator()
    for m in LOCATOR_KIND.finditer(extra):
        kind = "Table" if m.group(1).startswith("Tab") else "Fig"
        if (kind, m.group(2)) not in loc.items:
            loc.items.append((kind, m.group(2)))
    for m in re.finditer(r"(?<![\w.])pp?\.?\s?\d+(?:\s*[-–]\s*\d+)?", extra):
        loc.pages += [p for p in _pages_in(m.group(0)) if p not in loc.pages]
    return loc


def _blank_span(text: str, start: int, end: int) -> str:
    return text[:start] + " " * (end - start) + text[end:]


@dataclass
class _Sentence:
    start: int
    text: str                                        # masked: citations, ids and locators blanked
    cited: list
    ids: list
    locator: _Locator


def _analyse(sentence: str) -> _Sentence:
    """Citations, ids and locators of 1 sentence, with their text blanked."""
    cited: list[int] = []
    ids: list[str] = []
    loc = _Locator()
    text = sentence
    for m in list(CITATION.finditer(text)):
        nums = [m.group(1)] + [p.strip() for p in m.group(2).split(",")[1:]]
        for n in nums:
            if n.isdigit() and int(n) not in cited:
                cited.append(int(n))
        loc.add(_bracket_locator(m.group(2)))
        text = _blank_span(text, m.start(), m.end())
    for pattern in (PAREN_ID, ARXIV_ID):
        for m in list(pattern.finditer(text)):
            ident = _strip_id(m.group(1))
            if ident not in ids:
                ids.append(ident)
            text = _blank_span(text, m.start(), m.end())
    for m in list(PAGE_PAREN.finditer(text)):
        loc.pages += [p for p in _pages_in(m.group(1)) if p not in loc.pages]
        text = _blank_span(text, m.start(), m.end())
    for m in list(PAGE_DOT.finditer(text)):
        loc.pages += [p for p in _pages_in(m.group(0)) if p not in loc.pages]
        text = _blank_span(text, m.start(), m.end())
    return _Sentence(0, text, cited, ids, loc)


def _numbers(masked: str, known_ids: set) -> list[tuple[int, str]]:
    for m in list(ANY_ID.finditer(masked)):
        if _strip_id(m.group(1)) in known_ids:
            masked = _blank_span(masked, m.start(), m.end())
    found, seen = [], set()
    for m in NUMBER.finditer(masked):
        token = m.group(0)
        if EXCLUDED_PREFIX.search(masked[:m.start()]):
            continue
        plain = token.replace(",", "")
        if not token.endswith("%") and plain.isdigit() and (len(plain) == 1 or YEAR.fullmatch(plain)):
            continue
        if token not in seen:
            seen.add(token)
            found.append((m.start(), token))
    return found


def _alternatives(token: str) -> list[str]:
    core = token.rstrip("%").replace(",", "")
    alts = [re.escape(core)]
    if token.endswith("%"):
        try:
            fraction = format((Decimal(core) / 100).normalize(), "f")
        except InvalidOperation:
            fraction = ""
        if "." in fraction:
            alts.append(re.escape(fraction) + "0*")          # §16.4: 50% <-> 0.5, 0.50
    return alts


def _matcher(alternatives: list[str]) -> re.Pattern:
    return re.compile(r"(?<![\d.])(?:" + "|".join(alternatives) + r")(?!\d)(?!\.\d)")


def _is_weak(token: str, pages: list[int]) -> bool:
    plain = token.replace(",", "")
    small_integer = not token.endswith("%") and plain.isdigit() and int(plain) < 1000
    return small_integer or len(pages) >= WEAK_PAGES


def _locator_match(pages: list[int], texts: dict[int, str], loc: _Locator) -> bool:
    if any(p in loc.pages for p in pages):
        return True
    for kind, ident in loc.items:
        rx = re.compile(r"\bTable\s*" + re.escape(ident) + r"(?![\w]|\.\d)" if kind == "Table"
                        else r"\bFig(?:\.|ure)\s*" + re.escape(ident) + r"(?![\w]|\.\d)")
        if any(rx.search(texts.get(p, "")) for p in pages):
            return True
    return False


# ---------------------------------------------------------------------------------------------- sources

class _Papers:
    """Page texts of cited papers, read once each, with commas removed."""

    def __init__(self, folder: Path):
        self.folder = folder
        self.cache: dict[str, list[tuple[int, str]] | None] = {}

    def pages(self, arxiv_id: str) -> list[tuple[int, str]] | None:
        if arxiv_id not in self.cache:
            path = self.folder / (stored_name(arxiv_id) + ".txt")
            pages = None
            if path.is_file():
                text = read_input(str(path), "paper text")
                pages = [(n, body.replace(",", "")) for n, body in split_pages(text)]
            self.cache[arxiv_id] = pages
        return self.cache[arxiv_id]


REFERENCE_LINE = re.compile(r"^\s*(?:[-*+]\s+|\d{1,9}[.)]\s+)?\[(\d+)\]")


def reference_list(lines: list[str], buckets: list[str]) -> dict[int, str | None]:
    """{n: arXiv id or None} for `[n] ...` and `- [n] ...` entries in the references bucket (§15.3, §16.4)."""
    entries: dict[int, list[str]] = {}
    current = None
    for line, bucket in zip(lines, buckets):
        if bucket != "references":
            current = None
            continue
        m = REFERENCE_LINE.match(line)
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
        refs[n] = _strip_id(m.group(1)) if m else None
    return refs


NAME_BEFORE_ID = re.compile(r"([A-Z][\w.+-]*(?:[ \t]+[A-Z][\w.+-]*)*)[ \t]*\(\s*(?:arXiv:?\s*)?(" + BARE_ID + r")\s*\)")
NAME_WORD = re.compile(r"[A-Za-z][\w.+-]*")


def _table_cells(line: str) -> list[str]:
    body = line.strip()
    body = body[1:] if body.startswith("|") else body
    body = body[:-1] if body.endswith("|") else body
    return [c.strip() for c in re.split(r"(?<!\\)\|", body)]


def table_names(lines: list[str]) -> dict[str, str]:
    """{name: arXiv id} from table cells that pair a name with an id (`2511.02824 Kosmos`) (§16.4)."""
    names: dict[str, str] = {}
    for line in lines:
        if not line.lstrip().startswith("|"):
            continue
        for cell in _table_cells(line):
            m = ANY_ID.search(cell) or ARXIV_ID.search(cell)
            if not m:
                continue
            rest = cell[:m.start()] + " " + cell[m.end():]
            rest = re.sub(r"(?i)\barxiv:?", " ", rest)
            rest = re.sub(r"[*_`()\[\],;:]", " ", rest)
            name = " ".join(rest.split())
            if name and NAME_WORD.match(name):
                names.setdefault(name, _strip_id(m.group(1)))
    return names


def _ids_named(text: str, names: dict[str, str]) -> list[str]:
    ids = []
    for name, ident in names.items():
        if re.search(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", text) and ident not in ids:
            ids.append(ident)
    return ids


# ---------------------------------------------------------------------------------------------- ledger

def _ledger_rows(text: str) -> list[tuple[list[str], bool]]:
    rows = []
    for line in text.split("\n"):
        s = line.strip()
        if not s.startswith("|") or set(s) <= set("|-: "):      # not a row, or the separator row
            continue
        cells = [re.sub(r"^[*_`]+|[*_`]+$", "", c.strip()).strip().replace(",", "")
                 for c in s.strip("|").split("|")]
        rows.append((cells, "derived" in s.lower()))
    return rows


def _ledger_status(token: str, rows) -> str | None:
    rx = _matcher([re.escape(token.rstrip("%").replace(",", ""))])
    hits = [derived for cells, derived in rows if any(rx.search(c) for c in cells)]
    if not hits:
        return None
    return "derived" if any(hits) else "ledgered"


# ---------------------------------------------------------------------------------------------- units

@dataclass
class _Unit:
    """A piece of text checked as 1 block: a prose paragraph (split into sentences) or 1 table row."""
    line_of: object                 # offset -> 1-based line
    text: str
    sentences: list                 # [(start, end)]
    table: bool = False
    inherited: object = None        # _Sentence from a table caption or header row


def _is_table_line(line: str) -> bool:
    return line.lstrip().startswith("|")


def _is_separator(line: str) -> bool:
    return bool(re.fullmatch(r"\s*\|?[\s:|-]*-[\s:|-]*\|?\s*", line))


CAPTION = re.compile(r"^(?:\*\*|\*|_)?(?:Table|Fig\.)\s?[A-Z]?\d+\.")


def _cites(sentence: _Sentence) -> bool:
    return bool(sentence.cited or sentence.ids)


def _table_units(lines: list[str], keep) -> list[_Unit]:
    """Rows of tables (in kept lines) whose caption or header row cites a paper (§16.4)."""
    units = []
    n = len(lines)
    i = 0
    while i < n:
        if not (keep(i) and _is_table_line(lines[i])):
            i += 1
            continue
        start = i
        while i < n and keep(i) and _is_table_line(lines[i]):
            i += 1
        end = i                                                       # rows start..end-1
        caption = None
        k = start - 1
        while k >= 0 and not lines[k].strip():
            k -= 1
        if k >= 0 and CAPTION.match(lines[k].strip()):
            j = k - 1
            while j >= 0 and not lines[j].strip():
                j -= 1
            if j < 0 or not _is_table_line(lines[j]):
                caption = lines[k]
        k = end
        while k < n and not lines[k].strip():
            k += 1
        if caption is None and k < n and CAPTION.match(lines[k].strip()):
            caption = lines[k]
        source = _analyse(caption or "")
        header = _analyse(lines[start])
        source.cited += [c for c in header.cited if c not in source.cited]
        source.ids += [c for c in header.ids if c not in source.ids]
        source.locator.add(header.locator)
        if not _cites(source):
            continue
        body_start = start + 1
        if body_start < end and _is_separator(lines[body_start]):
            body_start += 1
        for r in range(body_start, end):
            if _is_separator(lines[r]):
                continue
            row = " " + " | ".join(_table_cells(lines[r]))
            units.append(_Unit(lambda _o, r=r: r + 1, row, [(0, len(row))], True, source))
    return units


def _prose_units(lines: list[str], keep) -> list[_Unit]:
    units = []
    for para in _paragraphs(lines, keep):
        starts, joined = [], ""
        for i in para:
            starts.append(len(joined))
            marker = LIST_MARKER.match(lines[i])
            line = lines[i]
            if marker:
                line = " " * marker.end() + line[marker.end():]
            joined += line + "\n"
        joined = joined[:-1]

        def line_of(offset: int, starts=starts, para=para) -> int:
            k = max(j for j, s in enumerate(starts) if s <= offset)
            return para[k] + 1

        units.append(_Unit(line_of, joined, split_sentences(joined)))
    return units


# ---------------------------------------------------------------------------------------------- tracing

def _excerpt(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= EXCERPT_WIDTH else text[:EXCERPT_WIDTH - 1] + "…"


@dataclass
class _Context:
    refs: dict
    names: dict
    known_ids: set
    papers: "_Papers"
    ledger: list


def _claims_in_unit(shown: str, unit: _Unit, ctx: _Context) -> list[dict]:
    analysed = []
    for s, e in unit.sentences:
        a = _analyse(unit.text[s:e])
        a.start = s
        analysed.append(a)
    para_cited, para_ids, para_loc = [], [], _Locator()
    for a in analysed:
        para_cited += [c for c in a.cited if c not in para_cited]
        para_ids += [i for i in a.ids if i not in para_ids]
        para_loc.add(a.locator)
    inherited = unit.inherited
    named = [] if unit.table else _ids_named(unit.text, ctx.names)
    claims = []
    for a in analysed:
        numbers = _numbers(a.text, ctx.known_ids)
        if not numbers:
            continue
        loc = _Locator()
        if a.cited:
            cited, ids = a.cited, []
            loc.add(a.locator)
        elif para_cited:
            cited, ids = para_cited, []
            loc.add(a.locator if a.locator else para_loc)
        elif inherited is not None:
            cited, ids = list(inherited.cited), list(inherited.ids)
            loc.add(a.locator)
            loc.add(inherited.locator)
        elif para_loc.pages and (para_ids or named):
            cited = []
            ids = list(para_ids) + [i for i in named if i not in para_ids]
            loc.add(a.locator if a.locator.pages else para_loc)
        else:
            continue
        papers = []
        for n in cited:
            if ctx.refs.get(n) and ctx.refs[n] not in papers:
                papers.append(ctx.refs[n])
        papers += [i for i in ids if i not in papers]
        sources = [(i, ctx.papers.pages(i)) for i in papers]
        sources = [(i, p) for i, p in sources if p is not None]
        lead = len(a.text) - len(a.text.lstrip())
        line = unit.line_of(a.start + lead)
        for pos, token in numbers:
            rx = _matcher(_alternatives(token))
            texts: dict[int, str] = {}
            for _, pp in sources:
                for n, body in pp:
                    if rx.search(body):
                        texts[n] = texts.get(n, "") + "\n" + body
            pages = sorted(texts)
            weak = match = False
            if pages:
                status = "located"
                weak = _is_weak(token, pages)
                match = _locator_match(pages, texts, loc)
            else:
                status = _ledger_status(token, ctx.ledger) or ("untraced" if sources else "no_source")
            claims.append({"path": shown, "line": line, "number": token, "citations": list(cited),
                           "papers": papers, "status": status, "pages": pages,
                           "stated_pages": sorted(loc.pages), "weak": weak, "locator_match": match,
                           "_order": (line, a.start + pos), "_sentence": unit.text[a.start:a.start + len(a.text)]})
    return claims


def _trace_file(shown: str, text: str, ctx: _Context) -> list[dict]:
    lines = _mask(text)
    buckets = heading_buckets(text.split("\n"))
    units = _prose_units(lines, lambda i: buckets[i] == "body")
    units += _table_units(lines, lambda i: buckets[i] in ("body", "appendix"))
    claims = []
    for unit in units:
        claims += _claims_in_unit(shown, unit, ctx)
    claims.sort(key=lambda c: c["_order"])
    return claims


def _finding(rule, severity, path, line, message, excerpt=""):
    return {"rule": rule, "severity": severity, "path": path, "line": line, "message": message,
            "excerpt": excerpt}


NO_CLAIMS = "no citations found; this tool needs [n] references or name + (pN) locators"


@tool(
    "claims_trace",
    "Trace every cited number in a report to a page of its source. Body sentences citing [n] (a paragraph's "
    "citations cover its uncited sentences), paragraphs naming a paper with its arXiv id (in the paragraph or "
    "a report table row) and a page locator (pN)/(pN, pM)/p. N, and rows of tables whose caption or header "
    "cites a paper are checked against the papers' text in `papers` (from papers_fetch), page by page (51% "
    "also matches 0.51). Unlocated numbers may be backed by a ledger table (a row saying 'derived' marks them "
    "derived). Statuses: located, derived, ledgered, untraced (T001 warning), no_source (T002 info). A "
    "located integer below 1000 or a number on 5+ pages is weak; without a locator match ([n, Table k], "
    "[n, p. 4], (p4)) it is T003 (info). T004 (warning): no claims at all. `files` are extra Markdown files "
    "checked with the report's references.",
    {"type": "object",
     "properties": {
         "report": {"type": "string", "description": "Markdown report with a References section"},
         "papers": {"type": "string", "description": "folder holding {arXiv id}.txt paper texts"},
         "ledger": {"type": "string", "description": "Markdown ledger of verified numbers (tables)"},
         "files": {"type": "array", "items": {"type": "string"},
                   "description": "extra Markdown files (deck scripts, notes) checked the same way"},
     },
     "required": ["report", "papers"],
     "additionalProperties": False},
    readOnlyHint=True,
)
def claims_trace(report: str, papers: str, ledger: str | None = None, files: list[str] | None = None) -> dict:
    report_text = read_input(native_path(report), "report")
    folder = Path(native_path(papers))
    if not folder.is_dir():
        raise ToolError(f"papers folder not found: {papers}")
    ledger_rows = _ledger_rows(read_input(native_path(ledger), "ledger")) if ledger is not None else []
    extra, seen = [], {path_key(report)}
    for f in files or []:
        if path_key(f) in seen:
            continue
        seen.add(path_key(f))
        extra.append((f, read_input(native_path(f), "file")))

    raw_lines = report_text.split("\n")
    refs = reference_list(raw_lines, heading_buckets(raw_lines))
    names = table_names(raw_lines)
    known = {i for i in refs.values() if i} | set(names.values())
    for line in raw_lines:
        known.update(_strip_id(m.group(1)) for m in PAREN_ID.finditer(line))
        known.update(_strip_id(m.group(1)) for m in ARXIV_ID.finditer(line))
    ctx = _Context(refs, names, known, _Papers(folder), ledger_rows)
    claims = _trace_file(report.replace("\\", "/"), report_text, ctx)
    report_claims = len(claims)
    for path, text in extra:
        claims += _trace_file(path.replace("\\", "/"), text, ctx)

    findings = []
    for c in claims:
        sentence = c.pop("_sentence")
        c.pop("_order")
        if c["status"] == "untraced":
            where = ", ".join(c["papers"])
            findings.append(_finding("T001", "warning", c["path"], c["line"],
                                     f"{c['number']} (cited {c['citations'] or c['papers']}) is not found in "
                                     f"{where} and has no ledger row", _excerpt(sentence)))
        elif c["status"] == "no_source":
            findings.append(_finding("T002", "info", c["path"], c["line"],
                                     f"{c['number']}: no cited source {c['citations'] or c['papers']} has a "
                                     f"paper text in {papers}", _excerpt(sentence)))
        elif c["status"] == "located" and c["weak"] and not c["locator_match"]:
            pages = ", ".join(map(str, c["pages"]))
            findings.append(_finding("T003", "info", c["path"], c["line"],
                                     f"{c['number']} is a weak location (page {pages}) with no matching locator; "
                                     "check it by hand", _excerpt(sentence)))
    if report_claims == 0:
        findings.append(_finding("T004", "warning", report.replace("\\", "/"), None, NO_CLAIMS))
    findings.sort(key=lambda f: (f["path"], f["line"] or 0, f["rule"]))
    counts = {"error": 0, "warning": sum(f["severity"] == "warning" for f in findings),
              "info": sum(f["severity"] == "info" for f in findings)}
    summary = {s: sum(c["status"] == s for c in claims) for s in STATUSES}
    return {"ok": True, "findings": findings, "counts": counts, "claims": claims, "summary": summary}


# ---------------------------------------------------------------------------------------------- CLI

def add_cli(groups) -> None:
    p = groups.add_parser("claims", help="trace cited numbers to source pages")
    cmds = p.add_subparsers(dest="command", required=True)
    c = cmds.add_parser("trace", help="check every cited number against the cited papers")
    c.add_argument("report")
    c.add_argument("--papers", required=True)
    c.add_argument("--ledger")
    c.add_argument("--in", dest="files", nargs="+", action="extend", metavar="FILE")
    common_flags(c, checker=True)
    c.set_defaults(handler=_cli_trace)


def _cli_trace(args) -> CliResult:
    r = claims_trace(args.report, args.papers, ledger=args.ledger, files=args.files)
    lines = [f"{c['path']}:{c['line']}: {c['number']} {c['status']}"
             + (f" p{','.join(map(str, c['pages']))}" if c["pages"] else "") for c in r["claims"]]
    lines.append(", ".join(f"{k} {v}" for k, v in r["summary"].items()))
    return CliResult(r, "\n".join(lines))
