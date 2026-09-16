"""MANIFEST §15.4 `deck_diff` / `tundlekit deck diff` (hand edits back into build scripts), §15.10 registration.

Decks are built with deck_build (§3.2) and copies are hand-edited with python-pptx.
"""
from __future__ import annotations

import pytest

import helpers_r3 as r3

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

OLD_TITLE = "Execution Broker isolates side effects"
NEW_TITLE = "Execution Broker contains side effects"


@pytest.fixture
def deck(tmp_path):
    return r3.build_deck(tmp_path / "old.pptx")


def diff(old, new, **kw):
    res = r3.call("deck_diff", old=str(old), new=str(new), **kw)
    assert isinstance(res["changes"], list)
    for c in res["changes"]:
        assert set(c) >= {"slide", "field", "old", "new", "diff", "hint"}
        assert c["field"] in ("title", "text", "notes", "hidden", "added", "removed", "moved")
        assert isinstance(c["hint"], list) and len(c["hint"]) <= 3
    return res


def test_registered_in_deck_module_read_only():
    """§15.10: deck_diff is registered by tundlekit.deck and is read-only (§0.2 schema rules)."""
    t = r3.get_tool("deck_diff")
    assert t.annotations.get("readOnlyHint") is True
    assert t.input_schema["type"] == "object"
    assert t.input_schema.get("additionalProperties") is False
    assert {"old", "new", "search"} <= set(t.input_schema["properties"])


def test_identical_copy_has_no_changes(deck, tmp_path):
    """§15.4: an identical deck gives changes: []."""
    import shutil

    copy = tmp_path / "copy.pptx"
    shutil.copyfile(deck, copy)
    assert diff(deck, copy)["changes"] == []


def test_rebuilt_same_spec_has_no_changes(deck, tmp_path):
    """§15.4: decks compare by their deck_inspect outputs, so a rebuild of the same spec is identical."""
    again = r3.build_deck(tmp_path / "again.pptx")
    assert diff(deck, again)["changes"] == []


def test_changed_title(deck, tmp_path):
    """§15.4: a title edit is a `title` change on the slide's number with a unified diff."""
    new = r3.edit_frame(deck, tmp_path / "new.pptx", "3", OLD_TITLE, NEW_TITLE)
    res = diff(deck, new)
    titles = r3.changes_of(res, "title")
    assert len(titles) == 1
    c = titles[0]
    assert str(c["slide"]) == "3"
    assert c["old"] == OLD_TITLE and c["new"] == NEW_TITLE
    assert isinstance(c["diff"], str)
    assert "-" + OLD_TITLE in c["diff"] and "+" + NEW_TITLE in c["diff"]
    for field in ("notes", "hidden", "added", "removed", "moved"):
        assert r3.changes_of(res, field) == [], field


def test_changed_notes(deck, tmp_path):
    """§15.4: a notes edit is a `notes` change with old/new notes text and a unified diff."""
    new_notes = "TIME 0:30\nSAY: Kept tools failed the held-out tests in most runs we looked at."
    new = r3.edit_notes(deck, tmp_path / "new.pptx", "2", new_notes)
    res = diff(deck, new)
    notes = r3.changes_of(res, "notes")
    assert len(notes) == 1
    c = notes[0]
    assert str(c["slide"]) == "2"
    assert "keeping a tool is not evidence" in c["old"]
    assert "in most runs we looked at" in c["new"]
    assert isinstance(c["diff"], str) and "in most runs we looked at" in c["diff"]
    assert r3.changes_of(res, "title") == [] and r3.changes_of(res, "text") == []


def test_hidden_slide(deck, tmp_path):
    """§15.4: hiding a slide is a `hidden` change with booleans and diff null."""
    new = r3.set_hidden(deck, tmp_path / "new.pptx", "4", True)
    res = diff(deck, new)
    assert len(res["changes"]) == 1
    c = res["changes"][0]
    assert c["field"] == "hidden"
    assert str(c["slide"]) == "4"
    assert c["old"] is False and c["new"] is True
    assert c["diff"] is None


def test_removed_slide(deck, tmp_path):
    """§15.4: a deleted slide is a `removed` change carrying the old slide's number; slides pair by number."""
    new = r3.remove_slide(deck, tmp_path / "new.pptx", "3")
    res = diff(deck, new)
    removed = r3.changes_of(res, "removed")
    assert [str(c["slide"]) for c in removed] == ["3"]
    assert r3.changes_of(res, "added") == []
    assert r3.changes_of(res, "title") == []
    assert r3.changes_of(res, "notes") == []


