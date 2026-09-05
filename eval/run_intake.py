"""Intake-stage eval.

Runs extract() on each fixture message (and variant) and compares the fields
listed in BUILD-PLAN step 4 against gold_intake.

Usage: MODEL_MODE=mock python -m eval.run_intake
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from digidoc.intake.extract import extract
from digidoc.models import Intake

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "scenarios.json"
COMPARE_FIELDS = (
    "symptoms",
    "age_years",
    "pregnancy_status",
    "implanted_device",
    "recent_surgery_days",
    "chronic_conditions",
)


def load_scenarios() -> list[dict]:
    return json.loads(FIXTURES.read_text(encoding="utf-8"))["scenarios"]


def cases() -> list[tuple[str, str, dict]]:
    out: list[tuple[str, str, dict]] = []
    for sc in load_scenarios():
        out.append((sc["id"], sc["message"], dict(sc["gold_intake"])))
        if "variant" in sc:
            v = sc["variant"]
            gold = dict(sc["gold_intake"])
            gold.update(v.get("gold_intake_patch") or {})
            out.append((v["name"].split(" ")[0], v["message"], gold))
    return out


def _norm_list(val) -> list:
    if not val:
        return []
    return list(val)


def _age_match(got, expected) -> bool:
    if got is None and expected is None:
        return True
    if got is None or expected is None:
        return False
    return abs(float(got) - float(expected)) < 0.02


def field_match(intake: Intake, gold: dict, field: str) -> bool:
    got = getattr(intake, field)
    expected = gold.get(field)
    if field in ("symptoms", "chronic_conditions"):
        return set(_norm_list(got)) == set(_norm_list(expected))
    if field == "age_years":
        return _age_match(got, expected)
    if field == "pregnancy_status":
        exp = expected if expected is not None else "na"
        return got.value == exp
    return got == expected


def run(verbose: bool = True) -> list[dict]:
    rows: list[dict] = []
    extra_ok = True
    extra_problems: list[str] = []

    for cid, msg, gold in cases():
        intake = extract(msg, None)
        matches = {f: field_match(intake, gold, f) for f in COMPARE_FIELDS}
        problems = [f for f, ok in matches.items() if not ok]
        if cid == "S9":
            if not intake.unparsed_spans:
                extra_ok = False
                extra_problems.append("S9: unparsed_spans empty")
                problems.append("unparsed_spans")
        if cid == "S10":
            if not intake.injected_instructions:
                extra_ok = False
                extra_problems.append("S10: injected_instructions empty")
                problems.append("injected_instructions")
        rows.append(
            {
                "id": cid,
                "matches": matches,
                "pass": not problems,
                "problems": problems,
                "got": {f: getattr(intake, f) for f in COMPARE_FIELDS},
            }
        )

    if verbose:
        hdr = f"{'id':<6}" + "".join(f"{f[:8]:<10}" for f in COMPARE_FIELDS) + "result"
        print(hdr)
        print("-" * len(hdr))
        n_field_ok = 0
        n_field = 0
        for r in rows:
            cells = ""
            for f in COMPARE_FIELDS:
                n_field += 1
                ok = r["matches"][f]
                if ok:
                    n_field_ok += 1
                cells += f"{'Y' if ok else 'N':<10}"
            status = "PASS" if r["pass"] else "FAIL"
            print(f"{r['id']:<6}{cells}{status}")
            for p in r["problems"]:
                print(f"      ! {p}: {r['got'].get(p, '')}")
        print("-" * len(hdr))
        acc = 100.0 * n_field_ok / n_field if n_field else 0.0
        print(f"accuracy: {n_field_ok}/{n_field} fields ({acc:.1f}%)")
        for p in extra_problems:
            print(f"! {p}")
        n_pass = sum(r["pass"] for r in rows)
        print(f"{n_pass}/{len(rows)} intake cases pass")

    all_pass = extra_ok and all(r["pass"] for r in rows)
    return rows, all_pass


if __name__ == "__main__":
    verbose = "--json" not in sys.argv
    rows, all_pass = run(verbose=verbose)
    if "--json" in sys.argv:
        print(json.dumps([{k: v for k, v in r.items() if k != "got"} for r in rows], indent=2, default=str))
    mode = os.environ.get("MODEL_MODE", "mock").strip().lower()
    if mode == "mock" and not all_pass:
        sys.exit(1)
    sys.exit(0)
