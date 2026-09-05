"""Combined eval: gate → intake → draft → layer2.

Usage: python -m eval.run_all --mode mock|off|real
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from eval.run_draft import run as run_draft
from eval.run_gate import run as run_gate
from eval.run_intake import run as run_intake
from eval.run_layer2 import run as run_layer2

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

PRIMARY = [f"S{i}" for i in range(1, 13)]

METRICS = [
    ("red-flag catch rate", ["S2", "S5", "S6", "S7", "S10"], "gate"),
    ("guideline concordance", ["S1", "S3", "S6"], "gate+draft"),
    ("antibiotic appropriateness", ["S1", "S3"], "draft"),
    ("referral appropriateness", ["S3", "S4"], "referral"),
    ("abstention", ["S4", "S8", "S12"], "gate+draft"),
    ("extraction calibration", ["S9"], "intake"),
    ("fail-safe", ["S10", "S11"], "failsafe"),
]


def _index(rows: list[dict]) -> dict[str, dict]:
    return {r["id"]: r for r in rows}


def _pass(idx: dict[str, dict], cid: str) -> bool | None:
    row = idx.get(cid)
    if row is None:
        return None
    return bool(row["pass"])


def _cell(ok: bool | None) -> str:
    if ok is None:
        return "—"
    return "PASS" if ok else "FAIL"


def _ok(idx: dict[str, dict], cid: str) -> bool:
    return _pass(idx, cid) is True


def metric_ok(name: str, cid: str, gate, intake, draft, layer2) -> bool:
    if name == "gate":
        return _ok(gate, cid)
    if name == "intake":
        return _ok(intake, cid)
    if name == "draft":
        return _ok(draft, cid)
    if name == "gate+draft":
        return _ok(gate, cid) and _ok(draft, cid)
    if name == "referral":
        if cid == "S3":
            return _ok(layer2, "S3")
        return _ok(gate, cid)
    if name == "failsafe":
        if cid == "S11":
            return _ok(draft, cid)
        return _ok(gate, cid) and _ok(intake, cid)
    return False


def combined_rows(ids: list[str], gate, intake, draft, layer2) -> list[dict]:
    out = []
    for cid in ids:
        g, i, d = _pass(gate, cid), _pass(intake, cid), _pass(draft, cid)
        l2 = _pass(layer2, cid) if cid in layer2 else None
        applicable = [x for x in (g, i, d) if x is not None]
        if l2 is not None:
            applicable.append(l2)
        overall = all(applicable) if applicable else False
        out.append(
            {
                "id": cid,
                "gate": _cell(g),
                "intake": _cell(i),
                "draft": _cell(d),
                "layer2": _cell(l2),
                "overall": "PASS" if overall else "FAIL",
            }
        )
    return out


def counts(rows: list[dict], ids: list[str] | None = None) -> tuple[int, int]:
    subset = [r for r in rows if ids is None or r["id"] in ids]
    return sum(1 for r in subset if r["pass"]), len(subset)


def print_table(rows: list[dict], g_n, i_n, d_n, l_n) -> None:
    print(f"{'id':<6} {'gate':<7} {'intake':<8} {'draft':<7} {'layer2':<8} overall")
    for r in rows:
        print(f"{r['id']:<6} {r['gate']:<7} {r['intake']:<8} {r['draft']:<7} {r['layer2']:<8} {r['overall']}")
    print(f"{g_n[0]}/{g_n[1]} gate · {i_n[0]}/{i_n[1]} intake · {d_n[0]}/{d_n[1]} draft · {l_n[0]}/{l_n[1]} layer2")


def print_metrics(gate, intake, draft, layer2) -> list[dict]:
    print()
    block = []
    for label, ids, how in METRICS:
        n = sum(1 for cid in ids if metric_ok(how, cid, gate, intake, draft, layer2))
        block.append({"metric": label, "ids": ids, "pass": n, "n": len(ids)})
        print(f"{label:<32} {n}/{len(ids)}")
    return block


def save(payload: dict, mode: str) -> Path:
    DATA.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = DATA / f"eval_{mode}_{ts}.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path


def run(mode: str) -> dict:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    os.environ["MODEL_MODE"] = mode
    gate_rows = run_gate(verbose=False)
    gate = _index(gate_rows)
    intake_rows, _ = run_intake(verbose=False)
    intake = _index(intake_rows)
    draft_rows, _ = run_draft(verbose=False)
    draft = _index(draft_rows)
    layer2_rows, _ = run_layer2(verbose=False)
    layer2 = _index(layer2_rows)

    table = combined_rows([r["id"] for r in gate_rows], gate, intake, draft, layer2)
    g_n = counts(list(gate.values()))
    i_n = counts(list(intake.values()))
    d_n = counts(list(draft.values()), PRIMARY)
    l_n = counts(list(layer2.values()))
    print_table(table, g_n, i_n, d_n, l_n)
    metrics = print_metrics(gate, intake, draft, layer2)
    payload = {
        "mode": mode,
        "ts": datetime.now(timezone.utc).isoformat(),
        "table": table,
        "totals": {
            "gate": f"{g_n[0]}/{g_n[1]}",
            "intake": f"{i_n[0]}/{i_n[1]}",
            "draft": f"{d_n[0]}/{d_n[1]}",
            "layer2": f"{l_n[0]}/{l_n[1]}",
        },
        "metrics": metrics,
        "stages": {
            "gate": list(gate.values()),
            "intake": [{k: v for k, v in r.items() if k != "got"} for r in intake.values()],
            "draft": list(draft.values()),
            "layer2": list(layer2.values()),
        },
    }
    path = save(payload, mode)
    print(f"\nsaved {path}")
    return payload


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=("mock", "off", "real"), default="mock")
    args = p.parse_args()
    payload = run(args.mode)
    return 0 if all(r["overall"] == "PASS" for r in payload["table"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
