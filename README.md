# DigiDoc — a digital GP for Indonesian primary care

Prototype for the SaxeCap FDE assignment. Start with [docs/ONE-PAGER.md](docs/ONE-PAGER.md).

## Layout

```
docs/          the design package (00–10) + ONE-PAGER.md + UI-DESIGN.md
fixtures/      scenarios.json — twelve demo scenarios, machine-readable
digidoc/
  models.py    the Intake / GateResult contract between stages
  gate/        deterministic safety gate: rules.py (readable), engine.py, safety_net.py
  intake/      model-driven structured intake
  retrieval/   guideline corpus + BM25
  draft/       guideline-cited draft, SOAP, ICD-10
  specialist/  Layer 2 modules; diabetic_foot/
  console/     doctor review console (FastAPI + static pages)
eval/          run_gate / run_intake / run_draft / run_layer2 / run_all
corpus/        guideline summaries + manifest
```

## Setup

```
pip install -r requirements.txt
```

Optional: set `OPENAI_API_KEY` and `DIGIDOC_MODEL` (default `gpt-5.6-luna`) for `--mode real`.

## Eval

```
make eval                              # MODEL_MODE=mock, writes data/eval_mock_*.json
python -m eval.run_all --mode mock
python -m eval.run_all --mode off
python -m eval.run_all --mode real     # needs OPENAI_API_KEY

python -m eval.run_gate                # no API key
python -m eval.run_intake
python -m eval.run_draft
python -m eval.run_layer2
```

Current pass table (`--mode mock`):

```
id     gate    intake   draft   layer2   overall
S1     PASS    PASS     PASS    —        PASS
S2     PASS    PASS     PASS    —        PASS
S3     PASS    PASS     PASS    PASS     PASS
S4     PASS    PASS     PASS    —        PASS
S4b    PASS    PASS     PASS    —        PASS
S5     PASS    PASS     PASS    —        PASS
S6     PASS    PASS     PASS    —        PASS
S6b    PASS    PASS     PASS    —        PASS
S7     PASS    PASS     PASS    —        PASS
S7b    PASS    PASS     PASS    —        PASS
S8     PASS    PASS     PASS    —        PASS
S9     PASS    PASS     PASS    —        PASS
S10    PASS    PASS     PASS    —        PASS
S10b   PASS    PASS     PASS    —        PASS
S11    PASS    PASS     PASS    —        PASS
S12    PASS    PASS     PASS    —        PASS
16/16 gate · 16/16 intake · 12/12 draft · 2/2 layer2

red-flag catch rate              5/5
guideline concordance            3/3
antibiotic appropriateness       2/2
referral appropriateness         2/2
abstention                       3/3
extraction calibration           1/1
fail-safe                        2/2
```

## Console

```
python -m digidoc.console.app
```

Doctor console: http://127.0.0.1:8000  
Patient simulator: http://127.0.0.1:8000/patient  

Both pages include a persistent Bahasa Indonesia / English selector. Use **Seed demo**
to load the twelve fixtures. Set `MODEL_MODE=real|mock|off` before startup, or use the
console selector.

### Language

The selector switches everything the app writes itself: interface chrome, intake field
labels and values, gate rule names and reasons, pre-screen questions, the action log, and
error messages. Two things do not move, by design:

- **Guideline chunks** in the citation panel stay in their source language, because they
  are the cited evidence. In English mode the panel says so.
- **Draft and Layer 2 clinical text** is written once, in the language selected when the
  case was created, and is never re-translated afterwards — the doctor signs a specific
  text, not a rendering of it. Seed or send a patient message in the language you want
  the drafts in. If a stored draft's language differs from the interface, the case says so
  above the draft.

Build status: steps 1–8 done. Steps 9–10 are demo/deck, not code.
