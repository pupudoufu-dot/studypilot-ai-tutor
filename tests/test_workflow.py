from __future__ import annotations

import unittest

from studypilot.diagnosis import DiagnosisAgent
from studypilot.models import ErrorType, Route, SessionState
from studypilot.workflow import StudyPilotWorkflow


class DiagnosisTests(unittest.TestCase):
    def test_recognizes_calculation_error(self) -> None:
        result = DiagnosisAgent().diagnose("方法会做，但这里通分错了。")
        self.assertEqual(result.error_type, ErrorType.CALCULATION_ERROR)
        self.assertGreaterEqual(result.confidence, 0.6)

    def test_ambiguous_reasoning_uses_clarification(self) -> None:
        result = DiagnosisAgent().diagnose("我就是觉得应该这样。")
        self.assertEqual(result.error_type, ErrorType.NEEDS_CLARIFICATION)
        self.assertTrue(result.is_low_confidence)

    def test_negated_misread_does_not_hide_calculation_error(self) -> None:
        result = DiagnosisAgent().diagnose(
            "\u6211\u4e0d\u662f\u770b\u9519\u9898\uff0c\u662f\u628a\u79fb\u9879\u7684\u7b26\u53f7\u5199\u53cd\u4e86\u3002"
        )
        self.assertEqual(result.error_type, ErrorType.CALCULATION_ERROR)
        self.assertGreaterEqual(result.confidence, 0.6)


class WorkflowTests(unittest.TestCase):
    def test_low_confidence_routes_to_clarification(self) -> None:
        state = SessionState("题目", "答案", "我就是觉得应该这样。")
        result = StudyPilotWorkflow().start(state)
        self.assertEqual(result["route"], Route.CLARIFY.value)
        self.assertIn("为什么", str(result["message"]))

    def test_hint_does_not_reveal_answer(self) -> None:
        state = SessionState("题目", "答案", "我漏看了最后一个限定条件。")
        result = StudyPilotWorkflow().start(state)
        self.assertEqual(result["route"], Route.TUTOR.value)
        self.assertFalse(result["hint"].reveals_answer)
        self.assertEqual(state.hint_budget, 2)

    def test_correct_retry_routes_to_transfer(self) -> None:
        state = SessionState("题目", "答案", "这里计算错了。")
        workflow = StudyPilotWorkflow()
        workflow.start(state)
        result = workflow.after_retry(state, "分数加法", correct=True)
        self.assertEqual(result["route"], Route.TRANSFER.value)
        self.assertIn("迁移练习", str(result["transfer_task"]))

    def test_zero_budget_escalates(self) -> None:
        state = SessionState(
            "题目", "答案", "我看错了题目要求。", hint_budget=0
        )
        result = StudyPilotWorkflow().start(state)
        self.assertEqual(result["route"], Route.ESCALATE.value)


if __name__ == "__main__":
    unittest.main()

