"""chart: bar charts as SVG (MANIFEST.md §5). Standard library only.

The highlighted bar takes its stage colour, every other bar is grey, and every bar carries its value as text,
so the chart never depends on colour alone.
"""
from __future__ import annotations

import json
import math
import pathlib
import unicodedata
from xml.sax.saxutils import escape

from tundlekit.palette import HAIR, INK, GREY, OUTCOME, PALE, STAGE
from tundlekit.registry import ToolError, tool

FONT = "Calibri, Arial, Helvetica, sans-serif"
PAD = 24
CHAR_W = 7.2            # rough width of 1 character at 13 px
BAR_T = 26              # bar thickness
BAR_GAP = 14
PLOT_LONG = 480         # length of the value axis in px
TITLE_SIZE, LABEL_SIZE, TAKEAWAY_SIZE = 18, 13, 15
LINE_H = LABEL_SIZE + 3     # line pitch of multi-line category labels
TICK_GAP = 18               # room under a horizontal chart for the value axis tick labels (axis: true)


# ------------------------------------------------------------------ spec
def _finite(v) -> bool:
    """A JSON number (not a bool) that converts to a finite float; 10**400 does not."""
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return False
    try:
        return math.isfinite(float(v))
    except OverflowError:
        return False


def _bad_chars(text: str) -> bool:
    """Control characters other than newline and tab, lone surrogates and non-characters can't go into SVG."""
    return any((unicodedata.category(ch) in ("Cc", "Cs") and ch not in "\n\t") or ch in "￾￿"
               for ch in text)


def _check_text(value, where: str, problems: list, required: bool = False) -> None:
    if value is None and not required:
        return
    if not isinstance(value, str):
        problems.append(f"{where}: must be a string")
    elif _bad_chars(value):
        problems.append(f"{where}: contains a control character")


def _load(spec, spec_path) -> dict:
    if (spec is None) == (spec_path is None):
        raise ToolError("give exactly 1 of spec or spec_path")
    if spec_path is not None:
        p = pathlib.Path(spec_path)
        try:
            spec = json.loads(p.read_text(encoding="utf-8-sig"))
        except FileNotFoundError:
            raise ToolError(f"spec file not found: {spec_path}") from None
        except (OSError, UnicodeDecodeError) as e:
            raise ToolError(f"cannot read {spec_path}: {e}") from None
        except (ValueError, RecursionError) as e:
            raise ToolError(f"{spec_path} is not valid JSON: {e}") from None
    if not isinstance(spec, dict):
        raise ToolError("spec: must be a JSON object")
    return spec


