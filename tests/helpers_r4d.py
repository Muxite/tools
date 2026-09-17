"""Shared helpers for the round-4 deck/docx tests (MANIFEST §16.2, §16.3, §16.7).

Builds on helpers_r3 (decks via deck_build, python-pptx edits, hand-built .docx zips). Not a conftest; test
modules import it as `import helpers_r4d as r4`. Nothing here imports tundlekit at module level.
"""
from __future__ import annotations

import difflib
import importlib
import json
import zipfile
from pathlib import Path

import helpers_r3 as r3
from helpers_r3 import (build_deck, content, need_pptx, open_deck, run_cli, slash, title_slide,  # noqa: F401
                        tool_error, write)

OWNER = dict(r3.OWNER, text_apply_edits="textlint", deck_lint="deck")


def call(name: str, **args):
    """Import the owning module (§15.10), then registry.call (§1). Path values become strings."""
    importlib.import_module("tundlekit." + OWNER[name])
    clean = {}
    for k, v in args.items():
        if isinstance(v, Path):
            v = str(v)
        elif isinstance(v, list):
            v = [str(x) if isinstance(x, Path) else x for x in v]
        clean[k] = v
    return importlib.import_module("tundlekit.registry").call(name, clean)


def similarity(a: str, b: str) -> float:
    """§16.2 title similarity (whitespace collapsed, case folded)."""
    n = lambda s: " ".join(s.casefold().split())  # noqa: E731
    return difflib.SequenceMatcher(None, n(a), n(b)).ratio()


# ------------------------------------------------------------------------------------ deck_diff (§16.2)
FIELDS = ("title", "text", "notes", "hidden", "added", "removed", "moved", "number")

# 10 titles that are pairwise dissimilar (checked by a test), as in a real capsule talk
TITLES = [
    "Kept tools fail held-out tests",
    "Execution Broker isolates side effects",
    "Retirement keeps the library small",
    "Gates decide admission",
    "Budgets cap every run at forty minutes",
    "Quarterly numbers from pilot teams",
    "Cost per accepted capsule by month",
    "Open questions for reviewers",
    "What we ask of the platform group",
    "Next steps and owners",
]


def ten_spec(order=None, titles=TITLES):
    """Content slides only, so slide k in spec order is numbered k (§3.2)."""
    order = list(range(len(titles))) if order is None else order
    return {"meta": {"id": "capsule"},
            "slides": [content(titles[i], say=f"Speaker text for slide about {titles[i].lower()} " + r3.SAY)
                       for i in order]}


def deck_diff(old, new, **kw):
    res = call("deck_diff", old=str(old), new=str(new), **kw)
    assert isinstance(res["changes"], list)
    for c in res["changes"]:
        assert set(c) >= {"slide", "field", "old", "new"}
        assert c["field"] in FIELDS, c
        assert isinstance(c["slide"], str), c          # §16.2: always a string
    return res


def of(res, field):
    return [c for c in res["changes"] if c["field"] == field]


def table_spec(rows, title="Results by gate"):
    return {"meta": {"id": "tables"}, "slides": [
        content("Kept tools fail held-out tests"),
        content(title, body={"kind": "table", "rows": rows}),
    ]}


# ------------------------------------------------------------------------------------ docx (§16.3)
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"
WPS_NS = "http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
V_NS = "urn:schemas-microsoft-com:vml"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def run(text: str) -> str:
    return f'<w:r><w:t xml:space="preserve">{esc(text)}</w:t></w:r>'


TAB = "<w:r><w:tab/></w:r>"
BR = "<w:r><w:br/></w:r>"


def para_xml(item) -> str:
    """str -> 1 run; list -> runs where "\\t" and "\\n" items become <w:tab/> and <w:br/>; ("raw", xml) -> as is."""
    if isinstance(item, tuple) and item[0] == "raw":
        return item[1]
    parts = [item] if isinstance(item, str) else item
    body = "".join(TAB if p == "\t" else BR if p == "\n" else run(p) for p in parts if p != "")
    return f"<w:p>{body}</w:p>"


def textbox_para(text: str, before: str = "") -> str:
    """A paragraph holding a text box written twice (mc:Choice and mc:Fallback), as Word saves it."""
    inner = f"<w:txbxContent><w:p>{run(text)}</w:p></w:txbxContent>"
    return ("raw", f"<w:p>{run(before) if before else ''}<w:r><mc:AlternateContent>"
                   f"<mc:Choice Requires=\"wps\"><w:drawing><wps:txbx>{inner}</wps:txbx></w:drawing></mc:Choice>"
                   f"<mc:Fallback><w:pict><v:textbox>{inner}</v:textbox></w:pict></mc:Fallback>"
                   f"</mc:AlternateContent></w:r></w:p>")


def make_docx(path: Path, paragraphs) -> Path:
    body = "".join(para_xml(p) for p in paragraphs)
    document = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<w:document xmlns:w="{W_NS}" xmlns:mc="{MC_NS}" xmlns:wps="{WPS_NS}" xmlns:v="{V_NS}" '
                f'mc:Ignorable="wps"><w:body>{body}<w:sectPr/></w:body></w:document>')
    ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/word/document.xml" '
          'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
          "</Types>")
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="word/document.xml"/></Relationships>')
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(str(path), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", document)
    return path


def document_xml(path: Path) -> str:
    with zipfile.ZipFile(str(path)) as z:
        return z.read("word/document.xml").decode("utf-8")


def docx_diff(old, new, **kw):
    res = call("docx_diff", old=str(old), new=str(new), **kw)
    assert isinstance(res["changes"], list)
    for c in res["changes"]:
        assert set(c) >= {"op", "old", "new", "old_index", "new_index", "hint"}
    return res


def apply_edits(**kw):
    return call("text_apply_edits", **kw)


def read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def emitted_by_file(data):
    """{file name: [edits]} from an emit_edits list (§16.3)."""
    assert isinstance(data, list)
    out = {}
    for obj in data:
        assert set(obj) >= {"path", "edits"}
        name = Path(obj["path"]).name
        assert name not in out, "1 object per target file"
        out[name] = obj["edits"]
    return out


# ------------------------------------------------------------------------------------ deck build (§16.7)
def build(tmp_path, spec, name="out.pptx", **kw):
    need_pptx()
    return call("deck_build", spec=spec, out=str(Path(tmp_path) / name), **kw)


def one_slide(body, **kw):
    return {"meta": {"id": "misc"}, "slides": [content("Kept tools fail held-out tests", body=body, **kw)]}


def slide_warnings(result, label="1"):
    return [w for w in result["warnings"] if w.startswith(f"slide {label}: ")]


def charts(pptx_path):
    prs = open_deck(pptx_path)
    return [sh.chart for s in prs.slides for sh in s.shapes if getattr(sh, "has_chart", False) and sh.has_chart]


def tables(pptx_path):
    prs = open_deck(pptx_path)
    return [sh.table for s in prs.slides for sh in s.shapes if getattr(sh, "has_table", False) and sh.has_table]


def cell_fonts(cell):
    return {r.font.name for p in cell.text_frame.paragraphs for r in p.runs if r.text}
