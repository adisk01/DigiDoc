# DigiDoc — one page

**Brief:** *The quality of healthcare in Indonesia can be inconsistent, with limited access
to knowledgeable doctors. We need to create a Digital Doctor for a healthcare company in
Indonesia.*

## The questions I would have asked, and what I assumed instead

| Question | My assumption | If wrong, what changes |
|----------|---------------|------------------------|
| Which doctors? | General practitioners (dokter umum). Primary care is where the volume, the variance, and the text-friendly work all are. | If the client is a specialist group, Layer 2 becomes the product and Layer 1 shrinks to intake. |
| Which company? | A multi-site primary care network under BPJS capitation, PE-backed. | If it's a consumer telehealth app, the liability model flips and I'd rebuild as a triage front-end for their existing doctors. |
| Which channel? | Text, WhatsApp-style, Bahasa Indonesia. | Voice adds an ASR dependency I'd measure first (see v1.5). Video is out. |
| Can the AI act alone? | No. A licensed doctor signs every clinical output. | Nothing changes — this is not negotiable under current Indonesian regulation. |

## Reframe

"Quality" in Indonesian primary care is two things: **guideline adherence** (an overloaded GP
skips the guideline, over-prescribes, misses dengue warning signs) and **specialist access**
(the GP is the only doctor the patient will see; the specialist is three hours away). The
digital doctor is therefore a **digital GP**, with specialist-knowledge backup for the GP.
It is not a digital cardiologist.

## The design

```
Patient (WhatsApp, Bahasa)
   → Layer 1: AI intake → safety gate (code) → guideline-cited draft → GP reviews & signs → patient
                                   ↓ emergency → hospital now
   → Layer 2: GP asks a specialist module (own corpus, own evals) → advice returns to GP → GP signs
```

- **Layer 1 raises the floor.** Every case: structured intake, deterministic red-flag check,
  draft where every clinical claim cites PNPK / Fornas / Kemenkes / IMCI. SOAP note and ICD-10
  come out of the same pass.
- **Layer 2 gives every GP a specialist in their pocket.** Advice goes to the doctor, never
  the patient.
- **Recognise-and-route for everything else.** Under-2s, pregnancy, post-op, implanted
  devices, mental health, exam-dependent, undifferentiated: captured at intake, gated in
  code, routed with a summary, never drafted.

## Non-negotiables

Doctor signs everything · red flags in code, not prompts · every claim cited · every failure
degrades toward more human involvement · safety-netting to the patient before review.

## What the prototype contains

Layer 1 end to end · one Layer 2 module (diabetic foot) · twelve scenario fixtures and an
eval runner · degraded mode (model off → route to doctor) · doctor console.

**Not in the prototype, and said so:** voice, images, EMR/SATUSEHAT integration (named as
deployment target), nurse task-shifting (named as v2), other specialist modules (pattern
shown, corpora not built).

## What I'd measure in a 12-week pilot

Red-flag catch rate on a doctor-reviewed set · guideline concordance · antibiotic
appropriateness · referral appropriateness · doctor edit/reject rate (0% edits is an alert,
not a win) · minutes released per consult · claims coding completeness.

## Why a PE sponsor cares

Sells (makes doctors better and faster, doesn't replace them or carry their liability) ·
compounds (same pipeline on every add-on clinic, day one) · measurable (metrics fall out of
the logs) · defensible (the model is rented; the guideline corpus, the gate, and the Bahasa
intake are owned).

## Honest limit

Where there is no doctor at all, this system is empty. That gap is real and it is the v2
hypothesis (nurse or midwife at the Puskesmas + remote supervising GP), not something this
prototype claims to solve.
