"""MANIFEST §16.2 deck_diff (round 4): pairing order, `moved` via a longest increasing subsequence, `number`
changes, 1 `text` change per table, `slide` always a string. §16.2 wins over §15.4 where they differ.

Decks are built with deck_build (§3.2); hand edits use python-pptx copies (helpers_r3).
"""
from __future__ import annotations

import itertools

import pytest

import helpers_r3 as r3
import helpers_r4d as r4

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

T = r4.TITLES


@pytest.fixture
def ten(tmp_path):
    return r4.build_deck(tmp_path / "old.pptx", spec=r4.ten_spec())


def rebuilt(tmp_path, order, titles=T, name="new.pptx"):
    return r4.build_deck(tmp_path / name, spec=r4.ten_spec(order, titles))


def numbers(res):
    return {(c["old"], c["new"]) for c in r4.of(res, "number")}


def remove_at(src, dst, index):
    """Drop the slide at 0-based index (python-pptx copy)."""
    prs = r4.open_deck(src)
    lst = prs.slides._sldIdLst
    sld_id = list(lst)[index]
    prs.part.drop_rel(sld_id.rId)
    lst.remove(sld_id)
    prs.save(str(dst))
    return dst


def test_fixture_titles_are_dissimilar():
    """Guard: the 10 fixture titles are distinct and pairwise below the §16.2 0.8 threshold, so in the cut
    scenarios every kept slide pairs by its exact title (step 1) and nothing is left for steps 2-3."""
    assert len(set(T)) == len(T)
    worst = max(r4.similarity(a, b) for a, b in itertools.combinations(T, 2))
    assert worst < 0.8, worst


def test_last_quarter_cut(ten, tmp_path):
    """§16.2: slides 6-7 cut, 8-10 renumbered 6-8, slide 3 moved after slide 5. Result: 2 removed, `number`
    changes for every renumbered slide, exactly 1 moved (outside the LIS), no title/text/added changes."""
    new = rebuilt(tmp_path, [0, 1, 3, 4, 2, 7, 8, 9])
    res = r4.deck_diff(ten, new)
    removed = r4.of(res, "removed")
    assert sorted(c["slide"] for c in removed) == ["6", "7"]
    assert sorted(c["old"] for c in removed) == sorted([T[5], T[6]])
    moved = r4.of(res, "moved")
    assert [(c["slide"], c["old"], c["new"]) for c in moved] == [("5", 3, 5)]
    assert numbers(res) == {("4", "3"), ("5", "4"), ("3", "5"), ("8", "6"), ("9", "7"), ("10", "8")}
    for c in r4.of(res, "number"):
        assert c["slide"] == c["new"]          # §16.2: the new slide's number text
    for field in ("title", "text", "added", "notes", "hidden"):
        assert r4.of(res, field) == [], (field, res["changes"])


def test_cut_without_move_has_no_moved(ten, tmp_path):
    """§16.2: renumbering explained by removals is not a move."""
    res = r4.deck_diff(ten, rebuilt(tmp_path, [0, 1, 2, 3, 4, 7, 8, 9]))
    assert sorted(c["slide"] for c in r4.of(res, "removed")) == ["6", "7"]
    assert r4.of(res, "moved") == []
    assert numbers(res) == {("8", "6"), ("9", "7"), ("10", "8")}
    assert {c["field"] for c in res["changes"]} == {"removed", "number"}


def test_renumbered_slide_with_small_title_edit(ten, tmp_path):
    """§16.2 step 1: title similarity >= 0.8 pairs across a renumber, giving `title` and `number` changes."""
    titles = list(T)
    titles[7] = "Open questions for the reviewers"
    assert r4.similarity(T[7], titles[7]) >= 0.8
    res = r4.deck_diff(ten, rebuilt(tmp_path, [0, 1, 2, 3, 4, 7, 8, 9], titles))
    (t,) = r4.of(res, "title")
    assert (t["slide"], t["old"], t["new"]) == ("6", T[7], titles[7])
    assert ("8", "6") in numbers(res)
    assert r4.of(res, "added") == []
    assert sorted(c["slide"] for c in r4.of(res, "removed")) == ["6", "7"]


def test_same_number_mid_similarity_is_a_title_change(tmp_path):
    """§16.2 step 2: same number text and title similarity >= 0.4 (below 0.8) still pairs."""
    old = r3.build_deck(tmp_path / "old.pptx")
    new_title = "Libraries need a retirement rule"
    assert 0.4 <= r4.similarity("Library growth needs retirement", new_title) < 0.8
    new = r3.edit_frame(old, tmp_path / "new.pptx", "4", "Library growth needs retirement", new_title)
    res = r4.deck_diff(old, new)
    assert [(c["field"], c["slide"]) for c in res["changes"]] == [("title", "4")]


