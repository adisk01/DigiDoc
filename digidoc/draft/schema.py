"""Draft objects. The model fills content; code chooses mode."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Citation(BaseModel):
    key: str
    section_id: str


class PlanItem(BaseModel):
    text: str
    citation: Citation
    drug: Optional[str] = None


class SOAP(BaseModel):
    S: str = ""
    O: str = ""
    A: str = ""
    P: str = ""


class ICD10(BaseModel):
    code: str
    label: str


class Draft(BaseModel):
    mode: str  # plan | summary | none | degraded
    language: str = "id"  # language the clinical text was written in, fixed at generation
    assessment: str = ""
    differentials: list[str] = Field(default_factory=list)
    plan: list[PlanItem] = Field(default_factory=list)
    soap: SOAP = Field(default_factory=SOAP)
    icd10: list[ICD10] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    abstain: bool = False
    abstain_reason: Optional[str] = None
    confidence: float = 0.0
