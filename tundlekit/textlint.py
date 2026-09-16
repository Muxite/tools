"""textlint: report prose and numbering checks (MANIFEST.md §7). Standard library only.

After tundle's style card (notes/40-style-card.md) and its checks (check_forbidden.py, check_fignums.py,
wordcount_sections.py): no em dashes, no first person, no hedges, no contractions, no status markers left in
the text, figure and table numbers that run 1, 2, 3 with every mention resolving, and words per section.
"""
from __future__ import annotations

import bisect
import os
import pathlib
import re
import shutil
import subprocess
from dataclasses import dataclass, field

from tundlekit.registry import ToolError, tool

SEVERITY = {
    "S001": "error", "S002": "error", "S003": "warning", "S004": "error", "S005": "warning", "S006": "error",
    "S007": "warning", "S008": "error", "S009": "warning", "S010": "warning", "S011": "warning",
}
DEFAULT_MAX_WORDS = 42
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
RULE_ID = re.compile(r"\b[Ss]\d{3}\b")


def _blank(chars: list[str], start: int, end: int) -> None:
    for k in range(start, end):
        if chars[k] != "\n":
            chars[k] = " "


def mask_markdown(lines: list[str]) -> tuple[list[str], dict[int, set | None]]:
    """Replace code, comments, URLs, link targets and front matter by spaces (columns are kept).

    Returns (masked lines, suppressions) where suppressions maps a 1-based line number to the rule ids a
    `<!-- lint-ignore ... -->` comment suppresses there (None: every rule).
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
ABBREVIATIONS_EXACT = {"Fig.", "Eq.", "No."}
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


def _sentences(par: _Paragraph) -> list[_Sentence]:
    out = []
    start = 0
    ends = [m.end() for m in SENTENCE_END.finditer(par.text) if not _is_abbreviation(par.text, m)]
    for end in ends + [len(par.text)]:
        chunk = par.text[start:end]
        words = _count_words(chunk)
        if words:
            lead = len(chunk) - len(chunk.lstrip())
            out.append(_Sentence(par.line_at(start + lead), words, par.original[start:end], par.section))
        start = end
    return out


# ====================================================================== line rules
FIRST_PERSON = re.compile(r"\b(?:[Ww][Ee]|[Oo][Uu][Rr][Ss]?|[Uu][Ss])\b|\bI(?= [a-z])")
HEDGES = re.compile(r"(?i:\b(?:arguably|seems|seem|seemingly|perhaps|somewhat|possibly|might"
                    r"|to\s+some\s+extent|it\s+appears)\b)|\bmay\b")
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


def _line_findings(path: str, lineno: int, masked: str, original: str, heading: bool, exempt: bool) -> list:
    out = []
    for rule, pattern, message, in_headings in _LINE_RULES:
        if heading and not in_headings:
            continue
        if rule == "S008" and exempt:
            continue
        for m in pattern.finditer(masked):
            if rule == "S002" and m.group(0) == "US":
                continue
            out.append(_finding(rule, SEVERITY[rule], path, lineno, message.format(m=m.group(0)),
                                _excerpt(original, m.start(), m.end())))
    return out


def lint_text(path: str, text: str, max_words: int = DEFAULT_MAX_WORDS) -> tuple[list[dict], dict]:
    """Run every §7.1 rule over 1 document. Returns (findings before rule filtering, stats)."""
    lines = _split_lines(text)
    masked, suppress = mask_markdown(lines)
    findings: list[dict] = []
    paragraphs: list[_Paragraph] = []
    current: _Paragraph | None = None
    exempt_level: int | None = None
    section: int | None = None

    def flush():
        nonlocal current
        if current is not None:
            paragraphs.append(current)
        current = None

    for idx, mline in enumerate(masked):
        lineno, original = idx + 1, lines[idx]
        if not mline.strip():
            flush()
            continue
        heading = HEADING.match(mline)
        if heading:
            flush()
            level, title = len(heading.group(1)), (heading.group(2) or "").rstrip("#").strip()
            if exempt_level is not None and level <= exempt_level:
                exempt_level = None
            if exempt_level is None and EXEMPT_HEADING.match(title):
                exempt_level = level
            section = 0 if section is None else section + 1
            findings += _line_findings(path, lineno, mline, original, True, exempt_level is not None)
            continue
        if _is_table_separator(mline) or THEMATIC_BREAK.match(mline):
            flush()
            continue
        findings += _line_findings(path, lineno, mline, original, False, exempt_level is not None)
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

    sentences = []
    for par in paragraphs:
        sentences += _sentences(par)
    opened: set[int] = set()        # sections whose first prose sentence has been checked
    for s in sentences:
        if s.words > max_words:
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

    findings = [f for f in findings if not _suppressed(suppress, f)]
    words = [s.words for s in sentences]
    stats = {"sentences": len(words), "words": sum(words),
             "mean_sentence_words": _round1(sum(words) / len(words)) if words else 0.0,
             "max_sentence_words": max(words, default=0),
             "list_items": sum(1 for p in paragraphs if p.is_item)}
    return findings, stats


def _suppressed(suppress: dict, finding: dict) -> bool:
    line = finding["line"]
    if line not in suppress:
        return False
    ids = suppress[line]
    return ids is None or finding["rule"] in ids


def _round1(x: float) -> float:
    """Round half up to 1 decimal place."""
    return int(x * 10 + 0.5 + 1e-9) / 10


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


def _mention_findings(path: str, text: str, known: set, skip_lines: set[int]) -> list[dict]:
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
                                    f"{label} does not match any caption in the reports",
                                    _excerpt(line, m.start(), m.end())))
    return out


# ====================================================================== wordcount (§7.3)
WORDCOUNT_HEADING = re.compile(r"^#{1,3}[ \t]")
FRONT_MATTER = "(front matter)"


def count_sections(text: str) -> list[tuple[str, int]]:
    """[(heading, words)] for headings of level 1-3; fenced code does not start sections."""
    out = []
    name, words = FRONT_MATTER, 0
    fence = None
    for line in _split_lines(text):
        if fence is None:
            m = FENCE_OPEN.match(line)
            if m:
                fence = m.group(1)
            elif WORDCOUNT_HEADING.match(line):
                out.append((name, words))
                name, words = line.strip(), 0
                continue
        elif _fence_close(fence).match(line):
            fence = None
        words += len(line.split())
    out.append((name, words))
    return [(n, w) for n, w in out if n != FRONT_MATTER or w]


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
      "(default 42), S010 framing section openers ('This section...'), S011 jargon (Eq. 3, pp). Code, HTML "
      "comments, URLs, link targets and front matter are skipped; '<!-- lint-ignore S003 -->' silences rules "
      "on its line and the next. paths: files, or directories (walked for *.md and *.txt). Returns {ok, "
      "findings: [{rule, severity, path, line, message, excerpt}], counts, stats: {path: {sentences, words, "
      "mean_sentence_words, max_sentence_words, list_items}}}.",
      {"type": "object",
       "properties": {
           "paths": {"type": "array", "items": {"type": "string"}, "description": "Files or directories."},
           "rules": {"type": "array", "items": {"type": "string"}, "description": "Only these rule ids."},
           "ignore": {"type": "array", "items": {"type": "string"}, "description": "Skip these rule ids."},
           "max_words": {"type": "integer", "description": "S009 sentence length limit (default 42)."},
       },
       "required": ["paths"],
       "additionalProperties": False},
      readOnlyHint=True)
def text_lint(paths: list[str], rules: list[str] | None = None, ignore: list[str] | None = None,
              max_words: int = DEFAULT_MAX_WORDS) -> dict:
    selected = set(_rule_list(rules, "rules")) or set(SEVERITY)
    selected -= set(_rule_list(ignore, "ignore"))
    if isinstance(max_words, bool) or not isinstance(max_words, int) or max_words < 1:
        raise ToolError("max_words: must be a positive integer")
    findings, stats = [], {}
    for shown, p in expand_paths(paths):
        file_findings, stats[shown] = lint_text(shown, _read(shown, p), max_words)
        findings += [f for f in file_findings if f["rule"] in selected]
    return _checker_result(findings, stats=stats)


@tool("text_fignums",
      "Check figure and table numbering in Markdown reports. Captions are lines starting '![Fig. N.', "
      "'*Fig. N.', '**Fig. N.', 'Fig. N.', '*Table N.', '**Table N.' or 'Table N.' (N may have an upper-case "
      "prefix such as E1; each kind and prefix is numbered on its own, per file). F001 duplicate number, F002 "
      "gap, F003 sequence not starting at 1, F004 out of order, F005 a 'Fig. N' or 'Table N' mention (in the "
      "reports, or anywhere in the refs files, e.g. deck footers) with no matching caption in any report. "
      "Mentions after 'arXiv' or 'paper' on the same line are skipped. Returns {ok, findings, counts, "
      "captions: {path: {Fig: {prefix: [numbers]}, Table: {...}}}}.",
      {"type": "object",
       "properties": {
           "paths": {"type": "array", "items": {"type": "string"}, "description": "Report files."},
           "refs": {"type": "array", "items": {"type": "string"},
                    "description": "Other files whose Fig./Table mentions must resolve against the reports."},
       },
       "required": ["paths"],
       "additionalProperties": False},
      readOnlyHint=True)
def text_fignums(paths: list[str], refs: list[str] | None = None) -> dict:
    reports = [(shown, _read(shown, p)) for shown, p in expand_paths(paths)]
    others = [(shown, _read(shown, p)) for shown, p in expand_paths(refs, "refs")] if refs else []
    findings, captions, known, caption_lines = [], {}, set(), {}
    for shown, text in reports:
        seqs, caption_lines[shown] = _captions(text)
        entry = {"Fig": {}, "Table": {}}
        for (kind, prefix), seq in seqs.items():
            entry[kind][prefix] = [number for number, _ in seq]
            known.update((kind, prefix, number) for number, _ in seq)
            findings += _sequence_findings(shown, kind, prefix, seq)
        captions[shown] = {kind: dict(sorted(seqs_.items())) for kind, seqs_ in entry.items()}
    for shown, text in reports:
        findings += _mention_findings(shown, text, known, caption_lines[shown])
    for shown, text in others:
        findings += _mention_findings(shown, text, known, set())
    return _checker_result(findings, captions=captions)


@tool("text_wordcount",
      "Count words per section (headings of level 1-3) in Markdown files. Words are whitespace tokens of the "
      "section body; text before the first heading is '(front matter)' and is left out when empty. With "
      "baseline (a git ref such as a tag), each section also gets the difference against the same file at "
      "that ref ('new' for a heading the baseline lacks). Returns {files: {path: {sections: [{heading, words, "
      "delta}], total, total_delta}}}; deltas are null without a baseline or when the file is not in the ref.",
      {"type": "object",
       "properties": {
           "paths": {"type": "array", "items": {"type": "string"}, "description": "Files or directories."},
           "baseline": {"type": "string", "description": "Git ref to compare against."},
       },
       "required": ["paths"],
       "additionalProperties": False},
      readOnlyHint=True)
def text_wordcount(paths: list[str], baseline: str | None = None) -> dict:
    files = {}
    checked: set = set()
    for shown, p in expand_paths(paths):
        current = count_sections(_read(shown, p))
        old = None
        if baseline is not None:
            old_text = _baseline_text(shown, p, baseline, checked)
            old = count_sections(old_text) if old_text is not None else None
        total = sum(words for _, words in current)
        files[shown] = {"sections": _deltas(current, old), "total": total,
                        "total_delta": None if old is None else total - sum(words for _, words in old)}
    return {"files": files}


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
    common_flags(c)
    c.set_defaults(handler=_cli_wordcount)


def _cli_lint(args):
    from tundlekit.cli_support import CliResult

    return CliResult(text_lint(args.paths, rules=args.rules, ignore=args.ignore, max_words=args.max_words))


def _cli_fignums(args):
    from tundlekit.cli_support import CliResult

    return CliResult(text_fignums(args.paths, refs=args.refs or None))


def _cli_wordcount(args):
    from tundlekit.cli_support import CliResult

    res = text_wordcount(args.paths, baseline=args.baseline)
    lines = []
    for path, info in res["files"].items():
        lines.append(f"=== {path} ===")
        lines.append(f"{'words':>7} {'delta':>7}  section")
        for s in info["sections"]:
            delta = "n/a" if s["delta"] is None else (s["delta"] if s["delta"] == "new" else f"{s['delta']:+d}")
            lines.append(f"{s['words']:>7} {delta:>7}  {s['heading'][:78]}")
        tail = "" if info["total_delta"] is None else f" ({info['total_delta']:+d} vs {args.baseline})"
        lines.append(f"{info['total']:>7} {'':>7}  TOTAL{tail}")
    return CliResult(res, text="\n".join(lines))
