# 09 — Care Pathway Limits & the Human Layer

Doc [03](03-scope-boundaries.md) covered what the *modality* cannot do. This document
covers two things it treated too lightly:

1. **Procedural and surgical care** — got one line. It needs more.
2. **The human-in-the-loop layer itself** — treated as the safety answer, when it is
   actually a design commitment that introduces its own failure modes.

> **The reframe that matters:** human-in-the-loop is not a safety guarantee. It is a
> safety *architecture*, and architectures fail. Saying "a doctor reviews everything" and
> stopping there is the same category of error as saying "the model is very accurate."
> Both are claims that need a failure analysis behind them.

---

## Part 1 — Procedural, surgical, and the referral boundary

### 1.1 What the system does at the surgical boundary

Anything requiring an operation, a procedure, or a physical intervention is **out of
scope for assessment and planning**. The system's job at that boundary is **recognition
and routing**, not decision-making.

Concretely, the system should:
- Recognise presentations that plausibly need surgical assessment
- Escalate with a structured summary
- Stop

It must never: stage a surgical decision, advise for or against an operation, estimate
urgency of an operation, or triage between surgical options.

### 1.2 Why, specifically

**Surgical decisions are exam-and-imaging decisions.** "Does this patient need an
appendicectomy" is answered by palpation, white cell count, and often a CT. The system
has none of these. A confident text-based answer here is not a slightly-wrong answer, it
is a fabricated one.

**Surgical risk stratification needs data the system doesn't hold.** ASA grade, cardiac
risk, anaesthetic history, functional status.

**Pre-operative assessment is a regulated clinical act.** Not a documentation task.

### 1.3 Post-operative care — the trap worth naming

This is a subtler failure and worth calling out explicitly, because it looks safe.

A post-op patient messaging about wound pain, low-grade fever, or discharge looks like a
routine primary care presentation. The intake will classify it as one. But post-operative
complications — anastomotic leak, surgical site infection, DVT, collection — present
exactly this way, and the appropriate threshold for concern is completely different.

**Design response:** recent surgery (within 30 days) is a **mandatory intake field** and a
**hard gate**. Any post-op patient routes directly to a clinician with no autonomous
drafting, regardless of how benign the complaint reads. The system's own confidence is
irrelevant here — the base rate has changed underneath it.

### 1.4 The same logic for other procedural domains

| Domain | Boundary |
|---|---|
| Obstetric delivery | Recognition and routing only. Already gated in [03](03-scope-boundaries.md). |
| Trauma | Red-flag escalation only. Never assessment. |
| Dental | Out of scope. Different clinician, different system. |
| Ophthalmology | Acute red eye and vision loss → red-flag escalation. Nothing else. |
| Oncology | Suspicion → urgent referral pathway. **Never staging, never prognosis, never treatment.** |
| Anything requiring a controlled substance | Out of scope on principle. Governance, not capability. |

### 1.5 The honest framing

**This system covers a slice of primary care. That slice is where the volume is, which is
why the economics work — but it is a slice.** Say it plainly rather than letting a
reviewer discover it.

---

## Part 2 — The human layer as a failure surface

Every failure below exists *because* of the human-in-the-loop design, not despite it.
This is the section most submissions will not have.

### 2.1 The bottleneck problem

**Doctor review is now the rate limiter for the entire system.**

The business case in [07](07-business-case.md) assumes 4 minutes of review per case.
Follow that through:

- 150 doctors × 4 min = the absolute ceiling on throughput
- The system **multiplies** doctor capacity. It does not **create** it.
- If demand exceeds review capacity, a queue forms — and a queue in clinical care is not
  a UX problem, it is a clinical risk.

### 2.2 The uncomfortable consequence for the brief

The brief said: *"limited access to knowledgeable doctors."*

**But this system requires a doctor to function. So it does not help where doctors are
absent — only where doctors exist but are overloaded.**

That distinction maps directly onto Indonesian geography. A Jakarta clinic with
overloaded GPs benefits enormously. A Puskesmas in Papua **with no doctor at all** gets
nothing from this design. And per the World Bank and WHO sources in
[08](08-sources.md), the access gap is worst precisely where doctors are absent.

**This is the sharpest limitation in the whole project and it should be stated first, not
buried.** A reviewer who spots it before you do will read it as a gap in your thinking.
A reviewer who hears you name it unprompted will read it as judgement.

