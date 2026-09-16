"""MANIFEST §4 via the CLI (§0.4): diagram render / validate / from-mermaid / to-mermaid with --json."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers_diagram_text import cli, cli_json, parse_svg  # noqa: E402

SPEC = {"title": "t", "nodes": [{"id": "a", "label": "A", "actor": "model"}, {"id": "b", "label": "B"}],
        "edges": [{"from": "a", "to": "b"}]}


def test_cli_render_writes_svg(tmp_path, capsys):
    sp = tmp_path / "s.json"
    sp.write_text(json.dumps(SPEC), encoding="utf-8")
    out = tmp_path / "o.svg"
    code, res, _ = cli_json(capsys, ["diagram", "render", str(sp), "-o", str(out), "--json"])
    assert code == 0
    assert res["path"] == str(out)
    root = parse_svg(out.read_text(encoding="utf-8"))
    assert float(root.get("width")) == res["width"]


def test_cli_render_invalid_spec_is_error(tmp_path, capsys):
    sp = tmp_path / "bad.json"
    sp.write_text(json.dumps({"nodes": [{"id": "a", "label": "A", "stage": "nope"}]}), encoding="utf-8")
    code, out, err = cli(capsys, ["diagram", "render", str(sp), "--json"])
    assert code == 1
    assert "nodes[0].stage" in json.loads(out)["error"]
    assert err.startswith("tundlekit: ")


def test_cli_validate_reports_problems(tmp_path, capsys):
    sp = tmp_path / "bad.json"
    sp.write_text(json.dumps({"nodes": [{"id": "a", "label": ""}]}), encoding="utf-8")
    _, res, _ = cli_json(capsys, ["diagram", "validate", str(sp), "--json"])
    assert res["ok"] is False and res["problems"]


def test_cli_from_and_to_mermaid(tmp_path, capsys):
    mmd = tmp_path / "d.mmd"
    mmd.write_text("flowchart TB\n  a(Think) --> b[Check]\n", encoding="utf-8")
    code, res, _ = cli_json(capsys, ["diagram", "from-mermaid", str(mmd), "--json"])
    assert code == 0
    assert [n["id"] for n in res["spec"]["nodes"]] == ["a", "b"]
    sp = tmp_path / "s.json"
    sp.write_text(json.dumps(res["spec"]), encoding="utf-8")
    code, res2, _ = cli_json(capsys, ["diagram", "to-mermaid", str(sp), "--json"])
    assert code == 0
    assert res2["mermaid"].splitlines()[0].strip() == "flowchart TB"
