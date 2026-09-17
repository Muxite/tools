"""translate: zh <-> en translation checks and resources (MANIFEST.md §10).

The checker is tundle's tcheck.py, vendored unchanged in tcheck.py and run in-process. The rules, traps,
glossary and prompts ship in data/ and prompts/ and are served by translate_resources.
"""
from __future__ import annotations

import contextlib
import io
import os
import re
import sys
from pathlib import Path

from tundlekit.cli_support import CliResult, common_flags
from tundlekit.registry import ToolError, tool
from tundlekit.translate import tcheck

HERE = Path(__file__).resolve().parent
RESOURCE_DIRS = ("data", "prompts")
MODES = ("encoding", "spans", "glossary", "glossary-slice", "all")
DIRECTIONS = ("zh-en", "en-zh")
NEEDS_TGT = ("spans", "glossary", "all")


def _need_file(spec: str, what: str) -> None:
    path = Path(tcheck._split_range(spec)[0])      # tcheck accepts `path:START-END`
    if not path.is_file():
        raise ToolError(f"{what} not found: {spec}")


def _positional(path: str) -> str:
    """A file argument argparse can't mistake for an option (MANIFEST §13.5)."""
    return os.path.join(".", path) if path.startswith("-") else path


def _tcheck_argv(mode, src, tgt, direction, domains, glossary, repair) -> list[str]:
    # Option values use the `--opt=value` form, so values starting with `-` stay values.
    argv = [f"--glossary={glossary}"] if glossary else []
    if mode == "encoding":
        argv += ["encoding", _positional(src)] + ([f"--repair={repair}"] if repair else [])
    elif mode == "glossary-slice":
        argv += [mode, _positional(src), f"--dir={direction}"]
    else:
        argv += [mode, _positional(src), _positional(tgt), f"--dir={direction}"]
    if domains and mode in ("glossary", "glossary-slice", "all"):
        argv += [f"--domains={','.join(domains)}"]
    return argv


@tool(
    "translate_check",
    "Run the mechanical zh<->en translation checks (tcheck) on files. mode encoding: garbled input "
    "(mojibake, U+FFFD, bad UTF-8; repair writes a fixed copy). spans: code spans, URLs and numbers kept "
    "from src to tgt. glossary: required and banned term renderings per direction. glossary-slice: the "
    "glossary rows relevant to src, to give a translator. all: every check on src and tgt. tgt is required "
    "for spans, glossary and all. Passing means no mechanical damage, not a faithful translation.",
    {"type": "object",
     "properties": {
         "mode": {"type": "string", "enum": list(MODES)},
         "src": {"type": "string", "description": "source file (path or path:START-END)"},
         "tgt": {"type": "string", "description": "translated file (spans, glossary, all)"},
         "direction": {"type": "string", "enum": list(DIRECTIONS), "description": "default zh-en"},
         "domains": {"type": "array", "items": {"type": "string"},
                     "description": "glossary domains to enforce (default general, ai4research)"},
         "glossary": {"type": "string", "description": "glossary TSV path (default: the vendored glossary)"},
         "repair": {"type": "string", "description": "encoding mode: write a repaired copy to this path"},
     },
     "required": ["mode", "src"],
     "additionalProperties": False},
    readOnlyHint=False,
)
def translate_check(mode: str, src: str, tgt: str | None = None, direction: str = "zh-en",
                    domains: list[str] | None = None, glossary: str | None = None,
                    repair: str | None = None) -> dict:
    if mode not in MODES:
        raise ToolError(f"mode must be one of {', '.join(MODES)}, got {mode!r}")
    if direction not in DIRECTIONS:
        raise ToolError(f"direction must be zh-en or en-zh, got {direction!r}")
    if mode in NEEDS_TGT and not tgt:
        raise ToolError(f"mode {mode} needs a target file (tgt)")
    if repair and mode != "encoding":
        raise ToolError("repair applies to encoding mode only")
    _need_file(src, "source file")
    if mode in NEEDS_TGT:
        _need_file(tgt, "target file")
    if glossary and mode != "encoding" and not Path(glossary).is_file():
        raise ToolError(f"glossary not found: {glossary}")
    if repair and Path(repair).exists() and Path(repair).resolve() == Path(tcheck._split_range(src)[0]).resolve():
        raise ToolError("repair must write a copy, not the source itself")

    argv = _tcheck_argv(mode, src, tgt, direction, domains, glossary, repair)
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = tcheck.main(argv)
    except SystemExit as exc:          # tcheck's own usage errors
        code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 2)
        code = code if code == 0 else 2
    except (OSError, UnicodeError, ValueError) as exc:
        raise ToolError(f"translate check failed: {exc}") from None
    return {"exit_code": code, "ok": code == 0, "output": out.getvalue(), "errors": err.getvalue()}


