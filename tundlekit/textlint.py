"""textlint: report prose and numbering checks (MANIFEST.md §7). Standard library only.

After tundle's style card (notes/40-style-card.md) and its checks (check_forbidden.py, check_fignums.py,
wordcount_sections.py): no em dashes, no first person, no hedges, no contractions, no status markers left in
the text, figure and table numbers that run 1, 2, 3 with every mention resolving, and words per section.
"""
from __future__ import annotations

import ast
import bisect
import codecs
import copy
import difflib
import fnmatch
import io
import json
import math
import os
import pathlib
import posixpath
import re
import shutil
import stat
import struct
import subprocess
import tempfile
import zipfile
import zlib
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


_GIT_BASH_DRIVE = re.compile(r"^/([A-Za-z])(?=/|$)")


def native_path(path: str) -> str:
    """§16.1: on Windows, a Git Bash path `/c/x` names `C:/x`; other spellings are returned unchanged."""
    if os.name == "nt" and isinstance(path, str):
        m = _GIT_BASH_DRIVE.match(path)
        if m and not os.path.exists(path):
            return f"{m.group(1).upper()}:" + (path[m.end():] or "/")
    return path


def path_key(path) -> str:
    """The identity of a file for deduplication: resolved (symlinks followed), case-folded where the OS is."""
    p = native_path(str(path))
    try:
        p = os.path.realpath(p)
    except (OSError, ValueError):
        p = os.path.abspath(p)
    return os.path.normcase(p)


def expand_paths(paths, arg: str = "paths") -> list[tuple[str, pathlib.Path]]:
    """Files named directly, plus *.md and *.txt under named directories (hidden directories skipped).

    Returns [(display path with / separators, filesystem path)], without duplicates, in argument order.
    """
    if not paths:
        raise ToolError(f"{arg}: give at least 1 file or directory")
    out, seen = [], set()
    for given in paths:
        p = pathlib.Path(native_path(given))
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
            key = path_key(f)
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
MAY_HEDGE_NEXT = ("be", "have", "well", "also", "help", "seem", "lead", "cause")   # §16.8: `may not` is not
PARTICIPLES_IRREGULAR = {"bound", "built", "chained", "kept", "made", "run", "set", "shown", "split", "used",
                         "written"}
QUOTED = re.compile(r'"[^"\n]*"|“[^”\n]*”')
HEDGES = re.compile(r"(?i:\b(?:arguably|seems|seem|seemingly|perhaps|somewhat|possibly|might"
                    r"|to\s+some\s+extent|it\s+appears)\b)"
                    r"|\bmay\b")
NEXT_WORDS = re.compile(r"[^\W\d_][\w'’-]*")
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


def _is_participle(word: str) -> bool:
    word = word.lower()
    return word in PARTICIPLES_IRREGULAR or (len(word) > 3 and word.endswith(("ed", "en")))


def _may_is_hedge(words: list[str]) -> bool:
    """§14.1/§16.8: lower-case `may` is a hedge only before the listed words, and not before be + participle."""
    if not words or words[0].lower() not in MAY_HEDGE_NEXT:
        return False
    return not (words[0].lower() == "be" and len(words) > 1 and _is_participle(words[1]))


def _line_findings(path: str, lineno: int, masked: str, original: str, kind: str, exempt: bool,
                   questions_ok: bool = False, next_words: list | None = None,
                   skip: frozenset = frozenset()) -> list:
    """Line rules for 1 line. kind is "heading", "prose" or "table"; exempt: inside an S008-exempt section;
    questions_ok: inside a question section (no S007); next_words: the first words of the next prose line;
    skip: rules that do not apply to this line (§16.8)."""
    out = []
    next_words = next_words or []
    quoted = None
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
        if rule in skip:
            continue
        for m in pattern.finditer(masked):
            if rule == "S002" and m.group(0) == "US":
                continue
            if rule == "S003":
                if quoted is None:
                    quoted = [x.span() for x in QUOTED.finditer(masked)]
                if any(a < m.start() < b for a, b in quoted):
                    continue
                if m.group(0) == "may":
                    words = NEXT_WORDS.findall(masked[m.end():])[:2]
                    if len(words) < 2:                     # the phrase continues on the next line
                        words = (words + next_words)[:2]
                    if not _may_is_hedge(words):
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


def _next_words(doc: _Structure, masked: list[str], idx: int) -> list[str]:
    """The first 2 words of the prose line after line idx (0-based), or [] when the next line is not prose."""
    k = idx + 1
    if k >= len(doc.kinds) or doc.kinds[k] is None or doc.kinds[k][0] != "prose":
        return []
    line = masked[k]
    quote = QUOTE_PREFIX.match(line)
    start = quote.end() if quote else 0
    if LIST_ITEM.match(line, start):
        return []
    return NEXT_WORDS.findall(line[start:])[:2]


ASK_INTRO = re.compile(r"ask", re.IGNORECASE)


def _line_skips(lines: list[str], masked: list[str], kinds: list) -> list[frozenset]:
    """Per line, the rules §16.8 switches off: S005 on captions and blockquotes, S007 in ask lists (list items
    under a line ending in ':' that contains 'ask')."""
    out = []
    ask_list = False
    for idx, kind in enumerate(kinds):
        if kind is None:
            out.append(frozenset())
            continue
        if kind[0] != "prose":
            ask_list = False
            out.append(frozenset())
            continue
        skip = set()
        mline = masked[idx]
        stripped = lines[idx].strip()
        if QUOTE_PREFIX.match(mline) or FIG_CAPTION.match(stripped) or TABLE_CAPTION.match(stripped):
            skip.add("S005")
        if LIST_ITEM.match(mline) or (ask_list and mline[:1].isspace()):
            if ask_list:
                skip.add("S007")
        else:
            body = mline.rstrip()
            ask_list = body.endswith(":") and ASK_INTRO.search(body) is not None
        out.append(frozenset(skip))
    return out


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
    skips = _line_skips(lines, masked, doc.kinds)
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
        next_words = _next_words(doc, masked, idx) if kind[0] == "prose" else []
        findings += _line_findings(path, idx + 1, masked[idx], lines[idx], kind[0], exempt_level is not None,
                                   question_level is not None, next_words, skips[idx])

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


_path_key = path_key


def _bound_refs(entries: list[str], report_keys: dict[str, str]) -> list[tuple[str, str | None]]:
    """[(refs file, shown name of the report it is bound to, or None)] from FILE and FILE=REPORT entries (§14.3).

    An entry that names an existing path is a plain FILE, even when it contains '='. Otherwise it is split at
    the '=' whose right side is 1 of the reports; REPORT must be 1 of `paths`.
    """
    out = []
    for entry in entries:
        if not isinstance(entry, str):
            raise ToolError("refs: must be a list of strings")
        if "=" not in entry or os.path.exists(native_path(entry)):
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
        if not isinstance(baseline_file, str) or not pathlib.Path(native_path(baseline_file)).is_file():
            raise ToolError(f"baseline_file: no such file: {baseline_file}")
        fixed_old = section_counts(_read(_display(baseline_file), pathlib.Path(native_path(baseline_file))),
                                   tables)
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
    p = pathlib.Path(native_path(path))
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


def replace_file(path: str, data: bytes) -> None:
    """§16.1: write data atomically (a temporary file in the same folder, then replace), keeping the file's
    permission bits, and writing through a symlink to its target."""
    target = pathlib.Path(os.path.realpath(native_path(str(path))))
    try:
        mode = stat.S_IMODE(os.stat(target).st_mode)
    except OSError:                                 # a new file: the default permissions
        umask = os.umask(0)
        os.umask(umask)
        mode = 0o666 & ~umask
    try:
        fd, tmp = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent))
    except OSError as e:
        raise ToolError(f"cannot write {path}: {e}") from None
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        if mode is not None:
            os.chmod(tmp, mode)
        os.replace(tmp, target)
    except OSError as e:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise ToolError(f"cannot write {path}: {e}") from None


_replace_file = replace_file


def _write_text(path: str, text: str, bom: bool) -> None:
    _replace_file(path, (codecs.BOM_UTF8 if bom else b"") + text.encode("utf-8"))


