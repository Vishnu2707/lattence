from datetime import UTC, datetime

from lattence.evidence import normalize_crypto_findings
from lattence_crypto.agility import AgilityComponent, CryptoAgilityScore
from lattence_crypto.chaos import DowngradeEvidence, DowngradeValidation
from lattence_crypto.pqc import MLDSAMigration, MLKEMMigration


def _migration(kind: str, compatible: bool):  # type: ignore[no-untyped-def]
    migration_type = MLKEMMigration if kind == "kem" else MLDSAMigration
    return migration_type(
        target="ML-KEM-768" if kind == "kem" else "ML-DSA-65",
        status="direct_ready" if compatible else "blocked",
        compatible=compatible,
        affected_node_ids=("crypto_algorithm:legacy",),
        required_changes=(),
        blocking_factors=() if compatible else ("runtime support missing",),
    )


def _agility(percentage: int) -> CryptoAgilityScore:
    factor = None if percentage == 100 else "migration incomplete"
    return CryptoAgilityScore(
        percentage=percentage,
        components=(AgilityComponent("migration_readiness", percentage, factor),),
        limiting_factors=() if factor is None else (factor,),
    )


def _downgrade(status: str) -> DowngradeValidation:
    evidence = DowngradeEvidence(
        experiment="key-exchange-downgrade",
        target_path="tls.conf",
        outcome="accepted" if status == "vulnerable" else "rejected",
        probe_returncode=0 if status == "vulnerable" else 1,
        original_sha256="a" * 64,
        mutated_sha256="b" * 64,
        rollback_verified=True,
    )
    if status == "blocked":
        return DowngradeValidation("blocked", None, (evidence,), ("timeout",))
    return DowngradeValidation(
        "vulnerable" if status == "vulnerable" else "resistant",
        status != "vulnerable",
        (evidence,),
        (),
    )


def test_normalizes_failed_crypto_results_into_frozen_finding_schema() -> None:
    findings = normalize_crypto_findings(
        "application:demo",
        datetime(2026, 1, 1, tzinfo=UTC),
        ml_kem=_migration("kem", False),
        ml_dsa=_migration("dsa", False),
        agility=_agility(20),
        downgrade=_downgrade("vulnerable"),
        tool_version="0.4.0",
    )

    assert [finding.id for finding in findings] == [
        "LT-PQC-201",
        "LT-PQC-202",
        "LT-PQC-203",
        "LT-PQC-204",
    ]
    assert all(finding.evidence.inputs for finding in findings)
    assert all(finding.reproduction.offline for finding in findings)
    assert findings[-1].severity == "critical"


def test_returns_no_findings_when_migration_agility_and_downgrade_pass() -> None:
    findings = normalize_crypto_findings(
        "application:demo",
        datetime(2026, 1, 1, tzinfo=UTC),
        ml_kem=_migration("kem", True),
        ml_dsa=_migration("dsa", True),
        agility=_agility(100),
        downgrade=_downgrade("resistant"),
    )

    assert findings == ()


def test_records_blocked_downgrade_validation_separately() -> None:
    findings = normalize_crypto_findings(
        "application:demo",
        datetime(2026, 1, 1, tzinfo=UTC),
        ml_kem=_migration("kem", True),
        ml_dsa=_migration("dsa", True),
        agility=_agility(100),
        downgrade=_downgrade("blocked"),
    )

    assert [finding.id for finding in findings] == ["LT-PQC-205"]
    assert findings[0].severity == "low"
