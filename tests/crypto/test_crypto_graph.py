from datetime import UTC, datetime

from lattence.graph import (
    Application,
    Certificate,
    CryptoAlgorithm,
    Edge,
    SecurityGraph,
    SourceRef,
)
from lattence_crypto.discovery import CryptoLibrary
from lattence_crypto.pqc import build_crypto_graph


def test_projects_crypto_assets_libraries_and_transitive_ancestors() -> None:
    application = Application(id="application:demo", name="demo")
    certificate = Certificate(
        id="certificate:server",
        name="server",
        public_key_algorithm="RSA",
        signature_algorithm="sha256WithRSAEncryption",
    )
    algorithm = CryptoAlgorithm(
        id="crypto_algorithm:x25519",
        name="X25519",
        source=SourceRef(path="tls.py", line=3),
        algorithm="X25519",
        purpose="key exchange",
        quantum_status="vulnerable",
        implementation="tls.py",
    )
    graph = SecurityGraph(
        project_id="demo",
        nodes=[algorithm, certificate, application],
        edges=[
            Edge(
                id="edge:app:cert",
                source_id=application.id,
                target_id=certificate.id,
                type="protected_by",
            ),
            Edge(
                id="edge:cert:algorithm",
                source_id=certificate.id,
                target_id=algorithm.id,
                type="protected_by",
                evidence_refs=["tls.py"],
            ),
        ],
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    library = CryptoLibrary("cryptography", "python", "pyproject.toml", ("tls.py",))

    projection = build_crypto_graph(graph, (library,))

    assert [node.id for node in projection.nodes] == sorted(
        [
            application.id,
            certificate.id,
            algorithm.id,
            "crypto_library:python:cryptography:pyproject.toml",
        ]
    )
    relationships = {
        (edge.source_id, edge.relationship, edge.target_id) for edge in projection.edges
    }
    assert (application.id, "protected_by", certificate.id) in relationships
    assert (certificate.id, "protected_by", algorithm.id) in relationships
    assert (
        "crypto_library:python:cryptography:pyproject.toml",
        "implements",
        algorithm.id,
    ) in relationships
    projected_certificate = next(
        node for node in projection.nodes if node.id == certificate.id
    )
    assert projected_certificate.quantum_status == "vulnerable"


def test_projection_excludes_unrelated_components_and_is_deterministic() -> None:
    crypto = CryptoAlgorithm(
        id="crypto_algorithm:tls13",
        name="TLS 1.3",
        algorithm="TLS 1.3",
        purpose="transport",
        quantum_status="unknown",
    )
    unrelated = Application(id="application:unrelated", name="unrelated")
    graph = SecurityGraph(
        project_id="demo",
        nodes=[unrelated, crypto],
        edges=[],
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    first = build_crypto_graph(graph)
    second = build_crypto_graph(graph)

    assert first == second
    assert [node.id for node in first.nodes] == [crypto.id]
    assert first.nodes[0].kind == "tls_configuration"
