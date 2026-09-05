"""Canonical symptom tags.

The intake model maps free text (Bahasa, Javanese, mixed) onto these tags. The gate only
ever sees tags, never prose. Keeping the vocabulary small and explicit is what makes the
gate auditable: a clinician can read this file and the rules file and know exactly what
fires and why.
"""

SYMPTOM_TAGS: dict[str, str] = {
    # general
    "fever": "demam",
    "fever_defervescence": "demam turun mendadak setelah beberapa hari",
    "feverish": "meriang / sumeng",
    "fatigue": "mudah lelah",
    "dizziness": "pusing",
    "appetite_loss": "nafsu makan turun",
    "lethargy": "lemas / tidak responsif",
    "syncope": "pingsan",
    # respiratory
    "cough": "batuk",
    "sore_throat": "sakit tenggorokan",
    "rhinorrhea": "pilek",
    "dyspnea": "sesak napas",
    # cardiac
    "chest_pain": "nyeri dada",
    "chest_pain_radiating": "nyeri dada menjalar ke lengan/rahang",
    "diaphoresis": "keringat dingin",
    "palpitations": "jantung berdebar",
    "device_shock_felt": "merasakan kejutan dari alat",
    "device_site_swelling": "bengkak di lokasi alat",
    # GI / dengue
    "abdominal_pain": "sakit perut",
    "abdominal_pain_severe": "sakit perut hebat",
    "persistent_vomiting": "muntah terus-menerus (>=3x)",
    "petechiae": "bintik merah di kulit",
    "bleeding": "perdarahan (gusi, hidung, BAB hitam)",
    # neuro / pregnancy
    "headache": "sakit kepala",
    "headache_severe": "sakit kepala hebat",
    "visual_disturbance": "pandangan kabur",
    "edema": "bengkak kaki/tangan/wajah",
    "convulsion": "kejang",
    # wounds
    "wound": "luka",
    "wound_nonhealing": "luka tidak sembuh >=14 hari",
    "wound_foul": "luka berbau",
    "foot_wound": "luka di kaki",
    "surgical_site_pain": "nyeri di bekas operasi",
    # paediatric (IMCI danger signs)
    "poor_feeding": "tidak mau minum/menyusu",
    # mental health
    "self_harm_ideation": "ingin mengakhiri hidup / tidak ingin hidup",
    "hopelessness": "merasa tidak berguna / putus asa",
}

CHRONIC_CONDITIONS: set[str] = {
    "diabetes", "hypertension", "asthma", "copd", "ckd", "heart_failure",
    "coronary_disease", "tb_on_treatment", "hiv", "cancer", "epilepsy",
}

IMPLANTED_DEVICES: set[str] = {"pacemaker", "icd", "crt", "stent", "insulin_pump"}