# ---------------------------------------------------------------------------------------------- terms

_AW = "A-Za-z0-9"                                   # ASCII word characters: CJK never counts as a boundary word
CAMEL = re.compile(rf"(?<![{_AW}])(?:[A-Z][a-z]+[A-Z][{_AW}]*|[a-z]+[A-Z][{_AW}]*)(?![{_AW}])")
CAPS = re.compile(rf"(?<![{_AW}])[A-Z]{{2,}}[{_AW}]*(?![{_AW}])")
_SLASH_PART = rf"(?:[A-Z]{{2,}}[{_AW}]*|[A-Z][a-z]+[A-Z][{_AW}]*|[a-z]+[A-Z][{_AW}]*|[A-Z][0-9]*)"
SLASH = re.compile(rf"(?<![{_AW}/])(?:{_SLASH_PART})(?:/{_SLASH_PART})+(?![{_AW}/])")
ASCII_RUN = re.compile(r"[A-Za-z0-9-]+(?: [A-Za-z0-9-]+)*")
LIST_MARKER = re.compile(r"^[ \t]*(?:[-*+•]|[0-9]{1,9}[.)])[ \t]+")
FENCED = re.compile(r"^[ \t]*(`{3,}|~{3,})[^\n]*\n.*?^[ \t]*\1[ \t]*$", re.M | re.S)
INLINE_CODE = re.compile(r"(`+)(?!`).+?(?<!`)\1(?!`)", re.S)
# ASCII-only classes: a URL or path stops at the first non-ASCII character (MANIFEST §16.6).
URL = re.compile(r"(?:https?|ftp)://[!-~]+|(?<![A-Za-z0-9_.-])www\.[!-~]+")
_PATH_CHARS = r"A-Za-z0-9_.~\-"
FILE_PATH = re.compile(rf"(?<![{_PATH_CHARS}/\\])(?:[A-Za-z]:)?[{_PATH_CHARS}]*(?:[/\\][{_PATH_CHARS}]+)+[/\\]?"
                       r"|(?<![A-Za-z0-9_.-])[A-Za-z0-9_-]+\.(?:py|md|json|jsonl|txt|tsv|csv|ya?ml|toml|js|ts|"
                       r"sh|ps1|bat|pptx|docx|xlsx|pdf|png|jpe?g|svg|html?|xml|ipynb|cfg|ini|log)(?![A-Za-z0-9_])")
CJK = re.compile(r"[㐀-䶿一-鿿豈-﫿぀-ヿ가-힯\U00020000-\U0002ffff]")
CJK_SHARE = 0.30
COMPARES = ("previous", "same-language")


def _blank(m: re.Match) -> str:
    return re.sub(r"[^\n]", " ", m.group(0))


def _terms_text(text: str) -> str:
    """Text with fenced code, inline code, URLs and file paths blanked out (newlines kept).

    Slash terms such as `TCP/IP` look like paths but are kept."""
    for rx in (FENCED, INLINE_CODE, URL):
        text = rx.sub(_blank, text)
    return FILE_PATH.sub(lambda m: m.group(0) if SLASH.fullmatch(m.group(0)) else _blank(m), text)


