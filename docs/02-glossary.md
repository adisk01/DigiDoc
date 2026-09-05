# 02 — Glossary

Every term used across these documents. Written for someone with no Indonesian
healthcare background. **Read this one first if the others feel dense.**

---

## A. Indonesian health system — the payer and the money

**BPJS Kesehatan**
The single national health insurer. A government body, not a private company. It runs
**JKN** and covers the large majority of Indonesians. Think of it as the NHS's budget
combined with a single-payer insurance claims operation. *Why you care: BPJS decides
what gets reimbursed, and therefore what a clinic can afford to do.*

**JKN (Jaminan Kesehatan Nasional)**
"National Health Insurance." The scheme itself. BPJS Kesehatan is the body that
administers JKN.

**PBI (Penerima Bantuan Iuran)**
Subsidised members — people whose premiums the government pays. A large share of
enrolment. Relevant because deactivating PBI members shrinks BPJS's contribution base.

**Capitation (kapitasi)**
How BPJS pays **primary care** providers: a fixed amount per registered member per month,
regardless of how many times that member visits. One cited rate is around IDR 8,000
per member per month.
*Why this is the single most important concept in this project:* under capitation, an
extra visit is pure **cost**, not revenue. So a clinic's profit is driven by cost per
covered life. **Anything that reduces clinician minutes per patient is direct margin.**
This is the entire economic engine of the proposal.

**INA-CBG (Indonesian Case Base Groups)**
How BPJS pays **hospitals**: a fixed tariff per case, grouped by diagnosis and severity.
It is Indonesia's version of DRG (Diagnosis-Related Groups). The hospital gets the
group's tariff whether the case cost more or less.
*Why you care:* the group assigned depends on the diagnosis codes recorded. Bad coding
means the hospital is paid for a lighter case than it actually treated. **Coding accuracy
is revenue.**

**Claim ratio**
Claims paid ÷ premiums collected. Above 100% means the insurer is paying out more than
it takes in. BPJS's ratio reached roughly 111.86% in early 2026.

**Fornas (Formularium Nasional)**
The national formulary — the official list of drugs BPJS will reimburse. A drug outside
Fornas means the patient pays cash.
*Why you care:* an AI that suggests clinically correct but non-reimbursed drugs creates
a bill the patient did not expect. A formulary check is cheap to build and immediately
demonstrates local fluency.

**Out-of-pocket (OOP)**
What patients pay directly. Historically a large share of Indonesian health spending.

---

## B. Indonesian health system — the facilities

**Puskesmas (Pusat Kesehatan Masyarakat)**
Community health centre. The backbone of public primary care. Roughly 10,000 nationwide,
each serving on the order of 25,000–30,000 people. Typically staffed with a GP, nurses,
midwives, a nutritionist.
*Why you care:* many operate short-staffed or without a doctor. This is where the access
gap physically lives.

**Poskesdes**
Village health post. A Puskesmas satellite, often run by the village midwife.

**Posyandu**
Community-run health post, staffed by volunteer community health workers (**kader**).
Mostly maternal and child health.

**RSUD (Rumah Sakit Umum Daerah)**
Regional public general hospital.

**Fasyankes (Fasilitas Pelayanan Kesehatan)**
Umbrella term: "healthcare facility." You will see it constantly in Indonesian
regulation.

**SIMRS (Sistem Informasi Manajemen Rumah Sakit)**
Hospital Management Information System — the local term for a hospital's core IT/EMR
system. Highly fragmented across vendors, which is exactly why integration is painful.

**Referral system (rujukan)**
Tiered gatekeeping. Patients start at primary care; only referred cases reach hospitals.
Bypassing it is generally not reimbursed.

---

## C. Regulation and data

**Kemenkes (Kementerian Kesehatan)**
The Ministry of Health.

**SATUSEHAT**
Indonesia's national health data exchange platform, run by Kemenkes. Previously called
IHS (Indonesia Health Service). Built on **HL7 FHIR R4**, with a FHIR server, terminology
server, master data server and developer hub. Hospitals are mandated to push clinical
encounter data to it.
*Why you care:* it is both the compliance stick and the integration opportunity.
Practitioner accounts put typical hospital integration at 12–19 weeks.

