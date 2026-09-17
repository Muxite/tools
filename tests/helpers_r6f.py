"""Helpers for the round-6 fixes tests (MANIFEST §19). Not a conftest; `import helpers_r6f as h`. No tundlekit
import at module level. Docx files are hand-built zips, so run properties, hyperlinks and w:del can be written."""
from __future__ import annotations

import ast
import importlib
import json
import os
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers_r4m import run_cli, sha256, write  # noqa: E402,F401
from helpers_r5b import (NOW, TODAY, authors_of, b014_count, by_rule, check_shape, files_under,  # noqa: E402,F401
                         installer, snapshot_name, summarise, title_of, tundle, windows_setup)

WINDOWS = os.name == "nt"
OWNER = {
    "text_apply_edits": "textlint", "docx_diff": "textlint", "text_xref": "textlint",
    "bundle_backup": "bundle", "bundle_lint": "bundle", "bundle_source": "bundle", "bundle_verify": "bundle",
    "diagram_render": "diagram", "chart_bar": "chart", "deck_build": "deck",
    "render_pdf": "render", "render_contact_sheet": "render", "render_office": "render",
    "papers_summary": "papers", "translate_terms": "translate",
}


def call(name: str, **args):
    """Import the owning module (§15.10), then registry.call (§1). Path values become strings."""
    importlib.import_module("tundlekit." + OWNER[name])
    clean = {k: str(v) if isinstance(v, Path) else [str(x) for x in v] if isinstance(v, list) and any(
        isinstance(x, Path) for x in v) else v for k, v in args.items()}
    return importlib.import_module("tundlekit.registry").call(name, clean)


def tool_error():
    return importlib.import_module("tundlekit.registry").ToolError


def read(path) -> str:
    return Path(path).read_text(encoding="utf-8")


def read_json(path):
    return json.loads(read(path))


def listing(folder) -> list:
    folder = Path(folder)
    return sorted(p.relative_to(folder).as_posix() for p in folder.rglob("*"))


def apply_edits(**kw):
    return call("text_apply_edits", **kw)


def docx_diff(old, new, **kw):
    res = call("docx_diff", old=str(old), new=str(new), **kw)
    assert isinstance(res["changes"], list)
    return res


def module_value(path, name):
    """The value of `NAME = <literal>` in a Python file (the file must parse)."""
    tree = ast.parse(read(path))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"{name} not assigned in {path}")


def emit_and_apply(cwd, old_paras, new_paras, search="src"):
    """docx_diff old.docx → new.docx with emit_edits, then apply the emitted file with write; returns both."""
    make_docx(cwd / "old.docx", old_paras)
    make_docx(cwd / "new.docx", new_paras)
    res = docx_diff(cwd / "old.docx", cwd / "new.docx", search=[str(cwd / search)],
                    emit_edits=str(cwd / "edits.json"))
    edits = read_json(cwd / "edits.json")
    applied = apply_edits(edits=edits, write=True) if edits else None
    return res, edits, applied


def only_edit(edits):
    (obj,) = edits
    (e,) = obj["edits"]
    return e


# ------------------------------------------------------------------------------------ docx builder
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
W = "{%s}" % W_NS


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def r(text: str = "", rpr: str = "") -> str:
    """A run: "\\t" → w:tab, "\\n" → w:br, other text → w:t; rpr is raw w:rPr content (e.g. '<w:i/>')."""
    props = f"<w:rPr>{rpr}</w:rPr>" if rpr else ""
    parts = []
    buf = ""
    for ch in text:
        if ch in "\t\n":
            if buf:
                parts.append(f'<w:t xml:space="preserve">{esc(buf)}</w:t>')
                buf = ""
            parts.append("<w:tab/>" if ch == "\t" else "<w:br/>")
        else:
            buf += ch
    if buf:
        parts.append(f'<w:t xml:space="preserve">{esc(buf)}</w:t>')
    return f"<w:r>{props}{''.join(parts)}</w:r>"


def p(*runs) -> str:
    """A paragraph from raw run XML strings (plain strings without '<' become plain runs)."""
    return "<w:p>" + "".join(x if x.startswith("<") else r(x) for x in runs) + "</w:p>"


