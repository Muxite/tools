"""Shared helpers for the round-4 misc tests (MANIFEST §16.6-§16.9).

Not a conftest. Test modules import it with `import helpers_r4m as h` (pytest puts tests/ on sys.path).
Nothing here imports tundlekit or an optional package at module level, so collection always succeeds.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import os
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"
GLOSSARY = REPO / "tundlekit" / "translate" / "data" / "glossary.tsv"

# §0.1 / §15.10: owning module of each tool used here
OWNER = {
    "papers_summary": "papers", "papers_index_check": "papers", "papers_peek": "papers",
    "translate_terms": "translate",
    "bundle_source": "bundle", "bundle_setup_table": "bundle", "bundle_lint": "bundle", "bundle_verify": "bundle",
    "diagram_render": "diagram", "diagram_validate": "diagram",
    "diagram_to_mermaid": "diagram", "diagram_from_mermaid": "diagram",
    "text_lint": "textlint",
}


# ------------------------------------------------------------------------------------ tool access
def call(name: str, **args):
    """Import the owning module, then registry.call (§1). Path values become strings."""
    importlib.import_module("tundlekit." + OWNER[name])
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


def check_shape(result):
    """§0.3 checker shape."""
    assert isinstance(result["ok"], bool)
    assert isinstance(result["findings"], list)
    for sev in ("error", "warning", "info"):
        assert result["counts"][sev] == sum(1 for f in result["findings"] if f["severity"] == sev)
    assert result["ok"] == (result["counts"]["error"] == 0)
    for f in result["findings"]:
        assert set(f) >= {"rule", "severity", "path", "line", "message", "excerpt"}
        assert "\\" not in f["path"]
    keys = [(f["path"], f["line"] or 0, f["rule"]) for f in result["findings"]]
    assert keys == sorted(keys)


def by_rule(result, rule):
    return [f for f in result["findings"] if f["rule"] == rule]


def rules(result):
    return [f["rule"] for f in result["findings"]]


def write(path, text: str = "") -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return path


def slash(p) -> str:
    return str(p).replace("\\", "/")


def norm(t: str) -> str:
    return t.replace("\r\n", "\n").strip("\n")


# ------------------------------------------------------------------------------------ bundle (§15.7, §16.6)
def installer(path, data: bytes = b"MZ fake installer\n", date=(2026, 3, 14)) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    ts = time.mktime(datetime(*date, 12, 0, 0).timetuple())
    os.utime(path, (ts, ts))
    return path


def sha256(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def heading(text: str) -> str:
    return norm(text).split("\n")[0]


def lint_tree(root: Path, files: dict) -> Path:
    for rel, text in files.items():
        write(Path(root) / rel, text)
    return Path(root)


def b003_paths(root) -> list:
    res = call("bundle_lint", root=str(root))
    return sorted(f["path"] for f in by_rule(res, "B003"))


# ------------------------------------------------------------------------------------ papers (§9, §15.8)
def marker_txt(path, pages) -> Path:
    return write(path, "".join(f"\n\n===== page {n} =====\n{body}" for n, body in enumerate(pages, 1)))


def paper_pages(page1, n_pages, refs_page=None, refs_line="References"):
    pages = [page1]
    for i in range(2, n_pages + 1):
        body = f"Section text on page {i}.\nMore words here.\n"
        if refs_page == i:
            body = f"Conclusion text.\n{refs_line}\n[1] Someone. A paper. 2024.\n"
        pages.append(body)
    return pages


def summary_lines(result) -> list:
    return norm(result["text"]).split("\n")


SUMMARY_BODY = ("## Summary\nText.\n\n## How it works (p2-4)\n- a\n\n## Results (p5)\n- b\n\n"
                "## Limitations\n- c\n\n## Relevance\nd\n")


def summary_file(papers_dir, pid: str, short: str, body: str = SUMMARY_BODY) -> Path:
    return write(Path(papers_dir) / "summaries" / f"{pid} - {short}.md",
                 f"# {pid} · {short}\n\nA. Author · arXiv {pid} · 10 pp (8 body)\nRead: p1-8\n\n{body}")


# ------------------------------------------------------------------------------------ translate (§16.6)
def approved_zh(en_term: str):
    """The approved zh renderings of a glossary row whose en alternatives include en_term (case-insensitive)."""
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) >= 6 and cols[5].strip() == "approved":
            if en_term.lower() in [a.strip().lower() for a in cols[0].split("|")]:
                return [z.strip() for z in cols[1].split("|") if z.strip()]
    return None


def term_count(result, term, index=0):
    """Count of a term (keys compared case-insensitively) in file `index`; 0 when the term is not a key."""
    for k, v in result["terms"].items():
        if k.lower() == term.lower():
            return v[index]
    return 0


def term_keys_lower(result):
    return {k.lower() for k in result["terms"]}


# ------------------------------------------------------------------------------------ SVG (§4, §16.7)
def tag(el) -> str:
    return el.tag.split("}", 1)[-1]


def svg_root(text: str):
    return ET.fromstring(text)


def svg_text(res, out=None) -> str:
    if res.get("svg"):
        return res["svg"]
    return Path(out or res["path"]).read_text(encoding="utf-8")


def group_frames(svg: str) -> dict:
    """{group id: (x0, y0, x1, y1)} from each `<g class="group">`'s first rect (§4.2)."""
    out = {}
    for g in svg_root(svg).iter():
        if tag(g) == "g" and "group" in (g.get("class") or "").split():
            rect = next(e for e in g.iter() if tag(e) == "rect")
            x, y = float(rect.get("x")), float(rect.get("y"))
            out[g.get("data-id")] = (x, y, x + float(rect.get("width")), y + float(rect.get("height")))
    return out


