#!/usr/bin/env python3
"""Deterministic checks for Chinese <-> English SWE translations.

Deliberately small: only failure modes a script can judge reliably.
  FM-10 garbled input     encoding FILE [--repair OUT]
  FM-3  protected spans   spans SRC TGT
  FM-1  listed terms      glossary SRC TGT --dir zh-en|en-zh
        prompt helper     glossary-slice SRC --dir ...
        everything        all SRC TGT --dir ...
Modal force, embellishment, omission, scope, causality, actors, and status
(FM-2, FM-4..FM-9) are judged by the critic pass (../prompts/critic.md), not
here. Passing tcheck means "no mechanical damage", not "faithful".

FILE/SRC/TGT accept `path:START-END` to select a 1-based inclusive line range.
If a file contains a <translation>...</translation> block (the translator
prompt's output format), only that block is checked. Check the translation
itself, not a note that also carries the original in footnotes.

Overrides: a glossary row that does not apply in context (e.g. 进程 meaning
"course of events", not an OS process) is overridden by a reader-visible
`[TN: ...]` in the target that names the source term. The override is
reported, never silent.

Exit status: 0 = no hard failures (warnings may be printed), 1 = hard
failure, 2 = usage error. Stdlib only.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_GLOSSARY = Path(__file__).resolve().parent / "data" / "glossary.tsv"
BOM = "\ufeff"
REPLACEMENT = "\ufffd"
CJK = re.compile("[\u3400-\u9fff\uf900-\ufaff]")
# Python's \w matches CJK, so `第3步` has no \b before the 3. Literal
# boundaries below use this ASCII class instead.
W = "A-Za-z0-9_"


@dataclass
class Report:
    """Hard failures, warnings, and context lines from one check."""

    fails: list[str] = field(default_factory=list)
    warns: list[str] = field(default_factory=list)
    infos: list[str] = field(default_factory=list)

    def extend(self, other: "Report") -> None:
        self.fails += other.fails
        self.warns += other.warns
        self.infos += other.infos

    def render(self, title: str) -> str:
        status = "FAIL" if self.fails else ("WARN" if self.warns else "OK")
        out = [f"== {title}: {status}"]
        out += [f"  FAIL  {m}" for m in self.fails]
        out += [f"  WARN  {m}" for m in self.warns]
        out += [f"  info  {m}" for m in self.infos]
        return "\n".join(out)


def _short(s: str, n: int = 70) -> str:
    s = s.replace("\n", "\\n")
    return repr(s if len(s) <= n else s[: n - 1] + "…")


# --------------------------------------------------------------------------
# Input


def _split_range(spec: str) -> tuple[str, tuple[int, int] | None]:
    m = re.fullmatch(r"(.+):(\d+)-(\d+)", spec)
    if m and not Path(spec).exists():
        return m.group(1), (int(m.group(2)), int(m.group(3)))
    return spec, None


def read_text(spec: str) -> str:
    """Read `path` or `path:START-END` as UTF-8 (CRLF normalised); join all <translation> blocks."""
    path, lines = _split_range(spec)
    text = Path(path).read_bytes().decode("utf-8", errors="replace").replace("\r\n", "\n")
    if lines:
        text = "\n".join(text.splitlines()[lines[0] - 1 : lines[1]]) + "\n"
    blocks = re.findall(r"<translation>\n?(.*?)\n?</translation>", text, re.S)
    return "\n\n".join(blocks) if blocks else text


FENCE = re.compile(r"^([ \t]*)(`{3,}|~{3,})([^\n]*)\n(.*?)^\1\2[ \t]*$", re.M | re.S)
FENCE_OPEN = re.compile(r"^[ \t]*(`{3,}|~{3,})", re.M)
INLINE = re.compile(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)")
TN = re.compile(r"\[(?:TN|AMBIGUOUS):[^\]]*\]")


def prose_only(text: str) -> str:
    """Text with fenced blocks and inline code removed, and ** / __ emphasis markers dropped.

    Dropping emphasis lets `**S**afety` match the term "safety".
    """
    return INLINE.sub(" ", FENCE.sub("\n", text)).replace("**", "").replace("__", "")


# --------------------------------------------------------------------------
# FM-10 encoding

# CP1252 renderings of UTF-8 continuation bytes 0x80-0xBF. The bytes CP1252
# leaves undefined (0x81 0x8D 0x8F 0x90 0x9D) survive as C1 controls, which
# the \x80-\xbf range covers along with 0xA0-0xBF.
_CONT = r"\x80-\xbf" + "ŒœŠšŸŽžƒˆ˜–—‘’‚“”„†‡•…‰‹›€™"
# A 3-byte UTF-8 lead E2-E9 or EF (CJK ideographs, CJK punctuation,
# full-width forms) read as CP1252 (â-é, ï) followed by two continuations,
# or a 2-byte lead C2/C3 (Â Ã) followed by one.
MOJIBAKE = re.compile(f"[â-éï][{_CONT}]{{2}}|[ÂÃ][{_CONT}]")


def _unmojibake_line(line: str) -> str | None:
    """Undo one UTF-8 -> CP1252 misdecode; None if the line doesn't round-trip."""
    try:
        raw = bytes(ord(c) if ord(c) < 256 else c.encode("cp1252")[0] for c in line)
        return raw.decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None


