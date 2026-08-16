from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_eval_data import build_cases  # noqa: E402
from run_eval import evaluate  # noqa: E402


class EvaluationTests(unittest.TestCase):
    def test_dataset_has_expected_coverage(self) -> None:
        cases = build_cases()
        self.assertEqual(len(cases), 200)
        self.assertEqual(len({case["knowledge_point"] for case in cases}), 40)
        self.assertEqual(len({case["expected_error_type"] for case in cases}), 5)

    def test_optimized_policy_improves_reproducible_metrics(self) -> None:
        metrics = evaluate(build_cases())
        accuracy = metrics["diagnosis_accuracy"]
        hard_decisions = metrics["low_confidence_hard_decision_rate"]
        exposure = metrics["first_turn_answer_exposure_rate"]
        self.assertGreater(accuracy["optimized_percent"], accuracy["baseline_percent"])
        self.assertLess(
            hard_decisions["optimized_percent"], hard_decisions["baseline_percent"]
        )
        self.assertLess(exposure["optimized_percent"], exposure["baseline_percent"])


if __name__ == "__main__":
    unittest.main()

