"""textlint: report prose and numbering checks (MANIFEST.md §7). Standard library only.

After tundle's style card (notes/40-style-card.md) and its checks (check_forbidden.py, check_fignums.py,
wordcount_sections.py): no em dashes, no first person, no hedges, no contractions, no status markers left in
the text, figure and table numbers that run 1, 2, 3 with every mention resolving, and words per section.
"""
from __future__ import annotations

import ast
import bisect
import codecs
import difflib
import math
import os
import pathlib
import posixpath
import re
import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass, field

from tundlekit.registry import ToolError, tool

SEVERITY = {
    "S001": "error", "S002": "error", "S003": "warning", "S004": "error", "S005": "warning", "S006": "error",
    "S007": "warning", "S008": "error", "S009": "warning", "S010": "warning", "S011": "warning",
    "S012": "info",
}
DEFAULT_MAX_WORDS = 42
DEFAULT_BAND = (15, 25)
BAND_MIN_SENTENCES = 5
TEXT_SUFFIXES = (".md", ".txt")
EXCERPT_WIDTH = 80


# ====================================================================== findings and files
def _finding(rule: str, severity: str, path: str, line: int | None, message: str, excerpt: str = "") -> dict:
    return {"rule": rule, "severity": severity, "path": path, "line": line, "message": message,
            "excerpt": excerpt}


def _checker_result(findings: list[dict], **extra) -> dict:
    findings = sorted(findings, key=lambda f: (f["path"], f["line"] or 0, f["rule"]))
    counts = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        counts[f["severity"]] += 1
    return {"ok": counts["error"] == 0, "findings": findings, "counts": counts, **extra}


def _display(path: str) -> str:
    return path.replace("\\", "/")


def expand_paths(paths, arg: str = "paths") -> list[tuple[str, pathlib.Path]]:
    """Files named directly, plus *.md and *.txt under named directories (hidden directories skipped).

    Returns [(display path with / separators, filesystem path)], without duplicates, in argument order.
    """
    if not paths:
        raise ToolError(f"{arg}: give at least 1 file or directory")
    out, seen = [], set()
    for given in paths:
        p = pathlib.Path(given)
        if p.is_dir():
            found = []
            for f in p.rglob("*"):
                rel = f.relative_to(p)
                if (f.is_file() and f.suffix.lower() in TEXT_SUFFIXES
                        and not any(part.startswith(".") for part in rel.parts)):
                    found.append((rel.as_posix(), f))
            base = pathlib.PurePosixPath(_display(given))
            files = [(str(base / rel), f) for rel, f in sorted(found, key=lambda t: t[0])]
        elif p.is_file():
            files = [(_display(given), p)]
        else:
            raise ToolError(f"{arg}: no such file or directory: {given}")
        for shown, f in files:
            key = os.path.normcase(os.path.abspath(f))
            if key not in seen:
                seen.add(key)
                out.append((shown, f))
    return out