def repair_mojibake(text: str) -> tuple[str, int]:
    """Repair mojibake lines, leaving clean lines untouched. Returns (text, lines_fixed)."""
    out, fixed = [], 0
    for line in text.split("\n"):
        if MOJIBAKE.search(line):
            repaired = _unmojibake_line(line)
            if repaired is not None:
                line, fixed = repaired, fixed + 1
        out.append(line)
    return "\n".join(out).removeprefix(BOM), fixed


def check_encoding(spec: str) -> Report:
    """Fail on undecodable bytes, U+FFFD, mid-file BOMs, or mojibake in prose.

    Mojibake inside backticks or code fences is ignored: documents that
    *describe* encoding damage quote it that way (notes/04-gotchas.md).
    """
    r = Report()
    data = Path(_split_range(spec)[0]).read_bytes()
    try:
        text = data.decode("utf-8").replace("\r\n", "\n")
    except UnicodeDecodeError as e:
        r.fails.append(f"not valid UTF-8 at byte {e.start}; if it is GBK, try `iconv -f gb18030 -t utf-8`")
        return r
    if text.startswith(BOM):
        r.warns.append("UTF-8 BOM at start of file (harmless alone; often accompanies mojibake)")
    if BOM in text[1:]:
        r.fails.append(f"{text.count(BOM, 1)} BOM character(s) mid-file")
    if REPLACEMENT in text:
        r.fails.append(f"{text.count(REPLACEMENT)} U+FFFD replacement character(s): bytes were lost upstream")
    hits = [(i, ln) for i, ln in enumerate(prose_only(text).splitlines(), 1) if MOJIBAKE.search(ln)]
    if hits:
        r.fails.append(
            f"CP1252 mojibake on {len(hits)} prose line(s) (UTF-8 read as Windows-1252); do not "
            f"translate as-is (FM-10). Repair a copy: tcheck.py encoding {spec} --repair OUT"
        )
        for _, ln in hits[:3]:
            fixed = _unmojibake_line(ln.removeprefix(BOM))
            r.infos.append(_short(ln, 40) + (f"  ->  {_short(fixed, 30)}" if fixed else ""))
    return r


# --------------------------------------------------------------------------
# FM-3 protected spans

URL = re.compile(r"https?://[^\s<>()\[\]\u3000-\u303f\u3400-\u9fff\uff00-\uffef]+")
PATH = re.compile(
    rf"(?<![{W}./~-])"
    rf"(?:(?:~|\.{{1,2}})?/[{W}.-]+(?:/[{W}.-]+)*/?"  # rooted: ~/a  /a  ./a  ../a
    rf"|[{W}.-]+(?:/[{W}.-]+)+\.[A-Za-z0-9]{{1,6}})"  # relative, must end in an extension
    rf"(?![{W}/])"
)
NUMBER = re.compile(rf"(?<![{W}.])\d+(?:[.,]\d+)*(?![{W}])")
TRANSLATED_COMMENT_LINE = re.compile(r"^\s*[-*]\s*line\s+\d+\b.*$", re.M | re.I)
LINK_TARGET = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HARD_KINDS = ("code block", "inline code", "link target", "URL", "path")


def extract_spans(text: str) -> dict[str, Counter]:
    """Multisets of protected literals by kind; each literal counts under one kind only."""
    spans: dict[str, Counter] = {k: Counter() for k in (*HARD_KINDS, "number")}
    for m in FENCE.finditer(text):
        spans["code block"][f"{m.group(3).strip()}\n{m.group(4).rstrip()}"] += 1
    prose = TRANSLATED_COMMENT_LINE.sub("", FENCE.sub("\n", text))
    for m in INLINE.finditer(prose):
        spans["inline code"][m.group(2).strip()] += 1
    prose = INLINE.sub(" ", prose)
    # Link targets, including Chinese heading anchors like (#胶囊定义), stay verbatim.
    for m in LINK_TARGET.finditer(prose):
        spans["link target"][m.group(1)] += 1
    prose = LINK_TARGET.sub("] ", prose)
    for m in URL.finditer(prose):
        spans["URL"][m.group(0).rstrip(".,;:!?'\"")] += 1
    prose = URL.sub(" ", prose)
    for m in PATH.finditer(prose):
        spans["path"][m.group(0).rstrip(".")] += 1
    prose = PATH.sub(" ", prose)
    for m in NUMBER.finditer(prose):
        spans["number"][m.group(0)] += 1
    return spans


