"""Canned Draft JSON for MODEL_MODE=mock. Looked up by fixture id or message."""

from __future__ import annotations

import json
from pathlib import Path

from digidoc.draft.schema import Citation, Draft, ICD10, PlanItem, SOAP

FIXTURES = Path(__file__).resolve().parent.parent.parent / "fixtures" / "scenarios.json"


def _cit(key: str, section_id: str) -> Citation:
    return Citation(key=key, section_id=section_id)


def _s1() -> Draft:
    ppk = "KEMENKES_PPK_FKTP_2022"
    c1, c2, c3 = _cit(ppk, "ARI-SYMPTOMATIC"), _cit(ppk, "ARI-NO-ABX"), _cit(ppk, "ARI")
    return Draft(
        mode="plan",
        assessment="ISPA viral pada dewasa: pilek, batuk, nyeri tenggorokan 3 hari tanpa tanda bahaya. Tata laksana simtomatik; tidak ada kriteria infeksi bakteri dari anamnesis ini.",
        differentials=["common cold / ISPA viral", "rinitis alergi", "faringitis"],
        plan=[
            PlanItem(text="Paracetamol untuk nyeri atau demam, dosis per Fornas.", citation=c3, drug="paracetamol"),
            PlanItem(text="Istirahat, cairan, pelembab hidung; chlorpheniramine bila pilek mengganggu, dosis per Fornas.", citation=c1, drug="chlorpheniramine"),
            PlanItem(text="Tidak meresepkan obat anti-bakteri untuk pola common cold 3 hari.", citation=c2, drug=None),
        ],
        soap=SOAP(
            S="Pilek, batuk, nyeri tenggorokan 3 hari. Tidak hamil. Tanpa obat rutin.",
            O="Belum diperiksa.",
            A="ISPA viral (common cold).",
            P="Simtomatik; safety-net sesak/nyeri dada/demam memburuk.",
        ),
        icd10=[ICD10(code="J00", label="Common cold"), ICD10(code="J06.9", label="ISPA atas akut")],
        citations=[c1, c2, c3],
        abstain=False,
        confidence=0.82,
    )


def _s3() -> Draft:
    k = "PERKENI_KAKI_DIABETIK_2021"
    c = _cit(k, "ASSESSMENT")
    return Draft(
        mode="summary",
        assessment="Luka kaki 2 minggu, berbau, pada diabetes dengan metformin tidak teratur dan ramuan herbal. Pemeriksaan langsung wajib (probe-to-bone, kedalaman, nekrosis, pulsus). Tidak menyusun rencana terapi dari teks.",
        differentials=["ulkus diabetikum", "selulitis", "osteomielitis"],
        plan=[],
        soap=SOAP(S="Luka jempol 2 minggu, bau, ramuan herbal, DM.", O="", A="Kaki diabetik, exam-dependent.", P=""),
        icd10=[ICD10(code="E11.6", label="DM dengan komplikasi kaki")],
        citations=[c, _cit(k, "REFERRAL")],
        abstain=False,
        confidence=0.7,
    )


def _s6b() -> Draft:
    c = _cit("KEMENKES_PPK_FKTP_2022", "HEADACHE-RED-FLAGS")
    return Draft(
        mode="summary",
        assessment="Sakit kepala 2 hari dengan edema dan gangguan penglihatan pada perempuan tidak hamil. Perlu tekanan darah dan funduskopi; bukan migrain sampai red flag disingkirkan.",
        differentials=["krisis hipertensi", "migrain dengan aura", "penyebab sekunder"],
        plan=[],
        soap=SOAP(S="Nyeri kepala, bengkak kaki, pandangan kabur. Tidak hamil.", O="", A="Headache red flags.", P=""),
        icd10=[ICD10(code="R51", label="Sakit kepala")],
        citations=[c],
        abstain=False,
        confidence=0.65,
    )


