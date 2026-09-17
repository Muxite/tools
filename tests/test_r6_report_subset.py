"""MANIFEST §18.1.1 supported Markdown (tables and excerpts are in test_r6_report_tables.py): each construct
maps to the paragraph/run structure of word/document.xml. Formatting is read through the style chain
(helpers_r6r.Styles), because §18.1.2 pins values, not where they are stored.
"""
from __future__ import annotations

import helpers_r6r as h


def doc(tmp_path, body, **kw):
    res = h.build(h.report(tmp_path, body), tmp_path / "out.docx", **kw)
    return res, res["out"]


def pairs(out):
    return [(s, t) for s, t, _ in h.paras(out)]


# ------------------------------------------------------------------------------------ headings, paragraphs
def test_headings_levels_trailing_hashes_and_bold(tmp_path):
    _, out = doc(tmp_path, "# One #\n\n## Two ##\n\n### Three\n\n   ## Indented\n")
    assert pairs(out) == [("Heading1", "One"), ("Heading2", "Two"), ("Heading3", "Three"), ("Heading2", "Indented")]
    st = h.Styles(out)
    assert all(st.on(r, p, "b") for _, _, p in h.paras(out) for _, r in h.runs(p))


def test_paragraph_lines_joined_and_ended_by_block_starts(tmp_path):
    _, out = doc(tmp_path, "Line one\nline two\n\nIntro:\n- a\n- b\nAfter list\n## Head\nTail\n")
    assert pairs(out) == [(None, "Line one line two"), (None, "Intro:"), ("ListBullet", "a"), ("ListBullet", "b"),
                          (None, "After list"), ("Heading2", "Head"), (None, "Tail")]


# ------------------------------------------------------------------------------------ lists
def test_bullets_and_second_level(tmp_path):
    _, out = doc(tmp_path, "- a\n* b\n+ c\n  - d\n\t- e\n - f\n")
    assert pairs(out) == [("ListBullet", "a"), ("ListBullet", "b"), ("ListBullet", "c"), ("ListBullet2", "d"),
                          ("ListBullet2", "e"), ("ListBullet", "f")]


def test_numbered_items_keep_marker_and_continuations(tmp_path):
    _, out = doc(tmp_path, "5. Five\n6) Six\n   continued here\n   and here\n10. Ten\n  3. Nested\n")
    assert pairs(out) == [("ListNumber", "5.  Five"), ("ListNumber", "6)  Six continued here and here"),
                          ("ListNumber", "10.  Ten"), ("ListNumber2", "3.  Nested")]


# ------------------------------------------------------------------------------------ quotes
def test_quote_joined_italic_and_depth_flattened(tmp_path):
    _, out = doc(tmp_path, "Before.\n\n> first line\n> second *em*\n>> deeper\n\nAfter.\n")
    assert pairs(out) == [(None, "Before."), ("Quote", "first line second em deeper"), (None, "After.")]
    st = h.Styles(out)
    p = h.paras(out)[1][2]
    assert all(st.on(r, p, "i") for _, r in h.runs(p))


# ------------------------------------------------------------------------------------ code
def test_code_block_breaks_tabs_and_no_inline(tmp_path):
    _, out = doc(tmp_path, "```python\n\n    x = 1  \n\ty\t= 2\n**not bold** `x`\n\n```\n")
    [(style, text, p)] = h.paras(out)
    assert style == "Code"
    assert text == "    x = 1\n\ty\t= 2\n**not bold** `x`"
    assert len([b for b in p.iter(h.W + "br") if b.get(h.W + "type") != "page"]) == 2
    assert len(list(p.iter(h.W + "tab"))) == 2
    st = h.Styles(out)
    assert not any(st.on(r, p, "b") for _, r in h.runs(p))


def test_tilde_and_indented_fences_and_empty_block(tmp_path):
    _, out = doc(tmp_path, "~~~\n```\ninner\n```\n~~~\n\n```\n\n\n```\n\n  ```\n  indented\n  ```\n")
    assert pairs(out) == [("Code", "```\ninner\n```"), ("Code", "  indented")]


# ------------------------------------------------------------------------------------ figures
def test_figure_png_extent_style_and_caption(tmp_path):
    h.png(tmp_path / "fig" / "a.png", 400, 300)
    h.jpeg(tmp_path / "b.jpg", 30, 45)
    res, out = doc(tmp_path, "![Fig. 1. The loop [2, Fig. 1].](fig/a.png)\n\n![Fig. 2. Photo.](b.jpg)\n")
    ps = h.paras(out)
    assert [s for s, _, _ in ps] == ["Figure", "Caption", "Figure", "Caption"]
    assert [t for _, t, _ in ps][1::2] == ["Fig. 1. The loop [2, Fig. 1].", "Fig. 2. Photo."]
    exts = [(int(e.get("cx")), int(e.get("cy"))) for e in h.xml(out).iter(h.WP + "extent")]
    assert exts == [(5943600, round(5943600 * 300 / 400)), (5943600, round(5943600 * 45 / 30))]
    media = sorted(n for n in h.names(out) if n.startswith("word/media/"))
    assert media == ["word/media/image1.png", "word/media/image2.jpeg"]
    assert res["figures"] == 2 and res["warnings"] == []


