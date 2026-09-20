import pytest
from lattence_crypto.pqc import (
    CryptoDependencyGraph,
    CryptoGraphNode,
    assess_ml_dsa_migration,
)


def _graph(*assets: CryptoGraphNode) -> CryptoDependencyGraph:
    return CryptoDependencyGraph(nodes=assets, edges=())


def _signature(name: str, status: str, *, kind: str = "algorithm") -> CryptoGraphNode:
    return CryptoGraphNode(
        id=f"{kind}:{name}",
        kind="certificate" if kind == "certificate" else "algorithm",
        name=name,
        quantum_status=status,
        purpose="signature",
    )


def test_ml_dsa_reports_existing_migration() -> None:
    result = assess_ml_dsa_migration(_graph(_signature("ML-DSA-65", "safe")))

    assert result.status == "already_migrated"
    assert result.compatible is True


def test_ml_dsa_prefers_hybrid_credentials_for_classical_certificates() -> None:
    result = assess_ml_dsa_migration(
        _graph(_signature("server certificate", "vulnerable", kind="certificate")),
        supported_signatures=("ECDSA", "ML-DSA-65"),
        hybrid_supported=True,
    )

    assert result.status == "hybrid_ready"
    assert result.affected_node_ids == ("certificate:server certificate",)
    assert "classical + ML-DSA-65" in result.required_changes[0]


@pytest.mark.parametrize(
    ("graph", "supported", "factor"),
    [
        (_graph(), (), "no signing assets discovered"),
        (
            _graph(_signature("ECDSA", "vulnerable")),
            ("ECDSA",),
            "runtime does not advertise ML-DSA-65",
        ),
    ],
)
def test_ml_dsa_reports_blocking_factors(
    graph: CryptoDependencyGraph, supported: tuple[str, ...], factor: str
) -> None:
    result = assess_ml_dsa_migration(graph, supported_signatures=supported)

    assert result.status == "blocked"
    assert result.blocking_factors == (factor,)
