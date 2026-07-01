from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SQLITE_TIMEOUT_SECONDS = 5.0
SQLITE_BUSY_TIMEOUT_MS = 5_000


@dataclass
class ReasoningTrace:
    trace_id: str
    timestamp: str
    operator: str
    model: str
    user_message: str
    compiled_messages: list[dict[str, str]]
    raw_model_output: str | None
    validated_output: dict[str, Any] | None
    validation_errors: list[str]
    repair_attempts: int
    final_answer: str | None

    @classmethod
    def new(cls, *, operator: str, model: str, user_message: str, compiled_messages: list[dict[str, str]]) -> "ReasoningTrace":
        return cls(
            trace_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            operator=operator,
            model=model,
            user_message=user_message,
            compiled_messages=compiled_messages,
            raw_model_output=None,
            validated_output=None,
            validation_errors=[],
            repair_attempts=0,
            final_answer=None,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TraceStore:
    def __init__(self, db_path: Path | str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=SQLITE_TIMEOUT_SECONDS)
        conn.execute(f"PRAGMA busy_timeout = {SQLITE_BUSY_TIMEOUT_MS}")
        return conn

    def _init(self) -> None:
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS traces (
                    trace_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    operator TEXT NOT NULL,
                    model TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_traces_timestamp ON traces(timestamp DESC)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_traces_operator_timestamp ON traces(operator, timestamp DESC)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_traces_model_timestamp ON traces(model, timestamp DESC)"
            )
            conn.commit()

    def save(self, trace: ReasoningTrace) -> None:
        payload = json.dumps(trace.to_dict(), ensure_ascii=False)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO traces(trace_id, timestamp, operator, model, user_message, payload)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (trace.trace_id, trace.timestamp, trace.operator, trace.model, trace.user_message, payload),
            )
            conn.commit()

    def get(self, trace_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM traces WHERE trace_id = ?", (trace_id,)).fetchone()
        if not row:
            return None
        return json.loads(row[0])

    def list_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        limit = min(max(limit, 1), 100)
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT trace_id, timestamp, operator, model, user_message FROM traces ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {"trace_id": r[0], "timestamp": r[1], "operator": r[2], "model": r[3], "user_message": r[4]}
            for r in rows
        ]
