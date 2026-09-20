import hashlib
import secrets
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .roles import Role

_SCHEMA = """
CREATE TABLE IF NOT EXISTS api_keys (
    key_hash TEXT PRIMARY KEY,
    caller_id TEXT NOT NULL,
    roles TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class ResolvedIdentity:
    caller_id: str
    roles: frozenset[Role]


@dataclass(frozen=True)
class ApiKeyRecord:
    caller_id: str
    roles: frozenset[Role]
    created_at: str


def _hash_key(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


class ApiKeyStore:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def create_key(self, caller_id: str, roles: frozenset[Role]) -> str:
        key = secrets.token_hex(32)
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO api_keys (key_hash, caller_id, roles, created_at) "
                "VALUES (?, ?, ?, ?)",
                (
                    _hash_key(key),
                    caller_id,
                    ",".join(sorted(role.value for role in roles)),
                    datetime.now(UTC).isoformat(),
                ),
            )
        return key

    def resolve(self, presented_key: str) -> ResolvedIdentity | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT caller_id, roles FROM api_keys WHERE key_hash = ?",
                (_hash_key(presented_key),),
            ).fetchone()
        if row is None:
            return None
        caller_id, roles_csv = row
        roles = frozenset(Role(value) for value in roles_csv.split(",") if value)
        return ResolvedIdentity(caller_id=caller_id, roles=roles)

    def list_keys(self) -> tuple[ApiKeyRecord, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT caller_id, roles, created_at FROM api_keys ORDER BY created_at"
            ).fetchall()
        return tuple(
            ApiKeyRecord(
                caller_id=caller_id,
                roles=frozenset(Role(value) for value in roles_csv.split(",") if value),
                created_at=created_at,
            )
            for caller_id, roles_csv, created_at in rows
        )

    def revoke_caller(self, caller_id: str) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM api_keys WHERE caller_id = ?", (caller_id,)
            )
            return cursor.rowcount
