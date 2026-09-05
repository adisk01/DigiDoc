# 07 — Business Case

**All figures below are illustrative placeholders using a hypothetical client profile.**
They demonstrate the model structure. Real numbers require client data. **Every
assumption is stated so a reviewer can attack it — that is the point of showing the
model rather than only the conclusion.**

---

## 1. Why now

Three forces converging, all verifiable from public sources:

**Supply is structurally short.** Physician density around 0.69 per 1,000 (World Bank,
2022) against a Ministry target of 1.0, with severe maldistribution toward Java and major
cities. WHO reported in March 2026 that only ~65% of Puskesmas meet minimum staffing
across the nine basic health-worker categories. **You cannot hire your way out of this
inside a hold period.**

**The payer is squeezed.** BPJS claim ratio rising 104.72% (2023) → 111.86% (early 2026),
with a reported Rp 3.47tn shortfall as of February 2026. Squeezed payer means squeezed
provider margins. **Efficiency stops being optional.**

**The data substrate arrived.** ~3,138 of 3,239 hospitals had EMR as of October 2025, and
SATUSEHAT compliance enforcement began in earnest in early 2026 with penalties against
~1,306 hospitals. Structured clinical data now exists where it didn't three years ago,
and someone at each facility is now accountable for it.

---

## 2. The model

### Hypothetical client
40 clinics · 150 doctors · 1.2M covered lives under BPJS capitation

### Assumptions — challenge every one of these

| # | Assumption | Value | Sensitivity |
|---|---|---|---|
| A1 | Consults per doctor per day, today | 30 | High |
| A2 | Average minutes per consult, today | 12 | High |
| A3 | Doctor review minutes per AI-drafted consult | 4 | **Highest — this is the whole case** |
| A4 | Share of volume eligible for the AI path | 60% | High — see below |
| A5 | Fully loaded doctor cost per hour | USD 12 | Medium |
| A6 | Working days per year | 250 | Low |
| A7 | Inference cost per consult | USD 0.03 | Low |

**On A4:** the 40% excluded is not waste — it is exam-dependent presentations, under-2s,
mental health, obstetric cases, and undifferentiated complaints. Those all still need a
doctor's full time. **Any model claiming 90%+ eligibility has not read the scope
document.**

### Capacity effect

Eligible consults per doctor-day: 30 × 60% = **18**
Time on eligible consults today: 18 × 12 min = **216 min**
Time with AI drafting: 18 × 4 min = **72 min**
**Minutes released per doctor per day: 144** (2.4 hours)

Across 150 doctors × 250 days:
**5.4 million doctor-minutes ≈ 90,000 doctor-hours released annually**

### Two ways to bank it

**Path A — capacity (preferred).** Absorb population growth and new capitated lives
without hiring. At 12 min per consult, 90,000 hours ≈ **450,000 additional consults per
year** of latent capacity. Under capitation, serving more covered lives with the same
clinical headcount is margin.

**Path B — cost.** 90,000 hours × USD 12 = **~USD 1.08M** annual clinical labour cost
avoided.

### Costs

| Item | Annual |
|---|---|
| Inference (~1.6M eligible consults × USD 0.03) | ~USD 48K |
| Infrastructure | ~USD 60K |
| Build (one-time, amortised) | ~USD 250K |
| Ongoing engineering + clinical governance | ~USD 200K |
| **Total year 1** | **~USD 558K** |

### Result

**Year 1 net EBITDA impact: ~USD 0.5M. Steady state: ~USD 0.75M+.**

At a 12x multiple, roughly **USD 6M+ of enterprise value** on a mid-size clinic platform
— before any roll-out to add-on acquisitions.

**The inference cost is the striking number.** Three cents against a doctor-hour of
twelve dollars. The economics are not close. Which means **the binding constraint is
clinical safety and adoption, not cost** — and that is exactly why the eval harness, not
the cost model, is the real deliverable.

---

## 3. Second revenue line: coding

The same pipeline produces a coded clinical note as a byproduct. For the network's
hospital-referred volume, ICD-10 accuracy drives **INA-CBG** group assignment, and group
assignment drives realised reimbursement per case.

I have deliberately **not** put a number on this. Quantifying it requires the client's
actual coding audit data, and inventing a coding-accuracy uplift figure would be exactly
the kind of unfounded number this document is structured to avoid. **Flag it as upside,
size it in diligence.**

Stating it this way is stronger than a fabricated figure. A PE reviewer has seen a
thousand invented uplift percentages.

---

## 4. What kills the case

Honest failure conditions:

- **A3 is wrong.** If doctor review takes 8 minutes rather than 4, the benefit halves. In
  the first weeks it *will* be 8 — trust has to be earned. This is the number to measure
  in the pilot before anything else.
- **A4 is wrong.** If eligible volume is 35% rather than 60%, the case weakens sharply.
- **Doctors reject the workflow.** Adoption is the highest-probability failure mode in
  the whole project, and it is a change-management problem, not a technical one.
- **Integration cost exceeds the AI value.** Real risk with fragmented SIMRS estates.
  Diligence before committing.
- **A safety incident.** Ends the programme regardless of the economics.
- **The client will not stand up clinical governance.** Per
  [09](09-hitl-and-pathway-limits.md) §5.2, that is a reason not to deploy — not a reason
  to deploy carefully.

---

## 4b. What this business case does not claim

**The system multiplies doctor capacity. It does not create it.** Doctor review is the
rate limiter, so throughput is capped at reviewer supply no matter how good the model
gets.

Which means the value above is only available **where doctors already exist but are
overloaded** — an urban or peri-urban clinic network. It is not available where there is
no doctor to review, and per the WHO and World Bank sources in [08](08-sources.md),
Indonesia's access gap is worst precisely where doctors are absent.

That is a real limit on the "improves healthcare access in Indonesia" story, and it
should be stated by us rather than discovered by the client. The absent-doctor case needs
a task-shifting design under remote supervision — a different regulatory problem, scoped
in [09](09-hitl-and-pathway-limits.md) §2.2 as a v2 hypothesis, **not claimed as solved
here.**

## 5. Pilot design

**Do not roll out. Prove it.**

- 3 clinics, 12 doctors, 8 weeks
- Weeks 1–2 **silent shadow mode**: system runs, output visible to nobody, compared
  against what the doctor actually did
- Weeks 3–8 live with mandatory review
- **Primary endpoint: measured doctor review time** (validates A3)
- Secondary: red-flag sensitivity, edit rate, doctor satisfaction, patient satisfaction
- Kill criteria per [05-eval-plan](05-eval-plan.md), agreed in writing before start

**Cost of pilot: low. Cost of being wrong at 40 clinics: very high.** That asymmetry is
the entire argument for staging it.
