"""Visible tests for `deck_pack` check mode (MANIFEST §18.2.2, §0.3, §0.4, §18.6).

Split from test_r6_deck_pack.py to keep files short; shared fixtures come from helpers_r6p.
"""
from __future__ import annotations

import pytest

import helpers_r6p as h

T = h.STD_TITLES
STD_TEXT = h.STD_TEXT


@pytest.fixture
def std(tmp_path):
    return h.build(tmp_path / "std.pptx")

# ------------------------------------------------------------------------------------ check (§18.2.2)
def test_fresh_pack_checks_clean(tmp_path, std):
    out = tmp_path / "PACK.md"
    h.pack(std, out=str(out))
    res = h.check(std, out)
    assert res["findings"] == [] and res["ok"] is True
    assert res["form"] == "generated"
    assert res["stated"] == {"slides": 7, "times": ["2:15", "2:55"]}
    assert res["deck"] == {"slides": 7, "core": 5, "inserts": 2, "core_time": "2:15", "total_time": "2:55"}
    assert [c["key"] for c in res["crib"]] == h.STD_KEYS
    assert [c["slide"] for c in res["crib"]] == list(range(1, 8))
    assert res["crib"][0]["line"] == h.line_of(STD_TEXT, "- slide 1:")


def test_changed_title_gives_one_k004(tmp_path, std):
    out = h.write(tmp_path / "PACK.md", STD_TEXT)
    deck = h.set_text(std, tmp_path / "new.pptx", 4, T[3], "Gates admit capsules")
    res = h.check(deck, out)
    assert h.rules(res) == ["K004"]
    f = res["findings"][0]
    assert f["severity"] == "warning" and f["line"] == h.line_of(STD_TEXT, "- slide 4:")
    assert T[3] in f["message"] and "Gates admit capsules" in f["message"]
    assert res["ok"] is True


def test_k004_ignores_a_note_after_middle_dot(tmp_path, std):
    text = STD_TEXT.replace(f"- slide 4: {T[3]}\n", f"- slide 4: {T[3]} · pause for questions\n")
    assert h.check(std, h.write(tmp_path / "P.md", text))["findings"] == []


def test_k001_stated_count_mismatch(tmp_path, std):
    text = STD_TEXT.replace("· 7 slides (", "· 9 slides (")
    res = h.check(std, h.write(tmp_path / "P.md", text))
    k = h.by_rule(res, "K001")
    assert len(k) == 1 and k[0]["severity"] == "error" and k[0]["line"] == 3
    assert res["ok"] is False and res["stated"]["slides"] == 9


def test_k001_accepts_core_count(tmp_path, std):
    text = STD_TEXT.replace("· 7 slides (", "· 5 slides (")
    assert h.by_rule(h.check(std, h.write(tmp_path / "P.md", text)), "K001") == []


def test_k006_stale_time(tmp_path, std):
    text = STD_TEXT.replace("with inserts 2:55", "with inserts 3:10")
    res = h.check(std, h.write(tmp_path / "P.md", text))
    k = h.by_rule(res, "K006")
    assert len(k) == 1 and k[0]["severity"] == "warning" and k[0]["line"] == 3
    assert res["stated"]["times"] == ["2:15", "3:10"] and res["ok"] is True


def test_k002_unknown_and_repeated_keys(tmp_path, std):
    text = STD_TEXT.replace("- slide 5: ", "- slide 9: extra slide\n- slide 2: again\n- slide 5: ")
    res = h.check(std, h.write(tmp_path / "P.md", text))
    k = h.by_rule(res, "K002")
    assert [f["line"] for f in k] == [h.line_of(text, "- slide 9:"), h.line_of(text, "- slide 2: again")]
    assert all(f["severity"] == "error" for f in k) and res["ok"] is False
    assert h.by_rule(res, "K003") == []


def test_no_crib_section_is_one_k002(tmp_path, std):
    text = "# Presenter pack: x\n\nDeck with 7 slides.\n\n## Talk\n\n- slide 1: something\n"
    res = h.check(std, h.write(tmp_path / "P.md", text))
    assert h.rules(res) == ["K002"] and res["findings"][0]["line"] is None


