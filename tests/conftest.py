from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolated_audit_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LATTENCE_AUDIT_DB", str(tmp_path / "lattence-audit.db"))
