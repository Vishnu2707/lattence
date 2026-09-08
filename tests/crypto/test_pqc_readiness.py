from datetime import UTC, datetime

from lattence.graph import CryptoAlgorithm, SecurityGraph
from lattence_crypto.pqc import assess_readiness


def _graph(names: tuple[str, ...]) -> SecurityGraph:
    algorithms = [
        CryptoAlgorithm(
            id=f"crypto_algorithm:{index}",
            name=name,
            algorithm=name,
            purpose="test",
            quantum_status="unknown",
        )
        for index, name in enumerate(names)
    ]
    return SecurityGraph(
        project_id="fixture",
        nodes=algorithms,
        edges=[],
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_calculates_weighted_readiness_percentage() -> None:
    result = assess_readiness(
        _graph(("ML-KEM-768", "X25519 + ML-KEM-768 hybrid", "RSA", "ECDSA"))
    )

    assert result.total == 4
    assert result.safe == 1
    assert result.hybrid == 1
    assert result.vulnerable == 2
    assert result.unknown == 0
    assert result.score_percent == 38


def test_empty_inventory_has_zero_readiness() -> None:
    result = assess_readiness(_graph(()))

    assert result.total == 0
    assert result.score_percent == 0