def _str_list(value, arg: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ToolError(f"{arg}: must be a list of strings")
    return value


# ====================================================================== xref (§15.2, §16.5)
XREF = re.compile(
    r"§\s?(?P<sec>\d+(?:\.\d+)*)"
    r"|\bApp\.\s?(?P<app>[A-Z](?:\.\d+)?)(?![A-Za-z0-9]|\.\d)"
    r"|\bFig\.\s?(?P<fig>[A-Z]?\d+)(?!\d|\.\d)"
    r"|\bTable\s(?P<tab>[A-Z]?\d+)(?!\d|\.\d)")
SECTION_HEADING = re.compile(r"^#{1,6}[ \t]+(\d+(?:\.\d+)*)(?=[.\s]|$)")
APPENDIX_HEADING = re.compile(r"^#{1,6}[ \t]+Appendix[ \t]+([A-Z])(?![A-Za-z0-9])")
APPENDIX_SUB_HEADING = re.compile(r"^#{1,6}[ \t]+([A-Z]\.\d+)(?!\d|\.\d)")
H1_TITLE = re.compile(r"^#[ \t]+(.*?)[ \t#]*$")
REPORT_NAME = re.compile(r"\b([A-Za-z][\w-]*)[ \t]+report\b", re.IGNORECASE)
NOT_A_REPORT_NAME = {"the", "this", "that", "a", "an", "our", "its", "same", "whole", "full", "main", "each",
                     "every", "which", "whose", "his", "her", "their", "your", "my"}
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


def _fenced_lines(lines: list[str]) -> set[int]:
    """0-based indexes of lines inside fenced code (fence lines included)."""
    out, fence = set(), None
    for i, line in enumerate(lines):
        if fence is None:
            m = FENCE_OPEN.match(line)
            if m:
                fence = _fence_close(m.group(1))
                out.add(i)
        else:
            out.add(i)
            if fence.match(line):
                fence = None
    return out


def report_name(text: str, path: str) -> str:
    """§16.5 pinned: the report's own name: its H1 title (lower-cased) when that ends in 'report', otherwise
    the parent directory name with 'report-X' read as 'X report'."""
    lines = _split_lines(text)
    fenced = _fenced_lines(lines)
    for i, line in enumerate(lines):
        if i in fenced:
            continue
        m = H1_TITLE.match(line)
        if m:
            title = " ".join(m.group(1).lower().split())
            if re.search(r"\breport$", title):
                return title
            break
    parent = pathlib.Path(os.path.abspath(native_path(path))).parent.name.lower()
    m = re.fullmatch(r"report[-_ ](.+)", parent)
    if m:
        return f"{m.group(1).replace('-', ' ').replace('_', ' ')} report"
    return parent


def _singular(word: str) -> str:
    return word[:-1] if len(word) > 3 and word.endswith("s") else word


def _names_own_report(word: str, own: str) -> bool:
    own_words = own.split()
    if len(own_words) < 2:
        return False
    return _singular(word.lower()) == _singular(own_words[-2])


def find_references(line: str, own_report: str | None = None) -> list[tuple[re.Match, tuple[str, str]]]:
    """Every §N(.M)*, App. X(.n), Fig. Pn and Table Pn in a line, except those after `arXiv` or `paper`
    (§15.2), inside a citation bracket that starts with a number, or after another report's name (§16.5)."""
    citations = None
    out = []
    for m in XREF.finditer(line):
        head = line[:m.start()]
        if CITED_PAPER.search(head):
            continue
        if citations is None:
            citations = _citation_spans(line)
        if any(a < m.start() < b for a, b in citations):
            continue
        if own_report is not None and any(
                w.group(1).lower() not in NOT_A_REPORT_NAME and not _names_own_report(w.group(1), own_report)
                for w in REPORT_NAME.finditer(head)):
            continue
        out.append((m, _ref_key(m)))
    return out


def _report_heading(line: str):
    """(kind, id, span of the id) for a numbered or appendix heading line, else None."""
    for pattern, kind in ((SECTION_HEADING, "§"), (APPENDIX_HEADING, "App"), (APPENDIX_SUB_HEADING, "App")):
        m = pattern.match(line)
        if m:
            return kind, m.group(1), m.span(1)
    return None


def report_targets(text: str) -> set[tuple[str, str]]:
    """Reference keys a report defines: numbered headings, appendix headings, figure and table captions.
    Fenced code holds no targets (§16.5)."""
    lines = _split_lines(text)
    fenced = _fenced_lines(lines)
    targets = set()
    for i, line in enumerate(lines):
        if i in fenced:
            continue
        heading = _report_heading(line)
        if heading:
            targets.add(heading[:2])
    seqs, _ = _captions("\n".join("" if i in fenced else line for i, line in enumerate(lines)))
    for (kind, prefix), seq in seqs.items():
        targets.update((kind, f"{prefix}{number}") for number, _ in seq)
    return targets


def walk_inputs(paths: list[str], suffixes: tuple, arg: str, exclude=None,
                seen: set | None = None) -> list[tuple[str, pathlib.Path]]:
    """Files given directly plus files with `suffixes` under given directories, deduplicated by resolved path
    (§16.1: C:/x, C:\\x and /c/x are 1 input). `exclude` globs drop walked files."""
    out = []
    seen = set() if seen is None else seen
    for given in paths:
        p = pathlib.Path(native_path(given))
        if p.is_dir():
            found = _walk(str(p), suffixes, _display(given))
            found = [(shown, f) for shown, f in found if not _excluded(shown, f, p, exclude)]
        elif p.is_file():
            found = [(_display(given), p)]
        else:
            raise ToolError(f"{arg}: no such file or directory: {given}")
        for shown, f in found:
            key = path_key(f)
            if key not in seen:
                seen.add(key)
                out.append((shown, f))
    return out


def _excluded(shown: str, f: pathlib.Path, base: pathlib.Path, exclude) -> bool:
    if not exclude:
        return False
    rel = f.relative_to(base).as_posix()
    candidates = (shown, rel, f.name, _display(str(f)))
    for pattern in exclude:
        pat = _display(pattern)
        for c in candidates:
            if fnmatch.fnmatchcase(c, pat) or fnmatch.fnmatchcase(c, pat.rstrip("/") + "/*") \
                    or fnmatch.fnmatchcase(c, "*/" + pat) or fnmatch.fnmatchcase(c, "*/" + pat.rstrip("/") + "/*"):
                return True
    return False


def _xref_files(paths: list[str]) -> list[tuple[str, pathlib.Path]]:
    return walk_inputs(paths, XREF_SUFFIXES, "files")


def _walk(base: str, suffixes: tuple, shown_base: str | None = None) -> list[tuple[str, pathlib.Path]]:
    """Files under base with the given suffixes (hidden folders skipped), as (base joined with the relative
    path using /, path), sorted by relative path."""
    root = pathlib.Path(base)
    shown_base = base if shown_base is None else shown_base
    found = []
    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for name in files:
            if name.lower().endswith(suffixes):
                f = pathlib.Path(folder) / name
                found.append((f.relative_to(root).as_posix(), f))
    return [(posixpath.join(_display(shown_base), rel), f) for rel, f in sorted(found, key=lambda t: t[0])]


# ---------------------------------------------------------------------- slice sources (§16.5)
_UNRESOLVED = object()
PATH_WRAPPERS = {"read_text", "read_bytes", "open", "resolve", "absolute", "expanduser", "as_posix"}


class _ModulePaths:
    """Module-level path bindings of a build script: anchors (paths of __file__) and .md sources."""

    def __init__(self, tree: ast.Module, script: pathlib.Path):
        self.script = script
        self.anchors: dict[str, pathlib.Path] = {}
        self.sources: dict[str, object] = {}          # name -> Path, or _UNRESOLVED
        self.bound: set[str] = set()
        for node in tree.body:
            targets, value = [], None
            if isinstance(node, ast.Assign):
                targets, value = node.targets, node.value
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                targets, value = [node.target], node.value
            names = [t.id for t in targets if isinstance(t, ast.Name)]
            if not names:
                continue
            self.bound.update(names)
            anchor = self._anchor(value)
            if anchor is not None:
                for name in names:
                    self.anchors[name] = anchor
                continue
            literals = [n.value for n in ast.walk(value) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
            if any(lit.rstrip().lower().endswith(".md") for lit in literals):
                resolved = self._source(value, literals)
                for name in names:
                    self.sources.setdefault(name, resolved)

    def _anchor(self, node) -> pathlib.Path | None:
        """The directory or file an expression built only from __file__ and anchors names, else None."""
        if isinstance(node, ast.Name):
            if node.id == "__file__":
                return self.script
            return self.anchors.get(node.id)
        if isinstance(node, ast.Call):
            func = node.func
            fname = func.attr if isinstance(func, ast.Attribute) else func.id if isinstance(func, ast.Name) else None
            if fname in ("Path", "PurePath", "realpath", "abspath") and len(node.args) == 1:
                return self._anchor(node.args[0])
            if fname == "dirname" and len(node.args) == 1:
                inner = self._anchor(node.args[0])
                return inner.parent if inner is not None else None
            if fname in ("resolve", "absolute") and isinstance(func, ast.Attribute) and not node.args:
                return self._anchor(func.value)
            return None
        if isinstance(node, ast.Attribute) and node.attr == "parent":
            inner = self._anchor(node.value)
            return inner.parent if inner is not None else None
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) \
                and node.value.attr == "parents":
            inner = self._anchor(node.value.value)
            index = node.slice
            if inner is not None and isinstance(index, ast.Constant) and isinstance(index.value, int) \
                    and not isinstance(index.value, bool) and 0 <= index.value < len(inner.parents):
                return inner.parents[index.value]
        return None

    def _path_parts(self, node) -> tuple[list[str], list]:
        """(string literals, bases) of the path-building part of an expression, in order. A base is an anchor
        path, or a string naming something that is not an anchor."""
        anchor = None if isinstance(node, ast.Constant) else self._anchor(node)
        if anchor is not None:
            return [], [anchor]
        if isinstance(node, ast.Constant):
            return ([node.value], []) if isinstance(node.value, str) else ([], [])
        if isinstance(node, ast.Name):
            return [], [node.id]
        if isinstance(node, ast.BinOp):
            l1, n1 = self._path_parts(node.left)
            l2, n2 = self._path_parts(node.right)
            return l1 + l2, n1 + n2
        if isinstance(node, (ast.Attribute, ast.Subscript)):
            return self._path_parts(node.value)
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in PATH_WRAPPERS:
                return self._path_parts(func.value)
            fname = func.attr if isinstance(func, ast.Attribute) else func.id if isinstance(func, ast.Name) else ""
            args = node.args[:1] if fname in ("open", "Path", "PurePath", "str") else node.args
            if fname not in ("open", "Path", "PurePath", "str", "join", "abspath", "realpath"):
                return [], ["<call>"]
            lits, names = [], []
            for arg in args:
                l1, n1 = self._path_parts(arg)
                lits += l1
                names += n1
            return lits, names
        return [], ["<expr>"]

    def _source(self, value, literals: list[str]) -> object:
        """Resolve an .md source binding: an anchor joined with the literals, or the literals relative to the
        script's directory and its parents (up to 4 levels)."""
        parts, names = self._path_parts(value)
        if not parts or not parts[-1].rstrip().lower().endswith(".md"):
            return _UNRESOLVED
        if any(isinstance(n, str) for n in names):
            return _UNRESOLVED
        anchors = names
        rel = pathlib.PurePosixPath(*[p.replace("\\", "/") for p in parts])
        if anchors:
            base = anchors[0]
            base = base.parent if base == self.script else base
            candidate = pathlib.Path(base) / rel
            return candidate if candidate.is_file() else _UNRESOLVED
        if pathlib.PurePath(str(rel)).is_absolute() or re.match(r"^[A-Za-z]:", str(rel)):
            candidate = pathlib.Path(native_path(str(rel)))
            return candidate if candidate.is_file() else _UNRESOLVED
        folder = self.script.parent
        for _ in range(5):
            candidate = folder / rel
            if candidate.is_file():
                return candidate
            if folder.parent == folder:
                break
            folder = folder.parent
        return _UNRESOLVED

    def resolve(self, name: str) -> object:
        if name in self.sources:
            return self.sources[name]
        return _UNRESOLVED


def _call_name(call: ast.Call) -> str | None:
    func = call.func
    return func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else None


def _default_source(tree: ast.Module, paths: _ModulePaths) -> object:
    """The source a between()/section() call without src slices: the default of a `src` parameter bound to an
    .md name (None: use the report)."""
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name not in MARKER_CALLS:
            continue
        args = node.args
        positional = args.posonlyargs + args.args
        defaults = dict(zip([a.arg for a in positional][len(positional) - len(args.defaults):], args.defaults))
        defaults.update({a.arg: d for a, d in zip(args.kwonlyargs, args.kw_defaults) if d is not None})
        default = defaults.get("src")
        if isinstance(default, ast.Name) and default.id in paths.sources:
            resolved = paths.resolve(default.id)
            if resolved is not _UNRESOLVED:
                return resolved
    return None


def _call_source(call: ast.Call, paths: _ModulePaths):
    """(True, name or None) when the call names its source, else (False, None). name None: not a plain name."""
    for kw in call.keywords:
        if kw.arg == "src":
            return True, kw.value.id if isinstance(kw.value, ast.Name) else None
    if len(call.args) >= 3 and isinstance(call.args[2], ast.Name):
        return True, call.args[2].id
    return False, None


def _marker_calls(tree: ast.Module) -> list[ast.Call]:
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and _call_name(n) in MARKER_CALLS]
    return sorted(calls, key=lambda c: (c.lineno, c.col_offset))


