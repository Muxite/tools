"""§0.4 CLI conventions."""
import json
import subprocess
import sys

import pytest

from helpers_core import (REPO_ROOT, gitenv, make_tundle, reg, run_cli, run_cli_json,  # noqa: F401
                          subprocess_env, write)


@pytest.fixture
def pair(tmp_path, gitenv):  # noqa: F811
    mine = make_tundle(tmp_path / "mine", version="2026.09.16.2", commit=False)
    other = tmp_path / "other"
    write(other, "VERSION", "2026.09.15.4\n")
    return mine, other


def test_version_flag(capsys):
    """§0.4 `tundlekit --version` prints `tundlekit <version>` and returns 0."""
    import tundlekit
    rc, out, _ = run_cli(capsys, ["--version"])
    assert rc == 0
    assert out.strip() == f"tundlekit {tundlekit.__version__}"


def test_main_returns_int_not_exit(capsys, pair):
    """§0.4 main(argv) -> int and never calls sys.exit itself (for a successful command)."""
    from tundlekit import cli
    mine, other = pair
    rc = cli.main(["bundle", "compare", str(other), "--root", str(mine), "--json"])
    assert rc == 0


def test_json_output_is_only_json_with_indent_2(capsys, pair):
    """§0.4 --json prints the result as JSON (indent=2, ensure_ascii=False) and nothing else."""
    mine, other = pair
    rc, out, _ = run_cli(capsys, ["bundle", "compare", str(other), "--root", str(mine), "--json"])
    assert rc == 0
    data = json.loads(out)
    assert out.strip() == json.dumps(data, indent=2, ensure_ascii=False)
    assert data["result"] == "this_newer"


def test_json_output_not_ascii_escaped(capsys, tmp_path, gitenv):  # noqa: F811
    """§0.4 ensure_ascii=False: non-ASCII text is printed as-is."""
    mine = make_tundle(tmp_path / "mine", version="2026.09.16.2", commit=False)
    other = tmp_path / "другой-副本"
    write(other, "VERSION", "2026.09.16.2\n")
    rc, out, _ = run_cli(capsys, ["bundle", "compare", str(other), "--root", str(mine), "--json"])
    assert rc == 0
    assert "другой-副本" in out
    assert "\\u" not in out


def test_toolerror_exit_1_and_stderr(capsys, pair, tmp_path):
    """§0.4 on ToolError: `tundlekit: <message>` on stderr, return 1."""
    mine, _ = pair
    rc, out, err = run_cli(capsys, ["bundle", "compare", str(tmp_path / "nowhere"), "--root", str(mine)])
    assert rc == 1
    assert "tundlekit: " in err
    assert "no VERSION" in err


def test_toolerror_json_error_object(capsys, pair, tmp_path):
    """§0.4 with --json a ToolError also prints {"error": "<message>"} to stdout."""
    mine, _ = pair
    rc, out, err = run_cli(capsys, ["bundle", "compare", str(tmp_path / "nowhere"), "--root", str(mine), "--json"])
    assert rc == 1
    data = json.loads(out)
    assert list(data) == ["error"]
    assert "no VERSION" in data["error"]
    assert f"tundlekit: {data['error']}" in err


def test_unknown_group_is_usage_error(capsys):
    """§0.4 exit 2 on usage error (argparse)."""
    rc, _, _ = run_cli(capsys, ["no-such-group", "x"])
    assert rc == 2


def test_unknown_bundle_command_is_usage_error(capsys):
    """§0.4 exit 2 on usage error."""
    rc, _, _ = run_cli(capsys, ["bundle", "frobnicate"])
    assert rc == 2


def test_tools_json_lists_every_tool(capsys):
    """§0.4 `tundlekit tools --json` prints {"tools": [Tool.listing()...]} for every registered tool."""
    rc, data, _ = run_cli_json(capsys, ["tools"])
    assert rc == 0
    assert list(data) == ["tools"]
    registered = reg().load_all()
    by_name = {t["name"]: t for t in data["tools"]}
    assert set(by_name) == set(registered)
    for name, t in registered.items():
        assert by_name[name] == json.loads(json.dumps(t.listing()))


def test_call_runs_tool_with_args(capsys, pair):
    """§0.4 `tundlekit call <tool> --args JSON` prints the result as JSON."""
    mine, other = pair
    args = json.dumps({"other": str(other), "root": str(mine)})
    rc, out, _ = run_cli(capsys, ["call", "bundle_compare", "--args", args])
    assert rc == 0
    data = json.loads(out)
    assert data == {"mine": "2026.09.16.2", "theirs": "2026.09.15.4", "other": str(other),
                    "result": "this_newer"}


def test_call_unknown_tool_exit_2(capsys):
    """§0.4 unknown tool name: exit 2 and a stderr message containing the name."""
    rc, _, err = run_cli(capsys, ["call", "no_such_tool_xyz"])
    assert rc == 2
    assert "no_such_tool_xyz" in err


def test_call_invalid_args_exit_1(capsys, pair):
    """§0.4 invalid arguments: exit 1, {"error": ...} on stdout, message naming the property."""
    mine, _ = pair
    rc, out, _ = run_cli(capsys, ["call", "bundle_compare", "--args", json.dumps({"root": str(mine)})])
    assert rc == 1
    data = json.loads(out)
    assert "other" in data["error"]


def test_python_dash_m_tundlekit_version():
    """§0.1 `python -m tundlekit` == `tundlekit`."""
    import tundlekit
    p = subprocess.run([sys.executable, "-m", "tundlekit", "--version"], capture_output=True,
                       env=subprocess_env(), cwd=str(REPO_ROOT), timeout=120)
    assert p.returncode == 0
    assert p.stdout.decode("utf-8").strip() == f"tundlekit {tundlekit.__version__}"


def test_subprocess_stdout_is_utf8(tmp_path, gitenv):  # noqa: F811
    """§0.4 stdout is written as UTF-8 even on Windows consoles (no PYTHONIOENCODING)."""
    mine = make_tundle(tmp_path / "mine", version="2026.09.16.2", commit=False)
    other = tmp_path / "副本"
    write(other, "VERSION", "2026.09.16.2\n")
    p = subprocess.run([sys.executable, "-m", "tundlekit", "bundle", "compare", str(other),
                        "--root", str(mine), "--json"], capture_output=True, env=subprocess_env(),
                       cwd=str(REPO_ROOT), timeout=120)
    assert p.returncode == 0, p.stderr
    data = json.loads(p.stdout.decode("utf-8"))
    assert data["other"] == str(other)


def test_call_args_file(capsys, tmp_path, gitenv):  # noqa: F811
    """§0.4 `tundlekit call <tool> --args-file PATH`."""
    mine = make_tundle(tmp_path / "m", version="2026.09.16.9", commit=False)
    other = tmp_path / "o"
    write(other, "VERSION", "2026.09.16.10\n")
    af = tmp_path / "args.json"
    af.write_text(json.dumps({"root": str(mine), "other": str(other)}), encoding="utf-8")
    rc, out, _ = run_cli(capsys, ["call", "bundle_compare", "--args-file", af])
    assert rc == 0
    assert json.loads(out)["result"] == "other_newer"


def test_tools_text_lists_names(capsys):
    """§0.4 `tundlekit tools` (no --json) lists every registered tool."""
    rc, out, _ = run_cli(capsys, ["tools"])
    assert rc == 0
    for name in reg().load_all():
        assert name in out
