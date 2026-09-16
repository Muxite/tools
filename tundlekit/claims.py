"""Claim tracing: cited numbers to source pages (MANIFEST.md §15.3).

Every sentence in a report's body that cites a reference `[n]` and states a number is checked against the text of
the cited arXiv papers (fetched with `tundlekit papers fetch`), page by page. Numbers that no page shows can be
backed by a ledger of verified numbers instead.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from tundlekit.cli_support import CliResult, common_flags
from tundlekit.papers import (MD_HEADING, heading_buckets, read_input, reference_ids, split_pages,
                              stored_name)
from tundlekit.registry import ToolError, tool

STATUSES = ("located", "derived", "ledgered", "untraced", "no_source")
EXCERPT_WIDTH = 80

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
    for end in [*sentence_ends(text), len(text)]:
        if end > start and text[start:end].strip():
            spans.append((start, end))
        start = max(start, end)
    return spans


# ---------------------------------------------------------------------------------------------- numbers

CITATION = re.compile(r"\[\s*(\d+)\s*((?:,[^\[\]]*)?)\]")
NUMBER = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)*%?")
EXCLUDED_PREFIX = re.compile(r"(?:§|Fig\.|Table|App\.|arXiv:?)\s*$")
YEAR = re.compile(r"(?:19|20)\d\d")


def _citations(sentence: str) -> tuple[list[int], str]:
    """Cited reference numbers (deduplicated, in order) and the sentence with citation brackets blanked."""
    cited: list[int] = []

    def take(m: re.Match) -> str:
        nums = [m.group(1)] + [p.strip() for p in m.group(2).split(",")[1:]]
        for n in nums:
            if n.isdigit() and int(n) not in cited:
                cited.append(int(n))
        return " " * len(m.group(0))

    return cited, CITATION.sub(take, sentence)


def _numbers(masked: str) -> list[tuple[int, str]]:
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
    alts = [core]
    if token.endswith("%"):
        try:
            fraction = format((Decimal(core) / 100).normalize(), "f")
        except InvalidOperation:
            fraction = ""
        if "." in fraction:
            alts.append(fraction)
    return alts


def _matcher(alternatives: list[str]) -> re.Pattern:
    body = "|".join(re.escape(a) for a in alternatives)
    return re.compile(r"(?<![\d.])(?:" + body + r")(?!\d)(?!\.\d)")


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
    rx = _matcher([token.rstrip("%").replace(",", "")])
    hits = [derived for cells, derived in rows if any(rx.search(c) for c in cells)]
    if not hits:
        return None
    return "derived" if any(hits) else "ledgered"


# ---------------------------------------------------------------------------------------------- tracing

def _excerpt(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= EXCERPT_WIDTH else text[:EXCERPT_WIDTH - 1] + "…"


def _trace_file(shown: str, text: str, refs: dict, papers: _Papers, ledger) -> list[dict]:
    lines = _mask(text)
    buckets = heading_buckets(text.split("\n"))
    claims = []
    for para in _paragraphs(lines, lambda i: buckets[i] == "body"):
        starts, joined = [], ""
        for i in para:
            starts.append(len(joined))
            joined += lines[i] + "\n"
        joined = joined[:-1]

        def line_of(offset: int) -> int:
            k = max(j for j, s in enumerate(starts) if s <= offset)
            return para[k] + 1

        for s, e in split_sentences(joined):
            cited, masked = _citations(joined[s:e])
            if not cited:
                continue
            numbers = _numbers(masked)
            if not numbers:
                continue
            lead = len(masked) - len(masked.lstrip())
            line = line_of(s + lead)
            ids = []
            for n in cited:
                if refs.get(n) and refs[n] not in ids:
                    ids.append(refs[n])
            sources = [(i, papers.pages(i)) for i in ids]
            sources = [(i, p) for i, p in sources if p is not None]
            for pos, token in numbers:
                rx = _matcher(_alternatives(token))
                pages = sorted({n for _, pp in sources for n, body in pp if rx.search(body)})
                if pages:
                    status = "located"
                else:
                    status = _ledger_status(token, ledger) or ("untraced" if sources else "no_source")
                claims.append({"path": shown, "line": line, "number": token, "citations": cited,
                               "papers": ids, "status": status, "pages": pages,
                               "_order": (line, s + pos), "_sentence": joined[s:e]})
    claims.sort(key=lambda c: c["_order"])
    return claims


@tool(
    "claims_trace",
    "Trace every cited number in a report to a page of its source. Each body sentence that cites [n] and "
    "states a number is checked against the cited arXiv papers' text in `papers` (from papers_fetch), page by "
    "page (51% also matches 0.51). Unlocated numbers may be backed by a ledger table of verified numbers "
    "(a row saying 'derived' marks them derived). Statuses: located, derived, ledgered, untraced (T001 "
    "warning), no_source (T002 info). `files` are extra Markdown files checked with the report's references.",
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
    report_text = read_input(report, "report")
    folder = Path(papers)
    if not folder.is_dir():
        raise ToolError(f"papers folder not found: {papers}")
    ledger_rows = _ledger_rows(read_input(ledger, "ledger")) if ledger is not None else []
    extra = [(f, read_input(f, "file")) for f in (files or [])]

    raw_lines = report_text.split("\n")
    refs = reference_ids(raw_lines, heading_buckets(raw_lines))
    source = _Papers(folder)
    claims = _trace_file(report.replace("\\", "/"), report_text, refs, source, ledger_rows)
    for path, text in extra:
        claims += _trace_file(path.replace("\\", "/"), text, refs, source, ledger_rows)

    findings = []
    for c in claims:
        sentence = c.pop("_sentence")
        c.pop("_order")
        if c["status"] == "untraced":
            where = ", ".join(c["papers"])
            findings.append({"rule": "T001", "severity": "warning", "path": c["path"], "line": c["line"],
                             "message": f"{c['number']} (cited {c['citations']}) is not found in {where} "
                                        "and has no ledger row",
                             "excerpt": _excerpt(sentence)})
        elif c["status"] == "no_source":
            findings.append({"rule": "T002", "severity": "info", "path": c["path"], "line": c["line"],
                             "message": f"{c['number']}: no cited reference {c['citations']} has a paper text "
                                        f"in {papers}",
                             "excerpt": _excerpt(sentence)})
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
