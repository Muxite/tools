"""§0.5 MCP server over stdio (newline-delimited JSON-RPC 2.0)."""
import json

import pytest

from helpers_core import (McpProcess, gitenv, make_tundle, mcp_run, note, reg, req,  # noqa: F401
                          write)

SUPPORTED = ["2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"]


@pytest.fixture
def tundle(tmp_path, gitenv):  # noqa: F811
    root = make_tundle(tmp_path / "t", version="2026.09.16.3")
    other = tmp_path / "o"
    write(other, "VERSION", "2026.09.17.1\n")
    return root, other


def _init(id_=1, version="2025-06-18"):
    return req(id_, "initialize", {"protocolVersion": version, "capabilities": {},
                                   "clientInfo": {"name": "pytest", "version": "0"}})


def test_initialize_result(tmp_path):
    """§0.5 initialize result: protocolVersion, capabilities, serverInfo, instructions."""
    import tundlekit
    rc, resp, _, _ = mcp_run([_init(1, "2025-06-18")], cwd=tmp_path)
    assert rc == 0
    assert len(resp) == 1
    r = resp[0]
    assert r["jsonrpc"] == "2.0" and r["id"] == 1
    res = r["result"]
    assert res["protocolVersion"] == "2025-06-18"
    assert res["capabilities"]["tools"] == {"listChanged": False}
    assert res["serverInfo"] == {"name": "tundlekit", "version": tundlekit.__version__}
    assert isinstance(res["instructions"], str) and res["instructions"].strip()


@pytest.mark.parametrize("version", ["2025-11-25", "2024-11-05"])
def test_initialize_echoes_supported_version(tmp_path, version):
    """§0.5 a supported requested version is echoed."""
    _, resp, _, _ = mcp_run([_init(1, version)], cwd=tmp_path)
    assert resp[0]["result"]["protocolVersion"] == version


def test_initialize_unsupported_version_gets_latest(tmp_path):
    """§0.5 otherwise the server answers 2025-11-25."""
    _, resp, _, _ = mcp_run([_init(1, "2023-01-01")], cwd=tmp_path)
    assert resp[0]["result"]["protocolVersion"] == "2025-11-25"


def test_initialized_notification_has_no_response(tmp_path):
    """§0.5 notifications/initialized: no response."""
    rc, resp, _, _ = mcp_run([_init(1), note("notifications/initialized"), req(2, "ping")], cwd=tmp_path)
    assert rc == 0
    assert [r["id"] for r in resp] == [1, 2]


def test_ping(tmp_path):
    """§0.5 ping: result {}."""
    _, resp, _, _ = mcp_run([req(5, "ping")], cwd=tmp_path)
    assert resp == [{"jsonrpc": "2.0", "id": 5, "result": {}}]


def test_tools_list_all_in_registration_order(tmp_path):
    """§0.5 tools/list: every registered tool, registration order, no nextCursor."""
    _, resp, _, _ = mcp_run([_init(1), req(2, "tools/list")], cwd=tmp_path)
    res = resp[1]["result"]
    assert "nextCursor" not in res
    expected = [json.loads(json.dumps(t.listing())) for t in reg().load_all().values()]
    assert res["tools"] == expected


def test_tools_call_success(tmp_path, tundle):
    """§0.5 tools/call success: text is json.dumps(result), structuredContent is result, isError false."""
    root, other = tundle
    args = {"other": str(other), "root": str(root)}
    _, resp, _, _ = mcp_run([_init(1), req(2, "tools/call", {"name": "bundle_compare", "arguments": args})],
                            cwd=tmp_path)
    res = resp[1]["result"]
    assert res["isError"] is False
    assert len(res["content"]) == 1 and res["content"][0]["type"] == "text"
    expected = {"mine": "2026.09.16.3", "theirs": "2026.09.17.1", "other": str(other), "result": "other_newer"}
    assert res["structuredContent"] == expected
    assert json.loads(res["content"][0]["text"]) == expected


def test_tools_call_toolerror_is_iserror(tmp_path, tundle):
    """§0.5 ToolError -> result with isError true and the message as text."""
    root, _ = tundle
    args = {"other": str(tmp_path / "missing"), "root": str(root)}
    _, resp, _, _ = mcp_run([req(2, "tools/call", {"name": "bundle_compare", "arguments": args})], cwd=tmp_path)
    res = resp[0]["result"]
    assert res["isError"] is True
    assert res["content"][0]["type"] == "text"
    assert "no VERSION" in res["content"][0]["text"]
    assert "structuredContent" not in res


