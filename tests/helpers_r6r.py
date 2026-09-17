"""Shared helpers for the round-6 `report_build` tests (MANIFEST §18.1, §18.4, §18.6).

Not a conftest: test modules do `import helpers_r6r as h`. Nothing imports tundlekit at module level, so the
suite collects before `tundlekit/report.py` exists. Pillow is used only to make test figures.
"""
from __future__ import annotations

import importlib
import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pytest

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = "{%s}" % W_NS
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
NS = {"w": W_NS, "wp": WP[1:-1], "dc": "http://purl.org/dc/elements/1.1/",
      "dcterms": "http://purl.org/dc/terms/",
      "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"}
OWNER = {"report_build": "report", "docx_diff": "textlint", "text_apply_edits": "textlint",
         "render_office": "render"}
NOW = "2026-09-16T10:00"
PARTS = ["[Content_Types].xml", "_rels/.rels", "docProps/core.xml", "docProps/app.xml", "word/document.xml",
         "word/styles.xml", "word/settings.xml", "word/numbering.xml", "word/footer1.xml",
         "word/_rels/document.xml.rels"]


# ------------------------------------------------------------------------------------ calling tools
def call(name, **args):
    """Import the owning module lazily (§18.6), then registry.call (§1). Paths become strings."""
    importlib.import_module("tundlekit." + OWNER[name])
    clean = {k: (str(v) if isinstance(v, Path) else v) for k, v in args.items()}
    return importlib.import_module("tundlekit.registry").call(name, clean)


def tool_error():
    return importlib.import_module("tundlekit.registry").ToolError


def build(report, out=None, **kw):
    out = out if out is not None else Path(report).with_name("out.docx")
    return call("report_build", report=report, out=out, **kw)


def build_error(report, out=None, **kw) -> str:
    with pytest.raises(tool_error()) as exc:
        build(report, out, **kw)
    return str(exc.value)


def run_cli(capsys, argv):
    """tundlekit.cli.main in-process (§0.4): (code, parsed JSON or None, stdout, stderr)."""
    from tundlekit import cli

    capsys.readouterr()
    try:
        code = cli.main([str(a) for a in argv])
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 2
    out, err = capsys.readouterr()
    try:
        data = json.loads(out) if out.strip() else None
    except ValueError:
        data = None
    return code, data, out, err


def no_office(monkeypatch, running=(), seen=None):
    """§18.4: replace tundlekit.render.office_running; record the all_apps values it receives."""
    from tundlekit import render

    def stub(all_apps=False):
        if seen is not None:
            seen.append(all_apps)
        return list(running(all_apps) if callable(running) else running)

    monkeypatch.setattr(render, "office_running", stub)


# ------------------------------------------------------------------------------------ writing inputs
def write(path, text: str = "", newline="\n") -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline=newline) as f:
        f.write(text)
    return path


def png(path, w=40, h=20, color=(40, 90, 160)) -> Path:
    from PIL import Image

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (w, h), color).save(path, format="PNG")
    return path


def jpeg(path, w=30, h=45) -> Path:
    from PIL import Image

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (w, h), (200, 60, 30)).save(path, format="JPEG")
    return path


def report(folder, body: str, name="REPORT.md") -> Path:
    return write(Path(folder) / name, body)


# ------------------------------------------------------------------------------------ rich sample
# Modelled on report-general/REPORT.md and report-capsules/REPORT.md; uses only §18.1.1 constructs, with
# blank lines around quotes and figures, so A1 applies (§18.1.4).
RICH = """---
title: ignored front matter
---
# AI4Research: Workflow **and** Platform

Muk Chunpongtong · September 2026

This report covers 3 subjects:

- How the workflow turns a request into *checked* evidence
- How it compares with the `state of the art`
  - nested detail with snake_case_name kept
- Which platform the work moves to

Code claims were read in the source at pinned commits,
and paper claims were read in the [cited paper](https://arxiv.org/abs/2504.08066).
<!-- a hidden
reviewer note -->

---

## 1. The goal: 3 claims

> LLMs interpret semantics; deterministic code validates structure,
> maintains references and schedules.

| Term | Meaning |
|---|---|
| capsule | A contract for 1 capability, written in YAML with typed inputs and outputs |
| gate | A check that decides **PASS** or FAIL |

*Table 1. The terms the report rests on.*

![Fig. 1. The workflow [2, Fig. 1]. Tinted boxes are model calls.](build/fig/fig-workflow.png)

### 1.1 Order of work

1. Pinning a version on every capsule id
2. Adding the generalist capsule behind a flag,
   with a gap record for every node
3. Measuring how often the gate rejects

Node 114 removed the logging:

```
- output_ls.extend([
-     {TOOL_USED_MARKER: tool_name},
+ output_ls.append({"tool_invocation": {...}})
```

![Fig. 2. A photo figure.](deck-src/photo.jpg)

\\pagebreak

## Appendix A. Sources

Escaped \\*stars\\* and a \\| pipe stay as text, and ***both*** styles work.
"""


def rich(folder) -> Path:
    """REPORT.md with a 400x300 PNG and a 30x45 JPEG figure."""
    folder = Path(folder)
    png(folder / "build" / "fig" / "fig-workflow.png", 400, 300)
    jpeg(folder / "deck-src" / "photo.jpg", 30, 45)
    return report(folder, RICH)


