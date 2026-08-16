"""Diagnosis -> Tutor -> Planner workflow with explicit routing decisions."""

from __future__ import annotations

from .diagnosis import DiagnosisAgent
from .models import Route, SessionState
from .planner import PlannerAgent
from .tutor import TutorAgent


class StudyPilotWorkflow:
    def __init__(self, confidence_threshold: float = 0.6) -> None:
        self.diagnosis_agent = DiagnosisAgent(confidence_threshold)
        self.tutor_agent = TutorAgent()
        self.planner_agent = PlannerAgent()

    def start(self, state: SessionState) -> dict[str, object]:
        diagnosis = self.diagnosis_agent.diagnose(state.student_reasoning)
        state.diagnosis = diagnosis
        state.record(
            "diagnosis",
            error_type=diagnosis.error_type.value,
            confidence=diagnosis.confidence,
            evidence=list(diagnosis.evidence),
        )

        if diagnosis.is_low_confidence:
            state.route = Route.CLARIFY
            message = self.diagnosis_agent.clarification_question()
            state.record("route", route=state.route.value, message=message)
            return {"route": state.route.value, "diagnosis": diagnosis, "message": message}

        if state.hint_budget <= 0:
            state.route = Route.ESCALATE
            message = "提示预算已用完，建议回到定义或请求教师进一步帮助。"
            state.record("route", route=state.route.value, message=message)
            return {"route": state.route.value, "diagnosis": diagnosis, "message": message}

        state.route = Route.TUTOR
        hint = self.tutor_agent.next_hint(
            diagnosis.error_type, attempts=state.attempts, budget=state.hint_budget
        )
        state.hint_budget -= 1
        state.record("hint", level=hint.level, text=hint.text, reveals_answer=hint.reveals_answer)
        return {"route": state.route.value, "diagnosis": diagnosis, "hint": hint}

    def after_retry(self, state: SessionState, knowledge_point: str, correct: bool) -> dict[str, object]:
        state.attempts += 1
        state.record("retry", correct=correct, attempts=state.attempts)

        if correct and state.diagnosis is not None:
            state.route = Route.TRANSFER
            task = self.planner_agent.build_transfer_task(
                knowledge_point, state.diagnosis.error_type
            )
            state.record("route", route=state.route.value, transfer_task=task)
            return {"route": state.route.value, "transfer_task": task}

        return self.start(state)

