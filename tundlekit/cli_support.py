"""Contract between tundlekit/cli.py and the modules that contribute command groups.

Each module in tundlekit.MODULES defines:

    def add_cli(groups) -> None:
        '''groups is the argparse sub-parsers object of the top-level parser.'''
        p = groups.add_parser("deck", help="...")
        cmds = p.add_subparsers(dest="command", required=True)
        c = cmds.add_parser("build", help="...")
        c.add_argument("spec_path")
        common_flags(c)                     # adds --json (and --strict when checker=True)
        c.set_defaults(handler=_cli_build)

    def _cli_build(args) -> CliResult: ...

cli.main parses argv, calls args.handler(args), and prints the result with emit(). A handler may raise
registry.ToolError; cli.main turns that into exit 1 as MANIFEST.md §0.4 says.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass


@dataclass
class CliResult:
    result: dict
    text: str | None = None        # human-readable output; None means format_default(result)
    exit_code: int | None = None   # None means: 1 if result["ok"] is False (or warnings under --strict), else 0


def common_flags(parser: argparse.ArgumentParser, checker: bool = False) -> None:
    parser.add_argument("--json", action="store_true", help="print the result as JSON")
    if checker:
        parser.add_argument("--strict", action="store_true", help="warnings also fail (exit 1)")


def format_findings(result: dict) -> str:
    """1 line per finding, then a summary line (MANIFEST.md §2.9 format, used by every checker)."""
    lines = [f"{f['path']}:{f['line'] or 0}: {f['rule']} {f['severity']}: {f['message']}"
             for f in result.get("findings", [])]
    c = result.get("counts", {})
    state = "ok" if result.get("ok") else "FAILED"
    lines.append(f"{state}: {c.get('error', 0)} error(s), {c.get('warning', 0)} warning(s), {c.get('info', 0)} info")
    return "\n".join(lines)


def format_default(result: dict) -> str:
    if "findings" in result and "counts" in result:
        return format_findings(result)
    return json.dumps(result, indent=2, ensure_ascii=False)


def exit_code_for(res: CliResult, strict: bool = False) -> int:
    if res.exit_code is not None:
        return res.exit_code
    r = res.result
    if r.get("ok") is False:
        return 1
    if strict and r.get("counts", {}).get("warning", 0):
        return 1
    return 0


def emit(res: CliResult, as_json: bool, strict: bool = False, out=None) -> int:
    """Print a handler's result and return the exit code."""
    import sys

    out = out or sys.stdout
    if as_json:
        out.write(json.dumps(res.result, indent=2, ensure_ascii=False) + "\n")
    else:
        text = res.text if res.text is not None else format_default(res.result)
        if text:
            out.write(text.rstrip("\n") + "\n")
    return exit_code_for(res, strict)
