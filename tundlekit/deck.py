"""deck: presentations from a JSON spec (MANIFEST.md §3), after tundle's deckkit.py and checks/.

1 slide = stage-coloured eyebrow + takeaway title + a body that carries the point (bullets, lines, table,
figure, excerpt or chart) + source footer + slide number. Research slides add a DEMONSTRATED BY strip, design
slides a THUS strip, a phase's first slide an IN/OUT strip. Notes: TIME, SAY, IF ASKED.

Insert slides are optional slides numbered after the core slide they follow ("9a"); their notes open with an
INSERT line and their time is counted apart from the core time.

python-pptx and Pillow are imported inside the functions that need them; deck_lint on a spec needs neither.
"""
from __future__ import annotations

import json
import math
import pathlib
import re
import unicodedata

from tundlekit.palette import PPT, STAGE, tint
from tundlekit.registry import ToolError, tool

SLIDE_TYPES = ("title", "divider", "content")
BODY_KINDS = ("bullets", "lines", "table", "figure", "excerpt", "chart")
INSERT_MODES = ("shown", "hidden", "off")
DEFAULT_TARGET, DEFAULT_MAX, DEFAULT_WPS = "40:00", "45:00", 2.3
INSERT_LINE = "INSERT: optional slide; delete or hide it and the talk flows unchanged"

MAX_INSERTS = 26                    # letters a..z after 1 core slide

TIME_RE = re.compile(r"([0-9]{1,3}):([0-5][0-9])")
NUMBER_RE = re.compile(r"[0-9]+[a-z]?")
NOTES_TIME_RE = re.compile(r"^TIME[ \t]+([0-9]{1,3}):([0-9][0-9])(?![0-9])", re.M)
NOTES_SAY_RE = re.compile(r"^SAY:(.*?)(?=^IF ASKED:|^MUST HIT:|\Z)", re.M | re.S)


# ------------------------------------------------------------------ small helpers
def mmss(seconds: int) -> str:
    return f"{seconds // 60}:{seconds % 60:02d}"


def parse_time(text) -> int | None:
    """M:SS -> seconds, or None when the text is not in that format."""
    m = TIME_RE.fullmatch(text) if isinstance(text, str) else None
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None


def budget_status(seconds: int, target: int, maximum: int) -> str:
    if seconds > maximum:
        return "OVER BUDGET"
    if seconds > target:
        return "over target"
    return "ok"


def _is_num(v) -> bool:
    """A JSON number (not a bool) that converts to a finite float; 10**400 does not."""
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return False
    try:
        return math.isfinite(float(v))
    except OverflowError:
        return False


def _short(value) -> str:
    """A bounded repr for problem messages (never fails, even for huge ints)."""
    try:
        text = repr(value)
    except ValueError:
        text = f"<{type(value).__name__}>"
    return text if len(text) <= 40 else text[:37] + "..."


def bad_chars(text: str) -> bool:
    """Control characters other than newline and tab (and lone surrogates) can't be written to PPTX or SVG."""
    return any((unicodedata.category(ch) in ("Cc", "Cs") and ch not in "\n\t") or ch in "￾￿"
               for ch in text)


def _check_text(value, where: str, problems: list, required: bool = False) -> None:
    if value is None and not required:
        return
    if not isinstance(value, str):
        problems.append(f"{where}: must be a string")
    elif bad_chars(value):
        problems.append(f"{where}: contains a control character")


def _is_file(path: pathlib.Path) -> bool:
    try:
        return path.is_file()
    except (OSError, ValueError):
        return False


def _words(text: str) -> int:
    return len(text.split())


def _display(path) -> str:
    return str(path).replace("\\", "/")


def _require_office(pillow: bool = True):
    try:
        import pptx  # noqa: F401
    except ImportError:
        raise ToolError("python-pptx is not installed (pip install python-pptx, or tundlekit[office])") from None
    if pillow:
        try:
            import PIL  # noqa: F401
        except ImportError:
            raise ToolError("Pillow is not installed (pip install Pillow, or tundlekit[office])") from None


# ------------------------------------------------------------------ spec loading and validation (§3.1)
def read_json(path: pathlib.Path, what: str):
    """Parse a JSON file (a UTF-8 BOM is allowed); any failure is a ToolError."""
    try:
        text = path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise ToolError(f"{what} not found: {path}") from None
    except (OSError, ValueError) as e:
        raise ToolError(f"cannot read {what} {path}: {e}") from None
    try:
        return json.loads(text)
    except (ValueError, RecursionError) as e:
        raise ToolError(f"{what} {path} is not valid JSON: {e}") from None


def load_spec(spec, spec_path) -> tuple[dict, pathlib.Path, str]:
    """Return (spec, base directory for relative paths, display path for findings)."""
    if (spec is None) == (spec_path is None):
        raise ToolError("give exactly 1 of spec or spec_path")
    if spec_path is None:
        base, shown = pathlib.Path.cwd(), "<spec>"
    else:
        p = pathlib.Path(spec_path)
        spec = read_json(p, "spec file")
        base, shown = p.resolve().parent, _display(spec_path)
    if not isinstance(spec, dict):
        raise ToolError("spec: must be a JSON object")
    return spec, base, shown


def _resolve(base: pathlib.Path, path: str) -> pathlib.Path:
    p = pathlib.Path(path)
    return p if p.is_absolute() else base / p


def _is_image(path: pathlib.Path) -> bool:
    try:
        with open(path, "rb") as f:
            head = f.read(8)
    except OSError:
        return False
    return head.startswith(b"\x89PNG\r\n\x1a\n") or head.startswith(b"\xff\xd8\xff")


