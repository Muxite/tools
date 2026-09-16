"""Report and deck review tools (MANIFEST.md §15.1).

review_coverage checks that a report and its deck make the same argument: every numbered body section is covered
by a slide (a `§N.M` footer or a similar title), every content slide covers a section, footers cite sections that
exist, and the design rules `R<n>` appear in both with the same names.

Standard library only at import; a .pptx deck needs python-pptx, imported lazily by tundlekit.deck.
"""
from __future__ import annotations

import difflib
import math
import pathlib
import re

from tundlekit.registry import ToolError, tool

SECTION_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
NUMBERED_RE = re.compile(r"^(\d+(?:\.\d+)?)\.?\s+(.*)$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
RULE_LINE_RE = re.compile(r"^\s*[-*•]?\s*R(\d+)\b[.:)]?\s+(.*)")
RULE_CELL_RE = re.compile(r"R(\d+)")
SECTION_REF_RE = re.compile(r"§\s*(\d+(?:\.\d+)*)")
PAPER_CONTEXT_RE = re.compile(r"arxiv|\bpaper\b", re.I)
CUT_SECTION_RE = re.compile(r"^§\s*(\d+(?:\.\d+)*)\.?$")
CUT_SLIDE_RE = re.compile(r"^slide\s+(\S+)$", re.I)
NUMBER_TEXT_RE = re.compile(r"[0-9]+[a-z]?")
FOOTER_TOP_IN = 6.9
EMU_PER_INCH = 914400
RULE_NAME_SIMILARITY = 0.5


def _norm(text: str) -> str:
    return " ".join(re.sub(r"[^\w\s]", "", text.lower()).split())


def similarity(a: str, b: str) -> float:
    """§15.1: SequenceMatcher ratio on lower-cased text with punctuation removed and whitespace collapsed."""
    return difflib.SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def _display(path: str) -> str:
    return str(path).replace("\\", "/")


def _read_text(path: str, what: str) -> str:
    p = pathlib.Path(path)
    try:
        return p.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise ToolError(f"{what} not found: {path}") from None
    except (OSError, ValueError) as e:
        raise ToolError(f"cannot read {what} {path}: {e}") from None


def _table_cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_separator_row(line: str) -> bool:
    return bool(re.fullmatch(r"\s*\|?[\s:|-]*-[\s:|-]*\|?\s*", line))


# ------------------------------------------------------------------ report
def read_report(text: str) -> tuple[list[dict], dict[str, tuple[int, str]]]:
    """(sections, rules) from the body bucket (§14.2) of a Markdown report.

    sections: [{"section", "heading", "line", "level"}] for numbered level-2/3 headings.
    rules: {n: (line, name)} for the first occurrence of each rule.
    """
    sections, rules = [], {}
    bucket, in_fence = "body", False
    for no, line in enumerate(text.splitlines(), 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = SECTION_HEADING_RE.match(line)
        if m:
            level, heading = len(m.group(1)), m.group(2).strip()
            if level == 1:
                bucket = "body"
            elif level == 2:
                if re.match(r"(?i)^(references|bibliography)\b", heading):
                    bucket = "references"
                elif re.match(r"(?i)^appendix\b", heading):
                    bucket = "appendix"
                else:
                    bucket = "body"
            if bucket == "body" and level in (2, 3):
                num = NUMBERED_RE.match(heading)
                if num:
                    sections.append({"section": num.group(1), "heading": num.group(2).strip(),
                                     "line": no, "level": level})
            continue
        if bucket != "body":
            continue
        n, name = _rule_in_line(line)
        if n is None and line.lstrip().startswith("|") and not _is_separator_row(line):
            cells = _table_cells(line)
            cm = RULE_CELL_RE.fullmatch(cells[0]) if cells else None
            if cm and len(cells) > 1:
                n, name = _rule_id(cm.group(1)), cells[1]
        if n is not None and n not in rules:
            rules[n] = (no, name)
    return sections, rules


def _rule_id(digits: str) -> str:
    """`R07` and `R7` are the same rule (no int(): the digit run may be arbitrarily long)."""
    return digits.lstrip("0") or "0"


def _rule_in_line(line: str):
    m = RULE_LINE_RE.match(line)
    if not m:
        return None, None
    return _rule_id(m.group(1)), m.group(2).strip()


# ------------------------------------------------------------------ deck
def _rules_from(lines: list[str], table_rows: list[list[str]]) -> dict[str, str]:
    """{n: name} of the rules on 1 slide, first occurrence wins."""
    found = {}
    for line in lines:
        n, name = _rule_in_line(line)
        if n is not None:
            found.setdefault(n, name)
    for row in table_rows:
        if not row:
            continue
        first = row[0].strip()
        cm = RULE_CELL_RE.fullmatch(first)
        if cm and len(row) > 1:
            found.setdefault(_rule_id(cm.group(1)), row[1].strip())
            continue
        n, name = _rule_in_line(first)
        if n is not None:
            found.setdefault(n, name)
    return found


def _spec_blocks(body) -> list[dict]:
    if isinstance(body, dict):
        return [body]
    if isinstance(body, list):
        return [b for b in body if isinstance(b, dict)]
    return []


def _spec_slides(path: str) -> list[dict]:
    from tundlekit import deck

    plan = deck.Plan(*deck.load_spec(None, path))
    slides = []
    for sl in plan.slides:
        if sl["type"] != "content":
            continue
        s = sl["spec"]
        lines, rows = [], []
        for key in ("title", "eyebrow", "source", "thus"):
            if isinstance(s.get(key), str):
                lines.extend(s[key].split("\n"))
        lines.extend(deck._strip_texts(s))
        for block in _spec_blocks(s.get("body")):
            kind = block.get("kind")
            if kind in ("bullets", "lines"):
                for item in block.get("items") or []:
                    lines.extend(str(item).split("\n"))
            elif kind == "table":
                rows.extend([str(c) for c in r] for r in block.get("rows") or [])
            elif kind in ("excerpt", "point"):
                lines.extend(str(block.get("text", "")).split("\n"))
                if block.get("caption"):
                    lines.extend(str(block["caption"]).split("\n"))
            elif kind == "chart":
                lines.extend(str(c) for c in block.get("categories") or [])
                if block.get("takeaway"):
                    lines.append(str(block["takeaway"]))
        slides.append({"position": sl["position"], "number": sl["number"], "title": sl["title"],
                       "footer": s.get("source") or "", "rules": _rules_from(lines, rows)})
    return slides


def _pptx_slides(path: str) -> list[dict]:
    from tundlekit import deck

    prs = deck._open_pptx(path)
    slides = []
    for pos, slide in enumerate(prs.slides, 1):
        info = deck.read_slide(slide, pos)
        if info["number"] is None:
            continue
        lines, rows, footer = [], [], []
        for sh in deck._iter_shapes(slide.shapes):
            if getattr(sh, "has_text_frame", False) and sh.has_text_frame:
                text = sh.text_frame.text.replace("\x0b", "\n").replace("\r", "\n")
                lines.extend(text.split("\n"))
                top = sh.top
                stripped = text.strip()
                if (top is not None and top >= FOOTER_TOP_IN * EMU_PER_INCH and stripped
                        and not NUMBER_TEXT_RE.fullmatch(stripped)):
                    footer.append(stripped)
            if getattr(sh, "has_table", False) and sh.has_table:
                rows.extend([c.text for c in r.cells] for r in sh.table.rows)
        slides.append({"position": pos, "number": info["number"], "title": info["title"],
                       "footer": " ; ".join(footer), "rules": _rules_from(lines, rows)})
    return slides


def footer_citations(footer: str) -> list[str]:
    """Report sections a footer cites: `§N[.M]` mentions, skipping those after `arXiv` or `paper` in a segment."""
    cited = []
    for segment in re.split(r"[;·]", footer):
        for m in SECTION_REF_RE.finditer(segment):
            if PAPER_CONTEXT_RE.search(segment[:m.start()]):
                continue
            if m.group(1) not in cited:
                cited.append(m.group(1))
    return cited


# ------------------------------------------------------------------ cuts
def read_cuts(path: str) -> tuple[set[str], set[str]]:
    sections, slides = set(), set()
    for no, raw in enumerate(_read_text(path, "cuts file").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        m = CUT_SECTION_RE.match(line)
        if m:
            sections.add(m.group(1))
            continue
        m = CUT_SLIDE_RE.match(line)
        if m:
            slides.add(m.group(1))
            continue
        raise ToolError(f"cuts file {path} line {no}: expected '§N.M' or 'slide N', got {line!r}")
    return sections, slides


# ------------------------------------------------------------------ tool
@tool("review_coverage",
      "Check that a Markdown report and its deck (.pptx or deck spec .json) cover the same argument. Sections are "
      "the report's numbered level-2/3 body headings; a content slide covers a section when its source footer "
      "cites §N or §N.M (not after 'arXiv' or 'paper') or its title is similar to the heading (>= threshold, "
      "default 0.6). Findings: C001 section covered by no slide; C002 slide covering no section; C003 footer "
      "citing a section that does not exist; C004 rule R<n> in only 1 document; C005 rule names differ; C006 "
      "rule on several slides. cuts lists agreed cuts ('§2.7' or 'slide 12', # comments). Returns the outline "
      "with covering slides. A .pptx needs python-pptx.",
      {"type": "object",
       "properties": {
           "report": {"type": "string", "description": "the Markdown report"},
           "deck": {"type": "string", "description": "the deck: .pptx or deck spec .json"},
           "cuts": {"type": "string", "description": "text file of agreed cuts, 1 per line"},
           "threshold": {"type": "number", "description": "title similarity that covers a section (default 0.6)"}},
       "required": ["report", "deck"],
       "additionalProperties": False},
      readOnlyHint=True)
def review_coverage(report: str, deck: str, cuts: str | None = None, threshold: float = 0.6) -> dict:
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not math.isfinite(threshold):
        raise ToolError("threshold must be a finite number")
    sections, report_rules = read_report(_read_text(report, "report"))
    if not pathlib.Path(deck).is_file():
        raise ToolError(f"deck not found: {deck}")
    if deck.lower().endswith(".pptx"):
        slides = _pptx_slides(deck)
    else:
        slides = _spec_slides(deck)
    cut_sections, cut_slides = read_cuts(cuts) if cuts is not None else (set(), set())

    report_path, deck_path = _display(report), _display(deck)
    findings = []

    def add(rule, severity, path, line, message, excerpt=""):
        findings.append({"rule": rule, "severity": severity, "path": path, "line": line,
                         "message": message, "excerpt": excerpt[:80]})

    known = {s["section"]: s for s in sections}
    covered_by: dict[str, list[str]] = {s["section"]: [] for s in sections}
    slide_entries = []
    for sl in slides:
        covers = set()
        missing = []
        for ref in footer_citations(sl["footer"]):
            if ref in known:
                covers.add(ref)
            elif ref not in missing:
                missing.append(ref)
        for s in sections:
            if similarity(s["heading"], sl["title"]) >= threshold:
                covers.add(s["section"])
        for ref in missing:
            add("C003", "error", deck_path, sl["position"],
                f"slide {sl['number']} cites §{ref}, which is not a section of the report", sl["footer"])
        ordered = [s["section"] for s in sections if s["section"] in covers]
        for sec in ordered:
            if sl["number"] not in covered_by[sec]:
                covered_by[sec].append(sl["number"])
        slide_entries.append({"number": sl["number"], "title": sl["title"], "sections": ordered})
        if not ordered and sl["number"] not in cut_slides:
            add("C002", "warning", deck_path, sl["position"],
                f"slide {sl['number']} covers no report section", sl["title"])

    for s in sections:
        sec = s["section"]
        covered = bool(covered_by[sec]) or any(
            covered_by[c["section"]] for c in sections if c["section"].startswith(sec + "."))
        if not covered and sec not in cut_sections:
            add("C001", "warning", report_path, s["line"],
                f"section §{sec} is covered by no slide", s["heading"])

    deck_rules: dict[str, list[tuple[dict, str]]] = {}
    for sl in slides:
        for n, name in sl["rules"].items():
            deck_rules.setdefault(n, []).append((sl, name))
    for n in sorted(set(report_rules) | set(deck_rules), key=lambda n: (len(n), n)):
        in_report, on_slides = report_rules.get(n), deck_rules.get(n, [])
        if in_report and not on_slides:
            add("C004", "warning", report_path, in_report[0], f"rule R{n} is in the report but not in the deck",
                in_report[1])
        elif on_slides and not in_report:
            first, name = on_slides[0]
            add("C004", "warning", deck_path, first["position"],
                f"rule R{n} is on slide {first['number']} but not in the report", name)
        else:
            if similarity(in_report[1], on_slides[0][1]) < RULE_NAME_SIMILARITY:
                add("C005", "info", report_path, in_report[0],
                    f"rule R{n} is named {in_report[1]!r} in the report but {on_slides[0][1]!r} in the deck",
                    in_report[1])
        if len(on_slides) > 1:
            numbers = ", ".join(sl["number"] for sl, _ in on_slides)
            add("C006", "info", deck_path, on_slides[0][0]["position"],
                f"rule R{n} appears on {len(on_slides)} slides: {numbers}", on_slides[0][1])

    findings.sort(key=lambda f: (f["path"], f["line"] or 0, f["rule"]))
    counts = {sev: sum(1 for f in findings if f["severity"] == sev) for sev in ("error", "warning", "info")}
    return {"ok": counts["error"] == 0, "findings": findings, "counts": counts,
            "outline": [{"section": s["section"], "heading": s["heading"], "slides": covered_by[s["section"]]}
                        for s in sections],
            "slides": slide_entries}


# ------------------------------------------------------------------ CLI
def add_cli(groups) -> None:
    from tundlekit.cli_support import common_flags

    p = groups.add_parser("review", help="report and deck review checks")
    cmds = p.add_subparsers(dest="command", required=True)
    c = cmds.add_parser("coverage", help="check that a report and its deck cover the same sections and rules")
    c.add_argument("report", help="the Markdown report")
    c.add_argument("deck", help="the deck (.pptx or deck spec .json)")
    c.add_argument("--cuts", help="text file of agreed cuts ('§2.7' or 'slide 12' per line)")
    c.add_argument("--threshold", type=float, default=0.6, help="title similarity that covers a section")
    common_flags(c, checker=True)
    c.set_defaults(handler=_cli_coverage)


def _cli_coverage(args):
    from tundlekit.cli_support import CliResult, format_findings

    r = review_coverage(args.report, args.deck, cuts=args.cuts, threshold=args.threshold)
    outline = [f"  §{e['section']} {e['heading']}: slides {', '.join(e['slides']) or '-'}" for e in r["outline"]]
    return CliResult(r, text="\n".join(["outline:"] + outline) + "\n" + format_findings(r))
