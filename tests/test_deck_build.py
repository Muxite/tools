"""deck_build: the built file (MANIFEST §3.2)."""
import pytest

from helpers_deck import (EMU_PER_INCH, STAGE, all_text, build, charts, content, data_labels_on, divider,
                          frame_is_bold, frame_texts, frames, is_hidden, is_mono, make_png, need_office,
                          notes_text, numbers_on, pictures, point_fill, spec, tables, title_slide)


@pytest.fixture(autouse=True)
def _office():
    need_office()


# ------------------------------------------------------------------ page and slide count
def test_slide_size_and_count(tmp_path):
    # §3.2: 13.333 x 7.5 in, 1 slide per spec slide
    _, prs = build(tmp_path, spec(title_slide(), divider(), content(), content()))
    assert prs.slide_width / EMU_PER_INCH == pytest.approx(13.333, abs=0.01)
    assert prs.slide_height / EMU_PER_INCH == pytest.approx(7.5, abs=0.01)
    assert len(prs.slides) == 4


# ------------------------------------------------------------------ content slide parts
def test_content_slide_eyebrow_upper_title_exact_and_number(tmp_path):
    # §3.2: eyebrow in upper case; title text box exactly the title; number box exactly the number
    s = content(title="96.8% of kept tools fail held-out tests", eyebrow="Research")
    _, prs = build(tmp_path, spec(s))
    texts = frame_texts(prs.slides[0])
    assert "RESEARCH" in texts
    assert "96.8% of kept tools fail held-out tests" in texts
    assert numbers_on(prs.slides[0]) == ["1"]


def test_source_footer_present(tmp_path):
    # §3.2: the source footer (if given)
    _, prs = build(tmp_path, spec(content(source="Beyond Task Completion, Table 4")))
    assert "Beyond Task Completion, Table 4" in all_text(prs.slides[0])


def test_demonstrated_by_strip_text(tmp_path):
    # §3.2: DEMONSTRATED BY   {paper}  ·  {setup}
    s = content(demonstrated_by={"paper": "Beyond Task Completion (arXiv 2604.00392)",
                                 "setup": "99 tasks, 222 kept tools"})
    _, prs = build(tmp_path, spec(s))
    assert ("DEMONSTRATED BY   Beyond Task Completion (arXiv 2604.00392)  ·  99 tasks, 222 kept tools"
            in frame_texts(prs.slides[0]))


def test_thus_strip_text(tmp_path):
    # §3.2: THUS   {thus}
    _, prs = build(tmp_path, spec(content(thus="cap the tries at 3", stage="gates")))
    assert "THUS   cap the tries at 3" in frame_texts(prs.slides[0])


def test_phase_strip_text(tmp_path):
    # §3.2: IN   {in}        OUT   {out}
    _, prs = build(tmp_path, spec(content(phase={"in": "goal text", "out": "frozen contract"})))
    assert "IN   goal text        OUT   frozen contract" in frame_texts(prs.slides[0])


def test_no_strips_when_not_given(tmp_path):
    # §3.2: strips appear only with demonstrated_by / thus / phase
    _, prs = build(tmp_path, spec(content()))
    for t in frame_texts(prs.slides[0]):
        assert not t.startswith("DEMONSTRATED BY")
        assert not t.startswith("THUS   ")
        assert not t.startswith("IN   ")


def test_logo_added_when_file_exists(tmp_path):
    # §3.2: the logo (if meta.logo exists); relative to cwd for an inline spec (§3.1)
    make_png(tmp_path / "logo.png", 200, 200)
    s = spec(content(body={"kind": "bullets", "items": ["x"]}), logo=str(tmp_path / "logo.png"))
    _, prs = build(tmp_path, s)
    assert len(pictures(prs.slides[0])) == 1


def test_no_pictures_without_logo_on_bullet_slide(tmp_path):
    # §3.2: the logo only if meta.logo exists
    _, prs = build(tmp_path, spec(content()))
    assert pictures(prs.slides[0]) == []


# ------------------------------------------------------------------ bodies
def test_bullets_are_paragraphs_with_bullet_prefix(tmp_path):
    # §3.2: bullets are paragraphs "•  {item}"
    items = ["kept tools fail", "gates catch it", "tries are capped"]
    _, prs = build(tmp_path, spec(content(body={"kind": "bullets", "items": items})))
    want = [f"•  {i}" for i in items]
    paras = [[p.text for p in f.paragraphs] for f in frames(prs.slides[0])]
    assert want in paras