def _validate(spec: dict) -> list[str]:
    problems = []
    cats, vals, ns = spec.get("categories"), spec.get("values"), spec.get("n")
    if not isinstance(cats, list) or not cats:
        problems.append("categories: must be a non-empty list of strings")
        cats = None
    else:
        for i, c in enumerate(cats):
            _check_text(c, f"categories[{i}]", problems, required=True)
    if not isinstance(vals, list):
        problems.append("values: must be a list of numbers")
        vals = None
    else:
        for i, v in enumerate(vals):
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                problems.append(f"values[{i}]: must be a number")
            elif not _finite(v):
                problems.append(f"values[{i}]: must be a finite number")
            elif v < 0:
                problems.append(f"values[{i}]: negative values are not supported")
    if cats is not None and vals is not None and len(cats) != len(vals):
        problems.append(f"values: {len(vals)} values for {len(cats)} categories")
    if ns is not None:
        if not isinstance(ns, list) or not all(isinstance(x, int) and _finite(x) for x in ns):
            problems.append("n: must be a list of integers")
        elif cats is not None and len(ns) != len(cats):
            problems.append(f"n: {len(ns)} entries for {len(cats)} categories")
    hl = spec.get("highlight")
    if hl is not None:
        if isinstance(hl, bool) or not isinstance(hl, (int, str)):
            problems.append("highlight: must be a category index or a category name")
        elif isinstance(hl, int) and cats is not None and not 0 <= hl < len(cats):
            problems.append(f"highlight: index {hl} is out of range (0..{len(cats) - 1})")
        elif isinstance(hl, str) and cats is not None and hl not in cats:
            problems.append(f"highlight: {hl!r} is not one of the categories")
    for key in ("title", "unit", "takeaway"):
        _check_text(spec.get(key), key, problems)
    orientation = spec.get("orientation", "horizontal")
    if not isinstance(orientation, str) or orientation not in ("horizontal", "vertical"):
        problems.append("orientation: must be horizontal or vertical")
    mx = spec.get("max")
    if mx is not None:
        if not _finite(mx):
            problems.append("max: must be a finite number")
        elif isinstance(vals, list) and any(_finite(v) and v > mx for v in vals):
            problems.append(f"max: {mx} is below the largest value")
        elif mx < 0:
            problems.append("max: must not be negative")
    dec = spec.get("decimals")
    if dec is not None and (not isinstance(dec, int) or isinstance(dec, bool) or not 0 <= dec <= 10):
        problems.append("decimals: must be an integer from 0 to 10")
    stage = spec.get("stage", "gates")
    if not isinstance(stage, str):
        problems.append("stage: must be a string")
    elif stage not in STAGE:
        problems.append(f"stage: unknown stage {stage!r} (one of {', '.join(STAGE)})")
    hc = spec.get("highlight_color")
    if hc is not None:
        if not isinstance(hc, str):
            problems.append("highlight_color: must be a string")
        elif hc not in STAGE and hc not in OUTCOME:
            problems.append(f"highlight_color: unknown colour key {hc!r} "
                            f"(a stage: {', '.join(STAGE)}; or an outcome: {', '.join(OUTCOME)})")
    if not isinstance(spec.get("axis", False), bool):
        problems.append("axis: must be true or false")
    return problems


# ------------------------------------------------------------------ SVG helpers
def _x(v: float) -> str:
    """A coordinate as short text."""
    v = round(v, 2)
    return str(int(v)) if v == int(v) else str(v)


def _attr(s) -> str:
    return escape(str(s), {'"': "&quot;", "\n": "&#10;", "\r": "&#13;", "\t": "&#9;"})


def _text(x, y, s, size=LABEL_SIZE, anchor="start", cls=None, fill=INK, bold=False) -> str:
    c = f' class="{cls}"' if cls else ""
    b = ' font-weight="bold"' if bold else ""
    return (f'<text{c} x="{_x(x)}" y="{_x(y)}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{b}>'
            f"{escape(s)}</text>")


def _lines_text(x, y, lines, anchor="start", cls=None) -> str:
    """A label of 1 or more lines: 1 line is plain text, several are <tspan> lines, the first at y."""
    if len(lines) == 1:
        return _text(x, y, lines[0], anchor=anchor, cls=cls)
    c = f' class="{cls}"' if cls else ""
    spans = "".join(f'<tspan x="{_x(x)}" y="{_x(y + k * LINE_H)}">{escape(line)}</tspan>'
                    for k, line in enumerate(lines))
    return (f'<text{c} x="{_x(x)}" y="{_x(y)}" font-size="{LABEL_SIZE}" text-anchor="{anchor}" '
            f'fill="{INK}">{spans}</text>')


def _textw(s: str, size=LABEL_SIZE) -> float:
    return max(len(line) for line in s.split("\n")) * CHAR_W * size / LABEL_SIZE


