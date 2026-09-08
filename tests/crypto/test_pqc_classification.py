from datetime import UTC, datetime

import pytest
from lattence.graph import CryptoAlgorithm, SecurityGraph
from lattence_crypto.pqc import classify_algorithm, classify_graph


def _algorithm(name: str) -> CryptoAlgorithm:
    return CryptoAlgorithm(
        id=f"crypto_algorithm:{name.lower()}",
        name=name,
        algorithm=name,
        purpose="key exchange",
        quantum_status="unknown",
    )


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("ML-KEM-768", "safe"),
        ("RSA-2048", "vulnerable"),
        ("X25519 + ML-KEM-768 hybrid", "hybrid"),
        ("TLS 1.3", "unknown"),
    ],
)
def test_classifies_all_quantum_states(name: str, expected: str) -> None:
    assert classify_algorithm(_algorithm(name)).quantum_status == expected


def test_classifies_crypto_nodes_in_graph_only() -> None:
    algorithm = _algorithm("ECDSA")
    graph = SecurityGraph(
        project_id="fixture",
        nodes=[algorithm],
        edges=[],
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    classified = classify_graph(graph)

    node = classified.nodes[0]
    assert isinstance(node, CryptoAlgorithm)
    assert node.quantum_status == "vulnerable"
    assert graph.nodes[0].quantum_status == "unknown"