def test_table_is_native_with_str_cells_and_header(tmp_path):
    # §3.2: native table, cell text == str(cell), first row as header
    rows = [["Tool", "Kept", "Pass rate"], ["alpha", 222, 3.2], ["beta", 0, 96.8]]
    _, prs = build(tmp_path, spec(content(body={"kind": "table", "rows": rows})))
    tbls = tables(prs.slides[0])
    assert len(tbls) == 1
    t = tbls[0]
    assert len(t.rows) == 3 and len(t.columns) == 3
    got = [[t.cell(i, j).text for j in range(3)] for i in range(3)]
    assert got == [[str(c) for c in r] for r in rows]
    assert t.first_row is True


def test_table_widths_accepted(tmp_path):
    # §3.1: optional widths, 1 per column
    rows = [["a", "b"], ["c", "d"]]
    _, prs = build(tmp_path, spec(content(body={"kind": "table", "rows": rows, "widths": [3, 1]})))
    t = tables(prs.slides[0])[0]
    assert len(t.columns) == 2


def test_figure_wide_image_scaled_to_width(tmp_path):
    # §3.2: picture scaled to fit 11.8 x 5.3 in, keeping aspect ratio (4:1 -> 11.8 x 2.95)
    make_png(tmp_path / "wide.png", 2000, 500)
    _, prs = build(tmp_path, spec(content(body={"kind": "figure", "path": str(tmp_path / "wide.png")})))
    pics = pictures(prs.slides[0])
    assert len(pics) == 1
    w, h = pics[0].width / EMU_PER_INCH, pics[0].height / EMU_PER_INCH
    assert w == pytest.approx(11.8, abs=0.02)
    assert h == pytest.approx(2.95, abs=0.02)


def test_figure_tall_image_scaled_to_height(tmp_path):
    # §3.2: 1:2 image -> 2.65 x 5.3 in
    make_png(tmp_path / "tall.png", 600, 1200)
    _, prs = build(tmp_path, spec(content(body={"kind": "figure", "path": str(tmp_path / "tall.png")})))
    pic = pictures(prs.slides[0])[0]
    assert pic.height / EMU_PER_INCH == pytest.approx(5.3, abs=0.02)
    assert pic.width / EMU_PER_INCH == pytest.approx(2.65, abs=0.02)


def test_excerpt_lines_in_monospace(tmp_path):
    # §3.2: excerpt is a shape whose text frame holds the lines in a monospace font
    text = "def gate(tool):\n    return tool.passes(held_out)"
    _, prs = build(tmp_path, spec(content(body={"kind": "excerpt", "text": text})))
    lines = text.split("\n")
    hits = [f for f in frames(prs.slides[0]) if [p.text for p in f.paragraphs] == lines]
    assert hits, frame_texts(prs.slides[0])
    for p in hits[0].paragraphs:
        for r in p.runs:
            assert is_mono(r.font.name or p.font.name), r.font.name


def test_chart_body_is_native_bar_chart(tmp_path):
    # §3.2: native bar chart, 1 series, categories and values, data labels on
    body = {"kind": "chart", "categories": ["kept", "passed", "failed"], "values": [222, 7, 215]}
    _, prs = build(tmp_path, spec(content(body=body, stage="gates")))
    ch = charts(prs.slides[0])
    assert len(ch) == 1
    c = ch[0]
    name = c.chart_type.name if c.chart_type is not None else ""
    assert "BAR" in name or "COLUMN" in name
    plot = c.plots[0]
    assert len(list(plot.series)) == 1
    assert list(plot.categories) == ["kept", "passed", "failed"]
    assert list(plot.series[0].values) == pytest.approx([222, 7, 215])
    assert data_labels_on(c)


def test_chart_highlight_stage_colour_others_grey(tmp_path):
    # §3.2: highlighted point in a stage colour, the other points grey
    body = {"kind": "chart", "categories": ["a", "b", "c"], "values": [3, 5, 4], "highlight": 1}
    _, prs = build(tmp_path, spec(content(body=body, stage="gates")))
    ser = charts(prs.slides[0])[0].plots[0].series[0]
    hi = point_fill(ser, 1)
    assert hi in {v.lstrip("#").upper() for v in STAGE.values()}
    others = {point_fill(ser, 0), point_fill(ser, 2)}
    assert len(others) == 1
    grey = others.pop()
    assert grey is not None and grey != hi
    assert grey[0:2] == grey[2:4] == grey[4:6], grey


def test_chart_takeaway_bold(tmp_path):
    # §3.2: the takeaway as bold text
    body = {"kind": "chart", "categories": ["a", "b"], "values": [1, 2], "takeaway": "b doubles a"}
    _, prs = build(tmp_path, spec(content(body=body)))
    hits = [f for f in frames(prs.slides[0]) if f.text == "b doubles a"]
    assert hits
    assert frame_is_bold(hits[0])


def test_lines_body_builds(tmp_path):
    # §3.1: lines body with mono
    body = {"kind": "lines", "items": ["step one", "step two"], "mono": True}
    _, prs = build(tmp_path, spec(content(body=body)))
    txt = all_text(prs.slides[0])
    assert "step one" in txt and "step two" in txt


