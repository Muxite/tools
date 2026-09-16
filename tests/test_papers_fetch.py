"""MANIFEST §9 / §9.1 papers_fetch, against a localhost stand-in for arXiv."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_misc as h  # noqa: E402


@pytest.fixture
def server(monkeypatch):
    pytest.importorskip("pymupdf")
    h.no_proxy(monkeypatch)
    monkeypatch.delenv("TUNDLEKIT_ARXIV_BASE", raising=False)
    with h.ArxivServer() as srv:
        yield srv


def fetch(capsys, ids, d, *extra):
    return h.run_cli(["papers", "fetch", *ids, "--dir", d, *extra, "--json"], capsys)


def by_id(data):
    return {r["id"]: r for r in data["results"]}


def test_papers_tools_registered():
    """§9: tool names."""
    tools = h.registry().TOOLS
    for name in ("papers_fetch", "papers_body", "papers_peek", "papers_list"):
        assert name in tools


@pytest.mark.parametrize("command", ["fetch", "body", "abs", "grep", "list"])
def test_papers_cli_commands_exist(command):
    """§9.1-§9.4: CLI commands."""
    assert h.cli_command_exists("papers", command)


def test_download_with_base_url(server, tmp_path, capsys):
    """§9.1: base_url + '/' + id; status downloaded; pdf and txt written; pages/chars describe the text."""
    server.routes["/pdf/2401.00001"] = (200, h.pdf_bytes(["alpha page", "beta page"]))
    code, data, _, _ = fetch(capsys, ["2401.00001"], tmp_path, "--base-url", server.url("/pdf"), "--delay", "0")
    assert code == 0
    assert data["ok"] is True
    r = by_id(data)["2401.00001"]
    assert r["status"] == "downloaded"
    assert r["error"] is None
    assert Path(r["pdf"]).resolve() == (tmp_path / "2401.00001.pdf").resolve()
    assert Path(r["txt"]).resolve() == (tmp_path / "2401.00001.txt").resolve()
    assert (tmp_path / "2401.00001.pdf").read_bytes().startswith(b"%PDF-")
    assert r["pages"] == 2
    assert isinstance(r["chars"], int) and r["chars"] > 0
    assert server.paths() == ["/pdf/2401.00001"]


def test_text_file_uses_page_markers(server, tmp_path, capsys):
    """§9: fetch writes '\\n\\n===== page N =====\\n' + page text for each page."""
    server.routes["/pdf/2401.00002"] = (200, h.pdf_bytes(["alpha page", "beta page"]))
    code, _, _, _ = fetch(capsys, ["2401.00002"], tmp_path, "--base-url", server.url(), "--delay", "0")
    assert code == 0
    text = (tmp_path / "2401.00002.txt").read_text(encoding="utf-8")
    assert text.startswith("\n\n===== page 1 =====\n")
    assert "\n\n===== page 2 =====\n" in text
    first, second = text.split("===== page 2 =====")
    assert "alpha page" in first and "beta page" in second


def test_base_url_from_environment(server, tmp_path, capsys, monkeypatch):
    """§9.1: TUNDLEKIT_ARXIV_BASE is used when no argument is given (trailing slash handled)."""
    server.routes["/mirror/2401.00003"] = (200, h.pdf_bytes(["x"]))
    monkeypatch.setenv("TUNDLEKIT_ARXIV_BASE", server.url("/mirror/"))
    code, data, _, _ = fetch(capsys, ["2401.00003"], tmp_path, "--delay", "0")
    assert code == 0
    assert by_id(data)["2401.00003"]["status"] == "downloaded"
    assert server.paths() == ["/mirror/2401.00003"]


def test_user_agent_contains_tundlekit(server, tmp_path, capsys):
    """§9.1: the request sends a User-Agent containing 'tundlekit'."""
    server.routes["/pdf/2401.00004"] = (200, h.pdf_bytes(["x"]))
    fetch(capsys, ["2401.00004"], tmp_path, "--base-url", server.url(), "--delay", "0")
    headers = {k.lower(): v for k, v in server.requests[0]["headers"].items()}
    assert "tundlekit" in headers["user-agent"]


def test_present_pdf_not_downloaded(server, tmp_path, capsys):
    """§9.1: a PDF already present is not downloaded again (status present)."""
    h.make_pdf(tmp_path / "2401.00005.pdf", ["local copy"])
    code, data, _, _ = fetch(capsys, ["2401.00005"], tmp_path, "--base-url", server.url(), "--delay", "0")
    assert code == 0
    r = by_id(data)["2401.00005"]
    assert r["status"] == "present"
    assert r["error"] is None
    assert server.requests == []
    assert data["ok"] is True


def test_present_pdf_gets_missing_text(server, tmp_path, capsys):
    """§9.1: text is extracted when {id}.txt is missing, even for a present PDF."""
    h.make_pdf(tmp_path / "2401.00006.pdf", ["local one", "local two", "local three"])
    code, data, _, _ = fetch(capsys, ["2401.00006"], tmp_path, "--base-url", server.url(), "--delay", "0")
    assert code == 0
    r = by_id(data)["2401.00006"]
    assert (tmp_path / "2401.00006.txt").is_file()
    assert r["pages"] == 3


def test_not_a_pdf_is_failure_and_cleaned(server, tmp_path, capsys):
    """§9.1: a body not starting with %PDF- fails with 'not a PDF'; nothing is left on disk; CLI exits 1."""
    server.routes["/pdf/2401.00007"] = (200, b"<html>captcha</html>")
    code, data, _, _ = fetch(capsys, ["2401.00007"], tmp_path, "--base-url", server.url(), "--delay", "0")
    assert code == 1
    assert data["ok"] is False
    r = by_id(data)["2401.00007"]
    assert r["status"] == "failed"
    assert "not a PDF" in r["error"]
    assert list(tmp_path.glob("2401.00007*")) == []


def test_invalid_id_is_per_id_failure(server, tmp_path, capsys):
    """§9: an id not matching the format fails with 'invalid arXiv id'; others still run."""
    server.routes["/pdf/2401.00008"] = (200, h.pdf_bytes(["x"]))
    code, data, _, _ = fetch(capsys, ["../etc/passwd", "2401.00008"], tmp_path,
                             "--base-url", server.url(), "--delay", "0")
    assert code == 1
    assert data["ok"] is False
    results = data["results"]
    assert [r["id"] for r in results] == ["../etc/passwd", "2401.00008"]
    assert results[0]["status"] == "failed"
    assert "invalid arXiv id" in results[0]["error"]
    assert results[1]["status"] == "downloaded"
    assert server.paths() == ["/pdf/2401.00008"]


def test_http_error_does_not_stop_others(server, tmp_path, capsys):
    """§9.1: errors for 1 id never stop the others."""
    server.routes["/pdf/2401.00010"] = (200, h.pdf_bytes(["x"]))
    code, data, _, _ = fetch(capsys, ["2401.00009", "2401.00010"], tmp_path,
                             "--base-url", server.url(), "--delay", "0")
    assert code == 1
    r = by_id(data)
    assert r["2401.00009"]["status"] == "failed"
    assert r["2401.00009"]["error"]
    assert r["2401.00009"]["pages"] is None and r["2401.00009"]["chars"] is None
    assert r["2401.00010"]["status"] == "downloaded"
    assert not (tmp_path / "2401.00009.pdf").exists()


def test_old_style_id_stored_with_underscore(server, tmp_path, capsys):
    """§9: old-style ids (cs/0112017) are requested as-is and stored with '/' replaced by '_'."""
    server.routes["/pdf/cs/0112017"] = (200, h.pdf_bytes(["old"]))
    code, data, _, _ = fetch(capsys, ["cs/0112017"], tmp_path, "--base-url", server.url(), "--delay", "0")
    assert code == 0
    assert server.paths() == ["/pdf/cs/0112017"]
    assert (tmp_path / "cs_0112017.pdf").is_file()
    assert (tmp_path / "cs_0112017.txt").is_file()
    assert by_id(data)["cs/0112017"]["status"] == "downloaded"


def test_delay_between_downloads_only(server, tmp_path, capsys):
    """§9.1: delay is slept between actual downloads only, never before the first or after the last."""
    for i in (11, 12):
        server.routes[f"/pdf/2401.000{i}"] = (200, h.pdf_bytes(["x"]))
    start = time.monotonic()
    code, _, _, _ = fetch(capsys, ["2401.00011", "2401.00012"], tmp_path, "--base-url", server.url(),
                          "--delay", "2")
    end = time.monotonic()
    assert code == 0
    t1, t2 = (r["time"] for r in server.requests)
    assert t2 - t1 >= 1.9
    assert t1 - start < 1.5
    assert end - t2 < 1.5
