"""MANIFEST §15.9 doc-only skill `review-prompts`, and §15.10 (covering skills mention the new commands).

Generic §11 structure checks for review-prompts run in test_skills_structure.py (it is in REQUIRED_SKILLS).
"""
from __future__ import annotations

import re
from urllib.parse import unquote

import pytest

import helpers_r3 as r3

SKILL = r3.SKILLS_DIR / "review-prompts"
BRIEFS = {
    "so-what": ["Element", "So what", "Verdict"],
    "first-time-reader": ["Where", "Confusion", "Fix"],
    "adversarial-flaw-classes": ["Flaw class", "Found", "Fix"],
    "fact-check": ["Claim", "Source opened", "Page", "Verdict"],
}

# GUIDE-reports-and-presentations.md §8 flaw classes (tundle ai4research/notes)
FLAW_CLASSES = [
    "Box hides >1 model call", "Term before definition", "Paper nickname or author names", "Setup unstated",
    "Choice without justification", "Property only in prose", "Thin slide", "Jargon", "Coverage mismatch",
    "Ordering", "Layout", "Over-claim", "Legacy notes", "Meta / defensive notes",
]


def brief(name: str) -> str:
    p = SKILL / "prompts" / f"{name}.md"
    assert p.is_file(), f"missing {p}"
    return p.read_text(encoding="utf-8")


def skill_md() -> str:
    p = SKILL / "SKILL.md"
    assert p.is_file(), f"missing {p}"
    return p.read_text(encoding="utf-8")


def flat(text: str) -> str:
    """Lower-case text with Markdown emphasis/code marks removed and whitespace collapsed."""
    return re.sub(r"\s+", " ", re.sub(r"[*_`]", "", text)).lower()


def test_skill_front_matter():
    """§15.9/§11: skills/review-prompts/SKILL.md with name review-prompts and a description."""
    fields, body = r3.parse_frontmatter(skill_md())
    assert fields is not None
    assert fields.get("name") == "review-prompts"
    assert 0 < len(fields.get("description", "")) <= 1024
    assert body.strip()


@pytest.mark.parametrize("name", sorted(BRIEFS))
def test_brief_has_fixed_output_table(name):
    """§15.9: each brief carries its fixed output table (header cells in order)."""
    headers = r3.table_headers(brief(name))
    want = [c.lower() for c in BRIEFS[name]]
    assert any([c.lower() for c in h] == want for h in headers), headers


def test_so_what_verdicts():
    """§15.9: so-what verdicts are keep, cut or merge, for sections, paragraphs, bullets, rows and slides."""
    t = flat(brief("so-what"))
    for word in ("keep", "cut", "merge", "section", "paragraph", "bullet", "row", "slide"):
        assert word in t, word


def test_adversarial_brief_has_full_flaw_table():
    """§15.9: adversarial-flaw-classes holds the full GUIDE §8 flaw-class table."""
    t = flat(brief("adversarial-flaw-classes"))
    missing = [c for c in FLAW_CLASSES if flat(c) not in t]
    assert missing == []


@pytest.mark.parametrize("name", sorted(BRIEFS))
def test_brief_states_fresh_context_and_no_rewrite(name):
    """§15.9: each brief says the reviewer runs in a fresh context and reports findings without rewriting."""
    t = flat(brief(name))
    assert "fresh" in t and "context" in t
    assert "rewrit" in t
    assert "input" in t


@pytest.mark.parametrize("name", sorted(BRIEFS))
def test_brief_states_propagation(name):
    """§15.9: each brief says how findings propagate (search for every other instance)."""
    t = flat(brief(name))
    assert "every other instance" in t or ("propagat" in t and "search" in t)


def test_skill_names_input_tools():
    """§15.9: the skill says which tools produce each input."""
    t = skill_md()
    for tool in ("deck_inspect", "render_office", "review_coverage", "claims_trace"):
        assert f"`{tool}`" in t or tool in t, tool


@pytest.mark.parametrize("name", sorted(BRIEFS))
def test_brief_links_only_back_to_skill(name):
    """§15.9: each prompt file links back to SKILL.md, or has no links; relative links resolve."""
    for link in r3.relative_links(brief(name)):
        target = unquote(link.split("#", 1)[0])
        if not target:
            continue
        resolved = (SKILL / "prompts" / target).resolve()
        assert resolved == (SKILL / "SKILL.md").resolve(), link


@pytest.mark.parametrize("skill,command", [
    ("tundle-bundle", "bundle source"),
    ("tundle-bundle", "bundle setup-table"),
    ("paper-reading", "papers summary"),
    ("paper-reading", "papers index-check"),
    ("zh-en-translation", "translate terms"),
])
def test_covering_skill_mentions_new_command(skill, command):
    """§15.10: the skills that cover these areas mention the new commands."""
    root = r3.SKILLS_DIR / skill
    text = "\n".join(p.read_text(encoding="utf-8") for p in [root / "SKILL.md", *sorted(root.rglob("references/*.md"))]
                     if p.is_file())
    assert f"tundlekit {command}" in text, command