class Plan:
    """A validated spec with every slide's number, timing and text worked out."""

    def __init__(self, spec: dict, base: pathlib.Path, shown: str):
        self.spec, self.base, self.shown = spec, base, shown
        problems: list[str] = []
        self.meta = self._meta(spec.get("meta", {}), problems)
        slides = spec.get("slides")
        if not isinstance(slides, list) or not slides:
            problems.append("slides: must be a non-empty list")
            slides = []
        self.slides = []
        seen_core, run = False, 0
        for i, s in enumerate(slides):
            where = f"slides[{i}]"
            if not isinstance(s, dict):
                problems.append(f"{where}: must be an object")
                continue
            sl = self._slide(s, where, seen_core, problems)
            self.slides.append(sl)
            if sl["insert"]:
                run += 1
                if run == MAX_INSERTS + 1:
                    problems.append(f"{where}.insert: more than {MAX_INSERTS} insert slides after 1 core slide")
            else:
                seen_core, run = True, 0
        if problems:
            raise ToolError("invalid deck spec:\n" + "\n".join(f"- {p}" for p in problems))
        self._number()

    # ------------------------------------------------------------ meta
    def _meta(self, meta, problems) -> dict:
        if not isinstance(meta, dict):
            problems.append("meta: must be an object")
            meta = {}
        out = {"id": meta.get("id"), "title": meta.get("title"), "logo": None,
               "inserts": meta.get("inserts", "shown"), "words_per_second": meta.get("words_per_second", DEFAULT_WPS)}
        if out["id"] is not None and (not isinstance(out["id"], str) or not out["id"] or bad_chars(out["id"])):
            problems.append("meta.id: must be a non-empty string without control characters")
        _check_text(out["title"], "meta.title", problems)
        if not isinstance(out["inserts"], str) or out["inserts"] not in INSERT_MODES:
            problems.append(f"meta.inserts: must be one of shown, hidden, off, not {_short(out['inserts'])}")
        if not _is_num(out["words_per_second"]) or out["words_per_second"] <= 0:
            problems.append("meta.words_per_second: must be a positive finite number")
        logo = meta.get("logo")
        if logo is not None:
            if not isinstance(logo, str) or not logo:
                problems.append("meta.logo: must be a path string")
            else:
                p = _resolve(self.base, logo)
                out["logo"] = p if _is_file(p) else None      # a missing logo is ignored (§3.1a)
        budget = meta.get("budget", {})
        if not isinstance(budget, dict):
            problems.append("meta.budget: must be an object")
            budget = {}
        for key, default in (("target", DEFAULT_TARGET), ("max", DEFAULT_MAX)):
            value = budget.get(key, default)
            if parse_time(value) is None:
                problems.append(f"meta.budget.{key}: must be M:SS, not {_short(value)}")
                value = default
            out[key] = value
        return out

    # ------------------------------------------------------------ slides
    def _slide(self, s: dict, where: str, seen_core: bool, problems: list) -> dict:
        kind = s.get("type", "content")
        if not isinstance(kind, str) or kind not in SLIDE_TYPES:
            problems.append(f"{where}.type: unknown slide type {_short(kind)} (one of title, divider, content)")
            kind = "content"
        title = s.get("title")
        if not isinstance(title, str) or not title.strip():
            problems.append(f"{where}.title: required non-empty string")
            title = ""
        else:
            _check_text(title, f"{where}.title", problems)
        for key in ("subtitle", "byline", "eyebrow", "source", "thus"):
            _check_text(s.get(key), f"{where}.{key}", problems)
        stage = s.get("stage")
        if stage is not None and (not isinstance(stage, str) or stage not in STAGE):
            problems.append(f"{where}.stage: unknown stage {_short(stage)} (one of {', '.join(STAGE)})")
        insert = s.get("insert", False)
        if not isinstance(insert, bool):
            problems.append(f"{where}.insert: must be true or false")
            insert = False
        if insert and kind != "content":
            problems.append(f"{where}.insert: only content slides can be insert slides")
            insert = False
        elif insert and not seen_core:
            problems.append(f"{where}.insert: an insert slide must follow at least 1 core slide")
        demo = s.get("demonstrated_by")
        if demo is not None:
            if not isinstance(demo, dict):
                problems.append(f"{where}.demonstrated_by: must be an object with string paper and setup")
            else:
                _check_text(demo.get("paper"), f"{where}.demonstrated_by.paper", problems, required=True)
                _check_text(demo.get("setup"), f"{where}.demonstrated_by.setup", problems)
        phase = s.get("phase")
        if phase is not None:
            if not isinstance(phase, dict):
                problems.append(f"{where}.phase: must be an object with string in and out")
            else:
                _check_text(phase.get("in"), f"{where}.phase.in", problems, required=True)
                _check_text(phase.get("out"), f"{where}.phase.out", problems, required=True)
        body = s.get("body")
        if body is not None:
            self._body(body, f"{where}.body", problems)
        seconds, say, asked = self._notes(s.get("notes"), f"{where}.notes", problems)
        if not asked and s.get("asked") is not None:      # tolerated: asked beside notes instead of inside
            asked = self._asked(s["asked"], f"{where}.asked", problems)
        return {"spec": s, "type": kind, "title": title,
                "insert": insert, "seconds": seconds, "say": say, "asked": asked}

    def _body(self, body, where: str, problems: list) -> None:
        if not isinstance(body, dict):
            problems.append(f"{where}: must be an object")
            return
        kind = body.get("kind")
        if not isinstance(kind, str) or kind not in BODY_KINDS:
            problems.append(f"{where}.kind: unknown body kind {_short(kind)} (one of {', '.join(BODY_KINDS)})")
            return
        if kind in ("bullets", "lines"):
            self._texts(body.get("items"), f"{where}.items", problems)
            if kind == "lines" and not isinstance(body.get("mono", False), bool):
                problems.append(f"{where}.mono: must be true or false")
        elif kind == "table":
            rows = body.get("rows")
            if not isinstance(rows, list) or not rows or not all(isinstance(r, list) and r for r in rows):
                problems.append(f"{where}.rows: must be a non-empty list of non-empty rows")
                return
            if len({len(r) for r in rows}) != 1:
                problems.append(f"{where}.rows: rows have different lengths "
                                f"({', '.join(str(len(r)) for r in rows)})")
            for i, row in enumerate(rows):
                for j, cell in enumerate(row):
                    cw = f"{where}.rows[{i}][{j}]"
                    if isinstance(cell, str):
                        _check_text(cell, cw, problems)
                    elif cell is not None and not isinstance(cell, bool) and not _is_num(cell):
                        problems.append(f"{cw}: must be a string, a finite number, a boolean or null")
            widths = body.get("widths")
            if widths is not None:
                if not isinstance(widths, list) or not all(_is_num(w) and w > 0 for w in widths):
                    problems.append(f"{where}.widths: must be a list of positive numbers")
                elif len(widths) != len(rows[0]):
                    problems.append(f"{where}.widths: {len(widths)} widths for {len(rows[0])} columns")
        elif kind == "figure":
            path = body.get("path")
            if not isinstance(path, str) or not path:
                problems.append(f"{where}.path: required path to a PNG or JPEG file")
                return
            p = _resolve(self.base, path)
            if not _is_file(p):
                problems.append(f"{where}.path: figure file not found: {path}")
            elif not _is_image(p):
                problems.append(f"{where}.path: not a PNG or JPEG file: {path}")
        elif kind == "excerpt":
            _check_text(body.get("text"), f"{where}.text", problems, required=True)
            _check_text(body.get("caption"), f"{where}.caption", problems)
        elif kind == "chart":
            cats, vals = body.get("categories"), body.get("values")
            ok = self._texts(cats, f"{where}.categories", problems, non_empty=True)
            if not isinstance(vals, list) or not all(_is_num(v) for v in vals):
                problems.append(f"{where}.values: must be a list of finite numbers")
                ok = False
            if ok and len(cats) != len(vals):
                problems.append(f"{where}.values: {len(vals)} values for {len(cats)} categories")
            hl = body.get("highlight")
            if hl is not None and ok:
                if isinstance(hl, bool) or not isinstance(hl, (int, str)):
                    problems.append(f"{where}.highlight: must be a category index or name")
                elif isinstance(hl, int) and not 0 <= hl < len(cats):
                    problems.append(f"{where}.highlight: index {_short(hl)} is out of range")
                elif isinstance(hl, str) and hl not in cats:
                    problems.append(f"{where}.highlight: {_short(hl)} is not one of the categories")
            for key in ("unit", "takeaway"):
                _check_text(body.get(key), f"{where}.{key}", problems)

    @staticmethod
    def _texts(items, where: str, problems: list, non_empty: bool = False) -> bool:
        """A list of strings without control characters; returns whether it is usable."""
        if not isinstance(items, list) or not all(isinstance(t, str) for t in items) or (non_empty and not items):
            problems.append(f"{where}: must be a {'non-empty ' if non_empty else ''}list of strings")
            return False
        for i, t in enumerate(items):
            _check_text(t, f"{where}[{i}]", problems)
        return True

    def _notes(self, notes, where: str, problems: list):
        if not isinstance(notes, dict):
            problems.append(f"{where}: required object with a time")
            return 0, "", []
        time = notes.get("time")
        seconds = parse_time(time)
        if time is None:
            problems.append(f"{where}.time: required (M:SS)")
        elif seconds is None:
            problems.append(f"{where}.time: must be M:SS (1-3 digit minutes, seconds 00-59), not {_short(time)}")
        say = notes.get("say") or ""
        if not isinstance(say, str):
            problems.append(f"{where}.say: must be a string")
            say = ""
        else:
            _check_text(say, f"{where}.say", problems)
        return seconds or 0, say, self._asked(notes.get("asked"), f"{where}.asked", problems)

    @classmethod
    def _asked(cls, asked, where: str, problems: list) -> list:
        asked = asked or []
        return asked if cls._texts(asked, where, problems) else []

    # ------------------------------------------------------------ derived values
    def _number(self) -> None:
        core, letter = 0, 0
        for pos, sl in enumerate(self.slides, 1):
            sl["position"] = pos
            if sl["insert"]:
                letter += 1
                sl["number"] = f"{core}{chr(96 + letter)}"
            else:
                core += 1
                letter = 0
                sl["number"] = str(core) if sl["type"] == "content" else None
            sl["label"] = sl["number"] or str(pos)
            sl["notes_text"] = notes_text(sl)
            sl["face"] = face_text(sl["spec"], sl["type"])

    @property
    def core_seconds(self) -> int:
        return sum(s["seconds"] for s in self.slides if not s["insert"])

    @property
    def insert_seconds(self) -> int:
        return sum(s["seconds"] for s in self.slides if s["insert"])


