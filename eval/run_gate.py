"""Gate-stage eval.

Feeds each scenario's gold intake through the deterministic gate and checks:
  - route matches
  - draft_allowed matches
  - every expected rule ID fired (extra hits are reported but not failures)
  - prescreen / layer2 / safety_net expectations where given

Runs with no model, no network. This is the test you can run in CI on every commit.

Usage: python -m eval.run_gate [--json]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from digidoc.gate import evaluate
from digidoc.models import Intake

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "scenarios.json"


def load_scenarios() -> list[dict]:
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    return data["scenarios"]


def build_intake(base: dict, message: str, patch: dict | None = None) -> Intake:
    d = dict(base)
    if patch:
        d.update(patch)
    d["raw_message"] = message
    return Intake(**d)


def check(expect: dict, result) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if result.route.value != expect["route"]:
        problems.append(f"route: expected {expect['route']}, got {result.route.value}")
    if result.draft_allowed != expect["draft_allowed"]:
        problems.append(f"draft_allowed: expected {expect['draft_allowed']}, got {result.draft_allowed}")
    fired = {h.rule_id for h in result.hits}
    for rid in expect.get("hits", []):
        if rid not in fired:
            problems.append(f"missing hit {rid}")
    if not expect.get("hits") and any(not h.rule_id.startswith("R00") for h in result.hits):
        problems.append(f"expected no hits, got {sorted(fired)}")
    if expect.get("summary_only") is not None and result.summary_only != expect["summary_only"]:
        problems.append(f"summary_only: expected {expect['summary_only']}, got {result.summary_only}")
    if expect.get("prescreen_nonempty") and not result.prescreen:
        problems.append("expected prescreen questions, got none")
    for m in expect.get("layer2_modules", []):
        if m not in result.layer2_modules:
            problems.append(f"missing layer2 module {m}")
    if expect.get("safety_net_key") and result.safety_net_key != expect["safety_net_key"]:
        problems.append(f"safety_net_key: expected {expect['safety_net_key']}, got {result.safety_net_key}")
    return (not problems, problems)


def run(verbose: bool = True) -> list[dict]:
    rows: list[dict] = []
    for sc in load_scenarios():
        cases = [(sc["id"], sc["message"], sc["gold_intake"], None, sc["expect_gate"])]
        if "variant" in sc:
            v = sc["variant"]
            cases.append((v["name"].split(" ")[0], v["message"], sc["gold_intake"], v.get("gold_intake_patch"), v["expect_gate"]))
        for cid, msg, gold, patch, expect in cases:
            intake = build_intake(gold, msg, patch)
            r1 = evaluate(intake)
            r2 = evaluate(intake)
            deterministic = r1.model_dump() == r2.model_dump()
            ok, problems = check(expect, r1)
            if not deterministic:
                ok = False
                problems.append("non-deterministic result")
            rows.append(
                {
                    "id": cid,
                    "route": r1.route.value,
                    "draft_allowed": r1.draft_allowed,
                    "hits": [h.rule_id for h in r1.hits],
                    "safety_net": r1.safety_net_key,
                    "pass": ok,
                    "problems": problems,
                }
            )
    if verbose:
        print(f"{'id':<5} {'route':<18} {'draft':<6} {'hits':<48} {'result'}")
        print("-" * 96)
        for r in rows:
            hits = ",".join(r["hits"]) or "—"
            if len(hits) > 46:
                hits = hits[:43] + "..."
            status = "PASS" if r["pass"] else "FAIL"
            print(f"{r['id']:<5} {r['route']:<18} {str(r['draft_allowed']):<6} {hits:<48} {status}")
            for p in r["problems"]:
                print(f"      ! {p}")
        n_pass = sum(r["pass"] for r in rows)
        print("-" * 96)
        print(f"{n_pass}/{len(rows)} gate cases pass")
    return rows


if __name__ == "__main__":
    rows = run(verbose="--json" not in sys.argv)
    if "--json" in sys.argv:
        print(json.dumps(rows, indent=2))
    sys.exit(0 if all(r["pass"] for r in rows) else 1)
