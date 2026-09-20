import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from lattence.graph import JsonValue

_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    target TEXT NOT NULL,
    result TEXT NOT NULL,
    details TEXT NOT NULL
);
"""

_DB_ENV_VAR = "LATTENCE_AUDIT_DB"


@dataclass(frozen=True)
class AuditEvent:
    id: int
    timestamp: str
    actor: str
    action: str
    target: str
    result: str
    details: dict[str, JsonValue]


class AuditLog:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def record(
        self,
        *,
        actor: str,
        action: str,
        target: str,
        result: str,
        details: dict[str, JsonValue] | None = None,
    ) -> AuditEvent:
        timestamp = datetime.now(UTC).isoformat()
        payload = json.dumps(details or {}, sort_keys=True)
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO audit_log (timestamp, actor, action, target, result, "
                "details) VALUES (?, ?, ?, ?, ?, ?)",
                (timestamp, actor, action, target, result, payload),
            )
            event_id = cursor.lastrowid
        assert event_id is not None
        return AuditEvent(
            id=event_id,
            timestamp=timestamp,
            actor=actor,
            action=action,
            target=target,
            result=result,
            details=details or {},
        )

    def query(
        self,
        *,
        actor: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> tuple[AuditEvent, ...]:
        clauses = []
        params: list[str] = []
        if actor is not None:
            clauses.append("actor = ?")
            params.append(actor)
        if action is not None:
            clauses.append("action = ?")
            params.append(action)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, timestamp, actor, action, target, result, details "
                f"FROM audit_log{where} ORDER BY id DESC LIMIT ?",
                (*params, limit),
            ).fetchall()
        return tuple(
            AuditEvent(
                id=row[0],
                timestamp=row[1],
                actor=row[2],
                action=row[3],
                target=row[4],
                result=row[5],
                details=json.loads(row[6]),
            )
            for row in rows
        )


def default_audit_db_path(out: Path | None = None) -> Path:
    configured = os.environ.get(_DB_ENV_VAR)
    if configured:
        return Path(configured)
    base = out if out is not None and out.is_dir() else Path.cwd()
    return base / "lattence-audit.db"