GLOSS = re.compile("[(（][\u3400-\u9fff]{1,6}[)）]")  # a term gloss, not a sentence


def untranslated_ratio(text: str) -> float:
    """Share of Chinese in target prose, weighting one CJK character as ~2.5 Latin letters.

    Ignores inline code, fences, [TN]/[AMBIGUOUS] notes, and short
    parenthesised glosses of up to six characters such as "capsule (胶囊)".
    A parenthesised sentence of Chinese still counts.
    """
    prose = GLOSS.sub(" ", TN.sub(" ", prose_only(text)))
    cjk = len(CJK.findall(prose))
    units = cjk + len(re.findall(r"[A-Za-z]", prose)) / 2.5
    return cjk / units if units else 0.0


def check_spans(src: str, tgt: str, direction: str | None = None) -> Report:
    """Missing code/inline/link-target/URL/path fails; missing numbers and anything added warn."""
    r = Report()
    s = extract_spans(src)
    t = extract_spans(tgt)
    for kind in (*HARD_KINDS, "number"):
        for lit, n in (s[kind] - t[kind]).items():
            (r.fails if kind in HARD_KINDS else r.warns).append(f"{kind} missing from target ({n}x): {_short(lit)}")
        for lit, n in (t[kind] - s[kind]).items():
            r.warns.append(f"{kind} added in target ({n}x): {_short(lit)}")
    for text, side in ((src, "source"), (tgt, "target")):
        if FENCE_OPEN.search(FENCE.sub("", text)):
            r.warns.append(f"unbalanced code fence in {side}: a line range may have cut a block in half")
    if direction == "zh-en":
        ratio = untranslated_ratio(tgt)
        if ratio > 0.30:
            r.fails.append(f"target prose is {ratio:.0%} Chinese: untranslated, or the original was left in (FM-5)")
        elif ratio > 0.05:
            r.warns.append(f"target prose is {ratio:.0%} Chinese: check for untranslated passages "
                           "or footnoted originals (check the translation only)")
    if any(CJK.search(b) for b in s["code block"]):
        r.infos.append("source code blocks contain CJK: keep them byte-identical; translate comments "
                       "in a `*Translated comments:*` list (RULES.md 1.1)")
    return r


# --------------------------------------------------------------------------
# FM-1 glossary

GLOSSARY_FIELDS = ["en", "zh", "banned_en", "banned_zh", "domain", "status", "evidence", "note"]


def _alts(cell: str) -> list[str]:
    return [a.strip() for a in cell.split("|") if a.strip()]


def load_glossary(path: Path = DEFAULT_GLOSSARY) -> tuple[list[dict[str, str]], list[str]]:
    """(rows, problems). `#` lines are comments; `|` separates alternatives."""
    with open(path, encoding="utf-8", newline="") as f:
        lines = [ln for ln in f if ln.strip() and not ln.startswith("#")]
    rows, problems = [], []
    for n, row in enumerate(csv.DictReader(lines, delimiter="\t", quoting=csv.QUOTE_NONE), 2):
        if None in row or any(row.get(k) is None for k in GLOSSARY_FIELDS):
            problems.append(f"glossary row {n}: wrong column count (tab inside a cell?)")
            continue
        clean = {k: row[k].strip() for k in GLOSSARY_FIELDS}
        if clean["status"] not in ("approved", "pending"):
            problems.append(f"glossary row {n}: status {clean['status']!r} is not approved|pending")
        if clean["status"] == "approved" and not (clean["en"] and clean["zh"]):
            problems.append(f"glossary row {n}: approved row needs both en and zh")
        rows.append(clean)
    # Two approved rows must not map the same source term to disjoint renderings.
    for s_col, t_col in (("zh", "en"), ("en", "zh")):
        seen: dict[str, set[str]] = {}
        for row in rows:
            if row["status"] != "approved":
                continue
            for a in _alts(row[s_col]):
                targets = {t.lower() for t in _alts(row[t_col])}
                if a.lower() in seen and not seen[a.lower()] & targets:
                    problems.append(f"glossary conflict: {a!r} has two approved {t_col} renderings")
                seen.setdefault(a.lower(), set()).update(targets)
    return rows, problems


