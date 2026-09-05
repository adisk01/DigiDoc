# 08 — Sources

Two parts:
- **Part A** — every source behind the claims in these documents (the investigation trail)
- **Part B** — the corpus to actually ingest into the RAG knowledge base

**Verification key used throughout:**
- ✅ **Landed** — URL appeared directly in search results; content confirmed relevant
- ⚠️ **Locate** — I know this source exists and matters, but did not verify a working URL.
  **Search for it rather than trusting a URL I did not confirm.** A fabricated URL in a
  submission is worse than an honest gap.

---

# PART A — Investigation sources

## A1. Market & competitive landscape

| Source | URL | Used for |
|---|---|---|
| Ken Research — Indonesia Telemedicine Market 2026–2031 | ✅ https://www.kenresearch.com/industry-reports/indonesia-telemedicine-market | USD 405M (2025) → 977M (2031), 15.8% CAGR; Halodoc ~41.76% of online-health-app users; 3,138/3,239 hospitals with EMR (Oct 2025); internet penetration ~80.66% |
| Ken Research — Indonesia Telemedicine Outlook to 2028 | ✅ https://www.marketresearch.com/Ken-Research-v3771/Indonesia-Telemedicine-Outlook-44294427/ | Player founding years/HQ; Halodoc USD 80M Series D (2023, Astra/Temasek) |
| Estonia MFA — Indonesia HealthTech trade report | ✅ https://vm.ee/sites/default/files/documents/2025-03/Indonesia_Strategy_HealthTech.pdf | USD 2.4B by 2029 / 28.18% CAGR estimate; player list; Alodokter 40M monthly users, 45k doctors |
| sourcingcares.com — Indonesia telehealth (Jun 2026) | ✅ https://www.sourcingcares.com/post/global-tech-giants-fuel-indonesias-telehealth-revolution | Halodoc ~40% of digital outpatient; 20,000+ licensed doctors; Korea MoHW MOU Apr 2026 |
| Market Research Indonesia | ✅ https://marketresearchindonesia.com/insights/articles/indonesia-telemedicine-market-future-of-care | ~USD 750M 2025, 14–18% CAGR; Puskesmas partnerships |
| Emerging Markets Today | ✅ https://emergingmarkets.today/telemedicine-takes-center-stage-in-indonesias-health-sector-2023/ | Alodokter 2014, 30,000+ doctors, MoH partner |
| DealStreetAsia — Halodoc | ✅ https://www.dealstreetasia.com/stories/halodoc-209641 | Background (paywalled) |
| UNDP SDG Investor Platform | ✅ http://sdgprivatefinance.undp.org/leveraging-capital/sdg-investor-platform/telemedicine-and-ancillary-healthcare-services-focus-last | Halodoc pricing ~USD 2.45/15min; Alodokter 2021 revenue |

**The definitional problem is itself a finding.** These sources put "the Indonesian
telemedicine market" between USD 405M and USD 2.4B. Quote the range, name the reason
(scope disagreement over e-pharmacy GMV and hospital-linked virtual visits), don't pick
one.

## A2. Provider-side AI competitors

| Source | URL | Used for |
|---|---|---|
| MedMinutes CDSS launch (Apr 2026) | ✅ https://www.openpr.com/news/4454739/medminutes-launches-ai-powered-clinical-decision-support | Indonesian CDSS entrant, Semarang; cites Permenkes 24/2022 |
| MedMinutes — SATUSEHAT FHIR dev guide | ✅ https://dev.to/medminutes/integrating-indonesian-hospitals-with-satusehat-a-developers-guide-to-hl7-fhir-3ig | 12–19wk integration; ISO 8601 + timezone; ICD-10 WHO not CM; >98% submission target |
| Nexmedis (CB Insights) | ✅ https://www.cbinsights.com/company/nexmedis/alternatives-competitors | Jakarta CDSS/transcription startup, founded 2023 |
| MobiHealthNews — AIGP Health | ✅ https://www.mobihealthnews.com/news/asia/singapore-oks-first-agentic-ai-powered-clinical-scribe | Singapore HSA clearance; stated Indonesia/Malaysia expansion; WhatsApp-accessible |
| Adievia — SATUSEHAT penalties | ✅ https://adievia.co.id/en/guide/satusehat-hospital-obligation/ | ~1,306 hospitals (~44%) penalised early 2026; 30 Mar–30 Jun 2026 remediation window; tiered sanctions |

## A3. Workforce & access