def test_reordered_slides(deck, tmp_path):
    """§15.4: swapping 2 numbered slides gives `moved` changes with 1-based positions (pinned); nothing else
    changes."""
    new = r3.move_slide(deck, tmp_path / "new.pptx", 3, 4)   # slide "4" (position 4) <-> "5" (position 5)
    res = diff(deck, new)
    moved = r3.changes_of(res, "moved")
    assert moved, res
    allowed = {("4", 4, 5), ("5", 5, 4)}
    assert {(str(c["slide"]), c["old"], c["new"]) for c in moved} <= allowed
    assert all(c["diff"] is None for c in moved)
    others = [c for c in res["changes"] if c["field"] != "moved"]
    assert others == []


def test_changed_text_frame(deck, tmp_path):
    """§15.4: text is compared per frame; 1 edited frame gives 1 `text` change."""
    new = r3.edit_frame(deck, tmp_path / "new.pptx", "2", "•  first point\n•  second point",
                        "•  first point, restated")
    res = diff(deck, new)
    texts = r3.changes_of(res, "text")
    assert len(texts) == 1
    c = texts[0]
    assert str(c["slide"]) == "2"
    assert "second point" in c["old"]
    assert c["new"] == "•  first point, restated"
    assert isinstance(c["diff"], str)
    assert r3.changes_of(res, "title") == []


def test_hint_points_at_build_script(deck, tmp_path, monkeypatch):
    """§15.4: hint lists `path:line` where the old string occurs in files under `search` (.py walked); with a
    relative search entry the hint path is relative (pinned)."""
    monkeypatch.chdir(tmp_path)
    src = tmp_path / "src"
    script = r3.write(src / "build_deck.py",
                      "import json\n\nSLIDES = [\n    dict(\n        number=3,\n"
                      f"        title={OLD_TITLE!r},\n    ),\n]\n")
    r3.write(src / "notes.txt", OLD_TITLE + "\n")   # not a .py/.json/.md file: never hinted
    new = r3.edit_frame(deck, tmp_path / "new.pptx", "3", OLD_TITLE, NEW_TITLE)
    (c,) = r3.changes_of(diff(deck, new, search=["src"]), "title")
    assert [r3.slash(h) for h in c["hint"]] == ["src/build_deck.py:6"]
    assert r3.hint_matches(c["hint"][0], script, 6)


def test_hint_falls_back_to_longest_line(deck, tmp_path):
    """§15.4: when the whole old string is absent, its longest line of 12+ characters is searched."""
    src = tmp_path / "src"
    spec_md = r3.write(src / "deck-plan.md",
                       "# Plan\n\nSlide 3 body:\n\nthe broker leases each capability for one run only\n")
    old = "one broker per run\nthe broker leases each capability for one run only"
    new = r3.edit_frame(deck, tmp_path / "new.pptx", "3", old, "one broker per run")
    (c,) = r3.changes_of(diff(deck, new, search=[str(src)]), "text")
    assert c["old"] == old
    assert len(c["hint"]) == 1 and r3.hint_matches(c["hint"][0], spec_md, 5), c["hint"]


def test_hint_empty_when_not_found(deck, tmp_path):
    """§15.4: otherwise hint is []."""
    src = tmp_path / "src"
    r3.write(src / "build.py", "print('nothing relevant here')\n")
    new = r3.edit_frame(deck, tmp_path / "new.pptx", "3", OLD_TITLE, NEW_TITLE)
    (c,) = r3.changes_of(diff(deck, new, search=[str(src)]), "title")
    assert c["hint"] == []


def test_cli_deck_diff_json(deck, tmp_path, capsys):
    """§15.4/§15.10: `tundlekit deck diff OLD NEW --json` prints the result."""
    new = r3.set_hidden(deck, tmp_path / "new.pptx", "5", True)
    code, data, out, err = r3.run_cli(capsys, ["deck", "diff", deck, new, "--json"])
    assert code == 0, err
    assert [(c["field"], str(c["slide"])) for c in data["changes"]] == [("hidden", "5")]


def test_missing_deck_is_tool_error(deck, tmp_path):
    """§0.2: a missing input is a ToolError."""
    with pytest.raises(r3.tool_error()):
        r3.call("deck_diff", old=str(deck), new=str(tmp_path / "nope.pptx"))
