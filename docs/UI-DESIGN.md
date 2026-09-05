# UI design — doctor console and patient simulator

Two pages. The console is what the GP uses; the patient page is what you screen-record.
Static versions with sample data are in `digidoc/console/static/`. Cursor's job in step 6
is to replace the `MOCK` object in each file with `fetch()` calls — not to redesign.

## Who it's for and what it must do

A dokter umum at a BPJS clinic, 40 patients a day, mid-range laptop, sometimes a tablet.
The page has one job: let the doctor read a case in under a minute, see what the machine
decided and *why*, and sign, edit, or reject. Everything else is secondary.

The memorable element is the **trust ledger**: the gate result is shown as readable rule
cards (rule ID, plain reason, guideline anchor), and every clinical sentence in the draft
carries a numbered citation that opens the guideline chunk in a side panel. A reviewer
should be able to click any claim and land on its source in one motion. That is the
design's argument made visible.

## Tokens

Color — paper and ink, with semantic colour reserved for routes only:

| Token | Hex | Use |
|-------|-----|-----|
| `--paper` | `#FBFBF9` | page background |
| `--ink` | `#1C2430` | text |
| `--ink-2` | `#5B6470` | secondary text |
| `--rule` | `#E3E5E8` | hairlines, borders |
| `--well` | `#F1F2F0` | inset panels (raw message, unparsed spans) |
| `--teal` | `#177B6F` | signed state, specialist route, primary button |

Route badges (fill / text):
emergency `#FBE3E1 / #8E1E14` · urgent `#FBEDD2 / #7A4A05` · human handoff
`#EBE6F8 / #4A3A8A` · clinician review `#E6ECF3 / #2F4A6B` · specialist route
`#DFF0EC / #135F55` · routine `#E6F1E1 / #2F5E22`.

Both themes are the same design re-tinted, not two designs. Every rule reads its colour
from a variable, `[data-theme="dark"]` overrides the whole set, and no variable exists in
one theme without a counterpart in the other — that constraint is what stops them drifting.
Two consequences worth keeping:

- Route hues are fixed signals the doctor learns, so dark swaps their luminance and never
  their hue: an emergency badge is a dark red field with light red text, still red.
- White on the brand teal only reaches ~2.9:1 once the teal is brightened for a dark
  background, so dark inverts the primary button — near-black text on bright teal — and
  keeps the patient's outgoing chat bubble deeper than the accent teal, because that bubble
  carries body text. Text on colour is checked against AA, not eyeballed.

Theme is resolved before first paint by a small inline script, falling back to
`prefers-color-scheme`, and is stored under `digidoc-theme` shared by both pages. Resolving
it in the main script instead would flash a white console for a frame, which is the exact
thing a night-shift user switched to dark to avoid.

Type — one family, IBM Plex Sans (400, 500, 600), tabular numerals on.
Scale: 13px body, 15px section titles, 20px page/case title, 11px for rule IDs and ICD
codes (same family, not mono). Line height 1.5. Max line length ~70ch in the draft.

Spacing on an 8px grid. Border radius 4px for controls, 6px for panels. No shadows.

## Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ DigiDoc · Klinik Sehat Sejahtera        model: [real ▾]  [Seed demo] │
├────────────┬─────────────────────────────────────────────────────────┤
│ Queue      │  Case S3 · Perempuan, 52 · 14 menit yang lalu           │
│ ─────────  │  [ clinician review ]  R09 Diabetic foot · R10 Wound   │
│ ▌S2 emerg. │                                                          │
│ ▌S10 emerg │  Pesan pasien                                            │
│ ▌S8 handoff│  ┌──────────────────────────────────────────────────┐   │
│  S5 urgent │  │ Kaki saya ada luka di jempol, sudah 2 minggu …    │   │
│  S6 urgent │  └──────────────────────────────────────────────────┘   │
│  S3 review │                                                          │
│  S7 review │  Hasil gate                                              │
│  …         │  ┌ R09_DIABETIC_FOOT ─────────────────────────────┐     │
│            │  │ Luka kaki pada pasien diabetes                  │     │
│            │  │ Mengancam tungkai; perlu pemeriksaan langsung   │     │
│            │  │ PERKENI_KAKI_DIABETIK_2021 §assessment          │     │
│            │  └─────────────────────────────────────────────────┘     │
│            │                                                          │
│            │  Data terstruktur          (confidence bars, unparsed)  │
│            │  Draf untuk dokter         (mode badge, citations ¹ ²)  │
│            │  ─────────────────────────────────────────────────────  │
│            │  [Terima] [Ubah] [Tolak]     [Konsul spesialis ▾]  [Tanda tangan] │
│            │  Riwayat tindakan                                       │
└────────────┴─────────────────────────────────────────────────────────┘
                                          ┌ Sumber ────────────────┐
                                          │ (citation side panel)  │