def _borders_ok(line: str, start: int, end: int) -> bool:
    """True when a run has a non-ASCII character (or the line edge) on both sides, a single space allowed."""
    before = line[:start]
    if before.endswith(" "):
        before = before[:-1]
    after = line[end:]
    if after.startswith(" "):
        after = after[1:]
    return (before.strip() == "" or ord(before[-1]) > 127) and (after == "" or ord(after[0]) > 127)


def _has_non_ascii_letter(line: str) -> bool:
    return any(ord(c) > 127 and c.isalpha() for c in line)


def _outermost(spans: list[tuple[int, int, str]]) -> list[tuple[int, int, str]]:
    """Spans not properly contained in a longer span (a sub-term at the same place is not counted)."""
    spans = sorted(spans, key=lambda s: (s[0], -s[1]))
    kept, max_end, max_span = [], -1, None
    for s, e, t in spans:
        if max_span is not None and max_end >= e and max_span != (s, e):
            continue
        kept.append((s, e, t))
        if e > max_end:
            max_end, max_span = e, (s, e)
    return kept


def _line_terms(line: str) -> list[tuple[int, int, str]]:
    spans = [(m.start(), m.end(), m.group(0)) for rx in (SLASH, CAMEL, CAPS) for m in rx.finditer(line)]
    if _has_non_ascii_letter(line):                 # English-only lines give no run terms (§16.6)
        marker = LIST_MARKER.match(line)
        body = (" " * marker.end() + line[marker.end():]) if marker else line
        for m in ASCII_RUN.finditer(body):
            run = m.group(0)
            if 2 <= len(run.split(" ")) <= 4 and re.search("[A-Za-z]", run) \
                    and _borders_ok(body, m.start(), m.end()):
                spans.append((m.start(), m.end(), run))
    return _outermost(spans)


def find_terms(text: str) -> list[str]:
    """Technical terms in text, as first written, in order of first appearance (MANIFEST §15.6, §16.6)."""
    found: dict[str, tuple[int, str]] = {}
    offset = 0
    for line in _terms_text(text).split("\n"):
        for s, _, term in _line_terms(line):
            key = term.lower()
            if key not in found or offset + s < found[key][0]:
                found[key] = (offset + s, term)
        offset += len(line) + 1
    return [term for _, term in sorted(found.values())]


def _term_rx(term: str) -> re.Pattern:
    words = [re.escape(w) for w in term.split()]
    return re.compile(rf"(?<![{_AW}])" + r"\s+".join(words) + rf"(?![{_AW}])", re.I)


def _count_all(text: str, terms: list[str]) -> dict[str, int]:
    """Whole-word, case-insensitive counts; an occurrence inside a longer term's occurrence is not counted."""
    spans = [(m.start(), m.end(), t) for t in terms for m in _term_rx(t).finditer(text)]
    counts = dict.fromkeys(terms, 0)
    for _, _, t in _outermost(spans):
        counts[t] += 1
    return counts


def _count(text: str, term: str) -> int:
    return len(_term_rx(term).findall(text))


def _cjk_share(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if CJK.match(c)) / len(letters)


def _script(text: str) -> str:
    """The dominant script (CJK vs Latin). Technical-term tokens (CamelCase, acronyms, slash terms) are kept
    verbatim in translations, so they are left out: `RetryBudget已设置。` is a Chinese file."""
    for rx in (SLASH, CAMEL, CAPS):
        text = rx.sub(" ", text)
    return "cjk" if _cjk_share(text) > CJK_SHARE else "latin"