def _marker_literals(call: ast.Call) -> list[tuple[int, ast.Constant, str]]:
    """[(argument index, node, marker)] for the string-literal first 2 arguments that are checked."""
    out = []
    name = _call_name(call)
    for k, arg in enumerate(call.args[:2]):
        if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
            continue
        literal = arg.value
        if literal.startswith(("\n", "\r")) or not literal.strip():
            continue
        marker = f"### {literal} " if name == "section" and k == 0 else literal
        out.append((k, arg, marker))
    return out


def _marker_findings(shown: str, source: str, script: pathlib.Path, report_name_: str,
                     report_text: str) -> list[dict]:
    """X002: markers of between(...) / section(...) calls that their source doesn't hold once; X003: calls
    whose source cannot be resolved."""
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return []
    paths = _ModulePaths(tree, script)
    default = _default_source(tree, paths)
    cache: dict = {}
    out = []
    for call in _marker_calls(tree):
        name = _call_name(call)
        named, src_name = _call_source(call, paths)
        if named:
            resolved = paths.resolve(src_name) if src_name is not None else _UNRESOLVED
            if resolved is _UNRESOLVED:
                what = src_name if src_name is not None else "an expression"
                out.append(_finding("X003", "info", shown, call.lineno,
                                    f"{name}(...) slices {what}, which does not resolve to a Markdown file; "
                                    "its markers are not checked", what))
                continue
        else:
            resolved = default
        if resolved is None:
            text, where = report_text, report_name_
        else:
            key = str(resolved)
            if key not in cache:
                try:
                    raw = pathlib.Path(resolved).read_bytes().decode("utf-8-sig", "replace")
                except OSError:
                    raw = None
                cache[key] = None if raw is None else raw.replace("\r\n", "\n").replace("\r", "\n")
            text, where = cache[key], _display(os.path.relpath(resolved) if _same_drive(resolved) else str(resolved))
            if text is None:
                out.append(_finding("X003", "info", shown, call.lineno,
                                    f"{name}(...) source {where} cannot be read; its markers are not checked",
                                    where))
                continue
        for _, _, marker in _marker_literals(call):
            n = text.count(marker)
            if n != 1:
                state = "is missing from" if n == 0 else f"occurs {n} times in"
                out.append(_finding("X002", "warning", shown, call.lineno,
                                    f"marker {marker!r} of {name}(...) {state} {where}; "
                                    f"slicing needs it exactly once", marker))
    return out


def _same_drive(path) -> bool:
    try:
        os.path.relpath(path)
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------- renumbering (§15.2, §16.5)
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


def _respelled(m: re.Match, new_key: tuple[str, str]) -> tuple[int, int, str]:
    """(start, end, text) replacing only the identifier of a reference match, keeping its spelling and the
    zero padding of its number (§16.5)."""
    for group in ("sec", "app", "fig", "tab"):
        if m.group(group) is not None:
            break
    old = m.group(group)
    new = new_key[1]
    if group in ("fig", "tab"):
        old_prefix = old[0] if old[0].isalpha() else ""
        digits = old[len(old_prefix):]
        new_prefix = new[0] if new[0].isalpha() else ""
        number = new[len(new_prefix):]
        if len(digits) > 1 and digits.startswith("0"):
            number = number.zfill(len(digits))
        new = new_prefix + number
    return m.start(group), m.end(group), new


@dataclass
class _Span:
    start: int
    end: int
    text: str
    old: str
    new: str


def _apply_spans(body: str, spans: list[_Span]) -> tuple[str, list[tuple[str, str]]]:
    spans = sorted(spans, key=lambda s: (s.start, s.end))
    out, last, edits = [], 0, []
    for s in spans:
        if s.start < last:                        # overlapping: the first one wins
            continue
        out += [body[last:s.start], s.text]
        last = s.end
        edits.append((s.old, s.new))
    out.append(body[last:])
    return "".join(out), edits


def _reference_spans(body: str, mapping: dict, own: str | None) -> list[_Span]:
    spans = []
    for m, key in find_references(body, own):
        if key in mapping:
            start, end, text = _respelled(m, mapping[key])
            written = m.group(0)
            new_written = written[:start - m.start()] + text + written[end - m.start():]
            spans.append(_Span(start, end, text, written, new_written))
    return spans