# ------------------------------------------------------------------------------------ reading the package
def names(docx) -> list:
    with zipfile.ZipFile(docx) as z:
        return z.namelist()


def part(docx, name) -> bytes:
    with zipfile.ZipFile(docx) as z:
        return z.read(name)


def xml(docx, name="word/document.xml"):
    return ET.fromstring(part(docx, name))


def body(docx):
    return xml(docx).find("w:body", NS)


def style_id(p):
    s = p.find("w:pPr/w:pStyle", NS)
    return s.get(W + "val") if s is not None else None


def ptext(p) -> str:
    """Run text: w:t, run-level w:tab -> \\t, w:br -> \\n (page break -> \\f) (§16.3, §17.1)."""
    out = []
    for r in p.iter(W + "r"):
        for el in r:
            if el.tag == W + "t":
                out.append(el.text or "")
            elif el.tag == W + "tab":
                out.append("\t")
            elif el.tag == W + "br":
                out.append("\f" if el.get(W + "type") == "page" else "\n")
    return "".join(out)


def paras(docx) -> list:
    """Direct w:p children of w:body as (style id or None, text, element)."""
    return [(style_id(p), ptext(p), p) for p in body(docx) if p.tag == W + "p"]


def styled(docx, style) -> list:
    return [t for s, t, _ in paras(docx) if s == style]


def texts(docx) -> list:
    """Non-empty direct body paragraph texts."""
    return [t for _, t, _ in paras(docx) if t.strip()]


def tables(docx) -> list:
    return [t for t in body(docx) if t.tag == W + "tbl"]


def cell_texts(tbl) -> list:
    return [[ptext(tc) for tc in tr.findall("w:tc", NS)] for tr in tbl.findall("w:tr", NS)]


def core(docx) -> dict:
    root = xml(docx, "docProps/core.xml")
    get = lambda q: (root.find(q, NS).text or "") if root.find(q, NS) is not None else None  # noqa: E731
    return {"title": get("dc:title"), "creator": get("dc:creator"), "last": get("cp:lastModifiedBy"),
            "created": get("dcterms:created"), "modified": get("dcterms:modified")}


def diff(a, b) -> list:
    return call("docx_diff", old=a, new=b)["changes"]


# ------------------------------------------------------------------------------------ effective formatting
class Styles:
    """Resolve effective run/paragraph properties: direct -> character style -> paragraph style chain ->
    docDefaults (§18.1.2 pins values, not where they are stored)."""

    def __init__(self, docx):
        root = xml(docx, "word/styles.xml")
        self.by_id = {s.get(W + "styleId"): s for s in root.findall("w:style", NS)}
        self.default_p = next((s.get(W + "styleId") for s in root.findall("w:style", NS)
                               if s.get(W + "type") == "paragraph" and s.get(W + "default") in ("1", "true")), None)
        self.defaults = root.find("w:docDefaults", NS)

    def chain(self, sid):
        seen = set()
        while sid and sid in self.by_id and sid not in seen:
            seen.add(sid)
            yield self.by_id[sid]
            based = self.by_id[sid].find("w:basedOn", NS)
            sid = based.get(W + "val") if based is not None else None

    def _first(self, holders, path, attr):
        for h in holders:
            el = h.find(path, NS) if h is not None else None
            if el is not None and (attr is None or el.get(W + attr) is not None):
                return el if attr is None else el.get(W + attr)
        return None

    def ppr(self, p, tag, attr="val", style=None):
        sid = style or (style_id(p) if p is not None else None) or self.default_p
        holders = ([p.find("w:pPr", NS)] if p is not None else []) + [s.find("w:pPr", NS) for s in self.chain(sid)]
        if self.defaults is not None:
            holders.append(self.defaults.find("w:pPrDefault/w:pPr", NS))
        return self._first(holders, "w:" + tag, attr)

    def rpr(self, r, p, tag, attr="val", style=None):
        holders = []
        if r is not None:
            holders.append(r.find("w:rPr", NS))
            rs = r.find("w:rPr/w:rStyle", NS)
            if rs is not None:
                holders += [s.find("w:rPr", NS) for s in self.chain(rs.get(W + "val"))]
        sid = style or (style_id(p) if p is not None else None) or self.default_p
        holders += [s.find("w:rPr", NS) for s in self.chain(sid)]
        if self.defaults is not None:
            holders.append(self.defaults.find("w:rPrDefault/w:rPr", NS))
        return self._first(holders, "w:" + tag, attr)

    def on(self, r, p, tag, style=None) -> bool:
        el = self.rpr(r, p, tag, attr=None, style=style)
        return el is not None and el.get(W + "val", "1").lower() not in ("0", "false", "off")

    def size(self, r, p, style=None):
        v = self.rpr(r, p, "sz", style=style)
        return int(v) if v is not None else None

    def font(self, r, p, style=None):
        return self.rpr(r, p, "rFonts", "ascii", style=style)


def runs(p) -> list:
    """(text, run element) for runs holding text."""
    out = []
    for r in p.iter(W + "r"):
        t = "".join((x.text or "") for x in r.findall("w:t", NS))
        if t:
            out.append((t, r))
    return out


def run_with(p, text):
    for t, r in runs(p):
        if text in t:
            return r
    raise AssertionError(f"no run holding {text!r} in {ptext(p)!r}")
