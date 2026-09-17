"""MANIFEST §11 skill `deliverable-production`, and the diagram-maker layout/legibility reference.

Generic §11 structure checks (front matter, body length, real commands, registered tools, links) run in
test_skills_structure.py: both are reachable from SKILLS_DIR, and the skill is in REQUIRED_SKILLS.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_misc as h  # noqa: E402

SKILL = h.SKILLS_DIR / "deliverable-production" / "SKILL.md"
REFERENCE = h.SKILLS_DIR / "diagram-maker" / "references" / "layout-and-legibility.md"


def flat(text: str) -> str:
    """Lower-case text with Markdown emphasis/code marks removed and whitespace collapsed."""
    return re.sub(r"\s+", " ", re.sub(r"[*_`]", "", text)).lower()


def skill_text() -> str:
    assert SKILL.is_file(), f"missing {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def reference_text() -> str:
    assert REFERENCE.is_file(), f"missing {REFERENCE}"
    return REFERENCE.read_text(encoding="utf-8")


# --------------------------------------------------------------------------------- deliverable-production

def test_front_matter():
    """§11: name equals the directory, with a description and a body."""
    fields, body = h.parse_frontmatter(skill_text())
    assert fields is not None
    assert fields.get("name") == "deliverable-production"
    assert 0 < len(fields.get("description", "")) <= 1024
    assert body.strip()


@pytest.mark.parametrize("step", ["audience", "scope", "outline", "build", "render", "check", "review", "package"])
def test_production_order_covers_step(step):
    """The production order runs from audience and scope through render, check, review and hand-back."""
    assert step in flat(skill_text()), step


def test_decisions_come_before_building():
    """Audience and scope are decided first, and the slide count comes from the time budget."""
    t = flat(skill_text())
    assert "collapse" in t
    assert "slide count" in t and "time budget" in t


def test_read_aloud_early_with_margin():
    """The read-aloud rule: from the outline, with a timer, and a margin over planned time."""
    t = flat(skill_text())
    assert "aloud" in t
    assert "timer" in t
    assert "outline" in t
    assert "25%" in t


def test_sources_of_truth_and_hand_edits():
    """Markdown and specs are the source; built Office files are never edited and regenerated over."""
    t = flat(skill_text())
    assert "markdown" in t and "output" in t
    assert "hand-edit" in t or "hand edit" in t
    assert "tundlekit deck diff" in t


def test_two_verification_channels():
    """Checks and rendering are both required; an estimator's silence is not proof."""
    t = flat(skill_text())
    assert "render" in t and "check" in t
    assert "blind spot" in t or "estimator" in t


def test_cutting_and_insertion_rule():
    """Time is controlled with insertion slides, never by trimming core slides."""
    t = flat(skill_text())
    assert "insertion" in t
    assert "never by trimming core slides" in t


def test_lane_protocol():
    """Several agents: isolated worktrees, one commit per lane, the coordinator renders."""
    t = flat(skill_text())
    assert "worktree" in t
    assert "one commit per lane" in t
    assert "coordinator" in t
    assert "read-only audit" in t


def test_handback_package_documents():
    """The hand-back package names its documents and the rejection and doubt conventions."""
    t = flat(skill_text())
    for word in ("state table", "changelog", "presenter pack", "settled by"):
        assert word in t, word
    assert "rejected" in t


def test_presenter_pack_table_headers():
    """The presenter pack's slide table carries its fixed headers."""
    headers = [[c.strip().lower() for c in row] for row in table_headers(skill_text())]
    assert ["#", "title", "time", "crib line"] in headers, headers


def table_headers(md: str) -> list[list[str]]:
    """Header cells of every Markdown pipe table (a row followed by a |---| separator)."""
    lines, out = md.splitlines(), []
    for i, line in enumerate(lines[:-1]):
        nxt = lines[i + 1].strip()
        if line.strip().startswith("|") and re.fullmatch(r"\|?[\s:\-|]+\|?", nxt) and "-" in nxt:
            out.append([c.strip() for c in line.strip().strip("|").split("|")])
    return out


def test_names_real_cli_commands():
    """§11: the skill shows real CLI commands (also enforced generically)."""
    text = skill_text()
    assert h.cli_mentions(text)
    assert h.bad_cli_mentions(text) == []


# --------------------------------------------------------------------------------- diagram layout reference

def test_reference_is_linked_from_the_skill():
    """The diagram-maker skill links its layout and legibility reference."""
    skill = (h.SKILLS_DIR / "diagram-maker" / "SKILL.md").read_text(encoding="utf-8")
    assert "references/layout-and-legibility.md" in skill


def test_reference_recipe_table():
    """The reference maps what a figure must teach onto a layout recipe."""
    t = flat(reference_text())
    for recipe in ("linear pipeline", "small multiples", "decision table", "funnel", "trust boundary",
                   "layer stack", "spec card"):
        assert recipe in t, recipe


def test_reference_mechanism_not_component_map():
    """The first rule: draw the mechanism, not a component map."""
    t = flat(reference_text())
    assert "mechanism" in t
    assert "component map" in t


def test_reference_sizing_rule():
    """Text size is a ratio of the physical width, and the report width is the binding case."""
    t = flat(reference_text())
    assert "ratio" in t
    assert "report is the binding case" in t
    assert "widen the box or shorten the label" in t


def test_reference_states_spec_limits():
    """The reference says which layouts the automatic renderer cannot produce."""
    t = flat(reference_text())
    assert "cannot express" in t or "cannot" in t
    assert "wrap" in t and "rank" in t


def test_reference_names_real_cli_commands():
    """§11: the reference shows real CLI commands (also enforced generically)."""
    text = reference_text()
    assert h.cli_mentions(text)
    assert h.bad_cli_mentions(text) == []
