"""FastAPI backend for the doctor console and patient intake simulator."""

from __future__ import annotations

import json
import os
import uuid
from collections.abc import Iterator
from contextlib import contextmanager, nullcontext
from dataclasses import asdict
from pathlib import Path
from typing import Any, Literal

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from digidoc.console import store
from digidoc.console.presenters import case_view, queue_view
from digidoc.draft import draft
from digidoc.draft.schema import Draft
from digidoc.gate.safety_net import message_for
from digidoc.i18n import t
from digidoc.intake.questions import translate_question
from digidoc.llm import api_key
from digidoc.intake.session import IntakeSession, Turn
from digidoc.models import GateResult, Intake
from digidoc.retrieval import build_query, get_chunk, search
from digidoc.specialist.diabetic_foot.schema import ExamFindings
from digidoc.specialist.registry import get as specialist_get
from digidoc.specialist.registry import get_chunk as specialist_chunk

ROOT = Path(__file__).resolve().parent.parent.parent
STATIC = Path(__file__).resolve().parent / "static"
FIXTURES = ROOT / "fixtures" / "scenarios.json"

app = FastAPI(title="DigiDoc doctor console")
store.init_db()
SESSIONS: dict[str, IntakeSession] = {}


class PatientMessage(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    text: str = Field(min_length=1, max_length=10_000)
    language: Literal["id", "en"] = "id"


class ModelModeBody(BaseModel):
    mode: Literal["real", "mock", "off"]


class ActionBody(BaseModel):
    action: Literal["accept", "edit", "reject", "sign", "consult"]
    payload: dict[str, Any] = Field(default_factory=dict)
    language: Literal["id", "en"] = "id"


Language = Literal["id", "en"]


@contextmanager
def _model_mode(mode: str) -> Iterator[None]:
    old = os.environ.get("MODEL_MODE")
    os.environ["MODEL_MODE"] = mode
    try:
        yield
    finally:
        if old is None:
            os.environ.pop("MODEL_MODE", None)
        else:
            os.environ["MODEL_MODE"] = old


def _make_case(
    case_id: str,
    session_id: str,
    message: str,
    turn: Turn,
    *,
    force_draft_off: bool = False,
    language: str = "id",
) -> None:
    intake, gate = turn.intake, turn.gate_result
    chunks = search(build_query(intake, gate))
    with _model_mode("off") if force_draft_off else nullcontext():
        result = draft(intake, gate, chunks, language)
    store.insert_case(
        case_id=case_id,
        session_id=session_id,
        message=message,
        intake=intake.model_dump(mode="json"),
        gate=gate.model_dump(mode="json"),
        draft=result.model_dump(mode="json"),
        chunks=[asdict(chunk) for chunk in chunks],
    )


@app.get("/")
def console_page() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/patient")
def patient_page() -> FileResponse:
    return FileResponse(STATIC / "patient.html")


@app.post("/patient/message")
def patient_message(body: PatientMessage) -> dict[str, Any]:
    session = SESSIONS.setdefault(body.session_id, IntakeSession())
    turn = session.receive(body.text)
    # Outage fails closed immediately: queue the partial raw intake for a doctor.
    if os.environ.get("MODEL_MODE", "mock").lower() == "off":
        turn.complete = True
        turn.next_question = None
    case_id = None
    if turn.complete:
        case_id = f"C-{uuid.uuid4().hex[:8].upper()}"
        _make_case(
            case_id,
            body.session_id,
            turn.intake.raw_message,
            turn,
            language=body.language,
        )
        SESSIONS.pop(body.session_id, None)
    reply = (
        message_for(turn.gate_result.safety_net_key, body.language)
        if turn.complete
        else translate_question(turn.next_question, body.language)
    )
    return {
        "reply_to_patient": reply,
        "complete": turn.complete,
        "route": turn.gate_result.route.value if turn.complete else None,
        "case_id": case_id,
    }


@app.get("/queue")
def queue(language: Language = "id") -> list[dict[str, Any]]:
    return queue_view(store.list_cases(), language)


@app.get("/case/{case_id}")
def get_case(case_id: str, language: Language = "id") -> dict[str, Any]:
    row = store.get_case(case_id)
    if row is None:
        raise HTTPException(404, t("e_case_not_found", language))
    return case_view(row, store.actions_for(case_id), language)


@app.post("/case/{case_id}/action")
def case_action(case_id: str, body: ActionBody) -> dict[str, Any]:
    language = body.language
    row = store.get_case(case_id)
    if row is None:
        raise HTTPException(404, t("e_case_not_found", language))
    if row["frozen"]:
        raise HTTPException(409, t("e_case_frozen", language))

    actor = str(body.payload.get("doctor_id") or "dr.")
    if body.action == "sign":
        doctor_id = str(body.payload.get("doctor_id") or "").strip()
        if not doctor_id:
            raise HTTPException(422, t("e_doctor_required", language))
        store.sign_case(case_id, doctor_id)
        actor = doctor_id
    elif body.action == "edit":
        _edit_draft(row, body.payload, language)
    elif body.action == "consult":
        _consult(row, body.payload, language)
    store.add_action(case_id, body.action, body.payload, actor)
    updated = store.get_case(case_id)
    assert updated is not None
    return case_view(updated, store.actions_for(case_id), language)


def _edit_draft(row: Any, payload: dict[str, Any], language: str) -> None:
    if not row["draft_json"]:
        raise HTTPException(409, t("e_no_draft", language))
    current = json.loads(row["draft_json"])
    if "draft" in payload:
        candidate = payload["draft"]
    else:
        candidate = {**current, **{k: v for k, v in payload.items() if k not in ("doctor_id", "language")}}
    try:
        validated = Draft.model_validate(candidate)
    except Exception as exc:
        raise HTTPException(422, t("e_invalid_draft", language, detail=exc)) from exc
    store.update_draft(row["id"], validated.model_dump(mode="json"))


def _default_findings(module_name: str) -> dict[str, Any]:
    if module_name != "diabetic_foot":
        return {}
    scenarios = json.loads(FIXTURES.read_text(encoding="utf-8"))["scenarios"]
    for sc in scenarios:
        if sc["id"] == "S3":
            return dict(sc["layer2"]["exam_findings"])
    return {}


def _consult(row: Any, payload: dict[str, Any], language: str) -> None:
    gate = GateResult.model_validate_json(row["gate_json"])
    module_name = str(payload.get("module") or "")
    if module_name not in gate.layer2_modules:
        raise HTTPException(422, t("e_module_unavailable", language))
    if row["consult_json"]:
        # One consult per case. A second run would silently overwrite a result the doctor may
        # already have read and acted on, and the Wagner grade is not something to re-roll.
        raise HTTPException(409, t("e_consult_done", language))
    raw = payload.get("findings") or payload.get("exam_findings") or _default_findings(module_name)
    try:
        findings = ExamFindings.model_validate(raw)
    except Exception as exc:
        raise HTTPException(422, t("e_invalid_findings", language, detail=exc)) from exc
    module = specialist_get(module_name)
    intake = Intake.model_validate_json(row["intake_json"])
    result = module.consult(intake, gate, findings, language)
    store.update_consult(row["id"], result.model_dump(mode="json"))


@app.post("/admin/model_mode")
def set_model_mode(body: ModelModeBody) -> dict[str, Any]:
    os.environ["MODEL_MODE"] = body.mode
    return {"mode": body.mode, "key_available": bool(api_key())}


@app.get("/admin/model_mode")
def get_model_mode() -> dict[str, Any]:
    return {
        "mode": os.environ.get("MODEL_MODE", "mock").lower(),
        "key_available": bool(api_key()),
    }


@app.post("/admin/seed")
def seed_demo(language: Language = "id") -> dict[str, int]:
    store.clear_demo()
    SESSIONS.clear()
    scenarios = json.loads(FIXTURES.read_text(encoding="utf-8"))["scenarios"]
    # Always seed from the fixtures, whatever mode the console is in. The loop below feeds
    # each scenario its own message until intake is complete, which only terminates usefully
    # against the canned gold intake; a live model extracts a partial intake from the first
    # message and re-reading the same text teaches it nothing, so every scenario would land
    # incomplete and collapse to clinician_review with no draft.
    with _model_mode("mock"):
        for scenario in scenarios:
            session = IntakeSession()
            turn = session.receive(scenario["message"])
            while not turn.complete:
                turn = session.receive(scenario["message"])
            turn.intake.raw_message = scenario["message"]
            _make_case(
                scenario["id"],
                f"seed-{scenario['id']}",
                scenario["message"],
                turn,
                force_draft_off=(
                    scenario.get("runtime", {}).get("model_available") is False
                ),
                language=language,
            )
    return {"created": len(scenarios)}


@app.get("/corpus/{key}/{section_id}")
def corpus_chunk(key: str, section_id: str, language: Language = "id") -> dict[str, str]:
    chunk = get_chunk(key, section_id) or specialist_chunk(key, section_id)
    if chunk is None:
        raise HTTPException(404, t("e_chunk_missing", language))
    # Guideline text is the cited evidence: always shown in its source language.
    note = t("source_language_note", language) if language == "en" else ""
    if isinstance(chunk, dict):
        return {
            "key": chunk["key"],
            "section": chunk["section_id"],
            "title": chunk["title"],
            "text": chunk["text"],
            "source_note": note,
        }
    return {
        "key": chunk.key,
        "section": chunk.section_id,
        "title": chunk.title,
        "text": chunk.text,
        "source_note": note,
    }


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("digidoc.console.app:app", host=host, port=port)