def term_in(text: str, term: str, english: bool, loose: bool = False) -> bool:
    """Chinese: substring. English: word-bounded, case-insensitive, plural (loose: also -ed/-ing)."""
    return _term_rx(term, english, loose).search(text) is not None


def _columns(direction: str) -> tuple[str, str, str]:
    """(source column, target column, banned-target column)."""
    return ("zh", "en", "banned_en") if direction == "zh-en" else ("en", "zh", "banned_zh")


def _term_rx(term: str, english: bool, loose: bool = False) -> re.Pattern:
    if not english or CJK.search(term):
        return re.compile(re.escape(term))
    suffix = "(?:s|es|d|ed|ing)?" if loose else "(?:s|es)?"
    return re.compile(rf"(?<![{W}]){re.escape(term)}{suffix}(?![{W}])", re.I)


def _longest_first(terms) -> list[str]:
    # Ties break alphabetically so results never depend on set/hash order.
    return sorted(set(terms), key=lambda term: (-len(term), term))


def _mask(text: str, terms: list[str], english: bool, loose: bool = False) -> tuple[str, set[str]]:
    """Blank out terms longest-first; return the masked text and the terms that matched.

    Longest-first means a longer term claims its span before any term it
    contains: 信任等级 before 信任, "side effect" before "effect".
    """
    found = set()
    for term in _longest_first(terms):
        rx = _term_rx(term, english, loose)
        if rx.search(text):
            found.add(term)
            text = rx.sub(lambda m: "\x00" * len(m.group(0)), text)
    return text, found


def select_domains(rows: list[dict[str, str]], domains: str) -> list[dict[str, str]]:
    """Rows whose domain is in the comma-separated DOMAINS list."""
    wanted = {d.strip() for d in domains.split(",") if d.strip()}
    return [row for row in rows if row["domain"] in wanted]


def _relevance(rows: list[dict[str, str]], src: str, direction: str):
    """(relevant rows, shadowed approved rows).

    All rows claim source spans longest-first, so 信任等级 is read as one
    term rather than as 信任 plus 等级. When a *pending* row's longer term
    hides every occurrence of an approved row, the approved row is reported as
    shadowed, never silently dropped. Otherwise appending a pending row could
    switch off an approved one.
    """
    s_col = _columns(direction)[0]
    en = s_col == "en"
    prose = prose_only(src)
    _, found = _mask(prose, [a for row in rows for a in _alts(row[s_col])], en)
    approved_terms = [a for row in rows if row["status"] == "approved" for a in _alts(row[s_col])]
    _, found_approved_only = _mask(prose, approved_terms, en)
    relevant, shadowed = [], []
    for row in rows:
        terms = set(_alts(row[s_col]))
        if found & terms:
            relevant.append(row)
        elif row["status"] == "approved" and found_approved_only & terms:
            shadowed.append(row)
    return relevant, shadowed


def relevant_rows(rows: list[dict[str, str]], src: str, direction: str) -> list[dict[str, str]]:
    """Rows whose source term occurs in SRC prose, each span claimed by its longest term."""
    return _relevance(rows, src, direction)[0]