def _ticks(axis_max: float) -> list[tuple[float, str]]:
    """Round ticks from 0 up to axis_max (3 to 6 steps) as (fraction of axis_max, label without unit).

    Worked in decimal arithmetic, so any positive finite maximum works, from subnormal floats to 1.7e308
    (§16.1). Labels use fixed notation for ordinary magnitudes and scientific notation otherwise."""
    from decimal import Decimal, localcontext

    with localcontext() as ctx:
        ctx.prec = 40
        top = Decimal(axis_max)
        raw = top / 6
        mag = Decimal(1).scaleb(raw.adjusted())          # 10 ** floor(log10(raw))
        step = next(m * mag for m in (Decimal(1), Decimal(2), Decimal("2.5"), Decimal(5), Decimal(10))
                    if m * mag >= raw)
        count = int(top // step)
        ticks = [k * step for k in range(count + 1)]
        exps = [t.normalize().as_tuple().exponent for t in ticks if t]
        decimals = max([0] + [-e for e in exps])
        big = step * count >= Decimal("1e15")
        out = []
        for t in ticks:
            frac = float(t / top)
            if decimals <= 6 and not big:
                label = f"{t:.{decimals}f}"
            elif t == 0:
                label = "0"
            else:
                label = f"{t.normalize():.3e}".replace("E", "e")
                mant, _, exp = label.partition("e")
                mant = mant.rstrip("0").rstrip(".")
                label = f"{mant}e{int(exp)}"
            out.append((frac, label))
    return out


def _raw_value(v) -> str:
    return repr(float(v)) if isinstance(v, float) else str(v)


# ------------------------------------------------------------------ tool
@tool("chart_bar",
      "Draw a bar chart as SVG from a JSON spec (spec object or spec_path): categories, values (finite, >= 0), "
      "optional n per bar (label becomes 'name (n=N)'), highlight (index or category; drawn in the stage colour, "
      "the other bars grey), unit, decimals, takeaway (bold line under the chart), title, orientation "
      "(horizontal|vertical), max (axis maximum), stage (palette stage key, default gates), highlight_color "
      "(a stage or outcome key; overrides stage for the highlight), axis (true: value axis with gridlines and "
      "tick labels). A newline in a category splits its label into lines. Every bar carries a value label. "
      "Writes the SVG to out when given, else returns the SVG text. Returns the size and the "
      "length of every bar in px.",
      {"type": "object",
       "properties": {
           "spec": {"type": "object", "description": "the chart spec"},
           "spec_path": {"type": "string", "description": "path to a JSON chart spec"},
           "out": {"type": "string", "description": "optional .svg output path"}},
       "additionalProperties": False},
      readOnlyHint=False)
def chart_bar(spec: dict | None = None, spec_path: str | None = None, out: str | None = None) -> dict:
    spec = _load(spec, spec_path)
    problems = _validate(spec)
    if problems:
        raise ToolError("invalid chart spec:\n" + "\n".join(f"- {p}" for p in problems))
    out_path = None
    if out is not None:
        from tundlekit.render import check_path_string

        check_path_string(out, "out")
        try:
            out_path = pathlib.Path(out).resolve()
            parent_ok = out_path.parent.is_dir()
        except (OSError, ValueError) as e:
            raise ToolError(f"invalid output path {out!r}: {e}") from None
        if not parent_ok:
            raise ToolError(f"output directory does not exist: {out_path.parent}")

    svg, width, height, bars = _render(spec)
    result = {"path": None, "width": width, "height": height, "bars": bars}
    if out_path is None:
        result = {"svg": svg, **result}
    else:
        try:
            out_path.write_text(svg, encoding="utf-8")
        except (OSError, ValueError) as e:
            raise ToolError(f"cannot write {out}: {e}") from None
        result["path"] = str(out_path)
    return result


def _render(spec: dict):
    cats, vals = spec["categories"], spec["values"]
    ns = spec.get("n")
    unit = spec.get("unit") or ""
    title, takeaway = spec.get("title"), spec.get("takeaway")
    colour = STAGE[spec.get("stage", "gates")].lower()
    hc = spec.get("highlight_color")
    if hc is not None:                          # §14.6: overrides stage for the highlight
        colour = (STAGE.get(hc) or OUTCOME[hc]).lower()
    hl = spec.get("highlight")
    hi_index = cats.index(hl) if isinstance(hl, str) else hl

    axis_max = spec.get("max")
    if axis_max is None:
        axis_max = max(vals)
    if axis_max <= 0:
        axis_max = 1
    decimals = spec.get("decimals")
    if decimals is None:
        decimals = 0 if all(float(v).is_integer() for v in vals) else 1
    labels = [f"{c} (n={ns[i]})" if ns is not None else c for i, c in enumerate(cats)]
    value_texts = [f"{v:.{decimals}f}{unit}" for v in vals]

    axis = None
    if spec.get("axis"):
        axis = [(frac, label + unit) for frac, label in _ticks(axis_max)]
    layout = _vertical if spec.get("orientation", "horizontal") == "vertical" else _horizontal
    body, width, body_h, bars = layout(cats, labels, vals, value_texts, axis_max, hi_index, colour, axis)

    parts, y = [], PAD
    if title:
        width = max(width, _textw(title, TITLE_SIZE) + 2 * PAD)
        parts.append(_text(PAD, y + TITLE_SIZE, title, TITLE_SIZE, cls="heading", bold=True))
        y += TITLE_SIZE + 16
    parts.append(f'<g transform="translate(0,{_x(y)})">')
    parts.extend(body)
    parts.append("</g>")
    y += body_h
    if takeaway:
        width = max(width, _textw(takeaway, TAKEAWAY_SIZE) + 2 * PAD)
        y += 12
        parts.append(_text(PAD, y + TAKEAWAY_SIZE, takeaway, TAKEAWAY_SIZE, cls="takeaway", bold=True))
        y += TAKEAWAY_SIZE + 4
    width, height = math.ceil(width), math.ceil(y + PAD)

    head = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" font-family="{FONT}">']
    if title:
        head.append(f"<title>{escape(title)}</title>")
    head.append(f'<rect class="background" x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>')
    svg = "\n".join(head + parts + ["</svg>"]) + "\n"
    return svg, width, height, bars


def _bar(x, y, w, h, label, value, highlight, colour) -> str:
    cls = "bar highlight" if highlight else "bar"
    fill = colour if highlight else HAIR
    return (f'<rect class="{cls}" data-label="{_attr(label)}" data-value="{_attr(_raw_value(value))}" '
            f'x="{_x(x)}" y="{_x(y)}" width="{_x(w)}" height="{_x(h)}" fill="{fill}"/>')


def _axis_group(lines_and_labels) -> list[str]:
    """<g class="axis">: gridlines and tick labels, drawn before (under) the bars."""
    return ['<g class="axis">', *lines_and_labels, "</g>"]


def _horizontal(cats, labels, vals, value_texts, axis_max, hi_index, colour, axis=None):
    """Bars grow rightwards from a vertical axis; category labels sit left of it."""
    label_w = max(_textw(s) for s in labels)
    value_w = max(_textw(s) for s in value_texts)
    x0 = PAD + label_w + 10
    split = [s.split("\n") for s in labels]
    slot = max(BAR_T, max(len(lines) for lines in split) * LINE_H)
    parts, bars = [], []
    for i, v in enumerate(vals):
        y = i * (slot + BAR_GAP) + (slot - BAR_T) / 2
        length = round(v / axis_max * PLOT_LONG, 2)
        hi = i == hi_index
        mid = y + BAR_T / 2 + LABEL_SIZE * 0.35
        first = mid - (len(split[i]) - 1) * LINE_H / 2
        parts.append(_lines_text(x0 - 10, first, split[i], anchor="end", cls="category"))
        parts.append(_bar(x0, y, length, BAR_T, cats[i], v, hi, colour))
        parts.append(_text(x0 + length + 6, mid, value_texts[i], cls="value", bold=hi))
        bars.append({"label": cats[i], "value": v, "length": length, "highlight": hi})
    axis_h = len(vals) * (slot + BAR_GAP) - BAR_GAP
    parts.append(f'<line class="baseline" x1="{_x(x0)}" y1="-4" x2="{_x(x0)}" y2="{_x(axis_h + 4)}" '
                 f'stroke="{GREY}" stroke-width="1"/>')
    width = x0 + PLOT_LONG + 6 + value_w + PAD
    if axis:
        g = []
        for t, label in axis:
            x = x0 + t * PLOT_LONG
            g.append(f'<line class="grid" x1="{_x(x)}" y1="-4" x2="{_x(x)}" y2="{_x(axis_h + 4)}" '
                     f'stroke="{PALE}" stroke-width="1"/>')
            g.append(_text(x, axis_h + 6 + LABEL_SIZE, label, anchor="middle", cls="tick", fill=GREY))
        parts = _axis_group(g) + parts
        width = max(width, x0 + PLOT_LONG + _textw(axis[-1][1]) / 2 + PAD)
        axis_h += TICK_GAP
    return parts, width, axis_h, bars


def _vertical(cats, labels, vals, value_texts, axis_max, hi_index, colour, axis=None):
    """Bars grow upwards from a horizontal axis; category labels sit under each bar."""
    plot_h = PLOT_LONG * 0.6
    slot = max(BAR_T * 2.2, max(_textw(s) for s in labels + value_texts) + 12)
    top = LABEL_SIZE + 8                      # room for the value label above the tallest bar
    base = top + plot_h
    left = PAD + (max(_textw(label) for _, label in axis) + 8 if axis else 0)   # tick labels sit left
    split = [s.split("\n") for s in labels]
    parts, bars = [], []
    for i, v in enumerate(vals):
        cx = left + slot * i + slot / 2
        length = round(v / axis_max * plot_h, 2)
        hi = i == hi_index
        bw = min(slot - 12, BAR_T * 1.6)
        parts.append(_bar(cx - bw / 2, base - length, bw, length, cats[i], v, hi, colour))
        parts.append(_text(cx, base - length - 6, value_texts[i], anchor="middle", cls="value", bold=hi))
        parts.append(_lines_text(cx, base + LABEL_SIZE + 6, split[i], anchor="middle", cls="category"))
        bars.append({"label": cats[i], "value": v, "length": length, "highlight": hi})
    right = left + slot * len(vals)
    parts.append(f'<line class="baseline" x1="{_x(left)}" y1="{_x(base)}" x2="{_x(right)}" '
                 f'y2="{_x(base)}" stroke="{GREY}" stroke-width="1"/>')
    if axis:
        g = []
        for t, label in axis:
            y = base - t * plot_h
            g.append(f'<line class="grid" x1="{_x(left)}" y1="{_x(y)}" x2="{_x(right)}" y2="{_x(y)}" '
                     f'stroke="{PALE}" stroke-width="1"/>')
            g.append(_text(left - 6, y + LABEL_SIZE * 0.35, label, anchor="end", cls="tick", fill=GREY))
        parts = _axis_group(g) + parts
    height = base + LABEL_SIZE + 10 + (max(len(lines) for lines in split) - 1) * LINE_H
    return parts, right + PAD, height, bars


# ------------------------------------------------------------------ CLI
def add_cli(groups) -> None:
    from tundlekit.cli_support import common_flags

    p = groups.add_parser("chart", help="bar charts as SVG")
    cmds = p.add_subparsers(dest="command", required=True)
    c = cmds.add_parser("bar", help="draw a bar chart from a JSON spec")
    c.add_argument("spec_path", help="chart spec (.json)")
    c.add_argument("-o", "--out", help="output .svg (default: print the SVG)")
    common_flags(c)
    c.set_defaults(handler=_cli_bar)


def _cli_bar(args):
    from tundlekit.cli_support import CliResult

    r = chart_bar(spec_path=args.spec_path, out=args.out)
    text = r["svg"] if args.out is None else f"wrote {r['path']} ({r['width']} x {r['height']}, {len(r['bars'])} bars)"
    return CliResult(r, text=text)
