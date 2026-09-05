# 05 — Evaluation Plan

**In clinical AI, the evaluation is the product.** A demo without measurement is a
prototype; a demo with measurement is an argument.

Almost every submission to this brief will show a working chatbot. Very few will hand
over red-flag sensitivity on a held-out set. **This document is the differentiator.**

---

## 1. Evaluation set

**Target: 40–60 hand-written clinical vignettes**, each with expected behaviour specified
in advance — before seeing model output. Writing the expected answer after seeing the
output is not evaluation, it is rationalisation.

| Bucket | Count | Purpose |
|---|---|---|
| Red flag / emergency | 15 | MI, stroke, dengue warning signs, preeclampsia, infant sepsis, ectopic pregnancy, meningitis, DKA |
| Culture-bound presentation | 10 | *masuk angin*, *panas dalam*, *meriang* — split between benign and serious underlying cause |
| Routine primary care | 15 | URI, gastroenteritis, hypertension follow-up, dermatitis, uncomplicated UTI |
| Local disease burden | 10 | TB, dengue, typhoid, malaria — over-sampled deliberately |
| Adversarial | 5 | Antibiotic demand, symptom minimisation, drug-seeking, prompt injection |
| Out-of-scope | 5 | Mental health crisis, infant under 2, exam-dependent abdomen, obstetric |

Each vignette carries: presentation text (in realistic mixed-register Bahasa), expected
triage level, expected differential set, must-not-miss conditions, expected abstention
flag.

**Sourcing:** adapted from published Indonesian clinical guidance and standard teaching
cases, rewritten into realistic patient language. No real patient data.

---

## 2. Metrics

### Safety — the ones that decide deployment

| Metric | Target | Notes |
|---|---|---|
| **Red-flag sensitivity** | **100%** | Non-negotiable. Any miss is a build failure, not a tuning opportunity. |
| Red-flag specificity | Report honestly | Will be poor. That is the correct trade. |
| Over-triage rate | Track, don't optimise early | The cost of over-triage is money; under-triage is harm. Not symmetric. |
| Out-of-scope detection | 100% | Age gate, MH, obstetric, exam-dependent |
| Appropriate abstention rate | 5–15% | **Zero is a failure signal**, not success. It means the system never recognises its limits. |

### Quality

| Metric | Target |
|---|---|
| Correct condition in top-3 differential | ≥ 80% |
| Correct condition ranked first | ≥ 55% |
| Citation groundedness (claims traceable to a retrieved chunk) | ≥ 95% |
| ICD-10 top-1 accuracy | ≥ 70% |
| SOAP note completeness (rubric-scored) | ≥ 85% |
| Fornas compliance of drug suggestions | 100% flagged when off-list |

**Context for the differential targets:** published evaluation of consumer symptom
checkers puts top-3 accuracy in the high 70s to mid 80s and top-1 in the 50–62% range,
against reported GP first-impression accuracy of roughly 55–65%. So a top-1 target of
55% is not a weak target — it is roughly clinician-level first-impression performance,
and I would rather state that honestly than claim 95% and be disbelieved.

### Operations

| Metric | Target |
|---|---|
| Queue SLA breach rate | < 2% per tier |
| Unaccepted escalations aged > SLA | 0 |
| Overdue tracked investigations | 0 |
| Downgraded red flags (reviewer override) | Track; **each one audited** |
| p95 end-to-end latency | < 8s |
| Cost per consult (inference) | Track in USD; report against doctor-minute cost |
| Doctor review time per case | < 4 min |
| Doctor edit rate | **Track — do not minimise** (see below) |

---

## 3. The metric everyone gets wrong

**A falling doctor edit rate is ambiguous.** It can mean the drafts got better. It can
also mean the doctors stopped reading them.

These have opposite implications and identical dashboards.

Distinguishing them:
- Track review **dwell time** alongside edit rate. Edits falling *and* dwell time
  falling together is an automation-complacency signal, not a quality signal.
- Seed a small number of deliberately flawed drafts into the review queue as a standing
  QA control. Measure catch rate per doctor.
- Sample signed notes for independent clinical audit, monthly.

**Automation complacency is the most likely way this system hurts someone.** It deserves
a metric, not a paragraph.

The counterintuitive part, developed in [09](09-hitl-and-pathway-limits.md) §2.5:
**improving the model can reduce total system safety.** A system with 99% accurate drafts
produces less vigilant reviewers than one at 85%. If vigilance falls faster than draft
error does, net safety falls while every model-quality metric improves. This is why draft
accuracy alone is never a sufficient safety argument.

---

## 4. Honesty protocol

Rules I am holding myself to in the writeup and the demo:

1. **Always report n.** "100% red-flag sensitivity on 15 cases" — never "100% red-flag
   sensitivity."
2. **State what n needs to be.** 15 vignettes is a smoke test. Deployment needs several
   hundred, clinically reviewed, with inter-rater agreement measured.
3. **Show the failures.** The demo includes at least one case the system gets wrong or
   correctly abstains on. A demo with no failures is a demo that was curated.
4. **No cherry-picking.** Metrics are computed on the full set, every run.
5. **Vignettes are not patients.** Written cases are cleaner than real intake text.
   Real-world performance will be worse. Say so before someone else does.

**Calibrated honesty about a small n reads as senior. Overclaiming reads as junior.**
This is the single easiest place to win or lose credibility with a technical reviewer.

---

## 5. Path to production-grade evaluation

What I would do with real time and a clinical partner:

1. **Clinical review board.** 2–3 Indonesian GPs review and ratify the vignette set.
   Measure inter-rater agreement between them — if the doctors disagree, the ground truth
   is not ground truth.
2. **Scale to 500+ vignettes**, stratified by presentation frequency and by region.
3. **Silent shadow mode.** Run against real consultations, output visible to nobody.
   Compare to what the doctor actually did. This is the only honest pre-deployment test.
4. **Staged rollout.** One clinic → five → network. Kill criteria defined in advance and
   in writing.
5. **Continuous monitoring** with automatic rollback on safety-metric regression.
6. **Prospective evaluation** against clinical outcomes, not just against agreement with
   a doctor's note.

---

## 6. Kill criteria

Written down before building, so they cannot be negotiated afterward.

Stop the rollout if:
- Red-flag sensitivity drops below 100% on the ratified set at any point.
- Any patient safety incident is attributable to a system output.
- Doctor edit rate and dwell time fall together over a sustained period.
- Groundedness falls below 90%.
- The clinic begins reducing clinical headcount on the basis of the tool.

**A project with no pre-agreed kill criteria is a project that cannot be stopped once it
has momentum.** Writing these before the first line of code is the point.
