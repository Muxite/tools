"""Run the reference Host against the shared portable worker and preserve receipts."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parents[2]
sys.path.insert(0, str(REFERENCE))
from ccv2 import Host


def main():
    output = Path(sys.argv[1]).resolve()
    output.mkdir(parents=True, exist_ok=True)
    host = Host(output / "host-store")
    bundle = REFERENCE / "examples" / "portable"
    report = {"recorded_at": datetime.now(timezone.utc).isoformat(), "native": [], "image": []}
    native = host.seal(bundle)
    report["native_release"] = native
    cases = [("trim", {"text": " \tHello, portable CC!\r\n"}), ("empty", {}),
             ("echo", {"value": {"a": [None, True, 0, "\u4e2d\u6587"]}}),
             ("write-text", {"text": "Portable artifact \u4e2d\u6587\n"})]
    for capability, inputs in cases:
        receipt = host.call(native, capability, inputs, timeout=45)
        report["native"].append(receipt)
        if capability == "write-text" and receipt["state"] == "succeeded":
            expected = inputs["text"].encode("utf-8")
            artifact = receipt["outputs"]["file"]
            report["artifact_bytes_match"] = host.artifact_path(artifact).read_bytes() == expected
            report["artifact_digest_match"] = artifact["sha256"] == hashlib.sha256(expected).hexdigest()
    with tempfile.TemporaryDirectory(prefix="cc-v2-image-bundle-") as temporary:
        image_bundle = Path(temporary)
        shutil.copyfile(bundle / "image.yaml", image_bundle / "cc.yaml")
        shutil.copyfile(bundle / "tool.py", image_bundle / "tool.py")
        image_release = host.seal(image_bundle)
        report["image_release"] = image_release
        report["image"].append(host.call(image_release, "trim", cases[0][1], timeout=45))
    report["native_passed"] = all(r["state"] == "succeeded" for r in report["native"])
    report["image_passed"] = all(r["state"] == "succeeded" for r in report["image"])
    report["trim_outputs_equal"] = report["image_passed"] and report["native"][0]["outputs"] == report["image"][0]["outputs"]
    (output / "host-probe-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("native_passed", "image_passed", "trim_outputs_equal")}))


if __name__ == "__main__":
    main()
