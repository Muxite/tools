"""Shared helpers for the round-4 claims / xref / coverage tests (MANIFEST §16.4, §16.5, with §15.1-§15.3).

Not a conftest. Import with `import helpers_r4c as r4`. Builds on helpers_r3rc (tool access, checker shape,
file and deck writers); nothing imports tundlekit at module level.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers_r3rc import (  # noqa: E402,F401
    assert_checker_shape, build_pptx, claims, content, crlf_only, lines, of, read, review, run_cli, sec,
    tool_error, write, write_paper, write_spec, xref,
)


def pages(*texts) -> list:
    """Page texts; `None` entries become filler pages without numbers."""
    return [t if t is not None else "Filler page without figures." for t in texts]


def trace(report_path, papers="papers", **kw) -> dict:
    """claims_trace with the checker shape asserted (§0.3)."""
    res = claims(report=str(report_path), papers=str(papers), **kw)
    assert_checker_shape(res)
    return res


def by_key(res: dict) -> dict:
    """{(path, line, number): claim} (§15.3 pinned: `number` is the token as written)."""
    return {(c["path"], c["line"], c["number"]): c for c in res["claims"]}


def numbers_at(res: dict, line: int, path: str | None = None) -> set:
    return {c["number"] for c in res["claims"] if c["line"] == line and (path is None or c["path"] == path)}


def is_weak(c: dict) -> bool:
    return c.get("weak") is True


def is_locator_match(c: dict) -> bool:
    return c.get("locator_match") is True


def run_xref(**kw) -> dict:
    res = xref(**kw)
    assert_checker_shape(res)
    return res


def run_review(**kw) -> dict:
    res = review(**kw)
    assert_checker_shape(res)
    return res


def lines_of(res: dict, rule: str) -> list:
    return sorted(f["line"] for f in of(res, rule))


def where(res: dict, rule: str) -> list:
    return [(f["path"], f["line"]) for f in of(res, rule)]
