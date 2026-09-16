"""MANIFEST §13.5 and §13.1/§13.4 full-match rules (with §6, §8.1, §9.1, §10): visible cases."""
from __future__ import annotations

import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers_misc as h  # noqa: E402
from helpers_core import subprocess_env  # noqa: E402


def tiny_pdf() -> bytes:
    """A valid 1-page PDF written by hand (no optional packages needed)."""
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 100] >>"]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref)
    return bytes(out)


class Server:
    """Local server: `routes` maps a path to (body, declared Content-Length or None)."""

    def __init__(self):
        self.routes = {}
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802
                body, length = outer.routes.get(self.path, (b"missing", None))
                self.send_response(200 if self.path in outer.routes else 404)
                self.send_header("Content-Type", "application/pdf")
                self.send_header("Content-Length", str(length if length is not None else len(body)))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(body)
                self.wfile.flush()
                self.close_connection = True

            def log_message(self, *a):
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}/pdf"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


@pytest.fixture
def server(monkeypatch):
    h.no_proxy(monkeypatch)
    monkeypatch.delenv("TUNDLEKIT_ARXIV_BASE", raising=False)
    srv = Server()
    yield srv
    srv.close()


def test_truncated_download_fails_only_that_id(server, tmp_path):
    """§13.5: an IncompleteRead makes that id failed with no files left; the next id still downloads."""
    good = tiny_pdf()
    server.routes["/pdf/2401.00007"] = (good[:40], len(good))      # Content-Length larger than sent
    server.routes["/pdf/2401.00008"] = (good, None)
    res = h.call_tool("papers_fetch", {"ids": ["2401.00007", "2401.00008"], "dir": str(tmp_path),
                                       "base_url": server.url, "delay": 0})
    by = {r["id"]: r for r in res["results"]}
    assert by["2401.00007"]["status"] == "failed"
    assert by["2401.00007"]["pdf"] is None and by["2401.00007"]["error"]
    assert not any(p.name.startswith("2401.00007") for p in tmp_path.iterdir())
    assert by["2401.00008"]["status"] == "downloaded"
    assert (tmp_path / "2401.00008.pdf").read_bytes() == good
    assert res["ok"] is False


def test_arxiv_id_with_trailing_newline_is_invalid(tmp_path):
    """§13.1/§9: id patterns are full matches; `2401.00006\\n` is `invalid arXiv id`."""
    res = h.call_tool("papers_fetch", {"ids": ["2401.00006\n"], "dir": str(tmp_path),
                                       "base_url": "http://127.0.0.1:9/pdf", "delay": 0})
    (r,) = res["results"]
    assert r["status"] == "failed"
    assert "invalid arXiv id" in r["error"]
    assert list(tmp_path.iterdir()) == []


def test_render_pdf_truncated_json_stdout(tmp_path):
    """§13.5: whatever the outcome, `render pdf ... --json` stdout is only the JSON (no library noise)."""
    pdf = tmp_path / "broken.pdf"
    data = tiny_pdf()
    pdf.write_bytes(data[: len(data) // 2])
    p = subprocess.run([sys.executable, "-m", "tundlekit", "render", "pdf", str(pdf), "-o", str(tmp_path / "o"),
                        "--json"], capture_output=True, env=subprocess_env(), cwd=str(tmp_path), timeout=120)
    parsed = json.loads(p.stdout.decode("utf-8"))
    assert isinstance(parsed, dict)
    assert p.returncode in (0, 1)


def test_translate_source_named_like_an_option(tmp_path, monkeypatch):
    """§13.5: a file argument starting with `-` reaches tcheck as a file (exit 0 or 1, never usage error 2)."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "-x.md").write_text("plain English text\n", encoding="utf-8")
    res = h.call_tool("translate_check", {"mode": "encoding", "src": "-x.md"})
    assert res["exit_code"] in (0, 1), res
    assert res["exit_code"] == 0 or "-x.md" in res["output"] + res["errors"]


def test_tint_rejects_trailing_newline():
    """§6/§13: tint input must match fully; `#0072b2\\n` raises ValueError."""
    from tundlekit.palette import tint

    with pytest.raises(ValueError):
        tint("#0072b2\n")


def test_truncated_download_cli_exit_code(server, tmp_path, capsys):
    """§13.5/§9.1: via the CLI, a truncated download is a per-id failure: exit 1 and a results list."""
    good = tiny_pdf()
    server.routes["/pdf/2403.00009"] = (good[:30], len(good))
    code, data, _, _ = h.run_cli(["papers", "fetch", "2403.00009", "--dir", tmp_path, "--base-url", server.url,
                                  "--delay", "0", "--json"], capsys)
    assert code == 1
    assert data["results"][0]["status"] == "failed"
    assert list(tmp_path.iterdir()) == []