| Source | URL | Used for |
|---|---|---|
| World Bank — Indonesia Health Labor Market | ✅ https://documents1.worldbank.org/curated/en/099081623045022875/pdf/P1762890641c9306908a100cb06c343af30.pdf | Puskesmas catchment 25–30k; ~10,000 Puskesmas; staffing composition; WHO/SDG benchmarks |
| WHO Indonesia (Mar 2026) | ✅ https://www.who.int/indonesia/news/detail/03-03-2026-indonesia-strengthens-health-workforce-planning-through-labour-market-analysis | Only 65% of Puskesmas meet 9-category minimum staffing; ~65,000 specialist shortfall by 2032; 78.1% of public hospitals have all 7 basic specialties |
| World Bank via Trading Economics | ✅ https://tradingeconomics.com/indonesia/physicians-per-1-000-people-wb-data.html | 0.69 physicians per 1,000 (2022) |
| Kompas — doctor shortage | ✅ https://www.kompas.id/baca/english/2022/07/20/dealing-with-shortage-of-medical-doctors-in-indonesia | ~160k shortfall; >70% of physicians in Java/big cities |
| UMY (Dec 2025) | ✅ https://www.umy.ac.id/en/rasio-dokter-indonesia-jauh-dari-standar-who-apa-implikasinya/ | BPJS data: 454 Puskesmas without a GP |
| ObserverID | ✅ https://observerid.com/shortages-of-medical-doctors-in-indonesia/ | GP/specialist counts; ~12,000 graduates/yr |

## A4. Payer economics

| Source | URL | Used for |
|---|---|---|
| Windonesia (Apr 2026) | ✅ https://windonesia.com/article/bpjs-kesehatan-under-strain-as-claims-outpace-revenues | **Claim ratio 104.72% → 105.78% → 107.69% → 111.86%**; Rp 29.26tn vs Rp 32.73tn (Feb 2026); 58.32M inactive participants |
| ScienceDirect — UHC financing | ✅ https://www.sciencedirect.com/science/article/pii/S294985622500090X | Capitation vs INA-CBG mechanics; IDR 8,000/member/month clinic example |
| Health Economics Insights (Jul 2026) | ✅ https://journal.privietlab.org/index.php/HEIJ/article/view/2137 | Strategic vs passive purchasing; INA-CBG tariff calibration critique |
| The PRAKARSA | ✅ https://theprakarsa.org/en/bpjs-kesehatan-terancam-gagal-bayar-masalah-lama-yang-perlu-terobosan-baru/ | Deficit projections |
| World Bank — Indonesia UHC deep dive | ✅ https://thedocs.worldbank.org/en/doc/a900ebb6b3caa6b3823d75724e0673ed-0200022022/related/AHFF-Lunch-session-Deep-Dive-Indonesia.pdf | HFIS, VCLAIM, INA-CBG e-claim systems |

## A5. Regulation

| Source | URL | Used for |
|---|---|---|
| Kemenkes Farmalkes — UU 17/2023 | ✅ https://farmalkes.kemkes.go.id/en/unduh/uu-17-2023/ | Health Omnibus Law, official |
| Nusantara Legal — UU 17/2023 overview | ✅ https://nusantaralegal.com/general-overview-and-key-points-of-new-indonesia-omnibus-health-law-no-17-of-2023/ | Relationship to Permenkes 20/2019 |
| SIP Law Firm | ✅ https://siplawfirm.id/telemedicine-di-indonesia | Telemedicine licensing stack; sync vs async definitions |
| Dialogia Iuridica | ✅ https://journal.maranatha.edu/index.php/dialogia/article/view/9422 | Patient/worker protection gaps post-UU 17/2023 |
| Riviera Publishing — telemedicine regulation | ✅ https://jmi.rivierapublishing.id/index.php/rp/article/download/2267/979 | **PDP Law untested in telemedicine**; weak enforcement of localisation |
| Dinasti Review — AI in telemedicine | ✅ https://dinastires.org/JLPH/article/download/2475/1882 | Permenkes 20/2019 service types; PP 28/2024 |
| arXiv — AI regulation cross-jurisdictional | ✅ https://arxiv.org/pdf/2511.22211 | Stranas KA 2020–2045; MOCI Circular 9/2023 AI ethics; **no binding medical-AI law yet** |

## A6. Benchmarks for the eval targets

