"""§0.1/§0.2 tool conventions across every registered tool, and §12 pyproject.toml."""
import json
import re
import subprocess
import sys
import tomllib

import pytest

from helpers_core import BUNDLE_TOOLS, REPO_ROOT, reg, subprocess_env

ALL_TOOL_NAMES = BUNDLE_TOOLS + [
    "deck_build", "deck_lint", "deck_inspect",
    "diagram_render", "diagram_validate", "diagram_from_mermaid", "diagram_to_mermaid",
    "chart_bar", "palette_get", "text_lint", "text_fignums", "text_wordcount",
    "render_pdf", "render_contact_sheet", "render_office", "render_backends",
    "papers_fetch", "papers_body", "papers_peek", "papers_list",
    "translate_check", "translate_resources",
]


def test_every_manifest_tool_is_registered():
    """§0.1 every module in MODULES registers its tools; tool names from §2–§10."""
    tools = reg().load_all()
    missing = [n for n in ALL_TOOL_NAMES if n not in tools]
    assert missing == []


def test_every_schema_is_closed_object():
    """§0.2 every tool schema has type object and additionalProperties false."""
    for name, t in reg().load_all().items():
        assert t.input_schema.get("type") == "object", name
        assert t.input_schema.get("additionalProperties") is False, name


def test_every_description_nonempty_and_short():
    """§0.2 non-empty description of at most 1024 characters."""
    for name, t in reg().load_all().items():
        assert isinstance(t.description, str) and t.description.strip(), name
        assert len(t.description) <= 1024, name


def test_every_listing_is_json_serialisable():
    """§0.2/§0.5 listings go over the wire as JSON."""
    for t in reg().load_all().values():
        assert json.loads(json.dumps(t.listing())) == t.listing()


@pytest.mark.parametrize("name", ["bundle_status", "bundle_compare", "bundle_lint", "bundle_verify"])
def test_readonly_bundle_tools_annotated(name):
    """§0.2 tools that only read carry readOnlyHint: true."""
    assert reg().TOOLS[name].annotations.get("readOnlyHint") is True


def test_writing_bundle_tools_annotated():
    """§0.2 release/prune/init carry readOnlyHint false; prune also destructiveHint true."""
    tools = reg().TOOLS
    for name in ("bundle_release", "bundle_prune", "bundle_init"):
        assert tools[name].annotations.get("readOnlyHint") is False, name
    assert tools["bundle_prune"].annotations.get("destructiveHint") is True


def test_bundle_required_arguments():
    """§2.3 summary required; §2.4 other required."""
    tools = reg().TOOLS
    assert "summary" in tools["bundle_release"].input_schema.get("required", [])
    assert "other" in tools["bundle_compare"].input_schema.get("required", [])


def test_bundle_schema_properties():
    """§2.3–§2.7 argument names."""
    tools = reg().TOOLS
    props = lambda n: set(tools[n].input_schema.get("properties", {}))  # noqa: E731
    assert {"summary", "root"} <= props("bundle_release")
    assert {"other", "root"} <= props("bundle_compare")
    assert {"keep", "yes", "root"} <= props("bundle_prune")
    assert {"root"} <= props("bundle_init")
    assert {"root", "max_path", "large_mb"} <= props("bundle_lint")
    assert {"root"} <= props("bundle_status")
    assert {"root"} <= props("bundle_verify")


def test_import_does_not_pull_optional_packages():
    """§0.1 importing any tundlekit module must not import an optional package at module level."""
    code = (
        "import sys, importlib\n"
        "import tundlekit, tundlekit.registry, tundlekit.cli, tundlekit.mcp_server\n"
        "from tundlekit import MODULES\n"
        "for m in MODULES: importlib.import_module('tundlekit.' + m)\n"
        "bad = [m for m in ('pptx', 'PIL', 'fitz', 'pymupdf') if m in sys.modules]\n"
        "print(','.join(bad))\n"
    )
    p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=subprocess_env(),
                       cwd=str(REPO_ROOT), timeout=120)
    assert p.returncode == 0, p.stderr
    assert p.stdout.strip() == ""


# ---------------------------------------------------------------- §12 pyproject.toml

def _pyproject():
    with open(REPO_ROOT / "pyproject.toml", "rb") as f:
        return tomllib.load(f)


def _names(reqs, extras):
    """Distribution names in a requirement list, expanding self-references like tundlekit[office]."""
    out = set()
    for r in reqs:
        m = re.match(r"\s*([A-Za-z0-9_.\-]+)\s*(?:\[([^\]]*)\])?", r)
        name = m.group(1).lower().replace("_", "-")
        if name == "tundlekit" and m.group(2):
            for ex in m.group(2).split(","):
                out |= _names(extras[ex.strip()], extras)
        else:
            out.add(name)
    return out


def test_pyproject_project_basics():
    """§12 project tundlekit, requires-python >= 3.10, no required dependencies."""
    proj = _pyproject()["project"]
    assert proj["name"] == "tundlekit"
    assert re.sub(r"\s", "", proj["requires-python"]) == ">=3.10"
    assert proj.get("dependencies", []) == []


def test_pyproject_version_matches_package():
    """§12 version from tundlekit.__version__ (static duplicate allowed)."""
    import tundlekit
    proj = _pyproject()["project"]
    if "version" in proj:
        assert proj["version"] == tundlekit.__version__
    else:
        assert "version" in proj.get("dynamic", [])


def test_pyproject_extras_office_and_pdf():
    """§12 office = python-pptx, Pillow; pdf = pymupdf."""
    extras = _pyproject()["project"]["optional-dependencies"]
    assert _names(extras["office"], extras) == {"python-pptx", "pillow"}
    assert _names(extras["pdf"], extras) == {"pymupdf"}


def test_pyproject_console_scripts():
    """§12 console scripts tundlekit and tundlekit-mcp."""
    scripts = _pyproject()["project"]["scripts"]
    assert scripts["tundlekit"].replace(" ", "") == "tundlekit.cli:console"
    assert scripts["tundlekit-mcp"].replace(" ", "") == "tundlekit.mcp_server:console"


def test_pyproject_all_and_dev_extras():
    """§12 all = office + pdf; dev = all + pytest."""
    extras = _pyproject()["project"]["optional-dependencies"]
    assert _names(extras["all"], extras) == {"python-pptx", "pillow", "pymupdf"}
    assert _names(extras["dev"], extras) == {"python-pptx", "pillow", "pymupdf", "pytest"}


def test_cli_console_exits_with_main_code(monkeypatch, capsys):
    """§12 console() calls sys.exit(main())."""
    from tundlekit import cli
    monkeypatch.setattr(sys, "argv", ["tundlekit", "--version"])
    with pytest.raises(SystemExit) as ei:
        cli.console()
    assert ei.value.code in (0, None)
    assert "tundlekit " in capsys.readouterr().out


def test_mcp_console_exits_0_on_empty_stdin():
    """§12 tundlekit-mcp console() = sys.exit(main()); §0.5 exit 0 when stdin closes."""
    code = "from tundlekit import mcp_server\nmcp_server.console()\n"
    p = subprocess.run([sys.executable, "-c", code], input=b"", capture_output=True, env=subprocess_env(),
                       cwd=str(REPO_ROOT), timeout=120)
    assert p.returncode == 0, p.stderr
    assert p.stdout == b""
