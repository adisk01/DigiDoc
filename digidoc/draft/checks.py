"""Post-generation checks. Any failure → summary + abstain."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from digidoc.draft.antibiotics import ANTIBIOTICS
from digidoc.draft.schema import Draft
from digidoc.models import Intake
from digidoc.retrieval.index import Chunk

ROOT = Path(__file__).resolve().parent.parent.parent
LOG_PATH = ROOT / "data" / "log.jsonl"
FORNAS = ROOT / "corpus" / "fornas_list.txt"
ICD_RE = re.compile(r"^[A-Z]\d{2}(\.\d{1,2})?$")

ARI_TAGS = {"cough", "rhinorrhea", "sore_throat"}

# Stewardship is about not *prescribing* antibiotics for a viral pattern. A sentence that
# tells the doctor not to prescribe them is the behaviour we want, so it must not trip the
# check. Anything naming an antibiotic without one of these cues still fails.
NEGATION_CUES: tuple[str, ...] = (
    "no ", "not ", "non-", "without", "avoid", "withhold", "refrain", "unnecessary",
    "no need", "do not", "don't", "rather than", "instead of", "absence of", "unless",
    "tidak ", "tanpa ", "jangan", "hindari", "bukan", "belum ", "kecuali",
)

SENTENCE_SPLIT = re.compile(r"[.;\n•]|(?<=[a-z0-9])\s-\s")


def _fornas() -> set[str]:
    names = set()
    for line in FORNAS.read_text(encoding="utf-8").splitlines():
        n = line.strip().lower()
        if n:
            names.add(n)
            names.add(n.replace(" ", ""))
    return names


def _log(reason: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "kind": "draft_check",
        "error": reason,
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _blob(d: Draft) -> str:
    return json.dumps(d.model_dump(), ensure_ascii=False).lower()


def _is_ari(intake: Intake) -> bool:
    return bool(ARI_TAGS & set(intake.symptoms)) and "dyspnea" not in intake.symptoms


def _prose(d: Draft) -> list[str]:
    """Free text a clinician would read, sentence by sentence."""
    parts = [d.assessment, d.abstain_reason or "", *d.differentials]
    parts += [d.soap.S, d.soap.O, d.soap.A, d.soap.P]
    parts += [item.text for item in d.plan]
    parts += [f"{c.code} {c.label}" for c in d.icd10]
    out: list[str] = []
    for part in parts:
        out.extend(s.strip().lower() for s in SENTENCE_SPLIT.split(part or "") if s.strip())
    return out


def _antibiotic_prescribed(draft: Draft) -> str | None:
    """Name of an antibiotic the draft actually puts forward, or None.

    A prescribing plan item counts outright. Elsewhere, a mention only counts when the
    sentence carrying it is not a negation.
    """
    for item in draft.plan:
        drug = (item.drug or "").strip().lower()
        if any(name in drug for name in ANTIBIOTICS):
            return drug
    for sentence in _prose(draft):
        for name in ANTIBIOTICS:
            if name in sentence and not any(cue in sentence for cue in NEGATION_CUES):
                return name
    return None


def check(draft: Draft, intake: Intake, chunks: list[Chunk], mode: str) -> list[str]:
    reasons: list[str] = []
    allowed = {(c.key, c.section_id) for c in chunks}
    for i, item in enumerate(draft.plan):
        cit = (item.citation.key, item.citation.section_id)
        if cit not in allowed:
            reasons.append(f"plan[{i}] citation {cit} not in retrieved chunks")
        if item.drug:
            if item.drug.strip().lower() not in _fornas():
                reasons.append(f"plan[{i}] drug {item.drug!r} not in Fornas list")
    if mode == "summary" and draft.soap.P.strip():
        reasons.append("SOAP.P must be empty in summary mode")
    for icd in draft.icd10:
        if not ICD_RE.match(icd.code):
            reasons.append(f"ICD-10 code {icd.code!r} failed regex")
    if _is_ari(intake):
        offender = _antibiotic_prescribed(draft)
        if offender:
            reasons.append(f"ARI stewardship: {offender!r} put forward in draft")
    return reasons


def apply_failures(draft: Draft, reasons: list[str]) -> Draft:
    if not reasons:
        return draft
    _log("; ".join(reasons))
    data = draft.model_dump()
    data["mode"] = "summary"
    data["plan"] = []
    data["abstain"] = True
    data["abstain_reason"] = "; ".join(reasons)
    data["confidence"] = min(draft.confidence, 0.2)
    soap = data.get("soap") or {}
    soap["P"] = ""
    data["soap"] = soap
    return Draft.model_validate(data)