| Source | URL | Used for |
|---|---|---|
| Conferbot — symptom checker triage study summary | ✅ https://www.conferbot.com/blog/symptom-checker-chatbot | Cites JMIR 2025, 12 platforms / 500 vignettes: triage 82–88%, top-3 78–85%, top-1 52–62%, GP first-impression 55–65%, safety-critical sensitivity 94–97% |
| Doctronic | ✅ https://www.doctronic.ai/blog/free-symptom-checkers-reviewed/ | Top-3 ~70%, top-1 ~34% (different methodology — note the disagreement) |

⚠️ **Trace the JMIR study to primary before citing it in your deck.** I have it
second-hand from a vendor blog, and vendor blogs summarising research favourably is a
known failure mode. The two sources above disagree substantially on top-1 accuracy,
which is itself a reason to go to primary.

---

# PART B — Knowledge base corpus

## B1. Tier 1 — build the demo on these

Highest authority, publicly downloadable, directly relevant to primary care.

### Kemenkes PNPK — the backbone of the corpus

| Resource | URL |
|---|---|
| PNPK collection (all years) | ✅ https://kemkes.go.id/id/media/subfolder/pedoman/pedoman-nasional-pelayanan-kedokteran-pnpk |
| English landing | ✅ https://www.kemkes.go.id/eng/media/subfolder/pedoman/pedoman-nasional-pelayanan-kedokteran-pnpk |
| PNPK 2025 | ✅ https://www.kemkes.go.id/id/media/list/pedoman/pedoman-nasional-pelayanan-kedokteran-pnpk/pnpk-2025 |
| PNPK 2024 | ✅ https://kemkes.go.id/id/media/list/pedoman/pedoman-nasional-pelayanan-kedokteran-pnpk/pnpk-2024 |
| PNPK 2023 | ✅ https://kemkes.go.id/id/media/list/pedoman/pedoman-nasional-pelayanan-kedokteran-pnpk/pnpk-2023 |
| PNPK 2022 | ✅ https://kemkes.go.id/id/media/list/pedoman/pedoman-nasional-pelayanan-kedokteran-pnpk/pnpk-2022 |
| PNPK 2020 | ✅ https://kemkes.go.id/id/media/list/pedoman/pedoman-nasional-pelayanan-kedokteran-pnpk/pnpk-2020 |
| Kemenkes downloads (pedoman category) | ✅ https://kemkes.go.id/id/category-download/pedoman/3 |
| Yankes Ditjen PNPK notice | ✅ https://yankes.kemkes.go.id/view_unduhan/62/pemberitahuan-pedoman-nasional-pelayanan |
| Kemenkes repository (TB PNPK = book/124) | ✅ https://repository.kemkes.go.id/book/124 |

**Start with 2022–2025.** Pull 6–8 guidelines matching your vignette buckets. Do not try
to ingest everything — a small, well-chunked, correctly-cited corpus demos far better
than a large sloppy one.

### Formulary (Fornas) — for the reimbursement check

| Resource | URL |
|---|---|
| **Kepmenkes 1199/2025 — Fornas (most recent found)** | ✅ https://farmalkes.kemkes.go.id/en/unduh/keputusan-menteri-kesehatan-republik-indonesia-nomor-hk-01-07-menkes-1199-2025-tentang-formularium-nasional/ |
| Kepmenkes 2197/2023 — Fornas | ✅ https://farmalkes.kemkes.go.id/en/unduh/kepmenkes-2197-2023/ |
| Kepmenkes 1818/2024 — amendment to 2197/2023 | ✅ https://iaijabar.id/2024/11/25/keputusan-menteri-kesehatan-republik-indonesia-nomor-hk-01-07-menkes-1818-2024-tentang-perubahan-atas-keputusan-menteri-kesehatan-nomor-hk-01-07-menkes-2197-2023-tentang-formularium-nasional/ |
| Kepmenkes 1970/2022 | ✅ https://farmalkes.kemkes.go.id/unduh/kepmenkes-1970-2022/ |

⚠️ **Check for anything superseding 1199/2025 before you build on it.** Fornas is amended
frequently — note the 2023 → 2024 amendment pattern above. **Your versioning story
depends on getting this right, and a reviewer may well ask.**

**Fornas is not a document, it's a lookup table.** Extract to structured rows
(drug, form, strength, restriction, care level) and query it as data. Do not RAG over it
— semantic search on a drug list produces near-misses, and a near-miss on a drug name is
a wrong drug.

### Disease-specific — matched to Indonesian burden

