"""diagram: SVG diagrams from a JSON spec or a Mermaid flowchart subset (MANIFEST.md §4).

Standard library only. The drawing rules come from tundle's figures.py and palette.py: colour = stage,
style = actor (a model call is a tinted box with a MODEL tag, deterministic code a white box with a CODE tag,
a record a document with a folded corner, an external party a grey box), 1 box per model call, a legend
whenever more than 1 actor is shown, and every shape carries text so nothing depends on colour alone.

Layout is a small layered (Sugiyama-style) layout: back edges are found by depth-first search, ranks are
longest paths, edges that span several ranks get dummy points, and a barycentre pass is kept only when it
strictly reduces crossings. Everything is deterministic: the same spec gives byte-identical SVG.
"""
from __future__ import annotations

import importlib
import json
import math
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from dataclasses import dataclass, field

from tundlekit.palette import GREY, HAIR, INK, STAGE, tint
from tundlekit.registry import ToolError, tool

ID_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")   # always used with fullmatch
ACTORS = ("model", "code", "record", "external")
DIRECTIONS = ("LR", "TB")
DEFAULT_STAGE, DEFAULT_ACTOR, DEFAULT_DIRECTION = "dispatch", "code", "LR"

_TOP_KEYS = ("title", "direction", "nodes", "edges", "groups", "legend", "tags", "note", "wrap")
_NODE_KEYS = ("id", "label", "sub", "stage", "actor", "dashed", "rank")
_EDGE_KEYS = ("from", "to", "label", "dashed")
_GROUP_KEYS = ("id", "label", "nodes", "stage")

LEGEND_TEXT = {"model": "MODEL call", "code": "CODE (deterministic)", "record": "record", "external": "external"}
SESSION_TEXT = "1 box = 1 model session"


class _InputError(ToolError):
    """The input itself is malformed (bad JSON, a Mermaid syntax error): a spec problem for diagram_validate."""


# ====================================================================== spec validation
def _warn_unknown(obj: dict, known: tuple, where: str, warnings: list[str]) -> None:
    for key in obj:
        if key not in known:
            warnings.append(f"{where}: unknown key {key!r} is ignored")


def check_spec(spec) -> tuple[list[str], list[str]]:
    """Check a diagram spec (§4.1, §13.4). Returns (problems, warnings); problems carry JSON-path prefixes.

    Every field is type-checked before it is used, so a wrong type is a listed problem, never a crash.
    """
    problems: list[str] = []
    warnings: list[str] = []
    if not isinstance(spec, dict):
        return ["spec: must be a JSON object"], warnings
    _warn_unknown(spec, _TOP_KEYS, "spec", warnings)

    _check_text(spec, "title", "", problems)
    _check_text(spec, "note", "", problems)
    _check_choice(spec, "direction", "", DIRECTIONS, problems)
    legend = spec.get("legend", "auto")
    if not (legend is True or legend is False or legend == "auto"):
        problems.append(f"legend: must be \"auto\", true or false, got {_show(legend)}")
    _check_bool(spec, "tags", "", problems)
    _check_count(spec, "wrap", "", 1, problems)

    ids: dict[str, str] = {}          # id -> where it was defined (nodes and groups share 1 namespace)
    node_ids: set[str] = set()
    nodes = spec.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        problems.append("nodes: must be a non-empty list of node objects")
        nodes = nodes if isinstance(nodes, list) else []
    for i, n in enumerate(nodes):
        where = f"nodes[{i}]"
        if not isinstance(n, dict):
            problems.append(f"{where}: must be an object")
            continue
        _warn_unknown(n, _NODE_KEYS, where, warnings)
        _check_id(n.get("id"), where, ids, problems, node_ids)
        _check_text(n, "label", where, problems, required=True)
        _check_text(n, "sub", where, problems)
        _check_choice(n, "stage", where, tuple(STAGE), problems)
        _check_choice(n, "actor", where, ACTORS, problems)
        _check_bool(n, "dashed", where, problems)
        _check_count(n, "rank", where, 0, problems)

    edges = spec.get("edges", [])
    if not isinstance(edges, list):
        problems.append("edges: must be a list of edge objects")
        edges = []
    for j, e in enumerate(edges):
        where = f"edges[{j}]"
        if not isinstance(e, dict):
            problems.append(f"{where}: must be an object")
            continue
        _warn_unknown(e, _EDGE_KEYS, where, warnings)
        for end in ("from", "to"):
            ref = e.get(end)
            if not isinstance(ref, str):
                problems.append(f"{where}.{end}: must be a node id string")
            elif ref not in node_ids:
                problems.append(f"{where}.{end}: unknown node {_show(ref)}")
        if isinstance(e.get("from"), str) and e.get("from") == e.get("to"):
            problems.append(f"{where}: self-loop on {_show(e['from'])} is not allowed")
        _check_text(e, "label", where, problems)
        _check_bool(e, "dashed", where, problems)

    groups = spec.get("groups", [])
    if not isinstance(groups, list):
        problems.append("groups: must be a list of group objects")
        groups = []
    owner: dict[str, str] = {}
    for k, g in enumerate(groups):
        where = f"groups[{k}]"
        if not isinstance(g, dict):
            problems.append(f"{where}: must be an object")
            continue
        _warn_unknown(g, _GROUP_KEYS, where, warnings)
        _check_id(g.get("id"), where, ids, problems)
        _check_text(g, "label", where, problems)
        _check_choice(g, "stage", where, tuple(STAGE), problems)
        members = g.get("nodes")
        if not isinstance(members, list) or not members:
            problems.append(f"{where}.nodes: must be a non-empty list of node ids")
            continue
        gid = g.get("id") if isinstance(g.get("id"), str) else where
        for m, ref in enumerate(members):
            if not isinstance(ref, str):
                problems.append(f"{where}.nodes[{m}]: must be a node id string")
            elif ref not in node_ids:
                problems.append(f"{where}.nodes[{m}]: unknown node {_show(ref)}")
            elif ref in owner:
                problems.append(f"{where}.nodes[{m}]: node {_show(ref)} already belongs to group {_show(owner[ref])}")
            else:
                owner[ref] = gid
    return problems, warnings


# control characters other than tab, line feed and carriage return (\r is written as a line break, section 13.6)
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")


def _show(value) -> str:
    """A short repr for messages (long or huge values are cut)."""
    try:
        text = repr(value)
    except ValueError:              # an int beyond Python's digit limit
        return f"<{type(value).__name__} too large to show>"
    return text if len(text) <= 60 else text[:57] + "..."


def _field(where: str, key: str) -> str:
    return f"{where}.{key}" if where else key


def _check_text(obj: dict, key: str, where: str, problems: list, required: bool = False) -> None:
    name = _field(where, key)
    if key not in obj:
        if required:
            problems.append(f"{name}: required non-empty string is missing")
        return
    value = obj[key]
    if not isinstance(value, str):
        problems.append(f"{name}: must be a string, got {type(value).__name__}")
        return
    if required and not value.strip():
        problems.append(f"{name}: must be a non-empty string")
    bad = _CONTROL.search(value)
    if bad:
        problems.append(f"{name}: contains control character U+{ord(bad.group(0)):04X}")


def _check_choice(obj: dict, key: str, where: str, choices: tuple, problems: list) -> None:
    if key not in obj:
        return
    value = obj[key]
    if not isinstance(value, str) or value not in choices:
        problems.append(f"{_field(where, key)}: must be one of {', '.join(choices)}, got {_show(value)}")


def _check_bool(obj: dict, key: str, where: str, problems: list) -> None:
    if key in obj and not isinstance(obj[key], bool):
        problems.append(f"{_field(where, key)}: must be true or false, got {_show(obj[key])}")


def _check_count(obj: dict, key: str, where: str, minimum: int, problems: list) -> None:
    """An optional integer >= minimum (booleans, strings and floats are refused; §13.4 finite)."""
    if key not in obj:
        return
    value = obj[key]
    ok = isinstance(value, int) and not isinstance(value, bool) and value >= minimum
    if ok:
        try:
            ok = math.isfinite(float(value))
        except OverflowError:
            ok = False
    if not ok:
        problems.append(f"{_field(where, key)}: must be an integer >= {minimum}, got {_show(value)}")


def _check_id(value, where: str, ids: dict, problems: list, node_ids: set | None = None) -> None:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        problems.append(f"{where}.id: must match {ID_RE.pattern}, got {_show(value)}")
    elif value in ids:
        problems.append(f"{where}.id: duplicate id {_show(value)} (already used by {ids[value]})")
    else:
        ids[value] = where
        if node_ids is not None:
            node_ids.add(value)


def _require_valid(spec) -> list[str]:
    """Raise 1 ToolError listing every problem; return the warnings otherwise."""
    problems, warnings = check_spec(spec)
    if problems:
        raise ToolError("invalid diagram spec: " + "; ".join(problems))
    return warnings


# ====================================================================== input sources
def _read_file(path: str, what: str) -> str:
    p = pathlib.Path(path)
    try:
        return p.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise ToolError(f"{what}: file not found: {path}") from None
    except IsADirectoryError:
        raise ToolError(f"{what}: is a directory: {path}") from None
    except UnicodeDecodeError:
        raise ToolError(f"{what}: not UTF-8 text: {path}") from None
    except OSError as e:
        raise ToolError(f"{what}: cannot read {path}: {e}") from None


