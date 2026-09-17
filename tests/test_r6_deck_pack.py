"""Visible tests for `deck_pack` (MANIFEST §18.2, registration §18.6, conventions §0.2-§0.4)."""
from __future__ import annotations

import pytest

import helpers_r6p as h

T = h.STD_TITLES
STD_TEXT = h.STD_TEXT


@pytest.fixture
def std(tmp_path):
    return h.build(tmp_path / "std.pptx")


# ------------------------------------------------------------------------------------ generate (§18.2.1)
def test_generate_exact_text_and_result(std):
    res = h.pack(std)
    assert res["text"] == STD_TEXT
    assert res["path"] is None and res["written"] is False
    assert (res["core_time"], res["total_time"]) == ("2:15", "2:55")
    assert res["warnings"] == []


def test_result_slides_carry_keys_flags_seconds_and_asked(std):
    slides = h.pack(std)["slides"]
    assert [s["key"] for s in slides] == h.STD_KEYS
    assert [s["position"] for s in slides] == list(range(1, 8))
    assert [s["insert"] for s in slides] == [False] * 4 + [True, True, False]
    assert [s["seconds"] for s in slides] == [20, 30, 10, 40, 25, 15, 35]
    assert [s["title"] for s in slides] == T
    assert slides[1]["asked"] == h.STD_ASKED
    assert slides[0]["asked"] == [] and slides[4]["asked"] == ["Is 96.8% comparable: no, different tools"]
    assert not any(s["hidden"] for s in slides)


def test_hidden_inserts_are_flagged_and_counted(tmp_path):
    deck = h.build(tmp_path / "hid.pptx", inserts="hidden")
    text = h.pack(deck)["text"]
    assert "· 7 slides (5 core, 2 inserts) · core 2:15 · with inserts 2:55" in text
    assert f"- slide 4a (insert, hidden): {T[4]}" in h.lines(text)
    assert f"- slide 4b (insert, hidden): {T[5]}" in h.lines(text)


def test_inserts_off_gives_core_only_numbering(tmp_path):
    deck = h.build(tmp_path / "off.pptx", inserts="off")
    res = h.pack(deck)
    assert [s["key"] for s in res["slides"]] == ["1", "2", "3", "4", "5"]
    assert "Deck: `off.pptx` · 5 slides (5 core, 0 inserts) · core 2:15 · with inserts 2:15" in res["text"]
    assert "|  | **Inserts** | 0:00 |  |" in h.lines(res["text"])


def test_hidden_core_slide_flag_and_time_still_counted(tmp_path, std):
    deck = h.hide(std, tmp_path / "h.pptx", 4)
    res = h.pack(deck)
    assert f"- slide 4 (hidden): {T[3]}" in h.lines(res["text"])
    assert res["slides"][3]["hidden"] is True
    assert res["core_time"] == "2:15"


def test_titles_collapse_whitespace_and_escape_pipes_in_table(tmp_path):
    spec = {"slides": [h.content("Gates   decide  admission"), h.content("Recall | precision")]}
    text = h.pack(h.build(tmp_path / "t.pptx", spec))["text"]
    ls = h.lines(text)
    assert "- slide 1: Gates decide admission" in ls
    assert "- slide 2: Recall | precision" in ls
    assert "| 1 | Gates decide admission | 0:30 | 0:30 |" in ls
    assert "| 2 | Recall \\| precision | 0:30 | 1:00 |" in ls


def test_if_asked_none(tmp_path):
    spec = {"slides": [h.title("Opening"), h.content("Only slide")]}
    text = h.pack(h.build(tmp_path / "n.pptx", spec))["text"]
    assert "\n## If asked\n\n(none)\n\n## Timing\n" in text


def test_if_asked_bullets_parse_continuations_and_stop_lines(tmp_path, std):
    notes = ("TIME 0:30\nSAY: short talk\nIF ASKED: first inline answer\n- second answer\ncontinued here\n\n"
             "- third answer\nMUST HIT: not a bullet\n- also not a bullet")
    deck = h.set_notes(std, tmp_path / "n.pptx", 2, notes)
    res = h.pack(deck)
    assert res["slides"][1]["asked"] == ["first inline answer", "second answer continued here", "third answer"]
    assert "- second answer continued here" in h.lines(res["text"])
    assert "not a bullet" not in res["text"]


