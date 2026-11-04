"""Record real native/image feasibility evidence; an unavailable engine is a block."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parents[2] / "examples" / "portable"
IMAGE = "docker.io/library/python@sha256:1148dbb014615300fa7e713b2f94f550c0d1c69780c0805f84f093ceee34dd0b"


def run(command, packet=None, timeout=30):
    try:
        result = subprocess.run(command, input=json.dumps(packet) if packet else None,
                                text=True, capture_output=True, timeout=timeout)
        return {"command": command, "exit_code": result.returncode,
                "stdout": result.stdout, "stderr": result.stderr}
    except subprocess.TimeoutExpired as exc:
        return {"command": command, "exit_code": None, "timed_out": True,
                "stdout": str(exc.stdout or ""), "stderr": str(exc.stderr or "")}


def main():
    cases = [
        ("trim", {"text": " \tHello, portable CC!\r\n"}, {"trimmed": "Hello, portable CC!"}),
        ("trim", {"text": "\u00a0 retain Unicode whitespace \u00a0"},
         {"trimmed": "\u00a0 retain Unicode whitespace \u00a0"}),
        ("empty", {}, {}),
        ("echo", {"value": {"a": [None, True, 0, "\u4e2d\u6587"], "nested": {}}},
         {"value": {"a": [None, True, 0, "\u4e2d\u6587"], "nested": {}}}),
    ]
    report = {"recorded_at": datetime.now(timezone.utc).isoformat(),
              "python": sys.version, "image": IMAGE,
              "worker_sha256": hashlib.sha256((BUNDLE / "tool.py").read_bytes()).hexdigest(),
              "native_cases": []}
    with tempfile.TemporaryDirectory(prefix="cc-v2-portable-") as temp:
        root = Path(temp)
        incoming, outgoing = root / "in", root / "out"
        incoming.mkdir()
        outgoing.mkdir()
        for index, (capability, inputs, expected) in enumerate(cases):
            packet = {"call": "direct-probe", "attempt": str(index), "capability": capability,
                      "inputs": inputs, "output_dir": str(outgoing), "resources": {}}
            result = run([sys.executable, str(BUNDLE / "tool.py")], packet)
            result["packet"] = packet
            result["expected"] = {"outcome": "ok", "outputs": expected}
            try:
                result["passed"] = result["exit_code"] == 0 and json.loads(result["stdout"]) == result["expected"]
            except (ValueError, KeyError):
                result["passed"] = False
            report["native_cases"].append(result)
        packet = {"call": "image-probe", "attempt": "0", "capability": "trim",
                  "inputs": cases[0][1], "output_dir": "/cc/out", "resources": {}}
        command = ["docker", "run", "--rm", "-i", "--network", "none", "--read-only",
                   "--mount", f"type=bind,source={BUNDLE},target=/cc/bundle,readonly",
                   "--mount", f"type=bind,source={incoming},target=/cc/in,readonly",
                   "--mount", f"type=bind,source={outgoing},target=/cc/out",
                   IMAGE, "python", "/cc/bundle/tool.py"]
        result = run(command, packet, timeout=45)
        result["packet"] = packet
        result["expected"] = {"outcome": "ok", "outputs": cases[0][2]}
        try:
            result["passed"] = result["exit_code"] == 0 and json.loads(result["stdout"]) == result["expected"]
        except (ValueError, KeyError):
            result["passed"] = False
        result["status"] = "passed" if result["passed"] else "blocked" if "dockerDesktopLinuxEngine" in result["stderr"] else "failed"
        report["image_attempt"] = result
    report["equivalence"] = "not established: image process did not execute" if report["image_attempt"]["status"] == "blocked" else "matched for trim case" if report["image_attempt"]["passed"] else "failed"
    report["native_status"] = "passed" if all(x["passed"] for x in report["native_cases"]) else "failed"
    (HERE / "probe-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"native": report["native_status"], "image": report["image_attempt"]["status"], "equivalence": report["equivalence"]}))


if __name__ == "__main__":
    main()