**HL7 FHIR (Fast Healthcare Interoperability Resources)**
The international standard for exchanging health data. Defines data objects called
**resources** (Patient, Encounter, Condition, Observation, Medication) and a REST API to
move them. Pronounced "fire." R4 is the version SATUSEHAT uses.
*Practical gotchas from field reports:* SATUSEHAT requires ISO 8601 datetimes with
timezone (`2026-04-04T10:30:00+07:00`), and validates against **ICD-10 WHO**, not
ICD-10-CM — some ICD-10-CM codes simply do not exist there.

**Permenkes**
"Peraturan Menteri Kesehatan" — a Ministry of Health regulation. Cited by number and
year. **Permenkes 20/2019** governs telemedicine between health facilities.
**Permenkes 24/2022** is the electronic medical records regulation that underpins the
SATUSEHAT mandate.

**UU 17/2023 (Health Omnibus Law)**
The 2023 Health Law. Consolidated a large amount of prior health legislation and
explicitly recognises telehealth and telemedicine.

**PP 28/2024**
"Peraturan Pemerintah" — the Government Regulation implementing UU 17/2023.

**UU 27/2022 (PDP Law)**
Indonesia's Personal Data Protection law. Broadly GDPR-shaped. Health data is sensitive
personal data. Legal commentary notes the framework remains relatively untested in
telemedicine specifically — which is a reason for caution, not a reason to ignore it.

**STR (Surat Tanda Registrasi)**
A doctor's registration certificate. Practising requires a valid one.

**Stranas KA**
Indonesia's National AI Strategy (2020–2045). Alongside MOCI Circular Letter 9/2023 on
AI ethics, it is guidance rather than binding sectoral AI law. **As of this writing there
is no Indonesian equivalent of the EU AI Act's binding medical-AI regime.** Design as if
one is coming.

---

## D. Clinical and local-context terms

**Masuk angin**
Literally "wind entering." A culture-bound complaint with no direct clinical equivalent —
covers bloating, chills, aches, fatigue, general malaise. Extremely common presenting
complaint.
*Why you care:* an English-trained model maps this to nothing useful. Handling it
correctly is the single highest-credibility moment available in a demo.

**Panas dalam**
"Inner heat." Sore throat, mouth ulcers, a feeling of internal heat.

**Meriang**
Feverish, chills-and-aches, feeling unwell without a confirmed fever.

**Jamu**
Traditional Indonesian herbal medicine. Widely used, frequently alongside prescribed
drugs, and frequently not disclosed to the doctor. Worth an interaction check.

**Red flag**
A symptom that signals a possible emergency requiring immediate escalation regardless of
what else is going on. Examples: crushing chest pain radiating to the arm or jaw, sudden
unilateral weakness or speech loss, dengue warning signs, preeclampsia features in
pregnancy, signs of sepsis in an infant.
*Why you care:* red flags must be handled by deterministic code, never by model
judgement alone. This is the core safety commitment.

**Triage**
Sorting patients by urgency: emergency / urgent / routine / self-care. Distinct from
diagnosis. **Triage is the safety-critical task; diagnosis is the useful one.**

**Differential diagnosis**
The ranked list of conditions that could explain the presentation. Not one answer — a
list.

**SOAP note**
The standard clinical note format: **S**ubjective (what the patient reports),
**O**bjective (findings, vitals, labs), **A**ssessment (clinical impression),
**P**lan (what happens next).

**ICD-10**
The international diagnosis coding system. Note the WHO vs CM distinction above.

**IMCI (Integrated Management of Childhood Illness)**
WHO protocol for managing common childhood illness in low-resource settings, designed to
be usable by non-physician health workers.

**PNPK (Pedoman Nasional Pelayanan Kedokteran)**
Indonesian National Clinical Practice Guidelines, issued by Kemenkes. **These are the
primary retrieval corpus** — not UpToDate, not US guidelines.

**Over-triage / under-triage**
Over-triage: sending a low-risk patient to emergency care unnecessarily. Wastes money,
erodes trust. Under-triage: failing to escalate a genuine emergency. **Under-triage can
kill people.** The two errors are not symmetric and must not be optimised as if they were.

---

## E. Technical terms in this build

**RAG (Retrieval-Augmented Generation)**
Instead of relying on model memory, retrieve relevant source passages from a document
store and feed them into the prompt. The model answers *from the retrieved text*.
*Why:* clinical guidance must be traceable to a citable source, and guidelines change.

**Chunking**
Splitting source documents into retrievable passages. Chunk badly and you split a
dosing table from its header, and the model confidently reads the wrong row.

**Embedding / vector search**
Text is converted to a numeric vector; similar meanings sit close together. Retrieval
finds nearest neighbours. **pgvector** adds this to Postgres so you don't need a separate
vector database.