def notes_text(sl: dict) -> str:
    """The speaker notes of a slide in the §3.2 format."""
    parts = [INSERT_LINE] if sl["insert"] else []
    parts.append(f"TIME {sl['spec']['notes']['time']}")
    if sl["say"]:
        parts.append(f"SAY: {sl['say']}")
    if sl["asked"]:
        parts.append("IF ASKED:")
        parts.extend(f"- {a}" for a in sl["asked"])
    return "\n".join(parts)


def _strip_texts(s: dict) -> list[str]:
    out = []
    demo = s.get("demonstrated_by")
    if isinstance(demo, dict):
        out.append(f"DEMONSTRATED BY   {demo.get('paper', '')}  ·  {demo.get('setup', '')}")
    if isinstance(s.get("phase"), dict):
        out.append(f"IN   {s['phase'].get('in', '')}        OUT   {s['phase'].get('out', '')}")
    if s.get("thus"):
        out.append(f"THUS   {s['thus']}")
    return out


def face_text(s: dict, kind: str) -> str:
    """All text a spec slide shows (§3.3): title, eyebrow, subtitle, byline, body, strips, cells, takeaway."""
    out = [s.get("title") or ""]
    for key in ("eyebrow", "subtitle", "byline"):
        if s.get(key):
            out.append(s[key].upper() if key == "eyebrow" else s[key])
    if kind == "content":
        if s.get("source"):
            out.append(s["source"])
        out.extend(_strip_texts(s))
        body = s.get("body") or {}
        k = body.get("kind")
        if k in ("bullets", "lines"):
            out.extend(body.get("items", []))
        elif k == "table":
            out.extend(str(c) for r in body.get("rows", []) for c in r)
        elif k == "excerpt":
            out.append(body.get("text", ""))
            if body.get("caption"):
                out.append(body["caption"])
        elif k == "chart":
            out.extend(body.get("categories", []))
            if body.get("takeaway"):
                out.append(body["takeaway"])
    return "\n".join(t for t in out if t)


# ------------------------------------------------------------------ building (§3.2)
W, H = 13.333, 7.5
INK, INK2, MUTED, HAIRC, PALEC, CODEBG, GREYBAR = "000000", "404040", "767676", "BFBFBF", "EDEDED", "F4F4F4", "9A9A9A"
FONT, MONO = "Calibri", "Consolas"
LOGO_W = 0.42
BODY_X, BODY_W = 0.75, 11.8
FIG_W, FIG_H = 11.8, 5.3


