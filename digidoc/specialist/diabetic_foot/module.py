"""Diabetic foot Layer 2: grade and referral in code; model writes narrative only."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from digidoc.llm import ModelUnavailable, complete
from digidoc.models import GateResult, Intake
from digidoc.specialist.diabetic_foot.schema import (
    Citation,
    ConsultResult,
    ExamFindings,
    Grade,
    StartNowItem,
)

CORPUS_DIR = Path(__file__).resolve().parent / "corpus"
CORPUS_KEY = "LAYER2_DIABETIC_FOOT"
HEADING = re.compile(r"^## \[([^\]]+)\]\s*(.*)$")

SYSTEM = """You advise an Indonesian GP on a diabetic foot exam already graded in code.
Do not change Wagner grade or referral. Write JSON only:
narrative ({narrative_language}, mention Wagner and referral), referral (routine|urgent|emergency),
start_now: [{{text, citation: {{key, section_id}}}}] citing only provided chunks,
referral_letter_points (list of strings), confidence (0-1).
Every start_now item needs a citation into the provided chunks. No doses; say dosis per Fornas.
"""

NARRATIVE_LANGUAGE = {
    "id": "Bahasa Indonesia",
    "en": "English; the guideline chunks stay in Bahasa Indonesia and are cited unchanged",
}

# Wagner criteria and referral reasons are computed in code, so both renderings live here.
CRITERIA = {
    "superficial": {"id": "ulkus superfisial", "en": "superficial ulcer"},
    "probe_superficial": {
        "id": "probe-to-bone dilaporkan; grade mengikuti kedalaman superfisial",
        "en": "probe-to-bone reported; grade follows the superficial depth",
    },
    "probe_positive": {"id": "probe-to-bone positif", "en": "probe-to-bone positive"},
    "deep": {"id": "ulkus dalam", "en": "deep ulcer"},
    "to_bone": {"id": "kedalaman sampai tulang", "en": "depth reaching bone"},
    "necrotic": {"id": "jaringan nekrotik", "en": "necrotic tissue"},
}

REASON = {
    "systemic": {
        "id": "Wagner {g}: tanda sistemik — rujuk emergensi.",
        "en": "Wagner {g}: systemic signs — emergency referral.",
    },
    "deep": {
        "id": "Wagner {g}: luka dalam dan/atau nekrosis — rujuk urgent, bukan rawat jalan biasa.",
        "en": "Wagner {g}: deep wound and/or necrosis — urgent referral, not routine outpatient care.",
    },
    "pulses": {
        "id": "Wagner {g}: nadi tidak teraba (iskemia) — rujuk urgent.",
        "en": "Wagner {g}: pulses not palpable (ischaemia) — urgent referral.",
    },
    "cellulitis": {
        "id": "Wagner {g}: selulitis luas — rujuk urgent.",
        "en": "Wagner {g}: extensive cellulitis — urgent referral.",
    },
    "routine": {
        "id": "Wagner {g}: ulkus superfisial tanpa nekrosis — rawat di primer dengan follow-up.",
        "en": "Wagner {g}: superficial ulcer without necrosis — manage in primary care with follow-up.",
    },
}


@lru_cache(maxsize=1)
def load_chunks() -> list[dict]:
    chunks: list[dict] = []
    for path in sorted(CORPUS_DIR.glob("*.md")):
        current_id, title, buf = None, "", []
        for line in path.read_text(encoding="utf-8").splitlines():
            m = HEADING.match(line)
            if m:
                if current_id is not None:
                    chunks.append(
                        {"key": CORPUS_KEY, "section_id": current_id, "title": title, "text": "\n".join(buf).strip()}
                    )
                current_id, title, buf = m.group(1), m.group(2).strip(), []
            elif current_id is not None:
                buf.append(line)
        if current_id is not None:
            chunks.append(
                {"key": CORPUS_KEY, "section_id": current_id, "title": title, "text": "\n".join(buf).strip()}
            )
    return chunks


def get_chunk(key: str, section_id: str) -> dict | None:
    for c in load_chunks():
        if c["key"] == key and c["section_id"].lower() == section_id.lower():
            return c
    return None


def wagner_and_referral(f: ExamFindings, language: str = "id") -> tuple[Grade, str, str]:
    lang = language if language in ("id", "en") else "id"
    crit = lambda key: CRITERIA[key][lang]  # noqa: E731
    reason = lambda key, g: REASON[key][lang].format(g=g)  # noqa: E731

    criteria: list[str] = []
    if f.depth == "superficial" and not f.necrotic_tissue:
        criteria.append(crit("superficial"))
        if f.probe_to_bone:
            criteria.append(crit("probe_superficial"))
        grade = Grade(value="1", criteria_met=criteria)
    elif f.depth == "to_bone" or f.probe_to_bone or (f.depth == "deep" and f.necrotic_tissue):
        if f.probe_to_bone:
            criteria.append(crit("probe_positive"))
        if f.depth == "deep":
            criteria.append(crit("deep"))
        if f.depth == "to_bone":
            criteria.append(crit("to_bone"))
        if f.necrotic_tissue:
            criteria.append(crit("necrotic"))
        grade = Grade(value="3", criteria_met=criteria)
    elif f.depth == "deep":
        criteria.append(crit("deep"))
        grade = Grade(value="2", criteria_met=criteria)
    else:
        criteria.append(crit("superficial"))
        grade = Grade(value="1", criteria_met=criteria)

    if f.systemic_signs:
        return grade, "emergency", reason("systemic", grade.value)
    if f.depth in ("deep", "to_bone") or f.necrotic_tissue:
        return grade, "urgent", reason("deep", grade.value)
    if not f.pulses_palpable:
        return grade, "urgent", reason("pulses", grade.value)
    if f.cellulitis_cm >= 5:
        return grade, "urgent", reason("cellulitis", grade.value)
    return grade, "routine", reason("routine", grade.value)


def _parse_model(raw: str, chunks: list[dict]) -> dict:
    data = json.loads(raw.strip())
    by_id = {(c["key"], c["section_id"].lower()): c for c in chunks}
    items: list[StartNowItem] = []
    for row in data.get("start_now") or []:
        cit = row.get("citation") or {}
        hit = by_id.get((cit.get("key", ""), str(cit.get("section_id", "")).lower()))
        if not hit:
            continue
        items.append(
            StartNowItem(
                text=row["text"],
                citation=Citation(key=hit["key"], section_id=hit["section_id"]),
            )
        )
    return {
        "narrative": str(data.get("narrative") or ""),
        "referral": data.get("referral"),
        "start_now": items,
        "points": [str(p) for p in (data.get("referral_letter_points") or [])],
        "confidence": float(data.get("confidence") or 0.0),
    }


def consult(
    intake: Intake,
    gate: GateResult,
    findings: ExamFindings | dict,
    language: str = "id",
) -> ConsultResult:
    language = language if language in NARRATIVE_LANGUAGE else "id"
    f = findings if isinstance(findings, ExamFindings) else ExamFindings.model_validate(findings)
    grade, referral, reason = wagner_and_referral(f, language)
    chunks = load_chunks()
    model_blob: dict | None = None
    try:
        raw = complete(
            SYSTEM.format(narrative_language=NARRATIVE_LANGUAGE[language]),
            json.dumps(
                {
                    "intake": intake.model_dump(mode="json"),
                    "gate_route": gate.route.value,
                    "findings": f.model_dump(),
                    "code_grade": grade.model_dump(),
                    "code_referral": referral,
                    "chunks": chunks,
                },
                ensure_ascii=False,
            ),
            json_schema=None,
            mock_key=f"layer2:{language}:diabetic_foot",
        )
        model_blob = _parse_model(raw, chunks)
    except (ModelUnavailable, json.JSONDecodeError, KeyError, TypeError, ValueError):
        model_blob = None

    override, model_said = False, None
    start_now: list[StartNowItem] = []
    points: list[str] = []
    narrative = ""
    confidence = 0.0
    if model_blob:
        narrative = model_blob["narrative"]
        start_now = model_blob["start_now"]
        points = model_blob["points"]
        confidence = model_blob["confidence"]
        stated = model_blob["referral"]
        if stated and stated != referral:
            override, model_said = True, str(stated)
    citations = []
    for item in start_now:
        cit = item.citation
        if not any(c.key == cit.key and c.section_id == cit.section_id for c in citations):
            citations.append(cit)
    return ConsultResult(
        language=language,
        grade=grade,
        referral=referral,  # type: ignore[arg-type]
        referral_reason=reason,
        narrative=narrative,
        start_now=start_now,
        referral_letter_points=points,
        citations=citations,
        confidence=confidence,
        override=override,
        model_said=model_said,
    )
