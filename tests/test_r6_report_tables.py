"""MANIFEST §18.1.3 tables, §18.1.1 excerpts, §18.1.2 page/styles/core properties/package, and acceptance
A2/A4 (§18.1.4) for `report_build`. Only what §18.1.2 pins is asserted (not theme, docDefaults, numbering
definitions, relationship ids or layout).
"""
from __future__ import annotations

import os
import re
import subprocess

import pytest

import helpers_r6r as h

TABLE = """Intro words here.

| Term | Meaning of the term, which is a much longer description column |
|:---|---:|
| capsule | A contract for 1 capability, written in YAML with typed inputs, outputs and effects on the system |
| gate | A check that decides **PASS** or FAIL, with `code` |
| short |
| pipe | a \\| b |

*Table 1. Terms.*
"""


def tbl_doc(tmp_path, body=TABLE):
    res = h.build(h.report(tmp_path, body), tmp_path / "out.docx")
    return res, res["out"]


def widths(tbl):
    return [int(g.get(h.W + "w")) for g in tbl.findall("w:tblGrid/w:gridCol", h.NS)]


# ------------------------------------------------------------------------------------ tables §18.1.3
def test_table_cells_padding_escapes_and_counts(tmp_path):
    res, out = tbl_doc(tmp_path)
    [tbl] = h.tables(out)
    cells = h.cell_texts(tbl)
    assert cells[0] == ["Term", "Meaning of the term, which is a much longer description column"]
    assert cells[2] == ["gate", "A check that decides PASS or FAIL, with code"]
    assert cells[3] == ["short", ""]
    assert cells[4] == ["pipe", "a | b"]
    assert len(cells) == 5 and res["tables"] == 1
    assert res["words"] == 3 + 3, "table cells are not counted; caption is"
    assert [s for s, _, _ in h.paras(out)] == [None, "Caption"]


def test_table_header_rows_and_layout(tmp_path):
    _, out = tbl_doc(tmp_path)
    [tbl] = h.tables(out)
    rows = tbl.findall("w:tr", h.NS)
    head = rows[0]
    assert head.find("w:trPr/w:tblHeader", h.NS) is not None
    assert all(r.find("w:trPr/w:cantSplit", h.NS) is not None for r in rows)
    fills = [tc.find("w:tcPr/w:shd", h.NS) for tc in head.findall("w:tc", h.NS)]
    assert all(f is not None and f.get(h.W + "fill").upper() == "EDEDED" for f in fills)
    st = h.Styles(out)
    for tc in head.findall("w:tc", h.NS):
        for p in tc.findall("w:p", h.NS):
            assert all(st.on(r, p, "b") for _, r in h.runs(p))
    tblpr = tbl.find("w:tblPr", h.NS)
    assert tblpr.find("w:jc", h.NS).get(h.W + "val") == "center"
    assert tblpr.find("w:tblLayout", h.NS).get(h.W + "type") == "fixed"
    assert tblpr.find("w:tblStyle", h.NS).get(h.W + "val") == "TableGrid"


def test_table_widths_grid_and_cells(tmp_path):
    _, out = tbl_doc(tmp_path)
    [tbl] = h.tables(out)
    grid = widths(tbl)
    assert len(grid) == 2 and abs(sum(grid) - 9648) <= 2
    assert grid[1] > grid[0], "a column of long text is wider than a column of short words"
    for tr in tbl.findall("w:tr", h.NS):
        got = [int(tc.find("w:tcPr/w:tcW", h.NS).get(h.W + "w")) for tc in tr.findall("w:tc", h.NS)]
        assert got == grid


def test_table_cell_size_and_code_run(tmp_path):
    _, out = tbl_doc(tmp_path)
    [tbl] = h.tables(out)
    st = h.Styles(out)
    tc = tbl.findall("w:tr", h.NS)[2].findall("w:tc", h.NS)[1]
    p = tc.find("w:p", h.NS)
    plain = h.run_with(p, "A check")
    assert st.size(plain, p) == 19 and int(st.ppr(p, "spacing", "after")) == 20
    code = h.run_with(p, "code")
    assert st.font(code, p) == "Consolas" and st.size(code, p) == 17