class _Builder:
    """The deckkit slide kit, driven by a Plan instead of by build scripts."""

    def __init__(self, plan: Plan, inserts: str):
        from pptx import Presentation
        from pptx.util import Inches

        self.plan, self.inserts = plan, inserts
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Inches(W), Inches(H)
        self.blank = self.prs.slide_layouts[6]
        self.warnings: list[str] = []
        self.label = ""

    # ------------------------------------------------------------ primitives
    @staticmethod
    def rgb(h):
        from pptx.dml.color import RGBColor

        return RGBColor.from_string(h)

    def warn(self, text: str) -> None:
        self.warnings.append(f"slide {self.label}: {text}")

    def check_text(self, y, w, h, paras, spacing, body=True) -> None:
        """deckkit's overflow heuristic: warn when the estimated text height exceeds its box or the slide."""
        need = 0.0
        for text, size, mono in paras:
            cpl = max(1, int((w - 0.1) * 72 / (size * (0.6 if mono else 0.5))))
            lines = sum(max(1, math.ceil(len(seg) / cpl)) for seg in text.split("\n"))
            need += lines * size * 1.2 / 72 + size * spacing / 72
        if need > h + 0.08 or (body and y + need > H - 0.45):
            first = paras[0][0] if paras else ""
            self.warn(f"text needs {need:.2f} in, box {h:.2f} in: {first[:48]!r}")

    def tb(self, s, x, y, w, h, paras, align=None, anchor=None, spacing=0.35, body=True):
        """A text box; paras are (text, size, bold, colour[, font])."""
        from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
        from pptx.util import Inches, Pt

        t = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        f = t.text_frame
        f.word_wrap = True
        f.vertical_anchor = anchor if anchor is not None else MSO_ANCHOR.TOP
        f.margin_left = f.margin_right = Inches(0.04)
        f.margin_top = f.margin_bottom = Inches(0.02)
        for i, p in enumerate(paras):
            text, size, bold, color = p[:4]
            font = p[4] if len(p) > 4 else FONT
            para = f.paragraphs[0] if i == 0 else f.add_paragraph()
            para.alignment = align if align is not None else PP_ALIGN.LEFT
            para.space_after = Pt(size * spacing)
            r = para.add_run()
            r.text = text
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.color.rgb = self.rgb(color)
            r.font.name = font
        self.check_text(y, w, h, [(p[0], p[1], len(p) > 4 and p[4] == MONO) for p in paras], spacing, body)
        return t

    def rect(self, s, x, y, w, h, fill, line=None):
        from pptx.enum.shapes import MSO_SHAPE
        from pptx.util import Inches, Pt

        b = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        b.fill.solid()
        b.fill.fore_color.rgb = self.rgb(fill)
        if line:
            b.line.color.rgb = self.rgb(line)
            b.line.width = Pt(0.75)
        else:
            b.line.fill.background()
        b.shadow.inherit = False
        return b

    def logo(self, s, x=None, y=0.24, w=LOGO_W):
        from pptx.util import Inches

        path = self.plan.meta["logo"]
        if path is None:
            return None
        x = W - 0.6 - w if x is None else x
        try:
            return s.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(w))
        except Exception as e:  # an unreadable image is a user problem, not a crash
            raise ToolError(f"cannot use logo {path}: {e}") from None

    def strip(self, s, y, runs, colour, fill, h, text_len, size):
        """A full-width strip with a coloured left edge; runs are (text, bold, colour, size)."""
        from pptx.enum.text import MSO_ANCHOR
        from pptx.util import Inches, Pt

        b = self.rect(s, 0.75, y, W - 1.5, h, fill)
        self.rect(s, 0.75, y, 0.09, h, colour)
        f = b.text_frame
        f.word_wrap = True
        f.vertical_anchor = MSO_ANCHOR.MIDDLE
        f.margin_left = Inches(0.25)
        p = f.paragraphs[0]
        for text, bold, col, sz in runs:
            r = p.add_run()
            r.text = text
            r.font.size = Pt(sz)
            r.font.bold = bold
            r.font.color.rgb = self.rgb(col)
            r.font.name = FONT
        cpl = int((W - 1.9) * 72 / (size * 0.5))
        if text_len > cpl * max(1, round(h / 0.45)):
            self.warn(f"{runs[0][0].strip()} strip too long for 1 line ({text_len} chars)")
        return b

    # ------------------------------------------------------------ slides
    def build(self):
        for sl in self.plan.slides:
            if sl["insert"] and self.inserts == "off":
                continue
            self.label = sl["label"]
            s = self.prs.slides.add_slide(self.blank)
            if sl["type"] == "title":
                self.title_slide(s, sl["spec"])
            elif sl["type"] == "divider":
                self.divider(s, sl["spec"])
            else:
                self.content(s, sl)
            if sl["insert"] and self.inserts == "hidden":
                s._element.set("show", "0")
            s.notes_slide.notes_text_frame.text = sl["notes_text"]
        return self.prs

    def title_slide(self, s, spec):
        self.rect(s, 0.95, 2.4, 1.4, 0.08, INK)
        self.tb(s, 0.9, 2.65, 11.5, 1.0, [(spec["title"], 44, True, INK)])
        if spec.get("subtitle"):
            self.tb(s, 0.9, 3.75, 11.5, 1.5, [(spec["subtitle"], 24, False, INK2)])
        if spec.get("byline"):
            self.tb(s, 0.9, 5.9, 9, 0.5, [(spec["byline"], 16, False, MUTED)])
        self.logo(s, x=0.9, y=0.9, w=0.9)

    def divider(self, s, spec):
        self.rect(s, 0, 0, W, H, "141414")
        self.rect(s, 0.95, 2.55, 1.2, 0.06, "FFFFFF")
        self.tb(s, 0.9, 2.8, 11.5, 1.0, [(spec["title"], 40, True, "FFFFFF")])
        if spec.get("subtitle"):
            self.tb(s, 0.9, 3.8, 11.5, 0.9, [(spec["subtitle"], 24, False, "BDBDBD")])

    def content(self, s, sl):
        from pptx.enum.text import PP_ALIGN

        spec = sl["spec"]
        stage = spec.get("stage")
        col = PPT.get(stage, MUTED)
        if stage:
            self.rect(s, 0.6, 0.36, 0.22, 0.22, col)
        eyebrow = (spec.get("eyebrow") or "").upper()
        if eyebrow:
            self.tb(s, 0.9 if stage else 0.6, 0.3, 10.5, 0.35, [(eyebrow, 11, True, col)])
        self.tb(s, 0.58, 0.58, W - 1.2, 0.75, [(spec["title"], 30, True, INK)])
        self.rect(s, 0.6, 1.38, W - 1.2, 0.02 if stage else 0.012, col if stage else HAIRC)
        if spec.get("source"):
            self.tb(s, 0.6, 7.02, 11.2, 0.3, [(spec["source"], 10, False, MUTED)], body=False)
        self.logo(s)
        self.tb(s, W - 1.2, 7.02, 0.6, 0.3, [(sl["number"], 10, False, MUTED)], align=PP_ALIGN.RIGHT, body=False)

        top, bottom = 1.6, 6.9
        demo = spec.get("demonstrated_by")
        if demo:
            text = f"{demo['paper']}  ·  {demo.get('setup', '')}"
            self.strip(s, top - 0.08, [("DEMONSTRATED BY   ", True, "555555", 12), (text, False, INK, 15)],
                       "555555", "F2F2F2", 0.5, len("DEMONSTRATED BY") + 3 + len(text), 15)
            top += 0.58
        phase = spec.get("phase")
        if phase:
            edge = PPT[stage] if stage else PALEC
            runs = [("IN   ", True, MUTED, 12), (phase["in"], False, INK, 15),
                    ("        OUT   ", True, MUTED, 12), (phase["out"], False, INK, 15)]
            self.strip(s, top - 0.08, runs, edge, PALEC, 0.46, 19 + len(phase["in"]) + len(phase["out"]), 15)
            top += 0.54
        if spec.get("thus"):
            thus_col = PPT.get(stage, INK)
            fill = tint(thus_col, 0.12).lstrip("#").upper()
            self.strip(s, 6.38, [("THUS   ", True, thus_col, 12), (spec["thus"], False, INK, 17)],
                       thus_col, fill, 0.56, 7 + len(spec["thus"]), 17)
            bottom = 6.25
        body = spec.get("body")
        if body:
            self.body(s, body, top + 0.2, bottom, stage)

    # ------------------------------------------------------------ bodies
    def body(self, s, body, y, bottom, stage):
        h = bottom - y
        kind = body["kind"]
        if kind == "bullets":
            self.tb(s, BODY_X, y, BODY_W, h, [(f"•  {t}", 24, False, INK) for t in body["items"]], spacing=0.6)
        elif kind == "lines":
            font = MONO if body.get("mono") else FONT
            self.tb(s, BODY_X, y, BODY_W, h, [(t, 22, False, INK, font) for t in body["items"]], spacing=0.5)
        elif kind == "table":
            self.table(s, body["rows"], y, body.get("widths"))
        elif kind == "figure":
            self.figure(s, _resolve(self.plan.base, body["path"]), y - 0.2, bottom)
        elif kind == "excerpt":
            self.excerpt(s, body["text"], y, h - (0.45 if body.get("caption") else 0), body.get("caption"))
        elif kind == "chart":
            self.chart(s, body, y, h, stage)

    def table(self, s, rows, y, widths, x=BODY_X, w=BODY_W, size=17, head=15, row_h=0.62):
        from pptx.enum.text import MSO_ANCHOR
        from pptx.util import Inches, Pt

        nr, nc = len(rows), len(rows[0])
        shp = s.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(row_h * nr)).table
        tot = sum(widths) if widths else nc
        colw = [w * (widths[j] if widths else 1) / tot for j in range(nc)]
        for j in range(nc):
            shp.columns[j].width = Inches(colw[j])
        shp.first_row = True
        est = 0.0
        for i, row in enumerate(rows):
            shp.rows[i].height = Inches(row_h)
            row_need = row_h
            for j, cell in enumerate(row):
                c = shp.cell(i, j)
                c.fill.solid()
                c.fill.fore_color.rgb = self.rgb(PALEC if i == 0 else "FFFFFF")
                c.margin_left = c.margin_right = Inches(0.08)
                c.margin_top = c.margin_bottom = Inches(0.03)
                c.vertical_anchor = MSO_ANCHOR.MIDDLE
                tf = c.text_frame
                tf.word_wrap = True
                text = str(cell)
                r = tf.paragraphs[0].add_run()
                r.text = text
                sz = head if i == 0 else size
                r.font.size = Pt(sz)
                r.font.name = FONT
                r.font.bold = i == 0 or (j == 0 and nc > 1)
                r.font.color.rgb = self.rgb(INK)
                cpl = max(1, int((colw[j] - 0.16) * 72 / (sz * 0.5)))
                row_need = max(row_need, math.ceil(max(1, len(text)) / cpl) * sz * 1.2 / 72 + 0.12)
            est += row_need
        if y + est > H - 0.4:
            self.warn(f"table needs {est:.2f} in from y={y:.2f} and runs past the slide bottom")
        return shp

    def figure(self, s, path, y, bottom, x=BODY_X):
        from PIL import Image
        from pptx.util import Inches

        try:
            with Image.open(path) as im:
                iw, ih = im.size
        except Exception as e:
            raise ToolError(f"cannot read figure {path}: {e}") from None
        fw, fh = FIG_W, FIG_W * ih / iw
        if fh > FIG_H:
            fh, fw = FIG_H, FIG_H * iw / ih
        if y + fh > bottom + 0.05:
            self.warn(f"figure needs {fh:.2f} in from y={y:.2f} and runs past the body area")
        return s.shapes.add_picture(str(path), Inches(x + (FIG_W - fw) / 2), Inches(y),
                                    width=Inches(fw), height=Inches(fh))

    def excerpt(self, s, text, y, h, caption, x=BODY_X, w=BODY_W, size=15):
        from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
        from pptx.util import Inches, Pt

        box = self.rect(s, x, y, w, h, CODEBG, line=HAIRC)
        f = box.text_frame
        f.word_wrap = True
        f.vertical_anchor = MSO_ANCHOR.TOP
        f.margin_left = f.margin_right = Inches(0.18)
        f.margin_top = f.margin_bottom = Inches(0.12)
        lines = text.rstrip("\n").split("\n")
        for i, line in enumerate(lines):
            p = f.paragraphs[0] if i == 0 else f.add_paragraph()
            p.alignment = PP_ALIGN.LEFT
            p.space_after = Pt(0)
            p.font.name = MONO
            r = p.add_run()
            r.text = line
            r.font.size = Pt(size)
            r.font.name = MONO
            r.font.color.rgb = self.rgb(INK)
        self.check_text(y, w - 0.36, h - 0.2, [(line, size, True) for line in lines], 0.0)
        if caption:
            self.tb(s, x, y + h + 0.06, w, 0.35, [(caption, 12, False, MUTED)])
        return box

    def chart(self, s, body, y, h, stage):
        from pptx.chart.data import CategoryChartData
        from pptx.enum.chart import XL_CHART_TYPE
        from pptx.util import Inches, Pt

        cats, vals = body["categories"], body["values"]
        takeaway = body.get("takeaway")
        chart_h = h - (0.6 if takeaway else 0)
        data = CategoryChartData()
        data.categories = cats
        data.add_series("values", vals)
        gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(BODY_X), Inches(y), Inches(BODY_W),
                                Inches(chart_h), data)
        chart = gf.chart
        chart.has_legend = False
        chart.font.size = Pt(14)
        chart.font.name = FONT
        chart.category_axis.reverse_order = True     # first category on top, as in the spec
        chart.value_axis.has_major_gridlines = False
        chart.value_axis.visible = False
        plot = chart.plots[0]
        plot.gap_width = 60
        plot.has_data_labels = True
        labels = plot.data_labels
        labels.show_value = True
        decimals = 0 if all(float(v).is_integer() for v in vals) else 1
        unit = (body.get("unit") or "").replace('"', "")
        labels.number_format = ("0" if decimals == 0 else "0.0") + (f'"{unit}"' if unit else "")
        labels.number_format_is_linked = False
        hl = body.get("highlight")
        hi = cats.index(hl) if isinstance(hl, str) else hl
        colour = PPT[stage or "gates"]
        for i in range(len(vals)):
            fill = plot.series[0].points[i].format.fill
            fill.solid()
            fill.fore_color.rgb = self.rgb(colour if i == hi else GREYBAR)
        if takeaway:
            self.tb(s, BODY_X, y + chart_h + 0.1, BODY_W, 0.5, [(takeaway, 18, True, INK)])
        return gf