def test_k003_missing_slides(tmp_path, std):
    text = STD_TEXT.replace(f"- slide 4a (insert): {T[4]}\n", "").replace(f"- slide 3: {T[2]}\n", "")
    res = h.check(std, h.write(tmp_path / "P.md", text))
    k = h.by_rule(res, "K003")
    assert len(k) == 2 and all(f["line"] == h.line_of(text, "## Crib") for f in k)
    msg3 = next(f["message"] for f in k if T[2] in f["message"])
    msg4a = next(f["message"] for f in k if T[4] in f["message"])
    assert h.names_key(msg3, "3") and "insert" not in msg3
    assert "4a" in msg4a and "insert" in msg4a


def test_hand_form_k005_low_score_names_best_match(tmp_path):
    spec = {"slides": [h.content("Quokka habitats shrink yearly"), h.content("Marmot burrows collapse"),
                       h.content("Wombat droppings cube")]}
    deck = h.build(tmp_path / "d.pptx", spec)
    text = h.hand_pack(["- slide 1: quokka habitats shrink", "- slide 2: marmot burrows collapse",
                        "- slide 3: marmot burrows collapse"])
    res = h.check(deck, h.write(tmp_path / "P.md", text))
    assert res["form"] == "hand"
    k = h.by_rule(res, "K005")
    assert len(k) == 1 and k[0]["line"] == h.line_of(text, "- slide 3:") and k[0]["severity"] == "warning"
    assert h.names_key(k[0]["message"], "2")
    assert h.by_rule(res, "K004") == [] and h.by_rule(res, "K002") == []
    assert [c["score"] for c in res["crib"]] == [1.0, 1.0, 0.0]


@pytest.mark.parametrize("inserts", ["hidden", "off"])
def test_generated_pack_checks_clean_for_every_inserts_mode(tmp_path, inserts):
    deck = h.build(tmp_path / f"{inserts}.pptx", inserts=inserts)
    out = tmp_path / "PACK.md"
    h.pack(deck, out=str(out))
    res = h.check(deck, out)
    assert res["findings"] == [] and res["pack"] == str(out)


def test_generated_pack_with_missing_time_checks_clean(tmp_path, std):
    deck = h.set_notes(std, tmp_path / "t.pptx", 2, "SAY: nothing timed\nIF ASKED:\n- Why: because")
    out = tmp_path / "PACK.md"
    assert h.pack(deck, out=str(out))["warnings"] == ["slide 2: no TIME"]
    res = h.check(deck, out)
    assert res["findings"] == []
    assert res["stated"]["times"] == ["1:45", "2:25"]


def test_shown_pack_against_deck_built_without_inserts(tmp_path):
    shown = h.build(tmp_path / "std.pptx")
    out = tmp_path / "PACK.md"
    h.pack(shown, out=str(out))
    off = h.build(tmp_path / "off.pptx", inserts="off")
    res = h.check(off, out)
    assert h.rules(res) == ["K001", "K002", "K002", "K006"]
    assert [f["line"] for f in h.by_rule(res, "K002")] == [h.line_of(STD_TEXT, "- slide 4a"),
                                                           h.line_of(STD_TEXT, "- slide 4b")]
    assert res["deck"]["inserts"] == 0 and res["deck"]["total_time"] == "2:15"


def test_hand_pack_in_workflow_style_and_hidden_core_k003(tmp_path, std):
    deck = h.hide(std, tmp_path / "h.pptx", 7)
    crib = [f"- {k}: {t.lower()}" for k, t in zip(h.STD_KEYS[:6], T[:6])]
    text = h.hand_pack(crib, header="Against the deck (7 slides, 2:55).")
    res = h.check(deck, h.write(tmp_path / "P.md", text))
    assert res["form"] == "hand"
    assert [c["key"] for c in res["crib"]] == h.STD_KEYS[:6]
    assert res["crib"][4]["text"] == T[4].lower()
    assert [c["score"] for c in res["crib"]] == [1.0, 1.0, None, 1.0, 1.0, None]   # 1 key word: null
    k = h.by_rule(res, "K003")
    assert len(k) == 1 and "hidden" in k[0]["message"] and T[6] in k[0]["message"]
    assert h.names_key(k[0]["message"], "5") and "insert" not in k[0]["message"]
    assert h.rules(res) == ["K003"]