def test_squeezed_table_warns_and_still_sums(tmp_path):
    head = "| " + " | ".join(f"Supercalifragilistic{i}" for i in range(8)) + " |\n"
    body = "# T\n\n" + head + "|" + "---|" * 8 + "\n| " + " | ".join("x" for _ in range(8)) + " |\n"
    res, out = tbl_doc(tmp_path, body)
    assert len(res["warnings"]) == 1
    assert re.match(r"line \d+: table columns squeezed below their longest word", res["warnings"][0])
    assert abs(sum(widths(h.tables(out)[0])) - 9648) <= 8


# ------------------------------------------------------------------------------------ excerpts, A2
def excerpt_report(folder, sub="excerpts"):
    h.write(folder / sub / "sched_code.txt", "def plan():\n    return rules\n\n\n")
    h.write(folder / sub / "tamper.txt", "bundle[0].priority = 999\nassert not verify(bundle)\n")
    return h.report(folder, "# Listings\n\nThe compiler writes the grading rules.\n\n"
                            "{{excerpt:sched_code|Listing 1. The compiler writes the hashed input.}}\n\n"
                            "The tamper test flips 1 field.\n\n"
                            "  {{excerpt:tamper|Listing 2. The tamper test.}}  \n\nEnd.\n")


def test_excerpt_paragraph_format_and_caption(tmp_path):
    res = h.build(excerpt_report(tmp_path), tmp_path / "out.docx")
    out = res["out"]
    ps = h.paras(out)
    i = [t for _, t, _ in ps].index("def plan():\n    return rules")
    style, _, p = ps[i]
    assert style == "Code" and ps[i + 1][:2] == ("Caption", "Listing 1. The compiler writes the hashed input.")
    st = h.Styles(out)
    assert all(st.size(r, p) == 17 for _, r in h.runs(p))
    assert int(st.ppr(p, "ind", "left") or st.ppr(p, "ind", "start")) == 288
    assert st.ppr(p, "keepNext", None) is not None
    assert res["excerpts"] == 2


def test_a2_excerpts_are_the_only_inserts(tmp_path):
    src = excerpt_report(tmp_path)
    out = h.build(src, tmp_path / "out.docx")["out"]
    changes = h.diff(str(src), out)
    assert changes and all(c["op"] == "insert" for c in changes)
    assert [x for c in changes for x in c["new"]] == [
        "def plan():\n    return rules", "Listing 1. The compiler writes the hashed input.",
        "bundle[0].priority = 999\nassert not verify(bundle)", "Listing 2. The tamper test."]


def test_excerpt_default_build_excerpts_folder(tmp_path):
    src = excerpt_report(tmp_path, sub="build/excerpts")
    assert h.build(src, tmp_path / "out.docx")["excerpts"] == 2


def test_excerpt_missing_file_and_missing_dir(tmp_path):
    src = h.report(tmp_path, "# T\n\n{{excerpt:nowhere|Listing 1. X.}}\n")
    assert "excerpts" in h.build_error(src, tmp_path / "o.docx")
    (tmp_path / "excerpts").mkdir()
    assert "line 3: " in h.build_error(src, tmp_path / "o.docx")


# ------------------------------------------------------------------------------------ A4, styles §18.1.2
def test_a4_text_backend_shows_style_ids(tmp_path):
    out = h.build(h.rich(tmp_path), tmp_path / "out.docx")["out"]
    res = h.call("render_office", src=out, out_dir=str(tmp_path / "render"), backend="text")
    text = (tmp_path / "render" / "paragraphs.txt").read_text(encoding="utf-8")
    assert res["backend"] == "text"
    for sid in ("Heading1", "Heading2", "Heading3", "ListBullet", "ListBullet2", "ListNumber", "Quote",
                "Caption", "Code", "Figure", "Normal"):
        assert f"[{sid}]" in text, sid
    assert "[Normal] Muk Chunpongtong · September 2026" in text
    assert "[ListNumber] 1.  Pinning a version on every capsule id" in text