def _read_times(times_file: str) -> tuple[pathlib.Path, dict]:
    """Check a times ledger before anything is written: its directory must exist, and the file, when present,
    must be a JSON object of non-negative numbers."""
    try:
        path = pathlib.Path(times_file).resolve()
        parent_ok, exists = path.parent.is_dir(), path.exists()
    except (OSError, ValueError) as e:
        raise ToolError(f"invalid times file path {times_file!r}: {e}") from None
    if not parent_ok:
        raise ToolError(f"times file directory does not exist: {path.parent}")
    if not exists:
        return path, {}
    data = read_json(path, "times file")
    if not isinstance(data, dict) or not all(_is_num(v) and v >= 0 for v in data.values()):
        raise ToolError(f"times file {path} must be a JSON object of non-negative numbers")
    return path, data


@tool("deck_build",
      "Build a PowerPoint deck (.pptx, 13.333 x 7.5 in) from a JSON deck spec (spec object or spec_path). Slides "
      "are title, divider or content; content slides take an eyebrow, a takeaway title, a stage colour, a source "
      "footer, DEMONSTRATED BY / THUS / IN-OUT strips and a body (bullets, lines, table, figure, excerpt, chart). "
      "Every slide needs notes.time (M:SS); notes become TIME / SAY / IF ASKED. Insert slides (insert: true) are "
      "numbered after the core slide they follow (3a, 3b) and can be shown, hidden or left out (inserts). "
      "Returns slide numbers, core and insert times against the budget, overflow warnings, and, with "
      "times_file, a shared time ledger across decks (needs meta.id). Needs python-pptx and Pillow.",
      {"type": "object",
       "properties": {
           "spec": {"type": "object", "description": "the deck spec"},
           "spec_path": {"type": "string", "description": "path to a JSON deck spec"},
           "out": {"type": "string", "description": "output .pptx path (overwritten)"},
           "inserts": {"type": "string", "enum": list(INSERT_MODES),
                       "description": "overrides meta.inserts: shown, hidden or off"},
           "times_file": {"type": "string", "description": "JSON time ledger shared by several decks"}},
       "required": ["out"],
       "additionalProperties": False},
      readOnlyHint=False)
