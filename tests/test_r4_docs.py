"""MANIFEST §16.9: the skills cover the round-4 points (keyword checks on skills/<name>/SKILL.md and its
references/*.md)."""
from __future__ import annotations

import re

import pytest

import helpers_r4m as h


def has(text: str, pattern: str) -> bool:
    return re.search(pattern, text, re.I) is not None


@pytest.mark.parametrize("skill,pattern,why", [
    ("report-writing", r"\bT004\b", "0 claims (T004) is not a pass"),
    ("report-writing", r"\(pN\)", "name + (pN) locators"),
    ("report-writing", r"\bweak\b", "weak locations checked by hand"),
    ("report-writing", r"FILE=REPORT", "text xref pairs scripts with their report"),
    ("deliverable-review", r"tundlekit office check", "office check before builds"),
    ("zh-en-translation", r"\bL003\b", "L001 vs L003 on Chinese hops"),
    ("zh-en-translation", r"same-language", "--compare same-language"),
    ("tundle-bundle", r"bundle source\b[^\n]*--all", "bundle source DIR --all"),
    ("deck-builder", r"--ids\b", "--ids for times files"),
    ("deck-builder", r"\bmoved\b", "deck diff moved changes"),
    ("diagram-maker", r"wrap[^\n]*group|group[^\n]*wrap", "wrap with groups"),
])
def test_skill_mentions(skill, pattern, why):
    """§16.9: each skill documents its round-4 point."""
    text = h.skill_text(skill)
    assert text, f"skills/{skill}/SKILL.md exists"
    assert has(text, pattern), f"{skill}: {why} ({pattern})"


def test_deck_builder_mentions_number_changes():
    """§16.9: deck diff after cuts and reorders reports renumbering (number changes)."""
    text = h.skill_text("deck-builder")
    assert has(text, r"deck diff") and has(text, r"\bnumber\b")
