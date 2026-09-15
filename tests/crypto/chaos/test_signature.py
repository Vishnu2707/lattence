import sys
from pathlib import Path

import pytest
from lattence_crypto.chaos import (
    UnsafeCryptoMutation,
    execute_signature_downgrade,
    plan_crypto_mutation,
)


def test_executes_signature_downgrade_and_restores_original(tmp_path: Path) -> None:
    target = tmp_path / "tls.conf"
    original = "signature = ML-DSA-65\n"
    target.write_text(original, encoding="utf-8")
    plan = plan_crypto_mutation(
        tmp_path,
        "tls.conf",
        declared_paths=("tls.conf",),
        before_fragment="ML-DSA-65",
        after_fragment="ECDSA",
        dry_run=False,
    )
    command = (
        sys.executable,
        "-c",
        "from pathlib import Path; "
        "raise SystemExit('ECDSA' not in Path('tls.conf').read_text())",
    )

    result = execute_signature_downgrade(
        tmp_path, plan, probe_command=command
    )

    assert result.experiment == "signature-downgrade"
    assert result.downgrade_accepted is True
    assert result.rollback_verified is True
    assert target.read_text(encoding="utf-8") == original


def test_refuses_nonclassical_signature_destination(tmp_path: Path) -> None:
    (tmp_path / "tls.conf").write_text(
        "signature = ML-DSA-65\n", encoding="utf-8"
    )
    plan = plan_crypto_mutation(
        tmp_path,
        "tls.conf",
        declared_paths=("tls.conf",),
        before_fragment="ML-DSA-65",
        after_fragment="HMAC",
        dry_run=False,
    )

    with pytest.raises(UnsafeCryptoMutation, match="classical algorithm"):
        execute_signature_downgrade(
            tmp_path, plan, probe_command=(sys.executable, "-c", "")
        )
