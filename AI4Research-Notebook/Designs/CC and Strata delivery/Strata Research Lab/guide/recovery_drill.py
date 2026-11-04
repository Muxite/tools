"""Offline synthetic protocol drill. Run: python recovery_drill.py"""
import argparse
import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path

RUN = "one-gb10"
CELLS = ("q1", "q2")
# In deployment the protected scorer holds its own rubric and reference answers.
ANSWER_KEY = {"q1": "red", "q2": "blue"}



def digest(data):
    return hashlib.sha256(data).hexdigest()


def new_connection(path):
    db = sqlite3.connect(path)
    db.execute("CREATE TABLE IF NOT EXISTS lease (run TEXT PRIMARY KEY, epoch INTEGER)")
    db.execute("CREATE TABLE IF NOT EXISTS receipt (arm TEXT PRIMARY KEY, epoch INTEGER, path TEXT, sha TEXT)")
    return db


def fence(db, expected, stopped):
    if not stopped:
        raise ValueError("old attempt still owns the device")
    with db:
        cur = db.execute("UPDATE lease SET epoch=epoch+1 WHERE run=? AND epoch=?", (RUN, expected))
        if cur.rowcount != 1:
            raise ValueError("stale lease")


def seal(db, root, epoch, arm, payload):
    encoded = json.dumps(payload, sort_keys=True).encode()
    sha = digest(encoded)
    with db:
        # A write transaction fences the authority check and admission together.
        db.execute("BEGIN IMMEDIATE")
        active = db.execute("SELECT epoch FROM lease WHERE run=?", (RUN,)).fetchone()
        if active != (epoch,):
            raise ValueError("stale lease")
        if [row["id"] for row in payload["samples"]] != list(CELLS):
            raise ValueError("incomplete arm")
        if not payload["host_peak_samples_mib"]:
            raise ValueError("missing memory evidence")
        old = db.execute("SELECT sha FROM receipt WHERE arm=?", (arm,)).fetchone()
        if old:
            if old != (sha,):
                raise ValueError("conflicting evidence")
            return sha
        blob = root / sha
        blob.write_bytes(encoded)
        db.execute("INSERT INTO receipt VALUES (?,?,?,?)", (arm, epoch, str(blob), sha))
    return sha


def score(db, policy):
    gates = {gate["metric"]: gate["threshold"] for gate in policy["gates"]}
    receipts = db.execute("SELECT arm,path,sha FROM receipt ORDER BY arm").fetchall()
    if {r[0] for r in receipts} != {"baseline", "candidate"}:
        return "inconclusive"
    outcomes = {}
    for arm, path, expected in receipts:
        data = Path(path).read_bytes()
        if digest(data) != expected:
            return "inconclusive"
        raw = json.loads(data)
        rows = raw["samples"]
        if raw.get("checks") != {"inference-api": True, "router-parity": True}:
            return "inconclusive"
        quality = sum(row["answer"] == ANSWER_KEY[row["id"]] for row in rows) / len(rows)
        # Compute rates from captured counts/durations, ignoring candidate claims.
        pack_bytes = sum(raw["unique_pack_bytes_by_digest"].values())
        outcomes[arm] = (pack_bytes, max(raw["host_peak_samples_mib"]), quality, {
            phase: [row[phase + "_tokens"] / row[phase + "_s"] for row in rows]
            for phase in ("prefill", "decode")
        })
    b_bytes, b_peak, b_quality, b_rates = outcomes["baseline"]
    c_bytes, c_peak, c_quality, c_rates = outcomes["candidate"]
    rates_ok = all(c / b >= gates[phase] for phase in b_rates
                   for c, b in zip(c_rates[phase], b_rates[phase]))
    ok = (c_bytes / b_bytes <= gates["total-unique-pack-bytes"] and
          c_peak / b_peak <= gates["peak-shared-memory"] and
          c_quality - b_quality >= gates["quality"] and rates_ok)
    return "pass" if ok else "fail"


def fixture(peak, wrong=False):
    return {"checks": {"inference-api": True, "router-parity": True},
            "unique_pack_bytes_by_digest": {"fixture-shard": 1000 if peak == 1000 else 800},
            "host_peak_samples_mib": [peak - 10, peak], "worker_claim": "pass",
            "samples": [{"id": key, "answer": ("wrong" if wrong and key == "q2" else ANSWER_KEY[key]),
                         "prefill_tokens": 128, "prefill_s": 2, "decode_tokens": 16,
                         "decode_s": 1} for key in CELLS]}


def expect_rejection(reason, operation):
    try:
        operation()
    except ValueError as error:
        if str(error) == reason:
            return
        raise
    raise RuntimeError("accepted invalid operation: " + reason)


def check(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path,
                        default=Path(__file__).resolve().parents[1] / "shared/examples/evaluation-policy.json")
    policy = json.loads(parser.parse_args().policy.read_bytes())
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        dbpath = root / "manager.sqlite"
        db = new_connection(dbpath)
        with db:
            db.execute("INSERT INTO lease VALUES (?,1)", (RUN,))
        b = fixture(1000)
        original = seal(db, root, 1, "baseline", b)
        partial = fixture(900)
        partial["samples"].pop()
        quarantine = root / "attempt-1-partial.json"
        quarantine.write_text(json.dumps(partial))
        expect_rejection("incomplete arm", lambda: seal(db, root, 1, "candidate", partial))
        db.close()  # Simulate loss of the manager process; disk remains.
        db = new_connection(dbpath)
        check(score(db, policy) == "inconclusive", "missing evidence scored")
        expect_rejection("old attempt still owns the device", lambda: fence(db, 1, False))
        fence(db, 1, stopped=True)  # Operator stop receipt simulated for the drill.
        c = fixture(900, wrong=True)
        expect_rejection("stale lease", lambda: seal(db, root, 1, "candidate", c))
        accepted = seal(db, root, 2, "candidate", c)
        check(accepted == seal(db, root, 2, "candidate", c), "duplicate altered outcome")
        expect_rejection("conflicting evidence", lambda: seal(db, root, 2, "candidate", fixture(901)))
        check(quarantine.exists() and seal(db, root, 2, "baseline", b) == original, "lost prior evidence")
        check(score(db, policy) == "fail", "candidate self-report overrode the independent quality gate")
        (root / accepted).write_bytes(b"tampered")
        check(score(db, policy) == "inconclusive", "corruption accepted")
        db.close()
    print("PASS (synthetic only): sealed baseline survived reopen; incomplete arm excluded; "
          "unconfirmed stop and stale epoch rejected; duplicate deduplicated; conflict rejected; "
          "wrong answer overrode self-reported pass; corrupt evidence inconclusive.")


if __name__ == "__main__":
    main()

