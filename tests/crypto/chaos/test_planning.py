from pathlib import Path

import pytest
from lattence_crypto.chaos import UnsafeCryptoMutation, plan_crypto_mutation


def test_plans_declared_bounded_mutation_without_writing(tmp_path: Path) -> None:
    target = tmp_path / "tls.conf"
    target.write_text("group = ML-KEM-768\n", encoding="utf-8")

    plan = plan_crypto_mutation(
        tmp_path,
        "tls.conf",
        declared_paths=("tls.conf",),
        before_fragment="ML-KEM-768",
        after_fragment="X25519",
    )

    assert plan.target_path == "tls.conf"
    assert plan.replacements == 1
    assert plan.dry_run is True
    assert target.read_text(encoding="utf-8") == "group = ML-KEM-768\n"


@pytest.mark.parametrize(
    ("target_path", "declared", "message"),
    [
        ("tls.conf", (), "not declared"),
        ("../tls.conf", ("../tls.conf",), "project-relative"),
        ("tls.conf", ("tls.conf",), "not found"),
    ],
)
def test_refuses_unsafe_mutation_plans(
    tmp_path: Path,
    target_path: str,
    declared: tuple[str, ...],
    message: str,
) -> None:
    (tmp_path / "tls.conf").write_text("group = X25519\n", encoding="utf-8")

    with pytest.raises(UnsafeCryptoMutation, match=message):
        plan_crypto_mutation(
            tmp_path,
            target_path,
            declared_paths=declared,
            before_fragment="ML-KEM-768",
            after_fragment="X25519",
        )


def test_refuses_unbounded_timeout(tmp_path: Path) -> None:
    (tmp_path / "tls.conf").write_text("group = ML-KEM-768\n", encoding="utf-8")

    with pytest.raises(UnsafeCryptoMutation, match="at most 60"):
        plan_crypto_mutation(
            tmp_path,
            "tls.conf",
            declared_paths=("tls.conf",),
            before_fragment="ML-KEM-768",
            after_fragment="X25519",
            timeout_seconds=61,
        )
