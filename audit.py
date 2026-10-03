"""Durable review history: a small SQLite audit trail for advisor approval decisions."""

from __future__ import annotations

import csv
import io
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(os.getenv("BRIEFLY_AUDIT_DB", Path(__file__).parent / "audit.db"))
COLUMNS = ["id", "reviewed_at", "client_id", "action", "details", "proposed_at", "decision", "reviewer"]


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT, reviewed_at TEXT NOT NULL, client_id TEXT, action TEXT NOT NULL,
            details TEXT, proposed_at TEXT, decision TEXT NOT NULL, reviewer TEXT NOT NULL)"""
    )
    return conn


def record(proposal: dict, decision: str, client_id: str | None, reviewer: str = "Advisor (demo)") -> None:
    """Persist one approve/reject decision. Recording a decision never executes the proposed action."""
    with _connect() as conn:
        conn.execute(
            "INSERT INTO audit (reviewed_at, client_id, action, details, proposed_at, decision, reviewer) VALUES (?,?,?,?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(timespec="seconds"), client_id, proposal.get("action", ""),
             proposal.get("details", ""), proposal.get("timestamp", ""), decision, reviewer),
        )


def entries(limit: int | None = None) -> list[dict]:
    query = "SELECT " + ", ".join(COLUMNS) + " FROM audit ORDER BY id DESC" + (f" LIMIT {int(limit)}" if limit else "")
    with _connect() as conn:
        return [dict(zip(COLUMNS, row)) for row in conn.execute(query).fetchall()]


def to_csv() -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=COLUMNS)
    writer.writeheader()
    writer.writerows(entries())
    return buffer.getvalue()
