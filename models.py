"""Core data models kept dependency-free for easy review and reuse."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ErrorType(str, Enum):
    CONCEPT_GAP = "concept_gap"
    MISREAD_QUESTION = "misread_question"
    CALCULATION_ERROR = "calculation_error"
    METHOD_SELECTION = "method_selection"
    PROCEDURE_GAP = "procedure_gap"
    NEEDS_CLARIFICATION = "needs_clarification"


class Route(str, Enum):
    CLARIFY = "clarify"
    TUTOR = "tutor"
    TRANSFER = "transfer"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class Diagnosis:
    error_type: ErrorType
    confidence: float
    evidence: tuple[str, ...] = ()
    rationale: str = ""

    @property
    def is_low_confidence(self) -> bool:
        return self.confidence < 0.6


@dataclass(frozen=True)
class Hint:
    level: int
    text: str
    reveals_answer: bool = False


@dataclass
class SessionState:
    question: str
    student_answer: str
    student_reasoning: str
    correct_answer: str = ""
    attempts: int = 0
    hint_budget: int = 3
    diagnosis: Diagnosis | None = None
    route: Route | None = None
    history: list[dict[str, Any]] = field(default_factory=list)

    def record(self, event: str, **payload: Any) -> None:
        self.history.append({"event": event, **payload})