def _approved_zh() -> dict[str, list[str]]:
    """{lower-case en alternative: approved zh renderings} from the vendored glossary."""
    table: dict[str, list[str]] = {}
    try:
        lines = Path(tcheck.DEFAULT_GLOSSARY).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError, AttributeError):
        return table
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) < 6 or cols[0].strip() == "en" or cols[5].strip() != "approved":
            continue
        zh = [z.strip() for z in cols[1].split("|") if z.strip()]
        for en in cols[0].split("|"):
            key = " ".join(en.split()).lower()
            if key and zh:
                table.setdefault(key, [])
                table[key] += [z for z in zh if z not in table[key]]
    return table


def _finding(rule: str, severity: str, path: str, message: str, term: str) -> dict:
    return {"rule": rule, "severity": severity, "path": path.replace("\\", "/"), "line": None,
            "message": message, "excerpt": term}


@tool(
    "translate_terms",
    "Check that technical terms carry over between a source text and its translations: finds terms in src "
    "(CamelCase words, acronyms such as MCP, slash terms such as TCP/IP, runs of 2-4 English words set in "
    "Chinese text; code, URLs and file paths excluded), counts each in every file, and compares each target "
    "with the previous file (compare same-language: the nearest earlier file in the same script). L001 "
    "(warning): a term that disappeared. L002 (info): its count changed. L003 (info): gone, but a mostly "
    "Chinese target uses the glossary's approved rendering (glossary false turns this off).",
    {"type": "object",
     "properties": {
         "src": {"type": "string", "description": "source file"},
         "targets": {"type": "array", "items": {"type": "string"}, "minItems": 1,
                     "description": "translated files, compared in order"},
         "glossary": {"type": "boolean",
                      "description": "downgrade L001 to L003 when an approved zh rendering is used (default true)"},
         "compare": {"type": "string", "enum": list(COMPARES),
                     "description": "previous (default): each file against the one before it; same-language: "
                                    "against the nearest earlier file of the same script (CJK vs Latin)"},
     },
     "required": ["src", "targets"],
     "additionalProperties": False},
    readOnlyHint=True,
)
def translate_terms(src: str, targets: list[str], glossary: bool = True, compare: str = "previous") -> dict:
    if not targets:
        raise ToolError("give at least 1 target file")
    if compare not in COMPARES:
        raise ToolError(f"compare must be previous or same-language, got {compare!r}")
    paths = [src, *targets]
    texts = []
    for path in paths:
        p = Path(path)
        if not p.is_file():
            raise ToolError(f"file not found: {path}")
        try:
            raw = p.read_bytes().decode("utf-8", errors="replace").lstrip("﻿")
        except OSError as exc:
            raise ToolError(f"cannot read {path}: {exc}") from None
        texts.append(_terms_text(raw.replace("\r\n", "\n").replace("\r", "\n")))
    terms = find_terms(texts[0])
    per_file = [_count_all(text, terms) for text in texts]
    table = {t: [c[t] for c in per_file] for t in terms}
    scripts = [_script(text) for text in texts]
    renderings = _approved_zh() if glossary else {}

    findings = []
    for i in range(1, len(paths)):
        target = paths[i]
        if compare == "previous":
            prev = i - 1
        else:
            prev = next((k for k in range(i - 1, -1, -1) if scripts[k] == scripts[i]), None)
            if prev is None:
                continue
        previous = paths[prev]
        mostly_cjk = _cjk_share(texts[i]) > CJK_SHARE
        for term, counts in table.items():
            before, now = counts[prev], counts[i]
            if before > 0 and now == 0:
                used = None
                if mostly_cjk:
                    used = next((z for z in renderings.get(" ".join(term.split()).lower(), [])
                                 if z in texts[i]), None)
                if used is not None:
                    findings.append(_finding("L003", "info", target,
                                             f"'{term}' appears {before} time(s) in {previous} and not in "
                                             f"{target}: rendered as {used} (approved glossary rendering)", term))
                else:
                    findings.append(_finding("L001", "warning", target,
                                             f"'{term}' appears {before} time(s) in {previous} and not in "
                                             f"{target}", term))
            elif before != now and before and now:
                findings.append(_finding("L002", "info", target,
                                         f"'{term}' appears {before} time(s) in {previous} and {now} in {target}",
                                         term))
    findings.sort(key=lambda f: (f["path"], f["line"] or 0, f["rule"]))
    counts = {"error": 0, "warning": sum(f["severity"] == "warning" for f in findings),
              "info": sum(f["severity"] == "info" for f in findings)}
    return {"ok": True, "findings": findings, "counts": counts, "terms": table}


