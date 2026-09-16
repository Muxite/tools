"""MANIFEST §14 usefulness fixes: deck_lint (§14.4).

Companion to the other tests/test_r3_usefulness_*.py files (helpers in helpers_usefulness.py).
"""
from __future__ import annotations

import hashlib  # noqa: F401
import json  # noqa: F401
import re  # noqa: F401
import sys
from pathlib import Path

import pytest  # noqa: F401

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_usefulness as h  # noqa: E402
from helpers_usefulness import gitenv  # noqa: E402,F401  (fixture)


# ===================================================================== from the deck_lint group

INSERT = "INSERT: optional slide; delete or hide it and the talk flows unchanged"


def lint_spec(spec, **kw):
    res = h.call("deck_lint", spec=spec, **kw)
    h.check_shape(res)
    return res


def lint_pptx(paths, **kw):
    res = h.call("deck_lint", pptx_path=paths, **kw)
    h.check_shape(res)
    return res


def times(tmp_path, data, name="deck-times.json"):
    return h.write(tmp_path / name, json.dumps(data))


def test_single_element_list_equals_string(tmp_path):
    """§14.4: a list with 1 path lints like the plain path."""
    p = h.make_deck(tmp_path / "d.pptx", [h.slide("A — B", 1, footer="src"), h.slide("C", 2)])
    a = lint_pptx(p.as_posix())
    b = lint_pptx([p.as_posix()])
    assert h.pairs(a) == h.pairs(b)
    assert a["ok"] == b["ok"] is False


def test_times_file_not_written(tmp_path):
    """§14.4: lint reads the ledger; it never rewrites it."""
    t = times(tmp_path, {"capsule": 10})
    before = t.read_bytes()
    p = h.make_deck(tmp_path / "capsule.pptx", [h.slide("C", 1, footer="s", time="0:40")])
    lint_pptx(str(p), times_file=str(t))
    assert t.read_bytes() == before


def test_d014_is_a_warning_only():
    """§14.4: D014 findings leave ok true."""
    res = lint_spec(h.deck_spec(h.content(say=h.SAY25 + " — aside")))
    assert res["ok"] is True
    assert res["counts"]["warning"] >= 1


def test_d009_divider_like_slide_not_checked(tmp_path):
    """§14.4: slides without a number frame are not content slides."""
    p = h.make_deck(tmp_path / "d.pptx", [
        {"frames": [("The evidence", 40, 2.8), ("What the papers show", 24, 3.8)], "notes": "TIME 0:05"},
    ])
    assert h.lines(lint_pptx(str(p)), "D009") == []


def test_d005_additions_in_pptx_notes(tmp_path):
    """§14.4: D005 additions apply to SAY parsed from .pptx notes."""
    p = h.make_deck(tmp_path / "d.pptx", [
        h.slide("A", 1, footer="s"),
        h.slide("B", 2, footer="s", say=h.SAY25 + " Instead I'll skip to the ledger."),
    ])
    assert h.lines(lint_pptx(str(p)), "D005") == [2]
