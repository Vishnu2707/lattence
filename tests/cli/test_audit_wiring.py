from pathlib import Path

from lattence.cli import app
from lattence.governance import AuditLog
from typer.testing import CliRunner

runner = CliRunner()


def test_scan_records_an_audit_event(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "scan",
            "examples/vulnerable-agent",
            "--quiet",
            "--out",
            str(tmp_path),
            "--fail-on",
            "none",
        ],
    )
    assert result.exit_code == 0

    log = AuditLog(tmp_path / "lattence-audit.db")
    events = log.query(action="scan")
    assert events
    assert events[0].result == "completed"


def test_policy_check_records_an_audit_event(tmp_path: Path) -> None:
    scan = runner.invoke(
        app,
        [
            "scan",
            "examples/vulnerable-agent",
            "--quiet",
            "--out",
            str(tmp_path),
            "--fail-on",
            "none",
        ],
    )
    assert scan.exit_code == 0

    check = runner.invoke(
        app,
        [
            "policy",
            "check",
            str(tmp_path / "lattence-report.json"),
            "--scope",
            "examples/vulnerable-agent/lattence.targets.yaml",
            "--quiet",
            "--out",
            str(tmp_path),
        ],
    )
    assert check.exit_code == 0

    log = AuditLog(tmp_path / "lattence-audit.db")
    events = log.query(action="policy_check")
    assert events
    assert events[0].result == "allowed"
