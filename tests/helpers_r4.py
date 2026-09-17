"""Shared helpers for the review-round-4 safety tests (MANIFEST §16.1, §16.7 office_check / integral floats).

Not a conftest. Test modules import it with `import helpers_r4 as h`. Nothing here imports tundlekit (or an
optional package) at module level, so collection succeeds before the tools exist. Each tool call imports the
owning module (§15.10), then goes through `registry.call` (§1).
"""
from __future__ import annotations

import importlib
import io
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

REPO = Path(os.environ.get("TUNDLEKIT_REPO") or Path(__file__).resolve().parent.parent)

_OWNER = {"text": "textlint", "docx": "textlint", "deck": "deck", "diagram": "diagram", "chart": "chart",
          "papers": "papers", "bundle": "bundle", "render": "render", "office": "render",
          "review": "review", "claims": "claims", "palette": "palette"}


# ------------------------------------------------------------------------------------ tool access
def call(name: str, **args):
    """Import the owning module (§15.10), then registry.call (§1). Path values become str."""
    importlib.import_module("tundlekit." + _OWNER[name.split("_")[0]])
    from tundlekit import registry

    clean = {}
    for k, v in args.items():
        if isinstance(v, Path):
            v = str(v)
        elif isinstance(v, list):
            v = [str(x) if isinstance(x, Path) else x for x in v]
        clean[k] = v
    return registry.call(name, clean)


def tool_error():
    from tundlekit.registry import ToolError

    return ToolError


def run_cli(capsys, argv):
    """tundlekit.cli.main in-process (§0.4) -> (code, parsed JSON or None, stdout, stderr)."""
    importlib.import_module("tundlekit.render")
    from tundlekit import cli

    capsys.readouterr()
    try:
        code = cli.main([str(a) for a in argv])
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 2
    out, err = capsys.readouterr()
    data = None
    if out.strip():
        try:
            data = json.loads(out)
        except ValueError:
            data = None
    return code, data, out, err


def write(path, text: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return path


def names_index(message: str, index: int) -> bool:
    """§16.1: the ToolError names the edit index (0-based or 1-based wording both accepted)."""
    return re.search(rf"(?<![\d.]){index}(?![\d.])", message) is not None or \
        re.search(rf"(?<![\d.]){index + 1}(?![\d.])", message) is not None


# ------------------------------------------------------------------------------------ docx / zip
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
PNG_1PX = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360000002000100e221bc330000000049454e44ae426082")


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def make_docx(path, paragraphs, image: bool = False) -> Path:
    """A minimal hand-written .docx, 1 run per paragraph; optionally with word/media/image1.png (deflated)."""
    body = "".join(f'<w:p><w:r><w:t xml:space="preserve">{_esc(p)}</w:t></w:r></w:p>' for p in paragraphs)
    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           f'<w:document xmlns:w="{W_NS}"><w:body>{body}<w:sectPr/></w:body></w:document>')
    ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="xml" ContentType="application/xml"/>'
          '<Default Extension="png" ContentType="image/png"/>'
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
        z.writestr("word/document.xml", doc)
        if image:
            # large enough and compressible so that the entry is really deflated
            z.writestr("word/media/image1.png", PNG_1PX + b"\0" * 4096)
    return path


def docx_text(path) -> str:
    with zipfile.ZipFile(str(path)) as z:
        return z.read("word/document.xml").decode("utf-8")


def corrupt_entry(path, name: str) -> Path:
    """Break the deflate stream of one zip entry in place (first byte -> BTYPE 11, reserved)."""
    path = Path(path)
    with zipfile.ZipFile(str(path)) as z:
        info = z.getinfo(name)
    assert info.compress_type == zipfile.ZIP_DEFLATED, name
    data = bytearray(path.read_bytes())
    off = info.header_offset
    assert data[off:off + 4] == b"PK\x03\x04"
    n = int.from_bytes(data[off + 26:off + 28], "little")
    m = int.from_bytes(data[off + 28:off + 30], "little")
    start = off + 30 + n + m
    for i in range(min(8, info.compress_size)):
        data[start + i] = 0xFF
    path.write_bytes(bytes(data))
    with zipfile.ZipFile(str(path)) as z:           # sanity: the entry really is unreadable now
        with pytest.raises(Exception):
            z.read(name)
    return path


# ------------------------------------------------------------------------------------ pptx
def need_pptx():
    pytest.importorskip("pptx")
    pytest.importorskip("lxml")


