"""Tool registry shared by the CLI (`tundlekit call`) and the MCP server.

Every module registers its agent-facing functions with @tool. A registered function takes keyword
arguments that match its JSON Schema and returns a JSON-serialisable dict. User-facing failures
(bad input, refused operation) raise ToolError; anything else is a bug.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


class ToolError(Exception):
    """A failure the caller can act on: bad input, a refused operation, a missing dependency."""


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict
    func: Callable[..., dict]
    annotations: dict = field(default_factory=dict)

    def listing(self) -> dict:
        out = {"name": self.name, "description": self.description, "inputSchema": self.input_schema}
        if self.annotations:
            out["annotations"] = dict(self.annotations)
        return out


TOOLS: dict[str, Tool] = {}


def tool(name: str, description: str, schema: dict, **annotations: Any):
    """Register a function as an agent tool.

    schema: a JSON Schema object ({"type": "object", "properties": ..., "required": [...]}).
    annotations: MCP tool annotations, e.g. readOnlyHint=True, destructiveHint=True.
    """
    if schema.get("type") != "object":
        raise ValueError(f"{name}: schema must be a JSON Schema object")

    def wrap(func: Callable[..., dict]) -> Callable[..., dict]:
        if name in TOOLS and TOOLS[name].func is not func:
            raise ValueError(f"tool {name!r} registered twice")
        TOOLS[name] = Tool(name, description, schema, func, annotations)
        return func

    return wrap


_TYPES = {"string": str, "integer": int, "number": (int, float), "boolean": bool,
          "array": list, "object": dict, "null": type(None)}


def validate(schema: dict, args: dict) -> list[str]:
    """Shallow JSON Schema check of tool arguments: required, primitive types, enum, extras.

    Returns a list of problems, each naming the property. Nested objects are checked 1 level for type only.
    """
    problems = []
    if not isinstance(args, dict):
        return ["arguments must be an object"]
    props = schema.get("properties", {})
    for req in schema.get("required", []):
        if req not in args:
            problems.append(f"{req}: required property is missing")
    for key, value in args.items():
        spec = props.get(key)
        if spec is None:
            if schema.get("additionalProperties", True) is False:
                problems.append(f"{key}: unknown property")
            continue
        types = spec.get("type")
        if types is not None:
            types = types if isinstance(types, list) else [types]
            ok = False
            for t in types:
                py = _TYPES.get(t)
                if py is None:
                    ok = True
                    continue
                if t in ("integer", "number") and isinstance(value, bool):
                    continue
                if isinstance(value, py):
                    ok = True
            if not ok:
                problems.append(f"{key}: expected {' or '.join(types)}, got {type(value).__name__}")
                continue
        if "enum" in spec and value not in spec["enum"]:
            problems.append(f"{key}: must be one of {spec['enum']}, got {value!r}")
        if spec.get("type") == "array" and "items" in spec and isinstance(value, list):
            item_type = spec["items"].get("type")
            py = _TYPES.get(item_type) if isinstance(item_type, str) else None
            if py is not None:
                for i, item in enumerate(value):
                    if not isinstance(item, py) or (item_type in ("integer", "number") and isinstance(item, bool)):
                        problems.append(f"{key}[{i}]: expected {item_type}")
    return problems


def call(name: str, args: dict | None = None) -> dict:
    """Validate and run a registered tool. Raises KeyError for an unknown tool, ToolError for bad args."""
    t = TOOLS[name]
    args = args or {}
    problems = validate(t.input_schema, args)
    if problems:
        raise ToolError("invalid arguments: " + "; ".join(problems))
    return t.func(**args)


def load_all() -> dict[str, Tool]:
    """Import every tundlekit module so their @tool decorators run, then return the registry."""
    import importlib

    from tundlekit import MODULES

    for mod in MODULES:
        importlib.import_module(f"tundlekit.{mod}")
    # Registration follows import order, which cross-module imports can change; list tools in MODULES order.
    rank = {f"tundlekit.{mod}": i for i, mod in enumerate(MODULES)}

    def module_rank(t: Tool) -> int:
        name = t.func.__module__
        return rank.get(name, rank.get(name.rsplit(".", 1)[0], len(MODULES)))

    ordered = sorted(TOOLS.values(), key=module_rank)
    TOOLS.clear()
    TOOLS.update((t.name, t) for t in ordered)
    return TOOLS
