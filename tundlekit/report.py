"""Markdown report to .docx builder (MANIFEST.md §18.1).

Standard library only: the package is written with zipfile and XML strings, in the house style of the tundle
`build_report.py` (US Letter, Calibri 11 pt, 6.5 in figures, 9.5 pt tables and captions).
"""
from __future__ import annotations

import datetime as _dt
import os
import pathlib
import re
import struct
import subprocess
import zipfile
from dataclasses import dataclass, field
from xml.sax.saxutils import escape as _xml_escape

from tundlekit.registry import ToolError, tool

# ====================================================================== package parts (§18.1.2)
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC_NS = "http://schemas.openxmlformats.org/drawingml/2006/picture"
REL_BASE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
XML_HEAD = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

GREY = "595959"
BLACK = "000000"
FIGURE_EMU = 5943600                       # 6.5 in
TABLE_INCHES = 6.7
TWIPS = 1440

# paragraph style id -> run size in half-points (inline code runs are 1 pt smaller)
PARA_SIZE = {None: 22, "Heading1": 44, "Heading2": 32, "Heading3": 26, "ListBullet": 22, "ListBullet2": 22,
             "ListNumber": 22, "ListNumber2": 22, "Quote": 22, "Caption": 19, "Code": 18, "Figure": 22,
             "cell": 19}


def _style(sid: str, name: str, ppr: str = "", rpr: str = "", based: str | None = "Normal",
           extra: str = "") -> str:
    out = f'<w:style w:type="paragraph" w:styleId="{sid}"><w:name w:val="{name}"/>'
    if based:
        out += f'<w:basedOn w:val="{based}"/>'
    out += f'<w:next w:val="Normal"/>{extra}<w:qFormat/>'
    if ppr:
        out += f"<w:pPr>{ppr}</w:pPr>"
    if rpr:
        out += f"<w:rPr>{rpr}</w:rPr>"
    return out + "</w:style>"


def _fonts(name: str) -> str:
    return f'<w:rFonts w:ascii="{name}" w:hAnsi="{name}" w:eastAsia="{name}" w:cs="{name}"/>'


