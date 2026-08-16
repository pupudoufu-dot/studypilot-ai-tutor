"""Misconception diagnosis with explicit confidence and clarification fallback.

This is deliberately rule-based. It keeps the repository runnable without an
API key and makes the evaluation reproducible. A production system could swap
this module for an LLM-backed classifier while preserving the same contract.
"""

from __future__ import annotations

import re
from collections import defaultdict

from .models import Diagnosis, ErrorType


BASELINE_RULES: dict[ErrorType, tuple[str, ...]] = {
    ErrorType.CONCEPT_GAP: ("概念不懂", "不理解定义", "以为"),
    ErrorType.MISREAD_QUESTION: ("看错", "漏看", "读成"),
    ErrorType.CALCULATION_ERROR: ("算错", "计算错", "抄错"),
    ErrorType.METHOD_SELECTION: ("方法不对", "不知道用什么", "公式选错"),
    ErrorType.PROCEDURE_GAP: ("不知道下一步", "步骤忘了", "卡在"),
}


OPTIMIZED_RULES: dict[ErrorType, tuple[str, ...]] = {
    ErrorType.CONCEPT_GAP: (
        "概念不懂", "不理解定义", "以为", "没弄清", "混淆", "理解成",
        "不知道含义", "定义记反", "条件理解错",
    ),
    ErrorType.MISREAD_QUESTION: (
        "看错", "漏看", "读成", "忽略", "没注意", "审题", "少看",
        "把已知当成", "题意理解偏了",
    ),
    ErrorType.CALCULATION_ERROR: (
        "算错", "计算错", "抄错", "符号写反", "进位", "约分错",
        "通分错", "运算失误", "数字带错",
    ),
    ErrorType.METHOD_SELECTION: (
        "方法不对", "不知道用什么", "公式选错", "选了", "不该用",
        "用了错误", "思路方向", "方法选错", "公式套错",
    ),
    ErrorType.PROCEDURE_GAP: (
        "不知道下一步", "步骤忘了", "卡在", "做到这里", "接下来",
        "顺序", "漏了一步", "中间步骤", "不会继续",
    ),
}


PATTERN_RULES: dict[ErrorType, tuple[str, ...]] = {
    ErrorType.MISREAD_QUESTION: (r"把.+当成", r"题目.+没有看到"),
    ErrorType.CALCULATION_ERROR: (r"[-+×÷]号.+写反", r"从.+算成"),
    ErrorType.METHOD_SELECTION: (r"本来应该.+却用了",),
    ErrorType.PROCEDURE_GAP: (r"会做到.+但",),
}

OPTIMIZED_RULES[ErrorType.MISREAD_QUESTION] += ("\u6309\u5370\u8c61\u505a", "\u6ca1\u91cd\u65b0\u8bfb\u9898")
NEGATION_MARKERS = ("\u4e0d\u662f", "\u5e76\u975e", "\u6ca1\u6709")


class DiagnosisAgent:
    def __init__(self, confidence_threshold: float = 0.6) -> None:
        self.confidence_threshold = confidence_threshold

    def diagnose(self, reasoning: str, mode: str = "optimized") -> Diagnosis:
        text = reasoning.strip()
        rules = BASELINE_RULES if mode == "baseline" else OPTIMIZED_RULES
        scores: dict[ErrorType, list[str]] = defaultdict(list)

        for error_type, keywords in rules.items():
            for keyword in keywords:
                start = 0
                while (match_index := text.find(keyword, start)) != -1:
                    if not self._is_negated(text, match_index):
                        scores[error_type].append(keyword)
                    start = match_index + len(keyword)

        if mode == "optimized":
            for error_type, patterns in PATTERN_RULES.items():
                for pattern in patterns:
                    if re.search(pattern, text):
                        scores[error_type].append(f"/{pattern}/")

        if not scores:
            if mode == "baseline":
                return Diagnosis(
                    error_type=ErrorType.CONCEPT_GAP,
                    confidence=0.4,
                    rationale="Baseline forces a default label when evidence is missing.",
                )
            return Diagnosis(
                error_type=ErrorType.NEEDS_CLARIFICATION,
                confidence=0.35,
                rationale="No reliable evidence; ask a clarifying question instead of guessing.",
            )

        ranked = sorted(
            scores.items(), key=lambda item: (len(item[1]), item[0].value), reverse=True
        )
        best_type, evidence = ranked[0]
        tied = len(ranked) > 1 and len(ranked[0][1]) == len(ranked[1][1])
        confidence = 0.58 if tied else min(0.72 + 0.08 * (len(evidence) - 1), 0.94)

        if mode == "optimized" and confidence < self.confidence_threshold:
            return Diagnosis(
                error_type=ErrorType.NEEDS_CLARIFICATION,
                confidence=confidence,
                evidence=tuple(evidence),
                rationale="Signals conflict; clarification is safer than a hard diagnosis.",
            )

        return Diagnosis(
            error_type=best_type,
            confidence=confidence,
            evidence=tuple(evidence),
            rationale=f"Matched {len(evidence)} evidence signal(s).",
        )

    @staticmethod
    def _is_negated(text: str, match_index: int) -> bool:
        """Do not treat an explicitly rejected cause as positive evidence."""
        preceding_text = text[max(0, match_index - 4) : match_index]
        return any(marker in preceding_text for marker in NEGATION_MARKERS)

    @staticmethod
    def clarification_question() -> str:
        return "你能说说从哪一步开始不确定，或者你当时为什么选择这个方法吗？"