def _read(shown: str, p: pathlib.Path) -> str:
    try:
        text = p.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        raise ToolError(f"{shown}: not UTF-8 text") from None
    except OSError as e:
        raise ToolError(f"cannot read {shown}: {e}") from None
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _split_lines(text: str) -> list[str]:
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def _excerpt(line: str, start: int, end: int) -> str:
    """At most EXCERPT_WIDTH characters of the line around [start, end)."""
    line = line.rstrip()
    if len(line) <= EXCERPT_WIDTH:
        return line.strip()
    span = end - start
    if span >= EXCERPT_WIDTH:
        return line[start:start + EXCERPT_WIDTH]
    left = max(0, min(start - (EXCERPT_WIDTH - span) // 2, len(line) - EXCERPT_WIDTH))
    return line[left:left + EXCERPT_WIDTH].strip()


def _shorten(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= EXCERPT_WIDTH else text[:EXCERPT_WIDTH - 1] + "…"


# ====================================================================== masking (§7.1)
FENCE_OPEN = re.compile(r"^[ \t]*(`{3,}|~{3,})")     # any indentation: fences nest under list items


def _fence_close(fence: str) -> re.Pattern:
    """The line that closes a fence opened with `fence` (the same character, at least as many)."""
    return re.compile(r"^[ \t]*" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}[ \t]*$")
URL = re.compile(r"https?://[^\s<>\"'`]+")
URL_TRAILING = ".,;:!?'\")]}>"
LINK_TARGET = re.compile(r"\]\((?:[^()\n]|\([^()\n]*\))*\)")
REF_DEFINITION = re.compile(r"^ {0,3}\[[^\]\n]+\]:([^\n]*)$", re.MULTILINE)
LINT_IGNORE = re.compile(r"^\s*lint-ignore\b(.*)$", re.DOTALL)
LINT_FILE_IGNORE = re.compile(r"^\s*lint-file-ignore\b(.*)$", re.DOTALL)
FILE_WIDE = 0          # suppression key for `<!-- lint-file-ignore ... -->` (line numbers start at 1)
RULE_ID = re.compile(r"\b[Ss]\d{3}\b")


def _blank(chars: list[str], start: int, end: int) -> None:
    for k in range(start, end):
        if chars[k] != "\n":
            chars[k] = " "


def mask_markdown(lines: list[str]) -> tuple[list[str], dict[int, set | None]]:
    """Replace code, comments, URLs, link targets and front matter by spaces (columns are kept).

    Returns (masked lines, suppressions) where suppressions maps a 1-based line number to the rule ids a
    `<!-- lint-ignore ... -->` comment suppresses there (None: every rule), and FILE_WIDE to the rule ids that
    `<!-- lint-file-ignore ... -->` comments suppress in the whole file (§14.1; no ids suppress nothing).
    """
    masked = list(lines)
    n = len(lines)
    # YAML front matter
    if n and lines[0].rstrip() == "---":
        for j in range(1, n):
            if lines[j].rstrip() in ("---", "..."):
                for k in range(j + 1):
                    masked[k] = " " * len(lines[k])
                break
    # fenced code blocks
    i = 0
    while i < n:
        m = FENCE_OPEN.match(masked[i])
        if not m:
            i += 1
            continue
        fence = m.group(1)
        close = _fence_close(fence)
        j = i + 1
        while j < n and not close.match(lines[j]):
            j += 1
        for k in range(i, min(j, n - 1) + 1):
            masked[k] = " " * len(lines[k])
        i = j + 1

    text = "\n".join(masked)
    starts = [0] + [k + 1 for k, ch in enumerate(text) if ch == "\n"]
    chars = list(text)
    suppress: dict[int, set | None] = {}
    size = len(text)
    i = 0
    while i < size:
        ch = text[i]
        if ch == "`":
            j = i
            while j < size and text[j] == "`":
                j += 1
            closing = _closing_backticks(text, j, j - i)
            if closing is None:
                i = j
            else:
                _blank(chars, i, closing)
                i = closing
        elif text.startswith("<!--", i):
            end = text.find("-->", i + 4)
            end = size if end < 0 else end + 3
            directive = LINT_IGNORE.match(text[i + 4:max(i + 4, end - 3)])
            if directive:
                line = bisect.bisect_right(starts, i)
                ids = {r.upper() for r in RULE_ID.findall(directive.group(1))}
                for target in (line, line + 1):
                    if not ids or suppress.get(target, set()) is None:
                        suppress[target] = None
                    else:
                        suppress[target] = suppress.get(target, set()) | ids
            file_wide = LINT_FILE_IGNORE.match(text[i + 4:max(i + 4, end - 3)])
            if file_wide:
                ids = {r.upper() for r in RULE_ID.findall(file_wide.group(1))}
                suppress[FILE_WIDE] = suppress.get(FILE_WIDE, set()) | ids
            _blank(chars, i, end)
            i = end
        else:
            i += 1

    text = "".join(chars)
    for m in URL.finditer(text):
        end = m.end()
        while end > m.start() and text[end - 1] in URL_TRAILING:
            end -= 1
        _blank(chars, m.start(), end)
    text = "".join(chars)
    for m in LINK_TARGET.finditer(text):
        _blank(chars, m.start() + 1, m.end())
    for m in REF_DEFINITION.finditer(text):
        _blank(chars, m.start(1), m.end(1))
    return "".join(chars).split("\n"), suppress


def _closing_backticks(text: str, pos: int, run: int) -> int | None:
    """End index of the matching backtick run on the same line, or None."""
    eol = text.find("\n", pos)
    eol = len(text) if eol < 0 else eol
    k = pos
    while k < eol:
        if text[k] != "`":
            k += 1
            continue
        m = k
        while m < eol and text[m] == "`":
            m += 1
        if m - k == run:
            return m
        k = m
    return None


# ====================================================================== structure and sentences
HEADING = re.compile(r"^(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
THEMATIC_BREAK = re.compile(r"^ {0,3}([-*_])[ \t]*(?:\1[ \t]*){2,}$")
LIST_ITEM = re.compile(r"^[ \t]*(?:[-*+]|\d{1,9}[.)])(?:[ \t]+|$)")
QUOTE_PREFIX = re.compile(r"^[ \t]*(?:>[ \t]?)+")
EXEMPT_HEADING = re.compile(r"^(references|bibliography|appendix a\b)", re.IGNORECASE)
SENTENCE_END = re.compile(r"[.!?]+[\"'”’)\]]*(?=\s|$)")
ABBREVIATIONS_ANY_CASE = {"e.g.", "i.e.", "vs.", "approx.", "cf."}
ABBREVIATIONS_EXACT = {"Fig.", "Eq.", "No.", "App.", "Tab.", "Sec.", "Ref.", "Refs."}
SECTION_OPENER = re.compile(r"^(this section|in this section|here we|this chapter)\b", re.IGNORECASE)
WORD = re.compile(r"\w")
# after masking, an image line keeps only "![alt]" (and "[" "]" of a linked image)
IMAGE_ONLY = re.compile(r"^[ \t]*(?:\[?!\[[^\]]*\][ \t]*\]?[ \t]*)+$")


def _is_table_separator(line: str) -> bool:
    s = line.strip()
    return "|" in s and "-" in s and not s.strip("|:- \t")


@dataclass
class _Paragraph:
    is_item: bool
    section: int | None                            # index of the heading above it (None: before any heading)
    pieces: list = field(default_factory=list)     # [(offset in joined text, line number, column)]
    text: str = ""
    original: str = ""

    def add(self, lineno: int, column: int, masked: str, original: str) -> None:
        if self.text:
            self.text += " "
            self.original += " "
        self.pieces.append((len(self.text), lineno, column))
        self.text += masked
        self.original += original

    def line_at(self, offset: int) -> int:
        k = bisect.bisect_right([p[0] for p in self.pieces], offset) - 1
        return self.pieces[max(k, 0)][1]


@dataclass
class _Sentence:
    line: int
    words: int
    text: str
    section: int | None


def _is_abbreviation(text: str, m: re.Match) -> bool:
    if m.group(0) != ".":
        return False
    before = text[:m.start() + 1].split()
    if not before:
        return False
    token = before[-1].lstrip("([{\"'“‘")
    if token in ABBREVIATIONS_EXACT or token.lower() in ABBREVIATIONS_ANY_CASE:
        return True
    return token == "al." and len(before) >= 2 and before[-2].lstrip("([{\"'“‘") == "et"


def _count_words(text: str) -> int:
    return sum(1 for tok in text.split() if WORD.search(tok))


def _bracket_spans(text: str) -> list[tuple[int, int]]:
    """(start, end) of every matched [...] pair, outermost pairs only."""
    spans, stack = [], []
    for k, ch in enumerate(text):
        if ch == "[":
            stack.append(k)
        elif ch == "]" and stack:
            start = stack.pop()
            if not stack:
                spans.append((start, k + 1))
    return spans


def sentence_ends(text: str) -> list[int]:
    """Offsets just after each sentence end in 1 paragraph of text (§7.1, with the §15 pins).

    A sentence ends at . ! or ? followed by whitespace or the end, except after the listed abbreviations and
    never inside a matched [...] pair.
    """
    spans = _bracket_spans(text)
    starts = [s for s, _ in spans]
    ends = []
    for m in SENTENCE_END.finditer(text):
        k = bisect.bisect_right(starts, m.start()) - 1
        if k >= 0 and spans[k][0] < m.start() < spans[k][1] - 1:
            continue
        if not _is_abbreviation(text, m):
            ends.append(m.end())
    return ends


def _sentences(par: _Paragraph) -> list[_Sentence]:
    out = []
    start = 0
    for end in sentence_ends(par.text) + [len(par.text)]:
        chunk = par.text[start:end]
        words = _count_words(chunk)
        if words:
            lead = len(chunk) - len(chunk.lstrip())
            out.append(_Sentence(par.line_at(start + lead), words, par.original[start:end], par.section))
        start = end
    return out


# ====================================================================== line rules
FIRST_PERSON = re.compile(r"\b(?:[Ww][Ee]|[Oo][Uu][Rr][Ss]?|[Uu][Ss])\b|\bI(?= [a-z])")
MAY_HEDGE_NEXT = ("be", "have", "well", "also", "not", "help", "seem", "lead", "cause")
HEDGES = re.compile(r"(?i:\b(?:arguably|seems|seem|seemingly|perhaps|somewhat|possibly|might"
                    r"|to\s+some\s+extent|it\s+appears)\b)"
                    r"|\bmay\b(?=\s+(?:" + "|".join(MAY_HEDGE_NEXT) + r")\b|\s*$)")
FIRST_WORD = re.compile(r"^\W*?(\w+)")
CITATION_BRACKET = re.compile(r"\[\s*\d")
CONTRACTIONS = re.compile(r"(?i)\b\w*n['’]t\b|\b\w+['’](?:re|ve|ll|d|m)\b"
                          r"|\b(?:it|that|there|what|here|let|who)['’]s\b")
SEMICOLON = re.compile(r"(?<!&[A-Za-z]{2})(?<!&[A-Za-z]{3})(?<!&[A-Za-z]{4})(?<!&[A-Za-z]{5})(?<!&[A-Za-z]{6})"
                       r"(?<!&#\d{2})(?<!&#\d{3})(?<!&#\d{4});")
MARKERS = re.compile(r"⚠|(?i:\[(?:verified|proposed|doc|repo-claim)\]|\[(?:todo|tbd|footnote))|TODO:|XXX")
QUESTION = re.compile(r"\?+(?=\s|$|[\"'”’»)\]}])")
ET_AL = re.compile(r"\bet\s+al\.")
JARGON = re.compile(r"\bEq\.?\s*\(?\d|\bpp\b(?!\.\s*\d)")
EM_DASH = re.compile("—")

_LINE_RULES = (
    ("S001", EM_DASH, "em dash; use a comma, a colon or a full stop", True),
    ("S002", FIRST_PERSON, "first person {m!r}; describe the system, not the authors", True),
    ("S003", HEDGES, "hedge {m!r}; state the claim and bound it with a limitations list", False),
    ("S004", CONTRACTIONS, "contraction {m!r}; write the words out", False),
    ("S005", SEMICOLON, "semicolon; split the sentence or use a list", False),
    ("S006", MARKERS, "status marker or placeholder {m!r} left in the text", True),
    ("S007", QUESTION, "question in body prose; state the point instead", False),
    ("S008", ET_AL, "'et al.' outside References/Bibliography/Appendix A; cite by identifier", False),
    ("S011", JARGON, "jargon {m!r}; write 'Equation N' or 'percentage points'", False),
)


def _citation_spans(masked: str) -> list[tuple[int, int]]:
    """[...] pairs whose text starts with a number, such as [2, Eq. (5)] (§14.1: exempt from S011)."""
    return [(a, b) for a, b in _bracket_spans(masked) if CITATION_BRACKET.match(masked, a)]


def _line_findings(path: str, lineno: int, masked: str, original: str, kind: str, exempt: bool,
                   questions_ok: bool = False, next_word: str = "") -> list:
    """Line rules for 1 line. kind is "heading", "prose" or "table"; exempt: inside an S008-exempt section;
    questions_ok: inside a question section (no S007); next_word: the first word of the next prose line."""
    out = []
    heading = kind == "heading"
    citations = None
    for rule, pattern, message, in_headings in _LINE_RULES:
        if heading and not in_headings:
            continue
        if rule == "S008" and exempt:
            continue
        if rule in ("S005", "S007") and kind == "table":
            continue
        if rule == "S007" and questions_ok:
            continue
        for m in pattern.finditer(masked):
            if rule == "S002" and m.group(0) == "US":
                continue
            if rule == "S003" and m.group(0) == "may" and not masked[m.end():].strip() \
                    and next_word not in MAY_HEDGE_NEXT:
                continue
            if rule == "S011":
                if citations is None:
                    citations = _citation_spans(masked)
                if any(a < m.start() < b for a, b in citations):
                    continue
            out.append(_finding(rule, SEVERITY[rule], path, lineno, message.format(m=m.group(0)),
                                _excerpt(original, m.start(), m.end())))
    return out


@dataclass
class _Structure:
    """1 document split into line kinds and prose paragraphs."""
    kinds: list          # per line: None (not checked), ("heading", level, title), ("prose",) or ("table",)
    paragraphs: list[_Paragraph]


def _structure(lines: list[str], masked: list[str]) -> _Structure:
    kinds: list = []
    paragraphs: list[_Paragraph] = []
    current: _Paragraph | None = None
    section: int | None = None
    tables = _table_lines(masked)

    def flush():
        nonlocal current
        if current is not None:
            paragraphs.append(current)
        current = None

    for idx, mline in enumerate(masked):
        lineno, original = idx + 1, lines[idx]
        if not mline.strip():
            kinds.append(None)
            flush()
            continue
        heading = HEADING.match(mline)
        if heading:
            flush()
            kinds.append(("heading", len(heading.group(1)), (heading.group(2) or "").rstrip("#").strip()))
            section = 0 if section is None else section + 1
            continue
        if _is_table_separator(mline) or THEMATIC_BREAK.match(mline):
            kinds.append(None)
            flush()
            continue
        if idx in tables:                    # §14.1: a table row is neither a sentence nor a list item
            kinds.append(("table",))
            flush()
            continue
        kinds.append(("prose",))
        if IMAGE_ONLY.match(mline):          # a figure line is not prose (it may sit before a section's text)
            flush()
            continue
        quote = QUOTE_PREFIX.match(mline)
        column = quote.end() if quote else 0
        item = LIST_ITEM.match(mline, column)
        if item:
            flush()
            current = _Paragraph(True, section)
            column = item.end()
        elif current is None or (current.is_item and not mline[:1].isspace()):
            flush()
            current = _Paragraph(False, section)
        current.add(lineno, column, mline[column:], original[column:])
    flush()
    return _Structure(kinds, paragraphs)


def split_sentences(text: str) -> list[tuple[int, str]]:
    """The prose sentences of a Markdown document, as [(1-based line where the sentence starts, sentence)].

    Uses the §7.1 rules (masking, paragraphs, list items, abbreviations, no split inside [...]). The sentence text
    is the original text (not masked) with its line breaks joined by spaces; headings are not sentences.
    """
    lines = _split_lines(text.replace("\r\n", "\n").replace("\r", "\n"))
    masked, _ = mask_markdown(lines)
    out = []
    for par in _structure(lines, masked).paragraphs:
        out += [(s.line, s.text.strip()) for s in _sentences(par)]
    return out


QUESTION_HEADING = re.compile(r"question", re.IGNORECASE)


def _next_word(doc: _Structure, masked: list[str], idx: int) -> str:
    """The first word of the prose line after line idx (0-based), or "" when the next line is not prose."""
    k = idx + 1
    if k >= len(doc.kinds) or doc.kinds[k] is None or doc.kinds[k][0] != "prose":
        return ""
    line = masked[k]
    quote = QUOTE_PREFIX.match(line)
    start = quote.end() if quote else 0
    if LIST_ITEM.match(line, start):
        return ""
    m = FIRST_WORD.match(line[start:])
    return m.group(1) if m else ""


def lint_text(path: str, text: str, max_words: int = DEFAULT_MAX_WORDS,
              band: tuple = DEFAULT_BAND) -> tuple[list[dict], dict]:
    """Run every §7.1/§14.1 rule over 1 document. Returns (findings before rule filtering, stats)."""
    lines = _split_lines(text)
    masked, suppress = mask_markdown(lines)
    doc = _structure(lines, masked)
    paragraphs = doc.paragraphs
    findings: list[dict] = []
    exempt_level: int | None = None
    question_level: int | None = None
    for idx, kind in enumerate(doc.kinds):
        if kind is None:
            continue
        if kind[0] == "heading":
            level, title = kind[1], kind[2]
            if exempt_level is not None and level <= exempt_level:
                exempt_level = None
            if exempt_level is None and EXEMPT_HEADING.match(title):
                exempt_level = level
            if question_level is not None and level <= question_level:
                question_level = None
            if question_level is None and QUESTION_HEADING.search(title):
                question_level = level
        next_word = _next_word(doc, masked, idx) if kind[0] == "prose" else ""
        findings += _line_findings(path, idx + 1, masked[idx], lines[idx], kind[0], exempt_level is not None,
                                   question_level is not None, next_word)

    sentences = []
    for par in paragraphs:
        sentences += _sentences(par)
    opened: set[int] = set()        # sections whose first prose sentence has been checked
    for s in sentences:
        if s.words > max_words:     # table rows are not sentences, so S009 skips them (§14.1)
            findings.append(_finding("S009", "warning", path, s.line,
                                     f"sentence of {s.words} words (limit {max_words}); split it",
                                     _shorten(s.text)))
        if s.section is None or s.section in opened:
            continue
        opened.add(s.section)
        if SECTION_OPENER.match(s.text.strip()):
            findings.append(_finding("S010", "warning", path, s.line,
                                     "section opens with a framing sentence; open with the subject's function "
                                     "or status", _shorten(s.text)))

    prose_words = [s.words for par in paragraphs if not par.is_item for s in _sentences(par)]
    if len(prose_words) >= BAND_MIN_SENTENCES:
        mean = sum(prose_words) / len(prose_words)
        low, high = band
        if mean < low or mean > high:
            side = "below" if mean < low else "above"
            findings.append(_finding("S012", "info", path, None,
                                     f"mean prose sentence length {_round1(mean):g} words over "
                                     f"{len(prose_words)} sentences is {side} the band {low:g}-{high:g}",
                                     f"mean {_round1(mean):g} words"))

    findings = [f for f in findings if not _suppressed(suppress, f)]
    words = [s.words for s in sentences]
    stats = {"sentences": len(words), "words": sum(words),
             "mean_sentence_words": _round1(sum(words) / len(words)) if words else 0.0,
             "max_sentence_words": max(words, default=0),
             "list_items": sum(1 for p in paragraphs if p.is_item)}
    return findings, stats


def _suppressed(suppress: dict, finding: dict) -> bool:
    if finding["rule"] in suppress.get(FILE_WIDE, ()):
        return True
    line = finding["line"]
    if not line or line not in suppress:
        return False
    ids = suppress[line]
    return ids is None or finding["rule"] in ids


def _round1(x: float) -> float:
    """Round half up to 1 decimal place."""
    return int(x * 10 + 0.5 + 1e-9) / 10


def _check_band(band) -> tuple[float, float]:
    """S012's [low, high]: 2 finite non-negative numbers with low <= high (default [15, 25])."""
    if band is None:
        return DEFAULT_BAND
    ok = (isinstance(band, (list, tuple)) and len(band) == 2
          and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in band))
    if ok:
        try:
            ok = all(math.isfinite(float(x)) and float(x) >= 0 for x in band) and float(band[0]) <= float(band[1])
        except OverflowError:
            ok = False
    if not ok:
        raise ToolError("band: must be [low, high], 2 finite numbers >= 0 with low <= high")
    return band[0], band[1]


def _rule_list(values, arg: str) -> list[str]:
    out = []
    for value in values or []:
        for part in str(value).split(","):
            rule = part.strip().upper()
            if not rule:
                continue
            if rule not in SEVERITY:
                raise ToolError(f"{arg}: unknown rule {part.strip()!r} (known: {', '.join(SEVERITY)})")
            out.append(rule)
    return out


# ====================================================================== fignums (§7.2)
FIG_CAPTION = re.compile(r"^(?:!\[|\*\*|\*)?Fig\. ([A-Z]?)(\d+)\.(?!\d)")
TABLE_CAPTION = re.compile(r"^(?:\*\*|\*)?Table ([A-Z]?)(\d+)\.(?!\d)")
MENTION = re.compile(r"\b(?:(Fig)\.|(Table)) ([A-Z]?)(\d+)(?!\d)")
CITED_PAPER = re.compile(r"(?i)arxiv|\bpaper\b")


def _captions(text: str) -> tuple[dict, set[int]]:
    """{(kind, prefix): [(number, line)]} in file order, and the set of caption line numbers."""
    seqs: dict = {}
    caption_lines = set()
    for lineno, line in enumerate(_split_lines(text), 1):
        stripped = line.strip()
        for kind, pattern in (("Fig", FIG_CAPTION), ("Table", TABLE_CAPTION)):
            m = pattern.match(stripped)
            if m:
                seqs.setdefault((kind, m.group(1)), []).append((int(m.group(2)), lineno))
                caption_lines.add(lineno)
                break
    return seqs, caption_lines


def _sequence_findings(path: str, kind: str, prefix: str, seq: list[tuple[int, int]]) -> list[dict]:
    name = f"{kind}. {prefix}" if kind == "Fig" else f"{kind} {prefix}"
    series = f"'{name}N' numbering"
    out = []
    first_line: dict[int, int] = {}
    for number, line in seq:
        if number in first_line:
            out.append(_finding("F001", "error", path, line,
                                f"{name}{number} is numbered twice (first at line {first_line[number]})",
                                f"{name}{number}"))
        else:
            first_line[number] = line
    numbers = [number for number, _ in seq]
    unique = sorted(set(numbers))
    for a, b in zip(unique, unique[1:]):
        if b != a + 1:
            missing = f"{name}{a + 1}" if b == a + 2 else f"{name}{a + 1} to {name}{b - 1}"
            out.append(_finding("F002", "error", path, None,
                                f"gap in {series}: {name}{a} is followed by {name}{b} ({missing} missing)",
                                f"{name}{a} → {name}{b}"))
    if unique and unique[0] != 1:
        out.append(_finding("F003", "error", path, seq[0][1],
                            f"{series} starts at {unique[0]}, not 1", f"{name}{unique[0]}"))
    if numbers != sorted(numbers):
        line = next(line for (n1, _), (n2, line) in zip(seq, seq[1:]) if n2 < n1)
        out.append(_finding("F004", "error", path, line,
                            f"{series} is out of order: {', '.join(map(str, numbers))}",
                            ", ".join(f"{name}{number}" for number in numbers)))
    return out


def _mention_findings(path: str, text: str, known: set, skip_lines: set[int],
                      report: str | None = None) -> list[dict]:
    out = []
    for lineno, line in enumerate(_split_lines(text), 1):
        if lineno in skip_lines:
            continue
        for m in MENTION.finditer(line):
            if CITED_PAPER.search(line[:m.start()]):
                continue
            kind = m.group(1) or m.group(2)
            key = (kind, m.group(3), int(m.group(4)))
            if key not in known:
                label = m.group(0)
                out.append(_finding("F005", "error", path, lineno,
                                    f"{label} does not match any caption in "
                                    + (report if report is not None else "the reports"),
                                    _excerpt(line, m.start(), m.end())))
    return out


# ====================================================================== wordcount (§7.3)
WORDCOUNT_HEADING = re.compile(r"^#{1,3}[ \t]")
FRONT_MATTER = "(front matter)"


REFERENCES_BUCKET = re.compile(r"^(references|bibliography)\b", re.IGNORECASE)
APPENDIX_BUCKET = re.compile(r"^appendix\b", re.IGNORECASE)
BUCKETS = ("body", "appendix", "references")


def _heading_bucket(line: str, level: int, parent: str) -> str:
    """§14.2: level-2 References/Bibliography and Appendix headings start buckets; deeper headings inherit."""
    if level > 2:
        return parent
    if level < 2:
        return "body"
    title = line.strip()[level:].strip()
    if REFERENCES_BUCKET.match(title):
        return "references"
    if APPENDIX_BUCKET.match(title):
        return "appendix"
    return "body"


def section_counts(text: str, tables: bool = True) -> list[tuple[str, int, str]]:
    """[(heading, words, bucket)] for headings of level 1-3; fenced code does not start sections.

    With tables false, table rows (outside fenced code) are not counted.
    """
    lines = _split_lines(text)
    in_fence = []
    fence = None
    for line in lines:
        if fence is None:
            m = FENCE_OPEN.match(line)
            if m:
                fence = m.group(1)
                in_fence.append(True)
                continue
            in_fence.append(False)
        else:
            in_fence.append(True)
            if _fence_close(fence).match(line):
                fence = None
    skip = set() if tables else _table_lines(["" if f else line for f, line in zip(in_fence, lines)])
    out = []
    name, words, bucket = FRONT_MATTER, 0, "body"
    for idx, line in enumerate(lines):
        heading = None if in_fence[idx] else WORDCOUNT_HEADING.match(line)
        if heading:
            out.append((name, words, bucket))
            level = len(line) - len(line.lstrip("#"))
            name, words = line.strip(), 0
            bucket = _heading_bucket(line, level, bucket)
            continue
        if idx not in skip:
            words += len(line.split())
    out.append((name, words, bucket))
    return [(n, w, b) for n, w, b in out if n != FRONT_MATTER or w]


def count_sections(text: str, tables: bool = True) -> list[tuple[str, int]]:
    """[(heading, words)] for headings of level 1-3; fenced code does not start sections."""
    return [(n, w) for n, w, _ in section_counts(text, tables)]


def _git(args: list[str], cwd: pathlib.Path) -> subprocess.CompletedProcess:
    exe = shutil.which("git")
    if exe is None:
        raise ToolError("git not found: install git or leave out baseline")
    return subprocess.run([exe, "-C", str(cwd), *args], capture_output=True, timeout=60)


def _baseline_text(shown: str, p: pathlib.Path, ref: str, checked: set) -> str | None:
    """The file's content at ref, or None when the file isn't in that ref."""
    folder = p.resolve().parent
    prefix = _git(["rev-parse", "--show-prefix"], folder)
    if prefix.returncode != 0:
        raise ToolError(f"baseline: {shown} is not inside a git repository")
    top = _git(["rev-parse", "--show-toplevel"], folder).stdout.strip()
    if (top, ref) not in checked:
        if _git(["rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"], folder).returncode != 0:
            raise ToolError(f"baseline: unknown git ref {ref!r} in the repository of {shown}")
        checked.add((top, ref))
    rel = prefix.stdout.decode("utf-8", "replace").strip() + p.name
    shown_blob = _git(["show", f"{ref}:{rel}"], folder)
    if shown_blob.returncode != 0:
        return None
    text = shown_blob.stdout.decode("utf-8-sig", "replace")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _deltas(current: list[tuple[str, int]], old: list[tuple[str, int]] | None) -> list[dict]:
    """Match the k-th section with a heading to the k-th section with the same heading in the baseline."""
    old_by_name: dict[str, list[int]] = {}
    for name, words in old or []:
        old_by_name.setdefault(name, []).append(words)
    seen: dict[str, int] = {}
    out = []
    for name, words in current:
        k = seen.get(name, 0)
        seen[name] = k + 1
        if old is None:
            delta = None
        elif k < len(old_by_name.get(name, [])):
            delta = words - old_by_name[name][k]
        else:
            delta = "new"
        out.append({"heading": name, "words": words, "delta": delta})
    return out


# ====================================================================== tools
@tool("text_lint",
      "Check report prose against the house style (tundle style card). Rules: S001 em dash, S002 first person "
      "(we/our/ours/us/I), S003 hedges (arguably, seems, perhaps, might, may...), S004 contractions, S005 "
      "semicolons, S006 status markers and placeholders ([verified], [TODO, TODO:, XXX, ⚠), S007 questions in "
      "prose, S008 'et al.' outside References/Bibliography/Appendix A, S009 sentences over max_words words "
      "(default 42), S010 framing openers ('This section...'), S011 jargon (Eq. 3, pp), S012 (info) mean prose "
      "sentence length outside band (default [15, 25], 5+ sentences). Table rows skip S005/S007/S009; "
      "sections headed '...question...' skip S007. Code, comments, URLs, link targets and front matter are "
      "skipped; '<!-- lint-ignore S003 -->' silences rules on its line and the next, "
      "'<!-- lint-file-ignore S003 -->' in the whole file. paths: files or directories (*.md, *.txt). "
      "Returns {ok, findings, counts, stats: {path: {sentences, words, mean_sentence_words, "
      "max_sentence_words, list_items}}}.",
      {"type": "object",
       "properties": {
           "paths": {"type": "array", "items": {"type": "string"}, "description": "Files or directories."},
           "rules": {"type": "array", "items": {"type": "string"}, "description": "Only these rule ids."},
           "ignore": {"type": "array", "items": {"type": "string"}, "description": "Skip these rule ids."},
           "max_words": {"type": "integer", "description": "S009 sentence length limit (default 42)."},
           "band": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2,
                    "description": "S012 [low, high] mean sentence length (default [15, 25])."},
       },
       "required": ["paths"],
       "additionalProperties": False},
      readOnlyHint=True)
def text_lint(paths: list[str], rules: list[str] | None = None, ignore: list[str] | None = None,
              max_words: int = DEFAULT_MAX_WORDS, band: list | None = None) -> dict:
    selected = set(_rule_list(rules, "rules")) or set(SEVERITY)
    selected -= set(_rule_list(ignore, "ignore"))
    if isinstance(max_words, bool) or not isinstance(max_words, int) or max_words < 1:
        raise ToolError("max_words: must be a positive integer")
    band = _check_band(band)
    findings, stats = [], {}
    for shown, p in expand_paths(paths):
        file_findings, stats[shown] = lint_text(shown, _read(shown, p), max_words, band)
        findings += [f for f in file_findings if f["rule"] in selected]
    return _checker_result(findings, stats=stats)


def _path_key(path) -> str:
    return os.path.normcase(os.path.abspath(path))


def _bound_refs(entries: list[str], report_keys: dict[str, str]) -> list[tuple[str, str | None]]:
    """[(refs file, shown name of the report it is bound to, or None)] from FILE and FILE=REPORT entries (§14.3).

    An entry that names an existing path is a plain FILE, even when it contains '='. Otherwise it is split at
    the '=' whose right side is 1 of the reports; REPORT must be 1 of `paths`.
    """
    out = []
    for entry in entries:
        if not isinstance(entry, str):
            raise ToolError("refs: must be a list of strings")
        if "=" not in entry or os.path.exists(entry):
            out.append((entry, None))
            continue
        cuts = [k for k, ch in enumerate(entry) if ch == "="]
        bound = next(((entry[:k], report_keys[_path_key(entry[k + 1:])]) for k in cuts
                      if entry[k + 1:] and _path_key(entry[k + 1:]) in report_keys), None)
        if bound is None:
            file, report = entry.split("=", 1)
            raise ToolError(f"refs: {entry!r}: the report {report!r} after '=' is not one of the paths"
                            if file and report else f"refs: expected FILE or FILE=REPORT, got {entry!r}")
        if not bound[0]:
            raise ToolError(f"refs: expected FILE=REPORT, got {entry!r}")
        out.append(bound)
    return out


@tool("text_fignums",
      "Check figure and table numbering in Markdown reports. Captions are lines starting '![Fig. N.', "
      "'*Fig. N.', '**Fig. N.', 'Fig. N.', '*Table N.', '**Table N.' or 'Table N.' (N may have an upper-case "
      "prefix such as E1; each kind and prefix is numbered on its own, per file). F001 duplicate number, F002 "
      "gap, F003 sequence not starting at 1, F004 out of order, F005 a 'Fig. N' or 'Table N' mention (in the "
      "reports, or anywhere in the refs files, e.g. deck footers) with no matching caption in any report. "
      "A refs entry FILE=REPORT resolves that file against REPORT only (REPORT must be in paths). "
      "Mentions after 'arXiv' or 'paper' on the same line are skipped. Returns {ok, findings, counts, "
      "captions: {path: {Fig: {prefix: [numbers]}, Table: {...}}}}.",
      {"type": "object",
       "properties": {
           "paths": {"type": "array", "items": {"type": "string"}, "description": "Report files."},
           "refs": {"type": "array", "items": {"type": "string"},
                    "description": "Other files (FILE or FILE=REPORT) whose Fig./Table mentions must "
                                   "resolve against the reports."},
       },
       "required": ["paths"],
       "additionalProperties": False},
      readOnlyHint=True)
def text_fignums(paths: list[str], refs: list[str] | None = None) -> dict:
    files = expand_paths(paths)
    reports = [(shown, _read(shown, p)) for shown, p in files]
    report_keys = {_path_key(p): shown for shown, p in files}
    others, seen = [], set()
    for entry, bound in _bound_refs(refs or [], report_keys):
        for shown, p in expand_paths([entry], "refs"):
            if (_path_key(p), bound) not in seen:
                seen.add((_path_key(p), bound))
                others.append((shown, _read(shown, p), bound))
    findings, captions, known, caption_lines, known_in = [], {}, set(), {}, {}
    for shown, text in reports:
        seqs, caption_lines[shown] = _captions(text)
        entry = {"Fig": {}, "Table": {}}
        mine = known_in.setdefault(shown, set())
        for (kind, prefix), seq in seqs.items():
            entry[kind][prefix] = [number for number, _ in seq]
            mine.update((kind, prefix, number) for number, _ in seq)
            findings += _sequence_findings(shown, kind, prefix, seq)
        known |= mine
        captions[shown] = {kind: dict(sorted(seqs_.items())) for kind, seqs_ in entry.items()}
    for shown, text in reports:
        findings += _mention_findings(shown, text, known, caption_lines[shown])
    for shown, text, bound in others:
        findings += _mention_findings(shown, text, known if bound is None else known_in[bound], set(), bound)
    return _checker_result(findings, captions=captions)


@tool("text_wordcount",
      "Count words per section (headings of level 1-3) in Markdown files. Words are whitespace tokens of the "
      "section body; text before the first heading is '(front matter)' and is left out when empty. With "
      "baseline (a git ref such as a tag), each section also gets the difference against the same file at "
      "that ref ('new' for a heading the baseline lacks); baseline_file compares with another file instead. "
      "Level-2 'References'/'Bibliography' and 'Appendix...' headings start the references and appendix "
      "buckets (deeper headings inherit). tables=false leaves table rows out. Returns {files: {path: {sections: "
      "[{heading, words, delta, bucket}], total, total_delta, buckets: {body, appendix, references}}}}; deltas "
      "are null without a baseline or when the file is not in the ref.",
      {"type": "object",
       "properties": {
           "paths": {"type": "array", "items": {"type": "string"}, "description": "Files or directories."},
           "baseline": {"type": "string", "description": "Git ref to compare against."},
           "baseline_file": {"type": "string",
                             "description": "A file to compare against (not together with baseline)."},
           "tables": {"type": "boolean", "description": "Count table rows (default true)."},
       },
       "required": ["paths"],
       "additionalProperties": False},
      readOnlyHint=True)
def text_wordcount(paths: list[str], baseline: str | None = None, baseline_file: str | None = None,
                   tables: bool = True) -> dict:
    if baseline is not None and baseline_file is not None:
        raise ToolError("baseline and baseline_file are mutually exclusive: give 1 of them")
    if not isinstance(tables, bool):
        raise ToolError("tables: must be true or false")
    fixed_old = None
    if baseline_file is not None:
        if not isinstance(baseline_file, str) or not pathlib.Path(baseline_file).is_file():
            raise ToolError(f"baseline_file: no such file: {baseline_file}")
        fixed_old = section_counts(_read(_display(baseline_file), pathlib.Path(baseline_file)), tables)
    files = {}
    checked: set = set()
    for shown, p in expand_paths(paths):
        current = section_counts(_read(shown, p), tables)
        old = fixed_old
        if baseline is not None:
            old_text = _baseline_text(shown, p, baseline, checked)
            old = section_counts(old_text, tables) if old_text is not None else None
        old_pairs = None if old is None else [(n, w) for n, w, _ in old]
        sections = _deltas([(n, w) for n, w, _ in current], old_pairs)
        buckets = dict.fromkeys(BUCKETS, 0)
        for entry, (_, words, bucket) in zip(sections, current):
            entry["bucket"] = bucket
            buckets[bucket] += words
        total = sum(words for _, words, _ in current)
        files[shown] = {"sections": sections, "total": total,
                        "total_delta": None if old is None else total - sum(words for _, words, _ in old),
                        "buckets": buckets}
    return {"files": files}


# ====================================================================== raw files (§15: line endings kept)
_LINE_WITH_END = re.compile(r"[^\r\n]*(?:\r\n|\n|\r)|[^\r\n]+$")


def _lines_keepends(text: str) -> list[str]:
    """Lines with their own line ending ("\\r\\n", "\\n" or "\\r"); the last line may have none."""
    return _LINE_WITH_END.findall(text)


def _split_ending(line: str) -> tuple[str, str]:
    body = line.rstrip("\r\n")
    return body, line[len(body):]


def _read_raw(path: str, arg: str) -> tuple[str, bool]:
    """(text exactly as stored, had a UTF-8 BOM). ToolError when the file is missing or not UTF-8."""
    p = pathlib.Path(path)
    if not p.exists():
        raise ToolError(f"{arg}: no such file: {path}")
    if not p.is_file():
        raise ToolError(f"{arg}: not a file: {path}")
    try:
        data = p.read_bytes()
    except OSError as e:
        raise ToolError(f"{arg}: cannot read {path}: {e}") from None
    bom = data.startswith(codecs.BOM_UTF8)
    try:
        return data[len(codecs.BOM_UTF8) if bom else 0:].decode("utf-8"), bom
    except UnicodeDecodeError:
        raise ToolError(f"{arg}: not UTF-8 text: {path}") from None


def _replace_file(path: str, data: bytes) -> None:
    """Write data to path through a temporary file in the same folder, so a failure leaves the old file."""
    target = pathlib.Path(path)
    fd, tmp = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, target)
    except OSError as e:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise ToolError(f"cannot write {path}: {e}") from None


def _write_text(path: str, text: str, bom: bool) -> None:
    _replace_file(path, (codecs.BOM_UTF8 if bom else b"") + text.encode("utf-8"))


def _str_list(value, arg: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ToolError(f"{arg}: must be a list of strings")
    return value


# ====================================================================== xref (§15.2)
XREF = re.compile(
    r"§\s?(?P<sec>\d+(?:\.\d+)*)"
    r"|\bApp\.\s?(?P<app>[A-Z](?:\.\d+)?)(?![A-Za-z0-9]|\.\d)"
    r"|\bFig\.\s?(?P<fig>[A-Z]?\d+)(?!\d|\.\d)"
    r"|\bTable\s(?P<tab>[A-Z]?\d+)(?!\d|\.\d)")
SECTION_HEADING = re.compile(r"^#{1,6}[ \t]+(\d+(?:\.\d+)*)(?=[.\s]|$)")
APPENDIX_HEADING = re.compile(r"^#{1,6}[ \t]+Appendix[ \t]+([A-Z])(?![A-Za-z0-9])")
APPENDIX_SUB_HEADING = re.compile(r"^#{1,6}[ \t]+([A-Z]\.\d+)(?!\d|\.\d)")
MARKER_CALLS = ("between", "section")
XREF_SUFFIXES = (".py", ".json", ".md", ".txt")


def _ref_key(m: re.Match) -> tuple[str, str]:
    """(kind, id) of a reference match; figure and table numbers lose leading zeros."""
    if m.group("sec") is not None:
        return "§", m.group("sec")
    if m.group("app") is not None:
        return "App", m.group("app")
    kind, ident = ("Fig", m.group("fig")) if m.group("fig") is not None else ("Table", m.group("tab"))
    prefix = ident[0] if ident[0].isalpha() else ""
    return kind, prefix + str(int(ident[len(prefix):]))


def ref_label(key: tuple[str, str]) -> str:
    kind, ident = key
    return {"§": f"§{ident}", "App": f"App. {ident}", "Fig": f"Fig. {ident}", "Table": f"Table {ident}"}[kind]


def find_references(line: str) -> list[tuple[re.Match, tuple[str, str]]]:
    """Every §N(.M)*, App. X(.n), Fig. Pn and Table Pn in a line, except those after `arXiv` or `paper`."""
    return [(m, _ref_key(m)) for m in XREF.finditer(line) if not CITED_PAPER.search(line[:m.start()])]


def report_targets(text: str) -> set[tuple[str, str]]:
    """Reference keys a report defines: numbered headings, appendix headings, figure and table captions."""
    targets = set()
    for line in _split_lines(text):
        for pattern, kind in ((SECTION_HEADING, "§"), (APPENDIX_HEADING, "App"), (APPENDIX_SUB_HEADING, "App")):
            m = pattern.match(line)
            if m:
                targets.add((kind, m.group(1)))
    seqs, _ = _captions(text)
    for (kind, prefix), seq in seqs.items():
        targets.update((kind, f"{prefix}{number}") for number, _ in seq)
    return targets


def _xref_files(paths: list[str]) -> list[tuple[str, pathlib.Path]]:
    out = []
    for given in paths:
        p = pathlib.Path(given)
        if p.is_dir():
            out += [(shown, f) for shown, f in _walk(given, XREF_SUFFIXES)]
        elif p.is_file():
            out.append((_display(given), p))
        else:
            raise ToolError(f"files: no such file or directory: {given}")
    return out


def _walk(base: str, suffixes: tuple) -> list[tuple[str, pathlib.Path]]:
    """Files under base with the given suffixes (hidden folders skipped), as (base joined with the relative
    path using /, path), sorted by relative path."""
    root = pathlib.Path(base)
    found = []
    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for name in files:
            if name.lower().endswith(suffixes):
                f = pathlib.Path(folder) / name
                found.append((f.relative_to(root).as_posix(), f))
    return [(posixpath.join(_display(base), rel), f) for rel, f in sorted(found, key=lambda t: t[0])]


def _marker_findings(shown: str, source: str, report_name: str, report_text: str) -> list[dict]:
    """X002: string-literal markers of between(...) / section(...) calls that the report doesn't hold once."""
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return []
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    out = []
    for call in sorted(calls, key=lambda c: (c.lineno, c.col_offset)):
        func = call.func
        name = func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else None
        if name not in MARKER_CALLS:
            continue
        for arg in call.args[:2]:
            if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
                continue
            literal = arg.value
            if literal.startswith(("\n", "\r")) or not literal.strip():
                continue
            marker = f"### {literal} " if name == "section" else literal
            n = report_text.count(marker)
            if n != 1:
                where = "is missing from" if n == 0 else f"occurs {n} times in"
                out.append(_finding("X002", "warning", shown, call.lineno,
                                    f"marker {marker!r} of {name}(...) {where} {report_name}; "
                                    f"slicing needs it exactly once", marker))
    return out


def _parse_renumber(entries: list[str]) -> dict:
    """{old key: new key} from 'OLD=NEW' strings; both sides must be single references of the same kind."""
    mapping = {}
    for raw in entries:
        if "=" not in raw:
            raise ToolError(f"renumber: expected OLD=NEW, got {raw!r}")
        keys = []
        for side in raw.split("=", 1):
            m = XREF.fullmatch(side.strip())
            if not m:
                raise ToolError(f"renumber: {side.strip()!r} in {raw!r} is not a reference such as "
                                f"§4.2, App. D.4, Fig. 9 or Table A2")
            keys.append(_ref_key(m))
        old, new = keys
        if old[0] != new[0] or (old[0] == "App" and ("." in old[1]) != ("." in new[1])):
            raise ToolError(f"renumber: {raw!r} changes the kind of reference")
        if old in mapping:
            raise ToolError(f"renumber: {ref_label(old)} is renumbered twice")
        mapping[old] = new
    return mapping


def _renumber_line(body: str, mapping: dict, is_report: bool) -> tuple[str, list[tuple[str, str]]]:
    """Apply every renumbering to 1 line at once. Returns (new line, [(old label, new label)])."""
    spans = []                                    # (start, end, replacement, old key, new key)
    for m, key in find_references(body):
        if key in mapping:
            spans.append((m.start(), m.end(), ref_label(mapping[key]), key, mapping[key]))
    if is_report:
        for pattern, kind in ((SECTION_HEADING, "§"), (APPENDIX_HEADING, "App"), (APPENDIX_SUB_HEADING, "App")):
            m = pattern.match(body)
            if m and (kind, m.group(1)) in mapping:
                new = mapping[(kind, m.group(1))]
                spans.append((m.start(1), m.end(1), new[1], (kind, m.group(1)), new))
    spans.sort()
    out, last, edits = [], 0, []
    for start, end, replacement, old_key, new_key in spans:
        if start < last:                          # overlapping spans cannot happen; keep the first
            continue
        out += [body[last:start], replacement]
        last = end
        edits.append((ref_label(old_key), ref_label(new_key)))
    out.append(body[last:])
    return "".join(out), edits


def _renumber_text(text: str, mapping: dict, is_report: bool) -> tuple[str, list[tuple[int, str, str]]]:
    lines, edits = [], []
    for lineno, line in enumerate(_lines_keepends(text), 1):
        body, ending = _split_ending(line)
        new_body, line_edits = _renumber_line(body, mapping, is_report)
        lines.append(new_body + ending)
        edits += [(lineno, old, new) for old, new in line_edits]
    return "".join(lines), edits


# ====================================================================== apply edits (§15.5)
def _check_edits(edits) -> list[dict]:
    if not isinstance(edits, list):
        raise ToolError("edits: must be a list of {find, replace, count} objects")
    problems, out = [], []
    for i, e in enumerate(edits):
        where = f"edits[{i}]"
        if not isinstance(e, dict):
            problems.append(f"{where}: must be an object")
            continue
        for key in e:
            if key not in ("find", "replace", "count"):
                problems.append(f"{where}: unknown key {key!r}")
        if not isinstance(e.get("find"), str) or not e.get("find"):
            problems.append(f"{where}.find: must be a non-empty string")
        if not isinstance(e.get("replace"), str):
            problems.append(f"{where}.replace: must be a string")
        count = e.get("count", 1)
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            problems.append(f"{where}.count: must be an integer >= 1")
        out.append({"find": e.get("find"), "replace": e.get("replace"), "count": count})
    if problems:
        raise ToolError("invalid edits: " + "; ".join(problems))
    return out


def _unified(old_lines: list[str], new_lines: list[str], path: str) -> str:
    shown = _display(path)
    return "\n".join(difflib.unified_diff(old_lines, new_lines, f"a/{shown}", f"b/{shown}", lineterm=""))


def _edit_text_file(path: str, edits: list[dict], write: bool) -> dict:
    text, bom = _read_raw(path, "path")
    crlf = "\r\n" in text and re.search(r"(?<!\r)\n", text) is None
    work = text.replace("\r\n", "\n") if crlf else text
    current, applied, failures = work, 0, []
    for i, e in enumerate(edits):
        found = current.count(e["find"])
        if found != e["count"]:
            failures.append({"index": i, "find": e["find"], "found": found})
            continue
        current = current.replace(e["find"], e["replace"])
        applied += 1
    old_lines = [_split_ending(x)[0] for x in _lines_keepends(work)]
    new_lines = [_split_ending(x)[0] for x in _lines_keepends(current)]
    if write and not failures and current != work:
        _write_text(path, current.replace("\n", "\r\n") if crlf else current, bom)
    return {"ok": not failures, "applied": applied, "failures": failures,
            "diff": _unified(old_lines, new_lines, path)}


# ====================================================================== docx (§15.4, §15.5)
W_NAMESPACES = ("http://schemas.openxmlformats.org/wordprocessingml/2006/main",
                "http://purl.oclc.org/ooxml/wordprocessingml/main")
_XML_ENTITY = re.compile(r"&(?:#(\d+)|#x([0-9a-fA-F]+)|(amp|lt|gt|quot|apos));")
_XML_NAMED = {"amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'"}


def _xml_unescape(text: str) -> str:
    def one(m: re.Match) -> str:
        if m.group(1):
            return chr(int(m.group(1)))
        if m.group(2):
            return chr(int(m.group(2), 16))
        return _XML_NAMED[m.group(3)]
    return _XML_ENTITY.sub(one, text)


def _xml_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


@dataclass
class _Segment:
    """1 piece of paragraph text: a <w:t> element's content, or a tab/break (read-only)."""
    tag_start: int
    content_start: int
    content_end: int
    text: str
    editable: bool
    original: str = ""


class DocxText:
    """The paragraphs of a .docx main document, editable in place without touching any other XML."""

    def __init__(self, path: str, arg: str = "path"):
        self.path = path
        try:
            with zipfile.ZipFile(path) as z:
                self.infos = z.infolist()
                self.parts = {i.filename: z.read(i) for i in self.infos}
                self.comment = z.comment
        except FileNotFoundError:
            raise ToolError(f"{arg}: no such file: {path}") from None
        except (zipfile.BadZipFile, OSError) as e:
            raise ToolError(f"{arg}: not a readable .docx package: {path} ({e})") from None
        self.part = self._main_part()
        raw = self.parts[self.part]
        self.bom = raw.startswith(codecs.BOM_UTF8)
        try:
            self.xml = raw[len(codecs.BOM_UTF8) if self.bom else 0:].decode("utf-8")
        except UnicodeDecodeError:
            raise ToolError(f"{arg}: {self.part} in {path} is not UTF-8") from None
        self.paragraphs = self._scan()

    def _main_part(self) -> str:
        rels = self.parts.get("_rels/.rels", b"").decode("utf-8", "replace")
        m = re.search(r'<Relationship\b[^>]*Type="[^"]*/officeDocument"[^>]*>', rels)
        if m:
            target = re.search(r'Target="([^"]+)"', m.group(0))
            if target and target.group(1).lstrip("/") in self.parts:
                return target.group(1).lstrip("/")
        if "word/document.xml" in self.parts:
            return "word/document.xml"
        raise ToolError(f"not a .docx package (no main document): {self.path}")

    def _scan(self) -> list[list[_Segment]]:
        prefixes = re.findall(r'xmlns:([A-Za-z_][\w.-]*)="(?:%s)"' % "|".join(map(re.escape, W_NAMESPACES)),
                              self.xml) or ["w"]
        w = "(?:%s)" % "|".join(map(re.escape, prefixes))
        token = re.compile(
            rf"(?P<pe><{w}:p(?=[\s/])[^>]*/>)"
            rf"|(?P<po><{w}:p(?=[\s>])[^>]*>)"
            rf"|(?P<pc></{w}:p>)"
            rf"|(?P<t><{w}:t(?=[\s>])[^>]*(?<!/)>)(?P<tc>.*?)</{w}:t>"
            rf"|(?P<tab><{w}:tab/>)"
            rf"|(?P<br><{w}:(?:br|cr)(?=[\s/])[^>]*/>)", re.S)
        paragraphs: list[list[_Segment]] = []
        stack: list[int] = []
        for m in token.finditer(self.xml):
            if m.group("pe"):
                paragraphs.append([])
            elif m.group("po"):
                stack.append(len(paragraphs))
                paragraphs.append([])
            elif m.group("pc"):
                if stack:
                    stack.pop()
            elif stack:
                if m.group("t"):
                    text = _xml_unescape(m.group("tc"))
                    paragraphs[stack[-1]].append(_Segment(m.start(), m.start("tc"), m.end("tc"), text, True, text))
                else:
                    ch = "\t" if m.group("tab") else "\n"
                    paragraphs[stack[-1]].append(_Segment(m.start(), m.start(), m.end(), ch, False, ch))
        return paragraphs

    def texts(self, breaks: bool = False) -> list[str]:
        """Paragraph texts; with breaks, tabs and line breaks are included."""
        return ["".join(s.text for s in p if s.editable or breaks) for p in self.paragraphs]

    def editable(self) -> list[list[_Segment]]:
        return [[s for s in p if s.editable] for p in self.paragraphs]

    def xml_bytes(self) -> bytes:
        changed = sorted((s for p in self.paragraphs for s in p if s.editable and s.text != s.original),
                         key=lambda s: s.content_start)
        out, last = [], 0
        for s in changed:
            tag = self.xml[s.tag_start:s.content_start]
            if s.text != s.text.strip() and "xml:space" not in tag:
                tag = tag[:-1] + ' xml:space="preserve">'
            out += [self.xml[last:s.tag_start], tag, _xml_escape(s.text)]
            last = s.content_end
        out.append(self.xml[last:])
        return (codecs.BOM_UTF8 if self.bom else b"") + "".join(out).encode("utf-8")

    def save(self) -> None:
        fd, tmp = tempfile.mkstemp(prefix=".tundlekit-", suffix=".docx",
                                   dir=str(pathlib.Path(self.path).resolve().parent))
        os.close(fd)
        try:
            with zipfile.ZipFile(tmp, "w") as z:
                for info in self.infos:
                    data = self.xml_bytes() if info.filename == self.part else self.parts[info.filename]
                    z.writestr(info, data)
                z.comment = self.comment
            os.replace(tmp, self.path)
        except OSError as e:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise ToolError(f"cannot write {self.path}: {e}") from None


def _replace_in_runs(segments: list[_Segment], find: str, replace: str) -> None:
    """Replace every occurrence of find in 1 paragraph. The replacement goes into the first run an occurrence
    touches; the rest of the occurrence is removed from the runs after it."""
    pos = 0
    while True:
        text = "".join(s.text for s in segments)
        start = text.find(find, pos)
        if start < 0:
            return
        end = start + len(find)
        offset, placed = 0, False
        for s in segments:
            a, b = offset, offset + len(s.text)
            offset = b
            if b <= start or a >= end:
                continue
            left = s.text[:max(0, start - a)]
            right = s.text[end - a:] if end < b else ""
            s.text = left + (replace if not placed else "") + right
            placed = True
        pos = start + len(replace)


def _edit_docx(path: str, edits: list[dict], write: bool) -> dict:
    doc = DocxText(path)
    before = doc.texts()
    paragraphs = doc.editable()
    applied, failures = 0, []
    for i, e in enumerate(edits):
        found = sum("".join(s.text for s in p).count(e["find"]) for p in paragraphs)
        if found != e["count"]:
            failures.append({"index": i, "find": e["find"], "found": found})
            continue
        for p in paragraphs:
            _replace_in_runs(p, e["find"], e["replace"])
        applied += 1
    after = doc.texts()
    if write and not failures and after != before:
        doc.save()
    return {"ok": not failures, "applied": applied, "failures": failures, "diff": _unified(before, after, path)}


# ====================================================================== Markdown to paragraphs (§15.4)
_MD_ESCAPE = re.compile(r"\\([\\`*_{}\[\]()#+\-.!|<>~])")
_PROTECT_CHARS = "\\`*_{}[]()#+-.!|<>~"
_CODE_SPAN = re.compile(r"(`+)(.+?)\1")
_MD_COMMENT = re.compile(r"<!--.*?-->", re.S)
_MD_IMAGE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_MD_REF_LINK = re.compile(r"\[([^\]]+)\]\[[^\]]*\]")
_MD_AUTOLINK = re.compile(r"<((?:https?|mailto):[^>\s]+)>")
_MD_EMPHASIS = re.compile(r"(?<![A-Za-z0-9])_+|_+(?![A-Za-z0-9])|(?<!\s)\*+|\*+(?!\s)")
_PROTECTED = re.compile("[-]")
_QUOTES = str.maketrans({"‘": "'", "’": "'", "‚": "'", "‛": "'", "′": "'",
                         "“": '"', "”": '"', "„": '"', "‟": '"', "″": '"'})


def _protect(text: str) -> str:
    return "".join(chr(0xE000 + ord(c)) if c in _PROTECT_CHARS else c for c in text)


def markdown_inline(text: str) -> str:
    """Strip inline Markdown: emphasis, code backticks, link and image markup (their text is kept)."""
    text = _MD_ESCAPE.sub(lambda m: _protect(m.group(1)), text)
    text = _CODE_SPAN.sub(lambda m: _protect(m.group(2).strip()), text)
    text = _MD_COMMENT.sub("", text)
    text = _MD_IMAGE.sub(r"\1", text)
    text = _MD_LINK.sub(r"\1", text)
    text = _MD_REF_LINK.sub(r"\1", text)
    text = _MD_AUTOLINK.sub(r"\1", text)
    text = _MD_EMPHASIS.sub("", text)
    return _PROTECTED.sub(lambda m: chr(ord(m.group(0)) - 0xE000), text).strip()


def _table_lines(lines: list[str]) -> set[int]:
    rows = set()
    for i, line in enumerate(lines):
        if _is_table_separator(line) and i > 0 and "|" in lines[i - 1]:
            rows.add(i - 1)
            j = i
            while j < len(lines) and "|" in lines[j] and lines[j].strip():
                rows.add(j)
                j += 1
        elif line.lstrip().startswith("|"):
            rows.add(i)
    return rows


def _table_cells(line: str) -> list[str]:
    body = line.strip()
    body = body[1:] if body.startswith("|") else body
    body = body[:-1] if body.endswith("|") and not body.endswith("\\|") else body
    return [c.strip() for c in re.split(r"(?<!\\)\|", body)]


def markdown_paragraphs(text: str) -> list[str]:
    """Reduce Markdown to paragraphs (§15.4): blocks joined into 1 line, headings, list items and table cells
    as their own paragraphs, fenced code lines kept one by one, inline markup stripped, empties dropped."""
    text = _MD_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text.replace("\r\n", "\n").replace("\r", "\n"))
    lines = _split_lines(text)
    start = 0
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() in ("---", "..."):
                start = j + 1
                break
    tables = _table_lines(lines)
    out: list[str] = []
    block: list[str] = []
    in_item = False
    fence = None

    def flush():
        nonlocal in_item
        if block:
            out.append(markdown_inline(" ".join(block)))
            block.clear()
        in_item = False

    for i in range(start, len(lines)):
        line = lines[i]
        if fence is not None:
            if fence.match(line):
                fence = None
            elif line.strip():
                out.append(line.rstrip())
            continue
        m = FENCE_OPEN.match(line)
        if m:
            flush()
            fence = _fence_close(m.group(1))
            continue
        if not line.strip():
            flush()
            continue
        if i in tables:
            flush()
            if not _is_table_separator(line):
                out += [markdown_inline(c) for c in _table_cells(line)]
            continue
        heading = HEADING.match(line.strip()) if line.startswith(("#", " #", "  #", "   #")) else None
        if heading:
            flush()
            out.append(markdown_inline((heading.group(2) or "").rstrip("#")))
            continue
        if THEMATIC_BREAK.match(line):
            flush()
            continue
        quote = QUOTE_PREFIX.match(line)
        body = line[quote.end():] if quote else line
        item = LIST_ITEM.match(body)
        if item:
            flush()
            block.append(body[item.end():].strip())
            in_item = True
        elif in_item and not line[:1].isspace():
            flush()
            block.append(body.strip())
        else:
            block.append(body.strip())
    flush()
    return [p for p in out if p.strip()]


def normalise_paragraph(text: str) -> str:
    """Whitespace collapsed, curly quotes and apostrophes folded to straight ones."""
    return " ".join(text.translate(_QUOTES).split())


def document_paragraphs(path: str, arg: str) -> list[str]:
    """Non-empty paragraphs of a .docx (from its main document) or a Markdown file."""
    if pathlib.Path(path).suffix.lower() == ".docx":
        if not pathlib.Path(path).is_file():
            raise ToolError(f"{arg}: no such file: {path}")
        return [p for p in DocxText(path, arg).texts(breaks=True) if p.strip()]
    text, _ = _read_raw(path, arg)
    return markdown_paragraphs(text)


# ====================================================================== hints (§15.4)
HINT_SUFFIXES = (".py", ".json", ".md")


class HintIndex:
    """Find where a string occurs in the files under `search` (directories walked for .py, .json and .md)."""

    def __init__(self, search: list[str] | None):
        self.files = []
        for entry in search or []:
            p = pathlib.Path(entry)
            if p.is_dir():
                self.files += _walk(entry, HINT_SUFFIXES)
            elif p.is_file():
                self.files.append((_display(entry), p))
            else:
                raise ToolError(f"search: no such file or directory: {entry}")
        self._texts: dict[str, str] = {}

    def _text(self, shown: str, p: pathlib.Path) -> str:
        if shown not in self._texts:
            try:
                raw = p.read_bytes().decode("utf-8-sig", "replace")
            except OSError:
                raw = ""
            self._texts[shown] = raw.replace("\r\n", "\n").replace("\r", "\n")
        return self._texts[shown]

    def _occurrences(self, needle: str, limit: int) -> list[str]:
        hits = []
        for shown, p in self.files:
            text = self._text(shown, p)
            pos = text.find(needle)
            while pos >= 0 and len(hits) < limit:          # 1 hit per line
                hits.append(f"{shown}:{text.count(chr(10), 0, pos) + 1}")
                next_line = text.find("\n", pos)
                pos = -1 if next_line < 0 else text.find(needle, next_line + 1)
            if len(hits) >= limit:
                break
        return hits

    def hints(self, old: str, limit: int = 3) -> list[str]:
        """Up to `limit` 'path:line' locations of old, or of its longest line of 12+ characters."""
        if not self.files or not old:
            return []
        hits = self._occurrences(old, limit)
        if hits:
            return hits
        longest = max(old.splitlines() or [""], key=len).strip()
        if len(longest) >= 12 and longest != old:
            return self._occurrences(longest, limit)
        return []


# ====================================================================== tools (§15)
@tool("text_xref",
      "Resolve cross-references against a report and renumber them. Targets in the report: numbered headings "
      "(§N, §N.M), '## Appendix X.' and '### X.n' headings (App. X, App. X.n), and Fig./Table captions. Every "
      "§N, App. X(.n), Fig. Pn and Table Pn in `files` (deck scripts, specs, presenter packs; directories are "
      "walked) must hit a target (X001, error); mentions after 'arXiv' or 'paper' are skipped. X002 (warning): a "
      "between(...)/section(...) marker in a .py file that the report does not hold exactly once. `renumber` "
      "(e.g. ['Fig. 9=Fig. 10', 'Fig. 10=Fig. 9']) is applied simultaneously to the files and to the report's "
      "headings, captions and prose; whole references only. Without write it only lists the edits. Returns "
      "{ok, findings, counts, edits: [{path, line, old, new}]}.",
      {"type": "object",
       "properties": {
           "report": {"type": "string", "description": "The Markdown report that defines the targets."},
           "files": {"type": "array", "items": {"type": "string"}, "description": "Files to check."},
           "renumber": {"type": "array", "items": {"type": "string"}, "description": "OLD=NEW references."},
           "write": {"type": "boolean", "description": "Rewrite the files (default false: dry run)."},
       },
       "required": ["report"],
       "additionalProperties": False},
      readOnlyHint=False, destructiveHint=False)
def text_xref(report: str, files: list[str] | None = None, renumber: list[str] | None = None,
              write: bool = False) -> dict:
    mapping = _parse_renumber(_str_list(renumber, "renumber"))
    report_text, report_bom = _read_raw(report, "report")
    report_shown = _display(report)
    report_lf = report_text.replace("\r\n", "\n").replace("\r", "\n")
    targets = report_targets(report_lf)
    report_key = os.path.normcase(os.path.abspath(report))

    checked = []
    for shown, p in _xref_files(_str_list(files, "files")):
        text, bom = _read_raw(str(p), "files")
        checked.append((shown, p, text, bom))

    findings = []
    for shown, p, text, _ in checked:
        for lineno, line in enumerate(_lines_keepends(text), 1):
            body, _ = _split_ending(line)
            for m, key in find_references(body):
                if key not in targets:
                    findings.append(_finding("X001", "error", shown, lineno,
                                             f"{ref_label(key)} has no target in {report_shown}",
                                             _excerpt(body, m.start(), m.end())))
        if p.suffix.lower() == ".py":
            findings += _marker_findings(shown, text, report_shown, report_lf)

    edits, writes = [], []
    if mapping:
        for shown, p, text, bom in checked:
            if os.path.normcase(os.path.abspath(p)) == report_key:
                continue
            new_text, line_edits = _renumber_text(text, mapping, is_report=False)
            edits += [{"path": shown, "line": n, "old": old, "new": new} for n, old, new in line_edits]
            if line_edits:
                writes.append((str(p), new_text, bom))
        new_report, line_edits = _renumber_text(report_text, mapping, is_report=True)
        edits += [{"path": report_shown, "line": n, "old": old, "new": new} for n, old, new in line_edits]
        if line_edits:
            writes.append((report, new_report, report_bom))
    if write:
        for path, text, bom in writes:
            _write_text(path, text, bom)
    return _checker_result(findings, edits=edits)


@tool("text_apply_edits",
      "Anchored find and replace in a text file or a .docx. edits: [{find, replace, count (default 1)}]. Each "
      "find must occur exactly count times in the current text; edits apply in order, each to the previous "
      "result. If any edit fails nothing is written and every failure is listed. In a .docx, find must lie "
      "within 1 paragraph (it may span runs; the replacement goes into the first run touched) and every other "
      "package part is copied unchanged. Line endings are preserved. Without write it is a dry run. Returns "
      "{ok, applied, failures: [{index, find, found}], diff}.",
      {"type": "object",
       "properties": {
           "edits": {"type": "array", "items": {"type": "object"},
                     "description": "[{find, replace, count}] applied in order."},
           "path": {"type": "string", "description": "The text file or .docx to edit."},
           "write": {"type": "boolean", "description": "Write the result (default false: dry run)."},
       },
       "required": ["edits", "path"],
       "additionalProperties": False},
      readOnlyHint=False, destructiveHint=False)
def text_apply_edits(edits: list, path: str, write: bool = False) -> dict:
    checked = _check_edits(edits)
    if pathlib.Path(path).suffix.lower() == ".docx":
        if not pathlib.Path(path).is_file():
            raise ToolError(f"path: no such file: {path}")
        return _edit_docx(path, checked, write)
    return _edit_text_file(path, checked, write)


@tool("docx_diff",
      "Compare 2 documents paragraph by paragraph to carry hand edits back into build scripts: 2 .docx files, "
      "or a .docx and a Markdown file (either order). Markdown is reduced to paragraphs (blocks joined, "
      "headings, emphasis, code and link markup stripped, list items and table cells separate, fenced code "
      "lines kept). Paragraphs are compared after collapsing whitespace and folding curly quotes. Returns "
      "{changes: [{op: replace|insert|delete, old: [str], new: [str], old_index, new_index, hint}]} with "
      "0-based indexes and raw paragraph text; hint lists up to 3 'path:line' places under `search` (.py, "
      ".json, .md) where the first old paragraph occurs.",
      {"type": "object",
       "properties": {
           "old": {"type": "string", "description": "The earlier .docx or .md file."},
           "new": {"type": "string", "description": "The edited .docx or .md file."},
           "search": {"type": "array", "items": {"type": "string"},
                      "description": "Files or directories to search for hints."},
       },
       "required": ["old", "new"],
       "additionalProperties": False},
      readOnlyHint=True)
def docx_diff(old: str, new: str, search: list[str] | None = None) -> dict:
    a = document_paragraphs(old, "old")
    b = document_paragraphs(new, "new")
    index = HintIndex(_str_list(search, "search"))
    matcher = difflib.SequenceMatcher(None, [normalise_paragraph(p) for p in a],
                                      [normalise_paragraph(p) for p in b], autojunk=False)
    changes = []
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            continue
        changes.append({"op": op, "old": a[i1:i2], "new": b[j1:j2], "old_index": i1, "new_index": j1,
                        "hint": index.hints(a[i1]) if i2 > i1 else []})
    return {"changes": changes}


# ====================================================================== CLI
def add_cli(groups) -> None:
    from tundlekit.cli_support import common_flags

    p = groups.add_parser("text", help="report prose, numbering and word-count checks")
    cmds = p.add_subparsers(dest="command", required=True)

    c = cmds.add_parser("lint", help="check prose against the house style (S001-S011)")
    c.add_argument("paths", nargs="+", metavar="PATH")
    c.add_argument("--rules", action="append", help="only these rules, comma-separated (e.g. S001,S002)")
    c.add_argument("--ignore", action="append", help="skip these rules, comma-separated")
    c.add_argument("--max-words", type=int, default=DEFAULT_MAX_WORDS, help="S009 limit (default 42)")
    c.add_argument("--band", type=_band_arg, metavar="LOW,HIGH",
                   help="S012 band for the mean sentence length (default 15,25)")
    common_flags(c, checker=True)
    c.set_defaults(handler=_cli_lint)

    c = cmds.add_parser("fignums", help="check figure and table numbering (F001-F005)")
    c.add_argument("paths", nargs="+", metavar="REPORT")
    c.add_argument("--refs", nargs="+", action="extend", default=[], metavar="FILE",
                   help="other files whose mentions must resolve against the reports")
    common_flags(c, checker=True)
    c.set_defaults(handler=_cli_fignums)

    c = cmds.add_parser("wordcount", help="words per section, optionally against a git baseline")
    c.add_argument("paths", nargs="+", metavar="PATH")
    c.add_argument("--baseline", metavar="GITREF", help="compare with the files at this git ref")
    c.add_argument("--baseline-file", metavar="PATH", help="compare with this file instead of a git ref")
    c.add_argument("--no-tables", dest="tables", action="store_false", help="leave table rows out of the counts")
    common_flags(c)
    c.set_defaults(handler=_cli_wordcount)

    c = cmds.add_parser("xref", help="resolve §/App./Fig./Table references against a report, and renumber")
    c.add_argument("report", metavar="REPORT")
    c.add_argument("--in", dest="files", nargs="+", action="extend", default=[], metavar="FILE",
                   help="files whose references must resolve (deck scripts, specs, presenter packs)")
    c.add_argument("--renumber", nargs="+", action="extend", default=[], metavar="OLD=NEW",
                   help="renumber references, e.g. 'Fig. 9=Fig. 10' (all applied at once)")
    c.add_argument("--write", action="store_true", help="rewrite the files (default: list the edits)")
    common_flags(c, checker=True)
    c.set_defaults(handler=_cli_xref)

    c = cmds.add_parser("apply-edits", help="anchored find and replace in a text file or .docx")
    c.add_argument("edits_path", metavar="EDITS.json", help="a JSON list of {find, replace, count}")
    c.add_argument("path", metavar="FILE")
    c.add_argument("--write", action="store_true", help="write the result (default: dry run)")
    common_flags(c)
    c.set_defaults(handler=_cli_apply_edits)

    c = cmds.add_parser("docx-diff", help="paragraph changes between 2 .docx files, or a .docx and a .md")
    c.add_argument("old", metavar="OLD")
    c.add_argument("new", metavar="NEW")
    c.add_argument("--search", nargs="+", action="extend", default=[], metavar="PATH",
                   help="files or directories to search for where the old text comes from")
    common_flags(c)
    c.set_defaults(handler=_cli_docx_diff)


def _cli_xref(args):
    from tundlekit.cli_support import CliResult, format_findings

    res = text_xref(args.report, files=args.files, renumber=args.renumber, write=args.write)
    lines = [format_findings(res)]
    if res["edits"]:
        verb = "edited" if args.write else "planned edits (use --write to apply)"
        lines.append(f"{verb}:")
        lines += [f"  {e['path']}:{e['line']}: {e['old']} -> {e['new']}" for e in res["edits"]]
    return CliResult(res, text="\n".join(lines))


def _cli_apply_edits(args):
    import json

    from tundlekit.cli_support import CliResult

    text, _ = _read_raw(args.edits_path, "edits")
    try:
        edits = json.loads(text)
    except ValueError as e:
        raise ToolError(f"edits: {args.edits_path} is not valid JSON: {e}") from None
    if isinstance(edits, dict) and "edits" in edits:
        edits = edits["edits"]
    res = text_apply_edits(edits, args.path, write=args.write)
    lines = [res["diff"]] if res["diff"] else []
    lines += [f"edit {f['index']}: {f['find']!r} found {f['found']} time(s)" for f in res["failures"]]
    state = "written" if args.write and res["ok"] else "dry run" if res["ok"] else "nothing written"
    lines.append(f"{'ok' if res['ok'] else 'FAILED'}: {res['applied']} edit(s) applied, "
                 f"{len(res['failures'])} failed ({state})")
    return CliResult(res, text="\n".join(lines))


def _cli_docx_diff(args):
    from tundlekit.cli_support import CliResult

    res = docx_diff(args.old, args.new, search=args.search)
    lines = []
    for c in res["changes"]:
        lines.append(f"{c['op']} at old {c['old_index']} / new {c['new_index']}"
                     + (f"  (see {', '.join(c['hint'])})" if c["hint"] else ""))
        lines += [f"  - {p}" for p in c["old"]] + [f"  + {p}" for p in c["new"]]
    lines.append(f"{len(res['changes'])} change(s)")
    return CliResult(res, text="\n".join(lines))


def _cli_lint(args):
    from tundlekit.cli_support import CliResult

    return CliResult(text_lint(args.paths, rules=args.rules, ignore=args.ignore, max_words=args.max_words,
                               band=args.band))


def _band_arg(value: str) -> list:
    import argparse

    parts = value.split(",")
    try:
        if len(parts) != 2:
            raise ValueError
        return [_number(p) for p in parts]
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected LOW,HIGH (e.g. 15,25), got {value!r}") from None


def _number(text: str):
    text = text.strip()
    try:
        return int(text)
    except ValueError:
        return float(text)


def _cli_fignums(args):
    from tundlekit.cli_support import CliResult

    return CliResult(text_fignums(args.paths, refs=args.refs or None))


def _cli_wordcount(args):
    from tundlekit.cli_support import CliResult

    res = text_wordcount(args.paths, baseline=args.baseline, baseline_file=args.baseline_file,
                         tables=args.tables)
    against = args.baseline if args.baseline is not None else args.baseline_file
    lines = []
    for path, info in res["files"].items():
        lines.append(f"=== {path} ===")
        lines.append(f"{'words':>7} {'delta':>7}  section")
        for s in info["sections"]:
            delta = "n/a" if s["delta"] is None else (s["delta"] if s["delta"] == "new" else f"{s['delta']:+d}")
            lines.append(f"{s['words']:>7} {delta:>7}  {s['heading'][:78]}")
        tail = "" if info["total_delta"] is None else f" ({info['total_delta']:+d} vs {against})"
        lines.append(f"{info['total']:>7} {'':>7}  TOTAL{tail}")
        lines.append("        buckets: " + ", ".join(f"{k} {v}" for k, v in info["buckets"].items()))
    return CliResult(res, text="\n".join(lines))
