"""Small command-line demo that requires no API key."""

from __future__ import annotations

import argparse
import json

from .models import SessionState
from .workflow import StudyPilotWorkflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a StudyPilot diagnosis and hint step.")
    parser.add_argument("--question", required=True)
    parser.add_argument("--answer", required=True)
    parser.add_argument("--reasoning", required=True)
    parser.add_argument("--correct-answer", default="")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    state = SessionState(
        question=args.question,
        student_answer=args.answer,
        student_reasoning=args.reasoning,
        correct_answer=args.correct_answer,
    )
    result = StudyPilotWorkflow().start(state)
    payload = {
        "route": result["route"],
        "diagnosis": {
            "error_type": state.diagnosis.error_type.value if state.diagnosis else None,
            "confidence": state.diagnosis.confidence if state.diagnosis else None,
            "evidence": list(state.diagnosis.evidence) if state.diagnosis else [],
        },
        "message": result.get("message"),
        "hint": result["hint"].text if "hint" in result else None,
        "history": state.history,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))

