"""palette constants, tint and palette_get (MANIFEST §6)."""
import importlib

import pytest

from helpers_deck import call


@pytest.fixture
def pal():
    return importlib.import_module("tundlekit.palette")


def test_basic_constants(pal):
    # §6
    assert (pal.INK, pal.GREY, pal.HAIR, pal.PALE) == ("#000000", "#4d4d4d", "#9a9a9a", "#ececec")


def test_stage_values(pal):
    # §6 STAGE
    assert pal.STAGE == {
        "intent": "#0072B2", "binding": "#2A8FA8", "freeze": "#7B3FA0", "dispatch": "#D98200",
        "gates": "#008A63", "claims": "#B8527F", "build": "#3D4FB0", "library": "#8C5A2B",
        "external": "#6b6b6b",
    }


def test_outcome_values(pal):
    # §6 OUTCOME
    assert pal.OUTCOME == {"passed": "#008A63", "failed": "#D55E00", "skipped": "#bdbdbd",
                           "running": "#D98200", "ready": "#0072B2", "pending": "#ffffff"}


def test_ppt_values(pal):
    # §6: PPT = STAGE values without "#", upper-case
    assert pal.PPT["gates"] == "008A63"
    assert pal.PPT["external"] == "6B6B6B"
    assert set(pal.PPT) == set(pal.STAGE)


@pytest.mark.parametrize("color,amount,want", [
    ("#0072B2", 0.20, "#cce3f0"),   # 255-255*.2=204; 255-141*.2=226.8->227; 255-77*.2=239.6->240
    ("#000000", 0.18, "#d1d1d1"),   # 255-45.9=209.1 -> 209
    ("#ffffff", 0.5, "#ffffff"),
    ("#D98200", 1.0, "#d98200"),    # amount 1 keeps the colour, lower-cased
    ("#7B3FA0", 0.0, "#ffffff"),    # amount 0 is white
])
def test_tint_values(pal, color, amount, want):
    # §6 tint formula
    assert pal.tint(color, amount) == want


def test_tint_default_amount_and_no_hash(pal):
    # §6: default amount 0.18; input with or without "#"
    assert pal.tint("000000") == "#d1d1d1"
    assert pal.tint("#000000") == pal.tint("000000")


@pytest.mark.parametrize("bad", ["#12345", "zzzzzz", "", "#1234567"])
def test_tint_invalid_raises_value_error(pal, bad):
    # §6: invalid input raises ValueError
    with pytest.raises(ValueError):
        pal.tint(bad)


def test_palette_get_tool(pal):
    # §6 palette_get result
    res = call("palette_get")
    assert res["stage"] == pal.STAGE
    assert res["outcome"] == pal.OUTCOME
    assert (res["ink"], res["grey"], res["hair"], res["pale"]) == ("#000000", "#4d4d4d", "#9a9a9a", "#ececec")
    assert isinstance(res["rules"], list) and res["rules"]
    assert all(isinstance(r, str) and r for r in res["rules"])


def test_palette_get_rules_content():
    # §6: rules state colour = stage, style = actor, 1 box per model call, legend, no reliance on colour alone
    text = " ".join(call("palette_get")["rules"]).lower()
    for word in ("stage", "actor", "box", "model", "legend"):
        assert word in text, word
    assert "colour" in text or "color" in text