def _renumber_report(text: str, mapping: dict, own: str) -> tuple[str, list[tuple[int, str, str]], list]:
    """Renumber a report: references in prose, captions and headings; fenced code untouched.

    Returns (new text, [(line, old, new)], [(old heading line, new heading line, old id, new id)])."""
    raw_lines = _lines_keepends(text)
    bodies = [_split_ending(line)[0] for line in raw_lines]
    fenced = _fenced_lines(bodies)
    out, edits, headings = [], [], []
    for idx, line in enumerate(raw_lines):
        body, ending = _split_ending(line)
        if idx in fenced:
            out.append(line)
            continue
        spans = _reference_spans(body, mapping, own)
        heading = _report_heading(body)
        if heading and (heading[0], heading[1]) in mapping:
            new_key = mapping[(heading[0], heading[1])]
            start, end = heading[2]
            spans.append(_Span(start, end, new_key[1], ref_label(heading[:2]), ref_label(new_key)))
        new_body, line_edits = _apply_spans(body, spans)
        if heading and (heading[0], heading[1]) in mapping and new_body != body:
            headings.append((body.strip(), new_body.strip(), heading[1], mapping[(heading[0], heading[1])][1]))
        out.append(new_body + ending)
        edits += [(idx + 1, old, new) for old, new in line_edits]
    return "".join(out), edits, headings


def _marker_spans(source: str, headings: list) -> dict[int, list[_Span]]:
    """§16.5: slice markers that quote a renumbered heading, as spans per 1-based line."""
    if not headings:
        return {}
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return {}
    lines = _lines_keepends(source)
    out: dict[int, list[_Span]] = {}
    for call in _marker_calls(tree):
        name = _call_name(call)
        for k, arg in enumerate(call.args[:2]):
            if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)) or arg.lineno != arg.end_lineno:
                continue
            literal = arg.value
            core = literal.strip()
            if not core:
                continue
            new_core = None
            for old_line, new_line, old_id, new_id in headings:
                if name == "section" and k == 0:
                    if core == old_id:
                        new_core = new_id
                elif core in old_line and len(core) > len(old_id):
                    at = old_line.index(core)
                    number_at = old_line.find(old_id)
                    if at <= number_at and number_at + len(old_id) <= at + len(core):
                        new_core = core[:number_at - at] + new_id + core[number_at - at + len(old_id):]
                elif old_line in core:
                    new_core = core.replace(old_line, new_line)
                if new_core is not None:
                    break
            if new_core is None or new_core == core:
                continue
            raw = lines[arg.lineno - 1]
            encoded = raw.encode("utf-8")
            try:
                seg_start = len(encoded[:arg.col_offset].decode("utf-8"))
                seg_end = len(encoded[:arg.end_col_offset].decode("utf-8"))
            except UnicodeDecodeError:
                continue
            segment = raw[seg_start:seg_end]
            pos = segment.find(core)
            if pos < 0:
                continue
            start = seg_start + pos
            out.setdefault(arg.lineno, []).append(_Span(start, start + len(core), new_core, core, new_core))
    return out


def _renumber_file(text: str, mapping: dict, own: str, headings: list,
                   is_python: bool) -> tuple[str, list[tuple[int, str, str]]]:
    markers = _marker_spans(text, headings) if is_python else {}
    out, edits = [], []
    for lineno, line in enumerate(_lines_keepends(text), 1):
        body, ending = _split_ending(line)
        spans = _reference_spans(body, mapping, own) + markers.get(lineno, [])
        new_body, line_edits = _apply_spans(body, spans)
        out.append(new_body + ending)
        edits += [(lineno, old, new) for old, new in line_edits]
    return "".join(out), edits


# ====================================================================== apply edits (§15.5, §16.1, §16.3)
XML_ILLEGAL = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff￾￿]")
SURROGATE = re.compile("[\ud800-\udfff]")


def _check_edits(edits, where_prefix: str = "") -> list[dict]:
    if not isinstance(edits, list):
        raise ToolError(f"{where_prefix}edits: must be a list of {{find, replace, count}} objects")
    problems, out = [], []
    for i, e in enumerate(edits):
        where = f"{where_prefix}edits[{i}]"
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


def _check_characters(edits: list[dict], docx: bool, where_prefix: str = "") -> None:
    """§16.1: no XML-illegal characters in a .docx edit, no lone surrogates in any edit."""
    pattern = XML_ILLEGAL if docx else SURROGATE
    what = "a character that is not allowed in XML 1.0" if docx else "a lone surrogate"
    for i, e in enumerate(edits):
        for key in ("find", "replace"):
            m = pattern.search(e[key])
            if m:
                raise ToolError(f"invalid edits: {where_prefix}edits[{i}].{key} (edit index {i}) contains {what} "
                                f"(U+{ord(m.group(0)):04X}); nothing was written")


def _unified(old_lines: list[str], new_lines: list[str], path: str) -> str:
    shown = _display(path)
    return "\n".join(difflib.unified_diff(old_lines, new_lines, f"a/{shown}", f"b/{shown}", lineterm=""))


def _occurrence_offsets(text: str, find: str) -> list[int]:
    """Start offsets of the non-overlapping occurrences (as str.count counts them)."""
    out, pos = [], text.find(find)
    while pos >= 0:
        out.append(pos)
        pos = text.find(find, pos + len(find))
    return out


PY_SPLIT = re.compile(r"""(["'])((?:[ \t]*\\?[ \t]*(?:#[^\n]*)?\r?\n)*[ \t]*)\1""")


def _string_split_hint(text: str, find: str) -> str | None:
    """§16.3: 'spans a string-literal split at line N' when find matches once Python literal splits
    ("a "\\n "b", 'a ' 'b') are removed."""
    pieces, removed, last = [], [], 0          # removed: (offset in joined text, offset in text)
    joined_len = 0
    for m in PY_SPLIT.finditer(text):
        if not m.group(2):                        # an empty literal, not a split
            continue
        pieces.append(text[last:m.start()])
        joined_len += m.start() - last
        removed.append((joined_len, m.start()))
        last = m.end()
    if not removed:
        return None
    pieces.append(text[last:])
    joined = "".join(pieces)
    for start in _occurrence_offsets(joined, find):
        end = start + len(find)
        for at, original in removed:
            if start < at < end:
                return f"spans a string-literal split at line {text.count(chr(10), 0, original) + 1}"
    return None


class _TextTarget:
    """A text file under edit: line endings and BOM kept."""

    def __init__(self, path: str, shown: str):
        self.path, self.shown = path, shown
        text, self.bom = _read_raw(path, "path")
        self.crlf = "\r\n" in text and re.search(r"(?<!\r)\n", text) is None
        self.work = text.replace("\r\n", "\n") if self.crlf else text
        self.current = self.work

    def apply(self, e: dict) -> dict | None:
        offsets = _occurrence_offsets(self.current, e["find"])
        if len(offsets) != e["count"]:
            failure = {"find": e["find"], "found": len(offsets),
                       "lines": [self._line(self.current, k) for k in offsets]}
            if not offsets and pathlib.Path(self.path).suffix.lower() == ".py":
                hint = _string_split_hint(self.current, e["find"])
                if hint:
                    failure["hint"] = hint
            return failure
        self.current = self.current.replace(e["find"], e["replace"])
        return None

    @staticmethod
    def _line(text: str, offset: int) -> int:
        """1-based line number; a lone \\r also ends a line."""
        head = text[:offset]
        return head.count("\n") + len(re.findall(r"\r(?!\n)", head)) + 1

    def diff(self) -> str:
        old_lines = [_split_ending(x)[0] for x in _lines_keepends(self.work)]
        new_lines = [_split_ending(x)[0] for x in _lines_keepends(self.current)]
        return _unified(old_lines, new_lines, self.shown)

    def changed(self) -> bool:
        return self.current != self.work

    def data(self) -> bytes:
        text = self.current.replace("\n", "\r\n") if self.crlf else self.current
        return (codecs.BOM_UTF8 if self.bom else b"") + text.encode("utf-8")

    def save(self) -> None:
        replace_file(self.path, self.data())


class _DocxTarget:
    """A .docx under edit: only the main document part changes."""

    def __init__(self, path: str, shown: str):
        self.path, self.shown = native_path(path), shown
        self.doc = DocxText(path)
        self.before = self.doc.texts(breaks=True)

    def apply(self, e: dict) -> dict | None:
        paragraphs = self.doc.paragraphs
        found, lines, visible = 0, [], -1
        for p in paragraphs:
            text = "".join(s.text for s in p)
            if text.strip():
                visible += 1
            n = len(_occurrence_offsets(text, e["find"]))
            found += n
            lines += [visible] * n
        if found != e["count"]:
            return {"find": e["find"], "found": found, "lines": lines}
        for p in paragraphs:
            _replace_in_runs(p, e["find"], e["replace"])
        return None

    def diff(self) -> str:
        return _unified(self.before, self.doc.texts(breaks=True), self.shown)

    def changed(self) -> bool:
        return self.doc.texts(breaks=True) != self.before

    def data(self) -> bytes:
        return self.doc.package_bytes()

    def save(self) -> None:
        self.doc.save()


