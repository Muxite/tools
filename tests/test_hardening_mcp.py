"""MANIFEST §13.3 (with §0.5): the MCP server survives bad input, visible cases.

Lines are sent as raw bytes. The JSON text `"\\ud800"` is a valid JSON escape for a lone surrogate.
"""
from __future__ import annotations

import json
import subprocess

from helpers_core import mcp_argv, subprocess_env


def _run(lines, cwd, timeout=120):
    data = b"".join(line + b"\n" for line in lines)
    p = subprocess.Popen(mcp_argv(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         cwd=str(cwd), env=subprocess_env())
    try:
        out, _ = p.communicate(input=data, timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        p.communicate()
        raise AssertionError("MCP server did not exit after stdin closed")
    responses = [json.loads(line) for line in out.decode("utf-8", errors="surrogatepass").split("\n")
                 if line.strip()]
    return p.returncode, responses, out


PING_AFTER = b'{"jsonrpc":"2.0","id":"after","method":"ping"}'


def _answered_after(responses):
    return [r for r in responses if r.get("id") == "after"] == [{"jsonrpc": "2.0", "id": "after", "result": {}}]


def test_lone_surrogate_id_in_ping(tmp_path):
    """§13.3: a lone-surrogate id is answered (escaped, ensure_ascii) and the server keeps going."""
    rc, responses, raw = _run([b'{"jsonrpc":"2.0","id":"\\ud800","method":"ping"}', PING_AFTER], tmp_path)
    assert rc == 0
    assert len(responses) == 2
    assert responses[0]["id"] == "\ud800"
    assert responses[0].get("result") == {}
    assert _answered_after(responses)
    raw.decode("ascii")  # §13.3: responses are serialised with ensure_ascii=True


def test_deep_nesting_is_a_parse_error(tmp_path):
    """§13.3: '[' * 100000 (RecursionError while parsing) gives -32700 with id null; the server continues."""
    rc, responses, _ = _run([b"[" * 100000, PING_AFTER], tmp_path)
    assert rc == 0
    assert len(responses) == 2
    assert responses[0]["id"] is None
    assert responses[0]["error"]["code"] == -32700
    assert _answered_after(responses)


def test_deep_object_nesting_and_surrogate_notification(tmp_path):
    """§13.3: deep object nesting is -32700; a notification with a surrogate gets no response; exit 0 at EOF."""
    deep = b'{"a":' * 60000 + b"1" + b"}" * 60000
    note = b'{"jsonrpc":"2.0","method":"notifications/\\udc00"}'
    rc, responses, _ = _run([deep, note, PING_AFTER], tmp_path)
    assert rc == 0
    assert len(responses) == 2
    assert responses[0]["error"]["code"] == -32700 and responses[0]["id"] is None
    assert _answered_after(responses)