| Resource | URL |
|---|---|
| TB — national guidelines library | ✅ https://tbindonesia.or.id/pustaka-tb/pedoman-nasional-tatalaksana-tuberkulosis/ |
| TB — National Strategy 2020–2024 | ✅ https://www.tbindonesia.or.id/wp-content/uploads/2021/06/NSP-TB-2020-2024-Ind_Final_-BAHASA.pdf |
| TB — Revised STRANAS incl. 2025–26 interim | ✅ https://dinkes.banyuasinkab.go.id/wp-content/uploads/sites/247/2024/03/Revisi-STRANAS-TB-2020-2024-and-rencana-sementara-2025-2026_bahasa_22052023-2.pdf |
| TB — PNPK via IDAI | ✅ https://www.idai.or.id/professional-resources/pedoman-konsensus/pedoman-nasional-pelayanan-kedokteran-tata-laksana-tuberkulosis |
| **Dengue — PNPK paediatric/adolescent** | ✅ https://www.idai.or.id/professional-resources/pedoman-konsensus/pedoman-nasional-pelayanan-kedokteran-tata-laksana-infeksi-dengue-anak-dan-remaja |
| Diabetes — PERKENI downloads hub | ✅ https://pbperkeni.or.id/unduhan |
| Diabetes — **PERKENI DMT2 2024 (PDF)** | ✅ https://pbperkeni.or.id/wp-content/uploads/2025/08/DMT2-2024-Protected.pdf |
| Diabetes — PERKENI DMT2 2021 (PDF) | ✅ https://pbperkeni.or.id/wp-content/uploads/2021/11/22-10-21-Website-Pedoman-Pengelolaan-dan-Pencegahan-DMT2-Ebook.pdf |
| Diabetes — PERKENI insulin therapy | ✅ https://pbperkeni.or.id/wp-content/uploads/2021/11/22-10-21-_-Website-Pedoman-Petunjuk-Praktis-Terapi-Insulin-Pada-Pasien-Diabetes-Melitus-Ebook.pdf |
| Diabetes — PERKENI DMT2 catalogue page | ✅ https://pbperkeni.or.id/catalog-buku/pedoman-pengelolaan-dan-pencegahan-diabetes-mellitus-tipe-2-dewasa-di-indonesia |
| Diabetes — **KMK 302/2026 PPK (draws on PERKENI 2024, ADA 2026)** | ✅ https://keslan.kemkes.go.id/unduhan/fileunduhan1777518085_672976.pdf |
| Diabetes — earlier draft KMK | ✅ https://keslan.kemkes.go.id/unduhan/fileunduhan_1610340996_61925.pdf |
| Paediatrics — IDAI consensus hub | ✅ https://www.idai.or.id/professional-resources/pedoman-konsensus |
| Type 1 diabetes in children — IDAI | ✅ https://www.idai.or.id/professional-resources/pedoman-konsensus/konsensus-nasional-pengelolaan-diabetes-tipe-1 |

**`keslan.kemkes.go.id/unduhan/` is the useful find here** — direct PDF links to
Keputusan Menteri Kesehatan clinical practice guidelines, and KMK 302/2026 is recent.
Worth crawling that path for more.

## B2. Tier 2 — locate these yourself

I know these matter. I did not confirm working URLs, so **search rather than trust a
constructed link.**

| Source | Why it matters | How to find |
|---|---|---|
| ⚠️ **JDIH Kemenkes** (`jdih.kemkes.go.id`) | Official legal database — every Permenkes/KMK. Referenced in the KMK 302/2026 PDF footer. **The canonical place for regulation.** | Search "JDIH Kemenkes" |
| ⚠️ **SATUSEHAT developer portal** (`satusehat.kemkes.go.id`) | FHIR sandbox, API docs, terminology server. Cited by MedMinutes' guide. | Search "SATUSEHAT developer portal" |
| ⚠️ SATUSEHAT FHIR R4 Implementation Guide | Profiles and resource specs | ✅ Found: https://simplifier.net/guide/satusehat-fhir-r4-implementation-guide?version=current |
| ⚠️ WHO IMCI / MTBS | Paediatric danger-sign protocol; Indonesian adaptation is "MTBS" | Search "WHO IMCI chartbook" and "buku bagan MTBS Kemenkes" |
| ⚠️ WHO Dengue Guidelines | Warning-sign criteria for adults | Search "WHO dengue guidelines diagnosis treatment" |
| ⚠️ ICD-10 WHO browser (`icd.who.int`) | **WHO version, not CM** — critical per SATUSEHAT validation | Search "ICD-10 WHO browser" |
| ⚠️ PERKI (cardiology) | ACS and heart failure — your chest-pain red flags | Search "PERKI pedoman sindrom koroner akut" |
| ⚠️ InaSH (hypertension) | Highest-volume chronic condition | Search "InaSH konsensus hipertensi" |
| ⚠️ POGI (obstetrics) | Preeclampsia — high-consequence per scope doc | Search "POGI pedoman preeklampsia" |
| ⚠️ PAPDI (internal medicine) | PAPDI Consensus / Panduan Praktik Klinis | Search "PAPDI panduan praktik klinis" |
| ⚠️ BPJS Kesehatan | Capitation and INA-CBG rules | Search "BPJS Kesehatan regulasi kapitasi" |
| ⚠️ Profil Kesehatan Indonesia | Annual health statistics — disease burden priors | Search "Profil Kesehatan Indonesia Kemenkes" |
| ⚠️ Riskesdas / SKI | National health survey — prevalence data | Search "Survei Kesehatan Indonesia Kemenkes" |

