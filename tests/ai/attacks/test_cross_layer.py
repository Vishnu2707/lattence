from datetime import UTC, datetime

import pytest
from lattence.evidence import EvidenceBundle, Finding
from lattence.graph import CryptoAlgorithm, Dataset, Edge, EdgeType, SecurityGraph, Tool
from lattence_ai.attacks import CrossLayerAnalysisError, correlate_cross_layer_findings


def _finding(finding_id: str, target_node_id: str) -> Finding:
    evidence = EvidenceBundle.model_construct(id=f"evidence:{finding_id}")
    return Finding.model_construct(
        id=finding_id,
        target_node_id=target_node_id,
        evidence=evidence,
    )


def _graph(edge_type: EdgeType = "key_exchange") -> SecurityGraph:
    dataset = Dataset(id="dataset:rag", name="RAG")
    tool = Tool(id="tool:retrieval", name="retrieval")
    crypto = CryptoAlgorithm(
        id="crypto_algorithm:tls12",
        name="TLS 1.2",
        algorithm="TLS 1.2",
        purpose="transport",
        quantum_status="vulnerable",
    )
    return SecurityGraph(
        project_id="fixture",
        nodes=[dataset, tool, crypto],
        edges=[
            Edge(
                id="edge:tool:dataset",
                source_id=tool.id,
                target_id=dataset.id,
                type="accesses",
                evidence_refs=["app.py"],
            ),
            Edge(
                id="edge:tool:crypto",
                source_id=tool.id,
                target_id=crypto.id,
                type=edge_type,
                evidence_refs=["app.py", "tls.conf"],
            ),
        ],
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_correlates_ai_and_crypto_findings_over_real_oriented_edges() -> None:
    findings = (
        _finding("LT-AI-002", "dataset:rag"),
        _finding("LT-PQC-203", "crypto_algorithm:tls12"),
    )

    correlations = correlate_cross_layer_findings(_graph(), findings)

    assert len(correlations) == 1
    correlation = correlations[0]
    assert correlation.source_finding_id == "LT-AI-002"
    assert correlation.crypto_finding_id == "LT-PQC-203"
    assert [hop.edge_id for hop in correlation.path.hops] == [
        "edge:tool:dataset",
        "edge:tool:crypto",
    ]
    assert [hop.traversal for hop in correlation.path.hops] == [
        "reverse",
        "forward",
    ]
    assert correlation.evidence_refs == (
        "app.py",
        "evidence:LT-AI-002",
        "evidence:LT-PQC-203",
        "tls.conf",
    )
    assert "reverse accesses" in correlation.explanation
    assert "forward key_exchange" in correlation.explanation


def test_requires_a_crypto_relationship_and_known_finding_targets() -> None:
    findings = (
        _finding("LT-AI-002", "dataset:rag"),
        _finding("LT-PQC-203", "crypto_algorithm:tls12"),
    )

    assert correlate_cross_layer_findings(_graph("calls"), findings) == ()
    unknown = (*findings, _finding("LT-AI-009", "application:missing"))
    with pytest.raises(CrossLayerAnalysisError, match="unknown finding target"):
        correlate_cross_layer_findings(_graph(), unknown)


def test_ignores_findings_outside_cross_layer_domains() -> None:
    findings = (
        _finding("LT-POLICY-001", "dataset:rag"),
        _finding("LT-PQC-203", "crypto_algorithm:tls12"),
    )

    assert correlate_cross_layer_findings(_graph(), findings) == ()
