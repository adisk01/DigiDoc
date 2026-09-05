"""Translate stored clinical models into the static console's view shape.

Everything the app writes itself is rendered in the requested language. Text the model
wrote (draft, Layer 2 narrative) and text from the guideline corpus is shown in the
language it was written in, and labelled when that differs from the interface language.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Iterable

from digidoc.draft.schema import Citation, Draft
from digidoc.gate import i18n as gate_i18n
from digidoc.gate.rules import RULES
from digidoc.i18n import normalise, t
from digidoc.intake.questions import CONF_MIN
from digidoc.models import GateResult, Intake
from digidoc.retrieval import get_chunk as main_chunk
from digidoc.specialist.diabetic_foot.schema import ConsultResult
from digidoc.specialist.registry import get_chunk as specialist_chunk

GUIDELINES = {rule.rule_id: rule.guideline for rule in RULES}
ROUTE_RANK = {
    "emergency": 5,
    "human_handoff_now": 4,
    "urgent_same_day": 3,
    "clinician_review": 2,
    "specialist_route": 1,
    "routine": 0,
}


def _elapsed(iso: str, language: str, long: bool = False) -> str:
    then = datetime.fromisoformat(iso)
    minutes = max(0, int((datetime.now(timezone.utc) - then).total_seconds() / 60))
    return t("minutes_long" if long else "minutes_short", language, n=minutes)


def _who(intake: Intake, language: str) -> str:
    sex = {"m": t("male", language), "f": t("female", language)}.get(intake.sex)
    if intake.age_years is not None and intake.age_years < 1:
        months = t("months_short", language, n=round(intake.age_years * 12))
        return f"{t('infant', language)}, {months}"
    age = f"{intake.age_years:g}" if intake.age_years is not None else None
    parts = [part for part in (sex, age) if part]
    if intake.pregnancy_weeks:
        parts.append(t("pregnant_weeks", language, n=intake.pregnancy_weeks))
    return ", ".join(parts) or t("unknown", language)


def _value(value: Any, language: str, fallback_key: str = "not_asked") -> str:
    if value is None:
        return t(fallback_key, language)
    if isinstance(value, list):
        return " · ".join(str(v) for v in value) if value else t("none_value", language)
    return str(value)


def intake_view(intake: Intake, language: str = "id") -> dict[str, Any]:
    conf = intake.field_confidence
    patient = (
        t("self", language)
        if intake.patient_is_self is True
        else t("other", language)
        if intake.patient_is_self is False
        else t("not_asked", language)
    )
    pregnancy = {
        "yes": "pregnancy_yes",
        "no": "pregnancy_no",
        "unsure": "pregnancy_unsure",
        "na": "pregnancy_na",
    }[intake.pregnancy_status.value]
    if intake.sex == "m":
        # A patient volunteering "tidak hamil" before stating their sex leaves the field set
        # to "no"; reporting that on a male patient reads as a data error to the doctor.
        pregnancy = "pregnancy_na"
    if intake.recent_surgery_days is not None:
        surgery = t("surgery_days_ago", language, n=intake.recent_surgery_days)
    elif conf.get("recent_surgery_days", 0) >= CONF_MIN:
        # The patient was asked and said no. That is different from never having been asked,
        # and the doctor needs to be able to tell which one they are looking at.
        surgery = t("surgery_none", language)
    else:
        surgery = t("surgery_unknown", language)
    duration = (
        t("duration_days", language, n=f"{intake.duration_days:g}")
        if intake.duration_days is not None
        else t("not_asked", language)
    )
    fields = [
        [t("f_patient", language), patient, conf.get("patient_is_self", 0)],
        [t("f_age", language), _value(intake.age_years, language), conf.get("age_years", 0)],
        [
            t("f_sex", language),
            {"m": t("male", language), "f": t("female", language)}.get(intake.sex, t("not_asked", language)),
            conf.get("sex", 0),
        ],
        [t("f_pregnancy", language), t(pregnancy, language), conf.get("pregnancy_status", 0)],
        [t("f_surgery", language), surgery, conf.get("recent_surgery_days", 0)],
        [t("f_device", language), _value(intake.implanted_device, language, "none_value"), conf.get("implanted_device", 0)],
        [t("f_chronic", language), _value(intake.chronic_conditions, language), conf.get("chronic_conditions", 0)],
        [t("f_medications", language), _value(intake.medications, language), conf.get("medications", 0)],
        [t("f_allergies", language), _value(intake.allergies, language), conf.get("allergies", 0)],
        [t("f_complaint", language), _value(intake.chief_complaint, language), conf.get("chief_complaint", 0)],
        [t("f_duration", language), duration, conf.get("duration_days", 0)],
        [t("f_symptoms", language), _value(intake.symptoms, language), conf.get("symptoms", 0)],
    ]
    return {
        "fields": fields,
        "unparsed": intake.unparsed_spans,
        "injected": intake.injected_instructions,
    }


def _lookup_chunk(key: str, section_id: str):
    return main_chunk(key, section_id) or specialist_chunk(key, section_id)


def _citation_view(citation: Citation, language: str) -> dict[str, str]:
    chunk = _lookup_chunk(citation.key, citation.section_id)
    if isinstance(chunk, dict):
        title, text = chunk.get("title") or citation.section_id, chunk.get("text") or ""
    elif chunk is not None:
        title, text = chunk.title, chunk.text
    else:
        title, text = citation.section_id, t("e_chunk_missing", language)
    return {
        "key": citation.key,
        "section": citation.section_id,
        "title": title,
        "text": text,
        "source_note": t("source_language_note", language) if language == "en" else "",
    }


def draft_view(draft: Draft | None, gate: GateResult, language: str = "id") -> dict[str, Any] | None:
    if draft is None or draft.mode in ("none", "degraded"):
        return None
    refs: list[Citation] = []
    for citation in [*draft.citations, *(item.citation for item in draft.plan)]:
        if not any(
            c.key == citation.key and c.section_id == citation.section_id for c in refs
        ):
            refs.append(citation)
    numbers = {(c.key, c.section_id): str(i) for i, c in enumerate(refs, 1)}
    citations = {str(i): _citation_view(c, language) for i, c in enumerate(refs, 1)}
    assessment = draft.assessment
    if assessment and citations and not any(f"[{n}]" in assessment for n in citations):
        assessment += "".join(f"[{n}]" for n in citations)
    return {
        "mode": draft.mode,
        "abstain": draft.abstain,
        "abstain_reason": draft.abstain_reason,
        "confidence": draft.confidence,
        "assessment": assessment,
        "differentials": draft.differentials,
        "examine": [gate_i18n.note(n, language) for n in gate.notes_for_doctor],
        "plan": [
            {
                "text": item.text,
                "cite": numbers[(item.citation.key, item.citation.section_id)],
            }
            for item in draft.plan
        ],
        "soap": draft.soap.model_dump(),
        "icd10": [item.model_dump() for item in draft.icd10],
        "citations": citations,
        "language_note": (
            t("draft_language_note", language) if draft.language != language else ""
        ),
    }


def queue_view(rows: Iterable[Any], language: str = "id") -> list[dict[str, Any]]:
    language = normalise(language)
    items = []
    for row in rows:
        intake = Intake.model_validate_json(row["intake_json"])
        gate = GateResult.model_validate_json(row["gate_json"])
        draft = Draft.model_validate_json(row["draft_json"]) if row["draft_json"] else None
        items.append(
            {
                "id": row["id"],
                "route": gate.route.value,
                "who": _who(intake, language),
                "age": _elapsed(row["created_at"], language),
                "degraded": bool(draft and draft.mode == "degraded"),
                "_created": row["created_at"],
            }
        )
    items.sort(key=lambda item: (-ROUTE_RANK[item["route"]], item["_created"]))
    for item in items:
        item.pop("_created")
    return items


def case_view(row: Any, action_rows: Iterable[Any], language: str = "id") -> dict[str, Any]:
    language = normalise(language)
    intake = Intake.model_validate_json(row["intake_json"])
    gate = GateResult.model_validate_json(row["gate_json"])
    draft = Draft.model_validate_json(row["draft_json"]) if row["draft_json"] else None
    hits = []
    for hit in gate.hits:
        name, reason = gate_i18n.rule_text(hit.rule_id, hit.name, hit.reason, language)
        hits.append(
            {
                **hit.model_dump(mode="json"),
                "name": name,
                "reason": reason,
                "guideline": GUIDELINES.get(hit.rule_id, "—"),
            }
        )
    return {
        "id": row["id"],
        "route": gate.route.value,
        "who": _who(intake, language),
        "age": _elapsed(row["created_at"], language, long=True),
        "signed": (
            {"by": row["signed_by"], "at": _clock(row["signed_at"])}
            if row["signed_by"]
            else None
        ),
        "degraded": bool(draft and draft.mode == "degraded"),
        "message": row["message"],
        "hits": hits,
        "notes": [gate_i18n.note(n, language) for n in gate.notes_for_doctor],
        "prescreen": [
            f"{gate_i18n.prescreen(q, language)} — {t('unanswered', language)}"
            for q in gate.prescreen
        ],
        "intake": intake_view(intake, language),
        "draft": draft_view(draft, gate, language),
        "layer2": {
            "available": gate.layer2_modules,
            "result": (
                consult_view(json.loads(row["consult_json"]), language)
                if row["consult_json"]
                else None
            ),
        },
        "log": [_action_view(action, gate, language) for action in action_rows],
    }


def _clock(iso: str) -> str:
    return datetime.fromisoformat(iso).astimezone().strftime("%H:%M")


def _action_view(row: Any, gate: GateResult, language: str) -> dict[str, str]:
    if row["action"] == "created":
        what = t(
            "a_created",
            language,
            route=gate.route.value,
            safety_net=gate.safety_net_key,
        )
    else:
        what = t(f"a_{row['action']}", language)
    actor = row["actor"]
    if actor == "sistem":
        actor = t("actor_system", language)
    return {"t": _clock(row["created_at"]), "who": actor, "what": what}


def consult_view(data: dict[str, Any], language: str = "id") -> dict[str, Any]:
    result = ConsultResult.model_validate(data)
    refs = []
    for item in result.start_now:
        cit = item.citation
        if not any(c.key == cit.key and c.section_id == cit.section_id for c in refs):
            refs.append(cit)
    numbers = {(c.key, c.section_id): str(i) for i, c in enumerate(refs, 1)}
    citations = {}
    for i, cit in enumerate(refs, 1):
        raw = specialist_chunk(cit.key, cit.section_id) or {}
        citations[str(i)] = {
            "key": cit.key,
            "section": cit.section_id,
            "title": raw.get("title", cit.section_id) if isinstance(raw, dict) else cit.section_id,
            "text": raw.get("text", "") if isinstance(raw, dict) else "",
            "source_note": t("source_language_note", language) if language == "en" else "",
        }
    return {
        "module": result.module,
        "grade": result.grade.model_dump(),
        "referral": result.referral,
        "referral_reason": result.referral_reason,
        "override": result.override,
        "model_said": result.model_said,
        "start_now": [
            {"text": item.text, "cite": numbers[(item.citation.key, item.citation.section_id)]}
            for item in result.start_now
        ],
        "referral_letter_points": result.referral_letter_points,
        "citations": citations,
        "language_note": (
            t("draft_language_note", language) if result.language != language else ""
        ),
    }
