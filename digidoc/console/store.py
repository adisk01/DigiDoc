"""Small SQLite store for console cases and immutable action history."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = ROOT / "data" / "digidoc.db"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def init_db() -> None:
    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS cases (
              id TEXT PRIMARY KEY,
              session_id TEXT NOT NULL,
              message TEXT NOT NULL,
              intake_json TEXT NOT NULL,
              gate_json TEXT NOT NULL,
              draft_json TEXT,
              chunks_json TEXT NOT NULL,
              consult_json TEXT,
              created_at TEXT NOT NULL,
              signed_by TEXT,
              signed_at TEXT,
              frozen INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS actions (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
              action TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              actor TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            """
        )
        columns = {row["name"] for row in db.execute("PRAGMA table_info(cases)")}
        if "consult_json" not in columns:
            db.execute("ALTER TABLE cases ADD COLUMN consult_json TEXT")


def insert_case(
    *,
    case_id: str,
    session_id: str,
    message: str,
    intake: dict[str, Any],
    gate: dict[str, Any],
    draft: dict[str, Any] | None,
    chunks: list[dict[str, Any]],
) -> None:
    created = now_iso()
    with connect() as db:
        db.execute(
            """INSERT OR REPLACE INTO cases
               (id, session_id, message, intake_json, gate_json, draft_json,
                chunks_json, consult_json, created_at, signed_by, signed_at, frozen)
               VALUES (?, ?, ?, ?, ?, ?, ?, NULL, ?,
                       COALESCE((SELECT signed_by FROM cases WHERE id=?), NULL),
                       COALESCE((SELECT signed_at FROM cases WHERE id=?), NULL),
                       COALESCE((SELECT frozen FROM cases WHERE id=?), 0))""",
            (
                case_id,
                session_id,
                message,
                json.dumps(intake, ensure_ascii=False),
                json.dumps(gate, ensure_ascii=False),
                json.dumps(draft, ensure_ascii=False) if draft is not None else None,
                json.dumps(chunks, ensure_ascii=False),
                created,
                case_id,
                case_id,
                case_id,
            ),
        )
        db.execute(
            """INSERT INTO actions(case_id, action, payload_json, actor, created_at)
               VALUES (?, 'created', '{}', 'sistem', ?)""",
            (case_id, created),
        )


def get_case(case_id: str) -> sqlite3.Row | None:
    with connect() as db:
        return db.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()


def list_cases() -> list[sqlite3.Row]:
    with connect() as db:
        return db.execute("SELECT * FROM cases").fetchall()


def actions_for(case_id: str) -> list[sqlite3.Row]:
    with connect() as db:
        return db.execute(
            "SELECT * FROM actions WHERE case_id=? ORDER BY id", (case_id,)
        ).fetchall()


def add_action(case_id: str, action: str, payload: dict[str, Any], actor: str) -> None:
    with connect() as db:
        db.execute(
            """INSERT INTO actions(case_id, action, payload_json, actor, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                case_id,
                action,
                json.dumps(payload, ensure_ascii=False),
                actor,
                now_iso(),
            ),
        )


def update_draft(case_id: str, draft: dict[str, Any]) -> None:
    with connect() as db:
        db.execute(
            "UPDATE cases SET draft_json=? WHERE id=?",
            (json.dumps(draft, ensure_ascii=False), case_id),
        )


def update_consult(case_id: str, result: dict[str, Any]) -> None:
    with connect() as db:
        db.execute(
            "UPDATE cases SET consult_json=? WHERE id=?",
            (json.dumps(result, ensure_ascii=False), case_id),
        )


def sign_case(case_id: str, doctor_id: str) -> str:
    signed_at = now_iso()
    with connect() as db:
        db.execute(
            """UPDATE cases SET signed_by=?, signed_at=?, frozen=1
               WHERE id=? AND frozen=0""",
            (doctor_id, signed_at, case_id),
        )
    return signed_at


def clear_demo() -> None:
    with connect() as db:
        db.execute("DELETE FROM actions")
        db.execute("DELETE FROM cases")
