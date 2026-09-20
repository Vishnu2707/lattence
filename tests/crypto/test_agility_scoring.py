from lattence.graph import SourceRef
from lattence_crypto.agility import score_crypto_agility
from lattence_crypto.pqc import (
    CryptoDependencyGraph,
    CryptoGraphNode,
    MLDSAMigration,
    MLKEMMigration,
    QuantumExposure,
    QuantumVulnerableAsset,
)
from lattence_crypto.tls import HybridTLSValidation


def _migration(kind: str, compatible: bool = True) -> MLKEMMigration | MLDSAMigration:
    migration_type = MLKEMMigration if kind == "kem" else MLDSAMigration
    return migration_type(
        target="target",
        status="already_migrated" if compatible else "blocked",
        compatible=compatible,
        affected_node_ids=(),
        required_changes=(),
        blocking_factors=() if compatible else ("blocked",),
    )


def _hybrid(status: str = "valid") -> HybridTLSValidation:
    return HybridTLSValidation(
        status="valid" if status == "valid" else "invalid",
        tls_13=status == "valid",
        hybrid_key_exchange=status == "valid",
        hybrid_signature=status == "valid",
        node_ids=(),
        issues=() if status == "valid" else ("missing",),
    )


def test_scores_complete_crypto_agility_at_one_hundred() -> None:
    graph = CryptoDependencyGraph(
        nodes=(
            CryptoGraphNode(
                id="algorithm:ml-kem",
                kind="algorithm",
                name="ML-KEM-768",
                source_path=SourceRef(path="tls.py").path,
                implementation="tls.py",
                purpose="key exchange",
                quantum_status="safe",
            ),
            CryptoGraphNode(
                id="tls:1.3",
                kind="tls_configuration",
                name="TLS 1.3",
                source_path="tls.py",
            ),
        ),
        edges=(),
    )

    score = score_crypto_agility(
        graph,
        quantum_exposure=QuantumExposure(isolated_assets=(), paths=()),
        ml_kem=_migration("kem"),
        ml_dsa=_migration("dsa"),
        hybrid_tls=_hybrid(),
        downgrade_resistant=True,
    )

    assert score.percentage == 100
    assert score.limiting_factors == ()


def test_scores_and_names_every_limiting_factor() -> None:
    graph = CryptoDependencyGraph(
        nodes=(
            CryptoGraphNode(
                id="algorithm:rsa",
                kind="algorithm",
                name="RSA",
                quantum_status="vulnerable",
                purpose="signature",
            ),
        ),
        edges=(),
    )
    asset = QuantumVulnerableAsset(
        target_id="algorithm:rsa",
        source_paths=(),
    )

    score = score_crypto_agility(
        graph,
        quantum_exposure=QuantumExposure(isolated_assets=(asset,), paths=()),
        ml_kem=_migration("kem", False),
        ml_dsa=_migration("dsa", False),
        hybrid_tls=_hybrid("invalid"),
    )

    assert score.percentage == 15
    assert len(score.limiting_factors) == 5
    assert [component.name for component in score.components] == sorted(
        component.name for component in score.components
    )