**Groundedness / citation grounding**
Does every clinical claim in the output actually trace to a retrieved passage? Ungrounded
claims are hallucinations wearing a citation.

**Hallucination**
Fluent, confident, wrong. In clinical settings the fluency is what makes it dangerous.

**Abstention**
The system declining to answer and escalating instead. **An abstention rate of zero is a
red flag, not an achievement** — it means the system never recognises its own limits.

**Human-in-the-loop (HITL)**
A person reviews and approves before anything takes effect. Here: the doctor signs.

**Sensitivity vs specificity**
Sensitivity = of all true emergencies, what fraction did we catch? Specificity = of all
non-emergencies, what fraction did we correctly leave alone?
*For red flags, prioritise sensitivity, accept worse specificity, and report both.*

**Deterministic rules layer**
Plain code — `if` statements — not a model. Same input always gives the same output.
Used for red flags because it is auditable, testable, and cannot be talked out of its
answer by a persuasive prompt.

**Eval harness**
Automated test suite for AI output: a fixed set of cases, expected behaviour, scored
automatically, run on every change. **In clinical AI, this is the product.**

**Clinical vignette**
A short written case used for testing. "32-year-old woman, 3 days fever, retro-orbital
pain, petechiae, platelets falling." Expected output specified in advance.

**p95 latency**
The response time that 95% of requests come in under. Averages hide the bad tail; p95
doesn't.

**ASR / WER**
Automatic Speech Recognition. Word Error Rate is how it's scored. Bahasa Indonesia ASR
degrades on regional accents and Indonesian-English code-switching — measure it, don't
assume it.

**CDSS (Clinical Decision Support System)**
Software that helps clinicians decide — drug interaction alerts, guideline prompts,
differential suggestions. A regulated category in many jurisdictions.

**Ambient scribe**
Listens to the consultation and drafts the clinical note automatically.

---

## E2. Terms from the human-layer analysis

**Automation complacency**
The well-documented tendency of a human supervisor to stop attending carefully to
automation that is usually right. **It gets worse as the system gets better**, which is
why draft accuracy alone is never a sufficient safety argument.

**Safety-netting**
Plain-language instructions given to a patient about what would mean "come back
immediately" — issued at intake, before any review, because the illness does not pause
while the case sits in a queue.

**Loop closure**
Making sure an ordered investigation actually gets read and acted on. The failure —
"orphaned results" — is a leading category in real clinical negligence claims and one
prototypes never model.

**Degraded mode**
Defined behaviour when a dependency fails. Here it always means *less* autonomy: intake
stays open, drafting stops, cases route to humans.

**SLA (Service Level Agreement)**
The maximum time a case may wait per triage tier. In this system the queue is a clinical
object, not a UX detail, so an SLA breach pages someone rather than passing quietly.

**Task-shifting**
Moving clinical tasks to less specialised staff — nurses, midwives — usually under remote
supervision. The proposed answer to the absent-doctor case, and a **scope-of-practice**
question rather than a documentation one, which is why it needs separate legal design.

**Inter-rater agreement**
How often two clinicians reviewing the same case reach the same conclusion. If reviewers
disagree, "a doctor signed it" is a weaker guarantee than it sounds, and the ground truth
in your eval set isn't ground truth.

**Multi-morbidity / polypharmacy**
Several conditions at once / many concurrent medications. Guidelines are written
per-disease; patients are not. This is where single-disease retrieval is least useful and
most confidently wrong.

**Model drift**
The hosted model's behaviour changing because the provider updated it. Silent unless the
eval suite runs **on a schedule**, not just on deploy.

**ASA grade**
Anaesthetic risk classification used in pre-operative assessment. Listed here as an
example of data the system does not hold and therefore must not reason about.

---

## F. Business terms

**EBITDA**
Earnings Before Interest, Taxes, Depreciation and Amortisation. The standard proxy for
operating profit. **PE firms value companies as a multiple of EBITDA**, so a dollar of
EBITDA improvement is worth many dollars of enterprise value.

**Multiple expansion**
The valuation multiple itself rising — because the business is now more scalable, more
defensible, or growing faster. AI transformation stories are sold on this.

**Portfolio company / portco**
A business owned by the PE fund.

**Add-on acquisition**
A smaller business bought and folded into an existing portfolio company. Relevant because
a system built once can be deployed across every add-on — the roll-out argument.

**Sponsor**
The PE firm that owns the business.
