# 04 — Solution Architecture

---

## 1. The core commitment

**A licensed doctor signs every clinical output. The AI drafts; the doctor decides.**

Everything below follows from that one sentence. It is what keeps the system inside the
existing regulatory frame for medical practice, and it is what makes the risk profile
acceptable enough to actually deploy.

---

## 2. Flow

```
Patient (WhatsApp-style, Bahasa)
      │
      ▼
[1] STRUCTURED INTAKE
    Adaptive follow-up questions
    Mandatory fields: age, pregnancy status, who-is-this-for,
                      current medications, jamu use, allergies
    Output: typed clinical object + per-field confidence
      │
      ▼
[2] DETERMINISTIC SAFETY GATE          ◄── plain code, not a model
    Red-flag rules · age gate · pregnancy gate
    POST-OP GATE (surgery <30d) · procedural/surgical detection
    Mental-health detection · out-of-scope detection
    Multi-morbidity / polypharmacy complexity flags
      │
      ├──► EMERGENCY  ──► immediate escalation, pipeline STOPS
      ├──► EXAM-DEPENDENT / <2yrs / MH / POST-OP / SURGICAL
      │         ──► summary only, straight to doctor
      │
      ▼
    SAFETY-NETTING issued to patient NOW, before review
    ("if any of these happen, go to hospital — do not wait for a reply")
      │
      ▼ (routine path only)
[3] RETRIEVAL
    Indonesian guideline corpus (PNPK, Kemenkes, WHO IMCI)
    Hybrid: BM25 + vector, then rerank
      │
      ▼
[4] DRAFT GENERATION
    Differential (ranked, with citations)
    Suggested plan · SOAP note · ICD-10 (WHO)
    Every clinical claim carries a source reference
      │
      ▼
[5] POST-GENERATION CHECKS             ◄── plain code again
    Groundedness · Fornas check · interaction check
    Ramadan/fasting rule · confidence floor
      │
      ▼
[6] DOCTOR REVIEW CONSOLE
    Queue → draft → accept / edit / reject → SIGN
    Every edit captured as training signal
      │
      ▼
[7] OUTPUT
    Signed advice to patient · coded note to EMR
    → SATUSEHAT FHIR submission
```

**The safety gate sits before generation, not after.** An emergency never reaches the
model at all. This is deliberate: you cannot prompt-inject your way past an `if`
statement.

---

## 3. Why the safety layer is code, not prompt

| | Deterministic rules | LLM judgement |
|---|---|---|
| Same input, same output | Always | No |
| Auditable line by line | Yes | Not really |
| Testable in CI | Yes | Statistically only |
| Can be argued out of its answer | No | Yes |
| Explainable to a regulator | Trivially | Painfully |

Red-flag detection is the liability surface of the entire product. **It runs on code you
can point a regulator at.** The model is used where it is genuinely better — language
understanding, synthesis, drafting — and nowhere that a wrong answer kills someone
silently.

The model may *add* escalations. It may never *remove* one.

---

## 4. Retrieval design

**Corpus:** Kemenkes PNPK guidelines, national TB / dengue / hypertension / diabetes
guidance, WHO IMCI, Fornas drug list. Bahasa Indonesia primary; English where the
authoritative source is English.

**Chunking is the part that quietly decides quality.** Semantic chunking on document
structure, not fixed token windows — a dosing table separated from its header produces a
confident read of the wrong row. Each chunk carries: source document, section, version,
publication date.

**Retrieval:** hybrid BM25 + dense vector, then rerank. Pure vector search fails on exact
drug names and codes; pure keyword fails on paraphrased symptoms. Both are needed.

**Citations:** every clinical statement in a draft links to a chunk. A statement that
cannot be grounded is dropped, not softened. The reviewing doctor can click through to
the source — which is what makes review fast enough to be worth doing.

**Versioning:** guidelines change. The corpus is versioned and every generated note
records which corpus version produced it. Without this you cannot audit a decision made
six months ago.

