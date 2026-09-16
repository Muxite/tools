"""MANIFEST §4.1 (spec validation), §4.2 (argument exclusivity), §4.3 (diagram_validate)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers_diagram_text import diagram, tool_error  # noqa: E402


def problems_for(spec):
    res = diagram("diagram_validate", spec=spec)
    assert set(res) >= {"ok", "problems"}
    return res


def has_prefix(problems, prefix):
    return any(p.startswith(prefix) for p in problems)


# §4.3 a valid spec gives ok true and no problems
def test_valid_minimal_spec_is_ok():
    res = problems_for({"nodes": [{"id": "a", "label": "A"}]})
    assert res == {"ok": True, "problems": []} or (res["ok"] is True and res["problems"] == [])


# §4.1 the manifest's example spec is valid
def test_manifest_example_spec_is_valid():
    spec = {"title": "Capsule build path", "direction": "LR",
            "nodes": [{"id": "decide", "label": "build decision", "sub": "reads gap records",
                       "stage": "build", "actor": "model"},
                      {"id": "gate", "label": "admission gate", "stage": "gates", "actor": "code",
                       "dashed": False},
                      {"id": "lib", "label": "library\nappend-only · versioned", "stage": "library",
                       "actor": "record"}],
            "edges": [{"from": "decide", "to": "gate", "label": "manifest", "dashed": False}],
            "groups": [{"id": "cold", "label": "cold path", "nodes": ["decide", "gate"], "stage": "build"}],
            "legend": "auto", "tags": True, "note": "(illustrative)"}
    res = problems_for(spec)
    assert res["ok"] is True, res["problems"]


# §4.1 id pattern ^[A-Za-z_][A-Za-z0-9_-]*$
@pytest.mark.parametrize("bad_id", ["1abc", "has space", "dot.id", ""])
def test_bad_node_id_is_a_problem(bad_id):
    res = problems_for({"nodes": [{"id": "ok_1", "label": "x"}, {"id": bad_id, "label": "y"}]})
    assert res["ok"] is False
    assert has_prefix(res["problems"], "nodes[1]"), res["problems"]


# §4.1 id pattern accepts underscores and hyphens
def test_id_with_underscore_and_hyphen_is_valid():
    res = problems_for({"nodes": [{"id": "_a-b_9", "label": "x"}]})
    assert res["ok"] is True, res["problems"]


# §4.1 ids are unique across nodes
def test_duplicate_node_id_is_a_problem():
    res = problems_for({"nodes": [{"id": "a", "label": "x"}, {"id": "a", "label": "y"}]})
    assert res["ok"] is False
    assert has_prefix(res["problems"], "nodes[1]"), res["problems"]


# §4.1 label is a non-empty string
def test_empty_label_is_a_problem():
    res = problems_for({"nodes": [{"id": "a", "label": ""}]})
    assert res["ok"] is False
    assert has_prefix(res["problems"], "nodes[0].label"), res["problems"]


# §4.1 stage must be a palette.STAGE key (prefix example nodes[2].stage)
def test_unknown_stage_is_a_problem_with_path_prefix():
    res = problems_for({"nodes": [{"id": "a", "label": "x"}, {"id": "b", "label": "y"},
                                  {"id": "c", "label": "z", "stage": "nonsense"}]})
    assert res["ok"] is False
    assert has_prefix(res["problems"], "nodes[2].stage"), res["problems"]


# §4.1 actor ∈ model | code | record | external
def test_unknown_actor_is_a_problem():
    res = problems_for({"nodes": [{"id": "a", "label": "x", "actor": "human"}]})
    assert res["ok"] is False
    assert has_prefix(res["problems"], "nodes[0].actor"), res["problems"]


# §4.1 direction ∈ LR | TB
def test_bad_direction_is_a_problem():
    res = problems_for({"direction": "RL", "nodes": [{"id": "a", "label": "x"}]})
    assert res["ok"] is False
    assert any("direction" in p for p in res["problems"])


# §4.1 legend ∈ auto | true | false
@pytest.mark.parametrize("legend", ["auto", True, False])
def test_legend_values_accepted(legend):
    res = problems_for({"legend": legend, "nodes": [{"id": "a", "label": "x"}]})
    assert res["ok"] is True, res["problems"]


def test_bad_legend_is_a_problem():
    res = problems_for({"legend": "sometimes", "nodes": [{"id": "a", "label": "x"}]})
    assert res["ok"] is False
    assert any("legend" in p for p in res["problems"])


# §4.1 edges reference existing node ids
def test_edge_to_unknown_node_is_a_problem():
    res = problems_for({"nodes": [{"id": "a", "label": "x"}], "edges": [{"from": "a", "to": "ghost"}]})
    assert res["ok"] is False
    assert has_prefix(res["problems"], "edges[0]"), res["problems"]


# §4.1 self-loops are a problem
def test_self_loop_is_a_problem():
    res = problems_for({"nodes": [{"id": "a", "label": "x"}, {"id": "b", "label": "y"}],
                        "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "b"}]})
    assert res["ok"] is False
    assert has_prefix(res["problems"], "edges[1]"), res["problems"]


# §4.1 duplicate edges are allowed
def test_duplicate_edges_are_allowed():
    res = problems_for({"nodes": [{"id": "a", "label": "x"}, {"id": "b", "label": "y"}],
                        "edges": [{"from": "a", "to": "b"}, {"from": "a", "to": "b"}]})
    assert res["ok"] is True, res["problems"]


# §4.1 groups reference existing node ids
def test_group_with_unknown_member_is_a_problem():
    res = problems_for({"nodes": [{"id": "a", "label": "x"}],
                        "groups": [{"id": "g", "label": "G", "nodes": ["a", "nope"]}]})
    assert res["ok"] is False
    assert has_prefix(res["problems"], "groups[0]"), res["problems"]


# §4.1 a node may belong to at most 1 group
def test_node_in_two_groups_is_a_problem():
    res = problems_for({"nodes": [{"id": "a", "label": "x"}, {"id": "b", "label": "y"}],
                        "groups": [{"id": "g1", "label": "G1", "nodes": ["a"]},
                                   {"id": "g2", "label": "G2", "nodes": ["a", "b"]}]})
    assert res["ok"] is False
    assert any(p.startswith("groups[") for p in res["problems"]), res["problems"]


# §4.1 validation collects every problem into 1 ToolError with JSON-path prefixes
def test_render_raises_one_toolerror_listing_every_problem():
    spec = {"nodes": [{"id": "a", "label": "x", "stage": "nope"},
                      {"id": "b", "label": "y", "actor": "robot"}],
            "edges": [{"from": "a", "to": "zzz"}]}
    res = problems_for(spec)
    assert len(res["problems"]) >= 3
    with pytest.raises(tool_error()) as exc:
        diagram("diagram_render", spec=spec)
    msg = str(exc.value)
    for prefix in ("nodes[0].stage", "nodes[1].actor", "edges[0]"):
        assert prefix in msg


# §4.2 exactly 1 of spec | spec_path | mermaid | mermaid_path
def test_render_without_any_source_is_toolerror():
    with pytest.raises(tool_error()):
        diagram("diagram_render")


def test_render_with_two_sources_is_toolerror():
    with pytest.raises(tool_error()):
        diagram("diagram_render", spec={"nodes": [{"id": "a", "label": "x"}]},
                mermaid="flowchart LR\n  a --> b\n")


# §4.3 spec_path is accepted
def test_validate_accepts_spec_path(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"nodes": [{"id": "a", "label": "x", "stage": "bogus"}]}), encoding="utf-8")
    res = diagram("diagram_validate", spec_path=str(p))
    assert res["ok"] is False
    assert has_prefix(res["problems"], "nodes[0].stage")


# §4.3 also accepts mermaid
def test_validate_accepts_mermaid():
    res = diagram("diagram_validate", mermaid="flowchart LR\n  a[Alpha] --> b(Beta)\n")
    assert res["ok"] is True, res["problems"]
