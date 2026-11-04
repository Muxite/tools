import hashlib
import json
import math
import unittest
from pathlib import Path
from analyze_pairs import analyze, validate_record


def row(condition, pair="p1", total=8, status="completed", order=None):
    return {"schema_version": "1.0", "protocol_id": "draft-1", "case_id": "DEV-01",
            "split": "development", "pair_id": pair, "repetition": 1,
            "condition": condition, "order_position": order or (1 if condition == "cc" else 2),
            "assignment_seed": "seed-1", "started_at": None, "ended_at": None,
            "status": status, "termination_reason": None if status == "completed" else "budget cap",
            "prompt_sha256": "prompt-hash", "fixture_manifest_sha256": "fixture-hash",
            "environment": {"model": "model@pin", "tools": ["tool@1"]}, "cc_versions": [],
            "limits": {"wall_seconds": 600, "tokens": 5000, "tool_calls": 10},
            "measurements": {"elapsed_seconds": 12.5, "input_tokens": 100, "output_tokens": 50,
                             "tool_calls": 2, "cost_usd": None},
            "measurement_null_reason": {"cost_usd": "provider does not expose cost"},
            "artifact": None, "scores": None, "deviations": []}


def scored(condition, **kwargs):
    record = row(condition, **kwargs)
    value = kwargs.get("total", 8) // 4
    record["scores"] = {"factual_support": value, "task_coverage": value,
                        "reasoning_synthesis": value, "usability_format": value,
                        "total": value * 4, "critical_errors": []}
    return record


class PairAnalysisTests(unittest.TestCase):
    def test_matched_difference_and_metrics(self):
        result = analyze([scored("cc", total=12), scored("plain_agent", total=8)])
        self.assertEqual(result["accepted_completed_pairs"], 1)
        self.assertEqual(result["total_score_cc_minus_plain"]["mean"], 4)
        self.assertEqual(result["measurements"]["elapsed_seconds"]["accepted_pairs"]["paired_differences_cc_minus_plain"]["mean"], 0)
        self.assertIsNone(result["measurements"]["cost_usd"]["accepted_pairs"]["cc"]["mean"])

    def test_partial_pair_remains_visible(self):
        result = analyze([scored("cc")])
        self.assertFalse(result["primary_analysis_available"])
        self.assertIn("missing arm", result["excluded_pairs"][0]["reasons"])

    def test_failure_preserved_and_measurements_remain_visible(self):
        failed_cc = row("cc", status="failed")
        failed_cc["measurements"]["elapsed_seconds"] = 17
        result = analyze([failed_cc, scored("plain_agent")])
        self.assertEqual(result["status_counts"], {"completed": 1, "failed": 1})
        self.assertEqual(result["status_counts_by_condition"]["cc"], {"failed": 1})
        self.assertEqual(result["accepted_completed_pairs"], 0)
        self.assertEqual(result["measurements"]["elapsed_seconds"]["all_runs_by_condition"]["cc"]["mean"], 17)
        self.assertIn("arm not completed", result["excluded_pairs"][0]["reasons"])

    def test_mismatched_task_inputs_excluded(self):
        cc, plain = scored("cc"), scored("plain_agent")
        plain["prompt_sha256"] = "other-prompt"
        result = analyze([cc, plain])
        self.assertFalse(result["primary_analysis_available"])
        self.assertIn("mismatched prompt_sha256", result["excluded_pairs"][0]["reasons"])

    def test_mismatches_rejected(self):
        cc, plain = scored("cc"), scored("plain_agent")
        plain["limits"]["tokens"] = 4000
        result = analyze([cc, plain])
        self.assertEqual(result["accepted_completed_pairs"], 0)
        self.assertIn("mismatched limits", result["excluded_pairs"][0]["reasons"])

    def test_model_and_tools_mismatch_excluded(self):
        cc, plain = scored("cc"), scored("plain_agent")
        plain["environment"]["model"] = "other-model"
        result = analyze([cc, plain])
        self.assertIn("mismatched environment.model", result["excluded_pairs"][0]["reasons"])

    def test_nonfinite_and_negative_measurement_rejected(self):
        for value in (math.inf, math.nan, -1, True):
            record = row("cc")
            record["measurements"]["elapsed_seconds"] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "finite non-negative"):
                validate_record(record)

    def test_null_measurement_requires_reason(self):
        record = row("cc")
        record["measurement_null_reason"] = {}
        with self.assertRaisesRegex(ValueError, "requires a measurement_null_reason"):
            validate_record(record)

    def test_repeated_arm_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            analyze([scored("cc"), scored("cc")])

    def test_noncompleted_requires_reason(self):
        record = row("cc", status="interrupted")
        record["termination_reason"] = None
        with self.assertRaisesRegex(ValueError, "needs termination_reason"):
            validate_record(record)

    def test_dimension_bounds_and_total(self):
        record = scored("cc")
        record["scores"]["factual_support"] = 5
        with self.assertRaisesRegex(ValueError, "0 to 4"):
            validate_record(record)

    def test_wall_seconds_must_be_finite_and_positive(self):
        for value in (math.nan, math.inf, True, 0, -2):
            record = row("cc")
            record["limits"]["wall_seconds"] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "finite and positive"):
                validate_record(record)

    def test_completed_deviation_pair_appears_only_in_sensitivity(self):
        cc, plain = scored("cc", total=12), scored("plain_agent", total=8)
        cc["deviations"] = ["minor output formatting deviation"]
        result = analyze([cc, plain])
        self.assertEqual(result["accepted_completed_pairs"], 0)
        self.assertEqual(result["total_score_cc_minus_plain"]["n"], 0)
        self.assertEqual(result["exploratory_deviation_sensitivity"]["n"], 1)
        self.assertEqual(result["exploratory_deviation_sensitivity"]["score_difference"]["mean"], 4)

    def test_dev05_fixture_arithmetic_and_scorer_key(self):
        cases = Path(__file__).resolve().parents[1] / "Development-Cases"
        fixture = json.loads((cases / "DEV-05" / "fixture.json").read_text(encoding="utf-8-sig"))
        score_pairs = [row for row in fixture if row.get("cc", {}).get("score") is not None
                       and row.get("plain", {}).get("score") is not None]
        time_pairs = [row for row in fixture if row.get("cc", {}).get("elapsed_seconds") is not None
                      and row.get("plain", {}).get("elapsed_seconds") is not None]
        self.assertEqual(len(score_pairs), 1)
        self.assertEqual(score_pairs[0]["cc"]["score"] - score_pairs[0]["plain"]["score"], 2)
        self.assertEqual(len(time_pairs), 1)
        self.assertEqual(time_pairs[0]["cc"]["elapsed_seconds"] - time_pairs[0]["plain"]["elapsed_seconds"], -5)
        key = (cases / "DEV-05" / "scorer-key.md").read_text(encoding="utf-8-sig")
        self.assertIn("+2", key)
        self.assertIn("-5 seconds", key)

    def test_case_manifests_hash_only_execution_inputs(self):
        cases = Path(__file__).resolve().parents[1] / "Development-Cases"
        for case in sorted(cases.glob("DEV-*")):
            if not case.is_dir():
                continue
            manifest = json.loads((case / "manifest.json").read_text(encoding="utf-8"))
            names = {item["path"] for item in manifest["inputs"]}
            self.assertIn("prompt.txt", names)
            self.assertNotIn("scorer-key.md", names)
            for item in manifest["inputs"]:
                content = (case / item["path"]).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), item["sha256"])
            self.assertTrue((case / "scorer-key.md").is_file())


if __name__ == "__main__":
    unittest.main()