@pytest.mark.parametrize("sid, size, before, after", [
    ("Heading1", 44, 0, 120), ("Heading2", 32, 320, 120), ("Heading3", 26, 240, 80)])
def test_heading_styles(tmp_path, sid, size, before, after):
    out = h.build(h.rich(tmp_path), tmp_path / "out.docx")["out"]
    st = h.Styles(out)
    assert st.size(None, None, style=sid) == size and st.on(None, None, "b", style=sid)
    assert st.font(None, None, style=sid) == "Calibri"
    assert int(st.ppr(None, "spacing", "before", style=sid) or 0) == before
    assert int(st.ppr(None, "spacing", "after", style=sid)) == after
    assert st.ppr(None, "keepNext", None, style=sid) is not None


def test_page_margins_and_footer(tmp_path):
    out = h.build(h.rich(tmp_path), tmp_path / "out.docx")["out"]
    sects = list(h.body(out).iter(h.W + "sectPr"))
    assert len(sects) == 1
    sz, mar = sects[0].find("w:pgSz", h.NS), sects[0].find("w:pgMar", h.NS)
    assert (sz.get(h.W + "w"), sz.get(h.W + "h")) == ("12240", "15840")
    assert sz.get(h.W + "orient") in (None, "portrait")
    assert [mar.get(h.W + k) for k in ("top", "bottom", "left", "right")] == ["1152", "1152", "1296", "1296"]
    foot = h.part(out, "word/footer1.xml").decode("utf-8")
    assert re.search(r'w:fldCharType="begin"', foot) and re.search(r'w:fldCharType="end"', foot)
    assert re.search(r"<w:instrText[^>]*> PAGE </w:instrText>", foot)
    fp = h.xml(out, "word/footer1.xml").find("w:p", h.NS)
    st = h.Styles(out)
    assert st.ppr(fp, "jc") == "center"
    field_runs = list(fp.iter(h.W + "r"))
    assert field_runs and all(st.size(r, fp) == 19 for r in field_runs)
    assert all((st.rpr(r, fp, "color") or "").upper() == "595959" for r in field_runs)


# ------------------------------------------------------------------------------------ core, package, author
def test_core_properties_package_and_app(tmp_path, monkeypatch):
    monkeypatch.setenv("TUNDLEKIT_NOW", "2026-09-16T10:00:07")
    out = h.build(h.rich(tmp_path), tmp_path / "out.docx", author="Muk Chunpongtong")["out"]
    c = h.core(out)
    assert c == {"title": "AI4Research: Workflow and Platform", "creator": "Muk Chunpongtong",
                 "last": "Muk Chunpongtong", "created": "2026-09-16T10:00:07Z", "modified": "2026-09-16T10:00:07Z"}
    assert set(h.PARTS) <= set(h.names(out))
    assert "tundlekit" in h.part(out, "docProps/app.xml").decode("utf-8")


def test_author_env_then_git_then_empty(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    for k, v in {"HOME": home, "USERPROFILE": home, "GIT_CONFIG_GLOBAL": home / "none",
                 "GIT_CONFIG_NOSYSTEM": "1", "GIT_CEILING_DIRECTORIES": tmp_path}.items():
        monkeypatch.setenv(k, str(v))
    monkeypatch.setenv("TUNDLEKIT_AUTHOR", "Env Name")
    plain = h.report(tmp_path / "plain", "# T\n\nText.\n")
    assert h.build(plain, tmp_path / "a.docx")["author"] == "Env Name"
    monkeypatch.delenv("TUNDLEKIT_AUTHOR")
    assert h.build(plain, tmp_path / "b.docx")["author"] == ""
    assert h.core(tmp_path / "b.docx")["creator"] == ""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Repo Person"], check=True)
    src = h.report(repo / "notes", "# T\n\nText.\n")
    res = h.build(src, tmp_path / "c.docx")
    assert res["author"] == "Repo Person" and h.core(res["out"])["last"] == "Repo Person"
    assert os.path.isfile(res["out"])
