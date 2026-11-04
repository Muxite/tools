"""Replay read-only source and fixture probes. No engine, remote clone, model downloads or Docker required."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
from inspect_projection import FIXTURE, inspect_layout, inspect_shard, load_reader

HERE = Path(__file__).resolve().parent
CONTROL = "data/experimental-speed-projection/Qwen3.8-Flash-Next-experimental-speed-projection.gguf"


def git(repo, *args):
    return subprocess.check_output(["git", "-c", "core.autocrlf=false", "-C", str(repo), *args], stderr=subprocess.PIPE)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def apply_checked(repo, change):
    base = git(repo, "rev-parse", "HEAD").decode().strip()
    require(base == change["baseCommit"], "wrong-base")
    require(not git(repo, "status", "--porcelain"), "dirty-checkout")
    target = change["target"]
    require(sha(git(repo, "show", "HEAD:"+target)) == change["baseFileSha256"], "wrong-before-file")
    patch = (HERE / change["patch"]).resolve()
    require(patch.parent == HERE and sha(patch.read_bytes()) == change["patchSha256"], "wrong-patch")
    git(repo, "apply", "--index", "--check", str(patch))
    git(repo, "apply", "--index", str(patch))
    require(git(repo, "diff", "--cached", "--name-only", "-z").decode().split("\0") == [target, ""], "unexpected-changed-path")
    candidate = git(repo, "show", ":" + target)
    require(sha(candidate) == change["candidateFileSha256"] and sha((repo / target).read_bytes()) == sha(candidate),
            "wrong-candidate")
    return {"base": base, "patchedFile": target, "candidateFileSha256": sha(candidate),
            "materializedTreeGitOid": git(repo, "write-tree").decode().strip(), "scope": "source tree only"}


def test_synthetic_range(directory, reader):
    # A tiny two-expert F32 tensor. Distinct bytes in expert 1 catch slicing the first expert twice.
    path = directory / "synthetic.gguf"
    name = b"blk.0.ffn_down_exps.weight"
    header = (struct.pack("<4sIQQ", b"GGUF", 3, 1, 0) + struct.pack("<Q", len(name)) + name
              + struct.pack("<IQQQIQ", 3, 2, 2, 2, 0, 0))
    header += bytes(-len(header) % 32)
    tensors = struct.pack("<8f", *range(8))
    path.write_bytes(header + tensors)
    layout = {"shard": path.name, "nativeTensorName": name.decode(), "nativeQuantTypeId": 0,
              "roleTensorStartInShard": len(header), "expert": 1, "expertsPerLayer": 2}
    selected = inspect_shard(reader, path, layout)
    require(selected["bytes"] == 16 and selected["sha256"] == sha(tensors[16:]), "bad-expert-slice")
    path.write_bytes((header + tensors)[:-1])
    try:
        inspect_shard(reader, path, layout)
    except ValueError as error:
        require("bounds disagree" in str(error), "unexpected truncation failure")
    else:
        raise RuntimeError("truncated projection was accepted")
    return {"synthetic": True, "tensorShape": [2, 2, 2], "expertSelected": 1,
            "verifiedBytes": selected["bytes"], "truncatedShardRejected": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("strata", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    strata = args.strata.resolve(strict=True)
    change = json.loads((HERE / "source-change.json").read_bytes())
    base = change["baseCommit"]
    require(git(strata, "rev-parse", "HEAD").decode().strip() == base, "unexpected source reference")
    require(not git(strata, "diff", "HEAD", "--", FIXTURE, CONTROL, "tools/gguf_reader.py"), "dirty fixture or reader")
    reader = load_reader(strata)
    layout = inspect_layout(strata / FIXTURE, 0, 0, "down")
    control = reader.GGUFFile(strata / CONTROL)
    data = (strata / CONTROL).read_bytes()
    require(all(t.expected_bytes() and control.data_start + t.offset + t.expected_bytes() <= len(data)
                for t in control.tensors), "control vector out of bounds")
    try:
        inspect_shard(reader, strata / CONTROL, layout)
    except ValueError as error:
        require(str(error) == "required expert projection tensor is missing or duplicated", "unexpected control-vector error")
        mismatch = str(error)
    else:
        raise RuntimeError("control vector was wrongly accepted as MoE weights")
    report = {"layoutFixture": layout, "controlVectorGGUF": {"path": CONTROL, "fileBytes": len(data),
              "sha256": sha(data), "version": control.version, "tensorCount": len(control.tensors),
              "firstTensor": control.tensors[0].name, "firstShape": control.tensors[0].shape,
              "types": control.by_type(), "allIndexedPayloadsInBounds": True, "modelShardRejection": mismatch}}
    # Keep work inside this requested output directory. The new directory is private and ephemeral.
    with tempfile.TemporaryDirectory(prefix="probe-", dir=HERE) as path:
        temp = Path(path).resolve()
        require(temp.parent == HERE and temp.name.startswith("probe-"), "unexpected temporary directory")
        report["syntheticSliceTest"] = test_synthetic_range(temp, reader)
        checkout = temp / "strata"
        git(temp, "clone", "--shared", "--no-checkout", str(strata), str(checkout))
        git(checkout, "checkout", "--detach", base)
        report["candidate"] = apply_checked(checkout, change)
        git(checkout, "checkout", "-f", "--detach", base+"^")
        negative_base = git(checkout, "rev-parse", "HEAD").decode().strip()
        try:
            apply_checked(checkout, change)
        except ValueError as error:
            require(str(error) == "wrong-base", "wrong rejection")
            require(not git(checkout, "status", "--porcelain"), "wrong-base checkout was modified")
            report["wrongBase"] = {"base": negative_base, "reason": str(error), "checkoutCleanAfterRejection": True}
        else:
            raise RuntimeError("wrong base was accepted")
    encoded = json.dumps(report, indent=2) + "\n"
    if args.receipt:
        args.receipt.write_bytes(encoded.encode())
    print(encoded, end="")


if __name__ == "__main__":
    main()

