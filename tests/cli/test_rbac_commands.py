from pathlib import Path

import pytest
from lattence.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_create_key_list_and_revoke(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "rbac.db"
    monkeypatch.setenv("LATTENCE_RBAC_DB", str(db_path))

    create = runner.invoke(app, ["rbac", "create-key", "alice", "--role", "run_scans"])
    assert create.exit_code == 0
    key = create.stdout.strip()
    assert len(key) == 64

    listing = runner.invoke(app, ["rbac", "list"])
    assert listing.exit_code == 0
    assert "alice" in listing.stdout
    assert "run_scans" in listing.stdout

    revoke = runner.invoke(app, ["rbac", "revoke", "alice"])
    assert revoke.exit_code == 0
    assert "revoked 1" in revoke.stdout

    listing_after = runner.invoke(app, ["rbac", "list"])
    assert "alice" not in listing_after.stdout


def test_create_key_without_db_configured_fails_clearly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("LATTENCE_RBAC_DB", raising=False)

    result = runner.invoke(app, ["rbac", "create-key", "alice", "--role", "run_scans"])

    assert result.exit_code != 0
    assert "LATTENCE_RBAC_DB" in result.output
