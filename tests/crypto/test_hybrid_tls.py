import pytest
from lattence_crypto.pqc import CryptoDependencyGraph, CryptoGraphNode
from lattence_crypto.tls import validate_hybrid_tls


def _algorithm(
    name: str,
    status: str | None,
    purpose: str,
    *,
    kind: str = "algorithm",
) -> CryptoGraphNode:
    return CryptoGraphNode(
        id=f"{kind}:{name}",
        kind="tls_configuration" if kind == "tls" else "algorithm",
        name=name,
        quantum_status=status,
        purpose=purpose,
    )


def test_validates_complete_hybrid_tls_configuration() -> None:
    graph = CryptoDependencyGraph(
        nodes=(
            _algorithm("TLS 1.3", None, "transport", kind="tls"),
            _algorithm("X25519", "vulnerable", "key exchange"),
            _algorithm("ML-KEM-768", "safe", "key exchange"),
            _algorithm("ECDSA", "vulnerable", "signature"),
            _algorithm("ML-DSA-65", "safe", "signature"),
        ),
        edges=(),
    )

    result = validate_hybrid_tls(graph)

    assert result.status == "valid"
    assert result.tls_13 is True
    assert result.hybrid_key_exchange is True
    assert result.hybrid_signature is True
    assert result.issues == ()


def test_accepts_explicit_hybrid_algorithm_nodes() -> None:
    graph = CryptoDependencyGraph(
        nodes=(
            _algorithm("TLS 1.3", None, "transport", kind="tls"),
            _algorithm("X25519 + ML-KEM-768", "hybrid", "key exchange"),
            _algorithm("ECDSA + ML-DSA-65", "hybrid", "signature"),
        ),
        edges=(),
    )

    assert validate_hybrid_tls(graph).status == "valid"


@pytest.mark.parametrize(
    ("nodes", "status"),
    [
        ((), "invalid"),
        ((_algorithm("TLS 1.3", None, "transport", kind="tls"),), "partial"),
    ],
)
def test_reports_incomplete_hybrid_configuration(
    nodes: tuple[CryptoGraphNode, ...], status: str
) -> None:
    result = validate_hybrid_tls(CryptoDependencyGraph(nodes=nodes, edges=()))

    assert result.status == status
    assert result.issues
