"""§1 registry (given code): ToolError, Tool, TOOLS, tool(), validate(), call(), load_all()."""
import pytest

from tundlekit import registry
from tundlekit.registry import Tool, ToolError


@pytest.fixture
def empty_registry(monkeypatch):
    monkeypatch.setattr(registry, "TOOLS", {})
    return registry


SCHEMA = {"type": "object",
          "properties": {"name": {"type": "string"}, "n": {"type": "integer"},
                         "mode": {"type": "string", "enum": ["a", "b"]},
                         "tags": {"type": "array", "items": {"type": "string"}}},
          "required": ["name"], "additionalProperties": False}


def test_tool_registers_and_listing(empty_registry):
    """§1 tool() registers a Tool; listing() has name, description, inputSchema, annotations."""
    @registry.tool("demo_echo", "Echo.", SCHEMA, readOnlyHint=True)
    def echo(**kw):
        return dict(kw)

    t = registry.TOOLS["demo_echo"]
    assert isinstance(t, Tool)
    assert t.func is echo
    assert t.listing() == {"name": "demo_echo", "description": "Echo.", "inputSchema": SCHEMA,
                           "annotations": {"readOnlyHint": True}}


def test_listing_without_annotations_has_no_key(empty_registry):
    """§1 listing() omits annotations when none were given."""
    @registry.tool("demo_plain", "Plain.", {"type": "object"})
    def plain():
        return {}

    assert "annotations" not in registry.TOOLS["demo_plain"].listing()


def test_tool_rejects_non_object_schema(empty_registry):
    """§1 tool(): schema must be a JSON Schema object."""
    with pytest.raises(ValueError):
        registry.tool("demo_bad", "Bad.", {"type": "array"})


def test_tool_registered_twice_with_other_function_fails(empty_registry):
    """§1 tool(): a name registered twice with different functions raises ValueError."""
    registry.tool("demo_dup", "d", {"type": "object"})(lambda: {})
    with pytest.raises(ValueError):
        registry.tool("demo_dup", "d", {"type": "object"})(lambda: {})


def test_call_validates_and_runs(empty_registry):
    """§1 call(): validates then runs with keyword arguments."""
    registry.tool("demo_echo", "Echo.", SCHEMA)(lambda **kw: dict(kw))
    assert registry.call("demo_echo", {"name": "x", "n": 3}) == {"name": "x", "n": 3}


def test_call_unknown_tool_is_keyerror(empty_registry):
    """§1 call(): unknown tool -> KeyError."""
    with pytest.raises(KeyError):
        registry.call("demo_missing", {})


def test_call_invalid_args_is_toolerror(empty_registry):
    """§1 call(): bad args -> ToolError('invalid arguments: ...') naming the property."""
    registry.tool("demo_echo", "Echo.", SCHEMA)(lambda **kw: dict(kw))
    with pytest.raises(ToolError) as ei:
        registry.call("demo_echo", {"n": 1})
    assert str(ei.value).startswith("invalid arguments: ")
    assert "name" in str(ei.value)


def test_validate_required_and_unknown():
    """§1 validate(): required and additionalProperties false."""
    problems = registry.validate(SCHEMA, {"extra": 1})
    assert any(p.startswith("name:") for p in problems)
    assert any(p.startswith("extra:") for p in problems)


def test_validate_types_bool_is_not_integer():
    """§1 validate(): primitive types; a bool is not an integer."""
    assert registry.validate(SCHEMA, {"name": "x", "n": True})
    assert registry.validate(SCHEMA, {"name": "x", "n": "3"})
    assert registry.validate(SCHEMA, {"name": "x", "n": 3}) == []


def test_validate_enum():
    """§1 validate(): enum."""
    assert registry.validate(SCHEMA, {"name": "x", "mode": "a"}) == []
    problems = registry.validate(SCHEMA, {"name": "x", "mode": "c"})
    assert len(problems) == 1 and problems[0].startswith("mode:")


def test_toolerror_is_exception():
    """§1 ToolError is an Exception carrying the message."""
    assert issubclass(ToolError, Exception)
    assert str(ToolError("boom")) == "boom"


def test_load_all_returns_registry_with_bundle_tools():
    """§1 load_all() imports every module and returns TOOLS; §0.1 modules register at import time."""
    tools = registry.load_all()
    assert tools is registry.TOOLS
    for name in ("bundle_status", "bundle_release", "bundle_compare", "bundle_prune",
                 "bundle_init", "bundle_lint", "bundle_verify"):
        assert name in tools


def test_validate_number_accepts_int_and_float_not_bool():
    """§1 validate(): number = int or float, never bool."""
    from tundlekit.registry import validate
    s = {"type": "object", "properties": {"x": {"type": "number"}}}
    assert validate(s, {"x": 1}) == []
    assert validate(s, {"x": 1.5}) == []
    assert validate(s, {"x": False}) != []


def test_validate_extras_allowed_unless_closed():
    """§1 validate(): unknown properties only rejected with additionalProperties false."""
    from tundlekit.registry import validate
    assert validate({"type": "object", "properties": {}}, {"zz": 1}) == []


def test_validate_array_items():
    """§1 validate(): array item types are checked, naming the index."""
    from tundlekit.registry import validate
    s = {"type": "object", "properties": {"tags": {"type": "array", "items": {"type": "string"}}}}
    assert validate(s, {"tags": ["a", 2]}) == ["tags[1]: expected string"]


def test_validate_non_dict_and_union_types():
    """§1 validate(): non-object arguments; type lists."""
    from tundlekit.registry import validate
    assert validate({"type": "object"}, [1]) == ["arguments must be an object"]
    s = {"type": "object", "properties": {"p": {"type": ["string", "null"]}}}
    assert validate(s, {"p": None}) == []
    assert validate(s, {"p": 3}) != []


def test_call_none_args_and_same_function_reregistered(empty_registry):
    """§1 call(name, None) passes no arguments; registering the same function twice is fine."""
    r = empty_registry

    def f(**kw):
        return {"kw": kw}

    r.tool("ho_f", "f", {"type": "object"})(f)
    r.tool("ho_f", "f", {"type": "object"})(f)
    assert r.call("ho_f", None) == {"kw": {}}


def test_listing_annotations_copy(empty_registry):
    """§1 Tool.listing() returns a copy of the annotations."""
    r = empty_registry
    r.tool("ho_g", "g", {"type": "object"}, readOnlyHint=True)(lambda: {})
    lst = r.TOOLS["ho_g"].listing()
    lst["annotations"]["readOnlyHint"] = False
    assert r.TOOLS["ho_g"].annotations == {"readOnlyHint": True}
