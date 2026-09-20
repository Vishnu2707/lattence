from pathlib import Path

import pytest
from lattence.governance import AuditLog, default_audit_db_path


def test_record_and_query_round_trip(tmp_path: Path) -> None:
    log = AuditLog(tmp_path / "audit.db")

    event = log.record(
        actor="alice",
        action="scan",
        target="examples/vulnerable-agent",
        result="completed",
        details={"findings": 13},
    )

    assert event.id == 1
    events = log.query()
    assert len(events) == 1
    assert events[0].actor == "alice"
    assert events[0].details == {"findings": 13}


def test_query_filters_by_actor_and_action(tmp_path: Path) -> None:
    log = AuditLog(tmp_path / "audit.db")
    log.record(actor="alice", action="scan", target="a", result="completed")
    log.record(actor="bob", action="attack", target="b", result="completed")
    log.record(actor="alice", action="attack", target="c", result="completed")

    assert len(log.query(actor="alice")) == 2
    assert len(log.query(action="attack")) == 2
    assert len(log.query(actor="alice", action="attack")) == 1


def test_query_orders_newest_first_and_respects_limit(tmp_path: Path) -> None:
    log = AuditLog(tmp_path / "audit.db")
    for index in range(5):
        log.record(actor="alice", action="scan", target=str(index), result="completed")

    events = log.query(limit=2)
    assert [event.target for event in events] == ["4", "3"]


def test_log_persists_across_instances(tmp_path: Path) -> None:
    db_path = tmp_path / "audit.db"
    AuditLog(db_path).record(
        actor="alice", action="policy_check", target=".", result="completed"
    )

    reopened = AuditLog(db_path)
    assert len(reopened.query()) == 1


def test_default_audit_db_path_prefers_env_var(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    configured = tmp_path / "custom-audit.db"
    monkeypatch.setenv("LATTENCE_AUDIT_DB", str(configured))

    assert default_audit_db_path() == configured


def test_default_audit_db_path_falls_back_to_out_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("LATTENCE_AUDIT_DB", raising=False)

    assert default_audit_db_path(tmp_path) == tmp_path / "lattence-audit.db"
