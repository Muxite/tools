"""MANIFEST §16.7 (deck parts): deck lint `--ids` and the D013 message, strip-overlap warnings, chart `series`,
`pending` refused as highlight_color, table `mono_cols`."""
from __future__ import annotations

import json

import pytest

import helpers_r3 as r3
import helpers_r4d as r4

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


# ------------------------------------------------------------------------------------ deck lint --ids / D013
@pytest.fixture
def lint_case(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    deck = r3.build_deck(tmp_path / "capsule_v2.pptx")          # core time 2:15 (135 s)
    ledger = r4.write(tmp_path / "times.json", json.dumps({"capsule": 135, "workshop": 200}))
    return deck, ledger


def d013(res):
    return [f for f in res["findings"] if f["rule"] == "D013"]


def test_d013_names_present_keys_and_suggests_ids(lint_case, capsys):
    """§16.7: a missing id's D013 message names the keys present and suggests --ids."""
    code, data, out, err = r4.run_cli(capsys, ["deck", "lint", "capsule_v2.pptx", "--times-file", "times.json",
                                               "--json"])
    assert code == 1
    (f,) = d013(data)
    assert "capsule_v2" in f["message"]
    assert "capsule" in f["message"].replace("capsule_v2", "")      # the present key, not just the id
    assert "workshop" in f["message"]
    assert "--ids" in f["message"]


def test_cli_ids_selects_ledger_entry(lint_case, capsys):
    """§16.7/§14.4: `--ids capsule` maps the deck to its ledger entry; no D013."""
    code, data, out, err = r4.run_cli(capsys, ["deck", "lint", "capsule_v2.pptx", "--times-file", "times.json",
                                               "--ids", "capsule", "--json"])
    assert d013(data) == [], data["findings"]


def test_cli_ids_wrong_value_still_d013(lint_case, capsys):
    """§16.7: an id given with --ids that is absent from the ledger is a D013 naming the present keys."""
    code, data, out, err = r4.run_cli(capsys, ["deck", "lint", "capsule_v2.pptx", "--times-file", "times.json",
                                               "--ids", "capsul", "--json"])
    (f,) = d013(data)
    assert "workshop" in f["message"] and "capsul" in f["message"]


# ------------------------------------------------------------------------------------ strip overlap
POINT = {"kind": "point", "text": "One short point"}


def at(y, h=0.6, **kw):
    return dict(POINT, x=0.75, y=y, w=11.8, h=h, **kw)


@pytest.mark.parametrize("strip, bad_y, good_y", [
    ({"demonstrated_by": {"paper": "Beyond Task Completion", "setup": "99 tasks"}}, 1.6, 3.0),
    ({"thus": "Gates keep the library honest."}, 6.2, 5.0),
])
def test_positioned_block_over_strip_warns(tmp_path, strip, bad_y, good_y):
    """§16.7: a positioned block overlapping a strip gives a warning; clear of it, none."""
    good = r4.build(tmp_path, r4.one_slide([at(good_y)], **strip), "good.pptx")
    assert good["warnings"] == []
    bad = r4.build(tmp_path, r4.one_slide([at(bad_y)], **strip), "bad.pptx")
    assert r4.slide_warnings(bad), bad["warnings"]


def test_stacked_block_over_positioned_block_warns(tmp_path):
    """§16.7: a stacked block that overlaps a positioned one gives a warning."""
    stacked = dict(POINT, h=0.6)                 # stacked from the top of the body area
    good = r4.build(tmp_path, r4.one_slide([stacked, at(4.0)]), "good.pptx")
    assert good["warnings"] == []
    bad = r4.build(tmp_path, r4.one_slide([stacked, at(1.9)]), "bad.pptx")
    assert r4.slide_warnings(bad), bad["warnings"]


# ------------------------------------------------------------------------------------ charts
CATS = ["Q1", "Q2", "Q3"]
SERIES = [{"name": "kept", "values": [10, 20, 30]}, {"name": "passed", "values": [2, 5, 9]}]


@pytest.mark.parametrize("chart_type", ["bar", "line"])
def test_multi_series_chart_with_legend(tmp_path, chart_type):
    """§16.7: `series` gives a native chart with 1 series per entry and a legend."""
    body = {"kind": "chart", "categories": CATS, "series": SERIES, "chart_type": chart_type}
    res = r4.build(tmp_path, r4.one_slide(body))
    (chart,) = r4.charts(res["out"])
    plot_series = [s for p in chart.plots for s in p.series]
    assert [s.name for s in plot_series] == ["kept", "passed"]
    assert [list(s.values) for s in plot_series] == [[10, 20, 30], [2, 5, 9]]
    assert chart.has_legend is True
    assert ("LINE" in str(chart.chart_type)) == (chart_type == "line")


def test_single_values_chart_has_no_legend(tmp_path):
    """§3.2 unchanged: a `values` chart keeps 1 series and no legend."""
    res = r4.build(tmp_path, r4.one_slide({"kind": "chart", "categories": CATS, "values": [1, 2, 3]}))
    (chart,) = r4.charts(res["out"])
    assert len(list(chart.plots[0].series)) == 1
    assert chart.has_legend is False


def test_values_and_series_are_exclusive(tmp_path):
    """§16.7: giving both is a validation problem."""
    body = {"kind": "chart", "categories": CATS, "values": [1, 2, 3], "series": SERIES}
    with pytest.raises(r4.tool_error()) as e:
        r4.build(tmp_path, r4.one_slide(body))
    assert "slides[0].body" in str(e.value)


def test_series_length_mismatch_is_refused(tmp_path):
    """§3.1/§16.7: a series with a different number of values than categories is a validation problem."""
    body = {"kind": "chart", "categories": CATS,
            "series": [{"name": "kept", "values": [1, 2]}, {"name": "passed", "values": [1, 2, 3]}]}
    with pytest.raises(r4.tool_error()) as e:
        r4.build(tmp_path, r4.one_slide(body))
    assert "series" in str(e.value)


def test_pending_refused_as_highlight_color(tmp_path):
    """§16.7: `pending` (white) is refused for highlights; another outcome key still works."""
    body = {"kind": "chart", "categories": CATS, "values": [1, 2, 3], "highlight": 0}
    with pytest.raises(r4.tool_error()) as e:
        r4.build(tmp_path, r4.one_slide(dict(body, highlight_color="pending")))
    assert "highlight_color" in str(e.value)
    assert r4.build(tmp_path, r4.one_slide(dict(body, highlight_color="passed")))["out"]


# ------------------------------------------------------------------------------------ mono_cols
ROWS = [["Rule", "Pattern", "Meaning"], ["D003", "—", "em dash in a title"], ["D010", "et al.", "jargon"]]


def test_mono_cols_use_monospace_font(tmp_path):
    """§16.7: cells in `mono_cols` use the monospace font (the one `lines` with mono uses); others do not."""
    body = [{"kind": "lines", "items": ["tundle.sh status"], "mono": True},
            {"kind": "table", "rows": ROWS, "mono_cols": [1]}]
    res = r4.build(tmp_path, r4.one_slide(body))
    prs = r4.open_deck(res["out"])
    mono = {r.font.name for sh in prs.slides[0].shapes if sh.has_text_frame
            for p in sh.text_frame.paragraphs for r in p.runs if r.text == "tundle.sh status"}
    assert len(mono) == 1
    (table,) = r4.tables(res["out"])
    for i in range(len(ROWS)):
        assert r4.cell_fonts(table.cell(i, 1)) == mono
        assert r4.cell_fonts(table.cell(i, 0)).isdisjoint(mono)
        assert r4.cell_fonts(table.cell(i, 2)).isdisjoint(mono)


@pytest.mark.parametrize("bad", [[3], ["1"], 1, [-1]])
def test_bad_mono_cols_refused(tmp_path, bad):
    """§16.7/§3.1: mono_cols must list valid 0-based column indices."""
    with pytest.raises(r4.tool_error()) as e:
        r4.build(tmp_path, r4.one_slide({"kind": "table", "rows": ROWS, "mono_cols": bad}))
    assert "mono_cols" in str(e.value)