def check_glossary(src: str, tgt: str, direction: str, rows: list[dict[str, str]]) -> Report:
    """Per approved row present in the source:

    - a banned rendering with no approved rendering in the target fails (the
      wrong term was used instead of the right one);
    - a banned rendering alongside an approved one warns (it may translate
      something else in the same text);
    - no approved rendering at all warns;
    - a [TN] naming the source term overrides the row for the whole document.
    """
    r = Report()
    s_col, t_col, b_col = _columns(direction)
    t_en = t_col == "en"
    notes = " ".join(TN.findall(tgt))
    tgt_prose = TN.sub(" ", prose_only(tgt))
    relevant, shadowed = _relevance(rows, src, direction)
    for row in shadowed:
        r.warns.append(f"approved row {_alts(row[s_col])[0]} is not enforced here: every occurrence sits inside a "
                       "longer PENDING term. A human must approve or reject that pending row")
    renderings = [a for row in relevant if row["status"] == "approved" for a in _alts(row[t_col])]
    allowed = {a.lower() for a in renderings}
    for row in relevant:
        label = f"{_alts(row[s_col])[0]} -> {(_alts(row[t_col]) or ['?'])[0]}"
        if row["status"] != "approved":
            r.infos.append(f"pending term present: {label} (not enforced; see its note)")
            continue
        if any(term_in(notes, a, s_col == "en") for a in _alts(row[s_col])):
            r.infos.append(f"overridden by a [TN] naming the term: {label}. The override covers the whole "
                           "document; the critic checks every occurrence")
            continue
        # An approved rendering found only inside a banned phrase ("trust" in
        # "trust class") does not count as present.
        outside_banned, _ = _mask(tgt_prose, _alts(row[b_col]), t_en, loose=True)
        approved_present = any(term_in(outside_banned, a, t_en, loose=True) for a in _alts(row[t_col]))
        banned_hit = False
        for banned in _alts(row[b_col]):
            # Mask correct renderings first ("effects" inside "side effects"),
            # but never one the banned term contains ("trust" inside "trust class").
            shields = [a for a in renderings if a.lower() not in banned.lower()]
            unclaimed, _ = _mask(tgt_prose, shields, t_en, loose=True)
            if not term_in(unclaimed, banned, t_en, loose=True):
                continue
            banned_hit = True
            msg = f"banned rendering {banned!r} used (row {label})"
            if approved_present or banned.lower() in allowed:
                r.warns.append(msg + "; an approved rendering is also present, so it may translate something else. Verify")
            else:
                r.fails.append(msg + " and no approved rendering is present. If the row doesn't apply in this "
                               "sense, add a [TN] naming the source term")
        if not approved_present and not banned_hit:
            r.warns.append(f"approved rendering not found: {label}")
    return r


def glossary_slice(src: str, direction: str, rows: list[dict[str, str]]) -> str:
    cols = ["en", "zh", "banned_en", "banned_zh", "status", "note"]
    body = ["\t".join(row[c] for c in cols) for row in relevant_rows(rows, src, direction)]
    return "\n".join(["\t".join(cols), *body])


# --------------------------------------------------------------------------
# CLI


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--glossary", type=Path, default=DEFAULT_GLOSSARY)
    sub = p.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("encoding", help="FM-10 garbled-input check")
    e.add_argument("file")
    e.add_argument("--repair", metavar="OUT", help="write a repaired copy to OUT (never in place)")
    for name in ("spans", "glossary", "all"):
        q = sub.add_parser(name)
        q.add_argument("src")
        q.add_argument("tgt")
        q.add_argument("--dir", choices=("zh-en", "en-zh"), required=name != "spans")
        if name != "spans":
            q.add_argument("--domains", default="general,ai4research",
                           help="glossary domains to enforce (default: general,ai4research; "
                                "use `general` for text unrelated to AI4Research)")
    g = sub.add_parser("glossary-slice", help="print glossary rows relevant to SRC")
    g.add_argument("src")
    g.add_argument("--dir", choices=("zh-en", "en-zh"), required=True)
    g.add_argument("--domains", default="general,ai4research")
    a = p.parse_args(argv)

    if a.cmd == "encoding":
        rep = check_encoding(a.file)
        print(rep.render(f"encoding {a.file}"))
        if a.repair:
            text, n = repair_mojibake(read_text(a.file))
            Path(a.repair).write_text(text, encoding="utf-8")
            print(f"  repaired {n} line(s) -> {a.repair}; re-run `encoding` on it before use")
        return 1 if rep.fails else 0

    rows, problems = load_glossary(a.glossary)
    if a.cmd != "spans":
        rows = select_domains(rows, a.domains)
    if a.cmd == "glossary-slice":
        for msg in problems:
            print(f"WARN {msg}", file=sys.stderr)
        print(glossary_slice(read_text(a.src), a.dir, rows))
        return 0

    src, tgt = read_text(a.src), read_text(a.tgt)
    steps = []
    if a.cmd == "all":
        steps += [(f"encoding {f}", lambda f=f: check_encoding(f)) for f in (a.src, a.tgt)]
    if a.cmd in ("spans", "all"):
        steps.append(("spans (FM-3)", lambda: check_spans(src, tgt, a.dir)))
    if a.cmd in ("glossary", "all"):
        def run_glossary() -> Report:
            rep = check_glossary(src, tgt, a.dir, rows)
            rep.warns[:0] = problems
            return rep
        steps.append((f"glossary {a.dir} (FM-1)", run_glossary))
    total = Report()
    for title, run in steps:
        rep = run()
        print(rep.render(title))
        total.extend(rep)
    if a.cmd == "all":
        print(f"\n{len(total.fails)} hard failure(s), {len(total.warns)} warning(s). Passing means no "
              "mechanical damage, not faithful: run the critic for FM-2 and FM-4..9 (prompts/critic.md).")
    return 1 if total.fails else 0


if __name__ == "__main__":
    sys.exit(main())
