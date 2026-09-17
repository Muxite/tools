"""Shared helpers for the round-6 papers page / Office guard / docs / registration tests (MANIFEST §18.3-§18.6).

Not a conftest. Test modules import it with `import helpers_r6g as h` (pytest puts tests/ on sys.path).
Nothing here imports tundlekit or an optional package at module level, so collection always succeeds.
"""
from __future__ import annotations

import importlib
import json
import os
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(os.environ.get("TUNDLEKIT_REPO") or Path(__file__).resolve().parent.parent)
SKILLS_DIR = REPO / "skills"

# §0.1 / §18.6: owning module of each tool used here
OWNER = {"papers_page": "papers", "report_build": "report", "deck_pack": "deck",
         "text_apply_edits": "textlint", "bundle_backup": "bundle", "claims_trace": "claims"}


# ------------------------------------------------------------------------------------ tool access
def call(name: str, **args):
    importlib.import_module("tundlekit." + OWNER[name])
    from tundlekit import registry

    clean = {k: (str(v) if isinstance(v, Path) else
                 [str(x) if isinstance(x, Path) else x for x in v] if isinstance(v, list) else v)
             for k, v in args.items()}
    return registry.call(name, clean)


def tool_error():
    return importlib.import_module("tundlekit.registry").ToolError


def run_cli(capsys, argv):
    """tundlekit.cli.main in-process (§0.4) -> (code, parsed JSON or None, stdout, stderr)."""
    from tundlekit import cli

    capsys.readouterr()
    try:
        code = cli.main([str(a) for a in argv])
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 2)
    out, err = capsys.readouterr()
    try:
        return code, json.loads(out), out, err
    except ValueError:
        return code, None, out, err


def write(path, text: str = "") -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return path


# ------------------------------------------------------------------------------------ Office guard (§18.4)
def office_stub(monkeypatch, default=(), all_apps=()):
    """Stub render.office_running; returns the list of all_apps values it receives (`default`/`all_apps` names)."""
    from tundlekit import render

    calls = []

    def stub(*a, **k):
        flag = bool(k["all_apps"]) if "all_apps" in k else bool(a[0]) if a else False
        calls.append(flag)
        return list(all_apps if flag else default)

    monkeypatch.setattr(render, "office_running", stub)
    return calls


_PKG = "http://schemas.openxmlformats.org/package/2006/"
_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def make_docx(path, paragraphs) -> Path:
    """A minimal hand-written .docx with 1 run per paragraph."""
    from xml.sax.saxutils import escape

    body = "".join(f'<w:p><w:r><w:t xml:space="preserve">{escape(p)}</w:t></w:r></w:p>' for p in paragraphs)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", f'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="{_PKG}content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" '
                   'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                   '</Types>')
        z.writestr("_rels/.rels", f'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{_PKG}relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/'
                   'officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr("word/document.xml", f'<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="{_W}">'
                   f'<w:body>{body}<w:sectPr/></w:body></w:document>')
    return path


# ------------------------------------------------------------------------------------ papers page inputs (§18.3)
def summary_text(pid, title, sections, meta=("Doe, Roe · Lab · arXiv 1 Jan 2026 · 10 pp (6 body)",
                                             "Read: p1-6"), sep="·") -> str:
    """A summary in the INDEX format (§15.8). sections: [(heading, body)]."""
    out = [f"# {pid} {sep} {title}", ""] + list(meta) + [""]
    for head, body in sections:
        out += [f"## {head}", body.rstrip("\n"), ""]
    return "\n".join(out)


def summary(papers, pid, short, title, sections, **kw) -> Path:
    stem = pid.replace("/", "_")
    return write(Path(papers) / "summaries" / f"{stem} - {short}.md", summary_text(pid, title, sections, **kw))


def simple_sections(word):
    return [("Summary", f"{word} summary text."), ("How it works", f"- {word} mechanism"),
            ("Results", f"- {word} result"), ("Limitations", f"- {word} limit"), ("Relevance", f"- {word} use")]


def index_text(groups, preamble="3 summaries, one per paper text.") -> str:
    """groups: [(heading line after '## ', [row first cells])]."""
    out = ["# Paper summaries: index", "", preamble, ""]
    for head, rows in groups:
        out.append(f"## {head}")
        out += ["| Paper | One line |", "|---|---|"]
        out += [f"| {r} | one line about it |" for r in rows]
        out.append("")
    return "\n".join(out)


def build(papers, report, out, **kw):
    return call("papers_page", report=str(report), out=str(out), dir=str(papers), **kw)


# ------------------------------------------------------------------------------------ HTML reading
VOID = {"meta", "input", "br", "img", "link", "hr", "source", "wbr", "col", "area", "base", "embed"}


class Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs), parent, []

    @property
    def classes(self):
        return (self.attrs.get("class") or "").split()

    def text(self) -> str:
        return "".join(c if isinstance(c, str) else c.text() for c in self.children)

    def clean(self) -> str:
        return " ".join(self.text().split())

    def elements(self):
        for c in self.children:
            if isinstance(c, Node):
                yield c
                yield from c.elements()

    def find_all(self, tag=None, cls=None, id=None):
        return [e for e in self.elements() if (tag is None or e.tag == tag)
                and (cls is None or cls in e.classes) and (id is None or e.attrs.get("id") == id)]

    def find(self, tag=None, cls=None, id=None):
        found = self.find_all(tag, cls, id)
        return found[0] if found else None

    def kids(self, tag=None):
        return [c for c in self.children if isinstance(c, Node) and (tag is None or c.tag == tag)]


class _Builder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", {}, None)
        self.stack = [self.root]
        self.decls = []

    def handle_decl(self, decl):
        self.decls.append(decl)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node(tag, attrs, self.stack[-1]))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def parse(html: str) -> Node:
    b = _Builder()
    b.feed(html)
    b.close()
    b.root.decls = b.decls
    return b.root


def page(out) -> tuple:
    """(raw text, parsed root) of a built page."""
    return Path(out).read_bytes().decode("utf-8"), parse(Path(out).read_bytes().decode("utf-8"))


def articles(root) -> list:
    return [a.attrs.get("id") for a in root.find_all("article", cls="paper")]


def card(root, pid):
    return root.find("article", id="p-" + re.sub(r"[./]", "-", pid))


def groups(root) -> list:
    """[(section id, h2 text, [article ids])] in page order."""
    out = []
    for s in root.find_all("section", cls="group"):
        h2 = s.find("h2")
        out.append((s.attrs.get("id"), h2.clean() if h2 else None,
                    [a.attrs.get("id") for a in s.find_all("article", cls="paper")]))
    return out


def details_labels(art) -> list:
    return [(d.find("summary").clean(), "open" in d.attrs) for d in art.kids("details")]


# ------------------------------------------------------------------------------------ docs (§18.5)
def skill(name: str) -> str:
    root = SKILLS_DIR / name
    files = [root / "SKILL.md"] + sorted((root / "references").glob("*.md"))
    return "\n".join(f.read_text(encoding="utf-8") for f in files if f.is_file())


def section(text: str, title: str) -> str:
    """The body of the `## {title}` section (up to the next level-2 heading); '' when absent."""
    m = re.search(rf"^## {re.escape(title)}[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""