def _open_target(path: str, shown: str):
    if pathlib.Path(path).suffix.lower() == ".docx":
        if not pathlib.Path(native_path(path)).is_file():
            raise ToolError(f"path: no such file: {shown}")
        return _DocxTarget(native_path(path), shown)
    return _TextTarget(path, shown)


# ====================================================================== docx (§15.4, §15.5, §16.1, §16.3)
W_NAMESPACES = ("http://schemas.openxmlformats.org/wordprocessingml/2006/main",
                "http://purl.oclc.org/ooxml/wordprocessingml/main")
MC_NAMESPACE = "http://schemas.openxmlformats.org/markup-compatibility/2006"
_XML_ENTITY = re.compile(r"&(?:#(\d+)|#x([0-9a-fA-F]+)|(amp|lt|gt|quot|apos));")
_XML_NAMED = {"amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'"}
_ZIP_ERRORS = (zipfile.BadZipFile, zlib.error, EOFError, OSError, NotImplementedError, ValueError,
               RuntimeError, KeyError, struct.error)


def _xml_unescape(text: str) -> str:
    def one(m: re.Match) -> str:
        try:
            if m.group(1):
                return chr(int(m.group(1)))
            if m.group(2):
                return chr(int(m.group(2), 16))
        except (ValueError, OverflowError):
            return m.group(0)
        return _XML_NAMED[m.group(3)]
    return _XML_ENTITY.sub(one, text)


def _xml_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


@dataclass
class _Segment:
    """1 piece of paragraph text: a <w:t> element's content (editable), or a <w:tab/> or <w:br/> (\\t, \\n)."""
    tag_start: int
    content_start: int
    content_end: int
    text: str
    editable: bool
    original: str = ""
    prefix: str = "w"


def _run_content(prefix: str, text: str) -> str:
    """Text as run content: <w:t> pieces with <w:tab/> and <w:br/> for tabs and line breaks."""
    out = []
    for piece in re.split(r"(\t|\r\n|\n|\r)", text):
        if piece == "\t":
            out.append(f"<{prefix}:tab/>")
        elif piece in ("\n", "\r", "\r\n"):
            out.append(f"<{prefix}:br/>")
        elif piece:
            out.append(f'<{prefix}:t xml:space="preserve">{_xml_escape(piece)}</{prefix}:t>')
    return "".join(out)


def _read_member(z: zipfile.ZipFile, name: str, path: str, arg: str) -> bytes:
    try:
        return z.read(name)
    except _ZIP_ERRORS as e:
        raise ToolError(f"{arg}: corrupt .docx package: {path} (part {name}: {e})") from None


class DocxText:
    """The paragraphs of a .docx main document, editable in place without touching any other XML.

    Only the package relationships and the main document are decompressed (§16.1); every other part is copied
    as a raw zip entry when the file is saved.
    """

    def __init__(self, path: str, arg: str = "path"):
        self.path = native_path(path)
        self.shown = path
        try:
            with zipfile.ZipFile(self.path) as z:
                self.infos = z.infolist()
                self.comment = z.comment
                names = {i.filename for i in self.infos}
                rels = _read_member(z, "_rels/.rels", path, arg) if "_rels/.rels" in names else b""
                self.part = self._main_part(rels, names)
                raw = _read_member(z, self.part, path, arg)
        except FileNotFoundError:
            raise ToolError(f"{arg}: no such file: {path}") from None
        except ToolError:
            raise
        except _ZIP_ERRORS as e:
            raise ToolError(f"{arg}: not a readable .docx package: {path} ({e})") from None
        self.bom = raw.startswith(codecs.BOM_UTF8)
        try:
            self.xml = raw[len(codecs.BOM_UTF8) if self.bom else 0:].decode("utf-8")
        except UnicodeDecodeError:
            raise ToolError(f"{arg}: {self.part} in {path} is not UTF-8") from None
        self.paragraphs = self._scan()

    def _main_part(self, rels_bytes: bytes, names: set) -> str:
        rels = rels_bytes.decode("utf-8", "replace")
        for m in re.finditer(r'<Relationship\b[^>]*>', rels):
            if not re.search(r'Type="[^"]*/officeDocument"', m.group(0)):
                continue
            target = re.search(r'Target="([^"]+)"', m.group(0))
            if target and target.group(1).lstrip("/") in names:
                return target.group(1).lstrip("/")
        if "word/document.xml" in names:
            return "word/document.xml"
        raise ToolError(f"not a .docx package (no main document): {self.shown}")

    def _scan(self) -> list[list[_Segment]]:
        prefixes = re.findall(r'xmlns:([A-Za-z_][\w.-]*)="(?:%s)"' % "|".join(map(re.escape, W_NAMESPACES)),
                              self.xml) or ["w"]
        mc = re.findall(r'xmlns:([A-Za-z_][\w.-]*)="%s"' % re.escape(MC_NAMESPACE), self.xml) or ["mc"]
        w = "(?:%s)" % "|".join(map(re.escape, prefixes))
        m_ = "(?:%s)" % "|".join(map(re.escape, mc))
        token = re.compile(
            rf"(?P<fe><{m_}:Fallback(?=[\s/])[^>]*/>)"
            rf"|(?P<fo><{m_}:Fallback(?=[\s>])[^>]*>)"
            rf"|(?P<fc></{m_}:Fallback\s*>)"
            rf"|(?P<pe><(?P<pp>{w}):p(?=[\s/])[^>]*/>)"
            rf"|(?P<po><{w}:p(?=[\s>])[^>]*>)"
            rf"|(?P<pc></{w}:p\s*>)"
            rf"|(?P<t><(?P<tp>{w}):t(?=[\s>])[^>]*(?<!/)>)(?P<tc>.*?)</{w}:t\s*>"
            rf"|(?P<tab><(?P<xp>{w}):tab(?=[\s/])[^>]*/>)"
            rf"|(?P<br><(?P<bp>{w}):(?:br|cr)(?=[\s/])[^>]*/>)", re.S)
        paragraphs: list[list[_Segment]] = []
        stack: list[int] = []
        fallback = 0
        for m in token.finditer(self.xml):
            if m.group("fo"):
                fallback += 1
            elif m.group("fc"):
                fallback = max(0, fallback - 1)
            elif m.group("fe") or fallback:
                continue
            elif m.group("pe"):
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
                    paragraphs[stack[-1]].append(_Segment(m.start(), m.start("tc"), m.end("tc"), text, True, text,
                                                          m.group("tp")))
                else:
                    ch = "\t" if m.group("tab") else "\n"
                    prefix = m.group("xp") or m.group("bp") or "w"
                    paragraphs[stack[-1]].append(_Segment(m.start(), m.start(), m.end(), ch, False, ch, prefix))
        return paragraphs

    def texts(self, breaks: bool = False) -> list[str]:
        """Paragraph texts; with breaks, tabs and line breaks are included."""
        return ["".join(s.text for s in p if s.editable or breaks) for p in self.paragraphs]

    def editable(self) -> list[list[_Segment]]:
        return [[s for s in p if s.editable] for p in self.paragraphs]

    def xml_bytes(self) -> bytes:
        changed = sorted((s for p in self.paragraphs for s in p if s.text != s.original),
                         key=lambda s: s.tag_start)
        out, last = [], 0
        for s in changed:
            if s.editable:
                tag = self.xml[s.tag_start:s.content_start]
                special = re.search(r"[\t\r\n]", s.text) is not None
                if (s.text != s.text.strip() or special) and "xml:space" not in tag:
                    tag = tag[:-1] + ' xml:space="preserve">'
                body = _xml_escape(s.text)
                if special:
                    close, reopen = f"</{s.prefix}:t>", tag
                    body = re.sub(r"\r\n|\n|\r", lambda _: f"{close}<{s.prefix}:br/>{reopen}",
                                  body.replace("\t", f"{close}<{s.prefix}:tab/>{reopen}"))
                out += [self.xml[last:s.tag_start], tag, body]
                last = s.content_end
            else:                                   # a tab or break removed or overwritten
                out += [self.xml[last:s.tag_start], _run_content(s.prefix, s.text)]
                last = s.content_end
        out.append(self.xml[last:])
        return (codecs.BOM_UTF8 if self.bom else b"") + "".join(out).encode("utf-8")

    def package_bytes(self) -> bytes:
        """The package with the new main document; other entries are copied raw (not decompressed)."""
        data = self.xml_bytes()
        buffer = io.BytesIO()
        try:
            with open(self.path, "rb") as src, zipfile.ZipFile(buffer, "w") as out:
                for info in self.infos:
                    if info.filename == self.part:
                        new = zipfile.ZipInfo(info.filename, date_time=info.date_time)
                        new.compress_type = zipfile.ZIP_DEFLATED
                        new.external_attr = info.external_attr
                        new.create_system = info.create_system
                        new.comment = info.comment
                        out.writestr(new, data)
                    else:
                        _copy_raw_entry(src, out, info)
                out.comment = self.comment
        except _ZIP_ERRORS as e:
            raise ToolError(f"cannot rewrite {self.shown}: corrupt .docx package ({e})") from None
        return buffer.getvalue()

    def save(self) -> None:
        replace_file(self.path, self.package_bytes())


