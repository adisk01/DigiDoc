"""Turn loop: extract → gate → static follow-up or stop."""

from __future__ import annotations

from pydantic import BaseModel

from digidoc.gate import evaluate
from digidoc.intake.extract import extract
from digidoc.intake.questions import next_prompt
from digidoc.models import GateResult, Intake, Route

MAX_FOLLOW_UPS = 8
STOP_ROUTES = {Route.EMERGENCY, Route.HUMAN_HANDOFF_NOW}


class Turn(BaseModel):
    intake: Intake
    gate_result: GateResult
    next_question: str | None = None
    complete: bool


class IntakeSession:
    def __init__(self) -> None:
        self.intake: Intake | None = None
        self.questions_asked: int = 0
        self.asked: set[str] = set()
        self.pending: tuple[str, ...] = ()
        self.pending_question: str | None = None

    def receive(self, message: str) -> Turn:
        intake = extract(message, self.intake, self.pending_question, self.pending)
        self.intake = intake
        gate_result = evaluate(intake)

        if gate_result.route in STOP_ROUTES:
            return Turn(intake=intake, gate_result=gate_result, next_question=None, complete=True)

        if intake.extraction_failed:
            # Model outage or unparsable output. Asking again cannot succeed and would hold
            # the patient in a loop, so hand the case to the doctor with what we have.
            return Turn(intake=intake, gate_result=gate_result, next_question=None, complete=True)

        question, fields = next_prompt(intake, frozenset(self.asked))
        if question is None:
            return Turn(intake=intake, gate_result=gate_result, next_question=None, complete=True)

        if self.questions_asked >= MAX_FOLLOW_UPS:
            # Incomplete; R00_INCOMPLETE_INTAKE already handled in the gate.
            return Turn(intake=intake, gate_result=gate_result, next_question=None, complete=True)

        self.questions_asked += 1
        self.asked.add(question)
        self.pending_question, self.pending = question, fields
        return Turn(intake=intake, gate_result=gate_result, next_question=question, complete=False)
