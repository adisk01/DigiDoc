"""Safety gate rules.

Every rule is a plain Python predicate over the Intake object. No model is consulted.
A rule can only ADD a hit; nothing in the pipeline can remove one. Rules are evaluated in
listed order and the most severe route wins.

Guideline anchors are cited by document key (see corpus/manifest.json). They exist so a
clinician reviewing this file can check each rule against its source.

Adding a rule = adding an entry here + a fixture in fixtures/scenarios.json. Nothing else.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from digidoc.models import Intake, PregnancyStatus, Route

Predicate = Callable[[Intake], bool]


@dataclass(frozen=True)
class Rule:
    rule_id: str
    name: str
    route: Route
    when: Predicate
    reason: str
    guideline: str
    safety_net_key: str | None = None
    prescreen: tuple[str, ...] = ()
    layer2_modules: tuple[str, ...] = ()
    notes_for_doctor: tuple[str, ...] = ()


def _has(i: Intake, *tags: str) -> bool:
    return any(t in i.symptoms for t in tags)


def _all(i: Intake, *tags: str) -> bool:
    return all(t in i.symptoms for t in tags)


def _cond(i: Intake, c: str) -> bool:
    return c in i.chronic_conditions


# ---------------------------------------------------------------------------
# Emergency — hospital now, pipeline stops
# ---------------------------------------------------------------------------

R01_DENGUE_WARNING = Rule(
    rule_id="R01_DENGUE_WARNING",
    name="Dengue warning signs",
    route=Route.EMERGENCY,
    when=lambda i: (
        _has(i, "fever", "feverish")
        and ((i.fever_days or 0) >= 3 or _has(i, "fever_defervescence"))
        and _has(i, "abdominal_pain_severe", "persistent_vomiting", "petechiae", "bleeding", "lethargy")
    ),
    reason="Fever ≥3 days (or defervescence) with a WHO dengue warning sign",
    guideline="KEMENKES_DBD_2017 §warning-signs; WHO_DENGUE_2009 §2.3",
    safety_net_key="emergency_now",
)

R02_ACUTE_CHEST = Rule(
    rule_id="R02_ACUTE_CHEST",
    name="Acute chest pain",
    route=Route.EMERGENCY,
    when=lambda i: _has(i, "chest_pain", "chest_pain_radiating"),
    reason="Chest pain of any character is not assessable by text; treat as ACS until proven otherwise",
    guideline="PERKI_ACS_2018 §initial-assessment",
    safety_net_key="emergency_now",
)

R02b_DYSPNEA = Rule(
    rule_id="R02b_DYSPNEA",
    name="Difficulty breathing",
    route=Route.EMERGENCY,
    when=lambda i: _has(i, "dyspnea"),
    reason="Dyspnoea needs oxygen saturation measured, which text cannot do",
    guideline="KEMENKES_PPK_FKTP_2022 §red-flags",
    safety_net_key="emergency_now",
)

R14_CONVULSION = Rule(
    rule_id="R14_CONVULSION",
    name="Convulsion",
    route=Route.EMERGENCY,
    when=lambda i: _has(i, "convulsion"),
    reason="Seizure reported",
    guideline="WHO_IMCI_2014 §general-danger-signs; KEMENKES_PPK_FKTP_2022 §red-flags",
    safety_net_key="emergency_now",
)

# ---------------------------------------------------------------------------
# Mental health — immediate human handoff, nothing else generated
# ---------------------------------------------------------------------------

R08_SELF_HARM = Rule(
    rule_id="R08_SELF_HARM",
    name="Self-harm or suicidal ideation signal",
    route=Route.HUMAN_HANDOFF_NOW,
    when=lambda i: _has(i, "self_harm_ideation"),
    reason="Any expression of not wanting to live triggers a human immediately; no triage, no draft",
    guideline="KEMENKES_KESWA_2020 §crisis-response",
    safety_net_key="mental_health_handoff",
)

# ---------------------------------------------------------------------------
# Urgent same day — facility today, no draft
# ---------------------------------------------------------------------------

R03_PREECLAMPSIA = Rule(
    rule_id="R03_PREECLAMPSIA",
    name="Possible preeclampsia",
    route=Route.URGENT_SAME_DAY,
    when=lambda i: (
        i.pregnancy_status in (PregnancyStatus.YES, PregnancyStatus.UNSURE)
        and (i.pregnancy_weeks is None or i.pregnancy_weeks >= 20)
        and _has(i, "headache", "headache_severe")
        and _has(i, "edema", "visual_disturbance", "abdominal_pain_severe")
    ),
    reason="Headache with oedema or visual disturbance after 20 weeks: blood pressure must be measured today",
    guideline="POGI_HDK_2016 §diagnosis; KEMENKES_PNPK_PREEKLAMPSIA",
    safety_net_key="urgent_today",
)

R05_UNDER_TWO = Rule(
    rule_id="R05_UNDER_TWO",
    name="Child under 2 years",
    route=Route.CLINICIAN_REVIEW,
    when=lambda i: i.age_years is not None and i.age_years < 2,
    reason="Under-2s are outside any text-based assessment; IMCI danger-sign intake runs instead",
    guideline="WHO_IMCI_2014 §assess-and-classify",
    safety_net_key="child_under_two",
    prescreen=(
        "Apakah anak bisa minum atau menyusu?",
        "Apakah anak muntah setiap kali diberi makan/minum?",
        "Apakah anak pernah kejang?",
        "Apakah anak lemas, sulit dibangunkan, atau tidak sadar?",
        "Apakah napas anak cepat atau ada tarikan dinding dada?",
    ),
)

R05b_IMCI_DANGER_SIGN = Rule(
    rule_id="R05b_IMCI_DANGER_SIGN",
    name="IMCI general danger sign present",
    route=Route.URGENT_SAME_DAY,
    when=lambda i: (
        i.age_years is not None and i.age_years < 5
        and _has(i, "poor_feeding", "lethargy", "convulsion", "persistent_vomiting")
    ),
    reason="A general danger sign in a child under 5 means same-day facility assessment",
    guideline="WHO_IMCI_2014 §general-danger-signs",
    safety_net_key="urgent_today",
)

R07b_DEVICE_SYMPTOMATIC = Rule(
    rule_id="R07b_DEVICE_SYMPTOMATIC",
    name="Implanted cardiac device with symptoms",
    route=Route.URGENT_SAME_DAY,
    when=lambda i: (
        i.implanted_device in ("pacemaker", "icd", "crt")
        and _has(i, "syncope", "palpitations", "device_shock_felt", "device_site_swelling", "dizziness")
    ),
    reason="Symptomatic device patient is not a routine check; needs same-day interrogation",
    guideline="PERKI_DEVICE_FOLLOWUP §symptomatic-review",
    safety_net_key="urgent_today",
)

# ---------------------------------------------------------------------------
# Specialist route — recognise, pre-screen, route; never draft
# ---------------------------------------------------------------------------

R07_IMPLANTED_DEVICE = Rule(
    rule_id="R07_IMPLANTED_DEVICE",
    name="Implanted cardiac device",
    route=Route.SPECIALIST_ROUTE,
    when=lambda i: i.implanted_device in ("pacemaker", "icd", "crt"),
    reason="Device follow-up requires in-person interrogation; system pre-screens and routes to cardiology",
    guideline="PERKI_DEVICE_FOLLOWUP §routine-interval",
    safety_net_key="device_routing",
    prescreen=(
        "Apakah pernah pusing berat atau pingsan sejak kontrol terakhir?",
        "Apakah jantung terasa berdebar tidak teratur?",
        "Apakah pernah merasakan kejutan/sengatan dari alat?",
        "Apakah ada bengkak, merah, atau nyeri di lokasi alat?",
        "Apakah ada obat baru sejak kontrol terakhir?",
    ),
    notes_for_doctor=("Route to cardiology; attach pre-screen answers.",),
)

# ---------------------------------------------------------------------------
# Clinician review — doctor sees a summary; no plan is drafted
# ---------------------------------------------------------------------------

R04_PREGNANCY = Rule(
    rule_id="R04_PREGNANCY",
    name="Pregnant or unsure",
    route=Route.CLINICIAN_REVIEW,
    when=lambda i: i.pregnancy_status in (PregnancyStatus.YES, PregnancyStatus.UNSURE),
    reason="Pregnancy changes drug safety and the meaning of common symptoms; no drafting",
    guideline="KEMENKES_PPK_FKTP_2022 §special-populations",
    safety_net_key="clinician_review",
    notes_for_doctor=("Pregnant/unsure: check every medication against pregnancy category.",),
)

R06_POST_OP = Rule(
    rule_id="R06_POST_OP",
    name="Surgery within 30 days",
    route=Route.CLINICIAN_REVIEW,
    when=lambda i: i.recent_surgery_days is not None and i.recent_surgery_days <= 30,
    reason="Post-operative presentations mimic routine illness; SSI, leak, and VTE must be excluded by the operating team",
    guideline="KEMENKES_PPK_FKTP_2022 §post-operative; SCOPE_DOC_03 §surgical-limits",
    safety_net_key="clinician_review",
    notes_for_doctor=(
        "Post-op ≤30d. Consider surgical site infection, anastomotic leak, VTE. Contact operating surgeon.",
    ),
)

R09_DIABETIC_FOOT = Rule(
    rule_id="R09_DIABETIC_FOOT",
    name="Foot wound in a diabetic patient",
    route=Route.CLINICIAN_REVIEW,
    when=lambda i: _cond(i, "diabetes") and _has(i, "foot_wound", "wound_nonhealing"),
    reason="Diabetic foot is limb-threatening and exam-dependent; summary for the doctor, no plan",
    guideline="PERKENI_KAKI_DIABETIK_2021 §assessment; IWGDF_2023 §classification",
    safety_net_key="wound_come_in",
    layer2_modules=("diabetic_foot",),
    notes_for_doctor=(
        "Probe-to-bone, depth, necrosis, cellulitis extent, pulses. Consider HbA1c. Ask about topical remedies.",
    ),
)

R10_WOUND_GENERAL = Rule(
    rule_id="R10_WOUND_GENERAL",
    name="Non-healing or foul wound",
    route=Route.CLINICIAN_REVIEW,
    when=lambda i: _has(i, "wound_nonhealing", "wound_foul"),
    reason="Wounds need to be seen",
    guideline="KEMENKES_PPK_FKTP_2022 §wounds",
    safety_net_key="wound_come_in",
)

R11_PROLONGED_FEVER = Rule(
    rule_id="R11_PROLONGED_FEVER",
    name="Fever 5 days or more",
    route=Route.CLINICIAN_REVIEW,
    when=lambda i: _has(i, "fever", "feverish") and (i.fever_days or i.duration_days or 0) >= 5,
    reason="Fever ≥5 days in Indonesia: dengue, typhoid, and TB must be considered with labs",
    guideline="KEMENKES_PPK_FKTP_2022 §fever; KEMENKES_TIFOID_2006",
    safety_net_key="clinician_review",
    notes_for_doctor=("Differentials: dengue (NS1/serology), typhoid (Widal/Tubex/culture), malaria if endemic, TB.",),
)

R12_UNDIFFERENTIATED_CHRONIC = Rule(
    rule_id="R12_UNDIFFERENTIATED_CHRONIC",
    name="Undifferentiated chronic symptoms",
    route=Route.CLINICIAN_REVIEW,
    when=lambda i: (
        (i.duration_days or 0) >= 30
        and _has(i, "fatigue", "dizziness", "appetite_loss")
        and not _has(i, "fever", "cough", "chest_pain", "wound")
    ),
    reason="Weeks of non-specific symptoms have no guideline pattern; drafter must abstain and list what to rule out",
    guideline="SCOPE_DOC_03 §undifferentiated",
    safety_net_key="clinician_review",
    notes_for_doctor=("Consider anaemia, thyroid, diabetes, TB, depression. Labs needed before any plan.",),
)

R13_NEURO_VISUAL = Rule(
    rule_id="R13_NEURO_VISUAL",
    name="Headache with visual disturbance or oedema (non-pregnant)",
    route=Route.CLINICIAN_REVIEW,
    when=lambda i: (
        i.pregnancy_status not in (PregnancyStatus.YES, PregnancyStatus.UNSURE)
        and _has(i, "headache", "headache_severe")
        and _has(i, "visual_disturbance", "edema")
    ),
    reason="Headache with visual change or oedema needs blood pressure and fundoscopy",
    guideline="KEMENKES_PPK_FKTP_2022 §headache-red-flags",
    safety_net_key="clinician_review",
)

# Order matters only for display; severity resolution is by route rank in engine.py
RULES: list[Rule] = [
    R01_DENGUE_WARNING,
    R02_ACUTE_CHEST,
    R02b_DYSPNEA,
    R14_CONVULSION,
    R08_SELF_HARM,
    R03_PREECLAMPSIA,
    R05_UNDER_TWO,
    R05b_IMCI_DANGER_SIGN,
    R07_IMPLANTED_DEVICE,
    R07b_DEVICE_SYMPTOMATIC,
    R04_PREGNANCY,
    R06_POST_OP,
    R09_DIABETIC_FOOT,
    R10_WOUND_GENERAL,
    R11_PROLONGED_FEVER,
    R12_UNDIFFERENTIATED_CHRONIC,
    R13_NEURO_VISUAL,
]
