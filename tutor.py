"""Progressive hints controlled by a finite hint budget."""

from __future__ import annotations

from .models import ErrorType, Hint


HINT_TEMPLATES: dict[ErrorType, tuple[str, str, str]] = {
    ErrorType.CONCEPT_GAP: (
        "先回想这道题涉及的核心定义，它成立需要哪些条件？",
        "把题目中的已知条件逐一对应到定义，再检查是否遗漏限制。",
        "请写出定义并代入本题条件，然后重新尝试完整求解。",
    ),
    ErrorType.MISREAD_QUESTION: (
        "先别计算，重新圈出题目要求和所有限定词。",
        "对照你的答案，检查单位、范围、正负号或‘至少/至多’等词。",
        "请用自己的话复述题意，再根据复述后的目标重新作答。",
    ),
    ErrorType.CALCULATION_ERROR: (
        "思路可能是对的，先逐行检查数字和运算符。",
        "把中间结果单独重算一次，重点检查符号、进位、通分或约分。",
        "保留原方法，但从第一步开始重新计算并核对每个中间值。",
    ),
    ErrorType.METHOD_SELECTION: (
        "先判断题目给出的信息适合哪一类方法，不要急着套公式。",
        "比较两种可能的方法：各自需要什么条件？本题满足哪一种？",
        "请先写出选择该方法的理由，再用满足条件的方法重新求解。",
    ),
    ErrorType.PROCEDURE_GAP: (
        "回顾当前结果：它距离题目目标还差什么信息？",
        "把完整解题流程列成三步，定位你现在处于哪一步。",
        "从当前中间结果出发，补上下一步变换，再继续完成剩余步骤。",
    ),
}


class TutorAgent:
    def next_hint(self, error_type: ErrorType, attempts: int, budget: int) -> Hint:
        if error_type == ErrorType.NEEDS_CLARIFICATION:
            return Hint(level=0, text="请先补充你的思考过程，系统暂不判断错因。")

        templates = HINT_TEMPLATES[error_type]
        consumed = max(0, 3 - budget)
        level = min(max(attempts, consumed) + 1, 3)
        return Hint(level=level, text=templates[level - 1], reveals_answer=False)