def test_slide_without_time_counts_zero_and_warns(tmp_path, std):
    deck = h.set_notes(std, tmp_path / "t.pptx", 4, "SAY: no time here")
    res = h.pack(deck)
    assert res["warnings"] == ["slide 4: no TIME"]
    assert res["core_time"] == "1:35" and res["total_time"] == "2:15"
    assert f"| 4 | {T[3]} | - | 1:00 |" in h.lines(res["text"])


def test_out_writes_the_text(tmp_path, std):
    out = tmp_path / "PACK.md"
    res = h.pack(std, out=str(out))
    assert res["written"] is True and res["path"] == str(out)
    assert out.read_bytes().decode("utf-8").replace("\r\n", "\n") == res["text"] == STD_TEXT
    assert res["text"].endswith("\n") and not res["text"].endswith("\n\n")
    assert "\n\n\n" not in res["text"]


def test_existing_out_refused_unless_force(tmp_path, std):
    out = h.write(tmp_path / "PACK.md", "hand edits\n")
    with pytest.raises(h.tool_error()):
        h.pack(std, out=str(out))
    assert out.read_text(encoding="utf-8") == "hand edits\n"
    res = h.pack(std, out=str(out), force=True)
    assert res["written"] is True
    assert out.read_text(encoding="utf-8") == STD_TEXT


def test_without_out_nothing_is_written(tmp_path, std, monkeypatch):
    monkeypatch.chdir(tmp_path)
    before = sorted(p.name for p in tmp_path.iterdir())
    h.pack(std)
    assert sorted(p.name for p in tmp_path.iterdir()) == before


def test_out_and_check_together_is_an_error(tmp_path, std):
    p = h.write(tmp_path / "PACK.md", STD_TEXT)
    with pytest.raises(h.tool_error()):
        h.pack(std, out=str(tmp_path / "other.md"), check=str(p))
    assert not (tmp_path / "other.md").exists()


def test_cli_generate_and_check_exit_codes(tmp_path, std, capsys):
    out = tmp_path / "PACK.md"
    code, data, _, _ = h.run_cli(capsys, ["deck", "pack", std, "-o", out, "--json"])
    assert code == 0 and data["written"] is True and out.exists()
    code, data, _, _ = h.run_cli(capsys, ["deck", "pack", std, "--check", out, "--json"])
    assert code == 0 and data["findings"] == []
    stale = h.write(tmp_path / "S.md", STD_TEXT.replace("2:55", "3:10"))
    assert h.run_cli(capsys, ["deck", "pack", std, "--check", stale, "--json"])[0] == 0
    assert h.run_cli(capsys, ["deck", "pack", std, "--check", stale, "--json", "--strict"])[0] == 1
    bad = h.write(tmp_path / "B.md", STD_TEXT.replace("7 slides", "8 slides"))
    code, data, _, _ = h.run_cli(capsys, ["deck", "pack", std, "--check", bad, "--json"])
    assert code == 1 and data["ok"] is False


def test_registration_and_schema():
    h.call  # noqa: B018
    import importlib
    importlib.import_module("tundlekit.deck")
    t = importlib.import_module("tundlekit.registry").TOOLS["deck_pack"]
    s = t.input_schema
    assert set(s["properties"]) == {"pptx_path", "out", "force", "check"}
    assert s["required"] == ["pptx_path"] and s["additionalProperties"] is False
    assert t.annotations.get("readOnlyHint") is False and "destructiveHint" not in t.annotations


def test_tools_listing_includes_deck_pack(capsys):
    code, data, _, _ = h.run_cli(capsys, ["tools", "--json"])
    assert code == 0
    listing = {t["name"]: t for t in data["tools"]}
    assert listing["deck_pack"]["annotations"]["readOnlyHint"] is False
    assert 0 < len(listing["deck_pack"]["description"]) <= 1024


def test_generate_reports_deck_path_and_keeps_deck_unchanged(tmp_path, std):
    before = std.read_bytes()
    res = h.pack(std)
    assert res["deck"] == str(std)
    assert std.read_bytes() == before


def test_cli_out_and_check_together_fails(tmp_path, std, capsys):
    p = h.write(tmp_path / "PACK.md", STD_TEXT)
    code, _, _, _ = h.run_cli(capsys, ["deck", "pack", std, "-o", tmp_path / "x.md", "--check", p, "--json"])
    assert code in (1, 2)
    assert not (tmp_path / "x.md").exists()