def _s7() -> Draft:
    c = _cit("KEMENKES_PPK_FKTP_2022", "POST-OPERATIVE")
    return Draft(
        mode="summary",
        assessment="Hari ke-10 pasca apendektomi: nyeri luka operasi dan meriang. Mimik infeksi komunitas; SSI, kebocoran, VTE harus disingkirkan bersama tim operator. Tidak ada rencana ISPA.",
        differentials=["SSI", "ileus/kebocoran", "VTE", "infeksi viral"],
        plan=[],
        soap=SOAP(S="Nyeri jahitan, meriang, ops 10 hari lalu.", O="", A="Post-op ≤30d.", P=""),
        icd10=[ICD10(code="T81.4", label="Infeksi pasca prosedur (banding)")],
        citations=[c],
        abstain=False,
        confidence=0.6,
    )


def _s7b() -> Draft:
    c = _cit("KEMENKES_PPK_FKTP_2022", "ARI")
    c2 = _cit("KEMENKES_PPK_FKTP_2022", "FEVER-5D")
    return Draft(
        mode="plan",
        assessment="Meriang 1 hari tanpa operasi, tanpa tanda bahaya dari anamnesis. Simtomatik sambil safety-net.",
        differentials=["prodromal viral", "ISPA awal"],
        plan=[
            PlanItem(text="Paracetamol jika demam atau pegal, dosis per Fornas.", citation=c, drug="paracetamol"),
        ],
        soap=SOAP(S="Meriang 1 hari.", O="", A="Gejala prodromal ringan.", P="Simtomatik."),
        icd10=[ICD10(code="R50.9", label="Demam tidak khas")],
        citations=[c, c2],
        abstain=False,
        confidence=0.7,
    )


def _s9() -> Draft:
    c1 = _cit("KEMENKES_PPK_FKTP_2022", "FEVER-5D")
    c2 = _cit("KEMENKES_TIFOID_2006", "SUSPECT")
    return Draft(
        mode="summary",
        assessment="Meriang/pusing 5 hari; 'masuk angin' tidak dipetakan. Demam ≥5 hari: dengue dan tifoid harus masuk kerja. Jangan menutup sebagai masuk angin.",
        differentials=["dengue", "tifoid", "malaria jika endemis", "TB"],
        plan=[],
        soap=SOAP(S="Tidak enak badan 5 hari, meriang, pusing. Unparsed: masuk angin.", O="", A="Demam berkepanjangan.", P=""),
        icd10=[ICD10(code="R50.9", label="Demam")],
        citations=[c1, c2],
        abstain=False,
        confidence=0.55,
    )


def _s12() -> Draft:
    c = _cit("KEMENKES_PPK_FKTP_2022", "UNDIFFERENTIATED")
    return Draft(
        mode="summary",
        assessment="Lelah, pusing, nafsu makan turun 3 bulan tanpa pola guideline. Abstain dari rencana terapi. Laboratorium dan pemeriksaan untuk menyingkirkan penyebab umum.",
        differentials=["anemia", "tiroid", "diabetes", "TB"],
        plan=[],
        soap=SOAP(S="Fatigue, pusing, anoreksia 90 hari.", O="", A="Undifferentiated chronic.", P=""),
        icd10=[],
        citations=[c],
        abstain=True,
        abstain_reason="Tidak ada pola guideline; labs sebelum rencana.",
        confidence=0.35,
    )


BY_ID = {
    "S1": _s1,
    "S3": _s3,
    "S6b": _s6b,
    "S7": _s7,
    "S7b": _s7b,
    "S9": _s9,
    "S12": _s12,
}


def _table(language: str) -> dict:
    if language == "en":
        from digidoc.draft.canned_en import BY_ID as EN_BY_ID

        return EN_BY_ID
    return BY_ID


def canned_json(needle: str, language: str = "id") -> str:
    table = _table(language)
    if needle in table:
        return table[needle]().model_dump_json()
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    for sc in data["scenarios"]:
        if needle == sc["message"] and sc["id"] in table:
            return table[sc["id"]]().model_dump_json()
        variant = sc.get("variant")
        if variant and needle == variant["message"]:
            vid = variant["name"].split(" ")[0]
            if vid in table:
                return table[vid]().model_dump_json()
    # Unknown mock key: empty summary the parser can still read
    return Draft(
        mode="summary",
        language=language,
        assessment="",
        abstain=True,
        abstain_reason="no canned draft",
    ).model_dump_json()
