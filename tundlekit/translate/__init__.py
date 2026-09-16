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
ASCII_RUN = re.compile(r"[A-Za-z0-9-]+(?: [A-Za-z0-9-]+)*")
FENCED = re.compile(r"^[ \t]*(`{3,}|~{3,})[^\n]*\n.*?^[ \t]*\1[ \t]*$", re.M | re.S)
INLINE_CODE = re.compile(r"(`+)(?!`).+?(?<!`)\1(?!`)", re.S)
URL = re.compile(r"(?:https?|ftp)://\S+|www\.\S+")
FILE_PATH = re.compile(r"[\w.~-]*[/\\][\w./\\~-]*|\b[\w-]+\.(?:py|md|json|jsonl|txt|tsv|csv|ya?ml|toml|js|ts|"
                       r"sh|ps1|bat|pptx|docx|xlsx|pdf|png|jpe?g|svg|html?|xml|ipynb|cfg|ini|log)\b")


def _terms_text(text: str) -> str:
    """Text with fenced code, inline code, URLs and file paths blanked out (newlines kept)."""
    for rx in (FENCED, INLINE_CODE, URL, FILE_PATH):
        text = rx.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    return text


def _borders_ok(line: str, start: int, end: int) -> bool:
    """True when a run has a non-ASCII character (or the line edge) on both sides, a single space allowed."""
    before = line[:start]
    if before.endswith(" "):
        before = before[:-1]
    after = line[end:]
    if after.startswith(" "):
        after = after[1:]
    return (before == "" or ord(before[-1]) > 127) and (after == "" or ord(after[0]) > 127)


def find_terms(text: str) -> list[str]:
    """Technical terms in text, as first written, in order of first appearance (MANIFEST §15.6)."""
    found: dict[str, tuple[int, str]] = {}

    def add(pos: int, term: str) -> None:
        key = term.lower()
        if key not in found or pos < found[key][0]:
            found[key] = (pos, term)

    offset = 0
    for line in _terms_text(text).split("\n"):
        for rx in (CAMEL, CAPS):
            for m in rx.finditer(line):
                add(offset + m.start(), m.group(0))
        for m in ASCII_RUN.finditer(line):
            run = m.group(0)
            if 2 <= len(run.split(" ")) <= 4 and re.search("[A-Za-z]", run) \
                    and _borders_ok(line, m.start(), m.end()):
                add(offset + m.start(), run)
        offset += len(line) + 1
    return [term for _, term in sorted(found.values())]


def _count(text: str, term: str) -> int:
    words = [re.escape(w) for w in term.split()]
    rx = re.compile(rf"(?<![{_AW}])" + r"\s+".join(words) + rf"(?![{_AW}])", re.I)
    return len(rx.findall(text))


@tool(
    "translate_terms",
    "Check that technical terms carry over between a source text and its translations: finds terms in src "
    "(CamelCase words, capitalised acronyms such as MCP, and runs of 2-4 English words set in Chinese text; "
    "code, URLs and file paths excluded), counts each in every file, and compares each target with the "
    "previous file. L001 (warning): a term that disappeared. L002 (info): a term whose count changed.",
    {"type": "object",
     "properties": {
         "src": {"type": "string", "description": "source file"},
         "targets": {"type": "array", "items": {"type": "string"}, "minItems": 1,
                     "description": "translated files, compared in order"},
     },
     "required": ["src", "targets"],
     "additionalProperties": False},
    readOnlyHint=True,
)
def translate_terms(src: str, targets: list[str]) -> dict:
    if not targets:
        raise ToolError("give at least 1 target file")
    texts = []
    for path in [src, *targets]:
        p = Path(path)
        if not p.is_file():
            raise ToolError(f"file not found: {path}")
        try:
            raw = p.read_bytes().decode("utf-8", errors="replace").lstrip("﻿")
        except OSError as exc:
            raise ToolError(f"cannot read {path}: {exc}") from None
        texts.append(_terms_text(raw.replace("\r\n", "\n").replace("\r", "\n")))
    terms = find_terms(texts[0])
    table = {t: [_count(text, t) for text in texts] for t in terms}
    findings = []
    for i, target in enumerate(targets, 1):
        shown = target.replace("\\", "/")
        previous = src if i == 1 else targets[i - 2]
        for term, counts in table.items():
            before, now = counts[i - 1], counts[i]
            if before > 0 and now == 0:
                findings.append({"rule": "L001", "severity": "warning", "path": shown, "line": None,
                                 "message": f"'{term}' appears {before} time(s) in {previous} and not in {target}",
                                 "excerpt": term})
            elif before != now and before and now:
                findings.append({"rule": "L002", "severity": "info", "path": shown, "line": None,
                                 "message": f"'{term}' appears {before} time(s) in {previous} and {now} in {target}",
                                 "excerpt": term})
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
    common_flags(c, checker=True)
    c.set_defaults(handler=_cli_terms)


def _cli_terms(args) -> CliResult:
    return CliResult(translate_terms(args.src, args.targets))


def _cli_check(args) -> CliResult:
    r = translate_check(args.mode, args.src, tgt=args.tgt, direction=args.direction, domains=args.domains,
                        glossary=args.glossary, repair=args.repair)
    if r["errors"]:
        sys.stderr.write(r["errors"])
    return CliResult(r, r["output"], exit_code=r["exit_code"])


def _cli_resources(args) -> CliResult:
    r = translate_resources(args.name)
    return CliResult(r, r["text"] if args.name else "\n".join(r["resources"]))
