# 01 — Market Scan & Build / Buy / Partner

**Question this answers:** products like this already exist. Why are we building one?

---

## 1. The honest starting position

Indonesia has a mature, well-funded consumer telemedicine sector. Halodoc, Alodokter,
KlikDokter, SehatQ, Good Doctor and YesDok have been operating for years, several
predate COVID, and the market leaders serve tens of millions of monthly users. If the
brief meant "build another consumer symptom-checker app," the honest answer is: **don't.
That market is taken, well-capitalised, and the incremental value of a fifth entrant is
near zero.**

Saying this out loud is part of the deliverable. The scoping error most candidates will
make is to build a thin copy of Halodoc's front door.

### Who is already in the market

| Player | Founded | Position |
|---|---|---|
| Halodoc | 2016, Jakarta | Category leader. Full-stack: teleconsult + e-pharmacy + home lab. Roughly 40% of the digital outpatient segment. Raised ~USD 80M Series D (2023, Astra/Temasek). |
| Alodokter | 2014, Jakarta | Content-led. Very large monthly audience, large doctor panel, official MoH partner, insurance product (AloProteksi). |
| KlikDokter | 2008, Jakarta | Oldest. Kalbe-affiliated. Content + teleconsult. |
| Good Doctor | 2019, Jakarta | Grab-affiliated origin. |
| SehatQ / YesDok | 2018 / — | Second tier. |

Sources: Ken Research Indonesia Telemedicine Market report; Estonia MFA Indonesia
HealthTech trade report; sourcingcares.com market summary (June 2026).

### Market size — treat with caution

Published estimates diverge widely, which itself is worth flagging to a client:

- Ken Research: **USD 405M (2025) → USD 977M (2031), 15.8% CAGR**
- Estonia MFA trade report: **USD 2.4B by 2029, 28.18% CAGR**
- Market Research Indonesia: **~USD 750M in 2025, 14–18% CAGR to 2030**

The 4–5x spread across "the Indonesian telemedicine market" reflects different scope
definitions (does e-pharmacy GMV count? do hospital-linked virtual visits count?).
**Do not quote a single number as fact.** Quote the range and name the definitional
problem. In a PE diligence setting, noticing that the market-size numbers disagree is a
higher-value observation than picking one.

---

## 2. The gap the incumbents leave

The incumbents own the **consumer front door**. What they do not own, and what a PE-owned
provider group would actually pay for:

**a) The supply side is the real constraint, not the demand side.**
Indonesia's physician density sits around **0.69 per 1,000 people** (World Bank, 2022)
against a Ministry of Health target of 1.0. The Ministry has publicly acknowledged a
shortfall in the low hundreds of thousands of doctors. Distribution is worse than the
headline: the large majority of physicians and specialists cluster in Java and major
cities, and a meaningful number of Puskesmas operate without a general practitioner.
WHO reported in March 2026 that only about 65% of Puskesmas meet the minimum staffing
of nine basic health-worker categories, and projected a shortfall of roughly 65,000
medical specialists by 2032.

Adding another app does not create doctors. **Making each existing doctor-hour serve more
patients does.** That is a workflow problem inside a provider, not a consumer app problem.

**b) Provider-side documentation, coding, and reimbursement is largely unserved.**
The AI scribe / CDSS category is crowded globally (Abridge, Nuance/Microsoft, Freed,
athenaAmbient) but those products are English-first and priced for US health systems.
Local entrants exist and are early: MedMinutes (Semarang) launched a CDSS for Indonesian
hospitals in April 2026; Nexmedis (Jakarta, founded 2023) offers CDSS and consultation
transcription; Singapore's AIGP Health cleared an agentic AI scribe with the HSA and has
publicly targeted Indonesia and Malaysia for expansion. **This is an early, contested,
not-yet-won category — the opposite of consumer teleconsult.**

**c) A regulatory forcing function just created a budget line.**
Under Permenkes 24/2022, reinforced by later hospital regulation, every hospital must
connect to SATUSEHAT, the national FHIR R4 health data exchange. In early 2026 the
Ministry of Health imposed administrative penalties on roughly **1,306 hospitals (~44%)**
that had not completed EMR integration, with a remediation window running to 30 June
2026. Tiered sanctions run written warning → accreditation downgrade → licence
suspension.

