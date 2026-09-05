# 03 — Scope & Boundaries

**Question this answers:** where does "digital doctor" logic break down, and what am I
deliberately refusing to build?

A system that claims it can handle everything is a system nobody should deploy. This
document is the most important one in the set. **Knowing the edges is the senior skill.**

---

## Part 1 — Structural limits: what the modality itself cannot do

These are not model quality problems. **No amount of better AI fixes them**, because the
information required never reaches the system.

### 1.1 No physical examination

An asynchronous text consultation cannot palpate an abdomen, auscultate a chest,
percuss, check skin turgor, assess gait, or test a reflex. A large fraction of primary
care diagnosis depends on the hands.

*Concrete failure:* appendicitis. Rebound tenderness and guarding are examination
findings. A text intake reporting "stomach pain, 2 days, some nausea" is compatible with
gastroenteritis, constipation, ovarian torsion, ectopic pregnancy, and appendicitis. **The
system cannot distinguish these, and must not pretend to.**

*Design response:* the intake classifies presentations as **exam-dependent**, and for
these the output is a structured pre-consultation summary plus a recommendation to be
seen — never an assessment and plan.

### 1.2 No vitals, no labs, no imaging

Blood pressure, temperature, oxygen saturation, heart rate, respiratory rate. Sepsis,
shock, hypertensive emergency and hypoxia are defined by numbers the system does not
have. Patient-reported "I feel hot" is not a temperature.

*Design response:* treat every vital as unknown-unless-supplied. Never impute. Where a
vital would change the decision, say so explicitly and route to a facility that can
measure it.

### 1.3 The undifferentiated presentation

Real primary care is dominated by vague, multi-system complaints. "Tired for three
months." "Dizzy sometimes." "Not myself." These resolve through longitudinal observation
and clinical pattern recognition, not through a single structured intake.

*Design response:* explicitly out of scope for autonomous drafting. Route to a doctor
with a summary. **This is a large fraction of real volume and pretending otherwise
inflates every metric in the deck.**

### 1.4 Rare disease and the long tail

Retrieval-grounded systems are strong on what is documented and common. They are weakest
exactly where a knowledgeable doctor adds the most value: the atypical presentation of a
rare condition. Worse, the system's confidence does not drop appropriately in these
cases.

*Design response:* a novelty check. Presentations that match no guideline pattern well
should trigger abstention and escalation, not a low-confidence guess.

### 1.5 Paediatrics, especially infants

Infants do not report symptoms. Deterioration is fast, and the presentation is
non-specific — a septic neonate may present as "not feeding well" and "sleepy."

*Design response:* **hard age gate.** Under 2 years old, no autonomous drafting.
Structured intake against IMCI danger signs, then straight to a clinician. Non-negotiable.

### 1.6 Mental health and self-harm risk

Risk assessment requires rapport, tone, hesitation, and the things a person doesn't say.
Text intake is a poor channel and the failure mode is catastrophic.

*Design response:* out of scope for autonomous handling. Detect, do not assess. Any
indication of self-harm or crisis routes immediately to a human clinician and to
Indonesian crisis resources. **No triage score, no draft plan, no automated response
beyond immediate human handoff.**

### 1.7 Obstetrics

Pregnancy changes the meaning of nearly every symptom. Preeclampsia, ectopic pregnancy,
and placental abruption are time-critical and can present subtly. Indonesia's maternal
mortality burden makes this a high-consequence area.

*Design response:* pregnancy status is a mandatory intake field for any patient of
reproductive age. If pregnant or unsure, escalate thresholds sharply and restrict
autonomous drafting.

### 1.8 Anything requiring a controlled substance or a procedure

Out of scope on principle. Not a technical constraint — a governance one.

**Expanded in [09](09-hitl-and-pathway-limits.md) Part 1** — surgical decision-making,
post-operative presentations (which look deceptively routine), oncology, trauma and
other procedural domains each need their own boundary, not one shared line.

---

## Part 2 — Indonesia-specific failure modes

These are the ones that separate a generic global product from something that actually
works here.

### 2.1 Language, register, and code-switching

Bahasa Indonesia in clinical settings mixes formal Indonesian, colloquial Jakarta speech,
regional languages (Javanese, Sundanese, Batak, Minang and many more), and English
medical loanwords — often inside one sentence. Add SMS-style abbreviation and typos.

*Failure:* a symptom described in Javanese is silently dropped from the extracted
structure. The pipeline continues confidently on incomplete information.

*Design response:* extraction confidence scoring per field. Unparsed spans are surfaced
verbatim to the reviewing doctor rather than silently discarded. **Never let the
structure be more confident than the input.**

### 2.2 Culture-bound complaints

*Masuk angin*, *panas dalam*, *meriang* have no clean clinical mapping. They can mean
almost nothing, or they can be how a patient describes the prodrome of dengue, typhoid,
or an acute coronary event.

*Failure mode A:* dismiss as benign. Miss a serious illness.
*Failure mode B:* map each to a long differential. Over-triage everything, destroy trust,
flood the clinic.

*Design response:* these are treated as **entry points requiring mandatory structured
follow-up questions**, not as symptoms with a mapping. The follow-ups are what carry the
signal.

### 2.3 Local disease burden that global models under-weight

A model trained predominantly on Western data systematically under-weights:

