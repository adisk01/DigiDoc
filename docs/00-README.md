# Digital Doctor — Indonesia

**SaxeCap FDE AI Engineer — Take-home assignment**

---

## The brief, as given

> The quality of healthcare in Indonesia can be inconsistent, with limited access to
> knowledgeable doctors. We need to create a Digital Doctor for a healthcare company
> in Indonesia.

## How I interpreted it

The brief is deliberately underspecified. "A healthcare company in Indonesia" could mean
a clinic network, a hospital group, a telemedicine platform, a pharmacy chain, or an
insurer — and each has a different P&L, a different regulatory exposure, and a different
answer to "what should the AI actually do."

So the first deliverable is not a chatbot. It is a **scoping decision**, stated openly,
with the alternatives I rejected and why.

**What I built:** a doctor-supervised asynchronous consultation pipeline for a
multi-site primary care network with a telemedicine arm. The patient describes symptoms
in Bahasa Indonesia. The system performs structured intake, runs a deterministic
red-flag triage layer, retrieves from Indonesian clinical guidelines, and drafts a
clinical assessment, a plan, and a coded note. **A licensed doctor reviews, edits, and
signs. Nothing reaches a patient unsigned.**

**Why this shape:** it answers the literal brief, it survives contact with Indonesian
regulation because the licensed clinician remains the decision-maker, and the
note-plus-coding output produces reimbursement-side value as a byproduct of the same
pipeline. One system, two value streams.

---

## Document index

| # | Document | What it answers |
|---|----------|-----------------|
| 01 | [Market scan & build/buy/partner](01-market-scan.md) | Does this already exist? Why build rather than buy? |
| 02 | [Glossary](02-glossary.md) | Every domain and technical term used across these docs |
| 03 | [Scope & boundaries](03-scope-boundaries.md) | Where "digital doctor" logic breaks and what I refuse to build |
| 04 | [Solution architecture](04-architecture.md) | System design, data flow, tech choices |
| 05 | [Evaluation plan](05-eval-plan.md) | How I measure it, and what "good" means |
| 06 | [Decision log](06-decision-log.md) | Every significant call, with the reasoning and the alternative |
| 07 | [Business case](07-business-case.md) | The EBITDA argument and its assumptions |
| 08 | [Sources](08-sources.md) | Investigation trail + the corpus to ingest |
| 09 | [Care pathway limits & the human layer](09-hitl-and-pathway-limits.md) | Surgical/procedural limits; how the human-in-the-loop design itself fails |
| 10 | [Options, final approach, demo scenarios](10-options-final-approach-and-demo.md) | The seven readings of the brief, the two-layer decision, and the twelve demo scenarios |

---

## Reading order for a reviewer with 10 minutes

1. This page.
2. [Decision log](06-decision-log.md) — the reasoning, compressed.
3. [Care pathway limits & the human layer](09-hitl-and-pathway-limits.md) — what this
   cannot do, and how the human-in-the-loop design itself fails.
4. [Evaluation plan](05-eval-plan.md) — the numbers.
5. Demo.

**The one-line weakness, stated upfront:** this system helps where doctors are
*overloaded*. It does nothing where doctors are *absent* — and Indonesia's access gap is
worst exactly where doctors are absent. The human-in-the-loop design that makes it safe
is what caps its reach. Full treatment in [09](09-hitl-and-pathway-limits.md) §2.2.

---

## Status of facts in these documents

Figures sourced from public reporting are marked with a source URL. Figures I could not
verify to primary sources are marked **[UNVERIFIED]** and should be treated as
directional. Anything presented to a client would be re-checked against primary sources
first. I would rather flag an uncertain number than launder it into a confident one.
