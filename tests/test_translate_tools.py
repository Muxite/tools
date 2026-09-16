"""MANIFEST §10 translate_check and translate_resources."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_misc as h  # noqa: E402

PKG = h.REPO / "tundlekit" / "translate"
MOJIBAKE_LINE = "# Phase 22 çœŸå®žä»»åŠ¡"


def write(path: Path, text: str) -> Path:
    path.write_bytes(text.encode("utf-8"))
    return path


def check(capsys, *argv):
    return h.run_cli(["translate", "check", *[str(a) for a in argv], "--json"], capsys)


def assert_result(data, exit_code):
    assert set(data) >= {"exit_code", "ok", "output", "errors"}
    assert data["exit_code"] == exit_code
    assert data["ok"] is (exit_code == 0)
    assert isinstance(data["output"], str)
    assert isinstance(data["errors"], str)


def test_translate_tools_registered():
    """§10: tool names."""
    tools = h.registry().TOOLS
    assert "translate_check" in tools and "translate_resources" in tools


@pytest.mark.parametrize("command", ["check", "resources"])
def test_translate_cli_commands_exist(command):
    """§10: CLI commands."""
    assert h.cli_command_exists("translate", command)


# ------------------------------------------------------------------------------------------ check: encoding

def test_encoding_clean_ok(tmp_path, capsys):
    """§10: encoding mode on clean text: exit 0, ok true, tcheck output captured."""
    src = write(tmp_path / "zh.md", "# 标题\n\n能力胶囊是自闭环的。\n")
    code, data, _, _ = check(capsys, "encoding", src)
    assert code == 0
    assert_result(data, 0)
    assert "encoding" in data["output"] and "OK" in data["output"]


def test_encoding_mojibake_fails(tmp_path, capsys):
    """§10: a hard failure gives exit_code 1, ok false; the CLI returns the exit code."""
    src = write(tmp_path / "bad.md", MOJIBAKE_LINE + "\n")
    code, data, _, _ = check(capsys, "encoding", src)
    assert code == 1
    assert_result(data, 1)
    assert "FAIL" in data["output"]


def test_encoding_repair_writes_copy(tmp_path, capsys):
    """§10: --repair OUT applies to encoding and writes a repaired copy; the source is unchanged."""
    src = write(tmp_path / "bad.md", MOJIBAKE_LINE + "\n")
    out = tmp_path / "fixed.md"
    code, data, _, _ = check(capsys, "encoding", src, "--repair", out)
    assert data["exit_code"] == 1
    assert "真实任务" in out.read_text(encoding="utf-8")
    assert src.read_text(encoding="utf-8") == MOJIBAKE_LINE + "\n"


# ------------------------------------------------------------------------------------------ check: tgt required

@pytest.mark.parametrize("mode", ["spans", "glossary", "all"])
def test_tgt_required(mode, tmp_path, capsys):
    """§10: tgt is required for spans, glossary and all (ToolError: exit 1 and {"error"})."""
    src = write(tmp_path / "src.md", "线程安全\n")
    code, data, _, err = check(capsys, mode, src)
    assert code == 1
    assert "error" in data
    assert err.startswith("tundlekit: ")


# ------------------------------------------------------------------------------------------ check: spans

def test_spans_missing_code_fails(tmp_path, capsys):
    """§10: spans mode passes tcheck's verdict through."""
    src = write(tmp_path / "src.md", "运行 `make test` 命令。\n")
    tgt = write(tmp_path / "tgt.md", "Run the test command.\n")
    code, data, _, _ = check(capsys, "spans", src, tgt)
    assert code == 1
    assert_result(data, 1)
    assert "make test" in data["output"]


def test_spans_kept_code_ok(tmp_path, capsys):
    """§10: spans mode OK when the code span survives."""
    src = write(tmp_path / "src.md", "运行 `make test` 命令。\n")
    tgt = write(tmp_path / "tgt.md", "Run the `make test` command.\n")
    code, data, _, _ = check(capsys, "spans", src, tgt)
    assert code == 0
    assert_result(data, 0)


# ------------------------------------------------------------------------------------------ check: glossary

def test_glossary_default_direction_zh_en(tmp_path, capsys):
    """§10: direction defaults to zh-en, so glossary mode works without --dir."""
    src = write(tmp_path / "src.md", "这个函数是线程安全的。\n")
    tgt = write(tmp_path / "tgt.md", "This function is thread-safe.\n")
    code, data, _, _ = check(capsys, "glossary", src, tgt)
    assert code == 0
    assert_result(data, 0)


