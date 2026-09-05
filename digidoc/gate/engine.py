"""Gate engine.

Pure function: Intake -> GateResult. No I/O, no model, no randomness.
Run twice, same answer. That property is the whole point.
"""

from __future__ import annotations

from digidoc.gate.rules import RULES, Rule
from digidoc.models import GateResult, Intake, Route, RuleHit

# Higher rank wins. HUMAN_HANDOFF_NOW outranks EMERGENCY deliberately: a suicidal patient
# who also mentions chest pain gets a human first, and the human decides.
ROUTE_RANK: dict[Route, int] = {
    Route.ROUTINE: 0,
    Route.SPECIALIST_ROUTE: 1,
    Route.CLINICIAN_REVIEW: 2,
    Route.URGENT_SAME_DAY: 3,
    Route.EMERGENCY: 4,
    Route.HUMAN_HANDOFF_NOW: 5,
}

DEFAULT_SAFETY_NET = {
    Route.ROUTINE: "routine_safety_net",
    Route.SPECIALIST_ROUTE: "device_routing",
    Route.CLINICIAN_REVIEW: "clinician_review",
    Route.URGENT_SAME_DAY: "urgent_today",
    Route.EMERGENCY: "emergency_now",
    Route.HUMAN_HANDOFF_NOW: "mental_health_handoff",
}


def evaluate(intake: Intake, rules: list[Rule] | None = None) -> GateResult:
    rules = rules if rules is not None else RULES
    hits: list[RuleHit] = []
    fired: list[Rule] = []

    for rule in rules:
        try:
            if rule.when(intake):
                fired.append(rule)
                hits.append(RuleHit(rule_id=rule.rule_id, name=rule.name, route=rule.route, reason=rule.reason))
        except Exception as exc:  # a broken rule must fail closed, not open
            fired.append(rule)
            hits.append(
                RuleHit(
                    rule_id=rule.rule_id,
                    name=rule.name,
                    route=Route.CLINICIAN_REVIEW,
                    reason=f"rule raised {type(exc).__name__}; failing closed to clinician review",
                )
            )

    if hits:
        route = max((h.route for h in hits), key=lambda r: ROUTE_RANK[r])
    else:
        route = Route.ROUTINE

    # Conservative defaults when intake is incomplete
    if route == Route.ROUTINE and _incomplete_for_routine(intake):
        route = Route.CLINICIAN_REVIEW
        hits.append(
            RuleHit(
                rule_id="R00_INCOMPLETE_INTAKE",
                name="Mandatory intake field missing",
                route=Route.CLINICIAN_REVIEW,
                reason="Age or pregnancy status not established; cannot draft safely",
            )
        )

    draft_allowed = route == Route.ROUTINE
    summary_only = route in (Route.CLINICIAN_REVIEW,)

    # Safety-net key: most severe fired rule's key, else default for route
    safety_net_key = DEFAULT_SAFETY_NET[route]
    for rule in sorted(fired, key=lambda r: ROUTE_RANK[r.route], reverse=True):
        if rule.safety_net_key:
            safety_net_key = rule.safety_net_key
            break

    layer2: list[str] = []
    prescreen: list[str] = []
    notes: list[str] = []
    for rule in fired:
        for m in rule.layer2_modules:
            if m not in layer2:
                layer2.append(m)
        for q in rule.prescreen:
            if q not in prescreen:
                prescreen.append(q)
        for n in rule.notes_for_doctor:
            if n not in notes:
                notes.append(n)

    # Mental-health handoff: nothing else travels with it
    if route == Route.HUMAN_HANDOFF_NOW:
        layer2, prescreen, notes = [], [], ["Human contact required now. No triage performed by design."]

    if intake.injected_instructions:
        notes.append(
            "Message contained text addressed to the system (ignored by gate): "
            + " | ".join(intake.injected_instructions)
        )

    return GateResult(
        hits=hits,
        route=route,
        draft_allowed=draft_allowed,
        summary_only=summary_only,
        safety_net_key=safety_net_key,
        layer2_modules=layer2,
        prescreen=prescreen,
        notes_for_doctor=notes,
    )


def _incomplete_for_routine(i: Intake) -> bool:
    if i.age_years is None:
        return True
    # Female of reproductive age with pregnancy not established
    if i.sex == "f" and 12 <= i.age_years <= 55 and i.pregnancy_status.value == "na":
        return True
    return False