def _copy_raw_entry(src, out: zipfile.ZipFile, info: zipfile.ZipInfo) -> None:
    """Copy 1 zip entry (local header, compressed data, data descriptor) byte for byte."""
    src.seek(info.header_offset)
    header = src.read(30)
    if len(header) != 30 or header[:4] != b"PK\x03\x04":
        raise zipfile.BadZipFile(f"bad local header for {info.filename}")
    name_len, extra_len = struct.unpack("<HH", header[26:30])
    rest = src.read(name_len + extra_len + info.compress_size)
    if len(rest) != name_len + extra_len + info.compress_size:
        raise zipfile.BadZipFile(f"truncated entry {info.filename}")
    record = header + rest
    if info.flag_bits & 0x08:
        tail = src.read(4)
        if tail == b"PK\x07\x08":
            tail += src.read(12)
        else:
            tail += src.read(8)
        record += tail
    new = copy.copy(info)
    out.fp.seek(out.start_dir)
    new.header_offset = out.fp.tell()
    out.fp.write(record)
    out.start_dir = out.fp.tell()
    out.filelist.append(new)
    out.NameToInfo[new.filename] = new
    out._didModify = True


def _replace_in_runs(segments: list[_Segment], find: str, replace: str) -> None:
    """Replace every occurrence of find in 1 paragraph (tabs and breaks count as \\t and \\n).

    Only the part that differs between find and replace is rewritten. It goes into the first text run it
    touches; the rest of it is removed from the pieces after that run.
    """
    prefix = len(os.path.commonprefix([find, replace]))
    suffix = len(os.path.commonprefix([find[prefix:][::-1], replace[prefix:][::-1]]))
    insert = replace[prefix:len(replace) - suffix]
    pos = 0
    while True:
        text = "".join(s.text for s in segments)
        start = text.find(find, pos)
        if start < 0:
            return
        rs, re_ = start + prefix, start + len(find) - suffix
        spans, offset = [], 0
        for s in segments:
            spans.append((offset, offset + len(s.text)))
            offset += len(s.text)
        touched = [k for k, (a, b) in enumerate(spans) if a < re_ and b > rs]
        if not touched:                               # a pure insertion
            touched = [k for k, (a, b) in enumerate(spans) if a <= rs <= b and segments[k].editable][:1] \
                or [k for k, (a, b) in enumerate(spans) if a <= rs <= b][:1]
        host = next((k for k in touched if segments[k].editable), touched[0] if touched else None)
        if host is None:
            return
        for k in touched:
            s, (a, _) = segments[k], spans[k]
            left = s.text[:max(0, rs - a)]
            right = s.text[max(0, re_ - a):] if re_ - a < len(s.text) else ""
            if k == host:
                s.text = left + insert + right
            else:
                s.text = left + right
        pos = start + len(replace)


# ====================================================================== Markdown to paragraphs (§15.4)
_MD_ESCAPE = re.compile(r"\\([\\`*_{}\[\]()#+\-.!|<>~])")
_PROTECT_CHARS = "\\`*_{}[]()#+-.!|<>~"
_CODE_SPAN = re.compile(r"(`+)(.+?)\1")
_MD_COMMENT = re.compile(r"<!--.*?-->", re.S)
_BRACKETED = r"((?:[^\[\]]|\[(?:[^\[\]]|\[[^\[\]]*\])*\])*)"     # text with up to 2 levels of [...]
_MD_IMAGE = re.compile(r"!\[" + _BRACKETED + r"\]\((?:[^()\n]|\([^()\n]*\))*\)")
_MD_LINK = re.compile(r"\[" + _BRACKETED + r"\]\((?:[^()\n]|\([^()\n]*\))*\)")
_MD_DROP_LINE = re.compile(r"^\s*(?:\\(?:pagebreak|newpage|clearpage)(?:\{\})?|\{\{.*\}\})\s*$")
_LIST_NUMBER = re.compile(r"^\s*(\d{1,9}[.)])\s+")
_ORDERED_ITEM = re.compile(r"^[ \t]*(\d{1,9}[.)])(?:[ \t]+|$)")
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
    """Reduce Markdown to paragraphs (§15.4, §16.3): blocks joined into 1 line, headings, list items and table
    cells as their own paragraphs, a fenced code block as 1 paragraph (lines joined with \\n), inline markup
    stripped, page-break and {{placeholder}} lines dropped, empties dropped. List numbers are removed."""
    return [t for t, _ in markdown_blocks(text)]


def markdown_blocks(text: str) -> list[tuple[str, str | None]]:
    """[(paragraph, list number such as "1." or None)] as markdown_paragraphs, keeping each ordered list
    item's number apart."""
    text = _MD_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text.replace("\r\n", "\n").replace("\r", "\n"))
    lines = _split_lines(text)
    start = 0
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() in ("---", "..."):
                start = j + 1
                break
    tables = _table_lines(lines)
    out: list[tuple[str, str | None]] = []
    block: list[str] = []
    code: list[str] = []
    in_item = False
    number = None
    fence = None

    def flush():
        nonlocal in_item, number
        if block:
            out.append((markdown_inline(" ".join(block)), number))
            block.clear()
        in_item = False
        number = None

    def flush_code():
        while code and not code[-1].strip():
            code.pop()
        while code and not code[0].strip():
            code.pop(0)
        if code:
            out.append(("\n".join(code), None))
        code.clear()

    for i in range(start, len(lines)):
        line = lines[i]
        if fence is not None:
            if fence.match(line):
                fence = None
                flush_code()
            else:
                code.append(line.rstrip())
            continue
        m = FENCE_OPEN.match(line)
        if m:
            flush()
            fence = _fence_close(m.group(1))
            continue
        if not line.strip() or _MD_DROP_LINE.match(line):
            flush()
            continue
        if i in tables:
            flush()
            if not _is_table_separator(line):
                out += [(markdown_inline(c), None) for c in _table_cells(line)]
            continue
        heading = HEADING.match(line.strip()) if line.startswith(("#", " #", "  #", "   #")) else None
        if heading:
            flush()
            out.append((markdown_inline((heading.group(2) or "").rstrip("#")), None))
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
            ordered = _ORDERED_ITEM.match(body)
            number = ordered.group(1) if ordered else None
        elif in_item and not line[:1].isspace():
            flush()
            block.append(body.strip())
        else:
            block.append(body.strip())
    flush()
    if fence is not None:
        flush_code()
    return [(t, n) for t, n in out if t.strip()]


def normalise_paragraph(text: str) -> str:
    """Whitespace collapsed, curly quotes and apostrophes folded to straight ones."""
    return " ".join(text.translate(_QUOTES).split())


def _is_docx(path: str) -> bool:
    return pathlib.Path(path).suffix.lower() == ".docx"


def _raw_document(path: str, arg: str):
    """A .docx's non-empty paragraphs (list of str), or a Markdown file's blocks (list of (str, number))."""
    if _is_docx(path):
        if not pathlib.Path(native_path(path)).is_file():
            raise ToolError(f"{arg}: no such file: {path}")
        return [t for t in DocxText(path, arg).texts(breaks=True) if t.strip()]
    text, _ = _read_raw(path, arg)
    return markdown_blocks(text)


def _numbered_rest(text: str) -> tuple[str, str] | None:
    m = _LIST_NUMBER.match(text)
    return (m.group(1), text[m.end():]) if m else None


