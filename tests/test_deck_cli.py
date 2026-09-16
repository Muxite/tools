"""deck / chart / palette tools through the CLI and the registry (MANIFEST §0.2, §0.4, §3, §5, §6)."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from helpers_deck import SAY25, content, get_tool, run_cli, spec, title_slide, write_json

REPO = Path(__file__).resolve().parents[1]
MY_TOOLS = ["deck_build", "deck_lint", "deck_inspect", "chart_bar", "palette_get"]


@pytest.mark.parametrize("name", MY_TOOLS)
def test_tool_schema_conventions(name):
    # §0.2: object schema, additionalProperties false, description 1..1024 chars
    t = get_tool(name)
    assert t.input_schema["type"] == "object"
    assert t.input_schema.get("additionalProperties") is False
    assert 0 < len(t.description) <= 1024


@pytest.mark.parametrize("name", ["deck_lint", "deck_inspect", "palette_get"])
def test_read_only_tools_annotated(name):
    # §0.2: tools that only read carry readOnlyHint true
    assert get_tool(name).annotations.get("readOnlyHint") is True


def test_modules_do_not_import_optional_packages_at_import():
    # §0.1: importing a tundlekit module must not import an optional package
    code = ("import sys, tundlekit.deck, tundlekit.chart, tundlekit.palette;"
            "bad=[m for m in ('pptx','PIL','fitz') if m in sys.modules];"
            "print(','.join(bad)); sys.exit(1 if bad else 0)")
    env = dict(os.environ, PYTHONPATH=str(REPO))
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, cwd=str(REPO))
    assert r.returncode == 0, r.stdout + r.stderr


def test_cli_deck_build_and_lint(tmp_path, capsys):
    # §0.4 / §3.2 / §3.3 CLI forms with --json
    pytest.importorskip("pptx")
    pytest.importorskip("PIL")
    s = spec(title_slide(), content(source="Paper, Table 1", say=SAY25))
    p = write_json(tmp_path / "deck.json", s)
    out = tmp_path / "deck.pptx"
    code, data, _ = run_cli(["deck", "build", p, "-o", out, "--json"], capsys)
    assert code == 0
    assert data["core_slides"] == 2
    assert out.is_file()
    code, data, _ = run_cli(["deck", "lint", out, "--json"], capsys)
    assert code == 0 and data["ok"] is True
    code, data, _ = run_cli(["deck", "inspect", out, "--json"], capsys)
    assert code == 0 and len(data["slides"]) == 2


def test_cli_deck_build_inserts_and_times_file(tmp_path, capsys):
    # §3.2 CLI: --inserts MODE and --times-file PATH
    pytest.importorskip("pptx")
    pytest.importorskip("PIL")
    s = spec(content(), content(insert=True, time="0:20"), id="talk")
    p = write_json(tmp_path / "deck.json", s)
    tf = tmp_path / "times.json"
    code, data, _ = run_cli(["deck", "build", p, "-o", tmp_path / "o.pptx", "--inserts", "off",
                             "--times-file", tf, "--json"], capsys)
    assert code == 0
    assert data["inserts"] == "off"
    assert json.loads(tf.read_text(encoding="utf-8")) == {"talk": 30, "talk_inserts": 0}


def test_cli_lint_exit_codes(tmp_path, capsys):
    # §0.4: exit 1 on errors; --strict makes warnings exit 1
    bad = write_json(tmp_path / "bad.json", spec(content(title="A — B", source="x")))
    code, data, _ = run_cli(["deck", "lint", bad, "--json"], capsys)
    assert code == 1 and data["ok"] is False
    warn = write_json(tmp_path / "warn.json", spec(content(say="too few words", source="x")))
    code, data, _ = run_cli(["deck", "lint", warn, "--json"], capsys)
    assert code == 0 and data["counts"]["warning"] >= 1
    code, _, _ = run_cli(["deck", "lint", warn, "--strict", "--json"], capsys)
    assert code == 1


def test_cli_build_tool_error(tmp_path, capsys):
    # §0.4: ToolError -> exit 1, {"error": ...} on stdout, "tundlekit: " on stderr
    pytest.importorskip("pptx")
    pytest.importorskip("PIL")
    p = write_json(tmp_path / "deck.json", spec(content(time="bad")))
    code, data, err = run_cli(["deck", "build", p, "-o", tmp_path / "o.pptx", "--json"], capsys)
    assert code == 1
    assert "error" in data and "slides[0].notes.time" in data["error"]
    assert err.startswith("tundlekit: ")


def test_cli_chart_bar(tmp_path, capsys):
    # §5 CLI: tundlekit chart bar SPEC.json -o OUT.svg
    p = write_json(tmp_path / "c.json", {"categories": ["a", "b"], "values": [1, 2]})
    out = tmp_path / "c.svg"
    code, data, _ = run_cli(["chart", "bar", p, "-o", out, "--json"], capsys)
    assert code == 0
    assert out.is_file()
    assert Path(data["path"]).resolve() == out.resolve()
    assert len(data["bars"]) == 2


def test_cli_palette_show(capsys):
    # §6 CLI: tundlekit palette show
    code, data, _ = run_cli(["palette", "show", "--json"], capsys)
    assert code == 0
    assert data["stage"]["gates"].lower() == "#008a63"
    assert data["ink"] == "#000000"