def make_pptx(path, slides) -> Path:
    """slides: list of (title, body_text, notes_text or None), built with python-pptx (title+content layout)."""
    need_pptx()
    from pptx import Presentation
    from pptx.util import Inches

    prs = Presentation()
    for title, body, notes in slides:
        s = prs.slides.add_slide(prs.slide_layouts[5])        # title only
        s.shapes.title.text = title
        tb = s.shapes.add_textbox(Inches(1), Inches(2), Inches(6), Inches(1))
        tb.text_frame.text = body
        if notes is not None:
            s.notes_slide.notes_text_frame.text = notes
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(path))
    return path


def rewrite_parts(path, fn, pattern: str) -> Path:
    """Apply fn(lxml root) to every part whose name matches the regex `pattern`; rewrite the zip."""
    from lxml import etree

    path = Path(path)
    buf = io.BytesIO()
    with zipfile.ZipFile(str(path)) as zin, zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if re.fullmatch(pattern, info.filename):
                root = etree.fromstring(data)
                fn(root)
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
            zout.writestr(info.filename, data)
    path.write_bytes(buf.getvalue())
    return path


P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"p": P_NS, "a": A_NS}


def drop_notes_placeholder(root):
    """Remove the body placeholder (notes text) from a notes slide."""
    for sp in root.xpath("//p:sp[p:nvSpPr/p:nvPr/p:ph[@type='body']]", namespaces=NS):
        sp.getparent().remove(sp)


def drop_geometry(root):
    """Strip xfrm and preset geometry from every non-placeholder p:sp (a text box without geometry)."""
    for sp in root.xpath("//p:sp[not(p:nvSpPr/p:nvPr/p:ph)]", namespaces=NS):
        for spPr in sp.xpath("p:spPr", namespaces=NS):
            for child in list(spPr):
                spPr.remove(child)


def all_part_text(path, prefix: str) -> str:
    with zipfile.ZipFile(str(path)) as z:
        return "".join(z.read(n).decode("utf-8", "replace") for n in z.namelist() if n.startswith(prefix))


# ------------------------------------------------------------------------------------ misc
def content_slide(title, body, **kw):
    s = {"type": "content", "eyebrow": "Research", "title": title, "body": body,
         "notes": {"time": "0:30", "say": "a few words"}}
    s.update(kw)
    return s


def deck_spec(*slides, **meta):
    m = {"id": "r4"}
    m.update(meta)
    return {"meta": m, "slides": list(slides)}


def paper_txt(path, pages) -> Path:
    """§9 fetch text format."""
    return write(path, "".join(f"\n\n===== page {n} =====\n{body}" for n, body in enumerate(pages, 1)))


PAGE1 = ("Adaptive Tool Libraries for Research Agents\n"
         "Ada Lovelace, Alan Turing\n"
         "Abstract: we study tool libraries.\n")


def git_bash_form(p) -> str:
    """C:\\x\\y -> /c/x/y (Git Bash)."""
    s = str(p).replace("\\", "/")
    m = re.match(r"^([A-Za-z]):/(.*)$", s)
    assert m, s
    return f"/{m.group(1).lower()}/{m.group(2)}"


def can_symlink(tmp_path) -> bool:
    target = tmp_path / "_symtarget"
    target.write_text("x", encoding="utf-8")
    link = tmp_path / "_symlink"
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError, AttributeError):
        return False
    link.unlink()
    target.unlink()
    return True


def chmod_works(path, mode=0o640) -> bool:
    os.chmod(path, mode)
    return (os.stat(path).st_mode & 0o777) == mode


def python_env():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def run_into_closed_pipe(argv, reader_code="pass", timeout=60):
    """Run `python -m tundlekit ARGV` with stdout piped into a python process that exits at once.

    Returns (returncode, stderr text)."""
    reader = subprocess.Popen([sys.executable, "-c", reader_code], stdin=subprocess.PIPE,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    reader.wait(timeout=timeout)          # the reader is gone before the writer starts
    proc = subprocess.Popen([sys.executable, "-m", "tundlekit", *argv], stdout=reader.stdin,
                            stderr=subprocess.PIPE, cwd=str(REPO), env=python_env())
    reader.stdin.close()                  # the child holds the only write end; no reader remains
    _, err = proc.communicate(timeout=timeout)
    return proc.returncode, err.decode("utf-8", "replace")