def _reconcile(blocks: list, docx: list[str] | None) -> tuple[list[str], list[str] | None]:
    """§16.3: a Markdown list number is kept when the .docx has a paragraph that starts with it (and the same
    text), otherwise removed; a .docx paragraph loses its leading number when it matches such an item."""
    if docx is None:
        return [t for t, _ in blocks], None
    docx_norm = {normalise_paragraph(t) for t in docx}
    md_out, stripped = [], set()
    for text, number in blocks:
        if number is not None and normalise_paragraph(f"{number} {text}") in docx_norm:
            md_out.append(f"{number} {text}")
        else:
            md_out.append(text)
            if number is not None:
                stripped.add(normalise_paragraph(text))
    kept = {normalise_paragraph(t) for t in md_out}
    docx_out = []
    for text in docx:
        split = _numbered_rest(text)
        if split and normalise_paragraph(text) not in kept and normalise_paragraph(split[1]) in stripped:
            docx_out.append(split[1])
        else:
            docx_out.append(text)
    return md_out, docx_out


def compared_paragraphs(old: str, new: str) -> tuple[list[str], list[str]]:
    """The 2 paragraph lists docx_diff aligns (§15.4, §16.3)."""
    a, b = _raw_document(old, "old"), _raw_document(new, "new")
    if _is_docx(old) and not _is_docx(new):
        b, a2 = _reconcile(b, a)
        return a2, b
    if _is_docx(new) and not _is_docx(old):
        return _reconcile(a, b)
    return ([t for t, _ in a] if not _is_docx(old) else a), ([t for t, _ in b] if not _is_docx(new) else b)


def document_paragraphs(path: str, arg: str) -> list[str]:
    """Non-empty paragraphs of a .docx (from its main document) or a Markdown file."""
    doc = _raw_document(path, arg)
    return doc if _is_docx(path) else [t for t, _ in doc]


# ====================================================================== hints (§15.4)
HINT_SUFFIXES = (".py", ".json", ".md")


class HintIndex:
    """Find where a string occurs in the files under `search` (directories walked for .py, .json and .md)."""

    def __init__(self, search: list[str] | None):
        self.files = walk_inputs(search or [], HINT_SUFFIXES, "search")
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
def _split_pair(entry: str, arg: str) -> tuple[str, str | None]:
    """FILE or FILE=REPORT (§16.5). An entry naming an existing path is a plain FILE even with '='."""
    if not isinstance(entry, str) or not entry:
        raise ToolError(f"{arg}: must be a list of non-empty strings")
    if "=" not in entry or os.path.exists(native_path(entry)):
        return entry, None
    for k in [k for k, ch in enumerate(entry) if ch == "="]:
        left, right = entry[:k], entry[k + 1:]
        if left and right and os.path.isfile(native_path(right)):
            return left, right
    left, right = entry.split("=", 1)
    if left and right:
        raise ToolError(f"{arg}: {entry!r}: the report {right!r} after '=' does not exist")
    raise ToolError(f"{arg}: expected FILE or FILE=REPORT, got {entry!r}")


@dataclass
class _XrefReport:
    given: str
    shown: str
    text: str
    bom: bool
    lf: str
    targets: set
    own: str


@tool("text_xref",
      "Resolve cross-references against a report and renumber them. Targets: numbered headings (§N.M), "
      "'## Appendix X.'/'### X.n' headings (App. X.n), Fig./Table captions; fenced code holds none. Every "
      "§N, App. X, Fig. Pn, Table Pn in `files` (directories walked, `exclude` globs) must hit a target (X001); "
      "mentions after 'arXiv'/'paper', in numbered citation brackets [5, App. H], or after another report's "
      "name ('general report §3') are skipped. FILE=REPORT pairs a file with its own report (report then "
      "optional). X002: a between()/section() marker in a .py file that its source (src=NAME bound to an .md "
      "path, the module default, else the report) does not hold once; X003 (info): unresolvable source. "
      "`renumber` (['Fig. 9=Fig. 10', 'Fig. 10=Fig. 9']) applies at once to files, report headings, captions, "
      "prose and markers quoting renumbered headings, keeping spelling and zero padding. Without write it "
      "only lists edits. Returns {ok, findings, counts, edits: [{path, line, old, new}]}.",
      {"type": "object",
       "properties": {
           "report": {"type": "string", "description": "The Markdown report that defines the targets."},
           "files": {"type": "array", "items": {"type": "string"},
                     "description": "Files or directories to check; FILE=REPORT pairs one with its report."},
           "exclude": {"type": "array", "items": {"type": "string"},
                       "description": "Glob patterns of walked files to leave out."},
           "renumber": {"type": "array", "items": {"type": "string"}, "description": "OLD=NEW references."},
           "write": {"type": "boolean", "description": "Rewrite the files (default false: dry run)."},
       },
       "additionalProperties": False},
      readOnlyHint=False, destructiveHint=False)
def text_xref(report: str | None = None, files: list[str] | None = None, renumber: list[str] | None = None,
              write: bool = False, exclude: list[str] | None = None) -> dict:
    mapping = _parse_renumber(_str_list(renumber, "renumber"))
    excludes = _str_list(exclude, "exclude")
    if not isinstance(write, bool):
        raise ToolError("write: must be true or false")
    reports: dict[str, _XrefReport] = {}
    order: list[str] = []

    def load_report(given: str, arg: str) -> str:
        key = path_key(given)
        if key not in reports:
            text, bom = _read_raw(given, arg)
            lf = text.replace("\r\n", "\n").replace("\r", "\n")
            reports[key] = _XrefReport(given, _display(given), text, bom, lf, report_targets(lf),
                                       report_name(lf, given))
            order.append(key)
        return key

    default_key = load_report(report, "report") if report is not None else None
    pairs = [_split_pair(e, "files") for e in _str_list(files, "files")]
    if default_key is None:
        if not pairs:
            raise ToolError("report: required unless every files entry is FILE=REPORT")
        loose = [f for f, r in pairs if r is None]
        if loose:
            raise ToolError(f"files: {loose[0]!r} has no report: give report or write FILE=REPORT")

    checked, seen = [], set()
    for entry, bound in pairs:
        rkey = load_report(bound, "files") if bound is not None else default_key
        for shown, p in walk_inputs([entry], XREF_SUFFIXES, "files", excludes):
            key = (path_key(p), rkey)
            if key in seen:
                continue
            seen.add(key)
            text, bom = _read_raw(str(p), "files")
            checked.append((shown, p, text, bom, rkey))

    findings = []
    for shown, p, text, _, rkey in checked:
        rep = reports[rkey]
        for lineno, line in enumerate(_lines_keepends(text), 1):
            body, _ = _split_ending(line)
            for m, key in find_references(body, rep.own):
                if key not in rep.targets:
                    findings.append(_finding("X001", "error", shown, lineno,
                                             f"{ref_label(key)} has no target in {rep.shown}",
                                             _excerpt(body, m.start(), m.end())))
        if p.suffix.lower() == ".py":
            findings += _marker_findings(shown, text, pathlib.Path(os.path.abspath(p)), rep.shown, rep.lf)

    edits, writes = [], []
    if mapping:
        headings = {}
        for rkey in order:
            rep = reports[rkey]
            new_text, line_edits, changed = _renumber_report(rep.text, mapping, rep.own)
            headings[rkey] = changed
            edits += [{"path": rep.shown, "line": n, "old": old, "new": new} for n, old, new in line_edits]
            if new_text != rep.text:
                writes.append((rep.given, new_text, rep.bom))
        done = set()
        for shown, p, text, bom, rkey in checked:
            fkey = path_key(p)
            if fkey in reports or fkey in done:
                continue
            done.add(fkey)
            new_text, line_edits = _renumber_file(text, mapping, reports[rkey].own, headings.get(rkey, []),
                                                  p.suffix.lower() == ".py")
            edits += [{"path": shown, "line": n, "old": old, "new": new} for n, old, new in line_edits]
            if new_text != text:
                writes.append((str(p), new_text, bom))
    if write:
        for path, text, bom in writes:
            _write_text(path, text, bom)
    return _checker_result(findings, edits=edits)


@tool("text_apply_edits",
      "Anchored find and replace in text files or .docx files. edits: [{find, replace, count (default 1)}] for "
      "`path`, or the docx_diff emit_edits form [{path, edits: [...]}] (path then optional), applied "
      "all-or-nothing across files. Each find must occur exactly count times in the current text; edits apply "
      "in order. If any edit fails nothing is written and every failure is listed with the lines (docx: "
      "paragraph indices) of each occurrence; in .py files a find that only matches across a string-literal "
      "split gets a hint. In a .docx, find must lie within 1 paragraph (tabs are \\t, line breaks \\n; it may "
      "span runs) and every other package part is copied unchanged. XML-illegal characters are refused. Line "
      "endings are preserved; writes are atomic. Without write it is a dry run. Returns {ok, applied, "
      "failures: [{index, find, found, lines, hint?, path?}], diff}.",
      {"type": "object",
       "properties": {
           "edits": {"type": "array", "items": {"type": "object"},
                     "description": "[{find, replace, count}] for path, or [{path, edits}] per file."},
           "path": {"type": "string", "description": "The text file or .docx to edit (flat edits form)."},
           "write": {"type": "boolean", "description": "Write the result (default false: dry run)."},
       },
       "required": ["edits"],
       "additionalProperties": False},
      readOnlyHint=False, destructiveHint=False)