**The honest answer to it:** a task-shifting variant where one remote doctor supervises
AI-assisted nurses and midwives across several Puskesmas. Same architecture, different
supervision ratio. But it is a **materially different regulatory posture** — it touches
scope of practice, not just documentation — and it needs its own design and legal review
rather than being waved at as an extension. **Name it as the v2 hypothesis, don't claim
it as solved.**

### 2.3 When no doctor is available

Async plus a queue means gaps. Real ones:

| Situation | Risk |
|---|---|
| Nights and weekends | Cases queue with nobody reviewing |
| **Lebaran / Idul Fitri** | Multi-day national holiday. Staffing collapses. Demand does not. |
| Outbreak surge | Dengue season, respiratory surge — demand spikes exactly when doctors are most stretched |
| Sick reviewers | Small clinic networks have no bench |

**Design response:**
- Hard SLA per triage tier, with the clock visible to the patient
- **Automatic escalation on SLA breach** — a case that ages past its tier does not wait
  quietly, it pages someone
- If no reviewer is available within the SLA, the system tells the patient to seek care
  in person. **It does not silently hold the case.**
- Explicit degraded mode: intake stays open, drafting turns off, everything routes to
  in-person

**The failure mode to design against is silence.** A queue that grows without anyone
noticing is how an async system hurts someone.

### 2.4 Deterioration inside the window

The patient's illness does not pause while the case sits in a queue. A patient who was
routine at 09:00 can be an emergency by 14:00.

**Design response:**
- Safety-netting instructions issued at intake, before review — plain-language "if any of
  these happen, go to hospital now, do not wait for a reply"
- The patient can re-trigger the safety gate at any time by sending new symptoms
- Re-contact within a short window automatically raises triage priority
- **Time-since-intake is an input to triage, not just a metric**

### 2.5 Automation complacency — expanded

Covered briefly in [05](05-eval-plan.md), but it belongs here as the central human-layer
risk.

**A doctor reviewing 40 consecutive AI drafts that were all fine will not read the 41st
with the same attention.** This is not a character flaw. It is a well-documented property
of human supervision of reliable automation, and it gets *worse* as the system gets
better. A system with 99% draft accuracy produces less vigilant reviewers than one with
85% accuracy.

**The uncomfortable implication: improving the model can reduce total system safety** if
reviewer vigilance falls faster than draft error does.

**Design response:**
- Track edit rate **and** dwell time. Both falling together is the alarm.
- Seeded flawed drafts as a standing control; measure per-reviewer catch rate
- Cap consecutive reviews per session
- Vary the presentation so review does not become muscle memory
- Surface the model's uncertainty prominently — a draft flagged low-confidence gets read
  differently

### 2.6 Reviewer variance

Two doctors reviewing the same draft will not always agree. Neither is necessarily wrong
— clinical judgement has legitimate variance.

But it means "a doctor signed it" is a weaker guarantee than it sounds.

**Design response:** measure inter-rater agreement on a shared sample. Where reviewers
disagree systematically, that is a clinical governance question for the medical director,
not something the engineering team resolves by picking one.

### 2.7 When the doctor is wrong and the model was right

Overrides go both directions. A reviewer may downgrade a correct escalation — from
fatigue, from disagreement with the tool, or from automation resistance.

**Design response:** log every override with reason. **Downgraded red flags get
mandatory retrospective audit** — not to police doctors, but because a pattern of
downgrades either reveals a genuine over-triage problem in the rules or a genuine
vigilance problem in review. Both need to be known.

### 2.8 Handoff seams

**The AI→human and human→patient boundaries are where things get dropped.** Every
real-world clinical safety incident review finds this.

- Draft says "check BP"; doctor edits the plan; the check never gets ordered
- Doctor signs but the patient never receives the message
- Case escalated to a specialist who is not looking at that queue

**Design response:** every escalation is an object with an owner and a state, not a
message. Nothing is "sent" — things are **accepted**. Unaccepted escalations age and
alarm.

### 2.9 Reviewer scope

A GP reviewing a draft that actually needs a cardiologist is still an unqualified review.
The signature is real; the expertise is not.

**Design response:** route by required expertise, not just availability. Where the
network has no specialist, that is a referral, not a review.

---

## Part 3 — Loop closure

