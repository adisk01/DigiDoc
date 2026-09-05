"""Draft for the doctor. Mode is chosen in code, never by the model."""

from __future__ import annotations

import json
import os

from digidoc.draft.checks import apply_failures, check
from digidoc.draft.schema import Draft, SOAP
from digidoc.llm import ModelUnavailable, complete
from digidoc.models import GateResult, Intake, Route
from digidoc.retrieval.index import Chunk

NO_GENERATE = {
    Route.EMERGENCY,
    Route.URGENT_SAME_DAY,
    Route.HUMAN_HANDOFF_NOW,
    Route.SPECIALIST_ROUTE,  # fixtures + rules: never draft
}

PLAN_SYSTEM = """You write a guideline-cited draft for a licensed Indonesian GP. {language_line} Not for the patient.
Every clinical claim must use a citation (key, section_id) from the provided chunks only. No citation, no claim.
Plan items: drug names from Fornas if any; write "dosis per Fornas" never a number. Do not invent doses.
JSON only matching the Draft schema (assessment, differentials, plan, soap, icd10, citations, abstain, abstain_reason, confidence). Do not set mode.
{icd_line}
Do not mention antibiotics for viral URTI / common cold / ISPA without bacterial criteria.
"""

SUMMARY_SYSTEM = """You write a summary for a licensed Indonesian GP. {language_line} Not for the patient.
Do not write a plan; write assessment, differentials to rule out, and what the doctor should examine or order.
Every clinical claim must cite a provided chunk (key, section_id). SOAP.P must be empty. plan must be [].
JSON only matching Draft (assessment, differentials, plan, soap, icd10, citations, abstain, abstain_reason, confidence). Do not set mode.
{icd_line}
If the presentation is undifferentiated chronic symptoms, set abstain true.
"""

# The code is what the clinic bills and reports on, so the doctor should be editing a
# candidate rather than typing one from scratch. Format is dictated by checks.ICD_RE: a
# code outside it fails the draft, so the shape is spelled out here.
ICD_LINE = (
    "icd10: give at least one code for the assessment, as {\"code\": ..., \"label\": ...}. "
    "Format is a letter, two digits, and an optional one or two decimal digits (J06.9, E11.4, "
    "A90) — nothing else validates. Prefer the specific code when the intake supports it and "
    "the category code when it does not; do not code a diagnosis the assessment does not state. "
    "Leave icd10 empty only when abstaining."
)

LANGUAGE_LINE = {
    "id": "Write assessment, differentials, SOAP, and plan text in Bahasa Indonesia.",
    "en": (
        "Write assessment, differentials, SOAP, and plan text in English. "
        "Guideline chunks are in Bahasa Indonesia; cite them unchanged and do not translate "
        "the citation keys or section ids."
    ),
}


def _model_mode() -> str:
    return os.environ.get("MODEL_MODE", "mock").strip().lower()


def choose_mode(gate: GateResult, chunks: list[Chunk]) -> str:
    if _model_mode() == "off":
        if gate.route in NO_GENERATE:
            return "none"
        return "degraded"
    if gate.route in NO_GENERATE:
        return "none"
    if gate.route == Route.ROUTINE:
        if not chunks:
            return "summary"
        return "plan"
    if gate.route in (Route.CLINICIAN_REVIEW,):
        return "summary"
    return "summary"


def _empty(
    mode: str,
    *,
    abstain: bool = False,
    reason: str | None = None,
    language: str = "id",
) -> Draft:
    return Draft(
        mode=mode,
        language=language,
        soap=SOAP(),
        abstain=abstain,
        abstain_reason=reason,
        confidence=0.0,
    )


def _chunk_block(chunks: list[Chunk]) -> str:
    lines = []
    for c in chunks:
        lines.append(f"[{c.key} / {c.section_id}] {c.title}\n{c.text}")
    return "\n\n".join(lines)


def _user(intake: Intake, gate: GateResult, chunks: list[Chunk]) -> str:
    return json.dumps(
        {
            "intake": intake.model_dump(mode="json"),
            "gate_hits": [h.model_dump(mode="json") for h in gate.hits],
            "gate_route": gate.route.value,
            "notes_for_doctor": gate.notes_for_doctor,
            "chunks": [
                {"key": c.key, "section_id": c.section_id, "title": c.title, "text": c.text}
                for c in chunks
            ],
        },
        ensure_ascii=False,
    )


def _parse(raw: str) -> Draft:
    text = raw.strip()
    if text.startswith("```"):
        raise ValueError("fenced output")
    data = json.loads(text)
    data.setdefault("mode", "summary")
    data.setdefault("soap", {})
    return Draft.model_validate(data)


def draft(
    intake: Intake,
    gate: GateResult,
    chunks: list[Chunk],
    language: str = "id",
) -> Draft:
    language = language if language in LANGUAGE_LINE else "id"
    mode = choose_mode(gate, chunks)
    if mode == "none":
        return _empty("none", language=language)
    if mode == "degraded":
        return _empty(
            "degraded",
            abstain=True,
            reason="Model unavailable; case queued for the doctor with raw intake. No partial draft.",
            language=language,
        )
    if mode == "summary" and gate.route == Route.ROUTINE and not chunks:
        return _empty(
            "summary",
            abstain=True,
            reason="Empty retrieval; cannot draft a plan.",
            language=language,
        )

    template = PLAN_SYSTEM if mode == "plan" else SUMMARY_SYSTEM
    system = template.format(language_line=LANGUAGE_LINE[language], icd_line=ICD_LINE)
    try:
        raw = complete(
            system,
            _user(intake, gate, chunks),
            json_schema=Draft.model_json_schema(),
            mock_key=f"draft:{language}:{intake.raw_message}",
        )
    except ModelUnavailable:
        return _empty(
            "degraded",
            abstain=True,
            reason="Model unavailable; case queued for the doctor with raw intake. No partial draft.",
            language=language,
        )

    try:
        parsed = _parse(raw)
    except Exception:
        return _empty(
            "degraded",
            abstain=True,
            reason="Draft parse failure; queued with raw intake.",
            language=language,
        )

    parsed.mode = mode
    parsed.language = language
    if mode == "summary":
        parsed.plan = []
        parsed.soap.P = ""
    if any(h.rule_id == "R12_UNDIFFERENTIATED_CHRONIC" for h in gate.hits):
        parsed.abstain = True
        parsed.abstain_reason = parsed.abstain_reason or "Undifferentiated chronic; no guideline plan."

    reasons = check(parsed, intake, chunks, mode)
    return apply_failures(parsed, reasons)
