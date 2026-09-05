"""Shared data models for DigiDoc.

The Intake object is the contract between stages. Intake (model-driven) produces it;
the gate (deterministic) reads it; the drafter (model-driven) reads it plus the gate result.
Nothing downstream ever re-reads the raw message for clinical decisions — only for display.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PregnancyStatus(str, Enum):
    NO = "no"
    YES = "yes"
    UNSURE = "unsure"
    NA = "na"  # male, child, or not asked because not applicable


class Route(str, Enum):
    EMERGENCY = "emergency"                  # hospital now, pipeline stops
    URGENT_SAME_DAY = "urgent_same_day"      # facility today, no draft
    HUMAN_HANDOFF_NOW = "human_handoff_now"  # mental health; nothing generated
    CLINICIAN_REVIEW = "clinician_review"    # doctor sees summary only, no plan drafted
    SPECIALIST_ROUTE = "specialist_route"    # e.g. device follow-up; pre-screen, then route
    ROUTINE = "routine"                      # draft allowed, doctor reviews and signs


class Intake(BaseModel):
    """Structured output of the intake stage. All fields nullable because the
    intake may fail to extract them; the gate treats None conservatively."""

    raw_message: str
    patient_is_self: Optional[bool] = None
    age_years: Optional[float] = None
    sex: Optional[str] = None  # "m" | "f" | None
    pregnancy_status: PregnancyStatus = PregnancyStatus.NA
    pregnancy_weeks: Optional[int] = None
    recent_surgery_days: Optional[int] = None  # days since surgery, if any in last ~90d
    implanted_device: Optional[str] = None     # "pacemaker", "icd", etc.
    chronic_conditions: list[str] = Field(default_factory=list)  # canonical: "diabetes", ...
    medications: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    chief_complaint: Optional[str] = None
    duration_days: Optional[float] = None
    fever_days: Optional[float] = None
    symptoms: list[str] = Field(default_factory=list)  # canonical tags, see gate/tags.py
    unparsed_spans: list[str] = Field(default_factory=list)
    field_confidence: dict[str, float] = Field(default_factory=dict)
    injected_instructions: list[str] = Field(default_factory=list)  # text that looked like it was addressed to the system
    extraction_failed: bool = False  # model outage or unparsable output; stop asking, hand to a human


class RuleHit(BaseModel):
    rule_id: str
    name: str
    route: Route
    reason: str


class GateResult(BaseModel):
    hits: list[RuleHit]
    route: Route
    draft_allowed: bool
    summary_only: bool
    safety_net_key: str  # which patient-facing safety-net template to send
    layer2_modules: list[str] = Field(default_factory=list)  # specialist modules the GP may invoke
    prescreen: list[str] = Field(default_factory=list)       # extra questions to ask (device, IMCI)
    notes_for_doctor: list[str] = Field(default_factory=list)