- **Tuberculosis** — Indonesia carries one of the world's largest burdens. A chronic
  cough is a fundamentally different prior here than in London.
- **Dengue** — endemic, seasonal, with specific WHO warning signs. The dangerous phase
  begins as the fever falls, which is counterintuitive to a patient and to a naive model.
- **Typhoid**, **malaria** in eastern provinces, **leptospirosis** post-flooding.

*Design response:* geography- and season-aware priors. The evaluation set deliberately
over-samples these conditions. **The model's prior must be Indonesian, not global.**

### 2.4 Traditional medicine (jamu)

Widely used, rarely volunteered, and capable of real interactions.

*Design response:* explicit non-judgmental intake question. Asking neutrally is the only
way to get a truthful answer.

### 2.5 Ramadan and religious practice

Fasting shifts medication timing for diabetes and hypertension. Dosing advice that
ignores this is advice patients will quietly not follow.

*Design response:* a calendar-aware rule and an intake question. Cheap to build, and it
reads as genuine local fluency rather than a translated foreign product.

### 2.6 Formulary and affordability

A clinically ideal drug outside Fornas produces an out-of-pocket bill the patient did not
expect and may not pay.

*Design response:* every suggestion passes a Fornas check and is flagged when off-list.

### 2.7 Connectivity and device reality

Intermittent connectivity outside Java. Shared devices. Low-end Android. Data cost
sensitivity.

*Design response:* text-first, low-bandwidth, resumable sessions, no assumption of a
stable video call. **Design for the median user, not the Jakarta user.**

### 2.8 Identity on shared devices

One phone, one household. The person typing may not be the patient.

*Design response:* explicit "who is this for" step. Never assume the account holder is
the patient — the age gate depends on getting this right.

### 2.9 Regulatory ambiguity

Legal commentary consistently notes that UU 17/2023 and PP 28/2024 recognise telemedicine
but do not fully prescribe operational standards, and that the PDP Law remains relatively
untested in telemedicine specifically.

*Design response:* **the licensed doctor is the decision-maker in every flow.** This is
not a UX preference. It is the architectural choice that keeps the system inside the
existing, well-understood regulatory frame for medical practice rather than requiring a
new one. Everything else in the design follows from this.

---

## Part 3 — Adversarial and human failure modes

Failures that come from people behaving normally, not maliciously.

| Scenario | Risk | Response |
|---|---|---|
| Patient wants antibiotics for a viral URI | AI complies to be agreeable; contributes to AMR | Refusal path is explicit and scripted; doctor sees the request flagged |
| Patient minimises symptoms to get a quick prescription | Under-triage | Cross-check questions; inconsistency surfaced to reviewer |
| Patient exaggerates for a sick note | Over-triage, wasted capacity | Doctor decides; system does not issue documentation |
| Drug-seeking behaviour | Harm, legal exposure | Controlled substances out of scope entirely |
| Doctor rubber-stamps drafts under time pressure | **The single most dangerous failure in the whole system** | Track per-doctor edit rate and review dwell time; flag anomalies; deliberately seed known-flawed drafts in QA to test vigilance |
| Doctor over-rides correct escalations | Automation resistance | Log overrides; feed to clinical governance review |
| Clinic uses the tool to cut doctors rather than extend reach | Care quality collapse; reputational and clinical risk | Contract on capacity per doctor, not headcount reduction. **State this to the client explicitly.** |
| Patient treats the AI as a doctor | Delayed care | Persistent, unmissable framing at every touchpoint |
| Prompt injection via patient free text | Model manipulation | Patient input is data, never instruction; strict separation in the prompt architecture |

---

## Part 4 — Explicit non-goals

> **Superseded by the revised list in [09](09-hitl-and-pathway-limits.md) Part 6**, which
> adds the surgical, post-operative, oncology and continuity-of-care exclusions.

Stated so no one can claim they were implied:

1. **Not an autonomous diagnostician.** No clinical output reaches a patient without a
   licensed doctor's signature.
2. **Not an emergency service.** Red flags route to emergency care; the system does not
   manage them.
3. **Not a replacement for doctors.** A capacity multiplier for existing doctors.
4. **Not a prescriber.** Drafts a plan for a doctor to accept, edit, or reject.
5. **Not a mental health service.**
6. **Not a paediatric service under age 2.**
7. **Not a medical device seeking certification** in its current form — deliberately
   scoped to sit inside clinician-supervised practice. If the scope ever widens, this
   status must be re-examined before, not after.

---

## Part 5 — Where the concept generalises

The brief said "digital doctor," but the underlying pattern — **structured intake →
retrieval over authoritative local documents → deterministic safety rules → drafted
output → expert review and sign-off → capture the edit as signal** — is domain-general.

Same architecture, different corpus:

- **Claims adjudication** for an insurer: intake is a claim, corpus is policy documents
  and INA-CBG rules, expert is a claims assessor.
- **Loan underwriting**: corpus is credit policy, expert is a credit officer.
- **Contract review**: corpus is a legal playbook, expert is counsel.
- **Regulatory compliance review**: corpus is the regulation, expert is compliance.

This matters for the SaxeCap context specifically: **the reusable asset is the
review-and-sign-off architecture with its eval harness, not the clinical content.** That
is what gets deployed across a portfolio. Worth one slide, not more — but worth saying.