def test_tools_call_invalid_arguments_is_iserror(tmp_path):
    """§0.5 invalid arguments -> isError true, message names the property."""
    _, resp, _, _ = mcp_run([req(3, "tools/call", {"name": "bundle_compare", "arguments": {"bogus_prop": 1}})],
                            cwd=tmp_path)
    res = resp[0]["result"]
    assert res["isError"] is True
    assert "bogus_prop" in res["content"][0]["text"]


def test_tools_call_unknown_tool(tmp_path):
    """§0.5 unknown tool name -> JSON-RPC error -32602 with the name."""
    _, resp, _, _ = mcp_run([req(4, "tools/call", {"name": "nope_tool_zz", "arguments": {}})], cwd=tmp_path)
    assert resp[0]["id"] == 4
    assert resp[0]["error"]["code"] == -32602
    assert "nope_tool_zz" in resp[0]["error"]["message"]
    assert "result" not in resp[0]


def test_unknown_method(tmp_path):
    """§0.5 unknown method (request with an id) -> -32601."""
    _, resp, _, _ = mcp_run([req(9, "resources/frobnicate")], cwd=tmp_path)
    assert resp[0]["id"] == 9
    assert resp[0]["error"]["code"] == -32601


def test_parse_error(tmp_path):
    """§0.5 a line that is not valid JSON -> -32700 with id null."""
    _, resp, _, _ = mcp_run(["{not json", req(2, "ping")], cwd=tmp_path)
    assert resp[0]["error"]["code"] == -32700
    assert resp[0]["id"] is None
    assert resp[1]["result"] == {}


def test_array_is_invalid_request(tmp_path):
    """§0.5 valid JSON that is not a request object (an array) -> -32600, id null."""
    _, resp, _, _ = mcp_run(["[1, 2]"], cwd=tmp_path)
    assert resp[0]["error"]["code"] == -32600
    assert resp[0]["id"] is None


def test_object_without_method_keeps_id(tmp_path):
    """§0.5 an object with no method -> -32600, id taken from the object."""
    _, resp, _, _ = mcp_run([{"jsonrpc": "2.0", "id": 77}], cwd=tmp_path)
    assert resp[0]["error"]["code"] == -32600
    assert resp[0]["id"] == 77


def test_string_id_unchanged(tmp_path):
    """§0.5 responses carry the request id unchanged (string)."""
    _, resp, _, _ = mcp_run([req("abc-1", "ping")], cwd=tmp_path)
    assert resp[0]["id"] == "abc-1"
    assert resp[0]["jsonrpc"] == "2.0"


def test_blank_lines_ignored_and_exit_0(tmp_path):
    """§0.5 blank lines are ignored; the server exits 0 when stdin closes."""
    rc, resp, raw, _ = mcp_run(["", req(1, "ping"), "   ", ""], cwd=tmp_path)
    assert rc == 0
    assert resp == [{"jsonrpc": "2.0", "id": 1, "result": {}}]


def test_stdout_protocol_only(tmp_path, tundle):
    """§0.5 stdout carries protocol messages only, 1 per line."""
    root, other = tundle
    msgs = [_init(1), note("notifications/initialized"), req(2, "tools/list"),
            req(3, "tools/call", {"name": "bundle_status", "arguments": {"root": str(root)}})]
    rc, resp, raw, _ = mcp_run(msgs, cwd=tmp_path)
    assert rc == 0
    lines = [ln for ln in raw.split("\n") if ln != ""]
    assert len(lines) == 3
    for ln in lines:
        obj = json.loads(ln)
        assert obj["jsonrpc"] == "2.0"
    assert [r["id"] for r in resp] == [1, 2, 3]


def test_root_option_sets_default_root(tmp_path, tundle):
    """§0.5 `--root PATH` sets the default root; §0.5 absent arguments mean {}."""
    root, _ = tundle
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    _, resp, _, _ = mcp_run([req(1, "tools/call", {"name": "bundle_status"})], cwd=elsewhere,
                            extra_args=["--root", str(root)])
    res = resp[0]["result"]
    assert res["isError"] is False, res
    assert res["structuredContent"]["version"] == "2026.09.16.3"


def test_flushes_after_each_response(tmp_path):
    """§0.5 the server flushes after each response (a reply arrives while stdin stays open)."""
    srv = McpProcess(tmp_path)
    try:
        srv.send(req(1, "ping"))
        assert srv.recv(timeout=60) == {"jsonrpc": "2.0", "id": 1, "result": {}}
        srv.send(_init(2))
        assert srv.recv(timeout=60)["id"] == 2
    finally:
        rc = srv.close()
    assert rc == 0