def text_apply_edits(edits: list, path: str | None = None, write: bool = False) -> dict:
    if not isinstance(edits, list):
        raise ToolError("edits: must be a list of {find, replace, count} objects, or of {path, edits} objects")
    if not isinstance(write, bool):
        raise ToolError("write: must be true or false")
    per_file = bool(edits) and all(isinstance(e, dict) and "edits" in e for e in edits)
    if not per_file:
        if path is None:
            raise ToolError("path: required unless edits is a list of {path, edits} objects")
        groups = [(path, edits, "")]
    else:
        groups = []
        for k, obj in enumerate(edits):
            extra = [key for key in obj if key not in ("path", "edits")]
            if extra:
                raise ToolError(f"invalid edits: edits[{k}]: unknown key {extra[0]!r}")
            target = obj.get("path", path)
            if not isinstance(target, str) or not target:
                raise ToolError(f"invalid edits: edits[{k}].path: must be a non-empty string")
            groups.append((target, obj["edits"], f"{target}: "))

    checked = []
    for target, file_edits, where in groups:
        items = _check_edits(file_edits, where)
        _check_characters(items, pathlib.Path(target).suffix.lower() == ".docx", where)
        checked.append((target, items))

    targets: dict[str, object] = {}
    applied, failures, order = 0, [], []
    for entry, (target, items) in enumerate(checked):
        key = path_key(target)
        if key not in targets:
            targets[key] = _open_target(target, _display(target))
            order.append(key)
        state = targets[key]
        for i, e in enumerate(items):
            failure = state.apply(e)
            if failure is None:
                applied += 1
                continue
            failure = {"index": i, **failure}
            if per_file:
                failure["path"] = _display(target)
                failure["entry"] = entry
            failures.append(failure)
    if write and not failures:
        pending = [targets[k] for k in order if targets[k].changed()]
        payloads = [(t, t.data()) for t in pending]
        for t, data in payloads:
            replace_file(t.path, data)
    diff = "\n".join(d for d in (targets[k].diff() for k in order) if d)
    return {"ok": not failures, "applied": applied, "failures": failures, "diff": diff}


@tool("docx_diff",
      "Compare 2 documents paragraph by paragraph to carry hand edits back into build scripts: 2 .docx files, "
      "or a .docx and a Markdown file (either order). Markdown is reduced to paragraphs (blocks joined, "
      "headings, emphasis, code, link and image markup stripped, list items and table cells separate, a fenced "
      "code block is 1 paragraph, \\pagebreak and {{placeholder}} lines dropped; list numbers kept only when "
      "the .docx has them). Paragraphs are compared after collapsing whitespace and folding curly quotes. "
      "Returns {changes: [{op: replace|insert|delete, old: [str], new: [str], old_index, new_index, hint}]} "
      "with 0-based indexes and raw paragraph text; hint lists up to 3 'path:line' places under `search` (.py, "
      ".json, .md) where the first old paragraph occurs. emit_edits writes a text_apply_edits file "
      "[{path, edits}] for replace changes with exactly 1 hint (result edits_written).",
      {"type": "object",
       "properties": {
           "old": {"type": "string", "description": "The earlier .docx or .md file."},
           "new": {"type": "string", "description": "The edited .docx or .md file."},
           "search": {"type": "array", "items": {"type": "string"},
                      "description": "Files or directories to search for hints."},
           "emit_edits": {"type": "string",
                          "description": "Write a JSON edits file for text_apply_edits to this path."},
       },
       "required": ["old", "new"],
       "additionalProperties": False},
      readOnlyHint=True)
def docx_diff(old: str, new: str, search: list[str] | None = None, emit_edits: str | None = None) -> dict:
    if emit_edits is not None and (not isinstance(emit_edits, str) or not emit_edits):
        raise ToolError("emit_edits: must be a file path")
    a, b = compared_paragraphs(old, new)
    index = HintIndex(_str_list(search, "search"))
    matcher = difflib.SequenceMatcher(None, [normalise_paragraph(p) for p in a],
                                      [normalise_paragraph(p) for p in b], autojunk=False)
    changes = []
    emitted: dict[str, dict] = {}
    count = 0
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            continue
        hint = index.hints(a[i1]) if i2 > i1 else []
        changes.append({"op": op, "old": a[i1:i2], "new": b[j1:j2], "old_index": i1, "new_index": j1,
                        "hint": hint})
        if emit_edits is None or op != "replace" or i2 - i1 != j2 - j1:
            continue
        for k in range(i2 - i1):
            hits = hint if k == 0 else index.hints(a[i1 + k])
            if len(hits) != 1 or a[i1 + k] == b[j1 + k]:
                continue
            target = hits[0].rsplit(":", 1)[0]
            entry = emitted.setdefault(path_key(target), {"path": target, "edits": []})
            entry["edits"].append({"find": a[i1 + k], "replace": b[j1 + k], "count": 1})
            count += 1
    result = {"changes": changes}
    if emit_edits is not None:
        payload = json.dumps(list(emitted.values()), indent=2, ensure_ascii=False) + "\n"
        out = pathlib.Path(native_path(emit_edits))
        if out.is_dir():
            raise ToolError(f"emit_edits: {emit_edits} is a directory")
        if not out.parent.is_dir():
            raise ToolError(f"emit_edits: no such directory: {out.parent}")
        replace_file(str(out), payload.encode("utf-8"))
        result["edits_written"] = count
    return result


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
    c.add_argument("report", metavar="REPORT", nargs="?", help="the report (optional with --in FILE=REPORT)")
    c.add_argument("--in", dest="files", nargs="+", action="extend", default=[], metavar="FILE",
                   help="files whose references must resolve (deck scripts, specs, presenter packs); "
                        "FILE=REPORT pairs a file or directory with its own report")
    c.add_argument("--exclude", nargs="+", action="extend", default=[], metavar="GLOB",
                   help="leave out walked files matching these globs")
    c.add_argument("--renumber", nargs="+", action="extend", default=[], metavar="OLD=NEW",
                   help="renumber references, e.g. 'Fig. 9=Fig. 10' (all applied at once)")
    c.add_argument("--write", action="store_true", help="rewrite the files (default: list the edits)")
    common_flags(c, checker=True)
    c.set_defaults(handler=_cli_xref)

    c = cmds.add_parser("apply-edits", help="anchored find and replace in a text file or .docx")
    c.add_argument("edits_path", metavar="EDITS.json",
                   help="a JSON list of {find, replace, count}, or of {path, edits} (docx-diff --emit-edits)")
    c.add_argument("path", metavar="FILE", nargs="?", help="the file to edit (not needed for the {path, edits} form)")
    c.add_argument("--write", action="store_true", help="write the result (default: dry run)")
    common_flags(c)
    c.set_defaults(handler=_cli_apply_edits)

    c = cmds.add_parser("docx-diff", help="paragraph changes between 2 .docx files, or a .docx and a .md")
    c.add_argument("old", metavar="OLD")
    c.add_argument("new", metavar="NEW")
    c.add_argument("--search", nargs="+", action="extend", default=[], metavar="PATH",
                   help="files or directories to search for where the old text comes from")
    c.add_argument("--emit-edits", metavar="PATH", help="write a text apply-edits JSON file for unique hints")
    common_flags(c)
    c.set_defaults(handler=_cli_docx_diff)


def _cli_xref(args):
    from tundlekit.cli_support import CliResult, format_findings

    res = text_xref(args.report, files=args.files, renumber=args.renumber, write=args.write,
                    exclude=args.exclude or None)
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
        edits = [edits] if "path" in edits else edits["edits"]
    res = text_apply_edits(edits, args.path, write=args.write)
    lines = [res["diff"]] if res["diff"] else []
    lines += [(f"{f['path']}: " if "path" in f else "") + f"edit {f['index']}: {f['find']!r} found {f['found']} "
              f"time(s)" + (f" at {', '.join(map(str, f['lines']))}" if f["lines"] else "")
              + (f" ({f['hint']})" if f.get("hint") else "") for f in res["failures"]]
    state = "written" if args.write and res["ok"] else "dry run" if res["ok"] else "nothing written"
    lines.append(f"{'ok' if res['ok'] else 'FAILED'}: {res['applied']} edit(s) applied, "
                 f"{len(res['failures'])} failed ({state})")
    return CliResult(res, text="\n".join(lines))


def _cli_docx_diff(args):
    from tundlekit.cli_support import CliResult

    res = docx_diff(args.old, args.new, search=args.search, emit_edits=args.emit_edits)
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