```

Left column 280px, fixed. Right column scrolls. Citation panel slides in from the right at
360px and does not push content. Left-aligned everything; no centred text anywhere.

Queue order is severity rank descending, then age ascending. Emergency and handoff rows
carry a 3px left bar in their route colour; nothing else in the queue is coloured.

## States the console must render

| State | What shows |
|-------|------------|
| Route emergency / urgent / handoff | No draft section at all. A single line: "Tidak ada draf — pasien sudah diarahkan ke IGD / fasilitas hari ini / tim." Doctor can still add a note and close. |
| Route clinician review | Draft section with mode badge **Ringkasan** and no plan block. Differentials and "yang perlu diperiksa" only. |
| Route specialist route | Pre-screen answers block above the summary. |
| Route routine | Draft with mode badge **Rencana**, plan items each with citation, SOAP, ICD-10. |
| Draft abstained | Mode badge **Abstain** in amber, with the reason line. |
| Model off (degraded) | Mode badge **Model nonaktif**; raw intake only; a banner at top of the case: "Drafting mati. Kasus masuk antrian tanpa draf." |
| Unparsed spans present | A well-coloured box titled "Tidak terurai" listing the spans verbatim. |
| Injected instructions present | A red-bordered box titled "Teks yang ditujukan ke sistem (diabaikan)" listing them verbatim. |
| Layer 2 available | "Konsul spesialis" button enabled, with module name. Otherwise the button is absent, not disabled. |
| Layer 2 result | A panel below the draft: grade with criteria met, referral level as a badge, start-now items with citations, referral letter points. If the code overrode the model's referral level, an amber line says so. |
| Signed | Whole case body gets a thin teal left border; action buttons replaced by "Ditandatangani oleh dr. … pada …". Nothing editable. |
| Empty queue | "Belum ada kasus. Kirim pesan dari halaman pasien atau tekan Seed demo." |

## Language

Both pages carry a Bahasa Indonesia / English selector, stored in `localStorage` under
`digidoc-language`. Text falls into three tiers, and the tier decides what switching does:

| Tier | Examples | Behaviour |
|------|----------|-----------|
| App-owned | chrome, intake labels and values, gate rule names and reasons, pre-screen questions, action log, errors | Switches immediately. Static tables in `digidoc/i18n.py` and `digidoc/gate/i18n.py`; the server renders them, so changing language refetches `/queue` and `/case/{id}` rather than re-rendering in the browser. |
| Generated clinical text | draft assessment, differentials, SOAP, Layer 2 narrative | Written once at generation time in the language then selected, stored on `Draft.language` / `ConsultResult.language`, and never re-translated. A case whose draft language differs from the interface shows a one-line note above the draft. |
| Source evidence | guideline chunks in the citation panel | Always the source language. In English mode the panel adds "Source text is in Bahasa Indonesia." |

The middle tier is a safety property, not a limitation: the doctor signs a specific text.
Re-translating it on view would put an unreviewed second clinical text under the same
signature, so the language of a draft is fixed when it is written.

## Copy rules

Bahasa Indonesia for everything the doctor reads. Buttons name what happens: **Terima**,
**Ubah**, **Tolak**, **Tanda tangan**, **Konsul spesialis**. Sign confirmation: "Tanda
tangani sebagai dr. [name]? Kasus tidak bisa diubah setelah ini." Errors say what happened
and what to do: "Model tidak merespons. Kasus tetap masuk antrian tanpa draf."

Rule IDs and guideline keys stay in English/uppercase as they are in `rules.py` — they are
identifiers, and the doctor should be able to grep them.

## Patient page

A single chat column, 480px max, centred on the page (the one place centring is allowed —
it mimics a phone). Bubbles: patient right, system left. System bubbles for the static
safety-net messages get a thin left border in the route colour so the recording shows the
escalation visually. A small "Sesi baru" link at top. No avatars, no typing animation.

## What not to do

No dashboard tiles, no charts, no summary cards across the top. No icons in the queue. No
tooltips hiding information the doctor needs — show it. No colour except route badges and
the teal sign state.

## Visual pass

The structure above is unchanged; the surface treatment was tightened so the console reads
as a product rather than a wireframe. What was added:

- Layered surfaces. Page background is a slightly deeper grey and each section sits on a
  white card (1px hairline, 10px radius, one very soft shadow). Hierarchy comes from the
  surface, so section titles drop to 11px uppercase labels in `--ink-2`.
- Route badges are pills with a filled dot in the route colour. Queue rows carry the route
  bar for every escalated route, not only emergency and handoff, and the selected row is
  tinted teal with a right-edge marker. The queue header shows a case count.
- The action bar sticks to the bottom of the case column, so sign is always reachable in a
  long case. Signed cases keep the thin teal left border on the body.
- Confidence bars, SOAP letter chips, ICD-10 chips, and citation markers got real shapes;
  citation markers tint teal on hover.
- Patient page: gradient-teal patient bubbles with a tail, white system bubbles keeping the
  route border, auto-growing composer, and a row of demo shortcut chips that fill the box
  with a fixture message (they disappear after the first message). The chips insert Bahasa
  text in either interface language because `MODEL_MODE=mock` matches the fixture verbatim.

Motion stays minimal: the citation panel slide, a 4px rise when a case renders, and a small
pop on a new chat bubble. All three are disabled under `prefers-reduced-motion`.
