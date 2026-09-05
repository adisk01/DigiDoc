"""Layer-2 diabetic foot eval.

S3 exam_findings → urgent; relaxed (no necrosis, superficial) → routine.

Usage: MODEL_MODE=mock python -m eval.run_layer2
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from digidoc.gate import evaluate
from digidoc.models import Intake
from digidoc.specialist.registry import get

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "scenarios.json"
MODULE = "diabetic_foot"


def s3() -> dict:
    for sc in json.loads(FIXTURES.read_text(encoding="utf-8"))["scenarios"]:
        if sc["id"] == "S3":
            return sc
    raise SystemExit("S3 missing from fixtures")


def cases() -> list[tuple[str, dict, dict]]:
    sc = s3()
    findings = dict(sc["layer2"]["exam_findings"])
    expect = dict(sc["layer2"]["expect"])
    relaxed = dict(findings)
    relaxed["necrotic_tissue"] = False
    relaxed["depth"] = "superficial"
    return [
        ("S3", findings, expect),
        ("S3-relaxed", relaxed, {"referral": "routine"}),
    ]


def check(result, expect: dict) -> list[str]:
    problems: list[str] = []
    if result.referral != expect["referral"]:
        problems.append(f"referral: expected {expect['referral']}, got {result.referral}")
    blob = json.dumps(result.model_dump(mode="json"), ensure_ascii=False)
    for term in expect.get("must_mention") or []:
        if term.lower() not in blob.lower():
            problems.append(f"must_mention {term!r}")
    if expect.get("must_cite") and os.environ.get("MODEL_MODE", "mock").lower() != "off":
        if not result.start_now:
            problems.append("must_cite: no start_now items")
        from digidoc.specialist.diabetic_foot.module import load_chunks

        allowed = {(c["key"], c["section_id"]) for c in load_chunks()}
        for i, item in enumerate(result.start_now):
            cit = (item.citation.key, item.citation.section_id)
            if cit not in allowed:
                problems.append(f"start_now[{i}] citation {cit} not in module corpus")
    return problems


def run(verbose: bool = True) -> tuple[list[dict], bool]:
    sc = s3()
    gold = dict(sc["gold_intake"])
    gold["raw_message"] = sc["message"]
    intake = Intake(**gold)
    gate = evaluate(intake)
    module = get(MODULE)
    rows: list[dict] = []
    for cid, findings, expect in cases():
        result = module.consult(intake, gate, findings)
        problems = check(result, expect)
        rows.append(
            {
                "id": cid,
                "referral": result.referral,
                "wagner": result.grade.value,
                "n_start": len(result.start_now),
                "override": result.override,
                "pass": not problems,
                "problems": problems,
            }
        )
    if verbose:
        hdr = f"{'id':<12} {'wagner':<8} {'referral':<10} {'start':<6} {'ovr':<5} result"
        print(hdr)
        print("-" * len(hdr))
        for r in rows:
            print(
                f"{r['id']:<12} {r['wagner']:<8} {r['referral']:<10} {r['n_start']:<6} "
                f"{str(r['override']):<5} {'PASS' if r['pass'] else 'FAIL'}"
            )
            for p in r["problems"]:
                print(f"      ! {p}")
        print("-" * len(hdr))
        n = sum(r["pass"] for r in rows)
        print(f"{n}/{len(rows)} layer2 cases pass ({os.environ.get('MODEL_MODE', 'mock')})")
    return rows, all(r["pass"] for r in rows)


if __name__ == "__main__":
    verbose = "--json" not in sys.argv
    rows, ok = run(verbose=verbose)
    if "--json" in sys.argv:
        print(json.dumps(rows, indent=2))
    mode = os.environ.get("MODEL_MODE", "mock").strip().lower()
    if mode == "mock" and not ok:
        sys.exit(1)
    sys.exit(0 if ok or mode != "mock" else 1)