def _load_source(spec=None, spec_path=None, mermaid=None, mermaid_path=None) -> tuple[dict, list[str]]:
    """Resolve exactly 1 input to a spec. Returns (spec, warnings from the Mermaid import)."""
    given = [name for name, value in (("spec", spec), ("spec_path", spec_path), ("mermaid", mermaid),
                                      ("mermaid_path", mermaid_path)) if value is not None]
    if len(given) != 1:
        detail = f" (got {', '.join(given)})" if given else ""
        raise ToolError(f"give exactly 1 of spec, spec_path, mermaid or mermaid_path{detail}")
    if spec_path is not None:
        text = _read_file(spec_path, "spec_path")
        try:
            spec = json.loads(text)
        except ValueError as e:
            raise _InputError(f"spec_path: {spec_path} is not valid JSON: {e}") from None
        if not isinstance(spec, dict):
            raise _InputError(f"spec_path: {spec_path} must hold a JSON object")
        return spec, []
    if mermaid_path is not None:
        mermaid = _read_file(mermaid_path, "mermaid_path")
    if mermaid is not None:
        return mermaid_to_spec(mermaid)
    return spec, []


# ====================================================================== Mermaid subset (§4.4)
_MM_HEADER = re.compile(r"^(?:flowchart|graph)\b(?:\s+(\S+))?\s*$")
_MM_DIRECTIONS = {"LR": "LR", "RL": "LR", "TB": "TB", "TD": "TB", "BT": "TB"}
_MM_IGNORED = re.compile(r"^(classDef|class|style|linkStyle|click)\s")
_MM_GROUP_STAGE = re.compile(r"^%%\s*group\s+(\S+)\s+stage\s+(\S+)\s*$")
_MM_KEYWORDS = {"end", "subgraph", "graph", "flowchart", "style", "class", "classdef", "click", "linkstyle"}
_MM_UNSAFE_ID = ("--", "-.", "==", "&")
_MM_SUBGRAPH = re.compile(r"^subgraph\s+(\S+?)\s*(?:\[(.*)\])?\s*$")
# an id may contain "-", but not where an arrow starts ("-->", "---", "-- text", "-.")
_MM_ID = re.compile(r"[A-Za-z_](?:[A-Za-z0-9_]|-(?!-[->\s]|\.))*")
_MM_SHAPES = (("[(", ")]", "record"), ("{{", "}}", "external"), ("[", "]", "code"),
              ("(", ")", "model"), (">", "]", "record"))
_MM_CLASS = re.compile(r":::([A-Za-z0-9_-]+)")
_MM_EDGE = re.compile(r"""
      (?P<solid>-{2,}>|-{3,}|={2,}>|={3,})
    | (?P<dotted>-\.+->|-\.+-)
    | --\s+(?P<solid_text>.+?)\s+(?:-{2,}>|-{3,})
    | ==\s+(?P<thick_text>.+?)\s+(?:={2,}>|={3,})
    | -\.\s+(?P<dotted_text>.+?)\s+\.-+>?
""", re.VERBOSE)
_MM_PIPE = re.compile(r"\s*\|([^|]*)\|")
_MM_BR = re.compile(r"<br\s*/?>", re.IGNORECASE)
_MM_ENTITY = re.compile(r"#(quot|lt|gt|amp|\d+);")
_MM_NAMED = {"quot": '"', "lt": "<", "gt": ">", "amp": "&"}


def _mm_decode(text: str, strip: bool = True) -> str:
    """Mermaid label text to plain text: strip quotes, <br> to newline, entity codes (#quot;) to characters.

    With strip False (edge labels between pipes) the text keeps its surrounding spaces.
    """
    if strip:
        text = text.strip()
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        text = text[1:-1]
    text = _MM_BR.sub("\n", text)

    def entity(m: re.Match) -> str:
        name = m.group(1)
        if name.isdigit():
            code = int(name)
            return chr(code) if 0 < code < 0x110000 else m.group(0)
        return _MM_NAMED[name]

    return _MM_ENTITY.sub(entity, text)


def _mm_encode(text: str) -> str:
    """Plain text to Mermaid label text that _mm_decode turns back into the same string."""
    text = text.replace("#", "#35;").replace('"', "#quot;").replace("|", "#124;")
    text = text.replace("<", "#lt;").replace(">", "#gt;")
    return text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")


class _MermaidParser:
    """Parse the §4.4 flowchart subset into a diagram spec."""

    def __init__(self, text: str):
        self.lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        self.direction: str | None = None
        self.nodes: dict[str, dict] = {}
        self.edges: list[dict] = []
        self.groups: list[dict] = []
        self.member_of: dict[str, str] = {}
        self.open_groups: list[tuple[dict, int]] = []
        self.warnings: list[str] = []
        self.group_stages: dict[str, tuple[str, int]] = {}
        self.lineno = 0

    def error(self, detail: str) -> _InputError:
        return _InputError(f"mermaid line {self.lineno}: {detail}")

    def parse(self) -> dict:
        for self.lineno, raw in enumerate(self.lines, 1):
            line = raw.strip()
            stage_comment = _MM_GROUP_STAGE.match(line)
            if stage_comment:
                self.group_stages[stage_comment.group(1)] = (stage_comment.group(2), self.lineno)
            if not line or line.startswith("%%"):
                continue
            if line.endswith(";"):
                line = line[:-1].rstrip()
            if self.direction is None:
                self._header(line)
            elif _MM_IGNORED.match(line):
                self.warnings.append(f"line {self.lineno}: {line.split()[0]} statements are ignored")
            elif line == "end":
                if not self.open_groups:
                    raise self.error("'end' without an open subgraph")
                self._close_group()
            elif line == "subgraph" or line.startswith(("subgraph ", "subgraph\t")):
                self._subgraph(line)
            else:
                self._statement(line)
        if self.direction is None:
            self.lineno = len(self.lines)
            raise self.error("no 'flowchart' or 'graph' header found")
        while self.open_groups:
            group, opened = self.open_groups[-1]
            self.warnings.append(f"line {opened}: subgraph {group['id']!r} has no 'end'; closed at the end of input")
            self._close_group()
        self._apply_group_stages()
        return {"direction": self.direction, "nodes": list(self.nodes.values()), "edges": self.edges,
                "groups": self.groups}

    def _apply_group_stages(self) -> None:
        """Apply `%% group <id> stage <stage>` comments (written by spec_to_mermaid, §13.6)."""
        by_id = {g["id"]: g for g in self.groups}
        for gid, (stage, lineno) in self.group_stages.items():
            if gid not in by_id:
                self.warnings.append(f"line {lineno}: stage comment for unknown group {gid!r} is ignored")
            elif stage not in STAGE:
                self.warnings.append(f"line {lineno}: {stage!r} is not a palette stage; group {gid!r} keeps none")
            else:
                by_id[gid]["stage"] = stage

    # -- lines
    def _header(self, line: str) -> None:
        m = _MM_HEADER.match(line)
        if not m:
            raise self.error(f"expected a 'flowchart' or 'graph' header, got {line!r}")
        word = m.group(1)
        if word is None:
            self.direction = "TB"
        elif word.upper() in _MM_DIRECTIONS:
            self.direction = _MM_DIRECTIONS[word.upper()]
        else:
            raise self.error(f"unknown direction {word!r} (use LR, RL, TB, TD or BT)")

    def _subgraph(self, line: str) -> None:
        m = _MM_SUBGRAPH.match(line)
        if not m or not ID_RE.fullmatch(m.group(1)):
            raise self.error(f"expected 'subgraph id' or 'subgraph id [label]', got {line!r}")
        group = {"id": m.group(1)}
        if m.group(2) is not None:
            group["label"] = _mm_decode(m.group(2))
        group["nodes"] = []
        self.groups.append(group)            # listed in opening order; dropped again if it stays empty
        self.open_groups.append((group, self.lineno))

    def _close_group(self) -> None:
        group, opened = self.open_groups.pop()
        if not group["nodes"]:
            self.groups.remove(group)
            self.warnings.append(f"line {opened}: subgraph {group['id']!r} has no nodes and is dropped")

    def _statement(self, line: str) -> None:
        pos, left = self._node_list(line, 0)
        pos = self._skip_space(line, pos)
        while pos < len(line):
            m = _MM_EDGE.match(line, pos)
            if not m:
                raise self.error(f"expected an arrow at column {pos + 1}: {line!r}")
            pos = m.end()
            text = m.group("solid_text") or m.group("thick_text") or m.group("dotted_text")
            dashed = m.group("dotted") is not None or m.group("dotted_text") is not None
            if text is None:
                pipe = _MM_PIPE.match(line, pos)
                if pipe:
                    pos = pipe.end()
                    label = _mm_decode(pipe.group(1), strip=False)
                else:
                    label = ""
            else:
                label = _mm_decode(text)
            pos, right = self._node_list(line, self._skip_space(line, pos))
            for a in left:
                for b in right:
                    edge = {"from": a, "to": b}
                    if label:
                        edge["label"] = label
                    edge["dashed"] = dashed
                    self.edges.append(edge)
            left = right
            pos = self._skip_space(line, pos)

    # -- tokens
    @staticmethod
    def _skip_space(line: str, pos: int) -> int:
        while pos < len(line) and line[pos] in " \t":
            pos += 1
        return pos

    def _node_list(self, line: str, pos: int) -> tuple[int, list[str]]:
        ids = []
        while True:
            pos, nid = self._node_ref(line, pos)
            ids.append(nid)
            after = self._skip_space(line, pos)
            if after < len(line) and line[after] == "&":
                pos = self._skip_space(line, after + 1)
                continue
            return pos, ids

    def _node_ref(self, line: str, pos: int) -> tuple[int, str]:
        m = _MM_ID.match(line, pos)
        if not m:
            raise self.error(f"expected a node id (ASCII letters, digits, _ and -, not starting with a digit) "
                             f"at column {pos + 1}: {line!r}")
        nid, pos = m.group(0), m.end()
        label = actor = None
        for opener, closer, shape_actor in _MM_SHAPES:
            if line.startswith(opener, pos):
                label, pos = self._shape_text(line, pos + len(opener), closer)
                actor = shape_actor
                break
        stage = None
        cm = _MM_CLASS.match(line, pos)
        if cm:
            stage, pos = cm.group(1), cm.end()
        if pos < len(line) and line[pos] not in " \t&-=.":
            raise self.error(f"unexpected {line[pos]!r} at column {pos + 1}: {line!r}")
        self._touch(nid, label, actor, stage)
        return pos, nid

    def _shape_text(self, line: str, pos: int, closer: str) -> tuple[str, int]:
        if pos < len(line) and line[pos] == '"':
            end_quote = line.find('"', pos + 1)
            if end_quote < 0 or not line.startswith(closer, end_quote + 1):
                raise self.error(f"unterminated quoted label at column {pos + 1}: {line!r}")
            return _mm_decode(line[pos:end_quote + 1]), end_quote + 1 + len(closer)
        end = line.find(closer, pos)
        if end < 0:
            raise self.error(f"missing {closer!r} after the label at column {pos + 1}: {line!r}")
        return _mm_decode(line[pos:end]), end + len(closer)

    def _touch(self, nid: str, label, actor, stage) -> None:
        node = self.nodes.get(nid)
        if node is None:
            node = {"id": nid, "label": nid, "stage": DEFAULT_STAGE, "actor": DEFAULT_ACTOR}
            self.nodes[nid] = node
        if actor is not None:
            node["label"], node["actor"] = label, actor
        if stage is not None:
            if stage in STAGE:
                node["stage"] = stage
            else:
                self.warnings.append(f"line {self.lineno}: ':::{stage}' on {nid!r} is not a palette stage "
                                     f"and is ignored")
        if self.open_groups and nid not in self.member_of:
            group = self.open_groups[-1][0]
            group["nodes"].append(nid)
            self.member_of[nid] = group["id"]