def test_same_number_unrelated_title_is_removed_and_added(ten, tmp_path):
    """§16.2 steps 2 and 4: a slide whose title changed beyond recognition (< 0.4) is not paired by number."""
    replacement = "Zebra migration patterns"
    assert r4.similarity(T[3], replacement) < 0.4
    new = r3.edit_frame(ten, tmp_path / "new.pptx", "4", T[3], replacement)
    res = r4.deck_diff(ten, new)
    assert [(c["slide"], c["old"]) for c in r4.of(res, "removed")] == [("4", T[3])]
    added = r4.of(res, "added")
    assert [c["slide"] for c in added] == ["4"]
    assert r4.of(res, "title") == []


def test_duplicate_titles_prefer_same_number(tmp_path):
    """§16.2 step 1: among several exact-title candidates the same number text wins over position."""
    titles = ["Kept tools fail held-out tests", "Recap", "Gates decide admission", "Recap", "Next steps and owners"]
    old = r4.build_deck(tmp_path / "old.pptx", spec=r4.ten_spec(titles=titles))
    new = r3.move_slide(old, tmp_path / "new.pptx", 3, 0)       # "Recap" numbered 4 goes first
    res = r4.deck_diff(old, new)
    assert [(c["field"], c["slide"], c["old"], c["new"]) for c in res["changes"]] == [("moved", "4", 4, 1)]


def test_duplicate_titles_prefer_nearest_position(tmp_path):
    """§16.2 step 1: with no same-number candidate, the nearest position wins, so nothing moves."""
    titles = ["Kept tools fail held-out tests", "Recap", "Gates decide admission",
              "Budgets cap every run at forty minutes", "Recap", "Next steps and owners"]
    old = r4.build_deck(tmp_path / "old.pptx", spec=r4.ten_spec(titles=titles))
    new = r4.build_deck(tmp_path / "new.pptx", spec=r4.ten_spec(order=[1, 2, 3, 4, 5], titles=titles))
    res = r4.deck_diff(old, new)
    assert [c["slide"] for c in r4.of(res, "removed")] == ["1"]
    assert r4.of(res, "moved") == [] and r4.of(res, "title") == [] and r4.of(res, "added") == []
    assert numbers(res) == {("2", "1"), ("3", "2"), ("4", "3"), ("5", "4"), ("6", "5")}


ROWS = [["Gate", "Kept", "Passed"], ["unit", "222", "7"], ["held-out", "222", "5"]]


def test_table_gives_one_text_change_with_row_diff(tmp_path):
    """§16.2: 2 edited cells in 1 table are 1 `text` change whose diff has rows joined with ' | '."""
    rows = [list(r) for r in ROWS]
    rows[1][2], rows[2][2] = "8", "6"
    old = r4.build_deck(tmp_path / "old.pptx", spec=r4.table_spec(ROWS))
    new = r4.build_deck(tmp_path / "new.pptx", spec=r4.table_spec(rows))
    res = r4.deck_diff(old, new)
    (c,) = res["changes"]
    assert (c["field"], c["slide"]) == ("text", "2")
    lines = c["diff"].splitlines()
    for expected in ("-unit | 222 | 7", "+unit | 222 | 8", "-held-out | 222 | 5", "+held-out | 222 | 6"):
        assert expected in lines, (expected, c["diff"])
    assert "-Gate | Kept | Passed" not in lines and "+Gate | Kept | Passed" not in lines


def test_unnumbered_slide_label_is_hash_position(tmp_path):
    """§16.2: `slide` is "#<position>" for a slide without a number."""
    old = r3.build_deck(tmp_path / "old.pptx")
    new = r3.edit_frame(old, tmp_path / "new.pptx", None, "Capability capsules for AI research",
                        "Capability capsules for AI research teams")
    res = r4.deck_diff(old, new)
    assert [(c["field"], c["slide"]) for c in res["changes"]] == [("title", "#1")]


def test_removed_unnumbered_slide_uses_old_position(tmp_path):
    """§16.2: a removed slide without a number is labelled with the old slide's position; nothing else moves."""
    old = r3.build_deck(tmp_path / "old.pptx")
    new = remove_at(old, tmp_path / "new.pptx", 0)
    res = r4.deck_diff(old, new)
    assert [(c["field"], c["slide"]) for c in res["changes"]] == [("removed", "#1")]


def test_numbered_slide_label_is_string(tmp_path):
    """§16.2: `slide` is the number text as a string, also for `hidden`."""
    old = r3.build_deck(tmp_path / "old.pptx")
    new = r3.set_hidden(old, tmp_path / "new.pptx", "3", True)
    (c,) = r4.deck_diff(old, new)["changes"]
    assert c["slide"] == "3" and c["field"] == "hidden"


def test_cli_cut_json(ten, tmp_path, capsys):
    """§16.2/§0.4: the CLI prints the same result; slides are strings and `number` changes appear."""
    new = rebuilt(tmp_path, [0, 1, 2, 3, 4, 7, 8, 9])
    code, data, out, err = r4.run_cli(capsys, ["deck", "diff", ten, new, "--json"])
    assert code == 0, err
    assert all(isinstance(c["slide"], str) for c in data["changes"])
    assert sorted(c["field"] for c in data["changes"]) == ["number"] * 3 + ["removed"] * 2