---

## 5. Stack

| Layer | Choice | Why |
|---|---|---|
| API | FastAPI (Python) | Fast to build, typed, async, matches the role's primary language |
| Data | Postgres + pgvector | One database. A separate vector store is unjustified complexity at this scale. |
| Queue | Postgres-backed jobs | Redis/Celery is premature here |
| LLM | Hosted frontier model, provider-abstracted | Never train a base model. Abstraction leaves the local-inference door open for data residency. |
| Frontend | React + Tailwind | Doctor console must be fast and plain |
| Observability | Structured logs, per-request trace, cost per consult | You cannot improve what you do not measure |
| Deploy | Single container, one cloud region | See below |

**No Kubernetes. No microservices. No service mesh.** For a two-day prototype serving a
40-clinic pilot, infrastructure sprawl is not sophistication — it is a judgement error,
and an experienced reviewer will read it that way.

---

## 6. Data protection

Under UU 27/2022 (PDP Law), health data is sensitive personal data.

- **Data residency:** Indonesian region deployment as the default assumption; verify
  current requirements with counsel before any production commitment.
- **Minimisation:** the model receives clinical content, not identity. Names, NIK, and
  contact details are tokenised before the prompt boundary and re-joined after.
- **Retention:** clinical records per Indonesian medical-records requirements; raw
  prompt/response logs on a shorter clock.
- **Access:** role-based, fully audited. Every read of a patient record is logged.
- **Consent:** explicit, in Bahasa, plain language, at first contact. Explains AI
  involvement and that a doctor reviews everything.

The one that gets missed: **the doctor's edits are training signal, and they are also
clinical records.** Governance has to cover both uses from day one, not retrofitted after
someone notices.

---

## 7. Integration

**SATUSEHAT (FHIR R4):** map to Patient, Encounter, Condition, Observation, Medication.
Field notes worth respecting — ISO 8601 with timezone, and validate against ICD-10 WHO
rather than ICD-10-CM. Budget 12–19 weeks for a real hospital integration and **do not
put it on the critical path of a pilot.**

**EMR/SIMRS:** highly fragmented vendor landscape. Assume the worst: no API, CSV export
only. Design the pilot so it delivers value standalone and integrates later. A pilot that
cannot start until integration completes is a pilot that never starts.

---

## 7b. Operational safety design

Three mechanisms that exist because of the human-in-the-loop choice, not despite it.
Full reasoning in [09](09-hitl-and-pathway-limits.md).

**Queue SLA with automatic escalation.** Doctor review is the system's rate limiter, so
the queue is a clinical object, not a UX detail. Each triage tier carries a hard SLA. A
case that ages past its tier does not wait quietly — it pages someone. If no reviewer is
available inside the SLA, the patient is told to seek care in person. **The failure mode
being designed against is silence: a queue that grows with nobody noticing.**

**Degraded mode.** Every infrastructure failure degrades toward *more* human involvement,
never less. Model outage, latency spike, or empty retrieval all produce the same
behaviour: intake stays open, drafting turns off, cases route to the human queue. **There
is no failure path where the system acts more autonomously.**

**Loop closure.** Every ordered investigation becomes a tracked item with a named owner
and a due date; overdue items escalate. Missed results are a leading category in real
clinical negligence claims and the thing prototypes never model. The governing rule:
**an order the system cannot track is an order the system should not generate.**

## 8. What I would build next, in order

1. Ambient scribe for in-person visits — but only after measuring Bahasa ASR word error
   rate on real clinic audio.
2. Chronic disease follow-up agent over WhatsApp (hypertension, diabetes, TB adherence).
   Very high value against Indonesian disease burden, and lower clinical risk because the
   diagnosis already exists.
3. INA-CBG coding optimisation for the hospital tier.
4. Population-level surveillance from aggregated intake — early dengue and outbreak
   signal. Meaningful public-health value, and a genuine data moat.