## B3. Not a corpus — a lookup table

**Fornas, ICD-10, and drug interactions are structured data, not prose.** Extract them
into Postgres tables and query them deterministically. RAG over a drug list retrieves
*similar* drug names, and "similar to the right drug" is the wrong drug.

This distinction is worth making explicitly in your writeup — it shows you understand
that RAG is a tool for a specific problem shape, not a default.

---

# Part C — Practical notes on ingestion

## C1. Licensing

Indonesian government publications are generally issued for public professional use, and
Kemenkes actively publishes these for download. But **for a client deliverable, get this
confirmed in writing.** Professional society materials (PERKENI, IDAI, PERKI) are
association publications and may carry different terms — note that the PERKENI DMT2 2024
PDF filename literally contains "Protected."

For an interview prototype: document the sources, cite them properly, don't redistribute
the PDFs in your repo. **Ship the ingestion script, not the corpus.** That is also the
better engineering answer — the pipeline is the artefact.

## C2. What will actually go wrong

Not theoretical. Budget time for these:

- **Scanned pages.** Older Kemenkes PDFs are images. Check every document; OCR the ones
  that need it, and check OCR quality on tables specifically.
- **Tables are where the danger lives.** Dosing tables, diagnostic criteria, severity
  classifications. A naive PDF parser turns a table into unreadable soup, or worse,
  readable-but-scrambled soup. **A dosing table that parses into the wrong row order is
  a patient safety issue, not a formatting bug.** Extract tables separately and validate
  a sample by hand.
- **Bahasa chunking.** Test that your splitter handles Indonesian sentence boundaries and
  doesn't split on medical abbreviations.
- **Mixed language.** Guidelines mix Bahasa prose with English drug names and Latin
  anatomical terms. Your embedding model has to handle both — test it.
- **File size.** Some PNPKs run to hundreds of pages. Chunk on document structure
  (headings, sections), never on fixed token windows.

## C3. Metadata every chunk needs

```json
{
  "source_title": "PNPK Tata Laksana Tuberkulosis",
  "issuing_body": "Kemenkes RI",
  "document_type": "PNPK",
  "publication_year": 2020,
  "source_url": "https://repository.kemkes.go.id/book/124",
  "section_path": "BAB III > Diagnosis > Pemeriksaan Bakteriologis",
  "page": 42,
  "language": "id",
  "corpus_version": "v1.0.0",
  "ingested_at": "2026-09-03T10:00:00+07:00"
}
```

`corpus_version` is the one people skip and regret. **Every generated note must record
which corpus version produced it**, or you cannot audit a clinical decision made six
months ago — and "we can't reconstruct why the system said that" is not an answer anyone
in healthcare will accept.

## C4. Scope for a 2-day build

**6–8 documents, not 60.** Suggested set, mapped to your vignette buckets:

1. PNPK Tuberkulosis (TB bucket)
2. PNPK Dengue (dengue red flags)
3. PERKENI DMT2 2024 (chronic disease)
4. A hypertension guideline (highest-volume chronic)
5. IMCI/MTBS chartbook (paediatric danger signs)
6. Fornas → structured table, not RAG

Then **cite every one of them in your README.** A reviewer who sees real Kemenkes PNPK
citations in your output knows immediately that you did the local work rather than
wrapping an English medical model in a Bahasa prompt. That is the credibility moment the
whole corpus exists to produce.
