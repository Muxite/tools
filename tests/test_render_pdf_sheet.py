"""MANIFEST §8.1 render_pdf, §8.2 render_contact_sheet, §8.4 render_backends."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_misc as h  # noqa: E402


@pytest.fixture
def need_pdf():
    pytest.importorskip("pymupdf")


@pytest.fixture
def need_pil():
    pytest.importorskip("PIL")


# ------------------------------------------------------------------------------------------ registration

@pytest.mark.parametrize("name", ["render_pdf", "render_contact_sheet", "render_office", "render_backends"])
def test_render_tools_registered(name):
    """§8: the render tools are registered under their manifest names."""
    assert name in h.registry().TOOLS


@pytest.mark.parametrize("command", ["pdf", "sheet", "office", "backends"])
def test_render_cli_commands_exist(command):
    """§8: `tundlekit render pdf|sheet|office|backends`."""
    assert h.cli_command_exists("render", command)


# ------------------------------------------------------------------------------------------ §8.1 render_pdf

def test_render_pdf_all_pages(tmp_path, capsys, need_pdf):
    """§8.1: page-001.png ... (3 digits), result pages + files, out_dir created."""
    pdf = h.make_pdf(tmp_path / "doc.pdf", ["one", "two", "three"])
    out = tmp_path / "nested" / "out"
    code, data, _, _ = h.run_cli(["render", "pdf", pdf, "-o", out, "--json"], capsys)
    assert code == 0
    assert data["pages"] == 3
    names = [Path(f).name for f in data["files"]]
    assert names == ["page-001.png", "page-002.png", "page-003.png"]
    for f in data["files"]:
        p = Path(f)
        assert p.parent.resolve() == out.resolve()
        assert p.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_render_pdf_first_last_inclusive(tmp_path, capsys, need_pdf):
    """§8.1: first/last are 1-based and inclusive; files are numbered by page number."""
    pdf = h.make_pdf(tmp_path / "doc.pdf", ["a", "b", "c", "d"])
    out = tmp_path / "out"
    code, data, _, _ = h.run_cli(["render", "pdf", pdf, "-o", out, "--first", "2", "--last", "3", "--json"], capsys)
    assert code == 0
    assert data["pages"] == 4
    assert [Path(f).name for f in data["files"]] == ["page-002.png", "page-003.png"]
    assert sorted(p.name for p in out.glob("page-*.png")) == ["page-002.png", "page-003.png"]


def test_render_pdf_dpi_scales_output(tmp_path, capsys, need_pdf, need_pil):
    """§8.1: --dpi controls the raster size (a 200 pt page at 72 dpi is ~200 px wide, at 144 dpi ~400 px)."""
    pdf = h.make_pdf(tmp_path / "doc.pdf", ["x"], width=200, height=100)
    code, d72, _, _ = h.run_cli(["render", "pdf", pdf, "-o", tmp_path / "a", "--dpi", "72", "--json"], capsys)
    assert code == 0
    code, d144, _, _ = h.run_cli(["render", "pdf", pdf, "-o", tmp_path / "b", "--dpi", "144", "--json"], capsys)
    assert code == 0
    w72, _ = h.png_size(d72["files"][0])
    w144, _ = h.png_size(d144["files"][0])
    assert abs(w72 - 200) <= 2
    assert abs(w144 - 400) <= 3


def test_render_pdf_missing_file(tmp_path, capsys, need_pdf):
    """§8.1: a missing file gives ToolError (§0.4: exit 1, stderr `tundlekit: ...`, {"error"} with --json)."""
    code, data, _, err = h.run_cli(["render", "pdf", tmp_path / "nope.pdf", "-o", tmp_path / "o", "--json"], capsys)
    assert code == 1
    assert "error" in data
    assert err.startswith("tundlekit: ")


def test_render_pdf_non_pdf(tmp_path, capsys, need_pdf):
    """§8.1: a non-PDF file gives ToolError."""
    bad = tmp_path / "notes.txt"
    bad.write_text("hello, not a pdf\n", encoding="utf-8")
    code, data, _, _ = h.run_cli(["render", "pdf", bad, "-o", tmp_path / "o", "--json"], capsys)
    assert code == 1
    assert "error" in data


# ------------------------------------------------------------------------------------------ §8.2 contact sheets

def test_contact_sheet_paging_and_width(tmp_path, capsys, need_pil):
    """§8.2: cols x rows per sheet, contact-01.png..., width = cols*(thumb_width+14)+14."""
    imgs = [h.make_png(tmp_path / f"slide-{i:02d}.png", 300, 200) for i in range(1, 6)]
    out = tmp_path / "sheets"
    code, data, _, _ = h.run_cli(
        ["render", "sheet", *imgs, "-o", out, "--cols", "2", "--rows", "1", "--thumb-width", "100", "--json"], capsys)
    assert code == 0
    assert [Path(s).name for s in data["sheets"]] == ["contact-01.png", "contact-02.png", "contact-03.png"]
    for s in data["sheets"]:
        assert Path(s).is_file()
        assert h.png_size(s)[0] == 2 * (100 + 14) + 14


def test_contact_sheet_defaults_4x3_480(tmp_path, capsys, need_pil):
    """§8.2: defaults cols 4, rows 3, thumb width 480: 12 images make 1 sheet 1990 px wide."""
    imgs = [h.make_png(tmp_path / "in" / f"page-{i:03d}.png", 64, 48) for i in range(12)]
    code, data, _, _ = h.run_cli(["render", "sheet", *imgs, "-o", tmp_path / "out", "--json"], capsys)
    assert code == 0
    assert len(data["sheets"]) == 1
    assert h.png_size(data["sheets"][0])[0] == 4 * (480 + 14) + 14


def test_contact_sheet_keeps_aspect_ratio(tmp_path, capsys, need_pil):
    """§8.2: a thumbnail keeps its aspect ratio, so a 100x400 image at thumb width 100 needs >= 400 px of height."""
    img = h.make_png(tmp_path / "tall.png", 100, 400)
    code, data, _, _ = h.run_cli(
        ["render", "sheet", img, "-o", tmp_path / "out", "--cols", "1", "--rows", "1", "--thumb-width", "100",
         "--json"], capsys)
    assert code == 0
    w, hgt = h.png_size(data["sheets"][0])
    assert w == 1 * (100 + 14) + 14
    assert hgt >= 400


def test_contact_sheet_no_images_is_tool_error(tmp_path, need_pil):
    """§8.2: no images gives ToolError."""
    reg = h.registry()
    schema = reg.TOOLS["render_contact_sheet"].input_schema
    props = schema.get("properties", {})
    arrays = [k for k, v in props.items() if v.get("type") == "array"]
    assert len(arrays) == 1, "expected exactly 1 array property (the image list)"
    args = {arrays[0]: []}
    for req in schema.get("required", []):
        if req not in args:
            args[req] = str(tmp_path / "out")
    with pytest.raises(h.tool_error()):
        reg.call("render_contact_sheet", args)


# ------------------------------------------------------------------------------------------ §8.4 backends

def test_render_backends_shape(capsys):
    """§8.4: keys and value types."""
    code, data, _, _ = h.run_cli(["render", "backends", "--json"], capsys)
    assert code == 0
    for key in ("powerpoint", "pymupdf", "pillow", "pptx"):
        assert isinstance(data[key], bool), key
    for key in ("libreoffice", "svg_to_png"):
        assert data[key] is None or isinstance(data[key], str), key
    if sys.platform != "win32":
        assert data["powerpoint"] is False


def test_render_backends_reports_installed_packages():
    """§8.4: pymupdf / pillow / pptx reflect what is importable."""
    import importlib.util

    data = h.call_tool("render_backends")
    assert data["pymupdf"] == (importlib.util.find_spec("pymupdf") is not None
                               or importlib.util.find_spec("fitz") is not None)
    assert data["pillow"] == (importlib.util.find_spec("PIL") is not None)
    assert data["pptx"] == (importlib.util.find_spec("pptx") is not None)


def test_render_backends_libreoffice_from_env(tmp_path, monkeypatch):
    """§8.3/§8.4: TUNDLEKIT_SOFFICE names the LibreOffice executable, and backends reports its path."""
    exe = tmp_path / ("soffice.exe" if sys.platform == "win32" else "soffice")
    exe.write_bytes(b"")
    exe.chmod(0o755)
    monkeypatch.setenv("TUNDLEKIT_SOFFICE", str(exe))
    data = h.call_tool("render_backends")
    assert data["libreoffice"] is not None
    assert Path(data["libreoffice"]).resolve() == exe.resolve()


def test_render_backends_is_read_only():
    """§0.2: tools that only read carry readOnlyHint true."""
    assert h.registry().TOOLS["render_backends"].annotations.get("readOnlyHint") is True
