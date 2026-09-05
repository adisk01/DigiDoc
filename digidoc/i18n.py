"""Static console strings in Bahasa Indonesia and English.

Display text only. Nothing in this file changes a route, a rule, a citation, or a
clinical claim — those are decided in code and shown in whichever language they were
written in. Adding a language = adding a column here, not a model call.
"""

from __future__ import annotations

LANGUAGES = ("id", "en")
DEFAULT_LANGUAGE = "id"

STRINGS: dict[str, dict[str, str]] = {
    "id": {
        # relative time and patient line
        "minutes_short": "{n} mnt",
        "minutes_long": "{n} menit yang lalu",
        "infant": "Bayi",
        "months_short": "{n} bln",
        "pregnant_weeks": "hamil {n} mgg",
        "male": "Laki-laki",
        "female": "Perempuan",
        "unknown": "—",
        # intake values
        "not_asked": "Belum ditanya",
        "none_value": "Tidak ada",
        "self": "Diri sendiri",
        "other": "Orang lain",
        "pregnancy_yes": "Hamil",
        "pregnancy_no": "Tidak hamil",
        "pregnancy_unsure": "Tidak yakin",
        "pregnancy_na": "Tidak berlaku",
        "surgery_days_ago": "{n} hari lalu",
        "surgery_none": "Tidak ada",
        "surgery_unknown": "Belum diketahui",
        "duration_days": "{n} hari",
        "unanswered": "Belum dijawab",
        # intake field labels
        "f_patient": "Pasien",
        "f_age": "Usia",
        "f_sex": "Jenis kelamin",
        "f_pregnancy": "Kehamilan",
        "f_surgery": "Operasi ≤30 hari",
        "f_device": "Alat implan",
        "f_chronic": "Penyakit kronis",
        "f_medications": "Obat",
        "f_allergies": "Alergi",
        "f_complaint": "Keluhan utama",
        "f_duration": "Durasi",
        "f_symptoms": "Gejala",
        # action log
        "a_accept": "Terima draf",
        "a_edit": "Ubah draf",
        "a_reject": "Tolak draf",
        "a_sign": "Tanda tangan · kasus dibekukan",
        "a_consult": "Konsul spesialis",
        "a_created": "Kasus dibuat · rute: {route} · pesan safety-net terkirim ({safety_net})",
        "actor_system": "sistem",
        # language provenance
        "source_language_note": "Teks sumber dalam Bahasa Indonesia.",
        "draft_language_note": "Draf ini ditulis dalam bahasa Inggris.",
        # errors
        "e_case_not_found": "Kasus tidak ditemukan.",
        "e_case_frozen": "Kasus sudah ditandatangani dan dibekukan.",
        "e_doctor_required": "doctor_id wajib untuk tanda tangan.",
        "e_no_draft": "Kasus ini tidak memiliki draf untuk diubah.",
        "e_invalid_draft": "Format draf tidak valid: {detail}",
        "e_module_unavailable": "Modul spesialis tidak tersedia untuk kasus ini.",
        "e_consult_done": "Konsul spesialis sudah dijalankan untuk kasus ini.",
        "e_invalid_findings": "Temuan pemeriksaan tidak valid: {detail}",
        "e_chunk_missing": "Chunk sumber tidak ditemukan.",
    },
    "en": {
        "minutes_short": "{n} min",
        "minutes_long": "{n} minutes ago",
        "infant": "Infant",
        "months_short": "{n} mo",
        "pregnant_weeks": "{n} weeks pregnant",
        "male": "Male",
        "female": "Female",
        "unknown": "—",
        "not_asked": "Not asked",
        "none_value": "None",
        "self": "Themselves",
        "other": "Someone else",
        "pregnancy_yes": "Pregnant",
        "pregnancy_no": "Not pregnant",
        "pregnancy_unsure": "Unsure",
        "pregnancy_na": "Not applicable",
        "surgery_days_ago": "{n} days ago",
        "surgery_none": "None",
        "surgery_unknown": "Not established",
        "duration_days": "{n} days",
        "unanswered": "Not answered",
        "f_patient": "Patient",
        "f_age": "Age",
        "f_sex": "Sex",
        "f_pregnancy": "Pregnancy",
        "f_surgery": "Surgery ≤30 days",
        "f_device": "Implanted device",
        "f_chronic": "Chronic conditions",
        "f_medications": "Medicines",
        "f_allergies": "Allergies",
        "f_complaint": "Chief complaint",
        "f_duration": "Duration",
        "f_symptoms": "Symptoms",
        "a_accept": "Draft accepted",
        "a_edit": "Draft edited",
        "a_reject": "Draft rejected",
        "a_sign": "Signed · case frozen",
        "a_consult": "Specialist consult",
        "a_created": "Case created · route: {route} · safety-net message sent ({safety_net})",
        "actor_system": "system",
        "source_language_note": "Source text is in Bahasa Indonesia.",
        "draft_language_note": "This draft was written in Bahasa Indonesia.",
        "e_case_not_found": "Case not found.",
        "e_case_frozen": "This case is signed and frozen.",
        "e_doctor_required": "doctor_id is required to sign.",
        "e_no_draft": "This case has no draft to edit.",
        "e_invalid_draft": "Invalid draft format: {detail}",
        "e_module_unavailable": "That specialist module is not available for this case.",
        "e_consult_done": "A specialist consult has already been run for this case.",
        "e_invalid_findings": "Invalid examination findings: {detail}",
        "e_chunk_missing": "Source chunk not found.",
    },
}


def normalise(language: str | None) -> str:
    lang = (language or "").strip().lower()
    return lang if lang in LANGUAGES else DEFAULT_LANGUAGE


def t(key: str, language: str = DEFAULT_LANGUAGE, **fmt: object) -> str:
    table = STRINGS[normalise(language)]
    text = table.get(key) or STRINGS[DEFAULT_LANGUAGE].get(key, key)
    return text.format(**fmt) if fmt else text
