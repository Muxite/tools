"""MANIFEST §11 skills: structure, agent-agnostic wording, real commands and tools, links, coverage."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_misc as h  # noqa: E402

EXISTING = sorted(p.name for p in h.SKILLS_DIR.iterdir() if p.is_dir()) if h.SKILLS_DIR.is_dir() else []
ALL_SKILLS = sorted(set(h.REQUIRED_SKILLS) | set(EXISTING))
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def skill_text(name: str) -> str:
    path = h.SKILLS_DIR / name / "SKILL.md"
    assert path.is_file(), f"missing {path}"
    return path.read_text(encoding="utf-8")


def skill_markdown_files(name: str) -> list[Path]:
    root = h.SKILLS_DIR / name
    return [root / "SKILL.md", *sorted((root / "references").glob("*.md"))] if root.is_dir() else []


@pytest.mark.parametrize("name", h.REQUIRED_SKILLS)
def test_required_skill_exists(name):
    """§11: each required skill is skills/<name>/SKILL.md."""
    assert (h.SKILLS_DIR / name / "SKILL.md").is_file()


@pytest.mark.parametrize("name", ALL_SKILLS)
def test_frontmatter_name(name):
    """§11: name equals the directory name, matches ^[a-z0-9]+(-[a-z0-9]+)*$, <= 64 chars."""
    fields, _ = h.parse_frontmatter(skill_text(name))
    assert fields is not None, "SKILL.md must start with a --- front matter block"
    assert fields.get("name") == name
    assert NAME_RE.match(name) and len(name) <= 64


@pytest.mark.parametrize("name", ALL_SKILLS)
def test_frontmatter_description(name):
    """§11: description is non-empty, <= 1024 chars, and says when to use the skill."""
    fields, _ = h.parse_frontmatter(skill_text(name))
    assert fields is not None
    desc = fields.get("description", "")
    assert desc.strip()
    assert len(desc) <= 1024
    assert re.search(r"(?i)\b(when|use)\b", desc), "description should say when to use it"


@pytest.mark.parametrize("name", ALL_SKILLS)
def test_body_under_500_lines(name):
    """§11: the body is Markdown instructions, < 500 lines, and not empty."""
    fields, body = h.parse_frontmatter(skill_text(name))
    assert fields is not None
    assert body.strip()
    assert len(body.splitlines()) < 500


@pytest.mark.parametrize("name", ALL_SKILLS)
def test_no_vendor_tool_names(name):
    """§11: no vendor-specific tool names (Bash(, Read(, mcp__) in the skill's Markdown."""
    for path in skill_markdown_files(name):
        text = path.read_text(encoding="utf-8")
        for bad in ("Bash(", "Read(", "mcp__"):
            assert bad not in text, f"{path.name} contains {bad!r}"


@pytest.mark.parametrize("name", ALL_SKILLS)
def test_cli_commands_are_real(name):
    """§11: every `tundlekit <group> <command>` shown in a skill is a real CLI command."""
    bad = []
    for path in skill_markdown_files(name):
        bad += h.bad_cli_mentions(path.read_text(encoding="utf-8"))
    assert bad == []


@pytest.mark.parametrize("name", ALL_SKILLS)
def test_skill_mentions_cli(name):
    """§11: skills refer to the tools as CLI commands (`tundlekit ...`)."""
    mentions = []
    for path in skill_markdown_files(name):
        mentions += h.cli_mentions(path.read_text(encoding="utf-8"))
    if name == "held-out-build-gate":
        pytest.skip("a process skill need not name a tundlekit command")
    assert mentions, "no `tundlekit <group> <command>` shown"


@pytest.mark.parametrize("name", ALL_SKILLS)
def test_mcp_tool_names_are_registered(name):
    """§11: a backticked snake_case word starting with a registered group prefix must be a registered tool."""
    bad = []
    for path in skill_markdown_files(name):
        bad += h.bad_tool_mentions(path.read_text(encoding="utf-8"))
    assert bad == []


@pytest.mark.parametrize("name", ALL_SKILLS)
def test_relative_links_resolve(name):
    """§11: every relative link in SKILL.md resolves."""
    text = skill_text(name)
    base = h.SKILLS_DIR / name
    missing = []
    for link in h.relative_links(text):
        target = unquote(link.split("#", 1)[0])
        if target and not (base / target).exists():
            missing.append(link)
    assert missing == []


# (skill, regex) pairs from the §11 coverage table. Regexes are case-insensitive unless (?-i) is used.
COVERAGE = [
    ("tundle-bundle", r"bundle status"),
    ("tundle-bundle", r"bundle release"),
    ("tundle-bundle", r"bundle compare"),
    ("tundle-bundle", r"bundle lint"),
    ("tundle-bundle", r"bundle verify"),
    ("tundle-bundle", r"bundle prune"),
    ("tundle-bundle", r"SOURCE\.md"),
    ("tundle-bundle", r"latest"),
    ("deck-builder", r"deck lint"),
    ("deck-builder", r"deck build"),
    ("deck-builder", r"(?-i:SAY)"),
    ("deck-builder", r"(?-i:IF ASKED)"),
    ("deck-builder", r"(?-i:MUST HIT)"),
    ("deck-builder", r"insert"),
    ("deck-builder", r"TIME"),
    ("diagram-maker", r"diagram render"),
    ("diagram-maker", r"chart bar"),
    ("diagram-maker", r"mermaid"),
    ("diagram-maker", r"stage"),
    ("diagram-maker", r"actor"),
    ("report-writing", r"text lint"),
    ("report-writing", r"text fignums"),
    ("report-writing", r"text wordcount"),
    ("report-writing", r"limitation"),
    ("report-writing", r"style card"),
    ("deliverable-review", r"tundlekit render"),
    ("deliverable-review", r"contact sheet"),
    ("deliverable-review", r"adversarial"),
    ("deliverable-review", r"office"),
    ("paper-reading", r"papers fetch"),
    ("paper-reading", r"papers list"),
    ("paper-reading", r"papers abs"),
    ("paper-reading", r"papers grep"),
    ("paper-reading", r"papers body"),
    ("paper-reading", r"arxiv"),
    ("paper-reading", r"summar"),
    ("zh-en-translation", r"(?-i:T0)"),
    ("zh-en-translation", r"(?-i:T1)"),
    ("zh-en-translation", r"(?-i:T2)"),
    ("zh-en-translation", r"critic"),
    ("zh-en-translation", r"translate check"),
    ("zh-en-translation", r"translate resources"),
    ("held-out-build-gate", r"manifest"),
    ("held-out-build-gate", r"held[- ]out"),
    ("held-out-build-gate", r"visible"),
    ("held-out-build-gate", r"implementer"),
    ("held-out-build-gate", r"adversarial"),
]


@pytest.mark.parametrize("name,pattern", COVERAGE)
def test_required_coverage(name, pattern):
    """§11 table: each required skill covers its topics."""
    text = "\n".join(p.read_text(encoding="utf-8") for p in skill_markdown_files(name))
    assert text, f"skill {name} is missing"
    assert re.search("(?i)" + pattern, text), f"{name} does not mention {pattern!r}"