def test_glossary_banned_term_fails(tmp_path, capsys):
    """§10: a banned rendering fails (vendored glossary: 线程安全 must not become 'reentrant')."""
    src = write(tmp_path / "src.md", "这个函数是线程安全的。\n")
    tgt = write(tmp_path / "tgt.md", "This function is reentrant.\n")
    code, data, _, _ = check(capsys, "glossary", src, tgt, "--dir", "zh-en")
    assert code == 1
    assert_result(data, 1)


def test_glossary_en_zh_direction(tmp_path, capsys):
    """§10: --dir en-zh."""
    src = write(tmp_path / "src.md", "The function is thread-safe.\n")
    bad = write(tmp_path / "bad.md", "该函数是可重入的。\n")
    good = write(tmp_path / "good.md", "该函数是线程安全的。\n")
    code, data, _, _ = check(capsys, "glossary", src, bad, "--dir", "en-zh")
    assert code == 1 and data["ok"] is False
    code, data, _, _ = check(capsys, "glossary", src, good, "--dir", "en-zh")
    assert code == 0 and data["ok"] is True


def test_glossary_slice_needs_no_tgt(tmp_path, capsys):
    """§10: glossary-slice takes only SRC and prints the relevant glossary rows."""
    src = write(tmp_path / "src.md", "这个函数是线程安全的。\n")
    code, data, _, _ = check(capsys, "glossary-slice", src, "--dir", "zh-en")
    assert code == 0
    assert_result(data, 0)
    assert "thread-safe" in data["output"]
    assert "idempotent" not in data["output"]


def test_custom_glossary_path(tmp_path, capsys):
    """§10: --glossary PATH replaces the vendored glossary."""
    gl = tmp_path / "g.tsv"
    gl.write_text("en\tzh\tbanned_en\tbanned_zh\tdomain\tstatus\tevidence\tnote\n"
                  "widget\t小部件\tgadget\t\tgeneral\tapproved\t\t\n", encoding="utf-8")
    src = write(tmp_path / "src.md", "这是一个小部件。\n")
    tgt = write(tmp_path / "tgt.md", "This is a gadget.\n")
    code, data, _, _ = check(capsys, "glossary", src, tgt, "--glossary", gl)
    assert code == 1
    assert_result(data, 1)


def test_all_mode_summary(tmp_path, capsys):
    """§10: all mode runs every check and prints tcheck's summary."""
    src = write(tmp_path / "src.md", "运行 `make test`。这个函数是线程安全的。\n")
    tgt = write(tmp_path / "tgt.md", "Run `make test`. This function is thread-safe.\n")
    code, data, _, _ = check(capsys, "all", src, tgt, "--dir", "zh-en")
    assert code == 0
    assert_result(data, 0)
    assert "hard failure(s)" in data["output"]


def test_relative_paths_resolve_against_cwd(tmp_path, capsys, monkeypatch):
    """§0.2: relative paths resolve against the current directory."""
    write(tmp_path / "zh.md", "# 标题\n")
    monkeypatch.chdir(tmp_path)
    code, data, _, _ = check(capsys, "encoding", "zh.md")
    assert code == 0
    assert data["ok"] is True


# ------------------------------------------------------------------------------------------ resources

def package_resources():
    names = set()
    for sub in ("data", "prompts"):
        for p in (PKG / sub).iterdir():
            if p.is_file():
                names.add(f"{sub}/{p.name}")
    return names


def test_resources_listing():
    """§10: without name, every file in data/ and prompts/ as data/<file> or prompts/<file>."""
    data = h.call_tool("translate_resources")
    assert set(data["resources"]) == package_resources()
    assert "data/glossary.tsv" in data["resources"]
    assert "prompts/critic.md" in data["resources"]


def test_resources_read_by_name():
    """§10: with name, {"name", "text"}."""
    data = h.call_tool("translate_resources", {"name": "prompts/critic.md"})
    assert data["name"] == "prompts/critic.md"
    expected = (PKG / "prompts" / "critic.md").read_text(encoding="utf-8")
    assert data["text"].replace("\r\n", "\n") == expected.replace("\r\n", "\n")


def test_resources_unknown_name():
    """§10: an unknown name gives ToolError."""
    with pytest.raises(h.tool_error()):
        h.call_tool("translate_resources", {"name": "data/nope.md"})


def test_resources_cli(capsys):
    """§10: `tundlekit translate resources [--name NAME]`."""
    code, data, _, _ = h.run_cli(["translate", "resources", "--name", "data/RULES.md", "--json"], capsys)
    assert code == 0
    assert data["name"] == "data/RULES.md"
    assert data["text"].replace("\r\n", "\n") == \
        (PKG / "data" / "RULES.md").read_text(encoding="utf-8").replace("\r\n", "\n")


def test_resources_is_read_only():
    """§0.2: translate_resources only reads."""
    assert h.registry().TOOLS["translate_resources"].annotations.get("readOnlyHint") is True