# ------------------------------------------------------------------ title and divider
def test_title_slide_texts_and_no_number(tmp_path):
    # §3.2: title, subtitle and byline text boxes; title slides show no number
    s = title_slide(title="Capability capsules", subtitle="Building tools safely", byline="M. Muk, 2026")
    _, prs = build(tmp_path, spec(s))
    texts = frame_texts(prs.slides[0])
    for want in ("Capability capsules", "Building tools safely", "M. Muk, 2026"):
        assert want in texts
    assert numbers_on(prs.slides[0]) == []


def test_divider_texts_and_no_number(tmp_path):
    # §3.2: divider has title and subtitle text boxes, no number
    _, prs = build(tmp_path, spec(title_slide(), divider(title="The evidence", subtitle="what was measured")))
    texts = frame_texts(prs.slides[1])
    assert "The evidence" in texts and "what was measured" in texts
    assert numbers_on(prs.slides[1]) == []


# ------------------------------------------------------------------ numbering
def test_numbering_title_and_divider_advance_counter(tmp_path):
    # §3.2: title/divider advance the core counter but show no number
    res, prs = build(tmp_path, spec(title_slide(), content(), divider(), content(), content()))
    assert [numbers_on(s) for s in prs.slides] == [[], ["2"], [], ["4"], ["5"]]
    assert [x["number"] for x in res["slides"]] == [None, "2", None, "4", "5"]


def test_insert_numbering_letters(tmp_path):
    # §3.2: insert after core n is n + a, b, ...; letters restart after each core slide
    s = spec(content(), content(insert=True), content(insert=True), content(), content(insert=True))
    res, prs = build(tmp_path, s)
    assert [x["number"] for x in res["slides"]] == ["1", "1a", "1b", "2", "2a"]
    assert [numbers_on(sl) for sl in prs.slides] == [["1"], ["1a"], ["1b"], ["2"], ["2a"]]
    assert [x["insert"] for x in res["slides"]] == [False, True, True, False, True]


# ------------------------------------------------------------------ notes
def test_notes_full_format_byte_exact(tmp_path):
    # §3.2 notes format
    s = content(time="0:45", say="Most kept tools fail.", asked=["Why cap tries: cost.", "Which tasks: 99."])
    _, prs = build(tmp_path, spec(s))
    assert notes_text(prs.slides[0]) == (
        "TIME 0:45\nSAY: Most kept tools fail.\nIF ASKED:\n- Why cap tries: cost.\n- Which tasks: 99.")


def test_notes_time_only_when_say_empty(tmp_path):
    # §3.2: optional parts are omitted when empty
    d = divider(time="0:05")
    d["notes"] = {"time": "0:05"}
    _, prs = build(tmp_path, spec(title_slide(), d))
    assert notes_text(prs.slides[1]) == "TIME 0:05"


def test_notes_insert_slide_prefix(tmp_path):
    # §3.2: INSERT line first on insert slides
    s = spec(content(), content(insert=True, time="1:00", say="Extra detail."))
    _, prs = build(tmp_path, s)
    assert notes_text(prs.slides[1]) == (
        "INSERT: optional slide; delete or hide it and the talk flows unchanged\n"
        "TIME 1:00\nSAY: Extra detail.")
    assert not notes_text(prs.slides[0]).startswith("INSERT:")


# ------------------------------------------------------------------ inserts mode
def test_inserts_shown_default(tmp_path):
    # §3.2: shown -> inserts are normal slides
    res, prs = build(tmp_path, spec(content(), content(insert=True)))
    assert res["inserts"] == "shown"
    assert len(prs.slides) == 2
    assert not any(is_hidden(s) for s in prs.slides)


def test_inserts_hidden_from_meta(tmp_path):
    # §3.2: hidden -> show="0" on insert slides only
    res, prs = build(tmp_path, spec(content(), content(insert=True), content(), inserts="hidden"))
    assert res["inserts"] == "hidden"
    assert [is_hidden(s) for s in prs.slides] == [False, True, False]


def test_inserts_off_argument_overrides_meta(tmp_path):
    # §3.2: inserts argument overrides meta; off -> insert slides absent
    s = spec(content(title="Core one"), content(title="Extra", insert=True), content(title="Core two"),
             inserts="shown")
    res, prs = build(tmp_path, s, inserts="off")
    assert res["inserts"] == "off"
    assert len(prs.slides) == 2
    assert res["core_slides"] == 2
    assert res["insert_slides"] == 1
    assert len(res["slides"]) == 3
    for sl in prs.slides:
        assert "Extra" not in frame_texts(sl)
        assert not notes_text(sl).startswith("INSERT:")
    assert [numbers_on(sl) for sl in prs.slides] == [["1"], ["2"]]
