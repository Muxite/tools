"""Shared helpers for the review/xref/claims/apply-edits tests (MANIFEST §15.1, §15.2, §15.3, §15.5, §15.10).

Not a conftest (other suites write into tests/ in parallel). Import with `import helpers_r3rc as r3`.
Nothing here imports tundlekit at module level: each tool module (`tundlekit.review`, `tundlekit.claims`,
`tundlekit.textlint`) is imported lazily, so collection succeeds before the tools exist.
"""
from __future__ import annotations

import importlib
import json
import re
import zipfile
from pathlib import Path

FINDING_KEYS = {"rule", "severity", "path", "line", "message", "excerpt"}


# ------------------------------------------------------------------ tool access (§0.2, §1)
def call(module: str, name: str, **args) -> dict:
    """Import tundlekit.<module> (which registers its tools), then run registry.call."""
    importlib.import_module(f"tundlekit.{module}")
    from tundlekit import registry

    args = {k: (str(v) if isinstance(v, Path) else v) for k, v in args.items()}
    return registry.call(name, args)


def review(**args) -> dict:
    return call("review", "review_coverage", **args)


def claims(**args) -> dict:
    return call("claims", "claims_trace", **args)


def xref(**args) -> dict:
    return call("textlint", "text_xref", **args)


def apply_edits(**args) -> dict:
    return call("textlint", "text_apply_edits", **args)


def tool_error():
    from tundlekit.registry import ToolError

    return ToolError


def get_tool(module: str, name: str):
    importlib.import_module(f"tundlekit.{module}")
    from tundlekit import registry

    return registry.TOOLS[name]


def run_cli(capsys, argv):
    """tundlekit.cli.main(argv) in-process (§0.4). Returns (code, parsed JSON or None, stdout, stderr)."""
    from tundlekit import cli

    capsys.readouterr()
    try:
        code = cli.main([str(a) for a in argv])
    except SystemExit as exc:  # argparse usage errors / --help
        code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 2)
    out, err = capsys.readouterr()
    data = None
    if out.strip():
        try:
            data = json.loads(out)
        except ValueError:
            data = None
    return code, data, out, err


# ------------------------------------------------------------------ findings (§0.3)
def assert_checker_shape(res: dict):
    assert isinstance(res["ok"], bool)
    assert set(res["counts"]) >= {"error", "warning", "info"}
    for f in res["findings"]:
        assert set(f) >= FINDING_KEYS, f
        assert f["severity"] in ("error", "warning", "info")
        assert f["line"] is None or (isinstance(f["line"], int) and f["line"] >= 1)
        assert "\\" not in f["path"]
    for sev in ("error", "warning", "info"):
        assert res["counts"][sev] == sum(1 for f in res["findings"] if f["severity"] == sev)
    assert res["ok"] == (res["counts"]["error"] == 0)
    keys = [(f["path"], f["line"] or 0, f["rule"]) for f in res["findings"]]
    assert keys == sorted(keys)


def of(res: dict, rule: str) -> list:
    return [f for f in res["findings"] if f["rule"] == rule]


def sec(s) -> str:
    """A section id with any leading `§` and trailing `.` removed (the manifest does not pin the spelling)."""
    return str(s).strip().lstrip("§").strip().rstrip(".")


# ------------------------------------------------------------------ files
def write(path: Path, text: str) -> Path:
    """Write text exactly (no newline translation), UTF-8."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


def read(path: Path) -> str:
    return Path(path).read_bytes().decode("utf-8")


def write_paper(dirpath: Path, paper_id: str, pages) -> Path:
    """§9 fetch text format: for each page N, '\\n\\n===== page N =====\\n' + text."""
    text = "".join(f"\n\n===== page {n} =====\n{body}" for n, body in enumerate(pages, 1))
    return write(Path(dirpath) / f"{paper_id}.txt", text)


def write_paper_ff(dirpath: Path, paper_id: str, pages) -> Path:
    """pdftotext-style text: pages separated by form feeds (§9)."""
    return write(Path(dirpath) / f"{paper_id}.txt", "\f".join(pages) + "\f")


# ------------------------------------------------------------------ decks (§3)
def content(title: str, source: str | None = None, body=None, **extra) -> dict:
    s = {"type": "content", "title": title, "notes": {"time": "0:30", "say": "word " * 25}}
    if source is not None:
        s["source"] = source
    if body is not None:
        s["body"] = body
    s.update(extra)
    return s


def lines(*items) -> dict:
    return {"kind": "lines", "items": list(items)}


def write_spec(path: Path, slides, meta=None) -> Path:
    spec = {"meta": meta or {"id": "capsule"}, "slides": slides}
    return write(path, json.dumps(spec, indent=2, ensure_ascii=False))


def build_pptx(spec_path: Path, out: Path) -> Path:
    """Build a .pptx from a spec with tundlekit's own deck_build (§3.2)."""
    call("deck", "deck_build", spec_path=str(spec_path), out=str(out))
    return out


# ------------------------------------------------------------------ docx (§15.5)
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def make_docx(path: Path, paragraphs, extra_parts: dict | None = None) -> Path:
    """A minimal .docx written by hand. paragraphs: list of (style_id or None, [run texts]).

    The 2nd run of each paragraph is bold, so runs differ in formatting as in real documents.
    extra_parts: {zip name: bytes} added to the package (styles, media, docProps...).
    """
    body = []
    for style, runs in paragraphs:
        ppr = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
        rs = "".join(f'<w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">{_esc(r)}</w:t></w:r>'
                     if i == 1 else f'<w:r><w:t xml:space="preserve">{_esc(r)}</w:t></w:r>'
                     for i, r in enumerate(runs))
        body.append(f"<w:p>{ppr}{rs}</w:p>")
    document = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<w:document xmlns:w="{W_NS}"><w:body>{"".join(body)}<w:sectPr/></w:body></w:document>')
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
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
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", document)
        for name, data in (extra_parts or {}).items():
            z.writestr(name, data)
    return path


def docx_parts(path: Path) -> dict:
    with zipfile.ZipFile(str(path)) as z:
        return {n: z.read(n) for n in z.namelist()}


def docx_runs(path: Path) -> list:
    """[[run text, ...] per paragraph] from word/document.xml."""
    import xml.etree.ElementTree as ET

    root = ET.fromstring(docx_parts(path)["word/document.xml"])
    w = "{%s}" % W_NS
    out = []
    for p in root.iter(w + "p"):
        out.append(["".join(t.text or "" for t in r.iter(w + "t")) for r in p.iter(w + "r")])
    return out


def docx_paragraphs(path: Path) -> list:
    return ["".join(r) for r in docx_runs(path)]


EXTRA_PARTS = {
    "word/styles.xml": ('<?xml version="1.0" encoding="UTF-8"?>'
                        f'<w:styles xmlns:w="{W_NS}"><w:style w:styleId="Heading1"/></w:styles>').encode(),
    "docProps/core.xml": b'<?xml version="1.0"?><cp:coreProperties xmlns:cp="urn:x">Report</cp:coreProperties>',
    "word/media/image1.png": bytes(range(256)) * 4,
}


def n_applied(value) -> int:
    """`applied` may be a count or a list of applied edits; the manifest does not pin which."""
    return value if isinstance(value, int) else len(value)


def crlf_only(data: bytes) -> bool:
    return b"\n" in data and re.search(rb"(?<!\r)\n", data) is None