Separately, roughly **3,138 of 3,239 hospitals** had implemented electronic medical
records as of October 2025 (Ken Research). Structured clinical data now exists in a way
it did not three years ago. **The substrate for provider-side AI just became available,
and compliance pressure just made someone accountable for it.**

**d) The payer is under acute financial stress, which changes what gets funded.**
BPJS Kesehatan's claim ratio has risen from 104.72% (2023) → 105.78% (2024) → 107.69%
(2025) → **111.86% (early 2026)**. As of February 2026 the reported gap was
Rp 29.26tn premium revenue against Rp 32.73tn claims — a Rp 3.47tn shortfall
(source: windonesia.com, April 2026, citing BPJS leadership). Meanwhile capitation
rates paid to primary providers are thin — one cited figure is IDR 8,000 per member
per month.

**Read this correctly.** A squeezed payer means providers absorb margin pressure.
Under capitation, a clinic's profit is a function of cost per covered life, not visits
billed. **That makes clinician-time efficiency the single highest-leverage lever in the
provider P&L — which is exactly what this system sells.**

---

## 3. Build / Buy / Partner

The correct answer is not "build everything." It is a layered decision.

| Layer | Decision | Reasoning |
|---|---|---|
| Consumer acquisition front door | **Partner / don't compete** | Halodoc and Alodokter have won distribution. Fighting for it is capital-destructive. |
| Foundation model | **Buy** | Never train a base model. Use a hosted frontier model with a local-inference fallback path if data-residency requires it. |
| ASR (speech-to-text) for Bahasa | **Buy, then evaluate hard** | Bahasa Indonesia ASR quality varies sharply on regional accents and code-switching. Benchmark ≥2 vendors on real clinic audio before committing. |
| SATUSEHAT FHIR bridging | **Buy or partner** | Commodity integration work with local vendors already selling it (12–19 weeks for a typical hospital, per practitioner accounts). Do not rebuild. |
| Clinical reasoning + retrieval over **Indonesian** guidelines | **BUILD** | No incumbent does this well. Guidelines are in Bahasa, locally specific, and not in any vendor's corpus. |
| Red-flag / triage safety layer | **BUILD** | Cannot be outsourced. It is the liability surface. It must be deterministic, auditable, and owned. |
| Formulary (Fornas) + INA-CBG coding logic | **BUILD** | Indonesia-specific, tied to reimbursement, changes with regulation. This is the defensible moat. |
| Doctor review console | **BUILD** | The workflow *is* the product. Where the human-in-the-loop lives. |
| Eval harness | **BUILD** | In clinical AI the eval is the product. Never outsource your own grading. |

**The one-line version for an exec:** *We buy the intelligence and rent the plumbing. We
build the clinical safety layer, the Indonesian knowledge grounding, and the workflow —
because those are the parts nobody can sell us and the parts that decide whether this is
safe enough to deploy.*

---

## 4. Why a PE-owned provider is the right buyer

This matters for a SaxeCap-shaped answer specifically.

- A consumer app monetises transactions. A provider monetises **clinician capacity**.
- Under capitation, saved clinician minutes flow **straight to EBITDA** — no volume
  assumption required.
- Coding accuracy improvements show up in realised revenue per case, which is
  measurable inside one reporting period.
- A PE sponsor holding a clinic platform can deploy the same system across every
  add-on acquisition. **Build once, roll out across the portfolio.** That is the
  multiple-expansion story, and it is the reason to prefer a provider over a platform.

---

## 5. What would change this analysis

Stated so a reviewer can see the failure conditions:

- If Halodoc or Alodokter ships a strong provider-side clinical suite, the build case
  weakens sharply toward partnering.
- If Kemenkes issues binding rules on AI in clinical decision-making that require
  device-style certification, timeline and cost change materially.
- If ASR word-error-rate on real Indonesian clinic audio is above roughly 15%, the
  ambient-scribe path is not viable yet and the product should stay text-first.
- If the target clinic network's EMR cannot expose structured data, integration cost
  may exceed the value of the AI layer. Diligence this before signing anything.
