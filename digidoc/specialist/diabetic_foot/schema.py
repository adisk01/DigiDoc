"""Input findings and output of the diabetic-foot specialist module."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ExamFindings(BaseModel):
    probe_to_bone: bool
    necrotic_tissue: bool
    depth: Literal["superficial", "deep", "to_bone"]
    cellulitis_cm: float
    systemic_signs: bool
    pulses_palpable: bool
    hba1c: Optional[float] = None
    free_text: str = ""


class Grade(BaseModel):
    system: Literal["Wagner"] = "Wagner"
    value: str
    criteria_met: list[str] = Field(default_factory=list)


class Citation(BaseModel):
    key: str
    section_id: str


class StartNowItem(BaseModel):
    text: str
    citation: Citation


class ConsultResult(BaseModel):
    module: str = "diabetic_foot"
    language: str = "id"  # language of narrative and referral reason, fixed at generation
    grade: Grade
    referral: Literal["routine", "urgent", "emergency"]
    referral_reason: str
    narrative: str = ""
    start_now: list[StartNowItem] = Field(default_factory=list)
    referral_letter_points: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = 0.0
    override: bool = False
    model_said: Optional[str] = None