def make_docx(path, paragraphs) -> Path:
    """paragraphs: plain strings (1 run; \\t/\\n as tab/break) or raw '<w:p>...' XML."""
    body = "".join(x if x.startswith("<w:p>") else p(r(x)) for x in paragraphs)
    document = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="{W_NS}" '
                f'xmlns:r="{R_NS}"><w:body>{body}<w:sectPr/></w:body></w:document>')
    pkg = "http://schemas.openxmlformats.org/package/2006/"
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"
    parts = {
        "[Content_Types].xml": f'<Types xmlns="{pkg}content-types"><Default Extension="rels" ContentType='
                               '"application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" '
                               'ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType='
                               '"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                               "</Types>",
        "_rels/.rels": f'<Relationships xmlns="{pkg}relationships"><Relationship Id="rId1" '
                       f'Type="{rel}officeDocument" Target="word/document.xml"/></Relationships>',
        "word/_rels/document.xml.rels": f'<Relationships xmlns="{pkg}relationships"><Relationship Id="rId9" '
                                        f'Type="{rel}hyperlink" Target="https://example.org/guide" '
                                        'TargetMode="External"/></Relationships>',
        "word/document.xml": document,
    }
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(str(path), "w", zipfile.ZIP_DEFLATED) as z:
        for name, xml in parts.items():
            z.writestr(name, xml)
    return path


def document_xml(path) -> str:
    with zipfile.ZipFile(str(path)) as z:
        return z.read("word/document.xml").decode("utf-8")


def body_paragraphs(path) -> list:
    return list(ET.fromstring(document_xml(path)).find(W + "body").iter(W + "p"))


def run_texts(par) -> list:
    """[(text, is_italic, is_bold, in_hyperlink)] for every run of a paragraph (w:del runs excluded)."""
    out = []

    def walk(el, link, deleted):
        for child in el:
            if child.tag == W + "r":
                if deleted:
                    continue
                rpr = child.find(W + "rPr")
                text = "".join((n.text or "") if n.tag == W + "t" else "\t" if n.tag == W + "tab"
                               else "\n" if n.tag == W + "br" else "" for n in child)
                out.append((text, rpr is not None and rpr.find(W + "i") is not None,
                            rpr is not None and rpr.find(W + "b") is not None, link))
            else:
                walk(child, link or child.tag == W + "hyperlink", deleted or child.tag == W + "del")
    walk(par, False, False)
    return out


def para_text(par) -> str:
    return "".join(t for t, *_ in run_texts(par))


def texts(path) -> list:
    return [para_text(x) for x in body_paragraphs(path)]


# ------------------------------------------------------------------------------------ Windows file attributes
HIDDEN, SYSTEM = 0x2, 0x4


def _kernel32():
    import ctypes

    return ctypes.windll.kernel32


def get_attrs(path) -> int:
    return _kernel32().GetFileAttributesW(str(path))


def set_attrs(path, flags) -> None:
    assert _kernel32().SetFileAttributesW(str(path), get_attrs(path) | flags)


def clear_attrs(path) -> None:
    _kernel32().SetFileAttributesW(str(path), 0x80)  # FILE_ATTRIBUTE_NORMAL


# ------------------------------------------------------------------------------------ bundle
def backup(files, reason, **kw):
    if not isinstance(files, list):
        files = [files]
    return call("bundle_backup", files=[str(f) for f in files], reason=reason, **kw)


def labelled(label: str, stem: str, reason: str, ext: str, date: str = TODAY) -> str:
    """§19.2: `<label> <stem> (before <reason> <date>)<ext>`."""
    return f"{label} {snapshot_name(stem, reason, ext, date)}"


def pruned_paths(res, key="pruned") -> list:
    """Paths under `pruned` (or `not_pruned`); entries may be strings or {path, ...} objects."""
    return [x if isinstance(x, str) else x.get("path") for x in res.get(key, [])]


def not_pruned_paths(res) -> list:
    return pruned_paths(res, "not_pruned")


def skipped_for(res, name) -> list:
    """Entries of a batch result's `skipped` that name the installer (any key)."""
    return [s for s in res.get("skipped", []) if name in json.dumps(s, ensure_ascii=False)]


# ------------------------------------------------------------------------------------ xref
def xref(**kw):
    res = call("text_xref", **kw)
    check_shape(res)
    return res


def skip_unless_windows():
    if not WINDOWS:
        pytest.skip("Windows device names only")
