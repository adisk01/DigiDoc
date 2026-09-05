"""Static Bahasa follow-up questions. The model never writes these."""

from __future__ import annotations

from digidoc.models import Intake, PregnancyStatus

CONF_MIN = 0.6

# First missing field in this order is the one we ask.
QUESTION_ORDER: list[str] = [
    "patient_is_self",
    "age_years",
    "sex",
    "pregnancy_status",
    "chief_complaint",
    "duration_days",
    "chronic_conditions",
    "medications",
    "allergies",
    "recent_surgery_days",
    "implanted_device",
]

QUESTIONS: dict[str, str] = {
    "patient_is_self": (
        "Keluhan ini untuk Bapak/Ibu sendiri, atau untuk orang lain (anak/keluarga)?"
    ),
    "age_years": (
        "Berapa usia pasien? Sebutkan dalam tahun (untuk bayi, sebutkan dalam bulan)."
    ),
    "sex": "Apa jenis kelamin pasien (laki-laki atau perempuan)?",
    "pregnancy_status": "Apakah pasien sedang hamil, tidak hamil, atau tidak yakin?",
    "chief_complaint": "Apa keluhan utamanya saat ini?",
    "duration_days": "Sudah berapa hari keluhan ini berlangsung?",
    "chronic_conditions": (
        "Apakah ada penyakit menahun (misalnya diabetes, hipertensi, asma)? "
        "Jika tidak ada, jawab tidak."
    ),
    "medications": (
        "Obat apa yang sedang dikonsumsi, termasuk jamu atau ramuan? "
        "Jika tidak ada, jawab tidak."
    ),
    "allergies": "Apakah ada alergi obat atau makanan? Jika tidak ada, jawab tidak.",
    "recent_surgery_days": (
        "Apakah pasien menjalani operasi dalam 90 hari terakhir? "
        "Jika ya, berapa hari yang lalu? Jika tidak, jawab tidak."
    ),
    "implanted_device": (
        "Apakah pasien memakai alat tanam (pacemaker, ICD, stent, pompa insulin)? "
        "Jika ya, sebutkan jenisnya. Jika tidak, jawab tidak."
    ),
    "background": (
        "Terakhir, mohon jawab dalam satu pesan: (1) penyakit menahun seperti diabetes, "
        "hipertensi, asma; (2) obat rutin termasuk jamu; (3) alergi obat atau makanan; "
        "(4) operasi dalam 90 hari terakhir; (5) alat tanam seperti pacemaker atau stent. "
        "Sebutkan \"tidak ada\" untuk yang tidak ada."
    ),
}

# Asked as one message when only these are left: five separate turns is a lot to put a
# patient through, and the answers are usually a single "none".
BACKGROUND_FIELDS: tuple[str, ...] = (
    "chronic_conditions",
    "medications",
    "allergies",
    "recent_surgery_days",
    "implanted_device",
)

QUESTIONS_EN: dict[str, str] = {
    "patient_is_self": "Is this concern for you, or for someone else (a child or family member)?",
    "age_years": "How old is the patient? Give years, or months for a baby.",
    "sex": "What is the patient's sex (male or female)?",
    "pregnancy_status": "Is the patient pregnant, not pregnant, or unsure?",
    "chief_complaint": "What is the main concern right now?",
    "duration_days": "How many days has this concern been present?",
    "chronic_conditions": (
        "Does the patient have any long-term conditions, such as diabetes, hypertension, "
        "or asthma? If none, answer none."
    ),
    "medications": (
        "What medicines are currently being taken, including herbal remedies? "
        "If none, answer none."
    ),
    "allergies": "Are there any medicine or food allergies? If none, answer none.",
    "recent_surgery_days": (
        "Has the patient had surgery in the last 90 days? If yes, how many days ago? "
        "If not, answer no."
    ),
    "implanted_device": (
        "Does the patient have an implanted device such as a pacemaker, ICD, stent, "
        "or insulin pump? If yes, name it; otherwise answer no."
    ),
    "background": (
        "Last one, please answer in a single message: (1) long-term conditions such as "
        "diabetes, hypertension, or asthma; (2) regular medicines including herbal ones; "
        "(3) medicine or food allergies; (4) surgery in the last 90 days; (5) implanted "
        "devices such as a pacemaker or stent. Say \"none\" for anything that does not apply."
    ),
}

QUESTION_TRANSLATIONS = {
    QUESTIONS[key]: QUESTIONS_EN[key] for key in (*QUESTION_ORDER, "background")
}


def translate_question(question: str | None, language: str) -> str | None:
    if question is None or language != "en":
        return question
    return QUESTION_TRANSLATIONS.get(question, question)


def _conf(intake: Intake, field: str) -> float:
    return float(intake.field_confidence.get(field, 0.0))


def _known_value(intake: Intake, field: str) -> bool:
    if _conf(intake, field) < CONF_MIN:
        return False
    val = getattr(intake, field)
    if field in ("age_years", "sex", "chief_complaint", "duration_days"):
        return val is not None
    if field == "patient_is_self":
        return val is not None
    # lists / optional "none" fields: high confidence is enough (empty/None = no)
    return True


def _pregnancy_required(intake: Intake) -> bool:
    if intake.sex != "f" or intake.age_years is None:
        return False
    return 12 <= intake.age_years <= 55


def missing_mandatory(intake: Intake) -> list[str]:
    missing: list[str] = []
    for field in QUESTION_ORDER:
        if field == "pregnancy_status":
            if not _pregnancy_required(intake):
                continue
            if intake.pregnancy_status == PregnancyStatus.NA or _conf(intake, field) < CONF_MIN:
                missing.append(field)
            continue
        if not _known_value(intake, field):
            missing.append(field)
    return missing


def _candidates(intake: Intake) -> list[tuple[str, tuple[str, ...]]]:
    missing = missing_mandatory(intake)
    out: list[tuple[str, tuple[str, ...]]] = [
        (QUESTIONS[field], (field,)) for field in missing if field not in BACKGROUND_FIELDS
    ]
    background = tuple(field for field in missing if field in BACKGROUND_FIELDS)
    if len(background) > 1:
        # The background question lists its parts in this order, so the fields must match it.
        out.append((QUESTIONS["background"], BACKGROUND_FIELDS))
    elif background:
        out.append((QUESTIONS[background[0]], background))
    return out


def next_prompt(
    intake: Intake, asked: frozenset[str] = frozenset()
) -> tuple[str | None, tuple[str, ...]]:
    """The next unasked question plus the fields it asks about.

    The fields travel with the question because a bare reply ("none", "3 days") only means
    something against the question that prompted it; extraction needs both. Questions in
    `asked` are skipped: the patient has already answered them once, so repeating them cannot
    produce anything new and the gate treats what is still missing as an intake gap.
    """
    for question, fields in _candidates(intake):
        if question not in asked:
            return question, fields
    return None, ()


def next_question(intake: Intake) -> str | None:
    """Bahasa question for the first missing mandatory field, or None if complete."""
    return next_prompt(intake)[0]
