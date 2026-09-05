"""Single chokepoint for model calls.

MODEL_MODE=real|mock|off. Every call is logged to data/log.jsonl.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "scenarios.json"
LOG_PATH = ROOT / "data" / "log.jsonl"
DEFAULT_MODEL = "gpt-5.6-luna"


class ModelUnavailable(Exception):
    """MODEL_MODE=off, or the provider could not be reached."""


def _mode() -> str:
    return os.environ.get("MODEL_MODE", "mock").strip().lower()


def _model_name() -> str:
    return os.environ.get("DIGIDOC_MODEL", DEFAULT_MODEL)


def api_key() -> str:
    """OPENAI_API_KEY from the environment, else the local (uncommitted) config file.

    The config module is reloaded on every read: Python caches imports, so editing the
    file while the console is running would otherwise have no effect until a restart.
    """
    from_env = os.environ.get("OPENAI_API_KEY", "").strip()
    if from_env:
        return from_env
    try:
        import importlib

        from digidoc import local_config

        importlib.reload(local_config)
        return str(local_config.OPENAI_API_KEY or "").strip()
    except Exception:
        return ""


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _log(
    *,
    input_hash: str,
    mode: str,
    model: str,
    latency_ms: int,
    output_hash: str | None,
    error: str | None,
) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "input_hash": input_hash,
        "mode": mode,
        "model": model,
        "latency_ms": latency_ms,
        "output_hash": output_hash,
        "error": error,
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _load_scenarios() -> list[dict]:
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    return data["scenarios"]


def _with_confidence(gold: dict, scenario_id: str, message: str) -> dict:
    out = dict(gold)
    out.setdefault("raw_message", message)
    out.setdefault("symptoms", [])
    out.setdefault("chronic_conditions", [])
    out.setdefault("medications", [])
    out.setdefault("allergies", [])
    out.setdefault("unparsed_spans", [])
    out.setdefault("injected_instructions", [])
    keys = [
        "patient_is_self",
        "age_years",
        "sex",
        "pregnancy_status",
        "pregnancy_weeks",
        "recent_surgery_days",
        "implanted_device",
        "chronic_conditions",
        "medications",
        "allergies",
        "chief_complaint",
        "duration_days",
        "fever_days",
        "symptoms",
        "unparsed_spans",
        "injected_instructions",
    ]
    conf = {k: 0.95 for k in keys}
    if scenario_id == "S9":
        conf["chief_complaint"] = 0.55
        if not out.get("unparsed_spans"):
            out["unparsed_spans"] = ["masuk angin", "rasane ora kepenak"]
    out["field_confidence"] = conf
    return out


def _canned_json(mock_key: str | None, user: str) -> str:
    """Return gold_intake JSON for the fixture matching mock_key or the user text."""
    if mock_key and str(mock_key).startswith("draft:"):
        from digidoc.draft.canned import canned_json

        language, _, needle = str(mock_key)[6:].partition(":")
        return canned_json(needle, language)
    if mock_key and str(mock_key).startswith("layer2:"):
        from digidoc.specialist.diabetic_foot.canned import canned_json

        language, _, needle = str(mock_key)[7:].partition(":")
        return canned_json(needle, language)
    needle = mock_key if mock_key is not None else user
    for sc in _load_scenarios():
        if needle in (sc["id"], sc["message"]):
            payload = _with_confidence(sc["gold_intake"], sc["id"], sc["message"])
            return json.dumps(payload, ensure_ascii=False)
        variant = sc.get("variant")
        if not variant:
            continue
        vid = variant["name"].split(" ")[0]
        if needle in (vid, variant["message"]):
            gold = dict(sc["gold_intake"])
            gold.update(variant.get("gold_intake_patch") or {})
            payload = _with_confidence(gold, vid, variant["message"])
            return json.dumps(payload, ensure_ascii=False)
    raise ModelUnavailable(f"no canned output for mock_key={needle!r}")


def complete(
    system: str,
    user: str,
    json_schema: dict | None = None,
    mock_key: str | None = None,
) -> str:
    """Run one completion. json_schema is enforced in real mode via JSON mode."""
    mode = _mode()
    model = _model_name()
    schema_blob = json.dumps(json_schema, sort_keys=True) if json_schema else ""
    input_hash = _hash(system + "\n" + user + "\n" + schema_blob)
    t0 = time.perf_counter()

    if mode == "off":
        _log(
            input_hash=input_hash,
            mode=mode,
            model=model,
            latency_ms=int((time.perf_counter() - t0) * 1000),
            output_hash=None,
            error="ModelUnavailable",
        )
        raise ModelUnavailable("MODEL_MODE=off")

    if mode == "mock":
        try:
            out = _canned_json(mock_key, user)
            _log(
                input_hash=input_hash,
                mode=mode,
                model="mock",
                latency_ms=int((time.perf_counter() - t0) * 1000),
                output_hash=_hash(out),
                error=None,
            )
            return out
        except Exception as exc:
            _log(
                input_hash=input_hash,
                mode=mode,
                model="mock",
                latency_ms=int((time.perf_counter() - t0) * 1000),
                output_hash=None,
                error=type(exc).__name__,
            )
            raise

    if mode != "real":
        _log(
            input_hash=input_hash,
            mode=mode,
            model=model,
            latency_ms=int((time.perf_counter() - t0) * 1000),
            output_hash=None,
            error="unknown_mode",
        )
        raise ModelUnavailable(f"unknown MODEL_MODE={mode!r}")

    try:
        out = _openai_complete(system, user, json_schema, model)
        _log(
            input_hash=input_hash,
            mode=mode,
            model=model,
            latency_ms=int((time.perf_counter() - t0) * 1000),
            output_hash=_hash(out),
            error=None,
        )
        return out
    except Exception as exc:
        _log(
            input_hash=input_hash,
            mode=mode,
            model=model,
            latency_ms=int((time.perf_counter() - t0) * 1000),
            output_hash=None,
            error=type(exc).__name__,
        )
        if isinstance(exc, ModelUnavailable):
            raise
        raise ModelUnavailable(str(exc)) from exc


def _openai_complete(system: str, user: str, json_schema: dict | None, model: str) -> str:
    from openai import OpenAI

    key = api_key()
    if not key:
        raise ModelUnavailable(
            "No OpenAI key: set OPENAI_API_KEY or fill OPENAI_API_KEY in digidoc/local_config.py"
        )
    sys_prompt = system
    if json_schema:
        sys_prompt += (
            "\n\nRespond with a single JSON object matching this schema and no other text:\n"
            + json.dumps(json_schema, ensure_ascii=False)
        )
    kwargs: dict = {
        "model": model,
        "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user}],
        "max_completion_tokens": 4096,
    }
    if json_schema:
        kwargs["response_format"] = {"type": "json_object"}
    client = OpenAI(api_key=key)
    out = (client.chat.completions.create(**kwargs).choices[0].message.content or "").strip()
    if not out:
        raise ModelUnavailable("empty model response")
    return out