def deck_build(out: str, spec: dict | None = None, spec_path: str | None = None, inserts: str | None = None,
               times_file: str | None = None) -> dict:
    plan = Plan(*load_spec(spec, spec_path))
    mode = inserts or plan.meta["inserts"]
    if not isinstance(mode, str) or mode not in INSERT_MODES:
        raise ToolError(f"inserts must be one of shown, hidden, off, not {_short(mode)}")
    if times_file is not None and not plan.meta["id"]:
        raise ToolError("meta.id is required when times_file is given")
    try:
        out_path = pathlib.Path(out).resolve()
        parent_ok = out_path.parent.is_dir()
    except (OSError, ValueError) as e:
        raise ToolError(f"invalid output path {out!r}: {e}") from None
    if not parent_ok:
        raise ToolError(f"output directory does not exist: {out_path.parent}")
    tpath, times = _read_times(times_file) if times_file is not None else (None, None)
    _require_office()

    builder = _Builder(plan, mode)
    prs = builder.build()
    try:
        prs.save(str(out_path))
    except (OSError, ValueError) as e:
        raise ToolError(f"cannot write {out}: {e}") from None

    core, ins = plan.core_seconds, plan.insert_seconds
    target, maximum = parse_time(plan.meta["target"]), parse_time(plan.meta["max"])
    warnings = builder.warnings
    if core > maximum:
        warnings.append(f"slide all: core time {mmss(core)} is over the {plan.meta['max']} maximum")

    ledger = None
    if times_file is not None:
        deck_id = plan.meta["id"]
        times[deck_id] = core
        times[deck_id + "_inserts"] = 0 if mode == "off" else ins
        try:
            tpath.write_text(json.dumps(times, indent=1) + "\n", encoding="utf-8")
        except OSError as e:
            raise ToolError(f"cannot write times file {times_file}: {e}") from None
        decks = {k: v for k, v in times.items() if not k.endswith("_inserts")}
        combined = sum(decks.values())
        ledger = {"path": str(tpath), "decks": decks, "combined_seconds": combined,
                  "combined_time": mmss(int(combined)), "status": budget_status(combined, target, maximum)}
        if combined > maximum:
            warnings.append(f"slide all: decks in {tpath.name} together take {mmss(int(combined))}, "
                            f"over the {plan.meta['max']} maximum")

    return {
        "out": str(out_path),
        "core_slides": sum(1 for s in plan.slides if not s["insert"]),
        "insert_slides": sum(1 for s in plan.slides if s["insert"]),
        "inserts": mode,
        "core_seconds": core,
        "insert_seconds": ins,
        "core_time": mmss(core),
        "total_time": mmss(core if mode == "off" else core + ins),
        "budget": {"target": plan.meta["target"], "max": plan.meta["max"],
                   "status": budget_status(core, target, maximum)},
        "ledger": ledger,
        "warnings": warnings,
        "slides": [{"number": s["number"], "type": s["type"], "title": s["title"], "insert": s["insert"],
                    "seconds": s["seconds"], "say_words": _words(s["say"])} for s in plan.slides],
    }


# ------------------------------------------------------------------ reading a .pptx (§3.3, §3.4)
def _iter_shapes(shapes):
    from pptx.enum.shapes import MSO_SHAPE_TYPE

    for sh in shapes:
        if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from _iter_shapes(sh.shapes)
        else:
            yield sh


def _open_pptx(pptx_path: str):
    _require_office(pillow=False)
    from pptx import Presentation

    p = pathlib.Path(pptx_path)
    if not p.is_file():
        raise ToolError(f"file not found: {pptx_path}")
    try:
        return Presentation(str(p))
    except Exception as e:  # python-pptx raises assorted errors for files that are not decks
        raise ToolError(f"cannot open {pptx_path} as a .pptx: {e}") from None


def parse_notes(notes: str) -> tuple[int | None, str | None]:
    """(seconds or None, SAY text or None) from notes in the §3.2 format."""
    m = NOTES_TIME_RE.search(notes)
    seconds = int(m.group(1)) * 60 + int(m.group(2)) if m else None
    say = NOTES_SAY_RE.search(notes)
    return seconds, (say.group(1).strip() if say else None)