def boxes(res) -> dict:
    return {k: (v["x"], v["y"], v["x"] + v["w"], v["y"] + v["h"]) for k, v in res["nodes"].items()}


def overlap(a, b) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def same_band(a, b, axis=1) -> bool:
    """Boxes share a row (axis 1: y ranges overlap) or a column (axis 0)."""
    return a[axis] < b[axis + 2] and b[axis] < a[axis + 2]


def assert_layout_ok(res):
    b = boxes(res)
    for k, (x0, y0, x1, y1) in b.items():
        assert x0 >= -0.01 and y0 >= -0.01 and x1 <= res["width"] + 0.01 and y1 <= res["height"] + 0.01, k
    keys = list(b)
    for i, m in enumerate(keys):
        for n in keys[i + 1:]:
            assert not overlap(b[m], b[n]), (m, n)


def chain(n, prefix="a"):
    nodes = [{"id": f"{prefix}{i}", "label": f"step {i}"} for i in range(n)]
    edges = [{"from": f"{prefix}{i}", "to": f"{prefix}{i + 1}"} for i in range(n - 1)]
    return nodes, edges


FIXED_CONVERTERS = ("C:/Program Files/Inkscape", "C:/Program Files (x86)/Inkscape", "/Applications/Inkscape.app",
                    "/usr/bin/inkscape", "/usr/bin/rsvg-convert", "/opt/homebrew/bin/rsvg-convert",
                    "/usr/local/bin/rsvg-convert")


def only_pymupdf(monkeypatch, tmp_path):
    """Hide cairosvg and PATH converters so the pymupdf fallback (§14.6) is used; skip without pymupdf."""
    pytest.importorskip("pymupdf")
    for p in FIXED_CONVERTERS:
        if Path(p).exists():
            pytest.skip(f"a converter is installed at a fixed location: {p}")
    monkeypatch.setitem(sys.modules, "cairosvg", None)
    monkeypatch.setenv("PATH", "")
    monkeypatch.chdir(tmp_path)


def spy_pymupdf(monkeypatch):
    """Record every SVG document handed to pymupdf.open (the pre-raster SVG)."""
    import pymupdf

    seen = []
    real = pymupdf.open

    def spy(*a, **k):
        data = k.get("stream", a[0] if a and isinstance(a[0], (bytes, bytearray, str)) else None)
        if isinstance(data, (bytes, bytearray)):
            data = bytes(data).decode("utf-8", "replace")
        if isinstance(data, str) and "<svg" in data:
            seen.append(data)
        elif isinstance(data, str) and data.lower().endswith(".svg") and Path(data).is_file():
            seen.append(Path(data).read_text(encoding="utf-8"))
        return real(*a, **k)

    monkeypatch.setattr(pymupdf, "open", spy)
    if "fitz" in sys.modules and getattr(sys.modules["fitz"], "open", None) is real:
        monkeypatch.setattr(sys.modules["fitz"], "open", spy)
    return seen


def dark_pixels_near_arrow_tip(png, tip_x, mid_y, scale=None, width=None):
    """Dark pixels beside (not on) a horizontal edge line, 5-7 units before its end: only an arrowhead puts ink
    there."""
    import pymupdf

    pix = pymupdf.Pixmap(str(png))
    s = scale or (pix.width / width)
    n = 0
    for sx in range(int((tip_x - 7) * s), int((tip_x - 5) * s) + 1):
        for off in (1.3, 1.8, 2.2):
            for sy in (int((mid_y - off) * s), int((mid_y + off) * s)):
                if 0 <= sx < pix.width and 0 <= sy < pix.height and min(pix.pixel(sx, sy)[:3]) < 200:
                    n += 1
    return n


# ------------------------------------------------------------------------------------ text lint (§7, §16.8)
def lint(tmp_path, body: str, name="notes.md", **kw):
    p = write(Path(tmp_path) / name, body)
    res = call("text_lint", paths=[str(p)], **kw)
    check_shape(res)
    return res


def lines_of(result, rule) -> list:
    return [f["line"] for f in by_rule(result, rule)]


# ------------------------------------------------------------------------------------ skills (§11, §16.9)
def skill_text(name: str, with_refs: bool = True) -> str:
    root = SKILLS_DIR / name
    files = [root / "SKILL.md"]
    if with_refs:
        files += sorted((root / "references").glob("*.md"))
    return "\n".join(f.read_text(encoding="utf-8") for f in files if f.is_file())
