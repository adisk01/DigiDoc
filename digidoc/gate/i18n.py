"""Display translations for gate output.

rules.py is the source of truth and is written in English so a reviewer can grep it.
This file only carries the Bahasa Indonesia rendering of each rule's name and reason,
the Bahasa doctor notes, and the English rendering of the Bahasa pre-screen questions.
Nothing here can add, remove, or re-route a hit — it is read after the gate has decided.
"""

from __future__ import annotations

RULE_TEXT_ID: dict[str, tuple[str, str]] = {
    "R01_DENGUE_WARNING": (
        "Tanda bahaya dengue",
        "Demam ≥3 hari (atau fase defervescence) dengan tanda bahaya dengue WHO",
    ),
    "R02_ACUTE_CHEST": (
        "Nyeri dada akut",
        "Nyeri dada apa pun tidak dapat dinilai lewat teks; anggap ACS sampai terbukti bukan",
    ),
    "R02b_DYSPNEA": (
        "Sesak napas",
        "Sesak memerlukan pengukuran saturasi oksigen, yang tidak bisa dilakukan lewat teks",
    ),
    "R14_CONVULSION": ("Kejang", "Dilaporkan kejang"),
    "R08_SELF_HARM": (
        "Sinyal menyakiti diri atau pikiran bunuh diri",
        "Setiap ungkapan tidak ingin hidup langsung memanggil manusia; tanpa triase, tanpa draf",
    ),
    "R03_PREECLAMPSIA": (
        "Kemungkinan preeklampsia",
        "Sakit kepala dengan edema atau gangguan penglihatan setelah 20 minggu: tekanan darah harus diukur hari ini",
    ),
    "R05_UNDER_TWO": (
        "Anak di bawah 2 tahun",
        "Anak di bawah 2 tahun di luar jangkauan penilaian berbasis teks; intake tanda bahaya MTBS dijalankan",
    ),
    "R05b_IMCI_DANGER_SIGN": (
        "Tanda bahaya umum MTBS",
        "Tanda bahaya umum pada anak di bawah 5 tahun berarti penilaian fasilitas hari ini",
    ),
    "R07_IMPLANTED_DEVICE": (
        "Alat pacu jantung tertanam",
        "Kontrol alat memerlukan interogasi langsung; sistem melakukan pra-skrining lalu merujuk ke kardiologi",
    ),
    "R07b_DEVICE_SYMPTOMATIC": (
        "Alat pacu jantung dengan gejala",
        "Pasien alat yang bergejala bukan kontrol rutin; perlu interogasi hari ini",
    ),
    "R04_PREGNANCY": (
        "Hamil atau tidak yakin",
        "Kehamilan mengubah keamanan obat dan makna gejala umum; tidak ada drafting",
    ),
    "R06_POST_OP": (
        "Operasi dalam 30 hari",
        "Keluhan pasca operasi menyerupai penyakit biasa; SSI, kebocoran, dan VTE harus disingkirkan oleh tim operator",
    ),
    "R09_DIABETIC_FOOT": (
        "Luka kaki pada pasien diabetes",
        "Kaki diabetik mengancam tungkai dan bergantung pemeriksaan; ringkasan untuk dokter, tanpa rencana",
    ),
    "R10_WOUND_GENERAL": ("Luka tidak sembuh atau berbau", "Luka harus dilihat langsung"),
    "R11_PROLONGED_FEVER": (
        "Demam 5 hari atau lebih",
        "Demam ≥5 hari di Indonesia: dengue, tifoid, dan TB harus dipertimbangkan dengan laboratorium",
    ),
    "R12_UNDIFFERENTIATED_CHRONIC": (
        "Gejala kronis tidak terdiferensiasi",
        "Gejala non-spesifik berminggu-minggu tidak punya pola guideline; drafter harus abstain dan mendaftar yang perlu disingkirkan",
    ),
    "R13_NEURO_VISUAL": (
        "Sakit kepala dengan gangguan penglihatan atau edema (tidak hamil)",
        "Sakit kepala dengan perubahan penglihatan atau edema perlu tekanan darah dan funduskopi",
    ),
}

NOTE_ID: dict[str, str] = {
    "Route to cardiology; attach pre-screen answers.": (
        "Rujuk ke kardiologi; lampirkan jawaban pra-skrining."
    ),
    "Pregnant/unsure: check every medication against pregnancy category.": (
        "Hamil/tidak yakin: periksa setiap obat terhadap kategori kehamilan."
    ),
    "Post-op ≤30d. Consider surgical site infection, anastomotic leak, VTE. Contact operating surgeon.": (
        "Pasca operasi ≤30 hari. Pertimbangkan infeksi luka operasi, kebocoran anastomosis, VTE. "
        "Hubungi dokter bedah operator."
    ),
    "Probe-to-bone, depth, necrosis, cellulitis extent, pulses. Consider HbA1c. Ask about topical remedies.": (
        "Probe-to-bone, kedalaman, nekrosis, luas selulitis, pulsus. Pertimbangkan HbA1c. "
        "Tanyakan ramuan yang dioleskan."
    ),
    "Differentials: dengue (NS1/serology), typhoid (Widal/Tubex/culture), malaria if endemic, TB.": (
        "Banding: dengue (NS1/serologi), tifoid (Widal/Tubex/kultur), malaria bila endemis, TB."
    ),
    "Consider anaemia, thyroid, diabetes, TB, depression. Labs needed before any plan.": (
        "Pertimbangkan anemia, tiroid, diabetes, TB, depresi. Laboratorium diperlukan sebelum rencana apa pun."
    ),
}

PRESCREEN_EN: dict[str, str] = {
    # WHO IMCI danger signs (R05_UNDER_TWO)
    "Apakah anak bisa minum atau menyusu?": "Is the child able to drink or breastfeed?",
    "Apakah anak muntah setiap kali diberi makan/minum?": (
        "Does the child vomit everything they eat or drink?"
    ),
    "Apakah anak pernah kejang?": "Has the child had a seizure?",
    "Apakah anak lemas, sulit dibangunkan, atau tidak sadar?": (
        "Is the child lethargic, difficult to wake, or unconscious?"
    ),
    "Apakah napas anak cepat atau ada tarikan dinding dada?": (
        "Is the child breathing fast, or is there chest indrawing?"
    ),
    # Cardiac device pre-screen (R07_IMPLANTED_DEVICE)
    "Apakah pernah pusing berat atau pingsan sejak kontrol terakhir?": (
        "Any severe dizziness or fainting since the last check?"
    ),
    "Apakah jantung terasa berdebar tidak teratur?": "Any irregular heartbeat or palpitations?",
    "Apakah pernah merasakan kejutan/sengatan dari alat?": (
        "Have you felt a shock from the device?"
    ),
    "Apakah ada bengkak, merah, atau nyeri di lokasi alat?": (
        "Any swelling, redness, or pain at the device site?"
    ),
    "Apakah ada obat baru sejak kontrol terakhir?": (
        "Any new medicines since the last check?"
    ),
}


def rule_text(rule_id: str, name: str, reason: str, language: str) -> tuple[str, str]:
    """Bahasa rendering of a rule hit, or the English original from rules.py."""
    if language != "id":
        return name, reason
    return RULE_TEXT_ID.get(rule_id, (name, reason))


def note(text: str, language: str) -> str:
    return NOTE_ID.get(text, text) if language == "id" else text


def prescreen(question: str, language: str) -> str:
    return PRESCREEN_EN.get(question, question) if language == "en" else question