def read_slide(slide, index: int) -> dict:
    frames, cells = [], []
    best_size, title = -1, None
    for sh in _iter_shapes(slide.shapes):
        if getattr(sh, "has_text_frame", False) and sh.has_text_frame:
            tf = sh.text_frame
            frames.append(tf.text)
            for p in tf.paragraphs:
                for r in p.runs:
                    size = r.font.size or p.font.size or 0
                    if r.text.strip() and size > best_size:
                        best_size, title = size, tf.text
        if getattr(sh, "has_table", False) and sh.has_table:
            for row in sh.table.rows:
                cells.extend(c.text for c in row.cells)
    if title is None:
        title = next((t for t in frames if t.strip()), "")
    number = next((t.strip() for t in frames if NUMBER_RE.fullmatch(t.strip())), None)
    notes = slide.notes_slide.notes_text_frame.text if slide.has_notes_slide else ""
    notes = notes.replace("\r\n", "\n").replace("\r", "\n").replace("\x0b", "\n")
    seconds, say = parse_notes(notes)
    return {"index": index, "number": number, "title": title, "texts": frames + cells, "notes": notes,
            "seconds": seconds, "say_words": _words(say or ""), "insert": notes.startswith("INSERT:"),
            "hidden": slide._element.get("show") in ("0", "false"), "say": say or ""}


@tool("deck_inspect",
      "Read any .pptx and list its slides: 1-based index, slide number text (a text box that is just a number "
      "such as 3 or 3a), title (the text in the largest font), every text in shape order (table cells after), "
      "speaker notes, TIME seconds and SAY word count parsed from the notes, whether it is an insert slide "
      "(notes start with INSERT:) and whether it is hidden. Needs python-pptx.",
      {"type": "object",
       "properties": {"pptx_path": {"type": "string", "description": "path to the .pptx file"}},
       "required": ["pptx_path"],
       "additionalProperties": False},
      readOnlyHint=True)
def deck_inspect(pptx_path: str) -> dict:
    prs = _open_pptx(pptx_path)
    slides = []
    for i, slide in enumerate(prs.slides, 1):
        info = read_slide(slide, i)
        info.pop("say")
        slides.append(info)
    return {"path": str(pptx_path), "slides": slides}


# ------------------------------------------------------------------ linting (§3.3)
DEFENSIVE = ("i'm not going to", "i am not going to", "i'm not claiming", "i'll show", "i will show",
             "this talk will", "that's fine for")
BACKREF_RE = re.compile(r"(?i)\b(as we saw|as i said|as mentioned|next slide|coming up)\b")
INSERT_REF_RE = re.compile(r"(?i)\bslide\s+\d+[a-z]\b")
EQ_RE = re.compile(r"\bEq\.?\s*\d")


def _excerpt(text: str, start: int = 0, end: int | None = None) -> str:
    end = start if end is None else end
    a, b = max(0, start - 30), min(len(text), end + 30)
    return " ".join(text[a:b].split())[:80]


def _lint_records(records: list[dict], shown: str, wps: float, target: int, maximum: int,
                  is_spec: bool) -> list[dict]:
    findings = []

    def add(rule, severity, rec, message, excerpt=""):
        findings.append({"rule": rule, "severity": severity, "path": shown,
                         "line": rec["position"] if rec else None, "message": message, "excerpt": excerpt})

    for r in records:
        say, notes, face, title = r["say"], r["notes"], r["face"], r["title"]
        words = _words(say)
        if r["seconds"] is None:
            add("D012", "error", r, "slide has no TIME in its notes")
        elif words > r["seconds"] * wps + 1e-9:
            add("D001", "error", r, f"SAY is {words} words for {mmss(r['seconds'])} "
                                    f"(cap {int(r['seconds'] * wps)} at {wps:g} words/s)", _excerpt(say))
        if r["content"] and not r["insert"] and words < 20:
            add("D002", "warning", r, f"SAY is only {words} words on a content slide", _excerpt(say))
        if "—" in title:
            add("D003", "error", r, "title contains an em dash", _excerpt(title, title.index("—")))
        for phrase in ("MUST HIT", "The point of this slide"):
            if phrase in notes:
                i = notes.index(phrase)
                add("D004", "error", r, f"notes contain {phrase!r}", _excerpt(notes, i, i + len(phrase)))
        low = say.replace("’", "'").lower()
        for phrase in DEFENSIVE:
            if phrase in low:
                i = low.index(phrase)
                add("D005", "warning", r, f"SAY contains the meta or defensive line {phrase!r}",
                    _excerpt(say, i, i + len(phrase)))
                break
        if r["insert"]:
            for where, text in (("face text", face), ("SAY", say)):
                m = BACKREF_RE.search(text)
                if m:
                    add("D006", "error", r, f"insert slide refers to the flow in its {where}: {m.group(0)!r}",
                        _excerpt(text, m.start(), m.end()))
                    break
        else:
            for where, text in (("face text", face), ("SAY", say)):
                m = INSERT_REF_RE.search(text)
                if m:
                    add("D007", "error", r, f"core slide mentions an insert slide in its {where}: {m.group(0)!r}",
                        _excerpt(text, m.start(), m.end()))
                    break
        if is_spec and r["content"] and not r["source"]:
            add("D009", "warning", r, "content slide has no source footer")
        m = re.search(r"et al\.", face) or EQ_RE.search(face)
        if m:
            add("D010", "warning", r, f"face text contains {m.group(0)!r}", _excerpt(face, m.start(), m.end()))
        if len(title) > 90:
            add("D011", "warning", r, f"title is {len(title)} characters (over 90)", title[:80])

    core = sum(r["seconds"] or 0 for r in records if not r["insert"])
    if core > maximum:
        add("D008", "error", None, f"core time {mmss(core)} is over the {mmss(maximum)} maximum")
    elif core > target:
        add("D008", "warning", None, f"core time {mmss(core)} is over the {mmss(target)} target")
    return findings


def _time_arg(name: str, value, default: str) -> int:
    value = default if value is None else value
    seconds = parse_time(value)
    if seconds is None:
        raise ToolError(f"{name} must be M:SS, not {_short(value)}")
    return seconds