def _heading(level: int, size: int, before: int, after: int) -> str:
    return _style(f"Heading{level}", f"heading {level}",
                  ppr=f'<w:keepNext/><w:keepLines/><w:spacing w:before="{before}" w:after="{after}"/>'
                      f'<w:outlineLvl w:val="{level - 1}"/>',
                  rpr=f'{_fonts("Calibri")}<w:b/><w:bCs/><w:color w:val="{BLACK}"/>'
                      f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>')


def _styles_xml() -> str:
    normal = ('<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/>'
              '<w:pPr><w:spacing w:before="0" w:after="100" w:line="259" w:lineRule="auto"/></w:pPr>'
              f'<w:rPr>{_fonts("Calibri")}<w:color w:val="{BLACK}"/><w:sz w:val="22"/><w:szCs w:val="22"/>'
              '</w:rPr></w:style>')
    list_rpr = f'<w:color w:val="{BLACK}"/><w:sz w:val="22"/><w:szCs w:val="22"/>'
    styles = [
        normal,
        _heading(1, 44, 0, 120), _heading(2, 32, 320, 120), _heading(3, 26, 240, 80),
        _style("ListBullet", "List Bullet", rpr=list_rpr,
               ppr='<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'
                   '<w:spacing w:after="60"/><w:ind w:left="360" w:hanging="360"/>'),
        _style("ListBullet2", "List Bullet 2", rpr=list_rpr,
               ppr='<w:numPr><w:ilvl w:val="1"/><w:numId w:val="1"/></w:numPr>'
                   '<w:spacing w:after="60"/><w:ind w:left="720" w:hanging="360"/>'),
        _style("ListNumber", "List Number", rpr=list_rpr,
               ppr='<w:spacing w:after="60"/><w:ind w:left="720" w:hanging="360"/>'),
        _style("ListNumber2", "List Number 2", rpr=list_rpr,
               ppr='<w:spacing w:after="60"/><w:ind w:left="1080" w:hanging="360"/>'),
        _style("Quote", "Quote", ppr='<w:ind w:left="576" w:right="576"/>', rpr="<w:i/><w:iCs/>"),
        _style("Caption", "caption", ppr='<w:spacing w:before="40" w:after="160"/>',
               rpr=f'<w:i/><w:iCs/><w:color w:val="{GREY}"/><w:sz w:val="19"/><w:szCs w:val="19"/>'),
        _style("Code", "Code", ppr='<w:spacing w:before="80"/><w:ind w:left="432"/>',
               rpr=f'{_fonts("Consolas")}<w:color w:val="{BLACK}"/><w:sz w:val="18"/><w:szCs w:val="18"/>'),
        _style("Figure", "Figure", ppr='<w:keepNext/><w:spacing w:before="120" w:after="40"/><w:jc w:val="center"/>'),
        ('<w:style w:type="character" w:default="1" w:styleId="DefaultParagraphFont">'
         '<w:name w:val="Default Paragraph Font"/><w:uiPriority w:val="1"/><w:semiHidden/></w:style>'),
        ('<w:style w:type="table" w:default="1" w:styleId="TableNormal"><w:name w:val="Normal Table"/>'
         '<w:semiHidden/><w:tblPr><w:tblInd w:w="0" w:type="dxa"/><w:tblCellMar>'
         '<w:top w:w="0" w:type="dxa"/><w:left w:w="108" w:type="dxa"/><w:bottom w:w="0" w:type="dxa"/>'
         '<w:right w:w="108" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style>'),
        ('<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/>'
         '<w:basedOn w:val="TableNormal"/><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>'
         '<w:tblPr><w:tblBorders>'
         + "".join(f'<w:{b} w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
                   for b in ("top", "left", "bottom", "right", "insideH", "insideV"))
         + '</w:tblBorders></w:tblPr></w:style>'),
        ('<w:style w:type="paragraph" w:styleId="Footer"><w:name w:val="footer"/><w:basedOn w:val="Normal"/>'
         '<w:pPr><w:spacing w:after="0"/></w:pPr></w:style>'),
    ]
    defaults = ('<w:docDefaults><w:rPrDefault><w:rPr>' + _fonts("Calibri")
                + '<w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-US" w:eastAsia="en-US" w:bidi="ar-SA"/>'
                '</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="100" w:line="259" '
                'w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>')
    return (XML_HEAD + f'<w:styles xmlns:w="{W_NS}" xmlns:r="{R_NS}">' + defaults + "".join(styles)
            + "</w:styles>")


def _numbering_xml() -> str:
    glyphs = ["•", "o", "▪"]
    fonts = ["Symbol", "Courier New", "Wingdings"]
    levels = []
    for lvl in range(9):
        glyph = glyphs[lvl % 3]
        font = fonts[lvl % 3]
        left = 360 * (lvl + 1)
        # Symbol's bullet is at U+F0B7; write the plain bullet in Calibri-safe form instead
        rfonts = "" if lvl % 3 == 0 else f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:hint="default"/>'
        levels.append(f'<w:lvl w:ilvl="{lvl}"><w:start w:val="1"/><w:numFmt w:val="bullet"/>'
                      f'<w:lvlText w:val="{glyph}"/><w:lvlJc w:val="left"/>'
                      f'<w:pPr><w:ind w:left="{left}" w:hanging="360"/></w:pPr>'
                      f'<w:rPr>{rfonts}</w:rPr></w:lvl>')
    return (XML_HEAD + f'<w:numbering xmlns:w="{W_NS}" xmlns:r="{R_NS}">'
            '<w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="hybridMultilevel"/>'
            + "".join(levels) + '</w:abstractNum><w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>'
            '</w:numbering>')


def _footer_xml() -> str:
    rpr = f'<w:rPr><w:color w:val="{GREY}"/><w:sz w:val="19"/><w:szCs w:val="19"/></w:rPr>'
    return (XML_HEAD + f'<w:ftr xmlns:w="{W_NS}" xmlns:r="{R_NS}"><w:p><w:pPr><w:pStyle w:val="Footer"/>'
            f'<w:jc w:val="center"/></w:pPr>'
            f'<w:r>{rpr}<w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r>{rpr}<w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
            f'<w:r>{rpr}<w:fldChar w:fldCharType="separate"/></w:r>'
            f'<w:r>{rpr}<w:t>1</w:t></w:r>'
            f'<w:r>{rpr}<w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>')


def _settings_xml() -> str:
    return (XML_HEAD + f'<w:settings xmlns:w="{W_NS}" xmlns:r="{R_NS}">'
            '<w:defaultTabStop w:val="720"/><w:characterSpacingControl w:val="doNotCompress"/>'
            '<w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word"'
            ' w:val="15"/></w:compat></w:settings>')


def _content_types(image_exts: set[str]) -> str:
    wml = "application/vnd.openxmlformats-officedocument.wordprocessingml"
    defaults = ['<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
                '<Default Extension="xml" ContentType="application/xml"/>']
    for ext, mime in (("jpeg", "image/jpeg"), ("png", "image/png")):
        if ext in image_exts:
            defaults.append(f'<Default Extension="{ext}" ContentType="{mime}"/>')
    overrides = [("/word/document.xml", f"{wml}.document.main+xml"),
                 ("/word/styles.xml", f"{wml}.styles+xml"),
                 ("/word/settings.xml", f"{wml}.settings+xml"),
                 ("/word/numbering.xml", f"{wml}.numbering+xml"),
                 ("/word/footer1.xml", f"{wml}.footer+xml"),
                 ("/docProps/core.xml", "application/vnd.openxmlformats-package.core-properties+xml"),
                 ("/docProps/app.xml", "application/vnd.openxmlformats-officedocument.extended-properties+xml")]
    return (XML_HEAD + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            + "".join(defaults)
            + "".join(f'<Override PartName="{p}" ContentType="{t}"/>' for p, t in overrides) + "</Types>")


def _rels(items: list[tuple[str, str, str]]) -> str:
    return (XML_HEAD + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(f'<Relationship Id="{i}" Type="{t}" Target="{g}"/>' for i, t, g in items)
            + "</Relationships>")


def _package_rels() -> str:
    return _rels([("rId1", f"{REL_BASE}/officeDocument", "word/document.xml"),
                  ("rId2", "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties",
                   "docProps/core.xml"),
                  ("rId3", f"{REL_BASE}/extended-properties", "docProps/app.xml")])


def _core_xml(title: str, author: str, stamp: str) -> str:
    e = _xml_text
    return (XML_HEAD + '<cp:coreProperties '
            'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            f'<dc:title>{e(title)}</dc:title><dc:creator>{e(author)}</dc:creator>'
            f'<cp:lastModifiedBy>{e(author)}</cp:lastModifiedBy><cp:revision>1</cp:revision>'
            f'<dcterms:created xsi:type="dcterms:W3CDTF">{stamp}</dcterms:created>'
            f'<dcterms:modified xsi:type="dcterms:W3CDTF">{stamp}</dcterms:modified>'
            '</cp:coreProperties>')


def _app_xml() -> str:
    from tundlekit import __version__

    return (XML_HEAD + '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
            'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
            f'<Application>tundlekit</Application><AppVersion>{_app_version(__version__)}</AppVersion>'
            '<DocSecurity>0</DocSecurity></Properties>')


def _app_version(version: str) -> str:
    """AppVersion must look like XX.YYYY."""
    parts = (re.findall(r"\d+", version) + ["0", "0"])[:2]
    return f"{int(parts[0]):02d}.{int(parts[1]):04d}"


def _xml_text(text: str) -> str:
    return _xml_escape(text, {'"': "&quot;"})


def _timestamp() -> str:
    """§18.1.2: TUNDLEKIT_NOW (§2.1) as written, without zone conversion, else the current UTC time."""
    value = os.environ.get("TUNDLEKIT_NOW")
    if value:
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
            try:
                return _dt.datetime.strptime(value.strip(), fmt).strftime("%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                pass
        raise ToolError(f"invalid TUNDLEKIT_NOW {value!r}: expected YYYY-MM-DDTHH:MM or YYYY-MM-DDTHH:MM:SS")
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _zip_bytes(entries: list[tuple[str, bytes]]) -> bytes:
    """A deterministic zip: fixed entry order, 1980-01-01 timestamps, fixed attributes (§18.1.4 A3)."""
    import io

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in entries:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 0
            info.external_attr = 0
            z.writestr(info, data)
    return buf.getvalue()


# ====================================================================== images
def image_info(data: bytes) -> tuple[str, int, int] | None:
    """(extension, width, height) from a PNG or JPEG header, or None when the bytes are neither."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        if len(data) >= 24 and data[12:16] == b"IHDR":
            w, h = struct.unpack(">II", data[16:24])
            return ("png", w, h) if w and h else None
        return None
    if data[:2] != b"\xff\xd8":
        return None
    i = 2
    while i + 4 <= len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker == 0xFF:
            i += 1
            continue
        if marker in (0x01, 0xD8) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        if marker == 0xD9:
            return None
        (length,) = struct.unpack(">H", data[i + 2:i + 4])
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            if i + 9 > len(data):
                return None
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return ("jpeg", w, h) if w and h else None
        if length < 2:
            return None
        i += 2 + length
    return None


# ====================================================================== inline Markdown (§18.1.1)
@dataclass
class Run:
    text: str
    bold: bool = False
    italic: bool = False
    code: bool = False


_CODE_OPEN, _CODE_CLOSE = "", ""         # private-use markers around inline code
_EMPH_CHARS = "*_"


def _textlint():
    from tundlekit import textlint

    return textlint


def _unprotect(text: str) -> str:
    return "".join(chr(ord(c) - 0xE000) if 0xE000 <= ord(c) < 0xE080 else c for c in text)


def _pairs(s: str, removed: list[tuple[int, int]]) -> list[tuple[int, int, int]]:
    """Pair emphasis delimiter runs (spans of s that textlint's reduction removes) into (start, end, strength)
    ranges: strength 1 italic, 2 bold, 3 both. Unpaired delimiters format nothing."""
    runs = []                                        # (char, start, end)
    for a, b in removed:
        k = a
        while k < b:
            j = k
            while j < b and s[j] == s[k]:
                j += 1
            runs.append((s[k], k, j))
            k = j
    stack: list[list] = []                           # [char, start, end, remaining]
    out = []
    for ch, a, b in runs:
        before = s[a - 1] if a > 0 else " "
        after = s[b] if b < len(s) else " "
        if ch == "*":
            can_open, can_close = not after.isspace(), not before.isspace()
        else:
            can_open = not before.isalnum() and not after.isspace()
            can_close = not after.isalnum() and not before.isspace()
        n = b - a
        if can_close:
            for idx in range(len(stack) - 1, -1, -1):
                if stack[idx][0] == ch:
                    opener = stack[idx]
                    k = min(opener[3], n, 3)
                    out.append((opener[2], a, k))
                    del stack[idx:]
                    n = 0
                    break
            if n == 0:
                continue
        if can_open:
            stack.append([ch, a, b, n])
    return out


def inline_runs(text: str, warn=None) -> list[Run]:
    """Runs for inline Markdown. The concatenated run text always reduces (docx_diff normalisation) to
    textlint.markdown_inline(text): when the formatted parse would differ, 1 plain run of that text is used."""
    tl = _textlint()
    s = tl._MD_ESCAPE.sub(lambda m: tl._protect(m.group(1)), text)
    s = tl._CODE_SPAN.sub(lambda m: _CODE_OPEN + tl._protect(m.group(2).strip()) + _CODE_CLOSE, s)
    s = tl._MD_COMMENT.sub("", s)
    images = len(tl._MD_IMAGE.findall(s))
    if images and warn is not None:
        for _ in range(images):
            warn()
    s = tl._MD_IMAGE.sub(r"\1", s)
    s = tl._MD_LINK.sub(r"\1", s)
    s = tl._MD_REF_LINK.sub(r"\1", s)
    s = tl._MD_AUTOLINK.sub(r"\1", s)
    removed = [m.span() for m in tl._MD_EMPHASIS.finditer(s)]
    gone = set()
    for a, b in removed:
        gone.update(range(a, b))
    bold = [0] * len(s)
    italic = [0] * len(s)
    for a, b, k in _pairs(s, removed):
        for pos in range(a, b):
            if k >= 2:
                bold[pos] += 1
            if k != 2:
                italic[pos] += 1
    runs: list[Run] = []
    code = False
    for pos, c in enumerate(s):
        if c == _CODE_OPEN:
            code = True
            continue
        if c == _CODE_CLOSE:
            code = False
            continue
        if pos in gone:
            continue
        ch = _unprotect(c)
        fmt = (bold[pos] > 0, italic[pos] > 0, code)
        if runs and (runs[-1].bold, runs[-1].italic, runs[-1].code) == fmt:
            runs[-1].text += ch
        else:
            runs.append(Run(ch, *fmt))
    expected = tl.markdown_inline(text)
    got = "".join(r.text for r in runs)
    if tl.normalise_paragraph(got) != tl.normalise_paragraph(expected):
        return [Run(expected)] if expected else []
    return [r for r in runs if r.text]


# ====================================================================== blocks (§18.1.1)
@dataclass
class Para:
    style: str | None
    runs: list


@dataclass
class Code:
    lines: list
    excerpt: bool = False


@dataclass
class Figure:
    data: bytes
    ext: str
    width: int
    height: int


@dataclass
class PageBreak:
    pass


@dataclass
class Table:
    rows: list                       # [[runs per cell]]
    widths: list                     # twips per column


@dataclass
class Parsed:
    blocks: list = field(default_factory=list)
    problems: list = field(default_factory=list)      # (line, message)
    warnings: list = field(default_factory=list)      # (line, message)
    title: str | None = None
    excerpts: int = 0
    figures: int = 0
    page_breaks: int = 0
    tables: int = 0
    excerpt_texts: list = field(default_factory=list)


HEADING_LINE = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
QUOTE_LINE = re.compile(r"^[ \t]*>")
LIST_LINE = re.compile(r"^([ \t]*)([-*+]|\d{1,9}[.)])(?:[ \t]+|$)(.*)$")
EXCERPT = re.compile(r"\{\{excerpt:(\w+)\|(.+)\}\}")
PLACEHOLDER = re.compile(r"\{\{.*\}\}")
PAGE_BREAK = re.compile(r"\\(pagebreak|newpage|clearpage)(\{\})?")
REMOTE = re.compile(r"(?i)^(?:https?:|//)")


def _longest_word(cell: str) -> int:
    return max((len(w) for w in cell.replace("`", "").split()), default=0)


def column_widths(rows: list[list[str]]) -> tuple[list[float], bool]:
    """§18.1.3 (port of add_table): inches per column, and whether the floors exceed the table width."""
    cols = list(zip(*rows))
    floor = [0.075 * max(_longest_word(c) for c in col) + 0.15 for col in cols]
    need = [max(min(len(c), 70) for c in col) for col in cols]
    spare = max(TABLE_INCHES - sum(floor), 0)
    total = sum(need)
    widths = [f + spare * n / total for f, n in zip(floor, need)] if total else list(floor)
    scale = TABLE_INCHES / sum(widths)
    return [w * scale for w in widths], sum(floor) > TABLE_INCHES


class _Parser:
    def __init__(self, text: str, base: pathlib.Path, excerpts: pathlib.Path | None, excerpts_arg: str | None):
        tl = _textlint()
        self.tl = tl
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = tl._MD_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)
        self.lines = tl._split_lines(text)
        self.base = base
        self.excerpts = excerpts
        self.excerpts_arg = excerpts_arg
        self.out = Parsed()

    # ------------------------------------------------------------------ helpers
    def problem(self, i: int, message: str) -> None:
        self.out.problems.append((i + 1, message))

    def warn(self, i: int, message: str) -> None:
        self.out.warnings.append((i + 1, message))

    def runs(self, text: str, line_index: int) -> list:
        return inline_runs(text, warn=lambda: self.warn(line_index, "inline image not embedded"))

    def is_sep(self, i: int) -> bool:
        return 0 <= i < len(self.lines) and self.tl._is_table_separator(self.lines[i])

    def bare_header(self, i: int) -> bool:
        """A header row that does not start with `|` above a separator row."""
        line = self.lines[i]
        return "|" in line and not line.strip().startswith("|") and not self.is_sep(i) and self.is_sep(i + 1)

    def starts_block(self, i: int) -> bool:
        line = self.lines[i]
        s = line.strip()
        tl = self.tl
        return bool(tl.FENCE_OPEN.match(line) or s.startswith("|") or self.bare_header(i)
                    or PLACEHOLDER.fullmatch(s) or tl._MD_IMAGE.fullmatch(s) or PAGE_BREAK.fullmatch(s)
                    or tl.THEMATIC_BREAK.match(line) or HEADING_LINE.match(line) or QUOTE_LINE.match(line)
                    or LIST_LINE.match(line))

    # ------------------------------------------------------------------ main loop
    def parse(self) -> Parsed:
        tl = self.tl
        lines = self.lines
        for i, line in enumerate(lines):
            bad = tl.XML_ILLEGAL.search(line)
            if bad:
                self.problem(i, f"character U+{ord(bad.group(0)):04X} is not allowed in XML")
        i = 0
        if lines and lines[0].strip() == "---":
            for j in range(1, len(lines)):
                if lines[j].strip() in ("---", "..."):
                    i = j + 1
                    break
        while i < len(lines):
            line = lines[i]
            s = line.strip()
            fence = tl.FENCE_OPEN.match(line)
            if fence:
                i = self.code(i, fence.group(1))
            elif s.startswith("|") or self.bare_header(i):
                i = self.table(i)
            elif PLACEHOLDER.fullmatch(s):
                self.placeholder(i, s)
                i += 1
            elif tl._MD_IMAGE.fullmatch(s):
                self.figure(i, s)
                i += 1
            elif PAGE_BREAK.fullmatch(s):
                self.out.blocks.append(PageBreak())
                self.out.page_breaks += 1
                i += 1
            elif tl.THEMATIC_BREAK.match(line):
                i += 1
            elif HEADING_LINE.match(line):
                self.heading(i, HEADING_LINE.match(line))
                i += 1
            elif QUOTE_LINE.match(line):
                i = self.quote(i)
            elif LIST_LINE.match(line):
                i = self.item(i, LIST_LINE.match(line))
            elif not s:
                i += 1
            else:
                i = self.paragraph(i)
        self.out.problems.sort(key=lambda p: p[0])
        self.out.warnings.sort(key=lambda p: p[0])
        return self.out

    # ------------------------------------------------------------------ constructs
    def code(self, i: int, fence: str) -> int:
        close = self.tl._fence_close(fence)
        for j in range(i + 1, len(self.lines)):
            if close.match(self.lines[j]):
                break
        else:
            self.problem(i, "unterminated code fence")
            return len(self.lines)
        body = [x.rstrip() for x in self.lines[i + 1:j]]
        while body and not body[-1].strip():
            body.pop()
        while body and not body[0].strip():
            body.pop(0)
        if body:
            self.out.blocks.append(Code(body))
        return j + 1

    def table(self, i: int) -> int:
        lines = self.lines
        if not lines[i].strip().startswith("|"):
            self.problem(i + 1, "separator row under a header row that does not start with |")
            j = i + 2
            while j < len(lines) and "|" in lines[j] and lines[j].strip():
                j += 1
            return j
        if not self.is_sep(i + 1):
            self.problem(i, "a line starting with | is not part of a table (no separator row under it)")
            return i + 1
        head = self.tl._table_cells(lines[i])
        raw = [(i, head)]
        j = i + 2
        while j < len(lines) and "|" in lines[j] and lines[j].strip():
            row = self.tl._table_cells(lines[j])
            if len(row) > len(head):
                self.problem(j, f"table row has {len(row)} cells, the header row has {len(head)}")
            raw.append((j, row[:len(head)] + [""] * (len(head) - len(row))))
            j += 1
        widths, squeezed = column_widths([r for _, r in raw])
        if squeezed:
            self.warn(i, "table columns squeezed below their longest word")
        rows = [[self.runs(c, k) for c in r] for k, r in raw]
        self.out.blocks.append(Table(rows, [round(w * TWIPS) for w in widths]))
        self.out.tables += 1
        return j

    def placeholder(self, i: int, s: str) -> None:
        m = EXCERPT.fullmatch(s)
        if not m:
            self.problem(i, f"unknown placeholder {s}")
            return
        self.out.excerpts += 1
        if self.excerpts is None:
            where = (f"excerpts directory {self.excerpts_arg} does not exist" if self.excerpts_arg
                     else "no excerpts directory (excerpts or build/excerpts next to the report); pass excerpts")
            self.problem(i, f"excerpt {m.group(1)}: {where}")
            return
        path = self.excerpts / f"{m.group(1)}.txt"
        try:
            text = path.read_bytes().decode("utf-8-sig")
        except FileNotFoundError:
            self.problem(i, f"excerpt file not found: {path}")
            return
        except (OSError, UnicodeDecodeError) as e:
            self.problem(i, f"cannot read excerpt {path}: {e}")
            return
        text = text.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
        bad = self.tl.XML_ILLEGAL.search(text)
        if bad:
            self.problem(i, f"excerpt {path}: character U+{ord(bad.group(0)):04X} is not allowed in XML")
            return
        if text:
            self.out.blocks.append(Code(text.split("\n"), excerpt=True))
            self.out.excerpt_texts.append(text)
        caption = self.runs(m.group(2), i)
        if caption:
            self.out.blocks.append(Para("Caption", caption))
            self.out.excerpt_texts.append("".join(r.text for r in caption))

    def figure(self, i: int, s: str) -> None:
        m = self.tl._MD_IMAGE.fullmatch(s)
        alt = m.group(1)
        target = s[len(alt) + 4:-1].strip()
        if target.startswith("<") and ">" in target:
            target = target[1:target.index(">")]
        else:
            target = target.split()[0] if target.split() else ""
        if not target:
            self.problem(i, "figure has no file")
            return
        if REMOTE.match(target):
            self.problem(i, f"figure {target}: remote images are not supported")
            return
        path = self.base / target
        if not path.is_file():
            from urllib.parse import unquote

            decoded = self.base / unquote(target)
            if decoded.is_file():
                path = decoded
            else:
                self.problem(i, f"figure file not found: {target}")
                return
        try:
            data = path.read_bytes()
        except OSError as e:
            self.problem(i, f"cannot read figure {target}: {e}")
            return
        info = image_info(data)
        if info is None:
            self.problem(i, f"figure {target} is neither PNG nor JPEG")
            return
        self.out.blocks.append(Figure(data, *info))
        self.out.figures += 1
        caption = self.runs(alt, i)
        if caption:
            self.out.blocks.append(Para("Caption", caption))

    def heading(self, i: int, m: re.Match) -> None:
        level = len(m.group(1))
        text = (m.group(2) or "").rstrip("#").strip()
        if level > 3:
            self.problem(i, f"heading level {level} is not supported (use #, ## or ###)")
            return
        runs = self.runs(text, i) if text else []
        if not runs:
            self.problem(i, "heading has no text")
            return
        self.out.blocks.append(Para(f"Heading{level}", runs))
        if level == 1 and self.out.title is None:
            self.out.title = "".join(r.text for r in runs)

    def quote(self, i: int) -> int:
        tl = self.tl
        parts = []
        j = i
        while j < len(self.lines) and QUOTE_LINE.match(self.lines[j]):
            line = self.lines[j]
            content = line[tl.QUOTE_PREFIX.match(line).end():]
            if (LIST_LINE.match(content) or HEADING_LINE.match(content) or tl.FENCE_OPEN.match(content)
                    or content.strip().startswith("|") or tl._MD_IMAGE.fullmatch(content.strip())):
                self.problem(j, "only plain text is supported in a block quote")
            elif content.strip():
                parts.append((j, content.strip()))
            j += 1
        if parts:
            runs = self.runs(" ".join(p for _, p in parts), parts[0][0])
            if runs:
                self.out.blocks.append(Para("Quote", runs))
        return j

    def item(self, i: int, m: re.Match) -> int:
        indent = len(m.group(1).expandtabs(4))
        marker = m.group(2)
        text = m.group(3).strip()
        j = i + 1
        while (j < len(self.lines) and self.lines[j].strip() and self.lines[j][:1] in (" ", "\t")
               and not self.starts_block(j)):
            text += " " + self.lines[j].strip()
            j += 1
        if not text:
            self.problem(i, "empty list item")
            return j
        level = "2" if indent >= 2 else ""
        runs = self.runs(text, i)
        if marker[0].isdigit():
            self.out.blocks.append(Para(f"ListNumber{level}", [Run(marker + "  ")] + runs))
        elif runs:
            self.out.blocks.append(Para(f"ListBullet{level}", runs))
        return j

    def paragraph(self, i: int) -> int:
        parts = [self.lines[i].strip()]
        j = i + 1
        while j < len(self.lines) and self.lines[j].strip() and not self.starts_block(j):
            parts.append(self.lines[j].strip())
            j += 1
        text = " ".join(parts)
        tl = self.tl
        for k in range(i, j):          # an inline image warns on its own line
            for _ in tl._MD_IMAGE.findall(tl._MD_ESCAPE.sub("", self.lines[k])):
                self.warn(k, "inline image not embedded")
        if text.startswith("*Table ") and text.endswith("*") and not text.endswith("**"):
            runs, style = inline_runs(text[1:-1]), "Caption"
        else:
            runs, style = inline_runs(text), None
        if runs:
            self.out.blocks.append(Para(style, runs))
        return j


# ====================================================================== document.xml
def _text_xml(text: str) -> str:
    """w:t / w:tab / w:br content for text holding tabs and newlines."""
    out = []
    for k, line in enumerate(text.split("\n")):
        if k:
            out.append("<w:br/>")
        for n, piece in enumerate(line.split("\t")):
            if n:
                out.append("<w:tab/>")
            if piece:
                out.append(f'<w:t xml:space="preserve">{_xml_text(piece)}</w:t>')
    return "".join(out)


def _run_xml(run: Run, base_size: int, size: int | None = None, bold: bool = False) -> str:
    props = []
    if run.code:
        props.append(_fonts("Consolas"))
    if run.bold or bold:
        props.append("<w:b/><w:bCs/>")
    if run.italic:
        props.append("<w:i/><w:iCs/>")
    sz = base_size - 2 if run.code else size
    if sz is not None:
        props.append(f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>')
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    return f"<w:r>{rpr}{_text_xml(run.text)}</w:r>"


def _para_xml(style: str | None, body: str, ppr: str = "") -> str:
    props = (f'<w:pStyle w:val="{style}"/>' if style else "") + ppr
    return f"<w:p>{'<w:pPr>' + props + '</w:pPr>' if props else ''}{body}</w:p>"


def _code_xml(block: Code) -> str:
    rpr = '<w:rPr><w:sz w:val="17"/><w:szCs w:val="17"/></w:rPr>' if block.excerpt else ""
    ppr = '<w:keepNext/><w:ind w:left="288"/>' if block.excerpt else ""
    return _para_xml("Code", f"<w:r>{rpr}{_text_xml(chr(10).join(block.lines))}</w:r>", ppr)


def _figure_xml(n: int, rid: str, fig: Figure) -> str:
    cx = FIGURE_EMU
    cy = round(FIGURE_EMU * fig.height / fig.width)
    name = f"image{n}.{fig.ext}"
    return _para_xml("Figure", (
        f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
        f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
        f'<wp:docPr id="{n}" name="Picture {n}"/>'
        f'<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        f'<a:graphic><a:graphicData uri="{PIC_NS}"><pic:pic>'
        f'<pic:nvPicPr><pic:cNvPr id="{n}" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        f'</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'))


def _table_xml(table: Table) -> str:
    total = sum(table.widths)
    size = PARA_SIZE["cell"]
    out = ['<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/>'
           f'<w:tblW w:w="{total}" w:type="dxa"/><w:jc w:val="center"/><w:tblLayout w:type="fixed"/>'
           '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" '
           'w:noHBand="0" w:noVBand="1"/></w:tblPr><w:tblGrid>']
    out += [f'<w:gridCol w:w="{w}"/>' for w in table.widths]
    out.append("</w:tblGrid>")
    for r, row in enumerate(table.rows):
        head = r == 0
        out.append("<w:tr><w:trPr><w:cantSplit/>" + ("<w:tblHeader/>" if head else "") + "</w:trPr>")
        for runs, w in zip(row, table.widths):
            shd = '<w:shd w:val="clear" w:color="auto" w:fill="EDEDED"/>' if head else ""
            body = "".join(_run_xml(x, size, size=size, bold=head) for x in runs)
            out.append(f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{shd}</w:tcPr>'
                       + _para_xml(None, body, '<w:spacing w:after="20"/>') + "</w:tc>")
        out.append("</w:tr>")
    out.append("</w:tbl>")
    return "".join(out)


def _visible(block) -> str:
    if isinstance(block, Para):
        return "".join(r.text for r in block.runs)
    if isinstance(block, Code):
        return "\n".join(block.lines)
    return ""


def render_document(parsed: Parsed) -> tuple[bytes, list[tuple[str, str, bytes]], dict]:
    """(document.xml, [(relationship id, media name, data)], counts)."""
    body = []
    media = []
    paragraphs = words = 0
    blocks = parsed.blocks
    for k, block in enumerate(blocks):
        if isinstance(block, Para):
            base = PARA_SIZE[block.style]
            body.append(_para_xml(block.style, "".join(_run_xml(r, base) for r in block.runs)))
        elif isinstance(block, Code):
            body.append(_code_xml(block))
        elif isinstance(block, Figure):
            n = len(media) + 1
            rid = f"rIdImg{n}"
            media.append((rid, f"image{n}.{block.ext}", block.data))
            body.append(_figure_xml(n, rid, block))
        elif isinstance(block, PageBreak):
            body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        elif isinstance(block, Table):
            body.append(_table_xml(block))
            if k + 1 == len(blocks) or isinstance(blocks[k + 1], Table):
                body.append("<w:p/>")          # Word wants a paragraph after a table
                paragraphs += 1
            continue
        paragraphs += 1
        words += len(_visible(block).split())
    sect = ('<w:sectPr><w:footerReference w:type="default" r:id="rId4"/>'
            '<w:pgSz w:w="12240" w:h="15840"/>'
            '<w:pgMar w:top="1152" w:right="1296" w:bottom="1152" w:left="1296" w:header="720" w:footer="720" '
            'w:gutter="0"/><w:cols w:space="720"/><w:docGrid w:linePitch="360"/></w:sectPr>')
    xml = (XML_HEAD + f'<w:document xmlns:w="{W_NS}" xmlns:r="{R_NS}" xmlns:wp="{WP_NS}" xmlns:a="{A_NS}" '
           f'xmlns:pic="{PIC_NS}"><w:body>' + "".join(body) + sect + "</w:body></w:document>")
    return xml.encode("utf-8"), media, {"paragraphs": paragraphs, "words": words}


def package(parsed: Parsed, author: str) -> tuple[bytes, dict]:
    document, media, counts = render_document(parsed)
    rels = [("rId1", f"{REL_BASE}/styles", "styles.xml"),
            ("rId2", f"{REL_BASE}/settings", "settings.xml"),
            ("rId3", f"{REL_BASE}/numbering", "numbering.xml"),
            ("rId4", f"{REL_BASE}/footer", "footer1.xml")]
    rels += [(rid, f"{REL_BASE}/image", f"media/{name}") for rid, name, _ in media]
    entries = [("[Content_Types].xml", _content_types({n.rsplit(".", 1)[1] for _, n, _ in media})),
               ("_rels/.rels", _package_rels()),
               ("docProps/core.xml", _core_xml(parsed.title or "", author, _timestamp())),
               ("docProps/app.xml", _app_xml()),
               ("word/document.xml", document),
               ("word/_rels/document.xml.rels", _rels(rels)),
               ("word/styles.xml", _styles_xml()),
               ("word/settings.xml", _settings_xml()),
               ("word/numbering.xml", _numbering_xml()),
               ("word/footer1.xml", _footer_xml())]
    entries += [(f"word/media/{name}", data) for _, name, data in media]
    data = _zip_bytes([(n, d.encode("utf-8") if isinstance(d, str) else d) for n, d in entries])
    return data, counts


# ====================================================================== the tool (§18.1)
def _default_author(folder: pathlib.Path) -> str:
    env = os.environ.get("TUNDLEKIT_AUTHOR")
    if env:
        return env
    try:
        proc = subprocess.run(["git", "config", "user.name"], cwd=str(folder), capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=20)
    except (OSError, subprocess.SubprocessError):
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _default_excerpts(folder: pathlib.Path) -> pathlib.Path | None:
    for cand in (folder / "excerpts", folder / "build" / "excerpts"):
        if cand.is_dir():
            return cand
    return None


def _same_file(a: pathlib.Path, b: pathlib.Path) -> bool:
    try:
        if a.exists() and b.exists():
            return os.path.samefile(a, b)
    except OSError:
        pass
    return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


def _hand_edits(report: str, out: str, parsed: Parsed) -> int | None:
    """Changes between the report and an existing build (None when out is not a readable .docx). Inserts of the
    excerpt texts and captions this build writes are expected (§18.1.4 A2) and not counted."""
    tl = _textlint()
    try:
        changes = tl.docx_diff(report, out)["changes"]
    except Exception:  # noqa: BLE001 - any unreadable package counts as "cannot be read"
        return None
    expected = {tl.normalise_paragraph(t) for t in parsed.excerpt_texts}
    return sum(1 for c in changes
               if not (c["op"] == "insert" and all(tl.normalise_paragraph(p) in expected for p in c["new"])))


@tool("report_build",
      "Build a .docx from a Markdown report in the tundle house style (US Letter, Calibri 11 pt, 6.5 in figures, "
      "9.5 pt tables and captions, page-number footer). Supports ATX headings (#-###), paragraphs with bold, "
      "italic and code, bullet and numbered lists, pipe tables, block quotes, fenced code, whole-line PNG/JPEG "
      "figures with captions, *Table N. ...* captions, \\pagebreak and {{excerpt:name|caption}} placeholders. "
      "Every unsupported construct is reported as 'line N: ...' and nothing is written. An existing output with "
      "hand edits (docx_diff against the report) is refused unless overwrite. Refuses while Word or PowerPoint "
      "runs unless force_office. Standard library only.",
      {"type": "object",
       "properties": {
           "report": {"type": "string", "description": "the Markdown report"},
           "out": {"type": "string", "description": "output .docx path"},
           "excerpts": {"type": "string",
                        "description": "directory of excerpt .txt files; default: excerpts or build/excerpts "
                                       "next to the report"},
           "author": {"type": "string",
                      "description": "document author; default: TUNDLEKIT_AUTHOR, else git config user.name"},
           "overwrite": {"type": "boolean", "description": "replace an existing output even with hand edits"},
           "force_office": {"type": "boolean", "description": "write even while Word or PowerPoint runs"}},
       "required": ["report", "out"],
       "additionalProperties": False},
      readOnlyHint=False)
def report_build(report: str, out: str, excerpts: str | None = None, author: str | None = None,
                 overwrite: bool = False, force_office: bool = False) -> dict:
    tl = _textlint()
    from tundlekit import render as _render

    # 1. the report
    if not isinstance(report, str) or not report or "\0" in report:
        raise ToolError(f"report is not a valid path: {report!r}")
    src = pathlib.Path(tl.native_path(report))
    if not src.is_file():
        raise ToolError(f"report: no such file: {report}")
    try:
        text = src.read_bytes().decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ToolError(f"report: {report} is not UTF-8 text") from None
    except OSError as e:
        raise ToolError(f"cannot read {report}: {e}") from None

    # 2. the output path
    _render.check_path_string(out, "out")
    dst = pathlib.Path(tl.native_path(out))
    if dst.suffix.lower() != ".docx":
        raise ToolError(f"out must be a .docx file: {out}")
    if dst.is_dir():
        raise ToolError(f"out is a directory: {out}")
    if _same_file(src, dst):
        raise ToolError(f"out is the report itself: {out}")
    if not dst.parent.is_dir():
        raise ToolError(f"out: no such directory: {dst.parent}")

    # 3. Office guard (§18.4: .docx only, so the default set)
    if not force_office:
        running = _render.office_running()
        if running:
            raise ToolError(f"refusing to write {out} while {', '.join(running)} is running; close it or pass "
                            "force_office")

    # 4. parse, collecting every problem
    base = src.parent
    if excerpts is not None:
        if not excerpts or "\0" in excerpts:
            raise ToolError(f"excerpts is not a valid path: {excerpts!r}")
        ex_dir = pathlib.Path(tl.native_path(excerpts))
        ex_dir = ex_dir if ex_dir.is_dir() else None
    else:
        ex_dir = _default_excerpts(base)
    parsed = _Parser(text, base, ex_dir, excerpts).parse()
    if parsed.problems:
        lines = [f"line {n}: {m}" for n, m in parsed.problems]
        raise ToolError(f"{report}: {len(lines)} problem(s), nothing written:\n" + "\n".join(lines))

    if author is None:
        author = _default_author(base)
    bad = tl.XML_ILLEGAL.search(author)
    if bad:
        raise ToolError(f"author: character U+{ord(bad.group(0)):04X} is not allowed in XML")
    data, counts = package(parsed, author)

    # 5. hand-edit guard
    replaced = dst.exists()
    if replaced and not overwrite:
        n = _hand_edits(str(src), str(dst), parsed)
        if n is None:
            raise ToolError(f"{out} exists and cannot be read as a .docx: 0 changes can be checked; pass "
                            "overwrite to replace it")
        if n:
            raise ToolError(f"{out} has {n} change(s) against {report} (hand edits?); carry them back "
                            "(tundlekit text docx-diff) or pass overwrite to replace it")

    # 6. atomic write
    tl.replace_file(str(dst), data)
    return {"out": out, "title": parsed.title or "", "author": author, "paragraphs": counts["paragraphs"],
            "tables": parsed.tables, "figures": parsed.figures, "excerpts": parsed.excerpts,
            "page_breaks": parsed.page_breaks, "words": counts["words"], "replaced": replaced,
            "warnings": [f"line {n}: {m}" for n, m in parsed.warnings]}


# ====================================================================== CLI (§18.6)
def add_cli(groups) -> None:
    from tundlekit.cli_support import common_flags

    p = groups.add_parser("report", help="build report documents")
    cmds = p.add_subparsers(dest="command", required=True)
    c = cmds.add_parser("build", help="build a .docx from a Markdown report")
    c.add_argument("report", help="the Markdown report")
    c.add_argument("-o", "--out", required=True, help="output .docx")
    c.add_argument("--excerpts", help="directory of excerpt .txt files")
    c.add_argument("--author", help="document author")
    c.add_argument("--overwrite", action="store_true", help="replace an output that has hand edits")
    c.add_argument("--force-office", dest="force_office", action="store_true",
                   help="write even while Word or PowerPoint runs")
    common_flags(c)
    c.set_defaults(handler=_cli_build)


def _cli_build(args):
    from tundlekit.cli_support import CliResult

    res = report_build(report=args.report, out=args.out, excerpts=args.excerpts, author=args.author,
                       overwrite=args.overwrite, force_office=args.force_office)
    text = (f"wrote {res['out']} ({res['paragraphs']} paragraphs, {res['tables']} tables, "
            f"{res['figures']} figures, ~{res['words']} words outside tables)")
    if res["warnings"]:
        text += "\n" + "\n".join(f"warning: {w}" for w in res["warnings"])
    return CliResult(res, text=text, exit_code=0)
