"""Draft-stage eval.

Gold intake → gate → retrieval → draft. Checks each fixture's draft_expect.

Usage:
  MODEL_MODE=mock python -m eval.run_draft
  MODEL_MODE=off  python -m eval.run_draft
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from digidoc.draft.drafter import draft
from digidoc.draft.schema import Draft
from digidoc.gate import evaluate
from digidoc.models import Intake
from digidoc.retrieval import build_query, search

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "scenarios.json"


def load_scenarios() -> list[dict]:
    return json.loads(FIXTURES.read_text(encoding="utf-8"))["scenarios"]


def cases() -> list[tuple[str, str, dict, dict, bool]]:
    """id, message, gold, draft_expect, force_off."""
    out: list[tuple[str, str, dict, dict, bool]] = []
    for sc in load_scenarios():
        force_off = sc.get("runtime", {}).get("model_available") is False
        out.append((sc["id"], sc["message"], dict(sc["gold_intake"]), dict(sc.get("draft_expect") or {}), force_off))
        if "variant" in sc:
            v = sc["variant"]
            gold = dict(sc["gold_intake"])
            gold.update(v.get("gold_intake_patch") or {})
            expect = dict(v["draft_expect"]) if "draft_expect" in v else None
            out.append((v["name"].split(" ")[0], v["message"], gold, expect if expect is not None else {}, False))
    return out


def infer_expect(cid: str, gate_route: str, explicit: dict, model_mode: str) -> dict:
    if explicit:
        expect = dict(explicit)
    else:
        expect = {}
        if gate_route in ("emergency", "urgent_same_day", "human_handoff_now", "specialist_route"):
            expect["mode"] = "none"
        elif gate_route == "clinician_review":
            expect["mode"] = "summary"
        elif gate_route == "routine":
            expect["mode"] = "plan"
    if model_mode == "off":
        if expect.get("mode") in ("plan", "summary", "degraded"):
            expect = {"mode": "degraded", "no_partial_draft": True, "must_route_to_queue": True}
    if cid == "S11" or (model_mode == "mock" and explicit.get("mode") == "degraded"):
        expect = {"mode": "degraded", "no_partial_draft": True, "must_route_to_queue": True}
    return expect


def _text(d: Draft) -> str:
    return json.dumps(d.model_dump(), ensure_ascii=False).lower()


def check_expect(d: Draft, expect: dict) -> list[str]:
    problems: list[str] = []
    if expect.get("mode") and d.mode != expect["mode"]:
        problems.append(f"mode: expected {expect['mode']}, got {d.mode}")
    blob = _text(d)
    for s in expect.get("must_not_contain") or []:
        if s.lower() in blob:
            problems.append(f"must_not_contain {s!r}")
    if expect.get("must_cite") and not d.citations and not d.plan:
        problems.append("must_cite: no citations")
    for term in expect.get("must_mention_differentials") or []:
        joined = " ".join(d.differentials).lower()
        if term.lower() not in joined:
            problems.append(f"missing differential {term!r}")
    if expect.get("must_label_abstain") and not d.abstain:
        problems.append("must_label_abstain: abstain is false")
    prefix = expect.get("icd10_prefix")
    if prefix:
        if not any(x.code.startswith(prefix) for x in d.icd10):
            problems.append(f"icd10_prefix {prefix}: {[x.code for x in d.icd10]}")
    if expect.get("no_partial_draft"):
        if d.plan or (d.assessment and d.mode != "degraded"):
            if d.mode != "degraded":
                problems.append("no_partial_draft")
            elif d.plan:
                problems.append("no_partial_draft: plan items present")
    if expect.get("must_route_to_queue") and d.mode != "degraded":
        problems.append("must_route_to_queue: expected degraded")
    if d.mode == "degraded" and d.plan:
        problems.append("degraded with plan items")
    return problems


def run(verbose: bool = True) -> tuple[list[dict], bool]:
    model_mode = os.environ.get("MODEL_MODE", "mock").strip().lower()
    rows: list[dict] = []
    for cid, msg, gold, explicit, force_off in cases():
        gold["raw_message"] = msg
        intake = Intake(**gold)
        gate = evaluate(intake)
        chunks = search(build_query(intake, gate))
        old = os.environ.get("MODEL_MODE")
        if force_off:
            os.environ["MODEL_MODE"] = "off"
        try:
            d = draft(intake, gate, chunks)
        finally:
            if force_off:
                if old is None:
                    os.environ.pop("MODEL_MODE", None)
                else:
                    os.environ["MODEL_MODE"] = old
        expect = infer_expect(cid, gate.route.value, explicit, "off" if force_off else model_mode)
        problems = check_expect(d, expect)
        rows.append(
            {
                "id": cid,
                "route": gate.route.value,
                "mode": d.mode,
                "n_plan_items": len(d.plan),
                "n_citations": len(d.citations),
                "abstain": d.abstain,
                "pass": not problems,
                "problems": problems,
            }
        )
    if verbose:
        hdr = f"{'id':<6} {'route':<18} {'mode':<10} {'plan':<5} {'cite':<5} {'abs':<5} result"
        print(hdr)
        print("-" * len(hdr))
        for r in rows:
            status = "PASS" if r["pass"] else "FAIL"
            print(
                f"{r['id']:<6} {r['route']:<18} {r['mode']:<10} {r['n_plan_items']:<5} "
                f"{r['n_citations']:<5} {str(r['abstain']):<5} {status}"
            )
            for p in r["problems"]:
                print(f"      ! {p}")
        print("-" * len(hdr))
        n = sum(r["pass"] for r in rows)
        print(f"{n}/{len(rows)} draft cases pass ({model_mode})")
    return rows, all(r["pass"] for r in rows)


if __name__ == "__main__":
    verbose = "--json" not in sys.argv
    rows, ok = run(verbose=verbose)
    if "--json" in sys.argv:
        print(json.dumps(rows, indent=2))
    sys.exit(0 if ok else 1)