def mermaid_to_spec(text: str) -> tuple[dict, list[str]]:
    """Parse Mermaid flowchart text (§4.4). Returns (spec, warnings); raises ToolError naming the line."""
    if not isinstance(text, str):
        raise ToolError("mermaid: must be a string")
    parser = _MermaidParser(text)
    spec = parser.parse()
    warnings = list(parser.warnings)
    problems, _ = check_spec(spec)
    warnings += [f"the imported spec is not valid: {p}" for p in problems]
    return spec, warnings


def _check_mermaid_ids(spec: dict) -> None:
    """Refuse ids Mermaid would read as keywords or arrows (§13.6)."""
    bad = []
    for kind, items in (("node", spec["nodes"]), ("group", spec.get("groups", []))):
        for item in items:
            ident = item["id"]
            if ident.lower() in _MM_KEYWORDS:
                bad.append(f"{kind} id {ident!r} is a Mermaid keyword")
            elif any(seq in ident for seq in _MM_UNSAFE_ID):
                bad.append(f"{kind} id {ident!r} contains an arrow sequence ('--', '-.', '==' or '&')")
    if bad:
        raise ToolError("cannot write Mermaid: " + "; ".join(bad) + "; rename these ids")


def spec_to_mermaid(spec: dict) -> str:
    """Write a valid spec as Mermaid (§4.4). `sub` is folded into the label as a further line.

    A group's stage has no Mermaid syntax, so it is kept in a `%% group <id> stage <stage>` comment.
    """
    _check_mermaid_ids(spec)
    direction = spec.get("direction", DEFAULT_DIRECTION)
    lines = [f"flowchart {direction}"]
    opener = {"code": ("[", "]"), "model": ("(", ")"), "record": ("[(", ")]"), "external": ("{{", "}}")}
    for n in spec["nodes"]:
        label = n["label"] + ("\n" + n["sub"] if n.get("sub") else "")
        o, c = opener[n.get("actor", DEFAULT_ACTOR)]
        lines.append(f'    {n["id"]}{o}"{_mm_encode(label)}"{c}:::{n.get("stage", DEFAULT_STAGE)}')
    for g in spec.get("groups", []):
        if g.get("stage"):
            lines.append(f"    %% group {g['id']} stage {g['stage']}")
        head = f"    subgraph {g['id']}"
        if "label" in g:
            head += f' ["{_mm_encode(g["label"])}"]'
        lines.append(head)
        lines += [f"        {m}" for m in g["nodes"]]
        lines.append("    end")
    for e in spec.get("edges", []):
        arrow = "-.->" if e.get("dashed") else "-->"
        label = f"|{_mm_encode(e['label'])}|" if e.get("label") else ""
        lines.append(f"    {e['from']} {arrow}{label} {e['to']}")
    return "\n".join(lines) + "\n"


# ====================================================================== text metrics
FONT = "Helvetica, Arial, 'DejaVu Sans', sans-serif"
LABEL_PX, SUB_PX, TAG_PX, EDGE_PX, GROUP_PX, TITLE_PX, NOTE_PX, LEGEND_PX = 13, 11, 9, 11, 11, 16, 11, 11
PAD_X, PAD_Y = 14, 9           # inside a node box
MIN_W, MIN_H = 96, 40
TAG_ROW = 16                   # height reserved for the MODEL / CODE tag
MARGIN = 20
NODE_GAP = 22                  # between neighbours in the same rank
RANK_GAP = {"LR": 56, "TB": 48}
ROW_GAP = {"LR": 40, "TB": 48}         # the channel between wrapped rows (columns in TB)
GROUP_PAD, GROUP_LABEL_H = 12, 18
DUMMY = 8                      # cross-axis room for an edge passing through a rank


def _line_height(px: int) -> float:
    return round(px * 1.35, 2)


def _text_width(text: str, px: float, bold: bool = False) -> float:
    """A generous estimate of rendered text width, so labels always fit their boxes."""
    em = 0.0
    for ch in text:
        if unicodedata.combining(ch):
            continue
        if unicodedata.east_asian_width(ch) in ("W", "F"):
            em += 1.0
        elif ch in " iljI.,:;'|!`":
            em += 0.32
        elif ch in "mwMW@%":
            em += 0.92
        elif ch.isupper() or ch.isdigit():
            em += 0.7
        else:
            em += 0.6
    return em * px * (1.08 if bold else 1.0)


def _lines_width(lines: list[str], px: float, bold: bool = False) -> float:
    return max((_text_width(s, px, bold) for s in lines), default=0.0)


_XML_BAD = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]")


def _esc(text: str) -> str:
    text = _XML_BAD.sub("", text.replace("\t", " "))
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _attr(text: str) -> str:
    return _esc(text).replace('"', "&quot;")