@tool("deck_lint",
      "Check a deck spec (spec or spec_path) or a built .pptx (pptx_path) against the speaker-note and slide "
      "rules: D001 SAY longer than TIME x words_per_second; D002 core content slide with under 20 SAY words; "
      "D003 em dash in a title; D004 MUST HIT or 'The point of this slide' in notes; D005 meta or defensive "
      "lines in SAY; D006 insert slide referring to the flow; D007 core slide mentioning an insert slide; D008 "
      "core time over target (warning) or max (error); D009 content slide without source; D010 'et al.' or "
      "'Eq. N' on the face; D011 title over 90 chars; D012 slide without TIME. A spec needs no optional "
      "packages; a .pptx needs python-pptx.",
      {"type": "object",
       "properties": {
           "spec": {"type": "object", "description": "the deck spec"},
           "spec_path": {"type": "string", "description": "path to a JSON deck spec"},
           "pptx_path": {"type": "string", "description": "path to a built .pptx"},
           "words_per_second": {"type": "number", "description": "speaking rate (default meta, else 2.3)"},
           "target": {"type": "string", "description": "target core time M:SS (default meta budget, else 40:00)"},
           "max": {"type": "string", "description": "maximum core time M:SS (default meta budget, else 45:00)"}},
       "additionalProperties": False},
      readOnlyHint=True)
def deck_lint(spec: dict | None = None, spec_path: str | None = None, pptx_path: str | None = None,
              words_per_second: float | None = None, target: str | None = None, max: str | None = None) -> dict:
    if sum(x is not None for x in (spec, spec_path, pptx_path)) != 1:
        raise ToolError("give exactly 1 of spec, spec_path or pptx_path")
    if words_per_second is not None and (not _is_num(words_per_second) or words_per_second <= 0):
        raise ToolError("words_per_second must be a positive number")

    if pptx_path is not None:
        prs = _open_pptx(pptx_path)
        shown = _display(pptx_path)
        wps = words_per_second or DEFAULT_WPS
        target_s = _time_arg("target", target, DEFAULT_TARGET)
        max_s = _time_arg("max", max, DEFAULT_MAX)
        records = []
        for i, slide in enumerate(prs.slides, 1):
            info = read_slide(slide, i)
            records.append({"position": i, "title": info["title"], "face": "\n".join(info["texts"]),
                            "say": info["say"], "notes": info["notes"], "seconds": info["seconds"],
                            "insert": info["insert"], "content": info["number"] is not None, "source": None})
        is_spec = False
    else:
        plan = Plan(*load_spec(spec, spec_path))
        shown = plan.shown
        wps = words_per_second or plan.meta["words_per_second"]
        target_s = _time_arg("target", target, plan.meta["target"])
        max_s = _time_arg("max", max, plan.meta["max"])
        records = [{"position": s["position"], "title": s["title"], "face": s["face"], "say": s["say"],
                    "notes": s["notes_text"], "seconds": s["seconds"], "insert": s["insert"],
                    "content": s["type"] == "content", "source": s["spec"].get("source")}
                   for s in plan.slides]
        is_spec = True

    findings = _lint_records(records, shown, wps, target_s, max_s, is_spec)
    findings.sort(key=lambda f: (f["path"], f["line"] or 0, f["rule"]))
    counts = {sev: sum(1 for f in findings if f["severity"] == sev) for sev in ("error", "warning", "info")}
    core = sum(r["seconds"] or 0 for r in records if not r["insert"])
    return {"ok": counts["error"] == 0, "findings": findings, "counts": counts,
            "core_seconds": core, "insert_seconds": sum(r["seconds"] or 0 for r in records if r["insert"]),
            "core_time": mmss(core), "slides": len(records)}


# ------------------------------------------------------------------ CLI
def add_cli(groups) -> None:
    from tundlekit.cli_support import common_flags

    p = groups.add_parser("deck", help="presentations from a JSON spec")
    cmds = p.add_subparsers(dest="command", required=True)

    c = cmds.add_parser("build", help="build a .pptx from a deck spec")
    c.add_argument("spec_path", help="deck spec (.json)")
    c.add_argument("-o", "--out", required=True, help="output .pptx")
    c.add_argument("--inserts", choices=INSERT_MODES, help="shown, hidden or off (overrides meta.inserts)")
    c.add_argument("--times-file", dest="times_file", help="JSON time ledger shared by several decks")
    common_flags(c)
    c.set_defaults(handler=_cli_build)

    c = cmds.add_parser("lint", help="check a deck spec or a built .pptx")
    c.add_argument("path", help="deck spec (.json) or deck (.pptx)")
    c.add_argument("--words-per-second", dest="words_per_second", type=float, help="speaking rate")
    c.add_argument("--target", help="target core time M:SS")
    c.add_argument("--max", help="maximum core time M:SS")
    common_flags(c, checker=True)
    c.set_defaults(handler=_cli_lint)

    c = cmds.add_parser("inspect", help="list the slides, texts and notes of a .pptx")
    c.add_argument("pptx_path", help="deck (.pptx)")
    common_flags(c)
    c.set_defaults(handler=_cli_inspect)


def _cli_build(args):
    from tundlekit.cli_support import CliResult

    r = deck_build(out=args.out, spec_path=args.spec_path, inserts=args.inserts, times_file=args.times_file)
    lines = [f"wrote {r['out']}: {r['core_slides']} core slides, planned {r['core_time']} "
             f"({r['budget']['status']}; target {r['budget']['target']}, max {r['budget']['max']})"]
    if r["insert_slides"]:
        lines.append(f"  {r['insert_slides']} insert slides ({r['inserts']}), together {r['total_time']}")
    if r["ledger"]:
        led = r["ledger"]
        lines.append(f"  ledger {led['path']}: combined {led['combined_time']} ({led['status']})")
    lines += [f"  WARN {w}" for w in r["warnings"]]
    return CliResult(r, text="\n".join(lines))


def _cli_lint(args):
    from tundlekit.cli_support import CliResult, format_findings

    kw = {"words_per_second": args.words_per_second, "target": args.target, "max": args.max}
    kw = {k: v for k, v in kw.items() if v is not None}
    if args.path.lower().endswith(".pptx"):
        r = deck_lint(pptx_path=args.path, **kw)
    else:
        r = deck_lint(spec_path=args.path, **kw)
    text = format_findings(r) + f"\n{r['slides']} slides, core time {r['core_time']}"
    return CliResult(r, text=text)


def _cli_inspect(args):
    from tundlekit.cli_support import CliResult

    r = deck_inspect(args.pptx_path)
    lines = []
    for s in r["slides"]:
        flags = " ".join(f for f, on in (("insert", s["insert"]), ("hidden", s["hidden"])) if on)
        time = mmss(s["seconds"]) if s["seconds"] is not None else "no TIME"
        lines.append(f"{s['index']:>3} [{s['number'] or '-'}] {s['title']!r} {time}, "
                     f"{s['say_words']} SAY words {flags}".rstrip())
    return CliResult(r, text="\n".join(lines))
