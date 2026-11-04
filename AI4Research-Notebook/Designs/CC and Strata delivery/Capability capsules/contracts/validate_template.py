"""Offline design checks. Run with Python, jsonschema 4.x and referencing installed."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_bytes())


registry = Registry()
for schema_path in (ROOT / "m2a").glob("*.schema.json"):
    native = read(schema_path)
    Draft202012Validator.check_schema(native)
    registry = registry.with_resource(native["$id"], Resource.from_contents(native))
template_schema = read(ROOT / "cc-template.schema.json")
Draft202012Validator.check_schema(template_schema)
validator = Draft202012Validator(template_schema, registry=registry)
fixture = read(ROOT / "strata-template.example.json")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def index(items, key):
    result = {row[key]: row for row in items}
    require(len(result) == len(items), f"Duplicate {key}")
    return result


def check(template):
    validator.validate(template)
    package = template["package"]
    caps = index(template["capabilities"], "id")
    images = index(template["images"], "role")
    bindings = index(template["bindings"], "capability")
    require(set(package["members"]) == caps.keys() == bindings.keys(), "Member coverage differs")
    primary = package["execution"]
    require(any((row.get("image"), row["platform"]) == (primary["image"], primary["platform"])
                for row in images.values()), "Primary M2a carrier missing")
    for name, cap in caps.items():
        require(cap["package_id"] == package["id"], "Capability has wrong package")
        require(set(cap["effects"]) <= set(package["effect_ceiling"]), "Effect exceeds package ceiling")
        require(set(cap["required_providers"]) <= set(package["required_providers"]), "Provider missing")
        require(bindings[name]["image_role"] in images, "Unknown image role")
    for row in images.values():
        output = row.get("factory_output")
        if output:
            cap = caps.get(output["capability"])
            require(cap and output["port"] in {p["name"] for p in cap["outputs"]},
                    "Factory image output has no producing port")
            producer_image = images[bindings[cap["id"]]["image_role"]]
            require("image" in producer_image, "Factory image producer needs a pinned bootstrap image")
    if template["kind"] == "capability-bundle":
        return
    exp = template["experiment"]
    index(exp["gates"], "metric")
    index(exp["model"]["shards"], "file")
    index(exp["changes"], "output_artifact")
    for role in ("baseline_image_role", "candidate_image_role"):
        require(exp[role] in images, f"Unknown {role}")
    require(exp["benchmark_capability"] in caps, "Missing benchmark operation")
    for change in exp["changes"]:
        require(change["transform_capability"] in caps, "Missing transformation operation")
        require(change["input_pack"] == exp["model"]["pack"], "Unknown source pack")
        # The pilot only resolves bundled parameter contracts. Network fetches are outside this checker.
        path = (ROOT / change["contract"]["uri"]).resolve()
        require(path.is_relative_to(ROOT) and path.is_file(), "Parameter schema unavailable")
        require(sha256(path.read_bytes()).hexdigest() == change["contract"]["sha256"], "Parameter schema hash mismatch")
        params_schema = read(path)
        Draft202012Validator.check_schema(params_schema)
        Draft202012Validator(params_schema, registry=registry).validate(change["parameters"])


def negative(label, path, new_value):
    candidate = deepcopy(fixture)
    node = candidate
    for segment in path[:-1]:
        node = node[segment]
    node[path[-1]] = new_value
    try:
        check(candidate)
    except (ValidationError, ValueError):
        return
    raise AssertionError(f"Unexpected acceptance: {label}")


if __name__ == "__main__":
    check(fixture)
    bundle = deepcopy(fixture)
    bundle["kind"] = "capability-bundle"
    del bundle["experiment"]
    check(bundle)
    cases = [
        ("tagged image", ["images", 0, "image"], "example.invalid/carrier:latest"),
        ("nonexistent producer port", ["images", 3, "factory_output", "port"], "missing"),
        ("image selector ambiguous", ["images", 3, "image"], fixture["images"][0]["image"]),
        ("unbound operation", ["bindings", 0, "image_role"], "missing"),
        ("lost M2a member", ["package", "members"], ["strata.measure"]),
        ("foreign capsule", ["capabilities", 0, "package_id"], "cc.other"),
        ("excess effect", ["capabilities", 0, "effects"], ["host.write"]),
        ("untracked dispatch state", ["attempt"], 4),
        ("untracked snapshot", ["snapshot_id"], "checkpoint-2"),
        ("unknown model revision", ["experiment", "model", "revision"], "latest"),
        ("wrong parameter type", ["experiment", "changes", 0, "parameters", "rank"], "32"),
        ("unbounded rank", ["experiment", "changes", 0, "parameters", "rank"], 9999),
        ("changed parameter contract", ["experiment", "changes", 0, "contract", "sha256"], "0"*64),
        ("unsupported target", ["experiment", "changes", 0, "target", "projections"], ["router"]),
        ("zero time", ["experiment", "limits", "wall_seconds"], 0),
        ("missing evidence silently passes", ["experiment", "on_missing_evidence"], "pass"),
        ("runtime outcomes in declaration", ["verdict"], "pass"),
    ]
    for case in cases:
        negative(*case)
    print(f"PASS: 2 valid profiles and {len(cases)} rejecting cases. Design checks only.")

