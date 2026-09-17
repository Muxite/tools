"""Shared helpers for the round-5 tests (MANIFEST §17.1, §17.2, §17.6, on top of §15.2, §15.4, §15.5, §16.3, §16.5).

Not a conftest. Import with `import helpers_r5 as h`. Builds on helpers_r4d (docx builders) and helpers_r3rc
(checker shape, CLI runner); nothing imports tundlekit at module level, so collection succeeds before §17 exists.
"""
from __future__ import annotations

import importlib
import json
import os
import stat
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_r3 as r3  # noqa: E402
from helpers_r3rc import assert_checker_shape, of, read, run_cli, write, write_spec  # noqa: E402,F401
from helpers_r4d import (BR, TAB, W_NS, document_xml, esc, make_docx, need_pptx, open_deck,  # noqa: E402,F401
                         read_json, run, tool_error)

OWNER = {
    "text_apply_edits": "textlint", "docx_diff": "textlint", "text_xref": "textlint", "text_fignums": "textlint",
    "deck_diff": "deck", "deck_build": "deck", "review_coverage": "review", "diagram_render": "diagram",
    "office_check": "render",
}
W = "{%s}" % W_NS


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


def apply_edits(**kw):
    return call("text_apply_edits", **kw)


def docx_diff(old, new, **kw):
    res = call("docx_diff", old=str(old), new=str(new), **kw)
    assert isinstance(res["changes"], list)
    return res


def xref(**kw):
    res = call("text_xref", **kw)
    assert_checker_shape(res)
    return res


def where(res, rule):
    return [(f["path"], f["line"]) for f in of(res, rule)]


def same_file(a, b) -> bool:
    return os.path.normcase(os.path.realpath(str(a))) == os.path.normcase(os.path.realpath(str(b)))


def listing(folder) -> list:
    """Every file under folder (relative, / separators), to prove no temp or backup file is left behind."""
    folder = Path(folder)
    return sorted(p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file())


def make_read_only(path):
    os.chmod(str(path), stat.S_IREAD)


def make_writable(path):
    os.chmod(str(path), stat.S_IREAD | stat.S_IWRITE)


# ------------------------------------------------------------------------------------ docx (§17.1)
TABSTOPS = '<w:pPr><w:tabs><w:tab w:val="left" w:pos="720"/></w:tabs></w:pPr>'
PAGE_BR = '<w:r><w:br w:type="page"/></w:r>'


def para(parts, ppr: str = "") -> tuple:
    """A raw paragraph: str parts are runs, "\\t" a run tab, "\\n" a line break, "\\f" a page break."""
    body = "".join(TAB if p == "\t" else BR if p == "\n" else PAGE_BR if p == "\f" else run(p) for p in parts)
    return ("raw", f"<w:p>{ppr}{body}</w:p>")


def tabstop_para(parts) -> tuple:
    return para(parts, TABSTOPS)


def paragraphs(path) -> list:
    """Body paragraph texts read independently of tundlekit: run-level w:t, w:tab, w:br (page break = \\f)."""
    root = ET.fromstring(document_xml(path))
    out = []
    for p in root.iter(W + "p"):
        text = []
        for r in p.findall(W + "r"):
            for node in r:
                if node.tag == W + "t":
                    text.append(node.text or "")
                elif node.tag == W + "tab":
                    text.append("\t")
                elif node.tag == W + "br":
                    text.append("\f" if node.get(W + "type") == "page" else "\n")
        out.append("".join(text))
    return out


def assert_ppr_schema_shaped(path):
    """No text inside any w:pPr; w:tabs holds only w:tab elements without text or children."""
    root = ET.fromstring(document_xml(path))
    for ppr in root.iter(W + "pPr"):
        assert not list(ppr.iter(W + "t")), "w:t inside w:pPr"
        assert not list(ppr.iter(W + "r")), "w:r inside w:pPr"
        for tabs in ppr.iter(W + "tabs"):
            for child in tabs:
                assert child.tag == W + "tab", child.tag
                assert not list(child) and not (child.text or "").strip()
            assert len(list(tabs)) == 1


def emitted(path) -> list:
    """The emit_edits file, or [] when none was written ("nothing emitted")."""
    p = Path(path)
    return read_json(p) if p.exists() else []


# ------------------------------------------------------------------------------------ decks (§17.2)
def lines_slide(title, items, say=None):
    kw = {} if say is None else {"say": say}
    return r3.content(title, body={"kind": "lines", "items": list(items)}, **kw)


def build(path, slides):
    need_pptx()
    call("deck_build", spec={"meta": {"id": "r5"}, "slides": slides}, out=str(path))
    return Path(path)


def edit_line(src, dst, old_line, new_line):
    """Copy a deck with the 1 paragraph whose text is old_line set to new_line (first run keeps formatting)."""
    prs = open_deck(src)
    for slide in prs.slides:
        for tf in r3._frames(slide):
            for p in tf.paragraphs:
                if p.text == old_line:
                    p.runs[0].text = new_line
                    for extra in p.runs[1:]:
                        extra._r.getparent().remove(extra._r)
                    prs.save(str(dst))
                    return Path(dst)
    raise AssertionError(f"no paragraph {old_line!r}")


def edit_notes(src, dst, old, new):
    prs = open_deck(src)
    for slide in prs.slides:
        tf = slide.notes_slide.notes_text_frame
        if old in tf.text:
            tf.text = tf.text.replace(old, new)
            prs.save(str(dst))
            return Path(dst)
    raise AssertionError(f"no notes containing {old!r}")


def deck_diff(old, new, **kw):
    res = call("deck_diff", old=str(old), new=str(new), **kw)
    for c in res["changes"]:
        assert isinstance(c["hint"], list) and len(c["hint"]) <= 3
    return res


def hints(res, field):
    return [[h.replace("\\", "/") for h in c["hint"]] for c in res["changes"] if c["field"] == field]


def dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


# ------------------------------------------------------------------------------------ review_coverage (§17.6)
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


def _sp(shape_id: int, text: str, y: int) -> str:
    return (f'<p:sp xmlns:p="{P_NS}" xmlns:a="{A_NS}"><p:nvSpPr><p:cNvPr id="{shape_id}" name="Box {shape_id}"/>'
            '<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm>'
            f'<a:off x="457200" y="{y}"/><a:ext cx="4572000" cy="457200"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="en-US"/><a:t>{esc(text)}</a:t></a:r></a:p>'
            '</p:txBody></p:sp>')


def alternate_content(text: str, y: int = 2743200) -> str:
    """An mc:AlternateContent shape (Choice and Fallback copies), as PowerPoint writes newer shapes."""
    return ('<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
            'xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main">'
            f'<mc:Choice Requires="p14">{_sp(901, text, y)}</mc:Choice>'
            f'<mc:Fallback>{_sp(902, text, y)}</mc:Fallback></mc:AlternateContent>')


def inject_xml(pptx_path, slide_index: int, xml: str):
    """Append a raw shape element to a slide's shape tree (before any extLst) and save in place."""
    from lxml import etree

    prs = open_deck(pptx_path)
    tree = prs.slides[slide_index].shapes._spTree
    elm = etree.fromstring(xml)
    ext = [c for c in tree if c.tag.endswith("}extLst")]
    if ext:
        ext[0].addprevious(elm)
    else:
        tree.append(elm)
    prs.save(str(pptx_path))
    return Path(pptx_path)


def review(**kw):
    res = call("review_coverage", **{k: str(v) if isinstance(v, Path) else v for k, v in kw.items()})
    assert_checker_shape(res)
    return res