def _resources() -> list[str]:
    names = []
    for sub in RESOURCE_DIRS:
        folder = HERE / sub
        if folder.is_dir():
            names += [f"{sub}/{p.name}" for p in sorted(folder.iterdir()) if p.is_file()]
    return names


@tool(
    "translate_resources",
    "List or read the translation resources: the rules (data/RULES.md), the zh-en and en-zh trap lists, the "
    "failure modes, the glossary (data/glossary.tsv) and the translator and critic prompts (prompts/*.md). "
    "Without name, lists them; with name (as listed), returns the text.",
    {"type": "object",
     "properties": {"name": {"type": "string", "description": "a listed name, e.g. prompts/critic.md"}},
     "additionalProperties": False},
    readOnlyHint=True,
)
def translate_resources(name: str | None = None) -> dict:
    names = _resources()
    if name is None:
        return {"resources": names}
    if name not in names:
        raise ToolError(f"unknown resource {name!r}; available: {', '.join(names)}")
    try:
        text = (HERE / name).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ToolError(f"cannot read {name}: {exc}") from None
    return {"name": name, "text": text}


# ---------------------------------------------------------------------------------------------- CLI

def add_cli(groups) -> None:
    p = groups.add_parser("translate", help="zh<->en translation checks and resources")
    cmds = p.add_subparsers(dest="command", required=True)

    c = cmds.add_parser("check", help="run tcheck (encoding, spans, glossary, glossary-slice, all)")
    c.add_argument("mode", choices=MODES)
    c.add_argument("src")
    c.add_argument("tgt", nargs="?")
    c.add_argument("--dir", dest="direction", choices=DIRECTIONS, default="zh-en")
    c.add_argument("--domains", nargs="+")
    c.add_argument("--glossary")
    c.add_argument("--repair", metavar="OUT")
    common_flags(c)
    c.set_defaults(handler=_cli_check)

    c = cmds.add_parser("resources", help="list or print the rules, glossary and prompts")
    c.add_argument("--name")
    common_flags(c)
    c.set_defaults(handler=_cli_resources)

    c = cmds.add_parser("terms", help="check that technical terms carry over into translations")
    c.add_argument("src")
    c.add_argument("targets", nargs="+", metavar="TGT")
    c.add_argument("--no-glossary", dest="glossary", action="store_false",
                   help="never downgrade L001 to L003 for approved glossary renderings")
    c.add_argument("--compare", choices=COMPARES, default="previous",
                   help="compare each file with the previous one, or with the nearest earlier file in the same "
                        "script")
    common_flags(c, checker=True)
    c.set_defaults(handler=_cli_terms)


def _cli_terms(args) -> CliResult:
    return CliResult(translate_terms(args.src, args.targets, glossary=args.glossary, compare=args.compare))


def _cli_check(args) -> CliResult:
    r = translate_check(args.mode, args.src, tgt=args.tgt, direction=args.direction, domains=args.domains,
                        glossary=args.glossary, repair=args.repair)
    if r["errors"]:
        sys.stderr.write(r["errors"])
    return CliResult(r, r["output"], exit_code=r["exit_code"])


def _cli_resources(args) -> CliResult:
    r = translate_resources(args.name)
    return CliResult(r, r["text"] if args.name else "\n".join(r["resources"]))
