"""Generate a lightweight transfer task after the learner retries."""

from __future__ import annotations

from .models import ErrorType


TRANSFER_PROMPTS: dict[ErrorType, str] = {
    ErrorType.CONCEPT_GAP: "换一组数值，但保持同一概念条件，先说明定义再作答。",
    ErrorType.MISREAD_QUESTION: "完成一道包含不同限定词的同类题，并先复述题意。",
    ErrorType.CALCULATION_ERROR: "完成一道步骤相同但数字不同的题，并保留中间计算。",
    ErrorType.METHOD_SELECTION: "比较两道外观相似但解法不同的题，说明方法选择依据。",
    ErrorType.PROCEDURE_GAP: "完成一道同流程变式题，并为每一步标注目的。",
}


class PlannerAgent:
    def build_transfer_task(self, knowledge_point: str, error_type: ErrorType) -> str:
        if error_type == ErrorType.NEEDS_CLARIFICATION:
            return "诊断尚未确认，暂不生成迁移练习。"
        return f"【{knowledge_point}·迁移练习】{TRANSFER_PROMPTS[error_type]}"

