"""Read one Qwen expert projection from a native v3/v4 pack layout; use Strata's GGUF reader for its header."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


ROLES = ("gate", "up", "down")
FIXTURE = "tests/data/native_experts/iq3_s.txt"


def load_reader(strata):
    # The supplied source tree must be trusted. Its Python parser runs in this process.
    spec = importlib.util.spec_from_file_location("strata_gguf_reader", strata / "tools/gguf_reader.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def inspect_layout(path, layer, expert, projection):
    raw = path.read_bytes()
    header, *lines = raw.decode("utf-8").splitlines()
    match = re.search(r"^# strata native experts v([34]):.*?\(n_expert (\d+), total (\d+); absolute offsets in ([^,;)]+)", header)
    if not match:
        raise ValueError("expected a Strata native v3/v4 layout with GGUF projection offsets")
    version, count, total = map(int, match.groups()[:3])
    if not 0 <= expert < count:
        raise ValueError("expert index is outside the declared expert count")
    cursor = 0
    rows = []
    for line in lines:
        if not line.strip() or line.startswith("#"):
            continue
        fields = line.split()
        if len(fields) not in (8, 9):
            raise ValueError("missing or unsupported native layout fields")
        index, gu_type, down_type, offset, blob, *starts = map(int, fields[:8])
        if index != len(rows) or offset != cursor or blob <= 0 or min(starts) < 0:
            raise ValueError("noncontiguous layers or invalid native layout byte range")
        files = fields[8].split(",") if len(fields) == 9 else [match[4]]
        if len(files) == 1:
            files *= 3
        if len(files) != 3:
            raise ValueError("invalid per-role shard list")
        rows.append((offset, blob, [gu_type, gu_type, down_type], starts, files))
        cursor += count * blob
    if cursor != total or not 0 <= layer < len(rows):
        raise ValueError("invalid layout total or layer index")
    role = ROLES.index(projection)
    offset, blob, types, starts, files = rows[layer]
    return {
        "layoutSha256": hashlib.sha256(raw).hexdigest(), "nativeVersion": version,
        "layers": len(rows), "expertsPerLayer": count, "expertSlots": count * len(rows),
        "logicalExpertBytes": total, "layer": layer, "expert": expert, "projection": projection,
        "nativeTensorName": f"blk.{layer}.ffn_{projection}_exps.weight",
        "nativeQuantTypeId": types[role], "shard": files[role],
        "roleTensorStartInShard": starts[role], "wholeExpertBytes": blob,
        "wholeExpertOffsetInOptionalExpertsBin": offset + expert * blob,
        "projectionEvidence": "layout only; per-expert projection byte span requires a matching tensor header",
    }


def inspect_shard(reader, path, layout):
    gguf = reader.GGUFFile(path)
    matches = [t for t in gguf.tensors if t.name == layout["nativeTensorName"]]
    if len(matches) != 1:
        raise ValueError("required expert projection tensor is missing or duplicated")
    tensor = matches[0]
    count = layout["expertsPerLayer"]
    size = tensor.expected_bytes()
    start = gguf.data_start + tensor.offset
    if (path.name != layout["shard"] or tensor.type_id != layout["nativeQuantTypeId"]
            or len(tensor.shape) != 3 or min(tensor.shape) < 1 or tensor.shape[-1] != count
            or start != layout["roleTensorStartInShard"] or not size or size % count
            or start + size > path.stat().st_size):
        raise ValueError("shard identity, shape, encoding or data bounds disagree with the layout")
    per_expert = size // count
    # Check block geometry on a single expert boundary (a partial block cannot be split between experts).
    if tensor.shape[0] * tensor.shape[1] % reader.BLOCK_GEOMETRY[tensor.type_name][0]:
        raise ValueError("expert boundary falls inside a quantization block")
    pos = start + per_expert * layout["expert"]
    with path.open("rb") as stream:
        stream.seek(pos)
        data = stream.read(per_expert)
    if len(data) != per_expert:
        raise ValueError("truncated expert projection payload")
    return {"offset": pos, "bytes": per_expert, "sha256": hashlib.sha256(data).hexdigest(),
            "type": tensor.type_name, "shapeGgmlOrder": tensor.shape[:2],
            "coverage": "selected tensor slice only; whole-model pin is a separate admission check"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("strata", type=Path)
    parser.add_argument("--layout", type=Path)
    parser.add_argument("--layer", type=int, default=0)
    parser.add_argument("--expert", type=int, default=0)
    parser.add_argument("--projection", choices=ROLES, default="down")
    parser.add_argument("--gguf", type=Path, help="matching real model shard to verify the selected tensor and read its bytes")
    args = parser.parse_args()
    result = inspect_layout(args.layout or args.strata / FIXTURE, args.layer, args.expert, args.projection)
    if args.gguf:
        result["verifiedProjection"] = inspect_shard(load_reader(args.strata), args.gguf, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    main()

