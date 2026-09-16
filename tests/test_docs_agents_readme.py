"""MANIFEST §12 README.md and AGENTS.md."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_misc as h  # noqa: E402

README = h.REPO / "README.md"
AGENTS = h.REPO / "AGENTS.md"


def text(path: Path) -> str:
    assert path.is_file(), f"missing {path.name}"
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("path", [README, AGENTS], ids=["README", "AGENTS"])
def test_doc_exists(path):
    """§12: README.md and AGENTS.md exist and are not empty."""
    assert text(path).strip()


@pytest.mark.parametrize("path", [README, AGENTS], ids=["README", "AGENTS"])
def test_every_cli_command_exists(path):
    """§12: every CLI command in AGENTS.md and README.md exists."""
    assert h.bad_cli_mentions(text(path)) == []


def test_readme_install_instruction():
    """§12: README gives the install command `pip install -e .[all]`."""
    t = text(README)
    assert re.search(r"pip install -e \"?\.\[all\]\"?", t)


def test_readme_command_overview():
    """§12: README has the command overview: every command group is shown as `tundlekit <group> ...`."""
    groups = {g for g, _ in h.cli_mentions(text(README))}
    assert h.GROUPS <= groups, f"missing groups: {sorted(h.GROUPS - groups)}"


def test_readme_points_to_skills():
    """§12: README says where the skills are."""
    assert "skills/" in text(README)


def test_agents_claude_code_snippet():
    """§12: an MCP snippet for Claude Code (.mcp.json)."""
    t = text(AGENTS)
    assert ".mcp.json" in t
    assert "tundlekit-mcp" in t or "tundlekit.mcp_server" in t


def test_agents_codex_snippet():
    """§12: a Codex CLI snippet: config.toml with [mcp_servers.tundlekit]."""
    t = text(AGENTS)
    assert "config.toml" in t
    assert "[mcp_servers.tundlekit]" in t


def test_agents_gemini_snippet():
    """§12: a Gemini CLI snippet (settings.json)."""
    t = text(AGENTS)
    assert "Gemini" in t
    assert "settings.json" in t


def test_agents_generic_stdio_client():
    """§12: a generic stdio client."""
    assert re.search(r"(?i)stdio", text(AGENTS))


def test_agents_skills_install():
    """§12: how to install the skills (copy or link skills/<name>)."""
    t = text(AGENTS)
    assert "skills/" in t
    assert re.search(r"(?i)\b(copy|link|symlink)", t)


def test_agents_how_to_run_tests():
    """§12: how to run the tests (python -m pytest from the repo root)."""
    assert "pytest" in text(AGENTS)