def test_figure_empty_alt_angle_target_title_and_percent(tmp_path):
    """TARGET up to the first whitespace, <...> removed, percent-decoded when the literal file is missing."""
    h.png(tmp_path / "fig one.png")
    h.png(tmp_path / "plain.png")
    body = ("![](plain.png)\n\n![Fig. 2. Titled.](plain.png \"A title\")\n\n"
            "![Fig. 3. Angle.](<plain.png>)\n\n![Fig. 4. Decoded.](fig%20one.png)\n")
    res, out = doc(tmp_path, body)
    assert [s for s, _, _ in h.paras(out)] == ["Figure", "Figure", "Caption", "Figure", "Caption", "Figure", "Caption"]
    assert res["figures"] == 4 and res["warnings"] == []


def test_inline_image_not_embedded_warns(tmp_path):
    h.png(tmp_path / "a.png")
    res, out = doc(tmp_path, "# T\n\nSee ![the chart](a.png) here.\n")
    assert res["figures"] == 0 and not list(h.xml(out).iter(h.WP + "extent"))
    assert h.paras(out)[1][:2] == (None, "See the chart here.")
    assert res["warnings"] == ["line 3: inline image not embedded"]


# ------------------------------------------------------------------------------------ breaks
def test_page_break_variants_and_thematic_breaks(tmp_path):
    res, out = doc(tmp_path, "One.\n\n\\newpage\n\n  \\clearpage{}  \n\n***\n\n- - -\n\n___\n\n\\pagebreak\n\nTwo.\n")
    ps = h.paras(out)
    assert [t for _, t, _ in ps] == ["One.", "\f", "\f", "\f", "Two."]
    for _, _, p in ps[1:4]:
        brs = list(p.iter(h.W + "br"))
        assert len(brs) == 1 and brs[0].get(h.W + "type") == "page" and not list(p.iter(h.W + "t"))
    assert res["page_breaks"] == 3


# ------------------------------------------------------------------------------------ captions and inline
def test_paragraph_captions_only_star_table(tmp_path):
    _, out = doc(tmp_path, "*Table 1. Terms.*\n\n**Table 2. Bold.**\n\n*Figure 3. Not a caption.*\n\n"
                           "*Table 4.* and more\n")
    assert pairs(out) == [("Caption", "Table 1. Terms."), (None, "Table 2. Bold."),
                          (None, "Figure 3. Not a caption."), (None, "Table 4. and more")]
    st = h.Styles(out)
    p = h.paras(out)[0][2]
    r = h.runs(p)[0][1]
    assert st.on(r, p, "i") and st.size(r, p) == 19 and st.rpr(r, p, "color").upper() == "595959"


def test_inline_markup_runs(tmp_path):
    body = ("A **bold** and *it* and __b2__ and _i2_ and ***bi*** and snake_case_name and `code x` "
            "and [link](http://e.com) and [ref][r1] and <https://auto.example> and \\*esc\\* end.\n")
    _, out = doc(tmp_path, body)
    [(style, text, p)] = h.paras(out)
    assert style is None
    assert " ".join(text.split()) == ("A bold and it and b2 and i2 and bi and snake_case_name and code x and link "
                                      "and ref and https://auto.example and *esc* end.")
    st = h.Styles(out)
    fmt = {t: (st.on(r, p, "b"), st.on(r, p, "i")) for t, r in h.runs(p)}
    assert fmt["bold"] == (True, False) and fmt["b2"] == (True, False)
    assert fmt["it"] == (False, True) and fmt["i2"] == (False, True) and fmt["bi"] == (True, True)
    code = h.run_with(p, "code x")
    assert st.font(code, p) == "Consolas" and st.size(code, p) == 20
    assert not list(h.xml(out).iter(h.W + "hyperlink"))
    assert all(not (b or i) for t, (b, i) in fmt.items() if "snake_case_name" in t)


# ------------------------------------------------------------------------------------ preprocessing
def test_comments_front_matter_and_line_numbers(tmp_path):
    msg = h.build_error(h.report(tmp_path, "---\na: b\n---\n<!-- x\ny\n-->\n\n#### deep\n"), tmp_path / "o.docx")
    assert "line 8: " in msg
    _, out = doc(tmp_path, "---\ntitle: meta\n...\n# Real\n\nText <!-- hidden --> shown.\n")
    assert [(s, " ".join(t.split())) for s, t in pairs(out)] == [("Heading1", "Real"), (None, "Text shown.")]


def test_crlf_and_cr_line_endings(tmp_path):
    body = "# T\n\n- a\n- b\n\nPara one\npara two\n"
    h.write(tmp_path / "lf.md", body)
    h.write(tmp_path / "crlf.md", body, newline="\r\n")
    a = h.build(tmp_path / "lf.md", tmp_path / "a.docx")["out"]
    b = h.build(tmp_path / "crlf.md", tmp_path / "b.docx")["out"]
    assert pairs(a) == pairs(b)
    h.write(tmp_path / "cr.md", "# T\n\n#### deep\n", newline="\r")
    assert "line 3: " in h.build_error(tmp_path / "cr.md", tmp_path / "c.docx")
