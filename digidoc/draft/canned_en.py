"""English canned drafts for MODEL_MODE=mock.

Same clinical content as canned.py, written in English so an English-language demo shows
an English draft without a model call. Citation keys and section ids are identical; the
guideline chunks they point at stay in their source language.
"""

from __future__ import annotations

from digidoc.draft.schema import Citation, Draft, ICD10, PlanItem, SOAP


def _cit(key: str, section_id: str) -> Citation:
    return Citation(key=key, section_id=section_id)


def _s1() -> Draft:
    ppk = "KEMENKES_PPK_FKTP_2022"
    c1, c2, c3 = _cit(ppk, "ARI-SYMPTOMATIC"), _cit(ppk, "ARI-NO-ABX"), _cit(ppk, "ARI")
    return Draft(
        mode="plan",
        language="en",
        assessment="Viral upper respiratory infection in an adult: runny nose, cough, and sore throat for three days with no danger signs. Symptomatic management; this history meets no bacterial infection criteria.",
        differentials=["common cold / viral URTI", "allergic rhinitis", "pharyngitis"],
        plan=[
            PlanItem(text="Paracetamol for pain or fever, dose per Fornas.", citation=c3, drug="paracetamol"),
            PlanItem(text="Rest, fluids, nasal moisturisation; chlorpheniramine if the runny nose is troublesome, dose per Fornas.", citation=c1, drug="chlorpheniramine"),
            PlanItem(text="Do not prescribe antibacterials for a three-day common cold pattern.", citation=c2, drug=None),
        ],
        soap=SOAP(
            S="Runny nose, cough, sore throat for three days. Not pregnant. No regular medicines.",
            O="Not yet examined.",
            A="Viral URTI (common cold).",
            P="Symptomatic; safety-net for breathlessness, chest pain, worsening fever.",
        ),
        icd10=[ICD10(code="J00", label="Common cold"), ICD10(code="J06.9", label="Acute upper respiratory infection")],
        citations=[c1, c2, c3],
        abstain=False,
        confidence=0.82,
    )


def _s3() -> Draft:
    k = "PERKENI_KAKI_DIABETIK_2021"
    c = _cit(k, "ASSESSMENT")
    return Draft(
        mode="summary",
        language="en",
        assessment="Two-week foul-smelling foot wound in a diabetic patient on irregular metformin who has applied a herbal remedy. In-person examination is mandatory (probe-to-bone, depth, necrosis, pulses). No treatment plan can be built from text.",
        differentials=["diabetic foot ulcer", "cellulitis", "osteomyelitis"],
        plan=[],
        soap=SOAP(S="Big-toe wound for two weeks, foul, herbal remedy applied, diabetes.", O="", A="Diabetic foot, examination-dependent.", P=""),
        icd10=[ICD10(code="E11.6", label="Diabetes with foot complication")],
        citations=[c, _cit(k, "REFERRAL")],
        abstain=False,
        confidence=0.7,
    )


def _s6b() -> Draft:
    c = _cit("KEMENKES_PPK_FKTP_2022", "HEADACHE-RED-FLAGS")
    return Draft(
        mode="summary",
        language="en",
        assessment="Two-day headache with oedema and visual disturbance in a non-pregnant woman. Blood pressure and fundoscopy are needed; this is not migraine until red flags are excluded.",
        differentials=["hypertensive crisis", "migraine with aura", "secondary causes"],
        plan=[],
        soap=SOAP(S="Headache, swollen feet, blurred vision. Not pregnant.", O="", A="Headache red flags.", P=""),
        icd10=[ICD10(code="R51", label="Headache")],
        citations=[c],
        abstain=False,
        confidence=0.65,
    )


def _s7() -> Draft:
    c = _cit("KEMENKES_PPK_FKTP_2022", "POST-OPERATIVE")
    return Draft(
        mode="summary",
        language="en",
        assessment="Day 10 after appendectomy: surgical wound pain and feeling feverish. This mimics a community infection; surgical site infection, leak, and VTE must be excluded with the operating team. No URTI plan.",
        differentials=["surgical site infection", "ileus/leak", "VTE", "viral infection"],
        plan=[],
        soap=SOAP(S="Sore stitches, feverish, surgery 10 days ago.", O="", A="Post-op ≤30 days.", P=""),
        icd10=[ICD10(code="T81.4", label="Post-procedural infection (differential)")],
        citations=[c],
        abstain=False,
        confidence=0.6,
    )


def _s7b() -> Draft:
    c = _cit("KEMENKES_PPK_FKTP_2022", "ARI")
    c2 = _cit("KEMENKES_PPK_FKTP_2022", "FEVER-5D")
    return Draft(
        mode="plan",
        language="en",
        assessment="One day of feeling feverish, no surgery, no danger signs in this history. Symptomatic care with a safety net.",
        differentials=["viral prodrome", "early URTI"],
        plan=[
            PlanItem(text="Paracetamol for fever or aches, dose per Fornas.", citation=c, drug="paracetamol"),
        ],
        soap=SOAP(S="Feverish for one day.", O="", A="Mild prodromal symptoms.", P="Symptomatic."),
        icd10=[ICD10(code="R50.9", label="Fever, unspecified")],
        citations=[c, c2],
        abstain=False,
        confidence=0.7,
    )


def _s9() -> Draft:
    c1 = _cit("KEMENKES_PPK_FKTP_2022", "FEVER-5D")
    c2 = _cit("KEMENKES_TIFOID_2006", "SUSPECT")
    return Draft(
        mode="summary",
        language="en",
        assessment="Five days of feeling feverish and dizzy; 'masuk angin' was not mapped to a tag. Fever of five days or more means dengue and typhoid must be worked up. Do not close this as 'masuk angin'.",
        differentials=["dengue", "typhoid", "malaria if endemic", "TB"],
        plan=[],
        soap=SOAP(S="Unwell for five days, feverish, dizzy. Unparsed: masuk angin.", O="", A="Prolonged fever.", P=""),
        icd10=[ICD10(code="R50.9", label="Fever")],
        citations=[c1, c2],
        abstain=False,
        confidence=0.55,
    )


def _s12() -> Draft:
    c = _cit("KEMENKES_PPK_FKTP_2022", "UNDIFFERENTIATED")
    return Draft(
        mode="summary",
        language="en",
        assessment="Three months of fatigue, dizziness, and reduced appetite with no guideline pattern. Abstaining from a treatment plan. Laboratory work and examination are needed to exclude common causes.",
        differentials=["anaemia", "thyroid disease", "diabetes", "TB"],
        plan=[],
        soap=SOAP(S="Fatigue, dizziness, anorexia for 90 days.", O="", A="Undifferentiated chronic.", P=""),
        icd10=[],
        citations=[c],
        abstain=True,
        abstain_reason="No guideline pattern; laboratory results before any plan.",
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
