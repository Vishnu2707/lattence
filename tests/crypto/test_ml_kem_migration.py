import pytest
from lattence_crypto.pqc import (
    CryptoDependencyGraph,
    CryptoGraphNode,
    assess_ml_kem_migration,
)


def _graph(*algorithms: CryptoGraphNode) -> CryptoDependencyGraph:
    return CryptoDependencyGraph(nodes=algorithms, edges=())


def _key_exchange(name: str, status: str) -> CryptoGraphNode:
    return CryptoGraphNode(
        id=f"algorithm:{name}",
        kind="algorithm",
        name=name,
        quantum_status=status,
        purpose="key exchange",
    )


def test_ml_kem_reports_existing_migration() -> None:
    result = assess_ml_kem_migration(_graph(_key_exchange("ML-KEM-768", "safe")))

    assert result.status == "already_migrated"
    assert result.compatible is True


def test_ml_kem_prefers_hybrid_transition_for_vulnerable_exchange() -> None:
    result = assess_ml_kem_migration(
        _graph(_key_exchange("X25519", "vulnerable")),
        supported_groups=("x25519", "ML-KEM-768"),
        hybrid_supported=True,
    )

    assert result.status == "hybrid_ready"
    assert result.affected_node_ids == ("algorithm:X25519",)
    assert "classical + ML-KEM-768" in result.required_changes[0]


@pytest.mark.parametrize(
    ("graph", "supported", "factor"),
    [
        (_graph(), (), "no key-exchange assets discovered"),
        (
            _graph(_key_exchange("ECDHE", "vulnerable")),
            ("X25519",),
            "runtime does not advertise ML-KEM-768",
        ),
    ],
)
def test_ml_kem_reports_blocking_factors(
    graph: CryptoDependencyGraph, supported: tuple[str, ...], factor: str
) -> None:
    result = assess_ml_kem_migration(graph, supported_groups=supported)

    assert result.status == "blocked"
    assert result.blocking_factors == (factor,)