def _fmt(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _num(v: float):
    v = round(v, 2)
    return int(v) if v == int(v) else v


def _colour(c: str) -> str:
    return c.lower()


# ====================================================================== model
@dataclass
class _Node:
    id: str
    label: list[str]
    sub: list[str]
    stage: str
    actor: str
    dashed: bool
    tag: bool
    group: str | None = None
    rank: int = 0
    level: int = 0                  # index of the rank among the ranks that hold nodes
    w: float = 0.0
    h: float = 0.0
    x: float = 0.0
    y: float = 0.0


@dataclass
class _Edge:
    src: str
    dst: str
    label: list[str]
    dashed: bool
    back: bool = False
    flat: bool = False                              # both ends in the same rank
    chain: list = field(default_factory=list)       # layer items from the lower rank to the higher
    split: int | None = None                        # chain index where the chain continues in a later row
    path: list = field(default_factory=list)        # [(command, [(x, y), ...]), ...]
    label_box: tuple | None = None                  # (cx, cy, w, h)
    label_gap: tuple | None = None                  # ("gap", level) or ("channel", row) holding the label


@dataclass
class _Group:
    id: str
    label: str
    members: list[str]
    stage: str | None
    rect: tuple = (0.0, 0.0, 0.0, 0.0)


def _split(text: str) -> list[str]:
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def _build_model(spec: dict):
    tags = spec.get("tags", True)
    nodes = {}
    for n in spec["nodes"]:
        actor = n.get("actor", DEFAULT_ACTOR)
        nodes[n["id"]] = _Node(n["id"], _split(n["label"]), _split(n["sub"]) if n.get("sub") else [],
                               n.get("stage", DEFAULT_STAGE), actor, bool(n.get("dashed", False)),
                               bool(tags) and actor in ("model", "code"))
    edges = [_Edge(e["from"], e["to"], _split(e["label"]) if e.get("label") else [], bool(e.get("dashed", False)))
             for e in spec.get("edges", [])]
    groups = []
    for g in spec.get("groups", []):
        groups.append(_Group(g["id"], " ".join(_split(g.get("label", g["id"]))), list(g["nodes"]), g.get("stage")))
        for m in g["nodes"]:
            nodes[m].group = g["id"]
    return nodes, edges, groups


def _size_node(n: _Node) -> None:
    widths = [_lines_width(n.label, LABEL_PX, bold=True), _lines_width(n.sub, SUB_PX)]
    if n.tag:
        widths.append(_text_width("MODEL", TAG_PX, bold=True) + 12)
    fold = 8 if n.actor == "record" else 0
    n.w = max(MIN_W, math.ceil(max(widths) + 2 * PAD_X + fold))
    text_h = len(n.label) * _line_height(LABEL_PX) + len(n.sub) * _line_height(SUB_PX) + (2 if n.sub else 0)
    n.h = max(MIN_H, math.ceil(text_h + 2 * PAD_Y + (TAG_ROW if n.tag else 0)))


# ====================================================================== layout
def _mark_back_edges(order: list[str], edges: list[_Edge]) -> None:
    """Depth-first search from nodes in spec order; an edge into a node on the stack is a back edge."""
    out = {nid: [] for nid in order}
    for e in edges:
        out[e.src].append(e)
    state = dict.fromkeys(order, 0)            # 0 unseen, 1 on the stack, 2 finished
    for root in order:
        if state[root]:
            continue
        state[root] = 1
        stack = [(root, iter(out[root]))]
        while stack:
            nid, it = stack[-1]
            e = next(it, None)
            if e is None:
                state[nid] = 2
                stack.pop()
            elif state[e.dst] == 1:
                e.back = True
            elif state[e.dst] == 0:
                state[e.dst] = 1
                stack.append((e.dst, iter(out[e.dst])))


def _assign_ranks(order: list[str], nodes: dict, edges: list[_Edge], fixed: dict | None = None) -> None:
    """rank = longest path from a source over the forward edges (topological order, spec order for ties).

    Nodes in `fixed` keep their given rank (§14.6). Back edges are found by depth-first search over the edges
    that do not join 2 fixed nodes. Afterwards every edge is classed by its final ranks: forward, back
    (against the ranks) or flat (both ends in the same rank).
    """
    fixed = fixed or {}
    _mark_back_edges(order, [e for e in edges if not (e.src in fixed and e.dst in fixed)])
    succ = {nid: [] for nid in order}
    indeg = dict.fromkeys(order, 0)
    for e in edges:
        if not e.back and not (e.src in fixed and e.dst in fixed):
            succ[e.src].append(e.dst)
            indeg[e.dst] += 1
    for nid in order:
        nodes[nid].rank = fixed.get(nid, 0)
    ready = [nid for nid in order if indeg[nid] == 0]
    i = 0
    while i < len(ready):
        u = ready[i]
        i += 1
        for v in succ[u]:
            if v not in fixed:
                nodes[v].rank = max(nodes[v].rank, nodes[u].rank + 1)
            indeg[v] -= 1
            if indeg[v] == 0:
                ready.append(v)
    for e in edges:
        a, b = nodes[e.src].rank, nodes[e.dst].rank
        e.back, e.flat = a > b, a == b


def _crossings(layers: list[list], segments: list[tuple]) -> int:
    pos = [{item: i for i, item in enumerate(layer)} for layer in layers]
    by_rank: dict[int, list[tuple[int, int]]] = {}
    for r, a, b in segments:
        by_rank.setdefault(r, []).append((pos[r][a], pos[r + 1][b]))
    total = 0
    for pairs in by_rank.values():
        for i, (a1, b1) in enumerate(pairs):
            for a2, b2 in pairs[i + 1:]:
                if (a1 - a2) * (b1 - b2) < 0:
                    total += 1
    return total


def _order_layers(layers: list[list], segments: list[tuple]) -> list[list]:
    """Keep spec order unless barycentre sweeps strictly reduce the number of crossings."""
    best = [list(layer) for layer in layers]
    best_count = _crossings(best, segments)
    if best_count == 0 or len(layers) < 2:
        return best
    preds: dict = {}
    succs: dict = {}
    for _, a, b in segments:
        preds.setdefault(b, []).append(a)
        succs.setdefault(a, []).append(b)
    current = [list(layer) for layer in layers]

    def sweep(ranks, neighbours, offset):
        for r in ranks:
            ref = {item: i for i, item in enumerate(current[r + offset])}
            own = {item: i for i, item in enumerate(current[r])}

            def key(item):
                near = neighbours.get(item)
                bary = sum(ref[x] for x in near) / len(near) if near else float(own[item])
                return (bary, own[item])

            current[r] = sorted(current[r], key=key)

    for _ in range(6):
        for ranks, neighbours, offset in ((range(1, len(current)), preds, -1),
                                          (range(len(current) - 2, -1, -1), succs, 1)):
            sweep(ranks, neighbours, offset)
            count = _crossings(current, segments)
            if count < best_count:
                best, best_count = [list(layer) for layer in current], count
        if best_count == 0:
            break
    return best


class _Layout:
    """Compute node boxes, edge paths, group rectangles and the canvas for 1 validated spec.

    Ranks are compacted into levels (only ranks that hold a node take room), and levels are grouped into rows
    of `wrap` ranks (§14.6): the main axis restarts in every row and rows stack along the cross axis. An edge
    between rows leaves its row through the gap after the row's last level (the tail), runs along the channel
    below the row and enters its target's row from the gutter before the first level.
    """

    def __init__(self, spec: dict):
        self.spec = spec
        self.direction = spec.get("direction", DEFAULT_DIRECTION)
        self.lr = self.direction == "LR"
        self.wrap = spec.get("wrap")
        self.nodes, self.edges, self.groups = _build_model(spec)
        self.order = list(self.nodes)
        for n in self.nodes.values():
            _size_node(n)
        fixed = {n["id"]: n["rank"] for n in spec["nodes"] if "rank" in n}
        _assign_ranks(self.order, self.nodes, self.edges, fixed)
        self._make_levels()
        self._build_layers()
        self._place_main_axis()
        self._place_cross_axis()
        self._route_edges()
        self._place_groups()

    # -- helpers on layer items: a node id (str) or a dummy ("~", edge index, level)
    def _level(self, item) -> int:
        return self.nodes[item].level if isinstance(item, str) else item[2]

    def _main_size(self, item) -> float:
        if isinstance(item, str):
            n = self.nodes[item]
            return n.w if self.lr else n.h
        return 0.0

    def _cross_size(self, item) -> float:
        if isinstance(item, str):
            n = self.nodes[item]
            return n.h if self.lr else n.w
        return DUMMY

    def _group_of(self, item):
        return self.nodes[item].group if isinstance(item, str) else None

    def _point(self, main: float, cross: float) -> tuple[float, float]:
        return (main, cross) if self.lr else (cross, main)

    def _near(self, n: _Node) -> float:
        return n.x if self.lr else n.y

    def _far(self, n: _Node) -> float:
        return (n.x + n.w) if self.lr else (n.y + n.h)

    # -- steps
    def _make_levels(self) -> None:
        ranks = sorted({n.rank for n in self.nodes.values()})
        level_of = {r: i for i, r in enumerate(ranks)}
        for n in self.nodes.values():
            n.level = level_of[n.rank]
        self.n_levels = len(ranks)
        keys = [r // self.wrap if self.wrap else 0 for r in ranks]
        row_index = {k: i for i, k in enumerate(sorted(set(keys)))}
        self.row_of = [row_index[k] for k in keys]
        self.rows = []                   # [(first level, last level)]
        for level, row in enumerate(self.row_of):
            if row == len(self.rows):
                self.rows.append((level, level))
            else:
                self.rows[row] = (self.rows[row][0], level)

    def _build_layers(self) -> None:
        layers = [[] for _ in range(self.n_levels)]
        for nid in self.order:
            layers[self.nodes[nid].level].append(nid)
        segments = []
        for k, e in enumerate(self.edges):
            if e.flat:
                e.chain = [e.src, e.dst]
                continue
            low, high = (e.dst, e.src) if e.back else (e.src, e.dst)
            l0, l1 = self.nodes[low].level, self.nodes[high].level
            r0, r1 = self.row_of[l0], self.row_of[l1]
            if r0 == r1:
                parts = [[low] + [("~", k, lv) for lv in range(l0 + 1, l1)] + [high]]
            else:
                first = [low] + [("~", k, lv) for lv in range(l0 + 1, self.rows[r0][1] + 1)]
                second = [("~", k, lv) for lv in range(self.rows[r1][0], l1)] + [high]
                parts = [first, second]
                e.split = len(first)
            e.chain = [item for part in parts for item in part]
            for part in parts:
                for item in part:
                    if not isinstance(item, str):
                        layers[item[2]].append(item)
                start = self._level(part[0])
                for i in range(len(part) - 1):
                    segments.append((start + i, part[i], part[i + 1]))
        self.layers = _order_layers(layers, segments)

    def _label_level(self, e: _Edge) -> int | None:
        """The level whose following gap holds the edge's label (None: the label sits in a row channel)."""
        if e.split is not None:
            return None
        src = self.nodes[e.src].level
        return src - 1 if e.back else src

    def _place_main_axis(self) -> None:
        thick = [max(self._main_size(i) for i in layer if isinstance(i, str)) for layer in self.layers]
        before = [0.0] * self.n_levels      # group padding needed before / after each level
        after = [0.0] * self.n_levels
        for g in self.groups:
            levels = [self.nodes[m].level for m in g.members]
            before[min(levels)] = max(before[min(levels)], GROUP_PAD + (0 if self.lr else GROUP_LABEL_H))
            after[max(levels)] = max(after[max(levels)], GROUP_PAD)
        need = [0.0] * self.n_levels         # room an edge label needs in the gap after each level
        for e in self.edges:
            level = self._label_level(e) if e.label else None
            if level is not None:            # the label sits in the gap next to the edge's source
                w, h = self._label_size(e)
                need[level] = max(need[level], (w if self.lr else h) + 16)
        self.layer_start = [0.0] * self.n_levels
        self.layer_end = [0.0] * self.n_levels
        self.free = [(0.0, 0.0)] * self.n_levels     # the gap after each level (after a row's last: its tail)
        for first, last in self.rows:
            pos = before[first]
            for r in range(first, last + 1):
                self.layer_start[r] = pos
                self.layer_end[r] = pos + thick[r]
                free_start = pos + thick[r] + after[r]
                free = max(RANK_GAP[self.direction], need[r])
                self.free[r] = (free_start, free_start + free)
                if r < last:
                    pos = free_start + free + before[r + 1]
        for n in self.nodes.values():
            main = self.layer_start[n.level] + (thick[n.level] - self._main_size(n.id)) / 2
            if self.lr:
                n.x = main
            else:
                n.y = main

    def _place_cross_axis(self) -> None:
        self.cross_pos: dict = {}
        label_room = GROUP_LABEL_H if self.lr else 0
        extents = []
        for layer in self.layers:
            positions = []
            pos = 0.0
            prev_group = None
            for i, item in enumerate(layer):
                group = self._group_of(item)
                if i:
                    pos += NODE_GAP
                if group != prev_group:
                    if prev_group is not None:
                        pos += GROUP_PAD
                    if group is not None:
                        pos += GROUP_PAD + label_room
                positions.append(pos)
                pos += self._cross_size(item)
                prev_group = group
            if prev_group is not None:
                pos += GROUP_PAD
            extents.append((positions, pos))
        # rows stack along the cross axis, with a channel between them for the edges that change rows
        channel = [float(ROW_GAP[self.direction])] * len(self.rows)
        for e in self.edges:
            if e.split is not None and e.label:
                row = self.row_of[self.nodes[e.chain[0]].level]
                w, h = self._label_size(e)
                channel[row] = max(channel[row], (h if self.lr else w) + 16)
        offsets, self.channel_mid = [], []
        for k, (first, last) in enumerate(self.rows):
            lo = min(-extents[r][1] / 2 for r in range(first, last + 1))
            hi = max(extents[r][1] / 2 for r in range(first, last + 1))
            offset = 0.0 if not k else self.channel_mid[-1] + channel[k - 1] / 2 - lo
            offsets.append(offset)
            self.channel_mid.append(offset + hi + channel[k] / 2)
        for level, (layer, (positions, total)) in enumerate(zip(self.layers, extents)):
            for item, p in zip(layer, positions):
                self.cross_pos[item] = p - total / 2 + offsets[self.row_of[level]]
        for n in self.nodes.values():
            if self.lr:
                n.y = self.cross_pos[n.id]
            else:
                n.x = self.cross_pos[n.id]

    def _cross_center(self, item) -> float:
        return self.cross_pos[item] + self._cross_size(item) / 2

    def _label_size(self, e: _Edge) -> tuple[float, float]:
        return (_lines_width(e.label, EDGE_PX) + 8, len(e.label) * _line_height(EDGE_PX) + 4)

    def _attach(self, item, back: bool) -> float:
        """Cross-axis point where an edge meets an item; back edges meet nodes a quarter off-centre."""
        centre = self._cross_center(item)
        if back and isinstance(item, str):
            return centre + self._cross_size(item) / 4
        return centre

    def _set_label(self, e: _Edge, main: float, cross: float, gap: tuple) -> None:
        if e.label:
            w, h = self._label_size(e)
            e.label_box = (*self._point(main, cross), w, h)
            e.label_gap = gap

    def _through(self, e: _Edge, items: list, main: float, label_step: int | None) -> tuple[list, float]:
        """Segments along items (consecutive levels of 1 row), starting at `main` on the main axis."""
        segments = []
        start = self._level(items[0])
        for i in range(len(items) - 1):
            a, b = items[i], items[i + 1]
            fs, fe = self.free[start + i]
            ca, cb = self._attach(a, e.back), self._attach(b, e.back)
            if fs > main + 0.01:
                segments.append(("L", self._point(main, ca), self._point(fs, ca)))
            mid = (fs + fe) / 2
            segments.append(("C", self._point(fs, ca), self._point(mid, ca), self._point(mid, cb),
                             self._point(fe, cb)))
            main = fe
            if i == label_step:
                self._set_label(e, mid, (ca + cb) / 2, ("gap", start + i))
            if isinstance(b, str):
                near = self._near(self.nodes[b])
                if near > main + 0.01:
                    segments.append(("L", self._point(main, cb), self._point(near, cb)))
                    main = near
        return segments, main

    def _flat_segments(self, e: _Edge) -> list:
        """An edge between 2 nodes of the same rank: out of the source's far side, a loop through the gap after
        the level, and into the target's far side."""
        src, dst = self.nodes[e.src], self.nodes[e.dst]
        fs, fe = self.free[src.level]
        cs, cd = self._attach(e.src, True), self._attach(e.dst, True)
        mid = (fs + fe) / 2
        segments = []
        if fs > self._far(src) + 0.01:
            segments.append(("L", self._point(self._far(src), cs), self._point(fs, cs)))
        segments.append(("C", self._point(fs, cs), self._point(mid, cs), self._point(mid, cd),
                         self._point(fs, cd)))
        if fs > self._far(dst) + 0.01:
            segments.append(("L", self._point(fs, cd), self._point(self._far(dst), cd)))
        self._set_label(e, mid, (cs + cd) / 2, ("gap", src.level))
        return segments

    def _cross_row_segments(self, e: _Edge, j: int) -> list:
        """An edge from a lower row to a higher one (drawn low to high): through the rest of its row, along the
        row's tail, the channel below the row and the gutter before the rows, and into its target."""
        first, second = e.chain[:e.split], e.chain[e.split:]
        low = self.nodes[first[0]]
        segments, main = self._through(e, first, self._far(low), None)
        offset = (j % 5 - 2) * 4
        row = self.row_of[low.level]
        tail = self.free[self.rows[row][1]][0] + 20 + offset
        gutter = -20 + offset
        channel = self.channel_mid[row] + offset
        c_last, c_first = self._attach(first[-1], e.back), self._attach(second[0], e.back)
        corners = [(main, c_last), (tail, c_last), (tail, channel), (gutter, channel), (gutter, c_first)]
        for (m0, c0), (m1, c1) in zip(corners, corners[1:]):
            if abs(m0 - m1) > 0.01 or abs(c0 - c1) > 0.01:
                segments.append(("L", self._point(m0, c0), self._point(m1, c1)))
        self._set_label(e, (tail + gutter) / 2, channel, ("channel", row))
        if len(second) > 1:
            more, _ = self._through(e, second, gutter, None)
            segments += more
        else:
            near = self._near(self.nodes[second[0]])
            segments.append(("L", self._point(gutter, c_first), self._point(near, c_first)))
        return segments

    def _route_edges(self) -> None:
        """Route every edge along its chain, low rank to high rank, through the free part of each gap.

        A back edge is laid out as if it pointed forward and its path is then reversed, so its arrow still
        ends at its real target (on the target's far side).
        """
        crossing = 0
        for e in self.edges:
            if e.flat:
                segments = self._flat_segments(e)
            elif e.split is not None:
                segments = self._cross_row_segments(e, crossing)
                crossing += 1
            else:
                low = self.nodes[e.chain[0]]
                segments, _ = self._through(e, e.chain, self._far(low), len(e.chain) - 2 if e.back else 0)
            if e.back:
                segments = [(kind, *reversed(points)) for kind, *points in reversed(segments)]
            e.path = [("M", [segments[0][1]])] + [(kind, list(points[1:])) for kind, *points in segments]
        self._spread_labels()

    def _spread_labels(self) -> None:
        """Move labels that share a gap apart along the cross axis, and labels that share a row channel apart
        along the main axis (neither place holds nodes, so this is safe).

        Overlapping labels merge into clusters; each cluster is centred on its labels' wanted positions.
        """
        spacing = 3.0
        by_gap: dict[tuple, list] = {}
        for k, e in enumerate(self.edges):
            if e.label_box:
                cx, cy, w, h = e.label_box
                along_x = self.lr != (e.label_gap[0] == "gap")      # the axis the labels are spread along
                want, size = (cx, w) if along_x else (cy, h)
                by_gap.setdefault(e.label_gap, []).append((want, k, size, e, along_x))
        for items in by_gap.values():
            items.sort(key=lambda t: (t[0], t[1]))
            clusters: list[list] = []          # [start, total size, [(offset of centre, wanted, edge)]]
            for want, _, size, e, _ in items:
                clusters.append([want - size / 2, size, [(size / 2, want, e)]])
                while len(clusters) > 1 and clusters[-2][0] + clusters[-2][1] + spacing > clusters[-1][0]:
                    last = clusters.pop()
                    prev = clusters[-1]
                    shift = prev[1] + spacing
                    members = prev[2] + [(off + shift, w_, e_) for off, w_, e_ in last[2]]
                    prev[1] = shift + last[1]
                    prev[2] = members
                    prev[0] = sum(w_ - off for off, w_, _ in members) / len(members)
            along_x = items[0][4]
            for start, _, members in clusters:
                for off, _, e in members:
                    cx, cy, w, h = e.label_box
                    centre = start + off
                    e.label_box = (centre, cy, w, h) if along_x else (cx, centre, w, h)

    def _place_groups(self) -> None:
        for g in self.groups:
            boxes = [self.nodes[m] for m in g.members]
            x0 = min(n.x for n in boxes) - GROUP_PAD
            y0 = min(n.y for n in boxes) - GROUP_PAD - GROUP_LABEL_H
            x1 = max(n.x + n.w for n in boxes) + GROUP_PAD
            y1 = max(n.y + n.h for n in boxes) + GROUP_PAD
            x1 = max(x1, x0 + _text_width(g.label, GROUP_PX, bold=True) + 16)
            g.rect = (x0, y0, x1, y1)

    # -- canvas
    def content_bounds(self) -> tuple[float, float, float, float]:
        xs, ys = [], []
        for n in self.nodes.values():
            xs += [n.x, n.x + n.w]
            ys += [n.y, n.y + n.h]
        for g in self.groups:
            xs += [g.rect[0], g.rect[2]]
            ys += [g.rect[1], g.rect[3]]
        for e in self.edges:
            for _, points in e.path:
                for x, y in points:
                    xs.append(x)
                    ys.append(y)
            if e.label_box:
                cx, cy, w, h = e.label_box
                xs += [cx - w / 2, cx + w / 2]
                ys += [cy - h / 2, cy + h / 2]
        return min(xs), min(ys), max(xs), max(ys)

    def shift(self, dx: float, dy: float) -> None:
        for n in self.nodes.values():
            n.x, n.y = round(n.x + dx, 2), round(n.y + dy, 2)
        for g in self.groups:
            x0, y0, x1, y1 = g.rect
            g.rect = (x0 + dx, y0 + dy, x1 + dx, y1 + dy)
        for e in self.edges:
            e.path = [(cmd, [(x + dx, y + dy) for x, y in points]) for cmd, points in e.path]
            if e.label_box:
                cx, cy, w, h = e.label_box
                e.label_box = (cx + dx, cy + dy, w, h)


# ====================================================================== SVG
def _legend_actors(nodes: dict, legend) -> list[str]:
    present = {n.actor for n in nodes.values()}
    if legend is False or (legend == "auto" and len(present) < 2):
        return []
    return [a for a in ACTORS if a in present]


def _swatch_colours(actor: str, stage: str) -> tuple[str, str]:
    """(fill, stroke) for an actor's shape."""
    c = _colour(STAGE[stage])
    if actor == "model":
        return tint(c, 0.20), c
    if actor == "external":
        return "#f6f6f6", _colour(GREY)
    return "#ffffff", c


def _record_path(x: float, y: float, w: float, h: float) -> tuple[str, str, float]:
    fold = min(12.0, h * 0.3, w * 0.2)
    outline = (f"M{_fmt(x)},{_fmt(y)} H{_fmt(x + w - fold)} L{_fmt(x + w)},{_fmt(y + fold)} "
               f"V{_fmt(y + h)} H{_fmt(x)} Z")
    corner = f"M{_fmt(x + w - fold)},{_fmt(y)} V{_fmt(y + fold)} H{_fmt(x + w)}"
    return outline, corner, fold


def _shape_svg(actor: str, stage: str, x: float, y: float, w: float, h: float, dashed: bool,
               stroke_width: float = 1.4) -> list[str]:
    fill, stroke = _swatch_colours(actor, stage)
    dash = ' stroke-dasharray="5 3"' if dashed else ""
    common = f'fill="{fill}" stroke="{stroke}" stroke-width="{_fmt(stroke_width)}"{dash}'
    if actor == "record":
        outline, corner, _ = _record_path(x, y, w, h)
        return [f'<path class="shape" d="{outline}" {common}/>',
                f'<path d="{corner}" fill="none" stroke="{stroke}" stroke-width="{_fmt(stroke_width * 0.8)}"/>']
    radius = {"model": 8, "code": 2, "external": 12}[actor]
    radius = min(radius, h / 2)
    return [f'<rect class="shape" x="{_fmt(x)}" y="{_fmt(y)}" width="{_fmt(w)}" height="{_fmt(h)}" '
            f'rx="{_fmt(radius)}" {common}/>']


def _node_svg(n: _Node) -> list[str]:
    out = [f'<g class="node actor-{n.actor} stage-{n.stage}" data-id="{_attr(n.id)}">']
    out += ["  " + s for s in _shape_svg(n.actor, n.stage, n.x, n.y, n.w, n.h, n.dashed)]
    c = _colour(STAGE[n.stage])
    top = n.y + PAD_Y
    if n.tag:
        text = "MODEL" if n.actor == "model" else "CODE"
        tw = _text_width(text, TAG_PX, bold=True) + 8
        fill, ink = (c, "#ffffff") if n.actor == "model" else ("#ffffff", c)
        out.append(f'  <rect class="tag-bg" x="{_fmt(n.x + 6)}" y="{_fmt(n.y + 5)}" width="{_fmt(tw)}" '
                   f'height="12" rx="2" fill="{fill}" stroke="{c}" stroke-width="0.8"/>')
        out.append(f'  <text class="tag" x="{_fmt(n.x + 6 + tw / 2)}" y="{_fmt(n.y + 14.2)}" '
                   f'text-anchor="middle" font-size="{TAG_PX}" font-weight="bold" fill="{ink}">{text}</text>')
        top += TAG_ROW
    label_lh, sub_lh = _line_height(LABEL_PX), _line_height(SUB_PX)
    block = len(n.label) * label_lh + len(n.sub) * sub_lh + (2 if n.sub else 0)
    avail = n.y + n.h - PAD_Y - top
    line_top = top + (avail - block) / 2
    cx = n.x + (n.w - (8 if n.actor == "record" else 0)) / 2
    for line in n.label:
        base = line_top + label_lh / 2 + LABEL_PX * 0.35
        out.append(f'  <text class="label" x="{_fmt(cx)}" y="{_fmt(base)}" text-anchor="middle" '
                   f'font-size="{LABEL_PX}" font-weight="bold" fill="{_colour(INK)}">{_esc(line)}</text>')
        line_top += label_lh
    if n.sub:
        line_top += 2
    for line in n.sub:
        base = line_top + sub_lh / 2 + SUB_PX * 0.35
        out.append(f'  <text class="sub" x="{_fmt(cx)}" y="{_fmt(base)}" text-anchor="middle" '
                   f'font-size="{SUB_PX}" fill="{_colour(GREY)}">{_esc(line)}</text>')
        line_top += sub_lh
    out.append("</g>")
    return out


def _path_d(path: list) -> str:
    parts = []
    for cmd, points in path:
        parts.append(cmd + " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in points))
    return " ".join(parts)


def _edge_svg(e: _Edge) -> list[str]:
    colour = _colour(GREY) if e.dashed else _colour(INK)
    dash = ' stroke-dasharray="5 3"' if e.dashed else ""
    marker = "tk-arrow-dashed" if e.dashed else "tk-arrow"
    out = [f'<g class="edge" data-from="{_attr(e.src)}" data-to="{_attr(e.dst)}">',
           f'  <path d="{_path_d(e.path)}" fill="none" stroke="{colour}" stroke-width="1.3"{dash} '
           f'marker-end="url(#{marker})"/>']
    if e.label_box:
        cx, cy, w, h = e.label_box
        out.append(f'  <rect class="edge-label-bg" x="{_fmt(cx - w / 2)}" y="{_fmt(cy - h / 2)}" '
                   f'width="{_fmt(w)}" height="{_fmt(h)}" fill="#ffffff" fill-opacity="0.9"/>')
        lh = _line_height(EDGE_PX)
        top = cy - h / 2 + 2
        for line in e.label:
            out.append(f'  <text class="edge-label" x="{_fmt(cx)}" y="{_fmt(top + lh / 2 + EDGE_PX * 0.35)}" '
                       f'text-anchor="middle" font-size="{EDGE_PX}" font-style="italic" '
                       f'fill="{_colour(GREY)}">{_esc(line)}</text>')
            top += lh
    out.append("</g>")
    return out


def _group_svg(g: _Group) -> list[str]:
    colour = _colour(STAGE[g.stage]) if g.stage else _colour(HAIR)
    fill = tint(colour, 0.06) if g.stage else "none"
    x0, y0, x1, y1 = g.rect
    return [f'<g class="group" data-id="{_attr(g.id)}">',
            f'  <rect x="{_fmt(x0)}" y="{_fmt(y0)}" width="{_fmt(x1 - x0)}" height="{_fmt(y1 - y0)}" rx="6" '
            f'fill="{fill}" stroke="{colour}" stroke-width="1.1" stroke-dasharray="6 4"/>',
            f'  <text class="group-label" x="{_fmt(x0 + 8)}" y="{_fmt(y0 + 14)}" font-size="{GROUP_PX}" '
            f'font-weight="bold" fill="{colour if g.stage else _colour(GREY)}">{_esc(g.label)}</text>',
            "</g>"]


def _legend_entries(nodes: dict, actors: list[str]) -> tuple[list[tuple], float]:
    """[(kind, actor or text, x offset, width)], total width."""
    entries, x = [], 0.0
    for actor in actors:
        text = LEGEND_TEXT[actor]
        w = 22 + 6 + _text_width(text, LEGEND_PX)
        entries.append(("actor", actor, x, w))
        x += w + 18
    if "model" in actors:
        w = _text_width(SESSION_TEXT, LEGEND_PX)
        entries.append(("note", SESSION_TEXT, x, w))
        x += w + 18
    return entries, max(0.0, x - 18)


def _legend_svg(nodes: dict, entries: list[tuple], left: float, top: float) -> list[str]:
    stage_of = {}
    for n in nodes.values():
        stage_of.setdefault(n.actor, n.stage)
    out = ['<g class="legend">']
    for kind, value, dx, _ in entries:
        x = left + dx
        if kind == "actor":
            out += ["  " + s for s in _shape_svg(value, stage_of[value], x, top + 2, 22, 14, False, 1.0)]
            out.append(f'  <text x="{_fmt(x + 28)}" y="{_fmt(top + 13)}" font-size="{LEGEND_PX}" '
                       f'fill="{_colour(GREY)}">{_esc(LEGEND_TEXT[value])}</text>')
        else:
            out.append(f'  <text x="{_fmt(x)}" y="{_fmt(top + 13)}" font-size="{LEGEND_PX}" font-style="italic" '
                       f'fill="{_colour(GREY)}">{_esc(value)}</text>')
    out.append("</g>")
    return out


LEGEND_H = 18


def render_svg(spec: dict) -> tuple[str, int, int, dict]:
    """Lay out and draw a valid spec. Returns (svg text, width, height, {id: geometry})."""
    lay = _Layout(spec)
    title = " ".join(_split(spec.get("title") or ""))
    note = spec.get("note") or ""
    note_lines = _split(note) if note else []
    actors = _legend_actors(lay.nodes, spec.get("legend", "auto"))
    entries, legend_w = _legend_entries(lay.nodes, actors)

    x0, y0, x1, y1 = lay.content_bounds()
    content_w, content_h = x1 - x0, y1 - y0
    title_h = TITLE_PX * 1.3 + 10 if title else 0
    inner_w = max(content_w, _text_width(title, TITLE_PX, bold=True), legend_w,
                  _lines_width(note_lines, NOTE_PX))
    lay.shift(MARGIN + (inner_w - content_w) / 2 - x0, MARGIN + title_h - y0)
    bottom = MARGIN + title_h + content_h
    legend_top = bottom + 16 if entries else None
    if entries:
        bottom = legend_top + LEGEND_H
    note_top = bottom + 10 if note_lines else None
    if note_lines:
        bottom = note_top + len(note_lines) * _line_height(NOTE_PX)
    width = math.ceil(inner_w + 2 * MARGIN)
    height = math.ceil(bottom + MARGIN)

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" font-family="{FONT}">']
    if title:
        svg.append(f"<title>{_esc(title)}</title>")
    svg.append("<defs>")
    for marker_id, colour in (("tk-arrow", INK), ("tk-arrow-dashed", GREY)):
        svg.append(f'  <marker id="{marker_id}" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="9" '
                   f'markerHeight="9" markerUnits="userSpaceOnUse" orient="auto">'
                   f'<path d="M0,0 L10,5 L0,10 z" fill="{_colour(colour)}"/></marker>')
    svg.append("</defs>")
    svg.append(f'<rect class="background" x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>')
    if title:
        svg.append(f'<text class="title" x="{MARGIN}" y="{_fmt(MARGIN + TITLE_PX)}" font-size="{TITLE_PX}" '
                   f'font-weight="bold" fill="{_colour(INK)}">{_esc(title)}</text>')
    for g in lay.groups:
        svg += _group_svg(g)
    for e in lay.edges:
        svg += _edge_svg(e)
    for nid in lay.order:
        svg += _node_svg(lay.nodes[nid])
    if entries:
        svg += _legend_svg(lay.nodes, entries, MARGIN, legend_top)
    if note_lines:
        lh = _line_height(NOTE_PX)
        first = note_top + lh / 2 + NOTE_PX * 0.35
        spans = "".join(f'<tspan x="{MARGIN}" dy="{0 if i == 0 else _fmt(lh)}">{_esc(line)}</tspan>'
                        for i, line in enumerate(note_lines))
        svg.append(f'<text class="note" x="{MARGIN}" y="{_fmt(first)}" font-size="{NOTE_PX}" '
                   f'font-style="italic" fill="{_colour(GREY)}">{spans}</text>')
    svg.append("</svg>")

    geometry = {nid: {"x": _num(n.x), "y": _num(n.y), "w": _num(n.w), "h": _num(n.h), "rank": n.rank}
                for nid, n in lay.nodes.items()}
    return "\n".join(svg) + "\n", width, height, geometry


# ====================================================================== PNG
_INKSCAPE_PATHS = ("C:/Program Files/Inkscape/bin/inkscape.exe", "C:/Program Files (x86)/Inkscape/bin/inkscape.exe",
                   "/Applications/Inkscape.app/Contents/MacOS/inkscape")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _png_converters():
    """Yield (name, convert(svg_file, png_file)) for each available converter, in preference order."""
    try:
        cairosvg = importlib.import_module("cairosvg")
    except Exception:            # missing, or installed without the cairo library
        cairosvg = None
    if cairosvg is not None:
        yield "cairosvg", lambda src, dst: cairosvg.svg2png(url=str(src), write_to=str(dst))
    rsvg = shutil.which("rsvg-convert")
    if rsvg:
        yield "rsvg-convert", lambda src, dst: _run([rsvg, "-o", str(dst), str(src)])
    inkscape = shutil.which("inkscape") or next((p for p in _INKSCAPE_PATHS if os.path.isfile(p)), None)
    if inkscape:
        yield "inkscape", lambda src, dst: _run([inkscape, str(src), "--export-type=png",
                                                 f"--export-filename={dst}"])
    pymupdf = _load_pymupdf()
    if pymupdf is not None:
        yield "pymupdf", lambda src, dst: _pymupdf_png(pymupdf, src, dst)


def _load_pymupdf():
    """pymupdf (or its old name fitz), imported only when needed, with MuPDF messages sent to stderr."""
    for name in ("pymupdf", "fitz"):
        try:
            mod = importlib.import_module(name)
        except Exception:        # missing, hidden (sys.modules[name] = None) or broken
            continue
        if not hasattr(mod, "open"):
            continue
        try:
            mod.set_messages(fd=2)
        except Exception:        # older releases lack set_messages or its fd argument
            pass
        return mod
    return None


PYMUPDF_SCALE = 2                # pixels per SVG unit, for a sharp PNG


def _pymupdf_png(pymupdf, src: pathlib.Path, dst: pathlib.Path) -> None:
    doc = pymupdf.open(stream=src.read_bytes(), filetype="svg")
    try:
        page = doc[0]
        pix = page.get_pixmap(matrix=pymupdf.Matrix(PYMUPDF_SCALE, PYMUPDF_SCALE), alpha=False)
        pix.save(str(dst))
    finally:
        doc.close()


def _run(argv: list[str]) -> None:
    cp = subprocess.run(argv, capture_output=True, text=True, timeout=180)
    if cp.returncode != 0:
        raise RuntimeError((cp.stderr or cp.stdout or f"exit code {cp.returncode}").strip()[:300])


def _write_png(svg: str, png_path: str) -> None:
    """Convert with the first converter that works. The target is replaced only by a complete PNG."""
    target = pathlib.Path(png_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    failures = []
    with tempfile.TemporaryDirectory(prefix="tundlekit-png-") as tmp:
        src = pathlib.Path(tmp) / "diagram.svg"
        src.write_text(svg, encoding="utf-8")
        for name, convert in _png_converters():
            dst = pathlib.Path(tmp) / f"out-{name}.png"
            try:
                convert(src, dst)
                if dst.is_file() and dst.read_bytes()[:8] == PNG_MAGIC:
                    shutil.move(str(dst), str(target))
                    return
                failures.append(f"{name}: produced no PNG")
            except Exception as e:     # a broken converter: try the next one
                failures.append(f"{name}: {e}")
    if not failures:
        raise ToolError("no SVG to PNG converter found: install the Python package cairosvg "
                        "(pip install cairosvg), rsvg-convert (librsvg), Inkscape, or pymupdf "
                        "(pip install pymupdf)")
    raise ToolError("SVG to PNG conversion failed: " + "; ".join(failures))


# ====================================================================== tools
_SOURCE_PROPS = {
    "spec": {"type": "object", "description": "The diagram spec (MANIFEST §4.1) as a JSON object."},
    "spec_path": {"type": "string", "description": "Path to a JSON file holding the spec."},
    "mermaid": {"type": "string", "description": "Mermaid flowchart text (the §4.4 subset)."},
    "mermaid_path": {"type": "string", "description": "Path to a Mermaid flowchart file."},
}
_SPEC_HELP = (
    "Spec: {title?, direction?: LR|TB, nodes: [{id, label, sub?, stage?, actor?: model|code|record|external, "
    "dashed?, rank?: int>=0 (fixed)}], edges?: [{from, to, label?, dashed?}], groups?: [{id, label?, nodes: "
    "[ids], stage?}], legend?: auto|true|false, tags?: bool, note?, wrap?: int>=1 (ranks per row/column)}. "
    "stage is a palette stage (default dispatch); label lines split on \\n."
)


@tool("diagram_render",
      "Draw a pipeline/architecture diagram as SVG (and optionally PNG) with tundle's drawing rules: colour = "
      "stage, style = actor (model call = tinted box with a MODEL tag, code = white box with a CODE tag, record "
      "= document shape, external = grey), 1 box per model call, automatic legend when more than 1 actor is "
      "shown. Give exactly 1 of spec, spec_path, mermaid or mermaid_path. Layout is automatic, layered by "
      "rank and deterministic. " + _SPEC_HELP + " Returns {svg (when out is absent), path, png, width, "
      "height, nodes: {id: {x, y, w, h, rank}}, warnings}. PNG needs cairosvg, rsvg-convert, Inkscape or "
      "pymupdf (tried in that order).",
      {"type": "object",
       "properties": dict(_SOURCE_PROPS,
                          out={"type": "string", "description": "Write the SVG to this path."},
                          png={"type": "string", "description": "Also write a PNG to this path."}),
       "additionalProperties": False},
      readOnlyHint=False, destructiveHint=False, idempotentHint=True)
def diagram_render(spec: dict | None = None, spec_path: str | None = None, mermaid: str | None = None,
                   mermaid_path: str | None = None, out: str | None = None, png: str | None = None) -> dict:
    spec, warnings = _load_source(spec, spec_path, mermaid, mermaid_path)
    warnings = [w for w in warnings if not w.startswith("the imported spec is not valid")]
    warnings += _require_valid(spec)
    svg, width, height, geometry = render_svg(spec)
    if out is not None:
        target = pathlib.Path(out)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(svg, encoding="utf-8", newline="\n")
        except OSError as e:
            raise ToolError(f"cannot write {out}: {e}") from None
    if png is not None:
        _write_png(svg, png)
    return {"svg": svg if out is None else None, "path": out, "png": png, "width": width, "height": height,
            "nodes": geometry, "warnings": warnings}


@tool("diagram_validate",
      "Check a diagram spec (or Mermaid flowchart) without drawing it. Give exactly 1 of spec, spec_path, "
      "mermaid or mermaid_path. Returns {ok, problems: [str], warnings: [str]}; each problem starts with a "
      "JSON path such as nodes[2].stage. Spec problems never raise. " + _SPEC_HELP,
      {"type": "object", "properties": dict(_SOURCE_PROPS), "additionalProperties": False},
      readOnlyHint=True)
def diagram_validate(spec: dict | None = None, spec_path: str | None = None, mermaid: str | None = None,
                     mermaid_path: str | None = None) -> dict:
    try:
        spec, warnings = _load_source(spec, spec_path, mermaid, mermaid_path)
    except _InputError as e:
        return {"ok": False, "problems": [str(e)], "warnings": []}
    warnings = [w for w in warnings if not w.startswith("the imported spec is not valid")]
    problems, spec_warnings = check_spec(spec)
    return {"ok": not problems, "problems": problems, "warnings": warnings + spec_warnings}


@tool("diagram_from_mermaid",
      "Convert a Mermaid flowchart (subset) to a diagram spec. Give mermaid (text) or mermaid_path. Accepted: "
      "'flowchart|graph LR|RL|TB|TD|BT'; shapes id[code], id(model), id>record], id[(record)], "
      "id{{external}}; ':::stage' suffixes; edges -->, ---, ==>, -.->, -.- with |label| or '-- label -->'; "
      "chains and '&'; 'subgraph id [label]' ... 'end' as groups; %% comments. classDef/class/style/"
      "linkStyle/click lines are ignored with a warning; anything else is an error naming the line. "
      "Returns {spec, warnings}.",
      {"type": "object",
       "properties": {"mermaid": _SOURCE_PROPS["mermaid"], "mermaid_path": _SOURCE_PROPS["mermaid_path"]},
       "additionalProperties": False},
      readOnlyHint=True)
def diagram_from_mermaid(mermaid: str | None = None, mermaid_path: str | None = None) -> dict:
    if (mermaid is None) == (mermaid_path is None):
        raise ToolError("give exactly 1 of mermaid or mermaid_path")
    spec, warnings = _load_source(mermaid=mermaid, mermaid_path=mermaid_path)
    return {"spec": spec, "warnings": warnings}


@tool("diagram_to_mermaid",
      "Convert a diagram spec to Mermaid flowchart text: 'flowchart LR|TB', 1 line per node with its shape "
      "(actor) and ':::stage', subgraphs for groups, '-->' or '-.->' (dashed) edges with |label|. "
      "diagram_from_mermaid reads it back to the same nodes, edges, groups and direction; a node's sub is "
      "folded into its label as another line. Give spec or spec_path. Returns {mermaid}.",
      {"type": "object",
       "properties": {"spec": _SOURCE_PROPS["spec"], "spec_path": _SOURCE_PROPS["spec_path"]},
       "additionalProperties": False},
      readOnlyHint=True)
def diagram_to_mermaid(spec: dict | None = None, spec_path: str | None = None) -> dict:
    if (spec is None) == (spec_path is None):
        raise ToolError("give exactly 1 of spec or spec_path")
    spec, _ = _load_source(spec=spec, spec_path=spec_path)
    _require_valid(spec)
    return {"mermaid": spec_to_mermaid(spec)}


# ====================================================================== CLI
_MERMAID_SUFFIXES = (".mmd", ".mermaid")


def _source_args(path: str) -> dict:
    """A CLI input file is a Mermaid file by suffix (.mmd, .mermaid) or content; otherwise a JSON spec."""
    suffix = pathlib.Path(path).suffix.lower()
    if suffix in _MERMAID_SUFFIXES:
        return {"mermaid_path": path}
    if suffix != ".json":
        try:
            head = pathlib.Path(path).read_text(encoding="utf-8-sig").lstrip()
        except (OSError, UnicodeDecodeError):
            head = "{"
        if head and not head.startswith("{"):
            return {"mermaid_path": path}
    return {"spec_path": path}


def _print_warnings(args, warnings: list[str]) -> None:
    if not args.json:
        for w in warnings:
            print(f"warning: {w}", file=sys.stderr)


def add_cli(groups) -> None:
    from tundlekit.cli_support import common_flags

    p = groups.add_parser("diagram", help="SVG diagrams from a JSON spec or a Mermaid flowchart")
    cmds = p.add_subparsers(dest="command", required=True)

    c = cmds.add_parser("render", help="draw a diagram as SVG (and PNG)")
    c.add_argument("source", help="SPEC.json, or a Mermaid file (.mmd)")
    c.add_argument("-o", "--out", help="write the SVG here (default: print it)")
    c.add_argument("--png", help="also write a PNG here")
    common_flags(c)
    c.set_defaults(handler=_cli_render)

    c = cmds.add_parser("validate", help="check a spec without drawing it")
    c.add_argument("source", help="SPEC.json, or a Mermaid file (.mmd)")
    common_flags(c)
    c.set_defaults(handler=_cli_validate)

    c = cmds.add_parser("from-mermaid", help="convert a Mermaid flowchart to a spec")
    c.add_argument("mermaid_path", help="FILE.mmd")
    common_flags(c)
    c.set_defaults(handler=_cli_from_mermaid)

    c = cmds.add_parser("to-mermaid", help="convert a spec to a Mermaid flowchart")
    c.add_argument("spec_path", help="SPEC.json")
    common_flags(c)
    c.set_defaults(handler=_cli_to_mermaid)


def _cli_render(args):
    from tundlekit.cli_support import CliResult

    res = diagram_render(**_source_args(args.source), out=args.out, png=args.png)
    _print_warnings(args, res["warnings"])
    if args.out is None and args.png is None:
        return CliResult(res, text=res["svg"])
    lines = []
    if res["path"]:
        lines.append(f"wrote {res['path']} ({res['width']}x{res['height']})")
    elif res["svg"]:
        lines.append(res["svg"])
    if res["png"]:
        lines.append(f"wrote {res['png']}")
    return CliResult(res, text="\n".join(lines))


def _cli_validate(args):
    from tundlekit.cli_support import CliResult

    res = diagram_validate(**_source_args(args.source))
    _print_warnings(args, res["warnings"])
    text = "ok" if res["ok"] else "\n".join(["invalid:"] + [f"  {p}" for p in res["problems"]])
    return CliResult(res, text=text)


def _cli_from_mermaid(args):
    from tundlekit.cli_support import CliResult

    res = diagram_from_mermaid(mermaid_path=args.mermaid_path)
    _print_warnings(args, res["warnings"])
    return CliResult(res, text=json.dumps(res["spec"], indent=2, ensure_ascii=False))


def _cli_to_mermaid(args):
    from tundlekit.cli_support import CliResult

    res = diagram_to_mermaid(spec_path=args.spec_path)
    return CliResult(res, text=res["mermaid"])
