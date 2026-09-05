"""Canned Layer-2 model JSON for MODEL_MODE=mock."""

from __future__ import annotations

import json

KEY = "LAYER2_DIABETIC_FOOT"


def canned_json(_needle: str, language: str = "id") -> str:
    if language == "en":
        return _english()
    return json.dumps(
        {
            "referral": "urgent",
            "narrative": (
                "Temuan sesuai Wagner 3 (ulkus dalam, probe-to-bone, nekrosis). "
                "Perlu rujuk fasilitas yang dapat merawat kaki diabetik, bukan observasi chat."
            ),
            "start_now": [
                {
                    "text": "Offloading: hindari beban pada kaki yang terkena.",
                    "citation": {"key": KEY, "section_id": "OFFLOADING"},
                },
                {
                    "text": "Hentikan ramuan herbal; rawat luka steril. Antibiotik Fornas hanya setelah dokter memilih, dosis per Fornas.",
                    "citation": {"key": KEY, "section_id": "ANTIBIOTICS"},
                },
                {
                    "text": "Periksa GDS dan HbA1c hari ini; tinjau kepatuhan metformin.",
                    "citation": {"key": KEY, "section_id": "GLYCAEMIC"},
                },
            ],
            "referral_letter_points": [
                "Ulkus jempol, durasi 14 hari, ramuan herbal topikal",
                "Probe-to-bone, nekrosis, kedalaman dalam, selulitis terukur",
                "Nadi teraba; tidak ada tanda sistemik pada temuan ini",
                "Mohon rujuk untuk penilaian osteomielitis / Wagner dan tata laksana lanjutan",
            ],
            "confidence": 0.8,
        },
        ensure_ascii=False,
    )


def _english() -> str:
    return json.dumps(
        {
            "referral": "urgent",
            "narrative": (
                "Findings correspond to Wagner 3 (deep ulcer, probe-to-bone, necrosis). "
                "Refer to a facility able to manage diabetic foot; this is not for chat observation."
            ),
            "start_now": [
                {
                    "text": "Offloading: keep weight off the affected foot.",
                    "citation": {"key": KEY, "section_id": "OFFLOADING"},
                },
                {
                    "text": "Stop the herbal remedy; sterile wound care. Fornas antibiotics only once the doctor selects them, dose per Fornas.",
                    "citation": {"key": KEY, "section_id": "ANTIBIOTICS"},
                },
                {
                    "text": "Check random blood glucose and HbA1c today; review metformin adherence.",
                    "citation": {"key": KEY, "section_id": "GLYCAEMIC"},
                },
            ],
            "referral_letter_points": [
                "Big-toe ulcer, 14 days, topical herbal remedy",
                "Probe-to-bone, necrosis, deep, cellulitis measured",
                "Pulses palpable; no systemic signs in these findings",
                "Please assess for osteomyelitis / Wagner grade and ongoing management",
            ],
            "confidence": 0.8,
        },
        ensure_ascii=False,
    )
