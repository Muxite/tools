"""Shared colour system (MANIFEST.md §6), after tundle's palette.py.

Colour = stage. Style = actor: a model call is a tinted fill with a MODEL tag, deterministic code is a white
fill with a stage-colour border and a CODE tag, a record is drawn as a document. Outcome colours are used only
for node states. Hues are Okabe-Ito based, and every figure keeps text labels, so nothing depends on colour alone.
"""
from __future__ import annotations

import re

from tundlekit.registry import tool

INK, GREY, HAIR, PALE = "#000000", "#4d4d4d", "#9a9a9a", "#ececec"

STAGE = {
    "intent": "#0072B2",      # compiled intent, requirement contract
    "binding": "#2A8FA8",     # plan and capsule binding
    "freeze": "#7B3FA0",      # freeze, and anything frozen or protected
    "dispatch": "#D98200",    # dispatch, operator execution
    "gates": "#008A63",       # gates, evaluation
    "claims": "#B8527F",      # claims, delivery
    "build": "#3D4FB0",       # capsule cold path: deciding and building
    "library": "#8C5A2B",     # capsule library, versions, lifecycle
    "external": "#6b6b6b",    # outside the system: papers, MCP servers, peers
}

OUTCOME = {
    "passed": "#008A63",
    "failed": "#D55E00",
    "skipped": "#bdbdbd",
    "running": "#D98200",
    "ready": "#0072B2",
    "pending": "#ffffff",
}

# the stage colours for python-pptx (no leading #, upper-case)
PPT = {k: v.lstrip("#").upper() for k, v in STAGE.items()}

RULES = [
    "Colour = stage: a shape's colour says which stage of the pipeline it belongs to (palette STAGE).",
    "Style = actor: a model call is a tinted fill with a MODEL tag, deterministic code is a white fill with a "
    "stage-colour border and a CODE tag, a record is drawn as a document, external parties are grey.",
    "1 box per model call: every box drawn as a model is exactly 1 model session.",
    "Show a legend whenever more than 1 actor appears in a figure.",
    "Nothing depends on colour alone: every shape also carries a text label or tag, so the figure reads in "
    "greyscale and for colour-blind readers.",
]

_HEX = re.compile(r"[0-9a-fA-F]{6}")


def tint(hexcolor: str, amount: float = 0.18) -> str:
    """Mix a colour with white; amount is the share of the colour kept. Returns lower-case #rrggbb."""
    h = hexcolor[1:] if isinstance(hexcolor, str) and hexcolor.startswith("#") else hexcolor
    if not isinstance(h, str) or not _HEX.fullmatch(h):
        raise ValueError(f"not a #rrggbb colour: {hexcolor!r}")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    mix = [round(255 - (255 - c) * amount) for c in (r, g, b)]
    return "#{:02x}{:02x}{:02x}".format(*mix)


@tool("palette_get",
      "Return the shared colour system used by tundlekit diagrams, charts and decks: stage colours (colour = "
      "stage), outcome colours, the ink/grey/hair/pale neutrals, and the drawing rules (style = actor, 1 box per "
      "model call, a legend when more than 1 actor is shown, nothing depends on colour alone).",
      {"type": "object", "properties": {}, "additionalProperties": False},
      readOnlyHint=True)
def palette_get() -> dict:
    return {"stage": dict(STAGE), "outcome": dict(OUTCOME), "ink": INK, "grey": GREY, "hair": HAIR,
            "pale": PALE, "rules": list(RULES)}


# ------------------------------------------------------------------ CLI
def add_cli(groups) -> None:
    from tundlekit.cli_support import common_flags

    p = groups.add_parser("palette", help="the shared colour system")
    cmds = p.add_subparsers(dest="command", required=True)
    c = cmds.add_parser("show", help="print stage and outcome colours and the drawing rules")
    common_flags(c)
    c.set_defaults(handler=_cli_show)


def _cli_show(args):
    from tundlekit.cli_support import CliResult

    res = palette_get()
    lines = ["stage:"]
    lines += [f"  {k:<9} {v}" for k, v in res["stage"].items()]
    lines.append("outcome:")
    lines += [f"  {k:<9} {v}" for k, v in res["outcome"].items()]
    lines.append(f"ink {INK}  grey {GREY}  hair {HAIR}  pale {PALE}")
    lines.append("rules:")
    lines += [f"  - {r}" for r in res["rules"]]
    return CliResult(res, text="\n".join(lines))
