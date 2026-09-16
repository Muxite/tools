"""`tundlekit-mcp`: the tundlekit tools over MCP, stdio transport (MANIFEST.md §0.5).

1 JSON-RPC 2.0 message per line on stdin/stdout (UTF-8). Stdout carries protocol messages only; logs go to
stderr. Standard library only.

    tundlekit-mcp [--root PATH]
    python -m tundlekit.mcp_server [--root PATH]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback

from tundlekit import __version__, registry
from tundlekit.registry import ToolError

LATEST = "2025-11-25"
SUPPORTED = (LATEST, "2025-06-18", "2025-03-26", "2024-11-05")

PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INVALID_PARAMS, INTERNAL_ERROR = (
    -32700, -32600, -32601, -32602, -32603)

INSTRUCTIONS = (
    "tundlekit: tools for keeping a tundle transfer bundle (bundle_*: status, release, compare, prune, init, "
    "lint, verify), building and checking decks (deck_*), SVG diagrams and charts (diagram_*, chart_bar, "
    "palette_get), checking report prose (text_*), rendering pages and contact sheets (render_*), reading arXiv "
    "papers (papers_*) and checking zh<->en translations (translate_*). Every tool returns JSON; checkers return "
    "{ok, findings, counts}. Paths are relative to the server's working directory. bundle_prune rewrites git "
    "history: run it without yes=true first (dry run)."
)


def log(message: str) -> None:
    try:
        print(f"tundlekit-mcp: {message}", file=sys.stderr, flush=True)
    except Exception:
        pass  # logging must never take the server down


class Server:
    def __init__(self, tools: dict, default_root: str | None = None):
        self.tools = tools
        self.default_root = default_root

    # ------------------------------------------------------------ dispatch

    def handle_line(self, line: str) -> dict | None:
        """The response to 1 input line, or None when there is nothing to answer."""
        try:
            msg = json.loads(line)
        except Exception as e:  # ValueError, RecursionError from deep nesting, MemoryError, ...
            return error_response(None, PARSE_ERROR, f"parse error: {type(e).__name__}")
        if not isinstance(msg, dict):
            return error_response(None, INVALID_REQUEST, "invalid request: expected a JSON object")
        method = msg.get("method")
        is_notification = "id" not in msg
        msg_id = msg.get("id")
        if not isinstance(method, str):
            return error_response(msg_id, INVALID_REQUEST, "invalid request: no method")
        if is_notification:
            return None  # notifications/initialized, notifications/cancelled, ...: nothing to do
        params = msg.get("params")
        if params is None:
            params = {}
        if not isinstance(params, dict):
            return error_response(msg_id, INVALID_PARAMS, "params must be an object")
        handler = self.METHODS.get(method)
        if handler is None:
            return error_response(msg_id, METHOD_NOT_FOUND, f"method not found: {method}")
        try:
            result = handler(self, params)
        except RpcError as e:
            return error_response(msg_id, e.code, e.message)
        except Exception as e:
            log(traceback.format_exc())
            return error_response(msg_id, INTERNAL_ERROR, f"internal error: {type(e).__name__}: {e}")
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}

    # ------------------------------------------------------------ methods

    def initialize(self, params: dict) -> dict:
        requested = params.get("protocolVersion")
        version = requested if requested in SUPPORTED else LATEST
        return {
            "protocolVersion": version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "tundlekit", "version": __version__},
            "instructions": INSTRUCTIONS,
        }

    def ping(self, params: dict) -> dict:
        return {}

    def tools_list(self, params: dict) -> dict:
        return {"tools": [t.listing() for t in self.tools.values()]}

    def tools_call(self, params: dict) -> dict:
        name = params.get("name")
        if not isinstance(name, str) or name not in self.tools:
            raise RpcError(INVALID_PARAMS, f"unknown tool: {name}")
        args = params.get("arguments")
        if args is None:
            args = {}
        if not isinstance(args, dict):
            return tool_error("invalid arguments: arguments must be an object")
        if (self.default_root is not None and name.startswith("bundle_") and "root" not in args
                and "root" in self.tools[name].input_schema.get("properties", {})):
            args = {**args, "root": self.default_root}
        try:
            result = registry.call(name, args)
            text = json.dumps(result, ensure_ascii=True)
        except ToolError as e:
            return tool_error(str(e))
        except Exception as e:
            log(f"{name} failed:\n{traceback.format_exc()}")
            return tool_error(f"internal error: {type(e).__name__}: {e}")
        return {"content": [{"type": "text", "text": text}], "structuredContent": result, "isError": False}

    METHODS = {
        "initialize": initialize,
        "ping": ping,
        "tools/list": tools_list,
        "tools/call": tools_call,
    }


class RpcError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def error_response(msg_id, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def tool_error(message: str) -> dict:
    return {"content": [{"type": "text", "text": message}], "isError": True}


def _safe_id(value):
    return value if isinstance(value, (str, int, float)) and not isinstance(value, bool) else None


def _request_id(line: str):
    """The id of a message that failed while being handled, or None."""
    try:
        msg = json.loads(line)
        return _safe_id(msg.get("id")) if isinstance(msg, dict) else None
    except Exception:
        return None


def _protocol_stream():
    """A binary stream for protocol messages; fd 1 is pointed at stderr so stray prints can't corrupt it."""
    sys.stdout.flush()
    try:
        fd = os.dup(sys.stdout.fileno())
        os.dup2(sys.stderr.fileno(), sys.stdout.fileno())
        out = open(fd, "wb", buffering=0)
    except (OSError, ValueError, AttributeError):
        return sys.stdout.buffer
    sys.stdout = sys.stderr
    return out


def load_tools() -> dict:
    from tundlekit import cli

    try:
        return cli.all_tools()
    except Exception as e:
        log(f"not every tool module loaded ({type(e).__name__}: {e}); serving the others")
        cli.import_modules()
        return cli.order_tools()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tundlekit-mcp", description="tundlekit tools over MCP (stdio).")
    parser.add_argument("--root", help="default tundle root for bundle tools (default: the working directory)")
    parser.add_argument("--version", action="version", version=f"tundlekit-mcp {__version__}")
    args = parser.parse_args(argv)
    root = os.path.abspath(args.root) if args.root is not None else None

    try:
        sys.stderr.reconfigure(errors="backslashreplace")  # lone surrogates in log text
    except (AttributeError, ValueError, OSError):
        pass
    stdin = sys.stdin.buffer
    out = _protocol_stream()
    server = Server(load_tools(), default_root=root)
    while True:
        try:
            raw = stdin.readline()
        except KeyboardInterrupt:
            break
        if not raw:
            break
        try:
            line = raw.decode("utf-8")
        except UnicodeDecodeError as e:
            response = error_response(None, PARSE_ERROR, f"parse error: input is not UTF-8 ({e})")
        else:
            if not line.strip():
                continue
            try:
                response = server.handle_line(line)
            except Exception as e:  # never exit on bad input (§13.3)
                log(traceback.format_exc())
                response = error_response(_request_id(line), INTERNAL_ERROR, f"internal error: {type(e).__name__}")
        if response is None:
            continue
        try:
            data = json.dumps(response, ensure_ascii=True)
        except Exception as e:
            data = json.dumps(error_response(_safe_id(response.get("id")), INTERNAL_ERROR,
                                             f"internal error: {type(e).__name__}"), ensure_ascii=True)
        out.write(data.encode("ascii") + b"\n")
        out.flush()
    return 0


def console() -> None:
    """Console-script entry point."""
    sys.exit(main())


if __name__ == "__main__":
    console()
