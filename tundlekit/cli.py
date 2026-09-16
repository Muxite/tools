"""The `tundlekit` command line (MANIFEST.md §0.4).

    tundlekit --version
    tundlekit tools [--json]
    tundlekit call TOOL [--args JSON | --args-file PATH]
    tundlekit <group> <command> [args] [--json] [--strict]

Each module in tundlekit.MODULES contributes its group through add_cli(groups) (see cli_support.py).
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
import traceback

from tundlekit import MODULES, __version__, registry
from tundlekit.cli_support import CliResult, common_flags, emit, exit_code_for
from tundlekit.registry import ToolError

PROG = "tundlekit"


# ---------------------------------------------------------------- tool modules

def import_modules() -> dict:
    """Import every module in MODULES, skipping (with a stderr note) any that fails. Returns {name: module}."""
    loaded = {}
    for name in MODULES:
        try:
            loaded[name] = importlib.import_module(f"tundlekit.{name}")
        except Exception as e:  # a broken module must not take the other groups down
            print(f"{PROG}: skipping module {name}: {type(e).__name__}: {e}", file=sys.stderr)
    order_tools()
    return loaded


def _module_rank(t: registry.Tool) -> int:
    parts = (getattr(t.func, "__module__", "") or "").split(".")
    if len(parts) >= 2 and parts[0] == "tundlekit" and parts[1] in MODULES:
        return MODULES.index(parts[1])
    return len(MODULES)


def order_tools() -> dict:
    """Put registry.TOOLS in MODULES order, in place (§2.1a: listings follow MODULES order).

    Registration order depends on import order (a module may import another, or a caller may import a later
    module first); sorting by owning module, stable within a module, makes every listing deterministic.
    """
    tools = registry.TOOLS
    ordered = sorted(tools.values(), key=_module_rank)
    if list(tools.values()) != ordered:
        tools.clear()
        tools.update((t.name, t) for t in ordered)
    return tools


def all_tools() -> dict:
    """registry.load_all() (every module must import), in MODULES order."""
    registry.load_all()
    return order_tools()


# ---------------------------------------------------------------- stdio

def _utf8_stdio() -> None:
    """Write stdout as UTF-8 even on Windows consoles and pipes; never fail on stderr."""
    enc = (getattr(sys.stdout, "encoding", None) or "").lower().replace("-", "").replace("_", "")
    if enc != "utf8" and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(errors="backslashreplace")
        except (ValueError, OSError):
            pass


def _print_json(data: dict) -> None:
    sys.stdout.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- built-in commands

def _cli_tools(args) -> CliResult:
    try:
        tools = all_tools()
    except Exception as e:
        raise ToolError(f"cannot load every tool module: {type(e).__name__}: {e}") from None
    listing = [t.listing() for t in tools.values()]
    width = max((len(t["name"]) for t in listing), default=0)
    lines = []
    for t in listing:
        first = t["description"].strip().splitlines()[0] if t["description"].strip() else ""
        lines.append(f"{t['name']:<{width}}  {first}")
    return CliResult({"tools": listing}, "\n".join(lines))


class _UsageError(Exception):
    """A usage problem found after parsing: exit 2."""


def _cli_call(args) -> CliResult:
    tools = registry.TOOLS
    if args.tool not in tools:
        raise _UsageError(f"unknown tool: {args.tool} (see `{PROG} tools`)")
    if args.args_file is not None:
        try:
            with open(args.args_file, encoding="utf-8-sig") as f:
                text = f.read()
        except OSError as e:
            raise _UsageError(f"cannot read --args-file {args.args_file}: {e}") from None
    else:
        text = args.args if args.args is not None else "{}"
    try:
        tool_args = json.loads(text)
    except json.JSONDecodeError as e:
        raise _UsageError(f"--args is not valid JSON: {e}") from None
    if not isinstance(tool_args, dict):
        raise ToolError("invalid arguments: arguments must be a JSON object")
    return CliResult(registry.call(args.tool, tool_args))


# ---------------------------------------------------------------- parser and main

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=PROG, description="Agent-agnostic tools distilled from the tundle "
                                     "transfer bundle. Every command takes --json.")
    parser.add_argument("--version", action="store_true", help="print the version and exit")
    groups = parser.add_subparsers(dest="group", metavar="GROUP")

    p = groups.add_parser("tools", help="list every registered tool")
    common_flags(p)
    p.set_defaults(handler=_cli_tools)

    p = groups.add_parser("call", help="run any registered tool with JSON arguments; prints JSON")
    p.add_argument("tool", metavar="TOOL", help="tool name (see `tundlekit tools`)")
    src = p.add_mutually_exclusive_group()
    src.add_argument("--args", metavar="JSON", help="arguments as a JSON object")
    src.add_argument("--args-file", metavar="PATH", help="file holding the arguments as a JSON object")
    common_flags(p)
    p.set_defaults(handler=_cli_call, json=True, always_json=True)

    for name, module in import_modules().items():
        add_cli = getattr(module, "add_cli", None)
        if add_cli is None:
            continue
        try:
            add_cli(groups)
        except Exception as e:
            print(f"{PROG}: skipping CLI group of {name}: {type(e).__name__}: {e}", file=sys.stderr)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return the exit code. argparse usage errors raise SystemExit(2)."""
    _utf8_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.version:
        print(f"{PROG} {__version__}")
        return 0
    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_usage(sys.stderr)
        print(f"{PROG}: error: a command is required", file=sys.stderr)
        return 2

    as_json = bool(getattr(args, "json", False) or getattr(args, "always_json", False))
    strict = bool(getattr(args, "strict", False))
    try:
        res = handler(args)
    except _UsageError as e:
        print(f"{PROG}: {e}", file=sys.stderr)
        return 2
    except ToolError as e:
        message = str(e)
        print(f"{PROG}: {message}", file=sys.stderr)
        if as_json:
            _print_json({"error": message})
        return 1
    except Exception as e:
        traceback.print_exc()
        message = f"internal error: {type(e).__name__}: {e}"
        print(f"{PROG}: {message}", file=sys.stderr)
        if as_json:
            _print_json({"error": message})
        return 1
    if not isinstance(res, CliResult):
        res = CliResult(res)
    if getattr(args, "always_json", False):
        _print_json(res.result)
        return exit_code_for(res, strict)
    return emit(res, as_json, strict)


def console() -> None:
    """Console-script entry point."""
    sys.exit(main())


if __name__ == "__main__":
    console()
