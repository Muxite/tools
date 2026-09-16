"""Helpers for the diagram (MANIFEST §4) and textlint (MANIFEST §7) test modules.

Not a conftest: other suites share tests/. tundlekit is imported lazily so collection succeeds
before the package is implemented.
"""
from __future__ import annotations

import importlib
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

SVG_NS = "http://www.w3.org/2000/svg"
NS = {"s": SVG_NS}
SHAPE_TAGS = {"rect", "path", "polygon", "ellipse", "circle", "polyline"}
FINDING_KEYS = {"rule", "severity", "path", "line", "message", "excerpt"}


# ----------------------------------------------------------------------------- tool access
def _call(module: str, name: str, args: dict) -> dict:
    importlib.import_module(f"tundlekit.{module}")
    from tundlekit import registry

    return registry.call(name, args)


def diagram(name: str, **args) -> dict:
    """Call a §4 tool (diagram_render, diagram_validate, diagram_from_mermaid, diagram_to_mermaid)."""
    return _call("diagram", name, args)


def text(name: str, **args) -> dict:
    """Call a §7 tool (text_lint, text_fignums, text_wordcount)."""
    return _call("textlint", name, args)


def tool_error():
    from tundlekit.registry import ToolError

    return ToolError


def cli(capsys, argv):
    """Run tundlekit.cli.main(argv); return (exit_code, stdout, stderr)."""
    from tundlekit import cli as cli_mod

    capsys.readouterr()
    code = cli_mod.main(list(argv))
    out = capsys.readouterr()
    return code, out.out, out.err


def cli_json(capsys, argv):
    code, out, err = cli(capsys, argv)
    return code, json.loads(out), err


# ----------------------------------------------------------------------------- palette
def stage_colour(stage: str) -> str:
    from tundlekit.palette import STAGE

    return STAGE[stage].lower()


def tint(colour: str, amount: float) -> str:
    from tundlekit.palette import tint as t

    return t(colour, amount).lower()


# ----------------------------------------------------------------------------- SVG
def tag(el) -> str:
    return el.tag.split("}", 1)[-1]


def parse_svg(svg_text: str):
    return ET.fromstring(svg_text)


def attr(el, name: str):
    """An attribute value, falling back to the inline style property of the same name."""
    v = el.get(name)
    if v is not None:
        return v.strip()
    style = el.get("style") or ""
    for part in style.split(";"):
        if ":" in part:
            k, val = part.split(":", 1)
            if k.strip() == name:
                return val.strip()
    return None


def groups_with_class(root, cls: str):
    return [g for g in root.iter() if tag(g) == "g" and cls in (g.get("class") or "").split()]


def node_group(root, node_id: str):
    found = [g for g in groups_with_class(root, "node") if g.get("data-id") == node_id]
    assert len(found) == 1, f"expected 1 node group for {node_id!r}, found {len(found)}"
    return found[0]


def shapes(el):
    return [e for e in el.iter() if tag(e) in SHAPE_TAGS]


def texts(el):
    """Text content of every <text> (joined) and every <tspan>, stripped."""
    out = []
    for e in el.iter():
        if tag(e) == "text":
            out.append("".join(e.itertext()).strip())
        if tag(e) in ("text", "tspan") and e.text:
            out.append(e.text.strip())
    return out


def tag_texts(el):
    return ["".join(e.itertext()).strip() for e in el.iter()
            if tag(e) == "text" and "tag" in (e.get("class") or "").split()]


_TRANSLATE = re.compile(r"^\s*translate\(\s*([-\d.eE]+)(?:[\s,]+([-\d.eE]+))?\s*\)\s*$")


def absolute_offset(root, el):
    """Sum of translate() transforms on el's ancestors (and el). Skips the test for other transforms."""
    parents = {c: p for p in root.iter() for c in p}
    dx = dy = 0.0
    cur = el
    while cur is not None:
        tr = cur.get("transform")
        if tr:
            m = _TRANSLATE.match(tr)
            if not m:
                pytest.skip(f"cannot evaluate transform {tr!r}")
            dx += float(m.group(1))
            dy += float(m.group(2) or 0)
        cur = parents.get(cur)
    return dx, dy


def num(v) -> float:
    return float(re.match(r"\s*([-\d.eE]+)", str(v)).group(1))


def boxes(result: dict):
    """{id: (x0, y0, x1, y1)} from a diagram_render result (x, y taken as the top-left corner)."""
    return {k: (v["x"], v["y"], v["x"] + v["w"], v["y"] + v["h"]) for k, v in result["nodes"].items()}


def overlap(a, b) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def inside(inner, outer, eps=0.01) -> bool:
    return (inner[0] >= outer[0] - eps and inner[1] >= outer[1] - eps
            and inner[2] <= outer[2] + eps and inner[3] <= outer[3] + eps)


def rect_box(root, rect):
    dx, dy = absolute_offset(root, rect)
    x = num(rect.get("x", 0)) + dx
    y = num(rect.get("y", 0)) + dy
    return (x, y, x + num(rect.get("width")), y + num(rect.get("height")))


def spec_of(nodes, edges=(), **extra):
    """Build a spec from compact node tuples (id, label, stage, actor) or dicts."""
    out = []
    for n in nodes:
        if isinstance(n, dict):
            out.append(n)
        else:
            d = {"id": n[0], "label": n[1]}
            if len(n) > 2 and n[2]:
                d["stage"] = n[2]
            if len(n) > 3 and n[3]:
                d["actor"] = n[3]
            out.append(d)
    es = []
    for e in edges:
        es.append(e if isinstance(e, dict) else {"from": e[0], "to": e[1]})
    spec = {"nodes": out, "edges": es}
    spec.update(extra)
    return spec


# ----------------------------------------------------------------------------- findings
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


def rules(res: dict, rule: str | None = None):
    """[(rule, line)] of all findings, or [line] of one rule's findings."""
    if rule is None:
        return [(f["rule"], f["line"]) for f in res["findings"]]
    return [f["line"] for f in res["findings"] if f["rule"] == rule]


def lint_text(tmp_path, monkeypatch, body: str, name: str = "report.md", **kw) -> dict:
    """Write body to tmp_path/name, chdir there, run text_lint on the relative path."""
    monkeypatch.chdir(tmp_path)
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    res = text("text_lint", paths=[name], **kw)
    assert_checker_shape(res)
    return res


def write(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


# ----------------------------------------------------------------------------- git
def git_available() -> bool:
    return shutil.which("git") is not None


def git_env(monkeypatch, tmp_path: Path):
    cfg = tmp_path / "empty-gitconfig"
    cfg.write_text("", encoding="utf-8")
    for k, v in {
        "GIT_AUTHOR_NAME": "Test Author", "GIT_AUTHOR_EMAIL": "author@example.com",
        "GIT_COMMITTER_NAME": "Test Author", "GIT_COMMITTER_EMAIL": "author@example.com",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": str(cfg),
    }.items():
        monkeypatch.setenv(k, v)


def git(repo: Path, *args: str) -> str:
    cp = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)
    return cp.stdout


def init_repo(monkeypatch, tmp_path: Path) -> Path:
    if not git_available():
        pytest.skip("git not installed")
    git_env(monkeypatch, tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    return repo


def commit_all(repo: Path, msg: str = "commit"):
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", msg)