The failure that kills people in real health systems, and the one prototypes never model.

### 3.1 Orphaned results

Plan says "get a chest X-ray." Patient gets it. **Who looks at it?**

In a real clinic this is a named person with a worklist. In a prototype it is nobody, and
an abnormal result sits unread. Missed-results failures are a leading category in clinical
negligence claims globally.

**Design response:** every ordered investigation creates a tracked item with an owner and
a due date. Overdue items escalate. **An order the system cannot track is an order the
system should not generate.**

### 3.2 No longitudinal memory

The v1 design is episode-based. It does not know this is the patient's third visit for
the same complaint in six weeks — which is itself a red flag that no single-episode
system can see.

**Design response for v1:** state the limitation. **Design response for v2:** patient
timeline as a first-class object, with repeat-presentation detection as a rule in the
safety layer.

### 3.3 Multi-morbidity and polypharmacy

Guidelines are written per-disease. Patients are not. An elderly patient on eight
medications with four conditions is the case where single-disease guideline retrieval is
least useful and most confidently wrong.

**Design response:** medication count and comorbidity count as complexity flags that
suppress autonomous drafting above a threshold.

---

## Part 4 — Infrastructure and degraded mode

Failures with no clinical content that produce clinical consequences.

| Failure | Response |
|---|---|
| Model provider outage | Degraded mode: intake continues, drafting off, all cases to human queue. **Never fail silently.** |
| Latency spike | Timeout → route to human rather than wait |
| Retrieval returns nothing | Abstain. Do not generate ungrounded. |
| **Silent model drift** | Provider updates the model; behaviour shifts without notice. **Run the eval suite on a schedule, not just on deploy.** This is the one people miss. |
| Corpus staleness | Guideline supersession monitoring; corpus version pinned per output |
| Patient loses connectivity mid-intake | Resumable sessions; partial intake still queues |

**The design principle:** every failure mode degrades toward *more* human involvement,
never toward less. There is no failure path that results in the system acting more
autonomously.

---

## Part 5 — Liability and governance

Not engineering questions, but they decide whether this ships. **Being the person in the
room who raises them is the point.**

### 5.1 Open questions for client counsel

1. **Who is the practitioner of record?** The reviewing doctor signs — does their
   professional liability cover a decision made with AI assistance?
2. **Does their malpractice insurer know?** Some policies have exclusions.
3. **What is the STR position** on reviewing a case you did not personally interview?
4. **If the system misses something the deterministic rules should have caught, who is
   liable** — the doctor who signed, the clinic that deployed, or the vendor?
5. **What is the incident reporting path** when an AI-assisted decision causes harm?
6. **Does the patient consent cover AI involvement** in a way that would survive
   challenge?

### 5.2 Governance the client must stand up

Deployment is not a technical event. Before go-live the client needs:

- A named **medical director accountable for clinical safety** of the system
- A clinical governance committee reviewing metrics monthly
- An incident reporting and investigation process
- A change control process — **no prompt or rule change ships without clinical sign-off**
- A defined path for a clinician to raise a concern and stop the system

**If the client will not stand these up, that is a reason not to deploy — not a reason to
deploy carefully.** Worth saying in the room.

---

## Part 6 — Revised non-goals

Replaces the list in [03](03-scope-boundaries.md).

The system is **not**:

1. An autonomous diagnostician
2. An emergency service
3. A replacement for doctors — and specifically, **not a solution where no doctor exists**
4. A prescriber
5. A mental health service
6. A paediatric service under age 2
7. **A surgical or procedural decision system**
8. **A post-operative care system**
9. **An oncology staging, prognosis, or treatment system**
10. **A continuity-of-care or chronic disease management system** (v1)
11. **A results management system** — unless loop closure is built, in which case it must
    be built properly or not at all
12. A medical device seeking certification in its current scope

---

## The line to say out loud

If asked "what's the biggest weakness," this is the answer:

> **This system helps where doctors are overloaded. It does not help where doctors are
> absent — and Indonesia's access gap is worst exactly where doctors are absent. The
> human-in-the-loop design that makes it safe is also what caps its reach. Solving the
> absent-doctor case means task-shifting to nurses and midwives under remote supervision,
> which is a different regulatory problem and needs its own design.**

Naming your own ceiling is more convincing than any claim about the floor.
