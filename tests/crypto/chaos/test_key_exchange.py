import sys
from pathlib import Path

from lattence_crypto.chaos import (
    CryptoMutationPlan,
    execute_key_exchange_downgrade,
    plan_crypto_mutation,
)


def _plan(
    root: Path, *, timeout: float = 5.0, dry_run: bool = False
) -> CryptoMutationPlan:
    return plan_crypto_mutation(
        root,
        "tls.conf",
        declared_paths=("tls.conf",),
        before_fragment="ML-KEM-768",
        after_fragment="X25519",
        timeout_seconds=timeout,
        dry_run=dry_run,
    )


def test_executes_key_exchange_downgrade_and_always_rolls_back(
    tmp_path: Path,
) -> None:
    target = tmp_path / "tls.conf"
    original = "group = ML-KEM-768\n"
    target.write_text(original, encoding="utf-8")
    command = (
        sys.executable,
        "-c",
        "from pathlib import Path; "
        "raise SystemExit('X25519' not in Path('tls.conf').read_text())",
    )

    result = execute_key_exchange_downgrade(
        tmp_path, _plan(tmp_path), probe_command=command
    )

    assert result.executed is True
    assert result.downgrade_accepted is True
    assert result.rollback_verified is True
    assert target.read_text(encoding="utf-8") == original


def test_rolls_back_after_probe_timeout(tmp_path: Path) -> None:
    target = tmp_path / "tls.conf"
    original = "group = ML-KEM-768\n"
    target.write_text(original, encoding="utf-8")

    result = execute_key_exchange_downgrade(
        tmp_path,
        _plan(tmp_path, timeout=0.01),
        probe_command=(sys.executable, "-c", "import time; time.sleep(1)"),
    )

    assert result.timed_out is True
    assert result.rollback_verified is True
    assert target.read_text(encoding="utf-8") == original


def test_dry_run_does_not_execute_probe_or_mutate(tmp_path: Path) -> None:
    target = tmp_path / "tls.conf"
    original = "group = ML-KEM-768\n"
    target.write_text(original, encoding="utf-8")

    result = execute_key_exchange_downgrade(
        tmp_path,
        _plan(tmp_path, dry_run=True),
        probe_command=("does-not-exist",),
    )

    assert result.executed is False
    assert result.downgrade_accepted is None
    assert target.read_text(encoding="utf-8") == original
